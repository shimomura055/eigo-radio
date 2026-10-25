# -*- coding: utf-8 -*-
"""er118_fz_dialogue_context_tts_trial_01 の unit test (API 0、TTSもLLMも呼ばない)。
実行: PYTHONUTF8=1 .venv/Scripts/python.exe -m unittest er118_fz_dialogue_context_tts_trial_01_test_01 -v
"""
import json
import os
import shutil
import unittest

import numpy as np

import er118_fz_dialogue_context_tts_trial_01 as t


def text_section(prompt: str) -> str:
    return prompt.split("=== TEXT TO SPEAK", 1)[1]


def style_section(prompt: str) -> str:
    return prompt.split("=== END STYLE INSTRUCTIONS ===", 1)[0]


class SelectionTests(unittest.TestCase):
    def test_targets_are_real_adv_dialogue_clips(self):
        plan = t.load_plan()
        cl = {c["id"]: c for c in plan["clips"]}
        self.assertEqual(len(t.TARGETS), 8)
        self.assertEqual(len({x["id"] for x in t.TARGETS}), 8)
        for x in t.TARGETS:
            self.assertTrue(cl[x["id"]]["voice_role"].startswith("dialogue:"), x["id"])
        self.assertEqual({c["id"] for c in plan["clips"] if c["voice_role"].startswith("dialogue:")}, set(t.TARGET_IDS))

    def test_existing_audio_records_valid(self):
        for cid in t.TARGET_IDS:
            r = t.existing_audio_record(cid)
            self.assertTrue(r["original_matches_attempt_sha"], cid)
            self.assertEqual(r["tts_execution_mode"], "STANDARD")
            self.assertEqual(r["tts_model_id"], t.TTS_MODEL)
            self.assertEqual(r["style_effective_sha256"], t.EXPECTED_BASE_STYLE_SHA)
            self.assertIsNone(r["reuse_key_style_prefix_sha256"])      # Productionのreuse_keyにstyle hashが無い事実
            self.assertEqual(r["attempts"], 1)
            clip = {c["id"]: c for c in t.load_plan()["clips"]}[cid]
            self.assertEqual(t.tts_voice(clip), r["voice"], "②に使うVoice(voice_assignment)は①の実生成Voiceと同一")


class StyleTests(unittest.TestCase):
    def setUp(self):
        self.plan = t.load_plan()
        self.cl = {c["id"]: c for c in self.plan["clips"]}

    def test_base_style_is_production_default_and_prompt_matches_recorded_sha(self):
        self.assertEqual(t.sha_text(t.base_style()), t.EXPECTED_BASE_STYLE_SHA)
        clip = self.cl["full_story_part2_c7"]
        p = t.build_prompt(t.tts_text_for(clip), t.style_for_arm("base", None, None))
        self.assertTrue(t.sha_text(p).startswith("8c917f335f2be3f5"))   # EVIDENCE_01 §1の再構成sha(先行調査)と一致

    def test_ctx_differs_from_base_only_by_context_block(self):
        for x in t.TARGETS:
            clip = self.cl[x["id"]]
            ctx = t.extract_context(self.plan, x["id"])
            note = {"state": "She is anxious but determined.", "scene": "She stands in a shop.", "reaction": ""}
            b = t.build_prompt(t.tts_text_for(clip), t.style_for_arm("base", ctx, None))
            c = t.build_prompt(t.tts_text_for(clip), t.style_for_arm("ctx", ctx, note))
            self.assertEqual(text_section(b), text_section(c), "TEXT TO SPEAK区画は①②で完全同一")
            sb, sc = style_section(b), style_section(c)
            self.assertTrue(sc.startswith(sb.rstrip()), "②のSTYLE区画は①の文字列で始まる")
            tail = sc[len(sb.rstrip()):]
            self.assertTrue(tail.strip().startswith("CONTEXT FOR THIS ONE LINE"))
            self.assertEqual(sb.count("CONTEXT FOR"), 0)

    def test_target_text_not_in_context_block_and_text_section_only_target(self):
        for x in t.TARGETS:
            clip = self.cl[x["id"]]
            ctx = t.extract_context(self.plan, x["id"])
            blk = t.build_context_block(ctx, {"state": "s", "scene": "", "reaction": ""})
            self.assertNotIn(clip["text"], blk, x["id"])
            c = t.build_prompt(t.tts_text_for(clip), t.style_for_arm("ctx", ctx, None))
            self.assertEqual(text_section(c).split("===\n", 1)[1].split("\n=== END TEXT TO SPEAK")[0], t.tts_text_for(clip))
            self.assertIn("Do NOT read", blk)

    def test_context_extraction_rules(self):
        c7 = t.extract_context(self.plan, "full_story_part2_c7")
        self.assertIn("she whispered.", c7["stage_direction_sentences"])
        self.assertEqual(c7["narration_after"], "she whispered.")
        c5 = t.extract_context(self.plan, "full_story_part2_c5")
        self.assertEqual([d["text"] for d in c5["prev_dialogue"]], ['"Will you buy my hair?"', '"Twenty dollars."'])
        self.assertEqual(c5["next_dialogue"], [])    # 間の地の文(87語)が時間経過とみなされ除外
        c4 = t.extract_context(self.plan, "full_story_part2_c4")
        self.assertEqual(c4["stage_direction_sentences"], [])   # 演出語なし=対照
        for x in t.TARGETS:
            c = t.extract_context(self.plan, x["id"])
            self.assertLessEqual(len(c["prev_dialogue"]), 2)
            self.assertLessEqual(len(c["next_dialogue"]), 1)

    def test_all_context_text_is_verbatim_from_story(self):
        plan_text = " ".join(c["text"] for c in self.plan["clips"])
        for x in t.TARGETS:
            c = t.extract_context(self.plan, x["id"])
            for s in c["stage_direction_sentences"] + [c["narration_before"], c["narration_after"]] + [d["text"] for d in c["prev_dialogue"] + c["next_dialogue"]]:
                if s:
                    self.assertIn(s.strip(), plan_text)


