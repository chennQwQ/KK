from pathlib import Path

from src.api.object_catalog import SUPPORTED_KNOWLEDGE_EXTENSIONS
from src.api.schemas import KnowledgeBaseStatusResponse
from src.config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_PATH, DB_PATH, EMBED_MODEL
from src.ingestion_manifest import BuildSettings, MANIFEST_FILE, is_manifest_current, load_manifest

CHROMA_SQLITE_FILE = "chroma.sqlite3"


def build_knowledge_base_status(
    data_path: str | Path = DATA_PATH,
    db_path: str | Path = DB_PATH,
) -> KnowledgeBaseStatusResponse:
    data_dir = Path(data_path)
    db_dir = Path(db_path)
    source_files = _source_file_names(data_dir)
    manifest = load_manifest(db_dir)
    manifest_exists = manifest is not None
    index_exists = _has_chroma_index(db_dir)
    manifest_current = is_manifest_current(
        data_dir,
        BuildSettings(
            embedding_model=EMBED_MODEL,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        ),
        manifest,
    )

    if not source_files:
        status = "missing"
    elif index_exists and manifest_current:
        status = "ready"
    else:
        status = "needs_rebuild"

    return KnowledgeBaseStatusResponse(
        status=status,
        has_db=index_exists,
        object_id="kk-advisor",
        knowledge_base_name="KK 本地文档",
        document_count=len(source_files),
        source_files=source_files,
        manifest_exists=manifest_exists,
        index_exists=index_exists,
        manifest_current=manifest_current,
    )


def _source_file_names(data_path: Path) -> list[str]:
    if not data_path.exists():
        return []

    return sorted(
        item.name
        for item in data_path.iterdir()
        if item.is_file() and item.suffix.lower() in SUPPORTED_KNOWLEDGE_EXTENSIONS
    )


def _has_chroma_index(db_path: Path) -> bool:
    if not db_path.exists() or not db_path.is_dir():
        return False

    return any(
        child.name == CHROMA_SQLITE_FILE
        or (child.name != MANIFEST_FILE and child.is_dir())
        for child in db_path.iterdir()
    )
