"""Prototipos de indexing.lexical; sem implementacao."""
from pathlib import Path
from src.models.documents import Chunk
from src.models.index import IndexManifest
from src.models.documents import RankedChunk

class LexicalIndex:
    """Encapsular ranking e persistencia sem expor bibliotecas ao pipeline."""
    def __init__(self, method: str = "tfidf") -> None:
        """Validar metodo escolhido; nenhum modelo gerativo aqui."""
        ...

    def build(self, chunks: list[Chunk]) -> None:
        """Construir representacao lexical usando tokenize."""
        ...

    def search(self, query: str, k: int) -> list[RankedChunk]:
        """Ordenar por relevancia com desempate deterministico."""
        ...

    def save(self, directory: Path, manifest: IndexManifest) -> None:
        """Persistir chunks, vocabulario, estrutura de busca e manifesto."""
        ...

    @classmethod
    def load(cls, directory: Path) -> "LexicalIndex":
        """Validar e carregar indice construido pelo proprio projeto."""
        ...
