from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.lib.auth.auth_models import Token


from app.api.account.account_models import (
    RegisterAccountRequest,
    RegisterAccountResponse
)

from app.api.account.account_service import create_new_account, login_account

account_router = APIRouter()


@account_router.post(
    "/register",
    response_model=RegisterAccountResponse
)
async def register_account(request: RegisterAccountRequest):
    return await create_new_account(request.email, request.password)


@account_router.post(
    "/login",
    response_model=Token
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_account(form_data.username, form_data.password)
