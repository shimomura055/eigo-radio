# ============================================================
# er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_audio.py
# 管理ID: FAMILY-A-TREND-SYNTHESIS-AI-MANUFACTURING-PRODUCTION-RUN-01
# ============================================================
# 目的: er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_
# writer.pyで生成済みのA2/B1B article.md(Fact Checker/Ledger Deviation/
# Point Overlap QA通過済み)に対し、Scaffold(Preview/Comment)→Key Phrase
# →TTS(Standard同期)→Assembly→Audio Validation Gate opt-in ON経路まで、
# 既存Production関数のみを無変更で直接呼ぶ(前例
# er011_family_a_completion_a2_trend_end_to_end_01_run.pyと同一パターン)。
# 記事本文は再生成しない。
from __future__ import annotations

import hashlib
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl

THEME_ID = "family_a_trend_ai_manufacturing_prod_run_01"
OUT_DIR = f"er011_output/{THEME_ID}"

# A2の日本語タイトル(既存前例パターンを踏襲、英語タイトルの直訳。新しい
# 主張・数字を追加しない)。英語タイトル("The AI Factory Story Has Two
# Different Clocks"、a2/article.md H1、Writer run確認済み)の直訳。
A2_JAPANESE_TITLE = "AI工場の物語には、進み方の異なる2つの時計がある"

LEVELS = ["b1b", "a2"]


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_scaffold(level: str) -> dict:
    level_out_dir = f"{OUT_DIR}/{level}"
    with open(f"{level_out_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    parts = sc.split_article_text(article_text)
    save_json(f"{level_out_dir}/parts.json", parts)
    client = sc.get_client()
    run_fn = sc.run_b1_scaffold if level == "b1b" else sc.run_a2_scaffold
    with cl.logging_context(THEME_ID, f"scaffold_{level}"):
        support = run_fn(client, parts, level_out_dir, article_text)
    support_status = {k: v.get("status") for k, v in support.items()}
    print(f"[AUDIO][{level}] Scaffold(Preview/Comment)完了。status={support_status}")
    return parts


def run_key_phrases(level: str) -> str:
    level_out_dir = f"{OUT_DIR}/{level}"
    kp_dir = f"{level_out_dir}/key_phrases"
    with open(f"{level_out_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    article_id = f"FAMILY_A_TREND_AI_MFG_01_{level.upper()}"
    source_level = "B1-B(N3-01, direct generation)" if level == "b1b" else "A2(V2改1, N3-01)"
    process = "B1_SUPPORT" if level == "b1b" else "A2_SUPPORT"
    with cl.logging_context(THEME_ID, f"keyphrase_{level}"):
        kp = sc.run_key_phrases(article_text, kp_dir, article_id, source_level, process=process)
    sel_status = kp["selection"]["status"]
    canon_status = (kp.get("canonicalization") or {}).get("status")
    redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    save_json(f"{level_out_dir}/audit/run_key_phrases_result_summary.json", {
        "selection_status": sel_status, "canonicalization_status": canon_status,
        "redundancy_qa_status": redundancy_status, "redundancy_retry_log": kp.get("redundancy_retry_log"),
    })
    print(f"[AUDIO][{level}] Key Phrase結果: selection={sel_status} canonicalization={canon_status} "
          f"redundancy={redundancy_status}")
    if kp.get("canonicalization") is None or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        raise RuntimeError(f"{level} Key Phraseパイプライン失敗、STOP。selection={sel_status} "
                            f"canonicalization={canon_status}")
    if redundancy_status == "REDUNDANCY_NG":
        raise RuntimeError(f"{level} Key Phrase Redundancy QAがretry上限到達後もNG、STOP。"
                            "既存Loop Budgetを独自判断で回避しない。")
    return redundancy_status or canon_status


def run_tts(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    with cl.logging_context(THEME_ID, f"tts_{level}"):
        if level == "b1b":
            result = tts_gen.generate_b1_segments(theme)
        else:
            result = tts_gen.generate_a2_segments(theme)
    return result


def run_assembly(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    assemble_fn = asm.stage_assemble_b1 if level == "b1b" else asm.stage_assemble_a2
    with cl.logging_context(THEME_ID, f"assemble_{level}"):
        try:
            result = assemble_fn(theme)
            result["gate_off_result"] = "PASS"
        except RuntimeError as e:
            result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}
    return result


def run_gate_opt_in_check(level: str) -> dict:
    level_out_dir = f"{OUT_DIR}/{level}"
    gate_level = "B1" if level == "b1b" else "A2"
    rs = asm.derive_a_family_required_structure(gate_level)
    try:
        asm.verify_episode_audio_validation_gate(level_out_dir, gate_level, required_structure=rs)
        return {"gate_on_result": "PASS"}
    except RuntimeError as e:
        return {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:800]}


def run_level(level: str) -> dict:
    print(f"===== [AUDIO] level={level} 開始 =====")
    run_scaffold(level)
    kp_status = run_key_phrases(level)
    tts_result = run_tts(level)
    assemble_result = run_assembly(level)
    gate_on = run_gate_opt_in_check(level) if assemble_result.get("gate_off_result") == "PASS" else \
        {"gate_on_result": "SKIPPED_ASSEMBLE_NOT_PASS"}
    return {
        "level": level, "kp_status": kp_status, "tts_result": tts_result,
        "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
    }


def main() -> dict:
    global A2_JAPANESE_TITLE
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log_audio.jsonl")

    levels = sys.argv[1:] or LEVELS
    results = {}
    for level in levels:
        if level == "a2" and A2_JAPANESE_TITLE:
            tts_gen.JAPANESE_TITLES.update({THEME_ID: A2_JAPANESE_TITLE})
            print(f"[AUDIO] JAPANESE_TITLES登録(人手供給・直訳): {A2_JAPANESE_TITLE!r}")
        try:
            results[level] = run_level(level)
        except (RuntimeError, AssertionError) as e:
            results[level] = {"level": level, "status": "STOP", "error": str(e)}
            print(f"[AUDIO][{level}] STOP: {e}")

    save_json(f"{OUT_DIR}/audio_run_summary.json", results)
    print("[AUDIO] 完了。")
    return results


if __name__ == "__main__":
    main()
