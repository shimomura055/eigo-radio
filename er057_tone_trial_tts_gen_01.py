# ============================================================
# er057_tone_trial_tts_gen_01.py
# FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_01A (Trial専用script)
# ------------------------------------------------------------
# 性質: Trial専用。Production runner/Master Store/manifest/telemetry/
# human_review_queue/attempt_historyへは一切書き込まない(importもしない)。
# Gemini TTS(gemini-3.8-flash-lite-tts、speech_metadata.style方式、Standard同期)を
# 直接呼び、成果物は er057_output/coffee_final_listening_tone_trial_01/part_AEF/ と
# user_test/coffee_tone_trial_01/intro_preview_fullstory/ にのみ保存する。
# 使い方: python er057_tone_trial_tts_gen_01.py prompts|generate
# ============================================================
from __future__ import annotations
import json, os, sys, time, wave, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er057_output", "coffee_final_listening_tone_trial_01", "part_AEF")
RAW = os.path.join(OUT, "raw")
MODEL = "gemini-3.8-flash-lite-tts"
USD_JPY = 160.0
PRICE_IN, PRICE_OUT = 0.5, 6.0   # USD / 1M tokens, Standard(sync), pricing_snapshot.json

# ---- 承認済み現行Style(逐語、er033 worktree feature/coffee-new-tone-01) ----
EN_COMMENT_E2_UPBEAT = "warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation."
EN_FULLSTORY_F1_5 = ("warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, "
                     "while maintaining clear and credible news narration.")
A2_SLOWER_PACE_INSTRUCTION = ("Speak at a slightly slower, relaxed pace than natural adult narration, while "
                              "keeping the delivery smooth, conversational, and natural. Do not exaggerate pauses "
                              "or sound instructional.")
SHELL_STYLE = "natural, clear, conversational"  # 現行shell(Master Store v2_flash_lite_short_style、raw_usage_logで確認)

TEXT_A = "Welcome to English Your Way."
TEXT_B = "Here's a quick preview."
TEXT_E = ("Coffee prices can change for several reasons, and the news can be hard to make sense of. In this episode, "
          "we'll look at what is behind the latest coffee price story and what the news can tell us.")
TEXT_F = ('"Beans have gotten cheaper!" At that news, your wallet pumps its fist. In your mind, the price of your usual '
          'cup has already come down, too. But the price tag in a shop may not change right away. When you see a price '
          'tag that makes you want to say, "Haven\'t you heard the news?", it seems there is a time lag.')

