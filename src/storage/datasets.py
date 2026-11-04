"""Validated public dataset loading; answers are never retrieval content."""
from pathlib import Path

from src.models.questions import RagDataset


def load_dataset(path: Path) -> RagDataset:
    """Read UTF-8 JSON and preserve answered-question fields."""
    return RagDataset.model_validate_json(path.read_text(encoding='utf-8'))
