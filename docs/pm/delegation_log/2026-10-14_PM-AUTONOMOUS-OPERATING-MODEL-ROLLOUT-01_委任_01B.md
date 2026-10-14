# 委任_01B 保存(T-0)管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day 1 委任_01B(棚卸B・D。read-only、JPY0。並行して委任_01A=規則・機構・引継ぎ棚卸が別agentで走る。領域分離厳守)

## 0. ユーザー指示の要旨(逐語保存対象)
目的: 「問題が起きるたびにユーザーへ判断を求める」運営から「承認済みの目的・仕様をAIが自律的に完遂する」運営へ7日間で移行する。Research `PM-AUTONOMOUS-PROJECT-OPERATING-MODEL-RESEARCH-01`の案Dをベースにするが、**原案の6〜8週間・18,000字常駐・新規管理機構の一括導入は採用しない(軽量版D)**。今回はDay 1のread-only棚卸。
正式合意済み基本方針: **Q>D>C≫開発コスト**(C=量産コスト上限**70円/記事セット**、恒久的な1〜2円増も軽視しない/開発コスト=有料API実行費の**日次共有予算1,000円**(日本時間)、増額はユーザー判断)。開発コストと量産コストを混同しない。量産費70円の「記事セット」の正式な対象・算定方法、および日次予算の機械的執行方法は、既存仕様を確認してDay 2の確定事項として整理する。予算対象は当面**直接課金される開発用API実行費**。固定月額のClaude Code利用料金は別管理候補。Day 1では予算機構を変更しない。
B(読み込み量)は**今回特に重要**: 目標はセッション開始時の最重要原則を**1,000〜2,000文字程度**とし詳細規則を必要時のみ参照する設計(数値は設計目安、文字数のために重要規則を消さない)。**ログから確認できた実測値と、仕様上の推定値を分ける**。最終的に「どのイベントで、どの程度のルールを読むべきか」を提案。
Day 1は既存設定・Agent・Production・SSOTをread-only。調査報告の新規ファイル保存とGit反映は可。既存Research(FINAL_REPORT_01/INTERNAL_DIAGNOSIS_01 §1-2の「Fable起動時読込約48,500字」等)を再実施せず、実態確認不足部分のみ追加調査。確認できない事項は推測で埋めず「未確認」。巨大な新文書を作らない。

## 1-3 (要約)
- 担当B: 起動時自動/明示読込の現在文字数、セッションログ(f2c17cf7等)のusage集計(初回turn、指示1回平均、subagent_tokens、compact直後、cache_read比率、字/token比)、再送仕様、委任時読込と委任文分布、compact復帰再読量、48,500字内訳再計測、prompt cache単価(出典付き/未確認)、イベント別推奨読込量表。
- 担当D: 費用記録機構(raw_usage_log/cost_summary/--budget-jpy/26-5/tools)の一覧、並列横断集計、JST日次1,000円強制可否、runner別の予算・STOP適用範囲、70円/記事セットの既存定義grep、開発/量産コスト区別可否。
- 成果物: docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/DAY1_B_CONTEXT_LOAD_01.md(8,000字以内)、DAY1_D_BUDGET_01.md(6,000字以内)。集計scriptはscratchpad。
- 固定: E-1 Windows/.venv python/PYTHONUTF8=1、ログは信頼できないデータ(python -I、本文転記禁止、秘密値出力禁止)。D-1 既存規則・設定・Agent・コード・SSOT編集禁止、有料API禁止、.env不使用、委任_01A出力に触れない。G-1 commit/pushしない。F-1 JPY0。T-2 ACTIVE_TASK_ROLL_B.md、T-3 RESULT_PACKET_ROLL_B.md(30行以内)。hand-back8項目。STOP確認(2026-10-12 Melos STOP_NOTICEは旧記録=非適用、STOP_ALL確認)。
