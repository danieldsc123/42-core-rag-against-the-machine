"""Sparse TF-IDF/BM25 index with validated, pickle-free snapshots."""
from collections import Counter
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
        if not chunks:
            raise ValueError('cannot build an empty index')
        if len({chunk.chunk_id for chunk in chunks}) != len(chunks):
            raise ValueError('duplicate chunk IDs')
        self.chunks = chunks
        self.vocabulary = {}
        rows: list[int] = []
        columns: list[int] = []
        values: list[float] = []
        for row, chunk in enumerate(chunks):
            path = chunk.source.file_path
            counts = Counter(tokenize(chunk.text) + tokenize(path))
            for token, count in counts.items():
                column = self.vocabulary.setdefault(
                    token, len(self.vocabulary)
                )
                rows.append(row)
                columns.append(column)
                values.append(float(count))
        if not self.vocabulary:
            raise ValueError('corpus contains no searchable terms')
        matrix = sparse.csr_matrix(
            (values, (rows, columns)),
            shape=(len(chunks), len(self.vocabulary)), dtype=np.float64,
        )
        frequencies = np.asarray((matrix > 0).sum(axis=0)).ravel()
        count = len(chunks)
        if self.method == 'bm25':
            self.idf = np.log1p(
                (count - frequencies + 0.5) / (frequencies + 0.5)
            )
            lengths = np.asarray(matrix.sum(axis=1)).ravel()
            normalizer = 1.2 * (0.25 + 0.75 * lengths / lengths.mean())
            matrix = matrix.tocoo()
            matrix.data = (
                self.idf[matrix.col] * matrix.data * 2.2
                / (matrix.data + normalizer[matrix.row])
            )
            self.matrix = matrix.tocsr()
        else:
            self.idf = np.log((1 + count) / (1 + frequencies)) + 1
            matrix.data = 1 + np.log(matrix.data)
            matrix = matrix.multiply(self.idf).tocsr()
            norms = np.sqrt(np.asarray(matrix.power(2).sum(axis=1)).ravel())
            self.matrix = sparse.diags(1 / np.maximum(norms, 1e-12)) @ matrix
        self.matrix.sort_indices()

    def search(
        self,
        query: str,
        k: int,
    ) -> list[RankedChunk]:
        """Ordenar por relevancia com desempate deterministico."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError('query must not be empty')
        if not isinstance(k, int) or isinstance(k, bool) or k < 0:
            raise ValueError('k must be a nonnegative integer')
        if not self.chunks:
            raise ValueError('index has not been built')
        if k == 0:
            return []
        counts = Counter(tokenize(query))
        columns = [self.vocabulary[t] for t in counts
                   if t in self.vocabulary]
        if not columns:
            return []
        weights = np.array([
            counts[t] for t in counts if t in self.vocabulary
        ], dtype=np.float64)
        if self.method == 'tfidf':
            weights = (1 + np.log(weights)) * self.idf[columns]
            weights /= max(float(np.linalg.norm(weights)), 1e-12)
        scores = np.asarray(self.matrix[:, columns] @ weights).ravel()
        candidates = np.flatnonzero(scores > 0)
        ordered = candidates[np.lexsort((candidates, -scores[candidates]))]
        return [RankedChunk(chunk=self.chunks[int(i)], score=float(scores[i]))
                for i in ordered[:k]]

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
