# -*- coding: utf-8 -*-
"""ラベル分離ステップ(委任_01B)。casebank_01.json -> <stem>_blind.json(ラベル列なし) + <stem>_labels.json(集計専用)。
検出器(run_flagger_01.py)は *_blind.json だけを読み、*_labels.json は aggregate_flagger_01.py だけが読む。
ラベル列 = run_flagger_01.FORBIDDEN_KEYS に載るキー + labelsキー。
"""
import json
import os
import sys

LABEL_KEYS = {"label", "labels", "gold", "expected", "human_label", "human_judgement", "severity_label",
              "known_incident", "incident_id", "checker_reference", "checker_verdict", "label_note", "type_label"}


def split_cases(data):
    cases = data["cases"] if isinstance(data, dict) else data
    blind, labels = [], {}
    for c in cases:
        blind.append({k: v for k, v in c.items() if k not in LABEL_KEYS})
        labels[c["case_id"]] = {k: v for k, v in c.items() if k in LABEL_KEYS}
    return blind, labels


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("usage: make_blind_01.py casebank_01.json [out_dir]")
        return 2
    src = argv[0]
    out_dir = argv[1] if len(argv) > 1 else os.path.dirname(os.path.abspath(src))
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    blind, labels = split_cases(data)
    stem = os.path.splitext(os.path.basename(src))[0]
    bp = os.path.join(out_dir, stem + "_blind.json")
    lp = os.path.join(out_dir, stem + "_labels.json")
    with open(bp, "w", encoding="utf-8") as f:
        json.dump({"cases": blind}, f, ensure_ascii=False, indent=1)
    with open(lp, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=1)
    print("blind=%s (%d cases) labels=%s" % (bp, len(blind), lp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
