# -*- coding: utf-8 -*-
# loop2_cost_structure_01.py (OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_10、完全に¥0・APIなし・既存モジュールはimportのみ)
# 段階A(42 run)とrep30の保存出力だけを読み、(1)費用構造RCA (2)SC候補の具体性 (3)否定極性検査の是正案(オフライン再実装) (4)案別費用見込み を出す。
# 出力: loop2_cost_structure_01.json / .md(同ディレクトリ)。Trial専用、Production未配線、APPROVED_FOR_PRODUCTIONではない。
import glob, json, os, re, statistics as st, sys
from collections import Counter, defaultdict
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as cov
import er052_open233_stage1_stageA_01 as sa
import er052_open233_self_recovery_stage2_production_01 as s2p
import numpy as np

OUT = "er052_output/open233_kpi_recovery_02_offline_01"
RUNS = "er052_output/open233_stage1_stageA_01/runs"
REP30 = "er052_output/open233_self_recovery_flow_runner_01_rep30"
REP24_MEAN = 0.4401
GROUPS = {"SC": sa.SC_IDS, "B2watch": sa.WATCH_IDS, "NORMAL": sa.NORMAL_IDS, "holdout": sa.HOLDOUT_IDS}
GROUP_OF = {i: g for g, ids in GROUPS.items() for i in ids}
JPY_PER_OUT_TOK = s2p.PRICE_OUT * s2p.USD_JPY / 1e6
JPY_PER_IN_TOK = s2p.PRICE_IN * s2p.USD_JPY / 1e6
JPY_PER_CACHED_TOK = s2p.PRICE_CACHED * s2p.USD_JPY / 1e6


def load_runs():
    out = []
    for p in sorted(glob.glob(f"{RUNS}/s*/*.json")):
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def mean(x):
    x = list(x)
    return round(sum(x) / len(x), 4) if x else 0.0


def ols(X, y):
    X = np.array(X, float); y = np.array(y, float)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ b
    ss_res = float(((y - pred) ** 2).sum()); ss_tot = float(((y - y.mean()) ** 2).sum()) or 1.0
    return [round(float(v), 3) for v in b], round(1 - ss_res / ss_tot, 3)


# ---------------- 1. 費用構造RCA ----------------
def route_calls(run, route):
    return [c for c in run["audit"]["per_route"][route]["calls"] if c.get("usage")]


def call_cost_parts(u):
    it, ct, ot, rt = u.get("input_tokens", 0), u.get("cached_input_tokens", 0), u.get("output_tokens", 0), u.get("reasoning_tokens", 0)
    return {"in_uncached_jpy": max(it - ct, 0) * JPY_PER_IN_TOK, "in_cached_jpy": ct * JPY_PER_CACHED_TOK,
            "out_reasoning_jpy": rt * JPY_PER_OUT_TOK, "out_visible_jpy": max(ot - rt, 0) * JPY_PER_OUT_TOK}


def cost_rca(runs):
    R = {"price_jpy_per_Mtok": {"in": JPY_PER_IN_TOK * 1e6, "cached": JPY_PER_CACHED_TOK * 1e6, "out": JPY_PER_OUT_TOK * 1e6},
         "note": "output_tokensはreasoningを含む(official_cost_jpyがoutput_tokensだけに単価を掛けるため、reasoningの別加算は無い)。可視出力=output-reasoning"}
    types = defaultdict(list)  # (route, label) -> [(run, call)]
    for r in runs:
        for rt in ("r3", "r5"):
            for c in route_calls(r, rt):
                types[(rt, c["label"])].append((r, c))
    tab = {}
    for (rt, lab), v in types.items():
        us = [c["usage"] for _, c in v]
        parts = [call_cost_parts(u) for u in us]
        tot = [sum(p.values()) for p in parts]
        row = {"n_calls": len(v), "mean_input_tokens": mean(u["input_tokens"] for u in us), "mean_cached_tokens": mean(u["cached_input_tokens"] for u in us),
               "mean_output_tokens": mean(u["output_tokens"] for u in us), "mean_reasoning_tokens": mean(u["reasoning_tokens"] for u in us),
               "mean_visible_tokens": mean(u["output_tokens"] - u["reasoning_tokens"] for u in us), "mean_cost_jpy": mean(c.get("cost_jpy", 0) for _, c in v),
               "recomputed_cost_jpy": mean(tot)}
        for k in parts[0]:
            row["share_" + k] = round(sum(p[k] for p in parts) / sum(tot), 3)
        tab[f"{rt}/{lab}"] = row
    R["by_call_type"] = tab
    allc = [c for r in runs for rt in ("r3", "r5") for c in route_calls(r, rt)]
    parts = [call_cost_parts(c["usage"]) for c in allc]
    tot = sum(sum(p.values()) for p in parts)
    R["all_calls"] = {"n": len(allc), "mean_jpy": mean(c.get("cost_jpy", 0) for c in allc),
                      **{"share_" + k: round(sum(p[k] for p in parts) / tot, 3) for k in parts[0]}}
    R["failed_or_retry_calls"] = sum(1 for r in runs for rt in ("r3", "r5") for c in r["audit"]["per_route"][rt]["calls"] if not c.get("usage"))
    R["cached_zero_calls"] = sum(1 for c in allc if c["usage"]["cached_input_tokens"] == 0)
    # 出力長の回帰(r3: 可視出力tokens ~ SUPPORTED単位数 + CANDIDATE単位数 + 候補テキスト文字数)
    Xr3, yr3, Xr5, yr5, rows = [], [], [], [], []
    for r in runs:
        a = r["audit"]["per_route"]["r3"]
        cs = [x for x in a["candidates"] if "model" in x["sub_reasons"]]
        chars = sum(len("".join(x.get("issues") or [])) + len("".join(x.get("model_claims") or x.get("model_claim") or [])) for x in cs)
        st_ = list(a["unit_status"].values())
        ns = sum(1 for s in st_ if s.startswith("SUPPORTED")); nc = sum(1 for s in st_ if s == "CANDIDATE")
        cl = route_calls(r, "r3")
        if cl:
            u = cl[0]["usage"]
            Xr3.append([ns, nc, chars]); yr3.append(u["output_tokens"] - u["reasoning_tokens"])
            rows.append({"iid": r["instance_id"], "ns": ns, "nc": nc, "chars": chars, "visible": yr3[-1], "reasoning": u["reasoning_tokens"]})
        a5 = r["audit"]["per_route"]["r5"]; c5 = route_calls(r, "r5")
        if c5:
            st5 = list(a5["unit_status"].values())
            nm = sum(1 for s in st5 if s in ("MATCH", "DEVIATION")); nd = sum(1 for s in st5 if s == "DEVIATION")
            ch5 = sum(len("".join(x.get("issues") or [])) for x in a5["candidates"])
            u = c5[0]["usage"]
            Xr5.append([r["audit"]["n_facts"], nm, ch5]); yr5.append(u["output_tokens"] - u["reasoning_tokens"])
    b3, r2_3 = ols(Xr3, yr3); b5, r2_5 = ols(Xr5, yr5)
    R["r3_visible_regression"] = {"features": ["per SUPPORTED unit", "per CANDIDATE unit(skeleton)", "per candidate text char(issue+claim)"], "coef_tokens": b3, "r2": r2_3, "n": len(yr3)}
    R["r5_visible_regression"] = {"features": ["per fact", "per matched unit", "per issue char"], "coef_tokens": b5, "r2": r2_5, "n": len(yr5)}
    ns_m = mean(x[0] for x in Xr3); nc_m = mean(x[1] for x in Xr3); ch_m = mean(x[2] for x in Xr3)
    vis_m = mean(yr3)
    R["r3_visible_decomposition_mean_tokens"] = {"visible_mean": vis_m, "SUPPORTED_units_part": round(b3[0] * ns_m, 1), "CANDIDATE_skeleton_part": round(b3[1] * nc_m, 1),
                                                 "candidate_text_part": round(b3[2] * ch_m, 1), "SUPPORTED_share_of_visible": round(b3[0] * ns_m / vis_m, 3),
                                                 "mean_SUPPORTED_units": ns_m, "mean_CANDIDATE_units": nc_m, "mean_candidate_chars": ch_m}
    R["_r3_rows"] = rows
    return R


