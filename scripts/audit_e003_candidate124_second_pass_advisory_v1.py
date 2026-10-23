#!/usr/bin/env python3
"""Read-only check: second-pass rendered review vs frozen candidate preview.

This validates byte/data provenance and consistency, not the human quality decisions.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

PAIR_SHA = '83216697cf1d4293e735de6ca2832a21b2dc13e06fc07eeb87fb583e3fbe1a42'
DOCUMENT_SHA = 'af257bd6315a5645dde5574394b40309f6c9fb5ca0d046ef0022d3fa321e6fbf'
WORKLIST_SHA = '388387d300fe7ca168d47a5e0460b2277898987c158cd8c612c58e904c40b0e1'
MANIFEST_SHA = '3f0e61e0e6342570a8c8242059249ea3ad25d168a1ee600d6277c741bc43a724'
LONG = {1870,3419,3869,4200,4457,5828,5885,6190,6576,7217,7284}
RE_REVIEW = {2738,4320,5819,6288}
HOLD21 = {303,744,1293,1512,1651,2272,2515,3631,4151,4456,4949,5064,5599,5656,5775,5851,5870,5994,6417,7304,7340}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(path, expected):
    assert path.is_file(), f'Missing: {path}'
    assert sha(path.read_bytes()) == expected, f'SHA256 mismatch: {path}'


def parse_report(raw):
    matches = list(re.finditer(r'^## Source (\d+) — (.+)$', raw, re.M))
    assert len(matches) == 124
    out = {}
    for n, match in enumerate(matches):
        body = raw[match.end():matches[n+1].start() if n+1 < len(matches) else len(raw)]
        def capture(pattern):
            m = re.search(pattern, body, re.S)
            assert m, (match.group(1), pattern)
            return m.group(1).strip()
        source = int(match.group(1))
        assert source not in out
        out[source] = {
            'source_status': match.group(2),
            'chosen_sample_index': int(capture(r'Chosen sample: (\d+)')),
            'rejected_sample_index': int(capture(r'Rejected sample: (\d+)')),
            'absolute_token_gap': int(capture(r'Absolute token gap: (\d+)')),
            'prompt': capture(r'### Prompt\n\n(.*?)\n\n### Chosen response'),
            'chosen': capture(r'### Chosen response\n\n(.*?)\n\n### Rejected response'),
            'rejected': capture(r'### Rejected response\n\n(.*?)\n\n### Independent decision'),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', type=Path, default=Path('.'))
    ap.add_argument('--review-document', type=Path, default=Path.home()/'Downloads/e003_pair_review124_v1.md')
    args = ap.parse_args()
    root = args.repo_root.resolve()
    review_document = args.review_document.expanduser().resolve()
    advisory_path = root/'configs/preference/e003_candidate124_second_pass_advisory_v1.json'
    pairs_path = root/'data/preference_runs/e003_dpo_candidate124_v1/pairs_candidate.jsonl'
    worklist_path = root/'data/preference_runs/e003_dpo_candidate124_v1/review_worklist.json'
    input_manifest = root/'data/preference_runs/e003_dpo_candidate124_v1/manifest.json'
    verify(review_document, DOCUMENT_SHA)
    verify(pairs_path, PAIR_SHA)
    verify(worklist_path, WORKLIST_SHA)
    verify(input_manifest, MANIFEST_SHA)
    assert advisory_path.is_file()
    advisory = json.loads(advisory_path.read_text(encoding='utf-8'))
    assert advisory['schema'] == 'e003_candidate124_second_pass_text_review_advisory_v1'
    assert advisory['source_document_sha256'] == DOCUMENT_SHA
    assert advisory['candidate_jsonl_sha256_declared_by_source'] == PAIR_SHA
    for field in ('independent_human_signoff_performed','dpo_training_authorized','dpo_training_performed','official_test_used','original_data_modified'):
        assert advisory[field] is False, f'Unexpected authorization or modification: {field}'
    assert advisory['group_only_source2320_excluded'] is True
    assert advisory['second_pass_review_flags'] == sorted(RE_REVIEW)
    assert advisory['long_gap_sources'] == sorted(LONG)
    assert set(advisory['original_previously_screened_holds_excluded']) == HOLD21

    source_report = parse_report(review_document.read_text(encoding='utf-8'))
    orig_rows = [json.loads(line) for line in pairs_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    orig_by_source = {int(r['source_index']):r for r in orig_rows}
    assert len(orig_rows) == len(orig_by_source) == 124
    annotated = advisory['entries']
    annotation_by_source = {int(r['source_index']):r for r in annotated}
    assert len(annotated) == len(annotation_by_source) == 124
    assert set(source_report) == set(orig_by_source) == set(annotation_by_source)
    assert not (set(orig_by_source) & HOLD21)
    assert 2320 not in orig_by_source
    counts = Counter()
    reviewed_pairs = []
    for source in sorted(orig_by_source):
        row=orig_by_source[source]
        from_report=source_report[source]
        annotated_row=annotation_by_source[source]
        assert row['chosen_sample_index'] == from_report['chosen_sample_index'] == annotated_row['chosen_sample_index']
        assert row['rejected_sample_index'] == from_report['rejected_sample_index'] == annotated_row['rejected_sample_index']
        gap=row['absolute_token_gap']
        assert gap == from_report['absolute_token_gap'] == annotated_row['absolute_token_gap_from_uploaded_document']
        for field in ('prompt','chosen','rejected'):
            assert row[field].strip() == from_report[field].strip(), (source,field)
        assert sha(from_report['chosen'].encode()) == annotated_row['chosen_response_sha256_from_rendered_document']
        assert sha(from_report['rejected'].encode()) == annotated_row['rejected_response_sha256_from_rendered_document']
        assert annotated_row['source_document_status'] == from_report['source_status']
        assert annotated_row['independent_human_signoff_created_by_this_review'] is False
        assert annotated_row['training_authorized_by_this_review'] is False
        status=annotated_row['second_pass_advisory_recommendation']
        expected=(
            'PREEXISTING_PAIR_APPROVAL' if source == 5436 else
            'EXCLUDE_INITIAL_LENGTH_THRESHOLD' if source in LONG else
            'RE_REVIEW_REQUIRED' if source in RE_REVIEW else
            'RECOMMEND_FOR_INDEPENDENT_SIGNOFF'
        )
        assert status == expected
        if source in LONG: assert gap > 40
        elif source != 5436: assert gap <= 40
        if status == 'RECOMMEND_FOR_INDEPENDENT_SIGNOFF': reviewed_pairs.append(source)
        counts[status] += 1
    assert counts == {
        'RECOMMEND_FOR_INDEPENDENT_SIGNOFF':108,
        'RE_REVIEW_REQUIRED':4,
        'EXCLUDE_INITIAL_LENGTH_THRESHOLD':11,
        'PREEXISTING_PAIR_APPROVAL':1,
    }
    assert advisory['counts'] == dict(counts)
    assert advisory['sources_proposed_for_independent_human_signoff'] == reviewed_pairs
    assert source_report[5436]['chosen_sample_index'] == 2
    assert source_report[5436]['rejected_sample_index'] == 0
    print('=== E003 CANDIDATE124 SECOND-PASS TEXT AUDIT ===')
    print('Uploaded review document SHA256: VERIFIED')
    print('Frozen candidate preview, worklist, manifest SHA256: VERIFIED')
    print('All 124 pair identities, prompts, response texts, and gaps: VERIFIED')
    print('108 advisory candidates for independent human signoff: VERIFIED')
    print('4 re-review flags:', sorted(RE_REVIEW))
    print('11 length-based initial-run exclusions: VERIFIED')
    print('Prior approved exception 5436 sample2 > sample0: VERIFIED AS DOCUMENTED')
    print('21 prior HOLD groups and group-only 2320: EXCLUDED')
    print('New pair approvals: NONE | DPO training authorized: NO')
    print('SECOND-PASS TEXT AUDIT: PASSED (read-only)')

if __name__ == '__main__':
    main()
