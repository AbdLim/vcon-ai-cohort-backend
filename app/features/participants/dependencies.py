from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.features.participants.service import ParticipantService

async def get_participant_service(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ParticipantService:
    return ParticipantService(session)
