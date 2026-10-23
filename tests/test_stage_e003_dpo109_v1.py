#!/usr/bin/env python3
"""Unit and synthetic 124-source integration tests (no training or repo input changes)."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import sys
import unittest
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
import zipfile

HERE=Path(__file__).resolve()
REPO=HERE.parents[1]
ATTACHMENTS=Path('/mnt/data')
if not (ATTACHMENTS/'e003_pair_review124_v1.md').is_file():
    ATTACHMENTS=Path.home()/'Downloads'
PROJECT_FILES=ATTACHMENTS if ((ATTACHMENTS/'e003_pair_review124_v1.md').is_file()
                               and (ATTACHMENTS/'e003_final_review_signed_off_package.zip').is_file()) else None
ADVISORY_FILE= (ATTACHMENTS/'e003_candidate124_second_pass_advisory_v1.json')
if not ADVISORY_FILE.is_file():
    ADVISORY_FILE=REPO/'configs/preference/e003_candidate124_second_pass_advisory_v1.json'
BUILDER=HERE.parents[1]/'scripts/stage_e003_dpo109_v1.py'
spec=importlib.util.spec_from_file_location('e003_builder',BUILDER)
b=importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def example_fixture():
    assert PROJECT_FILES, 'Fixture document unavailable; set SKIP fixture in host tests'
    review=(PROJECT_FILES/'e003_pair_review124_v1.md').read_text(encoding='utf-8')
    with zipfile.ZipFile(PROJECT_FILES/'e003_final_review_signed_off_package.zip') as z:
        signed=json.loads(z.read('e003_all108_final_review_signed_off.json'))
    advisory=json.loads(ADVISORY_FILE.read_text())
    parts=re.findall(r'(?ms)^## Source (\d+) — .*?\n(.*?)(?=^---\n|\Z)', review)
    assert len(parts)==124,len(parts)
    pairs=[]
    for source_str,body in parts:
        src=int(source_str)
        samples=re.search(r'Chosen sample: (\d+)\nRejected sample: (\d+)\nAbsolute token gap: (\d+)',body)
        ci,ri,gap=(int(x) for x in samples.groups())
        prompt=body.split('### Prompt\n\n',1)[1].split('\n\n### Chosen response',1)[0]
        ch=body.split('### Chosen response\n\n',1)[1].split('\n\n### Rejected response',1)[0]
        rj=body.split('### Rejected response\n\n',1)[1].split('\n\n### Independent decision',1)[0]
        # Fixture generated token streams preserve only the count/gap/EOS invariants.
        pairs.append({'source_index':src,'prompt':prompt,'chosen':ch,'rejected':rj,
              'chosen_sample_index':ci,'rejected_sample_index':ri,
              'chosen_generated_tokens':100+gap,'rejected_generated_tokens':100,
              'chosen_generated_token_ids':[99]*(99+gap)+[151643],
              'rejected_generated_token_ids':[98]*99+[151643],
              'absolute_token_gap':gap,'native_eos_token_id':151643,
              'training_reference_answer':'50' if src==5436 else '1',
              'original_reference_answer':'55' if src==5436 else '1',
              'independent_pair_signoff':src==5436,
              'reference_training_only_erratum':src==5436,
              'full_dataset_approved':False,'training_authorized':False,
              'training_performed':False,'official_test_used':False})
    return pairs,advisory,signed


class TestDPOStage(unittest.TestCase):
    def test_normalize_question(self):
        self.assertEqual(b.normalize_question(' Question:  How   many?\nAnswer: '),'how many?')
    def test_shingles(self):
        self.assertEqual(b.shingles('one two three four five six'),
                         {('one','two','three','four','five'),('two','three','four','five','six')})
    def test_validation_split_and_duplicate_guard(self):
        train=[SimpleNamespace(source_index=i,question=f'Unrelated training question number {i} about arithmetic')
               for i in range(6726)]
        val=[SimpleNamespace(source_index=i,question=f'Independent validation question number {i} distinct from training')
             for i in range(6726,7473)]
        fake=SimpleNamespace(load_gsm8k_split=lambda _raw,_split,which:train if which=='training' else val)
        with tempfile.TemporaryDirectory() as td, patch.dict(sys.modules,{'llm_post_training.data.loader':fake}):
            stage=[{'source_index':i,'prompt':f'Question: Unrelated training question number {i} about arithmetic\nAnswer:'}
                   for i in range(109)]
            result=b.validation_clearance(Path(td),stage)
            self.assertEqual(result['selected_sources_in_training'],109)
            stage[0]['prompt']='Question: Independent validation question number 6726 distinct from training\nAnswer:'
            with self.assertRaisesRegex(ValueError,'prompt differs'):
                b.validation_clearance(Path(td),stage)

    def test_selection_real_signed_mock_originals(self):
        if not PROJECT_FILES:self.skipTest('Uploaded evidence not available on host')
        original,advisory,signed=example_fixture()
        rows,notes=b.select_rows(original,advisory,signed)
        self.assertEqual(len(rows),109)
        self.assertEqual(len(notes),109)
        self.assertEqual([n['source_index'] for n in notes],sorted(n['source_index'] for n in notes))
        self.assertEqual(sum(n['approval_record']=='source5436_prior_pinned_pair_approval' for n in notes),1)
        self.assertEqual(sum(n['sft_correction_not_applied_to_dpo'] for n in notes),3)
        self.assertTrue(all(n['training_authorized'] is False for n in notes))
    def test_fail_closed_tampered_approved_pair(self):
        if not PROJECT_FILES:self.skipTest('Uploaded evidence not available on host')
        original,advisory,signed=example_fixture()
        tampered=copy.deepcopy(original)
        next(p for p in tampered if p['source_index']==528)['chosen']+=' incorrect rewrite'
        with self.assertRaisesRegex(ValueError,'review hash mismatch'):
            b.select_rows(tampered,advisory,signed)
    def test_fail_closed_changed_pair_identity(self):
        if not PROJECT_FILES:self.skipTest('Uploaded evidence not available on host')
        original,advisory,signed=example_fixture()
        tampered=copy.deepcopy(original)
        next(p for p in tampered if p['source_index']==528)['chosen_sample_index']=3
        with self.assertRaisesRegex(ValueError,'Advisory identity mismatch'):
            b.select_rows(tampered,advisory,signed)
    def test_fail_closed_unsafe_training_flag(self):
        if not PROJECT_FILES:self.skipTest('Uploaded evidence not available on host')
        original,advisory,signed=example_fixture()
        tampered=copy.deepcopy(original)
        next(p for p in tampered if p['source_index']==528)['training_authorized']=True
        with self.assertRaisesRegex(ValueError,'safety flag'):
            b.select_rows(tampered,advisory,signed)
    def test_fail_closed_insert_excluded_source(self):
        if not PROJECT_FILES:self.skipTest('Uploaded evidence not available on host')
        original,advisory,signed=example_fixture()
        tampered=[p for p in original if p['source_index']!=5436]
        with self.assertRaisesRegex(ValueError,'Preview pair count not 124'):
            b.select_rows(tampered,advisory,signed)

if __name__=='__main__':unittest.main()
