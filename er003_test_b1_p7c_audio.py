# ============================================================
# er003_test_b1_p7c_audio.py
# ER-003-B1-P7C: er003_b1_p7c_audioの回帰テスト
# ============================================================
# 実TTS/MFA/Azure STT呼び出しは行わない。marker除去+英語Component
# 挿入のコアロジックは、合成波形(サンプル値で発話/無音を模した配列)で
# 検証する。

import unittest

import numpy as np

import er003_b1_p7c_audio as p7c


def _tone(n_samples: int, value: float = 0.5) -> "np.ndarray":
    return np.full(n_samples, value, dtype=np.float64)


def _silence(n_samples: int) -> "np.ndarray":
    return np.zeros(n_samples, dtype=np.float64)


class RemoveMarkersAndInsertComponentsTests(unittest.TestCase):
    """1000Hzサンプルレート相当の合成配列で、2marker・2Component挿入を
    行い、除去・無音調整・連結が仕様通りかを検証する(実データ非依存)。"""

    def setUp(self):
        self.sr = 1000  # 1サンプル=1ms、検証しやすい単位
        # 構造: [ja0(speech200)] [marker1(speech50)] [ja1(speech300)]
        #        [marker2(speech50)] [ja2(speech200)]
        # 値を区別するため、区間ごとに異なる振幅を使う。
        ja0 = _tone(200, 0.10)
        marker1 = _tone(50, 0.99)
        ja1 = _tone(300, 0.20)
        marker2 = _tone(50, 0.98)
        ja2 = _tone(200, 0.30)
        self.full = np.concatenate([ja0, marker1, ja1, marker2, ja2])

        self.spans = [
            {"marker_id": "marker_1", "start_seconds": 0.200, "end_seconds": 0.250,
             "preceding_end_seconds": 0.200, "following_start_seconds": 0.250},
            {"marker_id": "marker_2", "start_seconds": 0.550, "end_seconds": 0.600,
             "preceding_end_seconds": 0.550, "following_start_seconds": 0.600},
        ]
        self.components = [_tone(30, 0.77), _tone(30, 0.66)]

    def test_marker_audio_is_removed(self):
        result = p7c.remove_markers_and_insert_components(self.full, self.sr, self.spans, self.components)
        assembled = result["assembled"]
        self.assertNotIn(0.99, assembled.tolist())
        self.assertNotIn(0.98, assembled.tolist())

    def test_component_audio_is_present_in_order(self):
        result = p7c.remove_markers_and_insert_components(self.full, self.sr, self.spans, self.components)
        assembled = result["assembled"].tolist()
        idx_77 = assembled.index(0.77)
        idx_66 = assembled.index(0.66)
        self.assertLess(idx_77, idx_66)

    def test_gaps_achieve_target_exactly(self):
        result = p7c.remove_markers_and_insert_components(self.full, self.sr, self.spans, self.components)
        for adj in result["silence_adjustments"]:
            if adj["side"] == "trailing_before_english":
                self.assertAlmostEqual(adj["achieved_trailing_seconds"], p7c.GAP_BEFORE_TARGET_SECONDS, places=6)
            else:
                self.assertAlmostEqual(adj["achieved_leading_seconds"], p7c.GAP_AFTER_TARGET_SECONDS, places=6)

    def test_adjacent_japanese_speech_content_unchanged(self):
        result = p7c.remove_markers_and_insert_components(self.full, self.sr, self.spans, self.components)
        for adj in result["silence_adjustments"]:
            self.assertTrue(adj["speech_content_unchanged"], adj)

    def test_component_positions_extract_correct_samples(self):
        result = p7c.remove_markers_and_insert_components(self.full, self.sr, self.spans, self.components)
        assembled = result["assembled"]
        pos1 = result["component_positions"][0]
        segment = assembled[pos1["assembled_start_sample"]:pos1["assembled_end_sample"]]
        self.assertTrue(np.all(segment == 0.77))

    def test_short_quiet_following_token_is_never_dropped(self):
        # P6Aで実際に発生した「短く静かなへの脱落」を再現しないことを
        # 確認する回帰テスト。following側のspeech値を非常に小さくしても
        # (=短く静かな日本語token)、speech_content_unchangedが真である
        # ことを検証する。
        ja0 = _tone(200, 0.10)
        marker1 = _tone(50, 0.99)
        quiet_tail = _tone(20, 0.001)  # 短く静かな「へ」相当
        full = np.concatenate([ja0, marker1, quiet_tail])
        spans = [{"marker_id": "marker_1", "start_seconds": 0.200, "end_seconds": 0.250,
                  "preceding_end_seconds": 0.200, "following_start_seconds": 0.250}]
        result = p7c.remove_markers_and_insert_components(full, self.sr, spans, [_tone(30, 0.77)])
        leading_adj = [a for a in result["silence_adjustments"] if a["side"] == "leading_after_english"][0]
        self.assertTrue(leading_adj["speech_content_unchanged"])
        assembled = result["assembled"]
        self.assertIn(0.001, np.round(assembled, 3).tolist())


