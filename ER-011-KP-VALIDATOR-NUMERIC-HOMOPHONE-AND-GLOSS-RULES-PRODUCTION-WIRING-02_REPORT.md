# ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02

種別: **Production配線**。ユーザーが2026-09-06に`APPROVED_FOR_PRODUCTION`と
決定した3判断のうち、判断2(Track A縮小リスト採用)・判断3(Track B
Approach2採用)を配線し、判断4(Prompt規約A/B採用・規約C不採用)は
**規約Bのみ配線し、規約Aは配線不能であることをRuntime evidenceで実証**
した(詳細は§5)。**本タスクではSSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/
`OPEN_ITEMS.md`)・Git commit・`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET.md`
には一切触れていない**(別タスク`ER-011-ASSEMBLY-HEADROOM-SAFETY-VALVE-
PRODUCTION-WIRING-01`が担当。SSOT反映案は§7に転記可能な形で記載)。

Gate 3チェックリストは全項目実施済み(§6参照)。`PRODUCTION_WIRED`は
人間ユーザーの最終承認とSSOT反映後に宣言されるべきであり、本Reportでは
実装・回帰・Runtime evidence取得までの完了を報告する。

## 1. 変更ファイルと差分要旨

### 1.1 Track A(JA数字ゲート一般化、縮小リスト)

`er003_audio_tts_asr_safety.py`:
- `_KANJI_COUNTER_RE`(旧: 助数詞「つ」限定)を、閉じた助数詞リスト
  `("つ","泊","回","件","年","時間","か月","週","歳")`(**「日」「人」は
  意図的に除外**)の直前の単独漢数字(一〜九)へ拡張。
- `normalize_kanji_counter_numerals_ja()`(既存Production関数、シグネチャ
  無変更)がこの拡張済み正規化を行うようになる。
- この関数は`er007_ja_asr_validator_01.normalize_ja()`(全文JA Validator)
  と`er003_audio_tts_asr_safety.validate_japanese_short_segment_match()`
  (短seg Validator)の両方から呼ばれている共有部品のため、**両経路へ
  自動的に配線される**(呼び出し側コードの変更は不要)。

`er007_ja_asr_validator_01.py`: `normalize_ja()`のdocstringを拡張後の
仕様に合わせて更新(ロジック変更なし)。

「日」「人」を除外した理由(Trial-17実証済み): 「日」を含めると慣用句
「三日坊主」(不規則読み"mikkabouzu")が"3日坊主"へ変換され、kakasiが
数字文字を音声化しないため全文ひらがなASRとの読み一致フォールバックが
壊れる実regressionが発生する。「人」も「一人/二人」が不規則読み
("hitori"/"futari")であり同型のリスクを持つため予防的に除外。

### 1.2 Track B(EN厳密同音の数字ゲート例外、Approach2)

`er006_preprod_hardening_01_validation.py`:
- `normalize_numeric()`/`normalize_text()`に`convert_cardinals: bool = True`
  引数を追加(デフォルトは従来通り、既存呼び出しは無変更)。
- 新規`_tokenize_raw_no_cardinal_conversion()`: cardinal語変換前の「生語」
  token列を取得する診断用ヘルパー。
- 新規`_locate_number_mismatch_opcodes()`: 数字不一致opcodeの位置特定
  (`protected_check()`と同じSequenceMatcherを読み取り専用で再実行)。
- 新規`_try_homophone_number_rescue()`: alignment_safe(テキスト全体で
  cardinal変換によるtoken数変化が無いこと)を必須とし、1トークン対
  1トークンの置換opcode全てが変換前の生語同士でCMU辞書ARPAbet**完全**
  一致(`er008_asr_variant_hardening_15_homophone_en.homophone_arpabet_
  equivalent()`を再利用、新辞書なし)の場合のみrescueを許可する。
- `classify_asr_match()`の数字保護ゲート(`if not protected.passed:`)に、
  即`TRUE_CONTENT_MISMATCH`にする前の狭い例外として上記rescueを追加。
  該当時は新分類`HOMOPHONE_MATCH_NUMBER_EXCEPTION`(`should_pass=True`)
  を返し、`VALID_CLASSIFICATIONS`へ追加。reasonへrescue詳細
  (canonical/asr生語ペア)を必ず記録。
