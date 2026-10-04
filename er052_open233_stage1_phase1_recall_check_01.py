# -*- coding: utf-8 -*-
# er052_open233_stage1_phase1_recall_check_01.py
# OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01 委任_04c 作業5 (K14 Phase 1、DEV/Trial専用、Production非接続)
# 候補Stage1(V4A+重大誤解原則+列挙instruction+schema追加、昇格ルール除く=severityのみ)をgpt-6-luna n=2で新規実行し、
# Production V0記録出力(er050 step1/2の gpt-5.6-luna run_1 or fixture baseline_parsed)とclaim単位で比較する。
# runner/er051本体は変更しない(importのみ。runnerのcheck_budget/record_callはfixed budget file書込を避けるためruntimeでno-op化)。
import argparse
import json
import os
import re
import time

from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI  # noqa: E402

import er050_gpt6_checker_comparison_trial_01 as g6  # noqa: E402
import er051_open233_checker_trial_variant_01 as trial  # noqa: E402
import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402
import er052_open233_self_recovery_phase1_step3_stage1_compare_01 as step3cmp  # noqa: E402

OUT = "er052_output/open233_stage1_phase1_recall_check_01"
runner.check_budget = lambda state: None
runner.record_call = lambda *a, **k: None
NEG_IDS = ["neg1_meta_b3prod_a2", "neg2_meta_refresh_a2", "neg3_hormuz_prodrunner_b1b"]
PRIORITY = ["bgroup_B3", "bgroup_B4", "safety_A2A3", "safety_A4", "safety_A5", "bgroup_B2_hormuz"]


def instances():
    d = {}
    for fx in g6.step1_fixtures():
        d["safety_" + fx["id"]] = (fx, "er050_output/gpt6_checker_comparison_trial_01/step1/%s/gpt-5.6-luna/run_1.json" % fx["id"])
    for fx in g6.step2_fixtures():
        if fx["id"] in ("B2_hormuz", "B3", "B4"):
            d["bgroup_" + fx["id"]] = (fx, "er050_output/gpt6_checker_comparison_trial_01/step2/%s/gpt-5.6-luna/run_1.json" % fx["id"])
    for fid, p in step3cmp.NEGATIVE_SOURCE_FILES:
        if fid in NEG_IDS:
            d[fid] = (step3cmp.load_negative_fixture(fid, p), None)
    order = PRIORITY + [k for k in d if k not in PRIORITY]
    return {k: d[k] for k in order}


def v0_record(fx, path):
    # 優先: fixtureのbaseline_parsed(実Production V0記録)。無ければer050 step1/2のgpt-5.6-luna Production prompt run_1
    if fx.get("baseline_parsed"):
        return fx["baseline_parsed"], "fixture.baseline_parsed"
    if path and os.path.exists(path):
        x = json.load(open(path, encoding="utf8"))
        if x.get("parsed"):
            return x["parsed"], path
    return fx.get("baseline_parsed"), "fixture.baseline_parsed"


