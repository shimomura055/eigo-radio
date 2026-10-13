# TRIAL_REPORT_02: P0X(P0へ1段落追加)の有料run結果
管理ID: FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 委任_02 / 2026-10-13 / Trial専用・採用判断なし
有料run: Stage 1のみ 5 job、JPY4.8948(承認上限30・job上限2.5。最大job 1.162)、モデルgpt-6-luna(Production同一、例外)。Stage 2は未実行(regression_02.md)。
## 結果
- P1(裸no way 0/5、Bは全てB-valid): **PASS**(0/5、5/5が`no way to know`で全gate PASS)。
- P2(merged PASS≥4/5、有限助動詞INVALID 0): PASS(5/5、INVALID 0)。
- P3(良い選定の維持): **FAIL**。behind the scenes/unintentionally/contract workers 5/5だが`concierge` 0/5(対照2/2、目標≥4/5)。
- 副作用: 5枠目が断片拡張(`instead of AI`/`other end of the call`/`talking to AI`/`take care of`)へ置換。over_extended_items 7件/25(対照0/10)。
- 費用・時間: +20%/+45%(n=2対照、参考)。
## Status: REJECTED(M2P0維持)
ユーザー受入条件(3)(4)とSide effect規定により不採用。裸`no way`の解消という目的自体は達成(0/5、再現性5/5)したが、同じ段落が`concierge`の脱落と断片への機械的拡張を同時に起こした。回帰(Coffee/Hormuz/Meta Std)は測定していない。
## 付記・Production採用時の留意点
- 成立形は`no way to know`(案Bの実現形)。ユーザー例`have no way to know`は既存Validator(有限助動詞`have`)でINVALIDのため、本Trialは追加段落で`have`を含めない指示を入れ、Validatorは緩和していない(INVALID 0/5)。`have`系Validator仕様候補はOPEN-336へ追記。
- 追加段落は一般則であるため`no way`専用に絞れず波及する(hardcodeを避けた設計の裏面)。再発性が高ければ、同一問題への2回目以降の修正は条件B(Opus独立レビュー)の対象。
## 証跡
analysis_stage1_02.json / before_after_meta_adv_02.md / regression_02.md / cost_run_02.json / reuse_check_02.json(対照rows sha一致、prompt sha一致) / state_guard_02.json(Production state 8ファイル前後不変) / runs/meta_adv_M2P0X_run{1..5}/ / run_summary_02_stage1.json。
テスト: er064_kp_noway_01_test.pyは20件中2件が失敗(`test_paid_run_refused_*`は委任_01時点の「runs/・cost_run_02.json不在」を前提とする検査で、有料run実施後は想定どおり失敗。コード欠陥ではない。他18件PASS)。
