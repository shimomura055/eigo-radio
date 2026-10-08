# E2E_EVIDENCE: PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 委任_03 Phase 3

実施日: 2026-10-08。Family X Production runner(正式入口 `er019_family_x_entertainment_production_runner_01.py`)を本文生成まで(TTSなし、本runnerにTTS stageは無い)1記事実行。テーマは過去に完走した既存入力(`er019_output/family_x_b3_production_wiring_01/run_01/entry_point.json`のargs.theme = 「Meta Muse AI電話代行『人間コンシェルジュ』実験」)を再利用(新規テーマ選定なし)。out-dir: `er052_output/gpt6_wiring_e2e_01/run_01`。commit: Phase 1=92e07c40 / Phase 2=756ed882(コードは両commit後の状態で実行)。

## 結果(事実)

- **完走せず、Production Gateで正規にSTOP**: Advanced(EN)deviation checkが2回連続MAJOR(attempt1=案B JA再生成後も、attempt2=must-fix再生成後も)→ `RuntimeError: [STOP] Advanced deviation check: 再生成後もMAJOR...`。Standard stage・Key Phrase explanation stageには到達していない。
- STOP理由(deviation_checks/advanced_attempt1.json, attempt2.json、model=gpt-6-luna): MAJOR/origin=translation。attempt1「全体のAI電話アシスタントのテストを中断したように読めるが、Ledgerで確認されているのは人間担当者が関与する電話機能の当面のロールバック」、attempt2「`AI phone feature`とすることで、ロールバック対象を人間担当者関与の電話機能からAI電話機能全体へ広げている」。ModelContractViolation・単価未登録例外・5.6残存は発生していない。Gateは無効化していない。
- 実行は3回(attempt1: `--stage standard`指定ミスによるb1b不在FileNotFoundError[ログ`run_01_attempt1_stdout_stage_standard_arg_error.log`、API呼び出しはresearch〜JA writerまで]→ attempt2: `--stage all`、JA_RECHECK_REQUIRED STOP→案BでJA再生成 → attempt3: 再実行1回、Advanced MAJOR再STOP)。同一out-dirのraw_usage_log.jsonlに累積。

## 受入3点

| # | 項目 | 結果 |
|---|---|---|
| 1 | raw_usage_logのprocess別model_id | 観測した全11 stage・計 33 call 全てが `gpt-6-luna`(下表)。`gpt-5.6-luna`は0件。未観測: standard / kp_explanation(Gate STOPで未到達) |
| 2 | cost.json > 0 | **runner自身のcost.jsonは未生成**(STOP例外でmain()が`_write_cost_json`に到達しないため)。同runnerの`compute_stage_cost_breakdown()`を事後実行した値を`cost_at_stop_computed.json`に保存: total_jpy=19.481(>0、web_search 8 call含む) |
| 3 | 予算ガード累計 > 0 | stdout: `[E-FAMILY-RUNNER][cost] so far=5.89 JPY`(after research_ledger、attempt3)等。6-luna単価でfail-closed lookupが成功し>0。(最終`compute_cost_jpy_so_far`=6.68 JPY) |

## process別 model_id 実測(raw_usage_log.jsonl 集計、provider=openai)

| stage | model_id | call | input_tokens | output_tokens |
|---|---|---|---|---|
| research | gpt-6-luna | 1 | 41,923 | 5,898 |
| ledger | gpt-6-luna | 1 | 27,511 | 2,591 |
| storyline_b3 | gpt-6-luna | 1 | 3,016 | 4,202 |
| ja_original | gpt-6-luna | 2 | 4,174 | 6,777 |
| ja_original_check | gpt-6-luna | 2 | 7,501 | 3,124 |
| ja_original_must_fix | gpt-6-luna | 1 | 3,264 | 2,695 |
| ja_original_check_retry | gpt-6-luna | 1 | 4,028 | 681 |
| ja_r1 | gpt-6-luna | 2 | 14,168 | 2,990 |
| ja_r2 | gpt-6-luna | 2 | 17,766 | 2,971 |
| ja_r2_check | gpt-6-luna | 2 | 7,375 | 1,708 |
| advanced | gpt-6-luna | 12 | 25,156 | 18,694 |

web_search_call_count 合計 8(research 6 + ledger 2)。

## 費用・所要

- 実費(runnerの`compute_stage_cost_breakdown`): **¥19.48**(うちweb_search 8 call分を含む。stage別: research 10.743 / ledger 3.847 / storyline_b3 0.384 / ja_original 0.609 / ja_original_check 0.370 / must_fix 0.268 / check_retry 0.119 / ja_r1 0.466 / ja_r2 0.522 / ja_r2_check 0.255 / advanced 1.898)。上限¥30内。
- 所要: attempt1 270秒 / attempt2 195秒 / attempt3 76秒(epoch差、各`attempt*_start/end_epoch.txt`と`start/end_epoch.txt`)。合計541秒。

## 付随して判明した事実(未修正・範囲外)

- `er012_e...compute_cost_jpy_so_far()`(`assert_budget_ok`の予算ガード)は web_search tool課金(`web_search_call`単価)を計上しない。本E2Eでガード表示累計=6.68 JPYに対し、runnerの`compute_stage_cost_breakdown`は19.48 JPY(差=web_search 8 call分≒12.8 JPY)。`--budget-jpy 15`は事実上トークン費のみを制限した。本変更(単価未登録のfail-closed化)で生じた差ではなく既存仕様。修正は本委任のscope外のため行っていない(Fable判断事項)。
- 本件はO3(量産最初の10本で「EN Advanced deviation STOP 3本以上または保留0.3/記事以上」で条件D見直し)の観測として、n=1中STOP 1件(5.6時代の同一テーマrun_01は同Gateを通過して完走[`er019_output/.../run_01/cost.json`にadvanced/standard有り])。nが小さく評価は未確定。
