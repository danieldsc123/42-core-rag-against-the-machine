"""Prototipos de storage.datasets; sem implementacao."""
from pathlib import Path
from src.models.questions import RagDataset


def load_dataset(
    path: Path,
) -> RagDataset:
    """Validar JSON com Pydantic e preservar gabarito quando presente."""
    raise NotImplementedError('Implementar: load_dataset')
