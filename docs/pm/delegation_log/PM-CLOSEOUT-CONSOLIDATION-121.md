## 管理ID
PM-CLOSEOUT-CONSOLIDATION-121(UDR候補Reconciliation)

## 範囲
性質: read-only照合+SSOT追記(表記の是正のみ、意味変更なし)+Git。¥0、API呼び出しなし。Productionコード無編集。並行タスクなし。禁止: `git add -A`/`stash`/`amend`、既存行削除、新規判断語の付与(判断はFableが確定。本タスクは「DECISION_LOGに既決の記録があるか」の事実照合)。

## 固定ブロック
---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0: 本委任文を`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-121.md`へ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-121.md" --json-out "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-121_check.json"`を実行し結果をRESULT_PACKETへ1行記録(FAILでも継続)。
---

## ユーザー指示(原文)
> 既決事項を再度ユーザーへ確認しない。OPEN-121の古い残件表記をReconciliationする。(2026-09-13)ユーザーへ上げるOpen Itemの基準を是正する: 8分類し「今ユーザー判断が必要」のみ提示。

## 背景
CONSOLIDATION-120の機械棚卸し(文字列ベース)で「今ユーザー判断が必要」候補としてOPEN-106/120/124/132/133/134/135/147が挙がった。135/147は本日のTrial結果に基づく真のUDR(Fable確定済み)。残り6件(106/120/124/132/133/134)は、既決事項の表記が古いままの疑いがあるため、DECISION_LOGの決定記録と突合する。

## 事前指定Read一覧
- なし(すべてGrepで該当範囲のみ)

## 事前指定Grep一覧+追記位置・更新位置の手順
1. `OPEN_ITEMS.md`: 各ID(106/120/124/132/133/134)について Grep `-n` `^\| OPEN-<ID> \|` で範囲(次の`^\| OPEN-`行の直前)を特定し、範囲の**末尾600字**を`-o`(`.{0,600}$`)で取得。ここに含まれる管理ID・日付・Status語を記録。
2. `DECISION_LOG.md`: 各IDについて Grep `-n -o` `OPEN-<ID>.{0,200}` の**最新5件**(行番号の大きい順)を取得し、ユーザー決定(「ユーザー判断」「決定」「承認」「defer」「保留」「不要」「採用しない」等)の有無と内容を抽出。加えてOPEN-120は`3V Fact Safety|追加Trialは不要`、OPEN-132は`Phase1b|PHASE1B|3V.*配線`、OPEN-106は`試聴|完成音声|USER_LISTENING`、OPEN-124/134は各IDの要旨語をGrep(要旨語は手順1の末尾600字から取る)。`DECISION_LOG_HISTORY.md`も同じパターンで各1回Grep(古い決定の所在確認)。
3. 分類(事実ベース、Fableが最終確定): 各IDを (A)「DECISION_LOGにユーザー決定の記録あり→既決/defer(OPEN_ITEMS側の表記が古い)」/(B)「決定記録なし→真に未処理」/(C)「自然発火・観測待ち(判断不要)」のいずれかに、根拠(DECISION_LOG行番号+引用20字)付きで表にする。
4. (A)に該当するIDは、OPEN_ITEMS該当行末尾へ「**Reconciliation(2026-09-13、CONSOLIDATION-121)**: 本件は<DECISION_LOG管理ID/日付>でユーザー既決(<決定内容20字>)。Status表記を<既決/DEFERRED/観測待ち>へ整理、ユーザー判断待ちではない。」を追記(意味変更なし、既存文不変)。(B)(C)は追記しない。
5. `DECISION_LOG.md`: Grep `-n` `^## PM-CLOSEOUT-CONSOLIDATION-120|^## 参照元`(本文追記位置=`## 参照元`直前)。索引行は`CONSOLIDATION-120`索引行の直後。追記文: 「## PM-CLOSEOUT-CONSOLIDATION-121(2026-09-13)\nUDR候補Reconciliation: CONSOLIDATION-120の文字列棚卸しで挙がったOPEN-106/120/124/132/133/134について、DECISION_LOGの決定記録と突合し分類(表)。(A)既決・表記古い=<ID列挙>、(B)真に未処理=<ID列挙>、(C)観測待ち=<ID列挙>。(A)はOPEN_ITEMSへReconciliation注記を追記(意味変更なし)。最終確定はFable。」+索引行1行。

## 実行コマンド全文
- `git status --porcelain`

## Git
明示`git add`: `OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-121*`。コミットメッセージ`PM-CLOSEOUT-CONSOLIDATION-121: UDR候補6件のReconciliation(既決表記の整理、意味変更なし)`、末尾に
```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4
```
`git push origin main`まで(拒否時はエラー原文を報告し回避しない)。

## 報告
`docs/pm/RESULT_PACKET.md`へ20行以内: 分類表(ID/要旨15字/分類A・B・C/根拠[DECISION_LOG行番号+引用]/Bの場合に必要なユーザー判断の要旨)、追記位置、T-0検証結果、commit hash/push、一覧外操作の有無。最終メッセージ6行以内。
