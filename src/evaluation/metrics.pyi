"""Prototipos de evaluation.metrics; sem implementacao."""
from src.models.source import MinimalSource

def span_iou(left: MinimalSource, right: MinimalSource) -> float:
    """Calcular intersecao/uniao; arquivos diferentes nao correspondem."""
    ...


def question_recall(retrieved: list[MinimalSource], expected: list[MinimalSource], k: int, iou_threshold: float = 0.05) -> float:
    """Contar cada fonte esperada uma vez quando encontrada nos top-k."""
    ...
