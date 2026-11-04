"""Check exact source coverage and Markdown section boundaries."""
import pytest

from src.chunking.text import chunk_text
from src.models.documents import Document


@pytest.mark.parametrize('text', [
    '', 'Olá 🙂\r\n\r\nOutro parágrafo.\r\n', '\n\n\n', 'x' * 4001,
])
@pytest.mark.parametrize('limit', [1, 17, 2000])
def test_exact_coverage(text: str, limit: int) -> None:
    """Chunks cover the original once, with stable IDs and bounded sizes."""
    document = Document(file_path='data/raw/sample.md', text=text, kind='text')
    chunks = chunk_text(document, limit)
    assert ''.join(chunk.text for chunk in chunks) == text
    assert chunks == chunk_text(document, limit)
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)
    cursor = 0
    for chunk in chunks:
        assert chunk.source.file_path == document.file_path
        assert chunk.source.first_character_index == cursor
        cursor = chunk.source.last_character_index
        assert 0 < len(chunk.text) <= limit
    assert cursor == len(text)


@pytest.mark.parametrize('heading', ['# Title', '   ### Title', '#',
                                     'Title\n=====', 'Title\n-----'])
def test_heading_starts_section(heading: str) -> None:
    """Recognize titles even without a preceding empty line."""
    text = 'Introduction\n' + heading + '\nBody'
    document = Document(file_path='data/raw/sample.md', text=text, kind='text')
    chunks = chunk_text(document, 2000)
    assert chunks[0].text == 'Introduction\n'
    assert chunks[1].text == heading + '\nBody'


@pytest.mark.parametrize('fence', ['```', '~~~~'])
def test_fenced_code_stays_together(fence: str) -> None:
    """Ignore apparent headings, blank lines and shorter fences in code."""
    block = f'{fence}python\r\n# code\r\n\r\nx = 1\r\n'
    if fence == '~~~~':
        block += '~~~\r\n'
    block += fence + '\r\n'
    document = Document(
        file_path='data/raw/sample.md',
        text='Intro\r\n' + block + '# Real title\r\nBody', kind='text',
    )
    chunks = chunk_text(document, 2000)
    assert [chunk.text for chunk in chunks] == [
        'Intro\r\n', block, '# Real title\r\nBody',
    ]


def test_unclosed_fence_and_literal_hash() -> None:
    """An unclosed fence protects its body; a bare word with # is text."""
    text = '#not-a-title\ntext\n```\n# code\n\nmore'
    document = Document(file_path='data/raw/sample.md', text=text, kind='text')
    chunks = chunk_text(document, 2000)
    assert [chunk.text for chunk in chunks] == [
        '#not-a-title\ntext\n', '```\n# code\n\nmore',
    ]


@pytest.mark.parametrize('limit', [0, -1, 2001])
def test_invalid_limit_on_empty_document(limit: int) -> None:
    """Validate the size even when there are no chunks to build."""
    document = Document(file_path='data/raw/sample.md', text='', kind='text')
    with pytest.raises(ValueError):
        chunk_text(document, limit)
