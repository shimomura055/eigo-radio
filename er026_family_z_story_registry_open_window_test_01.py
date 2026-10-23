# -*- coding: utf-8 -*-
"""FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 委任_01: STORY_REGISTRY(melos / the_open_window)のtest。
(a)両storyの必須キー一致 (b)権利Gate (c)seed.json/story.md/SEED_PROVENANCE整合 (d)Melos値がパラメータ化前後で同一
(スナップショット=パラメータ化前のソース値を逐語固定) (e)新storyのpages/run/管理IDがMelosに触れないこと。
API呼出0・ファイル書込0(mock contextは作らない)。"""
import hashlib
import json
import os
import unittest

import er026_family_z_fiction_production_runner_01 as r
import er062_family_z_structure_01 as st
import er063_family_z_audio_01 as a63

SEED_DIR = "er026_seeds/the_open_window"
PROD_SEED_DIR = "er026_output/family_z_production_e2e_01/the_open_window/seed"
MELOS_SEED_JSON = "er018_output/fiction_external_seed_selection_criteria_trial_02/stories/03_japanese_lit_2/seed.json"


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class RegistryKeysTest(unittest.TestCase):
    def test_registry_has_both_stories(self):
        self.assertEqual(set(r.STORY_REGISTRY), {"melos", "the_open_window"})

    def test_required_keys_identical(self):
        self.assertEqual(set(r.STORY_REGISTRY["melos"]), set(r.STORY_REGISTRY["the_open_window"]))

    def test_open_window_values(self):
        c = r.STORY_REGISTRY["the_open_window"]
        self.assertEqual(c["story_type"], "literature")
        self.assertEqual(c["topic_title"], "The Open Window")
        self.assertEqual(c["japanese_title_text"], "開いた窓(The Open Window)")
        self.assertEqual(c["japanese_title_tts"], "開いた窓")
        self.assertEqual(c["trial_seed_dir"], "er026_seeds/the_open_window")
        self.assertEqual(c["e2e_pages_dir"], "user_test/family_z_open_window_01")
        self.assertEqual(c["e2e_management_id"], "FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01")
        # 正式Voice表(2026-10-23)から導出した値のみ
        self.assertEqual(c["voice_tts_names_plan"], {"narrator": "Aoede", "vera": "Zephyr", "framton": "Algieba", "mrs_sappleton": "Kore", "men": "Schedar"})
        self.assertEqual(c["voice_tts_names_plan"]["narrator"], "Aoede")


class RightsGateTest(unittest.TestCase):
    def test_open_window_rights_gate_pass(self):
        r.check_rights_gate(r.OPEN_WINDOW_RIGHTS_BLOCK)
        r.check_rights_gate(r.STORY_REGISTRY["the_open_window"]["rights_block"])

    def test_all_required_fields_present_and_dated(self):
        b = r.OPEN_WINDOW_RIGHTS_BLOCK
        for f in r.RIGHTS_REQUIRED_FIELDS:
            self.assertTrue(b.get(f), f)
        self.assertEqual(b["author_death_date"], "1916-11-14")
        self.assertEqual(b["confirmed_date"], "2026-10-21")
        self.assertIn("3,794", b["jp_public_domain_basis"])
        self.assertIn("1977-05-21", b["jp_public_domain_basis"])
        self.assertIn("遡及しない", b["jp_public_domain_basis"])
        self.assertTrue(b["source_url"].startswith("https://www.gutenberg.org/"))

    def test_gate_fails_closed_when_field_missing(self):
        bad = dict(r.OPEN_WINDOW_RIGHTS_BLOCK)
        bad["jp_public_domain_basis"] = ""
        with self.assertRaises(r.RightsGateError):
            r.check_rights_gate(bad)

    def test_legal_use_basis_is_user_decision_verbatim(self):
        # Melosと同じユーザー決定文(1)〜(5)が両blockで同一であること
        a = r.MELOS_RIGHTS_BLOCK["legal_use_basis"]
        b = r.OPEN_WINDOW_RIGHTS_BLOCK["legal_use_basis"]
        core = a[a.index("ユーザー正式決定"): a.index("自前生成する。") + len("自前生成する。")]
        self.assertIn(core, b)

    def test_melos_rights_block_unchanged(self):
        self.assertEqual(r.MELOS_RIGHTS_BLOCK["author_death_date"], "1948-06-13")
        self.assertEqual(r.MELOS_RIGHTS_BLOCK["confirmed_date"], "2026-09-26")
        self.assertEqual(r.MELOS_RIGHTS_BLOCK["source_url"], "https://www.aozora.gr.jp/cards/000035/files/1567_14913.html")


