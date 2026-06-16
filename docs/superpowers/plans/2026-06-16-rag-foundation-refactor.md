# RAG Foundation Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the persistence, manifest, answer-pipeline, and documentation foundation needed before the Next.js + FastAPI product migration.

**Architecture:** Keep the current Streamlit app working while extracting deeper Python modules. PostgreSQL/Qdrant/Next.js remain the product target, but this phase uses local files and SQLite-friendly interfaces so the current repo can be tested without external services.

**Tech Stack:** Python stdlib `unittest`, JSON manifest files, existing LangChain/Chroma/OpenAI stack, Streamlit UI.

---

## File Structure

- Modify `README.md`: add product architecture, memory persistence, vector database, chat categorization, and virtual agent storage sections.
- Modify `docs/superpowers/specs/2026-06-16-nextjs-fastapi-product-architecture-design.md`: append the memory/vector/category/agent design to the confirmed spec.
- Create `src/ingestion_manifest.py`: compute source file hashes, compare build settings, read/write `chroma_db/manifest.json`.
- Modify `src/vector_db.py`: use the manifest to decide whether the current Chroma index is stale.
- Create `src/answer_pipeline.py`: one deep answer module that owns retrieval, prompt assembly, streaming, citations, and memory persistence.
- Modify `src/rag_pipeline.py`: keep `ask_question` as a compatibility wrapper over `AnswerPipeline`.
- Modify `app.py`: consume the wrapper without breaking the current UI; optional streaming can be enabled once the generator is stable.
- Create `src/persistence_schema.py`: document and expose table definitions for future PostgreSQL/SQLite persistence.
- Create `tests/test_ingestion_manifest.py`: manifest comparison tests.
- Create `tests/test_answer_pipeline.py`: source dedupe and missing API-key behavior tests.
- Create `tests/test_persistence_schema.py`: table coverage tests for chat categories, agents, memory scopes, and messages.

## Task 1: Documentation Update

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-06-16-nextjs-fastapi-product-architecture-design.md`

- [ ] **Step 1: Add README architecture sections**

Add sections named:

```markdown
## 产品化扩展路线
## Memory 持久化设计
## 向量数据库优化与部署
## 对话分类存储
## 多虚拟对话对象设计
## 第一阶段重构计划
```

The content must state these defaults:

```text
产品目标：给别人登录使用的 Web 产品
主应用：Next.js + TypeScript
RAG 服务：FastAPI + Python
权威数据：PostgreSQL
临时状态：Redis
语义检索：Qdrant 或 Chroma
关系图谱：Neo4j
当前阶段：先在 Python 项目里建立 manifest、answer pipeline、persistence schema
```

- [ ] **Step 2: Append persistence design to the spec**

Append a section named `## Memory、分类和虚拟对象扩展设计` containing:

```markdown
- PostgreSQL 存用户、会话、消息、分类、虚拟对象、任务、引用。
- 向量库存文档 chunk 和长期语义 memory。
- Redis 存任务进度、短期缓存、流式临时状态。
- Neo4j 存实体关系和观点图谱。
- 聊天消息必须先进 PostgreSQL，向量库只负责召回。
```

- [ ] **Step 3: Verify docs render as text**

Run:

```powershell
Get-Content -First 80 -Encoding UTF8 README.md
Get-Content -Tail 80 -Encoding UTF8 docs\superpowers\specs\2026-06-16-nextjs-fastapi-product-architecture-design.md
```

Expected: Chinese text is readable and section headings are present.

## Task 2: Ingestion Manifest

**Files:**
- Create: `src/ingestion_manifest.py`
- Modify: `src/vector_db.py`
- Test: `tests/test_ingestion_manifest.py`

- [ ] **Step 1: Write failing manifest tests**

Create `tests/test_ingestion_manifest.py`:

