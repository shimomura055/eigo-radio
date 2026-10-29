# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-LR-ADOPTION-01 委任_02: ZセリフLR正式採用(最大TTS6回+LR1回+待機2回)のoffline test(API 0・有料run禁止)。

構成(TEST_PLAN_01の対応): P(Profile/定数) / S(状態機械・全NG経路・途中PASS・kill/resume行列・待機・ブロックゲート・v1互換・再生成・会計) /
L(LR入力選択・候補事前保護・LR block不変条件・HRQ/Lock・技術STOP・stop_retrying・Adv外側ループ) / R(記録・分類・台帳) / M1〜M7(Opus必須修正) / 注入ハーネス隔離。
正式経路 `_run_tts_stage_impl` を fake TTS/ASR/LLM(候補生成・QAだけ差替え、7 Gate/局所性/全文性/candidate_filterは実コード)で駆動する。
"""
import ast
import glob
import json
import os
import re

import pytest

import er063_family_z_audio_01 as z
import er122_fz_ctx_notes_01 as notes
import er122_fz_ctx_policy_01 as pol
import er122_fz_ctx_fakes_01 as fk
import er122_fz_ctx_policy_lr_helpers_01 as H
import er127_tts_block_policy_01 as er127

ROOT = os.path.dirname(os.path.abspath(__file__))
OK, NG, STOPRETRY = H.OK, H.NG, H.STOPRETRY
C3 = H.C3_ID


class Clock:
    def __init__(self, t=3_000_000.0):
        self.t, self.sleeps = t, []

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


class Crash(Exception):
    pass


def _fake_llm(calls):
    def fn(developer, user):
        calls.append(user)
        rows = json.loads(user.split("\n", 1)[1])
        items = [{"clip_id": r["clip_id"], "speaker_state": "He is calm.", "scene": "A quiet room.", "reaction_to_previous": "", "evidence": [r["line"]],
                  "has_explicit_cue": False} for r in rows]
        return {"raw": {"items": items}, "model_returned": "gpt-6-luna-test", "cost_jpy": 0.1}
    return fn


@pytest.fixture
def env(tmp_path, monkeypatch):
    notes.reset_providers_for_test()
    clk = Clock()
    monkeypatch.setattr(pol.RUNTIME, "clock", clk.now)
    monkeypatch.setattr(pol.RUNTIME, "sleep", clk.sleep)
    import er127_tts_block_policy_01 as e127
    monkeypatch.setattr(e127.RUNTIME, "clock", clk.now)
    monkeypatch.setattr(e127.RUNTIME, "sleep", clk.sleep)
    e127.register_stop_check(None)
    stop = {"fn": lambda run_dir, where: None, "log": []}

    def sentinel(run_dir, where):
        stop["log"].append(where)
        stop["fn"](run_dir, where)
    monkeypatch.setattr(z, "_check_stop_sentinel", sentinel)
    llm = []
    notes.LLM_FN = _fake_llm(llm)

    class E:
        pass
    e = E()
    e.clk, e.tmp, e.llm_calls, e.stop = clk, tmp_path, llm, stop
    e.run_dir = str(tmp_path / "run").replace("\\", "/")
    os.makedirs(e.run_dir, exist_ok=True)
    e.history = str(tmp_path / "attempt_history.jsonl")
    yield e
    notes.LLM_FN = None
    notes.reset_providers_for_test()


@pytest.fixture
def hrq(monkeypatch):
    import er006_secondary_asr_01 as secondary_asr
    rows = []
    monkeypatch.setattr(secondary_asr, "_log_human_review", lambda detail: rows.append(detail))
    return rows


@pytest.fixture
def lr(monkeypatch, tmp_path):
    import er020_tts_retry_local_rewrite_01 as er020
    # LR成果物(local_rewrite_recoveryのjson/履歴)をtmpへ(リポジトリに書かない)
    monkeypatch.setattr(er020, "_write_recovery_artifacts", lambda *a, **k: None)
    monkeypatch.setattr(er020, "_append_recovery_history", lambda *a, **k: None)
    monkeypatch.setattr(er020, "_write_pre_retts_audit", lambda *a, **k: None, raising=False)
    return H.FakeLR().install(monkeypatch)


def story_plan(level, c3_text=H.C3_TEXT):
    sc = [{"id": "full_story_part1_c1", "part": 1, "voice": "narrator", "speaker": "narrator", "text": "It was night. Mr. White said softly."},
          {"id": "full_story_part1_c2", "part": 1, "voice": "mr_white", "speaker": "mr_white", "text": H.C2_TEXT},
          {"id": C3, "part": 1, "voice": "morris", "speaker": "morris", "text": c3_text}]
    plan = z.build_level_plan(level, sc, "preview", {1: "c1", 2: "c2", 3: "c3"}, [], "T", japanese_title_text="x", story_key=H.STORY)
    return [s for s in plan if s.kind in ("narrator", "dialogue")]


def fake_narrator(spec, out_path):
    import numpy as np
    import er002_common as common
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    common.write_wav_float(out_path, np.zeros(2400, dtype=np.float32), common.SAMPLE_RATE, 1)
    return {"status": "OK", "path": out_path, "asr_text": spec.text, "attempts_log": [{"attempt": 1, "status": "OK", "verified": True}]}


def real_gens():
    d = z.real_generators()["dialogue"]
    return {"narrator": fake_narrator, "dialogue": d}


def world(env, c3_tts, c3_evals, *, asr_by_c3_attempt=None, with_c2=True):
    """c2(1回OK)+c3(c3_tts/c3_evals)。asr_by_c3_attempt={c3の評価通番(0始まり): 転写}。再開runはc2を再利用する(TTSなし)ので with_c2=False。"""
    pre_t, pre_e = ([True], [OK]) if with_c2 else ([], [])
    w = H.TWorld(pre_t + list(c3_tts), pre_e + list(c3_evals), tmp_root=str(env.tmp / "w"))
    w.asr_text = "ok"
    for k, v in (asr_by_c3_attempt or {}).items():
        w.asr_by_eval[k + len(pre_e)] = v
    return w


def run_stage(env, level, w, plan=None, only_clips=None):
    plan = plan or story_plan(level)
    with w.patched():
        return z._run_tts_stage_impl(env.run_dir, level, plan, generators=real_gens(), only_clips=only_clips, story_key=H.STORY), plan


@pytest.fixture
def adv_post(monkeypatch):
    import er003_v1_n3_01_tts_generate as n3
    seq = {"i": 0, "script": [], "calls": []}

    def post(name, narration_dir, tts_input, result, is_last_slot=False, log_human_review=True, **k):
        st = seq["script"][seq["i"]] if seq["i"] < len(seq["script"]) else "OK"
        seq["i"] += 1
        seq["calls"].append({"name": name, "tts_input": tts_input, "is_last_slot": is_last_slot, **k})
        r = dict(result)
        r["status"] = st
        r.setdefault("slowdown_applied", True)
        r["post_slowdown_asr_text"] = k.get("_asr") or result.get("asr_text")
        r["post_slowdown_classification"] = "TRUE_CONTENT_MISMATCH" if st != "OK" else "EXACT_MATCH"
        if st != "OK":
            r["reason"] = "fake post-slowdown NG"
        return r
    monkeypatch.setattr(n3, "apply_a2_slowdown_postprocess", post)
    return seq


def n_started(env, level):
    return H.load_state(env.run_dir, level)["n_started"]


CTX_MARK = "CONTEXT FOR THIS ONE LINE"


def kinds(w, skip=1):
    """c3のprompt列(先頭はc2)を ctx / legacy に分類"""
    return ["ctx" if CTX_MARK in p else "legacy" for p in w.prompts[skip:]]


# =====================================================================================================
# P: Profile / 定数
# =====================================================================================================
def test_p1_profile_z_dlg_ctx_is_lr_six_two_and_other_profiles_unchanged():
    p = er127.PROFILES["Z_DLG_CTX"]
    assert (p.lr, p.total_slots, p.max_tts, p.max_waits, p.third_style, p.block_attempts, p.cooldown_before) == (True, 6, 6, 2, "LEGACY_DIALOGUE", 3, (3,))
    assert set(er127.PROFILES) == {"EN_LR_STD", "EN_LR_ADV", "JA_STD", "KP_EN", "KP_EXPL", "Z_DLG_CTX", "Z_DLG_LEGACY", "SHELL_EN", "NO_TTS"}   # 9 policy名集合不変
    expect = {"EN_LR_STD": (True, 6, 6, 2), "EN_LR_ADV": (True, 6, 6, 2), "JA_STD": (False, 3, 3, 1), "KP_EN": (False, 4, 4, 1), "KP_EXPL": (False, 3, 3, 1),
              "Z_DLG_LEGACY": (False, 3, 3, 1), "SHELL_EN": (False, 3, 3, 0), "NO_TTS": (False, 0, 0, 0)}
    for k, v in expect.items():
        q = er127.PROFILES[k]
        assert (q.lr, q.total_slots, q.max_tts, q.max_waits) == v, k
    from er130_adopted_take_classifier_01 import _allowed_fallback_slots
    assert _allowed_fallback_slots(p, "x") == {3, 6}


def test_p2_legacy_policy_unchanged_no_lr(env, hrq):
    """policy=legacy(既存run・ロールバック)は従来動作(LRなし・3回)。3回NGで終端、LR LLMなし。"""
    import er122_fz_ctx_policy_01 as P
    P.Z_DIALOGUE_CTX_POLICY_DEFAULT = "legacy"
    try:
        w = world(env, [True] * 3, [NG] * 3)
        run_stage(env, "a2", w)
        assert w.tts_i == 1 + 3
        assert not os.path.exists(f"{env.run_dir}/a2/audit/dialogue_ctx_attempt_state.json")      # legacyはstateを作らない
    finally:
        P.Z_DIALOGUE_CTX_POLICY_DEFAULT = "fz_ctx_v1"


def test_p3_constants_are_consistent_single_source():
    assert pol.MAX_TOTAL_ATTEMPTS == er127.PROFILES["Z_DLG_CTX"].max_tts == er127.PROFILES["Z_DLG_CTX"].total_slots == 2 * pol.block_attempts() == 6
    import er011_human_review_lock_01 as rl
    assert pol.block_attempts() == rl.PRODUCTION_MAX_TTS_ATTEMPTS == er127.BLOCK_ATTEMPTS == 3
    src = open(os.path.join(ROOT, "er122_fz_ctx_policy_01.py"), encoding="utf-8").read()
    assert not re.search(r"MAX_TOTAL_ATTEMPTS\s*=\s*3\b", src)
    assert "os.environ" not in src and "getenv" not in src
    # 外側ループ既定予算=ブロック長(3)のまま(既存呼出の挙動を変えない)
    import inspect
    import er003_v1_n3_01_tts_generate as n3
    sig = inspect.signature(n3.generate_with_a2_slowdown_outer_loop)
    for k, d in (("total_budget", None), ("slot_offset", None), ("total_slots", None), ("final_block", True), ("lock_text", None), ("record_lock", True),
                 ("prior_generations", 0)):
        assert sig.parameters[k].default == d and sig.parameters[k].kind is inspect.Parameter.KEYWORD_ONLY, k


# =====================================================================================================
# S: 状態機械(正式経路 e2e)
# =====================================================================================================
def test_s1_std_full_ng_path_six_tts_one_lr_two_waits_then_terminal(env, hrq, lr):
    """①②ctx→180→③従来→LR→①'②'ctx→180→③'従来→HR。実TTS6・LR1・待機2。"""
    w = world(env, [True] * 6, [NG] * 6, asr_by_c3_attempt={0: H.C3_ASR_NG, 1: H.C3_ASR_NG, 2: H.C3_ASR_NG})
    run_stage(env, "a2", w)
    assert w.tts_i == 1 + 6 and kinds(w) == ["ctx", "ctx", "legacy", "ctx", "ctx", "legacy"]
    assert len(lr.gen_calls) == 1
    assert [s for s in env.clk.sleeps if s] and abs(sum(env.clk.sleeps) - 360.0) < 1e-6 and max(env.clk.sleeps) <= pol.SLICE_SECONDS
    st = H.load_state(env.run_dir, "a2")
    assert st["status"] == "TERMINAL_NG" and st["n_started"] == 6 and st["lr"]["state"] == "UNRESOLVED" and st["phase"] == "B2"
    assert sorted(st["cooldowns"]) == ["3", "6"] and all(c["total_elapsed_since_ref_seconds"] >= 180 for c in st["cooldowns"].values())
    assert [(a["n"], a["block"], a["ordinal"], a["mode"]) for a in st["attempts"]] == [(1, 0, 1, "ctx"), (2, 0, 2, "ctx"), (3, 0, 3, "legacy_fallback"),
                                                                                     (4, 1, 1, "ctx"), (5, 1, 2, "ctx"), (6, 1, 3, "legacy_fallback")]
    # LR block(④⑤⑥)は書換え後の本文を送る。元ブロック(①②③)は元原稿
    assert H.C3_TEXT.replace("really sure", "really certain") in w.prompts[4] and H.C3_TEXT in w.prompts[1] and "certain" not in w.prompts[1]
    # HRQ=終端NG1行、Lock=HR、累積TTS=6(行数どおり)
    assert len(hrq) == 1 and hrq[0]["canonical_text"] == H.C3_TEXT.replace("really sure", "really certain")
    lk = H.load_lock(env.run_dir, "a2")
    assert lk["state"] == "HUMAN_REVIEW_REQUIRED" and lk["cumulative_tts_attempts"] == 6 and lk["canonical_text_sha256"] == pol._sha256_text(z._norm_for_tts(story_plan("a2")[2]))
    e3 = H.results(env.run_dir, "a2")[C3]
    assert e3["status"] != "OK" and e3["dialogue_tts"]["n_started"] == 6 and e3["dialogue_tts"]["lr_state"] == "UNRESOLVED"


