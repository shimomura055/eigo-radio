# ============================================================
# er002_test_editorial.py
# ER-002-v1.1A-I1: 編集工程(アングル→Brief→台本→編集品質検品)のテスト
# ============================================================
# 実API・実TTS・実QA・新規トピック取得は一切行わない。すべてモックのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er002_test_editorial -v

import json
import unittest

import er002_common as common
import er002_editorial_angle_adapter as angle_adapter
import er002_editorial_common as ec
import er002_editorial_runner as runner
import er002_script_adapter as script_adapter
import er002_v1_1a_freeze as freeze_v1_1a
import er002_v1_freeze as freeze_v1
from er002_test_common import make_script, make_word_text


# ============================================================
# 共通フィクスチャ
# ============================================================
def make_fact_id_map(n=5):
    facts = [f"Fact number {i} happened." for i in range(1, n + 1)]
    return ec.assign_fact_ids(facts), facts


def make_candidate(angle_id, tension, role1, role2, claim1, claim2, takeaway,
                    opening_mode="verified_event", opening_fact_ids=("F01",),
                    hyp_required=False, article_id="a01"):
    return {
        "angle_id": angle_id, "article_id": article_id,
        "listener_relevance": "relevance text",
        "central_tension_or_question": tension,
        "concrete_opening": "opening text",
        "opening_mode": opening_mode,
        "opening_fact_ids": list(opening_fact_ids),
        "hypothetical_disclosure_required": hyp_required,
        "non_obvious_takeaway": takeaway,
        "point_one_editorial_role": role1, "point_one_core_claim": claim1, "point_one_fact_ids": ["F02"],
        "point_two_editorial_role": role2, "point_two_core_claim": claim2, "point_two_fact_ids": ["F03"],
        "listener_payoff": "payoff text", "in_one_line_target": "target text",
        "fact_support_map": [
            {"fact_id": "F01", "used_for": "opening"},
            {"fact_id": "F02", "used_for": "point_one"},
            {"fact_id": "F03", "used_for": "point_two"},
        ],
        "unsupported_assumptions": [],
    }


def make_angle_score_entry():
    return {
        "scores": {f: (5 if f == "fact_groundedness" else 4) for f in ec.ANGLE_SCORING_FIELDS},
        "evidence": {f: "evidence text" for f in ec.ANGLE_SCORING_FIELDS},
        "forced_disqualification_reasons": [],
        "unsupported_assumptions_detected": False,
        "fact_id_reference_valid": True,
    }


def make_passing_editorial_quality_response(overrides=None):
    base = {
        "brief_alignment": True, "opening_is_specific": True, "opening_is_grounded": True,
        "hypothetical_is_disclosed": None, "central_tension_present": True,
        "point_one_role_fulfilled": True, "point_two_role_fulfilled": True,
        "point_claims_are_distinct": True, "point_redundancy_detected": False,
        "narrative_coherence_present": True, "fact_enumeration_dominates": False,
        "non_obvious_takeaway_landed": True, "listener_payoff_present": True,
        "ungrounded_claims": [], "claim_strength_changed": [], "overstatement_or_dramatization": False,
        "overall_status": "pass", "evidence": "everything checks out",
    }
    base.update(overrides or {})
    return base


def make_valid_script(body_words=290, sub1_words=30, sub2_words=30, final_words=20):
    return make_script(body_words=body_words, sub1_words=sub1_words, sub2_words=sub2_words, final_words=final_words)


def make_valid_brief():
    return {
        "central_tension_or_question": "q", "opening_mode": "verified_event", "concrete_opening": "o",
        "opening_fact_ids": ["F01"], "hypothetical_disclosure_required": False,
        "point_one_editorial_role": "cause_explanation", "point_one_core_claim": "c1",
        "point_one_fact_ids": ["F02"],
        "point_two_editorial_role": "consequence_or_stakes", "point_two_core_claim": "c2",
        "point_two_fact_ids": ["F03"],
        "non_obvious_takeaway": "t", "listener_payoff": "p", "in_one_line_target": "target",
        "fact_support_map": [{"fact_id": "F01", "used_for": "x"}],
    }


