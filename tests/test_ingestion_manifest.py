import tempfile
import unittest
from pathlib import Path

from src.ingestion_manifest import BuildSettings, build_manifest, is_manifest_current


class IngestionManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "data"
        self.data_path.mkdir()
        self.settings = BuildSettings(
            embedding_model="test-embedding-model",
            chunk_size=800,
            chunk_overlap=100,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manifest_is_current_when_source_files_and_settings_match(self):
        (self.data_path / "notes.txt").write_text("alpha", encoding="utf-8")
        (self.data_path / "paper.pdf").write_bytes(b"%PDF-test")

        manifest = build_manifest(self.data_path, self.settings)

        self.assertTrue(is_manifest_current(self.data_path, self.settings, manifest))

    def test_manifest_is_stale_when_file_content_changes(self):
        source = self.data_path / "notes.txt"
        source.write_text("alpha", encoding="utf-8")
        manifest = build_manifest(self.data_path, self.settings)

        source.write_text("bravo", encoding="utf-8")

        self.assertFalse(is_manifest_current(self.data_path, self.settings, manifest))

    def test_manifest_is_stale_when_settings_change(self):
        (self.data_path / "notes.txt").write_text("alpha", encoding="utf-8")
        manifest = build_manifest(self.data_path, self.settings)

        changed_settings = BuildSettings(
            embedding_model="test-embedding-model",
            chunk_size=400,
            chunk_overlap=100,
        )

        self.assertFalse(is_manifest_current(self.data_path, changed_settings, manifest))


if __name__ == "__main__":
    unittest.main()
