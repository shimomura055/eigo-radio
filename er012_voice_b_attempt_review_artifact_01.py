# -*- coding: utf-8 -*-
# 一時生成スクリプト(scratchpad)。
# 管理ID: EDITORIAL-B-FAMILY-PHASE1-VOICE-B-ATTEMPT-REVIEW-ARTIFACT-01
# 目的: er012_output/editorial_b_family_production_phase1_02/b1b の
#       point_two(Voice B / Erinome)3 attempt分の専用試聴ページを生成する。
# 既存wav/JSONは読み取るだけで、一切変更しない。TTS/ASR/LLM呼び出しなし。

import sys
import os
import html
import json

sys.path.insert(0, r"C:\Users\tensh\eigo-radio")
from audio_review_player import (
    PLAYER_STANDARD_CSS,
    AUDIO_MIN_WIDTH_PX,
    abs_file_url,
)

BASE = r"C:\Users\tensh\eigo-radio\er012_output\editorial_b_family_production_phase1_02\b1b"
ATT_DIR = os.path.join(BASE, "narration", "attempts")

with open(os.path.join(BASE, "audit", "tts_generation_results.json"), "r", encoding="utf-8") as f:
    tts_results = json.load(f)

pt2 = tts_results["segments"]["point_two"]
canonical_text = pt2["canonical_text"]
voice = pt2.get("voice", "Erinome")
attempts = pt2["attempts_log"]

assert len(attempts) == 3, f"expected 3 attempts, found {len(attempts)}"

# --- script強調表示(canonical textの "do not need" の2箇所を強調) ---------
def highlight_script(text: str) -> str:
    esc = html.escape(text)
    # canonical_textには "do not need" が2回(1回目は前に "I", 2回目は
    # em dashで挟まれた "—or do not need—")登場する。両方を強調する。
    target = "do not need"
    out = []
    idx = 0
    lower = esc.lower()
    tgt_lower = target.lower()
    while True:
        pos = lower.find(tgt_lower, idx)
        if pos == -1:
            out.append(esc[idx:])
            break
        out.append(esc[idx:pos])
        out.append(f'<mark>{esc[pos:pos+len(target)]}</mark>')
        idx = pos + len(target)
    return "".join(out)

script_html = highlight_script(canonical_text)

rows = []
for att in attempts:
    n = att["attempt"]
    wav_path = os.path.join(ATT_DIR, os.path.basename(att["attempt_audio_path"]))
    wav_exists = os.path.isfile(wav_path)
    audio_html = (
        f'<audio controls preload="none" style="width:100%;min-width:{AUDIO_MIN_WIDTH_PX}px;height:32px;" '
        f'src="{abs_file_url(wav_path)}"></audio>'
        if wav_exists else '<span class="missing">wav未取得</span>'
    )

    qa = att.get("repetition_qa_evidence") or {}
    ngram = qa.get("method_a_ngram", {})
    flagged_matches = ngram.get("flagged_matches", [])
    flag_lines = []
    if flagged_matches:
        for m in flagged_matches:
            flag_lines.append(
                f'語句 "{html.escape(m.get("span_text","").strip())}" が '
                f'{m.get("first_start_s")}s と {m.get("second_start_s")}s の2箇所で検知'
                f'(canonical_repeat_count={m.get("canonical_repeat_count")}, '
                f'gap={m.get("gap_seconds")}s, intentional={m.get("intentional")})'
            )
    else:
        flag_lines.append("method_a_ngramでのflagなし")
    d_long = qa.get("method_d_spectral_long_lag", {})
    if d_long.get("flagged"):
        flag_lines.append(
            f'method_d_spectral_long_lagもflagged=true '
            f'(best_run_length={d_long.get("best_run_length_seconds")}s, '
            f'decision_threshold={d_long.get("decision_threshold_seconds")}s)'
        )
    qa_summary_html = "<br>".join(html.escape(x) if "<mark>" not in x else x for x in [
        l if isinstance(l, str) else str(l) for l in flag_lines
    ])

    asr_text = html.escape(att.get("asr_text", "(なし)"))
    duration = att.get("trim_info", {}).get("trimmed_duration_seconds", "?")
    instruction_type = html.escape(att.get("instruction_type", "?"))

    rows.append(f"""
    <tr>
      <td><b>Attempt {n}</b><br><small>voice={html.escape(voice)}<br>duration={duration}s<br>TTS方式={instruction_type}</small></td>
      <td>{audio_html}</td>
      <td class="txt">{script_html}</td>
      <td class="txt">{qa_summary_html}</td>
      <td class="txt">{asr_text}</td>
      <td class="txt">この2箇所の"do not need"が、著者が意図した反復として自然に聞こえるか、
        それとも不自然なTTS重複(コピペ的な繰り返し)に聞こえるかを確認してください。</td>
    </tr>""")

