# 結果: OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_03(M1〜M3 Trial実装と既存データ検証、2026-10-08)

Status: MEASURED(Trial)。Production変更なし(全フラグ既定OFF)、CURRENT_SPEC.md・`OPEN233_APPROVED_FLOW_SWITCHES` 値は無変更。実費 ¥56.849(上限¥60以内)。所要約40分。

## 変更ファイルと差分要点
- `er003_v1_en_direct_vfl_01_generate.py`(M2): `OPEN243_M2=1` のとき `run_deviation_check()` のprompt文言のみ差し替え。D1 changed_actor説明拡張、許容範囲リストに1項目(一般に想像できる補足・指標の一般化は新規主張を伴わない限り非指摘、因果は対象外と明記)、D3 `ORIGIN_INSTRUCTION_TEMPLATE_M2`。severity規則・10フラグ・schema不変。
- `er003_v1_n3_01_advanced_adaptation_generate.py`(M1): `generate_family_x_in_one_line()` に `ja_text/ledger_text/must_fix` 任意引数(未指定=従来prompt・戻り値と完全同一)、`FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1`(要件1行+JA/Ledger入力欄)。
- `er012_e_family_entertainment_two_level_runner_01.py`(M1/G3): `open243_majors_only_in_summary()`・`open243_m1_summary_only_retry()`(要約だけ最大2回再生成)・`open243_g3_record_translation_minor()`、Advanced枝の分岐(`OPEN243_M1=1` かつ要約のみMAJORのときだけ)。既存の全体再生成1回・ja_source→JA再確認STOP・段落数retry・再生成後MAJORならSTOPは不変。
- `er052_open233_stage1_reclassify_01.py`(M3/G3): `OPEN233_RECLASSIFY_PROTECT_FLAGS`(指定フラグtrueのmodel候補を再分類対象から外す)、`OPEN243_G3_TELEMETRY_PATH`(除外されたフラグ付き候補をjsonl記録)。
- 新規: `er052_open243_m123_trial_test_01.py`(単体テスト16件)、`er052_output/open243_translation_ng_analysis_01/trial_m123_01/`(DESIGN_M123.md=プロンプト変更前後の全文、RESULTS_M123.md、検証スクリプト、v1/v2/v3の生結果、spend_ledger.jsonl、logs、regression)。
- SSOT: REPORT §110、DECISION_LOG(索引+同名節、ユーザー回答3件逐語・Go)、OPEN_ITEMS OPEN-243(2,775字)、docs/pm/REPORT_LEDGER.md。
- プロンプト変更前後の全文: `trial_m123_01/DESIGN_M123.md` §5(自動生成、`_prompts_before_after.md`)。

## 結果(各 n=1、事実のみ)
| 検証 | 指標 | 旧/従来 | 新 |
|---|---|---|---|
| V1 | 要約MAJOR14世代 前回指摘の解消 | 6/14 | 14/14 |
| V1 | 再検査まで通過 | 6/14 | 12/14(未通過=G03・G08、変更していない本文の1文が新規MAJOR) |
| V1 | 要約STOP相当(未解消MAJOR) | 8 | 2 |
| V2 | 陽性26: 検出 / translation / ja_source | 11 / 7 / 4 | 8 / 6 / 2 |
| V2 | 主体型7: changed_actor=true | 2 | 3 |
| V2 | 重大 EV-25 / EV-28 | 未検出 / MAJOR | 未検出 / MAJOR |
| V2 | 許容文 G09「so」 / G02「users」・G06「oil prices」 / 同型 G07・G12 | MAJOR / 指摘なし / MAJOR | MAJOR / 指摘なし / 該当なし |
| V2 | 旧再実行40記事 MAJOR総数 / MAJOR記事 | 23 / 16 | 22 / 16 |
| V2 | 新の全59記事 | 旧19記事は未再実行で比較不能 | MAJOR 33 / 24記事 |
| V3 | EV-25 Stage 2(3回再生) | 実runは除外 | BLOCKING 1・ACCEPTABLE 2 |
| V3 | 保護17件(旧除外・最終EN残存) | - | BLOCKING 1(EV-25)・QUALITY 3・ACCEPTABLE 13 |
| V3 | ledger整合文の誤書換え | - | 0件(cycle1のStage 2で打切り、BLOCKING=書換え対象で計数) |
- 判定材料(依頼どおり): M1 要約STOP相当 8→2。M2 陽性26中translation判定 旧7→新6、主体型でchanged_actor=true 旧2→新3、許容3文は「so」のみMAJOR(仕様どおり)・他2文は旧でも出ず確認不能、旧再実行40記事のMAJOR 23→22。M3 EV-25は3回中1回BLOCKING、保護19件のうち再生した17件の内訳は上記、誤書換え0。
- 詳細: `trial_m123_01/RESULTS_M123.md`(V1表・V2事象別・V3 claim別)。

