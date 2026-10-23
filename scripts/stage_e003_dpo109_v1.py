#!/usr/bin/env python3
"""Stage only the 109 previously signed E003 ORIGINAL DPO preference pairs.

CPU/stdlib; no training or changes to existing outputs. Strict frozen inputs;
checks validation split through the repository's canonical GSM8K loader.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile

ZIP_SHA = '04b1e1ecd1daac8053f5a6a9a2143517169bfd8c6c2252b70325d0f69ea9f4aa'
SIGNED_JSON_SHA = '931d5f3c4223dd576b1dccf94f3272d926c2fd64ee1de21501db4a4258527201'
PREVIEW_SHA = '83216697cf1d4293e735de6ca2832a21b2dc13e06fc07eeb87fb583e3fbe1a42'
PREVIEW_MANIFEST_SHA = '3f0e61e0e6342570a8c8242059249ea3ad25d168a1ee600d6277c741bc43a724'
SECOND_PASS_SHA = 'c82ebb16b72cec8fd15e349f4b2582530de78b86bb3763b65d2faece6a7dbfd0'
SOURCE_SHA = '17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465'
SPLIT_SHA = '31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719'
EXCEPTION_APPROVAL_SHA = 'cb66fb12aae28eaac87a4dd0bdb0d32caab2d3fde19ebdd05506c34becec1705'
EXCLUDED_REVIEW = {2738,4320,5819,6288}
EXCLUDED_LENGTH = {1870,3419,3869,4200,4457,5828,5885,6190,6576,7217,7284}
HOLDS = {303,744,1293,1512,1651,2272,2515,3631,4151,4456,4949,5064,5599,5656,5775,5851,5870,5994,6417,7304,7340}
SIGNOFF_SFT_ONLY_CHANGES = {528,3012,6515}
SCHEMA = 'e003_dpo_signed109_staging_v1'
EOS_ID = 151643


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def sha_data(b):
    return hashlib.sha256(b).hexdigest()


def sha_path(path):
    return sha_data(path.read_bytes())


def pinned(root, relative, expected):
    path = root / relative
    require(path.is_file() and sha_path(path)==expected, f'Missing/changed pinned input {relative}')
    return path


def canonical_json(data):
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode('utf-8')


def canonical_jsonl(rows):
    return ''.join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',',':'))+'\n'
                   for row in rows).encode('utf-8')


def load_jsonl(path):
    content = path.read_text(encoding='utf-8').splitlines()
    require(content and all(s.strip() for s in content), f'Invalid blank/empty JSONL {path}')
    return [json.loads(s) for s in content]


def load_signed_package(archive):
    require(archive.is_file() and sha_path(archive)==ZIP_SHA, 'Signed review ZIP digest mismatch')
    with zipfile.ZipFile(archive) as z:
        checksums = {}
        for line in z.read('e003_final_review_SHA256SUMS.txt').decode().splitlines():
            digest, name = line.split('  ', 1)
            require(name not in checksums, 'Duplicate signed payload name')
            checksums[name]=digest
        require(set(checksums)=={
            'e003_all108_final_review_signed_off.xlsx',
            'e003_all108_final_review_signed_off.md',
            'e003_all108_final_review_signed_off.json',
            'e003_108_review_approved_sft_candidates.jsonl',
        },'Signed payload unexpected file set')
        require(set(z.namelist())==set(checksums)|{'e003_final_review_SHA256SUMS.txt'},'Signed ZIP extra/missing entries')
        for name,digest in checksums.items():
            require(sha_data(z.read(name))==digest,'Signed ZIP internal digest mismatch '+name)
        data=z.read('e003_all108_final_review_signed_off.json')
        require(sha_data(data)==SIGNED_JSON_SHA,'Signed JSON SHA mismatch')
    signed=json.loads(data)
    require(signed.get('requester_attestation_recorded') is True and signed.get('training_authorized') is False
            and signed.get('validation_set_leakage_checked') is False and signed.get('human_signoff_claimed') is False,
            'Signed review provenance/release flags changed')
    require(len(signed.get('pair_decisions', []))==108 and signed.get('counts',{}).get('final_dpo_pair_preferences_signed_off')==108,
            'Unexpected signed review population')
    return signed


def normalize_question(s):
    s=s.strip()
    if s.startswith('Question:'):
        s=s[len('Question:'):]
    s=re.sub(r'\s*Answer:\s*$', '', s)
    return ' '.join(unicodedata.normalize('NFKC',s).casefold().split())


def shingles(s, n=5):
    words=re.findall(r'\w+', s)
    return {tuple(words[i:i+n]) for i in range(max(0,len(words)-n+1))}


def validation_clearance(root, selected):
    # The project's own canonical split loader is the source of truth. Do not
    # guess the split schema or use the official GSM8K test set.
    for path in (str(root),str(root/'src')):
        if path not in sys.path:sys.path.insert(0,path)
    try:
        loader=importlib.import_module('llm_post_training.data.loader')
    except (ImportError,ModuleNotFoundError) as exc:
        raise ValueError('Cannot import canonical GSM8K loader; fail closed: '+str(exc)) from exc
    training=loader.load_gsm8k_split(root/'data/raw/gsm8k/train.jsonl',root/'configs/data/gsm8k_split_v1.json','training')
    validation=loader.load_gsm8k_split(root/'data/raw/gsm8k/train.jsonl',root/'configs/data/gsm8k_split_v1.json','validation')
    require(len(training)==6726 and len(validation)==747,'Unexpected frozen split sizes')
    train_ids={r.source_index for r in training}
    val_ids={r.source_index for r in validation}
    require(len(train_ids)==6726 and len(val_ids)==747 and not (train_ids&val_ids),'Nonpartitioned frozen split')
    require(len({normalize_question(r.question) for r in validation})==747,'Duplicate normalized validation questions')
    train_lookup={r.source_index:normalize_question(r.question) for r in training}
    val_norm={r.source_index:normalize_question(r.question) for r in validation}
    val_reverse={v:k for k,v in val_norm.items()}
    val_shingles={idx:shingles(q) for idx,q in val_norm.items()}
    suspicious=[]
    near_count=0
    for row in selected:
        source=row['source_index']
        require(source in train_ids and source not in val_ids, f'Source {source} excluded by frozen split')
        q=normalize_question(row['prompt'])
        require(q==train_lookup[source],f'Source {source} prompt differs from canonical training question')
        if q in val_reverse:
            suspicious.append((source,val_reverse[q],'exact-normalized-question'))
        qa=shingles(q)
        if len(qa)<12:continue
        for idx,qb in val_shingles.items():
            if len(qb)<12:continue
            jac=len(qa & qb)/len(qa | qb)
            if jac>=0.88:
                suspicious.append((source,idx,f'5gram-jaccard={jac:.3f}'))
                near_count+=1
    # No silent waiver for near-identical validation questions.
    require(not suspicious,'Potential train/validation question leakage (manual clearance required): '+repr(suspicious[:15]))
    return {'training_size':len(train_ids),'validation_size':len(val_ids),
            'selected_sources_in_training':len(selected),'normalized_exact_overlap':0,
            'near_duplicate_5gram_jaccard_ge_0_88':near_count,
            'near_duplicate_min_question_5grams':12,
            'near_duplicate_policy':'BLOCK_IF_DETECTED',
            'no_official_test_used':True}


def select_rows(preview, advisory, signed):
    require(len(preview)==124,'Preview pair count not 124')
    by_source={r['source_index']:r for r in preview}
    require(len(by_source)==124,'Duplicate preview source')
    expected_sources=set(advisory['sources_proposed_for_independent_human_signoff'])
    require(len(expected_sources)==108,'Expected 108 recommended source indices')
    require(len(advisory['entries'])==124,'Advisory entry count incorrect')
    adv_by_src={x['source_index']:x for x in advisory['entries']}
    require(len(adv_by_src)==124 and set(adv_by_src)==set(by_source),'Advisory/preview sets differ')
    signed_by_src={r['source_index']:r for r in signed['pair_decisions']}
    require(len(signed_by_src)==108 and set(signed_by_src)==expected_sources,
            'Signed decisions do not match 108 advisory recommendations')
    require(set(by_source)==expected_sources|EXCLUDED_REVIEW|EXCLUDED_LENGTH|{5436},
            'Unexpected source population; refuse silent inclusion')
    require(not (set(by_source) & HOLDS) and 2320 not in by_source,
            'HOLD or group-only source found in preview')
    result=[]
    annotations=[]
    for source in sorted(expected_sources|{5436}):
        pair=by_source[source]
        for field in ('full_dataset_approved','training_authorized','training_performed','official_test_used'):
            require(pair.get(field) is False, f'Preview pair {source} safety flag {field} not false')
        require(pair['native_eos_token_id']==EOS_ID,'Wrong native EOS ID')
        chosen_idx,rejected_idx=pair['chosen_sample_index'],pair['rejected_sample_index']
        require(type(chosen_idx)==int and type(rejected_idx)==int and chosen_idx!=rejected_idx,
                f'Invalid pair index {source}')
        gap=abs(pair['chosen_generated_tokens']-pair['rejected_generated_tokens'])
        require(gap==pair['absolute_token_gap'],'Token gap mismatch')
        for prefix in ('chosen','rejected'):
            ids=pair[prefix+'_generated_token_ids']
            require(isinstance(ids,list) and bool(ids) and all(type(n)==int for n in ids)
                    and ids[-1]==EOS_ID and len(ids)==pair[prefix+'_generated_tokens'],
                    f'Missing native EOS or tokens {source}:{prefix}')
            require(isinstance(pair[prefix],str) and pair[prefix].strip(), 'Empty response')
        approved_by='source5436_prior_pinned_pair_approval' if source==5436 else 'requester_self_attested_signed_108_review'
        if source==5436:
            require((chosen_idx,rejected_idx,gap)==(2,0,28), '5436 pair identity changed')
            require(pair['training_reference_answer']=='50' and pair['original_reference_answer']=='55'
                    and pair['independent_pair_signoff'] is True and pair['reference_training_only_erratum'] is True,
                    '5436 erratum/approval mismatch')
        else:
            a=adv_by_src[source]
            s=signed_by_src[source]
            require(a['second_pass_advisory_recommendation']=='RECOMMEND_FOR_INDEPENDENT_SIGNOFF',
                    f'Unexpected recommendation for {source}')
            require((a['chosen_sample_index'],a['rejected_sample_index'],a['absolute_token_gap_from_uploaded_document'])
                    ==(chosen_idx,rejected_idx,gap),f'Advisory identity mismatch {source}')
            require(s['requester_final_dpo_verdict']=='PREFER_ORIGINAL_CHOSEN'
                    and s['requester_assessment_signoff']=='APPROVED_AS_RECORDED'
                    and s['dpo_original_pair_preserved'] is True
                    and s['requester_final_review_status']=='SIGNED_OFF_BY_REQUESTER_SELF_ATTESTED'
                    and s['human_training_authorization'] is False
                    and s['final_training_authorization'] is False,
                    f'Missing or altered requester review {source}')
            for pref in ('chosen','rejected'):
                expected=s['sha256_'+pref]
                # Historic review sheet hashes trimmed display responses; don't
                # change original decoded text merely to match display formatting.
                require(sha_data(pair[pref].strip().encode('utf-8'))==expected and
                        expected==a[pref+'_response_sha256_from_rendered_document'],
                        f'Original selected {pref} review hash mismatch {source}')
            require(pair['independent_pair_signoff'] is False
                    and pair['reference_training_only_erratum'] is False,
                    f'Original advisory records changed {source}')
            require(gap<=40, f'Non-exception gap exceeds 40 {source}')
        # Do not attach fake EOS text; the original ID lists include EOS.
        result.append({'prompt':pair['prompt'],'chosen':pair['chosen'],'rejected':pair['rejected']})
        annotations.append({
            'source_index':source,'chosen_sample_index':chosen_idx,'rejected_sample_index':rejected_idx,
            'chosen_text_sha256_raw':sha_data(pair['chosen'].encode('utf-8')),
            'rejected_text_sha256_raw':sha_data(pair['rejected'].encode('utf-8')),
            'prompt_sha256_raw':sha_data(pair['prompt'].encode('utf-8')),
            'chosen_generated_token_ids':pair['chosen_generated_token_ids'],
            'rejected_generated_token_ids':pair['rejected_generated_token_ids'],
            'native_eos_id':EOS_ID,
            'chosen_generated_tokens':pair['chosen_generated_tokens'],
            'rejected_generated_tokens':pair['rejected_generated_tokens'],
            'signed_token_gap':pair['chosen_generated_tokens']-pair['rejected_generated_tokens'],
            'absolute_token_gap':gap,
            'approval_record':approved_by,
            'dpo_original_response_preserved':True,
            'sft_correction_not_applied_to_dpo':source in SIGNOFF_SFT_ONLY_CHANGES,
            'tokenization_preflight_passed':False,
            'training_authorized':False,
        })
    require(len(result)==len(annotations)==109,'Selection count mismatch')
    return result,annotations


def stage(root, signed_zip, code_revision):
    require(re.fullmatch(r'[a-f0-9]{40}',code_revision), 'Require full --code-revision SHA')
    git=subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],capture_output=True,text=True,check=True)
    require(git.stdout.strip()==code_revision,'Git HEAD differs from --code-revision')
    pinned(root,'data/raw/gsm8k/train.jsonl',SOURCE_SHA)
    pinned(root,'configs/data/gsm8k_split_v1.json',SPLIT_SHA)
    pinned(root,'data/preference_runs/e003_dpo_candidate124_v1/pairs_candidate.jsonl',PREVIEW_SHA)
    pinned(root,'data/preference_runs/e003_dpo_candidate124_v1/manifest.json',PREVIEW_MANIFEST_SHA)
    pinned(root,'configs/preference/e003_candidate124_second_pass_advisory_v1.json',SECOND_PASS_SHA)
    pinned(root,'configs/preference/e003_source5436_pair_approval_v1.json',EXCEPTION_APPROVAL_SHA)
    signed=load_signed_package(signed_zip)
    advisory=json.loads((root/'configs/preference/e003_candidate124_second_pass_advisory_v1.json').read_text())
    pairs=load_jsonl(root/'data/preference_runs/e003_dpo_candidate124_v1/pairs_candidate.jsonl')
    selected,notes=select_rows(pairs,advisory,signed)
    screening=validation_clearance(root,[{'source_index':note['source_index'],'prompt':pair['prompt']}
                                         for pair,note in zip(selected,notes)])
    selected_text=canonical_jsonl(selected)
    notes_text=canonical_jsonl(notes)
    manifest={
        'schema':SCHEMA+'_manifest',
        'status':'SIGNED_PAIR_SELECTION_STAGED_TOKENIZATION_AND_RELEASE_PENDING',
        'training_authorized':False,'training_performed':False,'official_test_used':False,
        'pair_count':109,'requester_signed_original_dpo_preferences':108,
        'separately_approved_erratum_pair_source':5436,
        'signed_review_provenance':'requester_self_attested_not_independent_cryptographic_signature',
        'new_sft_training':False,'sft_only_rewrites_used_in_dpo':False,
        'source_sft_only_corrections_kept_separate':sorted(SIGNOFF_SFT_ONLY_CHANGES),
        'excluded_reasoning_review':sorted(EXCLUDED_REVIEW),
        'excluded_long_token_gap':sorted(EXCLUDED_LENGTH),
        'excluded_held_sources':sorted(HOLDS),
        'excluded_group_only_source':2320,
        'git_revision':code_revision,
        'stage_builder_sha256':sha_path(Path(__file__).resolve()),
        'signed_review_zip_sha256':ZIP_SHA,
        'signed_review_json_sha256':SIGNED_JSON_SHA,
        'preview_pairs_sha256':PREVIEW_SHA,
        'preview_manifest_sha256':PREVIEW_MANIFEST_SHA,
        'second_pass_advisory_sha256':SECOND_PASS_SHA,
        'source5436_pair_approval_sha256':EXCEPTION_APPROVAL_SHA,
        'raw_train_sha256':SOURCE_SHA,'split_sha256':SPLIT_SHA,
        'pair_dataset_sha256':sha_data(selected_text),
        'pair_metadata_sha256':sha_data(notes_text),
        'validation_overlap_audit':screening,
        'native_eos_id_in_original_generated_token_ids':EOS_ID,
        'tokenizer_and_dpo_trainer_sequence_preflight':'NOT_YET_RUN',
        'dataset_freeze_and_run_authorization':'NOT_GRANTED',
        'caution':'Exactly original DPO chosen/rejected text, including any leading spaces. Do not train before DPO tokenizer/EOS and training-config audits and explicit authorization.'
    }
    return {'pairs_staged.jsonl':selected_text,'pair_metadata.jsonl':notes_text,'manifest.json':canonical_json(manifest)}


def publish_atomic(out,files):
    require(out.parent.is_dir() and not out.exists(),'Output directory must not already exist; refusing overwrite')
    stage_dir=Path(tempfile.mkdtemp(prefix='.e003_dpo109_pending_',dir=out.parent))
    try:
        for name,data in files.items():
            with (stage_dir/name).open('xb') as f:
                f.write(data)
                f.flush();os.fsync(f.fileno())
        require(not out.exists(),'Output appeared during stage')
        stage_dir.rename(out)
    finally:
        if stage_dir.exists():shutil.rmtree(stage_dir)
    for name,data in files.items():require((out/name).read_bytes()==data,'Postwrite digest mismatch')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo-root',type=Path,default=Path('.'))
    ap.add_argument('--signed-review-zip',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--code-revision',required=True)
    ap.add_argument('--preflight-only',action='store_true')
    args=ap.parse_args()
    root=args.repo_root.resolve();out=args.output_dir.resolve()
    require(not out.exists(),'Refusing to overwrite staged output')
    files=stage(root,args.signed_review_zip.resolve(),args.code_revision)
    preview=json.loads(files['manifest.json'])
    if not args.preflight_only:publish_atomic(out,files)
    print('=== E003 DPO109 SIGNED-SELECTION PREFLIGHT ===')
    print('108 signed original DPO preferences + 5436 approved exception: VERIFIED')
    print('21 HOLD, 4 re-review, 11 long-gap, group-only 2320: EXCLUDED')
    print('Frozen train/validation split:',preview['validation_overlap_audit']['training_size'], '/',
          preview['validation_overlap_audit']['validation_size'])
    print('Validation exact normalized or high-similarity overlap: NONE DETECTED')
    print('Staged DPO pair JSONL SHA256:',preview['pair_dataset_sha256'])
    print('DPO metadata JSONL SHA256:',preview['pair_metadata_sha256'])
    print('Output:', 'NONE (preflight only)' if args.preflight_only else out)
    print('DPO trainer tokenization and final training authorization: PENDING')
    print('No SFT, no GPU training: YES')
    print('E003 DPO109 SELECTION: PASSED (NOT TRAINING AUTHORIZED)')


if __name__=='__main__':
    main()
