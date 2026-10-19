# -*- coding: utf-8 -*-
"""ITEM1(FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_05, 2026-10-19): Key Phrase日本語意味の人称・指示対象整合のtest。
JPY0・実API/実TTS呼出なし(LLMはFakeFn、Zはbuild_mock_context)。

構成: (A)共通module(er003_key_words_gloss_alignment)の単体test=決定論の人称語突合(境界付き・再帰許容)/生成用と消費側の対象分離/
adopt_glossへの適用/retry理由の受渡し/kill switch/個別フレーズ分岐なしのGrep、(B)Z stage_kpの人称整合関所の統合test
(初回/reuse/regenerate/HR・provenance更新・_guard経由・--stage tts_*単独のfail-closed)。
"""
from __future__ import annotations

import contextlib
import glob
import io
import json
import os
import re
import shutil
import tempfile
import unittest
import unittest.mock as mock

import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga

REPO = os.path.dirname(os.path.abspath(__file__))


def _item(rank, disp, kp, gloss, reason=None, status=None, sentence="x", beyond=False):
    it = {"rank": rank, "display_phrase": disp, "key_phrase": kp, "used_form": kp, "japanese_gloss": gloss,
          "japanese_gloss_tts": kc.convert_display_gloss_to_tts_text(gloss), "kp_extends_beyond_candidate": beyond,
          "changed_from_display_phrase": disp != kp, "source_sentence": sentence}
    if reason:
        it["normalization_reason"] = reason
    if status:
        it["gloss_alignment_status"] = status
    return it


class FakeFn:
    def __init__(self, payloads, model="gpt-6-luna"):
        self.payloads, self.calls, self.model = list(payloads), 0, model

    def __call__(self):
        self.calls += 1
        p = self.payloads.pop(0)
        return (p if isinstance(p, str) else json.dumps(p, ensure_ascii=False)), self.model, "resp_x"


def _resp(*rows):
    return {"items": [{"rank": r, "current_gloss_consistent": c, "japanese_gloss": g,
                       "qa_reflects_all_key_phrase_words": "PASS", "reasoning": "r", "added_word_mappings": []}
                      for r, c, g in rows]}


class _FlagOn(unittest.TestCase):
    def setUp(self):
        old = ga.GLOSS_ALIGNMENT_ENABLED
        ga.GLOSS_ALIGNMENT_ENABLED = True
        self.addCleanup(setattr, ga, "GLOSS_ALIGNMENT_ENABLED", old)


# ============================================================ (A) 決定論の人称語突合
MISMATCH_CASES = [
    # (英語KP, 日本語意味, 不整合か)
    ("in someone's place", "あなたの代わりに", True),
    ("in someone's place", "君の立場で", True),
    ("in someone's place", "私の代わりに", True),
    ("in someone's place", "彼の代わりに", True),
    ("in someone's place", "誰かの代わりに", False),
    ("in someone's place", "人の立場で", False),
    ("tell someone off", "彼を叱る", True),
    ("tell someone off", "人を叱る", False),
    ("catch someone's attention", "彼女の注意を引く", True),
    ("keep an eye on someone", "彼らを見守る", True),
    ("thank someone", "あなた方に感謝する", True),
    ("thank someone", "私たちに感謝する", True),
    ("at one's own pace", "自分のペースで", False),            # 再帰one's: 自分は許容
    ("pump one's fist", "拳を突き上げる", False),
    ("take care of oneself", "自分自身を大切にする", False),
    ("put oneself in someone's shoes", "自分を人の立場に置く", False),   # 混在型: oneselfがあれば自分許容
    ("put oneself in someone's shoes", "あなたの立場に身を置く", True),
    ("stand in someone's way", "自分の邪魔をする", True),        # someone系のみのKPで自分は不整合
    # 英語側に具体人称がある表現は対象外(検査しない)
    ("tell me off", "私を叱る", False),
    ("thank you", "あなたに感謝する", False),
    ("give someone a piece of your mind", "あなたに文句を言う", False),
    ("each other", "お互い", False),
    # 境界: 漢字語の部分一致(暴君/主君/君主/下僕/私的/公私/彼方/彼岸)は検出しない
    ("serve someone's lord", "暴君に仕える", False),
    ("serve someone", "主君に仕える", False),
    ("obey someone", "君主に従う", False),
    ("serve someone", "下僕として仕える", False),
    ("someone's matter", "私的な問題", False),
    ("someone's matter", "公私の区別", False),
    ("someone", "彼方の人", False),
    ("someone", "彼岸の人", False),
    # 「相手/その人/人」は検出しない(someoneの自然な訳)
    ("someone", "相手", False),
    ("someone", "その人", False),
    # 英語KPに不定の人称が無ければ対象外
    ("right away", "すぐに", False),
    ("based on interviews", "あなたの意見をもとにした", False),
]


