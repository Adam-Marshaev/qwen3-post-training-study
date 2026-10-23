#!/usr/bin/env python3
"""Independent read-only, fail-closed E003 DPO109 staged dataset integrity check.

Does not call the staging builder or alter files. Does not authorize training.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys
import unicodedata
import zipfile

SIGN_ZIP_SHA='04b1e1ecd1daac8053f5a6a9a2143517169bfd8c6c2252b70325d0f69ea9f4aa'
SIGN_JSON_SHA='931d5f3c4223dd576b1dccf94f3272d926c2fd64ee1de21501db4a4258527201'
PREVIEW_SHA='83216697cf1d4293e735de6ca2832a21b2dc13e06fc07eeb87fb583e3fbe1a42'
SECOND_PASS_SHA='c82ebb16b72cec8fd15e349f4b2582530de78b86bb3763b65d2faece6a7dbfd0'
RAW_SHA='17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465'
SPLIT_SHA='31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719'
EXCEPTION_SHA='cb66fb12aae28eaac87a4dd0bdb0d32caab2d3fde19ebdd05506c34becec1705'
HOLD={303,744,1293,1512,1651,2272,2515,3631,4151,4456,4949,5064,5599,5656,5775,5851,5870,5994,6417,7304,7340}
EXCLUDE={1870,3419,3869,4200,4457,5828,5885,6190,6576,7217,7284,2738,4320,5819,6288,2320}
EOS=151643


def check(condition,message):
    if not condition:raise ValueError(message)


def sha(b):return hashlib.sha256(b).hexdigest()


def filehash(path):return sha(path.read_bytes())


def check_sha(path,expected):
    check(path.is_file() and filehash(path)==expected,'Missing/altered artifact '+str(path))


def read_jsonl(path):
    lines=path.read_text(encoding='utf-8').splitlines()
    check(lines and all(s.strip() for s in lines),'Blank or empty JSONL '+str(path))
    return [json.loads(line) for line in lines]


def norm(value):
    value=value.strip()
    if value.startswith('Question:'):value=value[len('Question:'):]
    value=re.sub(r'\s*Answer:\s*$', '', value)
    return ' '.join(unicodedata.normalize('NFKC',value).casefold().split())


def run(root, directory, review_zip):
    check(directory.is_dir(),'Staged DPO directory absent')
    check({p.name for p in directory.iterdir()}=={'pairs_staged.jsonl','pair_metadata.jsonl','manifest.json'},
          'Unexpected staged file set')
    for relative,expected in [
        ('data/raw/gsm8k/train.jsonl',RAW_SHA),
        ('configs/data/gsm8k_split_v1.json',SPLIT_SHA),
        ('data/preference_runs/e003_dpo_candidate124_v1/pairs_candidate.jsonl',PREVIEW_SHA),
        ('configs/preference/e003_candidate124_second_pass_advisory_v1.json',SECOND_PASS_SHA),
        ('configs/preference/e003_source5436_pair_approval_v1.json',EXCEPTION_SHA),
    ]:check_sha(root/relative,expected)
    check_sha(review_zip,SIGN_ZIP_SHA)
    with zipfile.ZipFile(review_zip) as z:
        sj=z.read('e003_all108_final_review_signed_off.json')
        check(sha(sj)==SIGN_JSON_SHA,'Signed JSON changed')
        recorded=json.loads(sj)
    signed={d['source_index']:d for d in recorded['pair_decisions']}
    approved_sources=set(signed)|{5436}
    check(len(signed)==108 and len(approved_sources)==109 and
          not(approved_sources & (HOLD|EXCLUDE)),'Wrong 109 signed source set')
    manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    check(manifest['schema']=='e003_dpo_signed109_staging_v1_manifest' and
          manifest['status']=='SIGNED_PAIR_SELECTION_STAGED_TOKENIZATION_AND_RELEASE_PENDING' and
          manifest['pair_count']==109,'Invalid 109 staging manifest')
    check(manifest['training_authorized'] is False and manifest['training_performed'] is False and
          manifest['official_test_used'] is False and
          manifest['dataset_freeze_and_run_authorization']=='NOT_GRANTED' and
          manifest['tokenizer_and_dpo_trainer_sequence_preflight']=='NOT_YET_RUN' and
          manifest['new_sft_training'] is False and manifest['sft_only_rewrites_used_in_dpo'] is False,
          'Premature training/release flag')
    for key,val in [
        ('signed_review_zip_sha256',SIGN_ZIP_SHA),('signed_review_json_sha256',SIGN_JSON_SHA),
        ('preview_pairs_sha256',PREVIEW_SHA),('second_pass_advisory_sha256',SECOND_PASS_SHA),
        ('source5436_pair_approval_sha256',EXCEPTION_SHA),
        ('raw_train_sha256',RAW_SHA),('split_sha256',SPLIT_SHA),
        ('pair_dataset_sha256',filehash(directory/'pairs_staged.jsonl')),
        ('pair_metadata_sha256',filehash(directory/'pair_metadata.jsonl')),
    ]:check(manifest.get(key)==val,'Manifest checksum mismatch: '+key)
    pairs=read_jsonl(directory/'pairs_staged.jsonl')
    metadata=read_jsonl(directory/'pair_metadata.jsonl')
    originals=read_jsonl(root/'data/preference_runs/e003_dpo_candidate124_v1/pairs_candidate.jsonl')
    original_by_src={r['source_index']:r for r in originals}
    check(len(originals)==124 and len(original_by_src)==124,'Preview invalid source count')
    advisory=json.loads((root/'configs/preference/e003_candidate124_second_pass_advisory_v1.json').read_text())
    check(set(advisory['sources_proposed_for_independent_human_signoff'])==set(signed),
          'Signed/second-pass source lists do not agree')
    check(len(pairs)==len(metadata)==109,'Wrong staged count')
    ids=[m['source_index'] for m in metadata]
    check(ids==sorted(approved_sources),'Staged source order/set mismatch')
    for row,note in zip(pairs,metadata):
        src=note['source_index']; upstream=original_by_src[src]
        check(set(row)=={'prompt','chosen','rejected'},f'Unsafe DPO schema in {src}')
        check(all(row[k]==upstream[k] for k in ('prompt','chosen','rejected')),
              f'Upstream source text changed in {src}')
        check((note['chosen_sample_index'],note['rejected_sample_index'])==
              (upstream['chosen_sample_index'],upstream['rejected_sample_index']),
              f'Pair identity changed in {src}')
        for prefix in ('chosen','rejected'):
            check(note[prefix+'_text_sha256_raw']==sha(row[prefix].encode('utf-8')),
                  f'Original raw response digest differs in {src}')
            check(note[prefix+'_generated_token_ids']==upstream[prefix+'_generated_token_ids'],
                  f'Native token IDs changed in {src}')
            seq=note[prefix+'_generated_token_ids']
            check(seq and seq[-1]==EOS and len(seq)==note[prefix+'_generated_tokens'],
                  f'Native EOS missing in {src}')
        check(note['prompt_sha256_raw']==sha(row['prompt'].encode('utf-8')),
              f'Prompt SHA mismatch in {src}')
        check(note['training_authorized'] is False and note['tokenization_preflight_passed'] is False and
              note['dpo_original_response_preserved'] is True,
              f'Unsafe row flags in {src}')
        if src==5436:
            check((note['chosen_sample_index'],note['rejected_sample_index'])==(2,0) and
                  upstream['training_reference_answer']=='50' and
                  upstream['original_reference_answer']=='55' and
                  note['approval_record']=='source5436_prior_pinned_pair_approval',
                  'Source5436 source-specific approval failed')
        else:
            d=signed[src]
            check(d['requester_final_dpo_verdict']=='PREFER_ORIGINAL_CHOSEN' and
                  d['requester_assessment_signoff']=='APPROVED_AS_RECORDED' and
                  d['final_training_authorization'] is False and
                  d['dpo_original_pair_preserved'] is True and
                  note['approval_record']=='requester_self_attested_signed_108_review',
                  f'Requester preference missing for {src}')
            for prefix in ('chosen','rejected'):
                check(sha(row[prefix].strip().encode('utf-8'))==d['sha256_'+prefix],
                      f'Original reviewed SHA mismatch in {src}:{prefix}')
            check(note['absolute_token_gap']<=40 and
                  note['sft_correction_not_applied_to_dpo']==(src in {528,3012,6515}),
                  'Gap or SFT correction policy violated in '+str(src))
    # Independently confirm explicit source-index separation from official frozen val.
    for entry in [str(root),str(root/'src')]:
        if entry not in sys.path:sys.path.insert(0,entry)
    loader=importlib.import_module('llm_post_training.data.loader')
    train=loader.load_gsm8k_split(root/'data/raw/gsm8k/train.jsonl',root/'configs/data/gsm8k_split_v1.json','training')
    val=loader.load_gsm8k_split(root/'data/raw/gsm8k/train.jsonl',root/'configs/data/gsm8k_split_v1.json','validation')
    train_map={r.source_index:norm(r.question) for r in train}
    val_map={r.source_index:norm(r.question) for r in val}
    check(len(train_map)==6726 and len(val_map)==747 and not(set(train_map)&set(val_map)),
          'Frozen split mismatch')
    val_norm=set(val_map.values())
    for note,row in zip(metadata,pairs):
        src=note['source_index']
        check(src in train_map and src not in val_map and norm(row['prompt'])==train_map[src]
              and norm(row['prompt']) not in val_norm, f'Train/val leak at {src}')
    check(manifest['validation_overlap_audit']['selected_sources_in_training']==109 and
          manifest['validation_overlap_audit']['normalized_exact_overlap']==0 and
          manifest['validation_overlap_audit']['near_duplicate_5gram_jaccard_ge_0_88']==0,
          'Missing validation leak audit clearance')
    print('=== E003 DPO109 INDEPENDENT STAGED DATASET AUDIT ===')
    print('Original DPO prompt/chosen/rejected bytes:',109,'/ 109 VERIFIED')
    print('Signed original requester preferences:',108,'/ 108 VERIFIED')
    print('Prior separately approved source5436: VERIFIED')
    print('Native EOS token IDs:',218,'/ 218 VERIFIED')
    print('Frozen split membership, exact val overlap and builder near-duplicate clearance: VERIFIED')
    print('SFT-only rewritten completions mixed in: NONE')
    print('109 staged pair SHA256:',manifest['pair_dataset_sha256'])
    print('Final DPO tokenizer/EOS preflight: NOT DONE | GPU training authorization: NO')
    print('E003 DPO109 INDEPENDENT STAGING AUDIT: PASSED (read-only)')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path('.'))
    p.add_argument('--output-dir',required=True,type=Path)
    p.add_argument('--signed-review-zip',required=True,type=Path)
    args=p.parse_args()
    run(args.repo_root.resolve(),args.output_dir.resolve(),args.signed_review_zip.resolve())

if __name__=='__main__':main()
