# E3 評価② Entertainment比較(OPEN-233-LEDGER-CLARITY-P-TRIAL-01、n=1、判定はFable)
Before=er019 meta run_03 b1b/JA、After=P' after_pprime_01 b1b/JA。証跡: E3_pairwise.json / E3_cost.json / E3_before_ent.json / ent_metrics.json。

## 1 決定論表(¥0、機械照合)
| 指標 | Before | After | 差 | 基準 | 照合 |
|---|---|---|---|---|---|
| EN b1b 文数 | 27 | 28 | +3.7% | - | - |
| EN b1b 語数 | 379 | 396 | +4.5% | - | - |
| EN b1b 平均文長(語) | 14.04 | 14.14 | +0.7% | ±20% | OK |
| EN b1b TTR | 0.4776 | 0.4773 | -0.1% | ±20% | OK |
| JA R0(original)12字逐語率 | 0.1518 | 0.1846 | +3.28pt | +5pt以内 | OK |
| JA R2(revision2)12字逐語率 | 0.0843 | 0.2486 | +16.43pt | +5pt以内 | NG |
注: 00c記載のBefore b1b(26文/362語/13.92/0.4917)は別集計。今回は同一ツールで再計算した値を使用(差は小さく結論不変)。Before standard/neg2(a2系)は最終記事の対応After a2が未生成のため比較対象外(00c値: standard 35文/9.57/0.5134、neg2 31文/11.32/0.4872、参考)。00dテンプレのBefore 0.1518はR0の値。R2のBeforeは今回算出。
JA文字数: Before R0 731/R2 878、After R0 715/R2 881。

## 2 pairwise(順序入替2 call、台帳非提示、X/Y伏せ)
model=gpt-5.6-sol(Writerはgpt-5.6-luna。別model・別tierだが同じOpenAI系統。既存ヘルパにOpenAI以外の呼出経路なし=完全な別ベンダーではない)。
| call | X | Y | story | tempo | natural | soft(説明的・硬さの少なさ) | overall |
|---|---|---|---|---|---|---|---|
| 1 | Before | After | Y(After) | Y | Y | Y | Y |
| 2 | After | Before | X(After) | X | X | X | X |
After優=2/2(全5軸)。Afterが「劣る」判定=0/10(0%)。理由要旨: Afterはrelay metaphorで物語が明確・文のリズムが多様・会話的な接続、Beforeは同じ論点の言い換え反復。基準(劣る率≤25%かつ4軸いずれも過半数でない)=充足。
注意: n=1記事・同一系統judge・位置入替で一貫(位置バイアス小)。judgeはLLM単独。

## 3 逐語コピー所見(JA、台帳との12字以上連続一致、上位5件。空白除去後)
After R0(7箇所/計132字): 26字「人間の請負業者による人種差別的な言及が含まれていたと」/25字「、一部のテストでは、人間が電話をかけた場合の成功率」/22字「コールセンターの請負業者に意図せず共有される」/18字「「humanconcierge」を試」/14字「、訓練を受けたエージェントが」
After R2(10箇所/計219字): 32字「情報がコールセンターの請負業者に意図せず共有される可能性があると」/32字「、通話記録に人間の請負業者による人種差別的な言及が含まれていたと」/30字「によると、一部のテストでは、人間が電話をかけた場合の成功率が」/30字「は、humanconcierge機能を当面ロールバックしたと」/24字「請負業者が電話をかけるテストを、適切な開示なしに」
Before R0(6箇所/計111字): 31字「訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを」/24字「スタッフによる人種に関する不適切な発言があったと」/17字「情報がコールセンターの契約スタッフ」/14字/13字
Before R2(4箇所/計74字): 24字「スタッフによる人種に関する不適切な発言があったと」/21字「訓練を受けた人間の契約スタッフが電話をかけ」/17字/12字
所見: 一致箇所は数・最長長とも増加(R2: 4→10箇所、最長24→32字、合計74→219字)。内容は事実記述文(請負業者・人種差別的言及・成功率)の台帳表現踏襲が中心。P'はclaimに具体語(請負業者等)を書くため、Writerがその語をそのまま使う傾向が出ている。Before側の「契約スタッフ」は台帳の語と一致している箇所のみ拾われている。物語・比喩部分への侵食は一致一覧からは見えない(下記EN抜粋と整合)。台帳丸写し傾向は「R2で増加」(基準NG)と「EN記事の語彙・文長・pairwiseには悪化なし」が併存。
ENは台帳がJAのため8語逐語率=0.0(Before/After共、参考・合否に使わない)。

## 4 Fable抜粋(EN b1b、逐語、見出し除く。mid=中央付近3文)
Before冒頭: It was a small twist. Behind a service that lets people ask AI to make phone calls, humans were actually making the calls. That kind of test was being carried out.
After冒頭: Having AI make phone calls for you. Just hearing that, it sounds like a useful service from the future. But in Meta's internal tests, an unexpected handoff was happening on some of those calls.
Before中盤: And if this was not properly explained, users had no way to know whether they were talking to AI or a person. They were enjoying the convenience of AI, only to find a human on the other end of the call without realizing it. That was what was happening behind the scenes.
After中盤: This handoff also looked strong in the numbers. According to a Meta vice president, in some tests, the success rate when humans made the calls reached 95% to 98%. Calls made by AI had a lower success rate.
Before結末: The more useful a service is, the less it should hide the people working behind the scenes. The Muse case showed us this simple but important point. Some calls made through Meta's AI assistant were actually handled by humans, without users being properly told.
After結末: Muse was the main character this time. But in the end, the one who drew attention was the human phone operator who appeared from behind the scenes. Meta's AI phone assistant handed some calls to human contractors, raising privacy concerns despite their higher success rates.
(Before/Afterでtopic切り口が異なる。Afterは数値の開示が中盤に出て説明寄りの文もあるが、冒頭は掴みがある。)

## 5 基準照合(機械的)と所見
- ±20%基準(文長・TTR): OK。JA12字逐語率: R0 OK(+3.28pt)、R2 NG(+16.43pt)。pairwise: OK(劣る0%)。
- 所見: EN記事のEntertainment(文長・語彙多様性・pairwise)に悪化の証拠なし、むしろ同系統judgeではAfter優。一方JA R2の台帳逐語一致が基準を大きく超過(要Fable判断: 主指標をR0とR2のどちらで見るか、00d記載は「original.md または R2」)。STOP条件「Entertainment品質に明確な悪化」には、EN側では該当しない。JA側逐語率NGは「台帳丸写し」懸念の候補だが、一致の中身は事実記述が中心。
- 制約: n=1、judge同系統、pairwiseは実費¥3.11で上限¥3を¥0.11超過(下記)。
実費: pairwise 2 call計¥3.1104(call1/2は E3_pairwise.json)。上限¥3超過=¥0.11。
