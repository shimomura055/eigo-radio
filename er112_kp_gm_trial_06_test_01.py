# -*- coding: utf-8 -*-
"""委任_30 Trial_06 DEV harness: API 0のtest(dry-runでAPI呼出0・Trial_05 X2pとのgolden一致・prior再提示・持ち込み検出・Production非編集・hard-core集合の事前固定)。"""
import json, unittest
from pathlib import Path
import argparse
import er112_kp_gm_trial_06 as T6
import er112_kp_gm_trial_05 as T5
import er112_kp_gm_trial_02 as T
import er003_key_words_gloss_alignment as ga

ROOT = Path(__file__).resolve().parent


def _ns(**kw):
    d = dict(arm="B0p,X2pp", reps="1", set="", keys="", siblings="auto", cap=0.0, tag="", workers=2, max_calls=0, max_level=0, verbose=False)
    d.update(kw)
    return argparse.Namespace(**d)


class T06(unittest.TestCase):
    def test_default_off_isolation_no_api_no_files(self):
        """cap<=0(既定)ではAPI client生成0・台帳/結果ファイル書込0。"""
        called = []
        orig = T.client
        T.client = lambda *a, **k: called.append(1) or (_ for _ in ()).throw(AssertionError("API client must not be created"))
        before = (T6.LEDGER6.exists(), T6.RES6.exists())
        try:
            T6.cmd_gen(_ns(set="S2", siblings="on"))
            T6.cmd_gen(_ns(set="HC", siblings="off", reps="1,2"))
        finally:
            T.client = orig
        self.assertEqual(called, [])
        self.assertEqual((T6.LEDGER6.exists(), T6.RES6.exists()), before)
        self.assertFalse(T6.LEDGER6.exists() and T6.total() > 0)

    def test_golden_x2pp_builder_matches_trial05_x2p_except_declared_diffs(self):
        """宣言した差分(rules_fulltext / prior / X2PP_SCOPE / X2PP_MEANING)を戻すと、Trial_05 build_x_message('X2p')と1文字も違わない(人称ありKP含む)。"""
        A = T6.all_kps6()
        for keys in (["draw a line", "sound no one asked for"], ["reach for someone's wallet"], ["add up"]):
            kps = [A[k] for k in keys if k in A]
            import er112_kp_gm_trial_04_gen as G
            kps = [kp for kp in kps if G.art_id(kp) == G.art_id(kps[0])]
            tgt = G._targets(kps)
            base = T5.build_x_message("X2p", tgt, kps[0]["article"])
            rules = ga.preflight(True)["rules"]
            mine = T6.build_x_message06(tgt, kps[0]["article"], rules=rules, prior=None, meaning=T5.X2P_MEANING, scope="")
            self.assertEqual(base, mine)

    def test_x2pp_message_contents(self):
        A = T6.all_kps6()
        kp = A["draw a line"]
        import er112_kp_gm_trial_04_gen as G
        tgt = G._targets([kp])
        m = T6.build_x_message06(tgt, kp["article"])
        self.assertIn(T6.X2PP_SCOPE, m)
        self.assertIn(T6.X2PP_MEANING, m)
        self.assertNotIn(T5.X2P_MEANING, m)
        self.assertIn(ga.preflight(True)["rules_fulltext"], m)             # Production全文選定itemが使う規則
        self.assertNotIn("他の文脈でも再利用できる", m)
        self.assertNotIn("<!--", m)                                         # Promptにマーカーを入れない(P')
        self.assertIn("定訳", m)
        self.assertIn("範囲の規則", m)

    def test_examples_not_leaked_from_evaluation_sets(self):
        """Promptの例示KP(work out/cut corners/break even)が評価集合(S2/R/held-out/HC)に含まれない(過学習防止)。"""
        ks = {k.lower() for k in T6.all_kps6()}
        for e in ("work out", "cut corners", "break even"):
            self.assertNotIn(e, ks)
            self.assertFalse([k for k in ks if e in k.split() or k == e])

    def test_prior_block_matches_production_item_form(self):
        A = T6.all_kps6()
        kp = A["draw a line"]
        import er112_kp_gm_trial_04_gen as G
        tgt = G._targets([kp])
        prior = {1: {"gloss": "線を引く", "reasons": ["qaがPASSでない"]}}
        m = T6.build_x_message06(tgt, kp["article"], prior=prior)
        prod = ga.build_user_message_corrected(tgt, kp["article"], prior=prior)
        needle = '"previous_attempt_rejected": {\n      "gloss": "線を引く",\n      "reasons": [\n        "qaがPASSでない"\n      ]\n    }'
        self.assertIn(needle, m)
        self.assertIn(needle, prod)
        pb = "previous_attempt_rejected(ある項目のみ)は、前回の応答が検証で却下された理由です。同じ誤りを繰り返さないでください。"
        self.assertIn(pb, m)
        self.assertIn(pb, prod)
        self.assertNotIn("previous_attempt_rejected(", T6.build_x_message06(tgt, kp["article"]))

    def test_schema_order_and_production_fields(self):
        s = T6.x06_schema()
        req = s["schema"]["properties"]["items"]["items"]["required"]
        i = req.index("japanese_gloss")
        self.assertEqual(req[i - 3:i], ["meaning_in_text_en", "naive_ja", "naive_ja_conveys"])
        self.assertTrue(set(ga.GLOSS_ALIGNMENT_JSON_SCHEMA["schema"]["properties"]["items"]["items"]["required"]) <= set(req))
        self.assertEqual(ga.GLOSS_ALIGNMENT_JSON_SCHEMA["name"] == s["name"], False)

    def test_detect_import_record_only(self):
        d = T6.detect_import
        self.assertIn("neg_in_gloss_not_in_kp", d("add up", "つじつまが合わない"))
        self.assertEqual(d("add up", "つじつまが合う"), [])
        self.assertEqual(d("an unseen clock", "見えない時計"), [])          # un- 語はKP側に否定あり
        self.assertEqual(d("without asking for another promise", "改めて約束を求めずに"), [])
        self.assertIn("past_tense_ending", d("move in the other direction", "売れ行きは逆に下がった"))
        self.assertEqual(d("pull back", "いったん取りやめる"), [])

    def test_groups_cap_keeps_eval_keys(self):
        keys = T6.keys_of(_ns(set="S2"))
        g5 = T6.build_groups(keys, True, 5)
        self.assertTrue(all(len(g["targets"]) <= 5 or len(g["eval_keys"]) > 5 for g in g5))
        got = {k for g in g5 for k in g["eval_keys"]}
        self.assertEqual(got, {k.lower() for k in keys})
        for g in g5:
            self.assertEqual([t["rank"] for t in g["targets"]], list(range(1, len(g["targets"]) + 1)))
            for t in g["targets"]:
                self.assertIsNone(t["japanese_gloss"])
                self.assertTrue(ga.is_fulltext_gloss_missing(t))          # Productionの新規生成itemと同形(全文選定・gloss未生成)

    def test_hardcore_set_predefined_and_independent_of_outputs(self):
        hc = T6.hc_kps()
        self.assertTrue(6 <= len(hc) <= 10)
        import er112_kp_gm_trial_04 as X4
        used = {k.lower() for k in X4.all_kps()} | {k.lower() for k in T5.R_KEYS}
        used |= {k.lower() for k in T5.heldout_order()[:10]}
        self.assertFalse({k.lower() for k in hc} & used)                  # 設計に使った/評価に使ったKPを含まない
        src = (T6.OUT6 / "hardcore_select_06.py").read_text(encoding="utf-8")
        self.assertNotIn("results.jsonl", src)
        self.assertNotIn("paid_calls", src)

    def test_harness_never_writes_to_production_modules(self):
        """harnessのファイル書込箇所(write_text/open(w)/_append)がProduction module(er003_/er019_/er026_/er105_)のpathを対象にしない。
        (Production非編集の実証は prodhash start/end の一致と `git diff` をruntime evidenceに記録する。gitの状態に依存するtestは作らない=恒常flake防止)"""
        import re
        src = (ROOT / "er112_kp_gm_trial_06.py").read_text(encoding="utf-8").splitlines()
        for ln in src:
            if re.search(r"write_text|\.write\(|open\([^)]*[\"']w|_append\(", ln) and not ln.lstrip().startswith(("#", "def ")):
                self.assertNotRegex(ln, r"er003_|er019_|er026_|er105_|er009_")

    def test_cost_fit_positive(self):
        f = T6.cost_fit()
        for arm in T6.ARMS:
            self.assertGreater(T6.est_call(arm, 5, f), T6.est_call(arm, 1, f) - 1e-9)
            self.assertGreater(f[arm]["a"], 0)


