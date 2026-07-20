# ER-002-v1.2M-JA / ER-003-P2 sentence metrics review (ER-003-P2A)

B2文長計測ロジックの根本原因修正前後の比較。APIは一切呼んでいない。B2本文は一切変更していない。

## A01

- 入力sha256: `f2b83508b1dc57e8aa5c655ec9b1803a414e006cbb63e10717ef79481bb082fb`(P2実行時と不変)

| 指標 | 修正前 | 修正後 |
|---|---|---|
| 文数 | 26 | 29 |
| 平均文長 | 11.46 | 10.28 |
| 最長文 | 24 | 24 |
| 32語超の文数 | 0 | 0 |
| B2_SENTENCE_METRICS判定 | B2_SENTENCE_METRICS_PASS | B2_SENTENCE_METRICS_PASS |

修正後、32語を超える文は存在しない。

## A02

- 入力sha256: `ca3c14ddefe4ef1264a3d72ea09330cbd5cdac70d4ba04830b07d44a788e08e2`(P2実行時と不変)

| 指標 | 修正前 | 修正後 |
|---|---|---|
| 文数 | 30 | 33 |
| 平均文長 | 13.2 | 12.0 |
| 最長文 | 59 | 28 |
| 32語超の文数 | 2 | 0 |
| B2_SENTENCE_METRICS判定 | B2_SENTENCE_METRICS_FAIL | B2_SENTENCE_METRICS_PASS |

修正後、32語を超える文は存在しない。

## ADD03

- 入力sha256: `2086548c88c07f9ef1d198d897c81f763f741fb289b7c49c9f38909f8e1343aa`(P2実行時と不変)

| 指標 | 修正前 | 修正後 |
|---|---|---|
| 文数 | 31 | 36 |
| 平均文長 | 12.55 | 10.81 |
| 最長文 | 37 | 18 |
| 32語超の文数 | 2 | 0 |
| B2_SENTENCE_METRICS判定 | B2_SENTENCE_METRICS_FAIL | B2_SENTENCE_METRICS_PASS |

修正後、32語を超える文は存在しない。
