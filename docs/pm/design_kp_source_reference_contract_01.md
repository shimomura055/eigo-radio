# 設計レビュー: Key Phrase `source_sentence`/`source_span` の
# Sentence ID方式(ハイブリッド参照契約)への移行可否

管理ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06
Phase A(設計レビューのみ、¥0・API呼び出しなし・コード変更なし・SSOT編集なし)
作成: Sonnet 5、2026-09-28

本書は事実(コード確認済み)と評価(Sonnetの判断)を明示的に分けて記述する。
「事実」は行番号・実測値で根拠を示し、「評価」は推測であることを明記する。

---

## 0. 前提事実(委任文の主張の裏付け)

**事実**: `KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05_REPORT.md` §3-3・
`er032_output/key_phrase_db_hybrid_core_v2_trial_05/x_twins_a2/
hybrid_core_v2_trial_result.json`を実際に確認した。twins_a2公式1回目は
選定itemの**5件全て**が`source_sentence`に外側の引用符を二重に付け足して
返し(例: `"\"Her digital twin appeared in the mirror\""`)、
`KEY_WORDS_STRUCTURE_INVALID`になった。原因はプロンプト側の表示書式に
ある:

- `er030_key_phrase_db_hybrid_selector_01.py:347`
  (`build_lightweight_user_message`)は
  `lines.append(f'{sid}: "{sentence_reference[sid]}"')` — 【SENTENCE
  REFERENCE】表で各文を`Sx: "text"`という**表示用の引用符**で囲んで
  提示している。
- 同ファイル188〜201行の`SELECTION_GUIDANCE`は「source_sentenceは
  必ず【SENTENCE REFERENCE】に列挙されている文をそのまま(一字一句、
  改変せず)使用してください」と明記しているが、この指示がむしろ
  「表示用の`"..."`込みでコピーする」ことを誘発しうる(実測でその通り
  発生した)。
- REPORT §3-3はさらに、`build_sentence_units`(Fix A、引用符を閉じた
  発話単位認識、`er030_key_phrase_db_hybrid_core_01.py:78-118`)が
  会話タグ境界(例: `wedding," he said`)で文の片側だけに引用符を残す
  ケースがあり、これが書式ゆらぎの土壌になっていると分析している
  (Sonnetもコードを確認し、108〜111行が先頭・末尾それぞれ1文字だけ
  引用符除去する実装であることを確認、内部の引用符は除去されない)。
- v1(`er030`、Family X Production)とv2(`er032`、Trial)は`build_sentence_
  units`/`attach_compact_context`を無変更のまま共有しているため
  (`er032_key_phrase_db_hybrid_core_v2_trial_05_stage1.py:594`に「無変更で
  再利用」と明記)、この脆弱性は**v1/v2共通**である(委任文の前提どおり)。
- 既にmax_attempts=1回勝負(`er030_key_phrase_db_hybrid_selector_01.py:470`
  `max_attempts=1`)であり、Production既定の`MAX_PRODUCTION_RETRY_ATTEMPTS
  =2`(`er003_key_words_production.py:159`)より再試行余地が少ない。

