# -*- coding: utf-8 -*-
"""RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C3(2026-10-10)。API呼び出し0、費用0円(API部はstub)。

C3対象:
  C3-1 audio runner TTS直前の三者sha照合(ensure_rf_record)。個別stage実行(--stage tts)でもRFが抜けない。
  C3-2 audio側 compute_cost_jpy_so_far の fail-closed 化(G-4)。cost_usd付きレコードは採用、RF Geminiレコードはcost_usd併記。
  C3-3 entertainment runner の cost.json を非OpenAI(Gemini)対応版へ切替。
  C3-4 Astra pricing note 更新(価格値は不変)。
  C3-5 review queue _IndexLock の PermissionError(別ファイル: er053_review_queue_01_test_01.py)。

実行: .venv/Scripts/python.exe -m pytest er053_c3_audio_guard_test_01.py -q
"""
from __future__ import annotations

import ast
import functools
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_entertainment_production_runner_01 as ent
import er053_cost_aggregate_01 as ca
import er053_review_queue_01 as rq
import er053_risk_flagger_production_01 as rf
from er053_risk_flagger_production_01_test_01 import LEDGER, Stub, _ok_text, flag

HERE = os.path.dirname(os.path.abspath(__file__))
PRICING = os.path.join(HERE, "er005_output", "cost_baseline_01", "pricing_snapshot.json")

# 3段落以上(v2構造: 見出しなし)+ In one line。LEDGERのF-003(Prices rose 20 percent.)と食い違う文を含む。
ARTICLE = """# Title Line

The company paused the feature. Prices rose 30 percent.

U.S. officials said it was fine. Many people watched closely.

Experts said the change would continue for some time.

## In one line
Prices matter, and so does a pause.
"""


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make_source(root, slug="_unit_test_c3_rf_guard_01", run="run_01", with_ledger=True):
    """cwd相対 er019_output/<slug>/<run> に fixture を作る(使い捨て、tearDownで削除)。"""
    sd = os.path.join("er019_output", slug, run)
    for level in ("a2", "b1b"):
        os.makedirs(os.path.join(sd, level), exist_ok=True)
        with open(os.path.join(sd, level, "article.md"), "w", encoding="utf-8", newline="") as f:
            f.write(ARTICLE)
    if with_ledger:
        os.makedirs(os.path.join(sd, "research_ledger"), exist_ok=True)
        with open(os.path.join(sd, "research_ledger", "verified_fact_ledger.txt"), "w", encoding="utf-8", newline="") as f:
            f.write(LEDGER)
    return sd


class Base(unittest.TestCase):
    def setUp(self):
        self.slug = "_unit_test_c3_rf_guard_01"
        self.source_dir = make_source(HERE, self.slug)
        self.out = tempfile.mkdtemp(prefix="c3_audio_out_")
        self.qroot = tempfile.mkdtemp(prefix="c3_queue_")
        self.addCleanup(shutil.rmtree, os.path.join("er019_output", self.slug), True)
        self.addCleanup(shutil.rmtree, self.out, True)
        self.addCleanup(shutil.rmtree, self.qroot, True)
        self.article_id = rq.derive_article_id(self.source_dir)

    def stub_rf(self, stub=None):
        self.stub = stub or Stub()
        return functools.partial(rf.run_risk_flagger, call_fn=self.stub, sleep_fn=lambda s: None)

    def put_queue(self, level, article_sha):
        """Review Queueのindexへ(article_id, level, sha)を直接1行入れる。"""
        rq.append_index(self.qroot, {"article_id": self.article_id, "article_level": level, "article_sha256": article_sha,
                                     "run_id": "rfPRE", "timestamp": "t", "status": "OK", "queue_path": "x"})

    def scaffold_sha(self, level, value=None):
        runner.record_scaffold_article_sha(self.out, level, f"{self.source_dir}/{level}/article.md")
        if value is not None:
            p = f"{self.out}/{runner.SCAFFOLD_SHA_RECORD}"
            d = json.load(open(p, encoding="utf-8"))
            d[level]["article_sha256"] = value
            json.dump(d, open(p, "w", encoding="utf-8"))


