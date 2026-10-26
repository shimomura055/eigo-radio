# -*- coding: utf-8 -*-
"""FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02: Phase 2 evidence driver(er122_fzcw_runtime_evidence_01.py)のmock test(API 0・実行なし)。

driverの安全性(注入口がProductionに無い・NG方向のみ・E-1は上書き0・公開page出力なし・自起動PIDのみ終了・STOP確認・共有台帳の前後記録)と、
強制NGで 文脈・感情付き -> 文脈・感情付き -> cooldown -> 従来方式 が想定どおり遷移することを、fake backend上で事前に確認する。
"""
import json
import os

import pytest

import er122_fz_ctx_fakes_01 as fk
import er122_fz_ctx_policy_01 as pol
import er122_fzcw_runtime_evidence_01 as drv
from er063_fz_ctx_wiring_test_01 import (OK, NG, adv_post, env, gens, legacy_prompt_for, results, run_stage, story_plan, world_for)  # noqa: F401
import er063_family_z_audio_01 as z

ROOT = os.path.dirname(os.path.abspath(__file__))


def _args(**kw):
    ap = drv.build_parser()
    base = ["--case", kw.pop("case", "E-2"), "--work", "the_monkeys_paw", "--run", "run_fzcw_test", "--budget-jpy", "10"]
    for k, v in kw.items():
        base += [f"--{k.replace('_', '-')}", str(v)]
    return ap.parse_args(base)


# ---------------------------------------------------------------- 注入口がProductionに無い / 構造
def test_production_code_has_no_injection_port():
    for fn in ("er063_family_z_audio_01.py", "er012_b_family_voices_production_01.py", "er003_v1_n3_01_tts_generate.py", "er122_fz_ctx_policy_01.py",
               "er122_fz_ctx_notes_01.py"):
        src = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        for banned in ("forced_ng", "evidence_driver", "er122_fzcw_runtime_evidence", "FZCW_FORCE", "inject_ng"):
            assert banned not in src, (fn, banned)
    pol_src = open(os.path.join(ROOT, "er122_fz_ctx_policy_01.py"), encoding="utf-8").read()
    assert "os.environ" not in pol_src and "getenv" not in pol_src and "argparse" not in pol_src       # env/flag/CLIでON・OFF・短縮できない


def test_driver_is_not_imported_by_production_modules():
    import glob
    import re
    for f in glob.glob(os.path.join(ROOT, "*.py")):
        b = os.path.basename(f)
        if b.startswith("er122_fzcw_runtime_evidence") or "_test" in b:
            continue
        if re.search(r"^\s*(import|from)\s+er122_fzcw_runtime_evidence", open(f, encoding="utf-8").read(), re.M):
            pytest.fail(f"{b} がevidence driverをimportしている")


def test_case_plans_and_e1_has_empty_injection():
    assert not drv.InjectionPlan("E-1").injects and drv.InjectionPlan("E-1").path == "normal"
    assert drv.InjectionPlan("E-2").wanted("rep", "any_clip", 1) and drv.InjectionPlan("E-2").wanted("rep", "any_clip", 2)
    assert not drv.InjectionPlan("E-2").wanted("rep", "any_clip", 3)                      # 3回目の従来方式は完全な本物の判定
    assert [drv.InjectionPlan("E-4").wanted("rep", "c", n) for n in (1, 2, 3, 4)] == [True, True, True, False]
    assert [drv.InjectionPlan("E-5").wanted("rep", "c", n) for n in (1, 2)] == [True, False]
    assert drv.InjectionPlan("E-6").wanted("post", "c", 1) and not drv.InjectionPlan("E-6").rep


def test_e1_with_nonempty_plan_is_refused(monkeypatch):
    a = _args(case="E-1")
    monkeypatch.setattr(drv.InjectionPlan, "injects", property(lambda self: True))
    with pytest.raises(drv.DriverError):
        drv.run_case(a, runner_main=lambda argv: 0, stop_check=lambda *x: 0)


