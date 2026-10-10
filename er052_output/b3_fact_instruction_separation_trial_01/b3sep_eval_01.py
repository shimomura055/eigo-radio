# -*- coding: utf-8 -*-
"""E1-E8, E10 evaluation (deterministic; no LLM). Run: .venv/Scripts/python.exe -X utf8 b3sep_eval_01.py
Outputs: eval/eval_results_02.json, eval/blind_outputs_02.md (+ blind_key_02.json), eval/side_by_side_02.md, eval/e5_missing_02.json
Definitions follow PREREGISTRATION_02.md section 3 (not changed after seeing results)."""
import sys, os, re, json, unicodedata, random, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b3sep_common_01 import *
import b3sep_build_01 as B
import er052_factlock_astra_e2e_runner_01 as run
sys.path.insert(0, f"{REPO}/er052_output/factlock_astra_e2e_trial_01")
import b3_annotation_check_01 as chk

EV = f"{HERE}/eval"
NUM = re.compile(r"\d[\d,\.]*")
LEX = re.compile(r"[一-龥ァ-ヶーA-Za-z0-9]{3,}")
CAUSAL = ["ため", "から", "により", "受け", "原因", "理由", "ことで"]
DATE = re.compile(r"\d+月\d+日")
SENT = re.compile(r"[^。\n]+。?")


def nf(s):
    return unicodedata.normalize("NFKC", s or "")


def num_tokens(s):
    out = set()
    for t in NUM.findall(nf(s)):
        t = t.replace(",", "").rstrip(".")
        if not t:
            continue
        out.add(t.lstrip("0") or "0")
    return out


def lex_tokens(s):
    return set(LEX.findall(nf(s)))


def sentences(facts_text):
    out = []
    for ln in facts_text.split("\n"):
        ln = re.sub(r"^\s*-\s*", "", ln).strip()
        for m in SENT.finditer(ln):
            s = m.group(0).strip()
            if s:
                out.append(s)
    return out


def sel_fields(facts, ids):
    return "\n".join(" ".join(str(v) for k, v in facts[i].items() if k not in ("tag", "ambiguous")) for i in ids if i in facts)


def load_units():
    """Return list of outputs: {arm, theme, rep, ids, storyline, facts_text, constraints_text, news_field, brief_md}"""
    units = []
    for th in THEMES:
        ti = theme_inputs(th)
        ev = ti["ev"]
        story, facts = run.parse_brief_md(ti["brief"])
        units.append({"arm": "C0", "theme": th, "rep": 0, "ids": ev["selected_fact_ids"], "storyline": story, "facts_text": facts + "\n", "constraints_text": "", "ledger": ti["ledger"]})
        for arm in ("C1", "Aprime"):
            for rep in (1, 2):
                p = f"{HERE}/runs/{arm}/{th}/rep{rep}/selection.json"
                if not os.path.exists(p):
                    continue
                sj = rj(p)
                par = sj["parsed"]
                if arm == "C1":
                    md = rd(f"{HERE}/runs/{arm}/{th}/rep{rep}/selected_brief_raw.md")
                    s, f = run.parse_brief_md(md)
                    units.append({"arm": "C1", "theme": th, "rep": rep, "ids": par["selected_fact_ids"], "storyline": s, "facts_text": f + "\n", "constraints_text": "",
                                  "ledger": ti["ledger"], "attempts": sj["attempts"]})
                else:
                    a = B.assemble_Aprime(ti["ledger"], par["selected_fact_ids"], par["selected_storyline"], par["selected_fact_brief"])
                    units.append({"arm": "Aprime", "theme": th, "rep": rep, "ids": a["ordered_ids"], "storyline": par["selected_storyline"], "facts_text": a["facts_text"],
                                  "constraints_text": a["constraints_text"], "constraint_items": a["constraint_items"], "ledger": ti["ledger"], "attempts": sj["attempts"],
                                  "raw_brief": par["selected_fact_brief"]})
    return units


def build_D(u, var):
    return B.assemble_D(u["ledger"], u["ids"], u["storyline"], var)


def e1(units, dunits):
    res = {}
    for arm in ("C0", "C1", "Aprime", "Dmin", "Dfull"):
        us = [x for x in (units if arm in ("C0", "C1", "Aprime") else dunits[arm]) if arm in ("Dmin", "Dfull") or x["arm"] == arm]
        n_out, n_hit, hits = 0, 0, []
        for u in us:
            hh = [s for s in sentences(u["facts_text"]) if B.IMP.search(s)]
            n_out += 1
            n_hit += bool(hh)
            hits += [{"theme": u["theme"], "rep": u["rep"], "sentence": s} for s in hh]
        res[arm] = {"outputs": n_out, "outputs_with_hit": n_hit, "hits": hits}
    return res


