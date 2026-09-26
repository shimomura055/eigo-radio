# Recon: Connected Speech Equivalence Layer / Repetition QA 適用範囲棚卸し(read-only)

Management-ID: FAMILY-X-COMMENT4-AUDIO-REVIEW-01(3-B部分)
作成: Sonnet(read-only recon、API呼び出し0、artifact変更0)

## 1. 実装箇所(Grep調査)

- OPEN-121 Repetition QA本体: `er011_open121_repetition_qa_production_01.py`
  (`apply_repetition_qa_gate`)。
- OPEN-122 Connected Speech Equivalence Layer本体:
  `er011_connected_speech_equivalence_layer_production_01.py`
  (`classify_connected_speech_equivalence`、ARPAbetカテゴリA〜G+
  phoneme prefix drop / final phoneme substitution判定、
  `phonetic_environment_categories`)。
- 基礎の3パターンconnected-speech判定(歯擦音連続/破裂音連続/再分節、
  Trial-07 VALIDATED、OPEN-122とは別物・**全segment共通で常時有効**):
  `er006_preprod_hardening_01_validation.py`
  `_classify_asr_match_core`内 `connected_speech.classify_connected_speech`
  呼び出し(L890, L933)。
- Cascade層(OPEN-122の実発火ゲート):
  `er006_secondary_asr_01.py` `evaluate_attempt_with_cascade_detail`
  L442-538。発火条件: `not verified and cascade_enabled and
  enable_connected_speech_equivalence_layer and cls.classification ==
  "TRUE_CONTENT_MISMATCH" and cls.protected.passed`(L518-519)。
- 呼び出し元でのTrue/False配線(Family A本体、Production正式経路):
  `er003_v1_n3_01_tts_generate.py` L767-773(b1b)・L898-904(a2)。
- 呼び出し元でのTrue/False配線(Family X Trial経路):
  `er019_family_x_pointless_tts_01.py` L44
  (`_BODY_PART_NAMES = ("full_story_part1", "full_story_part2",
  "full_story_part3")`、Sonnet裁量でpart3へ拡大)・L99-100・L148-149。

## 2. 適用範囲表

