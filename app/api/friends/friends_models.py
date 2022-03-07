from typing import Optional
from datetime import date

from pydantic import Field

from app.db.model_utils import CustomModel


class OperationOnUserModel(CustomModel):
    email: str = Field(...)
    msg: Optional[str] = Field(default="")


class FriendRequestResponseModel(CustomModel):
    friend_request_sent: bool = Field(..., alias="friendRequestSent")
    date_sent: date = Field(default=date.today(), alias="dateSent")
    msg: str = Field(...)


class FriendRequestAcceptedResponse(CustomModel):
    msg: str = Field(...)
    date_accepted: date = Field(default=date.today(), alias="dateAccepted")


class FriendRemovedResponse(CustomModel):
    msg: str = Field(...)
    date_removed: date = Field(default=date.today(), alias="dateRemoved")


class BlockUserResponseModel(CustomModel):
    blocked_user: str = Field(..., alias="blockedUser")
    date_blocked: date = Field(default=date.today(), alias="dateBlocked")
    msg: str = Field(...)

