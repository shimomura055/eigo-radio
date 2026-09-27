# KEY-PHRASE-DB-HYBRID-TRIAL-03 — LLM input軽量化(article全文非送信)+既知bug一般化修正Trial結果

管理ID: KEY-PHRASE-DB-HYBRID-TRIAL-03(Trial。到達可能Status=`REJECTED`/
`VALIDATED`/`USER_DECISION_REQUIRED`。**Production配線・
`APPROVED_FOR_PRODUCTION`化は行っていない。**)

新規ファイル: `er028_key_phrase_db_hybrid_trial_03_stage1.py`(Stage 1、
LLM不使用・決定論的、bug A/B/C修正+compact context構築)、
`er028_key_phrase_db_hybrid_trial_03_run.py`(orchestration、Stage 2として
既存Strategy Lを軽量化promptで1回呼ぶ)、`er028_key_phrase_db_hybrid_trial_03_test.py`
(unit test、30件・全PASS)。出力: `er028_output/key_phrase_db_hybrid_trial_03/`。

`er027_*`(Trial-02資産)・`er023_*`・`er003_key_words_production.py`・
`er003_b1_p2_keywords.py`・`er003_key_words_min_unit.py`は**すべてimport/
読み取りのみ、無変更**(prompt本体はTrial側でのin-memoryコピー)。

---

## 0. 既存資産照合(A/B/C分類、先頭で実施)

| 論点 | 分類 | 根拠 |
|---|---|---|
| Strategy Lがarticle全文をpromptへ渡す仕様 | **A(既存仕様あり)** | `er003_b1_p2_keywords.py`の`PROMPT_TEMPLATE_PATH`(`b1_p2_keywords_l_prompt_template.txt`)は`{approved_b1_article}`をそのまま埋め込む設計。Trial-02もこの仕様をそのまま踏襲していた。今回はこの仕様自体を変更するのではなく、**Trial側のin-memoryコピーでarticle全文差し込み部分だけを別内容に置き換える**(Production template・関数は無変更のまま)。 |
| 有限助動詞hard requirement(`have a big moment`)と自動retryの既定 | **A(既存仕様あり、未発火ではなく設計どおりの挙動)** | `er003_key_words_production.MAX_PRODUCTION_RETRY_ATTEMPTS = 2`(初回+1回retry)がProduction既定値。Trial-02・Trial-03とも`run_production_selection_gate(..., max_attempts=1)`をユーザー指示#6(1本文1 call)に従い明示指定しており、Production既定のretryをそもそも使っていない。Trial-02 §5.6で「Hybrid・Baseline両方が同一理由でINVALID」と確認済みで、これはvalidator bug・実装漏れではなく、Trial設計(max_attempts=1)がProduction既定のretry機構を意図的に使っていないことの帰結。**Production module自体に修正は不要**。 |
| possessive/品詞処理の既存関数 | **A(既存仕様あり、未使用箇所があった)** | 群1DB照合(`er023_key_phrase_db_extraction.match_candidate_against_group1`)は`er015_advanced_vocab_rule_trial_01_v2.lemma_candidates_v2`経由で`'s`除去を**マッチング用途では**既に行っていたが、結果として返す`surface_form`/`canonical_form`には元の`'s`が残る実装だった(bug C、§4参照)。 |
| upstream Topic metadataの所在 | **C(調査の結果、既存artifactとして存在するが専用の再利用経路は無かった)** | `entry_point.json`の`args.theme`は日本語原題、`ja_writer/runtime_evidence.json`の`title`も日本語(JA原稿タイトル)。英語版のTopic titleとして再利用可能なのは、Writerが既に生成し確定済みの`article.md`のH1見出し行のみ(新しいLLM callでの抽出ではなく、既存ファイルの最初の行を読むだけ)。本Trialではこれを再利用した。 |
| discontinuous phrasal verb false positive / Wiktionary multiword粗さ / possessive noise | **B(過去Trialで既知、Trial-02は未修正のまま「既知の残存ギャップ」として明記)** | Trial-02 REPORT §3・§6・§9で明記済み。本Trialは一般化して修正する(§4)。 |

---

## 1. 新しいHybrid input構造

Strategy Lへ渡すuser messageは以下の4ブロックのみで構成する(article全文は
一切含まない)。

1. **静的instructions**: 既存Production prompt template
   (`b1_p2_keywords_l_prompt_template.txt`)から、article本文の差し込み
   placeholder(`{approved_b1_article}`)とその直前のラベル行だけを機械的に
   除去した残りの文言(文言自体は一切変更していない)。
2. **Topic**: `article.md`のH1見出し行のみ(新しいLLM callでの再抽出はして
   いない、既存Writer成果物をそのまま読む)。
