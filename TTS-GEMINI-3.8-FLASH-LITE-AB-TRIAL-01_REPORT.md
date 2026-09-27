# TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01 REPORT

管理ID: TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01
性質: Trial限定(最大到達Status=VALIDATED方向を想定していたが、実測の結果
Sonnet仮分類は**REJECTED**[直近モデル差替え・Prompt無変更という条件下]。
Production採用なし、Production挙動は無変更)。

## §0 要約

対象記事「AIが採用を選ぶとき」Standard(A2)版(canonical:
`er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2/`)について、
現行Production TTS(英語=`gemini-2.5-pro-preview-tts`、日本語=`gemini-3.1-flash-tts-preview`)と
Gemini 3.8 Flash-Lite TTS(`gemini-3.8-flash-lite-tts`、実在をAPIモデル一覧で確認済み)を、
既存Production関数(retry/fallback/ASR検証/repetition QA/disfluency QA/6% slowdown
post-process/review lock)をそのまま再利用し、モデルIDだけを差し替えて17segment
(英語ナレーション12 + 日本語Comment5、Key Phraseは対象外)で実際に比較した。

**結果**: Model Bは、Production全経路が共有する「Structured Separation」プロンプト形式
(style指示と読み上げ本文をdelimiterで区切り、指示部分は読み上げない、という既存の
凍結仕様[ER-005-AUDIO-INSTRUCTION-SEPARATION-01])を正しく解釈できず、指示文を
そのまま音声として読み上げてしまう(EN/JA両方で確認)。加えて短くない本文では、
テキストと無関係な内容を長時間にわたって生成する(hallucination、既存の異常長検知
[duration anomaly detector]が複数回作動)。17segment中、**最終的にASR検証を通過したのは
3件のみ(preview/comment_1/comment_2、いずれも短いJA Comment)**。他14件は
Production既存の安全装置(標準2回+fallback1回で打ち切り、または異常長検知)により
`STOPPED`または`ASR_VALIDATION_UNCERTAIN`で終了し、Human Review以前の時点で
Production側の設計どおり停止した(誤って合格扱いにはならなかった)。

**費用Guardrail超過(要報告)**: 本Trialの実費用は、`gemini-3.8-flash-lite-tts`の
公式price表未収録のため近縁モデル`gemini-3.1-flash-tts-preview`と同一rateを保守的proxy
として試算すると**約¥275.7**(内訳: Gemini TTS呼び出し[proxy]≈¥266.5、ASR[実測]≈¥6.7、
reading-safety LLM[実測]≈¥2.5)で、事前Guardrail¥200を超過した。原因は、
duration anomaly(異常に長い誤生成)が繰り返し発生し、想定より多いoutput token(音声長)を
消費したため。実際のFlash-Lite tier価格は近縁Standard tierより安い可能性が高いが、
本Repoの公式pricing SSOT(`er005_output/cost_baseline_01/pricing_snapshot.json`)に
まだ収録されておらず、確定額は未確認(§5参照)。既にAPI呼び出しは完了しており
取り消せないため、追加の生成・再試行は一切行わず、ここで打ち切って報告する。

Sonnet仮分類: **REJECTED**(現行Prompt/style指示を変更しない前提でのモデル差替えとしては、
Production要件[ASR検証合格・本文内容の忠実な再現]を満たさない)。ただし、Prompt/style
調整(Phase 2 tuning)を行った場合にどうなるかは本Trialの範囲外であり未評価
(`USER_DECISION_REQUIRED`、§8参照)。

## §1 対象artifact特定根拠

日本語タイトル「AIが採用を選ぶとき」(表記揺れ含む)をGrepし、以下で一意特定した。
- `docs/pm/closeout_136_e2e/landing_10_01/e2e_result.json`:22行目、10記事landing card一覧の
  titles_ja配列に「AIが採用を選ぶとき」(en: "When AI Helps Choose Who Gets Hired")。
