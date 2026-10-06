# OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03 委任_L1r(簡略保存)
## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-03(委任_L1r: ハーネスをパターン契約へ整合し、A/B/C×5台帳+holdout2の要素Trialを実行、有料上限¥80)。
## 性質/到達上限Status/禁止事項
DEVツール整合+要素Trial実行(有料)+評価。到達上限は評価表と所見。禁止: Production変更/SSOT編集/git/対象fact_id・5テーマ固有語のprompt混入/prompt手直し再実行/Writer・B3実行。
## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 上限¥80、実費¥75.42。D-1: runs/cost_l1.jsonに集計。G-1/F-1該当なし。T-0: 本ファイル+check。T-2: TTSなし。T-3: 対象外。
## 事前指定Read一覧
gen_notes_p03.py、eval_notes_p03.py、run_patterns_p03.py、patterns/A・B・C、eval/targets.json・holdout.json、P0a_article_selection.md。
## 事前指定Grep一覧+追記位置・更新位置の手順
ハーネスをpattern.json契約へ整合(pass_ruleコード評価、B stage2 self_check、C promote+A fallback、--no-existing-notes)、holdout追加、7台帳×3パターン実行、eval、内容ラベル、ablation、結果md。
## 実行コマンド全文
.venv/Scripts/python.exe -m pytest er052_output/open233_polysemy_trial_03/tests/test_p03_tools.py -q
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/run_patterns_p03.py --patterns A_onepass,B_twostage,C_promote --slugs meta,hormuz,space_weapons,sewer,ai_control,A02,small_bag --parallel 3 --budget-jpy-per-call 5 --web-search none
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/eval_notes_p03.py --patterns A_onepass,B_twostage,C_promote --out er052_output/open233_polysemy_trial_03/eval/l1_summary.md
.venv/Scripts/python.exe er052_output/open233_polysemy_trial_03/tools/run_patterns_p03.py --patterns A_onepass --slugs meta,hormuz,space_weapons,sewer,ai_control --no-existing-notes --run-tag ablation --parallel 3 --budget-jpy-per-call 5 --web-search none
## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目)
ハーネス整合とtest、比較表要約、迎合チェック、ablation差、FN理由、台帳外混入件数、実費、所見、T-0結果。
