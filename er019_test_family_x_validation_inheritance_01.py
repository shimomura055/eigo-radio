# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 是正②: 再利用segmentの検証済み状態の証拠つき引継ぎ(REUSED_VALIDATED)の
Regression。API呼出なし(一時ディレクトリ・mockのみ)。Gate(asm.verify_episode_audio_validation_gate)は無変更で、
引き継いだentryは通り、証拠が無い/不一致/staleのsegmentは従来どおりBLOCKされることを確認する。"""
import hashlib
import json
import os
import shutil
import tempfile
import unittest

import er003_v1_n3_01_assemble as asm
import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_validation_inheritance_01 as vi


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _entry(text="hello world", wav_sha=None, path="x.wav", **kw):
    e = {"status": "OK", "asr_verified": True, "canonical_text": text, "text": text, "path": path,
         "disfluency_checked": False}
    if wav_sha:
        e["sha256"] = wav_sha
    e.update(kw)
    return e


class _Tmp(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        os.makedirs(f"{self.d}/narration")
        os.makedirs(f"{self.d}/audit")

    def wav(self, name, data=b"RIFFdata-1"):
        p = f"{self.d}/narration/{name}.wav"
        with open(p, "wb") as f:
            f.write(data)
        return p


class EvaluateTest(_Tmp):
    def test_ok_with_entry_sha(self):
        p = self.wav("a")
        ev = vi.evaluate_inheritance(_entry(wav_sha=_sha(b"RIFFdata-1")), p, expected_text="hello world")
        self.assertTrue(ev["ok"])
        self.assertEqual(ev["evidence"], "entry_sha256")

    def test_no_record_blocks(self):
        p = self.wav("a")
        self.assertEqual(vi.evaluate_inheritance(None, p)["reason"], "NO_SOURCE_ENTRY")

    def test_status_not_ok_or_asr_unverified_blocks(self):
        p = self.wav("a")
        sha = _sha(b"RIFFdata-1")
        for st in ("STOPPED", "ASR_VALIDATION_UNCERTAIN", "SKIPPED_NOT_SELECTED"):
            ev = vi.evaluate_inheritance(_entry(wav_sha=sha, status=st), p)
            self.assertFalse(ev["ok"], st)
        ev = vi.evaluate_inheritance(_entry(wav_sha=sha, asr_verified=False), p)
        self.assertEqual(ev["reason"], "SOURCE_ASR_NOT_VERIFIED")

    def test_sha_mismatch_blocks(self):
        p = self.wav("a", b"changed-audio")
        ev = vi.evaluate_inheritance(_entry(wav_sha=_sha(b"RIFFdata-1")), p)
        self.assertEqual(ev["reason"], "ENTRY_SHA256_MISMATCH")

    def test_text_mismatch_blocks(self):
        p = self.wav("a")
        ev = vi.evaluate_inheritance(_entry(wav_sha=_sha(b"RIFFdata-1")), p, expected_text="other text")
        self.assertEqual(ev["reason"], "CANONICAL_TEXT_MISMATCH")

    def test_wav_missing_blocks(self):
        ev = vi.evaluate_inheritance(_entry(wav_sha="a" * 64), f"{self.d}/narration/none.wav")
        self.assertEqual(ev["reason"], "WAV_MISSING")

    def test_no_identity_evidence_blocks(self):
        p = self.wav("a")
        self.assertEqual(vi.evaluate_inheritance(_entry(), p)["reason"], "NO_IDENTITY_EVIDENCE")

    def test_witness_both_must_match(self):
        p = self.wav("a")
        sha = _sha(b"RIFFdata-1")
        self.assertTrue(vi.evaluate_inheritance(_entry(), p, witness_sha256s=[sha, sha])["ok"])
        self.assertFalse(vi.evaluate_inheritance(_entry(), p, witness_sha256s=[sha, "0" * 64])["ok"])
        self.assertFalse(vi.evaluate_inheritance(_entry(), p, witness_sha256s=[sha, "SOURCE_WAV_MISSING"])["ok"])


class RunnerOnlySegmentsTest(_Tmp):
    def setUp(self):
        super().setUp()
        self._orig = runner._ONLY_SEGMENTS
        runner._ONLY_SEGMENTS = {"full_story_part1"}  # 対象はpart1だけ(commentは非選択)
        self.addCleanup(lambda: setattr(runner, "_ONLY_SEGMENTS", self._orig))
        self.sv = runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION

    def _gen(self):
        raise AssertionError("非選択segmentでgenerate_fnが呼ばれた")

    def test_validated_entry_is_preserved_not_overwritten(self):
        p = self.wav("comment_1")
        cached = {"style_version": self.sv, "segments": {"comment_1": _entry("c1", _sha(b"RIFFdata-1"), p)}}
        r = runner._generate_or_reuse(cached, "comment_1", p, self._gen, expected_text="c1")
        self.assertEqual(r["status"], "OK")
        self.assertEqual(r["validation_inheritance"]["label"], "REUSED_VALIDATED")
        self.assertEqual(r["validation_inheritance"]["wav_sha256"], _sha(b"RIFFdata-1"))

    def test_without_record_stays_skipped(self):
        p = self.wav("comment_1")
        for cached in (None, {"style_version": self.sv, "segments": {}}):
            r = runner._generate_or_reuse(cached, "comment_1", p, self._gen, expected_text="c1")
            self.assertEqual(r["status"], "SKIPPED_NOT_SELECTED")

    def test_changed_wav_stays_skipped(self):
        p = self.wav("comment_1", b"different")
        cached = {"style_version": self.sv, "segments": {"comment_1": _entry("c1", _sha(b"RIFFdata-1"), p)}}
        r = runner._generate_or_reuse(cached, "comment_1", p, self._gen, expected_text="c1")
        self.assertEqual(r["status"], "SKIPPED_NOT_SELECTED")

    def test_entry_without_sha_or_old_style_version_stays_skipped(self):
        p = self.wav("comment_1")
        r = runner._generate_or_reuse({"style_version": self.sv, "segments": {"comment_1": _entry("c1", None, p)}},
                                      "comment_1", p, self._gen, expected_text="c1")
        self.assertEqual(r["status"], "SKIPPED_NOT_SELECTED")
        r = runner._generate_or_reuse({"style_version": "old", "segments": {"comment_1": _entry("c1", _sha(b"RIFFdata-1"), p)}},
                                      "comment_1", p, self._gen, expected_text="c1")
        self.assertEqual(r["status"], "SKIPPED_NOT_SELECTED")

    def test_unvalidated_cached_entries_not_inherited(self):
        p = self.wav("comment_1")
        for st in ("STOPPED", "ASR_VALIDATION_UNCERTAIN"):
            cached = {"style_version": self.sv, "segments": {"comment_1": _entry("c1", _sha(b"RIFFdata-1"), p, status=st)}}
            r = runner._generate_or_reuse(cached, "comment_1", p, self._gen, expected_text="c1")
            self.assertEqual(r["status"], "SKIPPED_NOT_SELECTED")

    def test_kp_component_inheritance(self):
        p = self.wav("kp1_english")
        e = _entry("phrase", _sha(b"RIFFdata-1"), p)
        cached = {"style_version": self.sv, "key_phrases": {"1": {"english": e}}}
        runner._ONLY_SEGMENTS = {"full_story_part1"}
        r = runner._generate_or_reuse_kp(cached, 1, "english", p, self._gen, expected_text="phrase")
        self.assertEqual(r["status"], "OK")
        self.assertEqual(r["validation_inheritance"]["label"], "REUSED_VALIDATED")
        r2 = runner._generate_or_reuse_kp({"style_version": self.sv, "key_phrases": {}}, 1, "english", p, self._gen,
                                          expected_text="phrase")
        self.assertEqual(r2["status"], "SKIPPED_NOT_SELECTED")


class GateIntegrationTest(_Tmp):
    """Gate自体は無変更。引き継いだentryは通り、未検証・stale・記録なしはBLOCKされる。"""

    def _write_results(self, segments):
        with open(f"{self.d}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
            json.dump({"segments": segments, "key_phrases": {}}, f)

    def test_gate_passes_inherited_and_blocks_others(self):
        p = self.wav("comment_1")
        sha = _sha(b"RIFFdata-1")
        inh = vi.build_inherited_entry(_entry("c1", None, p, disfluency_checked=True), p, {"current_sha256": sha, "evidence": "seed_provenance_and_source_wav_sha256"},
                                       {"kind": "test"})
        # 引継ぎentryのみ -> 通過(例外なし)
        self._write_results({"comment_1": inh})
        asm.verify_episode_audio_validation_gate(self.d, "B1", article_text="x")
        # 記録なし(SKIPPED) -> BLOCK(従来どおり)
        self._write_results({"comment_1": inh, "preview": {"status": "SKIPPED_NOT_SELECTED"}})
        with self.assertRaises(RuntimeError) as cm:
            asm.verify_episode_audio_validation_gate(self.d, "B1", article_text="x")
        self.assertIn("preview=UNVALIDATED", str(cm.exception))
        self.assertNotIn("comment_1", str(cm.exception))

    def test_gate_blocks_inherited_entry_when_wav_changed_afterwards(self):
        p = self.wav("comment_1")
        sha = _sha(b"RIFFdata-1")
        inh = vi.build_inherited_entry(_entry("c1", None, p, disfluency_checked=True), p, {"current_sha256": sha, "evidence": "entry_sha256"}, {"kind": "test"})
        self._write_results({"comment_1": inh})
        self.wav("comment_1", b"tampered-after-inheritance")
        with self.assertRaises(RuntimeError) as cm:
            asm.verify_episode_audio_validation_gate(self.d, "B1", article_text="x")
        self.assertIn("ASSET_HASH_MISMATCH", str(cm.exception))


class RebuildStateTest(_Tmp):
    def setUp(self):
        super().setUp()
        self.src_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.src_root, ignore_errors=True)
        os.makedirs(f"{self.src_root}/run/narration")

    def _setup(self, cur_wav=b"WAV-A", src_wav=b"WAV-A", prov_sha=None, src_status="OK"):
        self.wav("topic_intro", cur_wav)
        with open(f"{self.src_root}/run/narration/topic_intro.wav", "wb") as f:
            f.write(src_wav)
        src = {"style_version": "v5", "segments": {"topic_intro": _entry("Today", None, "run/narration/topic_intro.wav", status=src_status)}}
        sp = f"{self.src_root}/src_results.json"
        json.dump(src, open(sp, "w", encoding="utf-8"))
        prov = {"roles": {"topic_intro": {"src": "x", "sha256": prov_sha or _sha(b"WAV-A")}}}
        pp = f"{self.src_root}/prov.json"
        json.dump(prov, open(pp, "w", encoding="utf-8"))
        json.dump({"segments": {"topic_intro": {"status": "SKIPPED_NOT_SELECTED"}}, "style_version": "v3"},
                  open(f"{self.d}/audit/tts_generation_results.json", "w", encoding="utf-8"))
        return sp, pp

    def test_inherit_ok(self):
        sp, pp = self._setup()
        rep = vi.rebuild_state(self.d, sp, self.src_root, pp, ["topic_intro"], {"topic_intro": "Today"})
        self.assertEqual(rep["inherited"], ["topic_intro"])
        e = rep["merged_segments"]["topic_intro"]
        self.assertEqual(e["validation_inheritance"]["label"], "REUSED_VALIDATED")
        self.assertEqual(e["sha256"], _sha(b"WAV-A"))

    def test_source_wav_sha_mismatch_blocks(self):
        # seedされたwav(Trial raw等)が、元runで検証されたwavと別物 -> 引継ぎ不可
        sp, pp = self._setup(cur_wav=b"WAV-TRIAL", src_wav=b"WAV-A", prov_sha=_sha(b"WAV-TRIAL"))
        rep = vi.rebuild_state(self.d, sp, self.src_root, pp, ["topic_intro"])
        self.assertEqual(rep["not_inherited"], ["topic_intro"])
        self.assertEqual(rep["labels"]["topic_intro"]["reason"], "WITNESS_SHA256_MISMATCH")

    def test_provenance_sha_mismatch_blocks(self):
        sp, pp = self._setup(prov_sha="0" * 64)
        rep = vi.rebuild_state(self.d, sp, self.src_root, pp, ["topic_intro"])
        self.assertEqual(rep["inherited"], [])

    def test_source_not_ok_blocks(self):
        sp, pp = self._setup(src_status="STOPPED")
        rep = vi.rebuild_state(self.d, sp, self.src_root, pp, ["topic_intro"])
        self.assertEqual(rep["inherited"], [])

    def test_apply_does_not_overwrite_existing_ok_and_backs_up(self):
        sp, pp = self._setup()
        rep = vi.rebuild_state(self.d, sp, self.src_root, pp, ["topic_intro"])
        backup = vi.apply_state(self.d, rep)
        self.assertTrue(os.path.exists(backup))
        cur = json.load(open(f"{self.d}/audit/tts_generation_results.json", encoding="utf-8"))
        self.assertEqual(cur["segments"]["topic_intro"]["status"], "OK")
        # 既にOKのentryがある場合は再構築対象外(上書きしない)
        rep2 = vi.rebuild_state(self.d, sp, self.src_root, pp, ["topic_intro"])
        self.assertEqual(rep2["inherited"], [])
        self.assertIn("EXISTING_ENTRY_PRESENT", rep2["labels"]["topic_intro"]["reason"])


if __name__ == "__main__":
    unittest.main()
