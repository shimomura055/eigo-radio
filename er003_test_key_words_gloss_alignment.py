# KP-GLOSS-ALIGNMENT-01 テスト(API不要、mock)
import json
import os
import tempfile
import unittest

import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga


def _explicit_on(cls):
    """2026-10-15 既定OFF化(KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_02): 既存testは『明示ON』経路を検証するため、
    各testでモジュールflagを明示的にONにする(終了時に元へ戻す)。既定OFFそのものはDefaultOffIsolation classで検証する。"""
    orig = cls.setUp if "setUp" in cls.__dict__ else None

    def setUp(self):
        old = ga.GLOSS_ALIGNMENT_ENABLED
        ga.GLOSS_ALIGNMENT_ENABLED = True
        self.addCleanup(setattr, ga, "GLOSS_ALIGNMENT_ENABLED", old)
        if orig is not None:
            orig(self)
    cls.setUp = setUp
    return cls


def _merged(items):
    return {"items": items, "overall_status": "PASS"}


def _item(rank, disp, kp, gloss, beyond=False, sentence="x"):
    return {"rank": rank, "display_phrase": disp, "key_phrase": kp, "used_form": kp, "japanese_gloss": gloss,
            "japanese_gloss_tts": kc.convert_display_gloss_to_tts_text(gloss),
            "kp_extends_beyond_candidate": beyond, "gloss_review_hint": beyond,
            "changed_from_display_phrase": disp != kp, "source_sentence": sentence}


class FakeFn:
    def __init__(self, payloads, model="gpt-6-luna"):
        self.payloads = list(payloads)
        self.calls = 0
        self.model = model

    def __call__(self):
        self.calls += 1
        p = self.payloads.pop(0)
        if isinstance(p, Exception):
            raise p
        return (p if isinstance(p, str) else json.dumps(p, ensure_ascii=False)), self.model, "resp_x"


def _resp(items):
    return {"items": [{"rank": r, "current_gloss_consistent": c, "japanese_gloss": g,
                       "qa_reflects_all_key_phrase_words": q, "reasoning": "r"} for r, c, g, q in items]}


@_explicit_on
class TargetSelection(unittest.TestCase):
    def test_extended_kp_is_target(self):
        self.assertTrue(ga.kp_adds_words_beyond_display("based on", "based on interviews"))

    def test_unchanged_not_target(self):
        self.assertFalse(ga.kp_adds_words_beyond_display("right away", "right away"))

    def test_inflection_not_target(self):
        self.assertFalse(ga.kp_adds_words_beyond_display("give back", "gave back"))

    def test_person_generalization_not_target(self):
        self.assertFalse(ga.kp_adds_words_beyond_display("catch their breath", "catch one's breath"))
        self.assertFalse(ga.kp_adds_words_beyond_display("give my word", "give one's word"))

    def test_article_removal_not_target(self):
        self.assertFalse(ga.kp_adds_words_beyond_display("the Strait", "Strait"))

    def test_flag_makes_target(self):
        m = _merged([_item(1, "x y", "x y", "g", beyond=True)])
        self.assertEqual(len(ga.select_alignment_targets(m["items"])), 1)

    def test_no_targets_no_api(self):
        m = _merged([_item(1, "right away", "right away", "すぐに")])
        called = []
        r = ga.align_glosses(m, "art", lambda msg: called.append(1))
        self.assertEqual(r["status"], "NO_TARGETS")
        self.assertIs(r["merged"], m)
        self.assertFalse(called)


