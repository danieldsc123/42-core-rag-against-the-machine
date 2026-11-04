"""Leitura dos documentos do corpus."""
from pathlib import Path
from typing import Literal

from src.ingestion.paths import canonical_source_path
from src.models.documents import Document


def read_document(file_path: Path, project_root: Path) -> Document:
    """Ler UTF-8 preservando caracteres e quebras de linha originais."""

    resolved_file = file_path.resolve()
    relative_path = canonical_source_path(resolved_file, project_root)

    with open(resolved_file, "r", encoding="utf-8", newline="") as file:
        content = file.read()

    kind: Literal["python", "text"]
    if file_path.suffix.lower() == ".py":
        kind = "python"
    else:
        kind = "text"

    return Document(text=content, kind=kind, file_path=relative_path)
