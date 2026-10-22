"""Extract verifiable numerical answers from generated text."""

import re

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


ExtractionStatus = Literal["valid", "missing", "ambiguous"]


@dataclass(frozen=True)
class AnswerExtraction:
    """Structured result of mathematical answer extraction."""

    answer: Decimal | None
    status: ExtractionStatus
    unwanted_continuation: bool


# Supported final-answer declarations:
#
#   Final answer: 204
#   The answer is 204
#   Final answer: -12.5
#   Final answer: 1,250
#
# We deliberately do not extract arbitrary numbers from reasoning.

FINAL_ANSWER_PATTERN = re.compile(
    r"(?<!\w)"
    r"(?:final[ \t]+answer[ \t]*:|the[ \t]+answer[ \t]+is)"
    r"[ \t]*"
    r"(?P<number>[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)"
    r"(?![\d,])",
    flags=re.IGNORECASE,
)


# Recognize explicitly boxed numerical answers such as:
#
#   \boxed{9}
#   \boxed{-12.5}
#   \boxed{1,250}
#
# Deliberately reject boxed arithmetic expressions or variables.
BOXED_ANSWER_PATTERN = re.compile(
    r"\\boxed\{[ \t]*"
    r"(?P<number>[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)"
    r"[ \t]*\}"
)


# Detect the start of a newly generated question.
NEXT_QUESTION_PATTERN = re.compile(
    r"^[ \t]*(?:Question[ \t]*:|\[Question\])",
    flags=re.IGNORECASE | re.MULTILINE,
)


def extract_final_answer(response: str) -> AnswerExtraction:
    """Extract a numerical final answer from generated text.

    Only explicit final-answer declarations are recognized.

    If the model begins another question, extraction is restricted
    to the response preceding that question.

    Conflicting answer declarations are treated as ambiguous.
    """

    next_question = NEXT_QUESTION_PATTERN.search(response)

    unwanted_continuation = next_question is not None

    if next_question is not None:
        response = response[:next_question.start()]

    matches = (
        FINAL_ANSWER_PATTERN.findall(response)
        + BOXED_ANSWER_PATTERN.findall(response)
    )

    if not matches:
        return AnswerExtraction(
            answer=None,
            status="missing",
            unwanted_continuation=unwanted_continuation,
        )

    answers = {
        Decimal(value.replace(",", ""))
        for value in matches
    }

    if len(answers) != 1:
        return AnswerExtraction(
            answer=None,
            status="ambiguous",
            unwanted_continuation=unwanted_continuation,
        )

    return AnswerExtraction(
        answer=answers.pop(),
        status="valid",
        unwanted_continuation=unwanted_continuation,
    )
