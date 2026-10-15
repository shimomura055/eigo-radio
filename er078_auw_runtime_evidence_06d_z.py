# -*- coding: utf-8 -*-
"""AUW 委任_06d: Z 経路の実音声 evidence(Dialogue 外側ループ / KP 英語 4回構成 / 非ラテン KP 救済 / 技術STOP)。
計測・隔離・累計 ledger(JPY 45 上限)は er078_auw_runtime_evidence_06d(→06b)を再利用。有料 API は --execute 指定時のみ。
使い方: .venv\\Scripts\\python.exe er078_auw_runtime_evidence_06d_z.py <part> [--execute --budget-jpy N]
"""
from __future__ import annotations

import argparse
import json
import os

import er078_auw_runtime_evidence_06d as m
from er078_auw_runtime_evidence_06d import begin, finish, _tb, _clip_rows, _line_count, table_from_attempt_history  # noqa: F401


def _z_prep():
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er063_family_z_audio_01 as Z
    return Z


def _run_z(part, level, plan, execute, budget, patch_fn=None, post_fn=None, extra_print=()):
    """plan(ClipSpec 列)を Production の Z.run_tts_stage で実行。patch_fn(res, out) は meter 計測 wrapper 設置後に呼ばれる故障注入/観測 patch(restore 関数を返す)。"""
    out, r77, before, snap0, res, meter, ok = begin(part, budget, execute)
    Z = _z_prep()
    res["plan"] = [{"clip_id": c.clip_id, "kind": c.kind, "level": c.level, "speaker": c.speaker, "text": c.text} for c in plan]
    run_dir = f"{out}/run"
    if ok:
        restore = patch_fn(res, out) if patch_fn else None
        try:
            r = Z.run_tts_stage(run_dir, level, plan)
            res["stage_result"] = {k: r[k] for k in ("results_path", "evidence_path", "statuses")}
        except Exception as e_:  # noqa: BLE001  deferred STOP 等。証拠として種別を残す
            _tb(res, "stage_exception", e_)
        finally:
            if restore:
                restore()
        res["clip_rows"] = _clip_rows(f"{run_dir}/{level}/audit/tts_generation_results.json")
        if post_fn:
            post_fn(res, out, run_dir)
    finish(out, r77, before, snap0, res, meter, extra_print=tuple(extra_print) + ("stage_exception",))


# ---------------------------------------------------------------- ④-a Dialogue(Std) 減速後NG -> 取り直し -> 通算3回(外側ループ)
DLG_TEXT = "I did not see a lower price today."
# "Shops may keep their prices for about nine months."(06b zep の減速前 wav)。減速段階の故障注入にだけ使う別文の実音声。
DLG_DECOY = "er058_output/unified_all_roles_production_wiring_01/evidence_06b/zep/run/a2/narration/full_story_part3_c1_original.wav"


def _dlg_patch(fail_calls, decoy=None):
    decoy = decoy or DLG_DECOY
    def patch(res, out):
        import er008_a2_postprocess_slowdown_01 as sd
        orig = sd.apply_a2_slowdown
        log = []

        def inj(src, dst, *a, **k):
            n = len(log) + 1
            if n in fail_calls:
                # 故障注入(半実音声): 減速段階の出力を「別文の実音声を 6% 減速したもの」に差し替える(= 減速後の再検証で必ず不一致)。
                # TTS・Primary ASR・Secondary(Azure)は実物。
                info = orig(decoy, dst, *a, **k)
                log.append({"call": n, "injected_decoy": True})
                return info
            log.append({"call": n, "injected_decoy": False})
            return orig(src, dst, *a, **k)
        sd.apply_a2_slowdown = inj
        res["slowdown_fault_injection"] = {"fail_calls": sorted(fail_calls), "calls": log, "decoy_wav": decoy}

        def restore():
            sd.apply_a2_slowdown = orig
        return restore
    return patch


