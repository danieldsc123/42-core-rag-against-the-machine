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
        if self.model is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if self.config.device.startswith('cuda') and not torch.cuda.is_available():
            raise ValueError('CUDA requested but not available')
        threads = int(os.environ.get('RAG_TORCH_THREADS', '4'))
        if threads < 1:
            raise ValueError('RAG_TORCH_THREADS must be positive')
        torch.set_num_threads(threads)
        tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name, trust_remote_code=False
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name, torch_dtype='auto', trust_remote_code=False
        )
        model.to(self.config.device)
        model.eval()
        limit = int(getattr(model.config, 'max_position_embeddings',
                            self.config.context_window_tokens))
        self.context_limit = min(self.config.context_window_tokens, limit)
        if self.config.max_new_tokens >= self.context_limit:
            raise ValueError('output budget exceeds model context limit')
        self.tokenizer = tokenizer
        self.model = model

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