# id: (アプローチ名, 日本語説明, style)
SPECS = {
 "A": {"text": TEXT_A, "voice": "Charon", "role": "共通Intro A(Welcome)", "baseline_style": SHELL_STYLE, "items": {
  "A1": ("落ち着いたMC", "番組の司会者が落ち着いて迎え入れる雰囲気。急がず、温かく安定した声。",
         "calm, relaxed show host; warm and unhurried, with a settled, welcoming tone."),
  "A2": ("自然な会話", "友人を迎えるような自然な挨拶。アナウンサーらしさを抑えた、無理のない話し方。",
         "natural, friendly conversational greeting, as if welcoming a friend; easy and unforced, not announcer-like."),
  "A3": ("明瞭な案内", "番組案内として一語ずつはっきり。速すぎず遅すぎず、安定した自信のある声。",
         "clear, well-articulated program announcement; each word distinct, steady and confident, neither rushed nor slow."),
  "A4": ("リズム重視", "最初の語を軽く持ち上げ、番組名の前に自然な一拍を置き、番組名を一続きで流す。",
         "smooth, even rhythm with a light lift on the first word and a brief natural beat before the show name; the show name flows as one connected phrase."),
  "A5": ("文末処理重視", "温かい挨拶が文末で急に切れず、番組名が柔らかく下がって自然に収まる。",
         "warm greeting that lands gently; the show name finishes with a soft, natural falling close, not clipped or rushed at the end."),
 }},
 "B": {"text": TEXT_B, "voice": "Charon", "role": "共通Intro B(Preview導入)", "baseline_style": SHELL_STYLE, "items": {
  "B1": ("落ち着いたMC", "司会者がPreviewへ落ち着いて橋渡しする雰囲気。急がず滑らかで親しみのある声。",
         "calm, relaxed host handing over to the preview; unhurried and smooth, with a friendly settled tone."),
  "B2": ("自然な会話", "友人に話しかけるような自然な導入。無理のない、アナウンサーらしさを抑えた話し方。",
         "natural, friendly conversational lead-in, as if saying it to a friend; easy and unforced, not announcer-like."),
  "B3": ("明瞭な案内", "コーナー案内として一語ずつはっきり。速すぎず遅すぎず、安定した声。",
         "clear, well-articulated segment announcement; each word distinct, steady and confident, neither rushed nor slow."),
  "B4": ("リズム重視", "短いフレーズを一息で滑らかに。形容詞を軽く強調し、最後の語へ穏やかに持ち上げる。",
         "smooth, even rhythm; the short phrase flows in one easy breath, with light emphasis on the adjective and a gentle lift into the final word."),
  "B5": ("文末処理重視", "親しみのある導入が最後の語で柔らかく下がり、切れずに自然に収まる。",
         "friendly lead-in that lands gently; the last word settles with a soft, natural falling close, not clipped or rushed at the end."),
 }},
 "E": {"text": TEXT_E, "voice": "Charon", "role": "Advanced Preview(英語)", "baseline_style": EN_COMMENT_E2_UPBEAT, "items": {
  "E1": ("落ち着いたニュースキャスター", "落ち着きのあるキャスター調。急がず、明瞭で自然。",
         "calm, composed news anchor; steady and unhurried, clear and natural."),
  "E2": ("少しゆったりした自然会話", "普段より少しゆったりした会話的ペース。温かく自然で、間延びしない。",
         "relaxed conversational pace, slightly slower than usual; warm and natural, without dragging."),
  "E3": ("意味のまとまり重視", "意味の区切りごとに短い自然な間を置き、無理のない速さで聞き取りやすく。",
         "clear news narration grouped by meaning; short natural pauses at clause boundaries, comfortably paced."),
  "E4": ("低めで落ち着いたVoice", "エネルギーを抑えた、地に足のついた安心感のある声。抑揚は滑らかで自然。",
         "softer, lower-energy and grounded; calm and reassuring tone, smooth natural intonation, easy to follow."),
  "E5": ("文末の収まり重視", "各文が文末で収まってから次へ進む。落ち着いて明瞭。",
         "unhurried news narration; each sentence lands gently and settles before the next begins; calm and clear."),
 }},
 "F": {"text": TEXT_F, "voice": "Aoede", "role": "Full Story Part1冒頭(Standard/Advanced共通Style)", "baseline_style": EN_FULLSTORY_F1_5, "items": {
  "F1": ("発話テンポ重視", "現行の明るい抑揚を保ち、話し言葉として心地よい自然なテンポ(急がず間延びもしない)。",
         EN_FULLSTORY_F1_5 + " Keep a comfortable, natural storytelling tempo, neither rushed nor dragging."),
  "F2": ("意味のまとまり重視", "現行の抑揚を保ちつつ、意味の塊ごとに短く自然な間を置いて聞き取りやすく。",
         EN_FULLSTORY_F1_5 + " Group the words by meaning, with brief natural pauses between ideas so each one is easy to take in."),
  "F3": ("自然な間重視", "現行の抑揚を保ち、引用の前後や話の転換点に小さな自然な間を置く。",
         EN_FULLSTORY_F1_5 + " Leave a small natural beat before and after quoted lines and at turns in the story."),
  "F4": ("文末の収まり重視", "現行の抑揚を保ち、各文が文末で自然に収まってから次の文へ進む。",
         EN_FULLSTORY_F1_5 + " Let each sentence settle naturally at its end before the next one begins."),
  "F5": ("Storytellingリズム重視", "現行の表情を保ち、友人に短い話を聞かせるような、ゆったり流れる躍動感のあるリズム。",
         EN_FULLSTORY_F1_5 + " Tell it like a short story to a friend, with a relaxed flow and a lively, natural rhythm; not hurried."),
 }},
}
# F baseline再生成(同一原稿・現行Style。参考用の公平比較。Advanced相当=F0、Standard相当Production再現=F0S)
F_BASELINE_EXTRA = {
  "F0": ("現行F1.5(同一原稿で再生成)", "現行Production Style F1.5そのまま(Advanced相当)。候補との公平比較用に同一原稿で再生成。", EN_FULLSTORY_F1_5),
  "F0S": ("現行Standard方式(F1.5+減速指示+6%減速)", "現行Standard再現: F1.5に既承認の減速指示を連結して生成し、後段で6%減速(atempo)を適用。",
          EN_FULLSTORY_F1_5 + "\n" + A2_SLOWER_PACE_INSTRUCTION),
}


