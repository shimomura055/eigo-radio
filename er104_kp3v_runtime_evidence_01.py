# ============================================================
# er104_kp3v_runtime_evidence_01.py
# KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_02: KP英語phrase「3-ASR多数決」のFamily X/Z正式経路 runtime evidence 取得driver。
# 各サブコマンドは「Production関数をそのまま呼ぶ」薄いdriverで、判定・retry・fallbackを変えない。監督ループ/自動再試行は持たない
# (1コマンド=1回実行。失敗時は再起動せず報告)。実行前に tools/stop_scope_check_01.py --managed-id KP-THREE-ASR-MAJORITY-PRODUCTION-01 --run-dir <run> を別途実行すること。
# 全API呼出(Primary=OpenAI / Secondary=Azure / TTS / Whisper)を passthrough spy で記録する(判定には影響しない)。
#   x          : Family X Production runner(--stage tts --level b1b --style-profile 記録=fx_20261017[K2])を専用out_dir・専用Storeで実行。
#                only_segments=kp1_english(think up: 旧Store entry=P PASS/S NG)・kp2_english(blurt: P NG/S PASS)=Storeの保存転写+ローカルWhisperのみで再利用判定、
#                kp3_english(bring in: Store無し)=新規生成経路。Primary/Azure/TTSの再呼出は新規kp3のみ。
#   x_rerun    : 同一out_dirの前回results再利用点(runner _generate_or_reuse_kp)=API 0を確認。
#   z_s1       : Family Z Production関数 run_tts_stage。dual導入前の実Z KP entry(er026 Melos run、証跡なし)をそのまま専用run_dirへ置き、
#                再利用点6(generate_or_reuse_z)のS1経路(Azure 1回+必要ならWhisper)を通す。人工entry・HR Lock迂回なし。
#   z_new      : Family Z Production関数 run_tts_stage で新規KP N本(24KP統計と同じ語句)を正式生成経路で生成。
#   z_rerun    : z_s1の同一run_dirを再実行=保存証跡での再利用(API 0)を確認。
#   summarize  : 上記結果を集約してJSON化(API 0)。
# ============================================================
from __future__ import annotations

import json
import os
import shutil
import sys
import time

OUT = "er104_output/kp3v_runtime_evidence_01"
SRC_X = "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01"
SLUG, RUN = "manga_ai_chat_byus", "run_byus_01"
PROD_STORE = "er006_output/master_audio_store_01"
SRC_Z = "er026_output/family_z_production_e2e_01/melos/run_kgcpw_z_e5_b1b_01"
CALLS: list = []


