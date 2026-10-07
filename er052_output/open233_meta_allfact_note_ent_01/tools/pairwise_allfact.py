# -*- coding: utf-8 -*-
"""pairwise_p01.py の本Trial用コピー(path/言語を引数化、複数ペア対応)。判定語は X/Y/tie。"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
import er003_v1_n3_01_advanced_adaptation_generate as g

MODEL = "gpt-5.6-sol"
RN = "er052_output/open233_polysemy_trial_04/runs/meta/control/rep1"
R = "er052_output/open233_meta_allfact_note_ent_01/runs/meta/nb"
SRC = {
 ("JA", "P1"): R + "/p1/rep1/ja_writer/revision2.md", ("JA", "P2"): R + "/p2/rep1/ja_writer/revision2.md", ("JA", "C"): RN + "/ja_writer/revision2.md",
 ("EN", "P1"): R + "/p1/rep1/b1b/article.md", ("EN", "P2"): R + "/p2/rep1/b1b/article.md", ("EN", "C"): RN + "/b1b/article.md",
}
PAIRS = [("JA", "P1", "C"), ("JA", "P2", "C"), ("JA", "P1", "P2"), ("EN", "P1", "C"), ("EN", "P2", "C"), ("EN", "P1", "P2")]
LANGNAME = {"JA": "Japanese", "EN": "English"}
PROMPT = """Below are two {lang} radio/podcast-style articles, X and Y, on the same topic. Compare them as entertainment reading/listening experience only (do NOT judge factual accuracy).
For each axis choose "X", "Y" or "tie":
- story: storytelling / narrative flow
- tempo: pacing and rhythm
- natural: naturalness of the language
- soft: less explanatory and less stiff (the one that is LESS explanatory/stiff wins)
- overall: overall entertainment quality
Return JSON only: {{"story":..,"tempo":..,"natural":..,"soft":..,"overall":..,"reason":"<=60 words"}}

=== X ===
{x}

=== Y ===
{y}
"""
OUT = "er052_output/open233_meta_allfact_note_ent_01/eval/pairwise_allfact.json"
def main():
    client = OpenAI(); price = g._load_pricing(); calls = []; total = 0.0
    for lang, a, b in PAIRS:
        ta = open(SRC[(lang, a)], encoding="utf-8").read(); tb = open(SRC[(lang, b)], encoding="utf-8").read()
        for order, (xl, yl, x, y) in enumerate([(a, b, ta, tb), (b, a, tb, ta)], 1):
            prompt = PROMPT.format(lang=LANGNAME[lang], x=x, y=y)
            r = client.responses.create(model=MODEL, input=prompt)
            u = r.usage; cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
            usd, jpy = g._compute_cost_jpy(price, MODEL, u.input_tokens, cached, u.output_tokens); total += jpy
            txt = r.output_text
            try:
                parsed = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
            except Exception:
                parsed = None
            calls.append({"lang": lang, "pair": f"{a}_vs_{b}", "order": order, "X": xl, "Y": yl, "model": r.model, "response": txt, "parsed": parsed,
                          "input_tokens": u.input_tokens, "output_tokens": u.output_tokens, "cost_jpy": jpy})
            print(lang, a, b, order, (txt or "")[:150].replace("\n", " "), flush=True)
            json.dump({"model_requested": MODEL, "calls": calls, "total_jpy": round(total, 4)}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("total_jpy", total)
main()