@pytest.mark.parametrize("pass_at", [1, 2, 3, 4, 5, 6])
def test_s2_std_pass_at_n_stops_immediately(env, hrq, lr, pass_at):
    evals = [NG] * (pass_at - 1) + [OK]
    w = world(env, [True] * pass_at, evals, asr_by_c3_attempt={0: H.C3_ASR_NG, 1: H.C3_ASR_NG, 2: H.C3_ASR_NG})
    run_stage(env, "a2", w)
    seg = H.results(env.run_dir, "a2")[C3]
    assert seg["status"] == "OK" and w.tts_i == 1 + pass_at
    assert len(lr.gen_calls) == (1 if pass_at >= 4 else 0)                       # n<=3 PASSならLR呼出0
    waits = {1: 0, 2: 0, 3: 180, 4: 180, 5: 180, 6: 360}[pass_at]
    assert abs(sum(env.clk.sleeps) - waits) < 1e-6
    fa = seg["final_adoption"]
    exp_depth = 0 if pass_at <= 3 else 1
    exp_ord = pass_at if pass_at <= 3 else pass_at - 3
    assert (fa["depth"], fa["ordinal"], fa["slot"]) == (exp_depth, exp_ord, "①②③"[exp_ord - 1] + ("'" if exp_depth else ""))
    assert fa["style_mode"] == ("FALLBACK" if exp_ord == 3 else "PRIMARY") and (fa["sent_style_sha"] is None) == (exp_ord == 3)
    assert len(hrq) == 0 and H.load_lock(env.run_dir, "a2")["state"] == "RESOLVED"
    assert H.load_state(env.run_dir, "a2")["status"] == "DONE_OK"
    if pass_at >= 4:
        dev = seg["audio_text_deviation"]
        assert seg["dialogue_tts"]["lr_state"] == "RESOLVED" and dev["canonical_text_before_local_rewrite"] == H.C3_TEXT
        assert dev["audio_text_after"] == H.C3_TEXT.replace("really sure", "really certain")
    else:
        assert "local_rewrite_recovery" not in seg