```python
import tempfile
import unittest
from pathlib import Path

from src.ingestion_manifest import (
    BuildSettings,
    build_manifest,
    is_manifest_current,
    load_manifest,
    save_manifest,
)


class IngestionManifestTests(unittest.TestCase):
    def test_manifest_is_current_when_sources_and_settings_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            db_dir = Path(tmp) / "db"
            data_dir.mkdir()
            db_dir.mkdir()
            (data_dir / "a.txt").write_text("hello", encoding="utf-8")

            settings = BuildSettings(
                embedding_model="model-a",
                chunk_size=800,
                chunk_overlap=100,
            )
            manifest = build_manifest(data_dir, settings)
            save_manifest(db_dir, manifest)

            loaded = load_manifest(db_dir)
            self.assertTrue(is_manifest_current(data_dir, settings, loaded))

    def test_manifest_is_stale_when_file_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            (data_dir / "a.txt").write_text("hello", encoding="utf-8")
            settings = BuildSettings("model-a", 800, 100)
            manifest = build_manifest(data_dir, settings)

            (data_dir / "a.txt").write_text("changed", encoding="utf-8")

            self.assertFalse(is_manifest_current(data_dir, settings, manifest))

    def test_manifest_is_stale_when_settings_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir()
            (data_dir / "a.txt").write_text("hello", encoding="utf-8")

            manifest = build_manifest(data_dir, BuildSettings("model-a", 800, 100))

            self.assertFalse(
                is_manifest_current(
                    data_dir,
                    BuildSettings("model-b", 800, 100),
                    manifest,
                )
            )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest tests.test_ingestion_manifest -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'src.ingestion_manifest'`.

- [ ] **Step 3: Implement manifest module**

Create `src/ingestion_manifest.py`:

```python
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANIFEST_FILE = "manifest.json"
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


@dataclass(frozen=True)
class BuildSettings:
    embedding_model: str
    chunk_size: int
    chunk_overlap: int


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_files(data_path: Path) -> list[Path]:
    if not data_path.exists():
        return []
    return sorted(
        path
        for path in data_path.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def build_manifest(data_path: str | Path, settings: BuildSettings) -> dict[str, Any]:
    data_dir = Path(data_path)
    sources = []
    for path in _source_files(data_dir):
        sources.append(
            {
                "name": path.name,
                "size": path.stat().st_size,
                "sha256": _hash_file(path),
            }
        )
    return {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "settings": asdict(settings),
        "sources": sources,
    }


def manifest_path(db_path: str | Path) -> Path:
    return Path(db_path) / MANIFEST_FILE


def load_manifest(db_path: str | Path) -> dict[str, Any] | None:
    path = manifest_path(db_path)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_manifest(db_path: str | Path, manifest: dict[str, Any]) -> None:
    db_dir = Path(db_path)
    db_dir.mkdir(parents=True, exist_ok=True)
    with manifest_path(db_dir).open("w", encoding="utf-8") as file:
        json.dump(manifest, file, ensure_ascii=False, indent=2)


def is_manifest_current(
    data_path: str | Path,
    settings: BuildSettings,
    manifest: dict[str, Any] | None,
) -> bool:
    if manifest is None:
        return False
    current = build_manifest(data_path, settings)
    return (
        manifest.get("version") == current["version"]
        and manifest.get("settings") == current["settings"]
        and manifest.get("sources") == current["sources"]
    )
```

- [ ] **Step 4: Integrate manifest into vector DB initialization**

Modify `src/vector_db.py` so `initialize_knowledge_base()` computes:

```python
settings = BuildSettings(
    embedding_model=EMBED_MODEL,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)
manifest = load_manifest(DB_PATH)
should_rebuild = not os.path.exists(DB_PATH) or not os.listdir(DB_PATH) or not is_manifest_current(DATA_PATH, settings, manifest)
```

After creating the vector DB, call:

```python
save_manifest(DB_PATH, build_manifest(DATA_PATH, settings))
```

- [ ] **Step 5: Run manifest tests**

Run:

```powershell
python -m unittest tests.test_ingestion_manifest -v
```

Expected: all tests PASS.

## Task 3: Persistence Schema

**Files:**
- Create: `src/persistence_schema.py`
- Test: `tests/test_persistence_schema.py`

- [ ] **Step 1: Write failing schema tests**

Create `tests/test_persistence_schema.py`:

