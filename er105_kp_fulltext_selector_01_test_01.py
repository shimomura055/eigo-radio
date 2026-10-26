# -*- coding: utf-8 -*-
"""er105_kp_fulltext_selector_01 のunit test(API 0・Production未配線)。
実行: .venv\\Scripts\\python.exe -m unittest er105_kp_fulltext_selector_01_test_01 -v"""
import glob
import hashlib
import json
import os
import re
import sys
import tempfile
import unittest

import er105_kp_fulltext_selector_01 as m

ROOT = os.path.dirname(os.path.abspath(__file__))
USER_MD = os.path.join(ROOT, "docs", "pm", "delegation_log", "2026-10-22_KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01_USER.md")

ARTICLE = (
    "# Coffee prices\n\n"
    "Market insiders say a time lag is built in. Retail prices follow raw beans slowly.\n"
    "Cafes keep raw beans in stock, so they don't feel a spike at once. Before you know it, the bill rises.\n"
    "Some owners pushed prices up in May. Others took a sharp turn toward cheaper blends.\n"
    "The stage is set for more increases. Retail prices may stay high.\n"
)


def _ok_call(items):
    """正常応答を返すcall_fnのfactory(make_call_fn用)。"""
    def make(msg):
        def fn():
            return json.dumps({"items": items}, ensure_ascii=False), "gpt-6-luna", "resp_x"
        return fn
    return make


class TestPromptFixed(unittest.TestCase):
    def test_prompt_matches_user_original_verbatim(self):
        with open(USER_MD, encoding="utf-8") as fh:
            text = fh.read()
        parts = text.split("\n---\n")
        # §2は「---」で挟まれた2本の間。Prompt 2本文=最初の`---`と次の`---`の間
        sec2 = text.split("## 2. 正式Prompt")[1].split("## 3.")[0]
        body = sec2.split("\n---\n")[1].strip("\n")
        self.assertEqual(body, m.PROMPT_2_TEXT)
        self.assertGreater(len(parts), 2)

    def test_prompt_sha_pinned(self):
        self.assertEqual(m.PROMPT_2_SHA256, hashlib.sha256(m.PROMPT_2_TEXT.encode("utf-8")).hexdigest())
        # 固定値(配線時もこの値が不変であること。変更はユーザー明示承認が必要)
        self.assertEqual(m.PROMPT_2_SHA256, EXPECTED_SHA)

    def test_key_prompt_conditions_present(self):
        t = m.PROMPT_2_TEXT
        for needle in ("**3つ**", "本文一致（絶対条件）", "5語以内（絶対条件）", "学習ポイントの明確化と最小化（必須）",
                       "上級者向けの学習価値", "易しい表現の除外", "3件選定", "語数も併記してください"):
            self.assertIn(needle, t)
        self.assertNotIn("5つ", t)   # 旧5件Promptの残存なし

    def test_message_prefix_intact_and_note_after_body(self):
        msg = m.build_user_message(ARTICLE)
        self.assertTrue(m.prompt_prefix_intact(msg))
        self.assertTrue(msg.endswith(ARTICLE))
        msg2 = m.build_user_message(ARTICLE, "note-x")
        self.assertTrue(m.prompt_prefix_intact(msg2))
        self.assertIn(ARTICLE + m.NOTE_DELIMITER + "note-x", msg2)

    def test_constants(self):
        self.assertEqual(m.KP_COUNT_MAX, 3)
        self.assertEqual(m.KP_WORDS_MAX, 5)
        self.assertEqual(m.SELECTION_MODEL_ID, "gpt-6-luna")
        sch = m.SELECTOR_JSON_SCHEMA["schema"]["properties"]["items"]
        # OF-KPFT-P-10: strictモードのschema拒否(HTTP 400)で全呼出が止まる事故を避けるため、件数制約はschemaに置かずローカル検証のみ
        self.assertNotIn("maxItems", sch)
        self.assertNotIn("minItems", sch)


EXPECTED_SHA = "a12896f485604f32efd52cb159d2615733c0eca262725af78db0b4f1c9a3dc9a"


class TestParse(unittest.TestCase):
    def test_valid(self):
        r = m.parse_selection(json.dumps({"items": [{"phrase": "time lag", "word_count": 2}]}))
        self.assertEqual(r[0]["phrase"], "time lag")
        self.assertEqual(r[0]["declared_word_count"], 2)

    def test_fail_closed_on_garbage(self):
        for bad in ("", "not json", "[]", json.dumps({"x": 1}), json.dumps({"items": [{"phrase": "", "word_count": 1}]}),
                    json.dumps({"items": ["a"]}), json.dumps({"items": [{"word_count": 2}]})):
            with self.assertRaises(m.ParseError):
                m.parse_selection(bad)

    def test_no_markdown_heuristic(self):
        # 自由文(Trialの表形式)は受理しない=手動補正に頼る余地を作らない
        with self.assertRaises(m.ParseError):
            m.parse_selection("| 表現 | 語数 |\n|---|---|\n| **time lag** | 2語 |")