class RemoveMarkersAndInsertComponentsAbsolutePositionTests(unittest.TestCase):
    """achieved_*/speech_content_unchangedの自己参照チェックだけでは、
    中間segmentが「前markerのleading調整」と「次markerのtrailing調整」
    の両方を受ける際の処理順序バグ(2026-08-06、ユーザー試聴で実際に
    検出)を見逃すことが判明した(バグ下でもachieved値・speech_content_
    unchangedはいずれも自己整合的に真を返してしまうため)。本テストは、
    各segmentへ異なるtone値を割り当て、完成音声内でのそのtoneの実際の
    出現位置から独立に間隔を逆算することで、バグを検出できる形にする。
    3marker(中間segmentが2つ)で検証する。"""

    def setUp(self):
        self.sr = 1000
        ja0 = _tone(200, 0.11)
        marker1 = _tone(50, 0.99)
        ja1 = _tone(300, 0.22)  # 中間segment(leading+trailingの両方を受ける)
        marker2 = _tone(50, 0.98)
        ja2 = _tone(300, 0.33)  # 中間segment(leading+trailingの両方を受ける)
        marker3 = _tone(50, 0.97)
        ja3 = _tone(200, 0.44)
        self.full = np.concatenate([ja0, marker1, ja1, marker2, ja2, marker3, ja3])

        self.spans = [
            {"marker_id": "marker_1", "start_seconds": 0.200, "end_seconds": 0.250,
             "preceding_end_seconds": 0.200, "following_start_seconds": 0.250},
            {"marker_id": "marker_2", "start_seconds": 0.550, "end_seconds": 0.600,
             "preceding_end_seconds": 0.550, "following_start_seconds": 0.600},
            {"marker_id": "marker_3", "start_seconds": 0.900, "end_seconds": 0.950,
             "preceding_end_seconds": 0.900, "following_start_seconds": 0.950},
        ]
        self.components = [_tone(30, 0.71), _tone(30, 0.72), _tone(30, 0.73)]

    def _last_index_of(self, arr, value):
        idx = np.where(arr == value)[0]
        self.assertGreater(len(idx), 0, f"value {value} not found")
        return int(idx[-1])

    def _first_index_of(self, arr, value):
        idx = np.where(arr == value)[0]
        self.assertGreater(len(idx), 0, f"value {value} not found")
        return int(idx[0])

    def test_gap_before_each_english_component_is_correct_independent_of_ordering(self):
        result = p7c.remove_markers_and_insert_components(self.full, self.sr, self.spans, self.components)
        assembled = result["assembled"]

        # marker_2直前(ja1の末尾=0.22の最後の出現)からComponent2(0.72)の
        # 開始までの実際のサンプル距離を、achieved値に頼らず直接測る。
        last_ja1 = self._last_index_of(assembled, 0.22)
        first_comp2 = self._first_index_of(assembled, 0.72)
        gap_samples = first_comp2 - last_ja1 - 1
        gap_seconds = gap_samples / self.sr
        self.assertAlmostEqual(gap_seconds, p7c.GAP_BEFORE_TARGET_SECONDS, delta=0.005)

        # marker_3直前(ja2の末尾=0.33)からComponent3(0.73)まわりも同様に確認。
        last_ja2 = self._last_index_of(assembled, 0.33)
        first_comp3 = self._first_index_of(assembled, 0.73)
        gap2_seconds = (first_comp3 - last_ja2 - 1) / self.sr
        self.assertAlmostEqual(gap2_seconds, p7c.GAP_BEFORE_TARGET_SECONDS, delta=0.005)

    def test_gap_after_each_english_component_is_correct_independent_of_ordering(self):
        result = p7c.remove_markers_and_insert_components(self.full, self.sr, self.spans, self.components)
        assembled = result["assembled"]

        last_comp1 = self._last_index_of(assembled, 0.71)
        first_ja1 = self._first_index_of(assembled, 0.22)
        gap_seconds = (first_ja1 - last_comp1 - 1) / self.sr
        self.assertAlmostEqual(gap_seconds, p7c.GAP_AFTER_TARGET_SECONDS, delta=0.005)

        last_comp2 = self._last_index_of(assembled, 0.72)
        first_ja2 = self._first_index_of(assembled, 0.33)
        gap2_seconds = (first_ja2 - last_comp2 - 1) / self.sr
        self.assertAlmostEqual(gap2_seconds, p7c.GAP_AFTER_TARGET_SECONDS, delta=0.005)


