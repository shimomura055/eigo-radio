# OPEN-258-JA-SECONDARY-ASR-PRODUCTION-WIRING-01 委任_03 (2026-10-11、Sonnet実行層)

範囲: ユーザー正式採用(`APPROVED_FOR_PRODUCTION` 2026-10-11)のC2 同形異音語ガード・推奨4 否定マーカー除外の実装、Phase 0回帰、最小runtime再確認(a)(e)。branch `feature/scg-ja-secondary-01`。mergeなし・SSOT編集なし。

実装: `er007_ja_secondary_asr_01.py`の`_scg_exclusion_reason`(+補助`_scg_heterophone_candidate`/`_scg_negation_marker_diff`/`_scg_negation_ranges`)のみ。共通ASR判定・呼出元・retry/fallback不変。
詳細: `er053_output/open258_scg_production_wiring_01/OPUS_REVIEW_FOLLOWUP_02.md`、runtime: `RUNTIME_EVIDENCE_02.md`/`runtime_evidence_02.jsonl`。
test: 新規`er007_ja_scg_c2_neg_test_01.py` 17件+更新`er007_ja_scg_phase0_regression_test_01.py`。Phase 0回帰: 救済13・C群NG5・PHONETIC3NG維持、「出演/出現」3 attempt PASS維持。
課金: 本委任約1.66円(累計約4.30円/5円)、新規TTS 0。追跡ファイル汚染(suite/runtimeによる共有ファイル追記・`_test_*`)は`git checkout --`/削除で復元済み。
