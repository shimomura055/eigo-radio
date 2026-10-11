# ANALYSIS_01 (MOCK乾式。実評価ではない)

本書は機械集計。『候補』は確定判定ではなく、Claude/人が根拠の妥当性を確認する(AI評価だけで最終FIXしない)。

- 解析対象: 成功96件 / 失敗・欠損0件 / actual model_id: ['gpt-6-luna']

## 1. 極端結果の検出

- 方式A: 検出なし
- 方式B: 検出なし
- 方式C: 検出なし
- 方式D: 検出なし

## 2. 再現性(同一方式N回の差=LLMゆらぎ)

| 方式 | 作品ペア数 | rep間の差の平均(0-1) | 最大 | 軸一致率 | Spearman(rep1,rep2) |
|---|---|---|---|---|---|
| A | 12 | 0.026 | 0.125 | 0.896 | 0.94 |
| B | 12 | 0.000 | 0.000 | 1.000 | 1.00 |
| C | 12 | 0.031 | 0.125 | 0.875 | 0.98 |
| D | 12 | 0.021 | 0.125 | 0.875 | 0.99 |

切り分け: 同一方式のrep間差=LLMゆらぎ、方式間の順位差=Prompt/基準差。rep間の順位相関が高く方式間相関が低ければPrompt設計差、rep間相関自体が低ければLLM能力/ゆらぎ。

## 3. 方式間で順位が大きく割れる作品

- L02: 順位差11.0 {'A': 1.0, 'B': 12.0, 'C': 3.0, 'D': 1.0}
- L11: 順位差10.0 {'A': 4.5, 'B': 1.5, 'C': 11.5, 'D': 8.0}
- L12: 順位差8.5 {'A': 9.0, 'B': 3.0, 'C': 11.5, 'D': 11.0}
- L05: 順位差7.5 {'A': 3.0, 'B': 10.5, 'C': 4.5, 'D': 4.0}
- L08: 順位差7.0 {'A': 6.5, 'B': 5.5, 'C': 1.0, 'D': 8.0}
- L07: 順位差6.5 {'A': 4.5, 'B': 8.0, 'C': 6.5, 'D': 11.0}
- L13: 順位差6.5 {'A': 12.0, 'B': 5.5, 'C': 10.0, 'D': 6.0}
- L03: 順位差5.0 {'A': 6.5, 'B': 1.5, 'C': 6.5, 'D': 2.0}
- L04: 順位差5.0 {'A': 8.0, 'B': 5.5, 'C': 4.5, 'D': 3.0}

## 4. L05(交尾)の方式別評価

- 方式A: 正規化0.75 順位3.0 軸別={'A': [2.0, 2.0], 'B': [4.0, 4.0], 'C': [5.0, 5.0], 'D': [5.0, 5.0]}
- 方式B: 正規化0.38 順位10.5 軸別={'A': [1.0, 1.0], 'B': [0.0, 0.0], 'C': [0.0, 0.0], 'D': [2.0, 2.0]}
- 方式C: 正規化0.66 順位4.5 軸別={'hook': [1.0, 2.0], 'development': [5.0, 5.0], 'aftertaste': [3.0, 3.0], 'originality': [5.0, 5.0]}
- 方式D: 正規化0.75 順位4.0 軸別={'extractability': [2.0, 2.0], 'loss_severity': [5.0, 5.0], 'reproducibility': [4.0, 4.0], 'style_independence': [5.0, 5.0]}

## 5. 根拠とスコアの矛盾候補(機械抽出)

候補21件(弱点語彙判定は文脈を見ないため偽陽性を含む)。

- 方式A L05 rep1 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['失われ']
- 方式A L05 rep2 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['失われ']
- 方式A L09 rep2 [overall_axes_gap] overall: 総合5 vs 軸平均2.75
- 方式B L05 rep1 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['失われ']
- 方式B L05 rep2 [weak_word_vs_high_score] D: 高評価なのに弱点語彙 ['失われ']
- 方式C L01 rep1 [overall_axes_gap] overall: 総合5 vs 軸平均3.00
- 方式C L01 rep2 [overall_axes_gap] overall: 総合5 vs 軸平均3.00
- 方式C L05 rep1 [weak_word_vs_high_score] originality: 高評価なのに弱点語彙 ['失われ']
- 方式C L05 rep2 [weak_word_vs_high_score] originality: 高評価なのに弱点語彙 ['失われ']
- 方式D L03 rep1 [lost_high_vs_loss_severity_score] loss_severity: severity=highの損失1件を列挙しながら loss_severity=4
- 方式D L03 rep2 [lost_high_vs_loss_severity_score] loss_severity: severity=highの損失1件を列挙しながら loss_severity=5
- 方式D L05 rep1 [weak_word_vs_high_score] style_independence: 高評価なのに弱点語彙 ['失われ']
- 方式D L05 rep2 [weak_word_vs_high_score] style_independence: 高評価なのに弱点語彙 ['失われ']
- 方式D L07 rep1 [lost_high_vs_loss_severity_score] loss_severity: severity=highの損失1件を列挙しながら loss_severity=4
- 方式D L07 rep1 [overall_axes_gap] overall: 総合1 vs 軸平均3.00
- 方式D L07 rep2 [lost_high_vs_loss_severity_score] loss_severity: severity=highの損失1件を列挙しながら loss_severity=4
- 方式D L07 rep2 [overall_axes_gap] overall: 総合1 vs 軸平均3.00
- 方式D L10 rep1 [lost_high_vs_loss_severity_score] loss_severity: severity=highの損失1件を列挙しながら loss_severity=5
- 方式D L10 rep2 [lost_high_vs_loss_severity_score] loss_severity: severity=highの損失1件を列挙しながら loss_severity=5
- 方式D L12 rep1 [lost_high_vs_loss_severity_score] loss_severity: severity=highの損失1件を列挙しながら loss_severity=5
- 方式D L12 rep2 [lost_high_vs_loss_severity_score] loss_severity: severity=highの損失1件を列挙しながら loss_severity=5

