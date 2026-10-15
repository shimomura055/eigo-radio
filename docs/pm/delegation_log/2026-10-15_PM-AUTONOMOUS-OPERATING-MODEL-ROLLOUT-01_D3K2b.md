# 委任_K2b 全文保存

## 管理ID

`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` Day 3〜4 = 委任_K2b(Phase C 採点原文B班の保存。前委任_K2は長文貼付がモデル安全フィルタに誤検知されAPIエラー終了し、途中切れファイルは削除済み。本委任では本文をプロンプトに含めず、採点者セッションの出力ログからスクリプトで抽出して保存する)。記録専用・費用JPY0。SSOT不編集。並行: 委任_K1b(A班、同方式)・委任_K3(C班+SSOT)。git index.lock衝突時は30秒待ち最大3回再試行。

## 重要な作業規律

- 抽出した本文を自分のコンテキストに読み込まない(cat/Read/typeで表示しない)。Pythonスクリプト内で処理し、stdoutには文字数・先頭30字・末尾30字・行数のみ出す(安全フィルタ再発防止)。
- 原文は1字も変えない(11-5 原文保存)。

## 手順

1. T-0: 本委任文を docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3K2b.md へ全文保存し、check_delegation_prompt.py を実行(FAILでも継続)。
2. 入力ログ: C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\tasks\afccb2ddcdc29e47b.output (採点者=opus-consultant B班セッションのJSONL transcript。全文表示禁止)。python -I で先頭数行のJSON構造(キー名・typeのみ)を確認。委任_K1bが C:\Users\tensh\eigo-radio-replay\_feasibility\extract_opus_text.py を作成済みなら再利用可(引数化)。無ければ自作し同pathに保存。
3. 抽出: message.role=="assistant" の content 内 type=="text" ブロック(またはSubagentHandbackのtool_use input本文)から、「## Phase C 独立採点: 合成7セッション(SC-C1〜C6・UC1)」で始まり、「`C:\Users\tensh\eigo-radio-replay\synthetic\wd_UC1\docs\pm\PM_GOVERNANCE.md`(2433-2446行)」で終わる最長ブロックを採点原文とする。複数候補があれば文字数を報告して最長を採用。見つからなければ候補の先頭30字一覧(最大10件)のみ報告。
4. 出力: docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/BLIND_REPLAY_SCORING_01_B.md。先頭3行(見出し、採点者行、逐語保存注記)+空行1つ+抽出本文(UTF-8、LF)。
5. 検証(スクリプト内): 読み戻して本文部分のsha256・文字数・行数・先頭30字・末尾30字をstdoutへ。
6. tools/secret_scan_01.py --staged hits=0 → 明示add(B.md、delegation_log 2件)→ commit → push。禁止: git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。
7. 報告: T-0/抽出方法/sha256・文字数・行数・先頭末尾30字/commit hash/raw URL/逸脱。本文は報告に含めない。
