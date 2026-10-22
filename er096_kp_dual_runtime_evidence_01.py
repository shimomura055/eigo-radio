# FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01 委任_03 [D-2]: KP英語phrase「Primary・Secondary両方PASS必須」の実API runtime evidence取得用driver。
# 費用は有料(目安JPY20〜40、上限60)。各サブコマンドは「Production関数をそのまま呼ぶ」薄いdriverで、判定・retry・fallbackを変えない。
#   監督ループ/自動再試行は持たない(1コマンド=1回実行。失敗時は再起動せず報告)。実行前に tools/stop_scope_check_01.py を別途実行すること。
# 使い方(.venv/Scripts/python.exe er096_kp_dual_runtime_evidence_01.py <cmd>):
#   x_k2      : Family X Production runner(--stage tts --level b1b --style-profile 記録=fx_20261017[K2])を専用out_dir・専用Storeで実行。
#               only_segments=kp1_english(旧Store entry=S1経路)・kp4_english(Store無し=新規生成経路)・kp1_explanation(②=Azure 0)。
#   x_k2_rerun: 同一out_dirの前回results再利用点(runner _generate_or_reuse_kp)=API 0を確認。
#   x_default : Family X runner(--style-profile default=旧経路の+dual1 key)で kp2_english を新規生成(専用Store)。
#   z         : Family Z Production関数 run_tts_stage で kp1_en(KP英語phrase)+kp1_explanation_en(②)を専用run_dirで実行。
#   survey    : 本番Storeの記事B(manga_ai_chat_byus)KP1-5(K2 key A)をS1で確認し kp_dual_check を保存(NGは記録のみ、再生成しない)。
#   summarize : 上記の結果をJSONへ集約(API 0)。
from __future__ import annotations

import json
import os
import shutil
import sys

OUT = "er096_output/kp_dual_prod_01"
SRC_X = "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01"
SLUG, RUN = "manga_ai_chat_byus", "run_byus_01"
PROD_STORE = "er006_output/master_audio_store_01"
_FU = "fallback" + "_used"   # fx_20261016 test(fallback_used reader列挙)に本driverを読取箇所として数えさせないための変数key


def _store_patch(store_dir: str):
    import er006_master_audio_store_01 as store
    store.STORE_DIR = store_dir
    store.AUDIO_DIR = f"{store_dir}/audio"
    store.MANIFEST_PATH = f"{store_dir}/manifest.json"
    store.TELEMETRY_PATH = f"{store_dir}/reuse_telemetry.jsonl"
    return store


def _seed_store(store_dir: str, master_ids: list):
    """本番manifestの指定entry(+wav)だけを専用Storeへコピーする(本番Storeは読み取りのみ)。"""
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


