管理ID: PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01(Fable Gate 3差し戻し1回目)+PM-CLOSEOUT-CONSOLIDATION-118
性質: 検証+軽微是正(¥0、API呼び出しなし)。Productionコード(er0*)無編集。並行中のTrialタスク(`FAMILY-A-DISCOVERY-*`、`er011_*`、`EDITORIAL-FUTURE-*`、`er013_*`)のファイルには触れない。`git index.lock`があれば10秒待ち最大3回。

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0: 本委任文を`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-118.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-118.md" --json-out "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-118_check.json"`を実行し結果をRESULT_PACKETへ1行記録(FAILでも継続)。
---

## 差し戻し理由(Fable)
直前タスクのRESULT_PACKET_W1で「`python run_project_regression.py`(default全件)は485件中371 passed/7 failed/107 errors」と報告されたが、本日の他タスクでは同コマンドで collected=2509〜2512/failed=3(既知無関係)が一貫して観測されている。107 errorsは実行環境・cwd・Python差の疑いが強く、Gate 3項目4(Regression PASS)は未確認扱い。確認が取れるまで`PRODUCTION_WIRED`判定は保留。

## 事前指定Read一覧
- `docs/pm/RESULT_PACKET_W1.md`(全文、1回)
- `docs/pm/templates/DELEGATION_READ_EFFICIENCY_BLOCK.md`(全文、1回)

## 事前指定Grep一覧+更新位置手順
1. `docs/pm/PM_GOVERNANCE.md`: Grep `-n` `F-1: transcript退避|Sonnet/Opusは対応不要|D-2` で、固定ブロックを転記した箇所の行番号を特定→F-1行のみ下記文言に置換(他行不変)。
2. `DECISION_LOG.md`: Grep `-n` `^## PM-CLOSEOUT-CONSOLIDATION-117|^## 参照元`(本文追記位置=`## 参照元`直前)、索引行は`CONSOLIDATION-117`索引行の直後。
3. `OPEN_ITEMS.md`: Grep `-n -o` `^\| OPEN-142 \|.{0,200}`(行番号のみ。追記は末尾400字を`-o`で確認してから末尾へ)。

## 実行コマンド全文
- `cd C:\Users\tensh\eigo-radio; python --version`
- `cd C:\Users\tensh\eigo-radio; python run_project_regression.py`(default全件。collected/passed/failed/errorsを記録。errorsが0でない場合、errors上位5件のテスト名と例外種別を記録し、前回107 errorsの原因[cwd/環境]を特定する。`docs/pm/tools`配下からの実行など環境差が原因なら再現して証明)
- `cd C:\Users\tensh\eigo-radio; python -m unittest docs.pm.tools.check_delegation_prompt_test_01 -v`(パッケージ化されていなければ `python docs/pm/tools/check_delegation_prompt_test_01.py -v`)
- `cd C:\Users\tensh\eigo-radio; python docs/pm/tools/collect_subagent_transcripts.py --help`→表示引数で退避: taskId `a4368e132f7f81b1d a5fd1934fcf8fd679`(tasks dir=`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks`、subagents dir=`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents`)
- `git status --porcelain`

## 是正内容
A. 固定ブロックF-1の文言を「F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。」に変更(`DELEGATION_READ_EFFICIENCY_BLOCK.md`、`DELEGATION_STANDARD_TEMPLATE.md`内の転記、PM_GOVERNANCE D-2の転記の3箇所を同一文言に)。理由: 直前タスクで「委任文の退避コマンド」と「F-1」が矛盾と解釈され退避が未実施になったため。
B. `docs/pm/tools/README.md`の「`run_project_regression.py --pattern`が`docs/pm/tools/`を再帰探索しない」注記に、正しい直接実行コマンドを併記。

## SSOT追記文
- DECISION_LOG `## PM-CLOSEOUT-CONSOLIDATION-118(2026-09-13)`: 「PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01 Gate 3再検証: 直前報告の全件回帰(485件/107 errors)は[特定した原因]によるもので、repo rootからの再実行結果は collected=<n>/passed=<n>/failed=<n>/errors=<n>(失敗は既知無関係<件数>)。Gate 3項目4を<充足/未充足>と確定し、最終Status=<PRODUCTION_WIRED/APPROVED_FOR_PRODUCTION(未充足: 項目4)>。固定ブロックF-1文言を是正(退避指示との矛盾解消)。」+索引行1行。
- OPEN_ITEMS OPEN-142末尾: 上記Status確定の1文。
- CURRENT_SPEC: 直前タスクが「第32弾(冒頭)」に書いたStatus語が最終Statusと一致するかGrep `-n` `委任文標準|D-2`で確認し、不一致なら該当行のみ修正。

## Git
明示`git add`: `docs/pm/templates/DELEGATION_READ_EFFICIENCY_BLOCK.md`、`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`、`docs/pm/PM_GOVERNANCE.md`、`docs/pm/tools/README.md`、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-118*.md/json`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、(修正時)`CURRENT_SPEC.md`、`docs/pm/transcripts/`追加分。`-A`/`stash`/`amend`禁止、Trial系未追跡差分を含めない。コミットメッセージ`PM-CLOSEOUT-CONSOLIDATION-118: 委任文標準(D-2)Gate 3再検証(全件回帰の再実行)+F-1文言是正+F-1退避`、末尾に
```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4
```
`git push origin main`まで(拒否時はエラー原文を報告し回避しない)。

## 報告
`docs/pm/RESULT_PACKET_W1.md`を上書き(20行以内): 全件回帰の再実行結果と前回不一致の原因、Gate 3項目4の確定、最終Status、T-0検証結果、退避結果、commit hash/push、一覧外操作の有無。最終メッセージ6行以内。
