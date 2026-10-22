# -*- coding: utf-8 -*-
"""er063_family_z_audio_01 のオフラインtest(mock TTS/ASR、課金0、実API呼出なし)。
実行: .venv/Scripts/python.exe -m unittest er063_family_z_audio_01_test_01 -v"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import unittest
from unittest import mock

import numpy as np

import er002_common as common
import er062_family_z_structure_01 as zst
import er063_family_z_audio_01 as z

SR = common.SAMPLE_RATE


def _write_tone(path: str, seconds: float = 1.0, amp: float = 0.2) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    t = np.arange(int(SR * seconds)) / SR
    common.write_wav_float(path, (amp * np.sin(2 * np.pi * 220 * t)).astype("float32"), SR, 1)


def _sha_or_none(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def make_plan(level: str, n_story: int = 4):
    story = [
        {"id": "full_story_part1_c1", "voice": "narrator", "text": "Melos was angry."},
        {"id": "full_story_part1_c2", "voice": "dionysius", "text": '"You will fail," said the king.'},
        {"id": "full_story_part2_c1", "voice": "narrator", "text": "He ran through the night."},
        {"id": "full_story_part3_c1", "voice": "melos", "text": '"I am here," said Melos.'},
    ][:n_story]
    kp = [{"rank": 1, "used_form": "run through", "japanese_gloss": "走り抜ける", "japanese_gloss_tts": "走り抜ける"}]
    comments = {1: "c1 text", 2: "c2 text", 3: "c3 text"}
    plan = z.build_level_plan(level, story, "preview text", comments, kp, "The Three-Day Promise",
                              "走れメロス" if level == "a2" else None)
    return plan, story, kp


def fake_generators(slow_std: bool = True, lr_clips=(), fail_clips=()):
    def make(kind):
        def fn(spec, out_path):
            if spec.clip_id in fail_clips:
                return {"status": "STOPPED", "reason": "x"}
            _write_tone(out_path, 1.06)
            r = {"status": "OK", "asr_text": spec.text, "disfluency_checked": True, "text": spec.text,
                 "standard_attempts_log": [{"attempt": 1, "instruction_type": "english_style_prefix_wide_margin",
                                            "style_prefix": {"sha256": "ab" * 32, "head200": "x"},
                                            "tts_model_id": "gemini-3.8-flash-lite-tts", "voice": spec.voice}]}
            if spec.clip_id in lr_clips:
                r["canonical_text_before_local_rewrite"] = spec.text
                r["local_rewrite_recovery"] = {"selection": {"selected": {"rewritten_segment": spec.text + " indeed"}}}
                r["cooldown_events"] = [{"cooldown_actual_seconds": 600.0}]
            if spec.kind == "kp_en":
                # KPDUAL-PROD-D2(UDR #139): KP英語phraseは実strictが両Provider PASSの監査record(asr_judgement.dual)を返す。
                # 前回results再利用(generate_or_reuse_z)はこの証跡を要する(fail-closed)ため、fakeも同形のrecordを返す。
                _t = z._norm_for_tts(spec)
                r["asr_judgement"] = {"state": "PASS", "reason_code": "dual_agreed", "dual": {
                    "required": True, "primary_provider": "openai", "secondary_provider": "azure", "primary_pass": True,
                    "primary_text": _t, "primary_rescued_by_secondary": False, "primary_rescue_layers": [],
                    "secondary_called": True, "secondary_pass": True, "secondary_text": _t, "outcome": "PASS"}}
            if spec.level == "a2" and z._CLIP_ID_RE.fullmatch(spec.clip_id) and slow_std:
                _write_tone(out_path.replace(".wav", "_original.wav"), 1.0)
                r["slowdown_applied"] = True
                r["slowdown_info"] = {"src_duration_seconds": 1.0, "dst_duration_seconds": 1.06}
            return r
        return fn
    return {k: make(k) for k in ("narrator", "dialogue", "topic_intro", "preview", "comment", "japanese_title", "kp_en", "kp_ja")}


class StyleTableTest(unittest.TestCase):
    def test_integrity_and_pins(self):
        rep = z.assert_style_table_integrity()
        # 2026-10-17 委任_15: 期待値を意図的に更新(旧: PD8/R2/M2、承認変更 N01->PD06 / R2->S3 / M2->P8-KP)。
        self.assertEqual(rep["PD06"], "3a680861e4d9d1bc46ddba4dc1fc91f26c68f9f9c5e5e450a85fcba7fda43c2d")
        self.assertEqual(rep["S3"], "060c08fde003cf7c2d15c654da96d3f857b8e7a9bd79eac31814ceaf7c923f33")
        self.assertEqual(rep["P8_KP"], "b12c8721eab8434b78d129c93491c0a826f229f4528e024d58de960e1ad191e7")
        self.assertEqual(rep["P7"], "0518000694e31ef7de6602401b7fa9abd3beb45654e95714817930582020b9fc")

    def test_origin_verbatim(self):
        if not os.path.exists("er057_output/pace_trial_02/prompts/prompts_pace_02.md"):
            self.skipTest("origin files absent")
        rep = z.verify_styles_against_origin(".")
        for k, v in rep.items():
            self.assertTrue(v["verbatim_match"], k)

    def test_std_narrator_is_pd06_verbatim_without_a2_instruction(self):
        # 2026-10-17 委任_15: 期待値を意図的に更新(旧: N01[2026-10-13]。ユーザー承認§2B: Narrator=PD06)。Std/Adv とも逐語(Std減速instruction非連結)。
        import er003_v1_n3_01_tts_generate as n3
        self.assertEqual(z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_STD"]["text"], z._STYLE_TEXT["PD06"])
        self.assertEqual(z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_ADV"]["text"], z._STYLE_TEXT["PD06"])
        self.assertNotIn(n3.A2_SLOWER_PACE_INSTRUCTION.strip(), z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_STD"]["text"])

    def test_x_constants_untouched_and_copies_match(self):
        import er033_tts_flash_lite_family_x_styles_01 as fl
        self.assertEqual(fl.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"], z._X_TOPIC_INTRO)
        self.assertEqual(fl.FAMILY_X_ROLE_STYLE_JA, z._X_JA_J3)
        self.assertEqual(fl.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0], "natural, clear, conversational")

    def test_std_dialogue_style_text_none_same_as_adv_and_label(self):
        # 2026-10-19 ③: Std/Adv Dialogueとも style_text_for=None。ラベルに旧SLOWERを含まない。
        sa = [s for s in make_plan("a2")[0] if s.kind == "dialogue"]
        sb = [s for s in make_plan("b1b")[0] if s.kind == "dialogue"]
        self.assertTrue(sa and sb)
        for s in sa + sb:
            self.assertIsNone(z.style_text_for(s), s.clip_id)
        std = z.FAMILY_Z_ROLE_STYLE["DIALOGUE_STD"]
        self.assertIsNone(std["text"])
        self.assertNotIn("SLOWER", std["style_label"] + std["origin"])
        # 共通Style対象外(EXCEPTION)のまま
        self.assertTrue(z.CROSS_FAMILY_COMMON_STYLE_MAP["DIALOGUE_STD"]["Z"].startswith("EXCEPTION"))
        # Std Dialogueのreuse_key style shaはAdvと同値(None由来)、他roleは従前どおりROLE_STYLE textのsha
        self.assertEqual(z.build_reuse_key(sa[0])["style_prefix_sha256"], z.build_reuse_key(sb[0])["style_prefix_sha256"])
        for lvl in ("a2", "b1b"):
            for s in make_plan(lvl)[0]:
                if s.kind != "dialogue":
                    self.assertEqual(z.build_reuse_key(s)["style_prefix_sha256"],
                                     z.style_prefix_sha256(z.FAMILY_Z_ROLE_STYLE[s.role_key]["text"]), s.clip_id)

    def test_effective_style_sha_std_dialogue_equals_adv_default(self):
        import er003_b1_p9a_audio as p9a
        sa = [s for s in make_plan("a2")[0] if s.kind == "dialogue"][0]
        self.assertEqual(z._effective_style_sha(sa, z.style_text_for(sa)), z.style_prefix_sha256(p9a.ENGLISH_STYLE_PREFIX))

    def test_no_a2_slower_prefix_remains_in_family_z_audio_module(self):
        import inspect
        self.assertNotIn("A2_ENGLISH_STYLE_PREFIX_SLOWER", inspect.getsource(z))
        # 共有定数自体は他Family用に残置
        import er003_v1_n3_01_tts_generate as n3
        self.assertTrue(hasattr(n3, "A2_ENGLISH_STYLE_PREFIX_SLOWER"))

    def test_narrator_style_not_mixed_into_dialogue(self):
        for lvl in ("a2", "b1b"):
            plan, _, _ = make_plan(lvl)
            for s in plan:
                st = z.style_text_for(s)
                if s.kind == "dialogue":
                    self.assertTrue(st is None or z._STYLE_TEXT["PD06"] not in st, s.clip_id)
                if s.kind in ("preview", "comment", "kp_en", "kp_ja", "topic_intro"):
                    self.assertTrue(st is None or z._STYLE_TEXT["PD06"] not in st)
        adv_d = [s for s in make_plan("b1b")[0] if s.kind == "dialogue"][0]
        self.assertIsNone(z.style_text_for(adv_d))  # style_prefix_overrideを渡さない
        std_d = [s for s in make_plan("a2")[0] if s.kind == "dialogue"][0]
        self.assertIsNone(z.style_text_for(std_d))  # 2026-10-19 決定③: Stdも既定Dialogue Style(Advと同一)

    def test_role_style_assignment(self):
        std, _, _ = make_plan("a2")
        adv, _, _ = make_plan("b1b")
        sty = lambda plan, cid: next(z.FAMILY_Z_ROLE_STYLE[s.role_key]["style_label"] for s in plan if s.clip_id == cid)
        self.assertEqual(sty(std, "preview"), "S3")   # 2026-10-17 委任_15: R2->S3(ユーザー承認§2B)
        self.assertEqual(sty(std, "comment_2"), "S3")
        self.assertEqual(sty(adv, "preview"), "E1")
        self.assertEqual(sty(adv, "comment_1"), "E2_UPBEAT")
        self.assertEqual(sty(adv, "kp1_en"), "K2")
        self.assertEqual(sty(adv, "kp1_ja"), "P8_KP")   # 2026-10-17 委任_15: M2->P8-KP


class DialogueVoiceTest(unittest.TestCase):
    def test_melos_routes_with_config_only(self):
        r = z.check_melos_voice_mechanism()
        self.assertTrue(r["melos_quote_routed"])
        self.assertEqual(r["melos_voice"], "Algieba")
        self.assertEqual(z.MELOS_VOICE_STATUS, "PROVISIONAL_UNAPPROVED")

    def test_registry_lacked_melos_key(self):
        import er026_family_z_fiction_production_runner_01 as r26
        self.assertNotIn("melos", r26.STORY_REGISTRY["melos"]["voice_tts_names_plan"])  # 追加は後続のer026統合

    def test_er062_speaker_vocabulary_maps(self):
        self.assertEqual(z.normalize_speaker("dialogue:king"), "dionysius")
        self.assertEqual(z.normalize_speaker("friend"), "selinuntius")
        self.assertEqual(z.normalize_speaker("dialogue:melos"), "melos")
        with self.assertRaises(z.FamilyZVoiceMappingStop):
            z.normalize_speaker("dialogue:other")
        plan = z.build_level_plan("b1b", [{"id": "full_story_part1_c1", "speaker": "king", "voice_role": "dialogue:king", "text": "x"}],
                                  "p", {1: "a", 2: "b", 3: "c"}, [], "T")
        self.assertEqual([s.voice for s in plan if s.kind == "dialogue"], ["Charon"])

    def test_unknown_speaker_stops(self):
        with self.assertRaises(z.FamilyZVoiceMappingStop):
            z.resolve_dialogue_voice("stranger")

    def test_attribution_agree(self):
        paras = ['"I will return," Melos told the king.']
        out = z.assert_dialogue_attribution(paras, lambda qs: {q["quote_id"]: "melos" for q in qs})
        self.assertEqual(out["p0_q0"], "melos")  # 王に誤割当されない

    def test_attribution_mismatch_stops_and_records(self):
        paras = ['"I am here," he said to his friend.']  # 決定論=selinuntius(friend言及)、実際はMelos
        d = tempfile.mkdtemp()
        try:
            with self.assertRaises(z.FamilyZDialogueAttributionStop):
                z.assert_dialogue_attribution(paras, lambda qs: {q["quote_id"]: "melos" for q in qs}, out_dir=d, level="a2")
            ov = json.load(open(f"{d}/dialogue_override_a2.json", encoding="utf-8"))
            self.assertEqual(ov["mismatches"][0]["deterministic_voice"], "selinuntius")
            self.assertEqual(ov["mismatches"][0]["llm_voice"], "melos")
        finally:
            shutil.rmtree(d)

    def test_mention_only_word_mismatch(self):
        paras = ['Dionysius watched him closely. "Go now," he said.']
        qs = z.extract_quotes(paras)
        self.assertEqual(qs[0]["deterministic_voice"], "dionysius")  # 言及だけで王に誤割当(決定論の既知弱点)
        with self.assertRaises(z.FamilyZDialogueAttributionStop):
            z.assert_dialogue_attribution(paras, lambda q: {x["quote_id"]: "melos" for x in q})


class LayoutAndReuseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.run = f"{self.tmp}/melos/run_01"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_layout_valid_for_both_levels(self):
        for lvl in ("a2", "b1b"):
            p = f"{z.narration_dir_for(self.run, lvl)}/full_story_part1_c1.wav"
            self.assertTrue(z.layout_is_valid(p))
            self.assertEqual(z.derive_segment_id(p), "full_story_part1_c1")
            import er011_human_review_lock_01 as rl
            self.assertEqual(rl.derive_segment_key(p)[1], lvl)
        self.assertFalse(z.layout_is_valid(f"{self.run}/a2/audio/x.wav"))

    def test_resolve_role_for_clips(self):
        import er020_tts_retry_local_rewrite_01 as rp
        self.assertEqual(rp.resolve_narrative_role("full_story_part3_c12"), "FULL_STORY")
        self.assertIsNone(rp.resolve_narrative_role("full_story_part1_c1_original"))

    def test_reuse_key_elements(self):
        plan, _, _ = make_plan("b1b")
        spec = plan[-1]
        wav = f"{self.run}/b1b/narration/{spec.wav_name()}"
        calls = []

        def gen():
            calls.append(1)
            _write_tone(wav)
            return z.build_entry(spec, wav, {"status": "OK", "asr_text": "x"})

        e1 = z.generate_or_reuse_z(None, spec, wav, gen)
        self.assertEqual(len(calls), 1)
        e2 = z.generate_or_reuse_z(e1, spec, wav, gen)
        self.assertTrue(e2.get("reused_from_previous_run"))
        self.assertEqual(len(calls), 1)
        for mutate in ("text", "voice", "version", "backend", "style"):
            c2 = dict(e1)
            rk = dict(e1["reuse_key"])
            if mutate == "text":
                rk["canonical_text_sha256"] = "0" * 64
            elif mutate == "voice":
                rk["voice"] = "Other"
            elif mutate == "version":
                rk["role_style_version"] = "other"
            elif mutate == "backend":
                rk["tts_backend"] = "legacy"
            else:
                rk["style_prefix_sha256"] = "1" * 64
            c2["reuse_key"] = rk
            n = len(calls)
            z.generate_or_reuse_z(c2, spec, wav, gen)
            self.assertEqual(len(calls), n + 1, mutate)

    def test_x_version_does_not_affect_reuse(self):
        import er019_family_x_audio_production_runner_01 as x
        plan, _, _ = make_plan("b1b")
        spec = plan[0]
        wav = f"{self.run}/b1b/narration/{spec.wav_name()}"
        _write_tone(wav)
        e = z.build_entry(spec, wav, {"status": "OK"})
        with mock.patch.object(x, "FAMILY_X_VARIABLE_ROLE_STYLE_VERSION", "changed"):
            r = z.generate_or_reuse_z(e, spec, wav, lambda: self.fail("should reuse"))
        self.assertTrue(r["reused_from_previous_run"])

    def test_stale_file_regenerates(self):
        plan, _, _ = make_plan("b1b")
        spec = plan[0]
        wav = f"{self.run}/b1b/narration/{spec.wav_name()}"
        _write_tone(wav)
        e = z.build_entry(spec, wav, {"status": "OK"})
        _write_tone(wav, 2.0)  # 実体が変わる
        hit = []
        z.generate_or_reuse_z(e, spec, wav, lambda: hit.append(1) or e)
        self.assertEqual(hit, [1])


class StageGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.run = f"{self.tmp}/melos/run_01"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run_stage(self, level, **kw):
        plan, story, kp = make_plan(level)
        out = z.run_tts_stage(self.run, level, plan, generators=fake_generators(**kw.pop("gen", {})), **kw)
        return plan, story, kp, out

    def test_dry_run_zero_side_effects(self):
        watched = ["er006_output/master_audio_store_01/manifest.json", "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
                   "er011_output/attempt_history.jsonl", "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
                   "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
                   "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl",
                   "er030_output/kp_backend_telemetry_01/telemetry.jsonl"]
        before = {p: _sha_or_none(p) for p in watched}
        plan, _, _ = make_plan("a2")
        called = []
        gens = {k: (lambda s, p, k=k: called.append(k)) for k in ("narrator", "dialogue", "topic_intro", "preview", "comment",
                                                                   "japanese_title", "kp_en", "kp_ja")}
        out = z.run_tts_stage(self.run, "a2", plan, generators=gens, dry_run=True)
        self.assertTrue(out["dry_run"])
        self.assertEqual(out["writes"], 0)
        self.assertEqual(called, [])
        self.assertFalse(os.path.exists(self.run))
        self.assertTrue(all(r["layout_valid"] for r in out["planned"]))
        self.assertEqual({p: _sha_or_none(p) for p in watched}, before)

    def test_evidence_schema(self):
        plan, _, _, out = self._run_stage("a2")
        data = json.load(open(out["results_path"], encoding="utf-8"))
        self.assertEqual(data["style_version"], z.FAMILY_Z_ROLE_STYLE_VERSION)
        for cid in ("full_story_part1_c2", "preview", "comment_3", "topic_intro_en", "japanese_title"):
            e = data["segments"][cid]
            for k in ("status", "segment_id", "narration_path", "role", "connected_speech_enabled", "tts_backend", "voice",
                      "style", "reuse_key", "attempts", "cooldown_occurred", "audio_text_deviation", "slowdown_applied"):
                self.assertIn(k, e, (cid, k))
            self.assertIn("instruction_label", e["style"])
            self.assertIn("style_prefix_sha256", e["style"])
            self.assertEqual(e["segment_id"], cid)
            for k in ("canonical_text_sha256", "role_style_version", "voice", "style_prefix_sha256", "tts_backend"):
                self.assertIn(k, e["reuse_key"])
        self.assertEqual(data["segments"]["full_story_part1_c2"]["role"], "FULL_STORY")
        self.assertIn("1", data["key_phrases"])
        self.assertIn("english", data["key_phrases"]["1"])
        ev = json.load(open(out["evidence_path"], encoding="utf-8"))
        row = [c for c in ev["clips"] if c["clip_id"] == "full_story_part1_c2"][0]
        self.assertEqual(row["derived_segment_id"], "full_story_part1_c2")
        self.assertEqual(row["model_ids_measured"], ["gemini-3.8-flash-lite-tts"])
        self.assertEqual(row["voice"], "Charon")
        self.assertTrue(row["slowdown_applied"])
        self.assertAlmostEqual(row["slowdown_ratio"], 1.06, places=2)
        # 配置: <run>/a2/narration/<segment>.wav
        self.assertTrue(os.path.exists(f"{self.run}/a2/narration/full_story_part1_c1.wav"))

    def test_resume_reuses_second_run(self):
        plan, _, _, _ = self._run_stage("b1b")
        calls = []
        gens = {k: (lambda s, p, k=k: calls.append(k)) for k in fake_generators()}
        out2 = z.run_tts_stage(self.run, "b1b", plan, generators=gens)
        self.assertEqual(calls, [])
        self.assertTrue(all(v == "OK" for v in out2["statuses"].values()))

    def test_checkpoint_resume_after_interruption(self):
        """委任_10: 途中でprocessが中断(例外)しても、完了済みclipは再課金せず再利用し、完走後は途中経過ファイルが残らない。"""
        plan, _, _ = make_plan("b1b")
        stop_at = plan[3].clip_id
        done = []

        def boom_factory(kind):
            base = fake_generators()[kind]

            def fn(spec, out_path):
                if spec.clip_id == stop_at:
                    raise KeyboardInterrupt("simulated kill")
                done.append(spec.clip_id)
                return base(spec, out_path)
            return fn
        gens = {k: boom_factory(k) for k in fake_generators()}
        with self.assertRaises(KeyboardInterrupt):
            z.run_tts_stage(self.run, "b1b", plan, generators=gens)
        self.assertEqual(len(done), 3)
        self.assertTrue(os.path.exists(f"{self.run}/b1b/audit/tts_checkpoint.json"))
        calls = []

        def counting(kind):
            base = fake_generators()[kind]
            return lambda spec, p: (calls.append(spec.clip_id), base(spec, p))[1]
        out = z.run_tts_stage(self.run, "b1b", plan, generators={k: counting(k) for k in fake_generators()})
        self.assertEqual(len(calls), len(plan) - 3)          # 完了済み3clipは再生成しない
        self.assertNotIn(plan[0].clip_id, calls)
        self.assertTrue(all(v == "OK" for v in out["statuses"].values()))
        self.assertFalse(os.path.exists(f"{self.run}/b1b/audit/tts_checkpoint.json"))

    def test_m2_gate_passes_local_rewrite_not_required_and_lists_deviation(self):
        # 委任_12D: local_rewrite_revalidation.verdict=NOT_REQUIRED は不採択理由にしない。deviation一覧をgate出力へ載せる。
        lvl = f"{self.run}/a2"
        plan, _, _, out = self._run_stage("a2")
        ids = [s.clip_id for s in plan]
        pth = f"{lvl}/audit/tts_generation_results.json"
        data = json.load(open(pth, encoding="utf-8"))
        data["segments"]["comment_2"]["audio_text_deviation"] = {
            "canonical_text_before_local_rewrite": "Melos drank", "audio_text_after": "He drank", "diff_summary": "Melos->He"}
        data["segments"]["comment_2"]["local_rewrite_revalidation"] = {"verdict": "NOT_REQUIRED"}
        json.dump(data, open(pth, "w", encoding="utf-8"))
        r = z.assert_tts_results_complete(lvl, ids)
        self.assertEqual([d["clip_id"] for d in r["audio_text_deviations"]], ["comment_2"])
        self.assertEqual(r["audio_text_deviations"][0]["audio_text_after"], "He drank")
        self.assertEqual(r["audio_text_deviations"][0]["canonical_text_before_local_rewrite"], "Melos drank")
        # 非OK(未採択)clipは従来どおり不採択
        data["segments"]["comment_2"]["status"] = "ASR_VALIDATION_UNCERTAIN"
        json.dump(data, open(pth, "w", encoding="utf-8"))
        with self.assertRaises(z.FamilyZTtsResultsIncompleteStop):
            z.assert_tts_results_complete(lvl, ids)

    def test_m2_gate_requires_file_and_entries(self):
        lvl = f"{self.run}/a2"
        with self.assertRaises(z.FamilyZTtsResultsIncompleteStop):
            z.assert_tts_results_complete(lvl, ["preview"])  # ファイル不在
        os.makedirs(f"{lvl}/audit")
        json.dump({}, open(f"{lvl}/audit/tts_generation_results.json", "w"))
        with self.assertRaises(z.FamilyZTtsResultsIncompleteStop):
            z.assert_tts_results_complete(lvl, ["preview"])  # 空dict
        # 2026-10-17 委任_15: Style記録の無い既存結果ファイルがあるdirは課金前STOP(Opus R-C4)になったため、fixtureを撤去してから新規実行する。
        os.remove(f"{lvl}/audit/tts_generation_results.json")
        plan, _, _, out = self._run_stage("a2")
        ids = [s.clip_id for s in plan]
        z.assert_tts_results_complete(lvl, ids)
        data = json.load(open(f"{lvl}/audit/tts_generation_results.json", encoding="utf-8"))
        del data["segments"]["comment_2"]
        json.dump(data, open(f"{lvl}/audit/tts_generation_results.json", "w", encoding="utf-8"))
        with self.assertRaises(z.FamilyZTtsResultsIncompleteStop) as cm:
            z.assert_tts_results_complete(lvl, ids)
        self.assertIn("comment_2", str(cm.exception))
        # KP entry欠落
        data = json.load(open(f"{lvl}/audit/tts_generation_results.json", encoding="utf-8"))
        data["segments"]["comment_2"] = {"status": "OK"}
        data["key_phrases"] = {}
        json.dump(data, open(f"{lvl}/audit/tts_generation_results.json", "w", encoding="utf-8"))
        with self.assertRaises(z.FamilyZTtsResultsIncompleteStop):
            z.assert_tts_results_complete(lvl, ids)

    def test_m2_gate_runs_before_shared_gate(self):
        plan, _, _ = make_plan("a2")
        with mock.patch("er003_v1_n3_01_assemble.verify_episode_audio_validation_gate") as shared:
            with self.assertRaises(z.FamilyZTtsResultsIncompleteStop):
                z.run_audio_gate(self.run, "a2", plan, [], article_text="a")
            shared.assert_not_called()

    def test_m1_slowdown_part3_cN_and_human_review(self):
        lvl = f"{self.run}/a2"
        nd = f"{lvl}/narration"
        # part3相当 + _cN: 記録なし+originalなし -> FAIL
        _write_tone(f"{nd}/full_story_part3_c2.wav", 1.0)
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_std_english_slowdown(lvl, {"full_story_part3_c2": {"status": "OK"}})
        # Human Review採択clip: 記録なし -> FAIL
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_std_english_slowdown(lvl, {"full_story_part3_c2": {"status": "STOPPED", "slowdown_applied": None}})
        # slowdown_applied False + original無し -> FAIL
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_std_english_slowdown(lvl, {"full_story_part3_c2": {"status": "OK", "slowdown_applied": False}})
        # original比1.06 (現行が長い) -> PASS
        _write_tone(f"{nd}/full_story_part3_c2_original.wav", 1.0)
        _write_tone(f"{nd}/full_story_part3_c2.wav", 1.06)
        r = z.verify_std_english_slowdown(lvl, {"full_story_part3_c2": {"status": "STOPPED"}})
        self.assertTrue(r["full_story_part3_c2"]["ok"])
        # 比1.00 -> FAIL
        _write_tone(f"{nd}/full_story_part3_c2.wav", 1.0)
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_std_english_slowdown(lvl, {"full_story_part3_c2": {"status": "STOPPED"}})
        # slowdown_applied True -> PASS (dialogue clip _c1含む)
        r = z.verify_std_english_slowdown(lvl, {"full_story_part1_c2": {"slowdown_applied": True}})
        self.assertTrue(r["full_story_part1_c2"]["ok"])
        # 1件でも不合格ならSTOP(例外なし)
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_std_english_slowdown(lvl, {"full_story_part1_c1": {"slowdown_applied": True},
                                                "full_story_part2_c1": {"status": "OK"}})

    def test_full_gate_pass_with_std_fakes_and_canonical_article(self):
        plan, story, kp, out = self._run_stage("a2")
        z.provision_shell_assets(self.run, "a2", kp_count=1)
        shell = list(z.SHELL_ASSET_SOURCES) + ["kp1_number"]
        with mock.patch("er003_v1_n3_01_assemble.verify_episode_audio_validation_gate") as shared:
            res = z.run_audio_gate(self.run, "a2", plan, shell, article_text="CANONICAL ARTICLE")
        self.assertTrue(res["m2_complete"])
        shared.assert_called_once()
        self.assertEqual(shared.call_args.kwargs["article_text"], "CANONICAL ARTICLE")
        self.assertEqual(shared.call_args.args[1], "A2")

    def test_adv_gate_skips_std_slowdown(self):
        plan, story, kp, out = self._run_stage("b1b", gen={"slow_std": False})
        z.provision_shell_assets(self.run, "b1b", kp_count=1)
        shell = list(z.SHELL_ASSET_SOURCES) + ["kp1_number"]
        with mock.patch("er003_v1_n3_01_assemble.verify_episode_audio_validation_gate"):
            res = z.run_audio_gate(self.run, "b1b", plan, shell, article_text="a")
        self.assertIsNone(res["m1_slowdown"])

    def test_std_without_slowdown_blocks_before_gate(self):
        plan, story, kp, out = self._run_stage("a2", gen={"slow_std": False})
        z.provision_shell_assets(self.run, "a2", kp_count=1)
        shell = list(z.SHELL_ASSET_SOURCES) + ["kp1_number"]
        with mock.patch("er003_v1_n3_01_assemble.verify_episode_audio_validation_gate") as shared:
            with self.assertRaises(z.FamilyZSlowdownGateStop):
                z.run_audio_gate(self.run, "a2", plan, shell, article_text="a")
            shared.assert_not_called()

    def test_local_rewrite_records_deviation_without_revalidation(self):
        # 2026-10-12ユーザー決定: er061再検証フックは撤去。audio_text_deviationの監査記録のみ(STOPしない)。
        calls = []

        def reval(text_before, text_after):
            calls.append(1)
            return {"verdict": "FAIL"}

        os.makedirs(f"{self.run}/writer")
        json.dump({"story_key": "melos", "chain": []}, open(f"{self.run}/writer/provenance.json", "w"))
        plan, _, _ = make_plan("b1b")
        out = z.run_tts_stage(self.run, "b1b", plan, generators=fake_generators(lr_clips={"full_story_part2_c1"}),
                              revalidate_fn=reval, article_text="He ran through the night. The end.")
        data = json.load(open(out["results_path"], encoding="utf-8"))
        e = data["segments"]["full_story_part2_c1"]
        self.assertEqual(e["audio_text_deviation"]["canonical_text_before_local_rewrite"], "He ran through the night.")
        self.assertIn("indeed", e["audio_text_deviation"]["audio_text_after"])
        self.assertTrue(e["cooldown_occurred"])
        self.assertEqual(calls, [])                                   # 再検証は呼ばれない
        self.assertEqual(e["local_rewrite_revalidation"]["verdict"], "NOT_REQUIRED")
        self.assertNotEqual(e.get("z_adoption"), "blocked_local_rewrite_revalidation")
        prov = json.load(open(f"{self.run}/writer/provenance.json", encoding="utf-8"))
        self.assertEqual(prov["audio_text_deviations"][0]["clip_id"], "full_story_part2_c1")
        ev = json.load(open(out["evidence_path"], encoding="utf-8"))
        row = [c for c in ev["clips"] if c["clip_id"] == "full_story_part2_c1"][0]
        self.assertIsNotNone(row["local_rewrite_diff"])
        self.assertTrue(row["cooldown_occurred"])

    def test_lr_without_article_text_does_not_stop(self):
        plan, _, _ = make_plan("b1b")
        out = z.run_tts_stage(self.run, "b1b", plan, generators=fake_generators(lr_clips={"full_story_part2_c1"}))
        data = json.load(open(out["results_path"], encoding="utf-8"))
        self.assertIn("audio_text_deviation", data["segments"]["full_story_part2_c1"])

    def test_er063_does_not_depend_on_er061(self):
        src = open(os.path.join(os.path.dirname(z.__file__), "er063_family_z_audio_01.py"), encoding="utf-8").read()
        self.assertIsNone(re.search(r"^\s*(import|from)\s+er061", src, re.M))
        self.assertNotIn("revalidate_after_local_rewrite(", src)

    def test_stop_sentinel_run_stops_before_any_generation(self):
        plan, _, _ = make_plan("b1b")
        calls = []
        gens = fake_generators()
        orig = gens["narrator"]
        gens["narrator"] = lambda s, p: (calls.append(s.clip_id), orig(s, p))[1]
        os.makedirs(self.run)
        open(f"{self.run}/STOP", "w").write("stop")
        with self.assertRaises(zst.FamilyZStopSentinel):
            z.run_tts_stage(self.run, "b1b", plan, generators=gens)
        self.assertEqual(calls, [])                                   # 新規API呼出なし
        self.assertTrue(os.path.exists(f"{self.run}/audit_stop_sentinel.jsonl"))   # 監査記録

    def test_stop_sentinel_stop_all_stops_mid_run_and_checkpoint_kept(self):
        plan, _, _ = make_plan("b1b")
        stop_all = os.path.join(self.tmp, "STOP_ALL")
        gens = fake_generators()
        orig = gens["narrator"]

        def gen(s, p):
            r = orig(s, p)
            open(stop_all, "w").write("stop")                          # 1clip生成後にSTOP_ALLが置かれる
            return r
        gens["narrator"] = gen
        with mock.patch.object(zst, "STOP_ALL_PATH", stop_all):
            with self.assertRaises(zst.FamilyZStopSentinel):
                z.run_tts_stage(self.run, "b1b", plan, generators=gens)
        ck = z.load_checkpoint(f"{self.run}/b1b")
        self.assertTrue(ck and ck["segments"])                         # 完了済みclipはcheckpointに残る(再課金防止)

    def test_only_clips_keeps_other_entries(self):
        plan, _, _, _ = self._run_stage("b1b")
        calls = []
        gens = fake_generators()
        orig = gens["narrator"]
        gens["narrator"] = lambda s, p: (calls.append(s.clip_id), orig(s, p))[1]
        # 全clipのreuse_keyを壊してonly_clipsだけが生成されることを見る
        out = z.run_tts_stage(self.run, "b1b", plan, generators=gens, only_clips={"full_story_part2_c1"})
        data = json.load(open(out["results_path"], encoding="utf-8"))
        self.assertIn("full_story_part1_c1", data["segments"])  # 保持
        self.assertEqual(set(out["statuses"]), {"full_story_part2_c1"})

    def test_failed_clip_status_recorded_not_adopted(self):
        plan, _, _, out = self._run_stage("b1b", gen={"fail_clips": {"comment_1"}})
        data = json.load(open(out["results_path"], encoding="utf-8"))
        self.assertEqual(data["segments"]["comment_1"]["z_adoption"], "failed")
        with self.assertRaises(z.FamilyZTtsResultsIncompleteStop):
            z.assert_tts_results_complete(f"{self.run}/b1b", ["comment_1"])


class EvidenceDetailTest(unittest.TestCase):
    def test_attempt_meta_model_voice_from_sidecar_json(self):
        tmp = tempfile.mkdtemp()
        try:
            wav = f"{tmp}/a.wav"
            json.dump({"model": "gemini-2.5-pro-preview-tts", "voice": "Charon"}, open(f"{tmp}/a.json", "w"))
            ev = z.extract_attempt_evidence({"attempts_log": [{"attempt": 1, "attempt_audio_path": wav}]})
            self.assertEqual(ev[0]["tts_model_id"], "gemini-2.5-pro-preview-tts")
            self.assertEqual(ev[0]["voice"], "Charon")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_effective_style_for_default_dialogue(self):
        import er003_b1_p9a_audio as p9a
        adv_d = [s for s in make_plan("b1b")[0] if s.kind == "dialogue"][0]
        self.assertEqual(z._effective_style_sha(adv_d, None), z._sha256_text(p9a.ENGLISH_STYLE_PREFIX))


class WiringTest(unittest.TestCase):
    """real_generators()が共有関数へ正しいstyle/引数を渡すことをmockで固定(実API呼出なし)。"""

    def _spec(self, level, kind, speaker="narrator"):
        plan, _, _ = make_plan(level)
        for s in plan:
            if s.kind == kind and (kind != "dialogue" or s.speaker == speaker):
                return s
        raise AssertionError((level, kind))

    def test_adv_narrator_uses_x_b1_entry_with_pd06(self):
        import er003_v1_sing01_news_tail_fix as ntf
        spec = self._spec("b1b", "narrator")
        with mock.patch.object(ntf, "generate_news_narration_wide_margin", return_value={"status": "OK"}) as m:
            z.real_generators()["narrator"](spec, "x/b1b/narration/full_story_part1_c1.wav")
        kw = m.call_args.kwargs
        self.assertEqual(kw["style_prefix_override"], z._STYLE_TEXT["PD06"])  # 2026-10-17 委任_15: N01 -> PD06(期待値を意図的に更新)
        self.assertEqual(kw["tts_backend"], "speech_metadata_flash_lite")
        self.assertTrue(kw["enable_connected_speech_equivalence_layer"])

    def test_std_narrator_uses_slowdown_path(self):
        import er003_v1_n3_01_tts_generate as n3
        spec = self._spec("a2", "narrator")
        with mock.patch.object(n3, "generate_a2_segment_with_slowdown", return_value={"status": "OK"}) as m:
            z.real_generators()["narrator"](spec, "x/a2/narration/full_story_part1_c1.wav")
        self.assertEqual(m.call_args.kwargs["style_prefix_override"], z._STYLE_TEXT["PD06"])  # 2026-10-17 委任_15: N01 -> PD06逐語(期待値を意図的に更新)

    def test_adv_dialogue_has_no_style_override_and_right_voice(self):
        import er012_b_family_voices_production_01 as bv
        spec = self._spec("b1b", "dialogue", "dionysius")
        with mock.patch.object(bv, "generate_voice_body_wide_margin", return_value={"status": "OK"}) as m:
            z.real_generators()["dialogue"](spec, "x/b1b/narration/full_story_part1_c2.wav")
        self.assertEqual(m.call_args.args[2], "Charon")
        self.assertNotIn("style_prefix_override", m.call_args.kwargs)

    def test_std_dialogue_default_style_same_as_adv_and_postprocess_6pct_no_pd8(self):
        # 2026-10-19 委任_04(ユーザー決定③): 期待値を意図的に更新(旧: Std Dialogue=A2_ENGLISH_STYLE_PREFIX_SLOWERを生成時に渡す)。
        # 現: Advと同一の既定Dialogue Style(style_prefix_overrideを渡さない)+生成後6%減速のみ。
        import er012_b_family_voices_production_01 as bv
        import er003_v1_n3_01_tts_generate as n3
        spec = self._spec("a2", "dialogue", "melos")
        with mock.patch.object(bv, "generate_voice_body_wide_margin", return_value={"status": "OK"}) as m, \
                mock.patch.object(n3, "apply_a2_slowdown_postprocess", return_value={"status": "OK", "slowdown_applied": True}) as pp:
            r = z.real_generators()["dialogue"](spec, "x/a2/narration/full_story_part3_c1.wav")
        self.assertEqual(m.call_args.args[2], "Algieba")
        self.assertNotIn("style_prefix_override", m.call_args.kwargs)   # Advと同一(既定ENGLISH_STYLE_PREFIX)
        self.assertEqual(m.call_args.kwargs, {"max_attempts": 3})
        pp.assert_called_once()
        self.assertTrue(r["slowdown_applied"])

    def test_preview_comment_kp_styles(self):
        import er003_v1_sing01_voice01_generate as v1
        import er003_v1_n3_01_tts_generate as n3
        with mock.patch.object(v1, "generate_charon_english", return_value={"status": "OK"}) as m:
            z.real_generators()["preview"](self._spec("b1b", "preview"), "x/b1b/narration/preview.wav")
            self.assertEqual(m.call_args.kwargs["style_prefix_override"], z._STYLE_TEXT["E1"])
            z.real_generators()["comment"](self._spec("b1b", "comment"), "x/b1b/narration/comment_1.wav")
            self.assertEqual(m.call_args.kwargs["style_prefix_override"], z._E2_UPBEAT)
        with mock.patch.object(n3, "generate_a2_japanese_with_reading_safety", return_value={"status": "OK"}) as m:
            z.real_generators()["preview"](self._spec("a2", "preview"), "x/a2/narration/preview.wav")
            self.assertEqual(m.call_args.kwargs["style_prefix_override"], z._STYLE_TEXT["S3"])
            z.real_generators()["kp_ja"](self._spec("a2", "kp_ja"), "x/a2/narration/kp1_ja.wav")
            self.assertEqual(m.call_args.kwargs["style_prefix_override"], z._STYLE_TEXT["P8_KP"])
        import er003_v1_repro01_main_generate as repro
        with mock.patch.object(repro, "generate_narration_snippet_verified_strict", return_value={"status": "OK"}) as m:
            z.real_generators()["kp_en"](self._spec("a2", "kp_en"), "x/a2/narration/kp1_en.wav")
            self.assertEqual(m.call_args.kwargs["style_prefix_override"], z._STYLE_TEXT["K2"])
        with mock.patch.object(repro, "generate_narration_snippet_verified_strict",
                               side_effect=[{"status": "STOPPED"}, {"status": "OK"}]) as m:
            r = z.real_generators()["kp_en"](self._spec("a2", "kp_en"), "x/a2/narration/kp1_en.wav")
            self.assertTrue(r["fallback_used"])
            self.assertEqual(m.call_args.kwargs["style_prefix_override"], repro.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION)


class SequenceAndPageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _seq(self, level):
        import er003_b1_p9a_audio as p9a
        nd = f"{self.tmp}/run/{level}/narration"
        plan, story, kp = make_plan(level)
        for s in plan:
            _write_tone(f"{nd}/{s.clip_id}.wav", 0.3)
        for n in list(z.SHELL_ASSET_SOURCES) + ["kp1_number"]:
            _write_tone(f"{nd}/{n}.wav", 0.3)
        gs = lambda mono, label: p9a.mono_24k_to_stereo_target(mono)
        zero = np.zeros((4800, 2), dtype="float32")
        seq = z.build_z_sequence(nd, level=level, story_clips=story, kp_items=kp, target_rms=0.1, gs=gs,
                                 gs_already_stereo=lambda d, l: d, intro_gained=zero, notification_gained=zero, outro_gained=zero)
        return [n for n, _ in seq if not n.startswith("_silence_")], story

    def test_comment_after_ids(self):
        _, story, _ = make_plan("a2")
        self.assertEqual(z.comment_after_segment_ids(story), {"2": "full_story_part1_c2", "3": "full_story_part2_c1"})

    def test_sequence_order_std_and_adv(self):
        names, _ = self._seq("a2")
        self.assertEqual(names[:3], ["Intro", "Welcome (Charon)", "Topic intro"])
        self.assertIn("Japanese title", names)
        order = ["Comment 1", "full_story_part1_c1", "full_story_part1_c2", "Comment 2", "full_story_part2_c1",
                 "Comment 3", "full_story_part3_c1", "Outro"]
        idx = [names.index(n) for n in order]
        self.assertEqual(idx, sorted(idx))
        self.assertNotIn("In One Line", " ".join(names))
        self.assertLess(names.index("Preview"), names.index("key_phrase_1"))
        self.assertLess(names.index("key_phrase_1"), names.index("Comment 1"))
        names_adv, _ = self._seq("b1b")
        self.assertNotIn("Japanese title", names_adv)
        self.assertEqual(names_adv[-1], "Outro")

    def test_page_lint(self):
        rows = [{"part": "Preview", "start": 1.0, "dur": 5.0, "file": "audio/a.mp3", "voice": "Aoede", "style": "S3", "script": "x"}]
        html = z.build_listening_page_html("Standard", rows, [("run through", "走り抜ける")], "audio/full.mp3", 100.0)
        lint = z.lint_page_html(html)
        self.assertEqual(lint, {"file_scheme": False, "level_label_leak": False, "kp_label_leak": False})
        self.assertIn("class='kp'", html)
        bad = z.lint_page_html("<p>(A2) file:///C:/x</p>")
        self.assertTrue(bad["file_scheme"] and bad["level_label_leak"])
        self.assertIn("standard.html", z.build_index_html([], []))   # 委任_19: index=標準フォーマット(詳細ページへの導線は補助表示)


class AssemblyAndPagesIntegrationTest(unittest.TestCase):
    """mock TTS音声でassemble_with_timeline(Family C builder)+headroom+timeline.json+試聴ページ生成を通す(オフライン)。"""

    def test_assembly_timeline_and_pages(self):
        tmp = tempfile.mkdtemp()
        try:
            run = f"{tmp}/melos/run_01"
            for level in ("a2", "b1b"):
                plan, story, kp = make_plan(level)
                z.run_tts_stage(run, level, plan, generators=fake_generators())
                z.provision_shell_assets(run, level, kp_count=1)
                tl = z.run_assembly(run, level, story, kp)
                self.assertTrue(os.path.exists(tl["wav"]))
                self.assertTrue(os.path.exists(f"{run}/{level}/assembly/timeline.json"))
                names = tl["sequence_order"]
                self.assertNotIn("In One Line", names)
                self.assertEqual(names[-1], "Outro")
                self.assertGreater(tl["duration_seconds"], 5)
            pages = z.build_pages(run, f"{tmp}/pages")
            for label in ("Standard", "Advanced"):
                with open(pages[label]["page"], encoding="utf-8") as f:
                    html = f.read()
                self.assertEqual(pages[label]["lint"], {"file_scheme": False, "level_label_leak": False, "kp_label_leak": False})
                self.assertIn("Voice:", html)
                self.assertIn("full_story_part1_c2", html)
                self.assertIn("Charon", html)  # 王のclip voice表示
            with open(pages["Standard"]["page"], encoding="utf-8") as f:
                self.assertIn("6%減速適用", f.read())
            self.assertTrue(os.path.exists(f"{tmp}/pages/index.html"))
            # 委任_19: indexはユーザー試聴ページ標準フォーマットに適合し、内部情報(Voice/Style/通知音)を載せない
            self.assertEqual(pages["index"]["standard_check"], "PASS")
            with open(f"{tmp}/pages/index.html", encoding="utf-8") as f:
                idx = f.read()
            self.assertNotIn("Voice:", idx)
            self.assertNotIn("(音楽・通知音。読み上げなし)", idx)   # 効果音行のscript表示は無い(読み上げなしは冒頭noteで1回明記: Gate 7 (f))
            self.assertEqual(idx.count("読み上げなし"), 1)
            self.assertIn("全編を通し再生", idx)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class PagesDirSingleSourceTest(unittest.TestCase):
    """委任_18: 試聴ページ出力先の既定値が runner E2E_PAGES_DIR / HRページ生成tool と一致し、旧melos_01でないこと。"""

    def test_pages_dir_defaults_match_runner_and_tool(self):
        import ast
        import inspect
        import er026_family_z_fiction_production_runner_01 as r
        self.assertEqual(z.PAGES_DIR, r.E2E_PAGES_DIR)
        self.assertEqual(z.PAGES_DIR, "user_test/family_z_melos_02")
        with open("tools/build_family_z_hr_review_page.py", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        out = [n.value.value for n in tree.body if isinstance(n, ast.Assign)
               and any(getattr(t, "id", "") == "OUT" for t in n.targets)]
        self.assertEqual(out, [z.PAGES_DIR])
        self.assertEqual(inspect.signature(z.build_pages).parameters["pages_dir"].default, z.PAGES_DIR)


if __name__ == "__main__":
    unittest.main()
