# ============================================================
# er007_ja_scg_phase0_regression_test_01.py
# OPEN-258-JA-SECONDARY-ASR-PRODUCTION-WIRING-01: SCG(Secondary Confirm Gate)の
# Phase 0 保存音声regression(課金0)。
# Phase 0 Trialで実Azureが返した転写(er053_output/open258_phase0_trial_01/results_01.jsonl
# の抜粋=er007_ja_scg_phase0_fixture_01.jsonl)を固定fixtureとして再生し、Production関数
# evaluate_attempt_ja_with_cascade_detailが Phase 0 の結論どおりに判定することを回帰確認する。
# Azureは呼ばずfixtureの転写を返すmockのみ、OpenAI/LLM(Reading Resolver)もOFF。
# ============================================================
from __future__ import annotations

import json
import os
import unittest
from unittest import mock

import er003_b1_p4_audio as p4
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as ja_secondary

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er007_ja_scg_phase0_fixture_01.jsonl")


def _load():
    with open(FIXTURE, encoding="utf-8") as f:
        return {r["key"]: r for r in (json.loads(l) for l in f if l.strip())}


FIX = _load()

# ユーザー正式決定(2026-10-11): 要試聴6音声はすべて原稿どおりと確認済み
LISTEN_CONFIRMED_6 = ["g11_kp5_ja_aoede_a1", "g18_meaning_2_a2", "g18_meaning_2_a3",
                      "g1_meaning_4_a1", "g27_kp1_ja_charon_a1", "g35_japanese_title_a1"]
# 救済成功7群(Phase 0 RESULT_01 (2)): g8 g11 g17 g20 g27 g31 g33
RESCUE_SUCCESS_7_GROUPS = {8: ["g8_kp4_ja_charon_a1"], 11: ["g11_kp5_ja_aoede_a1"], 17: ["g17_kp5_ja_charon_a1"],
                           20: ["g20_kp2_ja_charon_a1"], 27: ["g27_kp1_ja_charon_a1"],
                           31: ["g31_meaning_2_a1"], 33: ["g33_meaning_5_a1", "g33_meaning_5_a2"]}
META_3 = ["g35_japanese_title_a1", "g35_japanese_title_a2", "g35_japanese_title_a3"]
# 誤PASS検証C群(TTS誤り代理)5音声
FALSE_PASS_C_5 = ["g12_kp1_ja_aoede_a2", "g3_kp4_ja_charon_a1", "g4_kp2_ja_charon_a1",
                  "g5_kp4_ja_charon_a1", "g6_kp5_ja_charon_a1"]
PHONETIC_3_GROUPS = ["g2_kp2_ja_charon_a1", "g21_comment_3_a1", "g36_comment_1_a1"]
G7_SHORT_EXCLUDED = "g7_meaning_4_a1"


def _run(key):
    """fixtureのPrimary転写+Azure転写(mock)でProduction関数を実行する。
    (detail, azure_call_count)を返す。"""
    rec = FIX[key]
    calls = {"n": 0}

    def fake_azure(*a, **k):
        calls["n"] += 1
        return rec["secondary_text"], None

    with mock.patch.object(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False), \
         mock.patch.object(p4, "get_full_text_via_azure_stt_continuous", side_effect=fake_azure), \
         mock.patch.object(ja_secondary, "FEATURE_FLAG_JA_SCG_ENABLED", True):
        detail = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            rec["canonical"], rec["primary_asr"], "dummy.wav", cascade_enabled=True)
    return detail, calls["n"]


class Phase0FixtureIntegrity(unittest.TestCase):
    def test_fixture_has_25_rows_and_expected_groups(self):
        self.assertEqual(len(FIX), 25)
        for k in (META_3 + FALSE_PASS_C_5 + PHONETIC_3_GROUPS + [G7_SHORT_EXCLUDED] + LISTEN_CONFIRMED_6):
            self.assertIn(k, FIX)


