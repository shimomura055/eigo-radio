# PREVENTION_01
## 主因
background実行されたPython(対話モード/stdin無し)が終了せずWinError 123のトレースバックを無限出力 → Claude Codeのtask出力ファイルが上限5.37GBまで肥大(9本)。終了後も出力ファイルは自動削除されず、セッション横断で44GB蓄積。
## 実装済み(他へ未配線、API 0)
- tools/disk_space_check_01.py: 空きGB表示、--min-gb未満でrc=2。
- tools/claude_task_output_cleanup_01.py: A1/A2規則、dry-run既定、--applyで削除。
## 提案(未実装・要Fable/ユーザー判断)
1. 起動時/タスク開始時にdisk_space_check_01を呼ぶ(軽量・1秒未満)。閾値10GB目安。
2. 週次または日次で cleanup_01 --apply を手動/スケジュール実行。
3. background起動のPythonに`python -u script.py < /dev/null`を徹底し、`python`単体の対話起動を禁止(agent定義への注意書き案)。
4. 大出力コマンドは`| head -c`や`> file`で出力量を制限。
5. 完了済みscratch worktreeの回収手順を委任終了時チェックに追加。
agent定義・PM_GOVERNANCE・保存仕様・保持期間は変更していない。
