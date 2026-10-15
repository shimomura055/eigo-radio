# 委任_03 KP-GLOSS-ALIGNMENT-PRODUCTION-01 (2026-10-15)

## 管理ID
KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_03(既定OFFのFamily Z正式runner KP段を実LLMで通すruntime evidence追加+corrected modeもflag必須化[kill switch一元化]+SSOT追記)。前委任_02=commit c21cce27a(X実LLM evidence取得済み、Zはmock runnerの内蔵ダミーkp_fnのため再整合呼出箇所を通っておらず、Fableが不足と判定)。

## 性質/上限Status/禁止
性質: Production安全措置の実証補強+Trial経路の最小是正。到達上限Status: 「Z実LLM evidence取得済み・flag一元化済み・PRODUCTION_WIRED判定待ち(判定はFable)」。Opus Gate非該当。費用上限JPY3(Guardrail、Z KP段見込み1〜2円)。TTS実行禁止。
禁止: Melos正式run dir(run_e2e_01/run_e2e_02)への書込・再生成・Production反映、STOP_NOTICE/STOP/STOP_ALL編集、承認済みPrompt/Rule7/Gate/Lock変更、legacy挙動変更、gloss再整合ロジック変更(flag必須化1点除く)、git add -A/-f/amend/rebase/force push/stash/clean/reset --hard/checkout -f、.env読み書き。

## 固定ブロック
E-1 同一ファイル再読しない/D-1 Grep→範囲Read/G-1 git出力最小化/F-1 transcript退避不要/T-0 本ファイル保存+check_delegation_prompt実行/T-2 TTS禁止(TTS_EXECUTION_MODE=STANDARD明示、KP段で停止)/T-3 費用上限JPY3。

## ユーザー指示(原文)
「未承認のgloss再整合工程は、Productionで既定OFFにする方針を正式承認する。」「DEV／Trialでは明示的にONにして検証できる状態を維持する。」「OFF時に追加API呼出・gloss変更が発生しないことを確認する。」「Family X／Zを含む正式Production経路で、未承認工程が誤発火しないことを確認する。」「必要なRegression、runtime evidence、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS、Git反映まで確認する。」「既定OFFの安全措置のみAPPROVED_FOR_PRODUCTION。実証が揃うまでPRODUCTION_WIREDとはしない。」
Fable判定: 委任_02のZ evidence(mock runner)は不足。Zの正式KP関数(run_kp_with_outer_retry等)を実LLMで通し、flag未設定で再整合が呼ばれないことを実証。Python引数gloss_alignment_mode="corrected"だけで動く経路を塞ぎ、flag(EIGO_KP_GLOSS_ALIGNMENT=1)を唯一のkill switchに。Trial scriptはenv明示を追加。

## 事前指定Read一覧
VALIDATION_OFF_01.md全文、runner Grep、evidence_12A起動ログ先頭、scaffold/gloss_alignment/test各Grep範囲、tools/stop_scope_check_01.py 1-40、SSOT各Grep(原文は委任文参照)。

## 事前指定Grep一覧+追記位置・更新位置の手順
1. rg -n "gloss_alignment_mode|enabled=True" (er003_v1_n3_01_scaffold_generate.py er003_key_words_gloss_alignment.py er026 runner er019 runner)でcorrected分岐のenabled=True直書きをga.flag_enabled()結果へ。flag OFFならcorrectedでもstatus=DISABLED・API0・artifact不変。DefaultOffIsolationにtest追加。
2. Trial script(er071_..._trial.py/_t3_mock.py)先頭でos.environ["EIGO_KP_GLOSS_ALIGNMENT"]="1"を明示設定しログ「Trial: gloss alignment explicitly ON」。T3 mock再実行27/27 PASS。
3. Z evidence: Melos run dirのコピー(er071_output/m2p0_n01_production_wiring_01/gloss_alignment_default_off_01/evidence_z_real/run_off_z_01/)でKP段のkp_fnをProduction既定(実LLM)、他mockでstage_kpまで。事前にtools/stop_scope_check_01.pyで対象外確認。env未設定。確認: rc、KP成果物、kp_gloss_alignmentタグ0件、artifact0件、provenance legacy/flag False。不可能ならSTOP報告。
更新: VALIDATION_OFF_01.mdに§6 Family Z実LLM evidence/§7 flag一元化を追記。SSOT: OPEN-356行1文、DECISION_LOG委任_02節追記、OF-235備考、REPORT_LEDGER1行、CURRENT_SPEC1文。ACTIVE_TASK更新。

## 実行コマンド全文
pytest er003_test_key_words_gloss_alignment.py -q / er071_gloss_alignment_correction_01_t3_mock.py --out .../trial_t3_rerun_01/ --tts-execution-mode STANDARD --mock-all / stop_scope_check_01.py / Z evidence起動(TTS_EXECUTION_MODE=STANDARD, EIGO_KP_GLOSS_ALIGNMENT未設定) / run_project_regression.py --pattern er003*, er026*, er019*(新規failure 0)。素のpython禁止。

## SSOT追記文
- OPEN-356: 「2026-10-15 委任_03: Family Z正式runnerのKP段(実LLM、flag未設定)で再整合未呼出を実証(JPY<実績>)。mode=correctedでもflag明示ONが無ければ実行しないよう一元化。」
- DECISION_LOG: 「委任_03: Z実LLM evidence(commit <hash>)、flagを唯一のkill switchへ。」
- CURRENT_SPEC: 「gloss再整合はEIGO_KP_GLOSS_ALIGNMENT=1の明示ONが必須(mode指定のみでは実行されない)。」

## Git
明示add: 変更.py、VALIDATION_OFF_01.md、evidence_z_real配下md/json/log、trial_t3_rerun_01のjson、SSOT、delegation_log2ファイル。ACTIVE_TASK*/RESULT_PACKET*はadd禁止。コミット: `KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_03: 既定OFFのFamily Z正式runner KP段 実LLM evidence(flag未設定で再整合未呼出)+flagを唯一のkill switchへ一元化(mode=correctedもflag必須)+T3再確認+SSOT` trailer Managed-ID: KP-GLOSS-ALIGNMENT-PRODUCTION-01。git push origin main。

## 報告
docs/pm/RESULT_PACKET_KGA3.md(25行以内)。

## Opus台帳更新
OF-235: 備考に委任_03でZ実LLM evidence追加、flagを唯一のkill switchへ一元化。
