"""Aggregate mathematical reasoning evaluation results."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from llm_post_training.evaluation.answer_extraction import (
    AnswerExtraction,
    extract_final_answer,
)


@dataclass(frozen=True)
class EvaluationRecord:
    """Evaluation result for one mathematical problem."""

    expected_answer: Decimal
    extraction: AnswerExtraction
    generated_tokens: int
    reached_token_cap: bool = False

    def __post_init__(self) -> None:
        if self.generated_tokens < 0:
            raise ValueError("generated_tokens cannot be negative")

    @property
    def correct(self) -> bool:
        """Whether the model produced a valid, correct answer."""
        return (
            self.extraction.status == "valid"
            and self.extraction.answer == self.expected_answer
        )


@dataclass(frozen=True)
class EvaluationSummary:
    """Aggregate metrics across evaluated problems."""

    total: int
    correct: int
    valid_extractions: int
    missing_answers: int
    ambiguous_answers: int
    unwanted_continuations: int
    reached_token_cap_count: int

    accuracy: float
    extraction_rate: float
    missing_rate: float
    ambiguous_rate: float
    unwanted_continuation_rate: float
    reached_token_cap_rate: float
    mean_generated_tokens: float


def evaluate_response(
    response: str,
    expected_answer: Decimal,
    generated_tokens: int,
    reached_token_cap: bool = False,
) -> EvaluationRecord:
    """Evaluate one generated mathematical response."""

    extraction = extract_final_answer(response)

    return EvaluationRecord(
        expected_answer=expected_answer,
        extraction=extraction,
        generated_tokens=generated_tokens,
        reached_token_cap=reached_token_cap,
    )


def summarize_evaluations(
    records: Sequence[EvaluationRecord],
) -> EvaluationSummary:
    """Compute dataset-level metrics from evaluation records."""

    total = len(records)

    if total == 0:
        raise ValueError("Cannot summarize an empty evaluation")

    correct = sum(record.correct for record in records)

    valid = sum(
        record.extraction.status == "valid"
        for record in records
    )

    missing = sum(
        record.extraction.status == "missing"
        for record in records
    )

    ambiguous = sum(
        record.extraction.status == "ambiguous"
        for record in records
    )

    continuations = sum(
        record.extraction.unwanted_continuation
        for record in records
    )

    token_cap_count = sum(
        record.reached_token_cap
        for record in records
    )

    total_generated_tokens = sum(
        record.generated_tokens
        for record in records
    )

    return EvaluationSummary(
        total=total,
        correct=correct,
        valid_extractions=valid,
        missing_answers=missing,
        ambiguous_answers=ambiguous,
        unwanted_continuations=continuations,
        reached_token_cap_count=token_cap_count,
        accuracy=correct / total,
        extraction_rate=valid / total,
        missing_rate=missing / total,
        ambiguous_rate=ambiguous / total,
        unwanted_continuation_rate=continuations / total,
        reached_token_cap_rate=token_cap_count / total,
        mean_generated_tokens=total_generated_tokens / total,
    )
