# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_checker_floor_prod_wiring_test_01.py
# OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_04: 承認済み2点(Checker再分類4観点の正式採用/後段機械判定は数字のみ)の配線テスト。
# ネットワーク呼び出しなし(¥0、偽LLM/mockのみ)。PRODUCTION_WIRED判定ではない(E2E・runtime evidence後)。
# ============================================================
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import tempfile
import unittest
from unittest import mock

import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as cov
import er052_open233_stage1_reclassify_01 as reclf

ZERO = {k: False for k in cov.FLAG_KEYS}
LEDGER = """[VERIFIED] HF-001: 20％の償還料が7月13日に提案された。
  scope: ホルムズ海峡

[VERIFIED] HF-002: 徴収方法は示されなかった。
  scope: 償還料案
"""
BEFORE = """# Title Here

The plan was posted on July 13. It said 20% would be charged.

The post did not say how to collect it. So the plan left the stage.

Other paragraph has a plain sentence. And another plain sentence follows here.
"""
AFTER = BEFORE.replace("It said 20% would be charged.", "It said a fee would be charged.")
BEFORE_NR = BEFORE.replace("So the plan left the stage.", "The plan left the stage.").replace("did not say", "described")
AFTER_NR = AFTER.replace("So the plan left the stage.", "The plan left the stage.").replace("did not say", "described")

STATE_KEYS = tuple(runner.OPEN233_APPROVED_FLOW_SWITCHES) + ("BUDGET_STATE_PATH", "OUT_DIR", "TOTAL_BUDGET_JPY")


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


class RunnerStateMixin:
    """runner globalを各テストで保存/復元する(承認構成の適用がテスト間へ漏れない)。"""

    def setUp(self):
        self._saved = {k: getattr(runner, k) for k in STATE_KEYS if hasattr(runner, k)}
        self._tmp = tempfile.TemporaryDirectory()
        runner.BUDGET_STATE_PATH = os.path.join(self._tmp.name, "budget_state.json")

    def tearDown(self):
        for k, v in self._saved.items():
            setattr(runner, k, v)
        self._tmp.cleanup()


def _seg():
    return dict(segment_fn=runner.vs_sentence_segments_l6, initial_extra=runner.CAUSAL_SENTENCE_INITIAL_EN)


def cand(key, text, source="model_r3", route="r3", flags=None, related=("HF-001",), sub="model"):
    """合流前の経路別候補1件(cov._candidateと同形のdict)。"""
    f = dict(ZERO)
    f.update(flags or {})
    return {"unit_id": key, "unit_ids": [key] if key else [], "claim_text": text, "span": None, "routes": [route],
            "sub_reasons": [sub], "sources": [source], "issues": ["x"], "flags": f, "related_fact_ids": list(related),
            "model_claim": ""}


class ReclassFake:
    """再分類call用の偽call_fn。policy(cid, claim_text)->verdict。"""

    def __init__(self, policy=None, fail=False, drop_cids=(), bad_enum=()):
        self.policy, self.fail, self.drop, self.bad = policy or (lambda cid, t: "CANDIDATE"), fail, set(drop_cids), set(bad_enum)
        self.calls = []

    def __call__(self, label, developer, prompt, schema):
        self.calls.append({"label": label, "developer": developer, "prompt": prompt, "schema": schema})
        if self.fail:
            return None, {"cost_jpy": 0.0, "error": "fake"}
        rows = re.findall(r"\[(C\d+)\] \(旧Checkerの方向: [^)]*\) (.*)", prompt)
        res = []
        for cid, text in rows:
            if cid in self.drop:
                continue
            v = "WEIRD" if cid in self.bad else self.policy(cid, text)
            res.append({"cid": cid, "verdict": v, "fact_tags": ["none"], "actor_match": "n_a", "counterpart_match": "n_a",
                        "scope_match": "n_a", "qualifier_match": "n_a", "reason": "r"})
        return {"results": res}, {"cost_jpy": 0.25, "usage": {}}


class TestVerbatimTransplant(unittest.TestCase):
    """M3: prompt/DEVELOPER_MESSAGE/schemaをTrial script(正本)と逐語一致(sha256)で確認。"""

    @classmethod
    def setUpClass(cls):
        path = os.path.join("er052_output", "open233_reclassify_02", "reclassify_candidates_02.py")
        spec = importlib.util.spec_from_file_location("reclassify_candidates_02_trial", path)
        cls.trial = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.trial)

    def test_developer_message_sha256_identical(self):
        self.assertEqual(_sha(reclf.DEVELOPER_MESSAGE), _sha(self.trial.DEVELOPER_MESSAGE))

    def test_prompt_template_sha256_identical(self):
        self.assertEqual(_sha(reclf.PROMPT_TEMPLATE), _sha(self.trial.PROMPT_TEMPLATE))

    def test_schema_identical_and_has_four_match_fields(self):
        dump = lambda s: json.dumps(s, ensure_ascii=False, sort_keys=True)  # noqa: E731
        self.assertEqual(_sha(dump(reclf.SCHEMA)), _sha(dump(self.trial.SCHEMA)))
        props = reclf.SCHEMA["schema"]["properties"]["results"]["items"]["properties"]
        for k in ("actor_match", "counterpart_match", "scope_match", "qualifier_match"):
            self.assertIn(k, props)
        self.assertEqual(reclf.SCHEMA["name"], "open233_reclassify_verdicts_v2")

    def test_effort_and_model_same_as_trial(self):
        self.assertEqual(reclf.EFFORT, self.trial.EFFORT)
        self.assertEqual(reclf.EFFORT, "medium")
        self.assertEqual(runner.MODEL, self.trial.MODEL)
        self.assertEqual(runner.MODEL, "gpt-6-luna")

    def test_build_prompt_identical_to_trial_for_same_claims(self):
        fx = {"ledger_text": LEDGER, "article_text": BEFORE}
        cands = [cand("S1.2", "It said 20% would be charged."), cand("S2.1", "The post did not say.", route="r5", related=("HF-002",))]
        items, _ = reclf.claims_for_candidates(cands)
        trial_items = [{"cid": x["cid"], "claim_text": x["claim_text"], "routes": x["routes"], "related": x["related"]} for x in items]
        self.assertEqual(reclf.build_prompt(fx, items), self.trial.build_prompt(fx, trial_items))


