## 管理ID
OPEN-233-LEDGER-CLARITY-P-TRIAL-01(委任_E2: 評価③真の重大NG(HC-012 Rollback型必須)+①Checker副作用観測、¥0)

## 性質/到達上限Status/禁止事項
性質: 評価(read-only+評価ファイル1本)。到達上限: ラベル表と所見(最終判定はFable)。禁止: 有料API/記事・台帳の変更/Production変更/SSOT編集/git/再実行/Checker結果をS1・precheck4種除外等の承認根拠に使う記述。並行委任E1/E3の出力(eval/E1_*、eval/E3_*)には触らない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1: 該当なし。T-0: 簡略保存(本ファイル)+checker。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
③真の重大NG: HC-012のRollback型を必須確認。従来台帳で発生した意味の逆転・重大Fact誤りが新台帳で発生しないか、Rollback以外の既知重大NGで悪化がないか。生成記事そのものに真の重大NGがあるかを評価。①Checker副作用: 従来OKだった記事が不自然にNG扱いされていないか、不要NGが増えていないか。候補数削減は成功条件にしない。

## 事前指定Read一覧
After: er052_output/open233_ledger_clarity_p_trial_01/after_pprime_01/ の台帳・B3 brief・JA R0/R2・b1b記事。After Checker: checker_after_01/runs/meta_run03_advanced.json。Before: docs/pm/ledger_clarity_p_trial/00c_before_evidence.md、er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json。runner L9817-9900。er052_output/open233_prod_e2e_01/labeling_guide_01.md。

## 事前指定Grep一覧+追記位置・更新位置の手順
1. HC-012型3値ラベルを各段で逐語引用。2. After EN全文を台帳基準で走査。3. JA R0/R2走査。4. Checker副作用(候補数・blocking・Rewrite・human_review・floor・S1結果、non-blocking各1行、不要NG件数)。5. 出力 after_pprime_01/eval/E2_critical_ng_checker.md(90行以内)。

## 実行コマンド全文
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_E2.md --json-out docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_E2_check.json`

## SSOT追記文
なし。

## Git
なし。

## 報告
RESULT_PACKET項目12行以内: HC-012型各段ラベル、EN重大/軽微件数、gold相当誤り、JA段誤読、Checker比較、副作用所見、T-0結果。
