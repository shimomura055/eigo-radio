# ============================================================
# er012_b_voices_a2_cross_audit_fix_03_runner.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03(Lane B)
# ============================================================
# 横断監査(B-1〜B-5)の結果、B-2(英語タイトル直後のJapanese title欠落)
# のみが「既存A2標準の単純な配線漏れ」と判定され修正対象になった
# (B-1[Voice A/Bのslowdown要否]・B-4[Key Phrase "stay put"]は既存の
# USER_DECISION_REQUIRED項目[B-A2-9]・新failure mode疑いのためSTOP、
# 詳細はEDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03_REPORT.md
# 参照)。
#
# 本scriptは既存er012_editorial_b_voices_a2_trial02_runner.py(以下r02、
# 本タスクでjapanese_title関連の新規関数追加・引数修正のみ実施、既存
# 関数の中身は無変更)を、出力先だけ`.../editorial_b_voices_a2_free_
# address_03/`へ環境変数で切り替えて再利用する。_02の出力(article.md・
# parts.json・a2_support_texts.json・Key Phrase選定・Voice A/B解決結果・
# 全narration wav)はそのままコピーして再利用し、Master Audio Store経由
# 含め再生成しない(委任元指示の費用節約規則を遵守)。新規に生成するのは
# japanese_title.wav 1segmentのみ。コストログ(raw_usage_log.jsonl)は
# _02分を引き継がず_03独自に新規開始し、このrunで実際に発生した追加費用
# だけを計測できるようにする。
from __future__ import annotations

import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

SRC_DIR = "er012_output/editorial_b_voices_a2_free_address_02"
DST_DIR = "er012_output/editorial_b_voices_a2_free_address_03"

os.environ["A2_TRIAL02_OUT_DIR_OVERRIDE"] = DST_DIR
os.environ["A2_TRIAL02_EPISODE_BASENAME_OVERRIDE"] = "B_Family_A2_Free_Address_Trial03.wav"
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_tts_generate as n3_tts  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import er012_editorial_b_voices_a2_trial02_runner as r02  # noqa: E402(OUT_DIR override確定後にimport)


def _copy_baseline() -> None:
    """_02の全出力を_03へコピーする(raw_usage_log.jsonlだけは_03独自に
    新規開始するため除外)。コピー先の各ファイル内の"_02"パス文字列参照は
    (assembly段階で再生成されるgain_report/timeline/headroom_report/
    run_summary_assembleを除き)可読性のため"_03"へ置換する。"""
    if os.path.exists(DST_DIR):
        print(f"[FIX03-RUNNER] {DST_DIR} は既に存在するため、コピーをskipします。")
        return
    shutil.copytree(SRC_DIR, DST_DIR)
    old_cost_log = f"{DST_DIR}/a2/audit/raw_usage_log.jsonl"
    if os.path.exists(old_cost_log):
        os.remove(old_cost_log)  # _03独自の新規コストログをcl.install()で作る
    old_episode_wav = f"{DST_DIR}/a2/assembled/B_Family_A2_Free_Address_Trial02.wav"
    if os.path.exists(old_episode_wav):
        os.remove(old_episode_wav)  # Trial03側はrun_assembly()が新規ファイル名で書き出すため不要

    old_needle = "editorial_b_voices_a2_free_address_02"
    new_needle = "editorial_b_voices_a2_free_address_03"
    text_exts = (".json", ".txt", ".jsonl", ".md", ".html")
    for root, _dirs, files in os.walk(DST_DIR):
        for fn in files:
            if not fn.endswith(text_exts):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            if old_needle in content:
                content = content.replace(old_needle, new_needle)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
    print(f"[FIX03-RUNNER] {SRC_DIR} -> {DST_DIR} をコピーしました(baseline再利用、raw_usage_log.jsonlは除外)。")


def _generate_japanese_title_and_merge() -> dict:
    tts_results_path = f"{r02.AUDIT_DIR}/tts_generation_results.json"
    data = r02.load_json(tts_results_path)

    wav_path = f"{r02.NARRATION_DIR}/japanese_title.wav"
    existing = data["segments"].get("japanese_title")
    if existing and existing.get("status") == "OK" and os.path.exists(wav_path):
        print("[FIX03-RUNNER] japanese_title は生成済み(status=OK、wav存在)のため再生成をskipします(TTS再課金防止)。")
        return existing

    print(f"[FIX03-RUNNER] japanese_title生成(Aoede、標準A2経路、B-2追加分): {r02.JAPANESE_TITLE_TEXT!r}...")
    with cl.segment_context("japanese_title"):
        result = n3_tts.generate_a2_japanese_with_reading_safety(
            r02.JAPANESE_TITLE_TEXT, f"{r02.NARRATION_DIR}/japanese_title.wav",
            n3_tts.expected_substring_ja(r02.JAPANESE_TITLE_TEXT), max_extra_chars=30)
    data["segments"]["japanese_title"] = result
    r02.save_json(tts_results_path, data)

    run_summary_path = f"{r02.A2_DIR}/run_summary_tts.json"
    run_summary = r02.load_json(run_summary_path)
    run_summary["segment_status"]["japanese_title"] = result.get("status")
    r02.save_json(run_summary_path, run_summary)

    print(f"[FIX03-RUNNER] japanese_title status={result.get('status')} "
          f"asr_text={result.get('asr_text')!r}")
    return result


def main() -> None:
    _copy_baseline()
    cl.install(r02.COST_LOG_PATH)

    resolution = r02.load_json(f"{r02.AUDIT_DIR}/voice_resolution.json")
    voice_a, voice_b, reasons = resolution["voice_a"], resolution["voice_b"], resolution["reasons"]

    jt_result = _generate_japanese_title_and_merge()
    if jt_result.get("status") != "OK":
        print(f"[FIX03-RUNNER] japanese_title生成がstatus={jt_result.get('status')}のためAssembly/Playerを中止します。")
        return
    r02.assert_budget_ok("after japanese_title TTS (incremental)")

    assemble_summary = r02.run_assembly(voice_a, voice_b)
    if assemble_summary.get("status") != "OK":
        print(f"[FIX03-RUNNER] Assembly status={assemble_summary.get('status')}のためPlayerを生成しません。")
        return

    parts = r02.load_json(f"{r02.A2_DIR}/parts.json")
    support_texts = r02.load_json(f"{r02.A2_DIR}/a2_support_texts.json")
    timeline = r02.load_json(f"{r02.AUDIT_DIR}/timeline.json")
    player_path = r02.build_player_html(assemble_summary, timeline, parts, support_texts, voice_a, voice_b, reasons)
    print(f"[FIX03-RUNNER] player.html: {os.path.abspath(player_path)}")

    jpy, by_provider = r02.compute_cost_jpy_so_far()
    print(f"[FIX03-RUNNER] 完了。今回の追加TTS費用(_03独自ログ、japanese_title 1segmentのみ)="
          f"{jpy:.4f} JPY by_provider={by_provider}")


if __name__ == "__main__":
    main()
