# ============================================================
# er022_tts_gemini_3_8_flash_lite_next_trial_01_stage2_assets.py
# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01(Stage 2 A/B試聴artifact組み立て)
# ============================================================
# 性質: Trial補助(API課金なし、読み取り専用+mp3変換+player.html生成のみ)。
# 既存記事artifact(Production A側)は読み取るだけで一切変更しない。
from __future__ import annotations

import json
import os

import soundfile as sf

import er022_tts_gemini_3_8_flash_lite_next_trial_01_stage2 as stage2

OUT_DIR = stage2.OUT_DIR


def wav_to_mp3(src_wav_path: str, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    data, sr = sf.read(src_wav_path)
    sf.write(out_path, data, sr, format="MP3")


def main() -> None:
    result = json.load(open(f"{OUT_DIR}/audit/stage2_result.json", encoding="utf-8"))
    segment_configs = {c["segment_id"]: c for c in stage2.build_segment_configs()}

    rows = []
    for seg in result["segments"]:
        seg_id = seg["segment_id"]
        cfg = segment_configs.get(seg_id)
        if cfg is None or seg.get("final_status") == "NOT_ATTEMPTED_DUE_TO_EARLY_STOP":
            continue
        a_src = cfg["a_wav_path"]
        b_src = f"{OUT_DIR}/narration/{seg_id}.wav"
        a_out = f"{OUT_DIR}/segments_mp3/a/{seg_id}.mp3"
        b_out = f"{OUT_DIR}/segments_mp3/b/{seg_id}.mp3"
        wav_to_mp3(a_src, a_out)
        if os.path.exists(b_src):
            wav_to_mp3(b_src, b_out)
        rows.append({
            "segment_id": seg_id,
            "voice": cfg["voice"],
            "a_duration": cfg["a_duration_seconds"],
            "b_duration": seg.get("final_duration_seconds"),
            "status": seg.get("final_status"),
            "a_mp3": f"segments_mp3/a/{seg_id}.mp3",
            "b_mp3": f"segments_mp3/b/{seg_id}.mp3",
        })
        print(f"[written] {a_out}")
        print(f"[written] {b_out}")

    table_rows = "\n".join(f"""<tr>
  <td>{r['segment_id']}<br><span style="color:#888;font-size:0.8em">Voice: {r['voice']}</span></td>
  <td><audio controls preload="none" src="{r['a_mp3']}"></audio><br>{r['a_duration']}s</td>
  <td><audio controls preload="none" src="{r['b_mp3']}"></audio><br>{r['b_duration']}s
      <br><span class="status status-{r['status']}">{r['status']}</span></td>
</tr>""" for r in rows)

    html = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<title>TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01: Stage 2 A/B試聴</title>
<style>
body {{ font-family: sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
audio {{ width: 100%; }}
.status-OK {{ color: green; font-weight: bold; }}
.status-STOPPED {{ color: red; font-weight: bold; }}
</style></head>
<body>
<h1>TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01: Stage 2(2〜3 segment)A/B試聴
(Trial、Production非採用)</h1>
<p>A=現行Production(gemini-2.5-pro-preview-tts、Structured Separation prompt)。
B=Gemini 3.8 Flash-Lite TTS(gemini-3.8-flash-lite-tts、speech_metadataによる
verbatim transcript方式、style=""[plain TTS、全segment attempt1で即PASS])。
B列のstatusは既存Production ASR検証パイプライン(英語6分類Validator)の判定結果。</p>
<table>
<tr><th>Segment</th><th>A(現行Production)</th><th>B(Gemini 3.8 Flash-Lite、Trial)</th></tr>
{table_rows}
</table>
</body></html>"""
    with open(f"{OUT_DIR}/player.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[written] {OUT_DIR}/player.html")


if __name__ == "__main__":
    main()
