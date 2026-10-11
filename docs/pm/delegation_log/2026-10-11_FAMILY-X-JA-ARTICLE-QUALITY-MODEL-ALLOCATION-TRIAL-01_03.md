# FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 委任_03 (2026-10-11、Phase 2実行)

- 依頼元: Fable(ユーザーGo 2026-10-11)。範囲: Trial driver実装、A既存複製、B/C/D/E生成(B=STOP)、Blind比較ページ、RESULT_01。Production code/Prompt/Routing/CURRENT_SPEC変更なし、Research/Ledger再実行なし、英訳・RF・TTS・Audioなし。
- 実装: `er052_output/ja_article_quality_model_allocation_trial_01/maq_driver_01.py`(方式Y、Production moduleは無改変import、`require_model_or_override`使用)、`maq_driver_01_test_01.py`(無課金ドリフト検査ALL_PASS)、`aux_metrics_01.py`、`blind_page_01.py`。
- 実行: C/D/Eを別process並列で各1回のみ(全OK、新規課金JPY109.11、上限250内)。A=run_regen_01複製(0円)。B=課金前STOP(旧仕様=凍結旧B3+Sonnet subagent二重注記、代替仕様へ変更不可。選択肢はRESULT_01 5節)。
- 互換性: gpt-6.1-solのeffort=high・B3 json_schema、Astra B3 json_schemaとも受理。
- 証跡: RESULT_01.md、AUX_METRICS_01.md、BLIND_MAP_01.json(評価前開示禁止)、runs/<案>/。
- STOP: B案のみ(新規仕様判断=ユーザー/Fable判断待ち)。他案は完了。
