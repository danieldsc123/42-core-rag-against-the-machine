"""Chunking de Python por blocos sintáticos, preservando o texto original."""
import ast
import re

from src.chunking.spans import split_span, validate_chunk
from src.chunking.text import chunk_text
from src.models.documents import Chunk, Document
from src.models.source import MinimalSource


def chunk_python(
    document: Document,
    max_chunk_size: int,
) -> list[Chunk]:
    """Separar blocos do módulo e subdividir definições grandes.

    Usar posições de linhas, não colunas AST em bytes, para preservar offsets
    Unicode. Decoradores pertencem à definição. Código inválido usa o
    chunking textual, mantendo o tipo e os offsets do documento original.
    """
    if not 1 <= max_chunk_size <= 2000:
        raise ValueError('max_chunk_size deve estar entre 1 e 2000')

    text = document.text
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError, RecursionError):
        return chunk_text(document, max_chunk_size)

    line_offsets = [0]
    for newline in re.finditer(r'\r\n|\r|\n', text):
        line_offsets.append(newline.end())
    if line_offsets[-1] != len(text):
        line_offsets.append(len(text))
    boundaries = {0, len(text)}

    def collect_boundaries(node: ast.AST) -> None:
        """Keep small definitions whole and inspect children of large ones."""
        if isinstance(node, ast.stmt):
            first_line = node.lineno
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                first_line = min(
                    [first_line] + [d.lineno for d in node.decorator_list]
                )
            start = line_offsets[first_line - 1]
            end = line_offsets[node.end_lineno or node.lineno]
            boundaries.update((start, end))
            if end - start <= max_chunk_size:
                return
        for child in ast.iter_child_nodes(node):
            collect_boundaries(child)

    for node in tree.body:
        collect_boundaries(node)

    ordered = sorted(boundaries)
    chunks: list[Chunk] = []
    for start, end in zip(ordered, ordered[1:]):
        for chunk_start, chunk_end in split_span(
            text, start, end, max_chunk_size
        ):
            chunk = Chunk(
                chunk_id=f'{document.file_path}:{chunk_start}:{chunk_end}',
                source=MinimalSource(
                    file_path=document.file_path,
                    first_character_index=chunk_start,
                    last_character_index=chunk_end,
                ),
                text=text[chunk_start:chunk_end],
                kind=document.kind,
            )
            validate_chunk(chunk, document, max_chunk_size)
            chunks.append(chunk)
    return chunks
