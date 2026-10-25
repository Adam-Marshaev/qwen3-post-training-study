"""Reconstruct and verify E005's frozen GRPO training dataset.

Reads only the original GSM8K training file and frozen split.
Uses the existing evaluation prompt formatter.

Writes an immutable-by-convention, SHA256-verified JSONL
training dataset and a provenance manifest.

Never accesses the official GSM8K test split.
Never loads model weights or performs training.
"""

import argparse
import hashlib
import json
import math
import os
import statistics
from pathlib import Path

from transformers import AutoTokenizer

from llm_post_training.data.gsm8k import (
    parse_gsm8k_reference_answer,
)
from llm_post_training.evaluation.prompting import (
    BASELINE_PROMPT_VERSION,
    format_baseline_prompt,
)
from llm_post_training.training.grpo_reward import (
    GRPO_REWARD_VERSION,
)


BASE = "Qwen/Qwen3-0.6B-Base"

BASE_REVISION = (
    "57ca99e94acb83175495aa2c6b6b0cc498170924"
)

SOURCE_REVISION = (
    "714d35edd3bddeaf57f656f65f4216f9262e6cea"
)

IMAGE_DIGEST = (
    "sha256:"
    "07c6ab54329a0e930842c184979de941bba850"
    "c2e03daea8656a65848a7ee80e"
)

RAW_PATH = Path("data/raw/gsm8k/train.jsonl")
SPLIT_PATH = Path("configs/data/gsm8k_split_v1.json")

REWARD_PATH = Path(
    "src/llm_post_training/training/grpo_reward.py"
)

PROMPT_PATH = Path(
    "src/llm_post_training/evaluation/prompting.py"
)

BUILDER_PATH = Path(
    "protocols/e005_grpo_preparation_v1/"
    "build_grpo_dataset_v1.py"
)

DATASET_REPO_PATH = (
    "data/train_runs/e005_grpo_from_e002a_v1/"
    "inputs/grpo_train6726_v1.jsonl"
)

EXPECTED_RAW_SHA = (
    "17f347dc51477c50d4efb83959dbb7c56297"
    "aba886e5544ee2aaed3024813465"
)

EXPECTED_SPLIT_SHA = (
    "31030317d85b015263d05383bf69bb02daec"
    "5bc67874f5ad0e0b33fa5294c719"
)

EXPECTED_REWARD_SHA = (
    "152d7cac32736fb8f797644642ea2351427"
    "b8c6e2b911531c1b88acbfc4b7acb"
)

EXPECTED_DATA_SHA = (
    "93cc63e8e57cab769cc27b136707b63943"
    "b47be02de5a82d889bd0196e6ee866"
)

