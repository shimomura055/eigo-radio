# -*- coding: utf-8 -*-
"""C4 runner配線test: 正式 annotated B3 producer が 初回 / regeneration / resume / 再利用 の全経路で
  producer -> 契約検証(T-19) -> W-1(または再利用のU-1来歴確認) の順に呼ばれること、注記なしB3へのfallbackが無いこと。
API呼び出し0、費用0円(client・英訳・RFはstub。producer/契約/W-1/runner mainは実コード)。
実行: .venv/Scripts/python.exe -m pytest er053_c4_wiring_test_01.py -q
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import er019_family_x_entertainment_production_runner_01 as runner
import er053_b3_annotation_contract_01 as contract
import er053_b3_deterministic_producer_01 as annot
import er053_dev_b3_fixture_adapter_01 as adapter
import er053_family_x_factlock_ja_writer_01 as w1

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER_PY = os.path.join(HERE, "er019_family_x_entertainment_production_runner_01.py")


class FakeResp(SimpleNamespace):
    pass


class Client:
    """W-1のR0(Luna)/R1/R2(Astra)を順に返すstub。呼出を events に記録する。"""

    def __init__(self, events):
        self.events = events
        self.responses = self
        self.n = 0
        self.prompts = []
        self.scripts = [("メタの話\n人間が電話をしたというテストがありました。【事実1】\nこれは面白いですね。\n", "gpt-6.1-sol"),
                        ("# タイトル\n\n本文その1です。続きの文です。", "gpt-6.1-sol"),
                        ("# 新タイトル\n\n本文その2です。続きの文です。", "gpt-6.1-sol")]

    def create(self, **kw):
        self.events.append("w1:" + str(kw.get("model")))
        self.prompts.append(kw["input"][-1]["content"])
        text, model = self.scripts[self.n]
        self.n += 1
        return FakeResp(output_text=text, model=model, id="resp_%d" % self.n,
                        usage=SimpleNamespace(input_tokens=10, output_tokens=10))


def _boom(*a, **k):
    raise AssertionError("旧Checker(vfl01.run_deviation_check)が呼ばれた")


class Harness:
    def __init__(self, out, theme="central_bank_mortgage"):
        self.out, self.theme = out, theme
        self.events = []
        self.client = Client(self.events)

    # ---- stubs ----
    def research(self, client, topic, ledger_dir):
        self.events.append("research")
        return {"ledger_text": open(os.path.join(ledger_dir, "verified_fact_ledger.txt"), encoding="utf-8").read()
                if os.path.exists(os.path.join(ledger_dir, "verified_fact_ledger.txt")) else ""}

    def storyline(self, client, topic, ledger_text, out_dir):
        self.events.append("storyline")
        adapter.copy_inputs(self.theme, out_dir)             # B3出力(台帳・selected_brief.md・evidence)の複製のみ。注記は作らない
        return {}

    def writer_stage(self, client, theme, ja_text, ledger_text, budget_jpy, only=None, **kw):
        self.events.append(only)
        lv = "b1b" if only == "advanced" else "a2"
        os.makedirs(f"{self.out}/{lv}", exist_ok=True)
        with open(f"{self.out}/{lv}/article.md", "w", encoding="utf-8") as f:
            f.write(f"# {only}\n\nSentence one. Sentence two.\n")
        return {}

    def rf(self, out_dir, level, budget_jpy, run_label=None):
        self.events.append("rf:" + level)
        return {"status": "OK", "queue": {"saved": True}}

    def run(self, argv_extra):
        argv = ["runner", "--theme", "T", "--slug", "s", "--out-dir", self.out, *argv_extra]
        orig_prod, orig_val = annot.produce_annotated_b3, contract.validate_annotated_b3

        def spy_prod(out_dir):
            self.events.append("producer")
            return orig_prod(out_dir)

        def spy_val(out_dir):
            self.events.append("contract")
            return orig_val(out_dir)

        patches = [
            mock.patch.object(sys, "argv", argv), mock.patch.object(runner.cl, "install"),
            mock.patch.object(runner.vfl01, "get_client", return_value=self.client),
            mock.patch.object(runner, "run_research_and_ledger", side_effect=self.research),
            mock.patch.object(runner, "run_storyline_b3", side_effect=self.storyline),
            mock.patch.object(runner.efam, "run_writer_stage", side_effect=self.writer_stage),
            mock.patch.object(runner, "run_post_en_risk_flag", side_effect=self.rf),
            mock.patch.object(runner.efam, "assert_budget_ok", return_value=0.0),
            mock.patch.object(runner.vfl01, "run_deviation_check", side_effect=_boom),
            mock.patch.object(w1.time, "sleep", lambda s: None),
            mock.patch.object(annot, "produce_annotated_b3", side_effect=spy_prod),
            mock.patch.object(contract, "validate_annotated_b3", side_effect=spy_val),
        ]
        for p in patches:
            p.start()
        try:
            runner.main()
        finally:
            for p in reversed(patches):
                p.stop()
        return self.events


def seed_prior_run(out, theme="central_bank_mortgage", with_ja=True):
    """前回完了済みrun(B3出力+注記+W-1来歴付きJA記事)を作る。"""
    adapter.build_fixture(theme, out)
    if with_ja:
        d = os.path.join(out, "ja_writer")
        os.makedirs(d)
        with open(os.path.join(d, "revision2.md"), "w", encoding="utf-8") as f:
            f.write("W-1の日本語記事")
        with open(os.path.join(d, "runtime_evidence.json"), "w", encoding="utf-8") as f:
            json.dump({"chain_method": "W-1", "annotated_md_sha256": contract.validate_annotated_b3(out).annotated_md_sha256}, f)


class FourPathOrderTests(unittest.TestCase):
    def setUp(self):
        self.out = tempfile.mkdtemp(prefix="c4_wire_")

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def test_path1_initial_run_producer_then_contract_then_w1(self):
        h = Harness(self.out)
        ev = h.run([])                      # --stage all(既定)、全工程新規
        self.assertEqual(ev[:7], ["research", "storyline", "producer", "contract", "w1:gpt-6.1-sol", "w1:gpt-6.1-sol", "w1:gpt-6.1-sol"])
        self.assertEqual(ev[7:], ["advanced", "rf:b1b", "standard", "rf:a2"])
        # R0のニュース欄は 注記済みFacts + 制約ブロック(producer出力)
        a = contract.validate_annotated_b3(self.out)
        self.assertTrue(a.constraints_text)
        self.assertIn(a.news_field_text, h.client.prompts[0])
        self.assertEqual(a.producer, "deterministic_v2")
        pev = json.load(open(os.path.join(self.out, "storyline_b3", "audit", "annotation_producer_evidence.json"), encoding="utf-8"))
        self.assertEqual((pev["producer"], pev["llm_calls"]), ("deterministic_v2", 0))
        self.assertEqual(pev["rules_sha256"], annot.rules_sha256())
        wev = json.load(open(os.path.join(self.out, "ja_writer", "runtime_evidence.json"), encoding="utf-8"))
        self.assertEqual(wev["annotation_manifest_producer"], "deterministic_v2")

    def test_path2_regeneration_storyline_unchanged_selection_reuses_ja_after_producer_and_contract(self):
        seed_prior_run(self.out)
        h = Harness(self.out)
        ev = h.run(["--regenerate-stage", "storyline_b3"])
        self.assertEqual(ev[:4], ["research", "storyline", "producer", "contract"])       # producer -> U-1/契約(再利用の来歴確認)
        self.assertNotIn("w1:gpt-6.1-sol", ev)                                              # 同一注記shaなのでJA再利用
        self.assertEqual(ev[4:], ["advanced", "rf:b1b", "standard", "rf:a2"])

    def test_path2b_regeneration_with_changed_b3_selection_stops_at_u1_not_reusing_stale_ja(self):
        seed_prior_run(self.out, theme="small_bag")
        h = Harness(self.out, theme="byd_recall")           # 再生成でB3選定が別内容になった想定
        with self.assertRaises(runner.LegacyWriterProvenanceStop) as cm:
            h.run(["--regenerate-stage", "storyline_b3"])
        self.assertIn("PROVENANCE_MISMATCH", str(cm.exception))
        self.assertEqual(h.events[:4], ["research", "storyline", "producer", "contract"])
        self.assertNotIn("advanced", h.events)
        self.assertEqual(json.load(open(os.path.join(self.out, "storyline_b3", "annotation_manifest.json"), encoding="utf-8"))["producer"], "deterministic_v2")

    def test_path3_resume_writer_stage_with_existing_storyline_runs_producer_first(self):
        adapter.copy_inputs("central_bank_mortgage", self.out)      # B3まで完了・注記なし(再開前の状態)
        h = Harness(self.out)
        ev = h.run(["--stage", "writer", "--stop-after", "writer"])
        self.assertEqual(ev[:6], ["research", "producer", "contract", "w1:gpt-6.1-sol", "w1:gpt-6.1-sol", "w1:gpt-6.1-sol"])
        self.assertNotIn("storyline", ev)                             # B3は再実行しない(再開)

    def test_path4_reuse_branch_standard_only_runs_producer_then_u1_contract(self):
        seed_prior_run(self.out)
        for n in ("selected_brief_annotated.md", "annotation.json", "annotation_manifest.json", "writer_constraints.txt"):
            os.remove(os.path.join(self.out, "storyline_b3", n))     # 注記artifactが無い状態から再利用経路に入る
        h = Harness(self.out)
        ev = h.run(["--stage", "standard"])
        self.assertEqual(ev, ["research", "producer", "contract", "standard", "rf:a2"])
        self.assertNotIn("w1:gpt-6.1-sol", ev)                         # JA記事は再利用(Writer再実行なし)

    def test_producer_failure_stops_before_contract_w1_and_api(self):
        adapter.copy_inputs("central_bank_mortgage", self.out)
        p = os.path.join(self.out, "storyline_b3", "fact_selection_evidence.json")
        ev = json.load(open(p, encoding="utf-8"))
        ev["selected_fact_ids"] = ["NO-SUCH-ID"]
        json.dump(ev, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        h = Harness(self.out)
        with self.assertRaises(annot.AnnotationProducerError):
            h.run(["--stage", "writer"])
        self.assertEqual(h.events, ["research", "producer"])           # 契約・W-1・API・英訳・RFへ進まない(課金前STOP)
        self.assertEqual(h.client.n, 0)

    def test_producer_failure_after_regeneration_leaves_no_stale_annotation(self):
        seed_prior_run(self.out, with_ja=False)
        h = Harness(self.out)
        h.storyline = lambda *a, **k: (_ for _ in ()).throw(AssertionError("unused"))
        p = os.path.join(self.out, "storyline_b3", "fact_selection_evidence.json")
        ev = json.load(open(p, encoding="utf-8"))
        ev["selected_fact_ids"] = []
        json.dump(ev, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        with self.assertRaises(annot.AnnotationProducerError):
            h.run(["--stage", "writer"])
        self.assertFalse(os.path.exists(os.path.join(self.out, "storyline_b3", "selected_brief_annotated.md")))


class NoFallbackAstTests(unittest.TestCase):
    def setUp(self):
        self.tree = ast.parse(open(RUNNER_PY, encoding="utf-8").read())
        self.funcs = {n.name: n for n in self.tree.body if isinstance(n, ast.FunctionDef)}

    def _calls(self, fn):
        out = []
        for n in ast.walk(fn):
            if isinstance(n, ast.Call):
                f = n.func
                out.append((f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", ""), n.lineno))
        return out

    def test_main_calls_producer_before_writer_in_every_writer_path(self):
        calls = self._calls(self.funcs["main"])
        prod_lines = [ln for nm, ln in calls if nm == "run_annotation_producer"]
        writer_lines = [ln for nm, ln in calls if nm in ("run_ja_writer", "load_reused_ja_text")]
        self.assertEqual(len(prod_lines), 1)                                   # 分岐ごとに散在させず、storyline確定直後の1箇所
        self.assertTrue(writer_lines)
        self.assertLess(prod_lines[0], min(writer_lines))
        # producer呼出は storyline_b3 の if/else の後・--stop-after の前(全分岐を通る位置)
        src = open(RUNNER_PY, encoding="utf-8").read().split("\n")
        i = next(k for k, ln in enumerate(src, 1) if "run_annotation_producer(out_dir)" in ln and "def " not in ln)
        self.assertIn("storyline_b3", "\n".join(src[i:i + 4]))                  # 直後が stage==storyline_b3 の早期return判定

    def test_writer_is_only_reached_through_contract_validation_and_never_with_plain_b3(self):
        # run_ja_writer は w1.run_w1_writer のみを呼ぶ(W-1入口が validate_annotated_b3)。fact_selection_evidence/selected_brief.md を直接Writerへ渡さない
        names = [nm for nm, _ in self._calls(self.funcs["run_ja_writer"])]
        self.assertIn("run_w1_writer", names)
        src = open(RUNNER_PY, encoding="utf-8").read()
        for tok in ("selected_fact_brief_text\"]", "build_original_prompt", "run_ja_writer_o_r1_r2", "selected_brief_annotated.md"):
            self.assertNotIn(tok, "\n".join(ln for ln in src.split("\n") if "run_storyline_b3" not in ln and not ln.lstrip().startswith(("#", '"', "'"))
                                            and '"selected_fact_brief_text":' not in ln), tok)

    def test_no_switch_cli_or_env_for_annotation(self):
        opts = []
        for n in ast.walk(self.funcs["build_arg_parser"]):
            if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "add_argument":
                opts.append(n.args[0].value)
        self.assertEqual(sorted(opts), ["--budget-jpy", "--out-dir", "--regenerate-stage", "--run-label", "--slug", "--source-note",
                                        "--stage", "--stop-after", "--theme"])
        src = open(RUNNER_PY, encoding="utf-8").read()
        self.assertNotIn("os.environ", src)
        self.assertNotIn("getenv", src)
        pr = open(os.path.join(HERE, "er053_b3_deterministic_producer_01.py"), encoding="utf-8").read()
        for tok in ("os.environ", "getenv", "ArgumentParser", "sys.argv"):
            self.assertNotIn(tok, pr)

    def test_producer_function_has_no_conditional_skip_or_fallback(self):
        fn = self.funcs["run_annotation_producer"]
        self.assertEqual([n for n in ast.walk(fn) if isinstance(n, (ast.If, ast.Try, ast.IfExp))], [])      # 条件分岐・例外握りつぶしなし
        self.assertEqual([nm for nm, _ in self._calls(fn) if nm == "produce_annotated_b3"], ["produce_annotated_b3"])

    def test_no_trial_fixture_or_plain_b3_literal_in_production_modules(self):
        for f in ("er019_family_x_entertainment_production_runner_01.py", "er053_b3_annotation_contract_01.py",
                  "er053_family_x_factlock_ja_writer_01.py", "er053_b3_deterministic_producer_01.py"):
            src = open(os.path.join(HERE, f), encoding="utf-8").read()
            code = "\n".join(ln for ln in src.split("\n") if not ln.lstrip().startswith("#"))
            self.assertNotIn("er053_dev_b3_fixture_adapter", code, f)
            self.assertNotIn('"trial_fixture"', code, f)


if __name__ == "__main__":
    unittest.main()