def e2(units, dunits):
    res = {}
    def measure(u, cons_text, mode):
        facts, _ = B.parse_ledger(u["ledger"])
        tot = ok = 0
        miss = []
        for i in u["ids"]:
            nt = B.clean(facts[i].get("notes_for_writer", ""))
            if not nt:
                continue
            tot += 1
            if mode == "exact":
                hit = nt in cons_text
            else:
                m = difflib.SequenceMatcher(None, nt, u["facts_text"], autojunk=False).find_longest_match(0, len(nt), 0, len(u["facts_text"]))
                hit = m.size >= min(12, len(nt))
            ok += hit
            if not hit:
                miss.append(i)
        return tot, ok, miss
    for arm in ("C0", "C1"):
        t = o = 0
        for u in [x for x in units if x["arm"] == arm]:
            a, b, _ = measure(u, "", "fuzzy")
            t += a; o += b
        res[arm] = {"notes_total": t, "notes_reaching_writer_12char": o}
    t = o = 0; miss_all = []
    for u in [x for x in units if x["arm"] == "Aprime"]:
        a, b, m = measure(u, u["constraints_text"], "exact"); t += a; o += b; miss_all += [(u["theme"], u["rep"], m)] if m else []
    res["Aprime"] = {"notes_total": t, "notes_in_constraints_exact": o, "missing": miss_all}
    for var in ("Dmin", "Dfull"):
        t = o = 0
        for u in dunits[var]:
            a, b, _ = measure(u, u["constraints_text"], "exact"); t += a; o += b
        res[var] = {"notes_total": t, "notes_in_constraints_exact": o}
    return res


def e3_e4(arm_units):
    out = {"outputs": 0, "num_missing_total": 0, "num_claim_total": 0, "new_numbers": [], "missing_numbers": [], "lex_missing": [], "causal_increase": [], "date_order_diff": []}
    for u in arm_units:
        facts, _ = B.parse_ledger(u["ledger"])
        ids = [i for i in u["ids"] if i in facts]
        claims = "\n".join(B.clean(facts[i]["claim"]) for i in ids)
        ft = u["facts_text"]
        cn, fn = num_tokens(claims), num_tokens(ft)
        allf = num_tokens(sel_fields(facts, ids))
        miss, new = sorted(cn - fn), sorted(fn - allf)
        out["outputs"] += 1
        out["num_claim_total"] += len(cn)
        out["num_missing_total"] += len(miss)
        if miss:
            out["missing_numbers"].append({"theme": u["theme"], "rep": u["rep"], "tokens": miss})
        if new:
            out["new_numbers"].append({"theme": u["theme"], "rep": u["rep"], "tokens": new})
        lm = sorted(lex_tokens(claims) - {t for t in lex_tokens(claims) if t in nf(ft)})
        if lm:
            out["lex_missing"].append({"theme": u["theme"], "rep": u["rep"], "n": len(lm), "tokens": lm[:40]})
        cc = sum(nf(claims).count(w) for w in CAUSAL)
        cf = sum(nf(ft).count(w) for w in CAUSAL)
        if cf > cc:
            out["causal_increase"].append({"theme": u["theme"], "rep": u["rep"], "claim": cc, "facts": cf})
        dc, df = DATE.findall(nf(claims)), DATE.findall(nf(ft))
        order = lambda l: [x for k, x in enumerate(l) if x not in l[:k]]
        if order(dc) != order(df):
            out["date_order_diff"].append({"theme": u["theme"], "rep": u["rep"], "claims": order(dc), "facts": order(df)})
    return out


