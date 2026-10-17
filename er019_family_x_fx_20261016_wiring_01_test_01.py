# ============================================================
# er019_family_x_fx_20261016_wiring_01_test_01.py
# FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_02A(トラックA、2026-10-16)
# 既定Style profile fx_20261016 / KP英語K2の2段key / P8-KP role分離 / M3・M4 role別判定 / CLI未指定の自動適用 /
# A・B・C・Z非影響(golden・smoke)。全てAPI 0(mock)。
# 実行: .venv/Scripts/python.exe -m pytest er019_family_x_fx_20261016_wiring_01_test_01.py -q
# ============================================================
from __future__ import annotations

import ast
import contextlib
import hashlib
import inspect
import io
import json
import os
import re
import shutil
import tempfile
import unittest
import wave
from unittest import mock

import er006_audio_cost_pilot_02_shared_narration as shared
import er006_master_audio_store_01 as store
import er003_v1_repro01_main_generate as repro01
import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_kp_en_k2_store_01 as k2s
import er019_family_x_style_profile_01 as sp

FX = sp.PROFILE_FX_20261016          # 旧既定(2026-10-16〜10-17)。委任_03 Phase B以降はresume互換のみ(SUPPORT_JA=R2)。
FX_NEW = sp.PROFILE_FX_20261017      # 新規run既定(SUPPORT_JA=S3、他roleはFXと同一)
FL = "speech_metadata_flash_lite"


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def _eval_top_level(path: str, names: list[str]) -> dict:
    """Trial正本.pyを実行(import)せず、トップレベルのAssignだけをAST評価して値を取り出す(副作用なし)。"""
    tree = ast.parse(open(path, encoding="utf-8").read())
    ns: dict = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id in names:
            ns[node.targets[0].id] = eval(compile(ast.Expression(node.value), path, "eval"), {}, dict(ns))
    return ns


