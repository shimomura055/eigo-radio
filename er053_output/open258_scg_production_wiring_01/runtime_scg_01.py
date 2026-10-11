# ============================================================
# runtime_scg_01.py (OPEN-258-JA-SECONDARY-ASR-PRODUCTION-WIRING-01 委任_02)
# Production外のruntime evidence script。実Primary ASR(OpenAI gpt-4o-mini-transcribe)・
# 実Azure Speech STT・Production関数をそのまま使い、TTSだけ「保存済みwavを返す」差し替えにする
# (新規TTS=0)。使い方: python runtime_scg_01.py <case>   case = a|b|c|d|e
# 保存先: er053_output/open258_scg_production_wiring_01/runtime_evidence_01.jsonl(追記)
# ============================================================
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import sys
import time
import wave

WT = r"C:\Users\tensh\eigo-radio-scg"
MAIN = r"C:\Users\tensh\eigo-radio"
os.chdir(WT)
sys.path.insert(0, WT)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(MAIN, ".env"))  # worktreeには.envが無い(キーはmainの.envから)

import er002_common as common  # noqa: E402
import er003_b1_p4_audio as p4  # noqa: E402
import er003_b1_p9a_audio as p9a  # noqa: E402
import er003_v1_n3_01_tts_generate as n3  # noqa: E402
import er003_v1_sing01_voice01_generate as voice01  # noqa: E402
import er006_asr_provider_routing_01 as routing  # noqa: E402
import er007_ja_asr_validator_01 as javal  # noqa: E402
import er007_ja_secondary_asr_01 as ja  # noqa: E402
import er011_a2_reading_resolver_01 as rr  # noqa: E402
import er033_tts_flash_lite_backend_wiring_01 as flw  # noqa: E402

OUT_DIR = os.path.join(WT, "er053_output", "open258_scg_production_wiring_01")
EVIDENCE = os.path.join(OUT_DIR, "runtime_evidence_01.jsonl")
SCRATCH = os.path.join(OUT_DIR, "_runtime_tmp")  # 一時出力(commit対象外、後で削除)
os.makedirs(SCRATCH, exist_ok=True)

META_WAV = os.path.join(MAIN, "er019_output/family_x_audio_production_wiring_01/meta__run_regen_01/a2/narration/attempts/japanese_title_attempt1_customb8f0ff16.wav")
META_TEXT = "AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした"
G11_A1 = os.path.join(MAIN, "er012_output/editorial_b_family_voices_a2_production_wiring_01/kp_fix_01/a2/narration/attempts/kp5_ja_aoede_attempt1_standard.wav")
G11_A2 = os.path.join(MAIN, "er012_output/editorial_b_family_voices_a2_production_wiring_01/kp_fix_01/a2/narration/attempts/kp5_ja_aoede_attempt2_standard.wav")
G11_TEXT = "理屈の上では"
G12_WAV = os.path.join(MAIN, "er012_output/editorial_b_voices_a2_free_address_02/a2/narration/attempts/kp1_ja_aoede_attempt2_standard.wav")
G12_TEXT = "しばられず自由になれる感じの"
BUDGET_STOP_JPY = 4.0  # 追加課金上限5円。累計がこれを超えたら次の実行を拒否
ASR_JPY_PER_SEC = 0.003 / 60.0 * 160.0  # gpt-4o-mini-transcribe $0.003/min x 160円/USD(概算)

EVENTS: list = []


def dur(path):
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return None


def cumulative_cost():
    if not os.path.exists(EVIDENCE):
        return 0.0
    tot = 0.0
    for l in open(EVIDENCE, encoding="utf-8"):
        if l.strip():
            tot += json.loads(l).get("est_cost_jpy_case", 0.0) or 0.0
    return tot


# ---- 計装(実呼び出しを記録するだけ。挙動は変えない) ----
_orig_transcribe = routing.transcribe
_orig_strict = ja._azure_stt_strict
_orig_p4 = p4.get_full_text_via_azure_stt_continuous
_orig_resolve = rr.resolve_reading_diff


