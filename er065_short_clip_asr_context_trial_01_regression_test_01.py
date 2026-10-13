# -*- coding: utf-8 -*-
"""FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01 委任_03 回帰test(ASR/TTS呼出なし、既存転写を入力、Production state書込なし)。

目的(再発防止):
 (1) Production既存の連結発音機構(Pattern A/B/C、Equivalence Layer cheap、classify_asr_match)の現行挙動を固定(characterization)。
     Productionコードは今回無変更。将来の変更で『誤PASSが増える/正常な連結が取りこぼされる』方向に動いたら検知する。
 (2) Trial音韻判定(`er065_short_clip_asr_context_trial_01_p2_phon.py`、Production未配線)の判定・3分類を、実データ由来の転写で固定。
     真の誤発音/別語/語尾欠落の反例は、いかなる独立証拠があっても『許容』にならないことを固定(安全性)。
 (3) 『ASR転写だけ(独立証拠なし)では許容にしない』原則を固定。

実行: .venv\\Scripts\\python.exe er065_short_clip_asr_context_trial_01_regression_test_01.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er006_preprod_hardening_01_validation as val
import er011_b1_connected_speech_validator_01 as csv3
import er011_connected_speech_equivalence_layer_production_01 as eq
import er021_en_asr_semantic_equivalence_production_01 as _se
import er065_short_clip_asr_context_trial_01_p2_phon as P

# 共有telemetryへの追記を無効化(Production state保護)
_se.append_telemetry_log = lambda *a, **k: None

SEG = "full_story_part1"


def prod(canon, asr):
    r = val.classify_asr_match(canon, asr, segment_id=SEG)
    return r.classification, bool(r.should_pass)


class ProductionCharacterization(unittest.TestCase):
    """既存承認仕様の現行挙動(変更しない)。"""

    def test_pattern_a_spelling_level_accept(self):
        # 実データ: Std a2 part1_c5 take3 secondary Azure
        self.assertEqual(prod("Melos said.", "Melo said."), ("CONNECTED_SPEECH_ACCEPT", True))
        self.assertEqual(prod("The studies suggest that", "The study suggests that")[1], True)
        self.assertEqual(prod("the guards seized", "the guard seized"), ("CONNECTED_SPEECH_ACCEPT", True))
        self.assertEqual(prod("stores stock", "store stock")[1], True)

    def test_same_phonemes_different_spelling_not_accepted_by_production(self):
        # 設計上の不足(OPEN-327): 綴りが違う同音は現行では自動PASSしない。この固定が崩れたら是正が入った合図。
        for a in ("Mello said.", "Mellow said.", "Mellis said.", "Mellos said."):
            self.assertEqual(prod("Melos said.", a), ("ASR_VALIDATION_UNCERTAIN", False), a)

    def test_known_defects_not_passed(self):
        for a in ("Melon said.", "Marcus said.", "Mel said.", "Melody said."):
            self.assertFalse(prod("Melos said.", a)[1], a)
        for a in ("Melos aid.", "Melos."):
            self.assertEqual(prod("Melos said.", a), ("TRUE_CONTENT_MISMATCH", False), a)

    def test_no_over_accept_on_non_suffix_final_consonant(self):
        # 接尾辞でない語末子音の欠落は未分類のまま(過受理なし)
        self.assertFalse(prod("school starts", "schoo starts")[1])
        self.assertFalse(prod("nice sign", "nigh sign")[1])

    def test_validator_pattern_a_is_not_morphology_aware_OPEN330(self):
        # OPEN-330: 語幹末s(bus)も接尾辞sも区別せず受理される(現行仕様の記録)
        self.assertEqual(csv3.classify_connected_speech("bus stops", "bu stops")["new_judgment"], "CONNECTED_SPEECH_ACCEPT")

    def test_equivalence_layer_cannot_reach_oov_name(self):
        # CMU未収録(OOV)の固有名詞は音素列が作れず NOT_A_PHONEME_PREFIX_DROP(OPEN-327の構造的原因)
        self.assertIsNone(eq.word_phones("melos"))
        j = eq.classify_connected_speech_equivalence("Melos said.", "Mello said.")["layer_judgment"]
        self.assertEqual(j, "NOT_A_PHONEME_PREFIX_DROP")

    def test_equivalence_layer_in_dictionary_words_needs_corroboration(self):
        # 辞書語の語末子音脱落は音韻環境に該当しても、独立ASR corroboration無しでは accept しない
        j = eq.classify_connected_speech_equivalence("pay showed coffee", "pay show coffee")["layer_judgment"]
        self.assertIn(j, ("EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE", "NO_KNOWN_CATEGORY_MATCH", "NOT_A_PHONEME_PREFIX_DROP"))
        self.assertNotIn(j, eq.ACCEPT_JUDGMENTS)


class TrialPhonologyJudge(unittest.TestCase):
    """Trial音韻判定(Production未配線)。実データ由来の転写で固定。"""

    def v(self, c, a):
        return P.explain_diff(c, a)["verdict"]

    def test_melos_said_family_is_explained_as_ss_fusion(self):
        for a in ("Mello said.", "Mellow said.", "Melo said."):
            self.assertEqual(self.v("Melos said.", a), "PHON_EXPLAINED_FUSION", a)

    def test_resegmented_forms_are_weakly_explained(self):
        # 実データ(att5/att6): 融合した/s/ + said の /d/ 無声化の読み
        for a in ("meloset", "Mellowset."):
            self.assertEqual(self.v("Melos said.", a), "PHON_EXPLAINED_VOICING", a)

    def test_vowel_change_or_other_word_is_not_explained(self):
        for a in ("Mellis said.", "Melon said.", "Marcus said.", "Melody said.", "Mel said.", "Melos aid.", "Melos.", "Melo sat."):
            self.assertEqual(self.v("Melos said.", a), "NOT_EXPLAINED", a)

    def test_same_phonemes_full_s_is_homophone_only(self):
        self.assertEqual(self.v("Melos said.", "Mellos said."), "PHON_HOMOPHONE_ONLY")

    def test_general_words_real_data(self):
        self.assertEqual(self.v("the guards stopped", "the guard stopped"), "PHON_EXPLAINED_FUSION")   # s+s(Z+S)
        self.assertEqual(self.v("stores stock", "store stock"), "PHON_EXPLAINED_FUSION")
        self.assertEqual(self.v("The studies suggest", "The study suggest"), "PHON_EXPLAINED_FUSION")
        self.assertEqual(self.v("last time", "lass time"), "PHON_EXPLAINED_FUSION")                      # t+t(語末t脱落)
        self.assertEqual(self.v("pay showed coffee", "pay show coffee"), "PHON_EXPLAINED_FUSION")        # d+k 語末d脱落
        self.assertEqual(self.v("some muse calls", "some use calls"), "PHON_EXPLAINED_VOICING")          # m+m 語頭m融合(voicing差)

    def test_general_words_real_nonfusion_diffs_not_explained(self):
        self.assertEqual(self.v("when Melos spoke", "when Milo spoke"), "NOT_EXPLAINED")
        self.assertEqual(self.v("followed two groups", "followed three groups"), "NOT_EXPLAINED")
        self.assertEqual(self.v("is safe", "is unsafe"), "NOT_EXPLAINED")
        self.assertEqual(self.v("experts spoke with", "experts speak with"), "NOT_EXPLAINED")

    def test_oov_without_stem_has_no_phonological_evidence(self):
        # G2P欠如(g2p_en未導入): 辞書にも stem+s 派生にも該当しないOOVは音韻証拠なし
        self.assertEqual(self.v("Zxqvt said.", "Zxqv said."), "NO_PHONOLOGICAL_EVIDENCE")


class ThreeWayPolicy(unittest.TestCase):
    def tw(self, c, a, ev=None):
        return P.three_way(P.explain_diff(c, a), ev)["class"]

    def test_asr_guess_alone_never_allows(self):
        for a in ("Mello said.", "Mellow said.", "Melo said.", "meloset"):
            self.assertEqual(self.tw("Melos said.", a), "HR", a)

    def test_independent_evidence_allows_only_explained(self):
        self.assertEqual(self.tw("Melos said.", "Mello said.", {"acoustic_geminate_ok": True}), "許容")
        # [委任_04訂正] second_engine_exact(Azure+Phrase List)はPhrase List誘導のため独立証拠から除外 -> 単独では許容にならない
        self.assertEqual(self.tw("Melos said.", "Mello said.", {"second_engine_exact": True}), "HR")
        self.assertEqual(self.tw("Melos said.", "Mello said.", {"acoustic_geminate_ok": False}), "HR")
        self.assertEqual(self.tw("Melos said.", "Mello said.", {"acoustic_geminate_ok": False, "second_engine_exact": True}), "HR")
        self.assertEqual(self.tw("Melos said.", "Mello said.", {"acoustic_geminate_ok": True, "second_engine_exact": False}), "許容")

    def test_defects_never_allowed_even_with_evidence(self):
        ev = {"acoustic_geminate_ok": True, "second_engine_exact": True}
        for a in ("Melon said.", "Marcus said.", "Mel said.", "Melos aid.", "Melos.", "Mellis said.", "Melo sat."):
            self.assertEqual(self.tw("Melos said.", a, ev), "NG", a)
        self.assertEqual(self.tw("is safe", "is unsafe", ev), "NG")
        self.assertEqual(self.tw("followed two groups", "followed three groups", ev), "NG")

    def test_voicing_and_homophone_go_to_hr_even_with_evidence(self):
        ev = {"acoustic_geminate_ok": True}
        self.assertEqual(self.tw("Melos said.", "meloset", ev), "HR")
        self.assertEqual(self.tw("Melos said.", "Mellos said.", ev), "HR")

    def test_exact_is_allowed(self):
        self.assertEqual(self.tw("Melos said.", "Melos said."), "許容")


# ============================================================ 委任_04追加(Opus必須修正3 / 推奨: 回帰test不足の補完)
class TrialSafetyPremise_Delegation04(unittest.TestCase):
    """Trial音韻判定は protected_check を持たない。否定・時制・数・別語の反例を明示固定する(ASR呼出なし)。"""

    COUNTER = [("I can't talk", "I can talk"), ("he walked to town", "he walk to town"),
               ("great time", "gray time"), ("they walked to", "they walk to")]

    def test_documented_hole_explain_diff_alone_explains_negation_tense_lexical(self):
        # 設計前提(protected_check通過後にのみ適用)が崩れると危険になることの記録: 単体では『説明可』と出てしまう
        for c, a in self.COUNTER:
            self.assertEqual(P.explain_diff(c, a)["verdict"], "PHON_EXPLAINED_FUSION", (c, a))

    def test_risk_flags_detect_each_counterexample(self):
        self.assertIn("negation", P.risk_flags("I can't talk", "I can talk"))
        self.assertIn("tense_or_suffix_drop", P.risk_flags("he walked to town", "he walk to town"))
        self.assertIn("lexical_change_between_dictionary_words", P.risk_flags("great time", "gray time"))
        self.assertIn("number", P.risk_flags("three trees", "tree trees"))

    def test_with_flags_never_allows_counterexamples_even_with_evidence(self):
        ev = {"acoustic_geminate_ok": True, "second_engine_exact": True}
        for c, a in self.COUNTER:
            self.assertEqual(P.three_way_with_flags(c, a, ev)["class"], "HR", (c, a))
        self.assertEqual(P.three_way_with_flags("three trees", "tree trees", ev)["class"], "NG")

    def test_three_vs_tree_is_not_allowed(self):
        self.assertNotEqual(P.three_way_with_flags("three men", "tree men", {"acoustic_geminate_ok": True})["class"], "許容")

    def test_melos_still_allowed_with_acoustic_and_no_flags(self):
        # 回帰: 安全装置が Melos(OOV, S/Z + S) の許容経路を壊さない
        self.assertEqual(P.risk_flags("Melos said.", "Mello said."), [])
        self.assertEqual(P.three_way_with_flags("Melos said.", "Mello said.", {"acoustic_geminate_ok": True})["class"], "許容")

    def test_acoustic_evidence_not_applicable_to_stop_boundaries(self):
        # 音響(摩擦区間長)は s+s でしか較正されていない。破裂音境界(t+t, d+k)では『測定不能』扱い=証拠に数えない
        for c, a in (("last time", "lass time"), ("pay showed coffee", "pay show coffee")):
            e = P.explain_diff(c, a)
            self.assertEqual(e["verdict"], "PHON_EXPLAINED_FUSION")
            self.assertEqual(P.three_way(e, {"acoustic_geminate_ok": True})["class"], "HR", c)

    def test_acoustic_evidence_applies_to_sibilant_boundaries(self):
        self.assertEqual(P.three_way(P.explain_diff("stores stock", "store stock"), {"acoustic_geminate_ok": True})["class"], "許容")
        self.assertEqual(P.three_way(P.explain_diff("stores stock", "store stock"), {"acoustic_geminate_ok": False})["class"], "HR")

    def test_phrase_list_second_engine_is_not_independent(self):
        self.assertEqual(P.three_way(P.explain_diff("Melos said.", "Mello said."), {"second_engine_exact": True})["class"], "HR")


class ProductionPatternsAndEqLayer_Delegation04(unittest.TestCase):
    """既存対策の機能確認(単体関数レベル)の補完: Pattern B/C一般例、Eq Layer受理経路、減速後経路の配線。"""

    def test_pattern_b_general_examples(self):
        self.assertEqual(prod("it opened to", "it open to")[1], True)
        self.assertEqual(csv3.classify_connected_speech("opened to", "open to")["rule"], "Pattern_B_stop_consonant_sequence")
        # 反例: 次語頭が破裂音でなければ発火しない
        self.assertEqual(csv3.classify_connected_speech("opened up", "open up")["new_judgment"], "UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING")

    def test_pattern_c_general_examples(self):
        r = csv3.classify_connected_speech("The survey suggest", "The surveys suggest")
        self.assertEqual((r["rule"], r["new_judgment"]), ("Pattern_C_resegmentation_added_consonant", "CONNECTED_SPEECH_RESEGMENTATION"))

    def test_equivalence_layer_accept_path_with_corroboration(self):
        # 正例: 辞書語の語末d脱落で、独立ASR(Secondary/local)がcanonical綴りを返した場合のみ ACCEPT
        j = eq.classify_connected_speech_equivalence("pay showed coffee", "pay show coffee",
                                                     secondary_asr_text="pay showed coffee",
                                                     local_asr_text="pay showed coffee")["layer_judgment"]
        self.assertIn(j, eq.ACCEPT_JUDGMENTS)
        # 独立ASRが同じ誤り転写なら受理しない
        j2 = eq.classify_connected_speech_equivalence("pay showed coffee", "pay show coffee",
                                                      secondary_asr_text="pay show coffee",
                                                      local_asr_text="pay show coffee")["layer_judgment"]
        self.assertNotIn(j2, eq.ACCEPT_JUDGMENTS)

    def test_post_slowdown_wiring(self):
        import types
        import er003_v1_n3_01_tts_generate as gen
        calls = []
        orig = gen.secondary_asr.evaluate_attempt_with_cascade_detail

        def fake(*a, **k):
            calls.append(k)
            return {"classification": None, "verified": False, "cascade_invoked": True, "final_status": "X", "steps": []}
        gen.secondary_asr.evaluate_attempt_with_cascade_detail = fake
        try:
            # (1) TRUE_CONTENT_MISMATCH -> 減速後経路は即False。cascade(=Eq Layer入口)を一切呼ばない
            cls = types.SimpleNamespace(classification="TRUE_CONTENT_MISMATCH")
            self.assertFalse(gen._post_slowdown_cascade_rescue({}, "pay showed coffee", "pay show coffee", cls, "x.wav", "full_story_part1"))
            self.assertEqual(calls, [])
            # (2) UNCERTAIN -> cascadeが呼ばれる(feature flag有効時)。ただし Eq Layer flag は渡されない(未配線の記録: OPEN-122(4))
            if gen.secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED:
                cls = types.SimpleNamespace(classification="ASR_VALIDATION_UNCERTAIN")
                gen._post_slowdown_cascade_rescue({}, "Melos said.", "Mello said.", cls, "x.wav", "full_story_part1")
                self.assertEqual(len(calls), 1)
                self.assertNotIn("enable_connected_speech_equivalence_layer", calls[0])
        finally:
            gen.secondary_asr.evaluate_attempt_with_cascade_detail = orig

    def test_equivalence_layer_entry_is_true_content_mismatch_only(self):
        import inspect
        import er006_secondary_asr_01 as sa
        src = inspect.getsource(sa.evaluate_attempt_with_cascade_detail)
        self.assertIn('cls.classification == "TRUE_CONTENT_MISMATCH"', src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