class PersonReferenceMismatch(_FlagOn):
    def test_table(self):
        for kp, gloss, expected in MISMATCH_CASES:
            with self.subTest(kp=kp, gloss=gloss):
                self.assertEqual(bool(ga.person_reference_mismatch(kp, gloss)), expected)

    def test_reason_names_kp_gloss_and_word(self):
        r = ga.person_reference_mismatch("in someone's place", "あなたの代わりに")
        self.assertIn("in someone's place", r)
        self.assertIn("あなたの代わりに", r)
        self.assertIn("あなた", r)

    def test_no_phrase_specific_branch_in_module(self):
        """個別フレーズ・個別記事への分岐を持たない(hardcode禁止)。語彙は閉じた表のみ。"""
        src = open(os.path.join(REPO, "er003_key_words_gloss_alignment.py"), encoding="utf-8").read()
        for needle in ("in someone's place", "in your place", "in one's place", "代わりに", "メロス", "Melos", "melos"):
            self.assertNotIn(needle, src, needle)
        # 制約文の例示はcatch someone's attention型の別表現のみ
        self.assertNotIn("place", ga.PERSON_CONSTRAINT_TEXT)

    def test_same_code_path_for_swapped_fixtures(self):
        # fixtureを入れ替えても同一関数で判定される(関数は(kp, gloss)だけを見る)
        self.assertTrue(ga.person_reference_mismatch("lend someone a hand", "彼に手を貸す"))
        self.assertFalse(ga.person_reference_mismatch("lend someone a hand", "人に手を貸す"))


