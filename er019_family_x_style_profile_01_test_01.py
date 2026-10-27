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
        # b1 / a2 / a2 slower / a2 support_ja(V5, R2) / b1 KP explanation(V5, P3)
        # + 委任_02A: KP英語(K2、_kp_english_generate_fn) / Std KP日本語意味(P8-KP、_role_style_ja_kp_meaning)
        self.assertEqual(src.count("style_profile_mod.resolve_role_style("), 7)
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
        # 2026-10-13 FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01(Opus必須5 B'): 期待値を意図的に更新。
        # 旧: CLI未指定・記録なし -> default(何も書かない)。新: 新規out_dirはN01 profileへ解決し固定記録を作る。
        # `--style-profile default`を明示した場合は従来どおりdefault(何も書かない)。
        # 2026-10-16 委任_02A: 新規out_dirの既定はfx_20261016へ更新(ユーザー指示§4)。
        # 2026-10-17 委任_03 Phase B(S3正式採用): 既定はfx_20261017へ更新(fx_20261016はresume互換のみ)。
        pid, src = sp.resolve_run_profile(self.out, None, write=False)
        self.assertEqual((pid, src), ("fx_20261017", "default_new_run_fx_20261017"))
        self.assertFalse(os.path.exists(self.out))  # write=Falseでは書かない
        pid, _ = sp.resolve_run_profile(self.out, "default")
        self.assertEqual(pid, "default")
        self.assertFalse(os.path.exists(self.out))
        # legacy backend(Trial/regression用)では従来どおりdefault(N01はspeech_metadata_flash_lite必須、M5)
        pid, src = sp.resolve_run_profile(self.out, None, tts_backend="structured_separation")
        self.assertEqual((pid, src), ("default", "default_no_record_legacy_backend"))
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
            # 2026-10-13(Opus必須5 B'): 既存run state(記録なし)でCLI未指定は課金前にSTOP(N01へ途中適用しない)。
            # `--style-profile default`を明示すれば従来どおり通る(既存run不変)。
            with self.assertRaises(sp.StyleProfileStop, msg=rel):
                sp.resolve_run_profile(out, None)
            self.assertFalse(os.path.exists(sp.record_path(out)), rel)
            self.assertEqual(sp.resolve_run_profile(out, "default")[0], "default")

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
            ("b1b", lambda e: e.update(style_prefix="<default:ENGLISH_STYLE_PREFIX>"), "ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED"),
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

    def test_lr_adoption_blocks_even_when_fallback_used_false_open564(self):
        """委任_05 OPEN-564: LR採用attemptが①'/②'(fallback_used=False)でも、LOCAL_REWRITE_RECOVERYでM3はBLOCKのまま(Gate緩和ではない)。
        STD_FALLBACK_USED_OR_UNKNOWNは付かない(記録の正確化のみ)。"""
        for lvl in ("b1b", "a2"):
            g = sp.m3_assembly_gate("coffee_p8", lvl, _results(lvl, full_story_part2=lambda e: e.update(fallback_used=False, local_rewrite_recovery={"status": "RESOLVED_BY_LOCAL_REWRITE"})))
            self.assertEqual(g["status"], "BLOCK")
            v = g["blocked"][0]["violations"]
            self.assertIn("LOCAL_REWRITE_RECOVERY", v)
            self.assertNotIn("STD_FALLBACK_USED_OR_UNKNOWN", v)

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


# ================================================================
# FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01 委任_01: coffee_final_v5
#   Std Preview/Comment1〜4=R2、Adv KP英英解説=P3(+Full Story=P8維持)。Coffee限定。
# ================================================================
R2_SOURCE_MD = "er057_output/ja_aoede_style_trial_02/prompts/prompts_R.md"
P3_SOURCE_MD = "er057_output/kp_en_explanation_style_trial_01/prompts/prompts_kp_en_explanation_style_01.md"
C4_TRIAL_MD = "er057_output/coffee_comment4_trial_03/prompts/prompt_trial_03.md"
V5 = "coffee_final_v5"


