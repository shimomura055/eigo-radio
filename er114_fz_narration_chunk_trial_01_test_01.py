# -*- coding: utf-8 -*-
import os
import unittest
import er114_fz_narration_chunk_trial_01 as m

TTH = "er026_output/family_z_dev_trials/fz_essence_01/the_tell_tale_heart/1b_s1"


def _clip(words_text, voice="narrator", cid="c1"):
    t = m.normalize_for_tts(words_text)
    return {"id": cid, "voice": voice, "word_count": len(t.split()), "text": t}


class T(unittest.TestCase):
    def test_non_narrator_never_split(self):
        p = ["word " * 120]
        r = m.plan_clip_chunks(_clip(p[0], voice="old_man"), p)
        self.assertFalse(r["split"])

    def test_below_threshold_unchanged(self):
        p = ["One two three. " * 20]
        self.assertFalse(m.plan_clip_chunks(_clip(p[0]), p)["split"])

    def test_paragraph_boundary_preferred_and_lossless(self):
        paras = [("Alpha beta gamma delta. " * 11).strip(), ("Eps zeta eta theta. " * 11).strip(), ("Iota kappa lambda mu. " * 11).strip()]
        c = _clip(" ".join(paras))
        r = m.plan_clip_chunks(c, paras)
        self.assertTrue(r["split"])
        self.assertTrue(all(x["priority"] == 0 for x in r["cuts"]))
        self.assertEqual(m.normalize_for_tts(" ".join(x["text"] for x in r["chunks"])), c["text"])

    def test_never_cut_inside_quote(self):
        para = ('He said "Go now. Run fast. Do it." ' * 1) + ("Plain words here and there. " * 30)
        c = _clip(para)
        r = m.plan_clip_chunks(c, [para])
        for ch in r["chunks"]:
            self.assertEqual(ch["text"].count('"') % 2, 0)

    def test_min_chunk_words(self):
        para = "Short one. " * 3 + "x " * 130
        r = m.plan_clip_chunks(_clip(para), [para])
        for ch in r.get("chunks", []):
            self.assertGreaterEqual(ch["words"], m.MIN_CHUNK_WORDS)

    @unittest.skipUnless(os.path.exists(TTH + "/segment_plan_b1b.json"), "1b_s1 dir missing")
    def test_tth_1b_s1_expected(self):
        r = m.plan_run(TTH, "b1b", "writer/r2.md")
        got = {c["clip_id"]: [x["words"] for x in c["chunks"]] for c in r["clips"] if c["split"]}
        self.assertEqual(got, {"full_story_part1_c1": [78, 63], "full_story_part2_c3": [69, 49], "full_story_part3_c1": [74, 74]})
        # 既存のDialogue/話者切替clipは不変
        self.assertTrue(all(not c["split"] for c in r["clips"] if c["clip_id"] in ("full_story_part2_c1", "full_story_part2_c2")))

    @unittest.skipUnless(os.path.exists(TTH + "/segment_plan_b1b.json"), "1b_s1 dir missing")
    def test_tth_b_fine_expected(self):
        r = m.plan_run(TTH, "b1b", "writer/r2.md", target_words=50)
        got = {c["clip_id"]: [x["words"] for x in c["chunks"]] for c in r["clips"] if c["split"]}
        self.assertEqual(got, {"full_story_part1_c1": [36, 42, 63], "full_story_part2_c3": [44, 25, 49], "full_story_part3_c1": [57, 35, 56]})
        for c in r["clips"]:
            if c["split"]:
                self.assertEqual(sum(x["words"] for x in c["chunks"]), next(w for w in (141, 118, 148) if sum(x["words"] for x in c["chunks"]) == w))

    @unittest.skipUnless(os.path.exists(TTH + "/segment_plan_b1b.json"), "1b_s1 dir missing")
    def test_tth_b_alt_manual_expected_and_paragraph_info(self):
        r = m.plan_run(TTH, "b1b", "writer/r2.md", manual_cuts={"full_story_part2_c3": [2], "full_story_part3_c1": [1]})
        got = {c["clip_id"]: [x["words"] for x in c["chunks"]] for c in r["clips"] if c["split"]}
        self.assertEqual(got, {"full_story_part2_c3": [46, 72], "full_story_part3_c1": [57, 91]})
        self.assertTrue(all(c["paragraph_info_lost"] is False for c in r["clips"] if c["split"]))
        c = next(c for c in r["clips"] if c["clip_id"] == "full_story_part2_c3")
        self.assertTrue(c["chunks"][0]["text"].endswith("Wide open."))
        c = next(c for c in r["clips"] if c["clip_id"] == "full_story_part3_c1")
        self.assertTrue(c["chunks"][0]["text"].endswith("how little I feared?"))

    def test_manual_rejects_last_paragraph_cut(self):
        paras = ["One two three. " * 20, "Four five six. " * 20]
        c = _clip(" ".join(paras))
        with self.assertRaises(AssertionError):
            m.plan_clip_chunks_manual(c, paras, [1])

    def test_default_target_unchanged_and_sum(self):
        paras = [("Alpha beta gamma delta. " * 11).strip(), ("Eps zeta eta theta. " * 11).strip(), ("Iota kappa lambda mu. " * 11).strip()]
        c = _clip(" ".join(paras))
        r = m.plan_clip_chunks(c, paras)
        self.assertEqual(sum(x["words"] for x in r["chunks"]), c["word_count"])
        self.assertEqual(r["target_words"], 100)


if __name__ == "__main__":
    unittest.main()
