# -*- coding: utf-8 -*-
"""FAMILY-Z-YUKI-ONNA-PRODUCTION-01 委任_01: 『雪女』(Lafcadio Hearn "Yuki-Onna", Kwaidan 1904)のSTORY_REGISTRY登録値のtest。
登録はdata表への値追加のみ(ロジック・Prompt・閾値・Gate・flag・既存作品entryは無変更)。
(a)必須キーが既存作品と一致 (b)権利Gate (c)seed.json/story.md/SOURCE_PROVENANCE整合 (d)Seed承認検査(validate_source_essentials)
(e)Voice割当が正式Voice表の決定的割当規則どおり(女性は新順位Leda、pinなし) (f)lint表 (g)既存作品の値が不変 (h)pages/run/管理IDが既存作品に触れない
(i)ユーザー重点(わかりやすさ: 2話者・同一Voice・直線時系列)がSeedに入っている。API呼出0・ファイル書込0。"""
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

KEY = "yuki_onna"
SEED_DIR = "er026_seeds/yuki_onna"


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _seed():
    with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
        return json.load(f)


class RegistryTest(unittest.TestCase):
    def test_registered_alongside_existing(self):
        self.assertLessEqual({"melos", "the_open_window", "after_twenty_years", "the_gift_of_the_magi", "the_monkeys_paw",
                              "the_tell_tale_heart", "in_a_grove", KEY}, set(r.STORY_REGISTRY))

    def test_required_keys_identical_to_existing(self):
        for other in ("the_open_window", "melos", "after_twenty_years", "the_monkeys_paw", "in_a_grove"):
            self.assertEqual(set(r.STORY_REGISTRY[KEY]), set(r.STORY_REGISTRY[other]))

    def test_values(self):
        c = r.STORY_REGISTRY[KEY]
        self.assertEqual(c["story_type"], "literature")
        self.assertEqual(c["topic_title"], "Yuki-Onna")
        self.assertEqual(c["page_title_ja"], "雪女")
        self.assertEqual(c["japanese_title_text"], "雪女(Yuki-Onna)")
        self.assertEqual(c["japanese_title_tts"], "雪女")
        self.assertEqual(c["audio_file_prefix"], "YukiOnna")
        self.assertEqual(c["trial_seed_dir"], SEED_DIR)
        self.assertEqual(c["e2e_pages_dir"], "user_test/family_z_yuki_onna_01")
        self.assertEqual(c["e2e_management_id"], "FAMILY-Z-YUKI-ONNA-PRODUCTION-01")
        self.assertIs(c["rights_block"], r.YUKI_ONNA_RIGHTS_BLOCK)
        self.assertIs(c["speaker_config"], st.STORY_SPEAKER_CONFIG[KEY])

    def test_cli_choice_derived_from_registry(self):
        a = r.build_parser().parse_args(["--story", KEY, "--run", "run_x"])
        self.assertEqual(a.story, KEY)


class RightsGateTest(unittest.TestCase):
    def test_gate_pass_and_fields(self):
        r.check_rights_gate(r.YUKI_ONNA_RIGHTS_BLOCK)
        b = r.YUKI_ONNA_RIGHTS_BLOCK
        for f in r.RIGHTS_REQUIRED_FIELDS:
            self.assertTrue(b.get(f), f)
        self.assertEqual(b["author_death_date"], "1904-09-26")
        self.assertEqual(b["confirmed_date"], "2026-10-30")
        for token in ("3,794", "1965-05-21", "遡及しない", "1904"):
            self.assertIn(token, b["jp_public_domain_basis"])
        self.assertTrue(b["source_url"].startswith("https://www.gutenberg.org/"))

    def test_gate_fails_closed_when_field_missing(self):
        bad = dict(r.YUKI_ONNA_RIGHTS_BLOCK)
        bad["source_url"] = ""
        with self.assertRaises(r.RightsGateError):
            r.check_rights_gate(bad)

    def test_legal_use_basis_is_same_user_decision_text(self):
        self.assertEqual(r.YUKI_ONNA_RIGHTS_BLOCK["legal_use_basis"], r.OPEN_WINDOW_RIGHTS_BLOCK["legal_use_basis"])

    def test_death_plus_wartime_extension_computed(self):
        import datetime
        self.assertEqual(datetime.date(1954, 12, 31) + datetime.timedelta(days=3794), datetime.date(1965, 5, 21))


