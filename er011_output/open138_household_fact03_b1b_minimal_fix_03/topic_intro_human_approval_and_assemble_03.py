# ============================================================
# er011_output/open138_household_fact03_b1b_minimal_fix_03/
#   topic_intro_human_approval_and_assemble_03.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03(OPEN-138、
# A-FACT03-4=(a))
# ============================================================
# ユーザー決定(2026-09-09、A-FACT03-4=(a)): topic_intro(Household B1B、
# 既存承認済み音声、8月生成時ASR FAIL x6、現行ASR cascadeで事後再照合
# PASS[NORMALIZED_MATCH、continuation2 = FIX-02 §12.3])を、既存の人間承認
# 経路(er003_v1_n3_01_assemble.record_human_approval()、kp2_english/
# Phase 1 Voice Bと同一関数、FIX-02継続3回目[§13]でkp2_englishに適用した
# のと同一パターン)でHUMAN_APPROVEDとして記録し、stage_assemble_b1()→
# Audio Validation Gate(既定OFF内蔵+opt-in required_structure ON個別
# 呼び出し)→player生成まで進める。
#
# 条件(委任文どおり): 既存topic_intro音声はbyte不変(TTS再生成なし) /
# statusフィールドの捏造なし(2026-08-17当時のSTOPPED記録のまま、生成時
# ASR PASS扱いへ書き換えない) / HUMAN_APPROVEDは今回のユーザー判断に基づく
# 正規承認経路として記録する(新policy採用ではない) / noteに「現行ASR
# cascadeによる事後再照合PASS」を明記する。
#
# 本scriptはProduction関数を一切変更せず読み取り専用importのみで使用する。
# 再生成・Ledger改変・SSOT編集は行わない。
from __future__ import annotations

import hashlib
import json
import os

import er003_v1_n3_01_assemble as asm

OUT_ROOT = "er003_output/n3_01/household/fact03_fix_02"
B1_DIR = f"{OUT_ROOT}/b1b"
ORIGINAL_B1_DIR = "er003_output/n3_01/household/b1b"
THEME = {"theme_id": "household", "out_dir": OUT_ROOT}

APPROVAL_NOTE = (
    "2026-09-09 ユーザー判断A-FACT03-4(a)、現行ASR cascadeによる事後再照合"
    "PASS(NORMALIZED_MATCH、§12.3)、当時attempt 1〜6はFAIL、音声byte不変"
)
APPROVED_BY = "user_2026-09-09_HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03"


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def step1_sha256_precheck() -> dict:
    """narration/*.wav(attempts/配下除く)のうち、point_one以外の全segmentが
    original b1bとbyte一致していることを、承認記録・Assembly実行前に
    再確認する(FIX-02継続3回目のstep1と同一処理、topic_intro.wav自身も
    ここで無変更であることを確認する)。"""
    result = {"matches": [], "mismatches": [], "missing_in_original": []}
    for name in sorted(os.listdir(f"{B1_DIR}/narration")):
        if not name.endswith(".wav"):
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
    """topic_introのcanonical_textは、この記録上は top-level canonical_text/
    textフィールドを持たない(status/reason/attempts_log/legacy_asr_reverify
    のみ、kp2_englishと同型)ため、text=""で記録する(既存パターン踏襲)。
    参考として、legacy_asr_reverify.canonical_textの実文言をnoteとは別の
    診断フィールドへ残す(hash対象には含めない、record_human_approval()の
    仕様に従いcanonical_text引数の値だけがhash対象)。"""
    tts = _load(f"{B1_DIR}/audit/tts_generation_results.json")
    topic_intro_entry = tts["segments"]["topic_intro"]
    assert topic_intro_entry["status"] == "STOPPED", \
        f"想定外: topic_intro status={topic_intro_entry['status']!r}(STOPPED以外)"
    assert topic_intro_entry["legacy_asr_reverify"]["final_status"] == "NORMALIZED_MATCH", \
        "想定外: 現行ASR cascade再照合がNORMALIZED_MATCHではない(FIX-02 12.3の前提が崩れている)"
    canonical_text = topic_intro_entry.get("canonical_text") or topic_intro_entry.get("text") or ""

    before_status = topic_intro_entry["status"]

    asm.record_human_approval(B1_DIR, "topic_intro", canonical_text, approved_by=APPROVED_BY)

    approval_path = asm.human_approval_path(B1_DIR)
    approvals = _load(approval_path)
    approvals["topic_intro"]["note"] = APPROVAL_NOTE
    approvals["topic_intro"]["management_id"] = \
        "HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-03"
    approvals["topic_intro"]["asr_reverify_evidence"] = (
        "audit/tts_generation_results.json segments.topic_intro."
        "legacy_asr_reverify(canonical_text=\"Today's topic is Your Crisper "
        "Drawer Has 2 Jobs\\u2014and One Tiny Switch Decides Which.\", "
        "final_status=NORMALIZED_MATCH, cascade_invoked=true: Primary#1/#2["
        "OpenAI]は引き続き'CRISPR'と書き起こしASR_VALIDATION_UNCERTAINだが、"
        "entity_like該当によりcascade続行、Secondary#1[Azure]が文脈込みで"
        "'crisper'と正しく書き起こしNORMALIZED_MATCHでPASS。当時[2026-08-17]"
        "の6回試行[attempts_log]は全てASR_verdict=FAIL[旧Primary単発判定の"
        "まま]、この事後再照合[現行cascade]は当時のFAIL記録を書き換えるもの"
        "ではない)"
    )
    with open(approval_path, "w", encoding="utf-8") as f:
        json.dump(approvals, f, ensure_ascii=False, indent=2)

    # statusフィールドが捏造されていないことをここで再確認する(書き込み後、
    # 同一ファイルを再読込)。
    tts_after = _load(f"{B1_DIR}/audit/tts_generation_results.json")
    after_status = tts_after["segments"]["topic_intro"]["status"]
    assert after_status == before_status == "STOPPED", (
        f"status捏造検知: before={before_status!r} after={after_status!r}"
    )

    return {"approval_path": approval_path, "canonical_text": canonical_text,
            "status_before": before_status, "status_after": after_status,
            "recorded": approvals["topic_intro"]}


