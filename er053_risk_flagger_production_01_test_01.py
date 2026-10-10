# -*- coding: utf-8 -*-
"""er053_risk_flagger_production_01 のtest(API呼び出し0、費用¥0。API部はstub)。
実行: .venv/Scripts/python.exe -m pytest er053_risk_flagger_production_01_test_01.py -q
"""
from __future__ import annotations

import ast
import glob
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er053_risk_flagger_production_01 as rf

HERE = os.path.dirname(os.path.abspath(__file__))
ANT = os.path.join(HERE, "er052_output", "writer_dev_risk_flagger_01", "antenna_trial_01")
DET = os.path.join(HERE, "er052_output", "writer_dev_risk_flagger_01", "detectors")

LEDGER = (
    "[VERIFIED] F-001: The company paused the feature.\n"
    "  source: example\n"
    "\n"
    "[AMBIGUOUS - exact date unclear] F-002: A rollout may have started in May.\n"
    "\n"
    "[VERIFIED] F-003: Prices rose 20 percent.\n"
)
ARTICLE = "# Title Line\n\nThe company paused the feature. Prices rose 30 percent.\nU.S. officials said it was fine."


def _tmp():
    d = tempfile.mkdtemp(prefix="rf_test_")
    return d


def _files(d, article=ARTICLE, ledger=LEDGER):
    a = os.path.join(d, "article.md")
    l = os.path.join(d, "ledger.txt")
    open(a, "w", encoding="utf-8", newline="").write(article)
    open(l, "w", encoding="utf-8", newline="").write(ledger)
    return a, l


def _ok_text(flags):
    return json.dumps({"flags": flags}, ensure_ascii=False)


def flag(sid, conf=0.5, fids=("F-003",), typ="数量時系列"):
    return {"sentence_id": sid, "type": typ, "fact_ids": list(fids), "confidence": conf, "severity": "重大",
            "question": "台帳と食い違うのではありませんか"}


class Stub:
    """call_fn stub。scripts: {(model_key, condition): [response, ...]}、responseは (text) または Exception。"""

    def __init__(self, scripts=None, default=None, returned=None):
        self.scripts = {k: list(v) for k, v in (scripts or {}).items()}
        self.default = default if default is not None else _ok_text([])
        self.calls = []
        self.returned = returned or {}

    def __call__(self, model_key, model_id, system, user):
        cond = "A3" if system == rf.A3_SYSTEM else "A4"
        self.calls.append((model_key, cond, model_id))
        q = self.scripts.get((model_key, cond))
        item = q.pop(0) if q else self.default
        if isinstance(item, Exception):
            raise item
        usage = {"input_tokens": 1000, "output_tokens": 200, "reasoning_tokens": 50, "cached_tokens": 0}
        rid = f"resp_{model_key}_{cond}_{len(self.calls)}"
        return item, usage, rid, self.returned.get(model_key, rf.MODEL_SPECS[model_key]["model_id"])


class PromptShaTests(unittest.TestCase):
    def test_sha_fixed(self):
        self.assertEqual(rf.sha256_text(rf.A3_SYSTEM), "9d9950428419c3af824cc5b8676a4b564f96aeb87657c547d418cc86ef3538e9")
        self.assertEqual(rf.sha256_text(rf.A4_SYSTEM), "c87b95e5bcf1b5c266b8978c5688849eb339a6087efbcaf56bb7399ed128ef01")

    def test_byte_identical_to_trial_antenna_prompts(self):
        sys.path.insert(0, ANT)
        sys.path.insert(0, DET)
        try:
            import antenna_prompts as A
            self.assertEqual(rf.A3_SYSTEM, A.antenna_system(3))
            self.assertEqual(rf.A4_SYSTEM, A.antenna_system(4))
        finally:
            sys.path.remove(ANT)
            sys.path.remove(DET)


