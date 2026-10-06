# -*- coding: utf-8 -*-
# L3内容ラベル(評価のみ、Sonnet判断、人手確認前)。出力名はl3を含む(L1/L2のsheetは上書きしない)。
import json, collections
from pathlib import Path

TRIAL = Path(__file__).resolve().parents[1]
PAT = "B3_twostage_gate"
# 一致: Y/P/N/-(対象外)。型: V=真の逆転型(妥当)/D=変質止まり/H=誤り(hedge等)/X=Rが不自然
LAB = {("meta", "MUSE-HC-003"): ("-", "D", "設計説明段階↔実運用稼働の段階反転だが主題結論を変えるほどではない(L2 B2と同判断)"),
       ("space_weapons", "F-001"): ("N", "V", "防護用途↔攻撃用途の取違えで妥当だが既知誤読(初めて認めた発言→初めて配備)とは別(B2nと同判断)")}
TYPE = {"V": "真の逆転型(妥当)", "D": "変質止まり", "H": "hedge・帰属・範囲=誤り", "X": "Rが不自然=誤り"}
MATCH = {"Y": "一致", "P": "部分", "N": "不一致", "-": "-(対象外)"}


def main():
    ev = TRIAL / "eval"
    tg = json.loads((ev / "targets.json").read_text(encoding="utf-8"))["themes"]
    ho = json.loads((ev / "holdout.json").read_text(encoding="utf-8"))["themes"]
    th = {**tg, **ho}
    lines = ["# content label sheet(L3評価のみ・Sonnet判断・人手確認前): %s" % PAT, "凡例: l1/l2と同じ。", "",
             "| theme | fact_id | note(逐語) | 字数 | 既知誤読との一致 | 型 | 台帳外混入 | 警告 | 根拠 |", "|---|---|---|---|---|---|---|---|---|"]
    S = collections.Counter()
    per = {}
    for s in th:
        d = TRIAL / "runs" / PAT / s
        notes = json.loads((d / "notes.json").read_text(encoding="utf-8"))
        per[s] = len(notes)
        for n in notes:
            m, ty, why = LAB[(s, n["fact_id"])]
            lines.append("| %s | %s | %s | %d | %s | %s | 無 | %s | %s |" % (s, n["fact_id"], n["note"], len(n["note"]), MATCH[m], TYPE[ty], ",".join(n.get("warnings") or []) or "-", why))
            if s in tg:
                S["n"] += 1; S[ty] += 1
                S["extra" if m == "-" else "T_" + m] += 1
    lines += ["", "## stage1.5判定(対象factのみ。cid別likelihood)と対象の見落とし(FN)", ""]
    for s, t in tg.items():
        ja = {x["fact_id"]: x for x in json.loads((TRIAL / "runs" / PAT / s / "judgments_all.json").read_text(encoding="utf-8"))}
        att = {n["fact_id"] for n in json.loads((TRIAL / "runs" / PAT / s / "notes.json").read_text(encoding="utf-8"))}
        for f in t["targets"]:
            x = ja[f]
            lv = ",".join("%s=%s" % (v["cid"], v["likelihood"]) for v in x.get("stage1_5", [])) or "-"
            lines.append("- %s %s: stage1通過(run1,run2)=%s / stage1.5=%s / %s" % (s, f, x["stage1_run_pass"], lv, "付与" if f in att else "FN: " + ";".join(x["dropped_by"])))
    for s, t in ho.items():
        ja = {x["fact_id"]: x for x in json.loads((TRIAL / "runs" / PAT / s / "judgments_all.json").read_text(encoding="utf-8"))}
        for f in t["targets"]:
            x = ja[f]
            lv = ",".join("%s=%s" % (v["cid"], v["likelihood"]) for v in x.get("stage1_5", [])) or "-"
            lines.append("- (holdout参考) %s %s: stage1通過=%s / stage1.5=%s / %s" % (s, f, x["stage1_run_pass"], lv, ";".join(x["dropped_by"]) or "付与"))
    (ev / ("%s_content_label_sheet.md" % PAT)).write_text("\n".join(lines), encoding="utf-8")
    (ev / "l3_label_summary.json").write_text(json.dumps({"core": dict(S), "per_theme_attached": per}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(dict(S), per)


if __name__ == "__main__":
    main()