def _wrap_transcribe(wav_path, language, *a, **k):
    t0 = time.time()
    text, err = _orig_transcribe(wav_path, language, *a, **k)
    d = dur(wav_path)
    EVENTS.append({"event": "primary_asr", "provider": "openai_asr", "model_id": routing.require_asr_route(language)["model"],
                   "wav": os.path.basename(wav_path), "transcript": text, "error": err,
                   "wall_s": round(time.time() - t0, 2), "audio_s": d, "est_cost_jpy": round((d or 0) * ASR_JPY_PER_SEC, 4)})
    return text, err


def _wrap_strict(wav_path, language="ja-JP", timeout_seconds=90.0):
    t0 = time.time()
    text, err = _orig_strict(wav_path, language=language, timeout_seconds=timeout_seconds)
    d = dur(wav_path)
    EVENTS.append({"event": "azure_scg_secondary", "service": ja._scg_service_info(), "wav": os.path.basename(wav_path),
                   "transcript": text, "error": err, "wall_s": round(time.time() - t0, 2), "audio_s": d,
                   "est_cost_jpy": round(math.ceil(d or 0) * ja.SCG_AZURE_USD_PER_HOUR / 3600.0 * ja.SCG_JPY_PER_USD, 4)})
    return text, err


def _wrap_p4(wav_path, language="ja-JP", timeout_seconds=90.0):
    EVENTS.append({"event": "azure_legacy_cascade_call", "wav": os.path.basename(wav_path)})
    return _orig_p4(wav_path, language=language, timeout_seconds=timeout_seconds)


def _wrap_resolve(c, a):
    r = _orig_resolve(c, a)
    EVENTS.append({"event": "reading_resolver", "resolver_calls": r.get("resolver_calls"), "resolved_match": r.get("resolved_match"),
                   "est_cost_jpy": round(0.05 * (r.get("resolver_calls") or 0), 4)})  # 概算(Resolver LLM 1回=約0.05円の上限見積)
    return r


routing.transcribe = _wrap_transcribe
ja._azure_stt_strict = _wrap_strict
p4.get_full_text_via_azure_stt_continuous = _wrap_p4
rr.resolve_reading_diff = _wrap_resolve


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def make_fake_tts(seq, counter):
    """p9a.generate_narration_snippet / n3._generate_a2_japanese_minimal_instruction の差し替え。
    seq[i](iは呼出順、最後の要素を使い回す)の保存wavをout_pathへコピーして、実関数と同じ形のOK dictを返す。"""
    def fake(text, *a, **k):
        out_path = k.get("out_path") or (a[1] if len(a) > 1 else None)
        if out_path is None:
            raise RuntimeError("out_path not found")
        src = seq[min(counter["n"], len(seq) - 1)]
        counter["n"] += 1
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        shutil.copyfile(src, out_path)
        EVENTS.append({"event": "tts_substitute", "call_index": counter["n"], "src": os.path.basename(src)})
        d = dur(out_path)
        return {"status": "OK", "text": text, "language": "ja", "path": out_path, "model": "SUBSTITUTE(saved wav)",
                "voice": "SUBSTITUTE", "call_count": 1, "retry_count": 0, "sha256": sha(out_path),
                "duration_seconds": d, "trim_info": {"raw_duration_seconds": d, "trimmed_duration_seconds": d},
                "clipping_detected": False, "tts_backend": "structured_separation", "instruction": "substitute"}
    return fake


def fake_p9a_for(seq, counter):
    f = make_fake_tts(seq, counter)

    def fake(text, language, out_path, **k):
        return f(text, out_path=out_path)
    return fake


def fake_minimal_for(seq, counter):
    f = make_fake_tts(seq, counter)

    def fake(text, out_path, **k):
        return f(text, out_path=out_path)
    return fake


