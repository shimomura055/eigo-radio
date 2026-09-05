# ============================================================
# er011_open112_a2_peak_measurement_16.py
# OPEN-112-TREND-THEME2-B-A2-PEAK-MEASUREMENT-16
# ============================================================
# 目的: Trial-13 A2 AssemblyでProduction関数write_wav_float()のassert
# (peak=1.0350188975890593)が発火した原因を確定するための、読み取り
# 専用の追加計測。
#
# 厳守事項:
#   - 有償API呼び出しは一切行わない(TTS/ASR呼び出し無し)。
#   - Production関数(load_a2_sources/apply_a2_gain/build_a2_timeline)は
#     一切改変せず、そのままimportして呼ぶだけ。stage_assemble_a2は
#     呼ばない(=wavファイルを書き出さない)。
#   - 書き込みは本script自身が置かれているディレクトリ
#     (er011_output/open112_trend_theme2_b_a2_peak_measurement_16/)配下
#     のみに限定する。er011_output/open112_trend_theme2_b_full_audio_
#     trial_13/やer006_output/配下へは一切書き込まない(読み取りのみ)。
#   - docs/pm/ACTIVE_TASK.md・RESULT_PACKET.mdへは触れない(並行taskが
#     使用中のため)。
#   - Git操作は行わない。
#
# 実行方法:
#   .venv/Scripts/python.exe er011_output/open112_trend_theme2_b_a2_peak_measurement_16/er011_open112_a2_peak_measurement_16.py

from __future__ import annotations

import glob
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import numpy as np

# プロジェクトrootをsys.pathへ追加(このscript自体はscratch領域に置くが、
# import対象のProduction moduleはroot直下にあるため)。
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
os.chdir(_PROJECT_ROOT)  # Production関数は相対パス(er011_output/...)を前提にしているため

import er002_common as common  # noqa: E402
import er003_b1_p9a_audio as p9a  # noqa: E402
import er003_v1_n3_01_assemble as asm  # noqa: E402

OUT_DIR = _THIS_DIR  # このscript自身の置き場所(書き込み許容範囲)


def peak(samples: "np.ndarray") -> float:
    return float(np.max(np.abs(samples))) if len(samples) else 0.0


