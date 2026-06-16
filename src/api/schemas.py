from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    chat_id: str | None = None


class ChatResponse(BaseModel):
    answer: str


class HealthResponse(BaseModel):
    status: str


class KnowledgeBaseStatusResponse(BaseModel):
    status: str
    has_db: bool
