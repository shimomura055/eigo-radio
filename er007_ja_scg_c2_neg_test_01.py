# ============================================================
# er007_ja_scg_c2_neg_test_01.py
# OPEN-258 SCG 委任_03(2026-10-11ユーザー正式採用 APPROVED_FOR_PRODUCTION):
#   C2 同形異音語ガード / 推奨4 否定マーカー追加 の単体・統合test(課金0、Azure/LLMはmock)。
# ============================================================
from __future__ import annotations

import types
import unittest
from unittest import mock

import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as ja_secondary

excl = ja_secondary._scg_exclusion_reason


def fake_cls(diffs):
    prot = types.SimpleNamespace(number_mismatches=[], negation_mismatches=[], content_diffs=diffs)
    return types.SimpleNamespace(classification="TRUE_CONTENT_MISMATCH", protected=prot, similarity_ratio=0.9)


def d(c, a):
    return {"canonical": c, "asr": a, "entity_like": False}


class _Base(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False)
        p.start()
        self.addCleanup(p.stop)
        a = mock.patch.object(ja_secondary, "_azure_stt_strict")
        self.mock_azure = a.start()
        self.addCleanup(a.stop)

    def detail(self, canon, primary):
        return ja_secondary.evaluate_attempt_ja_with_cascade_detail(canon, primary, "dummy.wav", cascade_enabled=True)


class C2HeterophoneGuard(_Base):
    def test_heterophone_diffs_excluded_unit(self):
        # Primaryが書いた読みが原稿漢字の正当な読み候補に含まれる -> SCGにしない(NG=従来の再生成)
        for c, a in [("市場", "いちば"), ("市場", "しじょう"), ("一日", "ついたち"), ("一日", "いちにち"),
                     ("生物", "なまもの"), ("生物", "せいぶつ"), ("上手", "うわて"), ("上手", "かみて")]:
            r = excl(fake_cls([d(c, a)]))
            self.assertTrue(str(r).startswith("heterophone_reading_candidate"), (c, a, r))

    def test_misrecognition_not_over_excluded_unit(self):
        # Phase 0の救済事例(読みが候補に無い単なる誤認識)は除外しない
        for c, a in [("出演", "出現"), ("拒絶", "強制"), ("理屈", "肉"), ("演", "現"), ("絶", "制")]:
            self.assertIsNone(excl(fake_cls([d(c, a)])), (c, a))

    def test_unknown_reading_dictionary_missing_is_not_excluded(self):
        # 辞書に候補が無い(None)場合は除外しない(過剰除外防止)。既知の限界: 「行った」に対する
        # 「おこなった」は辞書(行: ぎょう/あん/こう/ゆき/いき)に読み候補が無く検知できない。
        self.assertIsNone(excl(fake_cls([d("行", "おこな")])))
        self.assertIsNone(excl(fake_cls([d("行った", "おこなった")])))

    def test_end_to_end_ichinichi_not_scg_pass(self):
        # 一日中雨でした / Primary「ついたち中」(TRUE_CONTENT_MISMATCH)。Azureが原稿どおり返しても誤PASSにしない
        canon, primary = "一日中雨でした", "ついたち中雨でした"
        self.mock_azure.return_value = (canon, None)
        r = self.detail(canon, primary)
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertFalse(r["verified"])
        self.assertEqual(r["scg_result"], "NOT_APPLIED")
        self.assertTrue(r["scg_info"]["exclusion_reason"].startswith("heterophone_reading_candidate"))
        self.assertTrue(r["classification"].should_retry)  # 従来の再生成へ

    def test_end_to_end_phase0_rescue_example_still_passes(self):
        canon, primary = "AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした", "AIの電話に人間が出現。問題は、キャスト変更のお知らせでした。"
        self.mock_azure.return_value = ("AIの電話に人間が出演。問題はキャスト変更のお知らせでした。", None)
        r = self.detail(canon, primary)
        self.assertEqual(self.mock_azure.call_count, 1)
        self.assertTrue(r["verified"])
        self.assertEqual(r["scg_result"], "PASS")

    def test_phonetic_match_primary_never_reaches_scg(self):
        # 同形異音語がPrimaryでPHONETIC_MATCH(既存判定でTRUE_CONTENT_MISMATCHでない)ならSCGの対象外(挙動不変)
        for c, p in [("今日は市場に行きます", "今日はいちばに行きます"), ("生物を観察する", "なまものを観察する"),
                     ("上手に歌う", "うわてに歌う")]:
            r = self.detail(c, p)
            self.assertNotIn("scg_result", r, c)
            self.assertEqual(self.mock_azure.call_count, 0)


