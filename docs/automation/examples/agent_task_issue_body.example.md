# agent_task_issue_body.example.md

管理ID: AUTO-001-04D-R2

このファイルは、`.github/ISSUE_TEMPLATE/agent_task.md`(Markdown Issueテンプレート)を使ってIssueを起票する際の記入例である。ChatGPT等が生成したMarkdown本文をGitHubへ貼り付ける際の形式イメージとして参照する。

実在するSecrets・APIキー・個人情報・未公開の生成物内容は含まない(架空の管理ID・架空のタスク内容による例示)。

---

## 記入例(この区切り線から下がIssue本文としてそのまま貼り付ける想定の内容)

<!-- AGENT_TASK_SPEC_START -->

## 管理ID

EXAMPLE-001

## 現在の問題

`scripts/example_report_builder.py`を手動実行すると、出力先ディレクトリが存在しない場合に`FileNotFoundError`で異常終了する。出力先の作成は呼び出し側の責務になっており、スクリプト自身は作成しない設計になっている。

## 原因に関する仮説

`open(output_path, "w")`を呼ぶ前に`os.makedirs(os.path.dirname(output_path), exist_ok=True)`を呼んでいないことが原因と考えられる。

## 目的

出力先ディレクトリが存在しない場合でも、`scripts/example_report_builder.py`が自動的にディレクトリを作成してから出力できるようにする。

## 期待動作・決定事項

* `scripts/example_report_builder.py`実行時、出力先ディレクトリが存在しなければ自動的に作成する。
* 既存の出力ファイルを上書きする挙動(既存仕様)は変更しない。
* ディレクトリ作成に失敗した場合(権限不足等)は、既存と同様に例外を送出する。

## 非対象範囲

* `scripts/example_report_builder.py`以外のスクリプトの出力処理は変更しない。
* 出力ファイルのフォーマット自体は変更しない。
* 新しいCLI引数は追加しない。

## 受入条件

- [ ] AC-01: 出力先ディレクトリが存在しない状態で`scripts/example_report_builder.py`を実行すると、`FileNotFoundError`にならずディレクトリが作成された上でファイルが出力されること
- [ ] AC-02: 出力先ディレクトリが既に存在する場合、従来通りファイルが上書き出力されること
- [ ] AC-03: 既存の単体テスト(`example_test_report_builder.py`)が全て成功すること

## テスト観点

既存の`example_test_report_builder.py`に、出力先ディレクトリが存在しないケースのテストケースを追加し、AC-01を機械的に検証する。既存のテストケースは変更しない。

## リスク

`os.makedirs`の`exist_ok=True`により、意図せず親ディレクトリまで作成される可能性がある。呼び出し元が想定していないパスへ書き込まないよう、出力先パスの決定ロジック自体は変更しないことで影響範囲を限定する。

## 人間確認事項

なし

## 変更区分

- サービス仕様変更：なし
- リポジトリ運用仕様変更：なし
- 実装方法だけの変更：はい

## 参考資料

なし

<!-- AGENT_TASK_SPEC_END -->
