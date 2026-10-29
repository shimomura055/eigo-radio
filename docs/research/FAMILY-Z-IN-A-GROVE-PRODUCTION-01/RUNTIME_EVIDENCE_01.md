# RUNTIME_EVIDENCE_01 (FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_07、2026-10-29) -- 途中(Cap停止)

状態: Adv(b1b)音声まで完了。**Std(a2)TTS以降は未実施(run累計Cap 70円超過見込みのため停止。判断候補)**。完成候補ページは未生成。

## 1. 選定確定(API 0)
| level | 照合コード | 確定ファイル | sha256 |
|---|---|---|---|
| Std a2 | AIF1-in_a_grove__a2__prod-4f0853-f48b5251-8ec5e76f-b4cfdee09f-0-0-7603 | key_phrases/a2/confirmed_selection.json | 9bf2f55ea955784d379b8f4c0b09b63e9af9ef8a3d2cfc6674118dc432d33b2c |
| Adv b1b | AIF1-in_a_grove__b1b__prod-333804-941647eb-ee543393-cd7ad21e57-0-0-3f4d | key_phrases/b1b/confirmed_selection.json | 7b0aa9b5277aacc59c7a2ae5532ebc4e65a3877e47bbbd8899aa512164fa5c8e |
- 手順: `er119_kp_human_review_cli_01.py confirm --from-readable`(dry-run rc=0→確定 rc=0、両level)。run=`er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01`。
- 照合: 復元payloadの candidates_sha256 = Std f48b52514ec544083dbdb0b3e4006c41fa2ad707f7b97065d180fef577f79344 / Adv 941647eb453de90d41fdced487cf47ed28a4065bb782f43dd206f75a0ad2bee4、text_sha256 = Std 8ec5e76f9381602be3cdea1af692e4592132c4f9ca3f7101f10260f517bee2a1 / Adv ee5433934163507384f4bb7dcd372d82c83859dddd1f1c0a5dc310e66d15621a。照合コードの各欄(c8/t8)と一致、不一致なし。意味文言はユーザー記載どおり(restore tool=fail-closed)。文法=選定なし(grammar_status=confirmed、NO_CANDIDATE_UNREVIEWED、study_text/confirmed_grammar.json sha eb6fc47ff8e15495a3701a721543a61f23d37e9b26b316fefa9351d30bcbc23f)。
- 貼付原文保存: `key_phrases/{a2,b1b}/confirmed_selection_source/rev1_readable.txt`、payload=rev1_payload.json。dry-run/confirm出力=`confirm_07/`。

## 2. stage別 rc・費用(e2e_stage_log.jsonl の spent_jpy_cumulative)
| 起動 | stage | rc | 累計(円) | 本起動増分(円) | 備考 |
|---|---|---|---|---|---|
| s7a (ts 1793229426) | kp | 0 | 39.4052 | +2.45(前 36.954) | 確定反映・Part1/2/gloss整合。両level。HR/STOPなし |
| s7b (ts 約1793229600) | tts_b1b | 0 | 59.5989 | +20.19 | 391.6秒。下記 |
- 起動は2回のみ(間隔>150秒、300秒窓内2起動以内)。STOP check(stop_check_07.json および _stop_scope_check_s7a/s7b.json)すべて stop=false。
- tts_a2: **未起動**。理由=(1)run累計Cap 70円に対し残り10.40円、tts_b1b実績20.19円から tts_a2 は約17〜21円と見込み、累計約77〜81円で超過、(2)BUDGET_PLAN_01の中間ゲート(c)に該当。加えてer007/er063/er078系の未commit差分(Worker I)が残存。