class TestFilterBeforeUnion(unittest.TestCase):
    """M1: 再分類は合流前に効く。混在候補でモデル側のchanged_numberが決定論側保持で残らない。"""

    def test_model_changed_number_does_not_leak_into_union_when_excluded(self):
        model = cand("S1.2", "It said 20% would be charged.", flags={"changed_number": True})
        det = cand("S1.2", "It said 20% would be charged.", source="deterministic", sub="number_not_in_fact")
        fake = ReclassFake(policy=lambda cid, t: "SUPPORTED")
        kept, info = reclf.reclassify_candidates({"ledger_text": LEDGER, "article_text": BEFORE}, [model, det], fake)
        self.assertEqual(info["status"], "ok")
        self.assertEqual([c["sources"] for c in kept], [["deterministic"]])
        merged = cov.union_candidates(kept)
        self.assertEqual(len(merged), 1)
        self.assertFalse(merged[0]["flags"]["changed_number"])  # 合流後にfilterするとここがTrueのまま残る
        self.assertEqual((info["n_excluded_entries"], info["n_excluded_with_changed_number"]), (1, 1))
        # 対照: 合流後なら(旧順序)changed_numberは決定論側保持の候補へORされてしまう
        post = cov.union_candidates([model, det])
        self.assertTrue(post[0]["flags"]["changed_number"])

    def test_deterministic_and_coverage_gap_never_sent_or_dropped(self):
        det = cand("S1.1", "Det claim here.", source="deterministic", sub="causal_not_in_fact")
        gap = cand("S1.3", "Gap claim here.", source="coverage_gap", sub="coverage_gap")
        mod = cand("S1.2", "Model claim here.")
        fake = ReclassFake(policy=lambda cid, t: "NO_FACT_CLAIM")
        kept, info = reclf.reclassify_candidates({"ledger_text": LEDGER, "article_text": BEFORE}, [det, gap, mod], fake)
        self.assertEqual({c["sources"][0] for c in kept}, {"deterministic", "coverage_gap"})
        self.assertNotIn("Det claim here.", fake.calls[0]["prompt"])
        self.assertNotIn("Gap claim here.", fake.calls[0]["prompt"])
        self.assertEqual((info["n_targets"], info["n_excluded_claims"]), (1, 1))

    def test_candidate_verdict_keeps_entry_and_flags(self):
        mod = cand("S1.2", "It said 20% would be charged.", flags={"changed_number": True})
        kept, info = reclf.reclassify_candidates({"ledger_text": LEDGER, "article_text": BEFORE}, [mod], ReclassFake())
        self.assertEqual(len(kept), 1)
        self.assertTrue(kept[0]["flags"]["changed_number"])
        self.assertEqual(info["n_excluded_claims"], 0)

    def test_same_key_two_routes_one_claim_one_verdict_both_entries_dropped(self):
        a = cand("S1.2", "It said 20% would be charged.", route="r3")
        b = cand("S1.2", "It said 20% would be charged.", source="model_r5", route="r5")
        fake = ReclassFake(policy=lambda cid, t: "NO_FACT_CLAIM")
        kept, info = reclf.reclassify_candidates({"ledger_text": LEDGER, "article_text": BEFORE}, [a, b], fake)
        self.assertEqual(kept, [])
        self.assertEqual((info["n_targets"], info["n_excluded_entries"]), (1, 2))

    def test_no_target_makes_no_call(self):
        det = cand("S1.1", "Det.", source="deterministic")
        fake = ReclassFake()
        kept, info = reclf.reclassify_candidates({"ledger_text": LEDGER, "article_text": BEFORE}, [det], fake)
        self.assertEqual(fake.calls, [])
        self.assertEqual(info["status"], "no_target")
        self.assertEqual(kept, [det])

    def test_call_uses_fixed_developer_message_schema_and_label(self):
        fake = ReclassFake()
        reclf.reclassify_candidates({"ledger_text": LEDGER, "article_text": BEFORE}, [cand("S1.2", "A claim here.")], fake)
        c = fake.calls[0]
        self.assertEqual(c["label"], "reclassify")
        self.assertIs(c["schema"], reclf.SCHEMA)
        self.assertEqual(c["developer"], reclf.DEVELOPER_MESSAGE)


