# -*- coding: utf-8 -*-
"""FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02: dialogue TTS attempt policy(ctx -> ctx -> 180秒cooldown -> 従来方式、総3回(2026-10-26: 旧600秒から180秒へ変更))のoffline test(API 0)。

共有ループ `er012_b.generate_voice_body_wide_margin` を、scriptされたfake backend(er122_fz_ctx_fakes_01)で駆動し、policy hook(案A)の
状態機械・永続state・resume・cooldown・上限3・最終slot・二重計上防止を検証する。時間は注入(実180秒は待たない)。ユーザー原文§6受入表の必須6ケース
(1回目PASS/1回目NG→2回目PASS/1・2回目NG→3回目PASS/3回ともNG/retry途中で中断・再開/X・Y不変)に対応。
"""
import ast
import json
import os

import pytest

import er122_fz_ctx_fakes_01 as fk
import er122_fz_ctx_policy_01 as pol

ROOT = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(ROOT, "docs", "research", "FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01", "golden", "golden_hook_none_01.json")
CTX_STYLE = "BASE STYLE\n\nCONTEXT FOR THIS ONE LINE (unit test marker) ctx-body"
CTX_SHA = pol._sha256_text(CTX_STYLE)
OK = (True, False, "EXACT_MATCH")
NG = (False, False, "TRUE_CONTENT_MISMATCH")


class Clock:
    def __init__(self, t=1_000_000.0):
        self.t = t
        self.sleeps = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


class Crash(Exception):
    pass


@pytest.fixture
def env(tmp_path, monkeypatch):
    clk = Clock()
    monkeypatch.setattr(pol.RUNTIME, "clock", clk.now)
    monkeypatch.setattr(pol.RUNTIME, "sleep", clk.sleep)
    stops = []

    class E:
        pass
    e = E()
    e.clk, e.stops, e.tmp = clk, stops, tmp_path
    e.crash_at = None

    def stop_check(where):
        stops.append(where)
        if e.crash_at is not None and e.crash_at(where):
            raise Crash(where)
    e.stop_check = stop_check
    return e


def make_world(tts, evals, tmp_root):
    w = fk.World(tts, evals, tmp_root=str(tmp_root))
    return w


def level_dir_of(w):
    return os.path.dirname(os.path.dirname(w.out_path))     # <tmp>/theme/b1b


def open_policy(env, w, **kw):
    return pol.DialogueAttemptPolicy(level_dir_of(w), "full_story_part1_c3", fk.TEXT, CTX_STYLE, CTX_SHA, out_path=w.out_path, stop_check=env.stop_check, **kw)


def run_std(env, w, policy=None, **kw):
    import er012_b_family_voices_production_01 as bv
    policy = policy or open_policy(env, w, **kw)
    saved = policy.saved_result()
    if saved is not None:
        return saved, policy
    with w.patched():
        r = bv.generate_voice_body_wide_margin(fk.TEXT, w.out_path, "Puck", max_attempts=policy.remaining(), attempt_hook=policy)
    policy.mark_counted()
    policy.finish(r)
    return r, policy


def legacy_prompt():
    g = json.load(open(GOLDEN, encoding="utf-8"))
    return g["single"]["S1_success"]["prompts"][0]


def has_ctx(prompt):
    return "CONTEXT FOR THIS ONE LINE" in prompt


# ---------------------------------------------------------------- ユーザー原文§6 受入表
def test_case1_first_pass_adopts_ctx(env):
    w = make_world([True], [OK], env.tmp)
    r, p = run_std(env, w)
    assert r["status"] == "OK" and w.tts_i == 1 and p.n_started == 1
    assert has_ctx(w.prompts[0]) and CTX_STYLE in w.prompts[0]
    assert p.st["status"] == "DONE_OK" and p.evidence()["final_mode"] == "ctx"
    assert env.clk.sleeps == []


def test_case2_first_ng_then_ctx_immediately_no_wait(env):
    w = make_world([True, True], [NG, OK], env.tmp)
    r, p = run_std(env, w)
    assert r["status"] == "OK" and w.tts_i == 2
    assert has_ctx(w.prompts[0]) and has_ctx(w.prompts[1])
    assert env.clk.sleeps == []                       # 即時Retry(待機0)
    assert p.evidence()["final_mode"] == "ctx" and p.evidence()["cooldown"] is None


