"""Descoberta de arquivos de código e documentação do corpus."""
from pathlib import Path
from typing import Iterator


def discover_files(
    corpus_root: Path,
) -> Iterator[Path]:
    """Descoberta de arquivos de código e documentação do corpus."""
    if not corpus_root.is_dir():
        raise NotADirectoryError(
            f'corpus_root deve ser um diretorio: {corpus_root}'
        )

    extensions = {".py", ".md", ".rst", ".txt"}

    for file_path in sorted(corpus_root.rglob('*')):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            yield file_path
