## 管理ID

OPEN-233-E2E-STAGEWISE-NG-AUDIT-01(委任_C1: 集計表の完成+SSOT反映+commit/push。¥0・API呼び出しなし)

## 性質/到達上限Status/禁止事項

- 性質: 既存成果物(3系統のNG台帳・stagewise_*.json)の再集計+SSOT反映のみ。到達上限Status=USER_DECISION_REQUIRED。
- 禁止: API呼び出し/記事生成/Production変更/CURRENT_SPEC編集/NG台帳の改変/notes_to_error_trace.mdの編集・commit/`git add -A`・amend・force/P2採否・Checker Production反映の判断。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

- E-1: 費用¥0。D-1: API費なし。G-1/F-1: 該当なし。T-0: 本ファイル簡略保存+check実行。T-2/T-3: 音声なし・対象外。

## 事前指定Read一覧

- er052_output/open233_allfact_note_e2e_02/eval/stagewise/stagewise_meta_hormuz.json、stagewise_sewer_ai_control.json、stagewise_space_weapons.json、NG_*.md(根拠確認)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep: NG_*.mdの「判定保留」「既存評価」。追記位置: REPORT末尾 §95、DECISION_LOG末尾、OPEN_ITEMS.mdのOPEN-237/238行末、docs/pm/ACTIVE_TASK.mdの管理ID行。

## 実行コマンド全文

- python C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/894f5cf0-e2ec-4a58-9b10-2bca7acce0da/scratchpad/gen95.py(STAGEWISE_SUMMARY.md生成)
- python docs/pm/tools/check_delegation_prompt.py --file C:/Users/tensh/eigo-radio/docs/pm/delegation_log/2026-10-07_OPEN-233-E2E-STAGEWISE-NG-AUDIT-01_C1.md --json-out C:/Users/tensh/eigo-radio/docs/pm/delegation_log/2026-10-07_OPEN-233-E2E-STAGEWISE-NG-AUDIT-01_C1_check.json

## SSOT追記文

- REPORT §95、DECISION_LOG 1エントリ、OPEN_ITEMS OPEN-237/238追記、ACTIVE_TASK行追加(内容は各ファイル参照)。

## Git

- 対象ファイルのみ個別`git add`(`git add -A`禁止)。commit message末尾にCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>。origin/mainへpush。

## 報告

- RESULT_PACKETは使わず、委任元へ14行以内で返す(主表・遷移・1記事当たり・重大NG・検算・保留・Production無変更・commit・T-0)。
