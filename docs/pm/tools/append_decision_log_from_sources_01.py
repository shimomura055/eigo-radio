# -*- coding: utf-8 -*-
"""DECISION_LOG.md末尾へ、既存ファイルから抽出したブロックを逐語コピーで追記する汎用スクリプト。
ブロック指定(--block、複数可、順に追記):
  T:<path>                 テキストファイル全体をそのまま追記(見出し・短文用)
  F:<path>@<start>@<end>   転写。start/endは行番号(1始まり、両端含む)。
                           startが数字以外なら「その正規表現に最初に一致する行」。
                           endが数字以外なら「start後で最初に一致する行の直前まで」、'EOF'ならファイル末尾。
F転写ブロックの前に「出典: <path> L<s>-<e>」を自動付与する。--dry-runで書き込まずに境界確認のみ。
"""
import argparse, re, sys
from pathlib import Path

def read_lines(p):
    return Path(p).read_text(encoding="utf-8").split("\n")

def resolve(path, start, end):
    lines = read_lines(path)
    if lines and lines[-1] == "":
        lines = lines[:-1]
    n = len(lines)
    if start.isdigit():
        s = int(start)
    else:
        rx = re.compile(start)
        s = next((i + 1 for i, l in enumerate(lines) if rx.search(l)), None)
        if s is None:
            sys.exit(f"start marker not found: {path} {start}")
    if end == "EOF":
        e = n
    elif end.isdigit():
        e = int(end)
    else:
        rx = re.compile(end)
        e = next((i for i in range(s, n) if rx.search(lines[i])), n)  # 1-based line i = line before match
    if not (1 <= s <= e <= n):
        sys.exit(f"bad range {path} {s}-{e} (n={n})")
    return s, e, "\n".join(lines[s - 1:e])

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="DECISION_LOG.md")
    ap.add_argument("--block", action="append", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out = []
    report = []
    for b in a.block:
        kind, _, rest = b.partition(":")
        if kind == "T":
            txt = Path(rest).read_text(encoding="utf-8").rstrip("\n")
            out.append(txt)
            report.append((rest, "-", len(txt), txt))
        elif kind == "F":
            m = re.match(r"^(.*?)@(.*?)@(.*)$", rest)
            path, st, en = m.group(1), m.group(2), m.group(3)
            s, e, body = resolve(path, st, en)
            label = f"出典: {path} L{s}-{e}"
            out.append(label + "\n\n" + body)
            report.append((path, f"L{s}-{e}", len(body), body))
        else:
            sys.exit(f"bad block kind: {b}")
    full = "\n\n" + "\n\n".join(out) + "\n"
    print(f"total_chars_appended={len(full)} blocks={len(report)}")
    for p, r, c, body in report:
        print(f"- {p} {r} chars={c} head={body[:40]!r} tail={body[-40:]!r}")
    if a.dry_run:
        print("DRY-RUN: no write")
        return
    with open(a.target, "a", encoding="utf-8", newline="") as f:
        f.write(full.replace("\r\n", "\n"))
    print("APPENDED")

if __name__ == "__main__":
    main()
