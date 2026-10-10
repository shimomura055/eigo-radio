# -*- coding: utf-8 -*-
"""B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02 Phase 2a 評価 (決定論・LLM判定なし・API不使用)。
指標定義は PREREGISTRATION_02.md 3節。結果を見て定義を変えない。
  .venv\\Scripts\\python.exe -X utf8 b3r2_eval_01.py [--baseline-only]
出力: eval/eval_results_02.json, eval/blind_sheet_02.md, eval/blind_key_02.json, eval/content_dump_02.json, eval/m11_*.json
E9(R0)は本委任では実行しない(Lane A C2が編集中のjaw/er012_e/er019 runnerを読まないため)。"""
import sys, os, re, json, random, difflib, ast, statistics as st, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
T1 = os.path.abspath(os.path.join(HERE, "..", "b3_fact_instruction_separation_trial_01"))
sys.path.insert(0, T1)
from b3sep_common_01 import THEMES, PROBLEM5, theme_inputs, rj, rd, wj, wt, sha, G0
import b3r2_rank_01 as RK
B1 = RK.B1
EV = os.environ.get("B3R2_EV", f"{HERE}/eval")
RUNS = os.environ.get("B3R2_RUNS", f"{HERE}/runs")
COSTL = os.environ.get("B3R2_COST", f"{HERE}/cost_ledger_b3r2_01.jsonl")
IMP = B1.IMP
NF = RK.nfkc
LEX = re.compile(r"[一-龥ァ-ヶーA-Za-z0-9]{3,}")
# 限定表現(Storylineが断定を避ける言い回し)。委任_02で定義を固定(ROOTFIX-01時の5/18は別定義のため、C1を同じ定義で再計算して比較する)
LIMIT_RE = re.compile(r"(断定|確定して(?:いない|おらず)|確認されて(?:いない|おらず)|明らかで(?:は)?ない|とは(?:限らない|言えない|いえない)|不明|未確定|可能性|とみられ|と見られ|とされ|と報じ|にとどま|にすぎ)")
ARMS_B3 = ("C1", "D-plus", "RoleOnly")


def sel_path(arm, th, rep):
    base = f"{T1}/runs/C1" if arm == "C1" else f"{RUNS}/{arm}"
    return f"{base}/{th}/rep{rep}/selection.json"


def load_sel(arm, th, rep):
    p = sel_path(arm, th, rep)
    if os.path.exists(p):
        return rj(p)
    pf = p.replace("selection.json", "selection_failed.json")
    return {"failed": True, **rj(pf)} if os.path.exists(pf) else None


def units(arm):
    out = []
    for th in THEMES:
        ti = theme_inputs(th)
        for rep in (1, 2):
            s = load_sel(arm, th, rep)
            if s is None:
                continue
            u = {"arm": arm, "theme": th, "rep": rep, "ledger": ti["ledger"], "sel": s, "failed": bool(s.get("failed"))}
            if not u["failed"]:
                par = s["parsed"]
                u.update(ids=par.get("selected_fact_ids", []), story=par.get("selected_storyline", ""), par=par)
            out.append(u)
    return out


def J(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if (a | b) else 1.0


def mean(x):
    x = list(x)
    return round(sum(x) / len(x), 4) if x else None


def common_len(a, b):
    a, b = NF(a), NF(b)
    if not a or not b:
        return 0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b)).size


# ---------------------------------------------------------------- M1
def m1(us, c0):
    res = {"n_outputs": len(us), "failed": sum(u["failed"] for u in us)}
    ok = [u for u in us if not u["failed"]]
    counts = [len(u["ids"]) for u in ok]
    res["mean_selected"] = mean(counts)
    res["rate_3_to_5"] = round(sum(3 <= c <= 5 for c in counts) / max(1, len(counts)), 4)
    res["n_3_to_5"] = sum(3 <= c <= 5 for c in counts)
    tot = amb = cons = 0
    for u in ok:
        facts, _ = B1.parse_ledger(u["ledger"])
        for i in u["ids"]:
            if i not in facts:
                continue
            tot += 1
            amb += facts[i]["ambiguous"]
            cons += bool(facts[i].get("notes_for_writer") or facts[i].get("ambiguity_note"))
    res["selected_total"] = tot
    res["ambiguous_adoption_rate"] = round(amb / tot, 4) if tot else None
    res["constrained_adoption_rate"] = round(cons / tot, 4) if tot else None
    by = {}
    for u in ok:
        by.setdefault(u["theme"], {})[u["rep"]] = u["ids"]
    res["jaccard_rep1_vs_rep2_mean"] = mean(J(v[1], v[2]) for v in by.values() if 1 in v and 2 in v)
    res["jaccard_exact_match_themes"] = sum(1 for v in by.values() if 1 in v and 2 in v and set(v[1]) == set(v[2]))
    res["jaccard_vs_C0_mean"] = mean(J(u["ids"], c0[u["theme"]]["ids"]) for u in ok)
    return res


