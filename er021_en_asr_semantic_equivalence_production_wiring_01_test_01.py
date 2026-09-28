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
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_b1_p9a_audio as p9a
import er003_v1_crosslevel_audio_02_common as crosslevel
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
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


class A2StandardPathProductionWiringFixTest(unittest.TestCase):
    """修正1回目(Fable差し戻し、EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-
    WIRING-01): 既知Gap「A2標準経路(er003_v1_crosslevel_audio_02_common.
    generate_english_segment_with_fallback()の標準呼び出し部分)には
    segment_idが未配線」を解消したことを、実際の呼び出し経路そのもの
    (crosslevel.generate_english_segment_with_fallback()
    -> repro01.generate_narration_snippet_verified_strict())を通して
    固定する。TTS(p9a.generate_narration_snippet)とPrimary ASR
    (repro01.routing.transcribe)のみモックし、Tier1判定
    (secondary_asr.evaluate_attempt_with_cascade/val.classify_asr_match)
    は実ロジックをそのまま通す(API呼び出しなし、¥0)。"""

    CANONICAL = "The price rose to two point three million dollars this year."
    ASR_NUMERIC_EQUIVALENT = "The price rose to $2.3 million this year."

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er021w2_a2_standard_path_test_")
        self.narration_dir = os.path.join(self.tmp_dir, "wiring_theme_asrw2", "a2", "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.tts_call_count = 0

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _fake_generate_narration_snippet(self, text, language, out_path, tts_call_fn=None,
                                          safety_margin_seconds=None, style_prefix_override=None,
                                          # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01
                                          # (2026-09-27)で追加された新規opt-in引数(既定値付き)。
                                          # このFakeは受理して無視するだけでよい。
                                          tts_backend="structured_separation"):
        self.tts_call_count += 1
        with open(out_path, "wb") as f:
            f.write(f"FAKE_AUDIO_ATTEMPT_{self.tts_call_count}".encode("utf-8"))
        return {"status": "OK", "text": text, "language": language, "path": out_path,
                "model": "fake-en-model", "voice": "Aoede", "duration_seconds": 1.0,
                "sha256": "dummy"}

    def test_full_story_part1_numeric_diff_rescued_at_attempt1_no_cooldown_no_fallback(self):
        # 修正前: 標準経路2回ともTRUE_CONTENT_MISMATCH -> 600秒cool-down ->
        # fallback(minimal instruction)経路でTier1がようやくPASS、という
        # 無駄な経路だった(Fable差し戻し理由そのもの)。
        # 修正後: 標準経路attempt1の時点でsegment_id="full_story_part1"
        # (role=FULL_STORY、5role適用対象)が渡り、Tier1 early-exitが
        # attempt1で直接発火する。
        out_path = os.path.join(self.narration_dir, "full_story_part1.wav").replace("\\", "/")
        with mock.patch.object(p9a, "generate_narration_snippet",
                                side_effect=self._fake_generate_narration_snippet), \
             mock.patch.object(repro01.routing, "transcribe",
                                return_value=(self.ASR_NUMERIC_EQUIVALENT, None)):
            result = crosslevel.generate_english_segment_with_fallback(
                self.CANONICAL, out_path, "The price rose", max_extra_chars=60)

        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["asr_verified"])
        self.assertEqual(result["audio_classification"], "NUMERIC_EQUIVALENCE_MATCH")
        self.assertFalse(result.get("fallback_used"))
        self.assertEqual(len(result["attempts_log"]), 1,
                          "attempt1(標準経路1回目)で救済され、attempt2すら不要であるべき")
        self.assertNotIn("cooldown_events", result,
                          "fallback(cool-down対象)経路へ一切進んでいないこと")
        self.assertEqual(self.tts_call_count, 1, "TTS呼び出しは標準経路attempt1の1回のみであるべき")

    def test_point_one_heading_non_applicable_role_regression_unaffected(self):
        # role gatingの回帰確認: HEADING(非適用role)のsegment_idでは、
        # 同じ数値差ペアでも本修正の影響を受けず、既存挙動(Tier1不発火、
        # 複数attempt消費)のまま。Family A/非対象roleへの副作用が無いことを
        # 実際の生成経路(標準呼び出し部分)で直接確認する。
        out_path = os.path.join(self.narration_dir, "point_one_heading.wav").replace("\\", "/")
        with mock.patch.object(p9a, "generate_narration_snippet",
                                side_effect=self._fake_generate_narration_snippet), \
             mock.patch.object(repro01.routing, "transcribe",
                                return_value=(self.ASR_NUMERIC_EQUIVALENT, None)):
            core = repro01.generate_narration_snippet_verified_strict.__wrapped__
            result = core(self.CANONICAL, "en", out_path, "The price rose",
                          max_attempts=2, segment_id="point_one_heading")

        self.assertEqual(result["status"], "STOPPED",
                          "非適用roleではTier1が発火せず、既存通り2回とも不合格で尽きるべき")
        self.assertEqual(len(result["attempts_log"]), 2)
        self.assertEqual(self.tts_call_count, 2, "非適用roleでは救済されず標準2回とも実際に消費するべき")
        for entry in result["attempts_log"]:
            self.assertNotEqual(entry.get("audio_classification"), "NUMERIC_EQUIVALENCE_MATCH")

    def test_no_segment_id_default_unchanged_family_a_regression(self):
        # segment_id未指定(Family A等、この修正の対象外呼び出し元)は
        # 従来通り無変更であることを、生成経路(repro01の標準関数)を直接
        # 通して確認する(既存のRoleGatingTestはclassify_asr_match単体
        # 呼び出しでの確認、本testは生成関数レベルでの確認)。
        out_path = os.path.join(self.narration_dir, "unrelated_family_a_segment.wav").replace("\\", "/")
        with mock.patch.object(p9a, "generate_narration_snippet",
                                side_effect=self._fake_generate_narration_snippet), \
             mock.patch.object(repro01.routing, "transcribe",
                                return_value=(self.ASR_NUMERIC_EQUIVALENT, None)):
            core = repro01.generate_narration_snippet_verified_strict.__wrapped__
            result = core(self.CANONICAL, "en", out_path, "The price rose", max_attempts=2)

        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(len(result["attempts_log"]), 2)
        self.assertEqual(self.tts_call_count, 2)


