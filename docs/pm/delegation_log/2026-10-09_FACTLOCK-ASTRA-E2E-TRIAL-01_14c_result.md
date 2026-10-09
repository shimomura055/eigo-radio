# 委任_14c 結果 FACTLOCK-ASTRA-E2E-TRIAL-01(2026-10-09) 事後評価ラベル worker3(openai_copyright / semiconductor_earnings / streaming_price)

- Status: ラベル付け完了(暫定、`label_source=sonnet_w3`)。API支出0、git未操作。Production変更なし。判定線評価・VALIDATED宣言なし。
- **ラベルはSonnetの推測であり確定扱いしない。** 台帳テキスト照合のみ。人間確認前提。

## 成果物
- `er052_output/factlock_astra_e2e_trial_01/eval/labels_w3.jsonl`(140行)
- `er052_output/factlock_astra_e2e_trial_01/eval/labels_w3_summary.md`(要約表、重大見逃し一覧、STOP/B1真偽、Rewrite要否、所見3行)
- 本書。一時スクリプトはscratchpad(`w3/`)のみ(リポジトリ外)。runs配下・他worker出力・SSOT本体は未編集。

## 結果の要点(詳細はsummary)
1. 6テーマ腕(出荷本文あり4、不出荷2)で、台帳と矛盾する重大なFact誤り・見逃しは0件(Sonnet照合の範囲)。重大側にぶれる境界は4件(openai新pre-B1のCMI主体、semiconductor新R0/R1のF5不整合、streaming旧の時制)を軽微(確信0.4-0.55)としてflag。
2. STOP/B1/再生成の根拠: openai新EN Adv STOP=軽微(見出し一般化)、openai新B1発火=軽微(境界)、semiconductor新EN Adv STOP=問題なし(偽陽性、**B3 qualifier由来**、AMBIGUOUS由来ではない)、openai旧JA_RECHECK=軽微。AMBIGUOUS(streaming F01/F07、semiconductor F1)由来の重大/軽微の指摘は0(Checker QUALITYのF07関連1件のみ、問題なし)。
3. semiconductor旧R2 FC MAJOR3件の完走経緯: R2 attempt1で3 MAJOR(真の問題は軽微1、偽陽性2)->must-fix1回(previous_response_id連鎖)->R2再生成(全面別稿)->attempt2 LEDGER_COMPLIANT(prior_issues 3件全解消)->JA完走。
4. 要Fable確認(欠陥候補): 旧腕Checker Standardで、小数点(「$29.」「$11.」「$2.」「$189.」)での文分割断片が独立claimとなりBLOCKING化、Rewrite7件中6件がこの断片起因。うち2件(semiconductor: 限定句「not the whole semiconductor segment」削除、streaming: Premium月額差額$2.50文を`deterministic_delete`で削除+二重空白)がCheckerが生んだ軽微劣化。実装修正は未実施(範囲外)。
5. 新腕のFact Lock選別(F5/F1を落とす)が、Writerの網羅性・否定の表現(semiconductor新R0/R1)でF5と不整合を起こした可能性(軽微/境界、推測)。

## 限界・注意
- Checker JSONのJA説明が一部文字化けしており、EN claim本文と台帳で判断。
- 出荷されなかったEN Advanced本文は`deviation_check`のpromptから復元して照合。old openaiのJA原本(JA_RECHECK前)も`ja_*_attempt1.json`のpromptから復元(runs配下の`ja_writer/*.md`は再生成後の版で、pre-recheck版ではない)。
- 集約行(n_claims/n_occurrences付き)は同質の複数claimを1行にまとめたため、行数と元claim数は一致しない。
- 人間確認の優先候補: openai新Adv(CMI主体と見出し)、semiconductor新Adv(B3 qualifier文)、streaming旧StdのRewrite後本文。
