# ============================================================
# er002_test_editorial_v1_1b.py
# ER-002-v1.1B-I1: 編集品質QAの事実入力契約修正のテスト
# ============================================================
# 実API・実TTS・実QA・新規トピック取得は一切行わない。すべてモックのみ。
# ER-002-v1.1A-PM1で発見された不具合(検証済み事実の本文が編集品質QAへ
# 一度も渡っていなかった)の修正を検証する。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er002_test_editorial_v1_1b -v

import hashlib
import json
import os
import unittest

import er002_common as common
import er002_editorial_common as ec
import er002_editorial_runner as runner
import er002_v1_1a_freeze as freeze_v1_1a
import er002_v1_1b_fixtures as fixtures
import er002_v1_1b_freeze as freeze_v1_1b


def make_passing_quality_response_v1_1b(overrides=None):
    base = {
        "brief_alignment": True, "opening_is_specific": True, "opening_is_grounded": True,
        "hypothetical_is_disclosed": None, "central_tension_present": True,
        "point_one_role_fulfilled": True, "point_two_role_fulfilled": True,
        "point_claims_are_distinct": True, "point_redundancy_detected": False,
        "narrative_coherence_present": True, "fact_enumeration_dominates": False,
        "non_obvious_takeaway_landed": True, "listener_payoff_present": True,
        "claim_strength_changed": [], "overstatement_or_dramatization": False,
        "claim_grounding_results": [
            {"claim_text": "c1", "claim_location": "body", "verdict": "grounded",
             "supporting_fact_ids": ["F01"], "rationale": "matches F01"},
        ],
        "ungrounded_claims": [],
        "factual_grounding_status": "pass",
        "brief_alignment_issues": [],
        "brief_alignment_status": "pass",
        "overall_status": "pass", "evidence": "everything checks out",
    }
    base.update(overrides or {})
    return base


VALID_FACT_IDS = {"F01", "F02", "F03", "F04", "F05"}


# ============================================================
# 要求1: 編集品質QAペイロードへF01〜F05の本文がすべて含まれる
# ============================================================
class FactRegistryInPromptTests(unittest.TestCase):
    def test_all_five_fact_texts_present_in_prompt(self):
        fact_registry = fixtures.load_fact_registry()
        brief = fixtures.load_editorial_brief()
        script = fixtures.load_script_attempt(1)
        prompt = ec.build_editorial_quality_prompt_v1_1b(script, brief, fact_registry)
        self.assertTrue(ec.fact_registry_fully_present_in_prompt(prompt, fact_registry))
        for fact_text in fact_registry.values():
            self.assertIn(fact_text, prompt)
        self.assertIn("VERIFIED FACT REGISTRY", prompt)

    # 要求2: fact registry本文を欠落させた入力を検出できる
    def test_missing_fact_text_is_detected_by_guard_utility(self):
        brief = fixtures.load_editorial_brief()
        script = fixtures.load_script_attempt(1)
        # 台本本文に一切登場しない合成事実を使う(実台本の文中に偶然
        # 同じ文字列が出現してガードが素通りすることを避けるため)
        full_registry = {"F90": "This synthetic fact never appears in the A01 script body anywhere."}
        incomplete_registry = {}  # F90の本文を完全に欠落させた入力を模す
        prompt_with_gap = ec.build_editorial_quality_prompt_v1_1b(script, brief, incomplete_registry)
        self.assertFalse(ec.fact_registry_fully_present_in_prompt(prompt_with_gap, full_registry))

    def test_v1_1a_prompt_still_never_includes_fact_registry(self):
        """v1.1Aのbuild_editorial_quality_promptは変更していないことの確認
        (要求11の一部)。修正前の不具合そのものが再現されることを示す。"""
        brief = fixtures.load_editorial_brief()
        script = fixtures.load_script_attempt(1)
        old_prompt = ec.build_editorial_quality_prompt(script, brief)
        self.assertNotIn("VERIFIED FACT REGISTRY", old_prompt)
        fact_registry = fixtures.load_fact_registry()
        self.assertFalse(ec.fact_registry_fully_present_in_prompt(old_prompt, fact_registry))


