# FAMILY-X-NEWS-2ARTICLES-E2E-01 RESULT_01 (委任_01, 2026-10-22 JST)

性質: 現行Production正式経路でのE2E(新Trial・新仕様・コード変更0)。最終ユーザー試聴PASSはユーザー本人の判断(AIは代行しない)。
Fable解釈の適用: 「Primary/Secondary両方PASS」= 本日PRODUCTION_WIREDの3-ASR多数決(OPEN-451)として現行既定のまま。PNAP(OPEN-450)・KP全文選定3件化(OPEN-454)も現行既定のまま(flag・コード変更なし)。

## 1. 記事ごとの結果
| 項目 | 記事A Prix Pascal | 記事B Tesla/SpaceX |
|---|---|---|
| slug / run | prix_pascal_ai_novel_prize / run_nws_01 | tesla_spacex_merger_talks / run_nws_01 |
| JAタイトル | AIと書いていない方は、応募できません。 | マスク氏の「良い考え」で、合併話が渋滞する？ |
| Std(a2) Status | USER_LISTENING_PENDING(完成候補) 299.64秒 | USER_LISTENING_PENDING(完成候補) 278.69秒 |
| Adv(b1b) Status | USER_LISTENING_PENDING(完成候補) 285.96秒 | USER_LISTENING_PENDING(完成候補) 272.58秒 |
| 試聴URL | https://shimomura055.github.io/eigo-radio/user_test/prix_pascal_ai_novel_prize_e2e_01/index.html | https://shimomura055.github.io/eigo-radio/user_test/tesla_spacex_merger_talks_e2e_01/index.html |
| 試聴ページ検査 | user_test_page_standard_check_01 PASS / HTTP200 / plays_ok 47/47・seek全OK・console error 0 | 同左 |
| text run dir | er019_output/prix_pascal_ai_novel_prize/run_nws_01 | er019_output/tesla_spacex_merger_talks/run_nws_01 |
| audio run dir | er019_output/family_x_audio_production_wiring_01/prix_pascal_ai_novel_prize__run_nws_01 | .../tesla_spacex_merger_talks__run_nws_01 |
| Ledger | VERIFIED 7 / AMBIGUOUS 1(F06 審査員・賞金) / REJECTED 0。B3採用 F01,F03,F05,F06,F07 | VERIFIED 7 / AMBIGUOUS 1(F04 遅延懸念) / REJECTED 0。B3採用 F01,F02,F04,F05,F07 |
| 音声segment | Std 11/11 OK, Adv 10/10 OK、retry 0、HR Lock全RESOLVED(17/16) | Std 11/11 OK, Adv 10/10 OK、retry 0、Lock全RESOLVED(17/15) |
| Gate | style_profile_gate PASS / key_phrase_source_gate 3/3 PASS(両level) / headroom valve: Advのみ発動(scalar 0.9956) | 全PASS、valve未発動 |
| PASS_WITH_WARNING(非ブロッキング) | Std 1: full_story_part2(SECONDARY_CONFIRMED)。Adv 0 | Std 2: topic_intro(SECONDARY_CORROBORATED)・full_story_part2。Adv 1: comment_1(SECONDARY_CONFIRMED) |
| KP(Std) | co-written with AI / behind the scenes / question shaped like a trophy | articles of incorporation / vote as a separate group / under review |
| KP(Adv) | go out of one's way / brace oneself for / shine a light on | turn on its head / articles of incorporation / fire the starting gun |
| KP 3-ASR投票 | 6件: PASS_DUAL(P+S)5・PASS_VOTE_2OF3(P+W)1(Adv KP2 "brace oneself for": Whisper決選がPASS=本番での自然発火) | 6件: PASS_DUAL 6(うちAdv KP2はStd音声のStore再利用+再判定 source=stored_evidence_rejudged) |
| 固有名詞アラーム(PNAP) | 0件(供給0・HR残0) | 0件(供給0・HR残0)。Musk/Tesla/SpaceXはアラーム対象外=発音不一致なし |
| kp_backend_used | fulltext_p2(両level、model gpt-6-luna、prompt_sha a12896f4…=設計固定値)・KP3件 | 同左 |

audit/evidence: 各audio run dirの entry_point.json / raw_usage_log.jsonl / {a2,b1b}/audit/{tts_generation_results,pronunciation_alarms,operator_alarm_report.md,pass_with_warning_listening_list,review_lock_state,style_profile_gate,key_phrase_source_gate,timeline}.json / key_phrases/keywords_runtime_metadata.json。ページ検査・再生evidence=docs/research/FAMILY-X-NEWS-2ARTICLES-E2E-01/{page_check_*,pages_play_evidence_*}.json、STOP確認=stop_check_*.json(rc=0)。

