# ============================================================
# er003_news_tail_fix_semantic_equivalence_surfacing_02_test_01.py
# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(D-4)
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe -m unittest \
#       er003_news_tail_fix_semantic_equivalence_surfacing_02_test_01 -v
#
# API呼び出し: 0(TTSパイプラインとPrimary ASRのみモック、Tier1判定
# ロジック自体は実物をそのまま通す。モック方式はer021_en_asr_semantic_
# equivalence_production_wiring_01_test_01.NewsTailFixB1WiringFixTestと
# 同一のharnessを踏襲する[別ファイルとして新規作成、既存ファイルは無編集
# =他Agent[EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02]との衝突回避])。
#
# 対象(D-4、Gate 3表「runtime確認済み」過大記載の是正): FULL_STORY経路
# (`er003_v1_sing01_news_tail_fix.generate_news_narration_wide_margin`)の
# attempts_log/attempt_audio/top-level戻り値へ`semantic_equivalence_info`
# を昇格する(既存のconnected_speech_info等と同じ昇格パターン)。
# classify_asr_match/cascade側のtelemetry.jsonl記録自体は既存のまま
# (無変更)であり、本Itemはこの関数のartifact(tts_generation_results.json
# 等)側の可視性gapのみを埋める。
from __future__ import annotations

import os
import shutil
import tempfile
import unittest

import er003_v1_sing01_news_tail_fix as news_tail_fix


class FullStoryNewsTailFixSemanticEquivalenceSurfacingTest(unittest.TestCase):
    CANONICAL = "The price rose to two point three million dollars this year."
    ASR_NUMERIC_EQUIVALENT = "The price rose to $2.3 million this year."

    def setUp(self):
        import numpy as np
        self.np = np
        self.tmp_dir = tempfile.mkdtemp(prefix="er003_news_tail_fix_semeq_surfacing_")
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

    def test_full_story_part1_semantic_equivalence_info_surfaced_top_level_and_attempts_log(self):
        narration_dir = os.path.join(self.tmp_dir, "wiring_theme_flx2", "b1b", "narration")
        os.makedirs(narration_dir, exist_ok=True)
        out_path = os.path.join(narration_dir, "full_story_part1.wav").replace("\\", "/")

        result = news_tail_fix.generate_news_narration_wide_margin(self.CANONICAL, out_path, max_attempts=3)

        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["audio_classification"], "NUMERIC_EQUIVALENCE_MATCH")
        # D-4是正: top-levelへ昇格済みで、Tier1発火時は非None。
        self.assertIsNotNone(result.get("semantic_equivalence_info"),
                              "FULL_STORY roleでTier1発火時、top-levelのsemantic_equivalence_infoが"
                              "Noneのままではいけない(D-4是正対象)")
        self.assertEqual(result["semantic_equivalence_info"]["tier_applied"], "tier1_numeric")
        # attempts_log側にも同じキーで昇格していることを確認する。
        self.assertIn("semantic_equivalence_info", result["attempts_log"][0])
        self.assertEqual(result["attempts_log"][0]["semantic_equivalence_info"]["tier_applied"], "tier1_numeric")

    def test_non_applicable_role_semantic_equivalence_info_key_present_but_none(self):
        # HEADING(非適用role)ではTier1自体が発火しないため、
        # semantic_equivalence_infoはNoneのまま(キー自体は存在する
        # =昇格ロジックが例外を投げないことの確認)。
        narration_dir = os.path.join(self.tmp_dir, "wiring_theme_flx2", "b1b", "narration")
        os.makedirs(narration_dir, exist_ok=True)
        out_path = os.path.join(narration_dir, "point_one_heading.wav").replace("\\", "/")

        result = news_tail_fix.generate_news_narration_wide_margin(self.CANONICAL, out_path, max_attempts=1)

        self.assertNotEqual(result.get("status"), "OK")
        self.assertIn("semantic_equivalence_info", result["attempts_log"][0])
        self.assertIsNone(result["attempts_log"][0]["semantic_equivalence_info"])


def run():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(FullStoryNewsTailFixSemanticEquivalenceSurfacingTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    run()
