import json
import os
from pathlib import Path
from types import SimpleNamespace

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_PATH
from src.document_ingestion import manifest_to_documents


def load_documents(data_path=DATA_PATH):
    docs = []
    root = Path(data_path)

    for file_name in sorted(os.listdir(root)):
        path = root / file_name
        if not path.is_file():
            continue

        if path.suffix.lower() == ".txt":
            loader = TextLoader(str(path), encoding="utf-8")
            docs.extend(loader.load())
            continue

        if path.suffix.lower() == ".pdf":
            structured_docs = _load_structured_manifest(root, path)
            if structured_docs:
                docs.extend(structured_docs)
                continue

            loader = PyPDFLoader(str(path))
            docs.extend(loader.load())

    return docs


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


def _load_structured_manifest(data_path: Path, source_path: Path):
    manifest_path = _structured_manifest_path(data_path, source_path)
    if not manifest_path.exists():
        return []

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return [_to_document(document) for document in manifest_to_documents(manifest)]


def _structured_manifest_path(data_path: Path, source_path: Path) -> Path:
    forum_path = data_path / "processed" / "forum" / f"{source_path.stem}.manifest.json"
    if forum_path.exists():
        return forum_path

    return data_path / "processed" / "books" / f"{source_path.stem}.manifest.json"


def _to_document(document):
    try:
        from langchain_core.documents import Document

        return Document(
            page_content=document["text"],
            metadata=document["metadata"],
        )
    except ImportError:
        return SimpleNamespace(
            page_content=document["text"],
            metadata=document["metadata"],
        )