```python
import unittest

from src.persistence_schema import TABLES, required_tables


class PersistenceSchemaTests(unittest.TestCase):
    def test_required_tables_cover_product_memory_design(self):
        self.assertEqual(
            required_tables(),
            {
                "users",
                "knowledge_bases",
                "documents",
                "ingestion_manifests",
                "chat_categories",
                "chat_tags",
                "chat_tag_links",
                "virtual_agents",
                "chats",
                "chat_participants",
                "messages",
                "citations",
                "memory_items",
                "jobs",
                "module_settings",
            },
        )

    def test_memory_items_include_scope_and_agent_columns(self):
        memory_columns = TABLES["memory_items"]
        self.assertIn("scope", memory_columns)
        self.assertIn("user_id", memory_columns)
        self.assertIn("agent_id", memory_columns)
        self.assertIn("chat_id", memory_columns)
        self.assertIn("importance", memory_columns)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest tests.test_persistence_schema -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement schema inventory**

Create `src/persistence_schema.py`:

```python
TABLES: dict[str, tuple[str, ...]] = {
    "users": ("id", "email", "display_name", "created_at"),
    "knowledge_bases": ("id", "owner_id", "name", "visibility", "created_at"),
    "documents": ("id", "knowledge_base_id", "source_type", "file_name", "checksum", "status", "created_at"),
    "ingestion_manifests": ("id", "document_id", "parser_version", "chunk_size", "chunk_overlap", "embedding_model", "created_at"),
    "chat_categories": ("id", "user_id", "name", "parent_id", "sort_order"),
    "chat_tags": ("id", "user_id", "name"),
    "chat_tag_links": ("chat_id", "tag_id"),
    "virtual_agents": ("id", "owner_id", "name", "system_prompt", "style_prompt", "retrieval_policy_id", "memory_policy_id", "is_public", "created_at"),
    "chats": ("id", "user_id", "agent_id", "knowledge_base_id", "category_id", "category_source", "title", "summary", "created_at", "updated_at"),
    "chat_participants": ("chat_id", "participant_type", "participant_id", "display_name"),
    "messages": ("id", "chat_id", "sender_type", "sender_id", "role", "content", "model_name", "token_usage", "created_at"),
    "citations": ("id", "message_id", "document_id", "page", "chunk_id", "source_preview"),
    "memory_items": ("id", "user_id", "agent_id", "chat_id", "knowledge_base_id", "scope", "content", "importance", "created_at"),
    "jobs": ("id", "user_id", "job_type", "status", "progress", "error_summary", "created_at", "updated_at"),
    "module_settings": ("id", "user_id", "knowledge_base_id", "module_name", "settings_json"),
}


def required_tables() -> set[str]:
    return set(TABLES)
```

- [ ] **Step 4: Run schema tests**

Run:

```powershell
python -m unittest tests.test_persistence_schema -v
```

Expected: all tests PASS.

## Task 4: Answer Pipeline

**Files:**
- Create: `src/answer_pipeline.py`
- Modify: `src/rag_pipeline.py`
- Test: `tests/test_answer_pipeline.py`

- [ ] **Step 1: Write failing answer pipeline tests**

Create `tests/test_answer_pipeline.py`:

```python
import os
import unittest
from unittest.mock import patch

from src.answer_pipeline import AnswerPipeline, RetrievedDocument, collect_sources


class FakeRetriever:
    def invoke(self, question):
        return [
            RetrievedDocument("alpha", {"source": "book1.pdf"}),
            RetrievedDocument("beta", {"source": "book1.pdf"}),
            RetrievedDocument("gamma", {"source": "qa.pdf"}),
        ]


class FakeDb:
    def as_retriever(self, search_kwargs):
        return FakeRetriever()


class FakeMemory:
    def load_memory_variables(self, values):
        return {"chat_history": []}

    def save_context(self, input_values, output_values):
        self.saved = (input_values, output_values)


