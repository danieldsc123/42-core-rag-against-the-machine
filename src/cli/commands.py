"""Python Fire commands coordinating the local RAG pipeline."""
from pathlib import Path

from src.evaluation.service import evaluate_results
from src.generation.model import LocalGenerator
from src.generation.pipeline import answer_dataset, answer_search_result
from src.indexing.lexical import LexicalIndex
from src.indexing.pipeline import build_index
from src.models.generation import GenerationConfig
from src.models.questions import UnansweredQuestion
from src.models.results import StudentSearchResults
from src.retrieval.service import search_dataset, search_question
from src.storage.datasets import load_dataset
from src.storage.paths import dataset_output_path
from src.storage.results import load_search_results, write_results


class RagCLI:
    """Coordenar servicos e transformar erros esperados em mensagens claras."""

    def index(
        self,
        max_chunk_size: int = 2000,
        corpus_path: str = 'data/raw',
        index_directory: str = 'data/processed',
        project_root: str = '.',
        method: str = 'bm25',
    ) -> None:
        """Construir indice e exibir resumo."""
        root = Path(project_root)
        corpus = Path(corpus_path)
        if not corpus.is_absolute():
            corpus = root / corpus
        report = build_index(
            corpus, Path(index_directory), root, max_chunk_size, method
        )
        print(report.model_dump_json(indent=2))

    def search(
        self,
        query: str,
        k: int = 10,
        index_directory: str = 'data/processed',
        save_path: str = 'data/output/search_results/single.json',
    ) -> Path:
        """Buscar uma pergunta e salvar StudentSearchResults."""
        index = LexicalIndex.load(Path(index_directory))
        result = search_question(UnansweredQuestion(question=query), index, k)
        return write_results(
            StudentSearchResults(search_results=[result], k=k), Path(save_path)
        )

    def search_dataset(
        self,
        dataset_path: str,
        k: int = 10,
        save_directory: str = 'data/output/search_results/UnansweredQuestions',
        index_directory: str = 'data/processed',
    ) -> Path:
        """Buscar dataset e salvar JSON com nome de entrada."""
        path = Path(dataset_path)
        dataset = load_dataset(path)
        index = LexicalIndex.load(Path(index_directory))
        results = search_dataset(dataset, index, k)
        output = dataset_output_path(path, Path(save_directory))
        return write_results(results, output)

    def answer(
        self,
        query: str,
        k: int = 10,
        index_directory: str = 'data/processed',
        project_root: str = '.',
        model_name: str = 'Qwen/Qwen3-0.6B',
        context_window_tokens: int = 8192,
        max_new_tokens: int = 512,
        device: str = 'cpu',
        save_path: str = 'data/output/search_results_and_answer/single.json',
    ) -> Path:
        """Buscar, preparar contexto, gerar e salvar resposta unica."""
        raise NotImplementedError('Implementar: answer')

    def answer_dataset(
        self,
        student_search_results_path: str,
        save_directory: str,
        project_root: str = '.',
        model_name: str = 'Qwen/Qwen3-0.6B',
        context_window_tokens: int = 8192,
        max_new_tokens: int = 512,
        device: str = 'cpu',
    ) -> Path:
        """Gerar respostas sobre fontes ja recuperadas, sem nova busca."""
        raise NotImplementedError('Implementar: answer_dataset')

    def evaluate(
        self,
        student_search_results_path: str,
        dataset_path: str,
        save_path: str = 'data/output/evaluation/report.json',
    ) -> Path:
        """Calcular e salvar relatorio proprio de recall."""
        raise NotImplementedError('Implementar: evaluate')
