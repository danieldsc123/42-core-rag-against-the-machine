"""Avaliar buscas salvas pelo ID da pergunta, sem avaliadores externos."""
from src.evaluation.metrics import question_recall
from src.models.evaluation import EvaluationReport
from src.models.questions import AnsweredQuestion, RagDataset
from src.models.results import StudentSearchResults


def evaluate_results(
    results: StudentSearchResults,
    ground_truth: RagDataset,
    ks: tuple[int, ...] = (1, 3, 5, 10),
    iou_threshold: float = 0.05,
) -> EvaluationReport:
    """Calcular o recall médio, contando resultados ausentes como zero."""
    if any(k < 0 for k in ks) or not 0 < iou_threshold <= 1:
        raise ValueError('invalid recall cutoffs or IoU threshold')
    references: dict[str, AnsweredQuestion] = {}
    for question in ground_truth.rag_questions:
        if not isinstance(question, AnsweredQuestion) or not question.sources:
            raise ValueError(
                'evaluation requires answered reference questions'
            )
        references[question.question_id] = question
    predictions = {r.question_id: r for r in results.search_results}
    if len(predictions) != len(results.search_results):
        raise ValueError('duplicate prediction question IDs')
    if set(predictions) - set(references):
        raise ValueError('predictions contain unknown question IDs')
    totals = {k: 0.0 for k in ks}
    for question_id, reference in references.items():
        prediction = predictions.get(question_id)
        sources = prediction.retrieved_sources if prediction else []
        for k in ks:
            totals[k] += question_recall(
                sources, reference.sources, k, iou_threshold
            )
    count = len(references)
    return EvaluationReport(
        recall_at_k={k: value / count if count else 0.0
                     for k, value in totals.items()},
        question_count=count,
        missing_question_ids=sorted(set(references) - set(predictions)),
    )
