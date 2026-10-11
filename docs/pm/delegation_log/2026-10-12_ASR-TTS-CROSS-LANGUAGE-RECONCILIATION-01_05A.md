# ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_05A(既存Production不具合是正のOpus必須M1〜M3→Regression→main merge→SSOT、2026-10-12)

## 変更点(feature commit d40cfbc7/6af09ede)
- M1 `er011` `archive_prior_tts_results`全体を`try/except`で隔離(本体`_archive_prior_tts_results_impl`、失敗時は`TTS_RESULTS_PRIOR_ATTEMPTS_ARCHIVE_FAILED`1行のみ)。
- M2 `er007` `_azure_stt_strict`にer006同形の`cl.record`(provider=azure、音声秒数)を1箇所追加。
- M3 **実装可(STOPなし)**: `generate_english_segment_with_fallback`/`generate_narration_snippet_verified_strict`へ既定0/Noneのopt-in引数`prior_generations`/`cooldown_total_budget`を追加、n3外側ループが通算消費数と総予算3を渡す。`maybe_cooldown_before_attempt`本体・新規分岐なし(差分約+20行)。通算3回目直前のみ発火(1周目fallback、2周目標準2回目、3周目標準1回目)。
- R1 RESOLVEDコメント更新、R2 test追加(LR救済結果で周回しない/残り1回でfallback 0回/実在results写し4本のarchive、行17,534〜33,986 bytes)。
- test追従: er007 `AzureStrictCancelTests`(cl.record mock)、er012_b a2_new_topic test fake(新opt-in引数受理)。

## test / Regression
新規 `er058_asr_tts_prodfix_01_test_01.py` 27件PASS。関連suite 168ファイル main=94 failed/8 errors → feature=93/8、新規failure 0(`er058_output/asr_tts_prodfix_01/REGRESSION_05A.md`)。merge後main再実行(er058/er007/er011/er020/er012_b/er003/er019系): 9 failed、全て既存fail集合内(新規0)。evidence: `RUNTIME_EVIDENCE_02.md`/`runtime_evidence_02.py`。

## Git
merge commit `d7ae4b9b`(`--no-ff`、競合なし、push済み)、rollback tag `rollback/pre-asr-tts-prodfix-01-20261012`(`9386d564`、push済み)。Master Store/telemetryへの混入なし(merge差分にer006 master store/telemetry/ledgerなし、attempt_historyはer058 Trial領域のみ)。mainの既存未commit差分(他agent/test由来のtelemetry等)は触れていない(test実行で増えた`er006_output/pool_pilot_01/...openai_ja_asr_quality_log.jsonl`のみrestore)。

## SSOT
`CURRENT_SPEC.md` L1692(遵守明確化のみ: 通算3回共有・cool-down通算・Azure費用集計)、`DECISION_LOG.md` 末尾エントリ、`OPEN_ITEMS.md` OPEN-270/271/275 CLOSED(L773/774/778)、OPEN-277 一部対応(L780、固定ラベル残2箇所明記)、新規OPEN-282(R3)/283(R4a)/284(R4b)/285(R5)(L785-788)、`docs/pm/REPORT_LEDGER.md`。
費用: 約JPY0.6(04AのAzure 1回)、05Aは0円。Azure契約tier(F0/S0)・実請求確認はユーザー。
## 後始末
worktree `eigo-radio-prodfix-base`削除(下記)。`eigo-radio-prodfix`はbranch保持のまま残置。
