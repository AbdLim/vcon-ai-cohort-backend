from fastapi import APIRouter, Depends, status, Query
from typing import Annotated, List, Optional
from app.core.responses import SuccessResponse, APIResponse
from app.features.cohorts.schemas import CohortResponse, CohortCreate, CohortUpdate, CohortWithSessionsResponse
from app.features.cohorts.service import CohortService
from app.features.cohorts.dependencies import get_cohort_service

router = APIRouter()

@router.get("/", response_model=APIResponse[List[CohortResponse]])
async def list_cohorts(
    service: Annotated[CohortService, Depends(get_cohort_service)],
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[int] = None
):
    cohorts = await service.get_cohorts(skip=skip, limit=limit, organization_id=organization_id)
    return SuccessResponse.create("Cohorts retrieved successfully", data=cohorts)

@router.post("/", response_model=APIResponse[CohortResponse], status_code=status.HTTP_201_CREATED)
async def create_cohort(
    data: CohortCreate,
    service: Annotated[CohortService, Depends(get_cohort_service)]
):
    cohort = await service.create_cohort(data)
    return SuccessResponse.create("Cohort created successfully", data=cohort)

@router.get("/{cohort_id}", response_model=APIResponse[CohortWithSessionsResponse])
async def get_cohort(
    cohort_id: int,
    service: Annotated[CohortService, Depends(get_cohort_service)]
):
    cohort = await service.get_cohort(cohort_id)
    return SuccessResponse.create("Cohort retrieved successfully", data=cohort)

@router.patch("/{cohort_id}", response_model=APIResponse[CohortResponse])
async def update_cohort(
    cohort_id: int,
    data: CohortUpdate,
    service: Annotated[CohortService, Depends(get_cohort_service)]
):
    cohort = await service.update_cohort(cohort_id, data)
    return SuccessResponse.create("Cohort updated successfully", data=cohort)

@router.delete("/{cohort_id}", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
async def delete_cohort(
    cohort_id: int,
    service: Annotated[CohortService, Depends(get_cohort_service)]
):
    await service.delete_cohort(cohort_id)
    return SuccessResponse.create("Cohort deleted successfully", data={"id": cohort_id})