def summarize_result(r):
    keep = {}
    for k in ("status", "asr_verified", "asr_text", "audio_classification", "fallback_used", "reason", "scg_info",
              "canonical_text", "tts_input_text_after_reading_safety"):
        if k in r:
            keep[k] = r[k]
    for logk in ("attempts_log", "standard_attempts_log", "fallback_attempts_log"):
        if r.get(logk):
            keep[logk] = [{kk: vv for kk, vv in a.items() if kk in ("attempt", "status", "asr_text", "length_ok", "verified", "audio_classification", "reason")
                           } | {"scg_result": (a.get("scg_info") or {}).get("scg_result")} for a in r[logk]]
    return keep


def finish(case, desc, expected, observed, judgement, extra):
    azure_scg = [e for e in EVENTS if e["event"] == "azure_scg_secondary"]
    cost = sum(e.get("est_cost_jpy", 0) or 0 for e in EVENTS)
    rec = {"case": case, "description": desc, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "expected": expected, "observed": observed, "judgement": judgement,
           "primary_model_id": routing.require_asr_route("ja-JP")["model"],
           "azure_scg_calls": len(azure_scg), "azure_legacy_cascade_calls": sum(1 for e in EVENTS if e["event"] == "azure_legacy_cascade_call"),
           "est_cost_jpy_case": round(cost, 4), "events": EVENTS, **extra}
    with open(EVIDENCE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    print(json.dumps({"case": case, "judgement": judgement, "observed": observed, "est_cost_jpy_case": rec["est_cost_jpy_case"],
                      "cumulative_jpy": round(cumulative_cost(), 4)}, ensure_ascii=False, default=str))


def case_a():
    wav = META_WAV
    primary, err = routing.transcribe(wav, "ja-JP")
    t0 = time.time()
    d = ja.evaluate_attempt_ja_with_cascade_detail(META_TEXT, primary, wav, cascade_enabled=True)
    wall = round(time.time() - t0, 2)
    scg = d.get("scg_info") or {}
    ok = d["final_status"] == ja.SCG_FINAL_STATUS and d["verified"]
    if not d.get("scg_applied") and d["verified"] and d["final_status"] != ja.SCG_FINAL_STATUS:
        judgement = "NOT_REPRODUCED(PrimaryがPASS、SCG発火せず。根拠に数えない)"
    else:
        judgement = "PASS" if ok else "FAIL"
    finish("a", "Production関数evaluate_attempt_ja_with_cascade_detailへMETA japanese_title attempt1保存wavを実呼出(実Primary+実Azure、Resolver本番ON)",
           "TCM->SCG->PASS(SECONDARY_CONFIRMED_PRIMARY_FALSE_NG)",
           {"primary_transcript": primary, "primary_cls": d["steps"][0]["classification"], "final_status": d["final_status"],
            "verified": d["verified"], "scg_result": d.get("scg_result"), "secondary_transcript": scg.get("secondary_transcript"),
            "judgement_reason": scg.get("judgement_reason"), "exclusion_reason": scg.get("exclusion_reason"),
            "evaluate_wall_s": wall, "service": ja._scg_service_info()},
           judgement, {"wav_sha256": sha(wav), "wav_seconds": dur(wav)})


def case_b():
    out = os.path.join(SCRATCH, "b_out.wav")
    counter = {"n": 0}
    p9a_orig = p9a.generate_narration_snippet
    p9a.generate_narration_snippet = fake_p9a_for([META_WAV], counter)
    flw_orig = n3.c.batch_wiring.make_batch_tts_call_fn
    n3.c.batch_wiring.make_batch_tts_call_fn = lambda *a, **k: None
    try:
        r = n3.generate_a2_japanese_with_reading_safety(META_TEXT, out, "出演")
    finally:
        p9a.generate_narration_snippet = p9a_orig
        n3.c.batch_wiring.make_batch_tts_call_fn = flw_orig
    log = r.get("attempts_log") or []
    azure_n = sum(1 for e in EVENTS if e["event"] == "azure_scg_secondary")
    primary_events = [e for e in EVENTS if e["event"] == "primary_asr"]
    if r.get("status") == "OK" and counter["n"] == 1 and (r.get("scg_info") or {}).get("scg_result") == "PASS":
        judgement = "PASS"
    elif r.get("status") == "OK" and counter["n"] == 1 and azure_n == 0:
        judgement = "NOT_REPRODUCED(PrimaryがPASS、SCG発火せず。根拠に数えない)"
    else:
        judgement = "FAIL"
    finish("b", "n3.generate_a2_japanese_with_reading_safety(実)->repro01 loop(実)->guarded_generate(実)、TTSのみ保存wav差替(META japanese_title)",
           "PASSでattempt1完了、TTS差替呼出1回(=再生成0)、SCG PASS",
           {"result": summarize_result(r), "tts_substitute_calls": counter["n"], "primary_asr_calls": len(primary_events),
            "azure_scg_calls": azure_n},
           judgement, {})


def case_c():
    out = os.path.join(SCRATCH, "c_out.wav")
    counter_std = {"n": 0}
    counter_fb = {"n": 0}
    p9a_orig = p9a.generate_narration_snippet
    fb_orig = n3._generate_a2_japanese_minimal_instruction
    p9a.generate_narration_snippet = fake_p9a_for([G11_A2], counter_std)  # 標準1〜2回目: g11 a2(Primary不一致、Azure不一致=SCG NG想定)
    n3._generate_a2_japanese_minimal_instruction = fake_minimal_for([G11_A1], counter_fb)  # fallback: g11 a1(SCG PASS想定)
    flw_orig = n3.c.batch_wiring.make_batch_tts_call_fn
    n3.c.batch_wiring.make_batch_tts_call_fn = lambda *a, **k: None
    try:
        r = n3.generate_a2_japanese_with_reading_safety(G11_TEXT, out, "理屈")
    finally:
        p9a.generate_narration_snippet = p9a_orig
        n3._generate_a2_japanese_minimal_instruction = fb_orig
        n3.c.batch_wiring.make_batch_tts_call_fn = flw_orig
    std_log = r.get("standard_attempts_log") or []
    fb_log = r.get("fallback_attempts_log") or []
    std_scg = [(a.get("scg_info") or {}).get("scg_result") for a in std_log]
    fb_scg = [(a.get("scg_info") or {}).get("scg_result") for a in fb_log]
    exp_ok = (counter_std["n"] == 2 and counter_fb["n"] == 1 and std_scg == ["NG", "NG"] and fb_scg == ["PASS"]
              and r.get("status") == "OK" and r.get("fallback_used") is True)
    judgement = "PASS" if exp_ok else "FAIL_OR_NOT_REPRODUCED(Primary/Azureの出力が想定と異なる。観測値をそのまま記録)"
    finish("c", "n3経路: 標準1〜2回目=g11音声(SCG NG想定)、fallback=g11良音声(SCG PASS想定)。TTSのみ差替、attempt消費とfallback SCGを確認",
           "標準2回消費(SCG NG x2)->fallback 1回(SCG PASS)->OK(fallback_used=True)、合計3回上限内",
           {"result": summarize_result(r), "std_tts_calls": counter_std["n"], "fallback_tts_calls": counter_fb["n"],
            "standard_scg_results": std_scg, "fallback_scg_results": fb_scg},
           judgement, {})


def case_c_g12():
    """c(g12版): 標準1〜2回目・fallbackとも g12音声(Primary不一致、Azureも縛られる=SCG NG想定)。
    NG時にattemptが消費され、合計3回(標準2+fallback1)でSTOPPEDになること(SCGで上限を超えない)を確認。"""
    out = os.path.join(SCRATCH, "cg12_out.wav")
    cs, cf = {"n": 0}, {"n": 0}
    p9a_orig, fb_orig = p9a.generate_narration_snippet, n3._generate_a2_japanese_minimal_instruction
    p9a.generate_narration_snippet = fake_p9a_for([G12_WAV], cs)
    n3._generate_a2_japanese_minimal_instruction = fake_minimal_for([G12_WAV], cf)
    flw_orig = n3.c.batch_wiring.make_batch_tts_call_fn
    n3.c.batch_wiring.make_batch_tts_call_fn = lambda *a, **k: None
    try:
        r = n3.generate_a2_japanese_with_reading_safety(G12_TEXT, out, "しばられず")
    finally:
        p9a.generate_narration_snippet, n3._generate_a2_japanese_minimal_instruction = p9a_orig, fb_orig
        n3.c.batch_wiring.make_batch_tts_call_fn = flw_orig
    std_log = r.get("standard_attempts_log") or []
    fb_log = r.get("fallback_attempts_log") or []
    std_scg = [(a.get("scg_info") or {}).get("scg_result") for a in std_log]
    fb_scg = [(a.get("scg_info") or {}).get("scg_result") for a in fb_log]
    ok = (cs["n"] == 2 and cf["n"] == 1 and r.get("status") == "STOPPED" and std_scg == ["NG", "NG"] and fb_scg == ["NG"])
    finish("c_g12", "n3経路: 標準1〜2回目・fallbackとも g12音声(SCG NG想定)。TTSのみ差替",
           "SCG NGでattempt消費(標準2+fallback1=合計3回)->STOPPED、誤PASSなし、Azure 3回",
           {"result": summarize_result(r), "std_tts_calls": cs["n"], "fallback_tts_calls": cf["n"],
            "standard_scg_results": std_scg, "fallback_scg_results": fb_scg},
           "PASS" if ok else "FAIL_OR_NOT_REPRODUCED(観測値をそのまま記録)", {})


def case_c2_fallback_pass():
    """c2: 標準2回はTTS失敗(差替=STOPPED)でattempt消費、fallback=META音声でSCG PASS。
    fallback attemptにもSCGが効くことを実コンポーネントで確認。"""
    out = os.path.join(SCRATCH, "c2_out.wav")
    cs, cf = {"n": 0}, {"n": 0}

    def std_fail(text, language, out_path, **k):
        cs["n"] += 1
        EVENTS.append({"event": "tts_substitute", "call_index": cs["n"], "src": "TTS_FAILURE(substitute STOPPED)"})
        return {"status": "STOPPED", "reason": "substitute TTS failure"}
    p9a_orig, fb_orig = p9a.generate_narration_snippet, n3._generate_a2_japanese_minimal_instruction
    p9a.generate_narration_snippet = std_fail
    n3._generate_a2_japanese_minimal_instruction = fake_minimal_for([META_WAV], cf)
    flw_orig = n3.c.batch_wiring.make_batch_tts_call_fn
    n3.c.batch_wiring.make_batch_tts_call_fn = lambda *a, **k: None
    try:
        r = n3.generate_a2_japanese_with_reading_safety(META_TEXT, out, "出演")
    finally:
        p9a.generate_narration_snippet, n3._generate_a2_japanese_minimal_instruction = p9a_orig, fb_orig
        n3.c.batch_wiring.make_batch_tts_call_fn = flw_orig
    fb_log = r.get("fallback_attempts_log") or []
    fb_scg = [(a.get("scg_info") or {}).get("scg_result") for a in fb_log]
    azure_n = sum(1 for e in EVENTS if e["event"] == "azure_scg_secondary")
    if r.get("status") == "OK" and r.get("fallback_used") and fb_scg == ["PASS"] and cs["n"] == 2 and cf["n"] == 1:
        j = "PASS"
    elif r.get("status") == "OK" and azure_n == 0:
        j = "NOT_REPRODUCED(PrimaryがPASS、SCG発火せず。根拠に数えない)"
    else:
        j = "FAIL_OR_NOT_REPRODUCED(観測値をそのまま記録)"
    finish("c2", "n3 fallback attemptのSCG: 標準2回=TTS失敗(差替)でattempt消費、fallback=META音声",
           "標準2回消費->fallback 1回目でSCG PASS->OK(fallback_used=True)",
           {"result": summarize_result(r), "std_tts_calls": cs["n"], "fallback_tts_calls": cf["n"], "fallback_scg_results": fb_scg,
            "azure_scg_calls": azure_n}, j, {})


def case_d():
    out = os.path.join(SCRATCH, "d_out.wav")
    with wave.open(META_WAV, "rb") as w:
        pcm = w.readframes(w.getnframes())
    calls = {"n": 0}

    def fake_resolve(text, style_prefix, model_name, voice_name, out_path=None, tts_backend="structured_separation",
                     build_tts_prompt=None, make_batch_tts_call_fn=None):
        def call_fn(prompt):
            calls["n"] += 1
            EVENTS.append({"event": "tts_substitute", "call_index": calls["n"], "src": os.path.basename(META_WAV)})
            return pcm
        return call_fn, "SUBSTITUTE_PROMPT"
    orig = flw.resolve_tts_call_and_prompt
    flw.resolve_tts_call_and_prompt = fake_resolve
    try:
        r = voice01.generate_charon_japanese(META_TEXT, out, "出演")
    finally:
        flw.resolve_tts_call_and_prompt = orig
    azure_n = sum(1 for e in EVENTS if e["event"] == "azure_scg_secondary")
    scg_res = (r.get("attempts_log") or [{}])[0].get("scg_info") or {}
    if r.get("status") == "OK" and scg_res.get("scg_result") == "PASS" and calls["n"] == 1:
        judgement = "PASS"
    elif r.get("status") == "OK" and azure_n == 0 and calls["n"] == 1:
        judgement = "NOT_REPRODUCED(PrimaryがPASS、SCG発火せず。根拠に数えない)"
    else:
        judgement = "FAIL_OR_NOT_REPRODUCED(観測値をそのまま記録)"
    finish("d", "voice01.generate_charon_japanese(B系日本語、実)、TTSのみMETA保存wavのPCMに差替",
           "SCG PASSで標準attempt1完了(TTS差替1回)",
           {"result": summarize_result(r), "tts_substitute_calls": calls["n"], "azure_scg_calls": azure_n},
           judgement, {})


def case_e():
    os.environ["JA_SCG_ENABLED"] = "0"
    wav = META_WAV
    primary, err = routing.transcribe(wav, "ja-JP")
    d = ja.evaluate_attempt_ja_with_cascade_detail(META_TEXT, primary, wav, cascade_enabled=True)
    azure_all = [e for e in EVENTS if e["event"].startswith("azure")]
    tcm = d["steps"][0]["classification"] == "TRUE_CONTENT_MISMATCH"
    if len(azure_all) == 0 and tcm and d["scg_result"] == "DISABLED_BY_FLAG" and not d["verified"]:
        judgement = "PASS"
    elif len(azure_all) == 0 and not tcm:
        judgement = "NOT_REPRODUCED(PrimaryがPASS、kill switchが効く状況にならず。根拠に数えない)"
    else:
        judgement = "FAIL"
    finish("e", "JA_SCG_ENABLED=0(kill switch)でMETA音声。Azure呼出0回・従来動作(TCMのまま)",
           "Azure呼出0回、scg_result=DISABLED_BY_FLAG、verified=False(従来のTRUE_CONTENT_MISMATCH)",
           {"primary_transcript": primary, "primary_cls": d["steps"][0]["classification"], "final_status": d["final_status"],
            "verified": d["verified"], "scg_result": d.get("scg_result"), "azure_calls": len(azure_all)},
           judgement, {})


if __name__ == "__main__":
    case = sys.argv[1]
    used = cumulative_cost()
    if used > BUDGET_STOP_JPY:
        print(f"STOP: cumulative {used} JPY > {BUDGET_STOP_JPY}")
        sys.exit(3)
    {"a": case_a, "b": case_b, "c": case_c, "c_g12": case_c_g12, "c2": case_c2_fallback_pass, "d": case_d, "e": case_e}[case]()
