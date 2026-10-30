# -*- coding: utf-8 -*-
"""Trial corpus builder: 記事本文(selector promptの本文後置部)+Before(現行Production候補)。read-only。"""
import json, os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BODY = "\n\n---\n\n【記事本文】\n"
NOTE = "\n\n---\n\n【前回の選定結果に関する指摘(機械診断)】\n"
X = "er019_output/family_x_audio_production_wiring_01/"
CASES = []
def add(cid, group, family, slug, level, kpdir, text_path=None):
    CASES.append(dict(id=cid, group=group, family=family, slug=slug, level=level, kpdir=kpdir, text_path=text_path))
for slug in ["untidiness_family_resource", "ai_chat_sponsored_persuasion", "jwst_mystery_emission_line", "meta_waddle_world"]:
    for lv in ("a2", "b1b"):
        add(f"{slug[:6]}_{lv}", "REQ", "X", slug, lv, f"{X}{slug}__run_fx4_01/{lv}/key_phrases")
for lv in ("a2", "b1b"):
    add(f"aiisland_{lv}", "GEN", "X", "ai_island_temple", lv, f"{X}ai_island_temple__run_form_prod_01/{lv}/key_phrases")
    add(f"moon_{lv}", "GEN", "X", "moon_shrinking", lv, f"{X}moon_shrinking__run_reselect_01/{lv}/key_phrases")
    add(f"surname_{lv}", "GEN", "Y", "surname_choice", lv, f"er121_output/family_y_production_01/surname_choice/run_02/key_phrases/{lv}")
    add(f"melos_{lv}", "GEN", "Z", "melos", lv, f"er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01/key_phrases/{lv}")
for lv in ("a2", "b1b"):
    add(f"ignobel_{lv}", "UNUSED", "X", "ig_nobel_2026", lv, None, f"er019_output/ig_nobel_2026/run_nws_02/{lv}/article.md")
    add(f"tesla_{lv}", "UNUSED", "X", "tesla_spacex_merger_talks", lv, None, f"er019_output/tesla_spacex_merger_talks/run_nws_01/{lv}/article.md")

def text_of(c):
    if c["text_path"]:
        t = open(os.path.join(ROOT, c["text_path"]), encoding="utf-8").read()
        return t
    p = os.path.join(ROOT, c["kpdir"], "kp_candidates", "round_1", "work", "keywords_selector_prompt.txt")
    s = open(p, encoding="utf-8").read()
    s = s.split(BODY, 1)[1]
    return s.split(NOTE, 1)[0].split("\n\n---\n\n")[0] if False else s.split(NOTE, 1)[0]

def before_of(c):
    if not c["kpdir"]: return None
    j = json.load(open(os.path.join(ROOT, c["kpdir"], "kp_candidates.json"), encoding="utf-8"))
    out = []
    for x in j["candidates"]:
        out.append(dict(selection_phrase=x["selection_phrase"], used_form=x["used_form"], gloss=x["japanese_gloss"], origin=x["origin"],
                        kind=x.get("kind") or ("word" if len(x["used_form"].split()) == 1 else "phrase"), sentence=x.get("source_sentence")))
    return dict(candidates=out, model=j.get("model_id"), prompt_ids=j.get("prompt_ids"), generated_at=j.get("generated_at"))

def build():
    res = []
    for c in CASES:
        t = text_of(c)
        b = before_of(c)
        res.append({**c, "text": t, "words": len(t.split()), "before": b})
    return res

if __name__ == "__main__":
    r = build()
    json.dump(r, open(os.path.join(os.path.dirname(__file__), "kpg01_work", "corpus.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for c in r:
        print(c["id"], c["group"], c["words"], (c["before"] or {}).get("prompt_ids"), len((c["before"] or {}).get("candidates", [])))
