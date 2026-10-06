# -*- coding: utf-8 -*-
"""OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02 委任_01: 01のコピー。変更はprompt本文(4点一致確認の追加)・schema(match項目追加)・見積較正のみ。段階A 42 runの保存候補を再分類するTrial。
到達上限=VALIDATED。Checker本体・runner・SSOTは編集しない。有料callは再分類の分類callのみ(run単位1 call)。
--stage estimate(¥0) / run(有料、--yes-run-paid必須) / agg(¥0)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.getcwd())
import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402  (fixture/gold定義の読み取りのみ。runnerの状態ファイルは触らない)
import er052_open233_self_recovery_stage2_production_01 as s2p  # noqa: E402
import er052_open233_stage1_coverage_checker_01 as cov  # noqa: E402
import er003_v1_en_direct_vfl_01_generate as vfl01  # noqa: E402

MODEL = runner.MODEL  # 既存checkerと同じ(gpt-6-luna)
EFFORT = "medium"      # 既存E2EのStage 1 r3と同じ(er052_open233_e2e_acceptance_01.py L72)
TOK_PER_CHAR = 0.42  # 01実測較正: 入力206,966tok/495,873字=0.417(01は0.66で過大見積)
SC_IDS = ["bgroup_B3", "safety_A2A3", "safety_A4", "safety_A5", "bgroup_B4", "neg5_hormuz_div_a2"]
WATCH_IDS = ["bgroup_B2_hormuz"]
NORMAL_IDS = ["neg1_meta_b3prod_a2", "neg2_meta_refresh_a2", "neg3_hormuz_prodrunner_b1b", "neg4_smallbag_div_a2",
              "neg6_smallbag_div_b1b", "neg7_meta_prodrunner_b1b"]
HOLDOUT_IDS = ["safety_er009_changed_number", "safety_er009_changed_actor", "safety_er009_changed_scope",
               "safety_er009_changed_causality", "safety_er009_changed_certainty", "safety_er009_changed_negation",
               "safety_er009_changed_comparison", "safety_er009_changed_time", "safety_er009_unsupported_new_claim"]

DEVELOPER_MESSAGE = (
    "あなたはニュース記事のFact Safety分類担当です。旧Checkerが『候補』として挙げた記事中の主張を、Verified Fact Ledgerと照らして3択に再分類します。"
    "重大度の判定はしません。数値・日付・固有名・因果・否定・比較を含む主張は厳しく見て、Ledgerと一致しない限りCANDIDATEにしてください。"
)

PROMPT_TEMPLATE = """【Verified Fact Ledger】
{ledger_text}

【記事全文(文脈)】
{article_text}

【再分類の対象(旧Checkerが候補にした主張。IDつき。これらのIDだけを使う)】
{claims_block}

【問い】
各主張について、次の3択のどれかを選んでください。
- SUPPORTED: Ledgerに裏付けがある(Ledgerのfactと一致、または言い換え・平易化の範囲)。
- NO_FACT_CLAIM: 比喩・つなぎ・一般論・読者への問いかけ・導入や締めの修辞など、Ledgerにない具体的なFactを追加していない。
- CANDIDATE: Ledgerとの食い違いがある、または、Ledgerにない具体的な新事実(数値・日付・固有名・因果・仕組みなど)の追加がある。

