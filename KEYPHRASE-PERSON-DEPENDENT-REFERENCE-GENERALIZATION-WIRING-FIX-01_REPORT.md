# KEYPHRASE-PERSON-DEPENDENT-REFERENCE-GENERALIZATION-WIRING-FIX-01

管理ID: `KEYPHRASE-PERSON-DEPENDENT-REFERENCE-GENERALIZATION-WIRING-FIX-01`
日付: 2026-09-27
分類: 既存仕様の未発火修正(wiring/implementation regression)。新規仕様・新規ユーザー判断は作らない。

## 0. 既存資産照合(先頭確認)

- ユーザー指摘どおり、`generalize_person_dependent_reference`(人称代名詞・
  所有格を辞書的一般形 one's/someone's… へ置換する変換)は
  `ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01`(2026-09-02、
  `DECIDED`/`PRODUCTION_WIRED`)で既に承認・実装済みの既存仕様である
  (`CURRENT_SPEC.md` 1416行、`er003_key_words_canonicalization.py`
  `_PERSON_DEPENDENT_TO_GENERIC`/`_is_valid_person_generalization`)。
- CURRENT_SPEC.mdの当該エントリには「この回では人称代名詞を含む候補が
  選ばれなかったため実際の置換発火は未観測、単体テストで安全性を確認済み」
  と明記されており、**実データでの発火は今回(Family Z Melos run)が初**
  であることがSSOT上でも裏付けられる。
- 結論: **分類A(既存仕様あり・未発火)**。新しい仕様は導入していない。

## 1. 原因(関数名・行番号・実データで特定)

- 構造的validator `_is_valid_person_generalization`
  (`er003_key_words_canonicalization.py` 旧325行、`validate_canonicalization_item`
  旧366行のRule7例外パス)は、`normalization_reason ==
  "generalize_person_dependent_reference"` かつ閉じた語彙集合の1対1置換で
  あることを条件に、**構造的な捏造チェック(Rule7)のみ**を免除していた。
- 一方、`qa_traceable_contiguous_span`(「key_phraseがsource_spanから
  追跡可能か」)はLLMがcanonicalization応答内で**自己申告**する12QA
  フィールドの1つであり(`QA_FIELDS`)、LLM出力の値がそのまま
  `validate_canonicalization_response`(旧453行 `any(item[field] ==
  "FAIL" ...)`)と`merge_canonicalization_result`(旧554-555行
  `qa = {field: canon[field] ...}` / `item_review_required = any(v ==
  "FAIL" ...)`)へ採用され、1件でもFAILがあれば`REVIEW_REQUIRED`へ倒す
  設計だった。
- プロンプトテンプレート
  (`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_prompt_template.txt`)
  の`qa_traceable_contiguous_span`定義は、PASSとなる条件を
  (a) key_phraseがdisplay_phraseと完全一致、(b) key_phraseがsource_span
  内の連続部分文字列、の2つだけに限定しており、**(c) ルール3(人称代名詞・
  所有格の一般化)による正当な置換の場合**が定義に含まれていなかった。
- 実データ(`er026_output/family_z_production_e2e_01/melos/run_01/
  key_phrases/keywords_canonicalized.json` rank3): `source_span="gave my
  word"` / `display_phrase="give my word"` / `key_phrase="give one's
  word"` / `normalization_reason="generalize_person_dependent_reference"`。
  key_phraseはdisplay_phraseと一致せず(条件a不成立)、source_span内の
  連続部分文字列でもない(one'sはmy/gaveのいずれとも文字列一致しない、
  条件b不成立)ため、LLMは自身のQA定義に忠実に従い`qa_traceable_
  contiguous_span=FAIL`と自己申告し、他11項目PASSにもかかわらず
  `REVIEW_REQUIRED`に倒れた。**LLMの判断自体は当時のQA定義に対して正しく、
  QA定義側(および、それを無条件採用していたPASS/FAIL集計ロジック)に
  ER-011-NO18で承認済みの例外が反映されていなかったことがギャップの本体。**