n_available = sum(1 for att in attempts if os.path.isfile(os.path.join(ATT_DIR, os.path.basename(att["attempt_audio_path"]))))

html_out = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>Voice B (point_two) Attempt Review - EDITORIAL-B-FAMILY-PHASE1-VOICE-B-ATTEMPT-REVIEW-ARTIFACT-01</title>
<style>
{PLAYER_STANDARD_CSS}
table.timeline th:nth-child(1), table.timeline td:nth-child(1) {{ width: 160px; }}
table.timeline th:nth-child(2), table.timeline td:nth-child(2) {{ width: {AUDIO_MIN_WIDTH_PX+40}px; }}
mark {{ background:#ffe08a; padding:0 2px; }}
</style>
</head>
<body>
<h1>Voice B (point_two) Attempt Review</h1>
<p>管理ID: EDITORIAL-B-FAMILY-PHASE1-VOICE-B-ATTEMPT-REVIEW-ARTIFACT-01</p>
<div class="note">
<b>判定目的:</b> B-Family Phase 1(記事theme=editorial_b_family_production_phase1_02、
level=b1b、segment=point_two、voice=Erinome)は、repetition QA
(method_a_ngram)が3 attemptすべてで、著者が意図した反復句
"<mark>do not need</mark> &#8230; <mark>do not need</mark>"
(em dash区切り、canonical textでは
"the people I need&mdash;or do not need&mdash;around me")を
誤って重複としてflagし、Assembly GATE_BLOCKEDとなりました
(record_human_approval()は本ページでは実行していません。判断後に別途実施)。
<br><br>
このページで、以下いずれかをご判断ください(3択):
<ul>
<li><b>自然 = 承認可</b>: 意図した反復として自然に聞こえる</li>
<li><b>不自然な重複</b>: TTSが誤って重複読み上げしたように聞こえる</li>
<li><b>判断困難</b>: 音声だけでは判断できない</li>
</ul>
</div>
<p>掲載attempt数: {n_available} / 3
{'(3本すべて揃っています)' if n_available == 3 else '(一部wav未取得。上記「wav未取得」表示箇所を参照)'}
</p>
<p><small>本ページは3つの独立したTTS attempt(同一segment=point_twoの
再試行)を並べて比較する専用artifactであり、1本化済み完成episode wavの
timeline(Gate 7 (g)のclick-seek)ではない。各行のAttempt順序=試行順、
再生は各attempt個別wavを直接再生する(seekボタンは対象外)。</small></p>
<table class="timeline">
<thead><tr><th>Attempt</th><th>再生</th><th>Script(強調=反復句)</th>
<th>QAがflagした箇所</th><th>ASR transcript</th><th>確認してほしいこと</th></tr></thead>
<tbody>
{"".join(rows)}
</tbody>
</table>
</body>
</html>
"""

out_path = r"C:\Users\tensh\eigo-radio\er012_output\editorial_b_family_production_phase1_02\voice_b_attempt_review.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_out)

print("WROTE:", out_path)
print("n_available:", n_available)
for att in attempts:
    wav_path = os.path.join(ATT_DIR, os.path.basename(att["attempt_audio_path"]))
    print(att["attempt"], os.path.isfile(wav_path), wav_path)