def _write_wav(path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(b"\x00\x00" * 2400)


# ============================================================
# 1. 定数・ソース突合(P8名称衝突の分離を含む)
# ============================================================
class ConstantsAndSourceTests(unittest.TestCase):
    NEW = (("PD06", sp.PD06_TEXT, sp.PD06_SHA256, sp.PD06_LENGTH, "3a680861e4d9", 177),
           ("P7", sp.P7_TEXT, sp.P7_SHA256, sp.P7_LENGTH, "0518000694e3", 136),
           ("K2", sp.K2_TEXT, sp.K2_SHA256, sp.K2_LENGTH, "9d905cfe6c04", 332),
           ("P8_KP", sp.P8_KP_JA_TEXT, sp.P8_KP_JA_SHA256, sp.P8_KP_JA_LENGTH, "b12c8721eab8", 93))

    def test_sha_and_length_match_approved_values(self):
        for label, text, sha, length, prefix, n in self.NEW:
            self.assertEqual(_sha(text), sha, label)
            self.assertTrue(sha.startswith(prefix), label)
            self.assertEqual(len(text), length, label)
            self.assertEqual(length, n, label)

    def test_no_wpm_specification(self):
        import er002_common as common
        for label, text, *_ in self.NEW:
            common.assert_no_wpm_specification(text)

    def test_verify_constants_detects_tampering(self):
        with mock.patch.object(sp, "K2_TEXT", sp.K2_TEXT + " "):
            with self.assertRaises(sp.StyleProfileStop):
                sp._verify_constants()
        with mock.patch.object(sp, "P7_TEXT", sp.P7_TEXT.replace("relaxed", "fast")):
            with self.assertRaises(sp.StyleProfileStop):
                sp._verify_constants()

    def test_constants_equal_trial_source_files(self):
        # PD06
        md = open("er057_output/pace_trial_02/prompts/prompts_pace_02.md", encoding="utf-8").read()
        m = re.search(r"## PD6 .*?```\n(.*?)\n```", md, re.S)
        self.assertEqual(sp.PD06_TEXT, m.group(1).strip())
        # P7 (KP英語解説音声)
        ns = _eval_top_level("er080_coffee_kp_pacing_trial_01.py", ["PROMPTS"])
        self.assertEqual(sp.P7_TEXT, ns["PROMPTS"]["p7"][1])
        # K2 = B_SPECS["K2"] (K2文 + B_GUARD)
        ns = _eval_top_level("er057_tone_trial_kp_ja_gen_01.py", ["B_GUARD", "B_SPECS"])
        self.assertEqual(sp.K2_TEXT, ns["B_SPECS"]["K2"][1])
        # P8-KP (Std KP日本語意味)
        ns = _eval_top_level("er057_std_kp_ja_style_trial_02.py", ["PROMPTS"])
        self.assertEqual(sp.P8_KP_JA_TEXT, ns["PROMPTS"]["P8"])

    def test_k2_equals_family_z_k2(self):
        # 2026-10-17 委任_15: 期待値を意図的に更新(旧: Zの`_K2`コピー定数と一致。Zはコピーを撤去しXのK2_TEXTを定数参照するため、同一objectであることを確認)。
        import er063_family_z_audio_01 as z
        self.assertIs(z._STYLE_TEXT["K2"], sp.K2_TEXT)

    def test_p8_name_collision_is_separated(self):
        # 旧Full Story候補P8(402字)は不変、KP用は別定数・別role
        self.assertEqual(len(sp.P8_TEXT), 402)
        self.assertEqual(sp.P8_SHA256, "3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595")
        self.assertNotEqual(sp.P8_TEXT, sp.P8_KP_JA_TEXT)
        self.assertNotEqual(sp.P8_SHA256, sp.P8_KP_JA_SHA256)
        self.assertEqual(sp.ROLE_KP_JA_MEANING, "KP_JA_MEANING")
        self.assertNotEqual(sp.ROLE_KP_JA_MEANING, "FULL_STORY")
        # 旧profile(coffee_p8/coffee_final_v5)のFULL_STORYは引き続き旧P8
        for pid in (sp.PROFILE_COFFEE_P8, sp.PROFILE_COFFEE_FINAL_V5):
            self.assertEqual(sp.get_profile(pid)["overrides"]["FULL_STORY"]["sha256"], sp.P8_SHA256)
            self.assertNotIn(sp.ROLE_KP_JA_MEANING, sp.get_profile(pid)["overrides"])
        # fx profileではFULL_STORYはPD06、KP日本語意味だけがP8-KP
        o = sp.get_profile(FX)["overrides"]
        self.assertEqual(o["FULL_STORY"]["sha256"], sp.PD06_SHA256)
        self.assertEqual(o[sp.ROLE_KP_JA_MEANING]["sha256"], sp.P8_KP_JA_SHA256)

    def test_old_constants_unchanged(self):
        self.assertEqual(sp.R2_SHA256, "625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f")
        self.assertEqual(sp.E1_SHA256, "8862317ff76693ff519ddfa956260a8cce2d540763333b54096b63161d84f641")
        self.assertEqual(sp.N01_SHA256, "d1956c91c925d197e27cf1204d7ed17248a96bef096b082fb1bd0846106a0477")
        self.assertEqual(sp.P3_SHA256, "a8aaec591ef6d9acb42532cc0c84b6edfb2f75991e713d413c565b7e27677acc")

    def test_variable_role_style_version_not_bumped(self):
        # R-12: bumpしない(旧profileのcache-version guardを変えない。新profileの区別は固定記録+Store keyで行う)
        self.assertEqual(runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION, "v3_j3_kp_meaning_and_explanation_guard")


# ============================================================
# 2. profile定義・解決・固定記録・旧profile
# ============================================================
class ProfileDefinitionTests(unittest.TestCase):
    def test_default_new_run_profile_is_fx(self):
        # 委任_03 Phase B(2026-10-17、S3正式採用): 新規run既定はfx_20261017。fx_20261016はresume互換のみ残置。
        self.assertEqual(sp.DEFAULT_NEW_RUN_PROFILE, FX_NEW)
        self.assertEqual(FX_NEW, "fx_20261017")
        self.assertEqual(FX, "fx_20261016")
        self.assertIn(FX, sp.STYLE_PROFILES)

    def test_six_roles_and_levels(self):
        self.assertEqual(set(sp.overridden_roles(FX)),
                         {"FULL_STORY", "SUPPORT_JA", "PREVIEW", "KP_EXPLANATION_EN", "KP_EN", "KP_JA_MEANING"})
        self.assertEqual(sp.ROLE_LEVELS["KP_EN"], ("a2", "b1b"))
        self.assertEqual(sp.ROLE_LEVELS["KP_JA_MEANING"], ("a2",))
        self.assertEqual(sp.ROLE_LEVELS["KP_EXPLANATION_EN"], ("b1b",))
        self.assertEqual(sp.ROLE_LEVELS["SUPPORT_JA"], ("a2",))
        self.assertEqual(sp.ROLE_LEVELS["PREVIEW"], ("b1b",))

    def test_resolve_role_style_per_role_and_level(self):
        base = lambda r: f"BASE:{r}"
        exp = {("FULL_STORY", "a2"): sp.PD06_TEXT, ("FULL_STORY", "b1b"): sp.PD06_TEXT,
               ("SUPPORT_JA", "a2"): sp.R2_TEXT, ("SUPPORT_JA", "b1b"): "BASE:SUPPORT_JA",
               ("PREVIEW", "b1b"): sp.E1_TEXT, ("PREVIEW", "a2"): "BASE:PREVIEW",
               ("KP_EXPLANATION_EN", "b1b"): sp.P7_TEXT, ("KP_EXPLANATION_EN", "a2"): "BASE:KP_EXPLANATION_EN",
               ("KP_EN", "a2"): sp.K2_TEXT, ("KP_EN", "b1b"): sp.K2_TEXT,
               ("KP_JA_MEANING", "a2"): sp.P8_KP_JA_TEXT, ("KP_JA_MEANING", "b1b"): "BASE:KP_JA_MEANING"}
        for (role, level), want in exp.items():
            self.assertEqual(sp.resolve_role_style(FX, role, level, base), want, (role, level))
        # IN_ONE_LINE / TOPIC_INTRO / COMMENT(非対象role)はbase素通し
        for role in ("IN_ONE_LINE", "TOPIC_INTRO", "COMMENT"):
            self.assertEqual(sp.resolve_role_style(FX, role, "b1b", base), f"BASE:{role}")

    def test_pd06_is_verbatim_for_std_no_slower_instruction(self):
        self.assertIs(sp.get_profile(FX)["overrides"]["FULL_STORY"]["std_append_slower_instruction"], False)
        rec = sp.build_record(FX)
        self.assertIs(rec["roles"]["FULL_STORY"]["std_append_slower_instruction"], False)

    def test_record_has_six_roles_with_levels_and_verifies(self):
        rec = sp.build_record(FX)
        self.assertEqual(set(rec["roles"]), set(sp.overridden_roles(FX)))
        self.assertEqual(rec["roles"]["KP_EN"]["sha256"], sp.K2_SHA256)
        self.assertEqual(rec["roles"]["KP_EN"]["levels"], ["a2", "b1b"])
        self.assertEqual(rec["roles"]["KP_JA_MEANING"]["length"], 93)
        self.assertEqual(sp.verify_record(rec), FX)
        rec["roles"]["KP_EN"]["sha256"] = "0" * 64
        with self.assertRaises(sp.StyleProfileStop):
            sp.verify_record(rec)

    def test_old_profiles_unchanged_and_still_listed(self):
        for pid in ("default", "coffee_p8", "coffee_final_v5", "n01", "coffee_n01_r2_p3", "coffee_n01_r2_p3_e1"):
            self.assertIn(pid, sp.STYLE_PROFILES)
        # 旧profileにはKP_EN/KP_JA_MEANING overrideは無い(旧KP経路のまま)
        for pid in ("default", "coffee_p8", "coffee_final_v5", "n01", "coffee_n01_r2_p3", "coffee_n01_r2_p3_e1"):
            self.assertNotIn("KP_EN", sp.get_profile(pid)["overrides"])
            self.assertNotIn("KP_JA_MEANING", sp.get_profile(pid)["overrides"])
        self.assertIn(FX, runner.build_arg_parser()._option_string_actions["--style-profile"].choices)
        self.assertIn("n01", runner.build_arg_parser()._option_string_actions["--style-profile"].choices)

    def test_migration_from_old_profiles_to_fx_is_rejected(self):
        for old in ("n01", "coffee_n01_r2_p3_e1", "coffee_n01_r2_p3", "coffee_final_v5", "coffee_p8"):
            with tempfile.TemporaryDirectory() as d:
                os.makedirs(f"{d}/audit")
                json.dump(sp.build_record(old), open(sp.record_path(d), "w", encoding="utf-8"))
                with self.assertRaises(sp.StyleProfileStop, msg=old):
                    sp.migrate_record(d, old, FX, "reason", "MID")

    def test_default_profile_is_not_applied_to_existing_run_without_record(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(f"{d}/a2/audit")
            open(f"{d}/a2/audit/tts_generation_results.json", "w").write("{}")
            with self.assertRaises(sp.StyleProfileStop):
                sp.resolve_run_profile(d, None, write=False, tts_backend=FL)
            self.assertEqual(sp.resolve_run_profile(d, "default", write=False, tts_backend=FL)[0], "default")

    def test_profile_resolution_warning_texts(self):
        w = sp.profile_resolution_warning("n01", "record")
        self.assertIn("[WARN][STYLE-PROFILE] 旧profileでresume中", w)
        self.assertIsNone(sp.profile_resolution_warning(FX_NEW, "record"))
        self.assertIsNone(sp.profile_resolution_warning(FX_NEW, "default_new_run_fx_20261017"))
        # 旧既定fx_20261016(R2)のrunをresumeする場合は旧profileとして警告(S3ではないことを目立たせる)
        self.assertIn("[WARN][STYLE-PROFILE] 旧profileでresume中", sp.profile_resolution_warning(FX, "record"))
        self.assertIn("legacy", sp.profile_resolution_warning("default", "default_no_record_legacy_backend"))


# ============================================================
# 3. M3 / M4 role別判定
# ============================================================
def _style_rec(role: str, text: str | None, applied: str | None = None):
    return {"profile_id": FX, "role": role, "expected_base_sha256": sp.get_profile(FX)["overrides"][role]["sha256"],
            "style_base_sha256": _sha(applied if applied is not None else text)}


def _kp_en_entry(path="primary", reused=False, fallback=False, versions=None):
    v = versions or (f"v2_margin030+k2.{sp.K2_SHA256[:12]}" if path == "primary" else "v2_margin030+lock.aaaaaaaaaaaa")
    e = {"status": "OK", "canonical_text": "opt out", "style_profile": _style_rec("KP_EN", sp.K2_TEXT),
         "master_audio_key": {"style_instruction_id": sp.KP_EN_STORE_STYLE_ID, "style_instruction_version": v,
                              "instruction_path": path},
         "reused": reused}
    if fallback:
        e["fallback_used"] = True
    elif not reused:
        e["fallback_used"] = False
    if not reused and not fallback:  # 新規生成: attempts_logに実送信style記録(hintなし=K2そのまま)
        e["attempts_log"] = [{"style_prefix": {"sha256": sp.K2_SHA256, "head200": sp.K2_TEXT[:200], "len": 332}}]
        e["en_pronunciation_resolver_info"] = {"hints_applied": False}
    return e


def _ja_meaning_entry(fallback_used=False):
    e = {"status": "OK", "canonical_text": "みおくる", "style_profile": _style_rec("KP_JA_MEANING", sp.P8_KP_JA_TEXT)}
    if fallback_used is not None:
        e["fallback_used"] = fallback_used
    return e


def _expl_entry():
    return {"status": "OK", "canonical_text": "to choose not to", "style_profile": _style_rec("KP_EXPLANATION_EN", sp.P7_TEXT),
            "attempts_log": [{"style_prefix": {"sha256": sp.P7_SHA256, "head200": sp.P7_TEXT[:200], "len": 136}}],
            "en_pronunciation_resolver_info": {"hints_applied": False}}


def _b1b_results(en=None, expl=None):
    return {"segments": {}, "key_phrases": {"1": {"english": en or _kp_en_entry(), "explanation": expl or _expl_entry()}}}


def _only_kp_targets(g, level):
    return sorted(x for x in g["checked"] if x.startswith("kp"))


class M3M4RoleTests(unittest.TestCase):
    def _gate(self, level, results, approvals=None):
        # fxは全role対象。KP以外のsegmentは「NO_SEGMENT_RECORD」になるので、KP関連blockedだけを見る。
        g = sp.m3_assembly_gate(FX, level, results, approvals)
        kp_blocked = [b for b in g["blocked"] if b["segment"].startswith("kp")]
        return g, kp_blocked

    def test_gate_targets_cover_all_kp_roles(self):
        t_b = {(n, r) for n, r, _ in sp._gate_targets(FX, "b1b", _b1b_results())}
        self.assertIn(("kp1_english", "KP_EN"), t_b)
        self.assertIn(("kp1_explanation", "KP_EXPLANATION_EN"), t_b)
        self.assertNotIn("KP_JA_MEANING", {r for _, r, _ in sp._gate_targets(FX, "b1b", _b1b_results())})
        res_a = {"segments": {}, "key_phrases": {"1": {"english": _kp_en_entry(), "japanese_meaning": _ja_meaning_entry()}}}
        t_a = {(n, r) for n, r, _ in sp._gate_targets(FX, "a2", res_a)}
        self.assertIn(("kp1_english", "KP_EN"), t_a)
        self.assertIn(("kp1_japanese_meaning", "KP_JA_MEANING"), t_a)
        self.assertNotIn("KP_EXPLANATION_EN", {r for _, r, _ in sp._gate_targets(FX, "a2", res_a)})

    def test_no_key_phrases_record_blocks_each_kp_role(self):
        for level, roles in (("b1b", {"KP_EN", "KP_EXPLANATION_EN"}), ("a2", {"KP_EN", "KP_JA_MEANING"})):
            tg = [(n, r, e) for n, r, e in sp._gate_targets(FX, level, {"segments": {}}) if "kp" in n]
            self.assertEqual({r for _, r, _ in tg}, roles)
            self.assertTrue(all(e is None for _, _, e in tg))

    def test_kp_en_fresh_primary_passes_with_final_style_check(self):
        g, kb = self._gate("b1b", _b1b_results())
        self.assertEqual(kb, [])
        self.assertEqual(g["warnings"], [])

    def test_kp_en_fresh_primary_wrong_final_style_blocks(self):
        e = _kp_en_entry()
        e["attempts_log"] = [{"style_prefix": {"sha256": "0" * 64, "head200": "x", "len": 3}}]
        _, kb = self._gate("b1b", _b1b_results(en=e))
        self.assertIn("FINAL_STYLE_SHA_MISMATCH_NO_HINT", kb[0]["violations"])

    def test_kp_en_store_reuse_passes_without_attempt_style(self):
        # Store hit entry(reused=True)は生成時のattemptを持たない: keyで判定しPASS、warningなし
        e = _kp_en_entry(reused=True)
        self.assertNotIn("attempts_log", e)
        g, kb = self._gate("b1b", _b1b_results(en=e))
        self.assertEqual(kb, [])
        self.assertEqual(g["warnings"], [])

    def test_kp_en_fallback_is_identified_by_key_and_warns_non_blocking(self):
        for e in (_kp_en_entry(path="english_lock_fallback", fallback=True),  # 新規生成のfallback
                  _kp_en_entry(path="english_lock_fallback", reused=True)):  # Store hitのfallback entry
            g, kb = self._gate("b1b", _b1b_results(en=e))
            self.assertEqual(kb, [], e)  # BLOCKしない(承認済み4回構成の一部)
            self.assertEqual([w["warning"] for w in g["warnings"]], ["KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2"])
            self.assertEqual(g["warnings"][0]["segment"], "kp1_english")

    def test_kp_en_old_minimal_key_or_missing_key_blocks(self):
        old = _kp_en_entry(reused=True)
        old["master_audio_key"] = {"style_instruction_id": "key_phrase_english_component",
                                   "style_instruction_version": "v2_margin030", "instruction_path": "primary"}
        _, kb = self._gate("b1b", _b1b_results(en=old))
        self.assertIn("KP_EN_STORE_KEY_ID_MISMATCH", kb[0]["violations"])
        self.assertIn("KP_EN_STORE_KEY_VERSION_MISMATCH", kb[0]["violations"])
        nokey = _kp_en_entry(reused=True)
        del nokey["master_audio_key"]
        _, kb = self._gate("b1b", _b1b_results(en=nokey))
        self.assertIn("KP_EN_STORE_KEY_MISSING", kb[0]["violations"])
        bad_path = _kp_en_entry(reused=True)
        bad_path["master_audio_key"]["instruction_path"] = "other"
        _, kb = self._gate("b1b", _b1b_results(en=bad_path))
        self.assertIn("KP_EN_STORE_KEY_PATH_INVALID", kb[0]["violations"])

    def test_kp_en_k2_text_change_invalidates_old_key_version(self):
        # K2文が変われば(sha12が変わり)旧versionのentryはversion不一致=BLOCK
        e = _kp_en_entry(reused=True, versions="v2_margin030+k2.000000000000")
        _, kb = self._gate("b1b", _b1b_results(en=e))
        self.assertIn("KP_EN_STORE_KEY_VERSION_MISMATCH", kb[0]["violations"])

    def test_kp_en_fresh_fallback_used_but_primary_key_blocks(self):
        e = _kp_en_entry()
        e["fallback_used"] = True
        _, kb = self._gate("b1b", _b1b_results(en=e))
        self.assertIn("KP_EN_FALLBACK_USED_BUT_KEY_NOT_FALLBACK_PATH", kb[0]["violations"])

    def test_kp_en_base_sha_mismatch_blocks(self):
        e = _kp_en_entry()
        e["style_profile"]["style_base_sha256"] = "0" * 64
        _, kb = self._gate("b1b", _b1b_results(en=e))
        self.assertIn("STYLE_BASE_SHA_MISMATCH_OR_MISSING", kb[0]["violations"])

    def test_kp_en_status_not_ok_blocks(self):
        e = _kp_en_entry()
        e["status"] = "STOPPED"
        _, kb = self._gate("b1b", _b1b_results(en=e))
        self.assertIn("KP_EN_STATUS_NOT_OK", kb[0]["violations"])

    def test_kp_en_human_approval_bypasses_block_with_matching_sha(self):
        e = _kp_en_entry()
        e["status"] = "STOPPED"
        approvals = {"kp1_english": {"canonical_text_sha256": _sha("opt out")}}
        g, kb = self._gate("b1b", _b1b_results(en=e), approvals)
        self.assertEqual(kb, [])
        self.assertEqual([h["segment"] for h in g["human_approved"] if h["segment"].startswith("kp")], ["kp1_english"])

    def test_kp_ja_meaning_pass_and_fallback_block(self):
        res = {"segments": {}, "key_phrases": {"1": {"english": _kp_en_entry(), "japanese_meaning": _ja_meaning_entry()}}}
        _, kb = self._gate("a2", res)
        self.assertEqual(kb, [])
        for fb in (True, None):  # fallback_used=True / 欠落(unknown)
            res["key_phrases"]["1"]["japanese_meaning"] = _ja_meaning_entry(fallback_used=fb)
            if fb is None:
                res["key_phrases"]["1"]["japanese_meaning"].pop("fallback_used", None)
            _, kb = self._gate("a2", res)
            self.assertEqual([b["segment"] for b in kb], ["kp1_japanese_meaning"], fb)
            self.assertIn("KP_JA_MEANING_FALLBACK_USED_OR_UNKNOWN", kb[0]["violations"])

    def test_kp_ja_meaning_base_sha_is_p8_kp_not_old_p8(self):
        e = _ja_meaning_entry()
        e["style_profile"]["style_base_sha256"] = sp.P8_SHA256  # 旧Full Story候補P8のshaは不可(名称衝突の混同防止)
        res = {"segments": {}, "key_phrases": {"1": {"english": _kp_en_entry(), "japanese_meaning": e}}}
        _, kb = self._gate("a2", res)
        self.assertIn("STYLE_BASE_SHA_MISMATCH_OR_MISSING", kb[0]["violations"])

    def test_kp_explanation_p7_same_rule_as_p3(self):
        _, kb = self._gate("b1b", _b1b_results())
        self.assertEqual(kb, [])
        e = _expl_entry()
        e["attempts_log"] = [{"style_prefix": {"sha256": "0" * 64, "head200": "x", "len": 1}}]
        _, kb = self._gate("b1b", _b1b_results(expl=e))
        self.assertIn("FINAL_STYLE_SHA_MISMATCH_NO_HINT", kb[0]["violations"])
        e = _expl_entry()
        e["status"] = "STOPPED"
        _, kb = self._gate("b1b", _b1b_results(expl=e))
        self.assertIn("KP_EXPLANATION_STATUS_NOT_OK", kb[0]["violations"])

    def test_kp_explanation_with_hint_uses_startswith(self):
        e = _expl_entry()
        aug = sp.P7_TEXT + " (pronunciation hint)"
        e["attempts_log"] = [{"style_prefix": {"sha256": _sha(aug), "head200": aug[:200], "len": len(aug)}}]
        e["en_pronunciation_resolver_info"] = {"hints_applied": True, "cache_hits": [{"surface": "opt"}]}
        _, kb = self._gate("b1b", _b1b_results(expl=e))
        self.assertEqual(kb, [])

    def test_m3_default_profile_still_noop_and_has_no_warnings_requirement(self):
        g = sp.m3_assembly_gate("default", "b1b", {})
        self.assertEqual(g["status"], "PASS")

    def test_violation_rename_has_no_old_name_left(self):
        src = open("er019_family_x_style_profile_01.py", encoding="utf-8").read()
        self.assertNotIn("ADV_STYLE_PREFIX_NOT_P8_PREFIXED", src)
        self.assertIn("ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED", src)
        rsrc = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        self.assertNotIn("P8対象segmentがP8で生成されていません", rsrc)
        self.assertIn("profile対象segmentが承認済みprofileのStyleで生成されていません", rsrc)


# ============================================================
# 4. Master Audio Store: K2 2段key
# ============================================================
class _StoreSandbox:
    """Store/manifest/telemetryを一時dirへ向ける(本番Storeを汚さない)。"""

    def __enter__(self):
        self.tmp = tempfile.mkdtemp(prefix="fx_store_")
        self._orig = (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH)
        store.STORE_DIR = self.tmp
        store.AUDIO_DIR = f"{self.tmp}/audio"
        store.MANIFEST_PATH = f"{self.tmp}/manifest.json"
        store.TELEMETRY_PATH = f"{self.tmp}/reuse_telemetry.jsonl"
        return self

    def __exit__(self, *a):
        store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def manifest(self):
        p = f"{self.tmp}/manifest.json"
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


class FakeStrict:
    """repro01.generate_narration_snippet_verified_strictの置換。style別に成否を制御し、呼出引数を記録する。"""

    def __init__(self, ok_styles):
        self.ok_styles = ok_styles  # 成功させるstyle_prefix_overrideの集合
        self.calls = []

    def __call__(self, text, language, out_path, expected_substring, **kw):
        self.calls.append({"text": text, "out_path": out_path, **kw})
        style = kw.get("style_prefix_override")
        n = kw.get("max_attempts")
        ok = style in self.ok_styles
        attempts = [{"style_prefix": {"sha256": _sha(style), "head200": style[:200], "len": len(style)}, "asr_text": text}
                    for _ in range(n)]
        if ok:
            _write_wav(out_path)
        return {"status": "OK" if ok else "STOPPED", "path": out_path, "attempts_log": attempts,
                "sha256": "abc", "asr_verified": ok, "asr_text": text, "disfluency_checked": True,
                "en_pronunciation_resolver_info": {"hints_applied": False}}


LOCK = repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION


class StoreTwoStageKeyTests(unittest.TestCase):
    def _run(self, fake, text="opt out", out=None, sandbox=None):
        out = out or f"{sandbox.tmp}/o/out.wav"  # review_lockの標準layout外=Lock bypass(下のaccounting testで別途検証)
        with mock.patch.object(repro01, "generate_narration_snippet_verified_strict", fake):
            return k2s.ensure_key_phrase_english_component_styled(
                text, out, style_text=sp.K2_TEXT, style_id=sp.KP_EN_STORE_STYLE_ID, tts_backend=FL)

    def test_key_values(self):
        ka, kb = k2s.key_phrase_styled_keys("opt out", sp.K2_TEXT, sp.KP_EN_STORE_STYLE_ID, "k2", FL)
        self.assertEqual(ka.style_instruction_id, "key_phrase_english_component_k2")
        self.assertEqual(ka.style_instruction_version, f"v2_margin030+k2.{sp.K2_SHA256[:12]}")
        self.assertEqual(ka.style_instruction_version, "v2_margin030+k2.9d905cfe6c04")
        self.assertEqual(ka.instruction_path, "primary")
        self.assertEqual(kb.style_instruction_id, "key_phrase_english_component_k2")
        self.assertEqual(kb.style_instruction_version, f"v2_margin030+lock.{_sha(LOCK)[:12]}")
        self.assertEqual(kb.instruction_path, "english_lock_fallback")
        self.assertNotEqual(ka.master_audio_id(), kb.master_audio_id())
        # 旧key(MINIMAL style)とは別id
        old = store.MasterAudioKey(language="en", speaker_voice="Aoede", tts_model_id=shared.TTS_MODEL_FLASH_LITE,
                                   canonical_text="opt out", level=None,
                                   style_instruction_id="key_phrase_english_component",
                                   style_instruction_version=shared.KEY_PHRASE_TRIM_POLICY_VERSION)
        self.assertNotEqual(ka.master_audio_id(), old.master_audio_id())
        self.assertNotEqual(kb.master_audio_id(), old.master_audio_id())

    def test_k2_text_change_changes_key(self):
        ka, _ = k2s.key_phrase_styled_keys("opt out", sp.K2_TEXT, sp.KP_EN_STORE_STYLE_ID, "k2", FL)
        ka2, _ = k2s.key_phrase_styled_keys("opt out", sp.K2_TEXT + "!", sp.KP_EN_STORE_STYLE_ID, "k2", FL)
        self.assertNotEqual(ka.master_audio_id(), ka2.master_audio_id())

    def test_primary_ok_saved_under_key_a_and_reused_with_zero_tts(self):
        with _StoreSandbox() as sb:
            fake = FakeStrict({sp.K2_TEXT})
            r1 = self._run(fake, sandbox=sb)
            self.assertEqual(r1["status"], "OK")
            self.assertIs(r1["fallback_used"], False)
            self.assertFalse(r1["reused"])
            self.assertEqual(r1["master_audio_key"]["instruction_path"], "primary")
            self.assertEqual(len(fake.calls), 1)
            self.assertEqual(fake.calls[0]["style_prefix_override"], sp.K2_TEXT)
            self.assertEqual(fake.calls[0]["max_attempts"], 2)
            self.assertEqual((fake.calls[0]["slot_offset"], fake.calls[0]["total_slots"]), (0, 4))
            m = sb.manifest()
            self.assertEqual([v["key"]["instruction_path"] for v in m.values()], ["primary"])
            # 2回目(別out_path、同text・同K2): TTS 0回でreuse、keyはAのまま
            fake2 = FakeStrict(set())
            r2 = self._run(fake2, out=f"{sb.tmp}/o2/out.wav", sandbox=sb)
            self.assertEqual(fake2.calls, [])
            self.assertTrue(r2["reused"])
            self.assertEqual(r2["master_audio_key"]["instruction_path"], "primary")
            self.assertEqual(r2["master_audio_key"]["style_instruction_version"], "v2_margin030+k2.9d905cfe6c04")

    def test_fallback_audio_saved_only_under_key_b_never_under_key_a(self):
        with _StoreSandbox() as sb:
            fake = FakeStrict({LOCK})  # K2は2回NG、ENGLISH_LOCKはOK
            r = self._run(fake, sandbox=sb)
            self.assertEqual(r["status"], "OK")
            self.assertIs(r["fallback_used"], True)
            self.assertEqual(r["master_audio_key"]["instruction_path"], "english_lock_fallback")
            self.assertEqual([c["style_prefix_override"] for c in fake.calls], [sp.K2_TEXT, LOCK])
            self.assertEqual([(c["max_attempts"], c["slot_offset"], c["total_slots"]) for c in fake.calls],
                             [(2, 0, 4), (2, 2, 4)])
            m = sb.manifest()
            self.assertEqual([v["key"]["instruction_path"] for v in m.values()], ["english_lock_fallback"])
            # 別記事で再度要求: key Aはmiss(K2を再試行する)。fallback entryはK2として再利用されない。
            fake2 = FakeStrict({sp.K2_TEXT})
            r2 = self._run(fake2, out=f"{sb.tmp}/o2/out.wav", sandbox=sb)
            self.assertEqual(r2["master_audio_key"]["instruction_path"], "primary")
            self.assertIs(r2["fallback_used"], False)
            self.assertEqual([c["style_prefix_override"] for c in fake2.calls], [sp.K2_TEXT])
            self.assertEqual(sorted(v["key"]["instruction_path"] for v in sb.manifest().values()),
                             ["english_lock_fallback", "primary"])  # B entryは壊れず残る(manifest clobberなし)

    def test_fallback_entry_reuse_keeps_key_b_identification_and_skips_lock_tts(self):
        with _StoreSandbox() as sb:
            self._run(FakeStrict({LOCK}), sandbox=sb)  # B entry作成
            fake = FakeStrict(set())  # K2はNGのまま。ENGLISH_LOCKはkey B hitでTTS不要
            r = self._run(fake, out=f"{sb.tmp}/o3/out.wav", sandbox=sb)
            self.assertEqual(r["status"], "OK")
            self.assertTrue(r["reused"])
            self.assertEqual([c["style_prefix_override"] for c in fake.calls], [sp.K2_TEXT])  # K2再試行のみ
            self.assertEqual(r["master_audio_key"]["instruction_path"], "english_lock_fallback")
            self.assertIs(r["fallback_used"], True)

    def test_both_fail_returns_non_ok_and_stores_nothing(self):
        with _StoreSandbox() as sb:
            fake = FakeStrict(set())
            r = self._run(fake, sandbox=sb)
            self.assertNotEqual(r["status"], "OK")
            self.assertIs(r["fallback_used"], True)
            self.assertEqual(len(fake.calls), 2)
            self.assertEqual(sb.manifest(), {})

    def test_review_lock_accounting_single_guard_total_four(self):
        with _StoreSandbox() as sb:
            fake = FakeStrict({LOCK})
            with mock.patch.object(repro01.review_lock, "check_before_generation", return_value={"proceed": True}) as chk, \
                 mock.patch.object(repro01.review_lock, "record_outcome") as rec:
                r = self._run(fake, sandbox=sb)
            self.assertEqual(chk.call_count, 1)
            self.assertEqual(rec.call_count, 1)  # 論理的な1生成=record 1回(二重会計なし)
            result = rec.call_args.args[3]
            self.assertEqual(len(result["fallback_attempts_log"]), 2)  # K2段の2回
            self.assertEqual(len(result["attempts_log"]), 2)  # ENGLISH_LOCK段の2回 => 通算4
            self.assertEqual(r["status"], "OK")

    def test_review_lock_not_touched_on_store_reuse(self):
        with _StoreSandbox() as sb:
            self._run(FakeStrict({sp.K2_TEXT}), sandbox=sb)
            with mock.patch.object(repro01.review_lock, "check_before_generation") as chk, \
                 mock.patch.object(repro01.review_lock, "record_outcome") as rec:
                r = self._run(FakeStrict(set()), out=f"{sb.tmp}/o2/out.wav", sandbox=sb)
            self.assertTrue(r["reused"])
            self.assertEqual((chk.call_count, rec.call_count), (0, 0))  # 従来のreuse時と同じ(Lockを触らない)

    def test_blocked_by_review_lock_is_not_stored_or_treated_as_fallback(self):
        with _StoreSandbox() as sb:
            fake = FakeStrict({sp.K2_TEXT})
            blocked = {"proceed": False, "status": "HUMAN_REVIEW_REQUIRED", "reason": "r", "locked_entry": {}}
            with mock.patch.object(repro01.review_lock, "check_before_generation", return_value=blocked):
                r = self._run(fake, sandbox=sb)
            self.assertNotEqual(r["status"], "OK")
            self.assertEqual(fake.calls, [])
            self.assertEqual(sb.manifest(), {})


# ============================================================
# 5. A/B/C golden(共有関数の既定=現行バイト同一)・store無変更
# ============================================================
class AbcGoldenTests(unittest.TestCase):
    def test_legacy_ensure_key_phrase_english_component_key_unchanged(self):
        captured = {}

        def fake_get_or_generate(key, out_path, gen):
            captured["key"] = key
            captured["gen"] = gen
            return {"status": "OK"}

        with mock.patch.object(store, "get_or_generate", fake_get_or_generate), \
             mock.patch.object(repro01, "generate_key_phrase_component_verified", return_value={"status": "OK"}) as gk:
            shared.ensure_key_phrase_english_component("opt out", "x/out.wav", tts_backend=FL)
            captured["gen"]("p.wav")
        k = captured["key"].as_dict()
        self.assertEqual(k["style_instruction_id"], "key_phrase_english_component")
        self.assertEqual(k["style_instruction_version"], "v2_margin030")
        self.assertEqual(k["instruction_path"], "primary")
        self.assertEqual((k["language"], k["speaker_voice"], k["level"]), ("en", "Aoede", None))
        gk.assert_called_once_with("opt out", "p.wav", tts_backend=FL)

    def test_legacy_keys_match_real_manifest_entries(self):
        # 実manifest(読み取りのみ)の旧KP entryについて、同じfieldから再計算したid==manifestのkey: A/B/Cのkeyが不変である証拠
        m = json.load(open("er006_output/master_audio_store_01/manifest.json", encoding="utf-8"))
        legacy = [(mid, e["key"]) for mid, e in m.items()
                  if e["key"].get("style_instruction_id") == "key_phrase_english_component"
                  and e["key"].get("style_instruction_version") == "v2_margin030"]
        self.assertGreater(len(legacy), 5)
        for mid, k in legacy[:40]:
            # canonical_text自体はhashのみ保存されているため、hash fieldから直接idを再計算する
            import json as _j
            payload = _j.dumps({f: k[f] for f in store.EQUALITY_FIELDS}, sort_keys=True)
            self.assertEqual(hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24], mid)

    def test_legacy_generate_key_phrase_component_verified_prompts_and_accounting_unchanged(self):
        fake = FakeStrict({repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX})
        with tempfile.TemporaryDirectory() as d, mock.patch.object(repro01, "generate_narration_snippet_verified_strict", fake):
            r = repro01.generate_key_phrase_component_verified("opt out", f"{d}/x/out.wav", tts_backend=FL)
        self.assertEqual(r["status"], "OK")
        self.assertIs(r["fallback_used"], False)
        c = fake.calls[0]
        self.assertEqual(c["style_prefix_override"], repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX)
        self.assertEqual((c["max_attempts"], c["slot_offset"], c["total_slots"]), (2, 0, 4))
        self.assertEqual(inspect.signature(repro01.generate_key_phrase_component_verified).parameters.keys(),
                         {"text": 0, "out_path": 0, "disfluency_qa": 0, "tts_backend": 0}.keys())

    def test_k2_store_module_is_family_x_only(self):
        # 新module(KP英語K2の2段key)をimportするのはFamily X runnerとtestだけ。Family A/B/C/Z・共有moduleは参照しない。
        users = []
        for fn in sorted(os.listdir(".")):
            if fn.endswith(".py") and fn != "er019_family_x_kp_en_k2_store_01.py":
                if "er019_family_x_kp_en_k2_store_01" in open(fn, encoding="utf-8", errors="replace").read():
                    users.append(fn)
        self.assertEqual(users, ["er019_family_x_audio_production_runner_01.py",
                                 "er019_family_x_fx_20261016_wiring_01_test_01.py"])

    def test_master_audio_store_module_unchanged_contract(self):
        self.assertEqual(store.EQUALITY_FIELDS, (
            "language", "level", "speaker_voice", "tts_model_id", "style_instruction_id", "style_instruction_version",
            "instruction_path", "canonical_text_hash", "audio_processing_version", "sample_rate", "channels"))
        src = open("er006_master_audio_store_01.py", encoding="utf-8").read()
        self.assertNotIn("fallback_used", src)  # additive追加は不要(keyで識別)=qa_evidenceの形は不変
        m = re.search(r'"qa_evidence": \{(.*?)\},\n', src, re.S)
        self.assertEqual(sorted(re.findall(r'"(\w+)":', m.group(1))),
                         ["asr_text", "asr_verified", "disfluency_checked", "disfluency_evidence", "sha256"])

    def test_fallback_used_consumers_do_not_read_kp_english_entries(self):
        # production(.py、test/evidence/trial以外)で`fallback_used`を「読む」箇所を列挙し、KP英語Store entryを読むconsumerが
        # M3(style_profile)以外に無いことを固定する(additive追加の副作用なし)。
        readers = {}
        for fn in sorted(os.listdir(".")):
            if not fn.endswith(".py") or "test" in fn or fn.startswith(("tools", "er057_", "er038_", "er052_", "er011_", "er010_",
                                                                          "er008_", "er021_", "er025_", "er078_auw_runtime")):
                continue
            src = open(fn, encoding="utf-8").read()
            n = len(re.findall(r'(?:\.get\(|\[)\s*"fallback_used"\s*[\],)]', src)) - len(re.findall(r'\["fallback_used"\]\s*=', src))
            if n > 0:
                readers[fn] = n
        # 期待: reader(読み取り)はstyle_profile(M3)・Family Z(自前のresult加工)・shared_narration(今回の2段key)のみ
        self.assertTrue(set(readers) <= {"er019_family_x_style_profile_01.py", "er063_family_z_audio_01.py",
                                         "er019_family_x_kp_en_k2_store_01.py",
                                         "er063_family_z_audio_01_smoke_01.py",
                                         # BAPE委任_04のStyle適用表集計script(read-only: 完了runのtts_generation_results.jsonを読み
                                         # audit配下のe2e_segment_style_table_bape_04.jsonへ書くのみ。Store entry/Production出力へ書き戻さない)
                                         "er019_bape_style_table_04.py"}, readers)


# ============================================================
# 6. runner結線(mock TTS): style捕捉・KP entryへのprofile記録・旧profile不変・threading
# ============================================================
def _ok(*_a, **_kw):
    return {"status": "OK", "canonical_text": "x"}


KP_B = {"items": [{"rank": 1, "used_form": "opt out", "japanese_gloss": "見送る", "display_phrase": "opt out",
                   "source_sentence": "Users can opt out."}]}
EXPL = {"items": {1: {"english_explanation": "to choose not to take part", "qa": {"passed": True}, "status": "OK"}},
        "audit": {}}


class RunnerKpWiringTests(unittest.TestCase):
    def _run_b1(self, profile):
        with mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component", side_effect=_ok) as legacy, \
             mock.patch.object(runner.kp_en_k2_store, "ensure_key_phrase_english_component_styled", side_effect=_ok) as styled, \
             mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations", return_value=EXPL), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified", side_effect=_ok) as expl:
            res, _ = runner._generate_key_phrase_segments_b1(KP_B, "dummy_dir", tts_backend=FL, style_profile=profile)
        return res, legacy, styled, expl

    def _run_a2(self, profile, **kw):
        with mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component", side_effect=_ok) as legacy, \
             mock.patch.object(runner.kp_en_k2_store, "ensure_key_phrase_english_component_styled", side_effect=_ok) as styled, \
             mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety", side_effect=_ok) as ja, \
             mock.patch.object(runner.n3_tts, "resolve_key_phrase_ja_gloss_tts", return_value=("みおくる", False)):
            res = runner._generate_key_phrase_segments_a2(KP_B, "dummy_dir", tts_backend=FL, style_profile=profile, **kw)
        return res, legacy, styled, ja

    def test_b1_fx_uses_k2_styled_path_and_p7_and_records_profile(self):
        res, legacy, styled, expl = self._run_b1(FX)
        legacy.assert_not_called()
        self.assertEqual(styled.call_count, 1)
        kw = styled.call_args.kwargs
        self.assertEqual((kw["style_text"], kw["style_id"], kw["style_tag"], kw["tts_backend"]),
                         (sp.K2_TEXT, "key_phrase_english_component_k2", "k2", FL))
        self.assertEqual(styled.call_args.args[0], "opt out")
        self.assertEqual(expl.call_args.kwargs["style_prefix_override"], sp.P7_TEXT)
        en = res[1]["english"]
        self.assertEqual(en["style_profile"]["role"], "KP_EN")
        self.assertEqual(en["style_profile"]["style_base_sha256"], sp.K2_SHA256)
        self.assertEqual(en["style_profile"]["expected_base_sha256"], sp.K2_SHA256)
        self.assertEqual(res[1]["explanation"]["style_profile"]["role"], "KP_EXPLANATION_EN")
        self.assertEqual(res[1]["explanation"]["style_profile"]["style_base_sha256"], sp.P7_SHA256)
        # phrase_repeatはenglishのコピー(同じrecord)
        self.assertEqual(res[1]["phrase_repeat"]["style_profile"], en["style_profile"])

    def test_a2_fx_uses_k2_and_p8_kp_for_japanese_meaning(self):
        res, legacy, styled, ja = self._run_a2(FX)
        legacy.assert_not_called()
        self.assertEqual(styled.call_args.kwargs["style_text"], sp.K2_TEXT)
        self.assertEqual(ja.call_args.kwargs["style_prefix_override"], sp.P8_KP_JA_TEXT)
        self.assertNotEqual(ja.call_args.kwargs["style_prefix_override"], sp.P8_TEXT)
        self.assertEqual(res[1]["japanese_meaning"]["style_profile"]["role"], "KP_JA_MEANING")
        self.assertEqual(res[1]["japanese_meaning"]["style_profile"]["style_base_sha256"], sp.P8_KP_JA_SHA256)
        self.assertEqual(res[1]["english"]["style_profile"]["style_base_sha256"], sp.K2_SHA256)

    def test_a2_style_profile_argument_is_threaded_from_generate_family_x_a2_segments(self):
        src = inspect.getsource(runner.generate_family_x_a2_segments)
        self.assertIn("style_profile=style_profile", src.split("_generate_key_phrase_segments_a2(")[1].split(")")[0])
        self.assertIn("style_profile", inspect.signature(runner._generate_key_phrase_segments_a2).parameters)
        self.assertEqual(inspect.signature(runner._generate_key_phrase_segments_a2).parameters["style_profile"].default, "default")

    def test_default_and_old_profiles_keep_legacy_kp_path_byte_identical(self):
        for prof in ("default", "n01", "coffee_n01_r2_p3_e1", "coffee_final_v5", "coffee_p8"):
            res, legacy, styled, expl = self._run_b1(prof)
            styled.assert_not_called()
            self.assertEqual(legacy.call_args.args[0], "opt out")
            self.assertEqual(legacy.call_args.kwargs, {"tts_backend": FL})
            self.assertNotIn("style_profile", res[1]["english"], prof)  # KP英語にK2記録を付けない
            res, legacy, styled, ja = self._run_a2(prof)
            styled.assert_not_called()
            from er033_tts_flash_lite_family_x_styles_01 import FAMILY_X_ROLE_STYLE_JA
            self.assertEqual(ja.call_args.kwargs["style_prefix_override"], FAMILY_X_ROLE_STYLE_JA, prof)  # 従来のJ3のまま
            self.assertNotIn("style_profile", res[1]["japanese_meaning"], prof)

    def test_default_profile_kp_explanation_is_unchanged_style(self):
        from er033_tts_flash_lite_family_x_styles_01 import KEY_PHRASE_EXPLANATION_EN
        _, _, _, expl = self._run_b1("default")
        self.assertEqual(expl.call_args.kwargs["style_prefix_override"], KEY_PHRASE_EXPLANATION_EN)
        _, _, _, expl = self._run_b1("n01")
        self.assertEqual(expl.call_args.kwargs["style_prefix_override"], KEY_PHRASE_EXPLANATION_EN)
        _, _, _, expl = self._run_b1("coffee_n01_r2_p3_e1")
        self.assertEqual(expl.call_args.kwargs["style_prefix_override"], sp.P3_TEXT)  # 旧Coffee profileはP3のまま

    def test_only_segments_regeneration_uses_same_profile_style_and_same_key(self):
        # `--only-segments kp1_english`: profileは固定記録から再解決され、K2 key(style_text/id/tag)は初回生成と同一
        first, _, styled1, _ = self._run_b1(FX)
        runner._ONLY_SEGMENTS = {"kp1_english"}
        try:
            with mock.patch.object(runner.kp_en_k2_store, "ensure_key_phrase_english_component_styled",
                                   side_effect=_ok) as styled2, \
                 mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations", return_value=EXPL):
                res, _ = runner._generate_key_phrase_segments_b1(KP_B, "dummy_dir", tts_backend=FL, style_profile=FX)
        finally:
            runner._ONLY_SEGMENTS = None
        self.assertEqual(styled2.call_args.kwargs, styled1.call_args.kwargs)
        self.assertEqual(res[1]["explanation"]["status"], "SKIPPED_NOT_SELECTED")
        self.assertEqual(res[1]["english"]["style_profile"]["style_base_sha256"], sp.K2_SHA256)
        # key構成も同一: 同じstyle_text/style_idから組むkey A/Bのidは初回と再生成で一致する
        ka1 = k2s.key_phrase_styled_keys("opt out", styled1.call_args.kwargs["style_text"],
                                            styled1.call_args.kwargs["style_id"], "k2", FL)
        ka2 = k2s.key_phrase_styled_keys("opt out", styled2.call_args.kwargs["style_text"],
                                            styled2.call_args.kwargs["style_id"], "k2", FL)
        self.assertEqual([k.master_audio_id() for k in ka1], [k.master_audio_id() for k in ka2])

    def test_runner_has_no_other_resolve_path_for_kp_japanese_meaning(self):
        # _role_style_ja()がKP japanese_meaningへ直接渡されていない(P8-KP化後は_role_style_ja_kp_meaning経由のみ)
        src = inspect.getsource(runner._generate_key_phrase_segments_a2)
        body = src.split("ja_r = _generate_or_reuse_kp(")[1].split("ja_r[\"canonical_text\"]")[0]
        self.assertNotIn("style_prefix_override=_role_style_ja()", body)
        self.assertIn("style_prefix_override=_role_style_ja_kp_meaning()", body)