## 3. tts_b1b 結果(b1b/audit/tts_generation_results.json、全26 segment status=OK)
- ASR判定: PASS 23 / PASS_WITH_WARNING 2 / PASS_WITH_PRONUNCIATION_ALARM 1。**HR 0(HR Lock/queueなし)**。
- PASS_W一覧(pass_with_warning_listening_list.json、参考情報・非ブロッキング、試聴推奨):
  - segments/full_story_part1_c10(old_woman Zephyr)reason=secondary_confirmed / label SECONDARY_CONFIRMED。canonical「"Takehiro was my daughter's husband,"」、Primary「Talking here was my daughter's husband.」、Secondary(Azure)「Takehiro was my daughter's husband.」(固有名詞の聞き取り差。Secondary一致で受理)。
  - segments/full_story_part3_c5(narrator Aoede)reason=primary_pass / label SECONDARY_CORROBORATED(Primary「Takahiro's」表記差をSecondary corroborationで受理)。
- 固有名詞発音アラーム(PASS_WITH_PRONUNCIATION_ALARM、アラーム付き完成・非ブロッキング): comment_3 の Tajomaru(Primary tanjuromaru / Secondary taj mahal)・Takehiro(takahiro)。原稿綴りは変更せず(発音供給0件)。operator_alarm_report.md参照。**comment_3は試聴で確認推奨**。
- 速度Gate: 会話(pro)14clipの slowdown_ratio 0.9407〜0.9502(atempo系 speed_profile 記録あり)。narrator(flash-lite)clipは None。Gate停止なし。
- Local Rewrite: 発火なし(attemptsにLR phaseなし。再試行は part2_c1 pro TRUE_CONTENT_MISMATCH→NORMALIZED_MATCH、comment_3 flash-lite TRUE_CONTENT_MISMATCH→PASS_WITH_PRONUNCIATION_ALARM のstandard再試行のみ)。
- ja_v2beta(JA-ASR v2+β)は英語levelのため稼働0件(ja_v2beta_completion_block.json: 新方式 active 0、error 0)。
- API呼出(cost_log tts_b1b): Gemini pro TTS 16、flash-lite TTS 19、OpenAI ASR 50、Azure STT 12、gpt-6-luna 2(実体表NER等)、Perplexity sonar 2(発音調査)。

## 4. Voice割当の実証(送信パラメータ=tts_generation_results.json segment.voice/model_ids_measured/speaker)
| 役 | Voice(送信) | model | segment例 |
|---|---|---|---|
| narrator(全編地の文) | Aoede | gemini-3.8-flash-lite-tts | full_story_part1_c2/c5/c8/c11, part2_c2, part3_c2/c5 |
| woodcutter | Algieba | gemini-2.5-pro-preview-tts | part1_c1, c3 |
| monk | Schedar | pro | part1_c4, c6 |
| constable | Fenrir | pro | part1_c7, c9 |
| old_woman | Zephyr | pro | part1_c10, c12 |
| tajomaru | Orus | pro | part2_c1, c3 |
| masago | Kore | pro | part3_c1, c3 |
| takehiro | Puck | pro | part3_c4, c6 |
- topic_intro/preview/comment_1-3 は narrator=Charon(flash-lite)で送信(既存Z設計の導入・コメント枠のVoice。全編narratorのAoedeとは別。本作でも既存仕様どおりで変更なし)。voice_assignment.json の narrator_voice=Aoede、各 speaker voice は表と一致(rule_voice一致、pinned=false)。
- a2側のVoice送信実証は tts_a2 未実施のため未取得。

## 5. 費用内訳(累計)
Writer〜std_adjust〜plan〜support(委任_06まで)+ kp(委任_06 約1.6+委任_07 約2.45)+ tts_b1b 20.19 = 累計 **59.5989円 / Cap 70円**。日次(JST 10-29)合算は本agent未集計。

## 委任_08(2026-10-29): tts_a2 未実施(並行Worker未commit差分との競合回避待機が60分を超過)
- stop_check_08.json(08:27頃)=stop false、rc=0。run Cap 70→90円(Fable判断、BUDGET_PLAN_01.md末尾追記。runnerはE2EBudgetが起動ごとに`--approved-budget-jpy`をlimitとしspent_fnはcost_log累計を読むため再計上なし: er026_family_z_fiction_production_runner_01.py:1237-1258,3073)。
- 競合確認(`git status --porcelain -- er007 er078_* er109 er063 er026_runner er121`)を2分間隔で30回(08:31〜09:29、最大60分)実施。初回9件→最大11件dirty。09:30:35にafc63717d(JA-ASR v2+β配線: er007/er063/er078系)がcommitされ、09:31時点の残差分=`er026_family_z_fiction_production_runner_01.py`(26行)と`er121_family_y_runner_01.py`(53行)のみ。内容はNUANCE-EXPLANATION配線(stage_pages/_verify_part2_outputsでnuance_for_display・count_nuance_blocks・NUANCE_HEADINGを使用)で本作とは別Workerの作業中差分。本runの起動対象ファイル(er026 runner)がdirtyのため、委任_08手順2に従いtts_a2は起動していない。
- API呼出=0、費用増分=0。累計 59.5989円 / Cap 90円(残30.40)。run出力・STOP・LOCK変更なし。
- HEAD(判定時)=afc63717d。ja_v2beta配線は含まれる(judge_rule_version等の記録有無は実run未実施のため未確認)。
- 再開条件: er026 runner/er121の未commit差分がcommitまたは解消された後、`--approved-budget-jpy 90` で `--stages tts_a2` を1起動 → 150秒以上空けて `--stages provision_shell,gate,assemble,pages,page_verify`。注意: NUANCE配線がHEADに入るとpages/page_verifyでニュアンス解説ブロックが期待される(in_a_grove側のnuance採否は今回未確認、要Fable確認)。

## 委任_09r(2026-10-29): 起動A tts_a2 = STOP(FamilyZTtsClipFailedStop、2 clip HR)。起動Bは未実施
- 前提確認: `git status --porcelain -- er026_*.py er120_*.py er128_*.py er121_*.py er003_*.py` = tracked変更0(`??`のer003_v1_p2*のみ、無視)。HEAD=9cdf9af3b。stop check(stop_check_09r_A.json)rc=0 stop=false。
- 起動A: 11:01:32 `--stages tts_a2 --approved-budget-jpy 90 --mode real --tts-execution-mode STANDARD`(run_launch_log pid 26904)。11:15:29終了。`[STOP] FamilyZTtsClipFailedStop: FAMILY_Z_TTS_CLIPS_NOT_OK(a2): {comment_3: STOPPED, full_story_part1_c3: STOPPED}`。STOP/STOP_ALL/RESTART_STORM sentinel生成なし。e2e_stage_log.jsonlにtts_a2行なし(stage失敗のため)。再起動せず(委任文: 各起動1回のみ)。
- 費用(compute_cost_jpy_so_far on cost_log.jsonl): 累計 **86.3468円 / Cap 90円**(a2分 +26.7479円。provider内訳 openai 39.85 / gemini 31.49 / openai_asr 3.46 / azure 11.55)。残り3.65円。a2はb1b(20.19円)より大きい: 3回試行+180秒cooldown(part1_c3 ctx x2 + legacy x1 の pro TTS、comment_3 flash-lite x3)の再試行分を含む。
- tts_generation_results.json(a2) 27 segment: OK 25 / STOPPED 2。ASR(英語: 20、JA 7)。OK25内訳: PASS 22 / PASS_WITH_WARNING 3(part1_c10 secondary_confirmed、part2_c5 secondary_confirmed、part3_c2 primary_pass+SECONDARY_ASR_CORROBORATED)/ HR 2(STOPPED)/ 固有名詞ALARM 0。
- STOPPED 2件(既存retry/fallbackを使い切り。人手判定変更なし):
  1. comment_3(日本語、narrator Aoede flash-lite): 全3試行(standard 2+fallback 1)TRUE_CONTENT_MISMATCH。原文「タジョマルと真砂では…」→ASR「太郎丸と政子」「多助丸と雅子」「多十丸と政子」。人名の読み(タジョマル/マサゴ)をASRが別名に誤認。JA HR queue 1行+HR Lock。JA v2+β: 同clipはlock(ja_v2beta_completion_blockのhr.lock参照)。
  2. full_story_part1_c3(英語、woodcutter Algieba pro): ASRは3試行とも原文と完全一致(NORMALIZED_MATCH, primary_pass)だが、repetition_qa(method_d' spectral_short_lag, 閾値0.6秒/sim 0.7)が3試行すべてflagged(run 1.24s/0.82s/0.80s、冒頭0.3〜0.7秒付近、lag 0.59〜0.76秒)で verified=false。method_a(n-gram)/method_d(長lag)はflagged=false。ctx x2→legacy_fallback x1とも同傾向=閾値0.6秒を僅かに超える短lag自己類似(Algieba声質に起因する疑い、真の繰返しかは未聴取)。
- JA-ASR v2+β稼働: JA判定record 7件/有効7/定数OFF0/E3E4ブロック0/エラー無効化0。`judge_rule_version`=`ja_v2beta_r1off_01`(tts_generation_results.jsonに7件、review_lock_state.jsonに9件)。新方式(v2/β)PASS_W 0件(β 0 / v2 0 / garble 0)、β費用0。6件=PASS(primary_pass)。comment_3のみ全試行不一致でHR。
- 声割当(送信実証、a2): narrator Aoede(flash-lite)、woodcutter Algieba、monk Schedar、constable Fenrir、old_woman Zephyr、tajomaru Orus、masago Kore、takehiro Puck(いずれもpro、voice_assignment.jsonと一致)。
- 次の一手候補(Fable判断。Cap残3.65円): `--only-clips comment_3,full_story_part1_c3`で2 clipのみ再実行(runner提示の既存手段)。ただし(1)part1_c3は同一repetition_qaで再flagされる確率が高く(3/3)、(2)comment_3はASRの人名誤認でTTS側の問題でない可能性が高い。推奨: 原因別にFableが判断(repetition_qa閾値・JA人名はPromptや閾値の変更=承認事項に触れるため独断せず)。