def test_s3_lr_is_at_most_once_and_reentry_is_forbidden(env, hrq, lr):
    w = world(env, [True] * 6, [NG] * 6, asr_by_c3_attempt={0: H.C3_ASR_NG})
    run_stage(env, "a2", w)
    assert len(lr.gen_calls) == 1
    # 再入禁止の多重防御: (1) persisted lr.state (2) LocalRewriteReentryError(depth>=1) (3) run_local_rewrite_recovery(depth>=1)
    p = pol.DialogueAttemptPolicy(f"{env.run_dir}/a2", C3, z._norm_for_tts(story_plan("a2")[2]), "x", H.load_state(env.run_dir, "a2")["ctx_style_sha256"],
                                  out_path=f"{env.run_dir}/a2/narration/{C3}.wav", stop_check=lambda w_: None, explicit_regenerate=False)
    assert p.enter_lr_phase() is False                                           # 終端後・LR使用済みはLR段へ進めない
    with pytest.raises(RuntimeError):
        p.save_lr_text("another rewrite")
    blk1 = pol.ZLrBlockAdapter(p)
    blk1.depth = 1
    with pytest.raises(er127.LocalRewriteReentryError):
        er127.lr_recover(blk1, text="t", out_path=f"{env.run_dir}/a2/narration/{C3}.wav", last_asr_text="x", block_call=lambda a, b: {}, merge=lambda a, b: a, last_attempt=None)
    import er020_tts_retry_local_rewrite_01 as er020
    with pytest.raises(RuntimeError):
        er020.run_local_rewrite_recovery(segment_id=C3, canonical_text="a b c", last_asr_text="a b d", retts_fn=lambda t: {}, depth=1)


