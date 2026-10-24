# -*- coding: utf-8 -*-
"""er115 M4 較正(API 0円)。人手ラベル(blind_labels_01.json; 照合関数の結果を見る前に本文を読んで付与)と、
旧照合(er114.ja_present / en_present)・新照合(er115.match_core / en_present)を突き合わせる。
加えて、Opus指摘の弱点(単位の言い換え・単位なし一致)を突く合成ストレスケース(著者が作成。コーパス由来ではない)で旧/新を比較する。
出力: er115_output/fx_numeric_retention_trial_01/calibration/calibration_result_01.json"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er114_fx_numeric_trace_01 as T   # noqa: E402
import er115_fx_numeric_retention_trial_01 as D   # noqa: E402

CAL_DIR = os.path.join(ROOT, "er115_output", "fx_numeric_retention_trial_01", "calibration")

# (surface, unit_hint, text, expected_present, note)  すべて合成(月・新聞型の表現を想定)。
SYNTHETIC = [
    # 単位の言い換え(陽性: 旧は偶然当たる/外れる、新は当てる)
    ("約42〜46", "m", "月の半径は約42から46メートル縮んだと推定された。", True, "m->メートル+範囲から"),
    ("約42〜46", "m", "半径は42〜46 m縮んだ。", True, "m表記そのまま"),
    ("約42〜46", "m", "半径は約42～46mほど縮んだ。", True, "全角波ダッシュ"),
    ("25%", "", "指数は25パーセント下落した。", True, "%->パーセント"),
    ("25%", "", "指数は２５％下落した。", True, "全角"),
    ("約9か月", "", "反映まで約9カ月かかる。", True, "か月->カ月"),
    ("約9か月", "", "反映まで9ヶ月かかる。", True, "か月->ヶ月"),
    ("約5,470本", "", "長さ1km超は約5470本だった。", True, "カンマ無し"),
    ("8,900本超", "", "8900本を超える崖を記録した。", True, "超->を超える"),
    ("最大£1,000", "", "最大1,000ポンドの罰金。", True, "£->ポンド"),
    ("最大50", "セント", "増減は10セントずつ、最大50セントまで。", True, "単位hint(セント)"),
    ("1.1", "km", "少なくとも約1.1キロメートル縮む。", True, "km->キロメートル"),
    # 陰性(誤判定を起こすべきでない): 旧は『単位なし同士=一致』で誤って True になりうる
    ("約42〜46", "m", "約42〜46人が参加した。", False, "単位違い(人): 旧=FP候補"),
    ("約42〜46", "m", "半径は約44メートル縮んだ。", False, "別の値"),
    ("約42〜46", "m", "傾きの想定範囲は42〜46度だった。", False, "単位違い(度): 旧=FP候補"),
    ("25%", "", "25人が反対した。", False, "単位違い"),
    ("7か月", "", "7日間で終わった。", False, "単位違い"),
    ("約9か月", "", "約9年かかる。", False, "単位違い"),
    ("3倍", "", "3人で分けた。", False, "単位違い"),
    ("最大50", "セント", "最大50人まで。", False, "単位hint(セント)に反する"),
    ("約45", "m", "約45度の傾き。", False, "単位違い(度)"),
]


def old_present(surface, text):
    keys = [T.skey(s) for s in T.P.extract_surfaces(text)]
    return bool(T.ja_present(surface, text, keys))


def run():
    lab = json.load(open(os.path.join(CAL_DIR, "blind_labels_01.json"), encoding="utf-8"))
    dump_p = os.path.join(CAL_DIR, "corpus_texts_for_labels.json")
    runs = {}
    for i, run in enumerate(T.discover()):
        ann = T.rj(os.path.join(run, "storyline_b3", "annotation.json"))
        tx = T.stage_texts(run)
        ann_md = os.path.join(run, "storyline_b3", "selected_brief_annotated.md")
        facts_marked = D.w1.parse_brief_md(D.rdt(ann_md))[1] if os.path.exists(ann_md) else ""
        approx = D.approx_forms_of(run)
        runs[i] = {"run": os.path.relpath(run, ROOT).replace("\\", "/"), "texts": tx, "facts_marked": facts_marked, "approx": approx}
    res = {"labels_sha256": D.sha_text(open(os.path.join(CAL_DIR, "blind_labels_01.json"), encoding="utf-8").read()),
           "old": {"TP": 0, "FP": 0, "FN": 0, "TN": 0}, "new": {"TP": 0, "FP": 0, "FN": 0, "TN": 0},
           "partial": [], "diff_old_new": [], "weak_new": 0, "errors": []}
    for r in lab["rows"]:
        run = runs[r["run_id"]]
        assert run["run"] == r["run"], (run["run"], r["run"])
        text = run["texts"][r["stage"]]
        hint = D.unit_hint_after(run["facts_marked"], r["surface"])
        old = old_present(r["surface"], text)
        m = D.match_core(r["surface"], text, hint, [run["approx"].get(D.nfkc(r["surface"]))])
        new = m["present"]
        if m["mode"] == "weak":
            res["weak_new"] += 1
        if r["label"] == "partial":
            res["partial"].append({**r, "old": old, "new": new})
            continue
        exp = r["label"] == "present"
        for name, got in (("old", old), ("new", new)):
            key = ("TP" if got else "FN") if exp else ("FP" if got else "TN")
            res[name][key] += 1
            if name == "new" and key in ("FP", "FN"):
                res["errors"].append({**r, "hint": hint, "kind": key, "mode": m["mode"]})
        if old != new:
            res["diff_old_new"].append({**r, "hint": hint, "old": old, "new": new, "mode": m["mode"]})
    syn = {"old": {"TP": 0, "FP": 0, "FN": 0, "TN": 0}, "new": {"TP": 0, "FP": 0, "FN": 0, "TN": 0}, "cases": []}
    for surface, hint, text, exp, note in SYNTHETIC:
        old = old_present(surface, text)
        new = D.match_core(surface, text, hint)["present"]
        row = {"surface": surface, "hint": hint, "text": text, "expected": exp, "old": old, "new": new, "note": note}
        for name, got in (("old", old), ("new", new)):
            syn[name][("TP" if got else "FN") if exp else ("FP" if got else "TN")] += 1
        syn["cases"].append(row)
    res["synthetic"] = syn
    # 英訳側: m/meters
    en_cases = [("約42〜46", "m", "shrank by about 42 to 46 meters", True), ("約42〜46", "m", "about 42 to 46 people came", False),
                ("25%", "", "fell 25 percent", True), ("約4億年", "", "about 400 million years ago", True),
                ("約4億年", "", "about 400 million dollars", False)]
    res["en_synthetic"] = [{"surface": s, "hint": h, "text": t, "expected": e, "new": bool(D.en_present(s, t, h)),
                            "old": bool(T.en_present(s, t)), "note": ""} for s, h, t, e in en_cases]
    os.makedirs(CAL_DIR, exist_ok=True)
    with open(os.path.join(CAL_DIR, "calibration_result_01.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    return res


if __name__ == "__main__":
    r = run()
    print("corpus(122 labeled, partial除外) old:", r["old"], "new:", r["new"], "weak_new:", r["weak_new"])
    print("synthetic(%d) old:" % len(SYNTHETIC), r["synthetic"]["old"], "new:", r["synthetic"]["new"])
    for e in r["errors"]:
        print("NEW-ERR", e)
    for c in r["synthetic"]["cases"]:
        if c["new"] != c["expected"] or c["old"] != c["expected"]:
            print("SYN", "old" if c["old"] != c["expected"] else "", "NEW" if c["new"] != c["expected"] else "", c["surface"], c["note"], "|", c["text"])
    for c in r["en_synthetic"]:
        print("EN", c["surface"], "exp", c["expected"], "old", c["old"], "new", c["new"])
    print("partial:", [(p["run_id"], p["surface"], p["stage"], p["old"], p["new"]) for p in r["partial"]])
