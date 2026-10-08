# -*- coding: utf-8 -*-
# ============================================================
# er052_gpt6_wiring_probe_01.py
# PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 委任_02 Phase 0 互換probe
# ============================================================
# 目的: gpt-6-luna で未確認だったProduction工程(Blueprint/Proper Noun/Std A2/
# Research/Coverage Gate/Support/Key Phrase explanation/Topic research)を、
# **実装と同じ呼び出しパターン**で1〜2 callずつ叩いて互換性を確認する。
#
# 制約:
# - Production codeは一切編集しない。routing.require_model / 各moduleのmodel定数 /
#   OpenAI Responses.create を**メモリ上でだけ**差し替える(ファイルは不変)。
# - 差し替えたrequire_modelは必ず require_model_or_override(..., override_reason=...)
#   を通す(理由なしの暗黙overrideはしない)。
# - 品質は評価しない(互換のみ)。入力は既存Trial成果物(読み取り)を再利用する。
# - 費用: 6-luna単価 0.10/0.01/0.50 $/1M、USD/JPY=160。--budget-jpy到達で以降のprobeを中止。
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

PROBE_MODEL = "gpt-6-luna"
OVERRIDE_REASON = "PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 Phase0 probe"
USD_JPY = 160.0
PRICE_IN, PRICE_CACHED, PRICE_OUT = 0.10, 0.01, 0.50  # $/1M tokens
WEB_SEARCH_USD_PER_CALL = 0.01  # 参考(tool fee概算、$10/1k calls)

ART_DIR = "er052_output/all6_writer_redesign_necessity_01/runs/hormuz/control/b1__all6__r1"
LEDGER_PATH = "er052_output/open233_polysemy_trial_02/ledgers/hormuz/control/research_ledger/verified_fact_ledger.txt"

PRODUCTION_FILES = [
    "er006_model_routing_contract_01.py", "er008_shared_point_blueprint_01.py",
    "er006_proper_noun_extraction_01.py", "er003_v1_n3_01_standard_a2_generate.py",
    "er006_pool_pilot_01_research.py", "er006_research_coverage_gate_01.py",
    "er003_v1_n3_01_scaffold_generate.py", "er019_family_x_kp_explanation_01.py",
    "er002_topic_adapter.py", "gather_topic.py", "er003_v1_en_direct_vfl_01_generate.py",
    "er005_output/cost_baseline_01/pricing_snapshot.json",
]

_TL = threading.local()
CALLS: list = []          # 全API callの記録
REQUIRE_LOG: list = []    # require_model差し替えの記録
_LOCK = threading.Lock()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def cost_usd_of(usage: dict, web_calls: int) -> float:
    inp = usage.get("input_tokens") or 0
    cached = usage.get("cached_tokens") or 0
    out = usage.get("output_tokens") or 0
    return ((max(inp - cached, 0)) * PRICE_IN + cached * PRICE_CACHED + out * PRICE_OUT) / 1e6 \
        + web_calls * WEB_SEARCH_USD_PER_CALL


def summarize_response(resp, kwargs: dict, elapsed: float) -> dict:
    usage = getattr(resp, "usage", None)
    details = getattr(usage, "input_tokens_details", None)
    u = {
        "input_tokens": getattr(usage, "input_tokens", None) or 0,
        "output_tokens": getattr(usage, "output_tokens", None) or 0,
        "cached_tokens": (getattr(details, "cached_tokens", None) or 0) if details is not None else 0,
    }
    out_items = getattr(resp, "output", None) or []
    types = [getattr(i, "type", "?") for i in out_items]
    web_calls = sum(1 for t in types if t == "web_search_call")
    reasoning_obj = getattr(resp, "reasoning", None)
    inc = getattr(resp, "incomplete_details", None)
    text = ""
    try:
        text = resp.output_text or ""
    except Exception:
        pass
    fmt = ((kwargs.get("text") or {}).get("format") or {}).get("type")
    schema_ok = None
    if fmt == "json_schema":
        try:
            json.loads(text)
            schema_ok = True
        except Exception:
            schema_ok = False
    return {
        "probe": getattr(_TL, "probe", None),
        "requested_model": kwargs.get("model"),
        "response_model": getattr(resp, "model", None),
        "response_id": getattr(resp, "id", None),
        "status": getattr(resp, "status", None),
        "incomplete_reason": getattr(inc, "reason", None) if inc is not None else None,
        "requested_reasoning": kwargs.get("reasoning"),
        "response_reasoning_effort": getattr(reasoning_obj, "effort", None) if reasoning_obj is not None else None,
        "has_web_search_tool": any(isinstance(t, dict) and t.get("type") == "web_search"
                                   for t in (kwargs.get("tools") or [])),
        "web_search_call_count": web_calls,
        "output_item_types": sorted(set(types)),
        "has_previous_response_id": bool(kwargs.get("previous_response_id")),
        "text_format": fmt,
        "schema_ok": schema_ok,
        "output_chars": len(text),
        "usage": u,
        "cost_usd": round(cost_usd_of(u, web_calls), 6),
        "cost_jpy": round(cost_usd_of(u, web_calls) * USD_JPY, 3),
        "elapsed_sec": round(elapsed, 2),
    }


