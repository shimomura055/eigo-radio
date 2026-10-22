# FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01 EVIDENCE_01(2026-10-22、調査・証拠提出のみ。API 0・新規TTS 0・費用0)

ユーザー原文: `docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01_USER.md`。完了条件=ユーザーが直接音声を聴き、各ASRの判定結果と照合できること。

## 0. 試聴ページ

https://shimomura055.github.io/eigo-radio/user_test/fx_kp_audio_ng3_listen_01/index.html (push後に有効)

12本(3件 x 4 attempt)すべてが再生できる(mp3変換コピー、元wav無変更)。生成script: `er107_fx_kp_audio_ng3_listen_page_01.py`。全値の機械可読版: `docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/evidence_data_01.json`。再生検証: `play_verify_local_01.json`(ローカルserver)、`play_verify_pages_01.json`(公開Pages)。

使用モデル: TTS=`gemini-3.8-flash-lite-tts`(voice Aoede、backend `speech_metadata_flash_lite`)[attempt json `model`/`voice`] / Primary=OpenAI `gpt-4o-mini-transcribe` / Secondary=Azure Speech STT `en-US`(phrase_list 0)[`raw_usage_log.jsonl` `model_id`] / Whisper(第3判定)=本番設定 faster-whisper `small`/int8/cpu(`er104_kp_three_asr_vote_01.py:30-31`)。

## 1. 重要な事実(先に結論)

- 3件とも、本番では**Whisperは1度も呼ばれていない**(coffee a2=NG_BOTH、coffee b1b最終=NG_PROTECTED_DISSENT、small_bag a2=NG_BOTH。`review_lock_state.json` `last_attempts_log[].asr_judgement.vote.whisper_called=false`)。設計上、P/S両NGまたは反対票側に保護差(数値)があるときはWhisperを呼ばない(`er104_kp_three_asr_vote_01.py:138-148 whisper_needed`、`tally`の`NG_PROTECTED_DISSENT`)。
- JRE2報告(`RESULT_01.md:65`)の「Whisperが`Pump Ones Fest`でNG」の保存記録(ファイル)は**見つからなかった**(Grep: docs/・tools/・er019_output/にヒットなし。`RESULT_01.md`本文のみ)。今回、保存wav全12本を同一設定でlocal再判定した結果、`Pump Ones Fest`が出るのは**coffee Advanced(b1b)のattempt#1の1本のみ**で、HR待ちとして残った最終wav(各件のattempt#4)ではない。coffeeの保存wav 8本のうちWhisperが一般的な誤読を示すのは1本のみ(下表)。したがって`RESULT_01.md:65`の「音声自体が不良で、ゲートは正しく止めた」は、本調査の12本全数の再判定では支持されない(coffeeについて)。ただしこれは音声を聴いた判断ではない(ユーザー試聴で確定)。
- Whisperの再判定値は「参考(本番の判定には使われていない)」。ASR転写は事実の並記であり発音正否の断定ではない。

## 2. 一覧表

### 2-1. 概要(依頼書 §2 の項目)

| 項目 | N1: pump one's fist (Standard) | N2: pump one's fist (Advanced) | N3: novelty minaudière (Standard) |
|---|---|---|---|
| 対象記事・レベル | coffee_prices `run_jre_01` / a2 | coffee_prices `run_jre_01` / b1b | small_bag `run_jre_01` / a2 |
| 正しいKey Phrase(判定canonical=TTS入力) | `pump one's fist`(rank1=KP1、記事表記`pumps its fist`から一般化) | 同左 | `novelty minaudière`(rank1=KP1、変更なし。アクセント`è`保持) |
| 最終判定 | `HUMAN_REVIEW_REQUIRED`(final_status=STOPPED)、17:40:32 | 同左、17:43:47 | 同左、18:03:58 |
| HRに至った理由 | 4回(Minimal 2回+English Lock 2回)全てASR投票不合格。最終#4はP=NG・S=NG→`NG_BOTH`(`secondary_value_diff`) | 最終#4はP=PASS・S=NG(Azureの`1's`が数値保護差)→`NG_PROTECTED_DISSENT`(`dissent_protected_diff:azure`)。#1-#3は`NG_BOTH` | 4回全てP=NG・S=NG(ともに`ASR_VALIDATION_UNCERTAIN`、loanword)→`NG_BOTH`(`secondary_not_accepted`)。Pronunciation Ledger/research 0件(`NO_SOURCE`) |
| TTS再生成・ASR再判定の履歴 | TTS 4回・ASR 4回(各attempt=OpenAI+Azure各1回)。HR確定後の再生成・再判定は**なし**(現在も`review_lock_state` `HUMAN_REVIEW_REQUIRED`のまま、HR queue追記のみ) | 同左(TTS 4回・ASR 4回) | 同左(TTS 4回・ASR 4回)。Perplexity発音research 1回が`HTTP 401`で失敗 |
| 出典 | `coffee_prices__run_jre_01/a2/audit/review_lock_state.json` `kp1_en`、`.../a2/narration/attempts/kp1_en_attempt{1-4}_*.json`、HR queue `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl:114`、`er011_output/attempt_history.jsonl:16937`、`raw_usage_log.jsonl:53-64` | `.../b1b/audit/review_lock_state.json`、attempts、HR queue:115、attempt_history:16953、`raw_usage_log.jsonl:99-110` | `small_bag__run_jre_01/a2/audit/review_lock_state.json`、attempts、HR queue:116、attempt_history:17070、`raw_usage_log.jsonl:63-75`(75=Perplexity 401) |

