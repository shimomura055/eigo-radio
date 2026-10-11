# 委任_25: OPEN-256 Opusレビュー是正 -> ¥0 replay -> runtime evidence -> SSOT
- 範囲: `er020_tts_retry_local_rewrite_01.py`(全文性検証の追加条件のみ)、test、replay/runtime script、証跡、SSOT。7 Gate・retry/fallback上限・Production Prompt・日本語経路は不変。
- 是正: span整合(採用。代案=編集予算は誤拒否0だが申告外変更を検出できず不採用)/数値保持/先頭引用符・ラベル拒否/docstring。推奨4は不実施(OPEN-259)。
- test: `er020_tts_retry_local_rewrite_fullseg_test_01.py` 32件PASS、既存er020_01(23)/trial_02(14)/cooldown_trial_01(17)/er007_ja(28)/er019 x2/er021(62)/er026(19)/dangling(4) PASS(.venv)。
- replay: `OPEN256_REPLAY_01.md/.json`(旧採択76維持・救済13/14・META3件all_seven True)。
- runtime: `OPEN256_RUNTIME_01.md`、`open256_runtime_01/run{1,2}/`(2回実行、run2が該当=旧NG/新OK採択、RESOLVED、ASR exact PASS)。実費約1.2円。
- 共有ファイル追記: `er011_output/attempt_history.jsonl` 2行、`er021 .../telemetry.jsonl`(run1)。既存行不変。
- SSOT: CURRENT_SPEC(Local Rewrite行へ追補)/DECISION_LOG(末尾へ追記)/OPEN_ITEMS(OPEN-256更新・257/258追記・259/260新規)/PM_GOVERNANCE 14-6新設/ACTIVE_TASK。
- PRODUCTION_WIREDは宣言していない(Fable Gate待ち)。
