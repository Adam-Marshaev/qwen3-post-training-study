#!/usr/bin/env python3
"""Read-only E003 training-pair preference-margin diagnostic."""
import hashlib
import json
import math
import statistics
from pathlib import Path

import torch
# Must precede loading the model on the V100.
torch.backends.python_native.triton.enabled = False
from datasets import Dataset
from peft import PeftModel
from peft.utils.save_and_load import set_peft_model_state_dict
from safetensors.torch import load_file
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from trl import DPOTrainer

# Import the exact, committed E003 training constants and configuration.
import train_e003_dpo_signed109_v1 as train

E003 = Path('data/train_runs/e003_dpo_signed109_f16e903_v1/final_policy_adapter/policy')
E003_SHA = '10ae46d412f87e39e95891455fd41e7b6d9bd20bd8e9110a304b38d37a09af4a'
E002A_SHA = 'f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def verify_sha(path, digest):
    require(path.is_file(), f'Missing artifact: {path}')
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    require(actual == digest, f'SHA256 mismatch: {path}: {actual}')


def check_weights(model, name, saved):
    actual = train.state(model, name)
    require(len(actual) == len(saved) == 224 and actual.keys() == saved.keys(),
            f'{name}: unexpected adapter tensor keys')
    require(all(torch.equal(actual[k].detach().cpu(), saved[k]) for k in saved),
            f'{name}: adapter not identical to saved FP32 weights')