class TestFailClosed(unittest.TestCase):
    FX = {"ledger_text": LEDGER, "article_text": BEFORE}

    def _cands(self):
        return [cand("S1.2", "Claim number one here."), cand("S2.1", "Claim number two here.")]

    def test_call_failure_keeps_all_and_status_failed(self):
        kept, info = reclf.reclassify_candidates(self.FX, self._cands(), ReclassFake(fail=True))
        self.assertEqual(len(kept), 2)
        self.assertEqual((info["status"], info["n_failclosed"], info["n_excluded_claims"]), ("failed", 2, 0))
        self.assertEqual(len(info["calls"]), 2)  # 1回 + 再実行1回(H1)

    def test_call_exception_keeps_all(self):
        def boom(*a, **k):
            raise RuntimeError("x")
        kept, info = reclf.reclassify_candidates(self.FX, self._cands(), boom)
        self.assertEqual((len(kept), info["status"]), (2, "failed"))

    def test_trialabort_is_not_swallowed(self):
        def abort(*a, **k):
            raise runner.TrialAbort("budget")
        with self.assertRaises(runner.TrialAbort):
            reclf.reclassify_candidates(self.FX, self._cands(), abort)

    def test_missing_cid_kept_as_candidate_others_filtered(self):
        fake = ReclassFake(policy=lambda cid, t: "SUPPORTED", drop_cids={"C2"})
        kept, info = reclf.reclassify_candidates(self.FX, self._cands(), fake)
        self.assertEqual([c["claim_text"] for c in kept], ["Claim number two here."])
        self.assertEqual((info["status"], info["n_failclosed"], info["n_excluded_claims"]), ("ok", 1, 1))

    def test_out_of_enum_verdict_is_failclosed(self):
        fake = ReclassFake(policy=lambda cid, t: "SUPPORTED", bad_enum={"C1"})
        kept, info = reclf.reclassify_candidates(self.FX, self._cands(), fake)
        self.assertEqual([c["claim_text"] for c in kept], ["Claim number one here."])
        self.assertEqual(info["n_failclosed"], 1)

    def test_non_dict_result_is_failed(self):
        kept, info = reclf.reclassify_candidates(self.FX, self._cands(), lambda *a: ({"results": "x"}, {}))
        self.assertEqual((len(kept), info["status"]), (2, "failed"))


class CovFake:
    """coverage module用の偽call_fn(r3/r5v/reclassify)。r3候補を`cands`のIDで返し、`flags`を付ける。再分類はpolicyで返す。"""

    def __init__(self, cands=(), flags=None, policy=None, reclass_fail=False):
        self.cands, self.flags = set(cands), dict(ZERO, **(flags or {}))
        self.rc = ReclassFake(policy=policy, fail=reclass_fail)
        self.calls = []

    def __call__(self, label, developer, prompt, schema):
        self.calls.append(label)
        if schema is reclf.SCHEMA:
            return self.rc(label, developer, prompt, schema)
        meta = {"cost_jpy": 0.5, "usage": {}}
        if schema is cov.R3_JSON_SCHEMA:
            ids = re.search(r"【判定必須の単位ID\(全\d+件\)】\n(.*)\n", prompt).group(1).split(", ")
            return {"unit_verdicts": [
                {"unit_id": i, "verdict": "CANDIDATE" if i in self.cands else "SUPPORTED", "support_fact_ids": ["HF-001"],
                 "ledger_quotes": ["20％の償還料が7月13日に提案された"], "issue": "x" if i in self.cands else "",
                 "claim_in_article": "", "related_fact_id": "HF-001" if i in self.cands else "",
                 "flags": dict(self.flags) if i in self.cands else dict(ZERO)} for i in ids]}, meta
        fids = re.search(r"【factID一覧\(全\d+件\)】\n(.*)\n", prompt).group(1).split(", ")
        return {"facts": [{"fact_id": f, "matches": []} for f in fids]}, meta


PRIOR = [{"fact_id": "HF-001", "claim_in_article": "It said a fee would be charged.", "issue": "i", "explanation": "e"}]


