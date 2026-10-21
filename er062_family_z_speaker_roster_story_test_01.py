# -*- coding: utf-8 -*-
"""FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 委任_01b: 話者roster/Voice表のstory別化test。
(a)Melos出力がパラメータ化前とバイト同一(旧ATTR_USER_TMPL展開結果・SPEAKERS・keywords・Voice表・aliasesを逐語固定)
(b)『開いた窓』rosterの解決 (c)未割当Voice(mrs_sappleton)のfail-closed (d)互換aliasが同一objectでドリフトしない。
API呼出0・ファイル書込0。"""
import json
import unittest

import er026_family_z_fiction_production_runner_01 as r
import er062_family_z_structure_01 as st
import er062_family_z_writer_01 as w
import er063_family_z_audio_01 as a63

# パラメータ化前(HEAD 65a1080d5)のATTR_USER_TMPLを逐語固定({tagged_story}のみ可変)
OLD_ATTR_USER_TMPL = """Below is a short story. Every quoted line is marked with a tag of the form [[Q:id]] right before the opening quotation mark.
For EVERY tagged quote, decide the speaker:
- "melos": the main character, Melos (including when he speaks to the king or to his friend)
- "king": the ruler / tyrant / king
- "friend": Melos's friend
- "other": any other speaker (a guard, bandits, a sister, a crowd, etc.)
- "narrator": the line is not spoken by a character (e.g. a quoted phrase used by the narrator)
Be careful: a name or role that appears NEAR a quote is not always the speaker (for example, in '"I will return," Melos told the king.' the speaker is melos, not king; in '"I am here," he said to his friend.' decide who "he" is from the story).
Return one entry per tag, exactly once, using exactly the id written inside the tag.

[Story]
{tagged_story}"""

OLD_ATTR_SCHEMA = {
    "name": "z_dialogue_attribution",
    "schema": {"type": "object",
               "properties": {"attributions": {"type": "array", "items": {
                   "type": "object",
                   "properties": {"quote_id": {"type": "string"},
                                  "speaker": {"type": "string", "enum": ["melos", "king", "friend", "other", "narrator"]},
                                  "basis": {"type": "string"}},
                   "required": ["quote_id", "speaker", "basis"], "additionalProperties": False}}},
               "required": ["attributions"], "additionalProperties": False},
    "strict": True,
}


class MelosByteIdenticalSnapshotTest(unittest.TestCase):
    def test_attr_prompt_identical(self):
        story = 'Para one. [[Q:q0_1]]"Hello," said Melos.\n\nPara two.'
        self.assertEqual(w.build_attr_user_prompt(story), OLD_ATTR_USER_TMPL.format(tagged_story=story))
        self.assertEqual(w.build_attr_user_prompt(story, "melos"), OLD_ATTR_USER_TMPL.format(tagged_story=story))

    def test_attr_schema_identical(self):
        self.assertEqual(w.ATTR_SCHEMA, OLD_ATTR_SCHEMA)
        self.assertEqual(w.build_attr_schema("melos"), OLD_ATTR_SCHEMA)

    def test_structure_constants(self):
        self.assertEqual(st.SPEAKERS, ("melos", "king", "friend", "other", "narrator"))
        self.assertEqual(json.dumps(st.Z_VOICE_KEYWORDS), json.dumps(
            {"melos": ["melos"], "king": ["ruler", "king", "tyrant"], "friend": ["friend"]}))   # 挿入順も固定

    def test_voice_table_and_aliases(self):
        self.assertEqual(json.dumps(a63.FAMILY_Z_DIALOGUE_VOICE_KEYWORDS), json.dumps(
            {"melos": ["melos"], "selinuntius": ["selinuntius", "friend"],
             "dionysius": ["dionysius", "ruler", "king", "tyrant"]}))
        self.assertEqual(a63.FAMILY_Z_DIALOGUE_VOICE_TTS_NAMES,
                         {"narrator": "Aoede", "melos": "Algieba", "selinuntius": "Erinome", "dionysius": "Charon"})
        self.assertEqual(a63.SPEAKER_ALIASES,
                         {"king": "dionysius", "friend": "selinuntius", "melos": "melos", "narrator": "narrator",
                          "dionysius": "dionysius", "selinuntius": "selinuntius"})

    def test_melos_defaults_resolve_as_before(self):
        self.assertEqual(a63.normalize_speaker("dialogue:king"), "dionysius")
        self.assertEqual(a63.resolve_dialogue_voice("dionysius"), "Charon")
        self.assertEqual(a63.resolve_dialogue_voice("melos"), "Algieba")
        with self.assertRaises(a63.FamilyZVoiceMappingStop):
            a63.normalize_speaker("other")          # Melosではotherは従来どおり未対応でSTOP
        with self.assertRaises(a63.FamilyZVoiceMappingStop):
            a63.resolve_dialogue_voice("mrs_sappleton")   # Melos表に無い=従来どおり未対応

    def test_compat_aliases_are_same_objects_as_single_source(self):
        c = st.STORY_SPEAKER_CONFIG["melos"]
        self.assertIs(st.SPEAKERS, c["speakers"])
        self.assertIs(st.Z_VOICE_KEYWORDS, c["z_voice_keywords"])
        self.assertIs(a63.FAMILY_Z_DIALOGUE_VOICE_KEYWORDS, c["dialogue_voice_keywords"])
        self.assertIs(a63.FAMILY_Z_DIALOGUE_VOICE_TTS_NAMES, c["dialogue_voice_tts_names"])
        self.assertIs(a63.SPEAKER_ALIASES, c["speaker_aliases"])
        self.assertIs(r.STORY_REGISTRY["melos"]["speaker_config"], c)

    def test_deterministic_attribution_default_is_melos(self):
        paras = ['"I will return," Melos told the king.']
        qs = st.extract_quotes(paras)
        self.assertEqual(st.deterministic_attribution(paras, qs), st.deterministic_attribution(paras, qs, story_key="melos"))
        self.assertEqual(st.deterministic_attribution(paras, qs), {"q0_1": "melos"})


