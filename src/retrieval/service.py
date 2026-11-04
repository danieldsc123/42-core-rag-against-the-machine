"""Retrieval consumes only question IDs and query text, never answers."""
from src.indexing.lexical import LexicalIndex
from src.models.results import MinimalSearchResults
from src.models.questions import RagDataset
from src.models.results import StudentSearchResults
from src.models.questions import UnansweredQuestion


def search_question(
    question: UnansweredQuestion,
    index: LexicalIndex,
    k: int,
) -> MinimalSearchResults:
    """Converter ranking em fontes validas de ate 2000 caracteres."""
    ranked = index.search(question.question, k)
    return MinimalSearchResults(
        question_id=question.question_id, question=question.question,
        retrieved_sources=[item.chunk.source for item in ranked],
    )


def search_dataset(
    dataset: RagDataset,
    index: LexicalIndex,
    k: int,
) -> StudentSearchResults:
    """Usar somente question_id e question, com indice carregado uma vez."""
    raise NotImplementedError('Implementar: search_dataset')
