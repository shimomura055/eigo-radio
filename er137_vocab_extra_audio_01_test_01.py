# -*- coding: utf-8 -*-
"""er137_vocab_extra_audio_01(Vocabulary掲載項目の英語音声、SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_02C)のオフラインtest。
mock TTS/ASR・課金0・実API呼出なし。実行: .venv/Scripts/python.exe -m unittest er137_vocab_extra_audio_01_test_01 -v
確認: (1)KP重複はTTS 0で再利用・②だけ生成 (2)resume=API 0 (3)KP3V/Whisper事前確認など既存安全装置が役割vocab_extra_englishにも掛かる
(4)失敗=Gate BLOCK/export STOP/article付与STOP(fail-closed)、Human Review承認後は通る (5)既存KP wav・vocab_confirmed.json・確定recordのsha不変
(6)X/Y/Zの3経路(Yはxr共通関数、Zはkind=kp_en spec)が同じ契約を通る (7)旧results・②無し・vocab_confirmed無しは従来どおり"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401  Production監査ログへの追記を隔離
import hashlib
import json
import os
import re
import shutil
import tempfile
import unittest
import wave
from unittest import mock

import er137_vocab_extra_audio_01 as vx
import er019_family_x_audio_production_runner_01 as xr
import er003_v1_n3_01_assemble as asm

SRC_RUN = "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01"


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _tone(path, seconds=0.6, hz=330):
    import math
    import struct
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sr = 24000
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(3000 * math.sin(2 * math.pi * hz * i / sr))) for i in range(int(sr * seconds))))


def _ok_entry(text, path):
    return {"status": "OK", "path": path, "sha256": _sha(path), "canonical_text": text, "text": text, "disfluency_checked": True}


def make_level(tmp, level="b1b"):
    """実run(月のしわ)のkey_phrases(確定record・vocab_confirmed・KP)を複製し、KP3件のwav+results(key_phrases)を作る。"""
    out = f"{tmp}/{level}"
    shutil.copytree(f"{SRC_RUN}/{level}/key_phrases", f"{out}/key_phrases")
    kp = json.load(open(f"{out}/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
    kpres = {}
    for it in kp["items"]:
        w = f"{out}/narration/kp{it['rank']}_en.wav"
        _tone(w, 0.5, 200 + 40 * it["rank"])
        kpres[str(it["rank"])] = {"english": _ok_entry(it["used_form"], w)}
    os.makedirs(f"{out}/audit", exist_ok=True)
    json.dump({"segments": {}, "key_phrases": kpres, "style_version": xr.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION},
              open(f"{out}/audit/tts_generation_results.json", "w", encoding="utf-8"), ensure_ascii=False)
    return out, kp


class Gen:
    """_kp_english_generate_fnの代替。呼出を記録し、wavを書いてOK(またはfail_terms=STOPPED)を返す。"""

    def __init__(self, fail_terms=()):
        self.calls, self.fail_terms = [], set(fail_terms)

    def __call__(self, style_profile, level, tts_backend, used_form, wav_path):
        def fn():
            self.calls.append(used_form)
            if used_form in self.fail_terms:
                return {"status": "STOPPED", "reason": "mock tts failure", "disfluency_checked": True}
            _tone(wav_path, 0.7, 500)
            return _ok_entry(used_form, wav_path)
        return fn, None


class X_Y_PathTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out, self.kp = make_level(self.tmp)
        self.nd = f"{self.out}/narration"
        self.p1 = mock.patch.object(xr.kp_vote, "vote_enabled", return_value=False)   # KP3V有効時の再利用ゲートは別testで確認
        self.p1.start()
        self.p2 = mock.patch.object(xr.kp_vote, "guard_whisper", side_effect=lambda fn, label: fn)
        self.p2.start()

    def tearDown(self):
        mock.patch.stopall()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _gen(self, gen, cached=None):
        with mock.patch.object(xr, "_kp_english_generate_fn", gen):
            return xr._generate_vocab_extra_segments(self.kp, self.nd, cached, level="b1b")

    def test_split_five_items_three_kp_two_extra(self):
        vocab = vx.load_level_vocab(f"{self.out}/key_phrases")
        sp = vx.split_vocab(vocab, self.kp["items"])
        self.assertEqual(len(sp), 5)
        self.assertEqual([s["term"] for s in sp if s["kp_rank"] is not None], ["way off", "porous", "culprit"])
        self.assertEqual([s["term"] for s in vx.extras_of(sp)], ["over its entire history", "puzzling"])

    def test_only_extras_generated_and_kp_untouched(self):
        kp_sha = {r: _sha(f"{self.nd}/kp{r}_en.wav") for r in (1, 2, 3)}
        vc_sha = _sha(f"{self.out}/key_phrases/vocab_confirmed.json")
        rec_files = [f for f in os.listdir(f"{self.out}/key_phrases") if os.path.isfile(f"{self.out}/key_phrases/{f}")]
        rec_sha = {f: _sha(f"{self.out}/key_phrases/{f}") for f in rec_files}
        gen = Gen()
        res = self._gen(gen)
        self.assertEqual(gen.calls, ["over its entire history", "puzzling"])         # KP重複3件はTTS 0
        self.assertEqual(sorted(res), ["v2", "v5"])
        for v in res.values():
            e = v["vocab_extra_english"]
            self.assertEqual(e["status"], "OK")
            self.assertTrue(os.path.exists(f"{self.nd}/vocab_extra_{e['vocab_index']}_en.wav"))
        self.assertEqual({r: _sha(f"{self.nd}/kp{r}_en.wav") for r in (1, 2, 3)}, kp_sha)   # 既存KP音声は再生成されない
        self.assertEqual(_sha(f"{self.out}/key_phrases/vocab_confirmed.json"), vc_sha)
        self.assertEqual({f: _sha(f"{self.out}/key_phrases/{f}") for f in rec_files}, rec_sha)

    def test_resume_is_api_zero(self):
        res = self._gen(Gen())
        gen2 = Gen()
        res2 = self._gen(gen2, cached={"vocab_extra": res, "style_version": xr.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION})
        self.assertEqual(gen2.calls, [])
        self.assertTrue(all(v["vocab_extra_english"].get("reused_from_previous_run") for v in res2.values()))

    def test_reuse_goes_through_kp3v_reuse_gate_for_new_role(self):
        res = self._gen(Gen())
        with mock.patch.object(xr.kp_vote, "vote_enabled", return_value=True), \
                mock.patch.object(xr.kp_vote, "kp_vote_reuse_ok", return_value={"ok": False, "action": "regen", "reason": "no_evidence"}) as m:
            gen3 = Gen()
            self._gen(gen3, cached={"vocab_extra": res})
        self.assertEqual(m.call_count, 2)       # KP英語と同じ再利用ゲートが②にも掛かる(証跡なし=再生成)
        self.assertEqual(len(gen3.calls), 2)

    def test_whisper_guard_applies_to_new_role(self):
        mock.patch.stopall()
        with mock.patch.object(xr.kp_vote, "guard_whisper", side_effect=lambda fn, label: fn) as g, \
                mock.patch.object(xr.kp_vote, "vote_enabled", return_value=False):
            with mock.patch.object(xr, "_kp_english_generate_fn", Gen()):
                xr._generate_vocab_extra_segments(self.kp, self.nd, None, level="b1b")
        self.assertEqual([c.args[1] for c in g.call_args_list], ["kpv2_vocab_extra_english", "kpv5_vocab_extra_english"])

    def test_no_vocab_confirmed_or_no_extra_means_no_key(self):
        os.remove(f"{self.out}/key_phrases/vocab_confirmed.json")
        gen = Gen()
        self.assertEqual(self._gen(gen), {})
        self.assertEqual(gen.calls, [])
        self.assertEqual(xr._generate_vocab_extra_segments(None, self.nd, None, level="b1b"), {})

    def test_gloss_hr_pending_writes_stopped_entries_zero_api(self):
        gen = Gen()
        with mock.patch.object(xr, "_gloss_alignment_hr_unresolved", return_value=[{"rank": 1}]):
            res = self._gen(gen)
        self.assertEqual(gen.calls, [])
        self.assertTrue(all(v["vocab_extra_english"]["status"] == "STOPPED" for v in res.values()))

    def test_y_layout_vocab_dir_is_found_and_not_silently_skipped(self):
        """Y/Zはvocab_confirmed.jsonが<run>/key_phrases/<level>にあり、<level>/key_phrases(assets copy)には無い。置き場の違いで0件扱いにならない。"""
        run = f"{self.tmp}/yrun"
        lvl = f"{run}/b1b"
        shutil.copytree(f"{self.out}/key_phrases", f"{run}/key_phrases/b1b")
        os.makedirs(f"{lvl}/key_phrases")
        shutil.copy(f"{run}/key_phrases/b1b/keywords_canonicalized.json", f"{lvl}/key_phrases/keywords_canonicalized.json")
        os.makedirs(f"{lvl}/narration")
        self.assertEqual(vx.find_kp_dir(lvl, "b1b"), f"{run}/key_phrases/b1b")
        self.assertEqual(vx.find_kp_dir(self.out, "b1b"), f"{self.out}/key_phrases")                 # X配置
        self.assertIsNone(vx.find_kp_dir(f"{self.tmp}/none/b1b", "b1b"))                              # vocab無し=対象外
        gen = Gen()
        with mock.patch.object(xr, "_kp_english_generate_fn", gen):
            res = xr._generate_vocab_extra_segments(self.kp, f"{lvl}/narration", None, level="b1b")
        self.assertEqual(sorted(res), ["v2", "v5"])
        self.assertEqual(gen.calls, ["over its entire history", "puzzling"])

    def test_y_audio_uses_same_shared_function_in_both_levels(self):
        src = open("er121_family_y_audio_01.py", encoding="utf-8").read()
        self.assertEqual(len(re.findall(r"xr\._generate_vocab_extra_segments\(kp, narration_dir, cached, level=\"(?:b1b|a2)\"", src)), 2)
        self.assertIn("vocab_extra=vocab_extra", src)
        self.assertIn("xr._vx_gate_hook(out_dir, level)", src)

    def test_x_runner_calls_in_both_levels_and_persists_key_only_when_present(self):
        src = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        self.assertEqual(src.count("_generate_vocab_extra_segments(kp, narration_dir, _cached, level="), 2)
        self.assertEqual(src.count('**({"vocab_extra": vocab_extra_results} if vocab_extra_results else {})'), 2)
        self.assertEqual(src.count("_vx_gate_hook(out_dir,"), 2)


class GateExportFailClosedTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out, self.kp = make_level(self.tmp)
        self.nd = f"{self.out}/narration"
        mock.patch.object(xr.kp_vote, "vote_enabled", return_value=False).start()
        mock.patch.object(xr.kp_vote, "guard_whisper", side_effect=lambda fn, label: fn).start()
        mock.patch.object(asm, "verify_key_phrase_source_gate", return_value=None).start()   # 本文照合Gateは本testの対象外(既存・不変)

    def tearDown(self):
        mock.patch.stopall()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _save(self, vx_res):
        p = f"{self.out}/audit/tts_generation_results.json"
        d = json.load(open(p, encoding="utf-8"))
        d["vocab_extra"] = vx_res
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)

    def _run(self, gen):
        with mock.patch.object(xr, "_kp_english_generate_fn", gen):
            res = xr._generate_vocab_extra_segments(self.kp, self.nd, None, level="b1b")
        self._save(res)
        return res

    def test_success_exports_five_mp3_and_article_gets_audio_for_all(self):
        self._run(Gen())
        asm.verify_episode_audio_validation_gate(self.out, "B1")              # 既存Gateを通る
        doc = vx.gate_hook(self.out, f"{self.out}/key_phrases", "b1b")
        self.assertTrue(doc["complete"])
        self.assertEqual([i["source"] for i in doc["items"]], ["kp_reuse", "vocab_extra_generated", "kp_reuse", "kp_reuse", "vocab_extra_generated"])
        for i in doc["items"]:
            self.assertGreater(i["dur"], 0)
            self.assertEqual(_sha(f"{self.out}/vocab_audio/{i['mp3']}"), i["sha256"])
        article = {"levels": {"adv": {"vocab": [{"heading": h, "fields": []} for h in ["way off", "over its entire history", "porous", "culprit", "puzzling"]]}}}
        vx.apply_to_article(article, {"b1b": doc})
        self.assertEqual(vx.validate_article(article), [])
        self.assertEqual(len(article["levels"]["adv"]["vocab"]), 5)

    def test_validate_article_detects_missing_audio_and_missing_file(self):
        self._run(Gen())
        doc = vx.gate_hook(self.out, f"{self.out}/key_phrases", "b1b")
        article = {"levels": {"adv": {"vocab": [{"heading": i["term"]} for i in doc["items"]]}}}
        vx.apply_to_article(article, {"b1b": doc})
        pub = f"{self.tmp}/pub"
        os.makedirs(f"{pub}/audio")
        self.assertEqual(len(vx.validate_article(article, public_dir=pub)), 5)       # fileが公開dirに無い=全件検出
        for i in doc["items"]:
            shutil.copy(f"{self.out}/vocab_audio/{i['mp3']}", f"{pub}/audio/{i['mp3']}")
        self.assertEqual(vx.validate_article(article, public_dir=pub), [])
        del article["levels"]["adv"]["vocab"][2]["audio"]
        self.assertEqual(len(vx.validate_article(article)), 1)

    def test_tts_failure_blocks_gate_export_and_article(self):
        self._run(Gen(fail_terms={"puzzling"}))
        with self.assertRaises(RuntimeError) as cm:
            asm.verify_episode_audio_validation_gate(self.out, "B1")
        self.assertIn("kpv5_vocab_extra_english=STOPPED", str(cm.exception))
        self.assertNotIn("kpv2_", str(cm.exception))
        doc = vx.export_level(self.out, f"{self.out}/key_phrases", "b1b", strict=False)
        self.assertFalse(doc["complete"])
        self.assertIn("kpv5_vocab_extra_english=STOPPED", doc["errors"])
        with self.assertRaises(vx.VocabAudioIncomplete):
            vx.export_level(self.out, f"{self.out}/key_phrases", "b1b")
        article = {"levels": {"adv": {"vocab": [{"heading": "puzzling"}]}}}
        with self.assertRaises(vx.VocabAudioIncomplete):
            vx.apply_to_article(article, {"b1b": doc})                              # 音声なし掲載を作らない
        self.assertNotIn("audio", article["levels"]["adv"]["vocab"][0])

    def test_human_approval_unblocks_exactly_the_approved_segment(self):
        self._run(Gen(fail_terms={"puzzling"}))
        os.makedirs(f"{self.out}/audit", exist_ok=True)
        text = "puzzling"
        _tone(f"{self.nd}/vocab_extra_5_en.wav", 0.7, 777)     # 人間が差替え/承認した音声(承認は本文sha一致で有効)
        json.dump({"kpv5_vocab_extra_english": {"canonical_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}},
                  open(asm.human_approval_path(self.out), "w", encoding="utf-8"))
        asm.verify_episode_audio_validation_gate(self.out, "B1")
        doc = vx.export_level(self.out, f"{self.out}/key_phrases", "b1b", strict=False)
        self.assertEqual(doc["errors"], [])
        self.assertTrue(doc["complete"])

    def test_missing_results_for_extras_is_stopped_before_assembly(self):
        p = f"{self.out}/audit/tts_generation_results.json"
        self.assertNotIn("vocab_extra", json.load(open(p, encoding="utf-8")))
        with self.assertRaises(vx.VocabAudioIncomplete) as cm:
            vx.assert_results_complete(self.out, f"{self.out}/key_phrases")
        self.assertIn("kpv2_vocab_extra_english=MISSING", str(cm.exception))

    def test_legacy_without_vocab_confirmed_is_untouched(self):
        os.remove(f"{self.out}/key_phrases/vocab_confirmed.json")
        vx.assert_results_complete(self.out, f"{self.out}/key_phrases")             # raiseしない
        d = vx.gate_hook(self.out, f"{self.out}/key_phrases", "b1b")
        self.assertTrue(d.get("skipped"))
        self.assertFalse(os.path.exists(f"{self.out}/vocab_audio"))

    def test_gate_unchanged_when_key_absent(self):
        asm.verify_episode_audio_validation_gate(self.out, "B1")                    # vocab_extraキー無し=従来どおり通る

    def test_export_idempotent_and_wav_tamper_detected(self):
        self._run(Gen())
        d1 = vx.export_level(self.out, f"{self.out}/key_phrases", "b1b")
        d2 = vx.export_level(self.out, f"{self.out}/key_phrases", "b1b")
        self.assertEqual([i["sha256"] for i in d1["items"]], [i["sha256"] for i in d2["items"]])
        _tone(f"{self.nd}/vocab_extra_2_en.wav", 0.9, 999)                          # entry.sha256と食い違う(stale)
        d3 = vx.export_level(self.out, f"{self.out}/key_phrases", "b1b", strict=False)
        self.assertIn("kpv2_vocab_extra_english=WAV_SHA_MISMATCH", d3["errors"])


class ZPathTest(unittest.TestCase):
    def setUp(self):
        import er063_family_z_audio_01 as z
        import er063_family_z_audio_01_test_01 as zt
        self.z, self.zt = z, zt
        self.tmp = tempfile.mkdtemp()
        self.run = f"{self.tmp}/melos/run_01"
        self.plan, _, _ = zt.make_plan("b1b")
        self.specs = z.vocab_extra_specs("b1b", [{"vocab_index": 2, "term": "over its entire history", "candidate_id": "c2"},
                                                   {"vocab_index": 5, "term": "puzzling", "candidate_id": "c5"}])

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_specs_use_kp_en_contract_and_stay_out_of_plan(self):
        for s in self.specs:
            self.assertEqual((s.kind, s.role_key, s.voice), ("kp_en", "KP_EN", "Aoede"))
            self.assertNotIn(s.clip_id, [p.clip_id for p in self.plan])

    def test_generate_reuse_and_gate_lookup(self):
        z = self.z
        out = z.run_tts_stage(self.run, "b1b", self.plan, generators=self.zt.fake_generators(), vocab_specs=self.specs)
        self.assertEqual(out["statuses"]["vocab_extra_2_en"], "OK")
        self.assertEqual(out["statuses"]["vocab_extra_5_en"], "OK")
        data = json.load(open(f"{self.run}/b1b/audit/tts_generation_results.json", encoding="utf-8"))
        self.assertEqual(sorted(data["vocab_extra"]), ["v2", "v5"])
        self.assertEqual(z._lookup_entry(data, "vocab_extra_5_en")["canonical_text"], "puzzling")
        # resume: 生成器が呼ばれたら失敗(=API 0)
        boom = {k: (lambda s, p: (_ for _ in ()).throw(AssertionError("API call on resume"))) for k in self.zt.fake_generators()}
        out2 = z.run_tts_stage(self.run, "b1b", self.plan, generators=boom, vocab_specs=self.specs)
        self.assertEqual(out2["statuses"]["vocab_extra_2_en"], "OK")
        data2 = json.load(open(f"{self.run}/b1b/audit/tts_generation_results.json", encoding="utf-8"))
        self.assertTrue(data2["vocab_extra"]["v2"]["vocab_extra_english"].get("reused_from_previous_run"))

    def test_failure_is_visible_to_stage_and_m2_gate(self):
        z = self.z
        out = z.run_tts_stage(self.run, "b1b", self.plan, generators=self.zt.fake_generators(fail_clips={"vocab_extra_5_en"}), vocab_specs=self.specs)
        self.assertEqual(out["statuses"]["vocab_extra_5_en"], "STOPPED")           # er026 stage_ttsはstatus!=OKでFamilyZTtsClipFailedStop
        ids = [s.clip_id for s in self.plan] + [s.clip_id for s in self.specs]
        with self.assertRaises(z.FamilyZTtsResultsIncompleteStop) as cm:
            z.assert_tts_results_complete(f"{self.run}/b1b", ids)
        self.assertIn("vocab_extra_5_en", str(cm.exception))

    def test_runner_passes_vocab_specs_to_tts_and_gate(self):
        src = open("er026_family_z_fiction_production_runner_01.py", encoding="utf-8").read()
        self.assertIn('story_key=ctx.slug, vocab_specs=inp.get("vocab_specs"))', src)
        self.assertIn('article_text=inp["article_text"], vocab_specs=inp.get("vocab_specs"))', src)
        self.assertIn("_vx.gate_hook(", src)


if __name__ == "__main__":
    unittest.main()