class SeedFilesTest(unittest.TestCase):
    def test_seed_schema_same_as_tell_tale_heart(self):
        with open("er026_seeds/the_tell_tale_heart/seed.json", encoding="utf-8") as f:
            o = json.load(f)
        s = _seed()
        self.assertEqual(list(o), list(s))
        self.assertEqual(set(o["rights_status"]), set(s["rights_status"]))
        self.assertEqual(set(o["source_essentials"]), set(s["source_essentials"]))
        self.assertEqual(s["rights_status"]["confirmed_date"], "2026-10-30")

    def test_load_trial_seed_and_story(self):
        loaded = r.load_trial_seed_and_story(KEY)
        title, body = r.strip_markdown_title(loaded["raw_trial_text"])
        self.assertEqual(title, "Yuki-Onna")
        self.assertTrue(body.startswith("In a village of Musashi Province, there lived two woodcutters"))
        self.assertTrue(body.rstrip().endswith("Never again was she seen."))

    def test_story_md_matches_source_provenance(self):
        with open(f"{SEED_DIR}/SOURCE_PROVENANCE.json", encoding="utf-8") as f:
            p = json.load(f)
        self.assertEqual(_sha(f"{SEED_DIR}/story.md"), p["story_md_sha256"])
        self.assertEqual(_sha(f"{SEED_DIR}/source_gutenberg_raw_extract.txt"), p["source_gutenberg_raw_extract_txt_sha256"])
        self.assertEqual(p["http_status"], 200)
        self.assertIn("1210", p["source_url"])
        for h in (p["story_md_sha256"], p["pg1210_txt_sha256"], p["source_gutenberg_raw_extract_txt_sha256"]):
            self.assertIn(h, _seed()["rights_status"]["confirmation_quote"])

    def test_story_md_is_extract_with_markers_removed_only(self):
        """story.mdは抽出本文から(脚注記号・挿絵行・斜体記号の除去、段落内改行の連結、題名行の追加)以外を一切変えていない。"""
        with open(f"{SEED_DIR}/source_gutenberg_raw_extract.txt", encoding="utf-8") as f:
            ext = f.read()
        with open(f"{SEED_DIR}/story.md", encoding="utf-8") as f:
            story = f.read()
        b = ext.split("\n", 2)[2]
        b = re.sub(r"\[Illustration\][^\n]*\n", "", b)
        b = re.sub(r"\s?\(\d\)", "", b)
        b = re.sub(r"\[\d\]", "", b)
        b = b.replace("_", "")
        paras = [re.sub(r"\s+", " ", x).strip() for x in re.split(r"\n\s*\n", b) if x.strip()]
        self.assertEqual(story, "### Yuki-Onna\n\n" + "\n\n".join(paras) + "\n")
        self.assertEqual(len(paras), 18)

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
        self.assertEqual(res["keep_names"], ["Minokichi", "Yuki"])
        self.assertEqual(res["items"], 5)   # ending 1 + setups 1 + causality 1 + keep_name 2 = 上限ちょうど
        self.assertLessEqual(res["items"], w.ESSENTIALS_MAX_ITEMS)

    def test_fail_closed_when_over_limit_or_quote_wrong(self):
        d = tempfile.mkdtemp()
        try:
            shutil.copyfile(f"{SEED_DIR}/story.md", os.path.join(d, "primary_text_excerpt.md"))
            over = _seed()
            over["source_essentials"]["setups_and_payoffs"].append({"setup": "a", "payoff": "b"})
            with self.assertRaises(w.FamilyZSeedEssentialsStop):
                w.validate_source_essentials(over, KEY, d)
            bad = _seed()
            bad["source_essentials"]["ending_reveal"]["source_quote"] = "She was never seen again."
            with self.assertRaises(w.FamilyZSeedEssentialsStop):
                w.validate_source_essentials(bad, KEY, d)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_source_quote_is_verbatim_last_sentence_of_original(self):
        q = _seed()["source_essentials"]["ending_reveal"]["source_quote"]
        with open(f"{SEED_DIR}/story.md", encoding="utf-8") as f:
            paras = [x for x in re.split(r"\n\s*\n", f.read()) if x.strip()]
        self.assertTrue(paras[-1].strip().endswith(q))

    def test_original_chain_present_in_seed(self):
        """ユーザー重点(原文§3): 吹雪の夜の出会い->誰にも話すな->再会/正体判明->約束を破った結果、の因果がSeedに入っている。"""
        elems = " ".join(_seed()["seed_elements"]).lower()
        for token in ("snowstorm", "woman all in white", "if he ever tells anybody", "even his own mother", "kill him", "yuki",
                      "ten children", "paper lamp", "it was i", "children asleep", "never again was she seen", "mosaku", "minokichi"):
            self.assertIn(token, elems, token)

    def test_clarity_instructions_in_conversion_plan(self):
        """ユーザー重点(原文§1・§3): 音声で追える(場面冒頭の時・場所の1文、時系列、話者2名のみ、同一Voice、約束の再提示)。"""
        cp = _seed()["conversion_plan"]
        for t in ("strictly chronological", "open each of the three scenes with one short, plain sentence", "Only two characters speak",
                  "Yuki and the woman in white are the same speaker", "plain speech tag that names the speaker",
                  "told nobody", "Do not reveal before the last scene that Yuki is the woman in white"):
            self.assertIn(t, cp)

    def test_reveal_withheld_until_end_and_narration_third_person(self):
        ess = _seed()["source_essentials"]
        self.assertIn("do not say or hint outright that Yuki is the woman in white", ess["ending_reveal"]["withhold_until_end"])
        self.assertIn("third person", ess["narration_voice"])


