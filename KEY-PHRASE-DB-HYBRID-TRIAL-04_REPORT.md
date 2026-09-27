# KEY-PHRASE-DB-HYBRID-TRIAL-04 — sentence segmentation一般化修正(Fix A)+
# rare/technical single word候補生成一般化修正(Fix B)、12本文再評価結果

管理ID: KEY-PHRASE-DB-HYBRID-TRIAL-04(Trial。到達可能Status=`REJECTED`/
`VALIDATED`/`USER_DECISION_REQUIRED`。**Production配線・
`APPROVED_FOR_PRODUCTION`化は行っていない。**)

新規ファイル: `er029_key_phrase_db_hybrid_trial_04_stage1.py`(Fix A/Bの
実装本体)、`er029_key_phrase_db_hybrid_trial_04_run.py`(12本文
orchestration)、`er029_key_phrase_db_hybrid_trial_04_test.py`(unit test、
18件・全PASS)。出力: `er029_output/key_phrase_db_hybrid_trial_04/`。

`er023_*`/`er027_*`/`er028_*`(Trial-01〜03資産)・`er003_key_words_*`・
`er003_b1_p2_keywords.py`は**すべてimport/読み取りのみ、無変更**(Trial-03の
再現性を保つ)。

---

## 0. 既存資産照合(Existing Spec / Prior Trial Check Gate、A/B/C分類)

| 論点 | 分類 | 根拠 |
|---|---|---|
| twins_a2のsentence segmentation起因INVALID | **B(過去Trialで既知、未修正)** | `KEY-PHRASE-DB-HYBRID-TRIAL-03_REPORT.md` §15-3で発見・記録済み、「本runでは修正していない」と明記されていた。本Trialが修正対象。 |
| wake_a2のrare single word機械screening漏れ | **B(過去Trialで既知、未修正)** | 同REPORT §15-4・§15-7で発見・記録済み、「新しいDBが必要」と要検討フラグが立っていた。本Trialが既存DB範囲内での修正を試みる対象。 |
| 会話タグ(Echo said等)のfalse positive | **B(過去Trialで既知、観測のみ)** | 同REPORT §15-5で発見済み、「実害なし、修正は行っていない」と明記。本Trialでもスコープ外として観測のみ継続(§4参照)。 |
| Wiktionary multiword lookupの`Category:English multiword terms`限定 | **A(既存仕様、min_n=2,3固定)** | `er027_key_phrase_db_hybrid_trial_02_stage1.select_unmatched_ngram_candidates_for_lookup`が明示的に`min_n=2, max_n=3`。1-gram拡張は新規実装が必要(本Trialで対応)。 |
| `_SENTENCE_SPLIT_RE`(`er023_key_phrase_db_extraction`)の文分割規則 | **A(既存仕様、終端句読点+空白/文末のみ)** | 個別記事向けの特別処理ではなく、全記事に一律適用される既存の一般ルール。本Trialはこの既存ルールの一般化拡張を新規ファイル側で行う(er023自体は無変更)。 |

---

## 1. Fix A: 会話文のsentence segmentation一般化修正

### 1-1. 根本原因

既存`er023_key_phrase_db_extraction._SENTENCE_SPLIT_RE`
(`[.!?]+(?=\s|$)`)は、終端句読点の直後に閉じ引用符が続く場合(例:
`"You asked me to wake you." "I did not."`)に分割できない。理由:
正規表現の肯定先読み`(?=\s|$)`が「句読点の直後が空白または文末」を
要求するが、閉じ引用符が句読点と空白の間に挟まると先読みが不成立になる。

実データ(twins_a2、Trial-03 §15-3): 4つの独立した発話文
(`"You asked me to wake you."` / `"I did not."` /
`"You did not remember asking."` / `Mara sat up.`)が、最後の
`Mara sat up.`(閉じ引用符を伴わない、既存規則でも分割可能な境界)まで
一切分割されず1個のsentence unitへ結合されていた。これがStrategy Lへの
SENTENCE REFERENCE(`S6: ""You asked...Mara sat up"`、二重引用符表示)と
なり、`validate_min_unit_selection`の「本文実在1文」判定に失敗した
(`KEY_WORDS_STRUCTURE_INVALID`)。

