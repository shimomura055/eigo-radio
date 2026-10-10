# -*- coding: utf-8 -*-
"""C2後の dangling reference 走査結果を保存し、残件を分類する(RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2、課金API 0件)。

走査本体は C1 の er053_dangling_reference_check_01.scan()(grep list・Production scope 9ファイルは C1 baseline と同一)。
残件(語単位の出現)を行単位で次に分類する:
  technical_qa_vocabulary   : 技術QA側の語彙(段落3分割retryの must_fix kwarg 等、音声化禁止記号QAのstage tag/evidence key)。維持対象。
  review_label_not_checker  : Opus L2レビュー所見ラベル(MAJOR-n 等)。旧Fact Checkerの severity=MAJOR とは無関係。
  trial_or_historical       : Trial/historical code(Production scope内では0件になる想定)
  truly_orphaned            : どれにも分類できない残件(0であること)
実行: .venv/Scripts/python.exe -X utf8 er053_output/risk_flagger_production_wiring_01/gen_dangling_after_c2_01.py
出力: er053_output/risk_flagger_production_wiring_01/dangling_after_c2.json
"""
import json
import os
import re
import sys

sys.dont_write_bytecode = True
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)

import er053_dangling_reference_check_01 as dg  # noqa: E402

# 行単位の分類規則(上から順に最初に一致したものを採用)
CLASS_RULES = [
    ("technical_qa_vocabulary", re.compile(r"_symbol_must_fix|symbol_must_fix|_FAMILY_X_PARAGRAPH_RETRY_MUST_FIX"),
     "段落3分割retry(must_fix kwargは技術QA、adv_gen/std_gen共有)・音声化禁止記号QA(T-01/T-02)のstage tag/evidence key"),
    ("review_label_not_checker", re.compile(r"MAJOR-\d"), "Opus L2レビュー所見ラベル(MAJOR-n)。旧Fact Checkerのseverity語ではない"),
]


def classify():
    res = dg.scan()
    words = list(dg.WORDS_CASE_SENSITIVE)
    out_files, totals = {}, {"technical_qa_vocabulary": 0, "review_label_not_checker": 0, "trial_or_historical": 0,
                             "truly_orphaned": 0}
    details = []
    for f in dg.SCOPE_FILES:
        p = os.path.join(REPO, f)
        per = {"technical_qa_vocabulary": 0, "review_label_not_checker": 0, "trial_or_historical": 0, "truly_orphaned": 0}
        for ln, line in enumerate(open(p, encoding="utf-8", errors="replace").read().split("\n"), 1):
            n = sum(line.count(w) for w in dg.SYMBOLS) + sum(line.count(w) for w in words) \
                + len(re.findall("|".join(re.escape(w) for w in dg.WORDS_CASE_INSENSITIVE), line, flags=re.I))
            if not n:
                continue
            cat = "truly_orphaned"
            for name, rx, _why in CLASS_RULES:
                if rx.search(line):
                    cat = name
                    break
            per[cat] += n
            totals[cat] += n
            details.append({"file": f, "line": ln, "count": n, "category": cat, "text": line.strip()[:140]})
        out_files[f] = per
    baseline = json.load(open(os.path.join(REPO, "er053_output", "risk_flagger_production_wiring_01", "dangling_baseline_c1.json"),
                              encoding="utf-8"))
    fact_checker_symbol_total = sum(sum(c.get(s, 0) for s in dg.SYMBOLS) for c in res["per_file"].values())
    return {
        "generated_for": "RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2",
        "baseline_c1_total_hits": baseline.get("total_hits"),
        "after_c2_total_hits_raw": res["total_hits"],
        "after_c2_fact_checker_symbols_total": fact_checker_symbol_total,
        "after_c2_residual_by_category": totals,
        "unclassified_truly_orphaned": totals["truly_orphaned"],
        "classification_rules": [{"category": n, "regex": rx.pattern, "rationale": why} for n, rx, why in CLASS_RULES],
        "per_file": out_files,
        "raw_per_file_counts": res["per_file"],
        "residual_lines": details,
        "scope_files": dg.SCOPE_FILES,
        "note": ("Fact Checker専用シンボル(JAFactCheckStopError/JARecheckRequiredError/run_deviation_check/open243_*/OPEN243_*/ja_recheck 等"
                 " 25種)の残存は0。残る語は技術QA語彙とレビュー所見ラベルのみ(分類済み)。audio runnerの MAJOR 20件は全て Opus L2所見ラベル"
                 "(MAJOR-1/3/4等のコメント・文字列)で C3 の対象外。"),
    }


def main():
    data = classify()
    p = os.path.join(REPO, "er053_output", "risk_flagger_production_wiring_01", "dangling_after_c2.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: data[k] for k in ("baseline_c1_total_hits", "after_c2_total_hits_raw", "after_c2_fact_checker_symbols_total",
                                           "after_c2_residual_by_category", "unclassified_truly_orphaned")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