class ReuseSeparationTests(unittest.TestCase):
    def test_production_reuse_key_cannot_distinguish_styles_but_trial_key_can(self):
        plan = t.load_plan()
        clip = {c["id"]: c for c in plan["clips"]}["full_story_part2_c7"]
        ctx = t.extract_context(plan, clip["id"])
        pk = t.production_reuse_key_for(clip)
        self.assertIsNone(pk["style_prefix_sha256"])     # Production: dialogueはstyle hash=None=②のStyleでも①を再利用してしまう
        sb, sc = t.style_for_arm("base", ctx, None), t.style_for_arm("ctx", ctx, {"state": "x", "scene": "", "reaction": ""})
        kb, kc = t.trial_reuse_key(clip, "base", sb, 1), t.trial_reuse_key(clip, "ctx", sc, 1)
        self.assertNotEqual(kb, kc)
        self.assertNotEqual(kb["style_sha256"], kc["style_sha256"])
        self.assertNotEqual(t.trial_reuse_key(clip, "ctx", sc, 1), t.trial_reuse_key(clip, "ctx", sc, 2))

    def test_module_does_not_import_or_call_production_reuse_or_store(self):
        with open(os.path.join(t.ROOT, "er118_fz_dialogue_context_tts_trial_01.py"), encoding="utf-8") as f:
            src = f.read()
        for bad in ("run_tts_stage(", "_cached_entry(", "master_audio_store", "er006_master"):
            code = [ln for ln in src.splitlines() if bad in ln and not ln.strip().startswith(("#", '"'))]
            self.assertEqual([ln for ln in code if "def " not in ln], [], bad)


class EmotionValidationTests(unittest.TestCase):
    def setUp(self):
        plan = t.load_plan()
        self.ctxs = [t.extract_context(plan, x) for x in ("full_story_part2_c7", "full_story_part2_c4")]

    def test_accept_verbatim_evidence(self):
        raw = [{"clip_id": "full_story_part2_c7", "speaker_state": "Della is quietly hopeful and afraid.", "scene": "She waits at home for Jim.",
                "reaction_to_previous": "", "evidence": ["she whispered", "kept returning to the mirror"], "has_explicit_cue": True},
               {"clip_id": "full_story_part2_c4", "speaker_state": "plain", "scene": "", "reaction_to_previous": "", "evidence": [], "has_explicit_cue": False}]
        v = t.validate_emotion_items(raw, self.ctxs)
        self.assertEqual(v["full_story_part2_c7"]["status"], "ACCEPTED")
        self.assertEqual(v["full_story_part2_c4"]["status"], "NO_EXPLICIT_CUE")
        self.assertEqual(v["full_story_part2_c4"]["state"], t.EMOTION_FALLBACK_STATE)

    def test_discard_non_verbatim_evidence_and_invented_names(self):
        raw = [{"clip_id": "full_story_part2_c7", "speaker_state": "Della is terrified.", "scene": "x", "reaction_to_previous": "",
                "evidence": ["she trembled with fear"], "has_explicit_cue": True},
               {"clip_id": "full_story_part2_c4", "speaker_state": "She speaks as Sofronie would, coldly.", "scene": "", "reaction_to_previous": "",
                "evidence": ["Twenty dollars."], "has_explicit_cue": True}]
        v = t.validate_emotion_items(raw, self.ctxs)
        self.assertEqual(v["full_story_part2_c7"]["status"], "DISCARDED")
        self.assertTrue(any(r.startswith("evidence_not_verbatim") for r in v["full_story_part2_c7"]["discard_reasons"]))
        self.assertEqual(v["full_story_part2_c4"]["status"], "DISCARDED")
        self.assertTrue(any("new_proper_noun" in r for r in v["full_story_part2_c4"]["discard_reasons"]))
        self.assertEqual(v["full_story_part2_c7"]["state"], t.EMOTION_FALLBACK_STATE)

    def test_missing_item_and_overlong_discarded(self):
        v = t.validate_emotion_items([], self.ctxs)
        self.assertEqual(v["full_story_part2_c7"]["status"], "DISCARDED")
        long_state = " ".join(["word"] * 40)
        v2 = t.validate_emotion_items([{"clip_id": "full_story_part2_c7", "speaker_state": long_state, "scene": "", "reaction_to_previous": "",
                                         "evidence": ["she whispered"], "has_explicit_cue": True}], self.ctxs)
        self.assertEqual(v2["full_story_part2_c7"]["status"], "DISCARDED")


