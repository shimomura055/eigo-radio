# COST_01: 委任_02の費用(実測、cost logger記録ベース)

2026-10-26 / 上限¥40(Guardrail)/ 見積¥21〜31(BUDGET_PLAN_02) / **実費 約¥11.2**(上限・見積内、超過なし)。費用は`evidence_01.json`のtotal_cost_jpy(token×単価、`compute_cost_jpy_so_far`)。

| 区分 | 実費(JPY) | 内訳 |
|---|---|---|
| X fresh(a2+b1b) | 3.26 | scaffold(call1/call2/canonicalization/Redundancy QA)2.03 + gloss整合1.23 |
| Y fresh(a2+b1b) | 3.25 | Part2文法候補0.42 + KP(選定/canon/QA)1.91 + gloss整合0.72 + **救済gloss強制再整合0.05 + 救済QA再判定0.16** |
| Z fresh(a2+b1b) | 2.95 | Part2文法候補0.27 + KP1.89 + gloss整合0.79 |
| replay 4件 | 1.71 | X 0.42 / Y a2 0.22 / Y b1b 0.22 / Z 0.85(救済gloss強制再整合0.30+QA再判定0.23を含む) |
| 再起動確認(X/Y/Z) | 0 | API 0(usage行数不変) |
| **合計** | **11.17** | |

- 救済フロー自体の追加費用(実測): fresh Y b1b(自然発火revert 1件)= gloss強制再整合¥0.05 + QA再判定¥0.16 = ¥0.21。replay Z(M1 2件)= ¥0.30 + ¥0.23 = ¥0.53。選定段の救済(D1/慣用句の核)は追加LLM 0(通常のcanonicalization・glossに乗る)。
- 量産原価影響(70円/記事セット目標): 救済発火時でも記事セット(a2+b1b)あたり約¥0.2〜0.8(≒0.3〜1.1%)、救済なしなら¥0。外側retryが救済で減る方向の原価減は未測定(freshでretry 0回のため)。
- 当日(JST)の累計は委任文の既使用約¥552 + 本委任約¥11.2(≒¥563)。日次¥1,000内。
