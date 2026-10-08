# -*- coding: utf-8 -*-
"""FACTLOCK Trial 集計。使い方: python agg_fl.py check | main
check: eval/FACTLOCK_CHECK_SUMMARY.md(factlock_check_r0/r1/r2.json 集計)
main : MANIFEST.json, eval/SUMMARY_FL.md, eval/HUMAN_CHECK_FL.md, eval/METRICS_FL.json(MAP開封は本scriptの集計時のみ)"""
import collections
import glob
import json
import os
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
BASE = "er052_output/factlock_writer_trial_01"
EVAL = f"{BASE}/eval"
A6 = "er052_output/all6_writer_redesign_necessity_01/runs"
PRICE = {"gpt-5.6-luna": (0.20, 0.02, 1.20), "gpt-6-luna": (0.10, 0.01, 0.50)}
USD_JPY = 160.0
CELLS = ["baseline", "all6", "factlock"]
STAGES = ["r0", "r1", "r2"]
LABELS = ["neutral", "untagged_brief_fact", "hedged_speculation", "background_general", "new_specific_claim"]


def jl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()] if os.path.exists(p) else []


def mean(xs):
    xs = list(xs)
    return statistics.mean(xs) if xs else float("nan")


def run_cost(d):
    t = 0.0
    for r in jl(f"{d}/raw_usage_log.jsonl"):
        pr = PRICE.get(r.get("model_id"))
        if not pr:
            continue
        t += (((r.get("input_tokens") or 0) - (r.get("cached_input_tokens") or 0)) * pr[0]
              + (r.get("cached_input_tokens") or 0) * pr[1] + (r.get("output_tokens") or 0) * pr[2]) / 1e6 * USD_JPY
    chk = 0.0
    bs = f"{d}/checker/budget_state_checker_after_p01.json"
    if os.path.exists(bs):
        chk = json.load(open(bs, encoding="utf-8")).get("cumulative_jpy", 0.0)
    return t, chk


def fl_runs():
    return sorted(d.replace("\\", "/") for d in glob.glob(f"{BASE}/runs/*/control/b*__factlock__r*")
                  if "_failed_a" not in d and os.path.exists(f"{d}/manifest.json"))


