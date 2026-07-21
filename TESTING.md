# Project-wide regression test

このリポジトリのER-002/ER-003回帰テストには、正式な実行入口が1つだけある。「全テスト成功」と報告してよいのは、この入口を実行した場合だけである。

## Command

```text
python run_project_regression.py
```

- リポジトリのどのディレクトリから実行しても、`run_project_regression.py`自身の場所を基準にrepository rootを解決するため、対象範囲は変わらない。
- `--pattern`で探索patternを上書きできるが、通常は使用しない(デフォルトのままにする)。
- `--json-summary <path>`で、collected/passed/failed/skippedをJSONへ保存できる(preflightや完了報告での参照用、省略可)。
- 終了コード: 全件成功時は`0`。収集0件、または1件でも失敗/エラーがあれば`0`以外。

## Scope

- Discovery: `unittest`の自動探索(glob pattern)。**手動でtest module名を列挙する方式は正式手順ではない**(ER-003-P2Jで、この方式が対象範囲の食い違い・テスト件数不一致の原因になったことを確認済み)。
- Pattern: `er0*_test_*.py`
- 対象: `er002_test_*.py`(ER-002)+ `er003_test_*.py`(ER-003)
- 対象外: `test_api.py`, `generate_test.py`, `tts_test.py`, `tts_style_test.py`など、`er002_test_*`/`er003_test_*`の命名規則に従わないスクリプト(単発の手動API疎通確認・レガシー生成スクリプトであり、回帰テストスイートの一部ではない)
- ER-001: 現時点でunittest形式の回帰テストが存在しない(ER-003-P2Kで調査済み)。将来`er001_test_*.py`が追加された場合、本patternへ含めるかは別途判断する。

新しい`er002_test_*.py`/`er003_test_*.py`ファイルを追加しても、このコマンド・patternのコード変更は不要で自動的に対象へ含まれる。

## Reporting rules

完了報告では、以下を分けて記載する。

```text
Targeted tests:
- command
- scope
- passed / failed / skipped

Project-wide regression:
- canonical command (python run_project_regression.py)
- scope (ER-002 + ER-003, er0*_test_*.py)
- collected / passed / failed / skipped
```

禁止:

- subsetだけの結果を「プロジェクト全体」と書くこと
- commandを示さずに「全テスト成功」とだけ書くこと
- collected件数とpassed件数を混同すること
- 手動列挙commandを正式なproject-wide regressionの証跡として再利用すること

個別タスク用のtargeted test(特定のテストファイル・特定のTestCaseのみを対象とする実行)は、開発中の早期失敗検出として引き続き使ってよい。ただし、それは「project-wide regression」ではなく、targeted testsとして明示すること。
