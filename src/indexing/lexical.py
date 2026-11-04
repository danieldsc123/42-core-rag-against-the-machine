"""Sparse TF-IDF/BM25 index with validated, pickle-free snapshots."""
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse

from src.indexing.tokenizer import tokenize, TOKENIZER_VERSION
from src.models.documents import Chunk
from src.models.index import IndexManifest
from src.models.documents import RankedChunk


class LexicalIndex:
    """Encapsular ranking e persistencia sem expor bibliotecas ao pipeline."""

    def __init__(
        self,
        method: str = 'bm25',
    ) -> None:
        """Validar metodo escolhido; nenhum modelo gerativo aqui."""
        if method not in ('tfidf', 'bm25'):
            raise ValueError('method must be tfidf or bm25')
        self.method = method
        self.chunks: list[Chunk] = []
        self.vocabulary: dict[str, int] = {}
        self.matrix: Any = sparse.csr_matrix((0, 0), dtype=np.float64)
        self.idf: Any = np.array([], dtype=np.float64)
        self.manifest: IndexManifest | None = None

    def build(
        self,
        chunks: list[Chunk],
    ) -> None:
        """Construir representacao lexical usando tokenize."""
        raise NotImplementedError('Implementar: build')

    def search(
        self,
        query: str,
        k: int,
    ) -> list[RankedChunk]:
        """Ordenar por relevancia com desempate deterministico."""
        raise NotImplementedError('Implementar: search')

    def save(
        self,
        directory: Path,
        manifest: IndexManifest,
    ) -> None:
        """Persistir chunks, vocabulario, estrutura de busca e manifesto."""
        raise NotImplementedError('Implementar: save')

    @classmethod
    def load(
        cls,
        directory: Path,
    ) -> 'LexicalIndex':
        """Validar e carregar indice construido pelo proprio projeto."""
        raise NotImplementedError('Implementar: load')
