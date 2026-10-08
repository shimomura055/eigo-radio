# -*- coding: utf-8 -*-
"""T-A 集計: MANIFEST.json(全run)と eval/SUMMARY_TA.md, HUMAN_CHECK_TA.md, METRICS_TA.json を作る。MAP開封は本script内(集計時のみ)。"""
import collections, glob, json, os, statistics, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
BASE = "er052_output/all6_writer_redesign_necessity_01"
RUNS, EVAL = f"{BASE}/runs", f"{BASE}/eval"
PRICE = {"gpt-5.6-luna": (0.20, 0.02, 1.20), "gpt-6-luna": (0.10, 0.01, 0.50)}
USD_JPY = 160.0
ARMS = ["baseline", "all6"]


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []


def run_cost(d):
    t = 0.0; by = collections.defaultdict(float)
    for r in jl(f"{d}/raw_usage_log.jsonl"):
        pr = PRICE.get(r.get("model_id"))
        if not pr: continue
        c = ((r.get("input_tokens") or 0) - (r.get("cached_input_tokens") or 0)) * pr[0] + (r.get("cached_input_tokens") or 0) * pr[1] + (r.get("output_tokens") or 0) * pr[2]
        c = c / 1e6 * USD_JPY
        by[r.get("stage") or "UNTAGGED"] += c; t += c
    chk = 0.0
    bs = f"{d}/checker/budget_state_checker_after_p01.json"
    if os.path.exists(bs):
        chk = json.load(open(bs, encoding="utf-8")).get("cumulative_jpy", 0.0)
    return t, chk, dict(by)


def manifest_rows():
    rows = []
    for man in sorted(glob.glob(f"{RUNS}/*/control/b*__*__r*/manifest.json")):
        d = os.path.dirname(man)
        m = json.load(open(man, encoding="utf-8"))
        name = os.path.basename(d)
        b, arm, rep = name.split("__")
        t, chk, by = run_cost_jpy_parts = run_cost(d)
        mid = m.get("model_ids_actual", {})
        row = {"key": f"{m['slug']}/{name}", "slug": m["slug"], "b": int(b[1:]), "arm": arm, "rep": int(rep[1:]),
               "brief_sha256": m.get("brief_sha256"), "exit_reason": m.get("exit_reason"), "wall_sec": m.get("wall_sec"),
               "model_ids_actual": {k: v for k, v in mid.items() if not k.startswith("_")},
               "checker_models_seen": mid.get("_checker_models_seen"),
               "cost_writer_jpy_recomputed": round(t, 3), "cost_checker_jpy": round(chk, 3), "cost_total_jpy": round(t + chk, 3),
               "cost_by_stage_jpy": {k: round(v, 3) for k, v in by.items()}, "switch_dump_sha256": (m.get("checker") or {}).get("switch_dump_sha256")}
        # JA Fact Check
        ev = f"{d}/ja_writer/runtime_evidence.json"
        if os.path.exists(ev):
            fc = json.load(open(ev, encoding="utf-8")).get("fact_checks_summary", {})
            row["ja_fc"] = {k: {"final_status": v.get("final_status"), "must_fix_applied": v.get("must_fix_applied"),
                                "n_must_fix": len(v.get("must_fix_used") or [])} for k, v in fc.items()}
        # EN advanced
        ws = f"{d}/writer_run_summary.json"
        if os.path.exists(ws):
            adv = json.load(open(ws, encoding="utf-8")).get("advanced", {})
            row["en_adv"] = {"deviation_overall_status": adv.get("deviation_overall_status"),
                             "retried_for_deviation": adv.get("retried_for_deviation"), "must_fix": len(adv.get("must_fix_used") or [])}
        # Checker
        for f in glob.glob(f"{d}/checker/runs/*.json"):
            c = json.load(open(f, encoding="utf-8"))
            row["checker"] = {"final_state": c.get("final_state"), "n_cycles": len(c.get("cycles") or []),
                              "stage1_candidates": len((c.get("all_deviations_raw") or {}).get("stage1") or []),
                              "n_calls": c.get("total_calls"), "run_cost_jpy": c.get("run_cost_jpy")}
        rows.append(row)
    return rows


