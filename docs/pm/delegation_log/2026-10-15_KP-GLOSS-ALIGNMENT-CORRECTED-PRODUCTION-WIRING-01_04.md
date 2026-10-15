# KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_04 (2026-10-15) 委任文(要約保存)

## 管理ID
KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01(KGCPW)委任_04。Family Zの未確認3点(Z正式経路でのalign発火[注入]・Z正式CLIのHR停止・Z E2E完成)を正式CLIで埋める。前委任_03(commit e46821295)の10条件表の部分確認(条件1(Z)/4/6(Z))の解消が目的。並行: Day3 委任_F3(SSOT6本等編集中)、委任_G。本委任はSSOT・ACTIVE_TASK・REPORT_LEDGER・台帳を編集しない(文案のみ)。

## QDC記録(11-6)
目的: 10条件のZ側1/4/6を確認済みに。試行: 委任_03はMelos run_e2e_02 copyで旧narrator様式guardで課金前停止。今回は新規run。費用見積JPY60〜80、当日累計約20/1,000。

## 性質/到達上限Status/禁止事項
- 性質: Production正式経路のruntime evidence(Family Z)。到達上限: Z_EVIDENCE_COMPLETE_PENDING_FABLE_JUDGMENT。PRODUCTION_WIREDは宣言しない。
- Opus独立技術レビューGate: 条件C実施済み。
- 費用上限JPY80(Guardrail)。T-3: 到達=自動STOPではなく暴走疑い時のみSTOP。各stageに--approved-budget-jpyを明示。
- 禁止: Productionコード・Prompt・flag・test・Melos原本(run_e2e_01/02)・Coffee完成版・user_test変更禁止。既存guard回避削除禁止(run_kgcpw_z_e5_a2_01/b1b_01のSTOPは削除せず再使用しない)。同一run dirへの短時間連続起動禁止(RESTART_STORM)。Batch不使用、TTS_EXECUTION_MODE=STANDARD明示。HR queue/Lock不使用。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止。
- 時間見込み: 約2.5h。直列。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3: 前委任と同一(T-2: 全clip新規生成は意図、見積100超は実行前STOP)。

## ユーザー指示(原文)
「Family X／Zの正式Production runnerでの実LLM発火確認」「異常時のHR例外、TTS・英語解説・assemble・公開ページの完成禁止」「HR解決後の再開」「Production正式経路でのE2E完成確認」「異常経路は、必要に応じて制御された失敗注入を利用すること。実LLMが自然に2回失敗するまで無益なTrialを繰り返さない。mock／失敗注入と実LLM evidenceは区別して報告すること。」

## KPI provenance欄
Z新規run=fresh+production_formal_path。HR停止=synthetic(失敗注入)+production_formal_path。E2E自己確認=Yes。

## Opus台帳更新
本体編集せず文案のみ(OF-KGDC-01/02/03・OF-KGCPW-08/09のZ側evidence追記)。

## 事前指定Read一覧
RESULT_PACKET_KGCPW3.md、VALIDATION_WIRING_03.md、er026 runner(Grep)、COST_LEDGER_MELOS_01.md、run_e2e_02構成、harness_kgcpw_01.py、KP_GLOSS_ALIGNMENT_HR_RESOLVE_01.md、PM_GOVERNANCE 26-2/26-5。

## 事前指定Grep+手順
run dir: er026_output/family_z_production_e2e_01/melos/run_kgcpw_z_e2e_01/(新規。writer段成果物のみcopy可=ensure_stage判定)。手順: (1)STOP確認 (2)見積 (3)--stage kp (4)Z HR停止(注入)+正式CLI tts_a2でFamilyZE2EStop rc=2 API0 (5)resolve_gloss→kp再開 (6)kp_expl_b1b→tts_a2→tts_b1b→provision_shell→gate→assemble→pages→page_verify --local、stage間cooldown (7)完成物確認 (8)summary。evidence: .../gloss_alignment_production_wiring_01/evidence/E11_z_e2e/。成果物: VALIDATION_WIRING_04.md(§0〜§5)。

## 実行コマンド全文
(.venv\Scripts\python.exe、TTS_EXECUTION_MODE=STANDARD) T-0 check、stop_scope_check_01.py、er026 --story melos --slug melos --run run_kgcpw_z_e2e_01 --mode real --stage <stage> --approved-budget-jpy <n>、harness_kgcpw_01.py --scenario z_a2 --align-mode fail2 ...、git status --porcelain / log。

## SSOT追記文
編集しない。委任_05用文案をRESULT_PACKETに。

## Git
SSOT編集権なし。明示add: VALIDATION_WIRING_04.md、evidence/E11_z_e2e/要約、(変更時)harness、delegation_log/..._04.md(+_check.json)。コミットメッセージ: 「KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_04: Family Z 正式CLI runtime evidence(...)。PRODUCTION_WIRED判定はFable、費用JPY<実測>」。push origin/main。

## 報告(RESULT_PACKET項目)
docs/pm/RESULT_PACKET_KGCPW4.md へ(1)〜(11)。
