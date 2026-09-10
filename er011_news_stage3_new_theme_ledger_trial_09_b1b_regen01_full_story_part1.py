# ============================================================
# er011_news_stage3_new_theme_ledger_trial_09_b1b_regen01_full_story_part1.py
# 管理ID: FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09-REGEN-01
# ============================================================
# 背景: FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09のB1B記事
# (in-vivo CAR-T/自己免疫疾患テーマ、NEJM 2026-09-03)で、
# `full_story_part1` segmentが既存retry上限(3回)を使い切っても
# ASR検証NG(TRUE_CONTENT_MISMATCH、"a report on"を3回とも一貫して
# 読み落とす)となり、HUMAN_REVIEW_REQUIRED(review_lock)へ到達、
# Assemblyは EPISODE_BLOCKED_BY_AUDIO_VALIDATION で正常STOPした
# (詳細: FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09_REPORT.md §4)。
#
# ユーザー決定(2026-09-10): 既存の承認済み再生成経路で1回のみ
# 再生成してよい。その1回でAudio Validation(ASR/disfluency QA)を
# 通らなければ追加再生成せずSTOPしユーザー確認へ戻す。
#
# 手本: er011_household_unified_final_candidate_01_segfix_comment3_01.py
# と同一パターン(review_lock.approve_regenerate()→元のsegment呼び出し
# と同一引数で既存TTS関数を呼ぶ→旧wavは*_original.wavとして退避→
# 再Assembly→Audio Gate→player生成)。本文・Prompt・引数は変更しない。
#
# 再生成経路(既存Production関数を無変更のまま呼ぶだけ):
#   - er011_human_review_lock_01.approve_regenerate()
#   - er003_v1_sing01_news_tail_fix.generate_news_narration_wide_margin()
#     (full_story_part1を元々生成したのと同一関数・同一引数
#     [disfluency_qa=False, enable_connected_speech_equivalence_layer=True,
#     enable_repetition_qa=True]、er003_v1_n3_01_tts_generate.
#     generate_b1_segments()内のfull_story_part1呼び出しと同一。この
#     関数自体が内部でmax_attempts=PRODUCTION_MAX_TTS_ATTEMPTS(=3)の
#     retryループを持つが、review_lockのREGENERATE_APPROVEDは「次の
#     1回の呼び出し」を許可するのみで、結果に応じてRESOLVED/
#     HUMAN_REVIEW_REQUIREDへ自動遷移し残らない=ユーザー承認の
#     「1回のみ再生成」と整合)。
#   - PASSなら再Assembly + Audio Validation Gate opt-in ON確認 + player
#     生成。NGならそこでSTOP(再Assemblyしない)。
#   - 旧full_story_part1.wavは full_story_part1_original.wav として
#     narration_dirに残す(上書き消去しない、既存慣行)。
#
# Production/Prompt/共有module編集なし、Git操作なし。費用上限: \30。
from __future__ import annotations

import html
import json
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import audio_review_player as arp
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as asm
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl
import er011_human_review_lock_01 as review_lock

THEME_ID = "news_stage3_new_theme_ledger_trial_09_b1b_full"
OUT_DIR = f"er011_output/{THEME_ID}"
LEVEL_OUT_DIR = f"{OUT_DIR}/b1b"
NARRATION_DIR = f"{LEVEL_OUT_DIR}/narration"
TARGET = "full_story_part1"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def step1_diagnose() -> dict:
    """再生成前のLock状態・3回のNG理由の確認(読み取りのみ)。"""
    lock_state = load_json(f"{LEVEL_OUT_DIR}/audit/review_lock_state.json")
    results = load_json(f"{LEVEL_OUT_DIR}/audit/tts_generation_results.json")
    lock_entry = lock_state[TARGET]
    result_entry = results["segments"][TARGET]
    finding = {
        "target": TARGET,
        "lock_state": lock_entry.get("state"),
        "lock_final_status": lock_entry.get("final_status"),
        "cumulative_tts_attempts": lock_entry.get("cumulative_tts_attempts"),
        "cumulative_asr_calls": lock_entry.get("cumulative_asr_calls"),
        "canonical_text": result_entry.get("canonical_text"),
        "ng_reason_per_attempt": [
            {"attempt": a["attempt"], "audio_classification": a["audio_classification"],
             "asr_text": a["asr_text"]}
            for a in lock_entry.get("last_attempts_log", [])
        ],
    }
    print(f"[{THEME_ID}][diagnose] {json.dumps(finding, ensure_ascii=False)}")
    assert finding["lock_state"] == "HUMAN_REVIEW_REQUIRED", (
        f"想定していたlock state(HUMAN_REVIEW_REQUIRED)と異なります: {finding['lock_state']}")
    return finding


