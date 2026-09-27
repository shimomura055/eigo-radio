# ============================================================
# er022_tts_gemini_3_8_flash_lite_next_trial_01_stage1_assets.py
# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01(Stage 1 A/B試聴artifact組み立て)
# ============================================================
# 性質: Trial補助(API課金なし、読み取り専用+mp3変換+player.html生成のみ)。
# 既存記事artifact(SOURCE_A_DIR)は読み取るだけで一切変更しない。
from __future__ import annotations

import json
import os

import soundfile as sf

SOURCE_A_DIR = "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2"
OUT_DIR = "er022_output/tts_gemini_3_8_flash_lite_next_trial_01/stage1"
SEGMENT_NAME = "tension_reflection"


def wav_to_mp3(src_wav_path: str, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    data, sr = sf.read(src_wav_path)
    sf.write(out_path, data, sr, format="MP3")


def main() -> None:
    a_src = f"{SOURCE_A_DIR}/narration/{SEGMENT_NAME}.wav"
    b_src = f"{OUT_DIR}/narration/{SEGMENT_NAME}.wav"
    a_out = f"{OUT_DIR}/segments_mp3/a/{SEGMENT_NAME}.mp3"
    b_out = f"{OUT_DIR}/segments_mp3/b/{SEGMENT_NAME}.mp3"
    wav_to_mp3(a_src, a_out)
    wav_to_mp3(b_src, b_out)

    result = json.load(open(f"{OUT_DIR}/audit/stage1_result.json", encoding="utf-8"))
    status = result.get("final_status")
    duration_b = result.get("final_duration_seconds")

    html = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<title>TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01: Stage 1 A/B試聴</title>
<style>
body {{ font-family: sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
audio {{ width: 100%; }}
.status-OK {{ color: green; font-weight: bold; }}
.status-STOPPED {{ color: red; font-weight: bold; }}
</style></head>
<body>
<h1>TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01: Stage 1(1 segment)A/B試聴
(Trial、Production非採用)</h1>
<p>対象記事: 「AIが採用を選ぶとき」Standard(A2)版。segment=tension_reflection
(Voice=Aoede、固有名詞"New York City"を含む唯一のsegment)。
A=現行Production(gemini-2.5-pro-preview-tts、Structured Separation prompt、
実測62.25秒)。B=Gemini 3.8 Flash-Lite TTS(gemini-3.8-flash-lite-tts、
speech_metadataによるverbatim transcript方式、style=""[plain TTS、attempt1で
即PASS]、実測{duration_b}秒)。B列のstatusは既存Production ASR検証パイプライン
(英語6分類Validator)の判定結果。</p>
<table>
<tr><th>Segment</th><th>A(現行Production)</th><th>B(Gemini 3.8 Flash-Lite、Trial)</th></tr>
<tr>
  <td>{SEGMENT_NAME}<br><span style="color:#888;font-size:0.8em">Voice: Aoede</span></td>
  <td><audio controls preload="none" src="segments_mp3/a/{SEGMENT_NAME}.mp3"></audio></td>
  <td><audio controls preload="none" src="segments_mp3/b/{SEGMENT_NAME}.mp3"></audio><br>
      <span class="status status-{status}">{status}</span></td>
</tr>
</table>
</body></html>"""
    with open(f"{OUT_DIR}/player.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[written] {OUT_DIR}/player.html")
    print(f"[written] {a_out}")
    print(f"[written] {b_out}")


if __name__ == "__main__":
    main()
