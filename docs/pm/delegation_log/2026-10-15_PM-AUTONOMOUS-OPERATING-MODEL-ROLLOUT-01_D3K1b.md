## 管理ID

`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` Day 3〜4 = 委任_K1b(Phase C 採点原文A班の保存。前委任_K1は長文貼付がモデル安全フィルタに誤検知されAPIエラー終了したため、**本委任では本文をプロンプトに含めず、採点者セッションの出力ログからスクリプトで抽出して保存**する)。記録専用・費用JPY0。SSOT不編集。並行: 委任_K2(B班)・委任_K3(C班+SSOT)。git `index.lock`衝突時は30秒待ち最大3回再試行。

## 重要な作業規律

- 抽出した本文を**自分のコンテキストに読み込まない**(`cat`/`Read`/`type`で表示しない)。Pythonスクリプト内で処理し、stdoutには文字数・先頭30字・末尾30字・行数のみ出す。これは安全フィルタ再発防止のため。
- 原文は1字も変えない(11-5 原文保存)。

## 手順

1. T-0: 本委任文を保存し、check_delegation_prompt.py を実行(FAILでも継続)。
2. 入力ログ: `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\tasks\a6be48b29e04d582d.output`(採点者=opus-consultant A班セッションのJSONL transcript)。まず`python -I`で構造のみ調査(値は表示しない)。
3. 抽出スクリプト(`C:\Users\tensh\eigo-radio-replay\_feasibility\extract_opus_text.py`、Repo外): assistant の text ブロック(またはSubagentHandback tool_use input)から、「Phase C 独立採点の結果です。採点者モデルは claude-opus-5-5 です」で始まり「合成シナリオとUC1の基準のみが書かれており、欠陥ケースと陰性対照の正解はRUBRICにあります。」で終わる最長ブロックを採点原文とする。両方あれば一致確認、不一致なら両文字数報告し長い方採用。見つからなければ候補先頭30字一覧(最大10件)のみ報告。
4. 出力: `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/BLIND_REPLAY_SCORING_01_A.md`。先頭3行(見出し・採点者行・逐語保存注記)+空行1+本文(UTF-8, LF)。
5. 検証: 読み戻し、sha256・文字数・行数・先頭末尾30字。
6. secret_scan --staged hits=0 → 明示add → commit「PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3 Phase C 委任_K1b: Opus採点原文A班(欠陥2+陰性1)を採点者ログからスクリプト抽出し逐語保存。JPY0」→ push origin/main。禁止: git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。
7. 報告: T-0結果/ログ構造キー名/抽出方法/sha256等/commit hash/raw URL/逸脱。本文は含めない。
