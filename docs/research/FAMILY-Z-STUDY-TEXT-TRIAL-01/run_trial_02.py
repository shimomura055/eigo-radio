# FAMILY-Z-STUDY-TEXT-TRIAL-01 Trial-02専用script(DEV。Production非参照)。
# run_trial_01.PROMPTのPart 1ブロックだけを差し替える(Part 2-4/制約/本文/KPは同一objectから派生)。
# 使い方: py run_trial_02.py build | send
import sys, os, json, hashlib, difflib
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import run_trial_01 as t1
OLD_START = "## Part 1. Vocabulary & Expressions\n"
OLD_END = "\n## Part 2."
s = t1.PROMPT.index(OLD_START); e = t1.PROMPT.index(OLD_END)
NEW_P1 = """## Part 1. Vocabulary & Expressions
上のKey Phrase 3件それぞれについて、次を書く: 1 英語表現 / 2 日本語の意味 / 3 本文中の英文(逐語引用) / 4 英文の日本語訳 / 5 実用性を重視した解説。
実用性重視の解説ルール: その単語・フレーズが、本文以外のどのような日常・仕事・社会的場面で使えるかを、具体的かつ簡潔に説明する。重視する点: 実際にどのような状況で使えるか / その表現を使うと何が伝わるか / 学習者が自分の英語表現に取り入れやすい説明になっているか。文法構造の解説は原則としてPart 2に任せる。「ほかの場面で使うと」という独立した追加例文は書かない。実用場面は日本語の解説文で伝える。
"""
PROMPT = t1.PROMPT[:s] + NEW_P1 + t1.PROMPT[e:]
if __name__ == "__main__":
    mode = sys.argv[1]
    open(os.path.join(BASE, "PROMPT_02.md"), "w", encoding="utf-8", newline="\n").write(
        "# PROMPT_02(Lunaへ渡したuser message全文。developer messageなし、few-shotなし、1 call。Part 1のみTrial-01から差替)\n\n```text\n" + PROMPT + "```\n")
    diff = "".join(difflib.unified_diff(t1.PROMPT.splitlines(1), PROMPT.splitlines(1), "PROMPT_01", "PROMPT_02", n=0))
    open(os.path.join(BASE, "PROMPT_DIFF_02.md"), "w", encoding="utf-8", newline="\n").write(
        "# PROMPT_DIFF_02(Trial-01→Trial-02のPrompt差分。差分はPart 1ブロックのみ)\n\n```diff\n" + diff + "\n```\n\n"
        "判断: ユーザー参考例3件(hand down/catch sight of/catch one's breath)はPromptに入れていない。入れると一発生成の評価にならない(参考例は評価時の比較基準のみ)。\n")
    print("prompt chars", len(PROMPT), "sha256", hashlib.sha256(PROMPT.encode()).hexdigest()[:16], "sha01", hashlib.sha256(t1.PROMPT.encode()).hexdigest()[:16])
    if mode == "send":
        from dotenv import load_dotenv; load_dotenv()
        from openai import OpenAI
        import time
        c = OpenAI(); t0 = time.time()
        r = c.responses.create(model="gpt-6-luna", input=[{"role": "user", "content": PROMPT}])
        el = time.time() - t0
        open(os.path.join(BASE, "OUTPUT_02_RAW.md"), "w", encoding="utf-8", newline="\n").write(r.output_text)
        u = r.usage
        d = {"model_requested": "gpt-6-luna", "model_actual": r.model, "response_id": r.id, "elapsed_sec": round(el, 1),
             "input_tokens": u.input_tokens, "cached_input_tokens": getattr(u.input_tokens_details, "cached_tokens", 0),
             "output_tokens": u.output_tokens, "reasoning_tokens": getattr(u.output_tokens_details, "reasoning_tokens", None),
             "reasoning_param": "not specified (provider default; same as Trial-01)"}
        uncached = d["input_tokens"] - d["cached_input_tokens"]
        usd = uncached*0.10/1e6 + d["cached_input_tokens"]*0.01/1e6 + d["output_tokens"]*0.50/1e6
        d["cost_usd"] = round(usd, 6); d["cost_jpy_at_160"] = round(usd*160, 4)
        json.dump(d, open(os.path.join(BASE, "usage_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(d, ensure_ascii=False))
