from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str
    chat_id: str | None = None
    object_id: str | None = None


class ChatCitation(BaseModel):
    source: str
    page: str | None = None
    quote: str | None = None
    document_kind: str | None = None
    item_id: str | None = None
    author: str | None = None
    floor: int | None = None
    page_start: int | None = None
    page_end: int | None = None
    topic: str | None = None


class ChatResponse(BaseModel):
    answer: str
    object_id: str | None = None
    citations: list[ChatCitation] = Field(default_factory=list)


class StudioObjectResponse(BaseModel):
    id: str
    name: str
    type: str = "object"
    domain: str = "general"
    status: str = "draft"
    icon: str = "O"
    description: str = ""
    knowledge_bases: list[str] = Field(default_factory=list)
    documents: int = 0
    chunks: str = "0"
    updated_at: str = "pending"


class StudioObjectsResponse(BaseModel):
    objects: list[StudioObjectResponse]


class HealthResponse(BaseModel):
    status: str


class KnowledgeBaseStatusResponse(BaseModel):
    status: str
    has_db: bool
    object_id: str = "kk-advisor"
    knowledge_base_name: str = "KK 本地文档"
    document_count: int = 0
    source_files: list[str] = Field(default_factory=list)
    manifest_exists: bool = False
    index_exists: bool = False
    manifest_current: bool = False


class ManifestRegenerateItem(BaseModel):
    source_file: str
    source_type: str
    manifest_path: str
    parse_status: str
    items: int = 0
    pages: int = 0
    chapters: int = 0


class ManifestRegenerateResponse(BaseModel):
    generated: list[ManifestRegenerateItem] = Field(default_factory=list)


class IndexRebuildResponse(BaseModel):
    status: str
    chunks: int = 0
    elapsed_ms: int = 0
    error: str | None = None
