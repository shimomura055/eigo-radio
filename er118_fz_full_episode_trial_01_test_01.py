# -*- coding: utf-8 -*-
"""er118_fz_full_episode_trial_01 の unit test (API 0、TTSもLLMも呼ばない)。
実行: $env:PYTHONPATH="netblock_harness_01"; .venv\\Scripts\\python.exe -m pytest er118_fz_full_episode_trial_01_test_01.py er118_fz_dialogue_context_tts_trial_01_test_01.py -q
"""
import json
import os
import shutil
import tempfile
import types
import unittest

import er118_fz_full_episode_trial_01 as m
import er118_fz_dialogue_context_tts_trial_01 as t


class InventoryTests(unittest.TestCase):
    def test_counts_and_speakers(self):
        exp = {("monkeys_paw", "a2"): 15, ("monkeys_paw", "b1b"): 17, ("melos", "a2"): 10, ("melos", "b1b"): 11}
        for (w, lv), n in exp.items():
            inv = m.inventory_case(w, lv)
            self.assertEqual(inv["n_dialogue"], n, (w, lv))
            self.assertTrue(inv["all_base_style_sha_match"], (w, lv))
            self.assertTrue(inv["all_status_ok"], (w, lv))
            self.assertTrue(inv["public_full_mp3_exists"], (w, lv))
            self.assertTrue(inv["production_wav_exists"], (w, lv))
        self.assertEqual(sum(exp.values()), 53)

    def test_round2_clips_flagged_as_no_reuse(self):
        inv = m.inventory_case("monkeys_paw", "b1b")
        self.assertEqual(sum(1 for r in inv["rows"] if r["in_round2_selection"]), 8)
        inv_std = m.inventory_case("monkeys_paw", "a2")
        self.assertEqual(sum(1 for r in inv_std["rows"] if r["in_round2_selection"]), 0)

    def test_speed_profile_per_level(self):
        for w in ("monkeys_paw", "melos"):
            self.assertTrue(all(r["speed_profile"] == "std_dialogue_none" for r in m.inventory_case(w, "a2")["rows"]))
            self.assertTrue(all(r["speed_profile"] == "adv_dialogue_fast6" for r in m.inventory_case(w, "b1b")["rows"]))


class ConfigureTests(unittest.TestCase):
    def test_globals_restored_after_use_case(self):
        before = {k: getattr(t, k) for k in m._T_GLOBALS}
        with m.use_case("melos", "b1b"):
            self.assertEqual(t.LEVEL, "b1b")
            self.assertNotEqual(t.SRC_RUN, before["SRC_RUN"])
        self.assertEqual({k: getattr(t, k) for k in m._T_GLOBALS}, before)    # Round 1/2既定(賢者の贈り物)が壊れない
        with self.assertRaises(RuntimeError):
            with m.use_case("melos", "a2"):
                raise RuntimeError("x")
        self.assertEqual({k: getattr(t, k) for k in m._T_GLOBALS}, before)

    def test_melos_voice_map_uses_production_voice(self):
        with m.use_case("melos", "b1b"):
            vm = t.voice_map()
            self.assertEqual(set(vm), {"melos", "king", "friend"})
            self.assertEqual(vm["melos"], "Algieba")
            self.assertEqual(vm["king"], "Charon")        # voice_assignment側のkeyは dionysius
            self.assertEqual(vm["friend"], "Erinome")     # 同 selinuntius

    def test_emotion_developer_title_swapped_rules_unchanged(self):
        with m.use_case("melos", "a2"):
            self.assertIn("Before the Last Light (Melos)", t.EMOTION_DEVELOPER)
            self.assertNotIn("Gift of the Magi", t.EMOTION_DEVELOPER)
            self.assertEqual(t.EMOTION_DEVELOPER.replace("Before the Last Light (Melos)", "X"), t._EMOTION_DEVELOPER_MAGI.replace("The Gift of the Magi", "X"))

    def test_context_extraction_runs_for_every_dialogue_clip(self):
        for w, lv in m.CASES:
            with m.use_case(w, lv):
                plan = t.load_plan()
                for x in m.dialogue_clips(plan):
                    ctx = t.extract_context(plan, x["id"])
                    self.assertEqual(ctx["text"], x["text"])
                    self.assertTrue(ctx["voice"])
                    prompt = t.build_prompt(t.tts_text_for(x), t.style_for_arm("ctx", ctx, None))
                    body = prompt.split("=== TEXT TO SPEAK", 1)[1]
                    self.assertNotIn("CONTEXT", body)    # 文脈は発話本文側に混入しない

    def test_monkeys_paw_allowed_names_include_plural_whites_without_changing_rule(self):
        with m.use_case("monkeys_paw", "a2"):
            self.assertIn("whites", t.ALLOWED_NAMES)
            self.assertTrue({"herbert", "mr", "mrs", "white"} <= t.ALLOWED_NAMES)    # Round 2の許可名は維持
            plan = t.load_plan()
            cid = m.dialogue_clips(plan)[0]["id"]
            ctx = t.extract_context(plan, cid)
            item = {"clip_id": cid, "speaker_state": "a little tense", "scene": "The Whites sit by the fire.", "reaction_to_previous": "", "evidence": [], "has_explicit_cue": False}
            self.assertEqual(t.validate_emotion_items([item], [ctx])[cid]["status"], "NO_EXPLICIT_CUE")     # 複数形は誤DISCARDにならない
            item["scene"] = "By the fire sits Mortimer."
            self.assertEqual(t.validate_emotion_items([item], [ctx])[cid]["status"], "DISCARDED")            # 本物の新規固有名詞は従来どおりDISCARD


