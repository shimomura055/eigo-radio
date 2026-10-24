# BUDGET_LOG_OB_03 (委任_22 run_03 の費用台帳。本委任の全有料支出)

- 承認: `er110_output/family_y_opinion_based_02/BUDGET_APPROVED.json`(Fable委任_22 §2、合計上限25円・1run)。起動は `er110_family_y_opinion_based_02.py run_03 --paid` の**1回のみ**(再起動0回、PID 13548、終了コード0)。モデル: 生成=gpt-6.1-sol(最新世代最上位系)、付番・構造タグ・Leakage判定=gpt-6-luna(理由=低コストで足りる機械照合/判定のみ)。
- 台帳の出典: `run_03/raw_usage_log.jsonl`のcost aggregate(`state.json` final_cost_jpy)と`budget_trace.json`。下表のstage名は並列thread間のタグ付けの重なりでずれる行がある(UNTAGGED・別Voice名)。**信頼できるのはrun累計列**。台帳(stdout控え)は`er110_output/family_y_opinion_based_02/run_03.log`。

## 段階別(budget_trace / stdoutのrun累計)

| 段階 | stage(call) | 増分(円) | run累計(円) |
|---|---|---|---|
| gen | ypl_ob_voice_1 | 5.198 | 13.637 |
| gen | ypl_ob_voice_2 | 4.415 | 13.637 |
| gen | ypl_ob_voice_3 | 4.024 | 13.637 |
| map1 | UNTAGGED | 0.211 | 14.17 |
| map1 | ypl_ob_map_voice_1_m1 | 0.215 | 14.17 |
| map1 | ypl_ob_map_voice_3_m1 | 0.107 | 14.17 |
| unmapped_regen | ypl_ob_map_voice_2_m1 | 4.863 | 22.901 |
| unmapped_regen | ypl_ob_voice_3_unmapregen | 3.868 | 22.901 |
| map2 | ypl_ob_map_voice_3_m2 | 0.126 | 23.159 |
| map2 | ypl_ob_voice_2_unmapregen | 0.132 | 23.159 |
| structure1 | ypl_ob_structure1 | 0.088 | 23.247 |
| final_map | ypl_ob_map_voice_1_final | 0.147 | 23.667 |
| final_map | ypl_ob_map_voice_2_final | 0.142 | 23.667 |
| final_map | ypl_ob_map_voice_3_final | 0.131 | 23.667 |

stdout控え(`run_03.log`): gen +13.637(54.7秒) → map1 +0.533(87.4秒) → unmapped_regen +8.731(139.6秒、V2・V3の各1回) → map2 +0.258 → structure1 +0.088(159.4秒) → final_map +0.42(209.0秒) → DONE。

- **run_03 実績: 23.667円**(承認上限25円以内)、所要約209秒。Gate(Leakage判定)は累計22円超のため`SKIPPED_BUDGET`(01から続く歯止め。再起動なし)。
- 本委任の有料支出合計: **23.667円**(run_03のみ。testは`--paid`を与えない隔離で、API呼出0)。0円作業: Fable評価記録、起動ガード、OPEN-493修正、集計。
- 10-24日次累計: 委任_21までの約390円(`BUDGET_LOG_OB_02.md` §3) + 23.667円 = **約413.7円**(本案件の把握分。他案件=KP委任_30・ASR委任_05等の並行支出は含まない)。日次1,000円の範囲内。

## 委任_23 追記: Leakage Gate後追い(2026-10-24)

- 承認: Fable委任_23(Gate後追い、上限2円、本文の再生成なし)。run_03の`voices_final.json`(本文)に対し、`run_gate_pl`を`max_judgements=1`で1回だけ実行(判定gpt-6-luna、effort=high。flag時の書換(sol)は構造上発生しない設定。実際はflagなし)。使い捨てスクリプトはscratchpad(リポジトリ外)、費用ログは`run_03/raw_usage_log_gate.jsonl`(別file)。
- 結果: **PASS**(7項目x3 Voice=21項目、flagged 0、n_fail_fields 0)。証跡=`run_03/gate_voices/{leak_check_1,gate_result,final_texts}.json`。`run_03/run_status.json`と`state.json`のgate_statusを`SKIPPED_BUDGET`->`PASS`に更新(`gate_status_original`・`gate_status_note`で後追いと明記、本文・final_textsは不変)。
- 費用: 本委任のAPI支出 **0.109円**(上限2円以内)。run_03の合計 23.667 + 0.109 = **23.776円**。再起動0回、Python環境は`.venv`(stop_scope_check: rc=0 非停止、`docs/pm/delegation_log/2026-10-24_FYV23_stop_check.json`)。
- 10-24日次累計(本案件の把握分): 約413.7円 + 0.109円 = **約413.8円**(他案件の並行支出は含まない)。日次1,000円の範囲内。
