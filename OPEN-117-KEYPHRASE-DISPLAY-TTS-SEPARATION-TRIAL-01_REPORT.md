# OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-01

管理ID: OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-01(Phase 1のみ)
種別: 短い隔離Trial(ユーザー承認済み、2026-09-06)
Production変更: なし(コード・Prompt・CURRENT_SPEC・status格上げ、いずれも無変更)
Phase 2(Theme 2 A2/B1のProduction正式経路での再生成)は本タスクでは実施していない。

## 0. 背景

`OPEN-117-KEYPHRASE-TILDE-GATE-RECHECK-01`(既存Report参照)で、Key Phrase
日本語gloss中の「～」を含む訳語はTTS(Production Batch API)で安定して
読めず、3/3(先頭単独「～を示す」、複合形「～を示す、～を指し示す」、
波ダッシュ版)すべて`TRUE_CONTENT_MISMATCH`で`STOPPED`となる一方、対照の
「何かを示す」は1/1合格(`NORMALIZED_MATCH`)と確定していた。規約B
(「～」不使用、gloss自体を自然な言い切り形へ書き換える)は維持したまま、
「表示用の辞書的表記」(「～を示す」)と「TTS読み上げ用テキスト」
(「なになにを示す」)を分離する方式が有効かを、本Trialで確認した。

## 1. 実装方法(TTS方式: Production標準Batch API)

RECHECK-01と同一のTrial手法を再利用した。

- Production関数`er003_v1_sing01_voice01_generate.generate_charon_japanese`
  (voice=Charon、model=`p9a.JAPANESE_MODEL_NAME`=`gemini-3.1-flash-tts-preview`、
  **Batch API**、`JAPANESE_STYLE_PREFIX`)を**Trial scriptから直接呼んだ**。
- 今回のTTS用テキストはいずれも「～」等のplaceholder記号を含まないため、
  Production正式経路(`generate_charon_japanese_with_reading_safety`、
  ゲート`detect_gloss_placeholder_notation`込み)を通しても本来ゲートには
  引っかからない対象である。低レベル関数を直接呼んだのはRECHECK-01との
  手法的一貫性のため(ゲートを迂回する目的ではない)。
- Productionコードは無変更・monkeypatchなし。ASR検証・Cascade判定・
  Duration異常検知は`generate_charon_japanese`内部の既存Production機構
  (`ja_secondary`のCascade、`er007_ja_asr_validator_01.classify_ja_asr_match`、
  `safety.detect_duration_anomaly`)がそのまま動作した。
- cost計測は`er005_cost_logger.install()`経由(Production標準の計測経路)。

script: `er011_open117_keyphrase_display_tts_separation_trial_01.py`
出力: `er011_output/open117_keyphrase_display_tts_separation_trial_01/`
(`results_open117_display_tts_sep.json`、`trial/narration/*.wav`(12件)、
`player.html`、`raw_usage_log_open117_display_tts_sep.jsonl`、
`cost_summary_open117_display_tts_sep.json`)

## 2. 入力別結果表(全12件、すべてstatus=OK)

| # | 表示用 | TTS用 | 結果 | 最終ASR書き起こし | 最終分類 | attempts | duration(trim後) |
|---|---|---|---|---|---|---|---|
| 1 | ～を示す(run1) | なになにを示す | OK | 何々を閉めす。 | PHONETIC_MATCH(attempt1) | 1 | 2.63s |
| 2 | ～を示す(run2) | なになにを示す | OK | 何々を締めす | PHONETIC_MATCH(attempt1) | 1 | 2.54s |
| 3 | ～を指す(run1) | なになにを指す | OK | 何々をさす | PHONETIC_MATCH(attempt1) | 1 | 1.95s |
| 4 | ～を指す(run2) | なになにを指す | OK | 何々を指す | PHONETIC_MATCH(attempt2、attempt1は"~をさす"でTRUE_CONTENT_MISMATCH) | 2 | 2.19s |
| 5 | ～につながる(run1) | なになににつながる | OK | 何々に繋がる | PHONETIC_MATCH(attempt2、attempt1は"~に繋がる"でTRUE_CONTENT_MISMATCH) | 2 | 2.07s |
| 6 | ～につながる(run2) | なになににつながる | OK | 何々につながる | PHONETIC_MATCH(attempt2、attempt1は"なになにつながる"[「に」欠落]でTRUE_CONTENT_MISMATCH) | 2 | 2.21s |
| 7 | ～を意味する(run1) | なになにを意味する | OK | 何々を意味する | PHONETIC_MATCH(attempt1) | 1 | 2.08s |
| 8 | ～を意味する(run2) | なになにを意味する | OK | 何々を意味する | PHONETIC_MATCH(attempt1) | 1 | 2.03s |
| 9 | 何かを示す(対照A) | 何かを示す(分離なし) | OK | 何かを締めす。 | PHONETIC_MATCH(attempt1) | 1 | 2.06s |
| 10 | ～を示す、～を指し示す(対照B) | なになにを示す、なになにを指し示す | OK | 何々を示す、何々を指し示す | PHONETIC_MATCH(attempt1、1文中2箇所とも安定) | 1 | 3.95s |
| 11 | ～を示す(代替1) | なにかを示す | OK | 何かを閉めす。 | PHONETIC_MATCH(attempt1) | 1 | 1.76s |
| 12 | ～を示す(代替2) | あるものを示す | OK | あるものを示す。 | NORMALIZED_MATCH(attempt1) | 1 | 1.95s |

