# ============================================================
# er003_test_b1_p9a_r1_audio.py
# ER-003-B1-P9A-R1: 修正版で追加した関数の回帰テスト
# ============================================================
# 実TTS/MFA/外部mp3呼び出しは行わない。合成データのみで検証する。

import unittest

import numpy as np

import er003_b1_p9a_audio as p9a


def _tone_stereo(n_samples: int, value: float = 0.3) -> "np.ndarray":
    return np.full((n_samples, 2), value, dtype=np.float64)


class BuildKeyPhraseBlockTests(unittest.TestCase):
    def setUp(self):
        self.sr = 1000
        self.number = _tone_stereo(100, 0.9)
        self.english = _tone_stereo(200, 0.5)
        self.japanese = _tone_stereo(150, 0.7)

    def test_order_is_number_english_japanese_english(self):
        block = p9a.build_key_phrase_block(self.number, self.english, self.japanese, self.sr)
        # 最初の100サンプルは番号(0.9)
        self.assertTrue(np.allclose(block[:100], 0.9))
        # 番号の直後、無音区間を挟んで英語(0.5)が2回、間に日本語(0.7)が1回現れる
        flat = block[:, 0]
        self.assertIn(0.9, flat.tolist())
        self.assertIn(0.5, flat.tolist())
        self.assertIn(0.7, flat.tolist())
        first_en_idx = flat.tolist().index(0.5)
        ja_idx = flat.tolist().index(0.7)
        second_en_idx = [i for i, v in enumerate(flat.tolist()) if v == 0.5 and i > ja_idx][0]
        self.assertLess(first_en_idx, ja_idx)
        self.assertLess(ja_idx, second_en_idx)

    def test_english_component_reused_identically_both_times(self):
        block = p9a.build_key_phrase_block(self.number, self.english, self.japanese, self.sr)
        flat = block[:, 0].tolist()
        count_05 = sum(1 for v in flat if v == 0.5)
        self.assertEqual(count_05, 400)  # 200サンプル×2回

    def test_block_ends_with_block_end_pause(self):
        block = p9a.build_key_phrase_block(self.number, self.english, self.japanese, self.sr)
        end_pause_samples = int(round(p9a.KEY_PHRASE_BLOCK_END_PAUSE_SECONDS * self.sr))
        tail = block[-end_pause_samples:]
        self.assertTrue(np.all(tail == 0.0))

    def test_is_stereo_shaped(self):
        block = p9a.build_key_phrase_block(self.number, self.english, self.japanese, self.sr)
        self.assertEqual(block.shape[1], 2)


class TrimTitleFromBodyTests(unittest.TestCase):
    def test_removes_only_prefix_keeps_body_unchanged(self):
        sr = 1000
        title = np.full(300, 0.9)  # タイトル部分(除去対象)
        gap = np.zeros(100)  # タイトルと本文の間の間
        body = np.full(500, 0.4)  # 本文第1文以降(保持対象)
        full = np.concatenate([title, gap, body])

        first_word_start_seconds = 0.4  # gap終了=bodyの開始(400サンプル目=0.4秒)
        result = p9a.trim_title_from_body(full, sr, first_word_start_seconds, natural_leading_seconds=0.05)
        trimmed = result["trimmed"]

        self.assertTrue(result["info"]["speech_content_unchanged"])
        # 本文の内容(0.4の値)が全てそのまま残っている
        self.assertEqual(int(np.sum(trimmed == 0.4)), 500)
        # タイトル(0.9の値)は残っていない
        self.assertEqual(int(np.sum(trimmed == 0.9)), 0)

    def test_natural_leading_silence_is_applied(self):
        sr = 1000
        title = np.full(300, 0.9)
        body = np.full(500, 0.4)
        full = np.concatenate([title, body])
        result = p9a.trim_title_from_body(full, sr, first_word_start_seconds=0.3, natural_leading_seconds=0.05)
        self.assertAlmostEqual(result["info"]["achieved_leading_seconds"], 0.05, places=6)


class NarrationTextConstantsV2Tests(unittest.TestCase):
    def test_v2_texts_match_user_instruction_verbatim(self):
        self.assertEqual(p9a.PODCAST_NAME_TEXT_V2, "Welcome to English Your Way.")
        self.assertEqual(p9a.KEY_PHRASES_INTRO_TEXT, "Here are today's key phrases.")
        self.assertEqual(p9a.POINT_EXPLANATION_TEXT, "ポイント解説")
        self.assertIn(p9a.ENGLISH_TITLE_TEXT, p9a.TOPIC_INTRO_TEXT_V2)
        self.assertTrue(p9a.TOPIC_INTRO_TEXT_V2.startswith("Today's topic is"))

    def test_five_key_phrases_defined_in_order(self):
        self.assertEqual(len(p9a.KEY_PHRASES), 5)
        self.assertEqual([kp["number"] for kp in p9a.KEY_PHRASES], ["One", "Two", "Three", "Four", "Five"])
        self.assertEqual([kp["english"] for kp in p9a.KEY_PHRASES],
                          ["shot on target", "take players off", "a narrow lead",
                           "close the door to the final", "stoppage time"])


if __name__ == "__main__":
    unittest.main()
