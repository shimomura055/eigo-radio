管理ID: FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01
Status: STOP(Gate 4静的確認でNG、記事生成・API呼び出しなし、実費¥0)。

原因: Production `er003_v1_n3_01_articles_generate.py`が本日commit
ce39de7b(OPEN-141差分QA+target-sentence-matching既定ON、ユーザー正式
判断2026-09-13)でTrial-03時点(d79a9f9a)から意味的に変更されており、
再利用予定の`run_one_pattern_connected`(Trial-03コピー、無改変で再利用の
約束)はこの新規安全ゲート(Local Rewrite受理直後のFact Checker A'再実行+
Ledger再確認+Point Overlap再計算)を含んでいない。再利用予定のfocus単独
baseline記事は実際にこの新ゲートを通過済み(diff_qa fieldで確認)であり、
新規生成の「focus+接続」記事だけがこれを欠くと比較が不公平・安全装置の
無断回避リスクとなるためSTOP。

他2ファイル(`er011_point_role_value_planning_01.py`/
`er006_pool_pilot_01_writer.py`)はTrial-03以降無変更。

詳細: `FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01_REPORT.md`
(選択肢4案、残る問題を記載)。

次アクション: Fable/ユーザー判断待ち(USER_DECISION_REQUIRED)。
新規driver・API呼び出し・Production/SSOT変更は行っていない。
