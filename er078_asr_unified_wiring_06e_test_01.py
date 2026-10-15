# -*- coding: utf-8 -*-
"""AUW 委任_06e: 06dの実run不整合F1(Z kp_en外側guard)・F2(Z circuit-open後のKeyError)・F3(A2外側ループ最終NGのHR末端/
asr_judgement更新)の是正test。API 0(通信遮断plugin下で実行)。Lock/queue/attempt_historyはtmpへ隔離する。
Lockロジック(er011_human_review_lock_01.py)は無変更で、既存のrecord_outcome/guarded_generateを正しく呼ぶだけ。"""
import json
import os
import wave

import pytest

import er003_v1_n3_01_tts_generate as n3_tts
import er006_secondary_asr_01 as sec
import er011_human_review_lock_01 as lock
import er063_family_z_audio_01 as z
import er063_family_z_audio_01_test_01 as zt
import er078_secondary_run_scope_01 as scope


@pytest.fixture(autouse=True)
def _iso(monkeypatch, tmp_path):
    sec.reset_secondary_cache()
    monkeypatch.setattr(sec, "_RUN_STATE", None)
    monkeypatch.setattr(sec, "_RUN_CACHE", None)
    monkeypatch.setattr(lock, "ATTEMPT_HISTORY_PATH", str(tmp_path / "attempt_history.jsonl"))
    monkeypatch.setattr(sec, "HUMAN_REVIEW_LOG_PATH", str(tmp_path / "hr_queue.jsonl"))
    yield
    sec.reset_secondary_cache()


def _tone(path, seconds=1):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(8000)
        w.writeframes(b"\x00" * (8000 * seconds))


def _lock_state(out_path):
    store = lock._load_store(lock._level_out_dir_from_out_path(out_path))
    return store.get(lock.derive_segment_key(out_path)[2]) or {}


def _queue_rows(tmp_path):
    p = tmp_path / "hr_queue.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


# ============================================================
# F2: run_tts_stage が circuit open 後も異常終了せず、技術STOP entryを結果JSONへ書く
# ============================================================
def test_f2_run_tts_stage_circuit_open_writes_technical_stop_entries_without_keyerror(tmp_path, capsys):
    run = str(tmp_path / "melos" / "run_01")
    plan, _, _ = zt.make_plan("b1b")
    base = zt.fake_generators()
    calls = []

    def make(kind):
        def fn(spec, out_path):
            calls.append(spec.clip_id)
            if len(calls) == 1:   # 1本目の生成中にSecondary連続障害でcircuit open(circuit breaker相当の状態)
                rs = sec._RUN_STATE
                rs.circuit_open = True
                rs.technical_stop_events.append({"type": "SECONDARY_UNAVAILABLE", "restartable": True, "approval_required": False})
            return base[kind](spec, out_path)
        return fn
    gens = {k: make(k) for k in base}
    out = z.run_tts_stage(run, "b1b", plan, generators=gens)         # 異常終了(KeyError)しない
    assert len(calls) == 1                                           # 残りclipはTTS 0
    statuses = out["statuses"]
    assert statuses[plan[0].clip_id] == "OK"
    rest = [s.clip_id for s in plan[1:]]
    assert rest and all(statuses[c] == scope.TECHNICAL_STOP_STATUS for c in rest)
    doc = json.load(open(out["results_path"], encoding="utf-8"))
    ents = list(doc["segments"].values()) + [e for kp in doc["key_phrases"].values() for e in kp.values()]
    ts = [e for e in ents if e.get("status") == scope.TECHNICAL_STOP_STATUS]
    assert len(ts) == len(rest)
    for e in ts:
        assert e["technical_stop"] is True and e["restartable"] is True and e["approval_required"] is False
        assert e["human_review_required"] is False and e["z_adoption"] == "failed"
        assert e["style"]["instruction_label"] and e["sha256"] is None      # build_entryを通っている・残存wavを記録しない
    assert "[TECHNICAL_STOP]" in capsys.readouterr().out                    # 停止の報告
    ev = json.load(open(out["evidence_path"], encoding="utf-8"))["clips"]
    assert len(ev) == len(plan)                                             # 全clipがevidence行を持つ