def main():
    print('=== E003 PREFERENCE LEARNING AUDIT (READ ONLY) ===', flush=True)
    require(torch.cuda.is_available(), 'CUDA GPU required')
    require(torch.cuda.get_device_capability(0) == (7, 0), 'Expected Tesla V100')
    require(not torch.backends.python_native.triton.enabled, 'Triton workaround inactive')
    require(train.BETA == 0.1 and train.N_PAIRS == 109 and train.EOS_ID == 151643,
            'Unexpected E003 training configuration')
    print('GPU:', torch.cuda.get_device_name(0), flush=True)

    pairs = train.check_artifacts()  # 109 rows + pinned signed-pairs SHA256
    verify_sha(train.ADAPTER_DIR / 'adapter_model.safetensors', E002A_SHA)
    verify_sha(E003 / 'adapter_model.safetensors', E003_SHA)
    summary_path = Path('data/train_runs/e003_dpo_signed109_f16e903_v1/e003_training_summary.json')
    state_path = Path('data/train_runs/e003_dpo_signed109_f16e903_v1/trainer_state.json')
    require(summary_path.is_file() and state_path.is_file(), 'Missing training provenance')
    summary, state = json.loads(summary_path.read_text()), json.loads(state_path.read_text())
    require(summary.get('steps') == state.get('global_step') == 14
            and summary.get('source_pairs_sha256') == train.PAIRS_SHA256
            and summary.get('native_eos_id') == train.EOS_ID
            and summary.get('training_use_cache') is False,
            'Training provenance check failed')
    print('109 signed pairs, both adapter SHA256 hashes, 14 steps: VERIFIED', flush=True)

    set_seed(train.SEED)
    tok = AutoTokenizer.from_pretrained(train.BASE, revision=train.BASE_REVISION,
                                        local_files_only=True)
    require(tok.pad_token_id == train.EOS_ID, 'Unexpected tokenizer PAD ID')
    tok.eos_token = tok.convert_ids_to_tokens(train.EOS_ID)
    require(tok.eos_token_id == 151643, 'Native EOS mismatch')

    base = AutoModelForCausalLM.from_pretrained(
        train.BASE, revision=train.BASE_REVISION, local_files_only=True,
        dtype=torch.float16, attn_implementation='eager').to('cuda')
    base.config.use_cache = False   # Teacher-forced scoring, not generation.
    model = PeftModel.from_pretrained(base, str(E003), adapter_name='policy',
                                     is_trainable=False)
    model.load_adapter(str(train.ADAPTER_DIR), adapter_name='reference',
                       is_trainable=False)
    policy_saved = load_file(str(E003 / 'adapter_model.safetensors'), device='cpu')
    ref_saved = load_file(str(train.ADAPTER_DIR / 'adapter_model.safetensors'),
                          device='cpu')
    # Correct PEFT's additional-adapter FP16 rounding issue found in E003.
    set_peft_model_state_dict(model, policy_saved.copy(), adapter_name='policy')
    set_peft_model_state_dict(model, ref_saved.copy(), adapter_name='reference')
    check_weights(model, 'policy', policy_saved)
    check_weights(model, 'reference', ref_saved)
    require(all(not p.requires_grad for p in model.parameters()),
            'Unexpected trainable parameters')
    model.set_adapter('policy')
    model.eval()

    args = train.build_config('/tmp/e003_preference_margin_diagnostic')
    args.gradient_checkpointing = False  # No backward pass.
    args.save_strategy = 'no'
    args.logging_strategy = 'no'
    trainer = DPOTrainer(model=model, ref_model=None, peft_config=None,
                         args=args, processing_class=tok,
                         train_dataset=Dataset.from_list(pairs))
    require(trainer.is_peft_model and trainer.ref_model is None and
            trainer.model_adapter_name == 'policy' and
            trainer.ref_adapter_name == 'reference',
            'Wrong DPO reference routing')
    require(trainer.optimizer is None and trainer.state.global_step == 0,
            'An optimizer or training step unexpectedly appeared')
    require(len(trainer.train_dataset) == 109, 'Preprocessing dropped pairs')
    for row in trainer.train_dataset:
        require(row['chosen_input_ids'][-1] == 151643 and
                row['rejected_input_ids'][-1] == 151643,
                'Completion native EOS missing')
        p, c, r = (len(row[f'{x}_input_ids']) for x in
                   ('prompt', 'chosen', 'rejected'))
        require(p <= 512 and max(c, r) <= 512 and p + max(c, r) <= 1024,
                'Unexpected truncation')
    trainer.model.eval()
    print('Native EOS, TRL tokenization, adapter routing: VERIFIED', flush=True)

    initial_margins, final_margins, deltas, losses = [], [], [], []
    chosen_shifts, rejected_shifts = [], []
    direct_reference_discrepancy = []
    with torch.inference_mode():
        for i, row in enumerate(trainer.train_dataset):
            batch = trainer.data_collator([row])
            batch = {k: v.to('cuda') for k, v in batch.items()}
            trainer.model.set_adapter('policy')
            out = trainer.concatenated_forward(trainer.model, batch)
            ref_c, ref_r = trainer.compute_ref_log_probs(batch)
            require(trainer.model.active_adapter == 'policy',
                    'Reference route failed to restore policy adapter')
            if i < 10:  # Estimate numerical noise in alternative score path.
                trainer.model.set_adapter('reference')
                direct_ref = trainer.concatenated_forward(trainer.model, batch)
                trainer.model.set_adapter('policy')
                direct_reference_discrepancy.extend([
                    abs(float(direct_ref['chosen_logps'].item()) - float(ref_c.item())),
                    abs(float(direct_ref['rejected_logps'].item()) - float(ref_r.item()))])
            pc, pr = float(out['chosen_logps'].item()), float(out['rejected_logps'].item())
            rc, rr = float(ref_c.item()), float(ref_r.item())
            require(all(math.isfinite(v) for v in (pc, pr, rc, rr)),
                    f'Nonfinite sequence logp on pair {i}')
            old, new = rc - rr, pc - pr
            initial_margins.append(old)
            final_margins.append(new)
            deltas.append(new - old)
            chosen_shifts.append(pc - rc)
            rejected_shifts.append(pr - rr)
            loss, _, _ = trainer.dpo_loss(
                out['chosen_logps'], out['rejected_logps'], ref_c, ref_r,
                loss_type='sigmoid', model_output=out)
            losses.append(float(loss.item()))
            if (i + 1) % 10 == 0 or i + 1 == 109:
                print(f'  Scored {i + 1}/109', flush=True)

    require(trainer.optimizer is None and trainer.state.global_step == 0,
            'Unexpected training activity')
    check_weights(model, 'policy', policy_saved)
    check_weights(model, 'reference', ref_saved)
    print('\n=== TRAINING-PAIR PREFERENCE RESULTS ===')
    print(f'E002a mean chosen-minus-rejected logp: {statistics.mean(initial_margins):+.6f}')
    print(f'E003  mean chosen-minus-rejected logp: {statistics.mean(final_margins):+.6f}')
    print(f'Mean margin improvement: {statistics.mean(deltas):+.6f}')
    print(f'Median margin improvement: {statistics.median(deltas):+.6f}')
    print(f'Mean absolute margin shift: {statistics.mean(map(abs, deltas)):.6f}')
    print(f'Min / max margin shift: {min(deltas):+.6f} / {max(deltas):+.6f}')
    print(f'Mean chosen logp shift: {statistics.mean(chosen_shifts):+.6f}')
    print(f'Mean rejected logp shift: {statistics.mean(rejected_shifts):+.6f}')
    print(f'E002a prefers chosen: {sum(v > 0 for v in initial_margins)}/109')
    print(f'E003 prefers chosen: {sum(v > 0 for v in final_margins)}/109')
    print(f'Positive / negative / zero shifts: '
          f'{sum(v > 0 for v in deltas)} / {sum(v < 0 for v in deltas)} / '
          f'{sum(v == 0 for v in deltas)}')
    print(f'Initial loss (identical policy/ref): {math.log(2):.8f}')
    print(f'E003 mean training-pair DPO loss: {statistics.mean(losses):.8f}')
    print(f'Max reference-scoring path discrepancy (10 pairs): '
          f'{max(direct_reference_discrepancy):.6f}')
    print('Training pairs are NOT held-out validation data.')
    print('No optimizer, backward, or checkpoint writes occurred.')
    print('E003 PREFERENCE AUDIT: PASSED', flush=True)


if __name__ == '__main__':
    main()