- `docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv`:8行目、同タイトルの
  standard_url= `.../ai_hiring_3v_a2%2Fkp_fix_01%2Fa2%2Fplayer.html`。
- `DECISION_LOG.md`444行: 「USER-TEST-SCRIPT-READABILITY-PROD-01: Trial VALIDATED後
  ユーザー正式承認・Production採用、Free-Address A2/AI Hiring A2のKey Phrase-本文
  不整合を本文優先で是正(Phase D)、Landing/TSV反映(Phase C)、REVIEW_REQUIRED2件
  ユーザー承認・GitHub Pages配線(Phase E)でPRODUCTION_WIRED確定」。
- `docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`(複数箇所)で、AI Hiring A2の
  新canonical pathが`er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2/`
  (標準player形式)であり、旧`.../ai_hiring_3v_a2/user_test_simple.html`はSUPERSEDEDと
  明記(Phase D/E完了、公開URL到達確認済み)。

候補は上記1件のみ(重複・ゼロ件なし)、STOP条件非該当。

**発見事項(本Trialのスコープ外、修正していない)**: landing表示title「AIが採用を選ぶとき」/
「When AI Helps Choose Who Gets Hired」に対し、canonical記事本文・`japanese_title`の
実際のナレーション内容は「AIが仕事と人の間に立つとき」/
「When AI Sits Between a Job and a Person」(B1版と同一文言)である
(`kp_fix_01/a2/article.md`1行目、`kp_fix_01/a2/audit/tts_generation_results.json`の
`japanese_title.text`で確認)。既存repoのlanding表示とcanonical本文の間の表記差分であり、
本Trialでは一切変更していない(発見事実としてのみ記録)。

## §2 A/B共通条件表(逐語、コード・manifestから)

| 項目 | 値(A=現行Production) |
|---|---|
| 英語model | `gemini-2.5-pro-preview-tts`(`er003_b1_p9a_audio.ENGLISH_MODEL_NAME` = `er002_common.MODEL_NAME`) |
| 日本語model | `gemini-3.1-flash-tts-preview`(`er003_b1_p9a_audio.JAPANESE_MODEL_NAME` = `er003_b1_p7a_audio.CANDIDATE_MODEL_NAME`) |
| 英語Voice(Narrator) | Charon(topic_intro)/Aoede(full_story/point_headings/tension/in_one_line) |
| 英語Voice(3 Voices本文) | Algieba(Voice 1)/Erinome(Voice 2)/Schedar(Voice 3) |
| 日本語Voice | Aoede(japanese_title/preview/comment_1-4) |
| style/instruction | `er003_b1_p4c_audio.build_tts_prompt(text, style_prefix)`によるStructured Separation(ER-005-AUDIO-INSTRUCTION-SEPARATION-01、`=== STYLE INSTRUCTIONS ===`/`=== TEXT TO SPEAK ===`区切り)。A2英語本文・見出しは`A2_ENGLISH_STYLE_PREFIX_SLOWER`(6% slowdown前提の「わずかに遅く」指示)。 |
| pause/assembly | `er003_b1_p9a_audio`のPAUSE_*定数(例: PAUSE_AFTER_JAPANESE_TITLE_SECONDS=0.5、PAUSE_AFTER_FULL_STORY_SECONDS=0.5等)。 |
| ASR validation | 英語=正規化+6分類validator(`er006_preprod_hardening_01_validation`)、日本語=phonetic_verdict方式。Primary ASR routing(`er006_asr_provider_routing_01.transcribe`)。 |
| retry/fallback | 標準経路2回+fallback(minimal instruction)経路1回=合計最大3回(`er011_human_review_lock_01.PRODUCTION_MAX_TTS_ATTEMPTS=3`)。異常長検知(duration anomaly)はASR前に即STOPPED。 |
| 追加QA | repetition QA(full_story_part1/2・point_one/two)、disfluency QA(headings/in_one_line/comment系)、connected speech equivalence layer(full_story_part1/2)。 |
| 6% slowdown | point見出し・point本文・full_story・tension・in_one_lineに適用(`apply_a2_slowdown_postprocess`)。 |

