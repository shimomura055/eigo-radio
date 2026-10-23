# -*- coding: utf-8 -*-
"""FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_02: 『二十年後』(O. Henry)のSTORY_REGISTRY登録値のtest。
登録はdata表への値追加のみ(ロジック・Prompt・閾値・Gate・flag・既存作品entryは無変更)。
(a)必須キーが既存2作品と一致 (b)権利Gate (c)seed.json/story.md/SOURCE_PROVENANCE整合 (d)Seed承認検査(validate_source_essentials)
(e)Voice割当が正式Voice表の決定的割当規則どおり (f)lint表 (g)既存2作品の値が不変 (h)pages/run/管理IDが既存作品に触れない。
API呼出0・ファイル書込0。"""
import hashlib
import json
import unittest

import er026_family_z_fiction_production_runner_01 as r
import er062_family_z_structure_01 as st
import er062_family_z_writer_01 as w
import er063_family_z_audio_01 as a63

KEY = "after_twenty_years"
SEED_DIR = "er026_seeds/after_twenty_years"
PROD_SEED_DIR = "er026_output/family_z_production_e2e_01/after_twenty_years/seed"


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class RegistryTest(unittest.TestCase):
    def test_registered_alongside_existing(self):
        self.assertEqual(set(r.STORY_REGISTRY), {"melos", "the_open_window", KEY})

    def test_required_keys_identical_to_existing(self):
        self.assertEqual(set(r.STORY_REGISTRY[KEY]), set(r.STORY_REGISTRY["the_open_window"]))
        self.assertEqual(set(r.STORY_REGISTRY[KEY]), set(r.STORY_REGISTRY["melos"]))

    def test_values(self):
        c = r.STORY_REGISTRY[KEY]
        self.assertEqual(c["story_type"], "literature")
        self.assertEqual(c["topic_title"], "After Twenty Years")
        self.assertEqual(c["japanese_title_text"], "二十年後(After Twenty Years)")
        self.assertEqual(c["japanese_title_tts"], "二十年後")
        self.assertEqual(c["trial_seed_dir"], SEED_DIR)
        self.assertEqual(c["e2e_pages_dir"], "user_test/family_z_after_twenty_years_01")
        self.assertEqual(c["e2e_management_id"], "FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01")
        self.assertIs(c["rights_block"], r.AFTER_TWENTY_YEARS_RIGHTS_BLOCK)
        self.assertIs(c["speaker_config"], st.STORY_SPEAKER_CONFIG[KEY])

    def test_cli_choice_derived_from_registry(self):
        a = r.build_parser().parse_args(["--story", KEY, "--run", "run_x"])
        self.assertEqual(a.story, KEY)


class RightsGateTest(unittest.TestCase):
    def test_gate_pass_and_fields(self):
        r.check_rights_gate(r.AFTER_TWENTY_YEARS_RIGHTS_BLOCK)
        b = r.AFTER_TWENTY_YEARS_RIGHTS_BLOCK
        for f in r.RIGHTS_REQUIRED_FIELDS:
            self.assertTrue(b.get(f), f)
        self.assertEqual(b["author_death_date"], "1910-06-05")
        self.assertEqual(b["confirmed_date"], "2026-10-23")
        for token in ("3,794", "1971-05-22", "遡及しない"):
            self.assertIn(token, b["jp_public_domain_basis"])
        self.assertTrue(b["source_url"].startswith("https://www.gutenberg.org/"))

    def test_gate_fails_closed_when_field_missing(self):
        bad = dict(r.AFTER_TWENTY_YEARS_RIGHTS_BLOCK)
        bad["source_url"] = ""
        with self.assertRaises(r.RightsGateError):
            r.check_rights_gate(bad)

    def test_legal_use_basis_is_same_user_decision_text(self):
        self.assertEqual(r.AFTER_TWENTY_YEARS_RIGHTS_BLOCK["legal_use_basis"], r.OPEN_WINDOW_RIGHTS_BLOCK["legal_use_basis"])