def measure_theme_a2(theme_id: str, out_dir: str, label: str) -> dict:
    """Production関数load_a2_sources→apply_a2_gain→build_a2_timelineを
    そのまま呼び出し、完成前の各piece peakを計測する(wavは書かない)。"""
    theme = {"theme_id": theme_id, "out_dir": out_dir}
    print(f"\n=== [{label}] theme_id={theme_id} out_dir={out_dir} ===")
    try:
        sources = asm.load_a2_sources(theme)
    except Exception as e:
        print(f"  load_a2_sources() failed: {type(e).__name__}: {e}")
        return {"label": label, "theme_id": theme_id, "out_dir": out_dir, "error": f"load_a2_sources: {e}"}

    # Previewの生wav(リサンプル前、24kHz mono)のpeakを直接読み直して測る
    # (apply_a2_gainはpreviewをgain=1.0のまま通すため、sources["preview_mono"]
    # がそのままAssembly前のPreview実体)。
    preview_mono_peak_pre_resample = peak(sources["preview_mono"])

    try:
        parts = asm.apply_a2_gain(sources)
    except Exception as e:
        print(f"  apply_a2_gain() failed: {type(e).__name__}: {e}")
        return {"label": label, "theme_id": theme_id, "out_dir": out_dir, "error": f"apply_a2_gain: {e}"}

    try:
        seq = asm.build_a2_timeline(parts)
    except Exception as e:
        print(f"  build_a2_timeline() failed: {type(e).__name__}: {e}")
        return {"label": label, "theme_id": theme_id, "out_dir": out_dir, "error": f"build_a2_timeline: {e}"}

    pieces = []
    for name, samples in seq:
        pk = peak(samples)
        dur = len(samples) / asm.SR
        pieces.append({"name": name, "peak": pk, "duration_seconds": round(dur, 3)})
    pieces_sorted = sorted(pieces, key=lambda p: p["peak"], reverse=True)

    total_duration = sum(p["duration_seconds"] for p in pieces)
    assembled_would_be_peak = max(p["peak"] for p in pieces) if pieces else 0.0

    print(f"  Preview生wav(リサンプル前, 24kHz mono) peak = {preview_mono_peak_pre_resample:.7f}")
    print(f"  A2合計尺(seq全piece合算) = {round(total_duration, 3)} 秒")
    print(f"  完成peak相当(=各pieceのmax、np.concatenateのみで重ね合わせ無しのため) "
          f"= {assembled_would_be_peak:.7f}")
    print("  --- peak降順 top 10 pieces ---")
    for p in pieces_sorted[:10]:
        print(f"    {p['peak']:.7f}  dur={p['duration_seconds']:>7.3f}s  {p['name']}")

    gain_report = parts["gain_report"]
    print("  --- gain_report ---")
    print(json.dumps(gain_report, ensure_ascii=False, indent=2))

    # 各pieceについて、リサンプル前(gain_report記載のpeak_after、mono
    # 24kHz時点)とリサンプル後(seq内、stereo 48kHz、build_a2_timelineに
    # 渡された実体)のpeakを対比する(Previewはgain_report上は特別scalar
    # なので上のpreview_mono_peak_pre_resampleと比較する)。
    resample_before_after = []
    # gain_reportのkeyとseq/pieceの名前対応表(narration系・a2_segments系)
    label_to_piece_name = {
        "welcome": "Welcome", "topic_intro": "Topic intro", "japanese_title": "Japanese title",
        "preview_intro": "Preview intro", "point_explanation": "Point explanation",
        "key_phrases_intro": "Key phrases intro", "full_story_intro": "Full story intro",
        "a2_comment_1": "Comment 1", "a2_comment_2": "Comment 2", "a2_comment_3": "Comment 3",
        "a2_comment_4": "Comment 4", "a2_full_story_part1": "Full Story Part 1",
        "a2_full_story_part2": "Full Story Part 2", "a2_point_one": "Point One",
        "a2_point_two": "Point Two", "a2_point_one_heading": "Point One semantic heading",
        "a2_point_two_heading": "Point Two semantic heading", "a2_in_one_line": "In One Line",
    }
    piece_peak_by_name = {p["name"]: p["peak"] for p in pieces}
    for gr_key, piece_name in label_to_piece_name.items():
        if gr_key in gain_report and piece_name in piece_peak_by_name:
            before = gain_report[gr_key].get("peak_after")
            after = piece_peak_by_name[piece_name]
            if before is not None and before > 0:
                overshoot_ratio = after / before
            else:
                overshoot_ratio = None
            resample_before_after.append({
                "gain_report_key": gr_key, "piece_name": piece_name,
                "peak_before_resample(mono_24k_after_gain)": before,
                "peak_after_resample(stereo_48k_in_seq)": after,
                "overshoot_ratio": overshoot_ratio,
            })
    # Previewは別枠(gain=1.0でgain_reportに"peak_after"が無いため個別追加)
    preview_after = piece_peak_by_name.get("Preview")
    if preview_after is not None:
        overshoot_ratio = (preview_after / preview_mono_peak_pre_resample
                            if preview_mono_peak_pre_resample > 0 else None)
        resample_before_after.append({
            "gain_report_key": "preview(no gain, gain=1.0)",
            "piece_name": "Preview",
            "peak_before_resample(mono_24k_after_gain)": preview_mono_peak_pre_resample,
            "peak_after_resample(stereo_48k_in_seq)": preview_after,
            "overshoot_ratio": overshoot_ratio,
        })

    print("  --- リサンプル前後peak対比(resample_poly 24k->48kのオーバーシュート) ---")
    for r in sorted(resample_before_after, key=lambda x: (x["overshoot_ratio"] or 0), reverse=True):
        print(f"    {r['piece_name']:<35} before={r['peak_before_resample(mono_24k_after_gain)']:.5f} "
              f"after={r['peak_after_resample(stereo_48k_in_seq)']:.5f} "
              f"ratio={r['overshoot_ratio']:.5f}" if r["overshoot_ratio"] else
              f"    {r['piece_name']:<35} (ratio計算不可)")

    return {
        "label": label, "theme_id": theme_id, "out_dir": out_dir,
        "preview_mono_peak_pre_resample": preview_mono_peak_pre_resample,
        "total_duration_seconds": round(total_duration, 3),
        "assembled_would_be_peak": assembled_would_be_peak,
        "pieces_sorted_by_peak_desc": pieces_sorted,
        "gain_report": gain_report,
        "resample_before_after": resample_before_after,
    }


