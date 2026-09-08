"""
管理ID: OPEN-121-METHOD-D-FLAG15-REVIEW-ARTIFACT-02
Fable(PM)委任によるSonnet実行。

背景(ユーザー決定 2026-09-08):
OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01
(er011_output/method_d_flag23_review_01/classification_table.json、
23件)のうち、真の重複として証拠・過去試聴で確定済みの8件
(open112_trial13 / open117_trial02_kp の in_one_line系4件+point_two系4件)
はユーザー確認対象から除外。確認対象は「誤flag可能性高14件+判断困難1件
=15件」。

現行の「1回目/2回目」表示だけでは何を比較すればよいか分かりにくい、
というユーザー指摘を受け、UIを改善する:
- 各occurrence(1回目/2回目)について、検知秒・前後1〜2秒の確認範囲
  (開始〜終了秒)・その範囲に対応するscript断片(ローカルfaster-whisper
  word-level timestampから機械抽出、算出できない場合は「位置未特定」と
  明記し推測しない)を明示する。
- 各occurrenceごとに、範囲を切り出した短いclip(新規ファイル、
  clips/配下)の単独再生ボタンを追加する(既存wavは読み取り専用)。
- 完全scriptには、上記2つのfragmentに対応する位置を(difflibによる
  トークン単位のfuzzy matchingで)可能な範囲でハイライトする。

方式Dの閾値変更・自動再生成は一切行わない。API呼び出しなし
(TTS/ASR/LLM有料API不使用)。word-level timestamp抽出には
er008_disfluency_qa_18.transcribe_verbatim()(faster-whisper、ローカル
CPU実行、無料、既存モジュールを無変更のままimport)を使う。

入力(すべて読み取りのみ、一切変更しない):
- er011_output/method_d_flag23_review_01/classification_table.json
  (23件。ここから8件除外し15件を対象にする)
- 各itemの元wavファイル(narration/配下、読み取りのみ)

出力: er011_output/method_d_flag15_review_02/
- classification_table.json (15件、occurrence別の検知秒・確認範囲・
  script断片・clipパスを追加した表)
- player.html (標準フォーマット、Gate 7 (g)(h)(j)(k)(l)準拠)
- clips/*.wav (新規切り出し、既存wavへの書き込みなし)

費用: ¥0(faster-whisperはローカルCPU実行でネットワーク課金なし。
TTS/ASR/LLM有料API呼び出しは一切行っていない)。
"""
from __future__ import annotations

import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_review_player import PLAYER_STANDARD_CSS, abs_file_url  # noqa: E402
import er008_disfluency_qa_18 as dq18  # noqa: E402 (word-level timestamp, local, free)

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE, "er011_output", "method_d_flag23_review_01")
OUT_DIR = os.path.join(BASE, "er011_output", "method_d_flag15_review_02")
CLIPS_DIR = os.path.join(OUT_DIR, "clips")

WINDOW_HALF_SECONDS = 1.5  # occurrenceごとの確認範囲(前後1.5秒)


def esc(s):
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def safe_id(item_id):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", item_id)


def normalize_tok(w):
    return re.sub(r"[.,!?;:\"'…—–-]", "", w.lower()).strip()


def get_words(wav_path):
    """ローカルfaster-whisperでword-level timestampを取得する(無料、既存
    モジュールを無変更のままimport)。失敗した場合はNoneを返す(推測しない)。"""
    try:
        words = dq18.transcribe_verbatim(wav_path)
    except Exception as e:
        print(f"  [warn] transcribe failed for {wav_path}: {e}")
        return None
    out = []
    for w in words:
        out.append({
            "text": w["text"],
            "start": float(w["start"]),
            "end": float(w["end"]),
        })
    return out


def fragment_for_time(words, t, half=WINDOW_HALF_SECONDS):
    """検知時刻tの前後half秒に重なる語をscript断片として抽出する。
    windowに1語も無い場合のみ、段階的に窓を広げる(2.5秒→4.0秒)。
    words自体が取得できていない、またはtがNoneの場合はNoneを返す
    (「位置未特定」として扱う。推測で埋めない)。"""
    if not words or t is None:
        return None
    for w_half in (half, 2.5, 4.0):
        cands = [w for w in words if not (w["end"] < t - w_half or w["start"] > t + w_half)]
        if cands:
            text = "".join(w["text"] for w in cands).strip()
            return {
                "text": text,
                "word_start": round(cands[0]["start"], 2),
                "word_end": round(cands[-1]["end"], 2),
                "window_half_seconds_used": w_half,
                "tokens_norm": [normalize_tok(w["text"]) for w in cands if normalize_tok(w["text"])],
            }
    return None


