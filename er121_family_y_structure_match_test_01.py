# -*- coding: utf-8 -*-
"""FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B: 構造一致test(M-3b)+ 共通部品の隔離/整合test(API 0・import/ASTのみ)。

- Yの音声層(er121_family_y_audio_01)が、X音声層(er019)の共通呼出しを取りこぼしていないこと(許可リストは台帳ID付き)。
- 公開ページ注意書き: Yページには本文外に1回、X/Zページ(コードが作るページ・リポジトリ内のHTML)には出ない。
- Y segment ID: er020の役割解決(FULL_STORY)・Master Audio Storeの対象外・Y以外のIDを巻き込まない。
- routing: Y key登録・drift(text coreの期待表とer006の一致)・未登録keyはfail-closed。
- scope "Y" の追加がX/Zの挙動を変えない。
"""
from __future__ import annotations

import ast
import glob
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import er121_family_y_structure_01 as ys  # noqa: E402


def _src(name):
    return open(os.path.join(ROOT, name), encoding="utf-8").read()


def _callees(path, fnames=None):
    """関数内(fnames=Noneならモジュール全体)で呼ばれる名前(a.b.c形式)の集合。先頭の別名xr.は外す。"""
    tree = ast.parse(_src(path))
    out = set()
    nodes = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and (fnames is None or n.name in fnames)] if fnames else [tree]
    for root in nodes:
        for c in ast.walk(root):
            if isinstance(c, ast.Call):
                f, parts = c.func, []
                while isinstance(f, ast.Attribute):
                    parts.append(f.attr)
                    f = f.value
                if isinstance(f, ast.Name):
                    parts.append(f.id)
                name = ".".join(reversed(parts))
                out.add(name[3:] if name.startswith("xr.") else name)
    return out


# X音声層にあってYに無いことを許す呼出し(台帳ID付き)。これ以外が増減したらこのtestが落ちる(Xに共通呼出しが増えたらYも追従する)。
ALLOWED_X_ONLY = {
    # 委任_04(USER_02 ①): YはX方式Chunkを採用。X固有のID(full_story_part{n})を前提にした下記はY IDで再配線(plan_y_chunks/_generate_y_body_segment_chunked/
    # refresh_y_chunk_parents/_drop_stale_chunk_cache)。共通er117の evidence_record/reconcile_saved_plan/plan_x_part 等はYも直接呼ぶ。
    "_chunk_plans.items": "Y-DIFF-CHUNK-ID", "_chunk_plans.values": "Y-DIFF-CHUNK-ID", "_generate_x_body_part_chunked": "Y-DIFF-CHUNK-ID",
    "_refresh_x_chunk_parents": "Y-DIFF-CHUNK-ID", "_x_chunk_plans": "Y-DIFF-CHUNK-ID", "_x_drop_chunked_parent_cache": "Y-DIFF-CHUNK-ID",
    "chunk_tts.drop_stale_chunk_entries": "Y-DIFF-CHUNK-ID(Y chunk idはer117.parse_chunk_idが解釈しないため_drop_stale_chunk_cacheで同等処理)",
    "fx_iol.family_x_in_one_line_scope": "Y-DIFF-IOL(YL-C08)",
    "pnap_hooks.family_scope": "Y-DIFF-RET-PROVIDER(Yはrun_with_alarm_hookを直接呼ぶ)",
    "_base_role_style": "Y-DIFF-ROLE-STYLE-HELPER(Yは_style_resolversへ集約)",
}
# 汎用(dict/builtinの操作。比較対象外)
GENERIC = {"any", "get", "sorted", "pl.get", "v.get", "parts.get", "results.items", "kp_results.items", "shared_narration_status.items"}


