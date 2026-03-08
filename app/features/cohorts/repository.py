from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.cohorts.models import Cohort

class CohortRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, cohort_id: int) -> Optional[Cohort]:
        statement = select(Cohort).options(selectinload(Cohort.sessions)).where(Cohort.id == cohort_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Cohort]:
        statement = select(Cohort).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()
        
    async def get_by_organization(self, organization_id: int, skip: int = 0, limit: int = 100) -> Sequence[Cohort]:
        statement = select(Cohort).where(Cohort.organization_id == organization_id).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(self, name: str, organization_id: int, description: Optional[str] = None) -> Cohort:
        cohort = Cohort(name=name, organization_id=organization_id, description=description)
        self.session.add(cohort)
        await self.session.flush()
        return cohort
        
    async def update(self, cohort: Cohort) -> Cohort:
        await self.session.flush()
        return cohort
        
    async def delete(self, cohort: Cohort) -> None:
        await self.session.delete(cohort)
        await self.session.flush()
