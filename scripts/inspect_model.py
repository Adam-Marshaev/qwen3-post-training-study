"""Inspect Qwen3-0.6B-Base architecture and GPU memory."""

import torch
import torch.backends.python_native as python_native
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen3-0.6B-Base"

# Pin the exact Hugging Face model revision for reproducibility.
MODEL_REVISION = "57ca99e94acb83175495aa2c6b6b0cc498170924"

DEVICE = "cuda:0"


def main() -> None:
    assert torch.cuda.is_available(), "CUDA is required for this experiment"

    # Avoid native Triton operator overrides on the Tesla V100.
    # PyTorch 2.14 may dispatch certain operations to Triton kernels.
    python_native.triton.enabled = False

    print("Native Triton enabled:", python_native.triton.enabled)

    print("Loading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
    )

    print("Loading pretrained model...")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        dtype=torch.float16,
        attn_implementation="eager",
        use_safetensors=True,
    )

    model.eval()

    config = model.config

    print("\n=== MODEL CONFIGURATION ===")

    print("Model:", MODEL_ID)
    print("Revision:", MODEL_REVISION)
    print("Architecture:", type(model).__name__)
    print("Vocabulary allocation:", config.vocab_size)
    print("Tokenizer vocabulary:", tokenizer.vocab_size)
    print("Hidden dimension:", config.hidden_size)
    print("Transformer layers:", config.num_hidden_layers)
    print("Query heads:", config.num_attention_heads)
    print("Key/value heads:", config.num_key_value_heads)
    print("Head dimension:", config.head_dim)
    print("MLP intermediate dimension:", config.intermediate_size)

    print("\n=== PARAMETER COUNT ===")

    num_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    parameter_bytes = sum(
        parameter.numel() * parameter.element_size()
        for parameter in model.parameters()
    )

    print(f"Parameters: {num_parameters:,}")
    print(f"Parameter storage: {parameter_bytes / 1024**2:.2f} MiB")

    print("\n=== EMBEDDING MATRIX ===")

    embedding = model.get_input_embeddings()

    print("Embedding shape:", tuple(embedding.weight.shape))
    print("Embedding dtype:", embedding.weight.dtype)

    assert embedding.weight.shape == (
        config.vocab_size,
        config.hidden_size,
    )

    print("\n=== FIRST TRANSFORMER LAYER ===")

    first_layer = model.model.layers[0]

    attention = first_layer.self_attn

    print("Query projection:", tuple(attention.q_proj.weight.shape))
    print("Key projection:", tuple(attention.k_proj.weight.shape))
    print("Value projection:", tuple(attention.v_proj.weight.shape))
    print("Output projection:", tuple(attention.o_proj.weight.shape))

    print("\n=== FEED-FORWARD NETWORK ===")

    mlp = first_layer.mlp

    print("Gate projection:", tuple(mlp.gate_proj.weight.shape))
    print("Up projection:", tuple(mlp.up_proj.weight.shape))
    print("Down projection:", tuple(mlp.down_proj.weight.shape))

    print("\n=== GPU MEMORY ===")

    torch.cuda.reset_peak_memory_stats()

    model = model.to(DEVICE)

    torch.cuda.synchronize()

    allocated_after_load = torch.cuda.memory_allocated()

    print(
        "Allocated after model load:",
        f"{allocated_after_load / 1024**2:.2f} MiB",
    )

    print("\n=== FORWARD PASS ===")

    prompt = (
        "A warehouse has 240 components. "
        "It ships 35% of them.\n"
        "Final answer:"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        add_special_tokens=False,
    ).to(DEVICE)

    print("Input shape:", tuple(inputs["input_ids"].shape))

    with torch.inference_mode():
        outputs = model(
            **inputs,
            use_cache=False,
        )

    torch.cuda.synchronize()

    logits = outputs.logits

    print("Logits shape:", tuple(logits.shape))
    print("Logits dtype:", logits.dtype)

    assert logits.shape == (
        1,
        inputs["input_ids"].shape[1],
        config.vocab_size,
    )

    assert torch.isfinite(logits).all().item()

    next_token_id = logits[0, -1].argmax().item()

    print("Most likely next token ID:", next_token_id)
    print(
        "Most likely next token:",
        repr(tokenizer.decode([next_token_id])),
    )

    print(
        "Peak GPU memory allocated:",
        f"{torch.cuda.max_memory_allocated() / 1024**2:.2f} MiB",
    )

    print("\nModel inspection: PASSED")


if __name__ == "__main__":
    main()
