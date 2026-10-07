# 2026-10-08 OPEN-233-PAIRWISE-JUDGE-MODEL-TRIAL-01 委任_01(T4、Fableから、転記)

Management-ID: OPEN-233-PAIRWISE-JUDGE-MODEL-TRIAL-01(委任_01)。目的: リンク済み(文, fact)対に対する狭い整合判定の精度を、現行判定モデルと別モデルで比較、上限¥30(¥27でSTOP)。

## 並行タスク(衝突回避)
commit用workerが並行(`er052_output/open233_{reversal_detect_01,link_precision_01}/`・`stage2_01/v3/`・docs/pm配下を個別add)。本委任の書込先: `er052_output/open233_pairwise_judge_01/`、`docs/pm/pairwise_judge_01/`、delegation_log。runner/checker/SSOT/ACTIVE_TASK/RESULT_PACKET編集禁止、git禁止。自分の同時プロセス<=2。held-outは手順4まで開かない。

## 背景・仮説
T3でCheckerは文→factのリンクをほぼ正しく付けている(support+related dev 19/21、held-out 14/14)が既知NG文を「整合」と誤判定。段階2の「同じモデルに重さを再判定」は失敗。仮説H: 判定単位を「1文x1 factの狭い対判定」にし、かつ判定モデルを変えると、既知NG検出率が上がり、対照文の誤検出は低く保てる。Writer・Checker本体は変えない(測定のみ)。

## 作業
1. 事前登録(`docs/pm/pairwise_judge_01/preregistration_T4.md`、時刻付き): 対象=dev既知NG located 29のうちoracle fact特定(約21)+対照同数(型を揃え、seed固定)。形式=1文x1 fact、出力 verdict in {contradicts, asserts_unstated, consistent, unclear}+根拠1行。条件=(A)現行判定モデルx狭い対判定、(B)別モデルx狭い対判定、(参考)現行Stage1/2保存判定。各3回反復。指標: 既知NG検出率(verdict!=consistent)、対照誤検出率、3/3一致率、重大2件(jb9k-n3、89wf)。合格: 検出>=15/21 かつ 誤検出<=4/21 かつ 3/3一致>=80%。費用<=¥30。held-out 1回。
2. 実行(dev)・費用記録。3. 分析(型別、現行保存判定との差、誤検出実例5件、asserts_unstatedの出方)。4. held-out 1回(方向のみ)。5. `er052_output/open233_pairwise_judge_01/T4_RESULT.md`(事前登録照合、PASS/FAIL、含意は事実のみ、限界: N小・oracle目視・モデル差と形式差の交絡)。6. T-0: 委任文保存+check.json。

## 報告
12行以内: 使用モデル(A/B)、検出率・誤検出率・一致率、重大2件、型別要点、PASS/FAIL、held-out方向、費用、ファイルパス。
