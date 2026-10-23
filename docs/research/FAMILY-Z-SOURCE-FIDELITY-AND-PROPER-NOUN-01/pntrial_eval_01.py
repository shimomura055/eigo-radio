# -*- coding: utf-8 -*-
"""PROPER_NOUN_TRIAL_01 評価(決定論・API0): 固有名詞出現一覧(回数・初出段落)、語数、WARN。"""
import re, json, os, sys, collections
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
import er062_family_z_structure_01 as st
D = "er026_output/family_z_production_e2e_01"
CAND = ["Framton", "Nuttel", "Vera", "Sappleton", "Ronnie", "Melos", "Dionysius", "Selinuntius", "Phidias", "Bertie"]
RUNS = [("the_open_window", "run_pntrial_01", "common"), ("the_open_window", "run_pntrial_02", "per_story"),
        ("melos", "run_pntrial_01", "common"), ("the_open_window", "run_e2e_01", "baseline(受入済み現行)"), ("melos", "run_e2e_06", "baseline(受入済み現行)")]
STOP_WORDS = set("The A An He She It They We You I His Her Their My Our Your This That These Those There Then But And So Or If When While As At In On Of To For From With By Not No Yes One Two Three Some Any All Each Every Sorry Such Who What Where Why How Which Oh Indeed Really Look Here Now Once Only Just Even Still Also Too Very More Most Many Much Few Little After Before Over Under Through Between Without Within Beyond Against Along Around Behind Beside Near Until Since Because Although Though Perhaps Maybe Never Always Sometimes Often Suddenly Slowly Quickly Finally Please Thank Thanks Good Bad Come Go Stop Run Wait Let Do Does Did Is Are Was Were Be Been Have Has Had Will Would Can Could Should May Might Must Shall Neither Either Both Another Other Others Nothing Something Anything Everything Someone Anyone Everyone Somewhere Anywhere Everywhere Forgive Farther Brown Water Pain Somehow Surely Hide Live Could".split())
out = []
for story, run, var in RUNS:
    for lvl, f in (("Adv", "r2.md"), ("Std", "std.md")):
        p = f"{D}/{story}/{run}/writer/{f}"
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8").read()
        title, body = st.split_title_body(t)
        paras = st.clean_body_paragraphs(body)
        names = {}
        for n in CAND:
            hits = [i for i, pp in enumerate(paras) if re.search(r"\b" + n + r"\b", pp)]
            cnt = len(re.findall(r"\b" + n + r"\b", body))
            if cnt:
                names[n] = {"count": cnt, "first_para": hits[0] + 1}
        # 候補外の大文字語(文頭・引用冒頭を除く)
        extra = collections.Counter()
        for pp in paras:
            for m in re.finditer(r"(?<![\.\?\!“”\"‘’'—\-] )(?<!^)(?<![“\"‘])\b([A-Z][a-z]{2,})\b", pp):
                w = m.group(1)
                if w not in STOP_WORDS and w not in CAND:
                    extra[w] += 1
        prov = json.load(open(f"{D}/{story}/{run}/writer/provenance.json", encoding="utf-8")) if os.path.exists(f"{D}/{story}/{run}/writer/provenance.json") else {}
        wc = st.body_word_count(t)
        out.append({"story": story, "run": run, "variant": var, "level": lvl, "words": wc, "paragraphs": len(paras),
                    "names": names, "other_capitalized_midsentence": dict(extra)})
json.dump(out, open("docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/pntrial_eval_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for o in out:
    print(o["story"], o["run"], o["variant"], o["level"], "words=%d paras=%d" % (o["words"], o["paragraphs"]), json.dumps(o["names"], ensure_ascii=False), "other:", o["other_capitalized_midsentence"])