# ---------------- 2. SC候補の具体性 ----------------
SPECIFIC = ("changed_number", "changed_actor", "changed_time", "changed_certainty", "changed_causality", "changed_comparison", "changed_negation")
GENERIC = ("changed_fact", "changed_scope", "unsupported_new_claim")
ELEM_RE = re.compile(r"数|人数|件|割合|%|％|時期|日|月|年|主体|担当|誰|範囲|因果|ため|理由|確信|断定|可能性|否定|比較|より|以上|以下|のみ|だけ|すべて|全て|一部|一時|限定")


def concreteness(c, blocks, mode="strict"):
    """strict: factが実在し、7種の具体要素フラグ(数値/主体/時期/確信度/因果/比較/否定)のいずれかが立つ。permissive: 要素語(正規表現)でも可。"""
    on = {k for k, v in (c.get("flags") or {}).items() if v}
    rel = [x for x in (c.get("related_fact_ids") or []) if x in blocks]
    iss = " ".join(i for i in (c.get("issues") or []) if i and not i.startswith("決定論検査で戻した"))
    spec = bool(on & set(SPECIFIC)); elem = bool(ELEM_RE.search(iss))
    if rel and (spec or (mode == "permissive" and elem)) and (mode == "strict" or len(iss) >= 25):
        return "CONCRETE"
    if rel and len(iss) >= 25:
        return "SEMI"
    return "VAGUE"


def cand_row(c, blocks):
    return {"flags_on": [k for k, v in (c.get("flags") or {}).items() if v], "related_fact_ids": c.get("related_fact_ids"),
            "issue": " / ".join(c.get("issues") or [])[:170], "claim": c["claim_text"][:100], "routes": c["routes"], "sub_reasons": c["sub_reasons"],
            "tier": concreteness(c, blocks)}


def sc_specificity(runs, blocks_by_inst):
    R = {"sc_rows": [], "holdout_rows": [], "hf011_rows": [], "tier_by_group": {}, "tier_by_label": {}}
    for r in runs:
        iid = r["instance_id"]; blocks = blocks_by_inst[iid]; uc = r["audit"]["union_candidates"]
        if iid in sa.SC_IDS:
            for d in runner._safety_critical_defs(iid):
                hit = [c for c in uc if sa.claim_matches_def(d, c["claim_text"])]
                rr = [cand_row(c, blocks) for c in hit]
                R["sc_rows"].append({"iid": iid, "sub_id": d["sub_id"], "sample": r["sample"], "n_matching": len(hit),
                                     "best_tier": ("CONCRETE" if any(x["tier"] == "CONCRETE" for x in rr) else (rr[0]["tier"] if rr else "MISSING")),
                                     "model_judged": any("model" in x["sub_reasons"] for x in rr), "cands": rr})
        if iid in sa.HOLDOUT_IDS:
            R["holdout_rows"].append({"iid": iid, "n_cands": len(uc), "cands": [cand_row(c, blocks) for c in uc]})
        if iid == "bgroup_B2_hormuz":
            hit = [c for c in uc if "HF-011" in (c.get("related_fact_ids") or []) or "disappearance of the fee plan" in c["claim_text"]]
            R["hf011_rows"].append({"sample": r["sample"], "n_matching": len(hit), "cands": [cand_row(c, blocks) for c in hit]})
        for mode in ("strict", "permissive"):
            cnt = Counter(concreteness(c, blocks, mode) for c in uc if "model" in c["sub_reasons"])
            g = GROUP_OF[iid]; t = R["tier_by_group"].setdefault(f"{mode}:{g}", Counter()); t.update(cnt)
    R["tier_by_group"] = {g: dict(v) for g, v in sorted(R["tier_by_group"].items())}
    import stageA_candidate_composition_01 as comp
    lab = Counter()
    for iid, labs in comp.SAMPLE_LABELS.items():
        d = json.load(open(f"{RUNS}/s1/{iid}.json", encoding="utf-8"))
        for c in d["audit"]["union_candidates"][:5]:
            u = c["unit_ids"][0]
            for mode in ("strict", "permissive"):
                tier = concreteness(c, blocks_by_inst[iid], mode) if "model" in c["sub_reasons"] else "DETERMINISTIC_ONLY"
                lab[(mode + ":" + labs[u], tier)] += 1
    R["tier_by_label"] = {f"{k[0]}|{k[1]}": v for k, v in sorted(lab.items())}
    R["sc_summary"] = {"n_sc_runs_x_defs": len(R["sc_rows"]), "best_tier": dict(Counter(x["best_tier"] for x in R["sc_rows"])),
                       "model_judged": sum(1 for x in R["sc_rows"] if x["model_judged"])}
    return R