def main():
    rows = manifest_rows()
    json.dump({"n_runs": len(rows), "runs": rows}, open(f"{BASE}/MANIFEST.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out = []
    P = out.append
    # ---- 副指標
    P("# SUMMARY_TA(T-A 集計)")
    P("")
    P("## 0. run状況")
    st = collections.Counter((r["arm"], r["exit_reason"] if r["exit_reason"] == "completed" else "STOP/失敗") for r in rows)
    P(f"総run数={len(rows)}。" + " / ".join(f"{a}: completed={st[(a,'completed')]}, stop_or_fail={st[(a,'STOP/失敗')]}" for a in ARMS))
    P("")
    P("### 0-1. STOP/失敗runの内訳(exit_reason)")
    for r in rows:
        if r["exit_reason"] != "completed":
            P(f"- {r['key']} ({r['arm']}): {str(r['exit_reason'])[:200]}")
    P("")
    P("## 1. 副指標(群別)")
    P("| 指標 | baseline | all6 |")
    P("|---|---|---|")
    def per(arm): return [r for r in rows if r["arm"] == arm]
    def fmt(f):
        return " | ".join(f(per(a)) for a in ARMS)
    n = lambda rs: len(rs)
    P("| run数 | " + fmt(lambda rs: str(len(rs))) + " |")
    P("| completed | " + fmt(lambda rs: str(sum(r['exit_reason'] == 'completed' for r in rs))) + " |")
    def ja_flag(rs, key):
        k = 0; tot = 0
        for r in rs:
            for stg, v in (r.get("ja_fc") or {}).items():
                tot += 1
                k += bool(v.get(key))
        return k, tot
    P("| JA Fact Check: must-fix発動(original/r2の判定単位) | " + fmt(lambda rs: "%d/%d" % ja_flag(rs, "must_fix_applied")) + " |")
    P("| JA Fact Check: 最終status非COMPLIANT | " + fmt(lambda rs: "%d/%d" % (sum(1 for r in rs for v in (r.get('ja_fc') or {}).values() if v.get('final_status') != 'LEDGER_COMPLIANT'), sum(len(r.get('ja_fc') or {}) for r in rs))) + " |")
    P("| JA Fact Check or Writer内部Gate STOP(run単位) | " + fmt(lambda rs: "%d/%d" % (sum(1 for r in rs if r['exit_reason'] != 'completed'), len(rs))) + " |")
    P("| EN Advanced deviation must-fix(再生成)発動 | " + fmt(lambda rs: "%d/%d" % (sum(1 for r in rs if (r.get('en_adv') or {}).get('retried_for_deviation')), sum(1 for r in rs if r.get('en_adv')))) + " |")
    def mean(xs): return f"{statistics.mean(xs):.2f}" if xs else "-"
    P("| Checker stage1候補数/本(平均) | " + fmt(lambda rs: mean([r['checker']['stage1_candidates'] for r in rs if r.get('checker')])) + " |")
    P("| Checker call数/本(平均) | " + fmt(lambda rs: mean([r['checker']['n_calls'] for r in rs if r.get('checker') and r['checker'].get('n_calls') is not None])) + " |")
    P("| Checker final_state分布 | " + fmt(lambda rs: ", ".join(f"{k}:{v}" for k, v in collections.Counter(r['checker']['final_state'] for r in rs if r.get('checker')).items())) + " |")
    P("| 費用/本(¥、Writer系再計算+Checker、completed) | " + fmt(lambda rs: mean([r['cost_total_jpy'] for r in rs if r['exit_reason'] == 'completed'])) + " |")
    P("| 費用 合計(¥、全run) | " + fmt(lambda rs: f"{sum(r['cost_total_jpy'] for r in rs):.1f}") + " |")
    P("| 所要時間/本(秒、completed平均) | " + fmt(lambda rs: mean([r['wall_sec'] for r in rs if r['exit_reason'] == 'completed' and r.get('wall_sec')])) + " |")
    P("")
    # ---- 評価
    mp_path = f"{EVAL}/_private/MAP.json"
    if not os.path.exists(mp_path) or not glob.glob(f"{EVAL}/judgments/*.json"):
        open(f"{EVAL}/SUMMARY_TA.md", "w", encoding="utf-8").write("\n".join(out))
        print("\n".join(out)); return
    mp = json.load(open(mp_path, encoding="utf-8"))
    code2 = {v["code"]: (k, v) for k, v in mp["articles"].items()}   # MAP開封(集計時のみ)
    judgments = {}
    for f in glob.glob(f"{EVAL}/judgments/*.json"):
        j = json.load(open(f, encoding="utf-8")); judgments[j["code"]] = j
    recs = []
    for code, j in judgments.items():
        if code not in code2: continue
        k, v = code2[code]
        p = j["parsed"]
        recs.append({"code": code, "key": k, "arm": v["arm"], "slug": v["slug"], "judge": j["judge"], "ng": p["ng_items"], "pending": p["pending"]})
    P("## 2. 盲検評価(ジャッジ=LLM単独、人間確認なし)")
    P(f"評価済み記事数={len(recs)}(baseline {sum(r['arm']=='baseline' for r in recs)} / all6 {sum(r['arm']=='all6' for r in recs)})")
    P("評価者(ジャッジ)別の記事数(armとの交絡確認): " + "; ".join(f"{jn}: baseline {sum(1 for r in recs if r['judge']==jn and r['arm']=='baseline')} / all6 {sum(1 for r in recs if r['judge']==jn and r['arm']=='all6')}" for jn in ("gpt-5.6-luna", "gpt-6-luna")))
    P("")
    def cnt(rs, stage_key=None, sev=None):
        return sum(1 for r in rs for i in r["ng"] if (stage_key is None or i[stage_key]) and (sev is None or i["severity"] == sev))
    def table(title, subsets):
        P(f"### {title}")
        P("| 区分 | 指標 | baseline | all6 | 差(all6-base) | 比(all6/base) |")
        P("|---|---|---|---|---|---|")
        for label, sk in (("JA R2", "in_r2"), ("EN", "in_en"), ("R0(修正前)", "in_r0")):
            for sev, sl in (("major", "重大件数"), ("minor", "軽微件数")):
                for name, rs_all in subsets:
                    a = [r for r in rs_all if r["arm"] == "baseline"]; b = [r for r in rs_all if r["arm"] == "all6"]
                    ca, cb = cnt(a, sk, sev), cnt(b, sk, sev)
                    pa = f"{ca}" ; pb = f"{cb}"
                    ratio = f"{cb/ca:.2f}" if ca else ("-" if not cb else "inf")
                    P(f"| {label}{('/'+name) if name else ''} | {sl}(n={len(a)}/{len(b)}) | {pa} | {pb} | {cb-ca:+d} | {ratio} |")
        P("")
    table("2-1. 全体 件数(NG項目の総数)", [("", recs)])
    P("### 2-2. 記事あたり(平均)")
    P("| 区分 | 指標 | baseline | all6 | 差 | 比 |")
    P("|---|---|---|---|---|---|")
    def per_article(rs, sk, sev):
        return cnt(rs, sk, sev) / len(rs) if rs else float("nan")
    for label, sk in (("JA R2", "in_r2"), ("EN", "in_en")):
        for sev, sl in (("major", "重大/記事"), ("minor", "軽微/記事")):
            a = per_article([r for r in recs if r["arm"] == "baseline"], sk, sev); b = per_article([r for r in recs if r["arm"] == "all6"], sk, sev)
            P(f"| {label} | {sl} | {a:.2f} | {b:.2f} | {b-a:+.2f} | {(b/a if a else float('nan')):.2f} |")
    pa = statistics.mean([len(r["pending"]) for r in recs if r["arm"] == "baseline"] or [float("nan")])
    pb = statistics.mean([len(r["pending"]) for r in recs if r["arm"] == "all6"] or [float("nan")])
    P(f"| 全体 | 保留/記事 | {pa:.2f} | {pb:.2f} | {pb-pa:+.2f} | {(pb/pa if pa else float('nan')):.2f} |")
    # 重大/軽微を含む記事の割合
    for label, sk in (("JA R2", "in_r2"), ("EN", "in_en")):
        for sev in ("major", "minor"):
            fa = [any(i[sk] and i["severity"] == sev for i in r["ng"]) for r in recs if r["arm"] == "baseline"]
            fb = [any(i[sk] and i["severity"] == sev for i in r["ng"]) for r in recs if r["arm"] == "all6"]
            P(f"| {label} | {sev}を1件以上含む記事の割合 | {sum(fa)}/{len(fa)} | {sum(fb)}/{len(fb)} | | |")
    P("")
    P("### 2-3. テーマ別(件数。JA R2+EN。重大/軽微)")
    P("| テーマ | 指標 | baseline | all6 |")
    P("|---|---|---|---|")
    for slug in ("meta", "hormuz", "space_weapons"):
        rs = [r for r in recs if r["slug"] == slug]
        a = [r for r in rs if r["arm"] == "baseline"]; b = [r for r in rs if r["arm"] == "all6"]
        for sev in ("major", "minor"):
            def c2(x): return sum(1 for r in x for i in r["ng"] if (i["in_r2"] or i["in_en"]) and i["severity"] == sev)
            P(f"| {slug} | {sev}件数(n={len(a)}/{len(b)}) | {c2(a)} | {c2(b)} |")
    P("")
    P("### 2-4. 評価者(ジャッジ)別(件数/記事。JA R2+EN、重大/軽微)")
    P("| 評価者 | arm | n | 重大/記事 | 軽微/記事 | 保留/記事 |")
    P("|---|---|---|---|---|---|")
    for jn in ("gpt-5.6-luna", "gpt-6-luna"):
        for arm in ARMS:
            rs = [r for r in recs if r["judge"] == jn and r["arm"] == arm]
            if not rs: continue
            f = lambda sev: sum(1 for r in rs for i in r["ng"] if (i["in_r2"] or i["in_en"]) and i["severity"] == sev) / len(rs)
            P(f"| {jn} | {arm} | {len(rs)} | {f('major'):.2f} | {f('minor'):.2f} | {statistics.mean(len(r['pending']) for r in rs):.2f} |")
    P("")
    P("### 2-5. R0->R2で初出した件数(増幅。R0に無くR2に存在=in_r0=false,in_r2=true) / EN初出(R2に無くENのみ) / R0にあってR2で解消")
    P("| 区分 | baseline | all6 |")
    P("|---|---|---|")
    def emerg(rs): return [i for r in rs for i in r["ng"] if i["in_r2"] and not i["in_r0"]]
    def en_new(rs): return [i for r in rs for i in r["ng"] if i["in_en"] and not i["in_r2"]]
    def fixed(rs): return [i for r in rs for i in r["ng"] if i["in_r0"] and not i["in_r2"]]
    for name, f in (("R2で初出(退行/増幅)", emerg), ("ENで初出", en_new), ("R0にありR2で解消", fixed)):
        a = [r for r in recs if r["arm"] == "baseline"]; b = [r for r in recs if r["arm"] == "all6"]
        sev = lambda xs: f"{len(xs)}(重大{sum(i['severity']=='major' for i in xs)}/軽微{sum(i['severity']=='minor' for i in xs)})"
        P(f"| {name} | {sev(f(a))} | {sev(f(b))} |")
    P("")
    P("### 2-6. NG型分布(kind、JA R2+EN存在項目)")
    kinds = ["subject", "object", "scope", "time", "negation", "causal", "added_fact"]
    P("| kind | baseline 重大 | baseline 軽微 | all6 重大 | all6 軽微 |")
    P("|---|---|---|---|---|")
    for k in kinds:
        row = []
        for arm in ARMS:
            for sev in ("major", "minor"):
                row.append(sum(1 for r in recs if r["arm"] == arm for i in r["ng"] if i["kind"] == k and (i["in_r2"] or i["in_en"]) and i["severity"] == sev))
        P(f"| {k} | " + " | ".join(map(str, row)) + " |")
    P("")
    open(f"{EVAL}/SUMMARY_TA.md", "w", encoding="utf-8").write("\n".join(out))
    # ---- 重大候補(ユーザー確認用、最大10件)
    cands = []
    for r in recs:
        for i in r["ng"]:
            if i["severity"] == "major" and (i["in_r2"] or i["in_en"]):
                cands.append((r, i))
    cands.sort(key=lambda x: (x[0]["arm"], x[0]["key"]))
    h = ["# HUMAN_CHECK_TA(重大候補、ユーザー確認用。LLM単独判定、人間確認前)", "",
         f"重大判定は全{len(cands)}件。以下は最大10件を、armが偏らないよう交互に列挙(MAP開封後のためarm表示あり。確認時の先入観に注意)。", ""]
    base = [c for c in cands if c[0]["arm"] == "baseline"]; allc = [c for c in cands if c[0]["arm"] == "all6"]
    picked = []
    for x, y in zip(base + [None] * 10, allc + [None] * 10):
        for z in (x, y):
            if z and len(picked) < 10: picked.append(z)
    for n_, (r, i) in enumerate(picked, 1):
        run_dir = mp["articles"][r["key"]]["run_dir"]
        h += [f"## {n_}. [{r['arm']}] {r['key']}(評価者={r['judge']})",
              f"- NG文: {i['text']}", f"- fact_id: {i['fact_id']} / 型: {i['kind']} / 存在: R0={i['in_r0']} R2={i['in_r2']} EN={i['in_en']}",
              f"- 判定理由: {i['reason']}", f"- 原文: `{run_dir}/ja_writer/revision2.md`(JA R2) / `{run_dir}/b1b/article.md`(EN)",
              f"- 台帳: `er052_output/open233_polysemy_trial_02/ledgers/{r['slug']}/control/research_ledger/verified_fact_ledger.txt`", ""]
    open(f"{EVAL}/HUMAN_CHECK_TA.md", "w", encoding="utf-8").write("\n".join(h))
    json.dump({"n_major_total": len(cands), "n_listed": len(picked)}, open(f"{EVAL}/HUMAN_CHECK_TA_meta.json", "w"))
    print("\n".join(out))


if __name__ == "__main__":
    main()
