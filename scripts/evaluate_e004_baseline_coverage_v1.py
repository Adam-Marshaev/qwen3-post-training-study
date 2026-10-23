"""E004-P1 E002a in-sample greedy baseline coverage diagnostic (inference only).

Read-only on the existing E004 candidate generation corpus and GSM8K source.
Writes separate immutable per-question inference checkpoints in the supplied
output directory. Does not evaluate, read, or train on GSM8K official test.
Frozen validation is not read. GPU used only without --preflight-only.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from time import perf_counter

SOURCE = Path('data/raw/gsm8k/train.jsonl')
MANIFEST = Path('configs/data/gsm8k_split_v1.json')
ADAPTER = Path('data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter')
RUN_DIR = Path('data/preference_runs/e004_p1_250_k4_fc6d484_v1')
CODE_REV_E004_GENERATOR = 'fc6d48475f018c1a26d98d81694c8b6fbc31b815'
CONFIG_SHA = '3bf70dedbb024536d715b08d8ee5e28b8f07e2d3c07166fcd25d5272f458a1d6'
CANDIDATES_SHA = '314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628'
ADAPTER_SHA = 'f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625'
SOURCE_SHA = '17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465'
MANIFEST_SHA = '31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719'
DOCKER_SHA = 'sha256:e6248de1867ccb6aae297a49228532721014f16888b126b8532705e0d9e8ee0e'
MODEL_REV = '57ca99e94acb83175495aa2c6b6b0cc498170924'
NATIVE_EOS = 151643
MAX_TOKENS = 512
CHECK_NAME = 'e004_p1_e002a_greedy250_coverage_v1'


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def bytes_json(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def write_immutable(path, raw):
    """Atomically create a new artifact without ever overwriting an existing one."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.incomplete_', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.link(temporary, path)   # fails if destination exists
        dirfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def is_mixed(group):
    valid = [r for r in group if r['eligible'] is True]
    return any(r['correct'] is True for r in valid) and any(r['correct'] is False for r in valid)


def validate_selection(metadata, summary, candidates, training, *, prompt_func):
    """Require full membership in the TRAINING split and exact source data."""
    require(metadata['selected_source_indices'] == sorted(metadata['selected_source_indices']),
            'Selected source indices not sorted')
    selected = metadata['selected_source_indices']
    require(len(selected) == 250 and len(set(selected)) == 250, 'Selection invalid')
    require(metadata['code_revision'] == CODE_REV_E004_GENERATOR, 'E004 generation Git revision mismatch')
    require(metadata['config_sha256'] == CONFIG_SHA, 'E004 generation config mismatch')
    require(summary['candidates_sha256'] == CANDIDATES_SHA and
            summary['code_revision'] == CODE_REV_E004_GENERATOR and
            summary['config_sha256'] == CONFIG_SHA and
            summary['reference_policy_adapter_sha256'] == ADAPTER_SHA and
            summary['training_performed'] is False and
            summary['official_test_used'] is False and
            summary['pilot_questions'] == 250 and
            summary['candidates'] == 1000 and
            summary['mixed_groups_with_potential_pair'] == 135,
            'E004 summary mismatch')
    require(len(training) == 6726, 'Frozen training partition size mismatch')
    train_by_id = {r.source_index: r for r in training}
    require(len(train_by_id) == 6726, 'Duplicate source indices in training split')
    require(set(selected) <= set(train_by_id), 'E004 selected a non-training source')
    by_id = defaultdict(list)
    require(len(candidates) == 1000, 'E004 candidate file count mismatch')
    for r in candidates:
        require(r['source_index'] in selected, 'Candidate outside E004 selection')
        by_id[r['source_index']].append(r)
    require(set(by_id) == set(selected), 'Candidate groups incomplete')
    for i in selected:
        rows = by_id[i]
        require(len(rows) == 4 and sorted(r['sample_index'] for r in rows) == list(range(4)),
                f'Bad four-sample group: {i}')
        correct_prompt = prompt_func(train_by_id[i].question)
        for row in rows:
            require(row['prompt'] == correct_prompt, f'Prompt mismatch: {i}')
            require(str(row['reference_answer']) == str(train_by_id[i].reference_answer),
                    f'Reference mismatch: {i}')
    mixed = {i for i in selected if is_mixed(by_id[i])}
    require(len(mixed) == 135, 'Mixed-group count mismatch')
    return selected, train_by_id, mixed, by_id


