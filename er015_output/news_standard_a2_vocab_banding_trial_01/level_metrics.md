# level_metrics.md — Level比較(Meta 3段階、参考値、機械判定は最終判断に用いない)

| 記事 | words | sentences | avg words/sent | avg syll/word | long-sent(>=20w)率 | subordinator/100w | FK grade(heuristic) |
|---|---|---|---|---|---|---|---|
| Meta Advanced Baseline | 330 | 25 | 13.2 | 1.455 | 0.16 | 4.55 | 6.72 |
| Meta Standard v1 (B-1) | 325 | 26 | 12.5 | 1.443 | 0.154 | 4.31 | 6.31 |
| Meta Standard v4 | 300 | 31 | 9.68 | 1.43 | 0.032 | 2.67 | 5.06 |
| Sewer Standard v3 (参考、既存計算値を引用) | 331 | 34 | 9.74 | 1.429 | 0.0 | 1.21 | 5.07 |

## 平均語/文の変化(参考)

- Advanced 13.2 -> Standard v1 12.5 -> Standard v4 9.68 (v1比 -2.82語、9〜11語/文目標との差: -0.32)