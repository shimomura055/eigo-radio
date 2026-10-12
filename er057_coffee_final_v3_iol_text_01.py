# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01: In One Line修正原稿の生成(Trial隔離、gpt-6-luna)。既存Story/Pointsのみ入力、新Fact禁止。"""
import os, sys, json, re, hashlib
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er057_output", "coffee_final_audio_assembly_01")
TONE = "C:/Users/tensh/eigo-radio-tone/er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01"
MODEL = "gpt-6-luna"; USD_JPY = 160.0
C4 = {"std": "コーヒー豆の値段が下がっても、店の値札がすぐに変わるとは限りません。値段が変わる時期には、豆以外の費用も関わります。続いて、記事の要点を英語で聞いていきましょう。",
      "adv": "The story shows why news about bean prices may not match the price you see for coffee right away. There can be a delay, and other costs matter too. Now, let's bring the main idea together."}
LEVEL = {"std": ("a2", "A2 (simple everyday words; short sentences of about 10-16 words; one idea per sentence; listening-friendly)"),
         "adv": ("b1b", "B1-upper (natural adult news English; sentences up to about 22 words; still easy to follow by ear)")}
DEV = ("You write the closing 'In One Line' segment of an English-learning news audio program. Follow every rule exactly.\n"
 "- Write EXACTLY 2 sentences (a 3rd sentence only if truly necessary).\n"
 "- Sentence 1 = the core of the article. Sentence 2 = its meaning / implication for the listener, closing the segment naturally.\n"
 "- Use ONLY facts already stated in the provided article (story and key phrases). Do NOT add any new fact, number, name, cause, or claim.\n"
 "- Keep numbers/qualifiers faithful (e.g. 'about'/'at least' and 'may' hedges must not be strengthened into certainty).\n"
 "- The segment follows a Japanese/English host Comment that says the main points will be summarized next; it must sound like a natural wrap-up of the whole article, not a repeat of the Comment.\n"
 "- Plain spoken English for TTS: no markdown, no quotation marks, no headings, no bullet points, digits are fine ('9 months').\n"
 "- Match the requested difficulty level.")
SCHEMA = {"name": "iol", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["sentences"], "properties": {"sentences": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["text", "basis"], "properties": {"text": {"type": "string"}, "basis": {"type": "string", "description": "which paragraph(s)/sentence(s) of the article support this sentence"}}}}}}}

def usage(resp):
    u = resp.usage; ind = getattr(u, "input_tokens_details", None)
    return {"in": u.input_tokens, "cached": (getattr(ind, "cached_tokens", 0) or 0) if ind else 0, "out": u.output_tokens}

def main():
    from dotenv import load_dotenv; load_dotenv(os.path.join(ROOT, ".env"))
    from openai import OpenAI; client = OpenAI()
    snap = json.load(open(os.path.join(ROOT, "er005_output", "cost_baseline_01", "pricing_snapshot.json"), encoding="utf-8"))
    pr = {e["meter"]: e["price"] for e in snap["prices"] if e.get("model") == MODEL}
    res = {}
    for lv in ("std", "adv"):
        d, lvtxt = LEVEL[lv]
        art = open(f"C:/Users/tensh/eigo-radio-tone/er019_output/coffee_prices/run_e_tone_01/{d}/article.md", encoding="utf-8").read()
        body = art.split("## In one line")[0].strip()
        kp = json.load(open(f"{TONE}/{d}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
        kps = [it.get("phrase") or it.get("keyword") or str(it) for it in sorted(kp["items"], key=lambda i: i["rank"])]
        user = (f"Difficulty level: {lvtxt}\n\n[ARTICLE (Story/Points)]\n{body}\n\n[KEY PHRASES]\n{', '.join(kps)}\n\n"
                f"[COMMENT 4 spoken just before this segment]\n{C4[lv]}\n\n[PREVIOUS In One Line (1 sentence, too short)]\n{art.split('## In one line')[1].strip()}\n\n"
                "Write the new In One Line (2 sentences).")
        resp = client.responses.create(model=MODEL, reasoning={"effort": "medium"}, input=[{"role": "developer", "content": DEV}, {"role": "user", "content": user}],
                                       text={"format": {"type": "json_schema", **SCHEMA}})
        assert str(resp.model).startswith(MODEL), resp.model
        u = usage(resp)
        cost = ((u["in"] - u["cached"]) * pr["input_tokens"] + u["cached"] * pr["cached_input_tokens"] + u["out"] * pr["output_tokens"]) / 1e6 * USD_JPY
        j = json.loads(resp.output_text)
        res[lv] = {"model": resp.model, "response_id": resp.id, "usage": u, "cost_jpy": round(cost, 4), "sentences": j["sentences"],
                   "text": " ".join(s["text"].strip() for s in j["sentences"]), "user_prompt_sha256": hashlib.sha256(user.encode()).hexdigest(),
                   "kp": kps}
        print(lv, res[lv]["text"], res[lv]["cost_jpy"], flush=True)
    json.dump(res, open(os.path.join(OUT, "iol_llm_result_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
if __name__ == "__main__": main()