def run(n, budget, hard_mult):
    client = OpenAI()
    os.makedirs(OUT, exist_ok=True)
    total = 0.0
    warned = False
    for k, (fx, _) in instances().items():
        for i in range(1, n + 1):
            f = "%s/%s/run_%d.json" % (OUT, k, i)
            if os.path.exists(f):
                total += json.load(open(f, encoding="utf8")).get("cost_jpy", 0.0)
                continue
            if total >= budget * hard_mult:
                print("HARD STOP guardrail", total)
                return
            call_log, state = [], {}
            t0 = time.time()
            parsed = runner.stage1_fresh_with_enumeration(
                client, state, [0], call_log, "%s_p1_%d" % (k, i), fx,
                developer_message=trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE)
            cost = sum(c.get("cost_jpy", 0.0) for c in call_log)
            total += cost
            os.makedirs(os.path.dirname(f), exist_ok=True)
            json.dump({"instance": k, "run": i, "model": runner.MODEL, "parsed": parsed, "call_log": call_log,
                       "cost_jpy": cost, "elapsed": round(time.time() - t0, 2)},
                      open(f, "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)
            print(k, i, round(cost, 4), "cum", round(total, 3), "api_failure" if parsed.get("_stage1_api_failure") else "")
            if total >= budget and not warned:
                print("NOTE: guardrail", budget, "reached (not auto-stop)")
                warned = True


def norm(s):
    return set(re.findall(r"[a-z0-9%$.]+", (s or "").lower()))


def same_claim(a, b):
    # claim本文のtoken重なり(小さい側の50%以上)。related_fact_idは判定に使わない(V0のer009合成fixtureはfact id無し、
    # 候補は同一claimに別fact idを付けることがある)。V0 claimが非英語(ASCII token<3、JA原文)の場合は、
    # 同instance内の候補MAJORが1件以上あれば一致扱い(instance単位の緩い照合、報告で明記)。
    x, y = norm(a.get("claim_in_article")), norm(b.get("claim_in_article"))
    if len(x) < 3:
        return bool(y)
    return bool(y) and len(x & y) / min(len(x), len(y)) >= 0.5


def majors(parsed):
    return [d for d in (parsed or {}).get("deviations", []) if d.get("severity") == "MAJOR"]


def sc_match(inst, dev):
    # Safety-critical claim照合: text_pattern(あれば)またはtext_substringがclaim本文に含まれるか(related_fact_idは見ない)
    for d in runner.SAFETY_CRITICAL_CLAIM_DEFS.get(inst, []):
        if d.get("expected", "BLOCKING") != "BLOCKING":
            continue
        c = dev.get("claim_in_article") or ""
        if d.get("text_pattern"):
            ok = re.search(d["text_pattern"], c, re.IGNORECASE) is not None
        else:
            ok = d["text_substring"].lower() in c.lower()
        if ok:
            return d["sub_id"]
    return None


def agg(n):
    S = {"inferior": [], "cand_only": [], "both": [], "neither_instances": [], "sc": {}, "neg": {}, "cost_jpy": 0.0, "n_runs": 0,
         "api_failures": 0}
    for k, (fx, vp) in instances().items():
        runs = []
        for i in range(1, n + 1):
            f = "%s/%s/run_%d.json" % (OUT, k, i)
            if os.path.exists(f):
                x = json.load(open(f, encoding="utf8"))
                runs.append(x)
                S["cost_jpy"] += x["cost_jpy"]
                S["n_runs"] += 1
                S["api_failures"] += 1 if x["parsed"].get("_stage1_api_failure") else 0
        if not runs:
            continue
        v0, _ = v0_record(fx, vp)
        v0m = majors(v0)
        cand_all = [(r["run"], d) for r in runs for d in majors(r["parsed"])]
        for d0 in v0m:
            hits = sorted({r for r, d in cand_all if same_claim(d0, d)})
            rec = {"instance": k, "claim": d0.get("claim_in_article"), "fact": d0.get("related_fact_id"),
                   "cand_hits": "%d/%d" % (len(hits), len(runs))}
            (S["inferior"] if not hits else S["both"]).append(rec)
        seen = []
        for r, d in cand_all:
            if any(same_claim(d, d0) for d0 in v0m) or any(same_claim(d, s) for s in seen):
                continue
            seen.append(d)
            hits = sorted({r2 for r2, d2 in cand_all if same_claim(d, d2)})
            S["cand_only"].append({"instance": k, "claim": d.get("claim_in_article"), "fact": d.get("related_fact_id"),
                                   "cand_hits": "%d/%d" % (len(hits), len(runs))})
        if not v0m and not cand_all:
            S["neither_instances"].append(k)
        for d in runner.SAFETY_CRITICAL_CLAIM_DEFS.get(k, []):
            if d.get("expected", "BLOCKING") != "BLOCKING":
                continue
            v0hit = any(sc_match(k, x) == d["sub_id"] for x in v0m)
            ch = sum(any(sc_match(k, x) == d["sub_id"] for x in majors(r["parsed"])) for r in runs)
            S["sc"][d["sub_id"]] = {"instance": k, "v0": v0hit, "cand": "%d/%d" % (ch, len(runs))}
        if k in NEG_IDS:
            S["neg"][k] = {"cand_major_runs": sum(bool(majors(r["parsed"])) for r in runs), "runs": len(runs),
                           "claims": [d.get("claim_in_article") for r in runs for d in majors(r["parsed"])]}
    S["cost_jpy"] = round(S["cost_jpy"], 4)
    S["verdict"] = "K14_ABSORBABLE (inferior 0)" if not S["inferior"] else "K14_USER_DECISION (inferior %d)" % len(S["inferior"])
    json.dump(S, open(OUT + "/agg_phase1.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: (v if k not in ("inferior", "cand_only", "both") else len(v)) for k, v in S.items()},
                     ensure_ascii=False, indent=1))
    for r in S["inferior"]:
        print("INFERIOR:", r)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="run", choices=["run", "agg"])
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--budget-jpy", type=float, default=8.0)
    ap.add_argument("--hard-mult", type=float, default=1.6)
    a = ap.parse_args()
    if a.stage == "run":
        run(a.n, a.budget_jpy, a.hard_mult)
    else:
        agg(a.n)
