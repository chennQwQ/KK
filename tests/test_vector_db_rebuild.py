import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path


def import_vector_db_with_stubs():
    modules = {
        "langchain_community": types.ModuleType("langchain_community"),
        "langchain_community.vectorstores": types.ModuleType(
            "langchain_community.vectorstores"
        ),
        "langchain_community.embeddings": types.ModuleType(
            "langchain_community.embeddings"
        ),
        "langchain_text_splitters": types.ModuleType("langchain_text_splitters"),
        "langchain_community.document_loaders": types.ModuleType(
            "langchain_community.document_loaders"
        ),
        "src.knowledge_graph": types.ModuleType("src.knowledge_graph"),
    }

    class Chroma:
        pass

    class HuggingFaceEmbeddings:
        pass

    class RecursiveCharacterTextSplitter:
        pass

    class TextLoader:
        pass

    class PyPDFLoader:
        pass

    modules["langchain_community.vectorstores"].Chroma = Chroma
    modules["langchain_community.embeddings"].HuggingFaceEmbeddings = (
        HuggingFaceEmbeddings
    )
    modules["langchain_text_splitters"].RecursiveCharacterTextSplitter = (
        RecursiveCharacterTextSplitter
    )
    modules["langchain_community.document_loaders"].TextLoader = TextLoader
    modules["langchain_community.document_loaders"].PyPDFLoader = PyPDFLoader
    modules["src.knowledge_graph"].initialize_knowledge_graph = lambda: None
    modules["src.knowledge_graph"].extract_and_load_knowledge = lambda *_args: None

    previous_modules = {
        name: sys.modules.get(name)
        for name in [*modules, "src.vector_db", "src.data_loader"]
    }
    sys.modules.update(modules)
    sys.modules.pop("src.vector_db", None)
    sys.modules.pop("src.data_loader", None)
    try:
        return importlib.import_module("src.vector_db")
    finally:
        for name, previous in previous_modules.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


class VectorDbRebuildTests(unittest.TestCase):
    def setUp(self):
        self.vector_db = import_vector_db_with_stubs()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "chroma"
        self.db_path.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manifest_only_directory_has_no_chroma_persistence(self):
        (self.db_path / "manifest.json").write_text("{}", encoding="utf-8")

        self.assertFalse(self.vector_db.has_chroma_persistence(self.db_path))

    def test_chroma_file_counts_as_persistence_when_manifest_exists(self):
        (self.db_path / "manifest.json").write_text("{}", encoding="utf-8")
        (self.db_path / "chroma.sqlite3").write_text("sqlite", encoding="utf-8")

        self.assertTrue(self.vector_db.has_chroma_persistence(self.db_path))

    def test_unrelated_file_does_not_count_as_chroma_persistence(self):
        (self.db_path / "manifest.json").write_text("{}", encoding="utf-8")
        (self.db_path / "notes.tmp").write_text("ignore", encoding="utf-8")

        self.assertFalse(self.vector_db.has_chroma_persistence(self.db_path))

    def test_reset_chroma_persist_directory_removes_only_contents(self):
        nested = self.db_path / "index" / "segment.bin"
        nested.parent.mkdir()
        nested.write_bytes(b"segment")
        (self.db_path / "chroma.sqlite3").write_text("sqlite", encoding="utf-8")

        self.vector_db.reset_chroma_persist_directory(self.db_path)

        self.assertTrue(self.db_path.exists())
        self.assertEqual([], list(self.db_path.iterdir()))
        self.assertTrue(Path(self.temp_dir.name).exists())


if __name__ == "__main__":
    unittest.main()
