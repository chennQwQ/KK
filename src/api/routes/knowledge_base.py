from collections.abc import Callable
from typing import Any

from fastapi import APIRouter

from src.api.routes.registry import API_ROUTES
from src.api.schemas import (
    IndexRebuildResponse,
    KnowledgeBaseStatusResponse,
    ManifestRegenerateResponse,
)

Provider = Callable[[], Any]


def create_knowledge_base_router(
    status_provider: Provider,
    manifest_regenerator: Provider,
    index_rebuilder: Provider,
) -> APIRouter:
    router = APIRouter()

    @router.get(
        API_ROUTES["knowledge_base_status"][1],
        response_model=KnowledgeBaseStatusResponse,
    )
    def knowledge_base_status():
        return status_provider()

    @router.post(
        API_ROUTES["knowledge_base_manifest_regenerate"][1],
        response_model=ManifestRegenerateResponse,
    )
    def regenerate_manifests():
        return manifest_regenerator()

    @router.post(
        API_ROUTES["knowledge_base_index_rebuild"][1],
        response_model=IndexRebuildResponse,
    )
    def rebuild_index():
        return index_rebuilder()

    return router