class TestRecheckFilter(unittest.TestCase):
    """M1/M2: Recheckでは再分類後の候補でprior_issues_resolvedを計算。前回指摘と同文の候補は再分類対象外。"""

    def _fx(self, art):
        return {"ledger_text": LEDGER, "article_text": art}

    def test_excluded_candidate_resolves_prior_issue_when_not_same_text(self):
        # 前回指摘の文面が別文(S2.1側の指摘)で、今回S1.2に出た候補が再分類で除外されるなら、解消判定は候補なし=解消
        prior = [{"fact_id": "HF-009", "claim_in_article": "Totally different old sentence about fees.", "issue": "i", "explanation": "e"}]
        llm = CovFake(cands={"S1.2"}, policy=lambda cid, t: "SUPPORTED")
        flt = reclf.make_candidate_filter(self._fx(AFTER_NR), llm, protected_claims=[p["claim_in_article"] for p in prior])
        res = cov.run_recheck_scope(self._fx(AFTER_NR), llm, BEFORE_NR, prior, candidate_filter=flt, **_seg())
        self.assertTrue(res["prior_issues_resolved"][0]["resolved"])
        self.assertEqual(res["audit"]["candidate_filter"]["n_excluded_claims"], 1)
        self.assertEqual(res["candidates"], [])

    def test_same_text_as_prior_issue_is_protected_and_stays_unresolved(self):
        llm = CovFake(cands={"S1.2"}, policy=lambda cid, t: "SUPPORTED")  # 通常なら除外される判定
        flt = reclf.make_candidate_filter(self._fx(AFTER_NR), llm, protected_claims=[p["claim_in_article"] for p in PRIOR])
        res = cov.run_recheck_scope(self._fx(AFTER_NR), llm, BEFORE_NR, PRIOR, candidate_filter=flt, **_seg())
        self.assertFalse(res["prior_issues_resolved"][0]["resolved"])  # 同文候補は残る(Stage 2が再判定)
        self.assertEqual(len(res["candidates"]), 1)
        f = res["audit"]["candidate_filter"]
        self.assertEqual((f["n_protected_keys"], f["n_excluded_claims"]), (1, 0))
        self.assertNotIn("reclassify", llm.calls)  # 対象0件のためcallも発生しない

    def test_filter_none_is_identical_to_previous_behavior(self):
        a = cov.run_recheck_scope(self._fx(AFTER_NR), CovFake(cands={"S1.2"}), BEFORE_NR, PRIOR, **_seg())
        b = cov.run_recheck_scope(self._fx(AFTER_NR), CovFake(cands={"S1.2"}), BEFORE_NR, PRIOR, candidate_filter=None, **_seg())
        self.assertEqual(a["candidates"], b["candidates"])
        self.assertIsNone(a["audit"]["candidate_filter"])

    def test_reclassify_failure_keeps_candidates_failclosed(self):
        llm = CovFake(cands={"S1.2"}, reclass_fail=True)
        flt = reclf.make_candidate_filter(self._fx(AFTER_NR), llm, protected_claims=["Unrelated old sentence text."])
        res = cov.run_recheck_scope(self._fx(AFTER_NR), llm, BEFORE_NR, PRIOR, candidate_filter=flt, **_seg())
        self.assertEqual(len(res["candidates"]), 1)
        self.assertEqual(res["audit"]["candidate_filter"]["status"], "failed")

    def test_fact_id_unit_unresolved_rule_unchanged(self):
        # same_fact規則(別文でも同fact_idの候補は未解消)は変更しない。残存リスクとして記録済み。
        prior = [{"fact_id": "HF-001", "claim_in_article": "Totally different old sentence about fees.", "issue": "i", "explanation": "e"}]
        llm = CovFake(cands={"S1.2"}, policy=lambda cid, t: "CANDIDATE")
        flt = reclf.make_candidate_filter(self._fx(AFTER_NR), llm, protected_claims=["Totally different old sentence about fees."])
        res = cov.run_recheck_scope(self._fx(AFTER_NR), llm, BEFORE_NR, prior, candidate_filter=flt, **_seg())
        self.assertFalse(res["prior_issues_resolved"][0]["resolved"])


class TestInitialAndExitFilter(unittest.TestCase):
    def _fx(self, art):
        return {"ledger_text": LEDGER, "article_text": art}

    def test_initial_filter_applies_before_union_and_audit_keeps_raw_route_candidates(self):
        llm = CovFake(cands={"S1.2"}, flags={"changed_number": True}, policy=lambda cid, t: "SUPPORTED")
        flt = reclf.make_candidate_filter(self._fx(BEFORE_NR), llm)
        res = cov.run_stage1_coverage(self._fx(BEFORE_NR), llm, candidate_filter=flt, **_seg())
        self.assertEqual(res["candidates"], [])
        self.assertEqual(res["audit"]["n_union_candidates"], 0)
        self.assertEqual(len(res["audit"]["per_route"]["r3"]["candidates"]), 1)  # 経路別の生候補は監査用に残る
        self.assertEqual(res["audit"]["candidate_filter"]["n_excluded_with_changed_number"], 1)

    def test_initial_filter_default_none_is_identity(self):
        llm = CovFake(cands={"S1.2"})
        res = cov.run_stage1_coverage(self._fx(BEFORE_NR), llm, **_seg())
        self.assertEqual(len(res["candidates"]), 1)
        self.assertIsNone(res["audit"]["candidate_filter"])

    def test_api_failure_skips_filter(self):
        class Fail(CovFake):
            def __call__(self, label, developer, prompt, schema):
                if label.startswith("r3"):
                    return None, {"cost_jpy": 0.0, "error": "x"}
                return super().__call__(label, developer, prompt, schema)
        llm = Fail()
        flt = reclf.make_candidate_filter(self._fx(BEFORE_NR), llm)
        res = cov.run_stage1_coverage(self._fx(BEFORE_NR), llm, candidate_filter=flt, **_seg())
        self.assertTrue(res["api_failure"])
        self.assertNotIn("reclassify", llm.calls)

    def test_exit_filter_applies_and_protected_same_text_stays(self):
        llm = CovFake(cands={"S1.2"}, policy=lambda cid, t: "NO_FACT_CLAIM")
        flt = reclf.make_candidate_filter(self._fx(BEFORE_NR), llm)
        res = cov.run_exit_full_r3(self._fx(BEFORE_NR), llm, candidate_filter=flt, **_seg())
        self.assertEqual(res["candidates"], [])
        self.assertEqual(res["audit"]["candidate_filter"]["n_excluded_claims"], 1)
        llm2 = CovFake(cands={"S1.2"}, policy=lambda cid, t: "NO_FACT_CLAIM")
        flt2 = reclf.make_candidate_filter(self._fx(BEFORE_NR), llm2, protected_claims=["It said 20% would be charged."])
        res2 = cov.run_exit_full_r3(self._fx(BEFORE_NR), llm2, candidate_filter=flt2, **_seg())
        self.assertEqual(len(res2["candidates"]), 1)  # 前回指摘と同文=出口でも再分類対象外