def highlight_canonical(canonical_text, frag_tokens_norm, mark_class):
    """canonical_text中で、fragの正規化トークン列に最も近い区間をdifflibで
    探し、<mark class="...">で囲んだ(text, matched_span_or_None)を返す。
    厳密な一致でなくても良い(TTSの実発話とcanonicalは表記ゆれがあり得る
    ため)が、最低2語一致しない場合はハイライトしない。"""
    if canonical_text is None or not frag_tokens_norm:
        return canonical_text, None
    tok_spans = [(m.start(), m.end(), m.group()) for m in re.finditer(r"\S+", canonical_text)]
    canon_norm = [normalize_tok(t[2]) for t in tok_spans]
    sm = difflib.SequenceMatcher(None, canon_norm, frag_tokens_norm, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size >= 2]
    if not blocks:
        return None, None
    best = max(blocks, key=lambda b: b.size)
    start_char = tok_spans[best.a][0]
    end_char = tok_spans[best.a + best.size - 1][1]
    highlighted = (
        esc(canonical_text[:start_char])
        + f'<mark class="{mark_class}">'
        + esc(canonical_text[start_char:end_char])
        + "</mark>"
        + esc(canonical_text[end_char:])
    )
    return highlighted, (start_char, end_char)


def merge_two_highlights(canonical_text, span_a, span_b):
    """1回目・2回目それぞれのハイライト区間(文字offset)を、重ならない前提で
    同時にcanonical_text全体へ適用する(esc込みのHTMLを1回で組み立てる)。
    どちらか/両方Noneの場合はハイライトなしのescテキストにする。"""
    if canonical_text is None:
        return '<span class="missing">未取得(canonical本文が確認できず)</span>'
    marks = []
    if span_a:
        marks.append((span_a[0], span_a[1], "mark-a"))
    if span_b:
        marks.append((span_b[0], span_b[1], "mark-b"))
    if not marks:
        return esc(canonical_text)
    marks.sort()
    # 重なっていたら統合して両方のクラスを併記する
    merged = []
    for s, e, cls in marks:
        if merged and s <= merged[-1][1]:
            ps, pe, pcls = merged[-1]
            merged[-1] = (ps, max(pe, e), pcls + " " + cls)
        else:
            merged.append((s, e, cls))
    out = []
    prev = 0
    for s, e, cls in merged:
        out.append(esc(canonical_text[prev:s]))
        out.append(f'<mark class="{cls}">')
        out.append(esc(canonical_text[s:e]))
        out.append("</mark>")
        prev = e
    out.append(esc(canonical_text[prev:]))
    return "".join(out)


def build_clip(wav_path, start_s, end_s, out_path):
    try:
        import soundfile as sf
        data, sr = sf.read(wav_path, always_2d=False)
        dur = len(data) / sr
        s = max(0.0, start_s)
        e = min(dur, end_s)
        if e <= s:
            return None
        region = data[int(s * sr): int(e * sr)]
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        sf.write(out_path, region, sr, subtype="PCM_16")
        return {"start_s": round(s, 2), "end_s": round(e, 2)}
    except Exception as e:
        print(f"  [warn] clip extraction failed for {wav_path}: {e}")
        return None


