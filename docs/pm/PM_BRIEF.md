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

- Sonnetへの委任は1管理IDあたり初回+Fableからの修正・再生成指示最大3回
  (合計最大4回)。1回で足りれば1回で止める(詳細は
  `docs/pm/PM_GOVERNANCE.md` 11節)
- Opusは診断目的で最大1回まで
- Opus診断の後、Sonnetを自動的に再実行しない
- 上記いずれかの上限に到達したら`USER_DECISION_REQUIRED`としてSTOPする

## ACTIVE_TASK固定ヘッダ(compact復帰用索引)

Fableは、`docs/pm/ACTIVE_TASK.md`を上書きする全ての委任で、ファイル冒頭に
以下の固定ヘッダを置く(本文はヘッダの後に続ける)。目安: ヘッダ全体で
15〜25行・300〜800 token以内。ヘッダは要約であり、詳細はSSOT
(`OPEN_ITEMS.md`等)を必要箇所だけGrepして確認する(鵜呑みにしない)。
compact直後の復帰手順は`CLAUDE.md`「Fableサンドイッチ運用(PM層)」節
末尾を参照。

### 書式

```
管理ID: <現在の管理ID>
Status: <一言>
UDR-blocking: <ID:一言、複数可>(なければ「なし」)
UDR-deferred: <ID:一言、複数可>(なければ「なし」)
APPROVED未配線: <ID:一言、複数可>(なければ「なし」)
STOP条件: <一言>(なければ「なし」)
次アクション: <一言>
```

### 記入例(2026-09-08時点、実状態)

```
管理ID: EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01(修正1回目)
Status: OPEN-121/122のB-Family本文配線は完了・テスト/回帰PASSだが、
  `point_two`(Voice B)がrepetition QA flaggedで3回STOPPED→GATE_BLOCKED、
  episode/player.html未生成
UDR-blocking: `point_two`著者意図の反復をcanonical-repeat-count logicが
  誤検出した疑い。(a)人間試聴承認/(b)tokenization改善を別タスク起票/
  (c)その他、をFable/ユーザーへ確認中(§9-6参照)
UDR-deferred: OPEN-121(重複検知一般拡張)/OPEN-122(Key Phrase展開)/
  OPEN-124(未追跡285件分類、別タスク進行中)/OPEN-125(entity誤判定Trial、低優先保留)
APPROVED未配線: なし(OPEN-121/122該当範囲はPRODUCTION_WIRED済み)
STOP条件: `point_two`がGATE_BLOCKEDのままAssembly未完了
次アクション: UDR-blockingの(a)/(b)/(c)判断後、Assembly再試行→受入判定
```

### 観測ログ

最初の数回のauto-compactは`docs/pm/COMPACT_OBSERVATION_LOG.md`(軽量な
Markdown表)へ観測結果を記録する。Fableは次にSonnetへ委任するタイミングで
記入を依頼する運用とする(大規模なTelemetry基盤は作らない)。

## 禁止事項

- Agent Teamsは使用しない
- 複数Agentの並列起動は`docs/pm/PM_GOVERNANCE.md` 8節の条件(独立タスク・
  一時ファイル衝突回避)を満たす場合のみ可
