#!/usr/bin/env python3
"""Extract the longest text (start-marker ... end-marker) from a Claude Code transcript jsonl.

Scans every string value (nested) in each jsonl line. For each string, finds
spans beginning with start-marker and ending with end-marker (from a start
occurrence to the last end-marker after it). Picks the longest span overall
(ties: the last occurrence). The model never re-outputs the body.
"""
import argparse
import json
import sys


def iter_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_strings(v)


def spans(s, sm, em):
    pos = 0
    while True:
        i = s.find(sm, pos)
        if i < 0:
            return
        j = s.rfind(em)
        if j >= i:
            yield s[i:j + len(em)]
        pos = i + len(sm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--start-marker", required=True)
    ap.add_argument("--end-marker", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--header-file", default=None)
    a = ap.parse_args()

    best = None
    with open(a.transcript, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            for s in iter_strings(obj):
                if a.start_marker not in s:
                    continue
                for sp in spans(s, a.start_marker, a.end_marker):
                    if best is None or len(sp) >= len(best):
                        best = sp
    if best is None:
        print("NOT_FOUND")
        sys.exit(1)
    header = ""
    if a.header_file:
        with open(a.header_file, encoding="utf-8") as f:
            header = f.read()
        if not header.endswith("\n"):
            header += "\n"
        header += "\n"
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(header + best + "\n")
    print("chars:", len(best))
    print("head60:", repr(best[:60]))
    print("tail60:", repr(best[-60:]))


if __name__ == "__main__":
    main()
