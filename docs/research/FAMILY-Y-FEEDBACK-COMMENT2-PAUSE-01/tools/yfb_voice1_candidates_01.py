# -*- coding: utf-8 -*-
"""FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_03 B: E-1 Voice 1の代替候補を、Production生成関数と同一設定で別dirへ生成する(採用はしない)。
Production関数・run_01の成果物(narration/audit/lock)は変更しない。出力は <run>/<level>/hr_adopt_prep/voice1_candidates/take<k>/ のみ。
生成設定は er121_family_y_audio_01.generate_y_{b1,a2}_segments の y_voice_1 `_gen` と同一(voice/style/ASR判定/Std=『ゆっくり』instruction+6%減速+減速後ASR再検証)。
候補は run_01 の review_lock/tts_generation_results に載らず、人間(ユーザー)の試聴選択後に既存 er121_e1_hr_adopt_r0_01 系の手続きで採用する(本scriptは採用しない)。"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time

sys.path.insert(0, os.getcwd())
SEG = "y_voice_1"


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--level", required=True, choices=("a2", "b1b"))
    ap.add_argument("--takes", type=int, default=3)
    a = ap.parse_args(argv)
    from dotenv import load_dotenv
    load_dotenv()
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er005_cost_logger as cl
    import er121_family_y_audio_01 as ya
    import er121_family_y_runner_01 as yr
    import er062_family_z_structure_01 as st
    import er003_v1_n3_01_tts_generate as n3_tts
    import er003_v1_sing01_news_tail_fix as news_tail_fix
    import er020_tts_retry_local_rewrite_01 as retry_primitive
    import er019_family_x_audio_production_runner_01 as xr
    import er019_family_x_style_profile_01 as style_profile_mod
    import er078_secondary_run_scope_01 as srs
    import er103_pnap_runner_hooks_01 as pnap_hooks
    import er109_xz_scope_01 as scope

    run, lv = a.run.replace("\\", "/"), a.level
    base = f"{run}/{lv}/hr_adopt_prep/voice1_candidates"
    os.makedirs(base, exist_ok=True)
    cost_log = f"{base}/cost_log_{lv}.jsonl"
    st.check_stop_sentinel("client:yfb_voice1_candidates", run)
    cl.install(cost_log)
    st.install_api_stop_guard()
    parts = json.load(open(f"{run}/{lv}/parts.json", encoding="utf-8"))
    text = parts["segments"][SEG]
    voice = ya.segment_voice_map()[SEG]
    _role_style, _base, _fl = ya._style_resolvers(lv, ya.TTS_BACKEND, yr.STYLE_PROFILE)

    def _base_slower(role):
        b = _base(role)
        return None if b is None else f"{b}\n{n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()}"

    def _role_style_slower(role):
        return style_profile_mod.resolve_role_style(yr.STYLE_PROFILE, role, "a2", _base_slower)

    for k in range(1, a.takes + 1):
        tdir = f"{base}/take{k}"
        ndir = f"{tdir}/narration"
        os.makedirs(ndir, exist_ok=True)
        out = f"{ndir}/{SEG}.wav"
        if os.path.exists(f"{tdir}/result.json"):
            print(f"[SKIP] take{k} 既存"); continue
        st.check_stop_sentinel("client:yfb_voice1_candidates_take", run)
        t0 = time.strftime("%Y-%m-%dT%H:%M:%S")

        def _gen():
            with ya.tts_voice(voice):
                if lv == "b1b":
                    return news_tail_fix.generate_news_narration_wide_margin(
                        xr._pnap_supply(text, n3_tts.tts_safe_news_en(text)), out, disfluency_qa=False,
                        enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(SEG),
                        enable_repetition_qa=True, enable_pronunciation_resolver=True,
                        style_prefix_override=_role_style("FULL_STORY"), tts_backend=ya.TTS_BACKEND)
                tts_input = xr._pnap_supply(text, n3_tts.tts_safe_news_en(text))
                return n3_tts.generate_a2_segment_with_slowdown(
                    tts_input, out, n3_tts.first_words(text),
                    style_prefix_override=(_role_style_slower("FULL_STORY") or n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER), disfluency_qa=False,
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(SEG),
                    enable_repetition_qa=True, tts_backend=ya.TTS_BACKEND)

        @srs.with_secondary_run
        @scope.family_scope("Y")
        def go():
            with cl.logging_context("run_01", f"voice1_candidate_{lv}_take{k}"):
                with cl.segment_context(SEG):
                    return pnap_hooks.run_with_alarm_hook("Y", tdir, _gen)

        res = go()
        ok = os.path.exists(out)
        rec = {"level": lv, "take": k, "segment": SEG, "voice": voice, "wav": out if ok else None, "wav_sha256": _sha(out) if ok else None,
               "status": res.get("status"), "asr_verified": res.get("asr_verified"),
               "asr_judgement_state": (res.get("asr_judgement") or {}).get("state"), "asr_reason_code": (res.get("asr_judgement") or {}).get("reason_code"),
               "post_slowdown_classification": res.get("post_slowdown_classification"), "post_slowdown_final_classification": res.get("post_slowdown_final_classification"),
               "tts_generations_used": res.get("tts_generations_used"), "duration_seconds": res.get("duration_seconds"),
               "expected_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "started_at": t0, "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "adopted": False, "note": "候補・未採用(ユーザー試聴選択前)。run_01のnarration/audit/review_lockは未変更",
               "raw_result": res}
        json.dump(rec, open(f"{tdir}/result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
        print(json.dumps({k2: rec[k2] for k2 in ("level", "take", "status", "asr_verified", "asr_judgement_state", "tts_generations_used", "duration_seconds", "wav")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
