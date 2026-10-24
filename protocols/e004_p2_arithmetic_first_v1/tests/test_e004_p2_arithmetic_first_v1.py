import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / 'scripts' / 'review_p2_arithmetic_first_v1.py'
SPEC = importlib.util.spec_from_file_location('p2_reviewer_test', SOURCE_PATH)
assert SPEC and SPEC.loader
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


class E004P2ArithmeticFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = R.read_groups(ROOT / 'inputs' / 'mixed137.jsonl')
        cls.decisions, cls.mechanical, cls.mechanical_summary = R.classify(cls.groups)
        cls.summary, cls.outputs = R.generate(ROOT / 'inputs' / 'mixed137.jsonl')

    def test_original_input_and_p1_mechanical_reference_pinned(self):
        self.assertEqual(R.digest((ROOT/'inputs'/'mixed137.jsonl').read_bytes()), R.INPUT_SHA)
        self.assertEqual(R.digest((ROOT/'references'/'strict_equation_screen_reference_v1.py').read_bytes()), 'dbf7ba5a335748c799998975f812b2a33bf1d11709607207c5f9f825232b7df5')
        self.assertEqual(R.digest((ROOT/'scripts'/'p2_screen_v1.py').read_bytes()), 'd42011b8e9f89d28f4ab556429dd3041f5a96fca76f102167600281e10107a0e')

    def test_narrow_mechanical_fork_only(self):
        original = (ROOT/'references'/'strict_equation_screen_reference_v1.py').read_text()
        fork = (ROOT/'scripts'/'p2_screen_v1.py').read_text()
        substitutions = [
            ('fe0ce3a7bb4cd20fedf4ee25e15e171e0047ff786ae39f16c2db4118934dcff0', 'fe4c4f034417b73be7862975889e102882be6d9f67352d62b9a568eaeb66faf9'),
            ('314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628', '568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79'),
            ('len(groups)==135', 'len(groups)==137'),
            ('"Not 135 groups"', '"Not 137 groups"'),
            ('"e004_p1_strict_arithmetic_screen_v1"', '"e004_p2_arithmetic_first_mechanical_v1"'),
            ('E004-P1', 'E004-P2'),
        ]
        for a,b in substitutions:
            self.assertIn(a, original)
            original = original.replace(a, b)
        self.assertEqual(original, fork)

    def test_137_mixed_groups_and_130_length_compatible(self):
        self.assertEqual(len(self.groups), 137)
        self.assertEqual(self.mechanical_summary['groups_length_compatible'], 130)
        self.assertEqual(self.mechanical_summary['groups_passing_mechanical_gates'], 87)

    def test_counts_advisory_and_no_training(self):
        from collections import Counter
        counts = Counter(d['decision'] for d in self.decisions)
        self.assertEqual(dict(counts), {'PROVISIONAL_ACCEPT_QC_REQUIRED':80,'REJECT_MECHANICAL':50,'REJECT_MATH_OR_MATERIAL_RELATION':7})
        self.assertFalse(self.summary['training_performed'])
        self.assertEqual(self.summary['approved_training_pairs'], 0)
        self.assertTrue(self.summary['manual_assistant_review_is_not_independent_certification'])

    def test_correct_incorrect_pair_integrity_and_gap(self):
        by = {g['source_index']:g for g in self.groups}
        for d in self.decisions:
            if d['chosen_sample_index'] is None:
                self.assertEqual(d['decision'], 'REJECT_MECHANICAL')
                continue
            chosen = by[d['source_index']]['responses'][d['chosen_sample_index']]
            rejected = by[d['source_index']]['responses'][d['rejected_sample_index']]
            self.assertTrue(chosen['eligible'] and chosen['correct'])
            self.assertTrue(rejected['eligible'] and not rejected['correct'])
            self.assertEqual(abs(chosen['generated_tokens']-rejected['generated_tokens']), d['pair_token_gap'])
            self.assertLessEqual(d['pair_token_gap'], 40)
            self.assertTrue(chosen['native_eos_stop'] and rejected['native_eos_stop'])

    def test_holds_are_explicit_and_subset_of_mechanical_passes(self):
        actual = {d['source_index'] for d in self.decisions if d['decision']=='REJECT_MATH_OR_MATERIAL_RELATION'}
        self.assertEqual(actual, set(R.MATERIAL_HOLDS))
        self.assertEqual(len(actual), 7)
        for d in self.decisions:
            self.assertFalse(d['approved_for_training'])

    def test_qc_fixed_disjoint_and_stratified(self):
        a, b = R.qc_samples(self.decisions)
        self.assertEqual(len(a), 30)
        self.assertEqual(len(b), 10)
        self.assertEqual({d['source_index'] for d in a}, set(self.summary['qc_accepted30_source_indices']))
        self.assertEqual({d['source_index'] for d in b}, set(self.summary['qc_rejected10_source_indices']))
        self.assertEqual(len([d for d in b if d['decision']=='REJECT_MECHANICAL']), 3)
        self.assertEqual(len([d for d in b if d['decision']=='REJECT_MATH_OR_MATERIAL_RELATION']), 7)
        self.assertFalse(set(self.summary['qc_accepted30_source_indices']) & set(self.summary['qc_rejected10_source_indices']))

    def test_byte_exact_outputs(self):
        for name, content in self.outputs.items():
            self.assertEqual((ROOT / 'outputs' / 'review' / name).read_bytes(), content, name)

    def test_malformed_or_changed_input_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)/'bad.jsonl'
            p.write_bytes((ROOT/'inputs'/'mixed137.jsonl').read_bytes()+b' ')
            with self.assertRaises(AssertionError):
                R.read_groups(p)

    def test_manual_holds_not_automatic_transfer(self):
        self.assertTrue(self.summary['p2_advisory_exclusions_not_transferable_automatic_filter'])
        self.assertTrue(all(d['manual_exception_not_automated'] for d in self.decisions if d['decision']=='REJECT_MATH_OR_MATERIAL_RELATION'))

if __name__ == '__main__': unittest.main()