- `evaluate_attempt()`(初回・retry・fallback全経路の統一エントリポイント、
  voice01/news_tail_fix/point_headings_aoede/repro01/crosslevel_audio_02
  等が既に配線済み)は`classify_asr_match()`をそのまま呼ぶため、**呼び出し
  側コードの変更なしに全経路へ配線される**。`should_stop_retrying()`は
  既存の`should_pass`セーフティネットにより新分類でも正しく動作する
  (Connected Speech Accept導入時と同じ設計)。

Approach1(緩いローカル判定)はTrial-17で構造的に不健全と実証済みのため
採用しない(実装もしていない)。

### 1.3 Prompt規約B(canonicalization prompt、key_phraseスコープのみ)

`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt`
の「その他の規則」節へ1行追加:
「key_phraseに「～」「〜」「…」のようなプレースホルダー記号を一切使わない
でください。...」

**規約A、および規約Bのgloss側は配線していない**(理由は§5、Gate 3
Runtime evidence(3)で実証)。

## 2. 回帰結果(件数・判定変化)

すべて「現在のHEAD(本タスク直前、他タスクのcommit `eb8d99c`込み)」を
baseline、本タスクの変更適用後をcandidateとして、同一入力を両方の
コードへ通して比較した(`git checkout HEAD --`で一時的に4ファイルのみを
戻し、baseline実行後に復元。対象外ファイルは一切触れていない)。

