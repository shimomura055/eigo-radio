FABLE-DELEGATION-MARKER: PM-CLOSEOUT-MEANS-VS-GOAL-RULE-01-委任_01-20261023

# 委任_01: PM判断プロセス是正(ユーザー指示 2026-10-23 §6)— Trial Closeoutで「手段の成否」と「目的の達成」を区別する規則をPM_GOVERNANCE・Fable運用へ必要十分に組み込む(過剰な新Gate・報告工程は設けない)。API 0、コード変更0。

## 背景
Key Phrase品質改善で、Fableが「A-3 v3(手段)の不採用推奨」をもって品質課題(目的)の解決・終了と取り違え、記事Bの最終承認保留に対し「現行維持」を推奨した。ユーザー指示原文=`docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_03.md`(委任_06 agentが保存中。数分待って読む。未着なら自分でjsonl最新userメッセージ「# 指示｜Key Phrase意味・説明品質の根本改善継続とPM判断是正」を同パスへ保存、衝突時は委任_06側を正)。§6「PM・Fableの判断プロセス是正」が対象。

## T-0
委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_PM-CLOSEOUT-MEANS-VS-GOAL-RULE-01_委任_01.md`(index 377以降、先頭MARKER一致)。ACTIVE_TASK自分の行のみ(並行: KP 委任_06、ASR PN/UKUS実装。pythonは自分のPIDのみ終了可。commitはpath限定+`git diff --cached --name-status`確認)。

## 実施
1. 既存規定の照合(Grep、全文読込禁止): PM_GOVERNANCE の Trial Closeout/PM Closeout Mandatory Check/11-6(問題解決運用: 解決見込みで再委任・再計画)/11-8(不具合判定)/29節(8原則の運用)/9節(報告フォーマット)、CLAUDE.md原則1・4・5、`.claude/agents/sandwich-pm.md`(あれば)のCloseout記述。「手段REJECTED→目的未達でもCloseしない」が既に含意されている箇所と、欠けている箇所を特定。
2. 最小追記(新節番号は既存の採番規則に従う。例: 11-9 または Closeout節の1項目追加):
   - Trial Closeoutでは必ず「手段の成否(試した仕様・Promptが有効だったか)」と「目的の達成(ユーザーが求めた品質問題が解消したか)」を分けて記載する。
   - 手段がREJECTED/不採用でも、目的未達なら改善タスクをCloseせず、原因・アプローチを見直して承認範囲内で継続する(効果のない手段の反復は停止)。品質未達を「現行維持」「仕様不採用」で終了処理しない。
   - ユーザー向け報告の「現在の状態」には目的達成度(達成/部分達成/未達)を明記。
   - RESULT_PACKET/Fable受入判定の既存4行目「失敗終了時の最終成果物と目的要件への適合」との関係を1文で接続(重複新設を避ける)。
   - 新Gate・新報告工程は作らない(既存のCloseout項目への1〜3行の追記で済ませる)。
3. `.claude/agents/sandwich-pm.md` または Fable向け運用文書にCloseout記述があれば同趣旨1行追記(無ければPM_GOVERNANCEのみ)。CLAUDE.mdは変更しない。
4. DECISION_LOG(是正の経緯: 事象・ユーザー指示・追記内容)、REPORT_LEDGER、OPEN新規行(PM-CLOSEOUT-MEANS-VS-GOAL-RULE-01、Status=REFLECTED)。
5. commit(path限定)、secret_scan hits=0、`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_PMCG1.md)
照合結果(既存で含意されていた箇所/欠けていた箇所)、追記全文(逐語)、commit・raw URL。RESULT_PACKET 4行+「判定整合: 重大NG=なし」。