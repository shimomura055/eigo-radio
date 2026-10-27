# -*- coding: utf-8 -*-
"""FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 委任_01: 『告げ口心臓』(Edgar Allan Poe)のSTORY_REGISTRY登録値のtest。
登録はdata表への値追加のみ(ロジック・Prompt・閾値・Gate・flag・既存作品entryは無変更)。
(a)必須キーが既存作品と一致 (b)権利Gate (c)seed.json/story.md/SOURCE_PROVENANCE整合 (d)Seed承認検査(validate_source_essentials)
(e)Voice割当が正式Voice表の決定的割当規則どおり (f)lint表 (g)既存作品の値が不変 (h)pages/run/管理IDが既存作品に触れない。
API呼出0・ファイル書込0(Seed承認検査はtempdirにstory.mdを複製して行う)。"""
import hashlib
import json
import os
import shutil
import tempfile
import unittest

import er026_family_z_fiction_production_runner_01 as r
import er062_family_z_structure_01 as st
import er062_family_z_writer_01 as w
import er063_family_z_audio_01 as a63

KEY = "the_tell_tale_heart"
SEED_DIR = "er026_seeds/the_tell_tale_heart"


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class RegistryTest(unittest.TestCase):
    def test_registered_alongside_existing(self):
        self.assertLessEqual({"melos", "the_open_window", "after_twenty_years", "the_gift_of_the_magi", "the_monkeys_paw", KEY},
                             set(r.STORY_REGISTRY))

    def test_required_keys_identical_to_existing(self):
        for other in ("the_open_window", "melos", "after_twenty_years", "the_monkeys_paw"):
            self.assertEqual(set(r.STORY_REGISTRY[KEY]), set(r.STORY_REGISTRY[other]))

    def test_values(self):
        c = r.STORY_REGISTRY[KEY]
        self.assertEqual(c["story_type"], "literature")
        self.assertEqual(c["topic_title"], "The Tell-Tale Heart")
        self.assertEqual(c["japanese_title_text"], "告げ口心臓(The Tell-Tale Heart)")
        self.assertEqual(c["japanese_title_tts"], "告げ口心臓")
        self.assertEqual(c["trial_seed_dir"], SEED_DIR)
        self.assertEqual(c["e2e_pages_dir"], "user_test/family_z_tell_tale_heart_01")
        self.assertEqual(c["e2e_management_id"], "FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01")
        self.assertIs(c["rights_block"], r.TELL_TALE_HEART_RIGHTS_BLOCK)
        self.assertIs(c["speaker_config"], st.STORY_SPEAKER_CONFIG[KEY])

    def test_cli_choice_derived_from_registry(self):
        a = r.build_parser().parse_args(["--story", KEY, "--run", "run_x"])
        self.assertEqual(a.story, KEY)


class RightsGateTest(unittest.TestCase):
    def test_gate_pass_and_fields(self):
        r.check_rights_gate(r.TELL_TALE_HEART_RIGHTS_BLOCK)
        b = r.TELL_TALE_HEART_RIGHTS_BLOCK
        for f in r.RIGHTS_REQUIRED_FIELDS:
            self.assertTrue(b.get(f), f)
        self.assertEqual(b["author_death_date"], "1849-10-07")
        self.assertEqual(b["confirmed_date"], "2026-10-24")
        for token in ("3,794", "1910-05-22", "遡及しない", "1843-01"):
            self.assertIn(token, b["jp_public_domain_basis"])
        self.assertTrue(b["source_url"].startswith("https://www.gutenberg.org/"))

    def test_gate_fails_closed_when_field_missing(self):
        bad = dict(r.TELL_TALE_HEART_RIGHTS_BLOCK)
        bad["source_url"] = ""
        with self.assertRaises(r.RightsGateError):
            r.check_rights_gate(bad)

    def test_legal_use_basis_is_same_user_decision_text(self):
        self.assertEqual(r.TELL_TALE_HEART_RIGHTS_BLOCK["legal_use_basis"], r.OPEN_WINDOW_RIGHTS_BLOCK["legal_use_basis"])