def check_summary():
    out, P = [], None
    P = out.append
    runs = fl_runs()
    recs = []
    for d in runs:
        r = {"dir": d, "name": "/".join(d.split("/")[-3:-2] + d.split("/")[-1:])}
        for s in STAGES:
            p = f"{d}/factlock_check_{s}.json"
            r[s] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
        p = f"{d}/factlock_diff.json"
        r["diff"] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
        p = f"{d}/factlock_summary.json"
        r["summ"] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
        recs.append(r)
    P("# FACTLOCK_CHECK_SUMMARY(照合指標、測定のみ。照合は6-luna自己判定で盲検rubricの代替ではない)")
    P("")
    P(f"対象run数={len(recs)}(照合結果が存在するrun: " + ", ".join(f"{s}={sum(1 for r in recs if r[s])}" for s in STAGES) + ")")
    P("")
    P("## 1. (i) 文単位: タグ付き文数・整合/不整合/判定不能(全run合計 / 記事平均)")
    P("| 段 | タグ付き文 合計 | 整合 | 不整合 | 判定不能 | 不整合率 | 判定不能率 | unknown_tags | 主張 supported/unsupported/undecidable |")
    P("|---|---|---|---|---|---|---|---|---|")
    for s in STAGES:
        rs = [r[s] for r in recs if r[s]]
        tg = sum(x["tagged_sentences"] for x in rs)
        c = collections.Counter()
        cc = collections.Counter()
        unk = 0
        for x in rs:
            ip = x.get("i_pairs") or {}
            c.update(ip.get("counts") or {})
            cc.update(ip.get("claim_counts") or {})
            unk += len(ip.get("unknown_tags") or [])
        den = tg or 1
        P(f"| {s.upper()} | {tg} | {c['整合']} | {c['不整合']} | {c['判定不能']} | {c['不整合']/den:.1%} | {c['判定不能']/den:.1%} | {unk} | {cc['supported']}/{cc['unsupported']}/{cc['undecidable']} |")
    P("")
    P("### 1-1. 主張別 unsupported 件数(run別、R0/R1/R2) と タグ外根拠件数")
    P("| run | R0 不整合文/タグ付き文 | R1 | R2 | R2 unsupported主張 |")
    P("|---|---|---|---|---|")
    for r in recs:
        row = []
        for s in STAGES:
            x = r[s]
            if not x:
                row.append("-"); continue
            ip = x.get("i_pairs") or {}
            row.append(f"{(ip.get('counts') or {}).get('不整合', 0)}/{x['tagged_sentences']}")
        u2 = (((r["r2"] or {}).get("i_pairs") or {}).get("claim_counts") or {}).get("unsupported", "-")
        P(f"| {r['name']} | " + " | ".join(row) + f" | {u2} |")
    P("")
    P("## 2. (ii) タグなし文の5分類(title含む。全run合計)")
    P("| 段 | タグなし文 | " + " | ".join(LABELS) + " | titleの分類(分布) |")
    P("|---|---|" + "---|" * (len(LABELS) + 1))
    for s in STAGES:
        rs = [r[s] for r in recs if r[s]]
        c = collections.Counter()
        un = 0
        tl = collections.Counter()
        for x in rs:
            iu = x.get("ii_untagged") or {}
            c.update(iu.get("counts") or {})
            un += iu.get("untagged_sentences", 0)
            tl[iu.get("title_label")] += 1
        P(f"| {s.upper()} | {un} | " + " | ".join(str(c[l]) for l in LABELS) + " | " + ", ".join(f"{k}:{v}" for k, v in tl.items()) + " |")
    P("")
    P("## 3. (iii) 数値(決定論。title含む)")
    P("| 段 | 数値トークン | match | match_surface_diff | hedge_changed | not_core | 不一致計 | core_used_without_tag | marks_echoed | 数量語(副指標) |")
    P("|---|---|---|---|---|---|---|---|---|---|")
    for s in STAGES:
        rs = [r[s] for r in recs if r[s]]
        c = collections.Counter()
        tot = cw = me = 0
        qw = collections.Counter()
        for x in rs:
            n = x["iii_numbers"]
            c.update(n["counts"]); tot += n["total"]; cw += len(n["core_used_without_tag"]); me += x["marks_echoed"]
            qw.update({k: v for k, v in (n.get("quantity_words") or {}).items() if isinstance(v, int)})
        P(f"| {s.upper()} | {tot} | {c['match']} | {c['match_surface_diff']} | {c['hedge_changed']} | {c['not_core']} | {c['hedge_changed']+c['not_core']} | {cw} | {me} | {sum(qw.values())} |")
    P("")
    P("### 3-1. R2の不一致数値トークン(hedge_changed / not_core)run別")
    for r in recs:
        x = r["r2"]
        if not x:
            continue
        bad = [t for t in x["iii_numbers"]["tokens"] if t["status"] in ("hedge_changed", "not_core")]
        if bad:
            P(f"- {r['name']}: " + ", ".join(f"{t['surface']}({t['status']}{',title' if t['is_title'] else ''})" for t in bad))
    P("")
    P("## 4. (iv) R0→R1→R2 タグ付き文の 維持/改変/削除/added/number_changed(全run合計)")
    P("| 区間 | 維持 | 改変 | 削除 | added | number_changed |")
    P("|---|---|---|---|---|---|")
    for k in ("r0_to_r1", "r1_to_r2", "r0_to_r2"):
        c = collections.Counter()
        for r in recs:
            if r["diff"]:
                c.update(r["diff"][k]["counts"])
        P(f"| {k} | {c['kept']} | {c['modified']} | {c['deleted']} | {c['added']} | {c['number_changed']} |")
    P("")
    P("## 5. タグ除去後の残存「【」/ 広め除去のみで消えた変形タグ")
    P("| 段 | residual_brackets_after_strip 合計 | broad_only_tags_removed 合計 |")
    P("|---|---|---|")
    for s in STAGES:
        res = sum(((r["summ"] or {}).get("strip", {}).get(s, {}).get("residual_brackets_after_strip", 0)) for r in recs)
        bo = sum(((r["summ"] or {}).get("strip", {}).get(s, {}).get("broad_only_tags_removed", 0)) for r in recs)
        P(f"| {s.upper()} | {res} | {bo} |")
    man_unexp = 0
    for r in recs:
        m = json.load(open(f"{r['dir']}/manifest.json", encoding="utf-8"))
        man_unexp += (m.get("residual_bracket_scan") or {}).get("unexpected_total", 0)
    P(f"\nmanifest `residual_bracket_scan.unexpected_total` 合計={man_unexp}")
    open(f"{EVAL}/FACTLOCK_CHECK_SUMMARY.md", "w", encoding="utf-8").write("\n".join(out))
    print("\n".join(out))


