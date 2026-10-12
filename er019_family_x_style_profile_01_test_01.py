# ============================================================
# er019_family_x_style_profile_01_test_01.py
# FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_02 (OPEN-300)
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_family_x_style_profile_01_test_01 -v
#
# API呼び出し: 0(実TTS/ASR/LLM呼び出しは全てmock、課金0)。
#
# 対象: 設計書 docs/pm/design/2026-10-12_COFFEE-P8-PRODUCTION-WIRING-DESIGN-02.md
#   Phase 1=Coffee Full Storyのみ。案2(--style-profile + out_dir固定記録 + 単一解決関数)。
#   M2(新out_dir限定STOP)/M3(Assembly前Gate)/M4(runtime evidence判定)/M5(backend STOP)/
#   S1(Std逐語+6%減速、Coffee限定例外)/S3(default byte同一・HEAD比較)。
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

import er002_common
import er003_v1_n3_01_tts_generate as n3_tts
import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_style_profile_01 as sp
import er033_tts_flash_lite_family_x_styles_01 as fl_styles

BASELINE_COMMIT = "776c6b92"  # 本委任の実装前HEAD(runner変更前)
P8_SOURCE_MD = "er057_output/aoede_style_trial_03/prompts/prompts_aoede_style_03.md"
FL = "speech_metadata_flash_lite"


def _ok(*_a, **_kw):
    return {"status": "OK", "canonical_text": "x"}


def _sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


class ConstantTests(unittest.TestCase):
    def test_p8_constant_matches_source_and_sha(self):
        self.assertEqual(len(sp.P8_TEXT), 402)
        self.assertEqual(sp.sha256_text(sp.P8_TEXT), "3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595")
        er002_common.assert_no_wpm_specification(sp.P8_TEXT)
        if os.path.exists(P8_SOURCE_MD):
            md = open(P8_SOURCE_MD, encoding="utf-8").read()
            block = re.search(r"```\n(.*?)\n```", md[md.index("## P8"):], re.S).group(1)
            self.assertEqual(block, sp.P8_TEXT)

    def test_shared_constants_unchanged(self):
        # 共通定数(FULL_STORY)はP8ではない(profile経由でのみ置換される)。
        self.assertNotEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"], sp.P8_TEXT)

    def test_unknown_profile_stops(self):
        with self.assertRaises(sp.StyleProfileStop):
            sp.get_profile("nope")


class ResolveRoleStyleTests(unittest.TestCase):
    ROLES = ("TOPIC_INTRO", "PREVIEW", "COMMENT", "FULL_STORY", "IN_ONE_LINE", "HEADING_READOUT")

    def test_default_is_pass_through_for_all_roles_and_levels(self):
        sentinel = object()
        for level in ("a2", "b1b"):
            for role in self.ROLES:
                self.assertIs(sp.resolve_role_style("default", role, level, lambda r: sentinel), sentinel)
                self.assertIsNone(sp.resolve_role_style("default", role, level, lambda r: None))

    def test_coffee_p8_overrides_full_story_both_levels_only(self):
        for level in ("a2", "b1b"):
            self.assertEqual(sp.resolve_role_style("coffee_p8", "FULL_STORY", level, lambda r: "BASE"), sp.P8_TEXT)
            for role in self.ROLES:
                if role != "FULL_STORY":
                    self.assertEqual(sp.resolve_role_style("coffee_p8", role, level, lambda r: "BASE"), "BASE")

    def test_overridden_roles_and_segments(self):
        self.assertEqual(sp.overridden_roles("coffee_p8"), ["FULL_STORY"])
        self.assertEqual(sp.overridden_roles("default"), [])
        self.assertEqual(sp.overridden_segment_names("coffee_p8"),
                          ["full_story_part1", "full_story_part2", "full_story_part3"])


