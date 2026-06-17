import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_PATH, DB_PATH, EMBED_MODEL
from src.data_loader import load_documents, split_documents
from src.ingestion_manifest import (
    BuildSettings,
    MANIFEST_FILE,
    build_manifest,
    is_manifest_current,
    load_manifest,
    save_manifest,
)

CHROMA_SQLITE_FILE = "chroma.sqlite3"
EMBEDDING_MODEL_KWARGS = {"local_files_only": True}


@dataclass
class IndexRebuildResult:
    status: str
    chunks: int = 0
    elapsed_ms: int = 0
    error: str | None = None


def create_vector_db(chunks, db_path=DB_PATH):
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs=EMBEDDING_MODEL_KWARGS,
    )
    db = Chroma.from_documents(chunks, embeddings, persist_directory=str(db_path))
    db.persist()
    return db


def load_vector_db(db_path=DB_PATH):
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs=EMBEDDING_MODEL_KWARGS,
    )
    return Chroma(persist_directory=str(db_path), embedding_function=embeddings)


def has_chroma_persistence(db_path):
    path = Path(db_path)
    if not path.exists() or not path.is_dir():
        return False

    return any(
        child.name == CHROMA_SQLITE_FILE
        or (child.name != MANIFEST_FILE and child.is_dir())
        for child in path.iterdir()
    )


def reset_chroma_persist_directory(db_path):
    path = Path(db_path)
    resolved_path = path.resolve()

    if resolved_path.parent == resolved_path:
        raise ValueError(f"Refusing to clear root directory: {resolved_path}")

    if resolved_path.exists() and not resolved_path.is_dir():
        raise ValueError(f"Chroma persist path is not a directory: {resolved_path}")

    resolved_path.mkdir(parents=True, exist_ok=True)
    for child in resolved_path.iterdir():
        resolved_child = child.resolve()
        if resolved_path not in resolved_child.parents:
            raise ValueError(f"Refusing to clear path outside Chroma DB: {resolved_child}")

        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def rebuild_vector_db(
    data_path=DATA_PATH,
    db_path=DB_PATH,
    build_knowledge_graph=True,
) -> IndexRebuildResult:
    started = time.perf_counter()

    try:
        reset_chroma_persist_directory(db_path)
        docs = load_documents(data_path=data_path)
        chunks = split_documents(docs)
        create_vector_db(chunks, db_path=db_path)

        settings = BuildSettings(
            embedding_model=EMBED_MODEL,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        save_manifest(db_path, build_manifest(data_path, settings))

        if build_knowledge_graph:
            _load_documents_into_knowledge_graph(docs)

        return IndexRebuildResult(
            status="rebuilt",
            chunks=len(chunks),
            elapsed_ms=int((time.perf_counter() - started) * 1000),
            error=None,
        )
    except Exception as exc:
        return IndexRebuildResult(
            status="failed",
            chunks=0,
            elapsed_ms=int((time.perf_counter() - started) * 1000),
            error=str(exc),
        )


def initialize_knowledge_base():
    settings = BuildSettings(
        embedding_model=EMBED_MODEL,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    manifest = load_manifest(DB_PATH)
    has_existing_chroma = has_chroma_persistence(DB_PATH)
    manifest_current = is_manifest_current(DATA_PATH, settings, manifest)
    should_rebuild = not has_existing_chroma

    if should_rebuild:
        print("Creating knowledge base...")
        docs = load_documents()
        chunks = split_documents(docs)
        db = create_vector_db(chunks)
        save_manifest(DB_PATH, build_manifest(DATA_PATH, settings))
        _load_documents_into_knowledge_graph(docs)
    else:
        if not manifest_current:
            print("Knowledge base manifest is stale; load existing index and rebuild explicitly when ready.")
        print("Loading knowledge base...")
        db = load_vector_db(DB_PATH)

    print("Knowledge base ready.")
    return db


def _load_documents_into_knowledge_graph(docs):
    knowledge_graph = _load_optional_knowledge_graph()
    kg_driver = knowledge_graph.initialize_knowledge_graph() if knowledge_graph else None
    if not kg_driver:
        return

    print("Loading extracted knowledge graph...")
    for doc in docs:
        doc_source = os.path.basename(doc.metadata.get("source", "unknown"))
        knowledge_graph.extract_and_load_knowledge(doc.page_content, doc_source)


def _load_optional_knowledge_graph():
    try:
        from src import knowledge_graph
    except ImportError:
        return None

    return knowledge_graph
