# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_53 作業3: Checker違反箇所の出力形式の限定確認(Trial専用、Checker呼び出しのみ)。

目的: ユーザー確認項目5つ(特定不能率/検出漏れ/false PASS/Human Review/コスト)を、対照(現行形式=`claim_in_article`
単一文字列)と処置(`CHECKER_SPANS_MODE="violation_spans"`、配列)で、同じ記事・同じLedger・同時期に比べる。
**flowは回さない**(Stage 2・Rewrite・Recheckの周回は呼ばない。Stage 1相当のChecker呼び出しだけ)。Production正式path
(er003等)は編集しない(runnerのimportのみ)。判定基準・モデル・effortはrunnerの現行Stage 1と同一(runnerの関数をそのまま呼ぶ)。

腕:
- 対照(ctl): runner.stage1_fresh_with_enumeration(V4A + 重大誤解原則のdeveloper message、prior_issuesなし)、CHECKER_SPANS_MODE=legacy。
- 処置(trt): 同じ呼び出しで、呼び出し中だけ CHECKER_SPANS_MODE=violation_spans(schemaは`violation_spans`、Prompt追記あり)。

予算stateは専用ファイル(本ディレクトリのbudget_state_spans_compare_01.json)。runner.BUDGET_STATE_PATH・TOTAL_BUDGET_JPYを
本スクリプト内で差し替えるため、既存の証跡ファイルを上書きしない。
実行: --stage probe(1記事×2腕×1回)→ --stage main(残り)→ --stage agg(オフライン集計、¥0)。
"""
import argparse
import csv
import itertools
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "er052_output", "open233_checker_spans_format_compare_01")
CALLS = os.path.join(OUT, "calls")
BUDGET_PATH = os.path.join(OUT, "budget_state_spans_compare_01.json")

import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402
import er051_open233_checker_trial_variant_01 as trial  # noqa: E402
import er052_open233_self_recovery_stage2_production_01 as s2p  # noqa: E402

runner.BUDGET_STATE_PATH = BUDGET_PATH
runner.TOTAL_BUDGET_JPY = 30.0

# 記事(既存fixtureのcycle1の本文・Ledger・日本語原文)。BLOCKING対象のfact_id集合は、design_open233_self_recovery_flow_01.md
# §7(7-0-iter4の現行ラベル)をrunnerの`SAFETY_CRITICAL_CLAIM_DEFS`(正本定義)とStage 1固定出力で具体化したもの。
# - hormuz_run03_standard: HF-009(Brent先物→市場全体の一般化、BLOCKING)
# - neg1_meta_b3prod_a2: 正常記事(Normal群、BLOCKING対象なし。検出漏れ・false PASSの分母に入れない)
# - bgroup_B4: B4-a=MUSE-HC-002(BLOCKING)。B4-b/c/dはQUALITY扱い(対象外)
# - safety_A4: A4-0=MUSE-HC-006、A4-1=MUSE-HC-012(BLOCKING)
# - meta_run03_standard: Meta-2=MUSE-HC-012(BLOCKING)。Meta-1=MUSE-HC-010はユーザー決定(2026-10-03)で軽微のため
#   BLOCKING対象から除外し、参考として別に数える
# - safety_er009_changed_number: Safety対照(合成改竄、changed_number、BLOCKING)。fact_idが付かないため、MAJORが
#   1件でも出れば検出(記事は1文のみ)
ARTICLES = {
    "hormuz_run03_standard": {"blocking": ["HF-009"], "reference": [], "kind": "problem"},
    "neg1_meta_b3prod_a2": {"blocking": [], "reference": [], "kind": "problem_normal"},
    "bgroup_B4": {"blocking": ["MUSE-HC-002"], "reference": [], "kind": "problem"},
    "safety_A4": {"blocking": ["MUSE-HC-006", "MUSE-HC-012"], "reference": [], "kind": "problem"},
    "meta_run03_standard": {"blocking": ["MUSE-HC-012"], "reference": ["MUSE-HC-010"], "kind": "multi_span"},
    "safety_er009_changed_number": {"blocking": ["*ANY_MAJOR*"], "reference": [], "kind": "safety_control"},
}
ARMS = ("ctl", "trt")
PROBE_ARTICLE = "bgroup_B4"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def get_fixtures():
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    return {a: insts[a]["fixture"] for a in ARTICLES}


class RecClient:
    """実クライアントのラッパー(生の応答の記録用)。"""

    def __init__(self, real):
        self._real = real
        self.last = None
        outer = self

        class _R:
            @staticmethod
            def create(**kw):
                resp = real.responses.create(**kw)
                outer.last = {"output_text": getattr(resp, "output_text", None), "usage": s2p._extract_usage(resp),
                              "prompt": kw["input"][-1]["content"], "developer": kw["input"][0]["content"]}
                return resp

        self.responses = _R


def call_path(art, arm, k):
    return os.path.join(CALLS, f"{art}__{arm}__{k}.json")


def done(art, arm, k):
    return os.path.exists(call_path(art, arm, k))


def call_one(rc, state, ce, art, arm, k, fx):
    label = f"sc01_{art}_{arm}_{k}"
    fixture = {"ledger_text": fx["ledger_text"], "article_text": fx["article_text"],
               "source_article_text": fx.get("source_article_text")}
    call_log = []
    rc.last = None
    t0 = time.time()
    err, parsed = None, None
    prev_mode = runner.CHECKER_SPANS_MODE
    runner.CHECKER_SPANS_MODE = (runner.CHECKER_SPANS_MODE_VIOLATION_SPANS if arm == "trt"
                                 else runner.CHECKER_SPANS_MODE_LEGACY)
    try:
        parsed = runner.stage1_fresh_with_enumeration(
            rc, state, ce, call_log, label, fixture,
            developer_message=trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE)
    except runner.TrialAbort:
        raise
    except Exception as e:  # noqa: BLE001  (JSON/schema失敗など。応答が得られていれば費用は計上する)
        err = f"{type(e).__name__}: {e}"
        if rc.last is not None:
            cost = round(s2p.official_cost_jpy(rc.last["usage"]), 4)
            state["cumulative_jpy"] += cost
            state["cumulative_calls"] += 1
            state["cumulative_errors"] += 1
            state["history"].append({"label": label, "cost_jpy": cost, "recovery_stage": "sc01_parse_failure",
                                      "usage": rc.last["usage"]})
            runner.save_budget_state(state)
    finally:
        runner.CHECKER_SPANS_MODE = prev_mode
    if parsed is not None and parsed.get("_stage1_api_failure"):
        err = "api_failure"
    last = rc.last or {}
    raw_devs = []
    try:
        raw_devs = json.loads(last.get("output_text") or "{}").get("deviations", [])
    except Exception:  # noqa: BLE001
        pass
    cost = round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4) or (
        round(s2p.official_cost_jpy(last["usage"]), 4) if last.get("usage") else 0.0)
    rec = {"article": art, "arm": arm, "k": k, "label": label, "model": runner.MODEL, "error": err,
           "cost_jpy": cost, "usage": last.get("usage"), "elapsed_seconds": round(time.time() - t0, 3),
           "prompt_sha256": s2p.sha256_text(last["prompt"]) if last.get("prompt") else None,
           "raw_output_text": last.get("output_text"), "raw_model_deviations": raw_devs,
           "final_deviations": ([dict(d) for d in parsed.get("deviations", [])] if parsed else None),
           "overall_status": parsed.get("overall_status") if parsed else None}
    os.makedirs(CALLS, exist_ok=True)
    with open(call_path(art, arm, k), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    return rec


def load_state():
    if os.path.exists(BUDGET_PATH):
        return load(BUDGET_PATH)
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


# ------------------------------------------------------------ 集計(オフライン、¥0)
def resolve_for(arm, dev, fx, ja_mode):
    """受け取り側の照合(VS_MATCH_EXT=ON)。処置腕は配列経路(registryを再構築してから)、対照腕は単一文字列。"""
    en = fx["article_text"]
    ja = fx.get("source_article_text") if ja_mode == "paired" else None
    prev = runner.CHECKER_SPANS_MODE
    runner.CHECKER_SPANS_MODE = (runner.CHECKER_SPANS_MODE_VIOLATION_SPANS if arm == "trt"
                                 else runner.CHECKER_SPANS_MODE_LEGACY)
    try:
        if arm == "trt" and isinstance(dev.get("violation_spans"), list):
            d2 = runner.assemble_claim_from_violation_spans(dev)
            return runner.resolve_violation_spans(d2["claim_in_article"], en, ja)
        return runner.resolve_violation_spans(dev.get("claim_in_article") or "", en, ja)
    finally:
        runner.CHECKER_SPANS_MODE = prev


def is_primary(d):
    return not d.get("detected_by_enumeration")


def aggregate():
    fxs = get_fixtures()
    runner.VS_MATCH_EXT = True
    recs = []
    for fn in sorted(os.listdir(CALLS)):
        recs.append(load(os.path.join(CALLS, fn)))
    rows = []
    detail = []
    for r in recs:
        art, arm = r["article"], r["arm"]
        fx = fxs[art]
        spec = ARTICLES[art]
        failed = bool(r.get("error"))
        devs = r.get("final_deviations") or []
        majors = [d for d in devs if d.get("severity") == "MAJOR"]
        majors_primary = [d for d in majors if is_primary(d)]
        usage = r.get("usage") or {}
        row = {"article": art, "arm": arm, "k": r["k"], "failed": failed, "error": r.get("error"),
               "cost_jpy": r.get("cost_jpy"), "output_tokens": usage.get("output_tokens"),
               "reasoning_tokens": usage.get("reasoning_tokens"), "input_tokens": usage.get("input_tokens"),
               "n_deviations": len(devs), "n_major": len(majors), "n_major_primary": len(majors_primary),
               "n_minor": sum(1 for d in devs if d.get("severity") == "MINOR")}
        # 特定不能(paired=現行の既定、english_only=参考)
        for mode in ("paired", "english_only"):
            unv_p = unv_all = 0
            for d in majors:
                res = resolve_for(arm, d, fx, mode)
                ok = res["status"] == "resolved"
                if not ok:
                    unv_all += 1
                    if is_primary(d):
                        unv_p += 1
                if mode == "paired":
                    detail.append({"article": art, "arm": arm, "k": r["k"], "primary": is_primary(d),
                                   "fact_id": d.get("related_fact_id"), "status": res["status"],
                                   "reason": res.get("reason"), "reason_detail": res.get("reason_detail"),
                                   "claim": d.get("claim_in_article"),
                                   "array_elements": res.get("array_elements")})
            row[f"unverified_primary_{mode}"] = unv_p
            row[f"unverified_all_major_{mode}"] = unv_all
        # 検出(fact_id単位)
        fact_set = {d.get("related_fact_id") for d in majors if d.get("related_fact_id")}
        row["major_fact_ids"] = sorted(fact_set)
        blk = spec["blocking"]
        if blk == ["*ANY_MAJOR*"]:
            row["blocking_total"], row["blocking_detected"] = 1, (1 if majors else 0)
        else:
            row["blocking_total"], row["blocking_detected"] = len(blk), sum(1 for f in blk if f in fact_set)
        row["reference_total"], row["reference_detected"] = len(spec["reference"]), sum(
            1 for f in spec["reference"] if f in fact_set)
        row["false_pass"] = bool(blk) and (not failed) and (len(majors) == 0)
        # 出力失敗(処置腕のみ意味がある項目)
        raw_devs = r.get("raw_model_deviations") or []
        row["major_with_empty_spans"] = sum(1 for d in raw_devs if d.get("severity") == "MAJOR"
                                            and isinstance(d.get("violation_spans"), list)
                                            and not [s for s in d["violation_spans"] if (s or "").strip()])
        non_verbatim = 0
        n_elems = 0
        elem_lens = []
        for d in raw_devs:
            for s in (d.get("violation_spans") or []):
                n_elems += 1
                elem_lens.append(len((s or "").strip()))
                if (s or "").strip() not in fx["article_text"]:
                    non_verbatim += 1
        row["array_elements_total"], row["array_elements_non_verbatim"] = n_elems, non_verbatim
        row["array_element_mean_len"] = round(sum(elem_lens) / len(elem_lens), 1) if elem_lens else None
        # 対照腕: 単一文字列の説明文混入(記事に逐語で存在しない、かつ照合で確定不能)
        rows.append(row)

    def arm_rows(arm):
        return [r for r in rows if r["arm"] == arm and not r["failed"]]

    def rate(n, d):
        return None if not d else round(n / d, 4)

    summary = {}
    for arm in ARMS:
        rs = arm_rows(arm)
        for mode in ("paired", "english_only"):
            pass
        n_major_primary = sum(r["n_major_primary"] for r in rs)
        n_major_all = sum(r["n_major"] for r in rs)
        det_rows = [r for r in rs if r["blocking_total"] > 0]
        det_n = sum(r["blocking_total"] for r in det_rows)
        det_d = sum(r["blocking_detected"] for r in det_rows)
        ref_rows = [r for r in rs if r["reference_total"] > 0]
        costs = [r["cost_jpy"] for r in rs if r["cost_jpy"] is not None]
        otoks = [r["output_tokens"] for r in rs if r["output_tokens"] is not None]
        summary[arm] = {
            "calls": len(rs), "failed_calls": sum(1 for r in rows if r["arm"] == arm and r["failed"]),
            "major_primary_total": n_major_primary, "major_all_total(same_fact展開含む)": n_major_all,
            "1_unverified_rate_primary_paired": rate(sum(r["unverified_primary_paired"] for r in rs), n_major_primary),
            "1_unverified_primary_paired": sum(r["unverified_primary_paired"] for r in rs),
            "1_unverified_rate_primary_english_only": rate(sum(r["unverified_primary_english_only"] for r in rs),
                                                           n_major_primary),
            "1_unverified_rate_all_major_paired": rate(sum(r["unverified_all_major_paired"] for r in rs), n_major_all),
            "2_blocking_facts_detected": f"{det_d}/{det_n}", "2_detection_rate": rate(det_d, det_n),
            "2_reference_MUSE-HC-010_detected": f"{sum(r['reference_detected'] for r in ref_rows)}/{sum(r['reference_total'] for r in ref_rows)}",
            "3_false_pass_calls": f"{sum(1 for r in det_rows if r['false_pass'])}/{len(det_rows)}",
            "3_false_pass_rate": rate(sum(1 for r in det_rows if r["false_pass"]), len(det_rows)),
            "4_human_review_calls(確定不能のMAJORを含む呼び出し)": f"{sum(1 for r in rs if r['unverified_primary_paired'] > 0)}/{len(rs)}",
            "4_human_review_unverified_majors_per_call": rate(sum(r['unverified_primary_paired'] for r in rs), len(rs)),
            "5_cost_jpy_mean": round(sum(costs) / len(costs), 4) if costs else None,
            "5_cost_jpy_min_max": [min(costs), max(costs)] if costs else None,
            "5_cost_jpy_total": round(sum(costs), 4),
            "5_output_tokens_mean": round(sum(otoks) / len(otoks), 1) if otoks else None,
            "6_major_with_empty_spans": sum(r["major_with_empty_spans"] for r in rs),
            "6_array_elements_total": sum(r["array_elements_total"] for r in rs),
            "6_array_elements_non_verbatim(説明文・位置ラベル等)": sum(r["array_elements_non_verbatim"] for r in rs),
            "mean_n_major_per_call": rate(n_major_all, len(rs)),
        }
    # 処置腕の要素ごとの確定率(paired)
    elem = [e for d in detail if d["arm"] == "trt" and d["primary"] for e in (d.get("array_elements") or [])]
    summary["trt"]["1_element_level_resolved"] = f"{sum(1 for e in elem if e['status'] == 'resolved')}/{len(elem)}"
    summary["trt"]["1_element_level_resolved_rate"] = rate(sum(1 for e in elem if e["status"] == "resolved"), len(elem))
    summary["trt"]["1_unverified_reasons"] = dict(Counter(
        d["reason"] for d in detail if d["arm"] == "trt" and d["primary"] and d["status"] != "resolved"))
    summary["ctl"]["1_unverified_reasons"] = dict(Counter(
        d["reason"] for d in detail if d["arm"] == "ctl" and d["primary"] and d["status"] != "resolved"))

    # 7. 対照どうしの揺れ: fact_id単位の検出一致率(同じ記事の対照n回のペアについて、各fact_idが「MAJORで出たか」が一致する率)
    def pair_agreement(arm):
        agree = total = 0
        per_article = {}
        for art in ARTICLES:
            rs = [r for r in rows if r["arm"] == arm and r["article"] == art and not r["failed"]]
            facts = sorted({f for r in rs for f in r["major_fact_ids"]})
            a_n = t_n = 0
            for x, y in itertools.combinations(rs, 2):
                for f in facts:
                    t_n += 1
                    a_n += 1 if ((f in x["major_fact_ids"]) == (f in y["major_fact_ids"])) else 0
            per_article[art] = f"{a_n}/{t_n}" if t_n else "n/a(fact_id無し・または1回のみ)"
            agree += a_n
            total += t_n
        return {"agreement": f"{agree}/{total}", "rate": rate(agree, total), "per_article": per_article}

    wobble = {"ctl_internal": pair_agreement("ctl"), "trt_internal": pair_agreement("trt")}
    # 処置と対照の差(fact_id別の検出率の差、BLOCKING対象のみ)
    diff = {}
    for art, spec in ARTICLES.items():
        for f in spec["blocking"] + spec["reference"]:
            if f == "*ANY_MAJOR*":
                key = f"{art}:any_MAJOR"
                fn = (lambda r: 1 if r["n_major"] > 0 else 0)
            else:
                key = f"{art}:{f}" + ("(参考)" if f in spec["reference"] else "")
                fn = (lambda r, f=f: 1 if f in r["major_fact_ids"] else 0)
            c = [fn(r) for r in rows if r["arm"] == "ctl" and r["article"] == art and not r["failed"]]
            t = [fn(r) for r in rows if r["arm"] == "trt" and r["article"] == art and not r["failed"]]
            diff[key] = {"ctl": f"{sum(c)}/{len(c)}", "trt": f"{sum(t)}/{len(t)}",
                         "diff_rate_trt_minus_ctl": (round(sum(t) / len(t) - sum(c) / len(c), 3) if c and t else None)}
    # 記事別の指摘数(量の変化)
    per_article_counts = {}
    for art in ARTICLES:
        per_article_counts[art] = {
            arm: {"major_primary_per_call": [r["n_major_primary"] for r in rows if r["arm"] == arm and r["article"] == art],
                  "unverified_primary_per_call": [r["unverified_primary_paired"] for r in rows
                                                   if r["arm"] == arm and r["article"] == art]}
            for arm in ARMS}
    res = {"n_calls": len(recs), "total_cost_jpy": round(sum(r.get("cost_jpy") or 0 for r in recs), 4),
           "summary_by_arm": summary, "wobble_ctl_vs_trt_internal_agreement": wobble,
           "per_blocking_fact_detection": diff, "per_article_counts": per_article_counts,
           "ground_truth": ARTICLES,
           "caveat": "回数が少ない(1記事・1腕あたりn=2〜3、計6記事)ため、率は参考値。結論は書かない(判定はFable)。"
                     "照合はVS_MATCH_EXT=ONで、paired(EN・JA両方、現行の既定)を主、english_onlyを参考として併記。"}
    with open(os.path.join(OUT, "results_01.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "unverified_detail_01.json"), "w", encoding="utf-8") as f:
        json.dump([d for d in detail if d["status"] != "resolved"], f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "cases_01.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        cols = list(rows[0].keys()) if rows else []
        w.writerow(cols)
        for r in rows:
            w.writerow([json.dumps(r[c], ensure_ascii=False) if isinstance(r[c], (list, dict)) else r[c]
                        for c in cols])
    print(json.dumps(res, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["probe", "main", "agg"])
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--budget-jpy", type=float, default=30.0)
    a = ap.parse_args()
    os.makedirs(CALLS, exist_ok=True)
    if a.stage == "agg":
        aggregate()
        return
    runner.TOTAL_BUDGET_JPY = a.budget_jpy
    fxs = get_fixtures()
    state = load_state()
    ce = [0]
    rc = RecClient(runner.vfl01.get_client())
    if a.stage == "probe":
        for arm in ARMS:
            if not done(PROBE_ARTICLE, arm, 1):
                r = call_one(rc, state, ce, PROBE_ARTICLE, arm, 1, fxs[PROBE_ARTICLE])
                print(f"probe {PROBE_ARTICLE}/{arm}: cost=¥{r['cost_jpy']} err={r['error']} usage={r['usage']}")
        costs = {arm: load(call_path(PROBE_ARTICLE, arm, 1))["cost_jpy"] for arm in ARMS}
        for n in (3, 2):
            est = sum(costs[arm] * len(ARTICLES) * n for arm in ARMS)
            print(f"見込み n={n}: {len(ARTICLES) * 2 * n} call, 概算¥{est:.2f}(probe単価ベース)")
        print("累計(専用state): ¥%.4f" % state["cumulative_jpy"])
        return
    for k in range(1, a.n + 1):
        for art in ARTICLES:
            for arm in ARMS:
                if done(art, arm, k):
                    continue
                if state["cumulative_jpy"] >= a.budget_jpy:
                    print(f"予算¥{a.budget_jpy}到達のため停止(未実施のcallが残る)。")
                    print("累計(専用state): ¥%.4f" % state["cumulative_jpy"])
                    return
                r = call_one(rc, state, ce, art, arm, k, fxs[art])
                print(f"{art}/{arm}/{k}: cost=¥{r['cost_jpy']} err={r['error']} 累計¥{state['cumulative_jpy']:.3f}")
    print("累計(専用state): ¥%.4f" % state["cumulative_jpy"])


if __name__ == "__main__":
    main()
