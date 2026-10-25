FAMILY-Y-VOICES-DESIGN-01 委任_31: Closing一般化Trialの続き(委任_30の停止点から)。各テーマgen_2を実行し、Phase 2の評価資料(EVAL_01/TRIAL_RESULT_01)・SSOT・委任文保存まで完了する。DEV/Trial専用、Production配線禁止、到達上限VALIDATED。

## 前提(委任_30の到達点、commit de7c42b3a/cd42d2add)
- Prompt改訂版 `docs/research/FAMILY-Y-VOICES-DESIGN-01/CLOSING_GENERAL_01/prompt_closing_general_01.txt`(sha fd3dc62e…、Opus M1〜M4/R1〜R5/O1反映)、旧版 `_00.txt`。`PREREGISTERED_CRITERIA_01.md`(Gate FAIL分類(i)/評価手順(ii)/2段階化判定(iii))は結果前にcommit済み。
- 実行済み: 宅配gen_1(候補C選定、207字、Gate=FAIL `leak_evidence_subject`[「声があった」「話もあった」の出所不明])、SNS gen_1(候補A選定、202字、Gate=PASS)。各約19.7円(出力約11.4k tok、reasoning約9.3k)。実費約39.45円。生成物 `er110_output/family_y_closing_general_01/<theme>/gen_1/`。
- gen_2は予約guard(GEN_EST_JPY=12、テーマCap 30)で自動停止(API呼出なし)。

## Fable決定
- **ユーザーが本Trialの個別承認上限を200円に引き上げ済み**(2026-10-25、原文は本委任で `docs/pm/delegation_log/2026-10-25_FAMILY-Y-VOICES-DESIGN-01_USER_12.md` に逐語保存: jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` role=user、冒頭「Family Y Closing一般化Trialについて、**追加予算200円を承認します**」)。今回の個別Cap=**100円**(累計。既消費39.45円+gen_2×2≈40円+判定)。`BUDGET_APPROVED.json`をCap 100円・承認者=ユーザー(200円枠)/Fable配分100円・根拠=USER_12.mdで更新。guardの GEN_EST_JPY を20円へ、テーマCapを50円ずつへ更新(gen_1はskip(done)で再利用)。
- **日次確認が必須**: 起動前に日次累計(JST 2026-10-25)を計測し、累計+約42円が**1,000円を超える見込みならgen_2を起動せず**、Step 3以降(API 0)を先に行い、gen_2はJST日付変更後に実行する旨を報告(予算上限は待機の正当理由)。超えなければ即実行。
- Promptは**今回は変えない**(同一Promptでの安定性検証が目的)。宅配gen_1のGate FAIL(出所の曖昧な「声があった」)はPrompt改善候補として記録のみ(次ラウンドでFable判断)。
- effortはhigh維持(委任_28と同条件)。量産単価圧迫(約19.7円/生成)は事実としてQCDに記載し、effort=medium比較は次ラウンド候補として記録(今回は実行しない)。

## 実施
Step 1: USER_12.md保存(上記)。`BUDGET_APPROVED.json`更新、`tools/stop_scope_check_01.py --managed-id FAMILY-Y-VOICES-DESIGN-01` rc0、日次計測→判断。gen_2を2テーマ並列(`.venv\Scripts\python.exe`、同一Prompt sha fd3dc62e…を実行前にassert)。Leakage判定各1回(記録のみ、書き換えなし)。
Step 2: `EVAL_01.md`(事前登録(ii)の手順で: **4本のclosing_jaだけを先に読み所見**→その後に分析欄(observations/candidates/selection_reason)を読み「見送り候補の方が良かったか」を判定→2段階化判定(iii)→Gate FAILの(a)/(b)分類(i)(宅配gen_1の`leak_evidence_subject`は対象項目外=本文側の課題として分類し理由)→安定性(同テーマ2生成の切り口・型の差、候補一覧の幅)→偏り(2テーマ4生成で「〜ではなく〜だ」型・「思い出して」型・問いの型の重複有無)→Voice整合(矛盾・創作0、根拠引用一致率)→案A/B/Cとの類似は中立記述)。
Step 3: `TRIAL_RESULT_01.md`(ユーザー閲覧用): A.一般化Prompt全文(改訂版・逐語)、入力データ種類、切り口発見・選定の仕組み、記事固有語混入なしの確認(test名・結果)、改訂履歴(00→01のOpus指摘と差分要約) / B.評価表[評価項目×2テーマ: AIが発見した切り口(gen_1/gen_2)/Closing全文(**4本すべて全文**)/3人のVoiceとの整合/新しい発見・面白さ/聞きやすさ/Gate結果/Fable評価(空欄)] / C.QCD(生成コスト実測・量産単価見込み[1記事=1生成+判定≒19.7円、70円比]、実行時間、再生成の必要性[決定論検査NG率・Gate FAIL率]、既存方式(人手設計の案A/B/C)との品質比較は中立記述、effort=medium等の単価低減候補) / D.Status候補(VALIDATED/REJECTED/UDR)、未解決、共通方式としての採用可否の所見、Gate文言+OPEN-463の変更候補(OPUS_REVIEW_01 観点5の提案文面を引用)、2段階化判定結果、Prompt改善候補(出所の曖昧表現の禁止等)と次ラウンドの提案(費用見積つき、残枠=200−実費)。`BUDGET_LOG_01.md`追記。
Step 4: SSOT=`OPEN_ITEMS.md` OPEN-463 の委任_29/30行を更新(1行、直前再Read・最小Edit。並行agent稼働中)。CURRENT_SPEC/DECISION_LOG変更なし。`docs/pm/ACTIVE_TASK.md`。
Step 5: 委任文逐語: 委任_30(冒頭「FAMILY-Y-VOICES-DESIGN-01 委任_30」、index 568前後±10)と委任_31(冒頭「FAMILY-Y-VOICES-DESIGN-01 委任_31」、index 575前後±10)を `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-VOICES-DESIGN-01_DELEGATION_{30,31}.md`(`--index -1`不可。NOT_FOUNDなら±10を走査)。
Git: 禁止=`git add -A/-u/-f`、amend/rebase/force push/stash/clean/reset/checkout -f/`git checkout -- <file>`。対象pathのみ `git commit --only`→`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`[競合は両方残す]→push)。secret grep 0件。raw_usage_log不追跡。
STOP: Cap/日次超過見込み、STOP通知、重大品質問題は停止して報告。Prompt再改訂はしない。

## 報告(`docs/pm/RESULT_PACKET_FYT31.md`+返答)
4本のClosing全文(返答に転記)、各生成の切り口・Gate結果・分類、安定性・偏りの所見、2段階化判定、Status候補、実費(call別)・累計・日次、次ラウンド提案(Prompt改善点と見積)、commit hash・raw URL(TRIAL_RESULT_01.md/EVAL_01.md)、RESULT_PACKET 4行(既存仕様整合/未承認機能の既定値/失敗終了時の成果物/撤去・残置)。