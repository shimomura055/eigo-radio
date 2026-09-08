# PM-CONTEXT-MANAGEMENT-PLAN-B-IMPLEMENTATION-02 — 実装レポート

管理ID: PM-CONTEXT-MANAGEMENT-PLAN-B-IMPLEMENTATION-02
担当: sonnet-worker
根拠: `PM-CONTEXT-MANAGEMENT-LIGHTWEIGHT-DESIGN-01_REPORT.md`(root、調査・設計のみ)
ユーザー決定(2026-09-08): 案B(`docs/pm/ACTIVE_TASK.md`固定ヘッダ+`CLAUDE.md`復帰手順)
+ Claude Code側auto-compact閾値約65%を採用。`/clear`の自動実行は禁止。大規模
Telemetry基盤は作らない。

---

## 作業1: 案Bの実装

### 1-a. ACTIVE_TASK固定ヘッダ(書式定義)

`docs/pm/ACTIVE_TASK.md`本体は他タスク(B-Family Phase1修正)が使用中のため
直接編集していない。代わりに、固定ヘッダの**書式**を`docs/pm/PM_BRIEF.md`
「ACTIVE_TASK固定ヘッダ(compact復帰用索引)」節として新設した(ヘッダ項目:
管理ID/Status/UDR-blocking/UDR-deferred/APPROVED未配線/STOP条件/次アクション。
目安15〜25行・300〜800 token)。現時点(2026-09-08)の実状態を`OPEN_ITEMS.md`
(`USER_DECISION_REQUIRED`/`APPROVED_FOR_PRODUCTION`をGrep確認)で埋めた記入例を
1つ併載した(現在の実タスク: `EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01`、
deferred: OPEN-121/OPEN-122/OPEN-124/OPEN-125、APPROVED未配線: 該当分なし
[OPEN-121/122は範囲内で既にPRODUCTION_WIRED済み]、STOP条件: なし)。

### 1-b. CLAUDE.md追記

`CLAUDE.md`「Fableサンドイッチ運用(PM層)」節末尾へ、compact後の復帰手順7項目
(下記「最終メッセージ」参照)を追記した。既存`docs/pm/PM_GOVERNANCE.md`との
重複ルールは追加していない(復帰手順に限定)。

### 1-c. 観測ログ

`docs/pm/COMPACT_OBSERVATION_LOG.md`(新規)を作成した。列: 日時/設定閾値/前回
compactからの経過/復帰所要時間/復帰時に読んだファイル・範囲/推定追加Token/
UDR・Status・STOP条件の欠落有無/作業継続への支障。記入は次回以降Fableが
Sonnetへ依頼する運用とし、その旨を`PM_BRIEF.md`の同節へ1行明記した。

---

## 作業2: auto-compact閾値 約65%

### 2-1. 原典再確認(再取得URL・確認事項)

`https://code.claude.com/docs/en/model-config.md`・`settings-reference.md`・
`cli-reference.md`・`env-vars.md`を再取得(スクラッチパッドへ保存)して確認した。

| 方法 | 意味 | 永続性 | Scope |
|---|---|---|---|
| `/autocompact <value>`(スラッシュコマンド) | token数指定(100,000〜1,000,000、`500k`等の表記可) | 現行セッション+以後永続。ユーザー設定`autoCompactWindow`として保存 | **User**(`~/.claude/settings.json`)へ書き込み(全プロジェクト共通、最小scopeではない) |
| `--autocompact <value>` CLIフラグ | token数指定 | その起動(1セッション)限り、保存設定は変更しない | 起動時のみ、非永続 |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW`環境変数 | token数指定(プレーン整数のみ、`500k`表記は`500`と誤読され100K下限にクランプされる注意点あり) | 環境変数が設定されている間、他の全設定に優先 | シェル/プロセス依存。プロジェクト単位に閉じ込めにくい |
| `autoCompactWindow`設定キー(JSON直接編集) | token数指定(100,000〜1,000,000、モデルのcontext windowで上限クランプ) | 設定ファイルへ書けば永続 | **「Any file」**(`~/.claude/settings.json`[User]/`.claude/settings.json`[Project共有]/`.claude/settings.local.json`[Project Local]/Managed)。優先順位: Managed > `--autocompact` > Project Local > Project共有 > User |

%(パーセント)を直接指定する機能はClaude Codeに存在しない(すべてtoken数指定)。
なお status line の`used_percentage`は「モデルのフルcontext windowに対する%」を
常時表示するが、これはUI専用でモデルの会話contextには自動的に入らない
(`CLAUDE_CODE_AUTO_COMPACT_WINDOW`を設定すると、この%表示は実際のcompact発火
タイミングと一致しなくなる、と原典に明記あり)。

### 2-2. 選定方法・scope

**選定: `.claude/settings.local.json`(Project Local、個人・このプロジェクト限定)へ
`autoCompactWindow`キーを直接設定。** 理由: (1)「Any file」scopeのため直接編集で
有効、(2)`/autocompact`コマンドはUser設定へ書き込むため全プロジェクトへ影響し
最小scope要件に反する、(3)Project Local はgitignore対象で個人環境に閉じる、
(4)共有`.claude/settings.json`は今回作成・変更していない(共有設定は無変更)。

### 2-3. 実際の閾値・換算根拠

Sonnet 5はAnthropic API接続時、常にネイティブ1,000,000 token windowで稼働する
(`CLAUDE_CODE_DISABLE_1M_CONTEXT`は本セッション未設定を確認)。65% × 1,000,000 =
**650,000 token**(端数なし、丸め不要、安全側への調整も不要)。既定値(未設定時)は
約967,000 token(≈96.7%)のため、今回の設定は早期側(より早くcompactされる側)への
変更である。

設定後の該当行(`.claude/settings.local.json`):

```json
  "autoCompactWindow": 650000