def test_case3_two_ng_then_cooldown_180_then_legacy_style_adopted(env):
    w = make_world([True, True, True], [NG, NG, OK], env.tmp)
    r, p = run_std(env, w)
    assert r["status"] == "OK" and w.tts_i == 3
    assert has_ctx(w.prompts[0]) and has_ctx(w.prompts[1]) and not has_ctx(w.prompts[2])
    assert abs(sum(env.clk.sleeps) - 180.0) < 1e-6 and max(env.clk.sleeps) <= pol.SLICE_SECONDS      # 実時間180秒を5秒刻みで
    assert sum(1 for s in env.stops if s.startswith("tts_cooldown")) >= 35
    assert p.evidence()["final_mode"] == "legacy_fallback" and p.evidence()["cooldown"]["total_elapsed_since_ref_seconds"] >= 180
    # 待機は2回目NGの後・3回目の前の1回だけ(1〜2回目の間は0)
    assert p.st["attempts"][2]["started_epoch"] - p.st["attempts"][1]["finished_epoch"] >= 180


def test_case3b_cooldown_constant_is_the_single_180_definition():
    import er020_tts_retry_local_rewrite_01 as er020
    import er127_tts_block_policy_01 as er127
    assert pol.cooldown_seconds() == er127.COOLDOWN_SECONDS == 180.0 and er020.LEGACY_COOLDOWN_SECONDS == 600.0      # 唯一の定義=er127(180)。旧600はscope外(A/B/C)専用
    src = open(os.path.join(ROOT, "er122_fz_ctx_policy_01.py"), encoding="utf-8").read()
    assert "os.environ" not in src and "getenv" not in src      # env/flagで短縮・ON/OFFできない


def test_case4_three_ng_stopped_hr_lock_no_fourth_no_lr(env, monkeypatch):
    import er011_human_review_lock_01 as review_lock
    w = make_world([True, True, True, True], [NG, NG, NG, OK], env.tmp)
    r, p = run_std(env, w)
    assert r["status"] == "STOPPED" and w.tts_i == 3            # 4回目なし
    assert p.st["status"] == "TERMINAL_NG" and p.n_started == 3
    with w.patched():
        chk = review_lock.check_before_generation(w.out_path, fk.TEXT, "en")
    assert chk["proceed"] is False and chk["status"] == "HUMAN_REVIEW_REQUIRED"      # Review Lock(0 API)
    # 再実行しても生成0(Lockが先にblock。さらにlockが無くてもpolicyが3回超過を許さない)
    w2 = make_world([True, True, True], [OK, OK, OK], env.tmp)
    w2.out_path = w.out_path
    r2, p2 = run_std(env, w2)
    assert w2.tts_i == 0 and r2["status"] == "HUMAN_REVIEW_LOCKED"


def test_case4b_without_lock_policy_alone_refuses_fourth(env):
    w = make_world([True, True, True], [NG, NG, NG], env.tmp)
    r, p = run_std(env, w)
    assert r["status"] == "STOPPED" and p.st["status"] == "TERMINAL_NG"
    import er011_human_review_lock_01 as review_lock
    # lockを消した状況(別run dirのlock等)を模擬: lockを外してもstateが3回消費済みなら生成0
    store = os.path.join(level_dir_of(w), "audit")
    for fn in os.listdir(store):
        if fn.startswith("review_lock_state"):
            os.remove(os.path.join(store, fn))
    w2 = make_world([True], [OK], env.tmp)
    w2.out_path = w.out_path
    r2, p2 = run_std(env, w2)
    assert w2.tts_i == 0 and r2["status"] == "STOPPED" and p2.remaining() == 0


