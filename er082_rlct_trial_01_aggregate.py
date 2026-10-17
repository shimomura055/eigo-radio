# ============================================================
# er082_rlct_trial_01_aggregate.py  (集計、JPY0、Trial専用)
# ============================================================
# 記事x方式の表(md/json): 費用[LLM/web_search別]、呼出数・クエリ数[種別別]、verdict遷移、選定Fact、Jaccard、
# 再選定回数、中心Fact(AMBIGUOUS)件数、契約検証、本番換算費用(Research+検証+B3+再選定、共有分も帰属)と削減率。
# 採否分類(REJECTED/VALIDATED/USER_DECISION_REQUIRED)は行わない(Fable独立レビュー+ユーザー判断事項)。
# ============================================================
from __future__ import annotations

import argparse
import os
import sys

import er082_rlct_trial_01_lib as lib
from er082_rlct_trial_01_lib import ARTICLES, METHODS, OUT_ROOT, load_json, save_json, save_text


CORRECTED = ["M2c", "M3c"]      # 委任_07 D6: 最終B3確認パス追加後(Stage 1a補正)
LABELS = {"M0": "従来(M0)", "M0b": "従来再実行(M0b)", "M0p": "同日再検証のみ(M0p)", "M1": "案1",
          "M2": "案2", "M3": "案1+2", "M2c": "案2(確認パス後)", "M3c": "案1+2(確認パス後)"}


def method_label(method: str, present: set) -> str:
    """M2c/M3cがある記事では、修正前のM2/M3を『(修正前・参考)』として併記する。"""
    if method in ("M2", "M3") and f"{method}c" in present:
        return LABELS[method] + "(修正前・参考)"
    return LABELS[method]


def _baseline_costs(out_root: str, article: str) -> dict:
    """既存run(複製)の raw_usage_log から Research/Ledger/B3 の実測費用を取る(stage tag別)。"""
    p = f"{out_root}/{article}/_inputs/raw_usage_log.jsonl"
    c = lib.cost_by_stage_tag(p, theme=None) if os.path.exists(p) else {}
    g = lambda k: c.get(k, {}).get("total_jpy", 0.0)  # noqa: E731
    ws = lambda k: c.get(k, {}).get("web_search_calls", 0)  # noqa: E731
    return {"research_jpy": g("research"), "ledger_jpy": g("ledger"), "b3_jpy": g("storyline_b3"),
            "research_ws_calls": ws("research"), "ledger_ws_calls": ws("ledger")}


def _step_total(res: dict, *names) -> float:
    return round(sum(v["total_jpy"] for k, v in res["cost"]["by_step"].items()
                     if any(k == n or k.startswith(n) for n in names)), 3)


def production_equivalent(out_root: str, article: str, method: str, res: dict, m2_res: dict | None) -> float | None:
    base = _baseline_costs(out_root, article)
    r = base["research_jpy"]
    if method == "M0":
        b3 = base["b3_jpy"] if ARTICLES[article]["b3_reusable"] else _step_total(res, "b3")
        return round(r + base["ledger_jpy"] + b3, 3)
    if method == "M0b":
        return round(r + base["ledger_jpy"] + _step_total(res, "b3"), 3)
    if method == "M1":
        return round(r + _step_total(res, "ledger") + _step_total(res, "b3"), 3)
    if method == "M2":
        return round(r + _step_total(res, "verify_sel", "b3"), 3)
    if method == "M3":
        shared = _step_total(m2_res, "b3_initial") if m2_res else 0.0
        return round(r + _step_total(res, "verify_sel", "b3") + shared, 3)
    if method in CORRECTED:     # 補正元実測+補正費用(res["cost_production_equivalent"])を使う
        cpe = res["cost_production_equivalent"]["total_jpy"]
        shared = _step_total(m2_res, "b3_initial") if (method == "M3c" and m2_res) else 0.0
        return round(r + cpe + shared, 3)
    return None        # M0p はLedgerのみの統制(本番換算対象外)


