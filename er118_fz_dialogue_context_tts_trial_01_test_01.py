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
        self.assertEqual(v["full_story_part2_c4"]["state"], "")   # Opus M2: 中立は状態行を出さない

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
        self.assertEqual(v["full_story_part2_c7"]["state"], "")

    def test_missing_item_and_overlong_discarded(self):
        v = t.validate_emotion_items([], self.ctxs)
        self.assertEqual(v["full_story_part2_c7"]["status"], "DISCARDED")
        long_state = " ".join(["word"] * 40)
        v2 = t.validate_emotion_items([{"clip_id": "full_story_part2_c7", "speaker_state": long_state, "scene": "", "reaction_to_previous": "",
                                         "evidence": ["she whispered"], "has_explicit_cue": True}], self.ctxs)
        self.assertEqual(v2["full_story_part2_c7"]["status"], "DISCARDED")


class LeakageTests(unittest.TestCase):
    """Opus M1: アライメント方式(difflib)、全attempt、単語境界、長さ補助フラグ。"""
    def setUp(self):
        self.plan = t.load_plan()
        self.c7 = t.extract_context(self.plan, "full_story_part2_c7")
        self.c2 = t.extract_context(self.plan, "full_story_part2_c2")

    def test_clean_asr_not_flagged(self):
        r = t.leakage_check("Please let him still think I'm pretty.", self.c7, None)
        self.assertFalse(r["flagged"])
        self.assertFalse(r["needs_listen"])
        self.assertTrue(t.verbatim_check("Please let him still think I'm pretty.", self.c7["text"])["token_equal"])

    def test_m1_c7_trailing_dialogue_tag_she_whispered_is_flagged(self):
        # 旧実装は見逃した最危険ケース(末尾が読点+CONTEXTに会話タグが入っている状況)
        r = t.leakage_check("Please let him still think I'm pretty, she whispered.", self.c7, None)
        self.assertTrue(r["flagged"])
        self.assertEqual(r["extra_tokens"], ["she", "whispered"])

    def test_m1_c2_next_line_leak_is_flagged(self):
        txt = self.c2["text"]
        r = t.leakage_check(txt + " Twenty dollars.", self.c2, None)
        self.assertTrue(r["flagged"])
        self.assertIn("twenty", r["extra_tokens"])
        self.assertTrue(r["context_only_hits"])      # 『twenty』はCONTEXTにだけある語

    def test_m1_single_speaker_label_is_flagged(self):
        r = t.leakage_check("Della " + self.c2["text"], self.c2, None)
        self.assertTrue(r["flagged"])
        self.assertEqual(r["extra_tokens"], ["della"])
        self.assertIn("della", r["context_only_hits"])

    def test_m1_homophone_replacement_not_extra(self):
        r = t.leakage_check("Please let him still think I'm pritty.", self.c7, None)   # 同数の置換=ASR揺れ
        self.assertFalse(r["flagged"])
        self.assertFalse(r["needs_listen"])

    def test_m1_single_extra_noncontext_word_needs_listen_only(self):
        r = t.leakage_check("Oh please let him still think I'm pretty.", self.c7, None)
        self.assertEqual(r["extra_tokens"], ["oh"])
        self.assertTrue(r["needs_listen"])
        self.assertFalse(r["flagged"])               # 1語かつCONTEXT専用語でない

    def test_m1_all_attempts_checked_and_final_separated(self):
        r = t.leakage_all_attempts(["Please let him still think I'm pretty, she whispered.", "Please let him still think I'm pretty."],
                                   "Please let him still think I'm pretty.", self.c7, None)
        self.assertTrue(r["leakage_any_attempt"])    # 途中attemptの混入はretryで隠れない
        self.assertFalse(r["leakage_final"])

    def test_m1_length_listen_flag(self):
        self.assertTrue(t.length_listen_flag(4.0, [2.0, 2.2]))
        self.assertFalse(t.length_listen_flag(2.7, [2.0, 2.2]))      # 1.4x未満
        self.assertFalse(t.length_listen_flag(1.0, [0.5, 0.5]))      # 1.4x超だが差が0.6秒以下

    def test_leak_flag_applies_to_base_arm_too(self):
        r = t.leakage_check("Della Please let him still think I'm pretty.", self.c7, None)   # note=None(base arm)
        self.assertTrue(r["flagged"])


