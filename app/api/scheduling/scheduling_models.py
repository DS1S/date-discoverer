from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import Field

from app.db.model_utils import (
    CustomModel,
    PyObjectId
)

from app.api.restaurant.restaurant_models import RestaurantModel


class DressCategory(str, Enum):
    DRESSY = "dressy"
    CASUAL = "casual"
    FORMAL = "formal"
    DISCRETIONARY = "whatever"


class Status(int, Enum):
    PENDING = 0
    REJECTED = 1
    APPROVED = 2


class BaseScheduledDateModel(CustomModel):
    meet_time: datetime = Field(..., alias="meetTime")
    dress_type: DressCategory = Field(..., alias="dressType")
    msg: Optional[str] = Field(default=None)


class ScheduledDateRequestModel(BaseScheduledDateModel):
    restaurant_id: PyObjectId = Field(..., alias="restaurantId")


class ScheduledDateModel(BaseScheduledDateModel):
    id: Optional[PyObjectId] = Field(..., alias="_id")
    sender_id: PyObjectId = Field(..., alias="senderId")
    receiver_id: PyObjectId = Field(..., alias="receiverId")
    restaurant: RestaurantModel = Field(...)
    status: Status = Field(...)


class ScheduledDateModelResponse(CustomModel):
    id: Optional[PyObjectId] = Field(..., alias="_id")
    meet_time: Optional[datetime] = Field(..., alias="meetTime")
    restaurant: Optional[RestaurantModel] = Field(...)
    dress_type: Optional[DressCategory] = Field(..., alias="dressType")
    msg: Optional[str] = Field(default=None)
    sender_id: Optional[PyObjectId] = Field(..., alias="senderId")
    receiver_id: Optional[PyObjectId] = Field(..., alias="receiverId")
    status: Optional[Status] = Field(...)
    successfully_sent: bool = Field(..., alias="successfullySent")
    request_msg: str = Field(..., alias="requestMsg")