class TargetSeparation(_FlagOn):
    """F1-1: 生成用の対象と消費側(未評価判定)の対象を分離する。"""

    def setUp(self):
        super().setUp()
        self.healthy = _item(1, "shock your wallet", "shock someone's wallet", "財布に響く",
                             reason=ga.PERSON_NORMALIZATION_REASON)
        self.bad = _item(2, "in your place", "in someone's place", "あなたの代わりに", reason=ga.PERSON_NORMALIZATION_REASON)
        self.plain = _item(3, "right away", "right away", "すぐに")
        self.items = [self.healthy, self.bad, self.plain]

    def test_is_person_generalized(self):
        self.assertTrue(ga.is_person_generalized(self.healthy))
        self.assertTrue(ga.is_person_generalized(_item(4, "catch their breath", "catch one's breath", "息を整える")))   # reasonなしでも表の1対1置換
        self.assertFalse(ga.is_person_generalized(self.plain))

    def test_generation_targets_include_all_person_generalized(self):
        ranks = [t["rank"] for t in ga.select_generation_targets(self.items)]
        self.assertEqual(ranks, [1, 2])
        # 従来の選定関数は不変(their->one'sは追加語に数えない)
        self.assertEqual(ga.select_alignment_targets(self.items), [])

    def test_consumer_does_not_stop_healthy_person_generalized(self):
        un = ga.collect_unevaluated({"items": self.items})
        self.assertEqual([x["rank"] for x in un], [2])      # 不整合itemのみ。健全な人称一般化item(rank1)は未評価扱いにしない

    def test_consumer_covers_item_with_status(self):
        """F1-2: statusにかかわらず全itemへ(旧版ALIGNEDで人称語が残るitemも素通りさせない)。"""
        self.bad["gloss_alignment_status"] = ga.STATUS_ALIGNED
        self.assertEqual([x["rank"] for x in ga.collect_unevaluated({"items": self.items})], [2])

    def test_human_resolved_is_warn_only(self):
        self.bad["gloss_alignment_status"] = ga.STATUS_HUMAN_RESOLVED
        self.assertEqual(ga.collect_unevaluated({"items": self.items}), [])
        self.assertEqual(ga.select_person_mismatches(self.items), [])
        w = ga.person_mismatch_warnings(self.items)
        self.assertEqual([x["rank"] for x in w], [2])

    def test_hr_items_are_left_to_collect_unresolved(self):
        self.bad["gloss_alignment_status"] = ga.STATUS_HR_REQUIRED
        self.assertEqual(ga.select_person_mismatches(self.items), [])
        self.assertEqual([x["rank"] for x in ga.collect_unresolved({"items": self.items})], [2])

    def test_kill_switch_off_disables_consumer_check(self):
        ga.GLOSS_ALIGNMENT_ENABLED = False
        self.assertEqual(ga.collect_unevaluated({"items": self.items}), [])

    def test_coffee_real_artifacts_have_zero_consumer_stops(self):
        """健全artifact(Coffee実artifact)で、消費側は人称一般化を理由にSTOPしない(F1-1回帰)。"""
        files = (glob.glob(os.path.join(REPO, "er019_output", "family_x_audio_production_wiring_01", "coffee_prices__*", "*", "key_phrases",
                                        "keywords_canonicalized.json"))
                 + glob.glob(os.path.join(REPO, "er019_output", "coffee_prices", "**", "keywords_canonicalized.json"), recursive=True))
        if not files:
            self.skipTest("Coffee実artifactが無い環境")
        n_generalized = 0
        for f in files:
            doc = json.load(open(f, encoding="utf-8"))
            items = doc.get("items") or []
            n_generalized += sum(1 for it in items if ga.is_person_generalized(it))
            base = [it for it in ga.select_alignment_targets(items) if not it.get("gloss_alignment_status")]
            self.assertEqual(ga.collect_unevaluated(doc), base, f)      # 従来の未評価判定と同一(人称由来の追加STOPは0件)
            self.assertEqual(ga.select_person_mismatches(items), [], f)
        self.assertGreater(n_generalized, 0, "fixtureに人称一般化itemが含まれていること")


