# -*- coding: utf-8 -*-
"""AUW 委任_06: 実音声 runtime evidence runner(EN Melos 回帰 / JA 値ガード / A2・Dialogue・KP)。
Production の判定関数(adapter)を実音声で呼ぶ evidence 専用 runner。Production コードは無編集(実行時に module 変数を差し替えるだけ)。
共有 state(HR queue / attempt_history / master_audio_store / telemetry / cost log / Ledger)は evidence 配下へ隔離(er077 runner の apply_isolation を再利用)。
有料 API は --execute 指定時のみ。1 呼出ごとに usage_log.jsonl へ記録(OpenAI primary ASR は cost logger に記録されないため runner 側 wrapper で記録)。
監督ループ・自動再試行なし。予算 hard stop 超過見込みで停止。
使い方: .venv\\Scripts\\python.exe er078_auw_runtime_evidence_06.py melos [--execute --budget-jpy N]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
EV = "er058_output/unified_all_roles_production_wiring_01/evidence_06"
MANAGED_IDS = ["AUW-06", "ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01"]
AZURE_JPY_PER_S = 0.0444      # er069 cost_02 実績
OPENAI_JPY_PER_CALL = 0.0094  # er077 EVIDENCE_RUN_01 と同じ単価
import stop_scope_check_01 as _stop_scope  # noqa: E402


def stop_present(out_dir):
    r = _stop_scope.check(MANAGED_IDS, os.path.join(ROOT, out_dir))
    return [f"{a['kind']}:{a['path']}" for a in r["applicable"]]


def wav_seconds(p):
    try:
        with wave.open(p, "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return 3.0


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


class Meter:
    def __init__(self, out_dir, hard_stop):
        self.out_dir, self.hard_stop = out_dir, hard_stop
        self.jpy = 0.0
        self.n_openai = 0
        self.n_azure = 0
        self.azure_by_sha = {}
        self.log = open(os.path.join(out_dir, "usage_log.jsonl"), "a", encoding="utf-8")

    def rec(self, **kw):
        kw["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        kw["cum_jpy"] = round(self.jpy, 4)
        self.log.write(json.dumps(kw, ensure_ascii=False) + "\n")
        self.log.flush()

    def check(self):
        if self.jpy > self.hard_stop:
            raise RuntimeError(f"[STOP] hard stop budget exceeded: {self.jpy:.3f} > {self.hard_stop}")


def install(meter):
    import er006_asr_provider_routing_01 as routing
    import er006_secondary_asr_01 as sec
    _t, _az = routing.transcribe, sec.get_full_text_via_azure_stt_with_phrase_list

    def t_wrap(wav, *a, **k):
        meter.check()
        meter.n_openai += 1
        meter.jpy += OPENAI_JPY_PER_CALL
        r = _t(wav, *a, **k)
        meter.rec(provider="openai", api="transcribe", wav=wav, est_jpy=OPENAI_JPY_PER_CALL, text=r[0], err=r[1])
        return r

    def az_wrap(wav, *a, **k):
        meter.check()
        s = sha(wav)
        meter.azure_by_sha[s] = meter.azure_by_sha.get(s, 0) + 1
        meter.n_azure += 1
        c = AZURE_JPY_PER_S * wav_seconds(wav)
        meter.jpy += c
        r = _az(wav, *a, **k)
        meter.rec(provider="azure", api="stt", wav=wav, sha=s[:12], est_jpy=round(c, 5), text=r[0] if isinstance(r, tuple) else None)
        return r

    routing.transcribe = t_wrap
    sec.get_full_text_via_azure_stt_with_phrase_list = az_wrap


def isolate(out_dir):
    import er077_m1_oov_multi_pronunciation_01_evidence_runner as r77
    os.makedirs(out_dir, exist_ok=True)
    before = r77.snapshot_state()
    iso = r77.apply_isolation(out_dir)
    return r77, before, iso


# ---------------------------------------------------------------- B: EN Melos
EX_DIR = "er069_output/attribution_clip_split_trial_01/gen02/wav"
EX_IDS = ([f"Melos_said_L2_adv_t{t}_raw" for t in (1, 2, 3, 4)]
          + [f"Melos_said_L2_std_t{t}_{v}" for t in (1, 2, 3, 4) for v in ("raw", "slow6")])
NEW = [("nonsib_left", "Melos left."), ("nonsib_ran", "Melos ran."), ("repeat", "Melos said Melos left."),
       ("neg_num", "Melos did not wait five days.")]
OLD_DIR = "er077_output/m1_oov_multi_pronunciation_01/evidence_01"


def run_melos(execute, budget, stored_primary=False):
    out = f"{EV}/melos_stored_primary" if stored_primary else f"{EV}/melos"
    r77, before, iso = isolate(out)
    hit = stop_present(out)
    obs = []
    for i in EX_IDS:
        obs.append({"id": i, "text": "Melos said.", "wav": f"{EX_DIR}/{i}.wav", "segment_id": "full_story_part1"})
    for i in EX_IDS:
        obs.append({"id": i + "__segNone", "text": "Melos said.", "wav": f"{EX_DIR}/{i}.wav", "segment_id": None})
    for k, text in NEW:
        for t in (1, 2, 3):
            obs.append({"id": f"{k}_t{t}", "text": text, "wav": f"{OLD_DIR}/gen/wav/{k}_t{t}_raw.wav", "segment_id": "full_story_part1"})
    missing = [o["wav"] for o in obs if not os.path.exists(o["wav"])]
    n_wav = len({o["wav"] for o in obs})
    plan = {"n_observations": len(obs), "n_distinct_wavs": n_wav, "missing_wavs": missing,
            "est_jpy_max": round(len(obs) * OPENAI_JPY_PER_CALL + n_wav * 1.6 * AZURE_JPY_PER_S, 3)}
    res = {"mode": "execute" if execute else "dry-run", "stop_files_present": hit, "plan": plan, "isolation": iso}
    if execute and not hit and not missing and plan["est_jpy_max"] <= budget:
        import er006_secondary_asr_01 as sec
        import er006_pronunciation_ledger_01 as ledger_mod
        import er006_asr_provider_routing_01 as routing
        meter = Meter(out, hard_stop=budget)
        install(meter)
        old = {c["id"]: c for c in json.load(open(f"{OLD_DIR}/clip_results.json", encoding="utf-8"))}
        sec.begin_secondary_run()  # run 単位 cache + circuit breaker(Production runner の with_secondary_run と同じ)
        rows = []
        try:
            for o in obs:
                if stop_present(out):
                    res["soft_stop"] = True
                    break
                sec._reset_m1_freeze_cache()
                n_az0 = meter.n_azure
                if stored_primary:  # Primary は 10/14 の保存転写を再利用(Primary側のみ可)。Secondary は実Azure
                    asr_text, err = old[o["id"]]["primary_asr"], None
                else:
                    asr_text, err = routing.transcribe(o["wav"], language="en-US")
                phrases = [h["canonical_spelling"] for h in ledger_mod.get_hint_for_text(o["text"], min_confidence="low")]
                d = sec.evaluate_attempt_with_cascade_detail(
                    o["text"], asr_text, [], o["wav"], language="en-US", ledger_phrases=phrases, cascade_enabled=True,
                    segment_id=o["segment_id"], attempt_ctx={"slot": 1, "script_version": "v0", "is_last_slot": False})
                aj = d["asr_judgement"]
                o_old = old.get(o["id"], {})
                rows.append({
                    "id": o["id"], "text": o["text"], "segment_id": o["segment_id"], "wav": o["wav"],
                    "primary_asr": asr_text, "primary_err": err, "new_verified": d["verified"], "new_final_status": d["final_status"],
                    "new_state": aj["state"], "new_reason": aj["reason_code"], "new_warnings": aj.get("warnings"),
                    "new_m1": bool(d.get("m1_multi_candidate")), "secondary_text": (aj.get("secondary") or {}).get("text"),
                    "value_guard": aj.get("value_guard"),
                    "azure_real_calls_this_obs": meter.n_azure - n_az0, "adapter": aj.get("adapter"),
                    "old_verified": o_old.get("verified"), "old_final_status": o_old.get("final_status"), "old_primary_asr": o_old.get("primary_asr"),
                    "old_m1": o_old.get("final_status") == "M1_MULTI_CANDIDATE_ACCEPT"})
                json.dump(rows, open(f"{out}/clip_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
        finally:
            sec.end_secondary_run()
        res["rows"] = len(rows)
        res["cost"] = {"est_total_jpy": round(meter.jpy, 4), "n_openai": meter.n_openai, "n_azure": meter.n_azure,
                       "azure_duplicate_wavs": sum(1 for v in meter.azure_by_sha.values() if v > 1),
                       "azure_max_calls_per_distinct_wav": max(meter.azure_by_sha.values(), default=0), "budget_jpy": budget}
    after = r77.snapshot_state()
    res["shared_state_unchanged"] = before == after
    json.dump(res, open(f"{out}/runner_{res['mode']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: res.get(k) for k in ("mode", "stop_files_present", "plan", "rows", "cost", "shared_state_unchanged")}, ensure_ascii=False, default=str))


# ---------------------------------------------------------------- B2: 実音声ネガティブ(canonical を別内容にして誤受理0を確認。TTS不要=既存wav再利用)
NEG_CASES = [
    ("num_diff_six", "neg_num_t1", "Melos did not wait six days."),
    ("num_diff_fifteen", "neg_num_t2", "Melos did not wait fifteen days."),
    ("neg_removed", "neg_num_t1", "Melos did wait five days."),
    ("neg_added_num_same", "nonsib_left_t1", "Melos did not leave."),
    ("other_word", "nonsib_left_t2", "Melos sat."),
    ("other_word2", "nonsib_ran_t1", "Melos won."),
    ("diff_name_sentence", "repeat_t1", "Melos said Melos won."),
]


def run_negatives(execute, budget):
    out = f"{EV}/melos_negatives"
    r77, before, iso = isolate(out)
    hit = stop_present(out)
    res = {"mode": "execute" if execute else "dry-run", "stop_files_present": hit,
           "plan": {"n_cases": len(NEG_CASES), "est_jpy_max": round(len(NEG_CASES) * (OPENAI_JPY_PER_CALL + 1.6 * AZURE_JPY_PER_S), 3)}}
    if execute and not hit and res["plan"]["est_jpy_max"] <= budget:
        import er006_secondary_asr_01 as sec
        import er006_pronunciation_ledger_01 as ledger_mod
        import er006_asr_provider_routing_01 as routing
        meter = Meter(out, hard_stop=budget)
        install(meter)
        sec.begin_secondary_run()
        rows = []
        try:
            for cid, wid, canon in NEG_CASES:
                wav = f"{OLD_DIR}/gen/wav/{wid}_raw.wav"
                sec._reset_m1_freeze_cache()
                n0 = meter.n_azure
                asr_text, err = routing.transcribe(wav, language="en-US")
                phrases = [h["canonical_spelling"] for h in ledger_mod.get_hint_for_text(canon, min_confidence="low")]
                d = sec.evaluate_attempt_with_cascade_detail(
                    canon, asr_text, [], wav, language="en-US", ledger_phrases=phrases, cascade_enabled=True,
                    segment_id="full_story_part1", attempt_ctx={"slot": 1, "script_version": "v0", "is_last_slot": False})
                aj = d["asr_judgement"]
                rows.append({"case": cid, "wav": wav, "actual_spoken_text": [c for c in NEW if wid.startswith(c[0])][0][1],
                             "canonical_given": canon, "primary_asr": asr_text, "verified": d["verified"], "state": aj["state"],
                             "reason": aj["reason_code"], "final_status": d["final_status"], "secondary_text": (aj.get("secondary") or {}).get("text"),
                             "value_guard": aj.get("value_guard"), "azure_calls": meter.n_azure - n0})
        finally:
            sec.end_secondary_run()
        res["rows"] = rows
        res["false_accepts"] = [r["case"] for r in rows if r["verified"]]
        res["cost"] = {"est_total_jpy": round(meter.jpy, 4), "n_openai": meter.n_openai, "n_azure": meter.n_azure}
    after = r77.snapshot_state()
    res["shared_state_unchanged"] = before == after
    json.dump(res, open(f"{out}/runner_{res['mode']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: res.get(k) for k in ("mode", "stop_files_present", "plan", "false_accepts", "cost", "shared_state_unchanged")}, ensure_ascii=False, default=str))


# ---------------------------------------------------------------- C: JA 値ガード(実音声。既存JA run の wav を再利用=TTS不要)
# (case_id, 候補index[ja_candidates.json], canonical を差し替える場合の文字列[None=原稿どおり], 種別)
JA_CASES = [
    ("household_title_2tsu", 0, None, "positive"),
    ("akb48_comment2_2saku", 3, None, "positive"),
    ("akb48_comment3_2saku", 4, None, "positive"),
    ("ai_factory_title_2tsu", 5, None, "positive"),
    ("household_title2_2tsu", 6, None, "positive"),
    ("akb48_title_AKB48_2saku", 1, None, "positive"),
    ("neg_household_3tsu", 6, "冷蔵庫の野菜室、3つの設定を使い分けると食品が長持ちする", "numeric_diff"),
    ("neg_ai_factory_3tsu", 5, "AI工場の物語には、進み方の異なる3つの時計がある", "numeric_diff"),
    ("neg_akb48_comment2_3saku", 3, "__REPLACE_2SAKU__", "numeric_diff"),
    ("neg_household_negation", 6, "冷蔵庫の野菜室、2つの設定を使い分けても食品は長持ちしない", "negation_diff"),
]


def run_ja(execute, budget):
    out = f"{EV}/ja"
    r77, before, iso = isolate(out)
    hit = stop_present(out)
    cands = json.load(open(f"{EV}/ja_candidates.json", encoding="utf-8"))
    plan = {"n_cases": len(JA_CASES), "est_jpy_max": round(len(JA_CASES) * (OPENAI_JPY_PER_CALL + 12 * AZURE_JPY_PER_S), 3)}
    res = {"mode": "execute" if execute else "dry-run", "stop_files_present": hit, "plan": plan, "isolation": iso}
    if execute and not hit and plan["est_jpy_max"] <= budget:
        import er006_asr_provider_routing_01 as routing
        import er006_secondary_asr_01 as sec
        import er007_ja_secondary_asr_01 as ja
        meter = Meter(out, hard_stop=budget)
        install(meter)
        _az = ja._azure_stt_strict

        def az_ja(wav, *a, **k):
            meter.check()
            s_ = sha(wav)
            meter.azure_by_sha[s_] = meter.azure_by_sha.get(s_, 0) + 1
            meter.n_azure += 1
            c = AZURE_JPY_PER_S * wav_seconds(wav)
            meter.jpy += c
            r = _az(wav, *a, **k)
            meter.rec(provider="azure", api="stt_strict_ja", wav=wav, sha=s_[:12], est_jpy=round(c, 5), text=r[0])
            return r
        ja._azure_stt_strict = az_ja
        sec.begin_secondary_run()
        rows = []
        try:
            for cid, idx, canon_override, kind in JA_CASES:
                f, k, wav, text, stored_asr = cands[idx]
                canon = text
                if canon_override == "__REPLACE_2SAKU__":
                    canon = text.replace("2作", "3作")
                elif canon_override:
                    canon = canon_override
                n0 = meter.n_azure
                asr_text, err = routing.transcribe(wav, language="ja-JP")
                d = ja.evaluate_attempt_ja_with_cascade_detail(
                    canon, asr_text, wav, cascade_enabled=True,
                    attempt_ctx={"slot": 1, "script_version": "v0", "is_last_slot": False, "segment_key": cid})
                aj = d["asr_judgement"]
                rows.append({"case": cid, "kind": kind, "source_run": f.replace("\\", "/").split("/audit")[0], "segment": k, "wav": wav,
                             "tts_canonical_text": text, "canonical_given": canon, "primary_asr": asr_text, "primary_err": err,
                             "stored_asr_text": stored_asr, "verified": d["verified"], "state": aj["state"], "reason": aj["reason_code"],
                             "final_status": d["final_status"], "warnings": aj.get("warnings"),
                             "secondary_text": (aj.get("secondary") or {}).get("text"), "value_guard": aj.get("value_guard"),
                             "azure_calls": meter.n_azure - n0, "asr_judgement": aj})
        finally:
            sec.end_secondary_run()
            ja._azure_stt_strict = _az
        res["rows"] = rows
        res["false_accepts"] = [r["case"] for r in rows if r["verified"] and r["kind"] != "positive"]
        res["positive_rejected"] = [r["case"] for r in rows if (not r["verified"]) and r["kind"] == "positive"]
        res["cost"] = {"est_total_jpy": round(meter.jpy, 4), "n_openai": meter.n_openai, "n_azure": meter.n_azure,
                       "azure_duplicate_wavs": sum(1 for v in meter.azure_by_sha.values() if v > 1)}
    after = r77.snapshot_state()
    res["shared_state_unchanged"] = before == after
    json.dump(res, open(f"{out}/runner_{res['mode']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: res.get(k) for k in ("mode", "stop_files_present", "plan", "false_accepts", "positive_rejected", "cost", "shared_state_unchanged")}, ensure_ascii=False, default=str))


# ---------------------------------------------------------------- E: Production正式path(Family Z run_tts_stage)で実TTS->A2減速後判定/Dialogue/KP解説
def run_z(execute, budget):
    out = f"{EV}/z_prod_path"
    r77, before, iso = isolate(out)
    hit = stop_present(out)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"   # 開発・短clip評価: Standard同期(PM_GOVERNANCE 7-1)。Batchの遅延を避ける
    import er063_family_z_audio_01 as Z
    plan = [
        Z.ClipSpec("full_story_part1_c1", "a2", "narrator",
                   "Coffee beans cost less now. Shops may still keep their prices for about nine months.",
                   voice="Aoede", role_key="NARRATOR_FULL_STORY_STD", part=1),
        Z.ClipSpec("full_story_part1_c2", "a2", "dialogue", "Why did you wait twenty minutes?",
                   voice="Charon", speaker="A", role_key="DIALOGUE_STD", part=1),
        Z.ClipSpec("kp1_explanation_en", "a2", "kp_expl_en",
                   "To keep your cool means to stay calm when things get hard. You do not lose your temper.",
                   voice="Aoede", role_key="KP_EXPL_EN", rank=1, language="en", extra={"used_form": "keep your cool"}),
    ]
    res = {"mode": "execute" if execute else "dry-run", "stop_files_present": hit, "isolation": iso,
           "plan": [{"clip_id": c.clip_id, "kind": c.kind, "voice": c.voice, "text": c.text} for c in plan]}
    run_dir = f"{out}/run"
    if execute and not hit:
        meter = Meter(out, hard_stop=budget)
        install(meter)
        # Z の run_tts_stage は with_secondary_run で自前の run scope を持つ(Production と同じ)
        r = Z.run_tts_stage(run_dir, "a2", plan)
        res["stage_result"] = {k: r[k] for k in ("results_path", "evidence_path", "statuses")}
        res["cost_asr_est"] = {"est_total_jpy": round(meter.jpy, 4), "n_openai": meter.n_openai, "n_azure": meter.n_azure,
                               "azure_by_sha": meter.azure_by_sha}
    after = r77.snapshot_state()
    res["shared_state_unchanged"] = before == after
    json.dump(res, open(f"{out}/runner_{res['mode']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: res.get(k) for k in ("mode", "stop_files_present", "stage_result", "cost_asr_est", "shared_state_unchanged")}, ensure_ascii=False, default=str))


# ---------------------------------------------------------------- D/E: A2減速後判定の Secondary 経路(実音声) + Secondary障害(mock) + 試聴リスト hook
def run_a2sec(execute, budget):
    import copy
    import shutil
    out = f"{EV}/a2_secondary"
    r77, before, iso = isolate(out)
    hit = stop_present(out)
    zdir = f"{EV}/z_prod_path/run/a2"
    zres = json.load(open(f"{zdir}/audit/tts_generation_results.json", encoding="utf-8"))
    res = {"mode": "execute" if execute else "dry-run", "stop_files_present": hit, "isolation": iso}
    if execute and not hit:
        import er003_v1_n3_01_tts_generate as n3
        import er006_secondary_asr_01 as sec
        import er078_pass_with_warning_registry_01 as pww
        meter = Meter(out, hard_stop=budget)
        install(meter)
        c1 = zres["segments"]["full_story_part1_c1"]
        c1_orig = f"{zdir}/narration/full_story_part1_c1_original.wav"
        melos_wav = f"{EX_DIR}/Melos_said_L2_adv_t3_raw.wav"
        # case: (id, name[=segment_id], source wav, canonical, base result, azure_mode)
        cases = [
            ("S1_melos_primaryNG_secondaryPASS", "full_story_part1", melos_wav, "Melos said.", None, "real"),
            ("S2_content_word_diff_both_NG", "full_story_part1", c1_orig,
             "Coffee beans cost less now. Banks may still keep their prices for about nine months.", c1, "real"),
            ("S3_numeric_diff_protected", "full_story_part1", c1_orig,
             "Coffee beans cost less now. Shops may still keep their prices for about ten months.", c1, "real"),
            ("S4_secondary_outage_mock_errreturn", "full_story_part1", c1_orig,
             "Coffee beans cost less now. Banks may still keep their prices for about nine months.", c1, "mock_outage_err"),
            ("S5_secondary_outage_mock_raise", "full_story_part1", c1_orig,
             "Coffee beans cost less now. Banks may still keep their prices for about nine months.", c1, "mock_outage_raise"),
        ]
        segs, rows = {}, []
        _az_metered = sec.get_full_text_via_azure_stt_with_phrase_list  # install()済みの計測wrapper
        for cid, name, src, canon, base, mode in cases:
            nd = f"{out}/narr_{cid}"
            os.makedirs(nd, exist_ok=True)
            shutil.copyfile(src, f"{nd}/{name}.wav")
            result = copy.deepcopy(base) if base else {"status": "OK", "text": canon, "language": "en", "path": f"{nd}/{name}.wav",
                                                       "sha256": sha(src), "duration_seconds": wav_seconds(src), "trim_info": None}
            result["path"] = f"{nd}/{name}.wav"
            result.pop("asr_judgement", None)
            sec.begin_secondary_run()
            n0 = meter.n_azure
            if mode.startswith("mock_outage"):
                def _out(*a, _m=mode, **k):
                    meter.rec(provider="azure", api="stt", mock="OUTAGE", mode=_m, note="mocked Secondary failure (no network call)")
                    if _m == "mock_outage_raise":
                        raise ConnectionError("mock Secondary outage")
                    return None, "mock Secondary service error"
                sec.get_full_text_via_azure_stt_with_phrase_list = _out
            exc = None
            try:
                r = n3.apply_a2_slowdown_postprocess(name, nd, canon, result, is_last_slot=False)
            except Exception as e_:  # noqa: BLE001  証拠として例外種別を記録(PASS扱いにはならない)
                exc = f"{type(e_).__name__}: {e_}"
                r = {"status": "EXCEPTION", "reason": exc}
            finally:
                sec.get_full_text_via_azure_stt_with_phrase_list = _az_metered
                sec.end_secondary_run()
            aj = r.get("asr_judgement") or r.get("asr_judgement_post_slowdown_ng") or {}
            rows.append({"case": cid, "mode": mode, "exception": exc, "canonical": canon, "status": r.get("status"), "post_slowdown_asr_text": r.get("post_slowdown_asr_text"),
                         "post_final_classification": r.get("post_slowdown_final_classification"), "state": aj.get("state"),
                         "reason": aj.get("reason_code"), "secondary_text": (aj.get("secondary") or {}).get("text"),
                         "secondary_called": (aj.get("secondary") or {}).get("called"), "secondary_error": (aj.get("secondary") or {}).get("error"),
                         "azure_real_calls": meter.n_azure - n0, "has_asr_judgement": bool(r.get("asr_judgement")),
                         "has_asr_judgement_post_slowdown_ng": bool(r.get("asr_judgement_post_slowdown_ng")),
                         "has_pre_slowdown": "asr_judgement_pre_slowdown" in r, "asr_judgement": aj})
            if r.get("status") == "OK":
                segs[f"{cid}"] = r
            res.setdefault("results_raw", {})[cid] = {k: r.get(k) for k in ("status", "reason")}
        res["rows"] = rows
        res["azure_dupes"] = sum(1 for v in meter.azure_by_sha.values() if v > 1)
        # JA PWW(JA run の実 asr_judgement) を同じ結果docへ(JA 経路も試聴リストに載ることの確認)
        jar = json.load(open(f"{EV}/ja/runner_execute.json", encoding="utf-8"))["rows"]
        for jr in jar:
            if jr["state"] == "PASS_WITH_WARNING" and jr["kind"] == "positive":
                segs["ja_" + jr["case"]] = {"status": "OK", "text": jr["canonical_given"], "language": "ja", "path": jr["wav"],
                                           "sha256": sha(jr["wav"]), "asr_judgement": jr["asr_judgement"], "segment_id": jr["case"], "role": "JAPANESE_TITLE"}
        run_dir = f"{out}/run_a2sec"
        os.makedirs(f"{run_dir}/audit", exist_ok=True)
        json.dump({"segments": segs, "key_phrases": {}}, open(f"{run_dir}/audit/tts_generation_results.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2, default=str)
        rep = pww.write_listening_list_safe(run_dir, standalone_html=True)  # 生成完了hookと同じ関数
        res["listening_list_report"] = rep
        lst = json.load(open(rep["json"], encoding="utf-8"))
        res["listening_list_count"] = lst["count"]
        res["cost"] = {"est_total_jpy": round(meter.jpy, 4), "n_openai": meter.n_openai, "n_azure": meter.n_azure}
    after = r77.snapshot_state()
    res["shared_state_unchanged"] = before == after
    json.dump(res, open(f"{out}/runner_{res['mode']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: res.get(k) for k in ("mode", "stop_files_present", "azure_dupes", "listening_list_count", "cost", "shared_state_unchanged")}, ensure_ascii=False, default=str))


# ---------------------------------------------------------------- C2: JA を Production 正式 path(Family Z run_tts_stage)で実TTS->実Primary->(NGなら)実Secondary
def run_zja(execute, budget):
    out = f"{EV}/z_ja_prod_path"
    r77, before, iso = isolate(out)
    hit = stop_present(out)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er063_family_z_audio_01 as Z
    plan = [
        Z.ClipSpec("japanese_title", "a2", "japanese_title", "コーヒー豆の値段が下がっても、お店の値札は9か月ほど変わらないかもしれません。",
                   voice="Aoede", role_key="STD_JA_PREVIEW", language="ja"),
        Z.ClipSpec("comment_1", "a2", "comment", "会議は十分で終わります。", voice="Aoede", role_key="STD_JA_COMMENT", language="ja"),
    ]
    res = {"mode": "execute" if execute else "dry-run", "stop_files_present": hit, "isolation": iso,
           "plan": [{"clip_id": c.clip_id, "kind": c.kind, "text": c.text} for c in plan]}
    run_dir = f"{out}/run"
    if execute and not hit:
        import er007_ja_secondary_asr_01 as ja
        meter = Meter(out, hard_stop=budget)
        install(meter)
        _az = ja._azure_stt_strict

        def az_ja(wav, *a, **k):
            meter.check()
            s_ = sha(wav)
            meter.azure_by_sha[s_] = meter.azure_by_sha.get(s_, 0) + 1
            meter.n_azure += 1
            c = AZURE_JPY_PER_S * wav_seconds(wav)
            meter.jpy += c
            r = _az(wav, *a, **k)
            meter.rec(provider="azure", api="stt_strict_ja", wav=wav, sha=s_[:12], est_jpy=round(c, 5), text=r[0])
            return r
        ja._azure_stt_strict = az_ja
        try:
            r = Z.run_tts_stage(run_dir, "a2", plan)
        finally:
            ja._azure_stt_strict = _az
        res["stage_result"] = {k: r[k] for k in ("results_path", "evidence_path", "statuses")}
        res["cost_asr_est"] = {"est_total_jpy": round(meter.jpy, 4), "n_openai": meter.n_openai, "n_azure": meter.n_azure,
                               "azure_by_sha": meter.azure_by_sha}
    after = r77.snapshot_state()
    res["shared_state_unchanged"] = before == after
    json.dump(res, open(f"{out}/runner_{res['mode']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: res.get(k) for k in ("mode", "stop_files_present", "stage_result", "cost_asr_est", "shared_state_unchanged")}, ensure_ascii=False, default=str))


# ---------------------------------------------------------------- A: 両NG -> 再生成 -> 通算3回 -> STOPPED/HR(実音声。KP解説=3回化の実run)
# 原稿を ASR が再現できない非語列にして、Production の KP解説経路(generate_key_phrase_explanation_en_verified、max_attempts=3)を実TTS+実Primary+実Secondaryで走らせる。
# 隔離: HR queue / attempt_history / review_lock_state は evidence 配下(本番 Lock・queue に書かない)。1 clip・再起動なし。
def run_zfail(execute, budget):
    out = f"{EV}/z_fail3_prod_path"
    r77, before, iso = isolate(out)
    hit = stop_present(out)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er063_family_z_audio_01 as Z
    plan = [Z.ClipSpec("kp1_explanation_en", "a2", "kp_expl_en", "Zxqvt brrkl vnmpw glorp fnuk xyzzy plugh.",
                       voice="Aoede", role_key="KP_EXPL_EN", rank=1, language="en", extra={"used_form": "xyzzy plugh"})]
    res = {"mode": "execute" if execute else "dry-run", "stop_files_present": hit, "isolation": iso,
           "plan": [{"clip_id": c.clip_id, "kind": c.kind, "text": c.text} for c in plan]}
    run_dir = f"{out}/run"
    if execute and not hit:
        meter = Meter(out, hard_stop=budget)
        install(meter)
        try:
            r = Z.run_tts_stage(run_dir, "a2", plan)
            res["stage_result"] = {k: r[k] for k in ("results_path", "evidence_path", "statuses")}
        except Exception as e_:  # noqa: BLE001  deferred STOP 等。証拠として種別を残す
            res["stage_exception"] = f"{type(e_).__name__}: {str(e_)[:400]}"
        res["cost_asr_est"] = {"est_total_jpy": round(meter.jpy, 4), "n_openai": meter.n_openai, "n_azure": meter.n_azure,
                               "azure_by_sha": meter.azure_by_sha, "azure_dupes": sum(1 for v in meter.azure_by_sha.values() if v > 1)}
    after = r77.snapshot_state()
    res["shared_state_unchanged"] = before == after
    json.dump(res, open(f"{out}/runner_{res['mode']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: res.get(k) for k in ("mode", "stop_files_present", "stage_result", "stage_exception", "cost_asr_est", "shared_state_unchanged")}, ensure_ascii=False, default=str))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["melos", "negatives", "ja", "z", "a2sec", "zja", "zfail"])
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--stored-primary", action="store_true")
    ap.add_argument("--budget-jpy", type=float, default=0.0)
    a = ap.parse_args()
    os.chdir(ROOT)
    if a.part == "zfail":
        run_zfail(a.execute, a.budget_jpy)
    if a.part == "zja":
        run_zja(a.execute, a.budget_jpy)
    if a.part == "a2sec":
        run_a2sec(a.execute, a.budget_jpy)
    if a.part == "z":
        run_z(a.execute, a.budget_jpy)
    if a.part == "ja":
        run_ja(a.execute, a.budget_jpy)
    if a.part == "negatives":
        run_negatives(a.execute, a.budget_jpy)
    if a.part == "melos":
        run_melos(a.execute, a.budget_jpy, a.stored_primary)


if __name__ == "__main__":
    main()
