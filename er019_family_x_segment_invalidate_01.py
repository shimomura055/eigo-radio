# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_02 是正③ (OF-X9): segmentの明示的・監査可能な無効化CLI(API呼出なし)。

背景: `--only-segments full_story_part2`はcache OK(status=OK+wav存在+text一致)のとき旧fallback音声を再利用し、再生成されない。
旧N01未適用take等を再生成対象にするには、「検証済みの記録」自体を明示的に無効化する必要がある。

動作(既定dry-run、`--apply`で実行):
  1. resultsのバックアップ `.pre_invalidate_<ts>.json` を作る。
  2. 対象entryのwav(と`<name>_original.wav`)を `<level_dir>/narration/_invalidated_02/<ts>/` へ**移動**(削除しない)。
     元entry全文も同ディレクトリに `<label>.entry.json` として保存する。
  3. resultsのentryを `status=INVALIDATED_FOR_REGENERATION`(理由・日時・退避先・元sha256・元status・元entryのfingerprint)へ置換する。
Audio Validation Gateは status!="OK" をUNVALIDATED扱い(fail-closed)にするため、再生成されるまでassemblyはBLOCKされる。
runnerは status!=OK のentryをreuseせずgenerate_fnへ進む(= 再生成経路に入る)。Gate/ASR/M3は緩和しない。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import time

INVALIDATED = "INVALIDATED_FOR_REGENERATION"
_KP_RE = re.compile(r"^kp([1-9]\d*)_(english|explanation|japanese_meaning|phrase_repeat)$")


def _sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fp(entry) -> str:
    return hashlib.sha256(json.dumps(entry, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _locate(data: dict, label: str):
    """(container, key) を返す。無ければ (None, None)。"""
    m = _KP_RE.match(label)
    if m:
        kp = (data.get("key_phrases") or {}).get(m.group(1))
        if kp is not None and m.group(2) in kp:
            return kp, m.group(2)
        return None, None
    seg = data.get("segments") or {}
    return (seg, label) if label in seg else (None, None)


def plan_and_apply(level_dir: str, labels: list, reason: str, apply: bool, results_path: str = None) -> dict:
    results_path = results_path or f"{level_dir}/audit/tts_generation_results.json"
    data = json.load(open(results_path, encoding="utf-8"))
    ts = time.strftime("%Y%m%dT%H%M%S")
    inv_dir = f"{level_dir}/narration/_invalidated_02/{ts}"
    report = {"results_path": results_path, "timestamp": ts, "reason": reason, "applied": apply, "labels": {}}
    plan = []
    for label in labels:
        cont, key = _locate(data, label)
        if cont is None:
            report["labels"][label] = {"ok": False, "reason": "ENTRY_NOT_FOUND"}
            continue
        entry = cont[key]
        path = entry.get("path") or f"{level_dir}/narration/{label}.wav"
        wavs = [p for p in (path, path[:-4] + "_original.wav" if path.endswith(".wav") else None) if p and os.path.exists(p)]
        rec = {"ok": True, "original_status": entry.get("status"), "original_sha256": entry.get("sha256"),
               "original_wavs": wavs, "original_wav_current_sha256": _sha(path) if os.path.exists(path) else None}
        report["labels"][label] = rec
        plan.append((label, cont, key, entry, wavs, rec))
    if not apply:
        return report
    os.makedirs(inv_dir, exist_ok=True)
    backup = f"{results_path[:-5]}.pre_invalidate_{ts}.json"
    shutil.copyfile(results_path, backup)
    report["backup"] = backup
    for label, cont, key, entry, wavs, rec in plan:
        moved = []
        for w in wavs:
            dst = os.path.join(inv_dir, os.path.basename(w))
            shutil.move(w, dst)
            moved.append(dst)
        with open(os.path.join(inv_dir, f"{label}.entry.json"), "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)
        cont[key] = {
            "status": INVALIDATED, "reason": reason, "invalidated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "moved_to": moved, "entry_backup": os.path.join(inv_dir, f"{label}.entry.json"),
            "original_status": entry.get("status"), "original_sha256": entry.get("sha256"),
            "original_entry_fingerprint_sha256": _fp(entry), "results_backup": backup,
        }
        rec["moved_to"] = moved
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return report


def main():
    ap = argparse.ArgumentParser(description="segmentの明示的無効化(再生成対象化)。既定dry-run")
    ap.add_argument("--run-dir", required=True, help="theme_out_dir(例 .../coffee_prices__run_m2p0_n01_01)")
    ap.add_argument("--level", required=True, choices=["a2", "b1b"])
    ap.add_argument("--segments", required=True, help="カンマ区切り(例 full_story_part2,kp1_english)")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--apply", action="store_true", help="実際に退避+置換する(既定はdry-run)")
    ap.add_argument("--output", default=None, help="結果jsonの出力先(新規ファイル)")
    a = ap.parse_args()
    rep = plan_and_apply(f"{a.run_dir}/{a.level}", [x.strip() for x in a.segments.split(",") if x.strip()],
                         a.reason, a.apply)
    if a.output:
        if os.path.exists(a.output):
            raise SystemExit(f"出力先が既に存在します: {a.output}")
        os.makedirs(os.path.dirname(a.output) or ".", exist_ok=True)
        json.dump(rep, open(a.output, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
