#!/usr/bin/env python3
"""Pinned E003 DPO109 candidate: safe validation by default; training gated.

No training is possible unless both --execute-approved-training AND the explicit
E003_DPO_TRAINING_APPROVED=YES environment variable are supplied. Do not use
that mode without an independent user authorization step.

Validation mode: reads pinned artifacts, loads named PEFT adapters, initializes
TRL, validates EOS/data/reference and checks a single no-gradient DPO loss.
No backward, optimizer creation, trainer.train(), or checkpoints in that mode.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from importlib.metadata import version
from pathlib import Path

import torch

# Established V100 backend policy. Must happen before any CUDA forward pass.
torch.backends.python_native.triton.enabled = False
torch.backends.cudnn.benchmark = False

from datasets import Dataset
from peft import PeftModel, get_peft_model_state_dict
from peft.utils.save_and_load import set_peft_model_state_dict
from safetensors.torch import load_file
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from trl import DPOConfig, DPOTrainer

BASE = 'Qwen/Qwen3-0.6B-Base'
BASE_REVISION = '57ca99e94acb83175495aa2c6b6b0cc498170924'
PAIRS_PATH = Path('data/preference_runs/e003_dpo_signed109_staged_277c863_v1/pairs_staged.jsonl')
PAIRS_SHA256 = '7d088bd70dc1d3d8b05f251a5560b37aca24a064ec7c4c81c91a03b8d84dc8e9'
ADAPTER_DIR = Path('data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter')
EOS_ID = 151643
N_PAIRS = 109
SEED = 42
BETA = 0.1
LR = 1e-6
ACCUMULATION = 8
BATCH_SIZE = 1
EPOCHS = 1
MAX_LENGTH = 1024
MAX_PROMPT_LENGTH = 512
MAX_COMPLETION_LENGTH = 512


def require(cond, explanation):
    if not cond:
        raise RuntimeError(explanation)


def state(model, adapter):
    return get_peft_model_state_dict(model, adapter_name=adapter, save_embedding_layers=False)


def check_artifacts():
    require(PAIRS_PATH.is_file(), f'Missing approved pairs: {PAIRS_PATH}')
    require(hashlib.sha256(PAIRS_PATH.read_bytes()).hexdigest() == PAIRS_SHA256,
            'Approved-pair SHA256 mismatch')
    pairs = [json.loads(line) for line in PAIRS_PATH.read_text(encoding='utf-8').splitlines()]
    require(len(pairs) == N_PAIRS, f'Expected {N_PAIRS} approved pairs, found {len(pairs)}')
    require(all(set(row) == {'prompt', 'chosen', 'rejected'} for row in pairs),
            'Pair schema mismatch')
    require((ADAPTER_DIR / 'adapter_model.safetensors').is_file(), 'E002a adapter missing')
    return pairs


def build_config(output_dir: str):
    return DPOConfig(
        output_dir=output_dir,
        model_adapter_name='policy', ref_adapter_name='reference',
        fp16=True, bf16=False, gradient_checkpointing=True,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=ACCUMULATION,
        learning_rate=LR, num_train_epochs=EPOCHS,
        lr_scheduler_type='linear', warmup_steps=0,
        optim='adamw_torch', max_grad_norm=1.0,
        beta=BETA, loss_type='sigmoid', label_smoothing=0.0,
        max_length=MAX_LENGTH, max_prompt_length=MAX_PROMPT_LENGTH,
        max_completion_length=MAX_COMPLETION_LENGTH,
        padding_free=False, precompute_ref_log_probs=False,
        reference_free=False, sync_ref_model=False,
        save_strategy='epoch', save_total_limit=1,
        eval_strategy='no', logging_strategy='steps', logging_steps=1,
        report_to='none', dataloader_num_workers=0, dataset_num_proc=None,
        remove_unused_columns=False, seed=SEED, data_seed=SEED,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-only', action='store_true',
                        help='Explicitly select read-only GPU validation (default)')
    parser.add_argument('--execute-approved-training', action='store_true',
                        help='TRAINING: requires separate user authorization and environment gate')
    parser.add_argument('--output-dir', default=None,
                        help='Explicit output directory, required for approved training')
    args = parser.parse_args()
    require(not (args.validate_only and args.execute_approved_training),
            'Choose validation or training, not both')
    training = args.execute_approved_training
    if training:
        require(os.environ.get('E003_DPO_TRAINING_APPROVED') == 'YES',
                'Training gate closed: E003_DPO_TRAINING_APPROVED=YES missing')
        require(args.output_dir is not None, 'Approved training requires --output-dir')
        out_dir = Path(args.output_dir).resolve()
        require(out_dir != Path.cwd() and not out_dir.exists(),
                'Training output directory must be a new, nonexistent directory')
        require(str(out_dir).startswith('/train-output/'),
                'Output directory must be under explicitly mounted /train-output')
    else:
        require(args.output_dir is None, 'Do not specify output path for validation')
        out_dir = Path('/tmp/e003_dpo_release_validation_only')

    print('=== E003 DPO109 {} ==='.format('AUTHORIZED TRAINING' if training else 'VALIDATION ONLY'), flush=True)
    for package, expected in [
        ('torch', '2.14.0+cu126'), ('trl', '0.26.2'), ('transformers', '4.57.6'),
        ('peft', '0.18.1'), ('accelerate', '1.12.0'), ('datasets', '4.0.0'),
    ]:
        actual = version(package)
        require(actual == expected, f'{package} expected {expected}, found {actual}')
    require(torch.cuda.is_available() and torch.cuda.get_device_capability(0) == (7, 0),
            'Expected CUDA V100 (sm_70)')
    require(not torch.backends.python_native.triton.enabled, 'Native Triton routing must be disabled')
    print('GPU:', torch.cuda.get_device_name(0), flush=True)
    print('Torch native Triton disabled: VERIFIED; attention=eager; FP16')

    pairs = check_artifacts()
    set_seed(SEED)
    tok = AutoTokenizer.from_pretrained(BASE, revision=BASE_REVISION, local_files_only=True)
    require(tok.pad_token_id == EOS_ID, 'Unexpected native EOS/PAD ID')
    require(tok.convert_tokens_to_ids('<|im_end|>') == 151645, 'Unexpected shipped EOS')
    tok.eos_token = tok.convert_ids_to_tokens(EOS_ID)
    require(tok.eos_token_id == EOS_ID, 'TRL EOS ID must be native 151643')

    base = AutoModelForCausalLM.from_pretrained(
        BASE, revision=BASE_REVISION, local_files_only=True,
        dtype=torch.float16, attn_implementation='eager').to('cuda')
    base.config.use_cache = False  # DPO ONLY. Generation/evaluation cache must be True.
    model = PeftModel.from_pretrained(base, str(ADAPTER_DIR),
                                     adapter_name='policy', is_trainable=True)
    model.load_adapter(str(ADAPTER_DIR), adapter_name='reference', is_trainable=False)
    saved = load_file(str(ADAPTER_DIR / 'adapter_model.safetensors'), device='cpu')
    pol = state(model, 'policy')
    require(len(saved) == 224 and saved.keys() == pol.keys(), 'E002a policy tensor schema mismatch')
    require(all(torch.equal(saved[k], pol[k].detach().cpu()) for k in saved),
            'Loaded policy differs from original E002a checkpoint')
    # PEFT extra adapter goes through a temporary FP16 cast on this tested stack.
    set_peft_model_state_dict(model, saved.copy(), adapter_name='reference')
    ref = state(model, 'reference')
    require(all(torch.equal(pol[k].detach().cpu(), ref[k].detach().cpu()) for k in saved),
            'Loaded reference not exactly equal to E002a policy')
    model.set_adapter('policy')
    trainable_policy = [(n, p) for n, p in model.named_parameters() if '.policy.' in n]
    frozen_ref = [(n, p) for n, p in model.named_parameters() if '.reference.' in n]
    require(trainable_policy and frozen_ref, 'Named PEFT adapters missing')
    require(all(p.requires_grad for _, p in trainable_policy), 'Policy LoRA is not trainable')
    require(all(not p.requires_grad for _, p in frozen_ref), 'Reference adapter must be frozen')
    require(all(not p.requires_grad for n, p in model.named_parameters()
                if '.policy.' not in n and '.reference.' not in n), 'Base model must be frozen')

    config = build_config(str(out_dir))
    require(config.model_adapter_name == 'policy' and config.ref_adapter_name == 'reference',
            'Explicit reference routing missing')
    trainer = DPOTrainer(model=model, ref_model=None, peft_config=None,
                         args=config, processing_class=tok,
                         train_dataset=Dataset.from_list(pairs))
    require(trainer.is_peft_model and trainer.ref_model is None, 'Unexpected separate base reference')
    require(trainer.model_adapter_name == 'policy' and trainer.ref_adapter_name == 'reference',
            'TRL adapter mapping mismatch')
    require(len(trainer.train_dataset) == N_PAIRS, 'TRL lost approved rows')
    for row in trainer.train_dataset:
        require(row['chosen_input_ids'][-1] == EOS_ID and row['rejected_input_ids'][-1] == EOS_ID,
                'TRL native EOS mismatch')
        p, c, r = (len(row[k + '_input_ids']) for k in ('prompt', 'chosen', 'rejected'))
        require(p <= MAX_PROMPT_LENGTH and c <= MAX_COMPLETION_LENGTH and
                r <= MAX_COMPLETION_LENGTH and p + max(c, r) <= MAX_LENGTH,
                'Unexpected truncation or sequence limit')
    steps = math.ceil(N_PAIRS / (BATCH_SIZE * ACCUMULATION)) * EPOCHS
    require(steps == 14, 'Optimizer step estimate drift')
    print(f'DPO config: beta={BETA}; LR={LR}; epochs={EPOCHS}; effective batch=8; planned steps={steps}')
    print('Signed rows + native EOS + reference routing + weights: PASS')

    if not training:
        require(trainer.optimizer is None and trainer.state.global_step == 0,
                'Validation must not create optimizer or train')
        batch = trainer.data_collator([trainer.train_dataset[0]])
        for side in ('chosen', 'rejected'):
            require(batch[f'{side}_input_ids'][0, -1].item() == EOS_ID and
                    batch[f'{side}_attention_mask'][0, -1].item() == 1,
                    'EOS collator mask mismatch')
        batch = {k: v.to('cuda') for k, v in batch.items()}
        trainer.model.eval()
        with torch.inference_mode():
            trainer.model.set_adapter('policy')
            scores = trainer.concatenated_forward(trainer.model, batch)
            ref_chosen, ref_rejected = trainer.compute_ref_log_probs(batch)
            require(trainer.model.active_adapter == 'policy', 'TRL did not restore policy')
            gaps = [(scores[k] - v).abs().max().item() for k, v in
                    (('chosen_logps', ref_chosen), ('rejected_logps', ref_rejected))]
            require(max(gaps) <= 0.02, f'Policy-reference logp gap: {gaps}')
            losses, _, _ = trainer.dpo_loss(scores['chosen_logps'], scores['rejected_logps'],
                                            ref_chosen, ref_rejected,
                                            loss_type='sigmoid', model_output=scores)
            loss = losses.mean().item()
            require(abs(loss - math.log(2)) < 0.01, f'Initial DPO loss mismatch: {loss}')
        require(trainer.optimizer is None and trainer.state.global_step == 0,
                'Validation unexpectedly advanced training')
        require(all(torch.equal(saved[k], state(model, 'policy')[k].detach().cpu()) for k in saved),
                'Policy changed during validation')
        print('Initial no-gradient DPO loss:', round(loss, 6))
        print('Peak preflight GPU allocation MiB:', round(torch.cuda.max_memory_allocated() / 2**20, 1))
        print('Training memory: NOT MEASURED; assess upon separately approved run')
        print('KV cache: OFF for DPO; MUST BE ON for generation/evaluation')
        print('Training authorized: NO; performed: NO')
        print('E003 DPO RELEASE VALIDATION: PASSED')
        return

    # This branch is intentionally unreachable during validation. The user must
    # separately authorize actual training and supply both CLI and env gates.
    require(trainer.state.global_step == 0 and trainer.optimizer is None,
            'Unexpected trainer state before start')
    require(model.base_model.model.config.use_cache is False, 'DPO cache must stay disabled')
    print('EXPLICITLY AUTHORIZED: STARTING 1 EPOCH / APPROX 14 OPTIMIZER STEPS', flush=True)
    result = trainer.train()
    require(trainer.state.global_step == steps,
            f'Expected {steps} optimizer steps, got {trainer.state.global_step}')
    final_dir = out_dir / 'final_policy_adapter'
    model.set_adapter('policy')
    model.save_pretrained(str(final_dir), selected_adapters=['policy'], safe_serialization=True)
    tok.save_pretrained(str(out_dir / 'tokenizer_native_eos'))
    trainer.save_state()
    info = {
        'experiment': 'E003', 'source_pairs_sha256': PAIRS_SHA256,
        'source_adapter_dir': str(ADAPTER_DIR), 'base_revision': BASE_REVISION,
        'steps': trainer.state.global_step, 'train_loss': result.training_loss,
        'native_eos_id': EOS_ID, 'generation_use_cache': True,
        'training_use_cache': False, 'seed': SEED,
    }
    (out_dir / 'e003_training_summary.json').write_text(json.dumps(info, indent=2) + '\n')
    print('E003 DPO TRAINING COMPLETE; outputs:', out_dir, flush=True)


if __name__ == '__main__':
    main()
