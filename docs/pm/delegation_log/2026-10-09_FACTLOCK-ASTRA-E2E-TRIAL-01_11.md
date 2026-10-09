# 委任_11 FACTLOCK-ASTRA-E2E-TRIAL-01 (2026-10-09) G1カナリア
管理ID: FACTLOCK-ASTRA-E2E-TRIAL-01 委任_11。G1カナリア(METAの新腕→Checker 1 run、旧腕→Advancedまで、実API)+検証。API支出上限 ¥70(見積¥43〜53+余裕)。Trial累計上限¥1,000、既支出¥178.99(Stage R ¥178.25+B3再生成¥0.74)。並行委任なし。git index.lock衝突時は10秒待って最大5回再試行。

## Fable判断(記録)
- inbound_tourism: 再委任1回後もA/B双方FAIL。RUN_ANNOTATION §6によりSTOP=「注記不能」として記録、本Trialは9テーマ(旧4+新5)で進める。ID_RE誤検出はスクリプト欠陥として修正(修正前後保存、テスト追加)、再検査は記録のみ。実FAILが残れば除外のまま。層別・判定線への影響(新テーマ n=5)は事前登録の注記として追記。
- hormuz・streaming_price は両腕ともB3 v2共有(旧4の凍結B3はhormuzのみv2に置換)。
- (c)AMBIGUOUS許容はFable判断で継続(ユーザーが覆せばsemiconductor/streamingを除外)。

## 作業
1. 前処理(¥0): ID_RE修正+テスト、inbound再検査(記録のみ)、新6本transcript監査、ws_check/astra単価/x1.5確認。
2. G1実行: `run --root er052_output/factlock_astra_e2e_trial_01/runs --themes meta --arms new --until new_check_adv --worker-id 1`、続けて `--arms old --until old_adv`(上限¥70のため `--cap-jpy 70 --alert-jpy 60` を追加)。空き物理メモリ4GB未満なら待機。
3. G1検証(設計書§5の全項目)。4. G1判定(欠陥あればG2へ進まずSTOP)。G2起動禁止・TTS禁止・Prompt文言変更禁止・上限¥70超過禁止。
5. 記録: 本ファイル、check結果、_11_result.md、RESULT_PACKET.md、DECISION_LOG.md末尾1節、ACTIVE_TASK.md固定ヘッダ、REPORT_LEDGER.md 1行、commit/push。
