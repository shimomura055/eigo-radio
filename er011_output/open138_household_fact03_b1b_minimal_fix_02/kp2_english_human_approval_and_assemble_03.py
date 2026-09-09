# ============================================================
# er011_output/open138_household_fact03_b1b_minimal_fix_02/
#   kp2_english_human_approval_and_assemble_03.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続、
# Fable修正指示3回目、A-FACT03-2=(a))
# ============================================================
# ユーザー決定(2026-09-09): kp2_english(Household B1B Key Phrase 2の
# 既存承認済み音声、ASR同音異義"crisper"/"CRISPR"でFAIL)はユーザー試聴OK。
# 既存Production承認経路(er003_v1_n3_01_assemble.record_human_approval()、
# ER-009-N1/OPEN-112 Subtask Eと同一関数)でHUMAN_APPROVEDを記録し、
# stage_assemble_b1()→Audio Validation Gate(既定OFF内蔵+opt-in
# required_structure ON個別呼び出し)まで確認する。
#
# 本scriptはProduction関数を一切変更せず読み取り専用importのみで使用する。
# 再生成・Ledger改変・SSOT編集は行わない。
from __future__ import annotations

import hashlib
import json
import os

import er003_v1_n3_01_assemble as asm
import er008_disfluency_qa_18 as dq18

OUT_ROOT = "er003_output/n3_01/household/fact03_fix_02"
B1_DIR = f"{OUT_ROOT}/b1b"
ORIGINAL_B1_DIR = "er003_output/n3_01/household/b1b"
THEME = {"theme_id": "household", "out_dir": OUT_ROOT}

APPROVAL_NOTE = (
    "2026-09-09 ユーザー試聴承認、A-FACT03-2(a)、ASR同音異義によるfalse "
    "reject、音声はbyte不変"
)
APPROVED_BY = "user_2026-09-09_HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02"


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def step1_sha256_precheck() -> dict:
    """narration/*.wavのうち、point_one以外の全segmentがoriginal b1bと
    byte一致していることを確認する(revision3aで書き換わったのは
    point_oneのみである前提の再確認、承認記録・Assembly実行前に行う)。"""
    result = {"matches": [], "mismatches": [], "missing_in_original": []}
    for name in sorted(os.listdir(f"{B1_DIR}/narration")):
        if not name.endswith(".wav") or "/attempts/" in name:
            continue
        cur_path = f"{B1_DIR}/narration/{name}"
        orig_path = f"{ORIGINAL_B1_DIR}/narration/{name}"
        if not os.path.exists(orig_path):
            result["missing_in_original"].append(name)
            continue
        cur_sha = _sha256(cur_path)
        orig_sha = _sha256(orig_path)
        entry = {"name": name, "current_sha256": cur_sha, "original_sha256": orig_sha}
        if cur_sha == orig_sha:
            result["matches"].append(entry)
        else:
            result["mismatches"].append(entry)
    result["match_count"] = len(result["matches"])
    result["mismatch_count"] = len(result["mismatches"])
    result["mismatch_names"] = [e["name"] for e in result["mismatches"]]
    return result


def step2_record_human_approval() -> dict:
    """kp2_englishのcanonical_textは、既存key phrase sub-entry仕様上
    canonical_text/textフィールドを持たない(ER-010-NO9-kp2_english
    one-off採用と同型)ため、text=""で記録する(既存パターン踏襲)。"""
    tts = _load(f"{B1_DIR}/audit/tts_generation_results.json")
    kp2_english_entry = tts["key_phrases"]["2"]["english"]
    assert kp2_english_entry["status"] == "STOPPED", \
        f"想定外: kp2_english status={kp2_english_entry['status']!r}(STOPPED以外)"
    canonical_text = kp2_english_entry.get("canonical_text") or kp2_english_entry.get("text") or ""

    asm.record_human_approval(B1_DIR, "kp2_english", canonical_text, approved_by=APPROVED_BY)

    approval_path = asm.human_approval_path(B1_DIR)
    approvals = _load(approval_path)
    approvals["kp2_english"]["note"] = APPROVAL_NOTE
    approvals["kp2_english"]["management_id"] = \
        "HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02"
    approvals["kp2_english"]["asr_homophone_evidence"] = (
        "audit/tts_generation_results.json key_phrases.2.english."
        "legacy_asr_reverify(canonical='crisper drawer', "
        "primary_asr='CRISPR drawer.', final_status=TRUE_CONTENT_MISMATCH, "
        "cascade_invoked=false: 短い2語フレーズのためentity_like/"
        "homophone_candidate判定が成立せずcascade対象外、"
        "topic_intro側の文脈込み発話ではSecondary ASRがcrisperと正しく"
        "書き起こしNORMALIZED_MATCH。同一音声・同一TTS生成の綴り相違に"
        "起因するfalse rejectと判断)"
    )
    with open(approval_path, "w", encoding="utf-8") as f:
        json.dump(approvals, f, ensure_ascii=False, indent=2)

    return {"approval_path": approval_path, "canonical_text": canonical_text,
            "recorded": approvals["kp2_english"]}


