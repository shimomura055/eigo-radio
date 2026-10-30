# er135_enduser_translate_test_01.py  (ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03T、API 0: LLMはmock)
import json
import re
import tempfile
import unittest

import er135_enduser_translate_01 as T

JA = {
    "Melos was angry.": "メロスは怒っていました。",
    "He walked three miles to the city.": "彼は3マイル歩いて街へ行きました。",
    "The king said, \"You are a fool.\"": "王は「おまえは愚か者だ」と言いました。",
    "Mr. Smith arrived at 5 p.m. yesterday.": "スミスさんは昨日の午後5時に着きました。",
    "\"Stop,\" he said.": "「止まれ」と彼は言いました。",
    "\"Go now.\"": "「今すぐ行け」",
    "Run!": "走れ!",
    "The cliffs on the Moon are small.": "月の崖は小さいです。",
    "Researchers mapped 8,900 cliffs.": "研究者たちは8,900の崖を地図にしました。",
    "He did not trust the king.": "彼は王を信用していませんでした。",
    "The Moon shrank by 42 to 46 meters.": "月は42〜46メートル縮みました。",
}


def _targets(prompt):
    body = prompt.split(T.TRANSLATE_TARGET_LABEL, 1)[1].split("\n# 出力形式")[0].split("\n" + T.RETRY_NOTE_LABEL)[0]
    return [re.match(r"^\d+\. (.*)$", l).group(1) for l in body.strip().split("\n")]


def _pairs(prompt):
    body = prompt[len(T.VERIFY_HEAD):].split("\n# 出力形式")[0]
    return re.findall(r"^\d+\. EN: (.*)\n   JA: (.*)$", body, re.M)


class FakeLLM:
    def __init__(self, ja=None, bad_verify=(), translate_script=None, verify_script=None):
        self.ja = dict(JA if ja is None else ja)
        self.bad_verify = set(bad_verify)
        self.translate_script = list(translate_script or [])   # 先頭から消費。Noneなら通常応答
        self.verify_script = list(verify_script or [])
        self.log = []
        self.prompts = []

    def __call__(self, kind, prompt):
        self.log.append(kind)
        self.prompts.append((kind, prompt))
        if kind == "translate":
            if self.translate_script:
                f = self.translate_script.pop(0)
                if f is not None:
                    return f(_targets(prompt), self.ja)
            ts = _targets(prompt)
            return json.dumps({"translations": [{"id": i, "ja": self.ja[t]} for i, t in enumerate(ts, 1)]}, ensure_ascii=False)
        if self.verify_script:
            f = self.verify_script.pop(0)
            if f is not None:
                return f(_pairs(prompt))
        ps = _pairs(prompt)
        return json.dumps({"results": [{"id": i, "ok": en not in self.bad_verify, "issue": "mock-ng"} for i, (en, ja) in enumerate(ps, 1)]})

    def n(self, kind):
        return self.log.count(kind)


def S(*texts, para=None):
    return [{"sid": f"s{i}", "en": t, **({"para": para[i - 1]} if para else {})} for i, t in enumerate(texts, 1)]


def run(sents, llm, d, part="p1"):
    return T.translate_part(part, sents, level="adv", family="Z", cache_dir=d, llm=llm, now_fn=lambda: "2026-10-30T00:00:00")


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.d = self._td.name

    def tearDown(self):
        self._td.cleanup()


