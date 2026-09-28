# ============================================================
# er042_key_phrase_advanced_english_explanation_audio_style_trial_03_page_01.py
# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03: 試聴ページ
# 生成(wav→mp3変換[lameenc、既存precedent er040_..._page_01.pyと同じ
# 判断枠組み、ffmpeg不要]+index.html)。GitHub Pages配布専用
# (user_test/kp_advanced_explanation_audio_trial_03/)。Production側は
# 一切変更しない(読み取りのみ)。
# ============================================================
from __future__ import annotations

import html
import json
import os
import wave

try:
    import lameenc
    _HAS_LAMEENC = True
except ImportError:
    _HAS_LAMEENC = False

OUT_DIR = "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz"
PAGE_DIR = "user_test/kp_advanced_explanation_audio_trial_03"
BEFORE_STYLE = "clear, precise, explanatory"
AFTER_STYLE = "clear, precise, unhurried"


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


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_rows() -> list[dict]:
    reused = load_json(os.path.join(OUT_DIR, "reused_audio_summary.json"))["reused"]
    after = load_json(os.path.join(OUT_DIR, "after_audio_summary.json"))["generated_after_explanation_audio"]

    phrase_by_rank = {r["rank"]: r for r in reused if r["label"] == "phrase_en"}
    before_by_rank = {r["rank"]: r for r in reused if r["label"] == "before_explanation_en"}
    after_by_rank = {a["rank"]: a for a in after}

    os.makedirs(PAGE_DIR, exist_ok=True)
    rows = []
    for rank in sorted(phrase_by_rank):
        phrase_entry = phrase_by_rank[rank]
        before_entry = before_by_rank[rank]
        after_entry = after_by_rank[rank]
        phrase = phrase_entry["phrase"]

        phrase_mp3 = f"kp{rank}_phrase_en.mp3"
        before_mp3 = f"kp{rank}_before_en.mp3"
        after_mp3 = f"kp{rank}_after_en.mp3"
        phrase_ok = wav_to_mp3(phrase_entry["dst"], os.path.join(PAGE_DIR, phrase_mp3))
        before_ok = wav_to_mp3(before_entry["dst"], os.path.join(PAGE_DIR, before_mp3))
        after_wav = os.path.join(OUT_DIR, "audio", f"kp{rank}_after_en.wav")
        after_ok = wav_to_mp3(after_wav, os.path.join(PAGE_DIR, after_mp3))

        rows.append({
            "rank": rank,
            "phrase": phrase,
            "explanation_text": before_entry["text"],
            "phrase_mp3": phrase_mp3 if phrase_ok else None,
            "before_mp3": before_mp3 if before_ok else None,
            "after_mp3": after_mp3 if after_ok else None,
            "before_style": before_entry.get("style_prefix_used"),
            "after_style": after_entry.get("style_prefix_used"),
            "before_duration": before_entry.get("duration_seconds"),
            "after_duration": after_entry.get("duration_seconds"),
            "before_asr_text": before_entry.get("asr_text"),
            "after_asr_text": after_entry.get("asr_text"),
            "before_asr_verified": before_entry.get("asr_verified"),
            "after_asr_verified": after_entry.get("asr_verified"),
            "after_retry_count": after_entry.get("retry_count"),
        })
    return rows


def _e(v) -> str:
    return html.escape("" if v is None else str(v))


def audio_tag(mp3_name: str | None) -> str:
    if not mp3_name:
        return "(mp3変換不可、wavのまま未配布)"
    return (f'<audio controls preload="none" style="width:220px">'
            f'<source src="{_e(mp3_name)}" type="audio/mpeg"></audio>')


