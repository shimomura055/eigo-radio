# -*- coding: utf-8 -*-
"""OCC-03 手計算照合: hand_contexts_03.txt を人が読んで決めた期待回数(規則表 RULES_01.md に従う)を、Production経路(exporter CLI)の出力と突き合わせる。API 0。
期待値の根拠: 各行の [区分#行] の文脈を目視し、確定(完全一致/活用形/人称スロット代名詞)だけを数えた。保留は uncertain として別記。"""
import json, os, sys
E = "docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/evidence_03/exports"
HAND = [  # (file, kind, term, 期待 counts(確定), 期待 uncertain合計)
 ("untidiness_family_resource__a2__cli.json", "phrase", "hear it out", {"story": 1}, 0),
 ("untidiness_family_resource__a2__cli.json", "word", "supplement", {"story": 4, "oneline": 2}, 0),          # supplement x3 + supplements x3 (story#0 x2, #2 'supplements', #8; oneline 'supplements' x2)
 ("untidiness_family_resource__b1b__cli.json", "phrase", "hear it out", {"story": 1}, 0),
 ("untidiness_family_resource__b1b__cli.json", "word", "clutter", {"story": 2, "comment": 1, "preview": 1, "oneline": 1}, 0),
 ("surname_choice__a2__cli.json", "phrase", "give something up", {"story": 1}, 0),                           # giving something up (something=it等の穴にsomethingそのもの=完全一致)
 ("surname_choice__a2__cli.json", "word", "thankful", {"story": 4}, 0),
 ("surname_choice__a2__cli.json", "word", "bothered", {"story": 1}, 2),                                      # bothered=確定1 / bother, bothers=別活用形=保留2
 ("surname_choice__b1b__cli.json", "phrase", "hold someone back", {"story": 1}, 0),                          # 選定表層 'hold my son back' の完全一致
 ("surname_choice__b1b__cli.json", "word", "grateful", {"story": 4}, 0),
 ("yuki_onna__a2__cli.json", "phrase", "slip away", {"story": 1}, 0),
 ("yuki_onna__a2__cli.json", "word", "mist", {"story": 1}, 0),
 ("yuki_onna__b1b__cli.json", "phrase", "slip away", {"story": 1}, 0),
 ("yuki_onna__b1b__cli.json", "word", "bar", {"story": 2}, 0),                                               # barred x2
]
bad = 0; rows = []
for f, kind, term, exp, unc in HAND:
    d = json.load(open(os.path.join(E, f), encoding="utf-8"))
    it = [x for x in d["phrases"] + d["words"] if x["term"] == term and (x.get("kind") == kind or True)][0]
    c = {k: v for k, v in it["occurrence"]["counts"].items() if v and k != "title"}
    u = sum((it["occurrence"].get("uncertain") or {}).values())
    ok = (c == exp and u == unc)
    bad += (not ok)
    rows.append({"file": f, "kind": kind, "term": term, "expected": exp, "expected_uncertain": unc, "actual": c, "actual_uncertain": u, "match": ok})
    print("%s %-9s %-22s exp=%s unc=%d | act=%s unc=%d" % ("OK " if ok else "NG ", kind, term, exp, unc, c, u))
json.dump(rows, open(os.path.join(os.path.dirname(E), "hand_check_03_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("mismatch=%d / %d" % (bad, len(HAND)))
sys.exit(1 if bad else 0)