class _Usage:
    input_tokens = 3000
    output_tokens = 900
    class input_tokens_details:
        cached_tokens = 0
    class output_tokens_details:
        reasoning_tokens = 500


class _Resp:
    def __init__(self, items):
        self.usage = _Usage()
        self.model = T.LUNA
        self.output_text = json.dumps({"items": items}, ensure_ascii=False)
        self.id = "fake"


class _FakeOpenAI:
    """API呼出0。呼ばれたmessage/schemaを記録し、rankごとに有効なitemを返す(1回目だけ rank1 を qa=FAIL にして retry を発生させるモード付き)。"""
    def __init__(self, fail_first_rank1=False, with_meaning=True):
        self.responses = self
        self.inputs, self.schemas, self.n = [], [], 0
        self.fail_first_rank1, self.with_meaning = fail_first_rank1, with_meaning

    def create(self, **kw):
        import re as _re
        self.n += 1
        msg = kw["input"][1]["content"]
        self.inputs.append((kw["input"][0]["content"], msg))
        self.schemas.append(kw["text"]["format"]["name"])
        ranks = [int(x) for x in _re.findall(r'"rank": (\d+)', msg.split("【対象項目】")[1].split("【記事本文")[0])]
        items = []
        for r in ranks:
            it = {"rank": r, "current_gloss_consistent": False, "japanese_gloss": "テスト訳" + "アイウエオカキクケコ"[r % 10],
                  "qa_reflects_all_key_phrase_words": "FAIL" if (self.fail_first_rank1 and self.n == 1 and r == 1) else "PASS",
                  "reasoning": "r", "added_word_mappings": []}
            if self.with_meaning:
                it.update({"meaning_in_text_en": "m", "naive_ja": "n", "naive_ja_conveys": "no"})
            items.append(it)
        return _Resp(items)


