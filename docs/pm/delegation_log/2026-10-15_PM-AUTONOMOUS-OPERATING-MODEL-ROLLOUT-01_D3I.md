# 委任_I(Day3-4 Phase B-0) 受領委任文(実行層Sonnetによる保存。主要部は逐語に近い要約、固定ブロックは定型要約)

## 管理ID
`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` Day 3〜4 = 委任_I(Phase B-0: 盲検リプレイをFableが自律起動するための小規模実動作確認。被験本番は起動しない)。ユーザー正式決定①(2026-10-15): 盲検リプレイは原則としてFable自身が隔離環境から被験セッションを起動し、独立したOpusに採点させる。ただしまず、`claude -p`等の実際の起動可否/Fable・Sonnet・Opusの実際のモデル・ルーティング/課金経路と費用上限/ツール権限・委任機能の動作/被験者と採点者の独立性/期待値・採点基準の漏洩がないこと/元のProduction Repoや秘密情報へアクセスできないこと、を確認する。安全性が確保できる方法をFableが選択してよい。`claude -p`で必要な検証委任ができない場合は対話セッションの自律起動等の代替を検討する。直ちにユーザー手作業へ戻さず自律的に解決可能な方法を調査する。既存の安全Gate・承認Gateは迂回しない。並行: 委任_H(Repo内の規則・SSOT編集)。本委任はRepo内では`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/REPLAY_FEASIBILITY_01.md`と`docs/pm/delegation_log/`のみ新規作成。index.lock衝突時は30秒待ち最大3回再試行。

## 性質/到達上限/禁止事項
- 実動作確認。到達上限: `REPLAY_FEASIBILITY_CONFIRMED`または`REPLAY_FEASIBILITY_BLOCKED`(理由付き)。
- 費用上限: 子セッション合計USD 1.0(約JPY150)相当をGuardrail(各起動`--max-budget-usd`)。到達・接近時は5条件(scope内/原因把握済み/異常retryでない/残作業明確/追加費用合理的)で超過を記録して継続可、暴走疑い時のみSTOP。課金経路が「API key従量」と判明し1セッション見積がUSD 1超なら、本番17セッションの見積(USD・JPY)を出してSTOP(7-9)。subscription経路ならその旨とレート制限見込みを記録。
- 禁止: 被験本番セッション(欠陥ケース2・陰性対照1・合成14)の起動、`C:\Users\tensh\eigo-radio-replay\`配下パッケージ内容(defect_case/negative_control/synthetic/rubric/_scorer_only)の変更(修正案は`runbook/*_v2`別名保存)、採点基準・期待値の転記、`.env`・APIキー値の出力、`~/.claude/settings.json`変更、git add -A/-f・amend・rebase・force push・stash・clean・reset --hard・checkout -f。時間見込み約1.0h。

## 固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(定型)
T-0: 本ファイルへ委任文保存+`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行。T-2: TTSなし。T-3: 上記Guardrail。

## 事前指定Read
BLIND_REPLAY_RUNBOOK_01.md全文 / RUN_SESSION.ps1・subject_settings.json(TASK_*.md・_scorer_only・rubricは読まない) / .claude/agents/{sandwich-pm,sonnet-worker,opus-consultant,haiku-worker}.md:1-6 / `~/.claude/settings.json`・Repo `.claude/settings*.json`(キー有無のみ)。

## 確認項目(結果をREPLAY_FEASIBILITY_01.mdへ)
1 起動可否 2 モデル・ルーティング・委任機能 3 課金経路 4 ツール権限・隔離 5 独立性・漏洩 6 ログ分離・並列 7 規則読込 8 判定(推奨起動方式・雛形・費用見込み・リスク)。実行コマンドは付録に逐語記録。

## 実行コマンド全文(要約)
T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <本ファイル> --json-out <本ファイル>_check.json` / 安全確認: `RUN_SESSION.ps1 -CheckOnly` / git: `git status --porcelain -- <対象>`、`git log --oneline -3`。

## Git
明示add: REPLAY_FEASIBILITY_01.md、本ファイル(+_check.json)(RESULT_PACKET_ROLL3Iも報告先)。probe出力・パッケージはadd禁止。push to origin/main。

## 報告
`docs/pm/RESULT_PACKET_ROLL3I.md`へ(1)T-0 (2)7項目結果表 (3)課金経路判定と17セッション費用見込み (4)委任機能の可否 (5)transcript保存先 (6)v2差分 (7)commit/push/raw URL (8)未確認事項・STOP有無 (9)Fable向け推奨方式と雛形。Fableは(2)(3)(4)を照合する。
