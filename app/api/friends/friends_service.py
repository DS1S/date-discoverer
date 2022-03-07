from datetime import date

from fastapi import HTTPException, status

from app.api.friends.friends_models import (
    OperationOnUserModel,
)
from app.lib.auth.auth_models import User
from app.db.mongo_driver import user_collection


async def _find_user_to_operate_on(email):
    user_to_process = await user_collection.find_one({"email": email})

    if not user_to_process:
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email <{email} not found."
        )

    return user_to_process


async def add_user_to_block_list(user: User, request: OperationOnUserModel):
    user_to_block = await _find_user_to_operate_on(request.email)

    if not user_to_block:
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email <{request.email} not found."
        )

    await user_collection.find_one_and_update(
        {"_id": user.id},
        {
            "$expr": {
                "$cond": {
                    "if": {
                        "blockedUsers": {"$nin": [user_to_block["_id"]]}
                    },
                    "then": {
                        "$push": {"blockedUsers": user_to_block["_id"]}
                    }
                }
            }
        }
    )

    response = {
        "blocked_user": request.email,
        "date_blocked": date.today(),
        "msg": f"User with email ${request.email} has been blocked successfully"
    }

    return response


async def add_to_friend_requests_of_user(
    user: User,
    request: OperationOnUserModel
):
    user_to_send = await _find_user_to_operate_on(request.email)

    if user.id in user_to_send["blockedUsers"]:
        return {
            "friend_request_sent": True,
            "date_sent": date.today(),
            "msg": f"User with email ${request.email} "
                   f"has you blocked, no friend request was sent."
        }

    await user_collection.find_one_and_update(
        {"_id": user_to_send["_id"]},
        {
            "$expr": {
                "$cond": {
                    "if": {
                        "friendRequests.email": {"$nin": [user.email]}
                    },
                    "then": {
                        "$push": {"friendRequests": request.dict(by_alias=True)}
                    }
                }
            }
        }
    )

    response = {
        "friend_request_sent": True,
        "date_sent": date.today(),
        "msg": f"User with email ${request.email} "
               f"has been sent a friend request."
    }

    return response


async def add_user_to_friends_list(
    user: User,
    request: OperationOnUserModel
):
    for index, friend_request in enumerate(user.friend_requests):
        if friend_request.email == request.email:
            friend_info = user.friend_requests.pop(index)
            user.friends.append(
                (await user_collection.find_one({
                    "email": friend_info.email
                }))["_id"]
            )
            await user_collection.find_one_and_update(
                {"_id": user.id},
                {
                    "$set": {
                        "friends": user.friends,
                        "friendRequests": user.friend_requests
                    }
                }
            )
            return {
                "msg": f"User with email {request.email} "
                       f"has been added to your friends list.",
                "date_accepted": date.today()
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with email {request.email} "
               f"has not sent you a friend request."
    )


async def show_all_friend_requests(user: User):
    return user.friend_requests