### 1-2. 修正内容(一般化、個別作品hardcodeなし)

`er029_key_phrase_db_hybrid_trial_04_stage1.QUOTE_AWARE_SENTENCE_SPLIT_RE`
(`[.!?]+[)\]"']{0,2}(?=\s|$)`)を新設し、終端句読点の直後に閉じ引用符・
閉じ括弧が0〜2文字続く境界も分割対象に含めた(英語の一般的な約物規則、
"X said." のような会話タグ文も引き続き独立文として扱われる)。分割後、
各sentence unitの先頭・末尾に残る単独の引用符(発話境界の片割れ)は
1文字だけ取り除く(SENTENCE REFERENCEテーブル表示の二重引用符化を防ぐ、
`validate_min_unit_selection`のsubstring照合[空白正規化・小文字化のみ]
には影響しない)。

`build_sentence_units_v4`として実装し、`run_stage1_for_article_v4`から
呼び出す。`er023`/`er027`/`er028`は無変更。

### 1-3. 修正確認(実データ、実LLM実行)

修正後、twins_a2のsentence unitは`"You asked me to wake you"` /
`"I did not"` / `"You did not remember asking"` / `"Mara sat up"`の
4つの独立したunitへ正しく分割された(unit test
`FixASentenceSegmentationQuoteAwareTests`5件で固定回帰化)。実LLM実行の
結果、twins_a2は**`KEY_WORDS_STRUCTURE_PASS`**に変わり(Trial-03は
`KEY_WORDS_STRUCTURE_INVALID`)、最終5件に`sit up`
(`source_span: "sat up"`, `source_sentence: "Mara sat up"`)が選定され、
validatorをそのまま(無変更)通過した(§13の実行ログ・JSON参照)。

通常の平叙文(会話を含まない記事、meta/hormuz/small_bag/wake/aihiring)の
sentence分割結果は、修正前後で実質的に同一であることを確認した(§4の
shortlist件数・bug再発チェック参照)。

---

## 2. Fix B: rare / technical single word候補生成一般化修正

### 2-1. 根本原因

`run_stage1_for_article_v3`(er028)は、n-gram候補が群1DB
(CEFR-J/NGSL/Wiktionary idiom系)のいずれにも一致しない場合
(`db_match_count==0`)、1-gram(単語1個)であっても無条件に候補から
除外していた。"grogginess"/"self-awakening"はCEFR-J/NGSL/Wiktionary
idiom系のいずれにも該当せず(実データ確認、§13)、機械screening段階で
完全に消えていた(Trial-03 §15-4、wake_a2で既存Production公開Key
Phrase5件中0件しか一致しなかった実害)。

### 2-2. まず試みたアプローチ(ユーザー指示どおり)とその限界

ユーザー指示どおり、まず`select_unmatched_ngram_candidates_for_lookup`の
min_n=1拡張に相当する経路(Wiktionary `Category:English lemmas`所属
確認による1-gram lookup、`wiktionary_unigram_lemma_lookup`)を実装した。
実データ確認(2026-09-27、実際のMediaWiki API呼び出し):

- "grogginess": `Category:English lemmas`に所属するページが存在 → 回収可能。
- "self-awakening": ページ自体が存在しない(`missing`) → **この経路だけでは回収不能**。

Wiktionary(英語版)は複合語として定着していない専門的な派生表現
(self-awakening等)を必ずしも見出し語化していないため、Wiktionary
lookup単体を「候補生成の唯一のゲート」にすると、ユーザーが例示した
fixture例自体を回収できない設計になってしまうことが実データで判明した。

### 2-3. 最終設計(既存DB範囲内、新DB不使用)

`find_repeated_compound_noun_candidates`(er027、複数語の重要名詞句を
DB一致なしでもwordfreq実在判定+CEFR-J品詞妥当性で拾う、既存の設計前例)
と同じ設計思想を1-tokenへ一般化した
(`select_rare_single_word_candidates`)。採否は以下の3条件の組み合わせ
(いずれも一般化されたルールであり、個別語のhardcodeではない):

