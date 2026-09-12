# DELEGATION_STANDARD_RULES_DRAFT

**草案(2026-09-12作成)。正式SSOTではない。**正式ルールは
`docs/pm/PM_GOVERNANCE.md`本文のみ(本ファイルはFable委任文作成時の
チェックリスト草案)。

## 禁止事項
- Git操作(commit/push/add -A/stash/clean)は明示許可がない限り禁止。
- API支出(LLM/TTS/ASR呼び出し)は明示許可・上限額の指定がない限り禁止。
- 他Agent成果物(並列稼働中の管理ID配下ファイル)への不可侵。

## 読込効率(E-1/D-1/G-1、PM_GOVERNANCE 11節)
- E-1: 同一task内で同一ファイルを再読しない。
- D-1: 配線タスクは該当関数/行範囲のみRead(全文読込禁止)。
- G-1: git出力は`--short`/`--quiet`で最小化。

## 命名・語彙
- 一時ファイル: `docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`(タスクごと上書き)。
- Status語彙: `VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`/
  `USER_DECISION_REQUIRED`を仕様どおり区別する。

## 報告形式
- `RESULT_PACKET.md`は短い要約のみ(目安20行)。詳細は既存REPORT/output構造へ。
- commit trailerはFable指定のものをそのまま使用。
