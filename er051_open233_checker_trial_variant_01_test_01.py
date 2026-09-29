# -*- coding: utf-8 -*-
# ============================================================
# er051_open233_checker_trial_variant_01_test_01.py
# OPEN-233-CHECKER-REDESIGN-TRIAL-01 (Phase A、委任_01) mock test
# ============================================================
# ネットワーク呼び出し・API支出は一切行わない。既存er050_output/配下の
# 保存済みrun json(V0=GPT6-MODEL-COMPARISON-TRIAL-01実測、84 call)を
# 再生(replay)してclassify_deviation_trial()等のTrial variantロジックを
# 検証する。Production(er003_v1_en_direct_vfl_01_generate.py)は
# import(読み取り専用)のみで、テスト内で一切変更しない。
from __future__ import annotations

import copy
import json
import unittest

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er051_open233_checker_trial_variant_01 as trial


class ClassifyDeviationBasicTest(unittest.TestCase):
    """classify_deviation_trial()の純粋なロジックを合成dictで検証する。"""

    def _base(self, severity="MINOR", **flags):
        d = {"claim_in_article": "x", "issue": "y", "severity": severity, "explanation": "z"}
        for k in vfl01.DEVIATION_FLAG_KEYS:
            d[k] = bool(flags.get(k, False))
        return d

    def test_major_stays_blocking_fail_closed_all_variants(self):
        d = self._base(severity="MAJOR", changed_fact=True)
        for variant in trial.VARIANTS:
            out = trial.classify_deviation_trial(d, variant)
            self.assertEqual(out["severity_final"], "BLOCKING")
            self.assertEqual(out["action"], "STOP")
            self.assertEqual(out["rule_id"], "existing_major_v2")

    def test_minor_promotable_flag_promotes_to_blocking(self):
        for flag in trial.PROMOTABLE_FLAG_KEYS:
            d = self._base(severity="MINOR", **{flag: True})
            out = trial.classify_deviation_trial(d, "V1")
            self.assertEqual(out["severity_final"], "BLOCKING", msg=flag)
            self.assertEqual(out["rule_id"], "promote_deterministic_flag_v1")
            self.assertIn(flag, out["basis"])

    def test_minor_non_promotable_flag_not_promoted(self):
        d = self._base(severity="MINOR", changed_fact=True, unsupported_new_claim=True)
        out = trial.classify_deviation_trial(d, "V1")
        self.assertNotEqual(out["severity_final"], "BLOCKING")

    def test_v1_default_quality_for_plain_minor(self):
        d = self._base(severity="MINOR")
        out = trial.classify_deviation_trial(d, "V1")
        self.assertEqual(out["severity_final"], "QUALITY")
        self.assertEqual(out["action"], "LOG_AND_PASS")
        self.assertEqual(out["rule_id"], "default_quality_v1")

    def test_v2_conservative_default_when_schema_fields_absent(self):
        # 旧データreplay相当(schema variantフィールドが無い)。
        # ACCEPTABLEへは倒さず、安全側でQUALITYにする。
        d = self._base(severity="MINOR")
        out = trial.classify_deviation_trial(d, "V2")
        self.assertEqual(out["severity_final"], "QUALITY")
        self.assertEqual(out["rule_id"], "default_quality_v2_conservative")

    def test_v2_acceptable_when_consistent_and_ledger_fact_basis(self):
        d = self._base(severity="MINOR")
        d["ledger_field_basis"] = "ledger_fact"
        d["observation_consistent"] = True
        out = trial.classify_deviation_trial(d, "V2")
        self.assertEqual(out["severity_final"], "ACCEPTABLE")
        self.assertEqual(out["action"], "PASS")

    def test_v2_quality_when_consistent_but_notes_basis(self):
        d = self._base(severity="MINOR")
        d["ledger_field_basis"] = "notes_writer_guidance"
        d["observation_consistent"] = True
        out = trial.classify_deviation_trial(d, "V2")
        self.assertEqual(out["severity_final"], "QUALITY")

    def test_v2_factual_constraint_conflict_overrides_qualifier(self):
        # qualifier(留保文)が存在しても、factual_constraintと矛盾する
        # 場合は非STOP化しない(v0.2 §6-3必須除外条件)。
        d = self._base(severity="MINOR", changed_causality=True)
        d["qualifier_present"] = True
        d["qualifier_text"] = "large, lasting"
        d["ledger_field_basis"] = "notes_factual_constraint"
        d["observation_consistent"] = False
        out = trial.classify_deviation_trial(d, "V2")
        self.assertEqual(out["severity_final"], "BLOCKING")
        self.assertEqual(out["rule_id"], "factual_constraint_override_v1")

    def test_origin_field_does_not_affect_classification(self):
        # originフィールドは分類ロジックの入力に一切使わない
        # (JA段origin=None誤降格の罠を回避する設計、v0.2 §1-E/§6-1)。
        d1 = self._base(severity="MAJOR", changed_causality=True)
        d1["origin"] = "ja_source"
        d2 = copy.deepcopy(d1)
        d2["origin"] = None
        for variant in trial.VARIANTS:
            out1 = trial.classify_deviation_trial(d1, variant)
            out2 = trial.classify_deviation_trial(d2, variant)
            for key in ("severity_final", "action", "basis", "rule_id"):
                self.assertEqual(out1[key], out2[key], msg=f"{variant}/{key}")

    def test_unknown_variant_raises(self):
        d = self._base()
        with self.assertRaises(ValueError):
            trial.classify_deviation_trial(d, "V9")

    def test_classify_does_not_mutate_input(self):
        d = self._base(severity="MINOR", changed_actor=True)
        original = copy.deepcopy(d)
        trial.classify_deviation_trial(d, "V1")
        self.assertEqual(d, original)


