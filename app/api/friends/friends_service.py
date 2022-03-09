from datetime import date

from fastapi import HTTPException, status

from app.api.friends.friends_models import (
    OperationOnUserModel,
)
from app.lib.auth.auth_models import User
from app.db.mongo_driver import user_collection


def _pop_and_return(v, x: list):
    for index, val in enumerate(x):
        if val == v:
            x.pop(index)
            return x


async def _find_user_to_operate_on(email):
    user_to_process = await user_collection.find_one({"email": email})

    if not user_to_process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email <{email}> not found."
        )

    return user_to_process


async def _update_for_block_on_user(user, user_to_block):
    await user_collection.find_one_and_update(
        {"_id": user.id},
        [{"$set": {
            "blockedUsers": {
                "$cond": {
                    "if": {
                        "$not": {"$in": [user_to_block["_id"], "$blockedUsers"]}
                    },
                    "then": user.blocked_users + [user_to_block["_id"]],
                    "else": "$blockedUsers"
                }
            },
            "friendRequests": {
                "$cond": {
                    "if": {
                        "$in": [user_to_block["email"], "$friendRequests.email"]
                    },
                    "then": _pop_and_return(
                        user_to_block["email"],
                        user.friend_requests
                    ),
                    "else": "$friendRequests"
                }
            },
            "friends": {
                "$cond": {
                    "if": {
                        "$in": [user_to_block["_id"], "$friends"]
                    },
                    "then": _pop_and_return(
                        user_to_block["_id"],
                        user.friends
                    ),
                    "else": "$friends"
                }
            }
        }}]
    )


async def add_user_to_block_list(user: User, request: OperationOnUserModel):
    user_to_block = await _find_user_to_operate_on(request.email)

    if not user_to_block:
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email <{request.email} not found."
        )

    await _update_for_block_on_user(user, user_to_block)
    await _update_for_block_on_user(
        User(**user_to_block),
        user.dict(by_alias=True)
    )

    response = {
        "blocked_user": request.email,
        "date_blocked": date.today(),
        "msg": f"User with email {request.email} has been blocked successfully"
    }

    return response


async def add_to_friend_requests_of_user(
    user: User,
    request: OperationOnUserModel
):
    user_to_send = User(**(await _find_user_to_operate_on(request.email)))

    if user.id in user_to_send.blocked_users:
        return {
            "friend_request_sent": False,
            "date_sent": date.today(),
            "msg": f"User with email {request.email}"
                   f" has you blocked, no friend request was sent."
        }

    if user.id in user_to_send.friends:
        return {
            "friend_request_sent": False,
            "date_sent": date.today(),
            "msg": f"User with email {request.email}"
                   f" already has you added."
        }

    friend_request_emails = [req.email for req in user_to_send.friend_requests]
    if user.email in friend_request_emails:
        return {
            "friend_request_sent": False,
            "date_sent": date.today(),
            "msg": f"User with email {request.email}"
                   f" is pending previous friend request."
        }

    await user_collection.find_one_and_update(
        {"_id": user_to_send["_id"]},
        [{"$set": {
            "friendRequests": {
                "$cond": {
                    "if": {
                        "$not": {"$in": [user.email, "$friendRequests.email"]}
                    },
                    "then": user_to_send["friendRequests"] +
                    [{"email": user.email, "msg": request.msg}],
                    "else": "$friendRequests"
                }
            }
        }}]
    )

    response = {
        "friend_request_sent": True,
        "date_sent": date.today(),
        "msg": f"User with email {request.email} "
               f"has been sent a friend request."
    }

    return response


async def add_user_to_friends_list(
    user: User,
    request: OperationOnUserModel
):
    friend_to_add = await _find_user_to_operate_on(request.email)

    if friend_to_add["_id"] in user.blocked_users:
        return {
            "msg": f"User with email {request.email} "
                   f"is on your blocked list.",
            "date_accepted": date.today()
        }

    for index, friend_request in enumerate(user.friend_requests):
        if friend_request.email == request.email:
            friend_info = user.friend_requests.pop(index)

            friend_id = (await user_collection.find_one_and_update(
                {"email": friend_info.email},
                {"$push": {"friends": user.id}}
            ))["_id"]

            user.friends.append(friend_id)

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


async def remove_friend_from_list(
    user: User,
    request: OperationOnUserModel
):
    friend_to_remove = User(**(await _find_user_to_operate_on(request.email)))

    if friend_to_remove.id not in user.friends:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email <{request.email}> "
                   f"not found in friends list."
        )

    user.friends.pop(user.friends.index(friend_to_remove.id))
    friend_to_remove.friends.pop(friend_to_remove.friends.index(user.id))

    await user_collection.find_one_and_update(
        {"_id": user.id},
        {"$set": {"friends": user.friends}}
    )

    await user_collection.find_one_and_update(
        {"_id": friend_to_remove.id},
        {"$set": {"friends": friend_to_remove.friends}}
    )

    return {
        "msg": f"Friend {request.email} has been removed.",
        "date_removed": date.today()
    }


async def show_all_friend_requests(user: User):
    return user.friend_requests