def e5(units, dunits):
    res = {}
    detail = {}
    for var in ("Dmin", "Dfull"):
        tot = {1: 0, 2: 0, 3: 0}
        rows = []
        for u, d in zip([x for x in units if x["arm"] in ("C0", "C1")], dunits[var]):
            facts, order = B.parse_ledger(u["ledger"])
            ids = set(u["ids"])
            S = nf(sel_fields(facts, [i for i in order if i in ids]))
            O = nf("\n".join(sel_fields(facts, [i]) for i in order if i not in ids))
            new = nf(d["facts_text"] + d["constraints_text"])
            toks = lex_tokens(u["facts_text"]) | num_tokens(u["facts_text"])
            miss = {1: [], 2: [], 3: []}
            for t in sorted(toks):
                if t in new:
                    continue
                if t in num_tokens(new):
                    continue
                miss[1 if t in S else 2 if t in O else 3].append(t)
            for k in miss:
                tot[k] += len(miss[k])
            rows.append({"arm": u["arm"], "theme": u["theme"], "rep": u["rep"], "grounded_in_selected": miss[1], "other_fact_only": miss[2], "not_in_ledger": miss[3]})
        res[var] = {"grounded_in_selected_fact_loss": tot[1], "other_fact_only": tot[2], "not_in_ledger_B3_rewording_or_new": tot[3]}
        detail[var] = rows
    wj(f"{EV}/e5_missing_02.json", detail)
    return res


def e6(dunits):
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er052_factlock_writer_trial_01_run as fl
    out = {"outputs": 0, "fails": [], "paths": {}}
    saved = fl.apply_factlock_patches()
    try:
        for var in ("Dmin", "Dfull"):
            for u in dunits[var]:
                out["outputs"] += 1
                d = u
                fail = []
                story, facts = run.parse_brief_md(d["brief_md"])
                if not (story and facts):
                    fail.append("parse_brief_md")
                if "【" in d["facts_text"]:
                    fail.append("bracket_in_fact_lines")
                ann = run.dryrun_annotate(d["brief_md"])
                n_tag = len(re.findall(r"【事実\d+】", ann))
                if n_tag != len(d["ordered_ids"]):
                    fail.append(f"tags {n_tag} != facts {len(d['ordered_ids'])}")
                _, facts_ann = run.parse_brief_md(ann)
                news = B.compose_news_field(facts_ann, d["constraints_text"])
                # (a) R0 news field
                pa = jaw.build_original_prompt(story, news)
                if d["constraints_text"] and pa.count(B.CONS_HEADING) != 1:
                    fail.append("constraint_block_count_in_R0_prompt")
                pre, post = pa.split("[ニュース]\n", 1)[0], pa.split(news, 1)[1]
                pre0, post0 = jaw.build_original_prompt(story, "XX").split("[ニュース]\n", 1)[0], jaw.build_original_prompt(story, "XX").split("XX", 1)[1]
                if pre != pre0 or post != post0:
                    fail.append("R0_template_prefix_suffix_differs_from_production_builder")
                # (b) er019 runner L159/174/339/361: selected_fact_brief_text passed to run_ja_writer -> jaw (Trial: writer_news_field_text)
                ev = json.loads(json.dumps(d["evidence"], ensure_ascii=False))
                nb = B.compose_news_field(ev["selected_fact_brief_text"], ev["writer_constraints_text"])
                if jaw.build_original_prompt(story, nb) != jaw.build_original_prompt(story, ev["writer_news_field_text"]):
                    fail.append("path_b_er019_runner")
                # (c) er012_e regen L1185: fact_evidence.get(...) after JSON round trip (disk format)
                ev2 = json.loads(json.dumps(ev, ensure_ascii=False))
                if jaw.build_original_prompt(story, ev2["writer_news_field_text"]) != jaw.build_original_prompt(story, nb):
                    fail.append("path_c_er012e_regen")
                # (d) W-1: md_facts_of_json / annotated_json_from / parse_brief_md / dev adapter
                jo = {"selected_storyline": story, "selected_fact_brief_text": ev["selected_fact_brief_text"]}
                if run.md_facts_of_json(jo) != d["facts_text"].strip("\n"):
                    fail.append("md_facts_of_json")
                aj = run.annotated_json_from(jo, ann)
                if B.compose_news_field(aj["selected_fact_brief_text"].rstrip("\n") + "\n", d["constraints_text"]).strip() != news.strip():
                    fail.append("annotated_json_from_route")
                try:
                    import er052_open233_polysemy_nb_dev_01 as dev
                    if tuple(dev.parse_brief_md(d["brief_md"])) != tuple(run.parse_brief_md(d["brief_md"])):
                        fail.append("dev_adapter_parse_differs")
                    dev_checked = True
                except Exception as ex:  # noqa
                    dev_checked = f"not_run:{type(ex).__name__}:{str(ex)[:80]}"
                out["paths"]["dev_adapter"] = dev_checked
                if fail:
                    out["fails"].append({"variant": var, "theme": u["theme"], "ids": d["ordered_ids"], "fail": fail})
    finally:
        fl.restore_factlock_patches(saved)
    if os.path.exists(f"{HERE}/eval/_tmp_brief.md"):
        os.remove(f"{HERE}/eval/_tmp_brief.md")
    return out


