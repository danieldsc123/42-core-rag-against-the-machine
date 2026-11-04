"""Verify interval boundaries and defensive chunk validation."""
import pytest

from src.chunking.spans import split_span, validate_chunk
from src.models.documents import Chunk, Document
from src.models.source import MinimalSource


def test_split_span_offsets() -> None:
    """Keep nonzero offsets, a shorter last block and empty intervals."""
    assert split_span('0123456789', 2, 9, 3) == [(2, 5), (5, 8), (8, 9)]
    assert split_span('', 0, 0, 2000) == []


@pytest.mark.parametrize('start,end,limit', [
    (-1, 2, 1), (2, 1, 1), (0, 4, 1), (0, 3, 0), (0, 3, 2001),
])
def test_invalid_span(start: int, end: int, limit: int) -> None:
    """Reject bad ranges and chunk sizes."""
    with pytest.raises(ValueError):
        split_span('abc', start, end, limit)


@pytest.mark.parametrize('error', [
    'none', 'path', 'empty', 'outside', 'size', 'text', 'kind', 'limit',
])
def test_validate_chunk(error: str) -> None:
    """Check valid slices and each failure independently of Pydantic."""
    document = Document(file_path='data/raw/example.py', text='á🙂bc',
                        kind='python')
    source = MinimalSource(file_path=document.file_path,
                           first_character_index=0, last_character_index=2)
    chunk = Chunk(chunk_id='example', source=source, text='á🙂', kind='python')
    limit = 2
    if error == 'path':
        chunk.source = source.model_copy(update={'file_path': 'other.py'})
    elif error == 'empty':
        chunk.source = source.model_copy(update={'last_character_index': 0})
    elif error == 'outside':
        chunk.source = source.model_copy(update={'last_character_index': 5})
    elif error == 'size':
        limit = 1
    elif error == 'text':
        chunk.text = 'changed'
    elif error == 'kind':
        chunk.kind = 'text'
    elif error == 'limit':
        limit = 0
    if error == 'none':
        validate_chunk(chunk, document, limit)
    else:
        with pytest.raises(ValueError):
            validate_chunk(chunk, document, limit)