# ---------------- 3. 否定極性検査の是正案(オフライン再実装、checker本体は無変更) ----------------
BENIGN_JA = re.compile(r"ほどなく|ではなく|でなく|意図せず|思いがけず|図らずも|知らず|にもかかわらず")
KANA = re.compile(r"[ぁ-んァ-ヶ]")
EXTRA_JA = ("なし",)
UNIT_EN_EXTRA = re.compile(r"(?<![\w'-])(?:dislik(?:e|es|ed)|lack(?:s|ed)?|fail(?:s|ed)\s+to|unable)(?![\w-])", re.I)
NOT_ONLY = re.compile(r"not\s+only\b", re.I)


def unit_neg_v2(text):
    t = NOT_ONLY.sub(" ", text)
    return bool(cov.NEGATION_EN_RE.search(t) or UNIT_EN_EXTRA.search(t))


def fact_neg_v2(block, scope="first"):
    lines = block.split("\n")
    line = lines[0] if scope == "first" else "\n".join(lines)
    if not KANA.search(line[:80]):
        return bool(cov.NEGATION_EN_RE.search(line))
    s = BENIGN_JA.sub("", line)
    return any(m in s for m in cov.NEGATION_MARKERS_JA + EXTRA_JA)


def neg_mismatch_v2(unit_text, blocks, scope_all=False):
    """scope_all=False: fact側はclaim行(1行目)のみ(是正案a)。True: fact block全行で否定を探す(是正案b=「全行照合」)。"""
    u_neg = unit_neg_v2(unit_text)
    f_first = [fact_neg_v2(b, "first") for b in blocks]
    f_all = [fact_neg_v2(b, "all" if scope_all else "first") for b in blocks]
    if not blocks:
        return False
    return (u_neg and not any(f_all)) or ((not u_neg) and all(f_first))


def negation_study(runs, blocks_by_inst):
    fires, rows = [], []
    for r in runs:
        iid = r["instance_id"]; bl = blocks_by_inst[iid]
        for c in r["audit"]["union_candidates"]:
            if "negation_polarity_mismatch" in c["sub_reasons"]:
                rf = (c.get("related_fact_ids") or [""])[0]
                fires.append((r, c, rf, bl.get(rf, "")))
    ocnt = vcnt = vball = 0; resid = []
    for r, c, rf, blk in fires:
        unit = c["claim_text"]
        orig = cov.negation_mismatch({"claim_text": unit, "text": unit, "type": "sentence"}, [blk]) if blk else False
        v2 = neg_mismatch_v2(unit, [blk]) if blk else False
        ocnt += orig; vcnt += v2
        vball += bool(blk and neg_mismatch_v2(unit, [blk], scope_all=True))
        if v2:
            resid.append({"iid": r["instance_id"], "unit": c["unit_ids"][0], "sample": r["sample"], "claim": unit[:110], "fact_id": rf, "fact_line": blk.split("\n")[0][:110],
                          "other_sub_reasons": [x for x in c["sub_reasons"] if x != "negation_polarity_mismatch"], "model_flagged": "model" in c["sub_reasons"]})
    uniq = {(x["iid"], x["unit"]) for x in resid}
    # ホールドアウト/SC: 決定論の否定検査にだけ頼って検出されたgold候補があるか
    only_neg = []
    for r in runs:
        iid = r["instance_id"]
        for c in r["audit"]["union_candidates"]:
            if "negation_polarity_mismatch" in c["sub_reasons"] and "model" not in c["sub_reasons"]:
                is_gold = any(sa.claim_matches_def(d, c["claim_text"]) for d in runner._safety_critical_defs(iid)) if iid in sa.SC_IDS else (iid in sa.HOLDOUT_IDS)
                if is_gold:
                    only_neg.append((iid, r["sample"]))
    # 合成否定反転(er009 changed_negation hold-out)に対する決定論検査の感度(LLMがSUPPORTEDと誤判定した場合の想定)
    syn = {}
    for r in runs:
        if r["instance_id"] == "safety_er009_changed_negation":
            c = r["audit"]["union_candidates"][0]; rf = (c.get("related_fact_ids") or [""])[0]; blk = blocks_by_inst[r["instance_id"]].get(rf, "")
            syn = {"claim": c["claim_text"], "fact_id": rf, "fact_line": blk.split("\n")[0][:140], "flags_on": [k for k, v in c["flags"].items() if v],
                   "routes": c["routes"], "sub_reasons": c["sub_reasons"],
                   "orig_det_detects": bool(blk and cov.negation_mismatch({"claim_text": c["claim_text"], "text": c["claim_text"], "type": "sentence"}, [blk])),
                   "v2_det_detects": bool(blk and neg_mismatch_v2(c["claim_text"], [blk])),
                   "v2b_allLines_det_detects": bool(blk and neg_mismatch_v2(c["claim_text"], [blk], scope_all=True)), "fact_block_line_count": len(blk.split(chr(10)))}
    return {"fired_total": len(fires), "orig_reproduced_with_first_fact_only": ocnt, "v2_remaining_total": vcnt, "v2b_allLines_remaining_total": vball, "v2_remaining_unique_unit": len(uniq),
            "v2_remaining_rows": resid, "gold_or_holdout_candidates_found_only_by_negation_check": only_neg, "synthetic_negation_holdout": syn,
            "variantB_remove_check_remaining": 0}