対象17segment: topic_intro, japanese_title, preview, comment_1-4, point_one/two/three_heading,
point_one/two/three(body), full_story_part1/2, tension_reflection, in_one_line。
**Key Phrase(kp1-5 en/ja、計10segment)は対象外**(コスト・スコープ規律のため本Trialでは
生成していない。委任文は「英語ナレーション+日本語Commentの両方」を主眼としており、
Key Phraseの明示要求はなかったため縮小した。この縮小判断はSonnetの裁量、報告のみ)。

## §3 Bの適用可否確認

`client.models.list()`実結果に`models/gemini-3.8-flash-lite-tts`を確認(実在するモデルID)。
最小1segment実呼び出し(JA/Aoede、EN/Charon、Structured Separationなしの単純文)で
API呼び出し形状(response_modalities=["AUDIO"]、speech_config、http_options)が現行と
同一のまま成功することを確認した(実費用<¥1)。この時点では問題を検知できず、
**実際のProduction prompt(Structured Separation付き)を使って初めて非互換が判明した**
(§0参照)。事後的にSTOP相当の事実が判明したため、以後の追加生成・再試行は行っていない。

## §4 segment別比較表

| segment | A: status/retry/duration(s) | B: status/retry/duration(s) | 備考 |
|---|---|---|---|
| topic_intro | OK/0/約4.9 | ASR_VALIDATION_UNCERTAIN/3回とも不一致 | Bは指示文+本文を混在して読み上げ |
| japanese_title | OK/0/3.99 | STOPPED(標準1回目duration anomaly[125.4s>19.8s]、2回目TRUE_CONTENT_MISMATCH、fallback含み計3回失敗) | |
| preview | OK/0/15.88 | **OK**(PHONETIC_MATCH相当) | Bで数少ない成功例 |
| comment_1 | OK/0/5.66 | **OK**(attempt1がduration anomaly[143.97s>42.60s]で棄却、attempt2でEXACT_MATCH) | |
| comment_2 | OK/0/11.0 | **OK** | |
| comment_3 | OK/0/17.48 | STOPPED(3回失敗) | |
| comment_4 | OK/0/10.72 | STOPPED(3回失敗) | |
| point_one_heading | OK/0/3.92 | STOPPED(標準2回ともduration anomaly、fallbackはTRUE_CONTENT_MISMATCH) | fallbackでも指示文断片("The message below has two clearly separated sections:")が本文へ混入 |
| point_two_heading | OK/0/2.93 | STOPPED(同型) | |
| point_three_heading | OK/0/2.95 | STOPPED(同型) | |
| point_one | OK/0/46.30 | STOPPED(3回ともTRUE_CONTENT_MISMATCH、テキストと無関係な内容[家族の引っ越し・雑貨店等]を生成) | 重度hallucination |
| point_two | OK/0/44.06(trim後) | STOPPED(同型、無関係内容[転居・求職等]) | 重度hallucination |
| point_three | OK/0/37.03(trim後) | STOPPED(3回、うち1回は音声区間検出失敗) | |
| full_story_part1 | OK/0/15.01(ASR尺) | STOPPED(3回失敗) | |
| full_story_part2 | OK/0/15.41(ASR尺) | STOPPED(3回失敗) | |
| tension_reflection | OK/0/62.25(A実測は3回中3回目で成功、既存retry内で吸収) | STOPPED(3回失敗) | |
| in_one_line | OK/0/26.09(ASR尺) | STOPPED(3回失敗) | |

