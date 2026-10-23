#!/usr/bin/env python3
"""Read-only, independent integrity audit of the E003 124-pair DPO PREVIEW.

No training, signoff, rewrite, or dataset finalization. Stdlib-only; does not
call the candidate builder. Checks output bytes against pinned SHA256 plus
re-derives per-pair identities, complete text, and token IDs from frozen input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

EXPECTED_PAIR_SHA = '83216697cf1d4293e735de6ca2832a21b2dc13e06fc07eeb87fb583e3fbe1a42'
EXPECTED_WORKLIST_SHA = '388387d300fe7ca168d47a5e0460b2277898987c158cd8c612c58e904c40b0e1'
ORIGINAL_SHA = '3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4'
RAW_SHA = '17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465'
SPLIT_SHA = '31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719'
AUDITOR_SHA = '4b5ba849d4edf47cf6cf56d86f2d80a7f10aa13a9d232fecbe2703a727d9160e'
DERIVATIVE_SHA = 'f8c74ddb4398fa4f79ca44bbda0c0d50c812ec73351fcacdee16d7e174e6662f'
APPROVAL_SHA = 'cb66fb12aae28eaac87a4dd0bdb0d32caab2d3fde19ebdd05506c34becec1705'
MASTER_SHA = 'c463c89e17297320fc890b1923e49763988ff339e6ea0b62c6d999536ae08cd6'
ADJUDICATION_SHA = '23886515468df3c4d00f079d744b8eb62224d7d0f97820a665e06feb4adeb3e2'
ERRATUM_APPROVAL_SHA = 'a031184e0abaaa345bc38adbb794f4521c7e60ac5eb51c5acba7d55a14143f69'
SCREENS_SHA = (
    '90d832c8cfb01c9d7d29c7e7b44563fb0616184f22a48ba42bc42ead08a07f36',
    'fc2acad26b36f571543073ad930473a96681fa24a20e3db5348dafea58ebf927',
    '1a401f515e2eef9b7277a4f55ef766c91955fec6eb81423fdf16fdae1ce014f2',
    '0811c0621b9ad18d69121543811bc5a0e10096ce91c708325e7c4a96c0aa712e',
    'ad2f23615da09d694fdfd48c9f1838c4409afb2e97a77ce1eacb41fe8aa1c2aa',
    '7b0f18faebdb431b3423e0dcfdf44e2b2721431bf0572de05901a06f6001191e',
    'ad855c48340e6600639a3e1cc8bca5f2d83b51029699ea7a08af6131a6ab08c2',
    '4ba14e3e6a037bbe2ccc99894b445bd5cb4ca399bea4601b6b97a24fbbdbab24',
)
EXPECTED_REV = 'e5a8af036c6e7dc190738458f7817dd87bd0b066'
SCHEMA = 'e003_dpo_preference_candidate124_v1'
NATIVE_EOS = 151643
HOLDS = frozenset((303,744,1293,1512,1651,2272,2515,3631,4151,4456,
                   4949,5064,5599,5656,5775,5851,5870,5994,6417,7304,7340))
LONG_GAPS = {1870:50,3419:53,3869:66,4200:41,4457:48,5828:47,
             5885:57,6190:54,6576:66,7217:112,7284:57}


def require(condition: bool, description: str) -> None:
    if not condition:
        raise AssertionError(description)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checksum(path: Path) -> str:
    require(path.is_file(), f'Missing input file: {path}')
    return digest(path.read_bytes())


def pinned(root: Path, relative: str, expected: str) -> None:
    actual = checksum(root / relative)
    require(actual == expected, f'SHA256 mismatch: {relative}; got {actual}')


def jsonfile(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def jsonlfile(path: Path):
    data = path.read_text(encoding='utf-8')
    require(data.endswith('\n') and data.strip(), f'Invalid JSONL file: {path}')
    lines = data.splitlines()
    require(all(line.strip() for line in lines), f'Blank JSONL line: {path}')
    return [json.loads(line) for line in lines]


def boolean_false_all(item: dict, keys: tuple[str,...], label: str) -> None:
    for field in keys:
        require(item.get(field) is False, f'Unsafe {label} flag: {field}')


def verify_one_pair(row: dict, originals: dict, proposals: dict) -> None:
    src = row['source_index']
    require(type(src) is int and src in proposals, f'Unrecognized paired source: {src}')
    selection = proposals[src]
    choice, rejection = row['chosen_sample_index'], row['rejected_sample_index']
    require(type(choice) is int and type(rejection) is int and choice != rejection,
            f'Invalid chosen/rejected identity: {src}')
    require((choice, rejection) == selection['pair'], f'Unapproved identity substitution: {src}')
    chosen = originals[(src, choice)]
    rejected = originals[(src, rejection)]
    require(row['schema'] == SCHEMA + '_pair', f'Invalid pair schema: {src}')
    require(chosen['prompt'] == rejected['prompt'] == row['prompt'], f'Prompt changed: {src}')
    for prefix, original in (('chosen',chosen),('rejected',rejected)):
        require(row[prefix] == original['response'], f'Original {prefix} response modified: {src}')
        require(row[prefix+'_generated_token_ids'] == original['generated_token_ids'],
                f'Original {prefix} tokens modified: {src}')
        tokens = original['generated_token_ids']
        require(isinstance(tokens,list) and 0<len(tokens)<256
                and all(type(x) is int for x in tokens)
                and tokens[-1] == NATIVE_EOS, f'Missing native EOS in {prefix}: {src}')
        require(original['generated_tokens'] == len(tokens)
                == row[prefix+'_generated_tokens'], f'Wrong {prefix} length: {src}')
        require(original['eligible'] is True and original['native_eos_stop'] is True
                and original['reached_token_cap'] is False
                and original['unwanted_continuation'] is False
                and original['extraction_status'] == 'valid',
                f'Ineligible {prefix}: {src}')
        require(original['sample_seed'] == 42 + src*100 + original['sample_index'],
                f'Unexpected RNG seed in {prefix}: {src}')
    require(row['native_eos_token_id'] == NATIVE_EOS, f'Wrong EOS field: {src}')
    gap = abs(chosen['generated_tokens']-rejected['generated_tokens'])
    require(row['absolute_token_gap'] == gap == selection['gap'], f'Token gap mismatch: {src}')
    require(row['original_reference_answer'] == str(chosen['reference_answer'])
            == str(rejected['reference_answer']), f'Changed original reference: {src}')
    boolean_false_all(row, ('full_dataset_approved','training_authorized',
                           'training_performed','official_test_used'),f'pair {src}')
    if src == 5436:
        require(choice == 2 and rejection == 0 and gap == 28, 'Wrong 5436 exception pair')
        require(chosen['correct'] is False and rejected['correct'] is True,
                'Original reference labels changed for exception')
        require(row['original_reference_answer'] == '55'
                and row['training_reference_answer'] == '50', 'Wrong 5436 training reference')
        require(row['reference_training_only_erratum'] is True
                and row['independent_pair_signoff'] is True
                and row['pair_review_status'] == 'INDEPENDENTLY_APPROVED_EXCEPTION_PAIR_ONLY'
                and row['review_source'] == 'configs/preference/e003_source5436_pair_approval_v1.json',
                '5436 exception provenance/signoff changed')
    else:
        require(chosen['correct'] is True and rejected['correct'] is False,
                f'Chosen/rejected original labels inverted: {src}')
        require(row['training_reference_answer'] == row['original_reference_answer'],
                f'Unexpected reference edit: {src}')
        require(row['reference_training_only_erratum'] is False
                and row['independent_pair_signoff'] is False
                and row['pair_review_status'] == 'ADVISORY_NOT_INDEPENDENTLY_APPROVED'
                and row['review_source'] == selection['review_source'],
                f'Advisory proposal incorrectly approved: {src}')


def run(root: Path, output: Path) -> None:
    require(root.is_dir() and output.is_dir(), 'Repository or output directory missing')
    pinned(root, 'data/raw/gsm8k/train.jsonl', RAW_SHA)
    pinned(root, 'configs/data/gsm8k_split_v1.json', SPLIT_SHA)
    pinned(root, 'data/preference_runs/e003_scale256_k4_v1/candidates.jsonl', ORIGINAL_SHA)
    pinned(root, 'data/preference_runs/e003_reference_erratum_5436_v1/regraded_candidates.jsonl',DERIVATIVE_SHA)
    pinned(root, 'configs/preference/e003_source5436_pair_approval_v1.json', APPROVAL_SHA)
    pinned(root, 'scripts/audit_e003_all_screens_readonly_v1.py',AUDITOR_SHA)
    pinned(root, 'data/preference_runs/e003_remaining_review122_v1/manifest.json',MASTER_SHA)
    pinned(root, 'configs/preference/e003_scale256_independent_adjudication3_v1.json',ADJUDICATION_SHA)
    pinned(root, 'configs/preference/e003_training_reference_erratum_approval_v1.json',ERRATUM_APPROVAL_SHA)
    require({p.name for p in output.iterdir()} ==
            {'pairs_candidate.jsonl','review_worklist.json','manifest.json'},
            'Preview output file set differs (extra/missing files)')
    require(checksum(output/'pairs_candidate.jsonl') == EXPECTED_PAIR_SHA,
            'Pair JSONL differs from deterministic preflight')
    require(checksum(output/'review_worklist.json') == EXPECTED_WORKLIST_SHA,
            'Worklist differs from deterministic preflight')
    manifest = jsonfile(output/'manifest.json')
    require(manifest.get('schema') == SCHEMA+'_manifest'
            and manifest.get('type') == 'PREF_DATASET_CANDIDATE_ONLY_NOT_TRAINING_READY'
            and manifest.get('status') == 'REQUIRES_INDEPENDENT_PAIR_AND_DATASET_SIGNOFF',
            'Manifest falsely indicates training readiness')
    require(manifest['code_revision'] == EXPECTED_REV,
            'Unexpected source code revision')
    require(manifest['builder_script_sha256'] == checksum(root/'scripts/build_e003_candidate124_v1.py'),
            'Builder file differs from preview provenance')
    for field, sha_value in (
        ('independent_auditor_sha256',AUDITOR_SHA),
        ('raw_train_sha256',RAW_SHA),('split_sha256',SPLIT_SHA),
        ('original_candidates_sha256',ORIGINAL_SHA),
        ('reference_erratum_derivative_sha256',DERIVATIVE_SHA),
        ('source5436_pair_approval_sha256',APPROVAL_SHA),
        ('candidate_jsonl_sha256',EXPECTED_PAIR_SHA),
        ('review_worklist_sha256',EXPECTED_WORKLIST_SHA)):
        require(manifest.get(field) == sha_value, f'Manifest {field} mismatch')
    require(manifest['pair_count'] == 124 and manifest['standard_advisory_pairs'] == 123
            and manifest['individually_human_approved_exception_pairs'] == 1
            and manifest['group_only_approval_without_pair'] == [2320]
            and manifest['hold_source_indices'] == sorted(HOLDS)
            and manifest['native_eos_token_id'] == NATIVE_EOS,
            'Manifest population/provenance mismatch')
    boolean_false_all(manifest,('original_candidates_modified',
                'full_dataset_independently_approved','training_authorized',
                'training_performed','official_test_used'), 'manifest')

    # Independently derive expected (source, chosen, rejected) identities from
    # the eight reviewed manifests. Never call builder import/function.
    screen_paths = [root/'configs/preference/e003_scale256_reasoning_screen24_advisory_v1.json'] + [
        root/f'configs/preference/e003_batch{i:02d}_reasoning_screen_advisory_v1.json'
        for i in range(7)]
    for path, expected_sha in zip(screen_paths, SCREENS_SHA, strict=True):
        require(checksum(path) == expected_sha, f'Review screen SHA256 mismatch: {path}')
    proposals = {}
    all_sources = set()
    no_pairs = set()
    for path in screen_paths:
        screen = jsonfile(path)
        boolean_false_all(screen,('independent_human_signoff','training_approved',
                                  'training_performed','official_test_used'),str(path))
        for group in screen['groups']:
            source = group['source_index']
            require(type(source) is int and source not in all_sources,
                    f'Duplicate reviewed source: {source}')
            all_sources.add(source)
            proposal = group['advisory_pair_proposal']
            if proposal is None:
                no_pairs.add(source)
                continue
            require(source not in HOLDS | {2320,5436},f'Restricted source has advisory pair: {source}')
            by_sample = {s['sample_index']:s for s in group['samples']}
            require(len(by_sample) == 4 and set(by_sample) == {0,1,2,3},
                    f'Wrong review sample set: {source}')
            chosen, rejected = proposal['chosen_sample_index'], proposal['rejected_sample_index']
            require(by_sample[chosen]['reasoning_verdict']=='SOUND'
                    and by_sample[rejected]['reasoning_verdict']=='FLAWED',
                    f'Review reasoning mismatch: {source}')
            require(by_sample[chosen].get('answer_matches_original_reference',
                by_sample[chosen].get('answer_matches_reference')) is True
                and by_sample[rejected].get('answer_matches_original_reference',
                by_sample[rejected].get('answer_matches_reference')) is False,
                f'Review correctness mismatch: {source}')
            possible = sorted(
                (abs(c['generated_tokens']-r['generated_tokens']),c['sample_index'],r['sample_index'])
                for c in group['samples'] for r in group['samples']
                if c['reasoning_verdict']=='SOUND' and c['eligible']
                and c.get('answer_matches_original_reference',c.get('answer_matches_reference')) is True
                and r['reasoning_verdict']=='FLAWED' and r['eligible']
                and r.get('answer_matches_original_reference',r.get('answer_matches_reference')) is False)
            expected = (proposal['absolute_token_length_gap'],chosen,rejected)
            require(possible and expected == possible[0],f'Nonminimal proposed length gap: {source}')
            proposals[source] = {'pair':(chosen,rejected),
                                 'gap':proposal['absolute_token_length_gap'],
                                 'review_source':str(path.relative_to(root))}
    require(len(all_sources)==146 and len(proposals)==123,
            'Screen population not exactly 146 groups / 123 proposals')
    require(no_pairs == HOLDS | {2320,5436},'Unexpected no-proposal group(s)')
    proposals[5436] = {'pair':(2,0),'gap':28,
                       'review_source':'configs/preference/e003_source5436_pair_approval_v1.json'}
    original_rows = jsonlfile(root/'data/preference_runs/e003_scale256_k4_v1/candidates.jsonl')
    require(len(original_rows)==1024,'Incorrect frozen candidate row count')
    originals = {(r['source_index'],r['sample_index']):r for r in original_rows}
    require(len(originals)==1024,'Duplicate original candidate key')
    pairs_path = output/'pairs_candidate.jsonl'
    rows = jsonlfile(pairs_path)
    require(len(rows)==124 and len({r['source_index'] for r in rows})==124,
            'Wrong final pair count or repeated source')
    require([r['source_index'] for r in rows]==sorted(proposals),
            'Wrong sorted candidate preview population')
    # Independent canonical serialization check; prevents whitespace drift.
    reconstructed = ''.join(json.dumps(r,sort_keys=True,separators=(',', ':'),ensure_ascii=False)+'\n'
                            for r in rows).encode('utf-8')
    require(pairs_path.read_bytes()==reconstructed,'Noncanonical JSONL serialization')
    for row in rows:
        verify_one_pair(row,originals,proposals)
    gaps = {r['source_index']:r['absolute_token_gap'] for r in rows
            if r['source_index']!=5436 and r['absolute_token_gap']>40}
    require(gaps==LONG_GAPS and manifest['token_gap_over_40_count']==11,
            'High length-gap roster changed')
    require(manifest['max_token_gap_standard']==112
            and manifest['token_gap_median_standard']==8,
            'Manifest token-gap statistics wrong')
    worklist = jsonfile(output/'review_worklist.json')
    require(worklist.get('schema') == SCHEMA+'_review_worklist'
            and worklist.get('status') == 'DRAFT_REVIEW_WORKLIST_NOT_SIGNOFF'
            and worklist.get('review_count') == 124
            and worklist.get('review_required_advisory_count') == 123
            and worklist.get('independently_approved_exception_source')==5436
            and worklist.get('group_only_human_approval_pair_unresolved')==2320
            and worklist.get('held_and_excluded_source_indices')==sorted(HOLDS),
            'Worklist review requirements changed')
    boolean_false_all(worklist,('full_dataset_approved','training_authorized',
                                'training_performed','official_test_used'),'worklist')
    expected_items = [
        {'source_index':row['source_index'],'chosen_sample_index':row['chosen_sample_index'],
         'rejected_sample_index':row['rejected_sample_index'],
         'absolute_token_gap':row['absolute_token_gap'],
         'independent_pair_signoff':row['independent_pair_signoff'],
         'decision':('ALREADY_PAIR_APPROVED_5436_ONLY' if row['source_index']==5436
                     else 'PENDING_INDEPENDENT_REVIEW')}
        for row in rows]
    require(worklist['pairs_to_review']==expected_items,'Worklist pair decisions/identities changed')
    expected_long=[{'source_index':src,'absolute_token_gap':gap} for src,gap in sorted(LONG_GAPS.items())]
    require(worklist['length_gap_over_40_token_pairs']==expected_long,
            'Worklist high-gap flags changed')
    approvals=Counter(bool(r['independent_pair_signoff']) for r in rows)
    require(approvals=={False:123,True:1},'Wrong approval tally')
    print('=== E003 CANDIDATE124 INDEPENDENT INTEGRITY AUDIT ===')
    print('Frozen raw/split/candidate/erratum/approval hashes: VERIFIED')
    print('Preview pairs SHA256:',EXPECTED_PAIR_SHA)
    print('Worklist SHA256:',EXPECTED_WORKLIST_SHA)
    print('Manifest SHA256:',checksum(output/'manifest.json'))
    print('Reviewed sources: 146 | Candidate pairs: 124 | Candidate rows crosschecked: 248')
    print('Exact original responses, prompts, native-EOS token IDs: VERIFIED')
    print('Screen proposals and deterministic minimum token-gap selection: VERIFIED')
    print('Source 5436: only approved pair 2 > 0, reference 55 -> 50: VERIFIED')
    print('21 HOLD sources and group-only source 2320: EXCLUDED')
    print('11 long token gaps: FLAGGED')
    print('123 advisory-only pairs: NOT PAIR-APPROVED')
    print('Full dataset signoff: NO | Training authorization: NO')
    print('CANDIDATE124 INDEPENDENT AUDIT: PASSED (read-only)')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path('.'))
    p.add_argument('--output-dir',type=Path,default=Path('data/preference_runs/e003_dpo_candidate124_v1'))
    args=p.parse_args()
    run(args.repo_root.resolve(),args.output_dir.resolve())

if __name__=='__main__':
    main()
