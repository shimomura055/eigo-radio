# -*- coding: utf-8 -*-
"""FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 委任_02 test(API呼出なし)。実行: python er054_family_z_story_pool_trial_02_test_01.py"""
import builtins
import json
import os
import subprocess
import sys
import unittest

import er006_model_routing_contract_01 as routing
import er054_family_z_story_pool_trial_common_01 as common
import er054_family_z_story_pool_quality_eval_trial_01 as qe
import er054_family_z_story_pool_rights_interpret_trial_01 as ri

# 委任_02時点のProduction key(Trial key追加前から存在した値)。変更されていないことを固定。
PRODUCTION_KEYS_EXPECTED = {
    "QUERY_PLANNING": "gpt-6-luna", "TOPIC_SELECTION": "gpt-6-luna", "EVIDENCE_PACK": "gpt-6-luna", "VFL": "gpt-6-luna",
    "VERIFICATION": "gpt-6-luna", "B1_WRITER": "gpt-6-luna", "A2_WRITER": "gpt-6-luna", "WRITER_FACT_CHECK": "gpt-6-luna",
    "B1_SUPPORT": "gpt-6-luna", "A2_SUPPORT": "gpt-6-luna", "SUPPORT_FACT_CHECK": "gpt-6-luna",
    "PROPER_NOUN_EXTRACTION": "gpt-6-luna", "SHARED_POINT_BLUEPRINT": "gpt-6-luna", "STANDARD_A2_ADAPTATION": "gpt-6-luna",
    "NATURAL_ENGLISH_ADAPTATION": "gpt-6-luna", "FAMILY_X_FLASH_LITE_TTS": "gemini-3.8-flash-lite-tts",
    "KEY_PHRASE_ADVANCED_EXPLANATION": "gpt-6-luna", "FAMILY_X_STORYLINE_B3": "gpt-6.1-sol", "FAMILY_X_RF_LUNA": "gpt-6-luna",
    "FAMILY_X_RF_GEMINI": "gemini-3.5-flash-lite", "FAMILY_X_FACTLOCK_R0": "gpt-6.1-sol", "FAMILY_X_FACTLOCK_REVISE": "gpt-6.1-sol",
}
HERE = os.path.dirname(os.path.abspath(__file__))


# 委任_02より後に、別の承認済み委任で追加されたProduction key(追加のみ。既存keyの値は不変=上のEXPECTEDで固定)。閉集合の更新として列挙:
#  - FAMILY_Z_*: FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_03(2026-10-12、routing contract内コメント参照)。C-1時点から既知FAILだった。
#  - FAMILY_X_B3_CORE_NUMBER_ROUNDING: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_06 C-2(2026-10-22、gpt-6-luna固定。値は下で固定)
LATER_APPROVED_PRODUCTION_KEYS = {
    "FAMILY_Z_WRITER_ADV_R0", "FAMILY_Z_WRITER_ADV_R1", "FAMILY_Z_WRITER_ADV_R2", "FAMILY_Z_STD_ADJUST", "FAMILY_Z_SEMANTIC_JUDGE",
    "FAMILY_Z_STORY_SPLIT", "FAMILY_Z_DIALOGUE_ATTRIBUTION", "FAMILY_X_B3_CORE_NUMBER_ROUNDING",
    "KEY_PHRASE_GENERAL_EXPLANATION",   # FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_14(2026-10-25、Part 1案α、SUPPORT_MODEL=gpt-6-luna)
    "KEY_PHRASE_SOURCE_SENTENCE_JA",   # FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_16(2026-10-25、Part 1 T1 訳工程、SUPPORT_MODEL=gpt-6-luna)
    "STUDY_TEXT_GRAMMAR_EXTRACT", "STUDY_TEXT_GRAMMAR_EXPLAIN",   # PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03(2026-10-25、Part 2、SUPPORT_MODEL=gpt-6-luna)
}


