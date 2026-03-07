from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.features.sessions.service import SessionsService

def get_sessions_service(db: AsyncSession = Depends(get_db)) -> SessionsService:
    return SessionsService(session=db)