def _dlg_post(part):
    def post(res, out, run_dir):
        p = f"{run_dir}/a2/audit/tts_generation_results.json"
        d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        e = (d.get("segments") or {}).get("full_story_part1_c2") or {}
        res["dialogue_entry"] = {k: e.get(k) for k in ("status", "tts_generations_used", "tts_generation_cap_reached", "slowdown_attempts_log", "reason",
                                                         "post_slowdown_classification", "slowdown_applied", "asr_verified")}
        aj = e.get("asr_judgement") or e.get("asr_judgement_post_slowdown_ng") or {}
        res["dialogue_entry"]["final_asr_judgement_state"] = aj.get("state")
        res["attempt_history_rows"] = table_from_attempt_history(part)
    return post


def _dlg_plan(Z):
    return [Z.ClipSpec("full_story_part1_c2", "a2", "dialogue", DLG_TEXT, voice=Z.resolve_dialogue_voice("melos"), speaker="melos",
                       role_key="DIALOGUE_STD", part=1, language="en")]


def run_dlg_recover(execute, budget):
    _run_z("dlg_recover", "a2", _dlg_plan(_z_prep()), execute, budget, _dlg_patch({1}), _dlg_post("dlg_recover"))


def run_dlg_cap(execute, budget):
    _run_z("dlg_cap", "a2", _dlg_plan(_z_prep()), execute, budget, _dlg_patch({1, 2, 3}), _dlg_post("dlg_cap"))


# 数値語を含まない別文(Primary は不一致=保護差ではない通常NG -> Secondary(Azure)1回 -> NG_BOTH の経路を通す)
DLG_DECOY2 = "er058_output/unified_all_roles_production_wiring_01/evidence_06b/zep/run/a2/narration/full_story_part1_c1_original.wav"


def run_dlg_cap2(execute, budget):
    _run_z("dlg_cap2", "a2", _dlg_plan(_z_prep()), execute, budget, _dlg_patch({1, 2, 3}, DLG_DECOY2), _dlg_post("dlg_cap2"))