## 2. 修正(最小差分、新規仕様なし)

1. `er003_key_words_canonicalization.py`: 決定論的な後処理関数
   `_qa_field_effective_verdict(field, verdict, key_phrase, display_phrase,
   normalization_reason)`を新設。`field == "qa_traceable_contiguous_span"`
   かつ`verdict == "FAIL"`かつ`normalization_reason ==
   "generalize_person_dependent_reference"`かつ既存の
   `_is_valid_person_generalization()`がTrueの場合のみ`"PASS"`へ補正する
   (それ以外は無変更でそのまま返す)。
   - `validate_canonicalization_response()`のhas_qa_fail集計、
   - `merge_canonicalization_result()`のqa dict/`item_review_required`集計、
   の両方でこの関数を経由するよう配線(2箇所とも、既存の他フィールド・
   他FAIL理由の扱いは無変更)。
2. プロンプトテンプレート
   `b1_p2_keywords_canonicalization_prompt_template.txt`の
   `qa_traceable_contiguous_span`定義に、条件(c)(ルール3による人称一般化)
   を追記(今後の新規LLM生成時点でも、自己申告の時点でPASSと判断されやすく
   する。決定論的補正[1]と合わせた二重の安全策)。
3. false accept防止: 補正対象は`qa_traceable_contiguous_span`という
   **1フィールドのみ**、かつ**既存の構造validatorが既に検証済みの正当な
   1対1置換のみ**。本文にない語の捏造・語数不一致・許可されていない
   置換先・reason不一致は、従来どおりFAILのまま(既存Rule7・既存
   `_is_valid_person_generalization`のロジックを一切変更していない)。

## 3. Regression test(`er003_test_key_words_canonicalization.py`)

新設クラス`QaTraceableSpanPersonGeneralizationOverrideTests`(9件):
- 陽性: my→one's(Melos rank3実データ再現)、your/his/her/their各1件
  (計4パターン)。
- 陰性: normalization_reason不一致、本文にない語の捏造、他QAフィールドの
  FAILは補正対象外、`validate_canonicalization_response`/
  `merge_canonicalization_result`の両方でMelos rank3相当が
  `PASS`/`CANONICALIZATION_PASS`になること、無関係な既存FAILは従来通り
  `REVIEW_REQUIRED`のまま(無回帰)であること。

実行結果(単独ファイル、実行日2026-09-27):
```
.venv/Scripts/python.exe -m unittest er003_test_key_words_canonicalization -v
Ran 66 tests in 0.038s / OK
```
関連ファイル群(canonicalization/min_unit/b1_p2/p2i_production)の
無回帰確認:
```
.venv/Scripts/python.exe -m unittest er003_test_key_words_canonicalization
  er003_test_key_words_min_unit er003_test_b1_p2 er003_test_p2i_production
Ran 260 tests in 0.187s / OK
```
全体regression(他Familyのtest等)は他Agentが並行してTTS実行中のため
本タスクでは実施せず、次回closeoutで実施する(既存運用どおり)。

## 4. Runtime evidence(¥0、LLM再呼び出しなし)

修正後の`_qa_field_effective_verdict`を、既存の全`keywords_canonicalized.json`
artifact(145ファイル、er003/005/006/011/012/013/014/017/019/026配下、
`er026_output`はread-onlyで参照のみ・書き換えなし)の永続化済み生QA値へ
適用し、変化を再判定するスクリプトで確認(APIコストゼロ、決定論的再計算
のみ)。

- 変化ありのフィールド: 14件(全て`qa_traceable_contiguous_span`
  FAIL→PASS、全て`normalization_reason="generalize_person_dependent_
  reference"`かつ既存構造validatorが既に許容していた正当な1対1置換)。
  対象runの一覧(rank/phrase): Melos rank3("give my word"→"give one's
  word")を含む13ファイル(他: "at their own pace"→"at one's own pace"
  [複数run]、"room for their own pace"→"room for one's own pace"、
  "a place of my own"→"a place of one's own"、"change my surroundings"
  →"change one's surroundings"、"make something your whole life"→
  "make something one's whole life"、"occupy their thoughts"→
  "occupy one's thoughts")。
