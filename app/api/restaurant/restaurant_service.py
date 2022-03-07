from typing import List

from fastapi import HTTPException, status

from pymongo import ReturnDocument
from bson import ObjectId

from app.db.mongo_driver import restaurant_collection
from app.db.model_utils import PyObjectId

from app.api.restaurant.restaurant_models import (
    RestaurantModel,
    RestaurantUpdateModel,
    PriceRating,
    RestaurantCategory,
    FoodCategory
)

from app.lib.misc.general import (
    pop_from_dict,
    within_radius
)


async def get_all_restaurants():
    restaurants = await restaurant_collection.find().to_list(length=None)
    return restaurants


async def get_restaurant(restaurant_id: PyObjectId):
    restaurant = await restaurant_collection.find_one({"_id": restaurant_id})

    if restaurant:
        return restaurant

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Restaurant with id <{restaurant_id}> not found."
    )


async def add_restaurant(request: RestaurantModel):
    request.id = ObjectId()

    for review in request.reviews:
        review.id = ObjectId()

    for menu_item in request.top_menu_items:
        menu_item.id = ObjectId()

    new_restaurant = await restaurant_collection.insert_one(
        request.dict(by_alias=True)
    )
    created_restaurant = await restaurant_collection.find_one(
        {"_id": new_restaurant.inserted_id}
    )
    return created_restaurant


async def remove_restaurant(restaurant_id: PyObjectId):
    restaurant_to_delete = await restaurant_collection.find_one_and_delete(
        {"_id": restaurant_id}
    )

    if restaurant_to_delete:
        return restaurant_to_delete

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Restaurant with id <{restaurant_id}> not found."
    )


async def update_restaurant_info(
        request: RestaurantUpdateModel,
        restaurant_id: PyObjectId
):
    for review in request.reviews_to_add:
        review.id = ObjectId()

    for menu_item in request.top_menu_items_to_add:
        menu_item.id = ObjectId()

    reviews_to_add = request.reviews_to_add
    menu_items_to_add = request.top_menu_items_to_add
    reviews_to_remove = request.reviews_to_remove
    menu_items_to_remove = request.top_menu_items_to_remove

    fields_to_update = request.dict(exclude_unset=True)
    pop_from_dict(fields_to_update, "reviews_to_add")
    pop_from_dict(fields_to_update, "top_menu_items_to_add")
    pop_from_dict(fields_to_update, "reviews_to_remove")
    pop_from_dict(fields_to_update, "top_menu_items_to_remove")

    await restaurant_collection.find_one_and_update(
        {"_id": restaurant_id},
        {
            "$set": fields_to_update,
            "$pull": {
                "reviews": {"_id": {"$in": reviews_to_remove}},
                "topMenuItems": {"_id": {"$in": menu_items_to_remove}}
            }
        },
        return_document=ReturnDocument.AFTER
    )

    reviews_to_add = [r.dict() for r in reviews_to_add]
    menu_items_to_add = [m.dict() for m in menu_items_to_add]

    restaurant_to_update = await restaurant_collection.find_one_and_update(
        {"_id": restaurant_id},
        {
            "$push": {
                "reviews": {"$each": reviews_to_add},
                "topMenuItems": {"$each": menu_items_to_add}
            }
        },
        return_document=ReturnDocument.AFTER
    )

    if not restaurant_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant with id <{restaurant_id}> not found."
        )

    return restaurant_to_update


async def query_match_restaurants(
    minimum_price_rating: PriceRating,
    restaurant_categories: List[RestaurantCategory],
    lat: float,
    long: float,
    radius: float,
    has_open_table: bool,
    minimum_rating: float,
    minimum_reviews: int,
    includes_vegan_options: bool,
    provides_food_categories: List[FoodCategory],
    max_spend: int,
    max_to_display: int
):
    query = {
        "$expr": {"$gte": [{"$size": "$reviews"}, minimum_reviews]},
        "reviewRating": {"$gte": minimum_rating},
        "restaurantCategory": {"$in": restaurant_categories},
        "priceRating": {"$gte": minimum_price_rating},
        "$and": []
    }

    if has_open_table:
        query["$and"].append({"openTableUrl": {"$ne": None}})

    if includes_vegan_options or provides_food_categories:
        if includes_vegan_options:
            vegan_filter = {"topMenuItems": {"$elemMatch": {"isVegan": True}}}
            query["$and"].append(vegan_filter)
        if provides_food_categories:
            food_filter = {
                "topMenuItems": {
                    "$elemMatch": {
                        "foodCategory": {
                            "$in": provides_food_categories
                        }
                    }
                }
            }
            query["$and"].append(food_filter)

    query["$and"].append({
        "topMenuItems": {
            "$elemMatch": {
                "price": {
                    "$lte": max_spend
                }
            }
        }
    })

    restaurants = await restaurant_collection.find(query).to_list(length=None)

    valid_restaurants = []

    for restaurant in restaurants:
        if within_radius(
            lat,
            long,
            restaurant["lat"],
            restaurant["long"],
            radius
        ):
            valid_restaurants.append(restaurant)

    return valid_restaurants[:max_to_display]