class SeedFilesTest(unittest.TestCase):
    def test_seed_schema_same_as_monkeys_paw(self):
        with open("er026_seeds/the_monkeys_paw/seed.json", encoding="utf-8") as f:
            o = json.load(f)
        with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
            s = json.load(f)
        self.assertEqual(list(o), list(s))
        self.assertEqual(set(o["rights_status"]), set(s["rights_status"]))
        self.assertEqual(set(o["source_essentials"]), set(s["source_essentials"]))
        self.assertEqual(s["rights_status"]["confirmed_date"], "2026-10-24")

    def test_load_trial_seed_and_story(self):
        loaded = r.load_trial_seed_and_story(KEY)
        title, body = r.strip_markdown_title(loaded["raw_trial_text"])
        self.assertEqual(title, "The Tell-Tale Heart")
        self.assertTrue(body.startswith("True!—nervous—very, very dreadfully nervous I had been and am"))
        self.assertTrue(body.rstrip().endswith("It is the beating of his hideous heart!”"))

    def test_story_md_matches_source_provenance(self):
        with open(f"{SEED_DIR}/SOURCE_PROVENANCE.json", encoding="utf-8") as f:
            p = json.load(f)
        self.assertEqual(_sha(f"{SEED_DIR}/story.md"), p["story_md_sha256"])
        self.assertEqual(_sha(f"{SEED_DIR}/source_gutenberg_raw_extract.txt"), p["source_gutenberg_raw_extract_txt_sha256"])
        self.assertEqual(p["http_status"], 200)
        self.assertIn("2148", p["source_url"])

    def test_raw_extract_and_story_md_have_same_words(self):
        with open(f"{SEED_DIR}/source_gutenberg_raw_extract.txt", encoding="utf-8") as f:
            raw = f.read().replace("_", "").split()
        raw = raw[3:]   # 見出し'THE TELL-TALE HEART.'(3語)は物語の語ではない(SOURCE_PROVENANCE story_md_transform)
        loaded = r.load_trial_seed_and_story(KEY)
        _t, body = r.strip_markdown_title(loaded["raw_trial_text"])
        self.assertEqual(raw, body.split())   # 見出しを除き、語・順序とも原文のまま
        self.assertEqual(len(body.split()), 2076)

    def test_source_essentials_pass_seed_approval_check(self):
        with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
            seed = json.load(f)
        d = tempfile.mkdtemp()
        try:
            shutil.copyfile(f"{SEED_DIR}/story.md", os.path.join(d, "primary_text_excerpt.md"))   # seed_check stageと同形(story.md複製)
            res = w.validate_source_essentials(seed, KEY, d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertTrue(res["present"])
        self.assertTrue(res["source_quote_checked_vs_last_paragraph"])
        self.assertEqual(res["keep_names"], [])   # 原作に人名なし(語り手・老人・警官すべて無名)
        self.assertLessEqual(res["items"], w.ESSENTIALS_MAX_ITEMS)

    def test_ending_not_spoiled_in_seed_withhold(self):
        with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
            s = json.load(f)
        self.assertIn("do not hint that the narrator will confess", s["source_essentials"]["ending_reveal"]["withhold_until_end"])
        self.assertIn("no explanation of whether the sound was real or only in his mind", s["conversion_plan"])

    def test_original_events_present_in_seed(self):
        with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
            s = json.load(f)
        elems = " ".join(s["seed_elements"]).lower()
        for token in ("vulture", "seven nights", "eighth night", "who's there", "watch wrapped in cotton", "three planks",
                      "police officers", "tear up the planks", "hideous heart", "not mad"):
            self.assertIn(token, elems.replace("for seven nights", "seven nights"), token)


class VoiceAndSpeakerTest(unittest.TestCase):
    def test_voice_assignment_follows_deterministic_rule(self):
        names = st.STORY_SPEAKER_CONFIG[KEY]["dialogue_voice_tts_names"]
        self.assertEqual(names, {"narrator": "Fenrir", "old_man": "Algieba", "officer": "Schedar"})
        self.assertEqual(r.STORY_REGISTRY[KEY]["voice_tts_names_plan"], names)
        asg = st.derive_voice_assignment(KEY)
        self.assertTrue(all(not row["pinned"] for row in asg["speakers"]))   # pin(個別例外)なし

    def test_speakers_resolve_and_unknown_fails_closed(self):
        self.assertEqual(a63.normalize_speaker("dialogue:old_man", KEY), "old_man")
        self.assertEqual(a63.resolve_dialogue_voice("officer", KEY), "Schedar")
        with self.assertRaises(Exception):
            a63.normalize_speaker("dialogue:other", KEY)

    def test_attr_schema_enum_is_story_roster(self):
        sch = w.build_attr_schema(KEY)
        enum = sch["schema"]["properties"]["attributions"]["items"]["properties"]["speaker"]["enum"]
        self.assertEqual(enum, ["old_man", "officer", "other", "narrator"])

    def test_main_character_for_revise_prompt(self):
        p = w.build_revise_prompt("BODY", KEY)
        self.assertIn("who stays unnamed", p)

    def test_deterministic_attribution_on_speech_tags(self):
        paras = ['"Who\'s there?" cried the old man.', '"Where is he?" asked the officer.']
        quotes = st.extract_quotes(paras)
        det = st.deterministic_attribution(paras, quotes, story_key=KEY)
        self.assertEqual(list(det.values()), ["old_man", "officer"])

    def test_narrator_own_quote_is_not_deterministically_assigned(self):
        paras = ['"Villains!" I shrieked, "I admit the deed!"']
        quotes = st.extract_quotes(paras)
        det = st.deterministic_attribution(paras, quotes, story_key=KEY)
        self.assertNotIn("old_man", list(det.values()))
        self.assertNotIn("officer", list(det.values()))


class LintTest(unittest.TestCase):
    def test_lint_blocks_ending_spoiler_not_normal_support(self):
        ok = st.lint_support_text("On a quiet night, a nervous man says he is not mad and tells how he watched an old man with a pale eye.", "en", KEY)
        self.assertEqual(ok, [])
        bad = st.lint_support_text("In the end the narrator will confess to the officers.", "en", KEY)
        self.assertTrue(any(x.startswith("SPOILER:") for x in bad))
        bad_ja = st.lint_support_text("最後に語り手は警官の前で自白してしまう。", "ja", KEY)
        self.assertTrue(any(x.startswith("SPOILER:") for x in bad_ja))
        # 殺害・床下の隠蔽はPart2以降のCommentに現れ得るため、結末語のみ禁止(一般語は入れない)
        mid = st.lint_support_text("The narrator hides the body under the floorboards before the officers arrive.", "en", KEY)
        self.assertEqual([x for x in mid if x.startswith("SPOILER:")], [])


class ExistingStoriesUnchangedTest(unittest.TestCase):
    def test_existing_stories_values_unchanged(self):
        mp = r.STORY_REGISTRY["the_monkeys_paw"]
        self.assertEqual(mp["voice_tts_names_plan"], {"narrator": "Aoede", "morris": "Algieba", "mr_white": "Schedar",
                                                     "herbert": "Fenrir", "visitor": "Orus", "mrs_white": "Zephyr"})
        self.assertEqual(mp["e2e_pages_dir"], "user_test/family_z_monkeys_paw_01")
        gm = r.STORY_REGISTRY["the_gift_of_the_magi"]
        self.assertEqual(gm["voice_tts_names_plan"], {"narrator": "Aoede", "della": "Zephyr", "madame": "Kore", "jim": "Algieba"})
        ow = r.STORY_REGISTRY["the_open_window"]
        self.assertEqual(ow["voice_tts_names_plan"], {"narrator": "Aoede", "vera": "Zephyr", "framton": "Algieba",
                                                     "mrs_sappleton": "Kore", "men": "Schedar"})
        mel = r.STORY_REGISTRY["melos"]
        self.assertEqual(mel["voice_tts_names_plan"], {"narrator": "Aoede", "selinuntius": "Erinome", "dionysius": "Charon"})
        aty = r.STORY_REGISTRY["after_twenty_years"]
        self.assertEqual(aty["voice_tts_names_plan"], {"narrator": "Aoede", "bob": "Algieba", "patrolman": "Schedar", "detective": "Fenrir"})
        for k, v in (("melos", "Melos"), ("the_open_window", "Framton"), ("after_twenty_years", "Bob"),
                     ("the_gift_of_the_magi", "Della"), ("the_monkeys_paw", "Mr. White")):
            self.assertEqual(w.STORY_MAIN_CHARACTER[k], v)
        self.assertEqual(st.STORY_LINT_CONFIG["the_monkeys_paw"]["forbidden_names"][0], "Morris")


class IsolationTest(unittest.TestCase):
    def test_context_paths_do_not_touch_other_stories(self):
        ctx = r.E2EContext(story_key=KEY, slug=KEY, run="run_sf_prod_01")
        self.assertEqual(ctx.pages_dir, "user_test/family_z_tell_tale_heart_01")
        self.assertEqual(ctx.out_dir, "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01")
        self.assertEqual(ctx.seed_dir, "er026_output/family_z_production_e2e_01/the_tell_tale_heart/seed")
        self.assertEqual(ctx.management_id, "FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01")
        for p in (ctx.pages_dir, ctx.out_dir, ctx.seed_dir):
            for other in ("melos", "open_window", "after_twenty", "monkeys_paw", "magi"):
                self.assertNotIn(other, p.lower())


if __name__ == "__main__":
    unittest.main()
