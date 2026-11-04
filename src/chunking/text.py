"""Chunking de texto por parágrafos, títulos e blocos de código."""
import re

from src.chunking.spans import split_span, validate_chunk
from src.models.documents import Chunk, Document
from src.models.source import MinimalSource


def chunk_text(
    document: Document,
    max_chunk_size: int,
) -> list[Chunk]:
    """Preservar offsets e subdividir blocos que excedam o limite.

    Títulos ATX (#) e Setext definem seções. Cercas Markdown protegem
    títulos e linhas vazias internos contra cortes, salvo por tamanho.
    """

    if not 1 <= max_chunk_size <= 2000:
        raise ValueError('max_chunk_size deve estar entre 1 e 2000')

    text = document.text
    boundaries = {0, len(text)}
    offset = 0
    previous_start = 0
    previous_content = False
    fence_character = ''
    fence_length = 0

    for line in text.splitlines(keepends=True):
        body = line.rstrip('\r\n')
        if fence_character:
            closing = re.fullmatch(r' {0,3}(`{3,}|~{3,})[ \t]*', body)
            if (closing and closing[1][0] == fence_character
                    and len(closing[1]) >= fence_length):
                fence_character = ''
                boundaries.add(offset + len(line))
            previous_content = False
        else:
            opening = re.fullmatch(r' {0,3}(`{3,}|~{3,})(.*)', body)
            if opening and not (
                opening[1][0] == '`' and '`' in opening[2]
            ):
                boundaries.add(offset)
                fence_character = opening[1][0]
                fence_length = len(opening[1])
                previous_content = False
            else:
                if re.match(r'^ {0,3}#{1,6}(?:[ \t]+|$)', body):
                    boundaries.add(offset)
                elif (previous_content
                      and re.fullmatch(r' {0,3}(?:=+|-+)[ \t]*', body)):
                    boundaries.add(previous_start)
                if not body.strip(' \t'):
                    boundaries.add(offset + len(line))
                previous_content = bool(body.strip(' \t'))
        previous_start = offset
        offset += len(line)

    ordered_boundaries = sorted(boundaries)

    chunks: list[Chunk] = []

    for start, end in zip(ordered_boundaries, ordered_boundaries[1:]):
        for chunk_start, chunk_end in split_span(
            text, start, end, max_chunk_size
        ):
            source = MinimalSource(
                file_path=document.file_path,
                first_character_index=chunk_start,
                last_character_index=chunk_end,
            )
            chunk = Chunk(
                chunk_id=(
                    f'{document.file_path}:{chunk_start}:{chunk_end}'
                ),
                source=source,
                text=text[chunk_start:chunk_end],
                kind=document.kind,
            )
            validate_chunk(chunk, document, max_chunk_size)
            chunks.append(chunk)

    return chunks
