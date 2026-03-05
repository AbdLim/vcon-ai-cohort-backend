from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Query
from typing import Annotated, List, Optional
from app.features.sessions.schemas import UploadResponse, SessionResponse, UrlUploadRequest
from app.features.sessions.service import SessionsService
from app.features.sessions.dependencies import get_sessions_service
from app.core.responses import SuccessResponse, APIResponse

router = APIRouter()

@router.get("/", response_model=APIResponse[List[SessionResponse]])
async def list_sessions(
    service: Annotated[SessionsService, Depends(get_sessions_service)],
    skip: int = 0,
    limit: int = 100,
    cohort_id: Optional[int] = None
):
    sessions = await service.get_sessions(skip=skip, limit=limit, cohort_id=cohort_id)
    return SuccessResponse.create("Sessions retrieved successfully", data=sessions)

@router.get("/{session_id}", response_model=APIResponse[SessionResponse])
async def get_session(
    session_id: int,
    service: Annotated[SessionsService, Depends(get_sessions_service)]
):
    session_record = await service.get_session(session_id)
    return SuccessResponse.create("Session retrieved successfully", data=session_record)

@router.post("/upload", response_model=APIResponse[UploadResponse], status_code=status.HTTP_202_ACCEPTED)
async def upload_session(
    title: Annotated[str, Form(...)],
    cohort_id: Annotated[int, Form(...)],
    file: Annotated[UploadFile, File(...)],
    service: Annotated[SessionsService, Depends(get_sessions_service)]
):
    """
    Upload a session recording. The request will return a 202 status and a task ID immediately,
    while processing the file in the background.
    """
    result = await service.upload_session(
        title=title,
        cohort_id=cohort_id,
        file=file
    )
    return SuccessResponse.create("Session upload initiated", data=result)

@router.post("/url", response_model=APIResponse[UploadResponse], status_code=status.HTTP_202_ACCEPTED)
async def import_session_url(
    request: UrlUploadRequest,
    service: Annotated[SessionsService, Depends(get_sessions_service)]
):
    """
    Import a session recording from a URL. The request will return a 202 status and a task ID immediately,
    while processing the URL in the background. Does not require multipart/form-data.
    """
    result = await service.import_session_url(
        title=request.title,
        cohort_id=request.cohort_id,
        url=request.url
    )
    return SuccessResponse.create("Session URL import initiated", data=result)