EXPECTED_E002A_SHA = (
    "f56bb5b7129de7ef4ba0b76cc3c6890136"
    "fe34270e410224493a051bb192c625"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def write_without_overwriting(path: Path, content: bytes):
    """Create a new artifact or verify an existing identical one."""
    if path.exists():
        require(
            path.is_file() and path.read_bytes() == content,
            f"Existing artifact differs; refusing overwrite: {path}",
        )
        print("Existing artifact verified:", path)
        return

    require(path.parent.is_dir(), f"Missing output directory: {path.parent}")

    # Exclusive creation prevents replacing an existing artifact.
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())

    require(
        path.read_bytes() == content,
        f"Post-write verification failed: {path}",
    )

    path.chmod(0o444)
    print("Created and verified:", path)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    print("=== VERIFY FROZEN INPUTS ===", flush=True)

    require(sha256(RAW_PATH) == EXPECTED_RAW_SHA, "Raw GSM8K hash mismatch")
    require(sha256(SPLIT_PATH) == EXPECTED_SPLIT_SHA, "Split hash mismatch")
    require(sha256(REWARD_PATH) == EXPECTED_REWARD_SHA, "Reward hash mismatch")

    require(
        BASELINE_PROMPT_VERSION == "gsm8k_qa_v1",
        "Prompt version changed",
    )

    require(
        GRPO_REWARD_VERSION == "gsm8k_exact_numeric_v1",
        "Reward version changed",
    )

    split = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))

    require(
        split["source_sha256"] == EXPECTED_RAW_SHA,
        "Split source hash mismatch",
    )

    records = [
        json.loads(line)
        for line in RAW_PATH.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    training_indices = split["training_indices"]
    validation_indices = split["validation_indices"]

    require(len(records) == 7473, "Unexpected GSM8K row count")

    require(
        len(training_indices) == len(set(training_indices)) == 6726,
        "Training partition mismatch",
    )

    require(
        len(validation_indices) == len(set(validation_indices)) == 747,
        "Validation partition mismatch",
    )

    training_set = set(training_indices)
    validation_set = set(validation_indices)

    require(
        training_set.isdisjoint(validation_set),
        "Training/validation overlap",
    )

    require(
        training_set | validation_set == set(range(7473)),
        "Incomplete partition",
    )

    print("Training questions:", len(training_indices))
    print("Validation questions:", len(validation_indices))
    print("Index overlap:", len(training_set & validation_set))

    print("\n=== LOAD PINNED TOKENIZER ===", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(
        BASE,
        revision=BASE_REVISION,
        local_files_only=True,
    )

    require(
        tokenizer.pad_token_id == 151643,
        "Native PAD token mismatch",
    )

    tokenizer.eos_token = tokenizer.convert_ids_to_tokens(151643)

    require(
        tokenizer.eos_token_id == 151643,
        "Native EOS token mismatch",
    )

    print("Model:", BASE)
    print("Revision:", BASE_REVISION)
    print("Prompt version:", BASELINE_PROMPT_VERSION)

    print("\n=== GENERATE CANONICAL JSONL ===", flush=True)

    output = bytearray()
    lengths = []

    for index in training_indices:
        record = records[index]

        question = record["question"]
        answer = record["answer"]

        require(
            isinstance(question, str) and question.strip(),
            f"Invalid question at index {index}",
        )

        require(
            isinstance(answer, str) and answer.strip(),
            f"Invalid reference at index {index}",
        )

        reference = parse_gsm8k_reference_answer(answer)

        require(
            reference.is_finite(),
            f"Nonfinite reference at index {index}",
        )

        prompt = format_baseline_prompt(question)

        require(
            "####" not in prompt,
            f"Reference-answer delimiter in prompt {index}",
        )

        tokens = tokenizer.encode(
            prompt,
            add_special_tokens=False,
        )

        require(
            0 < len(tokens) <= 256,
            f"Prompt exceeds 256 tokens at index {index}",
        )

        lengths.append(len(tokens))

        row = {
            "source_index": index,
            "prompt": prompt,
            "answer": answer,
        }

        line = json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ) + "\n"

        output.extend(line.encode("utf-8"))

    data_bytes = bytes(output)
    data_sha = hashlib.sha256(data_bytes).hexdigest()

    require(
        data_sha == EXPECTED_DATA_SHA,
        "Prospective dataset fingerprint mismatch: "
        f"{data_sha}",
    )

    require(
        len(lengths) == 6726,
        "Generated dataset row count mismatch",
    )

    require(
        max(lengths) == 215,
        "Longest prompt differs from audited result",
    )

    require(
        sum(length > 128 for length in lengths) == 87,
        "128-token distribution differs",
    )

    require(
        sum(length > 192 for length in lengths) == 2,
        "192-token distribution differs",
    )

    print("Dataset SHA256:", data_sha)
    print("Dataset bytes:", len(data_bytes))
    print("Rows:", len(training_indices))
    print("Mean prompt tokens:", round(statistics.mean(lengths), 2))
    print("Maximum prompt tokens:", max(lengths))
    print("Prompts truncated: ZERO")

    manifest = {
        "schema_version": "e005_grpo_dataset_manifest_v1",
        "experiment": "E005",
        "purpose": "GRPO training input",
        "source_git_revision": SOURCE_REVISION,
        "docker_image_digest": IMAGE_DIGEST,
        "base_model": {
            "id": BASE,
            "revision": BASE_REVISION,
            "native_eos_pad_id": 151643,
        },
        "starting_adapter": {
            "experiment": "E002a",
            "sha256": EXPECTED_E002A_SHA,
        },
        "source_dataset": {
            "path": str(RAW_PATH),
            "sha256": EXPECTED_RAW_SHA,
            "total_rows": 7473,
        },
        "split": {
            "path": str(SPLIT_PATH),
            "sha256": EXPECTED_SPLIT_SHA,
            "training_rows": 6726,
            "validation_rows": 747,
            "index_overlap": 0,
        },
        "prompt": {
            "version": BASELINE_PROMPT_VERSION,
            "formatter": "format_baseline_prompt",
            "formatter_source_sha256": sha256(PROMPT_PATH),
            "max_allowed_tokens": 256,
            "max_observed_tokens": max(lengths),
            "mean_observed_tokens": round(
                statistics.mean(lengths), 2
            ),
            "truncation_allowed": False,
        },
        "reward": {
            "version": GRPO_REWARD_VERSION,
            "source_sha256": EXPECTED_REWARD_SHA,
        },
        "builder": {
            "path": str(BUILDER_PATH),
            "sha256": sha256(BUILDER_PATH),
        },
        "output": {
            "path": DATASET_REPO_PATH,
            "sha256": data_sha,
            "bytes": len(data_bytes),
            "rows": len(training_indices),
            "columns": [
                "answer",
                "prompt",
                "source_index",
            ],
            "serialization": (
                "UTF-8 JSONL; sort_keys=True; "
                "ensure_ascii=False; "
                "separators=(',', ':'); "
                "one LF per row"
            ),
            "row_order": "frozen training_indices order",
        },
        "training_performed": False,
        "official_test_accessed": False,
    }

    manifest_bytes = (
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n"
    ).encode("utf-8")

    print("\n=== WRITE VERIFIED ARTIFACTS ===", flush=True)

    write_without_overwriting(args.output, data_bytes)

    require(
        sha256(args.output) == EXPECTED_DATA_SHA,
        "On-disk dataset hash mismatch",
    )

    write_without_overwriting(args.manifest, manifest_bytes)

    print("\n=== FINAL BUILDER RESULT ===")
    print("Dataset:", DATASET_REPO_PATH)
    print("Dataset SHA256:", sha256(args.output))
    print("Manifest SHA256:", sha256(args.manifest))
    print("Training examples:", 6726)
    print("Validation examples included: NO")
    print("E004 preference data accessed: NO")
    print("Official GSM8K test accessed: NO")
    print("Training performed: NO")
    print("E005 DATASET FREEZE: PASSED")


if __name__ == "__main__":
    main()