# ---------------------------------------------------------------- ④-b' KP 英語 phrase 4回構成(Production 関数 generate_key_phrase_component_verified を直接実行。X/legacy A の KP 英語が使う入口)
def run_kp4_leaf(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("kp4_leaf", budget, execute)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    wav = f"{out}/run/a2/narration/kp1_english.wav"      # Review Lock 有効な配置(.../<theme>/<level>/narration/<seg>.wav)
    res["text"] = KP4_TEXT
    if ok:
        import er003_v1_repro01_main_generate as repro01
        import er005_cost_logger as cl
        os.makedirs(os.path.dirname(wav), exist_ok=True)
        cl.install(f"{out}/cost_log_production.jsonl")
        try:
            with cl.segment_context("kp1_english"):
                r = repro01.generate_key_phrase_component_verified(KP4_TEXT, wav, tts_backend="speech_metadata_flash_lite")
            res["result"] = {k: r.get(k) for k in ("status", "reason", "fallback_used", "primary_instruction_type", "human_review_required")}
            res["n_primary_attempts"] = len(r.get("minimal_attempts_log") or [])
            res["n_english_lock_attempts"] = len(r.get("english_lock_attempts_log") or [])
        except Exception as e_:  # noqa: BLE001
            _tb(res, "exception", e_)
        res["attempt_history_rows"] = table_from_attempt_history("kp4_leaf")
        res["review_lock_state"] = json.load(open(f"{out}/run/a2/audit/review_lock_state.json", encoding="utf-8")) if os.path.exists(f"{out}/run/a2/audit/review_lock_state.json") else None
        res["hr_queue_lines"] = _line_count(f"{out}/human_review_queue.jsonl")
    finish(out, r77, before, snap0, res, meter, extra_print=("exception",))


# ---------------------------------------------------------------- ④-b KP 英語 phrase 4回構成(通算上限)の runtime
KP4_TEXT = "Xzqwtrlk wrangle"


def run_kp4(execute, budget):
    Z = _z_prep()
    plan = [Z.ClipSpec("kp1_en", "a2", "kp_en", KP4_TEXT, voice="Aoede", role_key="KP_EN", rank=1, language="en")]

    def post(res, out, run_dir):
        res["attempt_history_rows"] = table_from_attempt_history("kp4")
    _run_z("kp4", "a2", plan, execute, budget, None, post)


# ---------------------------------------------------------------- B(a) 非ラテン KP 救済(Primary に ja ヒントを与え非ラテン転写を誘発。TTS/Primary/Secondary は実物)
NL_CASES = [("kp1_en", "can't wait"), ("kp2_en", "30 percent")]


def _nl_patch(res, out):
    import er006_asr_provider_routing_01 as routing
    orig = routing.transcribe
    seen = {}
    log = []

    def tr(wav_path, language, timeout_seconds=90.0, prompt=None):
        # KP 英語 leaf の最初の Primary 呼出だけ language='ja'(prompt なし)で実 OpenAI を呼び、非ラテン(日本語)転写を誘発する。2 回目以降は通常。
        if language.lower().startswith("en") and prompt and wav_path not in seen:
            seen[wav_path] = 1
            route = routing.require_asr_route("ja-JP")
            text, err = routing._transcribe_openai_mini(wav_path, "ja-JP", route["model"], prompt=None)
            log.append({"wav": os.path.basename(wav_path), "forced_language_hint": "ja", "primary_text": text, "error": err})
            return text, err
        return orig(wav_path, language, timeout_seconds=timeout_seconds, prompt=prompt)
    routing.transcribe = tr
    res["primary_language_hint_injection"] = log

    def restore():
        routing.transcribe = orig
    return restore


def run_nlkp(execute, budget):
    Z = _z_prep()
    plan = [Z.ClipSpec(cid, "a2", "kp_en", t, voice="Aoede", role_key="KP_EN", rank=i + 1, language="en") for i, (cid, t) in enumerate(NL_CASES)]

    def post(res, out, run_dir):
        res["attempt_history_rows"] = table_from_attempt_history("nlkp")
    _run_z("nlkp", "a2", plan, execute, budget, _nl_patch, post)


# ---------------------------------------------------------------- B(d) 技術STOP(Secondary を mock 障害化、実 TTS/実 Primary で最終 slot まで到達)
TS_TEXTS = ["Mayor Xzqwtrlk said the new bridge would open in May.",
            "Mayor Qvxzmtk said the old road would close in June.",
            "Mayor Wzrqplk said the small park would open in July."]


def _ts_patch(res, out):
    import er006_secondary_asr_01 as sec
    orig = sec.get_full_text_via_azure_stt_with_phrase_list
    calls = []

    def down(wav, *a, **k):
        calls.append(os.path.basename(wav))
        return None, "mock Secondary(Azure) outage (06d fault injection)"
    sec.get_full_text_via_azure_stt_with_phrase_list = down
    res["secondary_fault_injection"] = {"mock_calls": calls, "note": "Secondary(Azure)のみ mock 障害。TTS・Primary ASR は実物"}

    def restore():
        sec.get_full_text_via_azure_stt_with_phrase_list = orig
    return restore


def _ts_post(res, out, run_dir):
    p = f"{run_dir}/b1b/audit/tts_generation_results.json"
    d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    res["entries"] = {cid: {k: e.get(k) for k in ("status", "technical_stop_status", "technical_stop", "human_review_required", "restartable",
                                                   "approval_required", "reason")}
                      for cid, e in (d.get("segments") or {}).items()}
    lock = f"{run_dir}/b1b/audit/review_lock_state.json"
    res["review_lock_state"] = json.load(open(lock, encoding="utf-8")) if os.path.exists(lock) else None
    res["hr_queue_lines"] = _line_count(f"{out}/human_review_queue.jsonl")
    res["attempt_history_rows"] = table_from_attempt_history("tstop")


def run_tstop(execute, budget):
    Z = _z_prep()
    plan = [Z.ClipSpec(f"comment_{i + 1}", "b1b", "comment", t, voice="Charon", role_key="ADV_EN_COMMENT", language="en") for i, t in enumerate(TS_TEXTS)]
    _run_z("tstop", "b1b", plan, execute, budget, _ts_patch, _ts_post)


# ---------------------------------------------------------------- B(a) probe: 実 Primary に言語ヒントを与えて否定入り phrase の非ラテン転写を得られるか(各 1 呼出、実費は Meter 記録)
def run_probe_nl(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("probe_nl", budget, execute)
    wav = f"{m.EV}/nlkp/run/a2/narration/kp1_en.wav"   # nlkp で実 TTS 済みの "can't wait"
    res["wav"] = wav
    rows = []
    if ok:
        import er006_asr_provider_routing_01 as routing
        model = routing.require_asr_route("en-US")["model"]
        for hint in ("zh-CN", "ko-KR", "ru-RU", "ar-SA"):
            text, err = routing._transcribe_openai_mini(wav, hint, model, prompt=None)
            rows.append({"hint": hint, "text": text, "error": err})
    res["rows"] = rows
    finish(out, r77, before, snap0, res, meter)


# ---------------------------------------------------------------- B(a) 非ラテン KP 救済: 否定/数値(半実音声)
# 実 Primary は否定入り英語 phrase を非ラテンで転写しなかった(probe_nl: 言語ヒント zh/ko/ru/ar でも "Can't wait!")ため、
# 実 TTS 音声 + 実 Azure(Secondary) に、典型的な非ラテン Primary 転写(保存例、日本語)を与えて現行 adapter を実行する(半実音声)。
NL_PRIMARY_TEXTS = {"neg_ok": "待ちきれない三日間", "neg_diff": "待てる三日間", "val_diff": "待ちきれない四日間"}
NLNEG_CASES = [  # (case, spoken(TTS に読ませる), canonical, expected)
    ("neg_ok", "I can't wait for 3 days.", "I can't wait for 3 days.", "PASS_WITH_WARNING"),
    ("neg_diff", "I can wait for 3 days.", "I can't wait for 3 days.", "NG_PROTECTED"),
    ("val_diff", "I can't wait for 4 days.", "I can't wait for 3 days.", "NG_PROTECTED"),
]


def run_nlneg(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("nlneg", budget, execute)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    rows = []
    if ok:
        import er003_v1_repro01_main_generate as repro01
        import er006_secondary_asr_01 as sec
        os.makedirs(f"{out}/audio", exist_ok=True)
        for case, spoken, canon, expected in NLNEG_CASES:
            wav = f"{out}/audio/{case}.wav"      # Review Lock 配置外(bypass)。音声生成のみが目的
            try:
                r = repro01.generate_narration_snippet_verified_strict(spoken, "en", wav, spoken, max_attempts=1, max_extra_chars=10,
                                                                       safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
                                                                       asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT,
                                                                       enable_non_latin_cascade=True, tts_backend="speech_metadata_flash_lite")
                sec.reset_secondary_cache()
                d = sec.evaluate_attempt_with_cascade_detail(canon, NL_PRIMARY_TEXTS[case], [], wav, language="en-US", cascade_enabled=True,
                                                             enable_non_latin_cascade=True, attempt_ctx={"slot": 1, "script_version": "v0", "is_last_slot": False})
                j = d.get("asr_judgement") or {}
                rows.append({"case": case, "spoken_tts_text": spoken, "canonical": canon, "tts_status": r.get("status"), "tts_leaf_asr_text": r.get("asr_text"),
                             "injected_primary_text": NL_PRIMARY_TEXTS[case], "azure_text": (j.get("secondary") or {}).get("text"),
                             "adopted_text": (j.get("primary") or {}).get("adopted_text"), "state": j.get("state"), "reason": j.get("reason_code"),
                             "verified": d.get("verified"), "layers": (j.get("adapter") or {}).get("layers"),
                             "final_gate": j.get("final_gate"), "expected": expected, "as_expected": j.get("state") == expected})
            except Exception as e_:  # noqa: BLE001
                rows.append({"case": case, "error": f"{type(e_).__name__}: {str(e_)[:300]}"})
    res["rows"] = rows
    finish(out, r77, before, snap0, res, meter)


# ---------------------------------------------------------------- B(e) 試聴リスト導出失敗の表示(API 0): 06b zep2 の実 run に対し、registry の導出を失敗させて最終ページを再生成
def run_derive(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("derive", budget, execute)
    run_dir = "er058_output/unified_all_roles_production_wiring_01/evidence_06b/zep2/run"   # 実音声 run(読取のみ)
    res["source_run"] = run_dir
    if execute:
        import io
        import contextlib
        import er078_pass_with_warning_registry_01 as pww
        import er063_family_z_audio_01 as Z
        orig = pww.derive_listening_list
        res["derive_calls"] = 0

        def failing_derive(doc):
            res["derive_calls"] += 1
            raise RuntimeError("simulated registry derivation failure (06d fault injection)")
        pww.derive_listening_list = failing_derive
        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err):
                pages = Z.build_pages(run_dir, pages_dir=f"{out}/pages_fail")
            res["pages_fail"] = {k: v.get("page") for k, v in pages.items()}
        except Exception as e_:  # noqa: BLE001
            _tb(res, "exception", e_)
        finally:
            pww.derive_listening_list = orig
        res["stderr_warn"] = err.getvalue()[:600]
        for fname in ("standard.html", "advanced.html", "index.html"):
            path = f"{out}/pages_fail/{fname}"
            if os.path.exists(path):
                html = open(path, encoding="utf-8").read()
                res.setdefault("page_check", {})[fname] = {"has_derivation_failed_label": "導出失敗(要確認)" in html, "has_zero_label": "0件(該当なし" in html}
        # 対照: 失敗を注入しない通常 build(同じ run)では「導出失敗」が出ないこと
        pages2 = Z.build_pages(run_dir, pages_dir=f"{out}/pages_ok")
        for fname in ("standard.html", "advanced.html"):
            html = open(f"{out}/pages_ok/{fname}", encoding="utf-8").read()
            res.setdefault("page_check_control", {})[fname] = {"has_derivation_failed_label": "導出失敗(要確認)" in html, "has_zero_label": "0件(該当なし" in html}
    finish(out, r77, before, snap0, res, meter, extra_print=("page_check", "page_check_control", "exception"))


# ---------------------------------------------------------------- C 再利用経路の実動作(Z の results cache からの再利用): DIFF -> 再生成(実 TTS 1 clip) / EQUAL -> 再利用+asr_judgement_inherited(API 0)
HANSHIN_RES = "er003_output/n3_01/hanshin/a2/audit/tts_generation_results.json"   # reuse_blocklist.json の DIFF 16 件の 1 つ(topic_intro: 8-1 -> ASR "81")
ZEP_SRC = "er058_output/unified_all_roles_production_wiring_01/evidence_06b/zep"


def run_reuse(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("reuse", budget, execute)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import shutil
    import hashlib
    import er063_family_z_audio_01 as Z
    import er078_auw_runtime_evidence_06b as b6
    _, _, zplan = b6.zep_plan("a2")
    zspec = {s.clip_id: s for s in zplan}
    run_dir = f"{out}/run"
    narr = f"{run_dir}/a2/narration"
    os.makedirs(narr, exist_ok=True)
    os.makedirs(f"{run_dir}/a2/audit", exist_ok=True)
    zres = json.load(open(f"{ZEP_SRC}/run/a2/audit/tts_generation_results.json", encoding="utf-8"))
    segs = {}
    # (1) EQUAL 側: 06b zep の実音声 clip(full_story_part2_c1。保存 asr_judgement あり)をそのまま cache に置く
    eq_id = "full_story_part2_c1"
    shutil.copyfile(f"{ZEP_SRC}/run/a2/narration/{eq_id}.wav", f"{narr}/{eq_id}.wav")
    segs[eq_id] = zres["segments"][eq_id]
    # (2) DIFF 側: blocklist の hanshin topic_intro(保存 ASR "Hanshin wins 81" vs 原稿 "8-1")。再利用キーを現行 spec の key に合わせ、
    #     「現行 runner なら再利用される状態」を意図的に作る(guard が無ければ再利用される)。
    hres = json.load(open(HANSHIN_RES, encoding="utf-8"))
    he = dict(hres["segments"]["topic_intro"])
    tid = "topic_intro_en"
    canon = he["canonical_text"]
    spec_t = Z.ClipSpec(tid, "a2", "topic_intro", canon, voice="Aoede", role_key="TOPIC_INTRO_EN", language="en")
    shutil.copyfile(he["path"], f"{narr}/{tid}.wav")
    he["reuse_key"] = Z.build_reuse_key(spec_t)
    he["sha256"] = hashlib.sha256(open(f"{narr}/{tid}.wav", "rb").read()).hexdigest()
    he["status"] = "OK"
    segs[tid] = he
    doc = {k: v for k, v in zres.items() if k not in ("segments", "key_phrases")}
    doc.update({"segments": segs, "key_phrases": {}})
    json.dump(doc, open(f"{run_dir}/a2/audit/tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    shutil.copyfile(f"{ZEP_SRC}/run/a2/audit/narrator_style_record.json", f"{run_dir}/a2/audit/narrator_style_record.json")
    plan = [zspec[eq_id], spec_t]
    res["plan"] = [{"clip_id": c.clip_id, "kind": c.kind, "text": c.text} for c in plan]
    res["cache_entries_before"] = {eq_id: {"asr_text": segs[eq_id].get("asr_text"), "has_asr_judgement": bool(segs[eq_id].get("asr_judgement"))},
                                   tid: {"canonical_text": canon, "stored_asr_text": he.get("asr_text"), "source": HANSHIN_RES + "#/segments/topic_intro"}}
    if ok:
        try:
            r = Z.run_tts_stage(run_dir, "a2", plan)
            res["stage_result"] = {k: r[k] for k in ("results_path", "statuses")}
        except Exception as e_:  # noqa: BLE001
            _tb(res, "stage_exception", e_)
        d = json.load(open(f"{run_dir}/a2/audit/tts_generation_results.json", encoding="utf-8"))
        ent = d.get("segments") or {}
        res["entries_after"] = {cid: {"status": e.get("status"), "reused_from_previous_run": e.get("reused_from_previous_run"),
                                      "has_asr_judgement_inherited": bool(e.get("asr_judgement_inherited")),
                                      "inherited_state": (e.get("asr_judgement_inherited") or {}).get("state"),
                                      "reuse_value_guard_blocked_previous": e.get("reuse_value_guard_blocked_previous"),
                                      "new_asr_text": e.get("asr_text"), "has_asr_judgement": bool(e.get("asr_judgement")),
                                      "state": (e.get("asr_judgement") or {}).get("state")} for cid, e in ent.items()}
        res["attempt_history_rows"] = table_from_attempt_history("reuse") if os.path.exists(f"{m.EV}/reuse/attempt_history.jsonl") else []
    finish(out, r77, before, snap0, res, meter, extra_print=("stage_exception",))


PARTS = {"reuse": run_reuse, "derive": run_derive, "dlg_cap2": run_dlg_cap2, "kp4_leaf": run_kp4_leaf, "nlneg": run_nlneg, "probe_nl": run_probe_nl, "dlg_recover": run_dlg_recover, "dlg_cap": run_dlg_cap, "kp4": run_kp4, "nlkp": run_nlkp, "tstop": run_tstop}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=sorted(PARTS))
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--budget-jpy", type=float, default=0.0)
    a = ap.parse_args()
    os.chdir(m.ROOT)
    PARTS[a.part](a.execute, a.budget_jpy)


if __name__ == "__main__":
    main()