## 6. 引用の文字列一致率(原作理解の誤りとは別集計)

| 方式 | 引用数 | 不一致 | 一致率 |
|---|---|---|---|
| A | 96 | 0 | 1.000 |
| B | 96 | 0 | 1.000 |
| C | 96 | 0 | 1.000 |
| D | 96 | 0 | 1.000 |

不一致の内訳: {}(near=表記ゆれ・軽微な欠落、absent=原文に存在しない)。

## 7. 原作理解の誤り候補(機械抽出。確定は人/Claude)

- [character_not_in_source] A L01 mock
- [character_not_in_source] A L01 mock
- [character_not_in_source] A L02 mock
- [character_not_in_source] A L02 mock
- [character_not_in_source] A L03 mock
- [character_not_in_source] A L03 mock
- [character_not_in_source] A L04 mock
- [character_not_in_source] A L04 mock
- [character_not_in_source] A L05 mock
- [character_not_in_source] A L05 mock
- [character_not_in_source] A L07 mock
- [character_not_in_source] A L07 mock
- [character_not_in_source] A L08 mock
- [character_not_in_source] A L08 mock
- [character_not_in_source] A L09 mock
- [character_not_in_source] A L09 mock
- [character_not_in_source] A L10 mock
- [character_not_in_source] A L10 mock
- [character_not_in_source] A L11 mock
- [character_not_in_source] A L11 mock
- [character_not_in_source] A L12 mock
- [character_not_in_source] A L12 mock
- [character_not_in_source] A L13 mock
- [character_not_in_source] A L13 mock
- [character_not_in_source] B L01 mock
- [character_not_in_source] B L01 mock
- [character_not_in_source] B L02 mock
- [character_not_in_source] B L02 mock
- [character_not_in_source] B L03 mock
- [character_not_in_source] B L03 mock
- [character_not_in_source] B L04 mock
- [character_not_in_source] B L04 mock
- [character_not_in_source] B L05 mock
- [character_not_in_source] B L05 mock
- [character_not_in_source] B L07 mock
- [character_not_in_source] B L07 mock
- [character_not_in_source] B L08 mock
- [character_not_in_source] B L08 mock
- [character_not_in_source] B L09 mock
- [character_not_in_source] B L09 mock
- [character_not_in_source] B L10 mock
- [character_not_in_source] B L10 mock
- [character_not_in_source] B L11 mock
- [character_not_in_source] B L11 mock
- [character_not_in_source] B L12 mock
- [character_not_in_source] B L12 mock
- [character_not_in_source] B L13 mock
- [character_not_in_source] B L13 mock
- [character_not_in_source] C L01 mock
- [character_not_in_source] C L01 mock
- [character_not_in_source] C L02 mock
- [character_not_in_source] C L02 mock
- [character_not_in_source] C L03 mock
- [character_not_in_source] C L03 mock
- [character_not_in_source] C L04 mock
- [character_not_in_source] C L04 mock
- [character_not_in_source] C L05 mock
- [character_not_in_source] C L05 mock
- [character_not_in_source] C L07 mock
- [character_not_in_source] C L07 mock

## 8. 運用(時間・費用)

| 方式 | calls | 平均秒 | 平均出力tok | 実費(円) |
|---|---|---|---|---|
| A | 24 | 0.0 | 2000 | 5.76 |
| B | 24 | 0.0 | 2000 | 5.76 |
| C | 24 | 0.0 | 2000 | 5.76 |
| D | 24 | 0.0 | 2000 | 5.76 |

## 9. 人間確認推奨作品

- 各方式の最高/最低: A: 最高L02/最低L13; B: 最高L03/最低L02; C: 最高L08/最低L11; D: 最高L02/最低L01
- 割れ作品: ['L02', 'L11', 'L12', 'L05', 'L08', 'L07', 'L13', 'L03', 'L04']
- 常に確認: ['L05'](重要検証対象『交尾』)

## 10. 推奨・次点・不採用(人/Fableが記入。雛形)

- 最有望: (未記入)
- 次点: (未記入)
- 不採用: (未記入、理由付き)
- 限界・追加検証条件: (未記入)
