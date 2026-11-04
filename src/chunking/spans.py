"""Divisão de intervalos; validação de chunks ainda pendente."""
from src.models.documents import Chunk
from src.models.documents import Document


def split_span(
    text: str,
    start: int,
    end: int,
    max_chunk_size: int,
) -> list[tuple[int, int]]:
    """Subdividir intervalo grande sem perder posicoes no documento."""

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
    """Validar limites, tamanho e igualdade com o slice original."""
    raise NotImplementedError('Implementar: validate_chunk')