# ----------------------------------------------------------------
# runner経由のmock TTS捕捉(S3: default byte同一 / coffee_p8: Full Storyのみ)
# ----------------------------------------------------------------
def _make_b1b_dir(tmpdir):
    parts = {"title": "Sample Title", "part1": "Part one text.", "part2": "Body two text.",
             "part3": "Body three text.", "in_one_line": "In one line text."}
    support = {"preview": "Preview.", "comment_1": "C1.", "comment_2": "C2.", "comment_3": "C3.", "comment_4": "C4."}
    d = os.path.join(tmpdir, "b1b")
    os.makedirs(d, exist_ok=True)
    json.dump(parts, open(os.path.join(d, "parts.json"), "w", encoding="utf-8"))
    json.dump(support, open(os.path.join(d, "b1_support_texts.json"), "w", encoding="utf-8"))


def _make_a2_dir(tmpdir):
    parts = {"title": "Sample Title", "title_tts": "Sample Title", "part1": "Part one text.",
             "part2": "Body two text.", "part3": "Body three text.", "in_one_line": "In one line text."}
    support = {"preview": "プレビュー。", "comment_1": "コメント1。", "comment_2": "コメント2。",
               "comment_3": "コメント3。", "comment_4": "コメント4。"}
    d = os.path.join(tmpdir, "a2")
    os.makedirs(d, exist_ok=True)
    json.dump(parts, open(os.path.join(d, "parts.json"), "w", encoding="utf-8"))
    json.dump(support, open(os.path.join(d, "a2_support_texts.json"), "w", encoding="utf-8"))


def _capture(mod, tmpdir, backend=FL, **kw):
    """b1b/a2 全segmentの style_prefix_override を捕捉する。modはrunner本体またはHEAD版。"""
    cap = {"b1b": {}, "a2": {}}

    def charon(text, out, **k):
        cap["b1b"][os.path.basename(out)] = k.get("style_prefix_override")
        return {"status": "OK", "canonical_text": "x"}

    def wide(text, out, **k):
        cap["b1b"][os.path.basename(out)] = k.get("style_prefix_override")
        return {"status": "OK", "canonical_text": "x"}

    def a2_en_fallback(text, out, *a, **k):
        cap["a2"][os.path.basename(out)] = k.get("style_prefix_override")
        return {"status": "OK", "canonical_text": "x"}

    def a2_ja(text, out, *a, **k):
        cap["a2"][os.path.basename(out)] = k.get("style_prefix_override")
        return {"status": "OK", "canonical_text": "x"}

    def a2_slow(text, out, *a, **k):
        cap["a2"][os.path.basename(out)] = k.get("style_prefix_override")
        return {"status": "OK", "canonical_text": "x", "fallback_used": False}

    _make_b1b_dir(tmpdir)
    _make_a2_dir(tmpdir)
    with mock.patch.object(mod.shared_narration, "ensure_all_shared_narration_b1"), \
         mock.patch.object(mod.shared_narration, "ensure_all_shared_narration_a2"), \
         mock.patch.object(mod.voice01, "generate_charon_english", side_effect=charon), \
         mock.patch.object(mod.news_tail_fix, "generate_news_narration_wide_margin", side_effect=wide), \
         mock.patch.object(mod.crosslevel_common, "generate_english_segment_with_fallback", side_effect=a2_en_fallback), \
         mock.patch.object(mod.n3_tts, "generate_a2_japanese_with_reading_safety", side_effect=a2_ja), \
         mock.patch.object(mod.n3_tts, "generate_a2_segment_with_slowdown", side_effect=a2_slow):
        mod.generate_family_x_b1_segments(tmpdir, tts_backend=backend, **kw)
        mod.generate_family_x_a2_segments(tmpdir, "日本語タイトル", tts_backend=backend, **kw)
    return cap


def _load_head_runner():
    """BASELINE_COMMITのrunnerをin-memoryでロードする(HEAD比較用)。取得不能ならNone。"""
    try:
        src = subprocess.run(["git", "show", f"{BASELINE_COMMIT}:er019_family_x_audio_production_runner_01.py"],
                              capture_output=True, check=True).stdout.decode("utf-8")
    except Exception:
        return None
    spec = importlib.util.spec_from_loader("runner_head_baseline", loader=None)
    mod = importlib.util.module_from_spec(spec)
    exec(compile(src, "runner_head_baseline.py", "exec"), mod.__dict__)
    return mod


class RunnerCaptureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="style_profile_cap_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_default_style_prefix_overrides_identical_to_baseline_head(self):
        head = _load_head_runner()
        if head is None:
            self.skipTest("baseline commit not available")
        for backend in (FL, "structured_separation"):
            t1 = tempfile.mkdtemp(prefix="cap_head_")
            t2 = tempfile.mkdtemp(prefix="cap_new_")
            try:
                cap_head = _capture(head, t1, backend=backend)
                cap_new = _capture(runner, t2, backend=backend)  # style_profile既定=default
                self.assertEqual(cap_head, cap_new)
                self.assertTrue(cap_new["b1b"] and cap_new["a2"])
            finally:
                shutil.rmtree(t1, ignore_errors=True)
                shutil.rmtree(t2, ignore_errors=True)

    def test_default_writes_no_new_keys_in_segments(self):
        _capture(runner, self.tmp)
        for lvl in ("b1b", "a2"):
            res = json.load(open(f"{self.tmp}/{lvl}/audit/tts_generation_results.json", encoding="utf-8"))
            for name, entry in res["segments"].items():
                self.assertNotIn("style_profile", entry, (lvl, name))
        self.assertFalse(os.path.exists(f"{self.tmp}/audit/style_profile.json"))

    def test_coffee_p8_full_story_is_p8_both_levels_others_unchanged(self):
        t_def = tempfile.mkdtemp(prefix="cap_def_")
        try:
            cap_def = _capture(runner, t_def)
            cap_p8 = _capture(runner, self.tmp, style_profile="coffee_p8")
        finally:
            shutil.rmtree(t_def, ignore_errors=True)
        for lvl in ("b1b", "a2"):
            for fname, style in cap_p8[lvl].items():
                if fname in ("full_story_part1.wav", "full_story_part2.wav", "full_story_part3.wav"):
                    self.assertEqual(style, sp.P8_TEXT, (lvl, fname))
                else:
                    self.assertEqual(style, cap_def[lvl][fname], (lvl, fname))  # 他roleは不変(IN_ONE_LINE含む)
        # P8対象はFull Story 3 segmentのみ
        for lvl in ("b1b", "a2"):
            res = json.load(open(f"{self.tmp}/{lvl}/audit/tts_generation_results.json", encoding="utf-8"))
            with_rec = sorted(n for n, e in res["segments"].items() if "style_profile" in e)
            self.assertEqual(with_rec, ["full_story_part1", "full_story_part2", "full_story_part3"])
            for n in with_rec:
                self.assertEqual(res["segments"][n]["style_profile"]["style_base_sha256"], sp.P8_SHA256)

    def test_std_p8_is_verbatim_no_slower_instruction_but_default_std_is_combined(self):
        """S1(COFFEE-P8-STD-VERBATIM-EXCEPTION-01): Std Full StoryはP8逐語(減速指示非連結)。
        defaultのStdは従来どおり6-role style+A2_SLOWER_PACE_INSTRUCTION連結。"""
        t_def = tempfile.mkdtemp(prefix="cap_def_")
        try:
            cap_def = _capture(runner, t_def)
            cap_p8 = _capture(runner, self.tmp, style_profile="coffee_p8")
        finally:
            shutil.rmtree(t_def, ignore_errors=True)
        slower = n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()
        self.assertIn(slower, cap_def["a2"]["full_story_part1.wav"])
        self.assertEqual(cap_p8["a2"]["full_story_part1.wav"], sp.P8_TEXT)
        self.assertNotIn(slower, cap_p8["a2"]["full_story_part1.wav"])
        # in_one_lineのStdは(coffee_p8でも)従来どおり連結
        self.assertIn(slower, cap_p8["a2"]["in_one_line.wav"])
        # 例外IDがコード注記として固定されている
        src = open("er019_family_x_style_profile_01.py", encoding="utf-8").read()
        self.assertIn("COFFEE-P8-STD-VERBATIM-EXCEPTION-01", src)
        self.assertIn("er003_v1_n3_01_tts_generate.py", src)
        self.assertFalse(sp.STYLE_PROFILES["coffee_p8"]["overrides"]["FULL_STORY"]["std_append_slower_instruction"])

    def test_m5_legacy_backend_stops_for_non_default_profile(self):
        for fn in (runner.generate_family_x_b1_segments,):
            with self.assertRaises(sp.StyleProfileStop):
                fn(self.tmp, tts_backend="structured_separation", style_profile="coffee_p8")
        with self.assertRaises(sp.StyleProfileStop):
            runner.generate_family_x_a2_segments(self.tmp, "t", tts_backend="structured_separation",
                                                  style_profile="coffee_p8")
        # defaultはlegacy backend可(M5対象外)
        sp.assert_profile_backend("default", "structured_separation")

    def test_all_style_resolution_goes_through_single_resolver(self):
        """grep型: runnerのstyle解決(_role_style/_role_style_slower)は全てresolve_role_styleを経由する。"""
        src = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        self.assertEqual(src.count("style_profile_mod.resolve_role_style("), 3)  # b1 / a2 / a2 slower
        self.assertEqual(src.count("fl_styles.FAMILY_X_ROLE_STYLE_EN.get("), 2)  # 各_base_role_style内のみ
        self.assertEqual(src.count("def _base_role_style("), 2)
        # 非resolver経由の旧定義が残っていない
        self.assertNotIn("    def _role_style(role: str) -> str | None:\n        if tts_backend", src)


