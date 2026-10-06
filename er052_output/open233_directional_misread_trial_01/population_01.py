# population_01: OPEN-233 directional misread Trial母集団再集計 (read-only, no LLM)
import json, glob, os, re, sys, statistics
sys.path.insert(0, os.getcwd())
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as cov
OUT = "er052_output/open233_directional_misread_trial_01"
RUNS = sorted(glob.glob("er052_output/open233_prod_e2e_02/runs/*.json"))
LEX = ["ロールバック","撤回","復元","復活","再開","停止","中止","縮小","拡大","増加","減少","引き上げ","引き下げ","延期","前倒し","開始","終了","解除","導入","廃止","上昇","下落","低下","許可","禁止","承認","却下","追加","削除","免除","適用","緩和","強化","取り下げ","見送り","撤廃","値上げ","値下げ","引き上","引き下","急落","急騰","凍結","再導入","可決","否決","再び"]
def ja_head(block):
    first = block.split("\n")[0]
    return first.split(":", 1)[1] if ":" in first else first
def classify(block):
    head = ja_head(block)
    hits = [w for w in LEX if w in head]
    return hits
insts = {i["instance_id"]: i for i in runner.build_target_instances()}
rows = []
calls = []
for f in RUNS:
    d = json.load(open(f, encoding="utf-8"))
    iid = d["instance_id"]
    fx = insts[iid]["fixture"]
    blocks = cov.ledger_fact_blocks(fx["ledger_text"])
    facts = []
    for fid, b in blocks.items():
        h = classify(b)
        facts.append({"fact_id": fid, "state_change_candidate": bool(h), "basis_words": h})
    sp = cov.split_units(fx["article_text"], runner.vs_sentence_segments_l6, runner.CAUSAL_SENTENCE_INITIAL_EN)
    sc = d["stage1_coverage"]
    n_sent = sum(1 for u in sp["units"] if u["type"] in ("sentence", "heading", "title"))
    nsc = sum(1 for x in facts if x["state_change_candidate"])
    rows.append({"instance_id": iid, "fixture_id": fx["id"], "source_path": fx["source_path"],
        "ledger_chars": len(fx["ledger_text"]), "article_chars": len(fx["article_text"]),
        "n_facts": len(facts), "n_state_change_facts_approx": nsc,
        "state_change_ratio": round(nsc / max(1, len(facts)), 3),
        "stored_n_facts": sc.get("n_facts"), "stored_n_units": sc.get("n_units"),
        "stored_n_judged_units": sc.get("n_judged_units"), "recomputed_sentence_units": n_sent,
        "stage1_union_candidates": sc.get("n_union_candidates"),
        "facts": facts})
    for c in d["call_log"]:
        u = c.get("usage") or {}
        if u:
            calls.append((c.get("recovery_stage"), u.get("input_tokens", 0), u.get("output_tokens", 0), c.get("cost_jpy", 0)))
N = len(rows)
tot = lambda k: sum(r[k] or 0 for r in rows)
# implied price: cost = a*in + b*out (least squares, no intercept)
sxx = sum(c[1]**2 for c in calls); sxy = sum(c[1]*c[2] for c in calls); syy = sum(c[2]**2 for c in calls)
sxz = sum(c[1]*c[3] for c in calls); syz = sum(c[2]*c[3] for c in calls)
det = sxx*syy - sxy**2
a = (sxz*syy - syz*sxy)/det; b = (syz*sxx - sxz*sxy)/det
by_stage = {}
for s, i, o, c in calls:
    e = by_stage.setdefault(s, [0, 0, 0, 0.0]); e[0]+=1; e[1]+=i; e[2]+=o; e[3]+=c
res = {"n_runs": N, "implied_jpy_per_1M_in": round(a*1e6, 1), "implied_jpy_per_1M_out": round(b*1e6, 1),
       "calls_by_stage": {k: {"n": v[0], "in": v[1], "out": v[2], "jpy": round(v[3], 4)} for k, v in by_stage.items()}}