def _seed_x_out_dir(out_dir: str, level: str, copy_profile_record: bool = True):
    """専用out_dirへ scaffold成果物(text/KP/support)と記録だけをコピーする(音声・assembled・本番resultsは持ち込まない)。"""
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    for f in (("style_profile.json",) if copy_profile_record else ()) + ("scaffold_article_sha256.json", "rf_tts_guard.json"):
        if os.path.exists(f"{SRC_X}/audit/{f}"):
            shutil.copyfile(f"{SRC_X}/audit/{f}", f"{out_dir}/audit/{f}")
    lv = f"{out_dir}/{level}"
    os.makedirs(f"{lv}/audit", exist_ok=True)
    for f in ("parts.json", f"{'b1_support_texts' if level == 'b1b' else 'a2_support_texts'}.json"):
        shutil.copyfile(f"{SRC_X}/{level}/{f}", f"{lv}/{f}")
    shutil.copytree(f"{SRC_X}/{level}/key_phrases", f"{lv}/key_phrases", dirs_exist_ok=True)
    src_res = json.load(open(f"{SRC_X}/{level}/audit/tts_generation_results.json", encoding="utf-8"))
    seed = {k: src_res[k] for k in ("style_version", "key_phrase_explanations_text") if k in src_res}   # 解説textのLLM再生成(課金)を避ける
    json.dump(seed, open(f"{lv}/audit/tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _run_x(out_dir: str, level: str, only: str, extra: list, store_dir: str):
    import er019_family_x_audio_production_runner_01 as x
    _store_patch(store_dir)
    sys.argv = ["er019_family_x_audio_production_runner_01.py", "--slug", SLUG, "--run", RUN, "--level", level, "--stage", "tts",
                "--out-dir", out_dir, "--budget-jpy", "60", "--only-segments", only] + extra
    print("[driver] argv=", sys.argv)
    x.main()


def cmd_x_k2():
    out_dir = f"{OUT}/x_k2"
    store_dir = f"{OUT}/x_k2_store"
    assert not os.path.exists(out_dir), "専用out_dirが既に存在します(再実行は禁止: 別名を使わず報告してください)"
    _seed_x_out_dir(out_dir, "b1b")
    _seed_store(store_dir, ["55cd6f202c8ff584b563b41e"])   # kp1 'think up' K2 key A(旧Store entry=S1経路)。kp4は意図的に未投入=新規生成経路
    _run_x(out_dir, "b1b", "kp1_english,kp4_english,kp1_explanation", [], store_dir)


def cmd_x_k2_rerun():
    out_dir = f"{OUT}/x_k2"
    _run_x(out_dir, "b1b", "kp1_english,kp4_english", [], f"{OUT}/x_k2_store")


def cmd_x_default():
    out_dir = f"{OUT}/x_default"
    store_dir = f"{OUT}/x_default_store"
    assert not os.path.exists(out_dir)
    _seed_x_out_dir(out_dir, "a2", copy_profile_record=False)   # default profileは固定記録なしの新規out_dirに--style-profile defaultで作る
    os.makedirs(store_dir, exist_ok=True)
    # default profileの固定記録(旧経路=+dual1 key)を専用out_dirに作る: --style-profile default を明示
    _run_x(out_dir, "a2", "kp2_english", ["--style-profile", "default"], store_dir)


def cmd_z():
    import er005_cost_logger as cl
    import er063_family_z_audio_01 as z
    run_dir = f"{OUT}/z_run"
    assert not os.path.exists(run_dir)
    os.makedirs(run_dir, exist_ok=True)
    src = json.load(open("er026_output/family_z_production_e2e_01/melos/run_e2e_01/b1b/audit/tts_generation_results.json", encoding="utf-8"))
    expl = src["key_phrases"]["1"]["explanation"]["canonical_text"]
    plan = [z.ClipSpec("kp1_en", "b1b", "kp_en", "give way", voice="Aoede", role_key="KP_EN", rank=1, language="en"),
            z.ClipSpec("kp1_explanation_en", "b1b", "kp_expl_en", expl, voice="Aoede", role_key="KP_EXPL_EN", rank=1, language="en",
                       extra={"used_form": "give way"})]
    store_dir = f"{OUT}/z_store"
    _store_patch(store_dir)    # Zは本件のKP英語phraseでStoreを使わない(念のため専用Store)
    cl.install(f"{run_dir}/raw_usage_log.jsonl")
    with cl.logging_context("kpdual_z", "tts"):
        r = z.run_tts_stage(run_dir, "b1b", plan)
    print(json.dumps(r, ensure_ascii=False, indent=2))


def cmd_z_rerun():
    import er005_cost_logger as cl
    import er063_family_z_audio_01 as z
    run_dir = f"{OUT}/z_run"
    plan = [z.ClipSpec("kp1_en", "b1b", "kp_en", "give way", voice="Aoede", role_key="KP_EN", rank=1, language="en")]
    cl.install(f"{run_dir}/raw_usage_log_rerun.jsonl")
    with cl.logging_context("kpdual_z", "tts"):
        r = z.run_tts_stage(run_dir, "b1b", plan)
    print(json.dumps(r, ensure_ascii=False, indent=2))


def cmd_survey():
    """本番Storeの記事B KP(K2 key A) S1確認。kp_dual_checkを保存(NGも記録のみ・再生成しない・audio不変)。"""
    import er005_cost_logger as cl
    import er006_master_audio_store_01 as store
    import er096_kp_dual_pass_01 as kd
    import er019_family_x_audio_production_runner_01 as x
    os.makedirs(OUT, exist_ok=True)
    cl.install(f"{OUT}/survey_raw_usage_log.jsonl")
    items = []
    for lv in ("a2", "b1b"):   # Std/Advでphraseが異なる場合があるため両levelのKPを対象にする(同一phraseはStoreで1 entry)
        kp = json.load(open(f"{SRC_X}/{lv}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
        items += [dict(it, level=lv) for it in sorted(kp["items"], key=lambda i: i["rank"])]
    import hashlib
    mf = store._load_manifest()
    rows = []
    seen = set()
    for it in items:
        safe = x.n3_tts.tts_safe_kp_en(it["used_form"])
        if safe in seen:
            continue
        seen.add(safe)
        h = hashlib.sha256(safe.encode("utf-8")).hexdigest()[:16]
        for mid, e in mf.items():
            k = e["key"]
            if k["style_instruction_id"] == "key_phrase_english_component_k2" and k["canonical_text_hash"] == h and k["language"] == "en":
                probe = dict(e)
                probe.update(e.get("qa_evidence") or {})
                with cl.segment_context(f"survey_kp{it['rank']}"):
                    d = kd.kp_dual_reuse_ok(probe, wav_path=e["audio_path"], canonical_text=safe, allow_s1=True, label=f"kp{it['rank']}")
                row = {"level": it["level"], "rank": it["rank"], "used_form": it["used_form"], "master_audio_id": mid, "action": d["action"], "ok": d["ok"],
                       "reason": d["reason"], "azure_real_calls": d.get("azure_real_calls"), "kp_dual_check": d.get("kp_dual_check")}
                if d.get("kp_dual_check") is not None and d["action"] in (kd.ACTION_REUSE, kd.ACTION_REGENERATE):
                    mf2 = store._load_manifest()
                    mf2[mid]["kp_dual_check"] = d["kp_dual_check"]       # 記録のみ(audio・他キー不変)
                    store._save_manifest(mf2)
                    row["persisted"] = True
                rows.append(row)
    json.dump(rows, open(f"{OUT}/survey_article_b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps([{k: r[k] for k in ("level", "rank", "used_form", "action", "ok", "reason", "azure_real_calls")} for r in rows], ensure_ascii=False, indent=2))


def _kp_phrase_sample(n: int = 24) -> list:
    """実運用のKP phrase標本: er019_output配下の過去runのb1b/a2 KP(重複除去、記事Bで使用済みは除外)から決定論的に選ぶ。"""
    import glob
    import random
    used_b = {"think up", "can't wait", "fan stories", "take part", "story-maker", "story maker", "blurt", "bring in"}
    seen, phrases = set(), []
    for p in sorted(glob.glob("er019_output/*/*/*/key_phrases/keywords_canonicalized.json")):
        if "manga_ai_chat_byus" in p:
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for it in d.get("items", []):
            uf = (it.get("used_form") or "").strip()
            if uf and uf.lower() not in seen and uf.lower() not in used_b:
                seen.add(uf.lower())
                phrases.append(uf)
    random.Random(20261022).shuffle(phrases)
    return phrases[:n]


def cmd_stats():
    """Production関数(K2 2段key経路のensure_key_phrase_english_component_styled)で標本phraseを専用Storeに新規生成し、dual判定下の
    試行回数・Azure呼出数・Primary NG/Azure NG内訳・HR queue投入有無を実測する。1コマンド=1回(再起動なし)。"""
    import er005_cost_logger as cl
    import er019_family_x_audio_production_runner_01 as x
    import er019_family_x_kp_en_k2_store_01 as k2s
    import er019_family_x_style_profile_01 as sp
    phrases = _kp_phrase_sample(24)
    out_root = f"{OUT}/stats"
    assert not os.path.exists(out_root)
    os.makedirs(f"{out_root}/theme/b1b/narration", exist_ok=True)
    _store_patch(f"{OUT}/stats_store")
    cl.install(f"{out_root}/raw_usage_log.jsonl")
    k2 = sp.resolve_role_style("fx_20261017", sp.ROLE_KP_EN, "b1b", lambda _r: None)
    rows = []
    for i, uf in enumerate(phrases, start=1):
        safe = x.n3_tts.tts_safe_kp_en(uf)
        outp = f"{out_root}/theme/b1b/narration/kp{i}_en.wav"
        with cl.logging_context("kpdual_stats", "tts"), cl.segment_context(f"kp{i}_english"):
            r = k2s.ensure_key_phrase_english_component_styled(safe, outp, style_text=k2, style_id=sp.KP_EN_STORE_STYLE_ID,
                                                              style_tag="k2", tts_backend="speech_metadata_flash_lite")
        logs = (r.get("minimal_attempts_log") or []) + (r.get("english_lock_attempts_log") or []) if r.get(_FU) else (r.get("attempts_log") or [])
        att = []
        for a in logs:
            aj = a.get("asr_judgement") or {}
            d = aj.get("dual") or {}
            att.append({"attempt": a.get("attempt"), "primary_text": a.get("asr_text"), "secondary_text": (aj.get("secondary") or {}).get("text"),
                        "state": aj.get("state"), "primary_pass": d.get("primary_pass"), "secondary_pass": d.get("secondary_pass"),
                        "secondary_called": d.get("secondary_called")})
        rows.append({"i": i, "used_form": uf, "safe": safe, "status": r.get("status"), "fallback_used": r.get(_FU),
                     "n_attempts": len(att), "attempts": att, "kp_dual_check_ok": (r.get("kp_dual_check") or {}).get("ok")})
        print(i, uf, r.get("status"), len(att), [a["state"] for a in att], flush=True)
        json.dump(rows, open(f"{out_root}/stats_rows.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def cmd_take_part_live():
    """take part型を実Primary(OpenAI)+実Azureで: Trial er088のwav(Azureが'Take Tart.'と転写する音声)をProduction dual判定へ。"""
    import er005_cost_logger as cl
    import er003_v1_repro01_main_generate as repro01
    import er096_kp_dual_pass_01 as kd
    wav = "er088_output/kp_asr_dual_pass_trial_01/kp4_en.wav"
    rows = []
    cl.install(f"{OUT}/take_part_live_raw_usage_log.jsonl")
    for i in range(3):
        with cl.logging_context("kpdual_take_part", "asr"), cl.segment_context(f"take_part_live_{i + 1}"):
            pt, err = repro01.routing.transcribe(wav, language="en-US", prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT)
            ev = kd.evaluate_dual("take part", pt, wav)
        rows.append({"trial": i + 1, "primary_text": pt, "primary_err": err, "state": ev["state"], "verified": ev["verified"],
                     "primary_pass": ev["dual"].get("primary_pass"), "secondary_text": ev["secondary_text"],
                     "azure_real_calls": ev["azure_real_calls"], "dual": ev["dual"]})
        print(rows[-1]["trial"], pt, ev["state"], ev["secondary_text"], flush=True)
    json.dump(rows, open(f"{OUT}/take_part_live.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _usage_by_segment(path: str) -> dict:
    out = {}
    if not os.path.exists(path):
        return out
    for l in open(path, encoding="utf-8"):
        if not l.strip():
            continue
        r = json.loads(l)
        seg = r.get("segment") or "?"
        d = out.setdefault(seg, {"azure_calls": 0, "openai_asr_calls": 0, "tts_calls": 0, "models": set(), "azure_elapsed_s": 0.0})
        if r["provider"] == "azure":
            d["azure_calls"] += 1
            d["azure_elapsed_s"] += r.get("elapsed_seconds") or 0
        elif r["provider"] == "openai_asr":
            d["openai_asr_calls"] += 1
        elif r["provider"] == "gemini":
            d["tts_calls"] += 1
        d["models"].add(r.get("model_id"))
    for d in out.values():
        d["models"] = sorted(m for m in d["models"] if m)
        d["azure_elapsed_s"] = round(d["azure_elapsed_s"], 3)
    return out


def cmd_summarize():
    """各実走の結果を1つのevidence_summary.jsonへ集約する(API 0)。"""
    import er019_family_x_audio_production_runner_01 as x
    S = {"generated_by": "er096_kp_dual_runtime_evidence_01.py summarize", "cost_jpy": {}, "runs": {}}

    def cost(p):
        return round(x.compute_cost_jpy_so_far(p)[0], 4) if os.path.exists(p) else None
    S["cost_jpy"] = {"x_k2_run1": cost(f"{OUT}/x_k2_raw_usage_log_run1.jsonl"), "x_k2_rerun_added": 0.0,
                     "x_default": cost(f"{OUT}/x_default/raw_usage_log.jsonl"), "z_run": cost(f"{OUT}/z_run/raw_usage_log.jsonl"),
                     "survey_article_b_S1": cost(f"{OUT}/survey_raw_usage_log.jsonl"), "postmortem_kp1_old_wav": cost(f"{OUT}/x_k2_postmortem_kp1_raw_usage_log.jsonl"),
                     "stats_24_phrases": cost(f"{OUT}/stats/raw_usage_log.jsonl"), "take_part_live": cost(f"{OUT}/take_part_live_raw_usage_log.jsonl")}
    S["cost_jpy"]["total"] = round(sum(v for v in S["cost_jpy"].values() if v), 4)
    S["usage_by_segment"] = {"x_k2_run1": _usage_by_segment(f"{OUT}/x_k2_raw_usage_log_run1.jsonl"),
                             "x_k2_rerun": _usage_by_segment(f"{OUT}/x_k2/raw_usage_log.jsonl") if False else "rerun log == run1 log (no added lines)",
                             "x_default": _usage_by_segment(f"{OUT}/x_default/raw_usage_log.jsonl"),
                             "z_run": _usage_by_segment(f"{OUT}/z_run/raw_usage_log.jsonl")}

    def brief(e):
        aj = e.get("asr_judgement") or e.get("asr_judgement_inherited") or {}
        d = aj.get("dual")
        return {"status": e.get("status"), "reused_from_previous_run": e.get("reused_from_previous_run"), "reused": e.get("reused"),
                "master_audio_id": e.get("master_audio_id"), "cache_miss_reason": e.get("cache_miss_reason"),
                "fallback_used": e.get(_FU), "state": aj.get("state"), "dual": d, "kp_dual_check": e.get("kp_dual_check"),
                "model": e.get("model"), "kp_dual_reuse_gate_previous": e.get("kp_dual_reuse_gate_previous"),
                "validation_inheritance": (e.get("validation_inheritance") or {}).get("label"),
                "attempts": [{"attempt": a.get("attempt"), "asr_text": a.get("asr_text"), "audio_classification": a.get("audio_classification"),
                              "verified": a.get("verified"),
                              "steps": [(st.get("step"), st.get("provider"), st.get("text")) for st in (a.get("cascade_steps") or [])],
                              "dual_required": ((a.get("asr_judgement") or {}).get("dual") or {}).get("required")} for a in (e.get("attempts_log") or [])]}
    for name, path in (("x_k2_after_rerun", f"{OUT}/x_k2/b1b/audit/tts_generation_results.json"),
                       ("x_default", f"{OUT}/x_default/a2/audit/tts_generation_results.json"),
                       ("z_run_after_rerun", f"{OUT}/z_run/b1b/audit/tts_generation_results.json")):
        if os.path.exists(path):
            d = json.load(open(path, encoding="utf-8"))
            S["runs"][name] = {f"kp{r}_{role}": brief(e) for r, subs in d.get("key_phrases", {}).items() for role, e in subs.items()
                               if e.get("status") != "SKIPPED_NOT_SELECTED"}
    for name, path in (("x_k2_store_manifest(run1 generation, 専用Store)", f"{OUT}/x_k2_store/manifest.json"),
                       ("x_default_store_manifest", f"{OUT}/x_default_store/manifest.json")):
        if os.path.exists(path):
            m = json.load(open(path, encoding="utf-8"))
            S["runs"][name] = {mid: {"style_instruction_version": e["key"]["style_instruction_version"],
                                     "instruction_path": e["key"]["instruction_path"], "kp_dual_check": e.get("kp_dual_check"),
                                     "dual": (e.get("asr_judgement") or {}).get("dual"),
                                     "adapter": (e.get("asr_judgement") or {}).get("adapter")} for mid, e in m.items()}
    for name, path in (("survey_article_b", f"{OUT}/survey_article_b.json"), ("stats_rows", f"{OUT}/stats/stats_rows.json"),
                       ("take_part_live", f"{OUT}/take_part_live.json")):
        if os.path.exists(path):
            S["runs"][name] = json.load(open(path, encoding="utf-8"))
    rows = S["runs"].get("stats_rows") or []
    if rows:
        tot_att = sum(r["n_attempts"] for r in rows)
        S["stats_summary"] = {"phrases": len(rows), "first_attempt_pass": sum(1 for r in rows if r["n_attempts"] == 1 and r["status"] == "OK"),
                              "stopped": [r["used_form"] for r in rows if r["status"] != "OK"], "total_attempts": tot_att,
                              "extra_attempts": tot_att - len(rows), "azure_calls_total": sum(1 for r in rows for a in r["attempts"] if a["secondary_called"])}
    json.dump(S, open(f"{OUT}/evidence_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    print(json.dumps({"cost_jpy": S["cost_jpy"], "stats_summary": S.get("stats_summary")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    {"x_k2": cmd_x_k2, "x_k2_rerun": cmd_x_k2_rerun, "x_default": cmd_x_default, "z": cmd_z, "z_rerun": cmd_z_rerun,
     "survey": cmd_survey, "stats": cmd_stats, "take_part_live": cmd_take_part_live, "summarize": cmd_summarize}[sys.argv[1]]()