class ClassifyParsedResultTest(unittest.TestCase):
    def test_overall_action_trial_stop_when_any_blocking(self):
        parsed = {
            "deviations": [
                {"claim_in_article": "a", "issue": "i", "severity": "MAJOR", "explanation": "e",
                 **{k: False for k in vfl01.DEVIATION_FLAG_KEYS}},
            ],
            "overall_status": "LEDGER_DEVIATION",
        }
        out = trial.classify_parsed_result_trial(parsed, "V1")
        self.assertEqual(out["overall_action_trial"], "STOP")

    def test_overall_action_trial_pass_when_no_deviations(self):
        parsed = {"deviations": [], "overall_status": "LEDGER_COMPLIANT"}
        out = trial.classify_parsed_result_trial(parsed, "V1")
        self.assertEqual(out["overall_action_trial"], "PASS")


class PromptSchemaVariantTest(unittest.TestCase):
    def test_v0_v1_prompt_identical_to_production(self):
        self.assertEqual(trial.build_trial_prompt_template("V0"), vfl01.DEVIATION_PROMPT_TEMPLATE)
        self.assertEqual(trial.build_trial_prompt_template("V1"), vfl01.DEVIATION_PROMPT_TEMPLATE)

    def test_v2_v3_prompt_appends_diff_block(self):
        for variant in ("V2", "V3"):
            built = trial.build_trial_prompt_template(variant)
            self.assertEqual(built, vfl01.DEVIATION_PROMPT_TEMPLATE + trial.TRIAL_PROMPT_DIFF_BLOCK_V01)
            self.assertTrue(built.startswith(vfl01.DEVIATION_PROMPT_TEMPLATE))

    def test_diff_block_sha256_matches_design_doc(self):
        expected = "c7195a19fae043096318bfac3bac88327de1e522ab5fbddae6de53ea1f4efa80"
        self.assertEqual(trial.sha256_text(trial.TRIAL_PROMPT_DIFF_BLOCK_V01), expected)

    def test_v0_v1_schema_identical_to_production(self):
        self.assertEqual(trial.build_trial_deviation_schema("V0"), vfl01.DEVIATION_JSON_SCHEMA)
        self.assertEqual(trial.build_trial_deviation_schema("V1"), vfl01.DEVIATION_JSON_SCHEMA)

    def test_v2_v3_schema_adds_five_fields_and_stays_strict(self):
        for variant in ("V2", "V3"):
            schema = trial.build_trial_deviation_schema(variant)
            item = schema["schema"]["properties"]["deviations"]["items"]
            for key in trial.TRIAL_SCHEMA_EXTRA_KEYS:
                self.assertIn(key, item["properties"])
                self.assertIn(key, item["required"])
            self.assertFalse(item["additionalProperties"])
            self.assertTrue(schema["strict"])
            # 既存10フラグ+severity等も維持されていること(schema拡張であり置換ではない)
            for key in vfl01.DEVIATION_FLAG_KEYS:
                self.assertIn(key, item["properties"])

    def test_production_constants_unchanged_after_import(self):
        # Dangling Reference確認: er051のimportがvfl01側の定数を変更していないこと。
        actual = {
            "DEVIATION_PROMPT_TEMPLATE": trial.sha256_text(vfl01.DEVIATION_PROMPT_TEMPLATE),
            "DEVIATION_DEVELOPER_MESSAGE": trial.sha256_text(vfl01.DEVIATION_DEVELOPER_MESSAGE),
            "DEVIATION_JSON_SCHEMA": trial.sha256_text(json.dumps(vfl01.DEVIATION_JSON_SCHEMA, sort_keys=True)),
        }
        self.assertEqual(actual, g6.PHASE_A_SHA256)