class TestNormal(Base):
    def test_one_to_one(self):
        llm = FakeLLM()
        r = run(S("Melos was angry.", "He walked three miles to the city."), llm, self.d)
        self.assertEqual(r["ja"], {"s1": JA["Melos was angry."], "s2": JA["He walked three miles to the city."]})
        self.assertEqual(r["coverage"]["ratio"], 1.0)
        self.assertTrue(r["coverage"]["complete"])
        self.assertEqual(r["meta"]["api_calls"], {"translate": 1, "verify": 1})
        self.assertEqual(r["meta"]["ja_source"], "generated")
        self.assertEqual(r["meta"]["model"], "gpt-6-luna")
        self.assertEqual(r["meta"]["failures"], [])

    def test_prompt_has_context_and_numbered_ids(self):
        llm = FakeLLM()
        sents = S("Melos was angry.", "Run!", para=[0, 1])
        run(sents, llm, self.d)            # 1回目: 全部対象 → 文脈なし
        self.assertNotIn(T.TRANSLATE_CONTEXT_LABEL, llm.prompts[0][1])
        sents2 = S("Melos was angry.", "Mr. Smith arrived at 5 p.m. yesterday.", para=[0, 1])
        llm2 = FakeLLM()
        run(sents2, llm2, self.d)          # para0はキャッシュ → para1だけ翻訳、para0は文脈
        p = llm2.prompts[0][1]
        self.assertIn(T.TRANSLATE_CONTEXT_LABEL + "- Melos was angry.", p)
        self.assertEqual(_targets(p), ["Mr. Smith arrived at 5 p.m. yesterday."])

    def test_fragments_quotes_and_abbrev(self):
        llm = FakeLLM()
        sents = S("\"Stop,\" he said.", "\"Go now.\"", "Mr. Smith arrived at 5 p.m. yesterday.", "Run!")
        r = run(sents, llm, self.d)
        self.assertTrue(r["coverage"]["complete"], r["meta"]["failures"])
        self.assertEqual(r["ja"]["s4"], "走れ!")   # 短い台詞はcheck_jaの最小長/かな必須を緩和

    def test_prompt_rules(self):
        self.assertIn("まとめない", T.TRANSLATE_HEAD)
        self.assertIn("分けない", T.TRANSLATE_HEAD)
        self.assertIn("数字", T.TRANSLATE_HEAD)
        self.assertNotIn("Standard", T.TRANSLATE_HEAD)
        self.assertNotIn("Advanced", T.TRANSLATE_HEAD)


class TestMergeSplitRetry(Base):
    def test_merge_then_retry_ok(self):
        merged = lambda ts, ja: json.dumps({"translations": [{"id": 1, "ja": "メロスは怒っていました。彼は3マイル歩きました。"}]}, ensure_ascii=False)
        llm = FakeLLM(translate_script=[merged])
        r = run(S("Melos was angry.", "He walked three miles to the city."), llm, self.d)
        self.assertEqual(llm.n("translate"), 2)
        self.assertTrue(r["coverage"]["complete"])

    def test_split_twice_fail_closed(self):
        split = lambda ts, ja: json.dumps({"translations": [{"id": i, "ja": f"訳{i}です。"} for i in range(1, len(ts) + 2)]}, ensure_ascii=False)
        llm = FakeLLM(translate_script=[split, split])
        r = run(S("Melos was angry.", "He walked three miles to the city."), llm, self.d)
        self.assertEqual(llm.n("translate"), 2)   # retryは1回まで
        self.assertEqual(llm.n("verify"), 0)
        self.assertEqual(r["ja"], {"s1": None, "s2": None})
        self.assertEqual(r["coverage"]["translated"], 0)
        self.assertIn("parse", r["meta"]["failures"][0]["reason"])

    def test_id_mismatch_and_duplicate_and_bad_json(self):
        bad_ids = lambda ts, ja: json.dumps({"translations": [{"id": 2, "ja": "メロスは怒りました。"}, {"id": 1, "ja": "彼は歩きました。"}]}, ensure_ascii=False)
        dup = lambda ts, ja: json.dumps({"translations": [{"id": 1, "ja": "同じ訳です。"}, {"id": 2, "ja": "同じ訳です。"}]}, ensure_ascii=False)
        for f in (bad_ids, dup, lambda ts, ja: "not json"):
            llm = FakeLLM(translate_script=[f, f])
            r = run(S("Melos was angry.", "He did not trust the king."), llm, self.d)
            self.assertEqual(r["coverage"]["translated"], 0)

    def test_partial_failure_only_that_paragraph_null(self):
        # para0の数値が1回目で違う→retryでpara0のみ再依頼、para1は1回目で確定
        def first(ts, ja):
            return json.dumps({"translations": [{"id": 1, "ja": "彼は5マイル歩いて街へ行きました。"}, {"id": 2, "ja": JA["He did not trust the king."]}]}, ensure_ascii=False)
        llm = FakeLLM(translate_script=[first])
        r = run(S("He walked three miles to the city.", "He did not trust the king.", para=[0, 1]), llm, self.d)
        self.assertEqual(llm.n("translate"), 2)
        self.assertEqual(_targets(llm.prompts[1][1]), ["He walked three miles to the city."])
        self.assertTrue(r["coverage"]["complete"])

    def test_numeric_mismatch_both_attempts_paragraph_null(self):
        wrong = {**JA, "He walked three miles to the city.": "彼は5マイル歩いて街へ行きました。"}
        llm = FakeLLM(ja=wrong)
        r = run(S("He walked three miles to the city.", "He did not trust the king.", para=[0, 1]), llm, self.d)
        self.assertIsNone(r["ja"]["s1"])
        self.assertIsNotNone(r["ja"]["s2"])
        self.assertEqual(r["coverage"]["paragraphs_translated"], 1)
        self.assertEqual(r["coverage"]["ratio"], 0.5)
        self.assertFalse(r["coverage"]["complete"])
        self.assertIn("数値不一致", r["meta"]["failures"][0]["reason"])


