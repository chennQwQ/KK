import json
import re
from enum import StrEnum
from pathlib import Path
from typing import Any


class DocumentSourceType(StrEnum):
    BOOK = "book"
    FORUM_QA = "forum_qa"


BOOK_CHAPTER_OVERRIDES = {
    "book1.pdf": [
        {"title": "第一章", "page_start": 16},
        {"title": "第二章", "page_start": 75},
        {"title": "第三章", "page_start": 134},
        {"title": "第四章", "page_start": 193},
        {"title": "第五章", "page_start": 252},
    ],
}


def classify_document_source(path: str | Path) -> DocumentSourceType:
    name = Path(path).name.lower()
    if name.startswith("qa") or "qa" in Path(path).stem.lower():
        return DocumentSourceType.FORUM_QA

    return DocumentSourceType.BOOK


def build_forum_qa_manifest(source_file: str, pages: list[dict[str, Any]]) -> dict[str, Any]:
    items = []

    for page in pages:
        page_number = int(page["page"])
        text = str(page.get("text", ""))
        qa_pairs = _parse_qa_pairs(text)
        for index, qa_pair in enumerate(qa_pairs, start=1):
            items.append(
                {
                    "id": f"{Path(source_file).stem}-p{page_number}-{index}",
                    "item_type": "qa_pair",
                    "source_type": DocumentSourceType.FORUM_QA.value,
                    "source_file": source_file,
                    "question": qa_pair["question"],
                    "answer": qa_pair["answer"],
                    "topic": "uncategorized",
                    "page_start": page_number,
                    "page_end": page_number,
                }
            )
        if qa_pairs:
            continue

        for forum_post in _parse_forum_posts(text):
            items.append(
                {
                    "id": f"{Path(source_file).stem}-p{page_number}-floor{forum_post['floor']}",
                    "item_type": "forum_post",
                    "source_type": DocumentSourceType.FORUM_QA.value,
                    "source_file": source_file,
                    "author": forum_post["author"],
                    "posted_at": forum_post["posted_at"],
                    "floor": forum_post["floor"],
                    "content": forum_post["content"],
                    "comments": forum_post.get("comments", []),
                    "replies": forum_post.get("replies", []),
                    "topic": forum_post.get("topic", "uncategorized"),
                    "page_start": page_number,
                    "page_end": page_number,
                }
            )

    return {
        "source_type": DocumentSourceType.FORUM_QA.value,
        "source_file": source_file,
        "parse_status": "parsed" if items else "needs_review",
        "pages": [_page_record(page) for page in pages],
        "items": items,
    }


