# ============================================================
# er011_discovery_generalization_towels_trial_11_audio_03_b1b_individual_approval_and_assemble_01.py
# 管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-03-B1B-APPROVAL-AND-ASSEMBLY
# ============================================================
# 背景: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11のB1B
# `full_story_part1`は、6/6take(original 3take + resume 3take)とも
# 自動ASR検証(TRUE_CONTENT_MISMATCH)に合格しなかった。take5
# (resume#2、`full_story_part1_attempt5_englishstyleprefixwidemargin.wav`)
# は内容ほぼ完全一致で、差異はcanonical「has dried」(現在完了)がASRでは
# 「had dried」(過去完了)と書き起こされる点のみ(2箇所)。
#
# ユーザー決定(2026-09-12、原文):
#   「試聴しました。`has dried / had dried`は、hasの子音部分が弱く、
#   どちらとも聞こえる微妙な音です。今回はtake5でOKとします。今回の
#   take5に対する個別Human Approvalとして処理してください。一般仕様と
#   して「has/had差を許容する」という意味ではありません。」
#
# 本スクリプトが行うこと(既存Production関数を無変更のまま呼ぶだけ、
# 新しいGate・閾値・retry仕様・一般化ルールの追加なし):
#   1. take5(full_story_part1_attempt5)を narration/full_story_part1.wav
#      へ採用し、既存の人間承認メカニズム`record_human_approval()`
#      (er003_v1_n3_01_assemble.py)で個別承認として記録する。
#   2. review_lock_state.json のfull_story_part1エントリをRESOLVEDへ
#      更新する(この1segment・1takeに対する個別承認であることを
#      reasonへユーザー原文で明記)。
#   3. tts_generation_results.json を「実際に起きたこと」に同期する:
#        - full_story_part1: resume round(take4-6)の実attempt履歴を
#          追記し(originalの3件は無変更)、個別Human Approval注記を
#          追加する(status自体はSTOPPEDのまま、正直な記録)。
#        - full_story_part2: OPEN-121-REPETITION-QA-NUMBER-WORD-
#          EQUIVALENCE-PRODUCTION-FIX-01により、attempt2/3の
#          repetition_qa誤flagが解消され実際にはverified=Trueだった
#          ことが判明した(review_lock_state.jsonは既にRESOLVED済み、
#          今回はtts_generation_results.json側を同じ結論へ同期する
#          のみ)。TTS再生成は一切行わない。
#   4. 事前にtts_generation_results.jsonを
#      tts_generation_results.pre_sync_backup.jsonへバックアップする。
#   5. 既存script(er011_discovery_generalization_towels_trial_11_audio_
#      run.py)のassembly_stage("b1b")(stage_assemble_b1 + Audio
#      Validation Gate opt-in確認、無変更)を実行する。
#   6. B1B単体のplayer.html(既存player_stage()のB1B部分ロジックを
#      再利用、A2側run_summary_assemble.jsonが無くても動く単一level版)
#      と、既存プロジェクトに前例のあるsoundfile MP3書き出し
#      (er003_v1_b1_scaffold_audio_01_generate.py参照)による最終mp3を
#      b1b/assembled/ へ生成する。
#
# 新規TTS/ASR API呼び出しは一切行わない(¥0)。Production/Prompt/共有
# module/registry/SSOT編集・Git操作は一切行わない。A2は本スクリプトの
# 対象外(Assembly禁止、UDR#11待ち)。
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er003_v1_n3_01_assemble as asm
import er011_discovery_generalization_towels_trial_11_audio_run as run
import audio_review_player as arp
import er003_b1_p9a_audio as p9a

THEME_ID = "discovery_generalization_towels_trial_11"
OUT_DIR = f"er011_output/{THEME_ID}"
B1B_DIR = f"{OUT_DIR}/b1b"
NARRATION_DIR = f"{B1B_DIR}/narration"
ATTEMPTS_DIR = f"{NARRATION_DIR}/attempts"
AUDIT_DIR = f"{B1B_DIR}/audit"
RESULTS_PATH = f"{AUDIT_DIR}/tts_generation_results.json"
BACKUP_PATH = f"{AUDIT_DIR}/tts_generation_results.pre_sync_backup.json"
LOCK_PATH = f"{AUDIT_DIR}/review_lock_state.json"
RESUME04_PATH = f"{AUDIT_DIR}/human_review_resume_04_results.json"
THIS_OUT_DIR = f"{AUDIT_DIR}/audio_03_b1b_individual_approval_and_assemble_01"

