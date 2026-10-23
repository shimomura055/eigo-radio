# RUNTIME_EVIDENCE_01 (FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01 委任_01、2026-10-24)

run dir: `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/`(wavは未追跡)。実行は `.venv/Scripts/python.exe`、`TTS_EXECUTION_MODE=STANDARD`、Production経路のCLI(`er026_family_z_fiction_production_runner_01.py --story the_gift_of_the_magi --run run_sf_prod_01 ...`)。
STOP範囲確認 `tools/stop_scope_check_01.py --managed-id FAMILY-Z-GIFT-OF-THE-MAGI-PRODUCTION-01` は各起動前に rc=0(`_stop_scope_check_*.json`)。STOPセンチネル・RESTART_STORMの発動なし。他agentの「有料run(TTS)進行中」flagはなし(直列化待機0)。

## 起動履歴(run_launch_log.jsonl / console_*.txt)
| # | JST(2026-10-24) | stages | 結果 |
|---|---|---|---|
| 1 | 07:38 | seed_check,writer,std_adjust | OK 12.49円(Adv r0/r1/r2 + Std、Adv 434語/Std 449語、段落30/30) |
| 2 | 07:57頃 | plan,support | OK +0.64円。話者判定mismatch 0(全引用 llm_only=決定論がキーワード該当なしのため。LLM判定=正) |
| 3 | 08:01:27-08:03:19 | kp | OK +1.13円(累計14.26円) |
| 4 | 08:03:59-08:08:40 | tts_b1b(Adv) | rc=0、約4分41秒、累計23.43円 |
| 5 | 08:08:40-08:12:46 | tts_a2(Std) | rc=0、約4分06秒、累計33.19円 |
| 6 | 08:12:56-08:15:22 | provision_shell,gate,assemble,pages,page_verify(**1起動**) | rc=0。shared_gate=PASS(Std/Adv)、page_verify local PASS |
再起動 0回(各stage 1起動)。HR Lock・STOP・approve_regenerate 0回。

