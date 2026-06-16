import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


MANIFEST_FILE = "manifest.json"
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
MANIFEST_VERSION = 1


@dataclass(frozen=True)
class BuildSettings:
    embedding_model: str
    chunk_size: int
    chunk_overlap: int


def _source_files(data_path):
    path = Path(data_path)
    if not path.exists():
        return []

    return sorted(
        (
            source
            for source in path.iterdir()
            if source.is_file() and source.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=lambda source: source.name,
    )


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(data_path, settings):
    return {
        "version": MANIFEST_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "settings": asdict(settings),
        "sources": [
            {
                "name": source.name,
                "size": source.stat().st_size,
                "sha256": _sha256(source),
            }
            for source in _source_files(data_path)
        ],
    }


def manifest_path(db_path):
    return Path(db_path) / MANIFEST_FILE


def load_manifest(db_path):
    path = manifest_path(db_path)
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def save_manifest(db_path, manifest):
    path = manifest_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as manifest_file:
        json.dump(manifest, manifest_file, ensure_ascii=False, indent=2, sort_keys=True)
        manifest_file.write("\n")


def is_manifest_current(data_path, settings, manifest):
    if not manifest:
        return False

    current_manifest = build_manifest(data_path, settings)
    return (
        manifest.get("version") == current_manifest["version"]
        and manifest.get("settings") == current_manifest["settings"]
        and manifest.get("sources") == current_manifest["sources"]
    )
