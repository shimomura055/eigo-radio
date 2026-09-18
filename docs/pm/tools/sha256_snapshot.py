"""sha256_snapshot.py

USER-TEST-SCRIPT-READABILITY-PROD-01(Phase A/C共通再利用)。
TSVに記載されたuser_test/unified.html向けURLのsrc値(canonical playerファイル)と、
そのファイルが属するディレクトリ配下の全ファイル(mp3/wav等バイナリ含む)、および
`--extra`で指定した追加ファイルのsha256を計算し、JSON snapshotとして出力する。

canonical記事本文・player.html・音声・Key Phrase asset等を「一切変更していない」
ことを、作業前後のsnapshot diffで証明するための機械チェック用ツール。

使い方:
  python docs/pm/tools/sha256_snapshot.py \
      --paths-from docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv \
      --extra user_test/articles_2026_0918.html \
      --out docs/pm/closeout_136_e2e/script_readability_prod_01/phase_a/sha256_before.json

差分比較:
  python docs/pm/tools/sha256_snapshot.py --diff before.json after.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse as up
from pathlib import Path


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_srcs_from_tsv(tsv_path: str) -> list[str]:
    lines = Path(tsv_path).read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    srcs = []
    for line in lines[1:]:
        if not line.strip():
            continue
        cols = dict(zip(header, line.split("\t")))
        for col in ("standard_url", "advanced_url"):
            u = cols.get(col, "").strip()
            if not u:
                continue
            parsed = up.urlparse(u)
            qs = up.parse_qs(parsed.query)
            src = qs.get("src", [None])[0]
            if src:
                srcs.append(src)
    # de-duplicate while preserving order
    seen = set()
    out = []
    for s in srcs:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def build_snapshot(root: Path, srcs: list[str], extras: list[str]) -> dict:
    files: dict[str, str] = {}
    dirs_covered = set()
    for src in srcs:
        p = root / src
        if p.is_file():
            files[src] = sha256_of(p)
        d = p.parent
        if str(d) not in dirs_covered:
            dirs_covered.add(str(d))
            if d.is_dir():
                for sub in sorted(d.rglob("*")):
                    if sub.is_file():
                        rel = sub.relative_to(root).as_posix()
                        if rel not in files:
                            files[rel] = sha256_of(sub)
    for extra in extras:
        p = root / extra
        if p.is_file():
            files[extra] = sha256_of(p)
    return {"file_count": len(files), "files": files}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paths-from", help="TSVファイル(standard_url/advanced_urlのsrc=を抽出)")
    ap.add_argument("--extra", action="append", default=[], help="追加で含める単一ファイル(repo相対path、複数指定可)")
    ap.add_argument("--root", default=".", help="repo root(既定: カレントディレクトリ)")
    ap.add_argument("--out", help="出力先JSON path")
    ap.add_argument("--diff", nargs=2, metavar=("BEFORE", "AFTER"), help="2つのsnapshot JSONを比較して差分を表示")
    args = ap.parse_args()

    if args.diff:
        before = json.loads(Path(args.diff[0]).read_text(encoding="utf-8"))
        after = json.loads(Path(args.diff[1]).read_text(encoding="utf-8"))
        bf, af = before["files"], after["files"]
        added = sorted(set(af) - set(bf))
        removed = sorted(set(bf) - set(af))
        changed = sorted(k for k in (set(af) & set(bf)) if af[k] != bf[k])
        diff = {"added": added, "removed": removed, "changed": changed,
                "identical": not added and not removed and not changed}
        print(json.dumps(diff, ensure_ascii=False, indent=2))
        return 0 if diff["identical"] else 1

    if not args.paths_from or not args.out:
        print("--paths-from と --out が必要です(またはdiffモードは--diff)", file=sys.stderr)
        return 2

    root = Path(args.root).resolve()
    srcs = extract_srcs_from_tsv(args.paths_from)
    snap = build_snapshot(root, srcs, args.extra)
    snap["srcs"] = srcs
    snap["extras"] = args.extra
    Path(args.out).write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"snapshot written: {args.out} ({snap['file_count']} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
