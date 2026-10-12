"""FAMILY-Z-MELOS-CONNECTED-SPEECH-ROOT-CAUSE-AUDIT-01 委任_01 の再発防止test。
監査で確認した「既承認Connected Speech機構の実挙動と境界」を固定する(Production挙動は一切変更しない)。
有料API・ネットワーク・TTS・local ASRは使わない(Azure/OpenAI ASR/Ledger research/telemetryはmock)。
注意: 『stem同音の別綴り(Mello/Mellow)がNOT_PASS』のtestは"現行の承認済み境界"を記録するもので、
望ましい最終仕様ではない。この境界を変える変更は人間ユーザーの APPROVED_FOR_PRODUCTION が必要。"""
import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_tts_generate as tg
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er011_b1_connected_speech_validator_01 as csv3
import er011_connected_speech_equivalence_layer_production_01 as eq
import er020_tts_retry_local_rewrite_01 as role_gate
import er021_en_asr_semantic_equivalence_production_01 as _se


def setUpModule():
    # classify_asr_match(role適用)は不合格時に共有telemetry.jsonlへ追記するため、このtestでは無効化する
    patcher = mock.patch.object(_se, "append_telemetry_log")
    patcher.start()
    unittest.addModuleCleanup(patcher.stop)

SEG = "full_story_part1_c5"  # Family Zの実clip_id形式(FULL_STORY)
# 固有名詞(-s/-es終わり)の一般集合。Melos固有ではない。
NAMES = [("Melos", "Melo"), ("Marcus", "Marcu"), ("Thomas", "Thoma"), ("Dionysius", "Dionysiu"),
         ("Brutus", "Brutu"), ("Jesus", "Jesu"), ("Chris", "Chri"), ("James", "Jame"), ("Lucas", "Luca"),
         ("Hades", "Hade"), ("Silas", "Sila"), ("Judas", "Juda"), ("Venus", "Venu"), ("Orpheus", "Orpheu")]
NEXT_SIBILANT = ["said", "spoke", "smiled", "sat", "saw", "stood"]


class FlagPropagationAndRoleTests(unittest.TestCase):
    def test_family_z_clip_ids_resolve_to_full_story_and_cs_enabled(self):
        for cid in ("full_story_part1_c5", "full_story_part3_c9", "full_story_part2_c12"):
            self.assertEqual(role_gate.resolve_narrative_role(cid), "FULL_STORY", cid)
            self.assertTrue(role_gate.connected_speech_enabled_for(cid), cid)

    def test_suffixed_ids_are_not_misclassified(self):
        # fullmatch設計: _original等の接尾辞は不一致(別segment扱い)
        self.assertFalse(role_gate.connected_speech_enabled_for("full_story_part1_c5_original"))


class ApprovedPatternABoundaryTests(unittest.TestCase):
    def test_proper_noun_exact_stem_drop_before_sibilant_is_accepted_and_never_shadowed_by_entity_gate(self):
        """Primaryで固有名詞が接尾辞-sを落として(stem完全一致)転写された場合、entity gateに遮られず
        Pattern A(CONNECTED_SPEECH_ACCEPT)に到達する。ordering問題(entity_only/UNCERTAINが先)は
        この形では発生しない(_is_benign_plural_pairが差分を吸収し、最終fallbackでCS Validatorが走る)。"""
        for full, stem in NAMES:
            for nx in NEXT_SIBILANT:
                c = val.classify_asr_match(f"{full} {nx}.", f"{stem} {nx}.", segment_id=SEG)
                self.assertTrue(c.should_pass, (full, stem, nx, c.classification))
                self.assertEqual(c.classification, "CONNECTED_SPEECH_ACCEPT", (full, stem, nx))

    def test_pattern_a_not_applied_before_non_sibilant_next_word(self):
        c = val.classify_asr_match("Melos walked.", "Melo walked.", segment_id=SEG)
        self.assertNotEqual(c.classification, "CONNECTED_SPEECH_ACCEPT")

    def test_stem_homophone_spellings_remain_not_pass_current_approved_boundary(self):
        """Mello/Mellow(stemと同音だが綴りが違う)は現行承認範囲(綴り水準のPattern A)ではUNCERTAIN。
        Equivalence LayerもCMU未収録(melos)のためNOT_A_PHONEME_PREFIX_DROP。変更にはユーザー承認が必要。"""
        for asr in ("Mello said.", "Mellow said."):
            c = val.classify_asr_match("Melos said.", asr, segment_id=SEG)
            self.assertFalse(c.should_pass, asr)
            self.assertEqual(c.classification, "ASR_VALIDATION_UNCERTAIN", asr)
            self.assertEqual(csv3.classify_connected_speech("Melos said.", asr)["new_judgment"],
                             "UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING", asr)
            self.assertEqual(eq.classify_connected_speech_equivalence("Melos said.", asr)["layer_judgment"],
                             "NOT_A_PHONEME_PREFIX_DROP", asr)
        self.assertIsNone(eq.word_phones("melos"))  # CMU未収録(固有名詞はOOV)が構造的原因

    def test_counterexamples_never_pass(self):
        for canon, asr in [("Melos said.", "Melon said."), ("Melos said.", "Marcus said."),
                           ("Melos said.", "Melody said."), ("Marcus smiled.", "Marker smiled."),
                           ("The studies suggest a link.", "The studio suggests a link."),
                           ("The bosses said so.", "The bonus said so.")]:
            c = val.classify_asr_match(canon, asr, segment_id=SEG)
            self.assertFalse(c.should_pass, (canon, asr, c.classification))

    def test_general_noun_pattern_a_and_b_still_approved(self):
        self.assertEqual(val.classify_asr_match("The studies suggest a link.", "The study suggests a link.",
                                                segment_id="comment_1").classification, "CONNECTED_SPEECH_ACCEPT")
        self.assertEqual(val.classify_asr_match("He opened to them.", "He open to them.",
                                                segment_id="comment_1").classification, "CONNECTED_SPEECH_ACCEPT")