USER_APPROVAL_QUOTE = (
    "試聴しました。`has dried / had dried`は、hasの子音部分が弱く、どちらとも"
    "聞こえる微妙な音です。今回はtake5でOKとします。今回のtake5に対する個別"
    "Human Approvalとして処理してください。一般仕様として「has/had差を許容"
    "する」という意味ではありません。"
)

TAKE5_ATTEMPT_PATH = f"{ATTEMPTS_DIR}/full_story_part1_attempt5_englishstyleprefixwidemargin.wav"
FULL_STORY_PART1_WAV = f"{NARRATION_DIR}/full_story_part1.wav"


def log(msg):
    print(msg)


def sha256_of(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def step0_backup():
    if os.path.exists(BACKUP_PATH):
        log(f"[Step0] バックアップは既に存在します(スキップ): {BACKUP_PATH}")
        return
    data = load_json(RESULTS_PATH)
    save_json(BACKUP_PATH, data)
    log(f"[Step0] tts_generation_results.json を {BACKUP_PATH} へバックアップしました。")


def step1_approve_take5_and_swap_wav():
    assert os.path.exists(TAKE5_ATTEMPT_PATH), f"take5音声が見つかりません: {TAKE5_ATTEMPT_PATH}"
    take5_sha = sha256_of(TAKE5_ATTEMPT_PATH)
    pre_sha = sha256_of(FULL_STORY_PART1_WAV) if os.path.exists(FULL_STORY_PART1_WAV) else None
    log(f"[Step1] 置き換え前 narration/full_story_part1.wav sha256={pre_sha}")
    log(f"[Step1] take5(attempt5)sha256={take5_sha}")

    import shutil
    shutil.copyfile(TAKE5_ATTEMPT_PATH, FULL_STORY_PART1_WAV)
    new_sha = sha256_of(FULL_STORY_PART1_WAV)
    assert new_sha == take5_sha
    log(f"[Step1] narration/full_story_part1.wav を take5(attempt5)で置き換え完了。sha256={new_sha[:16]}...")

    results = load_json(RESULTS_PATH)
    canonical_text = results["segments"]["full_story_part1"]["canonical_text"]

    # 既存の人間承認メカニズム(手書きJSON改変ではなく既存API経由)。
    asm.record_human_approval(B1B_DIR, "full_story_part1", canonical_text, approved_by="user")
    log(f"[Step1] record_human_approval(out_dir={B1B_DIR!r}, segment_key='full_story_part1') 呼び出し完了。"
        f"audit/human_approved_segments.jsonへ記録。")
    return {"pre_sha256": pre_sha, "adopted_sha256": new_sha, "canonical_text": canonical_text}


def step2_update_review_lock_state():
    lock = load_json(LOCK_PATH)
    entry = lock["full_story_part1"]
    if entry["state"] == "RESOLVED" and entry.get("final_status") == "HUMAN_APPROVED":
        log("[Step2] review_lock_state.json は既にRESOLVED/HUMAN_APPROVED済みのためスキップします。")
        return entry
    assert entry["state"] == "HUMAN_REVIEW_REQUIRED", (
        f"想定外の初期state: {entry['state']}(HUMAN_REVIEW_REQUIREDを想定)")
    entry["state"] = "RESOLVED"
    entry["final_status"] = "HUMAN_APPROVED"
    entry["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    entry["adopted_attempt_audio_path"] = TAKE5_ATTEMPT_PATH
    entry["reason"] = (
        "個別Human Approval(2026-09-12、管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-"
        "TOWELS-TRIAL-11-AUDIO-03-B1B-APPROVAL-AND-ASSEMBLY)。6/6takeとも自動ASR"
        "検証はTRUE_CONTENT_MISMATCH(take5/6はcanonical『has dried』がASRでは"
        "『had dried』)。ユーザーが実際に試聴し、take5(resume#2、"
        f"{TAKE5_ATTEMPT_PATH})を個別に承認。ユーザー原文: 「{USER_APPROVAL_QUOTE}」"
        "一般仕様として『has/had差を許容する』という意味ではない(この1segment・"
        "1takeに対する個別承認のみ)。"
    )
    save_json(LOCK_PATH, lock)
    log("[Step2] review_lock_state.json の full_story_part1 を RESOLVED / HUMAN_APPROVED へ更新しました。")
    return entry


def step3a_sync_full_story_part1_results():
    results = load_json(RESULTS_PATH)
    entry = results["segments"]["full_story_part1"]
    assert entry["status"] == "STOPPED"

    if not os.path.exists(RESUME04_PATH):
        log("[Step3a] human_review_resume_04_results.json が見つからないため、resume round統合をスキップします。")
        resume_attempts = []
    else:
        resume_data = load_json(RESUME04_PATH)
        resume_entry = resume_data["full_story_part1"]
        resume_attempts = resume_entry["attempts_log"]

    original_count = len(entry["attempts_log"])
    already_merged = any(
        a.get("attempt_audio_path", "").endswith("full_story_part1_attempt4_englishstyleprefixwidemargin.wav")
        for a in entry["attempts_log"]
    )
    if already_merged:
        log("[Step3a] resume round(take4-6)は既にattempts_logへ統合済みのため、再統合はスキップします。")
    else:
        for i, a in enumerate(resume_attempts):
            merged = dict(a)
            merged["attempt"] = original_count + i + 1  # 4,5,6(実際のtake番号)へ採番し直す
            entry["attempts_log"].append(merged)
        log(f"[Step3a] resume round(take4-6)の実attempt履歴{len(resume_attempts)}件をattempts_logへ追記しました。")

    entry["adopted_attempt_audio_path"] = TAKE5_ATTEMPT_PATH
    entry["TRIAL11_AUDIO03_B1B_HUMAN_APPROVAL_NOTE"] = (
        f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-"
        "AUDIO-03-B1B-APPROVAL-AND-ASSEMBLY: 6/6take(original take1-3+resume take4-6)とも自動ASR"
        "検証はTRUE_CONTENT_MISMATCHのまま(status=STOPPEDは正直な記録として維持)。ユーザーが"
        f"take5({TAKE5_ATTEMPT_PATH})を実際に試聴し、既存メカニズムrecord_human_approval()で"
        f"個別承認した。ユーザー原文: 「{USER_APPROVAL_QUOTE}」一般仕様として「has/had差を許容する」"
        "という意味ではない(この1segment・1takeに対する個別承認のみ、新規TTS/ASR呼び出しなし)。"
        "narration/full_story_part1.wavはtake5(attempt5)で置き換え済み。"
    )
    results["segments"]["full_story_part1"] = entry
    save_json(RESULTS_PATH, results)
    log("[Step3a] tts_generation_results.json の full_story_part1 を同期しました(status=STOPPEDのまま、"
        "個別Human Approval注記+resume round履歴を追加)。")
    return entry


def step3b_sync_full_story_part2_results():
    results = load_json(RESULTS_PATH)
    entry = results["segments"]["full_story_part2"]
    if entry.get("status") == "OK":
        log("[Step3b] full_story_part2は既にstatus=OKへ同期済みのためスキップします。")
        return entry
    assert entry["status"] == "STOPPED"

    lock = load_json(LOCK_PATH)
    lock_entry = lock["full_story_part2"]
    assert lock_entry["state"] == "RESOLVED" and lock_entry.get("final_status") == "OK", (
        "review_lock_state.jsonのfull_story_part2がRESOLVED/OKであることを前提とします"
        "(OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01で既に更新済みのはず)。")

    adopted_path = lock_entry["adopted_attempt_audio_path"]
    assert adopted_path.endswith("full_story_part2_attempt2_englishstyleprefixwidemargin.wav")

    attempts_log = entry["attempts_log"]
    adopted_attempt = next(a for a in attempts_log if a["attempt_audio_path"] == adopted_path)

    # OPEN-121修正後の再判定結果(方式A: canonical_repeat_count=2/intentional=True/
    # flagged=False、方式D・D'は元々flagged=Falseのまま無変更)。数値は
    # OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01_REPORT.md
    # 5節および同タスクのscratchpad(part2_rejudge_results.json)の再計算結果を転記
    # (新規ASR呼び出しなし、¥0)。
    def _corrected_evidence(old_evidence):
        new_evidence = json.loads(json.dumps(old_evidence))  # deep copy
        new_evidence["flagged"] = False
        m = new_evidence["method_a_ngram"]["matches"][0]
        m["canonical_repeat_count"] = 2
        m["intentional"] = True
        m["flagged"] = False
        new_evidence["method_a_ngram"]["flagged"] = False
        new_evidence["method_a_ngram"]["flagged_matches"] = []
        return new_evidence

    for a in attempts_log:
        if a["attempt_audio_path"] in (
            f"{ATTEMPTS_DIR}/full_story_part2_attempt2_englishstyleprefixwidemargin.wav",
            f"{ATTEMPTS_DIR}/full_story_part2_attempt3_englishstyleprefixwidemargin.wav",
        ):
            a["repetition_qa_evidence"] = _corrected_evidence(a["repetition_qa_evidence"])
            a["verified"] = True

    new_entry = {
        "status": "OK",
        "text": entry["canonical_text"],
        "path": f"{NARRATION_DIR}/full_story_part2.wav",
        "asr_verified": True,
        "asr_text": adopted_attempt["asr_text"],
        "attempts_log": attempts_log,
        "instruction_type": adopted_attempt["instruction_type"],
        "trim_info": adopted_attempt["trim_info"],
        "clipping_detected": False,
        "audio_classification": adopted_attempt["audio_classification"],
        "connected_speech_info": adopted_attempt["connected_speech_info"],
        "disfluency_checked": adopted_attempt.get("disfluency_checked", False),
        "disfluency_evidence": adopted_attempt.get("disfluency_evidence"),
        "repetition_qa_checked": True,
        "repetition_qa_evidence": adopted_attempt["repetition_qa_evidence"],
        "canonical_text": entry["canonical_text"],
        "TRIAL11_AUDIO03_B1B_SYNC_NOTE": (
            f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-"
            "AUDIO-03-B1B-APPROVAL-AND-ASSEMBLY: OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-"
            "PRODUCTION-FIX-01(2026-09-12)適用後の遡及再判定により、attempt2/3の repetition_qa "
            "誤flag(『after two months』の正規2回出現をcanonical_repeat_count=0と誤判定)が解消され"
            "verified=Trueだったことが判明。review_lock_state.jsonは既にRESOLVED/OK(採用attempt2)へ"
            "更新済み(別タスク)。本タスクはtts_generation_results.jsonを同じ結論へ同期したのみ"
            "(TTS再生成なし、ローカルfaster-whisper再実行のみ、¥0)。resume round(take4-6)の"
            "attempt5/6も同じ修正で内容一致がPASSしていたが、既存の採用規則(retry loop内で最初に"
            "verified=Trueとなる取り)によりattempt2(original round)を採用。"
        ),
    }
    results["segments"]["full_story_part2"] = new_entry
    save_json(RESULTS_PATH, results)
    log("[Step3b] tts_generation_results.json の full_story_part2 を status=OK へ同期しました"
        "(attempt2採用、repetition_qa_evidence補正)。")
    return new_entry


def step4_assembly():
    os.makedirs(THIS_OUT_DIR, exist_ok=True)
    result = run.assembly_stage("b1b")
    save_json(f"{THIS_OUT_DIR}/assembly_result.json", result)
    log(f"[Step4] Assembly(Gate OFF経路)結果: {result.get('gate_off_result')} / "
        f"Gate opt-in ON経路結果: {result.get('gate_opt_in_result', {}).get('gate_on_result')}")
    if result.get("gate_off_result") != "PASS" or result.get("gate_opt_in_result", {}).get("gate_on_result") != "PASS":
        raise RuntimeError(f"B1B Assembly/GateがPASSしませんでした: {result}")
    return result


def build_b1b_only_player_html(assemble_result: dict) -> dict:
    """既存player_stage()(er011_discovery_generalization_towels_trial_11_
    audio_run.py)はA2+B1B結合ページのみを生成し、A2側run_summary_assemble.json
    が無いと動かない。A2は本タスクの対象外(UDR#11待ち、Assembly禁止)のため、
    同じ既存部品(run.build_b1b_rows/audio_review_player)だけを使い、B1B単独の
    player.htmlを生成する(新しいレンダリング仕様の追加なし、既存関数の
    呼び出し範囲を絞っただけ)。"""
    b1b_rows, b1b_kp_table, b1b_parts, b1b_support = run.build_b1b_rows()
    b1b_audio_url = run.au(assemble_result["out_path"])
    with open(f"{B1B_DIR}/article.md", encoding="utf-8") as f:
        b1b_article_md = f.read()

    scoped_seek_script = """
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-audio-target]").forEach(function (container) {
    var audioId = container.getAttribute("data-audio-target");
    container.querySelectorAll("button.seek").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var a = document.getElementById(audioId);
        a.currentTime = parseFloat(btn.getAttribute("data-sec"));
        a.play();
      });
    });
  });
});
""".strip("\n")

    note = f"""
<p class="note">
このページはFAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-03-B1B-
APPROVAL-AND-ASSEMBLY(Trial扱い、Production配線なし)のB1B単独試聴用ページです。
full_story_part1のtake5は個別Human Approval採用(has/had差、一般仕様化ではない)。
full_story_part2はOPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01
の遡及再判定によりattempt2を採用。A2はcomment_2がUDR#11(表記ゆれ対策採用)待ちの
ため本ページには含まれない(Assembly未実行)。標準フォーマット
(audio_review_player.py、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11、
Source列なし)準拠。<b>Focus ModuleのProduction採用判断はこのTrialでは行っていません。</b>
</p>
<p class="note">
B1B: duration={assemble_result['duration_seconds']}s / peak={assemble_result['peak']} /
clipping={assemble_result['clipping_detected']}。
</p>
"""

    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-03-B1B</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-03 — タオル臭テーマ B1B(Discovery Focus Module Part A単独)</h1>
{note}

<div data-audio-target="episode_audio_b1b">
<h2>B1B — 「{run.esc(b1b_parts.get('title'))}」</h2>
<audio id="episode_audio_b1b" class="main" controls src="{b1b_audio_url}"></audio>
<h3>B1B タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h3>
{arp.render_timeline_table(b1b_rows)}
<h3>B1B Key Phrase表</h3>
{b1b_kp_table}
<h3>B1B 記事全文(article.md)</h3>
<pre class="article">{run.esc(b1b_article_md)}</pre>
</div>

<script>
{scoped_seek_script}
</script>
</body>
</html>
"""
    player_out_path = f"{B1B_DIR}/assembled/player.html"
    with open(player_out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    abs_path = os.path.abspath(player_out_path).replace("\\", "/")
    log(f"[Step5] player.html 出力: {player_out_path}")
    log(f"[Step5] file:///{abs_path}")
    return {"player_html_path": player_out_path, "player_html_file_url": f"file:///{abs_path}"}


def step6_export_mp3(assemble_result: dict) -> dict:
    """既存プロジェクトに前例のあるsoundfile MP3書き出し
    (er003_v1_b1_scaffold_audio_01_generate.py: sf.write(path, data, sr,
    format="MP3"))を再利用し、既存Production assemble関数が出力するwavから
    最終mp3を追加生成する(Production関数自体は無変更、既存wav出力に加えて
    派生artifactを1つ増やすだけ)。"""
    import soundfile as sf
    wav_path = assemble_result["out_path"]
    data, sr = sf.read(wav_path)
    mp3_path = f"{B1B_DIR}/assembled/English_Your_Way_B1B_{THEME_ID.upper()}.mp3"
    sf.write(mp3_path, data, sr, format="MP3")
    log(f"[Step6] 最終mp3書き出し完了: {mp3_path}")
    return {"mp3_path": mp3_path}


def main():
    os.makedirs(THIS_OUT_DIR, exist_ok=True)
    step0_backup()
    approval = step1_approve_take5_and_swap_wav()
    lock_entry = step2_update_review_lock_state()
    part1_entry = step3a_sync_full_story_part1_results()
    part2_entry = step3b_sync_full_story_part2_results()
    assemble_result = step4_assembly()
    player = build_b1b_only_player_html(assemble_result)
    mp3 = step6_export_mp3(assemble_result)

    summary = {
        "approval": approval,
        "review_lock_entry": lock_entry,
        "part1_synced_entry_keys": list(part1_entry.keys()),
        "part2_synced_entry_status": part2_entry.get("status"),
        "assemble_result": assemble_result,
        "player": player,
        "mp3": mp3,
    }
    save_json(f"{THIS_OUT_DIR}/run_summary.json", summary)
    log("[main] 完了。詳細: " + f"{THIS_OUT_DIR}/run_summary.json")
    return summary


if __name__ == "__main__":
    main()
