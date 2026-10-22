# -*- coding: utf-8 -*-
"""er109 配線の常設golden回帰test(API 0・費用0)。ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_04(Opus 論点5(d))。
配線前HEAD(b7b6d07d8。Production .pyはbdf25b42fと同一)で固定した署名fixture(er109_output/aho4_golden_01/)を、現行コードで再計算した署名と比較する:
  scope未設定(=Family A/B/C・単体呼出相当) : 全行の署名が配線前と**完全一致**(5経路: adapter / adapter_kp / guard_entry / rejudge / make_voter)
  scope X / Z                                 : 署名が変わる行は固定した期待(post_wiring_changed)と完全一致、それ以外は配線前と完全一致。PASS->NGは0。
実行: .venv\\Scripts\\python.exe -m unittest er109_wiring_golden_test_01 -v    (run_project_regression.pyで毎回実行される)
署名計算は別processで行う(共有moduleのmonkeypatchを本processへ残さない)。"""
from __future__ import annotations

import concurrent.futures
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(ROOT, "er109_output", "aho4_golden_01")
TOOL = os.path.join(ROOT, "er109_wiring_signature_01.py")
_VOLATILE = ("created_at", "rejudged_at", "timing", "ms", "checked_at", "total_ms", "secondary_ms")


def _sv(o):
    if isinstance(o, dict):
        return {k: _sv(v) for k, v in o.items() if k not in _VOLATILE}
    if isinstance(o, list):
        return [_sv(v) for v in o]
    return o


def _load_jsonl(path, gz=False):
    opener = (lambda p: gzip.open(p, "rt", encoding="utf-8")) if gz else (lambda p: open(p, encoding="utf-8"))
    d = {}
    with opener(path) as f:
        for l in f:
            if l.strip():
                o = json.loads(l)
                d[o["k"].rsplit("|scope=", 1)[0]] = _sv(o["sig"])
    return d


def _pass_of(sig):
    if "verified" in sig:
        return sig.get("verified")
    if "ok" in sig:
        return sig.get("ok")
    if "blocked" in sig:
        return not sig.get("blocked")
    return None


_CACHE = {}


def _run_all_scopes():
    if _CACHE:
        return _CACHE
    tmp = tempfile.mkdtemp()
    env = dict(os.environ)
    for k in ("OPENAI_API_KEY", "GEMINI_API_KEY", "SPEECH_KEY", "AZURE_SPEECH_KEY"):
        env.setdefault(k, "dummy")
    env["PYTHONIOENCODING"] = "utf-8"

    def one(sc):
        out = os.path.join(tmp, f"sig_{sc}.jsonl")
        cmd = [sys.executable, TOOL, "--rows", os.path.join(FIX, "golden_rows_01.jsonl"), "--scope", sc, "--out", out]
        if sc != "none":
            cmd.append("--require-xz")
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise RuntimeError(f"signature run failed scope={sc}: {r.stderr[-800:]}")
        return sc, _load_jsonl(out)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        for sc, d in ex.map(one, ("none", "X", "Z")):
            _CACHE[sc] = d
    return _CACHE


class GoldenFixtureIntegrity(unittest.TestCase):
    def test_manifest_sha256(self):
        man = json.load(open(os.path.join(FIX, "manifest.json"), encoding="utf-8"))
        for f, sha in man["sha256"].items():
            with self.subTest(file=f):
                self.assertEqual(hashlib.sha256(open(os.path.join(FIX, f), "rb").read()).hexdigest(), sha)
        import re
        self.assertTrue(re.fullmatch(r"[0-9a-f]{40}", man["pre_wiring_commit"]))   # 配線前HEAD(Production .pyは bdf25b42f と同一)で採取

    def test_coverage_of_routes_and_rows(self):
        rows = [json.loads(l) for l in open(os.path.join(FIX, "golden_rows_01.jsonl"), encoding="utf-8") if l.strip()]
        self.assertGreaterEqual(len(rows), 250)
        whys = " ".join(r["why"] for r in rows)
        for needle in ("C4", "stored_onoff_compare_02", "代表: KP", "代表: Azure", "代表: 日本語", "Secondary ortho", "KP: "):
            self.assertIn(needle, whys)
        pre = _load_jsonl(os.path.join(FIX, "pre_wiring_signatures_none_01.jsonl.gz"), gz=True)
        routes = {k.split("|")[1] for k in pre}
        self.assertEqual(routes, {"adapter", "adapter_kp", "guard", "rejudge", "voter"})


class GoldenSignatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.now = _run_all_scopes()
        cls.pre = {"none": _load_jsonl(os.path.join(FIX, "pre_wiring_signatures_none_01.jsonl.gz"), gz=True),
                   "X": _load_jsonl(os.path.join(FIX, "pre_wiring_signatures_X_01.jsonl.gz"), gz=True),
                   "Z": _load_jsonl(os.path.join(FIX, "pre_wiring_signatures_Z_01.jsonl.gz"), gz=True)}
        cls.changed = {sc: _load_jsonl(os.path.join(FIX, f"post_wiring_changed_{sc}_01.jsonl.gz"), gz=True) for sc in ("X", "Z")}

    def test_scope_unset_is_identical_to_pre_wiring_all_routes(self):
        self.assertEqual(set(self.now["none"]), set(self.pre["none"]))
        diff = [k for k in self.pre["none"] if self.now["none"][k] != self.pre["none"][k]]
        self.assertEqual(diff, [], f"scope未設定(A/B/C相当)の署名が配線前から変わった: {diff[:5]}")

    def _scope_check(self, sc):
        pre, now, chg = self.pre[sc], self.now[sc], self.changed[sc]
        self.assertEqual(set(now), set(pre))
        self.assertTrue(set(chg) <= set(pre))
        unexpected = [k for k in pre if k not in chg and now[k] != pre[k]]
        self.assertEqual(unexpected, [], f"想定外の変化({sc}): {unexpected[:5]}")
        wrong = [k for k in chg if now[k] != chg[k]]
        self.assertEqual(wrong, [], f"期待どおりの変化と一致しない({sc}): {wrong[:5]}")
        pass_to_ng = [k for k in pre if _pass_of(pre[k]) is True and _pass_of(now[k]) is False]
        self.assertEqual(pass_to_ng, [], "PASS->NG が発生")
        ng_to_pass = [k for k in pre if _pass_of(pre[k]) is False and _pass_of(now[k]) is True]
        self.assertGreater(len(ng_to_pass), 10)          # 期待どおりの救済が実際に起きている(空打ちでない)

    def test_scope_X_changes_exactly_as_expected(self):
        self._scope_check("X")

    def test_scope_Z_changes_exactly_as_expected(self):
        self._scope_check("Z")

    def test_c4_table_rows_present_with_expected_verdicts(self):
        rows = {(r["canonical"], r["asr"], r.get("azure")): r["id"] for r in
                (json.loads(l) for l in open(os.path.join(FIX, "golden_rows_01.jsonl"), encoding="utf-8") if l.strip())}

        def v(canon, asr, azure=None, sc="X"):
            rid = rows[(canon, asr, azure)]
            return self.now[sc][f"{rid}|adapter"]
        self.assertTrue(v("Pump one's fist.", "Pump 1's fist.")["verified"])
        self.assertEqual(v("I said no.", "I said know.")["state"], "PASS_WITH_WARNING")
        for c, a in [("We have two cats.", "We have one cats."), ("I did not go.", "I did go."), ("I can't go.", "I can go."),
                     ("Take part in it.", "Take apart in it."), ("Point to the map.", "Point 2. the map.")]:
            self.assertFalse(v(c, a)["verified"], (c, a))
            self.assertFalse(v(c, a, sc="none")["verified"], (c, a))
        self.assertFalse(v("Pump one's fist.", "Pump 1's fist.", sc="none")["verified"])      # scope未設定は従来どおりNG


if __name__ == "__main__":
    unittest.main()
