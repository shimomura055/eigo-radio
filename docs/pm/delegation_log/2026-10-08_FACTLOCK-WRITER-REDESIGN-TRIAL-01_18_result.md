# 委任_18 結果: OpenAI Batch API は Astra Revise(R1/R2)量産に使えるか(事実整理のみ、判断はFable)

日付 2026-10-08 / API生成支出 ¥0(HTTP取得のみ、Batch投入なし) / SSOT・Production・git 無変更
生ドキュメント保存先: `er052_output/factlock_writer_trial_01/astra_pricing_01/raw_batch/`(`SHA256SUMS.txt`、`FETCH_NOTE.txt`)
取得日時: 2026-10-08 16:45-16:46 JST。出典URLは全て `https://developers.openai.com/api/docs/...`(.md版。platform.openai.com/docs は同URLへリダイレクト)。ファイル名は `guides_batch.md` 等。
check_delegation_prompt.py 結果: **FAIL**(必須セクション4件欠落[事前指定Read一覧/Grep一覧+手順/実行コマンド全文/報告形式]、固定ブロックE-1/D-1/G-1/F-1欠落、TTS関連warning2件)。指示どおり続行。

## 1. 事実表(出典の引用付き)
| 項目 | 値 | 出典(raw_batch内) | 引用 |
|---|---|---|---|
| completion window | **`24h`のみ** | guides_batch.md / ref_batches_create.md | "For now, the completion window can only be set to `24h`" / "Currently only `24h` is supported." |
| 所要の保証/典型 | 24時間以内。典型時間の数値記載は**なし**(「often more quickly」のみ) | guides_batch.md | "Each batch completes within 24 hours (and often more quickly)" |
| 1ジョブ上限 | 50,000リクエスト、入力ファイル200MB | guides_batch.md Rate limits | "A single batch may include up to 50,000 requests, and a batch input file can be up to 200 MB" |
| 1ファイル=1モデル | 入力ファイルは単一モデルのみ | guides_batch.md | "each input file can only include requests to a single model" |
| 対応エンドポイント | `/v1/responses`, `/v1/chat/completions` ほか(embeddings, completions, moderations, images, videos) | guides_batch.md / ref_batches_create.md | "`/v1/responses` (Responses API)" |
| gpt-6-astra の Batch 対応 | **Supported** | models_gpt-6-astra.md | Endpoints表 "Batch / v1/batch / Supported"、"Responses / v1/responses / Supported" |
| Astra Batch queue上限(キュー入力トークン) | Build 3,000,000 / Launch 200,000,000 / Grow 15,000,000,000 | models_gpt-6-astra.md | "Batch queue limit" 列。自組織の現行tierは**未確認** |
| Batch作成レート | 2,000バッチ/時 | guides_batch.md | "You can create up to 2,000 batches per hour." |
| 出力トークン上限・標準枠 | 出力上限なし。標準レート枠は消費しない | guides_batch.md | "currently has no output-token limit ... will not consume tokens from your standard per-model rate limits" |
| bodyパラメータ | 各行bodyは基底エンドポイントと同一 | guides_batch.md | "the parameters in each line's `body` field are the same as the parameters for the underlying endpoint" |
| reasoning.effort(high)のBatch内利用 | 明示記載**なし**(上記bodyの一般規則のみ。Astraはeffort low/medium/high/xhigh/max対応) | models_gpt-6-astra.md | Batchでeffortが有効という明示文は**未確認** |
| `previous_response_id` のBatch内利用 | Batchガイド・APIリファレンスに言及**なし = 未確認** | guides_batch.md(grep該当なし) | — |
| 失敗/期限切れ時の課金 | 期限切れ時、未完了リクエストはキャンセル。**完了済みリクエストのトークンのみ課金**。期限切れ行はerror fileに`batch_expired`で出力。自動再投入の記載なし(再実行は自分で再投入) | guides_batch.md "Batch expiration" | "You will be charged for tokens consumed from any completed requests." |
| 個別リクエスト失敗 | 失敗行はerror fileへ、成功行のみoutput file | guides_batch.md | "one response line for every successful request line" |
| ステータス | validating/failed/in_progress/finalizing/completed/expired/cancelling/cancelled | guides_batch.md | cancelは"up to 10 minutes" |
| 結果取得 | `output_file_id`/`error_file_id`をFiles APIでダウンロード、状態は`batches.retrieve`でポーリング。output fileは完了30日後に自動削除 | guides_batch.md | "automatically be deleted 30 days after the batch is complete" |
| 価格(Astra、USD/1M: input/cached/cache write/output) | Standard 10/1/12.5/50。Batch・Flex 5/0.5/6.25/25(Standardの50%)。Fast 20/2/25/100(2x)。Ultrafast 60/6/75/300 | models_gpt-6-astra.md(Standard・50%・2x)、委任_17取得`extracted_pricing.json`(pricing page、2026-10-08 16:38、sha256 161df7d8...) | "Batch and Flex are priced at 50% of Standard rates. Fast mode is priced at 2x the applicable rates." Ultrafast=60/300は`extracted_pricing.json`のみ(本委任で再取得なし)。Batch 5/0.5/25は再確認済(Standardの50%) |
| 長文脈 | 入力272K超は入力・cache 2x、出力1.5x | models_gpt-6-astra.md | 本用途(入力<1K tokens)では無関係 |
| Flex | Responses/Chat Completionsの同期リクエストに`service_tier:"flex"`。価格=Batchレート。**遅延の数値保証なし**("slower response times and occasional resource unavailability")。容量不足時`429 Resource Unavailable`(**課金なし**)。SDK既定timeout10分(例は15分)。429時はexp. backoff再試行、または`service_tier:auto`/省略でstandard再送 | guides_flex-processing.md | "Flex processing is in beta with limited model availability."。Astra対応はpricing pageのFlex行と、ガイド例が`model:"gpt-6-astra"`であることによる |
| Fast mode(旧Priority) | `service_tier:"fast"`(または"priority")。2x価格。**Astraにlatency SLAなし** | guides_fast-mode.md | "Fast mode for GPT-6 Astra does not include a latency SLA." "up to 2.5x"はGPT-5.6 Sol記述で、Astraでの倍率は**未確認** |
| Ultrafast | Astra向け最速tier。Astra既定TPM: Build 500,000 / Launch 1,000,000 / Grow 5,000,000。WebSockets推奨 | guides_ultrafast-mode.md | "Ultrafast mode is the fastest service tier ... broadly available for GPT-6 Astra" |
| Background mode | `background:true`で非同期実行、GETでポーリング(queued/in_progress)。**専用価格の記載なし**。Astra対応の明示は**未確認**(例示はGPT-5.2系)。`store`省略/false時は約10分後に削除 | guides_background.md | "execute long-running tasks on models like GPT-5.2 and GPT-5.2 Pro" |