def build_book_manifest(
    source_file: str,
    page_count: int,
    outline_entries: list[dict[str, Any]],
    chapter_overrides: list[dict[str, Any]] | None = None,
    pages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    source_starts = chapter_overrides if chapter_overrides else outline_entries
    chapter_starts = _chapter_starts_from_records(source_file, source_starts)
    page_text = {
        int(page["page"]): _clean_text(str(page.get("text", "")))
        for page in pages or []
    }
    chapters = []

    for index, chapter in enumerate(chapter_starts):
        next_start = (
            chapter_starts[index + 1]["page_start"]
            if index + 1 < len(chapter_starts)
            else page_count + 1
        )
        chapters.append(
            {
                **chapter,
                "page_end": max(chapter["page_start"], next_start - 1),
                "topic": "uncategorized",
                "text": _chapter_text(
                    page_text,
                    chapter["page_start"],
                    max(chapter["page_start"], next_start - 1),
                ),
            }
        )

    return {
        "source_type": DocumentSourceType.BOOK.value,
        "source_file": source_file,
        "parse_status": "parsed" if chapters else "needs_review",
        "page_count": page_count,
        "outline": [
            {
                "title": _clean_text(str(entry["title"])),
                "page": int(entry["page"]),
                "level": int(entry.get("level", 0)),
            }
            for entry in outline_entries
        ],
        "chapters": chapters,
    }


def write_json_manifest(path: str | Path, manifest: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def manifest_to_documents(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if manifest.get("chapters"):
        return [_book_chapter_document(manifest, chapter) for chapter in manifest["chapters"]]

    if manifest.get("items"):
        return [_item_document(manifest, item) for item in manifest["items"]]

    return [_page_document(manifest, page) for page in manifest.get("pages", []) if page.get("text")]


def extract_pdf_pages(path: str | Path, max_pages: int | None = None) -> list[dict[str, Any]]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = []
    page_count = len(reader.pages) if max_pages is None else min(len(reader.pages), max_pages)

    for index in range(page_count):
        page = reader.pages[index]
        pages.append(
            {
                "page": index + 1,
                "text": page.extract_text() or "",
            }
        )

    return pages


def extract_pdf_pages_with_ocr(
    path: str | Path,
    max_pages: int | None = None,
    min_native_chars: int = 40,
    native_extractor=extract_pdf_pages,
    ocr_page_extractor=None,
) -> list[dict[str, Any]]:
    pages = native_extractor(path, max_pages=max_pages)
    if ocr_page_extractor is None:
        ocr_page_extractor = extract_pdf_page_ocr_text

    for page in pages:
        text = _clean_text(str(page.get("text", "")))
        if len(text) >= min_native_chars:
            page["text"] = text
            page["extraction_method"] = "native"
            continue

        try:
            ocr_text = _clean_text(ocr_page_extractor(path, int(page["page"])))
        except Exception:
            page["text"] = text
            page["extraction_method"] = "ocr_unavailable"
            continue

        if ocr_text:
            page["text"] = ocr_text
            page["extraction_method"] = "ocr"
        else:
            page["text"] = text
            page["extraction_method"] = "native_sparse"

    return pages


def extract_pdf_page_ocr_text(path: str | Path, page_number: int) -> str:
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:
        return ""

    images = convert_from_path(
        str(path),
        first_page=page_number,
        last_page=page_number,
        dpi=220,
    )
    if not images:
        return ""

    return pytesseract.image_to_string(images[0], lang="chi_sim+eng")


def extract_pdf_outline_entries(path: str | Path) -> list[dict[str, Any]]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    entries: list[dict[str, Any]] = []
    _collect_outline_entries(reader, reader.outline, entries)
    return entries


def generate_forum_qa_manifest_file(
    pdf_path: str | Path,
    output_path: str | Path,
    max_pages: int | None = None,
) -> dict[str, Any]:
    source = Path(pdf_path)
    manifest = build_forum_qa_manifest(
        source_file=source.name,
        pages=extract_pdf_pages(source, max_pages=max_pages),
    )
    write_json_manifest(output_path, manifest)
    return manifest


def generate_book_manifest_file(
    pdf_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    from pypdf import PdfReader

    source = Path(pdf_path)
    reader = PdfReader(str(source))
    manifest = build_book_manifest(
        source_file=source.name,
        page_count=len(reader.pages),
        outline_entries=extract_pdf_outline_entries(source),
        chapter_overrides=BOOK_CHAPTER_OVERRIDES.get(source.name),
        pages=extract_pdf_pages_with_ocr(source),
    )
    write_json_manifest(output_path, manifest)
    return manifest


def _parse_qa_pairs(text: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r"(?:问|Q|Question)[:：]\s*(?P<question>.*?)[\r\n]+(?:答|A|Answer)[:：]\s*(?P<answer>.*?)(?=(?:[\r\n]+(?:问|Q|Question)[:：])|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    pairs = []

    for match in pattern.finditer(text):
        question = _clean_text(match.group("question"))
        answer = _clean_text(match.group("answer"))
        if question and answer:
            pairs.append({"question": question, "answer": answer})

    return pairs


def _parse_forum_posts(text: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"(?P<author>[\w\u4e00-\u9fff.-]+)\s+楼主\s+"
        r"(?P<posted_at>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s+"
        r"(?P<floor>\d+)楼\s+"
        r"(?P<content>.*?)(?=(?:[\w\u4e00-\u9fff.-]+\s+楼主\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+\d+楼\s+)|\Z)",
        re.DOTALL,
    )
    posts = []
    for match in pattern.finditer(text):
        content = _clean_text(match.group("content"))
        if not content:
            continue

        posts.append(
            {
                "author": match.group("author"),
                "posted_at": match.group("posted_at"),
                "floor": int(match.group("floor")),
                "content": content,
                "comments": _parse_comments(content),
                "replies": _parse_replies(content),
                "topic": _infer_topic(content),
            }
        )

    return posts


def _chapter_starts_from_records(
    source_file: str,
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    starts = []
    for index, entry in enumerate(records, start=1):
        title = _clean_text(str(entry.get("title", "")))
        if not title:
            continue

        is_override = "page_start" in entry
        if not is_override and not _is_chapter_title(title):
            continue

        starts.append(
            {
                "id": str(entry.get("id") or f"{Path(source_file).stem}-chapter-{index}"),
                "source_type": DocumentSourceType.BOOK.value,
                "source_file": source_file,
                "title": title,
                "page_start": int(entry.get("page_start") or entry.get("page")),
            }
        )

    return starts


def _chapter_text(page_text: dict[int, str], page_start: int, page_end: int) -> str:
    return "\n".join(
        text
        for page, text in sorted(page_text.items())
        if page_start <= page <= page_end and text
    )


def _parse_comments(content: str) -> list[dict[str, str]]:
    comments = []
    pattern = re.compile(
        r"(?:评论|comment)[:：]\s*(?:(?P<author>[\w\u4e00-\u9fff.-]+)\s*[:：]\s*)?(?P<content>[^。\n]+)",
        re.IGNORECASE,
    )
    for match in pattern.finditer(content):
        comments.append(
            {
                "author": match.group("author") or "unknown",
                "content": _clean_text(match.group("content")),
            }
        )
    return comments


def _parse_replies(content: str) -> list[dict[str, Any]]:
    replies = []
    pattern = re.compile(
        r"(?:回复|reply)\s*(?:(?P<floor>\d+)\s*(?:楼|floor))?[:：]\s*(?P<content>[^。\n]+)",
        re.IGNORECASE,
    )
    for match in pattern.finditer(content):
        floor = match.group("floor")
        replies.append(
            {
                "to_floor": int(floor) if floor else None,
                "content": _clean_text(match.group("content")),
            }
        )
    return replies


def _infer_topic(content: str) -> str:
    text = content.lower()
    topic_keywords = {
        "housing": ["房", "地产", "住房", "楼市"],
        "market": ["市场", "股票", "指数", "价格"],
        "currency": ["货币", "信用", "通胀", "美元"],
    }
    for topic, keywords in topic_keywords.items():
        if any(keyword in text for keyword in keywords):
            return topic
    return "uncategorized"


def _collect_outline_entries(reader: Any, outline: list[Any], entries: list[dict[str, Any]], level: int = 0) -> None:
    for item in outline:
        if isinstance(item, list):
            _collect_outline_entries(reader, item, entries, level + 1)
            continue

        try:
            page_number = reader.get_destination_page_number(item) + 1
        except Exception:
            continue

        entries.append(
            {
                "title": _clean_text(str(getattr(item, "title", item))),
                "page": page_number,
                "level": level,
            }
        )


def _is_chapter_title(title: str) -> bool:
    normalized = _clean_text(title)
    return bool(re.match(r"^(序)?第[一二三四五六七八九十百零〇\d]+章\b", normalized))


def _page_record(page: dict[str, Any]) -> dict[str, Any]:
    text = _clean_text(str(page.get("text", "")))
    return {
        "page": int(page["page"]),
        "text": text,
        "text_preview": text[:500],
        "text_length": len(text),
    }


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _item_document(manifest: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    if item.get("item_type") == "forum_post":
        return _forum_post_document(manifest, item)

    source_file = str(item.get("source_file") or manifest["source_file"])
    question = _clean_text(str(item.get("question", "")))
    answer = _clean_text(str(item.get("answer", "")))
    return {
        "text": f"Question: {question}\nAnswer: {answer}",
        "metadata": {
            "source": source_file,
            "source_type": str(item.get("source_type") or manifest["source_type"]),
            "document_kind": "forum_qa_item",
            "item_id": item.get("id"),
            "topic": item.get("topic", "uncategorized"),
            "page_start": int(item["page_start"]),
            "page_end": int(item["page_end"]),
            "parse_status": manifest.get("parse_status", "parsed"),
        },
    }


def _forum_post_document(manifest: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    comments = item.get("comments", [])
    replies = item.get("replies", [])
    text_parts = [_clean_text(str(item.get("content", "")))]
    text_parts.extend(
        f"Comment {comment.get('author', 'unknown')}: {_clean_text(str(comment.get('content', '')))}"
        for comment in comments
        if _clean_text(str(comment.get("content", "")))
    )
    text_parts.extend(
        f"Reply to floor {reply.get('to_floor')}: {_clean_text(str(reply.get('content', '')))}"
        for reply in replies
        if _clean_text(str(reply.get("content", "")))
    )
    return {
        "text": "\n".join(part for part in text_parts if part),
        "metadata": {
            "source": str(item.get("source_file") or manifest["source_file"]),
            "source_type": str(item.get("source_type") or manifest["source_type"]),
            "document_kind": "forum_post",
            "item_id": item.get("id"),
            "author": item.get("author"),
            "posted_at": item.get("posted_at"),
            "floor": int(item["floor"]),
            "topic": item.get("topic", "uncategorized"),
            "comment_count": len(comments),
            "reply_count": len(replies),
            "page_start": int(item["page_start"]),
            "page_end": int(item["page_end"]),
            "parse_status": manifest.get("parse_status", "parsed"),
        },
    }


def _book_chapter_document(manifest: dict[str, Any], chapter: dict[str, Any]) -> dict[str, Any]:
    title = _clean_text(str(chapter.get("title", "")))
    text = _clean_text(str(chapter.get("text", "")))
    page_start = int(chapter["page_start"])
    page_end = int(chapter["page_end"])
    return {
        "text": f"{title}\n{text}".strip(),
        "metadata": {
            "source": str(chapter.get("source_file") or manifest["source_file"]),
            "source_type": str(chapter.get("source_type") or manifest["source_type"]),
            "document_kind": "book_chapter",
            "item_id": chapter.get("id"),
            "chapter_title": title,
            "topic": chapter.get("topic", "uncategorized"),
            "page_start": page_start,
            "page_end": page_end,
            "parse_status": manifest.get("parse_status", "parsed"),
        },
    }


def _page_document(manifest: dict[str, Any], page: dict[str, Any]) -> dict[str, Any]:
    page_number = int(page["page"])
    return {
        "text": _clean_text(str(page["text"])),
        "metadata": {
            "source": str(manifest["source_file"]),
            "source_type": str(manifest["source_type"]),
            "document_kind": "forum_qa_page",
            "topic": "uncategorized",
            "page_start": page_number,
            "page_end": page_number,
            "parse_status": manifest.get("parse_status", "needs_review"),
        },
    }
