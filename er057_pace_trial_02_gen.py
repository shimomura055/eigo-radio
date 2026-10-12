# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-01 委任_01(PACE-02) Trial専用script(Production非経由)。
modes: prompts(prompts_pace_02.md生成) / gen(8候補x3Part生成+Primary ASR)。
Master Store/manifest/telemetry/queue/attempt_historyへは書かない。validator telemetryはプロセス内リストへ差替え。
再生成なし(技術失敗のみ1回retry)。ASR NGでも再生成せず警告記録。予算上限JPY40超過見込みで停止。"""
import os, sys, json, time, hashlib, concurrent.futures as cf, threading
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03 as B   # TTS直接呼出部・ASR判定を再利用(import時副作用なし)
OUT = os.path.join(ROOT, "er057_output", "pace_trial_02")
ATT = os.path.join(OUT, "attempts")
GENLOG = os.path.join(OUT, "generation_log_02.jsonl")
BUDGET = 40.0
F5_STYLE = "warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration. Tell it like a short story to a friend, with a relaxed flow and a lively, natural rhythm; not hurried."
CANDS = {
 "PD1": ("ニュースナレーション指示の全体再構成", "Read this as a warm, composed news presenter would on a friendly daytime program: clear, credible and approachable, with a steady, measured delivery and a gentle smile in the voice."),
 "PD2": ("テンポ誘導語の除去+表情維持", "Warm, friendly and expressive, with natural intonation and a smile in the voice; clear, credible news narration."),
 "PD3": ("意味単位での間(全体再構成)", "Friendly, expressive news storytelling. Pause briefly where an idea ends, at commas and between sentences, so each thought is easy to take in, then continue with a bright, warm tone."),
 "PD4": ("Podcastホスト調", "A warm, easygoing podcast host sharing an interesting news story with listeners: smiling, relaxed and confident, savoring the surprising moments instead of rushing to the next line."),
 "PD5": ("余裕のある語り(明るさ維持)", "Bright, warm and expressive, with the ease of a speaker who has plenty of time; let the key moments breathe, and keep the tone lively rather than slow or sleepy."),
 "PD6": ("聞き手への語りかけ+落ち着き", "Speak directly to one listener with warmth and a smile in your voice; calm, steady and reassuring, like a favorite morning radio host, while keeping the news clear and credible."),
 "PD7": ("文間の自然な呼吸+引用・数字で少し緩める", "Warm, friendly news narration. Take a natural breath between sentences and ease slightly on quoted words and key numbers, then carry on brightly with expressive intonation."),
 "PD8": ("ラジオ・フィーチャー調(温かく豊かな表現)", "Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy."),
}
def style_of(k): return CANDS[k][1]
def style_of_f5(): return F5_STYLE
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()

def cmd_prompts():
    L = ["# prompts_pace_02(FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-02 委任_01、Trial限定)", "",
         "送信方式: `generate_content`、`Part(text=<Advanced Full Story Part原稿(tts_safe_news_en適用済み)>, speech_metadata=SpeechMetadata(style=<下記style>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Aoede`、Standard同期。数値WPM・速度倍率はPromptに書かない。機械減速なし。",
         "今回は F5 の前半・後半を含む **Prompt全体** を、調整思想の異なる8方向へ再構成(追記ではなく置換・統合・削除)。分析は `PROMPT_ANALYSIS_02.md`。", "",
         "## F5(基準、既存音声を再利用・再生成なし)", "", f"文字数 {len(F5_STYLE)} / sha256 `{sha(F5_STYLE)}`", "", "```", F5_STYLE, "```", ""]
    for k, (jp, s) in CANDS.items():
        L += [f"## {k} {jp}", "", f"文字数 {len(s)}(F5 {len(F5_STYLE)}、差 {len(s)-len(F5_STYLE):+d})", "", f"sha256 `{sha(s)}`", "", "```", s, "```", "", "F5からの主要変更点: " + DIFF[k], ""]
    open(os.path.join(OUT, "prompts", "prompts_pace_02.md"), "w", encoding="utf-8").write(chr(10).join(L))
DIFF = {
 "PD1": "共通前半(gently upbeat / light sense of energy)と後半(short story to a friend / lively rhythm)を全削除し、「昼の番組の落ち着いた報道キャスター」役割+steady, measured delivery+gentle smileへ全面置換。",
 "PD2": "テンポ/エネルギー系の語(gently upbeat, light sense of energy, lively, rhythm, relaxed flow, not hurried)を全削除。表情語(warm, friendly, expressive, natural intonation, smile)と信頼性(credible news narration)のみ残す。最短(削除型)。",
 "PD3": "エネルギー語と友人への語り口を削除し、「意味が終わる所・コンマ・文間で短く間を置く」指示+bright, warm toneへ置換。",
 "PD4": "ニュースナレーション指定を外し、Podcastホスト役割(smiling, relaxed, confident)+「驚きの場面を味わい、次の行へ急がない」へ置換。",
 "PD5": "lively/rhythmを外し、「時間がたっぷりある話し手の余裕」+key momentsを呼吸させる+「slow/sleepyにしない」明示ガードへ置換。",
 "PD6": "ニュース調を従に回し、特定1人の聞き手への語りかけ+calm, steady, reassuring(朝のラジオホスト像)へ置換。",
 "PD7": "エネルギー語を削除し、「文間で自然に息継ぎ+引用語・重要数字で少し緩め、その後は明るく再開」の局所的な緩急指示へ置換。",
 "PD8": "ニュース調を外し、「愛されるラジオ・フィーチャー」調(unhurried, richly expressive, full vowels, gentle emphasis)+flat/sleepy防止へ置換。母音を十分に響かせる発声寄り。",
}
def run(job, cand, call, lock_state):
    import er002_common as common, er003_b1_p3u_audio as p3u, er003_audio_tts_asr_safety as safety
    import soundfile as sf
    style = style_of(cand); jid = f"{cand}_{job['id']}"
    if B._spent["jpy"] > BUDGET:
        B.append_log({"job": jid, "event": "BUDGET_STOP"}); return {"id": jid, "status": "BUDGET_STOP"}
    t0 = time.time(); samples = usage = None
    for tech in (1, 2):
        try:
            samples, usage = call(job["tts_input"], style, B.VOICE); break
        except Exception as e:
            append({"job": jid, "tech_try": tech, "event": "TTS_TECH_FAILURE", "error": f"{type(e).__name__}: {str(e)[:200]}"})
    if samples is None: return {"id": jid, "status": "TECH_FAIL"}
    tts_jpy = ((usage["input_tokens"] or 0) * B.PRICE_IN + (usage["output_tokens"] or 0) * B.PRICE_OUT) / 1e6 * B.USD_JPY
    with B._lock: B._spent["jpy"] += tts_jpy
    trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job": jid, "cand": cand, "part": job["id"], "attempt": 1, "model_requested": B.MODEL,
           "model_version": usage["model_version"], "voice": B.VOICE, "tts_backend": B.BACKEND, "execution_mode": "STANDARD(sync, DEV Trial)",
           "style_sha256": sha(style), "style_text": style, "tts_input_sha256": sha(job["tts_input"]), "manuscript_sha256": sha(job["manuscript"]),
           "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"], "tts_cost_jpy": round(tts_jpy, 4), "elapsed_s": round(time.time() - t0, 1)}
    if trimmed is None:
        rec.update(status="NO_SPEECH"); append(rec); return {"id": jid, "status": "NO_SPEECH"}
    wav = os.path.join(ATT, f"{jid}.wav"); common.write_wav_float(wav, trimmed, common.SAMPLE_RATE, 1)
    anomaly = safety.detect_duration_anomaly(ti["raw_duration_seconds"], job["tts_input"], "en")
    rec.update(wav=os.path.relpath(wav, ROOT).replace("\\", "/"), wav_sha256=B.sha_file(wav), raw_duration_s=ti["raw_duration_seconds"],
               trimmed_duration_s=round(len(trimmed) / common.SAMPLE_RATE, 3), duration_anomaly=anomaly)
    a = B.asr_and_judge(wav, job["tts_input"], job["role"])
    with B._lock: B._spent["jpy"] += a["asr_cost_jpy_est"]
    rec.update(status="OK", asr_model=B.ASR_MODEL, asr="primary_only(Trial隔離、NGでも再生成せず警告記録)", **a)
    append(rec)
    return {"id": jid, "status": "OK", "verified": a["verified"], "cls": a["classification"], "dur": rec["trimmed_duration_s"], "tts_jpy": rec["tts_cost_jpy"]}

_l = threading.Lock()
def append(rec):
    with _l:
        open(GENLOG, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")

def cmd_gen():
    os.makedirs(ATT, exist_ok=True)
    B.patch_validator_telemetry()
    jobs = [j for j in B.jobs_def() if j["level"] == "adv"]
    assert len(jobs) == 3
    call = B.make_tts_call(); t0 = time.time()
    tasks = [(j, c) for c in CANDS for j in jobs]
    with cf.ThreadPoolExecutor(6) as ex:
        results = list(ex.map(lambda t: run(t[0], t[1], call, None), tasks))
    summ = {"results": results, "spent_jpy_est": round(B._spent["jpy"], 3), "elapsed_s": round(time.time() - t0, 1),
            "validator_telemetry_redirected": B._sem_telemetry}
    json.dump(summ, open(os.path.join(OUT, "gen_summary_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in results: print(r)
    print("spent", summ["spent_jpy_est"], "elapsed", summ["elapsed_s"])

if __name__ == "__main__":
    {"prompts": cmd_prompts, "gen": cmd_gen}[sys.argv[1]]()
