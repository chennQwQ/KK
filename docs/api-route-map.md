# Frontend and Backend API Route Map

This document is the contract index between the Next.js frontend and the FastAPI backend.

Current implementation scope: only the KK local document set under `data/` is exposed as a real object. Other object types remain product roadmap items until persistence and upload flows are implemented.

## Backend structure

The FastAPI layer is split by product domain:

- `src/api/app.py`: application factory. It creates the `FastAPI` app and includes routers.
- `src/api/routes/registry.py`: canonical backend route names, methods, and paths.
- `src/api/routes/health.py`: system health router.
- `src/api/routes/objects.py`: RAG Studio object catalog router.
- `src/api/routes/knowledge_base.py`: knowledge-base router.
- `src/api/routes/chat.py`: chat router.
- `src/api/object_catalog.py`: temporary in-memory object catalog until persistence is introduced.
- `src/api/schemas.py`: Pydantic request and response models.
- `src/api/dependencies.py`: runtime providers for knowledge base, answer pipeline, and memory.

This keeps `app.py` as a composition module instead of mixing app creation, dependency wiring, and route handlers in one file.

## Frontend structure

The frontend API client is centralized under `web/src/lib/api/`:

- `routes.ts`: canonical frontend route constants matching backend paths.
- `types.ts`: TypeScript request and response contracts matching `src/api/schemas.py`.
- `client.ts`: shared `fetch` wrapper and API error type.
- `objects.ts`: object catalog client and snake_case to UI-model mapper.
- `chat.ts`: chat-specific client functions.
- `health.ts`: health-specific client functions.
- `knowledge-base.ts`: knowledge-base-specific client functions.

Feature code should call these domain files instead of using raw `fetch()` or hard-coded backend paths.

## Current route mapping

| Domain | Backend route | Backend handler | Backend schema | Frontend route constant | Frontend client |
| --- | --- | --- | --- | --- | --- |
| Health | `GET /health` | `src/api/routes/health.py:create_health_router` | `HealthResponse` | `apiRoutes.health` | `getHealth()` |
| Objects | `GET /objects` | `src/api/routes/objects.py:create_objects_router` | `StudioObjectsResponse` | `apiRoutes.objects` | `getObjects()` |
| Knowledge Base | `GET /knowledge-base/status` | `src/api/routes/knowledge_base.py:create_knowledge_base_router` | `KnowledgeBaseStatusResponse` | `apiRoutes.knowledgeBaseStatus` | `getKnowledgeBaseStatus()` |
| Knowledge Base | `POST /knowledge-base/manifests/regenerate` | `src/api/routes/knowledge_base.py:create_knowledge_base_router` | `ManifestRegenerateResponse` | `apiRoutes.knowledgeBaseManifestRegenerate` | `regenerateKnowledgeBaseManifests()` |
| Chat | `POST /chat` | `src/api/routes/chat.py:create_chat_router` | `ChatRequest`, `ChatResponse` | `apiRoutes.chat` | `askQuestion()` |

## Payload contracts

### `GET /health`

Response:

```json
{
  "status": "ok"
}
```

### `GET /knowledge-base/status`

Response:

```json
{
  "status": "needs_rebuild",
  "has_db": false,
  "object_id": "kk-advisor",
  "knowledge_base_name": "KK 本地文档",
  "document_count": 3,
  "source_files": ["book1.pdf", "book2.pdf", "qa.pdf"],
  "manifest_exists": true,
  "index_exists": false,
  "manifest_current": false
}
```

`status` is:

- `missing` when no supported local files exist under `data/`.
- `needs_rebuild` when local files exist but the Chroma index or manifest is missing/stale.
- `ready` when the Chroma index exists and the manifest matches the current local files/settings.

### `POST /knowledge-base/manifests/regenerate`

Response:

```json
{
  "generated": [
    {
      "source_file": "qa.pdf",
      "source_type": "forum_qa",
      "manifest_path": "data/processed/forum/qa.manifest.json",
      "parse_status": "parsed",
      "items": 846,
      "pages": 1018,
      "chapters": 0
    },
    {
      "source_file": "book2.pdf",
      "source_type": "book",
      "manifest_path": "data/processed/books/book2.manifest.json",
      "parse_status": "parsed",
      "items": 0,
      "pages": 0,
      "chapters": 12
    }
  ]
}
```

### `GET /objects`

Response:

```json
{
  "objects": [
    {
      "id": "kk-advisor",
      "name": "KK 投研助手",
      "type": "已构建对象",
      "domain": "KK 文档问答",
      "status": "可测试",
      "icon": "K",
      "description": "基于当前 data/ 目录中的 KK 相关文档构建的第一个真实 RAG 对象。",
      "knowledge_bases": ["KK 本地文档"],
      "documents": 3,
      "chunks": "待索引统计",
      "updated_at": "本地数据"
    }
  ]
}
```

The frontend maps `knowledge_bases` to `knowledgeBases` and `updated_at` to `updatedAt` before rendering.

### `POST /chat`

Request:

```json
{
  "question": "Question text",
  "chat_id": "optional-chat-id",
  "object_id": "kk-advisor"
}
```

Response:

```json
{
  "answer": "Answer text",
  "object_id": "kk-advisor",
  "citations": [
    {
      "source": "qa.pdf",
      "document_kind": "forum_post",
      "item_id": "qa-p2-floor2",
      "author": "kkndme",
      "floor": 2,
      "page_start": 2,
      "page_end": 2,
      "topic": "uncategorized"
    }
  ]
}
```

## Maintenance rules

When adding or changing a backend route:

1. Add the canonical method and path in `src/api/routes/registry.py`.
2. Implement the route in the matching `src/api/routes/<domain>.py` module.
3. Add or update Pydantic models in `src/api/schemas.py`.
4. Mirror the path in `web/src/lib/api/routes.ts`.
5. Mirror the payload contract in `web/src/lib/api/types.ts`.
6. Add a domain client function under `web/src/lib/api/`.
7. Update this document.
8. Run:

```powershell
.\.venv313\Scripts\python.exe -m unittest tests.test_api_app
npm.cmd run test
```
