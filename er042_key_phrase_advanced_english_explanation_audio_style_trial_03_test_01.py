# ============================================================
# er042_key_phrase_advanced_english_explanation_audio_style_trial_03_test_01.py
# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03: 単体test
# (費用ゼロ、API呼び出しは行わない)。unittest.TestCase形式
# (run_project_regression.py はunittest.TestLoader().discover()を使う)。
# ============================================================
from __future__ import annotations

import json
import os
import unittest

import er041_key_phrase_advanced_english_explanation_trial_02 as prior_trial
import er042_key_phrase_advanced_english_explanation_audio_style_trial_03 as trial

SOURCE_DIR = "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz"
OUT_DIR = "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz"
REUSED_PATH = os.path.join(OUT_DIR, "reused_audio_summary.json")
AFTER_PATH = os.path.join(OUT_DIR, "after_audio_summary.json")


class StyleConstantsTest(unittest.TestCase):
    """Before/AfterのStyle文言がユーザー指示と逐語一致していること。"""

    def test_before_style_matches_user_instruction(self):
        self.assertEqual(trial.BEFORE_STYLE, "clear, precise, explanatory")

    def test_after_style_matches_user_instruction(self):
        self.assertEqual(trial.AFTER_STYLE, "clear, precise, unhurried")


class VerbatimReuseTest(unittest.TestCase):
    """Phrase・英語解説文をer041(TRIAL-02のB候補)から逐語で読み込んで
    いることを検証する(再生成・再選定なし)。"""

    def test_source_rows_verbatim_from_er041_summary(self):
        rows = trial.load_source_rows(SOURCE_DIR)
        self.assertEqual(len(rows), 5)
        with open(os.path.join(SOURCE_DIR, "summary.json"), encoding="utf-8") as f:
            er041_summary = json.load(f)
        er041_by_rank = {r["rank"]: r for r in er041_summary["items"]}
        for row in rows:
            self.assertEqual(row["phrase"], er041_by_rank[row["rank"]]["phrase"])
            self.assertEqual(row["candidate_b_english_explanation"],
                              er041_by_rank[row["rank"]]["candidate_b_english_explanation"])

    def test_expected_five_phrases_unchanged(self):
        rows = trial.load_source_rows(SOURCE_DIR)
        phrases = {row["phrase"] for row in rows}
        self.assertEqual(phrases, {
            "give back", "sea blockade", "stand at center stage",
            "take a sharp turn", "recover the cost",
        })


class BeforeReuseGuardTest(unittest.TestCase):
    """Beforeのreuse判定(style_prefix_used一致・augmentation無し)が
    正しく機械検証されることを確認する(決定論、API不使用)。"""

    def test_verify_accepts_matching_style_no_augmentation(self):
        audio_summary = {
            "generated_new_explanation_audio": [
                {"rank": 1, "status": "OK", "style_prefix_used": "clear, precise, explanatory",
                 "en_pronunciation_resolver_info": {"hints_applied": False}},
            ]
        }
        result = trial.verify_before_style_reusable(audio_summary)
        self.assertIn(1, result)

    def test_verify_rejects_mismatched_style(self):
        audio_summary = {
            "generated_new_explanation_audio": [
                {"rank": 1, "status": "OK", "style_prefix_used": "clear, precise, neutral",
                 "en_pronunciation_resolver_info": {"hints_applied": False}},
            ]
        }
        with self.assertRaises(SystemExit):
            trial.verify_before_style_reusable(audio_summary)

    def test_verify_rejects_augmented_style(self):
        audio_summary = {
            "generated_new_explanation_audio": [
                {"rank": 1, "status": "OK", "style_prefix_used": "clear, precise, explanatory",
                 "en_pronunciation_resolver_info": {"hints_applied": True}},
            ]
        }
        with self.assertRaises(SystemExit):
            trial.verify_before_style_reusable(audio_summary)


class ProductionIsolationTest(unittest.TestCase):
    """本Trial scriptが、Key Phrase選定・Production Master Audio Store
    のpathを直接参照していないことを検証する。"""

    def test_does_not_import_production_key_phrase_selection_modules(self):
        with open("er042_key_phrase_advanced_english_explanation_audio_style_trial_03.py",
                  encoding="utf-8") as f:
            lines = f.readlines()
        forbidden = [
            "er003_v1_n3_01_scaffold_generate",
            "er003_b1_p2_keywords",
            "er003_key_words_canonicalization",
            "er003_key_words_production",
        ]
        import_lines = [ln for ln in lines
                         if (ln.strip().startswith("import ") or ln.strip().startswith("from "))]
        for name in forbidden:
            for ln in import_lines:
                self.assertNotIn(name, ln,
                                  f"Production Key Phrase選定モジュール({name})をimport文で参照しています: {ln!r}")

    def test_does_not_reference_production_master_store_path(self):
        with open("er042_key_phrase_advanced_english_explanation_audio_style_trial_03.py",
                  encoding="utf-8") as f:
            lines = f.readlines()
        code_lines = [ln for ln in lines if not ln.strip().startswith("#")]
        hits = [ln for ln in code_lines if "er006_output/master_audio_store_01" in ln]
        self.assertEqual(hits, [], f"Production Master Store pathがコード中に出現しています: {hits}")


@unittest.skipUnless(os.path.exists(REUSED_PATH), "実行済みreused_audio_summary.jsonが無いためskip")
class ExecutedReuseOutputTest(unittest.TestCase):
    """実際に実行したreused_audio_summary.jsonに対する実測検証。"""

    @classmethod
    def setUpClass(cls):
        with open(REUSED_PATH, encoding="utf-8") as f:
            cls.reused = json.load(f)["reused"]

    def test_ten_reused_files(self):
        self.assertEqual(len(self.reused), 10)

    def test_all_before_entries_have_before_style(self):
        before_entries = [r for r in self.reused if r["label"] == "before_explanation_en"]
        self.assertEqual(len(before_entries), 5)
        for entry in before_entries:
            self.assertEqual(entry["style_prefix_used"], "clear, precise, explanatory")

    def test_reused_files_exist_on_disk(self):
        for entry in self.reused:
            self.assertTrue(os.path.exists(entry["dst"]), f"missing: {entry['dst']}")


@unittest.skipUnless(os.path.exists(AFTER_PATH), "実行済みafter_audio_summary.jsonが無いためskip")
class ExecutedAfterOutputTest(unittest.TestCase):
    """実際に実行したafter_audio_summary.jsonに対する実測検証。"""

    @classmethod
    def setUpClass(cls):
        with open(AFTER_PATH, encoding="utf-8") as f:
            cls.after = json.load(f)["generated_after_explanation_audio"]

    def test_five_after_items_all_ok(self):
        self.assertEqual(len(self.after), 5)
        for item in self.after:
            self.assertEqual(item["status"], "OK")

    def test_after_style_used_matches_constant(self):
        for item in self.after:
            self.assertEqual(item["style_prefix_used"], trial.AFTER_STYLE)

    def test_after_asr_verified_true(self):
        for item in self.after:
            self.assertTrue(item.get("asr_verified"))

    def test_after_files_exist_on_disk(self):
        for item in self.after:
            rank = item["rank"]
            path = os.path.join(OUT_DIR, "audio", f"kp{rank}_after_en.wav")
            self.assertTrue(os.path.exists(path), f"missing: {path}")


if __name__ == "__main__":
    unittest.main()
