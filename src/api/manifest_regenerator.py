from pathlib import Path

from src.api.schemas import ManifestRegenerateItem, ManifestRegenerateResponse
from src.config import DATA_PATH
from src.document_ingestion import (
    DocumentSourceType,
    classify_document_source,
    generate_book_manifest_file,
    generate_forum_qa_manifest_file,
)


def regenerate_structured_manifests(data_path: str | Path = DATA_PATH) -> ManifestRegenerateResponse:
    root = Path(data_path)
    generated: list[ManifestRegenerateItem] = []

    for source in sorted(root.glob("*.pdf"), key=lambda path: path.name):
        source_type = classify_document_source(source)
        if source_type == DocumentSourceType.FORUM_QA:
            output_path = root / "processed" / "forum" / f"{source.stem}.manifest.json"
            manifest = generate_forum_qa_manifest_file(source, output_path)
        else:
            output_path = root / "processed" / "books" / f"{source.stem}.manifest.json"
            manifest = generate_book_manifest_file(source, output_path)

        generated.append(
            ManifestRegenerateItem(
                source_file=source.name,
                source_type=manifest["source_type"],
                manifest_path=str(output_path),
                parse_status=manifest["parse_status"],
                items=len(manifest.get("items", [])),
                pages=len(manifest.get("pages", [])),
                chapters=len(manifest.get("chapters", [])),
            )
        )

    return ManifestRegenerateResponse(generated=generated)