【規則】
1. 「Ledgerに明示されていない」だけでは CANDIDATE にしない。具体的Factの食い違い、または具体的な新事実の追加がある場合だけ CANDIDATE にする。
2. ただし、数値・日付・固有名・因果・否定・比較のいずれかを含む主張は、Ledgerと一致しない限り CANDIDATE とする(厳しく見る)。特に否定の有無・極性(あった/なかった、増えた/増えていない等)、因果の結び付け(so/because/therefore等)、比較・方向(上昇/下落、より大きい/小さい)、主体(誰が何をしたか)、範囲(一部/全部、一時的/恒久)、確信度(断定/推測)をLedgerと照合する。
3. 迷った場合、その主張が上記6種類のFactのどれかに関わるなら CANDIDATE、関わらない修辞・つなぎ・一般論なら NO_FACT_CLAIM とする。
4. SUPPORTED と判定する前に、主張が述べる具体的Factごとに、次の4点がLedgerと一致しているかを必ず照合する。1つでも mismatch(Ledgerと食い違う、または広げている・落としている)なら、SUPPORTED にせず CANDIDATE とする。
   (i) 主体: 誰が行ったか(actor_match)。
   (ii) 相手先・対象: 誰/何に対して行ったか(counterpart_match)。例: Ledgerが「AがBに対して行った」とするのを、記事が「AがCに対して行った」と書いていれば mismatch。
   (iii) 対象範囲: 範囲が広がっていないか(scope_match)。
   (iv) 限定条件: 一部・テスト・時期などの限定が落ちたり変わったりしていないか(qualifier_match)。
   各点は match / mismatch / n_a(その主張にその点が関わらない)のいずれかで出す。mismatch は、Ledgerの記述と食い違う、範囲を広げる、限定を落とす・変える場合に限る。Ledgerが単にその点へ触れていないだけでは mismatch にしない(規則1と同じ)。NO_FACT_CLAIM の主張は4点とも n_a とする。
