# FastAPI Service Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the existing RAG backend through a small FastAPI service without breaking the current Streamlit app.

**Architecture:** Add an API layer that depends on the existing `initialize_knowledge_base()` and `AnswerPipeline` modules. Keep service startup lazy and testable by allowing dependency injection for the DB and pipeline.

**Tech Stack:** FastAPI, Pydantic, Python `unittest`, existing Chroma/RAG modules.

---

## File Structure

- Create `src/api/__init__.py`: API package marker.
- Create `src/api/schemas.py`: Pydantic request/response models.
- Create `src/api/dependencies.py`: lazy knowledge-base and answer-pipeline dependency helpers.
- Create `src/api/app.py`: FastAPI application factory and routes.
- Modify `requirements.txt`: add `fastapi` and `uvicorn`.
- Modify `README.md`: add FastAPI run command and note it is the service foundation for future Next.js.
- Create `tests/test_api_app.py`: API route tests with fake dependencies.

## Task 1: API Schemas

**Files:**
- Create: `src/api/__init__.py`
- Create: `src/api/schemas.py`
- Test: `tests/test_api_app.py`

- [ ] Write failing tests that import `ChatRequest`, `ChatResponse`, `HealthResponse`, and `KnowledgeBaseStatusResponse`.
- [ ] Implement Pydantic models:
  - `ChatRequest(question: str, chat_id: str | None = None)`
  - `ChatResponse(answer: str)`
  - `HealthResponse(status: str)`
  - `KnowledgeBaseStatusResponse(status: str, has_db: bool)`
- [ ] Run `python -m unittest tests.test_api_app -v`.

## Task 2: FastAPI App Factory

**Files:**
- Create: `src/api/dependencies.py`
- Create: `src/api/app.py`
- Test: `tests/test_api_app.py`

- [ ] Write tests with FastAPI `TestClient` for:
  - `GET /health` returns `{"status": "ok"}`
  - `GET /knowledge-base/status` returns a status payload without initializing real Chroma in tests.
  - `POST /chat` calls a fake pipeline and returns `{"answer": "..."}`
- [ ] Implement `create_app(db_provider=None, pipeline_provider=None, memory_provider=None)`.
- [ ] Add routes:
  - `GET /health`
  - `GET /knowledge-base/status`
  - `POST /chat`
- [ ] Use injected providers in tests and lazy real providers in production.
- [ ] Run `python -m unittest tests.test_api_app -v`.

## Task 3: Runtime Docs And Dependencies

**Files:**
- Modify: `requirements.txt`
- Modify: `README.md`

- [ ] Add `fastapi` and `uvicorn` to `requirements.txt`.
- [ ] Add README commands:
  - Streamlit UI: `streamlit run app.py`
  - FastAPI service: `uvicorn src.api.app:app --reload`
- [ ] Explain FastAPI is an API foundation for the future Next.js frontend, while Streamlit remains the current UI.

## Task 4: Verification

- [ ] Run `python -m unittest discover -s tests -v`.
- [ ] Run `python -m py_compile app.py main.py src\config.py src\vector_db.py src\rag_pipeline.py src\data_loader.py src\knowledge_graph.py src\chat_history_manager.py src\ingestion_manifest.py src\answer_pipeline.py src\persistence_schema.py src\api\schemas.py src\api\dependencies.py src\api\app.py`.
- [ ] Run `git diff --check`.
- [ ] Commit with message `Add FastAPI service foundation`.

## Self-Review

- This plan does not implement Next.js, auth, PostgreSQL, or Redis. It creates the API foundation needed before those product layers.
- Tests avoid loading the real Chroma DB by using provider injection.
- Streamlit remains the current UI.