class OpenWindowRosterTest(unittest.TestCase):
    C = st.STORY_SPEAKER_CONFIG["the_open_window"]

    def test_registry_references_single_source(self):
        self.assertIs(r.STORY_REGISTRY["the_open_window"]["speaker_config"], self.C)

    def test_speakers_and_enum(self):
        self.assertEqual(self.C["speakers"], ("framton", "vera", "mrs_sappleton", "men", "other", "narrator"))
        self.assertEqual(w.build_attr_schema("the_open_window")["schema"]["properties"]["attributions"]["items"]
                         ["properties"]["speaker"]["enum"], list(self.C["speakers"]))

    def test_prompt_roster_and_no_melos_leak(self):
        p = w.build_attr_user_prompt("[[Q:q0_1]]\"Hi.\"", "the_open_window")
        for sp in self.C["speakers"]:
            self.assertIn(f'- "{sp}":', p)
        for leak in ("Melos", "melos", "king", "tyrant", "Selinuntius", "Dionysius"):
            self.assertNotIn(leak, p)
        self.assertIn("Framton", p)
        self.assertIn("Ronnie", p)
        self.assertTrue(p.endswith("[Story]\n[[Q:q0_1]]\"Hi.\""))

    def test_deterministic_attribution_uses_story_keywords(self):
        paras = ['"My aunt will be down presently," said Vera.', '"I hope," said the visitor.']
        qs = st.extract_quotes(paras)
        d = st.deterministic_attribution(paras, qs, story_key="the_open_window")
        self.assertEqual(d["q1_1"], "framton")
        self.assertIn(d["q0_1"], ("vera", "mrs_sappleton"))   # window内にaunt/Vera両語。先頭一致順に依存(LLMと突合しmismatchは人間確認)

    def test_reconcile_validates_against_story_roster(self):
        paras = ['"Hi," said Vera.']
        qs = st.extract_quotes(paras)
        ok = st.reconcile_attribution(paras, qs, {"q0_1": "vera"}, {"q0_1": "vera"}, "the_open_window")
        self.assertTrue(ok["ok"])
        bad = st.reconcile_attribution(paras, qs, {"q0_1": "vera"}, {"q0_1": "melos"}, "the_open_window")
        self.assertFalse(bad["ok"])        # melosはこのstoryのrosterに無い
        self.assertTrue(bad["problems"])

    def test_aliases_and_voices(self):
        self.assertEqual(a63.normalize_speaker("dialogue:vera", "the_open_window"), "vera")
        self.assertEqual(a63.resolve_dialogue_voice("vera", "the_open_window"), "Erinome")
        self.assertEqual(a63.resolve_dialogue_voice("framton", "the_open_window"), "Algieba")
        self.assertEqual(a63.resolve_dialogue_voice("men", "the_open_window"), "Charon")
        self.assertEqual(a63.resolve_dialogue_voice("narrator", "the_open_window"), "Aoede")
        with self.assertRaises(a63.FamilyZVoiceMappingStop):
            a63.normalize_speaker("other", "the_open_window")     # 想定外話者はMelos同様fail-closed
        with self.assertRaises(a63.FamilyZVoiceMappingStop):
            a63.normalize_speaker("melos", "the_open_window")

    def test_unassigned_voice_fails_closed(self):
        self.assertEqual(a63.normalize_speaker("mrs_sappleton", "the_open_window"), "mrs_sappleton")
        with self.assertRaises(a63.FamilyZVoiceMappingStop) as cm:
            a63.resolve_dialogue_voice("mrs_sappleton", "the_open_window")
        self.assertIn("VOICE_UNASSIGNED", str(cm.exception))

    def test_build_level_plan_fail_closed_on_unassigned_and_ok_otherwise(self):
        base = dict(preview_text="p", comments={1: "a", 2: "b", 3: "c"}, kp_items=[], topic_title="The Open Window",
                    japanese_title_text="開いた窓(The Open Window)")
        clips_ok = [{"id": "full_story_part1_c1", "speaker": "narrator", "text": "Hi."},
                    {"id": "full_story_part1_c2", "speaker": "vera", "text": '"Hi."'},
                    {"id": "full_story_part1_c3", "speaker": "men", "text": '"Hi."'}]
        plan = a63.build_level_plan("a2", clips_ok, story_key="the_open_window", **base)
        voices = {c.clip_id: c.voice for c in plan if c.clip_id.startswith("full_story")}
        self.assertEqual(voices, {"full_story_part1_c1": "Aoede", "full_story_part1_c2": "Erinome",
                                  "full_story_part1_c3": "Charon"})
        clips_bad = clips_ok + [{"id": "full_story_part1_c4", "speaker": "mrs_sappleton", "text": '"Hi."'}]
        with self.assertRaises(a63.FamilyZVoiceMappingStop):
            a63.build_level_plan("a2", clips_bad, story_key="the_open_window", **base)

    def test_lint_spoiler_minimal_list(self):
        cfg = st.STORY_LINT_CONFIG["the_open_window"]
        self.assertNotIn("最後に", cfg["spoiler_ja"])
        self.assertNotIn("結末", cfg["spoiler_ja"])
        self.assertIn("romance at short notice", cfg["spoiler_en"])
        self.assertEqual([], st.lint_support_text("A visitor hears an eerie story about a window.", "en", "the_open_window"))
        self.assertTrue(st.lint_support_text("The girl made up the whole story.", "en", "the_open_window"))


if __name__ == "__main__":
    unittest.main()