class GateTests(unittest.TestCase):
    def test_gen_refused_without_go_or_preflight(self):
        """GO(scope=Phase 1b)・自己検証・dry-runが無ければ gen は有料生成を起動しない(live経路は _require_go で止まる)。"""
        old = m.GO_FILE
        m.GO_FILE = "er118_output/fz_full_episode_trial_01/_nonexistent_GO.json"
        try:
            with self.assertRaises(SystemExit):
                m.gen_case("melos", "a2")
        finally:
            m.GO_FILE = old

    def test_llm_refused_without_go(self):
        old = m.GO_FILE
        m.GO_FILE = "er118_output/fz_full_episode_trial_01/_nonexistent_GO.json"
        try:
            with self.assertRaises(SystemExit):
                m.run_llm_case("melos", "a2", client=object())
        finally:
            m.GO_FILE = old

    def test_llm_refused_with_bad_go(self):
        tmp = tempfile.mkdtemp(dir=os.path.join(m.ROOT, "er118_output"))
        try:
            rel = os.path.relpath(os.path.join(tmp, "GO.json"), m.ROOT).replace("\\", "/")
            old = m.GO_FILE
            m.GO_FILE = rel
            for go in ({"managed_id": "x", "scope": m.SCOPE_PHASE1A, "cap_jpy": 5}, {"managed_id": m.MANAGED_ID, "scope": "Phase 1b", "cap_jpy": 5},
                       {"managed_id": m.MANAGED_ID, "scope": m.SCOPE_PHASE1A, "cap_jpy": 30}):
                with open(os.path.join(m.ROOT, rel), "w", encoding="utf-8") as f:
                    json.dump(go, f)
                with self.assertRaises(SystemExit):
                    m.run_llm_case("melos", "a2", client=object())
        finally:
            m.GO_FILE = old
            shutil.rmtree(tmp, ignore_errors=True)

    def test_llm_with_fake_client_writes_only_under_out_root_and_validates(self):
        tmp = tempfile.mkdtemp(dir=os.path.join(m.ROOT, "er118_output"))
        old = (m.GO_FILE, m.OUT_ROOT, m._stop_check)
        try:
            rel_out = os.path.relpath(tmp, m.ROOT).replace("\\", "/")
            m.OUT_ROOT = rel_out
            m.GO_FILE = f"{rel_out}/GO.json"
            m._stop_check = lambda *a, **k: None
            with open(os.path.join(tmp, "GO.json"), "w", encoding="utf-8") as f:
                json.dump({"managed_id": m.MANAGED_ID, "scope": m.SCOPE_PHASE1A, "cap_jpy": 5}, f)
            with m.use_case("melos", "a2"):
                plan = t.load_plan()
                ids = [x["id"] for x in m.dialogue_clips(plan)]
            items = [{"clip_id": i, "speaker_state": "", "scene": "In the hall.", "reaction_to_previous": "", "evidence": [], "has_explicit_cue": False} for i in ids]

            class R:
                model = "gpt-6-luna-2026"
                output_text = json.dumps({"items": items})
                usage = types.SimpleNamespace(input_tokens=1000, output_tokens=500, input_tokens_details=None)

            class C:
                class responses:
                    @staticmethod
                    def create(**kw):
                        assert kw["model"] == t.LLM_MODEL
                        return R()

            rec = m.run_llm_case("melos", "a2", client=C())
            self.assertEqual(rec["n_clips"], 10)
            self.assertEqual(rec["n_no_explicit_cue"], 10)
            self.assertTrue(os.path.exists(os.path.join(tmp, "melos", "a2", "llm", "emotion_notes.json")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "melos", "a2", "llm", "emotion_review.json")))
            rev = t.load_json(f"{rel_out}/melos/a2/llm/emotion_review.json")
            self.assertTrue(all(v["fable_decision"] is None for v in rev["items"].values()))   # Fableレビュー前
        finally:
            m.GO_FILE, m.OUT_ROOT, m._stop_check = old
            shutil.rmtree(tmp, ignore_errors=True)