## 2. 未確認項目一覧
1. Batchでの`reasoning.effort=high`動作の明示記載(一般規則からの推定のみ、実測なし)。
2. Batch内での`previous_response_id`の扱い(ドキュメント無記載)。
3. Batchの典型所要時間(公式数値なし。投入禁止のため実測もなし)。
4. 自組織のusage tier(=Astra Batch queue上限・Astra RPM/TPM)。
5. Flexの典型遅延/429発生率(公式数値なし)。
6. Background modeのAstra対応・価格。
7. Fast modeの対Astra速度倍率。
8. `platform.openai.com/docs/api-reference/batch`は403(保存物はエラーページ)。代替に`developers.openai.com/api/reference/resources/batches/methods/create.md`を取得(ref_batches_create.md)。
9. 実請求額(ダッシュボード)との突合(下記5節の注意)。

## 3. 現行パイプライン・リポジトリ事実(Grep)
- OpenAI Batch APIの利用実績: リポジトリ内に`purpose="batch"`・`/v1/batches`を使う自前コード**0件**(.venv除く)。`client.batches.create()`・Batch実績は**Gemini TTS Batch**(`er006_batch_tts_wiring_01.py`、google.genai)のみ。OpenAI側のBatch運用実績・実測遅延はなし。
- Production JA Writer: `er019_family_x_ja_writer_o_r1_r2_01.py`。**モデルは`gpt-5.6-luna`(WRITER_MODEL=vfl01.MODEL、L48)でAstraは現Production未配線(Trial専用)**。`call_fresh`(Original、L209)と`call_with_previous_response_id`(R1/R2、L223)はいずれも同期の`client.responses.create()`。R1→R2は`previous_response_id`で連鎖(失敗時のみ前記事全文貼付のfallback、L21-23/L366-375)。各段の間にFact Check(`vfl01.run_deviation_check`)・must-fix1回再生成・記号Gate(`detect_prohibited_symbols`)が挟まる(L278-343, L391-)。呼び出し側は`er019_family_x_entertainment_production_runner_01.py::run_ja_writer`(L182-)。
- Astra Trialの呼び出し(`astra_revise_matrix_01/tools/run_matrix.py` L62): `client.responses.create(model=MODEL, reasoning={"effort":"high"}, input=msgs)`、**`previous_response_id`不使用**(ログ`previous_response_id_used: False`)。各段は前段本文をuserメッセージに貼る方式であり、そのままBatch行の`body`にできる形。R1→R2の依存は「R1出力本文をR2入力へ貼る」のみ。
- Batch化に必要な改修箇所(実装なし、列挙のみ):
  1. `call_fresh`/`call_with_previous_response_id`を同期関数から「JSONL行生成→Files upload→`batches.create`→状態ポーリング→output取得」へ(戻り値が`response`オブジェクト前提=`.id/.model/usage`参照箇所の差し替え。Batch出力は`response.body`のdict)。
  2. `previous_response_id`連鎖はBatch間で使えるか未確認のため、fallback_full_text方式(前段全文貼付)を主経路にする設計変更。
  3. 段間のFact Check/must-fix/記号Gate(同期、各段直後に判定)をジョブ境界で分割するための状態保持(再開ポイント、`out_dir`中間成果物)。
  4. `er005_cost_logger`の`logging_context`(同期呼び出しに紐づく)をBatch usage集計へ適合。
  5. 予算ガード`efam.assert_budget_ok`の段間チェック位置。
  6. 失敗/期限切れ行(error file)の再投入と上限回数(既存retry上限との整合)。
  7. 1ファイル=1モデルのため、Original/R1/R2がAstraで揃うなら可、Fact CheckがLuna等なら別ジョブ。
