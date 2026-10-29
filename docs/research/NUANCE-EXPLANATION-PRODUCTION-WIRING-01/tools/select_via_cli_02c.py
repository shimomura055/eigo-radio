# -*- coding: utf-8 -*-
"""NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02C Track E: copy-run上で、HR(ニュアンス解説の採用/不採用)をKP HR CLI `nuance-select` で確定する(evidence用)。
候補doc(nuance_candidate.json)の candidate_sha256 を読んで --candidates-sha に渡す。V3フォームと同じ検証・同じsidecarを書く(testで同一性を確認済み)。API 0。
  py select_via_cli_02c.py --run <copy-run> --level b1b|a2 --choice adopt|reject
"""
import argparse
import glob
import json
import os
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
USER_REF = "docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/evidence/user_ref_02C.md"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--level", required=True, choices=("a2", "b1b"))
    ap.add_argument("--choice", required=True, choices=("adopt", "reject"))
    a = ap.parse_args(argv)
    hits = [p for p in glob.glob(os.path.join(a.run, "**", "nuance_candidate.json"), recursive=True)
            if (json.load(open(p, encoding="utf-8")).get("level_key") == a.level)]
    if len(hits) != 1:
        raise SystemExit(f"nuance_candidate.json(level={a.level})が1件ではありません: {hits}")
    doc = json.load(open(hits[0], encoding="utf-8"))
    sha = (doc.get("candidate") or {}).get("candidate_sha256")
    if not sha:
        raise SystemExit(f"候補がありません(status={doc.get('status')})")
    cmd = [sys.executable, os.path.join(REPO, "er119_kp_human_review_cli_01.py"), "nuance-select", "--run", a.run, "--level", a.level,
           "--choice", a.choice, "--candidates-sha", sha, "--by", "sonnet-02C-evidence-human-sim", "--user-ref", USER_REF]
    r = subprocess.run(cmd, cwd=REPO, env=dict(os.environ, PYTHONUTF8="1"))
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