## 実費(トークン実測 x 登録単価 gpt-6-luna、USD/JPY=160)
V1 ¥13.261(要約生成+検査)/V2 ¥28.380(新 ¥16.092、旧再実行 ¥12.288)/V3 ¥15.209(12回、再分類+Stage 2+第2意見)= ¥56.849。astraは不使用。内訳は `trial_m123_01/spend_ledger.jsonl`。

## 回帰テスト(フラグOFF)
新規16件+既存 er012_e runner 23、er003_v1_en_direct_vfl 9、er019 new_structure 31、er052 checker_floor_prod_wiring 59、er052 self_recovery_flow_runner 720、er006 pricing_coverage 7、er006 gpt6_wiring 9、er019 ja_recheck_retry 9・production_runner 2、er045 19 全PASS。ログ `trial_m123_01/regression/flags_off_final.log`。

## check_delegation_prompt
FAIL(標準フォーマット外: 性質/事前指定Read一覧/Grep一覧/実行コマンド全文セクションと固定ブロックラベル E-1/D-1/G-1/F-1 欠落)。指示どおり続行。結果 `2026-10-08_OPEN-243-TRANSLATION-NG-ANALYSIS-01_03.md_check.json`。

## 未解決点・逸脱
- 費用が事前見込み(約¥30)の約1.9倍(¥56.85)。上限¥60以内だが残り¥3.15。原因: EN検査1callが約¥0.27(推論トークン大)、要約生成が平均¥0.118。
- V2 の旧再実行は64中45(旧19記事分は予算上限のため未実施)。保存済み最終check(COMPLIANT)は選択バイアスで比較不可。
- 各条件n=1、EN検査・Stage 2は非決定的(旧検査の再実行だけで40記事中16記事にMAJOR)。V1の未通過2件も本文側の検査の揺れ。
- M1はAdvanced(Family X)枝のみ。Standard(A2)枝は未実装。V3はcycle 1のStage 2まで(Rewrite以降は未再生)。open238 replay 2件(同一入力)はT04で代表。
- V1の「主体・範囲の保持」は人手(LLM1名)目視。再生成要約は台帳の語に寄る傾向、G06は焦点がBrent先物の値動きへ移る。
- 新規仕様候補・追加判断事項: なし(採否はFable・ユーザー判断、Opus条件A/Cの要否はFable判断)。

## commit / raw URL
commit 2cf161ab682a11ea68bfa752e82fff8a418ea774(origin/main push済み)。主な raw URL(https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>):
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open243_translation_ng_analysis_01/trial_m123_01/DESIGN_M123.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_output/open243_translation_ng_analysis_01/trial_m123_01/RESULTS_M123.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er003_v1_n3_01_advanced_adaptation_generate.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er012_e_family_entertainment_two_level_runner_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er003_v1_en_direct_vfl_01_generate.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_open233_stage1_reclassify_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er052_open243_m123_trial_test_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/delegation_log/2026-10-08_OPEN-243-TRANSLATION-NG-ANALYSIS-01_03_result.md