def build_occurrence(row, label, t, wav_abs_path, words):
    """1回目 or 2回目のoccurrence情報(検知秒・確認範囲・script断片・clip)
    を組み立てる。"""
    occ = {"label": label, "detected_time_s": t}
    if t is None:
        occ["confirm_range"] = None
        occ["fragment"] = None
        occ["clip_path"] = None
        occ["position_status"] = "位置未特定(検知秒データなし)"
        return occ
    range_start = max(0.0, round(t - WINDOW_HALF_SECONDS, 2))
    dur = row.get("duration_seconds")
    range_end = round(t + WINDOW_HALF_SECONDS, 2)
    if dur is not None:
        range_end = min(dur, range_end)
    occ["confirm_range"] = {"start_s": range_start, "end_s": range_end}

    frag = fragment_for_time(words, t)
    if frag is None:
        occ["fragment"] = None
        occ["position_status"] = (
            "位置未特定(ASR word timestamp取得不可、または該当秒付近に語が無し)"
        )
    else:
        occ["fragment"] = frag
        occ["position_status"] = "特定"

    clip_out = os.path.join(
        CLIPS_DIR, f"{safe_id(row['item_id'])}__{label}_{range_start:.2f}s-{range_end:.2f}s.wav"
    )
    clip_info = build_clip(wav_abs_path, range_start, range_end, clip_out)
    if clip_info:
        occ["clip_path"] = os.path.relpath(clip_out, OUT_DIR).replace("\\", "/")
        occ["clip_url"] = abs_file_url(clip_out)
    else:
        occ["clip_path"] = None
        occ["clip_url"] = None
    return occ


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(CLIPS_DIR, exist_ok=True)

    with open(os.path.join(SRC_DIR, "classification_table.json"), encoding="utf-8") as f:
        rows23 = json.load(f)

    excluded = [r for r in rows23 if r["classification"] == "真の重複(証拠あり)"]
    rows15 = [r for r in rows23 if r["classification"] != "真の重複(証拠あり)"]
    assert len(excluded) == 8, f"expected 8 excluded rows, got {len(excluded)}"
    assert len(rows15) == 15, f"expected 15 target rows, got {len(rows15)}"

    out_rows = []
    n_both_located = 0
    n_partial = 0
    n_none = 0
    n_clips = 0

    for row in rows15:
        wav_abs_path = os.path.join(BASE, row["path"])
        print(f"processing: {row['item_id']}")
        words = get_words(wav_abs_path) if os.path.exists(wav_abs_path) else None

        occ_a = build_occurrence(row, "occ1", row.get("flag_time_a"), wav_abs_path, words)
        occ_b = build_occurrence(row, "occ2", row.get("flag_time_b"), wav_abs_path, words)

        located_a = occ_a["position_status"] == "特定"
        located_b = occ_b["position_status"] == "特定"
        if located_a and located_b:
            n_both_located += 1
        elif located_a or located_b:
            n_partial += 1
        else:
            n_none += 1
        n_clips += sum(1 for o in (occ_a, occ_b) if o.get("clip_path"))

        span_a = span_b = None
        highlighted_script = row.get("canonical_text")
        canonical_text = row.get("canonical_text")
        if canonical_text is not None:
            if occ_a.get("fragment"):
                _, span_a = highlight_canonical(canonical_text, occ_a["fragment"]["tokens_norm"], "mark-a")
            if occ_b.get("fragment"):
                _, span_b = highlight_canonical(canonical_text, occ_b["fragment"]["tokens_norm"], "mark-b")
            highlighted_script = merge_two_highlights(canonical_text, span_a, span_b)
        else:
            highlighted_script = None

        out_row = dict(row)  # 元の23件分の証拠フィールドをすべて引き継ぐ
        out_row["wav_abs_url"] = abs_file_url(wav_abs_path)
        out_row["asr_word_timestamps_available"] = words is not None
        out_row["occurrence_1"] = occ_a
        out_row["occurrence_2"] = occ_b
        out_row["highlighted_script_html"] = highlighted_script
        out_rows.append(out_row)

    with open(os.path.join(OUT_DIR, "classification_table.json"), "w", encoding="utf-8") as f:
        json.dump(out_rows, f, ensure_ascii=False, indent=2)

    build_player_html(out_rows, excluded)

    print(
        f"located both: {n_both_located} / partial: {n_partial} / none: {n_none} "
        f"(total {len(out_rows)}), clips written: {n_clips}"
    )
    print("wrote:", os.path.join(OUT_DIR, "classification_table.json"))
    print("wrote:", os.path.join(OUT_DIR, "player.html"))


