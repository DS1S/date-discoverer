from typing import List, Optional
from enum import Enum

from pydantic import Field
from bson import ObjectId

from app.db.model_utils import CustomModel, PyObjectId, Date


class PriceRating(str, Enum):
    LOW = "$"
    MEDIUM = "$$"
    HIGH = "$$$"
    Wealthy = "$$$$"


class MenuItemCategory(str, Enum):
    APP = "appetizer"
    MAIN = "main"
    DESSERT = "dessert"


class FoodCategory(str, Enum):
    CHICKEN = "chicken"
    BEEF = "beef"
    SEAFOOD = "seafood"
    DAIRY = "dairy"
    YEAST_CREATED = "pastry/bread"
    NOODLE = "noodle"
    VEGETABLE = "vegetable"

    @staticmethod
    def fields():
        return [
            FoodCategory.CHICKEN,
            FoodCategory.BEEF,
            FoodCategory.SEAFOOD,
            FoodCategory.DAIRY,
            FoodCategory.YEAST_CREATED,
            FoodCategory.NOODLE,
            FoodCategory.VEGETABLE
        ]


class RestaurantCategory(str, Enum):
    KOREAN = "korean"
    JAPANESE = "japanese"
    ITALIAN = "italian"
    CHINESE = "chinese"
    FAST_FOOD = "fast food"
    COFFEE = "coffee"
    DESSERT = "dessert"
    PUB = "pub"
    MEXICAN = "mexican"
    INDIAN = "indian"
    AMERICAN = "american"
    CANADIAN = "canadian"
    SOUTH_AMERICAN = "south american"

    @staticmethod
    def fields():
        return [
            RestaurantCategory.KOREAN,
            RestaurantCategory.JAPANESE,
            RestaurantCategory.ITALIAN,
            RestaurantCategory.CHINESE,
            RestaurantCategory.FAST_FOOD,
            RestaurantCategory.COFFEE,
            RestaurantCategory.DESSERT,
            RestaurantCategory.PUB,
            RestaurantCategory.MEXICAN,
            RestaurantCategory.INDIAN,
            RestaurantCategory.AMERICAN,
            RestaurantCategory.CANADIAN,
            RestaurantCategory.SOUTH_AMERICAN
        ]


class MenuItemModel(CustomModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str = Field(...)
    price: float = Field(..., ge=0)
    menu_category: MenuItemCategory = Field(...)
    is_vegan: bool = Field(...)
    food_category: FoodCategory = Field(...)


class ReviewModel(CustomModel):
    id: PyObjectId = Field(default=None, alias="_id")
    review_msg: str = Field(...)
    rating: float = Field(..., ge=0, le=5)
    review_date: Date = Field(...)
    number_of_previous_reviews: int = Field(..., ge=0)


class RestaurantModel(CustomModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    # Generic Restaurant Data
    name: str = Field(...)
    city: str = Field(...)
    open_table_url: Optional[str] = Field(default=None)
    review_rating: float = Field(..., ge=0, le=5)
    price_rating: PriceRating = Field(...)
    restaurant_category: RestaurantCategory = Field(...)

    reviews: Optional[List[ReviewModel]] = Field(default=[])
    top_menu_items: Optional[List[MenuItemModel]] = Field(default=[])

    # Location Data
    lat: float = Field(..., ge=-90, le=90)
    long: float = Field(..., ge=-180, le=180)

    class Config:
        schema_extra = {
            "example": {
                "name": "McDonald's",
                "city": "Toronto",
                "openTableUrl": None,
                "reviewRating": 4.5,
                "priceRating": "$",
                "restaurantCategory": "fast food",
                "reviews": [
                    {
                        "reviewMsg": "Great place for burgers",
                        "rating": 4.0,
                        "reviewDate": "2022-03-06",
                        "numberOfPreviousReviews": 43
                    }
                ],
                "topMenuItems": [
                    {
                        "name": "Big Mac",
                        "price": 5.29,
                        "menuCategory": "main",
                        "isVegan": False,
                        "foodCategory": "beef"
                    }
                ],
                "lat": 32.231,
                "long": 123.12,
            }
        }


class RestaurantUpdateModel(CustomModel):
    name: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    open_table_url: Optional[str] = Field(default=None)
    review_rating: Optional[str] = Field(default=None)
    price_rating: Optional[str] = Field(default=None)
    restaurant_category: Optional[RestaurantCategory] = Field(default=None)

    reviews_to_remove: Optional[List[PyObjectId]] = Field(default=[])
    reviews_to_add: Optional[List[ReviewModel]] = Field(default=[])

    top_menu_items_to_remove: Optional[List[PyObjectId]] = Field(default=[])
    top_menu_items_to_add: Optional[List[MenuItemModel]] = Field(default=[])

    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    long: Optional[float] = Field(default=None, ge=-180, le=180)

