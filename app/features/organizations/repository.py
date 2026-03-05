from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.cohorts.models import Organization

class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, org_id: int) -> Optional[Organization]:
        statement = select(Organization).where(Organization.id == org_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Organization]:
        statement = select(Organization).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(self, name: str, description: Optional[str] = None) -> Organization:
        org = Organization(name=name, description=description)
        self.session.add(org)
        await self.session.flush()
        return org
        
    async def update(self, org: Organization) -> Organization:
        await self.session.flush()
        return org
        
    async def delete(self, org: Organization) -> None:
        await self.session.delete(org)
        await self.session.flush()