def step3_gate_check_default() -> dict:
    try:
        asm.verify_episode_audio_validation_gate(B1_DIR, "B1")
        return {"status": "PASS"}
    except RuntimeError as e:
        return {"status": "BLOCKED", "error": str(e)}


def step4_gate_check_opt_in_structural() -> dict:
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


def step6_post_assemble_sha256_verify() -> dict:
    """Assembly後、narration配下の全wavが再度originalとの差分がpoint_one
    のみであることを確認する(Assembly自体はnarration wavを書き換えない
    read-only処理のはずだが、念のためAssembly後にも突合する)。"""
    return step1_sha256_precheck()


def main() -> None:
    out = {}
    out["step1_sha256_precheck"] = step1_sha256_precheck()
    out["step2_record_human_approval"] = step2_record_human_approval()
    out["step3_gate_check_default"] = step3_gate_check_default()
    out["step4_gate_check_opt_in_structural"] = step4_gate_check_opt_in_structural()
    out["step5_attempt_assemble"] = step5_attempt_assemble()
    out["step6_post_assemble_sha256_verify"] = step6_post_assemble_sha256_verify()

    result_path = ("er011_output/open138_household_fact03_b1b_minimal_fix_03/"
                   "topic_intro_human_approval_and_assemble_03_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(f"結果保存: {result_path}")
    print(f"sha256precheck: match={out['step1_sha256_precheck']['match_count']} "
          f"mismatch={out['step1_sha256_precheck']['mismatch_count']} "
          f"names={out['step1_sha256_precheck']['mismatch_names']}")
    print(f"status_before={out['step2_record_human_approval']['status_before']} "
          f"status_after={out['step2_record_human_approval']['status_after']}")
    print(f"gate_default: {out['step3_gate_check_default']['status']}")
    print(f"gate_opt_in_structural: {out['step4_gate_check_opt_in_structural']['status']}")
    print(f"assemble: {out['step5_attempt_assemble']['status']}")
    print(f"post_assemble_sha256: match={out['step6_post_assemble_sha256_verify']['match_count']} "
          f"mismatch={out['step6_post_assemble_sha256_verify']['mismatch_count']} "
          f"names={out['step6_post_assemble_sha256_verify']['mismatch_names']}")


if __name__ == "__main__":
    main()