def step2_backup_original() -> str:
    out_path = f"{NARRATION_DIR}/{TARGET}.wav"
    backup_path = f"{NARRATION_DIR}/{TARGET}_original.wav"
    assert os.path.exists(out_path), f"対象wavが見つかりません: {out_path}"
    if not os.path.exists(backup_path):
        shutil.copyfile(out_path, backup_path)
        print(f"[{THEME_ID}] b1b {TARGET}: 旧音声を {backup_path} へ退避しました。")
    else:
        print(f"[{THEME_ID}] b1b {TARGET}: 退避先 {backup_path} は既に存在します(再実行のため上書きしません)。")
    return backup_path


def step3_regenerate() -> dict:
    parts = load_json(f"{LEVEL_OUT_DIR}/parts.json")
    results_path = f"{LEVEL_OUT_DIR}/audit/tts_generation_results.json"
    all_results = load_json(results_path)
    old_entry = all_results["segments"][TARGET]

    text = parts["part1"]
    out_path = f"{NARRATION_DIR}/{TARGET}.wav"

    review_lock.approve_regenerate(
        out_path, tts_gen.tts_safe_news_en(text),
        approved_by="claude_code_operator_family_a_news_stage3_new_theme_ledger_trial_09_regen_01")
    print(f"[{THEME_ID}] b1b {TARGET}: REGENERATE_APPROVED付与。既存segment再生成経路"
          "(news_tail_fix.generate_news_narration_wide_margin、元のfull_story_part1"
          "呼び出しと同一引数)で再生成開始...")

    with cl.logging_context(THEME_ID, "tts_full_story_part1_regen01"), \
         cl.segment_context(TARGET):
        r = news_tail_fix.generate_news_narration_wide_margin(
            tts_gen.tts_safe_news_en(text), out_path,
            disfluency_qa=False,
            enable_connected_speech_equivalence_layer=True,
            enable_repetition_qa=True)
    r["canonical_text"] = text
    print(f"[{THEME_ID}] b1b {TARGET}: 再生成結果 status={r.get('status')} asr_text={r.get('asr_text')!r}")

    all_results["segments"][TARGET] = r
    save_json(results_path, all_results)

    summary_path = f"{LEVEL_OUT_DIR}/run_summary_tts.json"
    if os.path.exists(summary_path):
        all_summary = load_json(summary_path)
        all_status = {k: v.get("status") for k, v in all_results["segments"].items()}
        all_summary["segment_status"] = all_status
        save_json(summary_path, all_summary)

    save_json(
        f"{LEVEL_OUT_DIR}/audit/regen01_full_story_part1_family_a_news_stage3_new_theme_ledger_trial_09.json",
        {
            "management_id": "FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09-REGEN-01",
            "target": TARGET,
            "reason": (
                "ユーザー承認済み再生成1回(2026-09-10)。既存retry上限3回消化後も"
                "TRUE_CONTENT_MISMATCH('a report on'の読み落としを3回とも一貫して"
                "検出)でHUMAN_REVIEW_REQUIREDへ到達していたsegmentを、既存segment"
                "再生成経路(review_lock.approve_regenerate + "
                "news_tail_fix.generate_news_narration_wide_margin、元のfull_story_"
                "part1呼び出しと同一引数[disfluency_qa=False, "
                "enable_connected_speech_equivalence_layer=True, "
                "enable_repetition_qa=True])で再生成した。Prompt/本文は無変更。"
                "旧音声はfull_story_part1_original.wavとして退避。"
            ),
            "old_entry": old_entry,
            "new_entry": r,
        },
    )
    print(f"[{THEME_ID}] b1b {TARGET} 再生成・記録更新完了。status={r.get('status')}")
    return r


def step4_reassemble_and_gate() -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    with cl.logging_context(THEME_ID, "assemble_b1b_regen01"):
        try:
            result = asm.stage_assemble_b1(theme)
            result["gate_off_result"] = "PASS"
        except RuntimeError as e:
            result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}

    if result.get("gate_off_result") == "PASS":
        rs = asm.derive_a_family_required_structure("B1")
        try:
            asm.verify_episode_audio_validation_gate(LEVEL_OUT_DIR, "B1", required_structure=rs)
            result["gate_opt_in_result"] = {"gate_on_result": "PASS"}
        except RuntimeError as e:
            result["gate_opt_in_result"] = {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:800]}
    else:
        result["gate_opt_in_result"] = {"gate_on_result": "SKIPPED(gate_off_blocked)"}

    print(f"[{THEME_ID}] b1b 再Assembly + Gate opt-in ON結果: "
          f"gate_off={result.get('gate_off_result')} "
          f"gate_on={result.get('gate_opt_in_result', {}).get('gate_on_result')}")
    return result


