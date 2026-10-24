# FACT_CHECK_01 (FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_01, 2026-10-24)

出典: [G]=GIGAZINE https://gigazine.net/news/20261023-dopatan-wordgacha/ (curl取得、2026-10-24) / [W]=https://wordgacha.com/ (HTML meta description、`assets/i18n.js`のtitleNote・howRarity・howPull・howPacks・howMore・howIntro等のサービス自身の説明文) / Ledger=`er019_output/word_gacha/run_wg_01/research_ledger/`(VERIFIED 13/AMBIGUOUS 0/REJECTED 0)。
B3採用Fact(storyline_b3/selected_brief.md)=F03・F06の2件のみ(Min2方式)。本文の事実主張は下表の2件+導入の枠組みに限られる。

| 本文の主張(Std/Adv) | 出典 | 判定 |
|---|---|---|
| 英単語カードのレア度は7段階(C・UC・R・SR・SSR・UR・LR) | [G]「C、UC、R、SR、SSR、UR、LR」 / Ledger F03 | 一致 |
| よく使われる単語ほど低レア、使われない単語ほど高レア | [G]「よく見られる英単語ほどレアリティが低く…」 / [W]howRarity「毎日のように使う基本的な単語は C」 / F03 | 一致 |
| URのカード以上を引くとボーナス「Jackpot」が始まり、パックを続けて開封できる | [G]「UR以上だとジャックポットが始まります…何度も連続して10連パックを開封できます」 / F06 | 一致 |
| レアは学習上の優先度と別、レア度=使用頻度の並べ替え | [G]/[W]howRarity(使用頻度データwordfreqで決定)/ F12 | 一致(本文は「頻度」と「学習優先度」を分離) |
| ゲームだけでは「パックを開ける方に関心が移るか」は分からない | F10・F13(利用者調査・学習効果実験なし) | 一致(断定回避) |
| 導入の語り(良い生徒/財宝ハンターの比喩、「もう1回」等) | 本文の仮定・比喩であり事実主張ではない。「may/might」型の仮定表現 | 創作事実なし |

## 混同禁止3点の確認
1. ゲームを楽しめる≠学習効果が高い: 本文は学習効果を主張しない。「この仕組みだけでは…関心が移るか分からない」(IOLにも保持)。Ledger F13。
2. 派手な演出≠ドーパミン増加の実測: 本文に「ドーパミン増加」の記述なし(grep "dopamine"はタイトル中のサービス名「Dopa」のみ)。F11。
3. レア単語≠重要単語: 「A rare word does not have to be high on your study list」「Rarity ... not what learners should study first」と明示。F12。

## 創作0の確認
- 10連パック・連チャン継続率75%・ランク・実績・交換・単語テスト等はB3で不採用=本文に出ない。
- 本文中の数値は「seven levels」のみ(出典G/F03)。固有名詞は「Dopa English Word Gacha」(サービス名、F01)。
- 補足(Fable参考): [W]のi18nには「単語テスト(4択/つづり入力、忘却曲線に沿う復習)」が書かれているが、これはサービス自身の主張(第三者実証なし)で、本文には採用していない。公式ページ本文はResearchのWeb取得では読めず(SPA)、本検査でi18n.jsを直接取得してG記載内容(レア度・wordfreq・ジャックポット)と矛盾がないことを確認した。
