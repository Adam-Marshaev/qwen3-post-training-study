#!/usr/bin/env python3
"""Reproduce P2 mechanical screening, advisory arithmetic-first holds, and QC worksheets.

P1 mechanical predicates are preserved in p2_screen_v1.py (exact narrow fork).
The seven P2 source-level holds here are assistant review decisions, NOT a
transferable automatic semantic verifier. No training dataset is emitted.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
INPUT_SHA = 'fe4c4f034417b73be7862975889e102882be6d9f67352d62b9a568eaeb66faf9'
SEED = 20261024
MATERIAL_HOLDS = {
    658: 'Question prices use USD and EUR without a conversion rate. Subtracting 893 dollars and 874 euros as equivalent currency is unjustified.',
    660: 'Duke should have 2 ants, not 6, and Abe is omitted from the final summation. The reported 20 is coincidental.',
    979: 'Grant throws 20 yards and Kyle 40 yards; chosen computes twice the 4-yard increase instead, then adds 16+8 to obtain 24 accidentally.',
    2760: 'Chosen doubles the father’s current age and subtracts the son’s current age as though the father must first reach 64. The age relationship is invalid; 27 arises by coincidence.',
    4844: 'Chosen summation omits Kit-Kats and fails to subtract the 5 gifted lollipops; those errors cancel and the numeric total is coincidental.',
    5745: 'Response claims a 10-minute handstand and a 5-minute rest each contain 60 minutes, then treats the 15-minute cycle entirely as handstanding. Material temporal explanations contradict the problem.',
    7443: 'Response initially claims mother is 74-50=24 years old, confusing parent-child age gap with mother’s present age. Later self-correction gives 72 and final 22, but prior relationship is materially false.',
}
# Examples retained because the requested policy allows semantic/label slips.
ALLOWED_WORDING_NOTES = {
    1178: 'Uses -$2400 less for a $2400 pay shortfall; magnitude and operations are correct.',
    3230: 'Mislabels the giraffe revenue sentence as elephant revenue; 16*150 and 8*350 remain correct.',
    3804: 'Reports 4-6=-2 as daily shortage before using its positive magnitude 2; total shortage is correctly 14.',
    3945: 'Calls 15 people 15 pizzas, immediately divides by 3 correctly to obtain 5 pizzas.',
    4392: 'Calls 10 neighborhoods 10 streets; count 10*4*500 is correct.',
    4507: 'Labels 70/7 as days rather than weeks; multiplying 10 weeks by 6 hours/week yields correct 60.',
    4591: 'Repeated/incorrect units for 3*3=9, but counts consumption as 9+8+5 correctly.',
    6977: 'Calls the 110 total boys “present students”; actual equation 250-140 gives total boys, then subtracts 70 present boys correctly.',
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_jsonl(records: list[dict]) -> bytes:
    return ''.join(json.dumps(item, ensure_ascii=False, sort_keys=True) + '\n' for item in records).encode()


def load_screener():
    script = ROOT / 'scripts' / 'p2_screen_v1.py'
    spec = importlib.util.spec_from_file_location('p2_screen_frozen', script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_groups(path: Path):
    payload = path.read_bytes()
    assert digest(payload) == INPUT_SHA, 'Mixed-group export SHA mismatch'
    groups = [json.loads(line) for line in payload.splitlines() if line.strip()]
    assert len(groups) == 137
    assert len({g['source_index'] for g in groups}) == 137
    assert [g['source_index'] for g in groups] == sorted(g['source_index'] for g in groups)
    return groups


def classify(groups):
    mechanical, m_summary = load_screener().screen(groups)
    assert m_summary['groups_passing_mechanical_gates'] == 87
    assert m_summary['groups_length_compatible'] == 130
    assert len(mechanical) == 137
    assert set(MATERIAL_HOLDS).issubset({d['source_index'] for d in mechanical if d['top_pair']})
    decisions = []
    for d in mechanical:
        source = d['source_index']
        pair = d['top_pair']
        if pair is None:
            status = 'REJECT_MECHANICAL'
            reason = 'No pair passed exact frozen arithmetic, eligibility, terminal-answer, and length-gap gates.'
        elif source in MATERIAL_HOLDS:
            status = 'REJECT_MATH_OR_MATERIAL_RELATION'
            reason = MATERIAL_HOLDS[source]
        else:
            status = 'PROVISIONAL_ACCEPT_QC_REQUIRED'
            reason = ALLOWED_WORDING_NOTES.get(source, 'No material arithmetic or quantity-relation failure identified in advisory assistant review; not independently verified.')
        decisions.append({
            'source_index': source,
            'decision': status,
            'chosen_sample_index': pair['chosen_sample_index'] if pair else None,
            'rejected_sample_index': pair['rejected_sample_index'] if pair else None,
            'pair_token_gap': pair['gap'] if pair else None,
            'mechanically_eligible_pair_count': d['mechanically_eligible_pair_count'],
            'advisory_review_reason': reason,
            'allowed_wording_issue': source in ALLOWED_WORDING_NOTES,
            'manual_exception_not_automated': source in MATERIAL_HOLDS,
            'approved_for_training': False,
        })
    counts = Counter(d['decision'] for d in decisions)
    assert counts == {
        'REJECT_MECHANICAL': 50,
        'REJECT_MATH_OR_MATERIAL_RELATION': 7,
        'PROVISIONAL_ACCEPT_QC_REQUIRED': 80,
    }, counts
    return decisions, mechanical, m_summary


def qc_samples(decisions):
    accepted = sorted((d for d in decisions if d['decision'] == 'PROVISIONAL_ACCEPT_QC_REQUIRED'), key=lambda x: x['source_index'])
    mechanical = sorted((d for d in decisions if d['decision'] == 'REJECT_MECHANICAL'), key=lambda x: x['source_index'])
    held = sorted((d for d in decisions if d['decision'] == 'REJECT_MATH_OR_MATERIAL_RELATION'), key=lambda x: x['source_index'])
    rng = random.Random(SEED)
    accepted30 = sorted(rng.sample(accepted, 30), key=lambda x: x['source_index'])
    rejected10 = sorted(held + rng.sample(mechanical, 3), key=lambda x: x['source_index'])
    assert len(accepted30) == 30 and len(rejected10) == 10
    assert set(d['source_index'] for d in accepted30).isdisjoint(d['source_index'] for d in rejected10)
    return accepted30, rejected10


def worksheet(rows, groups_by, label):
    ret = [f'# E004-P2 arithmetic-first QC — {label}', '',
           f'- Fixed seed: `{SEED}`. Random accepted sample; rejected sample is STRATIFIED (all seven source-level material holds + three random mechanical rejects).',
           '- This sample is NOT independently adjudicated. All selected pairs remain provisional; no training approved.',
           '- Judge mathematical operations and quantity relationships; tolerate minor wording/units/referents.',
           '- For mechanical rejects, the diagnostic comparison shown below does NOT satisfy all mechanical gates.', '', '---', '']
    for d in rows:
        g = groups_by[d['source_index']]
        ci, wi = d['chosen_sample_index'], d['rejected_sample_index']
        if ci is None:
            correct = [r for r in g['responses'] if r['eligible'] and r['correct']]
            wrong = [r for r in g['responses'] if r['eligible'] and not r['correct']]
            pairs = sorted((abs(c['generated_tokens']-w['generated_tokens']), c['sample_index'], w['sample_index']) for c in correct for w in wrong)
            _, ci, wi = pairs[0]
        chosen, rejected = g['responses'][ci], g['responses'][wi]
        ret += [f'## Source {d["source_index"]} — chosen sample {ci}, rejected sample {wi}', '',
                f'- Decision: `{d["decision"]}`', f'- Reviewer note: {d["advisory_review_reason"]}',
                f'- Reference numeric answer: `{g["reference_answer"]}`',
                f'- Chosen/rejected token gap: `{abs(chosen["generated_tokens"]-rejected["generated_tokens"])}`', '',
                '**Question:**', '', '```text', g['prompt'].strip(), '```', '',
                '**Chosen response:**', '', '```text', chosen['response'].strip(), '```', '',
                '**Rejected response:**', '', '```text', rejected['response'].strip(), '```', '',
                '**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain', '',
                '**QC notes:**', '', '---', '']
    return ('\n'.join(ret) + '\n').encode()


def generate(input_path):
    groups = read_groups(input_path)
    decisions, mechanical, mechanical_summary = classify(groups)
    accepted, rejected = qc_samples(decisions)
    by = {g['source_index']: g for g in groups}
    decisions_bytes = canonical_jsonl(decisions)
    mechanical_bytes = canonical_jsonl(mechanical)
    summary = {
        'schema': 'e004_p2_arithmetic_first_review_advisory_v1',
        'run_code_revision': 'f543aa41ff917d96b8f26b38df9c6c00f91b1619',
        'candidates_sha256': '568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79',
        'mixed_input_sha256': INPUT_SHA,
        'generated_source_questions': 250,
        'mixed_groups': 137,
        'length_compatible_groups': 130,
        'mechanical_pass_groups': 87,
        'mechanical_reject_groups': 50,
        'advisory_material_relation_holds': 7,
        'provisional_pairs': 80,
        'provisional_yield_per_source': 0.32,
        'provisional_yield_per_mixed': round(80/137, 6),
        'approved_training_pairs': 0,
        'manual_assistant_review_is_not_independent_certification': True,
        'p2_advisory_exclusions_not_transferable_automatic_filter': True,
        'official_test_used': False,
        'training_performed': False,
        'qc_seed': SEED,
        'qc_accepted30_source_indices': [d['source_index'] for d in accepted],
        'qc_rejected10_source_indices': [d['source_index'] for d in rejected],
        'qc_rejected10_stratification': 'all 7 material relation holds plus 3 random mechanical rejects; not a representative reject sample',
        'decisions_sha256': digest(decisions_bytes),
        'mechanical_decisions_sha256': digest(mechanical_bytes),
        'screen_summary': mechanical_summary,
    }
    outputs = {
        'decisions_advisory.jsonl': decisions_bytes,
        'mechanical_decisions.jsonl': mechanical_bytes,
        'qc_accepted30_unreviewed.md': worksheet(accepted, by, '30 provisional accepts'),
        'qc_rejected10_unreviewed.md': worksheet(rejected, by, '10 rejects'),
        'summary.json': (json.dumps(summary, indent=2, sort_keys=True)+'\n').encode(),
    }
    return summary, outputs


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    summary, outputs = generate(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        target = args.output_dir / name
        if target.exists():
            assert target.read_bytes() == data, f'No overwrite: {target}'
        else:
            with target.open('xb') as f:
                f.write(data)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print('No DPO/GRPO training, no certified pairs, original P2 candidates unchanged.')


if __name__ == '__main__':
    main()
