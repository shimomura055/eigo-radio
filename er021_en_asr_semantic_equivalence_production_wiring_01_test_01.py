# ============================================================
# er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py
# 管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(Phase A+B)
# ============================================================
# unittest(API課金なし)。Production配線(classify_asr_matchのrole
# gating付きTier1 early-exit、evaluate_attempt_with_cascade_detailの
# Tier3 corroboration)を、実際に配線された経路そのもの経由で検証する
# (Trial module[er021_en_asr_semantic_equivalence_trial_01.py]は無変更
# のまま、本ファイルは一切importしない)。

from __future__ import annotations

import importlib.util
import json
import unittest

import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary_asr
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er021_en_asr_semantic_equivalence_production_01 as semantic_equivalence

APPLICABLE_SEGMENT_ID = "comment_1"       # role=COMMENT(5role適用対象)
NON_APPLICABLE_SEGMENT_ID = "point_one_heading"  # role=HEADING_READOUT(非適用)
KEY_PHRASE_SEGMENT_ID = "kp1_en"          # role=KEY_PHRASE(非適用)

TRIAL_CORPUS_PATH = "er021_output/en_asr_semantic_equivalence_trial_01/corpus.jsonl"


def _load_trial_corpus():
    """EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01で検証済みのcorpus(POSITIVE
    34/NEGATIVE 34、mechanism別内訳込み)を、Trial moduleをimportせずに
    そのまま読み込む(Production module側からの再検証用、¥0)。"""
    records = []
    with open(TRIAL_CORPUS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


class RoleGatingTest(unittest.TestCase):
    """Tier1 early-exitは、segment_id/role未指定または非適用roleでは
    一切発火しないこと(既存呼び出し元の挙動が完全に無変更であること)を
    固定する。"""

    CANONICAL = "The price rose to two point three million dollars this year."
    ASR = "The price rose to $2.3 million this year."

    def test_no_segment_id_no_role_gate_unchanged(self):
        r = val.classify_asr_match(self.CANONICAL, self.ASR)
        self.assertNotEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")
        self.assertFalse(r.should_pass)

    def test_applicable_role_via_segment_id_fires(self):
        r = val.classify_asr_match(self.CANONICAL, self.ASR, segment_id=APPLICABLE_SEGMENT_ID)
        self.assertEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")
        self.assertTrue(r.should_pass)
        self.assertFalse(r.should_retry)
        self.assertEqual(r.semantic_equivalence_info["tier_applied"], "tier1_numeric")

    def test_applicable_role_via_role_kwarg_fires(self):
        r = val.classify_asr_match(self.CANONICAL, self.ASR, role="FULL_STORY")
        self.assertEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")
        self.assertTrue(r.should_pass)

    def test_heading_role_not_applicable(self):
        r = val.classify_asr_match(self.CANONICAL, self.ASR, segment_id=NON_APPLICABLE_SEGMENT_ID)
        self.assertNotEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")
        self.assertFalse(r.should_pass)

    def test_key_phrase_role_not_applicable(self):
        r = val.classify_asr_match(self.CANONICAL, self.ASR, segment_id=KEY_PHRASE_SEGMENT_ID)
        self.assertNotEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")
        self.assertFalse(r.should_pass)

    def test_unknown_segment_id_not_applicable(self):
        r = val.classify_asr_match(self.CANONICAL, self.ASR, segment_id="some_unrecognized_segment_xyz")
        self.assertNotEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")

    def test_role_resolution_uses_er020_single_source_of_truth(self):
        # role gatingが実際にer020のresolve_narrative_role()と同じ判定に
        # 追従することを、5role全件+非適用2種で確認する。
        five_roles_segment_ids = ("full_story_part1", "comment_2", "preview",
                                   "topic_intro", "in_one_line")
        for seg in five_roles_segment_ids:
            with self.subTest(segment_id=seg):
                self.assertTrue(retry_primitive.connected_speech_enabled_for(seg))
                r = val.classify_asr_match(self.CANONICAL, self.ASR, segment_id=seg)
                self.assertEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")
        for seg in (NON_APPLICABLE_SEGMENT_ID, KEY_PHRASE_SEGMENT_ID):
            with self.subTest(segment_id=seg):
                self.assertFalse(retry_primitive.connected_speech_enabled_for(seg))


class Tier1ProductionCorpusTest(unittest.TestCase):
    """Trialのcorpus(POSITIVE 34/NEGATIVE 34)を、Production配線経由
    (val.classify_asr_match(..., segment_id=APPLICABLE_SEGMENT_ID))で
    再実行する。false accept 0・POSITIVE救済(Tier1該当分)を固定する。"""

    POSITIVE_NUMERIC = [
        ("The price rose to two point three million dollars, a fifteen percent "
         "increase from last year.",
         "The price rose to $2.3 million, a 15% increase from last year."),
        ("The company is now worth one point two billion dollars.",
         "The company is now worth $1.2 billion."),
        ("The policy was introduced in 1999.", "The policy was introduced in nineteen ninety-nine."),
        ("The forecast covers the period through 2026.",
         "The forecast covers the period through twenty twenty-six."),
        ("The meeting starts at 3:30 pm.", "The meeting starts at three thirty pm."),
        ("The article discusses World War II history.",
         "The article discusses World War 2 history."),
        ("The population is 2,300,000 people.",
         "The population is two million three hundred thousand people."),
    ]

    NEGATIVE_NUMERIC = [
        ("The price rose to $2.3 million.", "The price rose to $2.5 million."),
        ("There were fifteen participants.", "There were fifty participants."),
        ("Inflation rose by five percent.", "Inflation rose by five percentage points."),
        ("The device costs $100.", "The device costs 100."),
        ("The company is worth two point three million dollars.",
         "The company is worth $2.3 billion."),
        ("The fee is fifty dollars.", "The fee is £50."),
        ("The meeting starts at 3:30 pm.", "The meeting starts at 3:30 am."),
        ("The reference number is 1234567.",
         "The reference number is one two three four five six seven."),
    ]

    def test_positive_numeric_rescued_via_production_wiring(self):
        for canonical, asr in self.POSITIVE_NUMERIC:
            with self.subTest(canonical=canonical):
                r = val.classify_asr_match(canonical, asr, segment_id=APPLICABLE_SEGMENT_ID)
                self.assertEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")
                self.assertTrue(r.should_pass)

    def test_negative_numeric_no_false_accept_via_production_wiring(self):
        for canonical, asr in self.NEGATIVE_NUMERIC:
            with self.subTest(canonical=canonical):
                r = val.classify_asr_match(canonical, asr, segment_id=APPLICABLE_SEGMENT_ID)
                self.assertFalse(r.should_pass, f"false accept: {canonical!r} vs {asr!r} -> {r.classification}")
                self.assertNotEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")


class TrialFullCorpusViaProductionWiringTest(unittest.TestCase):
    """EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01の全corpus(POSITIVE 34/
    NEGATIVE 34、`er021_output/en_asr_semantic_equivalence_trial_01/
    corpus.jsonl`)を、Production配線経由(val.classify_asr_match(...,
    segment_id=...))で再実行する。mechanism='tier1_numeric'/
    'tier1_numeric_or_tier3'のPOSITIVEはTier1 early-exitで直接救済される
    ことを、NEGATIVE 34件全件はfalse accept 0(role適用状態でも一切
    NUMERIC_EQUIVALENCE_MATCH/SECONDARY_ASR_CORROBORATED_MATCHに
    ならないこと)を固定する。mechanism='tier3_corroboration'のPOSITIVE
    (規則的複数形・固有名詞、独立ASR corroborationが必要)は
    Tier3CascadeIntegrationTestで別途、実際のcascade経由(mock)で検証
    済みのためここでは対象外。mechanism='baseline_normalized_match'
    (2件、既存Production側で元々PASSしていたケース)は無回帰確認として
    含める。"""

    @classmethod
    def setUpClass(cls):
        cls.records = _load_trial_corpus()
        assert len(cls.records) == 68, f"corpus件数が想定外です: {len(cls.records)}"

    def test_negative_corpus_no_false_accept_via_production_wiring(self):
        negatives = [r for r in self.records if r["expected"] == "FAIL"]
        self.assertEqual(len(negatives), 34)
        for rec in negatives:
            with self.subTest(id=rec["id"]):
                r = val.classify_asr_match(rec["canonical"], rec["asr"], segment_id=APPLICABLE_SEGMENT_ID)
                self.assertFalse(r.should_pass, f"false accept: {rec['id']} -> {r.classification}")
                self.assertNotIn(r.classification,
                                  ("NUMERIC_EQUIVALENCE_MATCH", "SECONDARY_ASR_CORROBORATED_MATCH"))

    def test_positive_tier1_and_baseline_corpus_via_production_wiring(self):
        positives = [r for r in self.records
                     if r["expected"] == "PASS"
                     and r["mechanism"] in ("tier1_numeric", "tier1_numeric_or_tier3", "baseline_normalized_match")]
        self.assertEqual(len(positives), 27 + 1 + 2)
        for rec in positives:
            with self.subTest(id=rec["id"], mechanism=rec["mechanism"]):
                r = val.classify_asr_match(rec["canonical"], rec["asr"], segment_id=APPLICABLE_SEGMENT_ID)
                self.assertTrue(r.should_pass, f"regression: {rec['id']} -> {r.classification}")


class ExistingFixtureRegressionViaProductionWiringTest(unittest.TestCase):
    """既存OPEN-123 Regression fixture(POSITIVE 29+AMBIGUOUS 2+NEGATIVE 28、
    er006_preprod_hardening_01_validation_test.py)を、role gate適用状態
    (segment_id=APPLICABLE_SEGMENT_ID)でも無回帰・false accept 0のまま
    であることを固定する(Tier1がPOSITIVE fixtureの既存合格経路を壊さない
    こと、NEGATIVE fixtureを誤って救済しないことの両方を確認する)。"""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "_er006_fixtures_for_er021w", "er006_preprod_hardening_01_validation_test.py")
        cls.fixmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.fixmod)

    def test_positive_fixtures_no_regression_with_role_gate_on(self):
        for fx in self.fixmod.POSITIVE_FIXTURES:
            r = val.classify_asr_match(fx["canonical"], fx["asr"], segment_id=APPLICABLE_SEGMENT_ID)
            ok = r.should_pass or not r.should_retry
            self.assertTrue(ok, f"regression: {fx['name']} -> {r.classification}")

    def test_negative_fixtures_no_false_accept_with_role_gate_on(self):
        for fx in self.fixmod.NEGATIVE_FIXTURES:
            r = val.classify_asr_match(fx["canonical"], fx["asr"], segment_id=APPLICABLE_SEGMENT_ID)
            self.assertFalse(r.should_pass, f"false accept: {fx['name']} -> {r.classification}")