def _units():
    import er030_key_phrase_db_hybrid_core_01 as core
    return core.build_sentence_units(ARTICLE)


class TestLocateAndValidate(unittest.TestCase):
    def test_exact_case_and_boundaries(self):
        u = _units()
        self.assertEqual(m.locate_phrase(u, "time lag")[0]["span"], "time lag")
        self.assertEqual(m.locate_phrase(u, "Time Lag")[0]["span"], "time lag")        # 大文字小文字のみ吸収、spanは原文どおり
        self.assertEqual(m.locate_phrase(u, "before you know it")[0]["span"], "Before you know it")
        self.assertEqual(m.locate_phrase(u, "raw bean"), [])                           # 語の途中一致は不成立
        self.assertEqual(m.locate_phrase(u, "in the"), [])

    def test_apostrophe_and_dash_variants(self):
        import er030_key_phrase_db_hybrid_core_01 as core
        u = core.build_sentence_units("They don’t mind. A Saudi-led force arrived.")
        self.assertTrue(m.locate_phrase(u, "don't mind"))
        self.assertTrue(m.locate_phrase(u, "Saudi–led force"))

    def test_cross_sentence_phrase_not_matched(self):
        self.assertEqual(m.locate_phrase(_units(), "slowly. Cafes keep"), [])

    def test_validate_pass_and_resolution(self):
        sel = [{"phrase": "time lag", "declared_word_count": 2}, {"phrase": "pushed prices up", "declared_word_count": 3},
               {"phrase": "took a sharp turn", "declared_word_count": 4}]
        v = m.validate_and_resolve(sel, _units())
        self.assertTrue(v["ok"], v)
        self.assertEqual([r["selection_resolution_method"] for r in v["resolved"]], ["fulltext_exact_unique"] * 3)
        self.assertTrue(all(r["source_sentence_id"].startswith("S") for r in v["resolved"]))

    def test_first_of_n_when_phrase_in_multiple_sentences(self):
        v = m.validate_and_resolve([{"phrase": "retail prices", "declared_word_count": 2}], _units())
        self.assertTrue(v["ok"])
        r = v["resolved"][0]
        self.assertEqual(r["selection_resolution_method"], "fulltext_exact_first_of_N")
        self.assertEqual(r["occurrence_count"], 2)
        self.assertEqual(r["source_span"], "Retail prices")   # 原文スライス(先頭出現)

    def test_rejections(self):
        u = _units()
        cases = {
            "not_in_text": [{"phrase": "pass the baton", "declared_word_count": 3}],
            "six_words": [{"phrase": "Cafes keep raw beans in stock so", "declared_word_count": 7}],
            "paraphrase": [{"phrase": "time delay", "declared_word_count": 2}],
            "finite_aux": [{"phrase": "The stage is set", "declared_word_count": 4}],
            "dup": [{"phrase": "time lag", "declared_word_count": 2}, {"phrase": "Time Lag", "declared_word_count": 2}],
            "too_many": [{"phrase": p, "declared_word_count": 2} for p in ("time lag", "raw beans", "sharp turn", "more increases")],
            "empty": [],
        }
        for name, sel in cases.items():
            v = m.validate_and_resolve(sel, u)
            self.assertFalse(v["ok"], name)

    def test_declared_wc_mismatch_is_recorded_not_blocking(self):
        v = m.validate_and_resolve([{"phrase": "time lag", "declared_word_count": 5}], _units())
        self.assertTrue(v["ok"])
        self.assertTrue(v["resolved"][0]["declared_word_count_mismatch"])


