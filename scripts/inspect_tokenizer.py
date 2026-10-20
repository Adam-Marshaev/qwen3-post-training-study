"""Inspect tokenization behavior for Qwen3-0.6B-Base."""

from transformers import AutoTokenizer


MODEL_ID = "Qwen/Qwen3-0.6B-Base"


def main() -> None:
    """Load the tokenizer and inspect a mathematical reasoning prompt."""

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    prompt = (
        "A warehouse has 240 components. "
        "It ships 35% of them.\n"
        "Final answer:"
    )

    # Convert text into token IDs.
    token_ids = tokenizer.encode(
        prompt,
        add_special_tokens=False,
    )

    # Convert IDs into their corresponding token representations.
    tokens = tokenizer.convert_ids_to_tokens(token_ids)

    # Reconstruct the original text.
    decoded = tokenizer.decode(
        token_ids,
        skip_special_tokens=False,
        clean_up_tokenization_spaces=False,
    )

    print(f"Model: {MODEL_ID}")
    print(f"Vocabulary size: {tokenizer.vocab_size}")
    print(f"Total tokenizer entries: {len(tokenizer)}")
    print(f"Fast tokenizer: {tokenizer.is_fast}")

    print("\nOriginal prompt:")
    print(repr(prompt))

    print("\nToken IDs:")
    print(token_ids)

    print("\nToken breakdown:")
    for token_id, token in zip(token_ids, tokens):
        print(f"{token_id:>8} -> {token!r}")

    print("\nDecoded prompt:")
    print(repr(decoded))

    assert decoded == prompt, "Tokenization round-trip failed"
    assert len(token_ids) > 0, "No tokens generated"

    print("\nTokenizer verification: PASSED")


if __name__ == "__main__":
    main()
