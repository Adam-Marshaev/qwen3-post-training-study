"""Create E004-P2 generator/config deterministically from pinned E004-P1 source.

Offline/stdlib-only. This script does not run inference, modify model weights or
train anything. Refuses to overwrite files with different bytes.
"""
import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

PARENT = "fde14abdf6791a0796799087f85154982e1628dd"
P1_GENERATOR_SHA = "87f5c398a65dd89dafe4830b564f57ed0c1e95924e81b5da3395b21e7a4f86d8"
P1_CONFIG_SHA = "3bf70dedbb024536d715b08d8ee5e28b8f07e2d3c07166fcd25d5272f458a1d6"
P1_CANDIDATES_SHA = "314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628"
P1_DIR = "data/preference_runs/e004_p1_250_k4_fc6d484_v1"
P1_SCRIPT = Path("scripts/generate_e004_pilot_v1.py")
P1_CONFIG = Path("configs/preference/e004_pilot_v1.json")
P2_SCRIPT = Path("scripts/generate_e004_p2_v1.py")
P2_CONFIG = Path("configs/preference/e004_p2_v1.json")


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def check_file(path, expected):
    assert path.is_file(), f"Missing input: {path}"
    actual = sha_bytes(path.read_bytes())
    assert actual == expected, f"Input checksum mismatch {path}: {actual}"


def once(source, old, new):
    n = source.count(old)
    assert n == 1, f"Expected exactly one source anchor, found {n}: {old[:120]!r}"
    return source.replace(old, new, 1)


# New selector is standalone, but delegates to the exact frozen P1 selector
# to independently rederive the original 250 sources from E003 provenance.
NEW_SELECTOR = '''def choose_disjoint_questions(training, pilot_meta, pilot_summary, pilot_config,
                              scale_meta, scale_summary, scale_config, old_rows):
    """Independently rederive all 538 excluded TRAIN indices before P2 selection."""
    p1_selected, old_pilot, old_scale = choose_p1_disjoint_questions(
        training, pilot_meta, pilot_summary, pilot_config,
        scale_meta, scale_summary, scale_config, old_rows)
    p1_dir = Path("data/preference_runs/e004_p1_250_k4_fc6d484_v1")
    p1_meta = json.loads((p1_dir / "metadata.json").read_text(encoding="utf-8"))
    p1_summary = json.loads((p1_dir / "summary.json").read_text(encoding="utf-8"))
    p1_cfg_path = Path("configs/preference/e004_pilot_v1.json")
    require(sha256_file(p1_cfg_path) ==
            "3bf70dedbb024536d715b08d8ee5e28b8f07e2d3c07166fcd25d5272f458a1d6",
            "E004-P1 config checksum mismatch")
    p1_config = json.loads(p1_cfg_path.read_text(encoding="utf-8"))
    require(sha256_file(p1_dir / "candidates.jsonl") ==
            "314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628",
            "E004-P1 candidates checksum mismatch")
    p1_indices = [r.source_index for r in p1_selected]
    require(len(p1_indices) == SELECTED_COUNT and len(set(p1_indices)) == SELECTED_COUNT,
            "E004-P1 rederived selection invalid")
    require(p1_meta.get("run_type") == "e004_p1_candidate_generation" and
            p1_meta.get("version") == "e004_pilot_v1" and
            p1_meta.get("code_revision") == "fc6d48475f018c1a26d98d81694c8b6fbc31b815" and
            p1_meta.get("docker_image_id") == EXPECTED_IMAGE_ID and
            p1_meta.get("config_sha256") ==
            "3bf70dedbb024536d715b08d8ee5e28b8f07e2d3c07166fcd25d5272f458a1d6" and
            p1_meta.get("config") == p1_config and
            p1_meta.get("selected_source_indices") == p1_indices and
            p1_meta.get("excluded_pilot_source_indices") == old_pilot and
            p1_meta.get("excluded_scale_source_indices") == old_scale and
            p1_meta.get("reference_policy_adapter_sha256") == ADAPTER_SHA and
            p1_meta.get("training_only") is True and
            p1_meta.get("training_performed") is False and
            p1_meta.get("official_test_used") is False,
            "E004-P1 metadata/selection provenance mismatch")
    require(p1_summary.get("run_type") == "e004_p1_candidate_generation" and
            p1_summary.get("code_revision") == "fc6d48475f018c1a26d98d81694c8b6fbc31b815" and
            p1_summary.get("config_sha256") ==
            "3bf70dedbb024536d715b08d8ee5e28b8f07e2d3c07166fcd25d5272f458a1d6" and
            p1_summary.get("pilot_questions") == SELECTED_COUNT and
            p1_summary.get("candidates") == SELECTED_COUNT * SAMPLES and
            p1_summary.get("candidates_sha256") ==
            "314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628" and
            p1_summary.get("reference_policy_adapter_sha256") == ADAPTER_SHA and
            p1_summary.get("training_performed") is False and
            p1_summary.get("official_test_used") is False,
            "E004-P1 summary provenance mismatch")
    excluded = set(old_pilot) | set(old_scale) | set(p1_indices)
    require(len(old_pilot) == 32 and len(old_scale) == 256 and
            len(p1_indices) == 250 and len(excluded) == 538,
            "Previously sampled TRAIN questions must be unique (538)")
    ordered = sorted(training, key=lambda r: r.source_index)
    require(len(ordered) == 6726 and len({r.source_index for r in ordered}) == 6726,
            "Frozen training partition differs")
    remaining = [r for r in ordered if r.source_index not in excluded]
    require(len(remaining) == 6188, "Unexpected remaining TRAIN source count")
    selected = sorted(random.Random(42005).sample(remaining, SELECTED_COUNT),
                      key=lambda r: r.source_index)
    require(len(selected) == 250 and
            excluded.isdisjoint(r.source_index for r in selected),
            "P2 source selection overlaps previously sampled questions")
    return selected, old_pilot, old_scale, p1_indices


'''