def test_f2_normalize_leaves_normal_and_non_technical_entries_untouched():
    plan, _, _ = zt.make_plan("b1b")
    normal = {"status": "OK", "style": {"x": 1}}
    assert z.normalize_technical_stop_entry(plan[0], "x.wav", normal) is normal
    plain = {"status": "STOPPED"}
    assert z.normalize_technical_stop_entry(plan[0], "x.wav", plain) is plain


# ============================================================
# F1: Z kp_en の2段呼出が外側guard1つで包まれ、4回構成が成立する
# ============================================================
def _fake_strict_factory(script, seen):
    @lock.guarded_generate_with_language_arg      # 実物(generate_narration_snippet_verified_strict)と同じ内側guard
    def strict(text, language, out_path, expected, **kw):
        stage = len(seen)
        seen.append({"slot_offset": kw.get("slot_offset"), "total_slots": kw.get("total_slots"),
                     "max_attempts": kw.get("max_attempts"), "style": kw.get("style_prefix_override")})
        status = script[stage]
        n = kw.get("max_attempts")
        if status == "OK":
            _tone(out_path)
        return {"status": status, "attempts_log": [{"attempt": i + 1, "asr_text": "x"} for i in range(n)],
                "reason": None if status == "OK" else "ng"}
    return strict


def _kp_spec_from_plan():
    plan, _, _ = zt.make_plan("b1b")
    return next(s for s in plan if s.kind == "kp_en")


def test_f1_without_outer_guard_second_stage_is_locked_reproduction(tmp_path):
    out = str(tmp_path / "t" / "b1b" / "narration" / "kp1_en.wav")
    seen = []
    strict = _fake_strict_factory(["STOPPED", "STOPPED"], seen)
    r1 = strict("Xzqwtrlk wrangle", "en", out, "Xzqwtrlk wrangle", max_attempts=2, slot_offset=0, total_slots=4)
    r2 = strict("Xzqwtrlk wrangle", "en", out, "Xzqwtrlk wrangle", max_attempts=2, slot_offset=2, total_slots=4)
    assert r1["status"] == "STOPPED" and r2["status"] == "HUMAN_REVIEW_LOCKED" and len(seen) == 1     # 06d kp4の再現(是正前の挙動)


def test_f1_z_kp_en_runs_all_four_attempts_and_locks_only_after_stage2(tmp_path, monkeypatch):
    import er003_v1_repro01_main_generate as repro01
    seen = []
    monkeypatch.setattr(repro01, "generate_narration_snippet_verified_strict", _fake_strict_factory(["STOPPED", "STOPPED"], seen))
    monkeypatch.setattr(z, "style_text_for", lambda s: "MINIMAL")
    spec = _kp_spec_from_plan()
    out = str(tmp_path / "t" / "b1b" / "narration" / spec.wav_name())
    r = z.real_generators()["kp_en"](spec, out)
    assert [s["slot_offset"] for s in seen] == [0, 2] and [s["total_slots"] for s in seen] == [4, 4]    # 4回構成が成立
    assert [s["max_attempts"] for s in seen] == [2, 2]
    assert r["status"] == "STOPPED" and r["fallback_used"] is True
    assert len(r["fallback_attempts_log"]) == 2 and len(r["attempts_log"]) == 2                         # legacyと同じ会計(計4 TTS)
    st = _lock_state(out)
    assert st["state"] == "HUMAN_REVIEW_REQUIRED" and st["cumulative_tts_attempts"] == 4


def test_f1_stage1_stopped_does_not_lock_and_stage2_ok_resolves(tmp_path, monkeypatch):
    import er003_v1_repro01_main_generate as repro01
    seen = []
    monkeypatch.setattr(repro01, "generate_narration_snippet_verified_strict", _fake_strict_factory(["STOPPED", "OK"], seen))
    monkeypatch.setattr(z, "style_text_for", lambda s: "MINIMAL")
    spec = _kp_spec_from_plan()
    out = str(tmp_path / "t" / "b1b" / "narration" / spec.wav_name())
    r = z.real_generators()["kp_en"](spec, out)
    assert len(seen) == 2 and r["status"] == "OK" and r["fallback_used"] is True       # 1段目STOPPEDでLockが先に立たない
    assert _lock_state(out)["state"] == "RESOLVED"


