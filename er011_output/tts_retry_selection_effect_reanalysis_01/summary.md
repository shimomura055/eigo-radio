# TTS retry timing selection-effect reanalysis — summary

(自動生成。手動編集しないこと。再実行のたびに上書きされる。)

- observations: 483件 / cooldown_pairs: 74件

## Section1: 選別効果(素朴集計、種別Bのみ)

| 連続NG回数 | N | PASS | PASS率 | Wilson95%CI |
|---|---|---|---|---|
| 1 | 43 | 29 | 0.6744 | [0.5252, 0.7951] |
| 2 | 12 | 2 | 0.1667 | [0.047, 0.448] |
| 3plus | 15 | 4 | 0.2667 | [0.109, 0.5195] |

## Section2: 主分析(最初の3回全NG→4回目、N=8)

- 即時: N=1, PASS率=0.0, 95%CI=[0.0, 0.7935]
- 非即時: N=7, PASS率=0.4286, 95%CI=[0.1582, 0.7495]
- 差: 42.9ポイント、Fisher両側p=1.0、OR=0.4286(0セルありのためHaldane-Anscombe補正(+0.5)適用済み(参考値))
- 介入なし副分析: N=0件(統計不能)
- **母集団8件中8件が人的介入あり(100%)**

### 8件の内訳

| segment | gap | bucket | 4回目結果 | route変化 | 既知介入 |
|---|---|---|---|---|---|
| kp_new_normal | 3s | immediate | NG | なし | deliberate_diagnostic_parameter_sweep |
| point_one | 567s | short | PASS | なし | manuscript_text_change_before_regen |
| kp5_ja_charon | 2350s | medium | NG | あり | explicit_approve_regenerate_plus_route_change |
| full_story_part2 | 2466s | medium | NG | なし | explicit_approve_regenerate |
| full_story_part1 | 2716s | medium | NG | なし | explicit_approve_regenerate |
| full_story_part1 | 51635s | long | PASS | なし | explicit_approve_regenerate |
| meaning_4 | 71819s | long | PASS | あり | explicit_approve_regenerate_plus_route_change |
| comment_2 | 75332s | long | NG | あり | explicit_approve_regenerate_plus_route_change |

## Section3: 副分析(連続NG>=3、位置不問、N=15)

- 即時: N=4, PASS率=0.0
- 非即時: N=11, PASS率=0.3636
- Fisher両側p=0.5165
- manual_regenerate_beyond_loop_cap: 15/15件(100%)

## Section5: タオルB1 full_story_part1 観測例

- take4 gap=2716.0秒, 結果=NG
- take4以降、2022 survey文の欠落(content drop)は解消したが、take5で新たな残存差分(has→had、TRUE_CONTENT_MISMATCH、語差型)が発生し、segmentは現在もHUMAN_REVIEW_REQUIREDのまま未解決(既存FAMILY-A-DISCOVERY-TOWELS-B1B-SECONDARY-ASR-AND-RETRY-TIMING-RECONCILE-01_REPORT.md Part A/B参照)
- 既存報告(同上REPORT.md 5節)で『時間経過ではなく人的介入(review_lock.approve_regenerate()の明示的呼び出し)』と既に分類済み。時間効果単独への帰属はできない。本reanalysisはこの結論を上書きしない(1事例のみでの時間効果断定は禁止、指示7項)。

## Section6: 検出力計算(参考値)

| 即時PASS率(仮定) | 非即時PASS率(仮定) | 差(pt) | 必要N/群(alpha.05,power.8) |
|---|---|---|---|
| 0.1 | 0.4 | 30.0 | 29 |
| 0.2 | 0.4 | 20.0 | 79 |
| 0.3 | 0.4 | 10.0 | 354 |

- 現状の『介入なし』有効サンプル: 0件(主分析・副分析とも)

## Closeout

- **verdict: REJECTED**
- 『時間を空けるretry』をProduction仕様候補として今回採用しない、という意味でのREJECTED。『時間経過に効果が存在しない』という主張のREJECTEDではない(N不足・交絡のため効果の有無自体が判定不能。指示のとおり有意差なし=効果なしとは結論しない)。
- N不足: 主分析N=8(うち介入なし0件)、副分析N=15(うち介入なし0件)。
- 交絡: システム構造上、max_attempts超のattemptは常に人的介入を伴う。現行ログには『介入なしで時間だけ空いた自然発生の4回目retry』が存在しない。
- 選別効果: 素朴な連続NG回数別PASS率の低下(69%→17%→24-27%)は、同一の困難segmentが複数position(4,5,6回目…)で重複計上されることによる部分が大きい。母集団を『最初の3回全NG→4回目』に一意化すると、非即時群のPASS率(36-43%)は素朴な3+バケツの値(24-27%)よりむしろ高く、選別効果を制御すると『連続NGが即座に悪化を意味する』という単純な解釈は支持されない。

詳細はstrict_population_cases.jsonl / broader_3plus_cases.jsonl / summary.jsonを参照。