def step2b_disfluency_qa_kp2_english() -> dict:
    """kp2_englishはstatus=STOPPEDのまま(HUMAN_APPROVEDは承認記録側で別途
    成立)だが、Gateのdisfluency必須chek(`_english`サフィックス対象)は
    approval statusとは独立した別条件であり、continuation2(Fable修正
    指示2回目)で他12segmentへ適用したのと同じ既存Production関数
    (er008_disfluency_qa_18.check_segment_for_disfluency、faster-whisper
    ローカル実行、追加API課金なし)を、既存wav(narration/kp2_en.wav、
    byte不変)へそのまま事後適用する。TTS再生成は一切行わない。
    continuation2のlegacy_disfluency_qa_reapply.pyがstatus=="OK"を前提と
    していたのに対し、kp2_englishはSTOPPED+HUMAN_APPROVEDのため前提条件を
    status in ("OK","STOPPED")へ緩和して同一処理を適用する(処理内容自体は
    無変更)。"""
    wav_path = f"{B1_DIR}/narration/kp2_en.wav"
    tts = _load(f"{B1_DIR}/audit/tts_generation_results.json")
    entry = tts["key_phrases"]["2"]["english"]
    assert entry.get("status") == "STOPPED", f"想定外: status={entry.get('status')!r}"

    before_sha256 = _sha256(wav_path)
    evidence = dq18.check_segment_for_disfluency(wav_path, language="en", model_size="small")
    after_sha256 = _sha256(wav_path)
    assert before_sha256 == after_sha256, "kp2_en.wavがQA適用中に変化しました(禁止事項違反)"

    flagged = evidence["flagged"]
    entry["disfluency_checked"] = True
    entry["disfluency_evidence"] = evidence
    entry["disfluency_qa_retroactive_note"] = (
        "HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続、Fable修正指示"
        "3回目): 2026-08-17承認時点では存在しなかった現行Audio Validation Gate"
        "(ER-008-N8-FINAL-QA-HARDENING-21)のdisfluency QA必須化(_english"
        "サフィックスsegment対象)に対応するため、既存wav(byte不変)へ事後適用した"
        "証跡。TTS再生成は行っていない。statusフィールド自体はSTOPPEDのまま"
        "(HUMAN_APPROVEDはaudit/human_approved_segments.json側の別記録で成立)。"
    )
    entry["disfluency_qa_retroactive_status"] = "FAIL_FLAGGED_ADJACENT_REPETITION" if flagged else "PASS"

    with open(f"{B1_DIR}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(tts, f, ensure_ascii=False, indent=2, default=str)

    return {"wav_path": wav_path, "wav_sha256": before_sha256, "flagged": flagged,
            "word_count": evidence["word_count"], "transcript": evidence["transcript"],
            "repeats": evidence["repeats"], "method": evidence["method"],
            "result": "FAIL" if flagged else "PASS"}


def step3_gate_check_default() -> dict:
    """既定呼び出し(required_structureなし、OFF)と同一の経路を単独で
    実行し、結果(例外の有無・内容)を記録する。stage_assemble_b1()内部の
    load_b1_sources()が呼ぶものと同一関数・同一引数。"""
    try:
        asm.verify_episode_audio_validation_gate(B1_DIR, "B1")
        return {"status": "PASS"}
    except RuntimeError as e:
        return {"status": "BLOCKED", "error": str(e)}


def step4_gate_check_opt_in_structural() -> dict:
    """opt-in required_structure ON経路(OPEN-129)を個別に実行する。
    既存呼び出し元(stage_assemble_b1自体)はこの引数を渡さないため、
    Production挙動には影響しない診断専用の追加呼び出し。"""
    try:
        required_structure = asm.derive_a_family_required_structure("B1")
        asm.verify_episode_audio_validation_gate(B1_DIR, "B1", required_structure=required_structure)
        return {"status": "PASS"}
    except RuntimeError as e:
        return {"status": "BLOCKED", "error": str(e)}


def step5_attempt_assemble() -> dict:
    try:
        summary = asm.stage_assemble_b1(THEME)
        return {"status": "OK", "summary": summary}
    except RuntimeError as e:
        return {"status": "BLOCKED", "error": str(e)}


def main() -> None:
    out = {}
    out["step1_sha256_precheck"] = step1_sha256_precheck()
    out["step2_record_human_approval"] = step2_record_human_approval()
    out["step2b_disfluency_qa_kp2_english"] = step2b_disfluency_qa_kp2_english()
    out["step3_gate_check_default"] = step3_gate_check_default()
    out["step4_gate_check_opt_in_structural"] = step4_gate_check_opt_in_structural()
    out["step5_attempt_assemble"] = step5_attempt_assemble()

    result_path = ("er011_output/open138_household_fact03_b1b_minimal_fix_02/"
                   "kp2_english_human_approval_and_assemble_03_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(f"結果保存: {result_path}")
    print(f"sha256precheck: match={out['step1_sha256_precheck']['match_count']} "
          f"mismatch={out['step1_sha256_precheck']['mismatch_count']} "
          f"names={out['step1_sha256_precheck']['mismatch_names']}")
    print(f"kp2_english disfluency QA: {out['step2b_disfluency_qa_kp2_english']['result']}")
    print(f"gate_default: {out['step3_gate_check_default']['status']}")
    print(f"gate_opt_in_structural: {out['step4_gate_check_opt_in_structural']['status']}")
    print(f"assemble: {out['step5_attempt_assemble']['status']}")


if __name__ == "__main__":
    main()