class ValidationAndRetry(_FlagOn):
    def setUp(self):
        super().setUp()
        self.target = _item(2, "in your place", "in someone's place", "あなたの代わりに",
                            reason=ga.PERSON_NORMALIZATION_REASON, sentence="he will die in your place.")

    def test_check_applies_to_adopt_gloss_even_when_current_kept(self):
        """F1-3: current_gloss_consistent=真でcurrentを維持しても、採用値(=current)に人称語が残れば不合格。"""
        v = ga.validate_item_corrected(_resp((2, True, "あなたの代わりに"))["items"][0], self.target)
        self.assertFalse(v["valid"])
        self.assertEqual(v["adopt_gloss"], "あなたの代わりに")
        self.assertTrue(any("人称不整合" in r for r in v["reasons"]))

    def test_proposed_with_person_word_is_invalid(self):
        v = ga.validate_item_corrected(_resp((2, False, "君の代わりに"))["items"][0], self.target)
        self.assertFalse(v["valid"])
        self.assertTrue(any("人称不整合" in r for r in v["reasons"]))

    def test_indefinite_gloss_is_valid(self):
        v = ga.validate_item_corrected(_resp((2, False, "誰かの代わりに"))["items"][0], self.target)
        self.assertTrue(v["valid"], v["reasons"])
        self.assertIsNone(v["person_check"])

    def test_prompt_has_constraint_and_person_fields(self):
        msg = ga.build_user_message_corrected([self.target], "ART", rules="RULES")
        self.assertIn(ga.PERSON_CONSTRAINT_TEXT, msg)
        self.assertIn("『誤っている』に当たります", msg)
        self.assertIn('"indefinite_person_tokens_in_key_phrase"', msg)
        self.assertIn('"person_generalization"', msg)
        self.assertIn('"from": "your"', msg)
        self.assertIn("RULES", msg)
        self.assertNotIn("previous_attempt_rejected", msg)

    def test_prompt_unchanged_for_non_person_items(self):
        plain = _item(1, "based on", "based on interviews", "～をもとにした", beyond=True)
        msg = ga.build_user_message_corrected([plain], "ART", rules="RULES")
        self.assertNotIn(ga.PERSON_CONSTRAINT_TEXT, msg)
        self.assertNotIn("indefinite_person_tokens", msg)

    def test_retry_message_carries_previous_invalid_reason_per_item(self):
        f1 = FakeFn([_resp((2, True, "あなたの代わりに"))])
        f2 = FakeFn([_resp((2, False, "誰かの代わりに"))])
        fns = [f1, f2]
        seen = []

        def make(msg):
            seen.append(msg)
            return fns[len(seen) - 1]
        gate = ga.run_alignment_gate_corrected(make, [self.target], "ART", "RULES")
        self.assertEqual(gate["unresolved_ranks"], [])
        self.assertEqual(gate["adopted"][2]["attempt"], 2)
        self.assertNotIn("previous_attempt_rejected", seen[0])
        self.assertIn("previous_attempt_rejected", seen[1])
        self.assertIn("人称不整合", seen[1])
        self.assertIn("あなたの代わりに", seen[1])

    def test_two_failures_go_to_hr_via_existing_path(self):
        fn = FakeFn([_resp((2, True, "あなたの代わりに")), _resp((2, False, "彼の代わりに"))])
        merged = {"items": [self.target]}
        r = ga.align_glosses(merged, "ART", lambda m: fn, enabled=True)
        self.assertEqual(r["status"], "ALIGN_FAILED_HUMAN_REVIEW_REQUIRED")
        it = r["merged"]["items"][0]
        self.assertEqual(it["gloss_alignment_status"], ga.STATUS_HR_REQUIRED)
        self.assertEqual(it["key_phrase"], "in someone's place")        # KPは候補へ戻さない
        self.assertEqual(fn.calls, 2)                                   # 上限は既存の2回
        self.assertEqual(len(ga.collect_unresolved(r["merged"])), 1)

    def test_person_generalized_clean_item_is_realigned_target_at_generation(self):
        healthy = _item(1, "shock your wallet", "shock someone's wallet", "財布に響く", reason=ga.PERSON_NORMALIZATION_REASON)
        fn = FakeFn([_resp((1, True, "財布に響く"))])
        r = ga.align_glosses({"items": [healthy]}, "ART", lambda m: fn, enabled=True)
        self.assertEqual(r["targets"], [1])
        self.assertEqual(r["status"], "ALIGN_PASS")
        self.assertEqual(r["merged"]["items"][0]["gloss_alignment_status"], ga.STATUS_ALIGNED)

    def test_only_ranks_limits_repair_targets(self):
        healthy = _item(1, "shock your wallet", "shock someone's wallet", "財布に響く", reason=ga.PERSON_NORMALIZATION_REASON)
        fn = FakeFn([_resp((2, False, "誰かの代わりに"))])
        r = ga.align_glosses({"items": [healthy, self.target]}, "ART", lambda m: fn, enabled=True, only_ranks=[2])
        self.assertEqual(r["targets"], [2])
        self.assertEqual(r["merged"]["items"][1]["japanese_gloss"], "誰かの代わりに")
        self.assertNotIn("gloss_alignment_status", r["merged"]["items"][0])

    def test_kill_switch_off_means_no_api_and_no_change(self):
        fn = FakeFn([])
        merged = {"items": [self.target]}
        r = ga.align_glosses(merged, "ART", lambda m: fn, enabled=False)
        self.assertEqual(r["status"], "DISABLED")
        self.assertIs(r["merged"], merged)
        self.assertEqual(fn.calls, 0)


# ============================================================ (B) Z stage_kp 人称整合関所
_BASE = {}