# ============================================================
# 要求1: 3案のcentral tensionが同義なら全体を不合格にできる
# (完全一致ではなく実質的な同義 = LLMのdiversity_passedで判定)
# ============================================================
class DiversityCheckTests(unittest.TestCase):
    def test_llm_diversity_check_can_fail_synonymous_tensions(self):
        fact_ids, _facts = make_fact_id_map()
        valid_ids = set(fact_ids.keys())
        c1 = make_candidate("angle_1", "Why did the team win?", "cause_explanation",
                             "consequence_or_stakes", "c1a", "c1b", "t1")
        c2 = make_candidate("angle_2", "What caused the team's victory?", "human_or_concrete_detail",
                             "context_or_comparison", "c2a", "c2b", "t2")
        c3 = make_candidate("angle_3", "How did the win happen?", "counterpoint_or_tension",
                             "mechanism_or_process", "c3a", "c3b", "t3")
        raw_eval = {
            "diversity_passed": False,
            "diversity_evidence": "All three ask essentially the same causal question about the win.",
            "candidates": {},
        }
        result = ec.classify_angle_evaluation(raw_eval, [c1, c2, c3], valid_ids)
        self.assertEqual(result.status, "diversity_failed")
        self.assertIsNone(result.selected_angle_id)

    def test_exact_duplicate_tension_caught_by_rule_based_prescreen(self):
        c1 = make_candidate("angle_1", "same tension text", "cause_explanation", "consequence_or_stakes",
                             "c1a", "c1b", "t1")
        c2 = make_candidate("angle_2", "same tension text", "human_or_concrete_detail",
                             "context_or_comparison", "c2a", "c2b", "t2")
        errors = ec.rule_based_diversity_prescreen([c1, c2])
        self.assertTrue(any("central_tension" in e for e in errors))


# ============================================================
# 要求2: role enumが異なってもcore claimが同じなら不合格になる
# ============================================================
class RoleClaimDistinctnessTests(unittest.TestCase):
    def test_same_core_claim_fails_even_with_different_roles(self):
        fact_ids, _ = make_fact_id_map()
        c = make_candidate("angle_1", "t", "cause_explanation", "consequence_or_stakes",
                            "identical claim text", "identical claim text", "takeaway")
        errors = ec.validate_candidate_structure(c, set(fact_ids.keys()))
        self.assertTrue(any("core_claim" in e for e in errors))

    def test_different_role_and_different_claim_passes(self):
        fact_ids, _ = make_fact_id_map()
        c = make_candidate("angle_1", "t", "cause_explanation", "consequence_or_stakes",
                            "claim about cause", "claim about consequence", "takeaway")
        errors = ec.validate_candidate_structure(c, set(fact_ids.keys()))
        self.assertEqual(errors, [])


# ============================================================
# 要求3: 存在しないfact IDを不合格にできる
# ============================================================
class FactIdValidationTests(unittest.TestCase):
    def test_nonexistent_fact_id_rejected(self):
        fact_ids, _ = make_fact_id_map()
        c = make_candidate("angle_1", "t", "cause_explanation", "consequence_or_stakes",
                            "c1", "c2", "takeaway", opening_fact_ids=("F99",))
        errors = ec.validate_candidate_structure(c, set(fact_ids.keys()))
        self.assertTrue(any("F99" in e for e in errors))

    def test_empty_point_fact_ids_rejected(self):
        fact_ids, _ = make_fact_id_map()
        c = make_candidate("angle_1", "t", "cause_explanation", "consequence_or_stakes", "c1", "c2", "takeaway")
        c["point_one_fact_ids"] = []
        errors = ec.validate_candidate_structure(c, set(fact_ids.keys()))
        self.assertTrue(any("point_one_fact_ids" in e for e in errors))

    def test_empty_opening_fact_ids_allowed_for_hypothetical(self):
        fact_ids, _ = make_fact_id_map()
        c = make_candidate("angle_1", "t", "cause_explanation", "consequence_or_stakes", "c1", "c2", "takeaway",
                            opening_mode="hypothetical", opening_fact_ids=(), hyp_required=True)
        errors = ec.validate_candidate_structure(c, set(fact_ids.keys()))
        self.assertEqual(errors, [])

    def test_empty_opening_fact_ids_rejected_for_verified_event(self):
        fact_ids, _ = make_fact_id_map()
        c = make_candidate("angle_1", "t", "cause_explanation", "consequence_or_stakes", "c1", "c2", "takeaway",
                            opening_mode="verified_event", opening_fact_ids=())
        errors = ec.validate_candidate_structure(c, set(fact_ids.keys()))
        self.assertTrue(any("opening_fact_ids" in e for e in errors))


