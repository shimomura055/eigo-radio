# 委任_03c OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01

## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_03c: Opusレビュー分割ファイルの機械結合、OPEN_ITEMS整形、明示git add→commit→push)。コード・設計内容の変更なし。説明出力最小。Bash heredoc不使用。

## 性質/到達上限Status/禁止事項
性質: 記録整備+Git(¥0)。Status: USER_DECISION_REQUIRED(変更しない)。禁止: 残11 run/Production変更/`git add -A`/amend・rebase・force push/SSOT内容の変更(整形のみ可)/有料API。Opus Gate: 条件A済み。

## 固定ブロック
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力はcommit hash・push結果のみ報告。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を本ファイルへ逐語保存、check_delegation_prompt.py実行、結果1行を最終報告へ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
Git運用ルール: 意味のある変更はcommit→origin/main push。今回変更した対象ファイルだけを明示的にgit addし、git add -Aは使用しない。raw.githubusercontent.com URLを添える。

## 作業内容
1. 結合: docs/pm/opus_l2_review_open233_directional_misread_safety_01.md の末尾へ part1, part2, part2b, part3 をPowerShellで機械結合(順序 part1(U1-U3)→part2(U4)→part2b(F1)→part3)。
2. F1直後(「### F3」直前)へ3行追記(F2見出し・要旨・出典)。
3. Grep `^### ` で見出し順(総合判定/U1/U2/U3/U4/F1/F2/F3/F4/判断事項)確認。part1/part2/part2b/part3を削除。
4. OPEN_ITEMS.md L728: 委任_03bが表のセル外へ追記した進捗文を最終セル内(末尾`|`の前)へ移動(内容不変)。
5. git: 指定ファイルのみ明示git add、git status --shortで混入確認。
6. commit message 1行(系統的読み違い専用Safety設計完了ほか)。
7. git push origin main。

## 報告
最終報告6行以内: 結合見出し確認、OPEN_ITEMS整形結果、commit hash、push結果、T-0結果、raw URL 7件。