class TestOriginalItemsContract(unittest.TestCase):
    def setUp(self):
        v = m.validate_and_resolve([{"phrase": "pushed prices up", "declared_word_count": 3},
                                    {"phrase": "time lag", "declared_word_count": 2}], _units())
        self.items = m.build_original_items(v["resolved"])

    def test_no_candidate_id_contract_key(self):
        # source_reference_contractを付けない(付けると案A'窓拡張・kp_extends_beyond_candidateが誤発火する)
        for it in self.items:
            self.assertNotIn("source_reference_contract", it)
            self.assertNotIn("key_phrase_role", it)
            self.assertEqual(it["fulltext_source_ref"], m.FULLTEXT_SOURCE_REF_ID)

    def test_compatible_with_existing_canonicalization_input_and_merge(self):
        import er003_key_words_canonicalization as kc
        self.assertEqual(kc.expand_dangling_source_span(self.items[0]), self.items[0]["source_span"])   # 窓拡張なし
        msg = kc.build_user_message(self.items, ARTICLE)
        self.assertIn("pushed prices up", msg)
        canon_items = [{"rank": it["rank"], "key_phrase": it["display_phrase"], "changed_from_display_phrase": False,
                        "normalization_reason": "none", "reasoning": "r", **{f: "PASS" for f in kc.QA_FIELDS}} for it in self.items]
        merged = kc.merge_canonicalization_result(self.items, canon_items)
        self.assertEqual([i["rank"] for i in merged["items"]], [1, 2])
        self.assertEqual(merged["items"][0]["japanese_gloss_tts"], "")
        self.assertIsNone(merged["items"][0]["japanese_gloss"])   # gloss未生成=後段gloss工程の対象(設計書§4-3)
        self.assertFalse(merged["items"][0]["kp_extends_beyond_candidate"])
        v = kc.validate_canonicalization_response({"items": canon_items}, self.items)
        self.assertEqual(v.get("status"), "CANONICALIZATION_PASS", v)


class TestGate(unittest.TestCase):
    def test_pass_first_try(self):
        g = m.run_selection_gate(ARTICLE, _ok_call([{"phrase": "time lag", "word_count": 2},
                                                    {"phrase": "pushed prices up", "word_count": 3}]))
        self.assertEqual(g["status"], m.STATUS_PASS)
        self.assertTrue(g["shortfall"])           # 2件<3件=候補不足として許容(数合わせなし)
        self.assertEqual(len(g["attempts_detail"]), 1)

    def test_retry_then_pass_on_technical_failure(self):
        calls = {"n": 0}

        def make(msg):
            def fn():
                calls["n"] += 1
                if calls["n"] == 1:
                    raise ConnectionError("boom")
                return json.dumps({"items": [{"phrase": "time lag", "word_count": 2}]}), "gpt-6-luna", "r2"
            return fn
        g = m.run_selection_gate(ARTICLE, make)
        self.assertEqual(g["status"], m.STATUS_PASS)
        self.assertEqual(calls["n"], 2)
        self.assertEqual(g["attempts_detail"][0]["status"], m.STATUS_TECHNICAL_FAILED)

    def test_fail_closed_after_max_attempts_parse(self):
        calls = {"n": 0}

        def make(msg):
            def fn():
                calls["n"] += 1
                return "free text answer", "gpt-6-luna", "r"
            return fn
        g = m.run_selection_gate(ARTICLE, make)
        self.assertEqual(g["status"], m.STATUS_PARSE_FAILED)
        self.assertIsNone(g["items"])
        self.assertEqual(calls["n"], m.MAX_ATTEMPTS)   # 上限を超えて呼ばない

    def test_fail_closed_after_max_attempts_invalid(self):
        g = m.run_selection_gate(ARTICLE, _ok_call([{"phrase": "pass the baton", "word_count": 3}]))
        self.assertEqual(g["status"], m.STATUS_INVALID)
        self.assertIsNone(g["items"])
        self.assertEqual(len(g["attempts_detail"]), m.MAX_ATTEMPTS)

    def test_model_mismatch_is_technical_failure(self):
        def make(msg):
            def fn():
                raise m.ModelMismatchError("応答モデルが不一致")
            return fn
        g = m.run_selection_gate(ARTICLE, make)
        self.assertEqual(g["status"], m.STATUS_TECHNICAL_FAILED)

    def test_selector_fn_checks_actual_model_id(self):
        class R:
            model, id, output_text = "gpt-5.6-sol", "x", "{}"

        class C:
            class responses:
                @staticmethod
                def create(**kw):
                    return R()
        fn = m.make_selector_fn("msg", client=C())
        with self.assertRaises(m.ModelMismatchError):
            fn()


