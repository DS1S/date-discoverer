from fastapi import HTTPException, status

from pymongo import ReturnDocument
from bson import ObjectId

from app.db.mongo_driver import restaurant_collection
from app.db.model_utils import PyObjectId

from app.api.restaurant.restaurant_models import (
    RestaurantModel,
    RestaurantUpdateModel
)

from app.lib.misc.general import pop_from_dict


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