attempt構成の出典: `er003_v1_repro01_main_generate.py:831-862`(Primary=Minimal指示2回→不合格時のみEnglish Lock指示2回、合計最大4回、最終slotのNGのみHR queue投入)。attempt#1-#2=route `custom_60ebc452`(Minimal)、#3-#4=route `custom_31eb2f72`(English Lock)[attempt json `route`]。

### 2-2. 全attempt別の3系統ASR(12本。PASS/NGは各attempt json・`review_lock_state.json`の保存値。★=保存値なし)

PASS/NGの付け方: attempt#3/#4は`review_lock_state.json` `last_attempts_log[].asr_judgement.vote.{primary,secondary}.pass`の保存値。attempt#1/#2はper-attemptのvote blockが保存されておらず、Primaryはattempt jsonの`audio_classification`(NORMALIZED_MATCHをPASS)、Azureは最終NG・同一転写のattempt#3/#4保存値からの推定(★)。Whisper(参考)は今回の保存wav再判定の転写を既存Validator(`classify_asr_match`+同音救済)に通した単独判定(`evidence_data_01.json` `whisper_offline_*`)。

#### N1: coffee_prices a2 / `pump one's fist`

| # | 指示 | OpenAI(Primary)転写 / 判定 | Azure(Secondary)転写 / 判定 | 本番state | Whisper(本番) | Whisper(参考・local) |
|---|---|---|---|---|---|---|
| 1 | Minimal | `Pump one's fist.` / PASS(NORMALIZED_MATCH) | `Pump 1's fist.` / NG★ | NG(unified=NG_BOTH、vote block未保存) | 未実行(推定★) | `Pump One's Fist` / PASS |
| 2 | Minimal | `Pump one fist.` / NG(TRUE_CONTENT_MISMATCH) | `Pump 1's fist.` / NG★ | NG(同上) | 未実行(推定★) | `Pump one's fist` / PASS |
| 3 | English Lock | `Pump one fist.` / NG | `Pump 1's fist.` / NG(protected_diff) | NG_BOTH | 未実行(`whisper_called=false`) | `Pump One's Fist` / PASS |
| 4(★HR待ち残存wav) | English Lock | `Pump one fist.` / NG | `Pump 1's fist.` / NG(protected_diff) | NG_BOTH | 未実行(`whisper_called=false`) | `Pump Ones Fist` / PASS |

#### N2: coffee_prices b1b / `pump one's fist`

| # | 指示 | OpenAI(Primary)転写 / 判定 | Azure(Secondary)転写 / 判定 | 本番state | Whisper(本番) | Whisper(参考・local) |
|---|---|---|---|---|---|---|
| 1 | Minimal | `Pump one's fist.` / PASS | `Pump 1's.` / NG★ | NG(vote block未保存) | 未実行(推定★) | `Pump Ones Fest` / NG |
| 2 | Minimal | `Pump one fist.` / NG | `Pump 1's fist.` / NG★ | NG(同上) | 未実行(推定★) | `Pump One's Fist` / PASS |
| 3 | English Lock | `Pump once fist.` / NG | `Pump 1's fist.` / NG(protected_diff) | NG_BOTH | 未実行(`whisper_called=false`) | `Pump One's Fist` / PASS |
| 4(★HR待ち残存wav) | English Lock | `Pump one's fist.` / PASS(NORMALIZED_MATCH) | `Pump 1's fist.` / NG(protected_diff) | **NG_PROTECTED_DISSENT** | 未実行(`whisper_called=false`。保護差dissentのため呼ばない設計) | `Pump One's Fist` / PASS |

