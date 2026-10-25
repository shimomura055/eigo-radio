# ============================================================
# er019_fx_moon_title_individual_approval_01.py
# 管理ID: FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_10 Task A
# ============================================================
# ユーザー判断(2026-10-25、原文=docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_06.md):
#   Family X『月は少しずつ縮んでいる？』Standard日本語タイトル3 attemptを試聴し「どれも問題ありません」。
#   attempt 2を採用。音声再生成は不要。ASR NG記録は改ざん・消去せず保存。一般的なASR検査免除ではない。
# 先例: er011_discovery_generalization_towels_trial_11_audio_03_b1b_individual_approval_and_assemble_01.py
#   (既存record_human_approval()+review_lock_state RESOLVED/HUMAN_APPROVED+採用wavをnarrationへ配置)。
# 新しいGate・flag・迂回・例外コードは作らない。TTS/ASR API呼出0。この1segment・1attemptの個別承認のみ。
import hashlib, json, os, shutil, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
import er003_v1_n3_01_assemble as asm

RUN = "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03"
A2 = f"{RUN}/a2"
NARR = f"{A2}/narration"
ATT2 = f"{NARR}/attempts/japanese_title_attempt2_customb8f0ff16.wav"
DST = f"{NARR}/japanese_title.wav"
RESULTS = f"{A2}/audit/tts_generation_results.json"
LOCK = f"{A2}/audit/review_lock_state.json"
USER_MD = "docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_06.md"
APPROVED_BY = "user(2026-10-25 listening, 3 attempts all OK; attempt 2 adopted)"
SEG = "japanese_title"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def lj(p):
    return json.load(open(p, encoding="utf-8"))


def sj(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)


def main():
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    for p in (RESULTS, LOCK):
        b = p.replace(".json", ".pre_fxnr10_approval_backup.json")
        if not os.path.exists(b):
            shutil.copyfile(p, b)
    res = lj(RESULTS)
    ent = res["segments"][SEG]
    canon = ent["canonical_text"]
    pre_sha = sha(DST)
    att_sha = sha(ATT2)
    shutil.copyfile(ATT2, DST)
    assert sha(DST) == att_sha
    print("pre_sha", pre_sha, "adopted_sha", att_sha)

    asm.record_human_approval(A2, SEG, canon, approved_by=APPROVED_BY)

    lock = lj(LOCK)
    le = lock[SEG]
    assert le["state"] in ("HUMAN_REVIEW_REQUIRED", "RESOLVED"), le["state"]
    if le["state"] == "HUMAN_REVIEW_REQUIRED":
        le["prior_state"] = "HUMAN_REVIEW_REQUIRED"
        le["prior_final_status"] = le.get("final_status")
        le["state"] = "RESOLVED"
        le["final_status"] = "HUMAN_APPROVED"
        le["updated_at"] = now
        le["adopted_attempt_audio_path"] = ATT2
        le["adopted_audio_sha256"] = att_sha
        le["reason"] = ("個別Human Approval(2026-10-25、FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_10)。ユーザーが3 attemptを試聴し"
                        "「どれも問題ありません」、attempt 2を採用(主・副ASRで数値一致=value_guard EQUAL)。ASRのNG記録"
                        "(attempt_history/last_attempts_log)は保存。この1segment・1attemptへの個別承認のみで、一般的なASR検査免除ではない。"
                        f"原文={USER_MD}")
    lock[SEG] = le
    sj(LOCK, lock)

    ent["FXNR10_HUMAN_APPROVAL_NOTE"] = (
        f"[{now}] 個別Human Approval: ユーザー試聴(3 attempt全て問題なし)・attempt 2採用。status={ent['status']}と各attemptのASR NG"
        f"(attempts_log)は正直な記録として維持。narration/japanese_title.wavはattempt 2(sha256={att_sha})で置換"
        f"(置換前=attempt 3 minimal_fallback sha256={pre_sha})。TTS/ASR再生成0。一般仕様ではない。原文={USER_MD}")
    ent["adopted_attempt_audio_path"] = ATT2
    ent["adopted_audio_sha256"] = att_sha
    res["segments"][SEG] = ent
    sj(RESULTS, res)

    rec = {"segment": SEG, "approved_by": APPROVED_BY, "approved_at": now, "user_statement_source": USER_MD,
           "adopted_attempt": 2, "adopted_audio_sha256": att_sha, "replaced_audio_sha256_before": pre_sha,
           "canonical_text": canon, "canonical_text_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
           "asr_ng_records_preserved": [f"{A2}/audit/review_lock_state.json (last_attempts_log)",
                                        f"{A2}/audit/tts_generation_results.json segments.{SEG}.attempts_log",
                                        "er011_output/attempt_history.jsonl", "human_review_queue.jsonl"],
           "scope": "this single segment / attempt 2 only; NOT a general ASR-check exemption; no TTS/ASR call"}
    sj(f"{A2}/audit/fxnr10_user_approval_record.json", rec)
    print("done", now)


if __name__ == "__main__":
    main()
