# OPEN-256 是正後 (b) runtime evidence(委任_25)

スクリプト: `er053_family_x_open256_runtime_01.py <run>`。Production retry経路
`er003_v1_crosslevel_audio_02_common._local_rewrite_recovery_for_english_segment_with_fallback`(`run_local_rewrite_recovery`を呼ぶ実経路)を
META b1b comment_2 原稿逐語(Ledger/記事は読み取りのみ)で実行。`last_asr_text`はMETA記録済みの実ASR("Some use calls ...")。
TTS backend=`speech_metadata_flash_lite`(`gemini-3.8-flash-lite-tts`)、Luna=`gpt-6-luna`(候補生成・QAとも、実response.model)、ASR=Production routing(OpenAI+Azure cascade)。
隔離out dir: `open256_runtime_01/run{N}/`(wav・raw_usage_log・recovery_artifacts・runtime_result.json・shared_files_changed.json)。*.wavは.gitignoreのためローカルのみ(commitしない)。

| run | 採択候補 | 旧ルール(先頭15文字)判定 | 新ルール | status | 再TTS ASR | 判定 |
|---|---|---|---|---|---|---|
| 1 | id1 "Some Muse calls were **transferred** over ..." | 通る(先頭一致) | FULL_SEGMENT_OK / SPAN_CONSISTENT | RESOLVED_BY_LOCAL_REWRITE | verified=true("Some US calls were transferred ...") | **根拠に数えない**(旧ルールでも通る候補) |
| 2 | id1 "**Certain** Muse calls were handed over ..." | **不合格**(先頭15文字が異なる) | FULL_SEGMENT_OK / SPAN_CONSISTENT | RESOLVED_BY_LOCAL_REWRITE | verified=true("Certain Muse calls were handed over ..."、完全一致) | **該当(旧NG・新OK)** |

run2は全5候補が新ルール全文性OK(旧ルールでは全5件が先頭不一致で不合格)。7 Gate: 1・2が全PASS、3-5はGate不合格(従来どおり他Gateが判定)。
run1の候補は 1,3,4 が全Gate PASS(3・4は旧NG/新OKだが選択は unchanged_ratio 最大のid1)。

## 費用(実測のraw usage、Standard単価・1USD=160円換算)
run1 約0.62円 / run2 約0.63円(Luna 2 call + TTS 1 call + ASR。OpenAI ASR/AzureはトークンmeterなしのためAzure=audio時間ごく僅か・OpenAI ASRは数十トークンで未計上=計上漏れ上限でも<1円)。累計約1.2円(予算15円/30円以内)。
モデル: 最新世代系(Luna=`gpt-6-luna`、TTS=`gemini-3.8-flash-lite-tts`=Production既定)。

## 共有ファイルへの影響
- `er011_output/attempt_history.jsonl`: 各runで1行追記(`LOCAL_REWRITE_RECOVERY`、`segment_id=comment_2`、09:06:43 / 09:10:29)。既存行は不変。この追記は実経路の仕様(`_append_recovery_history`)で避けられない。
- `er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`: run1で追記(Production経路の既存telemetry)。
- `er011_output/local_rewrite_recovery/open256_runtime_run{1,2}/`: 実経路が固定pathへ書くため一時作成→run dirへ複製後に削除(既存artifactは不変更)。
- master audio store / human_review_queue / ledger: 変更なし(shared_files_changed.json参照)。`er052_output/ja_article_quality_model_allocation_trial_01/pages_playwright_evidence_01.json`のrun1中の変化は並行agentの更新(本タスクと無関係)。