class BudgetTests(unittest.TestCase):
    def test_budget_within_autonomous_window(self):
        b = [m.budget_case(w, lv) for w, lv in m.CASES]
        self.assertEqual(sum(x["n_clips"] for x in b), 53)
        self.assertTrue(all(x["style_increment_est_jpy"] > 0 for x in b))
        total_1call = sum(x["tts_ctx_est_jpy_1call_per_clip"] for x in b)
        self.assertLess(total_1call * 3.0 + 53 * 3.0 * m.R2_ASR_PER_CALL_JPY, 300)   # 天井(全clip通算3回)でも300円未満


class Phase1bGuardTests(unittest.TestCase):
    """Opus条件A M-1〜M-8 / R-1〜R-9 の反映test(API 0。接続試行0)。"""

    def _tmp_out_root(self):
        tmp = tempfile.mkdtemp(dir=os.path.join(m.ROOT, "er118_output"))
        return tmp, os.path.relpath(tmp, m.ROOT).replace("\\", "/")

    def test_realpath_guard_not_string_prefix(self):
        tmp, rel = self._tmp_out_root()
        old = m.OUT_ROOT
        try:
            m.OUT_ROOT = rel
            m.assert_writable(f"{rel}/a/b.json")
            m.assert_out_root(f"{rel}/run/x")
            for bad in (f"{rel}_evil/x.json", f"{rel}/../x.json", "er026_output/family_z_production_e2e_01/melos/run_e2e_06/a2/narration/x.wav",
                        "user_test/family_z_melos_02/index.html"):
                with self.assertRaises(SystemExit, msg=bad):
                    m.assert_writable(bad)
            with self.assertRaises(SystemExit):
                m.assert_out_root(f"{m.PAGE_ROOT}/x.html")      # run_dir は PAGE_ROOT では不可
        finally:
            m.OUT_ROOT = old
            shutil.rmtree(tmp, ignore_errors=True)

    def test_safe_copy_makes_distinct_file_and_refuses_hardlink_dst(self):
        tmp, rel = self._tmp_out_root()
        old = m.OUT_ROOT
        try:
            m.OUT_ROOT = rel
            src = f"{rel}/src.bin"
            with open(os.path.join(m.ROOT, src), "wb") as f:
                f.write(b"abc")
            m.safe_copy(src, f"{rel}/d/dst.bin")
            self.assertFalse(os.path.samefile(os.path.join(m.ROOT, src), os.path.join(m.ROOT, rel, "d", "dst.bin")))
            self.assertEqual(os.stat(os.path.join(m.ROOT, rel, "d", "dst.bin")).st_nlink, 1)
            os.link(os.path.join(m.ROOT, src), os.path.join(m.ROOT, rel, "d", "hard.bin"))      # dstがhardlinkなら書かない(Production破壊防止)
            with self.assertRaises(SystemExit):
                m.safe_copy(f"{rel}/d/dst.bin", f"{rel}/d/hard.bin")
            with open(os.path.join(m.ROOT, src), "rb") as f:
                self.assertEqual(f.read(), b"abc")
            with self.assertRaises(SystemExit):
                m.safe_copy(src, "er026_output/family_z_production_e2e_01/_must_not_write.bin")
        finally:
            m.OUT_ROOT = old
            shutil.rmtree(tmp, ignore_errors=True)

    def test_use_case_not_reentrant_and_restores_on_exception(self):
        before = {k: getattr(t, k) for k in m._T_GLOBALS}
        with m.use_case("melos", "a2"):
            with self.assertRaises(RuntimeError):
                with m.use_case("melos", "b1b"):
                    pass
            self.assertEqual(t.LEVEL, "a2")                  # 失敗した入れ子が外側のcaseを壊さない
        self.assertEqual({k: getattr(t, k) for k in m._T_GLOBALS}, before)
        self.assertIsNone(m._USE_CASE_ACTIVE["v"])
        with self.assertRaises(ZeroDivisionError):
            with m.use_case("melos", "b1b"):
                1 / 0
        self.assertEqual({k: getattr(t, k) for k in m._T_GLOBALS}, before)
        self.assertIsNone(m._USE_CASE_ACTIVE["v"])

    def test_require_go_scopes_separated(self):
        tmp, rel = self._tmp_out_root()
        old = m.GO_FILE
        try:
            m.GO_FILE = f"{rel}/GO.json"
            go_b = {"managed_id": m.MANAGED_ID, "scope": m.SCOPE_PHASE1B, "cap_jpy": 100}
            with open(os.path.join(m.ROOT, m.GO_FILE), "w", encoding="utf-8") as f:
                json.dump(go_b, f)
            self.assertEqual(m._require_go(m.SCOPE_PHASE1B, m.PHASE1B_CAP_JPY)["cap_jpy"], 100)
            with self.assertRaises(SystemExit):
                m._require_go()                                  # Phase 1a(5円)の関門では通らない
            go_b["cap_jpy"] = 150
            with open(os.path.join(m.ROOT, m.GO_FILE), "w", encoding="utf-8") as f:
                json.dump(go_b, f)
            with self.assertRaises(SystemExit):
                m._require_go(m.SCOPE_PHASE1B, m.PHASE1B_CAP_JPY)  # 100円超は不可
        finally:
            m.GO_FILE = old
            shutil.rmtree(tmp, ignore_errors=True)

    def test_adopt_decision_m7_m8(self):
        ok = {"status": "OK", "repetition_qa_checked": True, "comparison_valid": True, "leakage": {"leakage_final": False},
              "verbatim_observation": {"token_equal": False, "token_similarity": 0.8}}
        self.assertTrue(m.adopt_decision(ok)["adopted"])         # M-7: token_equal=False でも blocking にしない(Production PASS系なら採用)
        self.assertFalse(m.adopt_decision({**ok, "status": "STOPPED"})["adopted"])
        self.assertFalse(m.adopt_decision({**ok, "repetition_qa_checked": False})["adopted"])
        self.assertFalse(m.adopt_decision({**ok, "comparison_valid": False})["adopted"])
        d = m.adopt_decision({**ok, "leakage": {"leakage_final": True}})
        self.assertFalse(d["adopted"])
        self.assertTrue(d["hold_pending_fable_listen"])           # C3 flagged = 採用保留(Fable聴取確認待ち)

    def test_prod_inputs_a2_matches_runner_load_level_inputs(self):
        import er026_family_z_fiction_production_runner_01 as r
        for w, lv in (("monkeys_paw", "a2"), ("melos", "a2")):
            c = m.WORK_CFG[w]
            ctx = r.E2EContext(story_key=c["story_key"], slug=c["story_key"], run=os.path.basename(c["run"]))
            ref, mine = r.load_level_inputs(ctx, lv), m.prod_inputs(w, lv)
            self.assertEqual([x["id"] for x in ref["story_clips"]], [x["id"] for x in mine["story_clips"]])
            self.assertEqual(ref["kp_items"], mine["kp_items"])
            self.assertEqual(sorted(ref["chunk_plans"]), sorted(mine["chunk_plans"]))
            self.assertEqual([(s.clip_id, s.kind, s.text) for s in ref["plan"]], [(s.clip_id, s.kind, s.text) for s in mine["plan"]])
            self.assertEqual(ref["article_text"], mine["article_text"])

    def test_story_clips_0_is_non_dialogue_and_voice_consistency(self):
        """M-5(story_clips[0]非dialogue) / R-8(b)(同一speakerの全clipが同一Voice、voice_assignment.jsonと一致)。"""
        alias = {"king": "dionysius", "friend": "selinuntius"}
        for w, lv in m.CASES:
            self.assertNotIn(m.prod_inputs(w, lv)["story_clips"][0]["id"], m.dialogue_specs(w, lv))
            with m.use_case(w, lv):
                plan = t.load_plan()
                res = t.load_json(t.TTS_RESULTS_PATH)["segments"]
                by_sp = {}
                for x in m.dialogue_clips(plan):
                    by_sp.setdefault(x["speaker"], set()).add(res[x["id"]]["voice"])
                self.assertTrue(all(len(v) == 1 for v in by_sp.values()), (w, lv, by_sp))
                va = {sp["speaker"]: sp["voice"] for sp in t.load_json(f"{t.SRC_RUN}/voice_assignment.json")["speakers"]}
                for spk, voices in by_sp.items():
                    key = alias.get(spk, spk) if w == "melos" else spk
                    if key in va:
                        self.assertEqual(next(iter(voices)), va[key], (w, lv, spk))
                self.assertEqual(t.voice_map(), {k: next(iter(v)) for k, v in by_sp.items()})

    def test_build_run_dir_isolated_and_only_dialogue_replaced(self):
        """M-1/M-2/M-3/M-4: adoptedのdialogueだけTrial音声に置換、Production原音の _original は除去、全pathがOUT_ROOT配下、hardlink無し、非採用clipはProduction音声のまま。"""
        w, lv = "monkeys_paw", "b1b"
        specs = m.dialogue_specs(w, lv)
        cids = list(specs)
        a_cid, n_cid = cids[0], cids[1]
        tmp, rel = self._tmp_out_root()
        old = m.OUT_ROOT
        try:
            m.OUT_ROOT = rel
            fake = f"{rel}/fakegen"
            os.makedirs(os.path.join(m.ROOT, fake))
            prod_narr = f"{m.WORK_CFG[w]['run']}/{lv}/narration"
            with open(os.path.join(m.ROOT, prod_narr, f"{a_cid}.wav"), "rb") as f:
                data = f.read()
            with open(os.path.join(m.ROOT, fake, "g.wav"), "wb") as f:
                f.write(data + b"TRIAL-WAV")
            with open(os.path.join(m.ROOT, fake, "g_original.wav"), "wb") as f:
                f.write(data + b"TRIAL-ORIG")
            prod_res = t.load_json(f"{m.WORK_CFG[w]['run']}/{lv}/audit/tts_generation_results.json")
            entry = json.loads(json.dumps(prod_res["segments"][a_cid]))
            adopted = {a_cid: {"gen_wav": f"{fake}/g.wav", "gen_original": f"{fake}/g_original.wav", "entry": entry}}
            b = m.build_run_dir(w, lv, "run_t", adopted)
            narr = f"{b['run_dir']}/{lv}/narration"
            self.assertEqual(m.file_sha(f"{narr}/{a_cid}.wav"), m.file_sha(f"{fake}/g.wav"))
            self.assertEqual(m.file_sha(f"{narr}/{a_cid}_original.wav"), m.file_sha(f"{fake}/g_original.wav"))
            prod_shas = {m.file_sha(f"{prod_narr}/{fn}") for fn in os.listdir(os.path.join(m.ROOT, prod_narr)) if fn.endswith(".wav")}
            self.assertNotIn(m.file_sha(f"{narr}/{a_cid}_original.wav"), prod_shas)           # M-2: Trial _original はProductionのどのファイルとも一致しない
            self.assertEqual(m.file_sha(f"{narr}/{n_cid}.wav"), m.file_sha(f"{prod_narr}/{n_cid}.wav"))   # 非採用はProduction音声(M-8)
            iso = m.verify_isolation(w, lv, b["run_dir"])
            self.assertTrue(iso["ok"], iso)
            res = t.load_json(f"{b['run_dir']}/{lv}/audit/tts_generation_results.json")
            self.assertEqual(res["segments"][a_cid]["path"], f"{narr}/{a_cid}.wav")
            self.assertEqual(res["segments"]["full_story_part1_c1"]["path"], f"{narr}/full_story_part1_c1.wav")
            self.assertFalse([k for k, v in res["segments"].items() if isinstance(v.get("path"), str) and not m.under(v["path"], rel)])
            # Production側は不変
            self.assertEqual(m.file_sha(f"{prod_narr}/{a_cid}.wav"), hashlib_sha(os.path.join(m.ROOT, prod_narr, f"{a_cid}.wav")))
        finally:
            m.OUT_ROOT = old
            shutil.rmtree(tmp, ignore_errors=True)

    def test_m5_detects_condition_drift(self):
        w, lv = "melos", "a2"
        ptl = t.load_json(f"{m.WORK_CFG[w]['run']}/{lv}/assembly/timeline.json")
        self.assertTrue(m.compare_to_production(w, lv, copy_json(ptl), identical=False)["m5_ok"])
        x = copy_json(ptl)
        x["gain_report"]["target_rms"] += 0.001
        self.assertFalse(m.compare_to_production(w, lv, x, identical=False)["m5_ok"])
        x = copy_json(ptl)
        lab = next(k for k in x["gain_report"] if k not in ("target_rms",) and k not in m.dialogue_specs(w, lv) and "gain" in x["gain_report"][k])
        x["gain_report"][lab]["gain"] += 0.01
        self.assertFalse(m.compare_to_production(w, lv, x, identical=False)["m5_ok"])
        x = copy_json(ptl)
        x["headroom"]["scalar"] = 0.9
        self.assertFalse(m.compare_to_production(w, lv, x, identical=False)["m5_ok"])
        x = copy_json(ptl)       # dialogue labelのgain差は許容(差はセリフclipのみ)
        dl = next(k for k in x["gain_report"] if k in m.dialogue_specs(w, lv))
        x["gain_report"][dl]["gain"] += 0.05
        self.assertTrue(m.compare_to_production(w, lv, x, identical=False)["m5_ok"])

    def test_gen_case_injected_isolated_and_no_forbidden_round2_calls(self):
        """M-6: Round 1/2 moduleのglobal依存関数を例外化しても gen が通る(本module側再実装)。書込みは(差替えた)OUT_ROOT配下のみ、clip別dirに result.json。"""
        tmp, rel = self._tmp_out_root()
        old = m.OUT_ROOT
        forbidden = ("generate_arm", "snapshot_protected", "protected_paths", "est_next_clip_jpy", "trial_reuse_key", "_require_go", "_stop_check", "scan_repo_mtime")
        saved = {n: getattr(t, n) for n in forbidden}

        def boom(*a, **k):
            raise AssertionError("forbidden Round1/2 function called")
        import numpy as np
        import soundfile as sf

        def factory(level, cid):
            def fn(text, wav_rel, voice, style):
                sr = 24000
                sf.write(os.path.join(m.ROOT, wav_rel), (0.1 * np.sin(np.arange(sr) / 20.0)).astype("float32"), sr)
                self.assertIn("CONTEXT", style)
                self.assertNotIn("CONTEXT", text)         # 文脈は発話本文(TEXT TO SPEAK)に混入しない
                return {"status": "OK", "text": text, "path": wav_rel, "voice": voice, "asr_text": text, "attempts_log": [{"attempt": 1, "status": "OK", "verified": True}],
                        "instruction_type": "english_style_prefix_wide_margin", "repetition_qa_checked": True, "tts_generations_used": 1}
            return fn
        try:
            m.OUT_ROOT = rel
            for n in forbidden:
                setattr(t, n, boom)
            r = m.gen_case("melos", "a2", gen_fn_factory=factory, only=None)
            self.assertEqual(r["summary"]["n_clips"], 10)
            for cid in r["results"]:
                self.assertTrue(os.path.exists(os.path.join(tmp, "melos", "a2", "gen", cid, "result.json")))
                self.assertTrue(os.path.exists(os.path.join(tmp, "melos", "a2", "gen", cid, "a2", "narration", f"{cid}.wav")))
                self.assertFalse(r["results"][cid]["adopt"]["adopted"])     # 実送信prompt未捕捉(injection)なので comparison_valid=false → 不採用(安全側)
            self.assertTrue(os.path.exists(os.path.join(tmp, "melos", "a2", "gen_summary.json")))
        finally:
            for n, f in saved.items():
                setattr(t, n, f)
            m.OUT_ROOT = old
            shutil.rmtree(tmp, ignore_errors=True)

    def test_live_gen_requires_selfcheck_and_dryrun(self):
        tmp, rel = self._tmp_out_root()
        old = m.OUT_ROOT
        try:
            m.OUT_ROOT = rel
            with self.assertRaises(SystemExit):
                m._ensure_selfcheck_and_dryrun("melos", "a2")
        finally:
            m.OUT_ROOT = old
            shutil.rmtree(tmp, ignore_errors=True)

    def test_store_contamination_attribution(self):
        tmp, rel = self._tmp_out_root()
        try:
            a, b = f"{rel}/a.jsonl", f"{rel}/b.jsonl"
            with open(os.path.join(m.ROOT, a), "w", encoding="utf-8") as f:
                f.write(m.OUT_ROOT + "/x\n")
            with open(os.path.join(m.ROOT, b), "w", encoding="utf-8") as f:
                f.write("other agent\n")
            r = m.store_contamination([a, b], 0.0)
            self.assertEqual(r["contaminated"], [a])
            self.assertEqual(r["external_changes_not_from_this_trial"], [b])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_snapshot_diff_detects_production_change(self):
        before = {"runs": {"w": {"a": "1", "b": "2"}}, "pages": {"w": {"p": "1"}}, "stores": {"s": "1"}}
        after = {"runs": {"w": {"a": "1", "b": "3", "c": "9"}}, "pages": {"w": {"p": "1"}}, "stores": {"s": "2"}}
        d = m.snapshot_diff(before, after)
        self.assertEqual(d["runs"], ["w/b", "w/c"])
        self.assertEqual(d["pages"], [])
        self.assertEqual(d["stores"], ["s"])


