# ============================================================
# er040_tts_fixed_shell_master_champion_trial_01_page_01.py
# TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01(Trial、Production実装なし)
# ============================================================
# er040_tts_fixed_shell_master_champion_trial_01.pyの実行結果
# (champion_trial_results.json)を読み込み、(1)wav→mp3変換
# (lameenc、ffmpeg不要、環境にffmpeg/pydubが無いため既存precedent
# [er003_v1_b1_p3y_generate.py等]と同じ判断枠組みでmp3を優先し、
# エンコーダが無い場合のみwavのまま配布する)、(2)One→Five連結音声
# (候補セットごと)、(3)比較用index.html、を生成する。GitHub Pages配布
# 専用(`user_test/fixed_shell_champion_trial_01/`)。Production側は
# 一切変更しない(読み取りのみ)。
from __future__ import annotations

import json
import os
import wave

import er002_common as common

try:
    import lameenc
    _HAS_LAMEENC = True
except ImportError:
    _HAS_LAMEENC = False

RESULTS_PATH = "er040_output/tts_fixed_shell_master_champion_trial_01/champion_trial_results.json"
PAGE_DIR = "user_test/fixed_shell_champion_trial_01"

PHRASE_ORDER = [
    "welcome", "preview_intro", "key_phrases_intro", "full_story_intro",
    "num_one", "num_two", "num_three", "num_four", "num_five", "point_explanation",
]
NUMBER_PHRASES = ["num_one", "num_two", "num_three", "num_four", "num_five"]

CANDIDATE_LABELS = {
    "A": "Baseline / Candidate A(Production既存Master、そのまま再利用・新規TTS/ASR呼び出しなし)",
    "B": "Candidate B(Flash-Lite + Role style短文)",
    "C": "Candidate C(既存2.5 Pro系/structured_separation、style override無し)",
}


def wav_to_mp3(wav_path: str, mp3_path: str, bitrate: int = 128) -> bool:
    if not _HAS_LAMEENC:
        return False
    with wave.open(wav_path, "rb") as w:
        channels = w.getnchannels()
        framerate = w.getframerate()
        frames = w.readframes(w.getnframes())
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bitrate)
    encoder.set_in_sample_rate(framerate)
    encoder.set_channels(channels)
    encoder.set_quality(2)
    data = encoder.encode(frames)
    data += encoder.flush()
    os.makedirs(os.path.dirname(mp3_path) or ".", exist_ok=True)
    with open(mp3_path, "wb") as f:
        f.write(data)
    return True


def concat_wavs(wav_paths: list[str], out_wav_path: str) -> bool:
    """同一sample_rate/channelsのwavを単純連結する(pause挿入無し、
    比較目的のため意図的にraw連結、既存の音楽的join処理は使わない)。
    1件も無ければFalseを返す。"""
    frames_all = []
    params = None
    for p in wav_paths:
        if not os.path.exists(p):
            continue
        with wave.open(p, "rb") as w:
            if params is None:
                params = (w.getnchannels(), w.getsampwidth(), w.getframerate())
            frames_all.append(w.readframes(w.getnframes()))
    if not frames_all:
        return False
    os.makedirs(os.path.dirname(out_wav_path) or ".", exist_ok=True)
    with wave.open(out_wav_path, "wb") as w:
        w.setnchannels(params[0])
        w.setsampwidth(params[1])
        w.setframerate(params[2])
        for fr in frames_all:
            w.writeframes(fr)
    return True


