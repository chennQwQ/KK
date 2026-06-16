from collections.abc import Callable
from typing import Any

from fastapi import FastAPI

from src.api.dependencies import get_answer_pipeline, get_knowledge_base, get_memory
from src.api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    KnowledgeBaseStatusResponse,
)


Provider = Callable[[], Any]


def create_app(
    db_provider: Provider | None = None,
    pipeline_provider: Provider | None = None,
    memory_provider: Provider | None = None,
) -> FastAPI:
    app = FastAPI(title="KK RAG API")
    db_provider = db_provider or get_knowledge_base
    pipeline_provider = pipeline_provider or get_answer_pipeline
    memory_provider = memory_provider or get_memory

    @app.get("/health", response_model=HealthResponse)
    def health():
        return HealthResponse(status="ok")

    @app.get("/knowledge-base/status", response_model=KnowledgeBaseStatusResponse)
    def knowledge_base_status():
        db = db_provider()
        has_db = db is not None
        return KnowledgeBaseStatusResponse(
            status="ready" if has_db else "missing",
            has_db=has_db,
        )

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest):
        db = db_provider()
        pipeline = pipeline_provider()
        memory = memory_provider()
        answer = pipeline.answer(db, request.question, memory)
        return ChatResponse(answer=answer)

    return app


app = create_app()
