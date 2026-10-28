管理ID: FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_02 — 『藪の中(In a Grove)』Std/Adv正式Production制作→完成候補(USER_LISTENING_PENDING)まで。上限70円(BUDGET_PLAN_01: 中心約50円)。前例テンプレート=`docs/pm/delegation_log/2026-10-24_FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01_DELEGATION_02.md`(手順・STOP条件・Git規則はこれを正とし、本文中の作品固有値のみ本作に置換)。

## 前提(委任_01で準備済み、Fable Seed CP=PASS[source_quote=原作最終段と逐語一致、真相一本化禁止文言あり、keep_name 3件])。まず読む
- `docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/{SOURCE_CHECK_01,CP_CHECK_01,BUDGET_PLAN_01}.md`、seed `er026_seeds/in_a_grove/`、STORY_REGISTRY登録済み(commit a77950371、登録test 27 OK)。起動コマンド列は`CP_CHECK_01.md` §Bを正とする(`--story in_a_grove --run run_sf_prod_01 --mode real --approved-budget-jpy 70`、stages: ①seed_check,writer,std_adjust ②plan,support ③kp ④tts_b1b ⑤tts_a2 ⑥provision_shell,gate,assemble,pages,page_verify[必ず1起動])。
- ユーザー原文 `docs/pm/delegation_log/2026-10-28_FAMILY-Z-IN-A-GROVE-PRODUCTION-01_USER.md`(§2 証言者ごとの人物像・矛盾の維持・真相を一本化しない/§5 証言者Voice・Storytelling・Comment/Previewの先取り禁止/§8 報告項目/§9 STOP条件)。
- Fable判断(委任_01判断候補): essentials構成=keep_name 3名(Tajomaru/Masago/Takehiro)・setups 0件を採用(B)/視点設計=中立narrator(Aoede、話者紹介のみ)+各証言は当該Voice(B)/Comment・Preview lint値(B)を採用。公開ページ出典欄=既存Family Z権利ブロックのまま(青空文庫の入力者・校正者名は任意のため追加仕様なし)。日本語題TTS=「藪の中」のまま(ASR誤読時のみ「やぶの中」へdata表変更を検討)。
- Voice決定的割当(委任_01案、pin 0・新Voice探索なし): narrator=Aoede、woodcutter=Algieba、monk=Schedar、constable=Fenrir、old_woman=Zephyr、tajomaru=Orus、masago=Kore、takehiro=Puck。Writer出力の初出順・省略に応じてplan前にrosterのorder/話者をdata表で訂正(前例と同手順)。検非違使の質問が書かれた場合はnarrator枠。
- 本委任文を `docs/pm/delegation_log/2026-10-28_FAMILY-Z-IN-A-GROVE-PRODUCTION-01_委任_02.md` に逐語保存。

## 起動条件(全て満たしてから。1つでも不成立なら起動せず報告)
1. Z経路import graph(er026/er062/er063/er003*/er019_family_x_audio_production_runner_01.py 等)の.pyに未commit差分がなくHEADと一致(`git status`)。X Comment3委任は commit 84a61fba7/664443842/1502e25ca/1692b5fe5 でpush済み=cleanのはず。他に未commitの.pyがあれば起動せず報告。
2. `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --run-dir docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --out docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01/stop_check_02.json` rc=0、STOP/STOP_ALLセンチネルなし。
3. 日次費用集計(10-28 JST): 本日の既知支出は小額(JA-ASR約¥3.5、AI島Trial¥0.17、Comment3 ¥0.62、他0)。本件70円を加えて1,000円以内であることを cost_log で再集計し記録。
4. cost logger `install`。関連test(登録test 27)PASSを再確認。

## 実行
- stage順で起動(同一run起動間隔150秒以上、RESTART_STORM回避、TTS直列化flag尊重=他agentのTTS中は待つ。現在他agentのTTSはなし)。
- 必須Gate: seed_check(essentials fail-closed・source_quote最終段)/Writer(R0/R1/R2→Std調整)/KP/TTS/ASR/速度Gate(v2)/音声検査/公開検査。**STOP条件**: HR Lock(approve_regenerateはFable権限、停止して報告)、RESTART_STORM(自分で`--clear-stop`しない)、予算超過見込み(tts_b1b終了時に累計32円超なら再計算して続行可否を記録、70円超見込みなら停止報告)、原作の核心(3証言の矛盾・結末・真相不確定)の欠落等の重大品質問題、Production欠陥(修正は影響分析gate後・承認範囲内のみ)。速度Gate停止時は『猿の手』前例(該当clipのみ再生成、wav退避)。
- 作品固有の確認(新Gateではなく、CP checklist+目視): (a)7証言の構造と3当事者の矛盾(多襄丸=決闘で刺した/真砂=自分が小刀で刺した/武弘=自害+見えない手)が本文に残っているか、(b)原作にない真犯人・決定的証拠・客観的結論が創作されていないか、(c)証言者の切替が聞いて分かるか(narrator紹介+Voice)、(d)Comment/Previewが最後の証言内容・真相を先取りしていないか、(e)性暴力の扱いが非グラフィックで動機が消えていないか。問題があれば承認済み経路(regen/Local Rewrite)内で是正し記録。
- 完成後 `SOURCE_FIDELITY_CHECK_01.md`(Std/Adv本文と原典の対応: 7証言の所在、矛盾の構造、結末、essentials各項目の本文該当引用、CP重大/軽微の判定、Local Rewriteの開示)と `RUNTIME_EVIDENCE_01.md`(正式入口・stage・actual model_id・Gate結果・Voice割当(送信Voiceの実記録=tts_voice_sent)・速度Gate結果・KP一覧(英語/日本語gloss)・ASR結果・HR Lock有無・費用内訳(目標70円との差)・所要時間・試聴URL Std/Adv)。
- 公開: `user_test/family_z_in_a_grove_01/`(切替ページ)、page_verify PASS、Pages反映後の実測(200)。
- SSOT: `OPEN_ITEMS.md`新規OPEN(Status=COMPLETE_USER_LISTENING_PENDING、分類付き)、`DECISION_LOG.md`制作記録1件、`docs/pm/USER_DECISION_REGISTER_01.md`最終試聴UDR(次番号、非blocking。追記直前に再Readして重複しない番号)、`docs/pm/ACTIVE_TASK.md`に(H)行追加。別workerがSSOTを並行編集する可能性あり: 編集直前に再Read、最小Edit。
- Git: 自分の変更のみ明示`git add`→`git diff --cached --name-only`確認→commit→`git push origin HEAD:main`(FFのみ)。wav/mp3/raw_usage_log/STOP/lock不追跡(候補ページのmp3は前例の扱いに従う)。禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、reset --hard。
- 報告 `docs/pm/RESULT_PACKET_FZIG2.md`: ユーザー§8の10項目(1 試聴URL/2 原作・権利・Seed確認/3 証言者構成とVoice割当/4 矛盾の維持方法/5 本文・Comment・Preview・学習項目の品質/6 TTS・ASR・Assembly/7 実費と単価示唆/8 未解決・HR項目/9 Git・SSOT/10 Fable受入用証拠パス)+4行+判定整合行。到達目標は「正式完成候補・ユーザー最終試聴待ち」。PASS先取り禁止。hand-back: 試聴URL、Gate結果要約、Voice送信実記録、矛盾維持の要点(各当事者の証言の本文引用1行ずつ)、実費、HR有無、commit sha、判断候補。
