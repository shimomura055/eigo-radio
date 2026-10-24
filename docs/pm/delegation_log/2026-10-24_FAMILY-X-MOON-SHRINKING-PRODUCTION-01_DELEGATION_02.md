管理ID: FAMILY-X-MOON-SHRINKING-PRODUCTION-01 委任_02 — 「月は少しずつ縮んでいる?」のStd/Adv正式Production制作→完成候補(USER_LISTENING_PENDING)まで。上限100円。

## 前提(委任_01で準備済み。まず読む)
- `docs/research/FAMILY-X-MOON-SHRINKING-PRODUCTION-01/{FACT_CHECK_01,CP_CHECK_01,BUDGET_PLAN_01}.md`、入力 `er019_output/moon_shrinking/theme.txt`。手順は `CP_CHECK_01.md` §Bの起動コマンド列を正とする(text 1起動→audio 1起動→HR Lock時停止→final_page→play_verify)。
- ユーザー指示原文 `docs/pm/delegation_log/2026-10-24_FAMILY-XZ-MOON-TELLTALE-PRODUCTION-01_USER.md`(事実の扱い: 縮小量の対象期間・推定根拠・不確実性を正確に、急速に縮んでいると誤解させない、専門的すぎない、身近な疑問と意外性)。FACT_CHECK_01の禁止表現/許容表現リストをWriter入力に反映済みか確認。
- X2p'(KP日本語意味の新経路)はcommit d8fb8f9a4で配線済み(ユーザー承認済み仕様)。本作のKP段はこの承認済み経路で生成される。別agentが同配線のruntime evidence・記事B更新を並行実行中(TTSを使う)。
- 本委任文を `docs/pm/delegation_log/2026-10-24_FAMILY-X-MOON-SHRINKING-PRODUCTION-01_DELEGATION_02.md` に逐語保存(`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index <最新(487以降)> --out <path>`、先頭行一致確認)。

## 起動条件(全て満たしてから。1つでも不成立なら起動せず報告)
1. X経路import graphに未commitの.pyがなくHEADと一致(`git status`)。er003*.pyがcleanであること。
2. `stop_scope_check` rc=0、STOP/STOP_ALLセンチネルなし。
3. 日次費用再集計: 10-24 JST把握分約670円+並行中のX2p'委任(≤25円)+Z『告げ口心臓』(≤70円)+本件100円が1,000円以内であること(JST日付が変わっていれば新日次)。累計が上限の約8割で超過見込みなら続行前に報告。
4. cost logger `install`を忘れない。

## 実行
- CP_CHECK_01 §Bのとおり: text runner 1起動(`--stage all`)→audio runner 1起動(`--level both --stage all --budget-jpy 100`)→`er019_nws2_final_page_01.py`→`er019_nws2_play_verify_01.py`(公開URLで47項目相当の再生検査PASS)。同一run起動間隔150秒以上、RESTART_STORM回避、TTS直列化flag尊重(他agentのTTSが走っていれば待つ)、`.venv\Scripts\python.exe`。
- 必須Gate: Fact/本文/KP(A-1・②・X2p'適用、未承認KPなし)/TTS/ASR(PASS_WITH_WARNINGの根拠記録)/音声検査/Style Profile Gate/公開検査。retry/fallback/resumeは既存仕様のまま。**STOP条件**: HR Lock発生(approve_regenerateはFable権限、停止して報告)、Style Gateの人間承認待ち(停止して報告)、予算超過見込み、重大品質問題、Production欠陥の発見(修正は影響分析gateを経て承認範囲内のみ)。
- 承認済み仕様を変更しない。本作固有Prompt新設禁止。新仕様Trial転用禁止。
- 完成後に `FACT_CHECK_02.md`: 生成された本文(Std/Adv)の事実文を一次研究(Watters et al. 2026, PSJ 7(10) 239)と照合(縮小量42〜46m・期間・根拠・不確実性・「推定」表現、禁止表現0件)。問題があれば既存のLocal Rewrite/部分再生成の承認済み経路で是正(本文全再生成は最後の手段、費用内)。
- `RUNTIME_EVIDENCE_01.md`: 正式入口・stage・actual model_id・Gate結果・KP一覧(英語/日本語gloss、`meaning_stage`の記録=X2p'発火evidence)・ASR結果・HR Lock有無・Local Rewrite開示・費用内訳(目標70円との差)・所要時間・試聴URL(Std/Adv)。
- 公開: `user_test/family_x_moon_shrinking_01/`(切替ページ)。
- SSOT: `OPEN_ITEMS.md`に新規OPEN(本作Status=COMPLETE_USER_LISTENING_PENDING、分類付き)、`DECISION_LOG.md`に制作記録1件、`docs/pm/USER_DECISION_REGISTER_01.md`に最終試聴UDR(次番号、非blocking)、`docs/pm/ACTIVE_TASK.md`更新。**別agentが同SSOTを並行編集中**: 編集直前に該当箇所を再Read、最小Edit、衝突時は再Read再試行。
- Git: 自分の変更のみ(`git add <path>`→`git diff --cached --name-status`→`git commit --only -- <path…>`または前例のupdate-index方式→`git push origin HEAD:main`)。wav/mp3/raw_usage_log/STOP/lock/sources不追跡。禁止: `git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret grep 0件。OPEN-490: 全回帰等がtelemetryを書き換えてもstageしない。
- 報告 `docs/pm/RESULT_PACKET_FXMS2.md`: ユーザー§4の項目(Std/Adv試聴URL、全編・パート別再生、全スクリプトとKP、Gate結果、runtime evidence、実費、問題・未解決、SSOT/Git)+Fable受入用の証拠パス。到達目標は「正式完成候補・ユーザー最終試聴待ち」。PASS先取り禁止。