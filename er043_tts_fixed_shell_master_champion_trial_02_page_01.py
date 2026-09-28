# ============================================================
# er043_tts_fixed_shell_master_champion_trial_02_page_01.py
# TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02(Trial、Production実装なし)
# ============================================================
# er043_tts_fixed_shell_master_champion_trial_02.pyの実行結果
# (champion_trial_results.json)を読み込み、(1)wav→mp3変換・
# One→Five連結音声、(2)比較用index.htmlを生成する。mp3変換・wav連結は
# `er040_tts_fixed_shell_master_champion_trial_01_page_01.py`の既存実装
# (`wav_to_mp3`/`concat_wavs`)をそのままimportして流用する(独自の
# 再実装をしない)。GitHub Pages配布専用(`user_test/fixed_shell_
# champion_trial_02/`)。Production側は一切変更しない(読み取りのみ)。
from __future__ import annotations

import json
import os
import wave

import numpy as np

import er002_common as common
import er040_tts_fixed_shell_master_champion_trial_01_page_01 as page1

RESULTS_PATH = "er043_output/tts_fixed_shell_master_champion_trial_02/champion_trial_results.json"
OUT_DIR = "er043_output/tts_fixed_shell_master_champion_trial_02"
PAGE_DIR = "user_test/fixed_shell_champion_trial_02"

PHRASE_ORDER = [
    "welcome", "preview_intro", "key_phrases_intro", "full_story_intro",
    "num_one", "num_two", "num_three", "num_four", "num_five", "point_explanation",
]
NUMBER_PHRASES = ["num_one", "num_two", "num_three", "num_four", "num_five"]

CANDIDATE_LABELS = {
    "A": "Baseline / Candidate A(現行 Production Master、そのまま再利用・新規TTS/ASR呼び出しなし、¥0)",
    "B": "Candidate B(新規生成、group別に異なる修正style。詳細は各行のStyle Prompt全文を参照)",
    "C": "Candidate C(新規生成、group別に異なる修正style[Bとは別文言]。詳細は各行のStyle Prompt全文を参照)",
}

GROUP_LABELS = {
    "group1_no_complaint": "指摘なし(仕様は変えず同条件で2回生成、ばらつき比較)",
    "group2_full_story_intro_pace": "指摘あり: 発音が速すぎる→余裕を持たせる pace 調整",
    "group3_num_set": "指摘あり: One〜Five 5個セットのテンション/抑揚/語尾/音量/テンポ安定化(Fiveを疑問形にしない)",
    "group4_ja_point_explanation": "指摘あり: 平板→自然な抑揚",
}