class TestChecks(Base):
    def test_check_ja_ng_null(self):
        bad = {**JA, "Melos was angry.": "Melos was angry."}   # 英語のまま
        r = run(S("Melos was angry."), FakeLLM(ja=bad), self.d)
        self.assertIsNone(r["ja"]["s1"])
        self.assertIn("local_check", r["meta"]["failures"][0]["reason"])

    def test_check_ja_forbidden_pattern(self):
        bad = {**JA, "Melos was angry.": "(A2)メロスは怒りました。"}
        r = run(S("Melos was angry."), FakeLLM(ja=bad), self.d)
        self.assertIsNone(r["ja"]["s1"])

    def test_llm_verify_ng_null_and_not_cached(self):
        llm = FakeLLM(bad_verify={"He did not trust the king."})
        sents = S("Melos was angry.", "He did not trust the king.", para=[0, 1])
        r = run(sents, llm, self.d)
        self.assertIsNotNone(r["ja"]["s1"])
        self.assertIsNone(r["ja"]["s2"])
        self.assertIn("verify_ng", r["meta"]["failures"][0]["reason"])
        # 失敗は非キャッシュ: 次回は失敗段落だけ再翻訳(para0はキャッシュ)
        llm2 = FakeLLM()
        r2 = run(sents, llm2, self.d)
        self.assertTrue(r2["coverage"]["complete"])
        self.assertEqual(r2["meta"]["cache_hits"], 1)
        self.assertEqual(llm2.n("translate"), 1)
        self.assertEqual(_targets(llm2.prompts[0][1]), ["He did not trust the king."])

    def test_semantic_reversal_caught_by_verify_only(self):
        # 数値もcheck_jaも通るが意味反転(否定が抜けた)→ LLM照合で落ちる
        rev = {**JA, "He did not trust the king.": "彼は王を信用していました。"}
        llm = FakeLLM(ja=rev, bad_verify={"He did not trust the king."})
        r = run(S("He did not trust the king."), llm, self.d)
        self.assertIsNone(r["ja"]["s1"])

    def test_verify_response_broken_fail_closed(self):
        broken = lambda ps: "garbage"
        llm = FakeLLM(verify_script=[broken, broken])
        r = run(S("Melos was angry."), llm, self.d)
        self.assertEqual(llm.n("verify"), 2)   # retryは1回まで
        self.assertIsNone(r["ja"]["s1"])
        self.assertIn("verify_unavailable", r["meta"]["failures"][0]["reason"])
        self.assertEqual(T.load_generated(self.d)["entries"], {})

    def test_verify_missing_id_fail_closed(self):
        part = lambda ps: json.dumps({"results": [{"id": 1, "ok": True}]})
        llm = FakeLLM(verify_script=[part, part])
        r = run(S("Melos was angry.", "He did not trust the king."), llm, self.d)
        self.assertEqual(r["coverage"]["translated"], 0)

    def test_embed_cos_low_null(self):
        emb = lambda texts: [[1.0, 0.0] if i % 2 == 0 else [0.0, 1.0] for i in range(len(texts))]
        r = T.translate_part("p1", S("Melos was angry."), level="adv", family="Z", cache_dir=self.d, llm=FakeLLM(), embed_fn=emb)
        self.assertIsNone(r["ja"]["s1"])
        self.assertIn("embed_cos_low", r["meta"]["failures"][0]["reason"])

    def test_model_mismatch_stops(self):
        class Bad(FakeLLM):
            def __call__(self, kind, prompt):
                raise T.ModelContractError("x")
        with self.assertRaises(T.ModelContractError):
            run(S("Melos was angry."), Bad(), self.d)

    def test_routing_keys(self):
        self.assertEqual(T.routing.require_model("ENDUSER_JA_TRANSLATE", "gpt-6-luna"), "gpt-6-luna")
        self.assertEqual(T.routing.require_model("ENDUSER_JA_VERIFY", "gpt-6-luna"), "gpt-6-luna")


