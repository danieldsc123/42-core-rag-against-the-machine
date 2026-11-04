"""Modelos do manifesto e do relatório de indexação."""
from pathlib import Path
from typing import Literal
from pydantic import BaseModel


class IndexManifest(BaseModel):
    """Metadados para detectar índices incompatíveis ou desatualizados."""
    format_version: str
    method: Literal["tfidf", "bm25"]
    max_chunk_size: int
    corpus_root: str
    chunk_count: int
    tokenizer_version: str


class IndexReport(BaseModel):
    """Resumo da indexação e dos arquivos ignorados."""
    indexed_files: int
    chunk_count: int
    skipped_files: list[str]
    elapsed_seconds: float
    index_directory: Path
