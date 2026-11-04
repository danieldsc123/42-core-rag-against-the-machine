"""Prototipos de evaluation.service; sem implementacao."""
from src.models.evaluation import EvaluationReport
from src.models.questions import RagDataset
from src.models.results import StudentSearchResults


def evaluate_results(
    results: StudentSearchResults,
    ground_truth: RagDataset,
    ks: tuple[int, ...] = (1, 3, 5, 10),
    iou_threshold: float = 0.05,
) -> EvaluationReport:
    """Associar perguntas por ID e calcular media dos recalls por pergunta."""
    raise NotImplementedError('Implementar: evaluate_results')
