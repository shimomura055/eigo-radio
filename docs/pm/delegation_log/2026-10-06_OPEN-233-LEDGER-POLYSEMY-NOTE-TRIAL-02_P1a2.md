# OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02 委任_P1a-2(簡略保存)
## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02 委任_P1a-2(notes連結をtxt追記方式へ切替+5テーマnotes生成+差分0確認+配置)。
## 性質/到達上限Status/禁止事項
DEVツール改修+Trial前段(有料notes生成5call)。禁止: Production変更/Writer・B3・Checker実行/SSOT編集/git/既存台帳上書き/note手直し/新テーマResearch。差分0不成立ならSTOP。
## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 上限25円(各call 5円)。D-1: ledgers/cost_p1a.jsonに集計。G-1/F-1: 該当なし。T-0: 簡略保存+check。T-2: TTSなし。T-3: 対象外。
## 事前指定Read一覧
gen_notes_p02.py、check_notes_only_diff_p02.py、P0a_article_selection.md、er003_v1_en_direct_vfl_01_generate.py L289-303。
## 事前指定Grep一覧+追記位置・更新位置の手順
gen_notes_p02.pyへ--append-to-txt(+--reuse-raw)追加、txt決定論追記、check後に配置、hormuz topic探索、LEDGER_FREEZE_P02.json作成。
## 実行コマンド全文
pytest test_gen_notes_p02.py / gen_notes_p02.py --append-to-txt ... --budget-jpy 5(5テーマ) / check_notes_only_diff_p02.py / git status --porcelain(Production4ファイル)/ check_delegation_prompt.py。
## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目)
ツール改修・test、hormuz topic取得元、テーマ別付与note、diff結果、配置sha、実費、STOP、T-0結果。
