# 委任文(Fable→sonnet-worker)
管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_07(Trial-03 Fable独立評価の記録+UDR登録、API 0・コード変更0・Production変更0)

## 作業
1. `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/FABLE_EVAL_03.md` に以下を保存(EVAL_03.md末尾にも「Fable評価はFABLE_EVAL_03.md」と1行参照を追記):
```
# FABLE_EVAL_03 — Trial-03(Part 1・2改善)Fable独立評価(2026-10-25、委任_05/06成果、API 0)
- 対象: 『賢者の贈り物』/X『イグ・ノーベル賞2026』/Z『開いた窓』Advanced、最終Prompt=03d。Fableは03d第1標本3本と03c『賢者』を直接読んだ。
- Part 1: 3作品PASS。hand down=後輩への技能継承+判決を言い渡す用法、catch one's breath=忙しさから一息つく比喩、give way=圧力に屈する比喩、at a moment's notice/leap into action=仕事場面。創作用法・文法脱線なし、分量は前回同程度。注記=at a moment's notice/at short noticeの使い分けはやや断定的(誤りではない)。
- Part 2: 『賢者』=PASS(5標本すべて倒置文を選び、なぜ通常と異なる語順か/通常語順/提示順序と焦点/文学的効果を満たす。Trial-02のwhose解説から学習価値が明確に向上。文末焦点・直前文"The magi were wise men"との呼応は未言及)。『開いた窓』=第1標本の独立分詞構文(her eyes wide with horror)はher eyesを目的語と誤読しやすく学習価値あり=許容、第2標本=難文なし→0個=指示どおり。『イグ・ノーベル賞』=第1標本が基礎的な「命令文+and」でNG、第2標本が数値比較(more than three times as much A as B)でPASS。難文の少ない作品・説明文で選定が標本間で揺れる(各1/2)。指示を4段階強めても単調改善せず、作品側の天井+モデル傾向と判断し反復打切り(妥当)。
- Part 3/4: 副作用なし(全出力で形式維持、引用逐語不一致0)。
- 費用: Trial-03実費6.28円/10円。量産約0.28円/記事セット(Trial-02比+0.10円)。gpt-6-luna(最新、Trial-01/02と同一)。
- Status(Fable): VALIDATED(限定)。限定=Part 2の選定安定性(難文の少ない作品)、標本数各2、Production未承認。
- 推奨: (a)03dで採用判断へ(Production化設計: Prompt固定・引用逐語照合・人手確認フロー、Part 2は「難文がなければ0個」を正常系とする運用)。Part 2を機械的に安定させたい場合のみ(b)後段Gate等の新仕様Trial。
```
2. `docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR(#196想定、既存最終番号を確認して採番): 件名=英語学習解説Part 1・2改善Prompt(03d)の次工程。選択肢(a)採用判断へ進む(Production化設計、Part 2は0個を正常系)[推奨]/(b)Part 2安定化策の新仕様Trial(出力側決定論Gate等、要承認)/(c)中止。分類D、非blocking。参照=FABLE_EVAL_03.md、COMPARISON_03.md。
3. OPEN-497 Status=`VALIDATED(限定、Fable 2026-10-25)_PENDING_USER_DECISION(UDR #196)`。`DECISION_LOG.md` 1件。`docs/pm/ACTIVE_TASK.md` の該当行(委任_06行)をUDR番号付きに更新。
4. SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認。`py` を使用。
5. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 511 --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_07.md`。冒頭が「管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_07」と一致するか確認、不一致なら index 509〜514 を順に試す(`--index -1`不可)。
6. Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件) → `git commit --only -- <path…>` → `git push origin HEAD:main`。
7. 報告 `docs/pm/RESULT_PACKET_FZST7.md`: UDR番号、変更ファイル、commit hash、問題点。raw URL(FABLE_EVAL_03.md)。