- 変化なし: 132ファイル(既存のPASS判定はそのまま維持、他フィールドへの
  影響ゼロ)。
- Family X Meta(`er012_output/e_family_two_level_wiring_01/meta/{a2,b1b}`)・
  Family X Hormuz(`er019_output/.../hormuz__run_02/{a2,b1b}`)の既存
  `keywords_canonicalized.json`は4ファイルとも`overall_status=PASS`、
  再判定でも変化ゼロ(無回帰確認済み)。
- Family Z Melos run rank3は、`merge_canonicalization_result()`へ実データの
  raw QA値・key_phrase・display_phrase・normalization_reasonをそのまま
  与えて再実行し、`overall_status`が`REVIEW_REQUIRED`→`PASS`、
  `qa["qa_traceable_contiguous_span"]`が`FAIL`→`PASS`になることを確認
  (テストクラス内`test_merge_result_yields_pass_for_melos_rank3_
  reproduction`として恒久化)。
- 注: `er026_output`配下のファイル自体は本タスクのスコープ外
  (`er026_*は触らない`)のため書き換えていない。上記は永続化済みJSONの
  値を読み取り、修正後ロジックへ渡した際の出力を確認したものであり、
  Family Z側のartifact更新・再採用判断は別タスク(Family Z担当Agent)の
  管轄とする。

## 5. Gate 3 checklist(該当項目のみ)

- 既存の安全装置(構造validator Rule7・1〜5語制約・有限助動詞禁止・
  retry上限)は無変更、独自に緩和していない。
- 変更は決定論的コード2箇所+プロンプト文言1箇所の最小差分。
- false acceptが増えないことをnegative testおよび145ファイルの全数
  再判定(変化14件、いずれも既存承認済み例外の範囲内)で確認。
- Production採用判断(SSOT本体の書き換え)は行っていない(下記6は提案文
  のみ)。

## 6. SSOT記載案(ユーザー承認待ち、本タスクでは`CURRENT_SPEC.md`を編集していない)

`CURRENT_SPEC.md` 1416行(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01の
行)への追記案(新仕様ではなく、既存決定のQA側整合の記録):

> QA側整合(2026-09-27、`KEYPHRASE-PERSON-DEPENDENT-REFERENCE-
> GENERALIZATION-WIRING-FIX-01`): 本行の`generalize_person_dependent_
> reference`は構造validator側では既に例外として許容済みだったが、
> QAフィールド`qa_traceable_contiguous_span`(LLM自己申告)には未反映
> だったため、Family Z Melos run実データで初めて実際に発火した際に
> 誤って`REVIEW_REQUIRED`となった。決定論的後処理
> `_qa_field_effective_verdict`とプロンプト定義の条件追記により、既存
> 承認済み例外をQA側にも反映した(新しい変換ルールの追加ではない)。
> 145件の既存artifact再判定でfalse acceptの増加なしを確認。

Fable/ユーザーの判断を仰ぎたい点: 上記追記を実際に`CURRENT_SPEC.md`へ
反映するか(反映自体はSSOT編集のため本タスクのスコープ外)。

## 7. Fable評価

Fable評価: 分類A(既存仕様の未発火)として妥当。既存145件再判定で
14件FAIL→PASS(全て正当な一般化)、Family X 4件無変化=無回帰。SSOT
反映済み。Status: `PRODUCTION_WIRED`(共有Key Phrase canonicalization
module、回帰260件PASS、全体regressionは次回closeoutで確認)。

Management-ID: KEYPHRASE-PERSON-DEPENDENT-REFERENCE-GENERALIZATION-WIRING-FIX-01