# ---------------- 4. rep30(Stage 2以降)の構造と案別費用モデル ----------------
FIT_A, FIT_B = 0.099, 0.073  # 委任_09と同じStage 2費用fit(¥ ~ A + B x 候補数、候補範囲[0,10])


def rep30_structure():
    rep30, s2rows = defaultdict(list), []
    for p in glob.glob(f"{REP30}/instances_s*/*.json"):
        d = json.load(open(p, encoding="utf-8"))
        c1 = d["cycles"][0] if d["cycles"] else {}
        n2 = len(c1.get("stage2_results", []))
        rep30[d["instance_id"]].append({"n2": n2, "bl": c1.get("blocking_count", 0), "rw": sum(len(x.get("rewrite_records", [])) for x in d["cycles"]),
                                         "cost": d.get("total_cost_jpy", 0.0), "cycles": len(d["cycles"])})
        cl = [c for c in d["call_log"] if c.get("recovery_stage") == "stage2_second_judge" and "_c1_" in c["label"]]
        if n2 and cl:
            s2rows.append({"n2": n2, "in": sum(c["usage"]["input_tokens"] for c in cl), "cached": sum(c["usage"]["cached_input_tokens"] for c in cl),
                           "out": sum(c["usage"]["output_tokens"] for c in cl), "reas": sum(c["usage"]["reasoning_tokens"] for c in cl), "ncalls": len(cl),
                           "cost": sum(c.get("cost_jpy", 0) for c in cl)})
    bi, r2i = ols([[1, x["n2"]] for x in s2rows], [x["in"] for x in s2rows])
    bo, r2o = ols([[1, x["n2"]] for x in s2rows], [x["out"] for x in s2rows])
    bc, r2c = ols([[1, x["n2"]] for x in s2rows], [x["cost"] for x in s2rows])
    per_claim_in_cost = bi[1] * (1 - mean(x["cached"] / max(x["in"], 1) for x in s2rows)) * JPY_PER_IN_TOK + bi[1] * mean(x["cached"] / max(x["in"], 1) for x in s2rows) * JPY_PER_CACHED_TOK
    S = {"n_cycle1_instances_with_stage2": len(s2rows), "mean_calls_per_instance_cycle1": mean(x["ncalls"] for x in s2rows),
         "input_tokens_vs_n_candidates(intercept,slope)": bi, "r2_in": r2i, "output_tokens_vs_n(intercept,slope)": bo, "r2_out": r2o,
         "cost_jpy_vs_n(intercept,slope)": bc, "r2_cost": r2c,
         "per_candidate_cost_split_jpy": {"input_part": round(per_claim_in_cost, 4), "output_part(incl_reasoning)": round(bo[1] * JPY_PER_OUT_TOK, 4)},
         "note": "Stage 2は既にtitle/hook群とbody群のbatch callで、候補ごとにlocal_contextを入力へ載せる。費用の候補数依存は入力(local_context)と出力(判定+reasoning)の両方"}
    allr = [x for v in rep30.values() for x in v]
    tb, tn = sum(x["bl"] for x in allr), sum(x["n2"] for x in allr)
    nr = [x for i, v in rep30.items() if GROUP_OF.get(i) == "NORMAL" for x in v]
    rate_all = tb / tn; rate_nor = sum(x["bl"] for x in nr) / max(1, sum(x["n2"] for x in nr))
    fit = lambda n: 0.0 if n <= 0 else FIT_A + FIT_B * n
    rw = [x for x in allr if x["rw"] > 0]
    cpr = st.mean([(x["cost"] - fit(x["n2"])) / x["rw"] for x in rw])
    return rep30, S, rate_all, rate_nor, cpr, fit


def production_baseline():
    d = json.load(open(f"{OUT}/agg_production_baseline_cost_01.json", encoding="utf-8"))
    v = [x["check_plus_mustfix_jpy"] for x in d["rows"]]
    return {"n": len(v), "mean": round(sum(v) / len(v), 3), "median": round(st.median(v), 3), "min": min(v), "max": max(v), "run_02_hormuz": v[0]}


def tri_cost(n_unsure, reasoning):
    if n_unsure <= 0:
        return 0.0
    return s2p.official_cost_jpy({"input_tokens": 5000, "cached_input_tokens": 4500, "output_tokens": 300 + 40 * n_unsure + reasoning})


def run_features(r, blocks, b_sup, v2_keep):
    a = r["audit"]; iid = r["instance_id"]
    c3 = route_calls(r, "r3"); c5 = route_calls(r, "r5")
    f = {"iid": iid, "group": GROUP_OF[iid], "r3_cost": sum(c.get("cost_jpy", 0) for c in c3), "r5_cost": sum(c.get("cost_jpy", 0) for c in c5),
         "r5_reas": sum(c["usage"]["reasoning_tokens"] for c in c5), "r3_reas": sum(c["usage"]["reasoning_tokens"] for c in c3),
         "ns": sum(1 for s in a["per_route"]["r3"]["unit_status"].values() if s.startswith("SUPPORTED")), "cands": []}
    for c in a["union_candidates"]:
        sr = set(c["sub_reasons"]); model = "model" in sr
        only_neg = sr == {"negation_polarity_mismatch"}
        f["cands"].append({"routes": set(c["routes"]), "model": model, "only_neg": only_neg, "neg_kept_v2": v2_keep.get((r["sample"], iid, c["claim_text"]), True),
                           "tier": concreteness(c, blocks) if model else "DET", "fact": (c.get("related_fact_ids") or [""])[0]})
    return f


