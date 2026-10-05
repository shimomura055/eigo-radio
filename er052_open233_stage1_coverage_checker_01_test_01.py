# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_stage1_coverage_checker_01_test_01.py
# OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_06。ネットワーク呼び出しなし(¥0、偽LLM/mockのみ)。
# ============================================================
from __future__ import annotations

import unittest
from unittest import mock

import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as cov

ZERO = {k: False for k in cov.FLAG_KEYS}
LEDGER = """[VERIFIED] HF-001: 20％の償還料が7月13日に提案された。
  scope: ホルムズ海峡
  notes_for_writer: この提案と撤回の因果関係は一次資料で確認できない。

[VERIFIED] HF-002: 徴収方法は示されなかった。
  scope: 償還料案

[VERIFIED] HF-003: 米国は7月14日に案を撤回し、貿易投資案へ置き換えると述べた。
  causal_strength: 因果の結果として撤回された(情報源が明示)。
"""
ARTICLE = """# Title Here

The plan was posted on July 13. It said 20% would be charged.

The post did not say how to collect it. So the plan left the stage.

## In one line

The plan was posted on July 13. So the plan left the stage.
"""


def _split(text=ARTICLE):
    return cov.split_units(text, runner.vs_sentence_segments_l6, runner.CAUSAL_SENTENCE_INITIAL_EN)


def _item(uid, verdict="SUPPORTED", ids=("HF-001",), quotes=("20％の償還料が7月13日に提案された",), issue="", claim="",
          related="", flags=None):
    return {"unit_id": uid, "verdict": verdict, "support_fact_ids": list(ids), "ledger_quotes": list(quotes),
            "issue": issue, "claim_in_article": claim, "related_fact_id": related, "flags": flags or dict(ZERO)}


def _check_strict(test, schema, path="$"):
    """strict json_schema要件: object=additionalProperties False かつ required==properties全キー。"""
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            test.assertIs(schema.get("additionalProperties"), False, path)
            test.assertEqual(sorted(schema.get("required", [])), sorted(schema["properties"].keys()), path)
            for k, v in schema["properties"].items():
                _check_strict(test, v, f"{path}.{k}")
        if schema.get("type") == "array":
            _check_strict(test, schema["items"], path + "[]")


class TestSplitUnits(unittest.TestCase):
    def test_ids_roles_and_verbatim_offsets(self):
        sp = _split()
        by = {u["id"]: u for u in sp["units"]}
        self.assertEqual(by["T"]["text"], "# Title Here")
        self.assertEqual(by["S1.1"]["role"], "hook")
        self.assertEqual(by["S2.1"]["role"], "body")
        self.assertEqual(by["L1"]["role"], "oneline")
        self.assertFalse(by["P1"]["judged"])
        for u in sp["units"]:
            if u["type"] != "relation":
                self.assertEqual(ARTICLE[u["start"]:u["end"]], u["text"])
        self.assertNotIn("P1", sp["judged_ids"])

    def test_relation_units_for_causal_initial_sentences(self):
        sp = _split()
        self.assertEqual(sp["relation_ids"], ["R:S2.1+S2.2", "R:L1+L2"])
        r = {u["id"]: u for u in sp["units"]}["R:L1+L2"]
        self.assertEqual(r["claim_text"], "So the plan left the stage.")
        self.assertTrue(r["text"].startswith("The plan was posted on July 13."))

    def test_relation_regex_variants(self):
        rx = cov.build_relation_initial_re(runner.CAUSAL_SENTENCE_INITIAL_EN)
        for s in ("So it ended.", "This is why it ended.", "That is why x.", "As a result, x.", "Therefore x.",
                  "“So x.”", "Following the news, x."):
            self.assertTrue(rx.search(s), s)
        for s in ("Some people left.", "Soon after, x.", "But it ended.", "The reason is x."):
            self.assertFalse(rx.search(s), s)

    def test_same_sentence_groups(self):
        sp = _split()
        self.assertIn(["S1.1", "L1"], sp["same_sentence_groups"])

    def test_single_paragraph_short_article(self):
        sp = _split("Researchers studied 30 million payments. They found more tips.")
        self.assertEqual([u["id"] for u in sp["units"] if u["type"] == "sentence"], ["S1.1", "S1.2"])
        self.assertEqual(sp["relation_ids"], [])


class TestLedgerAndSchema(unittest.TestCase):
    def test_fact_blocks_v1_and_v2(self):
        b = cov.ledger_fact_blocks(LEDGER)
        self.assertEqual(sorted(b), ["HF-001", "HF-002", "HF-003"])
        self.assertIn("scope: ホルムズ海峡", b["HF-001"])
        v2 = cov.ledger_fact_blocks("=== Source ===\n\n[SRC-001] x\n\n[F-001] 本文A\n  scope: s\n\n[F-002] 本文B")
        self.assertEqual(sorted(v2), ["F-001", "F-002"])

    def test_schemas_are_strict_and_flags_are_existing_10(self):
        _check_strict(self, cov.R3_JSON_SCHEMA["schema"])
        _check_strict(self, cov.R5_JSON_SCHEMA["schema"])
        self.assertEqual(len(cov.FLAG_KEYS), 10)
        self.assertEqual(cov.FLAG_KEYS, runner.vfl01.DEVIATION_FLAG_KEYS)
        self.assertNotIn("severity", cov.R3_JSON_SCHEMA["schema"]["properties"]["unit_verdicts"]["items"]["properties"])

    def test_prompts_have_required_policy_text_and_sha256_recorded(self):
        for w in ("迷えば候補", "逐語引用", "一字一句", "重大度", "省略"):
            self.assertIn(w, cov.R3_PROMPT_TEMPLATE)
        self.assertEqual(cov.PROMPT_SHA256["R3_PROMPT_TEMPLATE"], cov.sha256_text(cov.R3_PROMPT_TEMPLATE))
        p = cov.build_r3_prompt(LEDGER, _split()["units"], ["S1.1"], rerun=True)
        self.assertIn("[S1.1]", p)
        self.assertIn("再実行", p)
        self.assertIn("[R:L1+L2]", p)

    def test_existing_v0_v4a_prompt_constants_untouched(self):
        self.assertNotIn("CANDIDATE", runner.vfl01.DEVIATION_PROMPT_TEMPLATE)
        self.assertNotIn("CANDIDATE", runner.trial.build_trial_prompt_template("V4A"))


