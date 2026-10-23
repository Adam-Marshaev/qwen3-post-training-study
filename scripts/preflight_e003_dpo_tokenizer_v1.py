#!/usr/bin/env python3
"""Read-only E003 109-pair TRL 0.26.2 tokenization and EOS preflight.

Requires the project-staged dataset and the exact offline Qwen3 tokenizer.
Does not load a model, initialize DPOTrainer, write files, or train.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from importlib.metadata import version
import json
from pathlib import Path

DATA_SHA = '7d088bd70dc1d3d8b05f251a5560b37aca24a064ec7c4c81c91a03b8d84dc8e9'
META_SHA = 'a304a05e9c9576e7df871b20f9027b35e4f461252ba35564019dca6303ac275a'
MODEL_ID = 'Qwen/Qwen3-0.6B-Base'
MODEL_REV = '57ca99e94acb83175495aa2c6b6b0cc498170924'
GIT_REV = '277c8636d7930c278fa8068a4c70f55b60ea770f'
NATIVE_STOP = 151643
CONFIGURED_EOS = 151645
MAX_LENGTH = 1024
MAX_PROMPT = 512
MAX_COMPLETION = 512


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    lines = path.read_text(encoding='utf-8').splitlines()
    require(bool(lines) and all(lines), f'Empty/blank JSONL: {path}')
    return [json.loads(line) for line in lines]


def check_staged(root: Path):
    stage = root / 'data/preference_runs/e003_dpo_signed109_staged_277c863_v1'
    paths = {name: stage / name for name in ('pairs_staged.jsonl', 'pair_metadata.jsonl', 'manifest.json')}
    for path in paths.values():
        require(path.is_file(), f'Missing staged file: {path}')
    require(digest(paths['pairs_staged.jsonl'].read_bytes()) == DATA_SHA, 'DPO pair digest mismatch')
    require(digest(paths['pair_metadata.jsonl'].read_bytes()) == META_SHA, 'DPO metadata digest mismatch')
    manifest = json.loads(paths['manifest.json'].read_text())
    require(manifest['pair_dataset_sha256'] == DATA_SHA, 'Manifest pair digest mismatch')
    require(manifest['pair_metadata_sha256'] == META_SHA, 'Manifest metadata digest mismatch')
    require(manifest['git_revision'] == GIT_REV, 'Manifest staging-code revision mismatch')
    require(manifest['training_authorized'] is False and manifest['training_performed'] is False,
            'Staged manifest unexpectedly claims training authorized or performed')
    require(manifest['pair_count'] == 109 and manifest['sft_only_rewrites_used_in_dpo'] is False,
            'Unexpected staged population or SFT-only content')
    pairs = read_jsonl(paths['pairs_staged.jsonl'])
    notes = read_jsonl(paths['pair_metadata.jsonl'])
    require(len(pairs) == len(notes) == 109, 'Expected 109 pairs and metadata rows')
    ids = [r['source_index'] for r in notes]
    require(ids == sorted(set(ids)) and 5436 in ids, 'Expected 109 source-unique ordered rows with 5436')
    for pair, note in zip(pairs, notes):
        require(set(pair) == {'prompt', 'chosen', 'rejected'}, 'Unexpected DPO data schema')
        for field in ('prompt', 'chosen', 'rejected'):
            require(isinstance(pair[field], str) and pair[field].strip(), f'Blank {field}')
            require(digest(pair[field].encode('utf-8')) == note['prompt_sha256_raw' if field == 'prompt' else f'{field}_text_sha256_raw'],
                    f'Text hash mismatch at source {note["source_index"]}, {field}')
        for choice in ('chosen', 'rejected'):
            ids_ = note[f'{choice}_generated_token_ids']
            require(len(ids_) > 1 and ids_[-1] == NATIVE_STOP, 'Original response EOS missing')
            require(len(ids_) == note[f'{choice}_generated_tokens'], 'Original response token length mismatch')
        require(note['training_authorized'] is False and note['tokenization_preflight_passed'] is False,
                'Unexpected staged approval/preflight flag')
    summary = json.loads((root / 'data/train_runs/e002a_sft_lora_native_eos_v1/summary.json').read_text())
    require(summary['training_complete'] is True and summary['epochs_completed'] == 2,
            'E002a has not been verified complete')
    require(summary['model_id'] == MODEL_ID and summary['model_revision'] == MODEL_REV and
            summary['supervised_eos_token_id'] == NATIVE_STOP,
            'E002a base model/revision/EOS drift')
    adapter_cfg = json.loads((root / 'data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter/adapter_config.json').read_text())
    require(adapter_cfg['base_model_name_or_path'] == MODEL_ID and adapter_cfg['r'] == 8,
            'E002a final adapter metadata drift')
    return pairs, notes


def analyze_pairs(tokenizer, pairs: list[dict], notes: list[dict], tokenizer_row):
    """TRL exact row tokenizer, with native EOS set on an in-memory tokenizer object."""
    require(tokenizer.pad_token_id == NATIVE_STOP, 'Unexpected Qwen pad token')
    require(tokenizer.eos_token_id == CONFIGURED_EOS, 'Unexpected as-shipped EOS token')
    stop_text = tokenizer.convert_ids_to_tokens(NATIVE_STOP)
    require(isinstance(stop_text, str) and tokenizer.convert_tokens_to_ids(stop_text) == NATIVE_STOP,
            'Cannot resolve native completion-stop token')
    # TRL's tokenize_row appends tokenizer.eos_token_id to BOTH responses.
    # Override only the in-memory tokenizer; do not rewrite dataset text or tokenizer files.
    tokenizer.eos_token = stop_text
    require(tokenizer.eos_token_id == NATIVE_STOP, 'TRL tokenizer EOS override failed')
    max_lengths = {'prompt': 0, 'chosen': 0, 'rejected': 0, 'combined': 0}
    noncanonical = []
    boundary_diffs = []
    tokenized = []
    for pair, note in zip(pairs, notes):
        src = note['source_index']
        fields = tokenizer_row(pair, processing_class=tokenizer, max_prompt_length=None,
                               max_completion_length=None, add_special_tokens=False)
        prompt = fields['prompt_input_ids']
        require(prompt and all(type(x) is int for x in prompt), f'No prompt tokens at {src}')
        max_lengths['prompt'] = max(max_lengths['prompt'], len(prompt))
        for choice in ('chosen', 'rejected'):
            ids = fields[f'{choice}_input_ids']
            require(len(ids) > 1 and ids[-1] == NATIVE_STOP, f'Missing native TRL EOS at {src} {choice}')
            require(CONFIGURED_EOS not in ids, f'SFT EOS 151645 inserted into {src} {choice}')
            require(NATIVE_STOP not in ids[:-1], f'Unexpected native EOS inside response at {src} {choice}')
            original_ids = note[f'{choice}_generated_token_ids']
            if ids != original_ids:
                noncanonical.append((src, choice, len(ids), len(original_ids)))
            # Tokenizing a completion independently is TRL 0.26.2's explicit behavior;
            # compare with joint text to flag segmentation differences, not silently alter it.
            joint = tokenizer(pair['prompt'] + pair[choice], add_special_tokens=False)['input_ids']
            if joint != prompt + ids[:-1]:
                boundary_diffs.append((src, choice))
            max_lengths[choice] = max(max_lengths[choice], len(ids))
            max_lengths['combined'] = max(max_lengths['combined'], len(prompt) + len(ids))
        tokenized.append(fields)
    require(max_lengths['prompt'] <= MAX_PROMPT and max_lengths['chosen'] <= MAX_COMPLETION
            and max_lengths['rejected'] <= MAX_COMPLETION and max_lengths['combined'] <= MAX_LENGTH,
            f'DPO truncation would occur at proposed limits: {max_lengths}')
    # TRL uses attention masks—not token-value comparison—to distinguish padding;
    # this matters because the native Qwen stop and pad IDs are both 151643.
    from trl.trainer.dpo_trainer import DataCollatorForPreference
    batch = DataCollatorForPreference(pad_token_id=tokenizer.pad_token_id)(tokenized[:2])
    for choice in ('chosen', 'rejected'):
        mask = batch[f'{choice}_attention_mask']
        ids = batch[f'{choice}_input_ids']
        for i in range(2):
            length = len(tokenized[i][f'{choice}_input_ids'])
            require(int(mask[i].sum()) == length, 'Completion attention mask includes padding')
            require(ids[i, length-1].item() == NATIVE_STOP and mask[i, length-1].item() == 1,
                    'Native EOS is being masked as padding')
            require(not bool(mask[i, length:].any()), 'Completion pad positions unmasked')
    for i in range(2):
        mask = batch['prompt_attention_mask'][i]
        require(int(mask.sum()) == len(tokenized[i]['prompt_input_ids']),
                'Prompt attention mask includes padding')
    return max_lengths, noncanonical, boundary_diffs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root', type=Path, default=Path('.'))
    args = p.parse_args()
    root = args.repo_root.resolve()
    print('=== E003 DPO109 TRL 0.26.2 TOKENIZER PREFLIGHT (NO TRAINING) ===', flush=True)
    pairs, notes = check_staged(root)
    print('Signed, staged 109 pairs and E002a checkpoint metadata: VERIFIED', flush=True)
    for pkg, want in (('trl', '0.26.2'), ('transformers', '4.57.6'), ('peft', '0.18.1')):
        found = version(pkg)
        require(found == want, f'{pkg} drift: {found} != {want}')
        print(f'{pkg}: {found}')
    from transformers import AutoTokenizer
    from trl import DPOTrainer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV, local_files_only=True)
    lengths, reencodings, boundaries = analyze_pairs(tokenizer, pairs, notes, DPOTrainer.tokenize_row)
    print('TRL native completion EOS ID:', tokenizer.eos_token_id)
    print('Native EOS and PAD share ID 151643: handled by attention masks')
    print('Maximum token lengths:', json.dumps(lengths, sort_keys=True))
    print('Original generated-ID vs separately retokenized-completion differences:', len(reencodings), '/ 218')
    if reencodings:
        print('  First 10 original-ID differences:', reencodings[:10])
    print('Prompt+completion joint vs TRL separate tokenization boundary differences:', len(boundaries), '/ 218')
    if boundaries:
        print('  First 10 boundary differences:', boundaries[:10])
    print('TRL data collator: completion EOS unmasked, padding masked: VERIFIED')
    print('Reference policy: MUST load two identical E002a LoRA adapters and set ref_adapter_name explicitly')
    print('WARNING: Default PEFT reference in TRL is the BASE MODEL, not E002a. Do not use default.')
    print('GPU model load / adapter-copy identity: NOT TESTED')
    print('Hyperparameters / final release: NOT FROZEN')
    print('Training authorized: NO; training performed: NO')
    if reencodings:
        print('E003 DPO109 TOKENIZER PREFLIGHT: HOLD — original-vs-TRL token identity differences need review')
        raise SystemExit(2)
    print('E003 DPO109 TOKENIZER PREFLIGHT: PASSED (REFERENCE/GPU PREFLIGHT PENDING)')


if __name__ == '__main__':
    main()
