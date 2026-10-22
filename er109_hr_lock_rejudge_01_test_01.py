# -*- coding: utf-8 -*-
"""er109_hr_lock_rejudge_01(HR Lock再判定CLI)のtest(API 0・費用0)。ASR-HOMOPHONE 委任_04(Opus M2/M12)。
実行: .venv\\Scripts\\python.exe -m unittest er109_hr_lock_rejudge_01_test_01 -v"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er109_hr_lock_rejudge_01 as cli
import er109_xz_scope_01 as xz
import er109_xz_scope_01_test_01 as T

TMP_ROOT = os.path.join(ROOT, "er019_output", "__er109_hr_test_tmp__")        # X許可root配下(testが作って消す)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class HrRejudgeTests(T.Base):
    def setUp(self):
        super().setUp()
        shutil.rmtree(TMP_ROOT, ignore_errors=True)
        os.makedirs(TMP_ROOT, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(TMP_ROOT, ignore_errors=True))
        self.n = 0

    def make_level(self, segments, level="b1b", theme="theme_x__run_t"):
        """segments: {seg_id: (canonical, [attempt dict...], is_kp)}。attempt dict: asr, secondary, whisper(KP), wav_ok, sha_ok"""
        ld = os.path.join(TMP_ROOT, theme, level)
        os.makedirs(os.path.join(ld, "audit"), exist_ok=True)
        os.makedirs(os.path.join(ld, "narration", "attempts"), exist_ok=True)
        lock, results = {}, {"segments": {}, "key_phrases": {}}
        for seg, (canon, atts, is_kp) in segments.items():
            log = []
            for i, a in enumerate(atts, 1):
                wav = os.path.join(ld, "narration", "attempts", f"{seg}_a{i}.wav")
                data = f"wav-{seg}-{i}".encode()
                if a.get("wav_ok", True):
                    open(wav, "wb").write(data)
                aj = {"state": "NG_BOTH", "reason_code": "secondary_value_diff", "audio_sha256": (_sha(data) if a.get("sha_ok", True) else "0" * 64),
                      "secondary": {"text": a.get("secondary"), "label": ""}}
                if is_kp:
                    aj["vote"] = {"required": True, "primary": {"text": a["asr"]}, "secondary": {"text": a.get("secondary")},
                                  "whisper": ({"text": a.get("whisper")} if a.get("whisper") else None), "whisper_called": bool(a.get("whisper"))}
                log.append({"attempt": i, "asr_text": a["asr"], "verified": False, "audio_classification": "TRUE_CONTENT_MISMATCH",
                            "attempt_audio_path": os.path.relpath(wav, ROOT).replace("\\", "/"), "asr_judgement": aj, "max_len": 40})
            lock[seg] = {"state": "HUMAN_REVIEW_REQUIRED", "canonical_text_sha256": _sha(canon.encode("utf-8")), "theme_id": theme, "level": level,
                         "segment_id": seg, "updated_at": "2026-10-23T00:00:00", "reason": "最終status=STOPPED", "last_attempts_log": log}
            if is_kp:
                results["key_phrases"][seg[2:-3]] = {"english": {"text": canon, "status": "STOPPED"}}
            else:
                results["segments"][seg] = {"text": canon, "status": "STOPPED"}
        json.dump(lock, open(os.path.join(ld, "audit", "review_lock_state.json"), "w", encoding="utf-8"), ensure_ascii=False)
        json.dump(results, open(os.path.join(ld, "audit", "tts_generation_results.json"), "w", encoding="utf-8"), ensure_ascii=False)
        return ld

    def cls(self, rep, seg):
        return next(c for c in rep["candidates"] if c["identification"]["segment_id"] == seg)

    def test_classes(self):
        ld = self.make_level({
            "full_story_part1": ("Pump one's fist.", [{"asr": "Pump 1's fist.", "secondary": "Pump 1's fist."}, {"asr": "Pump 1's fist.", "secondary": "Pump 1's fist."}], False),
            "full_story_part2": ("I said no.", [{"asr": "I said know.", "secondary": "I said know."}], False),
            "full_story_part3": ("We have two cats.", [{"asr": "We have one cats.", "secondary": "We have one cats."}], False),
            "comment_1": ("I said no.", [{"asr": "I said know.", "secondary": "I said know.", "sha_ok": False}], False),
            "comment_2": ("I said no.", [{"asr": "I said know.", "secondary": "I said know.", "wav_ok": False}], False),
            "comment_3": ("Pump one's fist.", [{"asr": "Pump a fist.", "secondary": None}], False),
        })
        rep = cli.evaluate_level(ld)
        self.assertEqual(rep["family"], "X")
        self.assertEqual(self.cls(rep, "full_story_part1")["class"], "PASS")
        c2 = self.cls(rep, "full_story_part2")
        self.assertEqual(c2["class"], "PASS_WITH_WARNING")
        self.assertIn("ORTHO_NEGATION_WORD_HOMOPHONE", c2["attempts"][0]["new"]["warnings"])
        self.assertIn("事後試聴必須", c2["note"])
        self.assertTrue(c2["candidate_id"].startswith("theme_x__run_t/b1b/full_story_part2@"))
        self.assertEqual(self.cls(rep, "full_story_part3")["class"], "NOT_CANDIDATE")
        self.assertEqual(self.cls(rep, "comment_1")["class"], "INSUFFICIENT_EVIDENCE")       # 記録shaと現在shaが不一致
        self.assertEqual(self.cls(rep, "comment_2")["class"], "INSUFFICIENT_EVIDENCE")       # 音声欠落
        self.assertEqual(self.cls(rep, "comment_3")["class"], "INSUFFICIENT_EVIDENCE")       # Secondary転写なし
        # 最小情報(識別/attemptごとのsha一致・保存転写・新旧判定/根拠/実行記録)
        c1 = self.cls(rep, "full_story_part1")
        self.assertEqual(c1["identification"]["canonical_text"], "Pump one's fist.")
        self.assertEqual(len(c1["attempts"]), 2)
        a = c1["attempts"][0]
        for k in ("wav_path", "recorded_sha256", "current_sha256", "sha_match", "stored_transcripts", "old", "new"):
            self.assertIn(k, a)
        self.assertEqual(c1["basis"]["er109_version"], xz.layer_version())
        self.assertTrue(c1["basis"]["per_attempt"])
        self.assertEqual(rep["execution"]["scope"], "X")
        self.assertEqual(rep["execution"]["api_calls"], 0)
        self.assertIn("commit", rep["execution"])

    def test_japanese_segment_is_not_candidate(self):
        ld = self.make_level({"comment_1": ("これはテストです。", [{"asr": "これはテストです。", "secondary": "これはテストです。"}], False)})
        c = cli.evaluate_level(ld)["candidates"][0]
        self.assertEqual(c["class"], "NOT_CANDIDATE")
        self.assertEqual(c["attempts"], [])                                       # 英語judgeに通していない

    def test_kp_needs_three_votes(self):
        ld = self.make_level({
            "kp1_en": ("I said no", [{"asr": "I said know", "secondary": "I said no"}], True),                      # P ortho PASS / S PASS -> 合格(P+S)
            "kp2_en": ("I said no", [{"asr": "I sed no", "secondary": "I said no"}], True),                       # P NG / S PASS -> Whisper必須だが無い
            "kp3_en": ("I said no", [{"asr": "I sed no", "secondary": "I said no", "whisper": "I said know"}], True),   # S+W (W ortho)
        })
        rep = cli.evaluate_level(ld)
        self.assertEqual(self.cls(rep, "kp1_en")["class"], "PASS_WITH_WARNING")
        self.assertEqual(self.cls(rep, "kp2_en")["class"], "INSUFFICIENT_EVIDENCE")
        c3 = self.cls(rep, "kp3_en")
        self.assertEqual(c3["class"], "PASS_WITH_WARNING")
        self.assertEqual(c3["attempts"][0]["new"]["vote_row"], "S+W")

    def test_canonical_hash_mismatch_is_insufficient(self):
        ld = self.make_level({"full_story_part1": ("Pump one's fist.", [{"asr": "Pump 1's fist.", "secondary": "Pump 1's fist."}], False)})
        res_path = os.path.join(ld, "audit", "tts_generation_results.json")
        d = json.load(open(res_path, encoding="utf-8"))
        d["segments"]["full_story_part1"]["text"] = "Different text."
        json.dump(d, open(res_path, "w", encoding="utf-8"))
        c = cli.evaluate_level(ld)["candidates"][0]
        self.assertEqual(c["class"], "INSUFFICIENT_EVIDENCE")

    def test_family_is_decided_by_data_root_and_others_refused(self):
        for bad in (os.path.join(ROOT, "er012_output", "x", "b1b"), os.path.join(ROOT, "er013_output", "c", "a2"), os.path.join(ROOT, "docs", "x"),
                    os.path.join(os.path.expanduser("~"), "elsewhere", "b1b")):
            with self.subTest(bad=bad):
                with self.assertRaises(cli.RefusedFamily):
                    cli.family_of_level_dir(bad)
        self.assertEqual(cli.family_of_level_dir(os.path.join(ROOT, "er019_output", "t", "r", "a2")), "X")
        self.assertEqual(cli.family_of_level_dir(os.path.join(ROOT, "er026_output", "family_z_production_e2e_01", "s", "r", "b1b")), "Z")
        with self.assertRaises(SystemExit):                                      # --scope 指定は存在しない(M2)
            cli.main(["--level-dir", TMP_ROOT, "--scope", "X"])

    def test_no_automatic_release_and_outputs(self):
        ld = self.make_level({"full_story_part1": ("Pump one's fist.", [{"asr": "Pump 1's fist.", "secondary": "Pump 1's fist."}], False)})
        lock_path = os.path.join(ld, "audit", "review_lock_state.json")
        before = open(lock_path, "rb").read()
        rep = cli.evaluate_level(ld)
        paths = cli.write_outputs(rep)
        cli.write_outputs(cli.evaluate_level(ld))
        self.assertEqual(open(lock_path, "rb").read(), before)                    # lockは1バイトも変えない(自動解除なし)
        cand = json.load(open(paths[0], encoding="utf-8"))
        self.assertEqual(cand["candidates"][0]["class"], "PASS")
        self.assertEqual(len(open(paths[1], encoding="utf-8").read().strip().split("\n")), 2)   # 実行ごとに追記
        self.assertIsNone(xz.current_scope())

    def test_cli_source_never_calls_approve_regenerate_or_imports_er011_lock(self):
        tree = ast.parse(open(os.path.join(ROOT, "er109_hr_lock_rejudge_01.py"), encoding="utf-8").read())
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                nm = getattr(n.func, "attr", getattr(n.func, "id", ""))
                self.assertNotEqual(nm, "approve_regenerate")
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in n.names] + [getattr(n, "module", None) or ""]
                self.assertFalse(any("er011_human_review_lock" in m for m in mods))

    def test_main_returns_and_summary(self):
        ld = self.make_level({"full_story_part1": ("I said no.", [{"asr": "I said know.", "secondary": "I said know."}], False)})
        out = os.path.join(TMP_ROOT, "summary.json")
        rc = cli.main(["--level-dir", ld, "--no-write", "--summary-out", out])
        self.assertEqual(rc, 0)
        s = json.load(open(out, encoding="utf-8"))
        self.assertEqual(s["by_class"], {"PASS_WITH_WARNING": 1})
        self.assertFalse(os.path.exists(os.path.join(ld, "audit", "er109_hr_rejudge_candidates.json")))


if __name__ == "__main__":
    unittest.main()
