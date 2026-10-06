# OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03 委任_L2(簡略保存)
## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03(委任_L2: ループ2=原因仮説H1〜H4に基づくパターンB2/B2nの設計、5台帳+holdout2の要素Trial、有料上限¥70、評価)。
## 性質/到達上限Status/禁止事項
DEV改修+prompt設計+要素Trial実行+評価。到達上限は比較表と所見(成立判定はFable)。禁止: Production変更/SSOT編集/git/対象fact_id・5テーマ固有語のprompt混入/prompt試行錯誤再実行/件数目安・上限のprompt記載。
## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 上限¥70、実費¥50.70。D-1: runs/cost_l2.jsonに集計。G-1/F-1該当なし。T-0: 本ファイル+check。T-2: TTSなし。T-3: 対象外。
## 事前指定Read一覧
docs/pm/polysemy_trial_03/L1_element_trial_result.md、eval/B_twostage_content_label_sheet.md、patterns/B_twostage/、tools/gen_notes_p03.py。
## 事前指定Grep一覧+追記位置・更新位置の手順
H1接頭辞空白正規化、H2 self_check緩和(警告のみ)、H3 R最大2列挙+B2のみ既存notesをstage2へ渡す、H4合成正例追加。patterns/B2_twostage_hint・B2n_twostage_nohintを新設、衛生チェックPASS後に実行・評価。
## 実行コマンド全文
.venv/Scripts/python.exe -m pytest er052_output/open233_polysemy_trial_03/tests/test_p03_tools.py -q
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/prompt_hygiene_p03.py --patterns er052_output/open233_polysemy_trial_03/patterns --forbidden er052_output/open233_polysemy_trial_03/eval/forbidden_terms.txt
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/run_patterns_p03.py --patterns B2_twostage_hint,B2n_twostage_nohint --slugs meta,hormuz,space_weapons,sewer,ai_control,A02,small_bag --parallel 3 --budget-jpy-per-call 5 --web-search none
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/eval_notes_p03.py --patterns B_twostage,B2_twostage_hint,B2n_twostage_nohint --out er052_output/open233_polysemy_trial_03/eval/l2_eval_table.md
## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目)
H1〜H4実装・test・衛生、比較表要約、基準照合、B2/B2n差、FN残、実費、所見2行、T-0結果。
