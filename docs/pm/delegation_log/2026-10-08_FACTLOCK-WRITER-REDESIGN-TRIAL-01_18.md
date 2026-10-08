管理ID: FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_18(OpenAI Batch API を Astra Revise(R1/R2)の量産に使えるかの調査。API生成支出¥0、一次情報のみ)。日付 2026-10-08。ユーザー指示「Batch処理が量産で現実的かどうか、もう少し踏み込んで調べてください。」

## 禁止事項
- LLM生成のAPI支出 ¥0(ドキュメントのHTTP取得、`GET /v1/models` 等の無料の参照系呼び出しは可。Batch ジョブの投入は**禁止**)。
- SSOT・Production コードを変更しない。git 操作をしない。
- **推測で数値を書かない**。取得できた一次情報(公式ドキュメント・価格ページ・API仕様)だけを根拠にし、各数値に出典URL・取得日時・該当箇所の引用を付ける。取得できなかった項目は「未確認」と書く(Fable/ユーザー指示: 重要数値は確認済みの値のみ)。
- 委任文(このメッセージ全文)を一字一句そのまま `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_18.md` に保存し、`docs/pm/tools/check_delegation_prompt.py --file <path>` を実行して結果を記録(FAILでも続行)。
- 結果は `docs/pm/RESULT_PACKET.md` と `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_18_result.md` に書く。取得した生ドキュメントは `er052_output/factlock_writer_trial_01/astra_pricing_01/raw_batch/` に保存(URL・日時・SHA)。

## 調べること(一次情報: https://platform.openai.com/docs/guides/batch、https://platform.openai.com/docs/api-reference/batch、https://platform.openai.com/docs/pricing、https://platform.openai.com/docs/models/gpt-6-astra、rate limits ページ等)
1. Batch API の仕様: 完了保証時間(completion window の選択肢と上限)、実際の典型所要(公式に記載があれば)、1ジョブの上限(リクエスト数・ファイルサイズ)、対応エンドポイント(本プロジェクトが使う Responses API `/v1/responses` が Batch 対象か、Chat Completions のみか)、gpt-6-astra が Batch 対象モデルか、reasoning 設定(effort=high)や `previous_response_id` の扱い、失敗・期限切れ時の課金と再実行の扱い、結果の取得方法。
2. 価格: Batch 割引率(Standard 比)、Flex との違い(遅延・可用性・価格)、Priority/Fast tier の価格と位置づけ。gpt-6-astra の Batch 単価は委任_17 で取得済み(5/0.5/25)、再確認のみ。
3. 本プロジェクトへの適用性(事実ベースで整理、判断はFable):
   - Astra R1→R2 は逐次依存(R2 入力 = R1 出力)。Batch だと R1 ジョブ完了後に R2 ジョブを投入する2段構成になる。完了保証時間が各段に掛かる場合の最悪所要を、公式記載の completion window から計算(推測しない)。
   - 現行パイプライン(`er019_family_x_entertainment_production_runner_01.py`)の R1/R2 呼び出し部が同期呼び出し前提か(`previous_response_id` 使用の有無、ステージ間の依存)を Grep で確認し、Batch 化に必要な改修箇所を列挙(実装はしない)。
   - CURRENT_SPEC.md の「量産はBatch標準」(TTS)の記載箇所を Grep し、TTS Batch 運用で既に許容している遅延・運用形態を引用。
   - 既存の Batch 利用実績(リポジトリ内に OpenAI Batch API の利用コードや記録があるか Grep: `batches`, `/v1/batches`, `completion_window`)。
4. 代替案の事実確認: Flex processing の仕様(遅延・レート・価格)、Responses API の `background` モード(あれば)の仕様と価格。

## result に書くこと
- 事実表(項目・値・出典URL・取得日時・引用)。未確認項目の一覧。
- 適用パターン別の整理: (a) Standard同期(現状)、(b) Batch 2段(R1→R2)、(c) Flex、(d) その他公式に存在する方式。各々について、公式記載の遅延上限・価格・対応可否・必要改修箇所。費用は Astra X系列3記事の実測トークン(`astra_revise_matrix_01/02` の usage_log)×各 tier の確認済み単価で算出(USD/JPY=160)。
- check_delegation_prompt 結果、所要時間。
