# VALIDATION_01 (KP-GLOSS-ALIGNMENT-PRODUCTION-01 OF-231/232/234の有効性検証)

モデル: `gpt-6-luna`(`routing.require_model("A2_SUPPORT", SUPPORT_MODEL)`、現行世代の最上位/推奨系=本番ラインと同一。評価用に旧/下位モデルは使っていない)。実API合計 JPY1.18(予算JPY10)。

## 1. データ範囲の訂正(重要)
指示の『Parity 10記事の`keywords_canonicalized.json`(A'/M2下)』に相当する記録corpusは存在しない。Parity(`parity_02.json`)はM2候補供給(rows sha256)の再現確認であり、canonicalized recordを持たない。A'/M2下のcanonicalized recordはCoffee(er019/er071)の4件のみ。代わりに次の2種を用いた(いずれもJPY0):
- (A) 全er*_output `keywords_canonicalized.json` 226 record / 1,129 item / 714ユニーク(display,KP,gloss)三つ組(`census_01.json`)
- (B) 記録済みcanonicalization応答(`canonicalization_runtime_metadata.json`のattempts)を**案A'の窓で再判定**してPASS/REVIEW_REQUIREDになるもの153 attempt / 765 itemを、記録済み選定itemとmerge(`aprime_targets_01.json`)

## 2. 対象件数(JPY0)
| 集計 | record | item | 再整合対象 | 率 |
|---|---|---|---|---|
| (A)全er*_output | 226 | 1,129 | 7(ユニーク5) | item 0.6% |
| (A)うちM2P0 Family Z(er073) | 16 | 80 | 2 | item 2.5% |
| (A)うちCoffee(er019/er071) | 4 | 20 | 3 | item 15% |
| (B)A'窓再判定 | 153 attempt(8 record) | 765 | 11(ユニーク6) | item 1.4% / attempt(記事相当)7.2%(11/153) |
- 1記事(5 item)あたり対象を含む割合の実測は約7%(B)。Opus見積り30〜40%は本corpusでは再現せず(Coffee 4 recordに限れば3/4)。A'下の実運用データが少なく、記事ごとの率は不確実(7%〜40%の幅で費用を見積る)。

## 3. 再整合の実行結果(実API、`replay_high_01.json`)
対象: 実対象ユニーク8件(A'/census由来、うち2件はもともと整合している対照を兼ねる)を**2回ずつ**=16 eval、対照(KP==display・整合済み、forced投入)10、スロット罠1。1バッチ5 item×6バッチ。全バッチ1回でALIGN_PASS(retry0)。

実対象の目視(根拠1行):
| KP | Before | After(high) | 判定と根拠 |
|---|---|---|---|
| based on interviews | ～をもとにした(不整合) | インタビューをもとにした | 整合: interviewsを反映、スロット残存なし |
| based on interviews | 〜をもとにして(不整合) | インタビューをもとにして | 整合: 同上(活用語尾も保持) |
| based on interviews | インタビューをもとにした(整合) | 同一 | 無変更(過剰書換えなし)。補足: 委任_04のcensus replay時の表でBefore欄が再整合後の値だった誤記を、本表で上記の通り訂正 |
| raw-bean prices | 焙煎前のコーヒー豆(不整合: pricesが欠落) | 焙煎前のコーヒー豆の価格 | 整合: prices反映 |
| bring in a human helper | 人を呼んで加える(不整合: helperの意味が曖昧) | 人間の助っ人を加える | 整合: human helperを反映 |
| close around me | 周りから迫ってくる(弱い不整合: me欠落) | 私の周りを取り囲む / 私を取り囲むように迫ってくる(rep2) | 整合: meを反映(meの一般化漏れ自体はOPEN-357) |
| urge to watch | ～したい衝動(不整合: スロット+watch欠落) | 見たいという衝動 | 整合: watch反映、「～」除去 |
| locked into a narrow view | 狭い見方に閉じ込められる(整合) | 同一 | 無変更 |
- Before不整合: 6/8(75%)。After不整合: **0/16**(2回とも全件整合)。決定論チェック違反(スロット誤用)0/16。
- 対照10件(forced): 9件無変更、1件変更(`drop the fee`『料金案を取り下げる』→『料金をなくす』、意味がずれる方向の弱い書換え)。本番では対照は対象外(再整合に入らない)ため実害は無いが、**対象に入った整合済みitemのうち約1/10は不要に書き換えられうる**ことの目安。
- スロット罠(`declare something to be`): 『～を…だと宣言する』の「…」(承認規則が禁止)を『～を～だと宣言する』に是正。KPにsomething有り=「～」許可で通過。

## 4. 追加確認
- OF-234(b): 全1,129 itemで『KPが短くなり、displayの**内容語**が失われた』ケースは0件。displayとの語差が出る22 item(1.9%)はすべて人称代名詞の一般化(my/their/your→one's等)と助動詞beの脱落のみ。頻度が低く内容語欠落0のため、対象条件への追加は行わない(`census_01.json`)。
- 決定論チェックの母集団観察: KPにスロット語が無いのにglossに『～』がある item は全体で29/1,129(2.6%)。多くは`point to`『～を示す』等の辞書的な正当表記で、**対象itemにのみ**適用されるため影響は限定的(再整合対象8件×2で誤FAIL0)。

## 5. 1,000本あたりの不良見積り(統計的限界を明記)
- 前提: 1本=1記事セット=2レベル×5 KP。再整合対象率 item 0.6〜1.4%(A)(B)、Coffee実運用15%(n=20)。1,000本=10,000 KP item(2レベル)なら対象60〜140 item(Coffee並みでは最大1,500)。
- 再整合なし: 対象の約75%(6/8)が不整合 → 約45〜105 item/1,000本(item 0.45〜1.05%)。
- 再整合あり: 実測16 eval中不整合0。ただし標本はユニーク8件・各2回で独立性が弱く、rule of three(95%上限 ≈ 3/16 = 19%)でも上限しか言えない。上限で計算すると対象60〜140 itemのうち最大11〜27 item/1,000本(item 0.1〜0.3%)。実測点推定は0。
- 限界: ユニーク対象が少なく(8)、1記事に複数対象がある場合・長い記事・別トピックでの再現は未確認。量産初期はFAILED通知(`gloss_alignment_fallback_events`)を必ず確認すること。

## 6. effort比較(OF-232、切替はしない)
| 項目 | high(現行) | medium |
|---|---|---|
| 6バッチ合計費用 | JPY0.683 | JPY0.494(-28%) |
| 1バッチ(5 item)平均 | 0.114 | 0.082 |
| 実対象16 eval After不整合 | 0 | 0 |
| 決定論チェック違反 | 0 | 0 |
| 過剰書換え(対照10) | 1 | 1(同一item『drop the fee』) |
- medium実対象の表現例: raw-bean prices→『生豆の価格』(rep2)、close around me→『私の周りに迫ってくる』。すべて目視で整合(highと同等)。ただし標本が小さく、品質同等は**この標本での確認**に留まる。
- 費用差は1呼出あたり約JPY0.03、1記事セット(対象率40%・2レベル)で約JPY0.02。切替の費用メリットは小さく、Q同等の確証も限定的のため、**切替は提案しない**(Fable/ユーザー判断材料としてのみ記録)。

## 7. 費用再見積り(実測ベース、`cost_01.json`)
- 実測: 5 item/バッチ 約JPY0.07〜0.14(high)。量産では対象itemのみ(通常1〜2 item)なので1呼出 約JPY0.07〜0.12。以前の見積り(0.3〜0.5/呼出)は過大だった。
- 通常: 対象率 7%〜40% × 1呼出 約0.1 × 2レベル = **約JPY0.014〜0.08/記事セット**(70円上限の0.02〜0.11%)。
- 最悪(上限回数の再整合を全レベルで消費): 2回×2レベル×0.14 = 約JPY0.57/記事セット。
- 絶対最悪(外側redundancy retryも上限2=計3 attempt、全attemptで2回消費): 12呼出×0.14 = 約JPY1.7/記事セット(Opus見積り約2円と整合)。
- 恒久的単価増として: 通常0.1円未満/記事セット。上限70円に対し無視できる範囲だが、最悪ケースの1.7円は「1〜2円の単価増を軽視しない」原則上、FAILED通知の頻度で運用監視する。