# ---------------------------------------------------------------- M2 / M3
def m2(us):
    rows = []
    for u in us:
        if u["failed"]:
            continue
        facts, _ = B1.parse_ledger(u["ledger"])
        story = u["story"]
        ids = [i for i in u["ids"] if i in facts]
        notes = [B1.clean(facts[i].get(k, "")) for i in ids for k in ("notes_for_writer", "ambiguity_note") if facts[i].get(k)]
        claims = "\n".join(B1.clean(facts[i]["claim"]) for i in ids)
        lex = set(LEX.findall(NF(story)))
        cov = sum(1 for w in lex if w in NF(claims)) / len(lex) if lex else 1.0
        sents = [s for s in re.split(r"(?<=。)", story) if s.strip()]
        v = RK.validate_number_ranks([], u["ledger"], ids, story)
        rows.append({"theme": u["theme"], "rep": u["rep"], "len": len(story), "len_in_75_155": 75 <= len(story) <= 155,
                     "fact_coverage": round(cov, 3), "imp_sentences": sum(bool(IMP.search(s)) for s in sents),
                     "notes_common_chars": max([common_len(story, n) for n in notes] or [0]),
                     "limit_expr": bool(LIMIT_RE.search(NF(story))),
                     "story_numbers_not_in_selected": [f for f in v["flags"] if f.startswith("STORYLINE_NUMBER_NOT_IN_SELECTED_FACTS")]})
    n = len(rows)
    res = {"n": n, "len_ok_rate": round(sum(r["len_in_75_155"] for r in rows) / n, 3) if n else None, "mean_len": mean(r["len"] for r in rows),
           "mean_fact_coverage": mean(r["fact_coverage"] for r in rows), "imp_hit_outputs": sum(r["imp_sentences"] > 0 for r in rows),
           "notes_common_ge12": sum(r["notes_common_chars"] >= 12 for r in rows), "limit_expr_count": sum(r["limit_expr"] for r in rows),
           "story_new_number_outputs": sum(bool(r["story_numbers_not_in_selected"]) for r in rows)}
    return res, rows


# ---------------------------------------------------------------- M4 (assembler)
def m4(us):
    tot = ok = 0
    imp_facts = 0
    for u in us:
        if u["failed"]:
            continue
        a = B1.assemble_D(u["ledger"], u["ids"], u["story"], BASE_VARIANT)
        facts, _ = B1.parse_ledger(u["ledger"])
        for i in a["ordered_ids"]:
            for k in ("notes_for_writer", "ambiguity_note"):
                t = B1.clean(facts[i].get(k, ""))
                if t:
                    tot += 1
                    ok += t in a["constraints_text"]
        imp_facts += sum(bool(IMP.search(s)) for ln in a["facts_text"].split("\n") for s in re.split(r"(?<=。)", ln) if s.strip())
    return {"constraints_total": tot, "constraints_exact_in_block": ok, "assembled_fact_lines_imp_hits": imp_facts}


# ---------------------------------------------------------------- M5/M6/M7/M8 : number ranks
def items_from_ranks(par, ledger, ids, story):
    nr = par.get("number_ranks") or []
    by = {}
    for r in nr:
        by.setdefault(r["fact_id"], []).append(r["surface"])
    der = RK.derive_ranks(ledger, [i for i in ids if i in B1.parse_ledger(ledger)[0]], story, surfaces_by_fact=by)
    return nr, der


def role_by_key(items):
    d = {}
    for it in items:
        k = it["key"]
        if d.get(k) != "core":
            d[k] = it["role"]
    return d


def gt_compare(th, key_roles):
    """GT(MERGED注記)に対する比較。key_roles={主数字キー:role}。GT中核の再現率/対応付け済みの一致率/適合率。"""
    ann = rj(f"{G0}/{th}/shared/annotation.json")
    gt = {}
    for g in ann["numbers"]:
        k = RK.main_numbers(g["surface"], RK.surface_kind(g["surface"]))
        if gt.get(k) != "core":
            gt[k] = g["class"]
    matched = [k for k in gt if k in key_roles]
    agree = [k for k in matched if gt[k] == key_roles[k]]
    gt_core = [k for k in gt if gt[k] == "core"]
    hit = [k for k in gt_core if key_roles.get(k) == "core"]
    arm_core_matched = [k for k in matched if key_roles[k] == "core"]
    prec = [k for k in arm_core_matched if gt[k] == "core"]
    return {"gt_n": len(gt), "gt_core": len(gt_core), "matched": len(matched), "agree": len(agree), "gt_core_hit": len(hit),
            "arm_core_matched": len(arm_core_matched), "arm_core_matched_and_gt_core": len(prec)}


