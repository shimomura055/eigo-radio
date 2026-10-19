# FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_02: 不具合③(OPEN-283)「Rewrite(Local Rewrite=LR)後の音声検査が旧原稿と
# 照合される不整合」の修正と、不具合②「最大2回のTTS再生成後にのみRewrite / Rewrite前の承認済み検証を省略しない」の固定test。
# 全てmock(ASR=routing.transcribe, Secondary=get_full_text_via_azure_stt_with_phrase_list, TTS/ffmpeg=差替え)。API呼出0・費用JPY0。
# HR queue・attempt_history・telemetryの書込先は全てmock/tmp_pathへ退避(リポジトリのstateを汚さない)。
import os
import unittest.mock as mock

import pytest

import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as sec
import er011_human_review_lock_01 as review_lock
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er003_v1_crosslevel_audio_02_common as crosslevel
import er003_v1_n3_01_tts_generate as tg

CANON = "Water came slowly through a crack in the rock. Melos drank, got onto his knees, and stood up."
REWRITTEN = "Water came slowly through a crack in the rock. He drank, got onto his knees, and stood up."
# 実機(run_e2e_04 Std part3_c1)の減速後転写に相当: 書換え後の文として読まれている
ASR_REWRITTEN = "Water came slowly through a crack in the rock. He drank, got on to his knees, and stood up."
ASR_WRONG = "Water came slowly through a crack in the rock. They danced, got onto their knees, and sat down."


class Az:
    def __init__(self, result=(None, "no result")):
        self.result, self.calls = result, 0

    def __call__(self, wav_path, language="en-US", phrases=None, **kw):
        self.calls += 1
        return self.result


def lr_result(rewritten=REWRITTEN, *, via="selection", status="RESOLVED_BY_LOCAL_REWRITE", fallback_used=True):
    """crosslevel/voice01/news_tail_fixの`_local_rewrite_recovery_for_*`が返す実形に合わせたLR採用結果。"""
    rec = {"status": status, "canonical_text": CANON,
           "selection": {"selected": {"id": "1", "rewritten_segment": rewritten}} if via == "selection" else {"selected": None},
           "retts_result": {"status": "OK", "text": rewritten}}
    return {"status": "OK", "text": rewritten, "sha256": None, "duration_seconds": 2.0,
            "local_rewrite_recovery": rec, "canonical_text_before_local_rewrite": CANON,
            "fallback_used": fallback_used}


@pytest.fixture(autouse=True)
def _iso(monkeypatch, tmp_path):
    sec.reset_secondary_cache()
    sec._reset_m1_freeze_cache()
    monkeypatch.setattr(sec, "_RUN_STATE", None)
    monkeypatch.setattr(sec, "_RUN_CACHE", None)
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: {})
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda *a, **k: None)
    monkeypatch.setattr(sec.semantic_equivalence, "append_telemetry_log", lambda *a, **k: None)
    monkeypatch.setattr(sec, "HUMAN_REVIEW_LOG_PATH", str(tmp_path / "hrq_en.jsonl"))
    monkeypatch.setattr(review_lock, "save_tts_attempt_audio", lambda *a, **k: "saved.wav")
    monkeypatch.setattr(review_lock, "append_attempt_history_event", lambda *a, **k: None)
    yield
    sec.reset_secondary_cache()


def _fake_stretch(src, dst):
    with open(dst, "wb") as f:
        f.write(b"POST_STRETCHED_" + os.path.basename(dst).encode())
    return {"src_duration_seconds": 2.0, "dst_duration_seconds": 2.12}