class V4APromptSchemaVariantTest(unittest.TestCase):
    """V4A(委任_03): V2のPrompt差分ブロックにカテゴリ境界明確化ブロックを追加。
    schema/post-hocはV2と同一。"""

    def test_v4a_prompt_appends_v01_then_v4a_block(self):
        built = trial.build_trial_prompt_template("V4A")
        expected = vfl01.DEVIATION_PROMPT_TEMPLATE + trial.TRIAL_PROMPT_DIFF_BLOCK_V01 + trial.TRIAL_PROMPT_DIFF_BLOCK_V4A
        self.assertEqual(built, expected)
        self.assertTrue(built.startswith(vfl01.DEVIATION_PROMPT_TEMPLATE + trial.TRIAL_PROMPT_DIFF_BLOCK_V01))

    def test_v4a_diff_block_sha256_matches_design_doc(self):
        expected = "7d8229090910ec1979ac2dbadd2ada8715c14ea441a4acd6edf5279291efe1ad"
        self.assertEqual(trial.sha256_text(trial.TRIAL_PROMPT_DIFF_BLOCK_V4A), expected)

    def test_v4a_diff_block_has_no_fixture_specific_wording(self):
        # Fable判定(2): fixture固有の固有名詞(実在の研究者名・記事の固有名詞等)を
        # 含めない一般的なcategory境界記述であること。
        forbidden = ["Harvard", "Kareem", "Haggag", "Giovanni", "Paci", "taxi", "tip"]
        for word in forbidden:
            self.assertNotIn(word, trial.TRIAL_PROMPT_DIFF_BLOCK_V4A, msg=word)

    def test_v4a_schema_identical_to_v2(self):
        # schema名(open233_trial_deviation_schema_v2/v4a)はvariant別に異なる
        # ことを許容し、実質的なitem schema(properties/required/strict)が
        # 同一であることを検証する(設計書§1-補(2)「schema variant・post-hoc v2
        # はV2と同一」)。
        schema_v2 = trial.build_trial_deviation_schema("V2")
        schema_v4a = trial.build_trial_deviation_schema("V4A")
        self.assertEqual(schema_v2["schema"], schema_v4a["schema"])
        self.assertEqual(schema_v2["strict"], schema_v4a["strict"])

    def test_v4a_post_hoc_identical_to_v2_for_various_inputs(self):
        base = {"claim_in_article": "x", "issue": "y", "explanation": "z"}
        cases = [
            {**base, "severity": "MAJOR", **{k: False for k in vfl01.DEVIATION_FLAG_KEYS}},
            {**base, "severity": "MINOR", **{k: False for k in vfl01.DEVIATION_FLAG_KEYS}, "changed_actor": True},
            {**base, "severity": "MINOR", **{k: False for k in vfl01.DEVIATION_FLAG_KEYS},
             "ledger_field_basis": "ledger_fact", "observation_consistent": True},
        ]
        for d in cases:
            out_v2 = trial.classify_deviation_trial(d, "V2")
            out_v4a = trial.classify_deviation_trial(d, "V4A")
            for key in ("severity_final", "action", "basis", "rule_id"):
                self.assertEqual(out_v2[key], out_v4a[key], msg=key)


class NotesClassificationTest(unittest.TestCase):
    def test_hormuz_notes_all_factual_constraint(self):
        self.assertEqual(len(trial.HORMUZ_NOTES_CLASSIFICATION), 12)
        self.assertTrue(all(v == "factual_constraint" for v in trial.HORMUZ_NOTES_CLASSIFICATION.values()))

    def test_meta_notes_all_factual_constraint(self):
        self.assertEqual(len(trial.META_NOTES_CLASSIFICATION), 15)
        self.assertTrue(all(v == "factual_constraint" for v in trial.META_NOTES_CLASSIFICATION.values()))

    def test_filter_removes_writer_guidance_notes_only(self):
        ledger_text = (
            "[VERIFIED] HF-001: claim one\n"
            "  scope: s1\n"
            "  notes_for_writer: keep me (factual constraint)\n"
            "\n"
            "[VERIFIED] X-999: claim two\n"
            "  scope: s2\n"
            "  notes_for_writer: drop me (writer guidance)\n"
        )
        classification = {"HF-001": "factual_constraint", "X-999": "writer_guidance"}
        out = trial.filter_ledger_notes_by_classification(ledger_text, classification)
        self.assertIn("keep me (factual constraint)", out)
        self.assertNotIn("drop me (writer guidance)", out)
        self.assertIn("claim one", out)
        self.assertIn("claim two", out)

    def test_filter_defaults_unknown_fact_id_to_factual_constraint(self):
        ledger_text = (
            "[VERIFIED] UNKNOWN-1: claim\n"
            "  notes_for_writer: should stay (unknown id, safe default)\n"
        )
        out = trial.filter_ledger_notes_by_classification(ledger_text, {})
        self.assertIn("should stay (unknown id, safe default)", out)