異常長・無音・ノイズ: 12件中0件(`safety.detect_duration_anomaly`は全件
"is_anomaly": false相当、全attemptが正常範囲[1.76〜4.04秒]の生音声長)。
fallback(minimal instruction経路)使用: 12件中0件(全件、標準経路2回以内で
解決)。

音声: `er011_output/open117_keyphrase_display_tts_separation_trial_01/player.html`
(12件のwavを埋め込み再生可能)。詳細JSON:
`er011_output/open117_keyphrase_display_tts_separation_trial_01/results_open117_display_tts_sep.json`。

## 3. 「なになに」vs「何か」等の比較

- **「なになに」(4主対象×2run=8件)**: 8件中5件がattempt1でPHONETIC_MATCH、
  3件(#4「指す」run2、#5「につながる」run1、#6「につながる」run2)は
  attempt1が`TRUE_CONTENT_MISMATCH`(ASRが「なになに」を**tilde記号
  「~」そのもの**として書き起こした、または助詞「に」を1箇所欠落)、
  attempt2で回復してPHONETIC_MATCH。**12件中STOPPEDは0件**であり、
  RECHECK-01の「～」直接投入(3件とも3回上限まで使い切ってSTOPPED)とは
  明確に異なる。
- **「何かを示す」(対照A)**: attempt1でPHONETIC_MATCH(RECHECK-01時点では
  `NORMALIZED_MATCH`だったが、今回はASRが「閉めす」と表記ゆれしたため
  `PHONETIC_MATCH`。判定は一貫してPASS)。
- **代替表現**: 「なにかを示す」(ひらがな表記)・「あるものを示す」も
  いずれもattempt1でPASS。今回試した4種類の口語的言い換え
  (なになに/何か/なにか/あるもの)は、いずれも安定して発話・検証できた。
- **複合形(対照B)**: Trial-13 kp4_ja実gloss相当の「なになにを示す、
  なになにを指し示す」(1文中に「なになに」が2回出現)もattempt1で
  一発PASSであり、単発形より不安定になる兆候は見られなかった。

### 追加発見(read-only、既存Production記録との整合)

`er006_output/pool_pilot_01/pool_benches_luna/b1b/audit/
tts_generation_results.json`(ER-006-KP5-CANONICAL-BUG-01で報告された
「associate with」の二重slot placeholder[「〜を…と結びつける」]の実
Production記録)を確認したところ、標準attempt2/5・fallback attempt1で
ASRが**「それを何々と結びつける。」「何々を、何々と結びつける。」**と
書き起こしていた(いずれも当時の生placeholder canonicalと不一致で
`TRUE_CONTENT_MISMATCH`のまま)。これは、TTSモデル(Charon)が
「〜」「…」のようなplaceholder記号を、しばしば実在の日本語単語
「何々」(なになに、「しかじか」と同義の口語的不定代名詞)として
**自発的に音声化する傾向がある**ことを示す既存の実データであり、
今回のTrialで「なになに」というTTS用テキストが安定して発話・認識
された理由と整合する(TTSにとって「何々」は未知の断片ではなく、
学習データ中に存在する自然な語彙だったと考えられる)。

## 4. 意味対応の評価

- 「～」(dictionary-style placeholder、目的語等が省略されていることを示す
  記法)と「なになに」(口語的な不定代名詞、「しかじか」と同義)は、
  「具体的な内容を示さず、動詞の対象がそこに入ることを示す」という
  **役割そのものは対応している**。「何か」(something)は「不特定の
  何らかの物事」という意味であり、「なになに」(such-and-such)とは
  厳密には異なるニュアンス(「何か」は存在を示す不定語、「なになに」は
  空欄・言い換え対象を指す言葉)だが、いずれも日本語として自然で、
  「gloss中の省略された目的語」という元の意図を壊さない口語的解決策
  という点では両方成立する。
- 「なになに」は辞書には載っていないが日常会話で普通に使われる語
  (例:「なになにをする、みたいな」)であり、**幼稚語・造語ではない**。
  ただし、実際に音声として聞いたときに英語圏学習者向けA2/B1リスナーに
  とって聞き取りやすい・意味が取りやすいか(「何々」という単語自体を
  知らないリスナーが違和感を持たないか)は、客観指標(duration・
  attempts数・ASR安定性)だけでは判定できず、**実際にplayer.htmlを
  聴いた人間の主観評価が必要**(本Trialの範囲外、STOP条件参照)。
- 既存A2/B1のComment・gloss文体([CURRENT_SPEC.md]既存記述)には
  「なになに」「何々」を使った表現の前例は見当たらなかった(read-only
  検索で確認、`grep`該当なし)。したがって仮に採用する場合は、既存の
  文体規約へ新しい語彙(「なになに」)を追加することになる(規約自体の
  変更はProduction採用時にユーザー判断が必要)。

## 5. 一般化可能な仕様として成立するか(read-only、実装なし)

### 5.1 規則変換 vs Prompt二重生成

- **規則変換案**(表示用「～」を機械的に「なになに」へ置換するだけで
  TTS用テキストを自動生成): 今回の4例(を示す/を指す/につながる/を意味
  する)では単純な文字列置換(「～」→「なになに」)がそのまま自然な
  TTS用テキストになった。ただし、「～」の直後に来る助詞・活用形に
  よっては置換結果が不自然になる可能性がある(例: 「中～高強度」のような
  範囲notation[Prompt規約Aでカバーされる別パターン]や、「～」が2つの
  異なる意味役割[目的語A・目的語B]を持つ二重slot[「～を…と結びつける」]
  では単純な一律置換だけでは意味が通らない可能性が高い、本Trialでは
  検証していない)。したがって「規則変換」は**単一slotの動詞句パターン
  (先頭「～」+助詞1つ)には有効そうだが、一般全パターンをカバーする
  保証はない**。
- **Prompt二重生成案**(選定Prompt側に表示用`japanese_gloss`とTTS用の
  新フィールド[例: `japanese_gloss_tts`]を両方生成させる): LLMに
  文脈全体を渡して生成させるため、二重slot等の複雑なパターンにも
  個別に自然な言い回しを選ばせられる可能性がある一方、新しいQA項目
  (2フィールド間の意味整合チェック)が必要になり、Prompt改修・
  既存QA(`qa_*`11項目)への影響評価が必要。

現時点でのSonnetの見解(実装しない、報告のみ): 対象が「先頭「～」+
単一助詞」パターン(規約Bが既にカバーする典型例の大半)に限定される
なら規則変換で足りる可能性が高いが、二重slot等の非典型例が残る限り、
安全側に倒すならPrompt側での明示的な二重生成の方が取りこぼしが少ない。
どちらを採るかはユーザー判断(仕様設計そのもの)。

### 5.2 影響範囲一覧(read-only、実装しない)

`keywords_canonicalized.json`スキーマへTTS用フィールドを追加する場合、
以下への影響が確認された(いずれも読み取り調査のみ、変更なし)。

1. **選定Prompt**(`er003_v1_translator_briefs/
   b1_p2_keywords_l_prompt_template.txt`): 新フィールドの生成指示・
   規約Bの記述追加が必要(現在は`japanese_gloss`1フィールドのみ生成)。
2. **Canonicalization**(`er003_key_words_canonicalization.py`、
   `keywords_canonicalized.json`スキーマ): `japanese_gloss`単一
   フィールドの構造(`er003_output/*/keywords_canonicalized.json`で
   確認、`items[].japanese_gloss`)を2フィールド構成へ拡張する必要。
   既存の11項目QA(`qa_*`)がどちらのフィールドを検証対象にするか
   の設計判断が必要。
3. **Master Audio Store cache identity**(`er006_master_audio_store_01.py`):
   `AudioCacheKey.canonical_text`(コード確認: 47行目)から
   `canonical_text_hash`(56-57行目、`sha256(canonical_text)[:16]`)を
   導出しキャッシュキーの一部に使っている。**表示用とTTS用を分離すれば、
   キャッシュキーの`canonical_text`は必然的に「TTS用テキスト」の方を
   使うべきになる**(現状は`japanese_gloss`＝両方兼用のテキストを
   そのままcanonical_textとして使っている実装であるため、分離後は
   TTS用テキストをcanonical_textとして渡すよう呼び出し側を変更する
   必要がある。既存のtrim v2/margin030等のversionキー[`_CACHE_KEY_FIELDS`
   38行目確認: `canonical_text_hash`, `audio_processing_version`,
   `sample_rate`, `channels`]自体の構造は変更不要だが、渡す値の選択が
   変わる)。
4. **review_lock**(`er011_human_review_lock_01.py`
   `@review_lock.guarded_generate("ja")`): `generate_charon_japanese`が
   受け取る`text`引数がTTS用テキストになる(現状のcanonical text概念と
   同じ扱いになるため、構造変更は不要と見られるが要確認)。
5. **Assembly**(記事音声組み立て): Key Phraseセグメントの音声は
   TTS用テキストから生成された音声であり、表示(記事ページ・字幕的
   表示があれば)は表示用テキストを使う、という2系統の値を正しく
   参照し分ける実装が必要(現状はAssembly段では単一の`japanese_gloss`
   のみを前提にしている可能性が高い、Assembly側コードの詳細調査は
   本Trialの範囲外)。
6. **表示側**(記事ページ・PDF等の表示用途があれば): 表示用テキスト
   (「～を示す」)をそのまま使い続けられる(変更不要)。

**Phase 2に向けた設計メモ**: 上記6項目のうち1〜4は「フィールド追加+
呼び出し側の参照先変更」で完結しそうだが、5(Assembly)は既存コードの
実際の参照経路を精査しないと影響範囲が確定できない。本Trial
(Trial adapterで低レベル関数を直接呼ぶ方式)だけでは、Assembly・
選定Prompt・Canonicalization・Master Audio Store呼び出し側という
Production正式経路の複数箇所を横断的に変更する必要があるタスクを
代替できない。すなわち**Trial adapterはPhase 1の安全な動作確認には
十分だが、Phase 2(Production正式経路での配線)には別途上記1〜5の
実装作業(スキーマ変更・Prompt改修・呼び出し側修正)が必要**という
見解である。

## 6. gateとの関係

- 今回のTTS用テキスト(「なになに」「何か」「なにかを示す」
  「あるものを示す」等)はいずれも`_GLOSS_PLACEHOLDER_CHARS`
  (`〜`/`～`/`…`)を含まないため、`detect_gloss_placeholder_notation`
  ゲートの対象外である(コード上も実行結果上も、ゲートへ到達する前に
  自然にPASSする)。
- 整理: 「ゲートは常に**TTSへ渡すテキスト**(=TTS用テキスト)に対して
  適用され、表示用の「～」は分離設計であればそもそもTTSへ渡らないため
  対象外になる」という想定整理は、本Trialの結果と矛盾しない
  (今回はTTS用テキストに「～」を含めなかったため、ゲート自体を
  経由していない。Phase 2でこの整理を正式に実装する場合、
  「表示用フィールドにだけ「～」が残ることを許容し、TTS用フィールドに
  「～」が残っていた場合のみゲートを適用する」という仕様変更が
  Production側に必要になる。これは**ゲートを弱める変更ではなく
  適用対象フィールドを明確化する変更**である)。
- ゲート自体のロジック変更は本Trialでは行っていない
  (`er003_audio_tts_asr_safety.py`は無変更)。

## 7. STOP条件の該当有無

- Trial結果が不安定: **該当なし**(12/12 OK、fallback未使用、異常長0件)。
- 「なになに」表現が不自然(客観指標上またはASR上): **客観指標上は
  該当なし**(duration正常範囲、attempts最大2回、PHONETIC_MATCHは
  既存Production機構による正当な判定)。**聴取者評価は本Trialの範囲外
  のため未確認**(4節参照、STOP対象ではなく別途確認事項として残す)。
- 表示用とTTS用の意味ズレ: **明確な意味ズレは確認されず**
  (4節参照、ニュアンス差はあるが役割は対応)。
- Validator・gate変更が必要: **該当なし**(6節参照、既存ゲート・
  Validatorとも無変更のまま整合)。
- 既存Production仕様との重大な矛盾: **該当なし**。
- 新たな`USER_DECISION_REQUIRED`: 8節参照。

## 8. Closeout分類

**VALIDATED**(Phase 1の範囲において、表示用/TTS用分離方式は
Production標準Batch APIで安定して発話・検証できることを確認した。
`VALIDATED`はProduction採用ではない)。

聴取者による主観評価(自然さ)は`USER_DECISION_REQUIRED`として残る
(player.htmlで実際に聴いた上でのユーザー判断が必要)。

## 9. Phase 2に進む場合の前提・必要なProduction変更の有無

Phase 2(Theme 2 A2/B1のProduction正式経路での再生成)へ進む場合、
以下がPhase 1未実施であり、進める前提として必要:

1. ユーザーによる「なになに」等TTS用表現の実際の聴取評価
   (player.html)、または代替表現(何か/なにか/あるもの等)からの選定。
2. 5.1節のどちらの方式(規則変換 or Prompt二重生成)を採るかの
   ユーザー判断・仕様確定。
3. 5.2節1〜5の実装(選定Prompt改修・Canonicalizationスキーマ拡張・
   Master Audio Store呼び出し側修正・Assembly参照先確認・review_lock
   確認)。
4. 上記実装後のregression test・runtime evidence取得。
5. `CURRENT_SPEC.md`への正式仕様追記(ユーザー`APPROVED_FOR_PRODUCTION`後)。

**Production変更は本タスクでは一切行っていない**(以下確認)。

## 10. cost

Production標準のGemini TTS Batch API(gemini-3.1-flash-tts-preview,
voice=Charon)+OpenAI ASR(gpt-4o-mini-transcribe)経路の実費、
計31 API call:

```
total_usd: 0.01572 (約2.52円)
  gemini_batch::batches.create          : $0.01469
  openai_asr::audio.transcriptions.create: $0.00103
```

計測方法: `er005_cost_logger.install()`(Production標準の計測経路)。
金額計算: `er011_open117_keyphrase_display_tts_separation_trial_01_cost_compute.py`
(RECHECK-01と同じ単価テーブル補完パターンを踏襲)。

## 11. Production変更なしの確認

- `er003_audio_tts_asr_safety.py`(ゲート本体): 無変更。
- `er003_v1_n3_01_tts_generate.py`(呼び出し側): 無変更。
- `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`
  (規約A/B): 無変更。
- `er003_key_words_canonicalization.py`・`keywords_canonicalized.json`
  スキーマ: 無変更。
- `er006_master_audio_store_01.py`: 無変更。
- `CURRENT_SPEC.md`: 無変更。
- monkeypatch: 使用していない(低レベル関数を直接呼んだのみ)。
- status格上げ: なし(`VALIDATED`はProduction採用ではない)。

## 12. 証跡

- Trial script: `er011_open117_keyphrase_display_tts_separation_trial_01.py`
- Cost計算script:
  `er011_open117_keyphrase_display_tts_separation_trial_01_cost_compute.py`
- 出力: `er011_output/open117_keyphrase_display_tts_separation_trial_01/`
  (`results_open117_display_tts_sep.json`,
  `cost_summary_open117_display_tts_sep.json`,
  `raw_usage_log_open117_display_tts_sep.jsonl`,
  `trial/narration/*.wav`(12件)、`player.html`)
- 過去データ根拠(read-only、repo内既存ファイル):
  `er006_output/pool_pilot_01/pool_benches_luna/b1b/audit/tts_generation_results.json`
  (3節参照)
- 関連既存Report: `OPEN-117-KEYPHRASE-TILDE-GATE-RECHECK-01_REPORT.md`
- 参照コード(read-only確認、変更なし):
  `er006_master_audio_store_01.py`(`AudioCacheKey`、
  `_CACHE_KEY_FIELDS`、`canonical_text_hash`)、
  `er003_output/a2_p2_keywords/A01/keywords_canonicalized.json`
  (`keywords_canonicalized.json`スキーマ例)