def _runner():
    import er026_family_z_fiction_production_runner_01 as r
    return r


def _base_root():
    """seed_check..support まで実行済みのmock run rootを1回だけ作る(各testはcopytreeして使う)。"""
    if "root" not in _BASE:
        r = _runner()
        root = tempfile.mkdtemp(prefix="itm1_base_")
        ctx = r.build_mock_context(root)
        with contextlib.redirect_stdout(io.StringIO()):
            r.run_stages(ctx, ["seed_check", "writer", "std_adjust", "plan", "support"])
        _BASE["root"] = root
    return _BASE["root"]


def tearDownModule():
    if "root" in _BASE:
        shutil.rmtree(_BASE["root"], ignore_errors=True)


def _make_kp_fn(r, bad_level="a2", bad_rank=2, gloss="あなたの代わりに"):
    """mockのkp_fn: 5件のKPを書く。bad_levelのbad_rank番は『英語は不定の人称、日本語意味は具体人称』(stale gloss)。"""
    calls = []

    def kp_fn(text, kp_dir, article_id, source_level, process=None, **kw):
        calls.append(source_level)
        spans = [s for s in r._MOCK_KP_CANDIDATES if s in text][:5]
        assert len(spans) == 5, spans
        lv = "a2" if source_level.upper() == "A2" else "b1b"
        items = []
        for i, s in enumerate(spans, 1):
            kp = s
            g = f"意味{i}"
            reason = None
            if lv == bad_level and i == bad_rank:
                kp = f"{s} someone's"       # 末尾に不定の人称(mockの表現。実在表現である必要はない)
                g = gloss
                reason = ga.PERSON_NORMALIZATION_REASON
            items.append({"rank": i, "source_span": s, "source_sentence": s, "display_phrase": s, "key_phrase": kp,
                          "used_form": kp, "japanese_gloss": g, "japanese_gloss_tts": g, "kp_extends_beyond_candidate": False,
                          "gloss_review_hint": False, "normalization_reason": reason or "none"})
        merged = {"items": items, "overall_status": "CANONICALIZATION_PASS", "article_id": article_id,
                  "canonicalization_version": "mock", "source_level": source_level}
        os.makedirs(kp_dir, exist_ok=True)
        json.dump(merged, open(f"{kp_dir}/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"},
                "canonicalization": {"status": "CANONICALIZATION_PASS", "merged": merged},
                "redundancy_qa": {"status": "REDUNDANCY_OK"}, "redundancy_retry_log": []}
    kp_fn.calls = calls
    return kp_fn