class TestApprovedSwitches(RunnerStateMixin, unittest.TestCase):
    """M5: 承認構成の名前付き定数・適用関数・assert。globalの既定は旧挙動のまま。"""

    def test_defaults_remain_legacy_until_applied(self):
        self.assertEqual(runner.FLOOR_MODE, "legacy_5flags")
        self.assertEqual(runner.PRECHECK_MODE, "legacy_all")
        self.assertFalse(runner.STAGE1_RECLASSIFY)
        self.assertEqual(runner.KPI_TRIAL_SWITCHES["FLOOR_VERIFY_MODE"], "time_only")  # 旧仕様(SUPERSEDED注記付きで残置)
        self.assertTrue(runner.KPI_TRIAL_SWITCHES["CAUSAL_FLOOR"])

    def test_apply_sets_all_and_asserts(self):
        applied = runner.apply_open233_approved_flow_switches()
        self.assertEqual(applied, runner.OPEN233_APPROVED_FLOW_SWITCHES)
        for k, v in runner.OPEN233_APPROVED_FLOW_SWITCHES.items():
            self.assertEqual(getattr(runner, k), v, k)
        runner.assert_open233_approved_flow_switches()

    def test_required_values(self):
        s = runner.OPEN233_APPROVED_FLOW_SWITCHES
        self.assertEqual((s["FLOOR_MODE"], s["FLOOR_VERIFY_MODE"], s["PRECHECK_MODE"]), ("number_only", "off", "number_only"))
        self.assertIs(s["CAUSAL_FLOOR"], False)
        self.assertIs(s["STAGE2_DOWNGRADE_VERIFY"], False)   # Opus追加assert
        self.assertIs(s["TIER0_G_L_ENABLED"], False)         # Opus追加assert
        self.assertIs(s["STAGE1_RECLASSIFY"], True)
        self.assertIs(s["STAGE2_SECOND_OPINION"], True)      # S1は旧E2Eと同じ設定を維持(Fable判断)
        self.assertEqual((s["STAGE1_MODE"], s["RECHECK_MODE"]), ("coverage_union", "coverage_union"))
        self.assertEqual((s["MAX_CYCLES"], s["HARD_MAX_CYCLES"], s["MODEL"]), (2, 3, "gpt-6-luna"))

    def test_assert_fails_listing_each_mismatch(self):
        runner.apply_open233_approved_flow_switches()
        runner.CAUSAL_FLOOR = True
        runner.TIER0_G_L_ENABLED = True
        runner.STAGE2_DOWNGRADE_VERIFY = True
        with self.assertRaises(AssertionError) as cm:
            runner.assert_open233_approved_flow_switches()
        for k in ("CAUSAL_FLOOR", "TIER0_G_L_ENABLED", "STAGE2_DOWNGRADE_VERIFY"):
            self.assertIn(k, str(cm.exception))

    def test_assert_fails_on_legacy_defaults(self):
        with self.assertRaises(AssertionError):
            runner.assert_open233_approved_flow_switches()

    def test_apply_is_idempotent_and_json_serializable(self):
        a = runner.apply_open233_approved_flow_switches()
        b = runner.apply_open233_approved_flow_switches()
        self.assertEqual(a, b)
        json.dumps(a)

    def test_old_kpi_switches_untouched_and_marked_superseded(self):
        src = open("er052_open233_self_recovery_flow_runner_01.py", encoding="utf-8").read()
        self.assertIn("SUPERSEDED by OPEN233_APPROVED_FLOW_SWITCHES", src)
        runner.apply_open233_approved_flow_switches()
        self.assertEqual(runner.KPI_TRIAL_SWITCHES["FLOOR_VERIFY_MODE"], "time_only")


