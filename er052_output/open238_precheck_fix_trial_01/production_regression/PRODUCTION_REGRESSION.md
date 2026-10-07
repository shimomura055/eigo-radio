# OPEN-238 Production配線 決定論Regression(¥0、API無し)

実行: precheck_baseline.py(差し替え無し、Productionモジュール直接)を26 runに再実行。比較対象は修正前ベースライン `../baseline/precheck_baseline.json`。
成果物: precheck_production.json(本実行)、o2_bitwise_check.json(HEAD版 vs 作業ツリー版の同一プロセス比較)、prod_e2e02_precheck_crosscheck.json。

## 26 run
- 修正前fires=2(ai_control P2 rep2: EVID-006[33.3], CONTROL-004[33.3]) -> Production配線後fires=0。
- 変化したrunは ai_control/nb/p2/rep2 の1 runのみ。他25 runは extracted_values/fires/all_precheck_kinds/QTY文を含め全項目不変。
- skipped 1(rep2_stop1、成果物なし)は修正前と同一。

## 他経路 bit単位不変(O2、HEAD版precheckと作業ツリー版を同一プロセスで比較、26 run)
- 文別loose抽出(runner L2838/coverage_checker L475型) 不変: True
- 台帳loose抽出(L3090型) 不変: True
- L322 changed_number_is_natural_rounding_only(全fact x 全文) 不変: True
- number_mismatch以外の全finding(JSON比較) 不変: True
- number_mismatch自体の差分は ai_control rep2 の上記2件消滅のみ。

## 承認構成9 run(prod_e2e_02)判定変化なし
- 9 runのChecker結果jsonに残るprecheck情報は rewrite_new_precheck_findings_count のみ(全て0、5 cycle分)。precheck findings本体は保存されていない。
- 再計算: 9 run(fixtureのEN/台帳)で修正前後ともprecheck fires=0(ベースライン比較で不変)。count記録のある4 run(bgroup_B3/meta_run03_standard/neg2_meta_refresh_a2/neg3_hormuz_prodrunner_b1b)の各cycleのbefore/after_rewrite本文をProduction版で再判定 -> number_mismatch 0件、記録値0と一致。判定変化なし。
