"""Prototipos de chunking.spans; sem implementacao."""
from src.models.documents import Chunk
from src.models.documents import Document

def split_span(text: str, start: int, end: int, max_chunk_size: int) -> list[tuple[int, int]]:
    """Subdividir intervalo grande sem perder posicoes no documento."""
    ...


def validate_chunk(chunk: Chunk, document: Document, max_chunk_size: int) -> None:
    """Validar limites, tamanho e igualdade com o slice original."""
    ...
