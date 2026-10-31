# -*- coding: utf-8 -*-
"""JA-GLOSS-NUANCE-01 Trial(後段の自己検査案 P): 第1段(現行方式A)の出力のうち、key_phraseが1語でgloss!=naive_jaのitemだけを対象に、
current_gloss / naive_ja(見出し訳) / 他の定訳 を候補として比べ直す小さな2回目呼出。DEV/Trial専用。
使い方: python stage2_check_trial_01.py <trial_dir> <tag> <A出力のrep> [model] [effort]  → <trial_dir>/stage2/<tag>__A<rep>__P.json"""
import json, os, sys, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gloss_nuance_trial_01 as T

DEV = "英語学習教材のKey Phraseに付ける日本語グロスの最終確認を行ってください。"
SCHEMA = {"name": "gloss_final_check", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {"items": {"type": "array", "items": {
    "type": "object", "additionalProperties": False, "required": ["rank", "candidates_considered", "final_gloss", "changed", "reason"],
    "properties": {"rank": {"type": "integer"}, "candidates_considered": {"type": "array", "items": {"type": "string"}},
                   "final_gloss": {"type": "string"}, "changed": {"type": "boolean"}, "reason": {"type": "string"}}}}}}}
HEAD = ("以下は英語学習教材の1語のKey Phraseと、第1段で生成した日本語グロス(current_gloss)です。naive_jaは英和辞典の見出し訳に相当する直訳です。"
        "各項目について、current_glossを最終採用してよいか確認し、最終のfinal_glossを決めてください。\n\n"
        "【判断基準(上から順に)】\n"
        "1. 本文での語義に合っている(誤訳・語義のずれが無い)。\n"
        "2. その英単語を、近い意味の一般的な英語の語(上位語・近義語)から区別する特徴(分野・含み・強さ・比喩の像)が、日本語でも伝わる最も限定的な1語である。\n"
        "3. 説明文・定義文ではなく、単語に対応する短い日本語(key_phraseと同じ品詞・同程度の長さ)である。\n"
        "4. 自然で平易な現代日本語である。\n\n"
        "【手順】current_gloss、naive_ja、必要なら本文の語義に合う別の定訳を候補として比べ、基準1〜4で最もよい1つを選ぶ(candidates_consideredに比べた候補を書く)。"
        "current_glossがすでに最良なら変更しない(変更のための変更はしない。changed=false)。訳語は原則1つ。1つでは重要な意味が落ちる、または誤解を生む場合に限り、括弧を使わず「A、B」で2つまで。\n\n")

def main(trial_dir, tag, rep, model="gpt-6-luna", effort="medium"):
    A = json.load(open(f"{trial_dir}/out/{tag}__A__gpt-6-luna__r{rep}.json", encoding="utf-8"))
    resp = json.loads(A["output_text"])
    prompt = open(f"{trial_dir}/inputs/{tag}.txt", encoding="utf-8").read()
    pi = prompt.find("【対象項目】"); pj = prompt.find("【記事本文(参考)】")
    pitems = {it["rank"]: it for it in json.loads(prompt[pi + len("【対象項目】"):pj])}
    article = prompt[pj:]
    tgt = []
    for it in resp["items"]:
        kp = pitems[it["rank"]]["key_phrase"]
        if " " not in kp.strip() and it["japanese_gloss"] != it["naive_ja"]:
            tgt.append({"rank": it["rank"], "key_phrase": kp, "source_sentence": pitems[it["rank"]]["source_sentence"],
                        "naive_ja": it["naive_ja"], "current_gloss": it["japanese_gloss"], "meaning_in_text_en": it["meaning_in_text_en"]})
    if not tgt:
        print("no targets"); return
    text = HEAD + "【対象項目】\n" + json.dumps(tgt, ensure_ascii=False, indent=2) + "\n\n" + article
    from dotenv import load_dotenv; load_dotenv(os.environ.get("JAG_ENV", r"C:\Users\tensh\eigo-radio\.env"))
    from openai import OpenAI
    t0 = time.time()
    r = OpenAI().responses.create(model=model, reasoning={"effort": effort}, text={"format": {"type": "json_schema", **SCHEMA}},
                                  input=[{"role": "developer", "content": DEV}, {"role": "user", "content": text}])
    u = r.usage; usage = {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                          "cached_input_tokens": getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0}
    c = T.cost_jpy(r.model, usage)
    os.makedirs(f"{trial_dir}/stage2", exist_ok=True)
    out = {"tag": tag, "from": f"A r{rep}", "model": r.model, "effort": effort, "usage": usage, "cost_jpy": c, "elapsed_s": round(time.time() - t0, 1),
           "targets": tgt, "output_text": r.output_text}
    json.dump(out, open(f"{trial_dir}/stage2/{tag}__A{rep}__P.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    led = f"{trial_dir}/ledger.json"
    L = json.load(open(led, encoding="utf-8")); L["calls"].append({"name": f"stage2 {tag} A{rep} P", "model": r.model, "usage": usage, "cost_jpy": c})
    L["total_jpy"] = round(L["total_jpy"] + c, 4); json.dump(L, open(led, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(tag, rep, usage, c, "cum", L["total_jpy"])

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], int(a[3]), *(a[4:6]))
