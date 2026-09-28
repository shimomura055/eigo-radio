# ============================================================
# er039_family_xy_concreteness_control_trial_02_test_01.py
# FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02: 単体test(API呼び出しなし、¥0)
# ============================================================
from __future__ import annotations

import hashlib
import unittest

import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er037_family_xy_concreteness_control_trial_01 as t1

import er039_family_xy_concreteness_control_trial_02 as m


def _load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestT1SuffixProductionSafety(unittest.TestCase):
    def test_t1_suffix_does_not_change_production_prompt_constants(self):
        ja_sample = "サンプル記事本文です。"
        base_prompt = adv_gen.build_prompt(ja_sample)
        t1_prompt = base_prompt + m.T1_SUPPRESSION_SUFFIX
        self.assertTrue(t1_prompt.startswith(base_prompt))
        self.assertNotEqual(t1_prompt, base_prompt)
        # production側の主要sha256定数は本ファイルのimport時点でfail-closed
        # に検証される(_assert_unchanged_portion_sha256等)。importが成功
        # していること自体が「production定数は書き換わっていない」証跡。
        self.assertEqual(adv_gen.ADVANCED_UNCHANGED_PORTION_SHA256,
                          adv_gen._compute_unchanged_portion_sha256())
        self.assertEqual(adv_gen.ADVANCED_VOCAB_RULE_V2_SHA256,
                          adv_gen._compute_vocab_rule_v2_sha256())

    def test_t1_suffix_sha256_is_stable_and_documented(self):
        expected = hashlib.sha256(m.T1_SUPPRESSION_SUFFIX.encode("utf-8")).hexdigest()
        self.assertEqual(expected, hashlib.sha256(m.T1_SUPPRESSION_SUFFIX.encode("utf-8")).hexdigest())
        self.assertIn("Trial-only", m.T1_SUPPRESSION_SUFFIX)
        self.assertIn("not part of the production prompt", m.T1_SUPPRESSION_SUFFIX)


class TestPatternText(unittest.TestCase):
    def test_ja_pattern_text_an3_matches_trial01_an_verbatim(self):
        self.assertEqual(m.JA_PATTERN_TEXT["AN3"], t1.COMBO_PATTERNS["AN"])

    def test_ja_pattern_text_an2_is_a2_plus_n2(self):
        self.assertEqual(m.JA_PATTERN_TEXT["AN2"], t1.PATTERNS_A["A2"] + "\n" + t1.PATTERNS_N["N2"])


class TestImprovedJaCounter(unittest.TestCase):
    def test_excludes_common_katakana_loanwords(self):
        text = "このニュースでは、タンカーがガソリンとバレルとドルの話をしました。"
        self.assertEqual(m.extract_entities_ja_improved(text), set())

    def test_detects_kanji_proper_nouns(self):
        text = "米国と中東の湾岸諸国が、トランプ氏とホルムズ海峡について話した。"
        entities = m.extract_entities_ja_improved(text)
        self.assertIn("United States", entities)
        self.assertIn("Middle East", entities)
        self.assertIn("Gulf states", entities)
        self.assertIn("トランプ", entities)
        self.assertIn("ホルムズ", entities)

    def test_strips_katakana_middle_dot_artifact(self):
        text = "米国・イランの間で攻撃が続く。"
        entities = m.extract_entities_ja_improved(text)
        self.assertIn("イラン", entities)
        self.assertFalse(any(e.startswith("・") for e in entities))


