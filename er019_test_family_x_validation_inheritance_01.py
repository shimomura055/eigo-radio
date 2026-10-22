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
import wave

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


def _wavbytes(tag=0, secs=0.5, rate=8000):
    """有効な16bit mono wavのbytes(tagで内容を変える)。"""
    import io
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((tag.to_bytes(2, "little", signed=True)) * int(rate * secs))
    return buf.getvalue()


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

    def test_unvalidated_cached_entries_not_marked_validated_but_carried_over(self):
        # OF-X11: STOPPED等はsha一致時にそのまま持ち越す(REUSED_VALIDATEDは付けない。Gateがstatusで判定=BLOCK維持)
        p = self.wav("comment_1")
        for st in ("STOPPED", "ASR_VALIDATION_UNCERTAIN", "HUMAN_REVIEW_LOCKED"):
            cached = {"style_version": self.sv, "segments": {"comment_1": _entry("c1", _sha(b"RIFFdata-1"), p, status=st)}}
            r = runner._generate_or_reuse(cached, "comment_1", p, self._gen, expected_text="c1")
            self.assertEqual(r["status"], st)
            self.assertNotIn("validation_inheritance", r)
            self.assertTrue(r["carried_over_unchanged"])
            self.assertTrue(vi.is_untouched_entry(r))
            # text不一致は持ち越さない
            r2 = runner._generate_or_reuse(cached, "comment_1", p, self._gen, expected_text="other")
            self.assertEqual(r2["status"], "SKIPPED_NOT_SELECTED")
        # sha不一致 / INVALIDATED entry は持ち越さない
        cached = {"style_version": self.sv, "segments": {"comment_1": _entry("c1", "0" * 64, p, status="STOPPED")}}
        self.assertEqual(runner._generate_or_reuse(cached, "comment_1", p, self._gen, expected_text="c1")["status"],
                         "SKIPPED_NOT_SELECTED")
        cached = {"style_version": self.sv, "segments": {"comment_1": {"status": "INVALIDATED_FOR_REGENERATION"}}}
        self.assertEqual(runner._generate_or_reuse(cached, "comment_1", p, self._gen, expected_text="c1")["status"],
                         "SKIPPED_NOT_SELECTED")

    def test_carried_stopped_entry_still_blocks_gate(self):
        p = self.wav("comment_1")
        cached = {"style_version": self.sv, "segments": {"comment_1": _entry("c1", _sha(b"RIFFdata-1"), p, status="STOPPED")}}
        r = runner._generate_or_reuse(cached, "comment_1", p, self._gen, expected_text="c1")
        json.dump({"segments": {"comment_1": r}}, open(f"{self.d}/audit/tts_generation_results.json", "w", encoding="utf-8"))
        with self.assertRaises(RuntimeError) as cm:
            asm.verify_episode_audio_validation_gate(self.d, "B1")
        self.assertIn("comment_1", str(cm.exception))

    def test_kp_component_inheritance(self):
        p = self.wav("kp1_english")
        e = _entry("phrase", _sha(b"RIFFdata-1"), p)
        # KPDUAL-PROD-D2(UDR #139): KP英語phraseの引継ぎは両Provider PASSの保存証跡を要する(fail-closed)。証跡なしは引き継がない。
        cached_nodual = {"style_version": self.sv, "key_phrases": {"1": {"english": dict(e)}}}
        runner._ONLY_SEGMENTS = {"full_story_part1"}
        r0 = runner._generate_or_reuse_kp(cached_nodual, 1, "english", p, self._gen, expected_text="phrase")
        self.assertEqual(r0["status"], "SKIPPED_NOT_SELECTED")
        e["kp_dual_check"] = {"version": "kp_dual_check_v1", "ok": True, "canonical_text": "phrase", "wav_sha256": _sha(b"RIFFdata-1"),
                              "primary": {"text": "phrase", "pass": True}, "secondary": {"text": "phrase", "pass": True}}
        cached = {"style_version": self.sv, "key_phrases": {"1": {"english": e}}}
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
    PTR = "docs/pm/delegation_log/2026-10-13_FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01_02.md#是正②OF-X5"

    def setUp(self):
        super().setUp()
        self.src_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.src_root, ignore_errors=True)
        os.makedirs(f"{self.src_root}/run/narration")

    def _setup(self, cur_wav=None, src_wav=None, prov_sha=None, src_status="OK", dur=0.5, rec_dur=0.5, src_ver="v5",
               entry_sha=None, with_prov=True, asr_text=None):
        cur_wav = cur_wav if cur_wav is not None else _wavbytes(1, dur)
        src_wav = src_wav if src_wav is not None else _wavbytes(1, dur)
        self.wav("topic_intro", cur_wav)
        with open(f"{self.src_root}/run/narration/topic_intro.wav", "wb") as f:
            f.write(src_wav)
        ent = _entry("Today", entry_sha, "run/narration/topic_intro.wav", status=src_status,
                     trim_info={"trimmed_duration_seconds": rec_dur})
        if asr_text is not None:
            ent["asr_text"] = asr_text
        src = {"style_version": src_ver, "segments": {"topic_intro": ent}}
        sp = f"{self.src_root}/src_results.json"
        json.dump(src, open(sp, "w", encoding="utf-8"))
        pp = None
        if with_prov:
            prov = {"roles": {"topic_intro": {"src": "x", "sha256": prov_sha or _sha(_wavbytes(1, dur))}}}
            pp = f"{self.src_root}/prov.json"
            json.dump(prov, open(pp, "w", encoding="utf-8"))
        json.dump({"segments": {"topic_intro": {"status": "SKIPPED_NOT_SELECTED"}}, "style_version": "v3"},
                  open(f"{self.d}/audit/tts_generation_results.json", "w", encoding="utf-8"))
        return sp, pp

    def _rb(self, sp, pp, **kw):
        kw.setdefault("cross_version_accepted_by", self.PTR)
        exp = kw.pop("exp", {"topic_intro": "Today"})
        return vi.rebuild_state(self.d, sp, self.src_root, pp, ["topic_intro"], exp, **kw)

    def test_inherit_ok_records_source_style_version_and_acceptance(self):
        sp, pp = self._setup()
        rep = self._rb(sp, pp)
        self.assertEqual(rep["inherited"], ["topic_intro"])
        e = rep["merged_segments"]["topic_intro"]
        v = e["validation_inheritance"]
        self.assertEqual(v["label"], "REUSED_VALIDATED")
        self.assertEqual(v["source_style_version"], "v5")
        self.assertEqual(v["cross_version_accepted_by"], self.PTR)
        self.assertEqual(v["evidence"], "witness_sha256_and_trimmed_duration")
        self.assertTrue(v["duration_witness"]["ok"])
        self.assertEqual(e["sha256"], _sha(_wavbytes(1, 0.5)))

    def test_style_version_mismatch_without_pointer_blocks(self):  # OF-X5
        sp, pp = self._setup()
        rep = self._rb(sp, pp, cross_version_accepted_by=None)
        self.assertEqual(rep["inherited"], [])
        self.assertEqual(rep["labels"]["topic_intro"]["reason"], "STYLE_VERSION_MISMATCH_NO_ACCEPTANCE_POINTER")
        # 同一style_versionなら不要
        sp, pp = self._setup(src_ver="v3")
        rep = self._rb(sp, pp, cross_version_accepted_by=None)
        self.assertEqual(rep["inherited"], ["topic_intro"])
        self.assertNotIn("cross_version_accepted_by", rep["merged_segments"]["topic_intro"]["validation_inheritance"])

    def test_duration_witness_mismatch_blocks(self):  # OF-X7
        sp, pp = self._setup(rec_dur=0.55)
        rep = self._rb(sp, pp)
        self.assertEqual(rep["labels"]["topic_intro"]["reason"], "DURATION_WITNESS_MISMATCH")
        sp, pp = self._setup(rec_dur=0.515)  # 15ms差は許容
        self.assertEqual(self._rb(sp, pp)["inherited"], ["topic_intro"])

    def test_missing_trim_info_blocks_for_shaless_entry(self):  # OF-X7 fail-closed
        sp, pp = self._setup()
        src = json.load(open(sp, encoding="utf-8"))
        del src["segments"]["topic_intro"]["trim_info"]
        json.dump(src, open(sp, "w", encoding="utf-8"))
        self.assertEqual(self._rb(sp, pp)["labels"]["topic_intro"]["reason"], "DURATION_WITNESS_MISMATCH")

    def test_entry_sha_path_without_provenance_roles(self):  # OF-X8: entry sha256経路(provenanceにrolesキー無し=copies形式)
        sp, pp = self._setup(entry_sha=_sha(_wavbytes(1, 0.5)), with_prov=False)
        rep = self._rb(sp, None)
        self.assertEqual(rep["inherited"], ["topic_intro"])
        self.assertEqual(rep["merged_segments"]["topic_intro"]["validation_inheritance"]["evidence"], "entry_sha256")
        pp2 = f"{self.src_root}/prov_copies.json"
        json.dump({"copies": [{"label": "topic_intro"}]}, open(pp2, "w", encoding="utf-8"))
        self.assertEqual(self._rb(sp, pp2)["inherited"], ["topic_intro"])

    def test_source_wav_sha_mismatch_blocks(self):
        # seedされたwav(Trial raw等)が、元runで検証されたwavと別物 -> 引継ぎ不可
        sp, pp = self._setup(cur_wav=_wavbytes(9), src_wav=_wavbytes(1), prov_sha=_sha(_wavbytes(9)))
        rep = self._rb(sp, pp)
        self.assertEqual(rep["not_inherited"], ["topic_intro"])
        self.assertEqual(rep["labels"]["topic_intro"]["reason"], "WITNESS_SHA256_MISMATCH")

    def test_provenance_sha_mismatch_blocks(self):
        sp, pp = self._setup(prov_sha="0" * 64)
        self.assertEqual(self._rb(sp, pp)["inherited"], [])

    def test_source_not_ok_blocks(self):
        sp, pp = self._setup(src_status="STOPPED")
        self.assertEqual(self._rb(sp, pp)["inherited"], [])

    def test_f1_rejudge_ng_blocks_and_ok_records_version(self):  # OF-X6
        sp, pp = self._setup()
        e = json.load(open(sp, encoding="utf-8"))
        txt = "Today's topic is coffee prices."
        e["segments"]["topic_intro"].update({"text": txt, "canonical_text": txt, "asr_text": txt})
        json.dump(e, open(sp, "w", encoding="utf-8"))
        ok = self._rb(sp, pp, exp={"topic_intro": txt}, level="b1b", rejudge_f1=True)
        self.assertEqual(ok["inherited"], ["topic_intro"])
        j = ok["merged_segments"]["topic_intro"]["validation_inheritance"]["f1_rejudge"]
        self.assertTrue(j["ok"])
        self.assertTrue(j["f1_version"].startswith("F1-"))
        e["segments"]["topic_intro"]["asr_text"] = "Today's topic is tea prices rising."
        json.dump(e, open(sp, "w", encoding="utf-8"))
        ng = self._rb(sp, pp, exp={"topic_intro": txt}, level="b1b", rejudge_f1=True)
        self.assertEqual(ng["inherited"], [])
        self.assertTrue(ng["labels"]["topic_intro"]["reason"].startswith("F1_REJUDGE_NG"))

    def test_f1_rejudge_not_applicable_for_japanese_labels(self):
        # AUW 委任_04(α更新): J11が統一judge入口経由になり、日本語segmentも再判定の対象(applicable=True)になった。
        # F1(英語連結発音)自体は日本語に適用しない(英語のclassify_asr_match/f1_versionは返さない)が、保存転写に対する
        # 最終ANDゲート(値DIFF/否定差)は適用する(DESIGN_02_ADDENDUM_01 §3-1)。API 0・Secondary新規呼出なし。
        rj = vi.rejudge_with_current_judge({"asr_text": "x", "text": "y"}, "a2", "preview")
        self.assertTrue(rj["applicable"])
        self.assertNotIn("f1_version", rj)
        self.assertEqual(rj["secondary_new_calls"], 0)
        self.assertFalse(vi.rejudge_with_current_judge({"asr_text": "三人", "text": "四人"}, "a2", "preview")["ok"])
        self.assertTrue(vi.is_japanese_label("a2", "japanese_title"))
        self.assertFalse(vi.is_japanese_label("a2", "in_one_line"))
        self.assertFalse(vi.is_japanese_label("b1b", "preview"))

    def test_apply_requires_expected_text(self):  # OF-X4
        sp, pp = self._setup()
        rep = self._rb(sp, pp)
        with self.assertRaises(SystemExit):
            vi.apply_state(self.d, rep, expected_texts=None)
        with self.assertRaises(SystemExit):
            vi.apply_state(self.d, rep, expected_texts={"topic_intro": ""})
        cur = json.load(open(f"{self.d}/audit/tts_generation_results.json", encoding="utf-8"))
        self.assertEqual(cur["segments"]["topic_intro"]["status"], "SKIPPED_NOT_SELECTED")  # 何も書かれていない

    def test_cli_apply_without_expected_text_is_refused(self):  # OF-X4 (CLI)
        sp, pp = self._setup()
        import sys
        argv = ["x", "--level-dir", self.d, "--level", "b1b", "--source", f"topic_intro|{sp}|{self.src_root}|{pp}",
                "--output", f"{self.d}/out.json", "--apply"]
        old = sys.argv
        sys.argv = argv
        try:
            with self.assertRaises(SystemExit) as cm:
                vi.main()
        finally:
            sys.argv = old
        self.assertIn("expected_text", str(cm.exception))
        self.assertFalse(os.path.exists(f"{self.d}/out.json"))

    def test_derive_expected_texts_from_current_files(self):  # OF-X4
        json.dump({"title": "T Title", "in_one_line": "One line.", "part1": "P1"}, open(f"{self.d}/parts.json", "w"))
        json.dump({"preview": "PV", "comment_1": "C1"}, open(f"{self.d}/a2_support_texts.json", "w"))
        exp = vi.derive_expected_texts(self.d, "a2", ["topic_intro", "in_one_line", "preview", "comment_1", "full_story_part1"])
        self.assertEqual(exp, {"topic_intro": "Today's topic is T Title.", "in_one_line": "One line.", "preview": "PV",
                               "comment_1": "C1", "full_story_part1": "P1"})

    def test_apply_does_not_overwrite_existing_ok_and_backs_up(self):
        sp, pp = self._setup()
        rep = self._rb(sp, pp)
        backup = vi.apply_state(self.d, rep, {"topic_intro": "Today"})
        self.assertTrue(os.path.exists(backup))
        cur = json.load(open(f"{self.d}/audit/tts_generation_results.json", encoding="utf-8"))
        self.assertEqual(cur["segments"]["topic_intro"]["status"], "OK")
        # 既にOKのentryがある場合は再構築対象外(上書きしない)
        rep2 = self._rb(sp, pp)
        self.assertEqual(rep2["inherited"], [])
        self.assertIn("EXISTING_ENTRY_PRESENT", rep2["labels"]["topic_intro"]["reason"])

    def test_seed_wav_replaces_with_backup_and_inherits(self):  # Adv in_one_line型(Trial rawを元runの検証済みtakeへ)
        sp, pp = self._setup(cur_wav=_wavbytes(9), src_wav=_wavbytes(1), with_prov=False)
        rep = self._rb(sp, None, seed_wav=True)
        self.assertEqual(rep["inherited"], ["topic_intro"])
        self.assertIn("topic_intro", rep["seed_copies"])
        vi.apply_state(self.d, rep, {"topic_intro": "Today"})
        self.assertEqual(_sha(open(f"{self.d}/narration/topic_intro.wav", "rb").read()), _sha(_wavbytes(1)))
        moved = os.listdir(f"{self.d}/narration/_replaced_02")
        self.assertEqual(len(moved), 1)  # 旧wavは削除せず退避
        cur = json.load(open(f"{self.d}/audit/tts_generation_results.json", encoding="utf-8"))
        self.assertIn("seeded_wav", cur["segments"]["topic_intro"]["validation_inheritance"])

    def test_seed_wav_ignores_stale_provenance_of_replaced_wav(self):
        """置換される現行wav(Trial raw)のprovenance sha(旧wav用)は新wavの証拠にならず無視される。ただし元wav sha+duration witnessは必須。"""
        sp, pp = self._setup(cur_wav=_wavbytes(9), src_wav=_wavbytes(1), prov_sha=_sha(_wavbytes(9)))
        rep = self._rb(sp, pp, seed_wav=True)
        self.assertEqual(rep["inherited"], ["topic_intro"])
        self.assertTrue(rep["labels"]["topic_intro"]["seed_provenance_ignored_because_wav_replaced"])
        # duration witnessが不一致なら、provenanceを無視した場合でも引継ぎ不可
        sp, pp = self._setup(cur_wav=_wavbytes(9), src_wav=_wavbytes(1), prov_sha=_sha(_wavbytes(9)), rec_dur=0.9)
        rep = self._rb(sp, pp, seed_wav=True)
        self.assertEqual(rep["labels"]["topic_intro"]["reason"], "DURATION_WITNESS_MISMATCH")


