from typing import List

from fastapi import APIRouter, Depends

from app.api.admin.admin_models import (
    BanUsersRequestModel,
    BanUsersResponseModel
)

from app.lib.auth.auth_models import (
    Roles,
    User
)

from app.api.admin.admin_service import (
    disable_user_accounts_by_email_and_id,
    show_all_users
)

from app.lib.auth.auth_service import get_user_with_roles

admin_router = APIRouter()


@admin_router.post("/ban-users", response_model=BanUsersResponseModel)
async def ban_users(
    request: BanUsersRequestModel,
    user: User = Depends(get_user_with_roles([Roles.ADMIN]))
):
    return await disable_user_accounts_by_email_and_id(user, request)


@admin_router.post("/retrieve-users", response_model=List[User])
async def retrieve_users(
    user: User = Depends(get_user_with_roles([Roles.ADMIN]))
):
    return await show_all_users()
