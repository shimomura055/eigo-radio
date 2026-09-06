# ============================================================
# er011_assembly_headroom_safety_valve_production_wiring_01_test_01.py
# ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-PRODUCTION-WIRING-01
# ============================================================
# 由来: OPEN-115(A2/B1 Assembly最終段のヘッドルーム不在)。
# `mono_24k_to_stereo_target()`内の`resample_poly`(24kHz→48kHz)が
# ゲイン制御の外にあり、内容依存で最大+8.9%程度のオーバーシュートを
# 起こすため(Trial-13 A2実測、OPEN-112-TREND-THEME2-B-A2-PEAK-
# MEASUREMENT-16で確定)、完成ミックス最終段へ一律ヘッドルーム安全弁
# (`apply_headroom_safety_valve`)を追加した。本テストは、ユーザー承認済み
# 仕様(閾値HEADROOM_PEAK_THRESHOLD・記録・例外化)を恒久固定する回帰。
#
# 対象4件(タスク指定の最低要件):
#   (a) peak<=閾値ならbyte同一(一切変更しない)
#   (b) peak>閾値で一律ゲイン適用・記録(相対バランス維持・原因piece記録)
#   (c) 適用後もpeak>1.0ならRuntimeError(write_wav_float()のassertより前)
#   (d) gain_report.json/timeline.json/headroom_report.jsonが
#       write_wav_float()より前に書き出されていること(write失敗時にも
#       audit証跡が残ることを実際のstage_assemble_a2で確認)
# 加えて、Production初回経路(stage_assemble_a2/stage_assemble_b1)へ
# 単一箇所で配線されていることを固定する。

import inspect
import os
import shutil
import tempfile
import unittest

import numpy as np

import er003_v1_n3_01_assemble as asm


def _sine_mono(duration_s: float = 0.02, amplitude: float = 0.3, freq: float = 440.0, sr: int = 24000):
    n = max(1, int(round(duration_s * sr)))
    t = np.arange(n) / sr
    return (amplitude * np.sin(2 * np.pi * freq * t)).astype(np.float64)


def _stereo_48k(duration_s: float = 0.02, amplitude: float = 0.3, freq: float = 440.0, sr: int = 48000):
    n = max(1, int(round(duration_s * sr)))
    t = np.arange(n) / sr
    mono = (amplitude * np.sin(2 * np.pi * freq * t)).astype(np.float64)
    return np.stack([mono, mono], axis=-1)


def _fake_a2_sources() -> dict:
    """load_a2_sources()の戻り値と同じ形の、安全な低振幅ダミーsources
    (実TTS/ASRを一切使わない、配線順序[write前にaudit証跡が存在するか]
    だけを検証するための合成データ)。"""
    narration_names_mono = [
        "welcome", "preview_intro", "point_explanation", "key_phrases_intro",
        "full_story_intro", "num_one", "num_two", "num_three", "num_four", "num_five",
        "topic_intro", "japanese_title", "meaning_1", "meaning_2",
    ]
    narration = {name: _sine_mono() for name in narration_names_mono}
    a2_segment_names = [
        "comment_1", "comment_2", "comment_3", "comment_4",
        "full_story_part1", "full_story_part2", "point_one", "point_two",
        "point_one_heading", "point_two_heading", "in_one_line",
    ]
    a2_segments = {name: _sine_mono(duration_s=0.05) for name in a2_segment_names}
    return {
        "intro": {"samples": _stereo_48k()}, "notification": {"samples": _stereo_48k()},
        "point_notification": {"samples": _stereo_48k()}, "outro": {"samples": _stereo_48k()},
        "preview_mono": _sine_mono(duration_s=0.05), "narration": narration,
        "key_phrase_components": {1: _sine_mono(), 2: _sine_mono()},
        "a2_segments": a2_segments, "kp_items": [{"rank": 1}, {"rank": 2}],
    }


