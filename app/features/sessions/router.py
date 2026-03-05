from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from typing import Annotated
from app.features.sessions.schemas import UploadResponse, SessionResponse
from app.features.sessions.service import SessionsService
from app.features.sessions.dependencies import get_sessions_service
from app.core.responses import SuccessResponse, APIResponse

router = APIRouter()

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
