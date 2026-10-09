# RESULT_TABLE_02: 追加Trial 結果(自動生成 aggregate_02.py、集計対象モデル=gpt-6-luna, gpt-5.6-luna, gpt-5.6-sol, deepseek-v4-flash)

## 1. 横並び(label rep1/rep2)

| case | human_tier | gpt-6-luna | gpt-5.6-luna | gpt-5.6-sol | deepseek-v4-flash |
|---|---|---|---|---|---|
| K01 | ユーザー確認済み(C、2026-10-09) | B/A | A/A | A/A | A/A |
| K02 | ユーザー確認済み | B/B | B/B | B/B | C/C |
| K03 | ユーザー確認済み(C、2026-10-09) | B/B | C/C | C/C | C/C |
| K04 | Sonnet暫定(未ラベル) | B/B | A/A | A/A | B/B |
| K06 | Sonnet暫定(ユーザー未裁定) | B/B | B/B | B/B | B/B |
| K08 | ユーザー確認済み(A、2026-10-09)。履歴: Son | A/A | A/A | A/A | A/A |
| K09 | ユーザー確認済み(A、2026-10-09)。履歴: Son | A/B | A/A | A/A | A/A |
| K10 | Sonnet暫定(因果語を含むため境界へ移動) | A/A | A/A | A/A | A/A |
| K11 | ユーザー判断(C寄り・Bの余地あり、2026-10-09) | B/B | B/B | B/B | B/B |
| K12 | ユーザー確認済み(A、2026-10-09)。履歴: Son | A/A | A/A | A/A | B/A |

## 2. モデル別指標

| model | M1判定(K01,K02,K03 x rep1,rep2) | M1 | C数(M1) | M2判定(K08,K09,K12) | M2 | M4自己一致 | K11 | 形式違反 | 実費JPY(登録単価) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-6-luna | BABBBB | REJECTED | 0/6 | AAABAA | PASS | 80% | B/B | 0 | 0.65 |
| gpt-5.6-luna | AABBCC | REJECTED | 2/6 | AAAAAA | PASS | 100% | B/B | 0 | 1.11 |
| gpt-5.6-sol | AABBCC | REJECTED | 2/6 | AAAAAA | PASS | 100% | B/B | 0 | 25.98 |
| deepseek-v4-flash | AACCCC | REJECTED | 4/6 | AAAABA | PASS | 90% | B/B | 0 | 6.06 |

## 3. モデル別Status(PREREGISTRATION_02 s6)

- gpt-6-luna: REJECTED
- gpt-5.6-luna: REJECTED
- gpt-5.6-sol: REJECTED
- deepseek-v4-flash: REJECTED

## 4. 人間既知ラベルとChecker参考(Checkerは正解扱いしない)