def scenario(feats, rep30, rate_all, rate_nor, cpr, fit, b_sup, B=False, D=False, E=False, A=None, R5CAP=None, RS=None, triage_reas=2500, cap10=False):
    rows = []
    for f in feats:
        cs = list(f["cands"])
        if D:
            cs = [c for c in cs if "r3" in c["routes"]]
        if B:
            cs = [c for c in cs if not (c["only_neg"] and not c["neg_kept_v2"])]
        s1 = f["r3_cost"] - (max(0.0, b_sup - 40) * f["ns"] * JPY_PER_OUT_TOK if E else 0.0)  # SUPPORTEDはunit_id+verdict+fact_idsの約40tokenだけ残す仮定
        if not D:
            s1 += f["r5_cost"] - (max(0, f["r5_reas"] - R5CAP) * JPY_PER_OUT_TOK if R5CAP else 0.0)
        if RS is not None:  # 両経路のreasoning tokenを一律RS倍にする仮定(reasoning effort引下げの感度分析、検出力への影響は未検証)
            s1 -= (1 - RS) * (f["r3_reas"] + (0 if D else f["r5_reas"])) * JPY_PER_OUT_TOK
        tri = 0.0; n_s2 = len(cs)
        if A is not None:
            conc = [c for c in cs if c["tier"] in ("CONCRETE", "DET")]
            uns = [c for c in cs if c["tier"] not in ("CONCRETE", "DET")]
            n_s2 = len(conc) + A * len(uns)
            tri = tri_cost(len(uns), triage_reas)
        rr = rep30[f["iid"]]; n2m = mean(x["n2"] for x in rr); cm = mean(x["cost"] for x in rr)
        n_eff = min(n_s2, 10) if cap10 else n_s2
        d_s2 = fit(n_eff) - fit(n2m)
        rate = rate_nor if f["group"] == "NORMAL" else rate_all
        extra_bl = rate * max(0.0, n_s2 - n2m)
        rows.append({"group": f["group"], "s1": s1, "tri": tri, "n_s2": n_s2, "d_s2": d_s2, "extra_bl": extra_bl, "rw": extra_bl * cpr, "rep30": cm,
                     "add_vs_rep30": s1 + tri + d_s2 + extra_bl * cpr})
    out = {}
    for g, sel in (("ALL42", lambda x: True), ("ARTICLE33(holdout除く)", lambda x: x["group"] != "holdout"), ("NORMAL", lambda x: x["group"] == "NORMAL"), ("SC", lambda x: x["group"] == "SC")):
        rs = [x for x in rows if sel(x)]
        add30 = mean(x["add_vs_rep30"] for x in rs)
        out[g] = {"n": len(rs), "stage1": mean(x["s1"] for x in rs), "triage": mean(x["tri"] for x in rs), "cands_to_stage2": mean(x["n_s2"] for x in rs),
                  "stage2_delta": mean(x["d_s2"] for x in rs), "extra_rewrite": mean(x["rw"] for x in rs), "expected_extra_blocking": mean(x["extra_bl"] for x in rs),
                  "add_vs_rep30": add30, "add_vs_rep24": round(mean(x["rep30"] for x in rs) + add30 - REP24_MEAN, 3),
                  "total_per_run": round(mean(x["rep30"] for x in rs) + add30, 3), "vs_production_2.77": round(mean(x["rep30"] for x in rs) + add30 - 2.77, 3)}
    return out


GRID = [("S0 現行(r3+r5、全候補)", {}), ("B 否定検査是正のみ", {"B": True}), ("D r5廃止(r3のみ)", {"D": True}), ("B+D【Safety基準未達: r3単独のモデル判定16/18】", {"B": True, "D": True}),
        ("E r3出力軽量化", {"E": True}), ("B+E", {"B": True, "E": True}), ("B+R5推論cap2000(未検証)", {"B": True, "R5CAP": 2000}),
        ("A(e=0.1)+B", {"A": 0.1, "B": True}), ("A(e=0.2)+B", {"A": 0.2, "B": True}), ("A(e=0.3)+B", {"A": 0.3, "B": True}),
        ("A(e=0.2)+B+E", {"A": 0.2, "B": True, "E": True}), ("A(e=0.2)+B+D", {"A": 0.2, "B": True, "D": True}), ("A(e=0.2)+B+D+E", {"A": 0.2, "B": True, "D": True, "E": True}),
        ("A(e=0.2)+B+E+R5cap2000(未検証)", {"A": 0.2, "B": True, "E": True, "R5CAP": 2000}),
        ("B+RS0.5(両経路reasoning半減、未検証)", {"B": True, "RS": 0.5}), ("A(e=0.2)+B+RS0.5(未検証)", {"A": 0.2, "B": True, "RS": 0.5}),
        ("A(e=0.2)+B+D+RS0.5(未検証)", {"A": 0.2, "B": True, "D": True, "RS": 0.5})]


