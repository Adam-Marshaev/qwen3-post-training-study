#!/usr/bin/env python3
"""Fail-closed, read-only reconciliation of E003 reasoning screens.

Does NOT create preference pairs, modify source data, or authorize training.
Usage: python3 audit_e003_all_screens_readonly_v1.py --repo-root .
"""
import argparse
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path

CANDIDATE_SHA = '3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4'
MASTER_SHA = 'c463c89e17297320fc890b1923e49763988ff339e6ea0b62c6d999536ae08cd6'
INITIAL_SHA = '90d832c8cfb01c9d7d29c7e7b44563fb0616184f22a48ba42bc42ead08a07f36'
BATCH_SHA = [
    'fc2acad26b36f571543073ad930473a96681fa24a20e3db5348dafea58ebf927',
    '1a401f515e2eef9b7277a4f55ef766c91955fec6eb81423fdf16fdae1ce014f2',
    '0811c0621b9ad18d69121543811bc5a0e10096ce91c708325e7c4a96c0aa712e',
    'ad2f23615da09d694fdfd48c9f1838c4409afb2e97a77ce1eacb41fe8aa1c2aa',
    '7b0f18faebdb431b3423e0dcfdf44e2b2721431bf0572de05901a06f6001191e',
    'ad855c48340e6600639a3e1cc8bca5f2d83b51029699ea7a08af6131a6ab08c2',
    '4ba14e3e6a037bbe2ccc99894b445bd5cb4ca399bea4601b6b97a24fbbdbab24',
]
REVIEW24 = 'configs/preference/e003_scale256_reasoning_screen24_advisory_v1.json'
RUN_ROOT = 'data/preference_runs/e003_remaining_review122_v1'
REQUIRED_DECISIONS = {
    'configs/preference/e003_scale256_independent_adjudication3_v1.json':
        '23886515468df3c4d00f079d744b8eb62224d7d0f97820a665e06feb4adeb3e2',
    'configs/preference/e003_training_reference_erratum_approval_v1.json':
        'a031184e0abaaa345bc38adbb794f4521c7e60ac5eb51c5acba7d55a14143f69',
    'configs/preference/e003_source5436_pair_approval_v1.json':
        'cb66fb12aae28eaac87a4dd0bdb0d32caab2d3fde19ebdd05506c34becec1705',
    'data/preference_runs/e003_reference_erratum_5436_v1/regraded_candidates.jsonl':
        'f8c74ddb4398fa4f79ca44bbda0c0d50c812ec73351fcacdee16d7e174e6662f',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_json(root, rel, digest):
    path = root / rel
    assert path.is_file(), f'Missing required artifact: {rel}'
    actual = sha(path)
    assert actual == digest, f'Checksum mismatch for {rel}: {actual}'
    return json.loads(path.read_text(encoding='utf-8'))


def run(root):
    candidates_path = root / 'data/preference_runs/e003_scale256_k4_v1/candidates.jsonl'
    assert candidates_path.is_file(), 'Frozen candidate file missing'
    assert sha(candidates_path) == CANDIDATE_SHA, 'Frozen candidate SHA mismatch'
    originals = [json.loads(line) for line in candidates_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    assert len(originals) == 1024, 'Expected 1024 frozen candidates'
    lookup = {(r['source_index'], r['sample_index']): r for r in originals}
    assert len(lookup) == 1024, 'Candidate keys not unique'

    master = verified_json(root, f'{RUN_ROOT}/manifest.json', MASTER_SHA)
    assert len(master['batches']) == 7
    initial = verified_json(root, REVIEW24, INITIAL_SHA)
    assert initial['schema'] == 'e003_scale256_reasoning_screen24_advisory_v1'
    assert initial['original_candidate_dataset_sha256'] == CANDIDATE_SHA

    for rel, checksum in REQUIRED_DECISIONS.items():
        p = root / rel
        assert p.is_file() and sha(p) == checksum, f'Missing or altered authorization artifact: {rel}'

    source_ids = set()
    proposals = []
    screen_without_pair = set()
    hold_ids = set()
    cnt = Counter()
    total_samples = 0

    def evaluate(doc, batch_id=None):
        nonlocal total_samples
        assert doc['independent_human_signoff'] is False
        assert doc['training_approved'] is False
        assert doc['training_performed'] is False
        assert doc['official_test_used'] is False
        if batch_id is None:
            expected_len = 24
            assert len(doc['groups']) == 24
        else:
            expected_len = 2 if batch_id == 6 else 20
            assert doc['batch_number'] == batch_id
            assert doc['source_index_order'] == master['batches'][batch_id]['source_indices']
            assert doc['batch_selection_manifest_sha256'] == sha(root / RUN_ROOT / f'batch_{batch_id:02d}_selection.json')
            assert doc['batch_review_report_sha256'] == sha(root / RUN_ROOT / f'batch_{batch_id:02d}_review.txt')
            assert len(doc['groups']) == expected_len
        assert len(doc['source_index_order']) == expected_len
        assert [g['source_index'] for g in doc['groups']] == doc['source_index_order']
        for g in doc['groups']:
            sid = g['source_index']
            assert sid not in source_ids, f'Repeated source index: {sid}'
            source_ids.add(sid)
            sample_list = g['samples']
            assert len(sample_list) == 4
            by_idx = {s['sample_index']: s for s in sample_list}
            assert set(by_idx) == {0,1,2,3}
            total_samples += 4
            for idx, sample in by_idx.items():
                orig = lookup[(sid, idx)]
                matches = sample.get('answer_matches_original_reference', sample.get('answer_matches_reference'))
                assert matches is orig['correct'], (sid,idx,'correct')
                assert sample['eligible'] is orig['eligible'], (sid,idx,'eligible')
                assert sample['native_eos_stop'] is orig['native_eos_stop'], (sid,idx,'native_eos')
                assert sample['generated_tokens'] == orig['generated_tokens'], (sid,idx,'tokens')
                assert sample['extracted_answer'] == str(orig['extracted_answer']), (sid,idx,'extracted')
            proposal = g['advisory_pair_proposal']
            if proposal is None:
                screen_without_pair.add(sid)
                continue
            assert g['recommendation'] in ('APPROVE','PROVISIONAL_APPROVE')
            chosen, rejected = proposal['chosen_sample_index'], proposal['rejected_sample_index']
            assert chosen != rejected and chosen in by_idx and rejected in by_idx
            ch, rj = by_idx[chosen], by_idx[rejected]
            assert ch['eligible'] and ch['native_eos_stop'] and ch['reasoning_verdict'] == 'SOUND'
            assert rj['eligible'] and rj['native_eos_stop'] and rj['reasoning_verdict'] == 'FLAWED'
            assert ch.get('answer_matches_original_reference', ch.get('answer_matches_reference')) is True
            assert rj.get('answer_matches_original_reference', rj.get('answer_matches_reference')) is False
            gap = abs(ch['generated_tokens']-rj['generated_tokens'])
            assert gap == proposal['absolute_token_length_gap']
            possibilities = [(abs(a['generated_tokens']-b['generated_tokens']), a['sample_index'], b['sample_index'])
                for a in sample_list for b in sample_list
                if a['eligible'] and a['native_eos_stop'] and a['reasoning_verdict']=='SOUND'
                and a.get('answer_matches_original_reference',a.get('answer_matches_reference')) is True
                and b['eligible'] and b['native_eos_stop'] and b['reasoning_verdict']=='FLAWED'
                and b.get('answer_matches_original_reference',b.get('answer_matches_reference')) is False]
            assert possibilities and min(possibilities) == (gap,chosen,rejected), (sid,'pair-selection')
            proposals.append((sid,gap))
            cnt['advisory_pairs'] += 1

    evaluate(initial)
    for i, expected_sha in enumerate(BATCH_SHA):
        rel = f'configs/preference/e003_batch{i:02d}_reasoning_screen_advisory_v1.json'
        batch = verified_json(root, rel, expected_sha)
        assert batch['schema'] == f'e003_remaining_review122_batch{i:02d}_reasoning_screen_advisory_v1'
        assert batch.get('original_candidate_dataset_sha256',batch.get('frozen_candidate_dataset_sha256')) == CANDIDATE_SHA
        evaluate(batch,i)

    assert len(source_ids) == 146 and total_samples == 584
    assert len(screen_without_pair) == 23, (len(screen_without_pair),screen_without_pair)
    assert screen_without_pair >= {744,2320,5436}
    hold_ids = screen_without_pair - {2320,5436}
    assert len(hold_ids) == 21 and 744 in hold_ids
    assert len(proposals) == 123
    assert len(source_ids - hold_ids) == 125

    proposal_gaps = [gap for _,gap in proposals]
    print('=== E003 ALL-SCREEN READ-ONLY RECONCILIATION ===')
    print(f'Unique source groups: {len(source_ids)} / 146 — VERIFIED')
    print(f'Frozen candidate metadata matched: {total_samples} / 584 — VERIFIED')
    print(f'Advisory pair proposals (subject to signoff): {len(proposals)}')
    print('Source 2320: human-approved GROUP only, rejected sample not approved')
    print('Source 5436: separately approved exception pair 2 > 0; derivative regrade pinned')
    print(f'Provisionally usable groups including both exceptions: {len(source_ids - hold_ids)}')
    print(f'HOLD groups excluded from pair preparation: {len(hold_ids)}')
    print('HOLD source indices:',sorted(hold_ids))
    print('Proposed-pair token gap median:', statistics.median(proposal_gaps))
    print('Proposed-pair token gap max:',max(proposal_gaps))
    print('Token gap >40:',[(sid,gap) for sid,gap in sorted(proposals) if gap > 40])
    print('Training-ready fully approved pair dataset: NO')
    print('Independent full dataset signoff: NO | Training authorization: NO')
    print('ALL-SCREEN RECONCILIATION: PASSED (read-only)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',default='.',type=Path)
    args = parser.parse_args()
    run(args.repo_root.resolve())

if __name__ == '__main__':
    main()
