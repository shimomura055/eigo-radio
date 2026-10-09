# -*- coding: utf-8 -*-
"""委任_09: B3 brief(v1/v2)の機械判定。(1)Selected Facts節の形式(箇条書き行数・'Storyline:'重複行・'素材:'行・段落) (2)briefの算用数字トークンのうち台帳全文に出ないもの(台帳外の導出数の候補) (3)選択台帳ID数。API支出0。"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
sys.path.insert(0, BASE)
import b3_annotation_check_01 as c
rd = lambda p: open(p, encoding="utf-8", newline="").read()
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
def fmt(brief):
    b = c.prep(brief); rng = c.facts_section_range(b)
    body = b[rng[0]:rng[1]] if rng else ""
    lines = [l for l in body.split("\n") if l.strip()]
    bullets = [l for l in lines if re.match(r"^\s*(?:-|・)\s*", l)]
    dup = [l for l in lines if re.match(r"^\s*Storyline[:：]", l)]
    sozai = [l for l in lines if re.match(r"^\s*素材[:：]", l)]
    para = [l for l in lines if l not in bullets and l not in dup and l not in sozai]
    return {"facts_section_lines": len(lines), "bullet_lines": len(bullets), "storyline_dup_lines": len(dup), "sozai_lines": len(sozai), "paragraph_lines": len(para),
            "annotatable_by_bullet_rule": len(bullets) > 0 or len(para) > 0 and not sozai}
def foreign_numbers(brief, ledger):
    lt = re.sub(r"(?<=\d),(?=\d)", "", ledger)
    lset = set(m.group(0) for m in NUM.finditer(lt))
    toks = []
    for m in NUM.finditer(c.prep(brief)):
        t = m.group(0).replace(",", "")
        if t not in lset: toks.append(t)
    return sorted(set(toks))
out = {}
for S in sys.argv[1:]:
    ledger = rd(os.path.join(BASE, "stage_r", S, "research_ledger", "verified_fact_ledger.txt"))
    for ver, d in (("v1", "storyline_b3"), ("v2", "storyline_b3_v2")):
        p = os.path.join(BASE, "stage_r", S, d)
        if not os.path.exists(os.path.join(p, "selected_brief.md")): continue
        b = rd(os.path.join(p, "selected_brief.md")); ev = json.load(open(os.path.join(p, "fact_selection_evidence.json"), encoding="utf-8"))
        r = fmt(b); r["numbers_not_in_ledger"] = foreign_numbers(b, ledger); r["selected_fact_ids"] = ev["selected_fact_ids"]; r["n_selected_ids"] = len(ev["selected_fact_ids"])
        r["same_problem_as_v1"] = None
        out[f"{S}_{ver}"] = r
        print(S, ver, json.dumps(r, ensure_ascii=False))
json.dump(out, open(os.path.join(HERE, "b3_v2_judge.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
