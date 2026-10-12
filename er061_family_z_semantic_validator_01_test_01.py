"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_04A: er061 意味保持Validatorのtest。

本ファイルのtestはAPI呼出なし(第2層はstub)。実呼出calibrationは
`er061_family_z_semantic_validator_01.py --calibrate` で別途実行し、その結果
(er060_output/melos_production_e2e_01/validator_calibration_01.json)の整合だけをここで検証する。"""
import copy
import json
import os
import shutil
import tempfile
import unittest
import warnings
from types import SimpleNamespace

import er061_family_z_semantic_validator_01 as v

FIX = "er061_fixtures"


def _fx(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


F1 = _fx("F1_trial2_r2_normal.md")
F2 = _fx("F2_existing_luna_normal.md")
F3 = _fx("F3_names_omitted_normal.md")
F5 = _fx("F5_ending_too_late.md")
ANCHORS = v.load_anchors()
SRC = v.load_source_info()
QUOTE = "Melos stood before the ruler"


def make_items(anchors=ANCHORS, overrides=None, quote=QUOTE):
    overrides = overrides or {}
    items = []
    for a in anchors["anchors"]:
        it = {"anchor_id": a["id"], "category": a["category"], "status": "preserved", "severity": "none",
              "evidence_quote": quote, "note": "ok"}
        it.update(overrides.get(a["id"], {}))
        items.append(it)
    return {"items": items}


class StubClient:
    """responses.create(**kw) を模す。payloads は呼出ごとに順に返す(尽きたら最後を繰り返す)。"""

    def __init__(self, payloads, model="gpt-6-luna"):
        self.payloads = list(payloads)
        self.calls = []
        self.model = model
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls.append(kw)
        p = self.payloads[min(len(self.calls) - 1, len(self.payloads) - 1)]
        text = p if isinstance(p, str) else json.dumps(p, ensure_ascii=False)
        return SimpleNamespace(
            output_text=text, model=self.model, id=f"resp_{len(self.calls)}",
            usage=SimpleNamespace(input_tokens=3000, output_tokens=1500,
                                  input_tokens_details=SimpleNamespace(cached_tokens=0)))


MAJOR_ENDING = {"N1": {"status": "altered", "severity": "major", "note": "ending changed"}}


class AnchorsTest(unittest.TestCase):
    def test_anchors_frozen_and_valid(self):
        a = v.load_anchors()
        self.assertTrue(a["created_before_candidate"])
        self.assertTrue(v._verify_self_sha(a))
        self.assertEqual(a["seed_sha256"], v.sha256_file(os.path.join(v.SEED_DIR, "seed.json")))
        cats = {x["category"] for x in a["anchors"]}
        self.assertTrue({"role_relation", "event", "causality", "sequence", "ending", "charm", "added_fact"} <= cats)
        self.assertTrue(a["forbidden_endings"])

    def test_seed_unchanged_vs_provenance(self):
        with open(os.path.join(v.SEED_DIR, "SEED_PROVENANCE.json"), encoding="utf-8") as f:
            prov = json.load(f)
        for name, meta in prov["files"].items():
            self.assertEqual(v.sha256_file(os.path.join(v.SEED_DIR, name)), meta["sha256"], name)

    def test_tamper_detected(self):
        tmp = tempfile.mkdtemp()
        try:
            p = os.path.join(tmp, "anchors.json")
            shutil.copy(v.ANCHORS_PATH, p)
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            d["anchors"][0]["required"] = False
            with open(p, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
            with self.assertRaises(v.AnchorsIntegrityError):
                v.load_anchors(p)
        finally:
            shutil.rmtree(tmp)

    def test_freeze_is_idempotent_and_does_not_overwrite(self):
        tmp = tempfile.mkdtemp()
        try:
            p = os.path.join(tmp, "v", "anchors.json")
            a1 = v.freeze_anchors(p)
            a2 = v.freeze_anchors(p)
            self.assertEqual(a1["sha256_self"], a2["sha256_self"])
            self.assertEqual(a1["sha256_self"], v.load_anchors()["sha256_self"])
        finally:
            shutil.rmtree(tmp)

    def test_build_takes_no_candidate(self):
        import inspect
        self.assertEqual(list(inspect.signature(v.build_validator_anchors).parameters), ["seed_dir"])


class Layer1Test(unittest.TestCase):
    def test_normal_fixtures_not_fail(self):
        for t in (F1, F2, F3):
            r = v.layer1_check(t, ANCHORS)
            self.assertNotEqual(r["verdict"], "FAIL", r)

    def test_names_not_required(self):
        # F3は人物名を持たない正常例。名前の欠落だけではFAILにも(名前に関する)WARNにもならない
        r = v.layer1_check(F3, ANCHORS)
        self.assertEqual(r["verdict"], "PASS")
        self.assertNotIn("Selinuntius", F3)

    def test_forbidden_ending_hard_fail(self):
        r = v.layer1_check(F5, ANCHORS)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertTrue(any(h["id"].startswith("FORBIDDEN_ENDING") for h in r["hard_fails"]))

    def test_too_late_in_middle_is_not_hard_fail(self):
        # 末尾N段落以外(中盤の迷い)の'too late'は高精度でないためhard FAILにしない
        t = F1.replace("“Why did I make that promise?” he whispered.",
                       "“It is too late,” he whispered.")
        self.assertNotEqual(v.layer1_check(t, ANCHORS)["verdict"], "FAIL")

    def test_foreign_full_name_rule(self):
        a = copy.deepcopy(ANCHORS)
        a["foreign_name_rules"]["full_names"] = [{"full_name": "Eugene Aram", "short_forms": ["Aram"]}]
        t = F1 + "\nEugene Aram watched them go.\n"
        r = v.layer1_check(t, a)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("FOREIGN_NAME_RULE_VIOLATION", [h["id"] for h in r["hard_fails"]])
        self.assertEqual(v.layer1_check(F1 + "\nAram watched them go.\n", a)["verdict"], "PASS")

    def test_all_required_anchors_missing(self):
        r = v.layer1_check("The cat sat on a mat. It was a nice day.\n\nBirds sang loudly.", ANCHORS)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("ALL_REQUIRED_ANCHORS_MISSING", [h["id"] for h in r["hard_fails"]])

    def test_partial_missing_is_warn_only(self):
        r = v.layer1_check(_fx("F4_friend_relation_missing.md"), ANCHORS)
        self.assertEqual(r["verdict"], "WARN")
        self.assertFalse(r["hard_fails"])

    def test_order_is_not_judged_in_layer1(self):
        paras = v.split_paragraphs(F1)
        shuffled = "\n\n".join(reversed(paras[:-3])) + "\n\n" + "\n\n".join(paras[-3:])
        r = v.layer1_check(shuffled, ANCHORS)
        self.assertNotEqual(r["verdict"], "FAIL")


class QuoteVerificationTest(unittest.TestCase):
    def test_verbatim_with_typographic_variation(self):
        self.assertTrue(v.quote_is_verbatim('"Give me three days," he said', F1))
        self.assertTrue(v.quote_is_verbatim("Melos   stood before THE ruler", F1))
        self.assertTrue(v.quote_is_verbatim("I will wait.", F1))  # *“I will wait.”* markdown/curly

    def test_fabricated_or_too_short_quotes_rejected(self):
        self.assertFalse(v.quote_is_verbatim("The dragon breathed fire over the wall", F1))
        self.assertFalse(v.quote_is_verbatim("", F1))
        self.assertFalse(v.quote_is_verbatim("ab", F1))


class SchemaTest(unittest.TestCase):
    def test_strict_schema_shape(self):
        s = v.JUDGE_SCHEMA
        self.assertTrue(s["strict"])
        item = s["schema"]["properties"]["items"]["items"]
        self.assertFalse(item["additionalProperties"])
        self.assertEqual(set(item["required"]), set(item["properties"]))
        self.assertFalse(s["schema"]["additionalProperties"])
        self.assertEqual(set(item["properties"]["status"]["enum"]), {"preserved", "altered", "missing"})
        self.assertIn("sequence", item["properties"]["category"]["enum"])

    def test_request_uses_routing_model_and_strict_schema(self):
        c = StubClient([make_items()])
        v.validate_semantic_preservation(F1, "b1b", client=c, anchors=ANCHORS, source_info=SRC)
        kw = c.calls[0]
        self.assertEqual(kw["model"], "gpt-6-luna")
        self.assertEqual(kw["text"]["format"]["type"], "json_schema")
        self.assertTrue(kw["text"]["format"]["strict"])
        user = kw["input"][1]["content"]
        for a in ANCHORS["anchors"]:
            self.assertIn(f'anchor_id={a["id"]}', user)
        self.assertIn("メロスは激怒した", user)  # 原作(日本語)を渡している
        self.assertIn("Melos stood before the ruler", user)  # 候補本文

    def test_routing_key_is_fixed_to_luna(self):
        import er006_model_routing_contract_01 as r
        self.assertEqual(r.PROCESS_MODEL_MAP[v.JUDGE_ROUTING_KEY], "gpt-6-luna")


class Layer2MockTest(unittest.TestCase):
    def run_v(self, payloads, text=F1, level="b1b", **kw):
        c = StubClient(payloads)
        res = v.validate_semantic_preservation(text, level, client=c, anchors=ANCHORS, source_info=SRC,
                                               tracker=v.CostTracker(cap_jpy=8.0), **kw)
        return res, c

    def test_all_preserved_pass_single_call(self):
        res, c = self.run_v([make_items()])
        self.assertEqual(res["verdict"], "PASS")
        self.assertFalse(res["stop_required"])
        self.assertEqual(len(c.calls), 1)
        self.assertEqual(res["model"]["actual_model_ids"], ["gpt-6-luna"])
        self.assertGreater(res["cost_jpy"], 0)
        self.assertEqual(res["usage_total"]["input_tokens"], 3000)

    def test_minor_is_warn(self):
        res, c = self.run_v([make_items(overrides={"M1": {"status": "altered", "severity": "minor"}})])
        self.assertEqual(res["verdict"], "WARN")
        self.assertFalse(res["stop_required"])

    def test_major_fail_requires_two_agreeing_judgements(self):
        p = make_items(overrides=MAJOR_ENDING)
        res, c = self.run_v([p, p])
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(res["stop_required"])
        self.assertEqual(len(c.calls), 2)
        self.assertTrue(res["layer2"]["confirmed"])
        self.assertEqual(res["layer2"]["confirmed_categories"], ["ending"])

    def test_major_then_pass_is_needs_review(self):
        res, c = self.run_v([make_items(overrides=MAJOR_ENDING), make_items()])
        self.assertEqual(res["verdict"], "NEEDS_REVIEW")
        self.assertTrue(res["stop_required"])
        self.assertFalse(res["layer2"]["confirmed"])

    def test_major_then_different_category_is_needs_review(self):
        other = {"E3": {"status": "missing", "severity": "major", "evidence_quote": ""}}
        res, c = self.run_v([make_items(overrides=MAJOR_ENDING), make_items(overrides=other)])
        self.assertEqual(res["verdict"], "NEEDS_REVIEW")

    def test_fabricated_quote_invalidates_and_needs_review(self):
        bad = make_items(overrides={"R3": {"evidence_quote": "The dragon breathed fire over the wall"}})
        res, c = self.run_v([bad])  # 無効 -> 再試行1回 -> 同じ無効 -> NEEDS_REVIEW
        self.assertEqual(res["verdict"], "NEEDS_REVIEW")
        self.assertEqual(len(c.calls), 2)
        j = res["layer2"]["judgements"][0]
        self.assertFalse(j["valid"])
        self.assertIn("evidence_quote_not_verbatim:R3", j["invalid_reasons"])

    def test_invalid_then_valid_recovers(self):
        bad = make_items(overrides={"R3": {"evidence_quote": "totally made up quote"}})
        res, c = self.run_v([bad, make_items()])
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(len(c.calls), 2)

    def test_fabricated_quote_on_fail_item_does_not_count_as_fail(self):
        # 捏造引用付きの「major altered」は有効なFAIL根拠にならない(NEEDS_REVIEW側)
        bad = make_items(overrides={"N1": {"status": "altered", "severity": "major",
                                           "evidence_quote": "The ruler laughed and the friend died"}})
        res, c = self.run_v([bad])
        self.assertEqual(res["verdict"], "NEEDS_REVIEW")
        self.assertNotEqual(res["verdict"], "FAIL")

    def test_missing_item_may_have_empty_quote(self):
        p = make_items(overrides={"E3": {"status": "missing", "severity": "major", "evidence_quote": ""}})
        res, c = self.run_v([p, p])
        self.assertEqual(res["verdict"], "FAIL")

    def test_coverage_gap_and_unknown_and_duplicate_and_category_mismatch(self):
        full = make_items()
        for mutate, tag in (
            (lambda d: d["items"].pop(), "coverage_missing"),
            (lambda d: d["items"].append(dict(d["items"][0], anchor_id="ZZ")), "unknown_anchor_id"),
            (lambda d: d["items"].append(dict(d["items"][0])), "duplicate_anchor_id"),
            (lambda d: d["items"][0].update(category="ending"), "category_mismatch"),
        ):
            d = copy.deepcopy(full)
            mutate(d)
            ev = v.evaluate_judgement(d, ANCHORS, F1)
            self.assertFalse(ev["valid"], tag)
            self.assertTrue(any(tag in r for r in ev["invalid_reasons"]), (tag, ev["invalid_reasons"]))

    def test_non_json_response_is_needs_review(self):
        res, c = self.run_v(["this is not json"])
        self.assertEqual(res["verdict"], "NEEDS_REVIEW")
        self.assertIn("json_parse_error", res["layer2"]["judgements"][0]["invalid_reasons"])

    def test_layer1_fail_x_layer2_pass_is_needs_review(self):
        res, c = self.run_v([make_items(quote="The ruler laughed")], text=F5)
        self.assertEqual(res["layer1"]["verdict"], "FAIL")
        self.assertEqual(res["layer2"]["verdict"], "PASS")
        self.assertEqual(res["verdict"], "NEEDS_REVIEW")
        self.assertTrue(res["stop_required"])

    def test_layer1_fail_x_layer2_fail_is_fail(self):
        p = make_items(overrides=MAJOR_ENDING, quote="The ruler laughed")
        res, c = self.run_v([p, p], text=F5)
        self.assertEqual(res["verdict"], "FAIL")

    def test_sequence_category_is_judged_by_layer2(self):
        p = make_items(overrides={"S1": {"status": "altered", "severity": "major"}})
        res, c = self.run_v([p, p])
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["layer2"]["confirmed_categories"], ["sequence"])

    def test_model_id_mismatch_stops(self):
        c = StubClient([make_items()], model="gpt-5.6-luna")
        with self.assertRaises(v.JudgeModelMismatch):
            v.validate_semantic_preservation(F1, "b1b", client=c, anchors=ANCHORS, source_info=SRC)

    def test_cost_is_per_validation_with_shared_tracker(self):
        tr = v.CostTracker(cap_jpy=8.0)
        c = StubClient([make_items()])
        r1 = v.validate_semantic_preservation(F1, "b1b", client=c, anchors=ANCHORS, source_info=SRC, tracker=tr)
        r2 = v.validate_semantic_preservation(F1, "b1b", client=c, anchors=ANCHORS, source_info=SRC, tracker=tr)
        self.assertAlmostEqual(r1["cost_jpy"], r2["cost_jpy"], places=4)
        self.assertAlmostEqual(tr.total_jpy, r1["cost_jpy"] + r2["cost_jpy"], places=3)
        self.assertEqual(r2["usage_total"]["input_tokens"], 3000)

    def test_budget_stop(self):
        t = v.CostTracker(cap_jpy=0.5, est_per_call_jpy=0.6)
        c = StubClient([make_items()])
        with self.assertRaises(v.JudgeBudgetExceeded):
            v.validate_semantic_preservation(F1, "b1b", client=c, anchors=ANCHORS, source_info=SRC, tracker=t)
        self.assertEqual(len(c.calls), 0)

    def test_result_files_written(self):
        tmp = tempfile.mkdtemp()
        try:
            c = StubClient([make_items()])
            res = v.validate_semantic_preservation(F1, "b1b", client=c, anchors=ANCHORS, source_info=SRC, out_dir=tmp)
            with open(os.path.join(tmp, "validator_result.json"), encoding="utf-8") as f:
                saved = json.load(f)
            for k in ("schema_version", "layer1", "layer2", "verdict", "stop_required", "model", "usage_total",
                      "cost_jpy", "candidate_sha256", "anchors_sha256"):
                self.assertIn(k, saved)
            self.assertEqual(saved["verdict"], res["verdict"])
            with open(os.path.join(tmp, "validator_summary.md"), encoding="utf-8") as f:
                self.assertIn("最終verdict", f.read())
        finally:
            shutil.rmtree(tmp)

    def test_layer1_only_when_no_client(self):
        res = v.validate_semantic_preservation(F1, "b1b", anchors=ANCHORS)
        self.assertIsNone(res["layer2"])
        self.assertEqual(res["verdict"], "PASS")
        res2 = v.validate_semantic_preservation(F5, "b1b", anchors=ANCHORS)
        self.assertEqual(res2["verdict"], "FAIL")


class StdChecksTest(unittest.TestCase):
    def test_identical_text_fails(self):
        r = v.std_vs_adv_checks(F1, F1, ANCHORS)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual(r["identical_sentence_ratio"], 1.0)
        self.assertIn("STD_IDENTICAL_TO_ADV", [f["id"] for f in r["fails"]])

    def test_identical_ratio_threshold_boundary(self):
        adv = "Melos ran fast. The ruler was cruel. His friend waited. The sun set slowly."
        half = "Melos ran fast. The ruler was cruel. A man waited for him. Evening came slowly."
        quarter = "Melos ran fast. A tyrant ruled the land. A man waited for him. Evening came slowly."
        r_half = v.std_vs_adv_checks(adv, half, ANCHORS)
        r_quarter = v.std_vs_adv_checks(adv, quarter, ANCHORS)
        self.assertEqual(r_half["identical_sentence_ratio"], 0.5)
        self.assertEqual(r_half["verdict"], "FAIL")  # >= 50% でFAIL
        self.assertEqual(r_quarter["identical_sentence_ratio"], 0.25)
        self.assertNotIn("STD_IDENTICAL_TO_ADV", [f["id"] for f in r_quarter["fails"]])

    def test_distinct_std_passes_identity_gate(self):
        std = "\n\n".join("Then, " + p for p in v.split_paragraphs(F1))
        r = v.std_vs_adv_checks(F1, std, ANCHORS)
        self.assertLess(r["identical_sentence_ratio"], 0.5)
        self.assertTrue(r["paragraph_count_match"])

    def test_paragraph_count_mismatch_fails(self):
        std = "\n\n".join(v.split_paragraphs(F2)[:-1])
        r = v.std_vs_adv_checks(F2, std + "\n\nExtra.", ANCHORS)  # 同数
        r2 = v.std_vs_adv_checks(F2, std, ANCHORS)
        self.assertTrue(r["paragraph_count_match"])
        self.assertFalse(r2["paragraph_count_match"])
        self.assertIn("STD_PARAGRAPH_COUNT_MISMATCH", [f["id"] for f in r2["fails"]])

    def test_avg_sentence_length_soft_gate_is_warn_not_fail(self):
        adv = "Melos stood before the ruler and spoke.\n\nHis friend waited quietly in the cold prison."
        std = "Melos stood before the ruler and spoke up loudly today.\n\nHis friend waited quietly in the cold prison there."
        r = v.std_vs_adv_checks(adv, std, ANCHORS)
        self.assertIn("STD_AVG_SENTENCE_LEN_NOT_SHORTER", [w["id"] for w in r["warns"]])
        self.assertEqual(r["verdict"], "WARN")

    def test_shorter_sentences_pass_soft_gate(self):
        adv = "Melos stood before the ruler and spoke with a loud and brave voice.\n\nHis friend waited quietly in the cold prison."
        std = "Melos stood before the ruler. He spoke.\n\nHis friend waited. It was cold."
        r = v.std_vs_adv_checks(adv, std, ANCHORS)
        self.assertNotIn("STD_AVG_SENTENCE_LEN_NOT_SHORTER", [w["id"] for w in r["warns"]])

    def test_std_identity_fail_propagates_to_overall(self):
        c = StubClient([make_items()])
        res = v.validate_semantic_preservation(F1, "a2", client=c, anchors=ANCHORS, source_info=SRC, adv_text=F1)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(res["stop_required"])
        self.assertIn("std:STD_IDENTICAL_TO_ADV", res["reasons"])

    def test_std_checks_not_run_for_adv_level(self):
        res = v.validate_semantic_preservation(F1, "b1b", anchors=ANCHORS, adv_text=F1)
        self.assertIsNone(res["std_checks"])


class LocalRewriteTest(unittest.TestCase):
    def test_after_pass_records_diff(self):
        after = F1.replace("Cold and wet, he ran on.", "Cold and tired, he ran on.")
        r = v.revalidate_after_local_rewrite(F1, after, ANCHORS)
        self.assertEqual(r["verdict"], "PASS")
        self.assertFalse(r["stop_required"])
        self.assertEqual(r["diff"]["removed_sentences"], ["Cold and wet, he ran on."])
        self.assertEqual(r["diff"]["added_sentences"], ["Cold and tired, he ran on."])
        self.assertNotEqual(r["diff"]["before_sha256"], r["diff"]["after_sha256"])
        self.assertFalse(r["layer2_performed"])

    def test_rewrite_that_breaks_ending_is_fail_and_regression(self):
        r = v.revalidate_after_local_rewrite(F1, F5, ANCHORS)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertTrue(r["stop_required"])
        self.assertTrue(r["regressed_to_fail"])

    def test_identical_rewrite(self):
        r = v.revalidate_after_local_rewrite(F1, F1, ANCHORS)
        self.assertTrue(r["diff"]["identical"])


class CompatWrapperTest(unittest.TestCase):
    def test_check_wrapper_warns_and_delegates(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ok, ids = v.check_character_name_rule(F3)
            ok_bad, ids_bad = v.check_character_name_rule(F5)
        self.assertTrue(any(issubclass(x.category, DeprecationWarning) for x in w))
        self.assertTrue(ok)  # 名前が無くてもPASS(旧仕様なら'Selinuntius','Dionysius'欠落でFAIL)
        self.assertEqual(ids, [])
        self.assertFalse(ok_bad)
        self.assertTrue(any(i.startswith("FORBIDDEN_ENDING") for i in ids_bad))

    def test_restore_wrapper_warns_and_does_not_edit(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            out = v.restore_character_names(F1)
        self.assertTrue(any(issubclass(x.category, DeprecationWarning) for x in w))
        self.assertEqual(out, F1)

    def test_legacy_er026_functions_still_exist_untouched(self):
        import er026_family_z_fiction_production_runner_01 as old
        self.assertTrue(callable(old.check_character_name_rule))
        self.assertTrue(callable(old.restore_character_names))
        # 旧仕様(名前必須)の挙動は残置されている=er026側は未編集
        self.assertFalse(old.check_character_name_rule(F3)[0])


class FixtureManifestTest(unittest.TestCase):
    def test_manifest_shas_match_and_coverage(self):
        with open(os.path.join(FIX, "fixtures_manifest.json"), encoding="utf-8") as f:
            m = json.load(f)
        ids = [x["id"] for x in m["fixtures"]]
        for need in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"):
            self.assertIn(need, ids)
        for x in m["fixtures"]:
            self.assertEqual(v.sha256_file(os.path.join(FIX, x["file"])), x["sha256"], x["id"])
            if x["id"] in ("F4", "F5", "F5b", "F6", "F7", "F8"):
                self.assertIn("原作逸脱", x["description"])
        exp = {x["id"]: x["expected_categories"] for x in m["fixtures"]}
        self.assertIn("role_relation", exp["F4"])
        self.assertEqual(exp["F5"], ["ending"])
        self.assertEqual(exp["F6"], ["causality"])

    def test_f3_has_no_foreign_names_and_f1_f2_sources_unchanged(self):
        self.assertNotIn("Dionysius", F3)
        self.assertNotIn("Selinuntius", F3)
        self.assertEqual(v.sha256_file("er059_output/melos_sol_b3z_trial_01/m2_sol_only/r2.md"),
                         v.sha256_file(os.path.join(FIX, "F1_trial2_r2_normal.md")))


class CalibrationArtifactTest(unittest.TestCase):
    """実呼出calibrationの結果ファイルの整合(結果ファイルが存在する場合のみ)。"""

    @unittest.skipUnless(os.path.exists(v.CALIBRATION_PATH), "calibration未実行")
    def test_calibration_all_ok_and_within_budget(self):
        with open(v.CALIBRATION_PATH, encoding="utf-8") as f:
            c = json.load(f)
        self.assertLessEqual(c["cost"]["total_jpy"], v.CALIBRATION_CAP_JPY)
        self.assertEqual(c["requested_model"], "gpt-6-luna")
        self.assertEqual(c["anchors_sha256"], v.load_anchors()["sha256_self"])
        self.assertIsNone(c["stopped"])
        self.assertTrue(c["all_ok"], [(r["fixture"], r["final_verdict"], r["layer2_fail_categories"])
                                      for r in c["rows"] if not r["calibration_ok"]])


if __name__ == "__main__":
    unittest.main()