def build_evidence_html(row):
    parts = []
    if row.get("asr_text"):
        parts.append(f'<b>生成時ASR:</b> {esc(row["asr_text"])}')
    if row.get("asr_verdict"):
        parts.append(f'<b>ASR verdict:</b> {esc(row["asr_verdict"])}')
    if row.get("disfluency_checked"):
        de = row.get("disfluency_evidence") or {}
        parts.append(f'<b>disfluency QA:</b> flagged={de.get("flagged")}, repeats={de.get("repeats")}')
    if row.get("evidence_source"):
        parts.append(f'<small>証拠source: {esc(row["evidence_source"])}</small>')
    if not parts:
        return '<span class="missing">未取得(生成時ASR記録が見つからず)</span>'
    return "<br>".join(parts)


def occ_html(occ, idx, audio_id):
    label_disp = "1回目" if occ["label"] == "occ1" else "2回目"
    t = occ["detected_time_s"]
    if t is None:
        return f'<b>{label_disp}:</b> 検知秒データなし<br><span class="missing">{esc(occ["position_status"])}</span>'
    cr = occ["confirm_range"]
    seek_btn = (
        f'<button class="seek" onclick="seekOwn(\'{audio_id}\', {t})">'
        f"&#9654; {t:.2f}s({label_disp})</button>"
    )
    range_disp = f'確認範囲 {cr["start_s"]:.2f}s〜{cr["end_s"]:.2f}s' if cr else ""
    frag = occ.get("fragment")
    if frag:
        frag_disp = f'<b>断片:</b> "{esc(frag["text"])}"'
    else:
        frag_disp = f'<span class="missing">{esc(occ["position_status"])}</span>'
    clip_html = ""
    if occ.get("clip_path"):
        clip_html = (
            f'<button class="seek" onclick="playClip(this)" '
            f'data-src="{occ["clip_url"]}">&#9654; 該当範囲のみ再生</button>'
        )
    return (
        f"{seek_btn}<br><small>{range_disp}</small><br>{frag_disp}<br>{clip_html}"
    )


ROW_TEMPLATE = """
<tr>
  <td>
    <audio id="{audio_id}" controls preload="none" src="{wav_url}"></audio><br>
    <small>duration={duration}s / run={run}s / lag={lag}s / sim={sim}</small>
  </td>
  <td><b>{group}</b> / {level} / {segment_id}<br>
    <small>voice={voice} / model={model} / instr={instr}</small><br>
    <small>review_lock={review_lock_state}/{review_lock_final}</small>
  </td>
  <td>{occ1_html}<hr>{occ2_html}</td>
  <td class="txt">{script_html}</td>
  <td>{evidence_html}</td>
  <td><b>{classification}</b><br><small>{rationale}</small></td>
  <td>
    <label><input type="radio" name="judge_{idx}" value="dup"> 真の重複</label><br>
    <label><input type="radio" name="judge_{idx}" value="falseflag"> 正常音声への誤flag</label><br>
    <label><input type="radio" name="judge_{idx}" value="unclear"> 判断困難</label>
  </td>
</tr>
"""


def build_player_html(rows, excluded_rows):
    body_rows = []
    for idx, row in enumerate(rows):
        audio_id = f"a{idx}"
        body_rows.append(
            ROW_TEMPLATE.format(
                idx=idx,
                audio_id=audio_id,
                wav_url=row["wav_abs_url"],
                duration=row.get("duration_seconds"),
                run=row.get("best_run_length_seconds"),
                lag=row.get("flag_lag_seconds"),
                sim=row.get("flag_similarity"),
                group=esc(row["group"]),
                level=esc(row["level"]),
                segment_id=esc(row["segment_id"]),
                voice=esc(row.get("voice") or "情報なし(audit記録なし)"),
                model=esc(row.get("model") or "情報なし"),
                instr=esc(row.get("instruction_type") or "情報なし"),
                review_lock_state=esc(row.get("review_lock_state") or "(記録なし)"),
                review_lock_final=esc(row.get("review_lock_final_status") or "(記録なし)"),
                occ1_html=occ_html(row["occurrence_1"], idx, audio_id),
                occ2_html=occ_html(row["occurrence_2"], idx, audio_id),
                script_html=row.get("highlighted_script_html")
                or '<span class="missing">未取得(canonical本文が確認できず)</span>',
                evidence_html=build_evidence_html(row),
                classification=esc(row["classification"]),
                rationale=esc(row["classification_rationale"]),
            )
        )

    excluded_list_html = "".join(
        f"<li><code>{esc(r['item_id'])}</code> — {esc(r['classification_rationale'][:80])}...</li>"
        for r in excluded_rows
    )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>OPEN-121 方式D flag15件 レビュー(部品試聴、完成episodeではない)</title>
