# -*- coding: utf-8 -*-
"""JA-GLOSS-NUANCE-01 Trial: gloss新規生成(X2p', newgen_meaning_v1)の現行Prompt(A)と改善案Prompt(B)を、
保存済みの実入力(gloss_alignment_prompt.txt)で再生して比較する。DEV/Trial専用。Production経路(er003_key_words_gloss_alignment.py)は変更しない。
- A = 保存済みPromptそのまま(現行Productionの文面と一致することを assert)。
- B = A の NEWGEN_MEANING_TEXT 内 japanese_gloss 欄を差替え + 訳語の選び方欄を追加(他は1字も変えない)。
- 呼出は make_alignment_fn と同一(responses API / reasoning=high / developer=NEWGEN_DEVELOPER_MESSAGE / schema=NEWGEN_JSON_SCHEMA)。
- 費用: 確定単価(gpt-6-luna 0.10/0.01/0.50 USD per 1M、為替160円/USD=Production記録 0.6128円/回と整合)で呼出ごとに台帳へ加算し、cap超過見込みで停止。
使い方: python gloss_nuance_trial_01.py plan.json  (plan = {"jobs":[{"tag","prompt","arm","rep","model","only_ranks"?}], "cap_jpy":, "ledger":, "outdir":})"""
import json, os, sys, time, types, hashlib
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_WT = os.environ.get("JAG_WT", os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")))
sys.path.insert(0, REPO_WT)
# gaのimport連鎖(er002系)を避けるためのstub(replay用途のみ。make_alignment_fn/定数/schemaしか使わない)
_s = types.ModuleType("er003_audio_tts_asr_safety")
_k = types.ModuleType("er003_key_words_canonicalization"); _k._PERSON_DEPENDENT_TO_GENERIC = {}
sys.modules["er003_audio_tts_asr_safety"] = _s
sys.modules["er003_key_words_canonicalization"] = _k
import er003_key_words_gloss_alignment as ga

PRICING = {"gpt-6-luna": (0.10, 0.01, 0.50), "gpt-6.1-sol": (2.00, 0.10, 10.00)}  # USD per 1M (input, cached, output)
JPY_PER_USD = 160.0

OLD_BULLET_PREFIX = "- japanese_gloss: yesなら"
NEW_JG_BULLET = ("- japanese_gloss: yesなら、naive_jaをそのまま写さず、自然で平易な訳(英和辞典の定訳や日本語の慣用表現があればそれ)を選ぶ。"
    "partly/noのときは、まず、このkey_phraseのこの語義に日本語の定訳(英和辞典の見出し訳や日本語として定着した言い方。例: cut cornersなら「手を抜く」、break evenなら「収支がとんとんになる」)があればそれを優先し、"
    "無い場合だけ、naive_jaの字義の像を使わず、meaning_in_text_enの意味【全体】を日本語の慣用表現か平易な短い言い換えで表す(意味の一部だけを取り出した語にしない)。"
    "ただし、naive_ja自体が英和辞典の定訳で、本文の語義(比喩・拡張した用法を含む)でも日本語としてその語が通じるなら、partlyであってもその定訳を使ってよい"
    "(『字義の像を使わない』のは、その語では本文の意味が日本語として伝わらない場合の規則です)。"
    "naive_jaの語を別の語に置き換えるときは、動作主(誰が)・動詞の意味を変えない(例: 「誰も出なかった電話」を「誰もかけたくなかった電話」のように、動詞の意味を別の意味にずらさない)。"
    "key_phrase全体(目的語・修飾語を含む)の意味を落とさず、key_phraseと同じ品詞・同じ程度の長さの句にする(説明文・定義文にしない)。\n")
NEW_CHOICE_BULLET = ("- 訳語の選び方(japanese_glossの最終確認): 訳語は、本文の文脈で最も限定的な日本語1語(または自然な1句)にする。"
    "決めた訳語を、同じ意味領域の近い意味の一般語と比べ、key_phraseに固有の分野・含み・強さが日本語でも区別して伝わるかを確かめる"
    "(例: strollを「歩く」とせず「ぶらぶら歩く」、gulpを「飲む」とせず「ぐいっと飲む」)。"
    "meaning_in_text_enが一般的な言い換えになっていても、その一般語をそのままglossにしない(言い換えは意味を確かめるためのもので、訳語にそのまま使う語ではない)。"
    "訳語は原則1つにし、不必要に複数の意味を並べない。1つの訳語では重要な意味が落ちる、または誤解を生む場合に限り、括弧を使わず「A、B」の形で2つまで並べてよい。\n")

# ---- B2: B(v1)がverdictで0/3だった原因(yes分岐の「naive_jaをそのまま写さず」=OF-KP1-05 anchoring対策が、naive_ja=定訳のときも定訳を避けさせる)を直す改訂 ----
B2_JG_BULLET = ("- japanese_gloss: yesなら、naive_jaを無批判に写さず、自然で平易な訳を選ぶ(英和辞典の定訳や日本語の慣用表現があればそれを使う。naive_jaと同じ語になっても、それが定訳・日本語として定着した訳語だと確かめられる場合はよい)。"
    "partly/noのときは、まず、このkey_phraseのこの語義に日本語の定訳(英和辞典の見出し訳や日本語として定着した言い方。例: cut cornersなら「手を抜く」、break evenなら「収支がとんとんになる」)があればそれを優先し、"
    "無い場合だけ、naive_jaの字義の像を使わず、meaning_in_text_enの意味【全体】を日本語の慣用表現か平易な短い言い換えで表す(意味の一部だけを取り出した語にしない)。"
    "ただし、naive_ja自体が英和辞典の定訳で、本文の語義(比喩・拡張した用法を含む)でも日本語としてその語が通じるなら、partlyであってもその定訳を使ってよい"
    "(『字義の像を使わない』のは、その語では本文の意味が日本語として伝わらない場合の規則です)。"
    "naive_jaの語を別の語に置き換えるときは、動作主(誰が)・動詞の意味を変えない(例: 「誰も出なかった電話」を「誰もかけたくなかった電話」のように、動詞の意味を別の意味にずらさない)。"
    "key_phrase全体(目的語・修飾語を含む)の意味を落とさず、key_phraseと同じ品詞・同じ程度の長さの句にする(説明文・定義文にしない)。")
B2_CHOICE_BULLET = ("- 訳語の最終確認(japanese_glossを決めたら必ず行う): 選んだ日本語が、key_phraseよりも一般的な(上位・近義の)英語の語に当たる日本語と同じになっていないか確かめる"
    "(例: boastのglossを、sayに当たる「言う」にしない。sprintのglossを、runに当たる「走る」にしない)。"
    "同じになっている場合は、key_phrase固有の分野・含み・強さを保つ、より限定的な定訳に直す。meaning_in_text_enが一般的な言い換えでも、その一般語はglossの根拠にならない(言い換えは意味を確かめるためのもの)。"
    "ただし、key_phrase自体が一般的な語で、区別できる自然な日本語が無い場合は、そのままでよい。"
    "訳語は原則1つにし、不必要に複数の意味を並べない。1つの訳語では重要な意味が落ちる、または誤解を生む場合に限り、括弧を使わず「A、B」の形で2つまで並べてよい。")
B3_JG_BULLET = ("- japanese_gloss: 次の順で決める。"
    "(1) key_phraseが1語のとき(naive_jaは英和辞典の見出し訳にあたる): 見出し訳が自然で平易な日本語で、本文の語義でも日本語として通じる(比喩・拡張した用法でも、その日本語の語が同じ比喩・用法で使える場合を含む)なら、それをそのままjapanese_glossにする。"
    "見出し訳を、意味を言い換えた一般的な別の語(近い意味の上位語)や、説明文・定義文に置き換えない。見出し訳が本文の語義に合わない、または不自然なときだけ、本文の語義に合う別の定訳か、短い言い換えを選ぶ。"
    "(2) key_phraseが2語以上のとき: yesなら、naive_jaをそのまま写さず、自然で平易な訳(英和辞典の定訳や日本語の慣用表現があればそれ)を選ぶ。"
    "partly/noなら、まず、このkey_phraseのこの語義に日本語の定訳(英和辞典の見出し訳や日本語として定着した言い方。例: cut cornersなら「手を抜く」、break evenなら「収支がとんとんになる」)があればそれを優先し、"
    "無い場合だけ、naive_jaの字義の像を使わず、meaning_in_text_enの意味【全体】を日本語の慣用表現か平易な短い言い換えで表す(意味の一部だけを取り出した語にしない)。"
    "(1)(2)共通: naive_jaの語を別の語に置き換えるときは、動作主(誰が)・動詞の意味を変えない(例: 「誰も出なかった電話」を「誰もかけたくなかった電話」のように、動詞の意味を別の意味にずらさない)。"
    "key_phrase全体(目的語・修飾語を含む)の意味を落とさず、key_phraseと同じ品詞・同じ程度の長さの句にする(説明文・定義文にしない)。")
B3_CHOICE_BULLET = ("- 訳語の最終確認(japanese_glossを決めたら必ず行う): 記事全体を通じて筆者が続けている比喩(例: 試合・旅・劇などのたとえ)の中で使われている語は、比喩の像を保つ見出し訳をそのまま使うほうが、本文と学習項目の対応が学習者に伝わる。"
    "比喩が指す一般的な意味へ言い換えるのは、日本語ではその像が通じない場合だけにする。"
    "選んだ日本語が、key_phraseより一般的な(上位・近義の)英語の語に当たる日本語と同じになっていないかも確かめ、同じなら、key_phrase固有の分野・含み・強さを保つ訳に直す(key_phrase自体が一般的な語で、区別できる自然な日本語が無い場合はそのままでよい)。"
    "訳語は原則1つにし、不必要に複数の意味を並べない。1つの訳語では重要な意味が落ちる、または誤解を生む場合に限り、括弧を使わず「A、B」の形で2つまで並べてよい。")
VARIANTS = {"B": (NEW_JG_BULLET.rstrip("\n"), NEW_CHOICE_BULLET.rstrip("\n")), "B2": (B2_JG_BULLET, B2_CHOICE_BULLET), "B3": (B3_JG_BULLET, B3_CHOICE_BULLET)}


def build_b_meaning_text(variant="B"):
    base = ga.NEWGEN_MEANING_TEXT
    lines = base.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith(OLD_BULLET_PREFIX)]
    assert len(idx) == 1, idx
    jg, ch = VARIANTS[variant]
    lines[idx[0]] = jg
    # 訳語の選び方欄は japanese_gloss 欄の直後に追加
    lines.insert(idx[0] + 1, ch)
    return "\n".join(lines)


