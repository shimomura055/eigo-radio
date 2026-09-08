# ============================================================
# verify_reuse_sha256_a2.py
# 管理ID: OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01
# ============================================================
# rerun_02/a2(元) と rerun_04/a2(24.1%->about 24%置換+full_story_part1
# 再生成後)を比較し、full_story_part1関連(本体・attempts・
# audit/tts_generation_results.json・article.md・parts.json・
# numeric_minimal_fix_diff_a2.json等の意図的変更対象)を除く全ファイルが
# byte-for-byte一致することを確認する。
from __future__ import annotations

import hashlib
import json
import os

SRC_DIR = "er011_output/open112_trend_theme2_b_final_audio_rerun_02/a2"
DST_DIR = "er011_output/open112_trend_theme2_b_final_audio_rerun_04/a2"
OUT_PATH = "er011_output/open112_trend_theme2_b_final_audio_rerun_04/reuse_sha256_verification_a2.json"

INTENTIONALLY_CHANGED_SUFFIXES = (
    "article.md",
    "parts.json",
    "audit/tts_generation_results.json",
    # Production関数(Human Review Lock)が呼び出しの副作用として自動追記
    # する共有台帳。sha256一致は求めず、別途append-onlyであることを
    # 目視確認する(B1 rerun_04と同一パターン)。
    "audit/review_lock_state.json",
    # 再Assembly(stage_assemble_a2)自体が実測値から再生成する出力
    # (full_story_part1の音声長・gainが変わったことで数値も変わるのが
    # 正常な挙動、B1 rerun_04でも同様にgain_report/timelineは差分扱い)。
    "audit/gain_report.json",
    "audit/timeline.json",
    "audit/headroom_report.json",
    "run_summary_assemble.json",
)
INTENTIONALLY_CHANGED_PREFIXES = (
    "narration/full_story_part1.wav",
    "narration/full_story_part1_original.wav",
    "narration/attempts/full_story_part1_",  # 今回追加されたattemptファイルのみ
    "assembled/",  # 再Assembly出力(ファイル名にrerun番号を含むため別名)
)


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def is_intentionally_changed(rel: str) -> bool:
    if rel in INTENTIONALLY_CHANGED_SUFFIXES:
        return True
    for pref in INTENTIONALLY_CHANGED_PREFIXES:
        if rel.startswith(pref):
            return True
    return False


def main():
    matches = []
    mismatches = []
    changed_intentionally = []
    src_only = []

    src_files = []
    for root, _dirs, files in os.walk(SRC_DIR):
        for fn in files:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, SRC_DIR).replace("\\", "/")
            src_files.append(rel)

    for rel in sorted(src_files):
        src_path = os.path.join(SRC_DIR, rel)
        dst_path = os.path.join(DST_DIR, rel)
        if is_intentionally_changed(rel):
            changed_intentionally.append(rel)
            continue
        if not os.path.exists(dst_path):
            src_only.append(rel)
            continue
        s = sha256_of(src_path)
        d = sha256_of(dst_path)
        if s == d:
            matches.append(rel)
        else:
            mismatches.append({"file": rel, "src_sha256": s, "dst_sha256": d})

    out = {
        "matches": matches,
        "mismatches": mismatches,
        "changed_intentionally_skipped": changed_intentionally,
        "src_only_missing_in_dst": src_only,
        "match_count": len(matches),
        "mismatch_count": len(mismatches),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"match_count={len(matches)} mismatch_count={len(mismatches)}")
    if mismatches:
        print(json.dumps(mismatches, ensure_ascii=False, indent=2))
    print(f"changed_intentionally_skipped={changed_intentionally}")
    print(f"src_only_missing_in_dst={src_only}")
    print(f"-> {OUT_PATH}")


if __name__ == "__main__":
    main()
