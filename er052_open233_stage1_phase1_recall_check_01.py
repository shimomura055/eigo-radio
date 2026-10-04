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
import er003_v1_en_direct_vfl_01_generate as vfl01  # noqa: E402  (委任_05: V0 variantはProduction run_deviation_checkをそのまま呼ぶ)
import hashlib  # noqa: E402

OUT_BASE = "er052_output/open233_stage1_phase1_recall_check_01"
OUT = OUT_BASE
ONLY = []  # 委任_08: --onlyで対象instanceを限定(1/2補完用)
# 委任_05: model別単価($/1M tok in/cached/out、gpt-6-luna=s2p PRICE、gpt-5.6-luna=er050 REF)
RATES = {"gpt-6-luna": (0.10, 0.01, 0.50), "gpt-5.6-luna": (0.20, 0.02, 1.20)}
USD_JPY = 156.88


def cost_for(model, usage):
    ri, rc, ro = RATES[model]
    it, ct, ot = usage.get("input_tokens") or 0, usage.get("cached_input_tokens") or 0, usage.get("output_tokens") or 0
    return (max(it - ct, 0) / 1e6 * ri + ct / 1e6 * rc + ot / 1e6 * ro) * USD_JPY
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


A_TARGETS = ["bgroup_B3", "bgroup_B4", "safety_A2A3", "safety_A4", "safety_A5",  # Safety-critical群
             "bgroup_B2_hormuz", "bgroup_B1", "neg5_hormuz_div_a2", "meta_run03_standard",  # B群(+neg5 B3-same、meta標準)
             "neg1_meta_b3prod_a2", "neg2_meta_refresh_a2", "neg3_hormuz_prodrunner_b1b",  # 負例
             "hormuz_run03_advanced", "meta_run03_advanced", "hormuz_run02_advanced"]  # NORMAL群3
A_SC_INST = ["bgroup_B3", "bgroup_B4", "safety_A2A3", "safety_A4", "safety_A5"]
A_NEG = A_TARGETS[9:]
REP30 = "er052_output/open233_self_recovery_flow_runner_01_rep30"


def instances_a():
    ti = {i["instance_id"]: i for i in runner.build_target_instances()}
    return {k: (ti[k]["fixture"], ti[k].get("stage1_source")) for k in A_TARGETS}


def rep30_stage1(inst):
    # rep30が実際に使ったStage 1出力(frozen/V0差替え/fresh)= all_deviations_raw.stage1。s1/s2の存在するrun分(list)
    out = []
    for s in (1, 2):
        f = "%s/instances_s%d/%s.json" % (REP30, s, inst)
        if os.path.exists(f):
            out.append(json.load(open(f, encoding="utf8"))["all_deviations_raw"]["stage1"])
    return out


def v0_record(fx, path):
    # 優先: fixtureのbaseline_parsed(実Production V0記録)。無ければer050 step1/2のgpt-5.6-luna Production prompt run_1
    if fx.get("baseline_parsed"):
        return fx["baseline_parsed"], "fixture.baseline_parsed"
    if path and os.path.exists(path):
        x = json.load(open(path, encoding="utf8"))
        if x.get("parsed"):
            return x["parsed"], path
    return fx.get("baseline_parsed"), "fixture.baseline_parsed"


