from typing import List, Optional
from enum import Enum

from pydantic import Field


from app.db.model_utils import (
    CustomModel,
    PyObjectId
)


class BanReason(int, Enum):
    BUG_ABUSING = 1
    FOWL_LANGUAGE = 2
    DISCRETION_OF_ADMIN = 3

    UNKNOWN = 1000


class BanModel(CustomModel):
    reason: BanReason = Field(...)
    msg: Optional[str] = Field(...)


class BanModelById(BanModel):
    id: PyObjectId = Field(...)


class BanModelByEmail(BanModel):
    email: str = Field(...)


class BanUsersRequestModel(CustomModel):
    users_to_ban_by_id: List[BanModelById] = Field(..., alias="usersToBanById")
    users_to_ban_by_email: List[BanModelByEmail] = Field(..., alias="usersToBanByEmail")


class BanUsersResponseModel(CustomModel):
    users_banned: List[PyObjectId] = Field(..., alias="usersBanned")
    count: int = Field(...)
