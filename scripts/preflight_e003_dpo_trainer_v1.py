#!/usr/bin/env python3
"""E003 signed-109 actual TRL 0.26.2 trainer initialization + no-gradient loss preflight.

This script NEVER calls train(), backward(), step(), save_model(), or save_state().
The proposed DPOConfig values are PRELIMINARY and NOT training authorization.
"""
from __future__ import annotations

import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import torch

# The V100-safe backend already used for E002a training and evaluation.
torch.backends.python_native.triton.enabled = False
torch.backends.cudnn.benchmark = False

from datasets import Dataset
from peft import PeftModel, get_peft_model_state_dict
from peft.utils.save_and_load import set_peft_model_state_dict
from safetensors.torch import load_file
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer

MODEL = 'Qwen/Qwen3-0.6B-Base'
REV = '57ca99e94acb83175495aa2c6b6b0cc498170924'
PAIR_SHA = '7d088bd70dc1d3d8b05f251a5560b37aca24a064ec7c4c81c91a03b8d84dc8e9'
ADAPTER = Path('data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter')
PAIRS = Path('data/preference_runs/e003_dpo_signed109_staged_277c863_v1/pairs_staged.jsonl')
EOS_ID = 151643


def check(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def weights(model, name):
    return get_peft_model_state_dict(model, adapter_name=name, save_embedding_layers=False)


def main():
    print('=== E003 DPO109 TRL TRAINER PREFLIGHT: NO TRAINING ===', flush=True)
    for pkg, want in [('trl', '0.26.2'), ('transformers', '4.57.6'), ('peft', '0.18.1')]:
        check(version(pkg) == want, f'{pkg} must be {want}; found {version(pkg)}')
    check(torch.cuda.is_available() and torch.cuda.get_device_capability(0) == (7, 0),
          'Expected Tesla V100 sm_70')
    check(torch.backends.python_native.triton.enabled is False, 'Triton override not disabled')
    check(PAIRS.is_file(), 'Signed staged pairs not found')
    check(hashlib.sha256(PAIRS.read_bytes()).hexdigest() == PAIR_SHA, 'Pair digest drift')
    pairs = [json.loads(row) for row in PAIRS.read_text().splitlines()]
    check(len(pairs) == 109, 'Expected 109 pairs')
    check(all(set(p) == {'prompt', 'chosen', 'rejected'} for p in pairs), 'Pair schema drift')
    check(ADAPTER.joinpath('adapter_model.safetensors').is_file(), 'Adapter absent')
    print('GPU:', torch.cuda.get_device_name(0), flush=True)
    print('Pair SHA256: VERIFIED; approved pair count: 109', flush=True)

    tok = AutoTokenizer.from_pretrained(MODEL, revision=REV, local_files_only=True)
    check(tok.pad_token_id == EOS_ID, 'Unexpected padding ID')
    check(tok.convert_tokens_to_ids('<|im_end|>') == 151645, 'Unexpected shipped EOS')
    tok.eos_token = tok.convert_ids_to_tokens(EOS_ID)
    check(tok.eos_token_id == EOS_ID, 'Native 151643 EOS not set')

    base = AutoModelForCausalLM.from_pretrained(
        MODEL, revision=REV, local_files_only=True,
        dtype=torch.float16, attn_implementation='eager').to('cuda')
    base.config.use_cache = False  # DPO optimization only; generation/eval uses True.
    model = PeftModel.from_pretrained(base, str(ADAPTER), adapter_name='policy', is_trainable=True)
    model.load_adapter(str(ADAPTER), adapter_name='reference', is_trainable=False)

    saved = load_file(str(ADAPTER / 'adapter_model.safetensors'), device='cpu')
    before = weights(model, 'policy')
    check(len(saved) == 224 and saved.keys() == before.keys(), 'E002a tensors differ')
    check(all(torch.equal(saved[k], before[k].cpu()) for k in saved), 'Policy != E002a checkpoint')
    # PEFT loads additional adapters through an FP16 temporary path on this stack.
    # Restore the exact saved FP32 weights to the reference, in memory.
    set_peft_model_state_dict(model, saved.copy(), adapter_name='reference')
    after = weights(model, 'reference')
    check(all(torch.equal(before[k].cpu(), after[k].cpu()) for k in saved),
          'Reference != policy after precision restoration')
    model.set_adapter('policy')
    policy_trainable = [(n, p) for n, p in model.named_parameters() if '.policy.' in n]
    reference_params = [(n, p) for n, p in model.named_parameters() if '.reference.' in n]
    check(policy_trainable and reference_params, 'LoRA adapters not found in named parameters')
    check(all(p.requires_grad for _, p in policy_trainable), 'Policy adapter not trainable')
    check(all(not p.requires_grad for _, p in reference_params), 'Reference not frozen')
    check(all(not p.requires_grad for n, p in model.named_parameters()
              if '.policy.' not in n and '.reference.' not in n), 'Base model unexpectedly trainable')
    print('E002a policy/reference: 224/224 exact FP32 tensors; policy trainable, reference frozen')

    # Representative config for trainer integration ONLY. No hyperparameters frozen.
    args = DPOConfig(
        output_dir='/tmp/e003_dpo_preflight_only',
        model_adapter_name='policy', ref_adapter_name='reference',
        fp16=True, bf16=False, gradient_checkpointing=True,
        per_device_train_batch_size=1, gradient_accumulation_steps=8,
        learning_rate=1e-6, num_train_epochs=1,
        beta=0.1, loss_type='sigmoid', label_smoothing=0.0,
        max_length=1024, max_prompt_length=512, max_completion_length=512,
        padding_free=False, precompute_ref_log_probs=False,
        reference_free=False, sync_ref_model=False,
        save_strategy='no', eval_strategy='no', logging_strategy='no',
        report_to='none', dataloader_num_workers=0, dataset_num_proc=None,
        remove_unused_columns=False, seed=42,
    )
    check(args.model_adapter_name == 'policy' and args.ref_adapter_name == 'reference',
          'TRL adapter mapping drift')
    check(args.fp16 and not args.bf16 and not args.padding_free, 'V100 config drift')

    trainer = DPOTrainer(
        model=model, ref_model=None, peft_config=None, args=args,
        processing_class=tok, train_dataset=Dataset.from_list(pairs),
    )
    check(trainer.is_peft_model and trainer.ref_model is None, 'TRL reference model mode drift')
    check(trainer.model_adapter_name == 'policy' and trainer.ref_adapter_name == 'reference',
          'TRL trainer adapter routing drift')
    check(len(trainer.train_dataset) == 109, 'TRL tokenization lost rows')
    check(trainer.optimizer is None and trainer.state.global_step == 0,
          'An optimizer or training step appeared unexpectedly')
    for row in trainer.train_dataset:
        check(row['chosen_input_ids'][-1] == EOS_ID and row['rejected_input_ids'][-1] == EOS_ID,
              'TRL inserted wrong completion EOS')
        check(len(row['prompt_input_ids']) <= 512 and len(row['chosen_input_ids']) <= 512 and
              len(row['rejected_input_ids']) <= 512, 'Token truncation/limits invalid')
    print('TRL trainer initialization: PASS; 109 native-EOS rows, no optimizer')

    batch = trainer.data_collator([trainer.train_dataset[0]])
    for choice in ('chosen', 'rejected'):
        check(batch[f'{choice}_input_ids'][0, -1].item() == EOS_ID, 'Collator EOS lost')
        check(batch[f'{choice}_attention_mask'][0, -1].item() == 1, 'Collator EOS masked')
    batch = {name: value.to('cuda') for name, value in batch.items()}
    trainer.model.eval()  # no dropout or gradients; this is ONLY an inference/loss check.
    with torch.inference_mode():
        trainer.model.set_adapter('policy')
        policy_out = trainer.concatenated_forward(trainer.model, batch)
        ref_chosen, ref_rejected = trainer.compute_ref_log_probs(batch)
        check(trainer.model.active_adapter == 'policy', 'TRL did not restore policy after ref pass')
        gap_chosen = (policy_out['chosen_logps'] - ref_chosen).abs().max().item()
        gap_rejected = (policy_out['rejected_logps'] - ref_rejected).abs().max().item()
        check(max(gap_chosen, gap_rejected) <= 0.02,
              f'TRL preference log-prob discrepancy {gap_chosen}, {gap_rejected}')
        losses, _, _ = trainer.dpo_loss(
            policy_out['chosen_logps'], policy_out['rejected_logps'],
            ref_chosen, ref_rejected, loss_type='sigmoid', model_output=policy_out)
        loss = losses.mean().item()
        check(abs(loss - 0.69314718056) < 0.01, f'Initial DPO loss should be log(2), got {loss}')
    check(trainer.state.global_step == 0 and trainer.optimizer is None, 'Optimization was initiated')
    check(all(torch.equal(saved[k], weights(model, 'policy')[k].cpu()) for k in saved),
          'Preflight unexpectedly modified the policy')
    check(all(torch.equal(saved[k], weights(model, 'reference')[k].cpu()) for k in saved),
          'Preflight unexpectedly modified the reference')
    check(all(not p.requires_grad for _, p in reference_params), 'Reference is not frozen after ref pass')
    print(f'TRL chosen/rejected policy-ref logp gaps: {gap_chosen:.6g}, {gap_rejected:.6g}')
    print(f'Initial sigmoid DPO loss: {loss:.6f} (expected ln(2))')
    print('Reference routing + weight integrity + frozen reference: PASS')
    print('Peak allocated VRAM (MiB):', round(torch.cuda.max_memory_allocated() / 1024**2, 1))
    print('DPO hyperparameters: CANDIDATE ONLY; NOT FROZEN')
    print('Generation/evaluation KV cache: MUST BE ON; DPO cache: OFF')
    print('Training authorized: NO; training performed: NO')
    print('E003 TRL TRAINER PREFLIGHT: PASSED (TRAINING-MEMORY AND CONFIG FREEZE PENDING)')


if __name__ == '__main__':
    main()