# ============================================================
# 要求3・4・5: Brief未引用でもgrounded、1つのfact_idが複数claimを支える、
# F03が92分のclaimを支える
# ============================================================
class FactGroundingAcceptanceTests(unittest.TestCase):
    def test_claim_grounded_by_fact_id_not_referenced_by_brief_is_accepted(self):
        """BriefにF01が一度も出てこなくても(実際のA01 Briefがそうである)、
        F01に支えられるclaimはgroundedとして受理できる。"""
        brief = fixtures.load_editorial_brief()
        brief_fact_ids = (
            set(brief.get("opening_fact_ids", []))
            | set(brief.get("point_one_fact_ids", []))
            | set(brief.get("point_two_fact_ids", []))
            | {e["fact_id"] for e in brief.get("fact_support_map", [])}
        )
        self.assertNotIn("F01", brief_fact_ids, "このテストの前提: 実際のBriefはF01を引用していない")

        response = make_passing_quality_response_v1_1b({
            "claim_grounding_results": [
                {"claim_text": "Argentina defeated England 2-1", "claim_location": "body",
                 "verdict": "grounded", "supporting_fact_ids": ["F01"], "rationale": "F01そのもの"},
            ],
        })
        validated = ec.validate_editorial_quality_fields_v1_1b(response, VALID_FACT_IDS)
        classified = ec.classify_editorial_quality_v1_1b(validated)
        self.assertTrue(classified["passed"])

    def test_single_fact_id_supports_multiple_distinct_claims(self):
        """1つのF01が『対戦相手・スコア・大会段階・日付』の4つの個別claimを
        支えられる(まとめて1判定にしない)。"""
        response = make_passing_quality_response_v1_1b({
            "claim_grounding_results": [
                {"claim_text": "opponent was England", "claim_location": "body",
                 "verdict": "grounded", "supporting_fact_ids": ["F01"], "rationale": "F01: England"},
                {"claim_text": "score was 2-1", "claim_location": "body",
                 "verdict": "grounded", "supporting_fact_ids": ["F01"], "rationale": "F01: 2-1"},
                {"claim_text": "it was a World Cup semifinal", "claim_location": "body",
                 "verdict": "grounded", "supporting_fact_ids": ["F01"], "rationale": "F01: semifinal"},
                {"claim_text": "date was July 15, 2026", "claim_location": "body",
                 "verdict": "grounded", "supporting_fact_ids": ["F01"], "rationale": "F01: date"},
            ],
        })
        validated = ec.validate_editorial_quality_fields_v1_1b(response, VALID_FACT_IDS)
        classified = ec.classify_editorial_quality_v1_1b(validated)
        self.assertTrue(classified["passed"])
        self.assertEqual(len(validated["claim_grounding_results"]), 4)

    def test_f03_supports_92nd_minute_claim(self):
        response = make_passing_quality_response_v1_1b({
            "claim_grounding_results": [
                {"claim_text": "the winning goal was in the 92nd minute", "claim_location": "Point Two",
                 "verdict": "grounded", "supporting_fact_ids": ["F03"],
                 "rationale": "F03の本文に92nd minuteとある"},
            ],
        })
        validated = ec.validate_editorial_quality_fields_v1_1b(response, VALID_FACT_IDS)
        classified = ec.classify_editorial_quality_v1_1b(validated)
        self.assertTrue(classified["passed"])


