"""Utilities for parsing GSM8K reference answers."""

import re
from decimal import Decimal


# Match a complete final-answer line, for example:
#
# #### 72
# #### -12.5
# #### 1,250
#
# We do not extract intermediate calculations.

_FINAL_ANSWER_LINE = re.compile(
    r"^####[ \t]*(?P<answer>[^\r\n]*)$",
    flags=re.MULTILINE,
)

_NUMERIC_ANSWER = re.compile(
    r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
)


def parse_gsm8k_reference_answer(solution: str) -> Decimal:
    """Parse the numerical answer at the end of a GSM8K solution.

    Raises ValueError if the reference has no unique, valid
    final-answer line or contains text after that line.
    """

    text = solution.strip()

    matches = list(_FINAL_ANSWER_LINE.finditer(text))

    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one GSM8K final-answer line"
        )

    match = matches[0]

    if match.end() != len(text):
        raise ValueError(
            "Unexpected content after GSM8K final answer"
        )

    answer_text = match.group("answer").strip()

    if not _NUMERIC_ANSWER.fullmatch(answer_text):
        raise ValueError(
            f"Invalid GSM8K numerical answer: {answer_text!r}"
        )

    return Decimal(answer_text.replace(",", ""))