def patch_source(source):
    # All replacements must succeed *exactly once*; leave the decoding and
    # checkpointing functions untouched as verified with AST below.
    source = once(source, 'SCALE_VERSION = "e004_pilot_v1"',
                  'SCALE_VERSION = "e004_p2_v1"')
    source = once(source, '"purpose": "e004_p1_candidate_generation_only",',
                  '"purpose": "e004_p2_candidate_generation_only",')
    source = once(source, '"selection_seed": 42004,',
                  '"selection_seed": 42005,')
    source = once(source,
                  '"excluded_scale_dir": "data/preference_runs/e003_scale256_k4_v1",',
                  '"excluded_scale_dir": "data/preference_runs/e003_scale256_k4_v1",\n'
                  '        "excluded_p1_dir": "data/preference_runs/e004_p1_250_k4_fc6d484_v1",')
    source = once(source, 'def choose_disjoint_questions(',
                  'def choose_p1_disjoint_questions(')
    source = once(source, 'def main():', NEW_SELECTOR + 'def main():')
    source = once(source,
                  'selected, excluded_pilot, excluded_scale = choose_disjoint_questions(',
                  'selected, excluded_pilot, excluded_scale, excluded_p1 = choose_disjoint_questions(')
    source = once(source,
                  'print(f"Excluded original scale questions: {len(excluded_scale)}")',
                  'print(f"Excluded original scale questions: {len(excluded_scale)}")\n'
                  '        print(f"Excluded E004-P1 questions: {len(excluded_p1)}")\n'
                  '        print("Previously sampled source questions: 538")\n'
                  '        print(f"P2 selection SHA256: {hashlib.sha256(json.dumps([r.source_index for r in selected], separators=(\',\', \':\')).encode()).hexdigest()}")')
    source = once(source,
                  '"excluded_scale_source_indices": excluded_scale,',
                  '"excluded_scale_source_indices": excluded_scale,\n'
                  '        "excluded_p1_source_indices": excluded_p1,\n'
                  '        "p1_metadata_sha256": sha256_file(Path("data/preference_runs/e004_p1_250_k4_fc6d484_v1/metadata.json")),\n'
                  '        "p1_summary_sha256": sha256_file(Path("data/preference_runs/e004_p1_250_k4_fc6d484_v1/summary.json")),\n'
                  '        "p1_candidates_sha256": "314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628",')
    source = once(source, 'import fcntl\n', 'import fcntl\nimport hashlib\n')
    # Attribution strings only, not model/generation/checkpoint logic.
    source = source.replace('e004_p1_candidate_generation', 'e004_p2_candidate_generation')
    source = source.replace('E004-P1', 'E004-P2')
    source = source.replace('E004 P1', 'E004 P2')
    # Keep explicit references to the historical P1 run in the new selector.
    # Global display-name changes above must not re-label historical metadata.
    source = source.replace('p1_meta.get("run_type") == "e004_p2_candidate_generation"',
                            'p1_meta.get("run_type") == "e004_p1_candidate_generation"')
    source = source.replace('p1_summary.get("run_type") == "e004_p2_candidate_generation"',
                            'p1_summary.get("run_type") == "e004_p1_candidate_generation"')
    # Restore historical P1 labels in the inserted wrapper (not the P2 run labels).
    for suffix in (
        'config checksum mismatch', 'candidates checksum mismatch',
        'rederived selection invalid', 'metadata/selection provenance mismatch',
        'summary provenance mismatch',
    ):
        source = source.replace(f'E004-P2 {suffix}', f'E004-P1 {suffix}')
    source = source.replace('Excluded E004-P2 questions:', 'Excluded E004-P1 questions:')
    # Verify all historical source-artifact lookup strings remain unmodified.
    assert 'p1_meta.get("run_type") == "e004_p1_candidate_generation"' in source
    assert '"run_type": "e004_p2_candidate_generation"' in source
    tree = ast.parse(source)
    names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert names.count('choose_p1_disjoint_questions') == 1
    assert names.count('choose_disjoint_questions') == 1
    return source


