import uuid
import tempfile
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.sessions.schemas import UploadResponse
from app.features.sessions.models import Session
from app.features.sessions.repository import SessionsRepository
from app.worker.tasks import process_session_task
from typing import Optional, Sequence

class SessionsService:
    def __init__(self, session: AsyncSession):
        self.repository = SessionsRepository(session)
        self.session = session

    async def get_session(self, session_id: int) -> Session:
        session_record = await self.repository.get_by_id(session_id)
        if not session_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with id {session_id} not found"
            )
        return session_record

    async def get_sessions(self, skip: int = 0, limit: int = 100, cohort_id: Optional[int] = None) -> Sequence[Session]:
        if cohort_id:
            return await self.repository.get_by_cohort(cohort_id, skip, limit)
        return await self.repository.get_all(skip, limit)

    async def upload_session(self, title: str, cohort_id: int, file: UploadFile) -> UploadResponse:
        """
        Handles the initialization of a session upload.
        Creates a session record in the database with "processing" status and dispatches a Celery task.
        """
        # 1. Create the session database record
        new_session = Session(
            title=title,
            cohort_id=cohort_id,
            status="processing"
        )
        self.session.add(new_session)
        await self.session.flush() # Get the database ID
        
        # 2. Dispatch the background Celery task
        # We pass the session_id so the worker can update the DB later.
        # In a real scenario, we might upload the file to Cloudinary right here 
        # OR we might pass the file path/bytes to the worker. Since Celery needs serializable args,
        # we'll use a mocked local path or assume the file is passed differently.
        # For this MVP endpoint, we'll let the worker handle the mock upload to Cloudinary.
        
        file_content = await file.read()
        
        # Save to temporary file to avoid sending raw bytes through Redis/Celery JSON serialization
        import os
        tmp_fd, tmp_path = tempfile.mkstemp()
        with os.fdopen(tmp_fd, 'wb') as tmp:
            tmp.write(file_content)
        
        task = process_session_task.delay(
            session_id=new_session.id, 
            filename=file.filename,
            filepath=tmp_path
        )
        
        await self.session.commit()
        
        # 3. Return the response ID for polling status later
        return UploadResponse(
            task_id=task.id,
            status="processing"
        )

    async def import_session_url(self, title: str, cohort_id: int, url: str) -> UploadResponse:
        """
        Handles the initialization of a session upload from a URL.
        Creates a session record in the database with "processing" status and dispatches a Celery task.
        """
        new_session = Session(
            title=title,
            cohort_id=cohort_id,
            status="processing"
        )
        self.session.add(new_session)
        await self.session.flush() # Get the database ID
        
        task = process_session_task.delay(
            session_id=new_session.id, 
            filename=None,
            filepath=None,
            file_url=url
        )
        
        await self.session.commit()
        
        return UploadResponse(
            task_id=task.id,
            status="processing"
        )
