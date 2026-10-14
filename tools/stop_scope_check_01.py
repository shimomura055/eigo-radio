# -*- coding: utf-8 -*-
"""STOP適用範囲チェック(STOP-NOTICE-SCOPE-RULE-PRODUCTION-01、ユーザー2026-10-14 案a承認)。読取専用。

STOPセンチネル・STOP_NOTICEを作成/編集/削除しない。API 0。
判定順(1つでも「適用」があれば stop=True):
  1. 全体STOP_ALL(er026_output/family_z_production_e2e_01/STOP_ALL)           -> 常に適用
  2. 自runディレクトリの STOP                                                    -> 常に適用
  3. docs/pm/delegation_log/*STOP_NOTICE* を1件ずつ判定(下記)
  4. 自runディレクトリの RESTART_STORM_LOCK.json / 生存PIDが保持する RUN_LOCK.json -> 適用
NOTICE判定(上から順、最初に確定したもの):
  a. 構造化欄 status が CLOSED/RESOLVED/RELEASED/EXPIRED/解除/終了 or expires が過去 -> 非適用(inactive)
  b. 本文に自管理ID(--managed-id、複数可)が現れる                                    -> 適用
  c. 構造化欄 scope: ALL/全体/有料run全般/API/PARENT/親/FAMILY                         -> 適用
     scope: run限定(run:<名前>/LIMITED/限定run): 自run名が列挙されていれば適用、なければ非適用(他ID)
     scope が未知の値                                                                  -> 適用(fail-closed)
  d. 旧書式(scope欄なし): 「見出し/ファイル名の管理IDが一致」かつ「対象runを明示限定する文言
     (例: run_e2e_01 の以降の実行は無効)」かつ「全体宣言の文言なし」かつ「対象runが自runでない」
     のときだけ 非適用。それ以外(parse不能・読取失敗・限定文言なし)は 適用(fail-closed)。
管理IDの文字列が違うだけでは非適用にしない(上記a/c/dの根拠が必須)。
CLI: python tools/stop_scope_check_01.py --managed-id ID [--managed-id ID2] --run-dir DIR [--parent-id P] [--out JSON]
     rc=0 非停止 / rc=3 停止
"""
from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOP_ALL_REL = "er026_output/family_z_production_e2e_01/STOP_ALL"
NOTICE_GLOB_REL = "docs/pm/delegation_log/*STOP_NOTICE*"

_FIELD = re.compile(r"^[\s>*\-]*\**\s*(scope|status|issuer|expires|expiry|適用範囲|状態|発行主体|発行|期限)\s*\**\s*[:：]\s*\**\s*(.+?)\s*\**\s*$",
                    re.I | re.M)
_FIELD_KEY = {"scope": "scope", "適用範囲": "scope", "status": "status", "状態": "status",
              "issuer": "issuer", "発行主体": "issuer", "発行": "issuer",
              "expires": "expires", "expiry": "expires", "期限": "expires"}
_INACTIVE_STATUS = re.compile(r"^(closed|resolved|released|expired|inactive|解除|終了|閉鎖|失効)", re.I)
_GLOBAL_SCOPE = re.compile(r"^(all|global|全体|全run|全ての?run|有料run全般|有料run|api|paid|parent|親|family|ファミリ)", re.I)
_LIMITED_SCOPE = re.compile(r"^(run\s*[:=：]|limited|限定run|run限定|限定)", re.I)
# 旧書式: 対象runを明示限定する文言
_LEGACY_LIMIT = re.compile(r"(run_[A-Za-z0-9_]+)\s*の(?:以降の)?実行は無効")
# 旧書式: 全体宣言と読める文言(これがあれば限定とみなさない)
_LEGACY_GLOBAL = re.compile(r"(全体停止|全体STOP|全run|全ての有料|全API|全管理ID|all runs|STOP_ALL を発行|STOP_ALL発行)", re.I)
_HEADING_ID = re.compile(r"^#\s*STOP NOTICE\s*\(\s*([A-Z0-9][A-Z0-9\-]+)", re.M)
_FILE_ID = re.compile(r"^\d{4}-\d{2}-\d{2}_(.+?)_STOP_NOTICE")


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _has_id(text: str, ids) -> list:
    out = []
    for i in ids:
        if i and re.search(r"(?<![A-Za-z0-9\-])" + re.escape(i) + r"(?![A-Za-z0-9\-])", text):
            out.append(i)
    return out


