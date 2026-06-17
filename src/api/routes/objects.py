from collections.abc import Callable
from typing import Any

from fastapi import APIRouter

from src.api.routes.registry import API_ROUTES
from src.api.schemas import StudioObjectsResponse

Provider = Callable[[], Any]


def create_objects_router(object_provider: Provider) -> APIRouter:
    router = APIRouter()

    @router.get(API_ROUTES["objects"][1], response_model=StudioObjectsResponse)
    def objects():
        return StudioObjectsResponse(objects=object_provider())

    return router