# ---------------------------------------------------------------- resume / 中断再開
def test_case5a_interrupt_after_first_ng_resumes_at_second_not_rerun(env):
    env.crash_at = lambda where: where.endswith(":n2")
    w = make_world([True, True, True], [NG, OK, OK], env.tmp)
    with pytest.raises(Crash):
        run_std(env, w)
    assert w.tts_i == 1 and json.load(open(pol.StateStore(level_dir_of(w)).path))["clips"]["full_story_part1_c3"]["n_started"] == 1
    # 再開(別policy object=別process相当)
    env.crash_at = None
    w2 = make_world([True, True], [OK, OK], env.tmp)
    w2.out_path = w.out_path
    r, p = run_std(env, w2)
    assert r["status"] == "OK" and w2.tts_i == 1                       # n=2のみ(n=1は再実行されない)。総TTS=1+1
    assert has_ctx(w2.prompts[0]) and p.n_started == 2 and p.evidence()["resumed_from_process_state"] is True
    assert env.clk.sleeps == []


def test_case5b_interrupt_during_cooldown_resumes_waiting_only_remaining_then_n3(env):
    state = {"slices": 0}

    def crash(where):
        if where.startswith("tts_cooldown"):
            state["slices"] += 1
            return state["slices"] == 21       # 約100秒待った後に落ちる
        return False
    env.crash_at = crash
    w = make_world([True, True, True], [NG, NG, OK], env.tmp)
    with pytest.raises(Crash):
        run_std(env, w)
    waited1 = sum(env.clk.sleeps)
    assert 90 <= waited1 <= 110 and w.tts_i == 2
    # 落ちている間に実時間が60秒進み、再開
    env.clk.t += 60.0
    env.crash_at = None
    env.clk.sleeps.clear()
    w2 = make_world([True], [OK], env.tmp)
    w2.out_path = w.out_path
    r, p = run_std(env, w2)
    assert r["status"] == "OK" and w2.tts_i == 1 and not has_ctx(w2.prompts[0])     # 1〜2回目を再実行せずn=3の従来方式のみ
    waited2 = sum(env.clk.sleeps)
    assert abs((waited1 + 60.0 + waited2) - 180.0) < 1e-6 or (waited1 + 60.0 + waited2) >= 180.0
    assert waited2 < 180.0 - 100 + 60 and p.evidence()["cooldown"]["resumed"] is True
    assert p.evidence()["cooldown"]["total_elapsed_since_ref_seconds"] >= 180.0       # 再開でも前回NGから180秒以上
    assert p.evidence()["final_mode"] == "legacy_fallback"


def test_case5c_resume_after_cooldown_elapsed_waits_zero(env):
    env.crash_at = lambda where: where.startswith("tts_cooldown")
    w = make_world([True, True, True], [NG, NG, OK], env.tmp)
    with pytest.raises(Crash):
        run_std(env, w)
    env.clk.t += 3600.0
    env.crash_at = None
    env.clk.sleeps.clear()
    w2 = make_world([True], [OK], env.tmp)
    w2.out_path = w.out_path
    r, p = run_std(env, w2)
    assert env.clk.sleeps == [] and r["status"] == "OK" and w2.tts_i == 1


def test_started_but_unfinished_attempt_counts_as_consumed(env):
    """TTS中に落ちた(n=1 started・未完了)=消費済み。再開はn=2から(最大3回を超えない)。"""
    w = make_world([True, True, True], [OK, OK, OK], env.tmp)
    w.before_tts = lambda world: (_ for _ in ()).throw(Crash("tts crash")) if world.tts_i == 0 else None
    with pytest.raises(Crash):
        run_std(env, w)
    w2 = make_world([True, True], [OK, OK], env.tmp)
    w2.out_path = w.out_path
    r, p = run_std(env, w2)
    assert p.n_started == 2 and r["status"] == "OK" and has_ctx(w2.prompts[0])


def test_n3_started_then_crash_resume_has_zero_remaining_and_stops_with_lock(env):
    """n=3(従来方式)開始後に落ちた -> 再開は4回目を回さず、STOPPED+Review Lock(HR)で終わる(0 API)。"""
    w = make_world([True, True, True], [NG, NG, OK], env.tmp)
    w.before_tts = lambda world: (_ for _ in ()).throw(Crash("n3 tts crash")) if world.tts_i == 2 else None
    with pytest.raises(Crash):
        run_std(env, w)
    assert pol.StateStore(level_dir_of(w)).get("full_story_part1_c3")["n_started"] == 3
    env.clk.t += 5000.0
    w2 = make_world([True], [OK], env.tmp)
    w2.out_path = w.out_path
    r, p = run_std(env, w2)
    assert w2.tts_i == 0 and r["status"] == "STOPPED" and p.n_started == 3
    import er011_human_review_lock_01 as review_lock
    with w2.patched():
        assert review_lock.check_before_generation(w.out_path, fk.TEXT, "en")["proceed"] is False


