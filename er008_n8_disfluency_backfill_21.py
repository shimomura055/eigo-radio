# -*- coding: utf-8 -*-
# ============================================================
# er008_n8_disfluency_backfill_21.py
# ============================================================
# ER-008-N8-FINAL-QA-HARDENING-21 Item 1/8: 新しいAssemble Gate
# (_segment_missing_mandatory_disfluency_qa)は、disfluency QA配線
# (ER-18/19)より前に生成された既存assetをすべてfail-closedでblockする。
# これらの多くは実際には問題のない音声のはずなので、TTSを再生成せず、
# 無料・ローカル実行のfaster-whisperによるdisfluency検査を既存wavへ
# 直接かけ直し、
#   - flagged=False(異常なし) -> tts_generation_results.jsonへ
#     disfluency_checked=True/disfluency_evidenceをbackfillするだけ
#     (追加API課金ゼロ)
#   - flagged=True(反復検出) -> 実際にProduction経路で再生成が必要な
#     segmentとしてリストする(kp2のuneven choiceはここに入る想定)
# を判定する。
from __future__ import annotations

import json
import os

import er008_disfluency_qa_18 as dq18

THEME_DIR = "er006_output/pool_pilot_01/pool_n8_airport_line"

MANDATORY_BY_LEVEL = {
    "a2": {
        "segments": ("point_one_heading", "point_two_heading", "in_one_line"),
    },
    "b1b": {
        "segments": ("preview", "comment_1", "comment_2", "comment_3", "comment_4",
                     "in_one_line", "point_one_heading", "point_two_heading"),
    },
}


def _results_path(level_dir: str) -> str:
    return f"{THEME_DIR}/{level_dir}/audit/tts_generation_results.json"


def _load(level_dir: str) -> dict:
    with open(_results_path(level_dir), encoding="utf-8") as f:
        return json.load(f)


def _save(level_dir: str, data: dict) -> None:
    with open(_results_path(level_dir), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def _check_and_backfill(level_dir: str, seg_key: str, entry: dict) -> dict:
    path = entry.get("path") or f"{THEME_DIR}/{level_dir}/narration/{seg_key}.wav"
    if not os.path.exists(path):
        return {"seg_key": seg_key, "action": "MISSING_FILE", "path": path}
    evidence = dq18.check_segment_for_disfluency(path, language="en")
    entry["disfluency_checked"] = True
    entry["disfluency_evidence"] = evidence
    if evidence["flagged"]:
        # 検査は実施済み(disfluency_checked=True)だが不合格。status を
        # OKのまま残すとGateのmandatory-evidence判定は素通りしてしまう
        # (「チェック済み」と「合格」を区別する必要がある)ため、status
        # 自体をSTOPPEDへ落としてAUDIO_GATE_ALLOWED_STATUSESから確実に
        # 外し、Human Review Lock経由の追認では通らない形にする。
        entry["status"] = "STOPPED"
        entry["reason"] = (f"disfluency QA再検査で隣接単語repetitionを検出: "
                            f"{evidence['repeats']}")
        entry["disfluency_backfill_note"] = (
            "ER-008-N8-FINAL-QA-HARDENING-21: 既存assetへ無料ローカル"
            "disfluency再検査を実施した結果、反復が検出された。再生成が必要。")
        return {"seg_key": seg_key, "action": "NEEDS_REGENERATION", "path": path,
                "transcript": evidence["transcript"], "repeats": evidence["repeats"]}
    entry["disfluency_backfill_note"] = (
        "ER-008-N8-FINAL-QA-HARDENING-21: disfluency QA配線(ER-18/19)より前に"
        "生成されたassetのため、既存tts_generation_results.jsonにはtop-level "
        "disfluency_checkedが無かった(Gate側の新設fail-closedチェックで検出)。"
        "既存wavへ無料ローカルfaster-whisper再検査を実施し、反復なしを確認の上"
        "backfillした(TTS再生成なし、追加API課金なし)。")
    return {"seg_key": seg_key, "action": "BACKFILLED_CLEAN", "path": path}


def main():
    report = {}
    for level_dir, cfg in MANDATORY_BY_LEVEL.items():
        data = _load(level_dir)
        level_report = []

        for name in cfg["segments"]:
            entry = (data.get("segments") or {}).get(name)
            if entry is None:
                level_report.append({"seg_key": name, "action": "NO_ENTRY"})
                continue
            level_report.append(_check_and_backfill(level_dir, name, entry))

        for rank, kp in (data.get("key_phrases") or {}).items():
            en_entry = kp.get("english")
            if en_entry is None:
                continue
            seg_key = f"kp{rank}_english"
            en_entry["path"] = en_entry.get("path") or f"{THEME_DIR}/{level_dir}/narration/kp{rank}_en.wav"
            level_report.append(_check_and_backfill(level_dir, seg_key, en_entry))

        _save(level_dir, data)
        report[level_dir] = level_report

    with open(f"{THEME_DIR}/disfluency_backfill_21_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    for level_dir, items in report.items():
        print(f"=== {level_dir} ===")
        for item in items:
            print(f"  {item['seg_key']}: {item['action']}")
    return report


if __name__ == "__main__":
    main()
