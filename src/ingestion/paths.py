"""Conversão dos caminhos do corpus para caminhos relativos."""
from pathlib import Path


def canonical_source_path(
    file_path: Path,
    project_root: Path,
) -> str:
    """Conversão dos caminhos do corpus para caminhos relativos."""

    resolved_file = file_path.resolve()
    resolved_root = project_root.resolve()

    return resolved_file.relative_to(resolved_root).as_posix()
