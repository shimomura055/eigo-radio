# r3 support_fact_ids 棚卸し(委任_01 作業5、¥0)
- 出力: Stage1 r3のschema(`R3_JSON_SCHEMA`)に`support_fact_ids`(配列、SUPPORTED時は必須)があり、モデルは返している。決定論検査`verify_supported`(ledger逐語引用・数値・因果・否定)がこれを使う。
- 保存: **未保存**。`evaluate_r3`は検査後にstatus/model_verdictだけを返し、`per_route.r3`にsupport_fact_idsが無い。保存済み全ログ(er052_output配下のjson/jsonl)でGrepしても0件(prompt/schema定義の文字列を除く)。
- 最小変更(実装済み、既定OFF): `er052_open233_stage1_coverage_checker_01.py` の `evaluate_r3`(単位別support_fact_idsを返す)、`_run_r3`(outへ)、`run_stage1_coverage`(`per_route.r3.support_fact_ids`)、`run_recheck_scope`(`audit.r3_support_fact_ids`)。スイッチ `OPEN233_SAVE_R3_SUPPORT_IDS=1`。OFFではキー自体を作らない(テスト: er052_open233_stage2_w1w2_test_01.py TestSaveR3SupportIds)。
- 既存ログからの事後復元: **不可**(r3の生応答も保存されていない。per_routeのunit_status/model_verdictのみ)。
- oracle(評価JSON fact_id)との一致率: **要replay**(同版でr3を再実行しsupport_fact_idsを保存する必要。API要)。代替の粗い指標: Stage1候補のrelated_fact_ids(候補になった単位のみ)とdev項目fact_idの一致=stage1_candidate_rate.mdの「fact一致」(fact_id既知30件中29件が同factの候補を持つ)。これはSUPPORTED判定側のsupport_fact_idsの精度ではない。
