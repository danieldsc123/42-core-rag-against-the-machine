"""Verificar contratos do avaliador e casos extremos de validação."""
import json
from uuid import UUID

import pytest
from pydantic import ValidationError

from src.models.generation import GenerationConfig
from src.models.questions import (
    AnsweredQuestion, RagDataset, UnansweredQuestion,
)
from src.models.results import MinimalSearchResults, StudentSearchResults
from src.models.source import MinimalSource


def source(start: int = 0, end: int = 12) -> MinimalSource:
    """Criar uma fonte representativa do corpus."""
    return MinimalSource(
        file_path="data/raw/vllm-0.10.1/docs/features/lora.md",
        first_character_index=start,
        last_character_index=end,
    )


def test_question_uuid_and_reference_fields() -> None:
    """Gerar IDs independentes e preservar respostas nas uniões do dataset."""
    first = UnansweredQuestion(question="What is LoRA?")
    second = UnansweredQuestion(question="What is LoRA?")
    assert UUID(first.question_id)
    assert first.question_id != second.question_id
    dataset = RagDataset.model_validate({"rag_questions": [{
        "question_id": "q1", "question": "What is LoRA?",
        "answer": "An adapter method.", "sources": [source().model_dump()],
        "difficulty": "easy", "is_valid": True,
    }]})
    assert isinstance(dataset.rag_questions[0], AnsweredQuestion)
    assert dataset.rag_questions[0].answer == "An adapter method."


@pytest.mark.parametrize("fields", [
    {"answer": "incomplete"}, {"sources": []},
    {"answer": "invalid", "sources": [{"file_path": "missing offsets"}]},
])
def test_malformed_reference_cannot_become_unanswered(
    fields: dict[str, object],
) -> None:
    """Impedir que a união descarte silenciosamente gabaritos inválidos."""
    with pytest.raises(ValidationError):
        RagDataset.model_validate({
            "rag_questions": [{"question": "Why?", **fields}]
        })


def test_duplicate_ids_are_rejected() -> None:
    """Exigir identificadores únicos para associar perguntas pelo ID."""
    with pytest.raises(ValidationError):
        RagDataset(rag_questions=[
            UnansweredQuestion(question_id="same", question="First?"),
            UnansweredQuestion(question_id="same", question="Second?"),
        ])


@pytest.mark.parametrize("path", [
    "/etc/passwd", "../secret", "a/../../b", "C:/file", "a\\b", "",
])
def test_non_corpus_paths_are_rejected(path: str) -> None:
    """Exigir caminhos relativos portáveis antes do acesso aos arquivos."""
    with pytest.raises(ValidationError):
        MinimalSource(
            file_path=path, first_character_index=0, last_character_index=1
        )


@pytest.mark.parametrize("start,end", [(-1, 2), (2, 2), (3, 1)])
def test_invalid_ranges_are_rejected(start: int, end: int) -> None:
    """Exigir que a fonte descreva um intervalo crescente e não vazio."""
    with pytest.raises(ValidationError):
        source(start, end)


def test_reference_spans_may_exceed_retrieval_limit() -> None:
    """Permitir gabaritos maiores que o limite de 2000 caracteres da busca."""
    reference = source(end=3000)
    with pytest.raises(ValidationError):
        MinimalSearchResults(
            question_id="q", question="Why?", retrieved_sources=[reference]
        )
    result = MinimalSearchResults(
        question_id="q", question="Why?",
        retrieved_sources=[source(end=2000)],
    )
    payload = StudentSearchResults(search_results=[result], k=5)
    assert json.loads(payload.model_dump_json())["k"] == 5
    with pytest.raises(ValidationError):
        StudentSearchResults(search_results=[], k=-1)
    assert StudentSearchResults(search_results=[], k=0).search_results == []


def test_invalid_generation_budget_is_rejected() -> None:
    """Impedir que os tokens da saída ocupem toda a janela de contexto."""
    assert GenerationConfig().model_name == "Qwen/Qwen3-0.6B"
    with pytest.raises(ValidationError):
        GenerationConfig(context_window_tokens=512, max_new_tokens=512)