def _spy_install(tag: str):
    """Primary/Azure/Whisper/TTS呼出をpassthroughでjsonlに記録する(判定・戻り値は不変)。"""
    import er003_v1_repro01_main_generate as r1
    import er006_asr_provider_routing_01 as routing
    import er006_secondary_asr_01 as sec
    import er104_kp_three_asr_vote_01 as kp3v
    path = f"{OUT}/{tag}_api_calls.jsonl"
    os.makedirs(OUT, exist_ok=True)

    def wrap(obj, name, provider):
        orig = getattr(obj, name)

        def _w(*a, **k):
            t = time.time()
            try:
                return orig(*a, **k)
            finally:
                rec = {"t": time.strftime("%H:%M:%S"), "provider": provider, "ms": int((time.time() - t) * 1000),
                       "arg0": (str(a[0])[:100] if a else None)}
                CALLS.append(rec)
                with open(path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        setattr(obj, name, _w)
    wrap(routing, "transcribe", "primary_openai")
    wrap(sec, "get_full_text_via_azure_stt_with_phrase_list", "secondary_azure")
    wrap(kp3v, "whisper_transcribe", "whisper_local_small")
    wrap(r1.p9a, "generate_narration_snippet", "tts_gemini")
    return path


def _isolate_side_effects(out_dir: str):
    """HR queue / attempt history を専用out_dirへ退避(本番queueへ書かない)。"""
    import er006_secondary_asr_01 as sec
    import er011_human_review_lock_01 as review_lock
    sec.HUMAN_REVIEW_LOG_PATH = f"{out_dir}/_hr_queue_en.jsonl"
    review_lock.ATTEMPT_HISTORY_PATH = f"{out_dir}/_attempt_history.jsonl"


def _store_patch(store_dir: str):
    import er006_master_audio_store_01 as store
    store.STORE_DIR = store_dir
    store.AUDIO_DIR = f"{store_dir}/audio"
    store.MANIFEST_PATH = f"{store_dir}/manifest.json"
    store.TELEMETRY_PATH = f"{store_dir}/reuse_telemetry.jsonl"
    return store


def _seed_store(store_dir: str, master_ids: list):
    os.makedirs(f"{store_dir}/audio", exist_ok=True)
    prod = json.load(open(f"{PROD_STORE}/manifest.json", encoding="utf-8"))
    mf = {}
    for mid in master_ids:
        e = json.loads(json.dumps(prod[mid]))
        dst = f"{store_dir}/audio/{mid}.wav"
        shutil.copyfile(prod[mid]["audio_path"], dst)
        e["audio_path"] = dst
        mf[mid] = e
    json.dump(mf, open(f"{store_dir}/manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return mf


def _seed_x_out_dir(out_dir: str, level: str):
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    for f in ("style_profile.json", "scaffold_article_sha256.json", "rf_tts_guard.json"):
        if os.path.exists(f"{SRC_X}/audit/{f}"):
            shutil.copyfile(f"{SRC_X}/audit/{f}", f"{out_dir}/audit/{f}")
    lv = f"{out_dir}/{level}"
    os.makedirs(f"{lv}/audit", exist_ok=True)
    for f in ("parts.json", f"{'b1_support_texts' if level == 'b1b' else 'a2_support_texts'}.json"):
        shutil.copyfile(f"{SRC_X}/{level}/{f}", f"{lv}/{f}")
    shutil.copytree(f"{SRC_X}/{level}/key_phrases", f"{lv}/key_phrases", dirs_exist_ok=True)
    src_res = json.load(open(f"{SRC_X}/{level}/audit/tts_generation_results.json", encoding="utf-8"))
    seed = {k: src_res[k] for k in ("style_version", "key_phrase_explanations_text") if k in src_res}
    json.dump(seed, open(f"{lv}/audit/tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _run_x(out_dir: str, level: str, only: str, store_dir: str, budget: str = "5"):
    import er019_family_x_audio_production_runner_01 as x
    _store_patch(store_dir)
    _isolate_side_effects(out_dir)
    sys.argv = ["er019_family_x_audio_production_runner_01.py", "--slug", SLUG, "--run", RUN, "--level", level, "--stage", "tts",
                "--out-dir", out_dir, "--budget-jpy", budget, "--only-segments", only]
    print("[driver] argv=", sys.argv)
    x.main()


def cmd_x():
    out_dir = f"{OUT}/x_k2"
    store_dir = f"{OUT}/x_k2_store"
    assert not os.path.exists(out_dir), "専用out_dirが既に存在します(再実行は禁止: 別名を使わず報告してください)"
    _seed_x_out_dir(out_dir, "b1b")
    mf = _seed_store(store_dir, ["55cd6f202c8ff584b563b41e", "0c527a56ad772429e5d2ffa8"])   # think up(b1b kp1) / blurt(b1b kp2)
    json.dump(mf, open(f"{OUT}/x_k2_store_manifest_BEFORE.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    _spy_install("x")
    import er104_kp_vote_reuse_01 as kv
    kv.reset_preflight()
    _run_x(out_dir, "b1b", "kp1_english,kp2_english,kp3_english", store_dir)
    shutil.copyfile(f"{store_dir}/manifest.json", f"{OUT}/x_k2_store_manifest_AFTER.json")
    json.dump(kv.preflight_once(), open(f"{OUT}/x_whisper_preflight.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def cmd_x_rerun():
    out_dir = f"{OUT}/x_k2"
    _spy_install("x_rerun")
    _run_x(out_dir, "b1b", "kp1_english,kp2_english,kp3_english", f"{OUT}/x_k2_store")


def _z_cached_kps(level: str):
    d = json.load(open(f"{SRC_Z}/{level}/audit/tts_generation_results.json", encoding="utf-8"))
    rows = []
    for rank, subs in sorted((d.get("key_phrases") or {}).items(), key=lambda kv: int(kv[0])):
        e = (subs or {}).get("english")
        if isinstance(e, dict) and e.get("status") == "OK":
            rows.append((int(rank), e))
    return d, rows


def cmd_z_s1():
    import er005_cost_logger as cl
    import er063_family_z_audio_01 as z
    run_dir = f"{OUT}/z_s1"
    assert not os.path.exists(run_dir)
    os.makedirs(run_dir, exist_ok=True)
    _store_patch(f"{OUT}/z_s1_store")
    _isolate_side_effects(run_dir)
    _spy_install("z_s1")
    import er104_kp_vote_reuse_01 as kv
    kv.reset_preflight()
    cl.install(f"{run_dir}/raw_usage_log.jsonl")
    results = {}
    for level in ("a2", "b1b"):
        level_dir = f"{run_dir}/{level}"
        os.makedirs(f"{level_dir}/audit", exist_ok=True)
        z.assert_run_style_record(level_dir, level, write=True)         # NEW_RUN: 現行Productionの期待recordを書く(entry自体は実物のまま)
        d, rows = _z_cached_kps(level)
        narr = z.narration_dir_for(run_dir, level)
        os.makedirs(narr, exist_ok=True)
        plan, keep = [], {"key_phrases": {}}
        for rank, e in rows:
            src_wav = e["path"]
            spec = z.ClipSpec(f"kp{rank}_en", level, "kp_en", e["canonical_text"], voice="Aoede", role_key="KP_EN", rank=rank, language="en")
            shutil.copyfile(src_wav, f"{narr}/{spec.wav_name()}")
            plan.append(spec)
            keep["key_phrases"].setdefault(str(rank), {})["english"] = e
        keep.update({"segments": {}, "tts_backend": d.get("tts_backend"), "style_version": d.get("style_version"), "level": level})
        json.dump(keep, open(f"{level_dir}/audit/tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        shutil.copyfile(f"{level_dir}/audit/tts_generation_results.json", f"{OUT}/z_s1_seed_results_{level}.json")
        with cl.logging_context("kp3v_z_s1", "tts"):
            results[level] = z.run_tts_stage(run_dir, level, plan)
        print(json.dumps({k: results[level].get(k) for k in ("status", "technical_stop", "summary") if k in results[level]}, ensure_ascii=False)[:600])
    json.dump({k: v for k, v in results.items()}, open(f"{OUT}/z_s1_run_returns.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)


def cmd_z_rerun():
    import er005_cost_logger as cl
    import er063_family_z_audio_01 as z
    run_dir = f"{OUT}/z_s1"
    _store_patch(f"{OUT}/z_s1_store")
    _isolate_side_effects(run_dir)
    _spy_install("z_rerun")
    cl.install(f"{run_dir}/raw_usage_log_rerun.jsonl")
    for level in ("a2", "b1b"):
        d = json.load(open(f"{OUT}/z_s1_seed_results_{level}.json", encoding="utf-8"))
        plan = [z.ClipSpec(f"kp{rank}_en", level, "kp_en", subs["english"]["canonical_text"], voice="Aoede", role_key="KP_EN", rank=int(rank), language="en")
                for rank, subs in sorted(d["key_phrases"].items(), key=lambda kv: int(kv[0]))]
        with cl.logging_context("kp3v_z_rerun", "tts"):
            z.run_tts_stage(run_dir, level, plan)


def cmd_z_new(n: int = 8):
    import er005_cost_logger as cl
    import er063_family_z_audio_01 as z
    run_dir = f"{OUT}/z_new"
    assert not os.path.exists(run_dir)
    os.makedirs(run_dir, exist_ok=True)
    _store_patch(f"{OUT}/z_new_store")
    _isolate_side_effects(run_dir)
    _spy_install("z_new")
    import er104_kp_vote_reuse_01 as kv
    kv.reset_preflight()
    rows = json.load(open("er096_output/kp_dual_prod_01/stats/stats_rows.json", encoding="utf-8"))
    phrases = [r["safe"] for r in rows][:n]
    plan = [z.ClipSpec(f"kp{i + 1}_en", "b1b", "kp_en", ph, voice="Aoede", role_key="KP_EN", rank=i + 1, language="en") for i, ph in enumerate(phrases)]
    cl.install(f"{run_dir}/raw_usage_log.jsonl")
    with cl.logging_context("kp3v_z_new", "tts"):
        r = z.run_tts_stage(run_dir, "b1b", plan)
    json.dump(r, open(f"{OUT}/z_new_run_return.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    print(json.dumps({k: r.get(k) for k in ("status", "technical_stop")}, ensure_ascii=False))


COMMANDS = {"x": cmd_x, "x_rerun": cmd_x_rerun, "z_s1": cmd_z_s1, "z_rerun": cmd_z_rerun, "z_new": cmd_z_new}

if __name__ == "__main__":
    sys.path.insert(0, ".")
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("usage: er104_kp3v_runtime_evidence_01.py <" + "|".join(COMMANDS) + ">")
        sys.exit(2)
    COMMANDS[sys.argv[1]]()
