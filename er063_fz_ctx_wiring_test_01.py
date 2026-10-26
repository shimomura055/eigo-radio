# -*- coding: utf-8 -*-
"""FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02: er063(Family Z TTS stage)への配線のoffline test(API 0)。

正式経路 `_run_tts_stage_impl` -> `prepare_dialogue_ctx` -> 実の `real_generators()["dialogue"]`(=generate_dialogue_ctx) -> 共有ループ
`er012_b.generate_voice_body_wide_margin`(attempt_hook) / Adv外側ループ `generate_with_a2_slowdown_outer_loop` を、fake TTS/ASR(er122_fz_ctx_fakes_01)と
fake LLMで駆動する。Std/Adv、初回・retry・fallback・resume・中断再開・HR Lock・明示再生成・X/Y/narrator不変を検証。
"""
import ast
import re
import json
import os
import subprocess

import pytest

import er063_family_z_audio_01 as z
import er122_fz_ctx_fakes_01 as fk
import er122_fz_ctx_notes_01 as notes
import er122_fz_ctx_policy_01 as pol

ROOT = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(ROOT, "docs", "research", "FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01", "golden", "golden_hook_none_01.json")
OK = (True, False, "EXACT_MATCH")
NG = (False, False, "TRUE_CONTENT_MISMATCH")
STORY = "the_monkeys_paw"


class Clock:
    def __init__(self, t=2_000_000.0):
        self.t, self.sleeps = t, []

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


class Crash(Exception):
    pass


def _fake_llm_factory(calls, fail_times=0):
    state = {"i": 0}

    def fn(developer, user):
        calls.append(user)
        state["i"] += 1
        if state["i"] <= fail_times:
            raise RuntimeError("llm down")
        rows = json.loads(user.split("\n", 1)[1])
        items = []
        for r in rows:
            items.append({"clip_id": r["clip_id"], "speaker_state": "He is calm.", "scene": "A quiet room.", "reaction_to_previous": "",
                          "evidence": [r["line"]], "has_explicit_cue": False})
        return {"raw": {"items": items}, "model_returned": "gpt-6-luna-test", "cost_jpy": 0.1}
    return fn


@pytest.fixture
def env(tmp_path, monkeypatch):
    notes.reset_providers_for_test()
    clk = Clock()
    monkeypatch.setattr(pol.RUNTIME, "clock", clk.now)
    monkeypatch.setattr(pol.RUNTIME, "sleep", clk.sleep)
    monkeypatch.setattr(z, "_check_stop_sentinel", lambda run_dir, where: None)
    llm_calls = []
    notes.LLM_FN = _fake_llm_factory(llm_calls)

    class E:
        pass
    e = E()
    e.clk, e.tmp, e.llm_calls = clk, tmp_path, llm_calls
    e.run_dir = str(tmp_path / "run").replace("\\", "/")
    os.makedirs(e.run_dir, exist_ok=True)
    yield e
    notes.LLM_FN = None
    notes.reset_providers_for_test()


def story_plan(level):
    sc = [{"id": "full_story_part1_c1", "part": 1, "voice": "narrator", "speaker": "narrator", "text": "It was night. Mr. White said softly."},
          {"id": "full_story_part1_c2", "part": 1, "voice": "mr_white", "speaker": "mr_white", "text": "I am here."},
          {"id": "full_story_part1_c3", "part": 1, "voice": "morris", "speaker": "morris", "text": "Are you sure?"}]
    plan = z.build_level_plan(level, sc, "preview", {1: "c1", 2: "c2", 3: "c3"}, [], "T", japanese_title_text="x", story_key=STORY)
    return [s for s in plan if s.kind in ("narrator", "dialogue")]


def fake_narrator(spec, out_path):
    import er002_common as common
    import numpy as np
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    common.write_wav_float(out_path, np.zeros(2400, dtype=np.float32), common.SAMPLE_RATE, 1)
    return {"status": "OK", "path": out_path, "asr_text": spec.text, "attempts_log": [{"attempt": 1, "status": "OK", "verified": True}]}


def real_dialogue():
    return z.real_generators()["dialogue"]


