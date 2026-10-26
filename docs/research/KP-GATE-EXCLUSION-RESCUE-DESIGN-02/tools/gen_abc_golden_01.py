# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03: A/B/C経路(allow_inflection_normalization=False)の『変更前Production(git HEAD)の出力』を固定するgoldenを生成する。
実行(変更前のHEAD版er003_key_words_canonicalization/er105を置いたdirで): py gen_abc_golden_01.py <repo_root_with_HEAD_modules> <out.json>
生成物 abc_golden_01.json は er105_kp_rule_compliance_test_01.py がバイト一致で比較する。API 0。"""
import glob
import json
import os
import sys

root, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, root)
os.chdir(root)
import er003_key_words_canonicalization as kc   # noqa: E402

RD = os.path.join(root, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-DESIGN-02")
adv = json.load(open(os.path.join(RD, "adversarial_01.json"), encoding="utf-8"))
hp = json.load(open(os.path.join(RD, "have_probe_02.json"), encoding="utf-8"))
cases = []
for c in adv["conversions"]:
    cases.append((c["key"], c["display"], c["display"], "lemma_normalization", c["display"]))
    cases.append((c["key"], c["display"], c["display"], None, None))
for w in sorted(set(hp["newly_unblocked_windows"]) | set(hp["still_blocked_windows"])):
    cases.append((w, w, w, None, w))
    cases.append((w, w, "x " + w + " y", "lemma_normalization", w))
for c in adv["have_roles"]:
    cases.append((c["phrase"], c["phrase"], c["phrase"], None, None))
for pat in ("er019_output", "er026_output", "er121_output"):
    for f in sorted(glob.glob(os.path.join(root, pat, "**", "keywords_canonicalized.json"), recursive=True)):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:   # noqa: BLE001
            continue
        for it in d.get("items", []):
            dp, kp = it.get("display_phrase"), it.get("key_phrase") or it.get("used_form")
            if dp and kp:
                cases.append((kp, dp, dp, it.get("normalization_reason"), dp))
seen, uniq = set(), []
for c in cases:
    if c not in seen:
        seen.add(c)
        uniq.append(c)
rows = []
for key, disp, span, reason, orig in uniq:
    r = kc.validate_canonicalization_item(key, disp, span, normalization_reason=reason, original_span=orig, allow_inflection_normalization=False)
    rows.append({"args": [key, disp, span, reason, orig], "result": r, "aux": kc._contains_finite_auxiliary(key)})
json.dump({"n": len(rows), "rows": rows}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
print("golden rows:", len(rows))