class ZPersonGate(_FlagOn):
    def setUp(self):
        super().setUp()
        self.r = _runner()
        self.root = tempfile.mkdtemp(prefix="itm1_run_")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        shutil.rmtree(self.root)
        shutil.copytree(_base_root(), self.root)
        self.ctx = self.r.build_mock_context(self.root)
        self.kp_fn = _make_kp_fn(self.r)
        self.ctx.hooks["kp_fn"] = self.ctx.mock_api.wrap("kp", self.kp_fn)
        self.factory_calls = []

    def _factory(self, payloads):
        fns = [FakeFn([p]) for p in payloads]

        def factory(msg):
            self.factory_calls.append(msg)
            return fns[len(self.factory_calls) - 1]
        self.ctx.hooks["gloss_align_factory"] = factory

    def _stage(self, ctx=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return self.r.run_stage(ctx or self.ctx, "kp")

    def _kp(self, lv="a2"):
        return json.load(open(f"{self.ctx.out_dir}/key_phrases/{lv}/keywords_canonicalized.json", encoding="utf-8"))

    def _prov_check(self, lv="a2"):
        w62 = self.r._m().w62
        pv = w62.rj(f"{self.ctx.out_dir}/writer/provenance.json")
        entry = pv["downstream_stages"][f"kp_{lv}"]
        self.assertEqual(entry["output_sha256"], w62.file_sha(f"{self.ctx.out_dir}/key_phrases/{lv}_result.json"))
        return entry

    def test_first_run_repairs_keeps_selection_updates_provenance_and_reuse_is_clean(self):
        self._factory([_resp((2, False, "誰かの代わりに"))])
        gate_wrap = mock.patch.object(self.r, "_gloss_person_gate", wraps=self.r._gloss_person_gate)
        with gate_wrap as gw:
            summary = self._stage()
        self.assertEqual(gw.call_count, 2)        # b1b + a2 の各levelで1回
        kp = self._kp()
        it = kp["items"][1]
        self.assertEqual(it["japanese_gloss"], "誰かの代わりに")
        self.assertEqual(it["gloss_alignment_status"], ga.STATUS_ALIGNED)
        self.assertEqual(it["japanese_gloss_tts"], "誰かの代わりに")
        # 選定・canonicalization(英語KP)は保持される
        self.assertTrue(it["key_phrase"].endswith(" someone's"))
        self.assertEqual(it["display_phrase"], it["source_span"])
        self.assertEqual(len(self.factory_calls), 1)          # 対象1 itemのみ=LLM 1回
        self.assertIn("indefinite_person_tokens_in_key_phrase", self.factory_calls[0])
        # artifact・stage結果・assets・provenance が同期
        res = self.r._m().w62.rj(f"{self.ctx.out_dir}/key_phrases/a2_result.json")
        self.assertEqual(res["canonicalization"]["merged"]["items"][1]["japanese_gloss"], "誰かの代わりに")
        rec = res["person_gloss_repairs"][0]
        self.assertEqual((rec["rank"], rec["old_gloss"], rec["new_gloss"], rec["version"]),
                         (2, "あなたの代わりに", "誰かの代わりに", ga.PERSON_ALIGNMENT_VERSION))
        self.assertIn("人称不整合", rec["reason"])
        entry = self._prov_check()
        self.assertEqual(entry["person_gloss_repairs"][0]["rank"], 2)
        installed = json.load(open(f"{self.ctx.out_dir}/a2/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
        self.assertEqual(installed["items"][1]["japanese_gloss"], "誰かの代わりに")
        self.assertEqual(summary["a2"]["gloss_person_gate"]["status"], "REPAIRED")
        self.assertEqual(summary["b1b"]["gloss_person_gate"]["status"], "CLEAN")
        # 同じrun dirで再実行(reuse): 出力sha不一致STOPにならず、追加のLLM呼出0・選定再実行0
        n_kp = len(self.kp_fn.calls)
        with gate_wrap as gw2:
            summary2 = self._stage()
        self.assertEqual(gw2.call_count, 2)
        self.assertEqual(len(self.factory_calls), 1)
        self.assertEqual(len(self.kp_fn.calls), n_kp)
        self.assertEqual(summary2["a2"]["status"], "reused")
        self.assertEqual(summary2["a2"]["gloss_person_gate"]["status"], "CLEAN")
        self.assertNotIn("synced_from_artifact", summary2["a2"]["gloss_person_gate"])     # SRC D1後処理だけの差でprovenanceを書換えない
        self.assertNotIn("synced_from_artifact", summary2["b1b"]["gloss_person_gate"])

    def test_guard_is_used_for_paid_repair(self):
        self._factory([_resp((2, False, "誰かの代わりに"))])
        labels = []
        real_guard = self.r._guard

        def spy(ctx, label, est):
            labels.append((label, est))
            return real_guard(ctx, label, est)
        with mock.patch.object(self.r, "_guard", side_effect=spy):
            self._stage()
        self.assertIn(("kp_a2_person_repair", self.r.E2E_PERSON_REPAIR_EST_JPY), labels)
        self.assertNotIn("kp_b1b_person_repair", [x[0] for x in labels])

    def test_reuse_path_repairs_legacy_artifact_and_kill_switch_off_is_noop(self):
        ga.GLOSS_ALIGNMENT_ENABLED = False                    # 旧(ON化前)artifactを永続化する
        self._factory([])
        s0 = self._stage()
        self.assertEqual(s0["a2"]["gloss_person_gate"]["status"], "DISABLED")
        self.assertEqual(self._kp()["items"][1]["japanese_gloss"], "あなたの代わりに")
        self.assertEqual(self.factory_calls, [])
        self.assertEqual(ga.collect_unevaluated(self._kp()), [])      # OFF時は消費側の検査も無効
        ga.GLOSS_ALIGNMENT_ENABLED = True
        self._factory([_resp((2, False, "誰かの代わりに"))])
        n_kp = len(self.kp_fn.calls)
        s1 = self._stage()
        self.assertEqual(s1["a2"]["status"], "reused")
        self.assertEqual(s1["a2"]["gloss_person_gate"]["status"], "REPAIRED")
        self.assertEqual(len(self.kp_fn.calls), n_kp)                # 選定は再実行しない
        self.assertEqual(self._kp()["items"][1]["japanese_gloss"], "誰かの代わりに")
        self._prov_check()
        s2 = self._stage()                                           # 次回はprovenance不一致STOPにならない
        self.assertEqual(s2["a2"]["gloss_person_gate"]["status"], "CLEAN")

    def test_regenerate_path_goes_through_gate(self):
        self._factory([_resp((2, False, "誰かの代わりに")), _resp((2, False, "誰かの代わりに"))])
        self._stage()
        self.ctx.regenerate_stage = "kp_a2"
        with mock.patch.object(self.r, "_gloss_person_gate", wraps=self.r._gloss_person_gate) as gw:
            s = self._stage()
        self.assertEqual(gw.call_count, 2)
        self.assertEqual(s["a2"]["status"], "generated")
        self.assertEqual(s["a2"]["gloss_person_gate"]["status"], "REPAIRED")
        self.assertEqual(len(self.factory_calls), 2)
        self._prov_check()

    def test_unrepairable_goes_to_existing_hr_stop_then_resume(self):
        self._factory([_resp((2, True, "あなたの代わりに")), _resp((2, False, "彼の代わりに"))])
        with self.assertRaises(self.r.FamilyZE2EStop) as cm:
            self._stage()
        self.assertIn("GLOSS_ALIGNMENT_HUMAN_REVIEW_REQUIRED(a2)", str(cm.exception))
        kd = f"{self.ctx.out_dir}/key_phrases/a2"
        self.assertEqual(self._kp()["items"][1]["gloss_alignment_status"], ga.STATUS_HR_REQUIRED)
        self.assertFalse(ga.validate_hr_report(f"{kd}/{ga.HR_REPORT_JSON}"))
        self.assertTrue(os.path.exists(f"{self.ctx.out_dir}/gloss_alignment_human_review_events.json"))
        self.assertEqual(len(self.factory_calls), 2)                  # 既存の上限2回。新しいSTOP経路は作らない
        # 解消前の再実行も同じHR経路で止まり、追加のLLM呼出はない(選定も再実行しない)
        n_kp = len(self.kp_fn.calls)
        with self.assertRaises(self.r.FamilyZE2EStop) as cm2:
            self._stage()
        self.assertIn("HUMAN_REVIEW_REQUIRED", str(cm2.exception))
        self.assertEqual(len(self.factory_calls), 2)
        self.assertEqual(len(self.kp_fn.calls), n_kp)
        # --stage tts_*単独起動: HR artifactを共有入力にしない(fail-closed)
        with self.assertRaises(self.r.FamilyZE2EStop):
            self.r.load_level_inputs(self.ctx, "a2")
        # 人間確定(resolve_gloss)後は通過。確定値に人称語が残ってもWARNのみ(STOP/再修復しない)
        ga.resolve_gloss(f"{kd}/keywords_canonicalized.json", 2, "私の代わりに", "itm1_test", now="2026-10-19T00:00:00+00:00")
        s = self._stage()
        self.assertEqual(s["a2"]["gloss_person_gate"]["status"], "CLEAN")
        self.assertEqual([w["rank"] for w in s["a2"]["gloss_person_gate"]["warnings"]], [2])
        self.assertEqual(len(self.factory_calls), 2)
        self.assertEqual(self._kp()["items"][1]["japanese_gloss"], "私の代わりに")
        res = self.r._m().w62.rj(f"{self.ctx.out_dir}/key_phrases/a2_result.json")
        self.assertEqual([{k: v for k, v in it.items() if k.startswith("gloss_") or k.startswith("japanese_gloss")}
                          for it in res["canonicalization"]["merged"]["items"]],
                         [{k: v for k, v in it.items() if k.startswith("gloss_") or k.startswith("japanese_gloss")}
                          for it in self._kp()["items"]])      # stage結果のgloss関連はartifactと同期(古いHR状態を残さない)
        self._prov_check()

    def test_tts_stage_standalone_is_fail_closed_on_unrepaired_artifact(self):
        ga.GLOSS_ALIGNMENT_ENABLED = False
        self._stage()                                                 # mismatchを残したままassetsを配備
        ga.GLOSS_ALIGNMENT_ENABLED = True
        with self.assertRaises(self.r.FamilyZE2EStop) as cm:
            self.r.load_level_inputs(self.ctx, "a2")
        self.assertIn("UNEVALUATED", str(cm.exception))
        # 修復後は通る
        self._factory([_resp((2, False, "誰かの代わりに"))])
        self._stage()
        self.assertTrue(self.r.load_level_inputs(self.ctx, "a2")["kp_items"])

    def test_mock_without_factory_hook_never_reaches_real_api(self):
        with self.assertRaises(self.r.FamilyZE2EStop) as cm:
            self._stage()
        self.assertIn("NO_FACTORY", str(cm.exception))

    def test_real_mode_factory_uses_production_routing_model(self):
        """real時の修復factoryは、scaffoldのgloss再整合と同じrouting(A2_SUPPORT/B1_SUPPORT=SUPPORT_MODEL)。API呼出はしない。"""
        import er006_model_routing_contract_01 as routing
        self.ctx.mode = "real"
        seen = []
        with mock.patch.object(ga, "make_alignment_fn", side_effect=lambda msg, **kw: seen.append((msg, kw)) or "FN"):
            for lv in ("a2", "b1b"):
                self.assertEqual(self.r._person_repair_factory(self.ctx, lv)("MSG"), "FN")
        self.assertEqual([kw["model"] for _, kw in seen], [routing.SUPPORT_MODEL] * 2)

    def test_clean_artifact_costs_nothing(self):
        self.ctx.hooks["kp_fn"] = self.ctx.mock_api.wrap("kp", _make_kp_fn(self.r, bad_level="none"))
        self._factory([])
        s = self._stage()
        self.assertEqual(self.factory_calls, [])
        self.assertEqual(s["a2"]["gloss_person_gate"]["status"], "CLEAN")


# ============================================================ (C) X runner: 消費側でSTOPのみ(修復経路なし)
class XRunnerStopOnly(_FlagOn):
    def test_x_gate_stops_on_mismatch_and_passes_healthy_without_repair(self):
        import er019_family_x_audio_production_runner_01 as x
        healthy = _item(1, "shock your wallet", "shock someone's wallet", "財布に響く", reason=ga.PERSON_NORMALIZATION_REASON)
        bad = _item(2, "in your place", "in someone's place", "あなたの代わりに", reason=ga.PERSON_NORMALIZATION_REASON)
        out = x._gloss_alignment_hr_unresolved({"items": [healthy, bad]})
        self.assertEqual([(i["rank"], i.get("_unevaluated")) for i in out], [(2, True)])
        self.assertEqual(x._gloss_alignment_hr_unresolved({"items": [healthy]}), [])
        # 修復用の関数をXは持たない(STOPのみ。OPEN_ITEMS記録)
        self.assertFalse(hasattr(x, "_gloss_person_gate"))
        stopped = x._gloss_alignment_stopped_entry(out, "kp2_en")
        self.assertEqual(stopped["status"], ga.STOPPED_STATUS)
        self.assertIn("KPを再生成", stopped["reason"])
        ga.GLOSS_ALIGNMENT_ENABLED = False
        self.assertEqual(x._gloss_alignment_hr_unresolved({"items": [healthy, bad]}), [])   # kill switch OFF時は無効


if __name__ == "__main__":
    unittest.main()