- TTS Batchで既に許容している遅延・運用形態(CURRENT_SPEC.md L1937、L2306): 「Batch APIは正式リリース後の実量産における正式TTS方式」、DEV/Trial等はStandard同期が既定(L2306)。「1 Batch jobの完了待ちは実測91〜167秒/件で、Standard(通常数秒)より大幅に遅い。ASR不一致でretryが発生するsegmentでは、retry回数分この待ち時間が積み重なる(実測: 英語segmentが4回attemptで522秒)。総生成コストは下がるが総生成時間は増える可能性があるため、量産運用時は監視すること。」(L1937)。実装は1job=1item、ポーリング間隔5秒・タイムアウト600秒(`er006_batch_tts_wiring_01.py` L55-56)で**同期的に待つブロッキング運用**。既存許容は「数分以内に返るGemini Batchの同期待ち」で、**24h窓を前提とした運用は未経験**。

## 4. 適用パターン別整理
最悪所要は公式のcompletion window(24hのみ)からの算術。典型値は公式に無いため推測しない。
| パターン | 公式記載の遅延 | 単価(Astra、1M tokens in/out) | 対応可否 | 最悪所要(R1+R2) | 必要改修 |
|---|---|---|---|---|---|
| (a) Standard同期(現状Trial) | 保証値の記載なし。**実測**(X系列R1/R2): R1 31.9/63.4/51.6秒、R2 51.5/46.5/48.3秒、1記事R1+R2は平均約98秒 | 10 / 50 | Astra対応(確認済) | 実測平均約98秒/記事(保証上限なし) | なし |
| (b) Batch 2段(R1→R2) | 各ジョブ24h以内、典型は「often more quickly」のみ | 5 / 25(50%) | Astra・/v1/responsesともSupported | R1ジョブ24h + R2ジョブ24h = **最大48時間**(各段にwindowが掛かる場合の算術上限。投入・取得の待ちは別) | 3節の1-7。effort=high/previous_response_idは未確認(Trialは貼付方式で後者不要) |
| (c) Flex(同期+`service_tier:"flex"`) | 遅延上限の保証なし、429は課金なしで再試行要 | 5 / 25(Batchと同額) | Responses対応、ガイド例にAstraあり | 公式上限なし(不定)。SDK timeout既定10分→例15分 | `service_tier:"flex"`追加、timeout延長、429時のbackoff/standard再送(既存retry上限と整合要)。同期構造はそのまま |
| (d1) Fast(`service_tier:"fast"`) | Astraにlatency SLAなし | 20 / 100(2x) | Responses対応 | 公式保証なし | パラメータ追加のみ |
| (d2) Ultrafast | 遅延数値の記載なし("fastest service tier")、Astra TPM Build 500K | 60 / 300(6x) | Astra対応、WebSockets推奨 | 公式保証なし | WebSocket経路 |
| (d3) Background mode | 非同期+ポーリング。Astra対応・価格・遅延は**未確認** | 未確認 | 未確認 | 未確認 | `background:true`+ポーリング |

