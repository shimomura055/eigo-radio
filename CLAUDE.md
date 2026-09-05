# Claude Codeへの指示

## 説明方法
私はプロジェクト責任者であり、詳細な実装担当者ではありません。

コード変更時は以下の順番で説明してください。

1. 何が問題だったか
2. 何を変更したか
3. 何が改善されるか
4. リスクや注意点

技術用語を使う場合は、最初に簡単な日本語説明を付けてください。

詳細なコード内部の説明は、必要な場合のみ補足してください。

## 開発方針
速度よりも安定性を優先してください。
大きな変更を行う前に、変更内容と影響範囲を説明してください。

## Git運用ルール
コードの修正やファイルの追加・削除など、意味のある変更を行い、動作確認(必要に応じてテスト)が完了したら、以下を自動的に実施する。

1. 変更内容が分かるCommit Messageを付けてCommitする。
2. GitHubのorigin/mainへPushする。

Commit Messageは、変更内容が分かる簡潔なものにする。

ただし、以下の場合は自動実行せず、必ずユーザーに確認する。
- 履歴の書き換え(amend、rebase、force push)
- 大規模なリファクタリングや削除を伴う変更
- エラーや競合(conflict)が発生した場合
- 動作確認に失敗した場合

それ以外の通常の開発では、Commit・Pushまでを一連の作業として自動的に完了する。

意味のある変更をCommit・Pushしたら、その報告の最後に、変更したファイルの
raw.githubusercontent.com URLを、そのままコピペできる形で必ず添える。

例:
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/tts_test.py

## Fableサンドイッチ運用(PM層)

- PM運用の入口は`docs/pm/PM_BRIEF.md`。正式仕様・決定履歴・未決事項は
  引き続きroot直下の`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/
  `HISTORY_INDEX.md`/`ER-*_REPORT.md`が正式SSOTであり、`docs/pm/`配下は
  その複製ではない。
- `docs/pm/ACTIVE_TASK.md`と`docs/pm/RESULT_PACKET.md`は一時ファイルであり、
  正式記録ではない(タスクごとに上書きされる)。
- サンドイッチ方式の起動は`claude --agent sandwich-pm`。
- 上記「Git運用ルール」は維持する。ただしサンドイッチ導入・更新作業では、
  今回変更した対象ファイルだけを明示的に`git add`し、`git add -A`は使用しない。
- ループ上限: Sonnet委任は合計最大2回(初回+修正1回)、Fableからの差し戻しは
  最大1回、Opusは診断目的で最大1回まで。上限到達時は`USER_DECISION_REQUIRED`
  としてSTOPする。
- Production採用(`APPROVED_FOR_PRODUCTION`)は人間ユーザーだけが承認できる。
- PM運用Gate(Gate 1〜7)・PM Closeout Mandatory Check・1記事ずつ完結原則・
  安全≠成功原則の正式SSOTは`docs/pm/PM_GOVERNANCE.md`(2026-09-05、
  PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01でユーザー承認済み)。ここへは
  全文を複製しない。