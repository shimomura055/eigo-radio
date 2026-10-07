# 2026-10-07 OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01(委任_D) 段階0-D B/C/C2成果物+設計書v1のcommit、ACTIVE_TASK更新(¥0)

(保存注記: 受領した委任文の要旨再構成。見出しは標準テンプレートに合わせて補完。)

## 管理ID
OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01(委任_D)

## 性質/到達上限Status/禁止事項
- 性質: commit+一時ファイル更新のみ。SSOT編集なし。API禁止。Opus条件Aレビュー(read-only)が並行。
- 禁止事項: Agent/Subagent起動、`git add -A`、無関係差分の編集、Production変更。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0)
- E-1: 事前指定範囲だけを実行し、拡大が必要なら報告して止める。
- D-1: Production正式pathとDEV/Trial pathを区別し、Trial成果をProductionへ混入させない。
- G-1: 実行した検証の結果(実測)だけを報告し、未実行の想定でPASSと書かない。
- F-1: 詳細証跡は既存のer052_output構造に置き、RESULT_PACKETには短い要約だけ書く。
- T-0: 本委任文を docs/pm/delegation_log/ へ保存しcheck_delegation_prompt.pyで検証。

## 事前指定Read一覧
- git status --porcelain

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep: 作業内容に応じ必要箇所のみ。追記位置・更新位置: docs/pm/ACTIVE_TASK.md固定ヘッダ、docs/pm/RESULT_PACKET.md上書き。作業内容: 個別add、ACTIVE_TASK/RESULT_PACKET更新、commit/push。

## 実行コマンド全文
1. `git add`(個別パス、git add -A禁止)、`git commit`、`git push origin main`

## SSOT追記文
- なし(SSOT編集なし。正式記録は後続Closeoutで実施)。

## Git(明示add対象・コミットメッセージ・trailer)
- 明示add: 成果物ディレクトリ・本委任文・check.json。`git add -A`禁止。trailer: Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>。push origin main。

## 報告(RESULT_PACKET項目)
- commit hashとpush結果
