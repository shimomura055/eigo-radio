管理ID: FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_17(gpt-6-astra の正式単価調査、API生成支出¥0)。日付 2026-10-08。ユーザー指示「調べて。」

## 目的
これまでの費用表で gpt-6-astra の単価を「gpt-6-sol × 2.5(2.00/0.20/10.00 USD per 1M → 5.00/0.50/25.00)」と**仮置き**していた。正式単価を一次情報から確認し、実測トークン数で費用を再計算する。

## 禁止事項
- LLM生成のAPI支出 ¥0。価格表の取得(HTTP GET)は可。
- SSOT・Production コード(er006_model_routing_contract_01.py、er005_output/cost_baseline_01/pricing_snapshot.json を含む)は**変更しない**(登録は Fable/ユーザー判断後の別委任)。git 操作をしない。
- 委任文(このメッセージ全文)を一字一句そのまま `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_17.md` に保存し、`docs/pm/tools/check_delegation_prompt.py --file <path>` を実行して結果を記録(FAILでも続行)。
- 結果は `docs/pm/RESULT_PACKET.md` と `docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_17_result.md` に書く。

## 手順
1. 一次情報の取得を試みる(順に、取得できたものを採用):
   a. OpenAI 公式価格ページ(https://openai.com/api/pricing/ および https://platform.openai.com/docs/pricing、https://platform.openai.com/docs/models/gpt-6-astra 等)を `curl`/PowerShell `Invoke-WebRequest` で取得し、`gpt-6-astra` の input / cached input / output(あれば batch・priority も)$/1M tokens を抽出。取得したHTML/JSONの該当部分を `er052_output/factlock_writer_trial_01/astra_pricing_01/raw/` に保存(取得URL・日時・SHA付き)。
   b. OpenAI API の models エンドポイント(`GET https://api.openai.com/v1/models/gpt-6-astra`、既存の環境変数 OPENAI_API_KEY を使用)で、価格情報が返るか確認(返らない場合は「価格情報なし」と記録)。
   c. リポジトリ内の既存記録: `DECISION_LOG.md`/`CURRENT_SPEC.md`/`docs/pm/` を Grep(`astra`、`6-sol`、`単価`、`pricing`)して、過去に astra 単価が確認された記録がないか確認。sol 単価の確認記録(DECISION_LOG 2026-09-29)の出典も再確認。
   d. 上記すべてで取得できない場合は「未確認」と明記し、推定のままである旨と、取得を阻んだ理由(ネットワーク制限・ページ構造等)を記録。
2. 再計算: 採用単価(正式 or 推定)で、以下の実測トークン(各 `usage_log.jsonl` / `.response.json`)から円換算を出し直す(USD/JPY=160):
   - Step 1 `step1_chat_repro_01`(F2_astra, F3_astra)
   - `astra_revise_matrix_01`(meta A/B r1〜r3)
   - `astra_revise_matrix_02`(hormuz/small_bag A/B r1〜r2)
   - 系列X(=A)の R1+R2 の3記事平均、1セット換算(現行約¥52 Standard / ¥43 Batch に加算)
   旧推定値との差分を表にする(reasoning tokens は output に含める。cached input があれば区別)。
3. 判断材料: 正式単価が取れた場合、routing contract / pricing_snapshot への登録案(値・出典URL・取得日時)を result に書く(登録自体は行わない)。

## result に書くこと
採用単価と出典(URL・取得日時・該当箇所の引用)、または未確認の理由、再計算表(旧推定 vs 新)、1セット換算の更新値、登録案、check_delegation_prompt 結果、所要時間。