# ----------------------------------------------------------------
# M2 / 固定記録
# ----------------------------------------------------------------
class RunProfileResolutionTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="style_profile_res_")
        self.out = os.path.join(self.root, "run_new")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_no_cli_no_record_is_default_and_writes_nothing(self):
        pid, src = sp.resolve_run_profile(self.out, None)
        self.assertEqual((pid, src), ("default", "default_no_record"))
        self.assertFalse(os.path.exists(self.out))
        pid, _ = sp.resolve_run_profile(self.out, "default")
        self.assertEqual(pid, "default")
        self.assertFalse(os.path.exists(self.out))

    def test_new_out_dir_coffee_p8_writes_record_with_overridden_roles(self):
        pid, src = sp.resolve_run_profile(self.out, "coffee_p8")
        self.assertEqual((pid, src), ("coffee_p8", "cli_new_record"))
        rec = json.load(open(sp.record_path(self.out), encoding="utf-8"))
        self.assertEqual(rec["profile_id"], "coffee_p8")
        self.assertEqual(rec["overridden_roles"], ["FULL_STORY"])  # M6
        self.assertEqual(rec["roles"]["FULL_STORY"]["sha256"], sp.P8_SHA256)

    def test_resume_without_cli_uses_record(self):
        sp.resolve_run_profile(self.out, "coffee_p8")
        self.assertEqual(sp.resolve_run_profile(self.out, None), ("coffee_p8", "record"))
        self.assertEqual(sp.resolve_run_profile(self.out, "coffee_p8"), ("coffee_p8", "record"))

    def test_cli_mismatch_with_record_stops(self):
        sp.resolve_run_profile(self.out, "coffee_p8")
        with self.assertRaises(sp.StyleProfileStop):
            sp.resolve_run_profile(self.out, "default")

    def test_record_sha_mismatch_stops(self):
        sp.resolve_run_profile(self.out, "coffee_p8")
        rec = json.load(open(sp.record_path(self.out), encoding="utf-8"))
        rec["roles"]["FULL_STORY"]["sha256"] = "0" * 64
        json.dump(rec, open(sp.record_path(self.out), "w", encoding="utf-8"))
        with self.assertRaises(sp.StyleProfileStop):
            sp.resolve_run_profile(self.out, None)

    def test_m2_existing_run_artifacts_stop_and_no_record_created(self):
        for rel in ("audit/tts_generation_results.json", "audit/review_lock_state.json",
                    "audit/human_approved_segments.json", "a2/audit/tts_generation_results.json",
                    "b1b/audit/review_lock_state.json", "b1b/audit/human_approved_segments.json"):
            out = os.path.join(self.root, "m2_" + re.sub(r"\W", "_", rel))
            os.makedirs(os.path.dirname(os.path.join(out, rel)), exist_ok=True)
            open(os.path.join(out, rel), "w").write("{}")
            with self.assertRaises(sp.StyleProfileStop, msg=rel):
                sp.resolve_run_profile(out, "coffee_p8")
            self.assertFalse(os.path.exists(sp.record_path(out)), rel)
            # default / 未指定は従来どおり通る(既存run不変)
            self.assertEqual(sp.resolve_run_profile(out, None)[0], "default")

    def test_m5_in_main_flow_helper(self):
        with self.assertRaises(sp.StyleProfileStop):
            sp.assert_profile_backend("coffee_p8", "structured_separation")
        sp.assert_profile_backend("coffee_p8", FL)


