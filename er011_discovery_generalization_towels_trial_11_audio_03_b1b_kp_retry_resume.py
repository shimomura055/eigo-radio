# ============================================================
# er011_discovery_generalization_towels_trial_11_audio_03_b1b_kp_retry_resume.py
# 管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-02-RESUME(補助)
# ============================================================
# 背景: er011_discovery_generalization_towels_trial_11_audio_run.py stage=b1bの
# 初回実行で、B1B Key Phrase選定がKEY_WORDS_STRUCTURE_INVALID(display_phraseが
# 1〜5語規約に反する1件、単発のLLM出力ゆらぎ)でSTOPした(Support[Preview/
# Comment]は既にstatus=OKで完了済み)。
#
# run_key_phrase_selection()はmax_attempts=1の単発gateであり、既存Production
# 前例(er011_no18_b1_kp_retry_01.py「No.18 B1のKey Phrase選定retry」、
# er003_v1_iran01_a2_kp_retry.py等)と同一の手当てとして、実Production関数
# (audio_run.keyphrase_stage、無変更)をそのまま再呼び出しするだけの最小retry
# を行う(新しい仕様判断・閾値は一切追加しない)。成功後は同じ無変更の
# audio_run.tts_stage/lock_summary_stage/assembly_stageをb1bに対して実行する
# (support_stageは既に完了済みのため再実行しない)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_discovery_generalization_towels_trial_11_audio_03_b1b_kp_retry_resume.py
# ============================================================
from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er011_discovery_generalization_towels_trial_11_audio_run as run

MAX_RETRY = 3


def main() -> dict:
    run.os.makedirs(f"{run.OUT_DIR}/audit", exist_ok=True)
    run.cl.install(run.AUDIO_COST_LOG_PATH)

    kp_summary = None
    for attempt in range(1, MAX_RETRY + 1):
        print(f"[B1B-KP-RETRY] attempt {attempt}/{MAX_RETRY}...")
        try:
            kp_summary = run.keyphrase_stage("b1b")
            print(f"[B1B-KP-RETRY] attempt {attempt} succeeded.")
            break
        except RuntimeError as e:
            print(f"[B1B-KP-RETRY] attempt {attempt} failed: {e}")
            kp_summary = None
    else:
        print("[B1B-KP-RETRY] 全attempt失敗。人手対応が必要。以降のstage(TTS/Assembly)は実行しない。")
        return {"level": "b1b", "status": "STOP", "error": "key_phrase retry exhausted"}

    tts_result = run.tts_stage("b1b")
    lock_summary = run.lock_summary_stage("b1b")
    assembly_result = run.assembly_stage("b1b")

    result = {
        "level": "b1b", "key_phrase": kp_summary, "tts": tts_result,
        "review_lock": lock_summary, "assembly": assembly_result,
    }
    run.save_json(f"{run.OUT_DIR}/audit/e2e_run_summary_audio_01_partial_b1b_resume_03.json", result)
    return result


if __name__ == "__main__":
    main()
