"""Modelos de generation."""
from typing_extensions import Self
from pydantic import BaseModel, Field, model_validator
from src.models.source import MinimalSource


class GenerationConfig(BaseModel):
    """Orcamento da aplicacao; conferir limite real ao carregar modelo."""
    model_name: str = "Qwen/Qwen3-0.6B"
    context_window_tokens: int = Field(default=8192, gt=0)
    max_new_tokens: int = Field(default=512, gt=0)
    device: str = "cpu"

    @model_validator(mode="after")
    def validate_budget(self) -> Self:
        """Reserve space for both the prompt and generated tokens."""
        if self.max_new_tokens >= self.context_window_tokens:
            raise ValueError(
                "max_new_tokens must be smaller than context_window_tokens"
            )
        return self


class PreparedPrompt(BaseModel):
    """Prompt final e fontes efetivamente incluidas no contexto."""
    text: str
    sources: list[MinimalSource]
    input_tokens: int