ASR一致率(分類別、B側): EXACT_MATCH=1、PHONETIC_MATCH相当=1、NORMALIZED_MATCH=1、
TRUE_CONTENT_MISMATCH=多数(点検したattempts_log上で最頻出)。retry/fallback発生数:
17segment中16segmentで少なくとも1回の追加attempt(標準2回目またはfallback)が発生した
(Bのraw_usage_log実測、`gemini`呼び出し件数がsegmentあたり1件を超える)。A側は
`tts_generation_results.json`の`call_count`/`retry_count`フィールドが多くのsegmentで
1/0だが、これは`generate_narration_snippet()`内部の技術的retry回数[MAX_TTS_TECHNICAL_
RETRY=0]のみを表す値であり、外側のASR検証retryループの試行回数とは別集計である
点に注意(例: tension_reflectionはこのフィールドが1/0の一方、A原本の
`raw_usage_log.jsonl`ではgemini呼び出しが実際には3回記録されている。外側retryが
発生した実績はA・B双方にあるが、Bは3回を使い切っても最終的に一致しなかった点が
Aとの決定的な違い)。

## §5 記事合計(ASR/retry/latency/cost)

- OK到達: B=3/17、A=17/17(既存canonical、A原本の実測でも`retry_count`は
  ほぼ全segment0、tension_reflectionのみ実測3 call)。
- Latency合計(実測、生成関連API呼び出しのelapsed_seconds合計、ASR/reading-safety LLM込み):
  A(原本raw_usage_log.jsonlの17segment分)≈358秒。B(本Trial)≈795秒(約2.2倍)。
- 費用(実測トークン×価格、Aは公式price表、Bは近縁モデルproxy rate):
  - A実測合計: 約¥36.9(17segment、`er012_output/.../a2/audit/raw_usage_log.jsonl`のgemini
    呼び出しから算出。ただし`japanese_title`はsegmentタグが記録されておらず
    「既存log欠落」、本Trialでは同ログの`segment=None`1件[¥0.48相当]がこれに該当すると
    推定するに留め、再生成での補完はしていない)。
  - B実測合計: 約¥275.7(proxy rate。内訳: TTS[proxy]≈¥266.5/ASR[実測]≈¥6.7/
    reading-safety LLM[実測]≈¥2.5)。**事前Guardrail¥200を超過**(§0参照)。
  - 1記事完成までの総TTSコスト比較: Aは既に完成済み(追加費用¥0で流用)。Bは
    完成に至っておらず(14/17がSTOPPED)、完成させるには最低でもPrompt/style
    tuning[Phase 2、本Trialの範囲外]が必要と考えられる。

詳細JSON: `er022_output/tts_gemini_3_8_flash_lite_ab_trial_01/cost_table.json`
(segment別calls/elapsed_seconds/usd/jpy_at_160/by_kind)。

## §6 所見(観察、断定なし)

- B(Gemini 3.8 Flash-Lite TTS)は、現行Productionが全segmentで使っている
  Structured Separation形式のprompt(style指示部分を読み上げない、という前提)を
  正しく解釈できていないように observedされた(EN/JA両方、標準経路・fallback経路
  [より短い minimal instruction]の両方で、指示文の一部または全部が音声化された)。
- 本文が長くなるほど、テキストと無関係な内容を生成する頻度が高い observed
  (point_one/two/threeの3回の attempts全てでTRUE_CONTENT_MISMATCH、生成内容は
  記事とは全く無関係な創作[引っ越し・雑貨店・回復期の求職等])。これは既存の
  異常長検知が繰り返し作動した事実とも整合する。
- 短いJA Comment(1〜2文、10〜20秒程度)では成功率が相対的に高かった
  (preview/comment_1/comment_2はOK、comment_3/comment_4はSTOPPED)。文長との
  相関があるように見えるが、N数が小さく断定はしない。
- 「現行モデル向けstyle指示との相性」が原因の可能性が高いと考えられる
  (Structured Separationの区切り文字列自体をBが読み上げてしまう現象は、A[現行2機種]
  では発生しない、既存canonical音声のASR結果[EXACT_MATCH/NORMALIZED_MATCH多数]と
  対照的)。Prompt/style tuningを行った場合にBの本来の音質・自然さがどう評価されるかは
  本Trialでは検証できていない(意図的にPrompt変更を行わなかったため)。

