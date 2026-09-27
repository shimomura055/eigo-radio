# 参考: JA_FACT_CHECK_STOP 実発火の記録(開発中の一時実行、本run_02の正式成果物ではない)

本ディレクトリは、Stage 1実装過程で最初にMeta run_02を実行した際に実際に
`JAFactCheckStopError`(JA_FACT_CHECK_STOP)が発火した実測ログである。
その後、(1) Fact Check呼び出しのcost stageタグ付け漏れ、(2) JA段retry
checkへの`prior_issues`未接続、の2点を修正したため、最終的なrun_02
(`../deviation_checks/`等)はこの2修正を反映したコードで再実行した
クリーンな結果(Original/R2ともLEDGER_COMPLIANT、must-fix不要)になっており、
この実行時のファイル(attempt1.json/attempt2.json等)は上書きされ現存しない。

ただし、この2修正は「overall_statusが既にLEDGER_DEVIATIONのまま」という
本記録のケースの判定結果には影響しない(修正(1)はcost集計の粒度のみ、
修正(2)はoverall_status==LEDGER_COMPLIANTなのにprior issueが未解消、という
別ケースのみに関わる安全側追加条件のため)。そのため、本記録は
JA_FACT_CHECK_STOPが実API上で正しく発火することの実証として現在も有効。

- `raw_console_log.txt`: 実行時のコンソール出力全文(traceback含む)
- `attempt1.txt`: 1回目Fact Check(JA Original)の逐語(MAJOR、related_fact_id=MUSE-HC-006、
  「Museの人間コンシェルジュ機能という特定のテスト」から「AIサービス全般の将来動向」への一般化)
- `attempt2.txt`: must-fix Rewrite後の2回目Fact Check(新たに別のMAJORが発生、
  related_fact_id=MUSE-HC-008、成功率の比較を「導入理由」であるかのような因果関係に拡張)
  →2回目もMAJORのためJAFactCheckStopErrorでSTOP(正しい挙動)
