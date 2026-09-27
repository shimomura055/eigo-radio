# ============================================================
# er022_tts_gemini_3_8_flash_lite_next_trial_01_stage3_assets.py
# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01(Stage 3 A/B試聴artifact組み立て)
# ============================================================
# 性質: Trial補助(API課金なし、読み取り専用+mp3変換+連続再生用結合+
# player.html生成のみ)。既存記事artifact(Production A側)は読み取るだけで
# 一切変更しない。
from __future__ import annotations

import json
import os

import numpy as np
import soundfile as sf

import er022_tts_gemini_3_8_flash_lite_next_trial_01_stage3 as stage3

OUT_DIR = stage3.OUT_DIR
SILENCE_PAD_SECONDS = 0.4


def wav_to_mp3(src_wav_path: str, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    data, sr = sf.read(src_wav_path)
    sf.write(out_path, data, sr, format="MP3")


def _read_mono(path: str) -> tuple[np.ndarray, int]:
    data, sr = sf.read(path)
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data, sr


def build_continuous_track(wav_paths: list[str], out_wav_path: str, out_mp3_path: str) -> float:
    """記事順に並んだwavを、SILENCE_PAD_SECONDS秒の無音を挟んで結合する
    (delegation文Stage3内容5「B側の全segment連続再生」)。既存artifact
    (A側wav)は読み取るだけで変更しない、新規生成物のみ書き出す。"""
    chunks = []
    sr_ref = None
    for p in wav_paths:
        if p is None or not os.path.exists(p):
            continue
        data, sr = _read_mono(p)
        if sr_ref is None:
            sr_ref = sr
        assert sr == sr_ref, f"サンプルレート不一致: {p} ({sr} != {sr_ref})"
        chunks.append(data)
        chunks.append(np.zeros(int(sr_ref * SILENCE_PAD_SECONDS), dtype=data.dtype))
    if not chunks:
        return 0.0
    combined = np.concatenate(chunks[:-1])  # 末尾の無音パディングは除く
    os.makedirs(os.path.dirname(out_wav_path), exist_ok=True)
    sf.write(out_wav_path, combined, sr_ref)
    sf.write(out_mp3_path, combined, sr_ref, format="MP3")
    return round(len(combined) / sr_ref, 3)


def main() -> None:
    result = json.load(open(f"{OUT_DIR}/audit/stage3_result.json", encoding="utf-8"))
    seg_by_id = {s["segment_id"]: s for s in result["segments"]}

    rows = []
    b_wav_paths_in_order = []
    a_wav_paths_in_order = []
    for seg_id in result["article_order"]:
        seg = seg_by_id.get(seg_id, {})
        a_ref = seg.get("a_reference", {})
        a_src = a_ref.get("wav_path")
        b_src = f"{OUT_DIR}/narration/{seg_id}.wav"
        has_b = os.path.exists(b_src) and seg.get("final_status") == "OK"

        a_mp3_rel = None
        if a_src and os.path.exists(a_src):
            a_out = f"{OUT_DIR}/segments_mp3/a/{seg_id}.mp3"
            wav_to_mp3(a_src, a_out)
            a_mp3_rel = f"segments_mp3/a/{seg_id}.mp3"
            a_wav_paths_in_order.append(a_src)

        b_mp3_rel = None
        if has_b:
            b_out = f"{OUT_DIR}/segments_mp3/b/{seg_id}.mp3"
            wav_to_mp3(b_src, b_out)
            b_mp3_rel = f"segments_mp3/b/{seg_id}.mp3"
            b_wav_paths_in_order.append(b_src)
        else:
            b_wav_paths_in_order.append(None)

        rows.append({
            "segment_id": seg_id,
            "role": seg.get("role"),
            "voice": seg.get("voice"),
            "attempt_count": seg.get("attempt_count"),
            "a_duration": a_ref.get("duration_seconds"),
            "a_existing_audio": a_ref.get("existing_audio"),
            "b_duration": seg.get("final_duration_seconds"),
            "status": seg.get("final_status"),
            "a_mp3": a_mp3_rel,
            "b_mp3": b_mp3_rel,
        })
        print(f"[written] a={a_mp3_rel} b={b_mp3_rel}")

    # B側 記事全体連続再生(delegation文Stage3内容5)
    b_full_duration = build_continuous_track(
        b_wav_paths_in_order, f"{OUT_DIR}/full_article_b.wav", f"{OUT_DIR}/full_article_b.mp3")
    # A側(既存Production audio、既存のもののみ結合。full_story_part2は
    # 既存音声が無いためgapが生じる=既存Production側も未完成であることを
    # 反映、無理に埋めない)
    a_full_duration = build_continuous_track(
        a_wav_paths_in_order, f"{OUT_DIR}/full_article_a_existing_only.wav",
        f"{OUT_DIR}/full_article_a_existing_only.mp3")
    print(f"[written] full_article_b.mp3 duration={b_full_duration}s")
    print(f"[written] full_article_a_existing_only.mp3 (existing 11 segments only) duration={a_full_duration}s")

    def row_html(r):
        a_audio = (f'<audio controls preload="none" src="{r["a_mp3"]}"></audio><br>{r["a_duration"]}s'
                   if r["a_mp3"] else '<span class="missing">既存Production音声なし</span>')
        b_audio = (f'<audio controls preload="none" src="{r["b_mp3"]}"></audio><br>{r["b_duration"]}s'
                   if r["b_mp3"] else '<span class="missing">未生成/STOPPED</span>')
        return f"""<tr>
  <td>{r['segment_id']}<br><span style="color:#888;font-size:0.8em">role: {r['role']} / voice: {r['voice']} / attempts: {r['attempt_count']}</span></td>
  <td>{a_audio}</td>
  <td>{b_audio}<br><span class="status status-{r['status']}">{r['status']}</span></td>
</tr>"""

    table_rows = "\n".join(row_html(r) for r in rows)

    html = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<title>TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01: Stage 3(1記事全12segment)A/B試聴</title>
<style>
body {{ font-family: sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
audio {{ width: 100%; }}
.status-OK {{ color: green; font-weight: bold; }}
.status-STOPPED {{ color: red; font-weight: bold; }}
.missing {{ color: #a33; font-style: italic; }}
.full-track {{ margin: 16px 0; padding: 12px; background: #f7f7f7; border: 1px solid #ddd; }}
</style></head>
<body>
<h1>TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01: Stage 3(Family X Hormuz B1B、記事全12segment)
A/B試聴(Trial、Production非採用)</h1>
<p>A=現行Production(gemini-2.5-pro-preview-tts、role別style prefix[Charon系=
B1_PREVIEW_STYLE_PREFIX_CALM、Aoede系=ENGLISH_STYLE_PREFIX素]、既存artifact
そのまま)。B=Gemini 3.8 Flash-Lite TTS(gemini-3.8-flash-lite-tts、
speech_metadataによるverbatim transcript方式、role別最小style
[Full Story=calm steady news narration/Comment・Preview=calm conversational/
Heading=brief and clear/In One Line=concise clear/Topic Intro=brief clear
engaging]、attempt1がこのrole別style、attempt2/3はStage1/2と同じ
fallback style)。B列のstatusは既存Production ASR検証パイプライン
(英語6分類Validator、Tier 1数値等価role gate込み)の判定結果。</p>

<div class="full-track">
<h2>記事全体 連続再生(delegation文Stage3内容5)</h2>
<p>B(Trial、全{len(result['article_order'])}segment、{SILENCE_PAD_SECONDS}秒無音区切り)
duration={b_full_duration}s:</p>
<audio class="full-track" controls preload="none" src="full_article_b.mp3"></audio>
<p>A(現行Production、既存音声がある11segmentのみを同順で結合。
full_story_part2は既存音声が無いためgapとして省略=既存Productionもこの
segmentは未完成であることを反映)duration={a_full_duration}s:</p>
<audio class="full-track" controls preload="none" src="full_article_a_existing_only.mp3"></audio>
</div>

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
