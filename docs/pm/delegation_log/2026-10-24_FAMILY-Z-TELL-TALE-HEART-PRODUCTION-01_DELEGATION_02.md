管理ID: FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01 委任_02 — 『告げ口心臓(The Tell-Tale Heart)』Std/Adv正式Production制作→完成候補(USER_LISTENING_PENDING)まで。上限70円。

## 前提(委任_01で準備済み。まず読む)
- `docs/research/FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01/{SOURCE_CHECK_01,CP_CHECK_01,BUDGET_PLAN_01}.md`、seed `er026_seeds/the_tell_tale_heart/`、STORY_REGISTRY登録済み(commit ed24bae8c、登録test23件OK)。手順は `CP_CHECK_01.md` §Bの起動コマンド列を正とする(`--story the_tell_tale_heart --run run_sf_prod_01 --mode real --approved-budget-jpy 70`、stages: ①seed_check,writer,std_adjust ②plan,support ③kp ④tts_b1b ⑤tts_a2 ⑥provision_shell,gate,assemble,pages,page_verify[必ず1起動])。
- ユーザー指示原文 `docs/pm/delegation_log/2026-10-24_FAMILY-XZ-MOON-TELLTALE-PRODUCTION-01_USER.md`(原作の重要な出来事・因果・結末維持/語り手の異常心理・緊張感・心臓の音の恐怖/承認済み構成・Voice・会話速度仕様を守る)。
- Voice決定的割当: narrator=Aoede、old_man=Algieba、officer=Schedar(登場順はWriter出力を見てplan前に確認)。語り手本人の引用台詞はnarrator枠。既存3パート構成・速度仕様v2(極短clip 0.90〜1.00含む)をそのまま適用。効果音・新Prompt・仕様変更禁止。
- X2p'(KP日本語意味の新経路)はcommit d8fb8f9a4で配線済み(ユーザー承認済み仕様、Z共通module)。本作のkp段はこの経路で生成される。別agentが同配線のruntime evidence・記事B更新を並行実行中(TTS使用)。並行でFamily X『月の縮小』も制作中(TTS使用)。
- 本委任文を `docs/pm/delegation_log/2026-10-24_FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01_DELEGATION_02.md` に逐語保存(`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index <最新(487以降)> --out <path>`、先頭行一致確認)。

## 起動条件(全て満たしてから。1つでも不成立なら起動せず報告)
1. Z経路import graphに未commitの.pyがなくHEADと一致(`git status`)。er003*.py/er026/er062/er063がcleanであること。
2. `stop_scope_check` rc=0、STOP/STOP_ALLセンチネルなし。
3. 日次費用再集計: 10-24 JST把握分約670円+並行中のX2p'委任(≤25円)+X『月の縮小』(≤100円)+本件70円が1,000円以内(JST日付が変わっていれば新日次)。累計が上限の約8割で超過見込みなら続行前に報告。
4. cost logger `install`を忘れない。

## 実行
- 上記stage順で起動(同一run起動間隔150秒以上、RESTART_STORM[5分間3回]回避、TTS直列化flag尊重=他agentのTTS中は待つ、`.venv\Scripts\python.exe`)。
- 必須Gate: seed_check(原作忠実性: 老人の目/7夜偵察/8夜目殺害と床下隠蔽/警官来訪/心臓音増大/自白、結末維持)/Writer/Std調整/KP(A-1・②・X2p'適用)/TTS/ASR/速度Gate(v2)/音声検査/公開検査。**STOP条件**: HR Lock(approve_regenerateはFable権限、停止して報告)、RESTART_STORM(自分で`--clear-stop`しない)、予算超過見込み、原作結末欠落等の重大品質問題、Production欠陥(修正は影響分析gate後・承認範囲内のみ)。速度Gate停止時は『猿の手』前例(該当clipのみ再生成、wav退避)に倣う。
- 完成後に `SOURCE_FIDELITY_CHECK_01.md`: 生成本文(Std/Adv)と原典の対応(維持項目4件の所在、因果、結末、語り手の心理と心臓音の扱い、Local Rewriteの開示)。
- `RUNTIME_EVIDENCE_01.md`: 正式入口・stage・actual model_id・Gate結果・Voice割当・速度Gate結果(極短clipの有無)・KP一覧(英語/日本語gloss、`meaning_stage`=X2p'発火evidence)・ASR結果・HR Lock有無・費用内訳(目標70円との差)・所要時間・試聴URL(Std/Adv)。
- 公開: `user_test/family_z_tell_tale_heart_01/`(切替ページ)、page_verify PASS。
- SSOT: `OPEN_ITEMS.md`に新規OPEN(Status=COMPLETE_USER_LISTENING_PENDING、分類付き)、`DECISION_LOG.md`に制作記録1件、`docs/pm/USER_DECISION_REGISTER_01.md`に最終試聴UDR(次番号、非blocking。X『月の縮小』agentも同時に番号を取るため、追記直前に再Readして重複しない番号にする)、`docs/pm/ACTIVE_TASK.md`更新。**別agentが同SSOTを並行編集中**: 編集直前に再Read、最小Edit、衝突時は再Read再試行。
- Git: 自分の変更のみ(`git add <path>`→`git diff --cached --name-status`→`git commit --only -- <path…>`または前例のupdate-index方式→`git push origin HEAD:main`)。wav/mp3/raw_usage_log/STOP/lock/sources不追跡。禁止: `git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret grep 0件。OPEN-490: telemetry書き換えをstageしない。
- 報告 `docs/pm/RESULT_PACKET_FZTTH2.md`: ユーザー§4の項目(Std/Adv試聴URL、全編・パート別再生、全スクリプトとKP、Gate結果、runtime evidence、実費、問題・未解決、SSOT/Git)+Fable受入用の証拠パス。到達目標は「正式完成候補・ユーザー最終試聴待ち」。PASS先取り禁止。