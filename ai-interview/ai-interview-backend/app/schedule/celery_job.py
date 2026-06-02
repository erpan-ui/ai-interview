import logging
import os
import tempfile
from fastapi import FastAPI

# 导入 Celery 应用
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


def setup_scheduler(app: FastAPI = None):
    """
    初始化定时任务调度器，使用 Celery
    
    Args:
        app: FastAPI应用实例
    """
    if not app:
        logger.error("FastAPI app instance is required for scheduler setup")
        return
    
    # 使用文件锁确保只有一个进程运行调度器初始化
    lock_file_path = os.path.join(tempfile.gettempdir(), "tip_scheduler.lock")
    logger.info(f"Lock file path: {lock_file_path}")
    
    try:
        # 检查锁文件是否存在
        if os.path.exists(lock_file_path):
            # 读取锁文件中的进程ID
            try:
                with open(lock_file_path, "r") as f:
                    pid = f.read().strip()
                    
                # 检查该进程是否仍在运行
                try:
                    os.kill(int(pid), 0)  # 检查进程是否存在
                    logger.info(f"Scheduler lock exists. Process {pid} is running the scheduler.")
                    # 此进程不运行调度器初始化
                    logger.info(f"Process {os.getpid()} will not initialize the scheduler.")
                    scheduler_enabled = False
                except ProcessLookupError:
                    # 进程不存在，删除旧锁文件
                    logger.warning(f"Process {pid} in lock file is not running. Removing stale lock file.")
                    os.remove(lock_file_path)
                    # 创建新锁文件
                    with open(lock_file_path, "w") as f:
                        f.write(str(os.getpid()))
                    logger.info(f"Acquired scheduler lock. This process (PID: {os.getpid()}) will initialize the scheduler.")
                    scheduler_enabled = True
            except Exception as e:
                # 如果读取锁文件失败，删除锁文件并创建新的
                logger.warning(f"Could not read scheduler lock file: {e}. Creating new lock.")
                os.remove(lock_file_path)
                with open(lock_file_path, "w") as f:
                    f.write(str(os.getpid()))
                logger.info(f"Acquired scheduler lock. This process (PID: {os.getpid()}) will initialize the scheduler.")
                scheduler_enabled = True
        else:
            # 锁文件不存在，创建新锁文件
            with open(lock_file_path, "w") as f:
                f.write(str(os.getpid()))
            logger.info(f"Acquired scheduler lock. This process (PID: {os.getpid()}) will initialize the scheduler.")
            scheduler_enabled = True
    except Exception as e:
        logger.error(f"Error handling scheduler lock: {e}")
        # 出错时默认不启用调度器
        scheduler_enabled = False
    
    if scheduler_enabled:
        logger.info("Celery task scheduler initialized")
        # 将 Celery 应用实例存储到 FastAPI 应用状态中，以便其他地方访问
        app.state.celery_app = celery_app

def shutdown_scheduler():
    """
    关闭调度器 - 对于Celery, 不需要特殊操作，
    因为Celery worker和beat进程是独立的进程
    """
    logger.info("Celery scheduler shutdown - no special actions needed")