# -*- coding: utf-8 -*-
"""回帰/単体test(API呼出なし)。python er069_attribution_clip_split_trial_01_test_01.py"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er069_attribution_clip_split_trial_01_lib as L
import er069_attribution_clip_split_trial_01_mkplan as M
import er069_attribution_clip_split_trial_01_measure as ME

OUT = "er069_output/attribution_clip_split_trial_01"
fails = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


check("bucket", [L.bucket(n) for n in (1, 2, 3, 4, 5, 6)] == ["<=2", "<=2", "3", "4-5", "4-5", ">=6"])
names = L.find_names('“Hi,” Melos said. Then Melos ran. “Go,” Selinuntius stepped.')
check("find_names Melos", "Melos" in names)
b = L.sib_boundaries("Melos said.", {"Melos"})
check("sib Melos+said proper", len(b) == 1 and b[0]["proper_noun"])
check("no sib Melos replied", L.sib_boundaries("Melos replied.", {"Melos"}) == [])
check("no sib he said", L.sib_boundaries("he said.", set()) == [])
tasks = M.build()
check("plan 144", len(tasks) == 144)
check("plan ids unique", len({t["id"] for t in tasks}) == 144)
check("plan lengths", {t["word_count"] for t in tasks if t["length"] == "L2"} == {2}
      and {t["word_count"] for t in tasks if t["length"] == "L4"} == {4}
      and {t["word_count"] for t in tasks if t["length"] == "L7"} == {7})
check("plan ss only said / nss only replied", all(("said" in t["text"]) == (t["boundary"] == "ss") for t in tasks))
check("plan every cell has 3 takes", all(sum(1 for u in tasks if u["id"].rsplit("_t", 1)[0] == t["id"].rsplit("_t", 1)[0]) == 3 for t in tasks))
check("norm", ME.norm("Melos said.") == "melos said")
ag = ME.agg([{"openai_verified": True, "azure_pass": False, "or_pass": True, "hr_proxy": False, "spell_openai": True,
              "spell_azure": False, "spell_whisper": False}], lambda r: "k")
check("agg", ag["k"]["n"] == 1 and ag["k"]["or_pass"] == 1)
da = json.load(open(f"{OUT}/desk_apply_01.json", encoding="utf8"))
check("desk_apply regression reproduces stored plan", all(v["regression_reproduces_stored_plan"] for v in da.values()))
check("desk_apply after has no lint findings", all(v["after"]["lint_findings"] == [] for v in da.values()))
check("desk_apply clip count unchanged", all(v["before"]["n_clips"] == v["after"]["n_clips"] for v in da.values()))
check("gen script never writes shared state (static scan)",
      not any(s in open("er069_attribution_clip_split_trial_01_gen.py", encoding="utf8").read()
              for s in ("er006_output", "er011_output", "er021_output", "er025_output", "melos/run_e2e_02")))
# --- 委任_02 ---
import er069_attribution_clip_split_trial_01_mkplan02 as M2
import er069_attribution_clip_split_trial_01_summarize02 as S2
t2 = M2.build()
check("plan02 84 tasks", len(t2) == 84 and len({t["id"] for t in t2}) == 84)
check("plan02 verbs cross s/ns with 3 each", {t["verb"] for t in t2 if t["vgroup"] == "s"} == {"said", "says", "sighed"}
      and {t["verb"] for t in t2 if t["vgroup"] == "ns"} == {"replied", "answered", "asked"})
check("plan02 s-group verbs start with sibilant, ns do not", all((t["verb"][0] == "s") == (t["vgroup"] == "s") for t in t2))
check("plan02 L2 fixed 2 words", all(t["word_count"] == 2 and t["text"] == f"{t['name']} {t['verb']}." for t in t2))
check("plan02 nophrase only Melos said/replied", {(t["name"], t["verb"]) for t in t2 if t["nophrase"]} == {("Melos", "said"), ("Melos", "replied")})
check("plan02 takes Melos4 Brontes3", len([t for t in t2 if t["name"] == "Melos" and t["verb"] == "said" and t["level"] == "adv"]) == 4
      and len([t for t in t2 if t["name"] == "Brontes" and t["verb"] == "said" and t["level"] == "adv"]) == 3)
check("summarize02 cnt/fmt", S2.fmt([{"k": True}, {"k": False}], "k") == "1/2")
check("summarize02 compare", S2.compare([{"vgroup": "a", "k": 1}] * 3, lambda r: r["vgroup"] == "a", lambda r: False, "k")[:2] == (3, 3))
r2 = json.load(open(f"{OUT}/results_02.json", encoding="utf8"))
check("results_02 obs 126 (std 2 + adv 1 per audio)", r2["n_obs"] == 126)
check("results_02 nophrase obs only on Melos said/replied", all((("azure_np" in r) == (r["name"] == "Melos" and r["verb"] in ("said", "replied"))) for r in r2["rows"]))
check("results_02 total within JPY25 guardrail", r2["total_jpy"] <= 25)
print("FAILS:", fails)
sys.exit(1 if fails else 0)