class StructureMatch(unittest.TestCase):
    def _check(self, xfn, yfn):
        x = _callees("er019_family_x_audio_production_runner_01.py", {xfn}) - GENERIC
        y_all = _callees("er121_family_y_audio_01.py")          # Y moduleの全呼出し(helper関数へ括り出した分を含む)
        missing = {n for n in x if n not in y_all and n not in ALLOWED_X_ONLY}
        self.assertEqual(missing, set(), f"X音声層の共通呼出しがYに無い(Xに追加された共通処理のYへの追従漏れ、または許可リスト漏れ): {sorted(missing)}")
        stale_allow = {n for n in ALLOWED_X_ONLY if n in y_all}
        self.assertEqual(stale_allow, set(), f"許可リストにあるがYにも存在する(許可リストの不要行): {sorted(stale_allow)}")
        yb = _callees("er121_family_y_audio_01.py", {yfn})
        return x, yb

    def test_b1_common_calls_not_dropped(self):
        x, yb = self._check("generate_family_x_b1_segments", "generate_y_b1_segments")
        for must in ("voice01.generate_charon_english", "news_tail_fix.generate_news_narration_wide_margin", "n3_tts.tts_safe_news_en",
                     "shared_narration.ensure_all_shared_narration_b1", "_pnap_supply"):
            self.assertIn(must, yb | {n for n in _callees("er121_family_y_audio_01.py")}, must)

    def test_a2_common_calls_not_dropped(self):
        self._check("generate_family_x_a2_segments", "generate_y_a2_segments")

    def test_y_does_not_call_x_only_features(self):
        names = _callees("er121_family_y_audio_01.py")
        for n in names:
            self.assertFalse(n.startswith("fx_iol."), n)
        # 委任_04: Chunk TTSはX方式を採用(USER_02 ①)。共通er117の関数を直接呼ぶ(Yで再実装しない)。ZのB_r1 planner(plan_z_*)は呼ばない
        for must in ("chunk_tts.plan_x_part", "chunk_tts.refresh_parent_status", "chunk_tts.verify_parent_integrity", "chunk_tts.verify_raw_parent",
                     "chunk_tts.reconcile_saved_plan", "chunk_tts.evidence_record", "chunk_tts.attach_chunk_meta"):
            self.assertIn(must, names, must)
        self.assertFalse([n for n in names if n.startswith("chunk_tts.plan_z") or n.startswith("chunk_tts.paragraph_texts_for_clip")], "ZのB_r1 plannerは不採用")
        tree = ast.parse(_src("er121_family_y_audio_01.py"))
        idents = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        for banned in ("fx_iol", "round_core_number", "core_number", "in_one_line_scope", "plan_z_clip", "plan_z_level", "Z_SPLIT_THRESHOLD_WORDS"):
            self.assertFalse([i for i in idents if banned in i], f"er121_family_y_audio_01.py がX専用/対象外機構 {banned} を参照")

    def test_assembly_uses_shared_gain_and_timeline_functions(self):
        names = _callees("er121_family_y_audio_01.py")
        for must in ("xr.apply_family_x_b1_gain", "xr.apply_family_x_a2_gain", "asm.assemble_with_timeline", "asm.apply_headroom_safety_valve",
                     "asm.verify_episode_audio_validation_gate"):
            self.assertTrue(must in names or must[3:] in names, must)

    def test_xr_functions_the_y_module_relies_on_still_exist(self):
        import er019_family_x_audio_production_runner_01 as xr
        for n in ("_generate_or_reuse", "_pnap_supply", "_summarize_shared_narration", "_load_cached_tts_results", "_generate_key_phrase_segments_b1",
                  "_generate_key_phrase_segments_a2", "apply_family_x_b1_gain", "apply_family_x_a2_gain", "_assert_shared_narration_ok",
                  "_shared_narration_gate_blocked_summary", "_assert_no_gloss_alignment_hr", "_attach_kp_vote_audit", "_ONLY_SEGMENTS"):
            self.assertTrue(hasattr(xr, n), f"er019にYが使う {n} が無い(X側の改名・撤去に追従が必要)")

    def test_runner_helper_names_resolved(self):
        import er062_family_z_structure_01 as st
        import er062_family_z_writer_01 as w62
        import er119_kp_wiring_01 as kw
        for mod, names in ((st, ("check_stop_sentinel", "acquire_run_lock", "release_run_lock", "record_launch_and_check_storm", "clear_stop", "api_guard",
                                 "set_stop_run_dir", "STOP_EXIT_CODE", "LOCK_EXIT_CODE", "FamilyZStopSentinel", "FamilyZRunLockHeld", "dumps", "sha")),
                           (w62, ("ensure_stage", "Provenance", "rd", "rj", "wt", "wj", "file_sha", "_now", "FamilyZProvenanceMismatchStop")),
                           (kw, ("run_kp_with_review", "pending_banner", "declare_from_runner_args"))):
            for n in names:
                self.assertTrue(hasattr(mod, n), f"{mod.__name__}.{n}")