class ThreeWayShaTests(Base):
    def test_all_three_match_means_no_rf(self):
        s = sha(f"{self.source_dir}/b1b/article.md")
        self.scaffold_sha("b1b")
        self.put_queue("b1b", s)
        called = []
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot,
                                    rf_runner=lambda **k: called.append(k))
        self.assertEqual(called, [])
        self.assertEqual(r["action"], "verified")
        self.assertTrue(r["match"])
        self.assertEqual(r["mismatch_reasons"], [])
        self.assertEqual(len(rq.read_index(self.qroot)), 1)        # Queueへ追記しない

    def test_no_queue_runs_rf_and_saves_queue_with_level_and_labels(self):
        self.scaffold_sha("b1b")
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, run_label="L3-A", queue_root=self.qroot,
                                    rf_runner=self.stub_rf())
        self.assertEqual(r["action"], "rf_executed")
        self.assertIn("no_queue_record", r["mismatch_reasons"])
        self.assertEqual(r["rf_status"], "OK")
        self.assertTrue(r["queue_saved"])
        self.assertEqual(r["run_label"], "audio_tts_guard:L3-A")
        rows = rq.read_index(self.qroot)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["article_id"], rows[0]["article_level"], rows[0]["article_sha256"]),
                         (self.article_id, "b1b", sha(f"{self.source_dir}/b1b/article.md")))
        self.assertEqual(rows[0]["run_label"], "audio_tts_guard:L3-A")
        # 記録: audit/rf_tts_guard.json と entry_point.json(rf module側)
        g = json.load(open(f"{self.out}/{runner.RF_TTS_GUARD_RECORD}", encoding="utf-8"))
        self.assertEqual(g["b1b"]["action"], "rf_executed")
        ep = json.load(open(f"{self.out}/entry_point.json", encoding="utf-8"))
        self.assertEqual(ep["risk_flagger"]["b1b"]["run_label"], "audio_tts_guard:L3-A")

    def test_second_call_after_rf_is_verified_idempotent(self):
        self.scaffold_sha("a2")
        run = self.stub_rf()
        r1 = runner.ensure_rf_record(self.source_dir, self.out, "a2", 150.0, queue_root=self.qroot, rf_runner=run)
        n = len(self.stub.calls)
        self.assertEqual(r1["action"], "rf_executed")
        r2 = runner.ensure_rf_record(self.source_dir, self.out, "a2", 150.0, queue_root=self.qroot, rf_runner=run)
        self.assertEqual(r2["action"], "verified")
        self.assertEqual(len(self.stub.calls), n)               # 2回目はAPI呼出なし

    def test_scaffold_sha_differs_from_source_runs_rf(self):
        s = sha(f"{self.source_dir}/b1b/article.md")
        self.scaffold_sha("b1b", value="0" * 64)          # scaffold後に記事が変わった想定
        self.put_queue("b1b", s)
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot, rf_runner=self.stub_rf())
        self.assertEqual(r["action"], "rf_executed")
        self.assertEqual(r["mismatch_reasons"], ["scaffold_sha_ne_source_sha"])

    def test_queue_sha_differs_from_source_runs_rf(self):
        self.scaffold_sha("b1b")
        self.put_queue("b1b", "f" * 64)
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot, rf_runner=self.stub_rf())
        self.assertEqual(r["action"], "rf_executed")
        self.assertEqual(r["mismatch_reasons"], ["source_sha_ne_queue_sha"])

    def test_scaffold_sha_missing_runs_rf(self):
        self.put_queue("b1b", sha(f"{self.source_dir}/b1b/article.md"))
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot, rf_runner=self.stub_rf())
        self.assertEqual(r["action"], "rf_executed")
        self.assertEqual(r["mismatch_reasons"], ["scaffold_sha_missing"])

    def test_queue_for_other_level_or_article_does_not_count(self):
        self.scaffold_sha("b1b")
        s = sha(f"{self.source_dir}/b1b/article.md")
        self.put_queue("a2", s)                                    # Level違い
        rq.append_index(self.qroot, {"article_id": "other_article", "article_level": "b1b", "article_sha256": s})
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot, rf_runner=self.stub_rf())
        self.assertEqual(r["action"], "rf_executed")

    def test_fallback_queue_in_source_dir_counts_as_record(self):
        """Queue保存失敗時のfallback(source_dir/risk_flagger_fallback/<level>__*/queue.json)も記録として認める。"""
        self.scaffold_sha("b1b")
        fb = os.path.join(self.source_dir, "risk_flagger_fallback", "b1b__rfX")
        os.makedirs(fb)
        json.dump({"article_id": self.article_id, "article_level": "b1b",
                   "article_sha256": sha(f"{self.source_dir}/b1b/article.md")}, open(os.path.join(fb, "queue.json"), "w"))
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot,
                                    rf_runner=lambda **k: self.fail("RF must not run"))
        self.assertEqual(r["action"], "verified")

    def test_derived_sha_mismatch_is_warning_only(self):
        """S3-2: a2派生元(b1b)sha不一致は警告記録のみ(三者が一致していればRFは走らない・STOPしない)。"""
        os.makedirs(f"{self.source_dir}/a2/audit", exist_ok=True)
        json.dump({"derived_from_advanced_sha256": "1" * 64}, open(f"{self.source_dir}/a2/audit/derived_from_advanced_sha256.json", "w"))
        self.scaffold_sha("a2")
        self.put_queue("a2", sha(f"{self.source_dir}/a2/article.md"))
        r = runner.ensure_rf_record(self.source_dir, self.out, "a2", 150.0, queue_root=self.qroot,
                                    rf_runner=lambda **k: self.fail("RF must not run"))
        self.assertEqual(r["action"], "verified")
        self.assertEqual(len(r["warnings"]), 1)
        self.assertIn("derived_from_advanced_sha_mismatch", r["warnings"][0]["warning"])


