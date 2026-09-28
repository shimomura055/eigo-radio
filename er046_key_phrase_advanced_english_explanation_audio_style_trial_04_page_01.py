# ============================================================
# er046_key_phrase_advanced_english_explanation_audio_style_trial_04_page_01.py
# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04: 試聴ページ
# 生成(wav→mp3変換[lameenc、既存precedent er042_..._page_01.pyと同じ
# 判断枠組み、ffmpeg不要]+index.html)。GitHub Pages配布専用
# (user_test/kp_advanced_explanation_audio_trial_04/)。Production側は
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

OUT_DIR = "er046_output/key_phrase_advanced_english_explanation_audio_style_trial_04/hormuz"
PAGE_DIR = "user_test/kp_advanced_explanation_audio_trial_04"
BEFORE_STYLE = "clear, precise, explanatory"
REFERENCE_AFTER_STYLE = "clear, precise, unhurried"
VARIANT_STYLES = {
    "A": "clear, precise, at a slightly relaxed pace",
    "B": "clear, precise, at a measured pace, without dragging",
    "C": "clear, precise, carefully paced for understanding, without slowing down",
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


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def word_count(text: str) -> int:
    return len([w for w in text.split() if w.strip()])


def build_rows() -> list[dict]:
    reused = load_json(os.path.join(OUT_DIR, "reused_audio_summary.json"))["reused"]
    variant = load_json(os.path.join(OUT_DIR, "variant_audio_summary.json"))["generated_variant_audio"]

    phrase_by_rank = {r["rank"]: r for r in reused if r["label"] == "phrase_en"}
    before_by_rank = {r["rank"]: r for r in reused if r["label"] == "before_explanation_en"}
    refafter_by_rank = {r["rank"]: r for r in reused if r["label"] == "reference_after_explanation_en"}
    variant_by_rank_label: dict[int, dict[str, dict]] = {}
    for item in variant:
        variant_by_rank_label.setdefault(item["rank"], {})[item["variant_label"]] = item

    os.makedirs(PAGE_DIR, exist_ok=True)
    rows = []
    for rank in sorted(phrase_by_rank):
        phrase_entry = phrase_by_rank[rank]
        before_entry = before_by_rank[rank]
        refafter_entry = refafter_by_rank[rank]
        variants = variant_by_rank_label.get(rank, {})
        phrase = phrase_entry["phrase"]
        explanation_text = before_entry["text"]
        wc = word_count(explanation_text)

        phrase_mp3 = f"kp{rank}_phrase_en.mp3"
        before_mp3 = f"kp{rank}_before_en.mp3"
        refafter_mp3 = f"kp{rank}_reference_after_en.mp3"
        phrase_ok = wav_to_mp3(phrase_entry["dst"], os.path.join(PAGE_DIR, phrase_mp3))
        before_ok = wav_to_mp3(before_entry["dst"], os.path.join(PAGE_DIR, before_mp3))
        refafter_ok = wav_to_mp3(refafter_entry["dst"], os.path.join(PAGE_DIR, refafter_mp3))

        variant_data = {}
        for label in ("A", "B", "C"):
            item = variants.get(label)
            if not item:
                variant_data[label] = None
                continue
            wav_path = item["path"]
            mp3_name = f"kp{rank}_variant_{label}_en.mp3"
            ok = wav_to_mp3(wav_path, os.path.join(PAGE_DIR, mp3_name))
            duration = item.get("duration_seconds")
            variant_data[label] = {
                "mp3": mp3_name if ok else None,
                "style": item.get("style_prefix_used"),
                "duration": duration,
                "asr_text": item.get("asr_text"),
                "asr_verified": item.get("asr_verified"),
                "retry_count": item.get("retry_count"),
                "status": item.get("status"),
                "wps": round(wc / duration, 2) if duration else None,
            }

        before_duration = before_entry.get("duration_seconds")
        refafter_duration = refafter_entry.get("duration_seconds")
        rows.append({
            "rank": rank,
            "phrase": phrase,
            "explanation_text": explanation_text,
            "word_count": wc,
            "phrase_mp3": phrase_mp3 if phrase_ok else None,
            "before_mp3": before_mp3 if before_ok else None,
            "reference_after_mp3": refafter_mp3 if refafter_ok else None,
            "before_style": before_entry.get("style_prefix_used"),
            "reference_after_style": refafter_entry.get("style_prefix_used"),
            "before_duration": before_duration,
            "reference_after_duration": refafter_duration,
            "before_wps": round(wc / before_duration, 2) if before_duration else None,
            "reference_after_wps": round(wc / refafter_duration, 2) if refafter_duration else None,
            "before_asr_text": before_entry.get("asr_text"),
            "reference_after_asr_text": refafter_entry.get("asr_text"),
            "before_asr_verified": before_entry.get("asr_verified"),
            "reference_after_asr_verified": refafter_entry.get("asr_verified"),
            "variants": variant_data,
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
    parts.append("<title>KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04 試聴・確認ページ</title>\n")
    parts.append("<style>\n"
                  "body { font-family: sans-serif; max-width: 1100px; margin: 20px auto; padding: 0 12px; }\n"
                  "h1 { border-bottom: 3px solid #333; padding-bottom: 8px; }\n"
                  "h2 { border-bottom: 2px solid #999; padding-bottom: 4px; margin-top: 40px; "
                  "background:#f5f5f5; padding:6px; }\n"
                  "table { border-collapse: collapse; width: 100%; margin-bottom: 10px; font-size: 13px; }\n"
                  "table th, table td { border: 1px solid #ccc; padding: 6px 8px; vertical-align: top; "
                  "text-align:left; }\n"
                  "table th { background: #eef; }\n"
                  ".style-box { font-family: monospace; background:#f0f0f0; padding:2px 6px; }\n"
                  ".note { background: #fff3e0; border: 1px solid #ef6c00; padding: 10px; margin: 14px 0; }\n"
                  ".ref { color: #888; }\n"
                  "</style>\n</head>\n<body>\n")
    parts.append("<h1>KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04</h1>\n")
    parts.append(
        "<p>管理ID: KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04"
        "(Trial、音声Styleのみ比較、Production未配線)。前提: Advanced Key Phrase英語解説の"
        "text仕様はユーザーが正式採用済み(<code>APPROVED_FOR_PRODUCTION</code>、"
        "KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02のB候補5件、Production wiringは未実施)。"
        "Hormuzの既存5 Key Phrase・既存英語解説文をそのまま使用(再生成・再選定なし)。</p>\n")
    parts.append(
        "<p><b>経緯</b>: TRIAL-03で Before = "
        f"<span class=\"style-box\">{_e(BEFORE_STYLE)}</span> と After = "
        f"<span class=\"style-box\">{_e(REFERENCE_AFTER_STYLE)}</span> を比較したが、"
        "ユーザー判断により After(unhurried)は<b>遅すぎた</b>(不採用)。本Trialは "
        "Before と unhurried の<b>中間の自然な速度感</b>を3案(A/B/C)で新規に探索する。"
        "Before・Reference After(参考、不採用)・Phrase EN音声はTRIAL-03の既存音声をそのまま"
        "再利用(新規TTS callなし)。A/B/Cのみ本Trialで新規15 call生成した。</p>\n")
    parts.append(
        "<div class=\"note\">本Trialの目的は音声Style比較のみです。Statusは"
        "<code>USER_DECISION_REQUIRED</code>(ユーザー試聴後に判断)。"
        "Key Phrase選定ロジック・DB Hybrid・Production Master Audio Storeは無変更。"
        "Reference After(unhurried)は<b>不採用</b>だが速度感の参考として掲載している。</div>\n")

    # duration比較表
    parts.append("<h2>duration比較表(速度感の客観指標: words per second)</h2>\n")
    parts.append("<table>\n<tr><th>#</th><th>Phrase</th><th>語数</th>"
                  "<th>Before<br>(explanatory)</th><th>A</th><th>B</th><th>C</th>"
                  "<th>Reference After<br>(unhurried, 不採用)</th></tr>\n")
    for row in rows:
        def cell(duration, wps):
            if duration is None:
                return "-"
            return f"{_e(duration)}s<br>({_e(wps)} wps)"
        a = row["variants"].get("A") or {}
        b = row["variants"].get("B") or {}
        c = row["variants"].get("C") or {}
        parts.append(
            f"<tr><td>{row['rank']}</td><td>{_e(row['phrase'])}</td><td>{row['word_count']}</td>"
            f"<td>{cell(row['before_duration'], row['before_wps'])}</td>"
            f"<td>{cell(a.get('duration'), a.get('wps'))}</td>"
            f"<td>{cell(b.get('duration'), b.get('wps'))}</td>"
            f"<td>{cell(c.get('duration'), c.get('wps'))}</td>"
            f"<td class=\"ref\">{cell(row['reference_after_duration'], row['reference_after_wps'])}</td></tr>\n")
    parts.append("</table>\n")
    parts.append("<p style=\"font-size:12px;color:#666\">wps = words per second"
                  "(語数 ÷ duration秒)。数値が小さいほどゆっくり話している。</p>\n")

    for row in rows:
        parts.append(f"<h2>#{row['rank']}: {_e(row['phrase'])}</h2>\n")
        parts.append("<table>\n")
        parts.append("<tr><th style=\"width:16%\"></th><th>内容</th><th style=\"width:28%\">実際に渡したStyle Prompt全文</th></tr>\n")
        parts.append(
            f"<tr><td>Phrase(共通)</td><td><b>{_e(row['phrase'])}</b> {audio_tag(row['phrase_mp3'])}</td>"
            "<td>(Phrase音声はTRIAL-03既存再利用、本TrialのStyle比較対象外)</td></tr>\n")
        parts.append(
            f"<tr><td>英語解説text(共通)</td><td colspan=\"2\">{_e(row['explanation_text'])}"
            f"(語数={row['word_count']})</td></tr>\n")
        parts.append(
            "<tr><td>Before音声<br>(参考、reuse)</td>"
            f"<td>{audio_tag(row['before_mp3'])}<br>"
            f"duration={_e(row['before_duration'])}s ({_e(row['before_wps'])} wps) / "
            f"asr_verified={_e(row['before_asr_verified'])}<br>"
            f"ASR text: {_e(row['before_asr_text'])}</td>"
            f"<td><span class=\"style-box\">{_e(row['before_style'])}</span></td></tr>\n")
        for label in ("A", "B", "C"):
            v = row["variants"].get(label)
            if not v:
                parts.append(f"<tr><td>Variant {label}<br>(新規生成)</td>"
                              "<td colspan=\"2\">(未生成、budget上限等でskipされた可能性)</td></tr>\n")
                continue
            parts.append(
                f"<tr><td>Variant {label}<br>(新規生成)</td>"
                f"<td>{audio_tag(v['mp3'])}<br>"
                f"duration={_e(v['duration'])}s ({_e(v['wps'])} wps) / "
                f"asr_verified={_e(v['asr_verified'])} / retry_count={_e(v['retry_count'])}<br>"
                f"ASR text: {_e(v['asr_text'])}</td>"
                f"<td><span class=\"style-box\">{_e(v['style'])}</span></td></tr>\n")
        parts.append(
            "<tr><td>Reference After音声<br>(参考、不採用、reuse)</td>"
            f"<td>{audio_tag(row['reference_after_mp3'])}<br>"
            f"duration={_e(row['reference_after_duration'])}s ({_e(row['reference_after_wps'])} wps) / "
            f"asr_verified={_e(row['reference_after_asr_verified'])}<br>"
            f"ASR text: {_e(row['reference_after_asr_text'])}</td>"
            f"<td><span class=\"style-box\">{_e(row['reference_after_style'])}</span></td></tr>\n")
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
