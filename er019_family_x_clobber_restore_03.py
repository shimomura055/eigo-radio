# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_03: `--only-segments` 実行で、sha256を持たない自run生成の検証済みentryが
SKIPPED_NOT_SELECTEDへ上書きされた場合の、明示的・監査可能な復元CLI(API呼出なし、既定dry-run)。

背景: 旧runnerは新規生成entryにsha256を書かなかったため、`--only-segments`で非選択になるとtry_inherit_from_cachedが
identity証拠不足で引継ぎできず、正式Validation済み(status=OK, asr_verified)の音声がUNVALIDATED(Gate BLOCK)になった。
(根本是正: runnerが新規生成entryへsha256を記録する。本CLIは是正前に上書きされたentryの復元用。)

復元の条件(すべて必要。Gateは緩和しない):
  1. バックアップresults(上書き直前の`tts_generation_results.pre_*.json`)のentryが status=="OK" かつ asr_verified is True
  2. 現行resultsの同labelが上書き可能status(SKIPPED_NOT_SELECTED/INVALIDATED_FOR_REGENERATION/None)
  3. wavが存在し、mtimeがバックアップ作成時刻以前(上書き後に変更されていない)
  4. entry.trim_info.trimmed_duration_secondsと現在wav長が±20ms以内(OF-X7 duration witness)
  5. expected_text(現行parts.json等)がentryのcanonical_text/textと完全一致
  6. 英語segmentは保存済みasr_textを現行(F1後)判定で再判定してOK(OF-X6)
復元entryは`validation_inheritance`(label=REUSED_VALIDATED, evidence=backup_entry_mtime_and_duration_witness, source_ref含む)を付与し、
現在wavのsha256を記録する。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import time

import er019_family_x_validation_inheritance_01 as vi
import er109_xz_scope_01 as er109_scope  # ASR-HOMOPHONE 委任_04: X専用toolの入口decorator(リテラル"X"のみ)

EVIDENCE = "backup_entry_wav_mtime_before_overwrite_and_trimmed_duration"


def _backup_epoch(backup_path: str) -> float:
    m = re.search(r"(\d{8}T\d{6})", os.path.basename(backup_path))
    if m:
        return time.mktime(time.strptime(m.group(1), "%Y%m%dT%H%M%S"))
    return os.path.getmtime(backup_path)


@er109_scope.family_scope("X")  # ASR-HOMOPHONE 委任_04: Family X専用。rejudgeをX scope内で実行
def plan_and_apply(level_dir: str, level: str, backup_path: str, labels: list, apply: bool, expected_texts: dict | None = None) -> dict:
    results_path = f"{level_dir}/audit/tts_generation_results.json"
    cur = json.load(open(results_path, encoding="utf-8"))
    bak = json.load(open(backup_path, encoding="utf-8"))
    expected_texts = expected_texts or vi.derive_expected_texts(level_dir, level, labels)
    cutoff = _backup_epoch(backup_path)
    report = {"level_dir": level_dir, "backup": backup_path, "applied": apply, "labels": {}}
    new_segments = {}
    for label in labels:
        entry = (bak.get("segments") or {}).get(label)
        cur_entry = (cur.get("segments") or {}).get(label)
        r = {"ok": False, "reason": None}
        report["labels"][label] = r
        if not isinstance(entry, dict) or entry.get("status") != "OK" or entry.get("asr_verified") is not True:
            r["reason"] = "BACKUP_ENTRY_NOT_VALIDATED_OK"
            continue
        if (cur_entry or {}).get("status") not in vi._OVERWRITABLE_STATUSES:
            r["reason"] = f"CURRENT_ENTRY_NOT_OVERWRITABLE({(cur_entry or {}).get('status')})"
            continue
        wav = f"{level_dir}/narration/{label}.wav"
        if not os.path.exists(wav):
            r["reason"] = "WAV_MISSING"
            continue
        if os.path.getmtime(wav) > cutoff:
            r["reason"] = "WAV_MODIFIED_AFTER_BACKUP"
            continue
        exp = expected_texts.get(label)
        if exp is None or not vi._text_matches(entry, exp):
            r["reason"] = "CANONICAL_TEXT_MISMATCH_OR_NO_EXPECTED"
            continue
        dw = vi._duration_witness(entry, wav)
        if not dw["ok"]:
            r["reason"] = "DURATION_WITNESS_MISMATCH"
            r["duration_witness"] = dw
            continue
        rj = vi.rejudge_with_current_judge(entry, level, label)
        if rj.get("applicable") and not rj.get("ok"):
            r["reason"] = f"F1_REJUDGE_NG({rj.get('reason')})"
            continue
        current = vi.sha256_file(wav)
        ev = {"current_sha256": current, "evidence": EVIDENCE, "duration_witness": dw}
        new_entry = vi.build_inherited_entry(
            entry, wav, ev, {"kind": "same_out_dir_clobbered_by_only_segments_rerun", "backup": backup_path, "label": label},
            source_style_version=bak.get("style_version"), f1_rejudge=rj, expected_text=exp)
        new_segments[label] = new_entry
        r.update(ok=True, reason="OK", wav_sha256=current, duration_witness=dw, f1_rejudge=rj)
    if apply and new_segments:
        ts = time.strftime("%Y%m%dT%H%M%S")
        shutil.copy2(results_path, f"{level_dir}/audit/tts_generation_results.pre_clobber_restore_{ts}.json")
        cur.setdefault("segments", {}).update(new_segments)
        json.dump(cur, open(results_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        report["backup_of_current"] = f"{level_dir}/audit/tts_generation_results.pre_clobber_restore_{ts}.json"
    return report


def main():
    ap = argparse.ArgumentParser(description="上書きされた検証済みentryの明示復元。既定dry-run")
    ap.add_argument("--level-dir", required=True)
    ap.add_argument("--level", required=True, choices=["a2", "b1b"])
    ap.add_argument("--backup", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if os.path.exists(args.output):
        raise SystemExit(f"output exists: {args.output}")
    rep = plan_and_apply(args.level_dir, args.level, args.backup, [x.strip() for x in args.labels.split(",") if x.strip()], args.apply)
    json.dump(rep, open(args.output, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: v["reason"] for k, v in rep["labels"].items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
