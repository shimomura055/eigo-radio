"""commit/push前 secret scan (GIT-SECRET-REPAIR-01, 2026-10-12).

秘密の値は一切表示しない。出力は 件数・ファイル・行番号・種別 のみ。
  python tools/secret_scan_01.py --paths a b ...      (作業ツリーのファイル)
  python tools/secret_scan_01.py --staged             (indexの内容)
  python tools/secret_scan_01.py --rev <commit>...    (commitが追加/変更したblob)
  python tools/secret_scan_01.py --untracked          (git status --porcelain の ??)
終了コード: 検出あり=1, なし=0.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_ENV_LEN = 12  # 短い値(region名等)は誤検出が多いので除外
SECRET_NAME_RE = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD)", re.I)

PATTERNS = [
    ("azure_key_context", re.compile(rb"(?i)(speech[_-]?key|subscription[-_ ]?key|ocp-apim-subscription-key)[\"'\s:=,\)\(b]{0,12}[0-9a-f]{32}(?![0-9a-zA-Z])")),
    ("sk_key", re.compile(rb"(?<![A-Za-z0-9_-])sk-[A-Za-z0-9_-]{20,}")),
    ("google_aiza", re.compile(rb"AIza[0-9A-Za-z_-]{30,}")),
    ("pplx_key", re.compile(rb"pplx-[A-Za-z0-9]{20,}")),
    ("tavily_key", re.compile(rb"tvly-[A-Za-z0-9_-]{16,}")),
    ("key_assign", re.compile(rb"(?i)(SPEECH_KEY|API_KEY)\s*=\s*[\"']?(?!\*\*\*|<|\$|%|None|\"|'|os\.|your|xxx|REDACTED)[A-Za-z0-9_\-]{16,}")),
]


def env_values(env_path=None):
    """(name, value) list from .env. 値は呼び出し側でも表示しない."""
    p = env_path or os.path.join(ROOT, ".env")
    out = []
    if not os.path.exists(p):
        return out
    try:
        from dotenv import dotenv_values
        d = dotenv_values(p)
    except Exception:
        d = {}
        for ln in open(p, encoding="utf-8", errors="ignore"):
            if "=" in ln and not ln.lstrip().startswith("#"):
                k, v = ln.split("=", 1)
                d[k.strip()] = v.strip().strip("\"'")
    for k, v in d.items():
        if v and len(v) >= MIN_ENV_LEN:
            out.append((k, v))
    return out


def scan_bytes(data, envs):
    """returns list of (lineno, kind)  -- no values."""
    hits = []
    lines = data.split(b"\n")
    for name, val in envs:
        vb = val.encode("utf-8")
        if vb in data:
            for i, ln in enumerate(lines, 1):
                if vb in ln:
                    hits.append((i, "env_value:" + name))
    for kind, rx in PATTERNS:
        for i, ln in enumerate(lines, 1):
            if rx.search(ln):
                hits.append((i, kind))
    return hits


def redact_bytes(data, envs):
    """env値・パターン一致部分を ***REDACTED*** に置換して返す."""
    for name, val in envs:
        data = data.replace(val.encode("utf-8"), b"***REDACTED***")
    for kind, rx in PATTERNS:
        def _sub(m):
            s = m.group(0)
            mm = re.search(rb"[0-9a-fA-F]{32}(?![0-9a-zA-Z])$", s) if kind == "azure_key_context" else None
            if mm:
                return s[:mm.start()] + b"***REDACTED***"
            return b"***REDACTED***"
        data = rx.sub(_sub, data)
    return data


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, check=True).stdout


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="*")
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--rev", nargs="*")
    ap.add_argument("--untracked", action="store_true")
    a = ap.parse_args(argv)
    envs = env_values()
    items = []  # (label, bytes)
    if a.paths:
        for p in a.paths:
            if os.path.isfile(p):
                items.append((p, open(p, "rb").read()))
    if a.untracked:
        for ln in _git("status", "--porcelain", "-z").split(b"\0"):
            if ln.startswith(b"?? "):
                p = ln[3:].decode("utf-8", "replace")
                full = os.path.join(ROOT, p)
                if os.path.isdir(full):
                    for dp, _, fs in os.walk(full):
                        for f in fs:
                            q = os.path.join(dp, f)
                            items.append((os.path.relpath(q, ROOT), open(q, "rb").read()))
                elif os.path.isfile(full):
                    items.append((p, open(full, "rb").read()))
    if a.staged:
        for p in _git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split(b"\0"):
            if p:
                items.append(("[index]" + p.decode(), _git("show", ":" + p.decode())))
    if a.rev:
        for r in a.rev:
            for p in _git("diff-tree", "-r", "--no-commit-id", "--name-only", "--diff-filter=ACMR", "-z", "--root", r).split(b"\0"):
                if p:
                    items.append((f"[{r[:8]}]" + p.decode(), _git("show", f"{r}:{p.decode()}")))
    total = 0
    for label, data in items:
        for ln, kind in scan_bytes(data, envs):
            total += 1
            print(f"HIT {label}:{ln} {kind}")
    print(f"scanned_files={len(items)} env_values_checked={len(envs)} patterns={len(PATTERNS)} hits={total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