def sum_gt(rows):
    s = {k: sum(r[k] for r in rows) for k in rows[0] if k not in ('theme', 'rep')} if rows else {}
    if s:
        s["agree_rate_matched"] = round(s["agree"] / s["matched"], 4) if s["matched"] else None
        s["gt_core_recall"] = round(s["gt_core_hit"] / s["gt_core"], 4) if s["gt_core"] else None
        s["core_precision_matched"] = round(s["arm_core_matched_and_gt_core"] / s["arm_core_matched"], 4) if s["arm_core_matched"] else None
    return s


BASE_VARIANT = "Dfull"      # D-base=D-full(ROOTFIX-01の事前登録規則で選択済み)


def line_texts(a):
    """組立済みFact行(Writerが読む文字列)の本文。D-fullはscope/conditions(指示調でないもの)をFact行へ移すため、数字の表記もそこから抽出する。"""
    return {fid: ln[2:] if ln.startswith("- ") else ln for fid, ln in zip(a["ordered_ids"], [x for x in a["facts_text"].split("\n") if x.strip()])}


def ddet(ledger, ids, story, assembled_text=True):
    """D-det(call 0): 決定論の表記抽出+規則導出。既定=D-base組立済みFact行+Storylineから抽出。assembled_text=Falseでclaimのみ(LLM number_ranksと同じ範囲)。"""
    ids2 = [i for i in ids if i in B1.parse_ledger(ledger)[0]]
    tb = line_texts(B1.assemble_D(ledger, ids2, story, BASE_VARIANT)) if assembled_text else None
    return RK.derive_ranks(ledger, ids2, story, with_story=True, text_by_fact=tb)


def conc_key_set(items):
    return {it["ikey"] for it in items}


def compare_llm_vs_det(der_llm, der_det, nr):
    """A5/M8: 同一入力(ids, storyline)でLLM抽出表記 vs 正規表現抽出の概念キー比較。"""
    kl, kd = conc_key_set(der_llm["items"]), conc_key_set(der_det["items"])
    rl = {}
    for it in der_llm["items"]:
        if rl.get(it["ikey"]) != "core":
            rl[it["ikey"]] = it["role"]
    rd_ = {}
    for it in der_det["items"]:
        if rd_.get(it["ikey"]) != "core":
            rd_[it["ikey"]] = it["role"]
    shared = kl & kd
    # LLM宣言role(number_ranksそのまま)と規則導出(D-det)の一致
    decl = {}
    fk = {(it["fact_id"], NF(it["surface"])): it["ikey"] for it in der_llm["items"]}
    for r in nr:
        c = fk.get((r["fact_id"], NF(r["surface"])))
        if c and decl.get(c) != "core":
            decl[c] = r["role"]
    s_llm = {(it["fact_id"], NF(it["surface"])) for it in der_llm["items"]}
    s_det = {(it["fact_id"], NF(it["surface"])) for it in der_det["items"]}
    return {"jaccard_concepts": round(J(kl, kd), 4), "n_llm": len(kl), "n_det": len(kd), "shared": len(shared),
            "llm_only_concepts": sorted(kl - kd), "det_only_concepts": sorted(kd - kl),
            "role_agree_shared_derived": sum(rl[c] == rd_[c] for c in shared),
            "role_agree_shared_declared_vs_det": sum(decl.get(c) == rd_[c] for c in shared),
            "llm_only_surfaces": sorted(s_llm - s_det), "det_only_surfaces": sorted(s_det - s_llm)}


