# -*- coding: utf-8 -*-
"""FAMILY-Y-PRODUCTION-LAUNCH-01 委任_08: a2 y_voice_1 attempt5(R0本文)の減速後ASR再検証を、正式経路と同じ関数
(er003_v1_n3_01_tts_generate.apply_a2_slowdown_postprocess=6%減速+統一judge)で1回実行し、別ファイルへ記録する(有料: ASR 1+必要ならSecondary)。
run_01の判定ファイルは改変しない。wavは作業dir(commitしない)。"""
from __future__ import annotations
import hashlib, json, os, shutil, sys, time

RUN = "er121_output/family_y_production_01/redelivery_fee/run_01"
PREP = f"{RUN}/a2/hr_adopt_prep"
OUT_JSON = f"{PREP}/y_voice_1_slowed_asr_recheck.json"
SEG, ATTEMPT_ROUTE = "y_voice_1", "custom53fd514d"


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main() -> int:
    import er005_cost_logger as cl
    import er003_v1_n3_01_tts_generate as n3
    import er019_family_x_audio_production_runner_01 as xr
    import er109_xz_scope_01 as scope
    import er078_secondary_run_scope_01 as srs
    work = f"{PREP}/slow_recheck_work"
    os.makedirs(work, exist_ok=True)
    cl.init_logger(f"{PREP}/y_voice_1_slowed_asr_recheck_cost_log.jsonl")
    src = f"{RUN}/a2/narration/attempts/{SEG}_attempt5_{ATTEMPT_ROUTE}.wav"
    canon = json.load(open(f"{RUN}/a2/audit/tts_generation_results.json", encoding="utf-8"))["segments"][SEG]["canonical_text"]
    src_sha = _sha(src)
    shutil.copyfile(src, f"{work}/{SEG}.wav")
    tts_input = xr._pnap_supply(canon, n3.tts_safe_news_en(canon))
    result = {"status": "OK"}

    @srs.with_secondary_run
    @scope.family_scope("Y")
    def go():
        with cl.logging_context("run_01", "y_voice_1_slowed_asr_recheck"):
            return n3.apply_a2_slowdown_postprocess(SEG, work, tts_input, result, is_last_slot=True, log_human_review=False)
    r = go()
    slowed = f"{work}/{SEG}.wav"
    jd = r.get("asr_judgement") or r.get("asr_judgement_post_slowdown_ng")
    rec = {"segment": SEG, "attempt": 5, "source_attempt_wav": src, "source_attempt_sha256": src_sha,
           "slowed_wav_sha256": _sha(slowed), "function": "er003_v1_n3_01_tts_generate.apply_a2_slowdown_postprocess(slowdown_pct=None, is_last_slot=True, log_human_review=False)",
           "expected_text_canonical_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(), "tts_input_text": tts_input,
           "status": r.get("status"), "asr_verified": r.get("asr_verified"), "post_slowdown_classification": r.get("post_slowdown_classification"),
           "post_slowdown_final_classification": r.get("post_slowdown_final_classification"), "post_slowdown_asr_text": r.get("post_slowdown_asr_text"),
           "post_slowdown_cascade_accepted": r.get("post_slowdown_cascade_accepted"), "post_slowdown_cascade": r.get("post_slowdown_cascade"),
           "slowdown_info": r.get("slowdown_info"), "reason": r.get("reason"), "asr_judgement": jd,
           "asr_model_id": __import__("er006_asr_provider_routing_01").require_asr_route("en-US").get("model"),
           "cost_estimate_jpy": 0.4, "cost_note": "cl.install未実行のためcost_log未記録。gpt-4o-mini-transcribe 46.5秒1呼出の推定(Secondary未呼出=Azure 0)。過去実測0.531円/clip(同系)を上限目安",
           "recheck_pass": bool(r.get("status") == "OK" and r.get("asr_verified") is True),
           "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    json.dump(rec, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    print(json.dumps({k: rec[k] for k in ("status", "asr_verified", "post_slowdown_classification", "post_slowdown_final_classification", "recheck_pass", "slowed_wav_sha256")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    sys.exit(main())