| segment種別 | 経路 | 適用有無 | 根拠(関数/行) |
|---|---|---|---|
| Full Story part1/2(B1・A2、英語) | Family A | **適用**(equivalence layer + repetition QA 両方True) | `er003_v1_n3_01_tts_generate.py` L767-773(b1b)/L898-904(a2)。呼び出し先`generate_news_narration_wide_margin`/`generate_a2_segment_with_slowdown`→`c.generate_english_segment_with_fallback`(`er003_v1_crosslevel_audio_02_common.py` L71-74, 99-103, 142-143) |
| Full Story part3(3分割、Family Xのみ存在するsegment) | Family X | **適用**(Sonnet裁量でpart1/2と同列に拡張) | `er019_family_x_pointless_tts_01.py` L38-44コメント「同種のB1英語本文segmentのため一般化」、L99-100/148-149 |
| Point heading(point_one_heading/point_two_heading、Family A限定、Family Xには存在しない) | Family A | **非適用** | b1b: `point_headings.generate`経由(フラグ自体を渡さない引数構成、L743-744)。a2: `generate_a2_segment_with_slowdown`呼び出しでフラグ未指定=既定False(L873-875) |
| Point body(point_one/point_two、Family A限定) | Family A | **適用**(Full Story part1/2と同じタプルに含まれる) | L768/773(b1b)、L899/904(a2) |
| Preview | Family A(B1)・Family X | **非適用**(構造的に不可能) | B1: `voice01.generate_charon_english`呼び出し(L713, L727、`er019...` L76-88)。この関数自体に`enable_connected_speech_equivalence_layer`引数が**存在しない**(`er003_v1_sing01_voice01_generate.py` L45-51のシグネチャ参照)。A2(Family Aのみ)は日本語生成(`generate_a2_japanese_with_reading_safety`、L862-863)のため英語ASR比較自体が発生しない |
| Comment 1〜4 | Family A(B1)・Family X | **非適用**(同上、構造的に不可能) | 同上。B1: `er003_v1_n3_01_tts_generate.py` L716-734。Family X: `er019_family_x_pointless_tts_01.py` L80-88。A2(Family Aのみ)は日本語(L858-863) |
| Topic intro | Family A(B1)・Family X | **非適用** | B1: `voice01.generate_charon_english`(引数無し、上記と同じ関数)。Family X: `er019...` L74-78も同関数。A2(Family Aのみ): `c.generate_english_segment_with_fallback`呼び出しだがフラグ未指定=既定False(L847-849) |
| In One Line | Family A(B1/A2)・Family X | **非適用**(明示的除外) | b1b L759-773/a2 L890-904のタプルに`in_one_line`は含まれるが、判定式`name in ("full_story_part1","full_story_part2","point_one","point_two")`には含まれない(コメントL764-766「in_one_lineは本文ではないため対象外」)。Family Xも同様(`_BODY_PART_NAMES`に含まれない) |
| Key Phrase EN | Family A・Family X共通(`shared_narration.ensure_key_phrase_english_component`→`generate_key_phrase_component_verified`) | **非適用**(別機構[non-Latin cascade]のみ適用) | `er003_v1_repro01_main_generate.py` L647/657: `enable_non_latin_cascade=True`のみを渡し、`enable_connected_speech_equivalence_layer`/`enable_repetition_qa`は未指定=既定False |
| Japanese segments(topic_intro/preview/comment JA[A2]、Key Phrase JA meaning、B1日本語kp) | 両Family | **対象外(別バリデータ)** | `ja_secondary.evaluate_attempt_ja_with_cascade`系(`er007_ja_secondary_asr_01.py`)を使用し、OPEN-121/122とは別のJA専用cascade。英語equivalence layerの適用対象ではない |
| 基礎3パターン(歯擦音連続/破裂音連続/再分節、OPEN-122とは別物) | 全English segment共通 | **常時適用**(フラグ無関係) | `er006_preprod_hardening_01_validation.py` `_classify_asr_match_core`内`connected_speech.classify_connected_speech`呼び出し(L890, L933)。`classify_asr_match`は全英語segmentで共通利用されるため、Comment 1〜4もこの基礎3パターンの恩恵は受ける(OPEN-122のARPAbet A〜G拡張版だけが対象外) |

## 3. 「同じ英語TTS/ASRなのにsegment種別で検証が抜ける」状態(事実)

- 事実1: Comment 1〜4・Preview・Topic intro(Charon voice経路、
  `voice01.generate_charon_english`)は、`enable_connected_speech_equivalence_layer`/
  `enable_repetition_qa`という**引数自体が関数シグネチャに存在しない**
  (呼び出し側がTrueを渡そうとしても渡せない)。Full Story part1/2/
  Point body(Aoede voice経路)とは別の関数であるため生じている。
- 事実2: In One Line・Key Phrase ENは、対象を渡せる関数
  (`generate_english_segment_with_fallback`/
  `generate_narration_snippet_verified_strict`)を経由しているにも
  関わらず、呼び出し元が明示的にFalse(またはフラグ省略)で呼んでいる
  (ユーザー承認済み適用範囲を「本文4segment(+Family Xのpart3)」に
  限定しているため、意図的な除外であり実装漏れではない)。
- 事実3: Family XはFamily Aに存在しないFull Story part3を持つが、
  Sonnetの裁量判断でOPEN-121/122の適用対象へ含めている
  (`er019_family_x_pointless_tts_01.py` L38-44)。これはユーザー承認済み
  適用範囲(「A2/B1英語本文segment=full_story_part1/2・point_one・
  point_two」)の文言を「本文3分割の3つ目」として字義通り一般化した
  ものであり、SSOT本文に「part3」という語自体は登場しない
  (Family X自体がPoint構造廃止・3分割という後発のTrialのため)。

