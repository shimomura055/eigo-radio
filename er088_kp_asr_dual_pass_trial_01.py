# ============================================================
# er088_kp_asr_dual_pass_trial_01.py
# FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01 委任_01 (限定Trial・ASR再実行のみ・TTS 0)
# 既存採用音声 kp4_en.wav(run_byus_01 Std KP4 "take part")に対し、Primary/Secondary/ローカルWhisperを
# 各N回独立実行し、Productionと同一の判定関数(evaluate_attempt_with_cascade_detail, force_secondary=True)で
# 「Primary+Secondary両方PASS」方式の挙動を記録する。Production code・Prompt・閾値は一切変更しない(import呼出のみ)。
# 共有ログへは書かない(cost loggerはTrial専用out_dirへ向ける。HR queue書込を行うwrapper
# evaluate_attempt_with_cascade は使わず _detail を直接呼ぶ)。
# ============================================================
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

OUT = os.environ.get("ER088_OUT", "er088_output/kp_asr_dual_pass_trial_01")  # 委任KP4R1: env上書き(既定=従来値)
SRC_WAV = os.environ.get("ER088_SRC_WAV") or "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/a2/narration/kp4_en.wav"
EXPECTED_SHA = os.environ.get("ER088_EXPECTED_SHA", "675cd6b1aec9865acbdb411b588672d9cc963b936bb4a35bb2d8158cb4172186")
CANON = "take part"
N_TRIALS = int(os.environ.get("ER088_N_TRIALS", "10"))
PARALLEL = 3
JPY_PER_USD = 160.0
OPENAI_IN_PER_M, OPENAI_OUT_PER_M = 1.25, 5.0   # pricing_snapshot.json (gpt-4o-mini-transcribe)
AZURE_USD_PER_HOUR = 1.0                          # pricing_snapshot.json (S0/S1 real-time)
GUARDRAIL_JPY = 30.0

os.makedirs(OUT, exist_ok=True)
import er005_cost_logger as cl  # noqa: E402
cl.install(os.path.join(OUT, "raw_usage_log.jsonl"))   # Trial専用path(共有ログへ書かない)

import er003_v1_repro01_main_generate as gen  # noqa: E402
import er006_asr_provider_routing_01 as routing  # noqa: E402
import er006_secondary_asr_01 as sec  # noqa: E402
import er006_preprod_hardening_01_validation as val  # noqa: E402
import er006_pronunciation_ledger_01 as pronun_ledger  # noqa: E402
import er008_disfluency_qa_18 as dq18  # noqa: E402
import er078_asr_unified_attempt_ctx_01 as attempt_ctx_mod  # noqa: E402

PROMPT = gen.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT
_tl = threading.local()


def _install_capture():
    """cost logger(install済み)のOpenAI ASR patchの外側で、応答(usage/_request_id)をthread-localに保持するだけの観測wrapper。"""
    from openai.resources.audio import transcriptions as tm
    inner = tm.Transcriptions.create

    def wrapped(self, *a, **k):
        t0 = time.time()
        _tl.calls = getattr(_tl, "calls", 0) + 1
        resp = inner(self, *a, **k)
        u = getattr(resp, "usage", None)
        _tl.last = {"request_id": getattr(resp, "_request_id", None), "text": getattr(resp, "text", None),
                    "input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None),
                    "elapsed_s": round(time.time() - t0, 3), "sent_prompt": k.get("prompt"), "language": k.get("language"),
                    "model": k.get("model")}
        return resp
    tm.Transcriptions.create = wrapped