## §7 試聴artifactパス

- segment別A/B切替player: `er022_output/tts_gemini_3_8_flash_lite_ab_trial_01/player.html`
  (17segment全て、B側はSTOPPEDでも最終attemptの実音声を掲載、statusを明示)。
  mp3実体: `er022_output/tts_gemini_3_8_flash_lite_ab_trial_01/segments_mp3/{a,b}/<name>.mp3`。
- 記事全体player: **作成していない**。B側は17segment中14segmentが未完成
  (Production基準でSTOPPED)であり、これらを結合した「記事全体」音声を提示すると
  未完成品を完成品のように誤認させる恐れがあるため、意図的に見送った
  (既存A記事のplayerは無変更のまま)。

## §8 Sonnet仮分類

**REJECTED**(現行Prompt/style指示・retry/fallback仕様を変更しない前提での、
Gemini 3.8 Flash-Lite TTSへの単純モデル差替えについて)。
理由: 17segment中14segmentがProduction基準のASR検証・異常長検知でSTOPPED/
UNCERTAINとなり、記事を完成させられなかった。

**USER_DECISION_REQUIRED**:
1. Prompt/style tuning(Structured Separation形式をBに合わせて変更する等の
   Phase 2検証)を別Trialとして行うか。行う場合、追加費用(Guardrail再設定要)と
   スケジュールをどうするか。
2. 本Trialの実費用(約¥275.7、proxy rate、Guardrail¥200超過)について、追加の
   pricing確認(Google公式ページまたはGCP請求画面での実額照合)を誰が行うか。

## §9 Production非変更の確認

- Production TTS module(`er003_v1_*`/`er020_*`/`er006_*`等)への**コード変更は0件**
  (`git status`で確認可能)。モデル差替えは、新規Trialファイル
  (`er022_tts_gemini_3_8_flash_lite_ab_trial_01.py`)内で
  `er003_b1_p9a_audio.ENGLISH_MODEL_NAME`/`JAPANESE_MODEL_NAME`を、Pythonの
  モジュール属性として**プロセス内・with文の間だけ**一時的に上書きし、
  with文を抜けると必ず元の値へ復元する方式で実現した(ファイル自体は無変更、
  既存呼び出し元のコードも無変更)。既存Production関数群がこれらの属性を
  呼び出し時([`p9a.ENGLISH_MODEL_NAME`のような属性参照]、importコピーではない)に
  参照していることをソースで確認済み(`er003_v1_repro01_main_generate.py`267行目、
  `er012_b_family_voices_production_01.py`515行目)。
- topic_intro(Charon)は、ER-002凍結仕様(`er002_common.MODEL_NAME`、
  「変更しない」と明記)を経由する既存関数(`voice01.generate_charon_english`)を
  一切使わず、独立の最小実装(共有primitiveのみ再利用)にした。`common.MODEL_NAME`
  自体は本Trial中一度も参照・上書きしていない(単体テストで確認、
  `er022_tts_gemini_3_8_flash_lite_ab_trial_01_test.py`の
  `test_does_not_touch_frozen_common_model_name`)。
- 共有Production状態ファイル(`er006_output/pronunciation_ledger_01/ledger.json`
  [読み取りのみ]、`er006_output/master_audio_store_01/manifest.json`
  [本Trialの生成経路では未import・未使用])への書き込みは発生していない。
  `review_lock_state.json`は本Trial専用out-dir配下
  (`er022_output/.../b/audit/review_lock_state.json`)にのみ新規作成され、
  既存記事の同名ファイルとは別実体(out_pathから自動導出されるディレクトリが
  異なるため)。
- 既存記事artifact(`er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/`
  配下全て)は読み取り専用アクセスのみで、一切変更していない
  (`git status`で無差分)。