# ----------------------------------------------------------------
# M4: runtime evidence判定
# ----------------------------------------------------------------
def _adv_entry(final_style=None, hints=None, base_sha=None):
    final_style = sp.P8_TEXT if final_style is None else final_style
    e = {"status": "OK", "style_prefix": final_style, "instruction_type": "english_style_prefix_wide_margin",
         "canonical_text": "t",
         "style_profile": {"profile_id": "coffee_p8", "role": "FULL_STORY",
                           "expected_base_sha256": sp.P8_SHA256,
                           "style_base_sha256": base_sha or sp.P8_SHA256},
         "en_pronunciation_resolver_info": {"hints_applied": bool(hints), "cache_hits": hints or []}}
    return e


def _std_entry(final_style=None, hints=None, fallback=False):
    final_style = sp.P8_TEXT if final_style is None else final_style
    rec = {"len": len(final_style), "sha256": _sha(final_style), "head200": final_style[:200]}
    return {"status": "OK", "fallback_used": fallback, "canonical_text": "t",
            "attempts_log": [{"attempt": 1, "style_prefix": rec}],
            "style_profile": {"profile_id": "coffee_p8", "role": "FULL_STORY",
                              "expected_base_sha256": sp.P8_SHA256, "style_base_sha256": sp.P8_SHA256},
            "en_pronunciation_resolver_info": {"hints_applied": bool(hints), "cache_hits": hints or []}}


class EvidenceTests(unittest.TestCase):
    def test_no_hint_requires_final_sha_equals_p8(self):
        self.assertTrue(sp.evaluate_segment_evidence(_adv_entry(), "b1b")["pass"])
        self.assertTrue(sp.evaluate_segment_evidence(_std_entry(), "a2")["pass"])
        bad = sp.evaluate_segment_evidence(_adv_entry(final_style=sp.P8_TEXT + " x"), "b1b")  # hintなし申告で末尾差
        self.assertFalse(bad["pass"])
        self.assertIn("FINAL_STYLE_SHA_MISMATCH_NO_HINT", bad["reasons"])

    def test_hint_appended_checks_head200_and_lists_cache_hits(self):
        hinted = sp.P8_TEXT + " Pronunciation: Arabica as AH-rab-ih-kuh."
        hits = [{"surface": "Arabica", "confidence": "high"}]
        for entry, level in ((_adv_entry(final_style=hinted, hints=hits), "b1b"),
                             (_std_entry(final_style=hinted, hints=hits), "a2")):
            ev = sp.evaluate_segment_evidence(entry, level)
            self.assertTrue(ev["pass"], ev)
            self.assertTrue(ev["hint_applied"])
            self.assertEqual(ev["cache_hits"], ["Arabica"])
        wrong_head = "X" + hinted[1:]
        self.assertFalse(sp.evaluate_segment_evidence(_adv_entry(final_style=wrong_head, hints=hits), "b1b")["pass"])

    def test_base_sha_mismatch_or_missing_fails(self):
        self.assertFalse(sp.evaluate_segment_evidence(_adv_entry(base_sha="0" * 64), "b1b")["pass"])
        e = _adv_entry()
        del e["style_profile"]
        self.assertFalse(sp.evaluate_segment_evidence(e, "b1b")["pass"])


# ----------------------------------------------------------------
# M3: Assembly前Gate
# ----------------------------------------------------------------
def _results(level, **overrides):
    mk = _adv_entry if level == "b1b" else _std_entry
    segs = {n: mk() for n in sp.overridden_segment_names("coffee_p8")}
    for n, fn in overrides.items():
        fn(segs[n])
    return {"segments": segs}