def _wav_seconds(p):
    import wave
    with wave.open(p, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def azure_est_jpy(seconds):
    return math.ceil(seconds) * AZURE_USD_PER_HOUR / 3600.0 * JPY_PER_USD


def openai_jpy(i, o):
    return ((i or 0) * OPENAI_IN_PER_M + (o or 0) * OPENAI_OUT_PER_M) / 1e6 * JPY_PER_USD


def run_trial(i, wav, ledger_phrases):
    rec = {"trial": i, "started_at": datetime.now(timezone.utc).isoformat()}
    t_all = time.time()
    _tl.calls = 0
    _tl.last = None
    t = time.time()
    asr_text, err = routing.transcribe(wav, language="en-US", prompt=PROMPT)   # Production KP Primary呼出と同一
    rec["primary_call"] = {"text": asr_text, "error": err, "wall_s": round(time.time() - t, 3),
                           "openai_calls_in_thread": _tl.calls, "response": getattr(_tl, "last", None)}
    detail = sec.evaluate_attempt_with_cascade_detail(
        CANON, asr_text, [], wav, language="en-US", ledger_phrases=ledger_phrases,
        cascade_enabled=sec.FEATURE_FLAG_SECONDARY_ASR_ENABLED, force_secondary=True, enable_non_latin_cascade=True,
        enable_connected_speech_equivalence_layer=False, segment_id=None,
        attempt_ctx=attempt_ctx_mod.build_attempt_ctx(1, 2, slot_offset=0, total_slots=4, max_len=len(CANON) + 10))
    audit = detail.get("asr_judgement") or {}
    p, s = audit.get("primary") or {}, audit.get("secondary") or {}
    cls = detail["classification"]
    rec["judge"] = {
        "dual_verified_production_force_secondary": bool(detail["verified"]), "state": audit.get("state"),
        "reason_code": audit.get("reason_code"), "final_status": detail.get("final_status"),
        "primary_passed": p.get("passed"), "primary_label": p.get("label"), "primary_text": p.get("text"),
        "primary_warning_labels": p.get("warning_labels"),
        "secondary_called": s.get("called"), "secondary_cached": s.get("cached"), "secondary_text": s.get("text"),
        "secondary_label": s.get("label"), "secondary_accepted": s.get("accepted"), "secondary_error": s.get("error"),
        "azure_real_calls": (audit.get("adapter") or {}).get("azure_real_calls"),
        "cache": (audit.get("adapter") or {}).get("cache"), "cost": audit.get("cost"), "timing": audit.get("timing"),
        "classification_reason": getattr(cls, "reason", None), "steps": detail.get("steps"),
        "human_review_required": detail.get("human_review_required"), "audit_record": audit,
    }
    # Primary転写の単独再分類(参考。Production判定は上のjudgeが正)
    pc = val.classify_asr_match(CANON, asr_text) if asr_text is not None else None
    rec["primary_val_classification"] = {"label": getattr(pc, "classification", None),
                                         "should_pass": getattr(pc, "should_pass", None), "reason": getattr(pc, "reason", None)}
    # judgeがSecondaryを呼ばなかった場合(Primary保護差NG等)のみ、Secondary独立測定のため補足で1回呼ぶ
    rec["secondary_supplement"] = None
    if not s.get("called") and not s.get("cached"):
        t = time.time()
        txt, e = sec.get_full_text_via_azure_stt_with_phrase_list(wav, language="en-US", phrases=ledger_phrases)
        sc = val.classify_asr_match(CANON, txt) if txt is not None else None
        rec["secondary_supplement"] = {"text": txt, "error": e, "wall_s": round(time.time() - t, 3),
                                       "label": getattr(sc, "classification", None), "should_pass": getattr(sc, "should_pass", None)}
    rec["dual_ok_by_definition"] = bool(p.get("passed")) and bool(s.get("accepted"))
    rec["trial_wall_s"] = round(time.time() - t_all, 3)
    resp = rec["primary_call"]["response"] or {}
    secs = _wav_seconds(wav)
    az_ran = bool(s.get("called") or rec["secondary_supplement"])
    rec["cost_jpy"] = {"primary_openai": round(openai_jpy(resp.get("input_tokens"), resp.get("output_tokens")), 5),
                       "azure_est_ceil_seconds": round(azure_est_jpy(secs), 5) if az_ran else 0.0,
                       "azure_exact_seconds": round(secs / 3600.0 * AZURE_USD_PER_HOUR * JPY_PER_USD, 5) if az_ran else 0.0}
    return rec


def run_whisper(i, wav):
    t = time.time()
    words = dq18.transcribe_verbatim(wav, language="en", model_size="small")
    text = " ".join(w["text"] for w in words).strip()
    wall = round(time.time() - t, 3)
    cls = val.classify_asr_match(CANON, text) if text else None
    alt = sec._step_alternate_pass(cls) if cls is not None and not cls.should_pass else None
    return {"trial": i, "text": text, "words": words, "wall_s": wall,
            "label": getattr(cls, "classification", None), "should_pass": getattr(cls, "should_pass", None),
            "alt_pass_label": alt, "pass_equivalent": bool((cls and cls.should_pass) or alt),
            "reason": getattr(cls, "reason", None),
            "config": "faster_whisper small cpu int8 language=en word_timestamps=True condition_on_previous_text=False vad_filter=False (dq18.transcribe_verbatim default)"}


def main():
    t_start = time.time()
    assert sec._RUN_CACHE is None and sec._RUN_STATE is None, "begin_secondary_run()が呼ばれている(cacheが有効)"
    wav = os.path.join(OUT, "kp4_en.wav")
    shutil.copyfile(SRC_WAV, wav)
    assert _sha(SRC_WAV) == EXPECTED_SHA and _sha(wav) == EXPECTED_SHA
    ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(CANON, min_confidence="low")]  # Production同一呼出
    setup = {"canonical": CANON, "wav_sha256": EXPECTED_SHA, "wav_seconds": _wav_seconds(wav),
             "ledger_phrases_azure_phrase_list": ledger_phrases, "phrase_list_nonempty": bool(ledger_phrases),
             "setWeight_executed(only if phrases non-empty, er006_secondary_asr_01.py:get_full_text_via_azure_stt_with_phrase_list)": bool(ledger_phrases),
             "azure_phrase_list_weight_const": sec.AZURE_PHRASE_LIST_WEIGHT, "primary_prompt": PROMPT,
             "primary_model": routing.ASR_ROUTING["en"], "run_cache_active": sec._RUN_CACHE is not None,
             "cascade_enabled": sec.FEATURE_FLAG_SECONDARY_ASR_ENABLED, "parallel": PARALLEL, "n_trials": N_TRIALS,
             "started_at": datetime.now(timezone.utc).isoformat()}
    json.dump(setup, open(os.path.join(OUT, "setup.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    _install_capture()
    results = []
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        futs = [ex.submit(run_trial, i, wav, ledger_phrases) for i in range(1, N_TRIALS + 1)]
        for f in futs:
            results.append(f.result())
    spent = sum(x["cost_jpy"]["primary_openai"] + x["cost_jpy"]["azure_est_ceil_seconds"] for x in results)
    api_wall = round(time.time() - t_start, 3)
    print("api phase done wall", api_wall, "est_jpy", round(spent, 4))
    wres = []
    tw = time.time()
    for i in range(1, N_TRIALS + 1):   # Whisperはローカル直列
        wres.append(run_whisper(i, wav))
    whisper_wall = round(time.time() - tw, 3)
    with open(os.path.join(OUT, "results.jsonl"), "w", encoding="utf-8") as f:
        for r, w in zip(results, wres):
            f.write(json.dumps({"trial": r["trial"], "primary_and_secondary": r, "whisper": w}, ensure_ascii=False, default=str) + "\n")
    json.dump({"api_phase_wall_s": api_wall, "whisper_phase_wall_s": whisper_wall, "total_wall_s": round(time.time() - t_start, 3),
               "est_jpy_api": round(spent, 5), "finished_at": datetime.now(timezone.utc).isoformat()},
              open(os.path.join(OUT, "timing.json"), "w"), indent=2)
    print("done", api_wall, whisper_wall)


if __name__ == "__main__":
    main()
