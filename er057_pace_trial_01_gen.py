# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-01 委任_02 Trial専用script(Production非経由)。
modes: prompts(prompts_pace_01.md生成) / gen(8候補x3Part生成+Primary ASR)。
Master Store/manifest/telemetry/queue/attempt_historyへは書かない。validator telemetryはプロセス内リストへ差替え。
再生成なし(技術失敗のみ1回retry)。ASR NGでも再生成せず警告記録。予算上限JPY40超過見込みで停止。"""
import os, sys, json, time, hashlib, concurrent.futures as cf, threading
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03 as B   # TTS直接呼出部・ASR判定を再利用(import時副作用なし)
OUT = os.path.join(ROOT, "er057_output", "pace_trial_01")
ATT = os.path.join(OUT, "attempts")
GENLOG = os.path.join(OUT, "generation_log_01.jsonl")
BUDGET = 40.0
BASE_STYLE = "warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration."
F5_TAIL = "Tell it like a short story to a friend, with a relaxed flow and a lively, natural rhythm; not hurried."
CANDS = {
 "PC1": ("落ち着いたニュースナレーション方向", "Deliver it like a calm, composed news narrator giving a measured, unhurried report."),
 "PC2": ("急がず自然な息継ぎ(文間の間)方向", "Take your time, with a natural, unhurried breath between sentences, as if talking with a friend and nothing to rush."),
 "PC3": ("意味単位で区切る方向", "Phrase the story in meaningful chunks, letting each idea land before moving on to the next."),
 "PC4": ("文末を静かに収める方向", "Let each sentence settle softly at its end, with a gentle fall in pitch, before the next one begins."),
 "PC5": ("目の前の1人へ語りかける方向", "Speak as if to one attentive listener sitting across from you, warm and conversational, easy to follow."),
 "PC6": ("重要語・数字を際立たせる方向", "Give key words and numbers a little extra weight and clarity, with natural pauses around them, so the main points stand out."),
 "PC7": ("ゆとりある語り手(余白)方向", "Tell it like a thoughtful storyteller, relaxed and spacious, with room to breathe between phrases; never hurried."),
 "PC8": ("丁寧で滑らかな運び方向(教材調は避ける)", "Speak with a measured, deliberate cadence that lets each point land, yet stays smooth and connected; never word by word."),
}
def style_of(k): return BASE_STYLE + " " + CANDS[k][1]
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()

def cmd_prompts():
    L = ["# prompts_pace_01(FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-01 委任_02、Trial限定)", "",
         "送信方式: `generate_content`、`Part(text=<Advanced Full Story Part原稿(tts_safe_news_en適用済み)>, speech_metadata=SpeechMetadata(style=<下記style>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Aoede`、Standard同期。数値WPM・速度倍率はPromptに書かない。機械減速なし。",
         "全候補は F5 の共通前半(Baseline現行Style)を維持し、F5固有の後半1文(`%s`)を、別方向の1文へ**置換**(追記ではない)。" % F5_TAIL, "",
         "## F5(基準、既存音声を再利用・再生成なし)", "", f"文字数 {len(style_of_f5())} / sha256 `{sha(style_of_f5())}`", "", "```", style_of_f5(), "```", ""]
    for k, (jp, tail) in CANDS.items():
        s = style_of(k)
        L += [f"## {k} {jp}", "", f"F5との差分: 後半1文を置換(F5後半 {len(F5_TAIL)}字 -> {len(tail)}字)。全体 {len(s)}字(F5 {len(style_of_f5())}字、差 {len(s)-len(style_of_f5()):+d})。", "",
              f"sha256 `{sha(s)}`", "", "```", s, "```", ""]
    open(os.path.join(OUT, "prompts", "prompts_pace_01.md"), "w", encoding="utf-8").write("\n".join(L))
def style_of_f5(): return BASE_STYLE + " " + F5_TAIL

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
    json.dump(summ, open(os.path.join(OUT, "gen_summary_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in results: print(r)
    print("spent", summ["spent_jpy_est"], "elapsed", summ["elapsed_s"])

if __name__ == "__main__":
    {"prompts": cmd_prompts, "gen": cmd_gen}[sys.argv[1]]()
