# level_metrics.md — Level比較(6記事、参考値、機械判定は最終判断に用いない)

| 記事 | words | sentences | avg words/sent | avg syll/word | long-sent(>=20w)率 | subordinator/100w | FK grade(heuristic) |
|---|---|---|---|---|---|---|---|
| 下水道 Advanced(A-1) | 354 | 26 | 13.62 | 1.483 | 0.077 | 3.11 | 7.22 |
| 下水道 Standard v1(A-2) | 364 | 27 | 13.48 | 1.451 | 0.074 | 2.75 | 6.78 |
| 下水道 Standard v2 | 333 | 35 | 9.51 | 1.465 | 0.0 | 1.5 | 5.41 |
| Meta Advanced(Baseline) | 330 | 25 | 13.2 | 1.455 | 0.16 | 4.55 | 6.72 |
| Meta Standard v1(B-1) | 325 | 26 | 12.5 | 1.443 | 0.154 | 4.31 | 6.31 |

## 平均語/文の変化(参考)

- 下水道: Advanced 13.62 -> v1 13.48 (-0.14) -> v2 9.51 (Advanced比 -4.11、9〜11語/文目標との差: -0.49)
- Meta: Standard v2未生成(budget STOP。下水道v2の1call完了時点で累計¥1.0828が上限¥1を超過したため2call目[Meta]は実行していない)

CEFR推定: なし(既存の.venvにtextstat等の推定ツールが無く、新規install未実施のためN/A。上記は標準ライブラリのみによる簡易ヒューリスティック参考値であり、機械判定を最終判断には用いない)。