## Production配線の対応(commit/時刻)
- 作品登録: commit 5bf3d590b(2026-10-24 07:51:55 JST、data表のみ)。pages/成果物: commit 7ab90c253。
- **KP課題②(所有格一般化 one's/someone's)**: FX-KP 委任_20 が commit **4128fffeb**(2026-10-24 08:01:09 JST)でX/Z Production配線済み。**kp段の実行は08:01:27 JSTでその18秒後**(HEAD=4128fffeb、`_kp_head_commit.txt`)。→ ②は適用された: Adv KP3 `catch her breath`->`catch one's breath`(possessor_roles=[her:self])、Std KP2 `smiled through her tears`->`smile through one's tears`(possessor_roles=[her:self])、`person_role_repair.status=NO_CHANGE`(`keywords_canonicalized.json`)。A-1(PRODUCTION_WIRED)も同経路。finalize前の再確認(08:15頃): kp関連ファイル(er105/er003_key_words_*/template)に4128fffeb以降のcommitなし(`git log --since`)、②再配線による再実行は不要。**注意**: ②のFable受入は本run時点で未了(ACTIVE_TASK委任_20行はruntime evidence実施中)。受入で配線内容が変わった場合のみkp段(+KP音声)の再実行が必要(費用小)。
- 未承認G3/課題①検査方式C等: 適用なし(`EIGO_KP_GLOSS_ALIGNMENT`は既定=ON[source=default、既存Production既定]のまま。DEV flagをONにしていない)。
- 作業ツリーに他agentの未commit変更が1ファイルあった(`er021_en_asr_semantic_equivalence_production_01.py` +66行、ASR-TIME-NUMERAL-EQUIVALENCE-01 の案C試作=`_try_clock_pair`、未承認・未commit。diff sha256先頭12=25a88eb84939 [TTS開始前]）。本作の原稿・ASR転記に『時+分』の隣接数詞語は無く(`By seven,`のみ)、判定結果へ影響する経路には入っていない(PASS理由は全て`primary_pass`/承認済みequivalence)。ただし作業ツリーの他agent未commit変更がrunに混在した事実としてここに記録する(隔離は作品側の問題ではない)。

## モデル
Writer(r0/r1/r2/std_adjust)=`gpt-6.1-sol`(最新世代の最上位系)、plan/support/kp/RET NER/gloss alignment=`gpt-6-luna`、TTS=`gemini-3.8-flash-lite-tts`(地の文・KP・案内)+`gemini-2.5-pro-preview-tts`(会話台詞clip=Z既定)、ASR=`gpt-4o-mini-transcribe`、二次ASR=`azure-speech-stt`。いずれも本番ライン既定(評価用途ではない)。

## Voice配役(`voice_assignment.json`、pinなし・決定的割当規則)
narrator=Aoede / Della=Zephyr / Madame Sofronie=Kore / Jim=Algieba / Adv補助(紹介・KP番号等)=Charon。Adv話者: narrator10・Della6・Madame1・Jim1 clip。Std: narrator10・Della6・Madame1・Jim1。

## 構成・再生時間
- Std(a2): 3part(語数192/115/136=43%/26%/31%、Std独自分割[Adv境界のStd写像がPart比20-45%を満たさないため既存仕様どおり独自分割、WARNのみ])、story18clip、通し296.5秒。
- Adv(b1b): 3part(語数123/126/179=29%/29%/42%)、story18clip、通し278.5秒。
- 本文: Adv 434語・Std 449語(330-470内)。

## ASR/TTS/retry/fallback/HR
- TTS段: Adv 全30 segment(story18+preview+comment3+KP+案内): attempt>1 は0件(`tts_generations_used`=1)。Std: kp1_ja(日本語KP『べっ甲のくし』)のみ attempt 2(attempt1 ASR=`メッコーノクシ` TRUE_CONTENT_MISMATCH -> attempt2 `べっこうのくし` PHONETIC_MATCH で採用)。fallback_used=0、local_rewrite=0、cooldown=0、Human Review Lock=0。
- 全TTS(Gemini)呼出: Adv 30(flash-lite 21+pro 9)、Std 31(flash-lite 23+pro 8)。Adv `full_story_part2_c4`(Madame『Twenty dollars.』)はTTS 2呼出/ASR 2呼出だが採用は1テイク(`tts_generations_used`=1)。per-attempt旧分類ラベルが `TRUE_CONTENT_MISMATCH` と記録された一方、最終判定(unified judge)は `PASS / primary_pass / ORTHOGRAPHIC_EQUIVALENT_MATCH`(ASR `twenty dollars`、value_guard `EQUAL` 20=20)。既存挙動の観測として記録(結果に影響なし)。
- Azure二次ASR: Adv 5呼出(comment_1、kp1-3_en、part2_c3)、Std 4呼出(kp1_ja、kp1-3_en)。
- approved equivalence(通過理由): Adv `TIER1_NUMERIC_EQUIVALENCE` 2(comment_2、part3_c9=ASR `Magi`大文字)、Std `READING_MATCH` 2(comment_1/3 日本語『ジム』->ASR『事務』同音)+`TIER1_DIFF_ANCHORED` 1(part1_c1 `$1.87`)。
- **PASS_WITH_WARNING(耳確認候補)** Adv 2件 / Std 0件: Adv `comment_1`('Listen for what **Della** is thinking...' ASR一次=`Del`、`SECONDARY_CORROBORATED`)、Adv `full_story_part2_c3`('The owner lifted the heavy **waves**.' ASR一次=`weights`、二次azure=`waves`で`SECONDARY_CONFIRMED`)。
- 時刻・数詞: 本文の時刻は `By seven` のみ。`$1.87`(Std)/`One dollar and eighty-seven cents`(Adv)/`twenty-one dollars`/`eighty-seven cents` は全てPASS(上記equivalence含む)。OPEN-482の影響なし。
- RET: 実体表 `audit/entity_table.json` builds=1 call(NER `gpt-6-luna`、0.041円)、実体5件(person/confirmed 1・person/weak 1・other_named/weak 2・work_title/weak 1、証拠として使用可1件)。Perplexity発音調査呼出0(Della/Jim/Madame=一般的英語名)。PNAP=発火なし、UKUS=発火なし(英米差の語なし)、固有名詞発音アラーム 0件(operator_alarm_report)、HR(固有名詞起因)0件。会話経路でのRET受理basis別発火(OPEN-472追認材料)は本runでは該当なし(会話clipはすべて`primary_pass`)。
- speed v2: Adv narrator none/dialogue fast6、Std narrator slow6(M1 slowdown applied)/dialogue none。`audio_text_deviations` 0件(Adv/Std)。Repetition QA flagged 0。

## Gate
`gate_result_04C.json`: Adv/Std とも `shared_gate=PASS`、`m2_complete=True`、`kp_vote_audit` checked 3 / blocking=false / missing_vote_evidence []、`article_text_source=canonical(原稿のまま)`。

## KP(現行Production: A-1+課題②)
Adv: `hand down`(～を後の世代に受け継がせる)/`catch sight of`(～をふと目にする)/`catch one's breath`(息を整える)。Std: `tortoise-shell combs`(べっ甲のくし)/`smile through one's tears`(涙を浮かべながらほほ笑む)/`the magi`(東方の三博士)。QA 全PASS、gloss整合 ALIGNED。Adv英語解説(15語以内)3件OK。

## 試聴ページ・検査
`user_test/family_z_gift_of_the_magi_01/`(index/standard/advanced、Std/Adv切替、通し・パート別再生、全スクリプト、KP2列、開発者向け情報なし)。local page_verify(`page_verify_local.json`): `user_page_standard_check overall=PASS`、index audio35/standard37/advanced38 全再生OK、http>=400 0、console error 0、file://なし、A2/B1ラベルなし。(local簡易serverはRange非対応のため `seek_ok_all=false`、公開側で再検証。)
公開page_verify(`er026_fz_play_verify_17.py`、Playwright実再生、JST 08:26、証跡=`page_verify_public.json`): URL=https://shimomura055.github.io/eigo-radio/user_test/family_z_gift_of_the_magi_01/index.html 。index audio35・standard 37・advanced 38 すべて plays_ok(plays_failed 0)、seek_ok_all=True(3ページ)、http>=400 0、console error 0、file://なし、A2/B1ラベル漏れなし、KP表 index6/standard3/advanced3、通し長 Std 296.51秒/Adv 278.46秒。

## 費用(実績、`cost_log.jsonl` / `e2e_stage_log.jsonl`)
累計 **33.19円**(上限100円・目標70円): Writer(r0/r1/r2/std_adjust)12.49 + plan/support 0.64 + kp 1.13 + tts_b1b(Adv)9.17 + tts_a2(Std)9.76 = 33.19円。再生成・retry 追加費用はkp1_ja 1回(<0.1円)のみ。10-24 JST日次累計(着手時260.07円)に加算して約293円(並行Y/KP分別)。制作所要時間: 登録約45分(原作取得・Seed・test・全回帰[約14分]を含む) + 制作各段(Writer 74+72秒、plan/support 約2分、kp 107秒、TTS 4:41+4:06、完成段 2:26) = 実行約18分。
