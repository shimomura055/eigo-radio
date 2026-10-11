# RUNTIME_EVIDENCE_02(委任_05A、2026-10-12、Opus必須M1〜M3 + 推奨R1/R2)

スクリプト: `er058_output/asr_tts_prodfix_01/runtime_evidence_02.py`(API課金0円、全てmock/保存済みファイルの写し、Azure実呼出なし)。モデル: TTS/ASRモデル評価ではなくコード是正のため該当なし。

## M3: 固定600秒cool-downが通算3回目直前に発火する(sleepはmock)
`generate_english_segment_with_fallback`へ新規opt-in引数`prior_generations`/`cooldown_total_budget`(既定0/None=従来動作)を追加。`generate_a2_segment_with_slowdown`が通算消費数と総予算3を渡し、標準経路(repro01)・fallback経路ともcool-down判定を通算試行番号で行う(同一module関数`er020.maybe_cooldown_before_attempt`を呼ぶだけで関数本体・新規分岐なし)。
| 周回 | 内側呼出 | cooldown呼出(通算試行,総予算,発火) | fallback呼出 |
|---|---|---|---|
| 1周目 | max3/標準2/prior0 | (1,3,no) (2,3,no) (3,3,**yes**) | 1(通算3回目) |
| 2周目(1回消費) | max2/標準2/prior1 | (2,3,no) (3,3,**yes**) | 0 |
| 3周目(2回消費) | max1/標準1/prior2 | (3,3,**yes**) | 0 |
旧実装では2周目以降は内側max_attempts<3のためcool-downが一度も発火しなかった。通算引数なし(既定)の標準経路ではcool-down呼出自体が無い(従来どおり)。

## M1: archive_prior_tts_results例外隔離
関数全体を`try/except Exception`で包み(本体`_archive_prior_tts_results_impl`)、失敗時は`TTS_RESULTS_PRIOR_ATTEMPTS_ARCHIVE_FAILED`1行のみ。失敗記録自体が失敗しても握り潰す。test: 内部例外/不正構造(segmentsがlist)/履歴書込失敗の3系統でraiseしない。実在results写し4本(n3 hanshin b1b/a2、er019 coffee b1b/a2、`ATTEMPT_HISTORY_PATH`を一時ファイルへ差替、課金0)で例外なし、attempt_history1行サイズ **27,287 / 17,534 / 30,039 / 33,986 bytes**(R3: 1回のarchiveで約17〜34KB。再利用segmentまで重複退避するため肥大監視をOPENへ)。

## M2: 日本語SCGのAzure費用計上
`_azure_stt_strict`にer006 L135と同形の`cl.record`(provider=azure、`audio_duration_submitted_seconds`、成功/失敗とも)を1箇所追加。fake Azure SDK+3秒wavでtest: `provider=azure`・`audio_duration_submitted_seconds=3.0`・success=Trueの1件を計上。集計側は委任_04Aの`cl.azure_stt_cost_usd`が秒/3600×登録単価で処理(SCG含む)。既存`AzureStrictCancelTests`(logger未初期化)は`cl.record`をmock。

## test / Regression
- `er058_asr_tts_prodfix_01_test_01.py` 27件PASS(新規10件: M1 4、M2 1、M3 4、R2 LR救済1)。
- 関連suite(er003/006/007/008/011/012/019/020/025/033/053系 168ファイル、pytest): main(e6f33c4f)=94 failed/8 errors、feature(修正前、本M1〜M3適用直後)=101 failed/8 errors。差分7件の内訳: er007 `AzureStrictCancelTests` 4件(`cl.record`新設でlogger未初期化→testでmock化、PASS)、er012_b `NarratorHeadingRetryPolicyAlignmentTests` 1件(fakeの固定シグネチャが新規opt-in引数を受理せず→fakeに既定値付き引数追加、PASS)、er020 `ProductionModuleUnchangedTest` 2件(未commit差分起因、commit後に再確認)。再実行結果は`REGRESSION_05A.md`参照。