class M3GateTests(unittest.TestCase):
    def test_default_profile_is_noop(self):
        self.assertEqual(sp.m3_assembly_gate("default", "b1b", {})["status"], "PASS")

    def test_pass_for_p8_generated_segments(self):
        for lvl in ("b1b", "a2"):
            g = sp.m3_assembly_gate("coffee_p8", lvl, _results(lvl))
            self.assertEqual(g["status"], "PASS", g)
            self.assertEqual(len(g["checked"]), 3)

    def test_block_conditions(self):
        cases = [
            ("b1b", lambda e: e.update(instruction_type="minimal_fallback"), "ADV_MINIMAL_FALLBACK"),
            ("b1b", lambda e: e.update(style_prefix="<default:ENGLISH_STYLE_PREFIX>"), "ADV_STYLE_PREFIX_NOT_P8_PREFIXED"),
            ("b1b", lambda e: e.update(local_rewrite_recovery={"x": 1}), "LOCAL_REWRITE_RECOVERY"),
            ("b1b", lambda e: e["style_profile"].update(style_base_sha256="0" * 64), "STYLE_BASE_SHA_MISMATCH_OR_MISSING"),
            ("a2", lambda e: e.update(fallback_used=True), "STD_FALLBACK_USED_OR_UNKNOWN"),
            ("a2", lambda e: e.update(local_rewrite_recovery={"x": 1}), "LOCAL_REWRITE_RECOVERY"),
        ]
        for lvl, mut, reason in cases:
            g = sp.m3_assembly_gate("coffee_p8", lvl, _results(lvl, full_story_part2=mut))
            self.assertEqual(g["status"], "BLOCK", reason)
            self.assertEqual([b["segment"] for b in g["blocked"]], ["full_story_part2"])
            self.assertIn(reason, g["blocked"][0]["violations"])

    def test_missing_segment_record_blocks(self):
        res = _results("b1b")
        del res["segments"]["full_story_part3"]
        g = sp.m3_assembly_gate("coffee_p8", "b1b", res)
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("NO_SEGMENT_RECORD", g["blocked"][0]["violations"])

    def test_human_approval_bypasses_only_with_matching_text_sha(self):
        res = _results("b1b", full_story_part2=lambda e: e.update(instruction_type="minimal_fallback"))
        approvals = {"full_story_part2": {"canonical_text_sha256": _sha("t")}}
        g = sp.m3_assembly_gate("coffee_p8", "b1b", res, approvals)
        self.assertEqual(g["status"], "PASS")
        self.assertEqual(g["human_approved"][0]["segment"], "full_story_part2")
        stale = {"full_story_part2": {"canonical_text_sha256": _sha("other text")}}
        self.assertEqual(sp.m3_assembly_gate("coffee_p8", "b1b", res, stale)["status"], "BLOCK")


class AssembleIntegrationTests(unittest.TestCase):
    """runnerのstage_assemble_family_x_*内でGateが呼ばれる(共有assembleは不変)。"""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="style_gate_asm_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _setup(self, lvl, profile, entry_mut=None):
        d = f"{self.root}/{lvl}"
        os.makedirs(f"{d}/key_phrases", exist_ok=True)
        os.makedirs(f"{d}/audit", exist_ok=True)
        json.dump({}, open(f"{d}/key_phrases/keywords_canonicalized.json", "w"))
        if profile != "default":
            sp.resolve_run_profile(self.root, profile)
        res = _results(lvl, full_story_part1=entry_mut or (lambda e: None))
        json.dump(res, open(f"{d}/audit/tts_generation_results.json", "w", encoding="utf-8"))

    def test_blocked_summary_for_both_levels_and_human_approval_bypass(self):
        for lvl in ("b1b", "a2"):
            self.root = tempfile.mkdtemp(prefix="style_gate_asm_")
            fn = runner.stage_assemble_family_x_b1 if lvl == "b1b" else runner.stage_assemble_family_x_a2
            if lvl == "b1b":
                self._setup(lvl, "coffee_p8", lambda e: e.update(instruction_type="minimal_fallback"))
            else:
                self._setup(lvl, "coffee_p8", lambda e: e.update(fallback_used=True))
            summary = fn(self.root, "slug")
            self.assertEqual(summary["status"], "BLOCKED_STYLE_PROFILE_GATE", lvl)
            self.assertEqual(summary["blocked"][0]["segment"], "full_story_part1")
            self.assertTrue(os.path.exists(f"{self.root}/{lvl}/audit/style_profile_gate.json"))
            shutil.rmtree(self.root, ignore_errors=True)

    def test_default_run_has_no_gate_artifact(self):
        self._setup("b1b", "default", lambda e: e.update(instruction_type="minimal_fallback"))
        self.assertIsNone(runner._style_profile_gate_blocked_summary(self.root, f"{self.root}/b1b", "b1b"))
        self.assertFalse(os.path.exists(f"{self.root}/b1b/audit/style_profile_gate.json"))