class TestRetryNote(Base):
    """E2(Z実走で観測): 『they→二人』『never again→二度と』の数詞が英文にない数としてlocal_check不合格 -> retryに指摘を付けて直す。"""

    JA2 = {"They shut the door.": "二人は戸を閉めた。", "She was never seen again.": "彼女は二度と姿を見せなかった。"}
    FIX = {"They shut the door.": "彼らは戸を閉めた。", "She was never seen again.": "彼女はもう決して姿を見せなかった。"}

    def test_first_prompt_has_no_note_and_retry_prompt_names_failed_sentences(self):
        sents = S("They shut the door.", "She was never seen again.")
        first = lambda ts, ja: json.dumps({"translations": [{"id": i, "ja": self.JA2[t]} for i, t in enumerate(ts, 1)]}, ensure_ascii=False)
        llm = FakeLLM(ja=dict(self.FIX), translate_script=[first])
        r = run(sents, llm, self.d)
        tr = [p for k, p in llm.prompts if k == "translate"]
        self.assertEqual(len(tr), 2)                                     # 初回 + retry1回(上限不変)
        self.assertNotIn(T.RETRY_NOTE_LABEL, tr[0])                      # 初回のPromptは従来と同一
        self.assertIn(T.RETRY_NOTE_LABEL, tr[1])
        self.assertIn("1番:", tr[1])
        self.assertIn("2番:", tr[1])                                     # 段落内の不合格の文すべてに指摘が付く
        self.assertIn("二人は戸を閉めた。", tr[1])                        # 前回の訳を示す
        self.assertEqual([r["ja"]["s1"], r["ja"]["s2"]], [self.FIX["They shut the door."], self.FIX["She was never seen again."]])

    def test_retry_that_still_fails_stays_fail_closed(self):
        sents = S("They shut the door.")
        llm = FakeLLM(ja=dict(self.JA2))                                 # 毎回『二人』のまま
        r = run(sents, llm, self.d)
        self.assertEqual(llm.n("translate"), 2)
        self.assertIsNone(r["ja"]["s1"])                                 # 数の余剰はfail-closed(英語のみ)


class TestNumbers(unittest.TestCase):
    def ok(self, en, ja):
        T.check_numbers(en, ja)

    def ng(self, en, ja):
        with self.assertRaises(ValueError):
            T.check_numbers(en, ja)

    def test_normalization(self):
        self.ok("He has three dogs.", "彼は犬を3匹飼っています。")
        self.ok("He has 3 dogs.", "彼は犬を三匹飼っています。")
        self.ok("There were twenty-one men.", "21人の男がいました。")
        self.ok("There were twenty-one men.", "二十一人の男がいました。")
        self.ok("About 8,900 cliffs.", "約8900の崖。")
        self.ok("About 8,900 cliffs.", "約八千九百の崖。")
        self.ok("Two hundred people came.", "200人が来ました。")
        self.ok("Three thousand five hundred.", "3,500です。")
        self.ok("It cost 30,000 yen.", "3万円かかりました。")
        self.ok("It cost 35,000 yen.", "3万5千円かかりました。")
        self.ok("In 2024 it began.", "二〇二四年に始まりました。")
        self.ok("42 to 46 meters", "42〜46メートル")
        self.ok("The third day came.", "三日目が来ました。")
        self.ok("She finished 2nd.", "彼女は2位でした。")
        self.ok("A rate of 5%.", "5パーセントです。")
        self.ok("Both men left.", "二人とも去りました。")   # 暗黙数

    def test_mismatch(self):
        self.ng("He has three dogs.", "彼は犬を4匹飼っています。")
        self.ng("He has three dogs.", "彼は犬を飼っています。")           # 欠落
        self.ng("He has dogs.", "彼は犬を5匹飼っています。")              # 余剰(追加)
        self.ng("About 8,900 cliffs.", "約8,000の崖。")

    def test_no_numbers_and_one(self):
        self.ok("No one came.", "誰も来ませんでした。")
        self.ok("One of them left.", "そのうちの一人が去りました。")