5. 判定ごとに reason(1行。4点のうち mismatch があればどの点かを含める)と fact_tags(その主張に含まれるFact種別: number/date/proper_noun/causality/negation/comparison のうち該当するもの。なければ none)を出す。
6. 対象の全IDを1件ずつ出力する。
"""

SCHEMA = {
    "name": "open233_reclassify_verdicts_v2", "strict": True,
    "schema": {"type": "object", "properties": {"results": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "cid": {"type": "string"},
            "verdict": {"type": "string", "enum": ["SUPPORTED", "NO_FACT_CLAIM", "CANDIDATE"]},
            "fact_tags": {"type": "array", "items": {"type": "string", "enum": ["number", "date", "proper_noun", "causality", "negation", "comparison", "none"]}},
            "actor_match": {"type": "string", "enum": ["match", "mismatch", "n_a"]}, "counterpart_match": {"type": "string", "enum": ["match", "mismatch", "n_a"]}, "scope_match": {"type": "string", "enum": ["match", "mismatch", "n_a"]}, "qualifier_match": {"type": "string", "enum": ["match", "mismatch", "n_a"]},
            "reason": {"type": "string"}},
        "required": ["cid", "verdict", "fact_tags", "actor_match", "counterpart_match", "scope_match", "qualifier_match", "reason"], "additionalProperties": False}}},
        "required": ["results"], "additionalProperties": False}}


def load_runs(in_dir):
    out = []
    for s in sorted(os.listdir(f"{in_dir}/runs")):
        for f in sorted(os.listdir(f"{in_dir}/runs/{s}")):
            with open(f"{in_dir}/runs/{s}/{f}", encoding="utf-8") as fh:
                out.append(json.load(fh))
    return out


def src_of(c):
    s = c.get("sources")
    if s:
        return s[0]
    return cov.source_of((c.get("routes") or ["r3"])[0], (c.get("sub_reasons") or [""])[0])


def ckey(c):
    return "|".join(c.get("unit_ids") or []) or ("TXT:" + (c.get("claim_text") or ""))


def entries_of(run):
    """route別の候補entry列。route=r3(記事→Ledger) / r5(Ledger→記事)。"""
    out = []
    for route in ("r3", "r5"):
        for c in (run["audit"]["per_route"].get(route) or {}).get("candidates", []):
            out.append({"route": route, "key": ckey(c), "source": src_of(c), "claim_text": c.get("claim_text") or "",
                        "related": c.get("related_fact_ids") or [], "sub_reasons": c.get("sub_reasons") or []})
    return out


def is_model(e):
    return e["source"].startswith("model_")


def claims_for_run(run):
    """LLM再分類の対象(model由来entryを持つ一意claim)。"""
    d = {}
    for e in entries_of(run):
        if is_model(e):
            x = d.setdefault(e["key"], {"key": e["key"], "claim_text": e["claim_text"], "routes": [], "related": []})
            if e["route"] not in x["routes"]:
                x["routes"].append(e["route"])
            for r in e["related"]:
                if r not in x["related"]:
                    x["related"].append(r)
    items = list(d.values())
    for i, x in enumerate(items, 1):
        x["cid"] = f"C{i}"
    return items


def build_prompt(fixture, items):
    lines = []
    for x in items:
        dirs = "/".join({"r3": "記事→Ledger", "r5": "Ledger→記事"}[r] for r in x["routes"])
        ref = ",".join(x["related"]) or "-"
        lines.append(f'[{x["cid"]}] (旧Checkerの方向: {dirs}; 旧Checkerが照合したfactID: {ref}) {x["claim_text"]}')
    return PROMPT_TEMPLATE.format(ledger_text=fixture["ledger_text"], article_text=fixture["article_text"], claims_block="\n".join(lines))


def get_insts():
    return {i["instance_id"]: i["fixture"] for i in runner.build_target_instances()}


def estimate(args):
    runs = load_runs(args.input_dir)
    insts = get_insts()
    rows, tot = [], [0.0, 0.0, 0.0]
    for r in runs:
        items = claims_for_run(r)
        if not items:
            rows.append({"sample": r["sample"], "instance_id": r["instance_id"], "n_claims": 0, "jpy_low_mid_high": [0, 0, 0]})
            continue
        p = build_prompt(insts[r["instance_id"]], items)
        it = int((len(p) + len(DEVELOPER_MESSAGE) + len(json.dumps(SCHEMA))) * TOK_PER_CHAR)
        # 較正(01実測: 42 call reasoning 61,961tok=1,475/call、可視出力29,955tok=57/claim。02は4点matchフィールド追加で可視を約+50/claim、reasoningは+20%を中央値と仮定=推測)
        est = []
        for rm, vc in ((1.0, 85), (1.2, 105), (1.5, 125)):
            vis = len(items) * vc + 30
            est.append(round(s2p.official_cost_jpy({"input_tokens": it, "output_tokens": int(1475 * rm) + vis}), 4))
        for k in range(3):
            tot[k] += est[k]
        rows.append({"sample": r["sample"], "instance_id": r["instance_id"], "n_claims": len(items), "est_input_tokens": it, "jpy_low_mid_high": est})
    out = {"n_runs": len(runs), "n_calls": sum(1 for x in rows if x["n_claims"]), "model": MODEL, "effort": EFFORT,
           "total_jpy_low_mid_high": [round(x, 2) for x in tot],
           "assumptions": "入力=文字数x0.42(01実測206,966tok/495,873字=0.417)、reasoning=01実測1,475tok/call x(1.0/1.2/1.5)、可視出力=claim数x(85/105/125)+30tok(01実測57/claim+match項目分、推測)",
           "rows": rows}
    os.makedirs(args.out_dir, exist_ok=True)
    json.dump(out, open(f"{args.out_dir}/cost_estimate.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("n_runs", "n_calls", "model", "effort", "total_jpy_low_mid_high")}, ensure_ascii=False))


def call_once(client, developer, prompt):
    return client.responses.create(model=MODEL, reasoning={"effort": EFFORT}, text={"format": {"type": "json_schema", **SCHEMA}},
                                   input=[{"role": "developer", "content": developer}, {"role": "user", "content": prompt}])


def do_run(client, run, fixture, out_dir):
    items = claims_for_run(run)
    path = f"{out_dir}/runs/s{run['sample']}/{run['instance_id']}.json"
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8")).get("cost_jpy", 0.0)
    rec = {"sample": run["sample"], "instance_id": run["instance_id"], "items": items, "results": {}, "calls": [], "cost_jpy": 0.0, "failclosed_cids": []}
    if items:
        prompt = build_prompt(fixture, items)
        parsed = None
        for attempt in range(2):  # 既存call_fnと同様に1回までretry
            t0 = time.time()
            try:
                resp = call_once(client, DEVELOPER_MESSAGE, prompt)
                usage = s2p._extract_usage(resp)
                cost = round(s2p.official_cost_jpy(usage), 4)
                rec["cost_jpy"] = round(rec["cost_jpy"] + cost, 4)
                rec["calls"].append({"attempt": attempt, "usage": usage, "cost_jpy": cost, "elapsed": round(time.time() - t0, 1)})
                parsed = json.loads(resp.output_text)
                break
            except Exception as e:  # noqa: BLE001
                rec["calls"].append({"attempt": attempt, "error": f"{type(e).__name__}: {e}"})
                time.sleep(1.0)
        for r in (parsed or {}).get("results", []):
            rec["results"][r["cid"]] = r
        rec["failclosed_cids"] = [x["cid"] for x in items if x["cid"] not in rec["results"]]  # 未返却=CANDIDATE扱い(fail-closed)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(rec, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return rec["cost_jpy"]


def run_stage(args):
    if not args.yes_run_paid:
        sys.exit("--yes-run-paid required")
    est = json.load(open(f"{args.out_dir}/cost_estimate.json", encoding="utf-8"))
    if est["total_jpy_low_mid_high"][1] > args.budget_jpy:
        sys.exit(f"estimate mid {est['total_jpy_low_mid_high'][1]} > budget {args.budget_jpy}: STOP")
    runs = load_runs(args.input_dir)
    insts = get_insts()
    client = vfl01.get_client()
    cum = 0.0
    todo = [r for r in runs if claims_for_run(r)]
    # 暴走防止Guardrail(T-3): 累計が予算の1.5倍を超えたら新規call発行を止めて報告。
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i in range(0, len(todo), args.workers):
            batch = todo[i:i + args.workers]
            for c in ex.map(lambda r: do_run(client, r, insts[r["instance_id"]], args.out_dir), batch):
                cum += c
            print(f"[{i + len(batch)}/{len(todo)}] cum=JPY{cum:.3f}", flush=True)
            if cum > args.budget_jpy * 1.5:
                print("GUARDRAIL: cum > 1.5x budget; stop issuing new calls", flush=True)
                break
    json.dump({"cum_jpy": round(cum, 4), "budget_jpy": args.budget_jpy}, open(f"{args.out_dir}/budget_state.json", "w"), indent=1)
    print("cum JPY", round(cum, 4))


# ------------------------- 集計 -------------------------
def norm(t):
    return runner._norm_for_residual(t)


def matches_def(d, claim_text):
    t = norm(claim_text)
    if norm(d["text_substring"]).lower() in t.lower():
        return True
    return bool(d.get("text_pattern") and re.search(d["text_pattern"], t, re.I))


def group_of(iid):
    return "SC" if iid in SC_IDS else "WATCH" if iid in WATCH_IDS else "NORMAL" if iid in NORMAL_IDS else "HOLDOUT"


def agg(args):
    runs = load_runs(args.input_dir)
    insts = get_insts()
    res = {}
    for r in runs:
        p = f"{args.out_dir}/runs/s{r['sample']}/{r['instance_id']}.json"
        res[(r["sample"], r["instance_id"])] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    per_run, gold_rows, watch = [], [], {"HF-011": [], "K19": [], "holdout": []}
    ex_nofact, ex_supp, boundary = [], [], []
    tot_cost, tot_calls, tot_in, tot_out = 0.0, 0, 0, 0
    for r in runs:
        iid, smp = r["instance_id"], r["sample"]
        rr = res[(smp, iid)]
        verd = {}  # key -> (verdict, tags, reason, failclosed)
        if rr:
            for x in rr["items"]:
                v = rr["results"].get(x["cid"])
                verd[x["key"]] = (v["verdict"], v["fact_tags"], v["reason"], False) if v else ("CANDIDATE", [], "fail-closed(未返却)", True)
            tot_cost += rr["cost_jpy"]
            for c in rr["calls"]:
                if "usage" in c:
                    tot_calls += 1
                    tot_in += c["usage"].get("input_tokens") or 0
                    tot_out += c["usage"].get("output_tokens") or 0
        ents = entries_of(r)
        for e in ents:
            if is_model(e):
                e["verdict"] = verd.get(e["key"], ("CANDIDATE", [], "no result", True))[0]
                e["survive"] = e["verdict"] == "CANDIDATE"
            else:
                e["survive"] = True  # 決定論・coverage_gapは不変
        keys_all = {e["key"] for e in ents}
        keys_llm = {e["key"] for e in ents if is_model(e)}
        after_all = {e["key"] for e in ents if e["survive"]}
        after_llm = {e["key"] for e in ents if is_model(e) and e["survive"]}
        det_only_keys = keys_all - keys_llm
        rt = {}
        for route in ("r3", "r5"):
            rt[route] = {"before_all": len({e["key"] for e in ents if e["route"] == route}),
                         "after_all": len({e["key"] for e in ents if e["route"] == route and e["survive"]}),
                         "before_llm": len({e["key"] for e in ents if e["route"] == route and is_model(e)}),
                         "after_llm": len({e["key"] for e in ents if e["route"] == route and is_model(e) and e["survive"]})}
        per_run.append({"sample": smp, "instance_id": iid, "group": group_of(iid), "union_before_all": len(keys_all), "union_after_all": len(after_all),
                        "union_before_llm": len(keys_llm), "union_after_llm": len(after_llm), "deterministic_or_gap_only_kept": len(det_only_keys),
                        "audit_union_n": r["audit"]["n_union_candidates"], "r3": rt["r3"], "r5": rt["r5"],
                        "n_failclosed": sum(1 for v in verd.values() if v[3])})
        txt_by_key = {e["key"]: e["claim_text"] for e in ents}
        for k, v in verd.items():
            if group_of(iid) == "NORMAL":
                row = {"run": f"s{smp}/{iid}", "claim": txt_by_key[k], "verdict": v[0], "tags": v[1], "reason": v[2]}
                if v[0] == "NO_FACT_CLAIM":
                    ex_nofact.append(row)
                elif v[0] == "SUPPORTED":
                    ex_supp.append(row)
            if (v[0] != "CANDIDATE" and any(t != "none" for t in v[1])) or (v[0] == "CANDIDATE" and all(t == "none" for t in v[1]) and not v[3]):
                boundary.append({"run": f"s{smp}/{iid}", "claim": txt_by_key[k], "verdict": v[0], "tags": v[1], "reason": v[2]})
        if iid in SC_IDS:
            blocks = cov.ledger_fact_blocks(insts[iid]["ledger_text"])
            for d in runner._safety_critical_defs(iid):
                m = [e for e in ents if matches_def(d, e["claim_text"])]
                row = {"sample": smp, "instance_id": iid, "sub_id": d["sub_id"], "before": bool(m), "after_any": any(e["survive"] for e in m),
                       "after_model": any(is_model(e) and e["survive"] for e in m),
                       "after_r3": any(e["route"] == "r3" and e["survive"] for e in m), "after_r5": any(e["route"] == "r5" and e["survive"] for e in m),
                       "before_r3": any(e["route"] == "r3" for e in m), "before_r5": any(e["route"] == "r5" for e in m), "dropped": []}
                for e in m:
                    if is_model(e) and not e["survive"]:
                        v = verd[e["key"]]
                        row["dropped"].append({"claim": e["claim_text"], "route": e["route"], "verdict": v[0], "tags": v[1], "reason": v[2],
                                               "ledger": {fid: blocks.get(fid, "") for fid in e["related"]}})
                gold_rows.append(row)
        if iid in WATCH_IDS:
            m = [e for e in ents if "HF-011" in e["related"]]
            watch["HF-011"].append({"sample": smp, "before": bool(m), "after": any(e["survive"] for e in m), "after_model": any(is_model(e) and e["survive"] for e in m),
                                    "n_before": len({e["key"] for e in m}), "n_after": len({e["key"] for e in m if e["survive"]}),
                                    "dropped": [{"claim": e["claim_text"], "verdict": verd[e["key"]][0], "tags": verd[e["key"]][1], "reason": verd[e["key"]][2]} for e in m if is_model(e) and not e["survive"]]})
        if iid == "safety_A2A3":
            m = [e for e in ents if "prices began to fall" in e["claim_text"]]
            watch["K19"].append({"sample": smp, "before": bool(m), "after": any(e["survive"] for e in m),
                                 "dropped": [{"claim": e["claim_text"], "verdict": verd[e["key"]][0], "tags": verd[e["key"]][1], "reason": verd[e["key"]][2]} for e in m if is_model(e) and not e["survive"]]})
        if iid in HOLDOUT_IDS:
            watch["holdout"].append({"instance_id": iid, "before": len(keys_all), "after": len(after_all), "after_llm": len(after_llm),
                                     "claims": [{"claim": e["claim_text"], "route": e["route"], "source": e["source"], "survive": e["survive"],
                                                 "verdict": verd.get(e["key"], (None, [], "", False))[0], "reason": verd.get(e["key"], (None, [], "", False))[2],
                                                 "tags": verd.get(e["key"], (None, [], "", False))[1]} for e in ents]})
    groups = {}
    for g in ("SC", "WATCH", "NORMAL", "HOLDOUT", "ALL"):
        rs = [x for x in per_run if g == "ALL" or x["group"] == g]
        n = len(rs)

        def mean(f):
            return round(sum(f(x) for x in rs) / n, 2) if n else None
        groups[g] = {"n_runs": n, "union_before_all": mean(lambda x: x["union_before_all"]), "union_after_all": mean(lambda x: x["union_after_all"]),
                     "union_before_llm": mean(lambda x: x["union_before_llm"]), "union_after_llm": mean(lambda x: x["union_after_llm"]),
                     "det_or_gap_only_kept": mean(lambda x: x["deterministic_or_gap_only_kept"]),
                     "r3_before": mean(lambda x: x["r3"]["before_all"]), "r3_after": mean(lambda x: x["r3"]["after_all"]),
                     "r5_before": mean(lambda x: x["r5"]["before_all"]), "r5_after": mean(lambda x: x["r5"]["after_all"]),
                     "r3_before_llm": mean(lambda x: x["r3"]["before_llm"]), "r3_after_llm": mean(lambda x: x["r3"]["after_llm"]),
                     "r5_before_llm": mean(lambda x: x["r5"]["before_llm"]), "r5_after_llm": mean(lambda x: x["r5"]["after_llm"])}
    gold_sum = {}
    for x in gold_rows:
        g = gold_sum.setdefault(x["sub_id"], {"runs": 0, "before": 0, "after_any": 0, "after_model": 0, "before_r3": 0, "after_r3": 0, "before_r5": 0, "after_r5": 0})
        g["runs"] += 1
        for f in ("before", "after_any", "after_model", "before_r3", "after_r3", "before_r5", "after_r5"):
            g[f] += int(x[f])
    out = {"groups": groups, "per_run": per_run, "gold_rows": gold_rows, "gold_summary": gold_sum, "watch": watch,
           "examples_nofact_normal": ex_nofact[:80], "examples_supported_normal": ex_supp[:80], "boundary": boundary[:80],
           "n_nofact_normal": len(ex_nofact), "n_supported_normal": len(ex_supp),
           "cost": {"n_calls_with_usage": tot_calls, "input_tokens": tot_in, "output_tokens": tot_out, "jpy": round(tot_cost, 4), "model": MODEL, "effort": EFFORT},
           "gold_pass": all(v["before"] == v["after_any"] for v in gold_sum.values())}
    json.dump(out, open(f"{args.out_dir}/reclassify_aggregate.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"groups": groups, "gold_summary": gold_sum, "cost": out["cost"]}, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--stage", required=True, choices=["estimate", "run", "agg"])
    ap.add_argument("--yes-run-paid", action="store_true")
    ap.add_argument("--budget-jpy", type=float, default=10.0)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    {"estimate": estimate, "run": run_stage, "agg": agg}[a.stage](a)


if __name__ == "__main__":
    main()
