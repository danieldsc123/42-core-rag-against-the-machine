"""Coordinate corpus reading, distinct chunkers and sparse indexing."""
from pathlib import Path
from time import perf_counter
from typing import Literal, cast

from tqdm import tqdm

from src.chunking.python import chunk_python
from src.chunking.text import chunk_text
from src.indexing.lexical import LexicalIndex
from src.indexing.tokenizer import TOKENIZER_VERSION
from src.ingestion.discovery import discover_files
from src.ingestion.reader import read_document
from src.models.documents import Chunk
from src.models.index import IndexManifest, IndexReport
from src.models.source import MinimalSource


def build_index(
    corpus_root: Path,
    index_directory: Path,
    project_root: Path,
    max_chunk_size: int = 2000,
    method: str = 'bm25',
) -> IndexReport:
    """Build an index with progress, reporting unreadable files and timing.

    Pack adjacent structural chunks to avoid indexing one-line statements
    as isolated evidence; source offsets still refer to the original text.
    """
    started = perf_counter()
    if not 1 <= max_chunk_size <= 2000:
        raise ValueError('max_chunk_size must be between 1 and 2000')
    index = LexicalIndex(method)
    files = list(discover_files(corpus_root))
    skipped: list[str] = []
    chunks: list[Chunk] = []
    indexed_files = 0
    for path in tqdm(files, desc='Indexing', unit='file'):
        try:
            document = read_document(path, project_root)
        except (OSError, UnicodeError, ValueError) as exc:
            skipped.append(f'{path}: {exc}')
            continue
        chunker = chunk_python if document.kind == 'python' else chunk_text
        structural = chunker(document, max_chunk_size)
        start = 0
        end = 0
        packed: list[tuple[int, int]] = []
        for chunk in structural:
            next_end = chunk.source.last_character_index
            if next_end - start > max_chunk_size:
                packed.append((start, end))
                start = end
            end = next_end
        if end > start:
            packed.append((start, end))
        for start, end in packed:
            text = document.text[start:end]
            if not text.strip():
                continue
            chunks.append(Chunk(
                chunk_id=f'{document.file_path}:{start}:{end}',
                source=MinimalSource(
                    file_path=document.file_path,
                    first_character_index=start, last_character_index=end,
                ), text=text, kind=document.kind,
            ))
        indexed_files += 1
    index.build(chunks)
    manifest = IndexManifest(
        format_version='1', method=cast(Literal['tfidf', 'bm25'], method),
        max_chunk_size=max_chunk_size,
        corpus_root=str(corpus_root.resolve()), chunk_count=len(chunks),
        tokenizer_version=TOKENIZER_VERSION,
    )
    index.save(index_directory, manifest)
    return IndexReport(
        indexed_files=indexed_files, chunk_count=len(chunks),
        skipped_files=skipped, elapsed_seconds=perf_counter() - started,
        index_directory=index_directory,
    )