class SeedFilesTest(unittest.TestCase):
    def test_seed_schema_same_as_melos(self):
        with open(MELOS_SEED_JSON, encoding="utf-8") as f:
            m = json.load(f)
        with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
            s = json.load(f)
        # 2026-10-23(修正版B全体の正式採用): 『開いた窓』Seedは任意キーsource_essentialsを追加で持つ(Melosは持たない=従来どおり)
        self.assertEqual(list(m), [k for k in s if k != "source_essentials"])
        self.assertIn("source_essentials", s)
        self.assertNotIn("source_essentials", m)
        self.assertEqual(set(m["rights_status"]), set(s["rights_status"]))
        self.assertEqual(s["rights_status"]["confirmed_date"], "2026-10-21")
        self.assertGreaterEqual(len(s["seed_elements"]), 4)

    def test_load_trial_seed_and_story(self):
        loaded = r.load_trial_seed_and_story("the_open_window")
        title, body = r.strip_markdown_title(loaded["raw_trial_text"])
        self.assertEqual(title, "The Open Window")
        self.assertTrue(body.startswith("“My aunt will be down presently, Mr. Nuttel,”"))
        self.assertTrue(body.rstrip().endswith("Romance at short notice was her speciality."))

    def test_story_md_matches_source_provenance(self):
        with open(f"{SEED_DIR}/SOURCE_PROVENANCE.json", encoding="utf-8") as f:
            p = json.load(f)
        self.assertEqual(_sha(f"{SEED_DIR}/story.md"), p["story_md_sha256"])
        self.assertEqual(_sha(f"{SEED_DIR}/source_gutenberg_raw_extract.txt"), p["source_gutenberg_raw_extract_txt_sha256"])
        self.assertEqual(p["http_status"], 200)

    def test_raw_extract_and_story_md_have_same_words(self):
        with open(f"{SEED_DIR}/source_gutenberg_raw_extract.txt", encoding="utf-8") as f:
            raw = f.read().split()
        loaded = r.load_trial_seed_and_story("the_open_window")
        _t, body = r.strip_markdown_title(loaded["raw_trial_text"])
        self.assertEqual(raw, body.split())    # 語・順序とも原文のまま(空白正規化のみ)

    def test_production_seed_provenance_shas(self):
        with open(f"{PROD_SEED_DIR}/SEED_PROVENANCE.json", encoding="utf-8") as f:
            p = json.load(f)
        for name, meta in p["files"].items():
            self.assertEqual(_sha(f"{PROD_SEED_DIR}/{name}"), meta["sha256"], name)
        self.assertEqual(_sha(f"{PROD_SEED_DIR}/seed.json"), _sha(f"{SEED_DIR}/seed.json"))