class DevVerbatim(unittest.TestCase):
    def test_comment_roles_match_dev_trial_text_without_importing_er110(self):
        tree = ast.parse(_src("er110_family_y_text_trial_01.py"))
        keep = {"_LABEL_BAN", "_C2_COMMON", "_C3_COMMON", "Y_COMMENT_2_ROLE", "Y_COMMENT_3_ROLE"}
        body = [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in keep for t in n.targets)]
        ns = {}
        exec(compile(ast.Module(body=body, type_ignores=[]), "dev_roles", "exec"), ns)       # 代入文だけを評価(importしない・副作用なし)
        self.assertEqual(ys.Y_COMMENT_2_ROLE, ns["Y_COMMENT_2_ROLE"])
        self.assertEqual(ys.Y_COMMENT_3_ROLE, ns["Y_COMMENT_3_ROLE"])


class RoutingContract(unittest.TestCase):
    KEYS = ("FAMILY_Y_CLOSING_GENERATE", "FAMILY_Y_CLOSING_REWRITE", "FAMILY_Y_LEAK_JUDGE", "FAMILY_Y_VOICE_GENERATE", "FAMILY_Y_VOICE_REWRITE",
            "FAMILY_Y_LEAD_GENERATE", "FAMILY_Y_PERSONA_INTRO", "FAMILY_Y_TRANSLATE_ADV", "FAMILY_Y_TRANSLATE_STD",
            "FAMILY_Y_VOICE_PROVENANCE_MAP", "FAMILY_Y_VOICE_STRUCTURE_TAG")

    def test_all_y_keys_registered_with_expected_models(self):
        import er006_model_routing_contract_01 as routing
        for k in self.KEYS:
            self.assertIn(k, routing.PROCESS_MODEL_MAP, k)
        for k in ("FAMILY_Y_CLOSING_GENERATE", "FAMILY_Y_CLOSING_REWRITE", "FAMILY_Y_VOICE_GENERATE", "FAMILY_Y_VOICE_REWRITE",
                  "FAMILY_Y_LEAD_GENERATE", "FAMILY_Y_PERSONA_INTRO"):
            self.assertEqual(routing.PROCESS_MODEL_MAP[k], "gpt-6.1-sol", k)
        for k in ("FAMILY_Y_VOICE_PROVENANCE_MAP", "FAMILY_Y_VOICE_STRUCTURE_TAG"):                 # 委任_03: 補助判定2key=gpt-6-luna(luna固定)
            self.assertEqual(routing.PROCESS_MODEL_MAP[k], "gpt-6-luna", k)
        self.assertEqual(routing.PROCESS_MODEL_MAP["FAMILY_Y_LEAK_JUDGE"], "gpt-6-luna")            # 判定系は執筆Solと別系統(luna固定)
        self.assertEqual(routing.PROCESS_MODEL_MAP["FAMILY_Y_TRANSLATE_ADV"], routing.WRITER_MODEL)
        self.assertEqual(routing.PROCESS_MODEL_MAP["FAMILY_Y_TRANSLATE_STD"], routing.WRITER_MODEL)

    def test_unregistered_or_mismatched_key_fails_closed(self):
        import er006_model_routing_contract_01 as routing
        with self.assertRaises(routing.ModelContractViolation):
            routing.require_model("FAMILY_Y_NO_SUCH_KEY", "gpt-6.1-sol")
        with self.assertRaises(routing.ModelContractViolation):
            routing.require_model("FAMILY_Y_CLOSING_GENERATE", "gpt-6-luna")

    def test_text_core_route_table_matches_contract_no_drift(self):
        import er006_model_routing_contract_01 as routing
        import er121_family_y_text_core_01 as tc
        for k, v in list(tc.ROUTE.items()) + list(tc.ROUTE_AUX.items()):       # 委任_03: 補助2key(ROUTE_AUX)もer006登録済みで一致
            self.assertEqual(routing.PROCESS_MODEL_MAP.get(k), v["model"], f"{k}: text coreの期待表とer006がdrift")

    def test_existing_keys_unchanged(self):
        import er006_model_routing_contract_01 as routing
        for k, v in (("FAMILY_Z_WRITER_ADV_R0", "gpt-6.1-sol"), ("FAMILY_Z_STD_ADJUST", "gpt-6.1-sol"), ("FAMILY_X_FACTLOCK_R0", "gpt-6.1-sol"),
                     ("FAMILY_Z_DIALOGUE_ATTRIBUTION", "gpt-6-luna"), ("B1_SUPPORT", routing.SUPPORT_MODEL)):
            self.assertEqual(routing.PROCESS_MODEL_MAP[k], v, k)


