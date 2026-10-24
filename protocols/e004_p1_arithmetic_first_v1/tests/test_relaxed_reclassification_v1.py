import hashlib
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/reclassify_arithmetic_first_v1.py'
spec=importlib.util.spec_from_file_location('e004_relaxed',SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ReclassificationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.groups,cls.prior,cls.mech=m.load_frozen()
  cls.rows,cls.counts=m.reclassify(cls.groups,cls.prior,cls.mech)
  cls.by={r['source_index']:r for r in cls.rows}

 def test_exact_input_hashes(self):
  self.assertEqual(m.sha(ROOT/'inputs/mixed135.jsonl'),m.COMPACT_SHA)
  self.assertEqual(m.sha(ROOT/'inputs/decisions_advisory.jsonl'),m.PRIOR_SHA)

 def test_counts(self):
  self.assertEqual(self.counts,{'PROVISIONAL_ACCEPT_QC_REQUIRED':83,'REJECT_MECHANICAL':44,'REJECT_MATH_OR_MATERIAL_RELATION':7,'REJECT_UNSUITABLE_NEGATIVE':1})

 def test_failclosed_exceptions(self):
  for i in m.CRITICAL_CHOSEN:
   self.assertEqual(self.by[i]['decision'],'REJECT_MATH_OR_MATERIAL_RELATION')
  for i in m.NEGATIVE_TOO_CHAOTIC:
   self.assertEqual(self.by[i]['decision'],'REJECT_UNSUITABLE_NEGATIVE')

 def test_relaxed_examples(self):
  for i in (25,1287,200,204,429,5711,5912,6632,1069,2192,3314,5464,6262,6730):
   self.assertEqual(self.by[i]['decision'],'PROVISIONAL_ACCEPT_QC_REQUIRED')

 def test_pair_integrity(self):
  for row in self.rows:
   if row['decision']=='PROVISIONAL_ACCEPT_QC_REQUIRED':
    self.assertLessEqual(row['pair_token_gap'],40)
    self.assertIsInstance(row['chosen_sample_index'],int)
    self.assertIsInstance(row['rejected_sample_index'],int)
   self.assertFalse(row['approved_for_training'])

 def test_frozen_original_advisory_reproduces_selection(self):
  for old in self.prior:
   top=self.mech[old['source_index']]['top_pair']
   if top:
    self.assertEqual(old['selected_chosen_sample_index'],top['chosen_sample_index'])
    self.assertEqual(old['selected_rejected_sample_index'],top['rejected_sample_index'])

 def test_qc_sampling_fixed_and_disjoint(self):
  yes,no,mdyes,mdno=m.qc_docs(self.groups,self.rows)
  self.assertEqual(len(yes),30)
  self.assertEqual(len(no),10)
  self.assertFalse(set(x['source_index'] for x in yes)&set(x['source_index'] for x in no))
  self.assertEqual(len([x for x in no if x['decision']=='REJECT_MECHANICAL']),2)
  self.assertEqual(mdyes.count('**Your QC decision:**'),30)
  self.assertEqual(mdno.count('**Your QC decision:**'),10)

 def test_deterministic_outputs(self):
  one=m.produce(); two=m.produce()
  self.assertEqual(one[1],two[1]);self.assertEqual(one[2],two[2]);self.assertEqual(one[3],two[3]);self.assertEqual(one[4],two[4])

 def test_baseline_parser_pretty_records(self):
  f=ROOT/'outputs/summary.json'
  # The frozen evaluation writer wrote concatenated pretty objects rather than standard JSONL.
  import tempfile
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'records.jsonl'
   p.write_text('{\n "source_index": 10\n}\n{\n "source_index":11\n}\n')
   self.assertEqual([x['source_index'] for x in m.read_concatenated_json(p)],[10,11])

if __name__=='__main__':unittest.main()
