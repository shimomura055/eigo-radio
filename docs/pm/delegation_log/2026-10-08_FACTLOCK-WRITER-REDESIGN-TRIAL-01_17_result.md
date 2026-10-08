# FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_17 result(2026-10-08、astra正式単価調査、API生成支出¥0)

## 結論
gpt-6-astra の正式単価を OpenAI 公式価格ページから取得できた。**旧推定(sol x2.5 = 5/0.5/25)は誤りで、実際は sol x5(Standard 10/1/50)**。astra の過去費用は全て約2倍が正しい。

## 採用単価と出典(USD/1M tokens、Short context)
- 出典: https://platform.openai.com/docs/pricing (HTTP 200、developers.openai.com/api/docs/pricing 配信)、取得 2026-10-08 16:38 JST。ページ内 TextTokenPricingTables の astra 行と HTML table(`gpt-6-astra | $10.00 | $1.00 | $12.50 | $50.00 | (Long) $20.00 | $2.00 | $25.00 | $75.00`)。列は Input / Cached input / Cache writes / Output。
- 同ページの gpt-6-sol 行 = 2/0.2/2.5/10(DECISION_LOG 2026-09-29 の sol 単価 2.00/0.20/10.00 と一致 -> 列解釈の検証済み)。
- gpt-6-astra: Standard 10 / 1 / (cache write 12.5) / 50。Batch 5 / 0.5 / 25。Flex 5/0.5/25(Batchと同額)。Fast 20/2/100。Ultrafast 60/6/300。Standard Long context 20/2/25/75(本試験の入力は全て<1000 tokens で対象外)。
- openai.com/api/pricing/ は HTTP 403(過去と同じ)。models endpoint(GET /v1/models/gpt-6-astra)は HTTP 200 だが価格情報なし(id/created/owned_by/shutdown_date のみ)。
- リポジトリ内に astra 単価の確認記録なし(DECISION_LOG 12796付近は「403で未確認」、20291等は「sol x2.5の推定」)。pricing_snapshot.json / routing contract にも astra 未登録。
- 保存: `er052_output/factlock_writer_trial_01/astra_pricing_01/raw/`(取得HTML3件+models_gpt-6-astra.json)、`.../extracted_pricing.json`(抽出値、HTML SHA256 付き)。pricing HTML sha256=161df7d8126a8287e0c0c4bc80950f977ab6b54a597d9bced35baeedbbb3a807。

## 再計算(USD/JPY=160、reasoning は output に含まれる(ログ値で検算一致)、cached input は全て0)
| 区分 | astra calls | 旧推定(5/0.5/25) | 新(Standard 10/1/50) | 差 |
|---|---|---|---|---|
| step1_chat_repro_01 (F2_astra 5.58->11.16, F3_astra 8.13->16.26) | 2 | 13.71 | 27.42 | +13.71 |
| astra_revise_matrix_01 (meta A/B r1-r3) | 6 | 45.77 | 91.55 | +45.77 |
| astra_revise_matrix_02 (hormuz/small_bag A/B r1-r2) | 8 | 60.21 | 120.43 | +60.21 |
| astra 計 | 16 | 119.70 | 239.39 | +119.70 |
| 各試験の総実費(luna/sol/ii概算込み、usage_log合計) | | 22.27 / 48.48 / 63.54 | 35.98 / 94.25 / 123.75 | |
| 3試験合計 | | 134.29 | 253.98 | +119.70 |
注: matrix_02 の DECISION_LOG 記載¥64.92 は usage_log 合計¥63.54 に r0_small_bag 生成分を含む差と思われる(未精査、要確認なら別途)。matrix_02 の新総額は同比率で約¥125前後。matrix_02 予算上限¥80は新単価では超過扱い(結果の数値自体は不変)。

個別(新): meta A r1/r2/r3 = 10.28/16.85/15.00(A系列 R1-R3 = 42.13、旧21.07)。

## 1セット換算(系列X(=A) R1+R2、3記事平均)
- meta 27.13 / hormuz 33.09 / small_bag 33.58 -> 平均 **約¥31.3(Standard)**、旧推定 ¥15.6。
- Batch(5/0.5/25、-50%)なら **約¥15.6**。
- 現行1記事 約¥52(Standard)/約¥43(Batch)に加算: **Standard 約¥83(52+31.3)、Batch 約¥59(43+15.6)**。旧推定換算は Standard 約¥68。
  (Batch astra は Batch を使えば旧推定 Standard と同額。Batch利用可否(同期性・遅延)は別途要確認。)
- 旧記録「Astra 3段で約¥21〜25」は新単価で約¥42〜50、「R1+R2 約+¥12.8〜¥16.8」は約+¥25.6〜¥33.6。

## 登録案(未実施)
pricing_snapshot.json / routing contract に `gpt-6-astra`: standard{input 10.00, cached_input 1.00, output 50.00}、batch{5.00, 0.50, 25.00}、(参考 long-context standard 20/2/75)。出典 https://platform.openai.com/docs/pricing、取得 2026-10-08T16:38+09:00、extracted_pricing.json 参照。要判断: DECISION_LOG/REPORT 内の過去の「sol x2.5推定」記述の注記訂正(§106-108、20291/20307/20315行付近)は別委任。

## check_delegation_prompt
FAIL(保存した委任文に必須セクション「事前指定Read一覧」「Grep一覧+追記位置・更新位置の手順」「実行コマンド全文」「表(RESULT_PACKET形式)」と固定ブロックE-1/D-1/G-1/F-1が無い。委任文は逐語保存のため修正せず、続行)。

## 所要時間・その他
約10分。LLM生成API支出¥0(価格ページGETとmodels endpoint GETのみ)。SSOT/Productionコード/pricing_snapshot未変更、git操作なし。