def load_results() -> dict:
    with open(RESULTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def measured_metrics_for(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    samples, framerate, channels, _ = common.read_wav_float(path)
    return common.measure_metrics(samples, framerate)


def build_comparison_data(results: dict) -> dict:
    """phraseごとにA/B/Cの状態・model/voice/style/duration/asr_textを
    まとめ、mp3変換とOne-Five連結も行う。副作用(ファイル書き込み)あり。"""
    os.makedirs(PAGE_DIR, exist_ok=True)
    table = {}
    numbers_seq_paths = {"A": [], "B": [], "C": []}

    for name in PHRASE_ORDER:
        row = {}
        for cand in ("A", "B", "C"):
            r = results["candidates"][cand].get(name)
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
                "model": r.get("model") or (r.get("key") or {}).get("tts_model_id"),
                "voice": r.get("voice", "Charon"),
                "tts_backend": r.get("tts_backend"),
                "attempt_count": (
                    "reused(新規attempt無し)" if r.get("reused_from_production")
                    else (len(r.get("attempts_log") or []) if r.get("attempts_log") else (
                        "N/A(既知失敗のため未実行)" if status == "SKIPPED_KNOWN_FAILURE" else None))),
            }
            wav_path = r.get("path")
            if status == "OK" and wav_path and os.path.exists(wav_path):
                metrics = measured_metrics_for(wav_path)
                entry["duration_seconds"] = metrics["duration_seconds"] if metrics else None
                entry["rms_dbfs"] = metrics["rms_dbfs"] if metrics else None
                mp3_name = f"{name}_cand{cand}.mp3"
                mp3_path = f"{PAGE_DIR}/{mp3_name}"
                converted = wav_to_mp3(wav_path, mp3_path)
                entry["audio_file"] = mp3_name if converted else None
                if not converted:
                    entry["audio_file_note"] = "mp3エンコーダ無し、wavのまま未配布(要フォローアップ)"
                if name in NUMBER_PHRASES:
                    numbers_seq_paths[cand].append(wav_path)
            elif status == "SKIPPED_KNOWN_FAILURE":
                entry["evidence_path"] = r.get("evidence_path")
                entry["open_item"] = r.get("open_item")
                entry["source_management_id"] = r.get("source_management_id")
            row[cand] = entry
        table[name] = row

    # One->Five連続再生(候補セットごと、揃っている分のみ連結)
    sequence_files = {}
    for cand in ("A", "B", "C"):
        out_wav = f"er040_output/tts_fixed_shell_master_champion_trial_01/one_to_five_cand{cand}.wav"
        ok = concat_wavs(numbers_seq_paths[cand], out_wav)
        if ok:
            mp3_name = f"one_to_five_cand{cand}.mp3"
            converted = wav_to_mp3(out_wav, f"{PAGE_DIR}/{mp3_name}")
            sequence_files[cand] = {
                "audio_file": mp3_name if converted else None,
                "included_count": len(numbers_seq_paths[cand]),
                "included_of": len(NUMBER_PHRASES),
            }
        else:
            sequence_files[cand] = {"audio_file": None, "included_count": 0, "included_of": len(NUMBER_PHRASES)}

    return {"table": table, "sequence_files": sequence_files}


def _fmt(v) -> str:
    return "" if v is None else str(v)


def build_html(comparison: dict) -> str:
    table = comparison["table"]
    seq = comparison["sequence_files"]
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
                cell = (f'{audio_html}status=OK<br>model={_fmt(e.get("model"))}<br>'
                        f'voice={_fmt(e.get("voice"))}<br>style="{_fmt(e.get("style_prefix_used"))}"<br>'
                        f'duration={_fmt(e.get("duration_seconds"))}s<br>rms={_fmt(e.get("rms_dbfs"))}dBFS<br>'
                        f'ASR="{_fmt(e.get("asr_text"))}"<br>attempts={_fmt(e.get("attempt_count"))}')
            elif status == "SKIPPED_KNOWN_FAILURE":
                cell = (f'status=SKIPPED_KNOWN_FAILURE(既知失敗、再生成せず)<br>'
                        f'根拠: {_fmt(e.get("source_management_id"))} {_fmt(e.get("open_item"))}<br>'
                        f'evidence: {_fmt(e.get("evidence_path"))}')
            elif status == "STOPPED":
                cell = f'status=STOPPED(3attempt不合格)<br>reason={_fmt(e.get("reason"))}'
            else:
                cell = f'status={_fmt(status)}'
            cand_cells.append(f"<td>{cell}</td>")
        rows_html.append(f"<tr><th>{name}</th>{''.join(cand_cells)}</tr>")

    seq_html = []
    for cand in ("A", "B", "C"):
        s = seq[cand]
        if s["audio_file"]:
            seq_html.append(
                f'<div><b>{CANDIDATE_LABELS[cand]}</b>: '
                f'<audio controls src="{s["audio_file"]}"></audio> '
                f'(収録{s["included_count"]}/{s["included_of"]}件、欠落分は無音挿入なし・そのまま省略)</div>')
        else:
            seq_html.append(f'<div><b>{CANDIDATE_LABELS[cand]}</b>: 連結不可(音声0件)</div>')

    legend = "".join(f"<li><b>{k}</b>: {v}</li>" for k, v in CANDIDATE_LABELS.items())

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01 試聴比較</title>
<style>
body {{ font-family: sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; font-size: 13px; }}
th {{ background: #eee; }}
audio {{ width: 240px; }}
</style>
</head>
<body>
<h1>TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01: 固定フレーズ Master Champion 試聴比較</h1>
<p>固定phrase(Welcome/Preview intro/Key Phrase intro/Full Story intro/One〜Five/ポイント解説)について、
Baseline(Candidate A=Production既存Master)/Candidate B(Role style)/Candidate C(既存2.5 Pro系)を比較する。
ユーザーが試聴のうえChampion(各phraseにつき採用candidate)を選んでください。選定後もProduction配線は
別管理IDで実施予定。</p>
<ul>{legend}</ul>
<h2>One→Five 連続再生比較</h2>
{''.join(seq_html)}
<h2>Phraseごと比較表</h2>
<table>
<tr><th>Phrase</th><th>{CANDIDATE_LABELS["A"]}</th><th>{CANDIDATE_LABELS["B"]}</th><th>{CANDIDATE_LABELS["C"]}</th></tr>
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
    with open("er040_output/tts_fixed_shell_master_champion_trial_01/comparison_data.json", "w",
              encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2, default=str)
    print(f"[ER040-PAGE] wrote {PAGE_DIR}/index.html (lameenc available={_HAS_LAMEENC})")


if __name__ == "__main__":
    main()
