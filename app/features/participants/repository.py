from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.participants.models import Participant

class ParticipantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, participant_id: int) -> Optional[Participant]:
        statement = select(Participant).where(Participant.id == participant_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Participant]:
        statement = select(Participant).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()
        
    async def get_by_cohort(self, cohort_id: int, skip: int = 0, limit: int = 100) -> Sequence[Participant]:
        statement = select(Participant).where(Participant.cohort_id == cohort_id).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Participant]:
        statement = select(Participant).where(Participant.user_id == user_id).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(self, **kwargs) -> Participant:
        participant = Participant(**kwargs)
        self.session.add(participant)
        await self.session.flush()
        return participant
        
    async def update(self, participant: Participant) -> Participant:
        await self.session.flush()
        return participant
        
    async def delete(self, participant: Participant) -> None:
        await self.session.delete(participant)
        await self.session.flush()