class Tier3CascadeIntegrationTest(unittest.TestCase):
    """evaluate_attempt_with_cascade_detail()内のTier3 corroborationブロックを、
    Azure呼び出しをmockして(API課金なし)実際の配線経路そのもので検証する。"""

    def setUp(self):
        self._orig_azure = secondary_asr.get_full_text_via_azure_stt_with_phrase_list

    def tearDown(self):
        secondary_asr.get_full_text_via_azure_stt_with_phrase_list = self._orig_azure

    def _run(self, canonical, asr, corroborating_text, segment_id=APPLICABLE_SEGMENT_ID):
        secondary_asr.get_full_text_via_azure_stt_with_phrase_list = (
            lambda wav_path, language="en-US", phrases=None, timeout_seconds=90.0: (corroborating_text, None))
        return secondary_asr.evaluate_attempt_with_cascade_detail(
            canonical, asr, [], "dummy_not_a_real_narration_path.wav",
            cascade_enabled=True, segment_id=segment_id)

    def test_plural_only_corroborated_by_secondary(self):
        canonical = "We need to bring the main point together."
        asr = "We need to bring the main points together."
        detail = self._run(canonical, asr, corroborating_text=canonical)
        self.assertTrue(detail["verified"])
        self.assertEqual(detail["final_status"], "SECONDARY_ASR_CORROBORATED_MATCH")
        info = detail["classification"].semantic_equivalence_info
        self.assertEqual(info["tier_applied"], "tier3_corroboration")
        self.assertEqual(info["sub_reason"], "plural_only")
        self.assertIn("secondary", info["corroborated_by"])
        self.assertTrue(info["warning"])

    def test_plural_only_not_corroborated_stays_uncertain(self):
        canonical = "We need to bring the main point together."
        asr = "We need to bring the main points together."
        # Secondaryも同じ誤り("points")を返す -> corroborationしない(安全側)。
        detail = self._run(canonical, asr, corroborating_text=asr)
        self.assertFalse(detail["verified"])
        self.assertEqual(detail["final_status"], "ASR_VALIDATION_UNCERTAIN")

    def test_role_not_applicable_tier3_not_attempted(self):
        canonical = "We need to bring the main point together."
        asr = "We need to bring the main points together."
        detail = self._run(canonical, asr, corroborating_text=canonical,
                            segment_id=NON_APPLICABLE_SEGMENT_ID)
        # role非適用のため、Tier3が発火せず既存挙動のまま
        # (cascade_eligible=False、is_entity_like/homophoneでもないため
        # cascade自体が発火しない)。
        self.assertFalse(detail["verified"])
        self.assertFalse(detail["cascade_invoked"])

    def test_no_segment_id_tier3_not_attempted(self):
        canonical = "We need to bring the main point together."
        asr = "We need to bring the main points together."
        detail = self._run(canonical, asr, corroborating_text=canonical, segment_id=None)
        self.assertFalse(detail["verified"])
        self.assertFalse(detail["cascade_invoked"])

    def test_numeric_mismatch_still_true_content_mismatch_not_swallowed_by_tier3(self):
        # Tier3はASR_VALIDATION_UNCERTAINのみを対象とする。数字の真の不一致
        # (TRUE_CONTENT_MISMATCH)がTier3経由で誤って救済されないことを確認。
        canonical = "The price rose to $2.3 million."
        asr = "The price rose to $2.5 million."
        detail = self._run(canonical, asr, corroborating_text=canonical)
        self.assertFalse(detail["verified"])
        self.assertEqual(detail["classification"].classification, "TRUE_CONTENT_MISMATCH")


