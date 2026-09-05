# PM_BRIEF — Fable向け案内板

**このファイルはSSOT(正式仕様の唯一の情報源)ではない。** 正式仕様・決定履歴・
未決事項・詳細報告は、すべてリポジトリroot直下および既存の個別レポートに
存在する。このファイルはその「入口の地図」だけを提供する。

## 参照順序(この順で見る)

1. `docs/pm/PM_BRIEF.md`(このファイル)
2. `docs/pm/ACTIVE_TASK.md` — 今進めているタスクの一時作業票(SSOTではない)
3. `docs/pm/RESULT_PACKET.md` — Sonnet/Opusからの一時報告(SSOTではない)
4. 必要な箇所だけ、以下のroot直下SSOTをGrepする(全文読み込みしない):
   - `CURRENT_SPEC.md` — 正式仕様SSOT
   - `DECISION_LOG.md` — 意思決定履歴
   - `OPEN_ITEMS.md` — 未決事項(唯一の管理場所。`docs/pm/`には作らない)
   - `HISTORY_INDEX.md` — 履歴索引
   - `ER-*_REPORT.md` — 個別タスクの正式な詳細報告・証跡

`ACTIVE_TASK.md`と`RESULT_PACKET.md`はタスクごとに上書きされる一時ファイルであり、
正式記録ではない。正式反映は必ず上記SSOTへ行う。

## Fableの読み方(コスト抑制)

- Fableは巨大SSOT(`CURRENT_SPEC.md`・`DECISION_LOG.md`)を全文読まない。
- 管理ID(`ER-XXX-...`/`OPEN-XXX-...`)・仕様名・Gate名でGrepし、必要箇所だけ読む。
- コード全体・大量ログ・`er0XX_output/`配下のディレクトリは読まない。

## 正式Status語彙(既存SSOTで使われているものをそのまま使う)

- `VALIDATED` — Trialとして有効性が確認された状態。**Production採用ではない。**
- `APPROVED_FOR_PRODUCTION` — **人間ユーザーだけが決定できる。** Fable/Sonnet/Opusは
  自ら`APPROVED_FOR_PRODUCTION`を宣言しない。
- `PRODUCTION_WIRED` — 正式Production経路へ配線済み。
- `USER_DECISION_REQUIRED` — 上限到達・仕様変更候補発見時などにSTOPし、
  人間ユーザーの判断を待つ状態。
- `REJECTED` — 却下された案。

Gateの正式定義(Audio Validation Gate、Human Review Lock等)は既存SSOT側の記述が正であり、
このファイルへ複製しない。

## PM運用Gate・Closeout原則

PM Gate 1〜7・PM Closeout Mandatory Check・1記事ずつ完結原則(例外条件含む)・
安全≠成功原則の正式SSOTは
`docs/pm/PM_GOVERNANCE.md`(2026-09-05、PM-HANDOFF-CHATGPT-001-CLOSEOUT-SSOT-01)。
全文はここへ複製しない。

## ループ上限(サンドイッチ運用)

- Sonnetへの委任は合計最大2回(初回+修正1回)
- Fableからsonnet-workerへの差し戻しは最大1回
- Opusは診断目的で最大1回まで
- Opus診断の後、Sonnetを自動的に再実行しない
- 上記いずれかの上限に到達したら`USER_DECISION_REQUIRED`としてSTOPする

## 禁止事項

- Agent Teamsは使用しない
- 複数Agentの並列起動は`docs/pm/PM_GOVERNANCE.md` 8節の条件(独立タスク・
  一時ファイル衝突回避)を満たす場合のみ可
