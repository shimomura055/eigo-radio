# OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04 委任_P4e (簡略保存)
## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04(P4e: Control条件5記事のPhase 1出力の段別ラベル付け、¥0)。
## 性質/到達上限Status/禁止事項
性質: 評価ラベル(read-only+評価ファイル)。禁止: 有料API/生成物変更/Production変更/SSOT編集/git/N+B評価/P4d領域(b1b,checker,cost_*)の読込。
## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1: 該当なし(¥0)。T-0: 本ファイル簡略保存+check実行。T-2/T-3: TTSなし・対象外。
## 事前指定Read一覧
eval_template_5articles.md、P0a_article_selection.md、labeling_guide_01.md、各記事brief/R0/R1/R2と固定台帳。
## 事前指定Grep一覧+追記位置・更新位置の手順
対象fact毎に3値ラベル、記事全体走査、Meta経路欄、決定論指標。出力は各runs/<slug>/eval/E_<slug>_control.md(5本)と docs/pm/polysemy_trial_04/control_labels_summary.md。
## 実行コマンド全文
`.venv/Scripts/python.exe er052_output/open233_ledger_clarity_p_trial_01/tools/ja_copy_rate_p01.py --ja <original.md|revision2.md> --ledger <control txt>`(5記事x2)と、`python docs/pm/tools/check_delegation_prompt.py --file <本ファイル> --json-out <同名_check.json>`。
## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目)
3値表要約・Meta経路逐語・候補件数・JA逐語率・出力パス・T-0結果。
