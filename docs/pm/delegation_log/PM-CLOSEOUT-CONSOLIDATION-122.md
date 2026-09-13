## 管理ID
PM-CLOSEOUT-CONSOLIDATION-122

## 範囲
性質: SSOT反映+Git。¥0、API呼び出しなし。Productionコード無編集。並行中のFamily Cタスク(`EDITORIAL-FUTURE-*`、`er013_*`、`docs/pm/RESULT_PACKET_FC4.md`)のファイルに触れない。禁止: `git add -A`/`stash`/`amend`、既存行削除、判断語の新規付与(Fable確定済み文言を転記)。`git index.lock`があれば10秒待ち最大3回。

## 固定ブロック
---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0: 本委任文を`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-122.md`へ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-122.md" --json-out "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-122_check.json"`を実行し結果をRESULT_PACKETへ1行記録(FAILでも継続)。
---

## ユーザー指示(原文)
> S2について追加Trialを先に増やさず、Production設計フェーズへ進むことを承認しました。ただし、これはまだProduction実装・配線承認ではありません。現在StatusはVALIDATED→Production設計着手可であり、APPROVED_FOR_PRODUCTIONではありません。(中略)Productionコードへの実装・配線はまだ行わず、設計完了後にGate 2としてユーザー判断を求めてSTOPしてください。

## 事前指定Read一覧
- `docs/pm/RESULT_PACKET_S2D.md`(全文、1回)

## 事前指定Grep一覧+追記位置・更新位置の手順
1. `OPEN_ITEMS.md`: Grep `-n` `^\| OPEN-135 \|`(範囲=次の`^\| OPEN-`行の直前)。範囲最終行末尾(閉じ`|`直前)へ追記(巨大行はPythonで安全に末尾追記可)。
2. `DECISION_LOG.md`: Grep `-n` `^## PM-CLOSEOUT-CONSOLIDATION-121|^## 参照元`(本文追記位置=`## 参照元`直前)。索引行は`CONSOLIDATION-121`索引行の直後に同形式で1行。該当行のみRead(前後3行)。

## SSOT追記文(そのまま使用、日付2026-09-13)
### OPEN_ITEMS.md OPEN-135 末尾追記
「**追記(2026-09-13、FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01、¥0設計完了、Status: VALIDATED→Production設計完了→`USER_DECISION_REQUIRED`[Gate 2]、実装・配線未承認)**: ユーザー承認(設計着手可、実装・配線は未承認)に基づき設計。要点: 分割=案P1推奨(Discovery専用新関数`run_one_pattern_staged`をopt-inの新`editorial_mode`で追加、既存`run_one_pattern`はNews/Trend/現行Discovery向けに無変更。案P2[全モード共通段階化]は回帰範囲が全経路に及び非推奨)。正式処理順=Focus解決→Stage 1 Main Story生成+Stage 1 QA(blocking時Stage 1再生成)→Stage 2 Role Planning(確定Main Story本文入力、角度hintなし)→Stage 3 Points生成+Evidence Compression+結合→Overlap/Value QA(Stage 2-3のみ再実行、`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`既存値)→記事全体Fact Checker/Ledger+Local Rewrite+差分QA→Directional Precheck→OK/NG。Stage 1再生成条件=(a)Main Story側Ledger MAJORがLocal Rewrite上限(3)でも未解決/(b)Stage 2-3 exhaustion後の最終fallback 1回/(c)記事全体Fact Checker FAIL(簡略locusルール)。`STAGE1_MAX_REGENERATIONS`=案1(1回)推奨(最悪でもMain Story生成コスト約2倍、案2=2回は約3倍・多重retryリスク、案3=0回は設計要求放棄)。Main Story固定原則の仕様文案(Stage 2-3では原則不変、Local Rewrite等既存安全装置の局所修正は例外・差分QAで再検証)。Fact Checker FAIL locus=案(ii)簡略ルール推奨(案(i)厳密分類はFAIL未発火で`locate_target_sentence`整合未検証)。既存QA整合表・News/Trend競合なし(P1)・共通ヘルパー化方針。Dangling Reference: Trial実装は`er011_discovery_stage3_rule_adjustment_trial_09.CURRENT_FOCUS_BLOCK`・S2 Trial関数群・Trial専用パーサーに依存→Production化時は`EDITORIAL_TYPE_MODULE_BLOCKS`へ正式登録+関数の正式移設で依存を切る。Gate 3準備: 分岐テスト6ケース/バイト不変テスト/統合テスト/runtime evidence(意図的MAJOR Ledgerで Stage 1 escalation実発火、概算¥40〜60/本)。Gate 2判断事項5件(分割方式/`STAGE1_MAX_REGENERATIONS`値/locus分類/Trial専用ファイルの扱い/実装着手可否と費用)。根拠: `FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01_REPORT.md`(commit 7ea4d5d)。」
### DECISION_LOG.md 新規エントリ(`## 参照元`直前)
「## PM-CLOSEOUT-CONSOLIDATION-122(2026-09-13)
FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01: ユーザー判断「S2について追加Trialを先に増やさず、Production設計フェーズへ進むことを承認しました。ただし、これはまだProduction実装・配線承認ではありません。現在StatusはVALIDATED→Production設計着手可であり、APPROVED_FOR_PRODUCTIONではありません。(中略)設計完了後にGate 2としてユーザー判断を求めてSTOPしてください。」に基づき¥0で設計完了。内容は上記OPEN-135追記のとおり。Status: `USER_DECISION_REQUIRED`(Gate 2、判断事項5件)。実装・配線・CURRENT_SPEC正式化なし。commit 7ea4d5d。」
索引行: CONSOLIDATION-121索引行と同形式で1行。

## 実行コマンド全文
- `.venv\Scripts\python.exe docs/pm/tools/collect_subagent_transcripts.py --help`→表示引数で退避: taskId `a2a55002a598ea8a3 a8f7888bd509a4165 acd3a35828bd1ac88`(tasks dir=`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks`、subagents dir=`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents`)
- `git status --porcelain`

## Git
明示`git add`: `OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-122*`、`docs/pm/transcripts/`追加分。コミットメッセージ`PM-CLOSEOUT-CONSOLIDATION-122: Discovery S2 Production設計(Gate 2判断待ち)のSSOT反映+F-1退避`、末尾に
```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4
```
`git push origin main`まで(拒否時はエラー原文を報告し回避しない)。

## 報告
`docs/pm/RESULT_PACKET.md`へ10行以内: commit hash/push結果、SSOT追記位置、T-0検証結果、退避結果、一覧外操作の有無。最終メッセージ6行以内。