# ============================================================
# 要求4: hypothetical openingで仮定表示がない台本を不合格にできる
# ============================================================
class HypotheticalDisclosureTests(unittest.TestCase):
    def test_hypothetical_without_disclosure_fails_quality_check(self):
        response = make_passing_editorial_quality_response({
            "hypothetical_is_disclosed": False, "overall_status": "fail",
        })

        def qa_fn(prompt):
            return json.dumps(response)

        outcome = ec.evaluate_editorial_quality("prompt", qa_fn, max_eval_attempts=1)
        self.assertEqual(outcome.final_outcome, "conclusive_fail")
        self.assertIn("hypothetical_is_disclosed_false", outcome.reasons)

    def test_non_hypothetical_null_disclosure_is_acceptable(self):
        response = make_passing_editorial_quality_response({"hypothetical_is_disclosed": None})

        def qa_fn(prompt):
            return json.dumps(response)

        outcome = ec.evaluate_editorial_quality("prompt", qa_fn, max_eval_attempts=1)
        self.assertEqual(outcome.final_outcome, "passed")


# ============================================================
# 要求5: 評価点数にevidenceがなければ判定不能になる
# ============================================================
class AngleEvidenceRequiredTests(unittest.TestCase):
    def test_missing_evidence_raises_inconclusive(self):
        fact_ids, _ = make_fact_id_map()
        c1 = make_candidate("angle_1", "t1", "cause_explanation", "consequence_or_stakes", "c1a", "c1b", "ta")
        raw_eval = {
            "diversity_passed": True, "diversity_evidence": "distinct",
            "candidates": {"angle_1": {
                "scores": {f: 4 for f in ec.ANGLE_SCORING_FIELDS}, "evidence": {},
                "forced_disqualification_reasons": [], "unsupported_assumptions_detected": False,
                "fact_id_reference_valid": True,
            }},
        }
        with self.assertRaises(ec.AngleEvaluationInconclusive):
            ec.classify_angle_evaluation(raw_eval, [c1], set(fact_ids.keys()))

    def test_partial_evidence_also_raises_inconclusive(self):
        fact_ids, _ = make_fact_id_map()
        c1 = make_candidate("angle_1", "t1", "cause_explanation", "consequence_or_stakes", "c1a", "c1b", "ta")
        entry = make_angle_score_entry()
        del entry["evidence"]["fact_groundedness"]  # 1項目だけ欠落
        raw_eval = {
            "diversity_passed": True, "diversity_evidence": "distinct",
            "candidates": {"angle_1": entry},
        }
        with self.assertRaises(ec.AngleEvaluationInconclusive):
            ec.classify_angle_evaluation(raw_eval, [c1], set(fact_ids.keys()))

    def test_complete_evidence_does_not_raise(self):
        fact_ids, _ = make_fact_id_map()
        c1 = make_candidate("angle_1", "t1", "cause_explanation", "consequence_or_stakes", "c1a", "c1b", "ta")
        raw_eval = {
            "diversity_passed": True, "diversity_evidence": "distinct",
            "candidates": {"angle_1": make_angle_score_entry()},
        }
        result = ec.classify_angle_evaluation(raw_eval, [c1], set(fact_ids.keys()))
        self.assertEqual(result.status, "selected")


# ============================================================
# 要求6・7: 全台本が必ず編集品質検品を通る/ルールベース診断が
# 正常でもLLM検品を省略しない
# ============================================================
class MandatoryQualityCheckTests(unittest.TestCase):
    def test_quality_check_always_invoked_even_when_heuristic_clean(self):
        """ルールベースの診断(detect_claim_strength_escalation_heuristic)が
        「問題なし」でも、LLM編集品質検品(quality_call_fn)は必ず呼ばれる
        ことを確認する。"""
        facts_text = "The setting is optional and can be turned off."
        script_text = "The setting is optional and users may turn it off."  # 誇張なし
        heuristic_findings = ec.detect_claim_strength_escalation_heuristic(facts_text, script_text)
        self.assertEqual(heuristic_findings, [], "この検証の前提: ヒューリスティックは異常なしと判定するケース")

        calls = {"n": 0}
        script = make_valid_script()
        brief = make_valid_brief()

        def script_write_fn(config):
            return script

        def quality_call_fn(prompt):
            calls["n"] += 1
            return json.dumps(make_passing_editorial_quality_response())

        stage = runner.run_script_stage_with_quality_gate(
            script_write_fn, brief, ec.build_editorial_quality_prompt, quality_call_fn)
        self.assertEqual(stage.status, "OK")
        self.assertGreaterEqual(calls["n"], 1, "ヒューリスティックが清浄でもLLM検品を省略してはいけない")


