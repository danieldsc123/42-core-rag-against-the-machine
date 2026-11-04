"""Answer previously retrieved evidence with a reusable local generator."""
from pathlib import Path

from tqdm import tqdm

from src.generation.model import LocalGenerator
from src.models.documents import Chunk
from src.storage.sources import read_source
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
    context: list[Chunk] = []
    for source in result.retrieved_sources:
        text = read_source(source, Path(project_root))
        context.append(Chunk(
            chunk_id=(f'{source.file_path}:{source.first_character_index}:'
                      f'{source.last_character_index}'),
            source=source, text=text,
            kind='python' if source.file_path.endswith('.py') else 'text',
        ))
    if context:
        prompt = generator.prepare_prompt(result.question, context)
        answer = generator.generate(prompt)
        sources = prompt.sources
    else:
        answer = 'The supplied sources do not contain enough information.'
        sources = []
    return MinimalAnswer(
        question_id=result.question_id, question=result.question,
        retrieved_sources=sources, answer=answer,
    )


def answer_dataset(
    results: StudentSearchResults,
    generator: LocalGenerator,
    project_root: str,
) -> StudentSearchResultsAndAnswer:
    """Reutilizar gerador e mostrar progresso, preservando IDs e k."""
    answers = [
        answer_search_result(result, generator, project_root)
        for result in tqdm(results.search_results, desc='Answering',
                           unit='question')
    ]
    return StudentSearchResultsAndAnswer(search_results=answers, k=results.k)