def report_rows(predictions, selected, mixed):
    """Pure function; no model import needed. All 250 must be present."""
    require(len(predictions) == 250 and len(set(predictions)) == 250, 'Prediction count/uniqueness wrong')
    require(set(predictions) == set(selected), 'Prediction index set mismatch')
    def totals(index_set):
        correct = sum(predictions[i]['correct'] is True for i in index_set)
        wrong = len(index_set) - correct
        return {'total':len(index_set), 'correct':correct, 'wrong':wrong,
                'accuracy':round(correct / len(index_set), 10)}
    nonmixed = set(selected) - mixed
    require(len(nonmixed) == 115, 'Expected 115 nonmixed source questions')
    all_stats, mixed_stats, other_stats = totals(selected), totals(mixed), totals(nonmixed)
    return {
        'all_250': all_stats,
        'mixed_135': mixed_stats,
        'nonmixed_115': other_stats,
        'mixed_share_of_all_baseline_errors': (
            round(mixed_stats['wrong'] / all_stats['wrong'], 10) if all_stats['wrong'] else None
        ),
        'error_rate_mixed_minus_nonmixed': round(
            mixed_stats['wrong']/135 - other_stats['wrong']/115, 10
        ),
        'contingency': {
            'mixed_baseline_wrong': mixed_stats['wrong'],
            'mixed_baseline_correct': mixed_stats['correct'],
            'nonmixed_baseline_wrong': other_stats['wrong'],
            'nonmixed_baseline_correct': other_stats['correct'],
        },
    }


