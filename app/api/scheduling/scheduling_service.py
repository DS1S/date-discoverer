from bson import ObjectId

from fastapi import HTTPException, status

from app.db.model_utils import PyObjectId
from app.db.mongo_driver import dates_collection, user_collection
from app.lib.auth.auth_models import User
from app.api.scheduling.scheduling_models import (
    ScheduledDateRequestModel,
    ScheduledDateModel,
    ScheduledDateModelResponse,
    Status
)


async def _lookup_schedule(user: User, schedule_id: PyObjectId):
    schedule = await dates_collection.find_one({"_id": schedule_id})

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with id {schedule_id} not found."
        )

    schedule = ScheduledDateModel(**schedule)

    if schedule.receiver_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Cannot accept date."
        )

    if schedule.status != Status.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Schedule not in proper state."
        )

    if schedule.sender_id in user.blocked_users:
        await dates_collection.find_one_and_delete({"_id": schedule_id})
        return False, {
            "request_msg": "You are blocked by the user, "
                           "did not send request",
            "successfullySent": False
        }

    return True, schedule


async def retrieve_all_dates_belonging_to_user(user: User, status_: Status):
    dates = await dates_collection.find(
        {
            "receiverId": user.id,
            "status": status_.value,
            "senderId": {"$nin": user.blocked_users}
        }
    ).to_list(length=None)

    return dates


async def send_date_request_to_receiver(
    request: ScheduledDateRequestModel,
    user: User,
    receiver_id: PyObjectId
):
    user_to_receive = user_collection.find_one({"_id": receiver_id})

    if user_to_receive:
        user_to_receive = User(**user_to_receive)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {receiver_id} not found."
        )

    if user.id in user_to_receive.blocked_users:
        return {
            "request_msg": "You are blocked by the user, "
                           "did not send request",
            "successfullySent": False
        }

    scheduled_date = ScheduledDateModel(
        receiver_id=receiver_id,
        sender_id=user.id,
        status=Status.PENDING,
        **request.dict()
    )

    scheduled_date.id = ObjectId()

    res = await dates_collection.insert_one(
        scheduled_date.dict(by_alias=True)
    )

    created_date = await dates_collection.find_one({"_id": res.inserted_id})

    return ScheduledDateModelResponse(
        successfully_sent=True,
        request_msg="Date sent successfully to the receiver.",
        **created_date
    )


async def accept_date_request_from_sender(
    schedule_id: PyObjectId,
    user: User
):
    success, res = await _lookup_schedule(user, schedule_id)

    if not success:
        return res

    await dates_collection.find_one_and_update(
        {"_id": schedule_id},
        {"$set": {"status": Status.APPROVED}}
    )

    res.status = Status.APPROVED
    return res


async def reject_date_request_from_sender(
    schedule_id: PyObjectId,
    user: User
):
    success, res = await _lookup_schedule(user, schedule_id)

    if not success:
        return res

    await dates_collection.find_one_and_update(
        {"_id": schedule_id},
        {"$set": {"status": Status.REJECTED}}
    )

    res.status = Status.REJECTED
    return res
