from typing import Optional, Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.participants.repository import ParticipantRepository
from app.features.participants.models import Participant
from app.features.participants.schemas import ParticipantCreate, ParticipantUpdate, ParticipantMetricsUpdate

class ParticipantService:
    def __init__(self, session: AsyncSession):
        self.repository = ParticipantRepository(session)
        self.session = session

    async def get_participant(self, participant_id: int) -> Participant:
        participant = await self.repository.get_by_id(participant_id)
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Participant with id {participant_id} not found"
            )
        return participant

    async def get_participants(self, skip: int = 0, limit: int = 100, cohort_id: Optional[int] = None, user_id: Optional[int] = None) -> Sequence[Participant]:
        if cohort_id:
            return await self.repository.get_by_cohort(cohort_id, skip, limit)
        if user_id:
            return await self.repository.get_by_user(user_id, skip, limit)
        return await self.repository.get_all(skip, limit)

    async def create_participant(self, data: ParticipantCreate) -> Participant:
        participant = await self.repository.create(
            user_id=data.user_id,
            cohort_id=data.cohort_id,
            role=data.role,
            metadata_json=data.metadata_json
        )
        await self.session.commit()
        return participant
        
    async def update_participant(self, participant_id: int, data: ParticipantUpdate) -> Participant:
        participant = await self.get_participant(participant_id)
        
        if data.role is not None:
            participant.role = data.role
        if data.metadata_json is not None:
            participant.metadata_json = data.metadata_json
            
        updated = await self.repository.update(participant)
        await self.session.commit()
        return updated
        
    async def update_metrics(self, participant_id: int, data: ParticipantMetricsUpdate) -> Participant:
        participant = await self.get_participant(participant_id)
        
        if data.sessions_attended is not None:
            participant.sessions_attended = data.sessions_attended
        if data.average_talk_time_pct is not None:
            participant.average_talk_time_pct = data.average_talk_time_pct
        if data.health_score is not None:
            participant.health_score = data.health_score
            
        updated = await self.repository.update(participant)
        await self.session.commit()
        return updated

    async def delete_participant(self, participant_id: int) -> None:
        participant = await self.get_participant(participant_id)
        await self.repository.delete(participant)
        await self.session.commit()