@_explicit_on
class Alignment(unittest.TestCase):
    def setUp(self):
        self.m = _merged([_item(1, "right away", "right away", "すぐに"),
                          _item(2, "based on", "based on interviews", "～をもとにした", beyond=True)])

    def test_realign(self):
        fn = FakeFn([_resp([(2, False, "インタビューをもとにした", "PASS")])])
        r = ga.align_glosses(self.m, "art", lambda msg: fn)
        it = r["merged"]["items"][1]
        self.assertEqual(r["status"], "ALIGN_PASS")
        self.assertEqual(it["japanese_gloss"], "インタビューをもとにした")
        self.assertEqual(it["japanese_gloss_tts"], "インタビューをもとにした")
        self.assertEqual(it["gloss_alignment"]["status"], "GLOSS_REALIGNED")
        self.assertEqual(it["gloss_alignment"]["original_japanese_gloss"], "～をもとにした")
        self.assertEqual(it["key_phrase"], "based on interviews")
        # 対象外itemは無変更
        self.assertEqual(r["merged"]["items"][0], self.m["items"][0])
        # 元mergedは変更しない
        self.assertEqual(self.m["items"][1]["japanese_gloss"], "～をもとにした")
        self.assertEqual(fn.calls, 1)

    def test_already_consistent(self):
        m = _merged([_item(2, "based on", "based on interviews", "インタビューをもとにした", beyond=True)])
        fn = FakeFn([_resp([(2, True, "インタビューをもとにした", "PASS")])])
        r = ga.align_glosses(m, "art", lambda msg: fn)
        self.assertEqual(r["merged"]["items"][0]["gloss_alignment"]["status"], "GLOSS_ALREADY_CONSISTENT")

    def test_retry_then_pass(self):
        fn = FakeFn([_resp([(2, False, "インタビュー（取材）をもとにした", "PASS")]),
                     _resp([(2, False, "インタビューをもとにした", "PASS")])])
        r = ga.align_glosses(self.m, "art", lambda msg: fn)
        self.assertEqual(fn.calls, 2)
        self.assertEqual(r["status"], "ALIGN_PASS")
        self.assertEqual(r["merged"]["items"][1]["japanese_gloss"], "インタビューをもとにした")

    def test_fallback_default_keeps_kp_and_marks_failed(self):
        """OF-227/228: 既定(ii)=最終KP維持+FAILED記録+通知。KPは戻さない。"""
        fn = FakeFn([_resp([(2, False, "x", "FAIL")]), RuntimeError("boom")])
        r = ga.align_glosses(self.m, "art", lambda msg: fn, article_id="ART1")
        self.assertEqual(fn.calls, ga.MAX_GLOSS_ALIGNMENT_ATTEMPTS)
        self.assertEqual(r["status"], "ALIGN_FAILED")
        it = r["merged"]["items"][1]
        self.assertEqual(it["key_phrase"], "based on interviews")
        self.assertEqual(it["japanese_gloss"], "～をもとにした")
        self.assertTrue(it["gloss_review_hint"])
        self.assertEqual(it["gloss_alignment_status"], "FAILED")
        self.assertEqual(it["gloss_alignment"]["status"], "GLOSS_ALIGNMENT_FAILED_KP_KEPT")
        self.assertEqual(r["merged"]["gloss_alignment_failed"][0]["rank"], 2)
        ev = r["fallback_event"]
        self.assertEqual(ev["reason_code"], "GLOSS_ALIGNMENT_FAILED")
        self.assertEqual(ev["article"], "ART1")
        # 対象外itemは無変更
        self.assertEqual(r["merged"]["items"][0], self.m["items"][0])

    def test_fallback_revert_mode_reverts_when_safe_and_invalidates_qa(self):
        m = _merged([dict(_item(2, "right away", "right away now", "すぐに今", beyond=True),
                          source_span="do it right away now", normalization_reason="restore_semantic_complement",
                          reasoning="r", qa={"a": "PASS"}, qa_overall_status="PASS", canonicalization_source_span="zzz")])
        fn = FakeFn([_resp([(2, False, "x", "FAIL")]), _resp([(2, False, "x", "FAIL")])])
        r = ga.align_glosses(m, "art", lambda msg: fn, fallback_mode=ga.FALLBACK_REVERT_IF_SAFE)
        it = r["merged"]["items"][0]
        self.assertEqual(it["key_phrase"], "right away")
        self.assertEqual(it["used_form"], "right away")
        self.assertEqual(it["normalization_reason"], "none")
        self.assertEqual(it["qa"], {"a": "INVALIDATED_BY_GLOSS_REVERT"})
        self.assertNotIn("canonicalization_source_span", it)
        self.assertTrue(it["gloss_review_hint"])
        self.assertEqual(it["gloss_alignment_status"], "FAILED")
        self.assertEqual(it["gloss_alignment"]["status"], "FALLBACK_KP_REVERTED_TO_DISPLAY_PHRASE")

    def test_fallback_revert_mode_blocked_by_dangling_tail_and_span(self):
        ok, why = ga.revert_to_candidate_allowed({"display_phrase": "based on", "source_span": "based on interviews"})
        self.assertFalse(ok)
        self.assertIn("末尾機能語", why)
        ok, why = ga.revert_to_candidate_allowed({"display_phrase": "take a player off", "source_span": "took off players"})
        self.assertFalse(ok)
        ok, why = ga.revert_to_candidate_allowed({"display_phrase": "right away", "source_span": "do it right away now"})
        self.assertTrue(ok)
        # revertモードでも不可のitemは(ii)で処理(KP維持)
        fn = FakeFn([_resp([(2, False, "x", "FAIL")]), _resp([(2, False, "x", "FAIL")])])
        r = ga.align_glosses(self.m, "art", lambda msg: fn, fallback_mode=ga.FALLBACK_REVERT_IF_SAFE)
        it = r["merged"]["items"][1]
        self.assertEqual(it["key_phrase"], "based on interviews")
        self.assertEqual(it["gloss_alignment"]["status"], "GLOSS_ALIGNMENT_FAILED_KP_KEPT")

    def test_flag_off_no_api_no_change(self):
        fn = FakeFn([])
        r = ga.align_glosses(self.m, "art", lambda msg: fn, enabled=False)
        self.assertEqual(r["status"], "DISABLED")
        self.assertIs(r["merged"], self.m)
        self.assertEqual(fn.calls, 0)

    def test_default_mode_keep(self):
        self.assertEqual(ga.GLOSS_ALIGNMENT_FALLBACK_MODE, ga.FALLBACK_KEEP_KP)

    def test_usage_cost_recorded_in_attempts(self):
        class U(FakeFn):
            def __call__(self):
                self.last_usage = {"input_tokens": 1000, "output_tokens": 500, "cached_input_tokens": 0}
                return super().__call__()
        fn = U([_resp([(2, False, "インタビューをもとにした", "PASS")])])
        r = ga.align_glosses(self.m, "art", lambda msg: fn)
        self.assertEqual(r["attempts"][0]["usage"]["input_tokens"], 1000)
        self.assertIsNotNone(r["attempts"][0]["cost_jpy"])
        self.assertEqual(r["cost_jpy"], r["attempts"][0]["cost_jpy"])

    def test_rank_mismatch_invalid(self):
        fn = FakeFn([_resp([(9, False, "a", "PASS")]), _resp([(9, False, "a", "PASS")])])
        r = ga.align_glosses(self.m, "art", lambda msg: fn)
        self.assertEqual(r["status"], "ALIGN_FAILED")

    def test_digit_and_paren_rejected(self):
        for bad in ("2つの", "インタビュー(取材)をもとにした", "インタビュー…をもとにした"):
            v = ga.validate_alignment_response(_resp([(2, False, bad, "PASS")]), [self.m["items"][1]])
            self.assertFalse(v["ok"], bad)

    def test_slot_tilde_allowed_only_when_kp_has_slot_word(self):
        t = [_item(2, "take someone's", "take someone's place", "～の代わりをする", beyond=True)]
        v = ga.validate_alignment_response(_resp([(2, False, "～の代わりをする", "PASS")]), t)
        self.assertTrue(v["ok"], v["reasons"])
        # KPにスロット語なし -> 「～」が残ればFAIL(LLMがPASSを自己申告しても)
        v = ga.validate_alignment_response(_resp([(2, False, "～をもとにした", "PASS")]), [self.m["items"][1]])
        self.assertFalse(v["ok"])
        self.assertTrue(any("スロット" in r for r in v["reasons"]))
        for ch in ("〜", "~"):
            self.assertTrue(ga.gloss_has_unjustified_slot("based on interviews", ch + "をもとにした"))
        self.assertFalse(ga.gloss_has_unjustified_slot("based on interviews", "インタビューをもとにした"))
        self.assertFalse(ga.gloss_has_unjustified_slot("pull oneself together", "～を落ち着かせる"))

    def test_already_consistent_with_stale_slot_gloss_is_rejected(self):
        """OF-230(b): GLOSS_ALREADY_CONSISTENT申告でも旧glossがスロット付き(KPにスロット語なし)ならFAIL->retry->fallback。"""
        fn = FakeFn([_resp([(2, True, "～をもとにした", "PASS")]), _resp([(2, True, "～をもとにした", "PASS")])])
        r = ga.align_glosses(self.m, "art", lambda msg: fn)
        self.assertEqual(r["status"], "ALIGN_FAILED")
        self.assertEqual(fn.calls, 2)

    def test_writes_audit_files(self):
        fn = FakeFn([_resp([(2, False, "インタビューをもとにした", "PASS")])])
        with tempfile.TemporaryDirectory() as d:
            ga.align_glosses(self.m, "art", lambda msg: fn, out_dir=d, article_id="A")
            meta = json.load(open(os.path.join(d, "gloss_alignment_runtime_metadata.json"), encoding="utf-8"))
            self.assertEqual(meta["final_status"], "ALIGN_PASS")
            self.assertTrue(os.path.exists(os.path.join(d, "gloss_alignment_prompt.txt")))


class PromptReuse(unittest.TestCase):
    def test_rules_extracted_from_approved_template(self):
        rules = ga.load_approved_gloss_rules()
        self.assertIn("括弧", rules)
        self.assertIn("漢数字", rules)
        msg = ga.build_user_message([_item(2, "based on", "based on interviews", "～をもとにした", True)], "ART")
        self.assertIn(rules, msg)
        self.assertIn("based on interviews", msg)

    def test_model_required(self):
        with self.assertRaises(ValueError):
            ga.make_alignment_fn("m", client=object())

    def test_model_mismatch_raises(self):
        class R:
            model = "other"; output_text = "{}"; id = "i"

        class C:
            class responses:
                @staticmethod
                def create(**k): return R()
        fn = ga.make_alignment_fn("m", client=C(), model="gpt-6-luna")
        with self.assertRaises(ga.GlossAlignmentModelMismatchError):
            fn()


class ScaffoldWiring(unittest.TestCase):
    def test_scaffold_calls_alignment_in_canonicalization_path(self):
        import inspect
        import er003_v1_n3_01_scaffold_generate as sc
        src = inspect.getsource(sc.run_key_phrase_canonicalization)
        self.assertIn("gloss_align.align_glosses", src)


