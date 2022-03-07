from typing import List, Optional

from fastapi import APIRouter, Path, Query, Depends

from app.db.model_utils import PyObjectId

from app.api.restaurant.restaurant_models import (
    RestaurantModel,
    RestaurantUpdateModel,
    PriceRating,
    RestaurantCategory,
    FoodCategory
)

from app.api.restaurant.restaurant_service import (
    get_all_restaurants,
    get_restaurant,
    add_restaurant,
    remove_restaurant,
    update_restaurant_info,
    query_match_restaurants,
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
    "/discover-restaurants",
    response_model=List[RestaurantModel]
)
async def discover_restaurants(
    user: User = Depends(get_user_with_roles([
        Roles.BASE_USER
    ])),
    minimum_price_rating: Optional[PriceRating] = Query(
        PriceRating.LOW,
        alias="minimumPriceRating"
    ),
    restaurant_categories: Optional[List[RestaurantCategory]] = Query(
        RestaurantCategory.fields(),
        alias="restaurantCategories"
    ),
    lat: float = Query(..., ge=-90, le=90),
    long: float = Query(..., ge=-180, le=180),
    radius: float = Query(..., gt=0),
    max_spend: int = Query(..., ge=0, alias="maxSpend"),
    has_open_table: Optional[bool] = Query(False, alias="hasOpenTable"),
    minimum_rating: Optional[float] = Query(0, ge=0, alias="minimumRating"),
    minimum_reviews: Optional[int] = Query(0, ge=0, alias="minimumReviews"),
    includes_vegan_options: Optional[bool] = Query(
        True,
        alias="includesVeganOptions"
    ),
    provides_food_categories: Optional[List[FoodCategory]] = Query(
        FoodCategory.fields(),
        alias="providesFoodCategories"
    ),
    max_to_display: Optional[int] = Query(3, gt=0, alias="maxToDisplay")
):
    return await query_match_restaurants(
        minimum_price_rating,
        restaurant_categories,
        lat,
        long,
        radius,
        has_open_table,
        minimum_rating,
        minimum_reviews,
        includes_vegan_options,
        provides_food_categories,
        max_spend,
        max_to_display
    )


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