# ============================================================
# 要求8・9: 主張強度エスカレーションの共通検出
# ============================================================
class ClaimStrengthEscalationTests(unittest.TestCase):
    def test_heuristic_detects_proposed_to_decided(self):
        findings = ec.detect_claim_strength_escalation_heuristic(
            "The policy was proposed by the government.",
            "The government has decided and finalized the policy.",
        )
        categories = [f["category"] for f in findings]
        self.assertIn("certainty_status", categories)

    def test_heuristic_detects_optional_to_mandatory(self):
        """A02の実例(default/optionalな設定がmandatoryへ強められる)を、
        A02専用のハードコードではなく共通検出器のテストケースとして使う。"""
        findings = ec.detect_claim_strength_escalation_heuristic(
            "The curfew is a default setting that teenagers can override.",
            "The curfew is mandatory and cannot be overridden by teenagers.",
        )
        categories = [f["category"] for f in findings]
        self.assertIn("obligation_scope", categories)

    def test_llm_claim_strength_changed_causes_conclusive_fail(self):
        response = make_passing_editorial_quality_response({
            "claim_strength_changed": [
                {"category": "obligation_scope", "original": "default/optional", "escalated_to": "mandatory"}
            ],
            "overall_status": "fail",
        })

        def qa_fn(prompt):
            return json.dumps(response)

        outcome = ec.evaluate_editorial_quality("prompt", qa_fn, max_eval_attempts=1)
        self.assertEqual(outcome.final_outcome, "conclusive_fail")
        self.assertIn("claim_strength_changed_present", outcome.reasons)

    def test_taxonomy_is_generic_not_a02_specific(self):
        """スキーマが記事非依存であることの確認(A02固有語がプロダクション
        taxonomyへハードコードされていないこと)。"""
        taxonomy_text = json.dumps(ec.CLAIM_STRENGTH_ESCALATION_TAXONOMY)
        for banned in ("16-year-old", "17-year-old", "curfew", "UK government"):
            self.assertNotIn(banned, taxonomy_text)


# ============================================================
# 要求10: Pointの役割未達を不合格にできる
# ============================================================
class PointRoleFulfillmentTests(unittest.TestCase):
    def test_point_one_role_not_fulfilled_fails(self):
        response = make_passing_editorial_quality_response({
            "point_one_role_fulfilled": False, "overall_status": "fail",
        })

        def qa_fn(prompt):
            return json.dumps(response)

        outcome = ec.evaluate_editorial_quality("prompt", qa_fn, max_eval_attempts=1)
        self.assertEqual(outcome.final_outcome, "conclusive_fail")
        self.assertIn("point_one_role_fulfilled", outcome.reasons)


# ============================================================
# 要求11: 事実羅列が主体の台本を不合格にできる
# ============================================================
class FactEnumerationTests(unittest.TestCase):
    def test_fact_enumeration_dominates_fails(self):
        response = make_passing_editorial_quality_response({
            "fact_enumeration_dominates": True, "narrative_coherence_present": False,
            "overall_status": "fail",
        })

        def qa_fn(prompt):
            return json.dumps(response)

        outcome = ec.evaluate_editorial_quality("prompt", qa_fn, max_eval_attempts=1)
        self.assertEqual(outcome.final_outcome, "conclusive_fail")
        self.assertIn("fact_enumeration_dominates", outcome.reasons)


# ============================================================
# 要求12・13: 解析不能時のみ再評価/確定的不合格は再評価しない
# ============================================================
class EditorialQualityRetryTests(unittest.TestCase):
    def test_parse_failure_triggers_reevaluation_same_script(self):
        calls = {"n": 0}

        def qa_fn(prompt):
            calls["n"] += 1
            if calls["n"] == 1:
                return "not valid json"
            return json.dumps(make_passing_editorial_quality_response())

        outcome = ec.evaluate_editorial_quality("prompt", qa_fn, max_eval_attempts=2)
        self.assertEqual(outcome.final_outcome, "passed")
        self.assertEqual(len(outcome.attempts), 2)
        self.assertEqual(calls["n"], 2)

    def test_conclusive_fail_does_not_reevaluate(self):
        calls = {"n": 0}

        def qa_fn(prompt):
            calls["n"] += 1
            return json.dumps(make_passing_editorial_quality_response({
                "point_redundancy_detected": True, "overall_status": "fail",
            }))

        outcome = ec.evaluate_editorial_quality("prompt", qa_fn, max_eval_attempts=2)
        self.assertEqual(outcome.final_outcome, "conclusive_fail")
        self.assertEqual(calls["n"], 1, "確定的な不合格は再評価しない")

    def test_both_inconclusive_after_max_attempts(self):
        def qa_fn(prompt):
            return "still not json"

        outcome = ec.evaluate_editorial_quality("prompt", qa_fn, max_eval_attempts=2)
        self.assertEqual(outcome.final_outcome, "inconclusive")
        self.assertEqual(len(outcome.attempts), 2)


