from typing import List, Optional
from enum import Enum

from pydantic import Field, BaseModel

from app.db.model_utils import PyObjectId, CustomModel
from app.api.friends.friends_models import OperationOnUserModel
from app.api.admin.admin_models import BanReason


class Token(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)


class TokenData(BaseModel):
    email: Optional[str] = Field(default=None)


class Roles(int, Enum):
    BASE_USER = 0
    ADMIN = 1


class User(CustomModel):
    # Base User data
    id: PyObjectId = Field(..., alias="_id")
    email: str = Field(...)
    disabled: bool = Field(...)
    ban_reason: Optional[BanReason] = Field(default=None, alias="banReason")
    ban_msg: Optional[str] = Field(default=None, alias="banMsg")
    banner_id: Optional[PyObjectId] = Field(default=None, alias="bannerId")
    roles: List[Roles] = Field(...)

    # Friends related data
    friends: List[PyObjectId] = Field(default=[])
    blocked_users: List[PyObjectId] = Field(default=[], alias="blockedUsers")
    friend_requests: List[OperationOnUserModel] = Field(
        default=[],
        alias="friendRequests"
    )


class DbUser(User):
    hashed_password: str = Field(...)

