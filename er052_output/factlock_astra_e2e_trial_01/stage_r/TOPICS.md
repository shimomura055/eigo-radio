# Stage R topic文(新6+補欠2)
2026-10-09 委任_06。形式は前回E2E(gpt6_wiring_e2e_01 run_02)の `Current news/lifestyle topic: ...` に揃え、「web検索で確認できた事実のみ・推測禁止」の指示を付加。原文は `topics.json`。
| slug | テーマ(ユーザー確定) | 備考 |
|---|---|---|
| byd_recall | BYDが18万台超をリコール、ブレーキペダル部品の欠陥 | 台数(183,211は要検証)・対象車種・製造期間・欠陥原因・安全リスク・事故有無・是正策を指定 |
| openai_copyright | USA TodayなどがOpenAIを著作権侵害で提訴 | 「提訴段階であり侵害認定ではない」を明示、主体・主張・裁判ステータスを指定 |
| central_bank_mortgage | 中央銀行の金利判断と住宅ローンへの影響 | どの中銀かはresearcherに任せた(最新判断を採用) |
| inbound_tourism | 訪日外国人数が過去最高水準に | |
| streaming_price | 動画配信サービスの値上げが続く | |
| semiconductor_earnings | 半導体大手の決算とAI需要の行方 | どの企業かはresearcherに任せた |
| coffee_prices (補欠1) | コーヒー価格の高騰 | 入替時のみ使用 |
| minimum_wage (補欠2) | 最低賃金の引き上げ | 入替時のみ使用 |
旧4(META/ホルムズ/宇宙兵器/ミニバッグ)は凍結台帳を再利用しresearchを呼ばない。B3再生成に渡すtopicは各凍結台帳の元topic(META/ホルムズ=旧entry_pointのtheme、宇宙兵器=旧entry_pointのtheme、ミニバッグ=run_02のtheme)。


## 委任_07 追記(2026-10-09、費用抑制のため対象を1社・1イベントに絞った修正案。旧案は上表のまま残す。原文は topics.json の `streaming_price_v2` / `semiconductor_earnings_v2`)
| slug | 修正topic要旨 |
|---|---|
| streaming_price (v2) | 直近の値上げ発表1件(1サービス)に限定。旧新料金(プラン別)・適用日・対象市場・会社が述べた理由のみ。他サービス比較・契約者反応は対象外 |
| semiconductor_earnings (v2) | 主要AIチップメーカー1社の直近四半期決算発表1件に限定。売上・データセンター/AI部門売上・次四半期ガイダンス・AI需要への会社側発言のみ。アナリスト予測・他社は対象外 |
