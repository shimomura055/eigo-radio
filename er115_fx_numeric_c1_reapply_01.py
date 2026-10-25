# -*- coding: utf-8 -*-
"""FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_06 C-1: 保存済みB3出力9本に『欄の数値をderive_ranksのStoryline同等として扱う』変更を決定論で再適用(API 0・DEV専用)。
出力: er115_output/fx_numeric_retention_trial_01/c1_reapply/ + docs/research/FX-CORE-NUMERIC-RETENTION-TRIAL-01/C1_REAPPLY_01.json"""
import json
import os
import sys

import er115_fx_numeric_retention_trial_01 as D

SAMPLES = [("moon_shrinking", "r6m1", False), ("moon_shrinking", "r6m2", False), ("coffee_prices", "r6c1", False),
           ("coffee_prices", "r6c2", False), ("semiconductor_earnings", "r6s1", False), ("semiconductor_earnings", "r6s2", False),
           ("coffee_prices", "r6c2", True), ("semiconductor_earnings", "r6s1", True), ("semiconductor_earnings", "r6s2", True)]
OUT_JSON = os.path.join(D.ROOT, "docs", "research", "FX-CORE-NUMERIC-RETENTION-TRIAL-01", "C1_REAPPLY_01.json")


def main():
    rows = []
    for article, sample, a1 in SAMPLES:
        sp = D.sample_dir(article, "A", sample)
        dst = os.path.join(D.OUT_ROOT, "c1_reapply", f"{sample}{'_attempt1' if a1 else ''}")
        r = D.reapply_field_priority(sp, dst, attempt1=a1)
        r["article"], r["sample_id"], r["attempt1"] = article, sample, a1
        rows.append(r)
        print(r["sample"], "base:", r["base"].get("status"), "->new:", r["new"].get("status"), "E_new=", r["new"].get("E"))
    D.wj(OUT_JSON, {"rows": rows})
    return 0


if __name__ == "__main__":
    sys.exit(main())
