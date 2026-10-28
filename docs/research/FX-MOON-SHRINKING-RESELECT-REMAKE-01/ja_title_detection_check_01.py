# 現行Production Primary判定(adapter, Azure stub, API 0)の検出能力確認: 月題原稿に対する負例(誤PASSさせてはいけない)と正例(通すべき)。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_detection_check_01.py
import json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
C = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
CASES = [
 ("正例: 原稿どおり(表層一致)", "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密", True),
 ("正例: 桁区切りなし+かな/カタカナ表記差", "月のシワ8900本超。その奥に潜む岩の上着の秘密", True),
 ("正例: 数詞を漢数字表記(八千九百)", "月のしわ、八千九百本超。その奥に潜む岩の上着の秘密", True),
 ("負例: しわ→すわ(N3-07型。Candidate E3で遮断済みの型)", "月のすわ、8,900本超。その奥に潜む岩の上着の秘密", False),
 ("負例: 値10倍(89,000)", "月のしわ、89,000本超。その奥に潜む岩の上着の秘密", False),
 ("負例: 値違い(8,000)", "月のしわ、8,000本超。その奥に潜む岩の上着の秘密", False),
 ("負例: 値違い(八千百)", "月のしわ、八千百本超。その奥に潜む岩の上着の秘密", False),
 ("負例: 岩→石", "月のしわ、8,900本超。その奥に潜む石の上着の秘密", False),
 ("負例: 語脱落(上着)", "月のしわ、8,900本超。その奥に潜む岩の秘密", False),
 ("今回a2型(月の詩は+八千九百): 現行Production", "月の詩は八千九百本超。その奥に潜む岩の上着の秘密", None),
]
E.api0_guard_on()
res = []
for name, p, expect_pass in CASES:
    r = E.primary_stage(C, p, False)
    ok = r["state"] in E.uj.PASSING_STATES
    res.append({"case": name, "primary": p, "state": r["state"], "reason": r["reason"], "passed": ok, "expected_pass": expect_pass,
                "as_expected": (None if expect_pass is None else ok == expect_pass)})
    print(json.dumps(res[-1], ensure_ascii=False))
E.api0_guard_off()
json.dump(res, open("docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_detection_check_01.out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