def analyze_ranks_arm(us, arm):
    """D-plus / Sep の number_ranks 評価(M5/M6/M7/M8)。各ユニット=(theme, rep)。Sepは入力=C0 ids/story。"""
    rows, item_n, item_agree, kind_agree, kind_n = [], 0, 0, 0, 0
    gt_llm_rows, gt_der_rows = [], []
    for u in us:
        if u["failed"]:
            continue
        th = u["theme"]
        c0 = theme_inputs(th)["ev"]
        ids = u["ids"] if arm == "D-plus" else c0["selected_fact_ids"]
        story = u["story"] if arm == "D-plus" else c0["selected_storyline"]
        par = u["par"] if arm == "D-plus" else u["sel"]["parsed"]
        nr, der = items_from_ranks(par, u["ledger"], ids, story)
        dmap = {(it["fact_id"], NF(it["surface"])): it["role"] for it in der["items"]}
        for r in nr:
            item_n += 1
            item_agree += dmap.get((r["fact_id"], NF(r["surface"]))) == r["role"]
            kind_n += 1
            kind_agree += RK.surface_kind(r["surface"]) == r["kind"]
        val = RK.validate_number_ranks(nr, u["ledger"], [i for i in ids], story)
        det = RK.derive_ranks(u["ledger"], [i for i in ids if i in B1.parse_ledger(u["ledger"])[0]], story)   # Fact本文のみ(LLM number_ranksと同じ範囲)
        cmp_ = compare_llm_vs_det(der, det, nr)
        miss_items = 0
        for f_ in val["flags"]:
            if f_.startswith("MISSING_SURFACES"):
                try:
                    miss_items += len(ast.literal_eval(f_.split(":", 2)[2]))
                except Exception:   # noqa: BLE001
                    miss_items += 1
        row = {"theme": th, "rep": u["rep"], "missing_items": miss_items, "n_det_fact_items": len(det["items"]), "n_items": len(nr), "final_errors": val["errors"], "flags": val["flags"],
               "no_core": any(f == "NO_CORE" for f in val["flags"]), "eligible_concepts_by_rule": sum(1 for it in der["items"] if it["eligible"]),
               "cmp_vs_ddet": cmp_}
        rows.append(row)
        if arm == "Sep":
            llm_roles = {}
            for r in nr:
                k = RK.main_numbers(r["surface"], RK.surface_kind(r["surface"]))
                if llm_roles.get(k) != "core":
                    llm_roles[k] = r["role"]
            gt_llm_rows.append({"theme": th, "rep": u["rep"], **gt_compare(th, llm_roles)})
            gt_der_rows.append({"theme": th, "rep": u["rep"], **gt_compare(th, role_by_key(der["items"]))})
    out = {"n_outputs": len(rows), "item_n": item_n, "role_agree_with_rule_items": item_agree, "role_agree_rate": round(item_agree / item_n, 4) if item_n else None,
           "kind_agree_rate": round(kind_agree / kind_n, 4) if kind_n else None,
           "outputs_with_no_core": sum(r["no_core"] for r in rows),
           "outputs_with_no_core_but_rule_eligible": sum(r["no_core"] and r["eligible_concepts_by_rule"] > 0 for r in rows),
           "missing_items_total": sum(r["missing_items"] for r in rows), "det_fact_items_total": sum(r["n_det_fact_items"] for r in rows),
           "missing_surfaces_outputs": sum(any(f.startswith("MISSING_SURFACES") for f in r["flags"]) for r in rows),
           "surface_only_in_ledger_field_outputs": sum(any(f.startswith("SURFACE_ONLY_IN_LEDGER_FIELD") for f in r["flags"]) for r in rows),
           "final_hard_errors_outputs": sum(bool(r["final_errors"]) for r in rows),
           "storyline_new_number_outputs": sum(any(f.startswith("STORYLINE_NUMBER_NOT_IN_SELECTED_FACTS") for f in r["flags"]) for r in rows),
           "mean_jaccard_concepts_vs_ddet": mean(r["cmp_vs_ddet"]["jaccard_concepts"] for r in rows),
           "llm_only_surface_total": sum(len(r["cmp_vs_ddet"]["llm_only_surfaces"]) for r in rows),
           "det_only_surface_total": sum(len(r["cmp_vs_ddet"]["det_only_surfaces"]) for r in rows)}
    if arm == "Sep":
        out["gt_vs_llm_roles"] = sum_gt(gt_llm_rows)
        out["gt_vs_rule_derived_from_llm_surfaces"] = sum_gt(gt_der_rows)
    return out, rows


def repro_sep(us):
    by = {}
    for u in us:
        if not u["failed"]:
            by.setdefault(u["theme"], {})[u["rep"]] = u["sel"]["parsed"]["number_ranks"]
    js, js_surf, role_agree, role_n = [], [], 0, 0
    per = {}
    for th, v in by.items():
        if 1 in v and 2 in v:
            a = {(r["fact_id"], NF(r["surface"]), r["role"]) for r in v[1]}
            b = {(r["fact_id"], NF(r["surface"]), r["role"]) for r in v[2]}
            a2 = {(r["fact_id"], NF(r["surface"])) for r in v[1]}
            b2 = {(r["fact_id"], NF(r["surface"])) for r in v[2]}
            js.append(J(a, b))
            js_surf.append(J(a2, b2))
            ra = {(r["fact_id"], NF(r["surface"])): r["role"] for r in v[1]}
            rb = {(r["fact_id"], NF(r["surface"])): r["role"] for r in v[2]}
            for k in set(ra) & set(rb):
                role_n += 1
                role_agree += ra[k] == rb[k]
            per[th] = round(J(a, b), 3)
    return {"jaccard_triplets_mean": mean(js), "jaccard_surfaces_mean": mean(js_surf), "role_agree_on_shared": f"{role_agree}/{role_n}", "per_theme": per}


