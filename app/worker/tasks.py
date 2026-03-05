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

@celery_app.task(name="process_session_task")
def process_session_task(session_id: int, filename: str = None, filepath: str = None, file_url: str = None):
    """
    Background task to process the uploaded session.
    Uploads the file to Cloudinary and updates the session Database record.
    """
    logger.info(f"Starting processing for Session ID: {session_id}")
    import os
    from app.services.cloudinary_service import CloudinaryService
    from app.db.session import SessionLocal
    from app.features.sessions.models import Session
    from sqlalchemy import select
    
    # 1. Upload to Cloudinary
    try:
        if file_url:
            public_url = CloudinaryService.upload_file_from_url(file_url, filename)
        elif filepath:
            public_url = CloudinaryService.upload_file_from_path(filepath, filename)
        else:
            raise ValueError("Neither filepath nor file_url provided")
        
        # 2. Update the database
        db = SessionLocal()
        session_record = db.execute(select(Session).where(Session.id == session_id)).scalar_one_or_none()
        
        if session_record:
            session_record.vcon_url = public_url
            session_record.status = "completed"
            db.commit()
            logger.info(f"Session DB record {session_id} updated successfully.")
        else:
            logger.error(f"Session ID {session_id} not found in DB.")
        db.close()
        
    except Exception as e:
        logger.error(f"Error processing session {session_id}: {e}")
        # Could set status to "failed" here
    finally:
        # Cleanup
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            
    return {"session_id": session_id, "status": "completed", "vcon_url": public_url}
