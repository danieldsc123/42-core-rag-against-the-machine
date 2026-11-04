"""Carregar datasets validados sem usar gabaritos como conteúdo de busca."""
from pathlib import Path

from src.models.questions import RagDataset


def load_dataset(path: Path) -> RagDataset:
    """Ler JSON UTF-8 preservando os campos das perguntas com gabarito."""
    return RagDataset.model_validate_json(path.read_text(encoding='utf-8'))
