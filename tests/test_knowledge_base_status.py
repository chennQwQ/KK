import tempfile
import unittest
from pathlib import Path

from src.api.knowledge_base_status import build_knowledge_base_status
from src.config import CHUNK_OVERLAP, CHUNK_SIZE, EMBED_MODEL
from src.ingestion_manifest import BuildSettings, build_manifest, save_manifest


class KnowledgeBaseStatusTests(unittest.TestCase):
    def test_status_reports_local_kk_documents_and_missing_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_path = root / "data"
            db_path = root / "chroma"
            data_path.mkdir()
            db_path.mkdir()
            (data_path / "book1.pdf").write_text("pdf", encoding="utf-8")
            (data_path / "book2.pdf").write_text("pdf", encoding="utf-8")
            (data_path / "ignore.tmp").write_text("tmp", encoding="utf-8")

            status = build_knowledge_base_status(data_path=data_path, db_path=db_path)

            self.assertEqual(status.status, "needs_rebuild")
            self.assertFalse(status.has_db)
            self.assertEqual(status.document_count, 2)
            self.assertEqual(status.source_files, ["book1.pdf", "book2.pdf"])
            self.assertFalse(status.manifest_exists)
            self.assertFalse(status.index_exists)
            self.assertFalse(status.manifest_current)

    def test_status_is_ready_when_manifest_and_chroma_index_are_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_path = root / "data"
            db_path = root / "chroma"
            data_path.mkdir()
            db_path.mkdir()
            (data_path / "book1.pdf").write_text("pdf", encoding="utf-8")
            (db_path / "chroma.sqlite3").write_text("sqlite", encoding="utf-8")
            settings = BuildSettings(
                embedding_model=EMBED_MODEL,
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
            )
            save_manifest(db_path, build_manifest(data_path, settings))

            status = build_knowledge_base_status(data_path=data_path, db_path=db_path)

            self.assertEqual(status.status, "ready")
            self.assertTrue(status.has_db)
            self.assertTrue(status.manifest_exists)
            self.assertTrue(status.index_exists)
            self.assertTrue(status.manifest_current)


if __name__ == "__main__":
    unittest.main()
