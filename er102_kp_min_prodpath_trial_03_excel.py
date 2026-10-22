# -*- coding: utf-8 -*-
"""KPMP3 Excel生成(API 0)。出力: docs/research/FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03/KP_MIN_PRODPATH_COMPARISON_03.xlsx"""
import json, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "er102_output" / "kp_min_prodpath_trial_03"
DST = ROOT / "docs" / "research" / "FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03" / "KP_MIN_PRODPATH_COMPARISON_03.xlsx"


def J(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def hdr(ws, row, fill="DDEBF7"):
    for c in ws[row]:
        c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor=fill); c.alignment = Alignment(wrap_text=True, vertical="top")


def main():
    val = J(OUT / "validation.json"); ev = J(OUT / "eval_summary.json"); man = J(ROOT / "er098_output/kp_six_model_trial_01/inputs/manifest.json")
    par = J(OUT / "prompt_parity.json"); S = val["summary"]; cost = J(OUT / "cost_summary.json")
    wb = Workbook()
    ws = wb.active; ws.title = "1_記事x順位 KP横並び"
    ws.append(["unit_id", "記事", "レベル", "rank", "既存Production key_phrase", "Arm A 選定直後(display_phrase)", "Arm A canonical後(key_phrase)", "Arm A 本文span",
               "Arm B 選定直後(display_phrase)", "Arm B canonical後(key_phrase)", "Arm B 本文span", "Arm A status", "Arm B status", "備考"])
    hdr(ws, 1)
    for u in man["units"]:
        uid = u["unit_id"]; d = val["units"][uid]; note = []
        if d["A"].get("kp_backend_used") not in (None, "db_hybrid"):
            note.append("Arm A=Strategy L fallback発生(db_hybrid KEY_WORDS_STRUCTURE_INVALID)")
        if d["B"].get("stale_disk_items") is not None:
            note.append("Arm B canonicalization INVALID(Rule7)=最終KPなし(出力は採用せず)")
        if (d["A"].get("redundancy_attempts") or 0) > 0:
            note.append("A: Redundancy retry %s回" % d["A"]["redundancy_attempts"])
        if (d["B"].get("redundancy_attempts") or 0) > 0:
            note.append("B: Redundancy retry %s回" % d["B"]["redundancy_attempts"])
        for rk in range(1, 6):
            p = d["production"][rk - 1] if rk <= len(d["production"]) else {}
            a = next((r for r in d["A"]["rows"] if r["rank"] == rk), {}); b = next((r for r in d["B"]["rows"] if r["rank"] == rk), {})
            ws.append([uid, u["article_id"], u["level"], rk, p.get("key_phrase"), a.get("display_phrase"), a.get("key_phrase"), a.get("source_span"),
                       b.get("display_phrase"), b.get("key_phrase"), b.get("source_span"), d["A"]["status"] if rk == 1 else None, d["B"]["status"] if rk == 1 else None,
                       "; ".join(note) if rk == 1 else None])
    for col, w in zip("ABCDEFGHIJKLMN", [12, 6, 10, 6, 26, 26, 26, 24, 26, 26, 24, 26, 26, 50]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "E2"

    ws = wb.create_sheet("2_品質・遵守・語数")
    ws.append(["指標", "既存Production(実記録)", "Arm A(現行template)", "Arm B(+第3条)", "備考"]); hdr(ws, 1)
    pa, pb = S["paired_A"], S["paired_B"]
    ws.append(["全14単位 成功(最終KP5件)", "14/14", "%d/14 (%s)" % (S["A"]["sets_5"], S["A"]["status"]), "%d/14 (%s)" % (S["B"]["sets_5"], S["B"]["status"]),
               "BはB_Standard/D_StandardがCanonicalization INVALID(Rule7)で最終KPなし(Productionなら下流STOP/Human Review)"])
    ws.append(["全単位 平均語数(選定直後 display_phrase)", S["production"]["display_words"]["mean"], S["A"]["display_words"]["mean"], S["B"]["display_words"]["mean"], "Bは成功13単位(65件)の値"])
    ws.append(["全単位 平均語数(canonical後 key_phrase)", S["production"]["key_words"]["mean"], S["A"]["key_words"]["mean"], S["B"]["key_words"]["mean"], ""])
    ws.append(["ペア12単位(A,Bとも成功)平均語数 display_phrase", "-", pa["display_words"]["mean"], pb["display_words"]["mean"], "同一12単位x60件で比較"])
    ws.append(["ペア12単位 平均語数 key_phrase", "-", pa["key_words"]["mean"], pb["key_words"]["mean"], ""])
    ws.append(["ペア12単位 平均語数 本文span", "-", pa["span_words"]["mean"], pb["span_words"]["mean"], ""])
    ws.append(["ペア12単位 語数分布(display) 1/2/3/4/5語", "-", "/".join(str(pa["display_words"]["dist"][str(k)]) for k in range(1, 6)),
               "/".join(str(pb["display_words"]["dist"][str(k)]) for k in range(1, 6)), "4語の消失(4件->0件)がBの主な変化"])
    ws.append(["2語以下の割合(display、ペア12単位)", "-", pa["display_words"]["le2"], pb["display_words"]["le2"], ""])
    ws.append(["5語超(display/key)", "0/0", "%d/%d" % (S["A"]["over5_display"], S["A"]["over5_key"]), "%d/%d" % (S["B"]["over5_display"], S["B"]["over5_key"]), "5語上限は全件遵守"])
    ws.append(["本文spanが本文に不在(機械)", "-", S["A"]["span_not_in_text"], S["B"]["span_not_in_text"], "Production契約(候補ID復元)で構造的に0"])
    ws.append(["重複(canonical後)", "-", S["A"]["duplicates"], S["B"]["duplicates"], ""])
    ws.append(["Redundancy QA retry発火単位数", "-", S["A"]["retries"], S["B"]["retries"], "両armとも同数"])
    ws.append(["Strategy L fallback発生単位数", "-", S["A"]["fallback"], S["B"]["fallback"], "A: E_Standardでdb_hybrid selectorがKEY_WORDS_STRUCTURE_INVALID"])
    ws.append(["既存Production KPとの一致(本文span)", "-", "%d/70 (ペア12単位 %d/60)" % (S["A"]["match_prod_span"], pa["match_prod_span"]),
               "%d/65 (ペア12単位 %d/60)" % (S["B"]["match_prod_span"], pb["match_prod_span"]), "Arm Aは現行の再現(プロンプト同一)だがLLM非決定性により約6割一致"])
    ws.append(["Arm A vs Arm B 一致(本文span, ペア12単位60件)", "-", S["paired_AB_match_span"], "", "A-Prod一致(約60%)とA-B一致(75%)が同程度=差はLLM揺らぎの範囲"])
    ws.append(["role 内訳 important/topic", "-", "%d/%d" % (S["A"]["roles"]["important"], S["A"]["roles"]["topic"]), "%d/%d" % (S["B"]["roles"]["important"], S["B"]["roles"]["topic"]), ""])
    ws.append([]); ws.append(["例示追跡", "既存Production", "Arm A", "Arm B", ""]); hdr(ws, ws.max_row)
    for name, d in S["examples"].items():
        def f(hh):
            return " / ".join("%s:%s->%s" % (h["unit"], h["source_span"], h["key"]) for h in hh) or "該当なし"
        ws.append([name, f(d["production"]), f(d["A"]), f(d["B"]), ""])
    for col, w in zip("ABCDE", [46, 40, 40, 40, 60]):
        ws.column_dimensions[col].width = w

    ws = wb.create_sheet("3_評価詳細(Sonnet5.5)")
    ws.append(["kind", "unit", "arm", "rank", "phrase", "語数", "V", "E", "N", "C", "U", "S", "X", "note"]); hdr(ws, 1)
    for r in sorted(ev["rows"], key=lambda r: (r["kind"], r["unit"], r["arm"], r["rank"])):
        ws.append([r["kind"], r["unit"], r["arm"], r["rank"], r["phrase"], r["words"], r["V"], r["E"], r["N"], r["C"], r["U"], r["S"], r["X"], r["note"]])
    ws.append([]); ws.append(["集計(平均、各60件)", "", "", "", "", "", "V", "E", "N", "C", "U", "S", "X", "padding sets(/12)"]); hdr(ws, ws.max_row)
    for kind, lab in (("span", "本文span(TRIAL-02 Trial1と同形)"), ("final", "canonical後key_phrase(最終)")):
        for arm in "AB":
            m = ev["summary"][kind][arm]
            ws.append([lab, "", "Arm " + arm, "", "", "", m["V"], m["E"], m["N"], m["C"], m["U"], m["S"], m["X"], m["padding_sets"]])
    ws.column_dimensions["E"].width = 36

    ws = wb.create_sheet("4_費用・条件")
    ws.append(["項目", "値"]); hdr(ws, 1)
    for k, v in cost.items():
        ws.append([k, v if not isinstance(v, (dict, list)) else json.dumps(v, ensure_ascii=False)])
    ws.append([]); ws.append(["Prompt Before(現行template: er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt)", ""]); hdr(ws, ws.max_row)
    ws.append(["template_A_current.txt 全文", (OUT / "inputs/template_A_current.txt").read_text(encoding="utf-8")])
    ws.append(["Prompt After(Arm B = 同 + 第3条を『display_phraseは1〜5語…』段落の直後へ挿入)", ""]); hdr(ws, ws.max_row)
    ws.append(["template_B_plus_clause3.txt 全文", (OUT / "inputs/template_B_plus_clause3.txt").read_text(encoding="utf-8")])
    ws.append(["Promptパリティ(Arm A選定Prompt vs 既存Production keywords_selector_prompt.txt、Arm B vs A差分行)", json.dumps(par, ensure_ascii=False)[:30000]])
    for r in ws.iter_rows(min_row=2):
        for c in r:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 52; ws.column_dimensions["B"].width = 120
    DST.parent.mkdir(parents=True, exist_ok=True); wb.save(DST); print("saved", DST)


if __name__ == "__main__":
    sys.exit(main())
