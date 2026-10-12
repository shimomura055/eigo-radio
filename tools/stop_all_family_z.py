# -*- coding: utf-8 -*-
"""Family Z 緊急停止ツール(Fable/ユーザー専用。委任_12A新設、PM_GOVERNANCE 26節)。

既定はdry-run(STOP_ALLを作らず、停止対象プロセスを列挙するだけ)。
  python tools/stop_all_family_z.py                      # dry-run: 対象プロセス列挙のみ
  python tools/stop_all_family_z.py --execute --reason "<text>"   # STOP_ALL作成 + 該当プロセスを taskkill /T /F
  python tools/stop_all_family_z.py --release --reason "<text>"   # STOP_ALL解除(監査記録。Fable/ユーザーのみ)
対象プロセス: コマンドラインに下記パターンを含む python/powershell/bash 系(このツール自身は除外)。
  er026_family_z / er062_family_z / er063_family_z / family_z_production_e2e_01 / run_e2e_ / runner_dbg / dbg[0-9]
有料runを起動しない。課金0。
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_STOP_ALL = os.path.join(REPO, "er026_output", "family_z_production_e2e_01", "STOP_ALL")
DEFAULT_PATTERN = r"er026_family_z|er062_family_z|er063_family_z|family_z_production_e2e_01|run_e2e_|runner_dbg|dbg[0-9]"
AUDIT = os.path.join(REPO, "er026_output", "family_z_production_e2e_01", "stop_all_audit.jsonl")


def list_processes(pattern: str) -> list:
    """(pid, name, commandline)。このツール自身(と親chain)は除く。"""
    ps = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|powershell|pwsh|bash|cmd' } | "
          "Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60).stdout
    if not out.strip():
        return []
    rows = json.loads(out)
    rows = rows if isinstance(rows, list) else [rows]
    me, rx = os.getpid(), re.compile(pattern)
    skip = {me, os.getppid()}
    hits = []
    for r in rows:
        cl = r.get("CommandLine") or ""
        if r["ProcessId"] in skip or "stop_all_family_z" in cl or not rx.search(cl):
            continue
        hits.append({"pid": r["ProcessId"], "ppid": r["ParentProcessId"], "name": r["Name"], "cmd": cl[:300]})
    return hits


def _audit(rec: dict) -> None:
    os.makedirs(os.path.dirname(AUDIT), exist_ok=True)
    rec = {"at": datetime.datetime.now().isoformat(), **rec}
    with open(AUDIT, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--execute", action="store_true", help="STOP_ALL作成+該当プロセス停止(未指定=dry-run)")
    ap.add_argument("--release", action="store_true", help="STOP_ALL解除(--reason必須)")
    ap.add_argument("--reason", default=None)
    ap.add_argument("--stop-all-path", default=DEFAULT_STOP_ALL, help="(試験用)STOP_ALLのpath")
    ap.add_argument("--pattern", default=DEFAULT_PATTERN, help="(試験用)停止対象のcommandline正規表現")
    ap.add_argument("--audit-path", default=None, help="(試験用)監査記録path")
    a = ap.parse_args(argv)
    global AUDIT
    if a.audit_path:
        AUDIT = a.audit_path
    if a.release:
        if not (a.reason or "").strip():
            print("--release には --reason が必須", file=sys.stderr)
            return 2
        existed = os.path.exists(a.stop_all_path)
        if existed:
            os.remove(a.stop_all_path)
        _audit({"event": "STOP_ALL_RELEASED", "reason": a.reason, "existed": existed, "path": a.stop_all_path})
        print(json.dumps({"released": existed, "path": a.stop_all_path}, ensure_ascii=False))
        return 0
    hits = list_processes(a.pattern)
    if not a.execute:
        print(json.dumps({"mode": "dry-run", "would_create": a.stop_all_path, "would_stop": hits,
                          "note": "--execute --reason で実行"}, ensure_ascii=False, indent=1))
        return 0
    if not (a.reason or "").strip():
        print("--execute には --reason が必須", file=sys.stderr)
        return 2
    os.makedirs(os.path.dirname(a.stop_all_path), exist_ok=True)
    with open(a.stop_all_path, "w", encoding="utf-8") as f:
        json.dump({"reason": a.reason, "created_at": datetime.datetime.now().isoformat(), "by": "tools/stop_all_family_z.py"},
                  f, ensure_ascii=False)
    stopped = []
    for h in sorted(hits, key=lambda x: x["pid"], reverse=True):
        r = subprocess.run(["taskkill", "/PID", str(h["pid"]), "/T", "/F"], capture_output=True, text=True)
        stopped.append({**h, "taskkill_rc": r.returncode})
    _audit({"event": "STOP_ALL_CREATED", "reason": a.reason, "path": a.stop_all_path, "stopped": stopped})
    print(json.dumps({"mode": "execute", "stop_all": a.stop_all_path, "stopped": stopped}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