## 2. 品質観察・未解決(合否はFable)
1. 記事A: B3はF06(審査員・賞金は未確定)・F07(受賞作未発表)を採用したが、Writerは本文(Std/Adv)で「受賞作はまだ決まっていない/審査員・賞金は未確定」を明示していない(Stdは"special meeting to judge"の比喩のみ)。誤った断定(受賞作あり等)は無い。ユーザー注意事項(未確定点を正確に扱う)の明示的な伝達は欠ける。再生成は委任範囲外のため未実施(判断候補は§6参照)。
2. 記事B: 事実制約(合併は未決定・検討段階・株主承認ハードル・遅延は未報告)は本文・In One Lineに反映(「no delay has been reported」「the deal is still under review」、SpaceXのClass B株別議決を明記)。
3. 記事B Std topic_intro: ASRが"slow murder talks"(台本"Slow Merger Talks")と聞き取り、既存の多語同音救済(OPEN-439、ユーザー受入済み)でPASS_WITH_WARNING(SECONDARY_CORROBORATED)。ASR側の誤聞の可能性が高いが、**この1箇所は人が耳で確認することを推奨**。
4. 警告: `a2_derived_from_advanced_sha_mismatch`(観測のみ・両記事とも、既存仕様の警告記録)。
5. RF(Risk Flagger、非Blocking)候補: A Adv 1 / Std 1、B Adv 2 / Std 4(queueはreview_queue/post_en/配下)。
6. 既知OPEN-456 F3(Azure数値整形)該当: なし(数字を含むKP無し、KP HR 0)。KP選定の外側retry枯渇(kp_stage_failed.json)も発生せず。HR/STOP/人工entry なし。

## 3. retry/fallback整合
M2-fallback使用なし(両level)。TTS retry 0。KP選定は外側retry未使用(final_status=KEY_WORDS_STRUCTURE_PASS)。Writer R0〜R2・Adv/Std構造PASS。Store再利用は記事B Adv KP2のみ(Std wavをMaster Audio Storeから再利用し3-ASR投票を再判定)。

## 4. モデル/Voice/routing(実測、raw_usage_log・metadata)
Research/Ledger/B3/Writer/RF: OpenAI gpt-6-luna等(Research web_search、B3選定は既存routing)、RF追加gemini-3.5系。KP選定/canonicalization/gloss alignment/Preview・Comment・解説: gpt-6-luna。TTS: gemini-3.8-flash-lite-tts(speech_metadata_flash_lite、style_profile fx_20261017)、Voice: StdはAoede単独、AdvはAoede 4+Charon 6 segment。ASR: Primary=openai gpt-4o-mini-transcribe、Secondary=Azure speech-stt、Whisper=small/int8(preflight ok、決選時のみ)。モデルの「最新」性は既存Production routingに従う(本案件で新規選定なし)。

## 5. 実費(JPY、出典=各run cost.json・console・raw_usage_log)
| Stage | 記事A | 記事B |
|---|---|---|
| Research(web_search) | 5.652 | 26.769 |
| Fact Ledger | 5.482 | 16.031 |
| B3 storyline+丸め判断 | 6.072 | 7.143 |
| Writer R0-R2 | 16.545 | 17.134 |
| Adv/Std英訳 | 0.566 | 0.961 |
| Risk Flagger | 1.27 | 約1.6 |
| text小計(cost.json total) | 35.59 | 69.65 |
| 音声scaffold(Preview/Comment/KP選定/gloss/解説) | 1.29 | 2.87 |
| TTS(Gemini) | 11.32 | 12.71 |
| ASR(OpenAI primary / Azure secondary) | 3.11 / 2.73 | 3.34 / 7.95 |
| 日本語読み調査(OpenAI) | 約0.02 | 約35.1(gpt-5.6-sol+web_search 1回、"X"=エックスをPronunciation Ledgerに新規登録。1回限り、Ledger登録済み以降は0) |
| audio小計(runner表示) | 18.47 | 61.96 |
| 合計(記事セット=Std+Adv) | **54.06** | **131.61** |
- 2記事合計 185.67円(案件上限300円内)。当日累計見込み: 開始時971円+185.67=約1,157円(上限1,500円内)。未計上: Whisper(ローカル¥0)・Claude Code利用料。
- 量産単価見込み: 平均 92.8円/セット(2記事の単純平均)。記事Bの日本語読み調査(約35円)はLedger登録後は再発しない1回限りのため、除外した定常見込みは A 54.1 / B 約96.5 / 平均約75.3円。目標70円に対し、Research(web_search)費用が記事により大きく変動(B 42.8円 vs A 11.1円)することが支配的な差。KP関連: 3件化後の音声は A 6KP=PASS_DUAL5+W1、追加APIはWhisperローカル0。
- 単価未登録の呼出: なし(raw_usage_logの全行にprovider/model_id記録)。

## 6. 判断候補(Fable判断、A/B/C/D区分は私見)
- 記事A本文への「受賞作未決定・審査員/賞金未確定」の明示: 区分D(新しいユーザー注意事項の充足度判断)。選択肢=(a)現状を完成候補としてユーザー試聴へ(誤りなし)(b)Writer再生成(text〜audio約54円、推奨しない: 誤りが無く、1原則「必要十分で止める」)。推奨=(a)。
- 記事B日本語読み調査の約35円: 区分B(承認範囲内の既存仕様、Ledger登録で1回限り)。

## 7. 手順・時間
text並列(A/B約8分)→A audio(scaffold〜assemble 約10分)‖B scaffold→B audio(Store競合回避のためTTSはA→B直列)→ページ生成→push→Pages反映→再生検証。総所要約1時間。Production .py変更0(新規script: er019_nws_final_page_01.py / er019_nws_play_verify_01.py=試聴ページ専用、Production経路外)。
commit: 2febfdcb3(成果物)、SSOT=次commit。
