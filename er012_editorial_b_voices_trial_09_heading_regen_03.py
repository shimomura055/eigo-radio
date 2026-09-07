# ============================================================
# er012_editorial_b_voices_trial_09_heading_regen_03.py
# EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03
# ============================================================
# ユーザー決定(2026-09-07、明示承認)に基づき、point_two_heading
# ("Another Voice: The freedom to move.")のTTS再生成を1回だけ実行する
# (review_lock.approve_regenerate()、根拠: EDITORIAL-B-FAMILY-VOICES-
# TRIAL-09-LOCK-RETRY-AND-FULL-ASSEMBLY-02_REPORT.md §8-2 (a))。
# PASSした場合のみ、既存Production primitive(asm.load_b1_sources/
# apply_b1_gain/assemble_with_timeline/apply_headroom_safety_valve)+
# Trial-09の既存Trial専用timeline(build_b1_voices_timeline_trial09、
# er012_editorial_b_voices_trial_09_audio.py、無変更のままimportして
# 呼ぶだけ)で1本化Assemblyを行い、Gate 7 (a)〜(l)準拠のplayer.htmlを
# 再生成する。
#
# 触れないもの: Lane Aファイル(er011_*, er006_*.py, er003_v1_*)自体、
# er012_editorial_b_voices_trial_09_audio.py自体(import・関数呼び出し
# のみ、編集しない)、Productionコード・Prompt・Validator本体。
# 書き込み: 本ファイル(root)、
# er012_output/editorial_b_voices_trial_09_audio/ 配下のみ
# (b1b/narration/point_two_heading.wav・b1b/narration/attempts/・
# b1b/audit/review_lock_state.json・b1b/audit/heading_regen_03_result.json・
# b1b/audit/user_approval_record_heading_regen_03.json・b1b/assembled/・
# b1b/audit/timeline.json等・player.html)。
#
# コスト上限: 本タスクで新規発生する分に限り¥100でSTOP。
from __future__ import annotations

import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う
# (委任文Aで明示指定)。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import audio_review_player as player_common  # PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11: 標準player生成の共通module
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as asm
import er003_v1_sing01_point_headings_aoede as point_headings
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er011_human_review_lock_01 as review_lock
import er012_editorial_b_voices_trial_09_audio as trial09  # Trial-09既存script、無変更のまま関数だけ呼ぶ

OUT_DIR = trial09.OUT_DIR
OUT_B1_DIR = trial09.OUT_B1_DIR
NARRATION_DIR = trial09.NARRATION_DIR
COST_LOG_PATH = trial09.COST_LOG_PATH

SEGMENT_NAME = "point_two_heading"
OUT_PATH = f"{NARRATION_DIR}/{SEGMENT_NAME}.wav"
BUDGET_JPY_CAP_THIS_TASK = 100.0
HUMAN_REVIEW_QUEUE_PATH = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"

APPROVAL_RATIONALE = (
    "ユーザー決定2026-09-07(明示承認、EDITORIAL-B-FAMILY-VOICES-TRIAL-09-"
    "HEADING-REGEN-AND-FULL-EPISODE-03委任文 item 1): point_two_heading"
    "(\"Another Voice: The freedom to move.\")の再生成を1回だけ承認する。"
    "根拠: EDITORIAL-B-FAMILY-VOICES-TRIAL-09-LOCK-RETRY-AND-FULL-"
    "ASSEMBLY-02_REPORT.md §8-2 (a)(『a. 明示的なapprove_regenerate()での"
    "ユーザー承認後の再生成』)。"
)


def load_json(path: str) -> dict:
    return trial09.load_json(path)


def save_json(path: str, obj) -> None:
    trial09.save_json(path, obj)


