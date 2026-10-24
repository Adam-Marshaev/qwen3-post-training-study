"""Deterministically derive E004-P3 (1200 questions) from frozen E004-P2.

Offline/stdlib only; preserves generation, evaluation, checkpoint, and resume
functions unchanged. Refuses to overwrite any differing file. No GPU/training.
"""
import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

PARENT = '331499df3175737bb9464a3d9a53a365fc494431'
P2_GENERATOR_SHA = '5069415d1068f5099db7b4da068d82fcdc2f77e2615e3972db565e9a89b55556'
P2_CONFIG_SHA = '1ba4f7bc96971aab5004eb78ff8ce30e7183389ff45c21d641068f719c8eb8a5'
P2_CANDIDATES_SHA = '568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79'
P2_METADATA_SHA = 'cefdb0f7f9cd9c32a49b6ecdfebea3097e2a093d5a0c3e69f8fda704e943851f'
P2_SUMMARY_SHA = 'fd240de075f87f10c5f756bc733a4cc59741fdd76795a66150fbd27ce19457b7'
P3_SELECTION_SHA = 'bfeb83304623bfdb2c8c952cba46d48ac36e251414b79d4763fb24f21b6ffed9'
P2_DIR = 'data/preference_runs/e004_p2_250_k4_f543aa4_v1'
P2_SCRIPT = Path('scripts/generate_e004_p2_v1.py')
P2_CONFIG = Path('configs/preference/e004_p2_v1.json')
P3_SCRIPT = Path('scripts/generate_e004_p3_v1.py')
P3_CONFIG = Path('configs/preference/e004_p3_v1.json')


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def check_file(path, expected):
    assert path.is_file(), f'Missing source file: {path}'
    actual = sha_bytes(path.read_bytes())
    assert actual == expected, f'Checksum mismatch {path}: {actual}'


def once(source, old, new):
    count = source.count(old)
    assert count == 1, f'Expected exactly one anchor ({count} found): {old[:140]!r}'
    return source.replace(old, new, 1)


def replace_function(source, name, new):
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(nodes) == 1, f'Missing or duplicated function: {name}'
    old = ast.get_source_segment(source, nodes[0])
    assert old and source.count(old) == 1
    return source.replace(old, new, 1)


