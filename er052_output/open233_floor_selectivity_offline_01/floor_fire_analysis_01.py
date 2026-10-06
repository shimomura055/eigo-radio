# -*- coding: utf-8 -*-
"""OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01 委任_01: 後段機械Safety(deterministic floor)の誤爆35件のread-only分析と設計案replay。
標準ライブラリのみ。runner/Production/prompt非import。LLM/API呼び出しなし(費用0円)。保存run jsonとextract jsonを読むだけ。
注意: ラベル(正当/不要/判断不能)はRCA(委任_22)の【推測】=Sonnet判定。設計案ruleは35件=in-sample。hold-outは別母集団(rep30 SC gold)で参考確認のみ。"""
import argparse, glob, json, os, re, sys, unicodedata
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser()
ap.add_argument("--extract", required=True)
ap.add_argument("--runs-dir", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--holdout-glob", default="er052_output/open233_self_recovery_flow_runner_01*/instances*/*.json")
args = ap.parse_args()
FLOOR_FLAGS = ["changed_actor", "changed_number", "changed_negation", "changed_comparison", "changed_time"]
CAT = {"changed_actor": "主体", "changed_number": "数字", "changed_negation": "否定", "changed_comparison": "比較", "changed_time": "時期",
       "changed_causality_floor": "因果", "tier0:aux:issue_actor": "その他(Tier0補助ベルト:issue文の主体語)"}
LEDGERS = {"meta": "er019_output/family_x_refresh_e2e_01/meta/run_03/ledger/verified_fact_ledger.txt",
           "hormuz": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_01/research_ledger/verified_fact_ledger.txt"}


def fam(inst):
    i = inst.lower()
    if "meta" in i or "safety_a4" in i or "safety_a5" in i or "bgroup_b4" in i:
        return "meta"
    if "hormuz" in i or "a2a3" in i or "bgroup_b3" in i:
        return "hormuz"
    return None


_L = {}


def ledger(f):
    if f is None:
        return "", {}
    if f not in _L:
        t = open(LEDGERS[f], encoding="utf-8").read()
        b = {}
        cur = None
        for ln in t.splitlines():
            m = re.match(r"^\[(?:VERIFIED\] )?([A-Z]+-[A-Z0-9-]+)[\]:]", ln)
            if m:
                cur = m.group(1)
                b[cur] = [ln]
            elif cur:
                b[cur].append(ln)
        _L[f] = (t, {k: "\n".join(v) for k, v in b.items()})
    return _L[f]


# RCA section 6 ラベル(推測、委任_22 Sonnet判定)。run別件数(誤/判断不能/正当)と例示から35件へ割付(claim先頭で指定、それ以外は不要)
LABEL_OVERRIDE = {
    "News reports also cited an employee": "正当", "It said human staff made inappropriate": "正当", "These calls were about trying": "正当",
    "It said that human staff made inappropriate": "正当", "On July 13, Trump posted": "正当", "The fee plan left the stage": "正当",
    "But as the conversation went on, the voice was not": "判断不能", "A human can handle situations": "判断不能",
    "Imagine asking AI to book": "判断不能", "But users could not know who was really": "判断不能", "Users might not know who was doing": "判断不能"}
ex = json.load(open(args.extract, encoding="utf-8"))
ex_blocking = [(run, c["cycle"], b) for run, r in ex["e2e"].items() if run != "bgroup_B3" for c in r["cycles"] for b in c["blocking"]]
RUN_ORDER = ["hormuz_run03_advanced", "meta_run03_advanced", "meta_run03_standard", "neg1_meta_b3prod_a2", "neg2_meta_refresh_a2",
             "neg3_hormuz_prodrunner_b1b", "neg7_meta_prodrunner_b1b"]
runjson = {}
for run in ["hormuz_run03_standard"] + RUN_ORDER:
    runjson[run] = json.load(open(os.path.join(args.runs_dir, "s1", run + ".json"), encoding="utf-8"))
recs = []
for run in RUN_ORDER:
    d = runjson[run]
    for c in d["cycles"]:
        for r in c.get("stage2_results", []):
            if r["materiality"] == "BLOCKING" and (r.get("floor_reason") or "").strip():
                recs.append({"run": run, "cycle": c["cycle"], "r": r})
assert len(recs) == len(ex_blocking) == 35, (len(recs), len(ex_blocking))
for a, (run, cy, b) in zip(recs, ex_blocking):
    assert a["run"] == run and a["cycle"] == cy and a["r"]["claim_text"] == b["claim"], (run, cy, b["claim"][:30])

NEG_EN = re.compile(r"\b(not|no|never|none|neither|nor|nobody|nothing|cannot|without|no longer)\b|n't", re.I)
CMP_EN = re.compile(r"\b(more|less|most|least|than|higher|lower|bigger|smaller|better|worse|larger|fewer|greater|increas\w*|decreas\w*|ris(?:e|es|en|ing)|rose|fall(?:s|ing|en)?|fell|drop\w*|grew|grow\w*|up|down|rather|instead|versus|compared)\b", re.I)
NUM_EN = re.compile(r"\d|%|\b(one|two|three|four|five|six|seven|eight|nine|ten|dozen|hundred|thousand|million|billion|half|twice|double|many|several|few|multiple|both|all|every|each|calls|reports|comments|messages|statements|times)\b", re.I)
TIME_CAL = re.compile(r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b|\b(19|20)\d\d\b|\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|yesterday|today|tomorrow|overnight)\b|\b\d+\s*(day|week|month|year|hour|minute)s?\b", re.I)
TIME_REL = re.compile(r"\b(began|begin|begins|started|start|after|before|soon|quickly|returned|continued|still|already|then|later|now|once|while|when|until|since|during|finally|eventually|will|becomes?|became|went on|as)\b", re.I)
ROLE_EN = re.compile(r"\b(users?|people|staff|company|employees?|workers?|AI|humans?|someone|everyone|they|he|she|you|who|persons?|cargo|ships?|executive)\b|[A-Z][a-z]+")
CMP_JA = re.compile(r"より|比べ|比較|上昇|下落|上げ|下げ|増加|減少|増え|減っ|高く|低く|高い|低い|倍|縮小|拡大|％|%|割合|一時")
NEG_JA = ("ない", "ではない", "でない", "せず", "なく", "なかっ", "なし", "否定", "誤り")
NOTES_FORBID = re.compile(r"(書かない|断定しない|と断定|扱わない|一般化しない|しない)")
ABSENT_RE = re.compile(r"(ありません|ありませんでした|記載(?:は)?(?:され)?(?:て)?(?:い)?(?:ません|ない)|示(?:され)?(?:て)?(?:い)?(?:ません|ない)|確認(?:でき)?(?:ません|ない)|明記(?:され)?(?:て)?(?:い)?(?:ません|ない)|述べて(?:い)?(?:ません|ない))")
CONTRA_RE = re.compile(r"異なり|異なる|矛盾|逆|反転|取り違|入れ替|変わっ|広げ|拡張|一般化|超え|限定|具体化|複数|戻っ|範囲|時系列|主体の")
MONTHS = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}


def norm_num(s):
    return unicodedata.normalize("NFKC", s or "")


def feats(rec):
    claim, dev, flags = rec["claim"], rec["dev"], rec["flags"]
    lt, bl = ledger(fam(rec["inst"]))
    fb = bl.get((rec["fact"] or "").strip()) if bl else None
    issue = dev.get("issue") or ""
    has_contra = bool(CONTRA_RE.search(issue))
    has_abs = bool(ABSENT_RE.search(issue))
    it = "contra_or_expansion" if has_contra else ("absence_only" if has_abs else "unclear")
    out = {}
    fbn = norm_num(fb) if fb else ""
    for f in flags:
        o = {"anchor": False, "strict_confirmed": False, "ledger_relevant": False, "note": ""}
        if f == "changed_comparison":
            o["anchor"] = bool(CMP_EN.search(claim))
            o["ledger_relevant"] = bool(fb and CMP_JA.search(fb)) and o["anchor"]
            o["note"] = ("ledger_cmp_term" if o["ledger_relevant"] else ("no_claim_cmp_word" if not o["anchor"] else ("no_ledger_cmp_term" if fb else "no_fact_block")))
            if not fb:
                o["ledger_relevant"] = True  # fail-closed
        elif f == "changed_negation":
            cn = bool(NEG_EN.search(claim))
            o["anchor"] = cn
            if fb:
                first = fb.split("\n")[0]
                ln = any(m in first for m in NEG_JA)
                nfor = any(NOTES_FORBID.search(x) for x in fb.split("\n") if "notes_for_writer" in x)
                agree = cn and (ln or nfor)
                mismatch = (cn and not (ln or nfor)) or ((not cn) and ln)
                o["strict_confirmed"] = bool(mismatch)
                o["ledger_relevant"] = bool(mismatch)
                o["note"] = "polarity_agree(claim_neg&ledger_neg/forbid)" if agree else ("polarity_mismatch" if mismatch else "no_neg_either")
            else:
                o["note"] = "no_fact_block(fail-closed)"
                o["ledger_relevant"] = True
        elif f == "changed_time":
            cal = TIME_CAL.search(claim)
            rel = TIME_REL.search(claim)
            o["anchor"] = bool(cal or rel)
            if cal and fb:
                md = {(MONTHS[m.group(1).lower()], int(m.group(2))) for m in re.finditer(r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2})", claim, re.I)}
                fd = {(int(a), int(b)) for a, b in re.findall(r"(\d{1,2})月(\d{1,2})日", fbn)}
                if md and not md <= fd:
                    o["strict_confirmed"] = True
                    o["ledger_relevant"] = True
                    o["note"] = "calendar_date_not_in_fact"
                else:
                    o["note"] = "calendar_token_consistent_or_nonparsed"
                    o["ledger_relevant"] = bool(cal and not md)
            else:
                o["note"] = "relational_time_only" if rel else "no_time_word"
                o["ledger_relevant"] = bool(rel) and has_contra
        elif f == "changed_number":
            o["anchor"] = bool(NUM_EN.search(claim))
            nums = set(re.findall(r"\d+(?:\.\d+)?", claim))
            fn = set(re.findall(r"\d+(?:\.\d+)?", fbn))
            single = bool(fb and re.search(r"numeric_value:\s*1件", fb)) and bool(re.search(r"\b(calls|reports|comments|messages|staff|these|many|several)\b", claim, re.I))
            if nums and not nums <= fn:
                o["strict_confirmed"] = True
                o["ledger_relevant"] = True
                o["note"] = "numeric_token_not_in_fact"
            elif single:
                o["strict_confirmed"] = True
                o["ledger_relevant"] = True
                o["note"] = "ledger_single_case_vs_plural_claim"
            else:
                o["note"] = "number_consistent_or_no_token"
        elif f == "changed_actor":
            pn = [w for w in re.findall(r"(?<!^)(?<![.!?]\s)\b[A-Z][a-zA-Z]+\b", claim)
                  if w not in ("I", "The", "A", "An", "So", "But", "And", "It", "They", "This", "That", "These", "At", "On", "In")]
            o["anchor"] = bool(ROLE_EN.search(claim))
            absent = [w for w in pn if lt and w.lower() not in lt.lower()]
            if absent:
                o["strict_confirmed"] = True
                o["ledger_relevant"] = True
                o["note"] = "proper_noun_not_in_ledger:" + ",".join(absent[:3])
            else:
                o["note"] = "no_new_proper_noun(role/generalization未確定)"
                o["ledger_relevant"] = has_contra
        out[f] = o
    return it, out


def fabricate(r, inst, cyc):
    dev = r["dev"]
    return {"inst": inst, "claim": r["claim_text"], "fact": dev.get("related_fact_id"), "dev": dev,
            "flags": [f for f in FLOOR_FLAGS if dev.get(f)], "llm": r.get("llm_materiality"), "fr": r.get("floor_reason") or "", "cycle": cyc}


rows = []
for i, a in enumerate(recs, 1):
    r = a["r"]
    rec = fabricate(r, a["run"], a["cycle"])
    fr = rec["fr"]
    reason_flags = fr.split(":", 1)[1].split(",") if fr.startswith("deterministic_floor:") else [fr]
    cats = [CAT.get(x, x) for x in reason_flags]
    label = "不要"
    for k, v in LABEL_OVERRIDE.items():
        if rec["claim"].startswith(k):
            label = v
    it, ff = feats({**rec, "flags": [x for x in reason_flags if x in FLOOR_FLAGS]})
    dev = r["dev"]
    llm = r.get("llm_materiality")
    llm3 = {"BLOCKING": "重大", "QUALITY": "軽微", "ACCEPTABLE": "問題なし"}[llm]
    rows.append({"no": i, "run": a["run"], "cycle": a["cycle"], "claim": rec["claim"], "fact_id": rec["fact"], "floor_reason": fr, "reason_flags": reason_flags,
                 "categories": cats,
                 "stage1_flags_true": [k for k in dev if k.startswith("changed_") and dev.get(k)] + (["unsupported_new_claim"] if dev.get("unsupported_new_claim") else []),
                 "stage1_routes": (dev.get("stage1_coverage") or {}).get("routes"), "stage1_sub_reasons": (dev.get("stage1_coverage") or {}).get("sub_reasons"),
                 "stage1_issue": dev.get("issue"), "llm_materiality": llm, "llm_3way": llm3,
                 "s1_second_opinion": "present" if r.get("second_opinion") else "none(floor強制のためS1対象外)",
                 "floor_verify": {"target": (r.get("floor_verify") or {}).get("target"), "reason": (r.get("floor_verify") or {}).get("target_reason"),
                                  "released": (r.get("floor_verify") or {}).get("released")},
                 "tier0": (r.get("tier0") or {}).get("target_reason"), "label_RCA_suggested": label, "issue_type": it, "flag_feats": ff,
                 "rewrite_outcome_run_level": runjson[a["run"]]["final_state"]})


def assign_cause(row):
    if row["label_RCA_suggested"] != "不要":
        return None
    if row["floor_reason"].startswith("changed_causality_floor") or row["floor_reason"].startswith("tier0:"):
        return "(iv)Tier0語彙"
    anchors = [row["flag_feats"].get(f, {}).get("anchor") for f in row["reason_flags"] if f in row["flag_feats"]]
    if row["issue_type"] == "absence_only" or not any(anchors):
        return "(i)フラグ不整合"
    return "(ii)種別妥当だが重大性判定欠如"


for r in rows:
    r["cause_unneeded"] = assign_cause(r)


def cat_table():
    t = {}
    for c in ["主体", "数字", "否定", "比較", "因果", "時期", "その他(Tier0補助ベルト:issue文の主体語)"]:
        sel = [r for r in rows if c in r["categories"]]
        t[c] = {"延べ発火": len(sel), "正当": sum(r["label_RCA_suggested"] == "正当" for r in sel), "不要": sum(r["label_RCA_suggested"] == "不要" for r in sel),
                "判断不能": sum(r["label_RCA_suggested"] == "判断不能" for r in sel),
                "LLM判定分布(重大/軽微/問題なし)": [sum(r["llm_3way"] == k for r in sel) for k in ("重大", "軽微", "問題なし")],
                "単独flag": sum(1 for r in sel if len(r["categories"]) == 1), "複合": sum(1 for r in sel if len(r["categories"]) > 1),
                "例(逐語)": [r["claim"] for r in sel][:3]}
    return t


CT = cat_table()


def decide(row):
    flags = [f for f in row["reason_flags"] if f in FLOOR_FLAGS]
    ff = row["flag_feats"]
    it = row["issue_type"]
    llm_block = row["llm_materiality"] == "BLOCKING"
    tier0 = not flags
    if tier0:
        strict, c1, anchor_any = False, False, True
    else:
        strict = any(ff[f]["strict_confirmed"] for f in flags)
        c1 = any(ff[f]["anchor"] and ff[f]["ledger_relevant"] and it != "absence_only" for f in flags)
        anchor_any = any(ff[f]["anchor"] for f in flags)
    res = {}
    res["案0_現行"] = "強制重大"
    res["案1_条件精緻化"] = "強制重大" if (c1 or tier0) else "非重大化(Stage2判定へ戻る)"
    res["案2_確定のみ強制+他は追加確認"] = "強制重大" if (strict or tier0) else "追加確認へ"
    res["案3_トリガーのみ"] = "追加確認へ"
    res["案4_floor撤廃+既存S1"] = "強制重大(LLM自身がBLOCKING)" if llm_block else "追加確認へ(既存S1)"
    force5 = strict or tier0 or (c1 and it == "contra_or_expansion")
    if force5:
        res["案5_段階化"] = "強制重大"
    elif it == "absence_only" and not strict:
        res["案5_段階化"] = "非重大化(Stage2判定へ戻る)"
    else:
        res["案5_段階化"] = "追加確認へ"
    return res


for r in rows:
    r["design"] = decide(r)
DESIGNS = list(rows[0]["design"].keys())
DT = {}
for dname in DESIGNS:
    agg = {}
    for lab in ("正当", "不要", "判断不能"):
        agg[lab] = dict(Counter(r["design"][dname] for r in rows if r["label_RCA_suggested"] == lab))
    S = lambda r: r["design"][dname].startswith("強制重大")
    DT[dname] = {"強制重大(35件中)": sum(S(r) for r in rows),
                 "うちfloorのみ起因(LLM非BLOCKING)": sum(S(r) and r["llm_materiality"] != "BLOCKING" for r in rows),
                 "最終BLOCKING(強制∪LLM BLOCKING)": sum(S(r) or r["llm_materiality"] == "BLOCKING" for r in rows),
                 "追加確認へ": sum(r["design"][dname].startswith("追加確認") for r in rows),
                 "追加確認へのうちLLM非BLOCKING": sum(r["design"][dname].startswith("追加確認") and r["llm_materiality"] != "BLOCKING" for r in rows),
                 "非重大化": sum(r["design"][dname].startswith("非重大化") for r in rows), "ラベル別行き先": agg}

# hold-out参考: rep30 SC gold
SC = {"bgroup_B3": ("HF-007", "flashy 20% plan"), "safety_A2A3": ("HF-003", "repay the money"), "safety_A4": ("MUSE-HC-006", "completed the exchanges with users"),
      "safety_A5": ("MUSE-HC-012", "temporarily put back the feature"), "bgroup_B4": ("MUSE-HC-002", "take over when AI alone has trouble")}
sc_rows = []
for p in sorted(glob.glob(args.holdout_glob)):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(d, dict) or "instance_id" not in d:
        continue
    inst = d["instance_id"]
    gold_flag = inst.replace("safety_er009_", "") if inst.startswith("safety_er009_") else None
    for c in d.get("cycles", []):
        for r in c.get("stage2_results", []):
            dev = r.get("dev", {})
            fr = r.get("floor_reason") or ""
            if not fr.startswith("deterministic_floor:") or dev.get("detected_by_enumeration"):
                continue
            is_gold = False
            if "events driving oil prices" in r["claim_text"] and dev.get("related_fact_id") == "HF-009":
                is_gold = True  # K16(時間関係の変更、委任_58の重大2件の片方)
            elif inst in SC:
                fid, sub = SC[inst]
                is_gold = (dev.get("related_fact_id") == fid and sub in r["claim_text"])
            elif gold_flag in FLOOR_FLAGS:
                is_gold = bool(dev.get(gold_flag))
            if not is_gold:
                continue
            rec = fabricate(r, inst, c["cycle"])
            rf = [x for x in fr.split(":", 1)[1].split(",") if x in FLOOR_FLAGS]
            it, ff = feats({**rec, "flags": rf})
            sc_rows.append({"inst": inst, "cycle": c["cycle"], "claim": r["claim_text"][:110], "flags": rf, "llm": r.get("llm_materiality"),
                            "issue_type": it, "strict": any(ff[f]["strict_confirmed"] for f in rf),
                            "c1": any(ff[f]["anchor"] and ff[f]["ledger_relevant"] and it != "absence_only" for f in rf),
                            "ledger_available": fam(inst) is not None, "issue": (dev.get("issue") or "")[:140]})
_seen = {}
for s in sc_rows:
    k = (s["inst"], s["claim"][:70], tuple(s["flags"]), s["llm"])
    _seen.setdefault(k, dict(s, n_records=0))["n_records"] += 1
sc_rows = list(_seen.values())
for s in sc_rows:
    s["案1"] = "強制" if s["c1"] else "非強制"
    s["案2"] = "強制" if s["strict"] else "追加確認"
    s["案5"] = "強制" if (s["strict"] or (s["c1"] and s["issue_type"] == "contra_or_expansion")) else ("非重大化" if s["issue_type"] == "absence_only" else "追加確認")
    s["案4"] = "強制(LLM自身)" if s["llm"] == "BLOCKING" else "追加確認(S1)"
sc_summary = {"list_floor_only_gold": [(s["inst"], s["claim"][:60], s["flags"], s["issue_type"], s["strict"], s["c1"]) for s in sc_rows if s["llm"] != "BLOCKING"], "n_unique_gold_floor_claims(非列挙複製、gold一致、全保存run重複排除)": len(sc_rows), "うちLLM非BLOCKING(floorだけが重大化)": sum(s["llm"] != "BLOCKING" for s in sc_rows)}
for k in ("案1", "案2", "案5", "案4"):
    sc_summary[k + "(floor-only gold)"] = dict(Counter(s[k] for s in sc_rows if s["llm"] != "BLOCKING"))

cost_by_stage = Counter()
for run, d in runjson.items():
    for x in d.get("call_log", []):
        cost_by_stage[x.get("recovery_stage", "?")] += x.get("cost_jpy", 0) or 0
s1_unit = []
for run, d in runjson.items():
    for c in d["cycles"]:
        for x in c.get("stage2_downgrade_confirm_log", []):
            if x.get("batch_n_claims"):
                s1_unit.append(x["batch_cost_jpy"] / x["batch_n_claims"])
cost = {"8run_total_by_stage_jpy": {k: round(v, 3) for k, v in cost_by_stage.items()}, "8run_total_jpy": round(sum(cost_by_stage.values()), 3),
        "S1_second_opinion_jpy_per_claim_mean": round(sum(s1_unit) / len(s1_unit), 4) if s1_unit else None, "n_s1_claim_records": len(s1_unit)}
out = {"provenance": "frozen(E2E保存run json)+RCA label reuse(推測ラベル)。設計replayはin-sample(35件)+rep30 SC gold(旧Stage1由来、hold-out参考、未較正)", "n": 35,
       "label_counts": dict(Counter(r["label_RCA_suggested"] for r in rows)),
       "cause_counts_unneeded24": dict(Counter(r["cause_unneeded"] for r in rows if r["cause_unneeded"])),
       "stage1_sub_reasons_all_model": all(r["stage1_sub_reasons"] == ["model"] for r in rows),
       "unsupported_new_claim_also_true": sum("unsupported_new_claim" in r["stage1_flags_true"] for r in rows),
       "llm_dist_all35": dict(Counter(r["llm_materiality"] for r in rows)), "category_table": CT, "design_table": DT,
       "sc_gold_holdout_summary": sc_summary, "cost": cost, "rows": rows, "sc_rows": sc_rows}
os.makedirs(args.out_dir, exist_ok=True)
json.dump(out, open(os.path.join(args.out_dir, "floor_fire_analysis_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
L = ["# floor_fire_analysis_01 (OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01 委任_01, read-only, 費用0円)", "",
     f"label_counts(RCA推測ラベル): {out['label_counts']} / LLM判定分布(35件): {out['llm_dist_all35']} / Stage1 sub_reasons全件model: {out['stage1_sub_reasons_all_model']} / unsupported_new_claim併発: {out['unsupported_new_claim_also_true']}/35", "",
     "## カテゴリ別(延べ。複合flagは複数カテゴリへ計上)", "| カテゴリ | 延べ発火 | 正当 | 不要 | 判断不能 | LLM判定(重大/軽微/問題なし) | 単独/複合 |", "|---|---|---|---|---|---|---|"]
for c, v in CT.items():
    L.append(f"| {c} | {v['延べ発火']} | {v['正当']} | {v['不要']} | {v['判断不能']} | {v['LLM判定分布(重大/軽微/問題なし)']} | {v['単独flag']}/{v['複合']} |")
L += ["", "## 不要24件の原因割付", str(out["cause_counts_unneeded24"]), "", "## 設計案replay(35件、in-sample)",
      "| 案 | 強制重大 | うちfloorのみ起因 | 最終BLOCKING(強制∪LLM) | 追加確認へ | 非重大化 | 正当6の行き先 | 判断不能5の行き先 |", "|---|---|---|---|---|---|---|---|"]
for k, v in DT.items():
    L.append(f"| {k} | {v['強制重大(35件中)']} | {v['うちfloorのみ起因(LLM非BLOCKING)']} | {v['最終BLOCKING(強制∪LLM BLOCKING)']} | {v['追加確認へ']} | {v['非重大化']} | {v['ラベル別行き先']['正当']} | {v['ラベル別行き先']['判断不能']} |")
L += ["", "## 35件一覧", "| no | run | cy | fact | floor | LLM | label | issue_type | 原因 | 案1 | 案2 | 案5 | claim |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    L.append(f"| {r['no']} | {r['run'][:14]} | {r['cycle']} | {r['fact_id']} | {r['floor_reason'].replace('deterministic_floor:','')} | {r['llm_3way']} | {r['label_RCA_suggested']} | {r['issue_type']} | {r['cause_unneeded'] or ''} | {r['design']['案1_条件精緻化'][:4]} | {r['design']['案2_確定のみ強制+他は追加確認'][:4]} | {r['design']['案5_段階化'][:4]} | {r['claim'][:60]} |")
L += ["", "## SC gold hold-out参考(rep30、旧Stage1由来)", json.dumps(sc_summary, ensure_ascii=False), "", "## コスト材料", json.dumps(cost, ensure_ascii=False)]
open(os.path.join(args.out_dir, "floor_fire_analysis_01.md"), "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))
