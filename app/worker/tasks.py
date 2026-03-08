import asyncio
from app.worker.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

import os
import json
import time
import httpx
import urllib.request
from sqlalchemy import select

from app.services.cloudinary_service import CloudinaryService
from app.services.vcon_service import VconBuilder
from app.services.ai_service import AIService
from app.features.sessions.models import Session

import app.features.auth.models
import app.features.users.models
import app.features.cohorts.models
import app.features.participants.models

from contextlib import contextmanager

@contextmanager
def get_task_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import NullPool
    from app.core.config import settings
    
    sync_uri = settings.SQLALCHEMY_DATABASE_URI.replace("postgresql+asyncpg://", "postgresql://")
    logger.info("Initializing NullPool engine for task...")
    engine = create_engine(sync_uri, poolclass=NullPool)
    session_maker = sessionmaker(bind=engine, expire_on_commit=False)
    
    try:
        with session_maker() as db:
            yield db
    finally:
        engine.dispose()

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
    # 1. Upload to Cloudinary
    public_url = None
    try:
        if file_url:
            public_url = CloudinaryService.upload_file_from_url(file_url, filename)
        elif filepath:
            public_url = CloudinaryService.upload_file_from_path(filepath, filename)
        else:
            raise ValueError("Neither filepath nor file_url provided")
        
        # 2. Update the database and create initial vCon
        def update_db_and_vcon():
            with get_task_db() as db:
                session_record = db.execute(select(Session).where(Session.id == session_id)).scalar_one_or_none()
                
                if session_record:
                    session_record.audio_file_url = public_url
                    session_record.status = "processing"
                    
                    # Builder creates initial vcon and adds recording
                    builder = VconBuilder(session_id=session_id, cohort_id=session_record.cohort_id)
                    builder.add_recording(file_path=filename or "recording", url=public_url)
                    vcon_json = builder.serialize()
                    
                    # Upload vCon JSON to Cloudinary
                    vcon_filename = f"vcon_{session_id}.json"
                    filepath_json = f"/tmp/{vcon_filename}"
                    with open(filepath_json, "w") as f:
                        f.write(vcon_json)
                        
                    vcon_url = CloudinaryService.upload_file_from_path(filepath_json, vcon_filename)
                    if os.path.exists(filepath_json):
                        os.remove(filepath_json)
                        
                    session_record.vcon_file_url = vcon_url
                    db.commit()
                    logger.info(f"Session DB record {session_id} vcon initialized successfully. URL: {vcon_url}")
                    return vcon_url
                else:
                    logger.error(f"Session ID {session_id} not found in DB.")
                    return None
                    
        vcon_url = update_db_and_vcon()
        
        if vcon_url:
            generate_transcript_task.delay(session_id)
        
    except Exception as e:
        logger.error(f"Error processing session {session_id}: {e}")
        # Could set status to "failed" here
    finally:
        # Cleanup
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            
    return {"session_id": session_id, "status": "processing", "audio_url": public_url, "vcon_url": vcon_url if 'vcon_url' in locals() else None}