def test_s4_kill_resume_matrix_total_real_tts_never_exceeds_six_and_consumed_never_rerun(env, hrq, lr, monkeypatch):
    """各attempt前・各待機中・LR LLM前でkill→再開。実TTSの総数は常に6、LRは1回、消費済みattemptは再実行されない。"""
    points = [f"tts_attempt:{C3}:n{k}" for k in range(2, 7)] + ["tts_cooldown", "lr_llm"]
    for where in points:
        notes.reset_providers_for_test()
        env.run_dir = str(env.tmp / f"run_{abs(hash(where)) % 10**6}").replace("\\", "/")
        os.makedirs(env.run_dir, exist_ok=True)
        lr.gen_calls.clear()
        hit = {"n": 0}

        def stop(run_dir, w_, where=where, hit=hit):
            if w_.startswith(where) and (hit["n"] == 0):
                hit["n"] = 1
                raise Crash(w_)
        env.stop["fn"] = stop
        w1 = world(env, [True] * 6, [NG] * 6, asr_by_c3_attempt={0: H.C3_ASR_NG, 1: H.C3_ASR_NG, 2: H.C3_ASR_NG})
        with pytest.raises(Crash):
            run_stage(env, "a2", w1)
        done1 = H.load_state(env.run_dir, "a2")["n_started"]
        assert H.load_state(env.run_dir, "a2")["status"] == "IN_PROGRESS"
        env.stop["fn"] = lambda run_dir, w_: None
        notes.reset_providers_for_test()
        env.clk.t += 10000.0         # 落ちている間に実時間が進む(待機は消費済み)
        left = 6 - done1
        w2 = world(env, [True] * left, [NG] * left, asr_by_c3_attempt={0: H.C3_ASR_NG, 1: H.C3_ASR_NG, 2: H.C3_ASR_NG}, with_c2=False)
        run_stage(env, "a2", w2)
        st = H.load_state(env.run_dir, "a2")
        assert (w1.tts_i - 1) + w2.tts_i == 6, where                             # c3の実TTS総数=6(再開側はc2を再利用=c2のTTSなし)
        assert st["n_started"] == 6 and st["status"] == "TERMINAL_NG", where
        assert len(lr.gen_calls) == 1, where                                      # LR LLMは全体で1回(再開でも再実行しない)
        assert [a["n"] for a in st["attempts"]] == [1, 2, 3, 4, 5, 6], where
    env.stop["fn"] = lambda run_dir, w_: None