# ============================================================
# 7. M3 Gate呼出(runner): warningのstdout列挙・BLOCK時のsummary
# ============================================================
class RunnerGateTests(unittest.TestCase):
    def _setup(self, d, results):
        os.makedirs(f"{d}/audit")
        os.makedirs(f"{d}/b1b/audit")
        json.dump(sp.build_record(FX), open(sp.record_path(d), "w", encoding="utf-8"))
        json.dump(results, open(f"{d}/b1b/audit/tts_generation_results.json", "w", encoding="utf-8"))

    def test_fallback_warning_is_printed_and_blocking_summary_has_warnings(self):
        res = _b1b_results(en=_kp_en_entry(path="english_lock_fallback", fallback=True))
        with tempfile.TemporaryDirectory() as d:
            self._setup(d, res)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                summary = runner._style_profile_gate_blocked_summary(d, f"{d}/b1b", "b1b")
            out = buf.getvalue()
            self.assertIn("[WARN][STYLE-PROFILE][M3] b1b kp1_english: KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2", out)
            gate = json.load(open(f"{d}/b1b/audit/style_profile_gate.json", encoding="utf-8"))
            self.assertEqual(gate["warnings"][0]["warning"], "KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2")
            # 非KP segmentの記録が無いのでBLOCK(NO_SEGMENT_RECORD)になるが、blockedにkp1_englishは含まれない(warningのみ)
            self.assertEqual(summary["status"], "BLOCKED_STYLE_PROFILE_GATE")
            self.assertNotIn("kp1_english", [b["segment"] for b in summary["blocked"]])
            self.assertEqual(summary["warnings"][0]["segment"], "kp1_english")