class LeakageTests(unittest.TestCase):
    def setUp(self):
        plan = t.load_plan()
        self.ctx = t.extract_context(plan, "full_story_part2_c7")

    def test_clean_asr_not_flagged(self):
        r = t.leakage_check("Please let him still think I'm pretty.", self.ctx, None)
        self.assertFalse(r["flagged"])
        self.assertTrue(t.verbatim_check("Please let him still think I'm pretty.", self.ctx["text"])["token_equal"])

    def test_context_words_flagged(self):
        r = t.leakage_check("Please let him still think I'm pretty. Narration just before dinner was nearly ready", self.ctx, None)
        self.assertTrue(r["flagged"])
        r3 = t.leakage_check("Please let him still think I'm pretty. By seven, dinner was nearly ready.", self.ctx, None)
        self.assertTrue(r3["flagged"])
        r4 = t.leakage_check("Please let him still think I'm pretty. She whispered.", self.ctx, None)
        self.assertTrue(r4["flagged"] or r4["surplus_words"] > 0)


class CaptureTests(unittest.TestCase):
    def test_capture_records_prompt_and_restores_env_and_factory(self):
        import er006_batch_tts_wiring_01 as bw
        orig = bw.make_batch_tts_call_fn
        called = []
        bw.make_batch_tts_call_fn = lambda m, v, *a, **k: (lambda prompt: called.append(prompt) or b"pcm")
        prev = os.environ.get("TTS_EXECUTION_MODE")
        try:
            log = []
            with t.capture_tts_requests(log, lambda: "lbl"):
                self.assertEqual(os.environ["TTS_EXECUTION_MODE"], "STANDARD")
                fn = bw.make_batch_tts_call_fn(t.TTS_MODEL, "Zephyr")
                fn("PROMPT BODY")
            self.assertEqual(called, ["PROMPT BODY"])
            self.assertEqual(log[0]["prompt"], "PROMPT BODY")
            self.assertEqual(log[0]["voice"], "Zephyr")
            self.assertEqual(log[0]["model"], t.TTS_MODEL)
            self.assertEqual(log[0]["tts_execution_mode"], "STANDARD")
            self.assertEqual(os.environ.get("TTS_EXECUTION_MODE"), prev)
        finally:
            bw.make_batch_tts_call_fn = orig


class GuardTests(unittest.TestCase):
    """DefaultOffIsolation相当: GO無しでは有料経路が一切起動せず、API呼出0・副作用ファイル0。"""
    def _listing(self):
        d = os.path.join(t.ROOT, t.OUT_DIR)
        out = []
        for dp, _dn, fns in os.walk(d):
            out += [os.path.join(dp, f) for f in fns]
        return sorted(out)

    def test_no_go_file_blocks_gen_and_llm(self):
        self.assertFalse(os.path.exists(os.path.join(t.ROOT, t.PHASE1_GO_FILE)))
        before = self._listing()
        with self.assertRaises(SystemExit):
            t.generate_arm("ctx", 1)
        with self.assertRaises(SystemExit):
            t.run_emotion_llm()
        self.assertEqual(before, self._listing())
        self.assertFalse(os.path.exists(os.path.join(t.ROOT, t.OUT_DIR, "raw_usage_log.jsonl")))

    def test_cap_over_30_rejected(self):
        p = os.path.join(t.ROOT, t.PHASE1_GO_FILE)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        try:
            with open(p, "w") as f:
                json.dump({"managed_id": t.MANAGED_ID, "cap_jpy": 31, "arms": ["ctx"]}, f)
            with self.assertRaises(SystemExit):
                t._require_go()
        finally:
            os.remove(p)


