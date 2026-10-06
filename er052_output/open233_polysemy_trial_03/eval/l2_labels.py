# -*- coding: utf-8 -*-
# L2内容ラベル(評価のみ、Sonnet判断、人手確認前)。値は l1_labels.py と同じ体系。
# 一致: Y一致/P部分/N不一致/- 対象外。型: V=真の逆転型(妥当)/D=変質止まり/H=hedge・帰属・範囲限定=誤り/X=Rが不自然=誤り
import json, re, sys
from pathlib import Path

TRIAL = Path(__file__).resolve().parents[1]
P2, P2N = "B2_twostage_hint", "B2n_twostage_nohint"
L = {}


def add(pat, theme, fid, m, t, why=""):
    L[(pat, theme, fid)] = (m, t, 0, why)


def bulk(pat, theme, spec):
    for fid, m, t in spec:
        add(pat, theme, fid, m, t)


# ---- B2(hint) ----
bulk(P2, "meta", [("MUSE-HC-001", "-", "V"), ("MUSE-HC-002", "-", "D"), ("MUSE-HC-003", "-", "D"), ("MUSE-HC-006", "-", "V"), ("MUSE-HC-007", "-", "V"),
                  ("MUSE-HC-012", "P", "D"), ("MUSE-HC-014", "N", "V"), ("MUSE-HC-015", "-", "D")])
add(P2, "meta", "MUSE-HC-012", "P", "D", "当面ロールバック↔恒久廃止。何を戻したか(方向)は未言及(L1-Bと同)")
add(P2, "meta", "MUSE-HC-014", "N", "V", "条件付き公開↔公開済みの段階反転で妥当だが既知誤読(商業者との改善の対象)とは別")
bulk(P2, "hormuz", [("HF-003", "-", "V"), ("HF-004", "-", "H"), ("HF-007", "P", "V"), ("HF-008", "-", "V"), ("HF-012", "-", "H")])
add(P2, "hormuz", "HF-007", "P", "V", "投稿段階↔置換完了。途中/最終の観点は薄い(L1-Bと同)")
bulk(P2, "space_weapons", [("F-002", "Y", "V"), ("F-007", "Y", "V"), ("F-008", "-", "V"), ("F-009", "Y", "V"), ("F-014", "-", "V"), ("F-019", "-", "X"),
                           ("F-020", "-", "X"), ("F-021", "-", "D"), ("F-024", "-", "V")])
bulk(P2, "sewer", [("F-008", "-", "V"), ("F-010", "N", "V"), ("F-011", "Y", "V"), ("F-012", "-", "V"), ("F-013", "-", "V"), ("F-016", "Y", "V")])
add(P2, "sewer", "F-010", "N", "V", "方針策定↔切替完了で既知の区域取違えとは別(L1-Bと同)")
bulk(P2, "ai_control", [("EVID-001", "-", "V"), ("EVID-002", "-", "V"), ("EVID-005", "-", "V"), ("EVID-006", "Y", "V"), ("EVID-007", "-", "V"),
                        ("EVID-008", "-", "D"), ("EVID-010", "-", "V"), ("CONTROL-002", "-", "V")])
bulk(P2, "A02", [("POL-02", "-", "V"), ("POL-03", "-", "D"), ("POL-04", "-", "V"), ("PILOT-04", "-", "D")])
# ---- B2n(nohint) ----
bulk(P2N, "meta", [("MUSE-HC-001", "-", "V"), ("MUSE-HC-002", "-", "D"), ("MUSE-HC-003", "-", "D"), ("MUSE-HC-006", "-", "V"), ("MUSE-HC-015", "-", "D")])
bulk(P2N, "hormuz", [("HF-002", "-", "V")])
bulk(P2N, "space_weapons", [("F-001", "N", "V"), ("F-002", "Y", "V"), ("F-003", "-", "X"), ("F-004", "-", "X"), ("F-005", "-", "X"), ("F-007", "Y", "V"),
                            ("F-008", "-", "V"), ("F-014", "-", "V"), ("F-015", "-", "D"), ("F-019", "-", "X"), ("F-020", "-", "X"), ("F-021", "-", "D")])