# ============================================================
# 要求6: 事実性pass・Brief整合性failを別々に処理できる
# ============================================================
class SeparateStatusTests(unittest.TestCase):
    def test_factual_pass_brief_alignment_fail_classified_correctly(self):
        response = make_passing_quality_response_v1_1b({
            "brief_alignment": False,
            "brief_alignment_status": "fail",
            "brief_alignment_issues": [
                {"claim_or_passage": "opening paragraph", "issue": "central_tensionから逸脱",
                 "rationale": "Briefのcentral_tension_or_questionと無関係な話題を導入している"},
            ],
        })
        validated = ec.validate_editorial_quality_fields_v1_1b(response, VALID_FACT_IDS)
        classified = ec.classify_editorial_quality_v1_1b(validated)
        self.assertFalse(classified["passed"])
        self.assertEqual(classified["failure_classification"], "BRIEF_ALIGNMENT_FAILURE")
        self.assertNotIn("factual_grounding_failed", classified["reasons"])

    def test_factual_fail_classified_as_ungrounded_not_brief_alignment(self):
        response = make_passing_quality_response_v1_1b({
            "claim_grounding_results": [
                {"claim_text": "fabricated claim", "claim_location": "body",
                 "verdict": "ungrounded", "supporting_fact_ids": [], "rationale": "レジストリに存在しない"},
            ],
            "ungrounded_claims": ["fabricated claim"],
            "factual_grounding_status": "fail",
        })
        validated = ec.validate_editorial_quality_fields_v1_1b(response, VALID_FACT_IDS)
        classified = ec.classify_editorial_quality_v1_1b(validated)
        self.assertFalse(classified["passed"])
        self.assertEqual(classified["failure_classification"], "UNGROUNDED_CLAIMS_FAILURE")


# ============================================================
# 要求7〜10: 応答整合性検証(inconclusive化)
# ============================================================
class ResponseConsistencyInconclusiveTests(unittest.TestCase):
    def test_grounded_with_empty_fact_ids_is_inconclusive(self):
        response = make_passing_quality_response_v1_1b({
            "claim_grounding_results": [
                {"claim_text": "c1", "claim_location": "body", "verdict": "grounded",
                 "supporting_fact_ids": [], "rationale": "..."},
            ],
        })
        with self.assertRaises(ec.EditorialQualityParseError):
            ec.validate_editorial_quality_fields_v1_1b(response, VALID_FACT_IDS)

    def test_nonexistent_fact_id_is_inconclusive(self):
        response = make_passing_quality_response_v1_1b({
            "claim_grounding_results": [
                {"claim_text": "c1", "claim_location": "body", "verdict": "grounded",
                 "supporting_fact_ids": ["F99"], "rationale": "..."},
            ],
        })
        with self.assertRaises(ec.EditorialQualityParseError):
            ec.validate_editorial_quality_fields_v1_1b(response, VALID_FACT_IDS)

    def test_toplevel_status_contradicts_claim_results_is_inconclusive(self):
        response = make_passing_quality_response_v1_1b({
            "factual_grounding_status": "pass",
            "claim_grounding_results": [
                {"claim_text": "c1", "claim_location": "body", "verdict": "ungrounded",
                 "supporting_fact_ids": [], "rationale": "..."},
            ],
            "ungrounded_claims": ["c1"],
        })
        with self.assertRaises(ec.EditorialQualityParseError):
            ec.validate_editorial_quality_fields_v1_1b(response, VALID_FACT_IDS)

    def test_ungrounded_claims_mismatch_with_claim_results_is_inconclusive(self):
        response = make_passing_quality_response_v1_1b({
            "factual_grounding_status": "fail",
            "claim_grounding_results": [
                {"claim_text": "c1", "claim_location": "body", "verdict": "ungrounded",
                 "supporting_fact_ids": [], "rationale": "..."},
            ],
            "ungrounded_claims": [],  # c1と不一致
        })
        with self.assertRaises(ec.EditorialQualityParseError):
            ec.validate_editorial_quality_fields_v1_1b(response, VALID_FACT_IDS)

    def test_full_evaluate_loop_ends_inconclusive_after_max_attempts_on_bad_input(self):
        def broken_qa_fn(prompt):
            return json.dumps(make_passing_quality_response_v1_1b({
                "claim_grounding_results": [
                    {"claim_text": "c1", "claim_location": "body", "verdict": "grounded",
                     "supporting_fact_ids": [], "rationale": "..."},
                ],
            }))

        outcome = ec.evaluate_editorial_quality_v1_1b(
            "prompt", broken_qa_fn, VALID_FACT_IDS, max_eval_attempts=2)
        self.assertEqual(outcome.final_outcome, "inconclusive")
        self.assertEqual(len(outcome.attempts), 2)


