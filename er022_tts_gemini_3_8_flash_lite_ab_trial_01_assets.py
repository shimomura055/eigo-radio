# ============================================================
# er022_tts_gemini_3_8_flash_lite_ab_trial_01_assets.py
# TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01(比較表・試聴artifact組み立て)
# ============================================================
# 性質: Trial補助(API課金なし、読み取り専用集計+mp3変換+player.html
# 生成のみ)。既存記事artifact(SOURCE_A_DIR)は読み取るだけで一切変更
# しない。er022_tts_gemini_3_8_flash_lite_ab_trial_01.pyの実行結果
# (tts_generation_results_b.json/raw_usage_log.jsonl)を集計する。
from __future__ import annotations

import json
import os

import soundfile as sf

import er012_b_voices_3v_a2_user_test_01 as v3

SOURCE_A_DIR = "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2"
OUT_DIR = "er022_output/tts_gemini_3_8_flash_lite_ab_trial_01"
B_DIR = f"{OUT_DIR}/b"
MP3_A_DIR = f"{OUT_DIR}/segments_mp3/a"
MP3_B_DIR = f"{OUT_DIR}/segments_mp3/b"

SEGMENT_ORDER = [
    "topic_intro", "japanese_title", "preview", "comment_1",
    "full_story_part1", "full_story_part2", "comment_2",
    "point_one_heading", "point_one", "point_two_heading", "point_two",
    "point_three_heading", "point_three", "comment_3",
    "tension_reflection", "comment_4", "in_one_line",
]

LABELS = {
    "topic_intro": "Topic intro (Charon, EN)",
    "japanese_title": "Japanese title (Aoede, JA)",
    "preview": "Preview (Aoede, JA)",
    "comment_1": "Comment 1 (Aoede, JA)",
    "full_story_part1": "Hook Part 1 (Aoede, EN, A2 slowdown)",
    "full_story_part2": "Hook Part 2 (Aoede, EN, A2 slowdown)",
    "comment_2": "Comment 2 (Aoede, JA)",
    "point_one_heading": "Voice 1 heading (Aoede, EN, A2 slowdown)",
    "point_one": "Voice 1 body (Algieba, A2 slowdown)",
    "point_two_heading": "Voice 2 heading (Aoede, EN, A2 slowdown)",
    "point_two": "Voice 2 body (Erinome, A2 slowdown)",
    "point_three_heading": "Voice 3 heading (Aoede, EN, A2 slowdown)",
    "point_three": "Voice 3 body (Schedar, A2 slowdown)",
    "comment_3": "Comment 3 (Aoede, JA)",
    "tension_reflection": "Tension reflection (Aoede, EN, A2 slowdown)",
    "comment_4": "Comment 4 (Aoede, JA)",
    "in_one_line": "In one line (Aoede, EN, A2 slowdown)",
}