1. **形態素条件**: 内部ハイフン(複合語シグナル、例: self-awakening)、
   または技術語・抽象名詞に典型的な派生接尾辞(`-ness`/`-tion`/`-sion`/
   `-ity`/`-ism`/`-ology`/`-ography`/`-ative`/`-ization`、例:
   grogginess)。
2. **頻度条件**: wordfreq zipf頻度が閾値(3.3)未満(既知だが稀な語)、
   または頻度データが一切存在しない(`frequency_unknown`区分、後述の
   安全策対象)。
3. **文脈条件**: 記事内出現回数(occurrence)を優先度算出に使用、記事
   タイトル関連語を優先、かつ**本文中に小文字表記での出現が最低1回ある
   こと**(固有名詞・会話タグの簡易除外ガード、"Echo"/"Mara"が常に
   大文字始まりで出現するため対象外になることを実データで確認、§4)。

さらに、既存group1 DB(CEFR-J/NGSL/Wiktionary idiom系)に一致する語は
`match_candidate_against_group1`(既存関数の再利用、判定基準の二重実装を
避ける)で確実に除外する。

**安全策(実装中に発見した副作用と対策)**: "minaudières"
(小さなクラッチバッグを指す語、small_bag記事に実在)が、既存の
ASCII限定トークナイザ(`ext._WORD_TOKEN_RE`、非ASCII文字[アクセント付き
"è"等]を認識しない、Trial-01から無変更の既存仕様)により
"minaudi"+"res"へ分断され、"minaudi"がwordfreq頻度データ皆無
(`frequency_unknown`)の1-token候補として誤って拾われることを実データで
発見した。この安全策として、`frequency_unknown`区分の候補**だけ**は
Wiktionary lemma lookupでの実在確認が取れた場合のみ最終採用する
gateを追加した(`build_rare_single_word_evidences`)。"minaudi"は
Wiktionaryにページが存在せず、この安全策により正しく除外されることを
確認した(unit test`test_frequency_unknown_candidate_dropped_without_
wiktionary_confirmation`)。一方、形態素条件(hyphen/接尾辞)または
既知の頻度データ(頻度データありだが閾値未満)で採用される候補は
Wiktionary確認の有無に関わらず採用する(self-awakeningはWiktionary未
確認のまま採用、grogginessはWiktionary確認・頻度データ両方が根拠として
残る)。

新しいDB(有料辞書・大規模コーパス等)は一切導入していない(既存の
CEFR-J/NGSL/Wiktionary/wordfreqの範囲内)。

### 2-4. 修正確認(実データ、実LLM実行)

wake_a2の最終5件に**grogginess・self-awakingが両方とも選定された**
(Trial-03 run_02では0/5、既存Production公開KP5件中0件一致だった)。
wake_b1bでもself-awakeningが選定された。既存Production公開KPとの一致数
(overlap_count、§3表参照)はwake_a2で0→2、wake_b1bで2→3に改善した。

---

## 3. 12本文比較表(Trial-03 vs Trial-04)

| article | Trial-03 shortlist | Trial-04 shortlist | Trial-03 structural | Trial-04 structural | Trial-03 cost(¥) | Trial-04 cost(¥) | 既存KP一致(03→04) |
|---|---:|---:|---|---|---:|---:|---|
| meta_a2 | 21 | 22 | PASS | PASS | 1.6026 | 1.1222 | N/A |
| meta_b1b | 22 | 24 | PASS | PASS | 0.6639 | 1.3080 | N/A |
| hormuz_a2 | 20 | 20 | PASS | PASS | 1.0426 | 1.1096 | N/A |
| hormuz_b1b | 20 | 20 | PASS | PASS | 1.1248 | 0.9399 | N/A |
| small_bag_a2 | 20 | 20 | PASS | PASS | 0.9551 | 1.1059 | N/A |
| small_bag_b1b | 20 | 20 | PASS | PASS | 1.2614 | 2.0284 | N/A |
| wake_a2 | 20 | 20 | PASS | PASS | 1.0745 | 0.8684 | 0/5 → **2/5** |
| wake_b1b | 20 | 20 | PASS | PASS | 0.9621 | 0.8861 | 2/5 → **3/5** |
| aihiring_a2 | 20 | 21 | PASS | PASS | 0.7179 | 0.7246 | 1/5 → 1/5 |
| aihiring_b1 | 20 | 20 | PASS | PASS | 1.0274 | 0.7710 | 1/5 → **2/5** |
| twins_a2 | 20 | 20 | **INVALID** | **PASS** | 1.1147 | 0.8780 | (参考2/5) → 2/5 |
| twins_b1 | 20 | 20 | PASS | PASS | 1.0743 | 1.0738 | 3/5 → 3/5 |
| **合計** | **243** | **247** | **11/12 PASS** | **12/12 PASS** | **¥12.6213** | **¥12.8159** | — |

