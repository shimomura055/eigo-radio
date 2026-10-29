# ============================================================
# er019_fx_moon_title_approved_audio_reuse_01.py
# 管理ID: FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03(2026-10-29)
# ============================================================
# ユーザー承認済み音声(run_ms_03 Std日本語題 attempt 2, sha256=f0c4b415...)を、同一canonical_textの
# run_reselect_01 Std日本語題segmentへ再利用する(TTS/ASR API呼出0)。
# 根拠: ユーザー原文§2-3「承認済みの音声について、同じ内容の再判断をユーザーに求めない」
#   (docs/pm/delegation_log/2026-10-29_FX-MOON-SHRINKING-RESELECT-REMAKE-01_USER_02.md)、
#   承認記録 ms_03 a2/audit/fxnr10_user_approval_record.json(scope="this single segment / attempt 2 only; NOT a general ASR-check exemption")。
# 先例(同一手順): er019_fx_moon_title_individual_approval_01.py(record_human_approval+review_lock RESOLVED/HUMAN_APPROVED+採用wav配置)。
# 新Gate・flag・迂回・例外コードは作らない。sha照合とcanonical_text sha照合に失敗したら何も書かず中断する。
import hashlib, json, os, shutil, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
import er003_v1_n3_01_assemble as asm

BASE = "er019_output/family_x_audio_production_wiring_01"
SRC_RUN = f"{BASE}/moon_shrinking__run_ms_03"
RUN = f"{BASE}/moon_shrinking__run_reselect_01"
SRC_WAV = f"{SRC_RUN}/a2/narration/attempts/japanese_title_attempt2_customb8f0ff16.wav"
SRC_REC = f"{SRC_RUN}/a2/audit/fxnr10_user_approval_record.json"
A2 = f"{RUN}/a2"
DST = f"{A2}/narration/japanese_title.wav"
RESULTS = f"{A2}/audit/tts_generation_results.json"
LOCK = f"{A2}/audit/review_lock_state.json"
USER_MD = "docs/pm/delegation_log/2026-10-29_FX-MOON-SHRINKING-RESELECT-REMAKE-01_USER_02.md"
SEG = "japanese_title"
APPROVED_SHA = "f0c4b41580d30e2da496a818a55ec0bbd012af8bbd7bfc39c47913da6eed6865"
APPROVED_CANON_SHA = "b02b1f603bf132f29d5d72db2d0dd8bcbe8d246b741497dccdce325bc9fbad16"
APPROVED_BY = ("user(2026-10-25 listening, run_ms_03 Std japanese_title attempt 2 adopted; "
               "reused sha-identical in run_reselect_01 per user 2026-10-29 USER_02 s2-3)")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def lj(p):
    return json.load(open(p, encoding="utf-8"))


def sj(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)


def main(apply: bool):
    rec = lj(SRC_REC)
    assert rec["adopted_audio_sha256"] == APPROVED_SHA, "承認記録のshaが想定と違う"
    assert rec["canonical_text_sha256"] == APPROVED_CANON_SHA
    assert rec["scope"].startswith("this single segment / attempt 2 only")
    src_sha = sha(SRC_WAV)
    assert src_sha == APPROVED_SHA, f"承認済みwavのshaが承認記録と不一致: {src_sha}"
    res = lj(RESULTS)
    ent = res["segments"][SEG]
    canon = ent["canonical_text"]
    canon_sha = hashlib.sha256(canon.encode("utf-8")).hexdigest()
    assert canon_sha == APPROVED_CANON_SHA, f"canonical_text不一致: {canon_sha}"
    lock = lj(LOCK)
    le = lock[SEG]
    assert le["state"] in ("HUMAN_REVIEW_REQUIRED", "RESOLVED"), le["state"]
    pre_sha = sha(DST)
    print("src_sha(approved)", src_sha, "canon_sha", canon_sha, "dst_pre_sha", pre_sha, "lock_state", le["state"], "status", ent.get("status"))
    if not apply:
        print("DRY-RUN: 照合PASS。書込みなし")
        return
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    for p in (RESULTS, LOCK):
        b = p.replace(".json", ".pre_fxms_reuse_approval_backup.json")
        if not os.path.exists(b):
            shutil.copyfile(p, b)
    # 採用wavを配置(置換前=attempt 3 fallbackはattempts/に保存済み)
    shutil.copyfile(SRC_WAV, DST)
    assert sha(DST) == APPROVED_SHA
    # attemptsへも承認済みwavの由来を残す(元attempt群は無改変)
    asm.record_human_approval(A2, SEG, canon, approved_by=APPROVED_BY)
    if le["state"] == "HUMAN_REVIEW_REQUIRED":
        le["prior_state"] = "HUMAN_REVIEW_REQUIRED"
        le["prior_final_status"] = le.get("final_status")
        le["state"] = "RESOLVED"
        le["final_status"] = "HUMAN_APPROVED"
        le["updated_at"] = now
        le["adopted_attempt_audio_path"] = SRC_WAV
        le["adopted_audio_sha256"] = APPROVED_SHA
        le["reason"] = ("承認済み音声の再利用(2026-10-29、FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03)。run_ms_03 Std日本語題 attempt 2"
                        "(sha256=f0c4b415...)はユーザー試聴OK・個別採用済み(2026-10-25)。同一canonical_text(sha b02b1f60...)・同一Voice/styleの"
                        "本runへsha照合のうえ再利用。本run自身の3 attempt(ASR NG記録=last_attempts_log)は保存。TTS/ASR再生成0。"
                        f"一般的なASR検査免除ではない。原文={USER_MD}")
    lock[SEG] = le
    sj(LOCK, lock)
    ent["FXMS_REUSE_APPROVAL_NOTE"] = (
        f"[{now}] 承認済み音声の再利用: ms_03 attempt 2(sha256={APPROVED_SHA})をnarration/japanese_title.wavへ配置"
        f"(置換前=本run attempt 3 minimal_fallback sha256={pre_sha})。本runのASR NG(attempts_log)は正直な記録として維持。"
        f"TTS/ASR再生成0。一般仕様ではない。原文={USER_MD}。承認記録={SRC_REC}")
    ent["adopted_attempt_audio_path"] = SRC_WAV
    ent["adopted_audio_sha256"] = APPROVED_SHA
    res["segments"][SEG] = ent
    sj(RESULTS, res)
    out = {"segment": SEG, "approved_by": APPROVED_BY, "recorded_at": now, "reused_from_run": SRC_RUN,
           "source_approval_record": SRC_REC, "source_approval_scope": rec["scope"],
           "adopted_audio_sha256": APPROVED_SHA, "replaced_audio_sha256_before": pre_sha,
           "canonical_text": canon, "canonical_text_sha256": canon_sha,
           "user_statement_source": USER_MD,
           "asr_ng_records_preserved": [f"{A2}/audit/review_lock_state.pre_fxms_reuse_approval_backup.json",
                                        f"{A2}/audit/tts_generation_results.json segments.{SEG}.attempts_log",
                                        f"{A2}/narration/attempts/japanese_title_attempt{{1,2,3}}_*.wav/json",
                                        "er011_output/attempt_history.jsonl", "er007_output/ja_asr_cascade_01/human_review_queue.jsonl"],
           "scope": ("reuse of the sha-identical user-approved audio (run_ms_03 attempt 2) for the same canonical_text; "
                     "NOT a general ASR-check exemption; no TTS/ASR call")}
    sj(f"{A2}/audit/fxms_reuse_approval_record.json", out)
    print("done", now)


if __name__ == "__main__":
    main(apply=("--apply" in sys.argv))