class T06Harness(unittest.TestCase):
    def _group(self):
        keys = ["add up", "run on"]
        return T6.build_groups(keys, True, 5)[0]

    def test_run_group_x2pp_with_fake_client_and_retry_prior(self):
        g = self._group()
        fake = _FakeOpenAI(fail_first_rank1=True)
        rows, calls = T6.run_group("X2pp", 1, g, "t", T6.RecClient(fake))
        self.assertEqual(len(calls), 2)                                    # attempt 1(全件) + attempt 2(rank1のみ)
        self.assertEqual(fake.schemas, ["kp_gloss_x2pp_trial06"] * 2)
        self.assertEqual(fake.inputs[0][0], T6.G.M_DEVELOPER)
        self.assertNotIn("previous_attempt_rejected(", fake.inputs[0][1])
        self.assertIn("previous_attempt_rejected(", fake.inputs[1][1])      # prior再提示
        self.assertEqual(len([r for r in rows if r["is_eval"]]), 2)
        self.assertTrue(all(r["gloss"] for r in rows))
        self.assertEqual(rows[0]["meta"]["attempts"], 2)
        self.assertEqual(rows[0]["meta"]["status"], "ALIGN_PASS")

    def test_run_group_b0p_uses_production_path_with_fake_client(self):
        g = self._group()
        fake = _FakeOpenAI(with_meaning=False)
        rows, calls = T6.run_group("B0p", 1, g, "t", T6.RecClient(fake))
        self.assertEqual(len(calls), 1)
        self.assertEqual(fake.schemas, [ga.GLOSS_ALIGNMENT_JSON_SCHEMA["name"]])          # Production schema
        self.assertEqual(fake.inputs[0][0], ga.DEVELOPER_MESSAGE)                           # Production developer message
        self.assertIn(ga.preflight(True)["rules_fulltext"], fake.inputs[0][1])              # rules_fulltext自動選択
        self.assertEqual(rows[0]["meta"]["status"], "ALIGN_PASS")
        self.assertTrue(all(r["gloss"] for r in rows))

    def test_x2pp_invalid_when_new_fields_missing(self):
        g = self._group()
        fake = _FakeOpenAI(with_meaning=False)                      # 旧schema相当の応答(新欄なし)を新経路が受けたらINVALID -> 安全側に止まる(WC-07相当)
        rows, calls = T6.run_group("X2pp", 1, g, "t", T6.RecClient(fake))
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(r["gloss"] is None for r in rows))
        self.assertEqual(rows[0]["meta"]["status"], "UNRESOLVED")


if __name__ == "__main__":
    unittest.main()