class TestFloorModes(RunnerStateMixin, unittest.TestCase):
    FLAGS = ("changed_actor", "changed_negation", "changed_comparison", "changed_time")

    def test_legacy_fires_on_all_five_flags(self):
        for k in self.FLAGS + ("changed_number",):
            self.assertEqual(runner.apply_floor("QUALITY", {k: True}, "stage1_llm"), ("BLOCKING", f"deterministic_floor:{k}"), k)

    def test_number_only_does_not_override_non_number_flags(self):
        runner.FLOOR_MODE = "number_only"
        for k in self.FLAGS + ("changed_causality", "changed_certainty", "changed_scope", "changed_fact"):
            self.assertEqual(runner.apply_floor("ACCEPTABLE", {k: True}, "stage1_llm"), ("ACCEPTABLE", None), k)

    def test_number_only_fires_on_number_alone_and_mixed(self):
        runner.FLOOR_MODE = "number_only"
        self.assertEqual(runner.apply_floor("QUALITY", {"changed_number": True}, "stage1_llm"),
                         ("BLOCKING", "deterministic_floor:changed_number"))
        self.assertEqual(runner.apply_floor("QUALITY", {"changed_number": True, "changed_actor": True, "changed_time": True}, "x"),
                         ("BLOCKING", "deterministic_floor:changed_number"))  # 理由は数字のみ

    def test_precheck_and_enumeration_duplicate_rules_unchanged(self):
        runner.FLOOR_MODE = "number_only"
        self.assertEqual(runner.apply_floor("ACCEPTABLE", {}, "precheck"), ("BLOCKING", "precheck_floor"))
        self.assertEqual(runner.apply_floor("QUALITY", {"changed_number": True, "detected_by_enumeration": True}, "x"), ("QUALITY", None))

    def test_invalid_floor_mode_raises(self):
        runner.FLOOR_MODE = "bogus"
        with self.assertRaises(ValueError):
            runner.apply_floor("QUALITY", {"changed_number": True}, "x")

    def test_floor_flags_constant_and_counterfactual_record_unchanged(self):
        self.assertEqual(runner.FLOOR_FLAGS, ["changed_actor", "changed_number", "changed_negation", "changed_comparison", "changed_time"])
        runner.FLOOR_MODE = "number_only"
        with mock.patch.object(runner, "floor_cited_eligible", return_value=True):  # 反実仮想(記録のみ)は旧5種のまま
            self.assertEqual(runner.apply_floor_cited("QUALITY", {"changed_actor": True}, "x", "(l)"),
                             ("BLOCKING", "deterministic_floor_cited:changed_actor"))

    def test_disclosure_gap_disqualifying_flags_explicit_and_unchanged(self):
        self.assertEqual(set(runner.DISCLOSURE_GAP_DISQUALIFYING_FLAGS), set(runner.FLOOR_FLAGS) | {"changed_scope"})

    def test_floor_verify_target_inactive_in_approved(self):
        runner.apply_open233_approved_flow_switches()
        t = runner.floor_verify_target("QUALITY", "deterministic_floor:changed_time", {"changed_time": True})
        self.assertEqual(t[:2], (False, "mode_off"))


class TestPrecheckNumberOnly(RunnerStateMixin, unittest.TestCase):
    KINDS = ("number_mismatch", "date_mismatch", "actor_missing", "negation_marker", "comparison_marker")

    def _findings(self):
        return [{"field": f"F-00{i}", "kind": k, "ledger_value": "v", "article_evidence": "e", "foreign_values": [3.0],
                 "detected_by": "precheck"} for i, k in enumerate(self.KINDS, 1)]

    def test_legacy_keeps_all_five(self):
        self.assertEqual([f["kind"] for f in runner.filter_precheck_findings(self._findings())], list(self.KINDS))

    def test_number_only_keeps_only_number_mismatch(self):
        runner.PRECHECK_MODE = "number_only"
        self.assertEqual([f["kind"] for f in runner.filter_precheck_findings(self._findings())], ["number_mismatch"])

    def test_invalid_mode_raises(self):
        runner.PRECHECK_MODE = "bogus"
        with self.assertRaises(ValueError):
            runner.filter_precheck_findings([])

    def test_build_claims_uses_the_one_filter_and_f3_shares_build(self):
        runner.PRECHECK_MODE = "number_only"
        fx = {"article_text": "# T\n\nResearchers studied more than 30 million payments last year.\n", "ledger_text": "(ledger)"}
        with mock.patch.object(runner.precheck, "run_precheck", return_value=self._findings()):
            claims = runner.build_precheck_floor_claims(fx, set())
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["related_fact_id"], "F-001")
        src = open("er052_open233_self_recovery_flow_runner_01.py", encoding="utf-8").read()
        self.assertEqual(src.count("build_precheck_floor_claims(fixture, set())"), 1)  # F3記録=同関数経由(別ロジックなし)

    def test_non_number_precheck_does_not_create_stage2_skip_claims_in_approved(self):
        runner.apply_open233_approved_flow_switches()
        fx = {"article_text": "# T\n\nSomeone did it.\n", "ledger_text": "(ledger)"}
        only_nonnum = [f for f in self._findings() if f["kind"] != "number_mismatch"]
        with mock.patch.object(runner.precheck, "run_precheck", return_value=only_nonnum):
            self.assertEqual(runner.build_precheck_floor_claims(fx, set()), [])

    def test_floor_reason_distinguishes_precheck_number_from_llm_number(self):
        runner.apply_open233_approved_flow_switches()
        self.assertEqual(runner.apply_floor("ACCEPTABLE", {}, "precheck")[1], "precheck_floor")  # (c) llm_materiality=None枠
        self.assertEqual(runner.apply_floor("ACCEPTABLE", {"changed_number": True}, "stage1_llm")[1],
                         "deterministic_floor:changed_number")  # (a)


