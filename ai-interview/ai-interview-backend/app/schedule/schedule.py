import logging
import asyncio
import os
import tempfile
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore

from app.schedule.job import (
    demo
)

logger = logging.getLogger(__name__)

# 全局变量用于存储调度器实例
scheduler = None

def async_task_wrapper(async_func):
    """包装异步函数，使其可以在调度器中运行"""
    def wrapper(*args, **kwargs):
        try:
            # 创建一个新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 在新事件循环中运行任务
            try:
                return loop.run_until_complete(async_func(*args, **kwargs))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error running async task: {e}", exc_info=True)
            raise
    return wrapper

def setup_scheduler(app: FastAPI = None):
    """
    初始化定时任务调度器，使用 APScheduler
    
    Args:
        app: FastAPI应用实例
    """
    global scheduler
    
    if not app:
        logger.error("FastAPI app instance is required for scheduler setup")
        return
    
    # 使用文件锁确保只有一个进程运行调度器
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
                    # 在Unix系统中，如果进程存在，os.kill(pid, 0)不会做任何事情
                    # 如果进程不存在，会抛出ProcessLookupError异常
                    os.kill(int(pid), 0)
                    logger.info(f"Scheduler lock exists. Process {pid} is running the scheduler.")
                    # 此进程不运行调度器
                    logger.info(f"Process {os.getpid()} will not run the scheduler.")
                    scheduler_enabled = False
                except ProcessLookupError:
                    # 进程不存在，删除旧锁文件
                    logger.warning(f"Process {pid} in lock file is not running. Removing stale lock file.")
                    os.remove(lock_file_path)
                    # 创建新锁文件
                    with open(lock_file_path, "w") as f:
                        f.write(str(os.getpid()))
                    logger.info(f"Acquired scheduler lock. This process (PID: {os.getpid()}) will run the scheduler.")
                    scheduler_enabled = True
            except Exception as e:
                # 如果读取锁文件失败，删除锁文件并创建新的
                logger.warning(f"Could not read scheduler lock file: {e}. Creating new lock.")
                os.remove(lock_file_path)
                with open(lock_file_path, "w") as f:
                    f.write(str(os.getpid()))
                logger.info(f"Acquired scheduler lock. This process (PID: {os.getpid()}) will run the scheduler.")
                scheduler_enabled = True
        else:
            # 锁文件不存在，创建新锁文件
            with open(lock_file_path, "w") as f:
                f.write(str(os.getpid()))
            logger.info(f"Acquired scheduler lock. This process (PID: {os.getpid()}) will run the scheduler.")
            scheduler_enabled = True
    except Exception as e:
        logger.error(f"Error handling scheduler lock: {e}")
        # 出错时默认不启用调度器
        scheduler_enabled = False
    
    # 如果不是指定运行调度器的进程，则跳过初始化
    if not scheduler_enabled:
        logger.info("Scheduler disabled for this worker process")
        return
    
    try:
        # 创建调度器实例
        scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            timezone='UTC'
        )
        
        # 添加定时任务
        scheduler.add_job(
            async_task_wrapper(demo),
            'interval', 
            seconds=60,
            id='demo_task',
            replace_existing=True,
            max_instances=1  # 限制最多只有一个实例在运行
        )
        
        # 启动调度器
        scheduler.start()
        logger.info("定时任务已注册并成功启动")
    except Exception as e:
        logger.error(f"Failed to setup scheduler: {e}", exc_info=True)

def shutdown_scheduler():
    """
    关闭调度器
    """
    global scheduler
    logger.info("Shutting down scheduler")
    logger.info(scheduler)
    
    try:
        if scheduler:
            scheduler.shutdown()
            logger.info("定时任务调度器已成功关闭")
    except Exception as e:
        logger.error(f"Error shutting down scheduler: {e}")