# TTS retry cool-down hypothesis analysis — summary

(自動生成。手動編集しないこと。再実行のたびに上書きされる。)

- 入力: er011_output/tts_retry_timing_monitor_01/observations.jsonl
- retry-after-NGペア総数: 56 (種別B: 53, 種別A参考値: 3)

## 表1: 種別B(品質NG)— 間隔bucketのみ

| bucket | N | PASS | PASS率 |
|---|---|---|---|
| 即時<150秒(同一run内自動retry相当) | 46 | 25 | 0.5435 |
| 長 6時間以上(別日相当) | 1 | 1 | 1.0 |
| 中 30分〜6時間 | 2 | 1 | 0.5 |
| 短時間 150秒〜30分 | 4 | 3 | 0.75 |

## 表2: 種別B — 連続NG回数 × 間隔bucket

| 連続NG回数 | bucket | N | PASS | PASS率 | 例 |
|---|---|---|---|---|---|
| 1 | 即時<150秒(同一run内自動retry相当) | 34 | 23 | 0.6765 | kp5_ja_charon@3s(NG); meaning_4@3s(PASS); kp2_ja_charon@4s(PASS); kp4_ja_charon@4s(PASS); meaning_2@5s(PASS); meaning_2@5s(PASS); kp_new_normal@5s(NG); kp4_en@5s(PASS) |
| 1 | 中 30分〜6時間 | 1 | 1 | 1.0 | point_two_heading@8357s(PASS) |
| 1 | 短時間 150秒〜30分 | 2 | 1 | 0.5 | meaning_4@172s(NG); point_two@377s(PASS) |
| 2 | 即時<150秒(同一run内自動retry相当) | 10 | 2 | 0.2 | kp4_ja_charon@4s(PASS); kp5_ja_charon@4s(NG); kp_new_normal@4s(NG); point_one@17s(NG); point_two@26s(NG); full_story_part1@37s(NG); point_two@43s(NG); point_one@50s(PASS) |
| 3plus | 即時<150秒(同一run内自動retry相当) | 2 | 0 | 0.0 | kp_new_normal@3s(NG); kp5_ja_charon@4s(NG) |
| 3plus | 長 6時間以上(別日相当) | 1 | 1 | 1.0 | full_story_part1@51635s(PASS) |
| 3plus | 中 30分〜6時間 | 1 | 0 | 0.0 | kp5_ja_charon@2350s(NG) |
| 3plus | 短時間 150秒〜30分 | 2 | 2 | 1.0 | kp5_ja_charon@282s(PASS); point_one@567s(PASS) |

## 表3: 種別B — generation_path × 手動介入補正 × 間隔bucket

| generation_path(機械判定) | 介入補正 | bucket | N | PASS | PASS率 |
|---|---|---|---|---|---|
| automatic_retry_within_loop_cap | deliberate_override | 中 30分〜6時間 | 1 | 1 | 1.0 |
| automatic_retry_within_loop_cap | no_override | 即時<150秒(同一run内自動retry相当) | 39 | 21 | 0.5385 |
| automatic_retry_within_loop_cap | no_override | 短時間 150秒〜30分 | 2 | 1 | 0.5 |
| manual_regenerate_beyond_loop_cap | no_override | 即時<150秒(同一run内自動retry相当) | 7 | 4 | 0.5714 |
| manual_regenerate_beyond_loop_cap | no_override | 長 6時間以上(別日相当) | 1 | 1 | 1.0 |
| manual_regenerate_beyond_loop_cap | no_override | 中 30分〜6時間 | 1 | 0 | 0.0 |
| manual_regenerate_beyond_loop_cap | no_override | 短時間 150秒〜30分 | 2 | 2 | 1.0 |

## Fisher正確検定(参考値、種別Bのみ、即時 vs 非即時統合)

- 即時: N=46, PASS率=0.5435
- 非即時(短+中+長統合): N=7, PASS率=0.7143
- 両側Fisher正確検定 p値 = 0.6851(参考値。件数が小さいため解釈注意)

## 「傾向が十分出た」の事前定義基準と現時点の判定

- 基準: 各binでN>=20 かつ、即時binと非即時bin(いずれか)のPASS率の差が20ポイント以上、かつ全ての非即時binに『deliberate_intervention'(手動介入・別run再実行)を伴わない自然発生の長間隔retryサンプル』が最低5件以上含まれること(手動介入100%のサンプルでは時間経過そのものの効果と介入効果を分離できないため)。
- 現状: 4bucket中の最小N = 1(基準N>=20)
- 現状: 即時 vs 非即時のPASS率差 = 17.1ポイント(基準20ポイント以上)
- 現状: 手動介入を伴わない非即時サンプル数 = 2件(基準5件以上、内訳: ['meaning_4@172s(short)', 'point_two@377s(short)'])
- **基準到達: False**

## 非即時(>=150秒)全件の個別監査(隠蔽なし、全件記載)

| segment | 間隔 | bucket | 連続NG | 結果 | generation_path | 介入補正 | 介入confound疑い |
|---|---|---|---|---|---|---|---|
| meaning_4 | 172s | short | 1 | NG | automatic_retry_within_loop_cap | なし | no |
| kp5_ja_charon | 282s | short | 6 | PASS | manual_regenerate_beyond_loop_cap | なし | YES |
| point_two | 377s | short | 1 | PASS | automatic_retry_within_loop_cap | なし | no |
| point_one | 567s | short | 3 | PASS | manual_regenerate_beyond_loop_cap | なし | YES |
| kp5_ja_charon | 2350s | medium | 3 | NG | manual_regenerate_beyond_loop_cap | なし | YES |
| point_two_heading | 8357s | medium | 1 | PASS | automatic_retry_within_loop_cap | あり | YES |
| full_story_part1 | 51635s | long | 3 | PASS | manual_regenerate_beyond_loop_cap | なし | YES |

詳細は cooldown_pairs.jsonl / summary.json を参照。
