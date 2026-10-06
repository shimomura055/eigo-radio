# OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03 委任_05b (逐語保存)

## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03(委任_05b: resume対応→未完分の追加実行(累計上限¥8厳守、残¥1.53)→merge(partial許容)→集計)。書込先: er052_open233_directional_trial_03.py(resume・encoding・partial mergeの最小修正のみ。判定ロジック・prompt不変)、同test、er052_output/open233_directional_misread_trial_03/配下、docs/pm/RESULT_PACKET_T03_05B.md、docs/pm/delegation_log/。testset/正解は凍結。Production code・SSOT・git操作なし。

## 性質/到達上限Status/禁止事項
性質: 有料限定Trialの残分実行(累計上限¥8、既に¥6.471消費、残¥1.53が絶対上限)。到達上限: 集計完了。禁止: 予算引き上げ/残11 run/Production変更/testset・正解変更/判定ロジック・prompt変更/既存結果の再実行/TRIAL-04自動移行。

## 固定ブロック
E-1, D-1, G-1, F-1, T-0, T-1, T-2, T-3(有料: 累計¥8厳守)。

## Fable固定方針
優先順位: (1)構成Y shard2未完分 (2)構成X shard2 held-out重大4件 (3)構成X shard2 N-01〜N-11。resume/partial merge/encoding最小修正。

## 作業内容
A. script最小修正+unit test。B. 追加実行(直列)。C. merge。D. 集計。E. RESULT_PACKET_T03_05B.md。

## 報告
最終報告12行以内。

## 事前指定Read一覧
1. docs/pm/RESULT_PACKET_T03_05.md 全文
2. er052_output/open233_directional_misread_trial_03/estimate_03.md 全文

## 事前指定Grep一覧+追記位置・更新位置の手順
er052_open233_directional_trial_03.py: Grep def main|def merge|results_shard|run_meta|print( -> 範囲Read -> 最小Edit。aggregate_trial_03.py: Grep missing|not_executed|def load_results -> 必要なら最小Edit。

## 実行コマンド全文
1. .venv/Scripts/python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_05b.md --json-out docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_05b.md_check.json
2. .venv/Scripts/python.exe -m unittest er052_open233_directional_trial_03_test
3. 追加実行・merge・集計(B〜D)

## SSOT追記文
なし

## Git
なし