def _setup(monkeypatch, primary, az):
    monkeypatch.setattr(tg.a2_slowdown, "apply_a2_slowdown", _fake_stretch)
    monkeypatch.setattr(tg.routing, "transcribe", lambda *a, **k: (primary, None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)


def _spy_judge(monkeypatch):
    """統一judgeに渡された『期待テキスト(第1引数)』を記録する(実関数はそのまま呼ぶ)。"""
    seen = []
    real = sec.evaluate_attempt_with_cascade_detail

    def spy(expected, *a, **k):
        seen.append(expected)
        return real(expected, *a, **k)

    monkeypatch.setattr(sec, "evaluate_attempt_with_cascade_detail", spy)
    return seen


def _post(tmp_path, result, canonical=CANON, name="full_story_part3_c1", **kw):
    (tmp_path / f"{name}.wav").write_bytes(b"PRE")
    return tg.apply_a2_slowdown_postprocess(name, str(tmp_path), canonical, result, **kw)


# ---------- 単一参照点(helper)の単体 ----------
def test_helper_returns_canonical_when_no_lr():
    assert retry_primitive.resolve_expected_text_after_local_rewrite({"status": "OK", "text": CANON}, CANON) == (CANON, "canonical_text")
    assert retry_primitive.resolve_expected_text_after_local_rewrite({}, CANON) == (CANON, "canonical_text")
    assert retry_primitive.resolve_expected_text_after_local_rewrite(None, CANON) == (CANON, "canonical_text")


def test_helper_returns_sent_text_when_lr_resolved():
    assert retry_primitive.resolve_expected_text_after_local_rewrite(lr_result(), CANON) == (REWRITTEN, "local_rewrite_text")
    # selectionが欠けても、再TTSに実際に渡した文(retts_result.text)を使う
    assert retry_primitive.resolve_expected_text_after_local_rewrite(lr_result(via="none"), CANON) == (REWRITTEN, "local_rewrite_text")


def test_helper_ignores_unresolved_lr_record():
    # RESOLVED_BY_LOCAL_REWRITE以外(=書換えが正式に採用されていない)は原稿を変えない
    r = lr_result(status="HUMAN_REVIEW_LOCKED_RETTS_FAILED")
    assert retry_primitive.resolve_expected_text_after_local_rewrite(r, CANON) == (CANON, "canonical_text")


# ---------- (a) LR採用後の減速後再検証は書換え後文と照合される ----------
def test_a_post_slowdown_reverify_uses_rewritten_text_after_lr(tmp_path, monkeypatch):
    az = Az()
    _setup(monkeypatch, ASR_REWRITTEN, az)
    seen = _spy_judge(monkeypatch)
    r = _post(tmp_path, lr_result())
    assert seen == [REWRITTEN]                          # 旧原稿(Melos入り)ではなく書換え後の実送信文で判定
    assert r["status"] == "OK" and r["asr_verified"] is True
    assert r["post_slowdown_expected_text_source"] == "local_rewrite_text"
    assert az.calls == 0                                # Primary PASS=Secondary不要(追加API 0)


def test_a_pre_fix_behaviour_would_have_failed_this_transcript(tmp_path, monkeypatch):
    """修正前と同じ『旧原稿で判定』を再現すると、同じ転写がNG_BOTH→STOPPED(=HR Lock)になる(testの検出力確認)。"""
    az = Az()
    _setup(monkeypatch, ASR_REWRITTEN, az)
    r = _post(tmp_path, {"status": "OK", "sha256": None, "duration_seconds": 2.0})   # LR記録なし=canonicalで判定
    assert r["status"] == "STOPPED"


# ---------- (b) LR非採用時は従来どおり ----------
def test_b_without_lr_expected_text_is_canonical(tmp_path, monkeypatch):
    az = Az()
    _setup(monkeypatch, CANON, az)
    seen = _spy_judge(monkeypatch)
    r = _post(tmp_path, {"status": "OK", "sha256": None, "duration_seconds": 2.0, "text": CANON})
    assert seen == [CANON]
    assert r["status"] == "OK" and r["post_slowdown_expected_text_source"] == "canonical_text"


def test_b_without_lr_mismatch_still_stops(tmp_path, monkeypatch):
    _setup(monkeypatch, ASR_WRONG, Az())
    r = _post(tmp_path, {"status": "OK", "sha256": None, "duration_seconds": 2.0})
    assert r["status"] == "STOPPED" and r["asr_verified"] is False


def test_b_unresolved_lr_record_does_not_change_expected_text(tmp_path, monkeypatch):
    _setup(monkeypatch, CANON, Az())
    seen = _spy_judge(monkeypatch)
    _post(tmp_path, lr_result(status="HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA"))
    assert seen == [CANON]


# ---------- (c) retry(外側ループ)/fallback/Dialogue経路でも正解原稿は『その結果が実際に送信した文』 ----------
def test_c_outer_loop_retry_resets_expected_text_per_generation(tmp_path, monkeypatch):
    """1周目=LR採用(書換え後文で再検証。転写が全く違えばNG)→2周目=通常生成(canonicalで再検証)。各周の正解原稿はその周の結果に従う。"""
    out = str(tmp_path / "full_story_part3_c1.wav").replace("\\", "/")
    open(out, "wb").write(b"PRE")                       # 生成器(mock)が出力したはずの減速前wav
    seq = [lr_result(), {"status": "OK", "sha256": None, "duration_seconds": 2.0, "text": CANON,
                          "attempts_log": [{"attempt": 1}]}]
    monkeypatch.setattr(tg.c, "generate_english_segment_with_fallback", lambda *a, **k: seq.pop(0))
    transcripts = [ASR_WRONG, CANON]
    monkeypatch.setattr(tg.a2_slowdown, "apply_a2_slowdown", _fake_stretch)
    monkeypatch.setattr(tg.routing, "transcribe", lambda *a, **k: (transcripts.pop(0), None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az())
    seen = _spy_judge(monkeypatch)
    r = tg.generate_a2_segment_with_slowdown(CANON, out, "Water")
    assert seen == [REWRITTEN, CANON]
    assert r["status"] == "OK"
    assert [a["status"] for a in r["slowdown_attempts_log"]] == ["STOPPED", "OK"]


def test_c_dialogue_outer_loop_uses_same_reference(tmp_path, monkeypatch):
    out = str(tmp_path / "full_story_part3_c1.wav").replace("\\", "/")
    open(out, "wb").write(b"PRE")                       # 生成器(mock)が出力したはずの減速前wav
    monkeypatch.setattr(tg.a2_slowdown, "apply_a2_slowdown", _fake_stretch)
    monkeypatch.setattr(tg.routing, "transcribe", lambda *a, **k: (ASR_REWRITTEN, None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az())
    seen = _spy_judge(monkeypatch)
    r = tg.generate_with_a2_slowdown_outer_loop("full_story_part3_c1", CANON, out, lambda max_attempts: lr_result())
    assert seen == [REWRITTEN] and r["status"] == "OK"


def test_c_post_slowdown_judge_ledger_hint_uses_rewritten_text(tmp_path, monkeypatch):
    """_post_slowdown_unified_judge内のLedger PhraseList導出も同じ正解原稿(書換え後文)を使う。"""
    import er006_pronunciation_ledger_01 as pl
    hint_args = []
    monkeypatch.setattr(pl, "get_hint_for_text", lambda text, **k: hint_args.append(text) or [])
    _setup(monkeypatch, ASR_REWRITTEN, Az())
    _post(tmp_path, lr_result())
    assert hint_args == [REWRITTEN]


# ---------- (d) 最終NG時のHR Lock遷移は維持される(Lockのkeyは従来どおり元の原稿) ----------
def test_d_final_ng_after_lr_still_reaches_hr_lock_with_canonical_lock_key(tmp_path, monkeypatch):
    out = str(tmp_path / "full_story_part3_c1.wav").replace("\\", "/")
    open(out, "wb").write(b"PRE")                       # 生成器(mock)が出力したはずの減速前wav
    monkeypatch.setattr(tg.c, "generate_english_segment_with_fallback",
                        lambda *a, **k: dict(lr_result(), attempts_log=[{"attempt": 1}] * 3))
    monkeypatch.setattr(tg.a2_slowdown, "apply_a2_slowdown", _fake_stretch)
    monkeypatch.setattr(tg.routing, "transcribe", lambda *a, **k: (ASR_WRONG, None))   # 書換え後文とも一致しない=本当のNG
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az())
    rec = []
    monkeypatch.setattr(review_lock, "record_outcome",
                        lambda out_path, text, language, result, **k: rec.append((text, result.get("status"))) or {"state": "HUMAN_REVIEW_REQUIRED"})
    r = tg.generate_a2_segment_with_slowdown(CANON, out, "Water")
    assert r["status"] == "STOPPED" and r["human_review_required"] is True
    assert r["review_lock_state_final"] == "HUMAN_REVIEW_REQUIRED"
    assert rec == [(CANON, "STOPPED")]                  # Lockのkey(canonical sha)は書換え前の原稿のまま(Lock/承認記録の同一性を維持)


# ---------- (e) ②: 最大2回のTTS再生成後にのみRewrite / Rewrite前の承認済み検証を省略しない ----------
def _fallback_outcome(verified):
    cls = mock.Mock()
    cls.classification = "EXACT_MATCH" if verified else "ASR_VALIDATION_UNCERTAIN"
    return {"ok": True, "result": {"status": "OK", "path": "x"}, "verified": verified, "stop_retrying": False,
            "asr_text": "t", "classification": cls, "length_ok": True, "final_length_ok": True,
            "disfluency_gate": {"disfluency_checked": False, "verified": verified},
            "repetition_gate": {"repetition_qa_checked": False, "verified": verified},
            "cascade_steps": [], "asr_judgement": None}


def _drive_english_fallback(monkeypatch, tmp_path, *, fallback_verified):
    out = str(tmp_path / "narration" / "full_story_part3_c1.wav").replace("\\", "/")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    calls = {"standard": 0, "fallback": 0, "lr_after_fallback_calls": None, "lr": 0}

    def std(*a, **k):
        calls["standard"] += 1
        return {"status": "STOPPED", "attempts_log": [{"attempt": 1, "asr_text": "a"}, {"attempt": 2, "asr_text": "b"}]}

    def fb(*a, **k):
        calls["fallback"] += 1
        return _fallback_outcome(fallback_verified)

    def lr(*a, **k):
        calls["lr"] += 1
        calls["lr_after_fallback_calls"] = calls["fallback"]
        return None

    monkeypatch.setattr(crosslevel, "generate_narration_snippet_verified_strict", std)
    monkeypatch.setattr(crosslevel, "_run_a2_minimal_fallback_attempt", fb)
    monkeypatch.setattr(crosslevel, "_local_rewrite_recovery_for_english_segment_with_fallback", lr)
    monkeypatch.setattr(crosslevel.retry_primitive, "maybe_cooldown_before_attempt", lambda *a, **k: None)
    monkeypatch.setattr(crosslevel.review_lock, "save_tts_attempt_audio", lambda *a, **k: "saved.wav")
    r = crosslevel.generate_english_segment_with_fallback.__wrapped__(
        CANON, out, "Water", enable_connected_speech_equivalence_layer=True)
    return r, calls


def test_e_rewrite_only_after_two_regenerations_exhausted(monkeypatch, tmp_path):
    r, calls = _drive_english_fallback(monkeypatch, tmp_path, fallback_verified=False)
    # TTS初回+再生成2回(標準2+fallback1=通算3、PRODUCTION_MAX_TTS_ATTEMPTS)を使い切った後で初めてRewriteへ進む
    assert review_lock.PRODUCTION_MAX_TTS_ATTEMPTS == 3
    assert calls["standard"] == 1 and calls["lr_after_fallback_calls"] == 1 and calls["lr"] == 1
    assert len(r["standard_attempts_log"]) + len(r["fallback_attempts_log"]) == 3


def test_e_rewrite_not_reached_when_pre_rewrite_verification_passes(monkeypatch, tmp_path):
    r, calls = _drive_english_fallback(monkeypatch, tmp_path, fallback_verified=True)
    assert r["status"] == "OK" and calls["lr"] == 0     # Rewrite前の承認済み検証(Primary/Secondary/音韻同等性)がPASSなら書換えない


def test_e_pre_rewrite_verification_is_the_approved_unified_judge_not_skipped():
    """fallback attempt本体は統一judge(Primary/Secondary/M1/Tier3/音韻同等性を含む既存経路)を必ず通る。"""
    import inspect
    src = inspect.getsource(crosslevel._run_a2_minimal_fallback_attempt)
    assert "secondary_asr.evaluate_attempt_with_cascade" in src and "force_secondary=True" in src


def test_e_cascade_on_never_requests_early_rewrite_via_stop_retrying(tmp_path, monkeypatch):
    """既定(cascade有効)では同一signature連続でもstop_retrying=False固定=『再生成を飛ばして早期Rewrite』は起きない(DESIGN_01 §4-2/§4-9)。"""
    import er006_preprod_hardening_01_validation as val
    verified, stop, cls = val.evaluate_attempt(CANON, ASR_WRONG, [])
    prior = [cls, cls]
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az())
    wav = str(tmp_path / "a.wav")
    open(wav, "wb").write(b"x")
    out = sec.evaluate_attempt_with_cascade_detail(CANON, ASR_WRONG, prior, wav, language="en-US", cascade_enabled=True)
    assert out["stop_retrying"] is False


# ---------- (c') resume/再利用/継承経路(保存転写の再判定)も書換え後文を正解とする ----------
def _saved_entry(with_lr):
    e = {"status": "OK", "text": CANON, "canonical_text": CANON, "asr_text": ASR_REWRITTEN, "sha256": "x"}
    if with_lr:
        e["local_rewrite_recovery"] = lr_result()["local_rewrite_recovery"]
        e["canonical_text_before_local_rewrite"] = CANON
    return e


def test_c_reuse_rejudge_uses_rewritten_text_for_lr_entry():
    import er019_family_x_validation_inheritance_01 as vi
    ok = vi.rejudge_with_current_judge(_saved_entry(True), "a2", "full_story_part3_c1", force_lang="en")
    assert ok["ok"] is True and ok["secondary_new_calls"] == 0          # API 0・書換え後の文に対して合格
    assert ok["tts_input"].startswith("Water came slowly") and "Melos" not in ok["tts_input"] and "He drank" in ok["tts_input"]
    ng = vi.rejudge_with_current_judge(_saved_entry(False), "a2", "full_story_part3_c1", force_lang="en")
    assert ng["ok"] is False                                            # LR記録なし=従来どおり(旧原稿で照合)


def test_c_reuse_value_guard_not_blocked_for_lr_entry_and_unchanged_without():
    import er078_reuse_value_guard_01 as rvg
    assert rvg.guard_entry(_saved_entry(True), label="x")["blocked"] is False
    # 値の差(LRとは無関係の旧挙動)は従来どおり検出される: LR記録なしで数値が変わった転写はblocked
    e = {"status": "OK", "text": "It costs 20 dollars.", "asr_text": "It costs 30 dollars.", "sha256": "x"}
    assert rvg.guard_entry(e, label="x")["blocked"] is True