class TestDeterministicChecks(unittest.TestCase):
    def setUp(self):
        self.sp = _split()
        self.by = {u["id"]: u for u in self.sp["units"]}
        self.blocks = cov.ledger_fact_blocks(LEDGER)

    def test_supported_with_real_quote_passes(self):
        self.assertEqual(cov.verify_supported(self.by["S1.1"], _item("S1.1"), self.blocks), [])

    def test_quote_missing_unknown_fact_and_fabricated_quote(self):
        self.assertIn("quote_missing", cov.verify_supported(self.by["S1.1"], _item("S1.1", quotes=()), self.blocks))
        self.assertIn("unknown_fact_id", cov.verify_supported(self.by["S1.1"], _item("S1.1", ids=("XX-9",)), self.blocks))
        r = cov.verify_supported(self.by["S1.1"], _item("S1.1", quotes=("存在しない引用文です",)), self.blocks)
        self.assertIn("quote_not_in_ledger", r)

    def test_quote_normalization_ignores_whitespace_and_width(self):
        q = "20% の償還料が 7月13日に提案された"  # 半角%・空白差はNFKC+空白除去で一致
        self.assertEqual(cov.verify_supported(self.by["S1.1"], _item("S1.1", quotes=(q,)), self.blocks), [])

    def test_i_number_not_in_fact(self):
        changed = {**self.by["S1.2"], "text": "It said 30% would be charged."}
        self.assertIn("number_not_in_fact", cov.verify_supported(changed, _item("S1.2"), self.blocks))
        self.assertNotIn("number_not_in_fact", cov.verify_supported(self.by["S1.2"], _item("S1.2"), self.blocks))
        self.assertEqual(cov.numbers_not_in_facts("It said 20% on July 13.", self.blocks["HF-001"]), [])
        self.assertEqual(cov.numbers_not_in_facts("About 2 million barrels.", "約200万バレル"), [])
        self.assertEqual(cov.numbers_not_in_facts("Brent was about 3%.", "2.6％上昇"), [])  # 自然な四捨五入
        self.assertEqual(cov.numbers_not_in_facts("Brent was about 2%.", "2.6％上昇"), [2.0])  # 意味が変わる丸め

    def test_ii_causal_word_without_fact_causal_description(self):
        # S2.2は関係単位の文(So...)。HF-002には因果記述が無い -> 戻す。HF-003には因果記述があるため戻さない。
        u = self.by["S2.2"]
        bad = cov.verify_supported(u, _item("S2.2", ids=("HF-002",), quotes=("徴収方法は示されなかった",)), self.blocks)
        self.assertIn("causal_not_in_fact", bad)
        ok = cov.verify_supported(u, _item("S2.2", ids=("HF-003",), quotes=("米国は7月14日に案を撤回し",)), self.blocks)
        self.assertNotIn("causal_not_in_fact", ok)
        # HF-001は因果を否定する記述(確認できない)を持つ -> 因果記述なし扱い
        den = cov.verify_supported(u, _item("S2.2", ids=("HF-001",), quotes=("20％の償還料が7月13日に提案された",)), self.blocks)
        self.assertIn("causal_not_in_fact", den)

    def test_iii_negation_polarity(self):
        neg = {"id": "X", "type": "sentence", "text": "The post did not say how to collect it.", "start": 0, "end": 1}
        pos = {"id": "Y", "type": "sentence", "text": "The post said how to collect it.", "start": 0, "end": 1}
        self.assertFalse(cov.negation_mismatch(neg, [self.blocks["HF-002"]]))
        self.assertTrue(cov.negation_mismatch(pos, [self.blocks["HF-002"]]))
        self.assertTrue(cov.negation_mismatch(neg, [self.blocks["HF-001"]]))

    def test_iv_group_inconsistency_returns_supported_to_candidate(self):
        status = {"S1.1": "SUPPORTED", "L1": "CANDIDATE"}
        cands: list = []
        n = cov.apply_group_consistency(status, cands, [["S1.1", "L1"]], self.by)
        self.assertEqual(n, 1)
        self.assertEqual(status["S1.1"], "SUPPORTED->CANDIDATE(group_inconsistent)")
        self.assertEqual(cands[0]["sub_reasons"], ["group_inconsistent"])
        status2 = {"S1.1": "SUPPORTED", "L1": "SUPPORTED"}
        self.assertEqual(cov.apply_group_consistency(status2, [], [["S1.1", "L1"]], self.by), 0)


class TestEvaluateAndUnion(unittest.TestCase):
    def setUp(self):
        self.sp = _split()
        self.by = {u["id"]: u for u in self.sp["units"]}
        self.blocks = cov.ledger_fact_blocks(LEDGER)

    def test_missing_ids_unknown_ids_and_duplicate_conflict(self):
        req = ["S1.1", "S1.2", "L1"]
        items = [_item("S1.1"), _item("ZZ9", verdict="CANDIDATE", claim="zz"), _item("L1"),
                 _item("L1", verdict="CANDIDATE", issue="dup")]
        ev = cov.evaluate_r3(items, self.by, req, self.blocks, ARTICLE)
        self.assertEqual(ev["missing"], ["S1.2"])
        self.assertEqual(ev["unknown_unit_ids"], ["ZZ9"])
        self.assertEqual(ev["status"]["L1"], "SUPPORTED->CANDIDATE(duplicate_conflict)")
        self.assertEqual(ev["status"]["S1.1"], "SUPPORTED")

    def test_union_dedups_relation_and_later_sentence_and_same_group(self):
        mk = lambda uid, route, flags=None: cov._candidate(  # noqa: E731
            self.by[uid], self.by, route, "model", "i-" + uid, {**ZERO, **(flags or {})}, "HF-001")
        merged = cov.union_candidates([mk("R:L1+L2", "r3", {"changed_causality": True}), mk("L2", "r5"), mk("S1.1", "r3"),
                                       mk("L1", "r5", {"changed_time": True})])
        self.assertEqual(len(merged), 2)
        a = next(m for m in merged if m["claim_text"] == "So the plan left the stage.")
        self.assertEqual(sorted(a["unit_ids"]), ["L2", "R:L1+L2"])
        self.assertEqual(sorted(a["routes"]), ["r3", "r5"])
        self.assertTrue(a["flags"]["changed_causality"])
        b = next(m for m in merged if m["claim_text"].startswith("The plan was posted"))
        self.assertEqual(sorted(b["unit_ids"]), ["L1", "S1.1"])
        self.assertTrue(b["flags"]["changed_time"])

    def test_r5_status_and_candidates(self):
        out = [{"fact_id": "HF-001", "matches": [
            {"unit_id": "S1.1", "verdict": "MATCH", "issue": "", "claim_in_article": "", "flags": dict(ZERO)},
            {"unit_id": "S1.2", "verdict": "DEVIATION", "issue": "x", "claim_in_article": "It said 20% would be charged.",
             "flags": {**ZERO, "changed_certainty": True}}]}]
        ev = cov.evaluate_r5(out, self.by, ["HF-001", "HF-002"], ARTICLE)
        self.assertEqual(ev["status"]["S1.1"], "MATCH")
        self.assertEqual(ev["status"]["S2.1"], "UNMENTIONED")
        self.assertEqual(len(ev["candidates"]), 1)
        self.assertEqual(ev["facts_missing"], ["HF-002"])

    def test_to_deviations_shape_and_no_severity_decision(self):
        c = cov._candidate(self.by["S1.2"], self.by, "r3", "model", "issue", {**ZERO, "changed_number": True}, "HF-001")
        d = cov.candidates_to_deviations(cov.union_candidates([c]))[0]
        self.assertEqual(d["severity"], "MAJOR")  # Stage 2への入口を通す印。重大度判定はStage 2
        self.assertEqual(d["claim_in_article"], "It said 20% would be charged.")
        self.assertIn("severity is decided by Stage 2", d["explanation"])
        self.assertEqual(d["related_fact_id"], "HF-001")


import re


class FakeLLM:
    """偽LLM(call_fn)。r3_fn/r5_fn=(label, required_ids_or_fact_ids)->応答dict、fail_labels=Noneを返すlabel。"""

    def __init__(self, r3_fn=None, r5_fn=None, fail_labels=()):
        self.r3_fn, self.r5_fn, self.fail, self.labels = r3_fn, r5_fn, set(fail_labels), []

    def __call__(self, label, developer, prompt, schema):
        self.labels.append(label)
        meta = {"cost_jpy": 1.0, "usage": {}}
        if label in self.fail:
            return None, {"cost_jpy": 0.0, "error": "fake"}
        if schema is cov.R3_JSON_SCHEMA:
            ids = re.search(r"【判定必須の単位ID\(全\d+件\)】\n(.*)\n", prompt).group(1).split(", ")
            return (self.r3_fn(label, ids) if self.r3_fn else {"unit_verdicts": [
                _item(i, "CANDIDATE", issue="x") for i in ids]}), meta
        fids = re.search(r"【factID一覧\(全\d+件\)】\n(.*)\n", prompt).group(1).split(", ")
        return (self.r5_fn(label, fids) if self.r5_fn else {"facts": [{"fact_id": f, "matches": []} for f in fids]}), meta