def _md_block(path, heading):
    md = open(path, encoding="utf-8").read()
    start = md.index(heading)
    return re.search(r"```\n(.*?)\n```", md[start:], re.S).group(1)


class V5ConstantTests(unittest.TestCase):
    def test_r2_matches_trial_source_and_sha(self):
        self.assertEqual(len(sp.R2_TEXT), 168)
        self.assertEqual(sp.sha256_text(sp.R2_TEXT), "625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f")
        if os.path.exists(R2_SOURCE_MD):
            self.assertEqual(_md_block(R2_SOURCE_MD, "## R2 "), sp.R2_TEXT)

    def test_p3_matches_trial_source_sha_and_is_p0_plus_diff(self):
        self.assertEqual(len(sp.P3_TEXT), 141)
        self.assertEqual(sp.sha256_text(sp.P3_TEXT), "a8aaec591ef6d9acb42532cc0c84b6edfb2f75991e713d413c565b7e27677acc")
        self.assertTrue(sp.P3_TEXT.startswith(fl_styles.KEY_PHRASE_EXPLANATION_EN + " "))
        if os.path.exists(P3_SOURCE_MD):
            self.assertEqual(_md_block(P3_SOURCE_MD, "## P3 "), sp.P3_TEXT)
        er002_common.assert_no_wpm_specification(sp.P3_TEXT)
        er002_common.assert_no_wpm_specification(sp.R2_TEXT)

    def test_shared_constants_unchanged_by_v5(self):
        self.assertEqual(fl_styles.KEY_PHRASE_EXPLANATION_EN, "clear, precise, at a measured pace, without dragging")
        self.assertNotEqual(fl_styles.FAMILY_X_ROLE_STYLE_JA, sp.R2_TEXT)

    def test_comment4_prompt_is_trial03_minimal_two_sentences(self):
        import er019_family_x_audio_plan_01 as plan
        c4 = plan.FAMILY_X_A2_COMMENT_4_ROLE
        self.assertEqual(sp.sha256_text(c4), "22feebde438ad5ec70d6a3ce19e067bc0c5fa3890de3fc600b5c6477278a3663")
        self.assertIn("In One Lineは、番組の最後に流れる英語による要点整理です。橋渡しの表現では、\n"
                      "「続いて」より「最後に」を使ってください。", c4)
        if os.path.exists(C4_TRIAL_MD):
            self.assertEqual(re.search(r"```\n(.*?)\n```", open(C4_TRIAL_MD, encoding="utf-8").read(), re.S).group(1), c4)
        # 他Role(Comment 3等)は不変
        self.assertNotIn("最後に", plan.FAMILY_X_A2_COMMENT_3_ROLE)


