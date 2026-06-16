import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_PATH, DB_PATH, EMBED_MODEL
from src.data_loader import load_documents, split_documents
from src.ingestion_manifest import (
    BuildSettings,
    build_manifest,
    is_manifest_current,
    load_manifest,
    save_manifest,
)
from src.knowledge_graph import initialize_knowledge_graph, extract_and_load_knowledge

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
    is_db_missing_or_empty = not os.path.exists(DB_PATH) or not os.listdir(DB_PATH)
    should_rebuild = is_db_missing_or_empty or not is_manifest_current(DATA_PATH, settings, manifest)

    if should_rebuild:
        print("⚙️ 创建知识库...")
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