def repro_dplus(us):
    by = {}
    for u in us:
        if not u["failed"]:
            by.setdefault(u["theme"], {})[u["rep"]] = (u["ids"], u["par"].get("number_ranks") or [])
    js = []
    per = {}
    for th, v in by.items():
        if 1 in v and 2 in v:
            common = set(v[1][0]) & set(v[2][0])
            a = {(r["fact_id"], NF(r["surface"]), r["role"]) for r in v[1][1] if r["fact_id"] in common}
            b = {(r["fact_id"], NF(r["surface"]), r["role"]) for r in v[2][1] if r["fact_id"] in common}
            js.append(J(a, b))
            per[th] = {"common_facts": len(common), "jaccard": round(J(a, b), 3)}
    return {"jaccard_on_common_facts_mean": mean(js), "per_theme": per}


# ---------------------------------------------------------------- retries / STOP / cost / latency (M7, M9)
def retry_stats(us, arm):
    out = {"outputs": len(us), "stop": 0, "retried": 0, "retry_numberranks_only": 0, "retry_other": 0, "stop_numberranks_only": 0, "stop_other": 0, "first_attempt_error_types": {}}
    for u in us:
        s = u["sel"]
        log = s.get("attempts_log") or []
        errs_by_attempt = [a.get("validation_errors") for a in log if a.get("validation_errors") is not None]
        hard = [[e for e in (x or []) if not e.startswith("RECHECK_NOTE_MISSING")] for x in errs_by_attempt]

        def only_nr(es):
            return bool(es) and all(e.startswith("NUMBER_RANKS_") for e in es)
        if u["failed"]:
            out["stop"] += 1
            if hard and all(only_nr(h) for h in hard if h):
                out["stop_numberranks_only"] += 1
            else:
                out["stop_other"] += 1
        elif s.get("attempts", 1) > 1:
            out["retried"] += 1
            if hard and only_nr(hard[0]):
                out["retry_numberranks_only"] += 1
            else:
                out["retry_other"] += 1
        for h in hard[:1]:
            for e in h:
                t = re.split(r"[:\[]", e)[0] if not e.startswith("NUMBER_RANKS_") else "NUMBER_RANKS_" + re.split(r"[:]", e[len("NUMBER_RANKS_"):])[0]
                out["first_attempt_error_types"][t] = out["first_attempt_error_types"].get(t, 0) + 1
    return out


def cost_latency(arm_name):
    p = COSTL
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if os.path.exists(p) else []
    rows = [r for r in rows if r["arm"] == arm_name]
    if not rows:
        return None
    lat = sorted(r["latency_seconds"] for r in rows if r.get("latency_seconds") is not None) or [0.0]
    return {"records": len(rows), "total_jpy": round(sum(r["jpy"] for r in rows), 3), "mean_jpy_per_record": mean(r["jpy"] for r in rows),
            "max_jpy": max(r["jpy"] for r in rows), "latency_mean": mean(lat), "latency_p95": lat[min(len(lat) - 1, int(len(lat) * 0.95))], "latency_max": lat[-1]}


