# ============================================================
# er014_output/four_type_observation_01/discovery/build_b1_human_review_player.py
# 管理ID: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY Part A
#
# 目的: Discovery B1(内部ID b1b)のsegment "full_story_part2"について、
# 追加TTS再生成は行わず、既存attempt音声(review_lock_state.jsonに記録
# 済みの最終3attempt)を人間が聞いて内容一致を確認・承認するための
# Human Review用player(HTML)を作る。既存標準Audio Review Player形式
# (audio_review_player.py、Gate 7準拠)を再利用・拡張する(相対パスのみ、
# file:///禁止)。
#
# 本スクリプトはAPIを呼ばない(¥0)。canonical本文(discovery/audio/
# b1b/parts.json の part2)・音声(既存wav)はどちらも変更しない。
# 差分検出は既存Validator/Checkerの新規追加ではなく、本スクリプト内の
# read-only語単位diff(difflib.SequenceMatcher)による表示専用の可視化。
# ============================================================
from __future__ import annotations

import difflib
import json
import os
import re
import sys
from datetime import datetime, timezone

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_DISCOVERY_DIR_ABS = os.path.dirname(os.path.abspath(__file__))
if _DISCOVERY_DIR_ABS not in sys.path:
    sys.path.insert(0, _DISCOVERY_DIR_ABS)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import audio_review_player as arp
import run_discovery_audio_completion as completion_mod  # wav_to_mp3()を再利用

