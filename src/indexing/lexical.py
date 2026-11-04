"""Sparse TF-IDF/BM25 index with validated, pickle-free snapshots."""
import hashlib
import json
import shutil
import tempfile
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
        if not self.chunks:
            raise ValueError('cannot save an unbuilt index')
        if (manifest.chunk_count != len(self.chunks)
                or manifest.method != self.method
                or manifest.tokenizer_version != TOKENIZER_VERSION
                or manifest.format_version != '1'):
            raise ValueError('manifest does not describe this index')
        directory.mkdir(parents=True, exist_ok=True)
        snapshot = Path(tempfile.mkdtemp(prefix='snapshot-', dir=directory))
        pointer: Path | None = None
        try:
            (snapshot / 'manifest.json').write_text(
                manifest.model_dump_json(), encoding='utf-8'
            )
            with (snapshot / 'chunks.jsonl').open('w', encoding='utf-8') as f:
                for chunk in self.chunks:
                    f.write(chunk.model_dump_json() + '\n')
            (snapshot / 'vocabulary.json').write_text(
                json.dumps(self.vocabulary), encoding='utf-8'
            )
            sparse.save_npz(snapshot / 'matrix.npz', self.matrix)
            np.save(snapshot / 'idf.npy', self.idf, allow_pickle=False)
            hashes = {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in snapshot.iterdir()
            }
            (snapshot / 'checksums.json').write_text(json.dumps(hashes))
            with tempfile.NamedTemporaryFile(
                mode='w', dir=directory, delete=False, prefix='.CURRENT-'
            ) as f:
                pointer = Path(f.name)
                f.write(snapshot.name)
            pointer.replace(directory / 'CURRENT')
            self.manifest = manifest
        except Exception:
            shutil.rmtree(snapshot)
            raise
        finally:
            if pointer is not None:
                pointer.unlink(missing_ok=True)

    @classmethod
    def load(
        cls,
        directory: Path,
    ) -> 'LexicalIndex':
        """Validar e carregar indice construido pelo proprio projeto."""
        name = (directory / 'CURRENT').read_text().strip()
        if not name.startswith('snapshot-') or Path(name).name != name:
            raise ValueError('invalid index snapshot pointer')
        snapshot = directory / name
        files = ['manifest.json', 'chunks.jsonl', 'vocabulary.json',
                 'matrix.npz', 'idf.npy']
        hashes = json.loads((snapshot / 'checksums.json').read_text())
        for name in files:
            digest = hashlib.sha256((snapshot / name).read_bytes()).hexdigest()
            if hashes.get(name) != digest:
                raise ValueError(f'index checksum mismatch: {name}')
        manifest = IndexManifest.model_validate_json(
            (snapshot / 'manifest.json').read_text(encoding='utf-8')
        )
        if (manifest.format_version != '1'
                or manifest.tokenizer_version != TOKENIZER_VERSION):
            raise ValueError('incompatible index; rebuild it')
        index = cls(manifest.method)
        with (snapshot / 'chunks.jsonl').open(encoding='utf-8') as f:
            index.chunks = [Chunk.model_validate_json(line) for line in f]
        vocabulary = json.loads(
            (snapshot / 'vocabulary.json').read_text(encoding='utf-8')
        )
        if (not isinstance(vocabulary, dict)
                or not all(isinstance(t, str) and type(i) is int
                           for t, i in vocabulary.items())
                or set(vocabulary.values()) != set(range(len(vocabulary)))):
            raise ValueError('invalid index vocabulary')
        index.vocabulary = vocabulary
        index.matrix = sparse.load_npz(snapshot / 'matrix.npz').tocsr()
        index.idf = np.load(snapshot / 'idf.npy', allow_pickle=False)
        if (len(index.chunks) != manifest.chunk_count
                or index.matrix.shape != (len(index.chunks), len(vocabulary))
                or index.idf.shape != (len(vocabulary),)
                or not np.isfinite(index.matrix.data).all()
                or not np.isfinite(index.idf).all()
                or (index.matrix.data < 0).any()
                or len({c.chunk_id for c in index.chunks}) != len(index.chunks)):
            raise ValueError('invalid index dimensions or weights')
        for chunk in index.chunks:
            size = (chunk.source.last_character_index
                    - chunk.source.first_character_index)
            if size > 2000 or len(chunk.text) != size:
                raise ValueError('invalid chunk in saved index')
        index.manifest = manifest
        return index
