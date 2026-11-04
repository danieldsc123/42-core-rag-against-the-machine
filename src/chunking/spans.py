"""Divisão de intervalos e validação de chunks do corpus."""
from src.models.documents import Chunk
from src.models.documents import Document


def split_span(
    text: str,
    start: int,
    end: int,
    max_chunk_size: int,
) -> list[tuple[int, int]]:
    """Subdividir intervalo grande sem perder posições no documento."""

    if not 1 <= max_chunk_size <= 2000:
        raise ValueError('max_chunk_size deve estar entre 1 e 2000')

    if not 0 <= start <= end <= len(text):
        raise ValueError('intervalo fora dos limites do texto')

    spans: list[tuple[int, int]] = []
    position = start
    while position < end:
        next_position = min(position + max_chunk_size, end)
        spans.append((position, next_position))
        position = next_position

    return spans


def validate_chunk(
    chunk: Chunk,
    document: Document,
    max_chunk_size: int,
) -> None:
    """Validar limites, tamanho e igualdade com o recorte original."""

    if not 1 <= max_chunk_size <= 2000:
        raise ValueError('max_chunk_size deve estar entre 1 e 2000')

    if chunk.source.file_path != document.file_path:
        raise ValueError('caminho do chunk diferente do documento')

    start = chunk.source.first_character_index
    end = chunk.source.last_character_index

    if not 0 <= start < end <= len(document.text):
        raise ValueError('intervalo do chunk fora dos limites do documento')

    if end - start > max_chunk_size:
        raise ValueError('tamanho do chunk excede max_chunk_size')

    if chunk.text != document.text[start:end]:
        raise ValueError('texto do chunk diferente do slice original')

    if chunk.kind != document.kind:
        raise ValueError('tipo do chunk diferente do documento')
