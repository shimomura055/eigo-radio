# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_02 作業4(有料、上限¥45): Tier 1確認役(`runner.run_downgrade_verify_call`)のoffline replay。
# 入力: 既存instance JSON全体(`diag._iter_instances`)のChecker MAJOR→Stage 2最終非BLOCKING(降格)534件(記録済みの
#   claim・局所文脈・Checkerのissue/flags・Ledger[fixture])。母数・nは固定(増やさない)。
# 設計: 補助ベルト(Tier 0、既定のTIER0_G_L_ENABLED=False)に該当した行は確認役を呼ばずBLOCKING扱い(ただし流出10行+neg5 6行は
#   確認役の独立した判別力を見るため、補助ベルト該当でも呼ぶ)。NORMAL群のラベル付き正当降格と流出・neg5行はn=2(2回目は再現性確認)。
#   G_L有効時の反実仮想(Tier 0にG_Lを足した場合)は呼び出し結果の再集計だけで出す(追加費用なし)。
# 採否判定(Fable評価5、事前設定・事後変更しない): (ii)<=10%かつ(i)=100% → 採用 / (ii)10〜25% → 調整1回 / (ii)>25%または(i)<100% → 不採用。
#   主指標は1回目のcall(2回目は再現性確認、(vii))。流出・neg5が2回とも閉じた率も併記する(保守側の参考値)。
# 使い方: --stage probe(6件のみ、単価と母集団の費用概算を出す)→ --stage main --budget-jpy 45 → --stage agg(API呼び出しなし)。
import argparse
import collections
import concurrent.futures
import json
import os
import random
import sys
import threading
import time

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage2_b3_misdowngrade_diag_01 as diag

OUT = "er052_output/open233_kpi_recovery_02_offline_01"
CALLS_PATH = f"{OUT}/replay_verify_01_calls.jsonl"
SUMMARY_PATH = f"{OUT}/replay_verify_01_summary.json"
POP_PATH = f"{OUT}/replay_verify_01_population.json"
BUDGET_PATH = f"{OUT}/replay_verify_01_budget.json"
NEG5 = "neg5_hormuz_div_a2"
NORMAL = runner.NORMAL_GROUP_INSTANCE_IDS
WORKERS = 4
MAX_RETRIES = 2


def _base_iid(iid):
    return iid[:-3] if iid.endswith("_n2") else iid


def build_population():
    fx = {i["instance_id"]: i["fixture"]["ledger_text"] for i in runner.build_target_instances()}
    old_def_ids = {iid for iid in runner.SAFETY_CRITICAL_CLAIM_DEFS}
    rows = []
    for f, dname, d in diag._iter_instances():
        if dname.endswith("_rep26"):
            continue  # 母集団は委任_02より前の既存ログに固定(rep26の出力を含めない)
        rub = diag._rubric_of_dir(dname)
        iid = d["instance_id"]
        for c in d["cycles"]:
            cyc = c.get("cycle", 1)
            for idx, e in enumerate(c.get("stage2_results") or []):
                dev = e.get("dev") or {}
                if dev.get("severity") != "MAJOR" or e["materiality"] == "BLOCKING":
                    continue
                claim = e.get("claim_text") or ""
                fid = (e.get("related_fact_id") or "").strip()
                # 旧定義(委任_01まで)の流出: 手作業登録(registered_inなし)の定義との一致
                sub_old = None
                for df in runner._safety_critical_defs(iid):
                    if not df.get("registered_in") and df["related_fact_id"] == fid and df["text_substring"] in claim:
                        sub_old = df["sub_id"]
                neg5_same = iid == NEG5 and runner.normalized_same_as_labeled(claim, "bgroup_B3")
                ledger = fx.get(_base_iid(iid), "")
                block = runner.floor_verify_fact_block(ledger, fid)
                cl = {"claim_text": claim, "dev": dev}
                blocked_aux, reason_aux = runner.stage2_release_guard(cl, block)  # 既定: G_L無効=補助ベルトのみ
                gl, gl_reason = runner.g_l_guard(dev, block)
                group = ("leak_old" if sub_old else "neg5_same" if neg5_same
                         else "normal_legit" if (iid in NORMAL and iid != NEG5) else "other")
                rows.append({
                    "key": f"{f}|c{cyc}|i{idx}", "file": f, "dir": dname, "rubric": rub, "instance_id": iid, "cycle": cyc,
                    "claim": claim, "local_context": e.get("local_context") or "", "issue": dev.get("issue") or dev.get("explanation") or "",
                    "fid": fid, "fact_block_found": block is not None, "materiality": e["materiality"],
                    "llm_materiality": e.get("llm_materiality"), "group": group, "sub_old": sub_old,
                    "tier0_aux": blocked_aux, "tier0_aux_reason": reason_aux, "gl": gl, "gl_reason": gl_reason,
                    "two_of_two": bool(e.get("two_of_two_downgraded"))})
    return rows, fx