# ---------------------------------------------------------------- M-1 二重計上 / M-2 最終slot
def test_m1_carried_log_only_uncounted_rows_and_prior_generations(env):
    env.crash_at = lambda where: where.endswith(":n2")
    w = make_world([True, True], [NG, OK], env.tmp)
    with pytest.raises(Crash):
        run_std(env, w)          # n=1は完了済み・未計上(guarded呼出が戻らず落ちた)
    p = open_policy(env, w)
    assert p.prior_generations() == 0
    rows = p.carried_log()
    assert len(rows) == 1 and rows[0]["overall_attempt_n"] == 1 and p.carried_log() == []      # 1回だけ返す
    # 計上済みになった試行は次回carried対象外(Adv pass1完了後の落ち)
    p.mark_counted()
    p2 = open_policy(env, w)
    assert p2.carried_log() == [] and p2.prior_generations() == 1


def test_m1_record_outcome_counts_each_attempt_exactly_once_across_resume(env, monkeypatch):
    import er011_human_review_lock_01 as review_lock
    seen = []
    real = review_lock.record_outcome

    def spy(out_path, text, language, result, *a, **k):
        seen.append(len(result.get("attempts_log") or []))
        return real(out_path, text, language, result, *a, **k)
    monkeypatch.setattr(review_lock, "record_outcome", spy)
    env.crash_at = lambda where: where.endswith(":n2")
    w = make_world([True, True], [NG, OK], env.tmp)
    with pytest.raises(Crash):
        run_std(env, w)
    env.crash_at = None
    w2 = make_world([True], [OK], env.tmp)
    w2.out_path = w.out_path
    r, p = run_std(env, w2)
    assert seen == [2]                                   # 再開passのrecord_outcome: carried(n=1)+新規(n=2)=2行。n=1を二重に数えない
    assert len(r["attempts_log"]) == 2 and [a["overall_attempt_n"] for a in r["attempts_log"]] == [1, 2]


def test_m2_resume_final_slot_matches_overall_n_and_hr_queue_row_exists(env):
    env.crash_at = lambda where: where.endswith(":n2")
    w = make_world([True, True, True], [NG, NG, NG], env.tmp)
    with pytest.raises(Crash):
        run_std(env, w)
    env.crash_at = None
    w2 = make_world([True, True], [NG, NG], env.tmp)
    w2.out_path = w.out_path
    r, p = run_std(env, w2)
    # 再開後: max_attempts=remaining=2。ループ内2番目=通算n=3。FZ-DIALOGUE-LR-ADOPTION-01: 最終slotは通算n=6だけ(n=3はLR前の③=最終slotではない)なので、
    # 判定器はこの時点でHR queue行を書かない(LR段を経た終端でdriverのregister_terminal_hrが1行を保証する。test_lr_* が固定)
    assert [c["is_last_slot"] for c in w2.attempt_ctxs] == [False, False]
    assert [c["slot"] for c in w2.attempt_ctxs] == [2, 3] and all(c["slot_offset"] if "slot_offset" in c else True for c in w2.attempt_ctxs)
    assert len(w2.hr_queue) == 0 and r["status"] == "STOPPED"
    assert p.n_started == 3


def test_m2_no_resume_last_slot_only_at_n6_not_at_n3(env):
    w = make_world([True, True, True], [NG, NG, NG], env.tmp)
    run_std(env, w)
    assert [c["is_last_slot"] for c in w.attempt_ctxs] == [False, False, False] and len(w.hr_queue) == 0     # n=3はLR前(最終slotではない)
    assert [c["slot"] for c in w.attempt_ctxs] == [1, 2, 3]


