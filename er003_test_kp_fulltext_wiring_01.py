# -*- coding: utf-8 -*-
"""KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_02: 全文選定(Prompt 2・最大3件)のX/Z Production配線test(API 0・オフライン)。
Opus条件A(OF-KPFT-P-01〜P-14)の各指摘に対応するtestと、A/B/C旧経路のバイト同一test、1/2/3件のrank駆動test、
Dangling Reference Grep testを含む。判定フィールド名(kp_dual_check/kp_vote_check)には依存しない(P-12)。
実行: .venv\\Scripts\\python.exe -W error -m unittest er003_test_kp_fulltext_wiring_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401  (Production監査ログ・telemetryへの追記を隔離)

import hashlib
import inspect
import json
import os
import re
import tempfile
import unittest
from unittest import mock

import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga
import er003_v1_n3_01_scaffold_generate as sc
import er011_key_phrase_set_redundancy_qa_01 as rq
import er019_family_x_kp_explanation_01 as kexp
import er030_key_phrase_db_hybrid_core_01 as core
import er105_kp_fulltext_selector_01 as ft

ROOT = os.path.dirname(os.path.abspath(__file__))
PROMPT_2_SHA = "a12896f485604f32efd52cb159d2615733c0eca262725af78db0b4f1c9a3dc9a"

ARTICLE = (
    "# Coffee prices\n\n"
    "Market insiders say a time lag is built in. Retail prices follow raw beans slowly.\n"
    "Cafes keep raw beans in stock, so they don't feel a spike at once. Before you know it, the bill rises.\n"
    "Some owners pushed prices up in May. Others took a sharp turn toward cheaper blends.\n"
    "The stage is set for more increases. Retail prices may stay high.\n"
)
PHRASES3 = [{"phrase": "pushed prices up", "word_count": 3}, {"phrase": "took a sharp turn", "word_count": 4},
            {"phrase": "time lag", "word_count": 2}]


def _sha(o) -> str:
    return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _sha_s(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------
# 共通fake
# ------------------------------------------------------------------
def selector_seq(seq):
    """seq=attemptごとの応答(list=items / str=生出力 / Exception)。returns (make_call_fn, state)。"""
    state = {"n": 0, "messages": []}

    def make_call_fn(msg):
        state["messages"].append(msg)

        def fn():
            i = min(state["n"], len(seq) - 1)
            state["n"] += 1
            r = seq[i]
            if isinstance(r, Exception):
                raise r
            raw = r if isinstance(r, str) else json.dumps({"items": r}, ensure_ascii=False)
            return raw, "gpt-6-luna", f"resp{state['n']}"
        return fn
    return make_call_fn, state


def _parse_items_json(user_message: str, marker: str) -> list:
    tail = user_message.split(marker, 1)[1]
    dec = json.JSONDecoder()
    obj, _ = dec.raw_decode(tail.lstrip())
    return obj


def fake_canon_factory(overrides=None, record=None, reason_default="none"):
    """kc.make_canonicalization_fn の差し替え。overrides={rank: (key_phrase, normalization_reason)}。"""
    overrides = overrides or {}

    def factory(user_message, **kw):
        if record is not None:
            record.append(kw)
        items = _parse_items_json(user_message, "【Key Phrase候補(JSON)】\n")
        out = []
        for it in items:
            kp, reason = overrides.get(it["rank"], (it["display_phrase"], reason_default))
            row = {"rank": it["rank"], "key_phrase": kp, "changed_from_display_phrase": kp != it["display_phrase"],
                   "normalization_reason": reason, "reasoning": "r"}
            for f in kc.QA_FIELDS:
                row[f] = "PASS"
            out.append(row)

        def fn():
            return json.dumps({"items": out}, ensure_ascii=False), "gpt-6-luna", "canon_resp"
        return fn
    return factory


def fake_gloss_factory(record=None):
    def factory(msg, **kw):
        if record is not None:
            record.append(msg)
        targets = _parse_items_json(msg, "【対象項目】\n")
        out = [{"rank": t["rank"], "current_gloss_consistent": False, "japanese_gloss": f"意味{'一二三四五'[t['rank'] - 1]}",
                "qa_reflects_all_key_phrase_words": "PASS", "reasoning": "r", "added_word_mappings": []} for t in targets]

        def fn():
            return json.dumps({"items": out}, ensure_ascii=False), "gpt-6-luna", "gloss_resp"
        fn.last_usage = None
        return fn
    return factory


def fake_red_factory(status_seq=None):
    seq = list(status_seq or [])

    def factory(msg, **kw):
        ranks = [int(x) for x in re.findall(r'"rank": (\d+)', msg.split("【Key Phrase", 1)[1])]
        import itertools
        dup = (seq.pop(0) if seq else "PASS") == "NG"
        pairs = [{"rank_a": a, "rank_b": b, "meaning_overlap": "PASS", "usage_context_overlap": "PASS",
                  "grammatical_teaching_value_overlap": "PASS", "conceptual_role_overlap": "PASS",
                  "is_near_duplicate": bool(dup and (a, b) == (1, 2)), "reasoning": "r"}
                 for a, b in itertools.combinations(sorted(ranks), 2)]

        def fn():
            return json.dumps({"pairs": pairs}), "gpt-6-luna", "red_resp"
        return fn
    return factory


class _Patched(unittest.TestCase):
    """telemetryの書込先を一時dirへ隔離する(Production telemetryを汚さない)。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        p = mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", os.path.join(self.tmp, "telemetry.jsonl"))
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(self._tmp.cleanup)


# ==================================================================
# P-04 基本形化validator(誤受理防止)
# ==================================================================
class TestInflectionValidator(unittest.TestCase):
    ACCEPT = [
        ("push prices up", "pushed prices up"), ("take a sharp turn", "took a sharp turn"),
        ("give back", "gave back some gains"), ("pump one's fist", "pumps its fist"), ("hand the baton", "hands the baton"),
        ("keep prices low", "kept prices low"), ("raw material", "raw materials"), ("hold the line", "held the line"),
        ("be through", "been through"),
    ]
    REJECT = [
        ("mix feelings", "mixed feelings"), ("heat debate", "heated debate"), ("new", "news"), ("good", "goods"),
        ("mean", "means"), ("sale tax", "sales tax"), ("saving account", "savings account"),
        ("raise concern", "raised concerns"),                 # V+名詞は形容詞/名詞修飾と区別できないため基本形化しない(範囲縮小)
        ("rise price", "rising prices"), ("raw materials", "raw beans"), ("push prices up", "took prices up"),
        ("up push prices", "pushed prices up"),               # 並べ替え
        ("push prices up quickly", "pushed prices up"),       # 語の追加
        ("left side", "left side"),                           # 無変更は本validatorの対象外(別経路で受理)
        ("leave side", "left side"),                          # left=分詞/方向の曖昧語+直後が名詞
        ("hand baton", "hands the baton"),                    # 語の削除
    ]

    def test_accept_table(self):
        for k, d in self.ACCEPT:
            with self.subTest(k=k, d=d):
                self.assertTrue(ft.is_valid_inflection_normalization(k, d))

    def test_reject_table(self):
        for k, d in self.REJECT:
            with self.subTest(k=k, d=d):
                self.assertFalse(ft.is_valid_inflection_normalization(k, d))

    def test_plural_only_on_last_token_and_exclusion_table(self):
        self.assertFalse(ft.is_valid_inflection_normalization("price rise", "prices rise"))   # 句末以外の単数化は不可
        for w in ("news", "goods", "means", "arms", "glasses", "savings", "earnings", "odds", "terms", "clothes", "series",
                  "species", "headquarters", "belongings"):
            self.assertIn(w, ft._PLURAL_EXCLUDE)

    def test_be_have_do_family_in_irregular_table(self):
        for w, base in (("is", "be"), ("are", "be"), ("was", "be"), ("were", "be"), ("been", "be"),
                        ("has", "have"), ("had", "have"), ("does", "do"), ("did", "do")):
            self.assertEqual(ft._FUNCTION_VERB_FORMS[w], base)