# ============================================================
# Part A: point_two_headingの再生成(1回のみ)
# ============================================================
def regenerate_point_two_heading() -> dict:
    parts = load_json(f"{OUT_B1_DIR}/parts.json")
    text = parts["point_two_heading"]
    assert text == "Another Voice: The freedom to move.", (
        f"想定外のcanonical_text(Trial-09原文と不一致): {text!r}")

    prior_lock = load_json(f"{OUT_B1_DIR}/audit/review_lock_state.json").get(SEGMENT_NAME, {})
    jpy_before, _ = trial09.compute_cost_jpy_so_far()

    approved_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    approval_entry = review_lock.approve_regenerate(OUT_PATH, text, approved_by="user")
    save_json(f"{OUT_B1_DIR}/audit/user_approval_record_heading_regen_03.json", {
        "management_id": "EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03",
        "segment_id": SEGMENT_NAME, "canonical_text": text,
        "approved_by": "user", "approved_at": approved_at, "rationale": APPROVAL_RATIONALE,
        "prior_lock_state_before_approval": prior_lock,
        "review_lock_entry_after_approval": approval_entry,
    })
    print(f"[HEADING-REGEN-03] approve_regenerate() 実行完了: state={approval_entry.get('state')}")

    # Trial-09が使ったのと同一のProduction関数(無変更)。TTS_EXECUTION_MODE=
    # STANDARDは本ファイル冒頭で明示設定済み。guarded_generate デコレータが
    # REGENERATE_APPROVED状態を検知し、1回分の再生成のみ許可する。
    result = point_headings.generate(text, OUT_PATH)
    jpy_after, by_provider_after = trial09.compute_cost_jpy_so_far()
    cost_delta = round(jpy_after - jpy_before, 4)
    print(f"[HEADING-REGEN-03] point_headings.generate() status={result.get('status')} "
          f"cost_delta={cost_delta} JPY")

    new_lock = load_json(f"{OUT_B1_DIR}/audit/review_lock_state.json").get(SEGMENT_NAME, {})

    # asm.verify_episode_audio_validation_gate()(Production、無変更)は
    # b1b/audit/tts_generation_results.json(run_tts_new_segments/
    # finalize_tts_resultsが書くaudit記録、review_lock_state.jsonとは
    # 別ファイル)を正として判定する。Trial-09原実行時点でこのfileには
    # HUMAN_REVIEW_LOCKEDのstaleな記録が残ったままなので、本タスクで
    # 新たに得たresultで当該1 segment分だけ更新する(finalize_tts_results()
    # が本来書くのと同じ形[result dict + canonical_text]、Gate関数自体は
    # 一切変更しない)。
    tts_results_path = f"{OUT_B1_DIR}/audit/tts_generation_results.json"
    tts_results = load_json(tts_results_path)
    entry = dict(result)
    entry["canonical_text"] = text
    tts_results["segments"][SEGMENT_NAME] = entry
    save_json(tts_results_path, tts_results)
    print(f"[HEADING-REGEN-03] tts_generation_results.json の{SEGMENT_NAME}を更新: "
          f"status={entry.get('status')}")

    hr_queue_detail = None
    if result.get("status") != "OK" and os.path.exists(HUMAN_REVIEW_QUEUE_PATH):
        with open(HUMAN_REVIEW_QUEUE_PATH, encoding="utf-8") as f:
            entries = [json.loads(line) for line in f if line.strip()]
        matches = [e for e in entries if e.get("canonical_text") == text]
        if matches:
            hr_queue_detail = matches[-1]  # 最新分(このattempt由来のはず)

    summary = {
        "management_id": "EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03",
        "segment_id": SEGMENT_NAME, "canonical_text": text,
        "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE"),
        "generate_result_status": result.get("status"),
        "generate_result": result,
        "cost_delta_jpy_this_call": cost_delta,
        "cost_by_provider_cumulative": by_provider_after,
        "budget_cap_jpy_this_task": BUDGET_JPY_CAP_THIS_TASK,
        "budget_ok": cost_delta <= BUDGET_JPY_CAP_THIS_TASK,
        "review_lock_entry_after_generate": new_lock,
        "human_review_queue_detail_if_reached": hr_queue_detail,
    }
    save_json(f"{OUT_B1_DIR}/audit/heading_regen_03_result.json", summary)
    if cost_delta > BUDGET_JPY_CAP_THIS_TASK:
        print(f"[HEADING-REGEN-03][BUDGET_GUARD] cost_delta={cost_delta} JPY > cap "
              f"{BUDGET_JPY_CAP_THIS_TASK} JPY(既に発生済みのため記録のみ、追加呼び出しはしない)")
    return summary


# ============================================================
# Part B: 1本化Assembly(PASSした場合のみ)+ Gate 7準拠player.html
# ============================================================
SFX_LABEL = "効果音(読み上げなし)"
JINGLE_LABEL_TEMPLATE = "音楽ジングル(ナレーションなし、読み上げなし)。{dur:.3f}秒の{name}をそのまま再生。"