class VoiceAndSpeakerTest(unittest.TestCase):
    EXPECT = {"narrator": "Aoede", "yuki": "Leda", "minokichi": "Algieba"}

    def test_voice_assignment_follows_deterministic_rule(self):
        names = st.STORY_SPEAKER_CONFIG[KEY]["dialogue_voice_tts_names"]
        self.assertEqual(names, self.EXPECT)
        self.assertEqual(r.STORY_REGISTRY[KEY]["voice_tts_names_plan"], names)
        asg = st.derive_voice_assignment(KEY)
        self.assertTrue(all(not row["pinned"] for row in asg["speakers"]))   # 新規作品=pinなし(FY-FZ-FEMALE-VOICE-RANK-01の新順位が適用される)
        self.assertNotIn("narrator_voice_pin", asg)
        self.assertNotIn(KEY, st.STORY_VOICE_PINS)
        self.assertEqual(len(set(self.EXPECT.values())), 3)   # 3声すべて別

    def test_speakers_resolve_and_unknown_fails_closed(self):
        self.assertEqual(a63.normalize_speaker("dialogue:yuki", KEY), "yuki")
        self.assertEqual(a63.resolve_dialogue_voice("yuki", KEY), "Leda")
        self.assertEqual(a63.resolve_dialogue_voice("minokichi", KEY), "Algieba")
        with self.assertRaises(Exception):
            a63.normalize_speaker("dialogue:other", KEY)

    def test_attr_schema_enum_is_story_roster(self):
        sch = w.build_attr_schema(KEY)
        enum = sch["schema"]["properties"]["attributions"]["items"]["properties"]["speaker"]["enum"]
        self.assertEqual(enum, ["yuki", "minokichi", "other", "narrator"])

    def test_main_character_and_names_for_revise_prompt(self):
        self.assertEqual(w.STORY_MAIN_CHARACTER[KEY], "Minokichi")
        ess = w.Essentials(_seed()["source_essentials"])
        p = w.build_revise_prompt("BODY", KEY, essentials=ess)
        self.assertIn("Minokichi", p)
        self.assertIn("keep the name", p)
        for t in ("Minokichi", "Yuki", "keep the name", "Never again was she seen.", "Not before the ending"):
            self.assertIn(t, ess.block_full, t)

    def test_deterministic_attribution_on_speech_tags(self):
        paras = ['"Remember what I say," whispered the woman in white.', '"Tell me about her," said Yuki.',
                 '"She was very like you," said Minokichi.', '"It was I," cried Yuki.']
        quotes = st.extract_quotes(paras)
        det = st.deterministic_attribution(paras, quotes, story_key=KEY)
        self.assertEqual(list(det.values()), ["yuki", "yuki", "minokichi", "yuki"])

    def test_same_speaker_for_white_woman_and_wife(self):
        cfg = st.STORY_SPEAKER_CONFIG[KEY]
        self.assertIn("the woman in white", cfg["z_voice_keywords"]["yuki"][0] + " " + " ".join(cfg["z_voice_keywords"]["yuki"]))
        self.assertIn("the same speaker in every scene", cfg["attr_roster_text"])
        self.assertEqual(sum(1 for row in st.STORY_VOICE_ROSTER[KEY] if row["gender"] == "female"), 1)

    def test_unclosed_opening_quote_is_a_quote_span(self):
        """藪の中(OPEN-596)で是正済みのquote_spans(story非依存)が本作でも効く: 閉じ引用符の無い末尾の“発言は発話区間になる。"""
        para = 'Yuki cried, “It was I, Yuki!'
        sp = st.quote_spans(para)
        self.assertEqual(len(sp), 1)
        self.assertTrue(para[sp[0][0]:sp[0][1]].startswith("“It was I"))


