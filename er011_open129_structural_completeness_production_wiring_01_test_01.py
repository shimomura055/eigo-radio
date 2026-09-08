# ============================================================
# er011_open129_structural_completeness_production_wiring_01_test_01.py
# OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01
# ============================================================
# 回帰テスト。run_project_regression.py(er0*_test_*.py自動探索)対象。
# TTS/LLM呼び出しなし、synthetic固定データのみ使用(¥0)。
from __future__ import annotations

import copy
import json
import os
import shutil
import tempfile
import unittest

import er003_v1_n3_01_assemble as asm
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_production_runner_01 as runner
import er012_b_family_voices_a2_production_01 as a2prod


def make_full_b1_segments(voice_a="Algieba", voice_b="Erinome", family=True):
    names_voice = {
        "topic_intro": "Charon", "preview": "Charon",
        "comment_1": "Charon", "comment_2": "Charon", "comment_3": "Charon", "comment_4": "Charon",
        "point_one_heading": "Aoede", "point_two_heading": "Aoede",
        "point_one": voice_a, "point_two": voice_b,
        "full_story_part1": None, "full_story_part2": None,
        "in_one_line": None,
    }
    if family:
        names_voice["tension_reflection"] = None
    segs = {}
    for name, voice in names_voice.items():
        segs[name] = {"status": "OK", "voice": voice, "disfluency_checked": True,
                      "canonical_text": f"text for {name}", "sha256": None, "path": None}
    kp = {str(r): {"english": {"status": "OK", "disfluency_checked": True},
                   "japanese": {"status": "OK", "disfluency_checked": True}} for r in range(1, 6)}
    return {"segments": segs, "key_phrases": kp}


def write_temp_results(data: dict) -> str:
    out_dir = tempfile.mkdtemp(prefix="open129_test_")
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return out_dir


class RequiredStructureDerivationTest(unittest.TestCase):
    def test_a_family_a2_structure_has_14_segments_all_aoede(self):
        rs = asm.derive_a_family_required_structure("A2")
        names = [n for n, _ in rs["segments"]]
        self.assertEqual(len(names), 14)
        self.assertIn("japanese_title", names)
        self.assertTrue(all(v == "Aoede" for _, v in rs["segments"]))

    def test_a_family_b1_structure_has_13_segments_no_tension(self):
        rs = asm.derive_a_family_required_structure("B1")
        names = [n for n, _ in rs["segments"]]
        self.assertEqual(len(names), 13)
        self.assertNotIn("tension_reflection", names)
        self.assertNotIn("japanese_title", names)

    def test_unknown_level_raises(self):
        with self.assertRaises(ValueError):
            asm.derive_a_family_required_structure("B_FAMILY_A2")

    def test_b_family_b1_vs_a_family_b1_differ_despite_same_level_string(self):
        """level="B1"という同一文字列でも、A-Family/B-Familyで構造が異なる
        (OPEN-129の起点となった既知の欠落)ことを、正本同士の比較で明示する。"""
        a_family = asm.derive_a_family_required_structure("B1")
        b_family = registry.build_required_structure("b1", "Algieba", "Erinome")
        a_names = {n for n, _ in a_family["segments"]}
        b_names = {n for n, _ in b_family["segments"]}
        self.assertNotEqual(a_names, b_names)
        self.assertIn("tension_reflection", b_names)
        self.assertNotIn("tension_reflection", a_names)

    def test_b_family_a2_required_structure_resolves_voice_a_b(self):
        rs = registry.build_required_structure("a2", "Algieba", "Erinome")
        by_name = dict(rs["segments"])
        self.assertEqual(by_name["point_one"], "Algieba")
        self.assertEqual(by_name["point_two"], "Erinome")
        self.assertEqual(by_name["topic_intro"], "Charon")
        self.assertEqual(rs["key_phrase_ranks"], 5)
        self.assertEqual(rs["key_phrase_subkey_count"], 2)


class GateOptInDefaultOffUnchangedTest(unittest.TestCase):
    """既定(required_structure未指定)で既存Gate挙動が変わらないこと。"""

    def setUp(self):
        self.data = make_full_b1_segments()
        del self.data["segments"]["full_story_part2"]  # segment欠落(構造完全性違反)
        self.out_dir = write_temp_results(self.data)

    def tearDown(self):
        shutil.rmtree(self.out_dir, ignore_errors=True)

    def test_missing_segment_not_detected_when_required_structure_omitted(self):
        # 既定(required_structure省略)ではentry自体が無いsegmentは検知しない
        # (OPEN-129がまさに指摘した既存の未対策領域、Gate自体は無変更)。
        try:
            asm.verify_episode_audio_validation_gate(self.out_dir, "B1")
        except RuntimeError as e:
            self.fail(f"required_structure省略時にBLOCKEDになった(既存挙動が変化): {e}")