3. **compact shortlist**: `重要な単語・単語群候補` / `phrase・idiom・
   phrasal verb候補` / `word候補`の3区分に分け、各行を
   `- candidate: "<表層形>" | type: <種別> | occ: <記事内出現回数> |
   evidence: <簡潔なDB根拠> | sentence: <参照sentence ID>`の1行形式で示す。
4. **SENTENCE REFERENCE**: 候補が実際に参照する文だけを、重複なく
   `S<n>: "<原文そのまま>"`の形で列挙する(1記事あたり10〜17文、記事の
   全文ではなく「候補が言及する文」の集合)。
5. **選定方針**: 「候補一覧の中からのみ選ぶ」「重要語1枠以上」
   「phrase/idiom/phrasal verb優先」「CEFRを主軸にしない」
   「source_sentenceは【SENTENCE REFERENCE】の文をそのまま使う」を明記。

Appendix(meta_a2、1本文分のprompt逐語)は§13参照。

---

## 2. article全文を送ったか

**送っていない。** 構造的assertion(`assert_no_full_article_body`、
本文から抽出した連続100語の窓を20語刻みでスライドさせ、promptへ部分
文字列として含まれていないことを確認)を6本文全てで実行し、例外なく
通過した(unit testでも同一ロジックを固定回帰化、
`NoFullArticleBodyInPromptTests`)。ただし、SENTENCE REFERENCEには
「候補が言及する文」を重複なく列挙するため、短い記事(300〜400語規模)
では記事のほぼ全文(センテンス単位で10〜17/17〜24文中)が結果的に
引用される。これは「article全文を一つの連続テキストとして再送しない」
という設計目的(§9のcost内訳参照)は満たすが、「文単位の情報量」としては
記事本文のかなりの部分を含む、という限界は正直に記録する。

---

## 3. bug修正内容(A〜E、既存資産照合の分類付き)

### 3-A. discontinuous phrasal verb false positive(分類: B→今回一般化修正)

Trial-02では"large bags out"→"bags out"、"an unexpected move in oil
prices"→"move in"、"a short play in three acts"→"play in"の3件が既知の
残存ギャップだった。本Trialでは、候補の直前1語(既存設計どおりの狭い
window)がCEFR-J品詞で`adjective`の場合、2語のphrasal_verb/idiom候補を
除外する規則を追加した(ADJ+NOUNの名詞句読みが疑われるため)。

**実装中に発見した副作用と修正**: 上記の単純な規則をそのまま6本文の実
データへ適用したところ、"A human **stood behind** the sign"("human"は
CEFR-Jで代表品詞が`adjective`扱いだが、実際はここでは名詞主語)・
"the chart only **pulled back** briefly"("only"も代表品詞`adjective`
扱いだが実際は副詞)の**2件の既存良好候補を新たに誤って除外する**ことが
判明した(CEFR-Jは語ごとに単一の代表品詞しか持たないため)。個別に
"human"/"only"をhardcode除外するのではなく、「候補自身の先頭語が
規則過去形(`-ed`語尾)または既存の不規則動詞過去形テーブル
(`IRREGULAR_VERB_BASE_FORM`、既存流用)に一致する場合、英語の形態論上
ほぼ確実に動詞であり名詞句として読める余地がないため、直前語の品詞に
関わらず除外しない」という一般規則を追加して修正した。修正後、6本文
全件で以下を確認した(§13の診断ログ参照):

- 新規に正しく除外: `play in`(hormuz_a2/b1b)・`move in`(hormuz_a2/b1b)・
  `bags out`(small_bag_b1b) = 既知3bugすべて解消
- 新規の誤除外: **0件**(修正後、追跡中の既知good candidate5件
  [`pulled back`/`take over`/`stepped out`/`call center`/`speaks for`
  等、er027 regression test由来]、および実データで新たに見つかった
  `stood behind`/`pulled back`いずれも保持を確認)

### 3-B. Wiktionary multiword_termの粗さ(分類: B→今回一般化修正)

`even though`/`other side`/`other end`がimportant noun phrase候補へ
誤混入する問題。原因は、群1DB内の`repeated_compound_noun`検出は既に
CEFR-J品詞による名詞句妥当性判定(`_is_plausible_noun_component`、
verb/adverb/preposition/conjunction/pronoun/determiner/auxiliary
verb/interjectionを除外)を経由していたが、Wiktionary multiword targeted
lookupのhitはこの判定を経由せず無条件に`important_noun_phrase_candidate
=True`にしていたこと。本Trialでは**同じ既存の品詞判定基準**を
lookup hitにも後付けで適用する関数
(`refine_multiword_hits_noun_phrase_flag`)を追加した。妥当でないと
判定された候補は削除せず、一般phrase候補として残す(ユーザー指示
「phrase/discourseとして価値があれば別category」に対応)。実データで
`even though`(adverb+adverb)・`other side`/`other end`
(determiner+noun、"other"の代表品詞=determiner)がいずれも
important判定から外れ、phrase候補へ降格されたことを確認した。
一方`call center`(noun+noun)は引き続きimportant判定を維持することも
確認した(bug D「重要候補を過剰に落とさない」との整合)。

