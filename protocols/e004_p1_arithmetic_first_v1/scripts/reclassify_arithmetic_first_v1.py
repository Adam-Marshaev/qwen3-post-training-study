#!/usr/bin/env python3
"""E004-P1 arithmetic-first *advisory* reclassification. No training, no writes to source data.

To reproduce: python3 scripts/reclassify_arithmetic_first_v1.py --verify
To assess baseline overlap: add --coverage PATH_TO_EXISTING_COVERAGE_JSONL

This is a deterministic reclassification of existing assistant advisory judgments, NOT a
fresh independent verification of chosen reasoning. Original source rows and prior
review rationales are preserved in the output. Explicit exclusions are documented.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from strict_equation_screen_reference_v1 import screen

COMPACT_SHA='fe0ce3a7bb4cd20fedf4ee25e15e171e0047ff786ae39f16c2db4118934dcff0'
PRIOR_SHA='42952af0b07b90eb2a591d7651e97880d33b56b7414218babfa3a8925fc99707'
ORIGINAL_SHA='314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628'
COVERAGE_SHA='1e8aab76fd3bb271c40c79393fb678ba335b9a9a77d18594dbd1a5bdb49a7c52'
PREDICTIONS_SHA='f549c524edb4720a6bdabb372ab75892faae0d35b6e3f72ad149fed0c471150c'

# Intentionally small, concrete hard exclusions. These chosen traces do not
# establish the stated answer by sound reasoning, or the source is ambiguous.
# Do not promote a source with a broken computation merely because its final
# number matches the reference.
CRITICAL_CHOSEN={
 1344:'Chosen calls a positive earnings increase a decrease throughout; reverses the requested quantity.',
 4483:'Chosen invents/reshuffles record purchasers and wrong half-collection math; correct final absolute difference is coincidental.',
 5588:'Chosen reverses who brings life vests and then uses that mislabeled group as unmet demand; material contradiction in population account.',
 6411:'Chosen adds magnets and buttons to gemstones instead of calculating gems for two earrings; reaches 24 by coincidence.',
 6786:'Chosen treats 20 months of growth as 20 years of aging; required time is (26-2)/0.1=240 months=20 years.',
 7019:'Question wording about a one-and-a-half increase is materially ambiguous; a rejected different interpretation may be defensible.',
 7305:'Chosen assumes an unstated change in number of cats; conclusion requires unsupported population relation.',
}
NEGATIVE_TOO_CHAOTIC={
 5932:'Rejected response has several disconnected false quantities and inconsistent conclusions; unsuitable style-confounded preference negative.',
}
# Former QC holds from the fixed-seed 30. Retain as visible annotations;
# dropping strict semantic polish does NOT magically erase the prior evidence.
PRIOR_QC_HOLDS={
 25:'Chosen contradiction in missed/hit wording; arithmetic nevertheless computes missed=175-(40+25)=110.',
 200:'Rejected mixes daily/monthly rates and repeats operations; incorrect negative retained as a preference signal.',
 1287:'"Three times faster" could be read ambiguously; chosen follows GSM8K reference and the rejected output is numerically incorrect.',
 3314:'Rejected is internally inconsistent; it is the negative, not a promoted chosen response.',
 5464:'Rejected mishandles multiple volume conversions; negative is wrong, chosen conversions are consistent.',
 5711:'Chosen omits per-hour units from the final division; uses correct net $10/hour.',
 5912:'Chosen leaves the last $2 juice charge unlabeled; the amount and sum are correct.',
 6632:'Question stipulates two yellows per red as an abstract team conversion; not normal soccer disciplinary practice.',
}


def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()

def stable_bytes(rows):
 return (''.join(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n' for r in rows)).encode('utf-8')

def load_frozen():
 compact=ROOT/'inputs/mixed135.jsonl'; prior=ROOT/'inputs/decisions_advisory.jsonl'
 assert sha(compact)==COMPACT_SHA,'Compact input SHA mismatch'
 assert sha(prior)==PRIOR_SHA,'Prior review SHA mismatch'
 groups=[json.loads(x) for x in compact.read_text().splitlines()]
 decisions=[json.loads(x) for x in prior.read_text().splitlines()]
 assert len(groups)==len(decisions)==135
 assert sorted(g['source_index'] for g in groups)==sorted(d['source_index'] for d in decisions)
 assert len({d['source_index'] for d in decisions})==135
 # Independently recompute the same mechanical screen from the exact exported responses.
 mechanical, summary=screen(groups)
 assert summary['groups']==135
 assert summary['original_candidates_sha256']==ORIGINAL_SHA
 assert summary['groups_passing_mechanical_gates']==91
 top={d['source_index']:d for d in mechanical}
 for d in decisions:
  original=top[d['source_index']]['top_pair']
  assert (original is None)==(d['selected_chosen_sample_index'] is None)
  if original:
   assert d['selected_chosen_sample_index']==original['chosen_sample_index']
   assert d['selected_rejected_sample_index']==original['rejected_sample_index']
   assert d['pair_token_gap']==original['gap']
  else:
   assert d['status']=='MECHANICAL_REJECT'
 return {g['source_index']:g for g in groups},decisions,top


def reclassify(groups, prior, mechanical):
 assert not (set(CRITICAL_CHOSEN)&set(NEGATIVE_TOO_CHAOTIC))
 decisions=[]
 for old in sorted(prior,key=lambda d:d['source_index']):
  source=old['source_index']
  original_status=old['status']
  if original_status=='MECHANICAL_REJECT':
   decision='REJECT_MECHANICAL';reason='No pair meets frozen arithmetic/eligibility/format/length checks.'
  elif source in CRITICAL_CHOSEN:
   decision='REJECT_MATH_OR_MATERIAL_RELATION';reason=CRITICAL_CHOSEN[source]
  elif source in NEGATIVE_TOO_CHAOTIC:
   decision='REJECT_UNSUITABLE_NEGATIVE';reason=NEGATIVE_TOO_CHAOTIC[source]
  else:
   decision='PROVISIONAL_ACCEPT_QC_REQUIRED'
   if original_status=='SEMANTIC_HOLD_CHOSEN':
    reason='Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.'
   elif original_status=='QUALITY_HOLD_REJECTED':
    reason='Relaxed: chosen is arithmetically sound in existing review; messy/wrong reasoning occurs in the rejected response.'
   else:
    reason='Retained from prior provisional first-pass review under arithmetic-first policy.'
  chosen_i=old['selected_chosen_sample_index'];rej_i=old['selected_rejected_sample_index']
  if chosen_i is not None:
   chosen=groups[source]['responses'][chosen_i]
   rejected=groups[source]['responses'][rej_i]
   assert chosen['eligible'] is True and chosen['correct'] is True
   assert rejected['eligible'] is True and rejected['correct'] is False
   assert abs(chosen['generated_tokens']-rejected['generated_tokens'])==old['pair_token_gap']<=40
   assert chosen['native_eos_stop'] is True and not chosen['reached_token_cap']
   assert rejected['native_eos_stop'] is True and not rejected['reached_token_cap']
  decisions.append({
   'source_index':source,'decision':decision,
   'chosen_sample_index':chosen_i,'rejected_sample_index':rej_i,
   'pair_token_gap':old['pair_token_gap'],
   'prior_status':original_status,'prior_rationale':old['rationale'],
   'current_policy_reason':reason,
   'prior_qc_hold':PRIOR_QC_HOLDS.get(source),
   'approved_for_training':False,
  })
 counts=Counter(d['decision'] for d in decisions)
 assert counts=={'PROVISIONAL_ACCEPT_QC_REQUIRED':83,'REJECT_MECHANICAL':44,'REJECT_MATH_OR_MATERIAL_RELATION':7,'REJECT_UNSUITABLE_NEGATIVE':1},counts
 assert sum(d['prior_status']=='SEMANTIC_HOLD_CHOSEN' and d['decision']=='PROVISIONAL_ACCEPT_QC_REQUIRED' for d in decisions)==28
 assert sum(d['prior_status']=='QUALITY_HOLD_REJECTED' and d['decision']=='PROVISIONAL_ACCEPT_QC_REQUIRED' for d in decisions)==6
 assert len([d for d in decisions if d['prior_qc_hold']])==8
 return decisions,dict(counts)


def qc_docs(groups, decisions):
 accepted=[x for x in decisions if x['decision']=='PROVISIONAL_ACCEPT_QC_REQUIRED']
 rejects=[x for x in decisions if x['decision']!='PROVISIONAL_ACCEPT_QC_REQUIRED']
 rng=random.Random(20261024)
 qc_good=sorted(rng.sample(accepted,30),key=lambda x:x['source_index'])
 hard_reject=[x for x in rejects if x['decision']!='REJECT_MECHANICAL']
 mechanical_reject=[x for x in rejects if x['decision']=='REJECT_MECHANICAL']
 assert len(hard_reject)==8
 qc_bad=sorted(hard_reject+rng.sample(mechanical_reject,2),key=lambda x:x['source_index'])
 def doc(rows,good):
  intro=['# E004-P1 relaxed arithmetic-first QC — '+('30 provisional accepts' if good else '10 review rejects'),'','- QC selection seed: `20261024`, Python `random.Random`.','- Sample from source-sorted decisions; excludes no source on correctness/baseline grounds.','- Rejected sample is intentionally STRATIFIED: all eight nonmechanical holds + two random mechanical rejects. Not representative of all rejects.','- This is an **unreviewed audit worksheet**. These are not signed or independently approved training pairs.','- Do not repair source responses. Review arithmetic validity and material relationships; minor wording slips are allowed.','','---','']
  for d in rows:
   g=groups[d['source_index']]
   ci=d['chosen_sample_index']; wi=d['rejected_sample_index']
   chosen=None;wrong=None
   if ci is not None:
    chosen=g['responses'][ci];wrong=g['responses'][wi]
   else:
    correct=[x for x in g['responses'] if x['eligible'] and x['correct']]
    bad=[x for x in g['responses'] if x['eligible'] and not x['correct']]
    pairs=sorted((abs(a['generated_tokens']-b['generated_tokens']),a['sample_index'],b['sample_index'],a,b) for a in correct for b in bad)
    _,ci,wi,chosen,wrong=pairs[0]
   intro.extend([f'## Source {d["source_index"]} — chosen sample {ci} / rejected sample {wi}',
    '',f'- Current decision: `{d["decision"]}`',f'- Previous review: `{d["prior_status"]}`',f'- Old concern: {d["prior_rationale"]}',f'- New policy reason: {d["current_policy_reason"]}',f'- Previous QC flag: {d["prior_qc_hold"] or "none"}',
    '- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.','',
    '**Question:**','','```text',g['prompt'].strip(),'```','','**Chosen:**','','```text',chosen['response'].strip(),'```','','**Rejected:**','','```text',wrong['response'].strip(),'```','','**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain','','**Reason:**','','---',''])
  return '\n'.join(intro)+'\n'
 return qc_good,qc_bad,doc(qc_good,True),doc(qc_bad,False)


def read_concatenated_json(path):
 text=path.read_text(encoding='utf-8'); decoder=json.JSONDecoder(); pos=0; out=[]
 while pos<len(text):
  while pos<len(text) and text[pos].isspace():pos+=1
  if pos==len(text):break
  item,pos=decoder.raw_decode(text,pos)
  out.append(item)
 return out


def baseline_join(path,decisions):
 assert sha(path)==COVERAGE_SHA,'Coverage SHA mismatch'
 records=read_concatenated_json(path)
 assert len(records)==250
 by={r['source_index']:r for r in records}
 assert len(by)==250
 selected={x['source_index'] for x in decisions if x['decision']=='PROVISIONAL_ACCEPT_QC_REQUIRED'}
 mixed={x['source_index'] for x in decisions}
 assert mixed<=set(by)
 assert sum(not by[i]['greedy_correct'] for i in mixed)==51
 assert sum(not by[i]['greedy_correct'] for i in by)==105
 return {'provisional_accepted':len(selected),'greedy_wrong':sum(not by[i]['greedy_correct'] for i in selected),'greedy_correct':sum(by[i]['greedy_correct'] for i in selected),'baseline_error_rate_training_partition':round(sum(not by[i]['greedy_correct'] for i in selected)/len(selected),6),'in_sample_only':True}


def produce(coverage=None):
 groups,prior,mechanical=load_frozen()
 decisions,counts=reclassify(groups,prior,mechanical)
 good,bad,doc_good,doc_bad=qc_docs(groups,decisions)
 payload=stable_bytes(decisions)
 summary={
  'schema':'e004_p1_arithmetic_first_relaxed_advisory_v1',
  'compact_input_sha256':COMPACT_SHA,
  'original_candidates_sha256':ORIGINAL_SHA,
  'prior_advisory_decisions_sha256':PRIOR_SHA,
  'decision_records_sha256':hashlib.sha256(payload).hexdigest(),
  'group_counts':dict(sorted(counts.items())),
  'mixed_groups':135,'generated_pilot_questions':250,
  'mechanical_pass_groups':91,'provisional_pairs':83,
  'provisional_yield_per_mixed':round(83/135,6),
  'provisional_yield_per_pilot_question':round(83/250,6),
  'qc_accepted30_source_indices':[x['source_index'] for x in good],
  'qc_rejected10_source_indices':[x['source_index'] for x in bad],
  'qc_sampling_seed':20261024,
  'qc_sample_policy':'30 random provisional accepts, eight hard rejects plus two random mechanical rejects (stratified)',
  'provisional_does_not_mean_certified':True,
  'approved_for_training':0,'training_performed':False,'official_test_used':False,
  'same_assistant_prior_review_not_independent':True,
  'data_modified':False,
 }
 if coverage:summary['baseline_overlap']=baseline_join(Path(coverage),decisions)
 return decisions,summary,payload,doc_good,doc_bad


def main():
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');p.add_argument('--coverage',default=None)
 args=p.parse_args(); decisions,summary,payload,good,bad=produce(args.coverage)
 files={'decisions_relaxed.jsonl':payload,'qc_accepted30_unreviewed.md':good.encode(),'qc_rejected10_unreviewed.md':bad.encode()}
 outputs=ROOT/'outputs'
 if args.verify:
  for name,data in files.items():
   existing=(outputs/name).read_bytes(); assert existing==data,f'Output differs: {name}'
  loaded=json.loads((outputs/'summary.json').read_text())
  assert {k:v for k,v in summary.items() if k!='baseline_overlap'}==loaded
  print('Frozen inputs, arithmetic screen, pair selection, report and samples: VERIFIED')
  print(json.dumps(summary,indent=2,sort_keys=True))
 else:
  outputs.mkdir(parents=True,exist_ok=True)
  for name,data in files.items():
   path=outputs/name
   if path.exists():assert path.read_bytes()==data,f'Refusing overwrite: {name}'
   else:path.write_bytes(data)
  summary_path=outputs/'summary.json';bytes_data=(json.dumps(summary,sort_keys=True,indent=2)+'\n').encode()
  if summary_path.exists():assert summary_path.read_bytes()==bytes_data,'Refusing overwrite summary'
  else:summary_path.write_bytes(bytes_data)
  print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__':main()
