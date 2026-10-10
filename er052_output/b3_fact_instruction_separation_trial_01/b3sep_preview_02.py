# -*- coding: utf-8 -*-
"""¥0工程: D-min / D-full / Dtag の preview(C0の selected_fact_ids を使用)。API不使用。実行: PYTHONIOENCODING=utf-8 py -I b3sep_preview_02.py"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b3sep_common_01 import *
import b3sep_build_01 as B
import er052_factlock_astra_e2e_runner_01 as run
OUT = f"{HERE}/preview_02"
rows = []
for th in THEMES:
    ti = theme_inputs(th); ev = ti["ev"]
    for var in ("Dmin", "Dfull", "Dtag"):
        a = B.assemble_D(ti["ledger"], ev["selected_fact_ids"], ev["selected_storyline"], var)
        wt(f"{OUT}/{th}__{var}__brief.md", a["brief_md"]); wt(f"{OUT}/{th}__{var}__constraints.md", a["constraints_text"])
        s, f = run.parse_brief_md(a["brief_md"]); ann = run.dryrun_annotate(a["brief_md"])
        n_tag = len(re.findall(r"【事実\d+】", ann))
        imp = [l for l in a["facts_text"].split("\n") if l and B.IMP.search(l)]
        rows.append({"theme": th, "variant": var, "n_facts": len(a["ordered_ids"]), "facts_chars": len(a["facts_text"]), "cons_chars": len(a["constraints_text"]),
                     "cons_lines": len(a["constraint_items"]), "moved_to_constraints": a["moved_to_constraints"], "ambiguous": a["ambiguous_facts"],
                     "parse_ok": bool(s and f), "tags_eq_facts": n_tag == len(a["ordered_ids"]), "imp_in_facts": imp, "bracket_in_facts": "【" in a["facts_text"]})
wj(f"{HERE}/preview_summary_02.json", rows)
for v in ("Dmin", "Dfull", "Dtag"):
    r = [x for x in rows if x["variant"] == v]
    print(v, "facts_chars_total", sum(x["facts_chars"] for x in r), "cons_chars_total", sum(x["cons_chars"] for x in r), "moved", sum(len(x["moved_to_constraints"]) for x in r),
          "imp_in_facts", sum(len(x["imp_in_facts"]) for x in r), "parse_ok", all(x["parse_ok"] for x in r), "tags_eq", all(x["tags_eq_facts"] for x in r), "bracket", any(x["bracket_in_facts"] for x in r))
for x in rows:
    if x["variant"] == "Dfull" and x["moved_to_constraints"]: print("MOVED", x["theme"], x["moved_to_constraints"])
    if x["variant"] == "Dfull" and x["imp_in_facts"]: print("IMP_IN_DFULL", x["theme"], x["imp_in_facts"])
