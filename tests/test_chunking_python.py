"""Check syntax boundaries and exact character coverage for Python."""
import pytest

from src.chunking.python import chunk_python
from src.models.documents import Document


@pytest.mark.parametrize('text', [
    '', '# only a comment\n', 'import os\nVALUE = 1\n',
    '@decorate\nasync def café():\n    return "🙂"\n',
    'def broken(:\r\n    "á🙂"\r\n', 'x = "nul\x00"',
    'TEXT = "' + 'á🙂' * 2000 + '"\r\n',
    'class Example:\n    def method(self):\n        return 1\n',
    'text = "á\u2028🙂"\n\ndef example():\n    pass\n',
])
@pytest.mark.parametrize('limit', [1, 31, 2000])
def test_exact_coverage(text: str, limit: int) -> None:
    """Preserve all characters, including comments, CRLF and invalid code."""
    document = Document(file_path='data/raw/example.py', text=text,
                        kind='python')
    chunks = chunk_python(document, limit)
    assert ''.join(chunk.text for chunk in chunks) == text
    assert chunks == chunk_python(document, limit)
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)
    cursor = 0
    for chunk in chunks:
        assert chunk.kind == 'python'
        assert chunk.source.file_path == document.file_path
        assert chunk.source.first_character_index == cursor
        cursor = chunk.source.last_character_index
        assert chunk.text == text[chunk.source.first_character_index:cursor]
        assert 0 < len(chunk.text) <= limit
    assert cursor == len(text)


def test_decorators_and_unicode_line_offsets() -> None:
    """Attach all decorators and use character offsets after Unicode."""
    prefix = 'label = "á🙂"\r\n\r\n'
    definition = '@first\r\n@second(1)\r\nasync def café():\r\n    pass\r\n'
    document = Document(file_path='data/raw/example.py',
                        text=prefix + definition, kind='python')
    chunks = chunk_python(document, 2000)
    assert chunks[-1].text == definition
    assert chunks[-1].source.first_character_index == len(prefix)


def test_small_class_whole_and_large_class_split_at_methods() -> None:
    """Inspect methods when the enclosing class exceeds the size limit."""
    first = '    def first(self):\n        return 1\n'
    second = '    def second(self):\n        return 2\n'
    text = 'class Example:\n' + first + second
    document = Document(file_path='data/raw/example.py', text=text,
                        kind='python')
    assert [c.text for c in chunk_python(document, 2000)] == [text]
    assert [c.text for c in chunk_python(document, 50)] == [
        'class Example:\n', first, second,
    ]


@pytest.mark.parametrize('limit', [0, -1, 2001])
def test_invalid_limit(limit: int) -> None:
    """Reject invalid size even for an empty Python file."""
    document = Document(file_path='data/raw/example.py', text='',
                        kind='python')
    with pytest.raises(ValueError):
        chunk_python(document, limit)