# ==================================================================
# P-02 canonicalization(fulltext専用schema/enum・validator・QA effective verdict)
# ==================================================================
def _fulltext_original(rank, display, **kw):
    it = {"rank": rank, "display_phrase": display, "source_span": display, "source_sentence": f"They {display} today.",
          "ja_gloss": None, "japanese_gloss": None, "fulltext_source_ref": ft.FULLTEXT_SOURCE_REF_ID,
          "source_sentence_id": f"S{rank}", "selection_resolution_method": "fulltext_exact_unique", "occurrence_count": 1,
          "occurrence_sentence_ids": [f"S{rank}"], "declared_word_count_mismatch": False}
    it.update(kw)
    return it


def _canon_row(rank, key, reason, **qa):
    row = {"rank": rank, "key_phrase": key, "changed_from_display_phrase": True, "normalization_reason": reason, "reasoning": "r"}
    for f in kc.QA_FIELDS:
        row[f] = qa.get(f, "PASS")
    return row


class TestCanonicalizationFulltext(unittest.TestCase):
    def test_shared_schema_and_enum_byte_identical_to_pre_change(self):
        # 委任_02着手前(HEAD)の値を固定。A/B/Cへ送るschemaが変わらないこと(OF-KPFT-P-02(1))。
        self.assertEqual(_sha(kc.CANONICALIZATION_JSON_SCHEMA), "1daac9087339ebf341692f1860763319aabe0e48a3f6eedd778d6355e578e88a")
        self.assertEqual(_sha(list(kc.NORMALIZATION_REASONS)), "fd341920a0833ace1de4f299e3c920b70da496c9e55e178f587dec8841f2056c")
        self.assertNotIn("lemma_normalization", kc.NORMALIZATION_REASONS)

    def test_fulltext_schema_adds_only_lemma_normalization(self):
        enum = kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT["schema"]["properties"]["items"]["items"]["properties"]["normalization_reason"]["enum"]
        self.assertIn("lemma_normalization", enum)
        self.assertEqual(set(enum) - {"lemma_normalization"}, set(kc.NORMALIZATION_REASONS))
        a = json.loads(json.dumps(kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT))
        b = json.loads(json.dumps(kc.CANONICALIZATION_JSON_SCHEMA))
        a["schema"]["properties"]["items"]["items"]["properties"]["normalization_reason"]["enum"] = None
        b["schema"]["properties"]["items"]["items"]["properties"]["normalization_reason"]["enum"] = None
        a["name"] = b["name"] = None
        self.assertEqual(a, b)   # enum以外は共有schemaと同一

    def test_lemma_accepted_for_fulltext_item_and_qa_traceable_not_review_required(self):
        orig = [_fulltext_original(1, "pushed prices up")]
        # 実LLMはqa_traceable_contiguous_spanをFAILと自己申告しうる(基本形化は表層形と一致しないため)
        parsed = {"items": [_canon_row(1, "push prices up", "lemma_normalization", qa_traceable_contiguous_span="FAIL")]}
        v = kc.validate_canonicalization_response(parsed, orig)
        self.assertEqual(v["status"], "CANONICALIZATION_PASS", v)

    def test_lemma_rejected_for_abc_item_without_marker(self):
        orig = [{"rank": 1, "display_phrase": "pushed prices up", "source_span": "pushed prices up", "source_sentence": "s"}]
        parsed = {"items": [_canon_row(1, "push prices up", "lemma_normalization")]}
        v = kc.validate_canonicalization_response(parsed, orig)
        self.assertEqual(v["status"], "CANONICALIZATION_INVALID")   # 共有enumに無く、Rule7でも拒否(A/B/C不変)

    def test_invalid_lemma_remains_invalid(self):
        orig = [_fulltext_original(1, "heated debate"), _fulltext_original(2, "raw beans")]
        parsed = {"items": [_canon_row(1, "heat debate", "lemma_normalization"), _canon_row(2, "raw materials", "lemma_normalization")]}
        v = kc.validate_canonicalization_response(parsed, orig)
        self.assertEqual(v["status"], "CANONICALIZATION_INVALID")
        self.assertEqual(sorted(r["rank"] for r in v["item_reasons"]), [1, 2])

    def test_contiguous_range_plus_lemma_accepted(self):
        # gave back some gains -> give back(display中の連続範囲+1対1の基本形化。P-02(3))
        orig = [_fulltext_original(1, "gave back some gains")]
        for reason in ("lemma_normalization", "generalize_person_dependent_reference"):   # 同時発生ではどちらのreasonでも受理(P-02(4))
            parsed = {"items": [_canon_row(1, "give back", reason)]}
            self.assertEqual(kc.validate_canonicalization_response(parsed, orig)["status"], "CANONICALIZATION_PASS", reason)

    def test_lemma_and_person_generalization_together(self):
        orig = [_fulltext_original(1, "pumps its fist")]
        for reason in ("lemma_normalization", "generalize_person_dependent_reference"):
            parsed = {"items": [_canon_row(1, "pump one's fist", reason)]}
            self.assertEqual(kc.validate_canonicalization_response(parsed, orig)["status"], "CANONICALIZATION_PASS", reason)

    def test_object_pronoun_kept_accepted_but_generalized_rejected(self):
        # JRE 委任_02: 目的格him->someoneは閉じた人称表外(却下)、himを残した基本形化は受理(template是正後に期待される出力)。
        orig = [_fulltext_original(1, "sentenced him to death")]
        ok = {"items": [_canon_row(1, "sentence him to death", "lemma_normalization")]}
        ng = {"items": [_canon_row(1, "sentence someone to death", "generalize_person_dependent_reference")]}
        self.assertEqual(kc.validate_canonicalization_response(ok, orig)["status"], "CANONICALIZATION_PASS")
        self.assertEqual(kc.validate_canonicalization_response(ng, orig)["status"], "CANONICALIZATION_INVALID")

    def test_other_reason_does_not_unlock_lemma(self):
        orig = [_fulltext_original(1, "pushed prices up")]
        parsed = {"items": [_canon_row(1, "push prices up", "other")]}
        self.assertEqual(kc.validate_canonicalization_response(parsed, orig)["status"], "CANONICALIZATION_INVALID")

    def test_effective_verdict_only_for_valid_normalization(self):
        f = kc._qa_field_effective_verdict
        self.assertEqual(f("qa_traceable_contiguous_span", "FAIL", "push prices up", "pushed prices up", "lemma_normalization", fulltext=True), "PASS")
        self.assertEqual(f("qa_traceable_contiguous_span", "FAIL", "push prices up", "pushed prices up", "lemma_normalization", fulltext=False), "FAIL")
        self.assertEqual(f("qa_traceable_contiguous_span", "FAIL", "heat debate", "heated debate", "lemma_normalization", fulltext=True), "FAIL")
        self.assertEqual(f("qa_core_meaning_preserved", "FAIL", "push prices up", "pushed prices up", "lemma_normalization", fulltext=True), "FAIL")

    def test_fulltext_template_has_lemma_rule_and_no_5_or_listening_blocker_ranking(self):
        t = kc.load_prompt_template(kc.FULLTEXT_PROMPT_TEMPLATE_PATH)
        self.assertIn("lemma_normalization", t)
        self.assertNotIn("5件の順位", t)
        self.assertNotIn("Listening Blocker Ranking", t)
        self.assertIn("{article_text}", t)
        self.assertIn("{items_json}", t)
        # JRE 委任_02(Z melos runtime evidence): LLMが目的格him等をsomeoneへ過剰一般化→決定論validator却下→外側retry尽きた事象の是正。
        self.assertIn("目的格", t)
        self.assertIn("そのまま残してください", t)
        # 旧templateはA/B/C用に無変更(git blob hashで固定)
        old = open(os.path.join(ROOT, kc.PROMPT_TEMPLATE_PATH), "rb").read().replace(b"\r\n", b"\n")
        self.assertEqual(hashlib.sha1(b"blob %d\0" % len(old) + old).hexdigest(), "6e19a90557b8512a0f3727cfa4547663df873ea4")