def all_rows():
    rows = []
    pats = [("factlock", f"{BASE}/runs/*/control/b*__factlock__r*"), ("all6", f"{A6}/*/control/b*__all6__r*"),
            ("baseline", f"{A6}/*/control/b*__baseline__r*")]
    for cell, pat in pats:
        for d in sorted(glob.glob(pat)):
            d = d.replace("\\", "/")
            if "_failed_a" in d or not os.path.exists(f"{d}/manifest.json"):
                continue
            m = json.load(open(f"{d}/manifest.json", encoding="utf-8"))
            slug = d.split("/control/")[0].split("/")[-1]
            b, _, rep = os.path.basename(d).split("__")
            t, chk = run_cost(d)
            row = {"key": f"{cell}/{slug}/{b}/{rep}", "cell": cell, "slug": slug, "b": int(b[1:]), "rep": int(rep[1:]),
                   "exit_reason": m.get("exit_reason"), "wall_sec": m.get("wall_sec"),
                   "cost_writer_jpy": round(t, 3), "cost_checker_jpy": round(chk, 3), "cost_total_jpy": round(t + chk, 3),
                   "model_ids_actual": {k: v for k, v in (m.get("model_ids_actual") or {}).items() if not k.startswith("_")}}
            ev = f"{d}/ja_writer/runtime_evidence.json"
            if os.path.exists(ev):
                fc = json.load(open(ev, encoding="utf-8")).get("fact_checks_summary", {})
                row["ja_fc"] = {k: {"final_status": v.get("final_status"), "must_fix_applied": v.get("must_fix_applied"),
                                    "n_must_fix": len(v.get("must_fix_used") or [])} for k, v in fc.items()}
            ws = f"{d}/writer_run_summary.json"
            if os.path.exists(ws):
                adv = json.load(open(ws, encoding="utf-8")).get("advanced", {})
                row["en_adv"] = {"retried": adv.get("retried_for_deviation"), "status": adv.get("deviation_overall_status")}
            for f in glob.glob(f"{d}/checker/runs/*.json"):
                c = json.load(open(f, encoding="utf-8"))
                row["checker"] = {"final_state": c.get("final_state"), "stage1": len((c.get("all_deviations_raw") or {}).get("stage1") or []),
                                  "calls": c.get("total_calls")}
            rows.append(row)
    return rows


