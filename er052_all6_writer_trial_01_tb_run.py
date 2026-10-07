# -*- coding: utf-8 -*-
"""ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01 Phase2 T-B(既知NG記事の再判定、Trial専用)。

既知NG(重大/軽微)を含む固定記事+台帳を、JA Fact Check(vfl01.run_deviation_check、同一prompt/schema、
hook_aware=False・include_related_fact_id=True。EN記事は source_article_text=JA R2 付き=Production EN deviation check相当)
へ入れ、gpt-5.6-luna / gpt-6-luna で各n=2判定する。Production codeは編集しない(modelは引数で明示)。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

BASE = "er052_output/all6_writer_redesign_necessity_01/T-B"
MODELS = ("gpt-5.6-luna", "gpt-6-luna")
OVERRIDE = "ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01"


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def key_text(ng_text: str) -> str:
    """NG文から比較用の本文を取り出す(「」内があればそれ、無ければ全体)。"""
    m = re.findall(r"[「『]([^」』]{6,})[」』]", ng_text or "")
    s = max(m, key=len) if m else (ng_text or "")
    return re.sub(r"\s+", "", s)


def bigrams(s: str):
    s = re.sub(r"[、。，．,.\s「」『』()（）]", "", s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def overlap(ng: str, claim: str) -> float:
    a = bigrams(key_text(ng))
    b = bigrams(claim or "")
    return len(a & b) / len(a) if a else 0.0


def judge_one(item, model, rep, client, vfl01, cl, results_dir):
    art_key = item["article_path"]
    out = f"{results_dir}/{item['item_id']}__{model}__r{rep}.json"
    if os.path.exists(out):
        return json.load(open(out, encoding="utf-8"))
    ledger = read(item["ledger_path"])
    article = read(item["article_path"])
    src = read(item["source_article_path"]) if item.get("source_article_path") else None
    kw = dict(hook_aware=False, include_related_fact_id=True)
    if src is not None:
        kw["source_article_text"] = src
    t0 = time.time()
    with cl.logging_context("ALL6_TB", f"tb_{model}"):
        res = vfl01.run_deviation_check(client, ledger, article, model=model, **kw)
    parsed = res["parsed"]
    devs = parsed.get("deviations", [])
    matched = []
    for d in devs:
        ov = overlap(item["ng_text"], d.get("claim_in_article", ""))
        if ov >= 0.4:
            matched.append({"severity": d.get("severity"), "overlap": round(ov, 2), "related_fact_id": d.get("related_fact_id"),
                            "claim": d.get("claim_in_article")})
    sev_order = {"MAJOR": 2, "MINOR": 1}
    matched_sev = max((sev_order.get(m["severity"], 0) for m in matched), default=0)
    any_sev = max((sev_order.get(d.get("severity"), 0) for d in devs), default=0)
    rec = {
        "item_id": item["item_id"], "kind": item["kind"], "ng_type": item["ng_type"], "model_requested": model,
        "model_actual": res.get("model"), "rep": rep, "overall_status": parsed.get("overall_status"),
        "n_deviations": len(devs), "n_major": sum(d.get("severity") == "MAJOR" for d in devs),
        "n_minor": sum(d.get("severity") == "MINOR" for d in devs),
        "matched": matched, "matched_severity": {2: "MAJOR", 1: "MINOR", 0: "NONE"}[matched_sev],
        "article_max_severity": {2: "MAJOR", 1: "MINOR", 0: "COMPLIANT"}[any_sev],
        "flags": {k: v for k, v in parsed.items() if k not in ("deviations", "overall_status")},
        "deviations": devs, "raw_text": res.get("raw_text"), "usage": res.get("usage"),
        "sec": round(time.time() - t0, 1),
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    return rec


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--yes-run-paid", action="store_true")
    a = ap.parse_args(argv)
    items = json.load(open(f"{BASE}/items.json", encoding="utf-8"))["items"]
    if a.limit:
        items = items[:a.limit]
    # 同一記事+同一入力は1回の判定を共有(item_idごとに保存はするが、APIは記事単位)
    jobs = [(it, m, r) for r in range(1, a.reps + 1) for m in MODELS for it in items]
    print(f"jobs={len(jobs)} (items={len(items)} x models={len(MODELS)} x reps={a.reps})")
    if not a.yes_run_paid:
        return 0
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_model_routing_contract_01 as routing
    for m in MODELS:   # 実行前にrouting契約のoverride経路で許可確認(5.6はApproved、6-lunaは明示override)
        routing.require_model_or_override("WRITER_FACT_CHECK", m, override_reason=OVERRIDE)
    results_dir = f"{BASE}/results"
    os.makedirs(results_dir, exist_ok=True)
    cl.install(f"{BASE}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    # 記事が同じitemは同じ入力なので、2番目以降は先頭itemの結果を流用して再API呼び出しを避ける
    cache, lock = {}, threading.Lock()

    def work(job):
        it, m, r = job
        k = (it["article_path"], it.get("source_article_path"), m, r)
        with lock:
            if k in cache:
                first = cache[k]
            else:
                first = None
                cache[k] = it["item_id"]
        if first is None:
            return judge_one(it, m, r, client, vfl01, cl, results_dir)
        # 先頭itemの完了を待ってから、同記事の判定結果をこのitem向けに再マッチングして保存
        src = f"{results_dir}/{first}__{m}__r{r}.json"
        while not os.path.exists(src):
            time.sleep(1)
        base = json.load(open(src, encoding="utf-8"))
        matched = []
        for d in base["deviations"]:
            ov = overlap(it["ng_text"], d.get("claim_in_article", ""))
            if ov >= 0.4:
                matched.append({"severity": d.get("severity"), "overlap": round(ov, 2),
                                "related_fact_id": d.get("related_fact_id"), "claim": d.get("claim_in_article")})
        so = {"MAJOR": 2, "MINOR": 1}
        ms = max((so.get(x["severity"], 0) for x in matched), default=0)
        rec = dict(base, item_id=it["item_id"], kind=it["kind"], ng_type=it["ng_type"], matched=matched,
                   matched_severity={2: "MAJOR", 1: "MINOR", 0: "NONE"}[ms], shared_call_with=first)
        with open(f"{results_dir}/{it['item_id']}__{m}__r{r}.json", "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
        return rec

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        recs = list(ex.map(work, jobs))
    import er019_family_x_entertainment_production_runner_01 as runner
    cost = runner.compute_stage_cost_breakdown(f"{BASE}/raw_usage_log.jsonl")
    json.dump(cost, open(f"{BASE}/cost.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done", len(recs), cost)
    return 0


if __name__ == "__main__":
    sys.exit(main())
