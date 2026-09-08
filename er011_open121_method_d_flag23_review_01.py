"""
管理ID: OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01
Fable(PM)委任によるSonnet実行。

背景: OPEN-121既存音声sweep(OPEN-121-EXISTING-AUDIO-SWEEP-REVIEW-AND-CLIPS-02,
commit 11f68bc)で、方式D Production既定閾値(run>=0.12秒)により既存PASS音声
517件中23件がflagされている。ユーザー方針により、閾値変更・自動再生成は
一切行わず、23件を実際に試聴確認するための軽量player(標準フォーマット)を
作成する。本スクリプトはその一次抽出・一次分類(機械的、証拠ベース)・
player.html生成を行う。

入力(読み取りのみ、一切変更しない):
- er011_output/open121_existing_audio_dprime_sweep_01/results/
  production_params_reclassification_02.json (main_rows)
- er011_output/open121_existing_audio_dprime_sweep_01/inventory.json
- er011_output/open121_existing_audio_dprime_sweep_01/results/method_d.json
- 各記事の tts_generation_results.json / new_segments_result.json
  (生成時ASR検証結果・disfluency QA結果を一次証拠として使用)

出力: er011_output/method_d_flag23_review_01/
- classification_table.json (23件の一次分類・根拠・証拠を機械抽出した表)
- player.html (標準フォーマット試聴ページ、Gate 7 (g)(h)(j)(k)(l)準拠)

費用: ¥0(TTS/ASR/LLM API呼び出しなし。既存JSON読み取りとローカルHTML生成のみ)。
既存wav・JSONはすべて読み取りのみで、一切上書き・再生成していない。
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_review_player import (  # noqa: E402
    PLAYER_STANDARD_CSS,
    abs_file_url,
)

BASE = os.path.dirname(os.path.abspath(__file__))
SWEEP_DIR = os.path.join(BASE, "er011_output", "open121_existing_audio_dprime_sweep_01")
OUT_DIR = os.path.join(BASE, "er011_output", "method_d_flag23_review_01")


def load(relpath):
    with open(os.path.join(BASE, relpath), encoding="utf-8") as f:
        return json.load(f)


def find_audit_json(article_dir, level):
    for fname in ("tts_generation_results.json",):
        p = os.path.join(BASE, article_dir, level, "audit", fname)
        if os.path.exists(p):
            return p
    return None


def find_new_segments_json(article_dir, level):
    p = os.path.join(BASE, article_dir, level, "audit", "new_segments_result.json")
    if os.path.exists(p):
        return p
    return None


# ============================================================
# 一次分類(23件、証拠ベース、手動で対応付け)
# 根拠となった証拠は build() 内で機械抽出した値と突き合わせて
# classification_table.json に保存する。ここでは分類ラベルと
# 1行根拠のみを保持する(Sonnetは音声を聴けないため、最終判断では
# なく一次分類。ユーザーの実試聴で確定させる)。
# ============================================================
CLASSIFICATION = {
    "open112_trial13::er011_output/open112_trend_theme2_b_full_audio_trial_13::a2::in_one_line": (
        "真の重複(証拠あり)",
        "方式Aの独立ASR(faster-whisper)transcriptに文全体が2回連続で出現"
        "(disfluency_evidence.transcript参照)。既知バグ「In One Line "
        "BEFORE_FIX」と同一script・同一flag位置(time_a=7.52s/time_b=15.71s)"
        "で、2026-09-07ユーザー実試聴により実在バグと確定済み。",
    ),
    "open112_trial13::er011_output/open112_trend_theme2_b_full_audio_trial_13::a2::in_one_line_original": (
        "真の重複(証拠あり)",
        "同上と同一script・ほぼ同一flag位置(time_a=7.09s/time_b=14.82s)の"
        "backup版。方式Aでも同一spanをflag(canonical_repeat_count=0)。",
    ),
    "open112_trial13::er011_output/open112_trend_theme2_b_full_audio_trial_13::a2::point_two": (
        "真の重複(証拠あり)",
        "既知バグ「Point Two BUGGY」と同一script・同一flag位置"
        "(time_a=9.20s/time_b=18.84s、run=0.16s)。生成時ASR(EXACT_MATCH)は"
        "見逃したが、方式Aの独立ASRが文全体反復を検知し"
        "(canonical_repeat_count=1で正当な反復ではないと判定)、"
        "2026-09-07ユーザー実試聴で実在バグと確定済み。",
    ),
    "open112_trial13::er011_output/open112_trend_theme2_b_full_audio_trial_13::a2::point_two_original": (
        "真の重複(証拠あり)",
        "同上backup版。方式Aでも同一spanをflag(canonical_repeat_count=0)。",
    ),
    "open117_trial02_kp::er011_output/open117_keyphrase_display_tts_separation_trial_02::a2::in_one_line": (
        "真の重複(証拠あり)",
        "open112_trial13::in_one_lineと同一script・同一flag位置・同一defect"
        "(別task[OPEN-117]で生成された同一音声/再現)。",
    ),
    "open117_trial02_kp::er011_output/open117_keyphrase_display_tts_separation_trial_02::a2::in_one_line_original": (
        "真の重複(証拠あり)",
        "open112_trial13::in_one_line_originalと同一script・同一flag位置・"
        "同一defect。",
    ),
    "open117_trial02_kp::er011_output/open117_keyphrase_display_tts_separation_trial_02::a2::point_two": (
        "真の重複(証拠あり)",
        "open112_trial13::point_twoと同一script・同一flag位置・同一defect"
        "(既知バグの再現)。",
    ),
    "open117_trial02_kp::er011_output/open117_keyphrase_display_tts_separation_trial_02::a2::point_two_original": (
        "真の重複(証拠あり)",
        "open112_trial13::point_two_originalと同一script・同一flag位置・"
        "同一defect。",
    ),
    "pool_pilot_01/pool_benches::er006_output/pool_pilot_01/pool_benches::b1b::in_one_line": (
        "誤flagの可能性高",
        "生成時ASR verdict=EXACT_MATCH、方式Aも非flag。ASR全文に反復語句なし"
        "(run=0.14秒、閾値0.12秒すれすれ)。",
    ),
    "pool_pilot_01/pool_benches::er006_output/pool_pilot_01/pool_benches::b1b::topic_intro": (
        "誤flagの可能性高",
        "生成時ASR verdict=EXACT_MATCH、方式Aも非flag、run=0.12秒"
        "(Production閾値ちょうど境界値)。ASR全文に反復語句なし。",
    ),
    "pool_pilot_01/pool_n18_notifications::er006_output/pool_pilot_01/pool_n18_notifications::b1b::full_story_part1": (
        "誤flagの可能性高",
        "生成時ASR verdict=NORMALIZED_MATCH、ASR全文に反復語句なし、"
        "review_lock=RESOLVED/OK(既存人間レビュー済み)。run=0.14秒。",
    ),
    "pool_pilot_01/pool_n18_notifications_specfix_v2::er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2::a2::point_two_heading": (
        "誤flagの可能性高",
        "生成時disfluency QA(faster-whisper別経路)がflagged=false・"
        "repeats=[]で明示的に反復なしと確認済み。run=0.12秒(境界値)。",
    ),
    "pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r::er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r::a2::point_two_heading": (
        "誤flagの可能性高",
        "上記と同一script・同一flag位置(別バリアントgroup)。disfluency QA"
        "flagged=false・repeats=[]で反復なしと確認済み。run=0.12秒(境界値)。",
    ),
    "pool_pilot_01/pool_n5_cafes::er006_output/pool_pilot_01/pool_n5_cafes::a2::full_story_part2": (
        "誤flagの可能性高",
        "生成時ASR verdict=NORMALIZED_MATCH、ASR全文に反復語句なし。"
        "run=0.12秒(境界値)。",
    ),
    "pool_pilot_01/pool_n9_tip_screens::er006_output/pool_pilot_01/pool_n9_tip_screens::a2::full_story_part1": (
        "誤flagの可能性高",
        "生成時ASR verdict=NORMALIZED_MATCH、ASR全文に反復語句なし、"
        "review_lock=RESOLVED/OK。run=0.15秒。",
    ),
    "pool_pilot_01/pool_n9_tip_screens::er006_output/pool_pilot_01/pool_n9_tip_screens::a2::full_story_part1_original": (
        "誤flagの可能性高",
        "同一canonical・同一flag系列(sibling full_story_part1と同一script、"
        "review_lock=RESOLVED/OK)。sibling側ASR確認で反復なし。run=0.14秒。"
        "本ファイル自体の個別ASR記録は未取得(この点は判断困難要素として明記)。",
    ),
    "pool_pilot_01/pool_n9_tip_screens::er006_output/pool_pilot_01/pool_n9_tip_screens::b1b::in_one_line": (
        "誤flagの可能性高",
        "生成時disfluency QAがflagged=false・repeats=[]で明示的に反復なしと"
        "確認済み、review_lock=RESOLVED/OK。run=0.15秒。",
    ),
    "pool_pilot_01/pool_startups::er006_output/pool_pilot_01/pool_startups::a2::full_story_part1": (
        "判断困難",
        "tts_status=STOPPED(標準/minimal経路とも6回で不合格、正式verified=true"
        "の記録なし)。6回のASR試行いずれも反復語句は無いが、どの試行が実際に"
        "narration/へ残った音声と一致するか特定できない(duration不一致)。"
        "canonicalに正当な並行構文('More users create more value. More value "
        "attracts more users.')があり誤flagの説明も可能だが、生成ステータス"
        "自体が未検証のため一次分類は判断困難とする。",
    ),
    "er012_laneb_trial08::er012_output/editorial_b_voices_trial_08_audio/p3::b1b::point_one": (
        "誤flagの可能性高",
        "生成時ASR verdict=EXACT_MATCH(完全一致)、review_lock=RESOLVED/OK。"
        "run=0.12秒(境界値)。",
    ),
    "er003_output/a2_audio_01::er003_output/a2_audio_01::A02::full_story_part1": (
        "誤flagの可能性高",
        "new_segments_result.jsonでasr_verified=true・substring_ok=true"
        "(post-hoc検証、既存生成音声への事後確認)。ASR全文に反復語句なし。"
        "run=0.15秒。",
    ),
    "er003_output/n3_01::er003_output/n3_01/hanshin::a2::full_story_part2": (
        "誤flagの可能性高",
        "生成時asr_verified=true。ASR全文に反復語句なし(固有名詞の"
        "聞き取り差異のみ)。run=0.16秒。",
    ),
    "er003_output/n3_01::er003_output/n3_01/hanshin::a2::in_one_line": (
        "誤flagの可能性高",
        "ASR全文がcanonicalとほぼ一致し反復語句なし。run=0.14秒。",
    ),
    "er003_output/n3_01::er003_output/n3_01/hanshin::b1b::point_two_heading": (
        "誤flagの可能性高",
        "ASR全文(1文のみ)に反復語句なし。flag位置がtime_a=0.0s〜"
        "time_b=3.42s(clip全体長3.561秒)とほぼクリップ全体幅で、"
        "短い単文クリップ特有の自己相関アーティファクトの可能性が高い。"
        "run=0.13秒。",
    ),
}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    recl = load(
        "er011_output/open121_existing_audio_dprime_sweep_01/results/"
        "production_params_reclassification_02.json"
    )
    rows = [r for r in recl["main_rows"] if r["judgement"] in ("FLAG_D", "FLAG_D+FLAG_A")]
    assert len(rows) == 23, f"expected 23 FLAG_D rows, got {len(rows)}"

    inv = load("er011_output/open121_existing_audio_dprime_sweep_01/inventory.json")
    inv_by_id = {r["item_id"]: r for r in inv}
    method_d = load("er011_output/open121_existing_audio_dprime_sweep_01/results/method_d.json")

    out_rows = []
    for r in rows:
        item_id = r["item_id"]
        inv_r = inv_by_id.get(item_id, {})
        md = method_d.get(item_id, {})
        top = md.get("top_matches", [])
        best = top[0] if top else {}
        article_dir = inv_r.get("article_dir")
        level = r["level"]
        seg = r["segment_id"]

        asr_text = None
        asr_verdict = None
        disfluency_checked = None
        disfluency_evidence = None
        voice = None
        instruction_type = None
        model = None
        evidence_source = None

        audit_path = find_audit_json(article_dir, level) if article_dir else None
        if audit_path:
            with open(audit_path, encoding="utf-8") as f:
                ad = json.load(f)
            segd = ad.get("segments", {}).get(seg)
            if segd:
                asr_text = segd.get("asr_text")
                voice = segd.get("voice")
                model = segd.get("model")
                instruction_type = segd.get("instruction_type")
                attempts = segd.get("attempts_log") or segd.get("standard_attempts_log") or []
                if attempts:
                    last = attempts[-1]
                    asr_verdict = last.get("asr_verdict") or last.get("audio_classification")
                    disfluency_checked = last.get("disfluency_checked")
                    disfluency_evidence = last.get("disfluency_evidence")
                if segd.get("asr_verified") and asr_verdict is None:
                    asr_verdict = "asr_verified=true(verdict名称なし、旧schema)"
                evidence_source = os.path.relpath(audit_path, BASE).replace("\\", "/")

        canonical_text = inv_r.get("canonical_text")

        if asr_text is None:
            nsr_path = find_new_segments_json(article_dir, level) if article_dir else None
            if nsr_path:
                with open(nsr_path, encoding="utf-8") as f:
                    nsr = json.load(f)
                segd = nsr.get(seg)
                if segd:
                    asr_text = segd.get("asr_text")
                    if canonical_text is None:
                        canonical_text = segd.get("text")
                    if segd.get("asr_verified") and segd.get("substring_ok"):
                        asr_verdict = "asr_verified=true/substring_ok=true(post-hoc検証)"
                    evidence_source = os.path.relpath(nsr_path, BASE).replace("\\", "/")

        classification, rationale = CLASSIFICATION.get(
            item_id, ("判断困難", "一次証拠を機械抽出できず(要追加調査)")
        )

        out_rows.append(
            {
                "item_id": item_id,
                "group": r["group"],
                "level": level,
                "segment_id": seg,
                "path": r["path"],
                "wav_abs_url": abs_file_url(os.path.join(BASE, r["path"])),
                "duration_seconds": md.get("duration_seconds"),
                "best_run_length_seconds": md.get("best_run_length_seconds"),
                "flag_time_a": best.get("time_a_seconds"),
                "flag_time_b": best.get("time_b_seconds"),
                "flag_lag_seconds": best.get("lag_seconds"),
                "flag_similarity": best.get("similarity"),
                "d_prime_run_at_sim0.7": r.get("d_prime_run_at_sim0.7"),
                "review_lock_state": r.get("review_lock_state"),
                "review_lock_final_status": r.get("review_lock_final_status"),
                "a_flagged": r.get("a_flagged"),
                "a_flagged_spans": r.get("a_flagged_spans"),
                "canonical_text": canonical_text,
                "asr_text": asr_text,
                "asr_verdict": asr_verdict,
                "disfluency_checked": disfluency_checked,
                "disfluency_evidence": disfluency_evidence,
                "voice": voice,
                "model": model,
                "instruction_type": instruction_type,
                "evidence_source": evidence_source,
                "classification": classification,
                "classification_rationale": rationale,
            }
        )

    with open(os.path.join(OUT_DIR, "classification_table.json"), "w", encoding="utf-8") as f:
        json.dump(out_rows, f, ensure_ascii=False, indent=2)

    build_player_html(out_rows)

    # 集計
    from collections import Counter

    counts = Counter(r["classification"] for r in out_rows)
    print("classification counts:", dict(counts))
    print("wrote:", os.path.join(OUT_DIR, "classification_table.json"))
    print("wrote:", os.path.join(OUT_DIR, "player.html"))


def esc(s):
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_script_html(row):
    """canonical scriptを表示。方式AでflagされたitemはASRが検知した反復span
    (a_flagged_spans[0].span_text相当の内容)を太字強調する。方式Dのみの
    itemは秒単位の語句位置対応が取れないため、太字強調はせず
    「音響のみ検知(ASR文字起こしでは該当語句の反復なし)」と注記する。"""
    canonical = row.get("canonical_text")
    if canonical is None:
        return '<span class="missing">未取得(canonical本文が確認できず)</span>'
    html = esc(canonical)
    spans = row.get("a_flagged_spans") or []
    if spans:
        # 反復として検知された文の前半部分(重複の"元"側)を太字にする。
        # 表示上の目安であり、厳密な文字位置対応ではない(方式Aの検知は
        # 独立した別ASR transcript上でのn-gram一致であり、canonical上の
        # 文字位置と1:1対応するとは限らないため)。
        return f'{html}<br><b>[方式A検知(独立ASR): 実際の音声には下記が2回連続で出現したと推定]</b>'
    else:
        return f'{html}<br><small>(方式Dのみ検知。ASR文字起こし上は反復語句なし。下記ASR比較参照)</small>'


def build_evidence_html(row):
    parts = []
    if row.get("asr_text"):
        parts.append(f'<b>生成時ASR:</b> {esc(row["asr_text"])}')
    if row.get("asr_verdict"):
        parts.append(f'<b>ASR verdict:</b> {esc(row["asr_verdict"])}')
    if row.get("disfluency_checked"):
        de = row.get("disfluency_evidence") or {}
        parts.append(
            f'<b>disfluency QA:</b> flagged={de.get("flagged")}, '
            f'repeats={de.get("repeats")}'
        )
    spans = row.get("a_flagged_spans") or []
    for sp in spans:
        parts.append(
            f'<b>方式A検知span:</b> "{esc(sp.get("span_text"))}" '
            f'(canonical_repeat_count={sp.get("canonical_repeat_count")}, '
            f'{sp.get("first_start_s")}s-{sp.get("first_end_s")}s / '
            f'{sp.get("second_start_s")}s-{sp.get("second_end_s")}s)'
        )
    if row.get("evidence_source"):
        parts.append(f'<small>証拠source: {esc(row["evidence_source"])}</small>')
    if not parts:
        return '<span class="missing">未取得(生成時ASR記録が見つからず)</span>'
    return "<br>".join(parts)


ROW_TEMPLATE = """
<tr class="{row_cls}">
  <td>
    <button class="seek" onclick="seekOwn('a{idx}', {time_a})">&#9654; {time_a_disp}s(1回目)</button><br>
    <button class="seek" onclick="seekOwn('a{idx}', {time_b})">&#9654; {time_b_disp}s(2回目)</button><br>
    <small>run={run}s / lag={lag}s / sim={sim}</small>
  </td>
  <td><b>{group}</b> / {level} / {segment_id}<br>
    <small>voice={voice} / model={model} / instr={instr}</small><br>
    <small>duration={duration}s</small><br>
    <small>review_lock={review_lock_state}/{review_lock_final}</small>
  </td>
  <td class="txt">{script_html}</td>
  <td>{evidence_html}</td>
  <td><audio id="a{idx}" controls preload="none" src="{wav_url}"></audio></td>
  <td><b>{classification}</b><br><small>{rationale}</small></td>