class ReplayV0DataTest(unittest.TestCase):
    """既存er050_output/配下の保存済みrun json(V0実測、ネットワーク呼び出し
    なし)をreplayし、classify_deviation_trial()の挙動を実データで検証する。"""

    def test_real_minor_changed_actor_record_promotes_to_blocking(self):
        # step1_er009_changed_actor_n5 run_4(gpt-6-luna): severity=MINOR,
        # changed_actor=true(報告§Phase B-6の実測どおり)。
        parsed = trial.load_v0_parsed(
            "step1_er009_changed_actor_n5", "er009_changed_actor", "gpt-6-luna", attempt=4)
        out = trial.classify_parsed_result_trial(parsed, "V1")
        self.assertTrue(any(d["changed_actor"] and d["severity"] == "MINOR" for d in parsed["deviations"]))
        self.assertEqual(out["overall_action_trial"], "STOP")
        promoted = [d for d in out["deviations"] if d["rule_id"] == "promote_deterministic_flag_v1"]
        self.assertGreaterEqual(len(promoted), 1)

    def test_a_group_majors_remain_blocking_after_replay(self):
        for fixture_id in ("A2A3", "A4", "A5"):
            parsed = trial.load_v0_parsed("step1", fixture_id, "gpt-6-luna", attempt=1)
            for variant in trial.VARIANTS:
                out = trial.classify_parsed_result_trial(parsed, variant)
                self.assertEqual(out["overall_action_trial"], "STOP", msg=f"{fixture_id}/{variant}")
                for d in out["deviations"]:
                    if d["severity"] == "MAJOR":
                        self.assertEqual(d["severity_final"], "BLOCKING")

    def test_a5_minor_changed_actor_item_promotes_across_variants(self):
        # A5(gpt-6-luna run_1)にはMAJOR1件+MINOR(changed_actor=true)1件が
        # 含まれる(GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md §Phase B-3)。
        parsed = trial.load_v0_parsed("step1", "A5", "gpt-6-luna", attempt=1)
        minor_actor = [d for d in parsed["deviations"] if d["severity"] == "MINOR" and d["changed_actor"]]
        self.assertEqual(len(minor_actor), 1)
        for variant in trial.VARIANTS:
            out = trial.classify_deviation_trial(minor_actor[0], variant)
            self.assertEqual(out["severity_final"], "BLOCKING", msg=variant)

    def test_er009_eight_categories_remain_blocking_after_replay(self):
        # er009_changed_actor以外の8種は現行でも全件MAJOR PASSしている
        # (GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md §Phase B-3)ため、
        # 本Trial分類でもBLOCKINGを維持すること。
        categories = [
            "changed_number", "changed_scope", "changed_causality", "changed_certainty",
            "changed_negation", "changed_comparison", "changed_time", "unsupported_new_claim",
        ]
        for cat in categories:
            parsed = trial.load_v0_parsed("step1", f"er009_{cat}", "gpt-6-luna", attempt=1)
            for variant in trial.VARIANTS:
                out = trial.classify_parsed_result_trial(parsed, variant)
                self.assertEqual(out["overall_action_trial"], "STOP", msg=f"{cat}/{variant}")

    def test_b_group_no_erroneous_promotion_v1(self):
        # B1/B2_hormuz/B3/B4/Meta_run03_standard(gpt-6-luna run_1)を
        # replayし、既存で4カテゴリflagがfalseのdeviationがV1適用後も
        # 誤ってBLOCKINGへ昇格しない(promote_deterministic_flag_v1が
        # 発火しない)ことを確認する(誤昇格0件)。
        for fixture_id in ("B1", "B2_hormuz", "B3", "B4", "Meta_run03_standard"):
            parsed = trial.load_v0_parsed("step2", fixture_id, "gpt-6-luna", attempt=1)
            out = trial.classify_parsed_result_trial(parsed, "V1")
            for d in out["deviations"]:
                if d["rule_id"] == "promote_deterministic_flag_v1":
                    triggered = [k for k in trial.PROMOTABLE_FLAG_KEYS if d.get(k)]
                    self.assertTrue(triggered, msg=f"{fixture_id}: promoted without a triggered flag")

    def test_ja_stage_records_have_no_origin_key_and_are_not_auto_downgraded(self):
        # JA段(ja_original/ja_r2)のrecordはsource_article_text未指定のため
        # origin fieldを持たない(vfl01の仕様どおり)。classify_deviation_trial
        # はoriginを参照しないため、origin有無に関わらず同じseverity_final
        # になることをここでも確認する(実データでの再確認)。
        parsed = trial.load_v0_parsed("step3", "hormuz_run03_ja_r2", "gpt-6-luna", attempt=3)
        major_causality = [d for d in parsed["deviations"] if d["severity"] == "MAJOR" and d["changed_causality"]]
        self.assertGreaterEqual(len(major_causality), 1)
        for d in major_causality:
            self.assertNotIn("origin", d)
            out = trial.classify_deviation_trial(d, "V2")
            self.assertEqual(out["severity_final"], "BLOCKING")


