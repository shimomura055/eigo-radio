# -*- coding: utf-8 -*-
"""FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01 委任_01: 『賢者の贈り物』(O. Henry)のSTORY_REGISTRY登録値のtest。
登録はdata表への値追加のみ(ロジック・Prompt・閾値・Gate・flag・既存作品entryは無変更)。
(a)必須キーが既存作品と一致 (b)権利Gate (c)seed.json/story.md/SOURCE_PROVENANCE整合 (d)Seed承認検査(validate_source_essentials)
(e)Voice割当が正式Voice表の決定的割当規則どおり (f)lint表 (g)既存3作品の値が不変 (h)pages/run/管理IDが既存作品に触れない。
API呼出0・ファイル書込0。"""
import hashlib
import json
import unittest

import er026_family_z_fiction_production_runner_01 as r
import er062_family_z_structure_01 as st
import er062_family_z_writer_01 as w
import er063_family_z_audio_01 as a63

KEY = "the_gift_of_the_magi"
SEED_DIR = "er026_seeds/the_gift_of_the_magi"
PROD_SEED_DIR = "er026_output/family_z_production_e2e_01/the_gift_of_the_magi/seed"


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class RegistryTest(unittest.TestCase):
    def test_registered_alongside_existing(self):
        self.assertLessEqual({"melos", "the_open_window", "after_twenty_years", KEY}, set(r.STORY_REGISTRY))

    def test_required_keys_identical_to_existing(self):
        for other in ("the_open_window", "melos", "after_twenty_years"):
            self.assertEqual(set(r.STORY_REGISTRY[KEY]), set(r.STORY_REGISTRY[other]))

    def test_values(self):
        c = r.STORY_REGISTRY[KEY]
        self.assertEqual(c["story_type"], "literature")
        self.assertEqual(c["topic_title"], "The Gift of the Magi")
        self.assertEqual(c["japanese_title_text"], "賢者の贈り物(The Gift of the Magi)")
        self.assertEqual(c["japanese_title_tts"], "賢者の贈り物")
        self.assertEqual(c["trial_seed_dir"], SEED_DIR)
        self.assertEqual(c["e2e_pages_dir"], "user_test/family_z_gift_of_the_magi_01")
        self.assertEqual(c["e2e_management_id"], "FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01")
        self.assertIs(c["rights_block"], r.GIFT_OF_THE_MAGI_RIGHTS_BLOCK)
        self.assertIs(c["speaker_config"], st.STORY_SPEAKER_CONFIG[KEY])

    def test_cli_choice_derived_from_registry(self):
        a = r.build_parser().parse_args(["--story", KEY, "--run", "run_x"])
        self.assertEqual(a.story, KEY)


class RightsGateTest(unittest.TestCase):
    def test_gate_pass_and_fields(self):
        r.check_rights_gate(r.GIFT_OF_THE_MAGI_RIGHTS_BLOCK)
        b = r.GIFT_OF_THE_MAGI_RIGHTS_BLOCK
        for f in r.RIGHTS_REQUIRED_FIELDS:
            self.assertTrue(b.get(f), f)
        self.assertEqual(b["author_death_date"], "1910-06-05")
        self.assertEqual(b["confirmed_date"], "2026-10-24")
        for token in ("3,794", "1971-05-22", "遡及しない", "1905-12-10"):
            self.assertIn(token, b["jp_public_domain_basis"])
        self.assertTrue(b["source_url"].startswith("https://www.gutenberg.org/"))

    def test_gate_fails_closed_when_field_missing(self):
        bad = dict(r.GIFT_OF_THE_MAGI_RIGHTS_BLOCK)
        bad["source_url"] = ""
        with self.assertRaises(r.RightsGateError):
            r.check_rights_gate(bad)

    def test_legal_use_basis_is_same_user_decision_text(self):
        self.assertEqual(r.GIFT_OF_THE_MAGI_RIGHTS_BLOCK["legal_use_basis"], r.OPEN_WINDOW_RIGHTS_BLOCK["legal_use_basis"])


class SeedFilesTest(unittest.TestCase):
    def test_seed_schema_same_as_open_window(self):
        with open("er026_seeds/the_open_window/seed.json", encoding="utf-8") as f:
            o = json.load(f)
        with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
            s = json.load(f)
        self.assertEqual(list(o), list(s))
        self.assertEqual(set(o["rights_status"]), set(s["rights_status"]))
        self.assertEqual(s["rights_status"]["confirmed_date"], "2026-10-24")

    def test_load_trial_seed_and_story(self):
        loaded = r.load_trial_seed_and_story(KEY)
        title, body = r.strip_markdown_title(loaded["raw_trial_text"])
        self.assertEqual(title, "The Gift of the Magi")
        self.assertTrue(body.startswith("One dollar and eighty-seven cents. That was all."))
        self.assertTrue(body.rstrip().endswith("They are the magi."))

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
        self.assertEqual(raw[5:], body.split())   # 先頭の見出し'THE GIFT OF THE MAGI'(5語)を除き、語・順序とも原文のまま

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
        self.assertEqual(res["keep_names"], ["Della", "Jim"])
        self.assertLessEqual(res["items"], w.ESSENTIALS_MAX_ITEMS)

    def test_ending_not_spoiled_in_seed_withhold(self):
        with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
            s = json.load(f)
        self.assertIn("Before Jim reveals it", s["source_essentials"]["ending_reveal"]["withhold_until_end"])
        self.assertIn("The Gift of the Magi", s["conversion_plan"])


