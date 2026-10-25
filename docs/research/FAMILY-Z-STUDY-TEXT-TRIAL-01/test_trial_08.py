# Trial-08 テスト(API 0)。 py test_trial_08.py
# (1) run_trial_08 selftest(Tier規則・Prompt差分1文のみ・例文漏れなし) (2) Trial-07テストが不変 (3) Trial-07データへの再適用で「変化は優先順位由来のみ」(INVを選んでいた標本でのみ変わる)
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_trial_08 as t8, run_trial_07 as t7
t8.selftest()
t7.selftest()
o = t8.reselect()
for w, rows in o.items():
    for r in rows:
        if r["changed"]: assert any(m["feature_class"] == "INV" for m in r["old"]) and r["tier"] == "T1", (w, r["run"])   # 変化は旧選定がINVでTier1が存在する標本のみ
        else: assert [m["para"] for m in r["old"]] == [m["para"] for m in r["new"]], (w, r["run"])
        assert len(r["new"]) <= 1
print("test_trial_08 OK")