def gens(counter=None):
    d = real_dialogue()

    def dlg(spec, out_path):
        if counter is not None:
            counter.append(spec.clip_id)
        return d(spec, out_path)
    return {"narrator": fake_narrator, "dialogue": dlg}


def run_stage(env, level, world, plan=None, only_clips=None, generators=None):
    plan = plan or story_plan(level)
    with world.patched():
        return z._run_tts_stage_impl(env.run_dir, level, plan, generators=generators or gens(), only_clips=only_clips, story_key=STORY), plan


def legacy_prompt_for(spec):
    """基準commit(変更前コード)で凍結したgoldenの旧prompt(TEXT区画のみ当該clipの文へ差し替え)。"""
    g = json.load(open(GOLDEN, encoding="utf-8"))
    return g["single"]["S1_success"]["prompts"][0].replace(fk.TEXT, z._norm_for_tts(spec))


def world_for(env, tts, evals):
    w = fk.World(tts, evals, tmp_root=str(env.tmp / "w"))
    w.asr_text = "ok"          # 短いclip用(length_okを満たす)
    return w


def results(env, level):
    return json.load(open(f"{env.run_dir}/{level}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]


@pytest.fixture
def adv_post(monkeypatch):
    """Adv: 減速後の統一judge再検証(apply_a2_slowdown_postprocess)を scriptで差し替える。"""
    import er003_v1_n3_01_tts_generate as n3
    seq = {"i": 0, "script": []}

    def post(name, narration_dir, tts_input, result, is_last_slot=False, log_human_review=True, **k):
        st = seq["script"][seq["i"]] if seq["i"] < len(seq["script"]) else "OK"
        seq["i"] += 1
        r = dict(result)
        r["status"] = st
        r.setdefault("slowdown_applied", True)
        if st != "OK":
            r["reason"] = "fake post-slowdown NG"
        return r
    monkeypatch.setattr(n3, "apply_a2_slowdown_postprocess", post)
    return seq


# ---------------------------------------------------------------- 配線 / policy解決
def test_w1_prepare_attaches_ctx_to_dialogue_only_and_persists_run_policy(env):
    plan = story_plan("a2")
    rec = z.prepare_dialogue_ctx(env.run_dir, "a2", plan, story_key=STORY)
    assert rec["policy"] == "fz_ctx_v1" and os.path.exists(f"{env.run_dir}/audit/dialogue_tts_policy.json")
    for s in plan:
        if s.kind == "dialogue":
            assert s.extra["dialogue_ctx"]["policy"] == "fz_ctx_v1" and s.extra["dialogue_ctx"]["explicit_regenerate"] is False
            assert z.build_reuse_key(s)["dialogue_tts"]["policy"] == "fz_ctx_v1"
        else:
            assert "dialogue_ctx" not in s.extra and "dialogue_tts" not in z.build_reuse_key(s)       # narratorのkeyはバイト不変
    assert env.llm_calls == []                                    # prepareはLLMを呼ばない(M-5)
    p2 = story_plan("a2")
    z.prepare_dialogue_ctx(env.run_dir, "a2", p2, story_key=STORY, only_clips={"full_story_part1_c3"})
    assert [s.extra["dialogue_ctx"]["explicit_regenerate"] for s in p2 if s.kind == "dialogue"] == [False, True]


def test_w1b_existing_run_state_fixes_legacy_for_both_levels_no_mixing(env):
    os.makedirs(f"{env.run_dir}/a2/audit")
    open(f"{env.run_dir}/a2/audit/tts_checkpoint.json", "w").write("{}")           # 旧方式で生成済みのrun
    plan_b = story_plan("b1b")
    base_keys = [z.build_reuse_key(s) for s in plan_b]
    rec = z.prepare_dialogue_ctx(env.run_dir, "b1b", plan_b, story_key=STORY)
    assert rec["policy"] == "legacy"                              # b1bは未着手でもrun単位でlegacy固定(level間の方式混在を防ぐ)
    assert all("dialogue_ctx" not in s.extra for s in plan_b)
    assert [z.build_reuse_key(s) for s in plan_b] == base_keys   # policy=legacyのreuse_keyはバイト不変


def test_w1c_policy_file_is_authoritative_and_rollback_constant(env, monkeypatch):
    monkeypatch.setattr(pol, "Z_DIALOGUE_CTX_POLICY_DEFAULT", "legacy")
    assert z.prepare_dialogue_ctx(env.run_dir, "a2", story_plan("a2"), story_key=STORY)["policy"] == "legacy"
    monkeypatch.setattr(pol, "Z_DIALOGUE_CTX_POLICY_DEFAULT", "fz_ctx_v1")
    assert z.prepare_dialogue_ctx(env.run_dir, "b1b", story_plan("b1b"), story_key=STORY)["policy"] == "legacy"      # 保存済みのrun policyが優先


def test_w2_dry_run_writes_nothing_and_calls_no_api(env):
    before = sorted(os.listdir(env.run_dir))
    out = z._run_tts_stage_impl(env.run_dir, "a2", story_plan("a2"), generators=gens(), dry_run=True, story_key=STORY)
    assert out["dry_run"] is True and sorted(os.listdir(env.run_dir)) == before and env.llm_calls == []


def test_w12_rollback_to_legacy_sends_baseline_prompt_without_notes_or_state(env, monkeypatch):
    monkeypatch.setattr(pol, "Z_DIALOGUE_CTX_POLICY_DEFAULT", "legacy")
    w = world_for(env, [True, True], [OK, OK])
    run_stage(env, "a2", w)
    dl = [s for s in story_plan("a2") if s.kind == "dialogue"]
    assert [p for p in w.prompts] == [legacy_prompt_for(s) for s in dl]     # 従来方式=baselineと同一prompt
    assert env.llm_calls == [] and not os.path.exists(f"{env.run_dir}/a2/audit/dialogue_ctx_attempt_state.json")
    assert all("dialogue_tts" not in e for e in results(env, "a2").values())


# ---------------------------------------------------------------- Std 通し(初回・再利用・M-5・証跡)
def test_w3_std_first_pass_ctx_for_each_dialogue_llm_once_and_reuse_on_rerun(env):
    w = world_for(env, [True, True], [OK, OK])
    (out, plan) = run_stage(env, "a2", w)
    assert len(env.llm_calls) == 1                                           # level単位1 call
    assert all("CONTEXT FOR THIS ONE LINE" in p for p in w.prompts) and len(w.prompts) == 2
    seg = results(env, "a2")
    for cid in ("full_story_part1_c2", "full_story_part1_c3"):
        e = seg[cid]
        assert e["status"] == "OK" and e["dialogue_tts"]["final_mode"] == "ctx" and e["dialogue_tts"]["policy"] == "fz_ctx_v1"
        assert e["reuse_key"]["dialogue_tts"]["policy"] == "fz_ctx_v1"
        assert e["style"]["effective_style_prefix_sha256"] == e["dialogue_tts"]["ctx_style_sha256"]         # M-8: ctx採用のclipは「従来style」と記録しない
        assert e["attempts"][0]["tts_mode"] == "ctx" and e["attempts"][0]["style_prefix_sha256"] == e["dialogue_tts"]["ctx_style_sha256"]
        meta = json.load(open(os.path.splitext(seg[cid]["attempts"] and e["attempts"] and "x" or "x")[0] + ".json")) if False else None
    assert "dialogue_tts" not in seg["full_story_part1_c1"]                  # narratorは無変更
    # 再実行(resume): 全clipが再利用され、TTS 0・LLM 0・stateは変化なし
    notes.reset_providers_for_test()
    w2 = world_for(env, [True, True], [OK, OK])
    calls = []
    run_stage(env, "a2", w2, generators=gens(calls))
    assert calls == [] and w2.tts_i == 0 and len(env.llm_calls) == 1


def test_w3b_attempt_metadata_json_records_tts_mode(env):
    w = world_for(env, [True], [OK])
    plan = [s for s in story_plan("a2") if s.clip_id == "full_story_part1_c2"] + []
    full = story_plan("a2")
    run_stage(env, "a2", w, plan=full)
    seg = results(env, "a2")["full_story_part1_c2"]
    ap = None
    # attempts_logのattempt_audio_path(wav)と並ぶmetadata json
    d = json.load(open(f"{env.run_dir}/a2/audit/dialogue_ctx_attempt_state.json", encoding="utf-8"))
    row = d["clips"]["full_story_part1_c2"]["attempts"][0]["log_rows"][0]
    ap = row.get("attempt_audio_path")
    assert ap and os.path.exists(os.path.splitext(ap)[0] + ".json")
    assert json.load(open(os.path.splitext(ap)[0] + ".json", encoding="utf-8"))["tts_mode"] == "ctx"


def test_w3c_std_ng_ng_cooldown_then_legacy_style_adopted_e2e(env):
    w = world_for(env, [True, True, True, True], [OK, NG, NG, OK])        # clip2 n=1 OK / clip3 n=1 NG, n=2 NG, n=3 OK
    run_stage(env, "a2", w)
    seg = results(env, "a2")
    assert seg["full_story_part1_c2"]["dialogue_tts"]["final_mode"] == "ctx"
    e3 = seg["full_story_part1_c3"]
    assert e3["dialogue_tts"]["final_mode"] == "legacy_fallback" and e3["status"] == "OK"
    assert abs(sum(env.clk.sleeps) - 180.0) < 1e-6 and e3["dialogue_tts"]["cooldown"]["total_elapsed_since_ref_seconds"] >= 180
    legacy = legacy_prompt_for(story_plan("a2")[2])
    assert w.prompts[3] == legacy and w.prompts[1].count("CONTEXT FOR THIS ONE LINE") == 1 and w.prompts[2].count("CONTEXT FOR THIS ONE LINE") == 1
    assert e3["style"]["effective_style_prefix_sha256"] == z.style_prefix_sha256(__import__("er003_b1_p9a_audio").ENGLISH_STYLE_PREFIX)
    assert e3["style"]["fallback_used"] is False         # 既存のfallback_used(標準/fallback経路)の意味は変えない。3回目の方式はdialogue_ttsで記録


def test_w3d_std_three_ng_stops_with_hr_lock_and_gate_blocks(env):
    w = world_for(env, [True, True, True, True], [OK, NG, NG, NG])
    run_stage(env, "a2", w)
    seg = results(env, "a2")
    assert seg["full_story_part1_c3"]["status"] == "STOPPED" and w.tts_i == 4          # clip2: 1回 + clip3: 3回(4回目なし)
    assert seg["full_story_part1_c3"]["dialogue_tts"]["n_started"] == 3
    import er011_human_review_lock_01 as review_lock
    out3 = f"{env.run_dir}/a2/narration/full_story_part1_c3.wav"
    with w.patched():
        assert review_lock.check_before_generation(out3, z._norm_for_tts(story_plan("a2")[2]), "en")["proceed"] is False
    with pytest.raises(z.FamilyZAudioStop):       # Gate(assert_tts_results_complete)がBLOCK: 3回NGのclipは採択されない
        z.assert_tts_results_complete(f"{env.run_dir}/a2", [s.clip_id for s in story_plan("a2")])


def test_w14_review_locked_clip_costs_zero_api_and_zero_llm(env):
    w = world_for(env, [True, True, True, True], [OK, NG, NG, NG])
    run_stage(env, "a2", w)
    notes.reset_providers_for_test()
    llm_before = len(env.llm_calls)
    w2 = world_for(env, [True, True, True], [OK, OK, OK])
    run_stage(env, "a2", w2)                                   # c3はHR Lock済み -> block(0 API)。state不変
    assert w2.tts_i == 0 and len(env.llm_calls) == llm_before
    assert results(env, "a2")["full_story_part1_c3"]["status"] != "OK"


# ---------------------------------------------------------------- 中断・再開(stage level)
def test_w8_kill_during_cooldown_then_rerun_reuses_done_clips_and_continues_from_state(env):
    holder = {"n": 0}

    def stop_check(run_dir, where):
        if where.startswith("tts_cooldown"):
            holder["n"] += 1
            if holder["n"] == 11:
                raise Crash("kill")
    z_stop = z._check_stop_sentinel
    z._check_stop_sentinel = stop_check
    try:
        w = world_for(env, [True, True, True, True], [OK, NG, NG, OK])
        with pytest.raises(Crash):
            run_stage(env, "a2", w)
    finally:
        z._check_stop_sentinel = z_stop
    assert w.tts_i == 3 and len(env.llm_calls) == 1
    st = json.load(open(f"{env.run_dir}/a2/audit/dialogue_ctx_attempt_state.json", encoding="utf-8"))["clips"]
    assert st["full_story_part1_c2"]["status"] == "DONE_OK" and st["full_story_part1_c3"]["n_started"] == 2
    ck = json.load(open(f"{env.run_dir}/a2/audit/tts_checkpoint.json", encoding="utf-8"))["segments"]
    assert "full_story_part1_c2" in ck and "full_story_part1_c3" not in ck
    env.clk.t += 100.0
    notes.reset_providers_for_test()
    w2 = world_for(env, [True], [OK])
    calls = []
    run_stage(env, "a2", w2, generators=gens(calls))
    assert calls == ["full_story_part1_c3"] and w2.tts_i == 1 and len(env.llm_calls) == 1       # c2再利用、1〜2回目は再実行されない、LLM再callなし
    assert "CONTEXT" not in w2.prompts[0]                                                       # 再開後=n=3の従来方式
    e3 = results(env, "a2")["full_story_part1_c3"]
    assert e3["status"] == "OK" and e3["dialogue_tts"]["resumed_from_process_state"] is True and e3["dialogue_tts"]["final_mode"] == "legacy_fallback"


def test_w9_crash_after_done_ok_before_checkpoint_adopts_saved_result_zero_api(env, monkeypatch):
    real_save = z.save_checkpoint
    state = {"n": 0}

    def flaky(level_dir, segments, kps):
        state["n"] += 1
        if state["n"] == 2:                  # 1つ目=narrator、2つ目=dialogue c2(確定直後)
            raise Crash("died between record_outcome and checkpoint")
        return real_save(level_dir, segments, kps)
    monkeypatch.setattr(z, "save_checkpoint", flaky)
    w = world_for(env, [True, True], [OK, OK])
    with pytest.raises(Crash):
        run_stage(env, "a2", w)
    assert w.tts_i == 1
    monkeypatch.setattr(z, "save_checkpoint", real_save)
    notes.reset_providers_for_test()
    w2 = world_for(env, [True, True], [OK, OK])
    calls = []
    run_stage(env, "a2", w2, generators=gens(calls))
    assert w2.tts_i == 1                     # c2は作り直さない(保存結果を採用)。c3だけ新規に1回
    assert results(env, "a2")["full_story_part1_c2"]["dialogue_tts"]["adopted_saved_result"] is True
    assert results(env, "a2")["full_story_part1_c2"]["status"] == "OK"


def test_w9b_explicit_only_clips_regenerates_done_clip_as_new_cycle(env):
    w = world_for(env, [True, True], [OK, OK])
    run_stage(env, "a2", w)
    # 再生成のためresultsからentryを外す(運用上の明示再生成)+ --only-clips
    rp = f"{env.run_dir}/a2/audit/tts_generation_results.json"
    d = json.load(open(rp, encoding="utf-8"))
    d["segments"].pop("full_story_part1_c2")
    json.dump(d, open(rp, "w", encoding="utf-8"))
    notes.reset_providers_for_test()
    w2 = world_for(env, [True], [OK])
    run_stage(env, "a2", w2, only_clips={"full_story_part1_c2"})
    assert w2.tts_i == 1
    st = json.load(open(f"{env.run_dir}/a2/audit/dialogue_ctx_attempt_state.json", encoding="utf-8"))["clips"]["full_story_part1_c2"]
    assert st["cycle"] == 2 and st["history"][0]["reason_for_restart"] == "explicit_regenerate"


def test_w13_llm_failure_stops_before_any_dialogue_tts_and_is_resumable(env):
    notes.LLM_FN = _fake_llm_factory(env.llm_calls, fail_times=99)
    w = world_for(env, [True, True], [OK, OK])
    with pytest.raises(z.FamilyZDialogueCtxStop):
        run_stage(env, "a2", w)
    assert w.tts_i == 0 and len(env.llm_calls) == 2                       # dialogue TTS 0。初回+1回再試行
    ck = json.load(open(f"{env.run_dir}/a2/audit/tts_checkpoint.json", encoding="utf-8"))["segments"]
    assert list(ck) == ["full_story_part1_c1"]                            # 先行narratorは保持(再課金しない)
    notes.reset_providers_for_test()
    notes.LLM_FN = _fake_llm_factory(env.llm_calls)
    w2 = world_for(env, [True, True], [OK, OK])
    run_stage(env, "a2", w2)
    assert w2.tts_i == 2 and all(e["status"] == "OK" for e in results(env, "a2").values())


# ---------------------------------------------------------------- Adv
def test_w4_adv_first_pass_ok_and_post_slowdown_ok(env, adv_post):
    w = world_for(env, [True, True], [OK, OK])
    run_stage(env, "b1b", w)
    seg = results(env, "b1b")
    assert seg["full_story_part1_c2"]["dialogue_tts"]["final_mode"] == "ctx" and w.tts_i == 2
    assert all("CONTEXT FOR THIS ONE LINE" in p for p in w.prompts)


def test_w4b_adv_post_slowdown_ng_retakes_with_ctx_then_ok_n_continues_across_passes(env, adv_post):
    adv_post["script"] = ["STOPPED", "OK", "OK"]            # c2: pass1 post NG -> pass2 OK / c3: pass1 OK
    w = world_for(env, [True, True, True], [OK, OK, OK])
    run_stage(env, "b1b", w)
    seg = results(env, "b1b")
    e2 = seg["full_story_part1_c2"]
    assert e2["status"] == "OK" and e2["dialogue_tts"]["n_started"] == 2 and e2["dialogue_tts"]["final_mode"] == "ctx"
    assert w.prompts[0].count("CONTEXT FOR THIS ONE LINE") == 1 and w.prompts[1].count("CONTEXT FOR THIS ONE LINE") == 1       # n=2もctx
    assert env.clk.sleeps == []                                # n=1->n=2は即時(待機0)
    assert e2["tts_generations_used"] == 2


def test_w5_adv_n1_ng_n2_asr_ok_post_ng_then_n3_cooldown_legacy(env, adv_post):
    adv_post["script"] = ["STOPPED", "OK", "OK"]            # c2: pass1(n=1 NG, n=2 ASR OK) post NG -> pass2(n=3 legacy) OK
    w = world_for(env, [True, True, True, True], [NG, OK, OK, OK])
    run_stage(env, "b1b", w)
    e2 = results(env, "b1b")["full_story_part1_c2"]
    assert e2["status"] == "OK" and e2["dialogue_tts"]["final_mode"] == "legacy_fallback" and e2["dialogue_tts"]["n_started"] == 3
    assert "CONTEXT" not in w.prompts[2] and w.prompts[0].count("CONTEXT FOR THIS ONE LINE") == 1
    assert abs(sum(env.clk.sleeps) - 180.0) < 1e-6          # 2回目NG(減速後NG確定)の後に180秒
    assert e2["dialogue_tts"]["cooldown"]["total_elapsed_since_ref_seconds"] >= 180
    legacy = legacy_prompt_for(story_plan("b1b")[1])
    assert w.prompts[2] == legacy


def test_w5b_adv_three_ng_final_hr_lock_and_finalize(env, adv_post):
    adv_post["script"] = ["STOPPED", "STOPPED", "STOPPED"]
    w = world_for(env, [True, True, True, True], [OK, OK, OK, OK])
    run_stage(env, "b1b", w)
    e2 = results(env, "b1b")["full_story_part1_c2"]
    assert e2["status"] != "OK" and e2["dialogue_tts"]["n_started"] == 3 and w.tts_i >= 3
    import er011_human_review_lock_01 as review_lock
    out2 = f"{env.run_dir}/b1b/narration/full_story_part1_c2.wav"
    with w.patched():
        assert review_lock.check_before_generation(out2, z._norm_for_tts(story_plan("b1b")[1]), "en")["proceed"] is False


def test_w6_m3_ii_minimal_fallback_consumes_outer_budget_and_goes_to_hr_not_fourth(env, adv_post):
    """Opus M-3 / Fable判断(ii): ctx試行でminimal_fallback(1周2行)が起き外側の行会計が先に尽きる稀ケースは、従来方式(3回目)に到達せず安全側でSTOPPED->HR Lock。"""
    adv_post["script"] = ["STOPPED", "STOPPED"]
    # c2: n=1 TTS技術失敗->minimal fallback OK->ASR OK (2行) -> post NG -> 外側残予算1 -> n=2 ctx(最終slot) ASR NG -> STOPPED
    w = world_for(env, [False, True, True, True], [OK, NG, OK])
    run_stage(env, "b1b", w)
    e2 = results(env, "b1b")["full_story_part1_c2"]
    assert e2["status"] != "OK" and e2["dialogue_tts"]["n_started"] == 2
    assert e2["dialogue_tts"]["terminal_before_fallback"] is True            # 開示用の記録名
    assert e2["dialogue_tts"]["cooldown"] is None and e2["dialogue_tts"]["final_mode"] == "ctx"        # n=3(従来方式)に到達していない(cooldownなし)
    # 送信順: [0]=n=1のctx(技術失敗) [1]=n=1内のminimal fallback(既存の技術安全装置。CONTEXTなし) [2]=n=2のctx。従来方式(3回目)のpromptは送られていない
    assert "CONTEXT FOR THIS ONE LINE" in w.prompts[0] and "CONTEXT FOR THIS ONE LINE" not in w.prompts[1] and "CONTEXT FOR THIS ONE LINE" in w.prompts[2]
    legacy = legacy_prompt_for(story_plan("b1b")[1])
    assert legacy not in w.prompts[:3]
    assert len(w.hr_queue) >= 1                                              # 最終slotのNGがHR queueへ


def test_w7_adv_resume_after_pass1_counted_does_not_double_count(env, adv_post, monkeypatch):
    """Opus M-1: pass1(n=1 ASR OK)が完了しrecord_outcome済み(計上済み)の後、減速後NG->pass2の途中で落ちた。再開でpass1の行を再計上せず、
    外側ループへ計上済み行数(prior_generations)を渡して通算TTS予算を実消費に合わせる。"""
    adv_post["script"] = ["STOPPED", "OK", "OK"]
    state = {"n": 0}

    def stop_check(run_dir, where):
        if where.endswith(":n2") and state["n"] == 0:
            state["n"] = 1
            raise Crash("died at pass2 start")
    monkeypatch.setattr(z, "_check_stop_sentinel", stop_check)
    w = world_for(env, [True, True, True], [OK, OK, OK])
    with pytest.raises(Crash):
        run_stage(env, "b1b", w)
    st = json.load(open(f"{env.run_dir}/b1b/audit/dialogue_ctx_attempt_state.json", encoding="utf-8"))["clips"]["full_story_part1_c2"]
    assert st["n_started"] == 1 and st["attempts"][0]["counted"] is True and st["attempts"][0]["rows"] == 1
    monkeypatch.setattr(z, "_check_stop_sentinel", lambda run_dir, where: None)
    import er003_v1_n3_01_tts_generate as n3
    seen = {"priors": {}}
    real_outer = n3.generate_with_a2_slowdown_outer_loop

    def spy(name, *a, **k):
        seen["priors"][name] = k.get("prior_generations")
        return real_outer(name, *a, **k)
    monkeypatch.setattr(n3, "generate_with_a2_slowdown_outer_loop", spy)
    adv_post["i"] = 0
    adv_post["script"] = ["OK", "OK"]
    notes.reset_providers_for_test()
    w2 = world_for(env, [True, True], [OK, OK])
    run_stage(env, "b1b", w2)
    e2 = results(env, "b1b")["full_story_part1_c2"]
    assert seen["priors"]["full_story_part1_c2"] == 1 and e2["status"] == "OK" and e2["dialogue_tts"]["n_started"] == 2 and e2["tts_generations_used"] == 2
    assert w2.tts_i == 2 and all("CONTEXT FOR THIS ONE LINE" in p for p in w2.prompts[:1])


# ---------------------------------------------------------------- X/Y/B/C/narrator不変
def test_w11_x_y_runners_do_not_reference_new_modules_or_hook():
    import glob
    for pat in ("er019_*.py", "er121_*.py"):
        for f in glob.glob(os.path.join(ROOT, pat)):
            if f.endswith("_test_01.py") or "_test" in os.path.basename(f):
                continue
            src = open(f, encoding="utf-8").read()
            for banned in ("er122", "attempt_hook", "dialogue_ctx", "prior_generations"):
                assert banned not in src, (f, banned)


def test_w11b_non_dialogue_generators_source_unchanged_vs_baseline_commit():
    """narrator/topic_intro/preview/comment/japanese_title/kp_* generator(real_generators内の関数)のソースが基準commit(ab111631c)と同一。"""
    try:
        base = subprocess.run(["git", "show", "ab111631c:er063_family_z_audio_01.py"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    except Exception:
        pytest.skip("git基準commitを取得できない")
    cur = open(os.path.join(ROOT, "er063_family_z_audio_01.py"), encoding="utf-8").read()

    def inner(src):
        tree = ast.parse(src)
        rg = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "real_generators")
        return {n.name: ast.get_source_segment(src, n) for n in rg.body if isinstance(n, ast.FunctionDef)}
    b, c = inner(base), inner(cur)
    assert set(b) == set(c)
    for name in b:
        if name == "dialogue":
            continue
        if name == "_kp_en_two_stage":
            # TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02: KP英語の二段にだけ統一ブロック(er127)の差込みを許可。差込み部分を除くと基準commitと一字一句同一であること。
            cc = c[name]
            cc = re.sub(r"    @er127\.with_block\([^\n]*\n", "", cc)
            cc = cc.replace("def _kp_en_two_stage(text, out_path, spec, *, _blk=None):", "def _kp_en_two_stage(text, out_path, spec):")
            cc = re.sub(r",  (# KP3V[^\n]*)\n\s+\*\*er127\.stage_kwargs\([^\n]*?\)\)[^\n]*\n(?:        if _blk is not None[^\n]*\n[^\n]*\n)?", r")  \1\n", cc)
            assert cc == b[name], "kp_en: er127差込み以外の差分があります"
            continue
        assert b[name] == c[name], name
    # dialogue のlegacy分岐(Adv外側ループ・Std単一呼出)は現行コードが一字も変わらず残っている
    legacy_adv = "return n3_tts.generate_with_a2_slowdown_outer_loop(\n                spec.clip_id, text, out_path,"
    assert legacy_adv in c["dialogue"] and legacy_adv in b["dialogue"]
    assert "return bvoices.generate_voice_body_wide_margin(text, out_path, spec.voice)" in c["dialogue"]


def test_w11c_style_text_for_and_non_dialogue_keys_unchanged(env):
    plan = story_plan("a2")
    for s in plan:
        assert z.style_text_for(s) is None if s.kind == "dialogue" else True
    z.prepare_dialogue_ctx(env.run_dir, "a2", plan, story_key=STORY)
    for s in plan:
        assert z.style_text_for(s) is None if s.kind == "dialogue" else True          # 方式は style_prefix_override(attempt hook)経由で、style_text_for/FAMILY_Z_ROLE_STYLEは不変
        assert "style_prefix_sha256" in z.build_reuse_key(s)


def test_w15_dangling_reference_old_method_references_remain():
    src = open(os.path.join(ROOT, "er063_family_z_audio_01.py"), encoding="utf-8").read()
    for ref in ("def style_text_for", "def _effective_style_sha(", "def extract_attempt_evidence", "def build_reuse_key", "def generate_or_reuse_z",
                "generate_voice_body_minimal_fallback"[:0] or "def build_entry"):
        assert ref in src
    import er012_b_family_voices_production_01 as bv
    assert hasattr(bv, "generate_voice_body_minimal_fallback")


def test_w16_old_reader_compat_entries_without_new_keys_still_pass_evidence_row(env):
    """旧reader互換(additive): dialogue_ttsを持たない旧entryで _evidence_row / extract_attempt_evidence が従来どおり動く。"""
    plan = story_plan("a2")
    spec = plan[1]
    entry = z.build_entry(spec, f"{env.run_dir}/a2/narration/{spec.clip_id}.wav", {"status": "OK", "attempts_log": [{"attempt": 1, "status": "OK", "verified": True}]})
    row = z._evidence_row(spec, f"{env.run_dir}/a2/narration/{spec.clip_id}.wav", entry)
    assert "dialogue_tts" not in entry and "dialogue_tts" not in row
    assert entry["attempts"][0].get("tts_mode") is None and "tts_mode" not in entry["attempts"][0]
