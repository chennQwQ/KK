from fastapi import FastAPI

from src.api.routes.chat import create_chat_router
from src.api.routes.health import create_health_router
from src.api.routes.knowledge_base import create_knowledge_base_router
from src.api.routes.objects import create_objects_router
from src.api.routes.registry import API_ROUTES


def include_api_routes(
    app: FastAPI,
    *,
    db_provider,
    pipeline_provider,
    memory_provider,
    object_provider,
    knowledge_status_provider,
    manifest_regenerator,
    index_rebuilder,
) -> None:
    app.include_router(create_health_router())
    app.include_router(create_objects_router(object_provider))
    app.include_router(
        create_knowledge_base_router(
            knowledge_status_provider,
            manifest_regenerator,
            index_rebuilder,
        )
    )
    app.include_router(create_chat_router(db_provider, pipeline_provider, memory_provider, object_provider))


__all__ = ["API_ROUTES", "include_api_routes"]