@_explicit_on
class ScaffoldIntegration(unittest.TestCase):
    """sc.run_key_phrase_canonicalization(Production関数)を通して、gloss再整合が初回経路で効く/対象0件ならAPI呼出なし。"""

    def _run(self, kp_for_rank4, fake):
        import unittest.mock as mock
        import er003_v1_n3_01_scaffold_generate as sc
        originals = [
            {"rank": 1, "display_phrase": "right away", "source_span": "right away", "source_sentence": "Do it right away.",
             "ja_gloss": "すぐに", "source_reference_contract": "X"},
            {"rank": 2, "display_phrase": "based on", "source_span": "based on",
             "source_sentence": "It is an estimate based on interviews with sellers.", "ja_gloss": "～をもとにした",
             "source_reference_contract": "X"},
        ]
        qa = {f: "PASS" for f in kc.QA_FIELDS}
        parsed = {"items": [
            {"rank": 1, "key_phrase": "right away", "changed_from_display_phrase": False, "normalization_reason": "none",
             "reasoning": "r", **qa},
            {"rank": 2, "key_phrase": kp_for_rank4, "changed_from_display_phrase": kp_for_rank4 != "based on",
             "normalization_reason": "restore_semantic_complement" if kp_for_rank4 != "based on" else "none",
             "reasoning": "r", **qa},
        ]}
        with tempfile.TemporaryDirectory() as d,                 mock.patch.object(sc.kc, "run_canonicalization_gate",
                                  return_value=(parsed, "CANONICALIZATION_PASS", [], "gpt-6-luna", "resp")),                 mock.patch.object(sc.gloss_align, "make_alignment_fn", return_value=fake):
            res = sc.run_key_phrase_canonicalization("ART", originals, d, "A", process="A2_SUPPORT")
            saved = json.load(open(os.path.join(d, "keywords_canonicalized.json"), encoding="utf-8"))
        return res, saved

    def test_extended_kp_gets_realigned_gloss_in_saved_record(self):
        fake = FakeFn([_resp([(2, False, "インタビューをもとにした", "PASS")])])
        res, saved = self._run("based on interviews", fake)
        it = saved["items"][1]
        self.assertEqual(res["gloss_alignment_status"], "ALIGN_PASS")
        self.assertEqual(it["key_phrase"], "based on interviews")
        self.assertEqual(it["japanese_gloss"], "インタビューをもとにした")
        self.assertEqual(it["japanese_gloss_tts"], "インタビューをもとにした")
        self.assertEqual(saved["items"][0]["japanese_gloss"], "すぐに")

    def test_unextended_kp_makes_no_api_call(self):
        fake = FakeFn([])
        res, saved = self._run("based on", fake)
        self.assertEqual(res["gloss_alignment_status"], "NO_TARGETS")
        self.assertEqual(fake.calls, 0)
        self.assertEqual(saved["items"][1]["japanese_gloss"], "～をもとにした")

    def test_failed_alignment_keeps_kp_flags_failed_not_human_review(self):
        fake = FakeFn([_resp([(2, False, "x", "FAIL")]), _resp([(2, False, "x", "FAIL")])])
        res, saved = self._run("based on interviews", fake)
        self.assertEqual(res["status"], "CANONICALIZATION_PASS")
        self.assertEqual(saved["items"][1]["key_phrase"], "based on interviews")
        self.assertEqual(saved["items"][1]["japanese_gloss"], "～をもとにした")
        self.assertEqual(saved["items"][1]["gloss_alignment_status"], "FAILED")
        self.assertTrue(saved["items"][1]["gloss_review_hint"])
        self.assertEqual(res["gloss_alignment_status"], "ALIGN_FAILED")
        self.assertEqual(res["gloss_alignment_fallback"]["reason_code"], "GLOSS_ALIGNMENT_FAILED")


