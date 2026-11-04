"""Prototipos de cli.commands; sem implementacao."""
from pathlib import Path


class RagCLI:
    """Coordenar servicos e transformar erros esperados em mensagens claras."""

    def index(
        self,
        max_chunk_size: int = 2000,
        corpus_path: str = 'data/raw',
        index_directory: str = 'data/processed',
        project_root: str = '.',
        method: str = 'tfidf',
    ) -> None:
        """Construir indice e exibir resumo."""
        raise NotImplementedError('Implementar: index')

    def search(
        self,
        query: str,
        k: int = 10,
        index_directory: str = 'data/processed',
        save_path: str = 'data/output/search_results/single.json',
    ) -> Path:
        """Buscar uma pergunta e salvar StudentSearchResults."""
        raise NotImplementedError('Implementar: search')

    def search_dataset(
        self,
        dataset_path: str,
        k: int = 10,
        save_directory: str = 'data/output/search_results/UnansweredQuestions',
        index_directory: str = 'data/processed',
    ) -> Path:
        """Buscar dataset e salvar JSON com nome de entrada."""
        raise NotImplementedError('Implementar: search_dataset')

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