def parse_notice(path: str, text: str) -> dict:
    fields = {}
    for m in _FIELD.finditer(text):
        fields.setdefault(_FIELD_KEY[m.group(1).lower() if m.group(1).lower() in _FIELD_KEY else m.group(1)], m.group(2).strip())
    hm = _HEADING_ID.search(text)
    fm = _FILE_ID.match(os.path.basename(path))
    lm = _LEGACY_LIMIT.search(text)
    return {"fields": fields, "heading_id": hm.group(1) if hm else None, "file_id": fm.group(1) if fm else None,
            "legacy_limited_run": lm.group(1) if lm else None, "legacy_global_phrase": bool(_LEGACY_GLOBAL.search(text))}


def judge_notice(path: str, managed_ids, run_name: str, parent_ids=(), now=None) -> dict:
    rec = {"path": path.replace("\\", "/"), "sha256": None, "applies": True, "rule": None, "reason": None}
    try:
        rec["sha256"] = _sha256(path)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        rec.update(rule="unreadable", reason=f"読取失敗のため fail-closed: {e.__class__.__name__}")
        return rec
    p = parse_notice(path, text)
    rec["parsed"] = {k: p[k] for k in ("fields", "heading_id", "file_id", "legacy_limited_run", "legacy_global_phrase")}
    f = p["fields"]
    # a. status / expires
    st = f.get("status")
    if st and _INACTIVE_STATUS.match(st):
        rec.update(applies=False, rule="a_status_inactive", reason=f"status={st}")
        return rec
    ex = f.get("expires")
    if ex:
        try:
            d = datetime.datetime.fromisoformat(ex.strip().replace("Z", "").split("+")[0].strip())
            if d < (now or datetime.datetime.now()):
                rec.update(applies=False, rule="a_expired", reason=f"expires={ex} は過去")
                return rec
        except ValueError:
            rec.update(rule="a_expires_unparsable", reason=f"expires={ex} がparse不能のため fail-closed")
            return rec
    # b. 自ID(または親ID)が文面にある
    mine = _has_id(text, list(managed_ids) + list(parent_ids))
    if mine:
        rec.update(rule="b_own_or_parent_id_in_text", reason=f"自/親管理IDが本文に存在: {mine}")
        return rec
    # c. 構造化scope
    sc = f.get("scope")
    if sc:
        if _GLOBAL_SCOPE.match(sc):
            rec.update(rule="c_scope_global", reason=f"scope={sc}(全体/親/API系)")
            return rec
        if _LIMITED_SCOPE.match(sc):
            if run_name and re.search(r"(?<![A-Za-z0-9_])" + re.escape(run_name) + r"(?![A-Za-z0-9_])", sc):
                rec.update(rule="c_scope_limited_names_my_run", reason=f"scope={sc} が自run {run_name} を含む")
                return rec
            rec.update(applies=False, rule="c_scope_limited_other", reason=f"scope={sc}: 他ID限定、自IDも自runも非該当")
            return rec
        rec.update(rule="c_scope_unknown", reason=f"scope={sc} が未知の値のため fail-closed")
        return rec
    # d. 旧書式
    ids_ok = p["heading_id"] is not None and p["heading_id"] == p["file_id"]
    lim = p["legacy_limited_run"]
    if ids_ok and lim and not p["legacy_global_phrase"] and lim != run_name:
        rec.update(applies=False, rule="d_legacy_id_match_run_limited",
                   reason=f"旧書式: 見出しID=ファイル名ID={p['heading_id']}、対象run明示限定={lim}、全体宣言なし、自run={run_name}は対象外")
        return rec
    why = []
    if not ids_ok:
        why.append("見出しIDとファイル名IDが一致/取得できない")
    if not lim:
        why.append("対象run限定の文言なし")
    if p["legacy_global_phrase"]:
        why.append("全体宣言の文言あり")
    if lim and lim == run_name:
        why.append("限定対象が自run")
    rec.update(rule="d_failclosed", reason="旧書式で非適用の根拠が揃わず fail-closed: " + "; ".join(why))
    return rec


