# design_key_phrase_advanced_english_explanation_trial_02.md

管理ID: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02`
性質: Trial(Product仕様確認、text優先)。Production変更ゼロ。

## 1. 目的とスコープ

過去`KEY-PHRASE-LEVEL-SPEC-TRIAL-01`は、Key Phrase選定/Standard・
Advanced差/Topic Word/解説言語を同時に変えたため、Phrase選定Prompt v1
の失敗(4セット全FAIL、想定一致5/20)でTrial全体がREJECTED寄りとなった
(`KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md` 340行)。そのREJECT理由は
Advanced英語解説そのものの失敗ではない(同REPORT §7.2で解説の語数・
難度・意味正確性は問題なしと実測記録済み)。

本Trialは**Phrase選定ロジックに一切触れず**、Hormuz(`OPEN-221`で参照
された既存完成済みAdvanced Key Phrase 5個、`er019_output/
family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/
hormuz__run_06_flashlite_full_kp/b1b/key_phrases/
keywords_canonicalized.json`)をそのまま使い、
**A(英語Phrase+日本語意味=現行仕様)** と **B(同一英語Phrase+平易な
英語解説=Advanced候補)** の解説言語だけをisolated Trialする。

## 2. 前回仕様の再利用(逐語)

`er017_key_phrase_level_spec_trial_01.py` `ADVANCED_USER_TEMPLATE`
(196行)のexplanation_enフィールド定義文を、可能な限りそのまま
再利用する:

> a short, simple English explanation of the meaning — one sentence,
> plain words, easier than the phrase itself; not a dictionary
> definition. Example style: "raise privacy concerns" -> "to make
> people worry about how personal information is used or protected"

この一文を本Trial script内で`EXPLANATION_EN_SPEC_SENTENCE`定数として
逐語保持し、新Prompt本文に埋め込む(前回Prompt定数`er017_key_phrase_
level_spec_trial_01.ADVANCED_USER_TEMPLATE`自体は無変更・import読み取り
のみ、regressionテストで不変を確認)。

前回の機械チェック手法(`er017_key_phrase_level_spec_trial_01.py`
495-541行、`wordfreq.zipf_frequency`で解説語数・phraseとの難度比較)も
同じロジックをそのまま再利用する。前回実測(§7.2)では語数は最大12語/
目安15語以内に収まっており、本Trialも`MAX_WORDS=15`をそのまま流用する
(新規に決めた閾値ではなく前回実測ベース)。

Phrase選定・記事本文・日本語意味(`japanese_gloss`)は一切再生成しない
(Hormuz b1bの既存確定値をそのままA/B双方の入力として使う)。

## 3. 新規に追加する要素(前回になかった部分、Trial限定)

前回TrialはPhrase選定と同時に解説を生成したため、「既に確定した
Phraseに対して後から解説だけを付与する」独立callは前回に存在しない。
本Trialでは以下を**Trial限定の最小追加**として新設する(Production
Prompt・CURRENT_SPECへの影響なし):

1. 5 Phraseをまとめて1 callで解説させるuser message(前回は記事全体
   からの選定Promptに埋め込まれていたが、本Trialは選定を行わないため
   「既に選ばれたPhraseのリスト+各source_sentence+参考日本語意味」を
   入力として与える形に変更。explanation_enフィールド定義文自体は
   §2の逐語を保持)。
2. 新規Fact混入防止の明示指示(前回Promptには無かった追加制約。
   理由: 前回は記事全文を見て選定と同時に解説していたため記事外の
   事実混入リスクが低かったが、本Trialでは説明だけを独立生成する
   ため、source_sentenceにない固有名詞・数字を追加しないよう明記する
   必要がある)。
3. 日本語意味の直訳化を避ける指示(前回は日本語解説と英語解説が
   別レベル[Standard/Advanced]で完全に独立生成されていたため
   「日本語を英訳するな」という指示は不要だった。本Trialは同じ
   Phraseに対してA[日本語]が既に存在する状態でBを作るため、
   「日本語意味の直訳ではなく自然な英語で意味を説明する」を明示する
   必要がある)。

## 4. Prompt全文(本Trial新設分、逐語)

developer:
> You write short English explanations for Key Phrases that Japanese
> adult learners are studying in an English-learning news audio
> program. The phrases are already chosen; do not change them.

user(5 phrase分をまとめて1 call):
```
For each of the 5 Key Phrases below, write ONE short English
explanation of its meaning for an ADVANCED (CEFR B1) English learner.

