"""Modelos de evaluation."""
from pydantic import BaseModel


class EvaluationReport(BaseModel):
    """Recall medio por pergunta e cobertura dos IDs avaliados."""
    recall_at_k: dict[int, float]
    question_count: int
    missing_question_ids: list[str]