def wav_to_mp3(src_wav_path: str, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    data, sr = sf.read(src_wav_path)
    sf.write(out_path, data, sr, format="MP3")


def build_mp3_assets() -> dict:
    manifest = {"a": {}, "b": {}}
    for name in SEGMENT_ORDER:
        a_src = f"{SOURCE_A_DIR}/narration/{name}.wav"
        if os.path.exists(a_src):
            a_out = f"{MP3_A_DIR}/{name}.mp3"
            wav_to_mp3(a_src, a_out)
            manifest["a"][name] = a_out
        b_src = f"{B_DIR}/narration/{name}.wav"
        if os.path.exists(b_src):
            b_out = f"{MP3_B_DIR}/{name}.mp3"
            wav_to_mp3(b_src, b_out)
            manifest["b"][name] = b_out
    return manifest


def load_results() -> dict:
    return json.load(open(f"{B_DIR}/audit/tts_generation_results_b.json", encoding="utf-8"))


def load_a_tts_results() -> dict:
    return json.load(open(f"{SOURCE_A_DIR}/audit/tts_generation_results.json", encoding="utf-8"))


def compute_cost_table() -> list:
    """raw_usage_log.jsonlをsegment単位で集計する(実測token/elapsed、
    価格はer005_output/cost_baseline_01/pricing_snapshot.json[既存
    公式SSOT]を使う。gemini-3.8-flash-lite-ttsはこのSSOTに未収録のため、
    近縁モデルgemini-3.1-flash-tts-previewと同一rateを保守的proxyとして
    使い、その旨を明記する[実際のFlash-Lite価格はこれより安い可能性が
    高い])。"""
    pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]
    price = {(p["provider"], p["model"], p["meter"], p.get("tier", "Standard")): p["price"] for p in pricing}
    rows = [json.loads(l) for l in open(f"{B_DIR}/audit/raw_usage_log.jsonl", encoding="utf-8")]
    by_segment: dict = {}
    for r in rows:
        seg = r.get("segment") or "(none)"
        provider, model = r.get("provider"), r.get("model_id")
        it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
        elapsed = r.get("elapsed_seconds") or 0
        if provider == "gemini" and model == "gemini-3.8-flash-lite-tts":
            rate_in = price[("gemini", "gemini-3.1-flash-tts-preview", "input_tokens", "Standard")]
            rate_out = price[("gemini", "gemini-3.1-flash-tts-preview", "output_tokens", "Standard")]
            usd = it / 1e6 * rate_in + ot / 1e6 * rate_out
            kind = "tts_b_proxy_rate"
        elif provider == "openai" and model == "gpt-5.6-luna":
            rate_in = price[("openai", "gpt-5.6-luna", "input_tokens", "Standard")]
            rate_out = price[("openai", "gpt-5.6-luna", "output_tokens", "Standard")]
            usd = it / 1e6 * rate_in + ot / 1e6 * rate_out
            kind = "reading_safety_llm"
        elif provider == "openai_asr" and model == "gpt-4o-mini-transcribe":
            rate_in = price[("openai_asr", "gpt-4o-mini-transcribe", "input_tokens", "Standard")]
            rate_out = price[("openai_asr", "gpt-4o-mini-transcribe", "output_tokens", "Standard")]
            usd = it / 1e6 * rate_in + ot / 1e6 * rate_out
            kind = "asr"
        else:
            usd = 0.0
            kind = "other"
        d = by_segment.setdefault(seg, {"calls": 0, "elapsed_seconds": 0.0, "usd": 0.0, "by_kind": {}})
        d["calls"] += 1
        d["elapsed_seconds"] += elapsed
        d["usd"] += usd
        d["by_kind"][kind] = d["by_kind"].get(kind, 0.0) + usd
    table = []
    for seg in SEGMENT_ORDER:
        d = by_segment.get(seg, {"calls": 0, "elapsed_seconds": 0.0, "usd": 0.0, "by_kind": {}})
        table.append({
            "segment": seg, "calls": d["calls"], "elapsed_seconds": round(d["elapsed_seconds"], 2),
            "usd": round(d["usd"], 4), "jpy_at_160": round(d["usd"] * 160, 2), "by_kind": d["by_kind"],
        })
    return table


def build_player_html(manifest: dict, results: dict) -> str:
    rows = []
    for name in SEGMENT_ORDER:
        seg_result = results["segments"].get(name, {})
        status = seg_result.get("status", "N/A")
        a_path = manifest["a"].get(name)
        b_path = manifest["b"].get(name)
        a_tag = (f'<audio controls preload="none" src="segments_mp3/a/{name}.mp3"></audio>'
                 if a_path else "(no A audio)")
        b_tag = (f'<audio controls preload="none" src="segments_mp3/b/{name}.mp3"></audio>'
                 if b_path else "(no B audio)")
        rows.append(f"""
        <tr>
          <td>{LABELS.get(name, name)}<br><span class="segid">{name}</span></td>
          <td>{a_tag}</td>
          <td>{b_tag}<br><span class="status status-{status}">{status}</span></td>
        </tr>""")
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<title>TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01: segment別A/B試聴</title>
<style>
body {{ font-family: sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
audio {{ width: 100%; }}
.segid {{ color: #888; font-size: 0.8em; }}
.status-OK {{ color: green; font-weight: bold; }}
.status-STOPPED {{ color: red; font-weight: bold; }}
.status-ASR_VALIDATION_UNCERTAIN {{ color: orange; font-weight: bold; }}
</style></head>
<body>
<h1>TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01: segment別A/B試聴(Trial、Production非採用)</h1>
<p>対象記事: 「AIが採用を選ぶとき」Standard(A2)版。A=現行Production
(gemini-2.5-pro-preview-tts / gemini-3.1-flash-tts-preview)。
B=Gemini 3.8 Flash-Lite TTS(gemini-3.8-flash-lite-tts、同一テキスト・
同一Voice・同一instruction、モデルIDのみ差し替え)。B列のstatusは
既存Production ASR検証パイプラインの判定結果(STOPPED=3回試行後も
不一致/異常検知)。</p>
<table>
<tr><th>Segment</th><th>A(現行Production)</th><th>B(Gemini 3.8 Flash-Lite、Trial)</th></tr>
{"".join(rows)}
</table>
</body></html>"""


if __name__ == "__main__":
    manifest = build_mp3_assets()
    results = load_results()
    cost_table = compute_cost_table()
    with open(f"{OUT_DIR}/cost_table.json", "w", encoding="utf-8") as f:
        json.dump(cost_table, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/segments_mp3_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    html = build_player_html(manifest, results)
    with open(f"{OUT_DIR}/player.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("done. mp3 count a/b:", len(manifest["a"]), len(manifest["b"]))
    total_usd = sum(r["usd"] for r in cost_table)
    print("total estimated usd:", round(total_usd, 4), "jpy:", round(total_usd * 160, 2))