# ---------------------------------------------------------------- NG方向のみ
def test_rep_gate_wrapper_only_flips_true_to_false_never_false_to_true():
    plan = drv.InjectionPlan("E-2")
    rec = drv.Recorder()
    seq = {"v": [True, True, True, False]}

    def orig(verified, out_path, text, **k):
        return {"verified": seq["v"].pop(0), "repetition_qa_checked": True}
    w = drv.make_rep_gate_wrapper(orig, plan, rec)
    outs = [w(True, "/x/narration/c1.wav", "t")["verified"] for _ in range(4)]
    assert outs == [False, False, True, False]                       # ordinal 1,2のみTrue->False。3回目は本物のTrueのまま。元がFalseなら何もしない
    assert len(rec.overrides) == 2 and [o["ordinal"] for o in rec.overrides] == [1, 2]
    # 逆方向(NG->OK)の上書き経路が存在しない: ordinal対象でも元がFalseなら上書きしない
    plan2 = drv.InjectionPlan("E-2")
    rec2 = drv.Recorder()
    w2 = drv.make_rep_gate_wrapper(lambda v, p, t, **k: {"verified": False}, plan2, rec2)
    assert w2(True, "/x/narration/c1.wav", "t")["verified"] is False and rec2.overrides == []
    src = open(os.path.join(ROOT, "er122_fzcw_runtime_evidence_01.py"), encoding="utf-8").read()
    assert '["verified"] = True' not in src and '"status"] = "OK"' not in src


def test_post_slowdown_wrapper_only_flips_ok_to_stopped():
    plan = drv.InjectionPlan("E-6")
    rec = drv.Recorder()
    w = drv.make_post_slowdown_wrapper(lambda name, d, t, r, **k: dict(r), plan, rec)
    assert w("c1", "d", "t", {"status": "OK"})["status"] == "STOPPED"
    assert w("c1", "d", "t", {"status": "OK"})["status"] == "OK"        # 2回目以降は本物
    assert drv.make_post_slowdown_wrapper(lambda *a, **k: {"status": "STOPPED"}, plan, drv.Recorder())("c9", "d", "t", {"status": "STOPPED"})["status"] == "STOPPED"


def test_e1_installs_no_gate_wrapper_and_restores_everything():
    import er011_open121_repetition_qa_production_01 as rq
    import er003_v1_n3_01_tts_generate as n3
    import er002_common as common
    r0, p0, t0 = rq.apply_repetition_qa_gate, n3.apply_a2_slowdown_postprocess, common._call_tts_with_retry
    with drv.install_patches(drv.InjectionPlan("E-1"), drv.Recorder()):
        assert rq.apply_repetition_qa_gate is r0 and n3.apply_a2_slowdown_postprocess is p0        # Gate出力に触る経路が構造的に存在しない
        assert common._call_tts_with_retry is not t0                                                  # 送信prompt捕捉(記録のみ)
    assert common._call_tts_with_retry is t0
    with drv.install_patches(drv.InjectionPlan("E-2"), drv.Recorder()):
        assert rq.apply_repetition_qa_gate is not r0
    assert rq.apply_repetition_qa_gate is r0


# ---------------------------------------------------------------- 起動の安全性
def test_runner_argv_excludes_public_pages_and_isolates_pages_dir():
    a = _args(case="E-2", level="a2", only_clips="full_story_part1_c2")
    a.stages = drv.default_stages("E-2", "a2")
    argv = drv.build_runner_argv(a)
    assert "--stages" in argv and argv[argv.index("--stages") + 1] == "tts_a2" and "pages" not in argv[argv.index("--stages") + 1].split(",")
    assert argv[argv.index("--pages-dir") + 1].endswith("pages_evidence_unpublished") and "--tts-execution-mode" in argv and "STANDARD" in argv
    assert drv.default_stages("E-1", None) == "tts_b1b,tts_a2,provision_shell,gate,assemble"
    a.stages = "tts_a2,pages"
    with pytest.raises(drv.DriverError):
        drv.build_runner_argv(a)


def test_stop_scope_rc3_blocks_before_any_runner_call(monkeypatch, tmp_path):
    called = []
    monkeypatch.setattr(drv, "ROOT", str(tmp_path))
    monkeypatch.setattr(drv, "E2E_RUN_ROOT", str(tmp_path / "runs"))
    a = _args(case="E-2", level="a2")
    with pytest.raises(drv.DriverError):
        drv.run_case(a, runner_main=lambda argv: called.append(argv) or 0, stop_check=lambda *x: 3)
    assert called == []


def test_main_refuses_batch_mode_and_requires_level(monkeypatch):
    monkeypatch.setenv("TTS_EXECUTION_MODE", "BATCH")
    assert drv.main(["--case", "E-2", "--work", "melos", "--run", "r", "--budget-jpy", "1", "--level", "a2"]) == 2
    monkeypatch.setenv("TTS_EXECUTION_MODE", "STANDARD")
    assert drv.main(["--case", "E-2", "--work", "melos", "--run", "r", "--budget-jpy", "1"]) == 2


