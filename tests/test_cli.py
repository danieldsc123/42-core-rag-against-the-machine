"""Test the public CLI in subprocesses, including failure exit codes."""
import json
from pathlib import Path
import subprocess
import sys

import pytest


def invoke(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the actual module entrypoint without a shell."""
    return subprocess.run([sys.executable, '-m', 'src', *args],
                          capture_output=True, text=True, timeout=30)


def test_end_to_end_search_and_evaluation(tmp_path: Path) -> None:
    """Index files, search both scopes and evaluate output via CLI."""
    raw = tmp_path / 'raw'
    raw.mkdir()
    (raw / 'lora.md').write_text('LoRA adapters load dynamically.\n')
    index = tmp_path / 'index'
    result = invoke('index', '--corpus_path', str(raw), '--project_root',
                    str(tmp_path), '--index_directory', str(index))
    assert result.returncode == 0, result.stderr
    dataset = tmp_path / 'questions.json'
    dataset.write_text(json.dumps({'rag_questions': [{
        'question_id': 'q', 'question': 'LoRA adapters', 'answer': 'Reference',
        'sources': [{'file_path': 'raw/lora.md', 'first_character_index': 0,
                     'last_character_index': 30}],
    }]}))
    out = tmp_path / 'out'
    result = invoke('search_dataset', '--dataset_path', str(dataset), '--k',
                    '5', '--save_directory', str(out), '--index_directory',
                    str(index))
    assert result.returncode == 0, result.stderr
    output = out / dataset.name
    saved = json.loads(output.read_text())
    assert saved['search_results'][0]['question_id'] == 'q'
    assert saved['search_results'][0]['retrieved_sources']
    report = tmp_path / 'report.json'
    result = invoke('evaluate', '--student_search_results_path', str(output),
                    '--dataset_path', str(dataset), '--save_path', str(report))
    assert result.returncode == 0, result.stderr
    assert json.loads(report.read_text())['recall_at_k']['5'] == 1.0
    answer = tmp_path / 'answer.json'
    result = invoke('answer', 'LoRA adapters', '--k', '0', '--index_directory',
                    str(index), '--save_path', str(answer))
    assert result.returncode == 0, result.stderr
    assert json.loads(answer.read_text())['search_results'][0]['answer']
    result = invoke('search', '  ', '--index_directory', str(index))
    assert result.returncode != 0
    assert 'Traceback' not in result.stderr
    result = invoke('search', 'LoRA', '--k', '-1', '--index_directory',
                    str(index))
    assert result.returncode != 0
    assert 'Traceback' not in result.stderr


@pytest.mark.parametrize('args', [
    ['search', 'LoRA', '--index_directory', '/nonexistent/rag-index'],
    ['index', '--max_chunk_size', '2001'],
    ['search_dataset', '--dataset_path', '/nonexistent/questions.json'],
    ['answer_dataset', '--student_search_results_path', '/nonexistent/a.json',
     '--save_directory', '/tmp/rag-unused'],
])
def test_error_messages_without_tracebacks(args: list[str]) -> None:
    """Missing files and invalid arguments fail clearly and nonzero."""
    result = invoke(*args)
    assert result.returncode != 0
    assert 'Error:' in result.stderr and 'Traceback' not in result.stderr
