# ============================================================
# er006_pool_pilot_01_writer.py
# ER-006-POOL-PILOT-01: Writer(B1/A2)+FactCheck+LedgerDeviation
# ============================================================
# er003_v1_n3_01_articles_generate.py の本番run_one_pattern()をそのまま
# 呼び出す(prompt/instruction/Fact Checker/Deviation Checkは無変更)。
# B1/A2それぞれを個別にcl.logging_context()で囲むことで、共有のrun_theme()
# 一括呼び出しでは失われるLevel別costの区別を維持する。

from __future__ import annotations

import json
import os
import time

import er005_cost_logger as cl
import er003_v1_n3_01_articles_generate as gen
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er008_shared_point_blueprint_01 as blueprint_mod


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def run_writer_for_theme(client, master_full_text: str, theme_id: str, topic: str,
                          ledger_path: str, out_dir: str, blueprint=None,
                          evidence_compression: bool = False,
                          apply_evidence_compression_editor: bool = True,
                          editorial_mode: str | None = None,
                          trend_gate_checklist: dict | None = None) -> dict:
    """blueprint(er008_shared_point_blueprint_01.SharedPointBlueprint、
    A2/B1 Point Structure Semantic Alignmentタスクで追加)を渡すと、両
    Levelのpromptへ共通のPoint構造制約が挿入される。Noneの場合(既定)は
    旧来の呼び出しと完全に同一の挙動になる(後方互換、既存Topicへの
    影響なし)。

    evidence_compression(既定False)は方式B(Compression-aware Writer、
    ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03で試作、比較の結果
    不採用)のscript-only検証専用引数。**方式Cとは別物**であり、既定Falseの
    まま維持する(Production既定では使わない)。

    apply_evidence_compression_editor(既定True、ER-008-EVIDENCE-
    COMPRESSION-PROD-AND-N7-AUDIO-06でProduction既定へ昇格)が、ユーザー
    採用済みの方式C(Lossless Editor)。gen.run_one_pattern()内で、Writer
    出力に対しspoken layerだけを軽量化する(詳細はer003_v1_n3_01_
    evidence_compression_editor.py)。DEV/testでOFFにしたい場合のみ
    Falseを渡す。

    editorial_mode(既定None、OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-
    WIRING-01で追加): 例 "trend_synthesis"。gen.resolve_editorial_type_
    module_block()で解決したEditorial Type Module Blockを、build_
    common_block()のeditorial_type_module_block引数へ渡す。既定None
    (=空文字列)の場合、既存の全呼び出し元(A-Family全テーマ)は出力
    バイト列が1文字も変わらない(後方互換)。Mode判定の自動化はここでは
    行わない(呼び出し側が人間の判断で明示的に渡す値)。

    trend_gate_checklist(既定None): Trend Synthesis modeを使う場合の、
    Trend Gate 6条件+Mode判定2問チェックリストの**手動判定結果**を
    そのままrun summary(articles_run_summary.json)へ記録するための
    入力メタデータ。自動判定ロジックはここでは実装せず、値をそのまま
    転記するだけ(記録専用)。"""
    verified_ledger_text = load_text(ledger_path)
    editorial_type_module_block = gen.resolve_editorial_type_module_block(editorial_mode)

    results = {}
    timing = {}
    for label, instruction, level_out_dir, stage_tag in [
        ("B1B", gen.B1_B_DIRECT_INSTRUCTION, f"{out_dir}/b1b", "writer_b1"),
        ("A2", gen.A2_KAI1_INSTRUCTION, f"{out_dir}/a2", "writer_a2"),
    ]:
        blueprint_block = ""
        if blueprint is not None:
            level = "b1" if label == "B1B" else "a2"
            blueprint_block = blueprint_mod.render_blueprint_for_writer(blueprint, level)
        common_block = gen.build_common_block(master_full_text, topic, verified_ledger_text,
                                               shared_point_blueprint_block=blueprint_block,
                                               evidence_compression=evidence_compression,
                                               editorial_type_module_block=editorial_type_module_block)
        prompt = gen.build_prompt(common_block, instruction)
        t0 = time.time()
        with cl.logging_context(theme_id, stage_tag):
            result = gen.run_one_pattern(client, theme_id, label, prompt, verified_ledger_text,
                                          topic, level_out_dir,
                                          apply_evidence_compression=apply_evidence_compression_editor)
        timing[stage_tag] = round(time.time() - t0, 2)
        results[label] = result

    # articles_run_summary.json自体のschema(既存の{label: {...}}フラット構造)は
    # 既存呼び出し元との互換のため変更しない(下流で本ファイルをparseする既存
    # コードは確認されていないが、既定挙動不変の原則を優先し、mode metadataは
    # 別ファイルへ分離する)。editorial_mode/trend_gate_checklistは新規ファイル
    # run_metadata.json(OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01で
    # 追加)へ記録する。editorial_mode=None(既定)の場合もこのファイル自体は
    # 新規生成される(空runでも書き込むが、既存ファイルの上書き・schema変更は
    # 一切ない)。
    run_metadata = {"editorial_mode": editorial_mode, "trend_gate_checklist": trend_gate_checklist}
    with open(f"{out_dir}/run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/articles_run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in results.items()},
                   f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/writer_timing.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    print(f"[{theme_id}] Writer完了。editorial_mode={editorial_mode} timing={timing}")
    for label, r in results.items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')}")
    return {"results": results, "timing": timing, "run_metadata": run_metadata}


if __name__ == "__main__":
    print("This module is imported by er006_pool_pilot_01_run.py; not run directly.")