class StringComparisonSafetyTest(unittest.TestCase):
    """recon_02 C-1で個別確認が必要とされた文字列比較箇所(`should_stop_
    retrying`+`er006_secondary_asr_01.py`内の`classification ==`/`!=`
    比較4箇所)が、新規ラベル(`NUMERIC_EQUIVALENCE_MATCH`/`SECONDARY_
    ASR_CORROBORATED_MATCH`、いずれもshould_pass=True)に対して意図通り
    「非該当」(cascade_eligible判定に巻き込まれない、retry停止判定を
    誤発火させない)になることを固定する。"""

    def _numeric_match_result(self):
        r = val.classify_asr_match(
            "The price rose to two point three million dollars.",
            "The price rose to $2.3 million.", segment_id=APPLICABLE_SEGMENT_ID)
        self.assertEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")
        return r

    def test_is_entity_like_mismatch_false_for_numeric_equivalence_match(self):
        r = self._numeric_match_result()
        self.assertFalse(secondary_asr.is_entity_like_mismatch(r))

    def test_is_homophone_candidate_mismatch_false_for_numeric_equivalence_match(self):
        r = self._numeric_match_result()
        self.assertFalse(secondary_asr.is_homophone_candidate_mismatch(r))

    def test_step_alternate_pass_none_for_numeric_equivalence_match(self):
        r = self._numeric_match_result()
        self.assertIsNone(secondary_asr._step_alternate_pass(r))

    def test_should_stop_retrying_not_triggered_by_numeric_equivalence_match(self):
        # should_pass=Trueの結果は、evaluate_attempt()内でこの関数へ到達する
        # 前に(verified=True)確定するのが既定経路だが、念のため直接呼んでも
        # 安全側(誤ってFalseを返しretry継続の判断を壊さない)であることを
        # 固定する。
        r = self._numeric_match_result()
        self.assertFalse(val.should_stop_retrying([r, r, r]))

    def test_cascade_does_not_reach_eligibility_check_when_tier1_fires(self):
        # Tier1がPrimary#1で発火した場合、cascade_eligible判定
        # (is_entity_like_mismatch/is_homophone_candidate_mismatch)自体に
        # 到達しない(verified=Trueで早期return)ことをcascade全体で確認する。
        detail = secondary_asr.evaluate_attempt_with_cascade_detail(
            "The price rose to two point three million dollars.",
            "The price rose to $2.3 million.", [], "dummy_not_a_real_narration_path.wav",
            cascade_enabled=True, segment_id=APPLICABLE_SEGMENT_ID)
        self.assertTrue(detail["verified"])
        self.assertFalse(detail["cascade_invoked"])
        self.assertEqual(detail["classification"].classification, "NUMERIC_EQUIVALENCE_MATCH")


if __name__ == "__main__":
    unittest.main()