def _row_info(label: str, parts: dict, support_texts: dict, voice_a: str, voice_b: str,
              kp_by_rank: dict, dur_seconds: float) -> dict:
    """timelineの1エントリ(part label)から、player行に必要な情報
    (script text・voice名・個別音声パス・SFX判定)を、実際にAssembly
    (build_b1_voices_timeline_trial09、Production/Trial専用関数、無変更)
    が使った素材から機械的に導出する(推測補完はしない)。"""
    charon = "Charon"
    if label == "Intro":
        return {"text": JINGLE_LABEL_TEMPLATE.format(dur=dur_seconds, name="Intro.mp3"),
                "voice": None, "audio": None, "sfx": True,
                "src": f"{p9a.INTRO_MP3_PATH}(固定音源、記事非依存)"}
    if label == "Outro (Charon)":
        return {"text": JINGLE_LABEL_TEMPLATE.format(dur=dur_seconds, name="outro.mp3")
                        + " ラベルに(Charon)とあるが、実際はTTS読み上げではない固定音源ジングル"
                          "(build_b1_voices_timeline_trial09のラベル文言そのまま、他Production"
                          "パイプラインと同じ命名慣習)。",
                "voice": None, "audio": None, "sfx": True,
                "src": f"{p9a.OUTRO_MP3_PATH}(固定音源、記事非依存)"}
    if label.startswith("Notification "):
        return {"text": SFX_LABEL, "voice": None, "audio": None, "sfx": True,
                "src": f"{p9a.NOTIFICATION_MP3_PATH}(固定効果音)"}
    if label.startswith("Point Notification"):
        return {"text": SFX_LABEL, "voice": None, "audio": None, "sfx": True,
                "src": f"{asm.POINT_NOTIFICATION_MP3_PATH}(固定効果音)"}
    if label == "Welcome (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["welcome"], "voice": charon,
                "audio": f"{NARRATION_DIR}/welcome_charon.wav", "sfx": False,
                "src": "shared_narration.FIXED_ENGLISH_TEXTS['welcome'](固定テンプレート音声、Master Audio Store経由)"}
    if label == "Topic intro (Charon)":
        text = f"Today's topic is {parts['title']}."
        return {"text": text, "voice": charon, "audio": f"{NARRATION_DIR}/topic_intro.wav", "sfx": False,
                "src": "b1b/parts.json → title(記事固有、run_tts_new_segmentsと同一組み立て)"}
    if label == "Preview intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["preview_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/preview_intro_charon.wav", "sfx": False,
                "src": "shared_narration.FIXED_ENGLISH_TEXTS['preview_intro'](固定テンプレート音声)"}
    if label == "Preview (Charon)":
        return {"text": support_texts["preview"], "voice": charon,
                "audio": f"{NARRATION_DIR}/preview.wav", "sfx": False,
                "src": "b1b/b1_support_texts.json → preview"}
    if label == "Key phrases intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["key_phrases_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/key_phrases_intro_charon.wav", "sfx": False,
                "src": "shared_narration.FIXED_ENGLISH_TEXTS['key_phrases_intro'](固定テンプレート音声)"}
    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        kp = kp_by_rank[rank]
        en = kp["used_form"]
        ja = kp["japanese_gloss"]
        ja_tts = kp.get("japanese_gloss_tts", ja)
        text = f"EN: {en}<br>JA(表示): {ja}" + ("" if ja_tts == ja else f"<br>JA(TTS用): {ja_tts}")
        return {"text": text, "voice": "Aoede(EN)/Charon(JA)",
                "audio": (f"{NARRATION_DIR}/kp{rank}_en.wav", f"{NARRATION_DIR}/kp{rank}_ja_charon.wav"),
                "sfx": False, "src": f"b1b/key_phrases/keywords_canonicalized.json → items[{rank - 1}]"}
    if label == "Full story intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["full_story_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/full_story_intro_charon.wav", "sfx": False,
                "src": "shared_narration.FIXED_ENGLISH_TEXTS['full_story_intro'](固定テンプレート音声)"}
    if label.startswith("Comment 1 "):
        return {"text": support_texts["comment_1"], "voice": charon,
                "audio": f"{NARRATION_DIR}/comment_1.wav", "sfx": False,
                "src": "b1b/b1_support_texts.json → comment_1"}
    if label.startswith("Comment 2 "):
        return {"text": support_texts["comment_2"], "voice": charon,
                "audio": f"{NARRATION_DIR}/comment_2.wav", "sfx": False,
                "src": "b1b/b1_support_texts.json → comment_2"}
    if label.startswith("Comment 3 "):
        return {"text": support_texts["comment_3"], "voice": charon,
                "audio": f"{NARRATION_DIR}/comment_3.wav", "sfx": False,
                "src": "b1b/b1_support_texts.json → comment_3"}
    if label.startswith("Comment 4 "):
        return {"text": support_texts["comment_4"], "voice": charon,
                "audio": f"{NARRATION_DIR}/comment_4.wav", "sfx": False,
                "src": "b1b/b1_support_texts.json → comment_4"}
    if label.startswith("Hook Part 1"):
        return {"text": parts["part1"], "voice": "Aoede",
                "audio": f"{NARRATION_DIR}/full_story_part1.wav", "sfx": False,
                "src": "b1b/parts.json → part1"}
    if label.startswith("Hook Part 2"):
        return {"text": parts["part2"], "voice": "Aoede",
                "audio": f"{NARRATION_DIR}/full_story_part2.wav", "sfx": False,
                "src": "b1b/parts.json → part2"}
    if label.startswith("Narrator: One Voice heading"):
        return {"text": parts["point_one_heading"], "voice": "Aoede (Narrator)",
                "audio": f"{NARRATION_DIR}/point_one_heading.wav", "sfx": False,
                "src": "b1b/parts.json → point_one_heading"}
    if label.startswith("Voice A body"):
        return {"text": parts["point_one_body"], "voice": voice_a,
                "audio": f"{NARRATION_DIR}/point_one.wav", "sfx": False,
                "src": "b1b/parts.json → point_one_body"}
    if label.startswith("Narrator: Another Voice heading"):
        return {"text": parts["point_two_heading"], "voice": "Aoede (Narrator)",
                "audio": f"{NARRATION_DIR}/point_two_heading.wav", "sfx": False,
                "src": "b1b/parts.json → point_two_heading(本タスクで再生成、承認記録: "
                       "b1b/audit/user_approval_record_heading_regen_03.json)"}
    if label.startswith("Voice B body"):
        return {"text": parts["point_two_body"], "voice": voice_b,
                "audio": f"{NARRATION_DIR}/point_two.wav", "sfx": False,
                "src": "b1b/parts.json → point_two_body"}
    if label.startswith("Tension:"):
        return {"text": parts["tension_body"], "voice": "Aoede",
                "audio": f"{NARRATION_DIR}/tension_reflection.wav", "sfx": False,
                "src": "b1b/parts.json → tension_body(Trial-08由来、text hash確認のうえ再利用)"}
    if label.startswith("Closing:"):
        return {"text": parts["in_one_line"], "voice": "Aoede",
                "audio": f"{NARRATION_DIR}/in_one_line.wav", "sfx": False,
                "src": "b1b/parts.json → in_one_line"}
    return {"text": "【未取得】このラベルに対応するscript textを本スクリプトのマッピングで特定できませんでした。",
            "voice": None, "audio": None, "sfx": False, "src": "N/A"}