class FidelityAndUsedFormCheckTests(unittest.TestCase):
    def test_japanese_fidelity_all_present(self):
        text = "".join(p7c.JAPANESE_FIDELITY_PHRASES)
        result = p7c.check_japanese_fidelity(text)
        self.assertTrue(result["all_present"])
        self.assertFalse(result["forbidden_form_present"])
        self.assertEqual(result["marker_residue_count"], 0)
        self.assertTrue(result["ok"])

    def test_japanese_fidelity_detects_forbidden_form(self):
        text = "".join(p7c.JAPANESE_FIDELITY_PHRASES) + "守備を固める"
        result = p7c.check_japanese_fidelity(text)
        self.assertTrue(result["forbidden_form_present"])
        self.assertFalse(result["ok"])

    def test_japanese_fidelity_detects_marker_residue(self):
        text = "".join(p7c.JAPANESE_FIDELITY_PHRASES) + "目印"
        result = p7c.check_japanese_fidelity(text)
        self.assertEqual(result["marker_residue_count"], 1)
        self.assertFalse(result["ok"])

    def test_english_used_forms_case_insensitive(self):
        text = "SHOT ON TARGET and Take Players Off and a Narrow Lead and Close The Door To The Final and STOPPAGE TIME"
        result = p7c.check_english_used_forms(text)
        self.assertTrue(result["all_present_at_least_once"])

    def test_english_used_forms_missing_one(self):
        text = "take players off, a narrow lead, close the door to the final, stoppage time"
        result = p7c.check_english_used_forms(text)
        self.assertFalse(result["shot on target"]["present"])
        self.assertFalse(result["all_present_at_least_once"])


class ModelIsolationTests(unittest.TestCase):
    def test_preview_and_article_body_models_differ(self):
        result = p7c.check_model_isolation()
        self.assertTrue(result["isolated"])
        self.assertEqual(result["article_body_model_common_module"], "gemini-2.5-pro-preview-tts")
        self.assertEqual(result["preview_model_used_in_p7a"], "gemini-3.1-flash-tts-preview")
        self.assertTrue(result["article_body_model_is_frozen_spec"])


class MeasureEffectiveGapsTests(unittest.TestCase):
    def test_within_tolerance_flags(self):
        spans = [{"marker_id": "marker_1"}]
        silence_adjustments = [
            {"marker_id": "marker_1", "side": "trailing_before_english",
             "achieved_trailing_seconds": 0.41, "speech_content_unchanged": True},
            {"marker_id": "marker_1", "side": "leading_after_english",
             "achieved_leading_seconds": 0.34, "speech_content_unchanged": True},
        ]
        result = p7c.measure_effective_gaps(spans, silence_adjustments, [1.0])
        self.assertTrue(result[0]["within_tolerance_before"])  # |0.41-0.40|=0.01<=0.03
        self.assertFalse(result[0]["within_tolerance_after"])  # |0.34-0.30|=0.04>0.03


if __name__ == "__main__":
    unittest.main()
