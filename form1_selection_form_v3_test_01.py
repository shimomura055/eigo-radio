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
            if fn.startswith("ui_check_dummy") or fn == "articles.json":
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
        srcs = {
            "ai_island_temple__a2__prod.json": "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01/a2/key_phrases/kp_candidates.json",
            "ai_island_temple__b1b__prod.json": "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01/b1b/key_phrases/kp_candidates.json",
            "redelivery_fee__a2__prod.json": "er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01/key_phrases/a2/kp_candidates.json",
            "redelivery_fee__b1b__prod.json": "er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01/key_phrases/b1b/kp_candidates.json",
            "melos__a2__prod.json": "er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01/key_phrases/a2/kp_candidates.json",
            "monkeys_paw__b1b__prod.json": "docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/replay_results/R5a_Z_monkeys_paw_b1b_frozen_only/kp_candidates_doc.json",
        }
        checked = 0
        for fn, rel in srcs.items():
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path):
                continue
            src = _j(path)
            d = _j(os.path.join(FD, "data", fn))
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
        self.assertEqual(len(files), 7)
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
        self.assertEqual((n_sha, n_null), (5, 2))

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


if __name__ == "__main__":
    unittest.main()