NEW_P3_SELECTOR = '''def choose_disjoint_questions(training, pilot_meta, pilot_summary, pilot_config,
                              scale_meta, scale_summary, scale_config, old_rows):
    """Reconstruct P1/P2 provenance, then exclude all 788 used TRAIN indices."""
    p2_selected, old_pilot, old_scale, p1_indices = choose_p2_disjoint_questions(
        training, pilot_meta, pilot_summary, pilot_config,
        scale_meta, scale_summary, scale_config, old_rows)
    p2_dir = Path("data/preference_runs/e004_p2_250_k4_f543aa4_v1")
    p2_cfg_path = Path("configs/preference/e004_p2_v1.json")
    require(sha256_file(Path("scripts/generate_e004_p2_v1.py")) ==
            "5069415d1068f5099db7b4da068d82fcdc2f77e2615e3972db565e9a89b55556",
            "Frozen P2 generator checksum mismatch")
    require(sha256_file(p2_cfg_path) ==
            "1ba4f7bc96971aab5004eb78ff8ce30e7183389ff45c21d641068f719c8eb8a5",
            "Frozen P2 config checksum mismatch")
    require(sha256_file(p2_dir / "metadata.json") ==
            "cefdb0f7f9cd9c32a49b6ecdfebea3097e2a093d5a0c3e69f8fda704e943851f",
            "Frozen P2 metadata checksum mismatch")
    require(sha256_file(p2_dir / "summary.json") ==
            "fd240de075f87f10c5f756bc733a4cc59741fdd76795a66150fbd27ce19457b7",
            "Frozen P2 summary checksum mismatch")
    require(sha256_file(p2_dir / "candidates.jsonl") ==
            "568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79",
            "Frozen P2 candidates checksum mismatch")
    p2_meta = json.loads((p2_dir / "metadata.json").read_text(encoding="utf-8"))
    p2_summary = json.loads((p2_dir / "summary.json").read_text(encoding="utf-8"))
    p2_cfg = json.loads(p2_cfg_path.read_text(encoding="utf-8"))
    p2_indices = [r.source_index for r in p2_selected]
    require(len(p2_indices) == 250 and len(set(p2_indices)) == 250,
            "Recomputed P2 selection not 250 unique indices")
    require(p2_meta.get("run_type") == "e004_p2_candidate_generation" and
            p2_meta.get("version") == "e004_p2_v1" and
            p2_meta.get("code_revision") == "f543aa41ff917d96b8f26b38df9c6c00f91b1619" and
            p2_meta.get("docker_image_id") == EXPECTED_IMAGE_ID and
            p2_meta.get("config_sha256") ==
            "1ba4f7bc96971aab5004eb78ff8ce30e7183389ff45c21d641068f719c8eb8a5" and
            p2_meta.get("config") == p2_cfg and
            p2_meta.get("selected_source_indices") == p2_indices and
            p2_meta.get("excluded_pilot_source_indices") == old_pilot and
            p2_meta.get("excluded_scale_source_indices") == old_scale and
            p2_meta.get("excluded_p1_source_indices") == p1_indices and
            p2_meta.get("reference_policy_adapter_sha256") == ADAPTER_SHA and
            p2_meta.get("training_only") is True and
            p2_meta.get("training_performed") is False and
            p2_meta.get("official_test_used") is False,
            "Frozen P2 provenance/selection mismatch")
    require(p2_summary.get("run_type") == "e004_p2_candidate_generation" and
            p2_summary.get("code_revision") == "f543aa41ff917d96b8f26b38df9c6c00f91b1619" and
            p2_summary.get("config_sha256") ==
            "1ba4f7bc96971aab5004eb78ff8ce30e7183389ff45c21d641068f719c8eb8a5" and
            p2_summary.get("pilot_questions") == 250 and
            p2_summary.get("candidates") == 1000 and
            p2_summary.get("candidates_sha256") ==
            "568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79" and
            p2_summary.get("reference_policy_adapter_sha256") == ADAPTER_SHA and
            p2_summary.get("training_performed") is False and
            p2_summary.get("official_test_used") is False,
            "Frozen P2 summary provenance mismatch")
    excluded = set(old_pilot) | set(old_scale) | set(p1_indices) | set(p2_indices)
    require(len(old_pilot) == 32 and len(old_scale) == 256 and
            len(p1_indices) == 250 and len(p2_indices) == 250 and
            len(excluded) == 788, "Previously sampled source pools overlap")
    ordered = sorted(training, key=lambda r: r.source_index)
    require(len(ordered) == 6726 and len({r.source_index for r in ordered}) == 6726,
            "Unexpected frozen training partition")
    require(excluded.issubset(r.source_index for r in ordered),
            "Previously sampled questions missing from TRAIN split")
    remaining = [r for r in ordered if r.source_index not in excluded]
    require(len(remaining) == 5938, "Unexpected number of unused TRAIN questions")
    selected = sorted(random.Random(42006).sample(remaining, SELECTED_COUNT),
                      key=lambda r: r.source_index)
    indices = [r.source_index for r in selected]
    require(len(indices) == SELECTED_COUNT == 1200 and
            len(set(indices)) == 1200 and set(indices).isdisjoint(excluded),
            "P3 selection overlaps a frozen previous pool")
    selection_sha = hashlib.sha256(json.dumps(indices, separators=(",", ":")).encode()).hexdigest()
    require(selection_sha ==
            "bfeb83304623bfdb2c8c952cba46d48ac36e251414b79d4763fb24f21b6ffed9",
            "P3 selection differs from signed read-only preflight")
    return selected, old_pilot, old_scale, p1_indices, p2_indices


'''