class SeedFilesTest(unittest.TestCase):
    def test_seed_schema_same_as_open_window(self):
        with open("er026_seeds/the_open_window/seed.json", encoding="utf-8") as f:
            o = json.load(f)
        with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
            s = json.load(f)
        self.assertEqual(list(o), list(s))
        self.assertEqual(set(o["rights_status"]), set(s["rights_status"]))
        self.assertEqual(s["rights_status"]["confirmed_date"], "2026-10-23")

    def test_load_trial_seed_and_story(self):
        loaded = r.load_trial_seed_and_story(KEY)
        title, body = r.strip_markdown_title(loaded["raw_trial_text"])
        self.assertEqual(title, "After Twenty Years")
        self.assertTrue(body.startswith("The policeman on the beat moved up the avenue impressively."))
        self.assertTrue(body.rstrip().endswith("to do the job. JIMMY."))

    def test_story_md_matches_source_provenance(self):
        with open(f"{SEED_DIR}/SOURCE_PROVENANCE.json", encoding="utf-8") as f:
            p = json.load(f)
        self.assertEqual(_sha(f"{SEED_DIR}/story.md"), p["story_md_sha256"])
        self.assertEqual(_sha(f"{SEED_DIR}/source_gutenberg_raw_extract.txt"), p["source_gutenberg_raw_extract_txt_sha256"])
        self.assertEqual(p["http_status"], 200)

    def test_raw_extract_and_story_md_have_same_words(self):
        with open(f"{SEED_DIR}/source_gutenberg_raw_extract.txt", encoding="utf-8") as f:
            raw = f.read().replace("_", "").split()
        loaded = r.load_trial_seed_and_story(KEY)
        _t, body = r.strip_markdown_title(loaded["raw_trial_text"])
        self.assertEqual(raw[3:], body.split())   # 先頭の見出し'AFTER TWENTY YEARS'(3語)を除き、語・順序とも原文のまま

    def test_production_seed_provenance_shas(self):
        with open(f"{PROD_SEED_DIR}/SEED_PROVENANCE.json", encoding="utf-8") as f:
            p = json.load(f)
        for name, meta in p["files"].items():
            self.assertEqual(_sha(f"{PROD_SEED_DIR}/{name}"), meta["sha256"], name)
        self.assertEqual(_sha(f"{PROD_SEED_DIR}/seed.json"), _sha(f"{SEED_DIR}/seed.json"))
        self.assertEqual(_sha(f"{PROD_SEED_DIR}/primary_text_excerpt.md"), _sha(f"{SEED_DIR}/story.md"))

    def test_source_essentials_pass_seed_approval_check(self):
        with open(f"{PROD_SEED_DIR}/seed.json", encoding="utf-8") as f:
            seed = json.load(f)
        res = w.validate_source_essentials(seed, KEY, PROD_SEED_DIR)
        self.assertTrue(res["present"])
        self.assertTrue(res["source_quote_checked_vs_last_paragraph"])
        self.assertEqual(res["keep_names"], ["Bob", "Jimmy"])
        self.assertLessEqual(res["items"], w.ESSENTIALS_MAX_ITEMS)

    def test_ending_not_spoiled_in_seed_first_scene_elements(self):
        with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
            s = json.load(f)
        self.assertIn("Before the note", s["source_essentials"]["ending_reveal"]["withhold_until_end"])


