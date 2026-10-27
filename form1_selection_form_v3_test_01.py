# -*- coding: utf-8 -*-
"""LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_01 のtest(接続0・API 0・Production経路非依存)。
nodeでform_logic.jsの単体testを実行し、データ・参照HTML保全・Production非接続を検証する。"""
import hashlib
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(ROOT, "user_test", "selection_form_v3")
RD = os.path.join(ROOT, "docs", "research", "LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01")
REF = os.path.join(ROOT, "docs", "pm", "Phrase_Form", "eigo_radio_selection_form_reference.html")
REF_SHA256 = "13ef9085f625ea1618e63500793ffcbe959552c8ac0325484c623b1edb4fce79"   # 受領時の参照HTML(無改変)


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class SelectionFormV3Test(unittest.TestCase):
    def test_reference_html_unmodified(self):
        with open(REF, "rb") as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), REF_SHA256)

    def test_node_logic_suite(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "node が必要(form_logic.jsの単体test)")
        r = subprocess.run([node, os.path.join(RD, "selection_form_logic_test_01.js")], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("ALL PASS", r.stdout)

    def test_monkeys_paw_data_matches_trial02_result(self):
        d = _j(os.path.join(FD, "data", "monkeys_paw__b1b.json"))
        with open(os.path.join(ROOT, "docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/RESULT_02.md"), encoding="utf-8") as f:
            md = f.read()
        sec = md[md.index("## monkeys_paw:b1b"):]
        for it in d["phrases"] + d["words"]:
            self.assertIn("| " + it["term"] + " |", sec, it["term"])
        self.assertEqual((len(d["phrases"]), len(d["words"])), (7, 4))
        self.assertEqual(d["source"]["kind"], "DEV_TRIAL")
        self.assertEqual(d["grammar"], [])        # 正式文法候補なし。仮データを入れない
        self.assertNotIn("interferes", [x["term"] for x in d["phrases"] + d["words"]])   # Gate除外語は出さない

    def test_no_placeholder_grammar_in_formal_data(self):
        for fn in os.listdir(os.path.join(FD, "data")):
            if fn.startswith("ui_check_dummy") or fn == "articles.json" or fn == "legacy":
                continue
            s = open(os.path.join(FD, "data", fn), encoding="utf-8").read()
            self.assertNotIn("過去完了形", s)
            self.assertNotIn("分詞による名詞の後置修飾", s)

    def test_form_not_connected_to_production(self):
        """フォームはProduction Pythonを一切importしない/参照しない(静的HTML+JSのみ)。"""
        for fn in ("index.html", "form_logic.js"):
            s = open(os.path.join(FD, fn), encoding="utf-8").read()
            for bad in ("er119_", "er105_", "er003_", "er125_", "OPENAI_API_KEY", "api_key"):
                self.assertNotIn(bad, s, fn)

    def test_index_html_references_exist(self):
        s = open(os.path.join(FD, "index.html"), encoding="utf-8").read()
        for ref in ("form_logic.js", "data/articles.json"):
            self.assertIn(ref, s)
            self.assertTrue(os.path.exists(os.path.join(FD, ref)))

    # ---- 委任_02: 日本語訳・AI選定理由(既存値の再利用。AI再生成なし) ----
    @staticmethod
    def _xf():
        import importlib.util
        p = os.path.join(ROOT, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools", "export_form_data_01.py")
        spec = importlib.util.spec_from_file_location("export_form_data_01", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_gloss_status_rules(self):
        xf = self._xf()
        base = {"japanese_gloss": "訳", "flags": {"gloss_hr_pending": False}, "gates": {"gloss": "ALIGNED"}}
        self.assertEqual(xf.gloss_status(base, "PRODUCTION_FORMAL_PATH"), "official")
        self.assertEqual(xf.gloss_status(base, "REPLAY_FROZEN_INITIAL_REAL_BACKFILL"), "provisional")    # replayは正式扱いしない
        self.assertEqual(xf.gloss_status(base, "DEV_TRIAL"), "provisional")
        hr = dict(base, flags={"gloss_hr_pending": True}, gates={"gloss": "HR_PENDING"})
        self.assertEqual(xf.gloss_status(hr, "PRODUCTION_FORMAL_PATH"), "provisional")                  # 意味確認待ちは仮訳
        self.assertEqual(xf.gloss_status(dict(base, japanese_gloss=""), "PRODUCTION_FORMAL_PATH"), "missing")
        self.assertEqual(xf.gloss_status(dict(base, japanese_gloss=None), "PRODUCTION_FORMAL_PATH"), "missing")
        self.assertEqual(xf.gloss_status(dict(base, gates={"gloss": "HUMAN_RESOLVED"}), "PRODUCTION_FORMAL_PATH"), "official")

    def test_reason_info_rules(self):
        xf = self._xf()
        self.assertEqual(xf.reason_info({"reason_ja": "理由", "origin": "call2"}), ("理由", "ai_call2"))
        self.assertEqual(xf.reason_info({"reason_ja": "理由", "origin": "backfill"}), ("理由", "ai_backfill"))
        self.assertEqual(xf.reason_info({"reason_ja": "", "origin": "call1"}), ("", "none_call1_has_no_reason"))
        self.assertEqual(xf.reason_info({"reason_ja": "replay", "origin": "call2"}), ("", "none_placeholder_not_real"))
        self.assertEqual(xf.reason_info({"reason_ja": "", "origin": "call2"}), ("", "none_not_generated"))

    def test_form_data_reuses_existing_gloss_and_reason_verbatim(self):
        """各データの日本語訳・AI理由が、元のkp_candidates.json(またはTrial-02 trial_result.json)の値と逐語一致(再生成なし)。"""
        K = "er019_output/family_x_audio_production_wiring_01/"
        srcs = {          # 委任_04: 7+5 (run_kp75_ev_01)。旧3+5版(run_kpbf_ev_01)はdata/legacy/
            "ai_island_temple__a2__prod.json": K + "ai_island_temple__run_kp75_ev_01/a2/key_phrases/kp_candidates.json",
            "ai_island_temple__b1b__prod.json": K + "ai_island_temple__run_kp75_ev_01/b1b/key_phrases/kp_candidates.json",
            "uk_train_speaker_playback__a2__prod.json": K + "uk_train_speaker_playback__run_kp75_ev_01/a2/key_phrases/kp_candidates.json",
            "uk_train_speaker_playback__b1b__prod.json": K + "uk_train_speaker_playback__run_kp75_ev_01/b1b/key_phrases/kp_candidates.json",
            "redelivery_fee__a2__prod.json": "er121_output/family_y_production_01/redelivery_fee/run_kp75_ev_01/key_phrases/a2/kp_candidates.json",
            "redelivery_fee__b1b__prod.json": "er121_output/family_y_production_01/redelivery_fee/run_kp75_ev_01/key_phrases/b1b/kp_candidates.json",
            "melos__a2__prod.json": "er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01/key_phrases/a2/kp_candidates.json",
            "melos__b1b__prod.json": "er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01/key_phrases/b1b/kp_candidates.json",
            "legacy/ai_island_temple__a2__prod.json": "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01/a2/key_phrases/kp_candidates.json",
            "legacy/ai_island_temple__b1b__prod.json": "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01/b1b/key_phrases/kp_candidates.json",
            "legacy/redelivery_fee__a2__prod.json": "er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01/key_phrases/a2/kp_candidates.json",
            "legacy/redelivery_fee__b1b__prod.json": "er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01/key_phrases/b1b/kp_candidates.json",
            "legacy/melos__a2__prod.json": "er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01/key_phrases/a2/kp_candidates.json",
            "monkeys_paw__b1b__prod.json": "docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/replay_results/R5a_Z_monkeys_paw_b1b_frozen_only/kp_candidates_doc.json",
        }
        checked = 0
        for fn, rel in srcs.items():
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path):
                continue
            src = _j(path)
            d = _j(os.path.join(FD, "data", *fn.split("/")))
            by_id = {c["candidate_id"]: c for c in src["candidates"]}
            for e in d["phrases"] + d["words"]:
                c = by_id[e["id"]]
                self.assertEqual(e["ja_gloss"], c["japanese_gloss"], fn + e["term"])
                self.assertEqual(e["meaning_ja"], c["japanese_gloss"])
                if e["reason_ja"]:
                    self.assertEqual(e["reason_ja"], c["reason_ja"])
                checked += 1
        self.assertGreater(checked, 30)
        trial = _j(os.path.join(ROOT, "docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/runs/monkeys_paw__b1b__p7w5__r1/trial_result.json"))
        by_id = {c["candidate_id"]: c for c in trial["doc"]["candidates"]}
        d = _j(os.path.join(FD, "data", "monkeys_paw__b1b.json"))
        for e in d["phrases"] + d["words"]:
            self.assertEqual(e["ja_gloss"], by_id[e["id"]]["japanese_gloss"])
            self.assertEqual(e["reason_ja"], by_id[e["id"]].get("reason_ja") or "")

    def test_candidate_id_kind_and_sha_match_source_docs_verbatim(self):
        """委任_03: データJSONのcandidate_id/kind/candidates_sha256が元docと逐語一致。docに自己shaが無い場合はnull(捏造しない)。"""
        import glob
        files = [f for f in sorted(glob.glob(os.path.join(FD, "data", "*__*.json"))) if "ui_check" not in f]
        self.assertEqual(len(files), 10)
        n_sha = n_null = 0
        for f in files:
            d = _j(f)
            src = _j(os.path.join(ROOT, d["source_kp_candidates_path"]))
            doc = src.get("doc", src)
            by_id = {c["candidate_id"]: c for c in doc["candidates"]}
            items = d["phrases"] + d["words"] + d.get("overflow", [])
            ids = [e["candidate_id"] for e in items]
            self.assertEqual(len(set(ids)), len(ids), f)
            for e in items:
                c = by_id[e["candidate_id"]]
                self.assertEqual(e["id"], c["candidate_id"])
                if c.get("kind") in ("phrase", "word"):
                    self.assertEqual((e["kind"], e["kind_source"]), (c["kind"], "candidate_doc"), f)
                else:
                    self.assertEqual((e["kind"], e["kind_source"]), ("word" if len((c.get("used_form") or "").split()) == 1 else "phrase", "derived_from_word_count"), f)
            if doc.get("candidates_sha256"):
                self.assertEqual(d["candidates_sha256"], doc["candidates_sha256"], f)
                self.assertEqual(d["candidates_sha256_source"], "candidate_doc_field")
                recomputed = hashlib.sha256(json.dumps({k: v for k, v in doc.items() if k != "candidates_sha256"}, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
                self.assertEqual(d["candidates_sha256"], recomputed, f)
                n_sha += 1
            else:
                self.assertIsNone(d["candidates_sha256"], f)
                self.assertTrue(d["candidates_sha256_source"].startswith("unavailable_"), f)
                n_null += 1
        self.assertEqual((n_sha, n_null), (8, 2))

    # ---- 委任_04: P7/W5'(上限12・kind別cap 7/5)追従 ----
    def test_export_cap_default_12_and_cap_by_kind(self):
        xf = self._xf()
        base = dict(candidates=[], backfill={}, shortfall=True)
        cap, cbk, src = xf.cap_info(base)                                   # 記録が無いdocは既定12 / 7+5
        self.assertEqual((cap, cbk, src), (12, {"phrase": 7, "word": 5}, "default_12_7_5"))
        self.assertEqual(xf.cap_info(dict(base, shortfall_detail={"cap": 8}))[0], 8)   # 旧8 docは記録値を正とする
        c, b, s2 = xf.cap_info(dict(base, shortfall_detail={"cap": 12, "cap_by_kind": {"phrase": 7, "word": 5}}))
        self.assertEqual((c, b, s2), (12, {"phrase": 7, "word": 5}, "candidate_doc"))
        out = xf.convert(dict(base, shortfall_detail=None), slug="s", level="a2", name="n", family="X", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
        self.assertEqual((out["cap"], out["cap_by_kind"]), (12, {"phrase": 7, "word": 5}))
        self.assertIn("上限12件", out["shortfall_note_ja"])
        self.assertNotIn("上限8件", out["shortfall_note_ja"])
        self.assertEqual(xf.reason_info({"reason_ja": "理由", "origin": "call1"}), ("理由", "ai_call1"))       # P7ではcall1にも理由

    def test_reason_missing_warning_only_for_p7w5_docs(self):
        """委任_05(ユーザー決定2026-10-27 §4): 7+5 docで理由欠落は`data_warnings`、旧Prompt 2 docは警告なし(理由欄非表示のみ)。"""
        xf = self._xf()
        mk = lambda cid, rj: {"candidate_id": cid, "selection_phrase": cid, "used_form": cid, "japanese_gloss": "訳", "source_sentence": "s", "origin": "call1", "kind": "phrase", "reason_ja": rj, "ai_rank": 1}
        kw = dict(slug="s", level="a2", name="n", family="X", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
        p7 = xf.convert(dict(candidates=[mk("p_1", "理由"), mk("p_2", "")], backfill={}, prompt_ids={"call1": "kp_prompt_p7", "call2": "kp_prompt_w5p"}), **kw)
        self.assertEqual(len(p7["data_warnings"]), 1)
        self.assertEqual((p7["data_warnings"][0]["code"], p7["data_warnings"][0]["candidate_ids"]), ("reason_missing_in_p7w5", ["p_2"]))
        ok = xf.convert(dict(candidates=[mk("p_1", "理由")], backfill={}, prompt_ids={"call1": "kp_prompt_p7"}), **kw)
        self.assertNotIn("data_warnings", ok)
        old = xf.convert(dict(candidates=[mk("p_1", ""), mk("p_2", "理由")], backfill={}), **kw)       # prompt_idsなし=旧Prompt 2 doc
        self.assertNotIn("data_warnings", old)
        old2 = xf.convert(dict(candidates=[mk("p_1", "")], backfill={}, prompt_ids={"call1": "kp_prompt_2"}), **kw)
        self.assertNotIn("data_warnings", old2)
        for f in __import__("glob").glob(os.path.join(FD, "data", "*__prod.json")):          # 配線済み7+5 evidence docは全候補に理由あり=警告なし
            if "monkeys" not in f:
                self.assertNotIn("data_warnings", _j(f), f)

    def test_form_html_hides_reason_pane_without_reason(self):
        with open(os.path.join(FD, "index.html"), encoding="utf-8") as f:
            h = f.read()
        with open(os.path.join(FD, "form_logic.js"), encoding="utf-8") as f:
            j = f.read()
        for bad in ("AI理由なし", "ro.note", "（なし）", "REASON_NONE", "none_call1_has_no_reason"):
            self.assertFalse(bad in h + j, bad)
        self.assertIn("data_warnings", h)

    def test_kp75_form_data_cap12_kind_cap_and_reason_verbatim(self):
        import glob
        n = 0
        for f in sorted(glob.glob(os.path.join(FD, "data", "*__prod.json"))):
            if "monkeys" in f:
                continue
            d = _j(f)
            src = _j(os.path.join(ROOT, d["source_kp_candidates_path"]))
            self.assertIn("run_kp75_ev_01", d["source_kp_candidates_path"])
            self.assertEqual((d["cap"], d["cap_by_kind"]), (12, {"phrase": 7, "word": 5}), f)
            self.assertEqual(d["shortfall_detail"]["cap"], src["shortfall_detail"]["cap"] if src.get("shortfall_detail") else 12)
            self.assertLessEqual(len(d["phrases"]), 7)
            self.assertLessEqual(len(d["words"]), 5)
            by_id = {c["candidate_id"]: c for c in src["candidates"]}
            for e in d["phrases"] + d["words"]:
                c = by_id[e["candidate_id"]]
                self.assertEqual((e["kind"], e["kind_source"]), (c["kind"], "candidate_doc"))
                self.assertEqual(e["reason_ja"], c["reason_ja"])
                self.assertTrue(e["reason_ja"])
                self.assertEqual(e["ja_gloss_status"], "official")
                n += 1
        self.assertGreaterEqual(n, 70)

    def test_legacy_3plus5_data_retained_and_not_indexed(self):
        idx = _j(os.path.join(FD, "data", "articles.json"))
        for a in idx["articles"]:
            self.assertFalse((a.get("data") or "").startswith("data/legacy"), a)
        for fn in ("ai_island_temple__a2__prod", "ai_island_temple__b1b__prod", "redelivery_fee__a2__prod", "redelivery_fee__b1b__prod", "melos__a2__prod"):
            d = _j(os.path.join(FD, "data", "legacy", fn + ".json"))
            self.assertEqual(d["shortfall_detail"]["cap"], 8)
            self.assertIn("run_kpbf_ev_01", d["source_kp_candidates_path"])

    def test_form_has_no_regeneration_or_network_calls_beyond_data_fetch(self):
        s = open(os.path.join(FD, "index.html"), encoding="utf-8").read() + open(os.path.join(FD, "form_logic.js"), encoding="utf-8").read()
        for bad in ("api.openai.com", "generativelanguage", "XMLHttpRequest", "sendBeacon"):
            self.assertNotIn(bad, s)
        self.assertEqual(s.count("fetch("), 2)         # data/articles.json と data/<article>.json のみ

    def test_page_display_source_is_japanese_gloss(self):
        """公開ページ/音声のKP日本語意味の元=japanese_gloss(フォームの日本語訳と同一項目)であることの静的照合。"""
        s = open(os.path.join(ROOT, "er019_family_x_audio_production_runner_01.py"), encoding="utf-8").read()
        self.assertIn('JA: {kp[\'japanese_gloss\']}', s)
        self.assertIn('ja_r["display_gloss"] = item["japanese_gloss"]', s)


# ================= 委任_07: 人間可読コピー+照合コード(COPY_FORMAT_01)・送信/コピー動作(静的)・復元tool往復 =================
import importlib.util
import random
import tempfile
import re

_PROTO = os.path.join(RD, "proto06_copy_restore_01.py")
_FX = os.path.join(RD, "fixtures_07")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _node_dump(states):
    node = shutil.which("node")
    with tempfile.TemporaryDirectory() as td:
        sp = os.path.join(td, "states.json")
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(states, f, ensure_ascii=False)
        r = subprocess.run([node, os.path.join(RD, "readable_dump_07.js"), sp], capture_output=True, encoding="utf-8", cwd=ROOT)
    assert r.returncode == 0, r.stderr[-2000:]
    return json.loads(r.stdout)


def _live_files():
    idx = _j(os.path.join(FD, "data", "articles.json"))
    return [a["data"] for a in idx["articles"] if a.get("data")]


def _rand_state(proto, d, rnd, with_gram):
    st = proto.random_state(d, rnd, with_gram=False)
    pres = sorted(d.get("grammar") or [], key=lambda g: (g.get("rank") is None, g.get("rank") or 0))[:2]
    st["grammar"] = {}
    if with_gram and pres:
        st["grammar"][rnd.choice(pres)["id"]] = True
    st["grammar_zero"] = False
    if d.get("kp_confirmed"):   # ロック記事: フォームは保存状態でなく確定内容を採用する
        st["choices"] = {r["term"]: r["category"] for r in d["kp_confirmed"]["selection"]}
    return st


class ReadableCopyV3Test(unittest.TestCase):
    """node(フォーム実装)の出力が、設計試作(Python)の人間可読形式・照合コードとバイト一致し、復元で欠落なく往復できる。"""

    @classmethod
    def setUpClass(cls):
        cls.proto = _load(_PROTO, "proto06_copy_restore_01")
        cls.ref = _load(os.path.join(ROOT, "er128_form_readable_restore_01.py"), "er128_form_readable_restore_01")   # 委任_08: 正式な参照実装(コメント既定語/末尾=====の規則を含む)

    def test_fixed_fixture_byte_match(self):
        """固定fixture(データJSONと期待文字列をリポジトリに固定)。長文解説(約4,000字)・仮訳・未生成訳・同名文法・複数行コメントでも欠落なし。"""
        st = _j(os.path.join(_FX, "mini_state.json"))
        with tempfile.TemporaryDirectory() as td:   # git checkoutの改行変換(CRLF)に依存しないよう、fixtureをLFへ正規化したコピーで実行する(d6はLFバイト基準で固定)
            fp = os.path.join(td, "mini_article.json")
            with open(os.path.join(_FX, "mini_article.json"), "rb") as f:
                raw = f.read().replace(b"\r\n", b"\n")
            with open(fp, "wb") as f:
                f.write(raw)
            out = _node_dump([{"file": fp, "st": st}])[0]
        with open(os.path.join(_FX, "mini_expected_readable.txt"), encoding="utf-8", newline="") as f:
            exp = f.read().replace("\r\n", "\n")
        self.assertEqual(out["readable"], exp)
        d = _j(os.path.join(_FX, "mini_article.json"))
        body = d["grammar"][0]["body"][:-len("\n=====")]
        self.assertIn("【解説全文】\n" + body + "\n【解説ここまで】", out["readable"])   # 解説全文が一字も欠けない(終端記号=====のみ除外)
        self.assertNotIn("=====", out["readable"])
        self.assertTrue(re.search(r"照合コード\(変更しないでください\)：AIF1-mini_article-[0-9a-f]{6}-aaaa1111-1234abcd-[0-9a-f]{10}-[0-9a-f]{10}-[0-9a-f]{8}-[0-9a-f]{4}$", out["readable"]))
        self.assertTrue(out["send"]["text"].startswith("以下はeigo-radioの学習項目選定結果です。"))
        self.assertTrue(out["send"]["text"].endswith(exp))

    def test_node_python_byte_match_all_live_data(self):
        """全公開データ×乱択状態: node出力==Python試作出力(照合コードを含むバイト一致)。0/1件文法・ロック記事を含む。"""
        rnd = random.Random(20261027)
        states, metas = [], []
        for f in _live_files():
            d = _j(os.path.join(FD, f))
            for trial in range(8):
                st = _rand_state(self.proto, d, rnd, with_gram=(trial % 2 == 1))
                states.append({"file": f, "st": st})
                metas.append((f, d, st))
        outs = _node_dump(states)
        n_gram = n_lock = 0
        for (f, d, st), o in zip(metas, outs):
            stem = os.path.basename(f)[:-5]
            d6 = hashlib.sha256(open(os.path.join(FD, f), "rb").read()).hexdigest()[:6]
            st_ref = dict(st, grammar_zero=True) if not any((st.get("grammar") or {}).values()) else st   # 参照実装は新仕様の文法未決定を拒否するため0件は明示
            exp = self.ref.build_readable(stem, d, st_ref, d6)
            self.assertEqual(o["readable"], exp, f)
            n_gram += 1 if st["grammar"] else 0
            n_lock += 1 if d.get("kp_confirmed") else 0
        self.assertGreaterEqual(len(outs), 64)
        self.assertGreater(n_gram, 0)
        self.assertGreater(n_lock, 0)

    def test_restore_roundtrip_matches_buildStructured_and_detects_tamper(self):
        """nodeのコピー全文 -> 復元(試作) -> payload == フォーム既存buildStructured(selection/article/comment)。改変は全てfail-closed。"""
        rnd = random.Random(7)
        states, metas = [], []
        for f in _live_files():
            d = _j(os.path.join(FD, f))
            for trial in range(4):
                st = _rand_state(self.proto, d, rnd, with_gram=(trial % 2 == 1))
                states.append({"file": f, "st": st})
                metas.append((f, d, st))
        outs = _node_dump(states)
        data_dir = os.path.join(FD, "data")
        ok = 0
        for (f, d, st), o in zip(metas, outs):
            if d.get("candidates_sha256") is None:
                continue   # DEV Trial doc(候補集合shaなし)はer128が拒否する現行仕様。復元自体は別途
            payload, _ = self.proto.restore(o["readable"], data_dir)
            st_ = json.loads(json.dumps(o["structured"]))
            for g_ in st_["selection"]["grammar"]:   # フォームは表示順位(rank/rank_label)も併記するが、er128 cmd_from_formは読まない(照合の対象外)
                g_.pop("rank", None)
                g_.pop("rank_label", None)
            diffs = self.proto.compare(payload, {"structured": st_})
            self.assertEqual(diffs, [], f)
            ok += 1
        self.assertGreaterEqual(ok, 24)
        # 改変検出(AI島 Advanced + 文法1件): どれも RestoreError
        f = "data/ai_island_temple__b1b__prod.json"
        d = _j(os.path.join(FD, f))
        st = _rand_state(self.proto, d, random.Random(3), with_gram=True)
        if not st["grammar"]:
            st["grammar"][d["grammar"][0]["id"]] = True
        st["comment"] = "文法の例文を短く"
        txt = _node_dump([{"file": f, "st": st}])[0]["readable"]
        self.proto.restore(txt, data_dir)   # 無改変は復元できる
        lines = txt.split("\n")
        item_i = next(i for i, ln in enumerate(lines) if ln.startswith("- "))
        tampers = {
            "項目行欠落": "\n".join(lines[:item_i] + lines[item_i + 1:]),
            "日本語訳の意訳": txt.replace(lines[item_i], lines[item_i][:-1] + "る", 1),
            "解説の末尾切れ": txt.replace("【解説ここまで】", "", 1),
            "解説の一部改変": txt.replace("**", "", 1),
            "コメント改変": txt.replace("文法の例文を短く", "文法の例文を長く"),
            "照合コード欠落": txt[: txt.index("照合コード")],
            "照合コード1字改変": txt[:-1] + ("0" if txt[-1] != "0" else "1"),
        }
        for name, bad in tampers.items():
            with self.assertRaises(self.proto.RestoreError, msg=name):
                self.proto.restore(bad, data_dir)

    def test_er128_restore_module_if_present(self):
        """委任_07R の復元module(er128_form_readable_restore_01.py)が存在する場合、同じフォーム出力を復元でき、試作とpayloadが一致する。未存在ならskip。"""
        p = os.path.join(ROOT, "er128_form_readable_restore_01.py")
        if not os.path.exists(p):
            self.skipTest("er128_form_readable_restore_01.py 未配置")
        mod = _load(p, "er128_form_readable_restore_01")
        f = "data/ai_island_temple__a2__prod.json"
        d = _j(os.path.join(FD, f))
        st = _rand_state(self.proto, d, random.Random(11), with_gram=False)
        o = _node_dump([{"file": f, "st": st}])[0]
        pl, _ = mod.restore(o["readable"], os.path.join(FD, "data"), None)
        p0, _ = self.proto.restore(o["readable"], os.path.join(FD, "data"))
        for k in ("article", "selection", "comment"):
            self.assertEqual(pl[k], p0[k], k)

    def test_send_buttons_static_contract(self):
        """index.html: 送信=常にコピー後にwindow.open(同一クリック処理内)、URL閾値超は chatgpt.com を開き案内、コピー=JSON無し、技術情報はdetails内、上限ロジック不変。"""
        h = open(os.path.join(FD, "index.html"), encoding="utf-8").read()
        js = open(os.path.join(FD, "form_logic.js"), encoding="utf-8").read()
        self.assertIn("buildReadable", h)
        self.assertIn("<details", h)
        self.assertIn("技術情報付きでコピー", h)
        self.assertIn('id="copyTech"', h)
        self.assertLess(h.index("clipboard.writeText"), h.index("window.open(target"))   # writeTextをwindow.openより先に開始
        self.assertIn("'https://chatgpt.com/'", h)                                         # URL超過時は q なしで開く
        self.assertNotIn("Claude Code向け指示案", js)
        self.assertIn("var LIMITS = [3, 5, 12];", js)
        self.assertEqual(h.count("fetch("), 2)


if __name__ == "__main__":
    unittest.main()
