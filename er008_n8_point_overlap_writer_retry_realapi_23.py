# ============================================================
# er008_n8_point_overlap_writer_retry_realapi_23.py
# ER-008-N8-FINAL-PRODUCTION-HARDENING-23 SS3: Point overlap NG時の
# 「記事全体Writer retry」方式の実Writer/実API runtime evidence取得スクリプト。
# ============================================================
# er008_n8_point_overlap_article_retry_22_test_01.pyは制御フロー
# (retry上限・NG_REVIEW_REQUIRED・Point-only regenerationが呼ばれない等)を
# Writer/Fact Checker/Ledger Deviationすべてmockでverifyしたものであり、
# 実LLM呼び出しは一切含まない。ER-23ではユーザーから「実Writer/model/API
# 経路を使ったruntime evidenceが必須」と明示指示されたため、本スクリプトで
# 実際にOpenAI APIを呼び出して記事全体retryを検証する。
#
# 設計:
#   - attempt 0(初回)はNo.8実データを不用意に上書きしないため、確定的に
#     overlapする既存fixture記事(er008_n8_point_overlap_article_retry_22_
#     test_01.pyのOVERLAPPING_ARTICLEをそのまま再利用)をWriterの初回出力
#     として与える(ここは無償、mock)。
#   - retry(attempt 1以降)は実際にvfl01.run_writer_with_technical_retryを
#     呼び出す(実Writer API)。プロンプトはNo.8 A2の実際に使われた
#     prompt.txtをそのまま再利用する(読み取りのみ、No.8本番ファイルには
#     一切書き込まない。出力はすべて本スクリプト末尾のsummary jsonのみ)。
#   - retry後にPoint overlap QAが実際にNGを解消していれば(記事全体retryが
#     機能した実証)、そのままrun_one_pattern内部で実Fact Checker・実Ledger
#     Deviation Checkが呼ばれる(こちらも実API、mockしない)。
#   - Point-only regeneration(POINT_ONLY_REGENERATION_ENABLED)が呼ばれない
#     ことをアサートする。
#   - TTS/ASRは一切呼ばない(run_one_patternはTTSより前の工程のみ)。
#
# 実行方法:
#   PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe er008_n8_point_overlap_writer_retry_realapi_23.py

from __future__ import annotations

import json
import os
import tempfile
from unittest import mock

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er005_cost_logger as cl
from er008_n8_point_overlap_article_retry_22_test_01 import OVERLAPPING_ARTICLE

SCRATCH = ("C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/"
           "4559ebbb-f749-4719-a4c4-1a5c91891e44/scratchpad")
NO8_A2_PROMPT_PATH = "er006_output/pool_pilot_01/pool_n8_airport_line/a2/audit/prompt.txt"
NO8_LEDGER_PATH = "er006_output/pool_pilot_01/pool_n8_airport_line/research/verified_fact_ledger.txt"


def _fake_first_writer_result():
    return {"status": "STRUCTURE_PASS", "raw_text": OVERLAPPING_ARTICLE,
            "attempts": [{"status": "STRUCTURE_PASS", "note": "fixture(No.8本番へ書き込まない、無償)"}]}


def main():
    assert not gen.POINT_ONLY_REGENERATION_ENABLED, \
        "Point-only regenerationが有効化されている(ER-21で撤去済みのはず)"

    cl.install(f"{SCRATCH}/er23_point_overlap_writer_retry_realapi_raw_usage_log.jsonl")
    client = vfl01.get_client()

    with open(NO8_A2_PROMPT_PATH, encoding="utf-8") as f:
        real_prompt = f.read()
    with open(NO8_LEDGER_PATH, encoding="utf-8") as f:
        verified_ledger_text = f.read()

    real_writer_fn = gen.vfl01.run_writer_with_technical_retry
    call_log = []

    def writer_side_effect(*args, **kwargs):
        if len(call_log) == 0:
            call_log.append("fixture")
            return _fake_first_writer_result()
        call_log.append("real_api")
        return real_writer_fn(*args, **kwargs)

    out_dir = tempfile.mkdtemp(prefix="er008_point_overlap_realapi_", dir=SCRATCH)

    with mock.patch.object(gen.vfl01, "run_writer_with_technical_retry", side_effect=writer_side_effect):
        result = gen.run_one_pattern(
            client=client, theme_id="er23_realapi_validation", label="A2",
            prompt=real_prompt, verified_ledger_text=verified_ledger_text,
            topic="The Airport Line That Starts Before It Needs To (ER-23 realapi validation, not No.8 production)",
            out_dir=out_dir, apply_evidence_compression=False, apply_directional_fact_precheck=False)

    with open(f"{out_dir}/point_overlap_article_retry_log.json", encoding="utf-8") as f:
        retry_log = json.load(f)

    summary = {
        "call_log": call_log,
        "writer_call_count_total": len(call_log),
        "real_api_writer_call_count": call_log.count("real_api"),
        "result_status": result["status"],
        "point_overlap_article_retry_attempts": result.get("point_overlap_article_retry_attempts"),
        "retry_log_flagged_by_attempt": [entry.get("flagged") for entry in retry_log],
        "fact_status": result.get("fact_status"),
        "fact_verdict": result.get("fact_verdict"),
        "ledger_status": result.get("ledger_status"),
        "ledger_deviation_count": result.get("ledger_deviation_count"),
        "point_only_regeneration_enabled": gen.POINT_ONLY_REGENERATION_ENABLED,
        "out_dir": out_dir,
    }
    with open(f"{SCRATCH}/er23_point_overlap_writer_retry_realapi_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
