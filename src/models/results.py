"""Modelos públicos dos resultados de busca e das respostas."""
from typing_extensions import Self
from pydantic import BaseModel, Field, model_validator
from src.models.source import MinimalSource


class MinimalSearchResults(BaseModel):
    """Resultado de busca sem resposta gerada."""
    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]

    @model_validator(mode="after")
    def validate_source_sizes(self) -> Self:
        """Aplicar o limite do avaliador apenas às fontes recuperadas."""
        if any(
            source.last_character_index - source.first_character_index > 2000
            for source in self.retrieved_sources
        ):
            raise ValueError(
                "retrieved sources must have at most 2000 characters"
            )
        return self


class MinimalAnswer(MinimalSearchResults):
    """Resultado de busca acompanhado de resposta."""
    answer: str


class StudentSearchResults(BaseModel):
    """Formato externo de busca exigido pelo subject."""
    search_results: list[MinimalSearchResults]
    k: int = Field(ge=0, strict=True)


class StudentSearchResultsAndAnswer(BaseModel):
    """Formato externo de respostas exigido pelo subject."""
    search_results: list[MinimalAnswer]
    k: int = Field(ge=0, strict=True)
