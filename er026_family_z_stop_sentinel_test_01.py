# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_12A: STOP対策の実効検証(課金0・mock/dry-runのみ・実API 0)。

項目1〜7を固定する(項目8=統合testの環境起因failの再確認は別手順)。証跡は
er026_output/family_z_production_e2e_01/melos/evidence_12A/ へ書く。
実行: .venv/Scripts/python.exe -m unittest er026_family_z_stop_sentinel_test_01 -v
注意: 項目4の一部は STOP_ALL を一時的に実パスへ作成する(試験後に必ず削除。事前に存在する場合はtestを中止)。
"""
from __future__ import annotations

import contextlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

import er026_family_z_fiction_production_runner_01 as r
import er062_family_z_structure_01 as st
import er062_family_z_writer_01 as w62
import er063_family_z_audio_01 as a63

# 子processの入出力をUTF-8に固定する(Windows既定のcp932でのdecode不一致を防ぐ。REMAINING-ISSUES-01 項目4)
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

REPO = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
RUNNER = "er026_family_z_fiction_production_runner_01.py"
MELOS = os.path.join(REPO, "er026_output", "family_z_production_e2e_01", "melos")
EVID = os.path.join(MELOS, "evidence_12A")
REAL_RUN_COST_LOG = os.path.join(MELOS, "run_e2e_01", "cost_log.jsonl")
REAL_RUN_STAGE_LOG = os.path.join(MELOS, "run_e2e_01", "e2e_stage_log.jsonl")


_LOCK_PATH = os.path.join(MELOS, ".stoptest_exclusive.lock")
_LOCK_HELD = False


def _acquire_exclusive(wait_s: int = 900) -> None:
    """test全体のprocess間排他lock。本testは共有の固定dir(run_stoptest_*/evidence_12A)と実パスSTOP_ALLを
    使うため、同時に2プロセス走ると互いのdir削除/STOP_ALLで失敗する(2026-10-12 REMAINING-ISSUES-01で再現)。
    lock保持processが死んでいれば(PID不在)奪取する。"""
    global _LOCK_HELD
    os.makedirs(MELOS, exist_ok=True)
    deadline = time.time() + wait_s
    while True:
        try:
            fd = os.open(_LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, json.dumps({"pid": os.getpid(), "at": time.time()}).encode())
            os.close(fd)
            _LOCK_HELD = True
            return
        except FileExistsError:
            try:
                with open(_LOCK_PATH, encoding="utf-8") as fh:
                    holder = json.load(fh).get("pid")
            except Exception:
                holder = None
            if holder is not None and not st.pid_alive(holder):
                try:
                    os.remove(_LOCK_PATH)
                except OSError:
                    pass
                continue
            if time.time() > deadline:
                raise RuntimeError("他のSTOP sentinel testが実行中でlockを取得できない(900秒待機)")
            time.sleep(2)


def _release_exclusive() -> None:
    global _LOCK_HELD
    if _LOCK_HELD:
        try:
            os.remove(_LOCK_PATH)
        except OSError:
            pass
        _LOCK_HELD = False


def setUpModule():
    _acquire_exclusive()


def tearDownModule():
    _release_exclusive()


import atexit  # noqa: E402
atexit.register(_release_exclusive)


def ev(name: str, obj) -> None:
    os.makedirs(EVID, exist_ok=True)
    with open(os.path.join(EVID, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=str)


def run_dir(run: str, mock: bool = True) -> str:
    return os.path.join(MELOS, run + ("_mock" if mock else ""))


def cli(args, env=None, cwd=REPO, timeout=180):
    e = dict(os.environ)
    e.update(env or {})
    p = subprocess.run([PY, RUNNER] + list(args), cwd=cwd, env=e, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def counter(run: str):
    return read_jsonl(os.path.join(run_dir(run), "mock_api_calls.jsonl"))


def save_run_evidence(run: str, tag: str) -> None:
    """run dirの監査記録(カウンタ・audit・起動履歴・stage log)だけを証跡へ複製する。"""
    dst = os.path.join(EVID, tag)
    os.makedirs(dst, exist_ok=True)
    for d in (run_dir(run), run_dir(run, mock=False)):
        for fn in ("mock_api_calls.jsonl", "audit_stop_sentinel.jsonl", "run_launch_log.jsonl", "e2e_stage_log.jsonl",
                   "STOP", "RESTART_STORM_LOCK.json"):
            sp = os.path.join(d, fn)
            if os.path.exists(sp):
                shutil.copy(sp, os.path.join(dst, os.path.basename(d) + "__" + fn))


def purge_test_runs():
    if os.path.isdir(MELOS):
        for n in os.listdir(MELOS):
            if n.startswith("run_stoptest_"):
                shutil.rmtree(os.path.join(MELOS, n), ignore_errors=True)


@contextlib.contextmanager
def real_stop_all(note="12A test"):
    """実パスの STOP_ALL を一時作成する(既存なら使わない=中止)。必ず削除する。"""
    if os.path.exists(st.STOP_ALL_PATH):
        raise unittest.SkipTest("STOP_ALL が既に存在する(Fable/ユーザー操作中)。このtestは実行しない")
    os.makedirs(os.path.dirname(st.STOP_ALL_PATH), exist_ok=True)
    with open(st.STOP_ALL_PATH, "w", encoding="utf-8") as f:
        json.dump({"reason": note, "by": "er026_family_z_stop_sentinel_test_01"}, f)
    try:
        yield
    finally:
        if os.path.exists(st.STOP_ALL_PATH):
            os.remove(st.STOP_ALL_PATH)


def spec_of(clip_id="full_story_part1_c1"):
    return type("S", (), {"clip_id": clip_id})()


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(st.STOP_ALL_PATH):
            raise unittest.SkipTest("STOP_ALL が既に存在するため実効検証を実行しない")
        purge_test_runs()

    @classmethod
    def tearDownClass(cls):
        purge_test_runs()

    def tmp(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        return t

    def tearDown(self):
        st.set_stop_run_dir(None)
        st.uninstall_api_stop_guard()


# ============================================================
# 項目1: 初回実行中にSTOPを置く -> 次のAPI境界で停止
# ============================================================
class Item1InitialRunStop(Base):
    def test_item1_stop_midrun_stops_at_next_api_boundary(self):
        run = "run_stoptest_01"
        os.makedirs(run_dir(run, mock=False), exist_ok=True)       # <run>/STOP の置き場(mock実体は <run>_mock)
        env = dict(os.environ, FAMILY_Z_MOCK_API_DELAY_SEC="0.1")
        p = subprocess.Popen([PY, RUNNER, "--mode", "mock", "--stage", "all", "--run", run], cwd=REPO, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        try:
            deadline, tts_seen = time.time() + 120, 0
            while time.time() < deadline and p.poll() is None:
                rows = counter(run)
                tts_seen = sum(1 for x in rows if str(x["kind"]).startswith("tts:"))
                if tts_seen >= 3:                                     # writer->plan->support->kp を越え tts 途中
                    break
                time.sleep(0.05)
            self.assertGreaterEqual(tts_seen, 3, "TTS途中まで到達しなかった")
            with open(os.path.join(run_dir(run, mock=False), "STOP"), "w", encoding="utf-8") as f:
                f.write("item1 test STOP")
            stop_ts = time.time()
            n_at_stop = len(counter(run))
            out, err = p.communicate(timeout=120)
        finally:
            if p.poll() is None:
                p.kill()
        rows = counter(run)
        after = [x for x in rows if x["ts"] > stop_ts + 0.02]
        audit = read_jsonl(os.path.join(run_dir(run), "audit_stop_sentinel.jsonl"))
        stages = [x["stage"] for x in read_jsonl(os.path.join(run_dir(run), "e2e_stage_log.jsonl"))]
        time.sleep(0.5)
        n_final = len(counter(run))
        res = {"item": 1, "rc": p.returncode, "calls_at_stop": n_at_stop, "calls_final": n_final,
               "calls_after_stop_ts": len(after), "audit_records": audit, "stages_completed": stages,
               "run_lock_remaining": os.path.exists(os.path.join(run_dir(run), "RUN_LOCK.json")),
               "cost_log_created": os.path.exists(os.path.join(run_dir(run), "cost_log.jsonl")),
               "stderr_tail": err[-300:]}
        ev("item1_initial_run_stop.json", res)
        save_run_evidence(run, "item1_run_stoptest_01")
        self.assertEqual(p.returncode, 3)
        self.assertEqual(after, [])                         # STOP後のmock API呼出ゼロ
        self.assertEqual(n_final, len(counter(run)))
        self.assertLessEqual(n_final - n_at_stop, 1)         # STOP作成直前に通過済みの最大1呼出
        self.assertTrue(audit and audit[-1].get("sentinel", "").endswith("STOP"))
        self.assertNotIn("pages", stages)
        self.assertFalse(res["run_lock_remaining"])
        self.assertFalse(res["cost_log_created"])


# ============================================================
# 項目2: retry / fallback / cool-down 経路でも止まる
# ============================================================
class Item2RetryFallbackCooldown(Base):
    def _stop(self, d):
        with open(f"{d}/STOP", "w", encoding="utf-8") as f:
            f.write("stop")

    def test_item2a_shared_retry_loop_cannot_swallow_stop(self):
        """共有module(er002_common._call_tts_with_retry、`except Exception`でretry+sleep)を実際に通す。"""
        import er002_common as common
        d = self.tmp()
        api = r.MockApi(d)
        st.set_stop_run_dir(d)
        seq = []

        def tts_call(prompt):
            seq.append("call")
            api.call("tts_attempt", prompt)
            raise RuntimeError("simulated ASR NG -> retry")

        def sleep_fn(sec):
            seq.append("sleep")
            self._stop(d)                                   # retry待機中にSTOPが置かれる

        with self.assertRaises(st.FamilyZStopSentinelAbort):
            common._call_tts_with_retry(tts_call, "p", 3, sleep_fn)
        rows = read_jsonl(f"{d}/mock_api_calls.jsonl")
        ev("item2a_shared_retry_loop.json", {"item": 2, "sequence": seq, "api_calls": len(rows),
                                             "audit": read_jsonl(f"{d}/{st.AUDIT_NAME}")})
        self.assertEqual(len(rows), 1)                       # 1回目のみ。2回目のretry API呼出は阻止
        self.assertEqual(seq[:2], ["call", "sleep"])
        self.assertTrue(read_jsonl(f"{d}/{st.AUDIT_NAME}"))

    def test_item2b_primary_ng_then_fallback_blocked_in_z_wrapper(self):
        """Z側の生成wrapper(build_mock_context)経由: primary NG -> fallback の前でSTOP。"""
        d = self.tmp()
        ctx = r.build_mock_context(d, run="run_t2b")
        api, out = ctx.mock_api, os.path.join(d, "x.wav")
        calls = []

        def gen(spec, out_path):
            api.call("primary")
            calls.append("primary")
            self._stop(ctx.out_dir)                         # primaryがNGになった時点でSTOP
            api.call("fallback")                            # fallback経路(共有cascadeのgenerate_fn呼出相当)
            calls.append("fallback")
            return {"status": "OK"}

        ctx2 = r.build_mock_context(d, run="run_t2b", tts_generators={"narrator": gen})
        os.makedirs(ctx2.out_dir, exist_ok=True)
        wrapped = r.wrap_generators_with_budget(ctx2.hooks["tts_generators"], None, sentinel_dir=ctx2.out_dir)
        with self.assertRaises(st.FamilyZStopSentinelAbort):
            wrapped["narrator"](spec_of(), out)
        rows = read_jsonl(f"{ctx2.out_dir}/mock_api_calls.jsonl")
        ev("item2b_fallback_blocked.json", {"item": 2, "calls": calls, "counter_rows": len(rows), "kinds": [x["kind"] for x in rows]})
        self.assertEqual(calls, ["primary"])
        self.assertEqual(len(rows), 2)                       # wrapper入口 + primary のみ(fallbackは0)

    def test_item2c_stop_during_cooldown_blocks_regeneration_after_wait(self):
        import er020_tts_retry_local_rewrite_01 as er020
        d = self.tmp()
        api = r.MockApi(d)
        st.set_stop_run_dir(d)
        slept = []

        def fake_sleep(sec):                                # 実待機はしない。待機中にSTOPが置かれたことにする
            slept.append(sec)
            self._stop(d)

        info = er020.maybe_cooldown_before_attempt(3, 3, True, sleep_fn=fake_sleep)   # 共有module本体のcool-down
        self.assertEqual(slept, [er020.COOLDOWN_SECONDS])
        self.assertIsNotNone(info)
        with self.assertRaises(st.FamilyZStopSentinelAbort):
            api.call("tts_attempt3_after_cooldown")
        rows = read_jsonl(f"{d}/mock_api_calls.jsonl")
        ev("item2c_cooldown.json", {"item": 2, "cooldown_requested_seconds": slept, "cooldown_info": info,
                                    "api_calls_after_cooldown": len(rows), "audit": read_jsonl(f"{d}/{st.AUDIT_NAME}")})
        self.assertEqual(rows, [])

    def test_item2d_sdk_entry_guard_blocks_real_sdk_methods_before_network(self):
        """real時のSDK入口guard: 実SDKクラスをwrapし、STOP中は(selfがNoneでも)network以前に停止する。"""
        d = self.tmp()
        done = st.install_api_stop_guard()
        st.set_stop_run_dir(d)
        self._stop(d)
        from openai.resources.audio import transcriptions
        from openai.resources.responses import responses
        from google.genai import models
        blocked = {}
        for name, fn in (("openai.responses.create", lambda: responses.Responses.create(None, model="x", input="y")),
                         ("openai.audio.transcriptions.create", lambda: transcriptions.Transcriptions.create(None, file=b"x", model="m")),
                         ("gemini.models.generate_content", lambda: models.Models.generate_content(None, model="m", contents="c"))):
            with self.assertRaises(st.FamilyZStopSentinelAbort):
                fn()
            blocked[name] = True
        ev("item2d_sdk_entry_guard.json", {"item": 2, "installed": done, "blocked": blocked})
        self.assertIn("openai.responses.create", done)
        self.assertIn("gemini.models.generate_content", done)
        self.assertEqual(len(blocked), 3)

    def test_item2e_guard_passes_through_when_no_stop_and_is_outermost_after_cost_logger(self):
        class Dummy:
            def create(self, x):
                return ("ok", x)
        self.assertTrue(st._wrap_attr(Dummy, "create", "dummy"))
        self.assertFalse(st._wrap_attr(Dummy, "create", "dummy"))        # 二重wrapしない
        self.assertEqual(Dummy().create(3), ("ok", 3))
        import inspect
        src = inspect.getsource(r.build_real_context)
        self.assertLess(src.index("cl.install(cost_log)"), src.index("install_api_stop_guard()"))
        self.assertLess(src.index("install_api_stop_guard()"), src.index("vfl01.get_client()"))


# ============================================================
# 項目3: --regenerate-stage / resume
# ============================================================
class Item3RegenerateResume(Base):
    def test_item3_regenerate_and_resume_blocked_then_cleared_resume_works(self):
        run = "run_stoptest_03"
        rc, out, err = cli(["--mode", "mock", "--stage", "all", "--stop-after", "kp", "--run", run])
        self.assertEqual(rc, 0, err)
        n0 = len(counter(run))
        self.assertGreater(n0, 0)
        stop = os.path.join(run_dir(run, mock=False), "STOP")
        os.makedirs(os.path.dirname(stop), exist_ok=True)
        with open(stop, "w", encoding="utf-8") as f:
            f.write("item3")
        res = {"item": 3, "initial_calls": n0}
        for tag, args in (("regenerate_writer", ["--stage", "writer", "--regenerate-stage", "r2"]),
                          ("resume_tts_b1b", ["--stage", "tts_b1b"]),
                          ("resume_tts_a2", ["--stage", "tts_a2"]),
                          ("resume_all", ["--stage", "all"])):
            rc, _o, _e = cli(["--mode", "mock", "--run", run] + args)
            res[tag] = {"rc": rc, "calls_after": len(counter(run))}
            self.assertEqual(rc, 3, tag)
            self.assertEqual(len(counter(run)), n0, tag)           # 追加API呼出ゼロ
        audit = read_jsonl(os.path.join(run_dir(run), "audit_stop_sentinel.jsonl"))
        # startup確認は<run>_mock配下にも<run>配下にも記録されうる(どちらかに監査が残ればよい)
        audit_any = audit or read_jsonl(os.path.join(run_dir(run, mock=False), "audit_stop_sentinel.jsonl"))
        res["audit_count"] = len(audit_any)
        # 正規解除 -> resumeが再び動く(STOPが原因で止まっていたことの対照)
        rc, out, err = cli(["--mode", "mock", "--run", run, "--clear-stop", "--reason", "item3 test: resume allowed"])
        self.assertEqual(rc, 0, err)
        rc, out, err = cli(["--mode", "mock", "--run", run, "--stage", "tts_b1b"])
        res["after_clear_resume_rc"] = rc
        res["after_clear_calls"] = len(counter(run))
        ev("item3_regenerate_resume.json", res)
        save_run_evidence(run, "item3_run_stoptest_03")
        self.assertEqual(rc, 0, err)
        self.assertGreater(len(counter(run)), n0)
        self.assertTrue(audit_any)


# ============================================================
# 項目4: 親runner/別名wrapper/監視ループからの再起動阻止
# ============================================================
class Item4aWrappersBlockedByStopAll(Base):
    def _check(self, tag, rc, run, results):
        results[tag] = {"rc": rc, "run_dir_created": os.path.exists(run_dir(run)) or os.path.exists(run_dir(run, False))}
        self.assertEqual(rc, 3, tag)
        self.assertFalse(results[tag]["run_dir_created"], tag)          # STOP_ALL中は何も作らない

    def test_item4a_all_launch_paths_stopped_by_stop_all(self):
        results = {"item": "4a"}
        with real_stop_all():
            # (1) 直接起動 mock / real
            rc, _o, _e = cli(["--mode", "mock", "--stage", "all", "--run", "run_stoptest_4a1"])
            self._check("direct_mock", rc, "run_stoptest_4a1", results)
            rc, _o, _e = cli(["--mode", "real", "--stage", "all", "--run", "run_stoptest_4a2", "--approved-budget-jpy", "100"])
            self._check("direct_real", rc, "run_stoptest_4a2", results)
            # (2) runpy wrapper
            code = ("import runpy,sys; sys.argv=['%s','--mode','real','--stage','tts_a2','--run','run_stoptest_4a3',"
                    "'--approved-budget-jpy','100']; runpy.run_path('%s', run_name='__main__')" % (RUNNER, RUNNER))
            p = subprocess.run([PY, "-c", code], cwd=REPO, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
            self._check("runpy_wrapper", p.returncode, "run_stoptest_4a3", results)
            # (3) 別名コピー(ファイル名にer026_family_zを含まない)
            alias = os.path.join(REPO, "zz_alias_runner_tmp_12a.py")
            shutil.copy(os.path.join(REPO, RUNNER), alias)
            try:
                p = subprocess.run([PY, alias, "--mode", "real", "--stage", "tts_b1b", "--run", "run_stoptest_4a4",
                                    "--approved-budget-jpy", "100"], cwd=REPO, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
            finally:
                os.remove(alias)
            self._check("alias_copy", p.returncode, "run_stoptest_4a4", results)
            # (4) subprocess経由の親wrapper
            code = ("import subprocess,sys; sys.exit(subprocess.run([sys.executable,'%s','--mode','real','--stage','all',"
                    "'--run','run_stoptest_4a5','--approved-budget-jpy','100']).returncode)" % RUNNER)
            p = subprocess.run([PY, "-c", code], cwd=REPO, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
            self._check("subprocess_wrapper", p.returncode, "run_stoptest_4a5", results)
            # (5) 別cwdから絶対pathで起動(STOP_ALLは絶対path)
            p = subprocess.run([PY, os.path.join(REPO, RUNNER), "--mode", "real", "--stage", "all", "--run", "run_stoptest_4a6",
                                "--approved-budget-jpy", "100"], cwd=self.tmp(), capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
            # 別cwdでは共有module(er002_ja_article_generation)のimport時に相対path依存で失敗し、そもそもAPIに到達しない(既存仕様)。
            # STOP_ALL自体はcwd非依存(絶対path)であることを、cwdを変えた同一processで確認する。
            cwd0 = os.getcwd()
            os.chdir(self.tmp())
            try:
                hit_other_cwd = st.stop_sentinel_hit("nonexistent_run_dir")
            finally:
                os.chdir(cwd0)
            results["other_cwd"] = {"subprocess_rc": p.returncode, "subprocess_stderr_tail": p.stderr[-160:],
                                    "stop_all_detected_from_other_cwd": hit_other_cwd}
            self.assertNotEqual(p.returncode, 0)
            self.assertEqual(hit_other_cwd, st.STOP_ALL_PATH)
            self.assertFalse(os.path.exists(run_dir("run_stoptest_4a6", mock=False)))
            # (6) Writer単体CLI(er062)のreal
            p = subprocess.run([PY, "er062_family_z_writer_01.py", "--run", "run_stoptest_4a7", "--stage", "writer",
                                "--mode", "real", "--approved-budget-jpy", "50"], cwd=REPO, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
            results["writer_cli_real"] = {"rc": p.returncode, "stderr_tail": p.stderr[-200:]}
            self.assertEqual(p.returncode, 3)
            self.assertFalse(os.path.exists(w62.out_dir_for("melos", "run_stoptest_4a7")))
            # (7) 解除しなければ通らない(STOP_ALL存在中、--clear-stop でも STOP_ALL は消えない)
            rc, o, _e = cli(["--mode", "mock", "--run", "run_stoptest_4a1", "--clear-stop", "--reason", "x"])
            results["clear_stop_does_not_remove_stop_all"] = {"rc": rc, "stop_all_still_exists": os.path.exists(st.STOP_ALL_PATH)}
            self.assertTrue(os.path.exists(st.STOP_ALL_PATH))
        self.assertFalse(os.path.exists(st.STOP_ALL_PATH))
        ev("item4a_wrappers_blocked.json", results)

    def test_item4c_real_mode_refused_before_any_client_creation(self):
        """STOP_ALL中は --mode real をclient/cost logger生成の前に拒否する(各client取得箇所も個別に確認)。"""
        d = self.tmp()
        stop_all = os.path.join(d, "STOP_ALL")
        with open(stop_all, "w", encoding="utf-8") as f:
            f.write("x")
        boom = lambda *a, **k: (_ for _ in ()).throw(AssertionError("CLIENT/LOGGER CREATED UNDER STOP_ALL"))   # noqa: E731
        results = {"item": "4c"}
        with mock.patch.object(st, "STOP_ALL_PATH", stop_all), \
                mock.patch("er003_v1_en_direct_vfl_01_generate.get_client", boom), \
                mock.patch("er003_v1_b1_scaffold_01_generate.get_client", boom), \
                mock.patch("er005_cost_logger.install", boom), \
                mock.patch("er005_cost_logger.init_logger", boom):
            args = r.build_parser().parse_args(["--mode", "real", "--approved-budget-jpy", "100", "--run", "run_stoptest_4c"])
            with self.assertRaises(st.FamilyZStopSentinel):
                r.build_real_context(args)
            results["build_real_context"] = "STOPPED_BEFORE_CLIENT"
            self.assertFalse(os.path.exists(run_dir("run_stoptest_4c", mock=False)))
            with self.assertRaises(st.FamilyZStopSentinel):
                w62._setup_real(os.path.join(d, "w62run"))
            results["er062_setup_real"] = "STOPPED_BEFORE_CLIENT"
            with self.assertRaises(st.FamilyZStopSentinel):
                a63.real_generators()
            results["er063_real_generators"] = "STOPPED_BEFORE_CLIENT"
            with self.assertRaises(st.FamilyZStopSentinel):
                a63.default_llm_attribution_fn()([{"quote_id": "q", "quote": "x", "context": "y"}])
            results["er063_attribution_client"] = "STOPPED_BEFORE_CLIENT"
            import io
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                code = r.main(["--mode", "real", "--stage", "all", "--run", "run_stoptest_4c", "--approved-budget-jpy", "100"])
            results["main_real"] = {"rc": code}
            self.assertEqual(code, 3)
            self.assertFalse(os.path.exists(run_dir("run_stoptest_4c", mock=False)))
            r._release_launch_lock()
        ev("item4c_real_refused_before_client.json", results)


class Item4bRunLock(Base):
    def test_item4b_unit_pid_alive_and_stale_replacement(self):
        d = self.tmp()
        self.assertTrue(st.pid_alive(os.getpid()))
        dead = subprocess.Popen([PY, "-c", "pass"])
        dead.wait()
        self.assertFalse(st.pid_alive(dead.pid))
        with open(f"{d}/{st.RUN_LOCK_NAME}", "w", encoding="utf-8") as f:
            json.dump({"pid": dead.pid, "parent_pid": 1, "started_at": "x"}, f)
        rec = st.acquire_run_lock(d, ["t"])                         # stale -> 置換
        self.assertEqual(rec["pid"], os.getpid())
        self.assertTrue(any(x.get("event") == "RUN_LOCK_STALE_REPLACED" for x in read_jsonl(f"{d}/{st.AUDIT_NAME}")))
        self.assertTrue(st.release_run_lock(d))
        self.assertFalse(os.path.exists(f"{d}/{st.RUN_LOCK_NAME}"))

    def test_item4b_live_lock_refuses_second_launch_and_real_double_launch(self):
        results = {"item": "4b"}
        # (1) 生存中の別PIDが保持するlock -> rc=4、API呼出ゼロ
        run = "run_stoptest_4b1"
        os.makedirs(run_dir(run), exist_ok=True)
        holder = subprocess.Popen([PY, "-c", "import time; time.sleep(60)"])
        try:
            with open(os.path.join(run_dir(run), st.RUN_LOCK_NAME), "w", encoding="utf-8") as f:
                json.dump({"pid": holder.pid, "parent_pid": os.getpid(), "started_at": "now"}, f)
            rc, _o, err = cli(["--mode", "mock", "--stage", "all", "--run", run])
            results["live_lock_manual"] = {"rc": rc, "calls": len(counter(run)), "stderr": err[-200:]}
            self.assertEqual(rc, 4)
            self.assertEqual(counter(run), [])
            self.assertTrue(os.path.exists(os.path.join(run_dir(run), st.RUN_LOCK_NAME)))    # 他者のlockは消さない
        finally:
            holder.kill()
        # lock保持者が死ぬ -> stale -> 起動できる
        holder.wait()
        rc, _o, err = cli(["--mode", "mock", "--stage", "seed_check", "--run", run])
        results["stale_lock_after_holder_died"] = {"rc": rc}
        self.assertEqual(rc, 0, err)
        self.assertFalse(os.path.exists(os.path.join(run_dir(run), st.RUN_LOCK_NAME)))
        # (2) 実プロセス2つ: P1稼働中にP2を同一runで起動 -> P2はrc=4
        run2 = "run_stoptest_4b2"
        env = dict(os.environ, FAMILY_Z_MOCK_API_DELAY_SEC="0.25")
        p1 = subprocess.Popen([PY, RUNNER, "--mode", "mock", "--stage", "all", "--stop-after", "tts_a2", "--run", run2], cwd=REPO,
                              env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        try:
            t0 = time.time()
            while time.time() - t0 < 60 and not os.path.exists(os.path.join(run_dir(run2), st.RUN_LOCK_NAME)):
                time.sleep(0.05)
            with open(os.path.join(run_dir(run2), st.RUN_LOCK_NAME), encoding="utf-8") as fh:
                lock = json.load(fh)
            rc2, _o, err2 = cli(["--mode", "mock", "--stage", "all", "--stop-after", "tts_a2", "--run", run2])
            p1_out, p1_err = p1.communicate(timeout=120)
        finally:
            if p1.poll() is None:
                p1.kill()
        pids = {x["pid"] for x in counter(run2)}
        results["real_double_launch"] = {"p1_rc": p1.returncode, "p2_rc": rc2, "lock": lock, "api_caller_pids": sorted(pids),
                                         "lock_removed_after_p1_exit": not os.path.exists(os.path.join(run_dir(run2), st.RUN_LOCK_NAME))}
        ev("item4b_run_lock.json", results)
        save_run_evidence(run2, "item4b_run_stoptest_4b2")
        self.assertEqual(p1.returncode, 0, p1_err)
        self.assertEqual(rc2, 4)
        self.assertEqual(pids, {lock["pid"]})                         # API呼出はP1のみ
        self.assertTrue(results["real_double_launch"]["lock_removed_after_p1_exit"])
        self.assertGreater(lock["parent_pid"], 0)                      # 親PID(venv launcher)も記録される


class Item4dRestartStormAndItem6Clear(Base):
    def test_item4d_restart_storm_creates_stop_and_item6_requires_clear_stop(self):
        run = "run_stoptest_4d"
        results = {"item": "4d+6"}
        rcs = []
        for i in range(3):
            rc, _o, err = cli(["--mode", "mock", "--stage", "seed_check", "--run", run])
            rcs.append(rc)
        results["launch_rcs"] = rcs
        self.assertEqual(rcs, [0, 0, 3])                                # 3回目(5分間に3回)でRESTART_STORM
        d = run_dir(run)
        launches = [x for x in read_jsonl(f"{d}/{st.LAUNCH_LOG_NAME}") if x["event"] == "LAUNCH"]
        audit = read_jsonl(f"{d}/{st.AUDIT_NAME}")
        results["launch_log_entries"] = len(launches)
        results["audit_events"] = [x.get("event") for x in audit]
        self.assertEqual(len(launches), 3)
        self.assertTrue(all(x["parent_pid"] and x["pid"] for x in launches))
        self.assertTrue(os.path.exists(f"{d}/STOP"))
        self.assertTrue(os.path.exists(f"{d}/{st.RESTART_STORM_MARKER}"))
        with open(f"{d}/STOP", encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["reason"], "RESTART_STORM")
        self.assertIn("RESTART_STORM", results["audit_events"])
        # 以降の起動も停止(startup確認。起動履歴は増えない)
        rc, _o, _e = cli(["--mode", "mock", "--stage", "all", "--run", run])
        self.assertEqual(rc, 3)
        # STOPファイルだけ手動削除しても RESTART_STORM 由来は解除されない(markerが残る)
        os.remove(f"{d}/STOP")
        rc, _o, _e = cli(["--mode", "mock", "--stage", "all", "--run", run])
        results["after_manual_delete_rc"] = rc
        self.assertEqual(rc, 3)
        # --reason なしの --clear-stop は拒否
        rc, _o, _e = cli(["--mode", "mock", "--run", run, "--clear-stop"])
        results["clear_without_reason_rc"] = rc
        self.assertEqual(rc, 2)
        self.assertTrue(os.path.exists(f"{d}/{st.RESTART_STORM_MARKER}"))
        # 正規解除(--clear-stop --reason)
        rc, out, err = cli(["--mode", "mock", "--run", run, "--clear-stop", "--reason", "item4d test: storm acknowledged"])
        results["clear_with_reason_rc"] = rc
        self.assertEqual(rc, 0, err)
        self.assertFalse(os.path.exists(f"{d}/STOP"))
        self.assertFalse(os.path.exists(f"{d}/{st.RESTART_STORM_MARKER}"))
        cleared = [x for x in read_jsonl(f"{d}/{st.AUDIT_NAME}") if x.get("event") == "CLEARED"]
        results["cleared_audit"] = cleared
        self.assertEqual(len(cleared), 1)
        self.assertIn("storm acknowledged", cleared[0]["reason"])
        # 解除後は起動できる(カウントはCLEARED以降)
        rc, _o, err = cli(["--mode", "mock", "--stage", "seed_check", "--run", run])
        results["after_clear_rc"] = rc
        self.assertEqual(rc, 0, err)
        ev("item4d_item6_restart_storm_clear.json", results)
        save_run_evidence(run, "item4d_run_stoptest_4d")

    def test_item6_normal_stop_manual_delete_ok_run_closed_not_clearable_stop_all_untouched(self):
        results = {"item": 6}
        run = "run_stoptest_6"
        d = run_dir(run)
        os.makedirs(d, exist_ok=True)
        # 通常STOP: 手動削除で再開可
        with open(f"{d}/STOP", "w", encoding="utf-8") as f:
            f.write("plain")
        rc, _o, _e = cli(["--mode", "mock", "--stage", "seed_check", "--run", run])
        self.assertEqual(rc, 3)
        os.remove(f"{d}/STOP")
        rc, _o, err = cli(["--mode", "mock", "--stage", "seed_check", "--run", run])
        results["manual_delete_normal_stop_then_run_rc"] = rc
        self.assertEqual(rc, 0, err)
        # 通常STOPの --clear-stop も記録付きで可
        with open(f"{d}/STOP", "w", encoding="utf-8") as f:
            f.write("plain2")
        rc, _o, err = cli(["--mode", "mock", "--run", run, "--clear-stop", "--reason", "item6 plain clear"])
        self.assertEqual(rc, 0, err)
        self.assertTrue(any(x.get("event") == "CLEARED" for x in read_jsonl(f"{d}/{st.AUDIT_NAME}")))
        # RUN_CLOSED は --clear-stop でも解除不可(rc=5)
        with open(f"{d}/STOP", "w", encoding="utf-8") as f:
            json.dump({"reason": "RUN_CLOSED"}, f)
        rc, _o, err = cli(["--mode", "mock", "--run", run, "--clear-stop", "--reason", "try to reopen"])
        results["run_closed_clear_rc"] = rc
        self.assertEqual(rc, 5)
        self.assertTrue(os.path.exists(f"{d}/STOP"))
        ev("item6_clear_stop_rules.json", results)
        save_run_evidence(run, "item6_run_stoptest_6")


# ============================================================
# 項目5: STOP後のAPI呼出ゼロ・追加費用ゼロ(実run_e2e_01のcost_logが不変)
# ============================================================
class Item5NoSpendNoCalls(Base):
    SHARED = [REAL_RUN_COST_LOG, REAL_RUN_STAGE_LOG]

    def test_item5_real_run_logs_untouched_and_real_never_reaches_client(self):
        def snap():
            return {p: (os.path.getsize(p), os.stat(p).st_mtime_ns) if os.path.exists(p) else None for p in self.SHARED}
        before = snap()
        with real_stop_all():
            rc, _o, _e = cli(["--mode", "real", "--stage", "all", "--run", "run_e2e_01", "--approved-budget-jpy", "100"])
            self.assertEqual(rc, 3)
        run_closed = os.path.exists(os.path.join(MELOS, "run_e2e_01", "STOP"))
        after = snap()
        ev("item5_no_spend.json", {"item": 5, "real_run_attempt_rc": 3, "run_e2e_01_logs_before": before,
                                   "run_e2e_01_logs_after": after, "run_e2e_01_closed_STOP_present": run_closed})
        self.assertEqual(before, after)                    # cost_log/stage_logとも増えない=追加費用ゼロ


# ============================================================
# 項目7: Fable用緊急停止ツール
# ============================================================
class Item7StopAllTool(Base):
    def test_item7_tool_dry_run_execute_release(self):
        d = self.tmp()
        stop_all, audit = os.path.join(d, "STOP_ALL"), os.path.join(d, "audit.jsonl")
        marker = "FAMZ_DUMMY_MARKER_7f3a12a"
        dummy = subprocess.Popen([PY, "-c", f"import time; time.sleep(120)  # {marker}"])
        results = {"item": 7}
        try:
            time.sleep(1.0)
            tool_args = ["--stop-all-path", stop_all, "--audit-path", audit, "--pattern", marker]
            # dry-run: 列挙のみ・STOP_ALL未作成・プロセス生存
            p = subprocess.run([PY, "tools/stop_all_family_z.py"] + tool_args, cwd=REPO, capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            dry = json.loads(p.stdout)
            results["dry_run"] = dry
            self.assertEqual(p.returncode, 0)
            self.assertIn(dummy.pid, [x["pid"] for x in dry["would_stop"]])     # venv launcherと実体の2PIDが並ぶ場合がある
            self.assertFalse(os.path.exists(stop_all))
            self.assertIsNone(dummy.poll())
            # execute(--reason必須)
            p = subprocess.run([PY, "tools/stop_all_family_z.py", "--execute"] + tool_args, cwd=REPO, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
            self.assertEqual(p.returncode, 2)
            self.assertIsNone(dummy.poll())
            p = subprocess.run([PY, "tools/stop_all_family_z.py", "--execute", "--reason", "item7 test"] + tool_args, cwd=REPO,
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            ex = json.loads(p.stdout)
            results["execute"] = ex
            self.assertEqual(p.returncode, 0, p.stderr)
            dummy.wait(timeout=20)
            self.assertTrue(os.path.exists(stop_all))
            self.assertIsNotNone(dummy.poll())
            # release
            p = subprocess.run([PY, "tools/stop_all_family_z.py", "--release", "--reason", "item7 done"] + tool_args, cwd=REPO,
                               capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
            self.assertEqual(p.returncode, 0)
            self.assertFalse(os.path.exists(stop_all))
            results["audit"] = read_jsonl(audit)
            self.assertEqual([x["event"] for x in results["audit"]], ["STOP_ALL_CREATED", "STOP_ALL_RELEASED"])
        finally:
            if dummy.poll() is None:
                dummy.kill()
        ev("item7_stop_all_tool.json", results)

    def test_item7_governance_documents_rules(self):
        with open(os.path.join(REPO, "docs/pm/PM_GOVERNANCE.md"), encoding="utf-8") as f:
            t = f.read()
        i = t.index("## 26. ")
        sec = t[i:i + 6000]
        for key in ("STOP_ALL", "再起動", "RESTART_STORM"):
            self.assertIn(key, sec, key)


if __name__ == "__main__":
    unittest.main()