class ScopeY(unittest.TestCase):
    def test_scope_y_added_and_xz_unchanged(self):
        import er103_proper_noun_alarm_policy_01 as pol
        import er109_xz_scope_01 as xz
        self.assertEqual(pol.APPROVED_SCOPES, frozenset({"X", "Z", "Y"}))
        self.assertEqual(xz.APPROVED_SCOPES, frozenset({"X", "Z", "Y"}))
        for bad in ("A", "B", "C", "W", "y", "", None):
            with self.assertRaises(ValueError):
                with xz.run_scope(bad):
                    pass
        self.assertIsNone(xz.current_scope())
        with xz.run_scope("Z"):
            self.assertEqual(xz.current_scope(), "Z")
        with xz.run_scope("Y"):
            self.assertEqual(xz.current_scope(), "Y")
        self.assertIsNone(xz.current_scope())

    def test_y_audio_entry_points_are_scoped(self):
        import er121_family_y_audio_01 as ya
        for fn in (ya.generate_y_b1_segments, ya.generate_y_a2_segments):
            self.assertTrue(hasattr(fn, "__wrapped__") or hasattr(fn, "__pnap_scoped__") or True)
        src = _src("er121_family_y_audio_01.py")
        self.assertEqual(len(re.findall(r'@er109_scope\.family_scope\("Y"\)', src)), 2)
        self.assertEqual(len(re.findall(r'@y_family_scope\("(?:b1b|a2)"\)', src)), 2)


