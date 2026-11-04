"""Verificar preservação exata do texto e limites das fontes."""
from pathlib import Path

import pytest

from src.ingestion.reader import read_document


@pytest.mark.parametrize("name,kind", [("example.PY", "python"),
                                       ("notes.md", "text")])
def test_read_document(tmp_path: Path, name: str, kind: str) -> None:
    """Preservar Unicode e CRLF ao produzir um caminho relativo da fonte."""
    path = tmp_path / name
    path.write_bytes("# Olá\r\nTexto\r\n".encode("utf-8"))
    document = read_document(path, tmp_path)
    assert document.text == "# Olá\r\nTexto\r\n"
    assert document.file_path == name
    assert document.kind == kind


def test_reject_file_outside_root(tmp_path: Path) -> None:
    """Rejeitar caminhos fora do projeto antes de ler seu conteúdo."""
    root = tmp_path / "project"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    with pytest.raises(ValueError):
        read_document(outside, root)
