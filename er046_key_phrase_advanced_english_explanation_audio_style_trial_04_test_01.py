# ============================================================
# er046_key_phrase_advanced_english_explanation_audio_style_trial_04_test_01.py
# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04: 単体test
# (費用ゼロ、API呼び出しは行わない)。unittest.TestCase形式
# (run_project_regression.py はunittest.TestLoader().discover()を使う)。
# ============================================================
from __future__ import annotations

import json
import os
import unittest

import er046_key_phrase_advanced_english_explanation_audio_style_trial_04 as trial

SOURCE_DIR = "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz"
OUT_DIR = "er046_output/key_phrase_advanced_english_explanation_audio_style_trial_04/hormuz"
REUSED_PATH = os.path.join(OUT_DIR, "reused_audio_summary.json")
VARIANT_PATH = os.path.join(OUT_DIR, "variant_audio_summary.json")


class StyleConstantsTest(unittest.TestCase):
    """Before/Reference After/A/B/CのStyle文言がユーザー指示と逐語一致
    していること(速度の数値指定なし、"clear, precise"を含む)。"""

    def test_before_style_matches_prior_trial(self):
        self.assertEqual(trial.BEFORE_STYLE, "clear, precise, explanatory")

    def test_reference_after_style_matches_prior_trial(self):
        self.assertEqual(trial.REFERENCE_AFTER_STYLE, "clear, precise, unhurried")

    def test_variant_styles_have_three_entries(self):
        self.assertEqual(set(trial.VARIANT_STYLES.keys()), {"A", "B", "C"})

    def test_variant_styles_contain_clear_precise(self):
        for label, style in trial.VARIANT_STYLES.items():
            self.assertTrue(style.startswith("clear, precise"),
                             f"variant {label} does not start with 'clear, precise': {style!r}")

    def test_variant_styles_no_wpm_numeric_specification(self):
        import re
        for label, style in trial.VARIANT_STYLES.items():
            self.assertIsNone(re.search(r"\d", style),
                               f"variant {label} contains a digit (possible WPM spec): {style!r}")

    def test_variant_styles_values(self):
        self.assertEqual(trial.VARIANT_STYLES["A"], "clear, precise, at a slightly relaxed pace")
        self.assertEqual(trial.VARIANT_STYLES["B"],
                          "clear, precise, at a measured pace, without dragging")
        self.assertEqual(trial.VARIANT_STYLES["C"],
                          "clear, precise, carefully paced for understanding, without slowing down")


class VerbatimReuseTest(unittest.TestCase):
    """Phrase・英語解説文をTRIAL-03出力から逐語で読み込んでいることを
    検証する(再生成・再選定なし)。"""

    def test_source_rows_verbatim_from_trial03_after_summary(self):
        rows = trial.load_source_rows(SOURCE_DIR)
        self.assertEqual(len(rows), 5)
        with open(os.path.join(SOURCE_DIR, "after_audio_summary.json"), encoding="utf-8") as f:
            trial03_after = json.load(f)["generated_after_explanation_audio"]
        by_rank = {r["rank"]: r for r in trial03_after}
        for row in rows:
            self.assertEqual(row["phrase"], by_rank[row["rank"]]["phrase"])
            self.assertEqual(row["text"], by_rank[row["rank"]]["text"])

    def test_expected_five_phrases_unchanged(self):
        rows = trial.load_source_rows(SOURCE_DIR)
        phrases = {row["phrase"] for row in rows}
        self.assertEqual(phrases, {
            "give back", "sea blockade", "stand at center stage",
            "take a sharp turn", "recover the cost",
        })


class BeforeReuseGuardTest(unittest.TestCase):
    """Beforeのreuse判定(style_prefix_used一致)が正しく機械検証される
    ことを確認する(決定論、API不使用)。"""

    def test_verify_accepts_five_matching_before_entries(self):
        reused = {"reused": [
            {"rank": i, "label": "before_explanation_en",
             "style_prefix_used": "clear, precise, explanatory", "dst": f"x{i}.wav"}
            for i in range(1, 6)
        ]}
        result = trial.verify_before_reusable(reused)
        self.assertEqual(len(result), 5)

    def test_verify_rejects_mismatched_style(self):
        reused = {"reused": [
            {"rank": 1, "label": "before_explanation_en",
             "style_prefix_used": "clear, precise, neutral", "dst": "x1.wav"},
        ]}
        with self.assertRaises(SystemExit):
            trial.verify_before_reusable(reused)

    def test_verify_rejects_missing_entries(self):
        reused = {"reused": [
            {"rank": 1, "label": "before_explanation_en",
             "style_prefix_used": "clear, precise, explanatory", "dst": "x1.wav"},
        ]}
        with self.assertRaises(SystemExit):
            trial.verify_before_reusable(reused)


class ProductionIsolationTest(unittest.TestCase):
    """本Trial scriptが、Key Phrase選定・Production Master Audio Store
    のpathを直接参照していないことを検証する。"""

    def test_does_not_import_production_key_phrase_selection_modules(self):
        with open("er046_key_phrase_advanced_english_explanation_audio_style_trial_04.py",
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
        with open("er046_key_phrase_advanced_english_explanation_audio_style_trial_04.py",
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

    def test_fifteen_reused_files(self):
        self.assertEqual(len(self.reused), 15)

    def test_all_before_entries_have_before_style(self):
        before_entries = [r for r in self.reused if r["label"] == "before_explanation_en"]
        self.assertEqual(len(before_entries), 5)
        for entry in before_entries:
            self.assertEqual(entry["style_prefix_used"], "clear, precise, explanatory")

    def test_all_reference_after_entries_have_unhurried_style(self):
        after_entries = [r for r in self.reused if r["label"] == "reference_after_explanation_en"]
        self.assertEqual(len(after_entries), 5)
        for entry in after_entries:
            self.assertEqual(entry["style_prefix_used"], "clear, precise, unhurried")

    def test_reused_files_exist_on_disk(self):
        for entry in self.reused:
            self.assertTrue(os.path.exists(entry["dst"]), f"missing: {entry['dst']}")


@unittest.skipUnless(os.path.exists(VARIANT_PATH), "実行済みvariant_audio_summary.jsonが無いためskip")
class ExecutedVariantOutputTest(unittest.TestCase):
    """実際に実行したvariant_audio_summary.jsonに対する実測検証。"""

    @classmethod
    def setUpClass(cls):
        with open(VARIANT_PATH, encoding="utf-8") as f:
            cls.variant = json.load(f)["generated_variant_audio"]

    def test_fifteen_variant_items_all_ok(self):
        self.assertEqual(len(self.variant), 15)
        for item in self.variant:
            self.assertEqual(item["status"], "OK")

    def test_variant_style_used_matches_constant(self):
        for item in self.variant:
            label = item["variant_label"]
            self.assertEqual(item["style_prefix_used"], trial.VARIANT_STYLES[label])

    def test_variant_asr_verified_true(self):
        for item in self.variant:
            self.assertTrue(item.get("asr_verified"))

    def test_variant_files_exist_on_disk(self):
        for item in self.variant:
            rank = item["rank"]
            label = item["variant_label"]
            path = os.path.join(OUT_DIR, "audio", f"kp{rank}_variant_{label}_en.wav")
            self.assertTrue(os.path.exists(path), f"missing: {path}")


if __name__ == "__main__":
    unittest.main()