def test_run_case_writes_evidence_with_path_injection_flag_ledgers_and_pid(monkeypatch, tmp_path):
    monkeypatch.setattr(drv, "ROOT", str(tmp_path))
    monkeypatch.setattr(drv, "E2E_RUN_ROOT", str(tmp_path / "runs"))
    monkeypatch.setattr(drv, "SHARED_LEDGERS", ("ledger_a.jsonl",))
    (tmp_path / "ledger_a.jsonl").write_text("1\n2\n")

    def runner(argv):
        (tmp_path / "ledger_a.jsonl").write_text("1\n2\n3\n")        # runnerがprocess共通台帳へ1行追記した状況
        return 0
    a = _args(case="E-1")
    a.evidence_out = "ev/E1.json"
    ev = drv.run_case(a, runner_main=runner, stop_check=lambda *x: 0)
    assert ev["path"] == "normal" and ev["forced_ng_injection"] is False and ev["injected_override_count"] == 0
    assert ev["shared_ledgers"]["ledger_a.jsonl"] == {"lines_before": 2, "lines_after": 3, "added_lines": 1, "changed": True}
    assert ev["ledger_invalidation"] is None and ev["pid"] == os.getpid()
    saved = json.load(open(tmp_path / "ev" / "E1.json", encoding="utf-8"))
    assert saved["case"] == "E-1" and saved["runner_rc"] == 0
    a2 = _args(case="E-2", level="a2")
    a2.evidence_out = "ev/E2.json"
    ev2 = drv.run_case(a2, runner_main=lambda argv: 0, stop_check=lambda *x: 0)
    assert ev2["path"] == "forced_ng_fallback" and ev2["ledger_invalidation"] and "evidence専用" in ev2["ledger_invalidation"]


def test_kill_terminates_only_own_pid_via_os_exit_after_state_persisted(env):
    exits = []

    class Exit(Exception):
        pass

    def fake_exit(code):
        exits.append(code)
        raise Exit()
    w = fk.World([True, True], [NG, OK], tmp_root=str(env.tmp / "kw"))
    plan = drv.InjectionPlan("E-5")
    rec = drv.Recorder()
    parts = []
    rec.before_exit = lambda: parts.append("partial_written")
    import er012_b_family_voices_production_01 as bv
    pl = pol.DialogueAttemptPolicy(os.path.dirname(os.path.dirname(w.out_path)), "full_story_part1_c3", fk.TEXT, "CTX", pol._sha256_text("CTX"), out_path=w.out_path,
                                   stop_check=lambda where: None)
    with w.patched(), drv.install_patches(plan, rec, kill_after_attempt=1, exit_fn=fake_exit):
        with pytest.raises(Exit):
            bv.generate_voice_body_wide_margin(fk.TEXT, w.out_path, "Puck", max_attempts=3, attempt_hook=pl)
    assert exits == [137] and parts == ["partial_written"]
    st = pol.StateStore(os.path.dirname(os.path.dirname(w.out_path))).get("full_story_part1_c3")
    assert st["n_started"] == 1 and st["attempts"][0]["finished"] is True and st["attempts"][0]["verified"] is False       # 強制NGがstateに永続化済み
    import ast
    tree = ast.parse(open(os.path.join(ROOT, "er122_fzcw_runtime_evidence_01.py"), encoding="utf-8").read())
    called = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert not (called & {"kill", "terminate", "killpg", "taskkill", "Popen"}) and "psutil" not in imported         # 自PID(os._exit)以外の終了手段なし
    assert "subprocess" in imported and called >= {"run"}                                                      # subprocessはstop_scope_check実行のみ


# ---------------------------------------------------------------- 強制NGで想定どおり遷移する事前確認(offline)
def _run_with_driver(env, tts, evals, case, **kw):
    w = world_for(env, tts, evals)
    plan = drv.InjectionPlan(case)
    rec = drv.Recorder()
    with w.patched(), drv.install_patches(plan, rec, **kw):
        z._run_tts_stage_impl(env.run_dir, "a2", story_plan("a2"), generators=gens(), story_key="the_monkeys_paw")
    return w, rec


def test_e2_forced_ng_1_2_then_cooldown_then_real_legacy_attempt(env):
    w, rec = _run_with_driver(env, [True, True, True, True], [OK, OK, OK, OK], "E-2")
    # clip2: n=1,n=2を強制NG -> 600秒 -> n=3(従来方式・本物の判定=OK)。clip3: ordinal対象外ではない('*')ので同様
    e2 = results(env, "a2")["full_story_part1_c2"]
    assert e2["status"] == "OK" and e2["dialogue_tts"]["final_mode"] == "legacy_fallback" and e2["dialogue_tts"]["n_started"] == 3
    prompts = [r for r in rec.requests if r["clip"] == "full_story_part1_c2"]
    assert [r["has_context"] for r in prompts] == [True, True, False]
    assert prompts[2]["prompt_sha256"] == drv.hashlib.sha256(legacy_prompt_for(story_plan("a2")[1]).encode("utf-8")).hexdigest()
    assert abs(sum(env.clk.sleeps) - 1200.0) < 1e-6          # 2 clip x 600秒
    assert len([o for o in rec.overrides if o["clip"] == "full_story_part1_c2"]) == 2


