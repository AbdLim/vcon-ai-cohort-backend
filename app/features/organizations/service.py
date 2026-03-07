from typing import Optional, Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.organizations.repository import OrganizationRepository
from app.features.cohorts.models import Organization
from app.features.organizations.schemas import OrganizationCreate, OrganizationUpdate

class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.repository = OrganizationRepository(session)
        self.session = session

    async def get_organization(self, org_id: int) -> Organization:
        org = await self.repository.get_by_id(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with id {org_id} not found"
            )
        return org

    async def get_organizations(self, skip: int = 0, limit: int = 100) -> Sequence[Organization]:
        return await self.repository.get_all(skip, limit)

    async def create_organization(self, data: OrganizationCreate) -> Organization:
        org = await self.repository.create(name=data.name, description=data.description)
        await self.session.commit()
        return org
        
    async def update_organization(self, org_id: int, data: OrganizationUpdate) -> Organization:
        org = await self.get_organization(org_id)
        
        if data.name is not None:
            org.name = data.name
        if data.description is not None:
            org.description = data.description
            
        updated_org = await self.repository.update(org)
        await self.session.commit()
        return updated_org

    async def delete_organization(self, org_id: int) -> None:
        org = await self.get_organization(org_id)
        await self.repository.delete(org)
        await self.session.commit()
