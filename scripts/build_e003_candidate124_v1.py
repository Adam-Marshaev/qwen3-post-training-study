#!/usr/bin/env python3
"""E003 preference CANDIDATE preview: 123 advisory pairs + 1 approved exception.

CPU/stdlib only. Never starts training and never signs off the full dataset.
Frozen inputs are verified by the separately pinned consolidated auditor.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

SCHEMA = 'e003_dpo_preference_candidate124_v1'
SOURCE_RAW = 'data/raw/gsm8k/train.jsonl'
SPLIT = 'configs/data/gsm8k_split_v1.json'
SOURCE_SHA = '17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465'
SPLIT_SHA = '31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719'
AUDITOR_SHA = '4b5ba849d4edf47cf6cf56d86f2d80a7f10aa13a9d232fecbe2703a727d9160e'
CANDIDATE_SHA = '3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4'
NATIVE_EOS = 151643
HOLDS = {303,744,1293,1512,1651,2272,2515,3631,4151,4456,
         4949,5064,5599,5656,5775,5851,5870,5994,6417,7304,7340}
UNRESOLVED_GROUP_ONLY = 2320
EXCEPTION_SOURCE = 5436


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def json_read(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def jsonl_read(path: Path) -> list[dict]:
    lines = path.read_text(encoding='utf-8').splitlines()
    require(all(line.strip() for line in lines), f'Blank JSONL entry: {path}')
    return [json.loads(line) for line in lines]


def canonical_json(obj: dict) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode('utf-8')


def canonical_jsonl(rows: list[dict]) -> bytes:
    return ''.join(json.dumps(row, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n'
                   for row in rows).encode('utf-8')


def check_candidate(rec: dict, source: int, sample: int, *, original_correct: bool | None) -> None:
    require(type(rec.get('source_index')) is int and rec['source_index'] == source,
            f'Wrong candidate source: {source}/{sample}')
    require(type(rec.get('sample_index')) is int and rec['sample_index'] == sample,
            f'Wrong candidate sample: {source}/{sample}')
    require(rec.get('sample_seed') == 42 + source * 100 + sample,
            f'Wrong candidate RNG seed: {source}/{sample}')
    require(rec.get('eligible') is True and rec.get('native_eos_stop') is True,
            f'Ineligible or nonnative EOS: {source}/{sample}')
    require(rec.get('reached_token_cap') is False,
            f'Token cap reached: {source}/{sample}')
    require(rec.get('extraction_status') == 'valid'
            and rec.get('unwanted_continuation') is False,
            f'Invalid answer extraction: {source}/{sample}')
    require(isinstance(rec.get('response'), str) and 'the answer is' in rec['response'].lower(),
            f'Bad response: {source}/{sample}')
    require(isinstance(rec.get('prompt'), str) and bool(rec['prompt']),
            f'Bad prompt: {source}/{sample}')
    ids = rec.get('generated_token_ids')
    require(type(ids) is list and all(type(x) is int for x in ids)
            and 0 < len(ids) < 256 and ids[-1] == NATIVE_EOS,
            f'Native EOS IDs missing: {source}/{sample}')
    require(rec.get('generated_tokens') == len(ids),
            f'Token count mismatch: {source}/{sample}')
    if original_correct is not None:
        require(rec.get('correct') is original_correct,
                f'Original correctness mismatch: {source}/{sample}')


def make_pair(source: int, chosen: dict, rejected: dict, *, review_status: str,
              review_source: str, approved_pair: bool, original_reference: str,
              training_reference: str, expected_gap: int | None) -> dict:
    chosen_id, rejected_id = chosen['sample_index'], rejected['sample_index']
    require(chosen_id != rejected_id, f'Same chosen/rejected: {source}')
    require(chosen['prompt'] == rejected['prompt'], f'Prompt mismatch: {source}')
    check_candidate(chosen, source, chosen_id, original_correct=(True if source != 5436 else False))
    check_candidate(rejected, source, rejected_id, original_correct=(False if source != 5436 else True))
    gap = abs(chosen['generated_tokens'] - rejected['generated_tokens'])
    if expected_gap is not None:
        require(gap == expected_gap, f'Token-gap mismatch: {source}')
    # These strings are EXACT copied model outputs. Their token ID arrays already
    # contain native EOS, but skip-special-token decoded text does not: do not
    # append an EOS here; this is a review preview, not a trainer's token stream.
    return {
        'schema': SCHEMA + '_pair',
        'source_index': source,
        'prompt': chosen['prompt'],
        'chosen': chosen['response'],
        'rejected': rejected['response'],
        'chosen_sample_index': chosen_id,
        'rejected_sample_index': rejected_id,
        'chosen_generated_token_ids': chosen['generated_token_ids'],
        'rejected_generated_token_ids': rejected['generated_token_ids'],
        'chosen_generated_tokens': chosen['generated_tokens'],
        'rejected_generated_tokens': rejected['generated_tokens'],
        'absolute_token_gap': gap,
        'native_eos_token_id': NATIVE_EOS,
        'original_reference_answer': original_reference,
        'training_reference_answer': training_reference,
        'reference_training_only_erratum': source == 5436,
        'pair_review_status': review_status,
        'review_source': review_source,
        'independent_pair_signoff': approved_pair,
        'full_dataset_approved': False,
        'training_authorized': False,
        'training_performed': False,
        'official_test_used': False,
    }


def build_pairs(root: Path, audit_module):
    original_path = root / 'data/preference_runs/e003_scale256_k4_v1/candidates.jsonl'
    require(sha(original_path) == CANDIDATE_SHA, 'Frozen candidates SHA mismatch')
    originals = jsonl_read(original_path)
    require(len(originals) == 1024, 'Expected 1024 candidates')
    lookup = {(r['source_index'], r['sample_index']): r for r in originals}
    require(len(lookup) == len(originals), 'Duplicate candidate identity')

    screen_paths = [audit_module.REVIEW24] + [
        f'configs/preference/e003_batch{i:02d}_reasoning_screen_advisory_v1.json'
        for i in range(7)]
    require(len(screen_paths) == 8, 'Expected eight review manifests')
    screens = [json_read(root / name) for name in screen_paths]
    proposals = []
    without_pair = set()
    all_sources = set()
    gap_warnings = []
    for path, screen in zip(screen_paths, screens):
        require(screen['independent_human_signoff'] is False and
                screen['training_approved'] is False and
                screen['training_performed'] is False and
                screen['official_test_used'] is False,
                f'Unexpected screen permissions: {path}')
        for group in screen['groups']:
            source = group['source_index']
            require(source not in all_sources, f'Duplicate reviewed source: {source}')
            all_sources.add(source)
            p = group['advisory_pair_proposal']
            if p is None:
                without_pair.add(source)
                continue
            require(source not in HOLDS | {UNRESOLVED_GROUP_ONLY, EXCEPTION_SOURCE},
                    f'Unexpected pair proposal for restricted source: {source}')
            chosen_idx, rejected_idx = p['chosen_sample_index'], p['rejected_sample_index']
            by_sample = {s['sample_index']: s for s in group['samples']}
            chosen_meta, rejected_meta = by_sample[chosen_idx], by_sample[rejected_idx]
            require(chosen_meta['reasoning_verdict'] == 'SOUND'
                    and rejected_meta['reasoning_verdict'] == 'FLAWED',
                    f'Advisory reasoning not sound/flawed: {source}')
            require(chosen_meta.get('answer_matches_original_reference',
                                    chosen_meta.get('answer_matches_reference')) is True,
                    f'Chosen not answer-correct: {source}')
            require(rejected_meta.get('answer_matches_original_reference',
                                      rejected_meta.get('answer_matches_reference')) is False,
                    f'Rejected not answer-incorrect: {source}')
            chosen, rejected = lookup[(source,chosen_idx)], lookup[(source,rejected_idx)]
            require(chosen['reference_answer'] == rejected['reference_answer'],
                    f'Original reference mismatch: {source}')
            proposals.append(make_pair(
                source, chosen, rejected,
                review_status='ADVISORY_NOT_INDEPENDENTLY_APPROVED',
                review_source=path,
                approved_pair=False,
                original_reference=str(chosen['reference_answer']),
                training_reference=str(chosen['reference_answer']),
                expected_gap=p['absolute_token_length_gap'],
            ))
            gap = p['absolute_token_length_gap']
            if gap > 40:
                gap_warnings.append({'source_index':source,'absolute_token_gap':gap})
    require(len(all_sources) == 146, 'Expected all 146 mixed source groups')
    require(len(proposals) == 123, 'Expected 123 standard advisory pairs')
    require(without_pair == HOLDS | {UNRESOLVED_GROUP_ONLY, EXCEPTION_SOURCE},
            f'Unexpected no-pair groups: {sorted(without_pair)}')

    derivative_rel = 'data/preference_runs/e003_reference_erratum_5436_v1/regraded_candidates.jsonl'
    derivative_rows = jsonl_read(root / derivative_rel)
    require(len(derivative_rows) == 4 and
            [r['sample_index'] for r in derivative_rows] == [0,1,2,3],
            'Bad source 5436 derivative record set')
    for derived in derivative_rows:
        idx = derived['sample_index']
        require(derived['source_index'] == EXCEPTION_SOURCE, 'Derivative source mismatch')
        require(derived['original_candidate'] == lookup[(EXCEPTION_SOURCE, idx)],
                f'Derivative altered original candidate {idx}')
        require(derived['approved_training_only_reference_answer'] == '50',
                'Derivative changed approved reference')
        require(derived['corrected_correct'] is (idx == 2),
                'Derived correctness mismatch')
        require(derived['original_candidate']['reference_answer'] == '55',
                'Wrong original reference for exception')
        require(derived['pair_approved'] is False and derived['training_approved'] is False,
                'Derivative falsely asserts pair approval')
    exception = make_pair(
        EXCEPTION_SOURCE, derivative_rows[2]['original_candidate'],
        derivative_rows[0]['original_candidate'],
        review_status='INDEPENDENTLY_APPROVED_EXCEPTION_PAIR_ONLY',
        review_source='configs/preference/e003_source5436_pair_approval_v1.json',
        approved_pair=True,
        original_reference='55', training_reference='50', expected_gap=28,
    )
    require(exception['chosen_sample_index'] == 2 and exception['rejected_sample_index'] == 0,
            'Incorrect exception pair')
    proposals.append(exception)
    proposals.sort(key=lambda row: row['source_index'])
    require(len(proposals) == 124 and
            len({p['source_index'] for p in proposals}) == 124 and
            all(p['source_index'] not in HOLDS | {UNRESOLVED_GROUP_ONLY} for p in proposals),
            'Bad final proposal population')
    require(sum(bool(p['independent_pair_signoff']) for p in proposals) == 1,
            'Unexpected human pair signoff count')
    require(len(gap_warnings) == 11, 'Expected 11 token gaps >40')
    return proposals, sorted(gap_warnings, key=lambda r:r['source_index'])


def verify_repo_revision(root: Path, given: str) -> None:
    # Prefer host Git; the original inference Docker image has no git binary.
    try:
        completed = subprocess.run(
            ['git', '-C', str(root), 'rev-parse', 'HEAD'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=True, text=True,
        )
    except FileNotFoundError:
        completed = None
    if completed is not None:
        require(completed.stdout.strip() == given, 'Provided code revision differs from Git HEAD')
        return
    marker = root / '.git'
    if marker.is_file():
        value = marker.read_text(encoding='utf-8').strip()
        require(value.startswith('gitdir: '), 'Unrecognized .git file')
        gitdir = Path(value[8:])
        if not gitdir.is_absolute():
            gitdir = (root / gitdir).resolve()
    else:
        gitdir = marker
    require(gitdir.is_dir(), 'Git metadata missing')
    head = (gitdir / 'HEAD').read_text(encoding='utf-8').strip()
    if head.startswith('ref: '):
        ref = head[5:]
        refpath = gitdir / ref
        if refpath.is_file():
            head = refpath.read_text(encoding='utf-8').strip()
        else:
            # Packed refs, or worktree whose common refs are in commondir.
            common = gitdir
            if (gitdir / 'commondir').is_file():
                v = (gitdir / 'commondir').read_text(encoding='utf-8').strip()
                common = (gitdir / v).resolve()
                refpath = common / ref
                if refpath.is_file():
                    head = refpath.read_text(encoding='utf-8').strip()
            if head.startswith('ref: '):
                packed = common / 'packed-refs'
                require(packed.is_file(), f'Git reference missing: {ref}')
                candidates = [x.split(' ',1)[0] for x in packed.read_text().splitlines()
                              if not x.startswith(('#','^')) and x.endswith(' '+ref)]
                require(len(candidates)==1, f'Git packed ref not uniquely resolved: {ref}')
                head = candidates[0]
    require(re.fullmatch(r'[0-9a-f]{40}', head) is not None and head == given,
            'Provided code revision differs from .git HEAD')


def materialize(root: Path, code_revision: str):
    require(re.fullmatch(r'[a-f0-9]{40}',code_revision) is not None,
            'Pass full Git HEAD as --code-revision')
    verify_repo_revision(root, code_revision)
    # Exact provenance chain and soundness-eligibility checks; no model imports.
    auditor_path = root / 'scripts/audit_e003_all_screens_readonly_v1.py'
    require(sha(auditor_path) == AUDITOR_SHA, 'Consolidated auditor SHA changed')
    require(sha(root / SOURCE_RAW) == SOURCE_SHA, 'Raw GSM8K train SHA changed')
    require(sha(root / SPLIT) == SPLIT_SHA, 'Frozen split SHA changed')
    sys.path.insert(0, str(root / 'scripts'))
    import audit_e003_all_screens_readonly_v1 as auditor
    require(Path(auditor.__file__).resolve() == auditor_path.resolve(),
            'Unexpected auditor import location')
    auditor.run(root)  # Fail closed against 146 groups / 584 candidates / provenance.
    proposals, long_gaps = build_pairs(root, auditor)
    text = canonical_jsonl(proposals)
    manual = {
        'schema': SCHEMA + '_review_worklist',
        'status': 'DRAFT_REVIEW_WORKLIST_NOT_SIGNOFF',
        'review_count': 124,
        'review_required_advisory_count': 123,
        'independently_approved_exception_source': 5436,
        'group_only_human_approval_pair_unresolved': 2320,
        'held_and_excluded_source_indices': sorted(HOLDS),
        'length_gap_over_40_token_pairs': long_gaps,
        'pairs_to_review': [
            {'source_index':p['source_index'],
             'chosen_sample_index':p['chosen_sample_index'],
             'rejected_sample_index':p['rejected_sample_index'],
             'absolute_token_gap':p['absolute_token_gap'],
             'independent_pair_signoff':p['independent_pair_signoff'],
             'decision': 'ALREADY_PAIR_APPROVED_5436_ONLY'
                 if p['source_index'] == 5436 else 'PENDING_INDEPENDENT_REVIEW'}
            for p in proposals
        ],
        'full_dataset_approved':False,
        'training_authorized':False,
        'training_performed':False,
        'official_test_used':False,
    }
    worklist_text = canonical_json(manual)
    manifest = {
        'schema': SCHEMA + '_manifest',
        'type':'PREF_DATASET_CANDIDATE_ONLY_NOT_TRAINING_READY',
        'status':'REQUIRES_INDEPENDENT_PAIR_AND_DATASET_SIGNOFF',
        'code_revision':code_revision,
        'builder_script_sha256':sha(Path(__file__).resolve()),
        'independent_auditor_sha256':AUDITOR_SHA,
        'raw_train_sha256':SOURCE_SHA,
        'split_sha256':SPLIT_SHA,
        'original_candidates_sha256':CANDIDATE_SHA,
        'reference_erratum_derivative_sha256': 'f8c74ddb4398fa4f79ca44bbda0c0d50c812ec73351fcacdee16d7e174e6662f',
        'source5436_pair_approval_sha256':'cb66fb12aae28eaac87a4dd0bdb0d32caab2d3fde19ebdd05506c34becec1705',
        'pair_count':124,
        'standard_advisory_pairs':123,
        'individually_human_approved_exception_pairs':1,
        'group_only_approval_without_pair': [2320],
        'hold_source_indices':sorted(HOLDS),
        'token_gap_over_40_count':len(long_gaps),
        'token_gap_median_standard':statistics.median(
            x['absolute_token_gap'] for x in proposals if x['source_index'] != EXCEPTION_SOURCE),
        'max_token_gap_standard':max(
            x['absolute_token_gap'] for x in proposals if x['source_index'] != EXCEPTION_SOURCE),
        'candidate_jsonl_sha256':sha_bytes(text),
        'review_worklist_sha256':sha_bytes(worklist_text),
        'native_eos_token_id':NATIVE_EOS,
        'original_candidates_modified':False,
        'full_dataset_independently_approved':False,
        'training_authorized':False,
        'training_performed':False,
        'official_test_used':False,
        'note': ('The JSONL contains original decoded response text and original generated token IDs. '
                 'The native EOS appears in the ID stream, not the decoded text. '
                 'Do not feed this preview into a training runner without separate authorized dataset finalization.'),
    }
    return {'pairs_candidate.jsonl':text,
            'review_worklist.json':worklist_text,
            'manifest.json':canonical_json(manifest)}


def publish_atomic(path: Path, entries: dict[str,bytes]) -> None:
    require(path.parent.is_dir(), 'Output parent missing')
    require(not path.exists(), 'Refusing to overwrite output directory')
    staging = Path(tempfile.mkdtemp(prefix='.e003_candidate124_pending_',dir=path.parent))
    try:
        for name, data in entries.items():
            with (staging/name).open('xb') as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        require(not path.exists(), 'Output directory appeared during staging')
        staging.rename(path)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    for name,data in entries.items():
        require((path/name).read_bytes()==data, f'Postwrite mismatch: {name}')


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,default=Path('.'))
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--code-revision',required=True)
    parser.add_argument('--preflight-only',action='store_true')
    args=parser.parse_args()
    root=args.repo_root.resolve()
    out=args.output_dir.resolve()
    require(not out.exists(),f'Refusing to overwrite output: {out}')
    entries=materialize(root,args.code_revision)
    preview=json.loads(entries['manifest.json'])
    require(preview['pair_count']==124,'Unexpected pair count')
    if not args.preflight_only:
        publish_atomic(out,entries)
    print('\n=== E003 CANDIDATE124 PREVIEW ===')
    print('123 advisory pairs + 1 separately approved exception = 124 source-unique previews')
    print('21 HOLD sources excluded; source 2320 group approval does not authorize a pair')
    print('Maximum standard pair gap:',preview['max_token_gap_standard'])
    print('Preview dataset SHA256:',preview['candidate_jsonl_sha256'])
    print('Review worklist SHA256:',preview['review_worklist_sha256'])
    print('Output:', 'NONE (preflight)' if args.preflight_only else str(out))
    print('Independent full dataset signoff: NO; DPO training authorized: NO')
    print('CANDIDATE PREVIEW: PASSED')


if __name__=='__main__':
    main()
