# -*- coding: utf-8 -*-
"""X2p'(本文での語義を確定してから訳す方式)のProduction新規生成経路のtest(WC-01〜WC-12)。
FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_35(2026-10-24、UDR #179 APPROVED_FOR_PRODUCTION、XYZ共通)。
設計正本=docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/WIRING_DESIGN_07.md。JPY0・実API呼出なし(LLMはFake)。
Productionはer112(DEV/Trial)をimportしない。golden fixture(DEV build_x_message06の出力)はtest側にcommit済み(WIRING_35/)。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import unittest
from types import SimpleNamespace

import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga

REPO = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(REPO, "docs", "research", "FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01", "WIRING_35",
                      "golden_dev_x06_messages_01.json")

# 変更前(HEAD)の既存定数のsha256(不変性の固定。WC-01)
SHA_DEVELOPER = "e75e9dc5464fdc5e2a35db2a675ae7e7e5db5aacc99eb06a06bdc1268c68f3cb"
SHA_SCHEMA = "c41959bd37337255f94df762f2b593c4057475901d02cb92a49ad41e9bd954c2"
SHA_NEWGEN_TEXT = "9bd1ec21b3863e8d424356881670ea2b7d7078198680dda3b8306e6f2eb9914b"
SHA_PERSON_TEXT = "920e22b220671a711521addcb526240f6e578f0dc0b343fba9f438b567a73eee"

OLD_CLAUSE_1 = "他の文脈でも再利用できる"
OLD_CLAUSE_2 = "辞書に複数の語義がある表現で"


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _new_item(rank, kp, sentence="x", disp=None, reason=None):
    d = {"rank": rank, "display_phrase": disp or kp, "key_phrase": kp, "used_form": kp, "japanese_gloss": None,
         "source_sentence": sentence, "fulltext_source_ref": {"seq": rank}, "kp_extends_beyond_candidate": False}
    if reason:
        d["normalization_reason"] = reason
    return d


def _legacy_item(rank, kp, gloss, sentence="x", disp=None, beyond=False):
    return {"rank": rank, "display_phrase": disp or kp, "key_phrase": kp, "used_form": kp, "japanese_gloss": gloss,
            "japanese_gloss_tts": kc.convert_display_gloss_to_tts_text(gloss), "source_sentence": sentence,
            "kp_extends_beyond_candidate": beyond, "changed_from_display_phrase": (disp or kp) != kp}


def _row(rank, gloss, consistent=False, meaning=True, **over):
    r = {"rank": rank, "current_gloss_consistent": consistent, "japanese_gloss": gloss,
         "qa_reflects_all_key_phrase_words": "PASS", "reasoning": "r", "added_word_mappings": []}
    if meaning:
        r.update({"meaning_in_text_en": "to set a limit", "naive_ja": "線を引く", "naive_ja_conveys": "no"})
    r.update(over)
    return r


class FakeFn:
    def __init__(self, payload, msg, model="gpt-6-luna"):
        self.payload, self.msg, self.model = payload, msg, model
        self.last_usage = None

    def __call__(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        p = self.payload(self.msg) if callable(self.payload) else self.payload
        return (p if isinstance(p, str) else json.dumps(p, ensure_ascii=False)), self.model, "resp_x"


class Recorder:
    """make_factory_for(msg)の契約を満たし、呼ばれたmessageと型を記録する。respondersは呼出順のpayload(またはcallable)。"""

    def __init__(self, responders):
        self.responders = list(responders)
        self.msgs = []

    def __call__(self, msg):
        self.msgs.append(msg)
        r = self.responders.pop(0)
        return FakeFn(r, msg)


class _FlagOn(unittest.TestCase):
    def setUp(self):
        old = ga.GLOSS_ALIGNMENT_ENABLED
        ga.GLOSS_ALIGNMENT_ENABLED = True
        self.addCleanup(setattr, ga, "GLOSS_ALIGNMENT_ENABLED", old)
        self.rules = ga.preflight(True)["rules_fulltext"]


class WC01_Immutability(_FlagOn):
    def test_existing_constants_unchanged(self):
        self.assertEqual(_sha(ga.DEVELOPER_MESSAGE), SHA_DEVELOPER)
        self.assertEqual(_sha(json.dumps(ga.GLOSS_ALIGNMENT_JSON_SCHEMA, ensure_ascii=False, sort_keys=True)), SHA_SCHEMA)
        self.assertEqual(_sha(ga.NEW_GENERATION_TEXT), SHA_NEWGEN_TEXT)
        self.assertEqual(_sha(ga.PERSON_CONSTRAINT_TEXT), SHA_PERSON_TEXT)

    def test_legacy_only_uses_current_builder_bytes_and_legacy_request(self):
        items = [_legacy_item(1, "based on interviews", "～をもとにした", disp="based on", beyond=True),
                 _legacy_item(2, "take part", "参加する")]
        rec = Recorder([{"items": [_row(1, "インタビューをもとにした", False, meaning=False), _row(2, "参加する", True, meaning=False)]}])
        gate = ga.run_alignment_gate_corrected(rec, items, "ART", self.rules)
        self.assertEqual(len(rec.msgs), 1)
        self.assertEqual(rec.msgs[0], ga.build_user_message_corrected(items, "ART", self.rules))
        self.assertNotIsInstance(rec.msgs[0], ga.NewGenMessage)
        self.assertEqual(gate["n_calls"], {"newgen": 0, "legacy": 1})
        self.assertFalse(gate["mixed"])
        self.assertNotIn("path", gate["attempts"][0])    # 従来のattempt記録形を変えない
        # 実request: developer/schemaは現行のまま
        cap = []
        fn = ga.make_alignment_fn(rec.msgs[0], client=_FakeClient(cap), model="m")
        fn()
        self.assertEqual(cap[0]["input"][0]["content"], ga.DEVELOPER_MESSAGE)
        self.assertEqual(cap[0]["text"]["format"]["name"], "key_phrase_gloss_alignment_corrected")


class _FakeClient:
    def __init__(self, cap, resp_text='{"items": []}'):
        self.cap = cap
        self.responses = SimpleNamespace(create=self._create)
        self.resp_text = resp_text

    def _create(self, **kw):
        self.cap.append(kw)
        return SimpleNamespace(model=kw["model"], output_text=self.resp_text, id="r",
                               usage=SimpleNamespace(input_tokens=1, output_tokens=1, input_tokens_details=SimpleNamespace(cached_tokens=0)))


class WC02_NewgenSelection(_FlagOn):
    def test_new_generation_selects_newgen_path(self):
        items = [_new_item(1, "draw a line", "the railway had to draw a line."), _new_item(2, "work out")]
        rec = Recorder([{"items": [_row(1, "線引きをする"), _row(2, "うまくいく")]}])
        gate = ga.run_alignment_gate_corrected(rec, items, "ART", self.rules)
        self.assertEqual(len(rec.msgs), 1)
        self.assertIsInstance(rec.msgs[0], ga.NewGenMessage)
        self.assertEqual(gate["n_calls"], {"newgen": 1, "legacy": 0})
        self.assertEqual(sorted(gate["adopted"]), [1, 2])
        # make_alignment_fn: 新developer・新schema
        cap = []
        ga.make_alignment_fn(rec.msgs[0], client=_FakeClient(cap), model="m")()
        self.assertEqual(cap[0]["input"][0]["content"], ga.NEWGEN_DEVELOPER_MESSAGE)
        fmt = cap[0]["text"]["format"]
        self.assertEqual(fmt["name"], "key_phrase_gloss_alignment_corrected_newgen")
        props = list(fmt["schema"]["properties"]["items"]["items"]["properties"])
        self.assertEqual(props[:6], ["rank", "current_gloss_consistent", "meaning_in_text_en", "naive_ja", "naive_ja_conveys", "japanese_gloss"])
        old_props = list(ga.GLOSS_ALIGNMENT_JSON_SCHEMA["schema"]["properties"]["items"]["items"]["properties"])
        self.assertTrue(set(old_props) <= set(props))       # Production必須欄が全部schemaにある
        req = fmt["schema"]["properties"]["items"]["items"]["required"]
        self.assertTrue(set(old_props) <= set(req))
        for k in ga.NEWGEN_MEANING_FIELDS:
            self.assertIn(k, req)

    def test_record_in_item_gloss_alignment(self):
        items = [_new_item(1, "draw a line")]
        merged = {"items": items}
        rec = Recorder([{"items": [_row(1, "線引きをする")]}])
        out = ga.align_glosses(merged, "ART", rec, enabled=True)
        ga_rec = out["merged"]["items"][0]["gloss_alignment"]
        self.assertEqual(ga_rec["meaning_stage"], "applied")
        self.assertEqual(ga_rec["meaning_in_text_en"], "to set a limit")
        self.assertEqual(out["merged"]["items"][0]["japanese_gloss"], "線引きをする")
        self.assertEqual(out["meaning_stage"]["stage"], "applied")
        self.assertEqual(out["meaning_stage"]["n_newgen_calls"], 1)


class WC03_MessageContents(_FlagOn):
    def test_newgen_message_has_no_old_clauses_and_has_new_ones(self):
        m = ga.build_user_message_newgen_meaning([_new_item(1, "draw a line")], "ART", self.rules)
        self.assertNotIn(OLD_CLAUSE_1, m)
        self.assertNotIn(OLD_CLAUSE_2, m)
        self.assertIn("範囲の規則", m)
        self.assertIn("定訳", m)
        self.assertNotIn("newgen_meaning_v1", m)        # マーカー文字列を入れない
        self.assertNotIn("NewGenMessage", m)
        # rules_fulltextの抽出文がそのまま含まれる
        self.assertIn(self.rules, m)
        self.assertIn("【記事本文(参考)】\nART", m)

    def test_default_rules_is_fulltext(self):
        pf = ga.preflight(True)
        m = ga.build_user_message_newgen_meaning([_new_item(1, "draw a line")], "ART")
        self.assertIn(pf["rules_fulltext"], m)


class WC04_MixedBatch(_FlagOn):
    def test_mixed_batch_two_calls_split(self):
        new_items = [_new_item(1, "draw a line"), _new_item(2, "work out")]
        legacy_items = [_legacy_item(3, "based on interviews", "～をもとにした", disp="based on", beyond=True)]
        targets = new_items + legacy_items
        rec = Recorder([{"items": [_row(1, "線引きをする"), _row(2, "うまくいく")]},
                        {"items": [_row(3, "インタビューをもとにした", False, meaning=False)]}])
        gate = ga.run_alignment_gate_corrected(rec, targets, "ART", self.rules)
        self.assertEqual(len(rec.msgs), 2)
        newgen_msg, legacy_msg = rec.msgs
        self.assertIsInstance(newgen_msg, ga.NewGenMessage)
        self.assertNotIn(OLD_CLAUSE_1, newgen_msg)
        self.assertNotIn(OLD_CLAUSE_2, newgen_msg)
        self.assertNotIsInstance(legacy_msg, ga.NewGenMessage)
        self.assertEqual(legacy_msg, ga.build_user_message_corrected(legacy_items, "ART", self.rules))   # 現行builderとbyte一致
        self.assertEqual(sorted(gate["adopted"]), [1, 2, 3])
        self.assertTrue(gate["mixed"])
        self.assertEqual(gate["n_calls"], {"newgen": 1, "legacy": 1})
        self.assertEqual({a["path"] for a in gate["attempts"]}, {ga.NEWGEN_PATH, "legacy"})
        # apply: 新経路itemだけに3欄を記録、legacy側はmeaning_stage=legacy、3欄なし
        out = ga.apply_alignment_corrected({"items": targets}, targets, gate)
        by = {it["rank"]: it["gloss_alignment"] for it in out["items"]}
        self.assertEqual(by[1]["meaning_stage"], "mixed_split_newgen")
        self.assertEqual(by[3]["meaning_stage"], "legacy")
        self.assertNotIn("naive_ja", by[3])

    def test_mixed_attempt_total_cap_stays_2(self):
        targets = [_new_item(1, "draw a line"), _legacy_item(2, "take part", "参加する")]
        bad_new = {"items": [_row(1, "線を引く", meaning=False)]}                    # 新欄欠落→INVALID
        bad_leg = {"items": [_row(2, "x(括弧)", True, meaning=False)]}
        rec = Recorder([bad_new, bad_leg, bad_new, bad_leg, bad_new, bad_leg])
        gate = ga.run_alignment_gate_corrected(rec, targets, "ART", self.rules)
        self.assertEqual(len(rec.msgs), 4)               # 2 attempt x 2 call(上限2不変)
        self.assertEqual(gate["unresolved_ranks"], [1, 2])


class WC05_ABC_NoNewgen(_FlagOn):
    def test_abc_items_never_use_newgen(self):
        called = {"n": 0}
        orig = ga.build_user_message_newgen_meaning
        ga.build_user_message_newgen_meaning = lambda *a, **k: called.__setitem__("n", called["n"] + 1) or orig(*a, **k)
        self.addCleanup(setattr, ga, "build_user_message_newgen_meaning", orig)
        # A/B/C形: fulltext_source_refなし(glossあり・再整合対象)
        item = _legacy_item(1, "based on interviews", "～をもとにした", disp="based on", beyond=True)
        merged = {"items": [item]}
        rec = Recorder([{"items": [_row(1, "インタビューをもとにした", False, meaning=False)]}])
        out = ga.align_glosses(merged, "ART", rec, enabled=True)
        self.assertEqual(called["n"], 0)
        self.assertNotIsInstance(rec.msgs[0], ga.NewGenMessage)
        self.assertEqual(out["meaning_stage"]["stage"], "legacy")
        self.assertEqual(out["meaning_stage"]["n_newgen_calls"], 0)
        # gloss無しでもfulltext_source_refが無ければnewgen対象でない
        self.assertFalse(ga.is_fulltext_gloss_missing({"rank": 1, "key_phrase": "x", "japanese_gloss": None}))


class WC06_RetryPriorNoFallback(_FlagOn):
    def test_retry_reposts_prior_and_unresolved_goes_to_hr_without_legacy_fallback(self):
        items = [_new_item(1, "draw a line")]
        bad = {"items": [_row(1, "線を引く(括弧)")]}                      # 括弧禁止違反→INVALID
        rec = Recorder([bad, bad])
        gate = ga.run_alignment_gate_corrected(rec, items, "ART", self.rules)
        self.assertEqual(len(rec.msgs), 2)                               # attempt上限2
        for m in rec.msgs:
            self.assertIsInstance(m, ga.NewGenMessage)                   # 旧builderへ暗黙フォールバックしない
        self.assertNotIn("previous_attempt_rejected", rec.msgs[0])
        self.assertIn("previous_attempt_rejected", rec.msgs[1])          # retry時にprior再掲
        self.assertIn("括弧禁止違反", rec.msgs[1])
        self.assertEqual(gate["unresolved_ranks"], [1])
        out = ga.apply_alignment_corrected({"items": items}, items, gate)
        self.assertEqual(out["items"][0]["gloss_alignment_status"], ga.STATUS_HR_REQUIRED)
        self.assertEqual(out["items"][0]["key_phrase"], "draw a line")  # KP維持
        self.assertIsNone(out["items"][0]["japanese_gloss"])             # 旧gloss(未生成)維持・暗黙採用なし

    def test_technical_failure_consumes_attempt(self):
        items = [_new_item(1, "draw a line")]
        rec = Recorder([RuntimeError("boom"), {"items": [_row(1, "線引きをする")]}])
        gate = ga.run_alignment_gate_corrected(rec, items, "ART", self.rules)
        self.assertEqual([a["status"] for a in gate["attempts"]], ["TECHNICAL_FAILED", "ALIGN_PASS"])
        self.assertIn(1, gate["adopted"])


class WC07_Validate(_FlagOn):
    def _target(self):
        return _new_item(1, "draw a line")

    def test_missing_or_bad_new_fields_invalid(self):
        t = self._target()
        v = ga.validate_item_corrected(_row(1, "線引きをする", meaning=False), t, newgen=True)
        self.assertFalse(v["valid"])
        self.assertIn("meaning_stage_fields_invalid", v["reasons"])
        v = ga.validate_item_corrected(_row(1, "線引きをする", naive_ja_conveys="maybe"), t, newgen=True)
        self.assertIn("meaning_stage_fields_invalid", v["reasons"])
        v = ga.validate_item_corrected(_row(1, "線引きをする", naive_ja=" "), t, newgen=True)
        self.assertIn("meaning_stage_fields_invalid", v["reasons"])
        self.assertTrue(ga.validate_item_corrected(_row(1, "線引きをする"), t, newgen=True)["valid"])
        # newgen=False(legacy)では新欄の有無を見ない
        self.assertTrue(ga.validate_item_corrected(_row(1, "線引きをする", meaning=False), t, newgen=False)["valid"])

    def test_type_loss_old_schema_response_is_invalid_then_hr(self):
        """型喪失: 新経路messageがstr演算で素のstrになり旧schema・旧developerで呼ばれる→新欄の無い応答→INVALID→retry→HR(安全停止)。"""
        items = [_new_item(1, "draw a line")]
        caps = []

        def factory(msg):
            plain = msg + ""                       # str演算で型が失われる
            self.assertNotIsInstance(plain, ga.NewGenMessage)
            old_resp = json.dumps({"items": [_row(1, "線を引く", meaning=False)]}, ensure_ascii=False)
            fn = ga.make_alignment_fn(plain, client=_FakeClient(caps, old_resp), model="m")
            return fn

        gate = ga.run_alignment_gate_corrected(factory, items, "ART", self.rules)
        self.assertEqual(gate["unresolved_ranks"], [1])
        self.assertEqual(len(caps), 2)
        self.assertEqual(caps[0]["input"][0]["content"], ga.DEVELOPER_MESSAGE)     # 旧developerで呼ばれた
        self.assertEqual(gate["item_log"][1][0]["reasons"][0], "meaning_stage_fields_invalid")

    def test_record_only_fields_do_not_change_verdict(self):
        t = _new_item(1, "work out")
        base = ga.validate_item_corrected(_row(1, "うまくいく"), t, newgen=True)
        imp = ga.validate_item_corrected(_row(1, "うまくいかなかった"), t, newgen=True)      # 持ち込み(否定+過去)
        self.assertTrue(base["valid"] and imp["valid"])                                    # 合否に使わない
        self.assertEqual(imp["import_flags"], ["neg_in_gloss_not_in_kp", "past_tense_ending"])
        self.assertEqual(base["import_flags"], [])
        same = ga.validate_item_corrected(_row(1, "線を引く", naive_ja="線を引く", naive_ja_conveys="yes"), _new_item(1, "draw a line"), newgen=True)
        self.assertTrue(same["valid"])
        self.assertTrue(same["gloss_equals_naive_ja"])
        self.assertEqual(same["naive_ja_conveys"], "yes")

    def test_existing_checks_still_apply_on_newgen(self):
        t = self._target()
        self.assertIn("括弧禁止違反", ga.validate_item_corrected(_row(1, "線を引く(a)"), t, newgen=True)["reasons"])
        self.assertIn("算用数字禁止違反", ga.validate_item_corrected(_row(1, "線を1本引く"), t, newgen=True)["reasons"])
        self.assertIn("qa_reflects_all_key_phrase_words!=PASS",
                      ga.validate_item_corrected(_row(1, "線を引く", qa_reflects_all_key_phrase_words="FAIL"), t, newgen=True)["reasons"])
        # 人称整合(someone's -> あなたの)
        tp = _new_item(2, "catch someone's attention", reason=ga.PERSON_NORMALIZATION_REASON, disp="catch your attention")
        v = ga.validate_item_corrected(_row(2, "あなたの注意を引く"), tp, newgen=True)
        self.assertFalse(v["valid"])
        self.assertTrue(v["person_check"])
        # mapping gate(追加内容語)
        tm = _new_item(3, "based on interviews", disp="based on")
        r = _row(3, "インタビューをもとにした", added_word_mappings=[{"english_word": "interviews", "japanese_span": "存在しない"}])
        vm = ga.validate_item_corrected(r, tm, mapping_gate=True, newgen=True)
        self.assertFalse(vm["valid"])


class WC08_ZRepairLegacy(_FlagOn):
    def test_repair_with_current_gloss_never_uses_newgen_and_records_counts(self):
        kp = {"items": [_legacy_item(1, "catch someone's attention", "あなたの注意を引く", disp="catch your attention"),
                        _legacy_item(2, "take part", "参加する")]}
        kp["items"][0]["normalization_reason"] = ga.PERSON_NORMALIZATION_REASON
        rec = Recorder([{"items": [_row(1, "人の注意を引く", False, meaning=False)]}])
        with tempfile.TemporaryDirectory() as d:
            out = ga.align_glosses(kp, "ART", rec, out_dir=d, enabled=True, only_ranks=[1])
            meta = json.load(open(os.path.join(d, "gloss_alignment_runtime_metadata.json"), encoding="utf-8"))
        self.assertEqual(len(rec.msgs), 1)
        self.assertNotIsInstance(rec.msgs[0], ga.NewGenMessage)
        self.assertEqual(out["meaning_stage"]["n_newgen_calls"], 0)
        self.assertEqual(meta["meaning_stage"]["n_repaired"], 1)
        self.assertEqual(meta["meaning_stage"]["n_realigned"], 1)
        self.assertEqual(meta["meaning_stage"]["n_already_consistent"], 0)
        self.assertEqual(meta["meaning_stage"]["stage"], "legacy")


class WC09_FlagOff(_FlagOn):
    def test_flag_off_is_disabled_and_zero_calls(self):
        """EIGO_KP_GLOSS_ALIGNMENT=OFFは『gloss生成の全停止(本番停止)』であり撤退手段ではない。撤退は単一commitのgit revert。
        ここでは従来どおりDISABLED・API呼出0を確認するだけ。"""
        items = [_new_item(1, "draw a line")]
        rec = Recorder([])
        out = ga.align_glosses({"items": items}, "ART", rec, enabled=False)
        self.assertEqual(out["status"], "DISABLED")
        self.assertEqual(rec.msgs, [])
        # 消費側はgloss未生成のitemを未評価として止める(fail-closed。OFFは元の挙動へ戻る手段でない)
        self.assertEqual([it["rank"] for it in ga.select_consumer_unevaluated(items)], [1])


class WC10_MakeAlignmentFn(_FlagOn):
    def test_plain_str_and_explicit_args_keep_current(self):
        cap = []
        ga.make_alignment_fn("plain", client=_FakeClient(cap), model="m")()
        self.assertEqual(cap[0]["input"][0]["content"], ga.DEVELOPER_MESSAGE)
        self.assertEqual(cap[0]["text"]["format"]["name"], "key_phrase_gloss_alignment_corrected")
        cap2 = []
        msg = ga.NewGenMessage("x")
        sch = ga.GLOSS_ALIGNMENT_JSON_SCHEMA
        ga.make_alignment_fn(msg, client=_FakeClient(cap2), model="m", developer_message="DEV", schema=sch)()
        self.assertEqual(cap2[0]["input"][0]["content"], "DEV")                    # 呼出側の明示を優先
        self.assertEqual(cap2[0]["text"]["format"]["name"], "key_phrase_gloss_alignment_corrected")
        cap3 = []
        ga.make_alignment_fn(msg, client=_FakeClient(cap3), model="m", developer_message="DEV")()
        self.assertEqual(cap3[0]["input"][0]["content"], "DEV")
        self.assertEqual(cap3[0]["text"]["format"]["name"], "key_phrase_gloss_alignment_corrected_newgen")   # schemaは未明示→新規生成用


class WC11_NoDevImport(unittest.TestCase):
    def test_production_module_does_not_reference_dev_trial(self):
        src = open(os.path.join(REPO, "er003_key_words_gloss_alignment.py"), encoding="utf-8").read()
        # コメント・docstring内の説明は除き、import文とimportlib/__import__呼出だけを検査する
        for m in re.findall(r"^\s*(?:import|from)\s+([A-Za-z0-9_\.]+)", src, re.M):
            self.assertFalse(m.startswith("er112"), m)
        for needle in ("import_module(", "__import__(", "spec_from_file_location("):
            self.assertNotIn(needle, src, needle)


class WC12_Golden(_FlagOn):
    def setUp(self):
        super().setUp()
        self.g = json.load(open(GOLDEN, encoding="utf-8"))

    def test_messages_match_dev_trial06_bytes(self):
        for name, c in self.g["cases"].items():
            prior = {int(k): v for k, v in c["prior"].items()} if c["prior"] else None
            msg = ga.build_user_message_newgen_meaning(c["targets"], self.g["article"], prior=prior)
            self.assertEqual(msg, c["message"], name)
            self.assertIsInstance(msg, ga.NewGenMessage)

    def test_schema_and_developer_match_dev(self):
        self.assertEqual(ga.NEWGEN_DEVELOPER_MESSAGE, self.g["developer"])
        a = json.loads(json.dumps(ga.NEWGEN_JSON_SCHEMA))
        b = json.loads(json.dumps(self.g["schema"]))
        a.pop("name"), b.pop("name")
        self.assertEqual(json.dumps(a, ensure_ascii=False), json.dumps(b, ensure_ascii=False))   # 欄順込み

    def test_golden_covers_person_and_prior(self):
        cs = self.g["cases"]
        self.assertIn("indefinite_person_tokens_in_key_phrase", cs["person_noprior"]["message"])
        self.assertIn("previous_attempt_rejected", cs["plain_prior"]["message"])
        self.assertNotIn("previous_attempt_rejected", cs["plain_noprior"]["message"])


class WC13_FormalScaffoldEntry(_FlagOn):
    """X/Z共通の正式入口 sc.run_key_phrase_canonicalization(アルゴ: canonicalization -> merge -> align_glosses)で、
    全文選定itemのgloss新規生成がX2p'経路に入り、永続化artifactに記録が残ること(API 0、Fake)。"""

    def test_scaffold_entry_uses_newgen_and_persists_record(self):
        import unittest.mock as mock
        import er003_v1_n3_01_scaffold_generate as sc
        items = [_new_item(1, "draw a line", "the railway had to draw a line."), _new_item(2, "work out")]
        seen = []

        def fake_make_alignment_fn(msg, **kw):
            seen.append((type(msg).__name__, kw))
            return FakeFn({"items": [_row(1, "線引きをする"), _row(2, "うまくいく")]}, msg)

        with tempfile.TemporaryDirectory() as d,                 mock.patch.object(kc, "run_canonicalization_gate", return_value=({"items": []}, "CANONICALIZATION_PASS", [], "m", "r")),                 mock.patch.object(kc, "merge_canonicalization_result", return_value={"items": items}),                 mock.patch.object(ga, "make_alignment_fn", side_effect=fake_make_alignment_fn):
            res = sc.run_key_phrase_canonicalization("ART text", items, d, "art_wc13")
            art = json.load(open(os.path.join(d, "keywords_canonicalized.json"), encoding="utf-8"))
            meta = json.load(open(os.path.join(d, "gloss_alignment_runtime_metadata.json"), encoding="utf-8"))
            prompt = open(os.path.join(d, "gloss_alignment_prompt.txt"), encoding="utf-8").read()
        self.assertEqual(seen[0][0], "NewGenMessage")
        self.assertNotIn("developer_message", seen[0][1])      # 正式入口は明示せず、make_alignment_fnがP'で切替える
        self.assertEqual(res["gloss_alignment_status"], "ALIGN_PASS")
        self.assertEqual(meta["meaning_stage"]["stage"], "applied")
        self.assertEqual(art["items"][0]["gloss_alignment"]["meaning_stage"], "applied")
        self.assertNotIn(OLD_CLAUSE_1, prompt)                   # 保存されたPromptも新規生成用(marker無し)
        self.assertNotIn("newgen_meaning_v1", prompt)

    def test_y_trial_shares_common_module(self):
        for fn in ("er110_family_y_text_trial_01_run.py", "er110_family_y_persona_text_trial_01_run.py"):
            src = open(os.path.join(REPO, fn), encoding="utf-8").read()
            self.assertIn("import er003_v1_n3_01_scaffold_generate as sc", src, fn)
            self.assertRegex(src, r"sc\.run_key_phrases\([^)]*kp_backend=\"fulltext_p2\"", fn)
        for fn in ("er110_family_y_audio_trial_01.py", "er110_family_y_persona_audio_trial_01.py"):
            self.assertIn('"production_reachable": False', open(os.path.join(REPO, fn), encoding="utf-8").read(), fn)


if __name__ == "__main__":
    unittest.main()