def run(n, budget, hard_mult, variant="candidate", model="gpt-6-luna"):
    client = OpenAI()
    os.makedirs(OUT, exist_ok=True)
    total = 0.0
    warned = False
    for k, (fx, _) in (instances_a() if variant == "a_frozen_config" else instances()).items():
        if ONLY and k not in ONLY:
            continue
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
            extra = {}
            if variant == "a_frozen_config":
                # 委任_08 A構成: rep30 frozen出力の生成条件(er051 trial_02_run→trial.run_trial_deviation_check、V4A、model、
                # reasoning=vfl01.REASONING_EFFORT、developer=vfl01.DEVIATION_DEVELOPER_MESSAGE[原則なし]、schema=V4A標準[列挙なし]、
                # fixtureのinclude_related_fact_id/sourceフラグをそのまま渡す)を再現。severityのみで選別(昇格ルール不使用)。
                res = None
                for _try in range(3):
                    try:
                        res = trial.run_trial_deviation_check(
                            client, fx["ledger_text"], fx["article_text"], model, "V4A",
                            include_related_fact_id=fx.get("include_related_fact_id", False),
                            source_article_text=fx.get("source_article_text"))
                        break
                    except Exception as e:  # noqa: BLE001
                        print("retry", k, i, type(e).__name__, e)
                        time.sleep(1.0)
                if res is None:
                    parsed = {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_stage1_api_failure": True}
                    cost = 0.0
                else:
                    parsed = res["parsed"]
                    cost = cost_for(model, res["usage"])
                    extra = {"usage": res["usage"], "prompt_sha256": hashlib.sha256(res["prompt"].encode("utf8")).hexdigest(),
                             "model_returned": res["model"], "response_id": res["response_id"], "raw_parsed": res["raw_parsed"]}
            elif variant == "v0":
                kw = {"model": model, "hook_aware": fx.get("hook_aware", False)}
                if fx.get("include_related_fact_id"):
                    kw["include_related_fact_id"] = True
                if fx.get("source_article_text") is not None:
                    kw["source_article_text"] = fx["source_article_text"]
                res = None
                for _try in range(3):
                    try:
                        res = vfl01.run_deviation_check(client, fx["ledger_text"], fx["article_text"], **kw)
                        break
                    except Exception as e:  # noqa: BLE001
                        print("retry", k, i, type(e).__name__, e)
                        time.sleep(1.0)
                if res is None:
                    parsed = {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_stage1_api_failure": True}
                    cost = 0.0
                else:
                    parsed = res["parsed"]
                    cost = cost_for(model, res["usage"])
                    extra = {"usage": res["usage"], "prompt_sha256": hashlib.sha256(res["prompt"].encode("utf8")).hexdigest(),
                             "model_returned": res["model"]}
            else:
                runner.MODEL = model  # stage1_fresh_with_enumerationはmodule globalのMODELを使う
                parsed = runner.stage1_fresh_with_enumeration(
                    client, state, [0], call_log, "%s_p1_%d" % (k, i), fx,
                    developer_message=trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE)
                cost = sum(cost_for(model, c["usage"]) for c in call_log if c.get("usage"))
                extra = {"prompt_sha256": [c.get("prompt_sha256") for c in call_log]}
            total += cost
            os.makedirs(os.path.dirname(f), exist_ok=True)
            json.dump({"instance": k, "run": i, "model": model, "variant": variant, "parsed": parsed, "call_log": call_log, **extra,
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


def agg(n, out=None, quiet=False):
    out = out or OUT
    S = {"inferior": [], "cand_only": [], "both": [], "neither_instances": [], "sc": {}, "neg": {}, "cost_jpy": 0.0, "n_runs": 0,
         "api_failures": 0}
    for k, (fx, vp) in instances().items():
        runs = []
        for i in range(1, n + 1):
            f = "%s/%s/run_%d.json" % (out, k, i)
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
    json.dump(S, open(out + "/agg_phase1.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    if quiet:
        return S
    print(json.dumps({k: (v if k not in ("inferior", "cand_only", "both") else len(v)) for k, v in S.items()},
                     ensure_ascii=False, indent=1))
    for r in S["inferior"]:
        print("INFERIOR:", r)
    return S


def agg_a(n, out=None):
    # 委任_08 受入条件(1)〜(6)の機械集計。比較対象=rep30 frozen(実使用Stage 1、V0差替え含む)。
    out = out or OUT
    R = {"per_instance": {}, "sc": {}, "b_miss": [], "neg": {}, "structural": [], "api_failures": 0,
         "cost": {"total": 0.0, "n_calls": 0, "max_single": 0.0, "over3": []}}
    for k, (fx, src) in instances_a().items():
        runs = [json.load(open("%s/%s/run_%d.json" % (out, k, i), encoding="utf8")) for i in range(1, n + 1)
                if os.path.exists("%s/%s/run_%d.json" % (out, k, i))]
        if not runs:
            continue
        for r in runs:
            c = R["cost"]
            c["total"] += r["cost_jpy"]
            c["n_calls"] += 1
            c["max_single"] = max(c["max_single"], r["cost_jpy"])
            if r["cost_jpy"] > 3:
                c["over3"].append((k, r["run"], r["cost_jpy"]))
            R["api_failures"] += 1 if r["parsed"].get("_stage1_api_failure") else 0
            for d in majors(r["parsed"]):
                for key in ("claim_in_article", "issue", "severity"):
                    if not d.get(key):
                        R["structural"].append((k, r["run"], "missing " + key))
                if fx.get("include_related_fact_id") and not d.get("related_fact_id"):
                    R["structural"].append((k, r["run"], "related_fact_id missing"))
        rep = rep30_stage1(k)
        rep_major = [d for d in (rep[0] if rep else []) if d.get("severity") == "MAJOR"]
        if k in ("bgroup_B3", "bgroup_B2_hormuz"):  # rep30はV4A非検出のためV0記録(baseline_parsed)へ差替え=実使用の既知MAJOR
            rep_major = majors(fx.get("baseline_parsed"))
            rep = [(fx.get("baseline_parsed") or {}).get("deviations", [])] * len(rep)
        fresh_all = [(r["run"], d) for r in runs for d in majors(r["parsed"])]
        match = []
        for d0 in rep_major:
            hits = sorted({r for r, d in fresh_all if same_claim(d0, d)})
            match.append({"claim": d0.get("claim_in_article"), "fact": d0.get("related_fact_id"), "hits": "%d/%d" % (len(hits), len(runs))})
        fresh_only = sum(1 for r, d in fresh_all if not any(same_claim(d0, d) for d0 in rep_major))
        sha_ok = None
        if src:
            fz = json.load(open(src, encoding="utf8")).get("prompt_sha256")
            sha_ok = [r.get("prompt_sha256") == fz for r in runs]
        R["per_instance"][k] = {"runs": len(runs), "rep30_stage1_major_n": len(rep_major), "fresh_major_per_run": [len(majors(r["parsed"])) for r in runs],
                                "claim_match_rate": (sum(1 for m in match if not m["hits"].startswith("0/")) / len(match)) if match else None,
                                "rep30_claims": match, "fresh_only_major_claims": fresh_only, "prompt_sha_match_frozen": sha_ok}
        for d in runner.SAFETY_CRITICAL_CLAIM_DEFS.get(k, []):
            if k in A_SC_INST + ["neg5_hormuz_div_a2"] and d.get("expected", "BLOCKING") == "BLOCKING":
                ch = sum(any(sc_match(k, x) == d["sub_id"] for x in majors(r["parsed"])) for r in runs)
                fz = [any(sc_match(k, x) == d["sub_id"] for x in st if x.get("severity") == "MAJOR") for st in rep]
                R["sc"][d["sub_id"]] = {"instance": k, "fresh": "%d/%d" % (ch, len(runs)), "rep30_used": fz}
        if k in ("bgroup_B1", "bgroup_B2_hormuz", "bgroup_B3", "bgroup_B4", "neg5_hormuz_div_a2", "meta_run03_standard"):
            R["b_miss"] += [{"instance": k, **m} for m in match if m["hits"].startswith("0/")]
        if k in A_NEG:
            R["neg"][k] = {"fresh_runs_with_major": sum(bool(majors(r["parsed"])) for r in runs), "runs": len(runs),
                           "fresh_majors": sum(len(majors(r["parsed"])) for r in runs),
                           "rep30_runs_with_major": sum(1 for st in rep if any(d.get("severity") == "MAJOR" for d in st)), "rep30_runs": len(rep),
                           "rep30_majors": sum(1 for st in rep for d in st if d.get("severity") == "MAJOR")}
    V = R["neg"].values()
    fr, fn = sum(v["fresh_runs_with_major"] for v in V), sum(v["runs"] for v in V)
    zr, zn = sum(v["rep30_runs_with_major"] for v in V), sum(v["rep30_runs"] for v in V)
    R["neg_rate"] = {"fresh": "%d/%d" % (fr, fn), "fresh_pct": round(100.0 * fr / max(fn, 1), 1), "rep30": "%d/%d" % (zr, zn),
                     "rep30_pct": round(100.0 * zr / max(zn, 1), 1),
                     "fresh_majors_per_run": round(sum(v["fresh_majors"] for v in V) / max(fn, 1), 2),
                     "rep30_majors_per_run": round(sum(v["rep30_majors"] for v in V) / max(zn, 1), 2)}
    R["cost"]["avg_per_call"] = round(R["cost"]["total"] / max(R["cost"]["n_calls"], 1), 4)
    R["cost"]["total"] = round(R["cost"]["total"], 4)
    mr = [v["claim_match_rate"] for v in R["per_instance"].values() if v["claim_match_rate"] is not None]
    R["claim_match_rate_mean"] = round(sum(mr) / max(len(mr), 1), 3)
    json.dump(R, open(out + "/agg_a_frozen.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: R[k] for k in ("sc", "b_miss", "neg_rate", "cost", "claim_match_rate_mean", "structural", "api_failures")}, ensure_ascii=False, indent=1))
    for k, v in R["per_instance"].items():
        print(k, v["runs"], "rep30_major", v["rep30_stage1_major_n"], "fresh/run", v["fresh_major_per_run"], "match", v["claim_match_rate"],
              "fresh_only", v["fresh_only_major_claims"], "shaOK", v["prompt_sha_match_frozen"])
    return R


def matrix():
    # 委任_05: 2x2集計(セル別: SC検出/劣後件数/負例MAJOR誤検出/検出claim総数/費用per call/劣後6件の逐語表)
    cells = [("V0@6luna", OUT_BASE + "/cell_v0_6luna"), ("cand@6luna(04c)", OUT_BASE), ("cand@5.6luna", OUT_BASE + "/cell_cand_56luna")]
    base_inf = json.load(open(OUT_BASE + "/agg_phase1.json", encoding="utf8"))["inferior"]  # 委任_04cの劣後6件
    ins = instances()
    res = {}
    for name, d in cells:
        nn = max([int(re.search(r"run_(\d+)", fn).group(1)) for fn in __import__("glob").glob(d + "/*/run_*.json")] or [0])
        S = agg(nn, d, quiet=True)
        tot = 0
        for k in ins:
            for i in range(1, nn + 1):
                f = "%s/%s/run_%d.json" % (d, k, i)
                if os.path.exists(f):
                    tot += len(majors(json.load(open(f, encoding="utf8"))["parsed"]))
        tbl = []
        for r in base_inf:
            runs = [json.load(open("%s/%s/run_%d.json" % (d, r["instance"], i), encoding="utf8")) for i in range(1, nn + 1)
                    if os.path.exists("%s/%s/run_%d.json" % (d, r["instance"], i))]
            h = sum(any(same_claim({"claim_in_article": r["claim"]}, x) for x in majors(rr["parsed"])) for rr in runs)
            tbl.append({"instance": r["instance"], "claim": (r["claim"] or "")[:70], "hits": "%d/%d" % (h, len(runs))})
        res[name] = {"n": nn, "sc": {k: v["cand"] for k, v in S["sc"].items()}, "inferior": len(S["inferior"]),
                     "neg_major_runs": {k: "%d/%d" % (v["cand_major_runs"], v["runs"]) for k, v in S["neg"].items()},
                     "total_majors": tot, "cost_total_jpy": S["cost_jpy"], "n_runs": S["n_runs"],
                     "cost_per_call": round(S["cost_jpy"] / max(S["n_runs"], 1), 4), "api_failures": S["api_failures"], "inferior6": tbl}
    # V0@5.6記録(er050 step1/2 run_1 or fixture baseline_parsed)
    sc, tot, neg = {}, 0, {}
    for k, (fx, vp) in ins.items():
        v0, _ = v0_record(fx, vp)
        tot += len(majors(v0))
        if k in NEG_IDS:
            neg[k] = "%d/1" % bool(majors(v0))
    res["V0@5.6luna(record,n=1)"] = {"n": 1, "total_majors": tot, "neg_major_runs": neg, "inferior": 0}
    json.dump(res, open(OUT_BASE + "/matrix_2x2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="run", choices=["run", "agg", "matrix", "agg_a"])
    ap.add_argument("--stage1-variant", default="candidate", choices=["candidate", "v0", "a_frozen_config"])
    ap.add_argument("--model", default="gpt-6-luna")
    ap.add_argument("--out-subdir", default="")
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--budget-jpy", type=float, default=8.0)
    ap.add_argument("--hard-mult", type=float, default=1.6)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    ONLY = [x for x in a.only.split(",") if x]
    if a.out_subdir:
        OUT = OUT_BASE + "/" + a.out_subdir
    if a.stage == "run":
        run(a.n, a.budget_jpy, a.hard_mult, a.stage1_variant, a.model)
    elif a.stage == "agg":
        agg(a.n, OUT)
    elif a.stage == "agg_a":
        agg_a(a.n, OUT)
    else:
        matrix()