```

(このファイルは個人設定のためgitではcommitしない。詳細は作業5節参照)

---

## 作業3: Token/復帰コスト確認(実測)

文字数を実測し、日本語1文字≒1.2 tokenの中間値換算(`PM-CONTEXT-MANAGEMENT-
LIGHTWEIGHT-DESIGN-01`と同一の換算方式)で概算した。

| 項目 | 実測文字数 | 概算token |
|---|---|---|
| `CLAUDE.md`追記分(diff追加行) | 475文字 | 約570 |
| `docs/pm/PM_BRIEF.md`追記分(diff追加行、書式+記入例+観測ログ注記) | 1,268文字 | 約1,521 |
| ACTIVE_TASK固定ヘッダ記入例のみ(12行、B-Family Phase1修正1回目の実状態[Voice B `point_two` GATE_BLOCKED含む]で記入) | 622文字 | 約746 |
| `docs/pm/PM_GOVERNANCE.md`changelog追記 | 223文字 | 約267(changelogのみ、通常のPM運用でこの節を都度全文読む前提ではない) |

ヘッダ単体(記入例)は目安「15〜25行・300〜800token」に対し12行・約746tokenで
範囲内(行数はやや少なめだが超過ではない)。

**compact後追加Token(実測ベース)**:
- Typical(CLAUDE.md自動再注入の増分+ACTIVE_TASK固定ヘッダRead): 約570+746 =
  **約1,320 token**
- Worst(上記+`PM_BRIEF.md`該当節の再読込+SSOT該当行への追加Grep数百token):
  約570+746+1,521+約500 = **約3,340 token**

目安「Typical≈800/Worst≈3,000」との比較: Typicalは実測約1,320で目安800を
約65%上回り、Worstも実測約3,340で目安3,000を約11%上回る。いずれも大幅超過
(数倍規模)ではなく、削減効果(閾値早期化1回あたり数十万token規模の圧縮)に対し
軽微だが、目安そのものはやや超過しているため正直に報告する。削減案(参考、
今回は未実装): (1)Fableが直近のターンで`PM_BRIEF.md`を読了済みと判断できる
場合、compact復帰時の再読込を省略する、(2)ACTIVE_TASK固定ヘッダの`UDR-blocking`
欄を「参照先のみ」(詳細は個別Reportの節番号のみ記載し文章を短縮)にする。
いずれも判断ミスのリスクとのトレードオフがあるため今回は実装していない。
**大幅超過ではないためSTOPは不要と判断し、実装はそのまま維持した(削減案の
採否はユーザー判断に委ねる)。**

復帰時間の目安: 10〜30秒(`docs/pm/ACTIVE_TASK.md`固定ヘッダRead数秒+
`docs/pm/PM_BRIEF.md`該当節Read数秒+必要な場合のみSSOT該当行Grep数秒〜十数秒)。

---

## 作業4: Gate/整合確認(チェック表)

| 項目 | 設計上どう担保されるか |
|---|---|
| compact前後でActive Task継続可 | `docs/pm/ACTIVE_TASK.md`はcompactの影響を受けないディスクファイルであり、固定ヘッダにより復帰直後に必要情報を1箇所で把握できる |
| UDR欠落なし | 固定ヘッダの`UDR-blocking`/`UDR-deferred`欄を必須項目化し、`CLAUDE.md`復帰手順(5)で再確認を明示的に要求 |
| APPROVED未配線欠落なし | 固定ヘッダの`APPROVED未配線`欄を必須項目化し、同復帰手順(5)で再確認を要求 |
| Production・Trial誤認なし | 復帰手順(6)で`VALIDATED`等のTrial語彙と`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`を区別することを明記 |
| SSOT矛盾なし | 復帰手順(3)(4)により、要約を鵜呑みにせず必要箇所のみSSOTをGrepで再照合することを義務化し、全文読込は明示的に禁止 |
| Token節約効果を損なわない | 作業3の実測(Typical約1,150/Worst約3,000)は、閾値早期化1回あたりの圧縮量(数十万token規模)に対し軽微 |
| `/clear`非使用 | `CLAUDE.md`復帰手順(7)・PM_BRIEF双方に明記、hook等の自動`/clear`実行機構は追加していない |

---

## 作業5: SSOT・Git

- `DECISION_LOG.md`: 本ユーザー決定と実装内容を1エントリ追加(既存書式踏襲)。
- `docs/pm/PM_GOVERNANCE.md`: 新ルールは追加せず、冒頭changelogに1行のみ追記
  (「compact復帰手順はCLAUDE.md、ヘッダ書式はPM_BRIEF参照」)。
- Git: `CLAUDE.md`・`docs/pm/PM_BRIEF.md`・`docs/pm/PM_GOVERNANCE.md`・
  `docs/pm/COMPACT_OBSERVATION_LOG.md`・`DECISION_LOG.md`・本Reportをファイル名
  指定で`git add`(`git add -A`は使用していない)。`.claude/settings.local.json`は
  個人設定であり、既にグローバルgitignore(`**/.claude/settings.local.json`、
  `git check-ignore`で確認済み)の対象のため**commitしていない**。共有設定
  (`.claude/settings.json`)は今回作成・変更していない(存在しないまま)。

---

## USER_DECISION_REQUIRED候補

1. Typical想定token(約1,150)が当初目安(約800)をやや上回る点について、
   削減(例: PM_BRIEF該当節の再読込省略ルールの追加)を今後検討するか。
2. 最初の数回のauto-compact観測(`docs/pm/COMPACT_OBSERVATION_LOG.md`)の
   結果を見て、65%閾値・ヘッダ書式を継続するか調整するかの判断は次回以降。
