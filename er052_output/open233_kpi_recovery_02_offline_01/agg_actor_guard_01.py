# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_07 作業1-1(¥0): actor_guard_rejected全件の抽出と仮ラベル。
# 判定(仮ラベル、決定論): 新主体語(英語、runner.extract_actor_nouns)ごとに、(a)現行guard=Ledger全文に英語部分一致、
# (b)JA対訳辞書で関連fact/Ledger全文に対応語、(c)Checker issue/explanationに名指し、を調べる。
# 過剰拒否候補=現行guardは拒否だが(b)か(c)で許容される(Ledger照合型AG1なら許容)。それ以外は正当拒否候補。
import json, os, re, sys, glob, collections
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8")
import er052_open233_self_recovery_flow_runner_01 as runner
OUT = "er052_output/open233_kpi_recovery_02_offline_01"
JA = {  # 英語主体語 -> Ledger(日本語)での対応語(分析用の仮辞書、AG1実装時の設計素材)
    "user": ["利用者", "ユーザー", "使用者"], "customer": ["顧客", "客", "消費者"], "employee": ["従業員", "社員", "労働者"],
    "worker": ["労働者", "従業員", "作業員"], "staff": ["職員", "スタッフ", "従業員"], "contractor": ["請負", "業者"],
    "agent": ["エージェント", "代理"], "executive": ["経営者", "幹部", "役員"], "client": ["顧客", "依頼"],
    "spokesperson": ["広報", "報道官", "スポークスパーソン"], "spokespeople": ["広報", "報道官"],
    "engineer": ["エンジニア", "技術者"], "manager": ["管理者", "マネージャー", "経営"], "official": ["当局", "政府", "当局者"],
    "resident": ["住民"], "driver": ["運転手", "ドライバー"], "passenger": ["乗客"], "patient": ["患者"],
    "student": ["学生"], "teacher": ["教師", "教員"], "analyst": ["アナリスト", "分析"], "trader": ["トレーダー", "取引"],
    "investor": ["投資家"], "shareholder": ["株主"],
}
def lemma(a):
    a = a.lower()
    if a in ("spokespeople", "spokesperson", "staff"): return a
    return a[:-1] if a.endswith("s") and a[:-1] in JA else a
fx = {i["instance_id"]: i["fixture"]["ledger_text"] for i in runner.build_target_instances()}
def fact_block(led, fid):
    if not fid: return ""
    m = re.search(r"\[" + re.escape(fid) + r"\].*?(?=\n\[F-|\n===|\Z)", led, re.S)
    return m.group(0) if m else ""
def ja_hit(a, text):
    return any(w in text for w in JA.get(lemma(a), []))
rows, excluded_missing_ledger = [], 0
for p in sorted(x.replace("\\","/") for x in glob.glob("er052_output/open233_self_recovery_flow_runner_01_*/instances*/*.json")):
    run = p.split("/")[1].replace("open233_self_recovery_flow_runner_01_", "")
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception: continue
    iid = d.get("instance_id"); led = fx.get(iid)
    for c in d.get("cycles") or []:
        blk = [s for s in (c.get("stage2_results") or []) if s.get("materiality") == "BLOCKING"]
        for i, r in enumerate(c.get("rewrite_records") or []):
            h = r.get("handoff") or {}
            for a in h.get("level_attempts") or []:
                if a.get("result") != "actor_guard_rejected": continue
                cl = blk[i] if i < len(blk) else {}
                dev = cl.get("dev") or {}
                fid = cl.get("related_fact_id") or dev.get("related_fact_id")
                before = " ".join(a.get("targets") or []); after = " ".join(a.get("revised") or [])
                new = sorted(runner.extract_actor_nouns(after) - runner.extract_actor_nouns(before))
                issue = (dev.get("issue") or "") + " " + (dev.get("explanation") or "")
                ldg = led or ""
                fb = fact_block(ldg, fid)
                per = {}
                for n in new:
                    per[n] = {"en_in_ledger": n in ldg.lower(), "ja_in_related_fact": ja_hit(n, fb),
                              "ja_in_ledger": ja_hit(n, ldg), "in_issue": bool(re.search(r"\b" + re.escape(lemma(n)) + r"s?\b|" + "|".join(JA.get(lemma(n), ["#none#"])), issue, re.I))}
                ok_ag1 = bool(new) and all(v["ja_in_related_fact"] or v["in_issue"] or v["ja_in_ledger"] for v in per.values())
                strict_ok = bool(new) and all(v["ja_in_related_fact"] or v["in_issue"] for v in per.values())
                rows.append({"run": run, "instance": iid, "ledger_available": led is not None, "cycle": c.get("cycle"), "rec_idx": i,
                    "level": a.get("level"), "claim_identity": r.get("claim_identity"), "related_fact_id": fid,
                    "final_state": d.get("final_state"), "stage4_reason": d.get("stage4_reason"),
                    "ladder_exhausted": bool(r.get("ladder_exhausted_without_full_rewrite")),
                    "before": before, "after": after, "issue": (dev.get("issue") or "")[:400], "new_actors": new, "per_actor": per,
                    "fact_actor_scope": [l.strip() for l in fb.splitlines() if l.strip().startswith("scope:")],
                    "label_ag1_ledger_ok": ok_ag1, "label_ag1_related_or_issue_ok": strict_ok,
                    "label": "excess_candidate" if ok_ag1 else "legit_candidate"})