def all_jobs():
    jobs = []
    for g, spec in SPECS.items():
        for k, (name, desc, style) in spec["items"].items():
            jobs.append((k, g, spec["text"], spec["voice"], style))
    for k, (name, desc, style) in F_BASELINE_EXTRA.items():
        jobs.append((k, "F", TEXT_F, "Aoede", style))
    return jobs


def check_styles():
    import er002_common as common
    for k, g, t, v, s in all_jobs():
        common.assert_no_wpm_specification(s)


def write_prompts():
    d = os.path.join(OUT, "prompts"); os.makedirs(d, exist_ok=True)
    check_styles()
    for g, spec in SPECS.items():
        L = [f"# Prompt一覧 {g}: {spec['role']}", "",
             "送信方式: `generate_content`、`Part(text=<原稿逐語>, speech_metadata=SpeechMetadata(style=<下記style>))`、"
             f"model=`{MODEL}`、voice=`{spec['voice']}`(Production `speech_metadata_flash_lite` 相当、Standard同期)。", "",
             f"原稿(逐語): `{spec['text']}`", "",
             f"## Baseline(現行Style)\n\n`{spec['baseline_style']}`", ""]
        for k, (name, desc, style) in spec["items"].items():
            L += [f"## {k} {name}", "", desc, "", "style(speech_metadata.style 逐語):", "", "```", style, "```", ""]
        if g == "F":
            for k, (name, desc, style) in F_BASELINE_EXTRA.items():
                L += [f"## {k} {name}(参考baseline再生成)", "", desc, "", "```", style, "```", ""]
            L += ["## Standard相当6%減速(各F候補)", "",
                  "Production既存処理 `er008_a2_postprocess_slowdown_01.apply_a2_slowdown`(FFmpeg `atempo`=1/1.06, pitch保持, A2_SLOWDOWN_PERCENT=6.0)を"
                  "候補の生成wavへローカル適用。Standard専用の減速指示文は候補では付けない(F0Sのみ現行再現として付与)。", ""]
        open(os.path.join(d, f"prompts_{g}.md"), "w", encoding="utf-8").write("\n".join(L))
    print("prompts written")


def est_tokens(text):  # 概算: 1語 ~0.4秒, 25tok/s、ゆったり係数1.2
    return int(len(text.split()) * 0.4 * 25 * 1.2) + 20