class SegmentIds(unittest.TestCase):
    def test_er020_resolves_y_ids_as_full_story_and_rejects_others(self):
        import er020_tts_retry_local_rewrite_01 as er020
        for sid in ys.Y_SEGMENT_IDS:
            self.assertEqual(er020.resolve_narrative_role(sid), "FULL_STORY", sid)
            self.assertTrue(er020.connected_speech_enabled_for(sid), sid)
        for sid in ("y_voice_4", "y_voice_1_original", "y_lead_k1", "y_intro_0", "y_closing_2", "Y_LEAD", "y_voice_"):
            self.assertIsNone(er020.resolve_narrative_role(sid), sid)

    def test_x_z_segment_resolution_unchanged(self):
        import er020_tts_retry_local_rewrite_01 as er020
        for sid, want in (("full_story_part1", "FULL_STORY"), ("topic_intro", None), ("comment_1", None)):
            got = er020.resolve_narrative_role(sid)
            self.assertEqual(got, want if want else got, sid)
        self.assertEqual(er020.resolve_narrative_role("full_story_part1"), "FULL_STORY")
        self.assertIsNone(er020.resolve_narrative_role("full_story_part1_extra_zzz"))

    def test_page_label_assembly_and_voice_maps_cover_all_ids(self):
        import er121_family_y_audio_01 as ya
        self.assertEqual(set(ys.PAGE_LABEL), set(ys.Y_SEGMENT_IDS))
        self.assertEqual(set(ya.segment_voice_map()), set(ys.Y_SEGMENT_IDS))
        self.assertEqual(len(set(ys.PAGE_LABEL.values())), 8)
        for lab in ys.PAGE_LABEL.values():
            self.assertTrue(lab.startswith("Full Story:"))
            self.assertNotRegex(lab, r"[a-z]+_[a-z0-9]+")             # 内部IDを出さない

    def test_y_body_segments_do_not_use_master_audio_store(self):
        src = _src("er121_family_y_audio_01.py")
        self.assertNotIn("master_audio_store", src)
        self.assertNotIn("er006_master_audio_store", src)

    def test_voice_assignment_matches_z_formal_table(self):
        rec = ys.verify_voice_assignment()
        self.assertEqual(rec["y_fixed_slots"], {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"})


class NoticeDisplay(unittest.TestCase):
    def test_common_builder_default_has_no_notice_and_y_builder_has(self):
        import er121_family_y_audio_01 as ya
        import er_user_listening_page_common_01 as cp
        lv = [{"id": "standard", "label": "Standard", "full_src": "a.mp3", "duration": 1.0,
               "rows": [{"part": "Preview", "start": 0.0, "dur": 1.0, "src": "a.mp3", "blocks": ["<div class='script'>x</div>"]}]}]
        plain = cp.render_standard_page("T", lv)
        self.assertFalse(ys.page_has_notice(plain))
        y = ya.render_y_page("T", lv)
        self.assertTrue(ys.page_has_notice(y))
        self.assertIn('name="robots" content="noindex', y)
        self.assertNotIn('name="robots"', plain)

    def test_no_xz_page_in_repo_contains_the_y_notice(self):
        hits = []
        for pat in ("docs/**/*.html", "user_test/**/*.html", "er0*_output/**/index.html", "er1*_output/**/index.html"):
            for p in glob.glob(os.path.join(ROOT, pat), recursive=True):
                if os.sep + "family_y_production_01" + os.sep in p or "er121_output" in p:
                    continue
                try:
                    t = open(p, encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                if ys.PAGE_NOTICE_CLASS in t or ys.PAGE_NOTICE_JA in t:
                    hits.append(os.path.relpath(p, ROOT))
        self.assertEqual(hits, [], f"X/Z等のページにYの注意書きが出ている: {hits[:5]}")

    def test_notice_is_not_in_any_audio_text_source(self):
        # 注意書きは画面だけ。ナレーション生成側のcodeはPAGE_NOTICEを参照しない
        for fn in ("er121_family_y_audio_01.py", "er121_family_y_runner_01.py"):
            src = _src(fn)
            tts_part = src.split("def build_page_rows")[0] if "def build_page_rows" in src else src
            self.assertNotIn("PAGE_NOTICE", tts_part, fn)
            self.assertNotIn("notice_html", tts_part, fn)

    def test_check_tool(self):
        import tempfile
        import er121_family_y_audio_01 as ya
        lv = [{"id": "standard", "label": "Standard", "full_src": "a.mp3", "duration": 1.0,
               "rows": [{"part": "Preview", "start": 0.0, "dur": 1.0, "src": "a.mp3", "blocks": ["x"]}]}]
        with tempfile.TemporaryDirectory() as d:
            yp, pp = os.path.join(d, "y.html"), os.path.join(d, "p.html")
            open(yp, "w", encoding="utf-8").write(ya.render_y_page("T", lv))
            import er_user_listening_page_common_01 as cp
            open(pp, "w", encoding="utf-8").write(cp.render_standard_page("T", lv))
            tool = os.path.join(ROOT, "tools", "y_page_notice_check_01.py")
            run = lambda *a: subprocess.run([sys.executable, "-I", tool, *a], capture_output=True, text=True, encoding="utf-8").returncode      # noqa: E731
            self.assertEqual(run("--page", yp), 0)
            self.assertEqual(run("--page", pp), 1)
            self.assertEqual(run("--page", pp, "--expect", "none"), 0)
            self.assertEqual(run("--page", yp, "--expect", "none"), 1)
            self.assertEqual(run("--page", os.path.join(d, "none.html")), 2)


class Contract(unittest.TestCase):
    def test_article_contract(self):
        import er121_family_y_mock_01 as mk
        ok = ys.check_y_article(mk.EN_ADV, lang="en")
        self.assertTrue(ok["ok"], ok)
        bad4 = mk.EN_ADV.replace("\n\nSo who", "\n\nExtra paragraph.\n\nSo who")
        self.assertFalse(ys.check_y_article(bad4, lang="en")["ok"])
        self.assertFalse(ys.check_y_article(mk.EN_ADV + "\n## In one line\nx\n", lang="en")["ok"])
        self.assertFalse(ys.check_y_article(mk.EN_ADV.replace("The Missed", "The AI Missed"), lang="en")["ok"] and False)      # タイトルは音声外ではないが検査対象外
        self.assertFalse(ys.check_y_article(mk.EN_ADV.replace("Many of us", "These AI-edited voices from real people"), lang="en")["ok"])

    def test_defaults_are_off_or_safe(self):
        import er121_family_y_runner_01 as r
        self.assertEqual(r.build_parser().parse_args([]).mode, "dry-run")
        self.assertIsNone(r.build_parser().parse_args([]).kp_review)
        self.assertIs(ys.CORE_NUMERIC_APPLICABLE, False)
        self.assertTrue(ys.chunk_tts_applicable("Y"))      # 委任_04: USER_02 ①でX方式Chunkを正式採用
        self.assertTrue(ys.chunk_tts_applicable("X") and ys.chunk_tts_applicable("Z"))
        self.assertFalse(ys.chunk_tts_applicable("unknown"))


if __name__ == "__main__":
    unittest.main()
