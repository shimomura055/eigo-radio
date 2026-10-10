# -*- coding: utf-8 -*-
"""C4 移植sha表の生成(RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C4、課金API 0件)。
Trial 3ファイルの constant/regex/関数のソース原文のsha256と、Production producer module 側のsha256を並べ、逐語一致を記録する。
実行: .venv/Scripts/python.exe -X utf8 er053_output/risk_flagger_production_wiring_01/gen_c4_port_sha_table_01.py
出力: er053_output/risk_flagger_production_wiring_01/c4_port_sha_table.json
Trial moduleは import せず、ソースファイルをastで読むだけ(この生成scriptはDEV専用。Productionから参照されない)。
"""
import ast
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
import er053_b3_deterministic_producer_01 as prod  # noqa: E402

SRC = {
    "b3sep_build_01.py (ROOTFIX-01 assembler)": "er052_output/b3_fact_instruction_separation_trial_01/b3sep_build_01.py",
    "b3r2_rank_02.py (ROOTFIX-02 D-det v2)": "er052_output/b3_rootfix_trial_02/b3r2_rank_02.py",
    "b3r2_eval_01.py (build_annotated ほか)": "er052_output/b3_rootfix_trial_02/b3r2_eval_01.py",
}
PROD = "er053_b3_deterministic_producer_01.py"


def segs(rel):
    src = open(os.path.join(REPO, rel), encoding="utf-8", newline="").read().replace("\r\n", "\n")
    lines = src.split("\n")
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef):
            out[node.name] = "\n".join(lines[node.lineno - 1:node.end_lineno])
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = "\n".join(lines[node.lineno - 1:node.end_lineno])
    return out


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def main():
    ours = segs(PROD)
    rows, trial_all = [], {}
    for label, rel in SRC.items():
        for k, v in segs(rel).items():
            trial_all.setdefault(k, []).append((label, v))
    for name in prod._PORTED_NAMES:
        cands = trial_all.get(name, [])
        src_label, ident = None, False
        for label, v in cands:
            if v == ours[name]:
                src_label, ident = label, True
                break
        rows.append({"symbol": name, "kind": "function" if ours[name].startswith("def ") else "constant", "trial_source": src_label or (cands[0][0] if cands else None),
                     "trial_sha256": sha(cands[0][1]) if cands else None, "production_sha256": sha(ours[name]), "byte_identical": ident})
    summary = {"n_symbols": len(rows), "n_identical": sum(r["byte_identical"] for r in rows), "rule_version": prod.RULE_VERSION,
               "rules_sha256": prod.rules_sha256(), "rows": rows,
               "not_ported": {"b3sep_build_01.py": ["assemble_Aprime (A'腕)"], "b3r2_rank_02.py": ["validate_number_ranks (LLM出力の検証)"],
                              "b3r2_eval_01.py": ["その他の評価関数群(M指標・Blind sheet等)"]}}
    with open(os.path.join(HERE, "c4_port_sha_table.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: summary[k] for k in ("n_symbols", "n_identical", "rule_version", "rules_sha256")}, indent=1))
    by = {}
    for r in rows:
        by.setdefault(r["trial_source"], []).append(r["symbol"])
    for k, v in by.items():
        print(k, len(v))
    assert summary["n_symbols"] == summary["n_identical"], [r["symbol"] for r in rows if not r["byte_identical"]]


if __name__ == "__main__":
    main()