class T(unittest.TestCase):
    def test_trial_keys_are_luna(self):
        for k in common.TRIAL_KEYS:
            self.assertEqual(routing.PROCESS_MODEL_MAP[k], "gpt-6-luna")
        self.assertEqual(qe.PRIMARY_MODEL, "gpt-6-luna")
        self.assertEqual(ri.PRIMARY_MODEL, "gpt-6-luna")
        self.assertEqual(qe.ALLOWED_MODELS, ("gpt-6-luna",))
        self.assertEqual(ri.ALLOWED_MODELS, ("gpt-6-luna",))

    def test_production_keys_unchanged(self):
        for k, v in PRODUCTION_KEYS_EXPECTED.items():
            self.assertEqual(routing.PROCESS_MODEL_MAP[k], v, k)
        extra = set(routing.PROCESS_MODEL_MAP) - set(PRODUCTION_KEYS_EXPECTED) - set(common.TRIAL_KEYS) - LATER_APPROVED_PRODUCTION_KEYS
        self.assertFalse(extra, f"想定外のkey追加: {extra}")

    def test_core_number_rounding_key_is_luna_literal(self):
        self.assertEqual(routing.PROCESS_MODEL_MAP["FAMILY_X_B3_CORE_NUMBER_ROUNDING"], "gpt-6-luna")

    def test_non_trial_key_rejected(self):
        with self.assertRaises(routing.ModelContractViolation):
            common.resolve_trial_model("B1_WRITER")

    def test_disallowed_models_rejected(self):
        for m in ("gpt-6-astra", "gpt-6.1-sol", "gpt-5.6-luna", "", None):
            with self.assertRaises(routing.ModelContractViolation):
                common.check_model(common.KEY_QUALITY, m)
            with self.assertRaises(routing.ModelContractViolation):
                qe.eval_one("L01", m, qe.MockClient(), "unused", "t", mock=True)
            with self.assertRaises(routing.ModelContractViolation):
                ri.interpret_one("L01", m, ri.MockClient(), "unused", True)

    def test_sealed_guard(self):
        with self.assertRaises(common.SealedFileAccessError):
            common.assert_not_sealed(os.path.join(qe.BASE, "SEALED_PAST_RESULTS_L01_L06.json"))
        with self.assertRaises(common.SealedFileAccessError):
            common.assert_not_sealed("x/sealed_past_results_l01_l06.JSON")

    def test_drivers_never_open_sealed_file(self):
        opened = []
        real_open = builtins.open

        def spy(file, *a, **k):
            opened.append(str(file))
            return real_open(file, *a, **k)
        import tempfile
        builtins.open = spy
        try:
            with tempfile.TemporaryDirectory() as d:
                for w in qe.WORKS if hasattr(qe, "WORKS") else [f"L{i:02d}" for i in range(1, 11)]:
                    if qe.load_screening(w)["decision"] == "PASS":
                        qe.eval_one(w, "gpt-6-luna", qe.MockClient(), d, "t", mock=True)
                    ri.interpret_one(w, "gpt-6-luna", ri.MockClient(), d, True)
        finally:
            builtins.open = real_open
        self.assertTrue(opened)
        self.assertFalse([p for p in opened if "SEALED" in p.upper()])

    def test_source_does_not_read_sealed(self):
        for fn in ("er054_family_z_story_pool_quality_eval_trial_01.py", "er054_family_z_story_pool_rights_interpret_trial_01.py"):
            src = open(os.path.join(HERE, fn), encoding="utf-8").read()
            self.assertNotIn("SEALED_PAST_RESULTS_L01_L06.json", src.replace("(SEALED_PAST_RESULTS_L01_L06.json)", ""))

    def test_actual_model_id_recorded(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            r = ri.interpret_one("L01", "gpt-6-luna", ri.MockClient(), d, True)
            self.assertEqual(r["actual_model_id"], "gpt-6-luna")
            self.assertEqual(r["routing_key"], common.KEY_RIGHTS)
            q = qe.eval_one("L01", "gpt-6-luna", qe.MockClient(), d, "t", mock=True)
            self.assertEqual(q["actual_model_id"], "gpt-6-luna")
            self.assertEqual(q["routing_key"], common.KEY_QUALITY)

    def test_no_override_upgrade(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            # 委任_03: L04は原語原作ベースでPASSになったため、REVIEW_REQUIRED据え置きの検証は合成screeningで行う(L06=NGは実データ)
            orig = ri.load_screening
            def fake(wid):
                x = orig(wid)
                if wid == "L04":
                    x["decision"] = "REVIEW_REQUIRED"
                return x
            ri.load_screening = fake
            try:
                for mode in ("neutral", "upgrade", "concern"):
                    for w in ("L04", "L06"):
                        r = ri.interpret_one(w, "gpt-6-luna", ri.MockClient(mode), d, True)
                        self.assertEqual(r["reconcile"]["final_status_after_interpret"], r["reconcile"]["deterministic_decision"])
                        self.assertFalse(r["reconcile"]["final_pass_confirmed"])
            finally:
                ri.load_screening = orig
            r = ri.interpret_one("L01", "gpt-6-luna", ri.MockClient("concern"), d, True)
            self.assertEqual(r["reconcile"]["final_status_after_interpret"], "REVIEW_REQUIRED")
            self.assertTrue(r["reconcile"]["demoted"])
            r = ri.interpret_one("L01", "gpt-6-luna", ri.MockClient("neutral"), d, True)
            self.assertEqual(r["reconcile"]["final_status_after_interpret"], "PASS")
            self.assertFalse(r["reconcile"]["final_pass_confirmed"])

    def test_unfetched_source_never_auto_pass(self):
        scr = ri.load_screening("L01")
        scr["primary_source"]["fetch_ok"] = False
        out = ri.reconcile(scr, {"llm_concern_level": "none", "pass_equivalent": True})
        self.assertEqual(out["final_status_after_interpret"], "REVIEW_REQUIRED")
        scr = ri.load_screening("L01")
        scr["unconfirmed"] = [{"item": "x", "blocking": True}]
        out = ri.reconcile(scr, {"llm_concern_level": "none", "pass_equivalent": True})
        self.assertEqual(out["final_status_after_interpret"], "REVIEW_REQUIRED")

    def test_real_refused_without_budget(self):
        for fn in ("er054_family_z_story_pool_quality_eval_trial_01.py", "er054_family_z_story_pool_rights_interpret_trial_01.py"):
            p = subprocess.run([sys.executable, os.path.join(HERE, fn), "--mode", "real"], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", cwd=HERE)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("STOP", p.stderr + p.stdout)
            p = subprocess.run([sys.executable, os.path.join(HERE, fn), "--mode", "dry-run", "--models", "gpt-6-astra"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=HERE)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("許可モデル外", p.stderr + p.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