class NonBlockingTests(Base):
    def test_flags_present_still_returns_normally(self):
        self.scaffold_sha("b1b")
        st = Stub(scripts={("luna", "A3"): [_ok_text([flag("S-003")])]})
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot, rf_runner=self.stub_rf(st))
        self.assertEqual(r["rf_status"], "OK")
        self.assertGreaterEqual(r["issue_count"], 0)

    def test_rf_unavailable_all_down_still_returns(self):
        self.scaffold_sha("b1b")
        st = Stub(default=RuntimeError("down"))
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot, rf_runner=self.stub_rf(st))
        self.assertEqual(r["rf_status"], "RF_UNAVAILABLE")
        self.assertTrue(r["queue_saved"])               # RF_UNAVAILABLEもQueueへ保存される

    def test_unexpected_exception_in_rf_runner_is_non_blocking(self):
        self.scaffold_sha("b1b")

        def boom(**k):
            raise ValueError("unexpected")
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot, rf_runner=boom)
        self.assertEqual(r["rf_status"], "RF_UNAVAILABLE")
        self.assertIn("ValueError", r["rf_reason"])

    def test_missing_ledger_is_rf_unavailable_not_exception(self):
        shutil.rmtree(f"{self.source_dir}/research_ledger")
        self.scaffold_sha("b1b")
        r = runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot, rf_runner=self.stub_rf())
        self.assertEqual(r["rf_status"], "RF_UNAVAILABLE")

    def test_budget_stop_propagates_existing_safety_not_bypassed(self):
        """予算超過STOP(既存安全装置)はRF非Blockingでも握りつぶさない。"""
        self.scaffold_sha("b1b")
        # raw_usage_log.jsonlに上限超過の実額レコードを置く -> budget_check(assert_budget_ok)がRuntimeError -> BudgetCheckStop
        with open(f"{self.out}/raw_usage_log.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps({"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "cost_usd": 10.0}) + "\n")
        with self.assertRaises(rf.BudgetCheckStop):
            runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot, rf_runner=self.stub_rf())
        self.assertEqual(self.stub.calls, [])              # 予算超過のためAPI呼出前にSTOP

    def test_article_modified_propagates(self):
        self.scaffold_sha("b1b")

        def mutate(**k):
            with open(k["article_path"], "a", encoding="utf-8") as f:
                f.write("\nchanged\n")
            return {"status": "OK", "issues": [], "article_id": "x", "article_level": "b1b", "rf_run_id": "r",
                    "article_sha256": "0", "conditions": [], "timestamp": "t", "sentences": [], "facts": [], "raw": []}
        with self.assertRaises(rf.ArticleModifiedError):
            runner.ensure_rf_record(self.source_dir, self.out, "b1b", 150.0, queue_root=self.qroot, rf_runner=mutate)


