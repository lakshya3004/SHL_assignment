from fastapi import APIRouter
from app.api.routes import health, chat

api_router = APIRouter()

# Register routes with appropriate prefixes and tags for documentation
api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(chat.router, prefix="/chat", tags=["recommendation"])