_ST_LEDGER = (
    "[VERIFIED] HF-007: トランプ大統領は7月14日、20％の米国償還料を湾岸諸国との貿易・投資案件に置き換えると投稿した。\n"
    "  scope: 7月13日に提案した20％償還料\n"
    "  date_or_period: 2026-07-14\n"
    "  causal_strength: CAUSAL_STATED_BY_SOURCE\n"
    "  notes_for_writer: 7月14日の撤回の原因として記述しない。\n"
)
_ST_CLAIM = "Concerns continued on July 14. So the flashy 20% plan left the stage."


class TestRunStage2IntegrationApproved(RunnerStateMixin, unittest.TestCase):
    """承認構成でrun_stage2を通し、数字以外のフラグ付き候補がLLM判定のままBLOCKINGにならず、数字フラグだけBLOCKINGになることを確認。"""

    def _run(self, llm, **dev_kw):
        dev = {"severity": "MAJOR", "related_fact_id": "HF-007", "issue": "The claim overstates the Ledger.", "changed_fact": True}
        dev.update(dev_kw)
        article = ("# T\n\nIntro hook. It has two sentences, and a 2026 date.\n\nSecond paragraph has several sentences. "
                   f"It is a plain body paragraph. It keeps going.\n\n{_ST_CLAIM}\n\n## In one line\nSummary.\n")
        fixture = {"article_text": article, "ledger_text": _ST_LEDGER, "source_article_text": None}
        claims = [{"claim_text": _ST_CLAIM, "origin": "translation", "related_fact_id": "HF-007", "dev": dev, "detected_by": "stage1_llm"}]

        def fake(client, ledger_text, source, cl, rubric_text, model=None):
            return {"prompt_sha256": "d1", "parsed": {"judgments": [
                {"claim_index": 0, "materiality": llm, "basis": "none", "rewrite_kind": "none", "rewrite_hint": ""}]},
                    "model": "m", "response_id": "r", "usage": {}, "cost_jpy": 0.01, "elapsed_seconds": 0.01}
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        call_log = []
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner, "check_budget", lambda *a, **k: None), \
             mock.patch.object(runner.s2c, "run_stage2_batch_variant", fake):
            return runner.run_stage2(None, state, [0], call_log, "t04", fixture, claims)[0], call_log

    def test_non_number_flags_stay_llm_judgement_in_approved_config(self):
        runner.apply_open233_approved_flow_switches()
        for flag in ("changed_actor", "changed_negation", "changed_comparison", "changed_time", "changed_causality"):
            o, log = self._run("ACCEPTABLE", **{flag: True})
            self.assertEqual(o["materiality"], "ACCEPTABLE", flag)
            self.assertIsNone(o["floor_reason"], flag)
            self.assertNotIn("tier0", o)  # CAUSAL_FLOOR OFF: Tier 0因果floor/補助ベルトも不発
            self.assertEqual(len(log), 1)  # 追加call(verify/確認役)なし

    def test_actor_issue_text_aux_belt_does_not_fire_in_approved_config(self):
        runner.apply_open233_approved_flow_switches()
        o, _ = self._run("QUALITY", changed_actor=True, issue="The article identifies cargo carriers as the payers.")
        self.assertEqual((o["materiality"], o["floor_reason"]), ("QUALITY", None))

    def test_number_flag_blocks_via_deterministic_floor(self):
        runner.apply_open233_approved_flow_switches()
        o, log = self._run("QUALITY", changed_number=True)
        self.assertEqual(o["materiality"], "BLOCKING")
        self.assertEqual(o["floor_reason"], "deterministic_floor:changed_number")
        self.assertEqual(o["llm_materiality"], "QUALITY")  # AI判定との区別(floor_reasonで(a)と識別)
        self.assertEqual(len(log), 1)

    def test_llm_blocking_unchanged_by_approved_config(self):
        runner.apply_open233_approved_flow_switches()
        o, _ = self._run("BLOCKING", changed_actor=True)
        self.assertEqual((o["materiality"], o["floor_reason"]), ("BLOCKING", None))

    def test_legacy_default_still_forces_actor_flag_blocking(self):
        o, _ = self._run("ACCEPTABLE", changed_actor=True)
        self.assertEqual((o["materiality"], o["floor_reason"]), ("BLOCKING", "deterministic_floor:changed_actor"))


class _Resp:
    def __init__(self, text):
        self.output_text = text


class _FakeClient:
    def __init__(self):
        self.kw = []
        outer = self

        class _R:
            def create(self, **kw):
                outer.kw.append(kw)
                return _Resp(json.dumps({"results": []}))
        self.responses = _R()