| case | 人間既知 | Checker参考 |
|---|---|---|
| K01 | C=重大(ユーザー確認済み 2026-10-09。方向反転: ロールバックを復元と記述)。履歴: Fable確定+ユーザー呼称(旧区分) | 見逃し: 機械候補(negation_polarity_mismatch)→Stage1/Stage2=ACCEPTABLE→S1第2意見=ACCEPTABLE |
| K02 | 重大(台帳EVID-008の外部到達・不正アクセスと矛盾し、外へ出ていないと誤解させる) | 見逃し: Stage1 dev=MAJOR(scope拡大・unsupported_new_claim)→Stage2 materiality=QUALITY( |
| K03 | C=重大(ユーザー確認済み 2026-10-09。再有効化と読める意味反転。Safety-critical gold A5-0)。履歴: Fable確定(旧区分 | Checkerではなく旧Deviation Check: v1でMAJOR検出→must-fix retry 1回→LEDGER_COMPLIANT(当時は検出 |
| K04 | 未確定: Sonnetは『誤読はJA R0で既に発生』と記述(ユーザー未確認)。同型の『元に戻した』系はRB/CCP評価で『曖昧』(ユーザーはCCPの10件に異 | なし(JA R0はChecker未適用) |
| K06 | Sonnet W1=軽微(確信0.5、基準(6)字義なら重大寄り)。ユーザー回答待ち(HUMAN_CHECK_E2E_01 S-2) | 最終EN本文に残存(residual_miss。Checkerは修正せず) |
| K08 | 問題なし(類似文F-12は新9 runでSonnetが問題なしとラベル。この文自体は2026-10-09にユーザー確認済み=A) | 当該文は候補化されず(local_contextとして登場のみ) |
| K09 | 問題なし(ユーザー確認済み 2026-10-09。新9 runでSonnetが問題なしとラベル、台帳とほぼ逐語一致) | 未確認(参考なし) |
| K10 | 未確定(台帳のmisconfiguredと矛盾しないが『because of』で因果を明示=因果追加型。Opus所見によりM2から除外。ユーザー判定の対象は別文 | Stage1で候補化(causal_not_in_fact, negation_polarity_mismatch)→Stage2 ACCEPTABLE |
| K11 | C寄り・B余地あり(ユーザー判断 2026-10-09)。履歴: 重大(Sonnet判定。認められたのは『軌道上space control weapons配備』 | JA文のためChecker評価対象外(Checkerはなし EN のみ評価)。同内容のEN文はRewrite cycle1で BLOCKING検出→修正済(NG |
| K12 | 問題なし(Rollback評価ラベル=correct。『取りやめ/put on hold』で方向が確定、と単独評価)。ユーザー確認済み(A、2026-10-09 | 記事は最終PASS系(当該文でCheckerが候補化したかは未確認) |

## 5. C検出数・K11・両B件数

| model | K01 C数/2 | K02 C数/2 | K03 C数/2 | K11 C数/2 | K11 A見逃し数 | 両B件数(rep1,rep2とも同一caseでB) |
|---|---|---|---|---|---|---|
| gpt-6-luna | 0 | 0 | 0 | 0 | 0 | 5 |
| gpt-5.6-luna | 0 | 0 | 2 | 0 | 0 | 3 |
| gpt-5.6-sol | 0 | 0 | 2 | 0 | 0 | 3 |
| deepseek-v4-flash | 0 | 2 | 2 | 0 | 0 | 3 |

## 6. sol x deepseek 人間確認対象率(rep別、10ケース)

定義1=2評価者のラベル不一致のみ / 定義2=不一致+両方B。

| rep | 不一致case | 両Bcase | 定義1 | 定義2 |
|---|---|---|---|---|
| rep1 | K02,K04,K12 | K06,K11 | 3/10=30% | 5/10=50% |
| rep2 | K02,K04 | K06,K11 | 2/10=20% | 4/10=40% |

## 7. 事前登録の機械適用(PREREGISTRATION_02 s4-s6)

「改善」= M1 PASS、またはC数>0(gpt-6-lunaのC=0超)かつM2 PASS。

| model | M1 | M2 | M4 | 改善 | 安定検出(M1 6/6 C) | モデル別Status |
|---|---|---|---|---|---|---|
| gpt-6-luna | REJECTED | PASS | 80% | なし | いいえ | REJECTED |
| gpt-5.6-luna | REJECTED | PASS | 100% | あり | いいえ | REJECTED |
| gpt-5.6-sol | REJECTED | PASS | 100% | あり | いいえ | REJECTED |
| deepseek-v4-flash | REJECTED | PASS | 90% | あり | いいえ | REJECTED |

- 解釈規則の機械適用: Sol改善=True / DeepSeek改善=True。M1 PASS(安定検出)モデル=なし。
- 機械Status(Trial全体、対象=gpt-6-luna,gpt-5.6-luna,gpt-5.6-sol,deepseek-v4-flash): **REJECTED**
- 注意: 成功しても「LLM Checkerが客観的に正しい」とは結論しない。n=10・重大3件(+参考1)の機能確認。最終判定はFable待ち。

## 8. 実費(usage x 登録単価、USD/JPY=160)

| model | rep1 | rep2 | 合計 JPY |
|---|---|---|---|
| gpt-6-luna | 0.397 | 0.250 | 0.648 |
| gpt-5.6-luna | 0.637 | 0.478 | 1.115 |
| gpt-5.6-sol | 15.006 | 10.970 | 25.975 |
| deepseek-v4-flash | 3.903 | 2.161 | 6.064 |
| 合計(前Trial luna分+追加Trial) | | | 33.802 |

追加Trial分(sol+deepseek)= JPY 32.039。sol実効パラメータ: reasoning=medium, temperature=指定なし(拒否された), seed=未対応。形式違反0・再呼び出し0・例外0。

## 9. 揺れる論点(分けて記載、断定しない)
1. 解釈規則の衝突: 事前登録の「改善」定義(C数>0かつM2 PASS)を機械適用するとSol・DeepSeek・5.6-lunaは「改善あり」だが、「安定検出」(M1 6/6 C)を満たすモデルはゼロ。§5の「両方でも重大を安定検出できない→方式の現実性に強い疑義」にも該当する。どちらを主とするかはFable判断。
2. K01(restored vs rolled back、方向反転): 4モデル全てがrep1/rep2ともC検出なし(sol=A/A、DeepSeek=A/A、5.6-luna=A/A、6-luna=B/A混在)。モデル性能・vendorを替えても改善せず。ケース定義(言い換え許容範囲)の問題かモデル能力かは未切り分け。
3. K03はsol・5.6-luna・DeepSeekで安定C、K02はDeepSeekのみC。検出がケース偏在でn=10・HC-012偏重の限界は継承。
4. sol(高性能・高単価)はDeepSeekより安定検出が増えていない(M1 C数2/6 vs 4/6)。コスト対効果の観点ではsolは優位でない。
5. K04(Sonnet暫定のB寄り)をsol・5.6-lunaはA/Aとしたが人間未確定のためM指標に不使用。