class VoiceAndSpeakerTest(unittest.TestCase):
    def test_voice_assignment_follows_deterministic_rule(self):
        names = st.STORY_SPEAKER_CONFIG[KEY]["dialogue_voice_tts_names"]
        self.assertEqual(names, {"narrator": "Aoede", "della": "Zephyr", "madame": "Kore", "jim": "Algieba"})
        self.assertEqual(r.STORY_REGISTRY[KEY]["voice_tts_names_plan"], names)
        asg = st.derive_voice_assignment(KEY)
        self.assertTrue(all(row["pinned"] == (row["gender"] == "female") for row in asg["speakers"]))   # 男性=pinなし。女性=FY-FZ-FEMALE-VOICE-RANK-01で順位変更前の制作済みVoiceをpin(制作済み作品は差替えない)

    def test_speakers_resolve_and_unknown_fails_closed(self):
        self.assertEqual(a63.normalize_speaker("dialogue:jim", KEY), "jim")
        self.assertEqual(a63.resolve_dialogue_voice("della", KEY), "Zephyr")
        with self.assertRaises(Exception):
            a63.normalize_speaker("dialogue:other", KEY)

    def test_attr_schema_enum_is_story_roster(self):
        sch = w.build_attr_schema(KEY)
        enum = sch["schema"]["properties"]["attributions"]["items"]["properties"]["speaker"]["enum"]
        self.assertEqual(enum, ["della", "madame", "jim", "other", "narrator"])

    def test_main_character_for_revise_prompt(self):
        self.assertIn("only Della may have a personal name", w.build_revise_prompt("BODY", KEY))

    def test_deterministic_attribution_on_speech_tags(self):
        paras = ['"Will you buy my hair?" asked Della.', '"I buy hair," said Madame.', '"You\'ve cut off your hair?" asked Jim.']
        quotes = st.extract_quotes(paras)
        det = st.deterministic_attribution(paras, quotes, story_key=KEY)
        self.assertEqual(list(det.values()), ["della", "madame", "jim"])


class LintTest(unittest.TestCase):
    def test_lint_blocks_ending_spoiler_not_normal_support(self):
        ok = st.lint_support_text("On Christmas Eve, Della sells her long hair to buy a present for her husband Jim.", "en", KEY)
        self.assertEqual(ok, [])
        bad = st.lint_support_text("In the end Jim has sold his watch to buy the combs.", "en", KEY)
        self.assertTrue(any(x.startswith("SPOILER:") for x in bad))
        bad_ja = st.lint_support_text("ジムは時計を売ってデラの櫛を買っていた。", "ja", KEY)
        self.assertTrue(any(x.startswith("SPOILER:") for x in bad_ja))
        names = st.lint_support_text("Madame Sofronie buys her hair.", "en", KEY)
        self.assertTrue(names)


class ExistingStoriesUnchangedTest(unittest.TestCase):
    def test_existing_three_stories_values_unchanged(self):
        ow = r.STORY_REGISTRY["the_open_window"]
        self.assertEqual(ow["e2e_pages_dir"], "user_test/family_z_open_window_01")
        self.assertEqual(ow["voice_tts_names_plan"], {"narrator": "Aoede", "vera": "Zephyr", "framton": "Algieba",
                                                     "mrs_sappleton": "Kore", "men": "Schedar"})
        self.assertIs(ow["rights_block"], r.OPEN_WINDOW_RIGHTS_BLOCK)
        mel = r.STORY_REGISTRY["melos"]
        self.assertEqual(mel["voice_tts_names_plan"], {"narrator": "Aoede", "selinuntius": "Erinome", "dionysius": "Charon"})
        aty = r.STORY_REGISTRY["after_twenty_years"]
        self.assertEqual(aty["voice_tts_names_plan"], {"narrator": "Aoede", "bob": "Algieba", "patrolman": "Schedar", "detective": "Fenrir"})
        self.assertEqual(w.STORY_MAIN_CHARACTER["melos"], "Melos")
        self.assertEqual(w.STORY_MAIN_CHARACTER["the_open_window"], "Framton")
        self.assertEqual(w.STORY_MAIN_CHARACTER["after_twenty_years"], "Bob")
        self.assertEqual(st.STORY_LINT_CONFIG["the_open_window"]["forbidden_names"][0], "Sappleton")


class IsolationTest(unittest.TestCase):
    def test_context_paths_do_not_touch_other_stories(self):
        ctx = r.E2EContext(story_key=KEY, slug=KEY, run="run_sf_prod_01")
        self.assertEqual(ctx.pages_dir, "user_test/family_z_gift_of_the_magi_01")
        self.assertEqual(ctx.out_dir, "er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01")
        self.assertEqual(ctx.seed_dir, "er026_output/family_z_production_e2e_01/the_gift_of_the_magi/seed")
        self.assertEqual(ctx.management_id, "FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01")
        for p in (ctx.pages_dir, ctx.out_dir, ctx.seed_dir):
            for other in ("melos", "open_window", "after_twenty"):
                self.assertNotIn(other, p.lower())


if __name__ == "__main__":
    unittest.main()
