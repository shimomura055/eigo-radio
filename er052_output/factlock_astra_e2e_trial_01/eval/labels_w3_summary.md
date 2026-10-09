# 事後評価ラベル worker3 要約(openai_copyright / semiconductor_earnings / streaming_price)

- 管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_14c(2026-10-09)。ラベル本体: `labels_w3.jsonl`(140行、`label_source=sonnet_w3`)。API支出0、git未操作。
- **ラベルはSonnetの暫定推測であり、確定扱いしない。** 台帳(`runs/<theme>/shared/ledger.txt`)とのテキスト照合のみで付け、人間確認・判定線評価・VALIDATED宣言は行っていない。基準は`docs/pm/open233_materiality_criteria_2026-10-03.md`(重大/軽微/問題なし)。
- jsonlの列: theme, arm, level, stage, claim_id(文), label(Y=真に問題[重大/軽微]/N=問題なし/UNDECIDABLE), severity(重大/軽微/問題なし/判断不能), origin(Writer/B3由来/AMBIGUOUS由来/Checker/Checker artifact), en_origin(ja_source/translation), rewrite_needed, evidence, confidence, tool_result(元の検出)。「n_claims」「n_occurrences」付きの行は同質の複数claimを1行に集約。
- 注意: Checker JSON内のJA説明が一部文字化けしていたため、EN claim本文と台帳で判断した。

## 1. テーマ x 腕 要約表(行数ベース。集約行あり)

| テーマ | 腕 | JA(FC指摘/(ii)の真偽) | EN(deviation_check指摘の真偽) | Checker(候補の真偽、Rewrite) | 最終本文の残存(重大/軽微) | STOP等の根拠 |
|---|---|---|---|---|---|---|
| openai | 旧 | FC 0件。(ii)2件=問題なし。R2の訓練セット曖昧さ(軽微)がEN Advで検出->JA_RECHECK発火 | Adv attempt1 MAJOR1=軽微、再生成後Adv/Std=0 | Adv: S1候補4(+1)全て偽陽性、Rewrite0。Std: 候補11、真の軽微2(見出しAI models一般化[未修正で残存]、In one lineの主体曖昧)、Rewrite1(後者、実質不要の任意改善) | Adv 0/0、Std 0/1(見出し) | なし(完走) |
| openai | 新 | FC(R0-R2、B1前後とも)0件で見逃し2(B1前: CMI除去の主体が「モデルの出力」[軽微/境界]、B1後: 見出し「AI訴訟は…」一般化[軽微])。(ii)0 | pre-B1 Adv MAJOR1=軽微(境界)->B1回復。post-B1 Adv MAJOR1(見出し)=軽微->B1上限でSTOP | Checker未実行 | 出荷なし。不出荷Adv本文: 重大0/軽微1(見出し) | EN Adv STOP: 根拠は軽微のみ(過剰ブロックの疑い)。AMBIGUOUS・B3由来ではない(台帳にAMBIGUOUSなし、unmapped 0) |
| semiconductor | 旧 | R2 FC MAJOR3件中、真の問題1(軽微: ネットワークが企業売上に登場)、偽陽性2(一般用語定義・売上/利益定義)。must-fix1回で完走。(ii)最終4件は全て台帳F4/F5内(偽陽性)、うち1件に範囲拡張の低確信軽微 | Adv/Std 0 | Adv: S1候補8全て偽陽性。Std: 候補10中、真の軽微1(低確信)。**断片BLOCKING2件=小数点分割アーティファクト->Rewrite2(両方不要)、うち1件が限定句「not the whole semiconductor segment」を削除=Checker起因の軽微劣化** | Adv 0/1(低確信)、Std 0/2(Checker起因1含む) | なし(完走) |
| semiconductor | 新 | R0 FCは0件で見逃し(「AI半導体売上高の予想ではありません」=F5と不整合、軽微/境界)。R1 FC MAJOR1(「登場するのは三つ」)=軽微/境界、R2で解消。R2は重大0/軽微0。(ii)0 | Adv MAJOR1(「この発表だけでは両者のつながりは説明されない」)=**問題なし**。B3 qualifier由来。B1は上限3/3で拒否->STOP | Checker未実行 | 出荷なし。不出荷Adv本文: 重大0/軽微0 | EN Adv STOP: 根拠は偽陽性(問題なし)。**B3由来**(`unmapped_claims`のqualifier「因果関係を付け加えないこと」が文の源)。AMBIGUOUS(F1)由来ではない |
| streaming | 旧 | FC 0件。(ii)1件=問題なし。時制(新規9/23は調査基準日前に開始済みなのに未来形)の軽微(低確信、未検出) | Adv/Std 0 | Adv: 候補16全てACCEPTABLE、偽陽性。Std: BLOCKING4件は全て小数点断片アーティファクト->Rewrite4。真の軽微3(旧価格の未来形、年額のPremium/米国限定欠落)は改善、1件(Premium月額差額$2.50の文)は`deterministic_delete`で**文ごと削除=Checker起因の軽微劣化**+二重空白 | Adv 0/2(低確信)、Std 0/2(Checker起因1含む) | なし(完走) |
| streaming | 新 | FC 0件。(ii)0。見出しの米国限定欠落(軽微、JA・EN共通) | Adv/Std 0 | Adv: QUALITY4(真の軽微1[見出し]、F07関連の修辞1[問題なし、AMBIGUOUS由来]、断片2[アーティファクト])。Std: QUALITY4(真の軽微2[「各人で別の日」過一般化、「価格表=支払額」第三者請求例外欠落])。Rewrite0、M3保護0 | Adv 0/1、Std 0/3 | なし(完走) |

