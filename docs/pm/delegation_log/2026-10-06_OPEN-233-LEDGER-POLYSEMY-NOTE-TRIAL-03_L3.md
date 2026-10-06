# OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03 委任_L3(簡略保存)
## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03(委任_L3: 最終ループ=仮説H5〜H7に基づくパターンB3の設計、5台帳+holdout2の要素Trial、有料上限¥60、評価)。
## 性質/到達上限Status/禁止事項
DEV改修+prompt設計+要素Trial+評価。到達上限は比較表と所見(成立判定はFable)。禁止: Production file変更/SSOT編集/git/対象fact_id・5テーマ固有語のprompt混入/試行錯誤再実行(1回)/件数目安のprompt記載/評価sheet上書き。
## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 上限¥60、実費¥34.01。D-1: runs/cost_l3.jsonに集計。G-1/F-1該当なし。T-0: 本ファイル+check。T-2: TTSなし。T-3: 対象外。
## 事前指定Read一覧
docs/pm/polysemy_trial_03/L2_element_trial_result.md、eval/B2_twostage_hint_content_label_sheet.md、patterns/B2_twostage_hint/、tools/gen_notes_p03.py。
## 事前指定Grep一覧+追記位置・更新位置の手順
H5 stage1.5圧縮判定役(入力=fact_id+compressed_claim+Rのみ、high通過)、H6 stage1を2回実行して和集合、H7 max_chars=120。patterns/B3_twostage_gateを新設、ハーネスにstage1.5/repeats実装、衛生チェックPASS後に1回実行・評価。
## 実行コマンド全文
.venv/Scripts/python.exe -m pytest er052_output/open233_polysemy_trial_03/tests/test_p03_tools.py -q
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/prompt_hygiene_p03.py --patterns er052_output/open233_polysemy_trial_03/patterns --forbidden er052_output/open233_polysemy_trial_03/eval/forbidden_terms.txt
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/run_patterns_p03.py --patterns B3_twostage_gate --slugs meta,hormuz,space_weapons,sewer,ai_control,A02,small_bag --parallel 3 --budget-jpy-per-call 5 --web-search none
python er052_output/open233_polysemy_trial_03/eval/l3_labels.py
## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目)
H5〜H7実装・test・衛生、比較表要約、基準照合、stage1一致率と和集合効果、1.5却下内訳とFN、実費・累計、所見2行、T-0結果。
