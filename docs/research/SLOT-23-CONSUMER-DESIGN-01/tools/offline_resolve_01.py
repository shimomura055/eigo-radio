"""SLOT-23 委任_04A: 既存の確定済みX/Y/Z runの全件で、ハイライト解決器をオフライン実行する(API 0・read-only。出力は --out のみ)。

使い方: py -3 docs/research/SLOT-23-CONSUMER-DESIGN-01/tools/offline_resolve_01.py [--out <json>] [--md <md>]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
import er_learning_highlight_01 as hl   # noqa: E402


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def rt(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


# ---- Family別アダプタ(本文・表示単位の取得。配線班が同型を実装する) ----
def x_units(run_dir, lv):
    p = rj(os.path.join(run_dir, lv, "parts.json"))
    return [{"key": f"full_story_part{i}", "texts": [p[f"part{i}"]], "joiner": " "} for i in (1, 2, 3)]


def x_article(run_dir, lv):
    src = rj(os.path.join(run_dir, "entry_point.json"))["source_dir"]
    return rt(os.path.join(ROOT, src, lv, "article.md"))


def y_units(run_dir, lv):
    p = rj(os.path.join(run_dir, lv, "parts.json"))
    return [{"key": sid, "texts": [p["segments"][sid]], "joiner": " "} for sid in p["y_segment_order"] if sid in p["segments"]]


def y_article(run_dir, lv):
    import er121_family_y_structure_01 as ys
    return ys.canonical_body(rt(os.path.join(run_dir, "translate", f"{lv}.md")))


def z_units(run_dir, lv):
    plan = rj(os.path.join(run_dir, f"segment_plan_{lv}.json"))
    groups = {}
    for c in plan["clips"]:
        groups.setdefault(c["part"], []).append(c["text"])
    return [{"key": f"full_story_part{n}", "texts": t, "joiner": " "} for n, t in sorted(groups.items())]


def z_article(run_dir, lv):
    import er062_family_z_structure_01 as st
    _t, body = st.split_title_body(rt(os.path.join(run_dir, "writer", "r2.md" if lv == "b1b" else "std.md")))
    return "\n\n".join(st.clean_body_paragraphs(body))


def resolve_run(family, run_dir, lv, kp_dir, article, units):
    rec = rj(os.path.join(kp_dir, "confirmed_selection.json"))
    cands = rj(os.path.join(kp_dir, "kp_candidates.json"))
    items = hl.items_from_record(rec)
    res = hl.resolve_highlights(article, cands, items, units)
    return rec, res


def enumerate_runs():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "er*_output", "**", "key_phrases", "**", "confirmed_selection.json"), recursive=True)):
        p = p.replace("\\", "/")
        if "/audit/" in p:
            continue
        kp_dir = os.path.dirname(p)
        rel = p.split("/key_phrases/")[0]
        tail = p.split("/key_phrases/")[1]
        rec = rj(p)
        lv = rec["article"]["level"]
        fam = rec["article"]["family"]
        if os.path.basename(rel) == lv and fam == "x":   # X: key_phrases は <run>/<lv>/key_phrases/
            rel = os.path.dirname(rel)
        out.append({"family": fam, "level": lv, "run_dir": rel, "kp_dir": kp_dir})
    return out


def write_md(rows, path):
    L = ["# OFFLINE_RESOLVE_01 既存確定済みX/Y/Z run全件のハイライト解決(API 0、read-only)", "",
         "生成: `py -3 docs/research/SLOT-23-CONSUMER-DESIGN-01/tools/offline_resolve_01.py --md <本ファイル>`(JSON=`OFFLINE_RESOLVE_01.json`)。",
         "表示範囲=Full Story本文(X=parts.json part1-3 / Y=parts.json segments全件 / Z=segment_plan clips(Part別))。", "",
         "| Family | level | run | 判定 | 項目数 | 装飾 | ③訳 | NOTICE | ISSUE |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['family'].upper()} | {r['level']} | {r['run'].split('/')[-1]} | {r['status']} | {r.get('items','-')} | {r.get('decorated','-')} | {r.get('meanings','-')} | "
                 f"{', '.join(n['code']+':'+n['candidate_id'] for n in r.get('notices', [])) or '0'} | {', '.join(n['code']+':'+str(n['candidate_id']) for n in r.get('issues', [])) or '0'} |")
    L += ["", f"合計: {len(rows)} run-level、ISSUE={sum(len(r.get('issues', [])) for r in rows)}件、TOOL_ERROR={sum(1 for r in rows if r['status']=='TOOL_ERROR')}。", ""]
    for r in rows:
        if r["status"] == "TOOL_ERROR":
            L.append(f"- TOOL_ERROR {r['run']} {r['level']}: {r['error']}")
        for n in r.get("issues", []):
            L.append(f"- ISSUE {r['family'].upper()}/{r['level']}/{r['run'].split('/')[-1]}: `{n['code']}` {n['candidate_id']}: {n['detail']}")
        if r.get("variant_with_in_one_line"):
            L.append(f"  - 変種(表示範囲に In one line を加える): {r['variant_with_in_one_line']['status']}、NOTICE={[n['code'] for n in r['variant_with_in_one_line']['notices']]}")
    L += ["", "## AI島(`ai_island_temple__run_form_prod_01`)の全項目", ""]
    for r in rows:
        if "ai_island" in r["run"]:
            L += [f"### {r['level']}", "| 区分 | 本文表層形 | used_form | 文 | 単位 | 再配置 | 装飾 |", "|---|---|---|---|---|---|---|"]
            for h in r["highlights"]:
                L.append(f"| {h['kind']} | {h['surface']} | {h['used_form']} | {h['sentence_id']} | {h['unit']} | {h['relocated_from'] or '-'} | {h['decorate']} |")
            L.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write(chr(10).join(L) + chr(10))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs/research/SLOT-23-CONSUMER-DESIGN-01/OFFLINE_RESOLVE_01.json"))
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    rows = []
    for r in enumerate_runs():
        fam, lv, run_dir = r["family"], r["level"], r["run_dir"]
        row = {"family": fam, "level": lv, "run": os.path.relpath(run_dir, ROOT).replace("\\", "/")}
        try:
            if fam == "x":
                art, units = x_article(run_dir, lv), x_units(run_dir, lv)
            elif fam == "y":
                art, units = y_article(run_dir, lv), y_units(run_dir, lv)
            else:
                art, units = z_article(run_dir, lv), z_units(run_dir, lv)
            rec, res = resolve_run(fam, run_dir, lv, r["kp_dir"], art, units)
        except Exception as e:   # noqa: BLE001
            row.update(status="TOOL_ERROR", error=f"{type(e).__name__}: {e}")
            rows.append(row)
            continue
        row.update(status=res["status"], items=len(res["highlights"]) + len([i for i in res["issues"]]),
                   decorated=res["stats"]["decorated"], notices=res["notices"], issues=res["issues"],
                   highlights=[{k: h[k] for k in ("candidate_id", "kind", "used_form", "surface", "sentence_id", "relocated_from", "decorate")} | {"unit": h["pieces"][0]["unit_key"], "pieces": len(h["pieces"])} for h in res["highlights"]],
                   meanings=len(res["meanings"]))
        if res["status"] == "ISSUE" and fam == "x":
            # 変種: 表示範囲に「In one line」(Script表に出る別行)を加えた場合に解消するか(配線班への判断材料。既定の表示範囲=Full Storyは変えない)
            p3 = rj(os.path.join(run_dir, lv, "parts.json"))
            units2 = units + [{"key": "in_one_line", "texts": [p3["in_one_line"]], "joiner": " "}]
            _r2, res2 = resolve_run(fam, run_dir, lv, r["kp_dir"], art, units2)
            row["variant_with_in_one_line"] = {"status": res2["status"], "issues": res2["issues"], "notices": res2["notices"]}
        rows.append(row)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    if a.md:
        write_md(rows, a.md)
    for r in rows:
        print(r["family"], r["level"], r["run"].split("/")[-1], r["status"], "dec=", r.get("decorated"), "N=", len(r.get("notices", [])), "I=", len(r.get("issues", [])), r.get("error", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