# ==================================================================
# P-01 / P-06 選定 -> merge -> 生成対象/消費側(統合)
# ==================================================================
class TestSelectionToMergeIntegration(unittest.TestCase):
    def _select(self, phrases=None):
        mk, _ = selector_seq([phrases or PHRASES3])
        return ft.run_selection_gate(ARTICLE, mk, sleep_fn=lambda s: None)

    def test_original_items_use_selection_resolution_method_not_resolution_method(self):
        gate = self._select()
        self.assertEqual(gate["status"], "KEY_WORDS_STRUCTURE_PASS")
        for it in gate["items"]:
            self.assertIn("selection_resolution_method", it)
            self.assertNotIn("resolution_method", it)   # P-06: Z D1 gateが`exact`で上書きする同名フィールドとの衝突を避ける

    def test_merge_carries_fulltext_fields_and_downstream_selectors_fire(self):
        gate = self._select()
        orig = gate["items"]
        canon = [_canon_row(i["rank"], i["display_phrase"], "none") for i in orig]
        merged = kc.merge_canonicalization_result(orig, canon)
        for it in merged["items"]:
            for f in kc.FULLTEXT_PASSTHROUGH_FIELDS:
                self.assertIn(f, it, f)
            self.assertEqual(it["fulltext_source_ref"], ft.FULLTEXT_SOURCE_REF_ID)
        # gloss生成対象: 全件(glossが無い)
        self.assertEqual([t["rank"] for t in ga.select_generation_targets(merged["items"])], [1, 2, 3])
        # 消費側: glossを作る前のartifactはTTS/組立へ進めない
        self.assertEqual([t["rank"] for t in ga.select_consumer_unevaluated(merged["items"])], [1, 2, 3])
        self.assertEqual(len(ga.collect_unevaluated(merged)), 3)

    def test_merge_without_marker_is_unchanged_for_abc(self):
        orig = [{"rank": 1, "display_phrase": "take a stand", "source_span": "took a stand", "source_sentence": "s", "ja_gloss": "立場をとる"}]
        merged = kc.merge_canonicalization_result(orig, [_canon_row(1, "take a stand", "none")])
        self.assertNotIn("fulltext_source_ref", merged["items"][0])
        self.assertNotIn("source_sentence_id", merged["items"][0])

    def test_kill_switch_off_does_not_let_glossless_fulltext_items_through(self):
        gate = self._select()
        merged = kc.merge_canonicalization_result(gate["items"], [_canon_row(i["rank"], i["display_phrase"], "none") for i in gate["items"]])
        with mock.patch.object(ga, "GLOSS_ALIGNMENT_ENABLED", False):
            self.assertEqual(len(ga.collect_unevaluated(merged)), 3)   # X/Zではkill switch OFFは実質『停止スイッチ』
            abc = {"items": [{"rank": 1, "key_phrase": "x", "display_phrase": "x", "japanese_gloss": "x"}]}
            self.assertEqual(ga.collect_unevaluated(abc), [])           # A/B/Cは従来どおり(OFF時は評価対象外)

    def test_gloss_present_clears_consumer_stop(self):
        it = {"rank": 1, "key_phrase": "push prices up", "display_phrase": "push prices up", "japanese_gloss": "価格を押し上げる",
              "fulltext_source_ref": "fulltext_exact_v1", "gloss_alignment_status": "ALIGNED"}
        self.assertEqual(ga.select_consumer_unevaluated([it]), [])