### 3-C. possessive 's等のnoise(分類: A→未使用箇所の実装修正)

`user's`/`chart's`/`season's`のような所有格付き語がword候補として
そのまま残る問題。既存のlemma化(`lemma_candidates_v2`)は`'s`除去を
**DBマッチング判定のためだけ**に使っており、マッチ成功後に返す
`surface_form`/`canonical_form`は元の(所有格付き)表層形のままだった。
本Trialでは、word候補(`unit_type==word`)のcanonical_formが所有格
`'s`/`s'`で終わる場合、所有格を除いた基本形へ正規化する後処理
(`strip_possessive_noise_from_word_survivors`)を追加した。基本形の
候補が別途既に存在する場合は所有格側を除去して重複させない。実データで
`user's`→`user`・`chart's`→`Chart`・`season's`→`season`への正規化を
確認した。

### 3-D. important noun phrase bucket精度(過剰最適化の回避、確認事項)

`contract worker(s)`/`sea blockade`/`Brent crude`は、上記A〜C修正後も
6本文全てのshortlistで保持されることを確認した(§5表・§13診断ログ)。
`call center`もbug B修正後に important判定を維持することを確認済み
(§3-B)。false positive削減のための修正(A・B)が重要候補を新たに
落とす副作用がないことを、修正のたびに実データで再検証した(§3-A参照)。

### 3-E. small_bag `have a big moment`(分類: A、既存仕様どおり・Production module修正は不要)

Trial-02では、`max_attempts=1`(Trial設計上の意図的な制限、Production
既定の`MAX_PRODUCTION_RETRY_ATTEMPTS=2`とは別)により、Hybrid・Baseline
両方が同一の有限助動詞違反(`have a big moment`の"have")でINVALIDに
なった。本Trialでは**Production module・validatorに一切手を加えて
いない**。実データでは、本Trialのsmall_bag_b1b実行が**PASS**した
(§5・§7参照)。これはvalidatorの修正によるものではなく、本Trialの
設計(モデルの選択肢をStage 1 shortlistの候補群に限定する指示を
明示的に追加したこと、§1参照)が、結果として「有限助動詞を含む完全な
語句をゼロから生成する」余地をモデルから構造的に減らした、という
**副次的な効果**である可能性が高い(n=1回のみの観測であり、hard
requirement違反が今後絶対に起きないことを保証するものではない)。
Production module自体の修正は行っていない、行う必要も確認されなかった。

---

## 4. Regression結果(既存6本文、本文再生成なし、13項目)

| # | 確認項目 | meta_a2 | meta_b1b | hormuz_a2 | hormuz_b1b | small_bag_a2 | small_bag_b1b |
|---|---|---|---|---|---|---|---|
| 1 | shortlist 20前後 | 21 | 22 | 20 | 20 | 20 | 20 |
| 2 | contract worker(s)保持(shortlist) | ✅ | ✅ | N/A | N/A | N/A | N/A |
| 3 | Brent crude保持(shortlist) | N/A | N/A | ✅ | ✅ | N/A | N/A |
| 4 | sea blockade保持(shortlist→最終5) | N/A | N/A | shortlist✅/最終✅ | shortlist✅/最終✅ | N/A | N/A |
| 5 | phrase/idiom/phrasal verb候補が適切に残る | ✅(14件) | ✅(15件) | ✅(7件) | ✅(6件) | △(3件、genre起因で薄い、Trial-02同様) | △(3件、同左) |
| 6 | bags out false positive消失 | N/A | N/A | N/A | N/A | N/A | ✅ |
| 7 | noun phrase bucketのWiktionary誤分類減少 | ✅(even though/other side/other end降格) | ✅ | N/A | N/A | N/A | N/A |
| 8 | possessive noise除去 | ✅(user's→user) | ✅ | ✅(chart's→Chart) | ✅ | N/A | N/A |
| 9 | Strategy L 1 call | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 10 | article全文がLLM inputへ入っていない | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 11 | 最終5件構成が設計どおり | ✅(重要1+phrasal4) | ✅(重要1+phrasal4) | ✅(重要2+phrasal3) | ✅(重要3+phrasal2) | △(重要1+phrase2+word2) | △(重要1+phrase2+word2) |
| 12 | 現行同等以下のcost | ✅(§8参照、total -8.3%) | 同左 | 同左 | 同左 | 同左 | 同左 |
| 13 | 品質がTrial-02から明確に悪化していない | ✅ | ✅ | △(sea blockade非選択の回もあった、後述) | ✅ | △(word比率やや増、後述) | ✅(むしろ改善、INVALID→PASS) |

△の内訳(悪化ではなく設計どおりの限界・model裁量として記録):