def _run(llm, routes="both", article=ARTICLE):
    fx = {"ledger_text": LEDGER, "article_text": article}
    return cov.run_stage1_coverage(fx, llm, routes, runner.vs_sentence_segments_l6, runner.CAUSAL_SENTENCE_INITIAL_EN)


class TestRunStage1Coverage(unittest.TestCase):
    def test_missing_ids_rerun_once_then_coverage_gap(self):
        def r3(label, ids):
            return {"unit_verdicts": [_item(i, "CANDIDATE", issue="x") for i in ids if i != "S1.2"]}
        llm = FakeLLM(r3_fn=r3)
        res = _run(llm, "r3_only")
        self.assertEqual(llm.labels, ["r3", "r3_rerun"])  # 再実行は1回だけ
        pr = res["audit"]["per_route"]["r3"]
        self.assertEqual(pr["missing_first"], ["S1.2"])
        self.assertEqual(pr["missing_after_rerun"], ["S1.2"])
        self.assertTrue(pr["rerun_used"])
        self.assertEqual(pr["unit_status"]["S1.2"], "MISSING->CANDIDATE(coverage_gap)")
        gap = [m for m in res["candidates"] if "coverage_gap" in m["sub_reasons"]]
        self.assertEqual([m["unit_ids"] for m in gap], [["S1.2"]])
        self.assertFalse(res["api_failure"])

    def test_missing_ids_filled_by_rerun_leaves_no_gap(self):
        def r3(label, ids):
            keep = [i for i in ids if i != "S1.2"] if label == "r3" else ids
            return {"unit_verdicts": [_item(i, "CANDIDATE", issue="x") for i in keep]}
        res = _run(FakeLLM(r3_fn=r3), "r3_only")
        self.assertEqual(res["audit"]["per_route"]["r3"]["missing_after_rerun"], [])
        self.assertFalse([m for m in res["candidates"] if "coverage_gap" in m["sub_reasons"]])

    def test_api_failure_after_one_retry_is_flagged_fail_closed(self):
        llm = FakeLLM(fail_labels={"r3", "r3_retry"})
        res = _run(llm, "r3_only")
        self.assertEqual(llm.labels, ["r3", "r3_retry"])
        self.assertTrue(res["api_failure"])
        self.assertEqual(res["failed_routes"], ["r3"])
        parsed = cov.to_stage1_parsed(res)
        self.assertTrue(parsed["_stage1_api_failure"])
        self.assertEqual(parsed["deviations"], [])

    def test_transient_failure_recovers_by_retry(self):
        llm = FakeLLM(fail_labels={"r5"})
        res = _run(llm, "r5_only")
        self.assertEqual(llm.labels, ["r5", "r5_retry"])
        self.assertFalse(res["api_failure"])

    def test_fabricated_quote_supported_becomes_candidate(self):
        def r3(label, ids):
            return {"unit_verdicts": [
                _item(i, "SUPPORTED", quotes=("ありもしない引用です",)) if i == "S1.1" else _item(i, "CANDIDATE", issue="x")
                for i in ids]}
        res = _run(FakeLLM(r3_fn=r3), "r3_only")
        st = res["audit"]["per_route"]["r3"]["unit_status"]["S1.1"]
        self.assertEqual(st, "SUPPORTED->CANDIDATE(quote_not_in_ledger)")
        self.assertEqual(res["audit"]["returned_by_check"]["r3"] >= 1, True)

    def test_routes_selection_and_union_overlap(self):
        def r5(label, fids):
            return {"facts": [{"fact_id": "HF-001", "matches": [
                {"unit_id": "S1.2", "verdict": "DEVIATION", "issue": "d", "claim_in_article": "", "flags": dict(ZERO)}]}]}
        both = _run(FakeLLM(r5_fn=r5), "both")
        self.assertEqual(set(both["audit"]["per_route"]), {"r3", "r5"})
        self.assertIn("S1.2", both["audit"]["overlap"]["both"])
        self.assertEqual(both["audit"]["n_calls"], 2)
        r5only = _run(FakeLLM(r5_fn=r5), "r5_only")
        self.assertEqual(set(r5only["audit"]["per_route"]), {"r5"})
        self.assertIsNone(r5only["audit"]["overlap"])
        self.assertEqual([m["unit_ids"] for m in r5only["candidates"]], [["S1.2"]])
        self.assertEqual(both["audit"]["total_cost_jpy"], 2.0)
        with self.assertRaises(ValueError):
            _run(FakeLLM(), "bogus")

    def test_audit_has_prompt_sha_and_candidate_origin_info(self):
        res = _run(FakeLLM(), "both")
        a = res["audit"]
        self.assertIn("R3_PROMPT_TEMPLATE", a["prompt_sha256"])
        self.assertIn("same_sentence_groups", a)
        self.assertTrue(all("routes" in m and "sub_reasons" in m for m in a["union_candidates"]))


import glob
import os

