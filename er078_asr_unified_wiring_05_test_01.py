# AUW 委任_05: A2減速後判定(J7)の統一judge化 / Dialogue到達 / KP解説3回化(OF-AUW-12) / runner共有cache+circuit breaker /
# is_last_slot・attempt_ctx配線(HR queueは最終slotのNGのみ) / Family B・C hook / 静的監査(deferred 0・pending 0)のtest。
# 全てmock(Primary=routing.transcribe, Secondary=get_full_text_via_azure_stt_with_phrase_list / _azure_stt_strict, TTS=p9a/common)。
# API呼出0・費用JPY0。HR queue/リストの書込先は全てtmp_pathへ退避(リポジトリのqueue/artifactを汚さない)。
import ast
import hashlib
import inspect
import json
import os
import unittest.mock as mock
import wave

import numpy as np
import pytest

import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as sec
import er007_ja_secondary_asr_01 as ja
import er011_human_review_lock_01 as review_lock
import er078_asr_unified_attempt_ctx_01 as actx
import er078_asr_unified_judge_01 as uj
import er078_asr_unified_wiring_static_audit_01 as audit
import er078_pass_with_warning_registry_01 as reg
import er078_secondary_run_scope_01 as scope

ROOT = os.path.dirname(os.path.abspath(__file__))
CANON = "The quick brown fox jumps over the lazy dog."
WRONG = "The quick brown fox jumps over the lazy cat."     # 内容語1語のみ違う(TRUE_CONTENT_MISMATCH、保護差=数値/否定なし)


class Az:
    """Secondary(Azure)のmock。callsは実呼出回数。"""

    def __init__(self, result=(None, "no result"), raises=None):
        self.result, self.raises, self.calls = result, raises, 0

    def __call__(self, wav_path, language="en-US", phrases=None, **kw):
        self.calls += 1
        if self.raises:
            raise self.raises
        return self.result


class AzJa:
    def __init__(self, result=(None, "no result")):
        self.result, self.calls = result, 0

    def __call__(self, wav_path, language="ja-JP", timeout_seconds=90.0):
        self.calls += 1
        return self.result


def _wav(tmp_path, name="a.wav", seconds=1, rate=8000, fill=b"\x00"):
    p = tmp_path / name
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(rate)
        w.writeframes(fill * (rate * seconds))
    return str(p)


@pytest.fixture(autouse=True)
def _iso(monkeypatch, tmp_path):
    sec.reset_secondary_cache()
    sec._reset_m1_freeze_cache()
    monkeypatch.setattr(sec, "_RUN_STATE", None)
    monkeypatch.setattr(sec, "_RUN_CACHE", None)
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: {})            # ledger.json(作業ツリー差分)依存を排除
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda *a, **k: None)   # Perplexity研究呼出=課金を遮断
    monkeypatch.setattr(sec.semantic_equivalence, "append_telemetry_log", lambda *a, **k: None)
    monkeypatch.setattr(sec, "HUMAN_REVIEW_LOG_PATH", str(tmp_path / "hrq_en.jsonl"))
    monkeypatch.setattr(ja, "HUMAN_REVIEW_LOG_PATH_JA", str(tmp_path / "hrq_ja.jsonl"))
    monkeypatch.setattr(review_lock, "save_tts_attempt_audio", lambda *a, **k: "saved.wav")
    monkeypatch.setattr(review_lock, "append_attempt_history_event", lambda *a, **k: None)
    monkeypatch.setattr(ja.javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False, raising=False)   # LLM=課金0
    yield
    sec.reset_secondary_cache()


# ============================================================
# A. A2減速後判定(J7)の統一judge化
# ============================================================
def _fake_stretch(src, dst):
    with open(dst, "wb") as f:
        f.write(b"POST_STRETCHED_" + os.path.basename(dst).encode())
    return {"src_duration_seconds": 2.0, "dst_duration_seconds": 2.12}


