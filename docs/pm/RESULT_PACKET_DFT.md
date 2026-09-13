管理ID: FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01
(Fable修正指示1回目、STOP解除)
Status: 完了(Trial、Production採用ではない)。

前回STOP: Gate 4でOPEN-141差分QA(commit ce39de7b)を欠くtrial_03コピーを
検出しSTOP(REPORT 1〜6節に保全)。

今回: 接続関数を現行Production run_one_pattern(OPEN-141差分QA込み)と同等の
新コピー`er011_point_role_planning_focus_connection_trial_04.py`として作成。
`inspect.getsource`ベースの機械的ソース再構成テストで、hint注入4点(関数名/
引数追加/呼出2箇所置換/bareヘルパー14件のprod_gen.修飾)以外の差分ゼロを
実行毎に自動証明(test_01.py、6 test PASS)。LLMモック統合テストでhint=""時
Production版とbyte一致も確認。

回帰: pattern一致6 PASS。default全件2490件中2487 PASS(残り3件は既存の
自己参照カウント検証の既知失敗、無関係)。

Runtime: 新規driverでfocus+接続(案2 hintのみ)A2/B1を新規生成(実費¥46.47/
上限¥300)。両記事status=OK、fact_verdict=PASS、ledger_status=
LEDGER_COMPLIANT(A2側MINOR逸脱1件、non-blocking)。focus単独2記事は既存
Trial成果物を再利用。4記事比較artifact作成済み。

観察: hintはPoint Role Planningのrole出力に反映されるが、(1)A2/B1の役割が
「睡眠段階」「学習された期待」へ収束し角度多様性が低下、(2)因果的機序の
割当がMINOR逸脱を誘発、の2リスクを確認(いずれも既存安全装置の範囲内)。

REPORT: FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01_REPORT.md
比較artifact: er011_output/discovery_focus_role_planning_connection_trial_01/
comparison.md, index.html

次アクション: ユーザー判断待ち(Gate 1材料の評価、Production採用は別判断)。
