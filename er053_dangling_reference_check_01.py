# -*- coding: utf-8 -*-
"""er053_dangling_reference_check_01.py
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1(追加のみ、2026-10-10)。Dangling reference check script(読み取り専用、¥0)。

旧Fact Checker撤去(C2)の前後で「撤去対象への残存参照」を数えるためのgrep list走査。
C1時点の件数をbaselineとして出力する(C2で0または`SUPERSEDED`注記済みのみ、をS8として確認するための基準)。

走査対象(Production正式経路ファイル群。DESIGN_03 6-4 のProduction scope):
  er012_e_family_entertainment_two_level_runner_01.py / er019_family_x_entertainment_production_runner_01.py /
  er019_family_x_ja_writer_o_r1_r2_01.py / er019_family_x_audio_production_runner_01.py /
  er053_family_x_factlock_ja_writer_01.py / er053_risk_flagger_production_01.py / er053_review_queue_01.py /
  er053_b3_annotation_contract_01.py / er053_en_sentence_splitter_01.py
grep list: DESIGN_03 6-4(シンボル群) + 委任_06 指定の語(Stage1/Stage2/reclassify/MAJOR/MINOR/JA_RECHECK_REQUIRED/must_fix/
Deviation Check/Local Rewrite/full rewrite/Checker recovery/OPEN243_*)。
使い方: .venv/Scripts/python.exe -X utf8 er053_dangling_reference_check_01.py [--out <json path>]
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SCOPE_FILES = [
    "er012_e_family_entertainment_two_level_runner_01.py",
    "er019_family_x_entertainment_production_runner_01.py",
    "er019_family_x_ja_writer_o_r1_r2_01.py",
    "er019_family_x_audio_production_runner_01.py",
    "er053_family_x_factlock_ja_writer_01.py",
    "er053_risk_flagger_production_01.py",
    "er053_review_queue_01.py",
    "er053_b3_annotation_contract_01.py",
    "er053_en_sentence_splitter_01.py",
]

# DESIGN_03 6-4 のシンボル群(大文字小文字を区別)
SYMBOLS = [
    "OPEN243_M1", "OPEN243_M2", "OPEN243_G3_TELEMETRY_PATH", "OPEN233_RECLASSIFY_PROTECT_FLAGS", "open243_m1_enabled", "_open243_iol",
    "open243_g3_record_translation_minor", "open243_m1_summary_only_retry", "open243_majors_only_in_summary",
    "JARecheckRequiredError", "JAFactCheckStopError", "_must_fix_from_deviations", "_major_deviations", "build_must_fix_block",
    "original_must_fix", "ja_original_check", "ja_r2_check", "deviation_overall_status", "must_fix_used", "retried_for_deviation",
    "ja_recheck", "fact_checks_summary", "full_ledger_text=", "run_deviation_check", "er019_writer_run_summary_reconstruction",
]
# 委任_06 指定の語(自然語を含むため大文字小文字を区別しない語は別扱い)
WORDS_CASE_SENSITIVE = ["Stage1", "Stage2", "reclassify", "MAJOR", "MINOR", "JA_RECHECK_REQUIRED", "must_fix", "OPEN243_", "OPEN233_"]
WORDS_CASE_INSENSITIVE = ["Deviation Check", "Local Rewrite", "full rewrite", "Checker recovery"]


def count_in_text(text: str) -> dict:
    out = {}
    for s in SYMBOLS:
        n = text.count(s)
        if n:
            out[s] = n
    for w in WORDS_CASE_SENSITIVE:
        n = text.count(w)
        if n:
            out[w] = n
    for w in WORDS_CASE_INSENSITIVE:
        n = len(re.findall(re.escape(w), text, flags=re.I))
        if n:
            out[w + " (ci)"] = n
    return out


def scan(root: str = HERE, files=None) -> dict:
    files = files or SCOPE_FILES
    per_file, totals = {}, {}
    for f in files:
        p = os.path.join(root, f)
        if not os.path.exists(p):
            per_file[f] = {"_missing": True}
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            counts = count_in_text(fh.read())
        per_file[f] = counts
        for k, v in counts.items():
            totals[k] = totals.get(k, 0) + v
    return {"scope_files": files, "per_file": per_file, "totals": totals,
            "total_hits": sum(totals.values()),
            "symbols": SYMBOLS, "words_case_sensitive": WORDS_CASE_SENSITIVE, "words_case_insensitive": WORDS_CASE_INSENSITIVE}


def main(argv):
    out = None
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    res = scan()
    txt = json.dumps(res, ensure_ascii=False, indent=2)
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
