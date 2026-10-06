# -*- coding: utf-8 -*-
"""pairwise_p01: Before/After EN記事のEntertainment pairwise(順序入替2 call)。台帳は渡さない。"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
import er003_v1_n3_01_advanced_adaptation_generate as g

MODEL = "gpt-5.6-sol"
BEFORE = "er019_output/meta/run_03/b1b/article.md"
AFTER = "er052_output/open233_ledger_clarity_p_trial_01/after_pprime_01/b1b/article.md"
OUT = "er052_output/open233_ledger_clarity_p_trial_01/after_pprime_01/eval/E3_pairwise.json"
PROMPT = """Below are two English radio/podcast-style articles, X and Y, on the same topic. Compare them as entertainment reading/listening experience only (do NOT judge factual accuracy).
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
def main():
    b = open(BEFORE, encoding="utf-8").read(); a = open(AFTER, encoding="utf-8").read()
    client = OpenAI(); price = g._load_pricing(); calls = []; total = 0.0
    for name, x, y, xl, yl in [("call1_X=Before_Y=After", b, a, "Before", "After"), ("call2_X=After_Y=Before", a, b, "After", "Before")]:
        prompt = PROMPT.format(x=x, y=y)
        r = client.responses.create(model=MODEL, input=prompt)
        u = r.usage; cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
        usd, jpy = g._compute_cost_jpy(price, MODEL, u.input_tokens, cached, u.output_tokens)
        total += jpy
        txt = r.output_text
        try:
            s = txt[txt.index("{"):txt.rindex("}") + 1]; parsed = json.loads(s)
        except Exception:
            parsed = None
        calls.append({"name": name, "X": xl, "Y": yl, "model": r.model, "prompt": prompt, "response": txt, "parsed": parsed,
                      "input_tokens": u.input_tokens, "output_tokens": u.output_tokens, "cost_jpy": jpy})
        print(name, txt[:300])
    json.dump({"model_requested": MODEL, "calls": calls, "total_jpy": round(total, 4)}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"pairwise_jpy": round(total, 4), "model": MODEL, "cap_jpy": 3}, open(OUT.replace("E3_pairwise", "E3_cost"), "w"), indent=2)
    print("total_jpy", total)
main()