class M2NeutralTests(unittest.TestCase):
    def test_neutral_has_no_state_line_and_no_plainly(self):
        plan = t.load_plan()
        ctx = t.extract_context(plan, "full_story_part2_c4")
        raw = [{"clip_id": "full_story_part2_c4", "speaker_state": "plain", "scene": "A shop.", "reaction_to_previous": "", "evidence": [], "has_explicit_cue": False}]
        v = t.validate_emotion_items(raw, [ctx])["full_story_part2_c4"]
        blk = t.build_context_block(ctx, v)
        self.assertNotIn("state of mind", blk)
        self.assertNotIn("plainly", blk.lower())
        self.assertNotIn("flat", blk.lower().replace("overly restrained", ""))
        self.assertIn("Scene: A shop.", blk)
        d = t.validate_emotion_items([], [ctx])["full_story_part2_c4"]
        self.assertEqual(d["status"], "DISCARDED")
        self.assertNotIn("state of mind", t.build_context_block(ctx, d))


class M3ContextBlockTests(unittest.TestCase):
    def setUp(self):
        self.plan = t.load_plan()

    def test_head_and_tail_verbatim_from_opus(self):
        self.assertEqual(t.CONTEXT_HEAD, "CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. "
                                         "Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)")
        self.assertEqual(t.CONTEXT_TAIL, "Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. "
                         "The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, "
                         "and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, "
                         "without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. "
                         "If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. "
                         "Do not read any word of this CONTEXT block.")

    def test_c7_dialogue_tag_not_verbatim_manner_words_only(self):
        ctx = t.extract_context(self.plan, "full_story_part2_c7")
        blk = t.build_context_block(ctx, None)
        self.assertNotIn("she whispered", blk)                       # 会話タグは逐語で入れない
        self.assertIn("Manner words from the narration: kept returning, whispered", blk)
        self.assertNotIn("Stage direction", blk)                     # 演出文の重複行は撤去

    def test_neighbor_lines_unquoted_with_not_part_of_this_line(self):
        ctx = t.extract_context(self.plan, "full_story_part2_c5")
        blk = t.build_context_block(ctx, None)
        self.assertIn("Spoken line before (said by Della; not part of this line): Will you buy my hair?", blk)
        self.assertIn("Spoken line before (said by the hair-shop owner; not part of this line): Twenty dollars.", blk)
        self.assertNotIn('"Will you buy my hair?"', blk)

    def test_dialogue_tag_detector(self):
        self.assertTrue(t.is_dialogue_tag("she whispered."))
        self.assertFalse(t.is_dialogue_tag("Della had curled her short hair, but she kept returning to the mirror."))
        self.assertFalse(t.is_dialogue_tag("By seven, dinner was nearly ready."))


