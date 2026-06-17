import tempfile
import unittest
from pathlib import Path

from src.api.object_catalog import get_studio_objects


class ObjectCatalogTests(unittest.TestCase):
    def test_default_catalog_exposes_only_kk_object_from_local_documents(self):
        objects = get_studio_objects()

        self.assertEqual([item.id for item in objects], ["kk-advisor"])
        self.assertGreaterEqual(objects[0].documents, 1)
        self.assertIn("KK", objects[0].name)

    def test_document_count_comes_from_supported_files_in_data_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp)
            (data_path / "book1.pdf").write_text("pdf", encoding="utf-8")
            (data_path / "notes.txt").write_text("txt", encoding="utf-8")
            (data_path / "ignore.tmp").write_text("tmp", encoding="utf-8")

            objects = get_studio_objects(data_path=data_path)

            self.assertEqual(objects[0].documents, 2)


if __name__ == "__main__":
    unittest.main()
