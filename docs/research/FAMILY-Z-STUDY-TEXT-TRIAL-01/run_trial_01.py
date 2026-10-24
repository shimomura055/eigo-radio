# FAMILY-Z-STUDY-TEXT-TRIAL-01 Trial専用script(DEV。Production経路から参照されない)。
# 使い方: py run_trial_01.py build   -> PROMPT_01.md生成のみ(API 0)
#         py run_trial_01.py send    -> API 1 call(Luna)、OUTPUT_01_RAW.md/usage保存
import sys, json, re, io, os
BASE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(BASE, "..", "..", "..", "er026_output", "family_z_production_e2e_01", "the_gift_of_the_magi", "run_sf_prod_01")
TEXT = open(os.path.join(RUN, "writer", "r2.md"), encoding="utf-8").read()
paras = [p.strip() for p in TEXT.split("\n\n") if p.strip()]
title = paras[0]; body = paras[1:]
assert title == "# The Gift of the Magi"
numbered = "\n\n".join(f"[P{i}] {p}" for i, p in enumerate(body, 1))
KP = [
 ("hand down", "～を後の世代に受け継がせる", "One was Jim’s gold watch, handed down from his grandfather to his father, and then to him.", "to pass something to a younger person or a later generation"),
 ("catch sight of", "～をふと目にする", "Then she caught sight of herself in the mirror.", "to see something suddenly or by chance"),
 ("catch one's breath", "息を整える", "Outside a hair-goods shop, she paused just long enough to catch her breath.", "to pause and breathe normally again after effort"),
]
kp_txt = "\n".join(f"{i}. 英語表現: {k}\n   日本語gloss: {g}\n   本文の該当文: {s}\n   既存の音声解説(英語・重複回避用): \"{e}\"" for i,(k,g,s,e) in enumerate(KP,1))
PROMPT = f"""あなたは英語学習コンテンツの編集者です。下の英語ポッドキャスト台本(Advancedレベル)を読んだ学習者向けに、音声と連動して読む「英語学習テキスト解説」を日本語で書いてください。

# 作品・レベル
- 作品: The Gift of the Magi(『賢者の贈り物』)
- レベル: Advanced(CEFR B1を目標に書かれた英文。学習者はB1〜B2相当の日本語話者)

# 本文(段落番号[P1]〜[P{len(body)}]は参照用。引用では番号を書かない)
{numbered}

# 既存のKey Phrase(Part 1で使う。新たなフレーズ選定は禁止)
{kp_txt}

# 出力する内容(4つのPartをすべて、この順序・この見出しで)

## Part 1. Vocabulary & Expressions
上のKey Phrase 3件それぞれについて、次を書く: 英語表現 / 日本語での意味 / 本文中の英文とその日本語訳 / この表現の意味と、学習上なぜ重要か。
- 他の場面での追加例文は書かない。
- 「既存の音声解説」はすでに音声で流れているため、その単純な言い換え・繰り返しにしない。音声では触れていない観点(語法、構造、本文中での働き、似た表現との関係など)を扱う。

## Part 2. Grammar & Sentence Structure
本文から、学習価値の高い文法・構文を0〜2個選ぶ。無理に2個選ばない。適切なものがなければ0個とし、その旨を一文で書く。
- 各項目: 本文の英文の引用+日本語訳、文法・構文の仕組み、本文中での意味・効果。
- 教科書的な一般説明だけで終わらず、この英文を読み解く助けになる説明にする。

## Part 3. Nuance & Deeper Understanding
本文から価値のある英語表現・ニュアンスのテーマを0〜1個選ぶ。適切なテーマがなければ0個とし、その旨を一文で書く。
- 単語の意味だけでは伝わりにくいニュアンス、似た表現との違い、表現による印象の違いなどを深掘りする。
- Part 1・Part 2と内容を重複させない。
- 物語の感想や一般論ではなく、英語学習としての価値を重視する。

## Part 4. Think & Express
作品の内容に関連して、学習者が自分の考えを英語で表現するための問いを1問作る。次の4点を書く: 英語の質問 / その日本語訳 / 英語の回答例 / その日本語訳。回答例は学習者が参考にできる自然な英語にする。

# 制約
- 本文の英文を引用するときは、本文から一字一句そのまま(逐語)引用する。改変・要約・つなぎ合わせをしない。
- 本文にない事実・登場人物の言動・表現を作らない。説明は本文の根拠に基づく。
- 日本語は学習者に読みやすく書く。
- 理解度チェック・クイズは書かない。
- 出力はMarkdownのみ。上記の見出し(## Part 1〜4)構成を守り、前置き・後書きは付けない。
"""
if __name__ == "__main__":
    mode = sys.argv[1]
    open(os.path.join(BASE, "PROMPT_01.md"), "w", encoding="utf-8", newline="\n").write(
        "# PROMPT_01(Lunaへ渡したuser message全文。developer messageなし、few-shotなし、1 call)\n\n```text\n" + PROMPT + "```\n")
    open(os.path.join(BASE, "_prompt_raw.txt"), "w", encoding="utf-8", newline="\n").write(PROMPT)
    print("paras", len(body), "prompt chars", len(PROMPT), "words", len(re.findall(r"[A-Za-z’'-]+", "\n".join(body))))
    if mode == "send":
        from dotenv import load_dotenv; load_dotenv()
        from openai import OpenAI
        import time
        c = OpenAI(); t0 = time.time()
        r = c.responses.create(model="gpt-6-luna", input=[{"role": "user", "content": PROMPT}])
        el = time.time() - t0
        open(os.path.join(BASE, "OUTPUT_01_RAW.md"), "w", encoding="utf-8", newline="\n").write(r.output_text)
        u = r.usage
        d = {"model_requested": "gpt-6-luna", "model_actual": r.model, "response_id": r.id, "elapsed_sec": round(el, 1),
             "input_tokens": u.input_tokens, "cached_input_tokens": getattr(u.input_tokens_details, "cached_tokens", 0),
             "output_tokens": u.output_tokens, "reasoning_tokens": getattr(u.output_tokens_details, "reasoning_tokens", None),
             "reasoning_param": "not specified (provider default; same as Production KP stage)"}
        uncached = d["input_tokens"] - d["cached_input_tokens"]
        usd = uncached*0.10/1e6 + d["cached_input_tokens"]*0.01/1e6 + d["output_tokens"]*0.50/1e6
        d["cost_usd"] = round(usd, 6); d["cost_jpy_at_160"] = round(usd*160, 4)
        json.dump(d, open(os.path.join(BASE, "usage_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(d, ensure_ascii=False))