def build_full_player_html_03(assemble_summary: dict, timeline: list, parts: dict, support_texts: dict,
                               voice_a: str, voice_b: str, heading_regen_summary: dict) -> str:
    kp_data = load_json(f"{OUT_B1_DIR}/key_phrases/keywords_canonicalized.json")
    kp_by_rank = {item["rank"]: item for item in kp_data["items"]}

    abs_url = player_common.abs_file_url

    rows = []
    for entry in timeline:
        label = entry["part"]
        if label.startswith("pause_"):
            continue  # (l)は「各音声の再生ボタンと対応script」が対象、無音pauseは行を作らない
        info = _row_info(label, parts, support_texts, voice_a, voice_b, kp_by_rank, entry["duration_seconds"])
        sec = entry["start_seconds"]
        voice_disp = info["voice"] or ("SFX" if info["sfx"] else "—")
        if info["sfx"]:
            audio_html = "—"
        elif isinstance(info["audio"], tuple):
            audio_html = player_common.render_single_audio_html(tuple(abs_url(p) for p in info["audio"]))
        elif info["audio"]:
            audio_html = player_common.render_single_audio_html(abs_url(info["audio"]))
        else:
            audio_html = "—"
        # PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11(ユーザー決定
        # 2026-09-08): 標準formatからSource列を削除(info["src"]は本タスク以前の
        # 出典情報として引き続き_row_info内に保持するが、標準テーブルには出さない)。
        rows.append(player_common.render_timeline_row(
            sec, label, voice_disp, info["text"], audio_html,
            missing="未取得" in info["text"]))
    timeline_table = player_common.render_timeline_table(rows)

    kp_rows = []
    for rank in sorted(kp_by_rank):
        kp = kp_by_rank[rank]
        kp_rows.append(f'<tr><td>{rank}</td><td>{kp["used_form"]}</td><td>{kp["japanese_gloss"]}</td>'
                        f'<td>{kp.get("japanese_gloss_tts", kp["japanese_gloss"])}</td>'
                        f'<td>{kp.get("qa_overall_status")}</td></tr>')
    kp_table = ('<table class="kp"><thead><tr><th>#</th><th>English(used_form)</th><th>表示用gloss</th>'
                '<th>TTS用テキスト</th><th>redundancy QA</th></tr></thead>'
                f'<tbody>{"".join(kp_rows)}</tbody></table>')

    heading_note = (
        f"point_two_heading再生成(本タスク): status="
        f"{heading_regen_summary['generate_result_status']}、"
        f"cost_delta={heading_regen_summary['cost_delta_jpy_this_call']} JPY、"
        f"承認記録=audit/user_approval_record_heading_regen_03.json。"
    )

    episode_audio_url = abs_url(assemble_summary["out_path"])
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03 player</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03</h1>
<p class="note">
完成episode(1本化wav、Standard同期、B1のみ。A2は本Trialの対象外)。
duration={assemble_summary['duration_seconds']}s peak={assemble_summary['peak']}
clipping={assemble_summary['clipping_detected']}
headroom_safety_valve_applied={assemble_summary['headroom_safety_valve']['applied']}。
voice_a={voice_a} / voice_b={voice_b}(Narrator見出しは全てAoede固定)。{heading_note}
各行に「Seek(その開始秒へ、上部episode音声をseek)」「Segment名+voice」「実際に読み上げられたscript
(SFXは"効果音(読み上げなし)"と明記)」「個別音声」を同一行に配置(視線移動・長スクロール照合なし)。
標準player形式(PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11、ユーザー決定
2026-09-08): Source列は削除し、その分Script列の幅を広げ、個別音声の幅も拡大した
(再生ボタンが「…」メニューに隠れないようにするため)。
</p>