class LedgerTests(unittest.TestCase):
    def test_fix01_ambiguous_header(self):
        facts = rf.parse_ledger_complete(LEDGER)
        self.assertEqual([f["fact_id"] for f in facts], ["F-001", "F-002", "F-003"])
        self.assertIn("source: example", facts[0]["text"])
        self.assertEqual(facts[1]["text"], "A rollout may have started in May.")

    def test_incomplete_header_detected(self):
        bad = LEDGER + "[weird line without id]\n"
        with self.assertRaises(rf.LedgerIncomplete) as cm:
            rf.parse_ledger_complete(bad)
        self.assertEqual((cm.exception.n_broad, cm.exception.n_hdr, cm.exception.n_parsed), (4, 3, 3))
        self.assertTrue(cm.exception.examples)

    def test_empty_ledger_incomplete(self):
        with self.assertRaises(rf.LedgerIncomplete):
            rf.parse_ledger_complete("no headers here\n")

    def test_deterministic(self):
        self.assertEqual(rf.parse_ledger_text(LEDGER), rf.parse_ledger_text(LEDGER))

    def test_equal_to_trial_parser(self):
        sys.path.insert(0, DET)
        try:
            import ledger_restore_01 as LR
            old = LR._HDR
            LR._HDR = rf.LEDGER_HDR_RE
            try:
                self.assertEqual(LR.parse_ledger_text(LEDGER), rf.parse_ledger_text(LEDGER))
            finally:
                LR._HDR = old
        finally:
            sys.path.remove(DET)


class InputAndValidateTests(unittest.TestCase):
    def test_build_user_equals_trial(self):
        sys.path.insert(0, DET)
        try:
            import prompts_flagger as P
            unit = rf.build_units(ARTICLE, rf.parse_ledger_complete(LEDGER))
            self.assertEqual(rf.build_user(unit), P.build_user(unit))
        finally:
            sys.path.remove(DET)

    def test_sentences_use_production_splitter_and_no_context_in_llm_input(self):
        unit = rf.build_units(ARTICLE, rf.parse_ledger_complete(LEDGER))
        texts = [s["text"] for s in unit["sentences"]]
        self.assertIn("U.S. officials said it was fine.", texts)
        self.assertEqual(texts[0], "# Title Line")
        for s in unit["sentences"]:
            self.assertEqual((s["before"], s["after"]), ("", ""))

    def test_validate_flags_matches_trial(self):
        sys.path.insert(0, DET)
        try:
            import run_flagger_01 as R
            unit = rf.build_units(ARTICLE, rf.parse_ledger_complete(LEDGER))
            unit["unit_id"] = "t"      # Trial版のみ参照するキー
            cases = [_ok_text([flag("s3")]), _ok_text([]), "garbage", _ok_text([flag("s99")]),
                     _ok_text([dict(flag("s3"), confidence=1.5)]), _ok_text([dict(flag("s3"), type="x")]),
                     _ok_text([dict(flag("s3"), fact_ids=["NOPE"])]), "prefix " + _ok_text([flag("s3")]),
                     json.dumps({"nope": 1}), _ok_text([dict(flag("s3"), question=" ")])]
            for c in cases:
                a, va = rf.validate_flags(c, unit)
                b, vb = R.validate_flags(c, unit)
                self.assertEqual(a is None, b is None, c)
                if a is not None:
                    self.assertEqual([x["sentence_id"] for x in a], [x["sentence_id"] for x in b])
                else:
                    self.assertEqual(va, vb, c)
        finally:
            sys.path.remove(DET)


