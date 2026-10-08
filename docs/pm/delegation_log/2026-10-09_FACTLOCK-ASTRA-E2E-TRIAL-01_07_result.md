# 委任_07 結果(Stage R 残り)  Status=STAGE_R_COMPLETE(10テーマ全てVERIFIED>=5・B3生成済み)
保存先: `er052_output/factlock_astra_e2e_trial_01/stage_r/`

## 1. テーマ別結果
| slug | VERIFIED | B3 | 選択ID数 | 費用 | 状態 |
|---|---|---|---|---|---|
| byd_recall | 11 | 有 | 5 | ¥13.53 | 完了(_06) |
| openai_copyright | 8 | 有(_07) | 5 | ¥32.29 | 完了 |
| central_bank_mortgage | 11 | 有 | 6 | ¥22.90 | 完了(_06) |
| inbound_tourism | 11 | 有(_07) | 4 | ¥57.42 | 完了 |
| streaming_price(v2 topic) | 5(+AMBIGUOUS 2) | 有 | 6 | ¥34.97 | 完了(Disney+米国価格改定、research+ledger ¥34.46で¥35内) |
| semiconductor_earnings(v2 topic) | 5(+AMBIGUOUS 1) | 有 | 5 | ¥15.35 | 完了(Broadcom FY26 Q3) |
| meta / hormuz / space_weapons / small_bag(旧4) | 15/12/22/6 | 有(_06) | 3/3/5/3 | ¥0.42/0.43/0.56/0.38 | 完了 |
未完テーマなし。補欠入替なし。streaming/semiconductorのtopicは1社・1イベントに絞った(原文`topics.json` の `*_v2`、`TOPICS.md`に追記、旧案も残置)。

## 2. 累計費用
委任_06 ¥126.87 + 委任_07 ¥51.38 = **¥178.25**(見積¥100に対し+¥78.2)。委任_07単独は上限¥80内。原因: inbound_tourism ¥57.4(検索16+検証16 call)、openai ¥32.3、streaming ¥35.0(検索12+7 call)。見積は1テーマ約¥17想定、実測¥14〜57。詳細`COST_STAGE_R.md`。

## 3. 点検・凍結・明確化
- `LEDGER_SCHEMA_CHECK.md`(10台帳): 全件VERIFIEDのみ、量語ありでnumeric_value欄なしの記録は0件、warningsはsmall_bagのnumeric_value欄なしのみ。
- `FROZEN_INPUTS_SHA256.json`(10テーマ、LF正規化、全テーマselected_brief/evidence/full_ledgerあり)。
- `SPEC_V2_CLARIFICATIONS.md`((a)記録単位の代替規則、(b)丸めはunmapped_claims「新数値(丸め)」)。
- B3 briefの台帳外数字: hormuzの「25」のみ(他9テーマ0)。

## 4. 要確認(Fable判断)
- streaming/semiconductorの台帳にAMBIGUOUS記録(streaming F01,F07 / semiconductor F1)があり、`parse_ledger`のスクリプトはVERIFIEDのみ数える(記録数5)が、B3はAMBIGUOUSのF01,F07/F1(F1はsemiconductorで選択)を選択IDに含む。注記統合で「台帳外ID」扱いになる懸念あり(スクリプト側の扱いを確認要)。
- semiconductor F1は「最新決算の企業選定」自体がAMBIGUOUS(Micronが9月30日発表でBroadcom9月2日より後)。「leading AI chipmaker」の解釈次第で題材の最新性が揺れる。
- 未完テーマはないため8〜9記事で進める必要はなし(層別・判定線への影響なし)。
- 補足: B3 briefは全テーマ短い(3〜6事実)。

## 5. 所要時間・API支出
所要約5〜8分(4本並列、実行時間概算)。API支出¥51.38(上限¥80内)。Production変更なし、Astra・Writer以降・注記は未実施。