class LintTest(unittest.TestCase):
    def test_lint_blocks_identity_reveal_not_normal_support(self):
        ok = st.lint_support_text("A young woodcutter survives a snowstorm night after a strange woman in white makes him promise never to tell anyone.", "en", KEY)
        self.assertEqual(ok, [])
        for bad_text in ("Yuki is the snow woman, and he breaks his promise.", "In the end she melts into mist and is never seen again.",
                         "The true identity of his wife is revealed."):
            bad = st.lint_support_text(bad_text, "en", KEY)
            self.assertTrue(any(x.startswith("SPOILER:") for x in bad), bad_text)
        bad_ja = st.lint_support_text("妻の正体は雪女だった。", "ja", KEY)
        self.assertTrue(any(x.startswith("SPOILER:") for x in bad_ja))
        mid_ja = st.lint_support_text("吹雪の夜、若い木こりは白い女から「誰にも話すな」と命じられる。", "ja", KEY)
        self.assertEqual([x for x in mid_ja if x.startswith("SPOILER:")], [])

    def test_forbidden_name(self):
        self.assertTrue(any(x.startswith("FORBIDDEN_NAME:") for x in st.lint_support_text("Mosaku and Minokichi", "en", KEY)))
        self.assertEqual([x for x in st.lint_support_text("Minokichi and Yuki live together.", "en", KEY) if x.startswith("FORBIDDEN_NAME:")], [])


class ExistingStoriesUnchangedTest(unittest.TestCase):
    def test_existing_stories_values_unchanged(self):
        tth = r.STORY_REGISTRY["the_tell_tale_heart"]
        self.assertEqual(tth["voice_tts_names_plan"], {"narrator": "Fenrir", "old_man": "Algieba", "officer": "Schedar"})
        mp = r.STORY_REGISTRY["the_monkeys_paw"]
        self.assertEqual(mp["voice_tts_names_plan"], {"narrator": "Aoede", "morris": "Algieba", "mr_white": "Schedar",
                                                     "herbert": "Fenrir", "visitor": "Orus", "mrs_white": "Zephyr"})
        ig = r.STORY_REGISTRY["in_a_grove"]
        self.assertEqual(ig["voice_tts_names_plan"]["old_woman"], "Zephyr")
        self.assertEqual(ig["voice_tts_names_plan"]["masago"], "Kore")
        for k, v in (("melos", "Melos"), ("the_open_window", "Framton"), ("after_twenty_years", "Bob"),
                     ("the_gift_of_the_magi", "Della"), ("the_monkeys_paw", "Mr. White"), ("in_a_grove", "Tajomaru")):
            self.assertEqual(w.STORY_MAIN_CHARACTER[k], v)
        self.assertEqual(w.ESSENTIALS_EXEMPT_STORIES, ("melos",))
        self.assertEqual(st.STORY_NARRATOR_VOICE_PINS, {"the_tell_tale_heart": "Fenrir"})
        self.assertNotIn(KEY, st.STORY_NARRATOR_VOICE_PINS)   # 本作のnarratorは既定Aoede


class IsolationTest(unittest.TestCase):
    def test_context_paths_do_not_touch_other_stories(self):
        ctx = r.E2EContext(story_key=KEY, slug=KEY, run="run_yo_prod_01")
        self.assertEqual(ctx.pages_dir, "user_test/family_z_yuki_onna_01")
        self.assertEqual(ctx.out_dir, "er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01")
        self.assertEqual(ctx.seed_dir, "er026_output/family_z_production_e2e_01/yuki_onna/seed")
        self.assertEqual(ctx.management_id, "FAMILY-Z-YUKI-ONNA-PRODUCTION-01")
        for p in (ctx.pages_dir, ctx.out_dir, ctx.seed_dir):
            for other in ("melos", "open_window", "after_twenty", "monkeys_paw", "magi", "tell_tale", "grove"):
                self.assertNotIn(other, p.lower())


if __name__ == "__main__":
    unittest.main()
