# ONE-STEP-FURTHER-CORNER-TRIAL-01: DEV/Trial専用。Production code/Promptを一切import・編集しない(読むのは既存runの成果物と費用単価表の数値のみ)。
# 使い方: py osf01_gen.py dry | OSF_PAID=1 py osf01_gen.py gen <prompt_ver> <model> <tag> [cell ...]   cell=<y|x|z>_<std|adv>
import sys, os, re, json, time, threading, hashlib, importlib.util
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "docs", "research", "ONE-STEP-FURTHER-CORNER-TRIAL-01", "out"); USAGE = os.path.join(OUT, "usage_log.jsonl")
CAP_JPY = 60.0   # 委任の通常上限40、理由記録で60まで
PRICE = {"gpt-6-luna": (0.10, 0.01, 0.50), "gpt-6.1-sol": (2.00, 0.10, 10.00)}; USD_JPY = 160.0   # er009単価表(er009_n1_routing_governance_10_actual_model_cost.py:21,30,34)の数値
_lock = threading.Lock()
YB = "er121_output/family_y_production_01/surname_choice/run_02"
XB = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01"
ZB = "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_voice_fenrir_01"
TITLE = {"y": "When a Husband Chooses His Wife's Last Name: Their Voices (Family Y)", "x": "The Island Resets! But AI Has \"Strategy Notes\" (Family X)", "z": "The Tell-Tale Heart (Family Z)"}
CELLS = [f"{f}_{l}" for f in "yxz" for l in ("std", "adv")]
def _rj(p): return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
def _load_nt():
    sp = importlib.util.spec_from_file_location("nt01", os.path.join(ROOT, "docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/tools/nuance_trial_01.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def grammar_of(sd):
    out = []
    try:
        for i in _rj(f"{sd}/confirmed_grammar.json").get("items", []): out.append(i["title"])
    except Exception: pass
    try:
        for c in _rj(f"{sd}/grammar_candidates.json")["candidates"][:2]: out.append(f'{c["construct_ja"]}(例: {c["sentence"]})')
    except Exception: pass
    return out
def inputs_for(cell, T=None):
    f, lv = cell.split("_"); lk = "a2" if lv == "std" else "b1b"
    if f == "y":
        txt = open(os.path.join(ROOT, YB, "translate", f"{lk}.md"), encoding="utf-8").read()
        body = "\n\n".join(p.strip() for p in txt.split("\n\n")[1:] if p.strip())
        cs = _rj(f"{YB}/{lk}/audit/confirmed_selection.json"); kp = [(i["key_phrase"], i.get("japanese_gloss") or "") for i in cs["items"]]
        sd = f"{YB}/a2/study_text" if lk == "a2" else f"{YB}/study_text"
        nz = _rj(f"{sd}/confirmed_nuance.json")["candidate"]["expression"]
    else:
        T = T or _load_nt().load_targets(); t = T[("ai_island_" if f == "x" else "tth_") + lv]
        body = t["body"]; kp = [(k["expr"], k.get("gloss") or "") for k in t["kp"]]
        base = XB if f == "x" else ZB; sd = f"{base}/{lk}/study_text" if (f == "x" or lk == "a2") else f"{base}/study_text"
        nz = None
    return dict(cell=cell, family=f, level=("Standard(CEFR A2目標の英文。学習者はA2〜B1の日本語話者)" if lv == "std" else "Advanced(CEFR B1目標の英文。学習者はB1〜B2の日本語話者)"),
                lv=lv, title=TITLE[f], body=body, kp=kp, grammar=grammar_of(sd), nuance_expr=nz)

PROMPT_V1 = """あなたは日本人の英語学習者に、実際に「使える」英語表現を教える編集者です。下の記事を読んだ学習者向けに、新コーナー「One Step Further(もう一歩進んだ英語表現)」を作ります。
このコーナーの狙い: 学習者が「聞いたことはあるけれど自分では使えない」「こんな言い方があるのか、これは覚えたい」と感じる表現を、記事の話題をきっかけに紹介し、表現の引き出しを一つ増やすこと。単なる言い換え・難語やイディオムの披露ではない。

# 記事・レベル
- 記事: {title}
- レベル: {level}

# 本文(英文)
{body}

# このレベルで既に学習項目として扱う内容(重複を避ける対象)
- Key Phrase / Word: {kp}
- 文法・構文: {grammar}

# 作り方
1. 記事の話題・主張・状況・登場人物の気持ち(本文に書かれていること)から、学習者が自分の言葉で言いたくなる場面を3〜5つ考える。
2. 各場面で、日本人学習者が自力で英語にすると平易な言い方(基本表現)で止まってしまう場面を探し、「もう一歩進んだ表現」の候補を考える。発展表現は、記事の本文にある表現である必要はない(むしろ本文にない別の表現を紹介する)。
3. 次のテストで候補を絞る。
   (a) 日本人学習者が「意味は分かるが自分では出てこない」ものか。簡単すぎる(中学英語そのまま)ものや、辞書で語義を引いて終わる難語は外す。
   (b) 記事以外の場面(日常会話・ニュース・議論・仕事)でも使い回せるか。
   (c) 現代の自然な英語として、ネイティブが普通に使うか(古風・文語的・スラングは外す。ネイティブらしさの追求は不要)。
   (d) Key Phrase/Word・文法・本文に既出の表現と別物か(同じ語句・同じ核表現は不可)。
   (e) 「覚えたい」と思える発見があるか。
4. 4条件を満たす最良の候補を1つ、さらに独立して価値のある別の候補があれば2つ目を選ぶ。2つ目は価値が1つ目と同程度に高いときだけ。品質の低い候補で2件に増やさない(1件で良い)。
5. 各項目について基本表現を作る。基本表現は平易で誰にも分かる英文。発展表現は必ずしも同義でなくてよいが、意味・ニュアンス・使用場面・強さが変わる場合はmeaning_shift_noteで明確に述べる。無理な言い換え、不自然な比較は作らない。

# 規則
- 基本表現・発展表現は、学習者が自分の状況で言える一般的な文にする。記事の登場人物の言動として書く必要はない。記事にない事実・出来事・人物の心理を、記事の内容として述べない。topic_hook_jaは本文に書かれている話題・主張・気持ちだけを根拠に書く。
- 次の6表現は参考例として別に示されたものなので、そのまま選ばない: backfire / be sold on / live up to the hype / be torn between / the tide is turning / room for improvement。同じ種類の表現(同じ構造・同じ場面)を選ぶのも避け、この記事の話題に即した新しい表現を選ぶ。
- 難しい単語を使っていること自体を価値にしない。日本語は簡潔に。point_jaは2〜3文・合計120字以内で、使い方(どんな時に言うか)と応用場面を示す。why_jaは1〜2文。
- レベル差: Standardは日常会話で使える平易な表現(基本表現はA2、発展表現はB1程度まで)。Advancedは議論・仕事・ニュースにも応用できる表現(B1〜B2)。同じ記事の別レベルとは違う表現を選ぶ必要はないが、レベルに合った選定をする。
- 発展表現のスロット(〜部分)は「A」「something」「someone」などで示す。

# 出力(JSONのみ。前置き・コードフェンスなし)
{{
  "scenes_considered": ["検討した場面を日本語1行ずつ(3〜5件)"],
  "items": [
    {{
      "topic_hook_ja": "記事のどの話題・気持ちから着想したか(本文に書かれていることだけ。1〜2文)",
      "basic_en": "基本の平易な英文(学習者の一般文)",
      "basic_ja": "その日本語訳",
      "further_en": "もう一歩進んだ表現を含む英文(基本表現と同じ場面で言える完全な文)",
      "further_ja": "その日本語訳",
      "core_expression": "覚える核の表現(例: 'be A about B' のように短く)",
      "point_ja": "学習ポイント(上記規則)",
      "why_ja": "なぜこの表現を選んだか(1〜2文)",
      "meaning_shift_note": "基本表現からの意味・強さ・場面の違い。同義に近ければ空文字",
      "self_check": {{"usable_by_learner": "学習者が自分で使える場面を1つ", "not_in_kp_grammar_body": true}}
    }}
  ]
}}
- itemsは1〜2件。"""

PROMPTS = {"v1": PROMPT_V1}

# v2: v1の欠陥(同義語への単純置換=言い換え型、学校英語で既習の頻出熟語で新鮮味が薄い)に対する修正。構造・出力schemaはv1と同じ。
_V2_E = """   (e) 「覚えたい」と思える発見があるか。
   (f) 言い換え型でないか: 基本表現を同義語に置き換えただけ(例: useful→come in handy、decide→make up one's mind のように、意味がほぼ同じで差が「別の言い方」だけ)の候補は外す。発展表現が、基本表現では言えない含み(立場・距離感・度合い・感情の機微・話の運び方)を足すか、日本語から直訳しにくい発想を教えるものを選ぶ。
   (g) 新鮮味: 中学〜高校の熟語集に載っている頻出表現(例: pay off、come in handy、jump to conclusions のレベル)は、学習者が既に「知っている」ため原則外す。「聞いたことはあるが自分では使いこなせていない」ものを優先する。最初に浮かんだ候補が頻出表現なら、同じ場面で一段使える幅の広い別候補を探す。"""
PROMPTS["v2"] = (PROMPT_V1.replace("   (e) 「覚えたい」と思える発見があるか。", _V2_E)
    .replace("使い方(どんな時に言うか)と応用場面を示す。", "使い方(どんな時に言うか)、基本表現では言えない点(what it adds)、応用場面を示す。日本語話者が間違えやすい点(直訳しにくい点・前置詞・語順)が重要なら一言添える。"))
assert PROMPTS["v2"] != PROMPT_V1

def build_prompt(inp, ver):
    kp = "; ".join(f"{e}({g})" if g else e for e, g in inp["kp"]); gr = "; ".join(inp["grammar"]) or "(なし)"
    return PROMPTS[ver].format(title=inp["title"], level=inp["level"], body=inp["body"], kp=kp, grammar=gr)

def spent():
    if not os.path.exists(USAGE): return 0.0
    return sum((json.loads(l).get("cost_jpy") or 0) for l in open(USAGE, encoding="utf-8") if l.strip())
def cost(model, u):
    ip, cp, op = PRICE[model]; i = u.get("input_tokens") or 0; c = u.get("cached_input_tokens") or 0; o = u.get("output_tokens") or 0
    return round(((max(i - c, 0) * ip + c * cp + o * op) / 1e6) * USD_JPY, 4)
def get_client():
    from dotenv import load_dotenv; load_dotenv(os.path.join(ROOT, ".env"))
    from openai import OpenAI; return OpenAI()
def call(client, model, prompt, tag, max_out=9000):
    assert os.environ.get("OSF_PAID") == "1"
    with _lock:
        if spent() > CAP_JPY: raise RuntimeError("CAP refused")
    t0 = time.time(); r = client.responses.create(model=model, input=[{"role": "user", "content": prompt}], max_output_tokens=max_out); el = round(time.time() - t0, 2)
    u = r.usage; ud = {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None)}
    d = getattr(u, "input_tokens_details", None); ud["cached_input_tokens"] = getattr(d, "cached_tokens", 0) if d else 0
    od = getattr(u, "output_tokens_details", None); ud["reasoning_tokens"] = getattr(od, "reasoning_tokens", None) if od else None
    text = getattr(r, "output_text", None) or ""; c = cost(model, ud)
    os.makedirs(os.path.join(OUT, "raw"), exist_ok=True); open(os.path.join(OUT, "raw", f"{tag}.txt"), "w", encoding="utf-8", newline="\n").write(text)
    with _lock, open(USAGE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"tag": tag, "model": r.model, "requested": model, "response_id": r.id, "usage": ud, "cost_jpy": c, "elapsed_sec": el, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}, ensure_ascii=False) + "\n")
    return text, r.model, ud, c, el
