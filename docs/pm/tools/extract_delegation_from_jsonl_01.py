"""Extract the Nth message of a given role from a subagent transcript jsonl (text blocks concatenated)."""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--role", default="user")
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    n = -1
    with open(a.jsonl, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            m = o.get("message") or {}
            if (m.get("role") or o.get("type")) != a.role:
                continue
            c = m.get("content")
            if isinstance(c, str):
                text = c
            else:
                text = "".join(
                    b.get("text", "")
                    for b in (c or [])
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            if not text:
                continue
            n += 1
            if n == a.index:
                with open(a.out, "w", encoding="utf-8", newline="\n") as w:
                    w.write(text)
                print("OK chars=%d" % len(text))
                return 0
    print("NOT_FOUND", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
