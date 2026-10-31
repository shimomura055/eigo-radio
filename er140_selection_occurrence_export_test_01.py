# -*- coding: utf-8 -*-
"""exporter(export_form_data_01.py)への出現回数統合のtest(API 0・一時ディレクトリ以外へ書かない)。
SELECTION-UI-OCCURRENCE-COUNT-01 委任_02: 既定ON・--without-occurrence・区分未取得の扱い・自己検査・Opus M4(公開済みbatch参照fileの上書き拒否)・M6(区分本文が読めない)。
実行: .venv\\Scripts\\python.exe er140_selection_occurrence_export_test_01.py
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
EXP_PATH = os.path.join(HERE, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools", "export_form_data_01.py")
spec = importlib.util.spec_from_file_location("export_form_data_01_occ", EXP_PATH)
X = importlib.util.module_from_spec(spec)
spec.loader.exec_module(X)

STORY = "The clutter stayed. They put it away. Then she left out the clutter.\n\nA second clutter paragraph."


def cand(cid, used, sel=None, kind=None, rank=1, occ=None):
    c = {"candidate_id": cid, "used_form": used, "selection_phrase": sel or used, "japanese_gloss": "訳", "source_sentence": "s", "origin": "call1", "ai_rank": rank,
         "auto_eligible": True, "human_selectable": True, "flags": {}, "gates": {"gloss": "ALIGNED"}}
    if kind:
        c["kind"] = kind
    c["item"] = {"qa_overall_status": "PASS"}      # presentation_blockers を通す(fail-closed: PASS以外は提示しない)
    if occ is not None:
        c["item"]["occurrence_count"] = occ
    return c


def make_doc(cands):
    return {"level": "Advanced", "candidates": cands, "backfill": {}, "shortfall": False}


def write(root, rel, text):
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return p


def make_run(td, with_support=True):
    write(td, "run/b1b/parts.json", json.dumps({"title": "Clutter Court", "part1": STORY, "part2": "", "part3": "", "in_one_line": "Put it away."}))
    if with_support:
        write(td, "run/b1b/b1_support_texts.json", json.dumps({"preview": "A clutter preview.", "comment_1": "Clutter again."}))
    return os.path.join(td, "run", "b1b", "key_phrases", "kp_candidates.json").replace("\\", "/")


class ConvertOccurrence(unittest.TestCase):
    def convert(self, doc, cand_path, **kw):
        return X.convert(doc, slug="s", level="b1b", name="n", family="X", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="", cand_path=cand_path, **kw)

    def test_default_on_adds_occurrence_and_meta(self):
        with tempfile.TemporaryDirectory() as td:
            cp = make_run(td)
            doc = make_doc([cand("p1", "put away", kind="phrase", rank=1), cand("w1", "clutter", kind="word", rank=2)])
            out = self.convert(doc, cp)
            ph, wd = out["phrases"][0], out["words"][0]
            self.assertEqual(ph["occurrence"]["counts"], {"story": 1, "comment": 0, "preview": 0, "oneline": 1, "title": 0})
            self.assertEqual(ph["occurrence"]["forms"], {"put it away": 2})
            self.assertEqual(wd["occurrence"]["counts"], {"story": 3, "comment": 1, "preview": 1, "oneline": 0, "title": 1})
            self.assertEqual(wd["occurrence"]["total"], 5)
            self.assertEqual(out["occurrence_meta"]["v"], "occ-v1")
            self.assertEqual(out["occurrence_meta"]["unavailable"], [])
            self.assertEqual(sorted(out["occurrence_meta"]["sections"]), ["comment", "oneline", "preview", "story", "title"])

    def test_without_occurrence_flag_is_byte_identical_to_legacy(self):
        with tempfile.TemporaryDirectory() as td:
            cp = make_run(td)
            doc = make_doc([cand("p1", "put away", kind="phrase")])
            off = self.convert(doc, cp, occurrence=False)
            none_path = X.convert(doc, slug="s", level="b1b", name="n", family="X", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="", cand_path=None)
            self.assertNotIn("occurrence", off["phrases"][0])
            self.assertNotIn("occurrence_meta", off)
            self.assertNotIn("occurrence_meta", none_path)     # cand_path無しの呼出(既存test等)は従来とバイト同一
            for k in ("source_kp_candidates_path",):
                off.pop(k, None)
                none_path.pop(k, None)
            self.assertEqual(json.dumps(off, sort_keys=True), json.dumps(none_path, sort_keys=True))

    def test_unavailable_sections_are_recorded_not_zero(self):
        with tempfile.TemporaryDirectory() as td:
            cp = make_run(td, with_support=False)
            out = self.convert(make_doc([cand("w1", "clutter", kind="word")]), cp)
            self.assertEqual(out["words"][0]["occurrence"]["unavailable"], ["comment", "preview"])
            self.assertNotIn("comment", out["words"][0]["occurrence"]["counts"])
            self.assertEqual(out["occurrence_meta"]["unavailable"], ["comment", "preview"])

    def test_no_sections_found_gives_no_entry_occurrence_and_a_warning(self):
        with tempfile.TemporaryDirectory() as td:
            cp = os.path.join(td, "nothing", "b1b", "key_phrases", "kp_candidates.json").replace("\\", "/")
            out = self.convert(make_doc([cand("w1", "clutter", kind="word")]), cp)
            self.assertNotIn("occurrence", out["words"][0])
            self.assertEqual(out["occurrence_meta"]["error"], "sections_not_found")
            self.assertEqual(out["occurrence_meta"]["issues"][0]["code"], "occurrence_unavailable")
            self.assertNotIn("data_warnings", out)      # UIの【データ警告】と二重に出さない(UIは欠落をページ単位で案内する)

    def test_selfcheck_matches_and_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            cp = make_run(td)
            # 実表現 clutter の Story+OneLine+Title 完全一致 = 3(story) +1(title) = 4
            ok = self.convert(make_doc([cand("w1", "clutter", kind="word", occ=4)]), cp)
            self.assertEqual(ok["occurrence_meta"]["selfcheck"], {"checked": 1, "mismatches": []})
            bad = self.convert(make_doc([cand("w1", "clutter", kind="word", occ=3)]), cp)
            mm = bad["occurrence_meta"]["selfcheck"]["mismatches"]
            self.assertEqual(len(mm), 1)
            self.assertEqual((mm[0]["candidate_doc_occurrence_count"], mm[0]["exact_match_count"]), (3, 4))
            self.assertIn("occurrence_selfcheck_mismatch", [i["code"] for i in bad["occurrence_meta"]["issues"]])

    def test_zero_candidate_is_listed(self):
        with tempfile.TemporaryDirectory() as td:
            cp = make_run(td)
            out = self.convert(make_doc([cand("p9", "force away", kind="phrase")]), cp)
            self.assertEqual(out["phrases"][0]["occurrence"]["total"], 0)
            self.assertEqual(out["occurrence_meta"]["zero_candidates"], [{"candidate_id": "p9", "term": "force away"}])

    def test_overflow_entries_also_get_occurrence(self):
        with tempfile.TemporaryDirectory() as td:
            cp = make_run(td)
            cs = [cand("w%d" % i, "clutter" if i == 0 else "clutter%d" % i, kind="word", rank=i + 1) for i in range(7)]
            out = self.convert(make_doc(cs), cp)
            self.assertTrue(out["overflow"])
            self.assertTrue(all("occurrence" in e for e in out["overflow"]))

    def test_n5_generalized_form_counts_both_surface_and_generalized(self):
        with tempfile.TemporaryDirectory() as td:
            cp = make_run(td)
            c = cand("p1", "put something away", sel="put it away", kind="phrase")
            out = self.convert(make_doc([c]), cp)
            self.assertEqual(out["phrases"][0]["occurrence"]["counts"]["story"], 1)
            self.assertEqual(out["phrases"][0]["term"], "put something away")


class PublishedReferenceGuard(unittest.TestCase):
    """Opus M4: 公開済みbatchが参照するdata fileを、内容の異なるデータで上書きしない。"""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.data = os.path.join(self.td.name, "data")
        os.makedirs(os.path.join(self.data, "batches"))
        self.old = "OLD DATA\r\nline2"
        self.out = os.path.join(self.data, "art__b1b__prod.json")
        with open(self.out, "w", encoding="utf-8", newline="") as f:
            f.write(self.old)
        sha = hashlib.sha256(self.old.replace("\r\n", "\n").encode("utf-8")).hexdigest()
        with open(os.path.join(self.data, "batches", "twotier-x-test.json"), "w", encoding="utf-8") as f:
            json.dump({"schema": "eigo_radio_batch_v1", "id": "twotier-x-test", "members": ["art__b1b__prod"], "member_sha256": {"art__b1b__prod": sha}}, f)
        with open(os.path.join(self.data, "batches", "index.json"), "w", encoding="utf-8") as f:
            json.dump({"schema": "eigo_radio_batch_index_v1", "latest": None, "batches": []}, f)

    def tearDown(self):
        self.td.cleanup()

    def test_different_content_is_refused(self):
        c = X.published_reference_conflict(self.out, "NEW DATA")
        self.assertEqual([x["batch"] for x in c], ["twotier-x-test"])

    def test_identical_content_is_allowed_crlf_insensitive(self):
        self.assertEqual(X.published_reference_conflict(self.out, "OLD DATA\nline2"), [])

    def test_new_stem_is_allowed(self):
        self.assertEqual(X.published_reference_conflict(os.path.join(self.data, "art__b1b__occ01.json"), "NEW DATA"), [])

    def test_no_batches_dir_is_allowed(self):
        with tempfile.TemporaryDirectory() as other:
            self.assertEqual(X.published_reference_conflict(os.path.join(other, "x__b1b__prod.json"), "NEW"), [])

    def test_cli_refuses_with_rc5_and_leaves_file_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            cp = make_run(td)
            doc_path = os.path.join(td, "cand.json")
            with open(doc_path, "w", encoding="utf-8") as f:
                json.dump(make_doc([cand("w1", "clutter", kind="word")]), f)
            r = subprocess.run([sys.executable, EXP_PATH, "--cand", doc_path, "--slug", "art", "--level", "b1b", "--name", "n", "--family", "X", "--out", self.out], capture_output=True, cwd=td)
            self.assertEqual(r.returncode, 5, r.stderr.decode("utf-8", "replace")[:300])
            self.assertIn("REFUSED_PUBLISHED_REFERENCE", r.stderr.decode("utf-8", "replace"))
            with open(self.out, "rb") as f:
                self.assertEqual(f.read(), self.old.encode("utf-8"))

    def test_cli_default_on_writes_occurrence_to_new_stem(self):
        with tempfile.TemporaryDirectory() as td:
            cp = make_run(td)
            doc_path = os.path.join(td, "run", "b1b", "key_phrases", "kp_candidates.json")
            os.makedirs(os.path.dirname(doc_path), exist_ok=True)
            with open(doc_path, "w", encoding="utf-8") as f:
                json.dump(make_doc([cand("w1", "clutter", kind="word")]), f)
            new_out = os.path.join(self.data, "art__b1b__occ01.json")
            r = subprocess.run([sys.executable, EXP_PATH, "--cand", doc_path, "--slug", "art", "--level", "b1b", "--name", "n", "--family", "X", "--out", new_out], capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr.decode("utf-8", "replace")[:400])
            res = json.loads(r.stdout.decode("utf-8").strip().splitlines()[-1])
            self.assertEqual(res["occurrence"]["status"], "OK")
            with open(new_out, encoding="utf-8") as f:
                d = json.load(f)
            self.assertIn("occurrence", d["words"][0])
            # --without-occurrence は明示した場合のみ(警告つき)
            off_out = os.path.join(self.data, "art__b1b__off.json")
            r2 = subprocess.run([sys.executable, EXP_PATH, "--cand", doc_path, "--slug", "art", "--level", "b1b", "--name", "n", "--family", "X", "--out", off_out, "--without-occurrence"],
                                capture_output=True)
            self.assertEqual(r2.returncode, 0)
            self.assertIn("--without-occurrence", r2.stderr.decode("utf-8", "replace"))
            with open(off_out, encoding="utf-8") as f:
                self.assertNotIn("occurrence", json.load(f)["words"][0])


class AugmentExistingData(unittest.TestCase):
    def test_augment_adds_only_occurrence_keys(self):
        with tempfile.TemporaryDirectory() as td:
            cp = make_run(td)
            doc = make_doc([cand("p1", "put away", kind="phrase"), cand("w1", "clutter", kind="word", rank=2)])
            base = X.convert(doc, slug="s", level="b1b", name="n", family="X", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="", cand_path=cp, occurrence=False)
            aug = X.augment_form_data(base, doc, cand_path=cp)
            self.assertNotIn("occurrence", base["phrases"][0])      # 元は変更しない
            for k in ("occurrence_meta",):
                self.assertIn(k, aug)
            strip = json.loads(json.dumps(aug))
            strip.pop("occurrence_meta")
            for e in strip["phrases"] + strip["words"]:
                e.pop("occurrence")
            self.assertEqual(json.dumps(strip, sort_keys=True), json.dumps(base, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
