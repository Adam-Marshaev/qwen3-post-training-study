#!/usr/bin/env python3
"""CPU-only, read-only independent structural audit for E003 advisory review batches 03-06."""
import argparse
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path

CANDIDATE_SHA = '3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4'
MASTER_SHA = 'c463c89e17297320fc890b1923e49763988ff339e6ea0b62c6d999536ae08cd6'
SOURCE_SHA = 'aa28ddc894615d2b611007ea16cf2fde8d13254225278aa09fdb3ad99eb1def0'
EXPECTED_HOLDS = {3: {4949,5064,5599,5656,5775}, 4: {5851,5870,5994}, 5: {6417}, 6: {7304,7340}}
EXPECTED_COUNTS = {3:(20,15,5), 4:(20,17,3), 5:(20,19,1), 6:(2,0,2)}
EXPECTED_VERDICTS = {3: {'SOUND':37,'FLAWED':34,'BORDERLINE':4,'CONDITIONAL':5},
                     4: {'SOUND':33,'FLAWED':40,'BORDERLINE':7},
                     5: {'SOUND':40,'FLAWED':33,'BORDERLINE':7},
                     6: {'FLAWED':7,'BORDERLINE':1}}
EXPECTED_JSON_SHAS = {
    3:'ad2f23615da09d694fdfd48c9f1838c4409afb2e97a77ce1eacb41fe8aa1c2aa',
    4:'7b0f18faebdb431b3423e0dcfdf44e2b2721431bf0572de05901a06f6001191e',
    5:'ad855c48340e6600639a3e1cc8bca5f2d83b51029699ea7a08af6131a6ab08c2',
    6:'4ba14e3e6a037bbe2ccc99894b445bd5cb4ca399bea4601b6b97a24fbbdbab24'}
EXPECTED_MD_SHAS = {
    3:'b0432ecd85f67aee04c7c23236f1e7c887e4da1eefd825bd81579984fc72dedf',
    4:'cdc09448dcb8571fcc2cfbcc313d953be0cdd3fcc4ec2fbc1e5f69f55f3c06f4',
    5:'71a0c56fcfb96e1644bfd37183d555736cba5a1728c40dd9f583f08aa0a2b077',
    6:'255d85a0a479dabeaf3894341e47fa53d7d3372793e657873321240382e25f2d'}
EXPECTED_SUMMARY_SHA = '7d0255a73101b62b3262b97ac11f495dd4522215b30104fb3ccd3cee7465fee7'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def pair_choices(samples):
    return sorted((abs(c['generated_tokens'] - r['generated_tokens']),
                   c['sample_index'],r['sample_index'])
                  for c in samples for r in samples
                  if c['reasoning_verdict']=='SOUND'
                  and c['answer_matches_original_reference'] is True
                  and c['eligible'] is True and c['native_eos_stop'] is True
                  and r['reasoning_verdict']=='FLAWED'
                  and r['answer_matches_original_reference'] is False
                  and r['eligible'] is True and r['native_eos_stop'] is True)