# ------------------------------------------------------------
# main() 駆動(個別stage実行でもRFが抜けない)
# ------------------------------------------------------------
class MainStageTests(Base):
    def _drive(self, stage, rf_runner_factory=None, level="both", extra=()):
        events = []
        argv = ["x", "--slug", self.slug, "--run", "run_01", "--stage", stage, "--level", level, "--out-dir", self.out,
                "--tts-backend", "speech_metadata_flash_lite"] + list(extra)
        stub = Stub()
        orig_rf = rf.run_risk_flagger

        def fake_rf(**kw):
            events.append(("rf", kw["article_level"], dict(cl._CONTEXT)))
            return orig_rf(call_fn=stub, sleep_fn=lambda s: None, **kw)
        fake_sc = mock.Mock(return_value={"canonicalization": {"status": "OK"},
                                          "selection": {"status": "OK", "kp_backend_used": "db_hybrid"}})
        patches = [
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(runner.cl, "install", lambda p: None),
            mock.patch.object(vfl01, "get_client", lambda: object()),
            mock.patch.object(rq, "QUEUE_ROOT", self.qroot),
            mock.patch.object(rf, "run_risk_flagger", fake_rf),
            mock.patch.object(runner.sc, "run_key_phrases", fake_sc),
            mock.patch.object(runner, "run_family_x_b1_scaffold", lambda c, p, d: {}),
            mock.patch.object(runner, "run_family_x_a2_scaffold", lambda c, p, d: {}),
            mock.patch.object(runner, "generate_family_x_b1_segments",
                              lambda *a, **k: events.append(("tts", "b1b", dict(cl._CONTEXT)))),
            mock.patch.object(runner, "generate_family_x_a2_segments",
                              lambda *a, **k: events.append(("tts", "a2", dict(cl._CONTEXT)))),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        runner.main()
        return events, stub

    def test_stage_tts_alone_runs_rf_before_tts_when_no_queue(self):
        # scaffold記録だけ先に作る(別プロセスで--stage scaffold済みの想定)
        for lv in ("a2", "b1b"):
            self.scaffold_sha(lv)
        ev, stub = self._drive("tts")
        kinds = [(e[0], e[1]) for e in ev]
        for lv in ("a2", "b1b"):
            self.assertLess(kinds.index(("rf", lv)), kinds.index(("tts", lv)), kinds)
        self.assertEqual(sum(1 for e in ev if e[0] == "rf"), 2)
        self.assertGreater(len(stub.calls), 0)
        # RFは cl.logging_context の外(stage/themeがNone)、TTSはcontext内
        for e in ev:
            if e[0] == "rf":
                self.assertIsNone(e[2].get("stage"))
            else:
                self.assertEqual(e[2].get("stage"), "tts")

    def test_stage_tts_alone_with_queue_present_skips_rf(self):
        for lv in ("a2", "b1b"):
            self.scaffold_sha(lv)
            self.put_queue(lv, sha(f"{self.source_dir}/{lv}/article.md"))
        ev, stub = self._drive("tts")
        self.assertEqual([e for e in ev if e[0] == "rf"], [])
        self.assertEqual(sorted(e[1] for e in ev if e[0] == "tts"), ["a2", "b1b"])
        self.assertEqual(stub.calls, [])

    def test_stage_all_scaffold_then_tts_records_sha_then_rf_then_tts(self):
        """scaffold -> (scaffold時sha記録) -> tts前三者照合 -> RF(Queueなし) -> TTS。RFのQueue保存後に再度ttsすればRFは走らない。"""
        ev, stub = self._drive_all()
        self.assertTrue(os.path.exists(f"{self.out}/{runner.SCAFFOLD_SHA_RECORD}"))
        rec = json.load(open(f"{self.out}/{runner.SCAFFOLD_SHA_RECORD}", encoding="utf-8"))
        self.assertEqual(rec["b1b"]["article_sha256"], sha(f"{self.source_dir}/b1b/article.md"))
        self.assertEqual(rec["a2"]["article_sha256"], sha(f"{self.source_dir}/a2/article.md"))
        kinds = [(e[0], e[1]) for e in ev]
        self.assertLess(kinds.index(("rf", "b1b")), kinds.index(("tts", "b1b")))
        self.assertEqual(len(rq.read_index(self.qroot)), 2)

    def _drive_all(self):
        # all は assemble/player まで走るため、それらも無効化して scaffold -> tts までを観測する
        with mock.patch.object(runner, "stage_assemble_family_x_b1", lambda *a, **k: None), \
                mock.patch.object(runner, "stage_assemble_family_x_a2", lambda *a, **k: None), \
                mock.patch.object(runner, "build_player_html", lambda *a, **k: os.path.join(self.out, "player.html")), \
                mock.patch.object(runner, "derive_japanese_title", lambda sd: {"japanese_title": "題", "source": "test"}):
            return self._drive("all")

    def test_rf_unavailable_still_reaches_tts_via_main(self):
        for lv in ("a2", "b1b"):
            self.scaffold_sha(lv)
        events = []
        argv = ["x", "--slug", self.slug, "--run", "run_01", "--stage", "tts", "--out-dir", self.out,
                "--tts-backend", "speech_metadata_flash_lite"]
        down = Stub(default=RuntimeError("down"))
        with mock.patch.object(sys, "argv", argv), mock.patch.object(runner.cl, "install", lambda p: None), \
                mock.patch.object(vfl01, "get_client", lambda: object()), mock.patch.object(rq, "QUEUE_ROOT", self.qroot), \
                mock.patch.object(rf, "default_call_fn", down), \
                mock.patch.object(rf.time, "sleep", lambda s: None), \
                mock.patch.object(runner, "generate_family_x_b1_segments", lambda *a, **k: events.append("tts_b1b")), \
                mock.patch.object(runner, "generate_family_x_a2_segments", lambda *a, **k: events.append("tts_a2")):
            runner.main()
        self.assertEqual(sorted(events), ["tts_a2", "tts_b1b"])
        g = json.load(open(f"{self.out}/{runner.RF_TTS_GUARD_RECORD}", encoding="utf-8"))
        self.assertEqual({lv: g[lv]["rf_status"] for lv in g}, {"a2": "RF_UNAVAILABLE", "b1b": "RF_UNAVAILABLE"})

    def test_ensure_rf_record_wired_in_tts_branch_before_tts_generation_static(self):
        """AST: main()のtts分岐で、assert_production_tts_backend -> ensure_rf_record -> (logging_context内で)generate_*。"""
        src = open(os.path.join(HERE, "er019_family_x_audio_production_runner_01.py"), encoding="utf-8").read()
        tree = ast.parse(src)
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        tts_if = next(n for n in ast.walk(main) if isinstance(n, ast.If) and "tts" in ast.dump(n.test) and "all" in ast.dump(n.test)
                      and any("ensure_rf_record" in ast.dump(b) for b in n.body))
        order = []
        for stmt in tts_if.body:
            d = ast.dump(stmt)
            if "assert_production_tts_backend" in d:
                order.append("backend")
            elif "ensure_rf_record" in d:
                order.append("rf")
                self.assertNotIn("logging_context", d)         # RFはlogging_contextの外
            elif isinstance(stmt, ast.With) and "logging_context" in ast.dump(stmt.items[0]):
                order.append("tts_ctx")
                self.assertNotIn("ensure_rf_record", d)
        self.assertEqual(order, ["backend", "rf", "tts_ctx"])


# ------------------------------------------------------------
# C3-2 fail-closed
# ------------------------------------------------------------
class AudioCostFailClosedTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="c3_cost_")
        self.addCleanup(shutil.rmtree, self.d, True)

    def _log(self, *recs):
        p = os.path.join(self.d, "raw_usage_log.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
        return p

    def test_unregistered_model_raises_not_zero(self):
        p = self._log({"provider": "gemini", "model_id": "gemini-unregistered-xyz", "input_tokens": 1000, "output_tokens": 10})
        with self.assertRaises(routing.PricingNotFoundError):
            runner.compute_cost_jpy_so_far(p)

    def test_unregistered_openai_asr_raises(self):
        p = self._log({"provider": "openai_asr", "model_id": "whisper-unregistered", "input_tokens": 5})
        with self.assertRaises(routing.PricingNotFoundError):
            runner.compute_cost_jpy_so_far(p)

    def test_budget_guard_does_not_go_blind(self):
        p = self._log({"provider": "gemini", "model_id": "gemini-unregistered-xyz", "input_tokens": 10 ** 9})
        with self.assertRaises(routing.PricingNotFoundError):
            runner.assert_budget_ok(self.d, 150.0)

    def test_cost_usd_is_adopted_even_if_model_unregistered(self):
        """既存挙動維持: cost_usd付きレコードはprice()を呼ばず実額採用(Batch等)。"""
        p = self._log({"provider": "gemini", "model_id": "gemini-unregistered-xyz", "cost_usd": 0.01})
        jpy, byp = runner.compute_cost_jpy_so_far(p)
        self.assertAlmostEqual(jpy, 0.01 * runner.USD_JPY, places=6)

    def test_registered_models_token_priced(self):
        p = self._log({"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "input_tokens": 1_000_000, "output_tokens": 1_000_000})
        jpy, _ = runner.compute_cost_jpy_so_far(p)
        self.assertAlmostEqual(jpy, (0.30 + 2.50) * 160.0, places=4)

    def test_records_without_model_or_non_billed_provider_unchanged(self):
        p = self._log({"provider": "gemini_batch", "model_id": "gemini-3.8-flash-lite-tts"},
                      {"provider": "gemini", "input_tokens": 5},
                      {"provider": "other", "model_id": "zzz", "input_tokens": 5})
        jpy, byp = runner.compute_cost_jpy_so_far(p)
        self.assertEqual(jpy, 0.0)

    def test_no_stopiteration_zero_fallback_left_in_source(self):
        src = open(os.path.join(HERE, "er019_family_x_audio_production_runner_01.py"), encoding="utf-8").read()
        tree = ast.parse(src)
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "compute_cost_jpy_so_far")
        self.assertNotIn("StopIteration", ast.dump(fn))
        lp = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_load_pricing")
        self.assertIn("PricingNotFoundError", ast.dump(lp))

    def test_production_models_pricing_coverage_prerequisite(self):
        """前提test(DESIGN_03 8-2 G-4): 現行Production全model(TTS/ASR/KP/Writer/RF)の単価がinput/outputとも登録済み。"""
        prices = json.load(open(PRICING, encoding="utf-8"))["prices"]
        reg = {(p["provider"], p["model"], p["meter"]) for p in prices if p.get("tier", "Standard") == "Standard"}
        needed = [("gemini", "gemini-2.5-pro-preview-tts"), ("gemini", "gemini-3.1-flash-tts-preview"),
                  ("gemini", "gemini-3.8-flash-lite-tts"), ("gemini", "gemini-3.5-flash-lite"),
                  ("openai_asr", "gpt-4o-mini-transcribe"), ("openai", "gpt-6-luna"), ("openai", "gpt-6-astra"),
                  ("openai", "gpt-5.6-luna")]
        for pr, m in needed:
            for meter in ("input_tokens", "output_tokens"):
                self.assertIn((pr, m, meter), reg, (pr, m, meter))

    def test_rf_gemini_record_has_pinned_model_thinking_included_and_cost_usd(self):
        """RF Geminiレコード: model_id=pinned、output_tokensにthinking込み、cost_usd併記。audio側集計が同額で採用。"""
        recs = []
        prices = rf.load_prices("gemini-3.5-flash-lite", "gemini")
        usage = {"input_tokens": 2000, "output_tokens": 700, "reasoning_tokens": 500, "cached_tokens": 1000}
        with mock.patch.object(cl, "record", lambda e: recs.append(e)):
            rf._record_gemini_cost("gemini-3.5-flash-lite", usage, "rid", 1.0, 1, True, prices=prices)
        e = recs[0]
        self.assertEqual((e["provider"], e["model_id"]), ("gemini", "gemini-3.5-flash-lite"))
        self.assertEqual(e["output_tokens"], 700)                 # thinking込みの値をそのまま計上
        self.assertAlmostEqual(e["cost_usd"], (1000 * 0.30 + 1000 * 0.03 + 700 * 2.50) / 1e6, places=9)
        p = os.path.join(tempfile.mkdtemp(prefix="c3_rfrec_"), "raw_usage_log.jsonl")
        self.addCleanup(shutil.rmtree, os.path.dirname(p), True)
        open(p, "w", encoding="utf-8").write(json.dumps(e) + "\n")
        jpy, _ = runner.compute_cost_jpy_so_far(p)
        self.assertAlmostEqual(jpy, e["cost_usd"] * 160.0, places=8)

    def test_rf_failed_call_record_costs_zero(self):
        recs = []
        with mock.patch.object(cl, "record", lambda e: recs.append(e)):
            rf._record_gemini_cost("gemini-3.5-flash-lite", {}, None, 1.0, 1, False, "boom",
                                   prices=rf.load_prices("gemini-3.5-flash-lite", "gemini"))
        self.assertNotIn("cost_usd", recs[0])
        p = os.path.join(tempfile.mkdtemp(prefix="c3_rfrec_"), "raw_usage_log.jsonl")
        self.addCleanup(shutil.rmtree, os.path.dirname(p), True)
        open(p, "w", encoding="utf-8").write(json.dumps(recs[0]) + "\n")
        self.assertEqual(runner.compute_cost_jpy_so_far(p)[0], 0.0)


# ------------------------------------------------------------
# C3-3 cost.json 切替
# ------------------------------------------------------------
class CostJsonSwitchTests(unittest.TestCase):
    def test_entertainment_cost_json_includes_gemini_rf_stage_and_keeps_old_function(self):
        d = tempfile.mkdtemp(prefix="c3_costjson_")
        self.addCleanup(shutil.rmtree, d, True)
        recs = [{"provider": "openai", "model_id": "gpt-6-luna", "stage": "advanced", "input_tokens": 1000, "output_tokens": 100},
                {"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "stage": "risk_flag.gemini35fl.A3.b1b",
                 "input_tokens": 2000, "output_tokens": 500, "success": True},
                {"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "stage": "risk_flag.gemini35fl.A4.b1b", "success": False}]
        with open(f"{d}/raw_usage_log.jsonl", "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
        ent._write_cost_json(d)
        c = json.load(open(f"{d}/cost.json", encoding="utf-8"))
        self.assertIn("risk_flag.gemini35fl.A3.b1b", c["by_stage_jpy"])
        self.assertGreater(c["by_stage_jpy"]["risk_flag.gemini35fl.A3.b1b"], 0)
        self.assertNotIn("risk_flag.gemini35fl.A4.b1b", c["by_stage_jpy"])       # 失敗呼出は無課金(集計対象外)
        self.assertIn("gemini", c["by_provider_jpy"])
        self.assertEqual(set(c["risk_flag_by_level_model_condition_jpy"]), {"b1b"})
        # 旧関数は残置(openaiのみ=geminiは無視)。openai分の値は新旧で一致
        old = ent.compute_stage_cost_breakdown(f"{d}/raw_usage_log.jsonl")
        self.assertEqual(old["by_stage_jpy"]["advanced"], c["by_stage_jpy"]["advanced"])
        self.assertEqual(old["by_stage_jpy"].get("risk_flag.gemini35fl.A3.b1b"), 0.0)

    def test_audio_runner_does_not_import_entertainment_or_cost_aggregate(self):
        """循環import回避: audio runnerはefam/ca/entertainment runnerをimportしない(audio側は compute_cost_jpy_so_far を使う)。"""
        tree = ast.parse(open(os.path.join(HERE, "er019_family_x_audio_production_runner_01.py"), encoding="utf-8").read())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
        self.assertNotIn("er053_cost_aggregate_01", mods)
        self.assertNotIn("er012_e_family_entertainment_two_level_runner_01", mods)
        for m in mods:
            self.assertFalse(m.startswith(("er050", "er051", "er052")), m)


# ------------------------------------------------------------
# C3-4 Astra note
# ------------------------------------------------------------
class AstraPricingNoteTests(unittest.TestCase):
    def test_note_updated_values_unchanged(self):
        prices = json.load(open(PRICING, encoding="utf-8"))["prices"]
        astra = [p for p in prices if p["model"] == "gpt-6-astra"]
        self.assertEqual(len(astra), 4)
        vals = {p["meter"]: p["price"] for p in astra}
        self.assertEqual(vals, {"input_tokens": 10.0, "cached_input_tokens": 1.0, "output_tokens": 50.0, "cache_write_input_tokens": 12.5})
        for p in astra:
            self.assertIn("W-1 Production採用(2026-10-10ユーザー決定", p["note"])
            self.assertIn("係数1.0", p["note"])
            self.assertIn("マージン", p["note"])
            self.assertNotIn("Trial/DEV用", p["note"])


if __name__ == "__main__":
    unittest.main()
