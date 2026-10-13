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
        self.assertEqual(self.tw("Melos said.", "Mello said.", {"second_engine_exact": True}), "許容")
        self.assertEqual(self.tw("Melos said.", "Mello said.", {"acoustic_geminate_ok": False}), "HR")
        self.assertEqual(self.tw("Melos said.", "Mello said.", {"acoustic_geminate_ok": False, "second_engine_exact": True}), "HR")

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
