# -*- coding: utf-8 -*-
# ER-006-COST-WASTE-RCA-RESEARCH-COVERAGE-GATE-01: No.4のRound1(初回2ソース)
# 状態を、当時と同一のsourcesから再構築する(未来情報リーク防止のため、
# SRC-003/SRC-004は一切含めない)。Evidence Pack/VFL/Verificationの生成
# テキストは非決定的(LLM出力)のため、当時の生応答とビット一致はしないが、
# 与える情報(2ソースの内容)は完全に同一であり、Coverage Gateの検証目的
# (「この時点のEvidenceで足りていたか」)には十分な忠実な再構築となる。
import sys, json
sys.path.insert(0, '.')
import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/raw_usage_log.jsonl")

import er006_pool_pilot_01_research as research_mod
import er006_pool_pilot_01_ledger as ledger_mod

theme_id = "pool_n4_supermarket_round1_reconstruction"
out_dir = "er006_output/pool_pilot_01/coverage_gate_01/n4_round1_reconstruction"
title = "The Supermarket Shuffle: Why Shelves Keep Moving"
sources = json.load(open(f"{out_dir}/raw_sources_round1.json", encoding="utf-8"))["sources"]

result = research_mod.run_research_for_theme(theme_id, out_dir, title, sources)
ledger_text = ledger_mod.build_ledger_text_from_vfl(result["vfl"]["parsed"], result["evidence_pack"]["parsed"], title)
with open(f"{out_dir}/verified_fact_ledger_round1.txt", "w", encoding="utf-8") as f:
    f.write(ledger_text)
print("Round1 reconstruction done. Facts:", len(result["vfl"]["parsed"]["facts"]))
print("Verdicts:", {v: sum(1 for x in result['verification']['parsed']['verifications'] if x['verdict']==v)
                     for v in set(x['verdict'] for x in result['verification']['parsed']['verifications'])})
