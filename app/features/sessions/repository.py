from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.sessions.models import Session

class SessionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, session_id: int) -> Optional[Session]:
        statement = select(Session).where(Session.id == session_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Session]:
        statement = select(Session).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()
        
    async def get_by_cohort(self, cohort_id: int, skip: int = 0, limit: int = 100) -> Sequence[Session]:
        statement = select(Session).where(Session.cohort_id == cohort_id).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()