## 2. 重大Fact見逃し一覧(最終本文に残ったもの)

- **0件**。6テーマ腕(出荷本文あり4、不出荷2)の全文照合で、台帳と矛盾する数値・主体取り違え・否定反転・新規具体事実は見つからなかった(Sonnetの照合範囲で。確定ではない)。
- 重大側にぶれる可能性のある「境界」4件(いずれも重大とは付けず軽微、confidence 0.45-0.55。人間確認の優先候補):
  1. openai 新 pre-B1: CMI(著作権管理情報)除去の主体が文法上「モデルの出力」(F4はOpenAI)。criteria重大(2)主体の取り違えの字面に当たる。
  2. semiconductor 新 R0: 「会社が示した次の数字は、AI半導体売上高の予想ではありません」(F5は次四半期AI半導体217億ドル見通しを記載)=否定の反転の字面。R0 FCは見逃し、R2で消滅。
  3. semiconductor 新 R1: 「登場するのは三つ」(F5欠落の網羅性誤り)。R1 FCが検出しR2で解消。
  4. streaming 旧: 新規契約者の新価格が調査基準日前に開始済みなのに未来形(低確信)。
- 軽微の残存(最終出荷本文のみ): openai旧Std=見出し一般化1; semiconductor旧Adv=caveat範囲拡張(低確信)1、Std=限定句削除(Checker起因)+caveat範囲拡張2; streaming旧Adv=時制+年額限定(低確信)2、Std=Premium差額文削除(Checker起因)+時制2; streaming新Adv=見出しの米国限定1、Std=見出し+「各人で別の日」+「価格表=支払額」3。

## 3. STOP / B1回復の真偽

| 事象 | 指摘の真の重大度 | 起源 | 回復後に解消したか |
|---|---|---|---|
| openai新 B1回復#1(trigger=Adv MAJOR CMI主体) | 軽微(境界) | Writer(ja_source) | 指摘文は解消(新JAは「OpenAIが著作権管理情報を除去」)。ただし新JA見出しの一般化(軽微)で再度MAJORとなり、1記事1回上限でSTOP |
| openai新 EN Adv STOP(post-B1見出し) | 軽微 | Writer(ja_source) | 回復枠なし。**軽微のみでSTOP=過剰ブロックの疑い** |
| semiconductor新 B1拒否/EN Adv STOP | 問題なし(偽陽性) | **B3由来**(qualifier) | trial上限3/3で拒否。回復しても同種表現が再生成される可能性(推測) |
| semiconductor旧 R2 FC MAJOR3->must-fix | 軽微1+問題なし2 | Writer | must-fix1回でR2再生成、attempt2 COMPLIANT。再生成は全面別稿(台帳全Factを網羅) |
| openai旧 JA_RECHECK | 軽微 | Writer(ja_source) | 再生成後Adv/StdともCOMPLIANT |

## 4. Checker Rewrite の要否(3テーマ旧腕Standardで計7件)

- Rewrite 7件(openai1、semiconductor2、streaming4)。重大を直したRewriteは0件。真の軽微を直したのは4件(openai L1主体、streaming旧価格の過去形2・年額限定1)で、いずれも任意改善(軽微は必須修正ではない)。
- **小数点での文分割断片(「$29.」「$11.」「$2.」「$189.」など)が独立claimとなりBLOCKING化し、6件のRewriteがこの断片起因**。うち2件で新たな軽微劣化(semiconductor: 限定句削除、streaming: Premium差額文削除)。runnerの文分割の挙動であり、実装修正はしていない。Fableでの欠陥判断要。
- 新腕streamingはRewrite0・BLOCKING0で、Stage 2 QUALITY止まり(真の軽微5をそのまま許容)。M3保護はこの3テーマでは0件。旧腕openaiの「影」5件(changed_actor除外)は全て台帳一致の正しい記述で、保護しても真の問題の救出にはならない。

## 所見(3行)

1. 3テーマ6腕のラベルでは重大な事実誤り・見逃しは0。STOP/B1/再生成の発火根拠は軽微(openai新2、openai旧1)または偽陽性(semiconductor新1: B3 qualifier由来)で、人手介入の一部は軽微指摘に起因(推測、要人間確認)。
2. 旧腕Checker Standardの「BLOCKING->Rewrite」は小数点文分割断片によるアーティファクトが主(6/7件)で、うち2件はRewriteが限定句・差額文を削除する劣化を生んだ。新腕は断片がQUALITY止まりでRewriteに至らず。
3. 新腕の「3テーマで重大0」は、Fact LockでF5/F1等を選別外にした副作用(semiconductor新R0/R1のF5不整合、軽微/境界)とB3 qualifier由来のSTOPという新しい失敗モードも示す。人間確認推奨: openai新Adv(CMI主体と見出し)、semiconductor新Adv(B3 qualifier文)、streaming旧StdのRewrite後本文。
