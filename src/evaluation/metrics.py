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
    if k < 0 or not 0 < iou_threshold <= 1:
        raise ValueError('invalid k or IoU threshold')
    if not expected:
        raise ValueError('reference question must contain at least one source')
    found = sum(
        any(span_iou(actual, reference) >= iou_threshold
            for actual in retrieved[:k])
        for reference in expected
    )
    return found / len(expected)
