# -*- coding: utf-8 -*-
"""FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_02: Family Z(Advanced narrator 100語超=chunk TTS+0.2秒、B_r1)配線のtest(API 0・TTS 0。TTSはfake)。
実行: .venv/Scripts/python.exe -m pytest er117_z_chunk_wiring_test_01.py -q  (repo root)"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401  (Production監査ログへの追記を隔離)
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import numpy as np

import er002_common as common
import er062_family_z_structure_01 as zst
import er063_family_z_audio_01 as z
import er117_chunk_tts_production_01 as core

SR = common.SAMPLE_RATE

# 段落0=短い narrator clip / 段落1〜3=長い narrator clip(3段落・計約130語 → ceil(130/100)=2 chunk、段落境界で分割)
PARAS = [
    "The night was quiet and the old house slept.",
    " ".join(["Alpha beta gamma delta epsilon zeta."] * 7).strip(),          # 42語
    " ".join(["Eta theta iota kappa lambda mu nu."] * 6).strip(),            # 42語
    " ".join(["Xi omicron pi rho sigma tau upsilon."] * 6).strip(),          # 42語
    "A short closing paragraph for part three.",
]


def _clip(i, text, voice="narrator", idx=None):
    return {"id": i, "voice": voice, "speaker": voice, "text": core.normalize_for_tts(text), "word_count": core.wc(text),
            "source_paragraph_indices": idx or [], "part": int(i[len("full_story_part")])}


def story():
    return [
        _clip("full_story_part1_c1", PARAS[0], idx=[0]),
        _clip("full_story_part1_c2", '"You will fail," said the king.', voice="dionysius", idx=[0]),
        _clip("full_story_part2_c1", " ".join(PARAS[1:4]), idx=[1, 2, 3]),
        _clip("full_story_part3_c1", PARAS[4], idx=[4]),
    ]


def chunk_plans(level="b1b"):
    return core.plan_z_level(story(), PARAS, level)


def make_plan(level="b1b", chunked=True):
    kp = [{"rank": 1, "used_form": "run through", "japanese_gloss": "走り抜ける", "japanese_gloss_tts": "走り抜ける"}]
    comments = {1: "c1 text", 2: "c2 text", 3: "c3 text"}
    plan = z.build_level_plan(level, story(), "preview text", comments, kp, "The Three-Day Promise", "走れメロス" if level == "a2" else None,
                              chunk_plans=chunk_plans(level) if chunked else None)
    return plan, kp


def _tone(path, seconds=1.0, amp=0.2, freq=220):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    t = np.arange(int(SR * seconds)) / SR
    common.write_wav_float(path, (amp * np.sin(2 * np.pi * freq * t)).astype("float32"), SR, 1)


class Gens:
    def __init__(self, fail=(), lr=(), slowdown_narrator=()):
        self.calls, self.fail, self.lr, self.slowdown_narrator = [], set(fail), set(lr), set(slowdown_narrator)

    def make(self, kind):
        def fn(spec, out_path):
            self.calls.append(spec.clip_id)
            if spec.clip_id in self.fail:
                _tone(out_path, 0.5)
                return {"status": "STOPPED", "reason": "x"}
            adv_fast = spec.level == "b1b" and spec.kind == "dialogue"
            _tone(out_path, (1.0 / z.Z_ADV_DIALOGUE_SPEEDUP_TEMPO) if adv_fast else 1.0 + 0.1 * (hash(spec.clip_id) % 5), freq=200 + hash(spec.clip_id) % 50)
            r = {"status": "OK", "asr_text": spec.text, "disfluency_checked": True, "text": spec.text,
                 "standard_attempts_log": [{"attempt": 1, "instruction_type": "english_style_prefix_wide_margin",
                                            "style_prefix": {"sha256": "ab" * 32, "head200": "x"},
                                            "tts_model_id": "gemini-3.8-flash-lite-tts", "voice": spec.voice}]}
            if spec.clip_id in self.lr:
                r["canonical_text_before_local_rewrite"] = spec.text
                r["local_rewrite_recovery"] = {"selection": {"selected": {"rewritten_segment": spec.text + " indeed"}}}
            if spec.kind == "kp_en":
                t = z._norm_for_tts(spec)
                r["asr_judgement"] = {"state": "PASS", "reason_code": "dual_agreed", "dual": {
                    "required": True, "primary_provider": "openai", "secondary_provider": "azure", "primary_pass": True,
                    "primary_text": t, "primary_rescued_by_secondary": False, "primary_rescue_layers": [],
                    "secondary_called": True, "secondary_pass": True, "secondary_text": t, "outcome": "PASS"}}
            if spec.level == "a2" and spec.kind == "narrator":
                _tone(out_path.replace(".wav", "_original.wav"), 1.0)
                r["slowdown_applied"] = True
                r["slowdown_info"] = {"src_duration_seconds": 1.0, "dst_duration_seconds": 1.06, "slowdown_pct_target": 6.0}
            if adv_fast:
                _tone(out_path.replace(".wav", "_original.wav"), 1.0)
                r["slowdown_applied"] = True
                r["original_path"] = out_path.replace(".wav", "_original.wav")
                r["slowdown_info"] = {"src_duration_seconds": 1.0, "dst_duration_seconds": 1.0 / z.Z_ADV_DIALOGUE_SPEEDUP_TEMPO,
                                      "slowdown_pct_target": z.Z_ADV_DIALOGUE_SLOWDOWN_PCT}
            if spec.clip_id in self.slowdown_narrator:
                r["slowdown_applied"] = True
            return r
        return fn

    def gens(self):
        return {k: self.make(k) for k in ("narrator", "dialogue", "topic_intro", "preview", "comment", "japanese_title", "kp_en", "kp_ja")}


def _res(run, level="b1b"):
    return json.load(open(f"{run}/{level}/audit/tts_generation_results.json", encoding="utf-8"))


SHELL = list(z.SHELL_ASSET_SOURCES) + ["kp1_number"]


class ZPlanTests(unittest.TestCase):
    def test_plan_expands_only_adv_long_narrator(self):
        plan, _ = make_plan("b1b")
        ids = [s.clip_id for s in plan if s.kind in ("narrator", "dialogue")]
        self.assertEqual(ids, ["full_story_part1_c1", "full_story_part1_c2", "full_story_part2_c1_k1", "full_story_part2_c1_k2", "full_story_part3_c1"])
        self.assertNotIn("full_story_part2_c1", [s.clip_id for s in plan])               # 親ClipSpecは作らない
        k = {s.clip_id: s for s in plan}["full_story_part2_c1_k1"]
        self.assertEqual((k.kind, k.voice, k.role_key, k.part), ("narrator", "Aoede" if k.voice == "Aoede" else k.voice, "NARRATOR_FULL_STORY_ADV", 2))
        self.assertEqual(k.extra["chunk"]["parent_id"], "full_story_part2_c1")
        self.assertEqual(k.extra["chunk"]["count"], 2)
        self.assertEqual(" ".join(s.text for s in plan if s.clip_id.startswith("full_story_part2_c1_k")), core.normalize_for_tts(" ".join(PARAS[1:4])))

    def test_std_and_unchunked_plan_identical_to_legacy(self):
        a, _ = make_plan("a2", chunked=True)
        b, _ = make_plan("a2", chunked=False)
        self.assertEqual(a, b)                                                           # Std: chunk化しない(ClipSpec列が完全一致)
        c, _ = make_plan("b1b", chunked=False)
        d = z.build_level_plan("b1b", story(), "preview text", {1: "c1 text", 2: "c2 text", 3: "c3 text"},
                               [{"rank": 1, "used_form": "run through", "japanese_gloss": "x", "japanese_gloss_tts": "x"}], "The Three-Day Promise")
        self.assertEqual([s.clip_id for s in c if s.kind in ("narrator", "dialogue")],
                         ["full_story_part1_c1", "full_story_part1_c2", "full_story_part2_c1", "full_story_part3_c1"])
        self.assertEqual(len(d), len(c))

    def test_reuse_key_chunk_only_and_non_chunk_unchanged(self):
        plan, _ = make_plan("b1b")
        legacy, _ = make_plan("b1b", chunked=False)
        lk = {s.clip_id: z.build_reuse_key(s) for s in legacy}
        for s in plan:
            key = z.build_reuse_key(s)
            if (s.extra or {}).get("chunk"):
                self.assertEqual(key["chunk_tts"]["planner_version"], core.CHUNK_PLANNER_VERSION)
                self.assertEqual(key["chunk_tts"]["index"], s.extra["chunk"]["index"])
                self.assertEqual(key["chunk_tts"]["extra_pause_s"], 0.2)
            else:
                self.assertEqual(key, lk[s.clip_id])                                      # 非chunk specのkeyはバイト不変(旧entryの再利用を壊さない)
                self.assertNotIn("chunk_tts", key)
        # chunkのkeyは、同じ本文でも旧(非chunk)親clipのkeyと一致しない(旧親音声が再利用されない)
        self.assertNotEqual(z.build_reuse_key([s for s in plan if s.clip_id == "full_story_part2_c1_k1"][0]), lk["full_story_part2_c1"])

    def test_non_chunk_reuse_keys_match_previous_run_results_on_disk(self):
        """実run run_sf_prod_02(承認Trial対象)のresultsに保存されたreuse_keyと、新planの非chunk spec(Std全clip・Adv dialogue・短narrator・
        KP・Comment等)のkeyがバイト一致する(=旧音声の再利用が維持される)。"""
        run = "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02"
        if not os.path.exists(f"{run}/b1b/audit/tts_generation_results.json"):
            self.skipTest("run_sf_prod_02 missing")
        import er026_family_z_fiction_production_runner_01 as r26
        checked = 0
        for level in ("b1b", "a2"):
            lv = f"{run}/{level}"
            plan_json = json.load(open(f"{run}/segment_plan_{level}.json", encoding="utf-8"))
            sup = json.load(open(f"{run}/support/{level}_support.json", encoding="utf-8"))
            kp = json.load(open(f"{lv}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
            items = sorted(kp["items"], key=lambda x: x["rank"])
            kp_items = [{"rank": i["rank"], "used_form": i["used_form"], "japanese_gloss": i.get("japanese_gloss", ""),
                         "display_phrase": i["display_phrase"]} for i in items]
            expl = None
            if level == "b1b":
                ex = json.load(open(f"{run}/key_phrases/b1b/kp_explanations.json", encoding="utf-8"))
                expl = {int(k): v["english_explanation"] for k, v in ex["items"].items()}
            cfg = r26.STORY_REGISTRY["the_tell_tale_heart"]
            art = open(f"{run}/writer/{'r2.md' if level == 'b1b' else 'std.md'}", encoding="utf-8").read()
            _, body = zst.split_title_body(art)
            cps = core.plan_z_level(plan_json["clips"], zst.clean_body_paragraphs(body), level)
            plan = z.build_level_plan(level, plan_json["clips"], sup["preview"], {int(n): t for n, t in sup["comments"].items()}, kp_items,
                                      cfg["topic_title"], cfg.get("japanese_title_tts") if level == "a2" else None, kp_explanations=expl,
                                      story_key="the_tell_tale_heart", chunk_plans=cps)
            data = json.load(open(f"{lv}/audit/tts_generation_results.json", encoding="utf-8"))
            for s in plan:
                if (s.extra or {}).get("chunk"):
                    continue
                prev = z._cached_entry(data, s)
                if prev and prev.get("reuse_key") and prev["reuse_key"] == prev["reuse_key"]:
                    self.assertEqual(z.build_reuse_key(s), prev["reuse_key"], f"{level}:{s.clip_id}")
                    checked += 1
            if level == "b1b":
                self.assertEqual(sorted(p for p, v in cps.items() if v["chunked"]), ["full_story_part2_c1", "full_story_part3_c1"])
        self.assertGreater(checked, 20)

    def test_chunk_plans_from_specs_roundtrip(self):
        plan, _ = make_plan("b1b")
        got = z.chunk_plans_from_specs(plan)
        want = chunk_plans("b1b")["full_story_part2_c1"]
        self.assertEqual(sorted(got), ["full_story_part2_c1"])
        self.assertEqual([(c["chunk_id"], c["text"], c["words"], c["boundary_kind"]) for c in got["full_story_part2_c1"]["chunks"]],
                         [(c["chunk_id"], c["text"], c["words"], c["boundary_kind"]) for c in want["chunks"]])
        self.assertEqual(z.chunk_plans_from_specs(make_plan("a2")[0]), {})


class ZStageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.run = f"{self.tmp}/melos/run_01"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _tts(self, g=None, **kw):
        plan, kp = make_plan("b1b")
        g = g or Gens()
        out = z.run_tts_stage(self.run, "b1b", plan, generators=g.gens(), **kw)
        return plan, kp, g, out

    def test_chunk_entries_parent_aggregate_exact_parent_wav_and_artifacts(self):
        plan, kp, g, out = self._tts()
        seg = _res(self.run)["segments"]
        for cid in ("full_story_part2_c1_k1", "full_story_part2_c1_k2"):
            self.assertEqual(seg[cid]["status"], "OK")
            self.assertEqual(seg[cid]["role"], "FULL_STORY")                               # C4: chunk idがFULL_STORYに解決
            self.assertTrue(seg[cid]["connected_speech_enabled"])
            self.assertEqual(seg[cid]["chunk_tts"]["parent_id"], "full_story_part2_c1")
            self.assertEqual(seg[cid]["reuse_key"]["chunk_tts"]["index"], seg[cid]["chunk_tts"]["index"])
        par = seg["full_story_part2_c1"]
        self.assertEqual(par["status"], "OK")
        self.assertEqual(par["voice"], seg["full_story_part2_c1_k1"]["voice"])             # I7
        self.assertNotIn("-", [par["style"]["instruction_label"]])
        self.assertTrue(par["canonical_text"].startswith("Alpha"))
        nd = f"{self.run}/b1b/narration"
        core.verify_raw_parent(f"{nd}/full_story_part2_c1.wav", [f"{nd}/full_story_part2_c1_k{i}.wav" for i in (1, 2)])
        self.assertTrue(os.path.exists(f"{self.run}/b1b/audit/chunk_plan_b1b.json"))
        ev = json.load(open(f"{self.run}/b1b/audit/chunk_tts_evidence_b1b.json", encoding="utf-8"))
        self.assertEqual(ev["parents"]["full_story_part2_c1"]["chunk_count"], 2)
        self.assertEqual(g.calls.count("full_story_part2_c1_k1"), 1)
        self.assertNotIn("full_story_part2_c1", g.calls)
        self.assertEqual(out["statuses"]["full_story_part2_c1_k2"], "OK")
        self.assertNotIn("full_story_part2_c1", out["statuses"])                            # statusesはspec(chunk)単位。親は集約entry

    def test_failed_chunk_does_not_stop_later_chunks_parent_written_not_validated_and_resume_regenerates_only_it(self):
        plan, kp = make_plan("b1b")
        g = Gens(fail={"full_story_part2_c1_k1"})
        out = z.run_tts_stage(self.run, "b1b", plan, generators=g.gens())
        self.assertIn("full_story_part2_c1_k2", g.calls)                                    # R1: 失敗後も続行
        seg = _res(self.run)["segments"]
        self.assertEqual(seg["full_story_part2_c1"]["status"], core.PARENT_STATUS_NOT_ALL_VALIDATED)
        with self.assertRaises(z.FamilyZTtsResultsIncompleteStop):
            z.assert_tts_results_complete(f"{self.run}/b1b", z.required_clip_ids(plan, []))
        g2 = Gens()
        z.run_tts_stage(self.run, "b1b", plan, generators=g2.gens())
        self.assertEqual(g2.calls, ["full_story_part2_c1_k1"])                              # OK済みclip/chunkは再利用。失敗chunkだけ再生成
        self.assertEqual(_res(self.run)["segments"]["full_story_part2_c1"]["status"], "OK")

    def test_only_clips_parent_id_expands_to_chunks_and_chunk_id_direct(self):
        plan, kp = make_plan("b1b")
        z.run_tts_stage(self.run, "b1b", plan, generators=Gens().gens())
        g = Gens()
        z.run_tts_stage(self.run, "b1b", plan, generators=g.gens(), only_clips={"full_story_part2_c1"})
        self.assertEqual(g.calls, [])                                                       # 親id指定→全chunk対象(いずれもreuse_key一致で再利用)
        for fn in ("full_story_part2_c1_k2",):
            os.remove(f"{self.run}/b1b/narration/{fn}.wav")
        g = Gens()
        z.run_tts_stage(self.run, "b1b", plan, generators=g.gens(), only_clips={"full_story_part2_c1_k2"})
        self.assertEqual(g.calls, ["full_story_part2_c1_k2"])

    def test_text_change_regenerates_only_changed_chunk(self):
        plan, kp = make_plan("b1b")
        z.run_tts_stage(self.run, "b1b", plan, generators=Gens().gens())
        paras2 = list(PARAS)
        paras2[3] = paras2[3].replace("Xi omicron", "Xi omicrons")
        st = [dict(c) for c in story()]
        for c in st:
            if c["id"] == "full_story_part2_c1":
                c["text"] = core.normalize_for_tts(" ".join(paras2[1:4]))
        cps = core.plan_z_level(st, paras2, "b1b")
        plan2 = z.build_level_plan("b1b", st, "preview text", {1: "c1 text", 2: "c2 text", 3: "c3 text"}, make_plan("b1b")[1],
                                   "The Three-Day Promise", chunk_plans=cps)
        g = Gens()
        z.run_tts_stage(self.run, "b1b", plan2, generators=g.gens())
        self.assertEqual(g.calls, ["full_story_part2_c1_k2"])                               # 変わった段落を含むchunkだけ

    def test_old_planner_version_in_cached_entry_is_not_reused(self):
        plan, kp = make_plan("b1b")
        z.run_tts_stage(self.run, "b1b", plan, generators=Gens().gens())
        p = f"{self.run}/b1b/audit/tts_generation_results.json"
        d = json.load(open(p, encoding="utf-8"))
        d["segments"]["full_story_part2_c1_k1"]["reuse_key"]["chunk_tts"]["planner_version"] = "chunk_tts_v0"
        json.dump(d, open(p, "w", encoding="utf-8"))
        g = Gens()
        z.run_tts_stage(self.run, "b1b", plan, generators=g.gens())
        self.assertEqual(g.calls, ["full_story_part2_c1_k1"])                               # I1相当: reuse_keyの版不一致→再生成

    def test_resume_replan_prohibition_stops_before_any_call(self):
        plan, kp = make_plan("b1b")
        z.run_tts_stage(self.run, "b1b", plan, generators=Gens().gens())
        p = f"{self.run}/b1b/audit/chunk_plan_b1b.json"
        d = json.load(open(p, encoding="utf-8"))
        d["plans"]["full_story_part2_c1"]["chunks"][0]["text"] += " tampered"
        json.dump(d, open(p, "w", encoding="utf-8"))
        g = Gens()
        with self.assertRaises(core.ChunkIntegrityError):
            z.run_tts_stage(self.run, "b1b", plan, generators=g.gens())
        self.assertEqual(g.calls, [])

    def test_dry_run_has_no_side_effects_with_chunk_plan(self):
        plan, kp = make_plan("b1b")
        g = Gens()
        out = z.run_tts_stage(self.run, "b1b", plan, generators=g.gens(), dry_run=True)
        self.assertEqual(out["writes"], 0)
        self.assertFalse(os.path.exists(self.run))
        self.assertIn("full_story_part2_c1_k1", [p["clip_id"] for p in out["planned"]])


class ZGateAndAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.run = f"{self.tmp}/melos/run_01"
        # 共有Productionのshell/番号wav(untrackedで環境により無い)の代わりに、同名の合成toneを一時dirに置いてprovisionの入力にする
        import er003_v1_n3_01_assemble as asm
        shared = f"{self.tmp}/shared_narration"
        for src_name in list(z.SHELL_ASSET_SOURCES.values()) + list(z.NUMBER_ASSET_SOURCES.values()):
            _tone(f"{shared}/{src_name}", 0.4)
        self._patch = mock.patch.object(asm, "B1_SHARED_SOURCE_DIR", shared)
        self._patch.start()
        self._patch_kp = mock.patch.object(asm, "verify_key_phrase_source_gate")   # KP source gate(本件の対象外)だけ無効化。Audio Validation本体は実物
        self._patch_kp.start()

    def tearDown(self):
        self._patch_kp.stop()
        self._patch.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _prepare(self, **gk):
        plan, kp = make_plan("b1b")
        z.run_tts_stage(self.run, "b1b", plan, generators=Gens(**gk).gens())
        z.provision_shell_assets(self.run, "b1b", kp_count=1)
        return plan, kp

    def test_gate_covers_chunk_ids_speed_profile_and_rejects_slowdown_on_narrator_chunk(self):
        plan, kp = self._prepare()
        with mock.patch("er003_v1_n3_01_assemble.verify_episode_audio_validation_gate") as shared:
            res = z.run_audio_gate(self.run, "b1b", plan, SHELL, article_text="a")
        self.assertIn("full_story_part2_c1_k1", res["z_speed_profile"]["clips"])            # R2: chunk idも速度Gateの対象
        self.assertTrue(res["z_speed_profile"]["clips"]["full_story_part2_c1_k2"]["ok"])
        shared.assert_called_once()
        # Adv narrator chunkに速度後処理が掛かっていればSTOP
        d = _res(self.run)
        d["segments"]["full_story_part2_c1_k2"]["slowdown_applied"] = True
        json.dump(d, open(f"{self.run}/b1b/audit/tts_generation_results.json", "w", encoding="utf-8"))
        with mock.patch("er003_v1_n3_01_assemble.verify_episode_audio_validation_gate"):
            with self.assertRaises(z.FamilyZSlowdownGateStop):
                z.run_audio_gate(self.run, "b1b", plan, SHELL, article_text="a")

    def test_real_shared_gate_passes_parent_and_chunks_and_blocks_failed_chunk(self):
        import er003_v1_n3_01_assemble as asm
        plan, kp = self._prepare()
        z.run_audio_gate(self.run, "b1b", plan, SHELL, article_text="a", skip_shared_gate=True)
        asm.verify_episode_audio_validation_gate(f"{self.run}/b1b", "B1")                   # 親+chunk+他entryを実Gateが通す
        shutil.rmtree(self.run, ignore_errors=True)
        plan, kp = self._prepare(fail={"full_story_part2_c1_k1"})
        with self.assertRaises(z.FamilyZTtsResultsIncompleteStop):
            z.run_audio_gate(self.run, "b1b", plan, SHELL, article_text="a")

    def test_human_approval_then_gate_refreshes_parent_entry_and_wav(self):
        import er003_v1_n3_01_assemble as asm
        plan, kp = self._prepare(fail={"full_story_part2_c1_k1"})
        d = _res(self.run)
        k1 = d["segments"]["full_story_part2_c1_k1"]
        self.assertEqual(d["segments"]["full_story_part2_c1"]["status"], core.PARENT_STATUS_NOT_ALL_VALIDATED)
        asm.record_human_approval(f"{self.run}/b1b", "full_story_part2_c1_k1", k1["canonical_text"])
        os.remove(f"{self.run}/b1b/narration/full_story_part2_c1.wav")
        z.run_audio_gate(self.run, "b1b", plan, SHELL, article_text="a", skip_shared_gate=True)      # M2(c): gate冒頭でrefresh+保存
        par = _res(self.run)["segments"]["full_story_part2_c1"]
        self.assertEqual(par["status"], "OK")
        self.assertEqual(par["chunk_tts"]["human_approved_chunks"], ["full_story_part2_c1_k1"])
        self.assertTrue(os.path.exists(f"{self.run}/b1b/narration/full_story_part2_c1.wav"))
        asm.verify_episode_audio_validation_gate(f"{self.run}/b1b", "B1")

    def test_assembly_chunk_gain_gap_timeline_and_pages(self):
        plan, kp = self._prepare(lr={"full_story_part2_c1_k2"})
        story_clips = story()
        tl = z.run_assembly(self.run, "b1b", story_clips, kp, chunk_plans=z.chunk_plans_from_specs(plan))
        names = tl["sequence_order"]
        self.assertIn("full_story_part2_c1", names)
        self.assertFalse(any("_k" in n for n in names))                                      # timelineは親1エントリ
        ct = tl["chunk_tts"]["parents"]["full_story_part2_c1"]
        self.assertEqual(ct["chunk_ids"], ["full_story_part2_c1_k1", "full_story_part2_c1_k2"])
        a, b = ct["gap_offsets_in_episode_s"][0]
        self.assertAlmostEqual(b - a, 0.2, places=3)
        self.assertAlmostEqual(ct["gap_offsets_in_part_s"][0][1] - ct["gap_offsets_in_part_s"][0][0], 0.2, places=3)
        self.assertNotIn("gain", tl["gain_report"]["full_story_part2_c1"])                    # I7
        self.assertEqual(len(ct["gains"]), 2)
        # 実測: 親のtimeline区間長 == (chunk長合計 + 0.2秒) をstereo48kのサンプル数で確認(headroom適用前の整数一致)
        part = [e for e in tl["timeline"] if e["part"] == "full_story_part2_c1"][0]
        nd = f"{self.run}/b1b/narration"
        lens = [len(core.read_pcm16(f"{nd}/full_story_part2_c1_k{i}.wav")) for i in (1, 2)]
        self.assertAlmostEqual(part["duration_seconds"], (sum(lens) + 4800) / 24000, places=2)
        # narrator後の既存0.5秒が最後のchunkの後に1回だけ入る
        seq = tl["timeline"]
        idx = [i for i, e in enumerate(seq) if e["part"] == "full_story_part2_c1"][0]
        self.assertEqual(seq[idx + 1]["part"], "_silence_0.5")
        # ページ行: 親行はvoice/styleが「-」でなく、chunkのLocal Rewrite注記が親行に出る
        rows, _, _, _ = z.build_page_rows(self.run, "b1b", "x/", f"{self.tmp}/aud")
        row = [r for r in rows if r["clip_id"] == "full_story_part2_c1"][0]
        self.assertNotEqual(row["voice"], "-")
        self.assertNotEqual(row["style"], "-")
        self.assertTrue(row["script"].startswith("Alpha"))
        self.assertTrue(any("full_story_part2_c1_k2" in n and "Local Rewrite" in n for n in row["notes"]))

    def test_assembly_stops_if_parent_wav_not_raw_concat_and_without_chunk_plans_uses_legacy_path(self):
        plan, kp = self._prepare()
        nd = f"{self.run}/b1b/narration"
        core.write_pcm16(f"{nd}/full_story_part2_c1.wav", core.read_pcm16(f"{nd}/full_story_part2_c1.wav")[:-300])
        with self.assertRaises(core.ChunkIntegrityError):
            z.run_assembly(self.run, "b1b", story(), kp, chunk_plans=z.chunk_plans_from_specs(plan))
        # chunk_plansを渡さない(従来呼出)と親wavを従来どおり1 clipとして組み立てる(後方互換)
        z.run_assembly(self.run, "b1b", story(), kp)

    def test_assembly_stops_when_chunk_set_mismatches_plan(self):
        plan, kp = self._prepare()
        d = _res(self.run)
        del d["segments"]["full_story_part2_c1_k2"]
        json.dump(d, open(f"{self.run}/b1b/audit/tts_generation_results.json", "w", encoding="utf-8"))
        with self.assertRaises(core.ChunkIntegrityError):
            z.run_assembly(self.run, "b1b", story(), kp, chunk_plans=z.chunk_plans_from_specs(plan))


class ZMiscTests(unittest.TestCase):
    def test_warn_entry_maps_chunk_to_parent_clip_row(self):
        self.assertEqual(z._warn_entry_to_clip_id("segments/full_story_part2_c1_k2"), "full_story_part2_c1")
        self.assertEqual(z._warn_entry_to_clip_id("segments/full_story_part2_c1"), "full_story_part2_c1")
        self.assertEqual(z._warn_entry_to_clip_id("segments/comment_1"), "comment_1")
        self.assertEqual(z._warn_entry_to_clip_id("key_phrases/1/english"), "kp1_en")

    def test_strict_clip_id_re_unchanged_and_chunk_re_separate(self):
        self.assertIsNone(z._CLIP_ID_RE.fullmatch("full_story_part2_c1_k1"))
        self.assertIsNotNone(z._CLIP_OR_CHUNK_ID_RE.fullmatch("full_story_part2_c1_k1"))
        self.assertIsNotNone(z._CLIP_OR_CHUNK_ID_RE.fullmatch("full_story_part2_c1"))
        self.assertIsNone(z._CLIP_OR_CHUNK_ID_RE.fullmatch("full_story_part2_c1_k0"))
        self.assertEqual(z._CLIP_OR_CHUNK_ID_RE.fullmatch("full_story_part2_c13_k4").group(1, 2), ("2", "13"))
        with self.assertRaises(z.FamilyZAudioStop):                                            # 入力検証は厳密なまま(親clip idだけ)
            z.build_level_plan("b1b", [{"id": "full_story_part1_c1_k1", "voice": "narrator", "text": "x"}], "p", {1: "a", 2: "b", 3: "c"},
                               [{"rank": 1, "used_form": "u", "japanese_gloss": "g", "japanese_gloss_tts": "g"}], "T")
        self.assertEqual(z.comment_after_segment_ids(story()), {"2": "full_story_part1_c2", "3": "full_story_part2_c1"})

    def test_part_to_clip_id_unchanged(self):
        self.assertEqual(z.part_to_clip_id("full_story_part2_c1"), "full_story_part2_c1")
        self.assertIsNone(z.part_to_clip_id("full_story_part2_c1_k1"))


if __name__ == "__main__":
    unittest.main()
