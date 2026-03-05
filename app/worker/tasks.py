import asyncio
from app.worker.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="dummy_task")
def dummy_task(arg: str):
    """
    A simple dummy task to verify Celery setup.
    It takes a string, simulates a short delay, and returns a processed string.
    """
    logger.info(f"Dummy task received: {arg}")
    import time
    time.sleep(2)
    result = f"Processed: {arg}"
    logger.info(f"Dummy task completed: {result}")
    return result
