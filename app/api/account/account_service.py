from datetime import timedelta

from fastapi import HTTPException, status

from app.db.mongo_driver import user_collection
from app.lib.auth.auth_models import Roles

from app.api.account.account_models import RegisterAccountResponse

from app.lib.auth.auth_service import (
    authenticate_user,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


async def create_new_account(email, password):
    user = await user_collection.find_one({"email": "email"})
    if not user:
        user_data = {
            "email": email,
            "hashed_password": get_password_hash(password),
            "disabled": False,
            "roles": [Roles.BASE_USER],
            "friends": [],
            "blockedUsers": [],
            "friendRequests": [],
            "banReason": None,
            "banMsg": None,
            "bannerId": None
        }

        await user_collection.insert_one(
            user_data
        )

        return RegisterAccountResponse(
            account_details={"email": email, "password": password},
            success=True,
            msg="User has been successfully created."
        )
    return RegisterAccountResponse(
        success=False,
        msg="Email already exists."
    )


async def login_account(username, password):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}




