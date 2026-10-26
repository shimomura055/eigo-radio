# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE1-MALE7-TRIAL-01: Y『宅配』本文b(=y_voice_b)をVoice名で生成する男性7Voice比較Trial用生成(Trial専用、未採用)。
`docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/tools/yvp_cross_generate_01.py` の派生: Production関数をimportして同一呼出し(Voice名のみ差)。
差分: (1)Voice名を直接指定(男性限定の許可リスト) (2)計画JSONのbatch単位で実行(level混在可)
(3)起動時にimportした生成関数・設定のsha/関数名を launch_<phase>_batch<N>.json へ記録。run_01は読取のみ。出力は --out 配下のみ。
使い方: py ym7_generate_01.py --plan plan.json --batch N --out <dir> [--budget-jpy 80] [--spec-only]
  take出力: <out>/<level>/body<b>_<Voice>/take<k>/{narration/attempts/*.wav, narration/y_voice_<b>.wav, result.json}。既存result.jsonは再生成しない。"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time

sys.path.insert(0, os.getcwd())
RUN01 = "er121_output/family_y_production_01/redelivery_fee/run_01"
MALE_ALLOWED = {"Algieba", "Schedar", "Fenrir", "Orus", "Puck", "Iapetus", "Sadaltager", "Umbriel", "Achird"}   # 性別=Google公式Voice表(DESIGN_01 §2)で男性確認済みのみ
YEN_PER_COSTLINE_UPPER = 0.8


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_prod():
    from dotenv import load_dotenv
    load_dotenv()
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
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


def build_spec(level: str, body: int, voice: str, P=None) -> dict:
    """API 0。生成に使う設定。Voice以外が全Voiceで同一であることをtestでassertする。"""
    assert voice in MALE_ALLOWED, f"男性許可リスト外: {voice}"
    P = P or load_prod()
    ya, yr, n3, sp = P["ya"], P["yr"], P["n3"], P["sp"]
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
    return {"level": level, "segment": f"y_voice_{body}", "body": body, "voice_name": voice,
            "tts_backend": ya.TTS_BACKEND, "style_profile": yr.STYLE_PROFILE, "style_prefix": style, "style_prefix_sha256": _sha((style or "").encode("utf-8")),
            "text_sha256": _sha(text.encode("utf-8")), "words": len(text.split()), "generator": func,
            "slowdown_percent_a2": (slow.A2_SLOWDOWN_PERCENT if level == "a2" else None),
            "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE", "STANDARD")}


def module_shas(P):
    out = {}
    for k, m in P.items():
        f = getattr(m, "__file__", None)
        if f and os.path.exists(f):
            out[os.path.basename(f)] = _sha(open(f, "rb").read())[:16]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--batch", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-jpy", type=float, default=80.0)
    ap.add_argument("--slice", default="", help="batch内item index範囲 a:b(尾部を別processで前倒しする場合。重複生成を避けるため範囲は前方processの現在位置より先に限る)")
    ap.add_argument("--reverse", action="store_true", help="slice内を逆順に処理。着手済み(narration dirあり)のtakeはskip=forward processとの重複生成を避ける")
    ap.add_argument("--spec-only", action="store_true", help="API 0: 設定JSONだけ表示")
    a = ap.parse_args(argv)
    plan = json.load(open(a.plan, encoding="utf-8"))
    items = [i for i in plan["items"] if i["batch"] == a.batch]
    if a.slice:
        lo, hi = (int(x) for x in a.slice.split(":"))
        items = items[lo:hi]
    if a.reverse:
        items = list(reversed(items))
    P = load_prod()
    ya, xr, n3, nt, rp, ys = P["ya"], P["xr"], P["n3"], P["nt"], P["rp"], P["ys"]
    if a.spec_only:
        for it in items[:6]:
            print(json.dumps({k: (x if k != "style_prefix" else x[:60]) for k, x in build_spec(it["level"], it["body"], it["voice"], P).items()}, ensure_ascii=False))
        return 0
    os.makedirs(a.out, exist_ok=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er005_cost_logger as cl
    import er062_family_z_structure_01 as st
    import er078_secondary_run_scope_01 as srs
    import er103_pnap_runner_hooks_01 as pnap_hooks
    import er109_xz_scope_01 as scope
    tag = f"batch{a.batch}" + (f"_s{a.slice.replace(':', '-')}{'r' if a.reverse else ''}" if a.slice else "")
    cost_log = f"{a.out}/cost_log_{plan['phase']}_{tag}.jsonl"
    json.dump({"started_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "plan": a.plan, "batch": a.batch, "n_items": len(items), "module_sha16": module_shas(P),
               "tts_execution_mode": os.environ["TTS_EXECUTION_MODE"], "backend": ya.TTS_BACKEND},
              open(f"{a.out}/launch_{plan['phase']}_{tag}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    st.check_stop_sentinel("client:ym7", RUN01)
    st.check_stop_sentinel("client:ym7_out", a.out)
    cl.install(cost_log)
    st.install_api_stop_guard()
    for it in items:
        lv, b, voice, k = it["level"], it["body"], it["voice"], it["take"]
        spec = build_spec(lv, b, voice, P)
        seg = f"y_voice_{b}"
        text = body_text(lv, b)
        cdir = f"{a.out}/{lv}/body{b}_{voice}"
        tdir = f"{cdir}/take{k}"
        ndir = f"{tdir}/narration"
        if a.reverse and os.path.isdir(ndir) and not os.path.exists(f"{tdir}/result.json"):
            print(f"[SKIP-INPROGRESS] {lv} body{b} {voice} take{k} 他processが着手済み")
            continue
        os.makedirs(ndir, exist_ok=True)
        json.dump(spec, open(f"{cdir}/settings_{lv}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        _role_style, _base, _fl = ya._style_resolvers(lv, ya.TTS_BACKEND, P["yr"].STYLE_PROFILE)
        out = f"{ndir}/{seg}.wav"
        if os.path.exists(f"{tdir}/result.json"):
            print(f"[SKIP] {lv} body{b} {voice} take{k} 既存")
            continue
        est = sum(1 for _ in open(cost_log, encoding="utf-8")) * YEN_PER_COSTLINE_UPPER if os.path.exists(cost_log) else 0.0
        if est >= a.budget_jpy:
            print(f"[BUDGET_STOP] 概算{est:.1f}円 >= {a.budget_jpy}円。次のtake前に停止")
            return 4
        st.check_stop_sentinel("client:ym7_take", RUN01)
        t0 = time.strftime("%Y-%m-%dT%H:%M:%S")

        def _gen(text=text, out=out, voice=voice, seg=seg, lv=lv):
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
            with cl.logging_context("run_01", f"ym7_{lv}_b{b}_{voice}_take{k}"):
                with cl.segment_context(seg):
                    return pnap_hooks.run_with_alarm_hook("Y", tdir, _gen)

        res = go()
        ok = os.path.exists(out)
        rec = {"level": lv, "body": b, "voice": voice, "take": k, "segment": seg, "wav": out if ok else None,
               "wav_sha256": _sha(open(out, "rb").read()) if ok else None, "status": res.get("status"), "asr_verified": res.get("asr_verified"),
               "asr_judgement_state": (res.get("asr_judgement") or {}).get("state"), "asr_reason_code": (res.get("asr_judgement") or {}).get("reason_code"),
               "post_slowdown_final_classification": res.get("post_slowdown_final_classification"),
               "tts_generations_used": res.get("tts_generations_used"), "duration_seconds": res.get("duration_seconds"),
               "expected_text_sha256": spec["text_sha256"], "started_at": t0, "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "plan_seq": it.get("seq"), "batch": a.batch, "adopted": False, "note": "Trial(男性7Voice比較)。Production未採用・run_01未変更", "raw_result": res}
        json.dump(rec, open(f"{tdir}/result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
        print(json.dumps({x: rec[x] for x in ("level", "body", "voice", "take", "status", "asr_verified", "asr_judgement_state", "tts_generations_used", "duration_seconds", "finished_at")}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
