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
   - `OPEN_ITEMS.md` — 未決事項(唯一の管理場所。`docs/pm/`には作らない)。
     3,000文字超だった行はStatus要約のみを残し、履歴全文は
     `OPEN_ITEMS_HISTORY.md`(同じroot直下、別の管理場所ではなく
     `OPEN_ITEMS.md`各行の切り出し先)へ原文のまま移動した
     (PM-TOKEN-EFFICIENCY-T1-OPEN-ITEMS-RESTRUCTURE-01、2026-09-10)。
   - `HISTORY_INDEX.md` — 履歴索引
   - `ER-*_REPORT.md` — 個別タスクの正式な詳細報告・証跡
5. `docs/pm/MODEL_ROUTING_TRIAL_LOG.md` — モデル選定(Haiku/Sonnet/Opus)運用
   Trialの定義・Risk分類・実績ログ(SSOTではない。正式採用は別途ユーザー判断)

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
全文はここへ複製しない。新対策・仕様変更の前には、`docs/pm/PM_GOVERNANCE.md`
「2-1. 既存対策・仕様 Reconciliation Check」を必ず先に確認する
(2026-09-09追記)。+コスト影響評価(PM_GOVERNANCE 2-2)。自明な修正
(例: B-4V-1/2)は2-1確認後、承認範囲内で改善・改善Trialを実施してから
報告し、毎回UDRで止めない(STOP必須6条件あり、詳細は
`docs/pm/PM_GOVERNANCE.md` 11節「自明な修正の自律実施」、2026-09-09追記)。
主要artifactの再生成・修正前には、旧artifactの二重最終版化を避けるため
`docs/pm/PM_GOVERNANCE.md`「2-3. Artifact supersession確認」を必ず確認する
(2026-09-09追記)。報告単位(Lane/Workstream/Feature/Trial群等)を基準に
した即時報告・未回答フル再掲・Next Action/Reminder提示の正式SSOTは
`docs/pm/PM_GOVERNANCE.md`「12. 報告単位管理ルール(Reporting Unit
Rule)」(2026-09-10追記)。報告可能な単位が出たら他の並列作業を待たず
報告し、ユーザー未回答の過去報告があれば次回報告時にフルレポートで
必ず再掲する。Fable/sonnet-worker/opus-consultant/haiku-worker/ユーザーの
責任分担は`docs/pm/PM_GOVERNANCE.md`1節を参照(haiku-workerはSonnet不要の
read-only定型処理限定、2026-09-10追加)。新規記事のテーマ選定ルール
(Fable/Claudeが単独で決めない、新規記事は問題なければ最終版候補まで
持っていく前提)は`docs/pm/PM_GOVERNANCE.md`13節を参照(2026-09-10新設、
13-5は2026-09-11追記)。

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
20〜30行・300〜800 token以内(2026-09-10、報告単位管理ルール追加に伴い
15〜25行から緩和)。ヘッダは要約であり、詳細はSSOT(`OPEN_ITEMS.md`等)を
必要箇所だけGrepして確認する(鵜呑みにしない)。compact直後の復帰手順は
`CLAUDE.md`「Fableサンドイッチ運用(PM層)」節末尾を参照。

### 書式

```
管理ID: <現在の管理ID>
Status: <一言>
UDR-blocking: <ID:一言、複数可>(なければ「なし」)
UDR-deferred: <ID:一言、複数可>(なければ「なし」)
APPROVED未配線: <ID:一言、複数可>(なければ「なし」)
STOP条件: <一言>(なければ「なし」)
次アクション: <一言>
未回答報告: <報告単位名:未回答項目ID列挙、報告日、参照REPORT>(複数可、
  なければ「なし」。`docs/pm/PM_GOVERNANCE.md`12節「報告単位管理ルール」
  対象、2026-09-10追加)
報告単位Status: <単位名:状態>(複数可、例: Lane A-1 Household=CLOSED /
  Lane A-1 Discovery仕様=USER_DECISION_REQUIRED。2026-09-10追加)
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
