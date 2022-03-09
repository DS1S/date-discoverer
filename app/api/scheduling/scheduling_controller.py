from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query

from app.api.scheduling.scheduling_models import (
    ScheduledDateModel
)
from app.db.model_utils import PyObjectId
from app.lib.auth.auth_models import (
    User,
    Roles
)
from app.lib.auth.auth_service import get_user_with_roles
from app.api.scheduling.scheduling_service import (
    retrieve_all_dates_belonging_to_user,
    send_date_request_to_receiver,
    accept_date_request_from_sender,
    reject_date_request_from_sender
)
from app.api.scheduling.scheduling_models import (
    ScheduledDateRequestModel,
    ScheduledDateModelResponse,
    DateStatus
)

scheduling_router = APIRouter()


@scheduling_router.get(
    "/list-dates",
    response_model=List[ScheduledDateModel]
)
async def get_schedule_requests(
    status: DateStatus = Query(...),
    user: User = Depends(get_user_with_roles([Roles.BASE_USER]))
):
    return await retrieve_all_dates_belonging_to_user(user, status)


@scheduling_router.post(
    "/send-date-proposal/{receiverId}",
    response_model=ScheduledDateModelResponse
)
async def send_date_request(
    request: ScheduledDateRequestModel,
    receiver_id: PyObjectId = Path(..., alias="receiverId"),
    user: User = Depends(get_user_with_roles([Roles.BASE_USER]))
):
    return await send_date_request_to_receiver(request, user, receiver_id)


@scheduling_router.post(
    "/accept-date-proposal/{scheduleId}",
    response_model=ScheduledDateModelResponse
)
async def accept_date_request(
    schedule_id: PyObjectId = Path(..., alias="scheduleId"),
    user: User = Depends(get_user_with_roles([Roles.BASE_USER]))
):
    return await accept_date_request_from_sender(schedule_id, user)


@scheduling_router.post(
    "/reject-date-proposal/{scheduleId}",
    response_model=ScheduledDateModelResponse
)
async def reject_date_request(
    schedule_id: PyObjectId = Path(..., alias="scheduleId"),
    user: User = Depends(get_user_with_roles([Roles.BASE_USER]))
):
    return await reject_date_request_from_sender(schedule_id, user)
