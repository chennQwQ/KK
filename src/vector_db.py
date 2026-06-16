import os
import shutil
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
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
from src.knowledge_graph import initialize_knowledge_graph, extract_and_load_knowledge

CHROMA_SQLITE_FILE = "chroma.sqlite3"

# ========== 3. 创建向量库 ==========
def create_vector_db(chunks):
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = Chroma.from_documents(chunks, embeddings, persist_directory=DB_PATH)
    db.persist()
    return db

# ========== 4. 加载向量库 ==========
def load_vector_db():
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    return db


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


# ========== 5. 初始化知识库 (向量库 + 知识图谱) ==========
def initialize_knowledge_base():
    # 初始化知识图谱
    kg_driver = initialize_knowledge_graph()
    settings = BuildSettings(
        embedding_model=EMBED_MODEL,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    manifest = load_manifest(DB_PATH)
    has_existing_chroma = has_chroma_persistence(DB_PATH)
    manifest_current = is_manifest_current(DATA_PATH, settings, manifest)
    should_rebuild = not has_existing_chroma or not manifest_current

    if should_rebuild:
        print("⚙️ 创建知识库...")
        if has_existing_chroma and not manifest_current:
            reset_chroma_persist_directory(DB_PATH)

        docs = load_documents()
        chunks = split_documents(docs)
        db = create_vector_db(chunks)
        save_manifest(DB_PATH, build_manifest(DATA_PATH, settings))

        # 提取知识并导入到知识图谱
        if kg_driver:
            print("⚙️ 提取知识并导入知识图谱...")
            for doc in docs:
                doc_source = os.path.basename(doc.metadata.get('source', 'unknown'))
                extract_and_load_knowledge(doc.page_content, doc_source)
    else:
        print("📦 加载知识库...")
        db = load_vector_db()

    print("✅ 知识库准备完成")
    return db