class HeadroomSafetyValveUnitTests(unittest.TestCase):
    """apply_headroom_safety_valve()自体の分岐(a)(b)(c)を、実Assemblyを
    経由せず直接固定する。"""

    def test_a_below_threshold_is_byte_identical_and_unmodified(self):
        seq = [("piece_a", np.full((100, 2), 0.5, dtype=np.float64)),
               ("piece_b", np.full((100, 2), 0.3, dtype=np.float64))]
        assembled = np.ascontiguousarray(np.concatenate([s for _, s in seq], axis=0))
        result = asm.apply_headroom_safety_valve(assembled, seq)
        self.assertIs(result["assembled"], assembled, "閾値以下では同一オブジェクト(byte同一)を返すべきです")
        self.assertFalse(result["report"]["applied"])
        self.assertEqual(result["report"]["scalar"], 1.0)
        self.assertEqual(result["report"]["peak_before"], result["report"]["peak_after"])

    def test_b_above_threshold_applies_uniform_gain_and_records_cause(self):
        seq = [("loud_piece", np.full((10, 2), 1.05, dtype=np.float64)),
               ("quiet_piece", np.full((10, 2), 0.20, dtype=np.float64))]
        assembled = np.ascontiguousarray(np.concatenate([s for _, s in seq], axis=0))
        result = asm.apply_headroom_safety_valve(assembled, seq)
        report = result["report"]
        self.assertTrue(report["applied"])
        self.assertEqual(report["cause_piece"], "loud_piece")
        self.assertAlmostEqual(report["cause_piece_peak"], 1.05, places=6)
        expected_scalar = asm.HEADROOM_PEAK_THRESHOLD / 1.05
        self.assertAlmostEqual(report["scalar"], expected_scalar, places=6)
        scaled = result["assembled"]
        self.assertLessEqual(float(np.max(np.abs(scaled))), asm.HEADROOM_PEAK_THRESHOLD + 1e-9)
        # 相対バランス(全体一律スカラーのため、pieceどうしの比は不変)
        ratio_before = 1.05 / 0.20
        ratio_after = float(scaled[0, 0]) / float(scaled[-1, 0])
        self.assertAlmostEqual(ratio_before, ratio_after, places=6)

    def test_c_insufficient_headroom_raises_runtime_error(self):
        seq = [("extreme_piece", np.full((5, 2), 2.0, dtype=np.float64))]
        assembled = np.ascontiguousarray(np.concatenate([s for _, s in seq], axis=0))
        orig_threshold = asm.HEADROOM_PEAK_THRESHOLD
        # Production既定(0.98)では「適用後もpeak>1.0」は原理的に起きない
        # (scalar=threshold/peak_beforeなのでpeak_after==threshold<1.0)。
        # この異常系分岐そのものを固定するため、閾値を一時的に1.5へ変更し、
        # scalar適用後もpeak(2.0*0.75=1.5)が1.0を超える状況を再現する。
        asm.HEADROOM_PEAK_THRESHOLD = 1.5
        try:
            with self.assertRaises(RuntimeError) as ctx:
                asm.apply_headroom_safety_valve(assembled, seq)
            self.assertIn("ASSEMBLY_HEADROOM_SAFETY_VALVE_INSUFFICIENT", str(ctx.exception))
            self.assertIn("extreme_piece", str(ctx.exception))
        finally:
            asm.HEADROOM_PEAK_THRESHOLD = orig_threshold


class AuditWriteOrderingTests(unittest.TestCase):
    """(d) gain_report.json/timeline.json/headroom_report.jsonが
    write_wav_float()より前に書き出されることを、実際のstage_assemble_a2
    (Production関数そのもの)で確認する。sources自体は合成データに
    差し替えるが、stage_assemble_a2の内部ロジック(headroom適用→
    audit書き出し→write_wav_float)は一切変更せず呼び出す。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="er011_headroom_wiring01_")
        self._orig_load_a2_sources = asm.load_a2_sources
        self._orig_write_wav_float = asm.common.write_wav_float
        asm.load_a2_sources = lambda theme: _fake_a2_sources()

        def _boom(*args, **kwargs):
            raise AssertionError("simulated_write_wav_float_failure_for_ordering_test")
        asm.common.write_wav_float = _boom

    def tearDown(self):
        asm.load_a2_sources = self._orig_load_a2_sources
        asm.common.write_wav_float = self._orig_write_wav_float
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_d_audit_files_exist_before_write_wav_float_is_reached(self):
        theme = {"theme_id": "fake_headroom_ordering_test", "out_dir": self.tmp}
        with self.assertRaises(AssertionError):
            asm.stage_assemble_a2(theme)
        out_dir = f"{self.tmp}/a2"
        self.assertTrue(os.path.exists(f"{out_dir}/audit/gain_report.json"))
        self.assertTrue(os.path.exists(f"{out_dir}/audit/timeline.json"))
        self.assertTrue(os.path.exists(f"{out_dir}/audit/headroom_report.json"))
        # write_wav_floatをmockしているため、完成wav自体は生成されていない
        # ことも確認する(=証跡だけが先行して残るという意図どおりの動作)。
        self.assertFalse(os.path.exists(
            f"{out_dir}/assembled/English_Your_Way_A2_FAKE_HEADROOM_ORDERING_TEST.wav"))


class ProductionWiringSingleCallSiteTests(unittest.TestCase):
    """初回/retry/reassembly/regenerationが共有する唯一の関数
    (stage_assemble_a2/stage_assemble_b1)に、それぞれ1箇所だけ
    apply_headroom_safety_valve()が配線されていることを固定する。"""

    def test_stage_assemble_a2_calls_headroom_safety_valve_exactly_once(self):
        src = inspect.getsource(asm.stage_assemble_a2)
        self.assertEqual(src.count("apply_headroom_safety_valve("), 1)

    def test_stage_assemble_b1_calls_headroom_safety_valve_exactly_once(self):
        src = inspect.getsource(asm.stage_assemble_b1)
        self.assertEqual(src.count("apply_headroom_safety_valve("), 1)


if __name__ == "__main__":
    unittest.main()