class TestRunEntry(unittest.TestCase):
    def test_artifacts_and_result_shape(self):
        with tempfile.TemporaryDirectory() as d:
            res = m.run_fulltext_selection(
                ARTICLE, d, "art1", "A2", process="A2_SUPPORT",
                make_call_fn=_ok_call([{"phrase": "time lag", "word_count": 2}, {"phrase": "took a sharp turn", "word_count": 4},
                                       {"phrase": "raw beans", "word_count": 2}]))
            self.assertEqual(res["status"], "KEY_WORDS_STRUCTURE_PASS")
            self.assertEqual(res["kp_backend_used"], "fulltext_p2")
            self.assertEqual(len(res["original_items"]), 3)
            self.assertEqual(res["parsed"]["items"], res["original_items"])
            with open(f"{d}/keywords_runtime_metadata.json", encoding="utf-8") as fh:
                meta = json.load(fh)
            self.assertEqual(meta["prompt_sha256"], m.PROMPT_2_SHA256)
            self.assertEqual(meta["model_requested"], "gpt-6-luna")
            self.assertEqual(meta["model_id"], "gpt-6-luna")
            self.assertEqual(meta["kp_count_max"], 3)
            with open(f"{d}/keywords_selector_prompt.txt", encoding="utf-8") as fh:
                sent = fh.read()
            self.assertTrue(m.prompt_prefix_intact(sent))

    def test_failure_result_has_no_items(self):
        with tempfile.TemporaryDirectory() as d:
            res = m.run_fulltext_selection(ARTICLE, d, "a", "B1", process="B1_SUPPORT",
                                           make_call_fn=_ok_call([{"phrase": "invented phrase", "word_count": 2}]))
            self.assertEqual(res["status"], m.STATUS_INVALID)
            self.assertNotIn("original_items", res)
            self.assertIsNone(res["parsed"])

    def test_process_must_be_support_luna(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(m.FulltextSelectionError):
                m.run_fulltext_selection(ARTICLE, d, "a", "B1", process="STANDARD_A2_ADAPTATION", make_call_fn=_ok_call([]))
            with self.assertRaises(m.FulltextSelectionError):
                m.resolve_model(None)

    def test_resolve_model_is_luna_via_routing(self):
        self.assertEqual(m.resolve_model("A2_SUPPORT"), "gpt-6-luna")
        self.assertEqual(m.resolve_model("B1_SUPPORT"), "gpt-6-luna")


class TestIsolation(unittest.TestCase):
    """配線後の機械的証拠: er105を参照するProductionファイルは委任_02で配線した最小集合だけ(予期せぬ参照元が無い)。API 0。"""
    ALLOWED = {"er003_key_words_canonicalization.py", "er003_v1_n3_01_scaffold_generate.py",
               "er119_kp_candidates_01.py", "er119_kp_prompt_2v_01.py",
               "er125_kp_rescue_production_01.py"}   # KPRW1 委任_01(2026-10-26 APPROVED_FOR_PRODUCTION): 救済module(委任_02でProduction配線。er105のvalidatorを再利用)。KP Human Review(2026-10-25 APPROVED_FOR_PRODUCTION): 候補生成がer105の選定関数を再利用する

    def test_no_production_file_references_er105(self):
        offenders = []
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if b.startswith("er105_"):
                continue
            if b.startswith("er123_"):
                continue   # DEV専用module(KP-GATE-EXCLUSION-RESCUE-DESIGN-02。Production到達経路なし。委任_03で既存の失敗を是正: 委任_01から未登録だった)
            if b.startswith("er124_"):
                continue   # DEV/Trial専用module(KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01。Production到達経路なし。逆方向のimport禁止は er124_kp_phrase_word_trial_test_01.IsolationTests が担保)
            if b.startswith("er112_"):
                continue   # DEV/Trial専用module(Production到達経路なし。逆方向のimport禁止は er112_kp_gm_trial_01_test_01.test_no_production_module_imports_er112 が担保)
            with open(p, encoding="utf-8", errors="ignore") as f:
                if re.search(r"\ber105_kp_fulltext", f.read()) and "test" not in b and b not in self.ALLOWED:
                    offenders.append(b)
        self.assertEqual(offenders, [])


class TestTrialReplay(unittest.TestCase):
    """保存済みTrial-02のLuna実出力(5件版Prompt)の語句を、本文照合に通す(API 0)。モデル出力の本文一致・語数の実データ確認。"""

    def test_replay_luna_trial02_phrases(self):
        run_dir = os.path.join(ROOT, "er101_output", "kp_prompt_min_gen_trial_02", "runs", "n1_gpt-6-luna")
        files = sorted(glob.glob(run_dir + "/*.json"))
        if not files:
            self.skipTest("Trial-02 artifact not present")
        import er030_key_phrase_db_hybrid_core_01 as core
        total = ok_text = 0
        for f in files:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
            with open(os.path.join(ROOT, "er098_output", "kp_six_model_trial_01", "inputs", "articles", d["unit_id"] + ".txt"),
                      encoding="utf-8") as fh:
                art = fh.read()
            units = core.build_sentence_units(art)
            rows = [l for l in d["response_text"].splitlines() if l.strip().startswith("|")
                    and not set(l.replace("|", "").strip()) <= set("-: ")]
            for l in rows[1:]:
                phrase = [x.strip() for x in l.strip().strip("|").split("|")][0].replace("*", "").strip()
                total += 1
                if m.locate_phrase(units, phrase) and 1 <= m.count_words(phrase) <= 5:
                    ok_text += 1
        self.assertEqual(total, 70)
        # 実測: 69/70が本文連続一致(不一致1件=E_Standard `passed the baton`[本文は`hands the baton`系]=検証でretryされるべき実例)
        self.assertGreaterEqual(ok_text, 68)


class TestInflectionNormalizationPrototype(unittest.TestCase):
    """原形化validatorのプロトタイプ(未配線、設計書§4-2)。Trial-02(Haiku一般化)の失敗例を拒否し、基本形化のみ許す。"""

    def test_accepts_base_form_one_to_one_token_replacement(self):
        for k, d in [("push prices up", "pushed prices up"), ("roll back", "rolled back"), ("brush aside", "brushed aside"),
                     ("give back some gains", "gave back some gains"), ("take a sharp turn", "took a sharp turn"),
                     ("pump one's fist", "pumps its fist"), ("hand the baton", "hands the baton"), ("retail price", "retail prices"),
                     ]:
            self.assertTrue(m.is_valid_inflection_normalization(k, d), (k, d))

    def test_v_plus_adverb_or_noun_phrases_are_not_normalized(self):
        # 範囲縮小(開示): V+名詞・-ly以外の副詞は形容詞化分詞・名詞修飾と区別できないため基本形化しない(表層形のまま=Rule7無変更で扱う)
        # 委任_03(2026-10-26、区分1): 閉表の副詞(hard/fast/alone/again/often/always/never)と語幹CMU実在の-ly副詞が句末/前置詞等の前にある形は、
        # 承認文「先頭またはto直後の動詞」の目的に沿って原形化を許す(tried hard->try hard)。V+名詞(raised concerns)・表外の副詞(stopped short)は従来どおり拒否。
        for k, d in [("stop short", "stopped short"), ("raise concern", "raised concerns")]:
            self.assertFalse(m.is_valid_inflection_normalization(k, d), (k, d))
        self.assertTrue(m.is_valid_inflection_normalization("try hard", "tried hard"))

    def test_rejects_content_change_or_length_change(self):
        for k, d in [("keep raw materials in stock", "keep raw beans in stock"), ("human concierge service", "human concierge feature"),
                     ("moving something forward", "moving the story forward"), ("blurted something out", "blurted that out"),
                     ("hand the baton to someone", "hands the baton"), ("pumps their fist", "pumps its fist"),
                     ("time lag", "time lag"), ("", "time lag")]:
            self.assertFalse(m.is_valid_inflection_normalization(k, d), (k, d))


class TestZD1GateCompatibility(unittest.TestCase):
    """全文選定itemは、Z D1 gate(曖昧=STOP)を『exact』で冪等に通る(複数文出現でも先頭出現のunit全文がsource_sentenceのため一意)。"""

    def test_zd1_exact_resolution_including_first_of_n(self):
        import er026_family_z_src_posthoc_01 as P
        v = m.validate_and_resolve([{"phrase": "retail prices", "declared_word_count": 2},
                                    {"phrase": "Before you know it", "declared_word_count": 4},
                                    {"phrase": "took a sharp turn", "declared_word_count": 4}], _units())
        self.assertTrue(v["ok"], v)
        items = m.build_original_items(v["resolved"])
        kp = {"items": [{**it, "used_form": it["display_phrase"]} for it in items]}
        rep = P.apply_to_kp(kp, ARTICLE, "a2")
        self.assertEqual(rep["status"], "PASS", rep)
        self.assertEqual([i["resolution_method"] for i in rep["items"]], ["exact"] * 3)   # D1側のフィールド名(=exact)
        # OF-KPFT-P-06: D1が`resolution_method`を上書きしても、選定時の解決方式は別名で保持される
        self.assertEqual([i["selection_resolution_method"] for i in kp["items"]],
                         ["fulltext_exact_first_of_N", "fulltext_exact_unique", "fulltext_exact_unique"])
        self.assertEqual(rep["ambiguous"], [])


if __name__ == "__main__":
    unittest.main()
