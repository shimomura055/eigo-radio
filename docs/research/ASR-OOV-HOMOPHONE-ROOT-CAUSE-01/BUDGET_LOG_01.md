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

---
# 委任_02 追記 (2026-10-24 JST) 上限40円。実費 約11.7円(推計含む)

| # | 作業 | API | 内訳 | 費用 | 計測方法 |
|---|---|---|---|---|---|
| 5 | F1 ’修正の影響分析、E2 v2実装、全件リスト、保存データ再判定、Whisper局所転写 | なし(ローカル) | 保存データ・Ledger再利用、faster-whisper small | 0 | - |
| 6 | trial02: Ledger登録8語(既存正式経路、Perplexity sonar) | Perplexity | 8 call、入力4,768/出力2,165 tokens | 約7.5円 | token=cost log実測、request fee($5/1,000件)は公開価格仮定。**cost logger実記録は8件のperplexityのみ** |
| 7 | trial02: 正例18+負例5 clip TTS(`gemini-3.8-flash-lite-tts`)+Primary ASR(`gpt-4o-mini-transcribe`) | Gemini/OpenAI | 23 clip、合計88.8秒 | 約2.8円(上限推定3.7円) | **cost loggerを `init_logger` のみで起動し `install` を忘れた(私の手順ミス)ため、TTS/ASRの実記録が無い**。同日の実測単価(neg2: TTS 0.10円/clip、ASR 0.019円/clip)とclip秒数からの再構成。やり直しは有料runの再起動に当たるため実施せず |
| 8 | neg2: 追加音声負例 7 clip(TTS+ASR) | Gemini/OpenAI | `cl.install`で実記録 | **0.84円**(TTS 0.70+ASR 0.13) | cost log実測(`work/trial02_neg2/cost/usage_log.jsonl`) |
| 9 | azure arbiter: 3エンジン目の聞き取り4 clip | Azure Speech STT | `cl.install`で実記録 | **0.60円** | cost log実測(`work/trial02_azure_arbiter/cost/usage_log.jsonl`) |
| 合計 | | | | **約11.7円**(最大12.6円) / 上限40円 | |

- 事前: `stop_check_paid_02.json`(rc=0)、各有料scriptの先頭でも `stop_scope_check_01.py` rc=0を確認。再起動0・外部停止0・原因不明rc≠0 0回。有料run=trial02(1起動、JST 21:2x頃終了)→neg2(1起動)→azure arbiter(1起動)。いずれも別目的の新規run(同一runの再起動ではない)。
- 日次(JST 10-24): 把握分約618円+委任_01分(含)+本委任約11.7円=約630円/1,000円。個別Cap 40円内。
- 共有state: trial02は共有Ledgerを変更しない(Trial用コピー `work/trial02/ledger_trial.json`へ向け、実行前後sha256一致[`shared_state_changed: {}`])。
- 供給側G 1語あたり約0.94円(Perplexity)。

---
# 委任_03 追記 (2026-10-24 JST) 上限10円。実費 約3.2円(cost loggerの実記録＋単価換算)

| # | 作業 | API | 内訳 | 費用 | 計測方法 |
|---|---|---|---|---|---|
| 10 | E2W fail-closed化・1語位置判定、単体test、本run長segment再評価(Whisper small、20 attempt中E2単独受理3件のみ実行) | なし(ローカル) | 保存wav・保存ASR | 0 | - |
| 11 | OF-OOV-11: 正例10+負例20 clip TTS(`gemini-3.8-flash-lite-tts`、Aoede/Charon/Erinome)+Primary ASR(`gpt-4o-mini-transcribe`) | Gemini/OpenAI | `cl.install`で実記録(`work/trial03/cost/usage_log.jsonl`: TTS 30呼出・114.2秒・出力2,761token、ASR 30呼出) | 約2.75円 | 音声秒×0.01907円/秒(本run実測単価 17.60円/総TTS秒)=2.18円+ASR 30×0.019円(neg2実測単価)=0.57円。**トークン実記録あり、円額は換算** |
| 12 | 誤受理3clipの第3エンジン確認(Azure STT、PhraseListなし) | Azure | `cl.install`で実記録(`work/trial03_azure_arbiter/cost/usage_log.jsonl`: 3呼出・9.68秒) | 約0.43円 | 9.68秒×0.0444円/秒 |
| 合計 | | | | **約3.2円** / 上限10円 | |

- 事前: `stop_check_03.json`(rc=0)、各有料scriptの先頭でも`stop_scope_check_01.py` rc=0。再起動0・外部停止0・原因不明rc≠0 0回。有料run=trial03(1起動、JST 21:42開始)→azure arbiter(1起動、起動間隔>150秒)。他agentの「有料run(TTS)進行中」flagは`docs/pm/ACTIVE_TASK.md`に開始時点で無し(確認のみ・編集0)。
- 日次(JST 10-24): 把握分約630円+本委任約3.2円=約633円/1,000円。個別Cap 10円内。
- 共有state: 共有Ledger・Master Audio Store等には触れていない(Trial用Ledgerコピー`work/trial02/ledger_trial.json`を読むのみ)。