BASE_DIR = "er014_output/four_type_observation_01/discovery"
LOCK_PATH = f"{BASE_DIR}/audio/b1b/audit/review_lock_state.json"
PARTS_PATH = f"{BASE_DIR}/audio/b1b/parts.json"
OUT_HTML_PATH = f"{BASE_DIR}/audio/b1b/human_review_player.html"
OUT_DIFF_JSON_PATH = f"{BASE_DIR}/audio/b1b/human_review_diff.json"
WEB_REVIEW_DIR = f"{BASE_DIR}/audio/b1b/web/review"
SEGMENT_ID = "full_story_part2"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def tokenize(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def char_offset_of_token(tokens: list[str], idx: int) -> int:
    """tokensを単一スペースで再結合したと仮定した場合の、idx番目の
    token開始位置(文字数)。概算用(元の実際の空白/改行幅とは厳密には
    一致しない、difflib.SequenceMatcher.get_opcodes()のtoken indexを
    そのまま使うための近似)。"""
    return sum(len(t) + 1 for t in tokens[:idx])


def approx_text_len(tokens: list[str]) -> int:
    return sum(len(t) + 1 for t in tokens)


def html_escape(s: str) -> str:
    import html as html_mod
    return html_mod.escape(s)


def compute_word_diff(canonical_text: str, asr_text: str) -> list[dict]:
    canon_tokens = tokenize(canonical_text)
    asr_tokens = tokenize(asr_text)
    sm = difflib.SequenceMatcher(None, canon_tokens, asr_tokens, autojunk=False)
    diffs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        diffs.append({
            "tag": tag,
            "canonical_phrase": " ".join(canon_tokens[i1:i2]),
            "asr_phrase": " ".join(asr_tokens[j1:j2]),
            "canonical_token_range": [i1, i2],
            "asr_token_range": [j1, j2],
        })
    return diffs


def build_highlighted_html(tokens: list[str], ranges: list[tuple], css_class: str) -> str:
    """tokensを単一スペースで再結合しつつ、ranges内のtoken区間を
    <mark class=css_class>で囲んでハイライトする。"""
    parts = []
    covered = [False] * len(tokens)
    for (a, b) in ranges:
        for i in range(a, b):
            if 0 <= i < len(covered):
                covered[i] = True
    i = 0
    n = len(tokens)
    while i < n:
        if covered[i]:
            j = i
            while j < n and covered[j]:
                j += 1
            parts.append(f'<mark class="{css_class}">' + html_escape(" ".join(tokens[i:j])) + "</mark>")
            i = j
        else:
            parts.append(html_escape(tokens[i]))
            i += 1
    return " ".join(parts)


def main() -> None:
    lock_doc = load_json(LOCK_PATH)
    seg = lock_doc[SEGMENT_ID]
    parts_doc = load_json(PARTS_PATH)
    canonical_text = parts_doc["part2"]

    attempts = seg["last_attempts_log"]
    os.makedirs(WEB_REVIEW_DIR, exist_ok=True)

    attempt_records = []
    for a in attempts:
        n = a["attempt"]
        wav_path = a["attempt_audio_path"]
        duration = a["trim_info"]["raw_duration_seconds"]
        asr_text = a["asr_text"]
        mp3_name = f"{SEGMENT_ID}_attempt{n}.mp3"
        mp3_path = f"{WEB_REVIEW_DIR}/{mp3_name}"
        completion_mod.wav_to_mp3(wav_path, mp3_path)

        diffs = compute_word_diff(canonical_text, asr_text)
        canon_tokens = tokenize(canonical_text)
        asr_tokens = tokenize(asr_text)
        total_asr_len = approx_text_len(asr_tokens)

        diff_entries = []
        for d in diffs:
            j1, j2 = d["asr_token_range"]
            char_off = char_offset_of_token(asr_tokens, j1)
            ratio = (char_off / total_asr_len) if total_asr_len else 0.0
            est_seek = round(ratio * duration, 1)
            diff_entries.append({
                **d,
                "estimated_seek_seconds": est_seek,
                "estimated_seek_note": "概算(attempt音声duration x asr_text内の文字位置比、実測タイムスタンプではない)",
            })

        canonical_ranges = [tuple(d["canonical_token_range"]) for d in diffs]
        asr_ranges = [tuple(d["asr_token_range"]) for d in diffs]
        canonical_html = build_highlighted_html(canon_tokens, canonical_ranges, "diff-canon")
        asr_html = build_highlighted_html(asr_tokens, asr_ranges, "diff-asr")

        rel_mp3 = os.path.relpath(mp3_path, os.path.dirname(OUT_HTML_PATH)).replace("\\", "/")

        attempt_records.append({
            "attempt": n,
            "audio_classification": a["audio_classification"],
            "duration_seconds": duration,
            "wav_path": wav_path,
            "mp3_relative_path": rel_mp3,
            "asr_text": asr_text,
            "diff_count": len(diff_entries),
            "diffs": diff_entries,
            "canonical_html": canonical_html,
            "asr_html": asr_html,
        })

    diff_json_doc = {
        "segment_id": SEGMENT_ID,
        "level_display_name": "B1",
        "level_internal_id_note": "B1Bは内部IDとしてのみ注記(ユーザー向け表示名は「B1」)",
        "lock_state": seg.get("state"),
        "final_status": seg.get("final_status"),
        "reason": seg.get("reason"),
        "canonical_text": canonical_text,
        "canonical_text_sha256": seg.get("canonical_text_sha256"),
        "attempts": attempt_records,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "build_b1_human_review_player.py",
        "api_cost_jpy": 0.0,
        "note": "音声・canonical本文は変更していない。差分はattempt音声のASR書き起こし(review_lock_state.json"
                "に既存記録)とcanonical本文の語単位diff(difflib.SequenceMatcher、read-only可視化)。",
    }
    save_json(OUT_DIFF_JSON_PATH, diff_json_doc)

    default_attempt = attempt_records[-1]["attempt"]  # 最終(最も新しい)attemptを既定表示

    # ---- HTML組み立て(標準Audio Review Player CSSを再利用・拡張) ----
    extra_css = """
.diff-canon { background:#ffe3e3; text-decoration: line-through; }
.diff-asr { background:#fff3b0; }
table.diffs { border-collapse: collapse; width:100%; margin:8px 0 18px 0; font-size:0.88em; }
table.diffs th, table.diffs td { border:1px solid #ccc; padding:5px 7px; vertical-align:top; text-align:left; }
table.diffs th { background:#f0f0f0; }
.attempt-block { display:none; border:1px solid #ccc; padding:10px 14px; margin:8px 0 20px 0; }
.attempt-block.active { display:block; }
.attempt-tabs button { padding:6px 12px; margin-right:6px; cursor:pointer; }
.attempt-tabs button.active-tab { background:#333; color:#fff; }
.script-box { white-space:pre-wrap; border:1px solid #ddd; padding:10px; background:#fafafa; margin:8px 0; }
""".strip()

    tab_buttons = []
    attempt_blocks = []
    for rec in attempt_records:
        n = rec["attempt"]
        active = " active" if n == default_attempt else ""
        active_tab = " active-tab" if n == default_attempt else ""
        tab_buttons.append(
            f'<button class="attempt-tab{active_tab}" data-attempt="{n}">'
            f'Attempt {n}({rec["audio_classification"]}, diff={rec["diff_count"]})</button>'
        )
        diff_rows = "".join(
            f'<tr><td>{d["tag"]}</td>'
            f'<td>{html_escape(d["canonical_phrase"])}</td>'
            f'<td>{html_escape(d["asr_phrase"])}</td>'
            f'<td>約{d["estimated_seek_seconds"]}秒付近(概算)</td></tr>'
            for d in rec["diffs"]
        ) or '<tr><td colspan="4">差分なし</td></tr>'

        audio_html = arp.render_single_audio_html(rec["mp3_relative_path"])

        attempt_blocks.append(f'''
<div class="attempt-block{active}" id="attempt-block-{n}">
  <h3>Attempt {n}(音声分類: {html_escape(rec["audio_classification"])}, duration={rec["duration_seconds"]}秒)</h3>
  <p><b>(5) 個別segment再生</b>{" (既定表示)" if n == default_attempt else ""}</p>
  {audio_html}
  <p><b>(2) ASR transcript(差分ハイライト、黄色=canonicalとの差分箇所)</b></p>
  <div class="script-box">{rec["asr_html"]}</div>
  <p><b>(3)(4) 差分箇所・推定seek位置(概算)</b></p>
  <table class="diffs">
    <thead><tr><th>種別</th><th>canonical側</th><th>ASR側</th><th>推定seek位置</th></tr></thead>
    <tbody>{diff_rows}</tbody>
  </table>
</div>''')

    canonical_ref_html = html_escape(canonical_text).replace("\n", "<br>")

    js = """
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".attempt-tab").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var n = btn.getAttribute("data-attempt");
      document.querySelectorAll(".attempt-block").forEach(function (b) { b.classList.remove("active"); });
      document.querySelectorAll(".attempt-tab").forEach(function (b) { b.classList.remove("active-tab"); });
      document.getElementById("attempt-block-" + n).classList.add("active");
      btn.classList.add("active-tab");
    });
  });
});
""".strip()

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>Discovery B1 Human Review Player - full_story_part2</title>
<style>
{arp.PLAYER_STANDARD_CSS}
{extra_css}
</style>
</head>
<body>
<h1>Discovery B1(内部ID: B1B) Human Review Player - segment "full_story_part2"</h1>
<div class="note">
このplayerはB1(内部ID b1b)のsegment "full_story_part2"について、追加TTS再生成を行わず、
既存の3attempt音声を人間が聞いて内容一致を確認・承認するためのものです。音声・canonical本文は
変更していません。lock状態: <b>{html_escape(str(seg.get("state")))}</b>({html_escape(str(seg.get("final_status")))})。
理由: {html_escape(str(seg.get("reason")))}
</div>

<h2>(1) Canonical script(確定本文、2文分割版該当部)</h2>
<div class="script-box">{canonical_ref_html}</div>

<h2>Attempt選択</h2>
<div class="attempt-tabs">{"".join(tab_buttons)}</div>
<p><small>既定表示は最終(最も新しい)Attempt {default_attempt}です。他のAttemptもボタンで選択できます。</small></p>

{"".join(attempt_blocks)}

<script>
{js}
</script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUT_HTML_PATH), exist_ok=True)
    with open(OUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[B1-HUMAN-REVIEW] player生成完了: {OUT_HTML_PATH}")
    print(f"[B1-HUMAN-REVIEW] diff JSON: {OUT_DIFF_JSON_PATH}")
    for rec in attempt_records:
        print(f"  attempt{rec['attempt']}: mp3={rec['mp3_relative_path']} diff_count={rec['diff_count']}")


if __name__ == "__main__":
    main()