def collect_past_a2_summaries() -> list:
    """過去A2 assemble済み分の run_summary_assemble.json / gain_report.json
    を一覧化する(er006_output/pool_pilot_01配下 + er011_output/no18系)。
    完成peak・intro peak_after・Previewに関する値を確認する。"""
    candidates = sorted(glob.glob("er006_output/pool_pilot_01/*/a2/run_summary_assemble.json")) + \
        sorted(glob.glob("er011_output/*/*/a2/run_summary_assemble.json")) + \
        sorted(glob.glob("er011_output/*/a2/run_summary_assemble.json"))
    seen = set()
    rows = []
    for rs_path in candidates:
        if rs_path in seen:
            continue
        seen.add(rs_path)
        a2_dir = os.path.dirname(os.path.dirname(rs_path))
        gr_path = os.path.join(a2_dir, "audit", "gain_report.json")
        try:
            with open(rs_path, encoding="utf-8") as f:
                rs = json.load(f)
        except Exception as e:
            rows.append({"path": rs_path, "error": str(e)})
            continue
        row = {
            "a2_dir": a2_dir,
            "run_summary_status": rs.get("status"),
            "completed_peak": rs.get("peak"),
            "clipping_detected": rs.get("clipping_detected"),
            "duration_seconds": rs.get("duration_seconds"),
        }
        if os.path.exists(gr_path):
            try:
                with open(gr_path, encoding="utf-8") as f:
                    gr = json.load(f)
                row["target_rms"] = gr.get("target_rms")
                row["intro_peak_after"] = (gr.get("intro") or {}).get("peak_after")
                row["preview_note"] = (gr.get("preview") or {}).get("note")
                # 完成peakに最も近い候補(narration/a2_segments系のpeak_after最大)を探す
                max_key, max_val = None, -1.0
                for k, v in gr.items():
                    if isinstance(v, dict) and "peak_after" in v and isinstance(v["peak_after"], (int, float)):
                        if v["peak_after"] > max_val:
                            max_val = v["peak_after"]
                            max_key = k
                row["max_peak_after_among_gained_segments"] = max_val
                row["max_peak_after_segment_name"] = max_key
            except Exception as e:
                row["gain_report_error"] = str(e)
        rows.append(row)
    return rows


def main():
    results = {}

    # 1) Trial-13(問題発生元)
    results["trial13"] = measure_theme_a2(
        "open112_trend_theme2_b_full_audio_trial_13",
        "er011_output/open112_trend_theme2_b_full_audio_trial_13",
        "Trial-13(assert発火元)")

    # 2) No.18 specfix_v2(成功例、比較対象)
    results["no18"] = measure_theme_a2(
        "pool_n18_notifications_specfix_v2",
        "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2",
        "No.18 specfix_v2(成功例)")

    # 3) No.9(成功例、FINAL USER APPROVED)
    results["no9"] = measure_theme_a2(
        "pool_n9_tip_screens",
        "er006_output/pool_pilot_01/pool_n9_tip_screens",
        "No.9 tip_screens(成功例、FINAL USER APPROVED)")

    print("\n\n=== 過去A2 run_summary_assemble.json / gain_report.json 一覧 ===")
    past_rows = collect_past_a2_summaries()
    for row in past_rows:
        print(json.dumps(row, ensure_ascii=False))

    out_json_path = os.path.join(OUT_DIR, "measurement_result_16.json")
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "trial13": {k: v for k, v in results["trial13"].items() if k != "gain_report"} | {
                "gain_report": results["trial13"].get("gain_report")},
            "no18": results["no18"],
            "no9": results["no9"],
            "past_a2_summaries": past_rows,
        }, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n計測結果JSONを書き出しました(scratch領域のみ): {out_json_path}")


if __name__ == "__main__":
    main()