def esc(text: str) -> str:
    if text is None:
        return ""
    return html.escape(str(text)).replace("\n\n", "<br><br>").replace("\n", "<br>")


def au(path: str) -> str:
    return arp.abs_file_url(path)


def step5_player() -> dict:
    """Gateが通った場合のみplayer.htmlを生成する(既存audio_review_player標準
    部品を使い、er011_output/household_unified_final_candidate_01/build_player.py
    のbuild_b1b_rows()ロジックをB1B単独ページ向けに踏襲、無変更)。
    TTS/ASR/Assemblyは一切呼ばず、既に確定した音声wav・JSONを読むだけ。"""
    narration_dir = f"{LEVEL_OUT_DIR}/narration"
    parts = load_json(f"{LEVEL_OUT_DIR}/parts.json")
    support = load_json(f"{LEVEL_OUT_DIR}/b1_support_texts.json")
    timeline = load_json(f"{LEVEL_OUT_DIR}/audit/timeline.json")
    kp = load_json(f"{LEVEL_OUT_DIR}/key_phrases/keywords_canonicalized.json")
    kp_items = {item["rank"]: item for item in kp["items"]}

    def audio_url(name: str) -> str:
        return au(f"{narration_dir}/{name}.wav")

    fixed_text = {
        "welcome_charon": p9a.PODCAST_NAME_TEXT_V2,
        "preview_intro_charon": p9a.PREVIEW_INTRO_TEXT,
        "key_phrases_intro_charon": p9a.KEY_PHRASES_INTRO_TEXT,
        "full_story_intro_charon": p9a.FULL_STORY_INTRO_TEXT,
    }
    sfx_labels = {"Intro", "Notification 1", "Notification 2", "Notification 3", "Outro (Charon)",
                  "Point Notification (Point One cue)", "Point Notification (Point Two cue)"}

    def resolve_row(label: str):
        if label in sfx_labels:
            return "SFX", "効果音・音楽ジングル(読み上げなし、固定音源)。", "—"
        if label.startswith("pause_"):
            return None, None, None
        if label == "Welcome (Charon)":
            return "Charon", esc(fixed_text["welcome_charon"]), arp.render_single_audio_html(audio_url("welcome_charon"))
        if label == "Preview intro (Charon)":
            return "Charon", esc(fixed_text["preview_intro_charon"]), arp.render_single_audio_html(audio_url("preview_intro_charon"))
        if label == "Key phrases intro (Charon)":
            return "Charon", esc(fixed_text["key_phrases_intro_charon"]), arp.render_single_audio_html(audio_url("key_phrases_intro_charon"))
        if label == "Full story intro (Charon)":
            return "Charon", esc(fixed_text["full_story_intro_charon"]), arp.render_single_audio_html(audio_url("full_story_intro_charon"))
        if label == "Topic intro (Charon)":
            text = f"Today's topic is {parts['title']}."
            return "Charon", esc(text), arp.render_single_audio_html(audio_url("topic_intro"))
        if label == "Preview (Charon)":
            return "Charon", esc(support.get("preview")), arp.render_single_audio_html(audio_url("preview"))
        comment_map = {"Comment 1 (Charon)": 1, "Comment 2 (Charon)": 2,
                       "Comment 3 (Charon, Bridge)": 3, "Comment 4 (Charon)": 4}
        if label in comment_map:
            i = comment_map[label]
            return "Charon", esc(support.get(f"comment_{i}")), arp.render_single_audio_html(audio_url(f"comment_{i}"))
        if label.startswith("Key Phrase "):
            rank = int(label.split(" ")[-1])
            item = kp_items.get(rank)
            if item is None:
                return "Aoede/Charon", "未取得", "—"
            text = f"EN: {esc(item['used_form'])}<br>JA(表示/TTS共通): {esc(item['japanese_gloss'])}"
            audio_html = arp.render_single_audio_html((audio_url(f"kp{rank}_en"), audio_url(f"kp{rank}_ja_charon")))
            return "Aoede(EN)/Charon(JA)", text, audio_html
        if label == "Full Story Part 1 (Aoede)":
            return "Aoede", esc(parts.get("part1")), arp.render_single_audio_html(audio_url("full_story_part1"))
        if label == "Full Story Part 2 (Aoede)":
            return "Aoede", esc(parts.get("part2")), arp.render_single_audio_html(audio_url("full_story_part2"))
        if label == "Point One semantic heading (Aoede)":
            return "Aoede", esc(parts.get("point_one_heading")), arp.render_single_audio_html(audio_url("point_one_heading"))
        if label == "Point One (Aoede)":
            return "Aoede", esc(parts.get("point_one_body")), arp.render_single_audio_html(audio_url("point_one"))
        if label == "Point Two semantic heading (Aoede)":
            return "Aoede", esc(parts.get("point_two_heading")), arp.render_single_audio_html(audio_url("point_two_heading"))
        if label == "Point Two (Aoede)":
            return "Aoede", esc(parts.get("point_two_body")), arp.render_single_audio_html(audio_url("point_two"))
        if label == "In One Line (Aoede)":
            return "Aoede", esc(parts.get("in_one_line")), arp.render_single_audio_html(audio_url("in_one_line"))
        return "未取得", "未取得", "—"

    rows = []
    for entry in timeline:
        voice, script_html, audio_html = resolve_row(entry["part"])
        if voice is None:
            continue
        rows.append(arp.render_timeline_row(entry["start_seconds"], entry["part"], voice, script_html, audio_html,
                                             missing=False))

    kp_rows = ["<tr><th>#</th><th>English (used_form)</th><th>表示用 gloss</th><th>TTS用テキスト</th></tr>"]
    for rank in sorted(kp_items.keys()):
        item = kp_items[rank]
        kp_rows.append(f"<tr><td>{rank}</td><td>{esc(item['used_form'])}</td><td>{esc(item['japanese_gloss'])}</td>"
                        f"<td>{esc(item.get('japanese_gloss_tts') or item['japanese_gloss'])}</td></tr>")
    kp_table_html = f'<table class="kp"><thead>{kp_rows[0]}</thead><tbody>{"".join(kp_rows[1:])}</tbody></table>'

    assemble_summary = load_json(f"{LEVEL_OUT_DIR}/run_summary_assemble.json")
    audio_url_main = au(assemble_summary["out_path"])
    with open(f"{LEVEL_OUT_DIR}/article.md", encoding="utf-8") as f:
        article_md = f.read()

    note = f"""
<p class="note">
このページはFAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09-REGEN-01
(ユーザー承認済み再生成1回、Trial扱い、Production配線なし)のB1B試聴用
ページです。full_story_part1のみ既存Human Review Lock経由で1回再生成
(review_lock.approve_regenerate + 既存TTS関数を元と同一引数で呼び出し)
し、既存Assembly・Audio Validation Gate opt-in ON経路(OPEN-129)まで
PASSしました。他segmentは無変更です。標準フォーマット
(audio_review_player.py、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-
FORMAT-11、Source列なし)準拠。duration={assemble_summary['duration_seconds']}s
peak={assemble_summary['peak']} clipping={assemble_summary['clipping_detected']}。
</p>
"""

    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09-REGEN-01</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09-REGEN-01 — B1B「{esc(parts.get('title'))}」(full_story_part1再生成後)</h1>
{note}
<audio id="episode_audio" class="main" controls src="{audio_url_main}"></audio>
<h3>B1B タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h3>
{arp.render_timeline_table(rows)}
<h3>B1B Key Phrase表</h3>
{kp_table_html}
<h3>B1B 記事全文(article.md)</h3>
<pre class="article">{esc(article_md)}</pre>
<script>
{arp.SEEK_SCRIPT}
</script>
</body>
</html>
"""

    player_path = f"{OUT_DIR}/player.html"
    with open(player_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    abs_path = os.path.abspath(player_path).replace("\\", "/")
    print(f"[{THEME_ID}] player生成: {player_path}")
    print(f"file:///{abs_path}")
    return {"player_path": player_path, "abs_file_url": f"file:///{abs_path}"}


def main() -> dict:
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    diagnosis = step1_diagnose()
    step2_backup_original()
    regen_result = step3_regenerate()

    if regen_result.get("status") != "OK":
        print(f"[{THEME_ID}] b1b {TARGET}: 再生成結果status={regen_result.get('status')}"
              "(RESOLVEDでない)。再Assemblyせずここでstopします。")
        summary = {"diagnosis": diagnosis, "regen_result": regen_result,
                    "assembly_result": None, "player_result": None}
        save_json(f"{OUT_DIR}/regen01_full_story_part1_summary.json", summary)
        return summary

    assembly_result = step4_reassemble_and_gate()
    player_result = None
    if assembly_result.get("gate_opt_in_result", {}).get("gate_on_result") == "PASS":
        player_result = step5_player()
    else:
        print(f"[{THEME_ID}] Gate opt-in ONがPASSでないため、playerは生成しません。")

    summary = {
        "diagnosis": diagnosis,
        "regen_result": regen_result,
        "assembly_result": assembly_result,
        "player_result": player_result,
    }
    save_json(f"{OUT_DIR}/regen01_full_story_part1_summary.json", summary)
    print(f"[{THEME_ID}] REGEN-01 完了。")
    return summary


if __name__ == "__main__":
    main()
