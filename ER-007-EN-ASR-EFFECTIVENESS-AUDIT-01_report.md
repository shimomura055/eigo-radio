# ER-007-EN-ASR-EFFECTIVENESS-AUDIT-01 完了報告

**Audit専用タスク。実装変更は一切行っていない。新規API Costは$0**
(既存ログの再解析、既存の実音声fixture[No.6 Sweeny]の同一セッション内
既存検証結果の再利用、および検証ロジックへの仮想テキスト直接シミュレーション
のみ。新規TTS/ASR/LLM呼び出しはゼロ件)。

## 中心質問への回答(先に結論)

**English ASR Validatorは、日本語で見つかったような「長いsegmentでは
実質的に内容を見ていない」構造的gapを持っていない。** 長いFull Story
segment(実測94〜176語、500〜1,100文字超)の中間で意味が変わる誤りを
起こした場合も、実際のProduction Validator(`classify_asr_match`)へ
実データを通したところ、全17件のfixtureで期待通り検知された(詳細は
本文参照)。**最終判定: `EFFECTIVE`**。

## 1. English Production ASR call path

| # | 確認事項 | 結果 |
|---|---|---|
| 1 | ASR engine | OpenAI `gpt-4o-mini-transcribe`(Primary、`er006_asr_provider_routing_01.py`) |
| 2 | Primary ASR retry回数 | Cascade内で最大2回(`CASCADE_CONFIG.max_primary_attempts=2`) |
| 3 | `classify_asr_match()`までのcall path | `generate_narration_snippet_verified_strict(text,"en",...)` → `secondary_asr.evaluate_attempt_with_cascade()` → `val.evaluate_attempt()` → `classify_asr_match()`。B1/A2・Full Story/Point/Key Phrase/Preview/Commentの**全English segmentが同一のこの経路を通る**(下記4参照) |
| 4 | Secondary ASR Cascadeへ入る条件 | `classify_asr_match()`の結果が`ASR_VALIDATION_UNCERTAIN`かつ`content_word_diffs`が**全て**entity_like(固有名詞らしき語)である場合のみ(`is_entity_like_mismatch()`)。数字/否定/通常内容語の差が1件でもあれば`TRUE_CONTENT_MISMATCH`となりCascade対象外 |
| 5 | TTS retryへ戻る条件 | `should_retry=True`(=`TRUE_CONTENT_MISMATCH`または`TTS_FAILURE`)の場合。Cascade対象(entity-like)の場合はTTS再生成せずASRのみ再検証 |
| 6 | Human Reviewへ進む条件 | Cascade4段階(Primary#2→Secondary#1→Secondary#2)を尽くしても`should_pass`にならない場合、`human_review_required=True`としてqueueへ記録(TTSは再生成しない) |
| 7 | segment長による分岐 | **なし**。`classify_asr_match()`のロジック自体はsegment長に関わらず同一(word-level diff、全文字数・全語を評価対象とする) |
| 8 | segment種類による分岐 | **なし**。Full Story/Point/In One Line/Preview/Comment(B1英語)/Key Phrase Englishのいずれも同一の`generate_narration_snippet_verified_strict`→`classify_asr_match`経路を通る。差はsegmentごとの`max_extra_chars`(長さ許容、生成品質パラメータ)・trim safety margin(音声トリム)のみで、**検証ロジックの厳密さ自体は変わらない** |
| 9 | short/longでValidatorロジックが変わる箇所 | **なし**(日本語との決定的な違い)。日本語は30文字を境に検証方式そのものが変わる(prefix+lengthのみ vs 意味検証追加)が、英語は常に同一の`classify_asr_match()`(数字/否定/内容語Protected Check込み)を適用する |
| 10 | legacy validation pathがProductionに残っていないか | 旧`er003_audio_tts_asr_safety.validate_asr_match()`(**先頭N語[既定6語]のprefix一致のみ**という、現在の日本語Validatorと酷似した弱い方式)がコード上は現存するが、呼び出し元は`er003_v1_b1_scaffold_audio_03_generate.py`/`er003_v1_iran01_b1_audio_fix.py`/`er003_v1_sing01_audio_generate.py`/`er005_avr02_instruction_separation.py`/`er003_v1_sing01_voice01_labels_v2.py`のみで、いずれもCURRENT_SPEC記載の現行Production call site 6箇所には含まれない(legacy/experimental script)。**現行Productionへの残存は確認されなかった** |

## 2. No.1〜6 English segment長分布

既存の`tts_generation_results.json`を再解析(新規TTSなし)。**126 segment**
(6 topic × 21 segment/topic)を収集した。

| word count帯 | 件数 | 比率 |
|---|---|---|
| ≤20語 | 42 | 33.3% |
| 21〜40語 | 26 | 20.6% |
| 41〜60語 | 24 | 19.0% |
| 61〜100語 | 11 | 8.7% |
| >100語 | 23 | 18.3% |

Full Story Part1/2(最長のsegment種別)は、全24件(6 topic×2 level×2 part)で
**94〜176語(500〜1,128文字)**の範囲だった。長いsegmentは実際に相当数
存在する(全体の18.3%が100語超、27.0%が61語超)。

## 3. `classify_asr_match()`が実際に比較する内容

| 項目 | 扱い |
|---|---|
| 全文比較か | **はい**。`difflib.SequenceMatcher`によるword-level diffで、canonical/ASR両方の**全token列**を比較する(prefixのみではない) |
| token単位比較か | はい(空白区切りtoken列) |
| sequence/orderを見ているか | はい。`SequenceMatcher`はequal/replace/delete/insertのopcodeで並び自体を評価する(bag-of-wordsではない) |
| 数字 | **Protected**。canonical/ASR双方の数値トークン集合が完全一致しない限り`TRUE_CONTENT_MISMATCH`(桁区切り・小数点・パーセント・通貨・序数・指数等の表記ゆれは正規化後に比較) |
| 否定 | **Protected**。否定語リストとの一致有無が異なれば`TRUE_CONTENT_MISMATCH` |
| 固有名詞 | 部分的Protected。固有名詞らしき語(文中で大文字始まりだった語)**のみ**の差であれば`ASR_VALIDATION_UNCERTAIN`(Cascade対象)。固有名詞以外の内容語との複合差は`TRUE_CONTENT_MISMATCH`のまま |
| 内容語(動詞・形容詞・名詞等) | **Protected**。置換/欠落/追加のいずれも、固有名詞以外なら一致率に関わらず`TRUE_CONTENT_MISMATCH` |
| omission(脱落) | Protected。`SequenceMatcher`の`delete`opcodeとして検出、content_word_diffsへ記録 |
| addition(追加) | Protected。`insert`opcodeとして検出 |
| word order | 表記正規化(発音区別符号・ハイフン・複合語分かち書き・英米綴り・序数)の範囲でのみ許容差。意味を変える語順変化はopcode上の差として検出される |
| punctuation | 許容差(正規化で吸収、記号自体は比較対象外) |
| 数式(等号・不等号・掛け算記号・上付き指数等) | Protected(前々タスクで一般化済み)。`10⁻¹⁶`と`10⁻⁶`等、符号・桁が異なれば別tokenとして区別される |

**「文頭や一部tokenだけ合っていればPASSする構造になっていないか」への回答:
いいえ。** `SequenceMatcher`は文字列全体をtoken列として整列するため、
文中・文末のどこで差が生じても`content_word_diffs`/`number_mismatches`/
`negation_mismatches`として検出される。プレフィックスのみのチェックでは
ない(下記5-6で実証)。

## 4. Blind Spot Simulation結果(実データ、全17件)

No.4 Full Story Part2(長文、統計密度が高い実segment)・No.5 Point One本文
(中程度)・No.6 point_one_heading相当(短文)を土台に、`classify_asr_match()`
へ直接通した。**17件中17件が期待通りの結果。**

| # | カテゴリ | 変更内容(実データ土台) | 結果 |
|---|---|---|---|
| 5-1a | Content word置換 | `rose`→`fell`、`reached`→`dropped`(No.4 LONG) | `TRUE_CONTENT_MISMATCH`(検知) |
| 5-1b | Content word置換 | `places`→`chains`(No.5 MEDIUM) | `TRUE_CONTENT_MISMATCH`(検知) |
| 5-2a | 数字誤り | `150`→`140`(No.4 LONG) | `TRUE_CONTENT_MISMATCH`、`numbers=[('150','140')]`(検知) |
| 5-2b | 数字誤り | `1.71`→`1.17`(No.4 LONG) | `TRUE_CONTENT_MISMATCH`(検知) |
| 5-3a | 否定反転 | `did not find`→`did find`(No.4 LONG) | `TRUE_CONTENT_MISMATCH`、`negation=[('not','')]`(検知) |
| 5-3b | 否定反転 | `did not change`→`did change`(No.4 LONG) | `TRUE_CONTENT_MISMATCH`(検知) |
| 5-4 | 文中フレーズ脱落 | 中間の1段落(3文)を丸ごと削除(No.4 LONG) | `TRUE_CONTENT_MISMATCH`、`delete`opcode検出(検知) |
| 5-5 | 文中フレーズ追加 | canonicalにない一文を中間へ挿入(No.4 LONG) | `TRUE_CONTENT_MISMATCH`、`insert`opcode検出(検知) |
| 5-6 | **文頭・文末のみ保持**(対照テスト) | 文頭6語+文末6語のみ一致、中間を無関係な内容へ総入れ替え(No.4 LONG) | `TRUE_CONTENT_MISMATCH`(**PASSしない**。日本語で起きた問題の対照実証) |
| 5-7a | 固有名詞orthographic uncertainty | `Sweeny`→`Sweeney` | `ASR_VALIDATION_UNCERTAIN`、`is_entity_like_mismatch=True`(Cascade対象として正しく分岐) |
| 5-7b | 固有名詞orthographic uncertainty | `Ottoni`→`A Tony`(実観測パターン) | 同上 |
| 5-8a | 真の固有名詞違い | `Sweeny`→`Johnson`(実在別姓) | `ASR_VALIDATION_UNCERTAIN`、`is_entity_like_mismatch=True`(**分類層では5-7と区別されない、詳細は5節参照**) |
| 5-8b | 真の固有名詞違い | `Ottoni`→`Martinez` | 同上 |
| 5-8c | 真の固有名詞違い | `Boavida`→`Barcelona`(地名) | 同上 |
| 6-short | 長さ比較 | `powerless`→`powerful`(短文) | `TRUE_CONTENT_MISMATCH`(検知) |
| 6-medium | 長さ比較 | `discourage`→`encourage`(中文) | `TRUE_CONTENT_MISMATCH`(検知) |
| 6-long | 長さ比較 | `increased`→`decreased`(長文、全体に対する語数比率は最小) | `TRUE_CONTENT_MISMATCH`(検知) |

**5-6(文頭・文末のみ保持)は特に重要**: 日本語Validatorが構造的に見逃す
パターン(prefix一致のみでPASS)を英語で再現しようとしたが、`classify_asr_match`
は`SequenceMatcher`による全文token列比較のため、中間の大規模な入れ替えを
`TRUE_CONTENT_MISMATCH`として正しく検知した。

## 5. 固有名詞: 5-7/5-8の分類層と安全性層の違い(重要な補足)

fixture結果が示す通り、**`classify_asr_match()`単体では、真の固有名詞違い
(5-8)とASR表記ゆれ(5-7)は区別されない**(どちらも`is_entity_like_mismatch=True`
でCascade対象になる)。安全性は分類層ではなく、**Cascadeが実際に一致する
書き起こしを得られない限りPASSしない**という一段上位の設計で担保されている。

これを実際の音声で確認するため、同一セッション内で既に実施済みの検証結果
(`er006_output/pool_pilot_01/coverage_gate_01/cascade_production_on_verify_log.jsonl`、
本タスクでの新規API呼び出しなし)を再利用した。No.6 Sweeny実音声(B1/A2とも)
で、Cascade有効化後にPrimary#1→Primary#2→Secondary#1→Secondary#2の4段階
ASR-only再検証を行った結果、**いずれの段階でもcanonical(Sweeny)と一致する
書き起こしは得られず**、TTS再生成0件のままHuman Reviewへ到達することを
確認済みである。もし音声が実際に別の名前(例: Johnson)を発話していれば、
4段階のどの再ASRも"Sweeny"とは一致し得ないため、**同じ理屈でHuman Reviewへ
到達し、誤PASSはしない**。これはfixtureではなく実音声・実コード双方で
裏付けられた設計である。

## 6. Segment長による性能差

4節の6-short/6-medium/6-longの結果はいずれも`TRUE_CONTENT_MISMATCH`
(検知)で、**類似度スコアの希釈による見逃しは確認されなかった**。

理由はアーキテクチャ上明確である: `classify_asr_match()`は全体類似度
(`ratio`)を**PASS/FAILの直接判定には使わない**。数字・否定・内容語の
Protected Checkが「1件でもあれば`TRUE_CONTENT_MISMATCH`」という設計
(`non_entity_diffs`が空でない限りPASSしない)であり、全体類似度は
Protected Checkを通過した後の`HIGH_SIMILARITY_SAFE`/`ASR_VALIDATION_UNCERTAIN`
の分岐にしか使われない。**長文で1語が全体スコアに埋もれてPASSする、
という懸念された経路は構造的に存在しない**(6-longで176語中1語の反対語
置換が、全体類似度に関わらず確実に検知されたことがこれを裏付ける)。

## 7. Cascade安全性

コードAudit(1節4-6)とfixture(4節5-7・5-8、5節)の両方で確認した。

- `is_entity_like_mismatch()`は、`content_word_diffs`が**1件でも**
  非entity-likeであれば`False`を返す設計であり、数字違い・否定反転・
  重要content word置換・大きな脱落を含むケース(4節5-1〜5-6)は、
  そもそもCascadeの対象条件(`ASR_VALIDATION_UNCERTAIN`かつ全diffが
  entity-like)を満たさない。**Cascadeが起動する前に`TRUE_CONTENT_MISMATCH`
  として弾かれるため、Cascadeによる誤PASSの経路自体が存在しない**
- 5節で述べた通り、Cascade対象(entity-likeのみの差)であっても、実際に
  canonicalと一致する書き起こしが得られない限りPASSしない設計であり、
  真の固有名詞違いが「たまたま近い」程度で誤って救済される余地はない

## 8. No.1〜6実Production ASR validation log再解析

既存の`tts_generation_results.json`を再解析(新規TTS/ASRなし)。

| 指標 | 値 |
|---|---|
| Total English ASR-validated attempts(No.1〜6合計) | 200 |
| `TRUE_CONTENT_MISMATCH` | 108件(54.0%) |
| `NORMALIZED_MATCH` | 59件(29.5%) |
| `ASR_VALIDATION_UNCERTAIN` | 20件(10.0%) |
| `EXACT_MATCH` | 13件(6.5%) |
| `verified=True`(最終PASS) | 72/200(36.0%) |
| retryが発生したsegment | 24/84(28.6%) |

**`TRUE_CONTENT_MISMATCH`が全体の過半数(54.0%)を占めている**ことは、
Validatorが実際の量産運用で頻繁に不一致を検出し、単純な通過儀式になって
いないことを示す実測上の裏付けである(日本語のように「検証してはいるが
ほぼ常にPASSする」設計とは異なる)。28.6%のsegmentで実際にretryが発生して
いることも、初回attemptの内容が機械的に素通りしていないことを示す。

## 9. English ASR実効性最終判定: **`EFFECTIVE`**

- 長いsegmentを含め、全文token列を対象に内容を実質的に検証できている
  (1節・3節・4節)
- semantic-critical error(数字・否定・内容語置換・脱落・追加)を
  fixture上17/17件確実に検知した(4節)
- segment長による重大な弱化は確認されなかった(6節、希釈経路が構造的に
  存在しないことをコード・実測双方で確認)
- Cascadeは、真の内容誤りを誤ってPASSさせる経路を持たず、固有名詞の
  真偽判定も「実際に一致するまでPASSしない」という設計で安全に保たれている
  (5節・7節)
- 実運用ログ(No.1〜6、200 attempts)でも、Validatorが実際に高頻度で
  不一致を検出しretryを発生させていることが確認できた(8節)

## 10. 改善が必要な場合の候補

今回はEFFECTIVE判定のため大規模な改善は不要と判断するが、軽微な観察事項
として記録する。

- 5-8(真の固有名詞違い)は分類層(`classify_asr_match`)では区別されず、
  安全性はCascade+Human Reviewという上位層に依存している。これは
  「orthographic uncertaintyと真の誤りをASR段階で区別する必要はなく、
  最終的にHuman Reviewで正しく止まればよい」という現行設計の前提に
  沿っており、直ちに変更が必要とは判断しない。ただし、Cascade全段階が
  偶然canonicalと一致する誤字を返すような極端なケース(理論上のリスク、
  今回のfixtureでは再現していない)への追加の備えを検討する余地はある
- legacy `validate_asr_match()`(先頭6語prefixのみ)が現行Production
  call siteには残っていないことを確認したが、コード自体は削除されておらず、
  将来別の呼び出し元から誤って再利用されるリスクはゼロではない(現時点では
  対応不要と判断)

## 11. Productionコード変更有無

**なし。** 本タスクはAudit専用であり、English Validator・Japanese
Validator・Japanese segment分割・ASR provider・TTS model・Production
Writerのいずれも変更していない。

## 12. 新規API Cost

**$0**。新規TTS/ASR/LLM呼び出しは一切行っていない。5節のCascade実音声
確認は、同一セッション内で数時間前に実施済みの検証ログを再利用した
(そちらも当時のログでコスト計上済み、本タスクでの追加コストはゼロ)。

## 13. 残存Open Item

OPEN-60として、本Audit結果(English=EFFECTIVE、日本語=MATERIAL_VALIDATION_GAP
という非対称性)と、10節の軽微な観察事項を記録する。

## 非対象

English Validator修正、Japanese Validator修正、Japanese segment分割変更、
ASR provider変更、TTS model変更、No.7生成、新規Research、Production Writer
変更、いずれも実施していない。

Audit完了につきSTOPする。