# repro形式(rep22 cycle2_repro: トップレベルrewrite_records、claimは`input`)。同一(targets,revised)は重複除外。
seen = set()
for p in sorted(x.replace("\\", "/") for x in glob.glob("er052_output/open233_self_recovery_flow_runner_01_*/instances*/*repro*.json")):
    run = p.split("/")[1].replace("open233_self_recovery_flow_runner_01_", "")
    d = json.load(open(p, encoding="utf-8"))
    iid = os.path.basename(p).split("_cycle2")[0]; led = fx.get(iid) or ""
    inp = d.get("input") or {}
    for r in d.get("rewrite_records") or []:
        for a in (r.get("handoff") or {}).get("level_attempts") or []:
            if a.get("result") != "actor_guard_rejected": continue
            before = " ".join(a.get("targets") or []); after = " ".join(a.get("revised") or [])
            key = (run, iid, before, after)
            if key in seen: continue
            seen.add(key)
            fid = inp.get("related_fact_id"); fb = fact_block(led, fid)
            new = sorted(runner.extract_actor_nouns(after) - runner.extract_actor_nouns(before))
            per = {n: {"en_in_ledger": n in led.lower(), "ja_in_related_fact": ja_hit(n, fb), "ja_in_ledger": ja_hit(n, led), "in_issue": False} for n in new}
            ok_ag1 = bool(new) and all(v["ja_in_related_fact"] or v["ja_in_ledger"] for v in per.values())
            rows.append({"run": run, "instance": iid + "(repro)", "ledger_available": bool(led), "cycle": 2, "rec_idx": 0, "level": a.get("level"),
                "claim_identity": r.get("claim_identity"), "related_fact_id": fid, "final_state": d.get("final_state"), "stage4_reason": d.get("stage4_reason"),
                "ladder_exhausted": False, "before": before, "after": after, "issue": "(repro: claim_text=" + str(inp.get("claim_text"))[:100] + ")",
                "new_actors": new, "per_actor": per, "fact_actor_scope": [l.strip() for l in fb.splitlines() if l.strip().startswith("scope:")],
                "label_ag1_ledger_ok": ok_ag1, "label_ag1_related_or_issue_ok": ok_ag1, "label": "excess_candidate" if ok_ag1 else "legit_candidate"})
json.dump(rows, open(f"{OUT}/agg_actor_guard_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("attempts(actor_guard_rejected):", len(rows), " ledger_unavailable:", sum(1 for r in rows if not r["ledger_available"]))
byrec = collections.defaultdict(list)
for r in rows: byrec[(r["run"], r["instance"], r["cycle"], r["rec_idx"])].append(r)
print("distinct rewrite records with >=1 rejection:", len(byrec))
print("label counts(attempt):", collections.Counter(r["label"] for r in rows))
ex_inst = collections.defaultdict(set)
for k, v in byrec.items():
    ex = v[0]["ladder_exhausted"]; fs = v[0]["final_state"]
    print(k, "levels", [x["level"] for x in v], "exhausted", ex, "final", fs, v[0]["stage4_reason"], "labels", [x["label"] for x in v], "new", v[0]["new_actors"])
print("records ladder_exhausted:", sum(1 for v in byrec.values() if v[0]["ladder_exhausted"]))
print("records where all attempts excess_candidate:", sum(1 for v in byrec.values() if all(x["label"] == "excess_candidate" for x in v)))
print("records all-excess AND exhausted AND final STAGE4:", sum(1 for v in byrec.values() if all(x["label"] == "excess_candidate" for x in v) and v[0]["ladder_exhausted"] and (v[0]["final_state"] or "").startswith("STAGE4")))