def test_attempt_ctx_slot_6_is_the_only_last_slot_and_lr_block_uses_v1_and_m1_anchor(env):
    """B2(LR block)のattempt_ctx: slot=通算n(4〜6)、total_slots=6、script_version='v1'、m1_anchor_text=元原稿。is_last_slotはn=6のみ。"""
    w = make_world([True] * 6, [NG] * 6, env.tmp)
    p = open_policy(env, w)
    with w.patched():
        import er012_b_family_voices_production_01 as bv
        bv.generate_voice_body_wide_margin(fk.TEXT, w.out_path, "Puck", max_attempts=p.remaining(), attempt_hook=p)
        assert p.enter_lr_phase() is True
        p.save_lr_text(fk.TEXT + " rewritten")
        bv.generate_voice_body_wide_margin(fk.TEXT + " rewritten", w.out_path, "Puck", max_attempts=p.remaining(), attempt_hook=p)
    assert [c["slot"] for c in w.attempt_ctxs] == [1, 2, 3, 4, 5, 6]
    assert [c["is_last_slot"] for c in w.attempt_ctxs] == [False] * 5 + [True]
    assert [c.get("script_version") for c in w.attempt_ctxs] == ["v0", "v0", "v0", "v1", "v1", "v1"]
    assert [c.get("m1_anchor_text") for c in w.attempt_ctxs] == [None] * 3 + [fk.TEXT] * 3


# ---------------------------------------------------------------- 技術失敗 / minimal_fallback の扱い
def test_technical_failure_inside_ctx_attempt_uses_minimal_fallback_and_is_recorded(env):
    """ctx試行内のminimal_fallbackは既存の技術安全装置として許容。最終方式として minimal_fallback_in_ctx_attempt を記録する(Opus)。"""
    w = make_world([False, True], [OK], env.tmp)
    r, p = run_std(env, w)
    assert r["status"] == "OK" and p.n_started == 1
    assert p.evidence()["final_mode"] == "minimal_fallback_in_ctx_attempt"
    assert [a["tts_mode_effective"] for a in r["attempts_log"] if a.get("tts_mode_effective")] == ["minimal_fallback_in_ctx_attempt"]


def test_technical_failure_row_counts_two_rows_for_one_attempt(env):
    w = make_world([False, False, True, True, True], [NG, OK], env.tmp)
    r, p = run_std(env, w)
    assert p.st["attempts"][0]["rows"] == 2 and p.n_started >= 2


# ---------------------------------------------------------------- 状態遷移の判別(M-4)
def test_m4_done_ok_adopted_without_api_when_no_explicit_signal(env):
    w = make_world([True], [OK], env.tmp)
    r, p = run_std(env, w)
    assert r["status"] == "OK"
    w2 = make_world([True], [OK], env.tmp)
    w2.out_path = w.out_path
    r2, p2 = run_std(env, w2)                  # checkpoint欠落の再開(確定直後クラッシュ相当): 保存結果を採用
    assert w2.tts_i == 0 and r2["status"] == "OK" and r2["dialogue_tts"]["adopted_saved_result"] is True
    assert r2["path"] == r["path"] and r2["asr_text"] == r["asr_text"]


def test_m4_explicit_regenerate_starts_new_cycle(env):
    w = make_world([True], [OK], env.tmp)
    run_std(env, w)
    w2 = make_world([True], [OK], env.tmp)
    w2.out_path = w.out_path
    r2, p2 = run_std(env, w2, explicit_regenerate=True)
    assert w2.tts_i == 1 and p2.n_started == 1 and p2.st["cycle"] == 2
    assert p2.st["history"][0]["reason_for_restart"] == "explicit_regenerate" and p2.st["history"][0]["ended_status"] == "DONE_OK"


