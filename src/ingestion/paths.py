"""Prototipos de ingestion.paths; sem implementacao."""
from pathlib import Path


def canonical_source_path(
    file_path: Path,
    project_root: Path,
) -> str:
    """Produzir caminho relativo com /, igual ao prefixo esperado no corpus."""
    raise NotImplementedError('Implementar: canonical_source_path')
