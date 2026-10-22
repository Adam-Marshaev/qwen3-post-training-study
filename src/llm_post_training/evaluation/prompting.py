"""Versioned prompt templates for mathematical evaluation."""


BASELINE_PROMPT_VERSION = "gsm8k_qa_v1"


def format_baseline_prompt(question: str) -> str:
    """Format one mathematical question for causal LM inference.

    This template intentionally matches our initial successful
    Qwen3-0.6B-Base generation experiment.
    """

    if not isinstance(question, str):
        raise TypeError("question must be a string")

    question = question.strip()

    if not question:
        raise ValueError("question cannot be empty")

    return f"Question: {question}\nAnswer:"