def parse(text):
    a, b = text.find("{"), text.rfind("}")
    return json.loads(text[a:b + 1])
def worker(client, cell, ver, model, tag, res, T):
    try:
        inp = inputs_for(cell, T); pr = build_prompt(inp, ver); t = f"{cell}__{ver}__{tag}"
        text, m, ud, c, el = call(client, model, pr, t)
        try: doc = parse(text); err = None
        except Exception as e: doc = None; err = repr(e)
        json.dump({"cell": cell, "ver": ver, "model_requested": model, "model": m, "usage": ud, "cost_jpy": c, "elapsed_sec": el, "parse_error": err, "result": doc, "inputs_summary": {"kp": inp["kp"], "grammar": inp["grammar"], "nuance_expr": inp["nuance_expr"]}},
                  open(os.path.join(OUT, f"{t}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        res[cell] = {"cost": c, "sec": el, "err": err, "n": len((doc or {}).get("items", []))}
    except Exception as e:
        import traceback; res[cell] = {"error": repr(e), "tb": traceback.format_exc()}
def main():
    cmd = sys.argv[1]
    if cmd == "dry":
        T = _load_nt().load_targets()
        for c in CELLS:
            i = inputs_for(c, T); p = build_prompt(i, "v1"); print(c, "body_chars", len(i["body"]), "kp", [k[0] for k in i["kp"]], "gram", len(i["grammar"]), "prompt_chars", len(p), "nuance", i["nuance_expr"])
        return
    ver, model, tag = sys.argv[2:5]; cells = sys.argv[5:] or CELLS; os.makedirs(OUT, exist_ok=True)
    T = _load_nt().load_targets(); client = get_client(); res = {}; ths = []
    for c in cells:
        th = threading.Thread(target=worker, args=(client, c, ver, model, tag, res, T)); th.start(); ths.append(th)
    for th in ths: th.join()
    print(json.dumps(res, ensure_ascii=False, indent=1)); print("spent_total_jpy", round(spent(), 4))
if __name__ == "__main__": main()
