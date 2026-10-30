# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_02: er135_enduser_align_01.py(英語文<->日本語訳の対応づけ ja_align)と連動表示assetのtest。API 0。

実行: .venv\\Scripts\\python.exe -m pytest er135_enduser_align_test_01.py -q
 - fake embedder(概念IDからの決定論ベクトル)でDP・採否・degrade・キャッシュ・陳腐化・再計算不一致を検査
 - ゴールド回帰: docs/research/ENDUSER-EN-JA-LINKED-HIGHLIGHT-01/gold/ の実埋め込みキャッシュ(text-embedding-3-large, 1024次元)で
   emit群の誤対応0・1文ずらし合成の棄却率100%・coverage下限(API 0。`gold/`が無い環境ではskip)
 - 連動表示(app.js rev01-f)のjaHtml: nodeで実行(旧データ互換・UTF-16オフセット・escは切り出し後・不正データはフォールバック)
"""
import copy
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

import er135_enduser_align_01 as AL
import er135_enduser_page_01 as E
import er135_enduser_rules_01 as R
from er135_enduser_page_test_01 import Built, stop_code

ROOT = Path(__file__).resolve().parent
GOLD = ROOT / "docs" / "research" / "ENDUSER-EN-JA-LINKED-HIGHLIGHT-01" / "gold"


# ------------------------------------------------------------
# fake embedder: 先頭トークン(概念ID, 例 'A1')ごとに直交基底 + 小さな決定論ノイズ。同じ概念IDのEN/JAはcos高、別概念は低
# ------------------------------------------------------------
def _concept(text: str) -> str:
    return text.split()[0].split("|")[0]


def fake_embedder(texts):
    out = []
    for t in texts:
        c = _concept(t)
        rng = np.random.default_rng(abs(hash_c(c)) % (2 ** 32))
        v = rng.normal(size=64)
        r2 = np.random.default_rng(abs(hash_c(t)) % (2 ** 32))
        v = v / np.linalg.norm(v) + 0.15 * r2.normal(size=64) / 8.0
        out.append(v.tolist())
    return out, len(texts)


def hash_c(s: str) -> int:
    h = 1469598103934665603
    for ch in s.encode("utf-8"):
        h = ((h ^ ch) * 1099511628211) % (2 ** 63)
    return h


def mk_store(cache_dir=None, embedder=fake_embedder, allow_api=True):
    return AL.EmbedStore(cache_dir, embedder=embedder, allow_api=allow_api)


def part(sents, ja_paras, key="story_1", idx=3):
    """sents=[[ENテキスト,...] (段落ごと)], ja_paras=[JA段落文字列]"""
    paragraphs, n = [], 0
    for pa in sents:
        row = []
        for t in pa:
            row.append({"sid": f"{key}-s{n:03d}", "html": t, "text": t})
            n += 1
        paragraphs.append(row)
    return {"idx": idx, "key": key, "label": "Part 1", "kind": "story", "paragraphs": paragraphs, "ja": ja_paras, "ja_source": "approved_ja_manuscript"}


def art_of(p, lv="std"):
    return {"levels": {lv: {"parts": [p]}}}


# ============================================================
class A1_Primitives(unittest.TestCase):
    def test_split_ja_concat_equals_original_and_respects_quotes(self):
        t = "彼は言った。「やあ。元気？」そうか！ 最後は句点なし"
        segs = AL.split_ja(t)
        self.assertEqual("".join(t[a:b] for a, b in segs), t)
        self.assertEqual(len(segs), 3)                       # 「…。…？」内では切らない
        self.assertTrue(t[segs[1][0]:segs[1][1]].startswith("「やあ。元気？」"))
        self.assertEqual(AL.split_ja(""), [])
        self.assertEqual(AL.split_ja("終わり。"), [(0, 4)])

    def test_utf16_offsets_with_surrogate_pairs(self):
        s = "あ😀い。うえ"
        m = AL.cp_to_u16(s)
        self.assertEqual(m[-1], AL.u16_len(s))
        self.assertEqual(AL.u16_len(s), 7)                   # 😀=2 code unit
        self.assertEqual(AL.slice_u16(s, 1, 3), "😀")
        self.assertEqual(AL.slice_u16(s, 0, 7), s)
        with self.assertRaises(ValueError):
            AL.slice_u16(s, 2, 4)                            # ペアを割る位置

    def test_numbers_rule(self):
        self.assertTrue(AL.numbers_ok("The team counted more than 8,900.", "研究チームが数えたのは8,900本超。"))
        self.assertTrue(AL.numbers_ok("about 42 to 46 meters", "約42から46メートル"))
        self.assertTrue(AL.numbers_ok("two people", "二人の声"))
        self.assertTrue(AL.numbers_ok("30 people", "三十人"))
        self.assertTrue(AL.numbers_ok("３０人", "30人") if False else AL.numbers_ok("30 people", "３０人"))
        self.assertFalse(AL.numbers_ok("The team counted 8,900.", "数えたのは8,800本"))
        self.assertFalse(AL.numbers_ok("three voices", "二つの声"))
        self.assertTrue(AL.numbers_ok("no one came", "誰も来なかった"))         # 'one'は対象外(代名詞)
        self.assertEqual(AL.en_numbers("one two 3"), {2, 3})

    def test_names_rule_uses_dictionary_only(self):
        self.assertTrue(AL.names_ok("Tajomaru spoke.", "多襄丸は言った", None))
        self.assertTrue(AL.names_ok("Tajomaru spoke.", "多襄丸は言った", {"Tajomaru": ["多襄丸"]}))
        self.assertFalse(AL.names_ok("Tajomaru spoke.", "武弘は言った", {"Tajomaru": ["多襄丸"]}))
        self.assertTrue(AL.names_ok("Nobody spoke.", "誰も話さなかった", {"Tajomaru": ["多襄丸"]}))   # 辞書の名前がENに無ければ判定しない


# ============================================================
class A2_Alignment(unittest.TestCase):
    def _clean_part(self):
        # 概念ID: A..E。EN 5文 / JA 4文(B,Cが1文に統合)
        en = [["Aaa Even the moon has wrinkles.", "Bbb It looks smooth.", "Bbb Up close it is wrinkled.", "Ccc No cream needed.", "Ddd Wrinkles give clues."]]
        ja = ["Aaa 月にもしわがある。Bbb 夜空では滑らかに見えるが近くではしわだらけ。Ccc 美容液は不要だ。Ddd しわは手がかりだ。"]
        return part(en, ja)

    def test_one_to_one_and_many_to_one_grouping(self):
        p = self._clean_part()
        # 文末の句点で分割されるよう、JA各文に概念IDを付けたもの(概念ID後は空白区切り)
        al, st = AL.align_part(p, mk_store())
        self.assertEqual([g["sids"] for g in al], [[s["sid"]] for s in p["paragraphs"][0][:1]] + [[p["paragraphs"][0][1]["sid"], p["paragraphs"][0][2]["sid"]], [p["paragraphs"][0][3]["sid"]], [p["paragraphs"][0][4]["sid"]]])
        linked = [g for g in al if g["ja"]]
        self.assertEqual(len(linked), 4)
        for g in al:
            if g["ja"]:
                pi, a, b = g["ja"]
                txt = AL.slice_u16(p["ja"][pi], a, b)
                self.assertTrue(txt.endswith("。"), txt)
        self.assertEqual(st["linked"], 5)
        self.assertEqual(AL.check_part_align({**p, "ja_align": al}, "t"), [])

    def test_ambiguous_boundary_is_null_not_wrong(self):
        # EN3文が同じ概念(S)・JA2文も同じ概念: どの1文ずらしでも同等 -> 余裕が無く、安全側でnull(誤対応を出さない)
        en = [["Sss one.", "Sss two.", "Sss three."]]
        ja = ["Sss いち。Sss に。"]
        p = part(en, ja)
        al, st = AL.align_part(p, mk_store())
        self.assertEqual(st["linked"], 0)
        self.assertTrue(all(g["ja"] is None for g in al))

    def test_cos_below_tau_is_null(self):
        en = [["Xxx apple pie."]]
        ja = ["Yyy まったく別の話。"]
        al, st = AL.align_part(part(en, ja), mk_store())
        self.assertIsNone(al[0]["ja"])

    def test_number_mismatch_is_null(self):
        en = [["Aaa They counted 8,900."]]
        ja = ["Aaa 数えたのは8,800本。"]
        al, st = AL.align_part(part(en, ja), mk_store())
        self.assertIsNone(al[0]["ja"])
        self.assertEqual(st["reasons"].get("number_mismatch"), 1)

    def test_equal_count_paragraph_links_all_pairs_and_rejects_wrong_pairing(self):
        en = [["Aaa alpha.", "Bbb beta.", "Ccc gamma."]]
        ja = ["Aaa いち。Bbb に。Ccc さん。"]
        p = part(en, ja)
        al, st = AL.align_part(p, mk_store())
        self.assertEqual(st["linked"], 3)                              # 文数一致+相互最良: 全て1:1で連動
        self.assertEqual([g["sids"] for g in al], [[s["sid"]] for s in p["paragraphs"][0]])
        # JAの順序を入れ替えた(誤対応になる)段落: ENのi番目のJA最良がi番目でない -> 相互最良が崩れてnull
        ja2 = ["Bbb に。Aaa いち。Ccc さん。"]
        al2, st2 = AL.align_part(part(en, ja2), mk_store())
        self.assertEqual(sum(1 for g in al2 if g["ja"] is not None and g["sids"] == [p["paragraphs"][0][0]["sid"]]), 0)

    def test_single_sentence_paragraph_matches(self):
        al, _ = AL.align_part(part([["Aaa First, hear from a driver."]], ["Aaa 最初は配達ドライバーだ。"]), mk_store())
        self.assertIsNotNone(al[0]["ja"])
        self.assertEqual(al[0]["ja"], [0, 0, AL.u16_len("Aaa 最初は配達ドライバーだ。")])

    def test_paragraph_count_mismatch_is_all_null_with_degraded_note(self):
        p = part([["Aaa one."], ["Bbb two."]], ["Aaa いち。"])
        art = art_of(p)
        store = mk_store()
        info = AL.build_article_align(art, store)
        self.assertTrue(all(g["ja"] is None for g in art["levels"]["std"]["parts"][0]["ja_align"]))
        self.assertTrue(any("不一致" in d for d in info["degraded"]))

    def test_embedding_failure_is_all_null_and_degraded(self):
        def boom(texts):
            raise AL.AlignEmbedError("API down")
        p = self._clean_part()
        art = art_of(p)
        info = AL.build_article_align(art, mk_store(embedder=boom))
        g = art["levels"]["std"]["parts"][0]["ja_align"]
        self.assertTrue(all(x["ja"] is None for x in g))
        self.assertEqual(sum(len(x["sids"]) for x in g), 5)            # ENの全文が群に入る(null)
        self.assertTrue(info["degraded"] and "embedding_unavailable" in info["degraded"][0])
        self.assertEqual(info["coverage"]["std"]["sentences_linked"], 0)

    def test_embedding_failure_message_has_no_url_or_path_and_does_not_stop_the_build(self):
        import sys
        import types
        from unittest import mock

        class Boom(Exception):
            status_code = 503

        def raising(*a, **k):
            raise Boom("https://api.openai.com/v1/embeddings failed at C:" + chr(92) + "Users" + chr(92) + "x" + chr(92) + "y.py")
        fake_openai = types.SimpleNamespace(OpenAI=lambda: types.SimpleNamespace(embeddings=types.SimpleNamespace(create=raising)))
        with mock.patch.dict(sys.modules, {"openai": fake_openai}), mock.patch("time.sleep"):
            with self.assertRaises(AL.AlignEmbedError) as cm:
                AL.openai_embedder(["x"])
        self.assertNotIn("http", str(cm.exception))
        self.assertNotIn("C:", str(cm.exception))
        self.assertIn("503", str(cm.exception))
        # その文言でdegradedになっても、End Userページの生成(validate_output: 禁止path検査)は止まらない
        b = Built("x_moon")

        def boom(texts):
            raise AL.AlignEmbedError(str(cm.exception))
        art, sp, bi = b.data(align_store=mk_store(embedder=boom))
        self.assertTrue(bi["ja_align"]["degraded"])
        self.assertTrue(all(g["ja"] is None for L in art["levels"].values() for p in L["parts"] for g in p.get("ja_align", [])))
        self.assertEqual(bi["ja_align"]["coverage"]["std"]["sentences_linked"], 0)

    def test_deterministic_and_cache_makes_second_run_api_free(self):
        with tempfile.TemporaryDirectory() as td:
            p1, p2 = self._clean_part(), self._clean_part()
            s1 = mk_store(td)
            AL.build_article_align(art_of(p1), s1)
            self.assertGreater(s1.stats["api_calls"], 0)
            calls = []

            def counting(texts):
                calls.append(len(texts))
                return fake_embedder(texts)
            s2 = mk_store(td, embedder=counting)
            AL.build_article_align(art_of(p2), s2)
            self.assertEqual(calls, [])                                # キャッシュ再利用でAPI 0
            self.assertEqual(p1["ja_align"], p2["ja_align"])           # 同一結果
            s3 = AL.EmbedStore(td, allow_api=False)                    # verify相当: APIを呼べない
            al, _ = AL.align_part(p1, s3)
            self.assertEqual(al, p1["ja_align"])

    def test_allow_api_false_with_missing_cache_raises(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(AL.AlignEmbedError):
                AL.EmbedStore(td, allow_api=False).ensure(["Aaa x"])

    def test_en_sentence_change_re_aligns_and_input_sha_changes(self):
        p = self._clean_part()
        sha1 = AL.part_input_sha(p)
        p2 = copy.deepcopy(p)
        p2["paragraphs"][0][1]["text"] = "Bbb It looks very smooth."
        self.assertNotEqual(sha1, AL.part_input_sha(p2))
        p3 = copy.deepcopy(p)
        p3["ja"][0] = p3["ja"][0].replace("近くでは", "間近では")
        self.assertNotEqual(sha1, AL.part_input_sha(p3))


# ============================================================
class A3_StructureAndVerify(unittest.TestCase):
    def _aligned(self):
        p = A2_Alignment()._clean_part()
        art = art_of(p)
        store = mk_store()
        info = AL.build_article_align(art, store)
        return art, info, store

    def test_valid_passes_and_recompute_matches(self):
        art, info, store = self._aligned()
        v, ch = AL.verify_article_align(art, info, store)
        self.assertEqual(v, [])
        self.assertEqual(ch["recompute"], "done")
        v2, ch2 = AL.verify_article_align(art, info, None)
        self.assertEqual((v2, ch2["recompute"]), ([], "skipped_no_cache"))

    def test_stale_alignment_after_en_change_is_violation(self):
        art, info, store = self._aligned()
        art["levels"]["std"]["parts"][0]["paragraphs"][0][0]["text"] = "Aaa Even the moon has many wrinkles."   # EN変更・ja_alignは旧
        v, _ = AL.verify_article_align(art, info, None)
        self.assertTrue(any("陳腐化" in m for m in v), v)

    def test_tampered_alignment_fails_recompute(self):
        art, info, store = self._aligned()
        g = art["levels"]["std"]["parts"][0]["ja_align"]
        k = next(i for i, x in enumerate(g) if x["ja"])
        g[k]["ja"] = [0, 0, 3]                                          # 構造は満たすが再計算と不一致
        v, _ = AL.verify_article_align(art, info, store)
        self.assertTrue(any("再計算" in m for m in v), v)

    def test_missing_embedding_cache_fails_verify(self):
        art, info, _ = self._aligned()
        with tempfile.TemporaryDirectory() as td:
            v, _ = AL.verify_article_align(art, info, AL.EmbedStore(td, allow_api=False))
        self.assertTrue(any("キャッシュ" in m for m in v), v)

    def test_structure_violations(self):
        art, info, _ = self._aligned()
        base = art["levels"]["std"]["parts"][0]

        def viol(mut):
            p = copy.deepcopy(base)
            mut(p["ja_align"])
            return AL.check_part_align(p, "t")
        linked = [i for i, x in enumerate(base["ja_align"]) if x["ja"]]
        i0, i1 = linked[0], linked[1]
        self.assertTrue(viol(lambda g: g[i0].__setitem__("sids", ["no-such-sid"])))
        self.assertTrue(viol(lambda g: g[i1].__setitem__("sids", g[i0]["sids"])))                        # 重複sid
        self.assertTrue(viol(lambda g: g[i0].__setitem__("ja", [0, 5, 9999])))                           # 範囲外
        self.assertTrue(viol(lambda g: g[i0].__setitem__("ja", [0, 4, 4])))                              # 空
        self.assertTrue(viol(lambda g: g[i0].__setitem__("ja", [7, 0, 3])))                              # 段落index範囲外
        self.assertTrue(viol(lambda g: g[i1].__setitem__("ja", list(g[i0]["ja"]))))                      # JAが重なる
        self.assertTrue(viol(lambda g: g.reverse()))                                                     # 順序逆行
        self.assertTrue(viol(lambda g: g[i0].__setitem__("conf", 0.1)))                                  # conf<閾値なのにja有り
        self.assertEqual(viol(lambda g: None), [])
        p = copy.deepcopy(base)
        del p["ja"]
        self.assertTrue(AL.check_part_align(p, "t"))                                                     # jaが無いのにja_align

    def test_surrogate_split_offset_is_violation(self):
        p = part([["Aaa smile."]], ["Aaa 😀。"])
        p["ja_align"] = [{"g": 0, "sids": [p["paragraphs"][0][0]["sid"]], "ja": [0, 0, 5], "conf": 0.9}]
        self.assertTrue(any("サロゲート" in m for m in AL.check_part_align(p, "t")))
        p["ja_align"][0]["ja"] = [0, 0, AL.u16_len("Aaa 😀。")]
        self.assertEqual(AL.check_part_align(p, "t"), [])

    def test_params_are_frozen(self):
        self.assertEqual(AL.PARAMS, {"lam": 2.0, "len_w": 1.0, "pen_12": 0.9, "pen_22": 4.0, "pen_13": 1.5, "skip": 3.0, "tau": 0.5, "delta_path": 0.1,
                                     "delta_group": 0.0, "delta_sent": 0.0, "delta_group_en": -0.10, "delta_sent_en": -0.10, "eq_delta_ja": 0.0, "eq_delta_en": 0.0,
                                     "tau_para": 0.55, "tau_floor": 0.4})
        self.assertEqual((AL.EMBED_MODEL, AL.EMBED_DIMS), ("text-embedding-3-large", 1024))


# ============================================================
class A4_PageIntegration(unittest.TestCase):
    """er135_enduser_page_01への組込み(fixtureのdev HTML + fake embedder。API 0)。"""

    def test_x_fixture_gets_ja_align_and_passes_validate(self):
        b = Built("x_moon")
        store = mk_store()
        art, sp, bi = b.data(align_store=store)
        self.assertIn("ja_align", bi)
        self.assertTrue(bi["ja_align"]["applicable"])
        story = [p for p in art["levels"]["std"]["parts"] if p.get("ja")]
        self.assertTrue(story and all("ja_align" in p for p in story))
        for p in story:
            self.assertEqual(AL.check_part_align(p, "t"), [])
        self.assertEqual(bi["cost"]["api_calls"], 0)                     # ASR/LLM呼出は0(埋め込みは別枠)
        self.assertGreater(bi["cost"]["embedding_api_calls"], 0)
        # 訳本文・英語本文は不変(ja_alignはフィールド追加のみ)
        _art2, _sp2, _bi2 = b.data()
        for lv in art["levels"]:
            for p, q in zip(art["levels"][lv]["parts"], _art2["levels"][lv]["parts"]):
                p2 = {k: v for k, v in p.items() if k != "ja_align"}
                self.assertEqual(p2, q)

    def test_z_fixture_without_translation_calls_no_api_and_is_not_applicable(self):
        b = Built("z_melos02")
        calls = []

        def counting(texts):
            calls.append(len(texts))
            return fake_embedder(texts)
        art, sp, bi = b.data(align_store=mk_store(embedder=counting))
        self.assertEqual(calls, [])
        self.assertFalse(bi["ja_align"]["applicable"])
        self.assertTrue(all("ja_align" not in p for L in art["levels"].values() for p in L["parts"]))

    def test_y_paragraph_mismatch_is_stop(self):
        b = Built("y_fee03")
        art, sp, bi = b.data(align_store=mk_store())                   # 正常なYはPASS(1対1)
        for L in art["levels"].values():
            for p in L["parts"]:
                if p.get("ja"):
                    self.assertEqual(len(p["paragraphs"]), len(p["ja"]))
        art["levels"]["std"]["parts"][[i for i, p in enumerate(art["levels"]["std"]["parts"]) if p.get("ja")][0]]["ja"].append("余分な段落。")
        self.assertEqual(stop_code(E.validate_output, art, sp, bi, b.rows, b.study, b.meta, probe=b.probe), "ENDUSER_JA_ALIGN_Y_PARA_MISMATCH")

    def test_schema_rejects_bad_ja_align(self):
        b = Built("x_moon")
        art, sp, bi = b.data(align_store=mk_store())
        p = next(p for p in art["levels"]["std"]["parts"] if p.get("ja_align"))
        p["ja_align"][0]["extra"] = 1
        self.assertEqual(stop_code(E.check_schema, art, E.SCHEMA_ARTICLE_SPEC, "a"), "ENDUSER_SCHEMA")

    def test_validate_rejects_structurally_invalid_align(self):
        b = Built("x_moon")
        art, sp, bi = b.data(align_store=mk_store())
        p = next(p for p in art["levels"]["std"]["parts"] if p.get("ja_align"))
        p["ja_align"][0]["sids"] = ["bogus"]
        self.assertEqual(stop_code(E.validate_output, art, sp, bi, b.rows, b.study, b.meta, probe=b.probe), "ENDUSER_JA_ALIGN")

    def test_write_and_verify_consistency_with_cache_and_stale_injection(self):
        # build -> verify_consistency(cacheあり=再計算まで) -> EN変更の陳腐化注入でFAIL。公開dirを模した一時dir
        b = Built("x_moon")
        with tempfile.TemporaryDirectory() as td:
            pub = Path(td) / "pub"
            pub.mkdir()
            (pub / "index.html").write_text(b.html, encoding="utf-8")
            cache = Path(td) / "cache"
            store = mk_store(str(cache))
            art, sp, bi = b.data(align_store=store)
            E.write_enduser_page(pub / "enduser", (art, sp, bi))
            # 音声shaは疑似(FakeAudio)なのでverify_consistencyの音声項目以外を見る
            r = E.verify_consistency(pub, cache_dir=str(cache))
            codes = [v["code"] for v in r["violations"]]
            self.assertNotIn("ENDUSER_JA_ALIGN", codes, r["violations"])
            self.assertEqual(r["checked"]["ja_align"]["recompute"], "done")
            # キャッシュ無し(空dir)=verify失敗
            r2 = E.verify_consistency(pub, cache_dir=str(Path(td) / "empty"))
            self.assertIn("ENDUSER_JA_ALIGN", [v["code"] for v in r2["violations"]])
            # 陳腐化注入: article.jsonのENを変えるとfiles shaも変わるが、ja_alignの入力sha不一致も検出される
            ap = pub / "enduser" / "data" / "article.json"
            a = json.loads(ap.read_text(encoding="utf-8"))
            pt = next(p for p in a["levels"]["std"]["parts"] if p.get("ja_align"))
            pt["paragraphs"][0][0]["text"] = pt["paragraphs"][0][0]["text"] + " (edited)"
            ap.write_text(json.dumps(a, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            r3 = E.verify_consistency(pub)
            self.assertTrue(any(v["code"] == "ENDUSER_JA_ALIGN" and "陳腐化" in v["message"] for v in r3["violations"]), r3["violations"])

    def test_old_asset_build_is_stale_except_frozen_allowlist(self):
        self.assertEqual(R.ASSET_BUILD_ID, "rev01-f")
        self.assertTrue((ROOT / "enduser_page_assets" / "rev01-e" / "app.js").is_file())          # 旧assetは凍結・残置
        self.assertEqual(E.FROZEN_ASSET_DIRS, {"family_z_in_a_grove_01": "rev01-e"})
        E.check_assets(ROOT / "enduser_page_assets" / "rev01-e")                                  # 凍結assetは自身のmanifestと一致

    def test_hook_summary_exposes_ja_align(self):
        import inspect
        src = inspect.getsource(E.hook_run)
        self.assertIn('"ja_align"', src)
        self.assertIn("cache_dir=cache_dir", src)


# ============================================================
class A5_AssetJaHtml(unittest.TestCase):
    """app.js rev01-fのjaHtml()をnodeで実行(旧データ互換・UTF-16オフセット・escは切り出し後・不正データのフォールバック)。"""

    def _run(self, p, k, t):
        js = (ROOT / "enduser_page_assets" / R.ASSET_BUILD_ID / "app.js").read_text(encoding="utf-8")
        a = js.index("  function jaHtml(")
        b = js.index("  function glossHtml(")
        esc = "function esc(s) { return String(s == null ? '' : s).replace(/[&<>\"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;', \"'\": '&#39;' }[m]; }); }\n"
        code = esc + js[a:b] + "\nprocess.stdout.write(jaHtml(%s,%s,%s));" % (json.dumps(p), json.dumps(k), json.dumps(t, ensure_ascii=False))
        r = subprocess.run(["node", "-e", code], capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_old_data_without_ja_align_equals_plain_escaped_text(self):
        self.assertEqual(self._run({"idx": 2}, 0, "A<B&C「x」。"), "A&lt;B&amp;C「x」。")
        self.assertEqual(self._run({"idx": 2, "ja_align": []}, 0, "テキスト。"), "テキスト。")

    def test_spans_wrap_ranges_and_text_is_unchanged(self):
        t = "月にもしわがある。夜空では見える。末尾。"
        p = {"idx": 4, "ja_align": [{"g": 0, "sids": ["s0"], "ja": [0, 0, 9]}, {"g": 1, "sids": ["s1"], "ja": None}, {"g": 2, "sids": ["s2"], "ja": [0, 9, 17]}]}
        h = self._run(p, 0, t)
        self.assertEqual(h, '<span class="jhl" data-jg="4:0">月にもしわがある。</span><span class="jhl" data-jg="4:2">夜空では見える。</span>末尾。')
        self.assertEqual(re.sub(r"<[^>]+>", "", h), t)

    def test_other_paragraph_groups_are_ignored(self):
        p = {"idx": 1, "ja_align": [{"g": 0, "sids": ["s0"], "ja": [1, 0, 3]}]}
        self.assertEqual(self._run(p, 0, "あいうえお"), "あいうえお")

    def test_utf16_offsets_match_python_slice_with_emoji_and_escape_after_slice(self):
        t = "<b>😀笑う。</b>次。"
        a, b = 3, 3 + AL.u16_len("😀笑う。")
        p = {"idx": 0, "ja_align": [{"g": 0, "sids": ["s"], "ja": [0, a, b]}]}
        h = self._run(p, 0, t)
        self.assertEqual(h, '&lt;b&gt;<span class="jhl" data-jg="0:0">😀笑う。</span>&lt;/b&gt;次。')
        self.assertEqual(AL.slice_u16(t, a, b), "😀笑う。")

    def test_invalid_data_falls_back_to_plain_text(self):
        t = "あいうえおかきくけこ"
        for ja in ([0, 0, 99], [0, 5, 5], [0, 7, 3]):
            self.assertEqual(self._run({"idx": 0, "ja_align": [{"g": 0, "sids": ["s"], "ja": ja}]}, 0, t), t)
        overlap = {"idx": 0, "ja_align": [{"g": 0, "sids": ["a"], "ja": [0, 0, 6]}, {"g": 1, "sids": ["b"], "ja": [0, 4, 9]}]}
        self.assertEqual(self._run(overlap, 0, t), t)

    def test_asset_has_single_highlight_hook_point_and_no_flag(self):
        js = (ROOT / "enduser_page_assets" / R.ASSET_BUILD_ID / "app.js").read_text(encoding="utf-8")
        self.assertEqual(js.count("jaLight("), 2)                           # 定義1 + highlight()内の呼出1(他の呼出点なし)
        a = js.index("  function highlight(sid) {")
        self.assertIn("jaLight(sid);", js[a:a + 120])
        self.assertNotIn("Q.get('ja", js)                                    # query/flagでON/OFFできない
        css = (ROOT / "enduser_page_assets" / R.ASSET_BUILD_ID / "style.css").read_text(encoding="utf-8")
        self.assertIn(".jhl.on{background:var(--on);box-shadow:0 0 0 3px var(--on)}", css)
        self.assertIn(".sent.on{background:var(--on);box-shadow:0 0 0 3px var(--on)}", css)


# ============================================================
@unittest.skipUnless((GOLD / "ja_align_embed_v1.jsonl").is_file() and any(GOLD.glob("gold_*.txt")), "gold/が無い")
class A6_GoldRegression(unittest.TestCase):
    """ゴールド(既公開3記事x Std/Adv=50段落・265文・218群)に対し、固定PARAMSで emit群の誤対応0・合成ずらし棄却100%・coverage下限。API 0。"""

    @classmethod
    def setUpClass(cls):
        sys_path = str(ROOT / "tools")
        import sys
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)
        import ejh02_gold_eval_01 as G
        cls.G = G
        cls.res = G.evaluate()

    def test_no_wrong_emitted_group(self):
        self.assertEqual(self.res["wrong_groups"], [], self.res["wrong_groups"])

    def test_synthetic_one_sentence_shifts_are_all_rejected(self):
        self.assertGreater(self.res["synthetic_total"], 300)
        self.assertEqual(self.res["synthetic_accepted"], 0)

    def test_coverage_floor_and_recorded_values(self):
        self.assertGreaterEqual(self.res["coverage"], 0.70)
        self.assertGreaterEqual(self.res["coverage_by_level"]["adv"], 0.82)
        self.assertGreaterEqual(self.res["coverage_by_level"]["std"], 0.60)

    def test_equal_count_mode_rejects_all_adjacent_wrong_pairs(self):
        self.assertGreater(self.res["equal_mode_wrong_pairs_total"], 60)
        self.assertEqual(self.res["equal_mode_wrong_pairs_accepted"], 0)

    def test_holdout_article_ig_nobel(self):
        """採否規則の決定・解析に使っていない完全な未見記事(Ig Nobel Std/Adv 22段落・76文・69群)。"""
        r = self.G.evaluate(unseen=True, arts=("ig",))
        self.assertEqual(r["wrong_groups"], [])
        self.assertEqual(r["synthetic_accepted"], 0)
        self.assertEqual(r["equal_mode_wrong_pairs_accepted"], 0)
        self.assertGreaterEqual(r["coverage"], 0.85)

    def test_cross_paragraph_mispairing_rarely_emits(self):
        self.assertLessEqual(self.res["cross_emitted"], 3)

    def test_unseen_data_no_wrong_group_and_all_synthetic_rejected(self):
        """パラメータ決定に使っていない既存X記事3本(Paycheck Personality / manga byUs / Ig Nobel, 56段落・223文・197群)で同じ固定PARAMSを評価。"""
        r = self.G.evaluate(unseen=True)
        self.assertEqual(r["wrong_groups"], [], r["wrong_groups"])
        self.assertGreater(r["synthetic_total"], 250)
        self.assertEqual(r["synthetic_accepted"], 0)
        self.assertGreaterEqual(r["coverage"], 0.82)
        self.assertEqual(r["equal_mode_wrong_pairs_accepted"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