# ============================================================
# 8. CLI未指定: main()単位の自動適用・旧記録のresume・--tts-backend既定
# ============================================================
class MainCliTests(unittest.TestCase):
    SLUG, RUN = "coffee_prices", "run_v5_ms_01"

    def _main(self, argv):
        buf = io.StringIO()
        with mock.patch("sys.argv", ["x"] + argv), contextlib.redirect_stdout(buf):
            runner.main()
        return buf.getvalue()

    def test_tts_backend_default_is_approved_backend(self):
        a = runner.build_arg_parser().parse_args(["--slug", "s", "--run", "r"])
        self.assertEqual(a.tts_backend, "speech_metadata_flash_lite")
        self.assertIsNone(a.style_profile)

    def test_legacy_backend_is_still_fail_closed(self):
        with self.assertRaises(RuntimeError):
            runner.assert_production_tts_backend("structured_separation", allow_legacy_backend=False)
        runner.assert_production_tts_backend("speech_metadata_flash_lite", allow_legacy_backend=False)

    def test_main_plan_without_style_profile_flag_applies_fx_and_records_six_roles(self):
        if not os.path.exists(f"er019_output/{self.SLUG}/{self.RUN}/a2/article.md"):
            self.fail("fixture missing")
        with tempfile.TemporaryDirectory() as d:
            out = f"{d}/o"
            self._main(["--slug", self.SLUG, "--run", self.RUN, "--out-dir", out, "--stage", "plan",
                        "--tts-backend", FL, "--level", "a2"])
            ep = json.load(open(f"{out}/entry_point.json", encoding="utf-8"))
            self.assertEqual(ep["style_profile"], FX_NEW)
            self.assertEqual(ep["style_profile_source"], "default_new_run_fx_20261017")
            rec = sp.read_record(out)
            self.assertEqual(rec["profile_id"], FX_NEW)
            self.assertEqual(set(rec["roles"]), set(sp.overridden_roles(FX_NEW)))
            self.assertEqual(rec["roles"]["SUPPORT_JA"]["sha256"], sp.SUPPORT_JA_STYLE_S3_SHA256)
            plan = json.load(open(f"{out}/plan_run_result.json", encoding="utf-8"))["a2"]["style_profile_plan"]
            self.assertEqual(plan["profile_id"], FX_NEW)
            self.assertEqual(plan["roles_sha256"]["KP_EN"], sp.K2_SHA256)
            self.assertEqual(plan["roles_sha256"]["KP_JA_MEANING"], sp.P8_KP_JA_SHA256)
            self.assertEqual(plan["roles_sha256"]["FULL_STORY"], sp.PD06_SHA256)
            self.assertEqual(plan["full_story_style_sha256"], sp.PD06_SHA256)
            self.assertEqual(plan["full_story_style_length"], 177)

    def test_main_plan_with_default_backend_flag_omitted_also_applies_fx(self):
        # --tts-backendも省略(既定=承認済みbackend)しても新profileが自動適用される(CLI指定忘れ対策)
        with tempfile.TemporaryDirectory() as d:
            out = f"{d}/o"
            self._main(["--slug", self.SLUG, "--run", self.RUN, "--out-dir", out, "--stage", "plan", "--level", "a2"])
            self.assertEqual(json.load(open(f"{out}/entry_point.json", encoding="utf-8"))["style_profile"], FX_NEW)

    def test_main_resume_with_old_n01_record_keeps_old_profile_and_warns(self):
        for old in ("n01", "coffee_n01_r2_p3_e1"):
            with tempfile.TemporaryDirectory() as d:
                out = f"{d}/o"
                os.makedirs(f"{out}/audit")
                json.dump(sp.build_record(old), open(sp.record_path(out), "w", encoding="utf-8"))
                text = self._main(["--slug", self.SLUG, "--run", self.RUN, "--out-dir", out, "--stage", "plan",
                                   "--tts-backend", FL, "--level", "a2"])
                ep = json.load(open(f"{out}/entry_point.json", encoding="utf-8"))
                self.assertEqual((ep["style_profile"], ep["style_profile_source"]), (old, "record"), old)
                self.assertIn("[WARN][STYLE-PROFILE] 旧profileでresume中", text)
                # 記録は書き換わらない
                self.assertEqual(sp.read_record(out)["profile_id"], old)
                # KP英語は従来経路(K2 key不使用)・KP日本語意味はJ3のまま
                self.assertFalse(sp.has_role_override(old, "KP_EN", "b1b"))
                self.assertFalse(sp.has_role_override(old, "KP_JA_MEANING", "a2"))

    def test_main_new_dir_does_not_warn_for_fx(self):
        with tempfile.TemporaryDirectory() as d:
            text = self._main(["--slug", self.SLUG, "--run", self.RUN, "--out-dir", f"{d}/o", "--stage", "plan",
                               "--tts-backend", FL, "--level", "a2"])
            self.assertNotIn("[WARN][STYLE-PROFILE]", text)

    def test_main_explicit_legacy_backend_without_flag_gives_warning_and_default_profile(self):
        with tempfile.TemporaryDirectory() as d:
            text = self._main(["--slug", self.SLUG, "--run", self.RUN, "--out-dir", f"{d}/o", "--stage", "plan",
                               "--tts-backend", "structured_separation", "--level", "a2"])
            self.assertIn("[WARN][STYLE-PROFILE] tts_backendがlegacy", text)
            self.assertFalse(os.path.exists(sp.record_path(f"{d}/o")))  # 記録は作らない(従来どおり)