**評価**: 「再サンプルすれば通る」(REPORT §3-2の診断#2でtwins_a2はPASS)
は個々のjobには効くが、量産(数百〜数千記事)では低確率でも記事数に
比例して発生数が増える。根本原因がプロンプトの表示書式(引用符という
delimiter文字の二重利用)である以上、指示文言の追記だけでは構造的解決
にならない可能性が高い(既にSELECTION_GUIDANCEで「一字一句改変せず」を
明記済みでも発生している実測がこれを裏付ける)。

---

## 1. Sentence ID方式で失われる情報

**事実**: `source_sentence`/`source_span`の現在の消費先を全て確認した
(grep + 個別確認):
1. `er003_key_words_min_unit.py::validate_min_unit_selection`
   (429-438行): `source_sentence`がB2本文に実在するか、`source_span`が
   `source_sentence`内に実在するかの部分文字列一致チェックのみに使う。
2. `er003_key_words_canonicalization.py`(202-211行、354-406行):
   `qa_traceable_contiguous_span`判定で`key_phrase`が`source_span`の
   連続部分文字列(または1対1置換で説明可能)かを検証する材料としての
   み使う。
3. `er003_key_phrase_source_gate_01.py::check_key_phrase_source_presence`
   (66-118行): Assembly直前Gateで`source_span`(無ければ`source_sentence`)
   が現行本文に実在するかの部分文字列一致のみ。
4. `er011_key_phrase_set_redundancy_qa_01.py:116`: 5件相互の意味重複
   判定LLM呼び出しへ、`source_sentence`を**文脈情報としてそのまま
   プロンプトへ渡している**(意味比較の材料)。
5. Player/音声側(`er003_b2_key_words.py::build_key_words_reading_copy`、
   415-430行)は**`display_phrase`と`ja_gloss`のみ**を使い、
   `source_sentence`/`source_span`は一切使わない(確認済み、音声には
   出ない)。

**評価**: 4つの消費先は全て「文字列としての値」だけを見ており、
「LLMが**その場で自由生成した**文字列であること」自体には依存していない。
Sentence ID→canonical text復元でも、復元後の文字列を同じ場所に代入
すれば①〜④は**無変更で動作する**(検証済みの事実に基づく評価、実装は
していない)。したがって「失われる情報」は実質的に無い。むしろ復元
テキストは常に100%正確(Stage 1が決定論的に生成した`sentence_units`
由来)であり、現状のLLMコピーより**忠実性が高い**(現状はコピー揺らぎで
不正確になり得るため)。

---

## 2. phraseが複数sentence/spanにまたがる場合

**事実**: 候補生成(`er030_key_phrase_db_hybrid_core_01.py`の
n-gram/multiword/rare-word抽出ロジック、および`_iter_unigram_occurrences`
296-354行)は、いずれも`sentence_units`の**1文単位のtoken列**内で
n-gramを構成しており、文をまたぐ候補は構造的に生成され得ない。
また`attach_compact_context`(`er028_key_phrase_db_hybrid_trial_03_
stage1.py:312-342`)は候補ごとに**最初に出現した文のsentence ID1個**
だけを`context_sentence_id`として付与する(複数文にまたがる参照は
存在しない)。

**評価**: 現行のSELECTION_GUIDANCE(「そのsource_sentence内に実際に
現れる形の一部分」)も暗に1文内完結を前提にしている。したがって
Sentence ID方式へ移行しても「複数文にまたがるphrase」という現行仕様が
サポートしていないケースを新たに制限するわけではない(既存の制約を
維持するだけ)。

---

## 3. `source_span`との関係(spanも"文字列コピー"問題を持つか)

**評価(要検討事項として明記)**: `source_span`は`source_sentence`より
短い(通常1〜数語)ため引用符二重ラップの実測発生率は低いと推測される
が、同種の書式ゆらぎ(大文字化・句読点混入等)のリスクは原理的に残る。
実際、Trial-05の実データ(twins_a2)を見ると`source_span`自体は
`"digital twin"`のように引用符なしで正しく返っており(引用符問題は
`source_sentence`側のみで発生)、`source_span`固有の脆弱性は本Trial-05の
実測範囲では確認されていない。ただし証拠件数が少なく(quote-heavy
記事2本のみ)、統計的に「span側は安全」と断定はできない。

代替案として検討した2方式:
- **(a) sentence内オフセット**(start/end文字位置)で返させる: 復元は
  `sentence_reference[sid][start:end]`。LLMに数値を正確にカウントさせる
  ことになり、実際にはオフセットの数え間違いという**別の脆弱性**を
  導入するリスクがある(文字数を正確に数えるのはLLMが不得意な作業の
  一つであり、経験的にオフセット系の指示はテキストコピーより脆弱な
  ことが多い、と評価する。実測データはない)。
- **(b) 候補ID方式**(shortlist候補の`surface_form`をそのまま使う):
  `attach_compact_context`が既に各候補へ`context_sentence_id`を
  付与しており(§0参照)、`surface_form`はStage 1のn-gram抽出時点で
  **既に本文からの実測トークン列として決定済み**(`format_candidate_
  line`が表示するのと同じ値)。つまり候補ID方式なら`source_span`も
  LLMに一切書かせず、候補データから決定論的に復元できる。

**推奨**: (b)候補ID方式は`source_sentence`だけでなく`source_span`の
書式ゆらぎリスクも同時に消せる(§13の比較表・推奨案参照)。

---

## 4. quote-heavy dialogue・sentence segmentation(v1/v2差)

**事実**: `build_sentence_units`(§0参照)はv1/v2で完全に同一実装。
sentence IDは`attach_compact_context`が「そのプロンプト呼び出し内で
提示したSENTENCE REFERENCE表」に対して`S{idx+1}`という連番を**都度
再計算**する(`sentence_units`のindexに基づく、47-118行のbuild_sentence_
unitsの出力順)。つまりIDは記事×Stage1実行1回に閉じたローカルな
参照であり、他記事・他runとの間でID体系を共有する設計にはなっていない
(article_textが同一ならshortlist_cacheキー[sha256、S8]により同じ
IDマッピングが再利用される、`er030_key_phrase_db_hybrid_selector_01.py:
357-359,421-432`で確認済み)。

**評価**: 「その呼び出しで提示した表に対して閉じる」設計で問題ない。
retry(§9)・debug再現性は、`db_hybrid_stage1_debug.json`
(`_serializable_stage1`、439-440行)と`keywords_selector_prompt.txt`
(461-462行)が既に呼び出し単位でファイル保存されているため、ID→文の
対応は事後にも人間が追跡できる(現状のまま維持できる、追加実装不要)。

---

## 5. duplicate/similar sentence(同一文が2回出る場合)

**事実**: `build_sentence_units`はsentence_unitsを**出現順の連番**で
生成するため(コンテンツの一意性を要求しない)、同一文言が記事中に
2回現れても異なるIDが振られる(S12とS47等)。IDの一意性自体は保証
される(indexベースのため)。

**評価**: 復元時は`sentence_reference[sid]`が指す具体的な出現位置の
文字列を使うため、Source Gate(`normalize_text`による部分文字列一致、
`er003_key_phrase_source_gate_01.py`)は「本文のどこかに存在するか」
だけを見ており出現位置を区別しない。したがって同一文が複数箇所にある
場合でも復元テキストは常に本文の**どこかの**実在文と一致するため、
Gate判定への悪影響はない(現状と同じ挙動)。

---

## 6. heading/fragment(見出し・断片)

**事実**: `build_sentence_units`(89-93行)は見出し行(`#`始まり)を
`blocks`へ独立した1ブロックとして追加し、その後同じ文分割処理を通す。
見出しテキストは"#"記号を除去した状態で`sentence_units`に入る。

**評価**: 見出しがcandidateのcontext_sentence_idとして選ばれるケースは
理論上あり得る(見出し内にphrase候補が出現すれば)。復元テキストには
"#"が含まれないが、`_normalize_for_match`/`normalize_text`は空白の
正規化のみで"#"除去は行わないため、`normalized_sentence in
normalized_raw_article`の判定は「見出し行の"# "の後に続くテキストが
部分文字列として存在するか」になり、これは元々"#"を除いたテキストの
部分文字列一致なので**引き続き成立する**(現状の文字列コピー方式でも
同じ理屈で通っていたはずであり、ID方式によって新たに壊れる要素は
ない)。

---

## 7. multiword expression・pronoun normalization

**事実**: `pronoun_placeholder_rescue`(Trial-05で確認、例:
`his place`→Wiktionary`one's place`相当のidiom一致)は**候補生成
段階**で発生し、candidateの`surface_form`/`source_span`は**本文中の
実際の代名詞形(his等)のまま**保持される(正規化された`someone's`
形はcanonicalization段階=選定gateの**後工程**で生成される、
`er003_key_words_canonicalization.py`の`generalize_person_dependent_
reference`カテゴリ、CURRENT_SPEC 1463行に記載の既存仕様)。

**評価**: 候補ID方式は「候補が本文中でどの実際の形で出現したか」
(=`surface_form`、代名詞そのまま)をそのまま復元するだけであり、
display_phraseの一般化(person reference generalization)は選定gateの
後で走る既存canonicalizationの責務のまま変わらない。責務分離を壊さない。

---

## 8. 既存validatorとの整合(Production validator変更が必要か)

**事実**: `parse_selector_json`(`er003_key_words_min_unit.py:472-481`)
は`items`キーの存在しかチェックしないschema非依存の汎用関数であり、
`validate_min_unit_selection`(`p2g`)/`validate_production_selection`
(`prod`)は「渡された`parsed_with_metadata`の`items`各要素が持つ
文字列フィールドの値」だけを見て判定する(値がLLMの直接出力か、
プログラムが代入した値かを区別する実装は一切ない)。

**評価**: 新しいTrial layer(wrapper)が、LLM応答をparseした直後・
validator呼び出し前に、各itemへ`source_sentence`(と候補ID方式を
採る場合は`source_span`も)を`sentence_reference`/candidate情報から
決定論的に上書き・追記してから、既存の`p2g.validate_min_unit_
selection`(またはer003_key_words_production経由)へそのまま渡せば、
**Production validatorは一切変更不要**である(事実に基づく結論、
実装はしていない)。ただし、この場合`run_production_selection_gate`
(`er003_key_words_production.py:162-220`)自体は「parse直後に
validateする」という一体型の関数であり、間に復元ステップを挟む
フックがない。したがって既存`run_production_selection_gate`を
そのまま呼ぶことはできず、**同等の薄いgateループをTrial層に新規実装**
する必要がある(validatorそのものは再利用、gateのオーケストレーション
関数だけ新規、既存Production関数の改変はゼロ)。

---

## 9. retry/fallback整合

**事実**: `shortlist_cache`(S8、421-432行)はarticle_textのsha256を
キーに`s1r`(stage1+shortlist_info、`sentence_reference`を含む)を
保持し、Key Phrase Set Redundancy QA retry時も**同じキャッシュ済み
shortlist**(=同じsentence_reference/同じID体系)を再利用する設計に
既になっている。したがってID方式でも「retry時にID体系が変わって
しまう」リスクは無い(既存のキャッシュ機構がそのまま担保する)。
Fallback(Strategy L全文方式、`er003_v1_n3_01_scaffold_generate.
_run_key_phrase_selection_strategy_l`相当)は本文全体をpromptへ送る
既存の別contractであり、`source_sentence`はLLMが本文から自由コピー
する現行仕様のまま変わらない(ID方式はDB Hybrid経路にのみ導入する
想定であり、fallback経路との契約混在は「Primary=ID参照/Fallback=
自由テキスト」という**現状のPrimary/Fallback構成と同型**になる。
validatorが値の出自を区別しないため、混在自体は技術的に問題ない)。

---

## 10. backward compatibility・artifact/schema影響

**評価**: `keywords_canonicalized.json`等の既存artifactは、復元後の
`source_sentence`(通常の正しい文字列)をそのまま保存すれば下流
(canonicalization/Redundancy QA/Source Gate/reading copy)は無変更で
動作する(§1で確認済みの消費先分析に基づく)。追加で`source_sentence_id`
(またはcandidate ID)を**新規フィールド**としてartifactへ保持しておけば、
監査時に「このsource_sentenceがどのID由来か」を後から追跡できる
(既存フィールドの意味は変えず追加するだけなので、既存の`_ITEM_SCHEMA_
PROPERTIES`ベースの下流コードに影響しない)。

---

## 11. migration方法

**評価**: 新方式は新規Trial module(er034相当)にのみ実装し、既存
artifact(v1 Production運用中の記事群)は一切re-processしない。
v1 Production(`er030`)への適用は、本Trial-06の検証結果を踏まえて
Fable/ユーザーが別途判断する完全に独立した意思決定(本Phaseの
スコープ外、委任文にも明記されている)。

---

## 12. 新たなfalse accept/false reject

**事実**: 既存schema(`_ITEM_SCHEMA_PROPERTIES`、115-134行)は
`phrase_type`/`normalization_type`/`inference_transparency`等**複数の
enumフィールドを既にJSON Schema strict modeで使用しており**
(`"enum": list(PHRASE_TYPES)`等)、OpenAI Structured Outputsの
enum制約自体は既にProductionで稼働実績がある(新しい技術リスクでは
ない)。Sentence ID/候補IDのenum値数は1記事あたりshortlist総数
(実測20〜25件、Trial-04/05実測)程度であり、既存enumフィールドの
値数(PHRASE_TYPES=7、TRI_LEVELS=3等)より一桁多い程度に留まる。

**評価**:
- **false reject(構造的に防げる)**: 存在しないIDをenumで拒否できる
  ため、モデルが「Sxx」を捏造するケースは**Structured Outputsの
  スキーマレベルで構造的に発生しなくなる**(現状のfree-text方式では
  「本文に実在しない文字列」を返すこと自体は技術的に可能で、これが
  今回のINVALIDの直接原因だった)。
- **new false accept(要警戒)**: IDは実在するが、モデルが**意図と
  異なる候補ID**を選んでしまうケース(取り違え)は、schema上は
  「有効な応答」としてPASSしてしまう可能性がある。ただし:
  (a) 候補ID方式(§3(b))を採れば、選んだ候補のsurface_form/
  source_sentenceは常に「実在する何らかの正しい候補」に対応するため、
  最悪でも「別の実在候補を選んでしまった」という**選定ミス**に留まり、
  「架空の文字列を主張する」という現状の失敗モードより実害は小さい。
  (b) 下流のcanonicalization`qa_traceable_contiguous_span`
  (既存Production、無変更)が、display_phraseと(復元された)
  source_spanの整合性を引き続きチェックするため、明らかな取り違え
  (display_phraseと無関係なsource_span)は既存の安全網でも一定程度
  検出され得る(完全ではない、既存の限界と同水準)。
  (c) 取り違えの実際の発生率は本Phase(設計レビューのみ)では未計測
  であり、Trial実装段階での実データ確認が必要(推測にとどめる)。

---

## 13. 代替案比較表

| 案 | 書式揺らぎ耐性 | 情報損失 | validator変更範囲 | 実装コスト | false accept/reject | v1/v2適用容易性 |
|---|---|---|---|---|---|---|
| (i) Sentence ID + span文字列(span は引き続きLLMが自由記述) | source_sentence側は解消、source_span側は未解決のまま残る(§3) | なし | 無変更(§8) | 中(新規schema+新規gate関数) | span取り違えrisk小さいまま残存 | 容易(sentence_reference既存流用) |
| (ii) Sentence ID + sentence内文字オフセット | 新たな脆弱性(オフセットの数え間違い)を導入しうる(§3評価) | なし(理論上) | 無変更 | 中〜高(オフセット検証ロジック新設) | オフセット外れ値によるfalse reject増加を懸念 | 容易だが検証が必要 |
| (iii) **候補ID方式**(shortlistの候補IDのみ返させ、source_sentence/source_spanともに一切LLMに書かせない) | **最も高い**(source_sentence/source_span双方の書式揺らぎを構造的に排除、§0・§3) | なし(§1で確認済み、消費先は文字列値のみ参照) | 無変更(§8) | 中(新規schema+新規gate関数、candidate ID付与はattach_compact_contextに1行追加相当と推定) | 取り違えrisk残るが実害は「別の実在候補」に留まる(§12) | 容易(context_sentence_id/surface_formが既にStage1で決定済み) |
| (iv) 現行+正規化強化(validator側で引用符等を寛容化) | 限定的(既知の書式=表示delimiterの引用符には対応できるが、未知の新しい書式揺らぎには対応できない、モグラ叩きになるリスク) | なし | **Production validator変更が必要**(`_normalize_for_match`等の改修、影響範囲が全Family共通の既存Production関数に及ぶ) | 低(一見)だが将来の再発防止という観点では最も弱い | 揺らぎパターンを網羅できなければfalse rejectが残り続ける | 容易だがProduction本体改修を伴う |

**評価の要点**: (iv)は最速だが「そもそもLLMにcanonical sentenceを
再生成/再コピーさせる必要があるか」というユーザーの問題提起に答えて
いない対症療法であり、かつ**唯一Production validator本体の改修**を
要する(他案は全てTrial層のwrapperで完結)。(i)/(ii)は`source_sentence`
のみを対象にしており`source_span`の同種リスクを未解決のまま残す。
(iii)が「量産時に書式揺らぎでSTOPしないこと」という最優先評価軸に
対し最も構造的に効き、かつProduction資産(validator/canonicalization/
Source Gate)を一切変更せずに実現できる。

---

## 14. Fableへの推奨案

**推奨: (iii)候補ID方式(改良版)、比較表でのB相当**

理由:
1. `source_sentence`/`source_span`双方の書式揺らぎを、LLMに一切
   「本文文字列を書かせない」ことで構造的に排除できる(§0の実測
   root causeに直接効く)。
2. 復元される文字列は常にStage 1が決定論的に生成した実在テキスト
   そのものであり、`_verify_source_spans_against_raw_article`
   (`er030_key_phrase_db_hybrid_selector_01.py:362-382`、Opus L2
   所見S3で追加された既存Gate)は理論上**恒常的にPASS**する
   (この失敗モード自体が構造的に解消される、実データでの確認は
   Trial実装段階で必要)。
3. 既存Production validator(`p2g.validate_min_unit_selection`)・
   canonicalization(Rule 7 `qa_traceable_contiguous_span`)・
   Source Consistency Gate(`er003_key_phrase_source_gate_01`)は
   **一切変更不要**(§1・§8で確認済み)。
4. schema enum制約はOpenAI Structured Outputsで既にProduction実績が
   ある技術(§12)であり、新規リスクの持ち込みではない。

Trial実装の最小範囲(本Phaseでは未実装、次Phaseの提案):
- 新規`er034_key_phrase_db_hybrid_source_reference_contract_trial_06_*`
  として、v1(`er029`)/v2(`er032`)のいずれの選定層もラップする
  薄い層を追加する。Production `er030`・v1 baseline(`er029`)・
  Production validator(`p2g`/`prod`)はいずれも無変更のまま。
- 新規schema: 既存`_ITEM_SCHEMA_PROPERTIES`から`source_span`/
  `source_sentence`を除去し、代わりに`source_candidate_id`
  (enum、当該呼び出しのshortlist候補IDのみ許可)を追加した派生
  schemaをTrial層で定義する(既存p2g/prodのschema定義自体は変更しない、
  コピーして差分適用)。
- `attach_compact_context`相当の処理に、候補ごとの一意な
  `candidate_id`(例: `C1`, `C2`...)を付与する軽量拡張をTrial層で
  追加する(既存`er028_key_phrase_db_hybrid_trial_03_stage1.
  attach_compact_context`は無変更のまま、Trial wrapper側で戻り値に
  ラップして付与する想定)。
- gate関数: `parse_selector_json`(既存、無変更)→
  candidate_id解決(新規、Trial層)→`source_sentence`/`source_span`を
  candidate情報から代入(新規、Trial層)→`p2g.validate_min_unit_
  selection`(既存、無変更)、という順に呼ぶ薄いオーケストレーション
  関数を新設する。

検証計画(次Phase以降、ユーザー承認後):
- 対象: twins A2・Melos A2(quote-heavy、既知の失敗事例)+ Family X
  12本文(既存回帰確認用)。
- 1本文1 call厳守、article全文非送信の既存原則を維持
  (`assert_no_full_article_body`を流用)。
- 反復安定性(同一本文で複数回サンプルしてもstructural INVALIDが
  発生しないこと)は、構造修正(enum制約)後に**複数サンプルでの実測**
  が必要(1回のPASSだけでは「たまたま」の可能性を排除できない、
  Trial-05 REPORT §3-3が指摘した「単発サンプルの限界」と同じ教訓)。
- cost: 既存DB Hybridと同等(prompt構成はSENTENCE REFERENCE表を
  candidate ID表に置き換えるだけで、article全文は元々含まないため
  token数は同等〜微減と推定)。

受入条件との対応: 「量産時に書式揺らぎでSTOPしないこと」という
最優先評価軸に対し、(iii)は根本原因(LLMによる本文文字列の自由
コピー)そのものを除去する設計であり、他案より高い達成見込みと
評価する(実装・実測は次Phase)。

**STOP条件該当の有無**: 本Phase(設計レビューのみ)ではSTOP対象の
事象は発生していない。Trial実装(次Phase)を開始する場合は、新規
コード追加・API呼び出しを伴うため、通常のPM Governanceループ上限
(Sonnet委任1管理IDあたり初回+3回)の対象になる想定である。

---

## 付記: 未確定・要ユーザー判断の論点(USER_DECISION_REQUIRED候補)

- (iii)採用の場合、`display_phrase`の自由記述性(lemma化等の
  normalization_type)は維持されるが、「モデルが誤った候補IDを選ぶ
  (取り違え)」という新しい失敗モードの実害率は未計測(§12(c))。
  Trial実装時に実データで計測すべき。
- v1 Production(`er030`)への適用可否・タイミングは、本Trial-06が
  Sentence/候補ID方式の実データ検証(次Phase)で十分な安定性を示した
  後に、Fable/ユーザーが別途判断する(本Phaseでは提案のみ、判断も
  実装もしていない)。
- (iv)(validator側の正規化強化)を(iii)と**併用**するか(表示用引用符
  程度は最後の安全網として`_normalize_for_match`が吸収できるようにする)
  は、Production validator改修を伴うため、これも別途ユーザー判断が
  必要な論点として明記しておく(本書は(iii)単独での構造的解決を推奨
  するが、多層防御として(iv)の軽微な追加を妨げるものではない)。
