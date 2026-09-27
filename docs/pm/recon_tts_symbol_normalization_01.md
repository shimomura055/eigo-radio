# Recon: TTS記号正規化(全Family共通)設計調査(read-only、Phase 1)

管理ID: TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(Phase 1)
作成: Sonnet実行層(read-only recon、Production code/Prompt/SSOT変更なし、
API費用¥0)

前提: 本文書は「事実(コード引用・実データ引用)」と「推測/設計提案」を
区別する。事実にはファイルパス・行番号・関数名を付す。既存の関連recon
(`docs/pm/recon_connected_speech_scope_01.md`、
`docs/pm/recon_reading_validation_wiring_01.md`、
`docs/pm/recon_tts_local_rewrite_wiring_01.md`)と重複する詳細は、
新規知見のみ追記し全文は複製しない(該当箇所で参照する)。

---

## 0. ユーザー決定の要約(委任文からの転記、正本は委任文本体)

「使う必要のない曖昧記号は、そもそも原稿に生成させない。そのうえで
必要な記号だけを決定論的にTTS変換する。」実装思想は3層: (1) Writer/
Promptで予防、(2) Validatorで禁止記号検出、(3) 許可記号のみTTS
Normalizerで決定論的変換。対象はNews全Family(A/B/C/X/Z)・Fiction・
Preview・Comment・Heading・Key Phrase・In One Line・titleなど
Productionで音声化される全経路。本Phase 1はこの3層の設計・現状調査
のみで、Production変更は一切行っていない。

---

## 1. 音声化経路インベントリ

### 1.1 Family別の現行Status(前提整理)

| Family | Production Status | 根拠 |
|---|---|---|
| Family A(News、B1/A2標準) | `PRODUCTION_WIRED`(既存の主力経路) | `er003_v1_n3_01_tts_generate.py`が中核 |
| Family B(Editorial Voices) | `PRODUCTION_WIRED`(一部Trial継続中) | `er012_b_family_voices_production_01.py`。**日本語segmentが存在しない**(1.4節) |
| Family C(Future Story) | `PRODUCTION_WIRED` | `er013_family_c_production_01.py`/`_runner_01.py`。Dialogue Voice割当は既承認(CURRENT_SPEC.md「Family Z」節Z-4参照、Family C側運用実績として言及) |
| Family X(News、3分割構造) | 一部`PRODUCTION_WIRED`(Meta1件STOP中、詳細`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md`) | `er019_family_x_audio_production_runner_01.py` |
| Family Z(Fiction) | **未実装**(`USER_DECISION_REQUIRED`、Production配線なし) | CURRENT_SPEC.md「Family Z(Fiction)」節冒頭「Production配線自体は未実装」。Trial script(`er018_fiction_*.py`)のみ存在、本調査では**対象外**として扱う |
| legacy(er001〜er003初期、b1redesign/cefr_direct/iran01等) | 過去のTrial/旧世代Production | 本調査では**対象外**(1.5節のコーパス調査で言及するのみ) |

### 1.2 Family A/X共通: Japanese TTS入口(中核2関数)

`er003_v1_n3_01_tts_generate.py`の以下2関数が、Family A(B1/A2)・
Family X(audio_production_runner経由でも同モジュールをimport、
`grep`で確認: `er019_family_x_audio_production_runner_01.py` L47
`import er003_v1_n3_01_tts_generate as n3_tts`)・Family C
(`er012_b_family_voices_production_01.py` L67 `import
er003_v1_n3_01_tts_generate as tts_gen`、後述1.4節)で共有される
唯一の日本語TTS入口である:

- `generate_charon_japanese_with_reading_safety()`(L298-341、B1)
- `generate_a2_japanese_with_reading_safety()`(L491-、A2)

両関数とも同じ順序(`docs/pm/recon_reading_validation_wiring_01.md`
1.1節と同一): `tts_safe_ja()` → `safety.detect_gloss_placeholder_
notation()`(1件でもあれば`STOPPED`、TTS呼び出し自体をしない) →
`safety.classify_foreign_tokens_in_japanese_text()` →
`foreign_token_gate_requires_stop()`(HUMAN_REVIEW分類のみブロック) →
`safety.to_tts_safe_japanese_fraction_reading()` → 実TTS呼び出し。

これが`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md`が報告した
「Key Phrase以外の日本語TTS経路にも適用済み」の実体であり、A2
`japanese_title`(ja_writer正式path由来)がこのゲートで`STOPPED`に
なったのは、`japanese_title`も内部的にこの2関数のどちらか(A2なので
`generate_a2_japanese_with_reading_safety`)を経由してTTSへ渡される
ためである(`generate_a2_segments()`内、L834以降で呼び出し。本調査では
呼び出し箇所の逐一確認まではしていない[Phase 2でgrep確認推奨]が、
Stage 3aのSTOP実測結果自体がこの経路であることを裏付けている)。

### 1.3 B1/A2 segment別の生成関数マップ(Family A実測)

`generate_b1_segments()`(L697-828)・`generate_a2_segments()`(L834-)を
読解した結果:

| segment | Writer/生成元 | TTS入口(英語) | TTS入口(日本語) |
|---|---|---|---|
| topic_intro | `f"Today's topic is {parts['title']}."`(L715、機械組み立て、LLM生成ではない) | `voice01.generate_charon_english`(L721) | (A2は日本語有無未確認、Phase 2) |
| preview / comment_1-4 | `support[name]`(`b1_support_texts.json`、`sc`モジュールの`run_support_text`、`PREVIEW_ROLE`/`COMMENT`系Prompt) | `voice01.generate_charon_english`(L736、`style_prefix_override`あり) | A2は`generate_a2_japanese_with_reading_safety`経由(`docs/pm/recon_connected_speech_scope_01.md`該当行) |
| point_one_heading / point_two_heading | `parts[name]`(article.md ###見出し、`sc.clean_heading`で番号ラベル除去済み) | `point_headings.generate`(L756、Connected Speech非適用) | (Family Aのみ存在、Family Xには無し) |
| full_story_part1/2(・Family Xのみpart3) | article.md本文セクション | `news_tail_fix.generate_news_narration_wide_margin`(L772) | 該当なし(本文は英語のみ) |
| point_one / point_two | article.md ###本文 | 同上(L772、`enable_repetition_qa=True`) | 該当なし |
| in_one_line | article.md `## In one line`セクション | 同上(L772、`disfluency_qa=True`) | 該当なし |
| Key Phrase EN(kp*_en) | 選定Prompt(`b1_p2_keywords_l_prompt_template.txt`)→canonicalization | `shared_narration.ensure_key_phrase_english_component`(L804、Master Audio Store経由) | — |
| Key Phrase JA(kp*_ja) | 同上のjapanese_gloss/japanese_gloss_tts | — | `generate_charon_japanese_with_reading_safety`(L813、`resolve_key_phrase_ja_gloss_tts`経由でTTS用フィールドを解決) |

Title(表示用・音声用)・japanese_title・A2 commentのJA版は
`er003_v1_n3_01_articles_generate.py`(gen)・`er019_family_x_ja_writer_
o_r1_r2_01.py`(Family X専用ja_writer)等、別モジュールで生成される
(1.5節・1.6節)。

### 1.4 Family B(Editorial Voices)の実態: 日本語segmentが存在しない

`er012_b_family_voices_production_01.py`は`er003_v1_n3_01_tts_
generate`を`tts_gen`としてimportしている(L67)が、`generate_charon_
japanese_with_reading_safety`・`generate_a2_japanese_with_reading_
safety`・`voice01.generate_charon_japanese`・`tts_safe_ja`・
`detect_gloss_placeholder_notation`・`classify_foreign_tokens_in_
japanese_text`のいずれも本ファイル内で**呼び出されていない**
(grep 0件)。日本語segment名(`japanese`/`_ja`/`title_ja`等)も
本ファイル内に**存在しない**(grep 0件)。すなわちFamily B
(Editorial Voices)は現状**英語のみのFamily**であり、本タスクが
対象とする日本語固有の記号ルール(「なになに」変換、日本語ポーズ等)は
**Family Bには適用対象が存在しない**(英語側ルール[括弧・%$¥・URL・
絵文字・Markdown]は引き続き対象)。

### 1.5 Family C(Future Story)の実態

`er013_family_c_production_runner_01.py`は`er012_b_family_voices_
production_01`(`bvoices`、L69)経由で`voice01`/`repro01`を利用する
構成であり、上記1.4節の「日本語segmentなし」という性質を
**Family Cも引き継いでいる可能性が高い**(bvoices自体に日本語呼び出しが
存在しないため)。ただし本調査では`er013_family_c_production_01.py`
(`fam_c`)本体・Dialogue Voice割当箇所(`classify_quote_voice_window`)
までは読解していない(Phase 2で確認推奨)。CURRENT_SPEC.md「Family Z」
節はFamily Cを「Future Story専用設計」「In One Line相当のsegmentが
Family Cに存在しない」と明記しており、segment構成自体がFamily A/Xとは
異なる。

### 1.6 Family X固有: ja_writer(japanese_title生成経路)

`er019_family_x_ja_writer_o_r1_r2_01.py`は、`NEWS-FAMILY-X-JA-FACT-
CHECK-PRODUCTION-WIRING-01`が持つ日本語title生成の正式pathである
(`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md`記載の
`ja_writer/runtime_evidence.json["title"]`)。本ファイルをgrep調査した
結果、**絵文字・括弧・Markdown装飾・placeholder記号に関する禁止文言・
正規化関数は一切存在しない**(`絵文字`/`emoji`/`括弧`/`Markdown`/
`normalize_article_formatting`いずれも0件)。これは1.7節で述べる
Family Aの`normalize_article_formatting()`(emoji/bold除去)が
**Family X(ja_writer)には適用されていない**ことを意味し、Stage 3aで
実際に観測された「A2 japanese_titleに三点リーダーが残っていた」
STOPの構造的原因の一つと推測される(Prompt側の予防層がFamily A/Xで
不均一)。

### 1.7 Family A: 記事本文レベルの既存Normalizer(emoji/Markdown bold)

`er003_v1_n3_01_articles_generate.py`に、本タスクの関心と重なる
**既存の第1層(Prompt予防)+第3層(決定論的Normalizer)の実例**がある:

- Prompt側(L168-172、`Formatting requirements`ブロック):
  「絵文字(emoji)。タイトル先頭の💳などを含む、全ての絵文字を禁止
  します」「装飾目的の不要なMarkdown bold(`**...**`)。必要な正式
  Markdown構造(##・###・####の見出し)は維持してください」。
- Normalizer側(L633-657、`normalize_article_formatting()`):
  Unicode category `So`(Symbol, Other)の文字を機械的に除去(emoji)、
  `re.sub(r'\*\*(.+?)\*\*', r'\1', ...)`でMarkdown boldを除去。
  呼び出し箇所: L857(通常生成後)・L1189(Local Rewrite後、article_text
  再正規化)。

この既存実装は、ユーザーが今回要求する「Prompt予防+決定論的
Normalizer」という2層構成の**既存前例**であり、括弧・波ダッシュ・
三点リーダー等への拡張は、この関数の隣に新規サブ関数を追加する形で
自然に一般化できる(4節で設計)。ただし、この呼び出し箇所
(`er003_v1_n3_01_articles_generate.py`)がFamily X(ja_writer)・
Family C(future_writer)から再利用されているかは確認できなかった
(1.6節のとおりFamily Xでは未確認=**Gap**)。

### 1.8 Trial専用・対象外経路(明記)

- `er008_*`系(N8 Trial群)・`er014_output/four_type_observation_01/*`・
  `er011_*_trial_*`単発Trial scriptは、いずれもTrial専用または既に
  supersededな経路であり、本調査の「現行Production経路」の対象外。
- Family Z(Fiction)は1.1節のとおりProduction配線自体が未実装のため
  対象外(将来Phase 2以降で本設計をFamily Z配線時に適用する参照先には
  なりうる)。
- `docs/pm/recon_connected_speech_scope_01.md`のsegment別表(2節)・
  `docs/pm/recon_tts_local_rewrite_wiring_01.md`のrole別表(2節)は、
  英語segmentのretry/fallback経路(Connected Speech Equivalence
  Layer・cool-down・Local Rewrite)の適用範囲を確定済みであり、本文書は
  重複して再掲しない(5節で参照するのみ)。

---

## 2. 既存ルール一覧(記号別)

| 記号 | 既存Prompt禁止 | 既存Validator/Gate | 既存Normalizer | 所在(逐語引用+行番号) |
|---|---|---|---|---|
| 〜/～(placeholder用途) | Key Phrase gloss限定で「許容」に緩和済み(規約B撤回) | `detect_gloss_placeholder_notation()`(全位置、Key Phrase以外のJA text全般にも実質適用、1.2節) | 文頭・読点直後のみ「なになに」変換(`convert_display_gloss_to_tts_text`) | Prompt: `b1_p2_keywords_l_prompt_template.txt` L23「日本語グロスは…「～」「〜」を使ってもかまいません」。Gate: `er003_audio_tts_asr_safety.py` L122-133。Normalizer: `er003_key_words_canonicalization.py` L174-187 |
| …(三点リーダー) | Key Phrase gloss限定で明示禁止(規約B、無変更) | 同上Gate(`detect_gloss_placeholder_notation`の対象文字に含む、L122) | **無し**(変換対象外のまま無変換、KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01_REPORT.md 6節「…は一切変換しない」) | Prompt: 同上ファイル L23「ただし「…」のようなプレースホルダー記号は使わないでください」 |
| /(スラッシュ) | **無し**(grep 0件) | **無し** | **無し** | (該当なし、Gap) |
| 括弧 ()（） | Key Phrase gloss限定で明示禁止(`KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01`) | `_JA_GLOSS_PARENTHETICAL_RE`(Key Phrase gloss限定、`er003_key_words_min_unit.py` L306, 443) | **無し** | Prompt: `b1_p2_keywords_l_prompt_template.txt`(括弧禁止パラグラフ、`KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01_REPORT.md`2.1節に全文引用あり)。本文(comment/full_story等)・英語側には**無し**(Gap) |
| ：；(コロン・セミコロン) | **無し** | **無し** | **無し** | (該当なし、Gap。ただし1.9節のコーパス調査で本文中に高頻度出現) |
| 省略形(e.g./i.e./etc.) | **無し** | **無し** | **無し**(`DEFAULT_JA_READING_DICTIONARY`に該当エントリなし、`er003_audio_tts_asr_safety.py` L681-700) | (該当なし、Gap) |
| 数値記号 % $ ¥ | Key Phrase選定Promptのみ「数値の穴埋めが必要な不完全表現を選ばない」(仕様B、placeholder型回避。記号自体の禁止ではない) | 記号自体へのValidatorは**無し** | **無し**(`tts_safe_en`/`tts_safe_number_words_en`はいずれも%$¥を扱わない、L573-612) | Prompt: `b1_p2_keywords_l_prompt_template.txt`(仕様B該当文、`KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01_REPORT.md`2節) |
| URL/email | **無し** | **無し** | **無し** | (該当なし、Gap。1.9節コーパス調査でも記事本文中の実例は未検出) |
| 絵文字 | Family A本文レベルで明示禁止(1.7節) | 検出専用Validatorは無いがNormalizerが機械除去(実質的にGate相当) | `normalize_article_formatting()`(Unicode category `So`除去) | `er003_v1_n3_01_articles_generate.py` L168-172, L633-657 |
| Markdown装飾(bold等) | Family A本文レベルで明示禁止(1.7節、見出し構造`##`等は維持) | 無し | `normalize_article_formatting()`(`**...**`除去) | 同上 L171, L655 |
| 内部制作ラベル(Part 1等) | 個別記事で発見都度対応(prompt側修正) | `classify_foreign_tokens_in_japanese_text`(JA)/`detect_internal_production_labels_in_english_text`(EN) | 無し(検出のみ、HUMAN_REVIEW) | `er003_audio_tts_asr_safety.py` L708-834 |

### 1.9 参考: 既存corpus(article.md)での記号出現実測(Phase 1範囲、コスト¥0)

`er0XX_output/**/article.md`をローカルgrep(API呼び出しなし)で機械的に
数えた結果(全439件、うち`er011_output`以降=「直近世代」350件):

| 記号 | 全439件中の出現数/出現ファイル数 | 直近350件での非見出し(本文)出現 |
|---|---|---|
| …(U+2026) | 262回/262ファイル | **0件**(全て`## In one line…`という古い世代[legacy]の見出し名装飾で、見出し自体はTTS対象外。直近世代article.mdの本文には出現なし) |
| 〜(U+301C) | 3回/1ファイル | 未確認(件数僅少) |
| ：（全角）/：（半角colon） | 1,072回/380ファイル | 未分類(Markdown見出し記法`###`直後のラベル等との混在が疑われる、Phase 2でheading/body分離要) |
| ;（セミコロン） | 152回/110ファイル | 同上未分類 |
| %（半角） | 340回/95ファイル | 同上未分類(本文中の数値表現の可能性が高い) |
| $（ドル） | 56回/23ファイル | 同上未分類 |
| ( ) （半角括弧） | 35回/7ファイル | 同上未分類 |
| /（スラッシュ） | 233回/13ファイル | 同上未分類 |
| ¥・全角(・全角% | 0件 | — |

**重要な限定**: 上記はarticle.md(記事本文Markdown)のみの機械的文字数
カウントであり、(a) Markdown見出し記法・comment/preview/key phrase等の
別ファイル(`b1_support_texts.json`等)は含まない、(b) 実際にTTSへ渡る
箇所かどうか(見出しかどうか)は個別確認していない。実際にStage 3a/3bで
STOPが実測されたのは記事本文ではなく`japanese_title`(ja_writer別経路)
と`key_phrases`のjapanese_gloss(scaffold LLM生成物)であり、これらは
上記article.mdカウントには含まれない。Phase 2では、実際にTTS入口へ渡る
時点のテキスト(`parts.json`/`b1_support_texts.json`/
`keywords_canonicalized.json`/ja_writer出力)を対象にした頻度調査を
推奨する。

---

## 3. ギャップ表(ユーザー採用ルール × 経路)

凡例: 満=既存で満たす / 一部=部分的に満たす / 未=未対応 / 競合=既存仕様との
競合あり

| ルール | Family A(B1/A2) | Family X | Family B | Family C | Key Phrase |
|---|---|---|---|---|---|
| 〜/～→なになに(全位置) | **一部**(Gate自体は全位置で発火・ブロックするが「なになに」への変換は文頭/読点直後のみ、mid-stringはSTOPPEDのまま=変換されず止まるだけ) | 一部(同左、Stage 3aで実証済みのSTOP) | 該当なし(日本語segmentなし、1.4節) | 未確認(Phase 2) | **満**(Key Phrase gloss限定で文頭/読点直後のみ配線済み) |
| …→ポーズ(非発話) | **未**(Gateが検出してSTOPするのみ、ポーズへの変換機構なし) | 未(同左、Stage 3a実例) | 該当なし | 未確認 | 未(Key Phrase geneでも変換せず無条件STOP、既存設計どおり) |
| /禁止 | 未(Writer Prompt未対応) | 未 | 未確認 | 未確認 | 未(Key Phrase専用Promptにも/禁止文言なし) |
| 括弧禁止 | **未**(本文Writer Promptに無し、1.7節のFormatting requirementsにも括弧は含まれない) | 未 | 未確認 | 未確認 | **満**(Key Phrase gloss限定でPrompt+Validator配線済み、2026-09-06) |
| ：；→ポーズ | 未 | 未 | 該当なし(英語のみ、コロン自体の禁止/変換もFamily B英語本文には未確認) | 未確認 | 未 |
| 省略形(e.g.等) | 未(Trial evidence待ち、辞書登録の必要性自体が未確認) | 未 | 未 | 未 | 未 |
| %$¥→自然語 | **一部**(Key Phrase選定Promptに「placeholder型を選ばない」の1文のみ、記号自体の自然語化はなし) | 未確認 | 未確認 | 未確認 | 一部(同左) |
| URL/email禁止 | 未(Prompt未対応、ただし1.9節のとおり実例自体が現行corpusで未検出=低リスク) | 未 | 未確認 | 未確認 | 該当性低(Key Phraseの性質上URL/emailは出現しにくい) |
| 絵文字・Markdown除去 | **満**(1.7節、Prompt+Normalizer) | **競合/Gap**(1.6節、ja_writerに未適用。article.md本体側[emailで生成される英語article.md]がFamily Xでどう生成されるかは本調査未確認、Phase 2要) | 未確認 | 未確認 | 該当性低 |

**総括**: 現在`PRODUCTION_WIRED`まで到達しているのはいずれも**Key
Phrase gloss限定**(〜/～の文頭/読点直後変換、括弧禁止、placeholder型
選定回避)であり、ユーザーが今回要求する「全Family横断・本文含む
全経路への一般化」は、括弧・〜/～(mid-string)・…・：；・%$¥・URL・
省略形のいずれについても**本文Writer/本文TTS入口には未到達**。
絵文字・Markdown除去のみFamily Aで本文レベルの実装例があるが、
Family X(ja_writer)には未適用であることを1.6節で確認した。

---

## 4. 設計案(3層)

### 4(a) Prompt追加文言案

**方針**: 既存の「Key Phrase gloss限定ルール」(規約A/B、括弧禁止、
placeholder型回避)と、本文Writer向けの新規ブロックは**別々のPrompt
ファイルに存在する別々の指示**であり、統合・書き換えではなく
**横展開(コピー)**とする(重複ではなく、対象読者[LLM]が異なる別ファイル
への同種指示の追加という位置づけ)。

新規「音声禁止記号ブロック」案(本文Writer向け、Family A
`er003_v1_n3_01_articles_generate.py`の`Formatting requirements`
[L168-172]と同一箇所へのパラグラフ追加、既存のemoji/bold文言の直後):

> - 波ダッシュ「〜」「～」は、具体的な内容を省略した空欄・言い換えの
>   代わりとして使わないでください(例:「〜の場合」のような未確定な
>   言い回し)。書くべき内容を実際に書いてください。
> - 三点リーダー「…」「……」は使わないでください。間を置きたい場合は
>   通常の句点・読点で表現してください。
> - スラッシュ「/」は使わないでください。「and」「or」(日本語は
>   「と」「または」)で書いてください。
> - 括弧「()」「（）」「[]」は使わないでください。補足情報は通常の
>   文として本文に統合してください。
> - コロン「:」・セミコロン「;」は使わないでください。文を区切りたい
>   場合は句点・読点、または別の文にしてください。
> - パーセント・ドル・円などの数値は、記号(%、$、¥)ではなく、
>   「50パーセント」「50 percent」「千円」のように自然な言葉で
>   書いてください。
> - URLやメールアドレスは書かないでください。
> - 絵文字・顔文字・装飾的な特殊記号は使わないでください。

このブロックを、Family A本文Writer(`er003_v1_n3_01_articles_generate.
py`)・Family X ja_writer(`er019_family_x_ja_writer_o_r1_r2_01.py`)・
Family B/C(該当する本文生成Prompt、Phase 2で特定)・Key Phrase gloss
Prompt(既存の規約A/Bと**重複しないよう**差分のみ、〜/～は既存が「許容」
のため本ブロックの波ダッシュ文言は**Key Phrase Promptには追加しない**、
括弧は既存済みのため追加しない、…/;/:のみ追加余地)へ展開する。

**重複回避の原則**: 各Prompt側で、追加前に既存文言をgrepし
(`KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01`の実施パターンを
踏襲)、既に同義の文言がある場合は追加しない。

### 4(b) Validator設計

**配置先**: `er003_audio_tts_asr_safety.py`内に新規セクション
(例: 「G. 音声化禁止記号の検出(TTS Symbol Prohibition Gate)」)を
既存のセクションA〜Fと同じ形式で追加する(このファイルはすでに
「TTS呼び出し前のゲート集」という役割を持つ唯一のモジュールであり、
新規モジュールを作る必要はない)。

**既存`detect_gloss_placeholder_notation`との関係**: 既存関数は
Key Phrase gloss文脈の〜/～/…検出に特化しており(関数名・コメントとも
gloss前提)、汎用化のために書き換えると既存呼び出し元(`generate_
charon_japanese_with_reading_safety`等)への影響範囲が広がる。**既存
関数は維持し、新規に汎用版
`detect_prohibited_symbols(text: str, language: str) -> dict`を追加**
する設計を推奨する(找つけた記号ごとに検出理由を返す、既存の
`classify_foreign_tokens_in_japanese_text`と同じ「findings配列+
requires_stop判定関数」のパターンを踏襲: `symbol_gate_requires_stop
(findings) -> bool`)。既存`detect_gloss_placeholder_notation`は
Key Phrase gloss専用のまま残し、新関数は本文Writer出力(comment/
full_story/preview/title/heading等)向けとして別途配線する(呼び出し
側で両方チェックする箇所[Key Phrase]と、新関数のみチェックする箇所
[本文]が生じるのは許容、既存のOPEN-121/122のrole別配線パターンと
整合)。

**must-fix retry機構との接続**: 既存の「TTS呼び出し前ゲートで
STOPPED」というパターン(`detect_gloss_placeholder_notation`・
`foreign_token_gate_requires_stop`と同型)をそのまま踏襲すれば、
新規Validatorも既存のHuman Review Lock・retry予算管理(3層: 標準→
fallback→Human Review Lock)にそのまま接続できる(新しいRetry上限・
新しいLockを作らない)。**ただしWriter生成時点でブロックするか、TTS
呼び出し直前でブロックするかは設計判断が必要**: 現行のKey Phrase
gloss placeholder Gateは「TTS呼び出し直前」でブロックしており、
Writer/Scaffold再生成にはフィードバックされない(Stage 3aのSTOPが
「gloss自体の再生成」を促す形にはなっていない、既存retry機構内で
自動修復されない)。ユーザー方針(「そもそも原稿に生成させない」)に
最も忠実にするには、**Writer出力の直後(TTS入口より前、記事生成
パイプラインの中)**にもValidatorを設置し、違反時はWriterへの
再生成promptへフィードバックする経路(既存のmust-fix retry/QA機構、
例えば`er003_v1_n3_01_articles_generate.py`のLocal Rewrite系や
Key Phrase Set Redundancy QAと同型の「NG理由をpromptへ追記して
再生成」パターン)への接続が必要になる。これは**Phase 2の実装対象**
であり、既存のどの再生成ループへ接続するかはWriter/Scaffold側の
既存構造をさらに読解する必要がある(本Phase 1では未確定、Phase 2の
最初の調査項目とする)。

### 4(c) Normalizer設計

**日本語**: `convert_display_gloss_to_tts_text()`
(`er003_key_words_canonicalization.py`)と`tts_safe_ja()`
(`er003_v1_n3_01_tts_generate.py`)は**役割が異なる**(前者は表示用→
TTS用の一発変換[Key Phrase専用フィールド生成]、後者はTTS直前の
使い捨てコピー生成)。ユーザー要求([1] 〜/～を全位置で「なになに」、
[2] …を句読点等へ、[3] ：；を句読点等へ)を実現するには:

1. `tts_safe_ja()`(L661-667)を拡張し、現行の「先頭のみ除去」を
   「全位置の〜/～→なになに置換」へ一般化する(既存の
   `_LEADING_TILDE_RE`[Key Phrase専用]とは別に、`er003_audio_tts_
   asr_safety.py`側に汎用版`normalize_tilde_placeholder_ja(text)`を
   新設し、`tts_safe_ja()`から呼ぶ案。Key Phrase側の`convert_display_
   gloss_to_tts_text()`は「表示用は変えず、文頭/読点直後だけ変換する」
   という**独自の保守的スコープ**を意図的に持つため[コメントL166-173
   「それ以外の位置…は一切変換しない」]、これは変更せず維持する
   [Key Phraseのglossは辞書的な定義文であり、mid-stringの「〜」が
   「AをBと結びつける」型の項変数記法である可能性が本文より高いため
   -- 全位置変換だと非文になるリスクがKey Phraseの方が高い、
   ER-006-KP5-CANONICAL-BUG-01のコメントL107-113参照]。すなわち
   **Key Phrase gloss=既存の保守的ルールを維持、本文/title等の
   一般テキスト=新規汎用ルールを適用**という**意図的な非対称設計**を
   提案する)。
2. 「…」「……」→句点(「。」)または読点(「、」)への決定論的変換を
   `tts_safe_ja()`(日本語)・新規`tts_safe_ellipsis_en()`(英語、
   `tts_safe_en()`へ統合)に追加する。Gemini TTS公式の`<short pause>`
   /`<long pause>`インラインタグ(5節で詳述)が現行Production採用
   モデルで有効かは未検証のため、**Phase 1時点の推奨は「句読点への
   決定論的置換」**(ユーザー指示の代替案どおり)。
3. 「：」「；」→読点または句点への変換も同様に`tts_safe_ja`/
   `tts_safe_en`へ追加。

**英語**: `tts_safe_en()`(L573-576)は現状カーリークォート除去のみ。
括弧・スラッシュ・％$¥は「TTSでの読み上げ自体は禁止ではない」
(英語TTSモデルは"%"を"percent"と読める可能性が高い)ため、ユーザー方針
「可能な限り原稿生成時点で自然語表現」を優先し、**Normalizer側での
決定論的変換ではなく(1) Prompt予防を主、(2) Validatorでの検出を
従とする**設計を推奨する(数値のnatural-language化はWriter側の
文脈判断が必要で、Normalizerでの機械変換[$83→"eighty-three dollars"
等]は既存の`tts_safe_number_words_en`と役割が重なるが、桁数・通貨
種別の一般化は非決定論的判断を要するため、user方針「意味の自動判断が
必要なケースはUSER_DECISION_REQUIRED」に該当する可能性が高い、7節参照)。

**日英共通の統合方針**: 新規関数はいずれも`er003_audio_tts_asr_safety.
py`(TTS入力正規化セクションA)へ追加し、`tts_safe_ja`/`tts_safe_en`
からこれらを呼ぶ形にする(既存の`to_tts_safe_japanese_fraction_
reading`と同じ「TTS直前の使い捨てコピー生成」という設計原則を維持、
canonical text自体は変更しない)。

---

## 5. TTS側pause機構の公式確認(HTTP GET実施)

**取得日時**: 2026-09-27(本タスク実施時)。
**URL**: `https://ai.google.dev/gemini-api/docs/speech-generation`
(`curl`でHTTP 200取得、HTMLからテキスト抽出)。

**逐語引用(英語、抜粋)**:

> "Pacing and pauses: You can control rhythm and silence at three
> levels of granularity: Punctuation and ellipses: Use commas,
> dashes (--), and ellipses (...) for natural conversational
> hesitation. Inline pause tags: Insert `<short pause>` or
> `<long pause>` at exact points in the script where a speaker
> should pause: 'Hold on, let me think... `<short pause>` Alright,
> I've got it.'"

**モデル適用範囲の重要な限定**: 同ページは`gemini-3.8-flash-lite-tts`
向けの最新ドキュメントであり、以下のMigration guide文言がある:

> "Use Gemini 3.8 Flash-Lite TTS (`gemini-3.8-flash-lite-tts`) as
> your fast, cost-efficient workhorse replacement for
> `gemini-3.1-flash-tts-preview`. ... Migration guide: If you are
> migrating from `gemini-3.1-flash-tts-preview` or earlier Gemini
> TTS models to Gemini 3.8 TTS: Move turn-level directions into
> `speech_metadata`..."

すなわち`<short pause>`/`<long pause>`インラインタグと
`speech_metadata`によるstyle制御は、**Gemini 3.8 TTS世代の新機能**
として案内されており、現行Production採用モデル(英語=
`gemini-2.5-pro-preview-tts`、日本語=`gemini-3.1-flash-tts-preview`、
`TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01_REPORT.md`冒頭で確認済み)が
これらのタグ・フィールドをサポートするかは、**本ページの記載だけでは
確認できない**(ページ自体が3.1以前を「migrate元」として扱っており、
3.1側のドキュメントページは別に存在する可能性があるが、本タスクでは
未取得)。

さらに、`gemini-3.8-flash-lite-tts`自体は既に
`TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01`でユーザー承認済みProduction
Prompt形式(Structured Separation)を正しく解釈できず、instruction
leakage・hallucinationを起こして**Sonnet仮分類REJECTED**となっている
(同Report §0)。したがって「3.8へモデルごと切り替えてpauseタグを使う」
という選択肢は**現時点でProduction不採用方向**であり、pauseタグの
利用可否を確認するには、**現行モデル(2.5-pro-preview-tts /
3.1-flash-tts-preview)側で`<short pause>`等のタグが解釈されるかを
別途小規模Trialで確認する必要がある**(未実施、Phase 2候補)。

**結論**: 公式な正式pause/breakタグは存在する(3.8世代で確認)。
現行Production採用モデルでの有効性は**未確認**。Phase 1時点での
安全側の代替案は、ユーザー指示どおり「句読点への決定論的置換」
(4(c)節)とする。

---

## 6. retry/fallback/regeneration経路での有効性

- **Key Phrase経路**: 既存の`convert_display_gloss_to_tts_text`は
  `merge_canonicalization_result()`内で1回だけ計算され、Key Phrase Set
  Redundancy QA retry(最大2回)は選定Prompt自体を再実行するため、
  retryのたびに新しい`japanese_gloss`から再度この変換が実行される
  (`KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01_REPORT.md`10節で
  確認済み)。新規汎用Normalizerも同じ場所(TTS呼び出し直前)に置けば、
  Key Phrase retry・A2/B1標準retry・fallback(minimal instruction)・
  Local Rewrite回復のいずれの経路でも「TTS呼び出し直前に必ず通る」
  という既存契約(`generate_charon_japanese_with_reading_safety`/
  `generate_a2_japanese_with_reading_safety`の冒頭で毎回`tts_safe_ja`
  を呼ぶ設計)を再利用でき、**新しい経由漏れは生じない**(Local
  Rewriteが生成した新テキストも、再度この関数を通ってTTSへ渡るため)。
- **英語側**: `tts_safe_en`/`tts_safe_news_en`も同様に、B1
  Full Story/Point/Comment/Previewの各生成関数の冒頭で毎回呼ばれる
  (`generate_news_narration_wide_margin`/`generate_charon_english`の
  呼び出し元、`er003_v1_n3_01_tts_generate.py` L722/736/773で確認)。
  ここへ新規Normalizerを追加すれば同様に全retry/fallback経路を通る。
- **Assembly側Audio Validation Gate**: 無変更のまま(`NEWS-FAMILY-X-
  AUDIO-PRODUCTION-WIRING-01_REPORT.md`が実証したとおり、Gate自体は
  今回のPhase 1で一切変更していない。Phase 2でValidator/Normalizerを
  追加しても、Gate自体のブロック条件[STOPPED segmentがあればepisode
  assembly中止]は変更しない設計とする)。
- **Family X固有の懸念**: `docs/pm/recon_tts_local_rewrite_wiring_01.
  md`4節が指摘するとおり、A2側のcool-down/Local Rewrite回復は一部
  未配線(Gap、Full Story/Point/In One LineのA2側)。本タスクの
  Normalizer/Validatorはこの既存Gapを解消するものではなく、既存Gapの
  上に追加されるだけである点を明記する(新たな安全機構の後退では
  ないが、既存Gapの解消需要とは別軸)。

---

## 7. USER_DECISION_REQUIRED候補(意味判断が必要なケース)

1. **範囲表記「中〜高」の〜**: 全位置変換を採用した場合、「中〜高
   強度」のような範囲表記の「〜」まで「なになに」に変換されると
   意味が壊れる(Key Phrase glossの既存設計がこのケースを意図的に
   「変換対象外のまま無変換」としている理由そのもの、2節参照)。
   本文Writer側では「範囲表記の〜は使わず『中程度から高程度』のように
   書く」というPrompt予防で対応する案が考えられるが、**既存記事
   corpusに実例が見つかっていない**(1.9節)ため、実例が出た場合に
   個別判断が必要。
2. **数値placeholder「〜%」**: Key Phrase gloss側は既に選定Prompt
   レベルで回避誘導済み(2節)。本文Writer側で同種の表現(「売上を
   〜%押し上げる」等)が生じた場合の扱いは未定義。
3. **固有名称の記号**(例: 企業名・製品名に含まれる記号、"AT&T"の
   "&"等): 一般化せず個別報告する方針(委任文の指示どおり)。本調査
   では実例は見つかっていない。
4. **既存仕様との競合**: Key Phrase gloss側の「〜/～は許容」という
   既存ルール(規約B撤回、2026-09-06)と、本文側の新規「〜/～は
   placeholder用途のみ許容」という今回のルールが、**Key Phrase以外の
   短い日本語text(title/comment等)にどこまで同じ緩和を適用するか**は
   未定義(Key Phrase gloss=辞書的定義文という特殊な文脈があるため
   「～を示す」のような表現が正当だが、title/commentは通常文であり
   同じ緩和が必要かは疑問。ユーザー判断が必要)。
5. **:;の日本語での実際の使用実態**: 1.9節のコーパス調査で1,072件
   (コロン)・152件(セミコロン)が検出されたが、Markdown見出し記法
   由来かどうか未分類。もし大半がMarkdown由来(TTS対象外)であれば
   このルールの優先度は低く、逆に本文中に多数残っているなら優先度は
   高い。Phase 2で実データ分類が必要。
6. **英語側の%$¥の自然語化**: Writer側で完全に記号を使わせない
   予防策が最優先だが、既存記事の一部(1.9節、%=95ファイル、
   $=23ファイル)には既に記号が残っている可能性があり、遡及的な
   書き換えを行うかは既存artifactの扱い方針(過去artifact不再生成の
   既存原則)との整合を含めユーザー判断が必要。

---

## 8. Phase 2実装計画

### 8.1 変更ファイル一覧(見積り)

| ファイル | 変更内容 | 見積り行数 |
|---|---|---|
| `er003_audio_tts_asr_safety.py` | 新規セクションG(`detect_prohibited_symbols`/`symbol_gate_requires_stop`/`normalize_tilde_placeholder_ja`/`normalize_ellipsis_pause`/`normalize_colon_semicolon_pause`等) | +80〜150 |
| `er003_v1_n3_01_tts_generate.py` | `tts_safe_ja`/`tts_safe_en`から新規Normalizer呼び出しを追加 | +10〜20 |
| `er003_v1_n3_01_articles_generate.py` | Formatting requirementsブロックへ記号禁止パラグラフ追加、`normalize_article_formatting`拡張要否の判断 | +10〜20(Prompt文言) |
| `er019_family_x_ja_writer_o_r1_r2_01.py` | 同種のPrompt予防ブロック追加(1.6節のGap解消) | +10〜20 |
| Family B/C該当Writer(Phase 2で特定) | 同上 | 未見積り(要追加調査) |
| `er003_key_words_canonicalization.py` | 変更なし(Key Phrase既存ルールは維持する設計のため) | 0 |
| test各種 | 新規Validator/Normalizerのunit test | +40〜80 |

### 8.2 影響範囲

- Key Phrase既存経路(`PRODUCTION_WIRED`済み)には触れない設計
  (4(c)節の非対称設計)。
- Family A/X本文経路・Family X ja_writer・Family B/C(該当あれば)の
  Prompt+Normalizerが新規追加範囲。
- Assembly Gate・Human Review Lock・Connected Speech層・Local
  Rewrite層はいずれも無変更(既存retry/fallback上限を再利用)。

### 8.3 Gate 3チェックリスト充足計画

既存PM_GOVERNANCE Gate 3(想定: 回帰・Runtime evidence・approved spec
との一致確認)に対応する形で、Phase 2では: (a) 新規unit test、
(b) 既存全体回帰(`run_project_regression.py`)、(c) 実TTS Standard
同期でのRuntime evidence(6節fixture案参照)、(d) SSOT更新
(CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md)を実施する計画。

### 8.4 費用見積(Runtime evidence取得分のみ)

fixture案(次節)の記号×言語×位置の代表ケース(概算12〜16パターン)を
それぞれ1回ずつTTS Standard同期で実行する場合、既存の同規模Trial実測
(`KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01`で¥5.3程度/6件LLM
呼び出し、TTS/ASRは別途)を参考に、TTS+ASR実測を含めても**概算
¥50〜150程度**(既存の同種fixture検証Trialの実測レンジ、確定額は
Phase 2実施時に確認)。

---

## 9. fixture案(代表記号ケース)

| # | 記号 | 言語 | 位置 | 入力例 | 期待Normalizer出力 | 期待Validator判定 |
|---|---|---|---|---|---|---|
| 1 | 〜 | JA | 文頭 | 「〜を示す」 | 「なになにを示す」 | PASS(既存Key Phrase経路と同一) |
| 2 | 〜 | JA | 文中(mid-string) | 「地元の店を〜と結びつける」 | 「地元の店をなになにと結びつける」(**本文用の新規汎用ルール、Key Phrase用は変換せずSTOPPEDのまま**) | 本文=PASS(新規)/Key Phrase=STOPPED(既存維持) |
| 3 | 〜 | JA | 範囲表記 | 「中〜高強度」 | 変換しない(意味的判断が必要、7節UDR-1) | USER_DECISION_REQUIRED |
| 4 | … | JA | 文中 | 「それは…違う」 | 「それは、違う」(読点変換) | PASS |
| 5 | … | EN | 文中 | "Wait... that's wrong" | "Wait, that's wrong"(comma変換) | PASS |
| 6 | / | JA | 文中 | 「AとB/Cのどちらか」 | Writer予防が主、Normalizerでは変換せずValidatorでブロック(意味的に and/or の判別が必要なため) | STOPPED(Writer再生成を促す) |
| 7 | 括弧 | JA | 補足併記 | 「値上がり(値段が上がること)」 | 変換しない、Validatorでブロック | STOPPED |
| 8 | ：；| JA | 文中 | 「理由は3つ:予算、人手、時間」 | 「理由は3つ。予算、人手、時間」 | PASS |
| 9 | ：；| EN | 文中 | "Three reasons: budget, staff, time" | "Three reasons. budget, staff, time"(またはカンマ) | PASS |
| 10 | % | EN | 数値 | "50% of users" | 変換しない(Writer予防が主、"50 percent"はWriter側で書く) | Validatorは検出のみ(blockはしない、Prompt優先) |
| 11 | $ | EN | 数値 | "$83" | 同上(Writer予防優先) | 同上 |
| 12 | URL | JA/EN | — | "https://example.com" | Writer予防のみ(Normalizerでの機械除去はしない、記事内容として不適切なため生成させない方針) | STOPPED(検出時) |
| 13 | 絵文字 | JA/EN | — | "素晴らしい😊" | 既存`normalize_article_formatting`と同じUnicode `So`除去 | 既存どおりPASS(除去後) |
| 14 | Markdown | EN | — | "**important**" | 既存`normalize_article_formatting`と同じ`**`除去 | 既存どおりPASS |
| 15(Meta1) | … | JA | japanese_title(Stage 3a実例) | canonical title中の"…"(実データ、`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md`) | ポーズ変換または再生成 | 現状STOPPED→今回の設計でPASSへ改善見込み |
| 16(Meta2) | 〜 | JA | key_phrases kp1 gloss(Stage 3a実例) | B1B kp1 rank1 japanese gloss中の"〜"(実データ、同Report) | 既存Key Phrase経路の対象(mid-stringなら既存どおりSTOPPED維持) | 既存どおり(Key Phraseは意図的に非対称、上記#2参照) |

---

## 10. Dangling Reference Check(Phase 1範囲)

本Phase 1はドキュメント作成のみでコード変更を行っていないため、
Dangling Referenceの発生源はない。Phase 2実装時には、既存の
`detect_gloss_placeholder_notation`・`convert_display_gloss_to_tts_
text`・`_JA_GLOSS_PARENTHETICAL_RE`のいずれも変更しない設計(4節)の
ため、既存呼び出し元への影響はない前提。Phase 2実装完了後に改めて
Dangling Reference Checkを実施する。

---

## 11. 今回実施しなかったこと

- Production code・Prompt・SSOT(CURRENT_SPEC.md/DECISION_LOG.md/
  OPEN_ITEMS.md)への変更(委任範囲外、Phase 2)。
- 実際のTTS/ASR API呼び出し(費用¥0を維持)。
- Family B/C本体(`er012_b_family_voices_production_01.py`本体・
  `er013_family_c_production_01.py`本体)の日本語segment有無の完全な
  確定(1.4-1.5節、Phase 2でさらなるgrep確認を推奨)。
- コロン・セミコロン・%$¥がMarkdown見出し由来か本文由来かの分類
  (1.9節、Phase 2推奨)。
- 現行Production採用TTSモデル(`gemini-2.5-pro-preview-tts`/
  `gemini-3.1-flash-tts-preview`)での`<short pause>`タグ実際の解釈
  可否の実測Trial(5節、Phase 2候補)。

---

## 12. 証跡・参照先一覧

- `NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md`(Stage 3a/3b、
  実STOP実例)
- `KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01_REPORT.md`
- `KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01_REPORT.md`
- `TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01_REPORT.md`
- `OPEN_ITEMS.md` OPEN-117行・OPEN-118行
- `docs/pm/recon_connected_speech_scope_01.md`
- `docs/pm/recon_reading_validation_wiring_01.md`
- `docs/pm/recon_tts_local_rewrite_wiring_01.md`
- `er003_audio_tts_asr_safety.py`
- `er003_key_words_canonicalization.py`
- `er003_key_words_min_unit.py`
- `er003_v1_n3_01_tts_generate.py`
- `er003_v1_n3_01_articles_generate.py`
- `er019_family_x_audio_production_runner_01.py`
- `er019_family_x_ja_writer_o_r1_r2_01.py`
- `er012_b_family_voices_production_01.py`
- `er013_family_c_production_runner_01.py`
- `CURRENT_SPEC.md`「Family Z(Fiction)」節
- Gemini TTS公式ドキュメント: `https://ai.google.dev/gemini-api/docs/speech-generation`
  (HTTP GET取得日時: 2026-09-27)
