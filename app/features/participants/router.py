from fastapi import APIRouter, Depends, status
from typing import Annotated, List, Optional
from app.core.responses import SuccessResponse, APIResponse
from app.features.participants.schemas import ParticipantResponse, ParticipantCreate, ParticipantUpdate, ParticipantMetricsUpdate
from app.features.participants.service import ParticipantService
from app.features.participants.dependencies import get_participant_service

router = APIRouter()

@router.get("/", response_model=APIResponse[List[ParticipantResponse]])
async def list_participants(
    service: Annotated[ParticipantService, Depends(get_participant_service)],
    skip: int = 0,
    limit: int = 100,
    cohort_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    participants = await service.get_participants(skip=skip, limit=limit, cohort_id=cohort_id, user_id=user_id)
    return SuccessResponse.create("Participants retrieved successfully", data=participants)

@router.post("/", response_model=APIResponse[ParticipantResponse], status_code=status.HTTP_201_CREATED)
async def create_participant(
    data: ParticipantCreate,
    service: Annotated[ParticipantService, Depends(get_participant_service)]
):
    participant = await service.create_participant(data)
    return SuccessResponse.create("Participant created successfully", data=participant)

@router.get("/{participant_id}", response_model=APIResponse[ParticipantResponse])
async def get_participant(
    participant_id: int,
    service: Annotated[ParticipantService, Depends(get_participant_service)]
):
    participant = await service.get_participant(participant_id)
    return SuccessResponse.create("Participant retrieved successfully", data=participant)

@router.patch("/{participant_id}", response_model=APIResponse[ParticipantResponse])
async def update_participant(
    participant_id: int,
    data: ParticipantUpdate,
    service: Annotated[ParticipantService, Depends(get_participant_service)]
):
    participant = await service.update_participant(participant_id, data)
    return SuccessResponse.create("Participant updated successfully", data=participant)

@router.patch("/{participant_id}/metrics", response_model=APIResponse[ParticipantResponse])
async def update_participant_metrics(
    participant_id: int,
    data: ParticipantMetricsUpdate,
    service: Annotated[ParticipantService, Depends(get_participant_service)]
):
    participant = await service.update_metrics(participant_id, data)
    return SuccessResponse.create("Participant metrics updated successfully", data=participant)

@router.delete("/{participant_id}", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
async def delete_participant(
    participant_id: int,
    service: Annotated[ParticipantService, Depends(get_participant_service)]
):
    await service.delete_participant(participant_id)
    return SuccessResponse.create("Participant deleted successfully", data={"id": participant_id})
