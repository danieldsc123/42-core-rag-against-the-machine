"""Modelos de perguntas e datasets."""
from uuid import uuid4
from typing_extensions import Self
from pydantic import BaseModel, Field, model_validator
from src.models.source import MinimalSource


class UnansweredQuestion(BaseModel):
    """Pergunta com identificador gerado quando omitido."""
    question_id: str = Field(
        default_factory=lambda: str(uuid4()), min_length=1
    )
    question: str = Field(min_length=1)


class AnsweredQuestion(UnansweredQuestion):
    """Gabarito usado apenas na avaliação."""
    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """Preservar os campos do gabarito ao validar a união."""
    rag_questions: list[AnsweredQuestion | UnansweredQuestion]

    @model_validator(mode="before")
    @classmethod
    def validate_answer_pairs(cls, value: object) -> object:
        """Rejeitar gabaritos inválidos antes da seleção do tipo na união."""
        if isinstance(value, dict):
            for question in value.get("rag_questions", []):
                if isinstance(question, dict) and (
                    "answer" in question or "sources" in question
                ):
                    AnsweredQuestion.model_validate(question)
        return value

    @model_validator(mode="after")
    def validate_unique_ids(self) -> Self:
        """Rejeitar identificadores de perguntas duplicados."""
        ids = [question.question_id for question in self.rag_questions]
        if len(ids) != len(set(ids)):
            raise ValueError("question_id values must be unique")
        return self