class RunTests(unittest.TestCase):
    def setUp(self):
        self.d = _tmp()
        self.a, self.l = _files(self.d)
        self.out = os.path.join(self.d, "out")
        os.makedirs(self.out)
        self.sleeps = []

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def run_rf(self, stub, **kw):
        return rf.run_risk_flagger(article_path=self.a, ledger_path=self.l, article_id="art1", article_level="b1b",
                                   out_dir=self.out, call_fn=stub, sleep_fn=self.sleeps.append, **kw)

    def test_four_conditions_sequential_order_and_ok(self):
        st = Stub()
        r = self.run_rf(st)
        self.assertEqual(r["status"], "OK")
        self.assertEqual([(m, c) for m, c, _ in st.calls], list(rf.CONDITIONS))
        self.assertEqual([c["status"] for c in r["conditions"]], ["OK"] * 4)
        self.assertEqual({m: mid for m, _, mid in st.calls}, {"luna": "gpt-6-luna", "gemini35fl": "gemini-3.5-flash-lite"})

    def test_or_merge_and_dedupe(self):
        st = Stub({("luna", "A3"): [_ok_text([flag("s3", 0.4)])], ("luna", "A4"): [_ok_text([flag("s3", 0.7), flag("s4", 0.2, ())])],
                   ("gemini35fl", "A3"): [_ok_text([flag("s3", 0.3)])], ("gemini35fl", "A4"): [_ok_text([])]})
        r = self.run_rf(st)
        self.assertEqual([i["sentence_id"] for i in r["issues"]], ["s3", "s4"])
        s3 = r["issues"][0]
        self.assertEqual(len(s3["detected_by"]), 3)
        self.assertEqual({(d["model_key"], d["condition"]) for d in s3["detected_by"]},
                         {("luna", "A3"), ("luna", "A4"), ("gemini35fl", "A3")})
        self.assertEqual(s3["confidence"], 0.7)
        self.assertEqual(s3["article_level"], "b1b")
        self.assertEqual(len(r["raw"]), 4)       # rawを保持
        ms = r["model_stats"]
        self.assertEqual(ms["luna"]["a3_flag_count"], 1)
        self.assertEqual(ms["luna"]["a4_flag_count"], 2)
        self.assertEqual(ms["luna"]["unique_issue"], 2)
        self.assertEqual(ms["luna"]["overlap_a3_a4"], 1)
        self.assertEqual(ms["gemini35fl"]["zero_flag_article"], 0)
        self.assertEqual(ms["gemini35fl"]["unique_issue"], 1)

    def test_zero_flag_stats(self):
        r = self.run_rf(Stub())
        self.assertEqual(r["model_stats"]["luna"]["zero_flag_article"], 1)
        self.assertEqual(r["model_stats"]["gemini35fl"]["zero_flag_article"], 1)
        self.assertEqual(r["issues"], [])

    def test_transient_retry_two_then_ok(self):
        e = RuntimeError("boom")
        st = Stub({("luna", "A3"): [e, e, _ok_text([])]})
        r = self.run_rf(st)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(sum(1 for m, c, _ in st.calls if (m, c) == ("luna", "A3")), 3)
        self.assertEqual(self.sleeps[:2], [2, 4])

    def test_transient_exhausted_is_partial_not_exception(self):
        e = RuntimeError("boom")
        st = Stub({("luna", "A3"): [e, e, e]})
        r = self.run_rf(st)
        self.assertEqual(r["status"], "PARTIAL")
        self.assertEqual(r["conditions"][0]["status"], "RF_UNAVAILABLE")
        self.assertIn("transient_exhausted", r["conditions"][0]["reason"])
        self.assertEqual(sum(1 for m, c, _ in st.calls if (m, c) == ("luna", "A3")), 3)
        self.assertEqual(r["model_stats"]["luna"]["article_partial"], 1)

    def test_format_retry_once(self):
        st = Stub({("gemini35fl", "A4"): ["not json", _ok_text([])]})
        r = self.run_rf(st)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(sum(1 for m, c, _ in st.calls if (m, c) == ("gemini35fl", "A4")), 2)

    def test_format_fail_twice_unavailable(self):
        st = Stub({("gemini35fl", "A4"): ["bad", "bad"]})
        r = self.run_rf(st)
        self.assertEqual(r["status"], "PARTIAL")
        self.assertEqual(sum(1 for m, c, _ in st.calls if (m, c) == ("gemini35fl", "A4")), 2)   # 上限を増やさない

    def test_all_unavailable_and_visibility(self):
        e = RuntimeError("down")
        st = Stub(default=e)
        r = self.run_rf(st)
        self.assertEqual(r["status"], "RF_UNAVAILABLE")
        ep = json.load(open(os.path.join(self.out, "entry_point.json"), encoding="utf-8"))
        self.assertEqual(ep["risk_flagger"]["b1b"]["status"], "RF_UNAVAILABLE")
        self.assertEqual(len(ep["risk_flagger"]["b1b"]["conditions"]), 4)

    def test_entry_point_preserves_existing_keys(self):
        json.dump({"keep": 1}, open(os.path.join(self.out, "entry_point.json"), "w"))
        self.run_rf(Stub())
        ep = json.load(open(os.path.join(self.out, "entry_point.json"), encoding="utf-8"))
        self.assertEqual(ep["keep"], 1)
        self.assertEqual(ep["risk_flagger"]["b1b"]["status"], "OK")

    def test_ledger_incomplete_no_api(self):
        open(self.l, "w", encoding="utf-8").write(LEDGER + "[broken]\n")
        st = Stub()
        r = self.run_rf(st)
        self.assertEqual(r["status"], "RF_UNAVAILABLE")
        self.assertEqual(r["reason"], "ledger_incomplete")
        self.assertEqual(st.calls, [])
        self.assertEqual(r["ledger_incomplete_detail"]["n_broad"], 4)

    def test_article_sha_invariant_and_violation(self):
        st = Stub()
        r = self.run_rf(st)
        self.assertEqual(r["article_sha256"], hashlib.sha256(ARTICLE.encode("utf-8")).hexdigest())
        self.assertEqual(open(self.a, encoding="utf-8").read(), ARTICLE)

        def evil(mk, mid, system, user):
            open(self.a, "a", encoding="utf-8").write("x")
            return Stub()(mk, mid, system, user)
        with self.assertRaises(rf.ArticleModifiedError):
            self.run_rf(evil)

    def test_budget_check_exception_propagates(self):
        def bc():
            raise RuntimeError("[STOP] budget")
        st = Stub()
        with self.assertRaises(rf.BudgetCheckStop):
            self.run_rf(st, budget_check=bc)
        self.assertEqual(st.calls, [])

    def test_dry_run_no_calls(self):
        st = Stub()
        r = self.run_rf(st, dry_run=True)
        self.assertEqual(r["status"], "DRY_RUN")
        self.assertEqual(st.calls, [])
        self.assertEqual(set(r["requests"]), {"luna.A3", "luna.A4", "gemini35fl.A3", "gemini35fl.A4"})
        self.assertFalse(os.path.exists(os.path.join(self.out, "entry_point.json")))

    def test_model_mismatch_recorded_not_stopped(self):
        st = Stub(returned={"luna": "gpt-6.1-sol-2026"})
        r = self.run_rf(st)
        self.assertEqual(r["status"], "OK")
        self.assertTrue(any(c["model_mismatch"] for c in r["conditions"] if c["model_key"] == "luna"))
        self.assertTrue(any("model_id_mismatch" in w for w in r["warnings"]))

    def test_non_blocking_no_rewrite_or_branch_on_flags(self):
        # 全文にFlagが立っても、RFは記事を変えず、追加retry/再生成をしない(条件ごと1回のみ)
        st = Stub(default=_ok_text([flag("s3"), flag("s4")]))
        r = self.run_rf(st)
        self.assertEqual(len(st.calls), 4)
        self.assertEqual(r["status"], "OK")


