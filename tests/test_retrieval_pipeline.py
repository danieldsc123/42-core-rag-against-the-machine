"""Testar ranking esparso, persistência e fluxo real baseado em arquivos."""
from pathlib import Path

import pytest

from src.indexing.lexical import LexicalIndex
from src.indexing.pipeline import build_index
from src.models.questions import (
    AnsweredQuestion, RagDataset, UnansweredQuestion,
)
from src.retrieval.service import search_dataset
from src.storage.datasets import load_dataset
from src.storage.results import load_search_results, write_results


@pytest.mark.parametrize('method', ['tfidf', 'bm25'])
def test_index_roundtrip_and_ground_truth_isolation(
    tmp_path: Path, method: str,
) -> None:
    """Reproduzir rankings após recarga sem usar respostas de referência."""
    corpus = tmp_path / 'raw'
    corpus.mkdir()
    (corpus / 'lora.md').write_text('LoRA adapters load dynamically.\n')
    (corpus / 'quant.py').write_text('def quantize_model():\n    pass\n')
    report = build_index(
        corpus, tmp_path / 'index', tmp_path, method=method
    )
    assert report.indexed_files == 2
    assert not report.skipped_files
    index = LexicalIndex.load(tmp_path / 'index')
    ranking = index.search('LoRA adapters', 10)
    assert ranking[0].chunk.source.file_path == 'raw/lora.md'
    assert index.search('unknownzzzz', 10) == []
    assert index.search('LoRA', 0) == []
    assert index.search('LoRA', 100) == index.search('LoRA', 100)
    with pytest.raises(ValueError):
        index.search(' ', 1)
    with pytest.raises(ValueError):
        index.search('LoRA', -1)
    dataset = RagDataset(rag_questions=[
        UnansweredQuestion(question_id='q1', question='LoRA adapters'),
    ])
    answered = RagDataset(rag_questions=[AnsweredQuestion(
        question_id='q1', question='LoRA adapters', answer='secret quantize',
        sources=[ranking[0].chunk.source],
    )])
    plain = search_dataset(dataset, index, 5)
    assert search_dataset(answered, index, 5) == plain
    output = tmp_path / 'output' / 'results.json'
    write_results(plain, output)
    assert load_search_results(output) == plain
    dataset_path = tmp_path / 'questions.json'
    dataset_path.write_text(answered.model_dump_json())
    assert load_dataset(dataset_path) == answered
    saved = tmp_path / 'index' / (tmp_path / 'index/CURRENT').read_text()
    (saved / 'vocabulary.json').write_text('{}')
    with pytest.raises(ValueError, match='checksum'):
        LexicalIndex.load(tmp_path / 'index')


def test_empty_and_unreadable_corpus(tmp_path: Path) -> None:
    """Rejeitar a indexação de um corpus inteiramente inutilizável."""
    with pytest.raises(ValueError, match='empty index'):
        build_index(tmp_path, tmp_path / 'index', tmp_path)
    (tmp_path / 'bad.txt').write_bytes(b'\xff')
    with pytest.raises(ValueError, match='empty index'):
        build_index(tmp_path, tmp_path / 'index', tmp_path)