# ============================================================
# 要求14: 2台本とも不合格ならTTS関数が呼ばれない
# ============================================================
class PipelineTtsGatingTests(unittest.TestCase):
    def _make_passing_angle_generation_fn(self, fact_ids):
        def angle_generation_fn(config):
            return [
                make_candidate("angle_1", "tension one", "cause_explanation", "consequence_or_stakes",
                                "claim1a", "claim1b", "takeaway1"),
                make_candidate("angle_2", "tension two", "human_or_concrete_detail", "context_or_comparison",
                                "claim2a", "claim2b", "takeaway2"),
                make_candidate("angle_3", "tension three", "counterpoint_or_tension", "mechanism_or_process",
                                "claim3a", "claim3b", "takeaway3"),
            ]
        return angle_generation_fn

    def _make_passing_angle_eval_call_fn(self):
        def angle_eval_call_fn(prompt):
            return json.dumps({
                "diversity_passed": True, "diversity_evidence": "distinct",
                "candidates": {
                    "angle_1": make_angle_score_entry(),
                    "angle_2": make_angle_score_entry(),
                    "angle_3": make_angle_score_entry(),
                },
            })
        return angle_eval_call_fn

    def _make_passing_brief_inspection_call_fn(self):
        def brief_inspection_call_fn(prompt):
            return json.dumps({
                "schema_valid": True, "fact_ids_valid": True, "roles_distinct": True,
                "claims_distinct": True, "overall_status": "pass", "evidence": "ok",
            })
        return brief_inspection_call_fn

    def test_tts_not_called_when_both_script_attempts_fail(self):
        fact_ids, _ = make_fact_id_map()
        tts_calls = {"n": 0}

        def tts_call_fn(script):
            tts_calls["n"] += 1

        def script_write_fn_factory(brief):
            def script_write_fn(config):
                return make_valid_script()
            return script_write_fn

        def quality_call_fn(prompt):
            return json.dumps(make_passing_editorial_quality_response({
                "point_redundancy_detected": True, "overall_status": "fail",
            }))

        outcome = runner.run_editorial_article_pipeline(
            article_id="a01",
            angle_generation_fn=self._make_passing_angle_generation_fn(fact_ids),
            angle_eval_call_fn=self._make_passing_angle_eval_call_fn(),
            angle_eval_prompt_builder=lambda candidates: ec.build_angle_evaluation_prompt(candidates, set(fact_ids.keys())),
            brief_inspection_call_fn=self._make_passing_brief_inspection_call_fn(),
            brief_inspection_prompt_builder=ec.build_brief_inspection_prompt,
            script_write_fn_factory=script_write_fn_factory,
            quality_prompt_builder=ec.build_editorial_quality_prompt,
            quality_call_fn=quality_call_fn,
            valid_fact_ids=set(fact_ids.keys()),
            tts_call_fn=tts_call_fn,
        )
        self.assertEqual(outcome.status, "FAILED_SCRIPT_STAGE")
        self.assertEqual(tts_calls["n"], 0, "台本が確定しない限りTTS関数を呼んではいけない")
        self.assertEqual(len(outcome.script_stage.attempts), 2)

    def test_tts_called_when_pipeline_succeeds(self):
        """対照実験: 台本が通れば(tts_call_fnを渡している場合)実際に呼ばれることを確認する
        (これは「呼ばれない」テストの妥当性を裏付けるための対照)。"""
        fact_ids, _ = make_fact_id_map()
        tts_calls = {"n": 0}

        def tts_call_fn(script):
            tts_calls["n"] += 1

        def script_write_fn_factory(brief):
            def script_write_fn(config):
                return make_valid_script()
            return script_write_fn

        def quality_call_fn(prompt):
            return json.dumps(make_passing_editorial_quality_response())

        outcome = runner.run_editorial_article_pipeline(
            article_id="a01",
            angle_generation_fn=self._make_passing_angle_generation_fn(fact_ids),
            angle_eval_call_fn=self._make_passing_angle_eval_call_fn(),
            angle_eval_prompt_builder=lambda candidates: ec.build_angle_evaluation_prompt(candidates, set(fact_ids.keys())),
            brief_inspection_call_fn=self._make_passing_brief_inspection_call_fn(),
            brief_inspection_prompt_builder=ec.build_brief_inspection_prompt,
            script_write_fn_factory=script_write_fn_factory,
            quality_prompt_builder=ec.build_editorial_quality_prompt,
            quality_call_fn=quality_call_fn,
            valid_fact_ids=set(fact_ids.keys()),
            tts_call_fn=tts_call_fn,
        )
        self.assertEqual(outcome.status, "OK")
        self.assertEqual(tts_calls["n"], 1)


