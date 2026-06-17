from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.dependencies import get_answer_pipeline, get_knowledge_base, get_memory
from src.api.knowledge_base_status import build_knowledge_base_status
from src.api.manifest_regenerator import regenerate_structured_manifests
from src.api.object_catalog import get_studio_objects
from src.api.routes import include_api_routes


Provider = Callable[[], Any]
LOCAL_DEV_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3001",
    "http://localhost:3001",
]


def rebuild_knowledge_base_index():
    from src.vector_db import rebuild_vector_db

    return rebuild_vector_db()


def create_app(
    db_provider: Provider | None = None,
    pipeline_provider: Provider | None = None,
    memory_provider: Provider | None = None,
    object_provider: Provider | None = None,
    knowledge_status_provider: Provider | None = None,
    manifest_regenerator: Provider | None = None,
    index_rebuilder: Provider | None = None,
) -> FastAPI:
    app = FastAPI(title="KK RAG API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=LOCAL_DEV_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    db_provider = db_provider or get_knowledge_base
    pipeline_provider = pipeline_provider or get_answer_pipeline
    memory_provider = memory_provider or get_memory
    object_provider = object_provider or get_studio_objects
    knowledge_status_provider = knowledge_status_provider or build_knowledge_base_status
    manifest_regenerator = manifest_regenerator or regenerate_structured_manifests
    index_rebuilder = index_rebuilder or rebuild_knowledge_base_index

    include_api_routes(
        app,
        db_provider=db_provider,
        pipeline_provider=pipeline_provider,
        memory_provider=memory_provider,
        object_provider=object_provider,
        knowledge_status_provider=knowledge_status_provider,
        manifest_regenerator=manifest_regenerator,
        index_rebuilder=index_rebuilder,
    )

    return app


app = create_app()
