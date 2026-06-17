import tempfile
import unittest
from pathlib import Path

from src.document_ingestion import (
    DocumentSourceType,
    build_book_manifest,
    build_forum_qa_manifest,
    classify_document_source,
    extract_pdf_outline_entries,
    extract_pdf_pages,
    extract_pdf_pages_with_ocr,
    generate_book_manifest_file,
    generate_forum_qa_manifest_file,
    manifest_to_documents,
    write_json_manifest,
)


class DocumentIngestionPlanTests(unittest.TestCase):
    def test_classifies_qa_pdf_as_forum_qa_and_books_as_book(self):
        self.assertEqual(classify_document_source(Path("qa.pdf")), DocumentSourceType.FORUM_QA)
        self.assertEqual(classify_document_source(Path("book1.pdf")), DocumentSourceType.BOOK)
        self.assertEqual(classify_document_source(Path("book2.pdf")), DocumentSourceType.BOOK)

    def test_builds_book_manifest_from_outline_entries(self):
        manifest = build_book_manifest(
            source_file="book2.pdf",
            page_count=120,
            outline_entries=[
                {"title": "封面", "page": 1, "level": 0},
                {"title": "第一章  此朝无钱胜有钱", "page": 13, "level": 0},
                {"title": "谁毁掉了西周", "page": 16, "level": 0},
                {"title": "第二章  秦始皇统一了货币吗", "page": 35, "level": 0},
            ],
        )

        self.assertEqual(manifest["source_type"], "book")
        self.assertEqual(manifest["source_file"], "book2.pdf")
        self.assertEqual(manifest["parse_status"], "parsed")
        self.assertEqual(len(manifest["chapters"]), 2)
        self.assertEqual(manifest["chapters"][0]["title"], "第一章 此朝无钱胜有钱")
        self.assertEqual(manifest["chapters"][0]["page_start"], 13)
        self.assertEqual(manifest["chapters"][0]["page_end"], 34)
        self.assertEqual(manifest["chapters"][1]["page_end"], 120)

    def test_book_manifest_needs_review_when_outline_has_no_chapter_titles(self):
        manifest = build_book_manifest(
            source_file="book1.pdf",
            page_count=30,
            outline_entries=[
                {"title": "封面", "page": 1, "level": 0},
                {"title": "1", "page": 16, "level": 0},
            ],
        )

        self.assertEqual(manifest["parse_status"], "needs_review")
        self.assertEqual(manifest["chapters"], [])
        self.assertEqual(len(manifest["outline"]), 2)

    def test_book1_manifest_can_use_manual_chapter_overrides(self):
        manifest = build_book_manifest(
            source_file="book1.pdf",
            page_count=80,
            outline_entries=[{"title": "1", "page": 16, "level": 0}],
            chapter_overrides=[
                {"title": "第一章 货币的起点", "page_start": 16},
                {"title": "第二章 信用与周期", "page_start": 32},
            ],
        )

        self.assertEqual(manifest["parse_status"], "parsed")
        self.assertEqual(len(manifest["chapters"]), 2)
        self.assertEqual(manifest["chapters"][0]["page_end"], 31)
        self.assertEqual(manifest["chapters"][1]["page_end"], 80)

    def test_builds_forum_qa_manifest_from_extracted_pages(self):
        manifest = build_forum_qa_manifest(
            source_file="qa.pdf",
            pages=[
                {
                    "page": 1,
                    "text": "问：现在应该如何看待市场？\n答：先看周期，再看价格。\n问：风险在哪里？\n答：风险在共识过满。",
                }
            ],
        )

        self.assertEqual(manifest["source_type"], "forum_qa")
        self.assertEqual(manifest["source_file"], "qa.pdf")
        self.assertEqual(len(manifest["items"]), 2)
        self.assertEqual(manifest["items"][0]["question"], "现在应该如何看待市场？")
        self.assertEqual(manifest["items"][0]["answer"], "先看周期，再看价格。")
        self.assertEqual(manifest["items"][0]["page_start"], 1)
        self.assertEqual(manifest["parse_status"], "parsed")

    def test_builds_forum_post_items_from_real_pdf_floor_headers(self):
        manifest = build_forum_qa_manifest(
            source_file="qa.pdf",
            pages=[
                {
                    "page": 2,
                    "text": "kkndme 楼主 2010-08-10 19:06 2楼 1、人人都有居住权。房子是用来住的，不是用来炒的。",
                }
            ],
        )

        self.assertEqual(len(manifest["items"]), 1)
        self.assertEqual(manifest["items"][0]["item_type"], "forum_post")
        self.assertEqual(manifest["items"][0]["author"], "kkndme")
        self.assertEqual(manifest["items"][0]["posted_at"], "2010-08-10 19:06")
        self.assertEqual(manifest["items"][0]["floor"], 2)
        self.assertIn("人人都有居住权", manifest["items"][0]["content"])
        self.assertEqual(manifest["parse_status"], "parsed")

    def test_forum_qa_manifest_keeps_page_records_when_pairs_need_review(self):
        manifest = build_forum_qa_manifest(
            source_file="qa.pdf",
            pages=[{"page": 1, "text": "这是一段无法自动拆成问答的论坛内容。"}],
        )

        self.assertEqual(manifest["items"], [])
        self.assertEqual(manifest["parse_status"], "needs_review")
        self.assertEqual(manifest["pages"][0]["page"], 1)
        self.assertIn("论坛内容", manifest["pages"][0]["text_preview"])

    def test_writes_structured_manifest_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "processed" / "forum" / "qa.manifest.json"
            manifest = {"source_type": "forum_qa", "items": []}

            write_json_manifest(target, manifest)

            self.assertTrue(target.exists())
            self.assertIn('"source_type": "forum_qa"', target.read_text(encoding="utf-8"))

    def test_manifest_to_documents_prefers_qa_items(self):
        manifest = {
            "source_type": "forum_qa",
            "source_file": "qa.pdf",
            "parse_status": "parsed",
            "pages": [],
            "items": [
                {
                    "id": "qa-p3-1",
                    "question": "How should I read the market now?",
                    "answer": "Read the cycle before the price.",
                    "topic": "market",
                    "page_start": 3,
                    "page_end": 3,
                }
            ],
        }

        documents = manifest_to_documents(manifest)

        self.assertEqual(len(documents), 1)
        self.assertIn("Question: How should I read the market now?", documents[0]["text"])
        self.assertEqual(documents[0]["metadata"]["source"], "qa.pdf")
        self.assertEqual(documents[0]["metadata"]["source_type"], "forum_qa")
        self.assertEqual(documents[0]["metadata"]["page_start"], 3)
        self.assertEqual(documents[0]["metadata"]["page_end"], 3)
        self.assertEqual(documents[0]["metadata"]["topic"], "market")

    def test_manifest_to_documents_supports_forum_post_items(self):
        manifest = {
            "source_type": "forum_qa",
            "source_file": "qa.pdf",
            "parse_status": "parsed",
            "pages": [],
            "items": [
                {
                    "id": "qa-p2-floor2",
                    "item_type": "forum_post",
                    "source_type": "forum_qa",
                    "source_file": "qa.pdf",
                    "author": "kkndme",
                    "posted_at": "2010-08-10 19:06",
                    "floor": 2,
                    "content": "房子是用来住的，不是用来炒的。",
                    "topic": "uncategorized",
                    "page_start": 2,
                    "page_end": 2,
                }
            ],
        }

        documents = manifest_to_documents(manifest)

        self.assertEqual(documents[0]["text"], "房子是用来住的，不是用来炒的。")
        self.assertEqual(documents[0]["metadata"]["document_kind"], "forum_post")
        self.assertEqual(documents[0]["metadata"]["author"], "kkndme")
        self.assertEqual(documents[0]["metadata"]["floor"], 2)

    def test_forum_post_documents_include_comment_reply_and_topic_fields(self):
        manifest = {
            "source_type": "forum_qa",
            "source_file": "qa.pdf",
            "parse_status": "parsed",
            "pages": [],
            "items": [
                {
                    "id": "qa-p2-floor2",
                    "item_type": "forum_post",
                    "source_type": "forum_qa",
                    "source_file": "qa.pdf",
                    "author": "kkndme",
                    "posted_at": "2010-08-10 19:06",
                    "floor": 2,
                    "content": "房子是用来住的。",
                    "comments": [{"author": "reader", "content": "同意"}],
                    "replies": [{"to_floor": 1, "content": "回复一楼"}],
                    "topic": "housing",
                    "page_start": 2,
                    "page_end": 2,
                }
            ],
        }

        documents = manifest_to_documents(manifest)

        self.assertIn("Comment reader: 同意", documents[0]["text"])
        self.assertIn("Reply to floor 1: 回复一楼", documents[0]["text"])
        self.assertEqual(documents[0]["metadata"]["comment_count"], 1)
        self.assertEqual(documents[0]["metadata"]["reply_count"], 1)
        self.assertEqual(documents[0]["metadata"]["topic"], "housing")

    def test_manifest_to_documents_supports_book_chapters_with_text_chunks(self):
        manifest = {
            "source_type": "book",
            "source_file": "book1.pdf",
            "parse_status": "parsed",
            "chapters": [
                {
                    "id": "book1-chapter-1",
                    "title": "第一章 货币的起点",
                    "topic": "money",
                    "page_start": 10,
                    "page_end": 12,
                    "text": "chapter text",
                }
            ],
        }

        documents = manifest_to_documents(manifest)

        self.assertEqual(len(documents), 1)
        self.assertIn("第一章 货币的起点", documents[0]["text"])
        self.assertIn("chapter text", documents[0]["text"])
        self.assertEqual(documents[0]["metadata"]["document_kind"], "book_chapter")
        self.assertEqual(documents[0]["metadata"]["chapter_title"], "第一章 货币的起点")
        self.assertEqual(documents[0]["metadata"]["page_start"], 10)

    def test_manifest_to_documents_falls_back_to_page_records_when_items_need_review(self):
        manifest = {
            "source_type": "forum_qa",
            "source_file": "qa.pdf",
            "parse_status": "needs_review",
            "items": [],
            "pages": [
                {
                    "page": 4,
                    "text": "page level forum text",
                    "text_preview": "page level forum text",
                    "text_length": 21,
                }
            ],
        }

        documents = manifest_to_documents(manifest)

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]["text"], "page level forum text")
        self.assertEqual(documents[0]["metadata"]["source"], "qa.pdf")
        self.assertEqual(documents[0]["metadata"]["page_start"], 4)
        self.assertEqual(documents[0]["metadata"]["parse_status"], "needs_review")

    def test_extract_pdf_pages_returns_page_records_for_real_qa_pdf(self):
        pages = extract_pdf_pages(Path("data") / "qa.pdf", max_pages=1)

        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0]["page"], 1)
        self.assertIsInstance(pages[0]["text"], str)

    def test_extract_pdf_pages_with_ocr_uses_ocr_when_native_text_is_sparse(self):
        def fake_native(_path, max_pages=None):
            return [{"page": 1, "text": ""}]

        def fake_ocr(_path, page_number):
            return "ocr text"

        pages = extract_pdf_pages_with_ocr(
            Path("scan.pdf"),
            max_pages=1,
            native_extractor=fake_native,
            ocr_page_extractor=fake_ocr,
        )

        self.assertEqual(pages[0]["text"], "ocr text")
        self.assertEqual(pages[0]["extraction_method"], "ocr")

    def test_extract_pdf_pages_with_ocr_falls_back_when_ocr_runtime_fails(self):
        def fake_native(_path, max_pages=None):
            return [{"page": 1, "text": ""}]

        def broken_ocr(_path, page_number):
            raise RuntimeError("missing poppler")

        pages = extract_pdf_pages_with_ocr(
            Path("scan.pdf"),
            max_pages=1,
            native_extractor=fake_native,
            ocr_page_extractor=broken_ocr,
        )

        self.assertEqual(pages[0]["text"], "")
        self.assertEqual(pages[0]["extraction_method"], "ocr_unavailable")

    def test_extract_pdf_outline_entries_returns_real_book_outline(self):
        entries = extract_pdf_outline_entries(Path("data") / "book2.pdf")

        self.assertGreater(len(entries), 0)
        self.assertIn("title", entries[0])
        self.assertIn("page", entries[0])
        self.assertIn("level", entries[0])

    def test_generates_forum_qa_manifest_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "qa.manifest.json"

            manifest = generate_forum_qa_manifest_file(
                pdf_path=Path("data") / "qa.pdf",
                output_path=output_path,
                max_pages=1,
            )

            self.assertEqual(manifest["source_file"], "qa.pdf")
            self.assertTrue(output_path.exists())

    def test_generates_book_manifest_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "book2.manifest.json"

            manifest = generate_book_manifest_file(
                pdf_path=Path("data") / "book2.pdf",
                output_path=output_path,
            )

            self.assertEqual(manifest["source_file"], "book2.pdf")
            self.assertTrue(output_path.exists())
            self.assertIn("chapters", manifest)


if __name__ == "__main__":
    unittest.main()