class M5M6Tests(unittest.TestCase):
    def test_m5_comparison_valid_rules(self):
        sha = "abc"
        ok = t.comparison_validity({"status": "OK", "instruction_type": "english_style_prefix_wide_margin", "attempts_log": [{}]}, [{"prompt_sha256": sha}], sha)
        self.assertTrue(ok["comparison_valid"])
        fb = t.comparison_validity({"status": "OK", "instruction_type": "minimal_fallback", "attempts_log": [{}, {}]}, [{"prompt_sha256": sha}], sha)
        self.assertFalse(fb["comparison_valid"])
        self.assertTrue(fb["n_tts_calls_undercount_possible"])
        bad = t.comparison_validity({"status": "OK", "instruction_type": "english_style_prefix_wide_margin", "attempts_log": [{}]}, [{"prompt_sha256": "zzz"}], sha)
        self.assertFalse(bad["comparison_valid"])
        self.assertFalse(t.comparison_validity({"status": "STOPPED"}, [], sha)["comparison_valid"])

    def test_m6_intensity_words_discarded(self):
        plan = t.load_plan()
        ctx = t.extract_context(plan, "full_story_part2_c7")
        raw = [{"clip_id": ctx["clip_id"], "speaker_state": "Della is devastated and desperate.", "scene": "", "reaction_to_previous": "",
                "evidence": ["she whispered"], "has_explicit_cue": True}]
        v = t.validate_emotion_items(raw, [ctx])[ctx["clip_id"]]
        self.assertEqual(v["status"], "DISCARDED")
        self.assertTrue(any(r.startswith("intensity_word") for r in v["discard_reasons"]))
        self.assertEqual(v["state"], "")
        mild = [{"clip_id": ctx["clip_id"], "speaker_state": "Della is quietly hopeful.", "scene": "", "reaction_to_previous": "", "evidence": ["she whispered"], "has_explicit_cue": True}]
        self.assertEqual(t.validate_emotion_items(mild, [ctx])[ctx["clip_id"]]["status"], "ACCEPTED")

    def test_m6_developer_rules_8_to_10_present(self):
        d = t.EMOTION_DEVELOPER
        self.assertIn("8. Use mild, plain wording", d)
        self.assertIn("9. Describe the feeling, not acting instructions", d)
        self.assertIn("10. At least one evidence quote must come from the narration", d)
        self.assertIn("despair, devastated, terrified", d)

    def test_m6_review_gate_blocks_until_decided(self):
        d = "er118_output/_unit_review_tmp/llm"
        try:
            t.save_json(f"{d}/emotion_notes.json", {"validated": {"a": {"state": "s", "scene": "x", "reaction": "", "status": "ACCEPTED"}}})
            with self.assertRaises(SystemExit):
                t.load_reviewed_notes(f"{d}/emotion_notes.json", f"{d}/emotion_review.json")      # reviewファイル無し
            t.save_json(f"{d}/emotion_review.json", {"items": {"a": {"fable_decision": None}}})
            with self.assertRaises(SystemExit):
                t.load_reviewed_notes(f"{d}/emotion_notes.json", f"{d}/emotion_review.json")      # 未決
            t.save_json(f"{d}/emotion_review.json", {"items": {"a": {"fable_decision": "discard"}}})
            n = t.load_reviewed_notes(f"{d}/emotion_notes.json", f"{d}/emotion_review.json")
            self.assertEqual((n["a"]["state"], n["a"]["scene"]), ("", ""))
            t.save_json(f"{d}/emotion_review.json", {"items": {"a": {"fable_decision": "accept"}}})
            self.assertEqual(t.load_reviewed_notes(f"{d}/emotion_notes.json", f"{d}/emotion_review.json")["a"]["state"], "s")
        finally:
            shutil.rmtree(os.path.join(t.ROOT, "er118_output/_unit_review_tmp"), ignore_errors=True)

    def test_r1_session_order(self):
        self.assertEqual(t.SESSION_ORDER, (("ctx", 1), ("base", 1), ("ctx", 2)))


class R2FinalEquivalentTests(unittest.TestCase):
    def test_final_equiv_duration_ratio_is_1_over_1_06(self):
        import soundfile as sf
        d = "er118_output/_unit_fe_tmp"
        try:
            os.makedirs(os.path.join(t.ROOT, d), exist_ok=True)
            sf.write(os.path.join(t.ROOT, d, "a.wav"), (np.sin(np.arange(48000) / 20) * 0.1).astype("float32"), 24000)
            info = t.make_final_equivalent(f"{d}/a.wav", f"{d}/a_fe.wav")
            self.assertAlmostEqual(info["dst_duration_seconds"] / info["src_duration_seconds"], 1 / 1.06, delta=0.01)
        finally:
            shutil.rmtree(os.path.join(t.ROOT, d), ignore_errors=True)