def check(root):
    run=root/'data/preference_runs/e003_remaining_review122_v1'
    original_path=root/'data/preference_runs/e003_scale256_k4_v1/candidates.jsonl'
    assert sha(run/'manifest.json')==MASTER_SHA, 'Master manifest SHA mismatch'
    assert sha(original_path)==CANDIDATE_SHA, 'Frozen candidate SHA mismatch'
    master=load_json(run/'manifest.json')
    assert len(master['batches'])==7
    lookup={}
    with original_path.open(encoding='utf-8') as fh:
        for line in fh:
            if line.strip():
                r=json.loads(line); key=(r['source_index'],r['sample_index'])
                assert key not in lookup, 'Duplicate candidate'
                lookup[key]=r
    assert len(lookup)==1024
    summary_path=root/'docs/e003_batches03_06_advisory_release_summary_v1.json'
    assert sha(summary_path)==EXPECTED_SUMMARY_SHA
    release=load_json(summary_path)
    assert release['source_master_manifest_sha256']==MASTER_SHA
    assert release['archive_source_sha256']==SOURCE_SHA
    assert release['frozen_candidate_sha256']==CANDIDATE_SHA
    assert release['independent_pair_signoff'] is False
    assert release['training_approved'] is False and release['training_performed'] is False
    assert len(release['batch_summaries'])==4

    all_sources=set(); total=0; approvals=0; holds=0
    for bid in (3,4,5,6):
        ent=master['batches'][bid]
        assert ent['batch_number']==bid
        report=run/ent['review_file'];selection_path=run/ent['selection_file']
        assert sha(report)==ent['review_sha256']
        assert sha(selection_path)==ent['selection_sha256']
        selection=load_json(selection_path)
        assert selection['selected_source_indices']==ent['source_indices']
        assert selection['review_status']=='UNREVIEWED'
        assert selection['independent_pair_signoff'] is False
        assert selection['training_approved'] is False
        assert selection['training_performed'] is False
        assert selection['candidate_dataset_sha256']==CANDIDATE_SHA
        jp=root/f'configs/preference/e003_batch{bid:02d}_reasoning_screen_advisory_v1.json'
        md=root/f'docs/e003_batch{bid:02d}_reasoning_audit_advisory_v1.md'
        assert sha(jp)==EXPECTED_JSON_SHAS[bid],f'Batch {bid} advisory SHA mismatch'
        assert sha(md)==EXPECTED_MD_SHAS[bid],f'Batch {bid} markdown SHA mismatch'
        obj=load_json(jp)
        assert obj['schema']==f'e003_remaining_review122_batch{bid:02d}_reasoning_screen_advisory_v1'
        assert obj['batch_number']==bid
        assert obj['uploaded_archive_sha256']==SOURCE_SHA
        assert obj['batch_master_manifest_sha256']==MASTER_SHA
        assert obj['batch_selection_manifest_sha256']==sha(selection_path)
        assert obj['batch_review_report_sha256']==sha(report)
        assert obj['frozen_candidate_dataset_sha256']==CANDIDATE_SHA
        assert obj['independent_human_signoff'] is False
        for key in ('training_approved','training_performed','official_test_used','original_candidates_modified'):
            assert obj[key] is False
        groups=obj['groups']; size,expected_approvals,expected_holds=EXPECTED_COUNTS[bid]
        assert len(groups)==size and obj['source_index_order']==ent['source_indices']
        verdicts=Counter(); rc=Counter(); gaps=[]; holdindices=set()
        for g in groups:
            source=g['source_index']
            assert source not in all_sources,'Duplicate source across batches'
            all_sources.add(source);rc[g['recommendation']]+=1
            assert len(g['samples'])==4
            assert [s['sample_index'] for s in g['samples']]==[0,1,2,3]
            assert g['independent_pair_signoff'] is False
            assert isinstance(g['review_note'],str) and len(g['review_note'])>20
            for s in g['samples']:
                candidate=lookup[(source,s['sample_index'])]
                for x,y in [('answer_matches_original_reference','correct'),('eligible','eligible'),('native_eos_stop','native_eos_stop'),('generated_tokens','generated_tokens')]:
                    assert s[x] == candidate[y],f'{source}/{s["sample_index"]}: {x}'
                assert s['extracted_answer']==str(candidate['extracted_answer'])
                assert s['reasoning_verdict'] in {'SOUND','FLAWED','BORDERLINE','CONDITIONAL'}
                assert len(s['reasoning_note'])>12
                if s['reasoning_verdict']=='SOUND': assert s['answer_matches_original_reference'] is True
                if s['native_eos_stop']:
                    assert candidate['generated_token_ids'][-1]==151643
                verdicts[s['reasoning_verdict']]+=1;total+=1
            options=pair_choices(g['samples']); proposal=g['advisory_pair_proposal']
            if g['recommendation']=='PROVISIONAL_APPROVE':
                assert options,'Provisional approval without pair'
                assert proposal is not None
                actual=(proposal['absolute_token_length_gap'],proposal['chosen_sample_index'],proposal['rejected_sample_index'])
                assert actual==options[0],f'Non-minimal or invalid pair for source {source}'
                gaps.append(actual[0])
            else:
                assert g['recommendation']=='HOLD' and proposal is None
                assert not options, f'Hold group has sound eligible pair: {source}'
                holdindices.add(source)
        assert verdicts==EXPECTED_VERDICTS[bid]
        assert rc['PROVISIONAL_APPROVE']==expected_approvals
        assert rc['HOLD']==expected_holds
        assert holdindices==EXPECTED_HOLDS[bid]
        assert obj['summary']==release['batch_summaries'][bid-3]
        assert obj['summary']['proposed_pair_count']==len(gaps)
        assert obj['summary']['median_absolute_token_length_gap']==(statistics.median(gaps) if gaps else None)
        assert obj['summary']['maximum_absolute_token_length_gap']==(max(gaps) if gaps else None)
        approvals+=expected_approvals;holds+=expected_holds
        print(f'Batch {bid:02d}: {size} sources, {size*4} candidates, {expected_approvals} provisional approvals, {expected_holds} HOLD — VERIFIED')
    assert len(all_sources)==62 and total==248 and approvals==51 and holds==11
    assert all_sources==set(master['remaining_source_indices'][60:])
    print('Frozen inputs, pair eligibility, provenance and output hashes: VERIFIED')
    print('62/62 groups and 248/248 candidate metadata: VERIFIED')
    print('Provisional approvals: 51 | HOLDS: 11')
    print('Independent pair approval: NO | DPO training authorized: NO')
    print('BATCHES 03–06 ADVISORY AUDIT: PASSED')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repo-root',type=Path,default=Path('.'))
    check(p.parse_args().repo_root.resolve())