class V5ResolveTests(unittest.TestCase):
    def test_roles_and_levels(self):
        self.assertEqual(sp.overridden_roles(V5), ["FULL_STORY", "KP_EXPLANATION_EN", "SUPPORT_JA"])
        self.assertEqual(sp.overridden_segment_names(V5, "a2"),
                          ["full_story_part1", "full_story_part2", "full_story_part3",
                           "preview", "comment_1", "comment_2", "comment_3", "comment_4"])
        self.assertEqual(sp.overridden_segment_names(V5, "b1b"),
                          ["full_story_part1", "full_story_part2", "full_story_part3"])

    def test_support_ja_is_r2_for_a2_only_and_kp_is_p3_for_b1b_only(self):
        self.assertEqual(sp.resolve_role_style(V5, "SUPPORT_JA", "a2", lambda r: "BASE"), sp.R2_TEXT)
        self.assertEqual(sp.resolve_role_style(V5, "SUPPORT_JA", "b1b", lambda r: "BASE"), "BASE")
        self.assertEqual(sp.resolve_role_style(V5, "KP_EXPLANATION_EN", "b1b", lambda r: "BASE"), sp.P3_TEXT)
        self.assertEqual(sp.resolve_role_style(V5, "KP_EXPLANATION_EN", "a2", lambda r: "BASE"), "BASE")
        for level in ("a2", "b1b"):
            self.assertEqual(sp.resolve_role_style(V5, "FULL_STORY", level, lambda r: "BASE"), sp.P8_TEXT)
            for role in ("TOPIC_INTRO", "PREVIEW", "COMMENT", "IN_ONE_LINE", "HEADING_READOUT"):
                self.assertEqual(sp.resolve_role_style(V5, role, level, lambda r: "BASE"), "BASE")

    def test_other_profiles_unchanged(self):
        for prof in ("default", "coffee_p8"):
            for level in ("a2", "b1b"):
                for role in ("SUPPORT_JA", "KP_EXPLANATION_EN"):
                    self.assertEqual(sp.resolve_role_style(prof, role, level, lambda r: "BASE"), "BASE")
        self.assertEqual(sp.overridden_roles("coffee_p8"), ["FULL_STORY"])
        self.assertEqual(sp.overridden_segment_names("coffee_p8"), ["full_story_part1", "full_story_part2", "full_story_part3"])

    def test_record_roundtrip_and_sha_mismatch_stops(self):
        tmp = tempfile.mkdtemp(prefix="v5rec_")
        try:
            pid, src = sp.resolve_run_profile(tmp, V5)
            self.assertEqual((pid, src), (V5, "cli_new_record"))
            rec = sp.read_record(tmp)
            self.assertEqual(sorted(rec["roles"]), ["FULL_STORY", "KP_EXPLANATION_EN", "SUPPORT_JA"])
            self.assertEqual(rec["roles"]["SUPPORT_JA"]["sha256"], sp.R2_SHA256)
            self.assertEqual(rec["roles"]["KP_EXPLANATION_EN"]["sha256"], sp.P3_SHA256)
            self.assertEqual(sp.verify_record(rec), V5)
            self.assertEqual(sp.resolve_run_profile(tmp, None), (V5, "record"))
            with self.assertRaises(sp.StyleProfileStop):  # profile変更不可
                sp.resolve_run_profile(tmp, "coffee_p8")
            rec["roles"]["SUPPORT_JA"]["sha256"] = "0" * 64
            with self.assertRaises(sp.StyleProfileStop):
                sp.verify_record(rec)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_m5_legacy_backend_stops_for_v5(self):
        with self.assertRaises(sp.StyleProfileStop):
            sp.assert_profile_backend(V5, "structured_separation")
        sp.assert_profile_backend(V5, FL)


