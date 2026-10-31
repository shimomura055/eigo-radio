# -*- coding: utf-8 -*-
"""ユーザー承認3項目(2026-10-31)が正式moduleの実出力に一致するか。合成文(1行1unit)で count_entry を呼ぶ。API 0。"""
import os, sys, json
sys.path.insert(0, os.getcwd())
import er140_selection_occurrence_count_01 as oc
SEC = {"story": ["She put it away. He put the books away. They put away the toys."], "comment": [], "preview": [], "oneline": [], "title": [""]}
CASES = [
 ("承認1 代名詞1語の分離句動詞=確定", "put away", "put it away", {"story": 2}, 0),   # put it away + put away(完全一致)=確定2。put the books away=保留
 ("承認3 名詞句挿入=確定せず保留", "put away", "put away", None, 1),
 ("承認2 別語にもなり得る活用形(build->building)=保留", "build", "build", {}, 1, ["We saw a tall building."]),
 ("承認2 lie->lay=保留", "lie", "lie", {}, 1, ["She lay on the bed."]),
 ("承認2 good->goods=保留", "good", "good", {}, 1, ["They sell goods here."]),
 ("承認2 see->saw=保留", "see", "see", {}, 1, ["I saw a bird."]),
]
res = []; bad = 0
for case in CASES:
    label, term, sel, exp, unc = case[:5]
    sec = dict(SEC)
    if len(case) > 5: sec = dict(SEC, story=case[5])
    r = oc.count_entry(sec, term, sel)
    counts = {k: v for k, v in r["counts"].items() if v}
    u = sum((r.get("uncertain") or {}).values())
    ok = (exp is None or counts == exp) and u >= unc and (exp is not None or counts.get("story", 0) == 2)
    if label.startswith("承認3"): ok = (u >= 1 and counts.get("story") == 2)   # 同一文章: 確定は上の2件のみ、'put the books away'は未計上
    bad += (not ok)
    res.append({"case": label, "term": term, "selection_phrase": sel, "counts": counts, "uncertain": u, "uncertain_forms": r.get("uncertain_forms"), "ok": ok})
    print("OK " if ok else "NG ", label, counts, "uncertain=%d" % u, r.get("uncertain_forms"))
json.dump(res, open(os.path.join("docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/evidence_03", "approved3_check_03_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
sys.exit(1 if bad else 0)
