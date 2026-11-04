"""Prototipos de storage.sources; sem implementacao."""
from pathlib import Path
from src.models.source import MinimalSource


def read_source(
    source: MinimalSource,
    project_root: Path,
) -> str:
    """Conferir caminho e limites e recuperar slice sem alterar o arquivo."""
    raise NotImplementedError('Implementar: read_source')
