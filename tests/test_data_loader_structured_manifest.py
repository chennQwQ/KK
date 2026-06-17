import importlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path


def import_data_loader_with_stubs():
    modules = {
        "langchain_text_splitters": types.ModuleType("langchain_text_splitters"),
        "langchain_community": types.ModuleType("langchain_community"),
        "langchain_community.document_loaders": types.ModuleType(
            "langchain_community.document_loaders"
        ),
    }

    class RecursiveCharacterTextSplitter:
        def __init__(self, *args, **kwargs):
            pass

        def split_documents(self, documents):
            return documents

    class TextLoader:
        loaded_paths = []

        def __init__(self, path, encoding="utf-8"):
            self.path = path
            self.encoding = encoding

        def load(self):
            self.loaded_paths.append(Path(self.path).name)
            return []

    class PyPDFLoader:
        loaded_paths = []

        def __init__(self, path):
            self.path = path

        def load(self):
            self.loaded_paths.append(Path(self.path).name)
            return []

    modules["langchain_text_splitters"].RecursiveCharacterTextSplitter = (
        RecursiveCharacterTextSplitter
    )
    modules["langchain_community.document_loaders"].TextLoader = TextLoader
    modules["langchain_community.document_loaders"].PyPDFLoader = PyPDFLoader

    previous_modules = {
        name: sys.modules.get(name)
        for name in [*modules, "src.data_loader"]
    }
    sys.modules.update(modules)
    sys.modules.pop("src.data_loader", None)
    try:
        module = importlib.import_module("src.data_loader")
        return module, PyPDFLoader
    finally:
        for name, previous in previous_modules.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


class StructuredManifestDataLoaderTests(unittest.TestCase):
    def test_load_documents_prefers_structured_manifests_for_pdf_sources(self):
        data_loader, pdf_loader = import_data_loader_with_stubs()

        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp)
            (data_path / "qa.pdf").write_bytes(b"%PDF")
            (data_path / "book1.pdf").write_bytes(b"%PDF")
            manifest_path = data_path / "processed" / "forum" / "qa.manifest.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "source_type": "forum_qa",
                        "source_file": "qa.pdf",
                        "parse_status": "needs_review",
                        "items": [],
                        "pages": [
                            {
                                "page": 1,
                                "text": "manifest page text",
                                "text_preview": "manifest page text",
                                "text_length": 18,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            book_manifest_path = data_path / "processed" / "books" / "book1.manifest.json"
            book_manifest_path.parent.mkdir(parents=True)
            book_manifest_path.write_text(
                json.dumps(
                    {
                        "source_type": "book",
                        "source_file": "book1.pdf",
                        "parse_status": "parsed",
                        "chapters": [
                            {
                                "id": "book1-chapter-1",
                                "title": "第一章",
                                "topic": "money",
                                "page_start": 1,
                                "page_end": 4,
                                "text": "book chapter text",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            docs = data_loader.load_documents(data_path=data_path)

        self.assertEqual(pdf_loader.loaded_paths, [])
        self.assertEqual(len(docs), 2)
        docs_by_source = {doc.metadata["source"]: doc for doc in docs}
        self.assertEqual(docs_by_source["qa.pdf"].page_content, "manifest page text")
        self.assertEqual(docs_by_source["qa.pdf"].metadata["page_start"], 1)
        self.assertIn("book chapter text", docs_by_source["book1.pdf"].page_content)
        self.assertEqual(docs_by_source["book1.pdf"].metadata["document_kind"], "book_chapter")


if __name__ == "__main__":
    unittest.main()