def load_results() -> dict:
    with open(RESULTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def measured_metrics_for(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    samples, framerate, channels, _ = common.read_wav_float(path)
    return common.measure_metrics(samples, framerate)


# ------------------------------------------------------------
# 簡易F0(基本周波数)推定(自己相関ベース、librosa等の外部ライブラリ
# 不使用。本環境にlibrosaが無いための代替。short single-word wavの
# 「語尾が上がっているか(疑問形っぽさ)」を大まかに数値化する目的の
# 簡易proxy指標であり、厳密なピッチトラッキングではない[design doc §6]。
# ------------------------------------------------------------
def _autocorr_f0(frame: np.ndarray, sr: int, fmin: float = 70.0, fmax: float = 400.0) -> float | None:
    frame = frame - np.mean(frame)
    if np.max(np.abs(frame)) < 1e-4:
        return None
    corr = np.correlate(frame, frame, mode="full")
    corr = corr[len(corr) // 2:]
    min_lag = int(sr / fmax)
    max_lag = int(sr / fmin)
    if max_lag >= len(corr):
        return None
    segment = corr[min_lag:max_lag]
    if len(segment) == 0 or np.max(segment) <= 0:
        return None
    peak_lag = min_lag + int(np.argmax(segment))
    if peak_lag == 0:
        return None
    return sr / peak_lag


def estimate_pitch_trend(path: str, frame_ms: float = 40.0, hop_ms: float = 20.0) -> dict:
    """wavファイルの先頭30%区間と末尾30%区間の平均F0を比較し、
    上昇(rising、疑問形っぽさの疑い)/下降(falling)/平坦(flat)を返す。
    音声区間が短すぎる・無声区間ばかりの場合はNoneで「判定不可」を示す。"""
    if not os.path.exists(path):
        return {"trend": None, "reason": "file_not_found"}
    samples, sr, channels, _ = common.read_wav_float(path)
    frame_len = int(sr * frame_ms / 1000)
    hop_len = int(sr * hop_ms / 1000)
    if len(samples) < frame_len * 2:
        return {"trend": None, "reason": "audio_too_short_for_pitch_estimation"}
    f0s = []
    for start in range(0, len(samples) - frame_len, hop_len):
        f0 = _autocorr_f0(samples[start:start + frame_len], sr)
        f0s.append(f0)
    voiced = [(i, f0) for i, f0 in enumerate(f0s) if f0 is not None]
    if len(voiced) < 4:
        return {"trend": None, "reason": "insufficient_voiced_frames"}
    n = len(voiced)
    first_third = [f0 for _, f0 in voiced[:max(1, n // 3)]]
    last_third = [f0 for _, f0 in voiced[-max(1, n // 3):]]
    first_avg = float(np.mean(first_third))
    last_avg = float(np.mean(last_third))
    delta_hz = last_avg - first_avg
    delta_ratio = delta_hz / first_avg if first_avg else 0.0
    if delta_ratio > 0.08:
        trend = "rising(疑問形っぽさの疑い)"
    elif delta_ratio < -0.08:
        trend = "falling(平叙文らしい語尾)"
    else:
        trend = "flat(ほぼ平坦)"
    return {"trend": trend, "first_avg_hz": round(first_avg, 1), "last_avg_hz": round(last_avg, 1),
            "delta_ratio": round(delta_ratio, 3), "voiced_frame_count": n,
            "method": "autocorrelation(簡易proxy、librosa不使用、厳密なピッチトラッキングではない)"}


def _wav_path_for(candidate: str, name: str) -> str:
    return (f"{OUT_DIR}/TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_cand{candidate}"
            f"/shell/narration/{name}.wav")


def build_comparison_data(results: dict) -> dict:
    os.makedirs(PAGE_DIR, exist_ok=True)
    table = {}
    numbers_seq_paths = {"A": [], "B": [], "C": []}
    num_set_metrics = {"A": {}, "B": {}, "C": {}}

    for name in PHRASE_ORDER:
        row = {}
        for cand in ("A", "B", "C"):
            r = results["candidates"].get(cand, {}).get(name)
            if r is None:
                row[cand] = {"status": "NOT_ATTEMPTED"}
                continue
            status = r.get("status")
            entry = {
                "status": status,
                "canonical_text": r.get("canonical_text"),
                "style_prefix_used": r.get("style_prefix_used"),
                "asr_text": r.get("asr_text"),
                "reason": r.get("reason"),
                "model": r.get("model") or (r.get("key") or {}).get("tts_model_id")
                         or "gemini-3.8-flash-lite-tts",
                "voice": r.get("voice", "Charon"),
                "group": r.get("group"),
                "attempt_count": (
                    "reused(新規attempt無し、Production Baseline)"
                    if r.get("reused_from_production") or r.get("reused")
                    else (len(r.get("attempts_log") or []) if r.get("attempts_log") else
                          (1 if status == "OK" else None))),
            }
            wav_path = r.get("path") or _wav_path_for(cand, name)
            if status == "OK" and wav_path and os.path.exists(wav_path):
                metrics = measured_metrics_for(wav_path)
                entry["duration_seconds"] = metrics["duration_seconds"] if metrics else None
                entry["rms_dbfs"] = metrics["rms_dbfs"] if metrics else None
                mp3_name = f"{name}_cand{cand}.mp3"
                mp3_path = f"{PAGE_DIR}/{mp3_name}"
                converted = page1.wav_to_mp3(wav_path, mp3_path)
                entry["audio_file"] = mp3_name if converted else None
                if not converted:
                    entry["audio_file_note"] = "mp3エンコーダ無し、wavのまま未配布(要フォローアップ)"
                if name in NUMBER_PHRASES:
                    numbers_seq_paths[cand].append(wav_path)
                    pitch = estimate_pitch_trend(wav_path)
                    entry["pitch_trend"] = pitch
                    num_set_metrics[cand][name] = {
                        "duration_seconds": entry["duration_seconds"], "rms_dbfs": entry["rms_dbfs"],
                        "pitch_trend": pitch.get("trend"),
                    }
            elif status == "STOPPED":
                entry["note"] = "3attempt不合格(既存Human Review Lock、独自retry追加なし)。誤った内容の音声を提示しないため再生用mp3は生成しない。"
            row[cand] = entry
        table[name] = row

    sequence_files = {}
    alignment_summary = {}
    for cand in ("A", "B", "C"):
        out_wav = f"{OUT_DIR}/one_to_five_cand{cand}.wav"
        ok = page1.concat_wavs(numbers_seq_paths[cand], out_wav)
        if ok:
            mp3_name = f"one_to_five_cand{cand}.mp3"
            converted = page1.wav_to_mp3(out_wav, f"{PAGE_DIR}/{mp3_name}")
            sequence_files[cand] = {
                "audio_file": mp3_name if converted else None,
                "included_count": len(numbers_seq_paths[cand]),
                "included_of": len(NUMBER_PHRASES),
            }
        else:
            sequence_files[cand] = {"audio_file": None, "included_count": 0, "included_of": len(NUMBER_PHRASES)}

        durations = [v["duration_seconds"] for v in num_set_metrics[cand].values() if v["duration_seconds"] is not None]
        rmss = [v["rms_dbfs"] for v in num_set_metrics[cand].values() if v["rms_dbfs"] is not None]
        alignment_summary[cand] = {
            "ok_count": len(num_set_metrics[cand]),
            "duration_range_seconds": round(max(durations) - min(durations), 3) if len(durations) >= 2 else None,
            "rms_range_dbfs": round(max(rmss) - min(rmss), 3) if len(rmss) >= 2 else None,
            "per_word": num_set_metrics[cand],
        }

    return {"table": table, "sequence_files": sequence_files, "alignment_summary": alignment_summary}


def _fmt(v) -> str:
    return "" if v is None else str(v)


def _esc(v) -> str:
    s = _fmt(v)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_html(comparison: dict) -> str:
    table = comparison["table"]
    seq = comparison["sequence_files"]
    align = comparison["alignment_summary"]
    rows_html = []
    for name in PHRASE_ORDER:
        row = table[name]
        cand_cells = []
        for cand in ("A", "B", "C"):
            e = row[cand]
            status = e.get("status")
            if status == "OK":
                audio_html = (f'<audio controls src="{e["audio_file"]}"></audio><br>' if e.get("audio_file")
                              else "(mp3変換不可、wav参照のみ)<br>")
                pitch = e.get("pitch_trend") or {}
                pitch_html = (f'pitch_trend={_esc(pitch.get("trend"))}<br>' if pitch.get("trend") else "")
                cell = (f'{audio_html}status=OK<br>model={_esc(e.get("model"))}<br>'
                        f'voice={_esc(e.get("voice"))}<br>'
                        f'<b>Style Prompt全文</b>: "{_esc(e.get("style_prefix_used"))}"<br>'
                        f'duration={_fmt(e.get("duration_seconds"))}s<br>rms={_fmt(e.get("rms_dbfs"))}dBFS<br>'
                        f'{pitch_html}'
                        f'ASR="{_esc(e.get("asr_text"))}"<br>attempts={_fmt(e.get("attempt_count"))}')
            elif status == "STOPPED":
                cell = (f'status=STOPPED(3attempt不合格、既存Human Review Lock)<br>'
                        f'<b>Style Prompt全文</b>: "{_esc(e.get("style_prefix_used"))}"<br>'
                        f'reason={_esc(e.get("reason"))}<br>{_esc(e.get("note"))}')
            else:
                cell = f'status={_esc(status)}'
            cand_cells.append(f"<td>{cell}</td>")
        rows_html.append(f"<tr><th>{name}<br><small>{_esc(row['A'].get('group') or row['B'].get('group') or row['C'].get('group'))}</small></th>{''.join(cand_cells)}</tr>")

    seq_html = []
    for cand in ("A", "B", "C"):
        s = seq[cand]
        a = align[cand]
        if s["audio_file"]:
            seq_html.append(
                f'<div><b>{CANDIDATE_LABELS[cand]}</b>: '
                f'<audio controls src="{s["audio_file"]}"></audio> '
                f'(収録{s["included_count"]}/{s["included_of"]}件、欠落分は無音挿入なし・そのまま省略)<br>'
                f'揃い指標: OK件数={a["ok_count"]}/5、duration幅={_fmt(a["duration_range_seconds"])}秒、'
                f'RMS幅={_fmt(a["rms_range_dbfs"])}dB'
                f'</div>')
        else:
            seq_html.append(f'<div><b>{CANDIDATE_LABELS[cand]}</b>: 連結不可(OK音声0件)</div>')

    legend = "".join(f"<li><b>{k}</b>: {v}</li>" for k, v in CANDIDATE_LABELS.items())

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02 試聴比較</title>
<style>
body {{ font-family: sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; font-size: 13px; }}
th {{ background: #eee; }}
audio {{ width: 240px; }}
</style>
</head>
<body>
<h1>TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02: 固定フレーズ Master Champion 再試聴比較</h1>
<p>固定phrase(Welcome/Preview intro/Key Phrase intro/Full Story intro/One〜Five/ポイント解説)について、
Baseline(Candidate A=現行Production Master)/Candidate B/Candidate Cを比較する。
full_story_introは発音の速さ、One〜Fiveはテンション/抑揚/語尾/音量/テンポの揃い(特にFiveを疑問形に
しない)、ポイント解説は抑揚について、ユーザー指摘への修正候補を含む。
ユーザーが試聴のうえChampion(各phraseにつき採用candidate)を選んでください。選定後もProduction配線は
別管理IDで実施予定。</p>
<ul>{legend}</ul>
<h2>One→Five 連続再生比較</h2>
{''.join(seq_html)}
<h2>Phraseごと比較表(Style Prompt全文を各セルに表示)</h2>
<table>
<tr><th>Phrase / Group</th><th>{CANDIDATE_LABELS["A"]}</th><th>{CANDIDATE_LABELS["B"]}</th><th>{CANDIDATE_LABELS["C"]}</th></tr>
{''.join(rows_html)}
</table>
</body>
</html>
"""


def main() -> None:
    results = load_results()
    comparison = build_comparison_data(results)
    html = build_html(comparison)
    os.makedirs(PAGE_DIR, exist_ok=True)
    with open(f"{PAGE_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    with open(f"{OUT_DIR}/comparison_data.json", "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2, default=str)
    print(f"[ER043-PAGE] wrote {PAGE_DIR}/index.html")


if __name__ == "__main__":
    main()
