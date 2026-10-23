FABLE-DELEGATION-MARKER: FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01-委任_03-MERGE-20261023

# 委任_03: 速度A/B Trial — Advanced素材の試聴ページ統合・Production ASR確認・SSOT更新(Trial、Production変更禁止)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01_委任_03_MERGE.md`(N≈323〜333、先頭行MARKER一致確認)。
2. ACTIVE_TASK.md: 別agent(FAMILY-Y 委任_01A、ASR-HOMOPHONE 委任_05)が並行中。編集直前に再読込し、OPEN-462行だけ更新。有料呼出(Azure ASR)の直前・直後に同行へ「有料run進行中/終了(時刻)」。

## 1. 前提
- Standard側(委任_01): ページ `user_test/family_z_std_dialogue_speed_ab_01/index.html`(公開・60/60再生OK)、証跡 `docs/research/FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01/TRIAL_RESULT_01.md`、`er026_output/family_z_std_dialogue_speed_ab_01/analysis.json`、OPEN-462、UDR #159。
- Advanced側(委任_02_ADV): 素材 `er026_output/family_z_std_dialogue_speed_ab_01/adv/<story>/mp3/`(full_A/B、dNN_A/B)、`adv/manifest_adv.json`、`adv/analysis_adv.json`、証跡 `TRIAL_RESULT_ADV_01.md`。会話clipのみ atempo 1.06(ピッチ保持、`er008_a2_postprocess_slowdown_01.apply_a2_slowdown`再利用)、非対象clip sha一致、長さ比0.9435〜0.9519、ローカルWhisperでは高速化による劣化なし(不一致3件はA版も同じ転写)。Production既定のAzure ASRは未実行(見積約5.7円)。
- ユーザー追加指示原文: `docs/pm/delegation_log/2026-10-23_FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01_USER_02_ADV.md`(ページ要件: 各レベルのA/B通し再生/同一会話clipのA/B個別再生/NarratorとDialogueの速度比較[実測WPM]/変更箇所・内容が分かる表示。前回ページとまとめ、重複ページを作らない)。
- Fable判断: Advanced B版会話clip(29本)に**Production既定のASR検査(Azure Secondary相当、約5.7円)**を実行してPASS維持を確認する(Standard側と同水準の証拠にそろえる。300円枠内、本日累計は約70円)。別agentの有料run(ASR-HOMOPHONE 委任_05のZ TTS段)と重ならないよう、開始前に`Get-Process python`とACTIVE_TASKのOPEN-459行を確認し、走行中なら終了まで待機(5分間隔・最大30分)。

## 2. 作業
1. **Production ASR確認(Advanced B 29clip)**: Standard側(委任_01)が使ったのと同じProduction判定経路・手順で実行し、結果(一致/既存警告/新規欠陥)をA版の事後ASR記録と対比。費用は出典付き(raw_usage_log/est_jpy)。
2. **ページ統合**: `adv/<story>/mp3/`を`user_test/family_z_std_dialogue_speed_ab_01/<story>/adv/`等へコピーし、既存index.htmlに各作品の「Advanced」節を追加(既存のStandard節と同じ構成: A/B通し再生、会話ごとのA/B並列再生+A→B連続再生、同一性表[非対象clip sha一致数・台詞・Voice]、WPM表[Narrator vs Dialogue A/B、全clip中央値・8語以上・加重を併記]、**変更内容の明示**[Standard: 会話のみ6%減速撤去 / Advanced: 会話のみ機械処理で約6%高速化・ピッチ保持 / Narrator等は不変])。ページ先頭に比較条件表(ユーザー原文§2の表)を置く。既存のStandard節・mp3は変更しない(sha維持)。
3. **公開検証**: commit/push後、HTTP 200+Playwright実再生(新規追加分を含む全audio)、既存のページ標準検査。
4. **証跡**: `TRIAL_RESULT_01.md`に「Advanced統合」節を追記(ASR結果・WPM・同一性・費用、ADV証跡へのリンク)。
5. **SSOT**: OPEN-462の要約をStandard+Advancedに更新(Status=`TRIAL_COMPLETE_USER_DECISION_REQUIRED`維持)、UDR #159の判断項目を「作品×レベル(4組)それぞれA/Bどちらを採用するか」に更新(採用時の反映手順・費用: 既存4本は再組立+mp3差替えのみでTTS 0円、Productionの仕様変更[Std会話の減速skip / Adv会話の6%高速化後処理追加]はユーザー承認後)、DECISION_LOG 1件、REPORT_LEDGER 1行。commitは明示add(mp3含む。wavは含めない)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 3. 禁止
- Production仕様・コード・既存成果物・公開3ページ(`family_z_melos_02`/`family_z_melos_jre_01`/`family_z_open_window_01`)・Storeの変更、再生成、新Prompt/Style、独自の速度条件・品質基準の追加、Trial版のProduction反映。

## 4. 報告(docs/pm/RESULT_PACKET_FZSPAB3.md、同内容を最終報告で)
(1)統合後の試聴URL(作品・レベル別アンカー) (2)Advanced B のProduction ASR結果 (3)WPM表(作品×レベル×Narrator/Dialogue A/B) (4)公開再生検証数値 (5)費用(ASR実費、出典) (6)Production無変更の証拠 (7)commit・raw URL・SSOT (8)残件 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。