def validate_row(row, example, tokenizer):
    from llm_post_training.evaluation.metrics import evaluate_response
    from llm_post_training.evaluation.prompting import format_baseline_prompt
    require(row.get('run_type') == CHECK_NAME, 'Checkpoint run type mismatch')
    require(row.get('source_index') == example.source_index, 'Checkpoint source mismatch')
    require(row.get('question') == example.question, 'Checkpoint question mismatch')
    require(row.get('prompt') == format_baseline_prompt(example.question), 'Checkpoint prompt mismatch')
    require(row.get('reference_answer') == str(example.reference_answer), 'Reference mismatch')
    ids = row.get('generated_token_ids')
    require(isinstance(ids,list) and 1 <= len(ids) <= MAX_TOKENS and
            all(type(x) == int and 0 <= x < len(tokenizer) for x in ids), 'Token IDs invalid')
    require(row.get('generated_tokens') == len(ids), 'Token count mismatch')
    require(row.get('reached_token_cap') is (len(ids) == MAX_TOKENS), 'Token cap mismatch')
    require(row.get('native_eos_stop') is (ids[-1] == NATIVE_EOS), 'EOS mismatch')
    text = tokenizer.decode(ids, skip_special_tokens=True)
    require(row.get('raw_response') == text, 'Decoded response mismatch')
    judged = evaluate_response(response=text, expected_answer=example.reference_answer,
                               generated_tokens=len(ids), reached_token_cap=len(ids) == MAX_TOKENS)
    require(row.get('correct') is bool(judged.correct), 'Correctness mismatch')
    require(row.get('extraction_status') == judged.extraction.status, 'Extraction mismatch')
    require(row.get('extracted_answer') == (str(judged.extraction.answer)
            if judged.extraction.answer is not None else None), 'Extracted answer mismatch')
    require(row.get('unwanted_continuation') is bool(judged.extraction.unwanted_continuation),
            'Continuation mismatch')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--code-revision', required=True)
    p.add_argument('--docker-image-id', required=True)
    p.add_argument('--preflight-only', action='store_true')
    p.add_argument('--resume', action='store_true')
    p.add_argument('--stop-after-new', type=int)
    a = p.parse_args()
    require(bool(re.fullmatch('[0-9a-f]{40}', a.code_revision)), '40-char Git revision required')
    require(a.docker_image_id == DOCKER_SHA, 'Historical Docker image ID mismatch')
    require(a.stop_after_new is None or a.stop_after_new > 0, 'Invalid pause count')
    require(not (a.preflight_only and (a.resume or a.stop_after_new)), 'Preflight cannot resume or pause')
    require(sha(SOURCE) == SOURCE_SHA, 'GSM8K training source SHA mismatch')
    require(sha(MANIFEST) == MANIFEST_SHA, 'GSM8K split manifest SHA mismatch')
    require(sha(ADAPTER / 'adapter_model.safetensors') == ADAPTER_SHA, 'E002a adapter SHA mismatch')
    require(sha(RUN_DIR / 'candidates.jsonl') == CANDIDATES_SHA, 'E004 original candidates SHA mismatch')
    from llm_post_training.data.loader import load_gsm8k_split
    from llm_post_training.evaluation.prompting import format_baseline_prompt, BASELINE_PROMPT_VERSION
    from llm_post_training.evaluation.answer_extraction import ANSWER_EXTRACTION_VERSION
    from scripts.evaluate_gsm8k import verify_adapter_checkpoint, INFERENCE_PROTOCOL_VERSION, MODEL_ID, MODEL_REVISION
    require(MODEL_REVISION == MODEL_REV and INFERENCE_PROTOCOL_VERSION == 'gsm8k_val512_greedy_eager_cached_v1',
            'Frozen E002a decoding revision/protocol mismatch')
    provenance = verify_adapter_checkpoint(ADAPTER, ADAPTER_SHA,
                            require_completed_e002=False, native_eos_epoch=2)
    training = load_gsm8k_split(SOURCE, MANIFEST, 'training')
    candidates = [json.loads(x) for x in (RUN_DIR / 'candidates.jsonl').read_text(encoding='utf8').splitlines() if x.strip()]
    meta = read_json(RUN_DIR / 'metadata.json')
    old_summary = read_json(RUN_DIR / 'summary.json')
    indices, by_idx, mixed, by_group = validate_selection(meta, old_summary, candidates, training,
                                                        prompt_func=format_baseline_prompt)
    script_sha = sha(Path(__file__))
    basis = {
        'run_type': CHECK_NAME,
        'analysis_partition': 'frozen_training_in_sample_diagnostic',
        'official_test_used': False, 'validation_evaluated': False,
        'training_performed': False,
        'code_revision': a.code_revision,
        'evaluator_script_sha256': script_sha,
        'docker_image_id': DOCKER_SHA,
        'e004_source_run': str(RUN_DIR),
        'e004_generator_code_revision': CODE_REV_E004_GENERATOR,
        'e004_candidates_sha256': CANDIDATES_SHA,
        'e004_config_sha256': CONFIG_SHA,
        'gsm8k_train_source_sha256': SOURCE_SHA,
        'split_manifest_sha256': MANIFEST_SHA,
        'e002a_adapter_sha256': ADAPTER_SHA,
        'adapter_provenance': provenance,
        'model_id': MODEL_ID,
        'model_revision': MODEL_REV,
        'inference_protocol_version': INFERENCE_PROTOCOL_VERSION,
        'prompt_version': BASELINE_PROMPT_VERSION,
        'answer_extraction_version': ANSWER_EXTRACTION_VERSION,
        'decoding': 'greedy', 'max_new_tokens': MAX_TOKENS, 'use_cache': True,
        'attention_implementation': 'eager', 'precision': 'float16',
        'eos_token_id': NATIVE_EOS, 'pad_token_id': NATIVE_EOS,
        'stop_strings': ['\nQuestion:', '\n[Question]'],
        'selected_source_indices': indices,
        'mixed_source_indices': sorted(mixed),
    }
    if a.preflight_only:
        print('=== E004 BASELINE COVERAGE PREFLIGHT PASSED ===')
        print('Selected training questions:', len(indices))
        print('E004 mixed questions:', len(mixed))
        print('E004 nonmixed questions:', len(indices)-len(mixed))
        print('Pinned E002a adapter SHA256:', ADAPTER_SHA)
        print('Input candidates SHA256:', CANDIDATES_SHA)
        print('Greedy decoding: 512 max tokens, cached, eager, native EOS')
        print('GPU inference: NOT STARTED; output created: NO')
        return
    import torch
    import torch.backends.python_native as python_native
    from peft import PeftModel
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from scripts.evaluate_gsm8k import cached_generation_kwargs
    require(torch.cuda.is_available(), 'CUDA required for inference')
    python_native.triton.enabled = False
    output = a.output_dir
    if output.exists():
        require(a.resume, 'Existing output requires explicit --resume')
        require((output/'metadata.json').is_file(), 'Existing output missing metadata')
        require(read_json(output/'metadata.json') == basis, 'Run metadata mismatch; refusing resume')
        require(not (output/'summary.json').exists(), 'Completed run must not resume')
        require(not (output/'predictions.jsonl').exists(), 'Final predictions already exist')
    else:
        require(not a.resume, 'Cannot resume a non-existing run')
        output.mkdir(parents=True, exist_ok=False)
        write_immutable(output/'metadata.json', bytes_json(basis))
    progress = output/'progress'
    progress.mkdir(parents=True, exist_ok=True)
    files = list(progress.glob('source_*.json'))
    require(all(re.fullmatch(r'source_\d{5}\.json', f.name) for f in files), 'Unexpected checkpoint file')
    require(len(files) <= len(indices), 'Too many checkpoints')
    require(set(int(x.stem.split('_')[-1]) for x in files) <= set(indices), 'Unknown checkpoint ID')
    print('Loading frozen E002a tokenizer and policy...', flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV, local_files_only=True)
    require(tokenizer.eos_token_id == 151645 and tokenizer.pad_token_id == 151643, 'Qwen3 tokenizer EOS/PAD mismatch')
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, revision=MODEL_REV, local_files_only=True, dtype=torch.float16,
        attn_implementation='eager', use_safetensors=True,
    ).to('cuda:0')
    require(model.config.eos_token_id == NATIVE_EOS, 'Base model native EOS mismatch')
    model = PeftModel.from_pretrained(model, str(ADAPTER), is_trainable=False, autocast_adapter_dtype=True)
    require(len(model.peft_config) == 1, 'Expected exactly one LoRA adapter')
    model.config.use_cache = True
    model.eval()
    torch.cuda.reset_peak_memory_stats()
    results = {}
    for f in sorted(files):
        row = read_json(f)
        idx = row['source_index']
        require(f.name == f'source_{idx:05d}.json' and idx not in results,
                'Misnamed/duplicate checkpoint')
        validate_row(row, by_idx[idx], tokenizer)
        results[idx] = row
    print(f'Verified existing inference checkpoints: {len(results)}/250', flush=True)
    generated = 0
    for j, idx in enumerate(indices, start=1):
        if idx in results:
            continue
        ex = by_idx[idx]
        prompt = format_baseline_prompt(ex.question)
        inputs = tokenizer(prompt, return_tensors='pt', add_special_tokens=False).to('cuda:0')
        n_inputs = inputs['input_ids'].shape[1]
        torch.cuda.synchronize()
        started = perf_counter()
        with torch.inference_mode():
            output_ids = model.generate(**inputs, **cached_generation_kwargs(MAX_TOKENS, tokenizer))
        torch.cuda.synchronize()
        elapsed = perf_counter() - started
        ids = output_ids[0,n_inputs:].tolist()
        response = tokenizer.decode(ids, skip_special_tokens=True)
        cap = len(ids) == MAX_TOKENS
        from llm_post_training.evaluation.metrics import evaluate_response
        judged = evaluate_response(response=response, expected_answer=ex.reference_answer,
                                   generated_tokens=len(ids), reached_token_cap=cap)
        row = {
            'run_type': CHECK_NAME,
            'source_index': idx,
            'question': ex.question,
            'prompt': prompt,
            'reference_answer': str(ex.reference_answer),
            'raw_response': response,
            'extracted_answer': str(judged.extraction.answer) if judged.extraction.answer is not None else None,
            'extraction_status': judged.extraction.status,
            'correct': bool(judged.correct),
            'unwanted_continuation': bool(judged.extraction.unwanted_continuation),
            'generated_token_ids': ids,
            'generated_tokens': len(ids),
            'reached_token_cap': cap,
            'native_eos_stop': bool(ids) and ids[-1] == NATIVE_EOS,
            'generation_seconds': elapsed,
            'e004_mixed_group': idx in mixed,
            'e004_eligible_correct_count': sum(r['eligible'] and r['correct'] for r in by_group[idx]),
            'e004_eligible_incorrect_count': sum(r['eligible'] and not r['correct'] for r in by_group[idx]),
        }
        validate_row(row, ex, tokenizer)
        write_immutable(progress/f'source_{idx:05d}.json', bytes_json(row))
        results[idx] = row
        generated += 1
        print(f'[{j}/250] source={idx} mixed={idx in mixed} greedy_correct={row["correct"]} '
              f'answer_status={row["extraction_status"]} tokens={len(ids)} cap={cap}', flush=True)
        if a.stop_after_new is not None and generated >= a.stop_after_new:
            print('Engineering pause after immutable checkpoints; use --resume; no final dataset emitted.')
            return
    stats = report_rows(results, indices, mixed)
    ordered = [results[i] for i in indices]
    prediction_lines = b''.join(bytes_json(r) for r in ordered)
    coverage_lines = b''.join(bytes_json({
        'source_index':r['source_index'], 'mixed':r['e004_mixed_group'],
        'greedy_correct':r['correct'], 'extraction_status':r['extraction_status'],
        'eligible_sample_correct':r['e004_eligible_correct_count'],
        'eligible_sample_incorrect':r['e004_eligible_incorrect_count'],
    }) for r in ordered)
    sumdoc = {**basis, 'summary': stats,
              'predictions_sha256': hashlib.sha256(prediction_lines).hexdigest(),
              'coverage_sha256': hashlib.sha256(coverage_lines).hexdigest(),
              'checkpoints': len(results),
              'peak_allocated_vram_mib': torch.cuda.max_memory_allocated()/1024**2}
    # Immutable completion order, summary written last after complete artifacts.
    write_immutable(output/'predictions.jsonl', prediction_lines)
    write_immutable(output/'coverage.jsonl', coverage_lines)
    write_immutable(output/'summary.json', bytes_json(sumdoc))
    print('\n=== E004 P1 E002a GREEDY BASELINE COVERAGE: COMPLETE ===')
    print(json.dumps(stats, indent=2))
    print('Predictions SHA256:', sumdoc['predictions_sha256'])
    print('Coverage SHA256:', sumdoc['coverage_sha256'])
    print('Inference only: YES; training performed: NO')

if __name__ == '__main__':
    main()
