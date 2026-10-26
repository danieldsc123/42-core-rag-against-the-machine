"""Prototipos de models.generation; sem implementacao."""
from pydantic import BaseModel
from src.models.source import MinimalSource

class GenerationConfig(BaseModel):
    """Defaults a definir; modelo padrao Qwen/Qwen3-0.6B."""
    model_name: str
    context_window_tokens: int
    max_new_tokens: int
    device: str


class PreparedPrompt(BaseModel):
    """Prompt final e fontes efetivamente incluidas no contexto."""
    text: str
    sources: list[MinimalSource]
    input_tokens: int