class V5RunnerCaptureTests(unittest.TestCase):
    """runner経由(mock TTS)でStd preview/comment=R2、Adv KP解説=P3、Full Story=P8、他role/default不変。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="v5cap_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, tmpdir, profile, only=None):
        cap = {"a2": {}, "kp": {}, "b1b": {}}
        _make_b1b_dir(tmpdir)
        _make_a2_dir(tmpdir)
        kp = {"items": [{"rank": 1, "used_form": "price tag", "display_phrase": "price tag",
                         "japanese_gloss": "値札", "source_sentence": "A price tag."}]}
        os.makedirs(f"{tmpdir}/b1b/key_phrases", exist_ok=True)
        json.dump(kp, open(f"{tmpdir}/b1b/key_phrases/keywords_canonicalized.json", "w", encoding="utf-8"))

        def a2_ja(text, out, *a, **k):
            cap["a2"][os.path.basename(out)] = k.get("style_prefix_override")
            return {"status": "OK", "canonical_text": "x", "fallback_used": False}

        def kp_expl(text, out, style_prefix_override=None, tts_backend="x"):
            cap["kp"][os.path.basename(out)] = style_prefix_override
            return {"status": "OK", "attempts_log": [{"attempt": 1, "style_prefix": {
                "sha256": sp.sha256_text(style_prefix_override), "head200": style_prefix_override[:200],
                "len": len(style_prefix_override)}}]}

        def other_b1(text, out, *a, **k):
            cap["b1b"][os.path.basename(out)] = k.get("style_prefix_override")
            return {"status": "OK", "canonical_text": "x", "fallback_used": False}

        def other_a2(text, out, *a, **k):
            cap["a2"][os.path.basename(out)] = k.get("style_prefix_override")
            return {"status": "OK", "canonical_text": "x", "fallback_used": False}

        def kp_en(text, out, *a, **k):
            return {"status": "OK", "canonical_text": "x"}

        bundle = {"items": {1: {"english_explanation": "a tag showing the price", "status": "OK", "qa": {}}},
                  "phrases_signature": ["price tag"]}
        with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1"), \
             mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2"), \
             mock.patch.object(runner.kp_vote, "ensure_key_phrase_english_component_x_vote", side_effect=kp_en), \
             mock.patch.object(runner.voice01, "generate_charon_english", side_effect=other_b1), \
             mock.patch.object(runner.news_tail_fix, "generate_news_narration_wide_margin", side_effect=other_b1), \
             mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback", side_effect=other_a2), \
             mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety", side_effect=a2_ja), \
             mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=other_a2), \
             mock.patch.object(runner.n3_tts, "resolve_key_phrase_ja_gloss_tts", return_value=("値札", False)), \
             mock.patch.object(runner, "_resolve_kp_explanations_text", return_value=dict(bundle)), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified", side_effect=kp_expl), \
             mock.patch.object(runner, "_ONLY_SEGMENTS", only):
            runner.generate_family_x_b1_segments(tmpdir, tts_backend=FL, style_profile=profile)
            os.makedirs(f"{tmpdir}/a2/key_phrases", exist_ok=True)
            json.dump(kp, open(f"{tmpdir}/a2/key_phrases/keywords_canonicalized.json", "w", encoding="utf-8"))
            runner.generate_family_x_a2_segments(tmpdir, "タイトル", tts_backend=FL, style_profile=profile)
        return cap

    def test_v5_applies_r2_p3_and_leaves_others_identical_to_default(self):
        t_def = tempfile.mkdtemp(prefix="v5cap_def_")
        try:
            cap_def = self._run(t_def, "default")
            cap_v5 = self._run(self.tmp, V5)
        finally:
            shutil.rmtree(t_def, ignore_errors=True)
        # Std JA: preview/comment1-4=R2。japanese_title/meaning_1は不変(J3のまま)。
        for n in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
            self.assertEqual(cap_v5["a2"][f"{n}.wav"], sp.R2_TEXT, n)
            self.assertEqual(cap_def["a2"][f"{n}.wav"], fl_styles.FAMILY_X_ROLE_STYLE_JA, n)
        for n in ("japanese_title.wav", "meaning_1.wav"):
            self.assertEqual(cap_v5["a2"][n], cap_def["a2"][n], n)
            self.assertEqual(cap_v5["a2"][n], fl_styles.FAMILY_X_ROLE_STYLE_JA)
        # Adv KP解説=P3(defaultはP0=KEY_PHRASE_EXPLANATION_EN)
        self.assertEqual(cap_v5["kp"]["kp1_explanation_en.wav"], sp.P3_TEXT)
        self.assertEqual(cap_def["kp"]["kp1_explanation_en.wav"], fl_styles.KEY_PHRASE_EXPLANATION_EN)
        # Adv側のPreview/Comment/Full Story等: Full Storyのみ変更、他はdefaultと同一
        for fname, style in cap_v5["b1b"].items():
            if fname.startswith("full_story_part"):
                self.assertEqual(style, sp.P8_TEXT, fname)
            else:
                self.assertEqual(style, cap_def["b1b"][fname], fname)
        # 記録: 対象roleのsegmentだけにstyle_profile記録
        res = json.load(open(f"{self.tmp}/a2/audit/tts_generation_results.json", encoding="utf-8"))
        with_rec = sorted(n for n, e in res["segments"].items() if "style_profile" in e)
        self.assertEqual(with_rec, ["comment_1", "comment_2", "comment_3", "comment_4", "full_story_part1",
                                     "full_story_part2", "full_story_part3", "preview"])
        for n in ("preview", "comment_1"):
            self.assertEqual(res["segments"][n]["style_profile"]["style_base_sha256"], sp.R2_SHA256)
        resb = json.load(open(f"{self.tmp}/b1b/audit/tts_generation_results.json", encoding="utf-8"))
        self.assertEqual(resb["key_phrases"]["1"]["explanation"]["style_profile"]["style_base_sha256"], sp.P3_SHA256)

    def test_default_writes_no_support_or_kp_style_profile_keys(self):
        self._run(self.tmp, "default")
        res = json.load(open(f"{self.tmp}/a2/audit/tts_generation_results.json", encoding="utf-8"))
        resb = json.load(open(f"{self.tmp}/b1b/audit/tts_generation_results.json", encoding="utf-8"))
        self.assertTrue(all("style_profile" not in e for e in res["segments"].values()))
        self.assertNotIn("style_profile", resb["key_phrases"]["1"]["explanation"])
        self.assertNotIn("only_segments", res)

    def test_only_segments_generates_requested_only(self):
        only = {"preview", "comment_4", "kp1_explanation"}
        cap = self._run(self.tmp, V5, only=only)
        self.assertEqual(sorted(cap["a2"]), ["comment_4.wav", "preview.wav"])
        self.assertEqual(sorted(cap["kp"]), ["kp1_explanation_en.wav"])
        # Adv側: 同名(preview/comment_4)のみ(segment名はlevel共通。実運用は--levelで片側ずつ)。Full Story等は生成されない
        self.assertEqual(sorted(cap["b1b"]), ["comment_4.wav", "preview.wav"])
        res = json.load(open(f"{self.tmp}/a2/audit/tts_generation_results.json", encoding="utf-8"))
        self.assertEqual(res["only_segments"], sorted(only))
        self.assertEqual(res["segments"]["comment_1"]["status"], "SKIPPED_NOT_SELECTED")
        self.assertNotIn("style_profile", res["segments"]["comment_1"])
        self.assertNotIn("style_profile", res["segments"]["full_story_part1"])
        self.assertEqual(res["segments"]["preview"]["style_profile"]["style_base_sha256"], sp.R2_SHA256)
        # 未生成segmentがあるresultsはM3 GateがBLOCK(Assemblyへ進めない)
        self.assertEqual(sp.m3_assembly_gate(V5, "a2", res)["status"], "BLOCK")

    def test_only_segments_rejected_outside_tts_stage(self):
        for argv_extra in (["--stage", "assemble"], ["--stage", "all"], ["--dry-run"]):
            argv = ["x", "--slug", "s", "--run", "r", "--out-dir", f"{self.tmp}/o", "--only-segments", "preview"] + argv_extra
            with mock.patch("sys.argv", argv):
                with self.assertRaises(SystemExit):
                    runner.main()
        self.assertFalse(os.path.exists(f"{self.tmp}/o"))


class V5M3GateTests(unittest.TestCase):
    @staticmethod
    def _a2_support_entry(fallback=False, base=None):
        return {"status": "OK", "fallback_used": fallback, "canonical_text": "t",
                "style_profile": {"profile_id": V5, "role": "SUPPORT_JA", "expected_base_sha256": sp.R2_SHA256,
                                  "style_base_sha256": base or sp.R2_SHA256}}

    @staticmethod
    def _kp_entry(style=None, status="OK", base=None):
        style = sp.P3_TEXT if style is None else style
        return {"status": status, "canonical_text": "t",
                "attempts_log": [{"attempt": 1, "style_prefix": {"sha256": _sha(style), "head200": style[:200], "len": len(style)}}],
                "en_pronunciation_resolver_info": {"hints_applied": False, "cache_hits": []},
                "style_profile": {"profile_id": V5, "role": "KP_EXPLANATION_EN", "expected_base_sha256": sp.P3_SHA256,
                                  "style_base_sha256": base or sp.P3_SHA256}}

    def _a2_results(self, **mut):
        segs = {n: _std_entry() for n in sp.ROLE_SEGMENTS["FULL_STORY"]}
        for n in sp.ROLE_SEGMENTS["SUPPORT_JA"]:
            segs[n] = self._a2_support_entry()
        for n, fn in mut.items():
            fn(segs[n])
        return {"segments": segs}

    def test_a2_pass_and_blocks(self):
        g = sp.m3_assembly_gate(V5, "a2", self._a2_results())
        self.assertEqual(g["status"], "PASS", g)
        self.assertEqual(len(g["checked"]), 8)
        for mut, reason in ((lambda e: e.update(fallback_used=True), "JA_FALLBACK_USED_OR_UNKNOWN"),
                            (lambda e: e.pop("fallback_used"), "JA_FALLBACK_USED_OR_UNKNOWN"),
                            (lambda e: e["style_profile"].update(style_base_sha256="0" * 64), "STYLE_BASE_SHA_MISMATCH_OR_MISSING"),
                            (lambda e: e.update(local_rewrite_recovery={"x": 1}), "LOCAL_REWRITE_RECOVERY")):
            g = sp.m3_assembly_gate(V5, "a2", self._a2_results(comment_4=mut))
            self.assertEqual(g["status"], "BLOCK")
            self.assertEqual([b["segment"] for b in g["blocked"]], ["comment_4"])
            self.assertIn(reason, g["blocked"][0]["violations"])

    def test_a2_missing_support_record_blocks(self):
        res = self._a2_results()
        del res["segments"]["comment_2"]
        g = sp.m3_assembly_gate(V5, "a2", res)
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("NO_SEGMENT_RECORD", g["blocked"][0]["violations"])

    def test_b1b_kp_explanation_gate(self):
        res = {"segments": {n: _adv_entry() for n in sp.ROLE_SEGMENTS["FULL_STORY"]},
               "key_phrases": {"1": {"explanation": self._kp_entry()}, "2": {"explanation": self._kp_entry()}}}
        g = sp.m3_assembly_gate(V5, "b1b", res)
        self.assertEqual(g["status"], "PASS", g)
        self.assertEqual(sorted(n for n in g["checked"] if n.startswith("kp")), ["kp1_explanation", "kp2_explanation"])
        # P0(旧style)で生成された解説clipはBLOCK
        p0 = fl_styles.KEY_PHRASE_EXPLANATION_EN
        res["key_phrases"]["2"]["explanation"] = self._kp_entry(style=p0, base=sp.sha256_text(p0))
        g = sp.m3_assembly_gate(V5, "b1b", res)
        self.assertEqual(g["status"], "BLOCK")
        self.assertEqual([b["segment"] for b in g["blocked"]], ["kp2_explanation"])
        # STOPPED(text gate)もBLOCK
        res["key_phrases"]["2"]["explanation"] = {"status": "STOPPED", "canonical_text": "t"}
        self.assertEqual(sp.m3_assembly_gate(V5, "b1b", res)["status"], "BLOCK")
        # KP hint追記時はhead200で判定
        hinted = sp.P3_TEXT + " Pronunciation: x."
        e = self._kp_entry(style=hinted)
        e["en_pronunciation_resolver_info"] = {"hints_applied": True, "cache_hits": [{"surface": "x"}]}
        res["key_phrases"]["2"]["explanation"] = e
        self.assertEqual(sp.m3_assembly_gate(V5, "b1b", res)["status"], "PASS")

    def test_default_and_p8_gates_unaffected_by_v5_roles(self):
        res = {"segments": {n: _adv_entry() for n in sp.ROLE_SEGMENTS["FULL_STORY"]}}
        self.assertEqual(sp.m3_assembly_gate("coffee_p8", "b1b", res)["status"], "PASS")
        self.assertEqual(sp.m3_assembly_gate("default", "a2", {})["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
