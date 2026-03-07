from fastapi import APIRouter, Depends, status
from typing import Annotated, List
from app.core.responses import SuccessResponse, APIResponse
from app.features.organizations.schemas import OrganizationResponse, OrganizationCreate, OrganizationUpdate
from app.features.organizations.service import OrganizationService
from app.features.organizations.dependencies import get_organization_service

router = APIRouter()

@router.get("/", response_model=APIResponse[List[OrganizationResponse]])
async def list_organizations(
    service: Annotated[OrganizationService, Depends(get_organization_service)],
    skip: int = 0,
    limit: int = 100
):
    orgs = await service.get_organizations(skip=skip, limit=limit)
    return SuccessResponse.create("Organizations retrieved successfully", data=orgs)

@router.post("/", response_model=APIResponse[OrganizationResponse], status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    service: Annotated[OrganizationService, Depends(get_organization_service)]
):
    org = await service.create_organization(data)
    return SuccessResponse.create("Organization created successfully", data=org)

@router.get("/{org_id}", response_model=APIResponse[OrganizationResponse])
async def get_organization(
    org_id: int,
    service: Annotated[OrganizationService, Depends(get_organization_service)]
):
    org = await service.get_organization(org_id)
    return SuccessResponse.create("Organization retrieved successfully", data=org)

@router.patch("/{org_id}", response_model=APIResponse[OrganizationResponse])
async def update_organization(
    org_id: int,
    data: OrganizationUpdate,
    service: Annotated[OrganizationService, Depends(get_organization_service)]
):
    org = await service.update_organization(org_id, data)
    return SuccessResponse.create("Organization updated successfully", data=org)

@router.delete("/{org_id}", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
async def delete_organization(
    org_id: int,
    service: Annotated[OrganizationService, Depends(get_organization_service)]
):
    await service.delete_organization(org_id)
    return SuccessResponse.create("Organization deleted successfully", data={"id": org_id})
