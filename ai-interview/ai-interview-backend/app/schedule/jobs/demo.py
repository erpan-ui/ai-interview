import logging
from celery import shared_task
from app.db.base import create_scheduler_engine, create_scheduler_session_factory
import asyncio

logger = logging.getLogger(__name__)

@shared_task(name="app.schedule.jobs.demo.execute")
def execute():
    """
    Demo task for testing Celery execution
    This is a simple task that logs a message and demonstrates database connectivity
    """
    logger.info("=== DEMO TASK EXECUTION STARTED ===")
    
    # 创建此任务专用的数据库引擎和会话工厂
    scheduler_engine = create_scheduler_engine()
    SchedulerSessionLocal = create_scheduler_session_factory(scheduler_engine)
    
    # 使用新创建的会话工厂
    try:
        # This would be an async function in FastAPI context, but Celery tasks should be synchronous
        # So we're using a synchronous approach here
        logger.info("Connecting to database...")
        # You could add your database operations here
        logger.info("Database operations completed")
        
    except Exception as e:
        logger.error(f"Error in demo task: {e}", exc_info=True)
        raise
    finally:
        # Close engine properly by running the coroutine in an event loop
        logger.info("Closing database connection")
        # Create a new event loop to run the async dispose method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(scheduler_engine.dispose())
        finally:
            loop.close()
    
    logger.info("=== DEMO TASK EXECUTION COMPLETED SUCCESSFULLY ===")
    return {"status": "success", "message": "Demo task executed successfully"}