def verify_inherited_functions(original, fork):
    old = ast.parse(original)
    new = ast.parse(fork)
    names = ('atomic_write', 'canonical_json', 'verify_training', 'validate_record',
             'validate_group', 'generate_group', 'read_group')
    a = {n.name: n for n in old.body if isinstance(n, ast.FunctionDef)}
    b = {n.name: n for n in new.body if isinstance(n, ast.FunctionDef)}
    for name in names:
        assert name in a and name in b, f"Inherited function missing: {name}"
        assert ast.dump(a[name], include_attributes=False) == ast.dump(b[name], include_attributes=False), (
            f"Frozen generation/checkpoint code changed: {name}"
        )


def config_from_p1(data):
    c = json.loads(data)
    assert c.get('config_version') == 'e004_pilot_v1'
    assert c.get('purpose') == 'e004_p1_candidate_generation_only'
    assert c.get('selection_seed') == 42004
    assert c.get('pilot_questions') == 250 and c.get('samples_per_question') == 4
    assert c.get('excluded_scale_dir') == 'data/preference_runs/e003_scale256_k4_v1'
    c['config_version'] = 'e004_p2_v1'
    c['purpose'] = 'e004_p2_candidate_generation_only'
    c['selection_seed'] = 42005
    c['excluded_p1_dir'] = P1_DIR
    return json.dumps(c, sort_keys=True, indent=2, ensure_ascii=False) + '\n'


def generated_contents():
    check_file(P1_SCRIPT, P1_GENERATOR_SHA)
    check_file(P1_CONFIG, P1_CONFIG_SHA)
    check_file(Path(P1_DIR) / 'candidates.jsonl', P1_CANDIDATES_SHA)
    original = P1_SCRIPT.read_text(encoding='utf-8')
    fork = patch_source(original)
    verify_inherited_functions(original, fork)
    config = config_from_p1(P1_CONFIG.read_text(encoding='utf-8'))
    assert '"excluded_p1_dir": "data/preference_runs/e004_p1_250_k4_fc6d484_v1"' in fork
    return {P2_SCRIPT: fork.encode('utf-8'), P2_CONFIG: config.encode('utf-8')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true',
                        help='Create generated P2 files, refusing differences or overwrites')
    args = parser.parse_args()
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert actual == PARENT, f"Unexpected parent revision: {actual}"
    if args.install:
        status_lines = set(subprocess.check_output(
            ['git', 'status', '--porcelain'], text=True).splitlines())
        allowed = {
            '?? scripts/build_e004_p2_fork_v1.py',
            '?? tests/test_e004_p2_fork_v1.py',
            '?? docs/e004_p2_generation_protocol_v1.md',
            '?? scripts/generate_e004_p2_v1.py',
            '?? configs/preference/e004_p2_v1.json',
        }
        assert status_lines <= allowed, f'Unexpected repository changes: {status_lines - allowed}'
    files = generated_contents()
    for path, content in files.items():
        print(f'{path}: SHA256 {sha_bytes(content)} ({len(content)} bytes)')
        if path.exists():
            assert path.is_file() and path.read_bytes() == content, f"Refusing changed file: {path}"
            print('  Already matches')
        elif args.install:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as fp:
                fp.write(content)
            print('  INSTALLED')
        else:
            print('  Dry-run only')
    print('P2 BUILDER:', 'INSTALLED/VERIFIED' if args.install else 'DRY-RUN VERIFIED')
    print('GPU inference: NO; training: NO')


if __name__ == '__main__':
    main()
