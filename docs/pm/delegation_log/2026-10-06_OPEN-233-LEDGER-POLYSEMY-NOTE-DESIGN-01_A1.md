## 管理ID
OPEN-233-LEDGER-POLYSEMY-NOTE-DESIGN-01 委任_A1(notes伝達経路の事実確認、¥0)。
read-only、報告ファイル1本のみ。
## 性質/到達上限Status/禁止事項
事実確認。コード・prompt変更、有料API、SSOT編集、git、推測は禁止。
A2/A3出力には触らない。
未確認は「未確認」と書く。
## 事前指定Read一覧
er003 generate、er019 b3/ja_writer、er012/er019 production runner、er052 runnerの指定箇所。
P-TRIAL-01 after_pprime_01成果物。
## 事前指定Grep一覧+追記位置・更新位置の手順
notes_for_writer/ledger_text/must_fix等をGrepし、経路表を作成する。
判定(a)〜(h)とSTOP判定を出す。
出力はdocs/pm/polysemy_note/A1_notes_delivery_facts.md。
## 実行コマンド全文
python docs/pm/tools/check_delegation_prompt.py --file <本ファイル> --json-out <同名_check.json>
## SSOT追記文
なし。
## Git
なし。
## 報告(RESULT_PACKET項目)
判定a〜h、STOP有無、P-TRIAL実証、retry/Rewrite要点、出力パス、T-0結果。
## 固定ブロック
E-1: 該当なし(¥0)
D-1: 該当なし(¥0)
G-1: 該当なし(¥0)
F-1: 該当なし(¥0)
T-1: 該当なし。TTSなし(T-2/T-3対象外)