class Phase1bArtifactTests(unittest.TestCase):
    """生成前に取得した実測の成果物(API 0で再現可能)が成立していること。"""

    def test_selfcheck_all_units_exact_match(self):
        for w, lv in m.CASES:
            d = t.load_json(f"{m.case_dir(w, lv)}/selfcheck.json")
            self.assertTrue(d["pass"], (w, lv))
            self.assertEqual(d["compare"]["wav_max_abs_diff"], 0.0)
            self.assertTrue(d["gate"]["ok"])

    def test_dryrun_sinks_landed_in_out_root(self):
        d = t.load_json(f"{m.OUT_ROOT}/dryrun_sinks.json")
        self.assertTrue(d["pass"])
        self.assertTrue(d["attempt_history_sink_landed"] and d["lock_state_landed"] and d["human_review_sink_landed"])
        self.assertEqual(d["netblock_blocked_lines"], [])
        self.assertEqual(d["snapshot_diff"]["runs"] + d["snapshot_diff"]["pages"], [])

    def test_noise_band_sha_recorded_in_preregistration(self):
        sha = m.file_sha(f"{m.OUT_ROOT}/noise_band_r2.json")
        with open(os.path.join(m.ROOT, m.DOC_DIR, "PREREGISTERED_CRITERIA_02.md"), encoding="utf-8") as f:
            self.assertIn(sha, f.read())

    def test_all_emotion_reviews_filled_accept(self):
        n = 0
        for w, lv in m.CASES:
            rev = t.load_json(f"{m.case_dir(w, lv)}/llm/emotion_review.json")["items"]
            for cid, v in rev.items():
                self.assertEqual(v["fable_decision"], "accept", cid)
                self.assertTrue(v["summary_ja"], cid)
                n += 1
        self.assertEqual(n, 53)


def hashlib_sha(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def copy_json(o):
    return json.loads(json.dumps(o))


if __name__ == "__main__":
    unittest.main()
