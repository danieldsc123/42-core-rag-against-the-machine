"""Prototipos de generation.pipeline; sem implementacao."""
from src.generation.model import LocalGenerator
from src.models.results import MinimalAnswer
from src.models.results import MinimalSearchResults
from src.models.results import StudentSearchResults
from src.models.results import StudentSearchResultsAndAnswer


def answer_search_result(
    result: MinimalSearchResults,
    generator: LocalGenerator,
    project_root: str,
) -> MinimalAnswer:
    """Ler os slices recuperados e gerar resposta fundamentada."""
    raise NotImplementedError('Implementar: answer_search_result')


def answer_dataset(
    results: StudentSearchResults,
    generator: LocalGenerator,
    project_root: str,
) -> StudentSearchResultsAndAnswer:
    """Reutilizar gerador e mostrar progresso, preservando IDs e k."""
    raise NotImplementedError('Implementar: answer_dataset')