def make_prompt(a_text, arm):
    assert ga.NEWGEN_MEANING_TEXT in a_text and a_text.count(ga.NEWGEN_MEANING_TEXT) == 1, "保存Promptが現行Production文面と一致しません"
    if arm == "A":
        return a_text
    if arm in VARIANTS:
        return a_text.replace(ga.NEWGEN_MEANING_TEXT, build_b_meaning_text(arm))
    raise ValueError(arm)


def cost_jpy(model, usage):
    pin, pc, pout = PRICING[model]
    inp = usage.get("input_tokens") or 0
    cached = usage.get("cached_input_tokens") or 0
    out = usage.get("output_tokens") or 0
    usd = ((inp - cached) * pin + cached * pc + out * pout) / 1e6
    return round(usd * JPY_PER_USD, 4)


def call_once(job, text):
    from dotenv import load_dotenv
    load_dotenv(os.environ.get("JAG_ENV", r"C:\Users\tensh\eigo-radio\.env"))
    from openai import OpenAI
    client = OpenAI()
    model = job.get("model", "gpt-6-luna")
    r = client.responses.create(
        model=model, reasoning={"effort": job.get("effort", "high")},
        text={"format": {"type": "json_schema", **ga.NEWGEN_JSON_SCHEMA}},
        input=[{"role": "developer", "content": ga.NEWGEN_DEVELOPER_MESSAGE}, {"role": "user", "content": text}])
    if r.model != model:
        raise RuntimeError(f"model mismatch {r.model} != {model}")
    u = r.usage
    usage = {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
             "cached_input_tokens": getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0}
    return r.output_text, r.model, r.id, usage