def test_s5_wait_only_before_n3_and_n6_and_stop_during_wait_keeps_state(env, hrq, lr):
    seen = []

    def stop(run_dir, where):
        seen.append(where)
    env.stop["fn"] = stop
    w = world(env, [True] * 6, [NG] * 6, asr_by_c3_attempt={0: H.C3_ASR_NG})
    run_stage(env, "a2", w)
    st = H.load_state(env.run_dir, "a2")
    assert sorted(st["cooldowns"]) == ["3", "6"]                                  # n=2,4,5の前に待機はない
    assert sum(1 for s in seen if s.startswith("tts_cooldown")) >= 70             # 5秒刻みで2回分(約36+36回)STOP確認
    # 待機起点=直前attemptの最終NG確定時刻
    assert st["cooldowns"]["3"]["ref_epoch"] == st["attempts"][1].get("final_ng_epoch") or st["attempts"][1]["finished_epoch"]
    assert st["cooldowns"]["6"]["ref_epoch"] == st["attempts"][4]["finished_epoch"]
    # 待機中STOP: stateは据置(IN_PROGRESS)、n_startedは増えない
    notes.reset_providers_for_test()
    env.run_dir = str(env.tmp / "run_stopwait").replace("\\", "/")
    os.makedirs(env.run_dir, exist_ok=True)
    env.stop["fn"] = lambda run_dir, where: (_ for _ in ()).throw(Crash(where)) if where.startswith("tts_cooldown") else None
    w2 = world(env, [True] * 6, [NG] * 6)
    with pytest.raises(Crash):
        run_stage(env, "a2", w2)
    st2 = H.load_state(env.run_dir, "a2")
    assert st2["status"] == "IN_PROGRESS" and st2["n_started"] == 2 and st2["cooldowns"]["3"]["ended_epoch"] is None
    env.stop["fn"] = lambda run_dir, where: None