# ============================================================
# 要求15: v1.0の凍結ファイルが変更されない
# ============================================================
class V1_0_UntouchedTests(unittest.TestCase):
    V1_0_PATH = "er002_output/_experiment_config/ER-002-v1.0_frozen_conditions.json"

    def test_v1_0_file_unchanged_after_v1_1a_operations(self):
        import hashlib
        with open(self.V1_0_PATH, "rb") as f:
            before = f.read()
        before_sha = hashlib.sha256(before).hexdigest()

        # v1.1A側の代表的な操作を一通り実行する
        _ = freeze_v1_1a.build_frozen_conditions()
        _ = script_adapter.build_prompt_v1_1a(
            "topic", {"F01": "fact"},
            make_valid_brief(),
        )
        fact_ids, _ = make_fact_id_map()
        _ = ec.build_angle_evaluation_prompt(
            [make_candidate("angle_1", "t", "cause_explanation", "consequence_or_stakes", "c1", "c2", "ta")],
            set(fact_ids.keys()))

        with open(self.V1_0_PATH, "rb") as f:
            after = f.read()
        self.assertEqual(before, after)
        self.assertEqual(hashlib.sha256(after).hexdigest(), before_sha)

    def test_v1_0_prompt_templates_unchanged(self):
        """v1.0が参照するプロンプトテンプレート文字列そのもの(COMMON_SCRIPT_
        PROMPT_TEMPLATE等)がv1.1Aのモジュール読み込み後もハッシュ不変で
        あることを確認する。"""
        v1_frozen = freeze_v1.build_frozen_conditions()
        self.assertEqual(
            v1_frozen["script_generation_prompt"]["sha256"],
            script_adapter.sha256_text(script_adapter.COMMON_SCRIPT_PROMPT_TEMPLATE),
        )


# ============================================================
# 補足: モデル責務分離・プロンプトハッシュの記録(ER-002-v1.1A-I1 1章・11章)
# ============================================================
class ModelResponsibilityAndFreezeTests(unittest.TestCase):
    def test_generation_and_evaluation_use_different_model_roles(self):
        self.assertEqual(angle_adapter.MODEL_ROLE, ec.ANGLE_GENERATION_MODEL_ROLE)
        self.assertEqual(ec.ANGLE_GENERATION_MODEL_ROLE, "openai_script_model")
        self.assertEqual(ec.ANGLE_EVALUATION_MODEL_ROLE, "gemini_qa_model")
        self.assertNotEqual(ec.ANGLE_GENERATION_MODEL_ROLE, ec.ANGLE_EVALUATION_MODEL_ROLE)

    def test_frozen_conditions_include_all_required_hashes(self):
        frozen = freeze_v1_1a.build_frozen_conditions()
        for key in ("angle_generation_prompt", "angle_evaluation_prompt", "brief_inspection_prompt",
                    "script_generation_prompt_v1_1a", "editorial_quality_prompt", "claim_strength_taxonomy",
                    "schemas", "retry_conditions"):
            self.assertIn(key, frozen)
            self.assertIn("sha256", frozen[key])
            self.assertEqual(len(frozen[key]["sha256"]), 64)

    def test_experiment_version_is_v1_1a_not_v1_0(self):
        self.assertEqual(freeze_v1_1a.EXPERIMENT_VERSION, "ER-002-v1.1A")
        self.assertEqual(freeze_v1.EXPERIMENT_VERSION, "ER-002-v1.0")


if __name__ == "__main__":
    unittest.main()
