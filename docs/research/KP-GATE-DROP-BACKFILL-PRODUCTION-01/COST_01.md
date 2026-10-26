# COST_01: 委任_03の費用(実測、usage log記録ベース)

2026-10-26 / 上限¥45(Guardrail) / 見積¥22〜30(BUDGET_PLAN_01+委任文) / **実費 約¥26.2**(見積・上限内、超過なし)。費用=token x 単価(`compute_cost_jpy_so_far`、`tools/cost_by_stage_01.py`・`tools/collect_evidence_02.py`が算出、出典=各run dirのusage log)。

| 区分 | 実費(JPY) | 内訳 |
|---|---|---|
| X AI島 fresh(a2+b1b) | 2.55 | scaffold(call1/call2/canon/RQA)1.65 + gloss整合0.90(補完なし) |
| X コーヒー R-9(a2+b1b) | 2.82 | scaffold 1.85 + gloss 0.96(補完なし) |
| X 中東 R-9(a2+b1b) | 3.89 | scaffold 2.35 + gloss 1.21 + 救済gloss再整合0.07 + 救済QA再判定0.25(補完2発動を含む) |
| Y 再配達 fresh(a2+b1b) | 4.26 | Part2文法候補0.53 + KP(選定/canon/QA/補完)2.47 + gloss 0.99 + 救済0.27(補完1発動を含む) |
| Z メロス fresh(a2+b1b) | 3.88 | Part2文法候補0.35 + KP 2.52 + gloss 1.00(補完1発動を含む) |
| replay 7件 | 8.85 | R1 1.42 / R2 1.64 / R3 1.12 / R4 1.47 / R5a 0.92 / R5b 1.38 / R6 0.90 |
| 再起動確認(Y/Z/X中東) | 0 | API 0(usage行数不変) |
| 猿の手Z起動(provenance不一致STOP)・R-9 #1初回(入力欠落) | 0 | いずれもAPI前に停止 |
| **合計** | **26.25** | |

- 当日(JST)累計: 委任文の既使用約¥595 + 本委任約¥26.2 ≒ **¥621**(日次¥1,000内)。
- **補完1発動あたりの追加費用(実測、補完に属するcallをresponse_idで特定。`tools/backfill_incremental_cost_01.py`)**: 2-V補完call ¥0.13〜0.17 + 補完分canonicalization ¥0.21〜0.27 + 補完分gloss整合 ¥0.21〜0.35 = **¥0.585(Y a2) / ¥0.620(Z a2) / ¥0.624(X中東a2) / ¥0.710(X中東b1b)、平均¥0.635**(見積¥0.7〜1.0より低い)。replay(補完2-V callのみ特定): ¥0.13〜0.15。Redundancy QAは1回のまま(増加なし)。
- **量産原価(70円/記事セット)への影響**: 本標本(10 level-run、除外が起きやすい記事を意図的に含む)では発動4/10=40%。1 level平均 ¥0.635 x 0.4 ≒ ¥0.25、記事セット(Std+Adv)で約¥0.5(目標の約0.7%)。両levelで発動した最悪でも約¥1.3(約1.9%)。除外0のlevelは増分¥0。実運用の発動率は記事により異なる(標本は偏りあり)。
- **外側retry全件再生成の削減(見込みと未測定)**: 旧条件(Gate除外+n_auto<3)の全件再生成1周は約¥1.0〜1.9(CURRENT_FLOW_01/BUDGET_PLAN_01の見積)。今回のfreshでは旧条件に該当するlevel(n_auto<3)が観測されず(最小n_auto=5)、削減額の実測は**未測定**。該当ケースでは補完(約¥0.6)が全件再生成(約¥1.0〜1.9)より安い見込み(net中立〜微減)。
- モデル: 全call `gpt-6-luna`(現行routing契約`SUPPORT_MODEL`)。本番ライン無変更。