class CostAndLoggerTests(unittest.TestCase):
    def setUp(self):
        self.d = _tmp()
        self.a, self.l = _files(self.d)
        self.records = []
        self.stages = []

        def fake_record(entry):
            self.records.append(dict(entry))
            self.stages.append(cl._CONTEXT["stage"])
        self.p = mock.patch.object(cl, "record", side_effect=fake_record)
        self.p.start()

    def tearDown(self):
        self.p.stop()
        shutil.rmtree(self.d, ignore_errors=True)

    def _run(self, stub, **kw):
        return rf.run_risk_flagger(article_path=self.a, ledger_path=self.l, article_id="art1", article_level="a2",
                                   call_fn=stub, sleep_fn=lambda s: None, **kw)

    def test_gemini_recorded_luna_not_double_recorded(self):
        r = self._run(Stub())
        self.assertEqual(r["status"], "OK")
        models = [x["model_id"] for x in self.records]
        self.assertEqual(models, ["gemini-3.5-flash-lite", "gemini-3.5-flash-lite"])   # Gemini 2件のみ。Lunaは手動記録しない
        self.assertTrue(all(x["provider"] == "gemini" for x in self.records))
        self.assertEqual(self.stages, ["risk_flag.gemini35fl.A3.a2", "risk_flag.gemini35fl.A4.a2"])
        self.assertIsNone(cl._CONTEXT["stage"])    # contextが外へ漏れない

    def test_failed_gemini_call_recorded_as_failure(self):
        e = RuntimeError("x")
        r = self._run(Stub({("gemini35fl", "A3"): [e, e, e]}))
        fails = [x for x in self.records if x["success"] is False]
        self.assertEqual(len(fails), 3)
        self.assertEqual(r["status"], "PARTIAL")

    def test_gemini_output_tokens_include_thinking(self):
        j = {"candidates": [{"content": {"parts": [{"text": "t", "thought": True}, {"text": '{"flags":[]}'}]}, "finishReason": "STOP"}],
             "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 4, "thoughtsTokenCount": 6, "cachedContentTokenCount": 2},
             "responseId": "r1", "modelVersion": "gemini-3.5-flash-lite"}
        text, usage, rid, mid = rf.parse_gemini_response(j)
        self.assertEqual(text, '{"flags":[]}')
        self.assertEqual(usage["output_tokens"], 10)
        self.assertEqual((usage["input_tokens"], usage["cached_tokens"], rid, mid), (10, 2, "r1", "gemini-3.5-flash-lite"))

    def test_cost_formula_and_stage_record_tokens(self):
        r = self._run(Stub())
        g = [c for c in r["conditions"] if c["model_key"] == "gemini35fl"][0]
        # 1000 in * 0.30 + 200 out * 2.50 per 1M = 0.0008 USD -> *160 = 0.128 JPY
        self.assertAlmostEqual(g["cost_jpy"], (1000 * 0.30 + 200 * 2.50) / 1e6 * 160.0, places=6)
        self.assertEqual(self.records[0]["output_tokens"], 200)
        self.assertEqual(self.records[0]["input_tokens"], 1000)

    def test_inside_logging_context_warns_not_stops(self):
        with cl.logging_context("OUTER", "outer_stage"):
            r = self._run(Stub())
        self.assertEqual(r["status"], "OK")
        self.assertTrue(any("called_inside_logging_context" in w for w in r["warnings"]))

    def test_pricing_gate_before_first_call_gemini_missing(self):
        snap = json.load(open(rf.PRICING_SNAPSHOT_PATH, encoding="utf-8"))
        snap["prices"] = [p for p in snap["prices"] if p["model"] != "gemini-3.5-flash-lite"]
        pp = os.path.join(self.d, "snap.json")
        json.dump(snap, open(pp, "w", encoding="utf-8"))
        st = Stub()
        r = self._run(st, pricing_path=pp)
        self.assertEqual(r["status"], "RF_UNAVAILABLE")
        self.assertEqual(r["reason"], "pricing_not_found")
        self.assertEqual(st.calls, [])               # Luna含め1回も呼ばない(G-1がRF初回呼出より先)

    def test_shipped_snapshot_has_gemini_prices_with_source(self):
        pr = rf.load_prices("gemini-3.5-flash-lite", "gemini")
        self.assertEqual((pr["input_tokens"], pr["cached_input_tokens"], pr["output_tokens"]), (0.30, 0.03, 2.50))
        snap = json.load(open(rf.PRICING_SNAPSHOT_PATH, encoding="utf-8"))
        ents = [p for p in snap["prices"] if p["model"] == "gemini-3.5-flash-lite"]
        self.assertEqual(len(ents), 3)
        for e in ents:
            self.assertIn("ai.google.dev/gemini-api/docs/pricing", e["source_url"])
            self.assertIn("2026-10-10", e["source_url"])

    def test_shipped_values_match_xm_prices_source(self):
        xm = json.load(open(os.path.join(HERE, "er052_output", "writer_dev_risk_flagger_01", "meta_rollback_crossmodel_01",
                                         "xm_prices_01.json"), encoding="utf-8"))["prices"]["gemini-3.5-flash-lite"]
        pr = rf.load_prices("gemini-3.5-flash-lite", "gemini")
        self.assertEqual((pr["input_tokens"], pr["cached_input_tokens"], pr["output_tokens"]), (xm["in"], xm["cached"], xm["out"]))

    def test_luna_priced(self):
        pr = rf.load_prices("gpt-6-luna", "openai")
        self.assertEqual((pr["input_tokens"], pr["output_tokens"]), (0.1, 0.5))

    def test_usd_jpy_matches_efam(self):
        import er012_e_family_entertainment_two_level_runner_01 as efam
        self.assertEqual(rf.USD_JPY, efam.USD_JPY)

    def test_efam_cost_function_prices_gemini_records(self):
        """既存のproduction予算ガード(efam.compute_cost_jpy_so_far)が、本moduleの書くGeminiレコードを単価付きで計上できる。"""
        import er012_e_family_entertainment_two_level_runner_01 as efam
        lp = os.path.join(self.d, "raw_usage_log.jsonl")
        open(lp, "w", encoding="utf-8").write(json.dumps(
            {"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "input_tokens": 1000, "output_tokens": 200}) + "\n")
        jpy, by = efam.compute_cost_jpy_so_far(lp)
        self.assertGreater(jpy, 0)


class RoutingTests(unittest.TestCase):
    def test_routing_keys_literal(self):
        m = routing.PROCESS_MODEL_MAP
        self.assertEqual(m["FAMILY_X_RF_LUNA"], "gpt-6-luna")
        self.assertEqual(m["FAMILY_X_RF_GEMINI"], "gemini-3.5-flash-lite")
        self.assertEqual(m["FAMILY_X_FACTLOCK_R0"], "gpt-6-luna")
        self.assertEqual(m["FAMILY_X_FACTLOCK_REVISE"], "gpt-6-astra")

    def test_existing_keys_unchanged(self):
        m = routing.PROCESS_MODEL_MAP
        for k in ("B1_WRITER", "A2_WRITER", "WRITER_FACT_CHECK", "KEY_PHRASE_ADVANCED_EXPLANATION", "NATURAL_ENGLISH_ADAPTATION"):
            self.assertEqual(m[k], "gpt-6-luna")
        self.assertEqual(m["FAMILY_X_FLASH_LITE_TTS"], "gemini-3.8-flash-lite-tts")

    def test_routing_drift_makes_rf_unavailable_without_api_call(self):
        d = _tmp()
        try:
            a, l = _files(d)
            st = Stub()
            with mock.patch.dict(routing.PROCESS_MODEL_MAP, {"FAMILY_X_RF_GEMINI": "gemini-9-other"}):
                r = rf.run_risk_flagger(article_path=a, ledger_path=l, article_id="x", article_level="b1b",
                                        call_fn=st, sleep_fn=lambda s: None)
            self.assertEqual(r["status"], "RF_UNAVAILABLE")
            self.assertEqual(r["reason"], "model_contract_violation")
            self.assertEqual(st.calls, [])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_request_bodies(self):
        _, _, b = rf.build_request("luna", "gpt-6-luna", "SYS", "USR")
        self.assertEqual(b, {"model": "gpt-6-luna", "instructions": "SYS", "input": "USR",
                             "reasoning": {"effort": "medium"}, "max_output_tokens": 8000})
        ep, _, g = rf.build_request("gemini35fl", "gemini-3.5-flash-lite", "SYS", "USR")
        self.assertTrue(ep.endswith("models/gemini-3.5-flash-lite:generateContent"))
        self.assertEqual(g, {"systemInstruction": {"parts": [{"text": "SYS"}]},
                             "contents": [{"role": "user", "parts": [{"text": "USR"}]}],
                             "generationConfig": {"maxOutputTokens": 8000}})


class StaticTests(unittest.TestCase):
    def test_no_trial_imports(self):
        src = open(os.path.join(HERE, "er053_risk_flagger_production_01.py"), encoding="utf-8").read()
        mods = set()
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module)
        for m in mods:
            self.assertFalse(m.startswith(("er050", "er051", "er052")), m)

    def test_no_env_switch_for_rf_behavior(self):
        """os.environ / os.getenv の読み取りは、APIキー取得(_key: 変数名経由)以外に存在しない(隠れswitch禁止)。"""
        src = open(os.path.join(HERE, "er053_risk_flagger_production_01.py"), encoding="utf-8").read()
        tree = ast.parse(src)
        literal_env = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                chain = ast.unparse(n.func)
                if chain in ("os.environ.get", "os.getenv", "os.environ.setdefault") and n.args:
                    a0 = n.args[0]
                    if isinstance(a0, ast.Constant):
                        literal_env.append(a0.value)
            if isinstance(n, ast.Subscript) and ast.unparse(n.value) == "os.environ":
                literal_env.append(ast.unparse(n.slice))
        self.assertEqual(literal_env, [])
        self.assertNotIn("OPEN243", src)
        self.assertNotIn("OPEN233", src)

    def test_aggregate_model_stats(self):
        s1 = {"luna": {"article_level": "a2", "a3_flag_count": 2, "cost_jpy": 1.0}, "_all": {}}
        s2 = {"luna": {"article_level": "a2", "a3_flag_count": 1, "cost_jpy": 0.5}, "_all": {}}
        agg = rf.aggregate_model_stats([("a2", s1), ("a2", s2), ("b1b", s1)])
        self.assertEqual(agg["a2"]["luna"]["a3_flag_count"], 3)
        self.assertEqual(agg["b1b"]["luna"]["a3_flag_count"], 2)


class LedgerScanTests(unittest.TestCase):
    """既存 er019_output 配下の verified_fact_ledger.txt 全件を¥0で走査(完全性assertが決定論的にUNAVAILABLEにならないことの確認)。
    FAILは件数と見出し例を evidence JSON に保存して報告する(parserの修正はしない)。"""

    def test_scan_all_existing_ledgers(self):
        files = sorted(glob.glob(os.path.join(HERE, "er019_output", "**", "verified_fact_ledger.txt"), recursive=True))
        self.assertGreater(len(files), 0)
        results = []
        for f in files:
            txt = open(f, encoding="utf-8").read()
            try:
                facts1 = rf.parse_ledger_complete(txt)
                facts2 = rf.parse_ledger_complete(txt)
                self.assertEqual(facts1, facts2)           # 決定論
                results.append({"path": os.path.relpath(f, HERE).replace("\\", "/"), "result": "PASS", "n_facts": len(facts1)})
            except rf.LedgerIncomplete as e:
                results.append({"path": os.path.relpath(f, HERE).replace("\\", "/"), "result": "FAIL", "n_broad": e.n_broad,
                                "n_hdr": e.n_hdr, "n_parsed": e.n_parsed, "examples": e.examples})
        out_dir = os.path.join(HERE, "er053_output", "risk_flagger_production_wiring_01")
        os.makedirs(out_dir, exist_ok=True)
        summary = {"scanned": len(results), "pass": sum(1 for r in results if r["result"] == "PASS"),
                   "fail": sum(1 for r in results if r["result"] == "FAIL"), "results": results}
        json.dump(summary, open(os.path.join(out_dir, "ledger_scan_er019_output.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print("LEDGER_SCAN", {k: summary[k] for k in ("scanned", "pass", "fail")})


if __name__ == "__main__":
    unittest.main()
