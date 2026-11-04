"""Validated search-result loading and atomic JSON output."""
from pathlib import Path
from src.models.results import StudentSearchResults
from src.models.results import StudentSearchResultsAndAnswer


def load_search_results(
    path: Path,
) -> StudentSearchResults:
    """Validar resultados antes de gerar respostas ou avaliar."""
    return StudentSearchResults.model_validate_json(
        path.read_text(encoding='utf-8')
    )


def write_results(
    results: StudentSearchResults | StudentSearchResultsAndAnswer,
    output_path: Path,
) -> Path:
    """Criar diretorio e gravar JSON validado sem deixar arquivo parcial."""
    raise NotImplementedError('Implementar: write_results')
