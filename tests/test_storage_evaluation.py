"""Testar limites das fontes, associação de perguntas e gravação atômica."""
from pathlib import Path
from unittest.mock import patch

import pytest

from src.evaluation.metrics import question_recall, span_iou
from src.evaluation.service import evaluate_results
from src.models.questions import AnsweredQuestion, RagDataset
from src.models.results import MinimalSearchResults, StudentSearchResults
from src.models.source import MinimalSource
from src.storage.results import write_results
from src.storage.sources import read_source


def test_source_crlf_and_symlink_escape(tmp_path: Path) -> None:
    """Contar caracteres e manter os caminhos resolvidos dentro da raiz."""
    root = tmp_path / 'project'
    root.mkdir()
    (root / 'sample.txt').write_bytes('á🙂\r\nZ'.encode())
    source = MinimalSource(file_path='sample.txt', first_character_index=1,
                           last_character_index=4)
    assert read_source(source, root) == '🙂\r\n'
    with pytest.raises(ValueError):
        read_source(source.model_copy(update={'last_character_index': 100}),
                    root)
    (tmp_path / 'outside.txt').write_text('secret')
    (root / 'link.txt').symlink_to(tmp_path / 'outside.txt')
    with pytest.raises(ValueError):
        read_source(source.model_copy(update={'file_path': 'link.txt'}), root)


def test_recall_matches_by_id_and_missing_is_zero() -> None:
    """Contar referências sem duplicar os acertos."""
    source = MinimalSource(file_path='raw/a.md', first_character_index=0,
                           last_character_index=10)
    other = source.model_copy(update={'file_path': 'raw/b.md'})
    assert span_iou(source, source) == 1.0
    assert span_iou(source, other) == 0.0
    assert question_recall([source, source], [source, other], 5) == 0.5
    assert question_recall([source], [source], 0) == 0.0
    truth = RagDataset(rag_questions=[
        AnsweredQuestion(question_id=q, question='Why?', answer='Answer',
                         sources=[source]) for q in ['q1', 'q2']
    ])
    result = MinimalSearchResults(question_id='q2', question='Why?',
                                  retrieved_sources=[source])
    report = evaluate_results(StudentSearchResults(search_results=[result],
                                                   k=5), truth)
    assert report.recall_at_k[5] == 0.5
    assert report.missing_question_ids == ['q1']
    with pytest.raises(ValueError, match='duplicate'):
        evaluate_results(StudentSearchResults(search_results=[result, result],
                                              k=5), truth)
    unknown = result.model_copy(update={'question_id': 'unknown'})
    with pytest.raises(ValueError, match='unknown'):
        evaluate_results(StudentSearchResults(search_results=[unknown], k=5),
                         truth)


def test_atomic_write_preserves_previous_output(tmp_path: Path) -> None:
    """Preservar a saída e limpar temporários se a troca falhar."""
    output = tmp_path / 'results.json'
    output.write_text('previous')
    with patch.object(Path, 'replace', side_effect=OSError('disk failure')):
        with pytest.raises(OSError):
            write_results(StudentSearchResults(search_results=[], k=0), output)
    assert output.read_text() == 'previous'
    assert list(tmp_path.iterdir()) == [output]