class AnswerPipelineTests(unittest.TestCase):
    def test_collect_sources_deduplicates_source_file_names(self):
        docs = [
            RetrievedDocument("a", {"source": "C:/tmp/book1.pdf"}),
            RetrievedDocument("b", {"source": "C:/tmp/book1.pdf"}),
            RetrievedDocument("c", {"source": "qa.pdf"}),
        ]
        self.assertEqual(collect_sources(docs), ["book1.pdf", "qa.pdf"])

    def test_missing_api_key_returns_clear_error(self):
        pipeline = AnswerPipeline(api_key=None)
        result = pipeline.answer(FakeDb(), "问题", FakeMemory())
        self.assertIn("缺少 DEEPSEEK_API_KEY", result)

    def test_compatibility_answer_saves_memory_with_fake_llm(self):
        memory = FakeMemory()
        pipeline = AnswerPipeline(api_key="test-key", client_factory=lambda **kwargs: None)

        with patch.object(pipeline, "_generate_text", return_value="回答"):
            result = pipeline.answer(FakeDb(), "问题", memory)

        self.assertIn("回答", result)
        self.assertIn("book1.pdf", result)
        self.assertEqual(memory.saved[0], {"input": "问题"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest tests.test_answer_pipeline -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement answer pipeline**

Create `src/answer_pipeline.py` with:

```python
import os
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from langchain_core.messages import AIMessage, HumanMessage
from openai import OpenAI

from src.config import DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, LLM_MODEL, STYLE_PROMPT


@dataclass(frozen=True)
class RetrievedDocument:
    page_content: str
    metadata: dict[str, Any]


def collect_sources(docs: Iterable[Any]) -> list[str]:
    sources: list[str] = []
    for doc in docs:
        source = getattr(doc, "metadata", {}).get("source")
        if not source:
            continue
        source_name = os.path.basename(source)
        if source_name not in sources:
            sources.append(source_name)
    return sources


class AnswerPipeline:
    def __init__(
        self,
        api_key: str | None = DEEPSEEK_API_KEY,
        base_url: str = DEEPSEEK_BASE_URL,
        model: str = LLM_MODEL,
        client_factory: Callable[..., Any] = OpenAI,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client_factory = client_factory

    def retrieve(self, db: Any, question: str) -> list[Any]:
        retriever = db.as_retriever(search_kwargs={"k": 4})
        return list(retriever.invoke(question))

    def build_messages(self, docs: list[Any], question: str, memory: Any) -> list[dict[str, str]]:
        context = "\n\n".join(getattr(doc, "page_content", "") for doc in docs)
        current_user_message = f"""
【参考内容】
{context}

【问题】
{question}

请直接、简洁地回答：
"""
        messages = [{"role": "system", "content": STYLE_PROMPT}]
        for msg in memory.load_memory_variables({})["chat_history"]:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": msg.content})
        messages.append({"role": "user", "content": current_user_message})
        return messages

    def stream_answer(self, db: Any, question: str, memory: Any) -> Iterable[str]:
        if not self.api_key:
            yield "调用 API 时出错：缺少 DEEPSEEK_API_KEY，请先配置环境变量。"
            return

        docs = self.retrieve(db, question)
        messages = self.build_messages(docs, question, memory)
        full_response = ""
        for content in self._generate_text(messages):
            full_response += content
            yield content

        sources = collect_sources(docs)
        if sources:
            sources_text = "\n\n**参考来源：**\n" + "\n".join(f"- {source}" for source in sources)
            full_response += sources_text
            yield sources_text

        memory.save_context({"input": question}, {"output": full_response})

    def answer(self, db: Any, question: str, memory: Any) -> str:
        return "".join(self.stream_answer(db, question, memory))

    def _generate_text(self, messages: list[dict[str, str]]) -> Iterable[str]:
        client = self.client_factory(api_key=self.api_key, base_url=self.base_url)
        stream = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
```

- [ ] **Step 4: Replace rag_pipeline compatibility wrapper**

Modify `src/rag_pipeline.py` to:

```python
from src.answer_pipeline import AnswerPipeline


def ask_question(db, question, memory):
    return AnswerPipeline().answer(db, question, memory)
```

- [ ] **Step 5: Run answer pipeline tests**

Run:

```powershell
python -m unittest tests.test_answer_pipeline -v
```

Expected: all tests PASS.

## Task 5: Verification

**Files:**
- Modify: none unless verification exposes failures.

- [ ] **Step 1: Run all unit tests**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: all tests PASS.

- [ ] **Step 2: Run Python compile check**

Run:

```powershell
python -m py_compile app.py main.py src\config.py src\vector_db.py src\rag_pipeline.py src\data_loader.py src\knowledge_graph.py src\chat_history_manager.py src\ingestion_manifest.py src\answer_pipeline.py src\persistence_schema.py
```

Expected: exit code 0.

- [ ] **Step 3: Inspect git diff**

Run:

```powershell
git diff --stat
git status --short
```

Expected: only docs, tests, and scoped Python refactor files changed.

## Self-Review

- Spec coverage: the plan covers documentation, memory persistence schema, vector manifest, answer pipeline extraction, and tests. Full Next.js/FastAPI migration is intentionally deferred because it is a separate multi-service implementation.
- Placeholder scan: no step uses `TBD`, `TODO`, or unspecified implementation.
- Type consistency: `BuildSettings`, `AnswerPipeline`, `RetrievedDocument`, `TABLES`, and `required_tables` signatures are consistent across tests and implementation steps.