</tr>
"""


def build_player_html(rows):
    from collections import Counter

    counts = Counter(r["classification"] for r in rows)

    body_rows = []
    for idx, row in enumerate(rows):
        time_a = row.get("flag_time_a")
        time_b = row.get("flag_time_b")
        body_rows.append(
            ROW_TEMPLATE.format(
                row_cls="",
                idx=idx,
                time_a=time_a if time_a is not None else 0,
                time_b=time_b if time_b is not None else 0,
                time_a_disp=f"{time_a:.2f}" if time_a is not None else "?",
                time_b_disp=f"{time_b:.2f}" if time_b is not None else "?",
                run=row.get("best_run_length_seconds"),
                lag=row.get("flag_lag_seconds"),
                sim=row.get("flag_similarity"),
                group=esc(row["group"]),
                level=esc(row["level"]),
                segment_id=esc(row["segment_id"]),
                voice=esc(row.get("voice") or "情報なし(audit記録なし)"),
                model=esc(row.get("model") or "情報なし"),
                instr=esc(row.get("instruction_type") or "情報なし"),
                duration=row.get("duration_seconds"),
                review_lock_state=esc(row.get("review_lock_state") or "(記録なし)"),
                review_lock_final=esc(row.get("review_lock_final_status") or "(記録なし)"),
                script_html=build_script_html(row),
                evidence_html=build_evidence_html(row),
                wav_url=row["wav_abs_url"],
                classification=esc(row["classification"]),
                rationale=esc(row["classification_rationale"]),
            )
        )

    summary_rows = "".join(
        f"<tr><td>{esc(k)}</td><td>{v}</td></tr>" for k, v in counts.items()
    )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>OPEN-121 方式D flag23件 一次レビュー(部品試聴、完成episodeではない)</title>
<style>
{PLAYER_STANDARD_CSS}
table.timeline th:nth-child(3), table.timeline td:nth-child(3) {{ width: auto; }}
table.timeline th:nth-child(4), table.timeline td:nth-child(4) {{ width: 320px; }}
table.timeline th:nth-child(6), table.timeline td:nth-child(6) {{ width: 220px; }}
</style>
</head>
<body>
<h1>OPEN-121 方式D flag23件 一次レビュー</h1>
<div class="note">
<b>注意: これは完成episodeの試聴ページではありません。</b>
方式D(自己相関ベースの重複/hallucination検知、Production既定閾値
run&ge;0.12秒)によりflagされた個別segment(部品)23件だけを集めた
軽量試聴ページです(管理ID: OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01)。
各行の「1回目/2回目」Seekボタンは、その行自身の個別音声(右の
&lt;audio&gt;)内で、方式Dが検知した類似run区間の開始秒へ移動します
(完成episode全体のplayerではありません)。
一次分類は機械的な証拠(生成時ASR検証結果・disfluency QA・方式Aの
独立ASR再検知結果)に基づくものであり、Sonnetは音声を実際に聴いて
いません。最終判断はユーザーの実試聴によります。閾値変更・自動再生成は
一切行っていません(既存wav・JSONは読み取りのみ)。
</div>

<h2>一次分類 集計(23件)</h2>
<table class="kp"><tr><th>一次分類</th><th>件数</th></tr>{summary_rows}</table>

<h2>23件 詳細(Seek / Segment・voice / Script / 証拠 / 音声 / 一次分類)</h2>
<table class="timeline">
<thead><tr><th>Seek(自音声内)</th><th>Segment/voice/review_lock</th><th>Script</th>
<th>証拠(ASR/disfluency/方式A)</th><th>個別音声</th><th>一次分類・根拠</th></tr></thead>
<tbody>
{"".join(body_rows)}
</tbody>
</table>

<script>
function seekOwn(audioId, sec) {{
  var a = document.getElementById(audioId);
  if (!a) return;
  a.currentTime = parseFloat(sec);
  a.play();
}}
</script>
</body>
</html>
"""
    with open(os.path.join(OUT_DIR, "player.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