def build_html(rows: list[dict]) -> str:
    parts = []
    parts.append("<!DOCTYPE html>\n<html lang=\"ja\">\n<head>\n<meta charset=\"utf-8\">\n")
    parts.append("<title>KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03 試聴・確認ページ</title>\n")
    parts.append("<style>\n"
                  "body { font-family: sans-serif; max-width: 1000px; margin: 20px auto; padding: 0 12px; }\n"
                  "h1 { border-bottom: 3px solid #333; padding-bottom: 8px; }\n"
                  "h2 { border-bottom: 2px solid #999; padding-bottom: 4px; margin-top: 40px; "
                  "background:#f5f5f5; padding:6px; }\n"
                  "table { border-collapse: collapse; width: 100%; margin-bottom: 10px; font-size: 13px; }\n"
                  "table th, table td { border: 1px solid #ccc; padding: 6px 8px; vertical-align: top; "
                  "text-align:left; }\n"
                  "table th { background: #eef; }\n"
                  ".style-box { font-family: monospace; background:#f0f0f0; padding:2px 6px; }\n"
                  ".note { background: #fff3e0; border: 1px solid #ef6c00; padding: 10px; margin: 14px 0; }\n"
                  "</style>\n</head>\n<body>\n")
    parts.append("<h1>KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03</h1>\n")
    parts.append(
        "<p>管理ID: KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03"
        "(Trial、音声Styleのみ比較、Production未配線)。前提: Advanced Key Phrase英語解説の"
        "text仕様はユーザーが正式採用済み(<code>APPROVED_FOR_PRODUCTION</code>、"
        "KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02のB候補5件、Production wiringは未実施)。"
        "Hormuzの既存5 Key Phrase・既存英語解説文をそのまま使用(再生成・再選定なし)。</p>\n")
    parts.append(
        "<p>比較: 同じ英語解説文に対し、<b>Before</b> = "
        f"<span class=\"style-box\">{_e(BEFORE_STYLE)}</span> と "
        "<b>After</b> = "
        f"<span class=\"style-box\">{_e(AFTER_STYLE)}</span> のStyleで音声化した。"
        "Before音声は KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02 (er041) が実際に "
        f"<span class=\"style-box\">{_e(BEFORE_STYLE)}</span> で生成した音声をそのまま再利用"
        "(新規TTS callなし)、After音声は本Trialで新規5 call生成した。"
        "Phrase EN音声(Phrase単体の発音)もHormuz既存artifactの再利用(新規生成なし)。</p>\n")
    parts.append(
        "<div class=\"note\">本Trialの目的は音声Style比較のみです。Statusは"
        "<code>USER_DECISION_REQUIRED</code>(ユーザー試聴後に判断)。"
        "Key Phrase選定ロジック・DB Hybrid・Production Master Audio Storeは無変更。</div>\n")

    for row in rows:
        parts.append(f"<h2>#{row['rank']}: {_e(row['phrase'])}</h2>\n")
        parts.append("<table>\n")
        parts.append("<tr><th style=\"width:18%\"></th><th>内容</th><th style=\"width:26%\">実際に渡したStyle Prompt全文</th></tr>\n")
        parts.append(
            f"<tr><td>Phrase(共通)</td><td><b>{_e(row['phrase'])}</b> {audio_tag(row['phrase_mp3'])}</td>"
            "<td>(Phrase音声はHormuz既存再利用、本TrialのStyle比較対象外)</td></tr>\n")
        parts.append(
            f"<tr><td>英語解説text(共通)</td><td colspan=\"2\">{_e(row['explanation_text'])}</td></tr>\n")
        parts.append(
            "<tr><td>Before音声<br>(reuse, er041)</td>"
            f"<td>{audio_tag(row['before_mp3'])}<br>"
            f"duration={_e(row['before_duration'])}s / asr_verified={_e(row['before_asr_verified'])}<br>"
            f"ASR text: {_e(row['before_asr_text'])}</td>"
            f"<td><span class=\"style-box\">{_e(row['before_style'])}</span></td></tr>\n")
        parts.append(
            "<tr><td>After音声<br>(新規生成)</td>"
            f"<td>{audio_tag(row['after_mp3'])}<br>"
            f"duration={_e(row['after_duration'])}s / asr_verified={_e(row['after_asr_verified'])} / "
            f"retry_count={_e(row['after_retry_count'])}<br>"
            f"ASR text: {_e(row['after_asr_text'])}</td>"
            f"<td><span class=\"style-box\">{_e(row['after_style'])}</span></td></tr>\n")
        parts.append("</table>\n")

    parts.append("</body>\n</html>\n")
    return "".join(parts)


def main() -> None:
    rows = build_rows()
    html_text = build_html(rows)
    os.makedirs(PAGE_DIR, exist_ok=True)
    with open(os.path.join(PAGE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_text)
    with open(os.path.join(PAGE_DIR, "page_data.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"[OK] wrote {PAGE_DIR}/index.html (lameenc available={_HAS_LAMEENC}, rows={len(rows)})")


if __name__ == "__main__":
    main()