def test_s6_block_gates_fail_closed(env):
    ld = f"{env.run_dir}/a2"
    p = pol.DialogueAttemptPolicy(ld, C3, "t", "S", pol._sha256_text("S"), out_path=f"{ld}/narration/{C3}.wav", stop_check=lambda w: None)
    for _ in range(3):
        d = p.before_attempt(1, 3, p.out_path)
        assert not d["stop"]
        p.after_attempt(1, [], False, "x")
    assert p.remaining() == 0 and p.before_attempt(1, 3, p.out_path)["stop"] is True        # B1終端でLR未実施のn=4は存在しない
    with pytest.raises(RuntimeError):
        p.save_lr_text("early")                                                            # phase=B1でLR本文は保存できない
    assert p.enter_lr_phase() is True and p.phase == "LR"
    assert p.remaining() == 0 and p.before_attempt(1, 3, p.out_path)["stop"] is True        # LR本文未保存でB2は開始できない
    p.save_lr_text("rewritten")
    assert p.phase == "B2" and p.remaining() == 3 and not p.before_attempt(1, 3, p.out_path)["stop"]


def test_s7_v1_state_compat(env):
    ld = f"{env.run_dir}/a2"
    os.makedirs(f"{ld}/audit", exist_ok=True)
    sha = pol._sha256_text("CTX")
    base = {"clip_id": C3, "canonical_text_sha256": pol._sha256_text("T"), "policy": "fz_ctx_v1", "ctx_style_sha256": sha, "n_started": 2, "cooldown": None,
            "done": None, "history": [], "created_at": "x", "cycle": 1,
            "attempts": [{"n": 1, "mode": "ctx", "finished": True, "verified": False, "counted": True, "rows": 1, "log_rows": []},
                         {"n": 2, "mode": "ctx", "finished": True, "verified": False, "counted": True, "rows": 1, "log_rows": []}]}
    v1 = {"schema": "fz_dialogue_ctx_attempt_state_v1", "clips": {C3: {**base, "status": "IN_PROGRESS"}}}
    json.dump(v1, open(f"{ld}/audit/dialogue_ctx_attempt_state.json", "w"))
    p = pol.DialogueAttemptPolicy(ld, C3, "T", "CTX", sha, out_path=f"{ld}/narration/{C3}.wav", stop_check=lambda w: None)
    assert p.decision.startswith("resume") and p.phase == "B1" and p.remaining() == 1 and p.lr["state"] == "NOT_STARTED"         # v1 IN_PROGRESSはそのまま継続
    # v1のTERMINAL_NG(n=3)は自動ではLRへ進まない(API 0。remaining=0。enter_lr_phaseもstatusがTERMINAL_NGなので拒否)
    v1["clips"][C3].update({"status": "TERMINAL_NG", "n_started": 3,
                            "attempts": base["attempts"] + [{"n": 3, "mode": "legacy_fallback", "finished": True, "verified": False, "counted": True, "rows": 1, "log_rows": []}]})
    json.dump(v1, open(f"{ld}/audit/dialogue_ctx_attempt_state.json", "w"))
    p2 = pol.DialogueAttemptPolicy(ld, C3, "T", "CTX", sha, out_path=f"{ld}/narration/{C3}.wav", stop_check=lambda w: None)
    assert p2.decision == "terminal_ng:attempts_exhausted" and p2.remaining() == 0 and p2.phase == "B1" and p2.enter_lr_phase() is False
    assert p2.before_attempt(1, 3, p2.out_path)["stop"] is True