class NewsTailFixB1WiringFixTest(unittest.TestCase):
    """修正2回目(Fable差し戻し、EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-
    WIRING-01): 既知Gap「B1本文(`er003_v1_sing01_news_tail_fix.py::
    generate_news_narration_wide_margin`、Full Story/Point/In One Line
    生成の主経路)にはsegment_idが未配線」を解消したことを、実際の関数
    そのもの経由で固定する。TTSパイプライン(`common._call_tts_with_retry`/
    `p3u.trim_english_keyword_silence`/`safety.detect_duration_anomaly`)と
    Primary ASR(`routing.transcribe`)のみモックし、Tier1判定
    (`secondary_asr.evaluate_attempt_with_cascade`/`val.classify_asr_match`)
    は実ロジックをそのまま通す(API呼び出しなし、¥0、モック方式は既存の
    `er011_open121_repetition_qa_production_wiring_01_test_01.
    GenerateNewsNarrationWideMarginScopeTests`と同一)。"""

    CANONICAL = "The price rose to two point three million dollars this year."
    ASR_NUMERIC_EQUIVALENT = "The price rose to $2.3 million this year."

    def setUp(self):
        import numpy as np
        self.np = np
        self.tmp_dir = tempfile.mkdtemp(prefix="er021w3_news_tail_fix_wiring_test_")
        self.tts_call_count = 0

        self.orig_call_tts = news_tail_fix.common._call_tts_with_retry
        self.orig_trim = news_tail_fix.p3u.trim_english_keyword_silence
        self.orig_anomaly = news_tail_fix.safety.detect_duration_anomaly
        self.orig_transcribe = news_tail_fix.routing.transcribe

        def _fake_call_tts_with_retry(call_fn, prompt, max_retry=None, sleep_fn=None):
            self.tts_call_count += 1
            fake_pcm = self.np.zeros(4000, dtype=self.np.int16).tobytes()
            return fake_pcm, 0, True, None

        news_tail_fix.common._call_tts_with_retry = _fake_call_tts_with_retry
        news_tail_fix.p3u.trim_english_keyword_silence = lambda samples, sr, safety_margin_seconds=None: (
            self.np.zeros(sr, dtype=self.np.float32), {"raw_duration_seconds": 1.0})
        news_tail_fix.safety.detect_duration_anomaly = lambda *a, **k: {"is_anomaly": False}
        news_tail_fix.routing.transcribe = lambda *a, **k: (self.ASR_NUMERIC_EQUIVALENT, None)

    def tearDown(self):
        news_tail_fix.common._call_tts_with_retry = self.orig_call_tts
        news_tail_fix.p3u.trim_english_keyword_silence = self.orig_trim
        news_tail_fix.safety.detect_duration_anomaly = self.orig_anomaly
        news_tail_fix.routing.transcribe = self.orig_transcribe
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_full_story_part1_numeric_diff_rescued_at_attempt1_no_cooldown(self):
        # 修正前: standard attempt 1・2ともTRUE_CONTENT_MISMATCHで
        # (enable_connected_speech_equivalence_layer=Falseのため)即STOPPED、
        # role gate自体が一切適用されなかった(Fable差し戻し理由と同型の
        # B1側Gap)。修正後: out_pathが".../<theme>/<level>/narration/
        # full_story_part1.wav"という標準命名慣習に従っていれば、
        # segment_id="full_story_part1"(role=FULL_STORY、5role適用対象)が
        # attempt1から渡り、Tier1 early-exitが直接発火する。
        narration_dir = os.path.join(self.tmp_dir, "wiring_theme_asrw3", "b1b", "narration")
        os.makedirs(narration_dir, exist_ok=True)
        out_path = os.path.join(narration_dir, "full_story_part1.wav").replace("\\", "/")

        result = news_tail_fix.generate_news_narration_wide_margin(self.CANONICAL, out_path, max_attempts=3)

        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["asr_verified"])
        self.assertEqual(result["audio_classification"], "NUMERIC_EQUIVALENCE_MATCH")
        self.assertEqual(len(result["attempts_log"]), 1,
                          "attempt1で救済され、attempt2以降のcool-downへ一切進まないこと")
        self.assertEqual(result.get("cooldown_events"), [],
                          "cool-downが不発火であること(enable_connected_speech_equivalence_layer=False既定、"
                          "かつattempt1で即PASSのため)")
        self.assertEqual(self.tts_call_count, 1, "TTS呼び出しはattempt1の1回のみであるべき")

    def test_point_one_heading_non_applicable_role_regression_unaffected(self):
        # role gatingの回帰確認: HEADING(非適用role)のsegment_idでは、
        # 同じ数値差ペアでも本修正の影響を受けず、既存挙動(Tier1不発火)の
        # まま。
        narration_dir = os.path.join(self.tmp_dir, "wiring_theme_asrw3", "b1b", "narration")
        os.makedirs(narration_dir, exist_ok=True)
        out_path = os.path.join(narration_dir, "point_one_heading.wav").replace("\\", "/")

        result = news_tail_fix.generate_news_narration_wide_margin(self.CANONICAL, out_path, max_attempts=1)

        self.assertNotEqual(result.get("status"), "OK",
                             "非適用roleではTier1が発火せず、既存通り不合格のままであるべき")
        self.assertEqual(len(result["attempts_log"]), 1)
        self.assertNotEqual(result["attempts_log"][0].get("audio_classification"), "NUMERIC_EQUIVALENCE_MATCH")
        self.assertEqual(self.tts_call_count, 1)

    def test_no_valid_narration_layout_segment_id_none_unchanged(self):
        # out_pathが標準命名慣習("<theme>/<level>/narration/<segment>.wav")
        # に従わない場合(既存呼び出し元の一部、単体テストのダミーパス等)は
        # segment_id=Noneのまま(role gate非適用)、既存挙動と完全に同じで
        # あることを確認する。
        out_path = os.path.join(self.tmp_dir, "dummy_out_no_layout.wav").replace("\\", "/")

        result = news_tail_fix.generate_news_narration_wide_margin(self.CANONICAL, out_path, max_attempts=1)

        self.assertNotEqual(result.get("status"), "OK")
        self.assertEqual(len(result["attempts_log"]), 1)
        self.assertNotEqual(result["attempts_log"][0].get("audio_classification"), "NUMERIC_EQUIVALENCE_MATCH")
        self.assertEqual(self.tts_call_count, 1)


