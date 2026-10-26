"""Prototipos de chunking.text; sem implementacao."""
from src.models.documents import Chunk
from src.models.documents import Document

def chunk_text(document: Document, max_chunk_size: int) -> list[Chunk]:
    """Usar headings/paragrafos e fallback para secoes grandes."""
    ...
