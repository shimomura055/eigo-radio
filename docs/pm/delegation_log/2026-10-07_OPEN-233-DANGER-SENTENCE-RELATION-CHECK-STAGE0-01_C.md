# 2026-10-07 OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01(委任_C) 段階0-C 関係抽出の反復安定性(stability/、実API少額)

(保存注記: 受領した委任文の要旨再構成。見出しは標準テンプレートに合わせて補完。)

## 管理ID
OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01(委任_C)

## 性質/到達上限Status/禁止事項
- 性質: Trial限定。予算内(実費¥7.81)。書込先 stability/ のみ。単層4並列以下。
- 禁止事項: Agent/Subagent起動、`git add -A`、無関係差分の編集、Production変更。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0)
- E-1: 事前指定範囲だけを実行し、拡大が必要なら報告して止める。
- D-1: Production正式pathとDEV/Trial pathを区別し、Trial成果をProductionへ混入させない。
- G-1: 実行した検証の結果(実測)だけを報告し、未実行の想定でPASSと書かない。
- F-1: 詳細証跡は既存のer052_output構造に置き、RESULT_PACKETには短い要約だけ書く。
- T-0: 本委任文を docs/pm/delegation_log/ へ保存しcheck_delegation_prompt.pyで検証。

## 事前指定Read一覧
- reclass/、sentences.json、schema_v0.json

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep: 作業内容に応じ必要箇所のみ。追記位置・更新位置: docs/pm/ACTIVE_TASK.md固定ヘッダ、docs/pm/RESULT_PACKET.md上書き。作業内容: 同一文を複数回関係抽出して反復一致率を測定。

## 実行コマンド全文
1. `.venv\Scripts\python.exe er052_output/open233_stage0_01/stability/run_stability.py`、`.venv\Scripts\python.exe er052_output/open233_stage0_01/stability/analyze.py`

## SSOT追記文
- なし(SSOT編集なし。正式記録は後続Closeoutで実施)。

## Git(明示add対象・コミットメッセージ・trailer)
- 明示add: 成果物ディレクトリ・本委任文・check.json。`git add -A`禁止。trailer: Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>。push origin main。

## 報告(RESULT_PACKET項目)
- STABILITY.md
