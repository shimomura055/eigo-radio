# 注記者の参照禁止リスト(FACTLOCK-ASTRA-E2E-TRIAL-01 委任_08、2026-10-09)
原則: 許可は「自分のプロンプトファイル1つのRead(1テーマにつき1回)」だけ。それ以外はリポジトリ全体が禁止。返答は本文で返し、ファイルは作らない(保存は呼び出し側)。

## 許可(注記者Aの例。Bは `__B.md`)
- `er052_output/factlock_astra_e2e_trial_01/annotation/prompts/<slug>__A.md` のRead(10テーマ、各1回)。機械可読版は `audit_config.json`。

## 禁止(例示。許可以外すべてが禁止)
- 他方の注記者のプロンプト(`__B.md` を読むA、またはその逆)と `annotation/out/` 全体(相手の返答)
- `er052_output/factlock_astra_e2e_trial_01/` 配下の上記以外すべて: `stage_r/`(台帳・B3・storyline_b3・fact_selection_evidence・full_ledger)、仕様v1/v2本体・USER_SUMMARY・OLD4_EXPECTED・OPUS_POINTS、`ANNOTATION_DELEGATION_TEMPLATE_v2.md`、PREREGISTRATION、DESIGN、各スクリプト、`old4_expected_eval_01.json`、`spec_v2_evidence/`、`annotation/` の他ファイル
- 過去のFactLock関連: `factlock_writer_trial_01/briefs`、`selected_brief_factlock*`、`ANNOTATION_LOG*`、`annotate_briefs*`、`astra_revise_matrix_02*`、`prep_inputs*`、`core_numbers*`、`annotation.json`(過去の注記結果)
- 旧凍結出力・評価・結果: `er0*_output/` 全体、`ER-*_REPORT.md`、`*RESULT*`、`*eval*`
- SSOT・運用文書: `CURRENT_SPEC.md`、`DECISION_LOG*.md`、`OPEN_ITEMS*.md`、`HISTORY_INDEX.md`、`CLAUDE.md`、`docs/pm/` 全体、`.claude/`
- ツール: Grep、Glob、Bash、Write、Edit、WebSearch、WebFetch、mcp__*、Agent(Readは上記の許可ファイルのみ)

## 監査
`audit_strict_01.py`(厳格: 許可Read以外のtool_useを全て違反、解釈できない行も違反)+ 基底 `../b3_annotator_audit_01.py`(禁止語照合)。違反があればその注記者の当該返答は採用せず、STOPしてFableへ報告(RUN_ANNOTATION.md 5節)。