@_explicit_on
class RulesExtraction(unittest.TestCase):
    EXPECTED_SHA256 = "447e07cb8b9a30850a8dc75b6c3cce48c53d99b5f1fafa88d19b778d9155949b"

    def test_sha256_pinned(self):
        """承認済みテンプレートの該当段落が変わったら検知する(OF-229)。"""
        self.assertEqual(ga.rules_sha256(ga.load_approved_gloss_rules()), self.EXPECTED_SHA256)

    def test_selection_instruction_paragraph_included(self):
        self.assertIn("短く自然な日本語グロス", ga.load_approved_gloss_rules())

    def test_extraction_failure_raises_immediately(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.txt")
            open(p, "w", encoding="utf-8").write("日本語グロスは1。\n\n日本語グロスは2。\n\n日本語グロスは3。\n")
            with self.assertRaises(ga.GlossRulesExtractionError):
                ga.load_approved_gloss_rules(p)
            open(p, "w", encoding="utf-8").write("短く自然な日本語グロスを付ける。\n\n日本語グロスは1。\n")
            with self.assertRaises(ga.GlossRulesExtractionError):
                ga.load_approved_gloss_rules(p)

    def test_preflight_caches_and_noop_when_disabled(self):
        self.assertIsNone(ga.preflight(False))
        a = ga.preflight(True)
        self.assertEqual(a["sha256"], self.EXPECTED_SHA256)
        self.assertIs(ga.preflight(True), a)

    def test_metadata_records_sha256(self):
        m = _merged([_item(2, "based on", "based on interviews", "～をもとにした", beyond=True)])
        fn = FakeFn([_resp([(2, False, "インタビューをもとにした", "PASS")])])
        with tempfile.TemporaryDirectory() as d:
            ga.align_glosses(m, "art", lambda msg: fn, out_dir=d, article_id="A")
            meta = json.load(open(os.path.join(d, "gloss_alignment_runtime_metadata.json"), encoding="utf-8"))
        self.assertEqual(meta["rules_sha256"], self.EXPECTED_SHA256)


class NoticeFiles(unittest.TestCase):
    def test_notice_written_and_stdout(self):
        ev = ga.build_gloss_alignment_fallback_record(
            "ART", [{"rank": 2, "key_phrase": "k", "japanese_gloss": "g", "action": "a"}], "m")
        with tempfile.TemporaryDirectory() as d:
            p = ga.write_failed_notice(d, [ev])
            self.assertTrue(os.path.exists(p))
            self.assertIsNone(ga.write_failed_notice(d, []))
        self.assertIn("ユーザーへ必ず報告", ga.format_failed_stdout([ev]))


# ============================================================
# 委任_02 (KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01): mode="corrected"(Trial専用)のunit test(API不要、mock)
# legacy(既定)のtestは上で無変更。ここでは「～」条件撤回・追加内容語span対応(record-only/gate)・item単位retry・
# HR状態の永続化・HR報告書(再読検証/fail-closed)・resolve_gloss・mode分離を決定論で検証する(O3)。
# ============================================================
def _cresp(items):
    """items: [(rank, consistent, gloss, mappings[(en, ja)], qa)]"""
    return {"items": [{"rank": r, "current_gloss_consistent": c, "japanese_gloss": g,
                       "added_word_mappings": [{"english_word": e, "japanese_span": j} for e, j in mp],
                       "qa_reflects_all_key_phrase_words": q, "reasoning": "r"} for r, c, g, mp, q in items]}


def _t(rank, disp, kp, gloss, sentence="x"):
    return _item(rank, disp, kp, gloss, beyond=True, sentence=sentence)


def _factory(payloads):
    fn = FakeFn(payloads)
    msgs = []

    def make(msg):
        msgs.append(msg)
        return fn
    return fn, make, msgs


@_explicit_on
class ModeSeparation(unittest.TestCase):
    def test_default_mode_is_legacy_and_env_not_used(self):
        self.assertEqual(ga.GLOSS_ALIGNMENT_MODE, "legacy")
        self.assertEqual(ga.resolve_mode(None), "legacy")
        self.assertEqual(ga.resolve_mode("corrected"), "corrected")
        with self.assertRaises(ValueError):
            ga.resolve_mode("CORRECTED")

    def test_default_align_glosses_is_legacy_behavior(self):
        m = _merged([_t(2, "based on", "based on interviews", "～をもとにした")])
        fn = FakeFn([_resp([(2, False, "x", "FAIL")]), _resp([(2, False, "x", "FAIL")])])
        r = ga.align_glosses(m, "art", lambda msg: fn)       # mode未指定=legacy: 従来のFAILED(素通り)形が出る
        it = r["merged"]["items"][0]
        self.assertEqual(it["gloss_alignment_status"], "FAILED")
        self.assertIsNotNone(r["fallback_event"])
        self.assertEqual(ga.collect_unresolved(r["merged"]), [])   # legacy FAILEDは新関所の対象ではない(挙動不変)

    def test_production_runners_do_not_pass_mode(self):
        import inspect
        import er019_family_x_audio_production_runner_01 as x
        src = inspect.getsource(x.run_theme_scaffold)
        self.assertIn('*, gloss_alignment_mode: str = "legacy"', src)
        self.assertIn('if gloss_alignment_mode == "legacy" else', src)   # legacyでは従来のcall形
        import er026_family_z_fiction_production_runner_01 as z
        self.assertEqual(z.E2EContext().gloss_alignment_mode, "legacy")

    def test_evidence_scripts_still_resolve_legacy_symbols(self):
        """証跡スクリプト(replay/census/offline_audit)が参照するlegacy記号が残っている(import破綻なし)。"""
        import re as _re
        names = set()
        for f in ("er071_gloss_alignment_01_replay.py", "er071_gloss_alignment_01_census.py",
                  "er071_gloss_alignment_correction_01_offline_audit.py"):
            names |= set(_re.findall(r"\bga\.([A-Za-z_][A-Za-z0-9_]*)", open(f, encoding="utf-8").read()))
        self.assertTrue(names)
        for n in names:
            self.assertTrue(hasattr(ga, n), n)


class AddedWordsAndMappings(unittest.TestCase):
    def test_added_content_words_exclude_function_words(self):
        self.assertEqual(ga.added_content_words("based on", "based on interviews"), ["interviews"])
        self.assertEqual(ga.added_content_words("close", "close around me"), ["me"])      # around=前置詞/不変化詞は対象外
        self.assertEqual(ga.added_content_words("narrow", "locked into a narrow view")[-1], "view")
        self.assertEqual(ga.added_content_words("right away", "right away"), [])
        # legacyの判定関数は不変(関数抽出のみ)
        self.assertTrue(ga.kp_adds_words_beyond_display("based on", "based on interviews"))

    def test_mapping_pass_and_fail_types(self):
        ok = ga.check_added_word_mappings(["interviews"], [{"english_word": "interviews", "japanese_span": "インタビュー"}],
                                          "インタビューをもとにした")
        self.assertTrue(ok["pass"])
        # span不実在(幻覚)
        bad = ga.check_added_word_mappings(["interviews"], [{"english_word": "interviews", "japanese_span": "取材"}],
                                           "インタビューをもとにした")
        self.assertFalse(bad["pass"])
        self.assertEqual(bad["span_not_in_gloss"], ["取材"])
        # 記号のみ
        sym = ga.check_added_word_mappings(["interviews"], [{"english_word": "interviews", "japanese_span": "～"}],
                                           "～をもとにした")
        self.assertFalse(sym["pass"])
        self.assertEqual(sym["symbol_only_spans"], ["～"])
        # 対応欠落
        miss = ga.check_added_word_mappings(["interviews"], [], "～をもとにした")
        self.assertEqual(miss["uncovered"], ["interviews"])

    def test_many_to_one_phrase_and_stem_and_nfkc(self):
        r = ga.check_added_word_mappings(
            ["raw", "bean"], [{"english_word": "raw-bean", "japanese_span": "生 豆"}], "生豆の値段")     # 句・多対一・空白除去
        self.assertTrue(r["pass"], r)
        r = ga.check_added_word_mappings(["prices"], [{"english_word": "price", "japanese_span": "値段"}], "値段が上がる")
        self.assertTrue(r["pass"])                                                                  # 語幹一致
        r = ga.check_added_word_mappings(["x"], [{"english_word": "x", "japanese_span": "ＡＢＣ"}], "ABC を示す")
        self.assertTrue(r["pass"])                                                                  # NFKC(全角->半角)+空白除去
        # 同じspanを複数語へ対応(重複可)
        r = ga.check_added_word_mappings(["human", "helper"],
                                        [{"english_word": "human", "japanese_span": "人の手"},
                                         {"english_word": "helper", "japanese_span": "人の手"}], "人の手を借りる")
        self.assertTrue(r["pass"])

    def test_no_required_words_is_not_checked(self):
        r = ga.check_added_word_mappings([], [], "～を示す")
        self.assertTrue(r["pass"])
        self.assertIn("note", r)


class ItemValidationCorrected(unittest.TestCase):
    def test_dictionary_tilde_is_not_a_failure(self):
        """方針A: 『～』の有無は合否に使わない。based on+『～をもとにした』(追加語なし)は一致=合格。"""
        t = _t(1, "based on", "based on", "～をもとにした")
        v = ga.validate_item_corrected(_cresp([(1, True, "～をもとにした", [], "PASS")])["items"][0], t)
        self.assertTrue(v["valid"], v["reasons"])
        self.assertEqual(v["adopt_gloss"], "～をもとにした")

    def test_tilde_with_missing_object_is_judged_by_meaning_not_symbol(self):
        """based on interviews+『～をもとにした』: LLMが不一致と判定し『インタビューをもとにした』を返せば合格。"""
        t = _t(2, "based on", "based on interviews", "～をもとにした")
        v = ga.validate_item_corrected(
            _cresp([(2, False, "インタビューをもとにした", [("interviews", "インタビュー")], "PASS")])["items"][0], t)
        self.assertTrue(v["valid"], v["reasons"])
        self.assertTrue(v["machine_check"]["pass"])

    def test_tilde_remaining_in_new_gloss_is_not_rejected_by_symbol(self):
        """『～』が残っていても、LLM判定PASSで(record-onlyの)mapping対応があれば合格。逆にmapping欠落は記録される。"""
        t = _t(2, "based on", "based on interviews", "x")
        v = ga.validate_item_corrected(
            _cresp([(2, False, "～をもとにした", [], "PASS")])["items"][0], t)
        self.assertTrue(v["valid"])                         # record-only: LLM判定を合否とする
        self.assertFalse(v["machine_check"]["pass"])        # ただしgate判定の記録は不合格(並記)
        self.assertEqual(v["machine_check"]["uncovered"], ["interviews"])

    def test_mapping_gate_makes_uncovered_invalid(self):
        t = _t(2, "based on", "based on interviews", "x")
        v = ga.validate_item_corrected(_cresp([(2, False, "～をもとにした", [], "PASS")])["items"][0], t, mapping_gate=True)
        self.assertFalse(v["valid"])
        self.assertTrue(any("mapping gate" in r for r in v["reasons"]))

    def test_true_must_keep_current_and_false_must_change(self):
        t = _t(2, "based on", "based on interviews", "インタビューをもとにした")
        v = ga.validate_item_corrected(_cresp([(2, True, "インタビューを元にした", [], "PASS")])["items"][0], t)
        self.assertFalse(v["valid"])                         # 真なのに別gloss(矛盾)
        v = ga.validate_item_corrected(_cresp([(2, False, "インタビューをもとにした", [], "PASS")])["items"][0], t)
        self.assertFalse(v["valid"])                         # 偽なのに不変(矛盾)

    def test_true_comparison_normalizes_only_space_and_tilde_and_adopts_original(self):
        t = _t(2, "take", "take someone's place", "～ の 代わり を する")
        v = ga.validate_item_corrected(_cresp([(2, True, "〜の代わりをする", [], "PASS")])["items"][0], t)
        self.assertTrue(v["valid"], v["reasons"])
        self.assertEqual(v["adopt_gloss"], "～ の 代わり を する")   # 採用値は常にcurrent原文

    def test_forbidden_symbols_and_qa_fail_still_rejected(self):
        t = _t(2, "based on", "based on interviews", "x")
        for g in ("2つの", "インタビュー(取材)をもとにした", "インタビュー…をもとにした"):
            v = ga.validate_item_corrected(_cresp([(2, False, g, [], "PASS")])["items"][0], t)
            self.assertFalse(v["valid"], g)
        v = ga.validate_item_corrected(_cresp([(2, False, "インタビューをもとにした", [], "FAIL")])["items"][0], t)
        self.assertFalse(v["valid"])
        self.assertFalse(ga.validate_item_corrected(None, t)["valid"])


class ItemLevelRetryAndFailure(unittest.TestCase):
    def setUp(self):
        self.m = _merged([_item(1, "right away", "right away", "すぐに"),
                          _t(2, "based on", "based on interviews", "～をもとにした"),
                          _t(3, "raw beans", "raw-bean prices", "焙煎前の豆")])

    def test_partial_success_then_retry_only_unresolved_and_first_valid_adopted(self):
        fn, make, msgs = _factory([
            _cresp([(2, False, "インタビューをもとにした", [("interviews", "インタビュー")], "PASS"),
                    (3, False, "x", [], "FAIL")]),
            _cresp([(3, False, "生豆の値段", [("raw-bean", "生豆"), ("prices", "値段")], "PASS")]),
        ])
        r = ga.align_glosses(self.m, "art", make, mode="corrected", enabled=True)
        self.assertEqual(fn.calls, 2)
        self.assertEqual(r["status"], "ALIGN_PASS")
        self.assertIn('"rank": 2', msgs[0])
        self.assertNotIn('"rank": 2', msgs[1])           # 2回目は未解決itemのみで再構築(OF-KGDC-09)
        self.assertIn('"rank": 3', msgs[1])
        items = r["merged"]["items"]
        self.assertEqual(items[1]["japanese_gloss"], "インタビューをもとにした")
        self.assertEqual(items[2]["japanese_gloss"], "生豆の値段")
        self.assertEqual(items[0], self.m["items"][0])    # 対象外itemは無変更
        self.assertEqual(items[1]["gloss_alignment_status"], "ALIGNED")
        self.assertEqual(ga.collect_unresolved(r["merged"]), [])

    def test_two_failures_mark_item_hr_required_and_keep_kp_and_gloss(self):
        bad = _cresp([(2, False, "x", [], "FAIL"), (3, False, "生豆の値段", [("raw-bean", "生豆"), ("prices", "値段")], "PASS")])
        fn, make, msgs = _factory([bad, _cresp([(2, False, "y", [], "FAIL")])])
        r = ga.align_glosses(self.m, "art", make, mode="corrected", enabled=True, article_id="A")
        self.assertEqual(r["status"], "ALIGN_PARTIAL_HUMAN_REVIEW_REQUIRED")
        self.assertEqual(fn.calls, 2)
        it2, it3 = r["merged"]["items"][1], r["merged"]["items"][2]
        self.assertEqual(it2["gloss_alignment_status"], ga.STATUS_HR_REQUIRED)
        self.assertEqual(it2["key_phrase"], "based on interviews")          # KPを短い候補へ戻さない
        self.assertEqual(it2["japanese_gloss"], "～をもとにした")             # 旧glossを維持(参考)
        self.assertTrue(it2["gloss_review_hint"])
        self.assertEqual(len(it2["gloss_alignment"]["failure"]["attempts"]), 2)
        self.assertEqual(it3["gloss_alignment_status"], "ALIGNED")           # 独立itemは成立分を採用(不必要に止めない)
        self.assertEqual([x["rank"] for x in ga.collect_unresolved(r["merged"])], [2])
        self.assertEqual(r["merged"]["gloss_alignment_unresolved"][0]["rank"], 2)

    def test_technical_and_parse_failures_consume_attempts_and_end_in_hr(self):
        fn, make, msgs = _factory([RuntimeError("boom"), "not json"])
        r = ga.align_glosses(self.m, "art", make, mode="corrected", enabled=True)
        self.assertEqual(fn.calls, 2)
        self.assertEqual(r["status"], "ALIGN_FAILED_HUMAN_REVIEW_REQUIRED")
        self.assertEqual(sorted(x["rank"] for x in ga.collect_unresolved(r["merged"])), [2, 3])
        self.assertEqual([a["verdict"] for a in r["merged"]["items"][1]["gloss_alignment"]["failure"]["attempts"]],
                         ["TECHNICAL_FAILED", "PARSE_FAILED"])

    def test_no_targets_and_disabled_make_no_api_call(self):
        m = _merged([_item(1, "right away", "right away", "すぐに")])
        calls = []
        r = ga.align_glosses(m, "art", lambda msg: calls.append(1), mode="corrected", enabled=True)
        self.assertEqual(r["status"], "NO_TARGETS")
        self.assertIs(r["merged"], m)
        r = ga.align_glosses(self.m, "art", lambda msg: calls.append(1), mode="corrected", enabled=False)
        self.assertEqual(r["status"], "DISABLED")
        self.assertFalse(calls)

    def test_never_reverts_kp_even_when_revert_would_be_safe(self):
        """legacyのfallback(i)相当(display_phraseへ戻す)は、correctedでは存在しない。"""
        m = _merged([_t(2, "right away", "right away now", "すぐに今")])
        fn, make, _ = _factory([_cresp([(2, False, "x", [], "FAIL")]), _cresp([(2, False, "y", [], "FAIL")])])
        r = ga.align_glosses(m, "art", make, mode="corrected", enabled=True)
        self.assertEqual(r["merged"]["items"][0]["key_phrase"], "right away now")

    def test_audit_files_and_cost(self):
        class U(FakeFn):
            def __call__(self):
                self.last_usage = {"input_tokens": 1000, "output_tokens": 500, "cached_input_tokens": 0}
                return super().__call__()
        fn = U([_cresp([(2, False, "インタビューをもとにした", [("interviews", "インタビュー")], "PASS"),
                        (3, False, "生豆の値段", [("raw-bean", "生豆"), ("prices", "値段")], "PASS")])])
        with tempfile.TemporaryDirectory() as d:
            r = ga.align_glosses(self.m, "art", lambda msg: fn, mode="corrected", enabled=True, out_dir=d, article_id="A")
            meta = json.load(open(os.path.join(d, "gloss_alignment_runtime_metadata.json"), encoding="utf-8"))
        self.assertEqual(meta["mode"], "corrected")
        self.assertEqual(meta["rules_sha256"], RulesExtraction.EXPECTED_SHA256)
        self.assertIsNotNone(r["cost_jpy"])
        self.assertEqual(r["attempts"][0]["usage"]["input_tokens"], 1000)


class PromptCorrected(unittest.TestCase):
    def test_message_has_new_instructions_and_no_slot_permission_sentence(self):
        t = [_t(2, "based on", "based on interviews", "～をもとにした")]
        msg = ga.build_user_message_corrected(t, "ART")
        self.assertIn(ga.load_approved_gloss_rules(), msg)                       # 承認規則は実行時抽出・無変更
        self.assertNotIn("スロット語がある場合に限り", msg)                         # 欠陥①の矛盾文を削除
        self.assertIn("「～」「〜」を含むかどうかは判定の基準ではありません", msg)
        self.assertIn("同じ部分を複数の語に対応させてかまいません", msg)            # Opus (b)
        self.assertIn('"added_content_words": [\n      "interviews"', msg)
        self.assertIn("インタビューをもとにした", msg)                              # 判定例

    def test_schema_requires_mappings(self):
        sch = ga.GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED["schema"]["properties"]["items"]["items"]
        self.assertIn("added_word_mappings", sch["required"])
        self.assertNotIn("added_word_mappings", ga.GLOSS_ALIGNMENT_JSON_SCHEMA["schema"]["properties"]["items"]["items"]["properties"])
        self.assertTrue(ga.GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED["strict"])

    def test_make_alignment_fn_uses_given_schema(self):
        seen = {}

        class R:
            model = "gpt-6-luna"; output_text = "{}"; id = "i"

        class C:
            class responses:
                @staticmethod
                def create(**k):
                    seen.update(k)
                    return R()
        fn = ga.make_alignment_fn("m", client=C(), model="gpt-6-luna", schema=ga.GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED)
        fn()
        self.assertEqual(seen["text"]["format"]["name"], "key_phrase_gloss_alignment_corrected")


def _hr_merged():
    fn, make, _ = _factory([_cresp([(2, False, "x", [], "FAIL")]), _cresp([(2, False, "y", [], "FAIL")])])
    m = _merged([_item(1, "right away", "right away", "すぐに"), _t(2, "based on", "based on interviews", "～をもとにした")])
    return ga.align_glosses(m, "art", make, mode="corrected", enabled=True)["merged"]


class HumanReviewReport(unittest.TestCase):
    def test_report_written_reread_validated_event_and_stdout(self):
        merged = _hr_merged()
        out = []
        with tempfile.TemporaryDirectory() as d:
            ev = ga.emit_human_review_notice(d, "ART", "a2", merged, print_fn=out.append)
            self.assertEqual(ga.validate_hr_report(os.path.join(d, ga.HR_REPORT_JSON)), [])
            doc = json.load(open(os.path.join(d, ga.HR_REPORT_JSON), encoding="utf-8"))
            md = open(os.path.join(d, ga.HR_REPORT_MD), encoding="utf-8").read()
        e = doc["entries"][0]
        self.assertEqual((e["article"], e["level"], e["rank"], e["key_phrase_en"]), ("ART", "a2", 2, "based on interviews"))
        self.assertEqual(e["current_japanese_gloss"], "～をもとにした")
        self.assertEqual(len(e["attempts"]), 2)
        self.assertTrue(e["failure_reasons"])
        rc = e["regeneration_candidates"]
        self.assertEqual(rc["reference_candidate"]["display_phrase"], "based on")
        self.assertIn("人間判断でのみ採用", rc["reference_candidate"]["caution"])
        self.assertIn("kp_regeneration", rc)
        self.assertIn("人間判断でのみ採用", md)
        self.assertFalse(ev["queue_used"])
        self.assertFalse(ev["human_review_lock_used"])
        self.assertTrue(ev["report_schema_validated"])
        self.assertEqual(len(out), 1)
        self.assertIn("[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED]", out[0])

    def test_no_unresolved_removes_stale_report_and_returns_none(self):
        merged = _hr_merged()
        with tempfile.TemporaryDirectory() as d:
            ga.emit_human_review_notice(d, "ART", "a2", merged, print_fn=lambda s: None)
            self.assertTrue(os.path.exists(os.path.join(d, ga.HR_REPORT_JSON)))
            ok = {"items": [dict(it, gloss_alignment_status="ALIGNED") for it in merged["items"]]}
            self.assertIsNone(ga.emit_human_review_notice(d, "ART", "a2", ok, print_fn=lambda s: None))
            self.assertFalse(os.path.exists(os.path.join(d, ga.HR_REPORT_JSON)))
            self.assertFalse(os.path.exists(os.path.join(d, ga.HR_REPORT_MD)))

    def test_write_failure_is_fail_closed(self):
        import unittest.mock as mock
        merged = _hr_merged()
        with tempfile.TemporaryDirectory() as d:
            real_open = open

            def bad_open(path, *a, **k):
                if str(path).endswith(ga.HR_REPORT_MD):
                    raise OSError("disk full (mock)")
                return real_open(path, *a, **k)
            with mock.patch("builtins.open", side_effect=bad_open):
                with self.assertRaises(ga.GlossAlignmentNotificationError):
                    ga.emit_human_review_notice(d, "ART", "a2", merged, print_fn=lambda s: None)

    def test_reread_validation_failure_is_fail_closed(self):
        import unittest.mock as mock
        merged = _hr_merged()
        with tempfile.TemporaryDirectory() as d, mock.patch.object(ga, "validate_hr_report", return_value=["entry0.attemptsが空"]):
            with self.assertRaises(ga.GlossAlignmentNotificationError):
                ga.emit_human_review_notice(d, "ART", "a2", merged, print_fn=lambda s: None)

    def test_validator_detects_empty_required_fields(self):
        merged = _hr_merged()
        with tempfile.TemporaryDirectory() as d:
            ga.emit_human_review_notice(d, "ART", "a2", merged, print_fn=lambda s: None)
            p = os.path.join(d, ga.HR_REPORT_JSON)
            doc = json.load(open(p, encoding="utf-8"))
            doc["entries"][0]["key_phrase_en"] = ""
            doc["entries"][0]["attempts"] = []
            json.dump(doc, open(p, "w", encoding="utf-8"), ensure_ascii=False)
            probs = ga.validate_hr_report(p)
        self.assertTrue(any("key_phrase_en" in x for x in probs))
        self.assertTrue(any("attempts" in x for x in probs))


class ResolveGloss(unittest.TestCase):
    def _write(self, d):
        p = os.path.join(d, "keywords_canonicalized.json")
        json.dump(_hr_merged(), open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return p

    def test_resolve_sets_human_resolved_and_clears_unresolved(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._write(d)
            ga.resolve_gloss(p, 2, "インタビューをもとにした", "tester", now="2026-10-15T00:00:00+00:00")
            doc = json.load(open(p, encoding="utf-8"))
            self.assertEqual(ga.collect_unresolved(doc), [])
            it = doc["items"][1]
            self.assertEqual(it["gloss_alignment_status"], "HUMAN_RESOLVED")
            self.assertEqual(it["japanese_gloss"], "インタビューをもとにした")
            self.assertEqual(it["japanese_gloss_tts"], "インタビューをもとにした")
            self.assertEqual(it["gloss_alignment_human_resolution"]["resolved_by"], "tester")
            self.assertEqual(it["gloss_alignment_human_resolution"]["previous_gloss"], "～をもとにした")
            self.assertNotIn("gloss_alignment_unresolved", doc)
            self.assertTrue(os.path.exists(os.path.join(d, "GLOSS_ALIGNMENT_HUMAN_RESOLUTIONS_01.jsonl")))
            self.assertEqual(doc["items"][0]["japanese_gloss"], "すぐに")      # 他itemは無変更

    def test_resolve_rejects_violations_without_writing(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._write(d)
            before = open(p, encoding="utf-8").read()
            for bad in ("2つの", "インタビュー(取材)をもとにした", "インタビュー…をもとにした", "  "):
                with self.assertRaises(ga.GlossResolveRejected):
                    ga.resolve_gloss(p, 2, bad, "tester")
            with self.assertRaises(ga.GlossResolveRejected):
                ga.resolve_gloss(p, 2, "インタビューをもとにした", " ")       # 記録者必須
            with self.assertRaises(ga.GlossResolveRejected):
                ga.resolve_gloss(p, 1, "すぐさま", "tester")                  # HR待ちでないitemは書き換えない
            self.assertEqual(open(p, encoding="utf-8").read(), before)


@_explicit_on
class ScaffoldCorrected(unittest.TestCase):
    def _canon(self, fake, mode):
        import unittest.mock as mock
        import er003_v1_n3_01_scaffold_generate as sc
        originals = [
            {"rank": 1, "display_phrase": "right away", "source_span": "right away", "source_sentence": "Do it right away.",
             "ja_gloss": "すぐに", "source_reference_contract": "X"},
            {"rank": 2, "display_phrase": "based on", "source_span": "based on",
             "source_sentence": "It is an estimate based on interviews with sellers.", "ja_gloss": "～をもとにした",
             "source_reference_contract": "X"},
        ]
        qa = {f: "PASS" for f in kc.QA_FIELDS}
        parsed = {"items": [
            {"rank": 1, "key_phrase": "right away", "changed_from_display_phrase": False, "normalization_reason": "none",
             "reasoning": "r", **qa},
            {"rank": 2, "key_phrase": "based on interviews", "changed_from_display_phrase": True,
             "normalization_reason": "restore_semantic_complement", "reasoning": "r", **qa}]}
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(sc.kc, "run_canonicalization_gate",
                                  return_value=(parsed, "CANONICALIZATION_PASS", [], "gpt-6-luna", "resp")), \
                mock.patch.object(sc.gloss_align, "make_alignment_fn", return_value=fake) as mk:
            kw = {} if mode is None else {"gloss_alignment_mode": mode}
            res = sc.run_key_phrase_canonicalization("ART", originals, d, "A", process="A2_SUPPORT", **kw)
            saved = json.load(open(os.path.join(d, "keywords_canonicalized.json"), encoding="utf-8"))
        return res, saved, mk

    def test_corrected_success_and_schema_passed(self):
        fake = FakeFn([_cresp([(2, False, "インタビューをもとにした", [("interviews", "インタビュー")], "PASS")])])
        res, saved, mk = self._canon(fake, "corrected")
        self.assertEqual(res["gloss_alignment_status"], "ALIGN_PASS")
        self.assertEqual(saved["items"][1]["japanese_gloss"], "インタビューをもとにした")
        self.assertIs(mk.call_args.kwargs.get("schema"), ga.GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED)

    def test_corrected_failure_persists_hr_status_not_legacy_failed(self):
        fake = FakeFn([_cresp([(2, False, "x", [], "FAIL")]), _cresp([(2, False, "y", [], "FAIL")])])
        res, saved, _ = self._canon(fake, "corrected")
        self.assertEqual(res["status"], "CANONICALIZATION_PASS")
        self.assertEqual(saved["items"][1]["gloss_alignment_status"], ga.STATUS_HR_REQUIRED)
        self.assertEqual(saved["items"][1]["key_phrase"], "based on interviews")
        self.assertIsNone(res["gloss_alignment_fallback"])
        self.assertEqual(res["gloss_alignment_unresolved_ranks"], [2])

    def test_default_mode_unchanged_legacy_and_no_schema_kwarg(self):
        fake = FakeFn([_resp([(2, False, "インタビューをもとにした", "PASS")])])
        res, saved, mk = self._canon(fake, None)
        self.assertEqual(res["gloss_alignment_status"], "ALIGN_PASS")
        self.assertNotIn("schema", mk.call_args.kwargs)
        self.assertNotIn("gloss_alignment_unresolved_ranks", res)

    def test_run_key_phrases_corrected_emits_one_event_on_final_artifact_only(self):
        import unittest.mock as mock
        import er003_v1_n3_01_scaffold_generate as sc
        merged = _hr_merged()
        impl_ret = {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"},
                    "canonicalization": {"status": "CANONICALIZATION_PASS", "merged": merged}, "redundancy_qa": {}}
        out = []
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(sc, "_run_key_phrases_impl", return_value=dict(impl_ret)) as impl, \
                mock.patch("builtins.print", side_effect=lambda *a, **k: out.append(" ".join(map(str, a)))):
            res = sc.run_key_phrases("ART", d, "AID", "A2", gloss_alignment_mode="corrected")
            self.assertTrue(os.path.exists(os.path.join(d, ga.HR_REPORT_JSON)))
        self.assertEqual(len(res["gloss_alignment_human_review_events"]), 1)
        self.assertEqual(res["status"], ga.STOPPED_STATUS)
        self.assertEqual(impl.call_args.kwargs["gloss_alignment_mode"], "corrected")
        self.assertEqual(len([o for o in out if "[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED]" in o]), 1)

    def test_run_key_phrases_legacy_call_shape_unchanged(self):
        import unittest.mock as mock
        import er003_v1_n3_01_scaffold_generate as sc
        impl_ret = {"selection": {}, "canonicalization": {"status": "CANONICALIZATION_PASS", "merged": _hr_merged()},
                    "redundancy_qa": {}}
        with tempfile.TemporaryDirectory() as d, mock.patch.object(sc, "_run_key_phrases_impl", return_value=dict(impl_ret)) as impl:
            res = sc.run_key_phrases("ART", d, "AID", "A2")
            self.assertNotIn("gloss_alignment_mode", impl.call_args.kwargs)
            self.assertNotIn("gloss_alignment_human_review_events", res)
            self.assertFalse(os.path.exists(os.path.join(d, ga.HR_REPORT_JSON)))


class DefaultOffIsolation(unittest.TestCase):
    """2026-10-15 ユーザー承認(案a): flag既定OFF。明示ONしない限りgloss再整合は実行されない(追加API呼出0・gloss不変・HR成果物なし)。"""

    @staticmethod
    def _fresh_flag(env_value):
        import subprocess
        import sys
        env = {k: v for k, v in os.environ.items() if k != "EIGO_KP_GLOSS_ALIGNMENT"}
        if env_value is not None:
            env["EIGO_KP_GLOSS_ALIGNMENT"] = env_value
        out = subprocess.run([sys.executable, "-c", "import er003_key_words_gloss_alignment as g;print(g.GLOSS_ALIGNMENT_ENABLED)"],
                             capture_output=True, text=True, env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        return out.stdout.strip()

    def test_env_unset_is_off_and_explicit_values(self):
        self.assertEqual(self._fresh_flag(None), "False")
        self.assertEqual(self._fresh_flag("0"), "False")
        self.assertEqual(self._fresh_flag(""), "False")
        self.assertEqual(self._fresh_flag("1"), "True")
        self.assertEqual(self._fresh_flag("true"), "True")

    def test_default_noop_legacy_and_corrected(self):
        old = ga.GLOSS_ALIGNMENT_ENABLED
        ga.GLOSS_ALIGNMENT_ENABLED = False   # 既定(env未設定)と同じ状態
        try:
            m = _merged([_item(2, "based on", "based on interviews", "～をもとにした", beyond=True)])
            for mode in (None, "legacy", "corrected"):
                fn = FakeFn([])
                with tempfile.TemporaryDirectory() as d:
                    r = ga.align_glosses(m, "art", lambda msg: fn, out_dir=d, article_id="a", mode=mode)
                    self.assertEqual(os.listdir(d), [])   # artifact/HR報告書なし
                self.assertEqual(r["status"], "DISABLED")
                self.assertIs(r["merged"], m)
                self.assertEqual(r["attempts"], [])
                self.assertEqual(fn.calls, 0)
            self.assertIsNone(ga.preflight())          # 承認規則の抽出も走らない
        finally:
            ga.GLOSS_ALIGNMENT_ENABLED = old

    def test_scaffold_default_off_makes_no_alignment_call(self):
        import unittest.mock as mock
        import er003_v1_n3_01_scaffold_generate as sc
        old = ga.GLOSS_ALIGNMENT_ENABLED
        ga.GLOSS_ALIGNMENT_ENABLED = False
        try:
            m = _merged([_item(2, "based on", "based on interviews", "～をもとにした", beyond=True)])
            with mock.patch.object(ga, "make_alignment_fn", side_effect=AssertionError("alignment API must not be created")):
                r = ga.align_glosses(m, "art", lambda msg: (_ for _ in ()).throw(AssertionError("no api")))
            self.assertEqual(r["status"], "DISABLED")
            self.assertTrue(hasattr(sc, "run_key_phrase_canonicalization"))
        finally:
            ga.GLOSS_ALIGNMENT_ENABLED = old

    def test_scaffold_canonicalization_default_off_no_call_no_change_no_files(self):
        """Production関数sc.run_key_phrase_canonicalization(X/Z共通の到達点)を通しても、既定OFFならAPI呼出0・gloss不変・追加成果物なし。"""
        import unittest.mock as mock
        import er003_v1_n3_01_scaffold_generate as sc
        old = ga.GLOSS_ALIGNMENT_ENABLED
        ga.GLOSS_ALIGNMENT_ENABLED = False
        try:
            originals = [{"rank": 2, "display_phrase": "based on", "source_span": "based on",
                          "source_sentence": "It is an estimate based on interviews with sellers.", "ja_gloss": "～をもとにした",
                          "source_reference_contract": "X"}]
            qa = {f: "PASS" for f in kc.QA_FIELDS}
            parsed = {"items": [{"rank": 2, "key_phrase": "based on interviews", "changed_from_display_phrase": True,
                                 "normalization_reason": "restore_semantic_complement", "reasoning": "r", **qa}]}
            fake = FakeFn([])
            for mode in (None, "legacy"):
                with tempfile.TemporaryDirectory() as d,                         mock.patch.object(sc.kc, "run_canonicalization_gate",
                                          return_value=(parsed, "CANONICALIZATION_PASS", [], "m", "resp")),                         mock.patch.object(sc.gloss_align, "make_alignment_fn", return_value=fake) as mk:
                    res = sc.run_key_phrase_canonicalization("ART", originals, d, "A", process="A2_SUPPORT",
                                                             **({} if mode is None else {"gloss_alignment_mode": mode}))
                    saved = json.load(open(os.path.join(d, "keywords_canonicalized.json"), encoding="utf-8"))
                    files = sorted(os.listdir(d))
                self.assertEqual(res["gloss_alignment_status"], "DISABLED")
                self.assertEqual(fake.calls, 0)
                self.assertEqual(mk.call_count, 0)
                self.assertEqual(saved["items"][0]["japanese_gloss"], "～をもとにした")
                self.assertNotIn("gloss_alignment_status", saved["items"][0])
                self.assertFalse([f for f in files if "GLOSS" in f.upper() or "HUMAN_REVIEW" in f.upper()])
        finally:
            ga.GLOSS_ALIGNMENT_ENABLED = old

    def _corrected_canon(self, flag):
        import unittest.mock as mock
        import er003_v1_n3_01_scaffold_generate as sc
        old = ga.GLOSS_ALIGNMENT_ENABLED
        ga.GLOSS_ALIGNMENT_ENABLED = flag
        try:
            originals = [{"rank": 2, "display_phrase": "based on", "source_span": "based on",
                          "source_sentence": "It is an estimate based on interviews with sellers.", "ja_gloss": "～をもとにした",
                          "source_reference_contract": "X"}]
            qa = {f: "PASS" for f in kc.QA_FIELDS}
            parsed = {"items": [{"rank": 2, "key_phrase": "based on interviews", "changed_from_display_phrase": True,
                                 "normalization_reason": "restore_semantic_complement", "reasoning": "r", **qa}]}
            fake = FakeFn([_cresp([(2, False, "インタビューをもとにした", [], "PASS")])])
            with tempfile.TemporaryDirectory() as d, mock.patch.object(sc.kc, "run_canonicalization_gate",
                                          return_value=(parsed, "CANONICALIZATION_PASS", [], "m", "resp")),                     mock.patch.object(sc.gloss_align, "make_alignment_fn", return_value=fake) as mk:
                res = sc.run_key_phrase_canonicalization("ART", originals, d, "A", process="A2_SUPPORT",
                                                         gloss_alignment_mode="corrected")
                files = sorted(os.listdir(d))
            return res, fake, mk, files
        finally:
            ga.GLOSS_ALIGNMENT_ENABLED = old

    def test_corrected_mode_without_flag_is_disabled_no_call(self):
        """委任_03: flagが唯一のkill switch。mode=correctedでもflag未設定ならDISABLED・API 0・HR成果物なし。"""
        res, fake, mk, files = self._corrected_canon(False)
        self.assertEqual(res["gloss_alignment_status"], "DISABLED")
        self.assertEqual(fake.calls, 0)
        self.assertEqual(mk.call_count, 0)
        self.assertFalse([f for f in files if "GLOSS" in f.upper() or "HUMAN_REVIEW" in f.upper()])

    def test_corrected_mode_with_flag_runs(self):
        res, fake, mk, files = self._corrected_canon(True)
        self.assertNotEqual(res["gloss_alignment_status"], "DISABLED")
        self.assertGreaterEqual(fake.calls, 1)
        self.assertTrue(ga.flag_enabled() is False)   # 復元済み(既定OFF)

    def test_explicit_on_still_works(self):
        m = _merged([_item(2, "based on", "based on interviews", "～をもとにした", beyond=True)])
        fn = FakeFn([_resp([(2, False, "インタビューをもとにした", "PASS")])])
        r = ga.align_glosses(m, "art", lambda msg: fn, enabled=True)
        self.assertEqual(fn.calls, 1)
        self.assertNotEqual(r["status"], "DISABLED")

    def test_mode_default_still_legacy(self):
        self.assertEqual(ga.GLOSS_ALIGNMENT_MODE, "legacy")


if __name__ == "__main__":
    unittest.main()