## 5. 費用試算(Astra X系列=系列A、3記事のR1+R2実測トークン × tier単価、USD/JPY=160)
実測トークン(usage_log.jsonl、stage=gen、series=A、round1-2、cached=0): 入力 計4,083 / 出力 計10,909(6呼び出し=3記事×R1,R2。記事: matrix_01の1本[テーマ名はログに無し]、hormuz、small_bag)。`output_tokens`を請求対象とした(`reasoning_tokens`はその内数扱い、ログのcost式と同じ)。
| tier | 3記事合計 | 1記事あたり |
|---|---|---|
| Standard(10/50) | $0.5863 = **約¥93.8** | 約¥31.3 |
| Batch(5/25) | $0.2931 = 約¥46.9 | 約¥15.6 |
| Flex(5/25) | $0.2931 = 約¥46.9 | 約¥15.6 |
| Fast(20/100) | $1.1726 = 約¥187.6 | 約¥62.5 |
| Ultrafast(60/300) | $3.5177 = 約¥562.8 | 約¥187.6 |

注意: `usage_log.jsonl`の`cost_jpy`(X系列R1+R2合計 ¥46.90)は5/25単価で計算済み(例: 576in/1170out→(576×5+1170×25)/1e6×160=¥5.1408と一致)。委任_17で旧推定(5/25)がStandard単価の誤りと判明済みのため、過去報告の「実費」(約¥48.5、約¥64.9等)はBatch/Flex相当の値で、Standard実行ならその約2倍(上表)。実請求額(ダッシュボード)との突合は未実施=未確認。

## 6. 事実としての整理(判断はFable)
- Batch 2段は価格50%引きだが、公式の時間保証は各ジョブ24h以内のみで、R1→R2の2段なら算術上限48h。典型値の公式記載はなく、OpenAI Batchの実測・運用実績はリポジトリに無い。既存のTTS Batchは同期待ち(timeout 600秒)運用で、24h窓の運用経験は無い。
- Flexは同額(5/25)で同期構造を維持できるが、遅延上限は公式に無く429(課金なし)が起こりうる。
- Production Writerは現状Luna(Astra未配線)。Batch化は段間のFact Check/Gateが同期前提のため、ジョブ境界での状態保持が必要。
- 所要時間(本委任): 約15分、API生成支出¥0。
