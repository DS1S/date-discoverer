from typing import List

from fastapi import APIRouter, Depends

from app.api.friends.friends_models import (
    OperationOnUserModel,
    FriendRequestResponseModel,
    BlockUserResponseModel,
    FriendRequestAcceptedResponse,
    FriendRemovedResponse
)

from app.api.friends.friends_service import (
    add_user_to_block_list,
    add_user_to_friends_list,
    add_to_friend_requests_of_user,
    show_all_friend_requests
)

from app.lib.auth.auth_service import get_user_with_roles
from app.lib.auth.auth_models import Roles, User

friends_router = APIRouter()


@friends_router.post(
    "/block-user",
    response_model=BlockUserResponseModel
)
async def block_user(
    request: OperationOnUserModel,
    user: User = Depends(get_user_with_roles([Roles.BASE_USER]))
):
    return await add_user_to_block_list(user, request)


@friends_router.post(
    "/send-friend-request",
    response_model=FriendRequestResponseModel
)
async def send_friend_request(
    request: OperationOnUserModel,
    user: User = Depends(get_user_with_roles([Roles.BASE_USER]))
):
    return await add_to_friend_requests_of_user(user, request)


@friends_router.post(
    "/accept-friend-request",
    response_model=FriendRequestAcceptedResponse
)
async def accept_friend_request(
    request: OperationOnUserModel,
    user: User = Depends(get_user_with_roles([Roles.BASE_USER]))
):
    return await add_user_to_friends_list(user, request)


@friends_router.post(
    "/remove-friend",
    response_model=FriendRemovedResponse
)
async def remove_friend(
    request: OperationOnUserModel,
    user: User = Depends(get_user_with_roles([Roles.BASE_USER]))
):
    pass

@friends_router.get(
    "/view-friend-requests",
    response_model=List[OperationOnUserModel]
)
async def view_friend_requests(
    user: User = Depends(get_user_with_roles([Roles.BASE_USER]))
):
    return await show_all_friend_requests(user)
