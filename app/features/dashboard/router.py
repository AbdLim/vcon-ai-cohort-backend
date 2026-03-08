from fastapi import APIRouter, Depends
from typing import Annotated
from app.core.responses import SuccessResponse, APIResponse
from app.features.dashboard.schemas import DashboardOverviewResponse
from app.features.dashboard.service import DashboardService
from app.features.dashboard.dependencies import get_dashboard_service

router = APIRouter()

@router.get("/overview", response_model=APIResponse[DashboardOverviewResponse])
async def get_overview(
    service: Annotated[DashboardService, Depends(get_dashboard_service)]
):
    overview_data = await service.get_overview()
    return SuccessResponse.create("Dashboard overview retrieved successfully", data=overview_data)
