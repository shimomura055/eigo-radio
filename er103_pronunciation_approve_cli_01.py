# -*- coding: utf-8 -*-
"""固有名詞TTS発音供給のB階層(媒体由来)承認CLI(運営者=人間が実行。AIが自動承認することはない)。
PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_02 配線点5-9。
使い方(既定はdry-run、--applyで書込み):
  python er103_pronunciation_approve_cli_01.py --surface Khaite --respelling Kate --approved-by <name> [--apply]
Ledgerの該当surface(fold一致、ledger_disabled除外)のentryに human_approved=True / tts_respelling / human_approved_by / human_approved_at を付け、
承認履歴を共有ログ(追記専用)へ残す。承認取消は --revoke。"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er006_pronunciation_ledger_01 as pl

APPROVAL_LOG = "er006_output/audio_retry_cascade_prod_01/pronunciation_approvals.jsonl"


def _fold(s):
    return " ".join((s or "").lower().split())


def approve(surface, respelling, approved_by, *, apply=False, revoke=False, ledger_loader=None, ledger_saver=None, log_path=APPROVAL_LOG):
    load = ledger_loader or pl._load
    save = ledger_saver or pl._save
    ledger = load()
    hits = [k for k, e in ledger.items() if _fold(e.get("surface")) == _fold(surface) and not e.get("ledger_disabled")]
    if not hits:
        return {"ok": False, "reason": "NO_MATCHING_LEDGER_ENTRY", "surface": surface}
    if not revoke:
        if not respelling or not approved_by:
            return {"ok": False, "reason": "respelling_and_approved_by_required"}
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    changed = []
    for k in hits:
        e = ledger[k]
        before = {x: e.get(x) for x in ("human_approved", "tts_respelling", "human_approved_by", "human_approved_at")}
        if revoke:
            for x in before:
                e.pop(x, None)
        else:
            e.update(human_approved=True, tts_respelling=respelling, human_approved_by=approved_by, human_approved_at=now)
        changed.append({"ledger_id": k, "before": before})
    if apply:
        save(ledger)
        os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"at": now, "surface": surface, "respelling": None if revoke else respelling, "approved_by": approved_by,
                                "revoked": bool(revoke), "entries": changed}, ensure_ascii=False) + "\n")
    return {"ok": True, "applied": bool(apply), "entries": [c["ledger_id"] for c in changed]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--surface", required=True)
    ap.add_argument("--respelling")
    ap.add_argument("--approved-by")
    ap.add_argument("--revoke", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    r = approve(a.surface, a.respelling, a.approved_by, apply=a.apply, revoke=a.revoke)
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
