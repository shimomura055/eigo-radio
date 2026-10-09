# 委任_10 結果 FACTLOCK-ASTRA-E2E-TRIAL-01(2026-10-09) Status=PARTIAL(9/10テーマ統合・配線・G0実照合PASS、inbound_tourism未統合、API支出¥0)

## 1. 成果物・commit・テスト
- commit: 16d00922ec2de3c8c9a134d4c047023313443b76(push済み)。raw URLは本文末尾。
- 修正: `er052_output/factlock_astra_e2e_trial_01/b3_annotation_check_01.py`(b_ledger_mapping)、`b3_annotation_check_01_test.py`(41件OK=従来40+1、`test_non_verified...`をPENDING/NOT_VERIFIED/REJECTED=FAILに拡張、`test_ambiguous_ledger_id_in_facts_warns_with_flag`新設)、`annotation/make_final_01.py`(B3 v2テーマ選択・JSON text行区切りfallback・final_json_check.jsonを累積)。`annotation/audit_strict_01_test.py` ALL_PASS。
- 新規: `annotation/wire_inputs_01.py`、`annotation/make_summary_10.py`、`annotation/prefix_scripts/b3_annotation_check_01.pre_delegation10.py`(修正前)、`inputs/<9テーマ>/`、`inputs/WIRING_SHA256.json`、`g0_real_annotation_01/`、`annotation/out/merged/{semiconductor_earnings,hormuz,streaming_price}/`、`annotation/final/{同3}/`。
- 更新: `annotation/ANNOTATION_SUMMARY_01.md`(10テーマ表・(c)(d)(e)・Bash使用者一覧。旧版は `_prev09.md`)、`annotation/RUN_ANNOTATION.md` 8節、`stage_r/SPEC_V2_CLARIFICATIONS.md`(c)-(f)、DECISION_LOG.md 1節、REPORT_LEDGER.md 1行。
- 証跡: `docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_10_check.json`。

## 2. (c)反映の差分と検査結果の変化
- 差分: `ledger[i]["status"]` が AMBIGUOUS のとき problems でなく warnings(「事実N: 台帳ID X は AMBIGUOUS (ambiguous_fact)」)+戻り値 `ambiguous_fact: {事実N:[ID]}`。他status(NOT_VERIFIED/REJECTED/PENDING等)は従来どおりFAIL。`AMBIGUOUS_FACT_MAP.json` と整合(semiconductor F1、streaming F01/F07、inbound F06[選択分])。
- semiconductor_earnings: 同一返答でA・Bとも FAIL(b)->PASS(+AMBIG F1)。統合PASS(事実1、中核3/周辺4、cap_dropped4、分割一致率1.00、中核Jaccard1.00、flags空)。
- streaming_price(再注記・B3 v2): A・Bとも単独PASS(+AMBIG F01,F07)、統合PASS(事実1、4/5、cap3、一致1.00/1.00)。
- hormuz(再注記・B3 v2): 単独PASS、統合PASS(事実4、4/4、cap4、一致1.00/1.00)。
- inbound_tourism: bはPASS(+AMBIG F06)になったが c_numbers が実FAIL(3節)。

## 3. inputs配線とG0実照合(runner `run --g0-only`、実注記、API/stageなし。`g0_real_annotation_01/g0_summary.json`)
全9テーマPASS: meta, byd_recall, central_bank_mortgage, openai_copyright, small_bag, space_weapons, semiconductor_earnings, hormuz, streaming_price(依頼の7+4節の2)。
- 注記版JSON整合検査は今回スキップなし(`annotated_json_vs_original` と `b3_annotation_full_check`=PASS)。置いたのは `selected_brief_annotated.md` / `fact_selection_evidence_annotated.json`(runnerの実ファイル名。依頼文の「注記版 fact_selection_evidence.json」に相当)/ `annotation.json`。
- hormuz・streaming_priceはB3 v2基準のため、inputsに v2 の `selected_brief.md`・`fact_selection_evidence.json`と `input_manifest.json`(FROZEN_INPUTS_SHA256.json の storyline_b3_v2 のLF sha)も配置(runner無改修。旧腕のB3もv2になる点は要確認)。台帳はstage_rを参照(manifest照合PASS)。
- 7テーマの `selected_fact_brief_text` 注記版JSONは make_final の規則(md側と同一)で生成。v2 evidence形式(storyline+改行区切りの箇条書き、空行なし)は行区切りfallbackを追加。openai_copyright/small_bagでmd側タグ数>JSON側(7 vs 6, 8 vs 7)なのは、Storyline内の印がJSONのfact textに含まれないため(従来どおり、整合検査はPASS)。

## 4. 残り3テーマの状態
- 再注記A/Bの reply.md は6本とも揃っていた(hormuz/streaming 09:20:22付近、inbound 09:20:45付近。以後mtime不変を確認)。hormuz・streaming_priceは上記のとおり完了。
- 重要: 新しい注記は B3 v2(`stage_r/<slug>/storyline_b3_v2/`)に対するもの。v1 briefで検査するとsha不一致でFAILになるため、検査・統合・finalはv2 briefで実施した(RUN_ANNOTATION 8節に手順)。
- inbound_tourism(v1 brief): A・B単独 FAIL(c_numbers)。A=`8`の分類漏れ(Storyline「8月単月」)、B=概念重複2件(`8月`が`2019年8月`/`2025年8月`に包含)+`2026`分類漏れ。加えて検査script側に欠陥候補: `ID_RE` が連字符なしID(`F01`)を除外できず、本文括弧「（F01）」内の数字(01,02,03,06)を分類漏れと誤検出。スクラッチ上でIDマスクを直して再検査してもA(`8`)・B(概念重複+`2026`)の実FAILは残る。統合せず・手直しせず。再委任は既に2回注記済みのため行わない(§6)。
- 6本の新transcriptは未保存のため監査未実施(旧v1ラウンドのtranscript.jsonlが残置)。手順はRUN_ANNOTATION 8節。`out/B/streaming_price/STOP_reason.txt` は旧ラウンド由来のため `STOP_reason_v1_attempt.txt` へ改名。

## 5. 未確認・Fable判断要
1. inbound_tourism: (i)ID_REマスク修正(直しても実FAIL残存)、(ii)除外して9テーマ(旧4+新5)で進行、(iii)プロンプト/仕様修正後に再実行(静かな差替禁止)。なおAMBIG(c)を覆す場合は inbound/semiconductor/streaming の3テーマ除外。
2. hormuz・streaming_priceの旧腕(old arm)の原B3もv2になる(旧4凍結B3ではない)。hormuz旧腕=B3 v2でよいか。
3. 呼び出し側によるtranscript保存と6本の監査(Bash使用の有無)。(d)による採用はv1ラウンド9本分のみ。
4. 実API経路は未実行。runner本体は無改修(31テスト再実行せず)。
5. `final_json_check.json` は累積方式へ変更(過去分の個別記録は旧commit)。

## 6. 所要時間・API支出
- 約45分。API支出 ¥0(生成呼び出しなし、既存スクリプト/テストのみ)。

## raw URL
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/b3_annotation_check_01.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/b3_annotation_check_01_test.py
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/annotation/ANNOTATION_SUMMARY_01.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/annotation/RUN_ANNOTATION.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/stage_r/SPEC_V2_CLARIFICATIONS.md
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/factlock_astra_e2e_trial_01/g0_real_annotation_01/g0_summary.json
https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-09_FACTLOCK-ASTRA-E2E-TRIAL-01_10_result.md
