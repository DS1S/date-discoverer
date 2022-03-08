from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.settings import settings

from app.api.health.health_controller import health_router
from app.api.account.account_controller import account_router
from app.api.restaurant.restaurant_controller import restaurant_router
from app.api.friends.friends_controller import friends_router
from app.api.admin.admin_controller import admin_router
from app.api.scheduling.scheduling_controller import scheduling_router


app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(health_router, tags=["Health"])
app.include_router(account_router, tags=["Account Operations"])
app.include_router(restaurant_router, prefix="/restaurants", tags=["Restaurant Operations"])
app.include_router(friends_router, prefix="/friends", tags=["Friend Operations"])
app.include_router(admin_router, prefix="/admin", tags=["Admin Operations"])
app.include_router(scheduling_router, tags=["Scheduling Operations"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