class NextRunCarriesRecordTest(_Tmp):
    """OF-X5: apply後の次回runner自動引継ぎでsource_style_version/cross_version_accepted_by/f1_rejudgeが保持される。"""

    def test_runner_auto_inheritance_preserves_source_record(self):
        orig = runner._ONLY_SEGMENTS
        runner._ONLY_SEGMENTS = {"full_story_part1"}
        self.addCleanup(lambda: setattr(runner, "_ONLY_SEGMENTS", orig))
        sv = runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION
        p = self.wav("comment_1", _wavbytes(1))
        base = _entry("c1", _sha(_wavbytes(1)), p)
        ev = {"current_sha256": _sha(_wavbytes(1)), "evidence": "entry_sha256"}
        inh = vi.build_inherited_entry(base, p, ev, {"kind": "t"}, source_style_version="v5_old",
                                       cross_version_accepted_by="PTR", f1_rejudge={"f1_version": "F1-x", "ok": True})
        cached = {"style_version": sv, "segments": {"comment_1": inh}}
        r = runner._generate_or_reuse(cached, "comment_1", p, lambda: 1 / 0, expected_text="c1")
        v = r["validation_inheritance"]
        self.assertEqual(v["source_style_version"], "v5_old")
        self.assertEqual(v["cross_version_accepted_by"], "PTR")
        self.assertEqual(v["f1_rejudge"]["f1_version"], "F1-x")
        self.assertEqual(v["carried_over_count"], 1)
        # 2回目の持ち越しでも保持
        r2 = runner._generate_or_reuse({"style_version": sv, "segments": {"comment_1": r}}, "comment_1", p,
                                       lambda: 1 / 0, expected_text="c1")
        self.assertEqual(r2["validation_inheritance"]["source_style_version"], "v5_old")
        self.assertEqual(r2["validation_inheritance"]["carried_over_count"], 2)


if __name__ == "__main__":
    unittest.main()
