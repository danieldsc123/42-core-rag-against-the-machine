"""Validated search-result loading and atomic JSON output."""
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from pydantic import BaseModel
from src.models.results import StudentSearchResults


def load_search_results(
    path: Path,
) -> StudentSearchResults:
    """Validar resultados antes de gerar respostas ou avaliar."""
    return StudentSearchResults.model_validate_json(
        path.read_text(encoding='utf-8')
    )


def write_results(
    results: BaseModel,
    output_path: Path,
) -> Path:
    """Criar diretorio e gravar JSON validado sem deixar arquivo parcial."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with NamedTemporaryFile(
            mode='w', encoding='utf-8', dir=output_path.parent,
            prefix='.' + output_path.name, suffix='.tmp', delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(results.model_dump_json(indent=2))
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(output_path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return output_path
