# -*- coding: utf-8 -*-
"""FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_01: 『藪の中』(芥川龍之介)のSTORY_REGISTRY登録値のtest。
登録はdata表への値追加のみ(ロジック・Prompt・閾値・Gate・flag・既存作品entryは無変更)。
(a)必須キーが既存作品と一致 (b)権利Gate (c)seed.json/story.md/SOURCE_PROVENANCE整合 (d)Seed承認検査(validate_source_essentials、5件上限・fail-closed)
(e)Voice割当が正式Voice表の決定的割当規則どおり(証言者7名、新Voice探索なし) (f)lint表 (g)既存作品の値が不変 (h)pages/run/管理IDが既存作品に触れない。
API呼出0・ファイル書込0(Seed承認検査はtempdirにstory.mdを複製して行う)。"""
import hashlib
import json
import os
import re
import shutil
import tempfile
import unittest

import er026_family_z_fiction_production_runner_01 as r
import er062_family_z_structure_01 as st
import er062_family_z_writer_01 as w
import er063_family_z_audio_01 as a63

KEY = "in_a_grove"
SEED_DIR = "er026_seeds/in_a_grove"
SRC_DIR = "docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/sources"


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _seed():
    with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
        return json.load(f)


class RegistryTest(unittest.TestCase):
    def test_registered_alongside_existing(self):
        self.assertLessEqual({"melos", "the_open_window", "after_twenty_years", "the_gift_of_the_magi", "the_monkeys_paw",
                              "the_tell_tale_heart", KEY}, set(r.STORY_REGISTRY))

    def test_required_keys_identical_to_existing(self):
        for other in ("the_open_window", "melos", "after_twenty_years", "the_monkeys_paw", "the_tell_tale_heart"):
            self.assertEqual(set(r.STORY_REGISTRY[KEY]), set(r.STORY_REGISTRY[other]))

    def test_values(self):
        c = r.STORY_REGISTRY[KEY]
        self.assertEqual(c["story_type"], "literature")
        self.assertEqual(c["topic_title"], "In a Grove")
        self.assertEqual(c["page_title_ja"], "藪の中")
        self.assertEqual(c["japanese_title_text"], "藪の中(In a Grove)")
        self.assertEqual(c["japanese_title_tts"], "藪の中")
        self.assertEqual(c["audio_file_prefix"], "InAGrove")
        self.assertEqual(c["trial_seed_dir"], SEED_DIR)
        self.assertEqual(c["e2e_pages_dir"], "user_test/family_z_in_a_grove_01")
        self.assertEqual(c["e2e_management_id"], "FAMILY-Z-IN-A-GROVE-PRODUCTION-01")
        self.assertEqual(c["e2e_theme_tag"], "FAMILY_Z_IN_A_GROVE_PRODUCTION_01")
        self.assertIs(c["rights_block"], r.IN_A_GROVE_RIGHTS_BLOCK)
        self.assertIs(c["speaker_config"], st.STORY_SPEAKER_CONFIG[KEY])

    def test_cli_choice_derived_from_registry(self):
        a = r.build_parser().parse_args(["--story", KEY, "--run", "run_x"])
        self.assertEqual(a.story, KEY)

    def test_voice_keywords_identical_to_speaker_config(self):
        c = r.STORY_REGISTRY[KEY]
        self.assertEqual(c["voice_keywords"], c["speaker_config"]["dialogue_voice_keywords"])
        self.assertEqual(c["voice_keywords"], c["speaker_config"]["z_voice_keywords"])