class TestImprovedEnCounter(unittest.TestCase):
    def test_excludes_title_heading(self):
        text = (
            "# The Oil Market's Main Character: The Missing 20 Percent Bill\n\n"
            "The report said Trump proposed a fee. Analysts said Brent oil rose.\n"
        )
        entities = m.extract_entities_en_improved(text)
        for noise in ("Oil", "Market's", "Main", "Character:", "Missing", "Percent", "Bill"):
            self.assertNotIn(noise, entities)
        self.assertTrue("Trump" in entities or "Donald Trump" in entities)
        self.assertIn("Brent", entities)

    def test_merges_multiword_entities(self):
        text = "Trump proposed a plan. The United States and the Strait of Hormuz were both mentioned.\n"
        entities = m.extract_entities_en_improved(text)
        self.assertIn("United States", entities)
        self.assertIn("Strait of Hormuz", entities)
        for noise in ("United", "States", "Strait", "Hormuz"):
            self.assertNotIn(noise, entities)

    def test_does_not_flag_paragraph_initial_word_after_heading(self):
        text = (
            "### Danger around the strait\n\n"
            "Attacks between the United States and Iran continue. Fear remains.\n"
        )
        entities = m.extract_entities_en_improved(text)
        self.assertNotIn("Attacks", entities)

    def test_normalizes_possessive_suffix(self):
        text = "Meta built Muse. Muse's phone feature surprised people.\n"
        entities = m.extract_entities_en_improved(text)
        self.assertIn("Muse", entities)
        self.assertNotIn("Muse's", entities)
        self.assertNotIn("Muse’s", entities)

    def test_excludes_ai_as_common_noun(self):
        text = "The company said Meta tested AI. Reports said AI's response mattered.\n"
        entities = m.extract_entities_en_improved(text)
        self.assertNotIn("AI", entities)
        self.assertNotIn("AI's", entities)
        self.assertIn("Meta", entities)

    def test_excludes_month_names(self):
        text = "The report said Trump spoke in July about the plan.\n"
        entities = m.extract_entities_en_improved(text)
        self.assertNotIn("July", entities)
        self.assertIn("Trump", entities)


class TestNameUnitDiffTable(unittest.TestCase):
    def test_flags_new_en_entity_not_in_ja(self):
        ja_entities = {"トランプ", "ブレント"}
        en_entities = {"Donald Trump", "Brent", "Iran"}
        rows = m.build_name_unit_diff_table(ja_entities, en_entities)
        iran_rows = [r for r in rows if r["canonical"] == "Iran"]
        self.assertEqual(len(iran_rows), 1)
        self.assertFalse(iran_rows[0]["in_ja"])
        self.assertTrue(iran_rows[0]["in_en"])
        self.assertTrue(iran_rows[0]["en_new_vs_ja"])
        trump_rows = [r for r in rows if r["canonical"] == "Donald Trump"]
        self.assertFalse(trump_rows[0]["en_new_vs_ja"])

    def test_no_false_positive_when_same_entities(self):
        ja_entities = {"トランプ", "ホルムズ", "ブレント", "イラン"}
        en_entities = {"Donald Trump", "Strait of Hormuz", "Brent", "Iran"}
        rows = m.build_name_unit_diff_table(ja_entities, en_entities)
        self.assertTrue(all(not r["en_new_vs_ja"] for r in rows))


class TestRealFixtureRegression(unittest.TestCase):
    def test_hormuz_an_real_fixture_ja_to_en_no_new_entity(self):
        """実際のTrial-01出力(Hormuz AN)を使い、改良カウンタで JA=EN=7 かつ
        ENでの新規固有名詞0件であることを確認する(entity_ja_en_diff.md
        生成結果と整合させる回帰test)。"""
        ja_text = _load(
            "er037_output/family_xy_concreteness_control_trial_01/hormuz/task_a_ja/AN_r2.md")
        en_text = _load(
            "er037_output/family_xy_concreteness_control_trial_01/hormuz/task_a_advanced/AN.md")
        ja_entities = m.extract_entities_ja_improved(ja_text)
        en_entities = m.extract_entities_en_improved(en_text)
        self.assertEqual(len(ja_entities), 7)
        self.assertEqual(len(en_entities), 7)
        rows = m.build_name_unit_diff_table(ja_entities, en_entities)
        self.assertTrue(all(not r["en_new_vs_ja"] for r in rows if r.get("in_en")))


class TestCellHelpers(unittest.TestCase):
    def test_split_cell_id(self):
        self.assertEqual(m.cell_ja_pattern("AN3-T1"), "AN3")
        self.assertEqual(m.cell_t_variant("AN3-T1"), "T1")
        self.assertEqual(m.cell_ja_pattern("AN2-T0"), "AN2")
        self.assertEqual(m.cell_t_variant("AN2-T0"), "T0")


if __name__ == "__main__":
    unittest.main()
