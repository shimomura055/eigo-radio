# 読取専用・オフライン: 既知可能性シグナル(CEFR-J/wordfreq)が「使える/使えない」かの確認。費用0。
import sys, os, json
sys.path.insert(0, os.getcwd())
import wordfreq
import er030_key_phrase_db_hybrid_core_01 as core
dbs = core.load_group1_dbs(); cj = dbs["cefr_j"]
rows = []
for ph in ["time lag", "lag", "push prices up", "be behind", "price increases", "right away", "take time", "on a regular basis", "show up",
           "come down", "come with", "raw bean", "price tag", "price measure", "pump one's fist", "in the ring", "hidden clock", "bad weather", "retail price"]:
    toks = ph.split()
    rows.append({"phrase": ph, "unit_in_cefrj": (cj.get(ph) or {}).get("cefr"),
                 "tokens": [{"t": t, "cefrj": (cj.get(t) or {}).get("cefr"), "zipf": round(wordfreq.zipf_frequency(t, "en"), 2)} for t in toks]})
json.dump(rows, open("er064_output/kp_candidate_selection_design_01/known_likelihood_signals_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
for r in rows:
    print(r["phrase"], "| unit:", r["unit_in_cefrj"], "|", " ".join(f"{x['t']}:{x['cefrj']}/{x['zipf']}" for x in r["tokens"]))
