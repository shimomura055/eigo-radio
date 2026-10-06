## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02(委任_P1a-3: notes生成規則の厳格化+5テーマ再生成(上限¥25、1回のみ)+差分0確認+配置更新)

## 性質/到達上限Status/禁止事項
性質: DEVツール改修+Trial前段再実行(有料5 call)。禁止: Production file変更/Writer・B3・Checker実行/SSOT編集/git/対象IDハードコード/再生成の繰り返し/notes手直し。

## 固定ブロック
E-1: 上限¥25。D-1: 実費をledgers/cost_p1a.jsonへgen2追記。G-1/F-1: 該当なし。T-0: 簡略保存+checker。T-2: TTSなし。T-3: 対象外。

## 事前指定Read一覧
gen_notes_p02.py(prompt部)、notes_summary_table_p1a.md、B_design.md §11

## 事前指定Grep一覧+追記位置・更新位置の手順
gen1をledgers/<slug>/gen1/へ退避→prompt厳格化(規則5〜7、reverse_reading/severity、--max-notes 3)→5テーマ再生成→diff PASS→配置更新、LEDGER_FREEZE_P02.json更新(gen1_sha保持)

## 実行コマンド全文
pytest tests/test_gen_notes_p02.py -q / gen_notes_p02.py --append-to-txt <txt> --out-dir ledgers/<slug> --budget-jpy 5 --max-notes 3 / check_notes_only_diff_p02.py --control <c> --nb <n> --out <p>

## SSOT追記文
なし。

## Git
なし。

## 報告
RESULT_PACKET参照。
