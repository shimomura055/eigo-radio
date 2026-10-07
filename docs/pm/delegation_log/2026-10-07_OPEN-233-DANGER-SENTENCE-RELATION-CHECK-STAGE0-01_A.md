# 2026-10-07 OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01 委任_A(既知の関係型NGの再分類+Opus所見保存+ユーザー決定のSSOT記録、¥0)

(保存注記: 受領した委任文の要旨保存。Opus所見の逐語は`docs/pm/opus_l2_review_stabilization_strategy_01.md`に保存し、ここへは複製しない。見出しは標準テンプレートに合わせて補完。)

## 管理ID
OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01(委任_A)

## 性質/到達上限Status/禁止事項
- 性質: read-only再分類+文書作成。API禁止(¥0)。Production変更なし、`APPROVED_FOR_PRODUCTION`なし。
- 並行タスク(衝突回避): 委任_B(危険文条件の検出率、`er052_output/open233_stage0_01/danger/`)、委任_C(関係抽出の反復安定性、`er052_output/open233_stage0_01/stability/`)が並行。本委任の書込先は`er052_output/open233_stage0_01/reclass/`、`docs/pm/opus_l2_review_stabilization_strategy_01.md`、`DECISION_LOG.md`(1エントリ追記のみ)、`docs/pm/stage0_01/`。ACTIVE_TASK/RESULT_PACKETは本委任が更新(B/Cは触らない)。git操作は本委任の最後に1回(個別add、B/Cの出力はaddしない)。
- 禁止事項: Agent/Subagent起動、B/Cの出力のadd、`git add -A`、無関係差分の編集。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0)
- E-1: 事前指定範囲だけを実行し、拡大が必要なら報告して止める。
- D-1: Production正式pathとDEV/Trial pathを区別し、Trial成果をProductionへ混入させない。
- G-1: 実行した検証の結果(実測)だけを報告し、未実行の想定でPASSと書かない。
- F-1: 詳細証跡は既存のer052_output構造に置き、RESULT_PACKETには短い要約だけ書く。
- T-0: 本委任文を`docs/pm/delegation_log/2026-10-07_OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01_A.md`へ保存し、check_delegation_prompt.pyで検証(FAILでも作業継続)。

## ユーザー指示(原文要旨、2026-10-07夜)
- 判断1=(A) Opus推奨経路を採用: Writerは単一パス自由生成のまま、危険文限定の関係検査+構造要素のRewrite置換禁止+否定・不在・全称・方向・主体の格下げ禁止+Writer自己注釈(振り分け用)+台帳側の動詞正規化。Fable当初案(2段Writer+全文関係diff)は撤回。
- 判断2=段階0開始を承認。ユーザーは約8時間不在。その間、予算¥1000でFable主体の自律改善ループ(段階0→方向が違えばOpusレビュー→新規計画→最初のテスト→OKなら進む/ダメなら再検証・再レビュー)。この間Opusレビュー回数は無制限。
- Fableの運用条件: Production変更・仕様原則変更・Safetyトレードオフは行わずSTOP/面白さの主指標(ユーザー盲検読み比べ)は夜間は取れないため代理指標のみ・非劣性未確認と明記/重大候補は人間確認パックへ/並列4単層以下/¥950で停止/各段階commit。

## 事前指定Read一覧
- `er052_output/open233_b3_trial_01/eval/articles/*.json`(55)、`er052_output/open233_control_checker_polysemy_trial_01/eval/articles/*.json`(18)、`er052_output/open233_ng_root_cause_01/eval/articles/*.json`(27、うちE2E_02由来15)、各`_private/MAP*.json`(出所特定用)
- `docs/pm/ng_root_cause_01/ng_origin_by_stage.md`(過去重大の工程分解)
- `er052_output/open233_control_checker_polysemy_trial_01/eval/{HUMAN_REVIEW_RESULT.md,RCA_jb9k_qvqc.md}`
- 各記事のR0/R2/EN本文(初出工程の確認用。該当文のみGrep)

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep: 各項目の該当文断片をR0(`ja_writer/original.md`)・R2(`ja_writer/revision2.md`)・EN(`b1b/article.md`)で検索(再分類スクリプトが実施)。
- 追記位置: `DECISION_LOG.md`末尾に1エントリ(書式は直近エントリに合わせる)。
- 更新位置: `docs/pm/ACTIVE_TASK.md`の固定ヘッダ+本文1行、`docs/pm/RESULT_PACKET.md`上書き(12行以内)。

## 実行コマンド全文
1. 再分類(Python、UTF-8): `.venv\Scripts\python.exe`相当で、100記事のng_items・pendingを読み、`er052_output/open233_stage0_01/reclass/known_relation_ng.jsonl`、`split.json`(seed=20261007、30%をheld-out)を生成。
2. 面白さ代理指標: `python docs/pm/stage0_01/narrative_count.py er052_output/open233_b3_trial_01/eval/blind_stage2/meta/dk7n/ja_writer/revision2.md`(hormuz/nn32、space_weapons/rvz5も同様)。
3. T-0検証: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-07_OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01_A.md --json-out docs/pm/delegation_log/2026-10-07_OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01_A_check.json`

## SSOT追記文
- `DECISION_LOG.md`末尾に「2026-10-07 OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01(ユーザー決定記録、委任_A)」(判断1=(A)採用、判断2=段階0承認+夜間自律ループ条件)を1エントリ追記。

## Git(明示add対象・コミットメッセージ・trailer)
- 明示add: `docs/pm/opus_l2_review_stabilization_strategy_01.md`、`DECISION_LOG.md`、`er052_output/open233_stage0_01/reclass/`、`docs/pm/stage0_01/`、`docs/pm/ACTIVE_TASK.md`、`docs/pm/RESULT_PACKET.md`、本件delegation_log(本文+check.json)。B/Cの出力はadd対象外。
- commit message: 「OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01 A: Opus戦略レビュー保存+ユーザー決定(A採用・夜間自律ループ¥1000)記録+既知関係型NG再分類(N件、dev/held-out分割)+面白さ代理指標v1、¥0」
- trailer: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`
- push origin main(index.lockがあれば最大5分待って再試行)。

## 報告(RESULT_PACKET項目)
15行以内: 再分類の件数と集計表(文種×初出工程、関係型比率、新主張比率、位置別)、held-out/dev件数、面白さ代理指標の要点、commit hash・push結果、check結果、raw URL(RECLASS.md、narrative_elements_v1.md、opus review)。
