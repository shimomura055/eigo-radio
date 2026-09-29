# 委任文記録: LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01(委任_03、2026-09-29)

## 管理ID

LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01(Part C=Part A/B の統合と §8「再設計に向けた材料」の整理、委任 _03)。**read-only 調査の統合。決定・採用提案・Production 変更提案を書かない**。一時ファイル `docs/pm/ACTIVE_TASK_LDC.md` / `docs/pm/RESULT_PACKET_LDC.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main`、HEAD `73253447` 以降)。出力先: `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`(root 直下、新規=正式 REPORT)+delegation_log のみ。Part A/B のファイルは編集しない(参照のみ)。**Production code・Prompt・Checker threshold・SSOT 4 点・REPORT_LEDGER の変更禁止、Trial 開始禁止、E2E 再開禁止、API 呼び出し禁止(¥0)、Opus 起動禁止**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 入力(全文 Read 可)

- `docs/pm/investigation_ledger_deviation_check_01_part_a.md`(章 1・2・6・7)
- `docs/pm/investigation_ledger_deviation_check_01_part_b.md`(章 3・4・5)
- 必要に応じ evidence ファイル(Part A/B が引用するパス)を Grep で再確認。**新規の調査範囲拡大はしない**(A/B の不整合を解消するための確認のみ)。

## 作業

1. **統合 REPORT** を、ユーザー指定の章立て 1〜8 で作成(1 役割整理[冒頭に「何が同じで何が違うか」]/2 hard・soft/3 過去 STOP 事例[A/B 表]/4 厳しさ 4 区分[クロス集計含む]/5 QCD 影響[未計測は「未計測」]/6 信頼性の最低ライン/7 Hormuz trace[「MAJOR になる理由」と「実害の論点」を分離]/8 再設計に向けた材料)。Part A/B の記述は要約せず必要箇所を転記(evidence の file:line・commit・管理ID を落とさない)。A/B 間で矛盾・重複があれば「整合メモ」で明示(例: Part A「同一関数」と Part B「旧世代 Checker」の関係=世代差の整理)。
2. **§8 再設計に向けた材料**(決定しない。各項目に根拠となる章・事例番号を付ける): 現行設計で守れているもの/過剰品質になっている可能性がある箇所/緩和すると危険な箇所/hard・soft を分けられそうな箇所(例: `notes_for_writer` の扱い、`origin=ja_source` の一律即 STOP、changed_causality・certainty の severity)/STOP ではなく warning・logging 候補になり得る箇所/追加 Trial が必要な論点(例: Checker 非決定性の実測=同一入力 n 回判定の一致率、留保文を含む claim 単位判定の扱い、Standard/Advanced 対称 Check の必要性)。**「この案を採用すべき」「Production をこう変更する」は書かない**。各材料は「観察された事実」と「論点」を分けて書く。
3. **未解決問題・未計測項目** の一覧(Part A/B から集約)。
4. 冒頭に Status 行: 「調査タスク(read-only)。Production code/Prompt/閾値/SSOT 変更なし。Family X E2E は STOP 維持。設計素案は ChatGPT 側で作成後、Opus L2 レビュー(未実施)」。ユーザー向け表記 Standard/Advanced。
5. REPORT_LEDGER への登録文案を RESULT_PACKET に(編集権なし)。

## 固定ブロック

T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_03.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_03.md --json-out docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_03.md_check.json` を実行し結果1行記録。T-2: TTS なし。T-3: API 支出なし。E-1/D-1/G-1/F-1 標準。

## 事前指定Read一覧 / 事前指定Grep一覧

- 上記入力 2 ファイル(全文)。evidence 再確認は Grep のみ。更新位置: 統合 REPORT(新規)、delegation_log。

## 実行コマンド全文

- `git pull --ff-only origin main`
- `git diff --stat HEAD`(本タスク由来のみ)

## Git

- add 対象(path 指定のみ): `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`、delegation_log+`_check.json`。メッセージ `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01: Part A/B統合REPORT(現行仕様・hard/soft・過去事例・4区分・QCD・最低ライン・Hormuz trace・再設計材料、決定なし)`、trailer `Management-ID: LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01`。push。

## 報告(RESULT_PACKET_LDC + handback、目安40行)

ユーザー指定フォーマットの各見出し(【現在のLedger Check】【現在のDeviation Check】【両者の違い】【hard constraint / soft guidance】【過去のSTOP事例】【過剰品質候補】【止めるべき重大事例】【QCD影響】【Hormuz事例のtrace】【信頼性の最低ライン】【再設計の論点】【未解決問題】)ごとに 2〜5 行の要点(Fable が正式報告に転記する)、整合メモの要点、commit hash・raw URL。