class EquivalenceLayerGatingTests(unittest.TestCase):
    """Equivalence LayerはTRUE_CONTENT_MISMATCH(+protected通過)のfallthroughでのみ呼ばれる。
    entity_only由来のASR_VALIDATION_UNCERTAINでは呼ばれない(今回のMelos said.の実測と一致)。"""

    def _cascade(self, canonical, primary, azure):
        layer_calls = []
        with mock.patch.object(sec.routing, "transcribe", return_value=(primary, None)), \
             mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list", return_value=(azure, None)), \
             mock.patch.object(sec, "_resolve_unresolved_entity_for_review", return_value=None), \
             mock.patch.object(sec.semantic_equivalence, "append_telemetry_log"), \
             mock.patch.object(sec, "_connected_speech_equivalence_layer_attempt",
                               side_effect=lambda *a, **k: layer_calls.append(a)):
            d = sec.evaluate_attempt_with_cascade_detail(
                canonical, primary, [], "dummy.wav", language="en-US", ledger_phrases=["Melos"],
                cascade_enabled=True, enable_connected_speech_equivalence_layer=True, segment_id=SEG)
        return d, layer_calls

    def test_layer_not_invoked_for_entity_only_uncertain_melos_said(self):
        d, layer_calls = self._cascade("Melos said.", "Mello said.", "Mellow said.")
        self.assertFalse(d["verified"])
        self.assertFalse(d["connected_speech_equivalence_layer_invoked"])
        self.assertEqual(layer_calls, [])
        self.assertEqual(d["final_status"], "ASR_VALIDATION_UNCERTAIN")

    def test_secondary_spelling_exact_stem_is_rescued_by_pattern_a_in_cascade(self):
        """実事例(a2 fallback attempt): Primary=Mello(UNCERTAIN)、Azure=Melo -> secondary stepでPattern A ACCEPT。"""
        d, _ = self._cascade("Melos said.", "Mello said.", "Melo said.")
        self.assertTrue(d["verified"])
        self.assertEqual(d["final_status"], "CONNECTED_SPEECH_ACCEPT")


class PostSlowdownPatternATests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="er026_csaudit_test_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.name = SEG
        self.out = f"{self.tmp}/{self.name}.wav"
        with open(self.out, "wb") as f:
            f.write(b"PRE")

    def _run(self, canonical, primary_asr, azure_text):
        def fake_stretch(src, dst):
            with open(dst, "wb") as f:
                f.write(b"POST")
            return {"src_duration_seconds": 1.2, "dst_duration_seconds": 1.27}
        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=fake_stretch), \
             mock.patch.object(tg.routing, "transcribe", return_value=(primary_asr, None)), \
             mock.patch.object(sec.routing, "transcribe", return_value=(primary_asr, None)), \
             mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list", return_value=(azure_text, None)), \
             mock.patch.object(sec, "_resolve_unresolved_entity_for_review", return_value=None), \
             mock.patch.object(sec.semantic_equivalence, "append_telemetry_log"):
            return tg.apply_a2_slowdown_postprocess(
                self.name, self.tmp, canonical, {"status": "OK", "sha256": None, "duration_seconds": 1.2})

    def test_post_slowdown_rescue_accepts_when_secondary_exact_stem(self):
        out = self._run("Melos said.", "Mello said.", "Melo said.")
        self.assertEqual(out["status"], "OK")
        self.assertTrue(out["post_slowdown_cascade_accepted"])
        self.assertEqual(out["post_slowdown_final_classification"], "CONNECTED_SPEECH_ACCEPT")

    def test_post_slowdown_still_stopped_when_all_asr_spell_homophone_variants(self):
        out = self._run("Melos said.", "Mello said.", "Mellow said.")
        self.assertEqual(out["status"], "STOPPED")

    def test_equivalence_layer_flag_not_passed_in_post_slowdown_path_known_gap_open122_4(self):
        """既知Gap(OPEN-122 追記(4))の事実固定: 減速後cascade救済はenable_connected_speech_equivalence_layerを渡さない
        (既定False)。UNCERTAIN限定の救済なので今回の事象には無関係。変更する場合はユーザー判断。"""
        seen = {}
        orig = sec.evaluate_attempt_with_cascade_detail

        def spy(*a, **k):
            seen.update(k)
            return orig(*a, **k)
        with mock.patch.object(sec, "evaluate_attempt_with_cascade_detail", side_effect=spy):
            self._run("Melos said.", "Mello said.", "Mellow said.")
        self.assertNotIn("enable_connected_speech_equivalence_layer", seen)


if __name__ == "__main__":
    unittest.main(verbosity=1)
