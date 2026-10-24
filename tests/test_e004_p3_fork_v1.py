"""Offline, non-training E004-P3 fork structural/regression tests."""
import ast
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

path = Path('scripts/build_e004_p3_fork_v1.py')
spec = importlib.util.spec_from_file_location('e004_p3_fork_builder_test', path)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class E004P3ForkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = builder.generated_contents()
        cls.source = cls.files[builder.P3_SCRIPT].decode('utf-8')
        cls.config = json.loads(cls.files[builder.P3_CONFIG])
        cls.tree = ast.parse(cls.source)
        cls.functions = {
            n.name: n for n in cls.tree.body if isinstance(n, ast.FunctionDef)
        }

    def test_p2_inputs_pinned(self):
        for file, expected in (
            (builder.P2_SCRIPT, builder.P2_GENERATOR_SHA),
            (builder.P2_CONFIG, builder.P2_CONFIG_SHA),
            (Path(builder.P2_DIR) / 'candidates.jsonl', builder.P2_CANDIDATES_SHA),
            (Path(builder.P2_DIR) / 'metadata.json', builder.P2_METADATA_SHA),
            (Path(builder.P2_DIR) / 'summary.json', builder.P2_SUMMARY_SHA),
        ):
            self.assertEqual(builder.sha_bytes(file.read_bytes()), expected)

    def test_generated_contents_reproducible(self):
        self.assertEqual(self.files, builder.generated_contents())
        for path, data in self.files.items():
            self.assertEqual(path.read_bytes(), data)

    def test_original_generation_logic_unchanged(self):
        builder.verify_inherited_functions(builder.P2_SCRIPT.read_text(), self.source)

    def test_config_preserves_weights_and_decoding(self):
        old = json.loads(builder.P2_CONFIG.read_text())
        new = dict(self.config)
        self.assertEqual(new.pop('config_version'), 'e004_p3_v1')
        self.assertEqual(new.pop('purpose'), 'e004_p3_candidate_generation_only')
        self.assertEqual(new.pop('selection_seed'), 42006)
        self.assertEqual(new.pop('pilot_questions'), 1200)
        self.assertEqual(new.pop('excluded_p2_dir'), builder.P2_DIR)
        for name in ('config_version','purpose','selection_seed','pilot_questions'):
            old.pop(name)
        self.assertEqual(new, old)
        self.assertEqual(self.config['samples_per_question'], 4)
        self.assertEqual(self.config['generation']['temperature'], 0.8)
        self.assertEqual(self.config['generation']['top_p'], 0.95)
        self.assertEqual(self.config['generation']['max_new_tokens'], 256)

    def test_three_distinct_selection_functions(self):
        for name in ('choose_p1_disjoint_questions', 'choose_p2_disjoint_questions',
                     'choose_disjoint_questions'):
            self.assertIn(name, self.functions)
        self.assertEqual(self.source.count('SELECTED_COUNT = 1200'), 1)
        for name in ('choose_p1_disjoint_questions', 'choose_p2_disjoint_questions'):
            snippet = ast.get_source_segment(self.source, self.functions[name])
            self.assertNotIn('SELECTED_COUNT', snippet, name)

    def test_selection_sha_and_disjointness_gates(self):
        new = ast.get_source_segment(self.source, self.functions['choose_disjoint_questions'])
        for marker in ('random.Random(42006)', 'len(excluded) == 788',
                       'len(remaining) == 5938', '== 1200', builder.P3_SELECTION_SHA,
                       'p2_meta.get("selected_source_indices") == p2_indices',
                       'p2_meta.get("official_test_used") is False'):
            self.assertIn(marker, new)
        self.assertNotIn('torch.', new)
        self.assertNotIn('test.jsonl', new)
        self.assertNotIn('validation', new)

    def test_prior_provenance_is_pinned(self):
        new = ast.get_source_segment(self.source, self.functions['choose_disjoint_questions'])
        for digest in (builder.P2_GENERATOR_SHA, builder.P2_CONFIG_SHA,
                       builder.P2_CANDIDATES_SHA, builder.P2_METADATA_SHA,
                       builder.P2_SUMMARY_SHA):
            self.assertIn(digest, new)

    def test_metadata_contains_p2_exclusion_and_hashes(self):
        for marker in ('"excluded_p2_source_indices": excluded_p2',
                       '"p2_metadata_sha256": sha256_file(',
                       '"p2_summary_sha256": sha256_file(',
                       '"p2_candidates_sha256":',
                       '"run_type": "e004_p3_candidate_generation"'):
            self.assertIn(marker, self.source)

    def test_no_silent_overwrite_or_training(self):
        script = ast.get_source_segment(self.source, self.functions['main'])
        for marker in ('require(not args.output_dir.exists()',
                       'flock(', '--preflight-only', '--resume', '--stop-after-new-groups'):
            if marker.startswith('--'):
                self.assertIn(marker, script)
            else:
                self.assertIn(marker, script)
        self.assertNotIn('optimizer.step(', script)
        self.assertNotIn('trainer.train(', script)

    def test_tampering_fails_closed(self):
        altered = builder.P2_SCRIPT.read_text().replace('SCALE_VERSION = "e004_p2_v1"',
                                                        'SCALE_VERSION = "unknown"')
        with self.assertRaises(AssertionError):
            builder.patch_source(altered)


if __name__ == '__main__':
    unittest.main()