- **#5/#11(small_bag系)**: Stage 1のphrase/idiom候補がこの記事genre
  では元々3件しか無い(Trial-02でも同じ制約)。ユーザー設計「不足時のみ
  word/termで補完」どおりword2件で補完しており、規則違反ではない。
  ただしTrial-02はarticle全文アクセスがあったため`set the mood`/
  `carry the load`のようなshortlistに無い新しいcollocationをモデルが
  自力で作れていた(全文が無ければ原理的に不可能)。本Trialは
  「候補一覧の中からのみ選ぶ」制約を明示したため、同じ記事genreで
  word比率がやや高くなる(0語→2語)。これは軽量化設計固有のtrade-off
  として正直に記録する(STOP条件「article全文を渡さないと品質維持
  不能」に該当するほど深刻ではないと判断したが、Fable/ユーザー評価を
  仰ぐ)。
- **#13(hormuz_a2)**: 1回目実行(修正前ルール)では最終5件に
  `sea blockade`が入らなかった(shortlistには残存)。2回目実行
  (修正後ルール、§13の最終確定結果)では`sea blockade`も選ばれた。
  同一記事・同一shortlistでもモデルの裁量で選択が変わりうることは
  Trial-02でも観測済みの傾向であり、機械screening側の問題ではない。

---

## 5. 最終5件(6本文、確定版=修正後ルールでの2回目実行)

### meta_a2
1. contract worker (noun_phrase) — 契約で働く人
2. pull back (phrasal_verb) — いったん引っ込める
3. take off (phrasal_verb) — 脱ぐ
4. step out (phrasal_verb) — 姿を現す
5. take over (phrasal_verb) — 引き継ぐ

### meta_b1b
1. turn out (phrasal_verb) — あとになって〜だと分かる
2. contract workers (noun_phrase) — 契約スタッフ
3. roll back (phrasal_verb) — 導入した機能をいったん取りやめる
4. stand behind (phrasal_verb) — AIの裏に人がいる
5. take over (phrasal_verb) — 引き継いで対応する

### hormuz_a2
1. be taken back (phrasal_verb) — 出した案が取り消される
2. give back (phrasal_verb) — 上がった分の一部を失う
3. pull back (phrasal_verb) — いったん値が下がる
4. Brent crude (technical_term) — 世界の原油価格の基準になる北海産原油
5. sea blockade (noun_phrase) — 海から船を通さないこと

### hormuz_b1b
1. give back (phrasal_verb) — 上がった分の一部を失う
2. center stage (noun_phrase) — 注目の中心に立つ
3. sea blockade (noun_phrase) — 海上封鎖
4. Brent crude (technical_term) — 世界の原油価格の基準になる原油
5. pull back (phrasal_verb) — いったん下がる

### small_bag_a2
1. catch the eye (idiom) — 目を引く
2. take over (phrasal_verb) — 取って代わる
3. clutch (word) — 小さな持ち手のないバッグ
4. runway (word) — ファッションショーの舞台
5. mini bag (noun_phrase) — 小さなバッグ

### small_bag_b1b
1. sit on (phrasal_verb) — 頂点にいる
2. all over (idiom) — あちこちに広がっている
3. clutch (word) — 小さな手持ちバッグ
4. novelty (word) — 変わったデザインのもの
5. mini bags (noun_phrase) — 小さなバッグ

(全項目のsource_span/source_sentence/normalization_type等は
`er028_output/key_phrase_db_hybrid_trial_03/<article>/hybrid3_trial_result.json`
に保存済み。全6本文の`source_sentence`は実際の記事本文の実在文と一致し、
既存validator=`validate_min_unit_selection`をノータッチのまま全件
`KEY_WORDS_STRUCTURE_PASS`で通過した。)

---

## 6. 新規記事Trialについて

規範(PM_GOVERNANCE 13節)どおり、regression(§4)が概ね受入水準に
達したと判断したため、**新規記事は生成せず、テーマ候補3件の提示のみ
行い、ここでSTOPする**(記事生成はユーザー選定後の次委任)。生成する
場合は既存の`er019_family_x_entertainment_production_runner_01.py`
(テキスト工程のみ)を使う前提で、生成コスト見積は**Meta実績
¥44.658/記事**(`er019_output/family_x_b3_production_wiring_01/run_01/cost.json`
実測、research¥14.47+ledger¥14.27+storyline_b3¥0.67+ja_writer3段階
¥0.74+advanced¥7.84+standard¥6.67)を参照値とする。

**テーマ候補3件(英語・日本語・選定理由)**:

1. **EN**: "Quiet Cracking: Why Some Workers Look Fine but Feel Burned Out"
   **JA**: 「静かな限界:元気そうに見えて実は限界の働き方」
   **理由**: Meta Museの記事と同じ「人間関係・働き方の実感」を扱う
   人間味のあるトレンドで、専門用語に依存せず、phrase/idiomの選定
   候補(burn out, quiet crackingのような複合表現、感情語彙)が豊富に
   見込める。一般ユーザーの関心も見込みやすい。