class V4CRegressionFixtureTest(unittest.TestCase):
    """V4-C(委任_03、設計書§1-補(4)): OPEN-233-CHECKER-REDESIGN-TRIAL-01
    Trial 1(委任_02)のStep1 changed_actor n=5で観測された、未昇格3件
    (V2#3/V3#3/V3#5)をnegative regression fixtureとしてfreezeする。

    fixtureの真の逸脱カテゴリはchanged_actor(gold=BLOCKING)だが、LLMは
    changed_actor=false(unsupported_new_claimのみtrue)・severity=MINORを
    返した。本テストは「このLLM出力パターンに対して、現行のV1昇格ルール
    (promote_deterministic_flag_v1、4カテゴリflagベース)は昇格しない
    (=severity_final!=BLOCKINGのまま)」という**現行ルールの既知の挙動**を
    固定するものであり、goldをACCEPTABLE/QUALITYへ変更する提案ではない。
    将来Prompt/ルールを拡張(例: V4-A)した際、この3件の実際のLLM再出力
    (別途Trial 2で新規に取得するraw response)がchanged_actor=trueへ変化して
    昇格するようになったかどうかを、本fixture(冷凍済みの旧LLM出力)と
    突き合わせて机上検証できるようにする。"""

    V4C_RECORDS = [
        ("V2#3", "er051_output/open233_checker_trial_01/trial_01/"
                  "step1_changed_actor_n5/er009_changed_actor/V2/run_3.json"),
        ("V3#3", "er051_output/open233_checker_trial_01/trial_01/"
                  "step1_changed_actor_n5/er009_changed_actor/V3/run_3.json"),
        ("V3#5", "er051_output/open233_checker_trial_01/trial_01/"
                  "step1_changed_actor_n5/er009_changed_actor/V3/run_5.json"),
    ]

    def _load_raw_deviation(self, path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        devs = d["raw_parsed"]["deviations"]
        self.assertEqual(len(devs), 1, msg=path)
        return devs[0]

    def test_frozen_pattern_is_changed_actor_false_unsupported_new_claim_true_minor(self):
        for label, path in self.V4C_RECORDS:
            dev = self._load_raw_deviation(path)
            self.assertEqual(dev["severity"], "MINOR", msg=label)
            self.assertFalse(dev["changed_actor"], msg=label)
            self.assertTrue(dev["unsupported_new_claim"], msg=label)

    def test_v1_rule_does_not_promote_frozen_pattern(self):
        for label, path in self.V4C_RECORDS:
            dev = self._load_raw_deviation(path)
            out = trial.classify_deviation_trial(dev, "V1")
            self.assertNotEqual(out["severity_final"], "BLOCKING", msg=label)
            self.assertNotEqual(out["rule_id"], "promote_deterministic_flag_v1", msg=label)

    def test_v2_v4a_post_hoc_layer_alone_also_does_not_promote_frozen_pattern(self):
        # V4-AはPrompt側の境界明確化であり、post-hoc昇格ルール自体は変更しない
        # (設計書§1-補(2))。post-hoc層だけをこの冷凍済みパターンへ再適用しても
        # 昇格しないことを確認する(post-hocだけでは解決しないことの記録)。
        for label, path in self.V4C_RECORDS:
            dev = self._load_raw_deviation(path)
            for variant in ("V2", "V4A"):
                out = trial.classify_deviation_trial(dev, variant)
                self.assertNotEqual(out["severity_final"], "BLOCKING", msg=f"{label}/{variant}")


if __name__ == "__main__":
    unittest.main()
