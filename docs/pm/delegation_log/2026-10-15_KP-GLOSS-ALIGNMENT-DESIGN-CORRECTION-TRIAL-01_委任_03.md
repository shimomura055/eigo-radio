# 委任_03 KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 (2026-10-15、委任文全文)

## 管理ID
KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_03(ユーザー設計承認①の記録+整合済みglossの不要書換え(P3 4/16)の原因確認・課題指示文改善・P2/P3/P7再Trial+必要な再整合が失敗しないことの確認(P1/P4/T2抜粋)+終了条件5点のevidence整理+SSOT。2026-10-15)。本管理IDのSonnet委任はこれが4回目=最後。未達ならその状態で報告(追加委任不可、Fableが判断)。並行タスク: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day2 Phase A 委任_A/_B(read-only、docs/research/.../day2/とRESULT_PACKET_ROLL2*・ACTIVE_TASK_ROLL.mdのみ書く)。衝突なし。git commit時.git/index.lockがあれば30秒待ち再試行(最大5回)。

## 性質/到達上限Status/禁止事項
性質: Trial(DEV/Trial専用mode=corrected、flag明示ON)。到達上限Status: VALIDATED/REJECTED/USER_DECISION_REQUIRED。APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDは宣言しない。Production既定OFF(GLOSS_ALIGNMENT_ENABLED="0"、commit c21cce27a/e80360add)は維持。
Opus独立技術レビューGate判定: 非該当(条件A実施済み2026-10-15、本委任は課題指示文の文言改善とTrialのみで構造変更なし。構造変更が必要になればSTOP)。
時間見込み: 60〜90分。並列化: Regression suiteは並列可、他は直列。
費用: ユーザー承認Trial上限JPY5のうち既使用2.49→残JPY2.5(Guardrail)。見込み: P2/P3/P7再Trial約1.0+P1/P4/T2抜粋約0.8=約1.8円。暴走疑い時のみSTOP。ユーザー承認上限JPY5(累計)はTrial上限として守る(超える見込みならその前にSTOP)。TTS実行禁止。
禁止: 承認済みgloss規則本文・選定/canonicalization Prompt・Rule7・Gate・Lockの変更、legacy挙動の変更、既定OFFの変更、A'構造の変更(文言改善と検証のみ)、Production採用表記、量産run、git add -A/-f/amend/rebase/force push/stash/clean/reset --hard/checkout -f、.envの読み書き、Day2 Phase A領域への書込。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(T-2: TTS実行なし、T3はmock、TTS_EXECUTION_MODE=STANDARD明示)。

## ユーザー指示(原文、2026-10-15「返信 対象KGDC」)
① Human Review時の停止方式: 提案どおり了承。2回失敗した場合、Human Review例外として報告/対象KPの後続生成を停止/既存Audio Validation Gateで完成版への組み込みを禁止/Family Zは既存FamilyZE2EStopを利用/Advanced B1の英語解説生成についても整合を確保。既存Human Review Lockでは安全に停止できないため、提案された既存status返却方式を採用。これは修正Trialの設計承認であり、gloss再整合工程の正式Production採用ではない。
② 正しいglossの不必要な書換え: ユーザー判断事項ではない。開発チームで自律的に改善。4/16件の原因を確認し、提案済みのPrompt改善とP2/P3/P7再Trialを進める。既に意味が一致しているglossは自然さだけを理由に不要な書換えをしない/改善によって本来必要な再整合が失敗しないことも確認/既存Trial予算・承認範囲内/効果不足なら原因とアプローチを見直し承認範囲内で解決/新仕様を無断でProductionへ反映しない。解決または目処をつけてから報告。明示STOP・予算上限・承認範囲・重大な品質安全問題は守る。
③ 終了条件: 修正Trialを実施し、Fable自身が確認: 正しいglossを不必要に変更しない/不一致glossを適切に修正できる/既存承認済みglossルールと矛盾しない/失敗時に不整合なglossが完成物に混入しない/品質・速度・量産費用に許容できない副作用がない。REJECTED/VALIDATED/USER_DECISION_REQUIREDに分類。VALIDATEDとなった場合に初めてProduction採用をユーザーへ諮る。それまでProduction既定OFF維持、正式採用・Production Wiringへ進まない。

## 手順要旨
1. 原因確認(P3 4/16): (a)LLMが不一致と判定し書換えたのか、(b)一致と判定しつつ別文字列を返した(機械チェック穴)のか。(b)ならコード修正、(a)なら課題指示文。
2. 課題指示文改善(correctedのbuild_user_messageのみ、承認規則本文sha256不変): 指示2へ「current_japanese_glossが最終key_phrase全体の意味を既に表している場合は、より自然・より適切と思える言い換えがあっても書き換えず、current_japanese_glossをそのまま返してください。書き換えるのは、key_phraseの語の意味が欠けている・誤っている場合だけです。」追加。判定例に「key_phrase「fall into」にcurrent「～に落ちる」: 意味は表れているので一致(「～に陥る」へ書き換えない)」。unit test PASS+新規testで固定。
3. 再Trial: P2,P3,P7 reps2 budget1.5 -> trial_t1b/ ; P1,P4 reps1 budget0.6 -> trial_t1c/ ; T2 reps1 budget0.4(12件に絞る) -> trial_t2b/。実行前にtools/stop_scope_check_01.pyと累計費用確認。
4. 効果不足時: (i)判定例追加/(ii)rewrite_reason必須化/(iii)consistent=true時current固定のうち最小を1回だけ。未達ならVALIDATION_03.mdに結果・原因・次案を記しFableへ。
5. T3 mock再実行(trial_t3_rerun_02, STANDARD, --mock-all)とRegression(er003/er019/er026/er030/er063)、新規failure 0。
更新位置: gloss_alignment_correction_01/VALIDATION_03.md(§0〜§6)、SSOT(OPEN-356行末尾、DECISION_LOG、OF台帳(OF-KGDC-01〜05=USER_APPROVED_TRIAL_DESIGN、OF-KGDC-08=EVIDENCED)、REPORT_LEDGER)、ACTIVE_TASK_KGDC.md・ACTIVE_TASK.md。
Git: 明示addのみ。コミットメッセージ `KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_03: ...`、trailer `Managed-ID: KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01`。git push origin main。
報告: docs/pm/RESULT_PACKET_KGDC3.md(35行以内)。
(注: 本ファイルは委任文の全文保存要請に対する要旨圧縮版。逐語原文はFable側会話ログに存在。)