# ============================================================
# 要求11: v1.1Aの凍結条件と成果物が変更されない
# ============================================================
class V1_1A_UntouchedTests(unittest.TestCase):
    def test_v1_1a_editorial_quality_constants_unchanged(self):
        # v1.1B-I1着手前に確認済みの値(手動で固定した既知値との照合)
        self.assertEqual(
            ec.EDITORIAL_QUALITY_REQUIRED_FIELDS,
            ["brief_alignment", "opening_is_specific", "opening_is_grounded", "hypothetical_is_disclosed",
             "central_tension_present", "point_one_role_fulfilled", "point_two_role_fulfilled",
             "point_claims_are_distinct", "point_redundancy_detected", "narrative_coherence_present",
             "fact_enumeration_dominates", "non_obvious_takeaway_landed", "listener_payoff_present",
             "ungrounded_claims", "claim_strength_changed", "overstatement_or_dramatization",
             "overall_status", "evidence"],
        )
        self.assertEqual(ec.MAX_EDITORIAL_QUALITY_EVAL_ATTEMPTS, 2)

    def test_v1_1a_frozen_conditions_still_buildable_and_stable(self):
        frozen_a = freeze_v1_1a.build_frozen_conditions()
        frozen_b = freeze_v1_1a.build_frozen_conditions()
        stable_a = {k: v for k, v in frozen_a.items() if k != "frozen_at"}
        stable_b = {k: v for k, v in frozen_b.items() if k != "frozen_at"}
        self.assertEqual(json.dumps(stable_a, sort_keys=True), json.dumps(stable_b, sort_keys=True))

    def test_v1_1b_inherited_hashes_match_v1_1a_directly(self):
        v1_1a_frozen = freeze_v1_1a.build_frozen_conditions()
        v1_1b_frozen = freeze_v1_1b.build_frozen_conditions()
        inherited = v1_1b_frozen["inherited_from_v1_1a"]
        self.assertEqual(inherited["angle_generation_prompt_sha256"], v1_1a_frozen["angle_generation_prompt"]["sha256"])
        self.assertEqual(inherited["angle_evaluation_prompt_sha256"], v1_1a_frozen["angle_evaluation_prompt"]["sha256"])
        self.assertEqual(inherited["brief_inspection_prompt_sha256"], v1_1a_frozen["brief_inspection_prompt"]["sha256"])
        self.assertEqual(
            inherited["script_generation_prompt_v1_1a_sha256"],
            v1_1a_frozen["script_generation_prompt_v1_1a"]["sha256"])
        self.assertEqual(inherited["claim_strength_taxonomy_sha256"], v1_1a_frozen["claim_strength_taxonomy"]["sha256"])

    def test_a01_v1_1a_run_artifacts_on_disk_unchanged_since_pm1(self):
        """ER-002-v1.1A-PM1で記録したsha256(artifact_sha256.json)と現在の
        ファイル内容が一致することを確認する(v1.1Aの実行成果物が
        v1.1B-I1の作業で上書きされていないことの直接的な証拠)。"""
        sha_path = "er002_output/A01/v1_1a/_pm1_analysis/artifact_sha256.json"
        if not os.path.exists(sha_path):
            self.skipTest("PM1のartifact_sha256.jsonが見つかりません")
        with open(sha_path, encoding="utf-8") as f:
            recorded = json.load(f)
        for rel_path, expected_sha in recorded.items():
            with open(rel_path, "rb") as f:
                actual_sha = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(actual_sha, expected_sha, f"{rel_path} が変更されています")

    def test_run_script_stage_default_quality_evaluate_fn_is_v1_1a_unchanged(self):
        """quality_evaluate_fnのデフォルト値が、明示的に注入しない既存の
        v1.1A呼び出しの挙動を一切変えないことを直接確認する。"""
        import inspect
        sig = inspect.signature(runner.run_script_stage_with_quality_gate)
        self.assertIs(sig.parameters["quality_evaluate_fn"].default, ec.evaluate_editorial_quality)


