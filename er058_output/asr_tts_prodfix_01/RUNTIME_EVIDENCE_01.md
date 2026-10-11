# RUNTIME_EVIDENCE_01(委任_04A、2026-10-12)

スクリプト: `er058_output/asr_tts_prodfix_01/runtime_evidence_01.py`(cap/fallback/fallback_entity/azure)。出力はTrial領域`er058_output/asr_tts_prodfix_01/run_*`(音声wavは削除済み)。Production telemetry・Master Store・Pronunciation Ledgerへの混入なし(attempt_history/queueはTrial領域へ差し替え、worktree内のtelemetry変更はgit restoreで復元、`git status`で確認)。`.env`は値を表示せずAzure呼出のみに使用。モデル: 評価対象はコード修正でありTTS/ASRモデル評価ではない(TTS・Primary ASR・Secondary mockのためモデル使用なし。Azure STTは本番と同一サービス)。

## (1) 減速後NGでも4回目生成が起きない(`cap`、正式経路・外部呼出のみmock、実FFmpeg減速)
| 条件 | 旧(main) | 新(fix) |
|---|---|---|
| 各周: 標準1回目NG→2回目OK→減速後NG(Coffee part2型) | TTS生成**6回**(`run_cap_base/cap_summary.json`) | TTS生成**3回**で打ち切り、STOPPED、`tts_generation_cap_reached=true`(`run_cap_fixed/cap_summary.json`) |
`run_fallback_fixed`(標準2回NG+minimal fallback、同一segment)は合計3回で`tts_generations_used=3`。

## (2) Azure費用が集計に出る(`azure`、実Azure STT 1回)
保存音声(`er003_output/a2_audio_01/A02/narration/in_one_line.wav`、13.611秒)をAzure STTへ1回送信。`run_azure_fixed/raw_usage_log.jsonl`のAzureレコード→新集計`aggregated_jpy=0.6049`(`by_provider azure 0.6`)。同じログを旧(main)集計関数で集計すると`(0.0, {'azure': 0.0})`(`base_aggregation_same_log.txt`)。実費用: Azure約0.6円(登録単価試算、契約tier未確認)。OpenAI/Gemini課金0円。

## (3) 転写・Styleが記録に残る
- `run_fallback_entity_fixed/attempt_history.jsonl`(標準1回目Primary="Some US calls..."、fallback force_secondary、Azure mock): `attempts_detail`に標準/fallbackのPrimary転写・`cascade_steps`(primary_1/tier3_corroboration_secondary[azure]/primary_2/secondary_1/secondary_2の各転写全文)・`instruction_label=MINIMAL_INSTRUCTION_PREFIX`・`style_prefix`(標準2027字/fallback 129字のlen+sha256+先頭200字)。
- 同runで、queue重複(fallbackのAzure steps)は`human_review_queue.jsonl`は1行のまま、転写は`HUMAN_REVIEW_QUEUE_DUPLICATE_SUPPRESSED`としてattempt_history.jsonlへ残った。
- `run_cap_fixed/attempt_history.jsonl`: `A2_SLOWDOWN_REVERIFY`に`post_slowdown_asr_text`が残る。
- `tts_generation_results.json`上書き前退避は単体test(`RecordAppendOnlyTest.test_prior_tts_results_archived_append_only`、追記2行・上書きなし)で確認(実`--stage tts`実行はTTS課金のため未実施)。

## test
- 新規`er058_asr_tts_prodfix_01_test_01.py` 17件PASS(旧コードでは上限/Azure系10件FAIL=回帰検知力あり)。
- 関連suite(er003/005/006/007/008/011/012/019/020/025/033/053系 168ファイル): 旧main=95 failed/8 errors、新=95 failed/8 errors(既存fail集合。差分: er020 ProductionModuleUnchangedTest 2件は未commit差分起因でcommit後PASS、er008_audio_validation_gate_05_test 2件はmain側のflaky→再実行PASS)。**新規failure 0**。
