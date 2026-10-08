# 委任_06 結果(Stage R)  Status=PARTIAL(新6中4テーマのみresearch実施、うち2テーマはB3未生成、2テーマ未実行)

保存先: `er052_output/factlock_astra_e2e_trial_01/stage_r/`(TOPICS.md、topics.json、<slug>/、LEDGER_SCHEMA_CHECK.md、FROZEN_INPUTS_SHA256.json、COST_STAGE_R.md、OLD4_B3_DIFF.json)

## 1. テーマ別結果
| slug | topic(要旨) | VERIFIED | B3 | 費用 | 入替 |
|---|---|---|---|---|---|
| byd_recall | BYD 18万台超リコール(183,211台=唐系142,895+秦系40,316の合算、公告2件) | 11/11 | 生成(選択5件) | ¥13.53 | なし |
| openai_copyright | USA Today等のOpenAI提訴 | 8/8 | **未生成**(¥31.83で¥30ガード停止、台帳は完成) | ¥31.83 | なし |
| central_bank_mortgage | 中銀金利判断と住宅ローン | 11/11 | 生成(選択6件) | ¥22.90 | なし |
| inbound_tourism | 訪日外国人過去最高 | 11/11 | **未生成**(¥56.82で¥30ガード停止、台帳は完成) | ¥56.82 | なし |
| streaming_price | 動画配信値上げ | - | **未実行**(予算) | 0 | - |
| semiconductor_earnings | 半導体決算とAI需要 | - | **未実行**(予算) | 0 | - |
補欠入替は発生せず(VERIFIED<3件のテーマなし、research失敗なし)。
停止判断: 4テーマ累計で¥125.08となり、残り2テーマ(実測¥14〜57/テーマ)は¥130上限に収まらないため未実行。openai/inboundはB3段が約¥0.6で済むが、「1テーマ¥30超は当該テーマを止めて報告」に従い実行していない(台帳は凍結可能、B3は後続で約¥1.2)。

## 2. 旧4のB3再生成(凍結台帳から、B3段のみ)
- 台帳sha256は凍結値と一致(meta ea0ce587/hormuz 9bd6834e/space_weapons f172a253/small_bag 0cc8ca3f、コピー後に再照合)。open233側の同名台帳とも`cmp`一致。
- research非実行の証跡: 4本とも stdout に「既存Ledgerを再利用」、raw_usage_logは`storyline_b3`段のみ(各1call、research/ledger 0call)。費用 meta¥0.42/hormuz¥0.43/space¥0.56/small_bag¥0.38=計¥1.79。
- 旧B3との差: 全4本で本文は非同一(LLM再生成のため)。選択ID: meta・hormuz・small_bagは旧と同一集合、space_weaponsのみF-012→F-011に変更。字数は全4本で短縮(412→346、473→392、783→705、409→376)。台帳外の数字: hormuzの新Storylineに「約25時間後」(台帳HF-007は「約24時間48分後」=丸め。台帳外の数字を作る方向)。他3本は台帳外数字なし。旧B3は4本とも台帳外数字なし。
- 結論: 旧4の新B3は旧B3と別物(凍結B3は使えない)。後続の注記・旧新腕とも本stage_rの新B3を入力にすること。旧B3(sha凍結済み設計書記載)は参考扱い。

## 3. 台帳スキーマ点検(詳細`LEDGER_SCHEMA_CHECK.md`)
- 点検対象8台帳(streaming/semiconductorは台帳なし)。全件VERIFIEDのみ。date_or_period欄は8台帳すべてに存在(openai 8/8、inbound 11/11、meta 15/15、hormuz 12/12、space 22/22、small_bag 6/6は全記録、byd_recall 7/11・central_bank 10/11は一部記録で欠)。numeric_value欄は7台帳に一部あり(全記録ではなく数値を持つ記録のみ)、**small_bagのみ0件=代替規則(statement内主数字)の適用対象**。量語があるのにnumeric_value欄が無い記録は全台帳で0件。
- 代替規則(date): 欄が1件も無い台帳は0。byd_recall(4記録)・central_bank_mortgage(1記録)は欄の無い個別記録があり、スクリプトは警告しない(要Fable確認)。

## 4. 凍結sha256
`er052_output/factlock_astra_e2e_trial_01/stage_r/FROZEN_INPUTS_SHA256.json`(8テーマ分、LF正規化。openai/inboundのB3はnull、streaming/semiconductorは項目なし)。

## 5. 費用・所要時間
合計¥126.87(上限¥130、残¥3.13)。内訳`COST_STAGE_R.md`。所要時間: 最初の有効バッチ開始(start_epoch.txt)から旧4完了まで実行時間約9〜15分(2並列×2バッチ+旧4を2並列×2、概算。開始時刻はstart_epoch.txtのみ記録)。1テーマ¥30超: openai ¥31.83、inbound ¥56.82(web_search 16call+ledger 16call、他テーマは3〜13call)。

## 6. 未確認・Fable判断要
1. 新6が4/6止まり。streaming_price・semiconductor_earnings(各¥14〜57)と、openai/inboundのB3(約¥1.2)を追加承認すれば継続可能(追加予算要)。または補欠(コーヒー・最低賃金)は未実行のためテーマ数を8にするか判断が必要。
2. inbound_tourismはresearch+ledgerで¥56.8(検索16+検証16 call)と突出。topic文でデータ範囲を絞り再実行するか、費用許容か。
3. hormuz新B3の「約25時間」丸めは注記仕様v2では台帳外数字に当たりうる(unmapped扱い)。
4. 初回起動はシステムpython(.venv外)でdotenv欠落により即失敗(API支出0)。以後`.venv/Scripts/python.exe`使用。
5. 補欠入替の妥当性判断は発生せず。台帳の薄いテーマはなし(最小はsmall_bagの6件)。