def test_e5_first_only_forced_ng_second_ctx_passes_immediately(env):
    w, rec = _run_with_driver(env, [True] * 6, [OK] * 6, "E-5")
    e2 = results(env, "a2")["full_story_part1_c2"]
    assert e2["dialogue_tts"]["final_mode"] == "ctx" and e2["dialogue_tts"]["n_started"] == 2 and env.clk.sleeps == []         # 即時Retry(待機0)


def test_e4_three_forced_ng_stops_with_hr_lock(env):
    w, rec = _run_with_driver(env, [True] * 8, [OK] * 8, "E-4")
    e2 = results(env, "a2")["full_story_part1_c2"]
    assert e2["status"] == "STOPPED" and e2["dialogue_tts"]["n_started"] == 3
    # 強制NGはrepetition QA段階。ASR判定自体はPASSなのでASR由来のHR queue行は出ない(Opus M-10(d))。HR Lockは最終STOPPEDで立つ
    assert w.hr_queue == []
    import er011_human_review_lock_01 as review_lock
    with w.patched():
        assert review_lock.check_before_generation(f"{env.run_dir}/a2/narration/full_story_part1_c2.wav", z._norm_for_tts(story_plan("a2")[1]), "en")["proceed"] is False


def test_e6_adv_post_slowdown_forced_ng_continues_outer_loop_with_ctx(env, adv_post):
    import er003_v1_n3_01_tts_generate as n3  # noqa: F401  (adv_postがapply_a2_slowdown_postprocessをfakeに差替え済み。driverはその上を包む)
    adv_post["script"] = ["OK"] * 6
    w = world_for(env, [True, True, True, True], [OK, OK, OK, OK])
    plan = drv.InjectionPlan("E-6")
    rec = drv.Recorder()
    with w.patched(), drv.install_patches(plan, rec):
        z._run_tts_stage_impl(env.run_dir, "b1b", story_plan("b1b"), generators=gens(), story_key="the_monkeys_paw")
    e2 = results(env, "b1b")["full_story_part1_c2"]
    assert e2["status"] == "OK" and e2["dialogue_tts"]["n_started"] == 2 and e2["dialogue_tts"]["final_mode"] == "ctx"
    prompts = [r for r in rec.requests if r["clip"] == "full_story_part1_c2"]
    assert [r["has_context"] for r in prompts] == [True, True] and env.clk.sleeps == []          # 通算n=2もctx。n=1->n=2は待機0


def test_ledger_snapshot_and_diff_helpers(tmp_path):
    (tmp_path / "x.jsonl").write_text("a\nb\n")
    s1 = drv.ledger_snapshot(str(tmp_path))
    assert s1["er011_output/attempt_history.jsonl"]["exists"] is False
    d = drv.ledger_diff(s1, s1)
    assert all(v["added_lines"] == 0 and v["changed"] is False for v in d.values())


def test_collect_added_rows_marks_only_rows_of_this_run_as_evidence_only(tmp_path):
    led = tmp_path / "q.jsonl"
    led.write_text('{"wav_path": "x/old_run/a2/narration/c1.wav"}\n')
    before = {"q.jsonl": {"lines": 1, "sha256": "x", "exists": True, "bytes": 0}}
    led.write_text('{"wav_path": "x/old_run/a2/narration/c1.wav"}\n{"wav_path": "x/run_fzcw_e2/a2/narration/c2.wav"}\n{"wav_path": "other/zzz.wav"}\n')
    rows = drv.collect_added_rows(before, "run_fzcw_e2", root=str(tmp_path))
    assert len(rows) == 1 and rows[0]["line_index"] == 1 and rows[0]["classification"] == "evidence_only_no_action_required"


def test_assembly_observations_reads_headroom_and_gain_reports_only(tmp_path):
    d = tmp_path / "a2" / "audit"
    d.mkdir(parents=True)
    (d / "headroom_report.json").write_text(json.dumps({"scalar": 0.97}))
    (d / "gain_report.json").write_text(json.dumps({"target_rms": 0.1}))
    obs = drv.assembly_observations(str(tmp_path), levels=("a2", "b1b"))
    assert obs == {"a2": {"headroom_report": {"scalar": 0.97}, "gain_report": {"target_rms": 0.1}}}