def main():
    rows = all_rows()
    json.dump({"trial_id": "FACTLOCK-WRITER-REDESIGN-TRIAL-01", "n_runs": len(rows), "runs": rows},
              open(f"{BASE}/MANIFEST.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out = []
    P = out.append
    P("# SUMMARY_FL(3セル同一パック。しきい値なし・有意性は主張しない)")
    P("")
    P("## 0. run状況")
    for c in CELLS:
        rs = [r for r in rows if r["cell"] == c]
        P(f"- {c}: {len(rs)}本、completed={sum(r['exit_reason']=='completed' for r in rs)}、STOP/失敗={sum(r['exit_reason']!='completed' for r in rs)}")
    for r in rows:
        if r["exit_reason"] != "completed":
            P(f"  - {r['key']}: {str(r['exit_reason'])[:160]}")
    P("")
    P("## 1. 副指標(セル別)")
    P("| 指標 | baseline(5.6現行) | all6(6現行) | factlock(6+FL) |")
    P("|---|---|---|---|")

    def per(c): return [r for r in rows if r["cell"] == c]

    def fmt(f): return " | ".join(f(per(c)) for c in CELLS)

    def ja(rs, key): return sum(1 for r in rs for v in (r.get("ja_fc") or {}).values() if v.get(key)), sum(len(r.get("ja_fc") or {}) for r in rs)
    P("| run数/completed | " + fmt(lambda rs: f"{len(rs)}/{sum(r['exit_reason']=='completed' for r in rs)}") + " |")
    P("| JA FC must-fix発動(判定単位) | " + fmt(lambda rs: "%d/%d" % ja(rs, "must_fix_applied")) + " |")
    P("| JA FC 最終非COMPLIANT | " + fmt(lambda rs: "%d/%d" % (sum(1 for r in rs for v in (r.get('ja_fc') or {}).values() if v.get('final_status') != 'LEDGER_COMPLIANT'), sum(len(r.get('ja_fc') or {}) for r in rs))) + " |")
    P("| STOP/失敗(run単位=STOP率) | " + fmt(lambda rs: "%d/%d" % (sum(r['exit_reason'] != 'completed' for r in rs), len(rs))) + " |")
    P("| EN deviation再生成発動 | " + fmt(lambda rs: "%d/%d" % (sum(1 for r in rs if (r.get('en_adv') or {}).get('retried')), sum(1 for r in rs if r.get('en_adv')))) + " |")
    P("| Checker stage1候補/本 | " + fmt(lambda rs: "%.2f" % mean(r['checker']['stage1'] for r in rs if r.get('checker'))) + " |")
    P("| Checker call数/本 | " + fmt(lambda rs: "%.2f" % mean(r['checker']['calls'] for r in rs if r.get('checker') and r['checker'].get('calls') is not None)) + " |")
    P("| Checker final_state | " + fmt(lambda rs: ", ".join(f"{k}:{v}" for k, v in collections.Counter(r['checker']['final_state'] for r in rs if r.get('checker')).items())) + " |")
    P("| 費用/本(Writer系再計算+Checker、全run平均、照合分は含まず※) | " + fmt(lambda rs: "%.2f" % mean(r['cost_total_jpy'] for r in rs)) + " |")
    P("| 費用 合計(JPY) | " + fmt(lambda rs: "%.1f" % sum(r['cost_total_jpy'] for r in rs)) + " |")
    P("| 所要時間/本(秒、全run平均。並列度は同一でない可能性あり) | " + fmt(lambda rs: "%.0f" % mean(r['wall_sec'] for r in rs if r.get('wall_sec'))) + " |")
    P("")
    P("※ factlockの照合(LLM)は raw_usage_log に含まれるため再計算費用に含む(別掲が必要な場合は stage名で分離)。")
    P("")
    mp_path = f"{EVAL}/_private/MAP.json"
    if not os.path.exists(mp_path) or not glob.glob(f"{EVAL}/judgments/*.json"):
        open(f"{EVAL}/SUMMARY_FL.md", "w", encoding="utf-8").write("\n".join(out))
        print("\n".join(out))
        return
    mp = json.load(open(mp_path, encoding="utf-8"))
    code2 = {v["code"]: (k, v) for k, v in mp["articles"].items()}
    recs = []
    for f in glob.glob(f"{EVAL}/judgments/*.json"):
        j = json.load(open(f, encoding="utf-8"))
        if j["code"] not in code2:
            continue
        k, v = code2[j["code"]]
        recs.append({"code": j["code"], "key": k, "cell": v["cell"], "slug": v["slug"], "b": v["b"], "rep": v["rep"], "judge": j["judge"],
                     "ng": j["parsed"]["ng_items"], "pending": j["parsed"]["pending"], "run_dir": v["run_dir"]})
    P("## 2. 盲検評価(LLM単独判定、人間確認なし)")
    P("評価済み: " + ", ".join(f"{c} {sum(r['cell']==c for r in recs)}" for c in CELLS))
    P("評価者別配分: " + "; ".join(f"{jn}: " + "/".join(f"{c}{sum(1 for r in recs if r['judge']==jn and r['cell']==c)}" for c in CELLS) for jn in ("gpt-5.6-luna", "gpt-6-luna")))
    P("")

    def cnt(rs, sk, sev):
        return sum(1 for r in rs for i in r["ng"] if (sk is None or i[sk]) and i["severity"] == sev)

    def cell_rs(c, sub=None):
        return [r for r in recs if r["cell"] == c and (sub is None or sub(r))]

    def ratio(a, b): return f"{b/a:.2f}" if a else ("-" if not b else "inf")
    P("本文の到達状況(STOP記事を母数に含めるが、生成されなかった段は評価対象外=NG0として現れる点に注意): " + "; ".join(
        f"{c}: R0有{sum(mp['articles'][r['key']]['present']['ja_writer/original.md'] for r in cell_rs(c))}/R2有{sum(mp['articles'][r['key']]['present']['ja_writer/revision2.md'] for r in cell_rs(c))}/EN有{sum(mp['articles'][r['key']]['present']['b1b/article.md'] for r in cell_rs(c))}(全{len(cell_rs(c))})" for c in CELLS))
    P("")
    P("### 2-1. 件数と記事あたり(factlock対all6 / factlock対baseline)")
    P("| 区分 | 指標 | baseline | all6 | factlock | FL-all6 | FL/all6 | FL-base | FL/base |")
    P("|---|---|---|---|---|---|---|---|---|")
    for label, sk in (("JA R2", "in_r2"), ("EN", "in_en"), ("R0", "in_r0")):
        for sev, sl in (("major", "重大(件)"), ("minor", "軽微(件)")):
            v = [cnt(cell_rs(c), sk, sev) for c in CELLS]
            P(f"| {label} | {sl} | {v[0]} | {v[1]} | {v[2]} | {v[2]-v[1]:+d} | {ratio(v[1], v[2])} | {v[2]-v[0]:+d} | {ratio(v[0], v[2])} |")
            if label != "R0":
                relkey = "ja_writer/revision2.md" if label == "JA R2" else "b1b/article.md"
                n = [sum(1 for r in cell_rs(c) if mp["articles"][r["key"]]["present"][relkey]) or 1 for c in CELLS]
                w = [v[i] / n[i] for i in range(3)]
                P(f"| {label} | {sl[:2]}/記事(分母=その段の本文がある記事: {n[0]}/{n[1]}/{n[2]}) | {w[0]:.2f} | {w[1]:.2f} | {w[2]:.2f} | {w[2]-w[1]:+.2f} | {(w[2]/w[1] if w[1] else float('nan')):.2f} | {w[2]-w[0]:+.2f} | {(w[2]/w[0] if w[0] else float('nan')):.2f} |")
    pv = [mean(len(r["pending"]) for r in cell_rs(c)) for c in CELLS]
    P(f"| 全体 | 保留/記事 | {pv[0]:.2f} | {pv[1]:.2f} | {pv[2]:.2f} | {pv[2]-pv[1]:+.2f} | | {pv[2]-pv[0]:+.2f} | |")
    for label, sk in (("JA R2", "in_r2"), ("EN", "in_en")):
        for sev in ("major", "minor"):
            f = [sum(any(i[sk] and i["severity"] == sev for i in r["ng"]) for r in cell_rs(c)) for c in CELLS]
            P(f"| {label} | {sev}を1件以上含む記事 | {f[0]}/{len(cell_rs('baseline'))} | {f[1]}/{len(cell_rs('all6'))} | {f[2]}/{len(cell_rs('factlock'))} | | | | |")
    P("")
    P("### 2-2. テーマ別(JA R2+EN。重大/軽微 件数)")
    P("| テーマ | 指標 | baseline | all6 | factlock |")
    P("|---|---|---|---|---|")
    for slug in ("meta", "hormuz", "space_weapons"):
        for sev in ("major", "minor"):
            vals = []
            for c in CELLS:
                rs = cell_rs(c, lambda r: r["slug"] == slug)
                vals.append(f"{sum(1 for r in rs for i in r['ng'] if (i['in_r2'] or i['in_en']) and i['severity']==sev)}(n={len(rs)})")
            P(f"| {slug} | {sev} | " + " | ".join(vals) + " |")
    P("")
    P("### 2-3. 評価者別(件数/記事。JA R2+EN)")
    P("| 評価者 | セル | n | 重大/記事 | 軽微/記事 | 保留/記事 |")
    P("|---|---|---|---|---|---|")
    for jn in ("gpt-5.6-luna", "gpt-6-luna"):
        for c in CELLS:
            rs = cell_rs(c, lambda r: r["judge"] == jn)
            if not rs:
                continue
            g = lambda sev: sum(1 for r in rs for i in r["ng"] if (i["in_r2"] or i["in_en"]) and i["severity"] == sev) / len(rs)
            P(f"| {jn} | {c} | {len(rs)} | {g('major'):.2f} | {g('minor'):.2f} | {mean(len(r['pending']) for r in rs):.2f} |")
    P("")
    P("### 2-4. R2初出(R0に無くR2に存在)/ EN初出 / R0にありR2で解消")
    P("| 区分 | baseline | all6 | factlock |")
    P("|---|---|---|---|")
    defs = (("R2で初出(退行)", lambda i: i["in_r2"] and not i["in_r0"]), ("ENで初出", lambda i: i["in_en"] and not i["in_r2"]),
            ("R0にありR2で解消", lambda i: i["in_r0"] and not i["in_r2"]), ("R0に存在(重大+軽微)", lambda i: i["in_r0"]))
    for name, fn in defs:
        vals = []
        for c in CELLS:
            xs = [i for r in cell_rs(c) for i in r["ng"] if fn(i)]
            vals.append(f"{len(xs)}(重大{sum(i['severity']=='major' for i in xs)}/軽微{sum(i['severity']=='minor' for i in xs)})")
        P(f"| {name} | " + " | ".join(vals) + " |")
    P("")
    P("### 2-5. NG型分布(kind。JA R2+EN存在項目。重大/軽微)")
    P("| kind | baseline | all6 | factlock |")
    P("|---|---|---|---|")
    for k in ["subject", "object", "scope", "time", "negation", "causal", "added_fact"]:
        vals = []
        for c in CELLS:
            vals.append("%d/%d" % tuple(sum(1 for r in cell_rs(c) for i in r["ng"] if i["kind"] == k and (i["in_r2"] or i["in_en"]) and i["severity"] == sev) for sev in ("major", "minor")))
        P(f"| {k} | " + " | ".join(vals) + " |")
    P("")
    # STOP記事の評価
    P("### 2-6. STOP/未完了runの評価結果(母数に含む)")
    for r in recs:
        if mp["articles"][r["key"]]["exit_reason"] != "completed":
            pres = mp["articles"][r["key"]]["present"]
            P(f"- {r['key']}: 到達段 " + ",".join(k.split('/')[-1] for k, v in pres.items() if v) + f" / 重大{sum(i['severity']=='major' for i in r['ng'])}・軽微{sum(i['severity']=='minor' for i in r['ng'])}")
    P("")
    # pairwise
    pwp = f"{EVAL}/pairwise.json"
    if os.path.exists(pwp):
        pw = json.load(open(pwp, encoding="utf-8"))
        win = collections.Counter()
        brief = collections.defaultdict(list)
        for key, v in pw.items():
            kf, ka, order = key.split("|")
            w = "tie" if v["winner_key"] == "tie" else ("factlock" if v["winner_key"] == kf else "all6")
            win[w] += 1
            brief[(kf, ka)].append(w)
        pos = collections.Counter(v["winner_label"] for v in pw.values())
        P("## 3. 面白さ pairwise(副指標。6-luna LLM判定、順序入替2回、24対x2=48判定、人間確認なし)")
        P(f"勝敗(判定単位): factlock {win['factlock']} / all6 {win['all6']} / tie {win['tie']}(位置バイアス確認 A:{pos['A']} B:{pos['B']} tie:{pos['tie']})")
        cons = collections.Counter()
        for _, ws in brief.items():
            cons["factlock一貫"] += ws.count("factlock") == 2
            cons["all6一貫"] += ws.count("all6") == 2
            cons["割れ/引分"] += not (ws.count("factlock") == 2 or ws.count("all6") == 2)
        P(f"brief対単位(2回とも同方向): {dict(cons)}(n={len(brief)})")
        P("")
        P("理由の抜粋(factlockが負けた判定の理由先頭8件):")
        n = 0
        for key, v in pw.items():
            kf, ka, order = key.split("|")
            if v["winner_key"] == ka and n < 8:
                P(f"- {kf}: {v['reason']}"); n += 1
        P("")
    open(f"{EVAL}/SUMMARY_FL.md", "w", encoding="utf-8").write("\n".join(out))
    cands = [(r, i) for r in recs for i in r["ng"] if i["severity"] == "major" and (i["in_r2"] or i["in_en"])]
    cands.sort(key=lambda x: (x[0]["cell"], x[0]["key"]))
    h = ["# HUMAN_CHECK_FL(重大候補、ユーザー確認用。LLM単独判定、人間確認前)", "",
         f"重大判定は全{len(cands)}件。最大10件をセルが偏らないよう巡回して列挙(MAP開封後のためセル表示あり。先入観に注意)。", ""]
    picked = []
    byc = {c: [x for x in cands if x[0]["cell"] == c] for c in CELLS}
    for t in range(10):
        for c in CELLS:
            if t < len(byc[c]) and len(picked) < 10:
                picked.append(byc[c][t])
    for n_, (r, i) in enumerate(picked, 1):
        h += [f"## {n_}. [{r['cell']}] {r['key']}(評価者={r['judge']})", f"- NG文: {i['text']}",
              f"- fact_id: {i['fact_id']} / 型: {i['kind']} / 存在: R0={i['in_r0']} R2={i['in_r2']} EN={i['in_en']}", f"- 判定理由: {i['reason']}",
              f"- 原文: `{r['run_dir']}/ja_writer/revision2.md` / `{r['run_dir']}/b1b/article.md`",
              f"- 台帳: `er052_output/open233_polysemy_trial_02/ledgers/{r['slug']}/control/research_ledger/verified_fact_ledger.txt`", ""]
    open(f"{EVAL}/HUMAN_CHECK_FL.md", "w", encoding="utf-8").write("\n".join(h))
    json.dump({"n_major_total": len(cands), "n_listed": len(picked)}, open(f"{EVAL}/METRICS_FL.json", "w"))
    print("\n".join(out))


if __name__ == "__main__":
    {"check": check_summary, "main": main}[sys.argv[1]]()
