"""Read validated source slices without altering original text."""
from pathlib import Path

from src.ingestion.paths import canonical_source_path
from src.models.source import MinimalSource


def read_source(source: MinimalSource, project_root: Path) -> str:
    """Reject path escapes and invalid character ranges before slicing."""
    source = MinimalSource.model_validate(source.model_dump())
    root = project_root.resolve()
    target = (root / source.file_path).resolve()
    canonical_source_path(target, root)
    with target.open(encoding='utf-8', newline='') as stream:
        text = stream.read()
    start = source.first_character_index
    end = source.last_character_index
    if not 0 <= start < end <= len(text):
        raise ValueError(f'source range outside file: {source.file_path}')
    if end - start > 2000:
        raise ValueError('retrieved source exceeds 2000 characters')
    return text[start:end]
