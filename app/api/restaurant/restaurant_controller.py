from typing import List

from fastapi import APIRouter, Path, Query, Depends

from app.db.model_utils import PyObjectId

from app.api.restaurant.restaurant_models import (
    RestaurantModel,
    RestaurantUpdateModel
)

from app.api.restaurant.restaurant_service import (
    get_all_restaurants,
    get_restaurant,
    add_restaurant,
    remove_restaurant,
    update_restaurant_info,
)

from app.lib.auth.auth_models import User, Roles
from app.lib.auth.auth_service import get_user_with_roles

restaurant_router = APIRouter()


@restaurant_router.get("", response_model=List[RestaurantModel])
async def retrieve_all_restaurants(
    user: User = Depends(get_user_with_roles([
        Roles.BASE_USER
    ]))
):
    return await get_all_restaurants()


@restaurant_router.get(
    "/{restaurantId}",
    response_model=RestaurantModel
)
async def retrieve_restaurant(
    restaurant_id: PyObjectId = Path(..., alias="restaurantId"),
    user: User = Depends(get_user_with_roles([
        Roles.BASE_USER
    ]))
):
    return await get_restaurant(restaurant_id)


@restaurant_router.post("", response_model=RestaurantModel)
async def create_restaurant(
    request: RestaurantModel,
    user: User = Depends(get_user_with_roles([
        Roles.ADMIN
    ]))
):
    return await add_restaurant(request)


@restaurant_router.delete(
    "/{restaurantId}",
    response_model=RestaurantModel
)
async def delete_restaurant(
    restaurant_id: PyObjectId = Path(..., alias="restaurantId"),
    user: User = Depends(get_user_with_roles([
        Roles.ADMIN
    ]))
):
    return await remove_restaurant(restaurant_id)


@restaurant_router.patch("/{restaurantId}", response_model=RestaurantModel)
async def update_restaurant(
    request: RestaurantUpdateModel,
    restaurant_id: PyObjectId = Path(..., alias="restaurantId"),
    user: User = Depends(get_user_with_roles([
        Roles.ADMIN
    ]))
):
    return await update_restaurant_info(request, restaurant_id)


@restaurant_router.get("/discover-restaurants")
async def discover_restaurants(
    user: User = Depends(get_user_with_roles([
        Roles.BASE_USER
    ]))
):
    pass