class TestCallFnEffortFixed(RunnerStateMixin, unittest.TestCase):
    """M3: 再分類callはlabel依存にせずmodel=MODEL・effort=medium・recovery_stage=stage1_reclassifyを固定。"""

    def _call(self, **kw):
        client, log = _FakeClient(), []
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner, "check_budget", lambda *a, **k: None), \
             mock.patch.object(runner.s2p, "_extract_usage", return_value={"input_tokens": 10, "output_tokens": 5}):
            fn = runner.make_stage1_call_fn(client, state, [0], log, "L", **kw)
            parsed, meta = fn("reclassify", "dev", "prompt", reclf.SCHEMA)
        return client, log, parsed, meta

    def test_override_pins_medium_even_when_r5_effort_is_high(self):
        runner.STAGE1_R5_REASONING = "high"
        runner.STAGE1_R3_REASONING = "high"
        client, log, parsed, meta = self._call(recovery_stage=reclf.RECOVERY_STAGE, effort_override=reclf.EFFORT)
        self.assertEqual(client.kw[0]["reasoning"], {"effort": "medium"})
        self.assertEqual(client.kw[0]["model"], runner.MODEL)
        self.assertEqual((log[0]["recovery_stage"], log[0]["reasoning_effort"], log[0]["label"]), ("stage1_reclassify", "medium", "L_reclassify"))
        self.assertEqual(parsed, {"results": []})

    def test_without_override_label_rule_gives_r5_effort(self):
        runner.STAGE1_R5_REASONING = "high"
        client, _, _, _ = self._call()
        self.assertEqual(client.kw[0]["reasoning"], {"effort": runner.vfl01.REASONING_EFFORT})  # 旧挙動(label依存)は不変

    def test_invalid_override_raises(self):
        with self.assertRaises(ValueError):
            self._call(effort_override="ultra")


class TestEntryWiring(RunnerStateMixin, unittest.TestCase):
    """M1: 初回/Recheck/出口の3入口が同じ`make_reclassify_filter`を合流前filterとして渡す。OFFでは従来と同一(None)。"""

    CALL = {"candidates": [], "api_failure": False, "failed_routes": [], "audit": {"candidate_filter": {"status": "no_target", "cost_jpy": 0.0}}}

    def _args(self):
        return (None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}, [0], [], "L")

    def test_initial_off_passes_none_on_passes_callable_and_records_summary(self):
        fx = {"ledger_text": LEDGER, "article_text": BEFORE}
        with mock.patch.object(runner.cov, "run_stage1_coverage", return_value=dict(self.CALL)) as m:
            parsed = runner.stage1_coverage_fresh(*self._args(), fx)
            self.assertIsNone(m.call_args.kwargs["candidate_filter"])
            self.assertNotIn("stage1_reclassify", parsed)
            runner.STAGE1_RECLASSIFY = True
            parsed = runner.stage1_coverage_fresh(*self._args(), fx)
            self.assertTrue(callable(m.call_args.kwargs["candidate_filter"]))
            self.assertEqual(parsed["stage1_reclassify"]["reclassify_status"], "no_target")

    def test_recheck_and_exit_pass_filter_and_protect_prior_claims(self):
        fx = {"ledger_text": LEDGER, "article_text": BEFORE}
        runner.STAGE1_RECLASSIFY = True
        seen = {}
        with mock.patch.object(runner.reclf, "reclassify_candidates", side_effect=lambda f, c, fn, prot=(): seen.update(prot=list(prot)) or (c, {})):
            rc = dict(self.CALL, prior_issues_resolved=[])
            with mock.patch.object(runner.cov, "run_recheck_scope", return_value=rc) as m:
                runner.run_recheck_coverage(*self._args(), fx, AFTER, [{"fact_id": "F", "claim_in_article": "Old flagged sentence here."}], BEFORE)
                flt = m.call_args.kwargs["candidate_filter"]
            flt([])
            self.assertEqual(seen["prot"], ["Old flagged sentence here."])
            with mock.patch.object(runner.cov, "run_exit_full_r3", return_value=dict(self.CALL)) as m2:
                runner.run_exit_check_coverage(*self._args(), fx, AFTER, protected_claims=["Earlier flagged."])
                flt2 = m2.call_args.kwargs["candidate_filter"]
            flt2([])
            self.assertEqual(seen["prot"], ["Earlier flagged."])

    def test_off_recheck_and_exit_pass_none(self):
        fx = {"ledger_text": LEDGER, "article_text": BEFORE}
        with mock.patch.object(runner.cov, "run_recheck_scope", return_value=dict(self.CALL, prior_issues_resolved=[])) as m, \
             mock.patch.object(runner.cov, "run_exit_full_r3", return_value=dict(self.CALL)) as m2:
            runner.run_recheck_coverage(*self._args(), fx, AFTER, [], BEFORE)
            runner.run_exit_check_coverage(*self._args(), fx, AFTER)
        self.assertIsNone(m.call_args.kwargs["candidate_filter"])
        self.assertIsNone(m2.call_args.kwargs["candidate_filter"])

    def test_static_every_stage1_entry_passes_filter_and_floor_has_single_call_site(self):
        with open("er052_open233_self_recovery_flow_runner_01.py", encoding="utf-8") as fh:
            src = fh.read()
        for fn in ("run_stage1_coverage", "run_recheck_scope", "run_exit_full_r3"):
            calls = re.findall(r"cov\.%s\((.*?)\n\n" % fn, src, re.S)
            self.assertEqual(len(calls), 1, fn)
            self.assertIn("candidate_filter=make_reclassify_filter(", calls[0], fn)
        self.assertEqual(len(re.findall(r"= apply_floor\(", src)), 1)  # floor適用は`_run_stage2_group`1箇所(初回/Recheck/出口/retry/次cycle共通)
        self.assertEqual(src.count("reclf.make_candidate_filter("), 1)  # 再分類filterの生成は1箇所

if __name__ == "__main__":
    unittest.main()