主要な変化:

- **structural PASS: 11/12 → 12/12**(twins_a2のINVALIDがFix Aで解消)。
- **既存Production KP一致**: wake系・aihiring_b1で改善(Fix Bによる
  rare single word回収の直接効果)。悪化は観測されなかった。
- **cost**: 合計¥12.6213→¥12.8159(+1.5%、実質同水準)。Guardrail
  ¥60・STOP閾値¥50のいずれにも抵触していない。
- **shortlist件数**: 合計243→247(+4、meta_a2/meta_b1b/aihiring_a2で
  各+1〜2、rare single word候補追加による軽微な増加)。20件前後の目安・
  STOP閾値30件のいずれも超過していない。

### 3-1. word比率(phrase偏重/word偏重チェック)

最終5件×12本文=60件のうち、モデル自身が`phrase_type`で「word」に
分類した件数: Trial-03 11/60(18.3%)→Trial-04 14/60(23.3%)。
増加分は主にsmall_bag系(clutch/roomy/pouch等)・wake_a2
(grogginess/build-up/timekeeper)・meta系(concierge)で、いずれも
Fix Bが新規に候補化した「重要な単語」区分からモデルが選んだ結果であり
(§2)、「重要語区分から少なくとも1個選ぶ」という既存設計方針(ユーザー
確定原則、Trial-02から継続)どおりの挙動である。phrase/idiom/phrasal
verb偏重が崩れたり、重要な名詞句(contract worker/sea blockade/Brent
crude/digital twin等)が最終5件から漏れた本文は無かった(§4)。

---

## 4. 既知bug A〜E再発チェック・会話タグfalse positive観察

