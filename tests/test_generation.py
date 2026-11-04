"""Exercise prompt budgets and abstention without downloading a model."""
import json
from typing import Any

import pytest

from src.generation.model import LocalGenerator
from src.generation.pipeline import answer_dataset
from src.models.documents import Chunk
from src.models.generation import GenerationConfig
from src.models.results import MinimalSearchResults, StudentSearchResults
from src.models.source import MinimalSource


class CharacterTokenizer:
    """Deterministic stand-in so budget boundary cases are reproducible."""

    def encode(self, text: str, **kwargs: Any) -> list[int]:
        """Count a character as one token in these isolated tests."""
        return list(range(len(text)))

    def apply_chat_template(self, messages: list[dict[str, str]],
                            **kwargs: Any) -> str:
        """Include system and user messages plus generation overhead."""
        assert kwargs['enable_thinking'] is False
        return json.dumps(messages, ensure_ascii=False) + '<assistant>'


def test_context_budget_and_selected_sources() -> None:
    """Skip large evidence and retain fitting sources within the budget."""
    generator = LocalGenerator(GenerationConfig(
        context_window_tokens=1300, max_new_tokens=100,
    ))
    generator.model = object()
    generator.tokenizer = CharacterTokenizer()
    chunks = []
    for i, text in enumerate(['A' * 1800, 'LoRA adapter endpoint']):
        chunks.append(Chunk(
            chunk_id=str(i), text=text, kind='text',
            source=MinimalSource(file_path=f'raw/{i}.md',
                                 first_character_index=0,
                                 last_character_index=len(text)),
        ))
    prompt = generator.prepare_prompt('What endpoint?', chunks + chunks)
    assert prompt.sources == [chunks[1].source]
    assert prompt.input_tokens + 100 <= 1300
    assert 'LoRA adapter endpoint' in prompt.text
    assert 'A' * 1800 not in prompt.text
    with pytest.raises(ValueError, match='budget'):
        generator.prepare_prompt('x' * 2000, [])
    with pytest.raises(ValueError):
        generator.prepare_prompt(' ', chunks)
    generator.close()
    assert generator.model is None and generator.tokenizer is None


def test_empty_results_abstain_without_loading_model() -> None:
    """Empty batches and k=0 preserve IDs and require no model download."""
    generator = LocalGenerator(GenerationConfig())
    results = StudentSearchResults(search_results=[MinimalSearchResults(
        question_id='q1', question='Why?', retrieved_sources=[],
    )], k=0)
    answers = answer_dataset(results, generator, '.')
    assert answers.k == 0
    assert answers.search_results[0].question_id == 'q1'
    assert answers.search_results[0].retrieved_sources == []
    assert 'not contain enough information' in answers.search_results[0].answer
    assert generator.model is None
    empty = answer_dataset(StudentSearchResults(search_results=[], k=5),
                           generator, '.')
    assert empty.search_results == [] and empty.k == 5
