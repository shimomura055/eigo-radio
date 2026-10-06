# TRIAL-03 testset_03(事前登録・凍結、実行後の変更禁止)

D61型は分析用の内部ラベルのみ。新しい重大カテゴリではなく、既存の重大Fact誤り基準で評価する。

## 内訳
| 区分 | 項目数 | repeat | call見込み |
|---|---|---|---|
| 既存(testset_02複製、内容不変) | 63 | G-01〜03/F-09/F-10/F-19/G-04〜06=3、他1 | 81 |
| held-out重大 H-G1〜H-G4 | 4 | 3 | 12 |
| held-out正常 H-F1〜H-F6 | 6 | 3 | 18 |
| 合計 | 73 | - | 111(=Σrepeat) |

## held-out項目(D61を見ずに手書き、LLM不使用)
| id | fact | 文 | phase | 期待 |
|---|---|---|---|---|
| H-G1 | HF-009 | Oil prices dropped after the withdrawal. | FINAL | REVERSED |
| H-G2 | HF-009 | Brent fell after the plan was dropped. | FINAL | REVERSED |
| H-G3 | HF-009 | Prices ended lower. | FINAL | REVERSED |
| H-G4 | HC-012 | Meta kept the human concierge feature running. | FINAL | REVERSED |
| H-F1 | HF-009 | Prices initially fell but recovered. | FINAL(INTERIM↓+FINAL↑) | SAME |
| H-F2 | HF-009 | Oil prices briefly dipped. | INTERIM | SAME |
| H-F3 | HF-009 | Oil prices stayed near earlier highs. | FINAL | SAME |
| H-F4 | HF-009 | The drop was short-lived. | INTERIM | SAME |
| H-F5 | HF-009 | Prices did not fall across the board. | UNSPECIFIED | SAME |
| H-F6 | HF-009 | Brent did not end lower than before. | FINAL | SAME |

## 合格基準(事前固定、逐語)と母数
| # | 基準 | 母数(id) |
|---|---|---|
| 1 | HC-012 3/3 | G-01(repeat3) |
| 2 | A5-0 3/3 | G-02(repeat3) |
| 3 | D61 2/3以上 | G-03(repeat3) |
| 4 | held-out重大例 平均2/3以上かつ全例1/3以上 | H-G1〜H-G4(各3、計12) |
| 5 | 正常43件+held-out正常例の不要重大判定0 | 既存faithful_state21+same_fact_not_mentioned17+non_directional5=43件(F-*/N*/ND-*等、gold_reversal/ambiguous/synthetic_reversal除く)+H-F1〜H-F6 |
| 6 | 不要Rewrite見込み0 | 基準5の母数(49項目、repeat反映) |
| 7 | 新たな重大見逃し0 | synthetic_reversal14+H-G系を含む全重大項目で、基準1〜4の対象外の見逃し |
| 8 | 前回解消誤爆3件の再発なし | F-09, F-10, F-19(各3) |

注: G-04〜G-06(ambiguous)は判定不能が適切で、REVERSED誤検出がないことのみ確認(基準5・6の母数外、重大見逃し対象でもない)。
