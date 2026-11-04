"""Lazy local Qwen generation with exact tokenizer-based context budgets."""
import gc
import json
import os
from typing import Any

from src.models.documents import Chunk
from src.models.generation import GenerationConfig
from src.models.generation import PreparedPrompt


class LocalGenerator:
    """Carregar modelo e tokenizer uma vez por execucao de geracao."""

    def __init__(
        self,
        config: GenerationConfig,
    ) -> None:
        """Guardar configuracao; nao carregar modelo ao importar modulo."""
        self.config = config
        self.tokenizer: Any = None
        self.model: Any = None
        self.context_limit = config.context_window_tokens

    def load(
        self,
    ) -> None:
        """Carregar Qwen/Qwen3-0.6B e seu tokenizer."""
        raise NotImplementedError('Implementar: load')

    def count_tokens(
        self,
        text: str,
    ) -> int:
        """Contar tokens com o tokenizer do modelo gerativo."""
        raise NotImplementedError('Implementar: count_tokens')

    def prepare_prompt(
        self,
        question: str,
        context: list[Chunk],
    ) -> PreparedPrompt:
        """Selecionar chunks dentro do budget, incluindo template e saida."""
        raise NotImplementedError('Implementar: prepare_prompt')

    def generate(
        self,
        prompt: PreparedPrompt,
    ) -> str:
        """Gerar somente continuacao/resposta, respeitando max_new_tokens."""
        raise NotImplementedError('Implementar: generate')

    def close(
        self,
    ) -> None:
        """Liberar recursos quando necessario."""
        raise NotImplementedError('Implementar: close')
