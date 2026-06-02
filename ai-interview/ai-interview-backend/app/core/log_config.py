import os
import json
from datetime import datetime
from logging.handlers import QueueHandler
from app.core.config import settings
import logging
import logging.handlers
from logging.config import dictConfig
from app.services.common.redis import redis_client
import sys
import threading
import time

# 日志目录
# 修复路径计算，确保始终指向项目根目录
script_path = os.path.abspath(__file__)
# 直接使用项目结构信息，从当前文件定位到项目根目录
# 当前文件在app/core/log_config.py，向上两级目录（不是三级）到达项目根目录
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(script_path), "../.."))

# 移除调试输出，避免在多进程环境下重复打印
# print(f"日志目录BASE_DIR: {BASE_DIR}")

LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")
SQLALCHEMY_LOG_FILE = os.path.join(LOG_DIR, f"sqlalchemy_{datetime.now().strftime('%Y%m%d')}.log")
MASTER_PROCESS_FILE = os.path.join(LOG_DIR, "master_process.lock")

# 根据环境设置日志级别
ENV = settings.ENV.lower()
LOG_LEVELS = {
    "development": "DEBUG",
    "testing": "INFO",
    "production": "WARNING"
}
LOG_LEVEL = LOG_LEVELS.get(ENV, "INFO")
SQLALCHEMY_LEVEL = "INFO" if ENV == "production" else "DEBUG"

# 判断是否为主进程
def is_master_process():
    # 获取当前进程ID
    pid = os.getpid()
    
    # 检查是否有UVICORN_PROCESS_ID环境变量
    worker_id = os.environ.get("UVICORN_WORKER_ID", os.environ.get("UVICORN_PROCESS_ID", None))
    
    # 如果有worker_id且为0，或者没有worker_id，则尝试成为master进程
    if (worker_id is not None and worker_id == "0") or worker_id is None:
        try:
            # 尝试创建锁文件
            if not os.path.exists(MASTER_PROCESS_FILE):
                with open(MASTER_PROCESS_FILE, "w") as f:
                    f.write(str(pid))
                return True
            else:
                # 读取锁文件并检查进程是否存在
                with open(MASTER_PROCESS_FILE, "r") as f:
                    master_pid = f.read().strip()
                    
                # 尝试确认该进程是否存在
                try:
                    os.kill(int(master_pid), 0)  # 不发送信号，只检查进程是否存在
                    # 进程存在，不是master
                    return pid == int(master_pid)
                except OSError:
                    # 进程不存在，更新锁文件并成为master
                    with open(MASTER_PROCESS_FILE, "w") as f:
                        f.write(str(pid))
                    return True
        except Exception:
            return False
    return False

# Redis日志处理器
class RedisLogHandler(logging.Handler):
    """使用Redis作为日志队列的处理器"""
    def __init__(self, redis_key='app:logs', max_queue_size=10000):
        super().__init__()
        self.redis_key = redis_key
        self.max_queue_size = max_queue_size
        # 存储待处理的日志，用于批量处理
        self._pending_logs = []
        self._max_batch_size = 100
        
    def emit(self, record):
        try:
            # 格式化日志记录
            log_entry = {
                'time': record.created,
                'name': record.name,
                'level': record.levelname,
                'message': self.format(record),
                'pathname': getattr(record, 'pathname', ''),
                'lineno': getattr(record, 'lineno', 0)
            }
            
            # 序列化日志
            try:
                serialized_log = json.dumps(log_entry)
                
                # 将日志添加到处理队列，避免阻塞或异步调用问题
                log_processor.add_log(serialized_log)
            except Exception as e:
                # 记录到标准错误输出，避免递归日志
                print(f"Redis日志处理器错误: {e}", file=sys.stderr)
        except Exception:
            self.handleError(record)