def test_f1_stage1_ok_returns_without_stage2(tmp_path, monkeypatch):
    import er003_v1_repro01_main_generate as repro01
    seen = []
    monkeypatch.setattr(repro01, "generate_narration_snippet_verified_strict", _fake_strict_factory(["OK"], seen))
    monkeypatch.setattr(z, "style_text_for", lambda s: "MINIMAL")
    spec = _kp_spec_from_plan()
    out = str(tmp_path / "t" / "b1b" / "narration" / spec.wav_name())
    r = z.real_generators()["kp_en"](spec, out)
    assert len(seen) == 1 and r["status"] == "OK" and r["fallback_used"] is False
    assert _lock_state(out)["state"] == "RESOLVED"


# ============================================================
# F3: A2外側ループの最終(通算3回目)減速後NG
# ============================================================
PRE_PASS = {"state": "PASS", "slot": 1, "reason": "primary_pass"}
POST_NG = {"state": "NG_BOTH", "slot": 1, "reason": "both_ng"}


def _patch_slowdown_env(monkeypatch, post_status_seq):
    """実apply_a2_slowdown_postprocess+実_post_slowdown_unified_judgeを使い、時間伸長・ASR転写・統一judge(evaluate...)のみ差し替える。"""
    monkeypatch.setattr(n3_tts.a2_slowdown, "apply_a2_slowdown",
                        lambda src, dst: {"src_duration_seconds": 1.0, "dst_duration_seconds": 1.06})
    monkeypatch.setattr(n3_tts.routing, "transcribe", lambda p, language=None: ("transcribed", None))
    seq = list(post_status_seq)
    judged = []

    def fake_eval(canon, asr, prior, wav, **kw):
        ctx = kw.get("attempt_ctx") or {}
        ok = seq.pop(0) == "OK"
        judged.append(bool(ctx.get("is_last_slot")))
        return {"verified": ok, "classification": None, "steps": [{"classification": "TRUE_CONTENT_MISMATCH"}],
                "final_status": "PASS" if ok else "NG_BOTH", "cascade_invoked": True, "stop_retrying": False,
                "human_review_required": (not ok) and bool(ctx.get("is_last_slot")), "canonical_text": canon, "wav_path": wav,
                "cost_guard_triggered": False, "asr_judgement": dict(PRE_PASS if ok else POST_NG)}
    monkeypatch.setattr(n3_tts.secondary_asr, "evaluate_attempt_with_cascade_detail", fake_eval)
    return judged


def _inner_gen_factory(out_path, text, log):
    @lock.guarded_generate("en")
    def inner(t, o, max_attempts=3):
        log.append(max_attempts)
        _tone(o)
        return {"status": "OK", "attempts_log": [{"attempt": 1, "asr_text": "x"}], "asr_judgement": dict(PRE_PASS)}
    return lambda max_attempts: inner(text, out_path, max_attempts=max_attempts)


def test_f3_outer_loop_final_ng_updates_judgement_locks_hr_and_queues_one_row(tmp_path, monkeypatch):
    out = (tmp_path / "t" / "a2" / "narration" / "full_story_part1_c2.wav").as_posix()
    judged = _patch_slowdown_env(monkeypatch, ["NG", "NG", "NG"])
    budgets = []
    r = n3_tts.generate_with_a2_slowdown_outer_loop("full_story_part1_c2", "Hello there.", out,
                                                    _inner_gen_factory(out, "Hello there.", budgets))
    assert budgets == [3, 2, 1] and r["status"] == "STOPPED" and judged == [False, False, True]
    # (i) asr_judgementは減速後NG。減速前PASSは退避
    assert r["asr_judgement"]["state"] == "NG_BOTH" and r["asr_judgement_pre_slowdown"]["state"] == "PASS"
    assert r["asr_judgement_post_slowdown_ng"]["state"] == "NG_BOTH"
    # (ii) LockがHUMAN_REVIEW_REQUIRED、HR queueは最終slotの1行のみ
    st = _lock_state(out)
    assert st["state"] == "HUMAN_REVIEW_REQUIRED" and st["final_status"] == "STOPPED"
    assert st["cumulative_tts_attempts"] == 3          # 実TTS3回(最終finalizeで二重計上しない)
    assert len(_queue_rows(tmp_path)) == 1 and r["human_review_required"] is True
    # Z entryにも反映(stale PASSを残さない)
    plan, _, _ = zt.make_plan("a2")
    entry = z.build_entry(plan[0], out, r)
    assert entry["asr_judgement"]["state"] == "NG_BOTH" and entry["status"] == "STOPPED"


