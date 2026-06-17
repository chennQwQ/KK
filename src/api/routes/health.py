from fastapi import APIRouter

from src.api.routes.registry import API_ROUTES
from src.api.schemas import HealthResponse


def create_health_router() -> APIRouter:
    router = APIRouter()

    @router.get(API_ROUTES["health"][1], response_model=HealthResponse)
    def health():
        return HealthResponse(status="ok")

    return router
