"""Prototipos de models.documents; sem implementacao."""
from typing import Literal
from pydantic import BaseModel
from src.models.source import MinimalSource

class Document(BaseModel):
    """Texto original, sem limpeza ou normalizacao de quebras de linha."""
    file_path: str
    text: str
    kind: Literal["python", "text"]


class Chunk(BaseModel):
    """text deve ser exatamente o slice original definido por source."""
    chunk_id: str
    source: MinimalSource
    text: str
    kind: Literal["python", "text"]


class RankedChunk(BaseModel):
    """Pontuacao interna; nao precisa aparecer no JSON externo."""
    chunk: Chunk
    score: float