def install_patches() -> dict:
    """メモリ上の差し替えだけを行う(ファイル無編集)。戻り値=原状復帰用。"""
    import openai.resources.responses as rr
    import er006_model_routing_contract_01 as routing

    orig_create = rr.Responses.create
    orig_require = routing.require_model

    def recording_create(self, *args, **kwargs):
        t0 = time.time()
        resp = orig_create(self, *args, **kwargs)
        rec = summarize_response(resp, kwargs, time.time() - t0)
        with _LOCK:
            CALLS.append(rec)
        return resp

    def probe_require_model(process, model=None):
        REQUIRE_LOG.append({"probe": getattr(_TL, "probe", None), "process": process,
                            "incoming_model": model, "forced_model": PROBE_MODEL,
                            "override_reason": OVERRIDE_REASON})
        return routing.require_model_or_override(process, PROBE_MODEL, override_reason=OVERRIDE_REASON)

    rr.Responses.create = recording_create
    routing.require_model = probe_require_model
    return {"rr": rr, "orig_create": orig_create, "routing": routing, "orig_require": orig_require}


def uninstall_patches(state: dict) -> None:
    state["rr"].Responses.create = state["orig_create"]
    state["routing"].require_model = state["orig_require"]


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------
# 各probe(実装関数を、実装と同じ呼び出しパターンのまま呼ぶ)
# ------------------------------------------------------------
def probe_blueprint(ctx):
    import er006_model_routing_contract_01 as routing
    import er008_shared_point_blueprint_01 as bp
    from openai import OpenAI
    model = routing.require_model_or_override("SHARED_POINT_BLUEPRINT", PROBE_MODEL, override_reason=OVERRIDE_REASON)
    ja = read(f"{ART_DIR}/ja_writer/original.md")
    topic_ja = ja.strip().splitlines()[0].lstrip("# ").strip()
    r = bp.run_blueprint_generation(OpenAI(), topic_ja, ctx["ledger"], model=model)
    return {"parsed_keys": sorted((r.get("parsed") or {}).keys())}


def probe_proper_noun(ctx):
    import er006_proper_noun_extraction_01 as pn
    r = pn.extract_proper_nouns(ctx["adv"], "(support text: probe)", "(key phrases: probe)")
    return {"items": len(r.get("items") or []), "model": r.get("model")}


def probe_standard_a2(ctx):
    import er003_v1_n3_01_standard_a2_generate as sa2
    r = sa2.generate_standard_a2(ctx["adv"], model=PROBE_MODEL)
    return {"model_id_actual": getattr(r, "model_id_actual", None),
            "attempts": getattr(r, "attempts", None),
            "out_chars": len(getattr(r, "text", "") or "")}


def probe_research(ctx):
    import er006_pool_pilot_01_research as rs
    work = os.path.join(ctx["out_dir"], "work_research")
    os.makedirs(work, exist_ok=True)
    adv = ctx["adv"]
    paras = [p for p in adv.split("\n\n") if p.strip()]
    sources = [
        {"source_id": "S1", "title": "probe source 1 (Trial article excerpt)", "access_status": "OK",
         "retrieval_method": "probe_fixed_text", "text": "\n\n".join(paras[1:3])},
        {"source_id": "S2", "title": "probe source 2 (Trial article excerpt)", "access_status": "OK",
         "retrieval_method": "probe_fixed_text", "text": "\n\n".join(paras[3:5])},
    ]
    ep = rs.run_stage_b2_evidence_pack("probe_hormuz", work, "Hormuz fee plan and oil prices", sources)
    vfl = rs.run_stage_b3_vfl("probe_hormuz", work, "Hormuz fee plan and oil prices", ep)
    return {"evidence_items": len(ep["parsed"]["evidence_items"]), "facts": len(vfl["parsed"]["facts"])}