def _slowdown(tmp_path, monkeypatch, canonical, primary, az, *, result=None, name="full_story_part1_c1", **kw):
    import er003_v1_n3_01_tts_generate as tg
    out = tmp_path / f"{name}.wav"
    out.write_bytes(b"PRE")
    result = result if result is not None else {"status": "OK", "sha256": None, "duration_seconds": 2.0}
    monkeypatch.setattr(tg.a2_slowdown, "apply_a2_slowdown", _fake_stretch)
    monkeypatch.setattr(tg.routing, "transcribe", lambda *a, **k: (primary, None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    return tg.apply_a2_slowdown_postprocess(name, str(tmp_path), canonical, result, **kw)


def test_j7_primary_pass_never_calls_secondary(tmp_path, monkeypatch):
    az = Az((CANON, None))
    r = _slowdown(tmp_path, monkeypatch, CANON, CANON, az)
    assert r["status"] == "OK" and r["asr_verified"] is True and az.calls == 0
    assert r["asr_judgement"]["state"] == uj.PASS and "post_slowdown_cascade" not in r
    assert r["post_slowdown_final_classification"]


def test_j7_primary_ng_secondary_pass_is_pass_with_warning_one_call_and_pre_slowdown_record_kept(tmp_path, monkeypatch):
    az = Az((CANON, None))
    pre = {"state": "PASS", "marker": "pre_slowdown_record"}
    r = _slowdown(tmp_path, monkeypatch, CANON, WRONG, az,
                  result={"status": "OK", "sha256": "stale", "duration_seconds": 2.0, "asr_judgement": pre})
    assert r["status"] == "OK" and r["asr_verified"] is True and az.calls == 1
    assert r["asr_judgement"]["state"] == uj.PASS_WITH_WARNING and uj.W_SECONDARY_CONFIRMED in r["asr_judgement"]["warnings"]
    assert r["asr_judgement_pre_slowdown"] == pre                      # 減速前(内側)の判定recordを退避
    assert r["post_slowdown_classification"] == "TRUE_CONTENT_MISMATCH"   # Primary層の判定は不変
    assert r["post_slowdown_cascade_accepted"] is True and r["post_slowdown_cascade"]["verified"] is True
    assert r["slowdown_applied"] is True and r["original_path"].endswith("_original.wav")
    # 6%減速の中身(比率)は不変
    assert r["duration_seconds"] == round(2.0 * 2.12 / 2.0, 3)


def test_j7_secondary_ng_both_stays_stopped_and_unavailable_fails_closed(tmp_path, monkeypatch):
    r = _slowdown(tmp_path, monkeypatch, CANON, WRONG, Az((WRONG, None)))
    assert r["status"] == "STOPPED" and r["asr_verified"] is False
    r2 = _slowdown(tmp_path, monkeypatch, CANON, WRONG, Az((None, "boom")))
    assert r2["status"] == "STOPPED" and r2["asr_verified"] is False                      # Secondary障害はPASS扱いにしない
    assert r2["asr_judgement_post_slowdown_ng"]["state"] == uj.NG_SECONDARY_UNAVAILABLE


def test_j7_value_and_negation_protected_diffs_not_rescued_by_secondary(tmp_path, monkeypatch):
    az = Az(("Melos waited three days.", None))
    r = _slowdown(tmp_path, monkeypatch, "Melos waited three days.", "Melos waited five days.", az)
    assert r["status"] == "STOPPED" and az.calls == 0
    assert r["asr_judgement_post_slowdown_ng"]["state"] == uj.NG_PROTECTED
    az2 = Az(("He did not go home.", None))
    r2 = _slowdown(tmp_path, monkeypatch, "He did not go home.", "He did go home.", az2)
    assert r2["status"] == "STOPPED" and az2.calls == 0


def test_j7_same_wav_secondary_duplicate_zero_within_run_scope(tmp_path, monkeypatch):
    import er003_v1_n3_01_tts_generate as tg
    wav = _wav(tmp_path)
    az = Az((CANON, None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    sec.begin_secondary_run()
    try:
        d1 = tg._post_slowdown_unified_judge({}, CANON, WRONG, wav, "full_story_part1_c1", True)
        d2 = tg._post_slowdown_unified_judge({}, CANON, WRONG, wav, "full_story_part1_c1", True)
    finally:
        sec.end_secondary_run()
    assert d1["verified"] and d2["verified"] and az.calls == 1          # run内の同一wav: Secondary実呼出1回
    az2 = Az((CANON, None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az2)
    tg._post_slowdown_unified_judge({}, CANON, WRONG, wav, "full_story_part1_c1", True)
    tg._post_slowdown_unified_judge({}, CANON, WRONG, wav, "full_story_part1_c1", True)
    assert az2.calls == 2                                               # 対照: scope外は呼出単位cache(従来どおり)


def test_j7_ledger_failure_does_not_block_primary_and_exception_is_fail_closed(tmp_path, monkeypatch):
    import er006_pronunciation_ledger_01 as pl
    monkeypatch.setattr(pl, "get_hint_for_text", lambda *a, **k: (_ for _ in ()).throw(OSError("ledger io")))
    r = _slowdown(tmp_path, monkeypatch, CANON, CANON, Az())
    assert r["status"] == "OK"                                           # Primary PASSはledger障害の影響を受けない
    monkeypatch.undo()


def test_j7_adapter_exception_fail_closed_and_misconfig_propagates(tmp_path, monkeypatch):
    import er003_v1_n3_01_tts_generate as tg
    monkeypatch.setattr(sec, "evaluate_attempt_with_cascade_detail", mock.Mock(side_effect=ConnectionError("net")))
    r = _slowdown(tmp_path, monkeypatch, CANON, WRONG, Az())
    assert r["status"] == "STOPPED" and r["post_slowdown_cascade"]["aborted_by_exception"] is True
    monkeypatch.setattr(sec, "evaluate_attempt_with_cascade_detail", mock.Mock(side_effect=RuntimeError("init_logger()が呼ばれていません")))
    with pytest.raises(RuntimeError):
        _slowdown(tmp_path, monkeypatch, CANON, WRONG, Az())


def test_j7_is_last_slot_passed_to_adapter_by_outer_loop_budget(tmp_path, monkeypatch):
    import er003_v1_n3_01_tts_generate as tg
    seen = []

    def spy_pp(name, narration_dir, text, result, is_last_slot=True, **kw):
        seen.append(is_last_slot)
        return {"status": "STOPPED", "reason": "x"}

    monkeypatch.setattr(tg.c, "generate_english_segment_with_fallback",
                        lambda *a, **k: {"status": "OK", "attempts_log": [{"attempt": 1}]})
    monkeypatch.setattr(tg, "apply_a2_slowdown_postprocess", spy_pp)
    tg.generate_a2_segment_with_slowdown("t", str(tmp_path / "seg.wav").replace("\\", "/"), "t")
    assert seen == [False, False, True]          # 通算TTS 1,2回目は後続slotあり=False、3回目(予算尽き)のみ最終slot=True
    # 既定(外側ループのない呼出元: Dialogue/B Voices)は減速後NG=最終
    assert inspect.signature(tg.apply_a2_slowdown_postprocess).parameters["is_last_slot"].default is True


def test_j7_pww_after_slowdown_appears_in_listening_list_with_post_slowdown_sha(tmp_path, monkeypatch):
    az = Az((CANON, None))
    run_dir = tmp_path / "wiring_theme_auw5" / "a2"
    narr = run_dir / "narration"
    narr.mkdir(parents=True)
    r = _slowdown(narr, monkeypatch, CANON, WRONG, az, result={"status": "OK", "sha256": "stale", "duration_seconds": 2.0,
                                                            "text": CANON, "path": str(narr / "full_story_part1_c1.wav")})
    assert r["asr_judgement"]["state"] == uj.PASS_WITH_WARNING
    final_sha = hashlib.sha256((narr / "full_story_part1_c1.wav").read_bytes()).hexdigest()
    assert r["sha256"] == final_sha                                       # 減速後wavのsha256に更新済み
    (run_dir / "audit").mkdir()
    (run_dir / "audit" / "tts_generation_results.json").write_text(
        json.dumps({"segments": {"full_story_part1_c1": dict(r, language="en")}}, ensure_ascii=False, default=str), encoding="utf-8")
    rep = reg.write_listening_list_safe(str(run_dir), standalone_html=True)      # 生成完了hookと同じ関数
    assert rep["error"] is None and rep["count"] == 1
    e = json.load(open(rep["json"], encoding="utf-8"))["entries"][0]
    assert e["segment_id"] == "full_story_part1_c1" and uj.W_SECONDARY_CONFIRMED in e["warning_labels"]
    assert e["primary_text"] == WRONG and e["secondary_text"] == CANON
    assert "事後試聴リスト(PASS_WITH_WARNING)" in open(rep["html"], encoding="utf-8").read()


def test_static_audit_deferred_zero_pending_zero_and_a2_entries_unified():
    assert audit.A2_PENDING_ENTRIES == [] and audit.PENDING_DELEGATION_05_CATEGORIES == ()
    assert audit.CAT_A2_DEFERRED not in audit.ALLOWED_CATEGORIES
    al = audit.load_allowlist()
    assert al["phase"] == "post_wiring"
    assert [e for e in al["entries"] if e["category"] in audit.DEFERRED_CATEGORIES + (audit.CAT_A2_DEFERRED,)] == []
    inv = audit.inventory()
    mod = "er003_v1_n3_01_tts_generate"
    assert (mod, "apply_a2_slowdown_postprocess", "en_validator.classify_asr_match") not in inv     # 直接判定は撤去
    assert (mod, "apply_a2_slowdown_postprocess", "routing.transcribe") in inv                      # Primary転写の取得のみ残る
    assert (mod, "_post_slowdown_unified_judge", "secondary_asr.evaluate_attempt_with_cascade_detail") in inv
    cats = {(e["function"], e["callee"]): e["category"] for e in al["entries"] if e["module"] == mod}
    assert cats[("apply_a2_slowdown_postprocess", "routing.transcribe")] == audit.CAT_PRIMARY_ACQUISITION
    assert cats[("_post_slowdown_unified_judge", "secondary_asr.evaluate_attempt_with_cascade_detail")] == audit.CAT_EN_ADAPTER_ENTRY


# ============================================================
# B. Dialogue(er063 / Family Z): 固有例外を維持したまま統一judge(J4+J7 / EN adapter)へ到達
# ============================================================
def _z_gens(monkeypatch):
    import er063_family_z_audio_01 as z
    monkeypatch.setattr(z, "_check_stop_sentinel", lambda *a, **k: None)
    return z, z.real_generators()


def test_dialogue_std_reaches_unified_judge_via_j4_and_j7_with_prompt_unchanged(tmp_path, monkeypatch):
    import er003_v1_n3_01_tts_generate as n3
    import er012_b_family_voices_production_01 as bv
    z, gens = _z_gens(monkeypatch)
    narr = tmp_path / "melos" / "run_01" / "a2" / "narration"
    narr.mkdir(parents=True)
    spec = z.ClipSpec("full_story_part1_c2", "a2", "dialogue", CANON, voice="Puck", speaker="king", role_key="")
    out_path = str(narr / "full_story_part1_c2.wav").replace("\\", "/")
    captured = {}
    inner_judgement = {"state": "PASS", "marker": "voice_body_inner"}

    def fake_voice_body(text, op, voice, **kw):
        captured.update(voice=voice, kw=kw)
        with open(op, "wb") as f:
            f.write(b"PRE")
        return {"status": "OK", "path": op, "voice": voice, "asr_judgement": inner_judgement, "sha256": "stale", "duration_seconds": 2.0}

    monkeypatch.setattr(bv, "generate_voice_body_wide_margin", fake_voice_body)
    monkeypatch.setattr(n3.a2_slowdown, "apply_a2_slowdown", _fake_stretch)
    monkeypatch.setattr(n3.routing, "transcribe", lambda *a, **k: (WRONG, None))
    az = Az((z.n3_tts.tts_safe_news_en(CANON) if hasattr(z, "n3_tts") else CANON, None))
    # Secondaryは原稿(normalizer後)を返す
    import er063_family_z_audio_01 as z2
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list",
                        Az((n3.tts_safe_news_en(CANON), None)))
    r = gens["dialogue"](spec, out_path)
    # Dialogue固有のPrompt/Voice不変。委任_06c(OF-AUW-C-08)で外側ループ化: 初回のmax_attempts=通算予算3(残予算)が追加される。
    assert captured["voice"] == "Puck" and captured["kw"] == {"max_attempts": 3}  # 2026-10-19 決定③: Z Std Dialogueは生成時Style override無し(Adv同一)
    assert r["status"] == "OK" and r["slowdown_applied"] is True
    assert r["asr_judgement"]["state"] == uj.PASS_WITH_WARNING            # J7(減速後)が統一judge経由でWARNING
    assert r["asr_judgement_pre_slowdown"] == inner_judgement             # J4(減速前)のrecordは退避
    assert z2 is z


def test_dialogue_adv_has_no_slowdown_and_no_style_override(tmp_path, monkeypatch):
    import er012_b_family_voices_production_01 as bv
    z, gens = _z_gens(monkeypatch)
    spec = z.ClipSpec("full_story_part1_c2", "b1b", "dialogue", CANON, voice="Puck", speaker="king")
    calls = []
    monkeypatch.setattr(bv, "generate_voice_body_wide_margin", lambda text, op, voice, **kw: calls.append((voice, kw)) or {"status": "OK"})
    r = gens["dialogue"](spec, str(tmp_path / "x.wav"))
    assert r == {"status": "OK"} and calls == [("Puck", {})]               # style_prefix_overrideを渡さない・減速なし(固有例外)


def test_dialogue_and_ja_paths_statically_reach_adapters_through_z_entrypoint():
    reach = audit.reachable_modules()
    assert {"er006_secondary_asr_01", "er007_ja_secondary_asr_01", "er078_asr_unified_judge_01"} <= set(reach)
    z_closure = audit._closure("er063_family_z_audio_01")
    assert {"er012_b_family_voices_production_01", "er003_v1_n3_01_tts_generate", "er006_secondary_asr_01"} <= z_closure
    src = inspect.getsource(__import__("er063_family_z_audio_01").real_generators)
    # 委任_06c(OF-AUW-C-08): Dialogue(Std)の減速後判定は外側ループ(generate_with_a2_slowdown_outer_loop)経由。その内部でJ7を呼ぶ。
    assert "bvoices.generate_voice_body_wide_margin" in src and "n3_tts.generate_with_a2_slowdown_outer_loop" in src
    assert "apply_a2_slowdown_postprocess" in inspect.getsource(__import__("er003_v1_n3_01_tts_generate").generate_with_a2_slowdown_outer_loop)
    # leaf側(J4)・減速後(J7)ともadapter入口を持つ(EN adapter経由)
    al = audit.load_allowlist()
    assert any(e["module"] == "er012_b_family_voices_production_01" and e["category"] == audit.CAT_EN_ADAPTER_ENTRY for e in al["entries"])
    assert any(e["module"] == "er003_v1_n3_01_tts_generate" and e["function"] == "_post_slowdown_unified_judge"
               and e["category"] == audit.CAT_EN_ADAPTER_ENTRY for e in al["entries"])


# ============================================================
# C. KP解説 3回化(OF-AUW-12)
# ============================================================
def test_kp_explanation_attempts_is_three_and_other_kp_counts_unchanged():
    import er003_v1_repro01_main_generate as r1
    import er019_family_x_audio_production_runner_01 as x
    assert x.KP_EXPLANATION_MAX_ATTEMPTS == 3 == review_lock.PRODUCTION_MAX_TTS_ATTEMPTS
    assert (r1.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS, r1.KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS, r1.KEY_PHRASE_TOTAL_MAX_ATTEMPTS) == (2, 2, 4)
    body = inspect.getsource(x.generate_key_phrase_explanation_en_verified)
    assert "max_attempts=KP_EXPLANATION_MAX_ATTEMPTS" in body and "max_attempts=2," not in body


def test_kp_explanation_call_arguments_only_count_changed(monkeypatch):
    import er003_v1_repro01_main_generate as r1
    import er019_family_x_audio_production_runner_01 as x
    captured = {}
    monkeypatch.setattr(r1, "generate_narration_snippet_verified_strict", lambda *a, **k: captured.update(args=a, kw=k) or {"status": "OK"})
    x.generate_key_phrase_explanation_en_verified("Run through means to cover quickly.", "k.wav", "STYLE", tts_backend="structured_separation")
    kw = captured["kw"]
    assert kw["max_attempts"] == 3
    assert kw["safety_margin_seconds"] == r1.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS and kw["style_prefix_override"] == "STYLE"
    assert kw["disfluency_qa"] is True and kw["enable_non_latin_cascade"] is True
    assert kw["asr_prompt"] == r1.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT and kw["tts_backend"] == "structured_separation"
    assert captured["args"][1] == "en"


def test_z_kp_expl_en_uses_same_function_and_three_attempts(monkeypatch):
    import er019_family_x_audio_production_runner_01 as x
    z, gens = _z_gens(monkeypatch)
    seen = {}
    monkeypatch.setattr(x, "generate_key_phrase_explanation_en_verified", lambda text, op, style_prefix_override, tts_backend: seen.update(t=text) or {"status": "OK"})
    spec = z.ClipSpec("kp1_explanation_en", "b1b", "kp_expl_en", "Explain.", voice="Aoede", role_key="KP_EXPL_EN")
    assert gens["kp_expl_en"](spec, "x.wav") == {"status": "OK"} and seen["t"] == "Explain."


def _patch_repro01_leaf(monkeypatch, tmp_path, *, asr_text, az, tts_counter):
    """repro01.generate_narration_snippet_verified_strict用のmock一式(TTS=p9a, Primary=routing, Secondary=Azure)。"""
    import er003_v1_repro01_main_generate as r1
    import er002_common as common

    def fake_tts(text, language, out_path, **kw):
        tts_counter.append(1)
        common.write_wav_float(out_path, np.zeros(8000, dtype=np.float32), common.SAMPLE_RATE, 1)
        return {"status": "OK", "duration_seconds": 1.0, "path": out_path, "sha256": "x"}

    monkeypatch.setattr(r1.p9a, "generate_narration_snippet", fake_tts)
    monkeypatch.setattr(r1.batch_wiring, "make_batch_tts_call_fn", lambda *a, **k: None)
    monkeypatch.setattr(r1.routing, "transcribe", lambda *a, **k: (asr_text, None))
    monkeypatch.setattr(r1.pron_resolver_core, "resolve_and_augment_en_style_prefix", lambda base, text: (base, {"hints_applied": False}))
    monkeypatch.setattr(r1.pronun_ledger, "get_hint_for_text", lambda *a, **k: [])
    monkeypatch.setattr(r1.dq18, "apply_disfluency_gate", lambda v, p, language="en", enabled=False: {"verified": v, "disfluency_checked": False, "disfluency_evidence": None})
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    return r1


def _hr_slots(monkeypatch, module, name="_log_human_review"):
    slots = []

    def spy(detail):
        slots.append((detail["asr_judgement"]["slot"], detail["asr_judgement"]["state"]))
    monkeypatch.setattr(module, name, spy)
    return slots


def test_kp_explanation_makes_three_tts_attempts_and_queues_hr_only_at_slot_three(tmp_path, monkeypatch):
    import er019_family_x_audio_production_runner_01 as x
    n = []
    r1 = _patch_repro01_leaf(monkeypatch, tmp_path, asr_text=WRONG, az=Az((WRONG, None)), tts_counter=n)
    slots = _hr_slots(monkeypatch, sec)
    monkeypatch.setattr(r1.repetition_qa, "apply_repetition_qa_gate", lambda v, *a, **k: {"verified": v, "repetition_qa_checked": False})
    r = x.generate_key_phrase_explanation_en_verified(CANON, str(tmp_path / "kp1_explanation_en.wav"), "STYLE")
    assert r["status"] == "STOPPED" and len(n) == 3                       # 旧2回 -> 新3回(最大+1 TTS/KP解説)
    assert [s for s, _ in slots] == [3]                                    # HR queue投入は最終slot(通算3)のNGのみ


def test_kp_explanation_success_on_third_attempt_is_ok(tmp_path, monkeypatch):
    import er019_family_x_audio_production_runner_01 as x
    n = []
    r1 = _patch_repro01_leaf(monkeypatch, tmp_path, asr_text=WRONG, az=Az((WRONG, None)), tts_counter=n)
    monkeypatch.setattr(r1.repetition_qa, "apply_repetition_qa_gate", lambda v, *a, **k: {"verified": v, "repetition_qa_checked": False})
    monkeypatch.setattr(r1.routing, "transcribe", lambda *a, **k: (CANON if len(n) >= 3 else WRONG, None))
    r = x.generate_key_phrase_explanation_en_verified(CANON, str(tmp_path / "kp2_explanation_en.wav"), "STYLE")
    assert r["status"] == "OK" and len(n) == 3                              # 旧2回では救えなかった3回目PASSを採用


def test_kp_phrase_four_call_structure_unchanged_and_hr_only_at_slot_four(tmp_path, monkeypatch):
    n = []
    r1 = _patch_repro01_leaf(monkeypatch, tmp_path, asr_text=WRONG, az=Az((WRONG, None)), tts_counter=n)
    monkeypatch.setattr(r1.repetition_qa, "apply_repetition_qa_gate", lambda v, *a, **k: {"verified": v, "repetition_qa_checked": False})
    slots = _hr_slots(monkeypatch, sec)
    r = r1.generate_key_phrase_component_verified(CANON, str(tmp_path / "kp1_en.wav"))
    assert r["status"] == "STOPPED" and len(n) == 4                         # MINIMAL 2 + ENGLISH_LOCK 2 = 4(不変)
    assert [s for s, _ in slots] == [4]                                      # 前半(slot1-2)・後半前半(slot3)はHR queue対象外


def test_ja_kp_gloss_path_has_no_local_rewrite_and_keeps_principal_hr():
    import er003_v1_n3_01_tts_generate as n3
    import er003_v1_sing01_voice01_generate as v01
    for fn in (n3.generate_a2_japanese_with_fallback, v01.generate_charon_japanese):
        s = inspect.getsource(fn)
        assert "run_local_rewrite" not in s and '"status": "STOPPED"' in s
    assert "guarded_generate" in inspect.getsource(n3).split("def generate_a2_japanese_with_fallback")[0][-400:]


# ============================================================
# D. runner共有cache / circuit breaker
# ============================================================
RUNNER_ENTRIES = [
    ("er019_family_x_audio_production_runner_01", "generate_family_x_b1_segments"),
    ("er019_family_x_audio_production_runner_01", "generate_family_x_a2_segments"),
    ("er063_family_z_audio_01", "run_tts_stage"),
    ("er012_b_family_production_runner_01", "run_tts"),
    ("er012_b_family_production_runner_01", "run_tts_a2"),
    ("er012_b_family_production_runner_01", "run_tts_a2_2v_new_topic"),
    ("er012_b_family_voices_production_01", "run_tts_3v"),
    ("er013_family_c_production_runner_01", "run_full_generation"),
    ("er003_v1_n3_01_tts_generate", "generate_b1_segments"),
    ("er003_v1_n3_01_tts_generate", "generate_a2_segments"),
]


@pytest.mark.parametrize("mod,fn", RUNNER_ENTRIES)
def test_every_production_runner_tts_entry_is_run_scoped(mod, fn):
    m = __import__(mod)
    assert getattr(getattr(m, fn), "__secondary_run_scoped__", False) is True, f"{mod}.{fn} にrun scopeが無い"


def test_run_scope_decorator_begin_end_nested_and_exception_cleanup():
    seen = []

    @scope.with_secondary_run
    def inner():
        seen.append(("inner", sec._RUN_STATE, sec._RUN_CACHE))

    @scope.with_secondary_run
    def outer():
        seen.append(("outer", sec._RUN_STATE, sec._RUN_CACHE))
        inner()
        seen.append(("after_inner", sec._RUN_STATE, sec._RUN_CACHE))

    assert sec._RUN_STATE is None
    outer()
    assert sec._RUN_STATE is None and sec._RUN_CACHE is None               # 終了時に必ず破棄
    assert seen[0][1] is not None and seen[0][2] is not None
    assert seen[1][1] is seen[0][1] and seen[1][2] is seen[0][2]            # 入れ子は外側scopeを再利用
    assert seen[2][1] is seen[0][1]                                          # 内側終了で外側を壊さない

    @scope.with_secondary_run
    def boom():
        raise ValueError("x")

    with pytest.raises(ValueError):
        boom()
    assert sec._RUN_STATE is None and sec._RUN_CACHE is None                # 例外でも破棄


def test_z_run_tts_stage_enables_run_scope_during_generators_and_cleans_up(tmp_path, monkeypatch):
    import er063_family_z_audio_01_test_01 as zt
    import er063_family_z_audio_01 as z
    plan, _story, _kp = zt.make_plan("b1b")
    states = []
    base = zt.fake_generators()

    def wrap(kind, fn):
        def g(spec, out_path):
            states.append((sec._RUN_STATE is not None, sec._RUN_CACHE is not None))
            return fn(spec, out_path)
        return g
    gens = {k: wrap(k, v) for k, v in base.items()}
    run = str(tmp_path / "melos" / "run_01").replace("\\", "/")
    monkeypatch.setattr(z, "_check_stop_sentinel", lambda *a, **k: None)
    pw = mock.patch.object(reg, "write_listening_list_safe", return_value={})
    with pw:
        z.run_tts_stage(run, "b1b", plan, generators=gens)
    assert states and all(a and b for a, b in states)
    assert sec._RUN_STATE is None


def test_en_and_ja_adapters_share_run_cache_same_wav_duplicate_secondary_zero(tmp_path, monkeypatch):
    wav_en = _wav(tmp_path, "en.wav", fill=b"\x01")
    wav_ja = _wav(tmp_path, "ja.wav", fill=b"\x02")
    az = Az((CANON, None))
    azj = AzJa(("ありがとうございます。", None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    monkeypatch.setattr(ja, "_azure_stt_strict", azj)

    @scope.with_secondary_run
    def run_scope():
        for _ in range(3):
            sec.evaluate_attempt_with_cascade_detail(CANON, WRONG, [], wav_en, cascade_enabled=True, segment_id="full_story_part1")
            ja.evaluate_attempt_ja_with_cascade_detail("ありがとうございます。", "ありがとうごさいます", wav_ja, cascade_enabled=True)
        return sec._RUN_STATE

    st = run_scope()
    assert az.calls == 1 and azj.calls == 1                                   # 同一wavのSecondaryは(言語別とも)run内で1回
    assert st.secondary_calls >= 1


def test_circuit_breaker_stops_secondary_after_consecutive_failures_and_is_technical_not_lock(tmp_path, monkeypatch):
    az = Az((None, "azure down"))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    lock_calls = []
    monkeypatch.setattr(review_lock, "record_outcome", lambda *a, **k: lock_calls.append(1))

    @scope.with_secondary_run
    def run_scope():
        out = []
        sec._RUN_STATE.circuit_breaker_threshold = 2
        for i in range(4):
            w = _wav(tmp_path, f"w{i}.wav", fill=bytes([i + 5]))
            d = sec.evaluate_attempt_with_cascade_detail(CANON, WRONG, [], w, cascade_enabled=True, segment_id="full_story_part1")
            out.append(d)
        return out, sec._RUN_STATE

    ds, st = run_scope()
    assert az.calls == 2 and st.circuit_open is True                          # 連続障害2回でそのrunのSecondaryを止める
    assert all(d["verified"] is False for d in ds)                            # 障害時はPASS扱いにしない
    assert ds[-1]["asr_judgement"]["state"] == uj.NG_SECONDARY_UNAVAILABLE and ds[-1]["technical_stop"]
    assert lock_calls == []                                                   # 技術STOPはHuman Review Lockではない


# ============================================================
# E. attempt_ctx / is_last_slot 配線
# ============================================================
def test_build_attempt_ctx_rules():
    assert actx.build_attempt_ctx(1, 3) == {"slot": 1, "is_last_slot": False, "script_version": "v0"}
    assert actx.build_attempt_ctx(3, 3)["is_last_slot"] is True
    assert actx.build_attempt_ctx(2, 2, total_slots=3)["is_last_slot"] is False        # 後段fallbackが残る標準経路
    assert actx.build_attempt_ctx(1, 2, slot_offset=2, total_slots=4)["slot"] == 3
    assert actx.build_attempt_ctx(2, 2, slot_offset=2, total_slots=4)["is_last_slot"] is True
    assert actx.build_attempt_ctx(1, 1, script_version="v1")["script_version"] == "v1"


LEAF_MODULES = ["er003_v1_sing01_voice01_generate", "er003_v1_sing01_news_tail_fix", "er003_v1_sing01_point_headings_aoede",
                "er012_b_family_voices_production_01", "er003_v1_repro01_main_generate", "er003_v1_crosslevel_audio_02_common",
                "er003_v1_n3_01_tts_generate"]


def test_every_leaf_adapter_call_passes_attempt_ctx_ast():
    total = 0
    for m in LEAF_MODULES:
        tree = ast.parse(open(os.path.join(ROOT, m + ".py"), encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                nm = audit._callee_name(node.func).split(".")[-1]
                if nm in ("evaluate_attempt_with_cascade", "evaluate_attempt_ja_with_cascade"):
                    total += 1
                    assert any(k.arg == "attempt_ctx" for k in node.keywords), f"{m}:{node.lineno} がattempt_ctxを渡していない"
    assert total == 10      # EN 6 leaf(voice01/news_tail_fix/point_headings/bvoices/repro01/crosslevel) + JA 4呼出(voice01 x2, repro01, n3)


def _tts_mocks(monkeypatch, tts_counter=None):
    import er002_common as common
    import er003_b1_p3u_audio as p3u
    import er003_audio_tts_asr_safety as safety
    import er003_b1_p9a_audio as p9a
    import er006_batch_tts_wiring_01 as bw
    import er003_b1_p4c_audio as p4c
    import er008_disfluency_qa_18 as dq18
    import er011_open121_repetition_qa_production_01 as rq

    def tts(*a, **k):
        if tts_counter is not None:
            tts_counter.append(1)
        return (np.zeros(4000, dtype=np.int16).tobytes(), 0, True, None)
    monkeypatch.setattr(common, "_call_tts_with_retry", tts)
    monkeypatch.setattr(p3u, "trim_english_keyword_silence", lambda samples, sr, safety_margin_seconds=None:
                        (np.zeros(sr, dtype=np.float32), {"raw_duration_seconds": 1.0, "trimmed_duration_seconds": 1.0}))
    monkeypatch.setattr(safety, "detect_duration_anomaly", lambda *a, **k: {"is_anomaly": False})
    monkeypatch.setattr(bw, "make_batch_tts_call_fn", lambda *a, **k: (lambda *x, **y: None))
    monkeypatch.setattr(p4c, "build_tts_prompt", lambda text, style: "prompt")
    monkeypatch.setattr(dq18, "apply_disfluency_gate", lambda v, p, language="en", enabled=False: {"verified": v, "disfluency_checked": False, "disfluency_evidence": None})
    monkeypatch.setattr(rq, "apply_repetition_qa_gate", lambda v, *a, **k: {"verified": v, "repetition_qa_checked": False})
    def snippet(text, language, out_path, **kw):
        if tts_counter is not None:
            tts_counter.append(1)
        common.write_wav_float(out_path, np.zeros(8000, dtype=np.float32), common.SAMPLE_RATE, 1)
        return {"status": "OK", "duration_seconds": 1.0, "path": out_path, "sha256": "x"}
    monkeypatch.setattr(p9a, "generate_narration_snippet", snippet)
    monkeypatch.setattr(routing, "transcribe", lambda *a, **k: (WRONG, None))


@pytest.mark.parametrize("leaf", ["news_tail_fix", "voice01_en", "point_headings", "bvoices", "repro01_en"])
def test_en_leaf_hr_queue_only_at_last_slot_and_no_double_submission(leaf, tmp_path, monkeypatch):
    import er003_v1_sing01_news_tail_fix as ntf
    import er003_v1_sing01_voice01_generate as v01
    import er003_v1_sing01_point_headings_aoede as ph
    import er012_b_family_voices_production_01 as bv
    import er003_v1_repro01_main_generate as r1
    n = []
    _tts_mocks(monkeypatch, n)
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az((WRONG, None)))
    queue = str(tmp_path / "hrq_en.jsonl")
    out_path = str(tmp_path / "wiring_theme_auw5" / "b1b" / "narration" / "full_story_part1.wav").replace("\\", "/")
    os.makedirs(os.path.dirname(out_path))
    # 実_log_human_reviewを使う(queue書込を実測)。slotはspyで補助記録
    slots = []
    real = sec._log_human_review
    monkeypatch.setattr(sec, "_log_human_review", lambda d: (slots.append(d["asr_judgement"]["slot"]), real(d)))
    if leaf == "news_tail_fix":
        r = ntf.generate_news_narration_wide_margin(CANON, out_path, max_attempts=3)
    elif leaf == "voice01_en":
        r = v01.generate_charon_english(CANON, out_path, max_attempts=3)
    elif leaf == "point_headings":
        r = ph.generate(CANON, out_path, max_attempts=3)
    elif leaf == "bvoices":
        r = bv.generate_voice_body_wide_margin(CANON, out_path, "Puck", max_attempts=3)
    else:
        monkeypatch.setattr(r1.pron_resolver_core, "resolve_and_augment_en_style_prefix", lambda b, t: (b, {"hints_applied": False}))
        monkeypatch.setattr(r1.pronun_ledger, "get_hint_for_text", lambda *a, **k: [])
        r = r1.generate_narration_snippet_verified_strict(CANON, "en", out_path, CANON, max_attempts=3)
    assert r["status"] == "STOPPED"                                        # 3NG -> STOPPED(leaf側HR Lock経路へ。回数・終了形は不変)
    assert slots == [3], slots                                             # 最終slotのNGのみ(slot1,2は投入されない)
    lines = open(queue, encoding="utf-8").read().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["canonical_text"] == CANON    # leaf側HR Lockとの二重投入なし(queue 1件)


def test_crosslevel_standard2_plus_fallback1_hr_queue_only_at_slot_three(tmp_path, monkeypatch):
    import er003_v1_crosslevel_audio_02_common as cl
    import er003_v1_repro01_main_generate as r1
    n = []
    _tts_mocks(monkeypatch, n)
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az((WRONG, None)))
    monkeypatch.setattr(r1.pron_resolver_core, "resolve_and_augment_en_style_prefix", lambda b, t: (b, {"hints_applied": False}))
    monkeypatch.setattr(r1.pronun_ledger, "get_hint_for_text", lambda *a, **k: [])
    monkeypatch.setattr(cl.pronun_ledger, "get_hint_for_text", lambda *a, **k: [])
    monkeypatch.setattr(cl.routing, "transcribe", lambda *a, **k: (WRONG, None))
    monkeypatch.setattr(r1, "generate_english_component_minimal_instruction",
                        lambda text, out_path, **k: (n.append(1), {"status": "OK", "path": out_path, "duration_seconds": 1.0})[1])
    slots = _hr_slots(monkeypatch, sec)
    r = cl.generate_english_segment_with_fallback(CANON, str(tmp_path / "dummy.wav"), "quick")
    assert r["status"] == "STOPPED" and len(n) == 3                           # 標準2 + minimal fallback 1(通算3、回数不変)
    assert [s for s, _ in slots] == [3]


@pytest.mark.parametrize("leaf", ["voice01_ja", "repro01_ja", "n3_ja"])
def test_ja_leaf_hr_queue_only_at_last_slot_and_stops_in_stopped_for_lock(leaf, tmp_path, monkeypatch):
    import er003_v1_sing01_voice01_generate as v01
    import er003_v1_repro01_main_generate as r1
    import er003_v1_n3_01_tts_generate as n3
    n = []
    _tts_mocks(monkeypatch, n)
    JA = "ありがとうございます、今日は晴れです"
    JA_NG = "さようなら明日は雨でしょう"
    monkeypatch.setattr(routing, "transcribe", lambda *a, **k: (JA_NG, None))
    monkeypatch.setattr(ja, "_azure_stt_strict", AzJa((JA_NG, None)))
    slots = []
    monkeypatch.setattr(ja, "_log_human_review", lambda d: slots.append(d["asr_judgement"]["slot"]))
    if leaf == "voice01_ja":
        monkeypatch.setattr(v01, "generate_charon_japanese_minimal_instruction", lambda text, out_path, tts_backend="x": (n.append(1), {"status": "OK", "path": out_path})[1])
        r = v01.generate_charon_japanese(JA, str(tmp_path / "dummy.wav"), "ありがとう")
    elif leaf == "repro01_ja":
        r = r1.generate_narration_snippet_verified_strict(JA, "ja", str(tmp_path / "dummy.wav"), "ありがとう", max_attempts=3)
    else:
        monkeypatch.setattr(n3, "_generate_a2_japanese_minimal_instruction", lambda text, out_path, tts_backend="x": (n.append(1), {"status": "OK", "path": out_path})[1])
        r = n3.generate_a2_japanese_with_fallback(JA, str(tmp_path / "dummy.wav"), "ありがとう")
    assert r["status"] == "STOPPED"                                           # 3NG -> STOPPED(既存のleaf側HR Lock経路へ。LRなし=原則HR)
    assert slots == [3], slots


def test_local_rewrite_retts_passes_script_version_v1_and_pww_lr_rewritten(tmp_path, monkeypatch):
    import er003_v1_sing01_news_tail_fix as ntf
    n = []
    _tts_mocks(monkeypatch, n)
    out_path = str(tmp_path / "wiring_theme_auw5" / "b1b" / "narration" / "full_story_part1.wav").replace("\\", "/")
    os.makedirs(os.path.dirname(out_path))
    REWRITTEN = "The fast brown fox jumps over the lazy dog."
    monkeypatch.setattr(routing, "transcribe", lambda *a, **k: (REWRITTEN if len(n) > 3 else WRONG, None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az((WRONG, None)))
    monkeypatch.setattr(sec, "_connected_speech_equivalence_layer_attempt", lambda *a, **k: None)
    monkeypatch.setattr(ntf.retry_primitive, "maybe_cooldown_before_attempt", lambda *a, **k: None)
    monkeypatch.setattr(sec, "_log_human_review", lambda d: None)

    def fake_recovery(*, segment_id, canonical_text, last_asr_text, retts_fn, out_dir=None, **kw):
        r = retts_fn(REWRITTEN)
        return {"status": "RESOLVED_BY_LOCAL_REWRITE" if r.get("status") == "OK" else "X", "retts_result": r}

    monkeypatch.setattr(ntf.retry_primitive, "run_local_rewrite_recovery", fake_recovery)
    r = ntf.generate_news_narration_wide_margin(CANON, out_path, max_attempts=3, enable_connected_speech_equivalence_layer=True)
    assert r["status"] == "OK"
    j = r["asr_judgement"]
    assert j["script_version"] == "v1" and j["state"] == uj.PASS_WITH_WARNING and uj.W_LR_REWRITTEN in j["warnings"]


def test_hr_lock_module_unchanged_and_stop_retrying_branches_recorded_only():
    import subprocess
    out = subprocess.run(["git", "diff", "--name-only", "961d5b360", "--", "er011_human_review_lock_01.py"],
                         capture_output=True, text=True, cwd=ROOT).stdout
    assert out.strip() == ""                                                 # HR Lock module(er011)は無変更を維持
    d = sec.evaluate_attempt_with_cascade_detail(CANON, WRONG, [], "nofile.wav", cascade_enabled=True, attempt_ctx={"is_last_slot": True})
    assert d["stop_retrying"] is False                                        # `if stop_retrying:`分岐は到達不能(削除は委任_07判断)
    left = 0
    for m in LEAF_MODULES:
        left += open(os.path.join(ROOT, m + ".py"), encoding="utf-8").read().count("if stop_retrying:")
    assert left > 0


# ============================================================
# F. Family B / C hook
# ============================================================
PWW_JUDGEMENT = {"state": "PASS_WITH_WARNING", "warnings": ["SECONDARY_CONFIRMED"], "reason_code": "secondary_confirmed",
                 "primary": {"text": WRONG}, "secondary": {"text": CANON}, "value_guard": {}}


def test_family_b_finalize_functions_write_listening_list_including_zero_section(tmp_path, monkeypatch):
    import er012_b_family_production_runner_01 as bp
    out1 = tmp_path / "b1"
    out3 = tmp_path / "b3v"
    for d in (out1, out3):
        (d / "audit").mkdir(parents=True)
    monkeypatch.setattr(bp, "OUT_B1_DIR", str(out1))
    monkeypatch.setattr(bp, "OUT_B1_DIR_3V", str(out3))
    monkeypatch.setattr(bp, "load_json", lambda p: {"items": []})
    seg = {"status": "OK", "text": CANON, "path": str(out1 / "x.wav"), "sha256": "abc", "asr_judgement": PWW_JUDGEMENT}
    bp.finalize_tts_results({"point_one": seg})
    lst = json.load(open(out1 / "audit" / "pass_with_warning_listening_list.json", encoding="utf-8"))
    assert lst["count"] == 1 and lst["entries"][0]["segment_id"] == "point_one"
    assert "事後試聴リスト(PASS_WITH_WARNING)" in open(out1 / "audit" / "pass_with_warning_listening_list.html", encoding="utf-8").read()
    bp.finalize_tts_results_3v({"point_one": {"status": "OK", "text": CANON, "path": "y.wav", "sha256": "abc"}})   # WARNINGなし
    assert json.load(open(out3 / "audit" / "pass_with_warning_listening_list.json", encoding="utf-8"))["count"] == 0
    assert "0件" in open(out3 / "audit" / "pass_with_warning_listening_list.html", encoding="utf-8").read()        # 0件でも節を出す
    # a2 / a2_2v_new_topic も同じhook(静的)
    src = inspect.getsource(bp)
    for fn in ("finalize_tts_results", "finalize_tts_results_3v", "finalize_tts_results_a2", "finalize_tts_results_a2_2v_new_topic"):
        body = inspect.getsource(getattr(bp, fn))
        assert "pww_registry.write_listening_list_safe" in body, fn
    assert "pww_registry" in src


def test_family_c_audit_entry_carries_judgement_and_hook_follows_results_write(tmp_path):
    import er013_family_c_production_runner_01 as cp
    fresh = cp.to_audit_entry({"status": "OK", "path": "p.wav", "sha256": "s", "asr_judgement": PWW_JUDGEMENT}, CANON, False)
    assert fresh["asr_judgement"] == PWW_JUDGEMENT
    assert "asr_judgement" not in cp.to_audit_entry({"status": "OK", "path": "p.wav"}, CANON, False)       # additive(無い場合はキー追加なし)
    wav = tmp_path / "seg.wav"
    wav.write_bytes(b"WAV")
    cp.mark_ok({"status": "OK", "asr_judgement": PWW_JUDGEMENT}, str(wav), "texthash")
    reused = cp.resumable_reuse(str(wav), "texthash")
    assert reused["asr_judgement_inherited"] == PWW_JUDGEMENT                  # resume/reuse時は元のWARNINGを継承
    inh = cp.to_audit_entry(reused, CANON, True)
    assert inh["asr_judgement_inherited"] == PWW_JUDGEMENT and "asr_judgement" not in inh
    es = reg.derive_listening_list({"segments": {"point_one": dict(inh, text=CANON)}})
    assert len(es) == 1 and es[0]["inherited"] is True
    wav.write_bytes(b"CHANGED")                                                 # wavが変わったら継承しない(sha256不一致)
    assert "asr_judgement_inherited" not in (cp.resumable_reuse(str(wav), "texthash") or {})
    body = inspect.getsource(cp.run_full_generation)
    i_write = body.index('tts_generation_results.json", "w"')
    i_hook = body.index("pww_registry.write_listening_list_safe")
    i_gate = body.index("verify_episode_audio_validation_gate")
    assert i_write < i_hook < i_gate                                             # results確定直後・Gate前にhook


def test_family_c_get_or_run_asr_is_diagnostic_only_not_a_judgement():
    import er013_family_c_production_runner_01 as cp
    s = inspect.getsource(cp)
    assert not any(w in s for w in ("evaluate_attempt", "classify_asr_match", "unified_judge")) and "asr_verified" not in s