def e7(dunits):
    rows = []
    for var in ("Dmin", "Dfull"):
        bad = 0
        for d in dunits[var]:
            ann = run.dryrun_annotate(d["brief_md"])
            ca, cd = chk.check_a(d["brief_md"], ann), chk.check_d(ann)
            idmap = dict(zip(range(1, len(d["ordered_ids"]) + 1), d["ordered_ids"]))
            ok = ca["status"] in ("PASS", "PASS_LAYOUT_NORMALIZED") and cd["status"] == "PASS" and cd["fact_numbers"] == list(idmap)
            bad += (not ok)
            if not ok:
                rows.append({"variant": var, "theme": d["theme"], "check_a": ca["status"], "check_d": cd})
        rows.append({"variant": var, "outputs": len(dunits[var]), "not_ok": bad})
    return rows


def e10(units, dunits):
    HEDGE = re.compile(r"確定|断定|確認でき|不明|とは限|分から|否定しない|未確認")
    res = {}
    for var in ("Dmin", "Dfull"):
        tot = a_ok = b_ok = 0
        for d in dunits[var]:
            facts, _ = B.parse_ledger(d["ledger"])
            for n, i in enumerate(d["ordered_ids"], 1):
                if not facts[i]["ambiguous"]:
                    continue
                tot += 1
                line = d["facts_text"].split("\n")[n - 1]
                a_ok += B.AMB_QUALIFIER in line
                nt = B.clean(facts[i].get("ambiguity_note", ""))
                b_ok += (not nt) or (nt in d["constraints_text"])
        res[var] = {"ambiguous_facts_selected": tot, "qualifier_in_fact_line": a_ok, "ambiguity_note_in_constraints_or_none": b_ok}
    for arm in ("C0", "C1", "Aprime"):
        tot = hedge = 0
        for u in [x for x in units if x["arm"] == arm]:
            facts, _ = B.parse_ledger(u["ledger"])
            amb = [i for i in u["ids"] if i in facts and facts[i]["ambiguous"]]
            if not amb:
                continue
            for i in amb:
                tot += 1
            hedge += bool(HEDGE.search(u["facts_text"] + u["constraints_text"]))
        res[arm] = {"ambiguous_facts_selected": tot, "outputs_with_hedge_wording_any": hedge,
                    "note": "hedge wording is theme-level regex (any hedge anywhere in brief), human check needed"}
    return res


def e1b(units, dunits):
    """Supplementary (added after the blind reading; not in PREREGISTRATION_02): ledger-internal terms / fact IDs / Storyline duplicate line inside the Facts text."""
    pat = {"ledger_term": re.compile(r"Ledger|台帳"), "fact_id": re.compile(r"(?<![A-Za-z0-9])[A-Z]{1,8}(?:-[A-Z]{1,4})?-?\d{1,4}(?![A-Za-z0-9])"),
           "storyline_dup": re.compile(r"^\s*(?:-\s*)?Storyline[:：]", re.M)}
    out = {}
    for arm, us in (("C0", [u for u in units if u["arm"] == "C0"]), ("C1", [u for u in units if u["arm"] == "C1"]), ("Aprime", [u for u in units if u["arm"] == "Aprime"]),
                    ("Dmin", dunits["Dmin"]), ("Dfull", dunits["Dfull"])):
        row = {"outputs": len(us)}
        for k, rx in pat.items():
            hit = []
            for u in us:
                ids = set(u["ids"])
                m = [x for x in rx.findall(u["facts_text"]) ] if k != "fact_id" else [x for x in rx.findall(u["facts_text"]) if x in ids or re.fullmatch(r"[A-Z]{1,8}(?:-[A-Z]{1,4})?-?\d{1,4}", x) and x in ids]
                if (k != "fact_id" and rx.search(u["facts_text"])) or (k == "fact_id" and m):
                    hit.append(f"{u['theme']}/rep{u['rep']}")
            row[k] = {"outputs": len(hit), "which": hit}
        out[arm] = row
    return out


