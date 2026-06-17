from collections.abc import Callable
from typing import Any

from fastapi import APIRouter
from fastapi import HTTPException

from src.api.object_catalog import find_studio_object
from src.api.routes.registry import API_ROUTES
from src.api.schemas import ChatCitation, ChatRequest, ChatResponse

Provider = Callable[[], Any]


def create_chat_router(
    db_provider: Provider,
    pipeline_provider: Provider,
    memory_provider: Provider,
    object_provider: Provider,
) -> APIRouter:
    router = APIRouter()

    @router.post(API_ROUTES["chat"][1], response_model=ChatResponse)
    def chat(request: ChatRequest):
        try:
            db = db_provider()
        except Exception as exc:
            return ChatResponse(
                answer=f"知识库暂不可用，无法完成 RAG 检索。请先确认 Chroma 索引和本地 embedding 模型可用。错误信息: {exc}",
                object_id=request.object_id,
                citations=[],
            )

        pipeline = pipeline_provider()
        memory = memory_provider()
        studio_object = find_studio_object(object_provider(), request.object_id)

        if request.object_id is not None and studio_object is None:
            raise HTTPException(status_code=404, detail="Object not found")

        if studio_object is not None and hasattr(pipeline, "answer_for_object"):
            result = pipeline.answer_for_object(db, request.question, memory, studio_object)
            return _chat_response_from_result(result, studio_object.id)

        answer = pipeline.answer(db, request.question, memory)
        return ChatResponse(answer=answer, object_id=request.object_id)

    return router


def _chat_response_from_result(result: Any, object_id: str) -> ChatResponse:
    if isinstance(result, dict):
        return ChatResponse(
            answer=str(result.get("answer", "")),
            object_id=object_id,
            citations=[ChatCitation(**item) for item in result.get("citations", [])],
        )

    return ChatResponse(answer=str(result), object_id=object_id)
