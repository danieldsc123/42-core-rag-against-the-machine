"""Modelo do relatório de avaliação."""
from pydantic import BaseModel


class EvaluationReport(BaseModel):
    """Recall médio por pergunta e cobertura dos IDs avaliados."""
    recall_at_k: dict[int, float]
    question_count: int
    missing_question_ids: list[str]
