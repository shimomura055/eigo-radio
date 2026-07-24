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

## Historical test evidence vs. current project-wide regression(ER-003-P2L)

過去のテスト件数調査(例: `er003_output/p2j/`のER-003-P2J成果物)と、現在の回帰テストは、明確に別の責務を持つ。

```text
Historical test evidence:
Validates the internal consistency and immutability of past test-run records.
It must not compare historical counts with the current collected count.

Current project-wide regression:
Run `python run_project_regression.py`.
This is the only evidence for the current HEAD's project-wide regression status.
```

- **Historical test evidence**(例: `er003_test_p2j_investigate.py`の`HistoricalRecordIntegrityTests`)は、保存済みJSON成果物が当時の記録として内部矛盾なく保存されているか(必須フィールドの存在、値の型、commit hash形式、command/scopeの非空性、enum妥当性)だけを検証する。保存された過去の数値(例: P2H=1032件、P2I=660件、P2J完了時点のcurrent_head=1117件)は、以後どれだけテストファイルが増えても書き換えない。**現在のlive集計件数と比較すること自体を行わない**(`==`・`>=`・`<=`のいずれも使わない)。件数の増減だけでtest消失やコード品質を判定しようとしない。
- **Current project-wide regression**(`python run_project_regression.py`)だけが、現在HEADの回帰品質の証跡になる。過去の記録との突き合わせは行わない。