class StdFullStoryPd06With6PercentSlowdownTests(unittest.TestCase):
    """Std Full StoryはPD06を逐語(A2減速instruction非連結)で渡し、既存の生成後6%減速関数
    (n3_tts.generate_a2_segment_with_slowdown)経由で生成する=PD06と6%減速の併用(ユーザー§2)。"""

    def _run_a2(self, profile, d):
        out = f"{d}/a2"
        os.makedirs(out)
        parts = {"title": "T", "part1": "P1 text.", "part2": "P2 text.", "part3": "P3 text.", "in_one_line": "IOL text."}
        support = {"preview": "プレビュー", "comment_1": "一", "comment_2": "二", "comment_3": "三", "comment_4": "四"}
        json.dump(parts, open(f"{out}/parts.json", "w", encoding="utf-8"))
        json.dump(support, open(f"{out}/a2_support_texts.json", "w", encoding="utf-8"))
        with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2", return_value={}),              mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback", side_effect=_ok),              mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety", side_effect=_ok),              mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=_ok) as slow:
            runner.generate_family_x_a2_segments(d, japanese_title="題", tts_backend=FL, style_profile=profile)
        return slow

    def test_fx_std_full_story_uses_pd06_verbatim_through_6pct_slowdown_function(self):
        with tempfile.TemporaryDirectory() as d:
            slow = self._run_a2(FX, d)
            by_name = {os.path.basename(c.args[1]): c.kwargs["style_prefix_override"] for c in slow.call_args_list}
            for n in ("full_story_part1.wav", "full_story_part2.wav", "full_story_part3.wav"):
                self.assertEqual(by_name[n], sp.PD06_TEXT, n)  # 逐語: A2_SLOWER_PACE_INSTRUCTIONを連結しない
                self.assertNotIn(runner.n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip(), by_name[n])
            self.assertNotEqual(by_name["in_one_line.wav"], sp.PD06_TEXT)  # IN_ONE_LINEは非対象(従来のbase)
            with open(f"{d}/a2/audit/tts_generation_results.json", encoding="utf-8") as f:
                res = json.load(f)
            for n in ("full_story_part1", "full_story_part2", "full_story_part3"):
                self.assertEqual(res["segments"][n]["style_profile"]["style_base_sha256"], sp.PD06_SHA256)
            self.assertEqual(res["segments"]["preview"]["style_profile"]["style_base_sha256"], sp.R2_SHA256)

    def test_default_profile_std_full_story_unchanged_style(self):
        with tempfile.TemporaryDirectory() as d:
            slow = self._run_a2("default", d)
            for c in slow.call_args_list:
                self.assertNotEqual(c.kwargs["style_prefix_override"], sp.PD06_TEXT)
                self.assertIn(runner.n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip(), c.kwargs["style_prefix_override"])