# ============================================================
# 誤検知解消の確認: 実際のA01台本2件が、修正後の入力契約の下では
# (適切な応答が返る限り)不合格にならないことを示す
# ============================================================
class MisdetectionResolutionDemonstrationTests(unittest.TestCase):
    """実APIは呼ばない。旧(v1.1A)応答が新スキーマの必須フィールドを
    欠くため新検証では確定的にinconclusive/エラーになること、および
    修正後の入力契約+訂正済み応答であれば同じ実台本がpassできることを
    モックのみで示す(ER-002-v1.1B-I1の『まず既存v1.1A台本2件を使って
    誤検知解消を確認』の要求に対応)。"""

    def test_old_v1_1a_quality_responses_lack_v1_1b_required_fields(self):
        for n in (1, 2):
            old_response = fixtures.load_old_quality_response(n)
            missing = [f for f in ec.EDITORIAL_QUALITY_REQUIRED_FIELDS_V1_1B if f not in old_response]
            self.assertTrue(missing, f"attempt{n}: 旧応答にv1.1B必須フィールドが欠落しているはず")

    def test_real_a01_scripts_pass_under_corrected_contract_with_well_formed_response(self):
        """PM1で確認済みの事実: A01台本のungrounded_claims判定はすべて
        F01〜F05のいずれかで裏付けられる真の事実だった。訂正後の契約
        (fact registry本文を渡す)の下で、正しく判定するQAが返す想定
        応答を与えれば、同じ実台本がpassになることを示す。"""
        fact_registry = fixtures.load_fact_registry()
        brief = fixtures.load_editorial_brief()

        for n in (1, 2):
            script = fixtures.load_script_attempt(n)
            prompt = ec.build_editorial_quality_prompt_v1_1b(script, brief, fact_registry)
            self.assertTrue(ec.fact_registry_fully_present_in_prompt(prompt, fact_registry))

            corrected_response = make_passing_quality_response_v1_1b({
                "claim_grounding_results": [
                    {"claim_text": "opponent/score/semifinal/date facts", "claim_location": "body",
                     "verdict": "grounded", "supporting_fact_ids": ["F01"], "rationale": "F01と一致"},
                    {"claim_text": "England scorer", "claim_location": "body",
                     "verdict": "grounded", "supporting_fact_ids": ["F02"], "rationale": "F02と一致"},
                    {"claim_text": "92nd minute winning goal", "claim_location": "Point Two",
                     "verdict": "grounded", "supporting_fact_ids": ["F03"], "rationale": "F03と一致"},
                    {"claim_text": "advanced to final against Spain", "claim_location": "body",
                     "verdict": "grounded", "supporting_fact_ids": ["F04"], "rationale": "F04と一致"},
                    {"claim_text": "Messi assist and cross", "claim_location": "Point One",
                     "verdict": "grounded", "supporting_fact_ids": ["F05"], "rationale": "F05と一致"},
                ],
            })

            def qa_fn(p, _resp=corrected_response):
                return json.dumps(_resp)

            outcome = ec.evaluate_editorial_quality_v1_1b(
                prompt, qa_fn, set(fact_registry.keys()),
                fact_registry_sha256=ec.sha256_json(fact_registry))
            self.assertEqual(outcome.final_outcome, "passed", f"attempt{n}が修正後の契約下でpassしない")
            self.assertEqual(outcome.fact_registry_sha256, ec.sha256_json(fact_registry))


# ============================================================
# フィクスチャローダ自体の健全性
# ============================================================
class FixtureLoaderTests(unittest.TestCase):
    def test_fixtures_contain_no_secrets(self):
        secret_markers = ["sk-", "AIza", "api_key", "apikey"]
        fixture_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er002_v1_1b_fixtures")
        for filename in os.listdir(fixture_dir):
            with open(os.path.join(fixture_dir, filename), encoding="utf-8") as f:
                content = f.read().lower()
            for marker in secret_markers:
                self.assertNotIn(marker, content, f"{filename}に秘密情報らしき文字列が含まれています")

    def test_fact_registry_has_five_facts(self):
        self.assertEqual(len(fixtures.load_fact_registry()), 5)

    def test_both_script_attempts_loadable(self):
        self.assertIsNotNone(fixtures.load_script_attempt(1))
        self.assertIsNotNone(fixtures.load_script_attempt(2))


if __name__ == "__main__":
    unittest.main()
