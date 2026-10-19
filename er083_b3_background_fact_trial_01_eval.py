# -*- coding: utf-8 -*-
"""er083_b3_background_fact_trial_01_eval.py
候補横断の比較表(機械抽出のみ)と、盲検評価用のblind pack作成、費用集計。内容の善し悪し(rubric 5軸)の判定はここでは行わない。

  python er083_b3_background_fact_trial_01_eval.py --out-root <dir> [--article middle_east_yemen_saudi] [--dry-run]
      [--out <comparison.md>] [--blind-pack <blind_pack.md>]
      -> comparison.md / comparison.json / spec_generalization_check.json / (blind_pack.md + 同dirの blind_key.json)
  python er083_b3_background_fact_trial_01_eval.py --out-root <dir> --cost-summary
      -> out-root配下の全 cost_log*.jsonl(run単位)の実費合計(M1: theme絞込なし、実API行を全て数える)

行(候補): Baseline(現行Production run_mey_01、読取のみ)、baseline_rerun/s<N>、C1/s<N>、C2/s<N>、C3/s<N>(M5: 複数sample)。
列: 採用ID / core(補完除く) / 追加Fact(+必要性) / 【背景確認】note / 下限2件 / 補完のみで下限充足(M2) / Storyline / Baseline差分 / 中核数値差分。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

import er083_b3_background_fact_trial_01_lib as lib


def _core_numbers(stage_dir: str) -> list | None:
    """producer出力 annotation.json の中核数値(class=core)のsurface集合(sorted)。無ければNone(M5: sidecar機械差分、0円)。"""
    ap = os.path.join(stage_dir, "annotation.json")
    if not os.path.isfile(ap):
        return None
    ann = json.loads(lib.read_text(ap))
    return sorted({n["surface"] for n in ann.get("numbers", []) if n.get("class") == "core"})


def _load_cand(cand_dir: str, label: str, cand: str, sample: int) -> dict | None:
    mp = os.path.join(cand_dir, "trial_meta.json")
    if not os.path.isfile(mp):
        return None
    meta = json.loads(lib.read_text(mp))
    ja = os.path.join(cand_dir, "ja_writer", "revision2.md")
    meta["_label"], meta["_cand"], meta["_sample"], meta["_dir"] = label, cand, sample, cand_dir
    meta["_ja_path"] = ja if os.path.isfile(ja) else None
    meta["core_numbers"] = _core_numbers(os.path.join(cand_dir, "storyline_b3"))
    return meta


def _load_production_baseline() -> dict:
    ev = json.loads(lib.read_text(os.path.join(lib.PRODUCTION_MEY_RUN, "storyline_b3", "fact_selection_evidence.json")))
    ledger = lib.read_text(os.path.join(lib.PRODUCTION_MEY_RUN, "research_ledger", "verified_fact_ledger.txt"))
    parsed = {"selected_storyline": ev["selected_storyline"], "fact_tests": ev["fact_tests"],
              "selected_fact_ids": ev["selected_fact_ids"], "recheck_note": ev.get("recheck_note")}
    ja = os.path.join(lib.PRODUCTION_MEY_RUN, "ja_writer", "revision2.md")
    return {"_label": "baseline(現行Production run_mey_01)", "_cand": "baseline", "_sample": 0, "candidate": "baseline",
            "status": "OK(Production既存run・読取のみ)",
            "analysis": lib.analyze_selection(parsed, ledger, ev["selected_fact_ids"]),
            "fact_reasons": {ft["fact_id"]: ft["reason"] for ft in ev["fact_tests"]},
            "core_numbers": _core_numbers(os.path.join(lib.PRODUCTION_MEY_RUN, "storyline_b3")),
            "_ja_path": ja if os.path.isfile(ja) else None}


def _sample_dirs(cand_root: str) -> list:
    if not os.path.isdir(cand_root):
        return []
    out = []
    for d in os.listdir(cand_root):
        m = re.fullmatch(r"s([0-9]+)", d)
        if m and os.path.isdir(os.path.join(cand_root, d)):
            out.append((int(m.group(1)), os.path.join(cand_root, d)))
    return sorted(out)


def collect(out_root: str, article: str, dry_run: bool) -> list:
    """Production baseline(読取のみ) + <article>/<candidate>/s<N> を全て(M5: 複数sample)。"""
    base = os.path.join(out_root, "_dryrun" if dry_run else "", article)
    rows = [_load_production_baseline()]
    for cand in lib.CANDIDATE_NAMES:
        for n, d in _sample_dirs(os.path.join(base, cand)):
            label = f"baseline_rerun/s{n}" if cand == "baseline" else f"{cand}/s{n}"
            m = _load_cand(d, label, cand, n)
            if m is None:
                continue
            ev_path = os.path.join(d, "storyline_b3", "fact_selection_evidence.json")
            if os.path.isfile(ev_path):
                ev = json.loads(lib.read_text(ev_path))
                m["fact_reasons"] = {ft["fact_id"]: ft["reason"] for ft in ev["fact_tests"]}
            rows.append(m)
    return rows


def _sel(r: dict) -> tuple:
    return tuple(sorted((r.get("analysis") or {}).get("selected_fact_ids") or []))


def _sig(r: dict) -> tuple:
    a = r.get("analysis") or {}
    return (tuple(sorted(a.get("core_selected_ids") or [])), tuple(sorted(a.get("supplement_fact_ids") or [])))


def sample_consistency(rows: list) -> dict:
    """M5の事前固定判定規則: 補完挙動とcore_selected_idsが同候補の全sampleで一貫し、かつBaseline(Production+再走)の観測範囲外
    (候補の採用ID集合がBaselineで観測された採用ID集合のいずれとも一致しない)の場合に限り「補助指示の効果」とみなす。n=1は判定不能。"""
    base_rows = [r for r in rows if r.get("_cand") == "baseline" and r.get("analysis")]
    base_observed = sorted({_sel(r) for r in base_rows})
    out = {"baseline_observed_selected_sets": [list(t) for t in base_observed],
           "baseline_n_samples_incl_production": len(base_rows),
           "baseline_core_selected_sets": [list(t) for t in sorted({_sig(r)[0] for r in base_rows})]}
    for cand in lib.CANDIDATE_NAMES:
        rs = [r for r in rows if r.get("_cand") == cand and r.get("_sample", 0) >= 1 and r.get("analysis")]
        if not rs:
            continue
        sigs = {_sig(r) for r in rs}
        consistent = len(sigs) == 1
        outside = all(_sel(r) not in base_observed for r in rs)
        if cand == "baseline":
            judgement = "Baseline自身の揺れの観測(再走)"
        elif len(rs) < 2:
            judgement = "n=1: 補助指示の効果は判定不能"
        elif consistent and outside:
            judgement = "補助指示の効果とみなす(一貫∧Baseline観測範囲外)"
        else:
            judgement = "補助指示の効果とはみなさない(不一貫またはBaseline観測範囲内)"
        out[cand] = {"n_samples": len(rs), "signatures": [{"core": list(c), "supplement": list(s_)} for c, s_ in sorted(sigs)],
                     "consistent": consistent, "outside_baseline_observed_range": outside,
                     "any_supplement": any(_sig(r)[1] for r in rs),
                     "min2_met_only_via_supplement_any": any(bool((r["analysis"] or {}).get("min2_met_only_via_supplement")) for r in rs),
                     "judgement": judgement}
    return out


def core_number_diffs(rows: list) -> list:
    """sidecar中核数値集合の、Production baselineとの差分(各行)。"""
    base = next((r for r in rows if r.get("_sample") == 0 and r.get("core_numbers") is not None), None)
    bset = set(base["core_numbers"]) if base else set()
    out = []
    for r in rows:
        if r.get("core_numbers") is None or r is base:
            continue
        cs = set(r["core_numbers"])
        out.append({"label": r["_label"], "core_numbers": sorted(cs), "added_vs_production_baseline": sorted(cs - bset),
                    "removed_vs_production_baseline": sorted(bset - cs)})
    return out


def render_md(rows: list, gen: dict) -> str:
    out = ["# 候補横断比較表(機械抽出。rubric判定は盲検評価)", ""]
    out.append("| 候補 | status | 採用ID | core(補完除く) | 追加Fact(補完マーカー付き) | Baseline差分(追加/除去) | 下限2件(VERIFIED採用数/core) | 補完のみで下限充足 | 最終call | 【背景確認】note |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        a = r.get("analysis") or {}
        out.append("| {l} | {st} | {sel} | {core} | {sup} | +{add} / -{rem} | {ok}({n}/{cn}) | {only} | {fc} | {note} |".format(
            l=r["_label"], st=r.get("status"), sel=",".join(a.get("selected_fact_ids") or []) or "-",
            core=",".join(a.get("core_selected_ids") or []) or "-",
            sup=",".join(a.get("supplement_fact_ids") or []) or "なし", add=",".join(a.get("added_vs_baseline") or []) or "-",
            rem=",".join(a.get("removed_vs_baseline") or []) or "-", ok="OK" if a.get("min2_satisfied") else "NG",
            n=a.get("verified_selected_n"), cn=a.get("core_verified_n"),
            only="**YES(問題)**" if a.get("min2_met_only_via_supplement") else "no", fc=r.get("final_result_call", "-"),
            note=(a.get("background_confirm_note") or "(なし)").replace("|", "/").replace("\n", " ")))
    out += ["", "## Storyline", ""]
    for r in rows:
        out.append(f"- **{r['_label']}**: {(r.get('analysis') or {}).get('selected_storyline')}")
    out += ["", "## 追加Factと必要性(reason原文)", ""]
    for r in rows:
        a = r.get("analysis") or {}
        for fid, reason in (a.get("supplement_reasons") or {}).items():
            out.append(f"- {r['_label']} / {fid}: {reason}")
    out += ["", "## sample一貫性(M5の事前固定規則)", "", "```", json.dumps(sample_consistency(rows), ensure_ascii=False, indent=1), "```", ""]
    out += ["## sidecar中核数値集合の差分(vs Production baseline、機械)", "", "```",
            json.dumps(core_number_diffs(rows), ensure_ascii=False, indent=1), "```", ""]
    out += ["## 全Factのreason(不採用理由を含む。盲検評価の根拠資料)", ""]
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


def _fact_summaries() -> dict:
    """Ledger本文からFact ID -> 内容要約(先頭40字)。盲検パックでID行を内容へ置換するため(M3)。"""
    txt = lib.read_text(os.path.join(lib.PRODUCTION_MEY_RUN, "research_ledger", "verified_fact_ledger.txt"))
    out = {}
    for m in re.finditer(r"^\[[A-Z]+\]\s+(F[0-9]{2}):\s*(.+)$", txt, re.M):
        out[m.group(1)] = m.group(2).strip()[:40]
    return out


def _mask_ids(text: str, summ: dict) -> str:
    return re.sub(r"(?<![A-Za-z0-9])(F[0-9]{2})(?![0-9])", lambda m: f"〈{summ.get(m.group(1), 'Fact')}…〉", text or "")


def blind_pack(rows: list, out_dir: str, pack_path: str | None = None, with_text_only: bool = False) -> dict:
    """候補名・sample名・Fact IDを伏せたパック(M3)。B3選定レベルは全行、記事テキストはある行のみ(with_text_only=Trueなら記事がある行だけ)。
    ラベルをハッシュ順でA,B,C..に並べ替え、対応表は blind_key.json(評価者には評価後の照合まで渡さない)。"""
    cand = [r for r in rows if r.get("analysis") and (r.get("_ja_path") or not with_text_only)]
    cand.sort(key=lambda r: hashlib.sha256((r["_label"] + "blind-v2").encode("utf-8")).hexdigest())
    names = [chr(ord("A") + i) for i in range(len(cand))]
    key = {n: r["_label"] for n, r in zip(names, cand)}
    summ = _fact_summaries()
    lines = ["# 盲検比較パック(候補名・sample名・Fact IDは伏せてあります。Fact IDは内容要約〈…〉に置換)", "",
             "注: 【背景補完】【背景確認】は評価対象の記録なので残してあります。", ""]
    for n, r in zip(names, cand):
        a = r.get("analysis") or {}
        sel = a.get("selected_fact_ids") or []
        lines += [f"## 選定{n}", "", f"- Storyline: {a.get('selected_storyline')}", f"- 採用Fact数: {len(sel)}", "- 採用Factの内容要約:"]
        for fid in sel:
            tag = "【補完】" if fid in (a.get("supplement_fact_ids") or []) else ""
            lines.append(f"  - {tag}{summ.get(fid, 'Fact')}…")
        if a.get("supplement_reasons"):
            lines.append("- 補完の理由(原文、ID置換済み):")
            for fid, reason in a["supplement_reasons"].items():
                lines.append(f"  - 〈{summ.get(fid, 'Fact')}…〉: {_mask_ids(reason, summ)}")
        lines += [f"- 背景確認note: {_mask_ids(a.get('background_confirm_note') or '(なし)', summ)}", ""]
        fr = r.get("fact_reasons") or {}
        if fr:
            lines.append("- 不採用Factの理由(ID置換済み):")
            for fid in sorted(fr):
                if fid not in sel:
                    lines.append(f"  - 〈{summ.get(fid, 'Fact')}…〉: {_mask_ids(fr[fid], summ)}")
            lines.append("")
        if r.get("_ja_path"):
            lines += ["### 記事テキスト", "", lib.read_text(r["_ja_path"]).strip(), ""]
    lib.write_text(pack_path or os.path.join(out_dir, "blind_pack.md"), "\n".join(lines))
    lib.write_json(os.path.join(out_dir, "blind_key.json"), key)   # 対応表はTrial出力dir側(評価者パックとは別置き)
    return key


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", default=lib.OUT_ROOT)
    ap.add_argument("--article", default=lib.DEFAULT_ARTICLE)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=None, help="comparison.md の出力先(省略時 out-root配下)")
    ap.add_argument("--blind-pack", nargs="?", const="", default=None, help="盲検パックmdの出力先(省略値=out-root配下)")
    ap.add_argument("--cost-summary", action="store_true")
    a = ap.parse_args(argv)
    out_root = os.path.abspath(a.out_root)
    if a.cost_summary:
        print(json.dumps(lib.cost_summary_tree(out_root), ensure_ascii=False, indent=1))
        return 0
    out_dir = os.path.join(out_root, "_dryrun" if a.dry_run else "")
    rows = collect(out_root, a.article, a.dry_run)
    gen = lib.generalization_report()
    lib.write_json(os.path.join(out_dir, "spec_generalization_check.json"), gen)
    lib.write_text(a.out or os.path.join(out_dir, "comparison.md"), render_md(rows, gen))
    lib.write_json(os.path.join(out_dir, "comparison.json"), [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows])
    if a.blind_pack is not None:
        print("blind key written:", list(blind_pack(rows, out_dir, a.blind_pack or None).keys()))
    print(f"rows={len(rows)} generalization_hits={ {k: v for k, v in gen.items() if v} or 'none' }")
    return 0 if not any(gen.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