class GenerateArmInjectionTests(unittest.TestCase):
    def setUp(self):
        self._out = t.OUT_DIR
        t.OUT_DIR = "er118_output/_unit_tmp"
        os.makedirs(os.path.join(t.ROOT, t.OUT_DIR, "llm"), exist_ok=True)
        plan = t.load_plan()
        ctxs = [t.extract_context(plan, x) for x in t.TARGET_IDS]
        raw = [{"clip_id": c["clip_id"], "speaker_state": "plain", "scene": "", "reaction_to_previous": "", "evidence": [], "has_explicit_cue": False} for c in ctxs]
        t.save_json(f"{t.OUT_DIR}/llm/emotion_notes.json", {"validated": t.validate_emotion_items(raw, ctxs)})

    def tearDown(self):
        shutil.rmtree(os.path.join(t.ROOT, t.OUT_DIR), ignore_errors=True)
        t.OUT_DIR = self._out

    def _fake(self, calls):
        import soundfile as sf

        def gen(text, out_path, voice, **kw):
            calls.append((text, voice, kw))
            sf.write(out_path, (np.sin(np.arange(24000) / 20) * 0.1).astype("float32"), 24000)
            return {"status": "OK", "asr_text": text.strip('"'), "audio_classification": "NORMALIZED_MATCH"}
        return gen

    def test_arms_pass_expected_style_override(self):
        calls = []
        t.generate_arm("base", 1, gen_fn=self._fake(calls), only=["full_story_part2_c7"])
        self.assertEqual(len(calls), 1)
        self.assertIsNone(calls[0][2]["style_prefix_override"])        # ①と同一=既定style
        self.assertEqual(calls[0][1], "Zephyr")
        calls2 = []
        t.generate_arm("ctx", 1, gen_fn=self._fake(calls2), only=["full_story_part2_c7"])
        sty = calls2[0][2]["style_prefix_override"]
        self.assertTrue(sty.startswith(t.base_style().rstrip()))
        self.assertIn("CONTEXT FOR THIS ONE LINE", sty)
        self.assertEqual(calls[0][0], calls2[0][0])                     # 本文・Voiceは同一
        self.assertEqual(calls[0][1], calls2[0][1])
        self.assertTrue(os.path.isfile(os.path.join(t.ROOT, t.OUT_DIR, "gen/ctx_t1/full_story_part2_c7/request_full.json")))
        with open(os.path.join(t.ROOT, t.OUT_DIR, "gen/ctx_t1/full_story_part2_c7/result.json"), encoding="utf-8") as f:
            rec = json.load(f)
        self.assertEqual(rec["reuse_key_trial"]["arm"], "ctx")


    def test_analyze_all_end_to_end_with_fake_generation(self):
        t.build_phase0_artifacts()
        t.generate_arm("base", 1, gen_fn=self._fake([]))
        t.generate_arm("ctx", 1, gen_fn=self._fake([]))
        page = "er118_output/_unit_page_tmp2"
        try:
            a = t.analyze_all(out_dir=t.OUT_DIR, page_dir=page)
            self.assertEqual(a["arms"], ["base_t1", "ctx_t1"])
            row = a["clips"]["full_story_part2_c7"]
            self.assertTrue(row["ctx_t1"]["verbatim"]["token_equal"])
            self.assertFalse(row["ctx_t1"]["leakage"]["flagged"])
            self.assertTrue(os.path.isfile(os.path.join(t.ROOT, page, "audio", "ctx_t1_full_story_part2_c7.mp3")))
            with open(os.path.join(t.ROOT, page, "index.html"), encoding="utf-8") as f:
                doc = f.read()
            self.assertIn("参考take: base_t1", doc)
            self.assertEqual(doc.count("未生成"), 0)
        finally:
            shutil.rmtree(os.path.join(t.ROOT, page), ignore_errors=True)


class MeasureAndPageTests(unittest.TestCase):
    def test_f0_on_tone(self):
        x = np.sin(2 * np.pi * 200 * np.arange(24000) / 24000) * 0.3
        f = t.f0_stats(x, 24000)
        self.assertAlmostEqual(f["median_hz"], 200, delta=8)

    def test_page_has_noindex_and_no_dummy_audio_for_missing_arm(self):
        t.build_phase0_artifacts()
        sel = t.load_json(f"{t.OUT_DIR}/phase0/selection.json")
        tmp = "er118_output/_unit_page_tmp"
        try:
            ap = t.build_page(sel, {"base": {sel[0]["id"]: "audio/A.mp3"}, "ctx": {}}, out_dir=tmp)
            with open(ap, encoding="utf-8") as f:
                doc = f.read()
            self.assertIn("noindex", doc)
            self.assertEqual(doc.count("<audio"), 1)
            self.assertEqual(doc.count("未生成"), 15)    # 8*2 - 1
        finally:
            shutil.rmtree(os.path.join(t.ROOT, tmp), ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