class Rec4NegationMarker(_Base):
    def neg(self, c, a):
        return ja_secondary._scg_negation_marker_diff(c, a)

    def test_negation_present_only_in_canonical_excluded(self):
        for c, a in [("縛られず自由に", "縛られる自由に"), ("彼は行かず帰る", "彼は行く帰る"),
                     ("許されざる行為", "許される行為"), ("知らぬ顔", "知る顔"), ("行くまい", "行くだろう"),
                     ("行きません", "行きます")]:
            self.assertIsNotNone(self.neg(c, a), (c, a))

    def test_negation_present_only_in_primary_excluded(self):
        for c, a in [("縛られる自由に", "縛られず自由に"), ("行きます", "行きません")]:
            self.assertIsNotNone(self.neg(c, a), (c, a))

    def test_negative_both_sides_same_marker_not_excluded(self):
        for c, a in [("彼は食べず私は寝ず", "彼は食べず私は寝ず"), ("行きません", "行きません")]:
            self.assertIsNone(self.neg(c, a), (c, a))

    def test_question_invitation_masen_ka_not_negation(self):
        self.assertIsNone(self.neg("一緒に行きませんか", "一緒に行きますか"))
        self.assertIsNone(self.neg("行きませんか", "行きますか"))

    def test_negation_outside_diff_not_excluded(self):
        # 差分外に否定語がある文(差分は「出演/出現」のみ)
        self.assertIsNone(self.neg("彼は来ず、出演した", "彼は来ず、出現した"))
        self.assertIsNone(self.neg("私は行かず帰る。出演者が来た", "私は行かず帰る。出現者が来た"))

    def test_mai_as_noun_part_not_excluded(self):
        # 「まい」が名詞の一部(毎日まいにち/迷子まいご/枚)
        self.assertIsNone(self.neg("まいにち出演する", "まいにち出現する"))
        self.assertIsNone(self.neg("まいごの子を探す", "まいごの犬を探す"))
        self.assertIsNone(self.neg("まいにち行く", "まいにち行った"))

    def test_zu_nu_inside_words_not_excluded(self):
        # 「ずっと」「ぬいぐるみ」「いぬ」等の部分文字列は否定ではない(単純な部分文字列判定でない証拠)
        for c, a in [("ずっと犬と行く", "ずっと猫と行く"), ("犬のぬいぐるみ", "猿のぬいぐるみ"),
                     ("ずっと出演する", "ずっと出現する")]:
            self.assertIsNone(self.neg(c, a), (c, a))

    def test_exclusion_reason_uses_negation_only_when_texts_given(self):
        cls = fake_cls([d("ず", "る")])
        self.assertIsNone(excl(cls))  # texts無し=従来どおり
        r = excl(cls, "縛られず自由に", "縛られる自由に")
        self.assertTrue(r.startswith("negation_marker_diff"), r)

    def test_end_to_end_g12_type_not_executed(self):
        canon, primary = "縛られず自由に生きる", "縛られる自由に生きる"
        self.mock_azure.return_value = (canon, None)  # Azureが原稿寄りに丸めても
        r = self.detail(canon, primary)
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertFalse(r["verified"])
        self.assertTrue(r["scg_info"]["exclusion_reason"].startswith(("negation_marker_diff", "negation_mismatch")))

    def test_fail_open_when_morph_unavailable(self):
        with mock.patch.object(ja_secondary, "_scg_negation_ranges", return_value=None):
            self.assertIsNone(self.neg("縛られず自由に", "縛られる自由に"))

    def test_shared_negation_logic_untouched(self):
        import er003_audio_tts_asr_safety as safety
        self.assertEqual(safety._NEGATION_MARKERS_JA, ("ない", "じゃない", "ではない", "でない", "せず", "未", "非", "無", "なく"))
        self.assertFalse(safety._has_negation_ja("縛られず"))  # 共通判定は従来どおり「ず」を検出しない


if __name__ == "__main__":
    unittest.main()