def e8():
    L = f"{HERE}/cost_ledger_b3sep_01.jsonl"
    rows = [json.loads(l) for l in open(L, encoding="utf-8") if l.strip()] if os.path.exists(L) else []
    out = {}
    for arm in sorted({r["arm"] for r in rows}):
        rr = [r for r in rows if r["arm"] == arm]
        out[arm] = {"calls": len(rr), "jpy_total": round(sum(r["jpy"] for r in rr), 3), "jpy_mean": round(sum(r["jpy"] for r in rr) / len(rr), 4),
                    "latency_mean_s": round(sum(r["latency_seconds"] for r in rr) / len(rr), 1), "retried": sum(1 for r in rr if r.get("attempts", 1) > 1)}
    out["_total_jpy"] = round(sum(r["jpy"] for r in rows), 3)
    loc = lambda p: sum(1 for _ in open(p, encoding="utf-8"))
    out["loc"] = {f: loc(f"{HERE}/{f}") for f in ("b3sep_build_01.py", "b3sep_eval_01.py", "b3sep_driver_01.py", "b3sep_common_01.py")}
    return out


def main():
    os.makedirs(EV, exist_ok=True)
    units = load_units()
    base = [u for u in units if u["arm"] in ("C0", "C1")]
    dunits = {v: [build_D(u, v) | {"theme": u["theme"], "rep": u["rep"], "ledger": u["ledger"], "src_arm": u["arm"]} for u in base] for v in ("Dmin", "Dfull")}
    for v in dunits:
        for d, u in zip(dunits[v], base):
            d["ids"] = d["ordered_ids"]; d["storyline"] = u["storyline"]
    R = {"n_units": {a: len([u for u in units if u["arm"] == a]) for a in ("C0", "C1", "Aprime")}}
    R["E1"] = e1(units, dunits)
    R["E2"] = e2(units, dunits)
    R["E3E4"] = {"Dmin": e3_e4([d | {"facts_text": d["facts_text"]} for d in dunits["Dmin"]]), "Dfull": e3_e4(dunits["Dfull"]),
                 "Aprime": e3_e4([u for u in units if u["arm"] == "Aprime"]), "C1": e3_e4([u for u in units if u["arm"] == "C1"]), "C0": e3_e4([u for u in units if u["arm"] == "C0"])}
    R["E5"] = e5(units, dunits)
    R["E6"] = e6(dunits)
    R["E7"] = e7(dunits)
    R["E10"] = e10(units, dunits)
    R["E1b_supplementary"] = e1b(units, dunits)
    R["E8"] = e8()
    # side-by-side + blind
    lines = []
    for th in THEMES:
        lines.append(f"\n\n# {th}\n")
        for u in [x for x in units if x["theme"] == th and x["arm"] in ("C0", "C1", "Aprime")]:
            lines.append(f"\n## {u['arm']} rep{u['rep']}  ids={u['ids']}\nStoryline: {u['storyline']}\n{u['facts_text']}\n" + (u["constraints_text"] if u["arm"] == "Aprime" else ""))
        d0 = [d for d in dunits["Dmin"] if d["theme"] == th and d["src_arm"] == "C0"][0]
        d1 = [d for d in dunits["Dfull"] if d["theme"] == th and d["src_arm"] == "C0"][0]
        lines.append(f"\n## Dmin (C0 ids)\n{d0['facts_text']}\n{d0['constraints_text']}\n## Dfull (C0 ids)\n{d1['facts_text']}\n{d1['constraints_text']}\n")
    wt(f"{EV}/side_by_side_02.md", "\n".join(lines))
    blind = []
    for u in [x for x in units if x["arm"] in ("C1", "Aprime")]:
        blind.append({"arm": u["arm"], "theme": u["theme"], "rep": u["rep"], "facts_text": u["facts_text"]})
    for d in dunits["Dmin"]:
        blind.append({"arm": "Dmin", "theme": d["theme"], "rep": d["rep"], "facts_text": d["facts_text"]})
    random.Random(20261010).shuffle(blind)
    key, md = {}, ["# blind outputs (arm names hidden). Review each for instruction/prohibition wording in the Facts text.\n"]
    for k, b in enumerate(blind, 1):
        key[f"X-{k:03d}"] = {x: b[x] for x in ("arm", "theme", "rep")}
        md.append(f"\n## X-{k:03d}  (theme: {b['theme']})\n{b['facts_text']}")
    wt(f"{EV}/blind_outputs_02.md", "\n".join(md))
    wj(f"{EV}/blind_key_02.json", key)
    wj(f"{EV}/eval_results_02.json", R)
    print(json.dumps({k: v for k, v in R.items() if k not in ("E5",)}, ensure_ascii=False)[:6000])
    print("E5", R["E5"])


if __name__ == "__main__":
    main()
