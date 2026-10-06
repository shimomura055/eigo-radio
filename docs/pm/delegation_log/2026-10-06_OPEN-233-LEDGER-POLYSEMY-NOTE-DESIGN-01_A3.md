## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01(委任_A3: 多義語候補の収集・分類、notes生成規則の草案、具体例、Trial評価表の準備、¥0)

## 性質/到達上限Status/禁止事項
性質: 設計草案(read-only+草案ファイル)。禁止: コード・prompt変更/有料API/SSOT編集/git/個別語のハードコード/前回P'の明確化規則9項目の持ち込み/Fact本文の書き換え提案。A1/A2出力には触らない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
該当なし(¥0)。T-0: 簡略保存+checker。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## 内容(要約)
事前指定Read(02_cases.md、3台帳、er003 notes_for_writer prompt)から多義語候補表・発火率・notes規則草案・具体例(a)(b)(c)を作成し docs/pm/polysemy_note/A3_polysemy_candidates_and_rules.md、A3_trial_eval_template.md へ出力。

## 事前指定Read一覧
docs/pm/ledger_clarity/02_cases.md、3台帳(meta/hormuz/small_bag)、er003_v1_en_direct_vfl_01_generate.py(notes_for_writerのみ)。

## 事前指定Grep一覧+追記位置・更新位置の手順
Grep notes_for_writer(er003のみ)。新規ファイル2本のため追記位置なし。

## 実行コマンド全文
- T-0のみ: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01_A3.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01_A3.md_check.json`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
(1)候補件数・内訳 (2)FP懸念 (3)規則要点 (4)具体例 (5)評価表所在 (6)T-0結果
