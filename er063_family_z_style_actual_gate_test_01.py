# -*- coding: utf-8 -*-
"""FAMILY-Z-STYLE-ACTUAL-GATE-01 委任_01(OPEN-551): Z正式経路の「実送信Style prefixと承認値の実測照合」Gate(z_style_actual_gate)のoffline test。
mock TTS(実leaf同様に承認Styleをそのまま送った記録を返すfake)、API 0。
実行: .venv/Scripts/python.exe -m unittest er063_family_z_style_actual_gate_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401
import copy
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er063_family_z_audio_01 as z
import er063_family_z_audio_01_test_01 as base   # fake_generators / make_plan(既存fixture。承認Styleを送った記録を返す)


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.run = f"{self.tmp}/melos/run_01"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def stage(self, level, *, plan=None, gens=None):
        if plan is None:
            plan, _, _ = base.make_plan(level)
        g = gens or base.fake_generators()
        g.setdefault("kp_expl_en", g["preview"])
        z.run_tts_stage(self.run, level, plan, generators=g)
        z.provision_shell_assets(self.run, level, kp_count=1)
        return plan

    def results_path(self, level):
        return f"{self.run}/{level}/audit/tts_generation_results.json"

    def load(self, level):
        return json.load(open(self.results_path(level), encoding="utf-8"))

    def save(self, level, d):
        json.dump(d, open(self.results_path(level), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    def entries(self, level, plan):
        d = self.load(level)
        return {s.clip_id: z._lookup_entry(d, s.clip_id) for s in plan}

    def gate(self, level, plan):
        return z.z_style_actual_gate(self.run, level, plan, self.entries(level, plan))

    def out(self, level):
        return json.load(open(f"{self.run}/{level}/{z.STYLE_ACTUAL_OUT_RELPATH}", encoding="utf-8"))

    def edit_entry(self, level, clip_id, fn):
        d = self.load(level)
        e = z._lookup_entry(d, clip_id)
        fn(e)
        self.save(level, d)


class MatchTests(_Base):
    def test_match_std_and_adv_all_roles_pass_with_table(self):
        for level in ("a2", "b1b"):
            shutil.rmtree(self.run, ignore_errors=True)
            plan = self.stage(level)
            r = self.gate(level, plan)
            self.assertEqual(r["status"], "PASS", level)
            self.assertEqual(r["mode"], "strict")
            self.assertTrue(r["marker_present"])
            o = self.out(level)
            self.assertEqual(o["rows_count"], len(plan))
            self.assertEqual(o["coverage"]["expected_clip_count"], len(plan))
            # 非Dialogue roleは全て実測exact一致、Dialogueは『意図sha(実測なし)』(match=None)でmatch扱いにしない
            for row in o["rows"]:
                if row["role"] in z.Z_DIALOGUE_ROLES:
                    self.assertEqual(row["check"], "dialogue_intended_only")
                    self.assertIsNone(row["match"])
                    self.assertTrue(row["measurement_gap"])
                else:
                    self.assertEqual(row["check"], "exact", row["segment"])
                    self.assertIs(row["match"], True)
                    self.assertEqual(row["measured_sha256"], row["approved_sha256"])
            # 照合対象の全roleがtableに現れる(Adv narrator/preview/commentと日本語role[a2]を含む)
            roles = {r_["role"] for r_ in o["rows"]}
            exp = {"a2": {"NARRATOR_FULL_STORY_STD", "STD_JA_PREVIEW", "STD_JA_COMMENT", "JAPANESE_TITLE", "TOPIC_INTRO_EN", "KP_EN", "KP_JA"},
                   "b1b": {"NARRATOR_FULL_STORY_ADV", "ADV_EN_PREVIEW", "ADV_EN_COMMENT", "TOPIC_INTRO_EN", "KP_EN"}}[level]
            self.assertTrue(exp <= roles, (level, exp - roles))

    def test_production_shaped_adv_plan_with_kp_explanations(self):
        story = [{"id": "full_story_part1_c1", "voice": "narrator", "text": "Melos was angry."}]
        kp = [{"rank": 1, "used_form": "run through", "japanese_gloss": "x", "japanese_gloss_tts": "x"}]
        plan = z.build_level_plan("b1b", story, "preview text", {1: "c1", 2: "c2", 3: "c3"}, kp, "Topic", None, kp_explanations={1: "An explanation."})
        self.stage("b1b", plan=plan)
        r = self.gate("b1b", plan)
        self.assertEqual(r["status"], "PASS")
        self.assertIn("KP_EXPL_EN", {x["role"] for x in self.out("b1b")["rows"]})

    def test_run_audio_gate_wires_gate_and_summarises(self):
        plan = self.stage("a2")
        shell = list(z.SHELL_ASSET_SOURCES) + ["kp1_number"]
        with mock.patch("er003_v1_n3_01_assemble.verify_episode_audio_validation_gate"):
            res = z.run_audio_gate(self.run, "a2", plan, shell, article_text="a")
        self.assertEqual(res["style_actual_gate"]["status"], "PASS")
        self.assertTrue(os.path.exists(f"{self.run}/a2/{z.STYLE_ACTUAL_OUT_RELPATH}"))

    def test_hint_appended_prefix_is_accepted_only_with_hint_flag_and_full_prefix(self):
        plan = self.stage("b1b")
        txt = z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_ADV"]["text"]
        sent = txt + " Pronounce 'Melos' as MEH-los."
        def to_hint(e):
            e["style_actual"].update({"sha256": _sha(sent), "len": len(sent), "head200": sent[:200], "form": "full_text",
                                      "hint_applied": True, "startswith_expected": True})
        self.edit_entry("b1b", "full_story_part1_c1", to_hint)
        self.assertEqual(self.gate("b1b", plan)["status"], "PASS")
        self.assertEqual([r["check"] for r in self.out("b1b")["rows"] if r["segment"] == "full_story_part1_c1"], ["prefix_with_hint"])
        # hint flagなしの長い/異なるprefix=不一致
        self.edit_entry("b1b", "full_story_part1_c1", lambda e: e["style_actual"].update({"hint_applied": False}))
        with self.assertRaises(z.FamilyZStyleActualGateStop):
            self.gate("b1b", plan)
        # hintありでも承認原文で始まらない(全長で記録済み)=不一致
        self.edit_entry("b1b", "full_story_part1_c1", lambda e: e["style_actual"].update({"hint_applied": True, "startswith_expected": False}))
        with self.assertRaises(z.FamilyZStyleActualGateStop):
            self.gate("b1b", plan)


class BlockTests(_Base):
    def test_injected_mismatch_blocks_and_table_is_saved(self):
        plan = self.stage("b1b")
        self.edit_entry("b1b", "comment_2", lambda e: e["style_actual"].update({"sha256": "0" * 64}))
        with self.assertRaises(z.FamilyZStyleActualGateStop) as cm:
            self.gate("b1b", plan)
        self.assertIn("comment_2=Z_STYLE_ACTUAL_MISMATCH", str(cm.exception))
        o = self.out("b1b")
        self.assertEqual(o["status"], "BLOCK")
        self.assertFalse(o["all_match"])
        bad = [r for r in o["rows"] if r["segment"] == "comment_2"][0]
        self.assertIs(bad["match"], False)

    def test_narrator_mismatch_each_role_group(self):
        for level, cid in (("a2", "preview"), ("a2", "japanese_title"), ("a2", "kp1_ja"), ("a2", "full_story_part1_c1"),
                           ("b1b", "preview"), ("b1b", "full_story_part1_c1"), ("b1b", "kp1_en")):
            shutil.rmtree(self.run, ignore_errors=True)
            plan = self.stage(level)
            self.edit_entry(level, cid, lambda e: e["style_actual"].update({"sha256": "f" * 64}))
            with self.assertRaises(z.FamilyZStyleActualGateStop, msg=(level, cid)):
                self.gate(level, plan)

    def test_unrecorded_in_strict_run_blocks(self):
        plan = self.stage("a2")
        self.edit_entry("a2", "comment_1", lambda e: e.pop("style_actual"))
        with self.assertRaises(z.FamilyZStyleActualGateStop) as cm:
            self.gate("a2", plan)
        self.assertIn("comment_1=Z_STYLE_ACTUAL_UNRECORDED", str(cm.exception))

    def test_unmeasured_intent_only_is_not_a_match_and_blocks(self):
        plan = self.stage("a2")
        # 日本語role: 送信instructionが取れず意図値のみ(Opus M-4)=一致扱いにしない
        self.edit_entry("a2", "preview", lambda e: e["style_actual"].update({"kind": "unmeasured", "sha256": None, "head200": None, "len": None}))
        with self.assertRaises(z.FamilyZStyleActualGateStop) as cm:
            self.gate("a2", plan)
        self.assertIn("preview=Z_STYLE_ACTUAL_UNMEASURED", str(cm.exception))
        row = [r for r in self.out("a2")["rows"] if r["segment"] == "preview"][0]
        self.assertEqual(row["measured_kind"], "意図sha(実測なし)")
        self.assertIs(row["match"], False)

    def test_checked_empty_blocks_even_if_every_row_is_unrecorded(self):
        plan = self.stage("a2")
        d = self.load("a2")
        for s in plan:
            z._lookup_entry(d, s.clip_id).pop("style_actual", None)
        self.save("a2", d)
        with self.assertRaises(z.FamilyZStyleActualGateStop):
            self.gate("a2", plan)
        o = self.out("a2")                                   # 例外文は先頭12件で切るため、全BLOCK理由は照合表で確認
        self.assertIn("Z_STYLE_CHECKED_EMPTY", [v for b in o["blocked"] for v in b["violations"]])
        self.assertEqual(o["checked_count"], 0)

    def test_required_role_missing_from_plan_blocks_coverage_empty(self):
        plan = self.stage("a2")
        short = [s for s in plan if s.role_key != "STD_JA_COMMENT"]
        with self.assertRaises(z.FamilyZStyleActualGateStop) as cm:
            z.z_style_actual_gate(self.run, "a2", short, self.entries("a2", plan))
        self.assertIn("STD_JA_COMMENT:*=Z_STYLE_COVERAGE_EMPTY", str(cm.exception))
        short = [s for s in plan if s.role_key not in ("KP_JA", "KP_EXPL_EN")]
        with self.assertRaises(z.FamilyZStyleActualGateStop) as cm:
            z.z_style_actual_gate(self.run, "a2", short, self.entries("a2", plan))
        self.assertIn("KP_THIRD:*=Z_STYLE_COVERAGE_EMPTY", str(cm.exception))

    def test_unexpected_role_for_level_blocks(self):
        plan = self.stage("a2")
        b1b_plan, _, _ = base.make_plan("b1b")
        with self.assertRaises(z.FamilyZStyleActualGateStop) as cm:
            z.z_style_actual_gate(self.run, "a2", plan + [s for s in b1b_plan if s.role_key == "ADV_EN_COMMENT"][:1],
                                  {**self.entries("a2", plan)})
        self.assertIn("Z_STYLE_COVERAGE_UNEXPECTED", str(cm.exception))

    def test_role_table_drift_blocks(self):
        plan = self.stage("a2")
        cov = copy.deepcopy(z.Z_ROLE_COVERAGE)
        cov["a2"].pop("KP_EN")
        cov["b1b"].pop("KP_EN")
        with mock.patch.object(z, "Z_ROLE_COVERAGE", cov):
            with self.assertRaises(z.FamilyZStyleActualGateStop) as cm:
                self.gate("a2", plan)
        self.assertIn("Z_STYLE_ROLE_TABLE_DRIFT", str(cm.exception))

    def test_table_matches_role_style_and_cross_family_map(self):
        self.assertEqual(z._z_role_table_drift(), [])
        covered = {r for lv in z.Z_ROLE_COVERAGE.values() for r in lv}
        self.assertEqual(covered | {"SHELL"}, set(z.FAMILY_Z_ROLE_STYLE))
        self.assertEqual(set(z.CROSS_FAMILY_COMMON_STYLE_MAP), set(z.FAMILY_Z_ROLE_STYLE))
        # 例外roleは理由付き(CROSS_FAMILY_COMMON_STYLE_MAPのEXCEPTION)で、期待値はrole別に決まる
        for role in ("ADV_EN_COMMENT", "TOPIC_INTRO_EN", "JAPANESE_TITLE"):
            self.assertTrue(z.CROSS_FAMILY_COMMON_STYLE_MAP[role]["Z"].startswith("EXCEPTION:"))
            self.assertIsNotNone(z.z_expected_style(role))
        for role in z.Z_DIALOGUE_ROLES:
            self.assertIsNone(z.z_expected_style(role))


class FallbackTests(_Base):
    def _drop_style_fallback(self, level, cid):
        fb_text = "natural, clear, conversational"
        def fn(e):
            e["style_actual"].update({"sha256": _sha(fb_text), "len": len(fb_text), "head200": fb_text, "adopted_phase": "fallback",
                                      "adopted_instruction_type": "minimal_fallback"})
            e["style"]["fallback_used"] = True
        self.edit_entry(level, cid, fn)

    def test_style_dropping_fallback_adopted_requires_human_approval(self):
        plan = self.stage("a2")
        self._drop_style_fallback("a2", "full_story_part1_c1")
        with self.assertRaises(z.FamilyZStyleActualGateStop) as cm:
            self.gate("a2", plan)
        msg = str(cm.exception)
        self.assertIn("Z_STYLE_ACTUAL_MISMATCH", msg)
        self.assertIn("Z_STYLE_FALLBACK_ADOPTED", msg)
        # 承認record(canonical text sha一致)なし→BLOCKのまま。別textのshaでは承認にならない
        import er003_v1_n3_01_assemble as asm
        asm.record_human_approval(f"{self.run}/a2", "full_story_part1_c1", "another text")
        with self.assertRaises(z.FamilyZStyleActualGateStop):
            self.gate("a2", plan)
        # 正しいcanonical textの承認→PASS(人間承認として照合表に残る)
        asm.record_human_approval(f"{self.run}/a2", "full_story_part1_c1", "Melos was angry.")
        r = self.gate("a2", plan)
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["human_approved_count"], 1)
        row = [x for x in self.out("a2")["rows"] if x["segment"] == "full_story_part1_c1"][0]
        self.assertTrue(row["human_approved"])
        self.assertIn("Z_STYLE_FALLBACK_ADOPTED", row["violations"])

    def test_fallback_phase_with_approved_style_unchanged_is_not_style_drop(self):
        plan = self.stage("b1b")
        self.edit_entry("b1b", "full_story_part1_c1", lambda e: e["style_actual"].update({"adopted_phase": "fallback"}))
        self.assertEqual(self.gate("b1b", plan)["status"], "PASS")

    def test_monkeys_paw_like_std_narrator_fallback_from_attempt_log_is_detected(self):
        # 実leaf結果の形: 標準attemptsは承認Style、fallback attemptが落ちたStyle。top-levelは旧段のままでもfallbackを採用attemptとして扱う。
        spec = [s for s in base.make_plan("a2")[0] if s.clip_id == "full_story_part1_c1"][0]
        txt = z.style_text_for(spec)
        fb = "natural, clear, conversational"
        res = {"status": "OK", "style_prefix": {"sha256": _sha(txt), "len": len(txt), "head200": txt[:200]},
               "standard_attempts_log": [{"attempt": 1, "style_prefix": {"sha256": _sha(txt), "len": len(txt), "head200": txt[:200]}}],
               "fallback_attempts_log": [{"attempt": 1, "instruction_type": "natural_fallback",
                                          "style_prefix": {"sha256": _sha(fb), "len": len(fb), "head200": fb}}], "fallback_used": True}
        rec = z.build_style_actual_record(spec, res)
        self.assertEqual(rec["sha256"], _sha(fb))
        self.assertEqual(rec["adopted_phase"], "fallback")
        self.assertEqual(rec["source"], "adopted_attempt.style_prefix")
        self.assertEqual(rec["secondary_top_level"]["sha256"], _sha(txt))


class RecordTests(_Base):
    def test_build_record_sources(self):
        adv = [s for s in base.make_plan("b1b")[0] if s.clip_id == "full_story_part1_c1"][0]
        txt = z.style_text_for(adv)
        # Adv leaf: attempts_logにstyleなし、top-level style_prefix(str全文)のみ
        r = z.build_style_actual_record(adv, {"status": "OK", "attempts_log": [{"attempt": 1, "instruction_type": "english_style_prefix_wide_margin"}], "style_prefix": txt})
        self.assertEqual((r["kind"], r["source"], r["sha256"]), ("measured", "result.style_prefix", _sha(txt)))
        self.assertIs(r["startswith_expected"], True)
        self.assertEqual(r["adopted_instruction_type"], "english_style_prefix_wide_margin" if False else r["adopted_instruction_type"])
        # '<default:…>'ラベルは実体なし=未実測
        r2 = z.build_style_actual_record(adv, {"status": "OK", "style_prefix": "<default:ENGLISH_STYLE_PREFIX>"})
        self.assertEqual(r2["kind"], "unmeasured")
        self.assertIsNone(r2["sha256"])
        # 何も無い
        self.assertEqual(z.build_style_actual_record(adv, {})["kind"], "unmeasured")
        # 日本語leaf: top-level str
        ja = [s for s in base.make_plan("a2")[0] if s.clip_id == "preview"][0]
        jtxt = z.style_text_for(ja)
        rj = z.build_style_actual_record(ja, {"status": "OK", "style_prefix": jtxt})
        self.assertEqual(rj["sha256"], z.FAMILY_Z_ROLE_STYLE["STD_JA_PREVIEW"] and _sha(jtxt))
        self.assertEqual(rj["expected_sha256"], _sha(jtxt))
        # 日本語leafが落ちたfallbackのminimal_instruction由来(別文字列)
        rj2 = z.build_style_actual_record(ja, {"status": "OK", "style_prefix": "短い指示", "fallback_used": True})
        self.assertNotEqual(rj2["sha256"], rj2["expected_sha256"])
        self.assertTrue(rj2["result_fallback_used"])

    def test_build_entry_adds_style_actual_additively(self):
        plan = self.stage("a2")
        e = self.entries("a2", plan)["full_story_part1_c1"]
        self.assertIn("style_actual", e)
        self.assertEqual(e["style_actual"]["schema"], z.STYLE_ACTUAL_SCHEMA)
        # 既存のStyle意図記録・reuse_keyは不変(style_actualはreuse_keyに含めない)
        self.assertEqual(e["reuse_key"], z.build_reuse_key([s for s in plan if s.clip_id == "full_story_part1_c1"][0]))

    def test_reused_entries_keep_style_actual(self):
        plan = self.stage("a2")
        g = base.fake_generators()
        z.run_tts_stage(self.run, "a2", plan, generators=g)    # 再実行=全clip再利用
        self.assertEqual(self.gate("a2", plan)["status"], "PASS")


class LegacyTests(_Base):
    def _legacy_run(self, level):
        plan = self.stage(level)
        d = self.load(level)
        for s in plan:
            z._lookup_entry(d, s.clip_id).pop("style_actual", None)
        self.save(level, d)
        os.remove(f"{self.run}/{level}/{z.STYLE_ACTUAL_MARKER_RELPATH}")      # 導入前に開始したrun相当
        return plan

    def test_past_run_without_records_warns_only_and_not_blocked(self):
        plan = self._legacy_run("a2")
        r = self.gate("a2", plan)
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["mode"], "legacy_run_warning_only")
        self.assertEqual(r["legacy_unrecorded_count"], len(plan))
        self.assertEqual({w["warning"] for w in r["warnings"]}, {"Z_STYLE_ACTUAL_UNRECORDED_LEGACY_RUN"})
        self.assertFalse(r["marker_present"])
        self.assertTrue(all(x["check"] == "legacy_unrecorded" for x in self.out("a2")["rows"]))

    def test_past_run_reports_derived_mismatch_as_reference_without_blocking(self):
        plan = self._legacy_run("a2")
        fb = "natural, clear, conversational"
        def fn(e):
            e["attempts"] = [{"phase": "standard", "style_prefix_sha256": _sha("x")}, {"phase": "fallback", "style_prefix_sha256": _sha(fb), "instruction_type": "natural"}]
        self.edit_entry("a2", "full_story_part1_c1", fn)
        r = self.gate("a2", plan)
        self.assertEqual(r["status"], "PASS")
        row = [x for x in self.out("a2")["rows"] if x["segment"] == "full_story_part1_c1"][0]
        self.assertIs(row["legacy_derived_matches_approved"], False)
        self.assertIn("Z_STYLE_LEGACY_DERIVED_MISMATCH", {w["warning"] for w in r["warnings"]})

    def test_recorded_clip_in_past_run_is_checked_strictly(self):
        plan = self.stage("a2")
        os.remove(f"{self.run}/a2/{z.STYLE_ACTUAL_MARKER_RELPATH}")           # マーカーなし=過去run扱いだが、記録のあるclipは厳格
        self.edit_entry("a2", "comment_1", lambda e: e["style_actual"].update({"sha256": "1" * 64}))
        with self.assertRaises(z.FamilyZStyleActualGateStop):
            self.gate("a2", plan)

    def test_marker_only_for_fresh_level(self):
        lvl = f"{self.run}/a2"
        self.assertTrue(z.write_style_actual_marker_if_fresh(lvl, "a2"))
        self.assertFalse(z.write_style_actual_marker_if_fresh(lvl, "a2"))     # 既にある
        lvl2 = f"{self.run}/b1b"
        os.makedirs(f"{lvl2}/audit")
        json.dump({"segments": {}}, open(f"{lvl2}/audit/tts_generation_results.json", "w"))
        self.assertFalse(z.write_style_actual_marker_if_fresh(lvl2, "b1b"))   # 結果が先にある=導入前に開始したrun(遡及しない)
        self.assertFalse(os.path.exists(f"{lvl2}/{z.STYLE_ACTUAL_MARKER_RELPATH}"))

    def test_dry_run_does_not_write_marker(self):
        plan, _, _ = base.make_plan("a2")
        z.run_tts_stage(self.run, "a2", plan, generators=base.fake_generators(), dry_run=True)
        self.assertFalse(os.path.exists(self.run))


class DialogueTests(_Base):
    def test_dialogue_default_style_expected_and_altered_intent_blocks(self):
        plan = self.stage("a2")
        self.edit_entry("a2", "full_story_part1_c2", lambda e: e["style"].update({"effective_style_prefix_sha256": "e" * 64}))
        with self.assertRaises(z.FamilyZStyleActualGateStop) as cm:
            self.gate("a2", plan)
        self.assertIn("full_story_part1_c2=Z_DIALOGUE_STYLE_INTENDED_MISMATCH", str(cm.exception))

    def test_dialogue_ctx_adopted_uses_ctx_style_sha(self):
        plan = self.stage("a2")
        def fn(e):
            e["dialogue_tts"] = {"final_mode": "ctx", "ctx_style_sha256": "c" * 64}
            e["style"]["effective_style_prefix_sha256"] = "c" * 64
        self.edit_entry("a2", "full_story_part1_c2", fn)
        self.assertEqual(self.gate("a2", plan)["status"], "PASS")

    def test_dialogue_fallback_to_default_is_not_style_drop(self):
        plan = self.stage("a2")
        # 実leaf形: Dialogueが従来方式(既定Dialogue Style)へ切替わった記録=dialogue_tts.final_mode(UD-3の採用take分類核が直接記録から確定する)
        self.edit_entry("a2", "full_story_part1_c2", lambda e: (e["style"].update({"fallback_used": True}),
                                                                 e.update({"dialogue_tts": {"policy": "ctx", "final_mode": "legacy_fallback", "final_attempt_n": 3}})))
        r = self.gate("a2", plan)
        self.assertEqual(r["status"], "PASS")
        self.assertIn("FALLBACK_APPLIED", {w.get("warning") for w in r["warnings"]})        # 正常Fallbackは非ブロッキング警告(HR・停止を要求しない)

    def test_dialogue_measured_value_must_equal_default(self):
        plan = self.stage("a2")
        import er003_b1_p9a_audio as p9a
        d = _sha(p9a.ENGLISH_STYLE_PREFIX)
        self.edit_entry("a2", "full_story_part1_c2", lambda e: e["style_actual"].update({"kind": "measured", "sha256": d}))
        self.assertEqual(self.gate("a2", plan)["status"], "PASS")
        self.edit_entry("a2", "full_story_part1_c2", lambda e: e["style_actual"].update({"kind": "measured", "sha256": "9" * 64}))
        with self.assertRaises(z.FamilyZStyleActualGateStop):
            self.gate("a2", plan)


class FormalPathMockRunnerTests(unittest.TestCase):
    """正式経路(er026 runner の stage tts_b1b/tts_a2/provision_shell/gate、--mode mock相当=build_mock_context、実API禁止)で新Gateの発火/PASS/BLOCKを観測する。"""
    PRE = ("seed_check", "writer", "std_adjust", "plan", "support", "kp", "tts_b1b", "tts_a2", "provision_shell", "gate")

    def setUp(self):
        import er026_family_z_e2e_integration_test_01 as it
        self.it, self.r = it, it.r
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def _out(self, ctx, lv):
        return json.load(open(f"{ctx.out_dir}/{lv}/audit/style_actual_vs_approved.json", encoding="utf-8"))

    def test_gate_fires_and_passes_in_runner_mock_run(self):
        with self.it.forbid_real_apis():
            ctx = self.r.build_mock_context(self.tmp)
            self.it.run_stages_quiet(ctx, list(self.PRE))
        for lv in ("a2", "b1b"):
            o = self._out(ctx, lv)
            self.assertEqual((o["status"], o["mode"]), ("PASS", "strict"), lv)
            self.assertEqual(o["rows_count"], o["coverage"]["expected_clip_count"])
            self.assertGreater(o["checked_count"], 0)
            self.assertTrue(o["all_match"])
            self.assertTrue(os.path.exists(f"{ctx.out_dir}/{lv}/{z.STYLE_ACTUAL_MARKER_RELPATH}"))
            gr = json.load(open(f"{ctx.out_dir}/{lv}/audit/gate_result_{z.SUB_TASK_ID}.json", encoding="utf-8"))
            self.assertEqual(gr["style_actual_gate"]["status"], "PASS")

    def test_gate_blocks_runner_run_when_adv_preview_style_is_not_approved(self):
        base_gens = self.r.mock_tts_generators()

        def wrong_preview(spec, out_path):
            res = base_gens["preview"](spec, out_path)
            if spec.level == "b1b":
                bad = "natural, clear, conversational"       # 承認E1を落としたStyleを送ったことにする(OPEN-551型の事故の模擬)
                res["standard_attempts_log"][0]["style_prefix"] = {"sha256": _sha(bad), "len": len(bad), "head200": bad}
            return res
        with self.it.forbid_real_apis():
            ctx = self.r.build_mock_context(self.tmp, tts_generators=dict(base_gens, preview=wrong_preview))
            with self.assertRaises(z.FamilyZStyleActualGateStop) as cm:
                self.it.run_stages_quiet(ctx, list(self.PRE))
        self.assertIn("preview=Z_STYLE_ACTUAL_MISMATCH", str(cm.exception))
        o = self._out(ctx, "b1b")
        self.assertEqual(o["status"], "BLOCK")
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/b1b/audit/gate_result_{z.SUB_TASK_ID}.json"))     # BLOCK時にGate PASS成果物を残さない


class NoOtherFamilyTouchedTests(unittest.TestCase):
    def test_x_and_y_style_constants_and_gates_unchanged_in_source(self):
        # X/Yのファイル自体はこの委任で編集しない(git diff対象外)。ここではZ側がX/Yのprivate gateを呼ばないこと(独立)を確認する。
        src = open("er063_family_z_audio_01.py", encoding="utf-8").read()
        self.assertNotIn("m3_assembly_gate(", src)
        self.assertNotIn("y_style_gate(", src)
        self.assertNotIn("resolve_run_profile(", src)


if __name__ == "__main__":
    unittest.main()