class TestCache(Base):
    def test_cache_reuse_api0(self):
        sents = S("Melos was angry.", "He did not trust the king.")
        run(sents, FakeLLM(), self.d)
        llm2 = FakeLLM()
        r = run(sents, llm2, self.d)
        self.assertEqual(llm2.log, [])
        self.assertTrue(r["coverage"]["complete"])
        self.assertEqual(r["meta"]["cache_hits"], 1)
        self.assertEqual(r["meta"]["api_calls"], {"translate": 0, "verify": 0})

    def test_entry_metadata(self):
        run(S("Melos was angry."), FakeLLM(), self.d)
        doc = T.load_generated(self.d)
        (ent,) = doc["entries"].values()
        self.assertEqual(ent["ja_source"], "generated")
        self.assertEqual(ent["model"], "gpt-6-luna")
        self.assertEqual(ent["prompt_sha256"], T.PROMPT_TEMPLATE_SHA256)
        self.assertEqual(ent["generated_at"], "2026-10-30T00:00:00")
        self.assertEqual(ent["part_id"], "p1")

    def test_one_sentence_changed_only_that_paragraph(self):
        a = S("Melos was angry.", "He did not trust the king.", "The Moon shrank by 42 to 46 meters.", para=[0, 1, 2])
        run(a, FakeLLM(), self.d)
        b = S("Melos was angry.", "The cliffs on the Moon are small.", "The Moon shrank by 42 to 46 meters.", para=[0, 1, 2])
        llm = FakeLLM()
        r = run(b, llm, self.d)
        self.assertEqual(llm.n("translate"), 1)
        self.assertEqual(_targets(llm.prompts[0][1]), ["The cliffs on the Moon are small."])
        self.assertEqual(len(_pairs(llm.prompts[1][1])), 1)   # 照合も新規分だけ
        self.assertEqual(r["meta"]["cache_hits"], 2)
        self.assertTrue(r["coverage"]["complete"])
        # 旧段落のentryは除去(陳腐化した訳を残さない)
        self.assertEqual(len(T.load_generated(self.d)["entries"]), 3)

    def test_prompt_sha_change_does_not_invalidate(self):
        sents = S("Melos was angry.")
        run(sents, FakeLLM(), self.d)
        old = T.PROMPT_TEMPLATE_SHA256
        try:
            T.PROMPT_TEMPLATE_SHA256 = "changed"
            llm = FakeLLM()
            r = run(sents, llm, self.d)
            self.assertEqual(llm.log, [])
            self.assertTrue(r["coverage"]["complete"])
        finally:
            T.PROMPT_TEMPLATE_SHA256 = old

    def test_model_change_does_not_invalidate(self):
        sents = S("Melos was angry.")
        run(sents, FakeLLM(), self.d)
        doc = T.load_generated(self.d)
        for e in doc["entries"].values():
            e["model"] = "other-model"
        T.save_generated(self.d, doc)
        llm = FakeLLM()
        run(sents, llm, self.d)
        self.assertEqual(llm.log, [])

    def test_failure_not_cached(self):
        llm = FakeLLM(translate_script=[lambda ts, ja: "x", lambda ts, ja: "x"])
        run(S("Melos was angry."), llm, self.d)
        self.assertEqual(T.load_generated(self.d)["entries"], {})

    def test_corrupt_cached_value_is_retranslated(self):
        sents = S("He walked three miles to the city.")
        run(sents, FakeLLM(), self.d)
        doc = T.load_generated(self.d)
        for e in doc["entries"].values():
            e["ja"] = ["彼は9マイル歩きました。"]
        T.save_generated(self.d, doc)
        llm = FakeLLM()
        r = run(sents, llm, self.d)
        self.assertEqual(llm.n("translate"), 1)
        self.assertEqual(r["ja"]["s1"], JA["He walked three miles to the city."])

    def test_broken_schema_raises(self):
        T.save_generated(self.d, {"schema": "old", "entries": {}})
        with self.assertRaises(T.EnduserTranslateError):
            run(S("Melos was angry."), FakeLLM(), self.d)

    def test_other_part_entries_kept(self):
        run(S("Melos was angry."), FakeLLM(), self.d, part="p1")
        run(S("He did not trust the king."), FakeLLM(), self.d, part="p2")
        self.assertEqual(len(T.load_generated(self.d)["entries"]), 2)


class TestCoverage(Base):
    def test_coverage_numbers(self):
        wrong = {**JA, "He did not trust the king.": "彼は王を信用していませんでした。そして走りました。そして泣きました。"}
        sents = S("Melos was angry.", "He did not trust the king.", "The Moon shrank by 42 to 46 meters.", "Run!", para=[0, 1, 1, 2])
        r = run(sents, FakeLLM(ja=wrong), self.d)   # para1(s2,s3)は結合の疑いでNG → null
        cov = r["coverage"]
        self.assertEqual((cov["sentences"], cov["translated"], cov["paragraphs"], cov["paragraphs_translated"]), (4, 2, 3, 2))
        self.assertAlmostEqual(cov["ratio"], 0.5)
        self.assertFalse(cov["complete"])
        self.assertEqual(r["meta"]["failures"][0]["sids"], ["s2", "s3"])

    def test_input_validation(self):
        for bad in ([], [{"sid": "a", "en": ""}], [{"sid": "a", "en": "x"}, {"sid": "a", "en": "y"}], [{"sid": "a", "en": "こんにちは"}]):
            with self.assertRaises(ValueError):
                run(bad, FakeLLM(), self.d)


if __name__ == "__main__":
    unittest.main()