FAIL1 = {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_stage1_api_failure": True}
OK1 = {"overall_status": "LEDGER_COMPLIANT", "deviations": []}


def _state0():
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def _inst(fixture=None, mode="fresh"):
    return {"instance_id": "unit_t06", "group": "unit", "expected_group_label": "unit", "stage1_mode": mode,
            "stage1_source": None,
            "fixture": fixture or {"ledger_text": "(l)", "article_text": "(a)", "source_article_text": None}}


class _Reached(Exception):
    pass


def _run_inst(inst, stage1_seq, switches=None, extra_patches=()):
    """stage1_fresh_with_enumeration(legacy経路)をstage1_seqで差し替えてrun_instanceを実行。(result, call_count)"""
    seq, calls = list(stage1_seq), []

    def fake_stage1(client, state, ce, call_log, label, fixture, developer_message=None):
        calls.append(label)
        return dict(seq.pop(0))

    patches = [mock.patch.object(runner, "stage1_fresh_with_enumeration", fake_stage1),
               mock.patch.object(runner, "save_json", lambda *a, **k: None)]
    patches += [mock.patch.object(runner, k, v) for k, v in (switches or {}).items()] + list(extra_patches)
    for p in patches:
        p.start()
    try:
        res = runner.run_instance(object(), _state0(), [0], inst, stage1_cache={})
    finally:
        for p in reversed(patches):
            p.stop()
    return res, calls


class TestRunnerSwitchesDefaultsAndDispatch(unittest.TestCase):
    def test_defaults_are_legacy_and_not_in_kpi_trial_switches(self):
        self.assertEqual(runner.STAGE1_MODE, "legacy_v4a")
        self.assertEqual(runner.STAGE1_ROUTES, "both")
        self.assertIs(runner.F3_PRECHECK_ALWAYS, False)
        self.assertIs(runner.STAGE1_FAIL_CLOSED, False)
        for k in ("STAGE1_MODE", "STAGE1_ROUTES", "F3_PRECHECK_ALWAYS", "STAGE1_FAIL_CLOSED"):
            self.assertNotIn(k, runner.KPI_TRIAL_SWITCHES)
        self.assertEqual(runner.MODEL, "gpt-6-luna")

    def test_dispatch_legacy_calls_existing_functions_and_coverage_branches(self):
        with mock.patch.object(runner, "stage1_fresh_with_enumeration", lambda *a, **k: {"via": "enum"}), \
             mock.patch.object(runner, "stage1_fresh", lambda *a, **k: {"via": "plain"}), \
             mock.patch.object(runner, "stage1_coverage_fresh", lambda *a, **k: {"via": "coverage"}):
            args = (None, {}, [0], [], "l", {}, "dm")
            self.assertEqual(runner.stage1_fresh_dispatch(*args, True), {"via": "enum"})
            self.assertEqual(runner.stage1_fresh_dispatch(*args, False), {"via": "plain"})
            with mock.patch.object(runner, "STAGE1_MODE", "coverage_union"):
                self.assertEqual(runner.stage1_fresh_dispatch(*args, True), {"via": "coverage"})
            with mock.patch.object(runner, "STAGE1_MODE", "bogus"):
                with self.assertRaises(ValueError):
                    runner.stage1_fresh_dispatch(*args, True)

    def test_coverage_fresh_with_fake_client_logs_calls_and_costs(self):
        class Resp:
            def __init__(self, t):
                self.output_text = t

        class Responses:
            def create(self, **kw):
                import json
                name = kw["text"]["format"]["name"]
                if "r3" in name:
                    ids = re.search(r"【判定必須の単位ID\(全\d+件\)】\n(.*)\n", kw["input"][1]["content"]).group(1).split(", ")
                    return Resp(json.dumps({"unit_verdicts": [_item(i, "CANDIDATE", issue="x") for i in ids]}))
                return Resp(json.dumps({"facts": []}))

        class Client:
            responses = Responses()

        log, st = [], _state0()
        with mock.patch.object(runner.s2p, "_extract_usage", lambda r: {"input_tokens": 1}), \
             mock.patch.object(runner.s2p, "official_cost_jpy", lambda u: 2.0), \
             mock.patch.object(runner, "save_budget_state", lambda s: None):
            parsed = runner.stage1_coverage_fresh(Client(), st, [0], log, "t06_stage1",
                                                  {"ledger_text": LEDGER, "article_text": ARTICLE})
        self.assertEqual([c["label"] for c in log], ["t06_stage1_r3", "t06_stage1_r5"])
        self.assertEqual(round(st["cumulative_jpy"], 2), 4.0)
        self.assertEqual(parsed["overall_status"], "LEDGER_DEVIATION")
        self.assertEqual(parsed["stage1_coverage_audit"]["total_cost_jpy"], 4.0)
        self.assertTrue(all(d["severity"] == "MAJOR" for d in parsed["deviations"]))

    def test_no_production_path_references_new_modules(self):
        for pat in ("er003*.py", "er009*.py", "er010*.py", "er012*.py", "er019*.py"):
            for f in glob.glob(os.path.join(os.path.dirname(__file__) or ".", pat)):
                with open(f, encoding="utf-8", errors="ignore") as fh:
                    self.assertNotIn("er052_open233", fh.read(), f)


class TestH1FailClosed(unittest.TestCase):
    def _no_stage2(self):
        def boom(*a, **k):
            raise AssertionError("後段(Stage 2)へ進んではならない")
        return [mock.patch.object(runner, "run_stage2", boom)]

    def test_legacy_fail_closed_reruns_once_then_stops_with_api_failure(self):
        res, calls = _run_inst(_inst(), [FAIL1, FAIL1], {"STAGE1_FAIL_CLOSED": True}, self._no_stage2())
        self.assertEqual(calls, ["unit_t06_stage1", "unit_t06_stage1_rerun"])
        self.assertEqual((res["final_state"], res["stage4_reason"]), ("STAGE4_ESCALATION", "api_failure"))
        self.assertTrue(res["stage4_allowlist"]["decisions"][0]["decision"]["allowed"])
        self.assertTrue(res["stage1_api_failure_stop"])

    def test_legacy_fail_closed_recovers_when_rerun_succeeds(self):
        res, calls = _run_inst(_inst(), [FAIL1, OK1], {"STAGE1_FAIL_CLOSED": True}, self._no_stage2())
        self.assertEqual(len(calls), 2)
        self.assertEqual(res["final_state"], "ACCEPTABLE_STAGE1")

    def test_switch_off_keeps_legacy_behavior_single_call_no_stop(self):
        res, calls = _run_inst(_inst(), [FAIL1])
        self.assertEqual(len(calls), 1)
        self.assertNotEqual(res["final_state"], "STAGE4_ESCALATION")
        self.assertNotIn("stage1_api_failure_stop", res)

    def test_coverage_union_does_not_rerun_again_in_runner(self):
        n = []

        def cov_fail(*a, **k):
            n.append(1)
            return dict(FAIL1)
        res, _ = _run_inst(_inst(), [], {"STAGE1_FAIL_CLOSED": True, "STAGE1_MODE": "coverage_union",
                                         "stage1_coverage_fresh": cov_fail}, self._no_stage2())
        self.assertEqual(len(n), 1)
        self.assertEqual(res["stage4_reason"], "api_failure")


class TestF3AndLegacyInvariance(unittest.TestCase):
    def _fx(self):
        ins = {i["instance_id"]: i for i in runner.build_target_instances()}["safety_er009_changed_number"]
        return {"ledger_text": ins["fixture"]["ledger_text"], "article_text": ins["fixture"]["article_text"],
                "source_article_text": None}

    def test_f3_off_stage1_miss_passes_early_even_with_precheck_hit(self):
        res, _ = _run_inst(_inst(self._fx()), [OK1])
        self.assertEqual(res["final_state"], "ACCEPTABLE_STAGE1")
        self.assertNotIn("f3_precheck_always", res)

    def test_f3_on_runs_precheck_floor_before_early_pass(self):
        def reached(*a, **k):
            raise _Reached()
        with self.assertRaises(_Reached):  # precheck floorがBLOCKING化されRewrite(Stage 3)へ進む=早期PASSしない
            _run_inst(_inst(self._fx()), [OK1], {"F3_PRECHECK_ALWAYS": True},
                      [mock.patch.object(runner, "run_stage3_for_claim", reached)])

    def test_f3_on_without_precheck_hit_still_passes_and_records_zero_hits(self):
        res, _ = _run_inst(_inst(), [OK1], {"F3_PRECHECK_ALWAYS": True})
        self.assertEqual(res["final_state"], "ACCEPTABLE_STAGE1")
        self.assertEqual(res["f3_precheck_always"], {"precheck_floor_hits": 0})
        self.assertEqual(res["switches"].get("F3_PRECHECK_ALWAYS"), None)  # 早期return経路のswitches記録は従来どおり不変

    def test_legacy_result_has_no_new_keys(self):
        res, _ = _run_inst(_inst(), [OK1])
        for k in ("stage1_coverage", "f3_precheck_always", "stage1_api_failure_stop"):
            self.assertNotIn(k, res)
        self.assertNotIn("STAGE1_MODE", res["switches"])

    def test_coverage_mode_ignores_reuse_fixture_and_runs_fresh(self):
        def no_reuse(*a, **k):
            raise AssertionError("reuseの保存済みV4A出力を使ってはならない")
        res, _ = _run_inst(_inst(mode="reuse"), [], {"STAGE1_MODE": "coverage_union",
                                                     "stage1_reuse": no_reuse,
                                                     "stage1_coverage_fresh": lambda *a, **k: dict(OK1)})
        self.assertEqual(res["final_state"], "ACCEPTABLE_STAGE1")


class TestStageAScript(unittest.TestCase):
    """段階Aスクリプトの¥0検証(偽client、一時ディレクトリ)。実API・実出力dirには一切触れない。"""

    def test_plan_estimate_guard_and_fake_run_aggregate(self):
        import json
        import tempfile
        import er052_open233_stage1_stageA_01 as sa

        plan = sa.plan()
        self.assertEqual(len(plan), 48)  # 13x3 + 9
        self.assertEqual(sum(1 for s, i in plan if i in sa.HOLDOUT_IDS), 9)
        self.assertEqual({s for s, i in plan if i in sa.HOLDOUT_IDS}, {1})
        insts = {i["instance_id"]: i for i in runner.build_target_instances()}
        est = sa.estimate_cost(insts, plan)
        lo, mid, hi = est["total_jpy_low_mid_high"]
        self.assertTrue(0 < lo < mid < hi)

        class Resp:
            def __init__(self, t):
                self.output_text = t

        class Responses:
            def create(self, **kw):
                name = kw["text"]["format"]["name"]
                if "r3" in name:
                    ids = re.search(r"【判定必須の単位ID\(全\d+件\)】\n(.*)\n", kw["input"][1]["content"]).group(1).split(", ")
                    return Resp(json.dumps({"unit_verdicts": [_item(i, "CANDIDATE", issue="x") for i in ids]}))
                return Resp(json.dumps({"facts": []}))

        class Client:
            responses = Responses()

        with tempfile.TemporaryDirectory() as td:
            patches = [mock.patch.object(sa, "OUT_DIR_A", td), mock.patch.object(sa, "BUDGET_STATE_A", td + "/b.json"),
                       mock.patch.object(runner, "OUT_DIR", runner.OUT_DIR), mock.patch.object(runner, "BUDGET_STATE_PATH", runner.BUDGET_STATE_PATH),
                       mock.patch.object(runner, "TOTAL_BUDGET_JPY", runner.TOTAL_BUDGET_JPY),
                       mock.patch.object(runner, "STAGE1_MODE", runner.STAGE1_MODE),
                       mock.patch.object(runner, "STAGE1_ROUTES", runner.STAGE1_ROUTES),
                       mock.patch.object(sa.vfl01, "get_client", lambda: Client()),
                       mock.patch.object(runner.s2p, "_extract_usage", lambda r: {}),
                       mock.patch.object(runner.s2p, "official_cost_jpy", lambda u: 0.5)]
            for p in patches:
                p.start()
            try:
                import contextlib
                import io
                with contextlib.redirect_stdout(io.StringIO()):
                    sa.run_main(65.0)
                runs = sa.load_runs()
                agg = sa.aggregate(runs)
                self.assertEqual(runner.STAGE1_MODE, "coverage_union")  # run中のみ(patch終了で復元)
            finally:
                for p in reversed(patches):
                    p.stop()
        self.assertEqual(runner.STAGE1_MODE, "legacy_v4a")
        self.assertEqual(len(runs), 48)
        self.assertEqual(agg["cost"]["n_calls"], 96)
        self.assertEqual(agg["cost"]["total_jpy"], 48.0)
        self.assertEqual(len(agg["gold_sc"]), 6)
        self.assertTrue(all(g["union_detected"] == "3/3" for g in agg["gold_sc"]))
        self.assertTrue(agg["criteria_result"]["sc_union_3of3_all"])
        self.assertTrue(agg["criteria_result"]["holdout_new_miss_zero"])
        self.assertEqual(agg["missing_id_rate_after_rerun"], 0.0)

    def test_main_requires_explicit_paid_flag(self):
        import sys
        import er052_open233_stage1_stageA_01 as sa
        with mock.patch.object(sys, "argv", ["x", "--stage", "main"]), mock.patch.object(sa, "run_main") as rm:
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
                sa.main()
            rm.assert_not_called()


class TestNegationCorrectionA(unittest.TestCase):
    """委任_11: 否定是正案a(`negation_mode="a"`)。既定legacyは不変。合成陽性例(否定付加/否定除去/二重否定)と旧149件の再分類。"""
    POS = "[VERIFIED] HF-001: 20％の償還料が7月13日に提案された。\n  scope: x"
    NEG = "[VERIFIED] HF-002: 徴収方法は示されなかった。\n  scope: y"

    def _u(self, text):
        return {"type": "sentence", "text": text, "claim_text": text}

    def test_synthetic_positive_negation_added_is_detected(self):
        self.assertTrue(cov.negation_mismatch_a(self._u("The plan was not posted on July 13."), [self.POS]))

    def test_synthetic_positive_negation_removed_is_detected(self):
        self.assertTrue(cov.negation_mismatch_a(self._u("The post explained how to collect it."), [self.NEG]))

    def test_synthetic_positive_double_negation_is_detected(self):
        # 二重否定(単位側に否定語、factは肯定)=極性が反転しているので保守的に検出する
        self.assertTrue(cov.negation_mismatch_a(self._u("It is not true that the plan was never posted."), [self.POS]))

    def test_matching_polarity_is_not_flagged(self):
        self.assertFalse(cov.negation_mismatch_a(self._u("The post did not say how to collect it."), [self.NEG]))
        self.assertFalse(cov.negation_mismatch_a(self._u("The plan was posted on July 13."), [self.POS]))

    def test_contrast_construction_and_not_only_are_excluded(self):
        soon = "[VERIFIED] HF-003: 米国はほどなく案を撤回した。\n  scope: z"
        u = self._u("The US withdrew the plan soon after.")
        self.assertTrue(cov.negation_mismatch(u, [soon]))      # legacy=誤発火(ほどなく=「なく」)
        self.assertFalse(cov.negation_mismatch_a(u, [soon]))   # 案a=対比構文を除外
        not_only = self._u("The plan was not only posted on July 13.")
        self.assertTrue(cov.negation_mismatch(not_only, [self.POS]))
        self.assertFalse(cov.negation_mismatch_a(not_only, [self.POS]))

    def test_only_is_not_broadly_excluded(self):
        # Opus#17条件(3): 「only」を除外語に広く入れない(本物の範囲の変化を消さない)
        self.assertEqual(cov._unit_neg_a("Only 3 firms joined."), bool(cov.NEGATION_EN_RE.search("Only 3 firms joined.")))
        self.assertEqual(cov.NOT_ONLY_RE.sub(" ", "Only 3 firms joined."), "Only 3 firms joined.")
        self.assertTrue(cov._unit_neg_a("The plan lacks any details."))  # lack/dislike/fail to/unableは追加

    def test_nashi_and_english_ledger_line(self):
        nashi = "[VERIFIED] HF-004: 合意は成立なし。\n  scope: w"
        self.assertFalse(cov.negation_mismatch(self._u("A deal was reached."), [nashi]))  # legacyは「なし」を拾わない
        self.assertTrue(cov.negation_mismatch_a(self._u("A deal was reached."), [nashi]))
        en = "[VERIFIED] HF-9: The plan was not posted.\n  scope: v"
        u = self._u("The plan was not posted.")
        self.assertTrue(cov.negation_mismatch(u, [en]))       # legacy=英語Ledger行で誤発火
        self.assertFalse(cov.negation_mismatch_a(u, [en]))

    def test_mode_switch_default_legacy_and_verify_supported_wiring(self):
        unit = {"type": "sentence", "text": "The US withdrew the plan soon after.", "claim_text": "The US withdrew the plan soon after."}
        item = _item("S1.1", ids=("HF-003",), quotes=("米国はほどなく案を撤回した",))
        bl = {"HF-003": "[VERIFIED] HF-003: 米国はほどなく案を撤回した。\n  scope: z"}
        self.assertIn("negation_polarity_mismatch", cov.verify_supported(unit, item, bl))
        self.assertIn("negation_polarity_mismatch", cov.verify_supported(unit, item, bl, "legacy"))
        self.assertNotIn("negation_polarity_mismatch", cov.verify_supported(unit, item, bl, "a"))
        with self.assertRaises(ValueError):
            cov.run_stage1_coverage({"ledger_text": LEDGER, "article_text": ARTICLE}, FakeLLM(), negation_mode="bogus")

    def test_old_149_firings_reclassified_to_9_unique_6(self):
        import json
        runs_dir = "er052_output/open233_stage1_stageA_01/runs"
        if not os.path.isdir(runs_dir):
            self.skipTest("stage A saved runs not present")
        insts = {i["instance_id"]: i for i in runner.build_target_instances()}
        blocks = {}
        old = new = 0
        uniq = set()
        for p in sorted(glob.glob(runs_dir + "/s*/*.json")):
            with open(p, encoding="utf-8") as fh:
                r = json.load(fh)
            iid = r["instance_id"]
            blocks.setdefault(iid, cov.ledger_fact_blocks(insts[iid]["fixture"]["ledger_text"]))
            for c in r["audit"]["union_candidates"]:
                if "negation_polarity_mismatch" not in c["sub_reasons"]:
                    continue
                blk = blocks[iid].get((c.get("related_fact_ids") or [""])[0], "")
                if not blk:
                    continue
                u = {"type": "sentence", "text": c["claim_text"], "claim_text": c["claim_text"]}
                old += cov.negation_mismatch(u, [blk])
                if cov.negation_mismatch_a(u, [blk]):
                    new += 1
                    uniq.add((iid, c["unit_ids"][0]))
        self.assertEqual(old, 149)
        self.assertEqual(new, 9)
        self.assertEqual(len(uniq), 6)


def _r3_support_some(label, ids):
    """S1.1・L1(同文グループ)はHF-001、S2.1はHF-002の逐語引用つきSUPPORTED。他はCANDIDATE(issue=r3cand-<id>)。"""
    def one(i):
        if i in ("S1.1", "L1"):
            return _item(i, "SUPPORTED")
        if i == "S2.1":
            return _item(i, "SUPPORTED", ids=("HF-002",), quotes=("徴収方法は示されなかった",))
        return _item(i, "CANDIDATE", issue="r3cand-" + i)
    return {"unit_verdicts": [one(i) for i in ids]}


def _run2(llm, routes="both", article=ARTICLE, **kw):
    fx = {"ledger_text": LEDGER, "article_text": article}
    return cov.run_stage1_coverage(fx, llm, routes, runner.vs_sentence_segments_l6, runner.CAUSAL_SENTENCE_INITIAL_EN, **kw)


class TestR5VerifySupported(unittest.TestCase):
    def test_default_r5_mode_is_full_and_labels_unchanged(self):
        llm = FakeLLM()
        res = _run2(llm)
        self.assertEqual(llm.labels, ["r3", "r5"])
        self.assertEqual(res["audit"]["r5_mode"], "full")

    def test_target_units_are_r3_supported_plus_relation_only(self):
        sp = _split()
        status = {"S1.1": "SUPPORTED", "S1.2": "CANDIDATE", "S2.1": "SUPPORTED", "S2.2": "SUPPORTED->CANDIDATE(quote_missing)", "T": "SUPPORTED"}
        ids = [u["id"] for u in cov.r5v_target_units(sp["units"], status)]
        self.assertEqual(sorted(i for i in ids if not i.startswith("R:")), ["S1.1", "S2.1", "S2.2", "T"])  # 委任_13: D(quote_missing)で戻された単位もモデル判定SUPPORTEDなので対象
        self.assertEqual(sorted(i for i in ids if i.startswith("R:")), sorted(sp["relation_ids"]))
        self.assertNotIn("S1.2", ids)
        self.assertNotIn("P1", ids)

    def test_prompt_has_full_article_and_no_r3_quotes_or_verdicts(self):
        seen = {}

        def r5(label, fids):
            return {"facts": [{"fact_id": f, "matches": []} for f in fids]}

        class Spy(FakeLLM):
            def __call__(self, label, developer, prompt, schema):
                seen[label] = (developer, prompt, schema)
                return super().__call__(label, developer, prompt, schema)
        res = _run2(Spy(r3_fn=_r3_support_some, r5_fn=r5), r5_mode="verify_supported")
        dev, prompt, schema = seen["r5v"]
        self.assertIs(schema, cov.R5_JSON_SCHEMA)  # 5-liteと同形(共用)
        self.assertIn(ARTICLE.strip(), prompt)      # 記事全文は文脈として渡す
        self.assertNotIn("r3cand-", prompt)         # r3のissue(判定)は渡さない
        self.assertNotIn("20％の償還料が7月13日に提案された", prompt.split("【Verified Fact Ledger】")[1].split("【記事全文")[1])  # r3引用はLedger節の外に出さない
        self.assertIn("[S1.1]", prompt.split("これらのIDだけをmatchesに使う)】")[1])
        self.assertNotIn("[S1.2]", prompt.split("これらのIDだけをmatchesに使う)】")[1].split("【factID一覧")[0])
        self.assertEqual(res["audit"]["r5_mode"], "verify_supported")
        self.assertIn("R5V_PROMPT_TEMPLATE", res["audit"]["prompt_sha256"])
        self.assertNotEqual(cov.PROMPT_SHA256["R5V_PROMPT_TEMPLATE"], cov.PROMPT_SHA256["R5_PROMPT_TEMPLATE"])

    def test_r5v_deviation_becomes_model_r5_candidate_and_is_in_union(self):
        def r5(label, fids):
            return {"facts": [{"fact_id": "HF-001", "matches": [
                {"unit_id": "S1.1", "verdict": "DEVIATION", "issue": "v", "claim_in_article": "", "flags": {**ZERO, "changed_time": True}}]}]}
        res = _run2(FakeLLM(r3_fn=_r3_support_some, r5_fn=r5), r5_mode="verify_supported")
        c = next(m for m in res["candidates"] if "S1.1" in m["unit_ids"])
        self.assertIn("r5", c["routes"])  # 同文グループ(L1)のr3候補と文キーで統合される
        self.assertIn("model_r5", c["sources"])
        self.assertTrue(c["flags"]["changed_time"])

    def test_no_targets_skips_r5v_call(self):
        llm = FakeLLM()  # 全単位CANDIDATE -> 関係単位は常に対象なので、関係単位が無い記事で確認
        art = "# T\n\nThe plan was posted on July 13. It said 20% would be charged.\n"
        res = cov.run_stage1_coverage({"ledger_text": LEDGER, "article_text": art}, llm, "both", runner.vs_sentence_segments_l6,
                                      runner.CAUSAL_SENTENCE_INITIAL_EN, r5_mode="verify_supported")
        self.assertEqual(llm.labels, ["r3"])
        self.assertTrue(res["audit"]["per_route"]["r5"]["calls"] == [])
        self.assertFalse(res["api_failure"])

    def test_r5v_requires_r3_result(self):
        with self.assertRaises(ValueError):
            _run2(FakeLLM(), "r5_only", r5_mode="verify_supported")
        with self.assertRaises(ValueError):
            _run2(FakeLLM(), "both", r5_mode="bogus")

    def test_stored_r3_reuse_skips_r3_call(self):
        first = _run2(FakeLLM(r3_fn=_r3_support_some))
        stored = first["audit"]["per_route"]["r3"]  # 保存audit形(unit_status/candidatesあり)
        llm = FakeLLM()
        res = _run2(llm, "both", r5_mode="verify_supported", r3_precomputed=stored)
        self.assertEqual(llm.labels, ["r5v"])
        self.assertTrue(res["audit"]["r3_reused"])
        self.assertTrue(res["audit"]["per_route"]["r3"]["reused_from_stored"])
        self.assertTrue(all("sources" in c for c in res["candidates"]))


class TestR5VTargetsByModelVerdict(unittest.TestCase):
    """委任_13: r5-V対象=r3の**モデル判定**SUPPORTED(D適用前)+関係単位。"""

    def test_d_changed_unit_is_target(self):
        sp = _split()
        status = {"S1.1": "SUPPORTED->CANDIDATE(negation_polarity_mismatch)", "S1.2": "CANDIDATE",
                  "S2.1": "SUPPORTED->CANDIDATE(number_not_in_fact,quote_missing)", "T": "SUPPORTED",
                  "S2.2": "SUPPORTED->CANDIDATE(group_inconsistent)"}
        ids = [u["id"] for u in cov.r5v_target_units(sp["units"], status)]
        for i in ("S1.1", "S2.1", "T", "S2.2"):
            self.assertIn(i, ids)
        self.assertNotIn("S1.2", ids)

    def test_relation_units_always_and_r3_candidate_conflict_gap_excluded(self):
        sp = _split()
        status = {"S1.1": "CANDIDATE", "S1.2": "SUPPORTED->CANDIDATE(duplicate_conflict)", "S2.1": "MISSING->CANDIDATE(coverage_gap)"}
        ids = [u["id"] for u in cov.r5v_target_units(sp["units"], status)]
        self.assertEqual(sorted(ids), sorted(sp["relation_ids"]))

    def test_model_verdict_takes_priority_over_status(self):
        sp = _split()
        status = {"S1.1": "SUPPORTED", "S1.2": "CANDIDATE"}
        mv = {"S1.1": "CANDIDATE", "S1.2": "SUPPORTED"}
        ids = [u["id"] for u in cov.r5v_target_units(sp["units"], status, mv)]
        self.assertIn("S1.2", ids)
        self.assertNotIn("S1.1", ids)

    def test_fresh_r3_records_model_verdict_and_d_changed_unit_reaches_r5v(self):
        seen = {}

        class Spy(FakeLLM):
            def __call__(self, label, developer, prompt, schema):
                seen[label] = prompt
                return super().__call__(label, developer, prompt, schema)
        # S2.1は引用不一致でD(quote_not_in_ledger)に戻されるが、モデル判定はSUPPORTED -> r5-V対象
        def r3(label, ids):
            return {"unit_verdicts": [_item(i, "SUPPORTED", ids=("HF-002",), quotes=("存在しない引用文です",)) if i == "S2.1"
                                      else _item(i, "CANDIDATE", issue="x") for i in ids]}
        res = _run2(Spy(r3_fn=r3), r5_mode="verify_supported")
        r3r = res["audit"]["per_route"]["r3"]
        self.assertTrue(r3r["unit_status"]["S2.1"].startswith("SUPPORTED->CANDIDATE("))
        self.assertEqual(r3r["model_verdict"]["S2.1"], "SUPPORTED")
        tail = seen["r5v"].split("これらのIDだけをmatchesに使う)】")[1].split("【factID一覧")[0]
        self.assertIn("[S2.1]", tail)

    def test_reapply_negation_a_restores_and_keeps_model_verdict(self):
        u = {"id": "X", "type": "sentence", "text": "The plan was not posted.", "claim_text": "The plan was not posted.",
             "start": 0, "end": 5, "para": "P1", "role": "", "judged": True}
        u2 = dict(u, id="Y", text="Other.", claim_text="Other.")
        en = "[VERIFIED] HF-9: The plan was not posted.\n  scope: v"
        pre = {"status": {"X": "SUPPORTED->CANDIDATE(negation_polarity_mismatch)",
                          "Y": "SUPPORTED->CANDIDATE(negation_polarity_mismatch,quote_missing)"},
               "candidates": [{"unit_id": "X", "unit_ids": ["X"], "related_fact_ids": ["HF-9"], "sources": ["deterministic"]},
                              {"unit_id": "Y", "unit_ids": ["Y"], "related_fact_ids": ["HF-9"], "sources": ["deterministic"]}]}
        out = cov.reapply_negation_a(pre, {"X": u, "Y": u2}, {"HF-9": en}, [])
        self.assertEqual(out["status"]["X"], "SUPPORTED")          # 否定案aで復帰
        self.assertTrue(out["status"]["Y"].startswith("SUPPORTED->CANDIDATE("))  # 他のD理由併存は不変
        self.assertEqual([c["unit_id"] for c in out["candidates"]], ["Y"])
        self.assertEqual(out["negation_reapplied"]["restored_to_supported"], ["X"])
        self.assertTrue(cov.r3_model_supported(out["status"]["Y"]))

    def test_reapply_group_inconsistent_recomputed(self):
        u = {"id": "A", "type": "sentence", "text": "a", "claim_text": "a", "start": 0, "end": 1, "para": "P1", "role": "", "judged": True}
        ub = dict(u, id="B")
        pre = {"status": {"A": "CANDIDATE", "B": "SUPPORTED->CANDIDATE(group_inconsistent)"},
               "candidates": [{"unit_id": "A", "unit_ids": ["A"], "sources": ["model_r3"]},
                              {"unit_id": "B", "unit_ids": ["B"], "sources": ["deterministic"]}]}
        out = cov.reapply_negation_a(pre, {"A": u, "B": ub}, {}, [["A", "B"]])
        self.assertTrue(out["status"]["B"].startswith("SUPPORTED->CANDIDATE(group_inconsistent"))  # 再適用で戻される
        self.assertEqual(sorted(c["unit_id"] for c in out["candidates"]), ["A", "B"])


class TestBracketedUnitIds(unittest.TestCase):
    def test_norm_uid(self):
        self.assertEqual(cov._norm_uid("[S2.1]"), "S2.1")
        self.assertEqual(cov._norm_uid(" [R:S4.1+S4.2] "), "R:S4.1+S4.2")
        self.assertEqual(cov._norm_uid("S2.1"), "S2.1")
        self.assertIsNone(cov._norm_uid(None))

    def test_r5_bracketed_id_is_valid_model_candidate_not_orphan(self):
        def r5(label, fids):
            return {"facts": [{"fact_id": "HF-001", "matches": [
                {"unit_id": "[S1.1]", "verdict": "DEVIATION", "issue": "v", "claim_in_article": "", "flags": ZERO}]}]}
        res = _run2(FakeLLM(r3_fn=_r3_support_some, r5_fn=r5), r5_mode="verify_supported")
        r5r = res["audit"]["per_route"]["r5"]
        self.assertEqual(r5r["unknown_unit_ids"], [])
        self.assertTrue(any(c["unit_ids"] == ["S1.1"] and "model" in c["sub_reasons"] for c in r5r["candidates"]))

    def test_is_model_cand_includes_orphan_unknown_unit_id(self):
        import er052_open233_stage1_stageA_01 as A
        self.assertTrue(A.is_model_cand({"sources": ["model_r5"], "sub_reasons": ["unknown_unit_id"]}))
        self.assertFalse(A.is_model_cand({"sources": ["deterministic"], "sub_reasons": ["number_not_in_fact"]}))
        self.assertFalse(A.is_model_cand({"sources": ["coverage_gap"], "sub_reasons": ["coverage_gap"]}))


class TestModelDeterministicSplit(unittest.TestCase):
    def test_source_of(self):
        self.assertEqual(cov.source_of("r3", "model"), "model_r3")
        self.assertEqual(cov.source_of("r5", "model"), "model_r5")
        self.assertEqual(cov.source_of("r3", "coverage_gap"), "coverage_gap")
        self.assertEqual(cov.source_of("r3", "negation_polarity_mismatch"), "deterministic")
        self.assertEqual(cov.source_of("r5", "unknown_unit_id"), "model_r5")

    def test_fabricated_quote_is_deterministic_and_counted_separately(self):
        def r3(label, ids):
            return {"unit_verdicts": [_item(i, "SUPPORTED", quotes=("ありもしない引用です",)) if i == "S1.1"
                                      else _item(i, "CANDIDATE", issue="x") for i in ids]}
        art = "# T" + chr(10) * 2 + "The plan was posted on July 13. It said 20% would be charged." + chr(10)
        res = _run2(FakeLLM(r3_fn=r3), "r3_only", art)
        c = next(m for m in res["candidates"] if m["unit_ids"] == ["S1.1"])
        self.assertEqual(c["sources"], ["deterministic"])
        a = res["audit"]
        self.assertEqual(a["n_model_candidates"] + a["n_deterministic_only_candidates"], a["n_union_candidates"])
        self.assertGreaterEqual(a["n_deterministic_only_candidates"], 1)

    def test_union_merges_sources_across_routes(self):
        sp = _split()
        by = {u["id"]: u for u in sp["units"]}
        d = cov._candidate(by["S1.1"], by, "r3", "negation_polarity_mismatch", "d", ZERO, "HF-001")
        m = cov._candidate(by["S1.1"], by, "r5", "model", "m", ZERO, "HF-001")
        merged = cov.union_candidates([d, m])
        self.assertEqual(len(merged), 1)
        self.assertEqual(sorted(merged[0]["sources"]), ["deterministic", "model_r5"])


class TestRunnerEffortAndSwitches(unittest.TestCase):
    def test_new_switch_defaults_unchanged(self):
        self.assertEqual(runner.STAGE1_R5_MODE, "full")
        self.assertEqual(runner.STAGE1_R3_REASONING, "high")
        self.assertEqual(runner.STAGE1_R5_REASONING, "high")
        self.assertEqual(runner.STAGE1_NEGATION_MODE, "legacy")
        self.assertEqual(runner.vfl01.REASONING_EFFORT, "high")
        for k in ("STAGE1_R5_MODE", "STAGE1_R3_REASONING", "STAGE1_R5_REASONING", "STAGE1_NEGATION_MODE"):
            self.assertNotIn(k, runner.KPI_TRIAL_SWITCHES)

    def test_effort_per_route_label(self):
        self.assertEqual(runner.stage1_effort_for_label("r3"), "high")
        with mock.patch.object(runner, "STAGE1_R3_REASONING", "medium"), mock.patch.object(runner, "STAGE1_R5_REASONING", "low"):
            self.assertEqual(runner.stage1_effort_for_label("r3"), "medium")
            self.assertEqual(runner.stage1_effort_for_label("r3_rerun"), "medium")
            self.assertEqual(runner.stage1_effort_for_label("r3_retry"), "medium")
            self.assertEqual(runner.stage1_effort_for_label("r5"), "low")
            self.assertEqual(runner.stage1_effort_for_label("r5v"), "low")
        with mock.patch.object(runner, "STAGE1_R5_REASONING", "bogus"), self.assertRaises(ValueError):
            runner.stage1_effort_for_label("r5v")

    def test_coverage_fresh_records_effort_and_passes_to_api(self):
        import json
        efforts = []

        class Resp:
            def __init__(self, t):
                self.output_text = t

        class Responses:
            def create(self, **kw):
                efforts.append((kw["text"]["format"]["name"], kw["reasoning"]["effort"]))
                if "r3" in kw["text"]["format"]["name"]:
                    ids = re.search(r"【判定必須の単位ID\(全\d+件\)】\n(.*)\n", kw["input"][1]["content"]).group(1).split(", ")
                    return Resp(json.dumps({"unit_verdicts": [_item(i, "SUPPORTED") if i == "S1.1" else _item(i, "CANDIDATE", issue="x")
                                                              for i in ids]}))
                return Resp(json.dumps({"facts": []}))

        class Client:
            responses = Responses()

        log = []
        with mock.patch.object(runner.s2p, "_extract_usage", lambda r: {"input_tokens": 1}), \
             mock.patch.object(runner.s2p, "official_cost_jpy", lambda u: 1.0), \
             mock.patch.object(runner, "save_budget_state", lambda s: None), \
             mock.patch.object(runner, "STAGE1_R3_REASONING", "medium"), \
             mock.patch.object(runner, "STAGE1_R5_REASONING", "low"), \
             mock.patch.object(runner, "STAGE1_R5_MODE", "verify_supported"):
            parsed = runner.stage1_coverage_fresh(Client(), _state0(), [0], log, "t11", {"ledger_text": LEDGER, "article_text": ARTICLE})
        self.assertEqual([e for _, e in efforts], ["medium", "low"])
        self.assertEqual([c["reasoning_effort"] for c in log], ["medium", "low"])
        self.assertEqual([c["label"] for c in log], ["t11_r3", "t11_r5v"])
        calls = parsed["stage1_coverage_audit"]["per_route"]
        self.assertEqual(calls["r3"]["calls"][0]["reasoning_effort"], "medium")
        self.assertEqual(calls["r5"]["calls"][0]["reasoning_effort"], "low")


class TestStageAScriptLoop2(unittest.TestCase):
    def test_plan_g_arm_and_estimate_modes_and_defaults(self):
        import er052_open233_stage1_stageA_01 as sa
        p = sa.plan_g_arm()
        self.assertEqual(len(p), 33)
        self.assertEqual(sum(1 for s, i in p if i in sa.SC_IDS), 18)
        self.assertEqual(sum(1 for s, i in p if i in sa.HOLDOUT_IDS), 9)
        self.assertEqual(sum(1 for s, i in p if i in sa.NORMAL_IDS), 6)
        insts = {i["instance_id"]: i for i in runner.build_target_instances()}
        hi = sa.estimate_cost_v2(insts, p, "full", "high", "high", None)["total_jpy_low_mid_high"]
        med = sa.estimate_cost_v2(insts, p, "verify_supported", "medium", "medium", None)["total_jpy_low_mid_high"]
        low = sa.estimate_cost_v2(insts, p, "verify_supported", "medium", "low", None)["total_jpy_low_mid_high"]
        self.assertTrue(med[1] < hi[1] and low[1] < med[1])
        self.assertEqual(len(sa.estimate_cost_v2(insts, p, "full", "high", "high", None)["rows"]), 33)

    def test_aggregate_has_model_vs_deterministic_and_worst_runs(self):
        import er052_open233_stage1_stageA_01 as sa
        agg = sa.aggregate([])
        self.assertIn("model_vs_deterministic", agg)
        self.assertIn("worst_runs", agg)
        self.assertIn("sc_union_3of3_by_M_all", agg["criteria_result"])


if __name__ == "__main__":
    unittest.main()