#### N3: small_bag a2 / `novelty minaudière`

| # | 指示 | OpenAI(Primary)転写 / 判定 | Azure(Secondary)転写 / 判定 | 本番state | Whisper(本番) | Whisper(参考・local) |
|---|---|---|---|---|---|---|
| 1 | Minimal | `Novelty Manoir` / NG(ASR_VALIDATION_UNCERTAIN) | `Novelty Menottiere.` / NG(UNCERTAIN) | NG_BOTH | 未実行(推定★) | `Novel Team in Audiaire` / NG |
| 2 | Minimal | `Novelty menagerie.` / NG | `Novelty Minotti Air.` / NG | NG_BOTH | 未実行(推定★) | `Novel Team in Naughty Air` / NG |
| 3 | English Lock | `Novelty monadiere` / NG | `Novelty Menottiere.` / NG | NG_BOTH(`secondary_not_accepted`) | 未実行(`whisper_called=false`) | `Novel Team Menaudier` / NG |
| 4(★HR待ち残存wav) | English Lock | `Novelty Monadier.` / NG | `Novelty Menottiere.` / NG | NG_BOTH(`secondary_not_accepted`) | 未実行(`whisper_called=false`) | `Novelty Menardier` / NG |

出典: 各attempt json `er019_output/family_x_audio_production_wiring_01/<run>/<level>/narration/attempts/kp1_en_attempt{N}_*.json`(`asr_text`、`cascade_steps`)、vote blockは`<run>/<level>/audit/review_lock_state.json` `kp1_en.last_attempts_log[].asr_judgement.vote`(#3/#4のみ)、Whisper(参考)は`evidence_data_01.json`。wav sha256はattempt json `sha256`と保存wavの再計算が全12本一致、最終`kp1_en.wav`はattempt#4と同一sha(`evidence_data_01.json` `is_final_hr_wav`)。

## 3. 原因の切り分け

分類: 1=TTS実発音不良 / 2=ASR誤認識・誤判定 / 3=現行判定仕様・救済処理の問題 / 4=現時点では判断不能。**音声を聴いた判断は含まない**(ユーザー試聴で確定)。

### N1 coffee a2 `pump one's fist` — 暫定: 4(判断不能。ASR系統間で割れ。聴取で1/2/3のいずれかに確定)

確認済み事実:
- 4 attemptでAzureは同一の`Pump 1's fist.`(数値表記`1's`)。OpenAIは#1のみ`Pump one's fist.`(PASS)、#2-#4は`Pump one fist.`(`'s`が転写されない)。Whisper(local)は4本とも`one's fist`相当(`Ones Fist`含む)でPASS。
- 最終wav(#4)は、3系統が揃って同種の崩れを転写しているわけではない(P: `'s`欠落 / S: 数値`1's` / W: 正常相当)。系統間で割れている。
- 本番ではP/S両NGのため`NG_BOTH`で、Whisperは呼ばれていない。

推測(未検証): (a)語末`'s`+`f`の連続をTTSが弱く発音し、Primaryだけが`'s`欠落として捉えた(分類1の可能性)。(b)Azureは`one's`を`1's`と数値整形(inverse text normalization)して返す傾向があり、実発音は正しい可能性(分類2/3)。(a)(b)はどちらも未検証。

### N2 coffee b1b `pump one's fist` — 暫定: 3(最終wav#4について)+ #1-#3は4

確認済み事実:
- HR待ちとして残った最終wav(#4)は、OpenAI=`Pump one's fist.`(PASS)、Whisper(local参考)=`Pump One's Fist`(PASS)で、期待どおりの転写。Azureのみ`Pump 1's fist.`。これが数値の保護差(`value_guard.secondary: DIFF hyp_drop(b) None->'1'`)として**protected dissent**となり、`NG_PROTECTED_DISSENT`でHRに至った。Whisperは設計上呼ばれない(`er104_kp_three_asr_vote_01.py:138-148`)。
- 同じ件の#1-#3では、P/Whisperが割れている: #1 Whisper`Pump Ones Fest`(NG、JRE2報告の保存記録に該当しうる唯一のwav)、#2 P`one fist`/W正常相当、#3 P`once fist`/W正常相当。

推測(未検証): 最終wav#4が実際に正しく発音されているなら、Azureの`1's`(数値整形)に起因する保護差が過剰にHRへ送った可能性(分類3、必要ならAzureの`one's`→`1's`整形の扱い)。ただし本タスクでは仕様変更・修正はしておらず、その要否は聴取結果次第。#1-#3の`once fist`/`Ones Fest`は、TTSの実発音不良(分類1)かASR側の揺れ(分類2)かを転写だけでは区別できない。

### N3 small_bag a2 `novelty minaudière` — 暫定: 4(判断不能)

確認済み事実:
- 4 attemptで、OpenAI・Azure・Whisper(参考)のどの系統も`minaudière`に相当する転写を一度も返していない。さらに4回の転写が系統内でも揃わない(P: `Manoir`/`menagerie`/`monadiere`/`Monadier.`、S: `Menottiere.`/`Minotti Air.`/`Menottiere.`/`Menottiere.`、W: `Novel Team in Audiaire`/`Novel Team in Naughty Air`/`Novel Team Menaudier`/`Novelty Menardier`)。3系統が揃って同種の崩れを返しているわけではなく、「3系統一致」は確認できない。
- 先頭の`Novelty`は、Primary 4/4・Azure 4/4・Whisper #4で転写されている(Whisperの#1-#3は`Novel Team`)。
- Primaryの分類は4回とも`ASR_VALIDATION_UNCERTAIN`(loanword、`entity_like_source=["loanword"]`)で、`TRUE_CONTENT_MISMATCH`(明確な不一致)ではない。発音辞書は`NO_SOURCE`(HR queue:116 `pronunciation_lookups`)で、発音research(Perplexity)は`HTTP 401`で失敗(`small_bag__run_jre_01/raw_usage_log.jsonl:75`)。
- TTS入力: `tts_safe_kp_en("novelty minaudière")`の戻り値は`novelty minaudière`(アクセント`è` U+00E8を保持)。これは関数実行で確認した値であり、Geminiへ実際に送信された文字列そのもののログは存在しない(未確認)。
- 判定canonicalもアクセント付き(HR queue:116 `canonical_text`)。

推測(未検証): 低頻度のフランス語借用語のため、どのASRも綴りに一致する転写を出せない可能性が高い(分類2または3: 検証手段がない)。実発音が適切かは転写だけでは判断できない。聴取で適切なら分類2/3、不適切なら分類1。

### 共通: `one's`形の生成履歴とTTS入力(N1/N2)

- 記事の選定句`pumps its fist`(source_span/display_phrase)→ canonicalizationで`pump one's fist`へ一般化(`normalization_reason=generalize_person_dependent_reference`、`changed_from_display_phrase=true`、reasoning: 擬人化された`wallet`に依存する所有格`its`を辞書的一般形`one's`へ、動詞を原形`pump`に)[`coffee_prices__run_jre_01/{a2,b1b}/key_phrases/keywords_canonicalized.json` items[0]]。`japanese_gloss_tts`はa2=`自分のこぶしを突き上げて喜ぶ`、b1b=`自分の拳を突き上げる`(同ファイル)。KP英語音声(kp1_en)のTTS入力は英語KPのみで、`tts_safe_kp_en("pump one's fist")`=`pump one's fist`(関数実行で確認。ASCII apostropheのまま)。
- `one's`はTTS・ASRの双方で`one's`/`1's`/`once`等に揺れやすい語形である可能性があるが、それ自体の裏付けは本調査では未確認。

## 4. 旧記述との差分・要約(Fable向け)

- `RESULT_01.md:65`(JRE2)の「coffee kp1は音声自体が不良」は、coffee 8wav全数のWhisper再判定では1本(b1b#1)しか支持されない。最終wav(各#4)は、a2はWhisper PASS・Primary/Azure NG、b1bはPrimary/Whisper PASS・Azureのみ数値保護差NG。
- 未確認: Gemini TTSへ実際に送られた文字列、Azure STTが`one's`を`1's`と返す一般傾向(今回の12本はcoffeeの8本中8本がAzure=`1's`で一貫している事実のみ確認)、各attemptの音声が実際に正しいか(ユーザー試聴)。
