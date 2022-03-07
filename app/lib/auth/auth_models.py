from typing import List, Optional
from enum import Enum

from pydantic import Field, BaseModel
from bson import ObjectId

from app.db.model_utils import PyObjectId, CustomModel


class Token(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)


class TokenData(BaseModel):
    email: Optional[str] = Field(default=None)


class Roles(int, Enum):
    BASE_USER = 0
    ADMIN = 1


class User(CustomModel):
    id: PyObjectId = Field(..., alias="_id")
    email: str = Field(...)
    disabled: bool = Field(...)
    roles: List[Roles] = Field(...)


class DbUser(User):
    hashed_password: str = Field(...)