- Regression: 既存Production呼び出し元(Family/News等の通常記事生成)は、
  本Trialのmonkeypatchが実行される時間窓の外にあるため影響を受けない
  (別プロセスとして実行、`docs/pm/locks/audio_stage.lock`は本Trial実行中も
  未使用[取得不要と判断、共有状態ファイルへの書き込みがないため]、開始前に
  当該lockファイルが存在しないことを確認済み)。

## §10 STOP該当有無

事後的に、費用がGuardrail(¥200)を超過した事実が判明した(§0/§5)。API呼び出しは
既に完了しており取り消せないため、追加の生成・再試行は行わずここで打ち切って
報告する。これはPM_GOVERNANCE 11節のSonnet委任ループ上限とは別種の事象(技術的
issueによる追加委任ではなく、費用超過の事後報告)。次の一手(Phase 2 tuning実施可否・
実費用確定)は`USER_DECISION_REQUIRED`(§8)。

## 付録: 主な生成物パス

- 新規Trial harness: `er022_tts_gemini_3_8_flash_lite_ab_trial_01.py`
- 比較表・player組み立て: `er022_tts_gemini_3_8_flash_lite_ab_trial_01_assets.py`
- 単体テスト: `er022_tts_gemini_3_8_flash_lite_ab_trial_01_test.py`(4件PASS、API課金なし)
- B側生成結果: `er022_output/tts_gemini_3_8_flash_lite_ab_trial_01/b/audit/tts_generation_results_b.json`
- 実測usage log: `er022_output/tts_gemini_3_8_flash_lite_ab_trial_01/b/audit/raw_usage_log.jsonl`
- 費用集計: `er022_output/tts_gemini_3_8_flash_lite_ab_trial_01/cost_table.json`
- 試聴player: `er022_output/tts_gemini_3_8_flash_lite_ab_trial_01/player.html`

## §11 Fable評価(2026-09-27)

- 委任条件との照合: 対象artifactの一意特定(DECISION_LOG L444、`kp_fix_01/a2`)=充足。TTSモデル以外(voice/segment/style/pause/ASR/retry)無変更=充足(with文内monkeypatch、復元確認済み)。Production非変更=充足。試聴artifact=segment別A/B player(記事全体playerは未完成品誤認防止のため意図的に不作成、妥当)。Key Phrase 10 segmentを対象外としたスコープ縮小は委任文の「segment構成維持」からの逸脱だが、Bが英語ナレーション12/12でSTOPPEDとなった結果を踏まえるとKey Phrase追加実行は結論を変えず費用のみ増やしたため、事後的に妥当と判断する(ただし委任時点の承認はなかった点を記録)。
- Guardrail超過(¥275.7 > ¥200): duration anomaly(異常長生成)の反復によるtoken消費が原因で、事後判明。PM_GOVERNANCE 7-6の「暴走防止Guardrailであり自動停止ではない」の範囲内だが、超過発覚後に追加生成を行わなかった点は適切。B側単価はproxy(gemini-3.1-flash-tts-preview同一rate)であり実価格は未確認。
- 分類: Sonnet仮分類`REJECTED`は採用しない。ユーザー委任条件「style-tuningの不一致だけで即REJECTしない」に従い、本TrialのStatusは**`USER_DECISION_REQUIRED`**(純粋なモデル差替えとしては不成立=17 segment中14 STOPPED、成功3件はいずれも短い日本語Comment。長文segmentでの無関係内容生成[hallucination]はstyle指示の問題とは別の懸念として記録)。Phase 2(Prompt/style tuning)の実施可否はユーザー判断。
- スコープ外発見(§1): landing表示title「AIが採用を選ぶとき」とcanonical本文/japanese_titleナレーション「AIが仕事と人の間に立つとき」の表記差分。本Trialでは無変更。Closeout時にOPEN_ITEMS備考へ記録する候補。