def test_f3_outer_loop_success_on_retry_does_not_finalize(tmp_path, monkeypatch):
    out = (tmp_path / "t" / "a2" / "narration" / "full_story_part1_c2.wav").as_posix()
    _patch_slowdown_env(monkeypatch, ["NG", "OK"])
    budgets = []
    r = n3_tts.generate_with_a2_slowdown_outer_loop("full_story_part1_c2", "Hello there.", out,
                                                    _inner_gen_factory(out, "Hello there.", budgets))
    assert r["status"] == "OK" and budgets == [3, 2]
    assert _lock_state(out)["state"] == "RESOLVED" and _queue_rows(tmp_path) == []
    assert r["asr_judgement"]["state"] == "PASS"
    assert "human_review_required" not in r


def test_f3_outer_loop_inner_failure_is_not_double_recorded(tmp_path, monkeypatch):
    out = (tmp_path / "t" / "a2" / "narration" / "full_story_part1_c2.wav").as_posix()
    _patch_slowdown_env(monkeypatch, [])
    calls = []
    real = lock.record_outcome
    monkeypatch.setattr(lock, "record_outcome", lambda *a, **k: calls.append(1) or real(*a, **k))

    @lock.guarded_generate("en")
    def inner(t, o, max_attempts=3):
        return {"status": "STOPPED", "attempts_log": [{"attempt": 1}, {"attempt": 2}], "reason": "inner ng"}
    r = n3_tts.generate_with_a2_slowdown_outer_loop("full_story_part1_c2", "Hello there.", out,
                                                    lambda m: inner("Hello there.", out, max_attempts=m))
    assert r["status"] == "STOPPED" and calls == [1]                  # 内側guardの1回のみ(外側finalizeは呼ばれない)
    assert _lock_state(out)["state"] == "HUMAN_REVIEW_REQUIRED" and _queue_rows(tmp_path) == []


def test_f3_narrator_loop_same_final_ng_handling(tmp_path, monkeypatch):
    """narrator側(generate_a2_segment_with_slowdown)の同構造にも同じ是正が入っている。"""
    out = (tmp_path / "t" / "a2" / "narration" / "full_story_part1.wav").as_posix()
    judged = _patch_slowdown_env(monkeypatch, ["NG", "NG", "NG"])
    budgets = []

    @lock.guarded_generate("en")
    def fake_inner(text, o, expected, **kw):
        budgets.append(kw.get("max_attempts"))
        _tone(o)
        return {"status": "OK", "attempts_log": [{"attempt": 1, "asr_text": "x"}], "asr_judgement": dict(PRE_PASS)}
    monkeypatch.setattr(n3_tts.c, "generate_english_segment_with_fallback", fake_inner)
    r = n3_tts.generate_a2_segment_with_slowdown("Hello there.", out, "Hello")
    assert budgets == [3, 2, 1] and r["status"] == "STOPPED" and judged == [False, False, True]
    assert r["asr_judgement"]["state"] == "NG_BOTH" and r["asr_judgement_pre_slowdown"]["state"] == "PASS"
    assert _lock_state(out)["state"] == "HUMAN_REVIEW_REQUIRED" and len(_queue_rows(tmp_path)) == 1


def test_f3_direct_apply_postprocess_default_does_not_write_queue(tmp_path, monkeypatch):
    """既定(log_human_review=False)のapply_a2_slowdown_postprocess直接呼出は従来どおりHR queueへ書かない(波及なし)。"""
    out = (tmp_path / "t" / "a2" / "narration" / "p1.wav").as_posix()
    _tone(out)
    _patch_slowdown_env(monkeypatch, ["NG"])
    r = n3_tts.apply_a2_slowdown_postprocess("p1", os.path.dirname(out), "Hello there.",
                                             {"status": "OK", "attempts_log": []}, is_last_slot=True)
    assert r["status"] == "STOPPED" and _queue_rows(tmp_path) == []
