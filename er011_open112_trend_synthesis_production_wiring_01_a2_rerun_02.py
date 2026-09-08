# ============================================================
# er011_open112_trend_synthesis_production_wiring_01_a2_rerun_02.py
# OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01: Fable修正指示(1回目)
# 対応 — A2再実行(既存Loop Budget/Point Overlap閾値は無変更、新規runとして
# 最大2回まで)
# ============================================================
# 背景: 元のGate 3 runtime evidence run(er011_open112_trend_synthesis_
# production_wiring_01_run.py)で、A2が既存Loop Budget(POINT_OVERLAP_
# ARTICLE_RETRY_MAX=2、記事全体Diagnostic Full Retry)の上限に到達し
# status=NG_REVIEW_REQUIREDで終了した。Fableの受入判定(Gate 7)により、
# 同じProduction正式path・同じTheme 2 Ledger/topic・同じLoop Budget・同じ
# Point Overlap閾値(0.40、無変更)で、「新規run」として最大2回まで再実行
# するよう指示された。
#
# 「同じProduction正式path」の実装方針: er006_pool_pilot_01_writer.
# run_writer_for_theme()は呼び出す度にB1B・A2の両方を生成する(ループ内で
# 両labelを回す設計)。B1BはすでにOK到達済みであり、B1Bを再度生成し直すのは
# 無駄な追加費用になる(costavoidance、上限¥50に抵触しうる)ため、
# run_writer_for_theme()がA2 labelに対して実際に呼ぶのと**全く同一の関数・
# 全く同一の引数**(gen.resolve_editorial_type_module_block →
# gen.build_common_block → gen.build_prompt → gen.run_one_pattern、
# apply_evidence_compression=True[既定])を、A2単体に絞って直接呼び出す
# (er006_pool_pilot_01_writer.py 66-87行と同一ロジック、B1Bループを
# 省いただけ)。既存の`er011_open112_trend_synthesis_production_wiring_01_
# a2_run02.py`(前回作業ミス是正の過程で用意されていた未使用スクリプト)を
# 出力先のみ本タスク指定のパスへ変更して踏襲する。Loop Budget
# (POINT_OVERLAP_ARTICLE_RETRY_MAX)・Point Overlap閾値(0.40)・Diagnostic
# Full Retryロジック・Point Value QAはすべて`gen.run_one_pattern()`内の
# 既存コードをそのまま使う(本ファイルは一切変更していない)。
#
# 出力: er011_output/open112_trend_synthesis_production_wiring_01/
# a2_rerun_02/attempt{1,2}/ (既存の a2/ evidence は上書きしない)。
# 「新規run」を2回まで許可されているため、attempt1がstatus=OKに到達したら
# attempt2は実行しない(1回でOKなら止める、の指示どおり)。
from __future__ import annotations

import argparse
import json

import er005_cost_logger as cl
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er011_open112_trend_synthesis_production_wiring_01_run as base

RERUN_ROOT = f"{base.OUT_DIR}/a2_rerun_02"


def run_attempt(attempt_num: int) -> dict:
    out_dir = f"{RERUN_ROOT}/attempt{attempt_num}"
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_text = gen.load_text(base.THEME2_LEDGER_PATH)
    block = gen.resolve_editorial_type_module_block("trend_synthesis")
    common_block = gen.build_common_block(master_full_text, base.TREND_TOPIC_JA, ledger_text,
                                           editorial_type_module_block=block)
    prompt = gen.build_prompt(common_block, gen.A2_KAI1_INSTRUCTION)
    with cl.logging_context(base.THEME_ID, f"writer_a2_rerun02_attempt{attempt_num}"):
        result = gen.run_one_pattern(client, base.THEME_ID, "A2", prompt, ledger_text,
                                      base.TREND_TOPIC_JA, out_dir)
    print(f"[a2_rerun_02] attempt{attempt_num}: status={result.get('status')} "
          f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
          f"point_overlap_article_retry_attempts={result.get('point_overlap_article_retry_attempts')}")
    with open(f"{out_dir}/rerun_attempt_summary.json", "w", encoding="utf-8") as f:
        json.dump({"attempt_num": attempt_num, "status": result.get("status"),
                    "fact_verdict": result.get("fact_verdict"),
                    "ledger_status": result.get("ledger_status"),
                    "point_overlap_article_retry_attempts": result.get("point_overlap_article_retry_attempts"),
                    "directional_fact_precheck_status": result.get("directional_fact_precheck_status")},
                  f, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=int, required=True, choices=[1, 2])
    args = parser.parse_args()
    cl.install(f"{RERUN_ROOT}/raw_usage_log.jsonl")
    run_attempt(args.attempt)
