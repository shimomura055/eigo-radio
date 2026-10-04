# OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01 委任_05

## 管理ID
OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01(委任_05)。並行タスクなし。

## 性質/到達上限Status/禁止事項
委任_04cのK14 Phase 1は「候補Stage1(V4A)@gpt-6-luna」vs「V0(Production vfl01)@gpt-5.6-luna記録値」でprompt差とモデル差が混在。残り2セルを実測し2x2を完成: (A)V0 prompt@gpt-6-luna n=2、(B)候補prompt@gpt-5.6-luna n=2(費用次第でn=1)。対象18 instance、claim照合token重なり50%、劣後=V0記録検出かつ当該セル0/2。あわせて委任_04e成果物(Opus#15ファイル・抽出スクリプト・委任ログ)のインデント整形とcommit。

## 到達上限/禁止
APPROVED_FOR_PRODUCTIONのまま。Production/Trial本体コード変更禁止(既存er052 recall checkスクリプトへ--stage1-variant/--model追加は可)。CURRENT_SPEC/PM_GOVERNANCE編集禁止。git add -A/stash/amend禁止。既存M差分・untracked不可触。ACTIVE_TASK/RESULT_PACKETはaddしない。

## 費用
Guardrail 22円(Cap到達=自動STOPではない)。(A)約10円、(B)n=2は約22円で合計超過のため(B)n=1(約11円)へ縮小可。Phase累計730.14/900円。

## 作業
1 T-0 / 2 引数追加(V0はProduction run_deviation_checkをimportして呼ぶ) / 3 実行(A)(B)+agg 2x2表 / 4 Opus#15インデント除去 / 5 SSOT(OPEN_ITEMS・REPORT 64・Gap文書6-8・REPORT_LEDGER) / 6 明示addでcommit/push。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ。
G-1: git出力は`--porcelain`/`--stat`/`--short`で最小化。
F-1: 自タスクのtranscript退避は不要。
T-2: 本委任はTTSを伴わない。
T-3: 費用上限はGuardrailでありCap到達=自動STOPではない。

## 事前指定Read一覧
er052_open233_stage1_phase1_recall_check_01.py全文、er003 run_deviation_check周辺、agg_phase1.json、Opus#15ファイルhead -20。

## 事前指定Grep一覧+追記位置・更新位置の手順
OPEN_ITEMS該当行、REPORT `^## §64`節末尾、Gap文書 `^### 6-7`後に6-8、REPORT_LEDGER末尾。

## 実行コマンド全文
.venv\Scripts\python.exe er052_open233_stage1_phase1_recall_check_01.py --stage1-variant v0 --model gpt-6-luna --n 2 --out-subdir cell_v0_6luna
.venv\Scripts\python.exe er052_open233_stage1_phase1_recall_check_01.py --stage1-variant candidate --model gpt-5.6-luna --n 2(または1) --out-subdir cell_cand_56luna
`--stage agg` / `--stage matrix`。git status --porcelain、明示add、commit、git push origin main、git log --oneline -1。

## Git
明示addのみ(add -A禁止)、commit message末尾にtrailer Co-Authored-By。メッセージ: OPEN-233-...: K14 Phase 1を2x2に補完(委任_05)。

## 報告(RESULT_PACKET項目)
結論8行以内、2x2表、費用、SSOT/commit/push/raw URL、Fableへの論点。
