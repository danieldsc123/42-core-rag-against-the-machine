"""Character-span overlap and per-question recall metrics."""
from src.models.source import MinimalSource


def span_iou(
    left: MinimalSource,
    right: MinimalSource,
) -> float:
    """Calcular intersecao/uniao; arquivos diferentes nao correspondem."""
    if left.file_path != right.file_path:
        return 0.0
    intersection = max(
        0, min(left.last_character_index, right.last_character_index)
        - max(left.first_character_index, right.first_character_index)
    )
    union = (left.last_character_index - left.first_character_index
             + right.last_character_index - right.first_character_index
             - intersection)
    return intersection / union if union else 0.0


def question_recall(
    retrieved: list[MinimalSource],
    expected: list[MinimalSource],
    k: int,
    iou_threshold: float = 0.05,
) -> float:
    """Contar cada fonte esperada uma vez quando encontrada nos top-k."""
    raise NotImplementedError('Implementar: question_recall')
