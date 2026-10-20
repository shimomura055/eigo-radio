# -*- coding: utf-8 -*-
"""FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 eval(機械採点。API 0)。

入力: <out>/<topic>/s<N>/<variant>/{draft.json, verified_fact_ledger.txt, summary.json}
採点規則: gold_02.json(gold_01の1項目を①実走後・候補実走前に訂正、docs参照)。item_retained=rendered Ledgerの単一Factブロックが全groupsに一致。
創作: 機械フラグ→adjudication_01.json(SUPPORTED(quote)/UNSUPPORTED)で確定。未判定は最終ラベルを出さない。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import statistics
import sys

import er085_research_fact_retention_trial_01_lib as lib


def load_gold(path: str | None = None) -> dict:
    return lib.read_json(path or os.path.join(lib.DOC_DIR, "gold_02.json"))


def eval_cell(cell_variant_dir: str, topic: str, gold: dict, adjud: dict, variant: str, sample: int) -> dict:
    items = gold["topics"][topic]["items"]
    watch = gold["topics"][topic]["watch"]
    draft = lib.read_json(os.path.join(cell_variant_dir, "draft.json"))
    ledger_text = lib.read_text(os.path.join(cell_variant_dir, "verified_fact_ledger.txt"))
    summ = lib.read_json(os.path.join(cell_variant_dir, "summary.json"))
    blocks = lib.split_blocks(ledger_text)
    m_ledger = lib.match_gold(items, [b["text"] for b in blocks])
    m_draft = lib.match_gold(items, [lib.fact_text(f) for f in draft["facts"]])
    per_item = {}
    for it in items:
        lr = m_ledger[it["id"]] is not None
        dr = m_draft[it["id"]] is not None
        per_item[it["id"]] = {"tier": it["tier"], "ledger": lr, "draft": dr,
                              "diag": "retained" if lr else ("lost_after_draft(検証/Ledger化で脱落)" if dr else "absent_in_draft(抽出で脱落)"),
                              "ledger_fact_id": blocks[m_ledger[it["id"]]]["fact_id"] if lr else None}
    flags = lib.fabrication_flags(blocks, watch)
    for fl in flags:
        key = f"{variant}|{topic}|s{sample}|{fl['fact_id']}"
        a = adjud.get(key)
        fl["adjudication"] = a["verdict"] if a else "UNADJUDICATED"
    flagged_ids = {fl["fact_id"] for fl in flags}
    prefix = f"{variant}|{topic}|s{sample}|"
    manual = sorted(k.split("|")[3] for k, v in adjud.items()
                    if k.startswith(prefix) and v.get("verdict") == "UNSUPPORTED" and k.split("|")[3] not in flagged_ids)
    return {
        "manual_unsupported": manual,
        "variant": variant, "topic": topic, "sample": sample, "per_item": per_item, "n_facts_draft": len(draft["facts"]),
        "n_blocks_ledger": len(blocks), "verdict_counts": summ["verdict_counts"], "schema_errors": summ["schema_errors"],
        "b3_ids_extractable": len(blocks) > 0 and all(b["fact_id"] for b in blocks), "flags": flags,
        "cost_jpy": summ["cost_jpy"], "n_llm_calls": summ["n_llm_calls"], "web_search_calls": summ["web_search_calls"],
        "latency_seconds": summ["latency_seconds"], "input_tokens": summ["input_tokens"], "output_tokens": summ["output_tokens"],
    }


def rate(cells: list, tier: str, which: str = "ledger") -> float | None:
    num = den = 0
    for c in cells:
        for r in c["per_item"].values():
            if r["tier"] == tier:
                den += 1
                num += 1 if r[which] else 0
    return round(num / den, 3) if den else None


def aggregate(cells: list) -> dict:
    by = {}
    for c in cells:
        by.setdefault((c["variant"], c["topic"]), []).append(c)
    base = {t: statistics.mean(x["n_facts_draft"] for x in v) for (var, t), v in by.items() if var == "E0"}
    out = {}
    for (var, t), v in sorted(by.items()):
        unadj = sum(1 for c in v for f in c["flags"] if f["adjudication"] == "UNADJUDICATED")
        unsup = sum(1 for c in v for f in c["flags"] if f["adjudication"] == "UNSUPPORTED") + sum(len(c.get("manual_unsupported", [])) for c in v)
        mean_facts = statistics.mean(x["n_facts_draft"] for x in v)
        out[f"{var}|{t}"] = {
            "n_samples": len(v),
            "key_ledger": rate(v, "KEY"), "key_draft": rate(v, "KEY", "draft"),
            "sec_ledger": rate(v, "SEC"), "ctrl_ledger": rate(v, "CTRL"),
            "mean_facts": round(mean_facts, 2), "delta_facts_vs_E0": round(mean_facts - base[t], 2) if t in base else None,
            "flags_total": sum(len(c["flags"]) for c in v), "flags_unadjudicated": unadj, "fabrication_unsupported": unsup,
            "mean_cost_jpy": round(statistics.mean(x["cost_jpy"] for x in v), 3), "mean_llm_calls": statistics.mean(x["n_llm_calls"] for x in v),
            "mean_latency_s": round(statistics.mean(x["latency_seconds"] for x in v), 1), "web_search_calls": sum(x["web_search_calls"] for x in v),
            "schema_errors": sum(len(x["schema_errors"]) for x in v),
        }
    return out


# ---------------------------------------------------------------------------
# 判定機械(設計v02 §9-1、事前登録。実走前commit)。最終ラベルはFable。
# ---------------------------------------------------------------------------
TOL = 1e-6


def classify_variant(variant: str, per_topic: dict, base: dict) -> dict:
    """per_topic/base: {topic: {key_ledger, ctrl_ledger, delta_facts_vs_E0, fabrication_unsupported, flags_unadjudicated, schema_errors, mean_llm_calls}}
    返り値: {'label','unmet':[...],'notes':[...]}。label:
      REJECTED(創作UNSUPPORTED>0、またはmey KEY改善<+0.10) /
      NOT_FINALIZABLE_UNADJUDICATED(創作フラグ未判定が残る) /
      NOT_VALIDATED_BELOW_CRITERION_A_PRIME(改善>=+0.10だが基準(a')未達のみ) /
      NOT_VALIDATED_CRITERIA_UNMET(他基準未達) /
      USER_DECISION_CANDIDATE_COST(a'〜g充足だが追加LLM呼出>0=費用判断が要る) /
      VALIDATED_CANDIDATE_PENDING_SEARCH_ARM(a'〜g充足。(h)検索回数/費用は検索込み腕で別判定)
    """
    unsupp = sum(t["fabrication_unsupported"] for t in per_topic.values())
    unadj = sum(t["flags_unadjudicated"] for t in per_topic.values())
    notes, unmet = [], []
    mey, mey0 = per_topic["mey"], base["mey"]
    imp = (mey["key_ledger"] or 0) - (mey0["key_ledger"] or 0)
    if unsupp > 0:
        return {"label": "REJECTED", "unmet": ["d:fabrication_unsupported=%d" % unsupp], "notes": notes}
    if unadj > 0:
        return {"label": "NOT_FINALIZABLE_UNADJUDICATED", "unmet": ["d:unadjudicated=%d" % unadj], "notes": notes}
    if imp < 0.10 - TOL:
        return {"label": "REJECTED", "unmet": ["a:mey KEY improvement %.3f < +0.10" % imp], "notes": notes}
    a_prime = (mey["key_ledger"] >= 0.9165 - TOL or imp >= 0.1665 - TOL) and mey["key_ledger"] >= 0.667 - TOL
    if not a_prime:
        unmet.append("a_prime")
    only_a_prime = True
    for t in ("muse", "coffee"):
        if t not in per_topic:
            continue
        pt, bt = per_topic[t], base[t]
        if pt["key_ledger"] < bt["key_ledger"] - 0.05 - TOL:
            unmet.append("b:%s regression" % t)
        elif bt["key_ledger"] < 0.9 and pt["key_ledger"] - bt["key_ledger"] < 0.15 - TOL:
            unmet.append("b:%s improvement<+0.15 (E0<0.9)" % t)
    for t, pt in per_topic.items():
        if pt["ctrl_ledger"] is not None and base[t]["ctrl_ledger"] is not None and pt["ctrl_ledger"] < base[t]["ctrl_ledger"] - 0.10 - TOL:
            unmet.append("c:%s CTRL regression" % t)
        if (pt["delta_facts_vs_E0"] or 0) > 2.0 + TOL:
            unmet.append("e:%s delta_facts>+2" % t)
        if pt["schema_errors"]:
            unmet.append("g:%s schema errors" % t)
    others = [u for u in unmet if u != "a_prime"]
    extra = any(per_topic[t]["mean_llm_calls"] > base[t]["mean_llm_calls"] + TOL for t in per_topic)
    if others:
        return {"label": "NOT_VALIDATED_CRITERIA_UNMET", "unmet": unmet, "notes": notes}
    if "a_prime" in unmet:
        return {"label": "NOT_VALIDATED_BELOW_CRITERION_A_PRIME", "unmet": unmet, "notes": ["mey KEY improvement=%.3f (>=+0.10, <a')" % imp]}
    if extra:
        return {"label": "USER_DECISION_CANDIDATE_COST", "unmet": [], "notes": ["追加LLM呼出>0: 費用対効果(f)はA〜D最良に対する追加改善+0.15以上かつ追加費用<=JPY1/記事で別判定"]}
    return {"label": "VALIDATED_CANDIDATE_PENDING_SEARCH_ARM", "unmet": [], "notes": ["(h)検索回数・恒常費用は検索込み腕の結果で別判定"]}


def classify_all(agg: dict) -> dict:
    topics = sorted({k.split("|")[1] for k in agg})
    variants = sorted({k.split("|")[0] for k in agg if k.split("|")[0] not in ("E0", "X1")})
    if not all(f"E0|{t}" in agg for t in topics):
        return {}
    base = {t: agg[f"E0|{t}"] for t in topics}
    out = {}
    for v in variants:
        pt = {t: agg[f"{v}|{t}"] for t in topics if f"{v}|{t}" in agg}
        if "mey" in pt:
            out[v] = classify_variant(v, pt, base)
    return out


def md_report(cells: list, agg: dict, gold: dict, title: str) -> str:
    L = [f"# {title}", "", f"(機械採点。gold={gold.get('frozen_at')})", "", "## 方式×題材 集計", "",
         "| 方式|題材 | n | KEY保持(Ledger) | KEY保持(下書き) | SEC | CTRL | Fact数平均 | Δ対E0 | フラグ(未判定/創作) | LLM呼出 | 費用JPY | 時間s | 検索 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, a in agg.items():
        L.append(f"| {k} | {a['n_samples']} | {a['key_ledger']} | {a['key_draft']} | {a['sec_ledger']} | {a['ctrl_ledger']} | {a['mean_facts']} | {a['delta_facts_vs_E0']} | "
                 f"{a['flags_total']}({a['flags_unadjudicated']}/{a['fabrication_unsupported']}) | {a['mean_llm_calls']} | {a['mean_cost_jpy']} | {a['mean_latency_s']} | {a['web_search_calls']} |")
    cls = classify_all(agg)
    if cls:
        L += ["", "## 方式別 機械判定(設計v02 §9-1。最終ラベルはFable)", ""]
        for v, c in cls.items():
            L.append(f"- {v}: **{c['label']}** unmet={c['unmet']} {c['notes']}")
    L += ["", "## gold項目別(各セル)", ""]
    for c in sorted(cells, key=lambda x: (x["topic"], x["variant"], x["sample"])):
        rows = [f"{iid}:{'OK' if r['ledger'] else 'MISS[' + r['diag'].split('(')[0] + ']'}" for iid, r in c["per_item"].items()]
        L.append(f"- {c['variant']}/{c['topic']}/s{c['sample']} (facts={c['n_facts_draft']}, {c['verdict_counts']}): " + " ".join(rows))
    L += ["", "## 創作候補フラグ(出典逐語照合が必要)", ""]
    n = 0
    for c in cells:
        for f in c["flags"]:
            n += 1
            L.append(f"- {c['variant']}|{c['topic']}|s{c['sample']}|{f['fact_id']}: {','.join(f['reasons'])} -> {f['adjudication']}")
    if n == 0:
        L.append("(フラグ0件)")
    return "\n".join(L) + "\n"


def collect(out_root: str, variants=None, include_dryrun=False, gold_path=None) -> list:
    gold = load_gold(gold_path)
    adj_path = os.path.join(lib.DOC_DIR, "adjudication_01.json")
    adjud = lib.read_json(adj_path) if os.path.exists(adj_path) else {}
    base = os.path.join(out_root, "_dryrun") if include_dryrun else out_root
    cells = []
    for sp in sorted(glob.glob(os.path.join(base, "*", "s*", "*", "summary.json"))):
        vdir = os.path.dirname(sp)
        sample = int(os.path.basename(os.path.dirname(vdir))[1:])
        topic = os.path.basename(os.path.dirname(os.path.dirname(vdir)))
        variant = os.path.basename(vdir)
        if topic not in gold["topics"] or (variants and variant not in variants):
            continue
        cells.append(eval_cell(vdir, topic, gold, adjud, variant, sample))
    return cells


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=lib.OUT_ROOT)
    ap.add_argument("--report", default=None)
    ap.add_argument("--variant", nargs="*", default=None)
    ap.add_argument("--include-dryrun", action="store_true")
    ap.add_argument("--gold", default=None, help="gold json path (default gold_02.json)")
    ap.add_argument("--title", default="XRFR eval")
    a = ap.parse_args(argv)
    cells = collect(os.path.abspath(a.out), a.variant, a.include_dryrun, a.gold)
    gold = load_gold(a.gold)
    agg = aggregate(cells)
    res = {"cells": cells, "aggregate": agg, "classification": classify_all(agg)}
    lib.write_json(os.path.join(os.path.abspath(a.out), "eval_summary_dryrun.json" if a.include_dryrun else "eval_summary.json"), res)
    md = md_report(cells, agg, gold, a.title)
    if a.report:
        lib.write_text(a.report, md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
