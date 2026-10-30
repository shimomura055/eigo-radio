# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03A: 英日連動ハイライトの全パート適用(構造確定/順序対応/周辺確率/生成訳の統合/対象一覧)のtest。API 0(embedder・LLMともmock)。

実行: .venv\\Scripts\\python.exe -m pytest er135_enduser_link_test_01.py -q
"""
import hashlib
import inspect
import json
import re
import tempfile
import unittest
from pathlib import Path

import numpy as np

import er135_enduser_align_01 as AL
import er135_enduser_page_01 as E
import er135_enduser_translate_01 as TR
from er135_enduser_align_test_01 import fake_embedder, mk_store, part, art_of
from er135_enduser_page_test_01 import Built

ROOT = Path(__file__).resolve().parent


# ------------------------------------------------------------
# mock LLM(translate_partのprotocol: translate=番号付き対象 / verify=番号付き対訳)。各英文に一意で構造Gateを通る日本語を返す
# ------------------------------------------------------------
def mock_ja(en: str) -> str:
    uniq = "".join(chr(0x3042 + int(c, 16) % 60) for c in hashlib.md5(en.encode("utf-8")).hexdigest()[:6])
    nums = sorted(TR.en_numbers(en))
    return f"これは{uniq}という文の訳です" + ("".join(f"({n})" for n in nums)) + "。"


class MockLLM:
    def __init__(self, bad_verify_en=()):
        self.bad = set(bad_verify_en)
        self.log, self.seen_en = [], []

    def __call__(self, kind, prompt):
        self.log.append(kind)
        if kind == "translate":
            body = prompt.split(TR.TRANSLATE_TARGET_LABEL, 1)[1].split("\n# 出力形式")[0]
            ts = [re.match(r"^\d+\. (.*)$", ln).group(1) for ln in body.strip().split("\n")]
            self.seen_en += ts
            return json.dumps({"translations": [{"id": i, "ja": mock_ja(t)} for i, t in enumerate(ts, 1)]}, ensure_ascii=False)
        body = prompt[len(TR.VERIFY_HEAD):].split("\n# 出力形式")[0]
        ps = re.findall(r"^\d+\. EN: (.*)\n   JA: (.*)$", body, re.M)
        return json.dumps({"results": [{"id": i, "ok": en not in self.bad, "issue": "mock-ng"} for i, (en, ja) in enumerate(ps, 1)]})


def counting_embedder():
    calls = []

    def f(texts):
        calls.append(len(texts))
        return fake_embedder(texts)
    return f, calls


# ============================================================
class L1_Tiers(unittest.TestCase):
    EN1 = ["Aaa The Moon shrank by about 42 meters."]

    def test_structural_one_sided_paragraphs_are_deterministic(self):
        g = AL.structural_groups(self.EN1, ["月は約42メートル縮んだ。"])
        self.assertEqual(g, [{"en": [0], "ja": (0, 1), "conf": 1.0, "why": "ok", "how": "det"}])
        g = AL.structural_groups(["Aaa One is here.", "Bbb Two is there.", "Ccc Three is gone."], ["ここに一つ、あそこに二つ、そして三つ消えた。"])
        self.assertEqual((g[0]["en"], g[0]["ja"], g[0]["how"]), ([0, 1, 2], (0, 1), "det"))
        g = AL.structural_groups(["Aaa The report was long and detailed overall."], ["報告書は長かった。", "細部まで詳しかった。"])
        self.assertEqual((g[0]["en"], g[0]["ja"]), ([0], (0, 2)))

    def test_structural_safety_checks_fall_through_to_embedding_path(self):
        self.assertIsNone(AL.structural_groups(self.EN1, ["月は約50メートル縮んだ。"]))      # 数字不一致
        self.assertIsNone(AL.structural_groups(["Aaa Yes."], ["はい、そうです。それは本当に長い長い長い長い返事の文章でした。"]))   # 文字数比が帯の外
        self.assertIsNone(AL.structural_groups(["Aaa A very long English sentence that keeps going on and on and on for quite a while."], ["はい。"]))
        self.assertIsNone(AL.structural_groups(["Aaa One.", "Bbb Two."], ["一。", "二。"]))                      # 両側2文以上=構造だけでは決まらない
        self.assertIsNone(AL.structural_groups([], ["あ。"]))

    def test_structural_paragraph_needs_no_embedding_and_makes_no_api_call(self):
        p = part([["Aaa The Moon shrank by about 42 meters."], ["Bbb A very quiet night passed over the whole town."]],
                 ["月は約42メートル縮んだ。", "町全体を、とても静かな夜が包んだ。"])
        self.assertEqual(AL.part_texts(p), [])
        emb, calls = counting_embedder()
        store = mk_store(embedder=emb)
        info = AL.build_article_align(art_of(p), store)
        self.assertEqual(calls, [])
        self.assertEqual(info["embedding"]["api_calls"], 0)
        self.assertEqual(info["coverage"]["std"]["coverage"], 1.0)
        self.assertEqual(info["coverage"]["std"]["linked_by_how"], {"det": 2})
        self.assertEqual({g["how"] for g in p["ja_align"]}, {"det"})
        self.assertEqual(AL.check_part_align(p, "t"), [])

    def test_equal_count_paragraph_uses_order_mapping_and_rejects_clear_contradiction(self):
        en = ["Aaa The cliffs are small.", "Bbb They show how the Moon cooled.", "Ccc Heat escaped slowly."]
        ja = ["Aaa 崖は小さい。", "Bbb 月がどう冷えたかを示している。", "Ccc 熱はゆっくり逃げた。"]
        bad = ["Ccc 熱はゆっくり逃げた。", "Bbb 月がどう冷えたかを示している。", "Aaa 崖は小さい。"]        # 対応が入れ替わっている(JA1文目がEN3文目の内容)
        st = mk_store_with(en + ja + bad)
        g = AL.align_paragraph(en, ja, st)
        self.assertEqual([(x["en"], x["ja"], x["how"]) for x in g], [([0], (0, 1), "order"), ([1], (1, 2), "order"), ([2], (2, 3), "order")])
        g2 = AL.align_paragraph(en, bad, st)
        self.assertTrue(all(x["ja"] is None or x["how"] != "order" or x["en"] == [1] for x in g2))
        self.assertNotIn(([0], (0, 1)), [(x["en"], x["ja"]) for x in g2])

    def test_marginal_probability_is_zero_for_non_move_shapes_and_valid_otherwise(self):
        en = ["Aaa a.", "Bbb b.", "Ccc c.", "Ddd d.", "Eee e.", "Fff f."]
        ja = ["Aaa あ。", "Bbb い。", "Ccc う。", "Ddd え。"]
        px = AL._Para(en, ja, mk_store_with(en + ja), AL.PARAMS)
        self.assertEqual(px.marg(0, 5, 0, 1), 0.0)               # EN5文xJA1文はDPのmoveに無い
        self.assertTrue(0.0 <= px.marg(0, 1, 0, 1) <= 1.0 + 1e-9)


def mk_store_with(texts):
    s = mk_store()
    s.ensure(texts)
    return s


# ============================================================
class L2_EmbedStoreRoundingAndVerify(unittest.TestCase):
    def test_in_memory_vector_equals_reloaded_vector(self):
        """不具合是正(11-8): 生成直後のメモリ上ベクトル(丸め前float32)と、保存(6桁丸め)から再読込したベクトルが食い違い、境界値の採否が1回だけ不一致になった。"""
        rng = np.random.default_rng(1)
        texts = [f"t{i}" for i in range(8)]
        vecs = {t: rng.normal(size=1024).tolist() for t in texts}
        with tempfile.TemporaryDirectory() as d:
            s1 = AL.EmbedStore(d, embedder=lambda ts: ([vecs[t] for t in ts], 5))
            s1.ensure(texts)
            s2 = AL.EmbedStore(d, allow_api=False)
            for t in texts:
                self.assertTrue(np.array_equal(s1.vec(t), s2.vec(t)), t)

    def test_verify_after_cache_reload_has_no_violation(self):
        b = Built("x_moon")
        with tempfile.TemporaryDirectory() as d:
            store = AL.EmbedStore(d, embedder=fake_embedder)
            art, sp, bi = b.data(align_store=store)
            v, _c = AL.verify_article_align(art, bi["ja_align"], AL.EmbedStore(d, allow_api=False))
            self.assertEqual(v, [])


# ============================================================
class L3_GeneratedTranslations(unittest.TestCase):
    def _targets(self, art):
        out = {}
        for lv, rows in art["levels"].items():
            for p in rows["parts"]:
                if p["kind"] in E.LINK_KINDS and p.get("paragraphs"):
                    out[(lv, p["key"])] = p
        return out

    def test_default_build_generates_nothing_and_records_missing(self):
        """既定(translate_fn=None)では生成せず、訳が無い英語partは ja_source 無し(=missing)の連動N/A。"""
        b = Built("z_melos02")
        art, sp, bi = b.data(align_store=mk_store())
        self.assertNotIn("generated_translation", bi)
        self.assertTrue(all("ja" not in p for L in art["levels"].values() for p in L["parts"]))
        lt = bi["link_targets"]
        stat = {(lv, r["kind"]): r["status"] for lv, rows in lt["parts"].items() for r in rows}
        self.assertEqual(stat[("adv", "story")], "missing")
        self.assertEqual(stat[("std", "story")], "missing")
        self.assertEqual(stat[("std", "preview")], "na_ja_only")          # Std Preview/Commentは日本語本文=英語対なし
        self.assertEqual(stat[("adv", "preview")], "missing")
        self.assertTrue(all(r["linked"] == 0 for rows in lt["parts"].values() for r in rows))

    def test_library_build_is_off_by_default_but_official_hook_generates_missing_parts(self):
        """委任_03B: build_enduser(ライブラリ直呼び)の既定は生成しない(None)。正式経路(hook_run/produce_enduser)は既定で本番LLM(DefaultLLM)を使い、
        明示的にNoneを渡したときだけ生成しない。実APIへ黙って落ちる経路(make_translator(None))は無い。"""
        self.assertIsNone(inspect.signature(E.build_enduser).parameters["translate_llm"].default)
        for fn in (E.hook_run, E.produce_enduser):
            self.assertIs(inspect.signature(fn).parameters["translate_llm"].default, E.AUTO_TRANSLATE_LLM)
        self.assertIsNone(E._resolve_translate_llm(None))                   # 明示None=生成しない
        sentinel = object()
        self.assertIs(E._resolve_translate_llm(sentinel), sentinel)         # 注入されたllmはそのまま
        self.assertIsInstance(E._resolve_translate_llm(E.AUTO_TRANSLATE_LLM), TR.DefaultLLM)
        with self.assertRaises(ValueError):
            E.make_translator("x", None)                                    # 実API既定へ黙って落ちない

    def test_translate_exception_is_part_failure_but_model_contract_is_fatal(self):
        """通信失敗等=そのpartだけ訳不成立(英語のみ+failures記録)。応答モデルが契約と違う=fallbackせずSTOP(例外を伝播)。"""
        b = Built("x_moon")
        def boom(part_id, sentences, *, level, family):
            raise RuntimeError("network down")
        art, _sp, bi = b.data(align_store=mk_store(), translate_fn=boom)
        gt = bi["generated_translation"]
        self.assertTrue(gt["failures"] and all(f["reasons"][0].startswith("exception: RuntimeError") for f in gt["failures"]))
        self.assertTrue(any("訳の新規生成が不成立" in w for w in bi["warnings"]))
        self.assertFalse(any(p.get("ja_source") == "generated" for L in art["levels"].values() for p in L["parts"]))
        def contract(part_id, sentences, *, level, family):
            raise TR.ModelContractError("model mismatch")
        with self.assertRaises(TR.ModelContractError):
            b.data(align_store=mk_store(), translate_fn=contract)

    def test_z_story_and_all_english_parts_get_generated_translation_with_mock(self):
        b = Built("z_melos02")
        llm = MockLLM()
        emb, calls = counting_embedder()
        with tempfile.TemporaryDirectory() as d:
            art, sp, bi = b.data(align_store=mk_store(embedder=emb), translate_fn=E.make_translator(d, llm))
        self.assertEqual(calls, [])                                       # 生成訳は構成上1:1=埋め込み0
        gen = bi["generated_translation"]
        self.assertEqual(gen["failures"], [])
        self.assertGreater(gen["api_calls"]["translate"], 0)
        lt = bi["link_targets"]
        for lv, rows in lt["parts"].items():
            for r in rows:
                if r["status"] == "na_ja_only" or r["kind"] == "preview":
                    continue
                self.assertEqual(r["status"], "generated", (lv, r))
                self.assertEqual(r["linked"], r["sentences"], (lv, r))
                self.assertEqual(r["how"], ["gen"])
        for (lv, key), p in self._targets(art).items():
            if p.get("ja_source"):
                self.assertEqual(p["ja_source"], "generated")
                self.assertEqual(len(p["ja"]), len(p["paragraphs"]))
                self.assertEqual(AL.check_part_align(p, key), [])
                self.assertEqual(AL.check_generated_part(p, key), [])
                for g in p["ja_align"]:                                   # 各文の訳が、その文のmock訳と一致
                    sent = next(s for pa in p["paragraphs"] for s in pa if s["sid"] == g["sids"][0])
                    self.assertEqual(AL.slice_u16(p["ja"][g["ja"][0]], g["ja"][1], g["ja"][2]), mock_ja(sent["text"]))
        # Std日本語のPreview/Commentは触らない(英語を新設しない・訳を付けない)
        for p in art["levels"]["std"]["parts"]:
            if p["kind"] in ("preview", "comment"):
                self.assertNotIn("ja", p)
        self.assertEqual(bi["translation_coverage"]["adv"]["story"]["source"], "generated")
        self.assertTrue(bi["ja_align"]["applicable"])
        self.assertEqual(bi["ja_align"]["embedding"]["api_calls"], 0)

    def test_preview_is_generated_because_asset_rev01_g_renders_it(self):
        """asset rev01-g(J26)はPreviewカードにも訳(trHtml)を出す。Previewは GENERATE_KINDS に入り、訳の無いAdv Previewだけ生成する。Std Previewは日本語本文=対象外。"""
        self.assertIn("preview", E.GENERATE_KINDS)
        js = (ROOT / "enduser_page_assets" / E.R.ASSET_BUILD_ID / "app.js").read_text(encoding="utf-8")
        self.assertIn("sentHtml(p)) + trHtml(p)", js)
        b = Built("x_moon")
        llm = MockLLM()
        with tempfile.TemporaryDirectory() as d:
            art, _sp, bi = b.data(align_store=mk_store(), translate_fn=E.make_translator(d, llm))
        pv = [p for p in art["levels"]["adv"]["parts"] if p["kind"] == "preview"]
        self.assertTrue(pv and all(p.get("ja_source") == "generated" and p.get("ja") for p in pv))
        for p in art["levels"]["std"]["parts"]:
            if p["kind"] == "preview":
                self.assertNotIn("ja", p)                      # Std Previewは日本語本文(英語対なし)=生成しない
        for p in pv:
            for pa in p["paragraphs"]:
                for s_ in pa:
                    self.assertIn(s_["text"], llm.seen_en)

    def test_approved_translations_are_never_regenerated(self):
        b = Built("x_moon")
        base_art, _sp, _bi = b.data(align_store=mk_store())
        llm = MockLLM()
        with tempfile.TemporaryDirectory() as d:
            art, sp, bi = b.data(align_store=mk_store(), translate_fn=E.make_translator(d, llm))
        for lv in art["levels"]:
            for p, q in zip(art["levels"][lv]["parts"], base_art["levels"][lv]["parts"]):
                if q.get("ja_source") == "approved_ja_manuscript":
                    self.assertEqual(p["ja"], q["ja"])
                    self.assertEqual(p["ja_source"], "approved_ja_manuscript")
                    self.assertEqual(p["ja_align"], q["ja_align"])
                    for pa in p["paragraphs"]:
                        for s in pa:
                            self.assertNotIn(s["text"], llm.seen_en)       # 承認済みのstory英文はLLMに渡していない
        stat = {(lv, r["kind"]): r["status"] for lv, rows in bi["link_targets"]["parts"].items() for r in rows}
        self.assertEqual(stat[("adv", "story")], "approved_ja_manuscript")
        self.assertEqual(stat[("adv", "preview")], "generated")              # asset rev01-gはPreviewカードに訳を描画する -> 生成する
        self.assertEqual(stat[("adv", "oneline")], "generated")
        self.assertEqual(stat[("std", "oneline")], "generated")
        self.assertEqual(stat[("adv", "comment")], "generated")
        self.assertEqual(stat[("std", "preview")], "na_ja_only")

    def test_cache_hit_makes_no_new_call_and_failure_leaves_english_only(self):
        b = Built("z_melos02")
        with tempfile.TemporaryDirectory() as d:
            l1 = MockLLM()
            art1, _s, bi1 = b.data(align_store=mk_store(), translate_fn=E.make_translator(d, l1))
            self.assertGreater(len(l1.log), 0)
            l2 = MockLLM()
            art2, _s, bi2 = b.data(align_store=mk_store(), translate_fn=E.make_translator(d, l2))
            self.assertEqual(l2.log, [])                                   # 再build/resume/pagesはAPI 0
            self.assertEqual(art1, art2)
            self.assertEqual(bi2["generated_translation"]["api_calls"], {"translate": 0, "verify": 0})
        # 失敗: 1文の対訳照合NG -> そのpartは付与しない(部分jaなし)、他partは生成、build全体は継続
        some_adv = next(p for p in art1["levels"]["adv"]["parts"] if p["kind"] == "comment")
        bad_en = some_adv["paragraphs"][0][0]["text"]
        with tempfile.TemporaryDirectory() as d:
            art3, _s, bi3 = b.data(align_store=mk_store(), translate_fn=E.make_translator(d, MockLLM(bad_verify_en=[bad_en])))
        g3 = bi3["generated_translation"]
        self.assertEqual([(f["level"], f["key"]) for f in g3["failures"]], [("adv", some_adv["key"])])
        failed = next(p for p in art3["levels"]["adv"]["parts"] if p["key"] == some_adv["key"])
        self.assertNotIn("ja", failed)
        self.assertNotIn("ja_align", failed)
        self.assertTrue(any("新規生成が不成立" in w for w in bi3["warnings"]))
        stat = {(lv, r["key"]): r["status"] for lv, rows in bi3["link_targets"]["parts"].items() for r in rows}
        self.assertEqual(stat[("adv", some_adv["key"])], "missing")
        others = [r for r in bi3["link_targets"]["parts"]["adv"] if r["key"] != some_adv["key"] and r["status"] != "na_ja_only" and r["kind"] != "preview"]
        self.assertTrue(others and all(r["status"] == "generated" for r in others))

    def test_tampered_generated_translation_is_detected(self):
        b = Built("z_melos02")
        with tempfile.TemporaryDirectory() as d:
            art, _s, bi = b.data(align_store=mk_store(), translate_fn=E.make_translator(d, MockLLM()))
        p = next(p for p in art["levels"]["adv"]["parts"] if p.get("ja_source") == "generated")
        self.assertEqual(AL.check_generated_part(p, "t"), [])
        p["ja"][0] += "余計な一文。"                                      # 訳文だけ書き換え -> 群が末尾まで覆わない
        self.assertTrue(any("末尾" in m for m in AL.check_generated_part(p, "t")))
        v, _c = AL.verify_article_align(art, bi["ja_align"], None)
        self.assertTrue(any("陳腐化" in m or "末尾" in m for m in v))

    def test_written_page_verifies_generated_translation_and_detects_staleness(self):
        b = Built("z_melos02")
        with tempfile.TemporaryDirectory() as td:
            pub = Path(td) / "pub"
            pub.mkdir()
            (pub / "index.html").write_text(b.html, encoding="utf-8")
            cache = Path(td) / "cache"
            art, sp, bi = b.data(align_store=mk_store(str(cache)), translate_fn=E.make_translator(str(cache), MockLLM()))
            E.write_enduser_page(pub / "enduser", (art, sp, bi))
            r = E.verify_consistency(pub, cache_dir=str(cache))
            codes = [v["code"] for v in r["violations"]]
            for c in ("ENDUSER_JA_ALIGN", "ENDUSER_LINK_TARGETS", "ENDUSER_GENERATED_TRANSLATION"):
                self.assertNotIn(c, codes, r["violations"])
            # 生成訳の英文が後から変わった(陳腐化)
            ap = pub / "enduser" / "data" / "article.json"
            a = json.loads(ap.read_text(encoding="utf-8"))
            pt = next(p for p in a["levels"]["adv"]["parts"] if p.get("ja_source") == "generated")
            pt["paragraphs"][0][0]["text"] += " (edited)"
            ap.write_text(json.dumps(a, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            r2 = E.verify_consistency(pub, cache_dir=str(cache))
            self.assertTrue(any(v["code"] == "ENDUSER_GENERATED_TRANSLATION" and "陳腐化" in v["message"] for v in r2["violations"]), r2["violations"])

    def test_build_ja_fields_is_all_or_nothing_and_offsets_are_utf16(self):
        paras = [[{"sid": "a", "text": "x"}, {"sid": "b", "text": "y"}], [{"sid": "c", "text": "z"}]]
        r = TR.build_ja_fields(paras, {"a": "あ😀。", "b": "い。", "c": "う。"})
        ja, groups = r
        self.assertEqual(ja, ["あ😀。い。", "う。"])
        self.assertEqual([g["ja"] for g in groups], [[0, 0, 4], [0, 4, 6], [1, 0, 2]])
        self.assertIsNone(TR.build_ja_fields(paras, {"a": "あ。", "b": None, "c": "う。"}))
        self.assertIsNone(TR.build_ja_fields(paras, {"a": "あ。", "b": "  ", "c": "う。"}))


# ============================================================
class L4_LinkTargets(unittest.TestCase):
    def test_x_family_table(self):
        b = Built("x_moon")
        art, sp, bi = b.data(align_store=mk_store())
        sm = bi["link_targets"]["summary"]
        self.assertEqual(set(sm["std"]["story"]["status"]), {"approved_ja_manuscript"})
        self.assertEqual(set(sm["std"]["preview"]["status"]), {"na_ja_only"})
        self.assertEqual(set(sm["adv"]["preview"]["status"]), {"missing"})
        self.assertEqual(set(sm["adv"]["comment"]["status"]), {"missing"})
        self.assertGreaterEqual(sm["adv"]["story"]["linked"], 0)       # fake embedderでは連動数は不定(実データの点灯率はgold評価で測る)
        self.assertLessEqual(sm["adv"]["story"]["linked"], sm["adv"]["story"]["sentences"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
