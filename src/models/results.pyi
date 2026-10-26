"""Prototipos de models.results; sem implementacao."""
from pydantic import BaseModel
from src.models.source import MinimalSource

class MinimalSearchResults(BaseModel):
    """Resultado de busca sem resposta gerada."""
    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """Resultado de busca acompanhado de resposta."""
    answer: str


class StudentSearchResults(BaseModel):
    """Formato externo de busca exigido pelo subject."""
    search_results: list[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """Formato externo de respostas exigido pelo subject."""
    search_results: list[MinimalAnswer]
    k: int
