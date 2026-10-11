# -*- coding: utf-8 -*-
"""er053_approved_master_rundir_builder_01.py
FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_05(2026-10-11、課金0、API呼出なし)。

案b(U-1限定受入)のrun dirを、主ツリーの原本(Trial成果物の無改変マスター)から **バイト完全コピー**
(shutil.copyfile)で構成する。git経由の複製は禁止(core.autocrlf=trueでLF->CRLF変換され、selected_brief.md/注記md/
sidecar/writer_constraintsのshaがmanifest記録値と不一致になるため)。コピー後に各ファイルの生shaを原本と照合する。

コピー対象(原本dir基準の相対パス): research_ledger/verified_fact_ledger.txt、storyline_b3/ 直下の全ファイル、
ja_writer/ 配下の全ファイル(revision2.md・runtime_evidence.json[MAQ_TRIAL_W-1のまま不改変]を含む)。
コピーしない: raw_usage_log.jsonl / cost_ledger_maq_01.jsonl / usage.json / export/ / 原本トップのruntime_evidence.json
(新runのコスト集計を汚さないため)。

書込: out_dir 配下の上記ファイル + out_dir/approved_master_rundir_build.json(複製元dir・全ファイル生sha表。
runnerの受理記録へ情報として転記される。判定の入力にはならない)。既存ファイルがある場合は生sha一致のときのみ許可、
不一致はSTOP(上書きしない)。

使い方:
  .venv/Scripts/python.exe er053_approved_master_rundir_builder_01.py --origin-dir <主ツリー原本E dir> --out-dir <run dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import time

BUILD_MANIFEST = "approved_master_rundir_build.json"


def _sha(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def collect_files(origin_dir: str) -> list:
    rels = []
    ledger = "research_ledger/verified_fact_ledger.txt"
    if not os.path.isfile(os.path.join(origin_dir, ledger)):
        raise FileNotFoundError(f"origin missing: {ledger}")
    rels.append(ledger)
    sdir = os.path.join(origin_dir, "storyline_b3")
    if not os.path.isdir(sdir):
        raise FileNotFoundError("origin missing: storyline_b3/")
    for name in sorted(os.listdir(sdir)):
        if os.path.isfile(os.path.join(sdir, name)):
            rels.append(f"storyline_b3/{name}")
    wdir = os.path.join(origin_dir, "ja_writer")
    if not os.path.isdir(wdir):
        raise FileNotFoundError("origin missing: ja_writer/")
    for root, _dirs, files in sorted(os.walk(wdir)):
        for name in sorted(files):
            rels.append(os.path.relpath(os.path.join(root, name), origin_dir).replace("\\", "/"))
    for must in ("ja_writer/revision2.md", "ja_writer/runtime_evidence.json", "storyline_b3/selected_brief.md",
                 "storyline_b3/selected_brief_annotated.md", "storyline_b3/annotation.json",
                 "storyline_b3/annotation_manifest.json", "storyline_b3/writer_constraints.txt"):
        if must not in rels:
            raise FileNotFoundError(f"origin missing: {must}")
    return rels


def build_rundir(origin_dir: str, out_dir: str) -> dict:
    origin_dir = os.path.abspath(origin_dir)
    out_dir = os.path.abspath(out_dir)
    rels = collect_files(origin_dir)
    files = {}
    for rel in rels:
        src = os.path.join(origin_dir, rel)
        dst = os.path.join(out_dir, rel)
        src_sha = _sha(src)
        if os.path.exists(dst):
            if _sha(dst) != src_sha:
                raise RuntimeError(f"[STOP] existing file differs from origin (no overwrite): {rel}")
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)                         # バイト完全コピー(git経由禁止)
        dst_sha = _sha(dst)
        if dst_sha != src_sha:
            raise RuntimeError(f"[STOP] copy sha mismatch: {rel} origin={src_sha} copy={dst_sha}")
        files[rel] = src_sha
    manifest = {"schema_version": 1, "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "origin_dir": origin_dir, "method": "shutil.copyfile(byte-exact, sha verified; git route forbidden)",
                "files": files}
    with open(os.path.join(out_dir, BUILD_MANIFEST), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    m = build_rundir(a.origin_dir, a.out_dir)
    print(f"[rundir-builder] copied {len(m['files'])} files from {m['origin_dir']} -> {os.path.abspath(a.out_dir)} (all sha verified)")


if __name__ == "__main__":
    main()
