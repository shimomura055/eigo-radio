# WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_01B (2026-10-09, sonnet-worker)
範囲: detectors/配下・価格ファイル・テストのみ。ACTIVE_TASK.mdは触っていない。API評価呼び出し0円、疎通のみ。
実施:
1. 単価登録: gpt-6.1-sol / deepseek-v4-pro 追加、gpt-5.6-sol を公式現行値へ更新(旧値はprice_history)。出典と原文行=er052_output/writer_dev_risk_flagger_01/detectors/PRICING_SOURCES_01.md。er006_model_routing_pricing_coverage_test_01 11件PASS。
2. 疎通: gpt-6.1-sol / gpt-6-astra / deepseek-v4-pro すべて成功。実費合計 JPY 0.21(cost_ledger.jsonl)。
3. 設計: detectors/DETECTOR_CANDIDATES_01.md(D0/D1map/D1full/D2/D3a-c/D4、旧モデル不使用明記、費用見積)。
4. harness: run_flagger_01.py / make_blind_01.py / aggregate_flagger_01.py / d0_directional.py / prompts_flagger.py / flagger_lib.py / estimate_cost_01.py / smoke_connectivity_01.py。ユニットテスト test_flagger_01.py 30件PASS(API不要)。
5. 参考: D0を既存10ケース(eval_items_01.json)に通した設計時動作確認 results/d0_none_sanity10.jsonl(検出率の根拠ではない)。
未実施: casebankへの実API評価(casebank未完成・別委任)。Production変更なし。