class VoiceAndSpeakerTest(unittest.TestCase):
    def test_voice_assignment_follows_deterministic_rule(self):
        names = st.STORY_SPEAKER_CONFIG[KEY]["dialogue_voice_tts_names"]
        self.assertEqual(names, {"narrator": "Aoede", "bob": "Algieba", "patrolman": "Schedar", "detective": "Fenrir"})
        self.assertEqual(r.STORY_REGISTRY[KEY]["voice_tts_names_plan"], names)
        asg = st.derive_voice_assignment(KEY)
        self.assertTrue(all(not row["pinned"] for row in asg["speakers"]))   # pin(個別例外)なし

    def test_speakers_resolve_and_unknown_fails_closed(self):
        self.assertEqual(a63.normalize_speaker("dialogue:jimmy", KEY), "patrolman")
        self.assertEqual(a63.resolve_dialogue_voice("patrolman", KEY), "Schedar")
        with self.assertRaises(Exception):
            a63.normalize_speaker("dialogue:other", KEY)

    def test_attr_schema_enum_is_story_roster(self):
        sch = w.build_attr_schema(KEY)
        enum = sch["schema"]["properties"]["attributions"]["items"]["properties"]["speaker"]["enum"]
        self.assertEqual(enum, ["bob", "patrolman", "detective", "other", "narrator"])

    def test_main_character_for_revise_prompt(self):
        self.assertIn("only Bob may have a personal name", w.build_revise_prompt("BODY", KEY))


class LintTest(unittest.TestCase):
    def test_lint_blocks_ending_spoiler_not_normal_support(self):
        ok = st.lint_support_text("A man waits in a dark doorway to keep a promise he made twenty years ago.", "en", KEY)
        self.assertEqual(ok, [])
        bad = st.lint_support_text("In the end Bob is arrested as a wanted man.", "en", KEY)
        self.assertTrue(any(x.startswith("SPOILER:") for x in bad))
        bad_ja = st.lint_support_text("二十年前の約束を守るため男は戸口で待つが、やがて逮捕される。", "ja", KEY)
        self.assertTrue(any(x.startswith("SPOILER:") for x in bad_ja))
        names = st.lint_support_text("Brady's restaurant used to stand here.", "en", KEY)
        self.assertTrue(names)


class ExistingStoriesUnchangedTest(unittest.TestCase):
    def test_existing_two_stories_values_unchanged(self):
        ow = r.STORY_REGISTRY["the_open_window"]
        self.assertEqual(ow["e2e_pages_dir"], "user_test/family_z_open_window_01")
        self.assertEqual(ow["voice_tts_names_plan"], {"narrator": "Aoede", "vera": "Zephyr", "framton": "Algieba",
                                                     "mrs_sappleton": "Kore", "men": "Schedar"})
        self.assertIs(ow["rights_block"], r.OPEN_WINDOW_RIGHTS_BLOCK)
        mel = r.STORY_REGISTRY["melos"]
        self.assertEqual(mel["voice_tts_names_plan"], {"narrator": "Aoede", "selinuntius": "Erinome", "dionysius": "Charon"})
        self.assertEqual(w.STORY_MAIN_CHARACTER["melos"], "Melos")
        self.assertEqual(w.STORY_MAIN_CHARACTER["the_open_window"], "Framton")
        self.assertEqual(st.STORY_LINT_CONFIG["the_open_window"]["forbidden_names"][0], "Sappleton")


class IsolationTest(unittest.TestCase):
    def test_context_paths_do_not_touch_other_stories(self):
        ctx = r.E2EContext(story_key=KEY, slug=KEY, run="run_sf_prod_01")
        self.assertEqual(ctx.pages_dir, "user_test/family_z_after_twenty_years_01")
        self.assertEqual(ctx.out_dir, "er026_output/family_z_production_e2e_01/after_twenty_years/run_sf_prod_01")
        self.assertEqual(ctx.seed_dir, "er026_output/family_z_production_e2e_01/after_twenty_years/seed")
        self.assertEqual(ctx.management_id, "FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01")
        for p in (ctx.pages_dir, ctx.out_dir, ctx.seed_dir):
            self.assertNotIn("melos", p.lower())
            self.assertNotIn("open_window", p.lower())


if __name__ == "__main__":
    unittest.main()
