# ============================================================
# er011_no18_evidence_compression_a_precision_21r_production_regen.py
# ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R
# ============================================================
# 目的: Pattern A(Representative Metric + Supporting Trend)+ Listener-
# Friendly Numeric Precisionを正式Production Evidence Compression Editor
# Prompt(er003_v1_n3_01_evidence_compression_editor.py)へ組み込んだ後、
# No.18 A2/B1を「正式Production経路」で再生成する(§5)。
#
# Writer自体は再生成しない(既存の、OPEN-108/109でLedger精密化済みの
# Writer出力=pool_n18_notifications_specfix_v2/{a2,b1b}/audit/
# writer_attempts.jsonのSTRUCTURE_PASS raw_textをそのまま再利用する)。
# 理由: (1) Evidence Compressionは既にFact-safeなWriter出力のspoken
# layerだけを軽量化する工程であり、Writer自体を再実行する安全上の必然性
# がない、(2) Writerを再実行すると乱数性によりPoint One/Two・Preview・
# Comment等Evidence Compressionと無関係な箇所まで書き変わり、ユーザーが
# 既に承認済みのNo.18本文内容(OPEN-107〜110で作り込んだもの)を不必要に
# 破棄してしまう、(3) 音声パーツ再利用(§6)はテキストが一致する場合のみ
# 可能であり、無関係な書き換えはそれを妨げる。
#
# それ以外の全工程(Evidence Compression Editor・Point Overlap/Value QA・
# Fact Checker・Ledger Deviation Check・Local Rewrite・Directional Fact
# Precheck)は、gen.run_one_pattern()という単一の実Production関数を、一切
# コード変更せずそのまま呼び出す(er011_no18_open108/109_ledger_refined_
# regenerate系と同じ手法)。Writer呼び出しだけを、既存raw_textをそのまま
# 返すstubへ差し替える(新規LLM呼び出しなし、既存承認済み文章を保持)。
#
# 出力先はpool_n18_notifications_specfix_v2を上書きせず、新しいtheme_id
# (pool_n18_notifications_specfix_v2_ec_a_precision_21r)へ書く(比較の
# ため、また既存git管理下の記録を破壊しないため)。

from __future__ import annotations

import json
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er005_cost_logger as cl
import er011_no18_specfix_v2_production_run_01 as driver

OLD_OUT_DIR = driver.OUT_DIR  # er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2
NEW_THEME_ID = "pool_n18_notifications_specfix_v2_ec_a_precision_21r"
NEW_OUT_DIR = f"er006_output/pool_pilot_01/{NEW_THEME_ID}"
TOPIC_JA = driver.TOPIC_JA

LEVELS = {
    "a2": {"label": "A2"},
    "b1b": {"label": "B1B"},
}


def _load_reused_writer_result(level: str) -> dict:
    """既存(Ledger精密化済み)Writer出力をそのまま再利用するためのwriter_result
    互換dictを組み立てる。新規LLM呼び出しは行わない。"""
    with open(f"{OLD_OUT_DIR}/{level}/audit/writer_attempts.json", encoding="utf-8") as f:
        attempts = json.load(f)
    pass_attempt = next(a for a in attempts if a["status"] == "STRUCTURE_PASS")
    raw_text = pass_attempt["raw_text"]
    reused_attempt = {
        "attempt": 1, "status": "STRUCTURE_PASS",
        "model": pass_attempt.get("model"), "response_id": pass_attempt.get("response_id"),
        "h3_count": pass_attempt.get("h3_count"), "headings": pass_attempt.get("headings"),
        "raw_text": raw_text,
        "note": "REUSED_VERBATIM_FROM_pool_n18_notifications_specfix_v2 (OPEN-108/109 Ledger-refined "
                "Writer output); NO new Writer LLM call was made for ER-011-NO18-EVIDENCE-COMPRESSION-"
                "A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R.",
    }
    return {"status": "STRUCTURE_PASS", "attempts": [reused_attempt], "raw_text": raw_text,
            "model": pass_attempt.get("model"), "response_id": pass_attempt.get("response_id")}


def _make_stub_writer(reused_result: dict):
    def _stub(client, user_message: str, max_attempts: int = 2, model: str = None) -> dict:
        return reused_result
    return _stub


def prepare_output_dirs() -> None:
    os.makedirs(NEW_OUT_DIR, exist_ok=True)
    new_research_dir = f"{NEW_OUT_DIR}/research"
    if not os.path.isdir(new_research_dir):
        shutil.copytree(f"{OLD_OUT_DIR}/research", new_research_dir)
        print(f"[21R] research/ を {OLD_OUT_DIR} から {NEW_OUT_DIR} へコピーしました(Ledger自体は無変更)。")


def run_level(client, level: str) -> dict:
    label = LEVELS[level]["label"]
    verified_ledger_text = open(f"{NEW_OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()
    master_full_text = __import__("er003_v1_en_direct_ab_01_generate").load_master_full_text()
    instruction = gen.A2_KAI1_INSTRUCTION if level == "a2" else gen.B1_B_DIRECT_INSTRUCTION
    common_block = gen.build_common_block(master_full_text, TOPIC_JA, verified_ledger_text)
    prompt = gen.build_prompt(common_block, instruction)  # 監査記録用(stub Writerは内容を使わない)

    reused_result = _load_reused_writer_result(level)
    original_run_writer = vfl01.run_writer_with_technical_retry
    gen.vfl01.run_writer_with_technical_retry = _make_stub_writer(reused_result)
    try:
        print(f"[21R] {label}: run_one_pattern()(実Production経路、Writerのみreuse-stub)開始...")
        with cl.logging_context(NEW_THEME_ID, f"writer_{level}_ec_a_precision_21r"):
            result = gen.run_one_pattern(
                client, NEW_THEME_ID, label, prompt, verified_ledger_text, TOPIC_JA,
                f"{NEW_OUT_DIR}/{level}")
    finally:
        gen.vfl01.run_writer_with_technical_retry = original_run_writer

    print(f"[21R] {label}: 完了。status={result.get('status')} fact_verdict={result.get('fact_verdict')} "
          f"ledger_status={result.get('ledger_status')} "
          f"evidence_compression_applied={result.get('evidence_compression_applied')}")
    return result


def main() -> dict:
    prepare_output_dirs()
    client = vfl01.get_client()
    cl.install(f"{NEW_OUT_DIR}/raw_usage_log_21r_articles.jsonl")

    summary = {}
    for level in ["a2", "b1b"]:
        summary[level] = run_level(client, level)

    with open(f"{NEW_OUT_DIR}/regen_21r_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in summary.items()},
                   f, ensure_ascii=False, indent=2, default=str)
    print(f"[21R] 両レベル完了。summary -> {NEW_OUT_DIR}/regen_21r_summary.json")
    return summary


if __name__ == "__main__":
    main()
