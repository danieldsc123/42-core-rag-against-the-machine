"""Prototipos de ingestion.reader; sem implementacao."""
from pathlib import Path
from src.models.documents import Document

def read_document(file_path: Path, project_root: Path) -> Document:
    """Ler UTF-8 preservando caracteres e quebras de linha originais."""
    ...