推測(事実と分離): 上記事実1・2は、いずれもOPEN-121/122のSSOT
(「呼び出し側がA2英語本文segment[full_story_part1/2・point_one・
point_two]でのみTrueを渡す」)に明示的に整合しており、意図的な適用範囲
限定である可能性が高い(Comment/Preview等は「本文」ではなく短い前置き・
合いの手segmentという性質上、対象外は設計判断と推測される)。ただし
その設計判断自体がComment 4のような「1語の単複差」ケースを
救済不能にしている、という副作用は今回初めて実データで確認された。

## 4. `point → points`(/s/追加型)の実コード確認

`docs/pm/recon_connected_speech_scope_01.md`作成時にAPI呼び出し無しで
ローカル実行(`python3 -c`、`er006_preprod_hardening_01_validation`と
`er011_connected_speech_equivalence_layer_production_01`を直接import)。

```python
import er006_preprod_hardening_01_validation as val
canonical = "The service looked like AI, but the work behind it was not always done by AI alone. Now, let's bring the main point together."
asr23 = "The service looked like AI, but the work behind it was not always done by AI alone. Now, let's bring the main points together."
cls = val.classify_asr_match(canonical, asr23)
# cls.classification == "ASR_VALIDATION_UNCERTAIN"
# cls.normalized_ratio == 0.96
# cls.protected.passed == True
# cls.protected.content_word_diffs == []   (単数/複数差は"benign plural pair"として吸収済み)
# cls.reason == "内容語の差は検出されないが、一致率がPASS基準に届かない"
```

```python
import er011_connected_speech_equivalence_layer_production_01 as cs_eq
cs_eq.classify_connected_speech_equivalence("the main point together", "the main points together")
# => {'layer_judgment': 'NOT_A_PHONEME_PREFIX_DROP', ...
#     'existing_result': {..., 'new_judgment': 'UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING', ...}}
```

結論(実コードで確認、3つの独立した理由すべてで救済されない):

1. **構造的に配線されていない**: comment_4は`voice01.generate_charon_english`
   経由であり、この関数には`enable_connected_speech_equivalence_layer`引数
   自体が存在しない(Full Story本文と別関数)。仮にProductionコードを
   変更してこの引数を追加・Trueで渡せるようにしたとしても、
2. **Cascadeの発火ゲート条件を満たさない**: OPEN-122の発火条件は
   `cls.classification == "TRUE_CONTENT_MISMATCH"`だが、実際の
   classificationは`ASR_VALIDATION_UNCERTAIN`(単数/複数差が
   `content_word_diffs`に計上されない設計のため、ratio 0.96が
   PASS閾値[0.98]未満というだけの「内容語差なし」ルートへ落ちる)。
   したがってCascade自体が呼ばれない。
3. **仮に直接equivalence layer関数を呼んでも判定はREJECT側**:
   `classify_connected_speech_equivalence`を直接呼んだ結果は
   `NOT_A_PHONEME_PREFIX_DROP`(canonical側の語がASR側の語の「prefix」
   ではなく、ASR側がcanonicalの後ろに`s`を追加した形であるため、
   この関数が想定する「phoneme drop」形状に一致しない)。

## 5. 提案(実装しない、提案のみ)

- 単数/複数のみの差(`point`→`points`等)を、既存の
  `_is_benign_plural_pair`吸収ロジックとは別に、ratio閾値の直前で
  「content_word_diffsが空かつ差分が単数/複数語尾のみ」の場合に限り
  救済する専用ルールを検討する余地はあるが、これは新しい仕様
  (Production挙動変更)でありUSER_DECISION_REQUIRED。
- Comment/Preview/Topic introにOPEN-121/122を拡大するかは、既存
  ユーザー承認済み適用範囲(「本文segmentのみ」)を変更する判断であり、
  同じくUSER_DECISION_REQUIRED。
- 上記いずれも本タスクでは実装しない(read-only recon のみ)。