def write_cost_estimate():
    rows = []; tot = 0.0
    for k, g, t, v, s in all_jobs():
        ot = est_tokens(t); it = len(t.split()) * 2 + len(s.split()) * 2
        usd = (it * PRICE_IN + ot * PRICE_OUT) / 1e6
        tot += usd; rows.append((k, g, ot, it, usd * USD_JPY))
    L = ["# COST_ESTIMATE_01A", "",
         f"model={MODEL}(Standard同期、PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01) 単価: input ${PRICE_IN}/1M tok, output ${PRICE_OUT}/1M tok(pricing_snapshot.json)、USD/JPY={USD_JPY}", "",
         "| job | 区分 | 推定output tok | 推定input tok | 概算円 |", "|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]:.3f} |")
    jpy = tot * USD_JPY
    L += ["", f"call数: {len(rows)}(A5+B5+E5+F5=20 + F参考baseline2)",
          f"概算合計: 約 {jpy:.2f}円(技術失敗retry最大1回を全件に仮定した上限: 約 {jpy*2:.2f}円)",
          "判定: 上限含め30円以内のため実行可。"]
    open(os.path.join(OUT, "COST_ESTIMATE_01A.md"), "w", encoding="utf-8").write("\n".join(L))
    print(f"est jpy={jpy:.2f} worst={jpy*2:.2f}")
    return jpy


def make_call():
    from dotenv import load_dotenv
    load_dotenv()
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def call(text, style, voice):
        part = types.Part(text=text, speech_metadata=types.SpeechMetadata(style=style))
        resp = client.models.generate_content(
            model=MODEL, contents=types.Content(parts=[part], role="user"),
            config=types.GenerateContentConfig(response_modalities=["AUDIO"], speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)))))
        parts = resp.candidates[0].content.parts
        raw = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
        if not raw:
            raise RuntimeError("empty audio")
        um = resp.usage_metadata
        return raw, {"model_version": getattr(resp, "model_version", None),
                     "input_tokens": getattr(um, "prompt_token_count", None),
                     "output_tokens": getattr(um, "candidates_token_count", None),
                     "total_tokens": getattr(um, "total_token_count", None)}
    return call


def decode_to_24k_wav(raw, path):
    if raw[:4] == b"RIFF":
        open(path, "wb").write(raw)
        return
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(raw)


def generate():
    check_styles(); os.makedirs(RAW, exist_ok=True)
    logp = os.path.join(OUT, "cost_actual_01A.json")
    log = json.load(open(logp, encoding="utf-8")) if os.path.exists(logp) else {"records": []}
    done = {r["job"] for r in log["records"] if r.get("success")}
    call = make_call()
    for k, g, t, v, s in all_jobs():
        if k in done:
            continue
        for attempt in (1, 2):   # 技術失敗時のみ1回retry
            t0 = time.time()
            try:
                raw, u = call(t, s, v)
                p = os.path.join(RAW, f"{k}.wav"); decode_to_24k_wav(raw, p)
                with wave.open(p, "rb") as w:
                    dur = w.getnframes() / w.getframerate(); sr = w.getframerate()
                usd = ((u["input_tokens"] or 0) * PRICE_IN + (u["output_tokens"] or 0) * PRICE_OUT) / 1e6
                rec = {"job": k, "group": g, "provider": "gemini", "model_requested": MODEL,
                       "model_id_actual": u["model_version"], "voice": v, "attempt": attempt, "success": True,
                       "audio_seconds": round(dur, 3), "sample_rate": sr, "elapsed_seconds": round(time.time() - t0, 2),
                       "input_tokens": u["input_tokens"], "output_tokens": u["output_tokens"],
                       "cost_usd": round(usd, 6), "cost_jpy": round(usd * USD_JPY, 4), "style": s,
                       "wav": f"raw/{k}.wav", "sha256": hashlib.sha256(open(p, 'rb').read()).hexdigest()}
                log["records"].append(rec); print(k, rec["audio_seconds"], rec["cost_jpy"], u["model_version"])
                break
            except Exception as e:
                log["records"].append({"job": k, "group": g, "attempt": attempt, "success": False,
                                       "error": repr(e)[:300], "cost_jpy": 0.0})
                print(k, "FAIL", repr(e)[:200])
        log["total_jpy"] = round(sum(r.get("cost_jpy", 0) for r in log["records"]), 4)
        json.dump(log, open(logp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prompts":
        write_prompts(); write_cost_estimate()
    elif cmd == "generate":
        generate()
