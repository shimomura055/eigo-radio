# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-KP-EN-EXPLANATION-STYLE-TRIAL-01 Trial専用(Production非経由、Production Style定数/Master Store/v4音声を変更しない)。
対象=Coffee v4 Advanced KP英語解説clip。同一voice(Aoede)・同一モデル(gemini-3.8-flash-lite-tts、sync generate_content)・同一原稿・同一trim(KEY_PHRASE margin 0.30s)。
P0=KEY_PHRASE_EXPLANATION_EN(Variant B現行)を同条件で再生成(+ノイズ基準 P0r2/P0r3)、P1-P8=P0に差分句のみ追加。各1回、ASR非verifiedなら同一Promptで最大2試行。
modes: prompts / gen <target...>"""
import os, sys, json, time, hashlib, threading, concurrent.futures as cf
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03 as B
OUT = os.path.join(ROOT, "er057_output", "kp_en_explanation_style_trial_01")
ATT = os.path.join(OUT, "attempts"); AUD = os.path.join(OUT, "audio"); GENLOG = os.path.join(OUT, "generation_log_01.jsonl")
BUDGET = 25.0; MAX_ATTEMPTS = 2; MARGIN = 0.30
P0 = "clear, precise, at a measured pace, without dragging"
import er033_tts_flash_lite_family_x_styles_01 as _fl
assert _fl.KEY_PHRASE_EXPLANATION_EN == P0
TARGETS = {  # kp番号 -> 解説原稿(v4使用clipのtts_generation_results.json text逐語)
 4: "to become lower in amount or level",
 1: "a delay between one event and another",
}
ADD = {
 "P1": ("文中ポーズ抑制", "Say the whole definition as one smooth, continuous phrase, without long pauses in the middle."),
 "P2": ("句のつながり", "Link the words together naturally, with only the briefest natural breaths between phrases."),
 "P3": ("文頭から文末まで途切れない流れ", "Let the sentence flow from its first word to its last, without stopping partway through."),
 "P4": ("文末処理", "Finish the last word cleanly and naturally, without trailing off or lingering."),
 "P5": ("自然な説明口調", "Sound like a friendly teacher giving a short, natural definition."),
 "P6": ("P1+P4 連続性+文末", None),
 "P7": ("P2+P5 つながり+説明口調", None),
 "P8": ("P1+P4+P5 バランス型", None),
}
COMBO = {"P6": ["P1", "P4"], "P7": ["P2", "P5"], "P8": ["P1", "P4", "P5"]}
def style_of(k):
    import re; k = re.sub(r"r\d$", "", k)
    if k == "P0": return P0
    parts = COMBO.get(k, [k])
    return P0 + " " + " ".join(ADD[p][1] for p in parts)
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
_l = threading.Lock(); _spent = {"jpy": 0.0}
def append(rec):
    with _l: open(GENLOG, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
def tts_input(kp):
    import er003_v1_n3_01_tts_generate as n3
    return n3.tts_safe_en(TARGETS[kp])
def cand_list():
    return ["P0", "P0r2", "P0r3"] + [f"P{i}" for i in range(1, 9)]

def cmd_prompts():
    L = ["# prompts_kp_en_explanation_style_01(FAMILY-X-COFFEE-KP-EN-EXPLANATION-STYLE-TRIAL-01、Trial限定)", "",
         "送信方式: `generate_content`、`Part(text=<解説原稿(tts_safe_en適用済み)>, speech_metadata=SpeechMetadata(style=<下記>))`、model=`gemini-3.8-flash-lite-tts`(Production同一、例外種別2: 測定対象=Production使用モデル)、voice=`Aoede`、Standard同期(Production実行はBATCH、モデル・voice・Style経路は同一)。trim=KEY_PHRASE_TRIM_SAFETY_MARGIN 0.30s(Production同一)。数値WPM・速度倍率・速度を上げる語(fast/quick/brisk/lively)はPromptに書かない。機械減速・機械無音除去なし。",
         "P1〜P8 = P0の文を一字も変えず末尾に差分句のみ追加。P0は現行Variant B(`KEY_PHRASE_EXPLANATION_EN`)。P0r2/P0r3はP0と同一Promptの再生成(TTS生成ごとのばらつき=ノイズ基準)。", "",
         "## 解説原稿(v4使用clipの逐語)", ""]
    for kp, t in TARGETS.items(): L.append(f"- KP{kp}: `{t}` (tts_input sha256 `{sha(tts_input(kp))}`)")
    L += ["", f"## P0(基準=現行Variant B) 文字数 {len(P0)} / sha256 `{sha(P0)}`", "", "```", P0, "```", ""]
    L += ["## 差分表", "", "| 候補 | 狙い | P0への追加句 | 文字数 | sha256 |", "|---|---|---|---|---|", f"| P0 | 現行 | (なし) | {len(P0)} | `{sha(P0)[:12]}` |"]
    for k in ADD:
        s = style_of(k); add = s[len(P0)+1:]
        L.append(f"| {k} | {ADD[k][0]} | {add} | {len(s)} | `{sha(s)[:12]}` |")
    L.append("")
    for k in ADD:
        s = style_of(k)
        L += [f"## {k} {ADD[k][0]}", "", f"文字数 {len(s)}(P0 {len(P0)}、差 {len(s)-len(P0):+d}) / sha256 `{sha(s)}`", "", "```", s, "```", ""]
    os.makedirs(os.path.join(OUT, "prompts"), exist_ok=True)
    open(os.path.join(OUT, "prompts", "prompts_kp_en_explanation_style_01.md"), "w", encoding="utf-8").write("\n".join(L))

def run(kp, cand, call):
    import er002_common as common, er003_b1_p3u_audio as p3u, er003_audio_tts_asr_safety as safety
    text = tts_input(kp); style = style_of(cand)
    for attempt in range(1, MAX_ATTEMPTS + 1):
        jid = f"kp{kp}_{cand}_a{attempt}"
        if _spent["jpy"] > BUDGET: return {"id": jid, "status": "BUDGET_STOP"}
        t0 = time.time(); samples = usage = None
        for tech in (1, 2):
            try: samples, usage = call(text, style, B.VOICE); break
            except Exception as e: append({"job": jid, "event": "TTS_TECH_FAILURE", "tech_try": tech, "error": f"{type(e).__name__}: {str(e)[:200]}"})
        if samples is None: continue
        tts = ((usage["input_tokens"] or 0) * B.PRICE_IN + (usage["output_tokens"] or 0) * B.PRICE_OUT) / 1e6 * B.USD_JPY
        with _l: _spent["jpy"] += tts
        trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=MARGIN)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job": jid, "kp": kp, "cand": cand, "attempt": attempt, "model_requested": B.MODEL, "model_version": usage["model_version"],
               "voice": B.VOICE, "execution_mode": "STANDARD(sync, DEV Trial)", "style_sha256": sha(style), "style_text": style,
               "tts_input": text, "tts_input_sha256": sha(text), "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"],
               "tts_cost_jpy": round(tts, 4), "elapsed_s": round(time.time() - t0, 1), "trim_info": {k: v for k, v in ti.items() if isinstance(v, (int, float, str, bool, type(None)))}}
        if trimmed is None: rec["status"] = "NO_SPEECH"; append(rec); continue
        wav = os.path.join(ATT, f"{jid}.wav"); common.write_wav_float(wav, trimmed, common.SAMPLE_RATE, 1)
        rec.update(wav=os.path.relpath(wav, ROOT).replace("\\", "/"), wav_sha256=B.sha_file(wav), raw_duration_s=ti["raw_duration_seconds"], trimmed_duration_s=round(len(trimmed) / common.SAMPLE_RATE, 3))
        a = B.asr_and_judge(wav, text, "kp_explanation_en")
        with _l: _spent["jpy"] += a["asr_cost_jpy_est"]
        rec.update(status="OK", asr_model=B.ASR_MODEL, **a); append(rec)
        if a["verified"]:
            import shutil; shutil.copyfile(wav, os.path.join(AUD, f"kp{kp}_{cand}.wav"))
            return {"id": jid, "status": "OK", "attempt": attempt, "cls": a["classification"]}
    return {"id": f"kp{kp}_{cand}", "status": "NOT_VERIFIED_AFTER_MAX"}

def cmd_gen(kps, rep=False):
    for p in (OUT + "/STOP", ROOT + "/er026_output/family_z_production_e2e_01/STOP_ALL"):
        assert not os.path.exists(p), "STOP sentinel: " + p
    os.makedirs(ATT, exist_ok=True); os.makedirs(AUD, exist_ok=True)
    B.patch_validator_telemetry(); call = B.make_tts_call(); t0 = time.time()
    cl = [f"P{i}r{n}" for i in range(1, 9) for n in (2, 3)] if rep else cand_list()   # rep=P1-P8の再生成(ノイズ対策の同一Prompt追加サンプル、候補追加ではない)
    jobs = [(kp, c) for kp in kps for c in cl]
    with cf.ThreadPoolExecutor(4) as ex: res = list(ex.map(lambda j: run(j[0], j[1], call), jobs))
    s = {"kps": kps, "results": res, "spent_jpy_est": round(_spent["jpy"], 3), "elapsed_s": round(time.time() - t0, 1)}
    json.dump(s, open(os.path.join(OUT, f"gen_summary_kp{'_'.join(map(str,kps))}{'_rep' if rep else ''}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in res: print(r)
    print(s["spent_jpy_est"], s["elapsed_s"])
if __name__ == "__main__":
    m = sys.argv[1]
    if m == "prompts": cmd_prompts()
    elif m == "rep": cmd_gen([int(a) for a in sys.argv[2:]], rep=True)
    else: cmd_gen([int(a) for a in sys.argv[2:]])