def baseline_c1_cost():
    rows = [json.loads(l) for l in open(f"{T1}/cost_ledger_b3sep_01.jsonl", encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r["arm"] == "C1" and r["kind"] == "b3"]
    return {"records": len(rows), "mean_jpy": mean(r["jpy"] for r in rows), "latency_mean": mean(r["latency_seconds"] for r in rows)}


def usage_stats(arm):
    base = f"{RUNS}/{arm}"
    tin = tout = n = rs = 0
    if not os.path.isdir(base):
        return None
    for th in THEMES:
        for rep in (1, 2):
            for nm in ("selection.json", "selection_failed.json"):
                p = f"{base}/{th}/rep{rep}/{nm}"
                if os.path.exists(p):
                    for r in rj(p).get("usage_rows", []):
                        tin += r.get("input_tokens") or 0
                        tout += r.get("output_tokens") or 0
                        rs += r.get("reasoning_tokens") or 0
                        n += 1
    return {"api_rows": n, "mean_in": round(tin / n) if n else None, "mean_out": round(tout / n) if n else None, "mean_reasoning": round(rs / n) if n else None}


# ---------------------------------------------------------------- M11 (existing annotation checker)
def orig_surface(text, surface):
    norm, idx = RK._norm_with_map(text)
    s = NF(surface)
    ps = RK.find_all(norm, s)
    if not ps:
        return None
    a = ps[0]
    return text[idx[a]: idx[a + len(s) - 1] + 1]


def build_annotated(ledger, ids, story, der, variant="Dmin"):
    a = B1.assemble_D(ledger, ids, story, BASE_VARIANT)
    role_s = {}
    for it in der["items"]:
        s = NF(it["surface"])
        if role_s.get(s) != "core":
            role_s[s] = it["role"]
    lines = a["facts_text"].split("\n")
    out_lines = []
    n = 0
    for ln in lines:
        if not ln.strip():
            out_lines.append(ln)
            continue
        n += 1
        fid = a["ordered_ids"][n - 1]
        body = ln[2:] if ln.startswith("- ") else ln
        its = [{"surface": it["surface"], "role": role_s[NF(it["surface"])]} for it in der["items"] if it["fact_id"] == fid]
        out_lines.append("- 【事実%d】" % n + RK.insert_marks(body, its))
    story_m = RK.insert_marks(story, [{"surface": s, "role": r} for s, r in role_s.items()])
    annotated = "# Selected Fact Brief\n\n## Storyline\n" + story_m + "\n\n## Selected Facts\n" + "\n".join(out_lines)
    # sidecar: 同じ表記(NFKC)は1項目。ledger_idsは表記を持つ全Fact。概念=derive_ranksの束ね(同表記/同Factのキー一致・包含)
    full_plain = a["brief_md"]
    nums, seen, cid = [], {}, {}
    for it in der["items"]:
        s_ = NF(it["surface"])
        cid.setdefault(it["concept"], "C%d" % (len(cid) + 1))
        if s_ in seen:
            seen[s_]["ledger_ids"] = sorted(set(seen[s_]["ledger_ids"]) | {it["fact_id"]})
            continue
        osf = orig_surface(full_plain, it["surface"]) or it["surface"]
        seen[s_] = {"surface": osf, "kind": it["kind"], "class": role_s[s_], "concept": cid[it["concept"]], "ledger_ids": [it["fact_id"]], "role": ""}
        nums.append(seen[s_])
    sidecar = {"slug": "b3r2", "annotator": "DETERMINISTIC", "spec_sha256": None, "brief_sha256": hashlib.sha256(a["brief_md"].encode("utf-8")).hexdigest(),
               "facts": [{"n": i + 1, "ledger_ids": [fid]} for i, fid in enumerate(a["ordered_ids"])], "numbers": nums, "unmapped_claims": [], "annotation_notes": []}
    return a["brief_md"], annotated, sidecar


def m11(kind_label, items_fn):
    sys.path.insert(0, f"{os.path.abspath(os.path.join(HERE, '..'))}/factlock_astra_e2e_trial_01")
    import b3_annotation_check_01 as chk
    res = {}
    for th in THEMES:
        got = items_fn(th)
        if got is None:
            continue
        ledger, ids, story, der = got
        brief, ann, side = build_annotated(ledger, ids, story, der)
        r = chk.run(brief, ann, ledger, side, spec_sha256=None, brief_sha256=side["brief_sha256"])
        probs = {k: v.get("problems", []) for k, v in r.items() if isinstance(v, dict) and v.get("problems")}
        res[th] = {"verdict": r["verdict"], "problems": probs, "n_numbers": len(side["numbers"]), "skipped": r.get("skipped")}
        wt(f"{EV}/m11/{kind_label}/{th}_annotated.md", ann)
        wj(f"{EV}/m11/{kind_label}/{th}_sidecar.json", side)
        wj(f"{EV}/m11/{kind_label}/{th}_check.json", r)
    return res


def categorize_problem(p):
    for key, name in (("annotator", "meta:annotator"), ("spec_sha256", "meta:spec_sha"), ("上限", "rule:cap_or_priority"), ("付け漏れ", "rule:core_missed"),
                      ("適格性なし", "rule:core_not_eligible"), ("分類漏れ", "mark:unclassified_digits"), ("印の不一致", "mark:mismatch"),
                      ("分類衝突", "mark:class_conflict"), ("別概念", "concept:bundling"), ("kind", "kind"), ("本文に", "surface_absent"), ("台帳", "ledger_mapping")):
        if key in p:
            return name
    return "other"


def summarize_m11(res):
    cnt, passes = {}, 0
    for th, r in res.items():
        passes += r["verdict"] == "PASS"
        for k, ps in r["problems"].items():
            for p in ps:
                c = categorize_problem(p)
                cnt[c] = cnt.get(c, 0) + 1
    return {"themes": len(res), "pass": passes, "problem_categories": cnt}


# ---------------------------------------------------------------- Blind sheet
def blind_sheet(c0):
    rnd = random.Random(20261010)
    key, lines = {}, ["# Blind目視シート(腕名は伏せてある。対応表は blind_key_02.json)\n", "Storyline比較(9テーマ)とcore集合(9テーマ)。各ブロックの腕はランダムID。判定は人手(Claude側)で行う。\n"]
    for th in THEMES:
        lines.append(f"\n## テーマ {th}\n")
        cand = []
        for arm in ("C1", "D-plus", "RoleOnly"):
            s = load_sel(arm, th, 1)
            if s and not s.get("failed"):
                cand.append((arm, s["parsed"]["selected_storyline"], s["parsed"]["selected_fact_ids"]))
        cand.append(("C0", c0[th]["story"], c0[th]["ids"]))
        rnd.shuffle(cand)
        ledger = theme_inputs(th)["ledger"]
        facts, _ = B1.parse_ledger(ledger)
        for k, (arm, story, ids) in enumerate(cand):
            bid = f"S-{th[:4]}-{chr(65 + k)}"
            key[bid] = {"arm": arm, "theme": th}
            lines.append(f"- [{bid}] Storyline: {story}\n  採用Fact: {', '.join(ids)}\n")
        # core集合
        sets = []
        c0i = c0[th]
        sets.append(("D-det", ddet(ledger, c0i["ids"], c0i["story"]), c0i["story"]))
        for arm in ("D-plus", "Sep"):
            s = load_sel(arm, th, 1)
            if s and not s.get("failed"):
                if arm == "D-plus":
                    ids, story, par = s["parsed"]["selected_fact_ids"], s["parsed"]["selected_storyline"], s["parsed"]
                else:
                    ids, story, par = c0i["ids"], c0i["story"], s["parsed"]
                nr, der = items_from_ranks(par, ledger, ids, story)
                sets.append((arm + "(LLM宣言role)", {"items": [{"fact_id": r["fact_id"], "surface": r["surface"], "role": r["role"]} for r in nr]}, story))
        rnd.shuffle(sets)
        for k, (arm, der, story) in enumerate(sets):
            bid = f"R-{th[:4]}-{chr(65 + k)}"
            key[bid] = {"arm": arm, "theme": th}
            core = [f"{i['surface']}({i['fact_id']})" for i in der["items"] if i["role"] == "core"]
            per = [i["surface"] for i in der["items"] if i["role"] != "core"]
            lines.append(f"- [{bid}] 中核: {', '.join(core) or '(なし)'}\n  周辺: {', '.join(per) or '(なし)'}\n  (Storyline: {story})\n")
    wt(f"{EV}/blind_sheet_02.md", "\n".join(lines))
    wj(f"{EV}/blind_key_02.json", key)


# ---------------------------------------------------------------- main
def main():
    baseline_only = "--baseline-only" in sys.argv
    os.makedirs(EV, exist_ok=True)
    c0 = {}
    for th in THEMES:
        ev = theme_inputs(th)["ev"]
        c0[th] = {"ids": ev["selected_fact_ids"], "story": ev["selected_storyline"]}
    out = {"models": "gpt-6-luna (B3系・Sep; Sol条件付き)", "e9": "NOT_EXECUTED_IN_THIS_DELEGATION (Phase 2b)", "arms": {}}
    A = {a: units(a) for a in ARMS_B3}
    A["Sep"] = units("Sep")
    A["SepSol"] = units("SepSol")
    # ---- C0をunit化(参考)
    c0u = [{"arm": "C0", "theme": th, "rep": 0, "ledger": theme_inputs(th)["ledger"], "failed": False, "ids": c0[th]["ids"], "story": c0[th]["story"],
            "par": {}, "sel": {}} for th in THEMES]
    out["M1"] = {a: m1(A[a], c0) for a in ARMS_B3 if A[a]}
    out["M1"]["C0_reference"] = {"mean_selected": mean(len(x["ids"]) for x in c0u)}
    out["M2"], m2rows = {}, {}
    for a in ARMS_B3 + ("C0",):
        us = A[a] if a != "C0" else c0u
        if us:
            out["M2"][a], m2rows[a] = m2(us)
    out["M4"] = {a: m4(A[a]) for a in ("D-plus", "RoleOnly") if A[a]}
    out["retry"] = {a: retry_stats(A[a], a) for a in ("D-plus", "RoleOnly", "Sep", "SepSol") if A[a]}
    out["cost_latency"] = {a: cost_latency(a) for a in ("D-plus", "RoleOnly", "Sep", "SepSol")}
    out["cost_latency"]["C1_baseline"] = baseline_c1_cost()
    out["usage"] = {a: usage_stats(a) for a in ("D-plus", "RoleOnly", "Sep", "SepSol")}
    rank_rows = {}
    for a in ("D-plus", "Sep", "SepSol"):
        if A[a]:
            out.setdefault("M5_M6_M7_M8", {})[a], rank_rows[a] = analyze_ranks_arm(A[a], "D-plus" if a == "D-plus" else "Sep")
    if A["Sep"]:
        out["M8_repro_Sep"] = repro_sep(A["Sep"])
    if A["D-plus"]:
        out["M8_repro_Dplus_common_facts"] = repro_dplus(A["D-plus"])
    # ---- D-det (call 0) on C0 ids/storyline: GT comparison + determinism check
    rows, rows2 = [], []
    det_det = True
    for th in THEMES:
        ti = theme_inputs(th)
        d1 = ddet(ti["ledger"], c0[th]["ids"], c0[th]["story"])
        d2 = ddet(ti["ledger"], c0[th]["ids"], c0[th]["story"])
        det_det &= [(i["surface"], i["role"]) for i in d1["items"]] == [(i["surface"], i["role"]) for i in d2["items"]]
        rows.append({"theme": th, **gt_compare(th, role_by_key(d1["items"]))})
    out["D_det_GT"] = {"per_theme": rows, "total": sum_gt(rows), "deterministic_rerun_equal": det_det,
                       "gt_core_distribution": {r["theme"]: r["gt_core"] for r in rows}, "note": "GT=C0 brief注記(MERGED)。D-detの既知値(予備プローブと同系統)。GTは人間正解ではない"}
    # ---- M11
    m11res = {}
    m11res["D-det_on_C0"] = m11("ddet_c0", lambda th: (theme_inputs(th)["ledger"], c0[th]["ids"], c0[th]["story"], ddet(theme_inputs(th)["ledger"], c0[th]["ids"], c0[th]["story"])))

    def dplus_items(th):
        u = [x for x in A["D-plus"] if x["theme"] == th and x["rep"] == 1 and not x["failed"]]
        if not u:
            return None
        u = u[0]
        nr, der = items_from_ranks(u["par"], u["ledger"], u["ids"], u["story"])
        return (u["ledger"], u["ids"], u["story"], der)
    if A["D-plus"]:
        m11res["D-plus_rep1"] = m11("dplus_rep1", dplus_items)
        m11res["D-det_on_Dplus_rep1"] = m11("ddet_dplus1", lambda th: (lambda u: None if not u else (u[0]["ledger"], u[0]["ids"], u[0]["story"], ddet(u[0]["ledger"], u[0]["ids"], u[0]["story"])))(
            [x for x in A["D-plus"] if x["theme"] == th and x["rep"] == 1 and not x["failed"]]))
    out["M11"] = {k: {"summary": summarize_m11(v), "per_theme": v} for k, v in m11res.items()}
    # ---- content dump for Claude-side analysis
    dump = {"ddet_items": {}, "llm_vs_det": {}}
    for th in THEMES:
        ti = theme_inputs(th)
        d1 = ddet(ti["ledger"], c0[th]["ids"], c0[th]["story"])
        dump["ddet_items"][th] = [{k: (i[k] if k != "key" else str(i[k])) for k in ("fact_id", "surface", "kind", "role", "eligible", "concept")} for i in d1["items"]]
        dump["ddet_items"][th + "__capped_off"] = d1["capped_off"]
    for a, rr in rank_rows.items():
        dump["llm_vs_det"][a] = [{"theme": r["theme"], "rep": r["rep"], "flags": r["flags"], "llm_only_surfaces": r["cmp_vs_ddet"]["llm_only_surfaces"], "det_only_surfaces": r["cmp_vs_ddet"]["det_only_surfaces"],
                                 "jaccard": r["cmp_vs_ddet"]["jaccard_concepts"]} for r in rr]
    # ---- 判定(事前登録の基準を機械的に適用。最終判定は人手目視後)
    out["m2_rows"] = m2rows
    wj(f"{EV}/eval_results_02.json", out)
    wj(f"{EV}/content_dump_02.json", dump)
    if not baseline_only:
        blind_sheet(c0)
    print(json.dumps({k: out[k] for k in ("M1", "M2", "M4", "retry", "cost_latency", "usage") if k in out}, ensure_ascii=False, indent=1)[:6000])
    print(json.dumps(out.get("M5_M6_M7_M8", {}), ensure_ascii=False, indent=1)[:3000])
    print(json.dumps(out["D_det_GT"]["total"], ensure_ascii=False))
    print(json.dumps({k: v["summary"] for k, v in out["M11"].items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
