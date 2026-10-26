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
    def test_gen_assemble_page_refused(self):
        for c in ("gen", "assemble", "page"):
            with self.assertRaises(SystemExit):
                m.main([c])

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
            m._stop_check = lambda: None
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


if __name__ == "__main__":
    unittest.main()
