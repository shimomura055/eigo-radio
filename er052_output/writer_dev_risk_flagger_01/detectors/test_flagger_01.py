# -*- coding: utf-8 -*-
"""委任_01B -> 委任_02 P0 ユニットテスト(API不要)。実行: python -X utf8 -m unittest test_flagger_01 (detectors/ で)"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate_flagger_01 as AG  # noqa: E402
import d0_directional as D0  # noqa: E402
import flagger_lib as L  # noqa: E402
import ledger_restore_01 as LR  # noqa: E402
import make_blind_01 as MB  # noqa: E402
import prompts_flagger as P  # noqa: E402
import run_flagger_01 as R  # noqa: E402

FACT = ("MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、"
        "機能を当面ロールバックしたと社内投稿で説明した。")
K01 = "The company also restored the human concierge feature to the way it had been before, at least for now."
K03 = "They also temporarily put back the feature in which humans handled the calls."
K12 = "The human concierge feature was then put on hold for the time being."
K02S = "Nor has anyone reported that an AI got out of the test environment."
OTHER_FACT = "Acme社は2025年に200人を採用した。"


def unit(sentence, fact=FACT, uid="u1", extra_facts=()):
    facts = [dict(fact_id="F1", text=fact)] + [dict(fact_id="X%d" % i, text=t) for i, t in enumerate(extra_facts)]
    return dict(unit_id=uid, facts=facts, sentences=[dict(sid="s1", text=sentence, before="", after="")])


def raw_casebank():
    """実スキーマ(fact{id,text,src}, context{before,after,source}, ラベル各種)のミニcasebank。"""
    def case(cid, sentence, label, basis, atype, split, legacy, **kw):
        c = dict(case_id=cid, legacy_ids=legacy, label=label, label_basis=basis, label_basis_detail="x", label_src="a/labels.md L1",
                 accident_type=atype, lang="EN", fact=dict(id="MUSE-HC-012", text="[VERIFIED] MUSE-HC-012: " + FACT, src="no/such/ledger.txt L1"),
                 sentence=sentence, context=dict(before="B.", after="A.", source="x/labels_merged.json"),
                 sentence_locator="x/article.md:3", article_full_text="x/article.md", near_dup_group=None, secondary_type=None,
                 notes="n", synthetic=False, split=split, legacy_case_id="zz", ja_counterpart=None)
        c.update(kw)
        return c
    return dict(cases=[
        case("c1", K01, "重大", "ユーザー確認", "rollback方向反転", "holdout", ["WE-K01"]),
        case("c2", K12, "非重大", "ユーザー確認", "(なし)", "dev", ["WE-K12"]),
        case("c3", K03, "重大", "ユーザー確認", "rollback方向反転", "dev", ["WE-K03"]),
        case("c4", "A plain sentence.", "非重大", "Sonnet判定", "(なし)", "dev", ["RC-K05"]),
        case("c5", "Another border sentence.", "非重大", "Sonnet判定", "(境界)", "dev", ["B-02"]),
    ], synthetic_reference=[
        dict(syn_id="S-12", fact_id="MUSE-HC-012", ledger_text="[VERIFIED] MUSE-HC-012: " + FACT, sentence="For now, Meta has restored the human concierge feature.",
             accident_type="rollback方向反転", label="重大(人工反転)", label_basis="Fable確定", src="s", origin="o", note="n", split="dev"),
        dict(syn_id="S-04", fact_id="HF-009", ledger_text="[VERIFIED] HF-009: 価格は戻った。", sentence="Prices left.",
             accident_type="数量時系列", label="重大(人工反転)", label_basis="Fable確定", src="s", origin="o", note="n", split="holdout"),
    ])


class D0Test(unittest.TestCase):
    def test_k01_k03_flagged_rollback(self):
        for s in (K01, K03):
            fl = D0.detect(unit(s))
            self.assertTrue(any(f["type"] == "rollback反転" and f["severity"] == "重大" and not f["gate_only"] for f in fl), s)

    def test_the_way_it_had_been_not_in_vocabulary(self):
        # K01は語彙設計時に参照した回帰テスト(汚染済み)。専用の語『the way it had been』は語彙から削除済み。
        for w in D0.GROUPS["rollback反転"]["R"]:
            self.assertNotIn("the way it had been", w)
        self.assertEqual(D0.side_hits("It is the way it had been.", "rollback反転")["R"], [])

    def test_faithful_sentence_not_flagged(self):
        self.assertEqual(D0.detect(unit(K12)), [])

    def test_japanese_k04(self):
        s = "人間コンシェルジュ機能を当面、以前の状態に戻しました。"
        self.assertTrue(any(f["type"] == "rollback反転" for f in D0.detect(unit(s))))

    def test_reverse_direction(self):
        f = "The company restored the feature on Monday."
        fl = D0.detect(unit("The company withdrew the feature on Monday.", fact=f))
        self.assertTrue(any(x["type"] == "rollback反転" for x in fl))

    def test_block_is_not_blockade_prefix_match(self):
        self.assertEqual(D0.side_hits("Iran announced a naval blockade of the strait.", "許可禁止反転")["W"], [])
        self.assertEqual(D0.side_hits("Regulators blocked the deal.", "許可禁止反転")["W"], ["block"])
        self.assertEqual(D0.side_hits("They halted production.", "rollback反転")["W"], ["halt"])
        self.assertEqual(D0.side_hits("The wall was restored.", "rollback反転")["R"], ["restore", "restored"])

    def test_absence_cue_is_gate_only_and_general_negation_excluded(self):
        fl = D0.detect(unit(K02S, fact="Anthropic reported three incidents of unauthorized access."))
        ab = [x for x in fl if x["type"] == "不在断定"]
        self.assertTrue(ab and all(x["gate_only"] for x in ab))
        self.assertFalse(any(x["type"] == "不在断定" for x in D0.detect(unit("The firm did not raise prices and has not slept.", fact="x"))))

    def test_quantity_uses_whole_ledger_and_is_gate_only(self):
        fl = D0.detect(unit("About 300 people joined in 2025.", fact="About 200 people joined in 2025."))
        q = [x for x in fl if x["type"] == "数量時系列"]
        self.assertTrue(q and q[0]["gate_only"])
        fl2 = D0.detect(unit("About 200 people joined in 2025.", fact="About 200 people joined in 2025."))
        self.assertFalse(any(x["type"] == "数量時系列" for x in fl2))
        # 台帳の別Factに数値があれば誤Flagしない(台帳全体と照合)
        fl3 = D0.detect(unit("About 300 people joined.", fact="About 200 people joined.", extra_facts=["Another fact: 300 staff."]))
        self.assertFalse(any(x["type"] == "数量時系列" for x in fl3))

    def test_flag_has_required_fields(self):
        f = D0.detect(unit(K01))[0]
        for k in ("unit_id", "sentence_id", "type", "fact_ids", "confidence", "severity", "question", "basis", "gate_only"):
            self.assertIn(k, f)
        self.assertTrue(f["question"].endswith("。"))

    def test_cross_language_all_pairs(self):
        # 英文×日本語台帳: 重なり語がなくても『方向語を含む文×方向語を含むFact』で総当たり照合される
        facts = [dict(fact_id="A", text="Acme社は200人を採用した。"), dict(fact_id="B", text="Zeta社はOrionサービスを撤回した。")]
        u = dict(unit_id="x", facts=facts, sentences=[dict(sid="s1", text="The firm restored the service last week.")])
        fl = D0.detect(u)
        self.assertTrue(any(x["fact_ids"] == ["B"] and x["type"] == "rollback反転" for x in fl))

    def test_gate_types_rule(self):
        g = D0.gate_types(unit("A plain sentence about nothing."))
        self.assertEqual(g, {"主体対象入替", "否定反転"})
        g2 = D0.gate_types(unit(K02S + " It rose 20 percent."))
        self.assertTrue({"不在断定", "数量時系列"} <= g2)
        self.assertIn("rollback反転", D0.gate_types(unit(K03)))


class ValidateTest(unittest.TestCase):
    def good(self, **kw):
        d = dict(sentence_id="s1", type="rollback反転", fact_ids=["F1"], confidence=0.8, severity="重大", question="向きは台帳どおりですか。")
        d.update(kw)
        return json.dumps({"flags": [d]}, ensure_ascii=False)

    def test_ok(self):
        fl, v = R.validate_flags(self.good(), unit(K01), ("rollback反転",))
        self.assertEqual(v, [])
        self.assertEqual(fl[0]["sentence"], K01)

    def test_empty_flags_ok(self):
        fl, v = R.validate_flags('{"flags":[]}', unit(K01))
        self.assertEqual((fl, v), ([], []))

    def test_bad_cases(self):
        u = unit(K01)
        self.assertIsNone(R.validate_flags("not json", u)[0])
        for key, val, code in (("sentence_id", "s9", "flag0_sentence_id_invalid"), ("fact_ids", ["Z"], "flag0_fact_ids_invalid"),
                               ("confidence", 1.5, "flag0_confidence_invalid"), ("question", "", "flag0_question_missing")):
            self.assertIn(code, R.validate_flags(self.good(**{key: val}), u)[1])
        self.assertIn("flag0_type_invalid", R.validate_flags(self.good(type="否定反転"), u, ("rollback反転",))[1])

    def test_wrapped_json_rescued(self):
        fl, v = R.validate_flags("結果です\n" + self.good() + "\n以上", unit(K01))
        self.assertEqual(v, [])

    def test_d1_max_flags_truncates_by_confidence(self):
        u = dict(unit_id="u", facts=[dict(fact_id="F1", text="t")], sentences=[dict(sid="s%d" % i, text="x") for i in range(1, 6)])
        flags = [dict(sentence_id="s%d" % i, type="数量時系列", fact_ids=["F1"], confidence=c, severity="重大", question="q。")
                 for i, c in zip(range(1, 6), (0.2, 0.9, 0.5, 0.7, 0.1))]
        fl, v = R.validate_flags(json.dumps({"flags": flags}), u, ("数量時系列",), max_flags=3)
        self.assertEqual(v, [])
        self.assertEqual([x["confidence"] for x in fl], [0.9, 0.7, 0.5])

    def test_d2rank_requires_exact_n_distinct(self):
        u = dict(unit_id="u", facts=[dict(fact_id="F1", text="t")], sentences=[dict(sid="s%d" % i, text="x") for i in range(1, 6)])
        mk = lambda sid, r: dict(rank=r, sentence_id=sid, type="その他", fact_ids=["F1"], confidence=0.3, severity="非重大",  # noqa: E731
                                 mismatch_terms=["a", "b"], question="q。")
        ok = json.dumps({"flags": [mk("s1", 1), mk("s2", 2), mk("s3", 3)]})
        fl, v = R.validate_flags(ok, u, rank_n=3)
        self.assertEqual(v, [])
        self.assertEqual(fl[0]["mismatch_terms"], ["a", "b"])
        self.assertIn("rank_count_2_expected_3", R.validate_flags(json.dumps({"flags": [mk("s1", 1), mk("s2", 2)]}), u, rank_n=3)[1])
        self.assertIn("rank_duplicate_sentence_id", R.validate_flags(json.dumps({"flags": [mk("s1", 1), mk("s1", 2), mk("s3", 3)]}), u, rank_n=3)[1])


class SchemaAndBlindTest(unittest.TestCase):
    def test_case_to_unit_real_schema_hides_src_source_notes(self):
        raw = raw_casebank()["cases"][0]
        u = R.case_to_unit(raw)
        self.assertEqual(u["unit_id"], "c1")
        self.assertEqual(u["sentences"][0]["before"], "B.")
        self.assertEqual(u["sentences"][0]["after"], "A.")
        msg = P.build_user(u)
        for w in ("labels_merged", "no/such", "article.md", "label", "WE-K01", "ユーザー確認", "rollback方向反転", "source", "src", "locator"):
            self.assertNotIn(w, msg)
        self.assertIn(K01, msg)

    def test_make_blind_splits_and_strips(self):
        blind, labels, report = MB.split_casebank(raw_casebank())
        self.assertEqual(sorted(blind), ["dev", "holdout", "synthetic_dev", "synthetic_holdout"])
        self.assertEqual([c["case_id"] for c in blind["dev"]], ["c2", "c3", "c4", "c5"])
        allowed = {"case_id", "lang", "fact", "sentence", "context", "ledger", "ledger_complete"}
        for sp, cs in blind.items():
            self.assertEqual(R.check_no_labels({"cases": cs}), [], sp)
            for c in cs:
                self.assertTrue(set(c) <= allowed, set(c) - allowed)
                self.assertEqual(set(c["fact"]), {"id", "text"})
                self.assertEqual(set(c["context"]), {"before", "after"})
        # ラベル側に全情報
        self.assertEqual(labels["c1"]["accident_type"], "rollback方向反転")
        self.assertEqual(labels["c1"]["known_incident"], "Rollback方向反転")
        self.assertEqual(labels["c2"]["neg_group"], "hard_negative")
        self.assertEqual(labels["c5"]["neg_group"], "boundary")
        self.assertEqual(labels["c4"]["neg_group"], "clear")
        self.assertEqual(labels["S-04"]["accident_type"], "方向反転(別Fact)")
        self.assertEqual(labels["S-12"]["accident_type"], "rollback方向反転")
        self.assertEqual(labels["S-12"]["split"], "synthetic_dev")

    def test_label_keys_cover_required_and_runner_shares_them(self):
        for k in ("label_basis", "label_basis_detail", "label_src", "accident_type", "notes", "near_dup_group", "legacy_ids",
                  "synthetic", "split", "known_incident", "label"):
            self.assertIn(k, MB.LABEL_KEYS)
            self.assertIn(k, R.FORBIDDEN_KEYS)

    def test_runner_refuses_labeled_input_each_key(self):
        for key in ("label_basis", "label_src", "accident_type", "notes", "near_dup_group", "legacy_ids", "synthetic", "split"):
            bad = {"cases": [dict(case_id="c", sentence="s", fact=dict(id="F", text="t"), **{key: "x"})]}
            self.assertTrue(R.check_no_labels(bad), key)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "cb.json")
            json.dump(raw_casebank(), open(p, "w", encoding="utf-8"), ensure_ascii=False)
            with self.assertRaises(ValueError):
                R.load_units(p)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.main(["--input", p, "--detector", "d0", "--set", "t"])
            self.assertEqual(rc, 2)

    def test_runner_source_never_opens_labels_file(self):
        src = open(os.path.join(HERE, "run_flagger_01.py"), encoding="utf-8").read()
        self.assertNotIn("_labels.json\"", src)
        self.assertNotIn("labels_path", src)

    def test_prompt_contains_no_label_info(self):
        blind, _l, _r = MB.split_casebank(raw_casebank())
        u = R.case_to_unit(blind["holdout"][0])
        msg = P.build_user(u)
        for w in ("重大", "known_incident", "label", "type_label", "WE-K", "ユーザー確認"):
            self.assertNotIn(w, msg)


class LedgerRestoreTest(unittest.TestCase):
    def test_parse_and_restore(self):
        txt = ("[VERIFIED] A-1: 文A。\n  scope: s\n  notes_for_writer: n\n\n[VERIFIED] A-2: 文B。\n  scope: t\n")
        facts = LR.parse_ledger_text(txt)
        self.assertEqual([f["fact_id"] for f in facts], ["A-1", "A-2"])
        self.assertTrue(facts[0]["text"].startswith("文A。\n  scope: s"))
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "verified_fact_ledger.txt")
            open(p, "w", encoding="utf-8").write(txt)
            rel = os.path.relpath(p, LR.REPO).replace("\\", "/") if p.startswith(LR.REPO) else p
            self.assertIsNotNone(LR._src_path(p + " L1") if os.path.isabs(p) else LR._src_path(rel + " L1"))


class RunnerTest(unittest.TestCase):
    def _blind_path(self, d, split="dev"):
        blind, _l, _r = MB.split_casebank(raw_casebank())
        p = os.path.join(d, "cb_%s_blind.json" % split)
        json.dump({"cases": blind[split]}, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return p

    def test_d0_end_to_end_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._blind_path(d)
            old = R.RESULTS_DIR
            R.RESULTS_DIR = os.path.join(d, "results")
            try:
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(R.main(["--input", p, "--detector", "d0", "--set", "t"]), 0)
                    self.assertEqual(R.main(["--input", p, "--detector", "d0", "--set", "t"]), 3)  # 上書き禁止
                rows = [json.loads(x) for x in open(os.path.join(R.RESULTS_DIR, "d0_none_t.jsonl"), encoding="utf-8")]
            finally:
                R.RESULTS_DIR = old
        by = {r["unit_id"]: r for r in rows}
        self.assertTrue(by["c3"]["flags"])   # K03
        self.assertEqual(by["c2"]["flags"], [])  # K12 忠実文
        self.assertEqual(by["c3"]["cost_jpy"], 0.0)

    def test_llm_requires_max_yen_and_dry_run_no_api(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._blind_path(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(R.main(["--input", p, "--detector", "d2", "--set", "t"]), 2)
                self.assertEqual(R.main(["--input", p, "--detector", "d1full", "--set", "t", "--dry-run"]), 0)
                self.assertEqual(R.main(["--input", p, "--detector", "d2rank", "--set", "t"]), 2)  # 記事モード専用
            out = buf.getvalue()
            self.assertIn("REFUSED", out)
            self.assertIn("呼び出し数(最小)=20", out)  # 4 units x 5 types (D1mapは廃止、D1fullのみ)

    def test_d1map_removed(self):
        self.assertNotIn("d1map", R.ALL_DETECTORS)

    def test_plan_calls_modes(self):
        facts = [dict(fact_id="A", text="Acme raised 50 million dollars in 2024."),
                 dict(fact_id="B", text="Zeta Corp suspended the Orion service."),
                 dict(fact_id="C", text="Foo Inc hired 10 staff."), dict(fact_id="D", text="Bar Ltd closed.")]
        u = dict(unit_id="x", mode="case", facts=facts, sentences=[dict(sid="s1", text="Zeta Corp restored the Orion service.")])
        full = R.plan_calls("d1full", u)
        self.assertEqual(len(full), 5)
        self.assertEqual(len(R.plan_calls("d2", u)), 1)
        self.assertEqual(len(json.loads(full[0][2])["facts"]), 4)  # 全台帳
        self.assertEqual(full[0][4], P.D1_MAX_FLAGS)  # Flag上限3
        gated = R.plan_calls("d1full", u, gate="d0")
        self.assertEqual({c[0] for c in gated}, {"d1:主体対象入替", "d1:否定反転", "d1:rollback反転"})  # 数値・不在cueなし
        self.assertEqual(len(R.plan_calls("d1full", u, types=["数量時系列"])), 1)

    def test_article_mode_units_keep_headings(self):
        with tempfile.TemporaryDirectory() as d:
            lp, ap_ = os.path.join(d, "l.json"), os.path.join(d, "a.md")
            json.dump({"facts": [dict(fact_id="F1", text="Acme paused the plan.")]}, open(lp, "w"))
            open(ap_, "w", encoding="utf-8").write("# Title\nAcme resumed the plan. It was big.\n\nNext para.")
            us = R.load_units(ledger=lp, article=ap_)
        self.assertEqual(len(us), 1)
        self.assertEqual(us[0]["mode"], "article")
        self.assertEqual([s["text"] for s in us[0]["sentences"]], ["# Title", "Acme resumed the plan.", "It was big.", "Next para."])

    def test_article_mode_d2rank_plan(self):
        u = dict(unit_id="x", mode="article", facts=[dict(fact_id="F1", text="t")],
                 sentences=[dict(sid="s%d" % i, text="x") for i in range(1, 8)])
        c = R.plan_calls("d2rank", u)
        self.assertEqual(c[0][5], 3)
        self.assertIn("ちょうど3文", c[0][1])
        u2 = dict(u, sentences=u["sentences"][:2])
        self.assertEqual(R.plan_calls("d2rank", u2)[0][5], 2)


class UnionTest(unittest.TestCase):
    def fl(self, t, c, sid="s1", q="q。", gate=False):
        return dict(unit_id="u", sentence_id=sid, type=t, fact_ids=["F1"], confidence=c, severity="重大", question=q, gate_only=gate)

    def test_dedup_and_keep_distinct_types(self):
        out = R.union_flags([("d0", [self.fl("rollback反転", 0.7, q="a。")]),
                             ("d1full", [self.fl("rollback反転", 0.9, q="b。"), self.fl("否定反転", 0.5)])])
        self.assertEqual(len(out), 2)
        rb = [x for x in out if x["type"] == "rollback反転"][0]
        self.assertEqual(rb["confidence"], 0.9)
        self.assertEqual(rb["question"], "b。")
        self.assertEqual(sorted(rb["sources"]), ["d0", "d1full"])

    def test_d0_gate_only_excluded_from_union(self):
        out = R.union_flags([("d0", [self.fl("不在断定", 0.35, gate=True), self.fl("数量時系列", 0.3, sid="s2", gate=True),
                                      self.fl("rollback反転", 0.6, sid="s3")]), ("d2", [])])
        self.assertEqual([x["type"] for x in out], ["rollback反転"])
        out2 = R.union_flags([("d0", [self.fl("不在断定", 0.35, gate=True)])], include_gate_only=True)
        self.assertEqual(len(out2), 1)


class AggregateTest(unittest.TestCase):
    LABELS = {
        "h1": dict(label="重大", label_basis="ユーザー確認", accident_type="rollback方向反転", known_incident="Rollback方向反転", split="dev", legacy_ids=["WE-K03"]),
        "h2": dict(label="重大", label_basis="Sonnet判定", accident_type="不在断定", split="dev", legacy_ids=["x"]),
        "s1": dict(label="重大", label_basis="Fable確定", accident_type="方向反転(別Fact)", split="dev", legacy_ids=["S-04"]),
        "n1": dict(label="非重大", label_basis="Sonnet判定", accident_type="(なし)", neg_group="clear", split="dev", legacy_ids=["a"]),
        "n2": dict(label="非重大", label_basis="Sonnet判定", accident_type="(境界)", neg_group="boundary", split="dev", legacy_ids=["b"]),
        "n3": dict(label="非重大", label_basis="ユーザー確認", accident_type="(なし)", neg_group="hard_negative", split="dev", legacy_ids=["S0-2"]),
        "o1": dict(label="重大", label_basis="ユーザー確認", accident_type="主体対象入替", split="holdout", legacy_ids=["y"]),
    }

    def rows(self):
        f = lambda c=0.7, sid="s1", t="rollback反転": [dict(type=t, sentence_id=sid, confidence=c, severity="重大")]  # noqa: E731
        return [dict(unit_id="h1", flags=f(), valid_json=True, cost_jpy=1.0), dict(unit_id="h2", flags=[], valid_json=True, cost_jpy=1.0),
                dict(unit_id="s1", flags=f(0.2), valid_json=True, cost_jpy=0.5),
                dict(unit_id="n1", flags=f() + f(sid="s2", t="数量時系列"), valid_json=True, cost_jpy=0.5),
                dict(unit_id="n2", flags=[], valid_json=True, cost_jpy=0),
                dict(unit_id="n3", flags=f(), valid_json=True, cost_jpy=0),
                dict(unit_id="o1", flags=f(), valid_json=True, cost_jpy=9)]

    def test_split_and_primary_secondary_recall(self):
        r = AG.aggregate(self.LABELS, self.rows(), split="dev")
        self.assertEqual(r["n_units"], 6)
        self.assertEqual((r["n_severe"], r["n_human"]), (3, 1))
        self.assertEqual((r["recall_human"]["k"], r["recall_human"]["n"]), (1, 1))
        self.assertEqual((r["recall_all"]["k"], r["recall_all"]["n"]), (2, 3))
        self.assertEqual(r["missed_severe"], ["h2"])
        self.assertAlmostEqual(r["cost_jpy"], 3.0)  # holdout行(o1=9)は含めない

    def test_fpr_groups_and_flag_counts(self):
        r = AG.aggregate(self.LABELS, self.rows(), split="dev")
        self.assertEqual((r["fpr_clear"]["k"], r["fpr_clear"]["n"]), (1, 1))
        self.assertEqual((r["fpr_boundary"]["k"], r["fpr_boundary"]["n"]), (0, 1))
        self.assertEqual((r["fpr_hard_negative"]["k"], r["fpr_hard_negative"]["n"]), (1, 1))
        # Flag数: (unit,sentence,type) 6 = h1:1 s1:1 n1:2 n3:1 / 固有文: h1:s1, s1:s1, n1:s1,s2, n3:s1 = 5
        self.assertEqual(r["flags_utype"], 5)
        self.assertEqual(r["flags_unique_sentences"], 5)
        self.assertEqual(r["fp_cases_hard_negative"], ["n3"])

    def test_same_sentence_two_types_counted_separately(self):
        rows = [dict(unit_id="n1", flags=[dict(type="a", sentence_id="s1", confidence=.5, severity="重大"),
                                          dict(type="b", sentence_id="s1", confidence=.5, severity="重大")], valid_json=True, cost_jpy=0)]
        r = AG.aggregate(self.LABELS, rows, split="dev")
        self.assertEqual((r["flags_utype"], r["flags_unique_sentences"]), (2, 1))

    def test_accident_type_known_incident_rollback_synthetic(self):
        r = AG.aggregate(self.LABELS, self.rows(), split="dev")
        self.assertEqual(r["recall_by_type"]["rollback方向反転"]["hit"], 1)
        self.assertEqual(r["recall_by_type"]["不在断定"]["hit"], 0)
        self.assertEqual(r["known_incidents"]["Rollback方向反転"]["hit"], 1)
        self.assertEqual((r["rollback"]["hit"], r["rollback"]["n"]), (1, 1))
        self.assertEqual((r["synthetic_direction_reversal"]["hit"], r["synthetic_direction_reversal"]["n"]), (1, 1))

    def test_min_conf_and_sweep(self):
        r = AG.aggregate(self.LABELS, self.rows(), split="dev", min_conf=0.5)
        self.assertEqual((r["recall_all"]["k"], r["recall_all"]["n"]), (1, 3))  # s1(0.2)が閾値で落ちる
        sw = AG.conf_sweep(self.LABELS, self.rows(), (0.0, 0.5, 0.9), split="dev")
        self.assertEqual([s["recall_all"]["k"] for s in sw], [2, 1, 0])
        self.assertIn("閾値曲線", AG.sweep_markdown("x", sw))

    def test_wilson(self):
        lo, hi = AG.wilson(8, 11)
        self.assertTrue(0.4 < lo < 0.5 and 0.85 < hi < 0.95, (lo, hi))
        self.assertIsNone(AG.wilson(0, 0))

    def test_s0_flip_recomputation_rule(self):
        base = AG.aggregate(self.LABELS, self.rows(), split="dev")
        flipped = AG.aggregate(self.LABELS, self.rows(), split="dev", s0_flip=["S0-2"])
        self.assertEqual(flipped["n_severe"], base["n_severe"] + 1)
        self.assertEqual(flipped["n_human"], base["n_human"] + 1)  # ユーザー確認の重大へ
        self.assertEqual(flipped["fpr_hard_negative"]["n"], base["fpr_hard_negative"]["n"] - 1)
        self.assertEqual((flipped["recall_all"]["k"], flipped["recall_all"]["n"]), (3, 4))  # n3はFlag済み=ヒット

    def test_exclude_gate_only(self):
        rows = [dict(unit_id="h2", flags=[dict(type="不在断定", sentence_id="s1", confidence=.35, severity="重大", gate_only=True)],
                     valid_json=True, cost_jpy=0)]
        self.assertEqual(AG.aggregate(self.LABELS, rows, split="dev")["recall_all"]["k"], 1)
        self.assertEqual(AG.aggregate(self.LABELS, rows, split="dev", exclude_gate_only=True)["recall_all"]["k"], 0)

    def test_markdown_contains_primary_columns(self):
        md = AG.to_markdown([("x", AG.aggregate(self.LABELS, self.rows(), split="dev"))])
        for w in ("Recall_human(主)", "Recall_all(副)", "FPR_hardneg", "Flag固有文"):
            self.assertIn(w, md)

    def test_article_mode_window_and_top3(self):
        sents = ["# Title", "Acme paused the plan.", "Fine one.", "It restored the plan.", "Tail A.", "Tail B.", "Tail C."]
        flags = [dict(sentence_id="s3", type="rollback反転", confidence=0.8), dict(sentence_id="s7", type="その他", confidence=0.9),
                 dict(sentence_id="s6", type="その他", confidence=0.5), dict(sentence_id="s5", type="その他", confidence=0.4)]
        r = AG.aggregate_article(sents, flags, ["It restored the plan.", "Never located sentence."], window=2, topk=3)
        it = r["items"][0]
        self.assertTrue(it["located"] and it["hit_window"])  # s3は位置4(index3)から-1文
        self.assertEqual(it["rank"], None)                     # 文自体(s4)にはFlagなし
        self.assertEqual(it["best_rank_in_window"], 2)         # 窓内(index1..5)では s3(0.8)が全体2位
        self.assertTrue(it["in_topk"])
        self.assertFalse(r["items"][1]["located"])
        self.assertEqual(r["n_located"], 1)
        self.assertEqual(r["flags_unique_sentences"], 4)


class CostGuardTest(unittest.TestCase):
    def test_prices_registered_and_latest_only(self):
        for m in L.MODELS:
            self.assertIsNotNone(L.load_prices(m), m)
        self.assertEqual(L.load_prices("gpt-6.1-sol"), (2.0, 0.1, 10.0))
        self.assertEqual(L.load_prices("deepseek-v4-pro"), (1.32, 0.044, 3.96))
        for old in ("gpt-5.6-sol", "gpt-5.6-luna", "gpt-6-luna", "deepseek-v4-flash"):
            self.assertNotIn(old, L.MODELS)  # 最新原則: 旧モデルは使わない
        self.assertIsNone(L.load_prices("gpt-99-mystery"))

    def test_cost_formula(self):
        p = L.load_prices("gpt-6.1-sol")
        self.assertAlmostEqual(L.cost_yen(p, 1_000_000, 1_000_000), (2.0 + 10.0) * L.USD_JPY)

    def test_ledger_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "ledger.jsonl")
            L.ledger_append(dict(cost_jpy=1.5), p)
            L.ledger_append(dict(cost_jpy=2.0), p)
            self.assertAlmostEqual(L.ledger_total(p), 3.5)

    def test_cost_ledger_limits_documented(self):
        doc = open(os.path.join(HERE, "run_flagger_01.py"), encoding="utf-8").read()
        self.assertIn("呼び出し前", doc)
        self.assertIn("過少計上", doc)

    def _units(self):
        blind, _l, _r = MB.split_casebank(raw_casebank())
        return [R.case_to_unit(c) for c in blind["dev"]]

    def test_cap_stops_before_call(self):
        units = self._units()
        with tempfile.TemporaryDirectory() as d:
            oldp, oldr, oldc = L.LEDGER_PATH, R.RESULTS_DIR, L.client_for
            L.LEDGER_PATH = os.path.join(d, "l.jsonl")
            L.ledger_append(dict(cost_jpy=999.0), L.LEDGER_PATH)
            R.RESULTS_DIR, R.LOGS_DIR = os.path.join(d, "r"), os.path.join(d, "lg")
            L.client_for = lambda cfg: object()
            try:
                with redirect_stdout(io.StringIO()):
                    rc = R.run_llm(units, "d2", "gpt-6.1-sol", "t", 10.0, 900.0)
            finally:
                L.LEDGER_PATH, R.RESULTS_DIR, L.client_for = oldp, oldr, oldc
        self.assertEqual(rc, 4)


class FakeLLMTest(unittest.TestCase):
    def _run(self, seq, detector="d2", units=None):
        blind, _l, _r = MB.split_casebank(raw_casebank())
        units = units or [R.case_to_unit(blind["dev"][1])]  # c3 (K03)
        calls = []

        def fake_call(client, model, system, user, max_out=None, effort="medium"):
            calls.append((system, user))
            return seq[min(len(calls) - 1, len(seq) - 1)], dict(input_tokens=1000, output_tokens=500, cached_tokens=0), "rid", model

        with tempfile.TemporaryDirectory() as d:
            saved = (L.LEDGER_PATH, R.RESULTS_DIR, R.LOGS_DIR, L.client_for, L.call_model)
            L.LEDGER_PATH = os.path.join(d, "l.jsonl")
            R.RESULTS_DIR, R.LOGS_DIR = os.path.join(d, "r"), os.path.join(d, "lg")
            L.client_for = lambda cfg: object()
            L.call_model = fake_call
            try:
                with redirect_stdout(io.StringIO()):
                    rc = R.run_llm(units, detector, "gpt-6.1-sol", "t", 50.0, 900.0)
                rows = [json.loads(x) for x in open(os.path.join(R.RESULTS_DIR, "%s_gpt-6.1-sol_t.jsonl" % detector), encoding="utf-8")]
                total = L.ledger_total()
            finally:
                L.LEDGER_PATH, R.RESULTS_DIR, R.LOGS_DIR, L.client_for, L.call_model = saved
        return rc, rows, calls, total

    GOOD = json.dumps({"flags": [dict(sentence_id="s1", type="rollback反転", fact_ids=["MUSE-HC-012"], confidence=0.8,
                                      severity="重大", question="向きは台帳どおりですか。")]}, ensure_ascii=False)

    def test_retry_once_on_bad_format_then_ok(self):
        rc, rows, calls, total = self._run(["garbage", self.GOOD])
        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 2)  # 初回+再呼び出し1回(上限)
        self.assertTrue(rows[0]["valid_json"])
        self.assertEqual(len(rows[0]["flags"]), 1)
        self.assertGreater(total, 0)

    def test_second_failure_gives_up(self):
        rc, rows, calls, _t = self._run(["garbage"])
        self.assertEqual(len(calls), 2)
        self.assertFalse(rows[0]["valid_json"])

    def test_request_to_llm_has_full_ledger_and_no_src(self):
        _rc, _rows, calls, _t = self._run([self.GOOD])
        user = json.loads(calls[0][1])
        self.assertEqual(list(user), ["facts", "sentences"])
        self.assertEqual(user["sentences"][0]["before"], "B.")
        for f in user["facts"]:
            self.assertEqual(set(f), {"fact_id", "text"})
        self.assertNotIn("labels_merged", calls[0][1])

    def test_d1full_runs_five_calls_and_caps_flags(self):
        many = json.dumps({"flags": [dict(sentence_id="s1", type="rollback反転", fact_ids=["MUSE-HC-012"], confidence=c,
                                          severity="重大", question="q。") for c in (0.1, 0.9, 0.5, 0.7)]}, ensure_ascii=False)
        rc, rows, calls, _t = self._run([many], detector="d1full")
        # rollback反転の呼び出し1回は採用(上限3件・確信度順に切り捨て)。他4タイプはtype不一致=形式違反で各1回だけ再呼び出し(5+4=9)
        self.assertEqual(len(calls), 9)
        self.assertEqual([x["confidence"] for x in rows[0]["flags"]], [0.9, 0.7, 0.5])
        self.assertFalse(rows[0]["valid_json"])


class PromptTest(unittest.TestCase):
    def test_d1_prompt_single_type(self):
        for t in P.TYPES:
            s = P.d1_system(t)
            self.assertIn("「%s」" % t, s)
            self.assertIn("1タイプだけ", s)
            self.assertIn("修正案", s)  # 修正案を出さない旨
            self.assertIn("最大3件", s)
        self.assertIn("軽微", P.d2_system())

    def test_d2_prompt_encourages_honest_low_confidence(self):
        self.assertIn("低めの確信度", P.d2_system())

    def test_d2rank_prompt(self):
        s = P.d2rank_system(30)
        for w in ("ちょうど3文", "mismatch_terms", "rank", "問題なし"):
            self.assertIn(w, s)


if __name__ == "__main__":
    unittest.main()