class GateOptInStructuralCompletenessTest(unittest.TestCase):
    """opt-in(required_structure指定)時の検知/非検知(reorderは対象外)。"""

    def setUp(self):
        self.base = make_full_b1_segments()
        self.rs = registry.build_required_structure("b1", "Algieba", "Erinome")

    def _run(self, data):
        out_dir = write_temp_results(data)
        try:
            asm.verify_episode_audio_validation_gate(out_dir, "B1", required_structure=self.rs)
            return False, None
        except RuntimeError as e:
            return True, str(e)
        finally:
            shutil.rmtree(out_dir, ignore_errors=True)

    def test_baseline_not_detected(self):
        detected, _ = self._run(copy.deepcopy(self.base))
        self.assertFalse(detected)

    def test_delete_segment_detected(self):
        data = copy.deepcopy(self.base)
        del data["segments"]["full_story_part2"]
        detected, msg = self._run(data)
        self.assertTrue(detected)
        self.assertIn("full_story_part2", msg)
        self.assertIn("STRUCTURAL_COMPLETENESS", msg)

    def test_voice_swap_detected(self):
        data = copy.deepcopy(self.base)
        data["segments"]["point_one"]["voice"], data["segments"]["point_two"]["voice"] = \
            data["segments"]["point_two"]["voice"], data["segments"]["point_one"]["voice"]
        detected, msg = self._run(data)
        self.assertTrue(detected)
        self.assertIn("VOICE_MISMATCH", msg)

    def test_extra_segment_detected(self):
        data = copy.deepcopy(self.base)
        data["segments"]["unexpected_bonus_segment"] = {
            "status": "OK", "voice": "Aoede", "canonical_text": "x", "sha256": None, "path": None,
        }
        detected, msg = self._run(data)
        self.assertTrue(detected)
        self.assertIn("UNEXPECTED_EXTRA_SEGMENT", msg)

    def test_reorder_not_detected_negative_control(self):
        data = copy.deepcopy(self.base)
        items = list(data["segments"].items())
        items[0], items[1] = items[1], items[0]
        data["segments"] = dict(items)
        detected, _ = self._run(data)
        self.assertFalse(detected)

    def test_incomplete_key_phrase_subentries_detected(self):
        data = copy.deepcopy(self.base)
        del data["key_phrases"]["3"]["japanese"]
        detected, msg = self._run(data)
        self.assertTrue(detected)
        self.assertIn("INCOMPLETE_KEY_PHRASE_SUBENTRIES", msg)

    def test_missing_key_phrase_rank_detected(self):
        data = copy.deepcopy(self.base)
        del data["key_phrases"]["5"]
        detected, msg = self._run(data)
        self.assertTrue(detected)
        self.assertIn("MISSING_KEY_PHRASE_RANK", msg)


class RetryRegenerationSegmentSetConsistencyTest(unittest.TestCase):
    """retry/regeneration整合: 再生成後もsegment集合が変わらないこと
    (コード追跡)。A2はreuse+新規生成のmergeで完全集合を維持
    (finalize_tts_results_a2)、B1はrun_tts()が常に固定の14segmentを
    生成する(finalize_tts_results)。いずれも、registry正本の
    required_segments名集合と一致することを確認する。"""

    def test_a2_reused_plus_new_segments_equals_required_structure_names(self):
        reused_or_new = set(runner.A2_SEGMENTS_TO_REUSE) | {"point_one", "point_two"}
        rs = registry.build_required_structure("a2", "Algieba", "Erinome")
        required_names = {n for n, _ in rs["segments"]}
        self.assertEqual(reused_or_new, required_names)

    def test_check_required_segments_completeness_unaffected_by_new_gate_argument(self):
        """既存のLane B runner側完全性チェック(a2prod.check_required_
        segments_completeness、Gate統合とは別物)が、本タスクのregistry
        追加キー(key_phrase_ranks等)によって壊れていないことを確認する。"""
        a2_config = registry.get_editorial_type_a2()
        required = a2_config["required_segments"]
        segment_status = {name: "OK" for name, _ in required}
        result = a2prod.check_required_segments_completeness(segment_status, "Algieba", "Erinome")
        self.assertTrue(result["complete"])
        self.assertEqual(result["expected_segment_count"], len(required))


if __name__ == "__main__":
    unittest.main()