add(P2N, "space_weapons", "F-001", "N", "V", "防護用途↔攻撃用途の取違えで、既知(初めて認めた発言→初めて配備)とは別")
bulk(P2N, "sewer", [("F-003", "-", "V"), ("F-004", "-", "H"), ("F-007", "-", "V"), ("F-008", "-", "V"), ("F-010", "Y", "V"), ("F-011", "Y", "V")])
add(P2N, "sewer", "F-010", "Y", "V", "市街化区域/調整区域の方式取違えを明示")
bulk(P2N, "ai_control", [("EVID-001", "-", "V"), ("EVID-002", "-", "V"), ("EVID-005", "-", "V"), ("EVID-006", "Y", "V"), ("EVID-007", "-", "V"),
                         ("EVID-008", "-", "D"), ("EVID-009", "-", "V"), ("EVID-010", "-", "V"), ("CONTROL-002", "-", "V")])
bulk(P2N, "A02", [("POL-02", "-", "V"), ("POL-04", "-", "V"), ("PILOT-01", "-", "H"), ("PILOT-02", "-", "D")])
bulk(P2N, "small_bag", [("F015", "-", "D")])

TYPE = {"V": "真の逆転型(妥当)", "D": "変質止まり", "H": "hedge・帰属・範囲=誤り", "X": "Rが不自然=誤り"}
MATCH = {"Y": "一致", "P": "部分", "N": "不一致", "-": "-(対象外)"}
AMB = re.compile("改める|改め|見直|改善|修正")
BAR = "|"
BAR_ESC = chr(92) + "|"


def main():
    ev = TRIAL / "eval"
    tg = json.loads((ev / "targets.json").read_text(encoding="utf-8"))["themes"]
    ho = json.loads((ev / "holdout.json").read_text(encoding="utf-8"))["themes"]
    th = {**tg, **ho}
    summary = {}
    for pat in (P2, P2N):
        lines = ["# content label sheet(L2評価のみ・Sonnet判断・人手確認前): %s" % pat,
                 "凡例: l1と同じ。警告=R_is_natural_reading=false。", "",
                 "| theme | fact_id | note(逐語) | 既知誤読との一致 | 型 | 台帳外混入 | 曖昧語流用 | 警告 | 根拠 |", "|---|---|---|---|---|---|---|---|---|"]
        cnt = {"V": 0, "D": 0, "H": 0, "X": 0, "n": 0, "foreign": 0, "amb": 0, "extra_n": 0, "extra_V": 0, "extra_D": 0, "extra_bad": 0,
               "T_Y": 0, "T_P": 0, "T_N": 0, "warn": 0}
        for s in th:
            notes = json.loads((TRIAL / "runs" / pat / s / "notes.json").read_text(encoding="utf-8"))
            for n in notes:
                key = (pat, s, n["fact_id"])
                if key not in L:
                    raise SystemExit("label missing: %s" % (key,))
                m, ty, fo, why = L[key]
                amb = 1 if AMB.search(n["note"]) else 0
                w = ",".join(n.get("warnings") or []) or "-"
                lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                    s, n["fact_id"], n["note"].replace(BAR, BAR_ESC), MATCH[m], TYPE[ty], "有" if fo else "無", "有" if amb else "無", w, why))
                if s in tg:
                    cnt["n"] += 1; cnt[ty] += 1; cnt["foreign"] += fo; cnt["amb"] += amb; cnt["warn"] += 1 if w != "-" else 0
                    if m == "-":
                        cnt["extra_n"] += 1
                        cnt["extra_V" if ty == "V" else "extra_D" if ty == "D" else "extra_bad"] += 1
                    else:
                        cnt["T_" + m] += 1
        lines += ["", "## 対象の見落とし(FN)と理由(judgments_all/rejectedより)", ""]
        for s, t in tg.items():
            d = TRIAL / "runs" / pat / s
            att = {n["fact_id"] for n in json.loads((d / "notes.json").read_text(encoding="utf-8"))}
            ja = {x["fact_id"]: x for x in json.loads((d / "judgments_all.json").read_text(encoding="utf-8"))}
            rj = {r["fact_id"]: r["reason"] for r in json.loads((d / "rejected.json").read_text(encoding="utf-8"))}
            for f in t["targets"]:
                if f in att:
                    continue
                x = ja.get(f)
                reason = ("rejected:%s(stage1通過・stage2でnote生成済み)" % rj[f]) if f in rj else ("stage1 " + "; ".join(x["dropped_by"]) if x and x["dropped_by"] else "不明")
                lines.append("- %s %s: %s" % (s, f, reason))
        (ev / ("%s_content_label_sheet.md" % pat)).write_text("\n".join(lines), encoding="utf-8")
        summary[pat] = cnt
    (ev / "l2_label_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
