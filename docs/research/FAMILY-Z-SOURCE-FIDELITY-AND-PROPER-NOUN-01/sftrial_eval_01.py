# -*- coding: utf-8 -*-
"""U1 Trial 委任_03 評価(決定論・API0): 各runの各段について 種明かし文の有無/位置、固有名詞、語数、段落数、既存guardrail、
結末前の種明かし漏れ候補語、伏線語の有無、費用。本文の意味判定(引用)は人(Sonnet)が読んで結果mdに貼る=ここは機械的な抽出のみ。"""
import re, json, os, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import er062_family_z_structure_01 as st

D = "er026_output/family_z_production_e2e_01/the_open_window"
OUT = "docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/sftrial_eval_01.json"
RUNS = ([("T1", f"run_sftrial_t1_0{i}", ("r0",)) for i in (1, 2, 3)] + [("T2", f"run_sftrial_t2_0{i}", ("r0",)) for i in (1, 2, 3)]
        + [("T3", f"run_sftrial_t3_0{i}", ("r0", "r1", "r2", "std_adjust")) for i in (1, 2)]
        + [("ref_01B_common", "run_pntrial_01", ("r0", "r1", "r2", "std_adjust")), ("ref_01B_per_story", "run_pntrial_02", ("r0", "r1", "r2", "std_adjust")),
           ("ref_baseline_prod", "run_e2e_01", ("r2", "std_adjust"))])
FILE = {"r0": "r0.md", "r1": "r1.md", "r2": "r2.md", "std_adjust": "std.md"}
CAND = ["Framton", "Nuttel", "Vera", "Sappleton", "Ronnie", "Bertie"]
STOP = set("The A An He She It They We You I His Her Their My Our Your This That These Those There Then But And So Or If When While As At In On Of To For From With By Not No Yes One Two Three Some Any All Each Every Such Who What Where Why How Which Oh Indeed Really Look Here Now Once Only Just Even Still Also Too Very More Most Many Much Few Little After Before Over Under Through Between Without Within Beyond Against Along Around Behind Beside Near Until Since Because Although Though Perhaps Maybe Never Always Sometimes Often Suddenly Slowly Quickly Finally Please Thank Thanks Good Bad Come Go Stop Run Wait Let Do Does Did Is Are Was Were Be Been Have Has Had Will Would Can Could Should May Might Must Shall Nothing Something Anything Everything Someone Anyone Everyone Sorry Romance Country Ganges India October French".split())
END_RE = re.compile(r"(short notice|speciality|specialty|spur of the moment|good at (?:making|inventing)|making up stor|invent(?:ed|ing)? stor|quick(?:ly)? (?:at )?(?:making|inventing))", re.I)
LEAK_RE = re.compile(r"\b(invent\w*|made up|make up|making up|lie[sd]?|lying|pretend\w*|fib\w*|tall tale|false story|not true|joke|prank|trick\w*|teas\w+)\b", re.I)


def analyze(path):
    t = open(path, encoding="utf-8").read()
    title, body = st.split_title_body(t)
    paras = st.clean_body_paragraphs(body)
    names = {}
    for n in CAND:
        c = len(re.findall(r"\b" + n + r"\b", body))
        if c:
            names[n] = {"count": c, "first_para": next(i for i, p in enumerate(paras) if re.search(r"\b" + n + r"\b", p)) + 1}
    extra = collections.Counter()
    for pp in paras:
        for m in re.finditer(r"(?<![\.\?\!“”\"‘’'—\-] )(?<!^)(?<![“\"‘])\b([A-Z][a-z]{2,})\b", pp):
            wd = m.group(1)
            if wd not in STOP and wd not in CAND:
                extra[wd] += 1
    end_hits = [(i + 1, p) for i, p in enumerate(paras) if END_RE.search(p)]
    last = paras[-1]
    leaks = []
    for i, p in enumerate(paras[:-1]):
        for m in LEAK_RE.finditer(p):
            leaks.append({"para": i + 1, "word": m.group(0), "ctx": p[max(0, m.start() - 40):m.end() + 40]})
    foresh = {k: bool(re.search(k, body, re.I)) for k in ("white", "Bertie", "spaniel", "bog|swallow|marsh", "open window|window", "ghost", "cemetery|graveyard|grave")}
    return {"words": st.body_word_count(t), "paragraphs": len(paras), "title": title, "names": names,
            "other_capitalized_midsentence": dict(extra),
            "ending_reveal_in_last_paragraph": bool(END_RE.search(last)), "ending_reveal_paragraphs": [i for i, _ in end_hits],
            "ending_reveal_last_paragraph_text": last if END_RE.search(last) else None,
            "last_paragraph_text": last, "possible_pre_ending_leak_words": leaks, "foreshadow_words_present": foresh}


rows = []
for arm, run, stages in RUNS:
    prov_p = f"{D}/{run}/writer/provenance.json"
    prov = json.load(open(prov_p, encoding="utf-8")) if os.path.exists(prov_p) else {}
    for stg in stages:
        p = f"{D}/{run}/writer/{FILE[stg]}"
        if not os.path.exists(p):
            rows.append({"arm": arm, "run": run, "stage": stg, "missing": True})
            continue
        r = {"arm": arm, "run": run, "stage": stg, **analyze(p)}
        e = next((x for x in prov.get("chain", []) if x["stage"] == stg), None)
        if e:
            r["cost_jpy"] = e.get("cost_jpy")
            r["guardrails"] = e.get("guardrails")
            r["actual_model_id"] = e.get("actual_model_id")
            r["prompt_sha256"] = e.get("prompt_sha256")
        rows.append(r)
json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in rows:
    if r.get("missing"):
        print(r["arm"], r["run"], r["stage"], "MISSING")
        continue
    print(f"{r['arm']:18s} {r['run']:18s} {r['stage']:10s} w={r['words']} p={r['paragraphs']} end_last={r['ending_reveal_in_last_paragraph']} "
          f"names={ {k: v['count'] for k, v in r['names'].items()} } other={r['other_capitalized_midsentence']} leaks={len(r['possible_pre_ending_leak_words'])} "
          f"cost={r.get('cost_jpy')} warn={(r.get('guardrails') or {}).get('warnings')}")