def main(plan_path):
    plan = json.load(open(plan_path, encoding="utf-8"))
    outdir = plan["outdir"]; os.makedirs(outdir, exist_ok=True)
    ledger_path = plan["ledger"]
    ledger = json.load(open(ledger_path, encoding="utf-8")) if os.path.exists(ledger_path) else {"calls": [], "total_jpy": 0.0}
    cap = plan["cap_jpy"]
    todo = []
    for j in plan["jobs"]:
        name = f'{j["tag"]}__{j["arm"]}__{j.get("model","gpt-6-luna")}__r{j["rep"]}'
        outp = os.path.join(outdir, name + ".json")
        if os.path.exists(outp):
            continue  # 再実行しても既存結果は再呼出しない(二重課金防止)
        todo.append((name, outp, j))
    est_per_call = plan.get("est_per_call_jpy", 0.8)
    if ledger["total_jpy"] + est_per_call * len(todo) > cap:
        print(f"STOP: 予定費用 {ledger['total_jpy'] + est_per_call*len(todo):.2f} > cap {cap}"); sys.exit(3)
    print(f"jobs to run: {len(todo)} (ledger so far {ledger['total_jpy']:.3f} JPY, cap {cap})")

    def run(t):
        name, outp, j = t
        a_text = open(j["prompt"], encoding="utf-8").read()
        text = make_prompt(a_text, j["arm"])
        t0 = time.time()
        out_text, model_id, rid, usage = call_once(j, text)
        c = cost_jpy(model_id, usage)
        rec = {"name": name, "job": j, "prompt_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
               "model": model_id, "response_id": rid, "usage": usage, "cost_jpy": c, "elapsed_s": round(time.time() - t0, 1),
               "output_text": out_text}
        json.dump(rec, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return rec
    with ThreadPoolExecutor(max_workers=plan.get("workers", 4)) as ex:
        for rec in ex.map(run, todo):
            ledger["calls"].append({k: rec[k] for k in ("name", "model", "response_id", "usage", "cost_jpy")})
            ledger["total_jpy"] = round(ledger["total_jpy"] + rec["cost_jpy"], 4)
            json.dump(ledger, open(ledger_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(rec["name"], rec["usage"], rec["cost_jpy"], "cum", ledger["total_jpy"])


if __name__ == "__main__":
    main(sys.argv[1])
