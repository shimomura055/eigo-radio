# BUDGET_LOG_01 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_01, 2026-10-24 JST)

上限: 15円(委任文)。実費: **約8.0円**(推計。Azureはtool内の送信秒×0.0444円/秒、OpenAIは公開単価からの概算で、OpenAI分はTrial scriptがcost loggerを持たないため実測ログなし)。

| # | 作業 | API | 内訳 | 費用 |
|---|---|---|---|---|
| 1 | 原因究明(a)(b)(c)(d)(e)、census、M1/E1/E2/B/F/Cのオフライン再判定、ローカルWhisper、F1/F2解析 | なし | 保存wav・保存ASR・Ledger再利用 | 0 |
| 2 | 候補A: OpenAI `gpt-4o-mini-transcribe` を routing.transcribe(prompt=...) で48呼出(実窓8本x3条件+masking対照8語x3条件) | OpenAI ASR | 約3.6分x$0.003/分 | 約1.6円 |
| 3 | 候補Aのmasking対照音声生成: OpenAI `tts-1` 8クリップ(約440字) | OpenAI TTS | 約$0.0066 | 約1.0円 |
| 4 | 候補C: Azure Speech STT 22呼出(実窓8x2条件+対照6)、送信120.8秒 | Azure | 120.8秒x0.0444円 | 5.36円 |
| 合計 | | | | **約8.0円** |

- 事前: `tools/stop_scope_check_01.py --managed-id ASR-OOV-HOMOPHONE-ROOT-CAUSE-01` rc=0(`stop_check_00.json`、有料run前`stop_check_paid_01.json`)。再起動0・外部停止0・原因不明rc≠0 0回。
- 日次(JST 10-24): 把握分約610円+本委任約8円=約618円/1,000円。個別Cap15円内。
- Azure利用ログ(Trial専用): `work/raw_usage_log_trial.jsonl`(本番logと分離)。
- 使用モデル: Primary=Production routing(`gpt-4o-mini-transcribe`)、Secondary=Azure Speech STT(Production)、ローカル=faster-whisper small、TTS対照=OpenAI tts-1(旧世代。例外理由=別系統の実発話で「別語を言う音声」を作るためで、比較評価の対象ではない)。
