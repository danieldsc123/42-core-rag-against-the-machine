"""Prototipos de indexing.pipeline; sem implementacao."""
from pathlib import Path
from src.models.index import IndexReport

def build_index(corpus_root: Path, index_directory: Path, project_root: Path, max_chunk_size: int = 2000, method: str = "tfidf") -> IndexReport:
    """Processar corpus com tqdm e medir tempo total; limite de 5 minutos."""
    ...
