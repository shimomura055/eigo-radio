# ACTIVATION_PROPOSAL_01 (設定ファイル案。本委任では未適用=委任_02でOpus安全レビュー後に有効化)

## (a) SessionStart hook: `.claude/settings.json`(プロジェクト共有、gitは `.claude/settings.json` を管理)
```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command",
        "command": "C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\tools\disk_guard_01.py --auto --quiet",
        "timeout": 30 } ] }
    ]
  }
}
```
OK経路は実測0.14〜0.5秒・出力1行。<20GB時のみ走査(実環境約15秒、worktree git status)。hook rc!=0(WARN/CRITICAL)でも作業は止めない(通知のみ)運用とするか委任_02で確認。

## (b) Worker開始手順: `.claude/agents/sonnet-worker.md` 100行目付近(stop_scope_check記述の直後)へ1行追加案
`- 作業開始時と有料run開始前に、`tools/disk_guard_01.py --auto --quiet` を実行し、rc=2(CRITICAL)なら新規の長時間/有料処理を始めずFableへ報告する(rc=1は警告のみ)。`

## (c) 長時間/有料処理の前: 既存のrunner前チェック列(stop_scope_check呼出の隣)へ同コマンドを追記。

## (d) Windowsタスクスケジューラ(管理者不要・常駐なし)
```
schtasks /create /tn "eigo-radio-disk-guard" /sc daily /st 04:00 /rl LIMITED /f ^
 /tr "C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\tools\disk_guard_01.py --auto --quiet"
```
PC電源OFF時は次回ログオン時にSessionStart/タスクの「見逃し実行」(`/it`不要、`StartWhenAvailable`はXML設定)で補う。

## 除外リスト運用
Fableが保持したいworktreeを `<scratchpad>\.disk_guard_keep` に1行1path(相対可)で追記(例 `wt_fix1`)。
