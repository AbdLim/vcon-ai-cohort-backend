from typing import Optional, Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.cohorts.repository import CohortRepository
from app.features.cohorts.models import Cohort
from app.features.cohorts.schemas import CohortCreate, CohortUpdate

class CohortService:
    def __init__(self, session: AsyncSession):
        self.repository = CohortRepository(session)
        self.session = session

    async def get_cohort(self, cohort_id: int) -> Cohort:
        cohort = await self.repository.get_by_id(cohort_id)
        if not cohort:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cohort with id {cohort_id} not found"
            )
        return cohort

    async def get_cohorts(self, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None) -> Sequence[Cohort]:
        if organization_id:
            return await self.repository.get_by_organization(organization_id, skip, limit)
        return await self.repository.get_all(skip, limit)

    async def create_cohort(self, data: CohortCreate) -> Cohort:
        cohort = await self.repository.create(
            name=data.name, 
            organization_id=data.organization_id, 
            description=data.description
        )
        await self.session.commit()
        return cohort
        
    async def update_cohort(self, cohort_id: int, data: CohortUpdate) -> Cohort:
        cohort = await self.get_cohort(cohort_id)
        
        if data.name is not None:
            cohort.name = data.name
        if data.description is not None:
            cohort.description = data.description
        if data.organization_id is not None:
            cohort.organization_id = data.organization_id
            
        updated_cohort = await self.repository.update(cohort)
        await self.session.commit()
        return updated_cohort

    async def delete_cohort(self, cohort_id: int) -> None:
        cohort = await self.get_cohort(cohort_id)
        await self.repository.delete(cohort)
        await self.session.commit()