2. **EN**: "Fewer Episodes, More Hype: Why Hit Shows Are Getting Shorter"
   **JA**: 「話数を減らして期待感UP:話題ドラマが短くなる理由」
   **理由**: small_bag記事と同様の「業界トレンドの数値対比」構造
   (エピソード数減少・視聴継続率等)を持ち、フレーズ動詞・コロケー
   ション(binge, hype up, cut back等)の候補が見込め、専門的すぎず
   一般ユーザーが実際に関心を持ちやすい。

3. **EN**: "Shrinkflation at 30,000 Feet: Airlines Trim Seat Space, Not Prices"
   **JA**: 「機内シートはますます狭く、値段はそのまま:航空業界の
   “隠れ値上げ”」
   **理由**: Hormuz記事と同様の「業界・価格・数値」を扱うビジネス
   トレンドで、句動詞(trim down, squeeze in, cut back)・技術寄り
   だが平易な用語(shrinkflation, seat pitch)のバランスが良く、
   Key Phrase候補の多様性を検証しやすい。

---

## 7. Trial-02との品質比較(9観点)

| 観点 | 所見 |
|---|---|
| article理解に重要か | 6本文とも維持(contract worker/sea blockade/Brent crude/turn out等、記事の核心語句が最終5件に含まれる) |
| learnerが他文脈でも使えるか | 概ね維持(pull back/take over/give back/catch the eye等は汎用性が高い)。`be taken back`(hormuz_a2)はやや記事固有の受動構文寄り |
| phrase・chunkとして自然か | 維持(turn out/roll back/stand behind/sit on/all over等、いずれも自然な学習単位) |
| article-specific fragmentではないか | 維持(過度に記事固有の断片は選ばれていない) |
| proper nounだけではないか | 維持(Brent crudeはtechnical_termとして妥当、proper noun単体の選定はない) |
| trivialすぎないか | 維持 |
| important term枠が意味のある語か | 維持・one部分改善(bug B修正によりcall center等の妥当な重要語のみがimportant枠に入り、even though等のノイズが混入しなくなった) |
| phrase偏重で重要termを隠していないか | 維持(重要枠は必ず1件以上確保、hormuz系は2〜3件) |
| word偏重へ戻っていないか | **small_bag系でTrial-02よりword比率がやや増加**(0語→2語、§4の△参照。「候補一覧内からのみ選ぶ」制約の副作用。genreの制約[phrase候補が元々3件のみ]によるものであり、機械screening側の後退ではない) |

---

## 8. input・output・reasoning token、cost・latency(実測、確定版2回目実行)

| article | input | output | reasoning | cost(¥) | latency(秒) | status |
|---|---:|---:|---:|---:|---:|---|
| meta_a2 | 2,494 | 7,931 | 6,681 | 1.6026 | 74.28 | PASS |
| meta_b1b | 2,592 | 3,414 | 2,108 | 0.6639 | 34.08 | PASS |
| hormuz_a2 | 2,332 | 5,391 | 4,142 | 1.0426 | 48.87 | PASS |
| hormuz_b1b | 2,384 | 5,461 | 4,213 | 1.1248 | 50.18 | PASS |
| small_bag_a2 | 2,272 | 4,936 | 3,624 | 0.9551 | 45.53 | PASS |
| small_bag_b1b | 2,361 | 6,530 | 5,178 | 1.2614 | 65.35 | PASS |
| **合計** | **14,435** | **33,663** | **25,946** | **¥6.6504** | **318.3** | 6/6 PASS |

(1回目実行[修正前ルール、比較用に保持]: 合計 input14,392/output32,545/
reasoning24,653/¥6.7091。ルール修正による差は誤差範囲。実API支出は
2回分の合計¥13.36で、Guardrail¥60・STOP閾値¥50のいずれにも抵触して
いない。)

**LLM call数**: 6回(1本文1 call、candidate cleanup用・Topic抽出用の
追加LLM callは実装していない)。

---

## 9. 現行Productionとのcost比較(token分解)

| 比較対象 | input token(1回あたり平均) | output token | reasoning | cost/call | 備考 |
|---|---:|---:|---:|---:|---|
| 現行Production(baseline、Trial-02実測、small_bag n=2) | 1,515 | 6,111 | 4,798 | ¥1.2228 | 候補ヒントなし、article全文+定型instructionsのみ |
| Trial-02 Hybrid(article全文+候補) | 2,712 | 5,711 | 4,514 | ¥1.2083 | article全文をそのまま送信 |
| **Trial-03 Hybrid3(本Trial、article全文なし)** | **2,406** | **5,611** | **4,324** | **¥1.1084** | article全文の代わりにTopic+shortlist+sentence reference |