| # | チェック項目 | 結果(12本文) |
|---|---|---|
| A | discontinuous phrasal verb false positive(bags out/move in/play in) | 再発なし(全12本文のstage1_debug.jsonをcanonical_form照合、該当ゼロ件) |
| B | Wiktionary multiword粗さ(even though/other side/other end) | meta_a2/meta_b1bのphrase_survivorsに引き続き出現するが、important_noun_candidatesには含まれない(bug B修正どおりphraseバケットへ降格済み、実データ確認済み) |
| C | possessive noise(user's/chart's/season's等) | word_survivorsに`'s`/`s'`終端の残存なし(全12本文確認) |
| D | important noun phrase bucket精度 | contract worker/sea blockade/Brent crude/digital twinはいずれも該当記事のshortlistで保持(hormuz_a2は今回sea blockadeがshortlistに残るがモデルが最終5件に選ばなかった、Trial-03でも観測済みのモデル裁量による揺らぎ、§3参照) |
| E | small_bag `have a big moment`(既存仕様、Production module無変更) | 本Trialでも未変更のまま、12本文全件PASS(Trial-03と同じ理由、Production module自体への変更は行っていない) |
| 会話タグFP(twins) | `echo said`/`mara said`がimportant_noun_candidatesに出現(Trial-03 §15-5と同一の既知観測) | 本Trialでも修正は行っていない(スコープ外)。実際の最終5件にはいずれの回も選ばれておらず、実害は今回も確認されなかった |

---

## 5. cost・token・latency(実測、12本文合計)

| article | input | output | reasoning | cost(¥) | status |
|---|---:|---:|---:|---:|---|
| meta_a2 | 2,531 | 5,423 | 4,139 | 1.1222 | PASS |
| meta_b1b | 2,696 | 6,363 | 5,119 | 1.3080 | PASS |
| hormuz_a2 | 2,352 | 5,387 | 4,124 | 1.1096 | PASS |
| hormuz_b1b | 2,389 | 4,497 | 3,106 | 0.9399 | PASS |
| small_bag_a2 | 2,291 | 5,378 | 4,142 | 1.1059 | PASS |
| small_bag_b1b | 2,397 | 10,165 | 8,804 | 2.0284 | PASS |
| wake_a2 | 2,370 | 4,128 | 2,815 | 0.8684 | PASS |
| wake_b1b | 2,402 | 4,215 | 2,952 | 0.8861 | PASS |
| aihiring_a2 | 2,382 | 3,377 | 2,070 | 0.7246 | PASS |
| aihiring_b1 | 2,409 | 3,614 | 2,296 | 0.7710 | PASS |
| twins_a2 | 2,304 | 4,189 | 2,966 | 0.8780 | PASS |
| twins_b1 | 2,302 | 5,209 | 3,961 | 1.0738 | PASS |
| **合計** | **28,825** | **61,945** | **46,494** | **¥12.8159** | **12/12 PASS** |

**LLM call数**: 12回(1本文1 call、Wiktionary lookup用・candidate
cleanup用の追加LLM callは実装していない)。Guardrail¥60・STOP閾値¥50の
いずれにも抵触していない(実測¥12.8159)。

（small_bag_b1bのcost/reasoningが他記事より高い[¥2.0284]のは、モデルの
reasoning token量の実行ごとの変動幅が大きいという既存の既知傾向
[Trial-03 §9でも言及]であり、Fix A/Bに起因する系統的な増加ではない。
input tokenはFix A/B適用後も他記事と同水準[2,397]であることからも
裏付けられる。）

---

## 6. 最終5件(12本文、確定)

### meta_a2
1. pull back (phrasal_verb) 2. concierge (word) 3. take off (phrasal_verb)
4. step out (phrasal_verb) 5. contract worker (noun_phrase)

### meta_b1b
1. concierge (word) 2. contract worker (noun_phrase) 3. turn out (phrasal_verb)
4. take over (phrasal_verb) 5. be rolled back (phrasal_verb)

### hormuz_a2
1. be taken back (phrasal_verb) 2. give back (phrasal_verb) 3. Brent crude (technical_term)
4. center stage (noun_phrase) 5. pull back (phrasal_verb)

### hormuz_b1b
1. give back (phrasal_verb) 2. Brent crude (technical_term) 3. pull back (phrasal_verb)
4. sea blockade (noun_phrase) 5. center stage (idiom)

### small_bag_a2
1. take over (phrasal_verb) 2. catch the eye (idiom) 3. clutch (word)
4. roomy (word) 5. pouch (word)

### small_bag_b1b
1. takeover (word) 2. clutch (word) 3. sit on (idiom) 4. tote (word) 5. all over (idiom)

### wake_a2
1. self-awakening (technical_term) 2. grogginess (word) 3. build-up (word)
4. timekeeper (word) 5. feel like (idiom)

### wake_b1b
1. self-awakening (technical_term) 2. body clock (noun_phrase) 3. heart rate (noun_phrase)
4. keep time (collocation) 5. as if (idiom)

### aihiring_a2
1. recruiter (word) 2. answer for (phrasal_verb) 3. go through (phrasal_verb)
4. give notice (idiom) 5. fair chance (noun_phrase)

### aihiring_b1
1. opt-out (technical_term) 2. answer for (phrasal_verb) 3. recruiter (word)
4. fairness check (noun_phrase) 5. pass through (phrasal_verb)

### twins_a2
1. digital twin (technical_term) 2. take over (phrasal_verb) 3. open the door (idiom)
4. repair office (noun_phrase) 5. **sit up (phrasal_verb)**(Trial-03でINVALIDの
原因になっていた項目、Fix Aにより`source_sentence: "Mara sat up"`で構造PASS)

### twins_b1
1. digital twin (technical_term) 2. take over (phrasal_verb) 3. move into (phrasal_verb)
4. audition (word) 5. contact lens (noun_phrase)

（全項目のsource_span/source_sentence/normalization_type等は
`er029_output/key_phrase_db_hybrid_trial_04/<article>/hybrid4_trial_result.json`
に保存済み。全12本文の`source_sentence`は実際の記事本文の実在文と一致し、
既存validator=`validate_min_unit_selection`をノータッチのまま
**全12件`KEY_WORDS_STRUCTURE_PASS`**で通過した。）

---

## 7. 副作用(Family X側の選定変化)

Fix Bはmeta/hormuz/small_bag(Family X、既存6本文)にも適用されるため、
rare single word候補が新たに出現した(concierge/flashy/palm-sized/
pouches/roomy/totes/small-bag等)。実データでは、meta_a2/meta_b1bで
"concierge"が最終5件に選ばれた(Trial-03では選ばれていなかった新規語)。
これは記事の核心語("Meta has pulled back the human **concierge**
feature")であり、悪化ではなくFix Bの意図どおりの改善と判断する。
small_bag系では"roomy"/"pouch"/"tote"/"takeover"が新たに選ばれ、Trial-03の
"runway"/"novelty"に代わった(いずれもファッション記事の一般語彙、
明確な悪化ではないが、モデル選択の変化として記録する)。重要な名詞句
(contract worker/Brent crude/sea blockade)の選定漏れは発生していない
(§4)。

---

## 8. STOP条件チェック

| STOP条件 | 該当有無 | 根拠 |
|---|---|---|
| 新DB採用判断が必要 | **非該当** | 既存CEFR-J/NGSL/Wiktionary/wordfreqの範囲内で両Fixを実装した(§2-3)。Wiktionary`Category:English lemmas`は同じWiktionary DB内の別カテゴリタグを追加参照しただけで、新規DB契約・新規データソースの導入ではない |
| 新しいProduct仕様が必要 | 非該当 | Stage 1候補生成の内部修正のみ、記事仕様・出力フォーマットの変更なし |
| 追加LLM callが必要 | 非該当 | 1本文1 call厳守(§5)。Wiktionary lookupはLLMではなくMediaWiki APIへの無料照会 |
| Production module変更が必要 | 非該当 | er003_key_words_*/er023/er027/er028すべて無変更 |
| 想定外の大幅cost増 | 非該当 | 合計¥12.6213→¥12.8159(+1.5%)、Guardrail¥60未達(§5) |

いずれも非該当であり、Sonnetの判断ではSTOP対象の事象は発生していない。

---

## 9. Fable評価欄

(空欄)

---

## 10. Status仮分類(Sonnet仮判定、確定はFable/ユーザー判断)

Fix A(twins_a2のsentence segmentation起因INVALID解消、12/12 structural
PASS達成)・Fix B(wake_a2のgrogginess/self-awakening回収、既存Production
KP一致数の改善)はいずれも実データで確認済みであり、副作用(bug A〜E再発・
重要語脱落・cost増・shortlist膨張)は観測されなかった(§3・§4・§8)。
Sonnetは`VALIDATED`を提案するが、以下2点はFable/ユーザー確認を推奨する
(§11参照)。

---

## 11. 未解決事項

1. Fix Bの頻度閾値(zipf 3.3)・形態素接尾辞リストは、今回12本文で
   実データ調整した値であり、他ジャンルの記事(専門技術記事等)での
   汎化性は未検証。
2. 会話タグfalse positive(echo said/mara said)は今回も未修正のまま
   (実害なし、スコープ外として明示的に据え置き)。将来Family
   Z/Fiction系記事が増える場合、一般化修正の要否をFable/ユーザーが
   判断する必要がある。
3. hormuz_a2で今回`sea blockade`がshortlistに残るが最終5件には選ばれ
   なかった(Trial-03でも観測済みのモデル裁量による揺らぎ、§4)。
   機械screening側の後退ではないと判断するが、確定的な保証ではない。
4. small_bag系で"roomy"/"pouch"/"tote"のような一般語彙がFix Bにより
   新たに候補化され、モデルがそれらを選ぶ頻度がやや増えた(§7)。
   「重要語」の閾値をさらに厳しくすべきかはFable/ユーザー判断が必要
   (現状は悪化と断定できる証拠はない)。

---

## 12. 証跡・再現方法

### 12-1. Unit test

`.venv/Scripts/python.exe -m unittest er029_key_phrase_db_hybrid_trial_04_test -v`
→ 18件、全PASS。既存`er028_key_phrase_db_hybrid_trial_03_test`(30件)・
`er027_key_phrase_db_hybrid_trial_02_test`(21件、実際の実行では計51件との
合算表示)も無変更のまま再確認済み、全PASS。

### 12-2. 実行コマンド(12本文、実API呼び出し)

`.venv/Scripts/python.exe er029_key_phrase_db_hybrid_trial_04_run.py`

出力: `er029_output/key_phrase_db_hybrid_trial_04/<article>/
{lightweight_selector_prompt.txt, hybrid4_trial_result.json, stage1_debug.json}`、
`er029_output/key_phrase_db_hybrid_trial_04/{cost.json, raw_usage_log.jsonl,
all_articles_stop_conditions.json}`。

### 12-3. 実行ログ(抜粋)

```
meta_a2: stage1: 390->144->142, shortlist=22, hybrid4_status=KEY_WORDS_STRUCTURE_PASS
meta_b1b: stage1: 406->158->155, shortlist=24, hybrid4_status=KEY_WORDS_STRUCTURE_PASS
hormuz_a2: stage1: 353->151->148, shortlist=20, hybrid4_status=KEY_WORDS_STRUCTURE_PASS
hormuz_b1b: stage1: 340->150->146, shortlist=20, hybrid4_status=KEY_WORDS_STRUCTURE_PASS
small_bag_a2: stage1: 284->115->114, shortlist=20, hybrid4_status=KEY_WORDS_STRUCTURE_PASS
small_bag_b1b: stage1: 291->121->120, shortlist=20, hybrid4_status=KEY_WORDS_STRUCTURE_PASS
wake_a2: stage1: 317->137->136, shortlist=20, hybrid4_status=KEY_WORDS_STRUCTURE_PASS, rare_word_final=['build-up','built-in','front-right','grogginess','self-awakening','timekeeper','twenty-four-hour']
wake_b1b: stage1: 385->154->152, shortlist=20, hybrid4_status=KEY_WORDS_STRUCTURE_PASS, rare_word_final=['self-awakening','self-awoke','short-nap']
aihiring_a2: stage1: 606->200->198, shortlist=21, hybrid4_status=KEY_WORDS_STRUCTURE_PASS
aihiring_b1: stage1: 522->200->200, shortlist=20, hybrid4_status=KEY_WORDS_STRUCTURE_PASS
twins_a2: stage1: 377->157->156, shortlist=20, hybrid4_status=KEY_WORDS_STRUCTURE_PASS
twins_b1: stage1: 461->192->190, shortlist=20, hybrid4_status=KEY_WORDS_STRUCTURE_PASS
Done. Total cost JPY: 12.8159
```

### 12-4. Wiktionary実在確認ログ(Fix B、2026-09-27実施)

```
grogginess: Category:English lemmas所属ページあり(確認可能)
self-awakening: ページ自体が存在しない(missing、確認不能)
minaudi: ページ自体が存在しない(missing、確認不能→frequency_unknown区分のため除外)
```

### 12-5. 共有ストア非書込み確認

Strategy L呼び出しは`run_production_selection_gate`(既存関数、無変更)を
validatorとしてのみ使用し、pronunciation ledger/master audio store/
human_review_queue/telemetry等への書き込みAPIは別途呼び出していない
(Trial-03と同じ設計、実行前後で該当ファイルのmtimeに変化がないことを
確認済み)。

---

## Status

**Sonnet報告完了、Fable/ユーザー判断待ち**(§10仮分類・§11未解決事項
参照。最終Status[`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`]の確定は
Fable/ユーザーに委ねる。Sonnetの仮提案は§10の`VALIDATED`)。

Management-ID: KEY-PHRASE-DB-HYBRID-TRIAL-04