class Phase0Regression(unittest.TestCase):
    def test_listen_confirmed_6_audios_pass(self):
        for k in LISTEN_CONFIRMED_6:
            detail, n = _run(k)
            self.assertTrue(detail["verified"], k)
            self.assertEqual(detail["final_status"], ja_secondary.SCG_FINAL_STATUS, k)
            self.assertEqual(detail["classification"].classification, ja_secondary.SCG_FINAL_STATUS, k)
            self.assertEqual(n, 1, f"{k}: Azureは1回だけ")
            self.assertFalse(detail["stop_retrying"], k)

    def test_meta_3_of_3_rescued(self):
        for k in META_3:
            detail, _ = _run(k)
            self.assertTrue(detail["verified"], k)
            self.assertEqual(detail["scg_result"], "PASS")

    def test_rescue_success_7_groups_pass(self):
        total = 0
        for g, keys in RESCUE_SUCCESS_7_GROUPS.items():
            for k in keys:
                detail, _ = _run(k)
                self.assertTrue(detail["verified"], f"group {g} {k}")
                total += 1
        self.assertEqual(len(RESCUE_SUCCESS_7_GROUPS), 7)
        self.assertEqual(total, 8)  # 7群で救済対象8 audio(g33は2 attempt)

    def test_false_pass_c_group_5_audios_all_ng(self):
        for k in FALSE_PASS_C_5:
            detail, n = _run(k)
            self.assertFalse(detail["verified"], f"誤PASS検出: {k}")
            self.assertEqual(detail["scg_result"], "NG", k)
            self.assertEqual(n, 1)
            # 従来の再生成へ戻る(STOPにも新規HumanReviewにもならない)
            self.assertFalse(detail["stop_retrying"], k)
            self.assertFalse(detail["human_review_required"], k)
            self.assertEqual(detail["classification"].classification, "TRUE_CONTENT_MISMATCH", k)

    def test_phonetic_match_3_groups_are_not_auto_pass(self):
        for k in PHONETIC_3_GROUPS:
            self.assertEqual(FIX[k]["sec_cls"], "PHONETIC_MATCH", k)
            detail, _ = _run(k)
            self.assertFalse(detail["verified"], f"PHONETIC_MATCHを自動PASSにしてはいけない: {k}")
            self.assertEqual(detail["scg_result"], "NG", k)
            self.assertEqual(detail["scg_info"]["secondary_classification"], "PHONETIC_MATCH", k)
            self.assertFalse(detail["stop_retrying"], k)

    def test_g7_short_text_similarity_below_0_4_not_executed(self):
        detail, n = _run(G7_SHORT_EXCLUDED)
        self.assertEqual(n, 0, "類似度0.4未満の短文ではAzureを呼ばない")
        self.assertFalse(detail["verified"])
        self.assertFalse(detail["scg_applied"])
        self.assertEqual(detail["scg_result"], "NOT_APPLIED")
        self.assertIn("similarity_lt_0.4", detail["scg_info"]["exclusion_reason"])

    def test_every_row_matches_phase0_secondary_pass_judgement(self):
        """25行すべて: 実行されたものはPhase 0のsec_passと同じ判定。除外(g7)は不実行。"""
        executed = passed = 0
        for k, rec in FIX.items():
            detail, n = _run(k)
            if k == G7_SHORT_EXCLUDED:
                self.assertEqual(n, 0)
                continue
            if rec["existing_exclusions"]:
                self.assertEqual(n, 0, k)
                continue
            self.assertEqual(n, 1, k)
            executed += 1
            self.assertEqual(detail["verified"], bool(rec["sec_pass"]), k)
            passed += int(detail["verified"])
        self.assertEqual(executed, 24)
        self.assertEqual(passed, 14)  # META 3 + 救済7群8音声(META重複なし: g11/g8/g17/g20/g27/g31/g33x2) + g18 2 + g1 1(g7はprobeで不実行)

    def test_scg_evidence_fields_saved(self):
        detail, _ = _run("g35_japanese_title_a1")
        info = detail["scg_info"]
        for key in ("scg_applied", "scg_result", "secondary_transcript", "judgement_reason",
                    "secondary_classification", "service", "azure_region", "speech_sdk_version",
                    "language", "phrase_list", "audio_seconds", "est_cost_jpy", "wall_seconds",
                    "primary_text", "timestamp"):
            self.assertIn(key, info)
        self.assertIs(info["scg_applied"], True)
        self.assertIs(info["phrase_list"], False)
        self.assertEqual(info["secondary_transcript"], FIX["g35_japanese_title_a1"]["secondary_text"])
        self.assertEqual(info["primary_text"], FIX["g35_japanese_title_a1"]["primary_asr"])
        self.assertTrue(any(s["step"] == "scg_secondary" for s in detail["steps"]))
        # 既存キーは不変
        for key in ("verified", "stop_retrying", "classification", "cascade_invoked", "steps",
                    "final_status", "human_review_required", "canonical_text", "wav_path"):
            self.assertIn(key, detail)


if __name__ == "__main__":
    unittest.main()