def plan_calls(rows, budget_jpy, unit_cost, shrink=False, seed=20261004):
    """[(row, rep)]。leak_old/neg5_sameは補助ベルト該当でも呼ぶ(n=2)。normal_legitはn=2。other/補助ベルト該当外のみ1回。"""
    calls = []
    others = [r for r in rows if r["group"] == "other" and not r["tier0_aux"]]
    if shrink:
        rnd = random.Random(seed)
        strata = collections.defaultdict(list)
        for r in others:
            strata[(r["materiality"], r["rubric"])].append(r)
        keep, quota = [], 200
        total = sum(len(v) for v in strata.values())
        for k in sorted(strata):
            n = max(1, round(quota * len(strata[k]) / total))
            keep += rnd.sample(strata[k], min(n, len(strata[k])))
        others = keep
    # 実行順(予算に達した場合に失う順): 流出・neg5(n=2) → NORMAL群1回目 → その他(層化サンプル)1回目 → NORMAL群2回目
    pri1 = [(r, k) for r in rows if r["group"] in ("leak_old", "neg5_same") for k in (1, 2)]
    pri2 = [(r, 1) for r in rows if r["group"] == "normal_legit" and not r["tier0_aux"]]
    other_ids = {r["key"] for r in others}
    pri3 = [(r, 1) for r in rows if r["group"] == "other" and r["key"] in other_ids]
    pri4 = [(r, 2) for r in rows if r["group"] == "normal_legit" and not r["tier0_aux"]]
    return pri1 + pri2 + pri3 + pri4


