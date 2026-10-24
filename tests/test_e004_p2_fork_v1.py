"""Deterministic source and disjointness checks for E004 P2; no GPU."""
import ast
import hashlib
import importlib.util
import json
import random
import unittest
from pathlib import Path
from types import SimpleNamespace

BUILDER_PATH = Path('scripts/build_e004_p2_fork_v1.py')
spec = importlib.util.spec_from_file_location('e004_p2_builder_under_test', BUILDER_PATH)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class E004P2ForkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = builder.generated_contents()
        cls.source = cls.files[builder.P2_SCRIPT].decode('utf-8')
        cls.config = json.loads(cls.files[builder.P2_CONFIG])

    def test_exact_p1_source_is_pinned(self):
        self.assertEqual(builder.sha_bytes(builder.P1_SCRIPT.read_bytes()), builder.P1_GENERATOR_SHA)
        self.assertEqual(builder.sha_bytes(builder.P1_CONFIG.read_bytes()), builder.P1_CONFIG_SHA)

    def test_generated_files_reproducible(self):
        self.assertEqual(self.files, builder.generated_contents())
        for path, content in self.files.items():
            self.assertEqual(path.read_bytes(), content, f'Generated fork not installed: {path}')

    def test_frozen_generation_logic_unchanged(self):
        builder.verify_inherited_functions(builder.P1_SCRIPT.read_text(), self.source)

    def test_config_freezes_generation_hyperparameters(self):
        old = json.loads(builder.P1_CONFIG.read_text())
        new = dict(self.config)
        self.assertEqual(new.pop('config_version'), 'e004_p2_v1')
        self.assertEqual(new.pop('purpose'), 'e004_p2_candidate_generation_only')
        self.assertEqual(new.pop('selection_seed'), 42005)
        self.assertEqual(new.pop('excluded_p1_dir'), builder.P1_DIR)
        for k in ('config_version', 'purpose', 'selection_seed'):
            old.pop(k)
        self.assertEqual(new, old)
        self.assertEqual(self.config['generation']['temperature'], 0.8)
        self.assertEqual(self.config['generation']['top_p'], 0.95)
        self.assertEqual(self.config['generation']['max_new_tokens'], 256)
        self.assertEqual(self.config['samples_per_question'], 4)

    def test_p2_provenance_fields_present(self):
        for part in ('"excluded_p1_source_indices": excluded_p1',
                     '"p1_metadata_sha256": sha256_file',
                     '"p1_summary_sha256": sha256_file',
                     '"p1_candidates_sha256":',
                     '"run_type": "e004_p2_candidate_generation"'):
            self.assertIn(part, self.source)

    def test_code_is_parseable_and_two_distinct_selection_functions(self):
        tree = ast.parse(self.source)
        names = [x.name for x in tree.body if isinstance(x, ast.FunctionDef)]
        self.assertEqual(names.count('choose_p1_disjoint_questions'), 1)
        self.assertEqual(names.count('choose_disjoint_questions'), 1)

    def test_selector_has_no_gpu_generation_or_test_split(self):
        tree = ast.parse(self.source)
        selector = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'choose_disjoint_questions')
        snippet = ast.get_source_segment(self.source, selector)
        self.assertIn('random.Random(42005)', snippet)
        self.assertIn('len(excluded) == 538', snippet)
        self.assertIn('len(remaining) == 6188', snippet)
        self.assertNotIn('torch.', snippet)
        self.assertNotIn('validation', snippet)
        self.assertNotIn('test.jsonl', snippet)

    def test_p2_disjoint_250_selection_and_determinism(self):
        # Exercise generated selector directly against *actual frozen P1 artifacts*.
        # A stub replaces only the inherited P1 selector. Historical E003/P1
        # selection and provenance checks are enforced by the P2 wrapper.
        meta = json.loads((Path(builder.P1_DIR) / 'metadata.json').read_text())
        old_pilot = meta['excluded_pilot_source_indices']
        old_scale = meta['excluded_scale_source_indices']
        old_p1 = meta['selected_source_indices']
        excluded = set(old_pilot) | set(old_scale) | set(old_p1)
        self.assertEqual(len(excluded), 538)
        remaining = [i for i in range(7473) if i not in excluded][:6188]
        self.assertEqual(len(remaining), 6188)
        training = [SimpleNamespace(source_index=i) for i in sorted(excluded | set(remaining))]
        self.assertEqual(len(training), 6726)
        selector_tree = ast.parse(self.source)
        selector_node = next(n for n in selector_tree.body if isinstance(n, ast.FunctionDef)
                             and n.name == 'choose_disjoint_questions')
        def require(ok, message):
            if not ok:
                raise AssertionError(message)
        bindings = {
            'Path': Path, 'json': json, 'random': random, 'require': require,
            'SELECTED_COUNT': 250, 'SAMPLES': 4,
            'ADAPTER_SHA': meta['reference_policy_adapter_sha256'],
            'EXPECTED_IMAGE_ID': meta['docker_image_id'],
            'sha256_file': lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest(),
            'choose_p1_disjoint_questions': lambda *args: (
                [SimpleNamespace(source_index=i) for i in old_p1], old_pilot, old_scale),
        }
        exec(compile(ast.Module(body=[selector_node], type_ignores=[]),
                     '<p2_selection_test>', 'exec'), bindings)
        fn = bindings['choose_disjoint_questions']
        selected, pilot, scale, p1 = fn(training, None, None, None, None, None, None, None)
        self.assertEqual(len(selected), 250)
        self.assertEqual(pilot, old_pilot)
        self.assertEqual(scale, old_scale)
        self.assertEqual(p1, old_p1)
        self.assertTrue(excluded.isdisjoint(r.source_index for r in selected))
        expected = sorted(random.Random(42005).sample(remaining, 250))
        self.assertEqual([r.source_index for r in selected], expected)
        self.assertEqual([r.source_index for r in fn(training, None, None, None, None, None, None, None)[0]], expected)

    def test_p1_source_pool_collision_rejected(self):
        # The selector must reject a P1/E003 collision even if the inherited
        # selector were changed to return a subtly overlapping source list.
        meta = json.loads((Path(builder.P1_DIR) / 'metadata.json').read_text())
        self.assertEqual(len(set(meta['selected_source_indices']) & set(meta['excluded_scale_source_indices'])), 0)
        self.assertEqual(len(set(meta['selected_source_indices']) & set(meta['excluded_pilot_source_indices'])), 0)


if __name__ == '__main__':
    unittest.main()
