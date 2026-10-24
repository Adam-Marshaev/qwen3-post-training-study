#!/usr/bin/env python3
"""Conservative, deterministic *advisory* E004-P2 arithmetic/pair pre-screen.

No language-model verification, no semantic approval, no training. Original
artifacts are read-only. Report is intentionally not a DPO training dataset.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

EXPECTED_COMPACT_SHA256 = "fe4c4f034417b73be7862975889e102882be6d9f67352d62b9a568eaeb66faf9"
EXPECTED_ORIGINAL_SHA256 = "568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79"
FINAL_PATTERN = re.compile(r"(?i)\bthe answer is\s*\$?(-?\d[\d,]*(?:\.\d+)?(?:/\d+)?)\s*\.?\s*$")
EXPR_CHARS = set("0123456789.,$%+-*/()×÷xX ")
MAX_ABS = 10**20


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def literal_value(node: ast.AST) -> Fraction:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return Fraction(str(node.value))
    if isinstance(node, ast.UnaryOp):
        value = literal_value(node.operand)
        if isinstance(node.op, ast.USub):
            return -value
        if isinstance(node.op, ast.UAdd):
            return value
    if isinstance(node, ast.BinOp):
        x, y = literal_value(node.left), literal_value(node.right)
        if isinstance(node.op, ast.Add):
            z = x + y
        elif isinstance(node.op, ast.Sub):
            z = x - y
        elif isinstance(node.op, ast.Mult):
            z = x * y
        elif isinstance(node.op, ast.Div):
            require(y != 0, "Division by zero")
            z = x / y
        else:
            raise ValueError("Disallowed math operator")
        require(abs(z) <= MAX_ABS, "Magnitude too large")
        return z
    raise ValueError("Non-arithmetic expression")


def evaluate(expr: str) -> Fraction:
    expr = expr.strip().rstrip(".").strip().replace("$", "")
    expr = expr.replace("×", "*").replace("÷", "/")
    expr = re.sub(r"(?<=\d),(?=\d{3}(?:\D|$))", "", expr)
    expr = re.sub(r"(?<=\d)\s*[xX]\s*(?=\d|\()", "*", expr)
    expr = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", expr)
    require(len(expr) <= 200, "Expression too long")
    require(re.fullmatch(r"[\d\s.()+\-*/]+", expr) is not None,
            "Unsupported arithmetic token")
    return literal_value(ast.parse(expr, mode="eval").body)


def arithmetic_suffix(s: str) -> str:
    i = len(s)
    while i > 0 and s[i-1] in EXPR_CHARS:
        i -= 1
    return s[i:].strip()


def arithmetic_prefix(s: str) -> str:
    i = 0
    while i < len(s) and s[i] in EXPR_CHARS:
        i += 1
    return s[:i].strip()


def equation_results(response: str) -> dict:
    checked, bad, unknown, examples = 0, 0, 0, []
    for line_number, line in enumerate(response.splitlines(), 1):
        if "=" not in line:
            continue
        parts = line.split("=")
        for n in range(len(parts)-1):
            left = arithmetic_suffix(parts[n])
            right = arithmetic_prefix(parts[n+1])
            # Extended surrounding prose is not arithmetic evidence; reject
            # unverifiable explicit equalities rather than silently skip them.
            if not left or not right:
                unknown += 1
                examples.append({"line":line_number,"status":"unknown", "text":line[:230]})
                continue
            try:
                lv, rv = evaluate(left), evaluate(right)
            except (ValueError, ZeroDivisionError, SyntaxError, OverflowError, RecursionError):
                unknown += 1
                examples.append({"line":line_number,"status":"unknown", "left":left[:100],"right":right[:100]})
                continue
            checked += 1
            if lv != rv:
                bad += 1
                examples.append({"line":line_number,"status":"arithmetic_false", "left":left[:100],"right":right[:100]})
    return {"checked":checked, "incorrect":bad, "unknown":unknown,
            "issues":examples[:12]}


def numeric_answer(raw: object) -> Fraction:
    s = str(raw).strip().replace("$", "").replace(",", "")
    require(re.fullmatch(r"-?\d+(?:\.\d+)?(?:/\d+)?",s) is not None,
            "Non-numeric answer")
    return evaluate(s)


def screen_response(row: dict, expected_answer: object) -> dict:
    reasons = []
    if not (row.get("eligible") is True and row.get("correct") is True and
            row.get("native_eos_stop") is True and row.get("reached_token_cap") is False
            and row.get("unwanted_continuation") is False and row.get("extraction_status") == "valid"):
        reasons.append("ineligible_or_not_correct")
    response = row.get("response", "")
    m = FINAL_PATTERN.search(response.strip())
    if not m:
        reasons.append("no_unambiguous_terminal_answer")
    else:
        try:
            if numeric_answer(m.group(1)) != numeric_answer(expected_answer):
                reasons.append("final_answer_mismatch")
        except (ValueError, ZeroDivisionError, SyntaxError):
            reasons.append("unparseable_reference_or_final_answer")
    eq = equation_results(response)
    if eq["checked"] < 2:
        reasons.append("fewer_than_two_verified_equations")
    if eq["incorrect"]:
        reasons.append("explicit_arithmetic_contradiction")
    if eq["unknown"]:
        reasons.append("unverifiable_explicit_equality")
    if len(response.strip()) < 35:
        reasons.append("too_little_reasoning")
    if len(response) > 4000:
        reasons.append("unusually_long_response")
    if re.search(r"\b(approximately|roughly|maybe|guess|probably)\b",response,re.I):
        reasons.append("hedged_reasoning")
    return {"passed_mechanical":not reasons,"reasons": sorted(set(reasons)),"equations":eq}


def screen_rejected(row: dict) -> dict:
    reasons = []
    if not (row.get("eligible") is True and row.get("correct") is False and
            row.get("native_eos_stop") is True and row.get("reached_token_cap") is False
            and row.get("unwanted_continuation") is False and row.get("extraction_status") == "valid"):
        reasons.append("not_eligible_rejected")
    eq = equation_results(row.get("response", ""))
    if eq["checked"] < 1:
        reasons.append("no_verified_arithmetic_in_rejection")
    if not FINAL_PATTERN.search(row.get("response", "").strip()):
        reasons.append("rejected_answer_missing")
    if len(row.get("response", "").strip()) < 35:
        reasons.append("too_little_reasoning_in_rejection")
    return {"passed_mechanical":not reasons,"reasons":sorted(set(reasons)),"equations":eq}


def screen(groups: list[dict]) -> tuple[list[dict],dict]:
    decisions = []
    reason_counts = Counter()
    all_chosen = all_rejected = 0
    compatible = 0
    seen = set()
    for g in groups:
        source = g["source_index"]
        require(isinstance(source,int) and source not in seen,"Duplicate/nonint source index")
        seen.add(source)
        rows = sorted(g["responses"],key=lambda r:r["sample_index"])
        require(len(rows)==4 and [r["sample_index"] for r in rows]==[0,1,2,3],
                "Expected four distinct samples per group")
        correct = [r for r in rows if r["eligible"] is True and r["correct"] is True]
        wrong = [r for r in rows if r["eligible"] is True and r["correct"] is False]
        require(bool(correct and wrong),"Group not mixed")
        require(len(correct)==g["eligible_correct_count"] and len(wrong)==g["eligible_incorrect_count"],"Eligibility count mismatch")
        expected_min_gap = min(abs(c["generated_tokens"]-w["generated_tokens"]) for c in correct for w in wrong)
        require(expected_min_gap==g["minimum_pair_token_gap"],"Length gap mismatch")
        all_chosen+=len(correct); all_rejected+=len(wrong)
        compatible+=(expected_min_gap<=40)
        chosen_decisions = {r["sample_index"]:screen_response(r,g["reference_answer"]) for r in correct}
        wrong_decisions = {r["sample_index"]:screen_rejected(r) for r in wrong}
        pairs=[]
        for c in correct:
            cd=chosen_decisions[c["sample_index"]]
            if not cd["passed_mechanical"]:continue
            for w in wrong:
                wd=wrong_decisions[w["sample_index"]]
                gap=abs(c["generated_tokens"]-w["generated_tokens"])
                if (wd["passed_mechanical"] and gap<=40 and c["response"].strip()!=w["response"].strip()):
                    pairs.append({"chosen_sample_index":c["sample_index"],
                                  "rejected_sample_index":w["sample_index"],
                                  "gap":gap,
                                  "chosen_checked_equations":cd["equations"]["checked"],
                                  "rejected_checked_equations":wd["equations"]["checked"],
                                  "rejected_arithmetic_errors":wd["equations"]["incorrect"]})
        pairs.sort(key=lambda p:(p["gap"],-p["chosen_checked_equations"],-p["rejected_checked_equations"],p["chosen_sample_index"],p["rejected_sample_index"]))
        for cd in chosen_decisions.values(): reason_counts.update(cd["reasons"])
        for wd in wrong_decisions.values():reason_counts.update(wd["reasons"])
        decision={"source_index":source,"minimum_pair_token_gap":expected_min_gap,
                  "mechanically_eligible_pair_count":len(pairs),"top_pair":pairs[0] if pairs else None,
                  "chosen_checks":chosen_decisions,"rejected_checks":wrong_decisions,
                  "semantic_verification":"NOT_PERFORMED",
                  "decision":"MECHANICAL_PASS_SEMANTIC_HOLD" if pairs else "REJECT_BY_MECHANICAL_GATE"}
        decisions.append(decision)
    require(len(groups)==137,"Not 137 groups")
    summary={"schema":"e004_p2_arithmetic_first_mechanical_v1", "original_candidates_sha256":EXPECTED_ORIGINAL_SHA256,
             "mixed_export_sha256":EXPECTED_COMPACT_SHA256,
             "groups":len(groups),"eligible_chosen_responses":all_chosen,"eligible_rejected_responses":all_rejected,
             "groups_length_compatible":compatible,
             "groups_passing_mechanical_gates":sum(bool(d["top_pair"]) for d in decisions),
             "groups_approved_for_training":0,
             "reason_counts_per_response":dict(sorted(reason_counts.items())),
             "semantics_verified":False,"training_performed":False,
             "purpose":"Conservative pre-screen only; not a verified preference dataset."}
    return decisions,summary


def write_new(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes()==content,"Refusing overwrite of differing output: "+str(path))
    else:
        with path.open("xb") as f:f.write(content)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--out-dir",type=Path,required=True)
    args=parser.parse_args()
    raw=args.input.read_bytes()
    require(sha256(raw)==EXPECTED_COMPACT_SHA256,"Compact export SHA256 mismatch")
    groups=[json.loads(line) for line in raw.splitlines() if line.strip()]
    decisions,summary=screen(groups)
    require(len(groups)==137,"Unexpected mixed group count")
    jsonl=("\n".join(json.dumps(d,sort_keys=True) for d in decisions)+"\n").encode()
    summary["screen_results_sha256"]=sha256(jsonl)
    summary_json=(json.dumps(summary,indent=2,sort_keys=True)+"\n").encode()
    write_new(args.out_dir/"decisions_advisory.jsonl",jsonl)
    write_new(args.out_dir/"summary.json",summary_json)
    print(json.dumps(summary,indent=2,sort_keys=True))
    print("NO TRAINING; NO HUMAN OR SEMANTIC VERIFICATION; NO PAIRS APPROVED")

if __name__=="__main__":main()
