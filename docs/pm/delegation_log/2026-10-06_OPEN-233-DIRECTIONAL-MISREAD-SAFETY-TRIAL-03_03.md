## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03(委任_03: 集計script・合格基準8項目自動チェック・X/Y比較・前回比regression・Closeout数値抽出)。並列委任_01(script)、_02(testset_03)、_04(SSOT)が同時進行。**書込先: `er052_output/open233_directional_misread_trial_03/{aggregate_trial_03.py,regression_vs_trial02.py,selftest/}`、`docs/pm/RESULT_PACKET_T03_03.md`、`docs/pm/delegation_log/`。他ファイル・SSOT・git操作なし。LLM呼出なし。**
作業方式: Write/Edit 1回40行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: ¥0集計準備。禁止: 有料API/SSOT編集/Status判定の自動化(基準充足の事実のみ出力、判定はFable)。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_03.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> 合格基準: HC-012 3/3維持/A5-0 3/3維持/D61 2/3以上/held-out重大例 平均2/3以上かつ全例最低1/3以上/正常43件+held-out正常例 不要な重大判定0/不要Rewrite見込み0件/run/新たな重大見逃し0/前回解消した誤爆3件を再発させない。
> 報告: 構成X/Yの結果/HC-012/A5-0/D61/held-out重大例/正常文誤爆/前回誤爆3件/不要Rewrite見込み/新規重大見逃し/AI揺れ/追加費用/run/Trial実費/前回Trialとの差。

## 入力契約(委任_01/02の出力。未完成のためこの契約で実装し、selftestはTRIAL-02結果を変換して行う)
results jsonl record(v2 keys+): `id, fact_id, label, origin, heldout(bool), expected_compare, acceptable_compare, expected_event_subject, expected_phase(任意), repeats: [{rep, selected_subject, article_phase, matched_event_phase, ledger_state, article_state, compare, fallback_used, fallback_calls, fallback_details}], final_compare_rep0, final_compares, cost_jpy`。summary: `n_items, n_calls, cost_jpy, fallback_calls, fallback_cost_jpy, by_label`。`ledger_cache.json`: `{fact_id: {rep1: [{subject_x,result_state,phase,quote}],...}}`。正解: `ledger_truth_03.json`(events[*].phase付き)、`testset_03.json`(heldout flag)。母集団: `../open233_directional_misread_trial_01/population_01.json`。前回: `../open233_directional_misread_trial_02/trial_summary_02.json`+`run/results_merged.jsonl`。

## 作業内容
A. `aggregate_trial_03.py --results-x <X merged> --results-y <Y merged> --ledger-cache --truth --testset --population --prev-summary --prev-results --out <dir>` → `trial_summary_03.{json,md}`。構成X/Yそれぞれと比較表で: (1)HC-012(G-01) k/3 (2)A5-0(G-02) k/3 (3)D61(G-03) k/3 (4)held-out重大例(H-G1〜4)各k/3・平均・最小 (5)正常文(既存label忠実・非該当=43件相当)+held-out正常例(H-F1〜6)のrep0 REVERSED件数(0が基準)・全repeat率 (6)不要Rewrite見込み=誤重大判定率×単位数(3水準) (7)新たな重大見逃し=前回(TRIAL-02)でREVERSED(rep0)だったgold/人工反転が今回REVERSED以外(id一覧)。Ledger事象リスト外の人工反転(outside_event_list)は参考集計 (8)前回誤爆3件(F-09/F-10/F-19)の3反復compare、再発=REVERSEDが1つでもあれば (9)**合格基準表8行**: 充足/未達+根拠数値、X/Y別 (10)AI揺れ: repeat 3項目で3反復のcompareが全一致した割合、phase判定の反復一致率 (11)フォールバック: 発動件数・call数・費用、発動したidと結果 (12)phase: Ledger側phase精度(truth対応付け)、記事側phase分布と期待phase一致率(expected_phaseがある項目) (13)費用: 実費、1 callあたり、1 runあたり追加¥(3水準、フォールバック率を加味) (14)前回比(TRIAL-02 blind): gold/誤爆/UNCLEAR/費用の差分表、項目単位の変化id一覧(`regression_vs_trial02.py`)。
B. `selftest/adapt_trial02.py`: TRIAL-02の`run/results_merged.jsonl`を本契約へ変換(phase/fallbackは空)しaggregateが完走、数値がTRIAL-02と整合(HC-012 3/3、D61 0/3、誤爆0)することを確認。testset_03/ledger_truth_03未完成なら最小ダミーで通し記録。
C. `docs/pm/RESULT_PACKET_T03_03.md`: 使い方、selftest結果、T-0。

## 事前指定Read一覧
1. `er052_output/open233_directional_misread_trial_02/aggregate_trial_02.py`: 全文(流用元)。
2. `er052_output/open233_directional_misread_trial_02/trial_summary_02.json`: 先頭40行。
3. `er052_output/open233_directional_misread_trial_01/population_01.json`: 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順
`run/results_merged.jsonl`(trial_02)は1行目のみPythonでkeys確認。新規ファイルのため追記位置なし。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_03.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_03.md_check.json`
2. selftest: `.venv\Scripts\python.exe er052_output\open233_directional_misread_trial_03\selftest\adapt_trial02.py` → `.venv\Scripts\python.exe er052_output\open233_directional_misread_trial_03\aggregate_trial_03.py ... --out er052_output\open233_directional_misread_trial_03\selftest\out`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_T03_03.md`。最終報告6行以内。