| スイート | 件数 | 判定変化 |
|---|---|---|
| JA Validator全fixture(POSITIVE/NEGATIVE/ENTITY_LIKE/PHONETIC_UNCERTAIN/WHOLE_TEXT×2/KNOWN_TRADEOFF、READING_RESOLVER系1件を除く) | 34件 | **0件** |
| JA Validator全体(上記+Reading Resolver実LLM1件、`er007_ja_asr_validator_01_test.py`フル実行) | 35件 | 全件PASS(exit 0) |
| er003短seg fixture代表4件(つ限定パターン等) | 4件 | **0件**(baseline/candidate一致、かつ期待値通り) |
| EN Validator全fixture(POSITIVE29+AMBIGUOUS2+NEGATIVE28、`er006_preprod_hardening_01_validation_test.py`) | 59件 | **0件**、フル実行exit 0 |
| EN homophone fixture(ER-008 Part J-2、`er008_asr_variant_hardening_15_homophone_en_test.py`) | 8ペア+entity 2件=6 test関数 | **0件**、ALL TESTS PASSED |
| Connected Speech Validator+A2 Reading Resolver(`er011_no18_connected_speech_reading_resolver_wiring_08_test.py`) | 15項目 | **0件**、全15項目PASS(#9で既存仕様通り実LLM呼び出し1回) |
| Key Phrase canonicalization(`er003_test_key_words_canonicalization.py`) | 43 test | **0件**、全PASS |

**判定が変わったケースは0件**(新規追加したTrack A/Bロジックは、既存の
全fixtureに対して一切副作用を発生させていない)。

補足(無関係): `er006_pool_benches_luna_audio_wiring_test.py`が
`er003_v1_sing01_news_tail_fix.py: audio_validationがimportされていない`
で1件failするが、`git stash`でTrack A/B変更を除去したbaselineでも同一
failureを確認済み(本タスク由来ではない既知の無関係failure)。

補足2: Trial-13 b1b `full_story_part1`等13件本文+kp1/2/5(EN/JA)を保存
テキストで再判定した際、`point_one`セグメントについて**Trial-13実行時の
歴史的な保存値**(`NORMALIZED_MATCH`)と、現在のbaseline/candidate両方の
再判定結果(`ASR_VALIDATION_UNCERTAIN`、"Slow"/"Solo"のentity_like判定)
が一致しない事象を発見したが、baseline/candidateで完全に同一結果
(§2表参照、19件中0件変化)であることを確認しており、**本タスクの変更に
起因しない**(Trial-13実行時[2026-09-05]から現在までの間の無関係な
コードドリフトの可能性、本タスクでは追跡していない、報告のみ)。同様に
No.18 A2 (`no18_tight_speech_only_removal_trial_15`)の14segmentについても
baseline/candidateは完全一致(0件変化)を確認した。

## 3. 新規回帰テスト(Gate 3チェックリスト、全件PASS)

`er011_output/kp_validator_numeric_homophone_gloss_production_wiring_02/gate3_new_fixtures_result.json`

- JA: 2泊/二泊→PASS(NORMALIZED_MATCH)、三日坊主→無変化(PHONETIC_MATCH
  のまま)、約2泊/約三泊→FAIL(TRUE_CONTENT_MISMATCH)、2泊/泊(数字消失)
  →FAIL、京三(固有名詞内漢数字)→無変換のままEXACT_MATCH。
- EN: "point to"/"Point two."→PASS+`HOMOPHONE_MATCH_NUMBER_EXCEPTION`
  ラベル記録、"...for you"/"...four you"→PASS+同ラベル、"point to"/
  "point three"→FAIL、canonical digit 2 vs asr digit 3→FAIL、近似音
  ("nine"/"mine")→FAIL(PASSしない)。
- Prompt規約B: 生成したuser_messageに「プレースホルダー記号」の文言が
  含まれることをassertで確認済み(§5のRuntime evidence(3)内で実施)。

## 4. Runtime evidence(TTS/ASR再生成なし)

保存先: `er011_output/kp_validator_numeric_homophone_gloss_production_wiring_02/`

**(1) kp3_ja_charon/kp4_en**(`runtime_evidence_trial13_revalidation.json`):
Trial-13 b1bで実際にSTOPPEDした全attempt(kp3標準2回+fallback1回、kp4
minimal2回+english_lock2回+fallback2回)の保存済みASR textを、修正後の
`classify_ja_asr_match()`/`classify_asr_match()`へ直接入力。

- kp3_ja_charon: 標準attempt2件→`NORMALIZED_MATCH`/True、fallback1件
  (ASR「中央地は約二泊。」、値→地の誤変換込み)→`PHONETIC_MATCH`/True
  (読みが一致するため、内容誤りではなく音訳ゆれと正しく判定)。
- kp4_en: 6attempt全て(いずれもASR"Point two.")→
  `HOMOPHONE_MATCH_NUMBER_EXCEPTION`/True、reasonへrescue詳細記録済み。

**(2) 既存PASS済みsegmentの無変化確認**: Trial-13 b1b本文13件+kp1/2/5
(EN/JA)、計19件をbaseline/candidate両方で再判定し**0件変化**
(`trial13_segments_kp125_baseline.json`/`_candidate.json`)。No.18 A2
14segmentも同様に0件変化(`no18_a2_revalidation_baseline.json`/
`_candidate.json`)。

**(3) Prompt規約A/B**: 実データ(実費、下記Cost参照)。

## 5. 発見: 規約A、および規約Bのgloss側は「canonicalization prompt」への
追加では配線できない(アーキテクチャ上の不一致、USER_DECISION_REQUIRED候補)

指示は「Production側の選定Prompt(canonicalization prompt生成コード、
`er011_output/.../b1b/key_phrases/canonicalization_prompt.txt`の生成元
=`er003_key_words_canonicalization.py`+
`b1_p2_keywords_canonicalization_prompt_template.txt`)」を対象に規約A/B
追加を求めていたが、コード調査とRuntime evidenceにより以下を確認した:

- `er003_key_words_canonicalization.py`の`CANONICALIZATION_JSON_SCHEMA`
  (Production schema)には`japanese_gloss`フィールドが**存在しない**。
  `build_user_message()`もitems_for_promptへgloss情報を一切渡さない。
- `merge_canonicalization_result()`の`japanese_gloss`は、**常に選定工程
  (方式L、`original.get("ja_gloss")`)からの無変更pass-through**であり、
  canonicalization工程はgloss文字列を一度も生成・変更しない。
- 実際にja_glossを生成しているのは、選定Prompt
  `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`
  (`er003_b1_p2_keywords.py`→`er003_key_words_production.py`→
  `er003_key_words_min_unit.py`の`_ITEM_SCHEMA_PROPERTIES`)であり、
  Trial-13の`keywords_selector_prompt.txt`と文字単位で一致することを
  確認した。

**実証(Runtime evidence(3)、実際に1回LLM呼び出し)**: 規約Bを追加した
現行canonicalization templateで、Trial-13 B1の実際の入力
(article.md+`keywords_runtime_metadata.json`の5件、rank/display_phrase/
source_span/source_sentence)に対しProduction関数
(`make_canonicalization_fn`/`run_canonicalization_gate`、schema無変更)を
1回実行した結果:
- `status=CANONICALIZATION_PASS`、5件全て`qa_overall_status=PASS`。
- key_phrase 5件は原本(Trial-13)と**全件完全一致**(学習価値の劣化なし)。
- LLM出力キー一覧に`japanese_gloss`は**存在しない**
  (`has_japanese_gloss_in_llm_output: False`)。
- `merge_canonicalization_result()`後のjapanese_glossは、rank4含め
  Trial-13原本の値(「～を示す、～を指し示す」、placeholderそのまま)と
  **完全に同一**——つまり規約A・規約Bのgloss側をこのprompt templateへ
  追加しても、実際のgloss出力には**一切効果が無い**ことを実データで
  確認した。

証跡: `gate3_evidence3_user_message.txt`(規約B文言の混入確認済み)、
`gate3_evidence3_raw_result.json`(生応答)、`gate3_evidence3_merged.json`
(マージ後、japanese_gloss無変化の確認)。

**結論**: 規約B(key_phraseスコープ)のみ、指示通りcanonicalization
templateへ配線した(§1.3、実効果あり)。規約A、および規約Bのgloss側
(「～」等の除去)を実際に効かせるには、選定Prompt
(`b1_p2_keywords_l_prompt_template.txt`、および同型のA2/B2用テンプレート)
側への追加が必要である。これは本タスクで名指しされたファイル
(canonicalization)の範囲外であり、選定Promptは他の全記事・全レベルで
共有される広く使われるPromptであるため、**本タスクでは実装せず報告する**
(拡大が必要と判断した場合は実装せず報告する、という運用ルールに従う)。
ユーザー/Fableの判断を仰ぐ。

## 6. Gate 3チェックリスト充足状況

- [x] Production正式初回経路への配線(初回・retry・fallback・Key Phrase
  Master Audio Store経路のいずれも、共有関数`classify_asr_match()`/
  `classify_ja_asr_match()`/`normalize_kanji_counter_numerals_ja()`を
  経由するため自動的に配線される。§1参照)。
- [x] 既存回帰(JA/EN/homophone/Connected Speech/Reading Resolver/
  canonicalization、§2)。
- [x] 新規回帰テスト(§3)。
- [x] Runtime evidence(§4)。
- [x] approved specとProduction挙動の一致確認: Track A(縮小リスト、
  日/人除外)・Track B(Approach2、alignment_safe必須、完全同音のみ)は
  approved specと完全一致。Prompt規約は規約Bのみ配線、規約A・規約Bの
  gloss側は配線不能をRuntime evidenceで実証(§5、乖離を隠さず報告)。
- [x] Report作成(本ファイル)。SSOT反映案は§7。

## 7. SSOT反映・commitは後続タスクで実施(本タスクでは未実施)

以下はそのまま貼り付け可能な形で記載する(本タスクではファイルへの
書き込み・commitは一切行っていない)。

### CURRENT_SPEC.md 追記案

```
## ASR Validator数字ゲート(JA閉じた助数詞リスト・EN完全同音例外)
2026-09-06(ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-
PRODUCTION-WIRING-02でPRODUCTION_WIRED、ユーザー承認判断2・3):
- JA: er003_audio_tts_asr_safety.normalize_kanji_counter_numerals_ja()は
  閉じた助数詞リスト(つ/泊/回/件/年/時間/か月/週/歳)の直前の単独漢数字
  (一〜九)を算用数字へ正規化する。「日」「人」は不規則読みによる
  regressionリスクのため意図的に除外(「二十」等の助数詞を伴わない
  漢数字も対象外)。
- EN: er006_preprod_hardening_01_validation.classify_asr_match()は、
  数字保護ゲートの唯一の不合格理由がalignment_safeな1対1の数字語置換で
  あり、かつcardinal変換前の生語同士がCMU辞書ARPAbet完全一致の場合のみ
  HOMOPHONE_MATCH_NUMBER_EXCEPTIONとしてPASSする(近似音は不可)。
- Key Phrase canonicalization prompt(b1_p2_keywords_canonicalization_
  prompt_template.txt)は、key_phraseにプレースホルダー記号
  (「～」「〜」「…」)を使わない規約を明記する。ただしja_glossは
  canonicalization工程では生成・変更されない(選定Prompt
  b1_p2_keywords_l_prompt_template.txt等が実際の生成元)ため、gloss側の
  同種の規約追加は別タスクの検討事項(OPEN-116参照)。
```

### DECISION_LOGエントリ案

```
## 2026-09-06 ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02
Trial-17検証済みのTrack A(JA助数詞リスト一般化・縮小版)・Track B(EN
完全同音の数字ゲート例外・Approach2)をProduction配線した(ユーザー
2026-09-06承認、判断2・3)。Prompt規約(判断4)はA/B採用のうち、規約B
(key_phraseのプレースホルダー禁止)のみcanonicalization prompt template
へ実配線した。規約A、および規約Bのgloss側(「～」除去)は、実際のjapanese_
gloss生成が選定Prompt(b1_p2_keywords_l_prompt_template.txt)側で行われ
canonicalization工程はglossを一切変更しないというアーキテクチャ上の
理由により、canonicalization templateへ追加しても効果が無いことを実LLM
呼び出し1回で実証した(canonicalization出力にjapanese_glossフィールド
自体が存在しないことも確認)。規約A・gloss側規約Bの実配線には、選定
Prompt(全記事・全レベル共有)への追加という、本タスクの指示範囲外の
作業が必要であり、USER_DECISION_REQUIRED(別タスクとして起票するか、
このまま据え置くか)。回帰: JA/EN/homophone/Connected Speech/Reading
Resolver/canonicalization test、計200件超で判定変化ゼロ。Runtime
evidence: Trial-13 kp3_ja_charon/kp4_enの保存済みSTOPPED attemptが
修正後ValidatorでPASSすることを確認、既存PASS済み33件(Trial-13本文13+
kp1/2/5×2言語+No.18 A2 14件)は無変化。詳細は
`ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-
WIRING-02_REPORT.md`参照。
```

### OPEN_ITEMS.md OPEN-116更新案(追記文、既存行の末尾に追加)

```
**2026-09-06追記(ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-
PRODUCTION-WIRING-02)**: Track A(縮小リスト)・Track B(Approach2)を
Production配線完了(回帰・Runtime evidenceとも問題なし、詳細は同管理ID
のREPORT参照)。Track C(規約A/B)は規約Bのみ配線(key_phraseスコープ)。
規約A、および規約Bのgloss側は、canonicalization工程がjapanese_glossを
生成・変更しない(選定Prompt側が生成元)というアーキテクチャ上の理由で
配線不能であることを実データで確認した。選定Prompt(b1_p2_keywords_l_
prompt_template.txt等、全記事共有)への追加要否は未着手、
USER_DECISION_REQUIRED。
```

### OPEN_ITEMS.md OPEN-40関連の補足案

```
**2026-09-06追記**: OPEN-116(a)のJA数字ゲート表記ゆれ問題は
ER-011-KP-VALIDATOR-NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-
WIRING-02でProduction配線済み(縮小リスト、日/人除外)。OPEN-40本体
(N3専用スクリプトのnormalization処理のProduction共通モジュール未統合)
自体は引き続き未解消。
```

## 8. Cost Trace

| 項目 | 内容 | 金額(概算) |
|---|---|---|
| Track A / Track B | ローカル判定のみ、API呼び出しなし | $0 |
| Runtime evidence (1)(2) | 保存済みテキストの再判定のみ、API呼び出しなし | $0 |
| Runtime evidence (3) | `gpt-5.6-sol`(reasoning effort=high)1回、canonicalization(Trial-13 B1 5件) | 実行はしたがusage(token数)はこの呼び出し経路では未取得(Production関数`make_canonicalization_fn`がusageを返さない設計のため)。Trial-17 Track C(同モデル・同reasoning effort・同程度の入出力サイズ)実績値(input 4720 tok/output 3165 tok、約$0.1185[約¥19])を参考値として記録 |
| Connected Speech/Reading Resolver regression | 既存test内の仕様通りの実LLM呼び出し1回(#9、A2 Reading Resolver、Track A/Bとは無関係の既存挙動) | 既存test既定コストのみ(新規追加なし) |

## 9. STOP条件該当有無

該当なし。近似音・別発音のPASS化、一般漢数字変換(A')、「日」「人」の
リスト追加、規約Cの追加、retry上限・fallbackの変更、TTS/ASR再生成、
並行タスク担当ファイル(`er003_v1_n3_01_assemble.py`・`er002_common.py`)
の編集、他Agent起動はいずれも行っていない。SSOT・Git・
`docs/pm/ACTIVE_TASK.md`・`RESULT_PACKET.md`への変更も行っていない
(本タスクの指示通り)。

## 10. 変更ファイル一覧(本タスクで編集した既存ファイルのみ)

- `er003_audio_tts_asr_safety.py`(Track A)
- `er007_ja_asr_validator_01.py`(Track A、docstring更新のみ)
- `er006_preprod_hardening_01_validation.py`(Track B)
- `er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt`(規約B)
- `er011_output/kp_validator_numeric_homophone_gloss_production_wiring_02/`配下の証跡ファイル(新規)
- 本Reportファイル(新規)

SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/
`HISTORY_INDEX.md`)・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`・
Gitへのcommitはいずれも本タスクでは実施していない(後続タスクで実施)。