# ==================================================================
# P-07 / P-10 / P-13 選定gate
# ==================================================================
class TestSelectionGate(unittest.TestCase):
    def test_prompt_2_text_unchanged_sha_and_prefix_in_every_attempt(self):
        self.assertEqual(ft.PROMPT_2_SHA256, PROMPT_2_SHA)
        mk, st = selector_seq([[{"phrase": "not in article", "word_count": 3}], PHRASES3])
        g = ft.run_selection_gate(ARTICLE, mk, sleep_fn=lambda s: None)
        self.assertEqual(g["status"], "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(len(st["messages"]), 2)
        for m in st["messages"]:
            self.assertTrue(m.startswith(ft.PROMPT_2_TEXT + ft.BODY_DELIMITER))   # Prompt 2本文は毎attempt一字も変わらない
            self.assertEqual(m.split(ft.BODY_DELIMITER, 1)[0], ft.PROMPT_2_TEXT)

    def test_second_attempt_gets_machine_diagnostic_note_after_body_only(self):
        mk, st = selector_seq([[{"phrase": "not in article", "word_count": 3}, PHRASES3[0], PHRASES3[2]], PHRASES3])
        ft.run_selection_gate(ARTICLE, mk, sleep_fn=lambda s: None)
        m1, m2 = st["messages"]
        self.assertNotIn(ft.NOTE_DELIMITER, m1)
        self.assertIn(ft.NOTE_DELIMITER, m2)
        self.assertTrue(m2.startswith(m1))                      # note=本文の後ろに後置(前半は初回と同一)
        note = m2.split(ft.NOTE_DELIMITER, 1)[1]
        self.assertIn("not in article", note)
        self.assertIn("本文に連続一致しない", note)

    def test_technical_failure_sleeps_before_retry(self):
        sleeps = []
        mk, st = selector_seq([RuntimeError("net"), PHRASES3])
        g = ft.run_selection_gate(ARTICLE, mk, sleep_fn=sleeps.append)
        self.assertEqual(g["status"], "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(sleeps, [2])

    def test_exhaustion_is_fail_closed_no_items(self):
        mk, _ = selector_seq([[{"phrase": "nope one", "word_count": 2}]])
        g = ft.run_selection_gate(ARTICLE, mk, sleep_fn=lambda s: None)
        self.assertEqual(g["status"], "KEY_WORDS_STRUCTURE_INVALID")
        self.assertIsNone(g["items"])
        self.assertEqual(len(g["attempts_detail"]), ft.MAX_ATTEMPTS)

    def test_sentence_boundary_reason_is_distinct(self):
        mk, _ = selector_seq([[{"phrase": "slowly Cafes keep", "word_count": 3}]])
        g = ft.run_selection_gate(ARTICLE, mk, sleep_fn=lambda s: None)
        reasons = " ".join(r for ir in g["attempts_detail"][0]["item_reasons"] for r in ir["reasons"])
        self.assertIn("文の境界をまたいでいる", reasons)

    def test_schema_has_no_array_size_constraints(self):
        arr = ft.SELECTOR_JSON_SCHEMA["schema"]["properties"]["items"]
        self.assertNotIn("minItems", arr)
        self.assertNotIn("maxItems", arr)   # 件数はローカル検証のみ(P-10: strictモードのschema拒否で全呼出が止まる事故を避ける)

    def test_http_400_is_config_error_not_retried(self):
        class BadRequestError(Exception):
            status_code = 400

        class _Resp:
            def create(self, **kw):
                raise BadRequestError("schema rejected")

        class _Client:
            responses = _Resp()

        calls = {"n": 0}

        def make(msg):
            calls["n"] += 1
            return ft.make_selector_fn(msg, client=_Client(), model="gpt-6-luna")
        with self.assertRaises(ft.FulltextSelectionError):
            ft.run_selection_gate(ARTICLE, make, sleep_fn=lambda s: None)
        self.assertEqual(calls["n"], 1)   # retryしない(即停止)

    def test_raw_outputs_saved_per_attempt(self):
        with tempfile.TemporaryDirectory() as d:
            mk, _ = selector_seq([[{"phrase": "not in article", "word_count": 3}], PHRASES3])
            ft.run_fulltext_selection(ARTICLE, d, "a1", "B1", make_call_fn=mk, sleep_fn=lambda s: None)
            raw = json.load(open(f"{d}/keywords_selector_raw_attempts.json", encoding="utf-8"))
            self.assertEqual([r["attempt"] for r in raw], [1, 2])
            self.assertIn("not in article", raw[0]["raw_text"])
            self.assertTrue(os.path.exists(f"{d}/keywords_selector_prompt_attempt2.txt"))
            meta = json.load(open(f"{d}/keywords_runtime_metadata.json", encoding="utf-8"))
            self.assertEqual(meta["prompt_sha256"], PROMPT_2_SHA)
            self.assertEqual(meta["kp_backend_used"], "fulltext_p2")

    def test_numeric_placeholder_precheck_rejects_and_names_reason(self):
        for bad in ("up 5 percent", "rose 3%", "up by percent", "about ~ percent", "so much…"):
            self.assertTrue(ft.numeric_placeholder_reasons(bad), bad)
        for ok in ("pushed prices up", "time lag", "up by half"):
            self.assertEqual(ft.numeric_placeholder_reasons(ok), [], ok)
        art = "Prices rose 3% last year. Owners pushed prices up in May.\n"
        mk, st = selector_seq([[{"phrase": "rose 3%", "word_count": 2}], [{"phrase": "pushed prices up", "word_count": 3}]])
        g = ft.run_selection_gate(art, mk, sleep_fn=lambda s: None)
        self.assertEqual(g["status"], "KEY_WORDS_STRUCTURE_PASS")
        self.assertIn("数値placeholder型の回避", st["messages"][1].split(ft.NOTE_DELIMITER, 1)[1])   # retry noteに理由が載る

    def test_up_to_three_and_shortfall_recorded(self):
        mk, _ = selector_seq([PHRASES3[:2]])
        g = ft.run_selection_gate(ARTICLE, mk, sleep_fn=lambda s: None)
        self.assertEqual(len(g["items"]), 2)
        self.assertTrue(g["shortfall"])
        mk, _ = selector_seq([PHRASES3 + [{"phrase": "spike at once", "word_count": 3}]])
        self.assertNotEqual(ft.run_selection_gate(ARTICLE, mk, sleep_fn=lambda s: None)["status"], "KEY_WORDS_STRUCTURE_PASS")


# ==================================================================
# Q6 gloss生成(拡張)
# ==================================================================
class TestGlossGeneration(unittest.TestCase):
    def _merged(self, n=3):
        mk, _ = selector_seq([PHRASES3[:n]])
        gate = ft.run_selection_gate(ARTICLE, mk, sleep_fn=lambda s: None)
        return kc.merge_canonicalization_result(gate["items"], [_canon_row(i["rank"], i["display_phrase"], "none") for i in gate["items"]])

    def test_new_generation_message_and_numeric_rule_only_for_fulltext(self):
        merged = self._merged()
        targets = ga.select_generation_targets(merged["items"])
        pf = ga.preflight(True)
        msg = ga.build_user_message_corrected(targets, ARTICLE, pf["rules_fulltext"])
        self.assertIn("新規生成の規則", msg)
        self.assertIn("数値を補わないと意味が成立しない句", msg)          # P-13: 旧template:15をgloss規則の抽出対象に含める
        abc_t = [{"rank": 1, "key_phrase": "push prices up", "display_phrase": "push prices up", "japanese_gloss": "価格を押し上げる", "source_sentence": "s"}]
        msg_abc = ga.build_user_message_corrected(abc_t, "ARTICLE", pf["rules"])
        self.assertNotIn("新規生成の規則", msg_abc)
        self.assertEqual(_sha_s(msg_abc.replace("ARTICLE", "ARTICLE")), "df113b4438c98fff2cd02aee906875fec644ad0bf1dc50329279b5aa0574bb4c")

    def test_abc_gloss_rules_and_schema_byte_identical_to_pre_change(self):
        self.assertEqual(_sha_s(ga.load_approved_gloss_rules()), "447e07cb8b9a30850a8dc75b6c3cce48c53d99b5f1fafa88d19b778d9155949b")
        self.assertEqual(_sha(ga.GLOSS_ALIGNMENT_JSON_SCHEMA), "c41959bd37337255f94df762f2b593c4057475901d02cb92a49ad41e9bd954c2")
        self.assertNotEqual(ga.load_approved_gloss_rules(include_numeric_rule=True), ga.load_approved_gloss_rules())

    def test_validate_item_skips_contradiction_only_for_new_generation(self):
        t = ga.select_generation_targets(self._merged(1)["items"])[0]
        resp = {"rank": 1, "current_gloss_consistent": True, "japanese_gloss": "価格を押し上げる",
                "qa_reflects_all_key_phrase_words": "PASS", "reasoning": "r", "added_word_mappings": []}
        v = ga.validate_item_corrected(resp, t)
        self.assertTrue(v["valid"], v["reasons"])      # current無し=新規生成: 真偽とcurrentの矛盾判定は適用しない
        self.assertEqual(v["adopt_gloss"], "価格を押し上げる")
        bad = dict(resp, japanese_gloss="価格(を)押し上げる")
        self.assertFalse(ga.validate_item_corrected(bad, t)["valid"])     # 括弧禁止など他の検査は全て適用
        abc = {"rank": 1, "key_phrase": "x y", "display_phrase": "x y", "japanese_gloss": "あ", "source_sentence": "s"}
        r2 = dict(resp, current_gloss_consistent=True, japanese_gloss="い")
        self.assertFalse(ga.validate_item_corrected(r2, abc)["valid"])    # A/B/Cの矛盾判定は従来どおり

    def test_align_glosses_generates_for_all_items_with_fake_llm(self):
        merged = self._merged(3)
        rec = []
        out = ga.align_glosses(merged, ARTICLE, lambda msg: fake_gloss_factory(rec)(msg), enabled=True)
        self.assertEqual(out["status"], "ALIGN_PASS")
        self.assertEqual(out["targets"], [1, 2, 3])
        for it in out["merged"]["items"]:
            self.assertTrue(it["japanese_gloss"])
            self.assertEqual(it["gloss_alignment_status"], "ALIGNED")
        self.assertEqual(ga.select_consumer_unevaluated(out["merged"]["items"]), [])
        self.assertEqual(len(rec), 1)   # 全3 itemを1 batch callで生成


# ==================================================================
# 配線: scaffold(全文選定backend)・外側retry(P-07/P-08)・A/B/C不変
# ==================================================================
class TestScaffoldFulltextPipeline(_Patched):
    def _run(self, seq, **kw):
        mk, st = selector_seq(seq)
        calls = {"n": 0}

        def sel_fn(msg, **kw2):
            calls["n"] += 1
            return mk(msg)
        patches = [mock.patch.object(ft, "make_selector_fn", sel_fn),
                   mock.patch.object(kc, "make_canonicalization_fn", fake_canon_factory(kw.get("canon_overrides"), kw.get("canon_rec"))),
                   mock.patch.object(ga, "make_alignment_fn", fake_gloss_factory(kw.get("gloss_rec"))),
                   mock.patch.object(rq, "make_redundancy_qa_fn", fake_red_factory(kw.get("red_seq"))),
                   mock.patch("time.sleep", lambda s: None)]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        d = os.path.join(self.tmp, kw.get("sub", "kp"))
        res = sc.run_key_phrases(ARTICLE, d, "aid", "B1", process="B1_SUPPORT", kp_backend="fulltext_p2", stop_run_dir=self.tmp)
        return d, res, st

    def test_end_to_end_three_items_to_final_artifact(self):
        d, res, st = self._run([PHRASES3], canon_overrides={1: ("push prices up", "lemma_normalization"), 2: ("take a sharp turn", "lemma_normalization")})
        self.assertNotIn("status", res)   # 成功時はtop-level statusなし(既存契約)
        self.assertEqual(res["selection"]["kp_backend_used"], "fulltext_p2")
        doc = json.load(open(f"{d}/keywords_canonicalized.json", encoding="utf-8"))
        self.assertEqual([it["used_form"] for it in doc["items"]], ["push prices up", "take a sharp turn", "time lag"])
        self.assertEqual([it["display_phrase"] for it in doc["items"]], ["pushed prices up", "took a sharp turn", "time lag"])   # 表層形は証跡として残る
        for it in doc["items"]:
            self.assertTrue(it["japanese_gloss"])
            self.assertEqual(it["gloss_alignment_status"], "ALIGNED")
            self.assertEqual(it["fulltext_source_ref"], "fulltext_exact_v1")
        # canonicalization入力=fulltext template
        self.assertIn("lemma_normalization", open(f"{d}/canonicalization_prompt.txt", encoding="utf-8").read())
        meta = json.load(open(f"{d}/canonicalization_runtime_metadata.json", encoding="utf-8"))
        self.assertEqual(meta["template"], "fulltext_p2")
        # 選定prompt=Prompt 2逐語
        sent = open(f"{d}/keywords_selector_prompt.txt", encoding="utf-8").read()
        self.assertTrue(sent.startswith(ft.PROMPT_2_TEXT + ft.BODY_DELIMITER))

    def test_canonicalization_uses_fulltext_schema_only_for_fulltext_items(self):
        rec = []
        self._run([PHRASES3], canon_rec=rec)
        self.assertIs(rec[0].get("schema"), kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT)

    def test_one_and_two_item_fixtures_flow_without_five_item_assumption(self):
        for n in (1, 2, 3):
            with self.subTest(n=n):
                d, res, _ = self._run([PHRASES3[:n]], sub=f"kp{n}")
                doc = json.load(open(f"{d}/keywords_canonicalized.json", encoding="utf-8"))
                self.assertEqual([it["rank"] for it in doc["items"]], list(range(1, n + 1)))
                self.assertEqual(res["selection"]["shortfall"], n < 3)
                red = json.load(open(f"{d}/keyphrase_redundancy_qa.json", encoding="utf-8"))
                self.assertEqual(red["status"], "REDUNDANCY_PASS")
                if n == 1:
                    self.assertEqual(red.get("skipped"), "ペアが無い(KP件数が2未満)")   # 1件ではRedundancy QAを呼ばない(API 0)

    def test_selection_invalid_twice_then_pass_counts_inside_outer_budget(self):
        bad = [{"phrase": "not in article", "word_count": 3}]
        # 外側1回目: 選定2attempt(bad,bad)でINVALID / 外側2回目: 成功
        d, res, st = self._run([bad, bad, PHRASES3])
        self.assertNotIn("status", res)
        self.assertEqual(len(res["outer_retry_log"]), 2)
        self.assertEqual(res["outer_retry_log"][0]["selection_status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_selection_failure_exhausts_outer_budget_and_retires_stale_artifact(self):
        bad = [{"phrase": "not in article", "word_count": 3}]
        d = os.path.join(self.tmp, "kp_exh")
        os.makedirs(d)
        open(f"{d}/keywords_canonicalized.json", "w", encoding="utf-8").write('{"items": [{"rank": 1, "note": "old"}]}')   # 旧attempt/旧runの残骸
        mk, _ = selector_seq([bad])
        with mock.patch.object(ft, "make_selector_fn", lambda msg, **kw: mk(msg)), mock.patch("time.sleep", lambda s: None):
            res = sc.run_key_phrases(ARTICLE, d, "aid", "B1", process="B1_SUPPORT", kp_backend="fulltext_p2", stop_run_dir=self.tmp)
        self.assertEqual(res["status"], "OUTER_RETRY_EXHAUSTED")
        self.assertIsNone(res["canonicalization"])
        self.assertEqual(len(res["outer_retry_log"]), sc.KP_OUTER_RETRY_MAX)
        self.assertFalse(os.path.exists(f"{d}/keywords_canonicalized.json"), "旧KPを本名で残さない(KPMP B1の恒久修正)")
        self.assertTrue(os.path.exists(f"{d}/keywords_canonicalized.STALE_attempt3.json"))

    def test_canonicalization_invalid_exhaustion_retires_artifact_from_earlier_attempt(self):
        # 外側1回目でcanonicalization成功+Redundancy NG -> 2,3回目でcanonicalization INVALID連続 => 最終失敗。1回目のartifactは本名で残らない
        d = os.path.join(self.tmp, "kp_c")
        calls = {"n": 0}
        ok_f, bad_f = fake_canon_factory(), fake_canon_factory({1: ("totally different", "none")})

        def canon_factory(um, **kw):   # 1回目のcanonicalizationだけPASS、以降は常にINVALID(本文に無い語)
            calls["n"] += 1
            return (ok_f if calls["n"] == 1 else bad_f)(um, **kw)
        mk, _ = selector_seq([PHRASES3])
        with mock.patch.object(ft, "make_selector_fn", lambda msg, **kw: mk(msg)), \
                mock.patch.object(kc, "make_canonicalization_fn", canon_factory), \
                mock.patch.object(ga, "make_alignment_fn", fake_gloss_factory()), \
                mock.patch.object(rq, "make_redundancy_qa_fn", fake_red_factory(["NG"])), \
                mock.patch("time.sleep", lambda s: None):
            res = sc.run_key_phrases(ARTICLE, d, "aid", "B1", process="B1_SUPPORT", kp_backend="fulltext_p2", stop_run_dir=self.tmp)
        self.assertEqual(res["status"], "OUTER_RETRY_EXHAUSTED")
        self.assertFalse(os.path.exists(f"{d}/keywords_canonicalized.json"))
        self.assertTrue([n for n in os.listdir(d) if n.startswith("keywords_canonicalized.STALE_attempt")])

    def test_stop_sentinel_checked_at_start_of_every_outer_round(self):
        d = os.path.join(self.tmp, "kp_stop")
        mk, st = selector_seq([PHRASES3])
        open(os.path.join(self.tmp, "STOP"), "w").close()
        import er062_family_z_structure_01 as zst
        with mock.patch.object(ft, "make_selector_fn", lambda msg, **kw: mk(msg)):
            with self.assertRaises(zst.FamilyZStopSentinel):
                sc.run_key_phrases(ARTICLE, d, "aid", "B1", process="B1_SUPPORT", kp_backend="fulltext_p2", stop_run_dir=self.tmp)
        self.assertEqual(st["n"], 0)   # 新規API呼出なし

    def test_outer_loop_is_not_nested_max_rounds_bounded(self):
        # Redundancy NGが続く場合の最大周回 = KEY_PHRASE_REDUNDANCY_RETRY_MAX + 1(選定失敗/canon失敗の予算とは別カウント)
        d = os.path.join(self.tmp, "kp_red")
        mk, st = selector_seq([PHRASES3])
        calls = {"red": 0}
        base = fake_red_factory(["NG", "NG", "NG", "NG"])

        def red_factory(msg, **kw):
            calls["red"] += 1
            return base(msg, **kw)
        with mock.patch.object(ft, "make_selector_fn", lambda msg, **kw: mk(msg)), \
                mock.patch.object(kc, "make_canonicalization_fn", fake_canon_factory()), \
                mock.patch.object(ga, "make_alignment_fn", fake_gloss_factory()), \
                mock.patch.object(rq, "make_redundancy_qa_fn", red_factory), mock.patch("time.sleep", lambda s: None):
            res = sc.run_key_phrases(ARTICLE, d, "aid", "B1", process="B1_SUPPORT", kp_backend="fulltext_p2", stop_run_dir=self.tmp)
        self.assertEqual(res["status"], "NG_REVIEW_REQUIRED")
        self.assertEqual(calls["red"], sc.KEY_PHRASE_REDUNDANCY_RETRY_MAX + 1)
        self.assertFalse(os.path.exists(f"{d}/keywords_canonicalized.json"))


class TestAbcUnchanged(_Patched):
    """A/B/C(kp_backend既定=strategy_l)の経路・入力・規則がバイト同一であること(27-7: 開発対象外)。"""

    def test_default_backend_still_strategy_l_in_shared_functions(self):
        self.assertEqual(inspect.signature(sc.run_key_phrase_selection).parameters["kp_backend"].default, "strategy_l")
        self.assertEqual(inspect.signature(sc.run_key_phrases).parameters["kp_backend"].default, "strategy_l")

    def test_canonicalization_template_schema_unchanged_for_abc_items(self):
        rec = []
        orig = [{"rank": 1, "display_phrase": "take a stand", "source_span": "took a stand", "source_sentence": "They took a stand.",
                 "ja_gloss": "立場をとる"}]
        with tempfile.TemporaryDirectory() as d, mock.patch.object(kc, "make_canonicalization_fn", fake_canon_factory(record=rec)), \
                mock.patch.object(ga, "make_alignment_fn", fake_gloss_factory()), mock.patch("time.sleep", lambda s: None):
            res = sc.run_key_phrase_canonicalization("They took a stand.", orig, d, "abc", process="B1_SUPPORT")
            prompt = open(f"{d}/canonicalization_prompt.txt", encoding="utf-8").read()
            meta = json.load(open(f"{d}/canonicalization_runtime_metadata.json", encoding="utf-8"))
        self.assertNotIn("schema", rec[0])            # 共有schema(既定)のまま
        self.assertNotIn("lemma_normalization", prompt)
        self.assertNotIn("template", meta)            # metadata形も不変
        self.assertEqual(res["status"], "CANONICALIZATION_PASS")

    def test_redundancy_developer_message_and_explanation_prompt_identical_for_five_items(self):
        self.assertEqual(_sha_s(rq.DEVELOPER_MESSAGE), "5ee833a945df4f118ef4c2e23d0f282214f6d05215089b7c17880b18871efb0f")
        self.assertEqual(rq.developer_message_for(5), rq.DEVELOPER_MESSAGE)
        items = [{"rank": i, "display_phrase": "p%d" % i, "source_sentence": "s%d" % i, "japanese_gloss": "g%d" % i} for i in range(1, 6)]
        self.assertEqual(_sha_s(kexp.build_explanation_user_message(items)), "3322edb0f1ee1a91266ba8785680e46682f6484def83295210762665b7a32273")

    def test_count_words_follow_actual_item_count(self):
        self.assertIn("Key Phrase 3件", rq.developer_message_for(3))
        items = [{"rank": i, "display_phrase": "p%d" % i, "source_sentence": "s", "japanese_gloss": "g"} for i in range(1, 4)]
        m = kexp.build_explanation_user_message(items)
        self.assertIn("For each of the 3 Key Phrases below", m)
        self.assertIn("x3 ]}", m)
        self.assertNotIn("x5", m)

    def test_old_selection_template_kept_as_gloss_rule_source(self):
        p = os.path.join(ROOT, ga.APPROVED_GLOSS_RULES_TEMPLATE_PATH)
        raw = open(p, "rb").read().replace(b"\r\n", b"\n")
        self.assertEqual(hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest(), "faeb182d37ef465ed34d65110c216492e5b8d11d")


# ==================================================================
# P-03 解説の対象=used_form
# ==================================================================
class TestExplanationPhrase(unittest.TestCase):
    def test_fulltext_item_uses_used_form_and_abc_uses_display_phrase(self):
        ftit = {"display_phrase": "pushed prices up", "used_form": "push prices up", "fulltext_source_ref": "fulltext_exact_v1"}
        self.assertEqual(kexp.explanation_phrase(ftit), "push prices up")
        old = {"display_phrase": "take a player off", "used_form": "take a player off"}
        self.assertEqual(kexp.explanation_phrase(old), "take a player off")
        old2 = {"display_phrase": "A", "used_form": "B"}   # マーカー無し(旧artifact/A/B/C)はdisplay_phrase(sig互換)
        self.assertEqual(kexp.explanation_phrase(old2), "A")


# ==================================================================
# X/Z配線(既定値・撤去・resume)
# ==================================================================
class TestFamilyZWiring(unittest.TestCase):
    def test_run_kp_stage_default_and_hook_use_fulltext_backend(self):
        import er026_family_z_fiction_production_runner_01 as z
        import er062_family_z_writer_01 as w
        ctx = type("C", (), {"hooks": {}})()
        self.assertIs(z._kp_fn_for_ctx(ctx), w.run_kp_with_outer_retry_fulltext)
        self.assertEqual(inspect.signature(w.run_kp_with_outer_retry_fulltext).parameters["generic_note"].default, "")   # Prompt 2逐語固定=汎用noteなし
        self.assertEqual(inspect.signature(w.run_kp_with_outer_retry).parameters["generic_note"].default, w.Z_KP_GENERIC_NOTE)
        self.assertIn("run_kp_with_outer_retry_fulltext", inspect.getsource(w.run_kp_stage))

    def test_z_fulltext_selection_receives_no_generic_note(self):
        import er062_family_z_writer_01 as w
        notes = []

        def sel(text, d, aid, lvl, process=None, diagnostic_note=None, **kw):
            notes.append(diagnostic_note)
            return {"status": "KEY_WORDS_STRUCTURE_INVALID", "parsed": None}
        with tempfile.TemporaryDirectory() as d:
            res = w.run_kp_with_outer_retry_fulltext("t", d, "a", "A2", process="A2_SUPPORT", select_fn=sel)
        self.assertEqual(res["status"], "OUTER_RETRY_EXHAUSTED")
        self.assertEqual(notes, [None, None, None])    # 3周ともPrompt 2へ汎用noteを足さない

    def test_legacy_keyphrase_stage_is_removed_with_explicit_error(self):
        import er026_family_z_fiction_production_runner_01 as z
        with self.assertRaises(z.LegacyKeyphraseStageRemoved) as cm:
            z.run_keyphrase_stage("melos", "s", "r")
        self.assertIn("FAMILY_Z_LEGACY_KEYPHRASE_STAGE_REMOVED", str(cm.exception))
        src = inspect.getsource(z.run_keyphrase_stage)
        self.assertNotIn("run_key_phrases", src)       # Strategy L/process=Noneの本体は残さない
        self.assertNotIn("process=None", src)

    def test_mock_kp_fn_is_three_items(self):
        import er026_family_z_fiction_production_runner_01 as z
        self.assertIn("[:3]", inspect.getsource(z.mock_kp_fn))

    def test_stage_kp_explanation_sig_uses_used_form_for_fulltext(self):
        import er026_family_z_fiction_production_runner_01 as z
        src = inspect.getsource(z.stage_kp)
        self.assertIn("explanation_phrase", src)
        self.assertIn("kp_backend_used", src)          # P-14: 旧5件KP再利用と区別できる表示


class TestZCheckpointPruning(unittest.TestCase):
    def _plan(self, kp):
        import er063_family_z_audio_01 as a63
        story = [{"id": "full_story_part1_c1", "voice": "narrator", "text": "Melos was angry."}]
        return a63.build_level_plan("b1b", story, "preview", {1: "c1", 2: "c2", 3: "c3"}, kp, "Title", None)

    def test_prune_by_reuse_key_not_by_rank(self):
        import er063_family_z_audio_01 as a63
        kp5 = [{"rank": i, "used_form": f"phrase {i}", "japanese_gloss": f"意味{i}", "japanese_gloss_tts": f"意味{i}"} for i in range(1, 6)]
        plan5 = self._plan(kp5)
        cached = {"segments": {}, "key_phrases": {}}
        for s in plan5:
            e = {"status": "OK", "reuse_key": a63.build_reuse_key(s), "sha256": None}
            a63._store(cached["segments"], cached["key_phrases"], s, e)
        # 再生成で3件・rank2の語句が変わった
        kp3 = [dict(kp5[0]), dict(kp5[1], used_form="other phrase"), dict(kp5[2])]
        plan3 = self._plan(kp3)
        pruned = a63.prune_cached_to_plan(cached, plan3)
        self.assertEqual(sorted(pruned["key_phrases"]), ["1", "2", "3"])        # rank4,5は新planに無い
        self.assertNotIn("english", pruned["key_phrases"]["2"])                  # rank2の旧語句(reuse_key不一致)は捨てる
        self.assertIn("english", pruned["key_phrases"]["1"])
        self.assertIn("english", pruned["key_phrases"]["3"])

    def test_provision_shell_assets_kp_count_is_required(self):
        import er063_family_z_audio_01 as a63
        self.assertIs(inspect.signature(a63.provision_shell_assets).parameters["kp_count"].default, inspect.Parameter.empty)

    def test_plan_is_rank_driven_for_one_two_three_items(self):
        for n in (1, 2, 3):
            kp = [{"rank": i, "used_form": f"phrase {i}", "japanese_gloss": f"意味{i}", "japanese_gloss_tts": f"意味{i}"} for i in range(1, n + 1)]
            plan = self._plan(kp)
            self.assertEqual(sorted({s.rank for s in plan if s.kind == "kp_en"}), list(range(1, n + 1)))


# ==================================================================
# Prompt 2の入出力形式調整(最終報告の根拠): 本文は無変更、形式は構造化出力・区切り・note後置のみ
# ==================================================================
class TestPrompt2IoAdjustmentsOnly(unittest.TestCase):
    def test_prompt_body_unchanged_and_only_io_format_added(self):
        self.assertEqual(ft.PROMPT_2_SHA256, PROMPT_2_SHA)
        msg = ft.build_user_message(ARTICLE)
        self.assertEqual(msg, ft.PROMPT_2_TEXT + "\n\n---\n\n【記事本文】\n" + ARTICLE)
        msg2 = ft.build_user_message(ARTICLE, "note")
        self.assertEqual(msg2, msg + "\n\n---\n\n【前回の選定結果に関する指摘(機械診断)】\nnote")
        self.assertTrue(ft.prompt_prefix_intact(msg2))
        self.assertFalse(ft.prompt_prefix_intact(msg.replace("3つ", "5つ", 1)))


# ==================================================================
# Dangling Reference / 5件前提の残存(X/Z到達経路)
# ==================================================================
XZ_PRODUCTION_FILES = (
    "er003_v1_n3_01_scaffold_generate.py", "er019_family_x_audio_production_runner_01.py", "er026_family_z_fiction_production_runner_01.py",
    "er062_family_z_writer_01.py", "er063_family_z_audio_01.py", "er105_kp_fulltext_selector_01.py",
)


def _read(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


class TestStaleKpClipsIgnoredByPlanDrivenGate(unittest.TestCase):
    """OF-KPFT-P-09: 同じrun dirに旧5件の kp4/kp5 音声・結果entryが残っていても、Gateは今回のplan(3件)が要求するclipだけを見る。"""

    def test_gate_checks_only_required_clips_and_ignores_stale_kp4_kp5(self):
        import json as _json
        import tempfile
        import er063_family_z_audio_01 as a63
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(f"{d}/audit")
            kp = {str(i): {"english": {"status": "OK"}, "japanese_meaning": {"status": "OK"}, "explanation": {"status": "OK"}}
                  for i in (1, 2, 3)}
            kp["4"] = {"english": {"status": "FAILED"}}   # 旧5件runの残り(不採択でも今回は無関係)
            kp["5"] = {"english": {"status": "OK"}}
            with open(f"{d}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
                _json.dump({"segments": {}, "key_phrases": kp}, f)
            req = [f"kp{i}_{k}" for i in (1, 2, 3) for k in ("en", "ja", "explanation_en")]
            r = a63.assert_tts_results_complete(d, req)
            self.assertEqual(r["checked"], 9)
            with self.assertRaises(a63.FamilyZTtsResultsIncompleteStop):   # 逆に4件目を要求すれば(旧5件plan)ちゃんと止まる
                a63.assert_tts_results_complete(d, req + ["kp4_en"])


class TestNoDanglingReferences(unittest.TestCase):
    def test_removed_identifiers_have_no_references_in_xz_production_files(self):
        removed = ("_run_key_phrase_selection_db_hybrid_with_fallback", "run_db_hybrid_selection", "KP_ARTICLE_COST_CAP", "build_m2_fallback_record",
                   "format_m2_fallback_stdout", "write_m2_fallback_notice", "M2_FALLBACK_NOTICE_FILENAME", "M2_RELATED_FALLBACK_REASON_CODES",
                   "strategy_l_fallback", "kp_backend=\"db_hybrid\"", "print_m2_fallback_final_line", "m2_fallback_events", "m2_fallback_by_level")
        for f in XZ_PRODUCTION_FILES:
            src = _read(f)
            for ident in removed:
                with self.subTest(file=f, ident=ident):
                    self.assertFalse(ident in src, f"{f}:{ident}")

    def test_xz_default_kp_backend_has_no_db_hybrid_default(self):
        for f in ("er019_family_x_audio_production_runner_01.py", "er026_family_z_fiction_production_runner_01.py", "er062_family_z_writer_01.py"):
            self.assertNotRegex(_read(f), r'kp_backend\s*[:=]\s*(?:str\s*=\s*)?"db_hybrid"')

    def test_no_five_item_constants_reachable_from_xz(self):
        # X/Z到達経路(全文選定backend)の件数は er105.KP_COUNT_MAX(=3)だけが置き場。旧5件定数をX/Zモジュールがimport/参照しない。
        for f in ("er019_family_x_audio_production_runner_01.py", "er026_family_z_fiction_production_runner_01.py",
                  "er062_family_z_writer_01.py", "er063_family_z_audio_01.py", "er105_kp_fulltext_selector_01.py"):
            src = _read(f)
            self.assertFalse(re.search(r"^\s*(?:import|from) er003_key_words_production", src, re.M), f)
            self.assertNotRegex(src, r"key_phrase_role", f)   # 4+1(Topic枠)はX/Zに存在しない
        self.assertEqual(ft.KP_COUNT_MAX, 3)

    def test_no_production_file_other_than_wiring_imports_er105_unexpectedly(self):
        # er105はscaffold(新backend委譲)・canonicalization(基本形化validator)からのみimportされる
        allowed = {"er003_v1_n3_01_scaffold_generate.py", "er003_key_words_canonicalization.py", "er105_kp_fulltext_selector_01.py"}
        for f in sorted(os.listdir(ROOT)):
            if f.endswith(".py") and re.match(r"er0\d\d_", f) and "test" not in f and f not in allowed:
                src = _read(f)
                self.assertFalse("import er105_kp_fulltext_selector_01" in src, f)


if __name__ == "__main__":
    unittest.main()