def load_calls():
    out = {}
    if os.path.exists(CALLS_PATH):
        for ln in open(CALLS_PATH, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                rec = json.loads(ln)
                out[(rec["key"], rec["rep"])] = rec
    return out


_lock = threading.Lock()


def do_call(client, fx, row, rep, state):
    ledger = fx.get(_base_iid(row["instance_id"]), "")
    block = runner.floor_verify_fact_block(ledger, row["fid"])
    rec = {"key": row["key"], "rep": rep, "instance_id": row["instance_id"], "group": row["group"], "ok": False}
    if block is None:
        rec.update(skipped="fact_block_unavailable", cost_jpy=0.0)
        return rec
    last = None
    for _ in range(1 + MAX_RETRIES):
        try:
            res = runner.run_downgrade_verify_call(client, row["claim"], row["local_context"], block, row["issue"], row["fid"])
            v = runner._dv_validate_call(res, block)
            rec.update(ok=True, verdict=v["verdict"], valid=v["valid"], invalid_reason=v["invalid_reason"],
                       citation_verbatim=v["citation_verbatim"], citation=v["ledger_citation"], basis=v["basis"],
                       explanation=v["explanation"], prompt_sha256=v["prompt_sha256"], cost_jpy=v["cost_jpy"],
                       usage=res.get("usage"))
            return rec
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    rec.update(error=last, cost_jpy=0.0)
    return rec


def run_calls(plan, fx, budget_jpy):
    client = vfl01.get_client()
    done = load_calls()
    todo = [(r, rep) for r, rep in plan if (r["key"], rep) not in done]
    state = {"cum": sum(x.get("cost_jpy") or 0.0 for x in done.values()), "errors": 0, "stop": None}
    print(f"to do {len(todo)} calls (already {len(done)}), cumulative so far JPY{state['cum']:.3f}, budget JPY{budget_jpy}", flush=True)

    def work(item):
        r, rep = item
        with _lock:
            if state["stop"] or state["cum"] >= budget_jpy:
                state["stop"] = state["stop"] or f"budget reached JPY{state['cum']:.3f}"
                return None
        rec = do_call(client, fx, r, rep, state)
        with _lock:
            state["cum"] += rec.get("cost_jpy") or 0.0
            if "error" in rec:
                state["errors"] += 1
                if state["errors"] >= 3:
                    state["stop"] = "3 API errors (STOP)"
            else:
                state["errors"] = 0
            with open(CALLS_PATH, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec
    with concurrent.futures.ThreadPoolExecutor(WORKERS) as ex:
        n = 0
        for rec in ex.map(work, todo):
            if rec is not None:
                n += 1
                if n % 50 == 0:
                    print(f"  {n}/{len(todo)} cum=JPY{state['cum']:.3f}", flush=True)
    json.dump({"cumulative_jpy": round(state["cum"], 4), "stop": state["stop"]}, open(BUDGET_PATH, "w", encoding="utf-8"))
    print("done; cumulative JPY%.4f stop=%s" % (state["cum"], state["stop"]), flush=True)
    return state


def stage_probe():
    rows, fx = build_population()
    groups = collections.Counter(r["group"] for r in rows)
    print("population:", len(rows), dict(groups), "aux-hit:", sum(1 for r in rows if r["tier0_aux"]),
          "fact_block_unavailable:", sum(1 for r in rows if not r["fact_block_found"]))
    json.dump([{k: v for k, v in r.items() if k not in ("local_context",)} for r in rows], open(POP_PATH, "w", encoding="utf-8"), ensure_ascii=False)
    pick = []
    for g in ("normal_legit", "normal_legit", "leak_old", "leak_old", "neg5_same", "other"):
        for r in rows:
            if r["group"] == g and r not in [p for p in pick] and r["fact_block_found"] and not (g == "other" and r["tier0_aux"]):
                if g == "leak_old" and any(p["sub_old"] == r["sub_old"] for p in pick if p["group"] == "leak_old"):
                    continue
                pick.append(r)
                break
    plan = [(r, 1) for r in pick]
    run_calls(plan, fx, 3.0)
    calls = load_calls()
    costs = [calls[(r["key"], 1)]["cost_jpy"] for r in pick if (r["key"], 1) in calls and calls[(r["key"], 1)].get("ok")]
    unit = sum(costs) / max(1, len(costs))
    full = plan_calls(rows, 45, unit)
    shrunk = plan_calls(rows, 45, unit, shrink=True)
    est = {"probe_calls": len(pick), "unit_cost_jpy_mean": round(unit, 4), "unit_cost_jpy_max": round(max(costs), 4) if costs else None,
           "planned_calls_full": len(full), "estimated_cost_full_jpy": round(len(full) * unit, 2),
           "planned_calls_shrunk": len(shrunk), "estimated_cost_shrunk_jpy": round(len(shrunk) * unit, 2)}
    print(json.dumps(est, ensure_ascii=False))
    for r in pick:
        c = calls.get((r["key"], 1)) or {}
        print(" ", r["group"], r["instance_id"], r["materiality"], "->", c.get("verdict"), "valid=%s" % c.get("valid"), "cost=%s" % c.get("cost_jpy"),
              "|", (r["claim"] or "")[:70].replace("\n", " "))
    json.dump(est, open(f"{OUT}/replay_verify_01_estimate.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def stage_main(budget_jpy):
    rows, fx = build_population()
    est = json.load(open(f"{OUT}/replay_verify_01_estimate.json", encoding="utf-8"))
    unit = est["unit_cost_jpy_mean"]
    full = plan_calls(rows, budget_jpy, unit)
    shrink = len(full) * unit > budget_jpy * 0.95
    plan = plan_calls(rows, budget_jpy, unit, shrink=shrink)
    print(f"planned {len(plan)} calls (full={len(full)}), est JPY{len(plan) * unit:.2f}, shrink={shrink}", flush=True)
    json.dump({"shrink": shrink, "n_planned": len(plan), "n_full": len(full), "unit_cost_estimate": unit,
               "shrink_reason": ("全件の概算が上限の95%超のため、NORMAL群正当降格全件+流出・neg5全件+その他は層化サンプル約200件へ縮小"
                                 if shrink else None)}, open(f"{OUT}/replay_verify_01_plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    run_calls(plan, fx, budget_jpy)


def blocking_outcome(row, call, g_l_on=False):
    """行のTier 0+Tier 1の最終結果: 'BLOCKING'/'RELEASE'/None(未実施)。"""
    if row["tier0_aux"] or (g_l_on and row["gl"]):
        return "BLOCKING", ("tier0_aux" if row["tier0_aux"] else "tier0_gl")
    if call is None:
        return None, "no_call"
    if call.get("skipped") == "fact_block_unavailable":
        return "BLOCKING", "fact_block_unavailable"
    if not call.get("ok"):
        return "BLOCKING", "api_failure"
    if not call.get("valid"):
        return "BLOCKING", call.get("invalid_reason") or "invalid"
    if call.get("verdict") != "RELEASE":
        return "BLOCKING", "upheld"
    return "RELEASE", "release"


def stage_agg():
    rows, fx = build_population()
    calls = load_calls()
    plan_info = json.load(open(f"{OUT}/replay_verify_01_plan.json", encoding="utf-8")) if os.path.exists(f"{OUT}/replay_verify_01_plan.json") else {}
    S = {"n_downgrades": len(rows), "groups": dict(collections.Counter(r["group"] for r in rows)),
         "plan": plan_info, "n_calls_recorded": len(calls)}

    def rate(rs, rep=1, g_l_on=False):
        res = [(r, blocking_outcome(r, calls.get((r["key"], rep)), g_l_on)) for r in rs]
        res = [(r, o) for r, o in res if o[0] is not None]
        n = len(res)
        b = sum(1 for r, o in res if o[0] == "BLOCKING")
        return {"n": n, "blocking": b, "rate": round(b / n, 4) if n else None,
                "reasons": dict(collections.Counter(o[1] for r, o in res if o[0] == "BLOCKING"))}
    for name, gl_on in (("main(Tier0=補助ベルトのみ)", False), ("counterfactual(Tier0にG_Lを追加)", True)):
        leak_old = [r for r in rows if r["group"] == "leak_old"]
        neg5s = [r for r in rows if r["group"] == "neg5_same"]
        leaks = leak_old + neg5s
        normal = [r for r in rows if r["group"] == "normal_legit"]
        legit = [r for r in rows if r["group"] in ("normal_legit", "other")]

        def both(rs):
            ok = 0
            for r in rs:
                o1 = blocking_outcome(r, calls.get((r["key"], 1)), gl_on)[0]
                o2 = blocking_outcome(r, calls.get((r["key"], 2)), gl_on)[0]
                if o1 == "BLOCKING" and (o2 in ("BLOCKING", None) or r["tier0_aux"]):
                    ok += 1
            return ok
        block = {
            "i_leak_closure_old10": rate(leak_old, 1, gl_on), "i_neg5_same6": rate(neg5s, 1, gl_on), "i_leaks16": rate(leaks, 1, gl_on),
            "i_leaks16_closed_in_both_calls": f"{both(leaks)}/{len(leaks)}",
            "ii_normal_legit": rate(normal, 1, gl_on), "ii_normal_legit_call2": rate(normal, 2, gl_on),
            "iii_all_downgrades": rate(rows, 1, gl_on), "iii_legit_only": rate(legit, 1, gl_on),
            "iv_by_materiality": {m: rate([r for r in legit if r["materiality"] == m], 1, gl_on) for m in ("QUALITY", "ACCEPTABLE")},
            "iv_by_rubric": {ru: rate([r for r in legit if r["rubric"] == ru], 1, gl_on) for ru in sorted({r["rubric"] for r in rows})},
            "iv_normal_by_materiality": {m: rate([r for r in normal if r["materiality"] == m], 1, gl_on) for m in ("QUALITY", "ACCEPTABLE")},
        }
        S[name] = block
    # (i)の開いた流出行(補助ベルト+確認役でBLOCKINGにならなかった行)
    S["open_leaks_main"] = [{"instance": r["instance_id"], "dir": r["dir"][-8:], "cycle": r["cycle"], "group": r["group"],
                             "verdict_call1": (calls.get((r["key"], 1)) or {}).get("verdict"),
                             "explanation": ((calls.get((r["key"], 1)) or {}).get("explanation") or "")[:200],
                             "claim": (r["claim"] or "")[:100]}
                            for r in rows if r["group"] in ("leak_old", "neg5_same")
                            and blocking_outcome(r, calls.get((r["key"], 1)))[0] != "BLOCKING"]
    # (v)(vi)(vii)
    called = [c for c in calls.values() if c.get("ok")]
    S["v_citation_not_verbatim"] = {"n_called_ok": len(called), "non_verbatim": sum(1 for c in called if not c.get("valid") and c.get("invalid_reason") == "ledger_citation_not_verbatim"),
                                    "rate": round(sum(1 for c in called if not c.get("valid")) / max(1, len(called)), 4)}
    errs = [c for c in calls.values() if "error" in c]
    S["api_failures"] = {"n": len(errs), "sample": [c.get("error") for c in errs[:3]]}
    S["fact_block_unavailable_rows"] = {"n": sum(1 for r in rows if not r["fact_block_found"]),
                                        "in_normal_legit": sum(1 for r in rows if not r["fact_block_found"] and r["group"] == "normal_legit")}
    costs = [c["cost_jpy"] for c in called]
    total = round(sum(c.get("cost_jpy") or 0.0 for c in calls.values()), 4)
    unit = (sum(costs) / len(costs)) if costs else 0.0
    rep24_rows = [r for r in rows if r["dir"].endswith("rep24")]
    rep24_runs = len({json.dumps([r["file"]]) for r in rep24_rows})
    import glob
    n_rep24_runs = len(glob.glob("er052_output/open233_self_recovery_flow_runner_01_rep24/instances_s*/*.json"))
    targets_per_run = len(rep24_rows) / max(1, n_rep24_runs)
    legit_block_rate = S["main(Tier0=補助ベルトのみ)"]["iii_legit_only"]["rate"] or 0.0
    S["vi_cost"] = {"total_replay_jpy": total, "unit_call_jpy": round(unit, 4),
                    "rep24_downgrade_targets_per_instance_run": round(targets_per_run, 3),
                    "added_verify_cost_per_article_jpy(推定=targets×単価)": round(targets_per_run * unit, 4),
                    "added_rewrite_cost_per_article_jpy(推定=targets×legit_BLOCKING率×Rewrite1回¥0.8[Opus#11推定上限])": round(targets_per_run * legit_block_rate * 0.8, 4),
                    "note": "Rewriteの追加費用は推定(実測はrep26)。KPI: 平均+¥2/記事以内・Cap+¥3以内"}
    agree = []
    for r in rows:
        if r["group"] in ("leak_old", "neg5_same", "normal_legit") and (r["key"], 1) in calls and (r["key"], 2) in calls:
            o1 = blocking_outcome(r, calls[(r["key"], 1)])[0]
            o2 = blocking_outcome(r, calls[(r["key"], 2)])[0]
            agree.append(o1 == o2)
    S["vii_n2_agreement"] = {"pairs": len(agree), "agree": sum(agree), "rate": round(sum(agree) / len(agree), 4) if agree else None}
    # 採否判定(Fable評価5、事前設定)
    main = S["main(Tier0=補助ベルトのみ)"]
    closed = main["i_leaks16"]
    i_ok = closed["n"] > 0 and closed["blocking"] == closed["n"]
    ii = main["ii_normal_legit"]["rate"]
    if i_ok and ii is not None and ii <= 0.10:
        decision = "採用して限定確認(rep26)へ"
    elif ii is not None and 0.10 < ii <= 0.25 and i_ok:
        decision = "調整1回(Tier 0語彙/prompt表現の明確化のみ、対象限定で再replay)"
    elif (ii is not None and ii > 0.25) or not i_ok:
        decision = "採用せずFableへ報告(KPI緩和は提案しない)"
    else:
        decision = "データ不足(判定不能)"
    if ii is not None and 0.10 < ii <= 0.25 and not i_ok:
        decision = "採用せずFableへ報告(KPI緩和は提案しない): (i)<100%"
    S["decision"] = {"rule": "(ii)<=10%かつ(i)=100%→採用 / (ii)10〜25%(かつ(i)=100%)→調整1回 / (ii)>25%または(i)<100%→不採用",
                     "i_leaks16_closed": f"{closed['blocking']}/{closed['n']}", "ii_normal_legit_blocking_rate": ii, "decision": decision}
    json.dump(S, open(SUMMARY_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(S, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["probe", "main", "agg"])
    ap.add_argument("--budget-jpy", type=float, default=45.0)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if args.stage == "probe":
        stage_probe()
    elif args.stage == "main":
        stage_main(args.budget_jpy)
    else:
        stage_agg()


if __name__ == "__main__":
    main()
