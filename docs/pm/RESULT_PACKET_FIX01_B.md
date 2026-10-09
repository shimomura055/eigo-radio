# RESULT_PACKET_FIX01_B (WRITER-R0-MODEL-IMPACT-TRIAL-01-FIX01 項目2・3、read-only、API費用 ¥0、2026-10-10)
詳細: er052_output/writer_dev_risk_flagger_01/fix01_ledger_audit/{LEDGER_AUDIT_01.md, ledger_audit_01.json, audit_ledger_coverage_01.py}
1. Disney+以外にも欠落あり: semiconductor_earnings(Broadcom)の F1(受領5/見出し6)。streaming_price は F01・F07(受領5/見出し7)。調査対象の台帳28本中この2テーマのみ(他26本は全件受領)。
2. 影響単位: 文単位ケース 9/78(dev4・holdout5、全て非重大ラベル)、記事 7/38(streaming4+semiconductor3)。重大ケース・Rollback・K12・合成14件は完全受領。
3. 過去Flag突合: Disney+の「理由が明示されていない」「Reutersコメント要請への回答状況」「説明がない」系(確認パック new EN/JA 各3 Flag、旧腕 s18 2件、R0 Trial の Luna4/Sol1)は、F07 に根拠があると読める(候補。最終判定なし)。semiconductor F1 に関連するFlagは無し。ユーザーの会話上の過去判定は記録上見つからず、Fableからの提供が必要。
4. 過去KPI案: 「一部再計算必要」。Recall(KPI1)・KPI4は影響なし。KPI2 FPR_clear は分母18中4件が影響、分子3中1件(rf_5cryu9)。KPI3は数値不変(強制列挙)だが中身が変わりうる。KPI5確認パックは52 Flag中10 Flagが影響(回答は未記入)。再実行見積り 約¥48(過去cost_jpyからの推定)。確定はFable/ユーザー。
5. 根本原因: ledger_restore_01._HDR の `[A-Z_]+\]` が、台帳生成コード(er003_v1_en_direct_vfl_01_generate.py L292)が決定論で付ける `[AMBIGUOUS - 断定禁止…]` に一致しない。AMBIGUOUS Factは毎回この形式なので再発構造。失敗は無音(件数照合なし)。リポジトリ全台帳540ファイルで見出し7,851行中123行(37ファイル)をパーサが読み飛ばす。casebank構築script(L127)にも同型の VERIFIED 限定パーサあり。
6. 修正案(未実装): C=実行時assert/件数記録(最重要)、A=正規表現拡張、B=全タグ受理+タグ別フィールド(Flagger入力仕様変更=ユーザー決定候補)、D=単一仕様モジュール化、E=生成側タグ簡素化。
7. 限界: 完全台帳でのFlagger再実行は未実施(「根拠あり」は台帳テキストとの内容照合)。E2E評価ラベルは台帳原文照合でパーサ非経由と読めるが、評価ワーカー入力は再点検していない。
8. 禁止事項遵守: detectors配下・FIX01-Aのディレクトリ・SSOT・git・APIに触れていない。