**token内訳の分解(なぜinput削減が11%程度に留まったか)**: Trial-03の
input token(平均2,406)は、baselineの平均(1,515)より**約890 token
多い**。内訳は概算で(a)Topic title行: 数十token、(b)compact
candidate一覧(20件前後、1行約15〜25token): 約350〜450token、
(c)SENTENCE REFERENCE(10〜17文、1文あたり10〜20token): 約200〜300token、
(d)選定方針の追加instructions: 約100〜150token。これらの合計が
「article全文を代替する」ために必要な最小限の情報量であり、この6本文
(300〜400語規模の短い記事)では、記事のほぼ全文が「候補が言及する文」
として結果的に参照される(§2参照)ため、SENTENCE REFERENCE自体の圧縮
余地は限定的だった。一方、Trial-02 Hybrid(article全文をそのまま
送信、平均2,712 input)と比較すると、**304 token(約11%)の削減**を
達成した。cost(¥1.1084/call)は、baseline(¥1.2228)・Trial-02 Hybrid
(¥1.2083)いずれよりも下回った(reasoning tokenの変動幅が大きく、
input削減の効果よりreasoning変動の影響の方が総costへの寄与が大きい
点には留意)。

**結論**: 「現行Strategy Lと同等以下のcost」目標は、cost実額ベースでは
達成した(baseline比-9.4%、Trial-02 Hybrid比-8.3%)。input token単体
では、article全文を完全に代替するためのcompact情報(候補+sentence
reference)がbaselineの素の入力よりなお大きいという構造的な限界がある
(短い記事genreでは、候補密度が高くsentence referenceの重複削減効果が
薄いため)。長い記事では、この差はより有利になる可能性が高いが、今回の
6本文(いずれも短い記事)では検証できていない(未解決事項として記録)。

---

## 10. Fable評価欄

(空欄)

---

## 11. Status仮分類(Sonnet仮判定、確定はFable/ユーザー判断)

`§9のSTOP条件チェック`(下表)はいずれも非該当と判定した。§4の△2件
(small_bag系word比率増加・hormuz_a2の最終5件選択ゆらぎ)は「明確な
悪化」ではなく「軽量化設計固有のtrade-off・モデル裁量の範囲」と
Sonnetは判断するが、**最終Status確定はFable/ユーザーに委ねる**。

| STOP条件 | 該当有無 | 根拠 |
|---|---|---|
| article全文を渡さないと品質維持不能 | **非該当** | 6/6本文がstructural PASS、重要語の保持も確認(§4・§5)。small_bag系のword比率増加はgenre制約由来で「品質維持不能」の水準ではないとSonnetは判断 |
| 追加LLM callが必要 | **非該当** | 1本文1 call厳守(§8) |
| costが現行より明確に高いまま | **非該当** | baseline比-9.4%、Trial-02 Hybrid比-8.3%(§9) |
| important termが機械screeningで落ちる | **非該当** | contract worker(s)/sea blockade/Brent crude/call centerいずれもshortlistで保持(§4) |
| known bug修正で正しいphraseを大量に落とす | **非該当** | 修正過程で2件の新規誤除外を発見し即座に一般化修正、最終的に既知good candidate 5件・実データ追加2件とも保持を確認(§3-A) |
| 新しいDBが必要 | **非該当** | 既存CEFR-J/NGSL/Wiktionary/wordfreqの範囲内 |
| Production仕様変更が必要 | **非該当** | Production module無変更 |
| 既存仕様との衝突 | **非該当** | §0参照 |

---

## 12. 未解決事項

1. small_bag系(phrase候補が薄いgenre)で、「候補一覧内からのみ選ぶ」
   制約により、Trial-02と比べてword比率がやや増加する trade-off が
   ある(§4・§7)。これを許容範囲とするか、モデルに限定的な創造の
   余地(shortlistに無い1〜2語程度の軽微な言い換えは許可する等)を
   残すべきかは、ユーザー/Fable判断が必要。
2. 今回の6本文はいずれも短い記事(300〜400語)であり、SENTENCE
   REFERENCEの重複削減効果が薄かった。より長い記事でのinput token
   削減効果は未検証(§9)。
3. hormuz_a2で、同一shortlistでも実行によって`sea blockade`が最終5件
   に入る場合と入らない場合があった(§4)。モデルの裁量の範囲と
   Sonnetは判断するが、確定的な保証ではない。
4. 委任文の`check_delegation_prompt.py`検証結果は**FAIL**だった
   (§13の実行ログ参照。D-2標準テンプレートの固定ブロックラベル
   `E-1/D-1/G-1/F-1`・先出しRead/Grep一覧の形式的記載を、受領した
   委任文が欠いていた)。委任文の実質的な指示内容自体は充足していた
   ため作業は実施したが、Fableへ形式面の是正を報告する。

---

## 13. 証跡・再現方法・Appendix

### 13-1. Unit test

