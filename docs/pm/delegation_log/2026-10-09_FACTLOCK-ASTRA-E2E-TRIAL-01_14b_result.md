# FACTLOCK-ASTRA-E2E-TRIAL-01 委任_14b 作業記録(事後評価ラベル付け worker2)

- 日付: 2026-10-09 / 担当: Sonnet worker2 / 範囲: small_bag, byd_recall, central_bank_mortgage × 新旧両腕
- API支出 ¥0、git操作なし、runs配下・SSOT・他worker出力(labels_w1*/labels_w3*)は未編集(読み取りのみ)
- 成果物: `er052_output/factlock_astra_e2e_trial_01/eval/labels_w2.jsonl`(242行)、`eval/labels_w2_summary.md`
- **ラベルは Sonnet(`label_source=sonnet_w2`)の推測。確定扱いしない。判定線の評価・VALIDATED等の宣言なし。**

## 結果要約
- 重大(Ledgerと食い違い読者に重大な誤解)と暫定判定したものは両腕・3テーマで0件。最終(出荷側)本文に残るのは軽微のみ(新腕: byd 2〜3件、small_bag 0、central は本文なし。旧腕: small_bag 3、byd 3、central 0)。
- STOP 4件(small_bag旧Std、byd新Std、byd旧Std、central新R0)はFCのMAJOR起点だが暫定ラベルでは軽微(うち central新R0の2件は軽微/重大の境界)。軽微起因の人手介入だった可能性が高い。
- central新 R0 STOP: 「30年固定」→「固定型」→「長期固定ローン」への言い換えと、再生成で新たに「レンジ」が脱落した「3.75％から4.00％に」がMAJOR判定。数値は台帳と一致し重大な誤りは無い(詳細はsummary §3)。
- Checker: 7 run・一意claim 97件中の真の軽微9件、重大0。新腕bydのRewrite 1件は不要(比喩ジョーク削除、BLOCKINGは偽陽性)。M3保護の便益は確認できず(個別claim特定不可)。
- B1回復: 担当3テーマの新腕では発動なし。案B(small_bag旧・byd旧): 発火理由は軽微と推定、再生成後に解消したが別の軽微でStandard STOP。M1(byd新Std): 要約の軽微を解消、本文の別の軽微でSTOP。

## Fableへの注意点(集計への影響)
1. 旧腕 small_bag/byd の(ii)件数は案B前JAの値(ii.jsonのtext_sha256が現行revision2.mdと不一致、案B前本文は未保存)。AGGREGATEの「M 新規具体主張(ii)最終JA」旧腕値はこの2テーマで最終JAを表していない。
2. B3由来(unmapped_claims)・AMBIGUOUS由来は3テーマとも対象記録なし。`origin=B3`は注記済みbrief Storyline由来の意味。
3. 人間確認推奨: byd_recall(新旧: 見出し断定の境界、軽微起因STOP)、central_bank_mortgage新(R0 STOP)、small_bag旧(軽微3件残存+STOP)。

## 判断に使った手順(再現用)
台帳・注記済みbrief・各run JSON(FC/deviation_check/ii/shadow/m3/Checker JSON)を読み、Checker JSONの stage2_results と stage1_coverage.candidate_filter.verdicts を機械的に全件列挙して、Sonnet判断を override 表で上書きする方式で `labels_w2.jsonl` を生成(生成スクリプトはスクラッチパッド内の一時物、リポジトリ外)。
