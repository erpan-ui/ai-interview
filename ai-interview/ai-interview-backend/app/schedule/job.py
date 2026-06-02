import logging
from app.db.base import create_scheduler_engine, create_scheduler_session_factory
logger = logging.getLogger(__name__)

async def demo():
    logger.info("Running scheduled task: demo")
    
    # 创建此任务专用的数据库引擎和会话工厂
    scheduler_engine = create_scheduler_engine()
    SchedulerSessionLocal = create_scheduler_session_factory(scheduler_engine)
    
    # 使用新创建的会话工厂
    async with SchedulerSessionLocal() as db:
        try:
            pass
        
        except Exception as e:
            logger.error(f"Error in demo: {e}", exc_info=True)
        finally:
            # 关闭数据库引擎
            await scheduler_engine.dispose()

