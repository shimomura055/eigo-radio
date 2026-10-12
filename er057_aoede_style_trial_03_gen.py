# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-AOEDE-STYLE-TRIAL-03 Trial専用(Production非経由)。
共通サンプル=Coffee v3 Advanced Part1 原稿(PD8既存音声=P0を再利用、P0は再生成しない)。
P1-P8 = PD8 に差分句のみ追加(速度指示 unhurried は維持)。各1回生成、ASR非verifiedなら同一Promptで最大2試行まで。
modes: prompts / gen"""
import os, sys, json, time, hashlib, concurrent.futures as cf, threading
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03 as B
OUT = os.path.join(ROOT, "er057_output", "aoede_style_trial_03")
ATT = os.path.join(OUT, "attempts"); GENLOG = os.path.join(OUT, "generation_log_03.jsonl")
BUDGET = 40.0; MAX_ATTEMPTS = 2
PD8 = "Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy."
PD8_SHA = "329ff46a5ec3877f7dc23375e14ee8a806efeff7cfe27963492a3cf95d182226"
INT1 = "Let the pitch rise and fall a little more on key words."
INT2 = "Let the pitch rise and fall noticeably on key words and at the ends of phrases, with a clear, natural melodic contour."
BRI1 = "Add a touch more brightness and a hint of a smile in the voice, while staying unhurried."
BRI2 = "Bring a cheerful, sparkling warmth with a clearly audible smile in the voice, while staying unhurried."
CLA = "Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard."
INT1c = "Let the pitch rise and fall a little more on key words."
CANDS = {
 "P1": ("抑揚 少し強め", [INT1], "抑揚(音の上下)を少しだけ強める句を追加"),
 "P2": ("抑揚 中程度", [INT2], "抑揚を中程度に強める句を追加(語末・句末の上下も指定)"),
 "P3": ("明るさ・活力 少し", [BRI1], "明るさ・笑顔感を少し足す句を追加(unhurried再掲)"),
 "P4": ("明るさ・活力 中程度", [BRI2], "明るさ・笑顔感を中程度に足す句を追加(unhurried再掲、lively等の速度誘発語は避ける)"),
 "P5": ("明瞭さ重点", [CLA], "子音・語尾・音節の明瞭さを指定する句を追加"),
 "P6": ("抑揚+明瞭", [INT1, CLA], "P1の抑揚句+P5の明瞭句"),
 "P7": ("明るさ+明瞭", [BRI1, CLA], "P3の明るさ句+P5の明瞭句"),
 "P8": ("抑揚+明るさ+明瞭 バランス型", [INT1, BRI1, CLA], "P1・P3・P5の各句を全て少しずつ(バランス型)"),
}
def style_of(k): return PD8 + " " + " ".join(CANDS[k][1])
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
_l = threading.Lock()
def append(rec):
    with _l: open(GENLOG, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
def job():
    return [j for j in B.jobs_def() if j["id"] == "adv_part1"][0]

def cmd_prompts():
    assert sha(PD8) == PD8_SHA
    L = ["# prompts_aoede_style_03(FAMILY-X-COFFEE-AOEDE-STYLE-TRIAL-03、Trial限定)", "",
         "送信方式: `generate_content`、`Part(text=<Coffee v3 Advanced Part1 原稿(tts_safe_news_en適用済み)>, speech_metadata=SpeechMetadata(style=<下記>))`、model=`gemini-3.8-flash-lite-tts`、voice=`Aoede`、Standard同期。数値WPM・速度倍率はPromptに書かない。機械減速なし。",
         "P1〜P8 = P0(PD8)の文を一字も変えず、末尾に差分句のみ追加。P0の速度指示(unhurried等)は全候補で維持。lively/energy等の速度を上げる語は使わない(Pace Trial-02でF5が最速だった知見の再利用)。", "",
         "## P0(基準=現行Coffee v3 Advanced使用のPD8、既存音声を再利用・再生成なし)", "", f"文字数 {len(PD8)} / sha256 `{sha(PD8)}`", "", "```", PD8, "```", ""]
    for k, (jp, add, d) in CANDS.items():
        s = style_of(k)
        L += [f"## {k} {jp}", "", f"文字数 {len(s)}(P0 {len(PD8)}、差 {len(s)-len(PD8):+d}) / sha256 `{sha(s)}`", "", "```", s, "```", "", f"P0からの差分: {d}。追加句: " + " / ".join(add), ""]
    open(os.path.join(OUT, "prompts", "prompts_aoede_style_03.md"), "w", encoding="utf-8").write("\n".join(L))

def run(cand, call):
    import er002_common as common, er003_b1_p3u_audio as p3u, er003_audio_tts_asr_safety as safety
    j = job(); style = style_of(cand)
    for attempt in range(1, MAX_ATTEMPTS + 1):
        jid = f"{cand}_a{attempt}"
        if B._spent["jpy"] > BUDGET: return {"id": cand, "status": "BUDGET_STOP"}
        t0 = time.time(); samples = usage = None
        for tech in (1, 2):
            try: samples, usage = call(j["tts_input"], style, B.VOICE); break
            except Exception as e: append({"job": jid, "event": "TTS_TECH_FAILURE", "tech_try": tech, "error": f"{type(e).__name__}: {str(e)[:200]}"})
        if samples is None: continue
        tts = ((usage["input_tokens"] or 0) * B.PRICE_IN + (usage["output_tokens"] or 0) * B.PRICE_OUT) / 1e6 * B.USD_JPY
        with B._lock: B._spent["jpy"] += tts
        trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job": jid, "cand": cand, "attempt": attempt, "model_requested": B.MODEL, "model_version": usage["model_version"],
               "voice": B.VOICE, "execution_mode": "STANDARD(sync, DEV Trial)", "style_sha256": sha(style), "style_text": style,
               "tts_input_sha256": sha(j["tts_input"]), "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"], "tts_cost_jpy": round(tts, 4), "elapsed_s": round(time.time() - t0, 1)}
        if trimmed is None: rec["status"] = "NO_SPEECH"; append(rec); continue
        wav = os.path.join(ATT, f"{jid}.wav"); common.write_wav_float(wav, trimmed, common.SAMPLE_RATE, 1)
        rec.update(wav=os.path.relpath(wav, ROOT).replace("\\", "/"), wav_sha256=B.sha_file(wav), raw_duration_s=ti["raw_duration_seconds"], trimmed_duration_s=round(len(trimmed) / common.SAMPLE_RATE, 3),
                   duration_anomaly=safety.detect_duration_anomaly(ti["raw_duration_seconds"], j["tts_input"], "en"))
        a = B.asr_and_judge(wav, j["tts_input"], j["role"])
        with B._lock: B._spent["jpy"] += a["asr_cost_jpy_est"]
        rec.update(status="OK", asr_model=B.ASR_MODEL, **a); append(rec)
        if a["verified"]: return {"id": cand, "status": "OK", "attempt": attempt, "cls": a["classification"], "wav": rec["wav"]}
    return {"id": cand, "status": "NOT_VERIFIED_AFTER_MAX", "wav": rec.get("wav") if 'rec' in dir() else None}

def cmd_gen():
    B.patch_validator_telemetry(); call = B.make_tts_call(); t0 = time.time()
    with cf.ThreadPoolExecutor(4) as ex: res = list(ex.map(lambda c: run(c, call), CANDS))
    s = {"results": res, "spent_jpy_est": round(B._spent["jpy"], 3), "elapsed_s": round(time.time() - t0, 1)}
    json.dump(s, open(os.path.join(OUT, "gen_summary_03.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in res: print(r)
    print(s["spent_jpy_est"], s["elapsed_s"])
if __name__ == "__main__": {"prompts": cmd_prompts, "gen": cmd_gen}[sys.argv[1]]()
