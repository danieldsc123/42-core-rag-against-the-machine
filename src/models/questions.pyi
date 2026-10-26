"""Prototipos de models.questions; sem implementacao."""
from pydantic import BaseModel
from src.models.source import MinimalSource

class UnansweredQuestion(BaseModel):
    """Gerar UUID como default de question_id na implementacao."""
    question_id: str
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """Gabarito usado apenas na avaliacao."""
    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """Preservar os campos do gabarito ao validar a uniao."""
    rag_questions: list[AnsweredQuestion | UnansweredQuestion]