# ============================================================
# 9. Family Z 非影響(smoke)
# ============================================================
class FamilyZIsolationTests(unittest.TestCase):
    def test_z_does_not_import_x_style_profile(self):
        tree = ast.parse(open("er063_family_z_audio_01.py", encoding="utf-8").read())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                mods.add(n.module)
        # 2026-10-17 委任_15: 期待値を意図的に更新(旧: Zはer019_family_x_style_profile_01を一切importしない)。承認§2BでZはXの承認済みStyle定数を
        # 参照するためmodule importは許可するが、X既定profile・profile解決は使わない(別test[er063_family_z_audio_01_pd06_run_style_test_01]のAST検査で固定)。
        self.assertEqual({m for m in mods if m.startswith("er019")},
                         {"er019_family_x_audio_production_runner_01", "er019_family_x_style_profile_01"})

    def test_z_only_x_function_signature_unchanged(self):
        sig = inspect.signature(runner.generate_key_phrase_explanation_en_verified)
        self.assertEqual(list(sig.parameters), ["explanation_text", "out_path", "style_prefix_override", "tts_backend"])
        self.assertEqual(sig.parameters["tts_backend"].default, "structured_separation")

    def test_z_lazy_import_of_x_runner_and_mock_call_succeed(self):
        # Zは`x_runner.generate_key_phrase_explanation_en_verified`をlazy importする。x_runner先頭importで
        # `er019_family_x_style_profile_01._verify_constants()`が走る(新4定数のsha/長さ検証を含む)が、
        # import自体と当該関数のmock呼出が成功し、Zが渡すstyle(Z自前のStyle)がそのまま送信されることを確認する。
        import importlib
        x = importlib.import_module("er019_family_x_audio_production_runner_01")
        sp._verify_constants()
        zs = "Z-OWN-STYLE-TEXT"
        with mock.patch.object(repro01, "generate_narration_snippet_verified_strict",
                               return_value={"status": "OK"}) as strict:
            r = x.generate_key_phrase_explanation_en_verified("an explanation.", "tmp/out.wav",
                                                              style_prefix_override=zs, tts_backend=FL)
        self.assertEqual(r["status"], "OK")
        kw = strict.call_args.kwargs
        self.assertEqual(kw["style_prefix_override"], zs)
        self.assertEqual(kw["max_attempts"], 3)
        self.assertEqual(kw["tts_backend"], FL)

    def test_z_role_style_constants_unchanged(self):
        # 2026-10-17 委任_15: 期待値を意図的に更新(旧: Zの_K2/_R2/_E1コピー定数のsha固定。ZはXの承認済み定数[K2/S3/E1]を参照する)。
        import er063_family_z_audio_01 as z
        for label, sha in (("K2", sp.K2_SHA256), ("S3", sp.SUPPORT_JA_STYLE_S3_SHA256), ("E1", sp.E1_SHA256),
                           ("PD06", sp.PD06_SHA256), ("P7", sp.P7_SHA256), ("P8_KP", sp.P8_KP_JA_SHA256)):
            self.assertEqual(_sha(z._STYLE_TEXT[label]), sha, label)
            self.assertEqual(z._STYLE_SHA256[label], sha, label)

    def test_z_source_references_x_constants_but_not_x_profile_machinery(self):
        # 2026-10-17 委任_15: 期待値を意図的に更新(旧: ZはXの新定数・profileを一切参照しない。承認§2BでZはX共通定数を参照する)。
        # ただしX既定profile(fx_20261016/17・DEFAULT_NEW_RUN_PROFILE)・profile解決・Master Store key系には従属しない(Opus R-C1)。
        src = open("er063_family_z_audio_01.py", encoding="utf-8").read()
        for token in ("PD06_TEXT", "P8_KP_JA_TEXT", "P7_TEXT", "K2_TEXT", "E1_TEXT", "SUPPORT_JA_STYLE_S3_20261017"):
            self.assertIn(token, src)
        for token in ("fx_20261016", "KP_EN_STORE_STYLE_ID", "ensure_key_phrase_english_component_styled"):
            self.assertNotIn(token, src)


if __name__ == "__main__":
    unittest.main()