res["totals"] = {k: tot(k) for k in ["n_facts", "n_state_change_facts_approx", "stored_n_units", "stored_n_judged_units", "recomputed_sentence_units", "stage1_union_candidates"]}
res["per_run_avg"] = {k: round(v/N, 2) for k, v in res["totals"].items()}
res["ratio_state_change_facts"] = round(res["totals"]["n_state_change_facts_approx"]/res["totals"]["n_facts"], 3)
res["unit_fact_mapping_saved"] = False
res["rows"] = rows
json.dump(res, open(OUT + "/population_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "rows"}, ensure_ascii=False, indent=1))
for r in rows:
    print({k: v for k, v in r.items() if k != "facts"})
# ---- cost estimate (implied price of gpt-6-luna from call_log fit; no other-model price table exists in repo)
pin, pout = a, b  # JPY/token
avg_f = res["per_run_avg"]["n_facts"]; avg_sc = res["per_run_avg"]["n_state_change_facts_approx"]
avg_u = res["per_run_avg"]["stored_n_judged_units"]
art_n = {"low": avg_sc, "mid": avg_u * res["ratio_state_change_facts"], "high": avg_u}
led_tok = {"low": (450, 80), "mid": (525, 80), "high": (600, 380)}
art_tok = {"low": (500, 60), "mid": (600, 60), "high": (700, 360)}
cost = {}
for mult_name, mult in [("same_model_x1.0", 1.0), ("ledger_model_x0.5(price unverified)", 0.5), ("ledger_model_x2.0(price unverified)", 2.0)]:
    cost[mult_name] = {}
    for lv in ["low", "mid", "high"]:
        led = avg_f * (led_tok[lv][0]*pin + led_tok[lv][1]*pout) * mult
        art = art_n[lv] * (art_tok[lv][0]*pin + art_tok[lv][1]*pout)
        cost[mult_name][lv] = {"ledger_only_jpy_per_run": round(led, 3), "article_side_jpy_per_run": round(art, 3), "total_jpy_per_run": round(led + art, 3)}
res["cost_estimate"] = {"price_basis": "gpt-6-luna implied JPY/token fit on 135 call_log entries", "article_units_per_run": {k: round(v, 2) for k, v in art_n.items()},
    "ledger_facts_per_run": round(avg_f, 2), "token_assumptions_ledger(in,out)": led_tok, "token_assumptions_article(in,out)": art_tok, "scenarios": cost,
    "reference_stage2_actual_jpy_per_judgment": round(7.2932/89, 4), "reference_current_total_per_run_jpy": 31.52/9}
for k in ("rows",): pass
json.dump(res, open(OUT + "/population_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res["cost_estimate"], ensure_ascii=False, indent=1))
# basis words per distinct ledger
seen = {}
for r in rows:
    key = r["n_facts"]
    if key in seen: continue
    seen[key] = 1
    print("LEDGER", r["instance_id"], r["n_facts"])
    for x in r["facts"]:
        print("  ", x["fact_id"], x["state_change_candidate"], x["basis_words"])
# ---- md
ce = res["cost_estimate"]; sc = ce["scenarios"]["same_model_x1.0"]
L = ["# population_01 (OPEN-233 directional misread Trial 母集団再集計, ¥0, LLMなし)", "",
 "## 所見", f"- 新9 run = 2種のLedgerのみ(hormuz系4run=12 fact / meta系5run=15 fact)。Ledger全Fact数: 計{res['totals']['n_facts']}件(run平均{avg_f:.2f})。",
 "  注: 計123はStage 1候補『123件』とは別物(偶然の一致。Stage 1候補=66件/run平均7.33)。",
 f"- 状態変化Fact(語彙近似・LLMなし): {res['totals']['n_state_change_facts_approx']}件/{res['totals']['n_facts']} = {res['ratio_state_change_facts']:.1%}(run平均{avg_sc:.2f})。近似のため精度未検証。語は弱いもの(適用/上昇/再開等)を含み偽陽性・偽陰性あり。",
 f"- 単位→fact対応: run jsonに**保存なし**(per_route.unit_status/model_verdictは単位ID→SUPPORTED/CANDIDATEのみ、support_fact_idsはE2E出力全体で0件。checker L670の既知制約)。",
 f"- 記事側確認件数/run: 下限={art_n['low']:.2f}(状態変化fact数、各1単位と仮定) / 近似mid={art_n['mid']:.2f}(判定単位{avg_u:.2f}×状態変化比率) / 上限={art_n['high']:.2f}(Stage 1判定単位全数)。タイトル・見出し含む。最終本文でなく修正前fixture本文で計数(9 run分、文数再計算と保存値は273 vs 275でほぼ一致)。",
 "", "## 表1 run別", "| instance | fixture | facts | 状態変化近似 | 全単位 | 判定単位 | S1候補 |", "|---|---|---|---|---|---|---|"]
for r in rows:
    L.append(f"| {r['instance_id']} | {r['fixture_id']} | {r['n_facts']} | {r['n_state_change_facts_approx']} | {r['stored_n_units']} | {r['stored_n_judged_units']} | {r['stage1_union_candidates']} |")
L += ["", "## 表2 単価(実績逆算)", f"- Stage 2/Checker model=gpt-6-luna(runner L280)、effort=high。call_log135件から逆算: 入力¥{pin*1e6:.1f}/1M tok、出力(reasoning含む)¥{pout*1e6:.1f}/1M tok。公式単価表はrepo内に無く未確認。Anthropic側単価表もrepo内に無い(パイプラインはAnthropic API不使用、OPUS-MODEL-ID-INVENTORY結果)。",
 f"- 実績参照: Stage 2後段¥7.29/89判定=¥{ce['reference_stage2_actual_jpy_per_judgment']}/判定(48 call)。現行E2E総額¥31.52/9run=¥{ce['reference_current_total_per_run_jpy']:.2f}/run。",
 "", "## 表3 追加処理コスト/run(¥、同一model gpt-6-luna、per-fact単独call)", "| 水準 | Ledger側全Fact | 記事側 | 合計 |", "|---|---|---|---|"]
for lv in ["low", "mid", "high"]:
    s = sc[lv]; L.append(f"| {lv} | {s['ledger_only_jpy_per_run']} | {s['article_side_jpy_per_run']} | {s['total_jpy_per_run']} |")
L += ["- low/mid=推論ほぼ無し(出力80/60tok)。highはreasoning上乗せ(+300tok)を許容。実際のeffort=highで運用すると出力が大幅増(Stage 1実績: 1 call出力約8.7k tok)で、highを超える可能性がある。",
 f"- Ledger側別model(単価0.5x/2x仮定、単価未確認): 合計mid ¥{ce['scenarios']['ledger_model_x0.5(price unverified)']['mid']['total_jpy_per_run']}/¥{ce['scenarios']['ledger_model_x2.0(price unverified)']['mid']['total_jpy_per_run']}。",
 "", "## 表4 状態変化近似の根拠語(Ledger別、fact_id: 根拠語)", "語彙: " + "/".join(LEX)]
done = set()
for r in rows:
    if r["n_facts"] in done: continue
    done.add(r["n_facts"]); L.append(f"- {r['fixture_id']}系({r['n_facts']} fact): " + "; ".join(f"{x['fact_id']}:{'/'.join(x['basis_words'])}" for x in r["facts"] if x["state_change_candidate"]) + f" / 非該当: " + ",".join(x["fact_id"] for x in r["facts"] if not x["state_change_candidate"]))
L += ["", "## 所在", "- fixture→Ledger: runner build_target_instances()の`fixture[ledger_text]`(source_pathは表1json参照、population_01.json rows[].source_path)。Ledger全文は各source_path(er019/er037配下audit/deviation_checks等)のledger_text。"]
open(OUT + "/population_01.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(L), "md lines")
