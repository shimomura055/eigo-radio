"""OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_11 反実仮想replay(¥0、LLM callなし)。

rep27/rep28/rep29の全instance(各38 run=s1/s2)の記録済みLLM出力を使い、新ロジック(Opus#14後のFable評価採用設計、設計書§18)が
決定論部分でどの終端へ行くかを追跡する。LLM callが必要な分岐は「call必要」として件数化する(結果は推測しない)。

出力: replay_counterfactual_rep27_29_01.json / .md(同じディレクトリ)。
注記: 同一cycle内で先行claimの書き換えが後続claimのcycle開始本文を変える場合は、cycle開始本文(記録済み)で近似する。
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er052_open233_self_recovery_flow_runner_01 as R  # noqa: E402

R.apply_kpi_trial_switches()  # KPI構成(新スイッチON、既定OFFの2つはOFFのまま)
OUT_DIR = os.path.join("er052_output", "open233_kpi_recovery_02_offline_01")
REPS = {27: "open233_self_recovery_flow_runner_01_rep27", 28: "open233_self_recovery_flow_runner_01_rep28",
        29: "open233_self_recovery_flow_runner_01_rep29"}
ALLOWED = R.STAGE4_ALLOWED_REASONS

INSTANCES = {i["instance_id"]: i for i in R.build_target_instances()}


def text_chain(d: dict, text0: str) -> list:
    """各cycle開始時点の英語本文(記録済みの置換後本文を連鎖)。"""
    out, cur = [], text0
    for c in d["cycles"]:
        out.append(cur)
        cur = c.get("en_text_after_rewrite", cur)
    out.append(cur)
    return out


def blocking_results(c: dict) -> list:
    return [s for s in c["stage2_results"] if s["materiality"] == "BLOCKING"]


def replay_t_delete(text: str, sr: dict) -> dict:
    """T(最終手段)を決定論部分だけ実行する: ladderの`last_resort_delete`経路(LLM callなし)。"""
    rec = {"claim_text": sr["claim_text"], "rewrite_kind": sr.get("rewrite_kind") or "narrow_scope",
           "materiality": "BLOCKING", "basis": sr.get("basis"), "dev": sr["dev"], "last_resort_delete": True,
           "rewrite_hint": sr.get("rewrite_hint") or ""}
    try:
        out = R.rewrite_ranges_ladder(None, {"cumulative_jpy": 0.0}, [0], [], "replay_T",
                                      {"ledger_text": "", "article_text": text}, "article_text", rec)
    except Exception as e:  # noqa: BLE001  LLM callに到達した等
        return {"status": "error", "detail": f"{type(e).__name__}: {e}"}
    h = out.get("handoff") or {}
    if out.get("target_not_locatable"):
        return {"status": "unlocatable", "reason": h.get("span_unverified_reason")}
    if h.get("structural_blocking"):
        return {"status": "structural", "reasons": (h.get("last_resort_delete") or {}).get("structural_reasons")}
    if out.get("guard_ok"):
        return {"status": "deleted", "deleted_chars": len(text) - len(out["updated_text"])}
    return {"status": "delete_failed", "method": out.get("method")}


def deterministic_counters(d: dict, texts: list) -> dict:
    """STAGE4でない周回も含め、新ロジックが介入しうる箇所(B′昇段・A2却下・BLOCKING固定)を記録から決定論で数える。"""
    cnt = Counter()
    regions: list = []
    pinned: dict = {}
    history: list = []
    flagged = []
    for k, c in enumerate(d["cycles"]):
        text = texts[k]
        # B′: この周のBLOCKING claimが前cycleまでの置換範囲と重なるか
        for sr in blocking_results(c):
            lv, n = R.location_prior_levels(regions, sr, text)
            if lv:
                cnt["bprime_location_carry"] += 1
                flagged.append({"cycle": c["cycle"], "kind": "B'", "claim": (sr.get("claim_span_text") or sr["claim_text"])[:80],
                                "prior_levels": lv})
        # BLOCKING固定: 非BLOCKINGの再判定が、過去のBLOCKING確定と同じキー(span集合+fact_id)か
        for sr in c["stage2_results"]:
            if sr["materiality"] == "BLOCKING":
                continue
            kk = R.claim_materiality_key(sr.get("claim_text", ""), sr["dev"].get("related_fact_id") or "", text)
            if kk is not None and kk in pinned:
                cnt["pin_would_override_nonblocking"] += 1
                flagged.append({"cycle": c["cycle"], "kind": "pin", "claim": sr["claim_text"][:80],
                                "pinned_from_cycle": pinned[kk]})
        for sr in blocking_results(c):
            sp = sr.get("span_resolution_cycle_start") or {}
            if sp.get("status") == "resolved" and sp.get("ranges"):
                pinned.setdefault(R._span_key(sp["ranges"], sr["dev"].get("related_fact_id") or ""), c["cycle"])
        # A2: 記録済みの成功した書き換え案が、過去状態へ戻る案だったか
        if history:
            for rr in c.get("rewrite_records", []):
                for att in ((rr.get("handoff") or {}).get("level_attempts") or []):
                    if att.get("result") != "success":
                        continue
                    for t, r_ in zip(att.get("targets") or [], att.get("revised") or []):
                        if R.revert_to_prior_state_detected(history, text, t, r_):
                            cnt["a2_revert_would_reject"] += 1
                            flagged.append({"cycle": c["cycle"], "kind": "A2", "target": t[:80], "revised": r_[:80]})
        # 状態更新
        if texts[k + 1] != text:
            regions = R.update_regions_after_rewrite(regions, text, c.get("rewrite_records", []), c["cycle"])
            history.append(text)
    return {"counters": dict(cnt), "flagged": flagged}


def route_stage4(d: dict, texts: list) -> dict:
    """legacy STAGE4の記録から、新ロジックの終端(決定論部分)を追う。"""
    reason = d["stage4_reason"]
    last = d["cycles"][-1]
    k = len(d["cycles"]) - 1
    text = texts[k]
    out = {"legacy_reason": reason, "legacy_cycles": len(d["cycles"])}
    if reason == "degenerate_rewrite_output":
        out.update(route="degenerate_rewrite_output -> blocking_structural_after_ladder", terminal="STAGE4:blocking_structural_after_ladder",
                   terminal_allowed=True, deterministic=True, calls_needed=[])
    elif reason == "ladder_exhausted_without_full_rewrite":
        recs = [r for r in last.get("rewrite_records", []) if r.get("ladder_exhausted_without_full_rewrite")]
        brs = blocking_results(last)
        idx = [i for i, r in enumerate(last.get("rewrite_records", [])) if r.get("ladder_exhausted_without_full_rewrite")]
        api_only = all(all((a.get("result") in ("api_failure", "parse_failure"))
                           for a in ((r.get("handoff") or {}).get("level_attempts") or [])) and
                       ((r.get("handoff") or {}).get("level_attempts")) for r in recs)
        if api_only:
            out.update(route="exhausted(API失敗のみ) -> api_failure", terminal="STAGE4:api_failure", terminal_allowed=True,
                       deterministic=True, calls_needed=[])
        else:
            t_res = [replay_t_delete(text, brs[i]) for i in idx if i < len(brs)]
            out["t_results"] = t_res
            if any(x["status"] in ("structural", "unlocatable", "delete_failed", "error") for x in t_res):
                out.update(route="exhausted -> T(構造要素/削除不可) -> blocking_structural_after_ladder",
                           terminal="STAGE4:blocking_structural_after_ladder", terminal_allowed=True, deterministic=True,
                           calls_needed=[])
            else:
                out.update(route="exhausted -> T(決定論削除) -> 全文Recheck 1回", terminal="call必要(Recheck 1回→RESOLVED_REWRITE/judge-only cycle/post_T_new_blocking)",
                           terminal_allowed=True, deterministic=False, calls_needed=["full_recheck x1"])
    elif reason == "unconfirmed_after_reverify":
        out.update(route="unconfirmed_after_reverify(出口廃止) -> 次cycleのStage 2(funnel)へ合流", terminal="call必要(Stage 2+S1)",
                   terminal_allowed=True, deterministic=False, calls_needed=["stage2+s1 x1(次cycle)"])
    elif reason == "same_claim_fact_id_reblocked":
        regions: list = []
        for kk, c in enumerate(d["cycles"][:-1]):
            if texts[kk + 1] != texts[kk]:
                regions = R.update_regions_after_rewrite(regions, texts[kk], c.get("rewrite_records", []), c["cycle"])
        lvs = []
        for sr in blocking_results(last):
            lv, _n = R.location_prior_levels(regions, sr, text)
            lvs.append({"claim": (sr.get("claim_span_text") or sr["claim_text"])[:70], "span_status": (sr.get("span_resolution_cycle_start") or {}).get("status"), "prior_levels": lv})
        out["location_carry"] = lvs
        out.update(route="same_claim_fact_id_reblocked(出口廃止) -> ladderへ(B′で前levelより上位から昇段、枯渇ならT)",
                   terminal="call必要(Rewrite L3/L4→Recheck)", terminal_allowed=True, deterministic=False,
                   calls_needed=["rewrite(上位level) x1以上", "full_recheck x1"])
    elif reason == "cycle_limit_exhausted_after_recheck":
        rc = (d.get("all_deviations_raw") or {}).get("rechecks") or []
        major = [x for x in (rc[-1]["deviations"] if rc else []) if x.get("severity") == "MAJOR"]
        res = []
        for x in major:
            r = R.resolve_violation_spans(x.get("claim_in_article") or "", text if k == len(d["cycles"]) - 1 else texts[-1], None)
            res.append({"claim": (x.get("claim_in_article") or "")[:70], "fact": x.get("related_fact_id"), "span": r["status"], "reason": r.get("reason")})
        out["recheck_major"] = res
        out.update(route="cycle_limit_exhausted_after_recheck(出口廃止) -> 判定だけのcycle(Stage 2+S1、Rewriteなし)",
                   terminal="call必要(Stage 2+S1 x%d claim。非BLOCKING→RESOLVED_REWRITE_THEN_DOWNGRADE、BLOCKING→T/位置不明なら blocking_confirmed_unlocatable_after_cap)" % len(major),
                   terminal_allowed=True, deterministic=False, calls_needed=[f"stage2+s1 x{len(major)}(判定だけのcycle)"])
    elif reason == "violation_span_unverified":
        unl = [r for r in last.get("rewrite_records", []) if r.get("target_not_locatable")]
        brs = blocking_results(last)
        rs = []
        for r_i, r in enumerate(last.get("rewrite_records", [])):
            if not r.get("target_not_locatable"):
                continue
            sr = brs[r_i] if r_i < len(brs) else None
            if sr is None:
                continue
            res = R.resolve_violation_spans(sr["claim_text"], text, None)
            rs.append({"claim": sr["claim_text"][:90], "legacy_reason": (r.get("handoff") or {}).get("span_unverified_reason"),
                       "now_status": res["status"], "now_reason": res.get("reason"), "now_level": res.get("level"),
                       "explain_split": (res.get("explain_split") or {}).get("reason")})
        out["span_retry"] = rs
        if rs and all(x["now_status"] == "resolved" for x in rs):
            out.update(route="violation_span_unverified(出口廃止) -> D(i)緩和で位置を確定 -> Rewrite", terminal="call必要(Rewrite→Recheck)",
                       terminal_allowed=True, deterministic=False, calls_needed=["rewrite x1以上", "full_recheck x1"])
        else:
            out.update(route="violation_span_unverified(出口廃止) -> carry list(Rewriteせず全文Recheckで位置再取得、PASS禁止)",
                       terminal="call必要(Recheck 1回→再取得できれば書き換え、できなければ blocking_confirmed_unlocatable_after_cap)",
                       terminal_allowed=True, deterministic=False, calls_needed=["full_recheck x1"])
    else:
        out.update(route="未分類", terminal="未分類", terminal_allowed=False, deterministic=True, calls_needed=[])
    return out


def main() -> None:
    rows, summary = [], Counter()
    for rep, dirname in REPS.items():
        for f in sorted(glob.glob(os.path.join("er052_output", dirname, "instances_s*", "*.json"))):
            d = json.load(open(f, encoding="utf-8"))
            sample = os.path.basename(os.path.dirname(f)).replace("instances_", "")
            iid = d["instance_id"]
            text0 = INSTANCES[iid]["fixture"]["article_text"]
            texts = text_chain(d, text0) if d["cycles"] else [text0, text0]
            row = {"rep": rep, "sample": sample, "instance_id": iid, "group": d.get("group"),
                   "legacy_final_state": d["final_state"], "legacy_stage4_reason": d.get("stage4_reason"),
                   "legacy_cycles": len(d["cycles"])}
            row.update(deterministic_counters(d, texts) if d["cycles"] else {"counters": {}, "flagged": []})
            for k_, v_ in row["counters"].items():
                summary[k_] += v_
            summary["runs"] += 1
            if d["final_state"] == "STAGE4_ESCALATION":
                row["new_route"] = route_stage4(d, texts)
                summary["legacy_stage4"] += 1
                summary["stage4_rerouted"] += 1
                if row["new_route"].get("terminal_allowed") is False:
                    summary["deterministic_terminal_outside_allowlist"] += 1
                if row["new_route"].get("deterministic"):
                    summary["deterministic_terminal"] += 1
                else:
                    summary["needs_llm_call"] += 1
            rows.append(row)
    out = {"summary": dict(summary), "allowed_reasons": sorted(ALLOWED), "rows": rows,
           "note": "決定論部分のみ。LLM callが必要な分岐は'call必要'として件数化(結果は推測しない)。"}
    json.dump(out, open(os.path.join(OUT_DIR, "replay_counterfactual_rep27_29_01.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    # md
    lines = ["# 反実仮想replay rep27〜29(¥0、決定論部分、委任_11)", "",
             f"- 対象: rep27/28/29の全run {summary['runs']}件(各38 run)。legacy STAGE4={summary['legacy_stage4']}件(rep27=3/rep28=3/rep29=3)",
             f"- **許可リスト外STAGE4(決定論部分で確定した終端が許可リスト外): {summary['deterministic_terminal_outside_allowlist']}件**",
             f"- 決定論で終端が確定: {summary['deterministic_terminal']}件 / LLM call必要: {summary['needs_llm_call']}件",
             f"- 非STAGE4の周回でも新ロジックが介入しうる箇所(記録からの決定論カウント): {json.dumps({k: v for k, v in summary.items() if k in ('bprime_location_carry', 'pin_would_override_nonblocking', 'a2_revert_would_reject')}, ensure_ascii=False)}",
             "", "## legacy STAGE4 9件の新経路", "",
             "| rep | sample | instance | legacy reason | 新経路 | 終端(決定論部分) | 必要call |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        if "new_route" in r:
            n = r["new_route"]
            lines.append(f"| {r['rep']} | {r['sample']} | {r['instance_id']} | {n['legacy_reason']} | {n['route']} | {n['terminal']} | {', '.join(n['calls_needed']) or '-'} |")
    lines += ["", "## 新ロジックが介入しうる周回(B′/A2/BLOCKING固定、記録からの決定論カウント)", ""]
    for r in rows:
        if r["flagged"]:
            lines.append(f"- rep{r['rep']} {r['sample']} {r['instance_id']}: " + json.dumps(r["flagged"], ensure_ascii=False)[:600])
    open(os.path.join(OUT_DIR, "replay_counterfactual_rep27_29_01.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(json.dumps(out["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