<style>
{PLAYER_STANDARD_CSS}
table.timeline th:nth-child(1), table.timeline td:nth-child(1) {{ width: 230px; }}
table.timeline th:nth-child(2), table.timeline td:nth-child(2) {{ width: 190px; }}
table.timeline th:nth-child(3), table.timeline td:nth-child(3) {{ width: 260px; }}
table.timeline th:nth-child(4), table.timeline td:nth-child(4) {{ width: auto; }}
table.timeline th:nth-child(5), table.timeline td:nth-child(5) {{ width: 260px; }}
table.timeline th:nth-child(7), table.timeline td:nth-child(7) {{ width: 150px; }}
table.timeline audio {{ min-width: 360px; width: 100%; }}
mark.mark-a {{ background:#ffe58a; }}
mark.mark-b {{ background:#a6d8ff; }}
mark.mark-a.mark-b {{ background:linear-gradient(90deg,#ffe58a,#a6d8ff); }}
details.excluded {{ margin-top:1.4em; }}
details.excluded summary {{ cursor:pointer; font-weight:bold; }}
</style>
</head>
<body>
<h1>OPEN-121 方式D flag15件 レビュー</h1>
<div class="note">
<b>この2箇所は、本来1回でよい内容が不自然に重複しているか?</b><br>
これは<b>完成episodeの試聴ページではありません</b>。方式D(自己相関ベースの
重複/hallucination検知、Production既定閾値run&ge;0.12秒)でflagされた
23件のうち、真の重複として証拠・過去試聴で確定済みの8件
(open112_trial13 / open117_trial02_kp の in_one_line系・point_two系、
既知バグ再現)はここでは除外し、確認が必要な残り15件
(誤flag可能性高14件+判断困難1件)だけを表示しています
(管理ID: OPEN-121-METHOD-D-FLAG15-REVIEW-ARTIFACT-02。除外8件の一覧は
ページ末尾に折りたたみで記載)。<br>
各行の「1回目/2回目」は、方式Dが自己相関で検知した類似区間の開始秒です。
検知秒付近のscript断片は、ローカルfaster-whisperのword-level timestamp
から機械抽出したものです(算出できなかった場合は推測せず
「位置未特定」と明記しています)。完全script欄の
<mark class="mark-a">黄色</mark>=1回目付近、
<mark class="mark-b">水色</mark>=2回目付近のハイライトも同じ機械抽出
(difflibによる近似マッチ)によるもので、一致語句が2語未満の場合は
ハイライトしていません。方式Dの閾値変更・自動再生成は一切行っていません
(既存wav・JSONは読み取りのみ。新規clipは本ページ専用の
`clips/`配下に切り出したもので、既存ファイルへの上書きはありません)。
判定欄(3択)は選択できますが保存機能はありません(最終判断は
ユーザー自身の記録による)。
</div>

<h2>15件 詳細</h2>
<table class="timeline">
<thead><tr><th>個別音声(全体)</th><th>Segment/voice/review_lock</th>
<th>1回目/2回目(検知秒・確認範囲・断片・該当範囲clip)</th>
<th>完全script(該当箇所ハイライト)</th><th>証拠(ASR/disfluency)</th>
<th>一次分類・根拠</th><th>判定</th></tr></thead>
<tbody>
{"".join(body_rows)}
</tbody>
</table>

<details class="excluded">
<summary>確定済み(確認不要) 8件 — 真の重複として過去試聴で確定済み</summary>
<ul>
{excluded_list_html}
</ul>
</details>

<script>
function seekOwn(audioId, sec) {{
  var a = document.getElementById(audioId);
  if (!a) return;
  a.currentTime = parseFloat(sec);
  a.play();
}}
var clipPlayers = {{}};
function playClip(btn) {{
  var src = btn.getAttribute('data-src');
  if (!clipPlayers[src]) {{
    var a = new Audio(src);
    clipPlayers[src] = a;
  }}
  clipPlayers[src].currentTime = 0;
  clipPlayers[src].play();
}}
</script>
</body>
</html>
"""
    with open(os.path.join(OUT_DIR, "player.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