`.venv/Scripts/python.exe -m unittest er028_key_phrase_db_hybrid_trial_03_test -v`
→ 30件、全PASS。既存`er027_key_phrase_db_hybrid_trial_02_test`(21件)・
`er023_key_phrase_db_trial_tests`(13件)も無変更のまま全PASSを再確認済み
(3ファイル合計64件同時実行でもPASS)。

### 13-2. 実行コマンド(全6本文、実API呼び出し)

`.venv/Scripts/python.exe er028_key_phrase_db_hybrid_trial_03_run.py`

出力: `er028_output/key_phrase_db_hybrid_trial_03/<article>/
{lightweight_selector_prompt.txt, hybrid3_trial_result.json, stage1_debug.json}`、
`er028_output/key_phrase_db_hybrid_trial_03/{cost.json, raw_usage_log.jsonl,
all_articles_stop_conditions.json}`

### 13-3. bug A修正過程の診断ログ(誤除外発見→修正→再検証)

修正前ルールでの実データ診断により、新規除外候補のうち
`stood behind`(meta_a2)・`pulled back`(hormuz_b1b)が、既存の
tracked known-good candidateと衝突する誤除外だったことを発見した。
形態論ガード追加後の再診断結果(既知good candidate5件の非除外確認+
既知bug3件の除外確認、全6本文):

```
meta_a2 new-rule exclusions: []
meta_b1b new-rule exclusions: []
hormuz_a2 new-rule exclusions: ['play in', 'move in']
hormuz_b1b new-rule exclusions: ['play in', 'move in']
small_bag_a2 new-rule exclusions: []
small_bag_b1b new-rule exclusions: ['bags out']
ALL_OK(known-good 5件のいずれも新ルールでは除外されていない)
```

### 13-4. Appendix: 1本文分のprompt逐語(meta_a2、確定版)

