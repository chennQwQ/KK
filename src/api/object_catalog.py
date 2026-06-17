from pathlib import Path

from src.api.schemas import StudioObjectResponse
from src.config import DATA_PATH

SUPPORTED_KNOWLEDGE_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}


def get_studio_objects(data_path: str | Path = DATA_PATH) -> list[StudioObjectResponse]:
    documents = _count_supported_documents(Path(data_path))

    return [
        StudioObjectResponse(
            id="kk-advisor",
            name="KK 投研助手",
            type="已构建对象",
            domain="KK 文档问答",
            status="可测试" if documents else "缺少文档",
            icon="K",
            description="基于当前 data/ 目录中的 KK 相关文档构建的第一个真实 RAG 对象。",
            knowledge_bases=["KK 本地文档"],
            documents=documents,
            chunks="待索引统计",
            updated_at="本地数据",
        )
    ]


def find_studio_object(
    objects: list[StudioObjectResponse],
    object_id: str | None,
) -> StudioObjectResponse | None:
    if object_id is None:
        return None

    return next((item for item in objects if item.id == object_id), None)


def _count_supported_documents(data_path: Path) -> int:
    if not data_path.exists():
        return 0

    return sum(
        1
        for item in data_path.iterdir()
        if item.is_file() and item.suffix.lower() in SUPPORTED_KNOWLEDGE_EXTENSIONS
    )
