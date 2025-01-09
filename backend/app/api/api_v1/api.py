from fastapi import APIRouter
from app.api.api_v1.endpoints import detection, auth, users, dashboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(detection.router, prefix="/detection", tags=["detection"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"]) 