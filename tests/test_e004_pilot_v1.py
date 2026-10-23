"""CPU-safe structural tests. No generation, evaluation, or training."""
import copy
import json
import random
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from scripts.generate_e004_pilot_v1 import (
    ADAPTER_SHA, NATIVE_EOS, PILOT_CONFIG_SHA, PILOT_REVISION,
    SELECTED_COUNT, SAMPLES, atomic_write, choose_disjoint_questions,
    output_summary, validate_config,
)

CONFIG = Path("configs/preference/e004_pilot_v1.json")
PILOT_CONFIG = Path("configs/preference/e003_pilot_v1.json")
SCALE_CONFIG = Path("configs/preference/e003_scale_v1.json")


def fixture():
    train = [SimpleNamespace(source_index=i, question=f"Test {i}", reference_answer=1)
             for i in range(6726)]
    original_pilot = sorted(random.Random(42).sample(range(6726), 32))
    remaining = [i for i in range(6726) if i not in set(original_pilot)]
    original_scale = sorted(random.Random(42003).sample(remaining, 256))
    pilot_config = json.loads(PILOT_CONFIG.read_text())
    scale_config = json.loads(SCALE_CONFIG.read_text())
    pilot_meta = {
        "run_type": "e003_preference_candidate_pilot", "code_revision": PILOT_REVISION,
        "config_sha256": PILOT_CONFIG_SHA, "config": pilot_config,
        "training_only": True, "reference_policy_adapter_sha256": ADAPTER_SHA,
        "selected_source_indices": original_pilot,
    }
    pilot_summary = {
        "candidates": 128, "pilot_questions": 32,
        "training_performed": False, "official_test_used": False,
        "code_revision": PILOT_REVISION,
    }
    from scripts.generate_e004_pilot_v1 import sha256_file, ORIGINAL_SCALE_CANDIDATES_SHA
    scale_meta = {
        "run_type": "e003_intermediate_candidate_generation", "version": "e003_scale_v1",
        "config": scale_config,
        "config_sha256": sha256_file(SCALE_CONFIG),
        "selected_source_indices": original_scale,
        "excluded_pilot_source_indices": original_pilot,
        "reference_policy_adapter_sha256": ADAPTER_SHA,
        "training_only": True, "training_performed": False, "official_test_used": False,
    }
    scale_summary = {
        "run_type": "e003_intermediate_candidate_generation", "candidates": 1024,
        "scale_questions": 256, "candidates_sha256": ORIGINAL_SCALE_CANDIDATES_SHA,
        "training_performed": False, "official_test_used": False,
    }
    rows = [dict(source_index=src, sample_index=s)
            for src in original_scale for s in range(4)]
    return (train, pilot_meta, pilot_summary, pilot_config,
            scale_meta, scale_summary, scale_config, rows)


class TestE004Pilot(unittest.TestCase):
    def test_exact_frozen_config(self):
        validate_config(json.loads(CONFIG.read_text()))

    def test_config_tampering_fails(self):
        original = json.loads(CONFIG.read_text())
        for keys, changed_value in (
            (("split",), "validation"),
            (("pilot_questions",), 251),
            (("selection_seed",), 42),
            (("samples_per_question",), 5),
            (("generation", "use_cache"), False),
            (("generation", "eos_token_id"), 151645),
            (("generation", "temperature"), 1.0),
        ):
            bad = copy.deepcopy(original)
            if len(keys) == 1: bad[keys[0]] = changed_value
            else: bad[keys[0]][keys[1]] = changed_value
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                validate_config(bad)

    def test_disjoint_250_and_reproducible(self):
        inputs = fixture()
        selected, old_pilot, old_scale = choose_disjoint_questions(*inputs)
        alt, alt_pilot, alt_scale = choose_disjoint_questions(list(reversed(inputs[0])), *inputs[1:])
        self.assertEqual([x.source_index for x in selected], [x.source_index for x in alt])
        self.assertEqual(old_pilot, alt_pilot)
        self.assertEqual(old_scale, alt_scale)
        self.assertEqual(len(selected), SELECTED_COUNT)
        self.assertEqual(len(set(old_pilot) | set(old_scale)), 288)
        self.assertFalse({x.source_index for x in selected} & (set(old_pilot) | set(old_scale)))

    def test_corrupted_prior_scale_metadata_rejected(self):
        f = list(fixture()); f[4] = copy.deepcopy(f[4]); f[4]["selected_source_indices"][0] = -7
        with self.assertRaises(ValueError): choose_disjoint_questions(*f)

    def test_corrupted_prior_candidate_group_rejected(self):
        f = list(fixture()); f[7] = f[7][:-1]
        with self.assertRaises(ValueError): choose_disjoint_questions(*f)

    def test_corrupted_pilot_index_rejected(self):
        f = list(fixture()); f[1] = copy.deepcopy(f[1]); f[1]["selected_source_indices"][0] = -7
        with self.assertRaises(ValueError): choose_disjoint_questions(*f)

    def test_atomic_write_never_overwrites(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "checkpoint.jsonl"
            atomic_write(path, "first\n")
            with self.assertRaises(FileExistsError): atomic_write(path, "second\n")
            self.assertEqual(path.read_text(), "first\n")

    def test_summary_is_generation_only(self):
        examples = [SimpleNamespace(source_index=i) for i in range(SELECTED_COUNT)]
        rows = []
        for i in range(SELECTED_COUNT):
            for j in range(SAMPLES):
                rows.append({
                    "source_index": i, "sample_index": j,
                    "native_eos_stop": True, "reached_token_cap": False,
                    "extraction_status": "valid", "eligible": True,
                    "correct": j == 0,
                    "generated_tokens": 42, "generation_seconds": 1.0,
                })
        result = output_summary(rows, examples, "0"*64, "0"*40, 100)
        self.assertEqual(result["run_type"], "e004_p1_candidate_generation")
        self.assertEqual(result["candidates"], 1000)
        self.assertEqual(result["pilot_questions"], 250)
        self.assertEqual(result["mixed_groups_with_potential_pair"], 250)
        self.assertFalse(result["training_performed"])
        self.assertFalse(result["official_test_used"])

if __name__ == "__main__":
    unittest.main()