def patch_source(source):
    # Capture the historical selectors BEFORE changing the global group count.
    tree = ast.parse(source)
    functions = {n.name: ast.get_source_segment(source, n)
                 for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert 'choose_p1_disjoint_questions' in functions
    assert 'choose_disjoint_questions' in functions
    # Pin P1 and P2 to their original 250-question count, even though the
    # global SELECTED_COUNT becomes 1200 for P3 generation and final audits.
    p1 = functions['choose_p1_disjoint_questions']
    p2 = functions['choose_disjoint_questions']
    assert p1.count('SELECTED_COUNT') >= 2
    assert p2.count('SELECTED_COUNT') >= 3
    source = replace_function(source, 'choose_p1_disjoint_questions',
                              p1.replace('SELECTED_COUNT', '250'))
    source = replace_function(source, 'choose_disjoint_questions',
                              p2.replace('SELECTED_COUNT', '250').replace(
                                  'def choose_disjoint_questions(',
                                  'def choose_p2_disjoint_questions(', 1))
    source = once(source, 'SCALE_VERSION = "e004_p2_v1"',
                  'SCALE_VERSION = "e004_p3_v1"')
    source = once(source, 'SELECTED_COUNT = 250', 'SELECTED_COUNT = 1200')
    source = once(source, '"purpose": "e004_p2_candidate_generation_only",',
                  '"purpose": "e004_p3_candidate_generation_only",')
    source = once(source, '"selection_seed": 42005,',
                  '"selection_seed": 42006,')
    source = once(source,
                  '"excluded_p1_dir": "data/preference_runs/e004_p1_250_k4_fc6d484_v1",',
                  '"excluded_p1_dir": "data/preference_runs/e004_p1_250_k4_fc6d484_v1",\n'
                  '        "excluded_p2_dir": "data/preference_runs/e004_p2_250_k4_f543aa4_v1",')
    source = once(source, 'def main():', NEW_P3_SELECTOR + 'def main():')
    source = once(source,
                  'selected, excluded_pilot, excluded_scale, excluded_p1 = choose_disjoint_questions(',
                  'selected, excluded_pilot, excluded_scale, excluded_p1, excluded_p2 = choose_disjoint_questions(')
    source = once(source,
                  'print(f"Excluded E004-P1 questions: {len(excluded_p1)}")',
                  'print(f"Excluded E004-P1 questions: {len(excluded_p1)}")\n'
                  '        print(f"Excluded E004-P2 questions: {len(excluded_p2)}")')
    source = once(source, 'print("Previously sampled source questions: 538")',
                  'print("Previously sampled source questions: 788")')
    source = once(source, 'print(f"P2 selection SHA256:',
                  'print(f"P3 selection SHA256:')
    source = once(source, '"excluded_p1_source_indices": excluded_p1,',
                  '"excluded_p1_source_indices": excluded_p1,\n'
                  '        "excluded_p2_source_indices": excluded_p2,\n'
                  '        "p2_metadata_sha256": sha256_file(Path("data/preference_runs/e004_p2_250_k4_f543aa4_v1/metadata.json")),\n'
                  '        "p2_summary_sha256": sha256_file(Path("data/preference_runs/e004_p2_250_k4_f543aa4_v1/summary.json")),\n'
                  '        "p2_candidates_sha256": "568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79",')
    assert source.count('"run_type": "e004_p2_candidate_generation",') == 2
    source = source.replace('"run_type": "e004_p2_candidate_generation",',
                            '"run_type": "e004_p3_candidate_generation",')
    source = once(source, '=== E004-P2 PREFLIGHT PASSED ===',
                  '=== E004-P3 PREFLIGHT PASSED ===')
    source = once(source, '=== E004-P2 GENERATION COMPLETE ===',
                  '=== E004-P3 GENERATION COMPLETE ===')
    source = once(source, 'E004-P2 config must exactly match',
                  'E004-P3 config must exactly match')
    source = source.replace('"""E004 P2 250-question disjoint, resumable generation pilot.',
                            '"""E004 P3 1200-question disjoint, resumable generation scale.')
    # Invariants: the two old selectors are independent of P3's larger count.
    parsed = ast.parse(source)
    funcs = [n.name for n in parsed.body if isinstance(n, ast.FunctionDef)]
    for name in ('choose_p1_disjoint_questions', 'choose_p2_disjoint_questions',
                 'choose_disjoint_questions'):
        assert funcs.count(name) == 1, name
    return source


def verify_inherited_functions(original, fork):
    old = {n.name: n for n in ast.parse(original).body if isinstance(n, ast.FunctionDef)}
    new = {n.name: n for n in ast.parse(fork).body if isinstance(n, ast.FunctionDef)}
    for name in ('atomic_write', 'canonical_json', 'verify_training', 'validate_record',
                 'validate_group', 'generate_group', 'read_group'):
        assert name in old and name in new, name
        assert ast.dump(old[name], include_attributes=False) == ast.dump(
            new[name], include_attributes=False), f'Inherited code changed: {name}'
    # Output summary should only change its P2->P3 run_type label.
    old_output = ast.get_source_segment(original, old['output_summary'])
    new_output = ast.get_source_segment(fork, new['output_summary'])
    assert old_output.replace('e004_p2_candidate_generation',
                              'e004_p3_candidate_generation') == new_output, (
        'Output summary changed beyond P3 provenance label')
    # Main changes only in disjointness/output labels/provenance, NOT decoding.
    before = ast.get_source_segment(original, old['main'])
    after = ast.get_source_segment(fork, new['main'])
    for anchor in ('generate_group(model, tokenizer, example)',
                   'atomic_write(checkpoint,', 'read_group(p, selected_map[idx], tokenizer)',
                   'torch.cuda.is_available()', 'PeftModel.from_pretrained(',
                   'torch.cuda.max_memory_allocated()', 'fcntl.flock('):
        assert anchor in before and anchor in after, anchor


def config_from_p2(data):
    c = json.loads(data)
    assert c.get('config_version') == 'e004_p2_v1'
    assert c.get('purpose') == 'e004_p2_candidate_generation_only'
    assert c.get('selection_seed') == 42005
    assert c.get('pilot_questions') == 250 and c.get('samples_per_question') == 4
    assert c.get('excluded_p1_dir') == 'data/preference_runs/e004_p1_250_k4_fc6d484_v1'
    c['config_version'] = 'e004_p3_v1'
    c['purpose'] = 'e004_p3_candidate_generation_only'
    c['selection_seed'] = 42006
    c['pilot_questions'] = 1200
    c['excluded_p2_dir'] = P2_DIR
    return json.dumps(c, sort_keys=True, indent=2, ensure_ascii=False) + '\n'


def generated_contents():
    check_file(P2_SCRIPT, P2_GENERATOR_SHA)
    check_file(P2_CONFIG, P2_CONFIG_SHA)
    check_file(Path(P2_DIR) / 'candidates.jsonl', P2_CANDIDATES_SHA)
    check_file(Path(P2_DIR) / 'metadata.json', P2_METADATA_SHA)
    check_file(Path(P2_DIR) / 'summary.json', P2_SUMMARY_SHA)
    original = P2_SCRIPT.read_text(encoding='utf-8')
    fork = patch_source(original)
    verify_inherited_functions(original, fork)
    config = config_from_p2(P2_CONFIG.read_text(encoding='utf-8'))
    assert '"excluded_p2_dir": "data/preference_runs/e004_p2_250_k4_f543aa4_v1"' in fork
    return {P3_SCRIPT: fork.encode('utf-8'), P3_CONFIG: config.encode('utf-8')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true',
                        help='Create P3 files without overwriting different bytes')
    args = parser.parse_args()
    rev = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert rev == PARENT, f'Unexpected Git revision: {rev}'
    if args.install:
        status = set(subprocess.check_output(
            ['git', 'status', '--porcelain'], text=True).splitlines())
        allowed = {
            '?? scripts/build_e004_p3_fork_v1.py',
            '?? tests/test_e004_p3_fork_v1.py',
            '?? docs/e004_p3_generation_protocol_v1.md',
            '?? scripts/generate_e004_p3_v1.py',
            '?? configs/preference/e004_p3_v1.json',
        }
        assert status <= allowed, f'Unexpected repository changes: {status - allowed}'
    for path, contents in generated_contents().items():
        print(f'{path}: SHA256 {sha_bytes(contents)} ({len(contents)} bytes)')
        if path.exists():
            assert path.is_file() and path.read_bytes() == contents, (
                f'Refusing to overwrite different file: {path}')
            print('  ALREADY VERIFIED')
        elif args.install:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as fp:
                fp.write(contents)
            print('  INSTALLED')
        else:
            print('  Dry run only')
    print('E004-P3 BUILDER:', 'INSTALLED/VERIFIED' if args.install else 'DRY RUN VERIFIED')
    print('GPU inference: NO; training: NO')


if __name__ == '__main__':
    main()
