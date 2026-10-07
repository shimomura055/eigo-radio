# 2026-10-07 OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 評価者X 委任文(要旨再構成)

管理ID: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01(評価者X、Fableが別インスタンスとして起動)
注記: 実際の委任本文(原文)は本委任_03のSonnetは保持していない。ここは `eval/eval_pack/` の割当・READMEから再構成した要旨(再構成であり原文ではない)。

## 範囲・禁止
API呼び出し・記事生成・SSOT編集・git操作・記事本文の編集は禁止。Meta全10記事の fact MUSE-HC-012 の3値ラベル(correct/ambiguous/misread/not_selected)のみ、JA R2 / EN Checker前 / EN最終 の3箇所で独立に判定(重大/軽微のrubric評価は行わない)。

## 事前指定Read
- `eval/eval_pack/assignment_rollback_X.md`(meta 10本)、`rollback_label_template.json`(criteria逐語)
- `er052_output/open233_control_checker_polysemy_trial_01/eval/eval_pack/README_EVALUATOR.md`(B3 rubric全文+読み替え、checker_rewrites・rollback_labels追加フィールド)、`article_schema.json`、`scores_template.json`、`rollback_label_template.json`、`unprovided_checklist_<slug>.md`

## 出力
`eval/rollback_x/meta_<code>.json`(rollback_label_template.json の形式、10件)

## 盲検
条件(Note有無・variant・Checker発火)は開示されない。MAPは開けない。他評価者の結果は読まない。