def test_s8_regeneration_new_cycle_and_lr_phase_is_never_reset(env, hrq, lr):
    # (a) DONE_OK + explicit_regenerate -> 新規サイクル(6スロット)
    w = world(env, [True], [OK])
    run_stage(env, "a2", w)
    notes.reset_providers_for_test()
    rp = f"{env.run_dir}/a2/audit/tts_generation_results.json"
    d = json.load(open(rp, encoding="utf-8"))
    d["segments"].pop(C3)                  # 運用上の明示再生成(entryを外す)+ --only-clips
    json.dump(d, open(rp, "w", encoding="utf-8"))
    w2 = world(env, [True], [OK], with_c2=False)
    run_stage(env, "a2", w2, only_clips={C3})
    st = H.load_state(env.run_dir, "a2")
    assert st["cycle"] == 2 and st["history"][-1]["reason_for_restart"] == "explicit_regenerate" and st["phase"] == "B1" and st["lr"]["state"] == "NOT_STARTED"
    # (b) LR phaseのIN_PROGRESS(--only-clipsの明示信号つき)でもリセットしない(resume)
    env.run_dir = str(env.tmp / "run_b").replace("\\", "/")
    os.makedirs(env.run_dir, exist_ok=True)
    notes.reset_providers_for_test()
    env.stop["fn"] = lambda run_dir, where: (_ for _ in ()).throw(Crash(where)) if where.startswith("lr_llm") else None
    w3 = world(env, [True] * 3, [NG] * 3, asr_by_c3_attempt={0: H.C3_ASR_NG}, with_c2=False)      # --only-clipsはc3だけ生成する
    with pytest.raises(Crash):
        run_stage(env, "a2", w3, only_clips={C3})
    assert H.load_state(env.run_dir, "a2")["phase"] == "LR"
    env.stop["fn"] = lambda run_dir, where: None
    notes.reset_providers_for_test()
    w4 = world(env, [True] * 3, [OK] * 3, with_c2=False)
    run_stage(env, "a2", w4, only_clips={C3})
    st = H.load_state(env.run_dir, "a2")
    assert st["cycle"] == 1 and st["n_started"] == 4 and st["status"] == "DONE_OK" and w4.tts_i == 1          # ④のみ(①〜③は再実行しない)
    env.stop["fn"] = lambda run_dir, where: None


def test_s9_accounting_counted_and_carried_do_not_double_count_across_lr_boundary(env, hrq, lr):
    """B1の3行は計上済みのままLR境界をまたぐ。resume時のrecord_outcome累積=旧3+新規(M2)。"""
    ld = f"{env.run_dir}/a2"
    w = world(env, [True] * 3, [NG] * 3, asr_by_c3_attempt={0: H.C3_ASR_NG})
    env.stop["fn"] = lambda run_dir, where: (_ for _ in ()).throw(Crash(where)) if where.startswith("tts_attempt") and where.endswith(":n5") else None
    with pytest.raises(Crash):
        run_stage(env, "a2", w)
    # n=1..4は未計上(outer guardのrecord_outcomeは論理生成の最後に1回。落ちたので未記録)。再開で全て1回だけ計上される
    st = H.load_state(env.run_dir, "a2")
    assert [a["counted"] for a in st["attempts"]] == [False, False, False, False] and st["n_started"] == 4
    env.stop["fn"] = lambda run_dir, where: None
    notes.reset_providers_for_test()
    w2 = world(env, [True] * 2, [NG] * 2, with_c2=False)
    run_stage(env, "a2", w2)
    lk = H.load_lock(env.run_dir, "a2")
    assert lk["cumulative_tts_attempts"] == 6 and lk["last_attempts_log"] and len(lk["last_attempts_log"]) == 6
    assert [a["counted"] for a in H.load_state(env.run_dir, "a2")["attempts"]] == [True] * 6
    assert lk["cumulative_tts_attempts"] <= 15      # MAX_CUMULATIVE_TTS_ATTEMPTS(15): 1サイクル6回は上限内
