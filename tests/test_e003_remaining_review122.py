"""Focused CPU-only invariants for the M3.15 seven-batch review exporter."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'prepare_e003_remaining_review122.py'
# Inside the user's repo, script and tests are siblings under root. Here too.
spec = importlib.util.spec_from_file_location('e003_remaining_review122_test_subject', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def record(source=81, sample=0, correct=False, eligible=True):
    ids = [42, m.NATIVE_EOS]
    return {'source_index': source, 'sample_index': sample,
            'sample_seed': 42 + source * 100 + sample, 'prompt': f'Question: Q{source}\nAnswer:',
            'reference_answer': '50', 'generated_token_ids': ids, 'generated_tokens': len(ids),
            'native_eos_stop': True, 'reached_token_cap': False,
            'eligible': eligible, 'correct': correct, 'extracted_answer': '50' if correct else '1',
            'response': f'Sample {sample} response. The answer is {50 if correct else 1}.'}


class RemainingReviewTests(unittest.TestCase):
    def setUp(self):
        self.example = SimpleNamespace(source_index=81, question='Q81', reference_answer=50)
        self.prompt = lambda question: f'Question: {question}\nAnswer:'

    def test_01_valid_record(self):
        m.validate_record(record(), self.example, self.prompt)

    def test_02_wrong_prompt_fails(self):
        rec = record(); rec['prompt'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'prompt'):
            m.validate_record(rec, self.example, self.prompt)

    def test_03_wrong_reference_fails(self):
        rec = record(); rec['reference_answer'] = '55'
        with self.assertRaisesRegex(ValueError, 'reference'):
            m.validate_record(rec, self.example, self.prompt)

    def test_04_wrong_seed_fails(self):
        rec = record(); rec['sample_seed'] += 1
        with self.assertRaisesRegex(ValueError, 'seed'):
            m.validate_record(rec, self.example, self.prompt)

    def test_05_invalid_eos_label_fails(self):
        rec = record(); rec['native_eos_stop'] = False
        with self.assertRaisesRegex(ValueError, 'EOS'):
            m.validate_record(rec, self.example, self.prompt)

    def test_06_length_and_cap_protected(self):
        rec = record(); rec['generated_tokens'] = 1
        with self.assertRaisesRegex(ValueError, 'token count'):
            m.validate_record(rec, self.example, self.prompt)
        rec = record(); rec['reached_token_cap'] = True
        with self.assertRaisesRegex(ValueError, 'Token cap'):
            m.validate_record(rec, self.example, self.prompt)

    def test_07_mixed_eligibility(self):
        rows = [record(sample=i, correct=(i == 0)) for i in range(4)]
        self.assertTrue(m.is_mixed(rows))
        rows[0]['eligible'] = False
        self.assertFalse(m.is_mixed(rows))

    def test_08_remaining_inventory(self):
        remaining = (m.FIRST_BATCH + list(range(2000, 2100)) + m.LAST_BATCH)
        self.assertEqual(len(remaining), 122)
        reviewed = list(range(8000, 8024))
        groups = {}
        for source in remaining + reviewed:
            groups[source] = [record(source, i, correct=(i == 0)) for i in range(4)]
        self.assertEqual(m.choose_remaining(groups, reviewed), remaining)
        with self.assertRaisesRegex(ValueError, 'Reviewed'):
            m.choose_remaining(groups, reviewed[:-1] + [1])

    def test_09_batch_sizes(self):
        self.assertEqual(list(map(len, m.partition(list(range(122))))), [20]*6 + [2])

    def test_10_renders_all_original_responses(self):
        rows = [record(sample=i, correct=(i == 0)) for i in range(4)]
        report = m.render_review(0, [81], {81: self.example}, {81: rows})
        self.assertEqual(report.count('COMPLETE ORIGINAL REASONING:'), 4)
        for row in rows:
            self.assertIn(row['response'], report)
        self.assertIn('no pair is approved', report)
        self.assertIn('ORIGINAL reference labels; no erratum', report)

    def test_11_preflight_does_not_write(self):
        indices = m.FIRST_BATCH + list(range(2000, 2100)) + m.LAST_BATCH
        examples = {i: SimpleNamespace(source_index=i, question=f'Q{i}', reference_answer=50)
                    for i in indices}
        groups = {i: [record(i, s, correct=(s == 0)) for s in range(4)] for i in indices}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch.object(m, 'load_and_verify', return_value=(examples, groups, indices, {})), \
                 patch.object(m.subprocess, 'check_output', return_value='a'*40+'\n'):
                m.prepare(root, root/'target', 'a'*40, True)
            self.assertFalse((root/'target').exists())

    def test_12_creates_complete_batches_and_refuses_overwrite(self):
        indices = m.FIRST_BATCH + list(range(2000, 2100)) + m.LAST_BATCH
        examples = {i: SimpleNamespace(source_index=i, question=f'Q{i}', reference_answer=50)
                    for i in indices}
        groups = {i: [record(i, s, correct=(s == 0)) for s in range(4)] for i in indices}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); target = root/'target'
            with patch.object(m, 'load_and_verify', return_value=(examples, groups, indices, {})), \
                 patch.object(m.subprocess, 'check_output', return_value='a'*40+'\n'):
                m.prepare(root, target, 'a'*40, False)
                self.assertEqual(len(list(target.iterdir())), 15)
                manifest = json.loads((target/'manifest.json').read_text())
                self.assertEqual(manifest['remaining_groups'], 122)
                self.assertEqual(len(manifest['batches']), 7)
                self.assertEqual(manifest['batches'][-1]['source_indices'], m.LAST_BATCH)
                self.assertFalse(manifest['flags']['training_approved'])
                with self.assertRaisesRegex(ValueError, 'overwrite'):
                    m.prepare(root, target, 'a'*40, False)


    def test_13_no_git_loose_ref_passes_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            branch = root / '.git' / 'refs' / 'heads' / 'main'
            branch.parent.mkdir(parents=True)
            (root / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
            branch.write_text('a' * 40 + '\n')
            data = self._fake_preflight_inputs()
            with patch.object(m, 'load_and_verify', return_value=data), \
                 patch.object(m.subprocess, 'check_output', side_effect=FileNotFoundError):
                m.prepare(root, root / 'output', 'a' * 40, True)
            self.assertFalse((root / 'output').exists())

    def test_14_no_git_packed_ref_passes_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gitdir = root / '.git'
            gitdir.mkdir()
            (gitdir / 'HEAD').write_text('ref: refs/heads/main\n')
            (gitdir / 'packed-refs').write_text(
                '# pack-refs with: peeled fully-peeled sorted\n'
                + ('b' * 40) + ' refs/heads/main\n'
            )
            self.assertEqual(m.git_head_from_files(root), 'b' * 40)

    def test_15_no_git_mismatched_revision_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            branch = root / '.git' / 'refs' / 'heads' / 'main'
            branch.parent.mkdir(parents=True)
            (root / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
            branch.write_text('a' * 40 + '\n')
            with patch.object(m.subprocess, 'check_output', side_effect=FileNotFoundError):
                with self.assertRaisesRegex(ValueError, 'Code revision'):
                    m.prepare(root, root / 'output', 'b' * 40, True)
            self.assertFalse((root / 'output').exists())

    def test_16_detached_head_and_linked_worktree(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gitdir = root / 'meta'
            gitdir.mkdir()
            (root / '.git').write_text('gitdir: meta\n')
            (gitdir / 'HEAD').write_text('c' * 40 + '\n')
            self.assertEqual(m.git_head_from_files(root), 'c' * 40)

    def _fake_preflight_inputs(self):
        indices = m.FIRST_BATCH + list(range(2000, 2100)) + m.LAST_BATCH
        examples = {i: SimpleNamespace(source_index=i, question=f'Q{i}', reference_answer=50)
                    for i in indices}
        groups = {i: [record(i, s, correct=(s == 0)) for s in range(4)] for i in indices}
        return examples, groups, indices, {}


if __name__ == '__main__':
    unittest.main()
