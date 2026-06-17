# Document Ingestion Plan

Current scope: use the existing KK files in `data/` as the first real object knowledge base.

## Source Types

Documents are classified before chunking:

- `book`: long-form books such as `book1.pdf` and `book2.pdf`.
- `forum_qa`: forum question/answer material such as `qa.pdf`.

The original PDFs remain in place. Structured manifests are generated under `data/processed/` and are preferred by Chroma ingestion when present.

## Processing Order

1. Process `qa.pdf` first because forum Q&A is naturally suited to RAG retrieval.
2. Process books by chapter after Q&A structure is stable.
3. Add automatic chapter detection and topic classification after the first manual/semiautomatic pass proves the metadata shape.

## Current QA Output

`data/processed/forum/qa.manifest.json` is generated from `qa.pdf`.

The current extractor records page-level text and previews, then parses stable forum floor headers into item-level `forum_post` records. Pages that cannot be parsed still remain available as page records, so Chroma ingestion can fall back without losing source coverage.

Current generated state:

```json
{
  "source_file": "qa.pdf",
  "source_type": "forum_qa",
  "parse_status": "parsed",
  "pages": 1018,
  "items": 846
}
```

## Manifest Contract

The root ingestion manifest records each source file with:

```json
{
  "name": "qa.pdf",
  "source_type": "forum_qa",
  "structured_manifest": "processed/forum/qa.manifest.json"
}
```

Books use:

```json
{
  "name": "book1.pdf",
  "source_type": "book",
  "structured_manifest": "processed/books/book1.manifest.json"
}
```

Current generated book state:

```json
[
  {
    "source_file": "book1.pdf",
    "source_type": "book",
    "parse_status": "needs_review",
    "outline": 293,
    "chapters": 0
  },
  {
    "source_file": "book2.pdf",
    "source_type": "book",
    "parse_status": "parsed",
    "outline": 66,
    "chapters": 12
  }
]
```

## Next Steps

1. Improve parser rules for comment blocks and nested replies inside each forum post.
2. Add topic classification for parsed forum posts.
3. Review `book1.pdf` manually or add OCR because its outline contains page-number entries rather than chapter titles.
4. Add OCR/full-text extraction for scanned book pages before using book manifests as primary Chroma text input.
5. Add a separate vector-index rebuild action after manifest regeneration, with status feedback from Chroma.

## Implemented Frontend Control

The knowledge-base module now calls `POST /knowledge-base/manifests/regenerate` and displays one row per generated manifest, including source type, parse status, page count, item count, and chapter count.