class RightsGateTest(unittest.TestCase):
    def test_gate_pass_and_fields(self):
        r.check_rights_gate(r.IN_A_GROVE_RIGHTS_BLOCK)
        b = r.IN_A_GROVE_RIGHTS_BLOCK
        for f in r.RIGHTS_REQUIRED_FIELDS:
            self.assertTrue(b.get(f), f)
        self.assertEqual(b["author_death_date"], "1927-07-24")
        self.assertEqual(b["confirmed_date"], "2026-10-28")
        for token in ("1977-12-31", "遡及しない", "1922", "kijyunn.html", "対象外"):
            self.assertIn(token, b["jp_public_domain_basis"])
        self.assertTrue(b["source_url"].startswith("https://www.aozora.gr.jp/cards/000879/"))

    def test_gate_fails_closed_when_field_missing(self):
        bad = dict(r.IN_A_GROVE_RIGHTS_BLOCK)
        bad["source_url"] = ""
        with self.assertRaises(r.RightsGateError):
            r.check_rights_gate(bad)

    def test_legal_use_basis_is_same_user_decision_text(self):
        self.assertEqual(r.IN_A_GROVE_RIGHTS_BLOCK["legal_use_basis"], r.OPEN_WINDOW_RIGHTS_BLOCK["legal_use_basis"])


