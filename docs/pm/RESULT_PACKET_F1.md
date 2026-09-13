# RESULT_PACKET_F1: PM-TOKEN-EFFICIENCY-F1-ZERO-BYTE-TRANSCRIPT-ROOT-CAUSE-01

- 性質: 原因特定(¥0)。Production/SSOT変更なし。Sonnet往復1回で完結。
- 原因: `tasks/<taskId>.output`はharness内部の完了時書き込みが約35%の確率で
  発生しない不具合(タスク開始時に空作成→そのまま放置)。単発クラッシュではなく
  全期間に分散した継続的な確率的不具合。
- 代替保存元発見: `<projectDir>/<sessionId>/subagents/agent-<taskId>.jsonl`に
  Claude Code標準の逐次追記ログとして完全なtranscript(usage含む)が存在。
- 検証: 0バイトのsubagent委任102件(a接頭辞)中102件(100%)が代替保存元から
  復元可能。直近10委任は10/10復元・確認済み。本タスク自身の委任でも実行中の
  リアルタイム再現に成功(tasks側は終始0バイト、subagents側は272KB→346KB→456KBと成長)。
- b接頭辞4件(Background Bash出力キャッシュ)はF-1スコープ外、問題なし。
- 観測基盤回復: `docs/pm/transcripts/`内の既知0バイトプレースホルダー4件を
  代替保存元から復元し`_recovered.jsonl`として追加(既存ファイルは無編集)。
  合計6.88MB、JSONL整合性検証済み(不正行0)。
- 修正要否: repo/SSOT側の修正は不要かつ対象外(harness内部問題)。
- 施策1/2効果測定へ進める状態か: 条件付きでYes。今回の復元データ+汎用スクリプト
  (`docs/pm/tools/collect_subagent_transcripts.py`、dry-run既定、追加コピーのみ)
  で必要なtranscriptは取得可能。恒久的なF-1手順変更(代替保存元を正式な
  fallbackにするか)はUSER_DECISION_REQUIREDとして提案のみ、未実施。
- 詳細: `PM-TOKEN-EFFICIENCY-F1-ZERO-BYTE-TRANSCRIPT-ROOT-CAUSE-01_REPORT.md`(root)。