Explanation instruction (reused from a prior approved Trial spec):
a short, simple English explanation of the meaning — one sentence,
plain words, easier than the phrase itself; not a dictionary
definition. Example style: "raise privacy concerns" -> "to make
people worry about how personal information is used or protected"

Additional rules for this task:
- The phrase itself must NOT be changed. Return it exactly as given.
- Do not add any name, number, or fact that is not already in the
  phrase or in the source sentence given below.
- Do not just translate the Japanese reference meaning word-for-word.
  Write a natural English explanation of the same meaning.
- The explanation should still make sense if the phrase is used in a
  different context, not only in this one news story.

Key Phrases:
1. phrase: "{phrase_1}"
   source_sentence: "{source_sentence_1}"
   japanese_reference_meaning (for accuracy check only, do not
   translate literally): "{japanese_gloss_1}"
... (5個分)

Return JSON only: {"explanations": [ {"phrase": ..., 
"english_explanation": ...} x5 ]}
```

schema(strict): `explanations`配列、`minItems=maxItems=5`。各item
`phrase`/`english_explanation`必須、`additionalProperties: false`。

候補は原則1案(品質が明らかに悪い場合のみ2案目、理由記録)。

## 5. 決定論チェック(前回ロジック再利用+新規Fact検出を追加)

1. Phrase同一性: 応答`phrase`が入力`display_phrase`と完全一致するか
   assert(不一致は`phrase_mismatch`として記録、表示は入力側を正とする)。
2. 語数上限: `MAX_WORDS=15`(§2の前回実測根拠)。
3. 語彙難度: `wordfreq.zipf_frequency`で解説内の語がphrase本体の
   最低zipfより難しい(zipfが低い)語を列挙(前回と同じロジック、
   `er017_key_phrase_level_spec_trial_01.py` 520-541行を移植)。
4. 新規Fact混入検出(新設): 解説文中の大文字語頭語(文頭を除く)と
   数字トークンを抽出し、`source_sentence`または`phrase`に
   (大小無視で)出現しない場合は`possible_new_fact`として記録。

## 6. LLM rubric(1 call、評価観点7項目)

各Phraseについて1〜5+根拠で評価:
`understandable_english_only` / `not_too_difficult` / `not_too_long` /
`explanation_simpler_than_phrase` / `reusability` /
`not_overfit_to_article` / `meaning_accuracy`。

## 7. 音声(任意)

`er038_tts_all_spoken_role_style_trial_01.py`から
`TRIAL_ROLE_STYLE_EN["KEY_PHRASE_EN"]`/
`TRIAL_ROLE_STYLE_EN["KEY_PHRASE_EXPLANATION_EN"]`
(既存定義のみ、値は無変更のimport再利用)と
`trial_master_audio_store`contextmanagerをimportで流用する。

- Phrase EN音声・JA意味音声(A用): Hormuz b1b
  `narration/kp{rank}_en.wav` / `kp{rank}_ja_charon.wav`を**新規生成
  せずコピーのみ**で流用(既存artifact、費用ゼロ)。
- B用の英語解説音声のみ新規に5 segment生成
  (`er003_v1_repro01_main_generate.generate_narration_snippet_verified_
  strict`を`KEY_PHRASE_EXPLANATION_EN`のstyleで直接呼ぶ、Trial専用
  Master Store隔離)。

## 8. 成果物

`user_test/kp_advanced_explanation_trial_02/index.html`:
5 Phrase × (A: EN句+JA意味 / B: 同一EN句+EN解説)のtext並列表+決定論
指標+rubric+(生成できれば)音声再生。GitHub Pagesで200確認。