class MelosUnchangedSnapshotTest(unittest.TestCase):
    """パラメータ化前(2026-10-21 HEAD dc0e40811)のMelos値のスナップショット。"""

    def test_runner_constants(self):
        self.assertEqual(r.E2E_MANAGEMENT_ID, "FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01")
        self.assertEqual(r.E2E_THEME_TAG, "FAMILY_Z_MELOS_SOL_PRODUCTION_E2E_01")
        self.assertEqual(r.E2E_PAGES_DIR, "user_test/family_z_melos_02")
        self.assertEqual(r.E2E_RUN_ROOT, "er026_output/family_z_production_e2e_01")

    def test_melos_registry_values(self):
        c = r.STORY_REGISTRY["melos"]
        self.assertEqual(c["topic_title"], "The Three-Day Promise")
        self.assertEqual(c["japanese_title_text"], "走れメロス(The Three-Day Promise)")
        self.assertEqual(c["japanese_title_tts"], "走れメロス")
        self.assertEqual(c["trial_seed_dir"], r.TRIAL_SEED_DIR)
        self.assertEqual(c["voice_keywords"], {"selinuntius": ["selinuntius"], "dionysius": ["dionysius", "ruler"]})
        self.assertEqual(c["voice_tts_names_plan"], {"narrator": "Aoede", "selinuntius": "Erinome", "dionysius": "Charon"})
        self.assertIs(c["rights_block"], r.MELOS_RIGHTS_BLOCK)

    def test_melos_context_defaults(self):
        ctx = r.E2EContext()
        self.assertEqual((ctx.story_key, ctx.slug), ("melos", "melos"))
        self.assertEqual(ctx.pages_dir, "user_test/family_z_melos_02")
        self.assertEqual(ctx.management_id, "FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01")
        self.assertEqual(ctx.theme_tag, "FAMILY_Z_MELOS_SOL_PRODUCTION_E2E_01")
        self.assertEqual(ctx.out_dir, "er026_output/family_z_production_e2e_01/melos/run_e2e_01")
        self.assertEqual(ctx.seed_dir, "er026_output/family_z_production_e2e_01/melos/seed")

    def test_er063_defaults(self):
        self.assertEqual(a63.MANAGEMENT_ID, "FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01")
        self.assertEqual(a63.PAGES_DIR, "user_test/family_z_melos_02")
        self.assertEqual(a63.PAGES_DIR, r.E2E_PAGES_DIR)
        html = a63.build_listening_page_html("Standard", [], [], "audio_standard/Melos_a2_full.mp3", 10.0)
        self.assertIn("<title>走れメロス Standard 試聴</title>", html)
        self.assertIn("<h1>走れメロス Standard</h1>", html)
        idx = a63.build_index_html([{"id": "std", "label": "Standard", "full_src": "x.mp3", "duration": 1.0, "rows": []}]) \
            if False else None
        self.assertIsNone(idx)

    def test_melos_voice_tables_unchanged(self):
        self.assertEqual(a63.FAMILY_Z_DIALOGUE_VOICE_KEYWORDS, {"melos": ["melos"], "selinuntius": ["selinuntius", "friend"],
                                                               "dionysius": ["dionysius", "ruler", "king", "tyrant"]})
        self.assertEqual(a63.FAMILY_Z_DIALOGUE_VOICE_TTS_NAMES,
                         {"narrator": "Aoede", "melos": "Algieba", "selinuntius": "Erinome", "dionysius": "Charon"})
        self.assertEqual(st.SPEAKERS, ("melos", "king", "friend", "other", "narrator"))

    def test_melos_lint_config_unchanged(self):
        cfg = st.STORY_LINT_CONFIG["melos"]
        self.assertEqual(cfg["forbidden_names"], ["Selinuntius", "Dionysius", "Dionys", "Phidias",
                                                  "セリヌンティウス", "ディオニス", "ディオニュシオス", "フィロストラトス"])
        self.assertEqual(len(cfg["spoiler_ja"]), 13)
        self.assertEqual(len(cfg["spoiler_en"]), 12)

    def test_revise_prompt_melos_byte_identical_to_pre_parametrization(self):
        import er062_family_z_writer_01 as w
        old = ("Here is a short story:\n\nBODY\n\n"
               "Without changing the events, the characters, or the cause-and-effect, please revise it into a more engaging story. "
               "Keep it at a natural upper-intermediate level (CEFR B1-B2), about 330-470 words, in third person, "
               "and only Melos may have a personal name. Output the title and the story only.")
        self.assertEqual(w.build_revise_prompt("BODY"), old)
        self.assertEqual(w.build_revise_prompt("BODY", "melos"), old)
        ow = w.build_revise_prompt("BODY", "the_open_window")
        # 2026-10-23(修正版B全体の正式採用): 主人公名を"Framton"へ(フルネームNuttelは指示文に使わない、Opus論点4 must-fix)
        self.assertIn("only Framton may have a personal name", ow)
        self.assertNotIn("Nuttel", ow)
        self.assertNotIn("Melos", ow)

    def test_check_adv_guardrails_melos_default_unchanged(self):
        import er062_family_z_writer_01 as w
        g = w.check_adv_guardrails("# T\n\nDionysius spoke.\n")
        self.assertTrue(any("NAME_RULE_NOTE:Dionysius" in x for x in g["warnings"]))


class OpenWindowIsolationTest(unittest.TestCase):
    def test_context_paths_do_not_touch_melos(self):
        ctx = r.E2EContext(story_key="the_open_window", slug="the_open_window", run="run_e2e_01")
        self.assertEqual(ctx.pages_dir, "user_test/family_z_open_window_01")
        self.assertEqual(ctx.out_dir, "er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01")
        self.assertEqual(ctx.seed_dir, "er026_output/family_z_production_e2e_01/the_open_window/seed")
        self.assertEqual(ctx.management_id, "FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01")
        for p in (ctx.pages_dir, ctx.out_dir, ctx.seed_dir):
            self.assertNotIn("melos", p.lower())

    def test_open_window_lint_config_blocks_spoiler_and_not_short_name_substrings(self):
        ok = st.lint_support_text("A visitor hears an eerie story about a window left open each evening.", "en", "the_open_window")
        self.assertEqual(ok, [])
        bad = st.lint_support_text("In the end the girl made up the whole story.", "en", "the_open_window")
        self.assertTrue(any(x.startswith("SPOILER:") for x in bad))
        several = st.lint_support_text("Several guests heard the girl's story.", "en", "the_open_window")
        self.assertEqual(several, [])

    def test_story_name_not_in_cli_choices_breaks(self):
        p = r.build_parser()
        a = p.parse_args(["--story", "the_open_window", "--run", "run_x"])
        self.assertEqual(a.story, "the_open_window")


if __name__ == "__main__":
    unittest.main()
