# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01: Y『宅配』の本文b(=y_voice_b担当本文)をVoice vで生成するクロス生成(Trial専用、未採用)。
Production関数(er121_family_y_audio_01 / er003 n3_tts / news_tail_fix)をimportして、`yfb_voice1_candidates_01.py`(=generate_y_{a2,b1}_segmentsのy_voice `_gen`と同一呼出し)の
本文とVoiceだけを引数化した派生。Voice以外(モデル・Style・ASR/QA・Std=6%減速)はProductionと同一。run_01は読取のみ。出力は --out 配下のみ。
使い方: py yvp_cross_generate_01.py --level a2|b1b --cells b:v[:takes],b:v[:takes],... --out <dir> [--budget-jpy 150] [--spec-only]
  cell の出力: <out>/body<b>_voice<v>/take<k>/{narration/attempts/*.wav, narration/y_voice_<b>.wav, result.json}。既存result.jsonのtakeは再生成しない(skip)。
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time

sys.path.insert(0, os.getcwd())
RUN01 = "er121_output/family_y_production_01/redelivery_fee/run_01"
VOICE_SLOT = {1: "Algieba", 2: "Zephyr", 3: "Schedar"}
YEN_PER_COSTLINE_UPPER = 0.8      # 予算ガード用の上限側概算(実績 17.52円/29行=0.60円/行)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_prod():
    from dotenv import load_dotenv
    load_dotenv()
    os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")
    import er121_family_y_audio_01 as ya
    import er121_family_y_runner_01 as yr
    import er003_v1_n3_01_tts_generate as n3_tts
    import er003_v1_sing01_news_tail_fix as news_tail_fix
    import er020_tts_retry_local_rewrite_01 as retry_primitive
    import er019_family_x_audio_production_runner_01 as xr
    import er019_family_x_style_profile_01 as style_profile_mod
    import er121_family_y_structure_01 as ys
    return dict(ya=ya, yr=yr, n3=n3_tts, nt=news_tail_fix, rp=retry_primitive, xr=xr, sp=style_profile_mod, ys=ys)


def body_text(level: str, body: int) -> str:
    return json.load(open(f"{RUN01}/{level}/parts.json", encoding="utf-8"))["segments"][f"y_voice_{body}"]


def build_spec(level: str, body: int, voice_slot: int, P=None) -> dict:
    """API 0。生成に使う設定(Style文・モデル・速度・関数名)をまとめる。Voice以外が全Voiceで同一であることをtestでassertする。"""
    P = P or load_prod()
    ya, yr, n3, sp = P["ya"], P["yr"], P["n3"], P["sp"]
    seg = f"y_voice_{body}"
    _role_style, _base, _fl = ya._style_resolvers(level, ya.TTS_BACKEND, yr.STYLE_PROFILE)

    def _base_slower(role):
        b = _base(role)
        return None if b is None else f"{b}\n{n3.A2_SLOWER_PACE_INSTRUCTION.strip()}"
    if level == "a2":
        style = sp.resolve_role_style(yr.STYLE_PROFILE, "FULL_STORY", "a2", _base_slower) or n3.A2_ENGLISH_STYLE_PREFIX_SLOWER
        func = "n3_tts.generate_a2_segment_with_slowdown(6% slowdown, post-slowdown ASR recheck, repetition_qa)"
    else:
        style = _role_style("FULL_STORY")
        func = "news_tail_fix.generate_news_narration_wide_margin(repetition_qa, pronunciation_resolver)"
    text = body_text(level, body)
    import er008_a2_postprocess_slowdown_01 as slow
    return {"level": level, "segment": seg, "body": body, "voice_slot": voice_slot, "voice_name": VOICE_SLOT[voice_slot],
            "tts_backend": ya.TTS_BACKEND, "style_profile": yr.STYLE_PROFILE, "style_prefix": style, "style_prefix_sha256": _sha((style or "").encode("utf-8")),
            "text_sha256": _sha(text.encode("utf-8")), "words": len(text.split()), "generator": func,
            "slowdown_percent_a2": (slow.A2_SLOWDOWN_PERCENT if level == "a2" else None),
            "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE", "STANDARD")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", required=True, choices=("a2", "b1b"))
    ap.add_argument("--cells", required=True, help="b:v[:takes],... (b,v in 1..3; takes既定=1)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-jpy", type=float, default=150.0)
    ap.add_argument("--spec-only", action="store_true", help="API 0: 設定JSONだけ表示")
    a = ap.parse_args(argv)
    cells = []
    for c in a.cells.split(","):
        p = [int(x) for x in c.split(":")]
        cells.append((p[0], p[1], p[2] if len(p) > 2 else 1))
    P = load_prod()
    ya, xr, n3, nt, rp, ys = P["ya"], P["xr"], P["n3"], P["nt"], P["rp"], P["ys"]
    lv = a.level
    if a.spec_only:
        for b, v, _ in cells:
            print(json.dumps({k: (x if k != "style_prefix" else x[:60]) for k, x in build_spec(lv, b, v, P).items()}, ensure_ascii=False))
        return 0
    os.makedirs(a.out, exist_ok=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er005_cost_logger as cl
    import er062_family_z_structure_01 as st
    import er078_secondary_run_scope_01 as srs
    import er103_pnap_runner_hooks_01 as pnap_hooks
    import er109_xz_scope_01 as scope
    cost_log = f"{a.out}/cost_log_{lv}.jsonl"
    st.check_stop_sentinel("client:yvp_cross", RUN01)
    st.check_stop_sentinel("client:yvp_cross_out", a.out)
    cl.install(cost_log)
    st.install_api_stop_guard()
    vmap = ya.segment_voice_map()
    for b, v, ntake in cells:
        spec = build_spec(lv, b, v, P)
        assert spec["voice_name"] == vmap[f"y_voice_{v}"], (spec["voice_name"], vmap)
        seg = f"y_voice_{b}"
        text = body_text(lv, b)
        cdir = f"{a.out}/body{b}_voice{v}"
        os.makedirs(cdir, exist_ok=True)
        json.dump(spec, open(f"{cdir}/settings_{lv}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        _role_style, _base, _fl = ya._style_resolvers(lv, ya.TTS_BACKEND, P["yr"].STYLE_PROFILE)
        for k in range(1, ntake + 1):
            tdir = f"{cdir}/take{k}"
            ndir = f"{tdir}/narration"
            os.makedirs(ndir, exist_ok=True)
            out = f"{ndir}/{seg}.wav"
            if os.path.exists(f"{tdir}/result.json"):
                print(f"[SKIP] {lv} body{b} voice{v} take{k} 既存")
                continue
            est = sum(1 for _ in open(cost_log, encoding="utf-8")) * YEN_PER_COSTLINE_UPPER if os.path.exists(cost_log) else 0.0
            if est >= a.budget_jpy:
                print(f"[BUDGET_STOP] 概算{est:.1f}円 >= {a.budget_jpy}円。次のtake前に停止")
                return 4
            st.check_stop_sentinel("client:yvp_cross_take", RUN01)
            t0 = time.strftime("%Y-%m-%dT%H:%M:%S")

            def _gen(text=text, out=out, voice=VOICE_SLOT[v], seg=seg):
                with ya.tts_voice(voice):
                    if lv == "b1b":
                        return nt.generate_news_narration_wide_margin(
                            xr._pnap_supply(text, n3.tts_safe_news_en(text)), out, disfluency_qa=False,
                            enable_connected_speech_equivalence_layer=rp.connected_speech_enabled_for(seg),
                            enable_repetition_qa=True, enable_pronunciation_resolver=True,
                            style_prefix_override=_role_style("FULL_STORY"), tts_backend=ya.TTS_BACKEND)

                    def _base_slower(role):
                        bb = _base(role)
                        return None if bb is None else f"{bb}\n{n3.A2_SLOWER_PACE_INSTRUCTION.strip()}"
                    st_slower = P["sp"].resolve_role_style(P["yr"].STYLE_PROFILE, "FULL_STORY", "a2", _base_slower)
                    return n3.generate_a2_segment_with_slowdown(
                        xr._pnap_supply(text, n3.tts_safe_news_en(text)), out, n3.first_words(text),
                        style_prefix_override=(st_slower or n3.A2_ENGLISH_STYLE_PREFIX_SLOWER), disfluency_qa=False,
                        enable_connected_speech_equivalence_layer=rp.connected_speech_enabled_for(seg),
                        enable_repetition_qa=True, tts_backend=ya.TTS_BACKEND)

            @srs.with_secondary_run
            @scope.family_scope("Y")
            def go():
                with cl.logging_context("run_01", f"yvp_cross_{lv}_b{b}_v{v}_take{k}"):
                    with cl.segment_context(seg):
                        return pnap_hooks.run_with_alarm_hook("Y", tdir, _gen)

            res = go()
            ok = os.path.exists(out)
            rec = {"level": lv, "body": b, "voice_slot": v, "voice": VOICE_SLOT[v], "take": k, "segment": seg, "wav": out if ok else None,
                   "wav_sha256": _sha(open(out, "rb").read()) if ok else None, "status": res.get("status"), "asr_verified": res.get("asr_verified"),
                   "asr_judgement_state": (res.get("asr_judgement") or {}).get("state"), "asr_reason_code": (res.get("asr_judgement") or {}).get("reason_code"),
                   "post_slowdown_final_classification": res.get("post_slowdown_final_classification"),
                   "tts_generations_used": res.get("tts_generations_used"), "duration_seconds": res.get("duration_seconds"),
                   "expected_text_sha256": spec["text_sha256"], "started_at": t0, "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                   "adopted": False, "note": "Trial(クロス生成)。Production未採用・run_01未変更", "raw_result": res}
            json.dump(rec, open(f"{tdir}/result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
            print(json.dumps({x: rec[x] for x in ("level", "body", "voice_slot", "take", "status", "asr_verified", "asr_judgement_state", "tts_generations_used", "duration_seconds", "finished_at")}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