# ----------------------------------------------------------------
# S2: plan段階のLedger hit / main CLI
# ----------------------------------------------------------------
class PlanStageTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="style_plan_")
        self.src = f"{self.root}/src"
        self.out = f"{self.root}/out"
        os.makedirs(f"{self.src}/b1b")
        open(f"{self.src}/b1b/article.md", "w", encoding="utf-8").write("dummy")
        self.parts = {"status": "OK", "title": "T", "part1": "Arabica beans.", "part2": "Body two.",
                      "part3": "Body three.", "in_one_line": "One line."}

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_default_plan_has_no_style_profile_key_and_p8_plan_records_ledger_hits(self):
        with mock.patch.object(runner.plan, "split_family_x_article_text_v2", return_value=dict(self.parts)):
            r_def = runner.run_plan_stage(self.src, self.out, ["b1b"])
            r_p8 = runner.run_plan_stage(self.src, self.out, ["b1b"], style_profile="coffee_p8")
        self.assertNotIn("style_profile_plan", r_def["b1b"])
        plan_rec = r_p8["b1b"]["style_profile_plan"]
        self.assertEqual(plan_rec["profile_id"], "coffee_p8")
        self.assertEqual(plan_rec["full_story_style_sha256"], sp.P8_SHA256)
        self.assertEqual(sorted(plan_rec["ledger_hits_web_lookup_disabled"]),
                          ["full_story_part1", "full_story_part2", "full_story_part3"])

    def test_compute_ledger_hits_with_mocked_ledger(self):
        fake_hit = {"surface": "Arabica", "confidence": "high"}

        def fake_aug(style, text, min_confidence="medium"):
            return (style + " HINT", [fake_hit]) if "Arabica" in text else (style, [])

        with mock.patch("er006_pronunciation_tts_injection_01.augment_style_prefix_with_pronunciation",
                        side_effect=fake_aug):
            hits = sp.compute_ledger_hits(self.parts)
        self.assertTrue(hits["full_story_part1"]["hint_applied"])
        self.assertFalse(hits["full_story_part2"]["hint_applied"])
        self.assertTrue(hits["full_story_part1"]["augmented_startswith_p8"])

    def test_main_stops_before_creating_anything_on_m5_and_m2(self):
        out = f"{self.root}/main_out"
        argv = ["x", "--slug", "s", "--run", "r", "--out-dir", out, "--style-profile", "coffee_p8",
                "--tts-backend", "structured_separation", "--allow-legacy-backend", "--dry-run"]
        with mock.patch("sys.argv", argv):
            with self.assertRaises(sp.StyleProfileStop):
                runner.main()
        self.assertFalse(os.path.exists(out))  # M5: --allow-legacy-backendでもSTOP、何も作らない
        # M2
        os.makedirs(f"{out}/a2/audit")
        open(f"{out}/a2/audit/tts_generation_results.json", "w").write("{}")
        argv2 = ["x", "--slug", "s", "--run", "r", "--out-dir", out, "--style-profile", "coffee_p8",
                 "--tts-backend", FL, "--dry-run"]
        with mock.patch("sys.argv", argv2):
            with self.assertRaises(sp.StyleProfileStop):
                runner.main()
        self.assertFalse(os.path.exists(sp.record_path(out)))


if __name__ == "__main__":
    unittest.main()
