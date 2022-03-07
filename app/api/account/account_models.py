from typing import Optional

from pydantic import Field

from app.db.model_utils import CustomModel


class RegisterAccountRequest(CustomModel):
    email: str = Field(...)
    password: str = Field(...)


class RegisterAccountResponse(CustomModel):
    account_details: Optional[RegisterAccountRequest] = Field(default=None)
    success: bool = Field(...)
    msg: str = Field(...)