class EvaluateTests(unittest.TestCase):
    def _clips(self, ctx_vals, ref_vals):
        def row(v):
            return {"rms_dbfs": v, "rms_lin": 10 ** (v / 20), "duration_s": 3.0, "articulation_wpm_300": 150.0, "f0": {"median_hz": 200.0, "range_semitones_p10_p90": 5.0}}
        return {"full_story_part2_c7": {"existing_A": row(ref_vals[0]), "base_t1": row(ref_vals[1]), "ctx_t1": row(ctx_vals[0]), "ctx_t2": row(ctx_vals[1])}}

    def test_complete_separation_forward_and_reverse(self):
        e = t.evaluate_trial(self._clips([-30.0, -31.0], [-24.0, -25.0]), 10.0)["separation"]["full_story_part2_c7"]
        self.assertTrue(e["forward"])
        self.assertFalse(e["reverse"])
        e2 = t.evaluate_trial(self._clips([-20.0, -21.0], [-24.0, -25.0]), 10.0)["separation"]["full_story_part2_c7"]
        self.assertFalse(e2["forward"])
        self.assertTrue(e2["reverse"])                 # 逆向きの完全分離も記録
        e3 = t.evaluate_trial(self._clips([-30.0, -24.5], [-24.0, -25.0]), 10.0)["separation"]["full_story_part2_c7"]
        self.assertFalse(e3["forward"] or e3["reverse"])

    def test_verdict_thresholds(self):
        ev = t.evaluate_trial(self._clips([-30.0, -31.0], [-24.0, -25.0]), 10.0)
        self.assertEqual(ev["d_verdict_mechanical"], "no_effect_mechanical")      # 方向あり1件のみ分離(<=1)

    def test_status_candidate_requires_conditions(self):
        ev = t.evaluate_trial(self._clips([-30.0, -31.0], [-24.0, -25.0]), 99.0)
        self.assertFalse(ev["conditions_abcefg"]["g_cost_within_cap"])
        self.assertTrue(ev["status_candidate"].startswith("REJECTED"))


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

    def setUp(self):
        # 実GO(PHASE1_GO.json)を触らないよう、GOファイル位置・出力先をtest専用の空dirへ向ける(DefaultOffIsolation: GO無し状態を再現)
        self._go, self._out = t.PHASE1_GO_FILE, t.OUT_DIR
        t.OUT_DIR = "er118_output/_unit_guard_tmp"
        t.PHASE1_GO_FILE = f"{t.OUT_DIR}/PHASE1_GO.json"
        shutil.rmtree(os.path.join(t.ROOT, t.OUT_DIR), ignore_errors=True)
        os.makedirs(os.path.join(t.ROOT, t.OUT_DIR), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(os.path.join(t.ROOT, t.OUT_DIR), ignore_errors=True)
        t.PHASE1_GO_FILE, t.OUT_DIR = self._go, self._out

    def test_no_go_file_blocks_gen_and_llm(self):
        self.assertFalse(os.path.exists(os.path.join(t.ROOT, t.PHASE1_GO_FILE)))
        before = self._listing()
        with self.assertRaises(SystemExit):
            t.generate_arm("ctx", 1)
        with self.assertRaises(SystemExit):
            t.generate_arm("base", 1)
        with self.assertRaises(SystemExit):
            t.run_emotion_llm()
        with self.assertRaises(SystemExit):
            t.run_session()
        self.assertEqual(before, self._listing())
        self.assertFalse(os.path.exists(os.path.join(t.ROOT, t.OUT_DIR, "raw_usage_log.jsonl")))

    def test_cap_over_30_rejected(self):
        p = os.path.join(t.ROOT, t.PHASE1_GO_FILE)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump({"managed_id": t.MANAGED_ID, "cap_jpy": 31, "arms": ["ctx"]}, f)
        with self.assertRaises(SystemExit):
            t._require_go()


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


    def test_m5_ng_clip_does_not_abort_remaining_clips(self):
        import soundfile as sf
        calls = []

        def gen(text, out_path, voice, **kw):
            calls.append(text)
            sf.write(out_path, (np.sin(np.arange(24000) / 20) * 0.1).astype("float32"), 24000)
            if len(calls) == 2:
                return {"status": "STOPPED", "reason": "x", "attempts_log": [{"attempt": 1, "status": "OK", "asr_text": "bad"}]}
            return {"status": "OK", "asr_text": text.strip('"'), "instruction_type": "english_style_prefix_wide_margin",
                    "attempts_log": [{"attempt": 1, "status": "OK", "asr_text": text.strip('"')}]}
        r = t.generate_arm("base", 1, gen_fn=gen)
        self.assertEqual(len(calls), 8)                     # NGの後も全8件を実行
        self.assertEqual(sum(1 for v in r.values() if v["status"] != "OK"), 1)
        bad = [v for v in r.values() if v["status"] != "OK"][0]
        self.assertFalse(bad["comparison_valid"])
        self.assertIn("leakage", bad)
        self.assertIn("attempts_asr_texts", bad)

    def test_analyze_all_end_to_end_with_fake_generation(self):
        t.build_phase0_artifacts()
        t.generate_arm("base", 1, gen_fn=self._fake([]))
        t.generate_arm("ctx", 1, gen_fn=self._fake([]))
        t.generate_arm("ctx", 2, gen_fn=self._fake([]))
        page = "er118_output/_unit_page_tmp2"
        try:
            a = t.analyze_all(out_dir=t.OUT_DIR, page_dir=page)
            self.assertEqual(a["arms"], ["base_t1", "ctx_t1", "ctx_t2"])
            row = a["clips"]["full_story_part2_c7"]
            self.assertTrue(row["ctx_t1"]["verbatim"]["token_equal"])
            self.assertFalse(row["ctx_t1"]["leakage"]["leakage_final"])
            self.assertTrue(os.path.isfile(os.path.join(t.ROOT, page, "audio", "ctx_t1_full_story_part2_c7.mp3")))
            with open(os.path.join(t.ROOT, page, "index.html"), encoding="utf-8") as f:
                doc = f.read()
            self.assertIn("A' 現行方式の別take", doc)
            self.assertIn("音量の大小ではなく", doc)
            self.assertEqual(doc.count("未生成"), 0)
        finally:
            shutil.rmtree(os.path.join(t.ROOT, page), ignore_errors=True)


class MeasureAndPageTests(unittest.TestCase):
    def test_f0_on_tone(self):
        x = np.sin(2 * np.pi * 200 * np.arange(24000) / 24000) * 0.3
        f = t.f0_stats(x, 24000)
        self.assertAlmostEqual(f["median_hz"], 200, delta=8)

    def test_page_has_noindex_and_no_dummy_audio_for_missing_arm(self):
        saved_out = t.OUT_DIR
        t.OUT_DIR = "er118_output/_unit_page_phase0_tmp"      # Round 1の実phase0を書換えない(Round 2で existing_audio_record にkeyを追加したため隔離)
        t.build_phase0_artifacts()
        sel = t.load_json(f"{t.OUT_DIR}/phase0/selection.json")
        tmp = "er118_output/_unit_page_tmp"
        try:
            ap = t.build_page(sel, {"base": {sel[0]["id"]: "audio/A.mp3"}, "ctx": {}}, out_dir=tmp)
            with open(ap, encoding="utf-8") as f:
                doc = f.read()
            self.assertIn("noindex", doc)
            self.assertEqual(doc.count("<audio"), 1)
            self.assertEqual(doc.count("未生成"), 31)    # 8*4 - 1
        finally:
            shutil.rmtree(os.path.join(t.ROOT, tmp), ignore_errors=True)
            shutil.rmtree(os.path.join(t.ROOT, t.OUT_DIR), ignore_errors=True)
            t.OUT_DIR = saved_out


class Round2ConfigTests(unittest.TestCase):
    """委任_04(Round 2): 作品/level/出力dirのパラメータ化。API 0。Round 1(magi)の挙動が不変であることと、新2作品の選定規則・隔離・費用ガードを検証する。"""
    WORKS2 = ("open_window", "monkeys_paw")

    def tearDown(self):
        t.configure("magi")

    def test_default_is_round1_magi_and_prompt_sha_unchanged(self):
        t.configure("magi")
        self.assertEqual(t.WORK_KEY, "magi")
        self.assertEqual(t.OUT_DIR, "er118_output/fz_dialogue_context_tts_trial_01")
        self.assertEqual(t.PHASE1_GO_FILE, "er118_output/fz_dialogue_context_tts_trial_01/PHASE1_GO.json")
        self.assertEqual(t.COST_LOG, "er118_output/fz_dialogue_context_tts_trial_01/raw_usage_log.jsonl")
        self.assertEqual(t.sha_text(t.EMOTION_DEVELOPER), "035b54ff44b28d645e831cd0266c47fd2691f0268d606de0a0bea3d6ecd39cab")
        self.assertEqual(t.emotion_prompt_sha(), "8bc8c816d5187ff060c438bce09b03e21492c7e44806241763631e55db291dce")
        self.assertEqual(len(t.TARGETS), 8)

    def test_round2_selection_rules(self):
        for w in self.WORKS2:
            t.configure(w)
            plan = t.load_plan()
            cl = {c["id"]: c for c in plan["clips"]}
            order = [c["id"] for c in plan["clips"]]
            ids = t.TARGET_IDS
            self.assertEqual(len(ids), 8, w)
            self.assertEqual(len(set(ids)), 8, w)
            self.assertEqual(ids, sorted(ids, key=order.index), f"{w}: plan順")
            for cid in ids:
                self.assertTrue(cl[cid]["voice_role"].startswith("dialogue:"), cid)
            words = [t.n_words(cl[c]["text"]) for c in ids]
            self.assertLessEqual(sum(1 for x in words if x <= 2), 1, f"{w}: 2語以下は1件以下")
            self.assertGreaterEqual(sum(1 for x in words if x >= 4), 6, f"{w}: 4語以上が主体")
            roles = [x["role"] for x in t.TARGETS]
            self.assertEqual((roles.count("directional"), roles.count("watch"), roles.count("stability")), (5, 2, 1), w)
            self.assertEqual(len(t.PRIMARY_METRICS), 5)
            self.assertEqual(len(t.OVERACT_WATCH), 2)
            self.assertIn(t.STABILITY_WATCH, ids)
            self.assertGreaterEqual(words[ids.index(t.STABILITY_WATCH)], 6, "安定監視clipは6語以上(Round 1で2語clipが不成立だった教訓)")
            for cid, (metric, direction) in t.PRIMARY_METRICS.items():
                self.assertIn(metric, ("rms_dbfs", "articulation_wpm_300", "f0_median_hz"))
                self.assertIn(direction, ("up", "down"))
            self.assertIn(t.EXAMPLE_CLIP_ID, ids)

    def test_round2_existing_audio_reusable_api0(self):
        for w in self.WORKS2:
            t.configure(w)
            for cid in t.TARGET_IDS:
                r = t.existing_audio_record(cid)
                self.assertTrue(os.path.isfile(os.path.join(t.ROOT, r["original_wav"])), cid)
                self.assertTrue(os.path.isfile(os.path.join(t.ROOT, r["final_wav"])), cid)
                self.assertEqual(r["tts_execution_mode"], "STANDARD")
                self.assertEqual(r["tts_model_id"], t.TTS_MODEL)
                self.assertEqual(r["asr_state"], "PASS", cid)
                self.assertIsNotNone(r["original_attempt_index"], f"{cid}: 採用原音がどのattemptかを特定できる")
                self.assertEqual(r["style_effective_sha256"], t.EXPECTED_BASE_STYLE_SHA)
                clip = {c["id"]: c for c in t.load_plan()["clips"]}[cid]
                self.assertEqual(t.tts_voice(clip), r["voice"], "②のVoice(voice_assignment)は①の実生成Voiceと同一")

    def test_round2_style_and_context_invariants(self):
        for w in self.WORKS2:
            t.configure(w)
            plan = t.load_plan()
            cl = {c["id"]: c for c in plan["clips"]}
            plan_text = " ".join(c["text"] for c in plan["clips"])
            self.assertEqual(t.sha_text(t.base_style()), t.EXPECTED_BASE_STYLE_SHA)
            for cid in t.TARGET_IDS:
                clip, ctx = cl[cid], t.extract_context(plan, cid)
                note = {"state": "quietly worried.", "scene": "At home.", "reaction": ""}
                b = t.build_prompt(t.tts_text_for(clip), t.style_for_arm("base", ctx, None))
                c = t.build_prompt(t.tts_text_for(clip), t.style_for_arm("ctx", ctx, note))
                self.assertEqual(text_section(b), text_section(c), "TEXT TO SPEAK区画は①②で同一")
                self.assertTrue(style_section(c).startswith(style_section(b).rstrip()))
                self.assertNotIn(clip["text"], t.build_context_block(ctx, note), cid)
                self.assertLessEqual(len(ctx["prev_dialogue"]), 2)
                self.assertLessEqual(len(ctx["next_dialogue"]), 1)
                for s in ctx["stage_direction_sentences"] + [ctx["narration_before"], ctx["narration_after"]] + [d["text"] for d in ctx["prev_dialogue"] + ctx["next_dialogue"]]:
                    if s:
                        self.assertIn(s.strip(), plan_text)

    def test_round2_cap_and_cost_log_shared_across_works(self):
        t.configure("open_window")
        go_a, log_a, out_a = t.PHASE1_GO_FILE, t.COST_LOG, t.OUT_DIR
        t.configure("monkeys_paw")
        self.assertEqual((t.PHASE1_GO_FILE, t.COST_LOG), (go_a, log_a), "30円Capとcost logは2作品で共有")
        self.assertNotEqual(t.OUT_DIR, out_a)
        self.assertTrue(go_a.startswith("er118_output/fz_dialogue_context_tts_trial_02/"))
        self.assertNotEqual(go_a, "er118_output/fz_dialogue_context_tts_trial_01/PHASE1_GO.json", "Round 1の出力・GOと分離")
        self.assertEqual(t.TRIAL_CAP_JPY, 30.0)

    def test_round2_go_cap_over_30_rejected_and_tts_arms_blocked_without_go_scope(self):
        t.configure("open_window")
        saved = t.PHASE1_GO_FILE
        t.PHASE1_GO_FILE = "er118_output/_unit_r2_go_tmp/PHASE1_GO.json"
        try:
            p = os.path.join(t.ROOT, t.PHASE1_GO_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                json.dump({"managed_id": t.MANAGED_ID, "cap_jpy": 31, "arms": ["ctx"]}, f)
            with self.assertRaises(SystemExit):
                t._require_go()
            with open(p, "w") as f:
                json.dump({"managed_id": t.MANAGED_ID, "cap_jpy": 30, "arms": []}, f)
            with self.assertRaises(SystemExit):
                t.generate_arm("ctx", 1)       # armsが許可されていない(Phase 1aのGO=TTS arm無し)ならTTS生成は起動しない
            with self.assertRaises(SystemExit):
                t.generate_arm("base", 1)
        finally:
            t.PHASE1_GO_FILE = saved
            shutil.rmtree(os.path.join(t.ROOT, "er118_output/_unit_r2_go_tmp"), ignore_errors=True)
    def test_round2_cap_lookahead_stops_before_exceeding_without_api(self):
        """Round 2追加のCap先読み: 実績+次clip見積>Capなら、API呼出前にSTOP(clip未生成)。TTS/LLMは呼ばない。"""
        import er019_family_x_audio_production_runner_01 as runner
        t.configure("monkeys_paw")
        self.assertGreater(t.est_next_clip_jpy("x" * 3000, t.TARGET_IDS[0]), 0.1)
        saved = (t.PHASE1_GO_FILE, t.COST_LOG, t.OUT_DIR, runner.compute_cost_jpy_so_far)
        tmp = "er118_output/_unit_r2_cap_tmp"
        try:
            t.OUT_DIR, t.PHASE1_GO_FILE, t.COST_LOG = tmp, f"{tmp}/PHASE1_GO.json", f"{tmp}/raw_usage_log.jsonl"
            os.makedirs(os.path.join(t.ROOT, tmp), exist_ok=True)
            with open(os.path.join(t.ROOT, t.PHASE1_GO_FILE), "w") as f:
                json.dump({"managed_id": t.MANAGED_ID, "cap_jpy": 30, "arms": ["base"]}, f)
            runner.compute_cost_jpy_so_far = lambda _p: (29.9, {})
            with self.assertRaises(SystemExit) as cm:
                t.generate_arm("base", 1)
            self.assertIn("Cap", str(cm.exception))
            self.assertFalse(os.path.exists(os.path.join(t.ROOT, tmp, "gen")) and any(
                f.endswith(".wav") for _d, _s, fs in os.walk(os.path.join(t.ROOT, tmp, "gen")) for f in fs), "wav未生成")
        finally:
            t.PHASE1_GO_FILE, t.COST_LOG, t.OUT_DIR, runner.compute_cost_jpy_so_far = saved
            shutil.rmtree(os.path.join(t.ROOT, tmp), ignore_errors=True)


    def test_round2_emotion_prompt_only_title_differs(self):
        t.configure("magi")
        base = t.EMOTION_DEVELOPER
        for w in self.WORKS2:
            t.configure(w)
            self.assertIn(t.WORK_TITLE, t.EMOTION_DEVELOPER)
            self.assertNotIn("Gift of the Magi", t.EMOTION_DEVELOPER)
            self.assertEqual(t.EMOTION_DEVELOPER.replace(t.WORK_TITLE, "The Gift of the Magi"), base, "作品名以外のrule 1〜10は無変更")
            self.assertEqual(t.EMOTION_SCHEMA["name"], "dialogue_delivery_notes")

    def test_round2_speaker_names_allowed_in_emotion_validation(self):
        t.configure("open_window")
        plan = t.load_plan()
        ctx = t.extract_context(plan, "full_story_part1_c14")
        raw = [{"clip_id": ctx["clip_id"], "speaker_state": "quietly sad, as Vera tells Framton about the lawn", "scene": "Vera speaks softly to Framton.",
                "reaction_to_previous": "", "evidence": ["Vera's voice grew quieter."], "has_explicit_cue": True}]
        v = t.validate_emotion_items(raw, [ctx])[ctx["clip_id"]]
        self.assertEqual(v["status"], "ACCEPTED", v["discard_reasons"])
        raw[0]["scene"] = "Vera speaks softly to Gertrude."
        v2 = t.validate_emotion_items(raw, [ctx])[ctx["clip_id"]]
        self.assertEqual(v2["status"], "DISCARDED")      # 入力に無い固有名詞は従来どおり破棄

    def test_round2_combined_page(self):
        tmp = "er118_output/_unit_combined_page_tmp"
        try:
            for w in self.WORKS2:
                t.configure(w)
                t.build_phase0_artifacts()
            ap = t.build_combined_page(page_root=tmp)
            with open(ap, encoding="utf-8") as f:
                doc = f.read()
            self.assertIn("noindex", doc)
            n_audio = 0     # 音声はpage_manifest.jsonに載ったpathだけ(未生成armにダミー音声を置かない)
            for w in self.WORKS2:
                t.configure(w)
                mp = os.path.join(t.ROOT, t.OUT_DIR, "page_manifest.json")
                if os.path.exists(mp):
                    man = t.load_json(f"{t.OUT_DIR}/page_manifest.json")
                    n_audio += sum(len(v) for v in list(man["pages"].values()) + list(man["extra"].values()))
            self.assertEqual(doc.count("<audio"), n_audio)
            self.assertEqual(doc.count("class='card'"), 16)
            self.assertEqual(doc.count("未生成"), 16 * 4 - n_audio)
            self.assertIn("../fz_dialogue_context_trial_01/index.html", doc)      # 前回『賢者の贈り物』ページへのリンク
            self.assertIn("Production採用ではありません", doc)
            self.assertIn("B 改善方式", doc)
            self.assertIn("A' 現行方式の別take", doc)
            self.assertIn("音量の大小ではなく", doc)
            self.assertIn("前後の会話・地の文", doc)
        finally:
            shutil.rmtree(os.path.join(t.ROOT, tmp), ignore_errors=True)

    def test_round2_single_page_links_and_title(self):
        t.configure("monkeys_paw")
        t.build_phase0_artifacts()
        sel = t.load_json(f"{t.OUT_DIR}/phase0/selection.json")
        tmp = "er118_output/_unit_single_page_tmp"
        try:
            ap = t.build_page(sel, {"base": {}, "ctx": {}}, out_dir=tmp)
            with open(ap, encoding="utf-8") as f:
                doc = f.read()
            self.assertIn("猿の手", doc)
            self.assertIn("../fz_dialogue_context_trial_01/index.html", doc)
            self.assertNotIn("賢者の贈り物』セリフ音声", doc)
        finally:
            shutil.rmtree(os.path.join(t.ROOT, tmp), ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
