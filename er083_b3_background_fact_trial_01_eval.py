# -*- coding: utf-8 -*-
"""er083_b3_background_fact_trial_01_eval.py
候補横断の比較表(機械抽出のみ)と、Sonnet盲検評価用のblind pack作成。内容の善し悪し(rubric 5軸)の判定はここでは行わない。

  python er083_b3_background_fact_trial_01_eval.py --out-root <dir> [--article middle_east_yemen_saudi] [--dry-run]
      -> <out-root>/[_dryrun/]comparison.md / comparison.json / spec_generalization_check.json
  python er083_b3_background_fact_trial_01_eval.py --out-root <dir> --blind-pack
      -> blind_pack.md(候補名を伏せ、A/B/...へ並べ替えた記事テキスト+選定Fact)と blind_key.json(対応表。評価者には渡さない)

行(候補): Baseline(現行Production run_mey_01、読取のみ。Baseline再走sampleがあれば baseline_rerun として追加)、C1、C2、C3(あれば)。
列: 採用ID / 不採用ID / 追加Fact(+必要性=reason先頭【背景補完】) / 【背景確認】note / 下限2件充足 / Storyline / Baseline差分 / 固有事例混入チェック。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import er083_b3_background_fact_trial_01_lib as lib


def _load_cand(cand_dir: str, label: str) -> dict | None:
    mp = os.path.join(cand_dir, "trial_meta.json")
    if not os.path.isfile(mp):
        return None
    meta = json.loads(lib.read_text(mp))
    ja = os.path.join(cand_dir, "ja_writer", "revision2.md")
    meta["_label"] = label
    meta["_ja_path"] = ja if os.path.isfile(ja) else None
    return meta


def _load_production_baseline() -> dict:
    ev = json.loads(lib.read_text(os.path.join(lib.PRODUCTION_MEY_RUN, "storyline_b3", "fact_selection_evidence.json")))
    ledger = lib.read_text(os.path.join(lib.PRODUCTION_MEY_RUN, "research_ledger", "verified_fact_ledger.txt"))
    parsed = {"selected_storyline": ev["selected_storyline"], "fact_tests": ev["fact_tests"],
              "selected_fact_ids": ev["selected_fact_ids"], "recheck_note": ev.get("recheck_note")}
    ja = os.path.join(lib.PRODUCTION_MEY_RUN, "ja_writer", "revision2.md")
    return {"_label": "baseline(現行Production run_mey_01)", "candidate": "baseline", "status": "OK(Production既存run・読取のみ)",
            "analysis": lib.analyze_selection(parsed, ledger, ev["selected_fact_ids"]),
            "fact_reasons": {ft["fact_id"]: ft["reason"] for ft in ev["fact_tests"]},
            "_ja_path": ja if os.path.isfile(ja) else None}


def collect(out_root: str, article: str, dry_run: bool) -> list:
    base = os.path.join(out_root, "_dryrun" if dry_run else "", article)
    rows = [_load_production_baseline()]
    for cand, label in (("baseline", "baseline_rerun(同Prompt再走sample)"), ("C1", "C1"), ("C2", "C2"), ("C3", "C3")):
        m = _load_cand(os.path.join(base, cand), label)
        if m is None:
            continue
        if cand == "baseline":
            m["_label"] = label
        ev_path = os.path.join(base, cand, "storyline_b3", "fact_selection_evidence.json")
        if os.path.isfile(ev_path):
            ev = json.loads(lib.read_text(ev_path))
            m["fact_reasons"] = {ft["fact_id"]: ft["reason"] for ft in ev["fact_tests"]}
        rows.append(m)
    return rows


def render_md(rows: list, gen: dict) -> str:
    out = ["# 候補横断比較表(機械抽出。rubric判定はSonnet盲検評価)", ""]
    out.append("| 候補 | status | 採用ID | 追加Fact(補完マーカー付き) | Baseline差分(追加/除去) | 下限2件(VERIFIED採用数) | 【背景確認】note |")
    out.append("|---|---|---|---|---|---|---|")
    for r in rows:
        a = r.get("analysis") or {}
        out.append("| {l} | {st} | {sel} | {sup} | +{add} / -{rem} | {ok}({n}) | {note} |".format(
            l=r["_label"], st=r.get("status"), sel=",".join(a.get("selected_fact_ids") or []) or "-",
            sup=",".join(a.get("supplement_fact_ids") or []) or "なし", add=",".join(a.get("added_vs_baseline") or []) or "-",
            rem=",".join(a.get("removed_vs_baseline") or []) or "-", ok="OK" if a.get("min2_satisfied") else "NG",
            n=a.get("verified_selected_n"), note=(a.get("background_confirm_note") or "(なし)").replace("|", "/").replace("\n", " ")))
    out += ["", "## Storyline", ""]
    for r in rows:
        out.append(f"- **{r['_label']}**: {(r.get('analysis') or {}).get('selected_storyline')}")
    out += ["", "## 追加Factと必要性(reason原文)", ""]
    for r in rows:
        a = r.get("analysis") or {}
        for fid, reason in (a.get("supplement_reasons") or {}).items():
            out.append(f"- {r['_label']} / {fid}: {reason}")
    out += ["", "## 全Factのreason(不採用理由を含む。盲検評価の根拠資料)", ""]
    for r in rows:
        fr = r.get("fact_reasons") or {}
        if not fr:
            continue
        sel = set((r.get("analysis") or {}).get("selected_fact_ids") or [])
        out.append(f"### {r['_label']}")
        for fid in sorted(fr):
            out.append(f"- {fid} [{'採用' if fid in sel else '不採用'}]: {fr[fid]}")
        out.append("")
    out += ["## 仕様文の固有事例混入チェック(機械確認。空=混入なし)", "", "```", json.dumps(gen, ensure_ascii=False, indent=1), "```", ""]
    return "\n".join(out)


def blind_pack(rows: list, out_dir: str) -> dict:
    """記事テキスト(ja_writer/revision2.md)がある行だけを、ラベルをハッシュ順で A,B,C.. に並べ替えて出力。"""
    cand = [r for r in rows if r.get("_ja_path")]
    cand.sort(key=lambda r: hashlib.sha256((r["_label"] + "blind-v1").encode("utf-8")).hexdigest())
    names = [chr(ord("A") + i) for i in range(len(cand))]
    key = {n: r["_label"] for n, r in zip(names, cand)}
    lines = ["# 盲検比較パック(候補名は伏せてあります)", ""]
    for n, r in zip(names, cand):
        a = r.get("analysis") or {}
        lines += [f"## 記事{n}", "", f"採用Fact: {','.join(a.get('selected_fact_ids') or [])}", "",
                  "### 記事テキスト", "", lib.read_text(r["_ja_path"]).strip(), ""]
    lib.write_text(os.path.join(out_dir, "blind_pack.md"), "\n".join(lines))
    lib.write_json(os.path.join(out_dir, "blind_key.json"), key)
    return key


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", default=lib.OUT_ROOT)
    ap.add_argument("--article", default=lib.DEFAULT_ARTICLE)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--blind-pack", action="store_true")
    a = ap.parse_args(argv)
    out_root = os.path.abspath(a.out_root)
    out_dir = os.path.join(out_root, "_dryrun" if a.dry_run else "")
    rows = collect(out_root, a.article, a.dry_run)
    gen = lib.generalization_report()
    lib.write_json(os.path.join(out_dir, "spec_generalization_check.json"), gen)
    lib.write_text(os.path.join(out_dir, "comparison.md"), render_md(rows, gen))
    lib.write_json(os.path.join(out_dir, "comparison.json"), [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows])
    if a.blind_pack:
        print("blind key written:", blind_pack(rows, out_dir).keys())
    print(f"rows={len(rows)} generalization_hits={ {k: v for k, v in gen.items() if v} or 'none' }")
    return 0 if not any(gen.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
