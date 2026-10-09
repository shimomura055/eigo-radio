# Opus独立技術レビュー(条件A)要約: WRITER-DEV-RISK-FLAGGER-DESIGN-01

- 対象: `er052_output/writer_dev_risk_flagger_01/`(DESIGN_RISK_FLAGGER_01.md v1、casebank、detectors/)
- 保存日: 2026-10-09(委任_02で保存。Fableから受領した所見要約。Opus所見は全件採用、ユーザーKPIの定義は変更しない)
- 注: 本書はFableから渡された14所見+推奨実行順の要約であり、Opus原文全文ではない。

## 所見(14件)

1. スキーマ不一致でD0がクラッシュし、出典パスがLLM入力へ漏えいする(`case_to_unit`が実スキーマ`fact{id,text,src}`・`context{before,after,source}`と不整合)。
2. 集計がKPIを計算できない(type_label/known_incidentが不在、splitなし、Recall_human等が未実装)。盲検のLABEL_KEYSも不足。
3. D0のK01検出はcasebankのFact強制採用による作為。D1map(D0近似で該当Factだけ渡す方式)は英語記事×日本語台帳で破綻 -> D1fullに一本化。
4. KPI4のRollbackはトートロジー(保留はK01のみ、語彙に逐語が入っている)。
5. casebankモードは実タスクと別物 -> 当該記事の全台帳を渡す。
6. タイプ別専用Detectorの適用先をラベルで選ぶのは漏えい。
7. D0の誤Flag構造(一般否定・価格定型句・block前方一致)。和集合に入れるのはrollback方向のみにする。
8. D2が『問題なし』に逃げられる -> D2rank(上位3文を必ず列挙)、D1にFlag上限。
9. Recall_humanを主、Recall_allを副にする。保留の人間確認済み重大は実質2件(K02・K11)。
10. FPR_clearの分母が易しい -> hard-negative(重大と同一Factの忠実文)を別掲。
11. Flag数は(unit,sentence,type)と固有文数の両方で数える。見出しを削除しない。
12. 予算見積は推論token実測後に更新する。
13. 項目7(Production Checkerを残す合理性)にはChecker判定の回収が必要。KPI5裁定用紙に所要分数欄を足す。
14. 記事単位に既知重大が0件 -> 既知重大を含む元記事を記事モードへ(保留側の元記事は最終評価のみ)。

## 推奨実行順(P0〜P5)

| 段階 | 上限 |
|---|---|
| P0 | ¥0 |
| P1 | ≤ ¥30 |
| P2 | ≤ ¥250 |
| P3 | ≤ ¥250 |
| P4 | ≤ ¥150 |
| P5 | ≤ ¥120 |
| 予備 | ¥200 |

## Fable判断(委任_02への指示)

- Opus所見は全件採用。ユーザーKPIの定義は変更しない。P0修正(¥0) -> P0' D0実測(¥0) -> P1パイロット(≤¥30) -> P2要素Trial(≤¥250)、P2完了でSTOPして報告。保留セットは流さない。
- 反映先: `er052_output/writer_dev_risk_flagger_01/DESIGN_RISK_FLAGGER_01.md` v2 §13。
