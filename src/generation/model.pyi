"""Prototipos de generation.model; sem implementacao."""
from src.models.documents import Chunk
from src.models.generation import GenerationConfig
from src.models.generation import PreparedPrompt

class LocalGenerator:
    """Carregar modelo e tokenizer uma vez por execucao de geracao."""
    def __init__(self, config: GenerationConfig) -> None:
        """Guardar configuracao; nao carregar modelo ao importar modulo."""
        ...

    def load(self) -> None:
        """Carregar Qwen/Qwen3-0.6B e seu tokenizer."""
        ...

    def count_tokens(self, text: str) -> int:
        """Contar tokens com o tokenizer do modelo gerativo."""
        ...

    def prepare_prompt(self, question: str, context: list[Chunk]) -> PreparedPrompt:
        """Selecionar chunks inteiros que caibam no budget, contando template e saida."""
        ...

    def generate(self, prompt: PreparedPrompt) -> str:
        """Gerar somente continuacao/resposta, respeitando max_new_tokens."""
        ...

    def close(self) -> None:
        """Liberar recursos quando necessario."""
        ...