def probe_coverage_gate(ctx):
    import er006_research_coverage_gate_01 as gate
    gate.GATE_MODEL = PROBE_MODEL  # メモリ上のみ。直書き定数でrequire_modelを呼ばない実装のため
    r = gate.run_coverage_gate("Hormuz fee plan and oil prices", ctx["ledger"])
    return {"verdict": (r.get("parsed") or {}).get("verdict")}


def probe_support_kp_selection(ctx):
    import er003_v1_n3_01_scaffold_generate as sc
    sc._log_kp_backend_telemetry = lambda *a, **k: None  # Production telemetry追記を避ける(メモリ上のみ)
    out = os.path.join(ctx["out_dir"], "work_support")
    r = sc.run_key_phrase_selection(ctx["adv"], out, "probe_hormuz", "b1", process="B1_SUPPORT",
                                    kp_backend="strategy_l", synthetic=True)
    return {"status": r.get("status"), "model_id": r.get("model_id")}


def probe_kp_explanation(ctx):
    import er019_family_x_kp_explanation_01 as kp
    kp.MODEL = PROBE_MODEL  # 直書き定数をメモリ上でのみ差し替え
    items = [
        {"rank": 1, "display_phrase": "pared their gains",
         "source_sentence": "Brent crude futures temporarily pared their gains.", "japanese_gloss": "上げ幅を縮めた"},
        {"rank": 2, "display_phrase": "near their highs",
         "source_sentence": "Oil prices stay near their highs.", "japanese_gloss": "高値圏にとどまる"},
        {"rank": 3, "display_phrase": "citing the cost of keeping it safe",
         "source_sentence": "The first post said the United States would seek 20 percent reimbursement, citing the cost of keeping it safe.",
         "japanese_gloss": "安全確保の費用を理由に挙げて"},
        {"rank": 4, "display_phrase": "moving at fast-forward speed",
         "source_sentence": "When it comes to policy proposals, this story is moving at fast-forward speed.",
         "japanese_gloss": "早送りの速さで進んでいる"},
        {"rank": 5, "display_phrase": "changed its look",
         "source_sentence": "The policy proposal had already changed its look.", "japanese_gloss": "見た目が変わった"},
    ]
    r = kp.generate_kp_explanations(items)
    return {"status_by_rank": {str(k): v.get("status") for k, v in (r.get("items") or {}).items()}}


def probe_topic_research(ctx):
    import er002_topic_adapter as ta
    ta.MODEL_SEARCH = PROBE_MODEL  # 直書き定数をメモリ上でのみ差し替え(web_search tool)
    fn = ta.make_topic_research_fn("technology")
    text = fn("October 08, 2026")
    return {"out_chars": len(text)}


PROBES = [
    ("SHARED_POINT_BLUEPRINT", probe_blueprint),
    ("PROPER_NOUN_EXTRACTION", probe_proper_noun),
    ("STANDARD_A2_ADAPTATION", probe_standard_a2),
    ("EVIDENCE_PACK+VFL", probe_research),
    ("RESEARCH_COVERAGE_GATE", probe_coverage_gate),
    ("B1_SUPPORT(KP selection)", probe_support_kp_selection),
    ("KEY_PHRASE_ADVANCED_EXPLANATION", probe_kp_explanation),
    ("QUERY_PLANNING/TOPIC_SELECTION(topic_adapter web_search)", probe_topic_research),
]


def total_cost_jpy() -> float:
    with _LOCK:
        return sum(c["cost_jpy"] for c in CALLS)


def run_one(name, fn, ctx, budget_jpy):
    _TL.probe = name
    if total_cost_jpy() >= budget_jpy:
        return {"probe": name, "result": "SKIPPED_BUDGET"}
    t0 = time.time()
    try:
        extra = fn(ctx)
        return {"probe": name, "result": "OK", "extra": extra, "elapsed_sec": round(time.time() - t0, 1)}
    except Exception as e:
        return {"probe": name, "result": "NG", "error_type": type(e).__name__,
                "error": str(e)[:600], "trace_tail": traceback.format_exc()[-800:],
                "elapsed_sec": round(time.time() - t0, 1)}