```
以下のB1英語記事本文から、初回リスニングで意味を取れず、その後の理解を止める可能性が高い英語表現を、支援価値の高い順にちょうど5個選んでください。

まず初回リスニングで難しい箇所を見つけ、その箇所をコピーするのではなく、学ぶべき最小の単語・句・コロケーションへ抽出してください。

display_phraseは1〜5語にしてください。完全文、主語と有限動詞を持つ節、記事固有の長い説明は禁止です。

動詞表現は本文の時制を残さず、原則として基本形へ直してください。受動表現を学ぶ価値がある場合は、be + past participleの見出し形を使用できます。

文字で読み返したときではなく、音声で一度だけ聞いたときに意味を処理できるかを最優先してください。

優先順位は、初回音声での処理困難、未知の可能性、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内重要度、汎用性の順です。

未知単語、題材固有表現、短い複数語パターン、比喩・感情表現を同格の候補として扱ってください。構成語から意味を容易に推測できる透明表現は、記事上重要でも優先度を下げてください。

「ソロ旅行を～％とする」のように、数値を補わないと意味が成立しない句・日本語グロス(数値の穴埋めを必要とする不完全な表現)は選ばないでください。それ単体で意味が成立する句・グロスを選んでください。

選ぶ表現は必ず本文中の実表現(source_span)に対応させ、短く自然な日本語グロスを付けてください。

日本語グロスは、辞書的に正しいだけでなく、日本人の英語学習者が聞いてすぐ意味を理解できる、自然で平易な現代日本語にしてください。直訳調や、「常態」「是正」のような過度に硬い報道語・漢語、一般的な学習者には伝わりにくい表現は避けてください。

日本語グロスには、括弧（　）を使って別の訳し方・専門用語・補足情報を書き添えないでください。音声だけで聞いてそのまま意味が伝わる、平易な言い換えだけの一文にしてください。

日本語グロスは、辞書的な表記として自然な範囲であれば「～」「〜」を使ってもかまいません(例: 「～を示す」)。ただし「…」のようなプレースホルダー記号は使わないでください。日本語グロスに数字を含める場合は、算用数字(1、2、3…)ではなく漢数字(一、二、三…)で書いてください。

【Topic】title: We Thought It Was AI—But There Was a Person Inside Meta’s Muse

【重要な単語・単語群候補】
- candidate: "contract workers" | type: noun_phrase | occ: 3 | evidence: repeated_compound_noun | sentence: S8
- candidate: "call center" | type: noun_phrase | occ: 1 | evidence: wiktionary_multiword | sentence: S17

【phrase / idiom / phrasal verb候補】
- candidate: "at all" | type: idiom | occ: 1 | evidence: wiktionary[idiom] | sentence: S4
- candidate: "come from" | type: phrasal_verb | occ: 1 | evidence: wiktionary[phrasal_verb] | sentence: S3
- candidate: "need to" | type: phrasal_verb | occ: 1 | evidence: wiktionary[phrasal_verb] | sentence: S39
- candidate: "pulled back" | type: phrasal_verb | occ: 1 | evidence: wiktionary[phrasal_verb] | sentence: S35
- candidate: "speaks for" | type: phrasal_verb | occ: 1 | evidence: wiktionary[idiom,phrasal_verb] | sentence: S39
- candidate: "stepped out" | type: phrasal_verb | occ: 1 | evidence: wiktionary[idiom,phrasal_verb] | sentence: S11
- candidate: "stood behind" | type: phrasal_verb | occ: 1 | evidence: wiktionary[idiom,phrasal_verb]+irregular_rescue | sentence: S26
- candidate: "take over" | type: phrasal_verb | occ: 1 | evidence: wiktionary[phrasal_verb] | sentence: S12
- candidate: "took off" | type: phrasal_verb | occ: 1 | evidence: wiktionary[phrasal_verb]+irregular_rescue | sentence: S10
- candidate: "want to know" | type: idiom | occ: 2 | evidence: wiktionary[idiom] | sentence: S30
- candidate: "went on" | type: phrasal_verb | occ: 1 | evidence: wiktionary[phrasal_verb]+irregular_rescue | sentence: S4
- candidate: "even though" | type: phrase | occ: 1 | evidence: wiktionary[multiword_term] | sentence: S24
- candidate: "other end" | type: phrase | occ: 1 | evidence: wiktionary[multiword_term] | sentence: S37
- candidate: "other side" | type: phrase | occ: 1 | evidence: wiktionary[multiword_term] | sentence: S30

【word候補】
- candidate: "Muse" | type: word | occ: 3 | evidence: cefr_j | sentence: S1
- candidate: "listens" | type: word | occ: 1 | evidence: cefr_j+ngsl_family | sentence: S20
- candidate: "reservations" | type: word | occ: 1 | evidence: cefr_j+ngsl_family | sentence: S29
- candidate: "admits" | type: word | occ: 1 | evidence: cefr_j+ngsl_family | sentence: S32
- candidate: "costume" | type: word | occ: 1 | evidence: cefr_j | sentence: S10

【SENTENCE REFERENCE】
S1: "We Thought It Was AI—But There Was a Person Inside Meta's Muse"
S3: "A call seemed to come from an AI agent"
S4: "But as the conversation went on, the voice was not AI at all"
S8: "In some calls through Muse, trained contract workers made the calls, not AI"
S10: "It was like someone took off an AI costume"
S11: "Then a person stepped out"
S12: "Having a person take over is not always a bad thing"
S17: "Then the user's sensitive information could be shared with a contract worker at a call center"
S20: "When people share their names, plans, or personal situations, it matters who listens"
S24: "A user might think the exchange was with AI, even though a person was involved"
S26: "A human stood behind the sign that said AI"
S29: "As AI becomes able to make calls or reservations for us, this question will become more familiar"
S30: "The more useful the feature, the more people will want to know who is on the other side"
S32: "Meta admits a mistake"
S35: "For now, Meta has pulled back the human concierge feature"
S37: "We must also know, at the start, who is on the other end"
S39: "Before AI speaks for us, we need to know whether the voice belongs to AI or a person"

【選定方針】
- 最終的に選ぶ5件は、必ず下記の候補一覧の中から選んでください。候補に
  無い新しい表現を作らないでください。
- 5個のうち少なくとも1個は、[重要な単語・単語群候補]区分から選んで
  ください(記事理解・再利用価値の高い重要な名詞・専門用語・複合語)。
- 残りは、[phrase / idiom / phrasal verb候補]区分を優先してください。
  良い候補が不足する場合のみ[word候補]区分で補ってください。
- CEFR難易度・語彙レベルを主要な判断軸にしないでください。
- 各itemのsource_sentenceは、必ず【SENTENCE REFERENCE】に列挙されている
  文をそのまま(一字一句、改変せず)使用してください。新しい文を作らない
  でください。source_spanは、そのsource_sentence内に実際に現れる形
  (元の活用形・大文字小文字を含む)の一部分にしてください。
```

### 13-5. D-2委任文検証結果(`check_delegation_prompt.py`)

```
status: FAIL
reasons:
  - 必須セクション欠落: 期限(または到達点Status/禁止事項), 先出し指定Read一覧,
    先出し指定Grep一覧+追記位置・更新位置の手順, 実行コマンド全文
  - 固定ブロックラベル欠落: E-1, D-1, G-1, F-1
  - 「実行コマンド全文」セクションが見つからない
```

受領した委任文の実質的な指示内容(管理ID・目的・設計・費用Guardrail・
報告項目・Git手順)自体は充足していたため作業は実施した。形式面の
是正はFable側の委任文標準運用の課題として報告する。

---

## Status

**Sonnet報告完了、Fable/ユーザー判断待ち**(§11仮分類・§12未解決事項
参照。最終Status[`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`]の
確定はFable/ユーザーに委ねる)。

Management-ID: KEY-PHRASE-DB-HYBRID-TRIAL-03