class SeedFilesTest(unittest.TestCase):
    def test_seed_schema_same_as_tell_tale_heart(self):
        with open("er026_seeds/the_tell_tale_heart/seed.json", encoding="utf-8") as f:
            o = json.load(f)
        s = _seed()
        self.assertEqual(list(o), list(s))
        self.assertEqual(set(o["rights_status"]), set(s["rights_status"]))
        self.assertEqual(set(o["source_essentials"]), set(s["source_essentials"]))
        self.assertEqual(s["rights_status"]["confirmed_date"], "2026-10-28")

    def test_load_trial_seed_and_story(self):
        loaded = r.load_trial_seed_and_story(KEY)
        title, body = r.strip_markdown_title(loaded["raw_trial_text"])
        self.assertEqual(title, "藪の中")
        self.assertTrue(body.startswith("#### 検非違使に問われたる木樵りの物語"))
        self.assertTrue(body.rstrip().endswith("中有の闇へ沈んでしまった。………"))

    def test_story_md_matches_source_provenance(self):
        with open(f"{SEED_DIR}/SOURCE_PROVENANCE.json", encoding="utf-8") as f:
            p = json.load(f)
        self.assertEqual(_sha(f"{SEED_DIR}/story.md"), p["story_md_sha256"])
        self.assertEqual(_sha(f"{SEED_DIR}/source_aozora_extract.txt"), p["source_aozora_extract_txt_sha256"])
        self.assertEqual(_sha(f"{SRC_DIR}/yabu_no_naka_body.txt"), p["source_aozora_extract_txt_sha256"])
        self.assertEqual(_sha(f"{SRC_DIR}/179_15255.html"), p["xhtml_179_15255_html_sha256"])
        self.assertEqual(p["http_status"], 200)
        self.assertIn("000879", p["source_url"])
        self.assertIn(p["story_md_sha256"], _seed()["rights_status"]["confirmation_quote"])

    def test_story_md_is_extract_with_headings_only(self):
        """story.mdは抽出本文から(見出し記号の置換・題名行の追加・末尾の日付行の除去)以外を一切変えていない。"""
        with open(f"{SEED_DIR}/source_aozora_extract.txt", encoding="utf-8") as f:
            ext = f.read()
        with open(f"{SEED_DIR}/story.md", encoding="utf-8") as f:
            story = f.read()
        ext_body = ext.rstrip("\n").split("\n")
        self.assertEqual(ext_body[-1], "（大正十年十二月）")   # 日付行のみ除去
        expect = "### 藪の中\n\n" + re.sub(r"^##H ", "#### ", "\n".join(ext_body[:-2]), flags=re.M) + "\n"
        self.assertEqual(story, expect)
        self.assertEqual(len(re.findall(r"^#### ", story, flags=re.M)), 7)   # 7証言
        self.assertEqual(len(ext), _seed_chars())

    def test_source_essentials_pass_seed_approval_check(self):
        seed = _seed()
        d = tempfile.mkdtemp()
        try:
            shutil.copyfile(f"{SEED_DIR}/story.md", os.path.join(d, "primary_text_excerpt.md"))   # seed_check stageと同形(story.md複製)
            res = w.validate_source_essentials(seed, KEY, d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertTrue(res["present"])
        self.assertTrue(res["source_quote_checked_vs_last_paragraph"])
        self.assertEqual(res["keep_names"], ["Tajomaru", "Masago", "Takehiro"])
        self.assertEqual(res["items"], 5)   # ending 1 + setups 0 + causality 1 + keep_name 3 = 上限ちょうど
        self.assertLessEqual(res["items"], w.ESSENTIALS_MAX_ITEMS)

    def test_fail_closed_when_over_limit_or_quote_wrong(self):
        d = tempfile.mkdtemp()
        try:
            shutil.copyfile(f"{SEED_DIR}/story.md", os.path.join(d, "primary_text_excerpt.md"))
            over = _seed()
            over["source_essentials"]["setups_and_payoffs"] = [{"setup": "a", "payoff": "b"}]
            with self.assertRaises(w.FamilyZSeedEssentialsStop):
                w.validate_source_essentials(over, KEY, d)
            bad = _seed()
            bad["source_essentials"]["ending_reveal"]["source_quote"] = "おれは助かった。"
            with self.assertRaises(w.FamilyZSeedEssentialsStop):
                w.validate_source_essentials(bad, KEY, d)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_source_quote_is_verbatim_last_sentence_of_original(self):
        q = _seed()["source_essentials"]["ending_reveal"]["source_quote"]
        with open(f"{SRC_DIR}/yabu_no_naka_body.txt", encoding="utf-8") as f:
            paras = [x for x in re.split(r"\n\s*\n", f.read()) if x.strip()]
        self.assertEqual(paras[-1].strip(), "（大正十年十二月）")
        self.assertTrue(paras[-2].strip().endswith(q + "………"))   # 末尾の最終文(省略符を除く)

    def test_no_single_truth_in_seed(self):
        """Seedの文言が真相を一本化しない(ユーザー原文§2-3・§5)。"""
        s = _seed()
        ess = s["source_essentials"]
        self.assertIn("no verdict", ess["ending_reveal"]["meaning"])
        self.assertIn("which of the three accounts is true", ess["ending_reveal"]["meaning"])
        self.assertIn("never tell the listener who the real killer is or which account is true", ess["ending_reveal"]["withhold_until_end"])
        self.assertIn("no one, in or out of the story, resolves the clash", ess["key_causality"][0])
        cp = s["conversion_plan"]
        for t in ("do not decide which one is true", "Do not reconcile the accounts", "do not call anyone a liar"):
            self.assertIn(t, cp)

    def test_original_structure_present_in_seed(self):
        elems = " ".join(_seed()["seed_elements"]).lower()
        for token in ("seven separate spoken testimonies", "woodcutter", "monk", "constable", "old woman", "tajomaru", "masago", "takehiro",
                      "twenty-third stroke", "medium", "unseen hand", "kill that man", "kill me", "rope", "comb"):
            self.assertIn(token, elems, token)


def _seed_chars():
    with open(f"{SEED_DIR}/SOURCE_PROVENANCE.json", encoding="utf-8") as f:
        return json.load(f)["characters_body"]


class VoiceAndSpeakerTest(unittest.TestCase):
    EXPECT = {"narrator": "Aoede", "woodcutter": "Algieba", "monk": "Schedar", "constable": "Fenrir", "old_woman": "Zephyr",
              "tajomaru": "Orus", "masago": "Kore", "takehiro": "Puck"}

    def test_voice_assignment_follows_deterministic_rule(self):
        names = st.STORY_SPEAKER_CONFIG[KEY]["dialogue_voice_tts_names"]
        self.assertEqual(names, self.EXPECT)
        self.assertEqual(r.STORY_REGISTRY[KEY]["voice_tts_names_plan"], names)
        asg = st.derive_voice_assignment(KEY)
        self.assertTrue(all(not row["pinned"] for row in asg["speakers"]))   # pin(個別例外)なし
        self.assertNotIn("narrator_voice_pin", asg)                           # 本文narratorも既定Aoede
        pool = st.FAMILY_Z_DIALOGUE_VOICE_POOL
        males = [row["voice"] for row in asg["speakers"] if row["gender"] == "male"]
        females = [row["voice"] for row in asg["speakers"] if row["gender"] == "female"]
        self.assertEqual(males, list(pool["male"]))      # 男性5名=Pool5名ちょうど(循環なし)
        self.assertEqual(females, list(pool["female"][:2]))
        self.assertEqual(len(set(self.EXPECT.values())), 8)   # 8声すべて別

    def test_speakers_resolve_and_unknown_fails_closed(self):
        self.assertEqual(a63.normalize_speaker("dialogue:tajomaru", KEY), "tajomaru")
        self.assertEqual(a63.resolve_dialogue_voice("takehiro", KEY), "Puck")
        self.assertEqual(a63.resolve_dialogue_voice("old_woman", KEY), "Zephyr")
        with self.assertRaises(Exception):
            a63.normalize_speaker("dialogue:other", KEY)

    def test_attr_schema_enum_is_story_roster(self):
        sch = w.build_attr_schema(KEY)
        enum = sch["schema"]["properties"]["attributions"]["items"]["properties"]["speaker"]["enum"]
        self.assertEqual(enum, ["woodcutter", "monk", "constable", "old_woman", "tajomaru", "masago", "takehiro", "other", "narrator"])

    def test_main_character_and_names_for_revise_prompt(self):
        self.assertEqual(w.STORY_MAIN_CHARACTER[KEY], "Tajomaru")
        ess = w.Essentials(_seed()["source_essentials"])
        p = w.build_revise_prompt("BODY", KEY, essentials=ess)
        self.assertIn("Tajomaru", p)
        self.assertIn("keep the name", p)
        block = ess.block_full
        for t in ("Tajomaru", "Masago", "Takehiro", "keep the name", "おれはそれぎり永久に、中有の闇へ沈んでしまった。", "Not before the ending"):
            self.assertIn(t, block, t)
        self.assertIn("no narrator of its own", block)

    def test_deterministic_attribution_on_speech_tags(self):
        paras = ['"I found him this morning," said the woodcutter.', '"He was with a woman," said the monk.',
                 '"This is Tajomaru," said the constable.', '"Please find my daughter," cried the old woman.',
                 '"I killed him fairly," said Tajomaru.', '"I could not die," said Masago.', '"I stabbed myself," said Takehiro.']
        quotes = st.extract_quotes(paras)
        det = st.deterministic_attribution(paras, quotes, story_key=KEY)
        self.assertEqual(list(det.values()), ["woodcutter", "monk", "constable", "old_woman", "tajomaru", "masago", "takehiro"])

    def test_old_woman_not_confused_with_wife(self):
        paras = ['"My daughter is strong," said the old woman.', '"I am ashamed," said the wife.']
        quotes = st.extract_quotes(paras)
        det = st.deterministic_attribution(paras, quotes, story_key=KEY)
        self.assertEqual(list(det.values()), ["old_woman", "masago"])


class LintTest(unittest.TestCase):
    def test_lint_blocks_last_testimony_and_truth_claims_not_normal_support(self):
        ok = st.lint_support_text("A man is found dead in a thicket, and several people tell what they know about it.", "en", KEY)
        self.assertEqual(ok, [])
        for bad_text in ("The dead man says he killed himself.", "In the end an unseen hand pulls out the dagger.",
                         "The real killer is the bandit."):
            bad = st.lint_support_text(bad_text, "en", KEY)
            self.assertTrue(any(x.startswith("SPOILER:") for x in bad), bad_text)
        bad_ja = st.lint_support_text("最後に夫の死霊は自殺したと語る。", "ja", KEY)
        self.assertTrue(any(x.startswith("SPOILER:") for x in bad_ja))
        # 多襄丸・真砂の語りの内容自体は後半Commentに現れ得る(結末の語のみ禁止、一般語・「どれが本当か分からない」は禁止しない)
        mid = st.lint_support_text("Tajomaru says he fought the man fairly, but Masago tells it differently, and nobody can say which is true.", "en", KEY)
        self.assertEqual([x for x in mid if x.startswith("SPOILER:")], [])
        mid_ja = st.lint_support_text("多襄丸は正々堂々と戦ったと語るが、真砂の話はそれと食い違い、どちらが本当かは誰にも分からない。", "ja", KEY)
        self.assertEqual([x for x in mid_ja if x.startswith("SPOILER:")], [])

    def test_forbidden_surname_style_name(self):
        self.assertTrue(any(x.startswith("FORBIDDEN_NAME:") for x in st.lint_support_text("Takehiro of Kanazawa", "en", KEY)))
        self.assertEqual([x for x in st.lint_support_text("Takehiro and Masago travel together.", "en", KEY) if x.startswith("FORBIDDEN_NAME:")], [])


class ExistingStoriesUnchangedTest(unittest.TestCase):
    def test_existing_stories_values_unchanged(self):
        tth = r.STORY_REGISTRY["the_tell_tale_heart"]
        self.assertEqual(tth["voice_tts_names_plan"], {"narrator": "Fenrir", "old_man": "Algieba", "officer": "Schedar"})
        mp = r.STORY_REGISTRY["the_monkeys_paw"]
        self.assertEqual(mp["voice_tts_names_plan"], {"narrator": "Aoede", "morris": "Algieba", "mr_white": "Schedar",
                                                     "herbert": "Fenrir", "visitor": "Orus", "mrs_white": "Zephyr"})
        gm = r.STORY_REGISTRY["the_gift_of_the_magi"]
        self.assertEqual(gm["voice_tts_names_plan"], {"narrator": "Aoede", "della": "Zephyr", "madame": "Kore", "jim": "Algieba"})
        mel = r.STORY_REGISTRY["melos"]
        self.assertEqual(mel["voice_tts_names_plan"], {"narrator": "Aoede", "selinuntius": "Erinome", "dionysius": "Charon"})
        for k, v in (("melos", "Melos"), ("the_open_window", "Framton"), ("after_twenty_years", "Bob"),
                     ("the_gift_of_the_magi", "Della"), ("the_monkeys_paw", "Mr. White"),
                     ("the_tell_tale_heart", "the narrator (who stays unnamed, as in the original)")):
            self.assertEqual(w.STORY_MAIN_CHARACTER[k], v)
        self.assertEqual(st.STORY_LINT_CONFIG["the_monkeys_paw"]["forbidden_names"][0], "Morris")
        self.assertEqual(w.ESSENTIALS_EXEMPT_STORIES, ("melos",))   # 免除はMelosのみ(本作は免除されない=fail-closed対象)
        self.assertEqual(st.STORY_NARRATOR_VOICE_PINS, {"the_tell_tale_heart": "Fenrir"})   # 本作にnarrator pinなし


class IsolationTest(unittest.TestCase):
    def test_context_paths_do_not_touch_other_stories(self):
        ctx = r.E2EContext(story_key=KEY, slug=KEY, run="run_sf_prod_01")
        self.assertEqual(ctx.pages_dir, "user_test/family_z_in_a_grove_01")
        self.assertEqual(ctx.out_dir, "er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01")
        self.assertEqual(ctx.seed_dir, "er026_output/family_z_production_e2e_01/in_a_grove/seed")
        self.assertEqual(ctx.management_id, "FAMILY-Z-IN-A-GROVE-PRODUCTION-01")
        for p in (ctx.pages_dir, ctx.out_dir, ctx.seed_dir):
            for other in ("melos", "open_window", "after_twenty", "monkeys_paw", "magi", "tell_tale"):
                self.assertNotIn(other, p.lower())


if __name__ == "__main__":
    unittest.main()