def test_m4_consuming_regenerate_approval_starts_new_cycle(env):
    import er011_human_review_lock_01 as review_lock
    w = make_world([True, True, True], [NG, NG, NG], env.tmp)
    run_std(env, w)
    w2 = make_world([True], [OK], env.tmp)
    w2.out_path = w.out_path
    with w2.patched():
        review_lock.approve_regenerate(w.out_path, fk.TEXT)                      # ユーザーの明示再生成承認(REGENERATE_APPROVED)
        flag = bool(review_lock.check_before_generation(w.out_path, fk.TEXT, "en").get("consuming_regenerate_approval"))
    assert flag is True
    r2, p2 = run_std(env, w2, consuming_regenerate_approval=flag)
    assert p2.st["cycle"] == 2 and p2.n_started == 1 and w2.tts_i == 1 and r2["status"] == "OK"


def test_m4_text_or_style_change_starts_new_cycle(env):
    w = make_world([True], [OK], env.tmp)
    run_std(env, w)
    w2 = make_world([True], [OK], env.tmp)
    w2.out_path = w.out_path
    p2 = pol.DialogueAttemptPolicy(level_dir_of(w2), "full_story_part1_c3", fk.TEXT + " More.", CTX_STYLE, CTX_SHA, out_path=w2.out_path, stop_check=env.stop_check)
    assert p2.st["cycle"] == 2 and p2.n_started == 0 and "state_mismatch" in p2.st["history"][0]["reason_for_restart"]
    p3 = pol.DialogueAttemptPolicy(level_dir_of(w2), "full_story_part1_c3", fk.TEXT, CTX_STYLE + "x", pol._sha256_text(CTX_STYLE + "x"), out_path=w2.out_path,
                                   stop_check=env.stop_check)
    assert p3.st["cycle"] == 3 and "state_mismatch" in p3.st["history"][-1]["reason_for_restart"]


def test_m4_saved_wav_changed_starts_new_cycle_not_adopting(env):
    w = make_world([True], [OK], env.tmp)
    run_std(env, w)
    with open(w.out_path, "ab") as f:
        f.write(b"x")                               # wavがstate保存時と異なる
    p2 = open_policy(env, w)
    assert p2.saved_result() is None and p2.st["cycle"] == 2 and p2.st["history"][0]["reason_for_restart"].startswith("done_ok_but_saved_wav")


def test_resume_with_only_clips_signal_still_continues_in_progress_cycle(env):
    """--only-clips(explicit)で起動した実行が途中で落ち、同じ引数で再開した場合も、同一サイクルの再開であり1〜2回目を再実行しない。"""
    env.crash_at = lambda where: where.endswith(":n2")
    w = make_world([True, True], [NG, OK], env.tmp)
    with pytest.raises(Crash):
        run_std(env, w, explicit_regenerate=True)
    env.crash_at = None
    w2 = make_world([True], [OK], env.tmp)
    w2.out_path = w.out_path
    r, p = run_std(env, w2, explicit_regenerate=True)
    assert w2.tts_i == 1 and p.n_started == 2 and p.st["cycle"] == 1


# ---------------------------------------------------------------- STOP / state原子書込
def test_stop_checked_before_every_attempt(env):
    w = make_world([True, True, True], [NG, NG, OK], env.tmp)
    run_std(env, w)
    assert [s for s in env.stops if s.startswith("tts_attempt")] == [f"tts_attempt:full_story_part1_c3:n{i}" for i in (1, 2, 3)]


def test_stop_during_cooldown_keeps_resume_anchor(env):
    env.crash_at = lambda where: where.startswith("tts_cooldown")
    w = make_world([True, True, True], [NG, NG, OK], env.tmp)
    with pytest.raises(Crash):
        run_std(env, w)
    st = pol.StateStore(level_dir_of(w)).get("full_story_part1_c3")
    assert st["cooldown"]["ref_epoch"] and st["cooldown"]["ended_epoch"] is None and st["n_started"] == 2


def test_state_write_is_atomic_no_tmp_left(env):
    w = make_world([True], [OK], env.tmp)
    run_std(env, w)
    d = os.path.join(level_dir_of(w), "audit")
    assert not [f for f in os.listdir(d) if f.endswith(".tmp")]
    assert json.load(open(os.path.join(d, "dialogue_ctx_attempt_state.json"), encoding="utf-8"))["schema"] == pol.STATE_SCHEMA


