# PARSER_USAGE_01: ledger_restore_01 / parse_ledger_file / _HDR の使用箇所(FIX01-C 項目1、API費用 ¥0、機械Grep)

方法: リポジトリ全体を Grep(パターン `ledger_restore_01|parse_ledger_file|\b_HDR\b`、*.py 全件。さらに *.sh/ps1/bat/cmd/js/ts/yml/yaml/toml/txt でも `ledger_restore_01|parse_ledger_file` を検索)。非.pyでのヒットは0件。

## 使用しているscript(全て er052_output/ 配下のDEV/Trial)
| パス | 使い方 |
|---|---|
| er052_output/writer_dev_risk_flagger_01/detectors/ledger_restore_01.py | 定義元(`_HDR` L12、`parse_ledger_file` L35、内部利用 L62) |
| er052_output/writer_dev_risk_flagger_01/detectors/run_flagger_01.py | import / parse_ledger_file 呼出 (L108) |
| er052_output/writer_dev_risk_flagger_01/detectors/p3_run_01.py | import / parse_ledger_file 呼出 (L27) |
| er052_output/writer_dev_risk_flagger_01/detectors/d0_article_sweep_01.py | import / parse_ledger_file 呼出 (L29) |
| er052_output/writer_dev_risk_flagger_01/detectors/make_blind_01.py | import(コメント言及あり) |
| er052_output/writer_dev_risk_flagger_01/detectors/test_flagger_01.py | import |
| er052_output/writer_r0_model_impact_trial_01/r0_trial_driver_01.py | import / parse_ledger_file 呼出 (L138)(R0 Trial 初回。欠落あり版) |
| er052_output/writer_r0_model_impact_trial_01/aggregate_01.py | import(`ledger_facts` 内、L35) |
| er052_output/writer_r0_model_impact_trial_01/r0_fix01_driver.py | process内で `LR._HDR` を差替えて parse_ledger_file 呼出(FIX01-A) |
| er052_output/writer_dev_risk_flagger_01/fix01_ledger_audit/audit_ledger_coverage_01.py | read-only 監査(FIX01-B)。現行パーサ出力と寛容正規表現を比較 |

## Production code からの参照
- リポジトリ root 直下の `er0XX_*.py`(本番ライン含む)に `ledger_restore_01` / `parse_ledger_file` / `_HDR` を参照するものは、上記Grepでは **0件**。ヒットは全て `er052_output/writer_dev_risk_flagger_01/` と `er052_output/writer_r0_model_impact_trial_01/` 配下。
- 注意(別事実): `_HDR` という名前はこの2ディレクトリ内でのみヒット。本番ラインが独自の台帳パーサを持つかどうかは本調査(上記3パターンのGrep)の対象外であり、未調査。
- 別系統の同型パーサ: `er052_output/writer_dev_risk_flagger_01/casebank/build_casebank_01.py` L127/L198 は `\[VERIFIED\]\s+(...):` のみ読む独自正規表現(ledger_restore_01 は使わない)。

## 参考
欠落内容は LEDGER_AUDIT_01.md を参照。修正・変更は行っていない。