# 创建一个队列处理线程，稍后使用
class LogQueueProcessor(threading.Thread):
    def __init__(self, redis_key='app:logs', daemon=True):
        super().__init__(daemon=daemon)
        self.redis_key = redis_key
        self.queue = []
        self.lock = threading.Lock()
        self.running = True
        
    def add_log(self, log_data):
        with self.lock:
            self.queue.append(log_data)
            
    def run(self):
        while self.running:
            # 处理队列中的日志
            logs_to_process = []
            with self.lock:
                if self.queue:
                    logs_to_process = self.queue.copy()
                    self.queue.clear()
            
            # 如果有日志要处理
            if logs_to_process:
                for log_data in logs_to_process:
                    try:
                        # 使用同步方式发送到Redis
                        redis_conn = redis_client.redis._connection_pool.get_connection("LPUSH")
                        redis_conn.send_command("LPUSH", self.redis_key, log_data)
                        redis_client.redis._connection_pool.release(redis_conn)
                    except Exception as e:
                        # 记录失败日志到备份文件
                        with open(os.path.join(LOG_DIR, "redis_failed_logs.txt"), "a") as f:
                            f.write(log_data + "\n")
            
            # 休眠一小段时间
            time.sleep(0.1)
    
    def stop(self):
        self.running = False
        self.join(timeout=2)  # 等待最多2秒让线程完成

# 创建并启动日志处理线程
log_processor = LogQueueProcessor()
log_processor.start()

# 创建一个多进程安全的文件处理器
class SafeTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """多进程安全的日志文件处理器"""
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
        # 使用多进程时避免文件权限冲突
        self.delay = True  # 延迟创建文件直到第一条日志写入
        self.mode = 'a'    # 总是追加模式

    def _open(self):
        # 避免多进程冲突的文件打开方式
        return open(self.baseFilename, self.mode, encoding=self.encoding)

# 初始化Redis日志处理器
redis_handler = RedisLogHandler()

# 配置日志格式化器
console_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] [PID:%(process)d] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] [PID:%(process)d] %(name)s [%(pathname)s:%(lineno)d]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 应用格式化器到Redis处理器
redis_handler.setFormatter(file_formatter)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console_formatter": {
            "format": "%(asctime)s [%(levelname)s] [PID:%(process)d] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "file_formatter": {
            "format": "%(asctime)s [%(levelname)s] [PID:%(process)d] %(name)s [%(pathname)s:%(lineno)d]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "console_formatter",
        },
        "file": {
            "class": "app.core.log_config.SafeTimedRotatingFileHandler",
            "level": LOG_LEVEL,
            "formatter": "file_formatter",
            "filename": LOG_FILE,
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "encoding": "utf-8",
        },
        "sqlalchemy_file": {
            "class": "app.core.log_config.SafeTimedRotatingFileHandler",
            "level": SQLALCHEMY_LEVEL,
            "formatter": "file_formatter",
            "filename": SQLALCHEMY_LOG_FILE,
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "encoding": "utf-8",
        },
        "redis": {
            "()": "app.core.log_config.RedisLogHandler",
            "level": LOG_LEVEL,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file", "redis"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "pdfminer": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": False,
        },
        "python_multipart": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["console", "sqlalchemy_file", "redis"],
            "level": SQLALCHEMY_LEVEL,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console", "file", "redis"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console", "file", "redis"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

def setup_logging():
    """应用日志配置"""
    # 确保日志目录存在
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    dictConfig(LOGGING_CONFIG)
    
    # 只在主进程中输出初始化日志
    if is_master_process():
        logging.getLogger("app.core.log_config").info("日志系统已初始化（主进程）")


def shutdown_logging():
    """关闭日志处理器，在多进程环境不需要特殊关闭"""
    # 停止日志处理线程
    log_processor.stop()
    
    # 只在主进程中输出关闭日志
    if is_master_process():
        logging.getLogger("app.core.log_config").info("正在关闭日志系统（主进程）")
        # 清理锁文件
        try:
            if os.path.exists(MASTER_PROCESS_FILE):
                os.remove(MASTER_PROCESS_FILE)
        except Exception:
            pass
    logging.shutdown()