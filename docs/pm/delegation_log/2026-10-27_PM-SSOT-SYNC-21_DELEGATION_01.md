# PM-SSOT-SYNC-21 委任文(保存: Sonnet実行層が受領した委任文の要約再構成。jsonl自動抽出はindex 727〜732でNOT_FOUNDのため手動保存)

## 管理ID

PM-SSOT-SYNC-21(SSOT同期: ユーザー正式決定3件[Y再配達Closeout+Voice説明文+Chunk境界マーカー USER_04 / AI島KP/KW各10件USER_CONFIRMED+文法選定仕様変更Top1/Top2 AI-ISLAND USER_02 / AI島V3フォーム実運用 AI-ISLAND USER]の記録、GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02/_02S/_03/_04、KCP 委任_03、YSP 委任_07、AIF 委任_01、PM_GOVERNANCE違反記録。API 0・JPY0)。本委任のみがSSOT 3ファイル+ACTIVE_TASK+PM_GOVERNANCE+USER_DECISION_REGISTER_01の編集権を持つ。

## 性質/禁止

SSOT同期(Fable判定の転記・整合)。禁止: SSOT全文読込、判定変更、Status格上げ、`add -f`/`pull --rebase`/pathspecなしcommit、worktree stale上書き。

## 固定ブロック

E-1/D-1/G-1/F-1: 従来どおり(委任文原文の固定ブロック参照)。T-0: 委任文保存+check。T-2/T-3: なし。

## 事前指定Read一覧

一次資料=docs/pm/RESULT_PACKET_{GPG2,GPG2S,GPG3,GPG4,KCP3,YSP7,AIF1}.md、ユーザー原文=delegation_log内のFAMILY-Y-STYLE-PROFILE-FIX-01_USER_04.md、AI-ISLAND-FORM-PRODUCTION-01_USER.md(USER_02は未保存=委任_02で保存)。

## 事前指定Grep一覧+追記位置・更新位置の手順

OPEN_ITEMS: OPEN-559/556/537/539/526/545/543/549/560、新規OPEN-561。CURRENT_SPEC: 文法/Part 2/最大2/独立枠/別途Fable/確定内容/Voice 1〜3/⏸。DECISION_LOG: 先頭ヘッダーチェーンへ3エントリ。PM_GOVERNANCE: 違反記録末尾追記。UDR: UDR-/OPEN-526/MONKEY。

## 実行コマンド全文

`py docs\pm\tools\check_delegation_prompt.py --file <本ファイル> --json-out <本ファイル>_check.json`。Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件。

## SSOT追記文

Fable判定A〜F(A=DECISION_LOG 3件、B=CURRENT_SPEC、C=OPEN_ITEMS、D=UDR、E=違反記録4件、F=ACTIVE_TASK)。実際の追記文は各SSOTおよびREPORT_01を参照。

## Git

commit message: `PM-SSOT-SYNC-21: ユーザー決定3件(...)記録、OPEN-559/556/537/545更新、OPEN-539/526/560 CLOSED、OPEN-561起票、違反記録(API 0)`。pathspec付きcommit、push。

## 報告

`docs/pm/RESULT_PACKET_SSOT21.md`: (0)T-0、(1)更新箇所、(2)齟齬・保留、(3)必須4行+判定整合、commit hash・raw URL。