def collect(out_root: str) -> dict:
    table = {}
    for art in ARTICLES:
        table[art] = {}
        for m in METHODS + CORRECTED:
            p = f"{out_root}/{art}/{m}/result.json"
            if os.path.isfile(p):
                table[art][m] = load_json(p)
    rows = []
    for art, ms in table.items():
        m0 = ms.get("M0")
        m0_ids = (m0 or {}).get("selected_fact_ids") or []
        m0_eq = production_equivalent(out_root, art, "M0", m0, None) if m0 else None
        present = set(ms)
        for m, res in ms.items():
            eq = production_equivalent(out_root, art, m, res, ms.get("M2")) if res.get("status") == "COMPLETED" else None
            tot = res["cost"]["total"]
            ws = res["web_search_calls"]
            tr = res.get("verdict_transitions") or {}
            rows.append({
                "article": art, "method": m, "label": method_label(m, present), "status": res["status"], "basis": res["usage_basis"],
                "dry_run": res.get("dry_run"),
                "trial_llm_jpy": tot["llm_jpy"], "trial_web_search_jpy": tot["web_search_jpy"],
                "trial_total_jpy": tot["total_jpy"],
                "web_search_calls": tot["web_search_calls"], "by_action_type": ws["by_action_type"],
                "query_count": ws["query_count"],
                "selected_fact_ids": res.get("selected_fact_ids"),
                "jaccard_vs_M0": lib.jaccard(res.get("selected_fact_ids") or [], m0_ids) if m != "M0" else 1.0,
                "reselect_count": (res.get("reselect") or {}).get("reselect_count"),
                "confirm_pass_count": (res.get("reselect") or {}).get("confirm_pass_count"),
                "b3_reselect_jpy": _step_total(res, "b3_reselect"), "b3_confirm_jpy": _step_total(res, "b3_confirm"),
                "corrected_from": res.get("corrected_from"),
                "cost_correction_only_jpy": (res.get("cost_correction_only") or {}).get("total_jpy"),
                "demotions_from_verified": tr.get("demotions_from_verified"),
                "promotions": tr.get("promotions_to_verified_or_up"),
                "ambiguous_central_count": (res.get("ambiguous_central") or {}).get("count"),
                "known_defect_status": res.get("known_defect_status"),
                "contract_all_pass": (res.get("contract") or {}).get("all_pass"),
                "verifier_model_matches_m0": res.get("verifier_model_matches_m0"),
                "b3_model": res.get("b3_model"),
                "soft_cap_exceeded_requests": [r["label"] for r in res.get("verify_requests", [])
                                               if r.get("exceeds_soft_cap_estimate")],
                "production_equivalent_jpy": eq,
                "saving_vs_M0_jpy": (round(m0_eq - eq, 3) if (eq is not None and m0_eq is not None) else None),
                "saving_vs_M0_pct": (round((m0_eq - eq) / m0_eq * 100, 1) if (eq is not None and m0_eq) else None),
            })
    return {"rows": rows, "note": _note(rows)}


def _note(rows: list) -> str:
    """キャプションは出力元で切替: 全行が dry_run=False かつ basis=OFFICIAL_API_RESPONSE なら実測(MEASURED)、
    全行 dry_run=True ならSYNTHETIC(stub)、混在は両方を明示(固定文言を廃止)。"""
    dr = [bool(r.get("dry_run")) for r in rows]
    if rows and not any(dr) and all(r.get("basis") == "OFFICIAL_API_RESPONSE" for r in rows):
        return "MEASURED(実測): 全行 dry_run=false かつ usage_basis=OFFICIAL_API_RESPONSE。"
    if rows and all(dr):
        return "SYNTHETIC(stub)。dry-runの値であり、実測ではない。"
    return "MIXED: dry_run行(SYNTHETIC stub)と実測行が混在。行ごとの dry_run/basis を確認すること。"


def to_markdown(agg: dict, title: str) -> str:
    L = [f"# {title}", "", agg["note"], "",
         "| 記事 | 方式 | status | Trial費用JPY(LLM/検索/計) | 検索呼出(種別) | クエリ | 選定Fact | Jaccard | 再選定/確認パス | 再選定B3/確認B3 JPY | 降格 | 昇格 | 中心AMBIG | 契約 | 本番換算JPY | 削減JPY | 削減% |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in agg["rows"]:
        L.append("| {a} | {m} | {s} | {l}/{w}/{t} | {c} {bt} | {q} | {sel} | {j} | {rs}/{cf} | {rj}/{cj} | {dm} | {pr} | {ac} | {ct} | {eq} | {sv} | {sp} |".format(
            a=r["article"], m=r["label"], s=r["status"], l=r["trial_llm_jpy"], w=r["trial_web_search_jpy"],
            t=r["trial_total_jpy"], c=r["web_search_calls"], bt=r["by_action_type"], q=r["query_count"],
            sel=",".join(r["selected_fact_ids"] or []), j=r["jaccard_vs_M0"], rs=r["reselect_count"], cf=r["confirm_pass_count"], rj=r["b3_reselect_jpy"], cj=r["b3_confirm_jpy"],
            dm=",".join(r["demotions_from_verified"] or []), pr=",".join(r["promotions"] or []),
            ac=r["ambiguous_central_count"], ct=r["contract_all_pass"], eq=r["production_equivalent_jpy"],
            sv=r["saving_vs_M0_jpy"], sp=r["saving_vs_M0_pct"]))
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_ROOT)
    ap.add_argument("--title", default="RLCT Trial 集計")
    a = ap.parse_args(argv)
    agg = collect(a.out)
    save_json(f"{a.out}/aggregate.json", agg)
    save_text(f"{a.out}/aggregate.md", to_markdown(agg, a.title))
    print(f"[aggregate] rows={len(agg['rows'])} -> {a.out}/aggregate.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