def build_summary(results, out_dir, sha_before, sha_after, budget_jpy) -> str:
    L = ["# Phase 0 probe サマリ(PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 委任_02)", "",
         "互換のみ確認、品質は未検証。モデル=gpt-6-luna(override理由付き、メモリ上差し替え)。",
         f"累計費用: ¥{total_cost_jpy():.2f} / 予算 ¥{budget_jpy}(6-luna 0.10/0.01/0.50 $/1M、USD/JPY=160、web_search概算$0.01/call)", "",
         "| 工程 | 結果 | API call数 | 実使用model_id | schema適合 | effort(要求→応答) | web_search_call | 出力長/切れ | 秒 | 費用¥ |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        cs = [c for c in CALLS if c["probe"] == r["probe"]]
        models = ",".join(sorted({str(c["response_model"]) for c in cs})) or "-"
        sch = ",".join(sorted({str(c["schema_ok"]) for c in cs})) or "-"
        eff = ",".join(sorted({f"{(c['requested_reasoning'] or {}).get('effort')}->{c['response_reasoning_effort']}" for c in cs})) or "-"
        web = sum(c["web_search_call_count"] for c in cs)
        trunc = ",".join(sorted({f"{c['output_chars']}字/{c['status']}" + (f"/{c['incomplete_reason']}" if c['incomplete_reason'] else "") for c in cs})) or "-"
        sec = round(sum(c["elapsed_sec"] for c in cs), 1)
        cost = round(sum(c["cost_jpy"] for c in cs), 2)
        L.append(f"| {r['probe']} | {r['result']} | {len(cs)} | {models} | {sch} | {eff} | {web} | {trunc} | {sec} | {cost} |")
    L += ["", "## NG/SKIPPED の症状"]
    ng = [r for r in results if r["result"] != "OK"]
    if not ng:
        L.append("- なし")
    for r in ng:
        L.append(f"- {r['probe']}: {r['result']} {r.get('error_type','')} {r.get('error','')}")
    L += ["", "## Production file sha256(probe前後)", "| file | 不変 |", "|---|---|"]
    for p in PRODUCTION_FILES:
        L.append(f"| {p} | {'OK' if sha_before.get(p) == sha_after.get(p) else 'CHANGED'} |")
    L += ["", "## require_model差し替え記録(全件override理由付き)", f"- 件数: {len(REQUIRE_LOG)}"]
    L.append("- 全件理由付き: " + str(all(r["override_reason"] for r in REQUIRE_LOG)))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--yes-run-paid", action="store_true")
    ap.add_argument("--parallel", type=int, default=2)
    args = ap.parse_args()
    if not args.yes_run_paid:
        print("[STOP] --yes-run-paid が必要です(有料API)。")
        sys.exit(2)
    from dotenv import load_dotenv
    load_dotenv()
    os.makedirs(args.out_dir, exist_ok=True)
    sha_before = {p: sha256_file(p) for p in PRODUCTION_FILES}
    ctx = {"out_dir": args.out_dir, "adv": read(f"{ART_DIR}/b1b/article.md"), "ledger": read(LEDGER_PATH)}
    state = install_patches()
    try:
        par = max(1, min(args.parallel, 2))
        with ThreadPoolExecutor(max_workers=par) as ex:
            futs = [ex.submit(run_one, n, f, ctx, args.budget_jpy) for n, f in PROBES]
            results = [f.result() for f in futs]
    finally:
        uninstall_patches(state)
    sha_after = {p: sha256_file(p) for p in PRODUCTION_FILES}
    with open(os.path.join(args.out_dir, "probe_results.json"), "w", encoding="utf-8") as f:
        json.dump({"results": results, "calls": CALLS, "require_log": REQUIRE_LOG,
                   "total_cost_jpy": total_cost_jpy(), "sha_before": sha_before, "sha_after": sha_after},
                  f, ensure_ascii=False, indent=2)
    summary = build_summary(results, args.out_dir, sha_before, sha_after, args.budget_jpy)
    with open(os.path.join(args.out_dir, "PROBE_SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write(summary)
    print(summary)


if __name__ == "__main__":
    main()