def test_corrupt_state_is_technical_stop_not_silently_forgotten(env):
    w = make_world([True], [OK], env.tmp)
    run_std(env, w)
    p = pol.StateStore(level_dir_of(w)).path
    open(p, "w").write("{not json")
    import er063_family_z_audio_01 as z
    with pytest.raises(z.FamilyZDialogueCtxStop):
        open_policy(env, w)


# ---------------------------------------------------------------- 従来方式への完全復帰(TEST-05)
def test_fallback_attempt_prompt_is_byte_identical_to_baseline_legacy_prompt(env):
    w = make_world([True, True, True], [NG, NG, OK], env.tmp)
    run_std(env, w)
    assert w.prompts[2] == legacy_prompt()                           # 基準commit(ab111631c相当)で凍結したgoldenの旧prompt
    assert not has_ctx(w.prompts[2]) and "CONTEXT" not in w.prompts[2] and "unit test marker" not in w.prompts[2]
    for t in ("Speaker of this line", "Spoken line before", "Narration just before", "Manner words", "ctx-body"):
        assert t not in w.prompts[2]


def test_before_attempt_3_returns_no_style_override(env):
    w = make_world([True], [OK], env.tmp)
    p = open_policy(env, w)
    d1, d2 = p.before_attempt(1, 3, w.out_path), None
    p.after_attempt(1, [], False, "x")
    d2 = p.before_attempt(2, 3, w.out_path)
    p.after_attempt(2, [], False, "x")
    d3 = p.before_attempt(3, 3, w.out_path)
    assert d1["style_prefix_override"] == CTX_STYLE and d2["style_prefix_override"] == CTX_STYLE and d3["style_prefix_override"] is None
    stop = p.before_attempt(4, 3, w.out_path)      # B1の4回目はLR未実施では存在しない(fail-closed。LRを経てphase=B2になるまで開かない)
    assert stop["stop"] is True and stop["reason"].startswith("ATTEMPT_BUDGET_EXHAUSTED(phase=B1")


# ---------------------------------------------------------------- hook=None のparity(golden)
@pytest.mark.skipif(not os.path.exists(GOLDEN), reason="golden未凍結")
def test_hook_none_is_byte_identical_to_frozen_golden_for_all_scenarios():
    g = json.load(open(GOLDEN, encoding="utf-8"))
    for name in fk.SCENARIOS:
        assert json.loads(json.dumps(fk.run_single(name), sort_keys=True)) == g["single"][name], name
    for name, (seq, post) in fk.OUTER_SCENARIOS.items():
        assert json.loads(json.dumps(fk.run_outer(name, seq, post), sort_keys=True)) == g["outer"][name], name


def test_hook_none_outer_loop_prior_generations_default_zero_is_identity():
    seq, post = fk.OUTER_SCENARIOS["O2_post_ng_then_ok"]
    a = fk.run_outer("O2", seq, post)
    b = fk.run_outer("O2", seq, post, prior_generations=0)
    assert a == b
    c = fk.run_outer("O2p", [("OK", 1)], ["OK"], prior_generations=1)        # 前プロセスで計上済み1行 -> 残予算2
    assert c["calls"]["gen"] == [2] and c["result"]["tts_generations_used"] == 2


# ---------------------------------------------------------------- 構造
def test_hook_signature_is_keyword_only_default_none_and_no_new_import_in_shared_modules():
    import inspect
    import er012_b_family_voices_production_01 as bv
    import er003_v1_n3_01_tts_generate as n3
    s = inspect.signature(bv.generate_voice_body_wide_margin)
    prm = s.parameters["attempt_hook"]
    assert prm.kind is inspect.Parameter.KEYWORD_ONLY and prm.default is None
    s2 = inspect.signature(n3.generate_with_a2_slowdown_outer_loop)
    assert s2.parameters["prior_generations"].kind is inspect.Parameter.KEYWORD_ONLY and s2.parameters["prior_generations"].default == 0
    for fn in ("er012_b_family_voices_production_01.py", "er003_v1_n3_01_tts_generate.py"):
        src = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.Import):
                assert not any("er122" in a.name for a in n.names), fn            # 共有moduleは新moduleをimportしない(hookはduck typing)
            if isinstance(n, ast.ImportFrom):
                assert "er122" not in (n.module or ""), fn