def main():
    runs = load_runs()
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    blocks = {iid: cov.ledger_fact_blocks(insts[iid]["fixture"]["ledger_text"]) for iid in {r["instance_id"] for r in runs}}
    R = {"n_runs": len(runs), "kpi_provenance": "既存fresh出力(段階A 42 run・rep30)の再集計と仮定付き積み上げ。E2Eではない。見込みは推測を含む"}
    R["cost_rca"] = cost_rca(runs)
    R["sc_specificity"] = sc_specificity(runs, blocks)
    R["negation"] = negation_study(runs, blocks)
    R["route_model_detection"] = route_model_detection(runs)
    b_sup = R["cost_rca"]["r3_visible_regression"]["coef_tokens"][0]
    v2_keep = {}
    for r in runs:
        for c in r["audit"]["union_candidates"]:
            if set(c["sub_reasons"]) == {"negation_polarity_mismatch"}:
                rf = (c.get("related_fact_ids") or [""])[0]; blk = blocks[r["instance_id"]].get(rf, "")
                v2_keep[(r["sample"], r["instance_id"], c["claim_text"])] = bool(blk and neg_mismatch_v2(c["claim_text"], [blk]))
    rep30, S, rate_all, rate_nor, cpr, fit = rep30_structure()
    R["stage2_structure"] = S
    R["rep30_rates"] = {"blocking_rate_all": round(rate_all, 3), "blocking_rate_NORMAL": round(rate_nor, 3), "cost_per_rewrite_excl_stage2": round(cpr, 3)}
    R["production_baseline_check_plus_mustfix_jpy"] = production_baseline()
    feats = [run_features(r, blocks[r["instance_id"]], b_sup, v2_keep) for r in runs]
    R["scenarios"] = {nm: {"flags": {k: v for k, v in fl.items()}, "result": scenario(feats, rep30, rate_all, rate_nor, cpr, fit, b_sup, **fl)} for nm, fl in GRID}
    R["scenarios_cap10"] = {nm: scenario(feats, rep30, rate_all, rate_nor, cpr, fit, b_sup, cap10=True, **fl)["ARTICLE33(holdout除く)"]["add_vs_rep30"] for nm, fl in GRID}
    R["scenarios_triage_reasoning_high_4500"] = {nm: scenario(feats, rep30, rate_all, rate_nor, cpr, fit, b_sup, triage_reas=4500, **fl)["ARTICLE33(holdout除く)"]["add_vs_rep30"]
                                                 for nm, fl in GRID if "A" in fl}
    # (C) 同一fact束ね: Stage 2が既にbatch callのため、節約は入力(local_context重複)分の上限のみ
    grp = []
    for f in feats:
        if f["group"] == "holdout":
            continue
        cs = f["cands"]; facts = {c["fact"] for c in cs if c["fact"]}; nofact = sum(1 for c in cs if not c["fact"])
        grp.append((len(cs), len(facts) + nofact))
    n_c, n_g = mean(x[0] for x in grp), mean(x[1] for x in grp)
    R["batching_C"] = {"mean_candidates": n_c, "mean_distinct_fact_groups": n_g, "mergeable": round(n_c - n_g, 2),
                       "max_saving_per_article_jpy(入力分のみ上限)": round((n_c - n_g) * S["per_candidate_cost_split_jpy"]["input_part"], 3),
                       "note": "出力・reasoning分は候補ごとに必要なため束ねても減らない前提(推測)。上限であり実測ではない"}
    json.dump(R, open(f"{OUT}/loop2_cost_structure_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o))
    write_md(R)
    print(json.dumps({k: R[k] for k in ("cost_rca",) if False}, ensure_ascii=False))
    print("done")



def route_model_detection(runs):
    """gold/hold-out単位の経路別検出を『モデル判定由来(M)/決定論検査のみ(D)/無し(-)』で分ける(r3単独の見かけの18/18に決定論検査が混ざっていないか)。"""
    res = defaultdict(lambda: defaultdict(list))
    for r in runs:
        iid = r["instance_id"]
        if iid in sa.SC_IDS:
            for d in runner._safety_critical_defs(iid):
                for rt in ("r3", "r5"):
                    cs = [c for c in r["audit"]["per_route"][rt]["candidates"] if sa.claim_matches_def(d, c["claim_text"])]
                    res[d["sub_id"]][rt].append("M" if any("model" in c["sub_reasons"] for c in cs) else ("D" if cs else "-"))
        if iid in sa.HOLDOUT_IDS:
            for rt in ("r3", "r5"):
                cs = r["audit"]["per_route"][rt]["candidates"]
                res[iid.replace("safety_er009_", "")][rt].append("M" if any("model" in c["sub_reasons"] for c in cs) else ("D" if cs else "-"))
    out = {k: {rt: "".join(v) for rt, v in d.items()} for k, d in res.items()}
    n_sc = [(k, rt) for k in out for rt in ("r3", "r5") if k in ("B3", "B4-a", "B3-same@neg5", "A2A3-0", "A4-0", "A5-0")]
    tot = {rt: [sum(out[k][rt].count("M") for k in out if k in ("B3", "B4-a", "B3-same@neg5", "A2A3-0", "A4-0", "A5-0")),
                sum(len(out[k][rt]) for k in out if k in ("B3", "B4-a", "B3-same@neg5", "A2A3-0", "A4-0", "A5-0"))] for rt in ("r3", "r5")}
    return {"per_gold": out, "SC_model_judged_detection_by_route": tot,
            "note": "M=その経路のモデル判定が候補化、D=決定論検査(SUPPORTED->CANDIDATE)でのみ候補化、-=その経路では候補なし。A4-0のr3はs1/s2がD(=誤発火の決定論否定検査が偶然goldに当たっただけ)"}


def write_md(R):
    c = R["cost_rca"]; L = ["# Stage 1 ループ2 費用構造RCA・SC候補具体性・否定検査是正・案別費用見込み(委任_10、¥0)", "",
                            f"KPI provenance: {R['kpi_provenance']}。Trial専用、Production未配線、APPROVED_FOR_PRODUCTIONではない。", "",
                            "## 1. 費用構造(段階A 42 run、実測usage)", "", "| call種別 | n | 入力tok | 出力tok | うちreasoning | 可視出力tok | ¥/call | 入力(未cache)% | reasoning% | 可視出力% |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in c["by_call_type"].items():
        L.append(f"| {k} | {v['n_calls']} | {v['mean_input_tokens']:.0f} | {v['mean_output_tokens']:.0f} | {v['mean_reasoning_tokens']:.0f} | {v['mean_visible_tokens']:.0f} | {v['mean_cost_jpy']} | {v['share_in_uncached_jpy']*100:.0f} | {v['share_out_reasoning_jpy']*100:.0f} | {v['share_out_visible_jpy']*100:.0f} |")
    a = c["all_calls"]; d = c["r3_visible_decomposition_mean_tokens"]
    L += ["", f"全{a['n']} call平均¥{a['mean_jpy']}/call。費用構成: 入力{a['share_in_uncached_jpy']*100:.0f}%、reasoning {a['share_out_reasoning_jpy']*100:.0f}%、可視出力{a['share_out_visible_jpy']*100:.0f}%(output tokenが約9割)。r3の欠落ID再実行callは0回(欠落ID 0%)。失敗call {c['failed_or_retry_calls']}(r5 API失敗1+retry1)。cache命中は2 callのみ(cached=0が{c['cached_zero_calls']}/{a['n']})。単価=入力¥{c['price_jpy_per_Mtok']['in']:.1f}/Mtok、出力¥{c['price_jpy_per_Mtok']['out']:.1f}/Mtok。",
          f"r3の可視出力(平均{d['visible_mean']:.0f}tok)の回帰(R2={c['r3_visible_regression']['r2']}、n=42): SUPPORTED 1単位≒{c['r3_visible_regression']['coef_tokens'][0]:.0f}tok、CANDIDATE 1単位≒{c['r3_visible_regression']['coef_tokens'][1]:.0f}tok(issue等の文字数は単位当たりに吸収)。平均SUPPORTED {d['mean_SUPPORTED_units']}単位x{c['r3_visible_regression']['coef_tokens'][0]:.0f}={d['SUPPORTED_units_part']:.0f}tok=可視出力の{d['SUPPORTED_share_of_visible']*100:.0f}%(逐語引用+support_fact_ids+空のflags/issue等の骨格を含む。逐語引用だけの内訳は出力生文字が未保存のため分離不能=推測)。",
          f"r5の可視出力回帰(R2={c['r5_visible_regression']['r2']}): fact当たり{c['r5_visible_regression']['coef_tokens'][0]:.0f}tok、対応単位当たり{c['r5_visible_regression']['coef_tokens'][1]:.0f}tok。r5は可視出力が小さい(約2.6k)がreasoning平均7.7k tokで費用の約7割。", ""]
    s = R["stage2_structure"]; rr = R["rep30_rates"]
    L += ["## 1b. Stage 2以降の構造(rep30実測)", "",
          f"Stage 2は既にtitle/hook群とbody群のbatch call(+S1第2意見call)で、候補ごとにlocal_contextを入力へ載せる。cycle1のcall数/instance平均{s['mean_calls_per_instance_cycle1']}。候補1件当たり(回帰、n={s['n_cycle1_instances_with_stage2']}): 入力{s['input_tokens_vs_n_candidates(intercept,slope)'][1]:.0f}tok(R2 {s['r2_in']})、出力{s['output_tokens_vs_n(intercept,slope)'][1]:.0f}tok(R2 {s['r2_out']})、費用¥{s['cost_jpy_vs_n(intercept,slope)'][1]}/候補(入力分¥{s['per_candidate_cost_split_jpy']['input_part']}+出力分¥{s['per_candidate_cost_split_jpy']['output_part(incl_reasoning)']})。BLOCKING率: 全体{rr['blocking_rate_all']}、NORMAL {rr['blocking_rate_NORMAL']}。Rewrite+Recheck¥{rr['cost_per_rewrite_excl_stage2']}/回。",
          f"(C)束ね: 候補{R['batching_C']['mean_candidates']}/記事に対し関連factは{R['batching_C']['mean_distinct_fact_groups']}種(束ね可能{R['batching_C']['mergeable']}件)だが、Stage 2は既にbatchで、節約は入力分の上限¥{R['batching_C']['max_saving_per_article_jpy(入力分のみ上限)']}/記事のみ(出力・判定は候補ごと)。", ""]
    open(f"{OUT}/loop2_cost_structure_01.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    write_md2(R)


def write_md2(R):
    sp = R["sc_specificity"]; L = ["## 2. SC候補の具体性(SC 18 run、hold-out 9 run、HF-011)", "",
        "判定規則(機械、gold変更なし): strict=related_fact_idがLedgerに実在し、7種の具体要素フラグ(数値/主体/時期/確信度/因果/比較/否定)のいずれかが立つ。SEMI=factありだが具体要素フラグなし。VAGUE=fact不明/issue短い。", "",
        "| instance | claim | run | 一致候補数 | flags(要素) | related fact | 経路 | tier |", "|---|---|---|---|---|---|---|---|"]
    for x in sp["sc_rows"]:
        c = x["cands"][0]
        L.append(f"| {x['iid']} | {x['sub_id']} | s{x['sample']} | {x['n_matching']} | {','.join(k.replace('changed_', '') for k in c['flags_on'])} | {','.join(c['related_fact_ids'] or [])} | {'+'.join(c['routes'])} | {x['best_tier']} |")
    L += ["", f"SC 18件: {sp['sc_summary']['best_tier']}、LLM判定由来(sub_reasonsにmodel){sp['sc_summary']['model_judged']}/18。hold-out 9件: "
          + str({x['iid'].replace('safety_er009_', ''): x['cands'][0]['tier'] for x in sp['holdout_rows']}) + "。",
          "HF-011(監視、B2_hormuz): " + str([x['n_matching'] for x in sp['hf011_rows']]) + "(run別一致候補数。検出1/3、r3経路のみ、flags=changed_causality+changed_certainty)。",
          "", "候補全体のtier分布(LLM由来候補、strict/permissive):", "", "| 群 | strict CONCRETE | SEMI | VAGUE |", "|---|---|---|---|"]
    for g in ("SC", "B2watch", "NORMAL", "holdout"):
        t = sp["tier_by_group"][f"strict:{g}"]
        L.append(f"| {g} | {t.get('CONCRETE', 0)} | {t.get('SEMI', 0)} | {t.get('VAGUE', 0)} |")
    L += ["", f"NORMAL先頭30件ラベル(委任_09、推測)x tier: {sp['tier_by_label']}", ""]
    rm = R["route_model_detection"]
    L += ["経路別のモデル判定由来検出(M=モデル判定、D=決定論検査のみ、-=無し。run順s1,s2,s3):", "", "| gold/hold-out | r3 | r5 |", "|---|---|---|"]
    for k, v in rm["per_gold"].items():
        L.append(f"| {k} | {v.get('r3')} | {v.get('r5')} |")
    L += ["", f"SC 6件x3 run=18のモデル判定由来検出: r3 {rm['SC_model_judged_detection_by_route']['r3']}、r5 {rm['SC_model_judged_detection_by_route']['r5']}。{rm['note']}", ""]
    n = R["negation"]; syn = n["synthetic_negation_holdout"]
    L += ["## 3. 否定極性検査の是正案(オフライン再実装、checker本体は無変更)", "",
          f"旧発火{n['fired_total']}件(第1support factのみでの再現{n['orig_reproduced_with_first_fact_only']}件)。是正案a(fact側=claim行のみ、対比構文「ほどなく/ではなく/でなく/意図せず」除外、「なし」追加、英語Ledger行は英語否定語で判定、単位側の英語は'not only'除外+dislike/lack/fail to/unable追加)で残る件数={n['v2_remaining_total']}(unique {n['v2_remaining_unique_unit']})。是正案b(さらにfact block全行で否定を探す=「全行照合」)は{n['v2b_allLines_remaining_total']}件だが、合成否定反転hold-out(er009 changed_negation)に対する決定論検査の感度が失われる(下記)。案c=決定論の否定検査を外す: 残0。",
          f"合成否定反転hold-out(LLMがSUPPORTEDと誤判定した場合の仮想感度): 旧検査={syn['orig_det_detects']}、是正案a={syn['v2_det_detects']}、是正案b(全行)={syn['v2b_allLines_det_detects']}(fact block{syn['fact_block_line_count']}行に別の否定語がある)。実際のrunではこの単位はLLM両経路(r3+r5)がchanged_negation付きで検出済み(sub_reasons={syn['sub_reasons']})。gold/hold-out候補のうち決定論の否定検査だけで検出されたもの: {len(n['gold_or_holdout_candidates_found_only_by_negation_check'])}件。", "",
          "是正案a後の残り(unique単位):", "", "| instance | 単位 | 内容 | 判定(推測) |", "|---|---|---|---|"]
    seen = set()
    for x in n["v2_remaining_rows"]:
        k = (x["iid"], x["unit"])
        if k in seen:
            continue
        seen.add(k)
        jd = "cannot型の留保がLedgerに無い=真の可能性あり(PLAUSIBLE_TRUE 2件)" if "cannot" in x["claim"] else ("対比『not X』がLedger claim行に無い=Ledgerに無い主張(NORMAL先頭ラベルRと同型)" if "not" in x["claim"] or "had not" in x["claim"] else "『only/still only』=情報欠如の言い換え(FP)")
        L.append(f"| {x['iid']} | {x['unit']} | {x['claim'][:70]} | {jd} |")
    L.append("")
    L += ["## 4. 案別費用見込み(rep30同基準、¥/run。add=rep30照合比、total=rep30費用+add、vs2.77=totalと Production check+mustfix 平均2.77の差)", "",
          "仮定: 段階A 42 runの候補集合を各案で機械的に絞り直し、Stage 2費用=委任_09と同じ線形fit(¥0.099+0.073x候補)、追加BLOCKING=rep30 BLOCKING率(NORMAL 0.10/他0.289)x増分候補数、Rewrite+Recheck¥0.314/回。A=strict tierのみStage 2、他はUNSURE(triage1 callを¥0.26と仮定、escalation率e)。E=r3のSUPPORTED 1単位を40tokへ。RS/R5CAP=reasoning削減の感度(未検証)。", "",
          "| 案 | NORMAL 候補→S2 | NORMAL add | NORMAL total | NORMAL vs2.77 | 記事33 add | 記事33 vs2.77 | ALL42 add | SC add |", "|---|---|---|---|---|---|---|---|---|"]
    for nm, v in R["scenarios"].items():
        r = v["result"]; nn = r["NORMAL"]; a3 = r["ARTICLE33(holdout除く)"]; al = r["ALL42"]; sc = r["SC"]
        L.append(f"| {nm} | {nn['cands_to_stage2']} | +{nn['add_vs_rep30']} | {nn['total_per_run']} | {nn['vs_production_2.77']:+} | +{a3['add_vs_rep30']} | {a3['vs_production_2.77']:+} | +{al['add_vs_rep30']} | +{sc['add_vs_rep30']} |")
    L += ["", "注: rep24基準(0.4401)でのaddは上記add+(rep30費用-0.4401)。KPI基準点がrep24かProduction 2.77かで結論が変わるため併記。cap10(Stage 2 fitの上限10候補)でのadd(記事33): " + str({k: v for k, v in R["scenarios_cap10"].items() if k.startswith(("S0", "B+D", "A(e=0.2)+B+D", "A(e=0.2)+B)"))}), ""]
    open(f"{OUT}/loop2_cost_structure_01.md", "a", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
