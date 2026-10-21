"""Generate a mathematical reasoning response using Qwen3-0.6B-Base."""

import torch
import torch.backends.python_native as python_native

from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen3-0.6B-Base"

MODEL_REVISION = "57ca99e94acb83175495aa2c6b6b0cc498170924"

DEVICE = "cuda:0"


def main() -> None:
    """Load the pretrained model and generate a response."""

    assert torch.cuda.is_available(), "CUDA is required"

    # Avoid incompatible native Triton operator overrides on Volta.
    python_native.triton.enabled = False

    print("Loading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
    )

    print("Loading model...")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        dtype=torch.float16,
        attn_implementation="eager",
        use_safetensors=True,
    )

    model = model.to(DEVICE)
    model.eval()

    prompt = (
        "Question: A warehouse has 240 components. "
        "It ships 35% of them and then receives 48 more. "
        "How many components remain?\n"
        "Answer:"
    )

    print("\n=== INPUT PROMPT ===")
    print(prompt)

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        add_special_tokens=False,
    ).to(DEVICE)

    input_length = inputs["input_ids"].shape[1]

    print("\nInput tokens:", input_length)

    print("\n=== GENERATION ===")

    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=96,
            do_sample=False,
            use_cache=False,
            stop_strings=["\nQuestion:"],
            tokenizer=tokenizer,
            pad_token_id=tokenizer.eos_token_id,
        )

    torch.cuda.synchronize()

    # Extract only newly generated tokens.
    new_token_ids = generated_ids[0, input_length:]

    response = tokenizer.decode(
        new_token_ids,
        skip_special_tokens=True,
    )

    print("\nGenerated response:")
    print(response)

    print("\n=== GENERATION STATISTICS ===")

    print("Input tokens:", input_length)
    print("Generated tokens:", len(new_token_ids))
    print("Total tokens:", generated_ids.shape[1])

    print(
        "Peak allocated GPU memory:",
        f"{torch.cuda.max_memory_allocated() / 1024**2:.2f} MiB",
    )

    assert len(new_token_ids) > 0, "No tokens generated"

    print("\nGeneration smoke test: PASSED")


if __name__ == "__main__":
    main()
