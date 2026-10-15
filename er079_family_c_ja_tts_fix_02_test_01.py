# -*- coding: utf-8 -*-
"""FAMILY-C-JA-TTS-PRODUCTION-FIX-01 委任_02: Family C 日本語Section TTS言語経路 + reuse_from由来照合の決定的test(API 0、mock)。
R1(自己参照排除)・R2(受理経路のコピー)・R3(.ok削除)・R9(非en言語ガード/language伝達)・英語回帰・Comment再利用/強制再生成。"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er013_family_c_production_runner_01 as runner

JA_OLD = "主人公は小さな銀色の箱を持っています。"
JA_NEW = "主人公は大きな金色の箱を抱えています。"


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def file_sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def mk_wav(path, payload=b"RIFFdummyWAVE"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(payload)


def mk_src(root, name, payload, meta=None, audit_entry=None, ok=True):
    """reuse_from側(root)にaudio/<name>(+.ok+meta)とaudit/tts_generation_results.jsonを作る。"""
    wav = f"{root}/audio/{name}"
    mk_wav(wav, payload)
    if ok:
        open(wav + ".ok", "w").write("ok")
    if meta is not None:
        json.dump(meta, open(wav + ".ok.meta.json", "w", encoding="utf-8"))
    if audit_entry is not None:
        ap = f"{root}/audit/tts_generation_results.json"
        os.makedirs(os.path.dirname(ap), exist_ok=True)
        d = json.load(open(ap, encoding="utf-8")) if os.path.exists(ap) else {"segments": {}, "key_phrases": {}}
        d["segments"][name.removesuffix(".wav")] = audit_entry
        json.dump(d, open(ap, "w", encoding="utf-8"), ensure_ascii=False)
    return wav


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.src = f"{self.tmp}/src"
        self.dst_audio = f"{self.tmp}/out/audio"
        os.makedirs(self.dst_audio, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def budget(self):
        return runner.BudgetTracker(100.0, f"{self.tmp}/log.jsonl")


class ProvenanceCheckTests(Base):
    def test_legacy_upgraded_meta_is_not_provenance_evidence(self):
        """R1: upgraded_from_legacy_ok:true のmetaは、text sha256が現行と一致していても由来証拠にしない。"""
        p = b"OLDAUDIO"
        mk_src(self.src, "comment_1_ja.wav", p,
               meta={"tts_text_sha256": sha(JA_OLD), "wav_sha256": hashlib.sha256(p).hexdigest(), "upgraded_from_legacy_ok": True})
        self.assertIsNone(runner.adopt_from_reuse_source(self.src, "comment_1_ja.wav", f"{self.dst_audio}/comment_1_ja.wav", sha(JA_OLD), JA_OLD))
        self.assertFalse(os.path.exists(f"{self.dst_audio}/comment_1_ja.wav"))

    def test_audit_entry_marked_reused_is_not_provenance_evidence(self):
        """R1: auditのentryが reused:True(再利用記録=現行textを無条件に書く)なら、sha256が全て一致しても採用しない。"""
        p = b"OLDAUDIO"
        mk_src(self.src, "comment_1_ja.wav", p, audit_entry={
            "status": "OK", "canonical_text": JA_OLD, "sha256": hashlib.sha256(p).hexdigest(), "reused": True})
        chk = runner.reuse_provenance_check(self.src, "comment_1_ja.wav", sha(JA_OLD))
        self.assertFalse(chk["ok"])
        self.assertEqual(chk["reason"], "audit_entry_is_reuse_record_not_fresh_generation")

    def test_legacy_meta_and_reused_audit_both_present_regenerates(self):
        p = b"OLDAUDIO"
        mk_src(self.src, "japanese_title.wav", p,
               meta={"tts_text_sha256": sha(JA_OLD), "wav_sha256": hashlib.sha256(p).hexdigest(), "upgraded_from_legacy_ok": True},
               audit_entry={"status": "OK", "canonical_text": JA_OLD, "sha256": hashlib.sha256(p).hexdigest(), "reused": True})
        self.assertFalse(runner.reuse_provenance_check(self.src, "japanese_title.wav", sha(JA_OLD))["ok"])

    def test_regular_meta_text_changed_not_adopted_and_old_wav_not_left(self):
        p = b"OLDAUDIO"
        mk_src(self.src, "comment_1_ja.wav", p, meta={"tts_text_sha256": sha(JA_OLD), "wav_sha256": hashlib.sha256(p).hexdigest()})
        r = runner.adopt_from_reuse_source(self.src, "comment_1_ja.wav", f"{self.dst_audio}/comment_1_ja.wav", sha(JA_NEW), JA_NEW)
        self.assertIsNone(r)
        self.assertFalse(os.path.exists(f"{self.dst_audio}/comment_1_ja.wav"))

    def test_regular_meta_wav_swapped_not_adopted(self):
        mk_src(self.src, "comment_1_ja.wav", b"SWAPPED", meta={"tts_text_sha256": sha(JA_OLD), "wav_sha256": "0" * 64})
        self.assertFalse(runner.reuse_provenance_check(self.src, "comment_1_ja.wav", sha(JA_OLD))["ok"])

    def test_no_meta_audit_fresh_match_adopted(self):
        p = b"FRESHAUDIO"
        mk_src(self.src, "comment_1_ja.wav", p, audit_entry={
            "status": "OK", "canonical_text": JA_OLD, "sha256": hashlib.sha256(p).hexdigest(), "reused": False})
        chk = runner.reuse_provenance_check(self.src, "comment_1_ja.wav", sha(JA_OLD))
        self.assertTrue(chk["ok"])
        self.assertEqual(chk["basis"], "audit_fresh_generation")

    def test_no_meta_audit_text_mismatch_or_wav_mismatch_or_missing_regenerates(self):
        p = b"FRESHAUDIO"
        mk_src(self.src, "a.wav", p, audit_entry={"status": "OK", "canonical_text": JA_OLD, "sha256": hashlib.sha256(p).hexdigest()})
        self.assertFalse(runner.reuse_provenance_check(self.src, "a.wav", sha(JA_NEW))["ok"])        # text不一致
        mk_src(self.src, "b.wav", p, audit_entry={"status": "OK", "canonical_text": JA_OLD, "sha256": "f" * 64})
        self.assertFalse(runner.reuse_provenance_check(self.src, "b.wav", sha(JA_OLD))["ok"])        # wav不一致
        mk_src(self.src, "c.wav", p)
        self.assertEqual(runner.reuse_provenance_check(self.src, "c.wav", sha(JA_OLD))["reason"], "no_provenance_evidence")
        self.assertEqual(runner.reuse_provenance_check(self.src, "nope.wav", sha(JA_OLD))["reason"], "src_wav_missing")


class AdoptCopyTests(Base):
    def test_adopt_replaces_existing_dst_and_writes_meta_itself(self):
        """R2: 既存dst(別内容wav+古い.ok+古いmeta)を確実に置換し、metaは採用関数自身が書く。"""
        p = b"GOODAUDIO"
        mk_src(self.src, "comment_1_ja.wav", p, meta={"tts_text_sha256": sha(JA_OLD), "wav_sha256": hashlib.sha256(p).hexdigest(),
                                                       "asr_judgement": {"verdict": "PASS_WITH_WARNING"}})
        dst = f"{self.dst_audio}/comment_1_ja.wav"
        mk_wav(dst, b"UNRELATED_STALE")
        open(dst + ".ok", "w").write("stale")
        json.dump({"tts_text_sha256": "stale", "upgraded_from_legacy_ok": True}, open(dst + ".ok.meta.json", "w"))
        r = runner.adopt_from_reuse_source(self.src, "comment_1_ja.wav", dst, sha(JA_OLD), JA_OLD)
        self.assertIsNotNone(r)
        self.assertEqual(open(dst, "rb").read(), p)
        meta = json.load(open(dst + ".ok.meta.json", encoding="utf-8"))
        self.assertEqual(meta["tts_text_sha256"], sha(JA_OLD))
        self.assertEqual(meta["wav_sha256"], file_sha(dst))
        self.assertEqual(meta["provenance_basis"], "src_meta")
        self.assertIn("comment_1_ja.wav", meta["reuse_from_source"])
        self.assertNotIn("upgraded_from_legacy_ok", meta)
        self.assertEqual(r.get("asr_judgement_inherited"), {"verdict": "PASS_WITH_WARNING"})   # 元WARNING recordの継承(試聴リスト維持)

    def test_unrelated_existing_dst_not_adopted_when_provenance_fails(self):
        """由来不明のときは既存dstを触らない(採用関数はNoneを返し、後段のTTSが上書きする)。"""
        mk_src(self.src, "comment_1_ja.wav", b"X")
        dst = f"{self.dst_audio}/comment_1_ja.wav"
        mk_wav(dst, b"KEEP")
        self.assertIsNone(runner.adopt_from_reuse_source(self.src, "comment_1_ja.wav", dst, sha(JA_OLD), JA_OLD))
        self.assertEqual(open(dst, "rb").read(), b"KEEP")


class TtsCallTests(Base):
    def test_failed_tts_leaves_no_ok_marker(self):
        """R3: 失敗attemptのwavと古い.okが同居しない(新規TTS前に.ok/.metaを削除、失敗後も残らない)。"""
        out = f"{self.dst_audio}/comment_1_ja.wav"
        mk_wav(out, b"OLD")
        open(out + ".ok", "w").write("ok")
        json.dump({"tts_text_sha256": sha(JA_OLD), "wav_sha256": "x"}, open(out + ".ok.meta.json", "w"))
        seen = {}

        def fake(text, language, out_path, exp):
            seen["ok_at_call"] = os.path.exists(out_path + ".ok")
            seen["meta_at_call"] = os.path.exists(out_path + ".ok.meta.json")
            mk_wav(out_path, b"FAILEDATTEMPT")
            return {"status": "STOPPED", "reason": "x"}
        with mock.patch.object(runner.repro01, "generate_narration_snippet_verified_strict", side_effect=fake):
            r = runner.tts_call_for_voice("narrator", JA_OLD, out, "comment_1_ja", self.budget(), {}, language="ja")
        runner.mark_ok(r, out, sha(JA_OLD))
        self.assertFalse(seen["ok_at_call"])
        self.assertFalse(seen["meta_at_call"])
        self.assertFalse(os.path.exists(out + ".ok"))
        self.assertFalse(os.path.exists(out + ".ok.meta.json"))
        self.assertIsNone(runner.resumable_reuse(out, sha(JA_OLD), JA_OLD))

    def test_language_ja_passed_to_verified_strict_and_cost_log(self):
        with mock.patch.object(runner.repro01, "generate_narration_snippet_verified_strict",
                               return_value={"status": "OK", "path": "p", "sha256": "s"}) as m:
            runner.tts_call_for_voice("narrator", JA_OLD, f"{self.dst_audio}/x.wav", "x", self.budget(), {}, language="ja")
        self.assertEqual(m.call_args.args[1], "ja")

    def test_default_language_is_en_for_story(self):
        with mock.patch.object(runner.repro01, "generate_narration_snippet_verified_strict",
                               return_value={"status": "OK", "path": "p", "sha256": "s"}) as m:
            runner.tts_call_for_voice("narrator", "Hello.", f"{self.dst_audio}/x.wav", "story_001", self.budget(), {})
        self.assertEqual(m.call_args.args[1], "en")

    def test_non_narrator_voice_with_ja_raises_before_budget_check(self):
        b = mock.Mock()
        for v in ("device", "brother"):
            with self.assertRaises(RuntimeError) as cm:
                runner.tts_call_for_voice(v, "text", "o.wav", "l", b, {"brother": "Algieba"}, language="ja")
            self.assertIn("NON_EN_LANGUAGE_NOT_SUPPORTED_FOR_VOICE", str(cm.exception))
        b.check_before.assert_not_called()


class SimpleAssetLanguageTests(Base):
    def _run(self, name, text, language):
        calls = []

        def fake(t, lang, out_path, exp):
            calls.append(lang)
            mk_wav(out_path, b"NEW" + lang.encode())
            return {"status": "OK", "path": out_path, "sha256": "s"}
        with mock.patch.object(runner.repro01, "generate_narration_snippet_verified_strict", side_effect=fake):
            r, reused = runner.run_simple_narrator_asset(name, text, language, f"{self.tmp}/out", self.dst_audio,
                                                         self.budget(), None, True)
        return calls, reused

    def test_japanese_title_and_preview_use_ja_topic_intro_uses_en(self):
        self.assertEqual(self._run("japanese_title.wav", JA_OLD, "ja")[0], ["ja"])
        self.assertEqual(self._run("preview_ja.wav", JA_NEW, "ja")[0], ["ja"])
        self.assertEqual(self._run("topic_intro_en.wav", "Today's topic is X.", "en")[0], ["en"])

    def test_reuse_from_text_changed_regenerates_with_ja(self):
        p = b"OLD"
        mk_src(self.src, "japanese_title.wav", p, meta={"tts_text_sha256": sha(JA_OLD), "wav_sha256": hashlib.sha256(p).hexdigest()})
        calls = []

        def fake(t, lang, out_path, exp):
            calls.append(lang)
            mk_wav(out_path, b"NEW")
            return {"status": "OK", "path": out_path, "sha256": "s"}
        with mock.patch.object(runner.repro01, "generate_narration_snippet_verified_strict", side_effect=fake):
            r, reused = runner.run_simple_narrator_asset("japanese_title.wav", JA_NEW, "ja", f"{self.tmp}/out",
                                                         self.dst_audio, self.budget(), self.src, True)
        self.assertFalse(reused)
        self.assertEqual(calls, ["ja"])
        self.assertEqual(open(f"{self.dst_audio}/japanese_title.wav", "rb").read(), b"NEW")

    def test_english_unchanged_text_reuses_with_zero_tts(self):
        """英語回帰: 由来が正しく不変のtopic_intro_enはAPI 0で再利用される。"""
        t = "Today's topic is The Future of Memory."
        p = b"EN_OK"
        mk_src(self.src, "topic_intro_en.wav", p, meta={"tts_text_sha256": sha(t), "wav_sha256": hashlib.sha256(p).hexdigest()})
        with mock.patch.object(runner.repro01, "generate_narration_snippet_verified_strict") as m:
            r, reused = runner.run_simple_narrator_asset("topic_intro_en.wav", t, "en", f"{self.tmp}/out", self.dst_audio,
                                                         self.budget(), self.src, True)
        self.assertTrue(reused)
        m.assert_not_called()


class CommentStageTests(Base):
    def _cfg(self):
        return {"comments": {"1": {"content_facts": "x"}}}

    def _setup_comments_md(self, text):
        os.makedirs(f"{self.tmp}/out", exist_ok=True)
        open(f"{self.tmp}/out/comments_ja.md", "w", encoding="utf-8").write(f"## Comment 1\n\n{text}\n\n")

    def _fake(self, calls):
        def fake(t, lang, out_path, exp):
            calls.append((lang, t))
            mk_wav(out_path, b"FRESH")
            return {"status": "OK", "path": out_path, "sha256": "s"}
        return fake

    def test_comment_tts_uses_ja_and_old_reuse_wav_not_attached_to_new_text(self):
        p = b"OLDCOMMENT"
        mk_src(self.src, "comment_1_ja.wav", p, meta={"tts_text_sha256": sha(JA_OLD), "wav_sha256": hashlib.sha256(p).hexdigest(),
                                                       "upgraded_from_legacy_ok": True})
        self._setup_comments_md(JA_NEW)
        calls = []
        with mock.patch.object(runner.repro01, "generate_narration_snippet_verified_strict", side_effect=self._fake(calls)):
            res = runner.run_comments_stage_a2(self._cfg(), f"{self.tmp}/out", self.dst_audio, "article", self.budget(), self.src,
                                               True, set(), "t")
        self.assertEqual(calls, [("ja", JA_NEW)])
        self.assertEqual(open(f"{self.dst_audio}/comment_1_ja.wav", "rb").read(), b"FRESH")
        self.assertFalse(res["audit"]["comment_1_ja"].get("reused"))

    def test_comment_unchanged_text_with_valid_provenance_reuses_without_tts(self):
        p = b"GOODCOMMENT"
        mk_src(self.src, "comment_1_ja.wav", p, meta={"tts_text_sha256": sha(JA_NEW), "wav_sha256": hashlib.sha256(p).hexdigest()})
        self._setup_comments_md(JA_NEW)
        with mock.patch.object(runner.repro01, "generate_narration_snippet_verified_strict") as m:
            res = runner.run_comments_stage_a2(self._cfg(), f"{self.tmp}/out", self.dst_audio, "article", self.budget(), self.src,
                                               True, set(), "t")
        m.assert_not_called()
        self.assertTrue(res["audit"]["comment_1_ja"]["reused"])

    def test_only_segments_comment_does_not_resurrect_old_wav_from_reuse_from(self):
        """--only-segments comment_1 では、reuse_fromに正規metaの旧wavがあっても復活しない(LLM文面は全Commentで再生成=mock)。"""
        p = b"OLDCOMMENT"
        mk_src(self.src, "comment_1_ja.wav", p, meta={"tts_text_sha256": sha(JA_NEW), "wav_sha256": hashlib.sha256(p).hexdigest()})
        self._setup_comments_md(JA_OLD)
        calls = []
        with mock.patch("er003_v1_iran01_a2_generate.get_client", return_value=object()), \
                mock.patch.object(runner.fam_c, "generate_family_c_a2_comment", return_value={"text": JA_NEW}), \
                mock.patch.object(runner.repro01, "generate_narration_snippet_verified_strict", side_effect=self._fake(calls)):
            runner.run_comments_stage_a2(self._cfg(), f"{self.tmp}/out", self.dst_audio, "article", self.budget(), self.src,
                                         True, {"comment_1"}, "t")
        self.assertEqual(calls, [("ja", JA_NEW)])


class RunnerSourceTests(unittest.TestCase):
    def test_forbidden_words_not_in_runner_source(self):
        src = open(runner.__file__, encoding="utf-8").read()
        for w in ("asr_verified", "evaluate_attempt", "unified_judge"):
            self.assertNotIn(w, src)

    def test_all_tts_call_sites_pass_language_or_default(self):
        src = open(runner.__file__, encoding="utf-8").read()
        self.assertIn('f"comment_{n}_ja", budget, {}, language="ja")', src)
        self.assertIn("name.removesuffix(\".wav\"), budget, {}, language=language)", src)


if __name__ == "__main__":
    unittest.main()
