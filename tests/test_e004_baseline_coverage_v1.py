"""Pure CPU tests: no GPU, no model weights, no external files."""
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from scripts.evaluate_e004_baseline_coverage_v1 import (
    ADAPTER_SHA, CANDIDATES_SHA, CODE_REV_E004_GENERATOR, CONFIG_SHA,
    is_mixed, report_rows, validate_selection, write_immutable, bytes_json,
)


class E004CoverageTests(unittest.TestCase):
    def setUp(self):
        self.selected = list(range(250))
        self.mixed = set(range(135))
        self.predictions = {i: {'correct': i % 2 == 0} for i in self.selected}

    def test_basic_contingency(self):
        result = report_rows(self.predictions, self.selected, self.mixed)
        self.assertEqual(result['all_250']['total'], 250)
        self.assertEqual(result['all_250']['correct'], 125)
        self.assertEqual(result['mixed_135']['correct'], 68)
        self.assertEqual(result['mixed_135']['wrong'], 67)
        self.assertEqual(result['nonmixed_115']['correct'], 57)
        self.assertEqual(result['nonmixed_115']['wrong'], 58)

    def test_no_lookahead_into_validation(self):
        with self.assertRaisesRegex(ValueError, 'Prediction index set mismatch'):
            report_rows({**{k:v for k,v in self.predictions.items() if k != 100}, 8000:{'correct':False}}, self.selected, self.mixed)

    def test_missing_result_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Prediction count'):
            report_rows({k:v for k,v in self.predictions.items() if k!=100},self.selected,self.mixed)

    def test_zero_error_denominator(self):
        all_correct = {i:{'correct':True} for i in self.selected}
        result=report_rows(all_correct,self.selected,self.mixed)
        self.assertIsNone(result['mixed_share_of_all_baseline_errors'])
        self.assertEqual(result['error_rate_mixed_minus_nonmixed'], 0)

    def test_mixed_eligibility(self):
        group = [dict(correct=True,eligible=True), dict(correct=False,eligible=True)]
        self.assertTrue(is_mixed(group))
        group[1]['eligible'] = False
        self.assertFalse(is_mixed(group))
        group[1]['eligible'] = True
        group[0]['correct'] = False
        self.assertFalse(is_mixed(group))

    def test_immutable_writer_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'out.json'
            write_immutable(path,bytes_json({'v':1}))
            with self.assertRaises(FileExistsError):
                write_immutable(path,bytes_json({'v':2}))
            self.assertEqual(json.loads(path.read_text()),{'v':1})

    def test_selection_validation_good(self):
        metadata, summary, candidates, training = self._fixture()
        selected, by_idx, mixed, groups = validate_selection(
            metadata,summary,candidates,training,prompt_func=lambda q:'Q:'+q)
        self.assertEqual(selected,list(range(250)))
        self.assertEqual(len(mixed),135)
        self.assertEqual(len(groups[0]),4)

    def test_reject_nontraining_source(self):
        metadata, summary, candidates, training = self._fixture()
        training[9].source_index=7001
        with self.assertRaisesRegex(ValueError, 'non-training'):
            validate_selection(metadata,summary,candidates,training,prompt_func=lambda q:'Q:'+q)

    def test_reject_reference_tampering(self):
        metadata, summary, candidates, training = self._fixture()
        candidates[0]['reference_answer']='999'
        with self.assertRaisesRegex(ValueError, 'Reference mismatch'):
            validate_selection(metadata,summary,candidates,training,prompt_func=lambda q:'Q:'+q)

    @staticmethod
    def _fixture():
        training=[SimpleNamespace(source_index=i,question=f'q{i}',reference_answer=str(i))
                  for i in range(6726)]
        metadata=dict(selected_source_indices=list(range(250)),
                      code_revision=CODE_REV_E004_GENERATOR,config_sha256=CONFIG_SHA)
        summary=dict(candidates_sha256=CANDIDATES_SHA,code_revision=CODE_REV_E004_GENERATOR,
                     config_sha256=CONFIG_SHA,reference_policy_adapter_sha256=ADAPTER_SHA,
                     training_performed=False,official_test_used=False,
                     pilot_questions=250,candidates=1000,mixed_groups_with_potential_pair=135)
        candidates=[]
        for i in range(250):
            for j in range(4):
                candidates.append(dict(source_index=i,sample_index=j,prompt=f'Q:q{i}',
                    reference_answer=str(i),eligible=True,correct=(j>0 if i<135 else True)))
        return metadata, summary, candidates, training


if __name__=='__main__':
    unittest.main()