def _pid_alive(pid: int) -> bool:
    """生存確認。Windowsでは os.kill(pid,0) が TerminateProcess になるため使わない。"""
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        try:
            code = ctypes.c_ulong()
            ok = k.GetExitCodeProcess(h, ctypes.byref(code))
            return bool(ok) and code.value == 259  # STILL_ACTIVE
        finally:
            k.CloseHandle(h)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def check(managed_ids, run_dir: str, repo: str = REPO, parent_ids=(), now=None, pid_alive=_pid_alive,
          self_pids=None) -> dict:
    if isinstance(managed_ids, str):
        managed_ids = [managed_ids]
    run_dir = os.path.abspath(run_dir)
    run_name = os.path.basename(run_dir.rstrip("/\\"))
    self_pids = set(self_pids if self_pids is not None else {os.getpid(), os.getppid()})
    res = {"managed_ids": list(managed_ids), "parent_ids": list(parent_ids), "run_dir": run_dir.replace("\\", "/"),
           "run_name": run_name, "checked_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "sentinels": [], "notices": [], "locks": [], "applicable": [], "stop": False}
    # 1. STOP_ALL
    p = os.path.join(repo, *STOP_ALL_REL.split("/"))
    ex = os.path.exists(p)
    res["sentinels"].append({"kind": "STOP_ALL", "path": p.replace("\\", "/"), "exists": ex})
    if ex:
        res["applicable"].append({"kind": "STOP_ALL", "path": p.replace("\\", "/"), "reason": "全体STOP"})
    # 2. 自run STOP
    p = os.path.join(run_dir, "STOP")
    ex = os.path.exists(p)
    res["sentinels"].append({"kind": "RUN_STOP", "path": p.replace("\\", "/"), "exists": ex})
    if ex:
        res["applicable"].append({"kind": "RUN_STOP", "path": p.replace("\\", "/"), "reason": "自runのSTOP"})
    # 3. NOTICE
    for np_ in sorted(glob.glob(os.path.join(repo, *NOTICE_GLOB_REL.split("/")))):
        j = judge_notice(np_, managed_ids, run_name, parent_ids, now)
        res["notices"].append(j)
        if j["applies"]:
            res["applicable"].append({"kind": "STOP_NOTICE", "path": j["path"], "rule": j["rule"], "reason": j["reason"]})
    # 4. lock
    p = os.path.join(run_dir, "RESTART_STORM_LOCK.json")
    ex = os.path.exists(p)
    res["locks"].append({"kind": "RESTART_STORM_LOCK", "path": p.replace("\\", "/"), "exists": ex})
    if ex:
        res["applicable"].append({"kind": "RESTART_STORM_LOCK", "path": p.replace("\\", "/"), "reason": "再起動嵐ロック"})
    p = os.path.join(run_dir, "RUN_LOCK.json")
    if os.path.exists(p):
        ent = {"kind": "RUN_LOCK", "path": p.replace("\\", "/"), "exists": True}
        try:
            with open(p, "r", encoding="utf-8") as f:
                pid = int(json.load(f).get("pid"))
            ent["pid"] = pid
            ent["alive"] = bool(pid_alive(pid))
            ent["is_self"] = pid in self_pids
            if ent["alive"] and not ent["is_self"]:
                res["applicable"].append({"kind": "RUN_LOCK", "path": p.replace("\\", "/"),
                                          "reason": f"生存PID {pid} が保持(二重起動)"})
        except (OSError, ValueError, TypeError) as e:
            ent["error"] = e.__class__.__name__
            res["applicable"].append({"kind": "RUN_LOCK", "path": p.replace("\\", "/"), "reason": "RUN_LOCK parse不能のため fail-closed"})
        res["locks"].append(ent)
    else:
        res["locks"].append({"kind": "RUN_LOCK", "path": p.replace("\\", "/"), "exists": False})
    res["stop"] = bool(res["applicable"])
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--managed-id", action="append", required=True)
    ap.add_argument("--parent-id", action="append", default=[])
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", default=None, help="結果JSONの保存先(読取専用判定の記録のみ)")
    a = ap.parse_args(argv)
    r = check(a.managed_id, a.run_dir, parent_ids=a.parent_id)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    print(json.dumps({"stop": r["stop"], "applicable": r["applicable"],
                      "notices": [{"path": n["path"], "applies": n["applies"], "rule": n["rule"]} for n in r["notices"]]},
                     ensure_ascii=False, indent=1))
    return 3 if r["stop"] else 0


if __name__ == "__main__":
    sys.exit(main())
