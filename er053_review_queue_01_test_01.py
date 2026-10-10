# -*- coding: utf-8 -*-
"""er053_review_queue_01 のtest(API呼び出し0、費用¥0)。
実行: .venv/Scripts/python.exe -m pytest er053_review_queue_01_test_01.py -q
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
from unittest import mock

import er053_review_queue_01 as rq
import er053_risk_flagger_production_01 as rf
from er053_risk_flagger_production_01_test_01 import ARTICLE, LEDGER, Stub, _files, _ok_text, flag

HERE = os.path.dirname(os.path.abspath(__file__))


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="rq_test_")
        self.a, self.l = _files(self.d)
        self.out = os.path.join(self.d, "out")
        os.makedirs(self.out)
        self.root = os.path.join(self.d, "review_queue", "post_en")
        st = Stub({("luna", "A3"): [_ok_text([flag("s3", 0.4)])], ("gemini35fl", "A4"): [_ok_text([flag("s3", 0.6), flag("s4", 0.3, ())])]})
        self.res = rf.run_risk_flagger(article_path=self.a, ledger_path=self.l, article_id="art_x", article_level="b1b",
                                       out_dir=self.out, call_fn=st, sleep_fn=lambda s: None, rf_run_id="rfTEST-1",
                                       producer="trial_fixture", run_label="W1_DOWNSTREAM_DEV_CONFIRM")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_layout_and_required_fields(self):
        r = rq.save_queue(self.res, self.out, root=self.root)
        self.assertTrue(r["saved"])
        base = os.path.join(self.root, "art_x", "b1b__rfTEST-1")
        self.assertEqual(r["path"], base)
        for f in ("queue.json", "queue.md", "inputs/sentences.json", "inputs/ledger.txt", "raw/luna_A3.jsonl", "raw/gemini35fl_A4.jsonl"):
            self.assertTrue(os.path.exists(os.path.join(base, f)), f)
        q = json.load(open(os.path.join(base, "queue.json"), encoding="utf-8"))
        for k in ("schema_version", "article_id", "article_level", "article_sha256", "run_id", "timestamp", "status",
                  "splitter_version", "conditions", "issues", "unlocated_flags", "producer", "run_label", "model_stats"):
            self.assertIn(k, q)
        self.assertNotIn("review_state", json.dumps(q))
        self.assertEqual((q["producer"], q["run_label"]), ("trial_fixture", "W1_DOWNSTREAM_DEV_CONFIRM"))
        it = q["issues"][0]
        for k in ("issue_id", "article_id", "article_level", "article_sha256", "run_id", "timestamp", "sentence_id",
                  "sentence_text", "context", "related_fact_ids", "facts", "flag_reasons", "detected_by", "confidence"):
            self.assertIn(k, it)
        self.assertEqual(it["issue_id"], f"art_x__b1b__{self.res['article_sha256'][:8]}__rfTEST-1__s3")
        self.assertTrue(it["facts"][0]["text"])
        self.assertEqual(it["facts"][0]["fact_id"], "F-003")
        for d in it["detected_by"]:
            for k in ("model_key", "model_id", "condition", "confidence", "raw_flag_source"):
                self.assertIn(k, d)
            self.assertTrue(os.path.exists(os.path.join(base, d["raw_flag_source"])))
        self.assertEqual(len(it["context"]["before"]), 2)
        self.assertLessEqual(len(it["context"]["after"]), 2)

    def test_context_not_in_llm_input(self):
        r = self.res
        for s in r["sentences"]:
            self.assertEqual((s["before"], s["after"]), ("", ""))

    def test_index_append_only(self):
        rq.save_queue(self.res, self.out, root=self.root)
        p = os.path.join(self.root, "index.jsonl")
        first = open(p, "rb").read()
        res2 = dict(self.res, rf_run_id="rfTEST-2")
        rq.save_queue(res2, self.out, root=self.root)
        second = open(p, "rb").read()
        self.assertTrue(second.startswith(first))        # 既存行は不変
        rows = rq.read_index(self.root)
        self.assertEqual([x["run_id"] for x in rows], ["rfTEST-1", "rfTEST-2"])
        self.assertEqual(rows[0]["queue_path"], "art_x/b1b__rfTEST-1")
        self.assertEqual(rows[0]["article_level"], "b1b")
        self.assertFalse(os.path.exists(p + ".lock"))   # lock解放

    def test_concurrent_appends_no_loss(self):
        errs = []

        def w(i):
            try:
                rq.append_index(self.root, {"i": i})
            except Exception as e:  # noqa: BLE001
                errs.append(e)
        ts = [threading.Thread(target=w, args=(i,)) for i in range(12)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(errs, [])
        self.assertEqual(sorted(x["i"] for x in rq.read_index(self.root)), list(range(12)))

    def test_concurrent_appends_12_threads_x_25_rounds_zero_failures(self):
        """C3-5: Windowsで別スレッドがlock保持・削除中のopen(O_EXCL)がPermissionErrorになる再現。
        12スレッド x 25回で失敗0・欠落0(修正前はPermissionErrorで失敗)。"""
        errs = []

        def w(i):
            for k in range(25):
                try:
                    rq.append_index(self.root, {"i": i, "k": k})
                except Exception as e:  # noqa: BLE001
                    errs.append(repr(e))
        ts = [threading.Thread(target=w, args=(i,)) for i in range(12)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(errs, [])
        self.assertEqual(len(rq.read_index(self.root)), 12 * 25)

    def test_lock_timeout_raises_from_append_but_save_queue_is_nonblocking(self):
        os.makedirs(self.root, exist_ok=True)
        lock = os.path.join(self.root, "index.jsonl.lock")
        open(lock, "w").write("held")
        with mock.patch.object(rq, "LOCK_TIMEOUT_S", 0.2):
            with self.assertRaises(TimeoutError):
                rq.append_index(self.root, {"x": 1}, lock_timeout=0.2)
        os.remove(lock)

    def test_save_failure_falls_back_to_out_dir_no_exception(self):
        blocker = os.path.join(self.d, "blockedfile")
        open(blocker, "w").write("x")
        bad_root = os.path.join(blocker, "sub")        # ファイルの下にはディレクトリを作れない
        r = rq.save_queue(self.res, self.out, root=bad_root)
        self.assertFalse(r["saved"])
        self.assertTrue(r["fallback"])
        self.assertTrue(os.path.exists(os.path.join(r["fallback_path"], "queue.json")))
        ep = json.load(open(os.path.join(self.out, "entry_point.json"), encoding="utf-8"))
        self.assertFalse(ep["risk_flagger_queue"]["b1b"]["saved"])

    def test_rf_unavailable_is_also_saved(self):
        st = Stub(default=RuntimeError("down"))
        res = rf.run_risk_flagger(article_path=self.a, ledger_path=self.l, article_id="art_y", article_level="a2",
                                  out_dir=self.out, call_fn=st, sleep_fn=lambda s: None, rf_run_id="rfU")
        r = rq.save_queue(res, self.out, root=self.root)
        self.assertTrue(r["saved"])
        q = json.load(open(os.path.join(r["path"], "queue.json"), encoding="utf-8"))
        self.assertEqual(q["status"], "RF_UNAVAILABLE")
        self.assertEqual(q["issues"], [])
        self.assertIn("RF_UNAVAILABLE", open(os.path.join(r["path"], "queue.md"), encoding="utf-8").read())

    def test_markdown_contains_key_info(self):
        r = rq.save_queue(self.res, self.out, root=self.root)
        md = open(os.path.join(r["path"], "queue.md"), encoding="utf-8").read()
        for s in ("b1b", "rfTEST-1", "luna-A3", "gemini35fl-A4", "F-003", "候補一覧"):
            self.assertIn(s, md)

    def test_safe_component_blocks_traversal(self):
        self.assertNotIn("..", rq.safe_component("../../etc"))
        self.assertNotIn("/", rq.safe_component("a/b\\c"))
        p = rq.queue_dir("../../evil", "b1b", "r1", self.root)
        self.assertTrue(os.path.abspath(p).startswith(os.path.abspath(self.root)))

    def test_root_is_file_relative_not_cwd(self):
        self.assertEqual(rq.QUEUE_ROOT, os.path.join(HERE, "review_queue", "post_en"))
        old = os.getcwd()
        os.chdir(self.d)
        try:
            self.assertTrue(os.path.isabs(rq.QUEUE_ROOT))
        finally:
            os.chdir(old)

    def test_derive_article_id(self):
        self.assertEqual(rq.derive_article_id("er019_output/meta/run_03/"), "run_03")
        self.assertEqual(rq.derive_article_id("er019_output/meta/run_03"), "run_03")


class RepoTests(unittest.TestCase):
    def test_readme_exists_and_mentions_levels(self):
        p = os.path.join(HERE, "review_queue", "post_en", "README.md")
        t = open(p, encoding="utf-8").read()
        for s in ("b1b", "a2", "RF_UNAVAILABLE", "queue.md", "index.jsonl"):
            self.assertIn(s, t)

    def test_queue_paths_not_gitignored(self):
        """review_queue配下はgit追跡可能(raw.githubusercontent.comから読める)=.gitignore非該当。読み取り専用のgit check-ignore。"""
        paths = ["review_queue/post_en/index.jsonl", "review_queue/post_en/README.md",
                 "review_queue/post_en/art/b1b__rf1/queue.json", "review_queue/post_en/art/b1b__rf1/queue.md",
                 "review_queue/post_en/art/b1b__rf1/raw/luna_A3.jsonl", "review_queue/post_en/art/b1b__rf1/inputs/ledger.txt"]
        for p in paths:
            r = subprocess.run(["git", "check-ignore", "-q", p], cwd=HERE)
            self.assertEqual(r.returncode, 1, f"{p} is gitignored")


if __name__ == "__main__":
    unittest.main()