<h2>Episode audio</h2>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_audio_url}"></audio>

<h2>タイムライン・全スクリプト(収録順、同一行にSeek+voice+script)</h2>
{timeline_table}

<h2>Key Phrase表(詳細、英語+日本語gloss)</h2>
{kp_table}

</body></html>
"""
    out_path = f"{OUT_DIR}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


def run_assembly_and_player(heading_regen_summary: dict) -> dict:
    voice_resolution = load_json(f"{OUT_DIR}/audit/voice_resolution.json")
    voice_a, voice_b = voice_resolution["voice_a"], voice_resolution["voice_b"]

    assemble_summary = trial09.run_voices_assembly(voice_a, voice_b)  # Production+Trial専用timeline、無変更
    print(f"[HEADING-REGEN-03] Assembly status={assemble_summary.get('status')}")
    if assemble_summary.get("status") != "OK":
        return {"assemble_summary": assemble_summary, "player_path": None}

    timeline = load_json(f"{OUT_B1_DIR}/audit/timeline.json")
    parts = load_json(f"{OUT_B1_DIR}/parts.json")
    support_texts = load_json(f"{OUT_B1_DIR}/b1_support_texts.json")
    player_path = build_full_player_html_03(
        assemble_summary, timeline, parts, support_texts, voice_a, voice_b, heading_regen_summary)
    print(f"[HEADING-REGEN-03] player.html: {os.path.abspath(player_path)}")
    return {"assemble_summary": assemble_summary, "player_path": player_path,
            "voice_a": voice_a, "voice_b": voice_b, "timeline": timeline}


def main() -> None:
    heading_summary = regenerate_point_two_heading()
    if heading_summary["generate_result_status"] != "OK":
        print("[HEADING-REGEN-03] STOP: point_two_headingの再生成がstatus=OKになりませんでした"
              f"(status={heading_summary['generate_result_status']})。Assemblyは実施せず、"
              "USER_DECISION_REQUIREDとして報告します(2回目の承認は求めません)。")
        return
    result = run_assembly_and_player(heading_summary)
    save_json(f"{OUT_B1_DIR}/audit/heading_regen_03_full_run_summary.json", {
        "heading_regen": heading_summary, "assembly": result.get("assemble_summary"),
        "player_path": result.get("player_path"),
    })
    print("[HEADING-REGEN-03] 完了。")


if __name__ == "__main__":
    main()