class StrictTier1SynthesisRuleTest(unittest.TestCase):
    """EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(Phase 2、ユーザー
    承認2026-09-28: strict版Tier1合成規則+分類A技術修正)。diff-anchored
    比較+punctuation由来局所差分吸収(打点略語・meridiem略記・hyphenated
    numeric・alphanumeric entity)、月名限定序数吸収、序数語("third"等)、
    "per cent"、数値語runの"and"飲み込みバグ修正、単独ローマ数字(V/X)の
    締める方向の安全化を、実際の配線経路(val.classify_asr_match(...,
    segment_id=APPLICABLE_SEGMENT_ID))で固定する。"""

    def _match(self, canonical, asr):
        return val.classify_asr_match(canonical, asr, segment_id=APPLICABLE_SEGMENT_ID)

    # ---- positive: 分類A技術修正が実際に救済すること ----

    def test_ordinal_word_matches_digit_suffix(self):
        r = self._match("The team completed the third attempt successfully.",
                         "The team completed the 3rd attempt successfully.")
        self.assertTrue(r.should_pass)
        self.assertEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")

    def test_per_cent_two_word_matches_percent_word(self):
        r = self._match("Sales rose by 20 per cent this quarter.",
                         "Sales rose by 20 percent this quarter.")
        self.assertTrue(r.should_pass)

    def test_per_cent_two_word_matches_percent_symbol(self):
        r = self._match("Sales rose by 20 per cent this quarter.",
                         "Sales rose by 20% this quarter.")
        self.assertTrue(r.should_pass)

    def test_and_swallow_parser_bug_fixed_true_equivalence_rescued(self):
        # 修正前は"and"が隣接する裸digit語(five)を誤って飲み込み、
        # canonical/ASR間でatom数がずれてTier1が正しい等価性を救済
        # できなかった(既存の安全装置を回避するものではなく、既存の
        # false rejectを解消する修正であることを固定する)。
        r = self._match("The bus arrives, and five minutes later it departs.",
                         "The bus arrives, and 5 minutes later it departs.")
        self.assertTrue(r.should_pass)

    def test_meridiem_abbreviation_matches_am_pm_word(self):
        r = self._match("The meeting starts at 10:16 am today.",
                         "The meeting starts at 10:16 a.m. today.")
        self.assertTrue(r.should_pass)

    def test_hyphenated_numeric_matches_spaced_form(self):
        r = self._match("It was a 15-minute walk worth $5.",
                         "It was a 15 minute walk worth $5.")
        self.assertTrue(r.should_pass)

    def test_alphanumeric_entity_hyphen_matches_spaced_form(self):
        r = self._match("The COVID-19 outbreak began in 2019.",
                         "The COVID 19 outbreak began in 2019.")
        self.assertTrue(r.should_pass)

    def test_date_ordinal_month_adjacent_absorbed(self):
        r = self._match("The curtain rose on July 13, costing $5.",
                         "The curtain rose on July 13th, costing $5.")
        self.assertTrue(r.should_pass)

    def test_act_one_hormuz_style_combined_punctuation_diffs_pass(self):
        # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01 Phase 3の
        # 既知gap(er003_test_v1_n3_01_tts_generate.py::
        # ActHeadingDigitReadingRegressionTests、role gate非適用の回帰
        # fixtureは無変更のまま)を、role gate適用状態(本来のProduction
        # 配線)で再現し、strict版Tier1合成規則により正しく等価
        # (PASS)へ是正されたことを固定する(OPEN-186/COVERAGE-REVIEW-02の
        # 是正そのもの)。旧fixtureとの関係: 旧fixtureはsegment_id/roleを
        # 渡さない呼び出しを検証しており、Tier1自体が発火しないため今回の
        # 修正の影響を受けず、無回帰のまま残る(是正はこのテストが担う)。
        canonical = (
            "The play unfolds in three acts. Act One introduces the "
            "characters. Act Two raises the stakes. Act Three resolves "
            "the conflict. The curtain rose on July 13. The cost of US "
            "efforts was notable."
        )
        asr_digit_and_punctuation_form = (
            "The play unfolds in three acts. Act 1 introduces the "
            "characters. Act 2 raises the stakes. Act 3 resolves "
            "the conflict. The curtain rose on July 13th. The cost of U.S. "
            "efforts was notable."
        )
        r = self._match(canonical, asr_digit_and_punctuation_form)
        self.assertTrue(r.should_pass, f"expected rescue via strict Tier1 synthesis rule, got {r.classification}")
        self.assertEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")
        self.assertTrue(r.semantic_equivalence_info["diff_spans"]["diff_anchored"])
        self.assertGreaterEqual(r.semantic_equivalence_info["diff_spans"]["absorbed_ops"], 1)

    # ---- negative: false accept 0(既存の安全性を拡張しない) ----

    def test_model_x_vs_model_10_not_absorbed(self):
        r = self._match("This is Model X, priced at $5.", "This is Model 10, priced at $5.")
        self.assertFalse(r.should_pass)
        self.assertNotEqual(r.classification, "NUMERIC_EQUIVALENCE_MATCH")

    def test_cardinal_vs_ordinal_28_28th_not_absorbed_outside_date_context(self):
        r = self._match("The study included 28 articles, costing $5.",
                         "The study included 28th articles, costing $5.")
        self.assertFalse(r.should_pass)

    def test_us_vs_uk_abbreviation_not_absorbed(self):
        r = self._match("The cost was $5 for US efforts.", "The cost was $5 for UK efforts.")
        self.assertFalse(r.should_pass)

    def test_approx_vs_exact_not_absorbed(self):
        r = self._match("About 20 people attended, costing $5.", "20 people attended, costing $5.")
        self.assertFalse(r.should_pass)

    def test_percent_vs_percentage_points_not_absorbed(self):
        r = self._match("Inflation rose by five percent, costing $5.",
                         "Inflation rose by five percentage points, costing $5.")
        self.assertFalse(r.should_pass)

    def test_roman_numeral_single_letter_without_label_context_not_absorbed(self):
        r = self._match("I bought a V for $5.", "I bought a 5 for $5.")
        self.assertFalse(r.should_pass)

    def test_roman_numeral_single_letter_with_label_context_still_absorbed(self):
        # 締める方向の安全化は「無条件」を止めるだけで、閉じたラベル文脈
        # (Section/Act/Part等)では従来通りローマ数字として機能すること。
        # (数字直後にcomma等が隣接すると_TOKEN_REの桁区切りcomma対応と
        # 干渉するため、意図的に数字とcommaが隣接しない文言にする。)
        r = self._match("Please review Section V for details, it costs $5.",
                         "Please review Section 5 for details, it costs $5.")
        self.assertTrue(r.should_pass)

    def test_digit_hyphen_digit_code_not_absorbed_by_tier1(self):
        # ハイフンが2つの数値atomの間に挟まる場合(コード/ID風の表記)は、
        # 「文字-数字」「数字-文字」拡張の対象外のままとし、Tier1自体の
        # 既存安全性を拡張しない(Tier1単体で直接確認する。旧Validator側
        # の独立した既存正規化[despaced()等、本タスクの変更範囲外]が
        # 別途NORMALIZED_MATCHで救済する場合があるが、それはTier1の
        # false acceptではない)。
        r = semantic_equivalence.tier1_numeric_equivalence(
            "The reference code is 12-34, costing $5.",
            "The reference code is 12 34, costing $5.")
        self.assertIsNone(r, "Tier1がハイフン区切りのコードを誤って吸収している(false accept)")

    def test_genuine_negative_number_sign_preserved_by_tier1(self):
        # Tier1自体が符号(-5 vs 5)を吸収しないことを直接確認する(旧
        # Validator側の独立した既存正規化は本タスクの変更範囲外)。
        r = semantic_equivalence.tier1_numeric_equivalence(
            "The change was -5 degrees, a shift of $3.",
            "The change was 5 degrees, a shift of $3.")
        self.assertIsNone(r, "Tier1が符号違いを誤って吸収している(false accept)")

    # ---- 長尺(>200 atom)・合成negative群: punctuation差と同居しても
    # 正当なnegativeが道連れで救済されないこと(false accept 0)を固定する。

    _LONG_BASE_SENTENCES = [
        "Act One introduces the characters in three acts.",
        "Act Two raises the stakes for everyone involved.",
        "Act Three resolves the conflict on stage.",
        "The curtain rose on July 13 in front of a large crowd.",
        "The cost of US efforts was notable across the region.",
        "The meeting starts at 10:16 am at the main office.",
        "The report is divided into 15 parts for the committee.",
        "Analysts said the plan could raise prices by 20 percent.",
        "The company said the change was worth about $5 million.",
        "Officials declined to comment on the record this week.",
    ]

    @classmethod
    def _long_canonical(cls):
        return " ".join(cls._LONG_BASE_SENTENCES * 2)

    @classmethod
    def _long_asr_punctuation_only(cls):
        # 番号ラベルdigit化・meridiem略記・US略語のみを変え、内容自体は
        # 変えない(canonicalと"意味的に完全に同じ"長尺ASR書き起こし)。
        sentences = [
            "Act 1 introduces the characters in three acts.",
            "Act 2 raises the stakes for everyone involved.",
            "Act 3 resolves the conflict on stage.",
            "The curtain rose on July 13th in front of a large crowd.",
            "The cost of U.S. efforts was notable across the region.",
            "The meeting starts at 10:16 a.m. at the main office.",
            "The report is divided into 15 parts for the committee.",
            "Analysts said the plan could raise prices by 20 percent.",
            "The company said the change was worth about $5 million.",
            "Officials declined to comment on the record this week.",
        ]
        return " ".join(sentences * 2)

    def test_long_segment_punctuation_only_diffs_pass(self):
        canonical = self._long_canonical()
        asr = self._long_asr_punctuation_only()
        # 前提: 200 atomを超える長尺segmentであることを固定する
        # (autojunk境界・diff-anchored化の効果を確認する対象規模)。
        self.assertGreater(len(semantic_equivalence._tier1_atoms(canonical)), 200)
        r = self._match(canonical, asr)
        self.assertTrue(r.should_pass, f"expected long-segment punctuation-only PASS, got {r.classification}")

    def test_long_segment_dropped_sentence_not_absorbed(self):
        canonical = self._long_canonical()
        sentences = self._long_asr_punctuation_only().split(". ")
        # 1文まるごと欠落させる(合成negative: 文の丸ごと欠落)。
        asr = ". ".join(sentences[:-2] + sentences[-1:])
        r = self._match(canonical, asr)
        self.assertFalse(r.should_pass, "文の丸ごと欠落が誤って救済されている(false accept)")

    def test_long_segment_negation_dropped_not_absorbed(self):
        canonical = self._long_canonical()
        asr = self._long_asr_punctuation_only().replace(
            "Officials declined to comment on the record this week.",
            "Officials agreed to comment on the record this week.", 1)
        r = self._match(canonical, asr)
        self.assertFalse(r.should_pass, "否定語欠落(declined->agreed)が誤って救済されている(false accept)")

    def test_long_segment_number_off_by_one_not_absorbed(self):
        canonical = self._long_canonical()
        asr = self._long_asr_punctuation_only().replace(
            "The report is divided into 15 parts for the committee.",
            "The report is divided into 16 parts for the committee.", 1)
        r = self._match(canonical, asr)
        self.assertFalse(r.should_pass, "数値1桁違いが誤って救済されている(false accept)")

    def test_long_segment_unit_only_diff_not_absorbed(self):
        canonical = self._long_canonical()
        asr = self._long_asr_punctuation_only().replace(
            "Analysts said the plan could raise prices by 20 percent.",
            "Analysts said the plan could raise prices by 20 percentage points.", 1)
        r = self._match(canonical, asr)
        self.assertFalse(r.should_pass, "単位のみ相違(percent->percentage points)が誤って救済されている(false accept)")

    def test_long_segment_us_vs_uk_not_absorbed(self):
        canonical = self._long_canonical()
        asr = self._long_asr_punctuation_only().replace(
            "The cost of U.S. efforts was notable across the region.",
            "The cost of U.K. efforts was notable across the region.", 1)
        r = self._match(canonical, asr)
        self.assertFalse(r.should_pass, "U.S.≠U.K.(別の実体)が誤って救済されている(false accept)")

    def test_long_segment_cardinal_vs_ordinal_non_month_adjacent_not_absorbed(self):
        canonical = self._long_canonical()
        # "15 parts"(基数) vs "15th parts"(序数、月名に隣接しない裸digit)。
        asr = self._long_asr_punctuation_only().replace(
            "The report is divided into 15 parts for the committee.",
            "The report is divided into 15th parts for the committee.", 1)
        r = self._match(canonical, asr)
        self.assertFalse(r.should_pass, "基数/序数の意味差(15 vs 15th、月名非隣接)が誤って救済されている(false accept)")


if __name__ == "__main__":
    unittest.main()