@celery_app.task(name="generate_transcript_task")
def generate_transcript_task(session_id: int):
    """
    Downloads the audio file, transcribes it via Whisper, 
    and appends the transcript to the existing vCon.
    """
    logger.info(f"Starting transcript task for Session ID: {session_id}")
    def process_transcript():
        logger.info("Inside process_transcript sync function...")
        try:
            with get_task_db() as db:
                logger.info("DB Context acquired. Executing select...")
                session = db.execute(select(Session).where(Session.id == session_id)).scalar_one_or_none()
                logger.info(f"Session fetched: {session is not None}")
                
                if not session or not session.audio_file_url or not session.vcon_file_url:
                    logger.error(f"Session {session_id} missing files/data for transcript.")
                    return False
                    
                audio_url = session.audio_file_url
                vcon_file_url = session.vcon_file_url
                cohort_id = session.cohort_id
        except Exception as e:
            logger.error(f"Error checking DB: {e}", exc_info=True)
            return False
            
        # 1. Download audio file locally
        temp_audio_path = f"/tmp/audio_{session_id}_{os.path.basename(audio_url)}"
        # Handle cloudinary urls with query params by just picking a basic name
        temp_audio_path = temp_audio_path.split("?")[0] 
        
        logger.info(f"Downloading audio from {audio_url}")
        try:
            # 10 minutes timeout for potentially large files (e.g. 100MB video)
            with httpx.stream("GET", audio_url, timeout=600.0, follow_redirects=True) as r:
                r.raise_for_status()
                with open(temp_audio_path, "wb") as f:
                    for chunk in r.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            logger.info(f"Successfully downloaded media to {temp_audio_path}")
            
            # Extract and compress audio to an MP3 using ffmpeg
            # This ensures Whisper gets a valid extension and stays under the 25MB file limit
            compressed_mp3_path = f"{temp_audio_path}.mp3"
            import subprocess
            logger.info(f"Extracting audio from {temp_audio_path} via ffmpeg...")
            subprocess.run([
                "ffmpeg", "-y", "-i", temp_audio_path,
                "-vn", # Disable video
                "-acodec", "libmp3lame", 
                "-q:a", "4", # Variable bitrate ~128kbps, excellent for speech
                compressed_mp3_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            logger.info(f"Successfully compressed to {compressed_mp3_path}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFMPEG audio extraction failed for {session_id}: {e}")
            if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
            if os.path.exists(compressed_mp3_path): os.remove(compressed_mp3_path)
            return False
        except Exception as e:
            logger.error(f"Failed to download/process audio for {session_id}: {e}")
            if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
            return False
            
        # 2. Transcribe via Whisper
        try:
            start_time = time.time()
            logger.info(f"Sending audio {compressed_mp3_path} to Whisper API...")
            transcript_text = AIService.generate_transcript(compressed_mp3_path)
            logger.info(f"Transcription completed in {time.time() - start_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Whisper transcription failed for {session_id}: {e}")
            if os.path.exists(compressed_mp3_path): os.remove(compressed_mp3_path)
            if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
            return False
        finally:
            if os.path.exists(compressed_mp3_path): os.remove(compressed_mp3_path)
            if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
        
        # 3. Fetch current Vcon JSON
        temp_vcon_path = f"/tmp/vcon_{session_id}.json"
        try:
            logger.info(f"Downloading vCon JSON from {vcon_file_url}")
            with httpx.stream("GET", vcon_file_url, timeout=120.0, follow_redirects=True) as r:
                r.raise_for_status()
                with open(temp_vcon_path, "wb") as f:
                    for chunk in r.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            
            with open(temp_vcon_path, "r") as f:
                vcon_json = f.read()
        except Exception as e:
            logger.error(f"Failed to download vCon JSON from {vcon_file_url}: {e}")
            if os.path.exists(temp_vcon_path): os.remove(temp_vcon_path)
            return False
            
        # 4. Update Vcon with builder
        builder = VconBuilder.from_json(vcon_json, session_id, cohort_id)
        builder.add_analysis(
            analysis_type="transcript",
            result={"text": transcript_text},
            vendor="openai-whisper"
        )
        updated_vcon_json = builder.serialize()
        
        # 5. Re-upload Vcon
        with open(temp_vcon_path, "w") as f:
            f.write(updated_vcon_json)
            
        new_vcon_url = CloudinaryService.upload_file_from_path(
            temp_vcon_path, 
            f"vcon_{session_id}_transcribed.json"
        )
        os.remove(temp_vcon_path)
        
        # 6. Update DB
        try:
            with get_task_db() as db:
                session_db = db.execute(select(Session).where(Session.id == session_id)).scalar_one_or_none()
                if session_db:
                    session_db.vcon_file_url = new_vcon_url
                    db.commit()
        except Exception as e:
            logger.error(f"Failed to update DB with new vcon URL: {e}")
            return False
        
        return True
            
    logger.info("Calling process_transcript()")
    success = process_transcript()
    logger.info(f"process_transcript returned {success}")
    if success:
        generate_semantic_analysis_task.delay(session_id)
        return {"session_id": session_id, "status": "transcription_complete"}
    else:
        try:
            with get_task_db() as db:
                session_db = db.execute(select(Session).where(Session.id == session_id)).scalar_one_or_none()
                if session_db:
                    session_db.status = "failed"
                    db.commit()
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")
        return {"session_id": session_id, "status": "transcription_failed"}

@celery_app.task(name="generate_semantic_analysis_task")
def generate_semantic_analysis_task(session_id: int):
    """
    Downloads Vcon to extract the transcript, sends it to instructor + GPT-4o,
    appends the semantic analysis to the Vcon, and updates DB caches.
    """
    logger.info(f"Starting semantic analysis task for Session ID: {session_id}")
    def process_semantic_analysis():
        try:
            with get_task_db() as db:
                session = db.execute(select(Session).where(Session.id == session_id)).scalar_one_or_none()
                if not session or not session.vcon_file_url:
                    logger.error(f"Session {session_id} missing vcon_file_url for semantic analysis.")
                    return False
                vcon_file_url = session.vcon_file_url
                cohort_id = session.cohort_id
        except Exception as e:
            logger.error(f"Error checking DB for semantic analysis: {e}")
            return False
            
        # 1. Download Vcon
        temp_vcon_path = f"/tmp/vcon_sem_{session_id}.json"
        try:
            logger.info(f"Downloading vCon JSON from {vcon_file_url}")
            with httpx.stream("GET", vcon_file_url, timeout=120.0, follow_redirects=True) as r:
                r.raise_for_status()
                with open(temp_vcon_path, "wb") as f:
                    for chunk in r.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            
            with open(temp_vcon_path, "r") as f:
                vcon_json = f.read()
        except Exception as e:
            logger.error(f"Failed to download vCon JSON: {e}")
            if os.path.exists(temp_vcon_path): os.remove(temp_vcon_path)
            return False
            
        # 2. Extract Transcript
        vcon_dict = json.loads(vcon_json)
        analyses = vcon_dict.get("analysis", [])
        transcript_text = None
        for a in analyses:
            if a.get("type") == "transcript" and a.get("vendor") == "openai-whisper":
                transcript_text = a.get("body", {}).get("text")
                break
                
        if not transcript_text:
            logger.error(f"No transcript found in vCon {session_id}.")
            if os.path.exists(temp_vcon_path): os.remove(temp_vcon_path)
            return False
            
        # 3. Generate Semantic Analysis via GPT-4o
        try:
            analysis_result = AIService.generate_semantic_analysis(transcript_text)
        except Exception as e:
            logger.error(f"Instructor semantic analysis failed for {session_id}: {e}")
            if os.path.exists(temp_vcon_path): os.remove(temp_vcon_path)
            return False
            
        # 4. Update Vcon
        builder = VconBuilder.from_json(vcon_json, session_id, cohort_id)
        builder.add_analysis(
            analysis_type="semantic",
            result=analysis_result,
            vendor="openai-gpt4o-instructor"
        )
        updated_vcon_json = builder.serialize()
        
        with open(temp_vcon_path, "w") as f:
            f.write(updated_vcon_json)
            
        new_vcon_url = CloudinaryService.upload_file_from_path(
            temp_vcon_path, 
            f"vcon_{session_id}_analyzed.json"
        )
        os.remove(temp_vcon_path)
        
        # 5. Caching metrics to Database
        try:
            with get_task_db() as db:
                session_db = db.execute(select(Session).where(Session.id == session_id)).scalar_one_or_none()
                if session_db:
                    session_db.vcon_file_url = new_vcon_url
                    session_db.summary = analysis_result.get("summary")
                    session_db.topics_json = analysis_result.get("topics", [])
                    session_db.action_items_json = analysis_result.get("action_items", [])
                    session_db.questions_asked_json = analysis_result.get("questions_asked", [])
                    session_db.talk_listen_ratios_json = analysis_result.get("talk_listen_ratios", {})
                    session_db.status = "completed"
                    db.commit()
        except Exception as e:
            logger.error(f"Failed to save semantic analysis metrics: {e}")
            return False
        
        return True
            
    success = process_semantic_analysis()
    if success:
        logger.info(f"Successfully processed semantic analysis for {session_id}.")
        return {"session_id": session_id, "status": "completed"}
    else:
        try:
            with get_task_db() as db:
                session_db = db.execute(select(Session).where(Session.id == session_id)).scalar_one_or_none()
                if session_db:
                    session_db.status = "failed"
                    db.commit()
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")
        return {"session_id": session_id, "status": "analysis_failed"}
