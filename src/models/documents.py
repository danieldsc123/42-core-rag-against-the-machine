"""Modelos de documentos, trechos e resultados classificados."""
from typing import Literal
from pydantic import BaseModel
from src.models.source import MinimalSource


class Document(BaseModel):
    """Texto original, sem limpeza ou normalização de quebras de linha."""
    file_path: str
    text: str
    kind: Literal["python", "text"]


class Chunk(BaseModel):
    """Exigir que text corresponda ao recorte original definido por source."""
    chunk_id: str
    source: MinimalSource
    text: str
    kind: Literal["python", "text"]


class RankedChunk(BaseModel):
    """Pontuação interna; não precisa aparecer no JSON externo."""
    chunk: Chunk
    score: float
