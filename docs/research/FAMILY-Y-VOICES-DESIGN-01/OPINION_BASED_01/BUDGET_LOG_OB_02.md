# BUDGET_LOG_OB_02 (委任_21 改善R0 2本の費用台帳。呼出別)

- 承認: `er110_output/family_y_opinion_based_02/BUDGET_APPROVED.json`(Fable作成、合計上限45円・2run・1runの歯止め22.5円)。モデル: 生成=gpt-6.1-sol(最新世代最上位系)、付番・構造タグ・Leakage判定=gpt-6-luna(理由=低コストで足りる機械照合/判定のみ)。
- 台帳の出典: 各runの`raw_usage_log.jsonl`をcost aggregate(`er053_cost_aggregate_01`)で集計した値と`budget_trace.json`(段階ごとの増分)。run_02a/run_02bの2本は並列に1回ずつ起動(再起動0回)。
- **注意(事故)**: 実run中に私(Sonnet)が走らせた全test実行が、`main(run_name)`testの承認ファイル読込バグ(`read_cap`の既定引数が定義時の実パスに固定され、testのmonkeypatchが効かなかった)により、**本物の有料runをtest用tmpフォルダで2回起動**した(約20.6円と約30.0円)。バグはその後修正。この2回の出力は記事に使っておらず、費用だけ発生した。§3に別記。旧共有台帳(`BUDGET_LOG_OB_run_02a/02b.md`)は4runの行が混在したため、本ファイルに作り直した。

## run_02a 段階別(budget_trace)

| 段階 | stage(call) | 増分(円) | run累計(円) | 経過(秒) |
|---|---|---|---|---|
| gen | ypl_ob_voice_1 | 4.579 | 12.434 | 43.2 |
| gen | ypl_ob_voice_2 | 4.202 | 12.434 | 43.2 |
| gen | ypl_ob_voice_3 | 3.653 | 12.434 | 43.2 |
| map1 | ypl_ob_map_voice_1_m1 | 0.168 | 12.933 | 64.9 |
| map1 | ypl_ob_map_voice_2_m1 | 0.193 | 12.933 | 64.9 |
| map1 | ypl_ob_map_voice_3_m1 | 0.138 | 12.933 | 64.9 |
| unmapped_regen | ypl_ob_voice_3_unmapregen | 4.772 | 17.705 | 102.3 |
| map2 | ypl_ob_map_voice_3_m2 | 0.17 | 17.875 | 121.3 |
| structure1 | ypl_ob_structure1 | 0.088 | 17.963 | 128.2 |
| gate | ypl_ob_voices_gate_leak1 | 0.263 | 20.092 | 175.8 |
| gate | ypl_ob_voices_gate_leak2 | 0.108 | 20.092 | 175.8 |
| gate | ypl_ob_voices_gate_rewrite1 | 1.758 | 20.092 | 175.8 |
| final_map | ypl_ob_map_voice_1_final | 0.2 | 20.639 | 234.1 |
| final_map | ypl_ob_map_voice_2_final | 0.129 | 20.639 | 234.1 |
| final_map | ypl_ob_map_voice_3_final | 0.218 | 20.639 | 234.1 |

- run_02a: raw_usage_log集計 **20.639円**、所要 234.1秒(開始 2026-10-24T00:19:00+00:00)

## run_02b 段階別(budget_trace)

| 段階 | stage(call) | 増分(円) | run累計(円) | 経過(秒) |
|---|---|---|---|---|
| gen | UNTAGGED | 5.287 | 13.841 | 46.0 |
| gen | ypl_ob_voice_1 | 4.75 | 13.841 | 46.0 |
| gen | ypl_ob_voice_3 | 3.804 | 13.841 | 46.0 |
| map1 | ypl_ob_map_voice_2_m1 | 0.138 | 14.271 | 62.8 |
| map1 | ypl_ob_map_voice_3_m1 | 0.139 | 14.271 | 62.8 |
| map1 | ypl_ob_voice_2 | 0.153 | 14.271 | 62.8 |
| unmapped_regen | ypl_ob_voice_3_unmapregen | 4.599 | 18.87 | 102.9 |
| map2 | ypl_ob_map_voice_3_m2 | 0.184 | 19.054 | 124.9 |
| structure1 | ypl_ob_structure1 | 0.087 | 19.141 | 131.7 |
| gate | ypl_ob_voices_gate_leak1 | 0.175 | 19.316 | 149.6 |
| final_map | ypl_ob_map_voice_1_final | 0.158 | 19.798 | 201.7 |
| final_map | ypl_ob_map_voice_2_final | 0.155 | 19.798 | 201.7 |
| final_map | ypl_ob_map_voice_3_final | 0.169 | 19.798 | 201.7 |

- run_02b: raw_usage_log集計 **19.796円**、所要 201.7秒(開始 2026-10-24T00:19:00+00:00)

## 2. 正規の2本の合計

| run | 費用(円) | 所要(秒) |
|---|---|---|
| run_02a | 20.639 | 234.1 |
| run_02b | 19.796 | 201.7 |
| **合計** | **40.435** | 並列(長い方) |

## 3. test実行による意図しない有料run(事故。成果物には不使用)

| 件 | 内容 | 費用(円) | 根拠 |
|---|---|---|---|
| 1 | 全test実行(.venv)中の`test_main_requires_budget_approval…`が実APIで1run(tmp)。最終段まで進行 | 20.597 | 旧共有台帳の該当行(run累計の最終値) |
| 2 | 再度のtest実行(-x)で同test、1run(tmp)。UNMAPPED再生成3本の後に予算の歯止めで停止 | 30.049 | 同上 |
| 計 | | **50.646** | |

- 正規2本 + 事故2件 = **約91.1円**(承認ファイルの合計上限45円を約46.1円超過)。10-24日次累計は約299円 + 約91円 = 約390円(日次1,000円の範囲内)。
- 再発防止: `read_cap`を実行時参照に修正し、当該testが実承認ファイルを読まないことを確認(全20 test PASS、以後のtest実行でAPI呼出なし)。
