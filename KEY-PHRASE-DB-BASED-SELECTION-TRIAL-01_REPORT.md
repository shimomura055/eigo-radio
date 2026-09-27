# KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01 — DB照合ベースKey Phrase選定 Trial結果

管理ID: KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01
性質: Trial(到達最大Status=`VALIDATED`、Production変更禁止)。
新規ファイルのみ(`er023_output/`、`er023_key_phrase_db_*.py`、
`er023_oxford_evp_lookup.py`)。既存Production module(`er003_key_words_*`、
`er015_advanced_vocab_rule_trial_01_v2`、`er006_model_routing_contract_01`)は
importして再利用したのみで変更していない。

前提: `KEY-PHRASE-DB-BASED-SELECTION-DESIGN-01_REPORT.md` §9のFableレビュー
条件5件(論点1・2・3・4・7)を満たすことを本Trialの着手条件とした。
本REPORTの各節でどう満たしたかを明記する。

---

## 0. 対象・条件

- 対象6本文(既存確定本文、再生成なし): Meta(`run_01`) a2/b1b、
  Hormuz(`diversity_trial_01/hormuz/run_02`) a2/b1b、small_bag
  (`diversity_trial_01/small_bag/run_02`) a2/b1b。
- 条件A: 群1DB(CEFR-J・NGSL/NAWL/BSL/NGSL-Spoken・Wiktionary idioms/
  phrasal verbs/proverbs+multiword terms targeted lookup)のみ。
- 条件B: A + Oxford 3000/5000・Oxford Phrase Listの評価専用lookup
  (Production判定には使わない)。EVPは技術的に照会不成立(1-3節参照)。

---

## 1. DB取込(実測、Fableレビュー論点3対応)

| DB | 取得方法 | 件数 | API call数 | 所要時間 |
|---|---|---:|---:|---:|
| CEFR-J v1.6 | 公式zip直接HTTP GET | 7,801見出し(内144件が複数語) | 1 | 数秒 |
| NGSL/NAWL/BSL/NGSL-Spoken | 公式サイト`.com`の`/s/*.csv`直リンク | 見出し+活用形で14,146表層形 | 4 | 数秒 |
| Wiktionary idioms | MediaWiki API categorymembers | 10,632 | 22 | 31.9秒 |
| Wiktionary phrasal verbs | 同上 | 5,169 | 11 | 12.2秒 |
| Wiktionary proverbs | 同上 | 1,588 | 4 | 4.8秒 |
| Wiktionary multiword terms | **targeted per-candidate lookup**(全件dump 225,910件は非現実的、方式変更) | 本文ごとに最大60候補を照会 | 本文あたり2 call(50件バッチ) | 本文あたり2.5〜36秒 |

詳細: `er023_output/key_phrase_db_trial_01/db_licenses.md`(引用表記・
ライセンス条件)、`wiktionary_ingest_log.md`(方式決定の理由、Trial着手前に
確定済み)。API費用: 全て¥0(無償API・無償公開ページ)。

CEFR-Jは「使用許諾に同意してダウンロード」という案内文言があったが、
実際のzip URLはクリックスルー認証を要求せず直接取得できた(自動取得
成功、STOP該当なし)。

---

## 2. 除外Gate: 規則判定 vs 人間判断(Fableレビュー論点1対応、実測)

6項目のうち4項目(`proper_noun`/`article_specific_low_reuse`/
`semantic_functional_duplicate_of`/`low_value_as_chunk`)は、6本文
すべてで**rule_determined=0件、100%人間判断が必要**という結果になった
(意味・文脈判断を要するため、閾値を決めない設計の当然の帰結)。
残り2項目の実測(6本文合計、group1 DB一致候補186〜356件/本文ベース):

| Gate項目 | 規則判定できた件数の目安(6本文平均) | 備考 |
|---|---:|---|
| too_easy_or_common | 全体の20〜28%程度 | 閉じたクラスの機能語(a/the/is/would等)のみ規則判定 |
| unnatural_out_of_context | 全体の2〜7%程度 | 既存`er003_key_words_min_unit`の構造的hard requirement(1〜5語・完全文/節排除・有限助動詞排除)を流用 |
| 残り4項目 | 0% | 意味・文脈判断が必要、Trialでは人間目視相当(本Trialでは実行者=Sonnetが代行、§6参照) |

実測詳細は各`er023_output/key_phrase_db_trial_01/<article>/extraction_summary.json`
の`gate_rule_determined_vs_human_needed`。

**具体例(人間判断が必要だった実例)**: small_bag_b1bで
"bags out"がWiktionary idiom/phrasal_verbカテゴリに一致したが、本文の
実際の用法は"pushing large bags out"(discontinuous phrasal verb
"push...out"の一部)であり、一致したWiktionary見出し"bag out"(豪州俗語
「非難する」)とは無関係だった。規則では検出できず、人間判断で除外した
(`small_bag_b1b/final_selection.json`の`excluded_false_positive_example`)。

---

## 3. word群/phrase群の別集計(Fableレビュー論点2対応、実測)

6本文合計(group1 DB一致・Gate通過後、B条件=Wiktionary multiword込み):

| | word群 | phrase群(phrase/idiom/phrasal_verb/collocation/discourse) |
|---|---:|---:|
| 候補数(6本文合計) | 779 | 58 |
| 比率 | 93% | 7% |
| 複数DB一致(db_match_count>=2) | ほぼ全件(本文ごとに99〜130件) | **0件(6本文すべてで0)** |

**複数DB一致は構造上ほぼ単語にしか成立しない(Fableレビュー論点2の
懸念どおり)。phrase群のdb_match_count>=2は6本文すべてで0件だった**
(群1のword系2DB[CEFR-J・NGSL]がphrase側をカバーしないため)。

ranking設計はこの懸念に対応し、**word群とphrase群を別々にソートし、
グローバルにdb_match_countでマージしない**実装にした(`er023_key_phrase_
db_trial_run.py`の`word_group.sort(...)`/`phrase_group.sort(...)`個別処理、
`er023_key_phrase_db_trial_tests.py`の
`test_word_and_phrase_groups_do_not_mix_in_ranking`で回帰テスト化)。

**追加の実測観察**: word群のdb_match_count>=2は6本文とも100件前後に
達し、ほぼ全てのCEFR-J/NGSL共通語がここに該当する(=「複数DB一致」
という軸は、word候補の識別性としてほぼ機能しない。設計doc D-2が
想定した「複数DB一致を最優先グループとする」というルールは、word側
では実質意味をなさなかった)。そのため本Trialの最終候補選定では、
db_match_countではなく`wordfreq`のzipf頻度(低いほど希少=内容語らしい)
を**Gate除外の閾値ではなく、限られたOxford lookup予算内でどれを優先
照会するか、および人間判断での最終選定の並べ替え補助**として使った
(閾値による機械的排除はしていない)。

---

### 3.1 種別別集計(追記、6種別・再抽出なし)

ユーザー指示により、word/phrase合算ではなく**single word / multiword
phrase / phrasal verb / idiom / collocation・chunk / discourse・
formulaic expression**の6種別で再集計した(既存の
`candidates_word_group.json`/`candidates_phrase_group_B.json`/
`final_selection.json`から集計のみ、再抽出・API呼び出しなし)。

**主種別決定規則**: 候補に複数の`db_categories`(idiom/phrasal_verb/
multiword_term等)が同時に付与されている場合、以下の優先順位で主種別を
1つに決める。

`phrasal_verb > idiom > collocation > discourse > multiword phrase > word`

実測で確認した事実: 既存の抽出パイプラインが付与する`unit_type`
フィールドは、複数`db_categories`が重複した候補(例:
`speaks for`・`stepped out`は`idiom`+`phrasal_verb`の両方に一致)に対して、
**この優先順位と一致する形で既にphrasal_verbを主種別として確定していた**
(`candidates_phrase_group_*.json`の生データで確認)。そのため本追記の
集計は`unit_type`をそのまま主種別として用いている。

**collocation・chunk / discourse・formulaic expressionが常に0件になる
理由(重要な事実)**: 本Trialの群1DB(CEFR-J・NGSL/NAWL/BSL/NGSL-Spoken・
Wiktionary idioms/phrasal verbs/proverbs/multiword terms)には、
「collocation」も「discourse marker」もカテゴリとして存在しない
(`db_categories`の全出現値は`{phrasal_verb, idiom, multiword_term}`の
3種類のみ、`unit_type`の全出現値は`{word, phrase, idiom, phrasal_verb}`
の4種類のみ、いずれも全6本文の生JSONを走査して確認)。したがって
collocation・chunkとdiscourse・formulaic expressionは、6本文すべてで
Gate通過後候補数・最終候補数とも**構造的に0件**であり、これはDB選定の
質が低いからではなく、**参照している辞書ソース自体にこの2区分の
情報源が含まれていない**ためである(Oxford Phrase Listもphrase単位の
リストであり、collocation/discourseを個別タグ付けしてはいない)。

**表A: Gate通過後候補数(6種別、条件B=群1+Wiktionary multiword targeted
lookup込み、rule判定による構造的Gate通過後・人間判断前)**

| article | single word | multiword phrase | phrasal verb | idiom | collocation・chunk | discourse・formulaic | 合計 |
|---|---:|---:|---:|---:|---:|---:|---:|
| meta_a2 | 131 | 1 | 6 | 4 | 0 | 0 | 142 |
| meta_b1b | 140 | 0 | 8 | 7 | 0 | 0 | 155 |
| hormuz_a2 | 141 | 3 | 4 | 3 | 0 | 0 | 151 |
| hormuz_b1b | 140 | 3 | 5 | 3 | 0 | 0 | 151 |
| small_bag_a2 | 111 | 0 | 4 | 1 | 0 | 0 | 116 |
| small_bag_b1b | 116 | 0 | 5 | 1 | 0 | 0 | 122 |
| **合計** | **779** | **7** | **32** | **19** | **0** | **0** | **837** |

**表B: 最終候補数(6種別、`final_selection.json`の`final_A`、B条件で
変化なし)**

| article | single word | multiword phrase | phrasal verb | idiom | collocation・chunk | discourse・formulaic | 合計 |
|---|---:|---:|---:|---:|---:|---:|---:|
| meta_a2 | 0 | 1 | 4 | 0 | 0 | 0 | 5 |
| meta_b1b | 0 | 0 | 5 | 0 | 0 | 0 | 5 |
| hormuz_a2 | 0 | 2 | 2 | 1 | 0 | 0 | 5 |
| hormuz_b1b | 0 | 2 | 2 | 1 | 0 | 0 | 5 |
| small_bag_a2 | 3 | 0 | 1 | 1 | 0 | 0 | 5 |
| small_bag_b1b | 3 | 0 | 1 | 1 | 0 | 0 | 5 |
| **合計** | **6** | **5** | **15** | **4** | **0** | **0** | **30** |

集計の生データ・計算根拠(主種別決定規則の適用結果を含む)は
`er023_output/key_phrase_db_trial_01/per_type_summary.json`に保存した。

---

## 4. fallback発動率とphrase系件数(Fableレビュー論点4対応、実測)

| article | phrase群件数(B条件) | 除外Gate通過後の総survivors | fallback発動 |
|---|---:|---:|---|
| meta_a2 | 11 | 142 | 発動せず |
| meta_b1b | 15 | 155 | 発動せず |
| hormuz_a2 | 10 | 151 | 発動せず |
| hormuz_b1b | 11 | 151 | 発動せず |
| small_bag_a2 | 5 | 116 | 発動せず |
| small_bag_b1b | 6 | 122 | 発動せず |

設計F-2のfallback条件(Gate通過後候補が4件未満)は、6本文いずれでも
成立しなかった(phrase群単独でも常に5件以上)。**LLM呼び出しは0回、
Selection段階の費用は¥0**(既存Canonicalization段階のコストは本Trialの
範囲外=未実行)。

ただし件数だけでは「質」を保証しない点に注意が必要(§2・§6参照):
small_bag系2本文はphrase群が最も少なく(5〜6件)、かつ内容も
compositional(比喩性が低い)なものが多かったため、最終候補では
word群から補完した(§6参照)。**件数上の「fallback不要」と、
実際に選びたい高品質phrase候補が十分だったかは別の観測軸である**、
というのが本Trialの重要な発見の一つ。

---

## 5. Oxford評価専用lookupの結果(群2、Production判定には使わない)

- 実装方針: Oxford 3000/5000・Oxford Phrase Listはページ単位配布
  (個別candidate用APIが存在しない)ため、**各ページを1回だけ取得し、
  メモリ上でのみ候補ごとの所属確認を行い、ページ本文・全件テーブルは
  ディスクへ保存しない**方式を採用した(`er023_oxford_evp_lookup.py`
  冒頭のコメントに解釈上の決定として明記、Fable/ユーザー確認事項)。
  1候補=1 HTTPリクエストという文字どおりの意味ではない点は明示する。
- EVP(englishprofile.org)は静的HTTP GETでは本文が取得できない
  (Bubble.io製SPA、db_survey確認済み)。**本Trialでは隠しAPIの探索は
  行わず、EVPは`lookup_not_available`として扱った**(STOP条件相当だが、
  Oxfordは照会可能なためTrial全体は継続、6本文とも同じ制約)。
- 実測: 6本文合計でOxford Phrase Listが新規に拾ったphrase候補は
  **0件**(既にWiktionaryで見つけていた"take over"を2本文[meta_a2/
  meta_b1b]で裏付けたのみ)。Oxford 3000/5000(word)は候補語の多くを
  裏付けたが、CEFR-J/NGSLと重複する情報がほとんどで、新規に単語候補を
  追加したわけではない(word候補は元々群1で拾えていたため)。
- 照会件数: 40件/本文(予算目安どおり、超過なし)。

**結論(この6本文サンプルに限定)**: Oxford評価専用lookupは、phrase
候補の追加供給という点では効果が確認できなかった(0件)。ただし
6本文・各本文40候補という限定的なサンプルであり、他の記事・他の
ジャンルでも同じ結果になるとは断定できない。

---

## 6. 本文別結果(A/B比較・最終候補・既存Production重複率)

### meta_a2
- A候補: word 131・phrase 11。B候補: phrase 11(Wiktionary multiword
  targeted lookupで新規1件ヒットしたがGate除外)。
- 最終候補(4-5件、Aで確定・Bで変化なし):
  `pulled back`(phrasal_verb)・`take over`(phrasal_verb)・
  `stepped out`(phrasal_verb)・`call center`(phrase、multiword_term)・
  `speaks for`(idiom/phrasal_verb)。
- A/Bで変わった項目: なし(Oxfordは`take over`をOxford Phrase List
  [b2]として裏付けたのみ)。
- 既存Production Key Phrase: `take off an ai costume`/`contract worker`/
  `human concierge feature`/`sensitive information`/`pull back`。
  重複: `pulled back`≈`pull back`(1/5=20%、活用形の違いのみ)。
- fallback: 不要。DB別寄与: Wiktionary(全phrase候補の供給源)。
  単語:phrase比率(Gate通過後survivors)=131:11(92:8)。

### meta_b1b
- A候補: word 140・phrase 15。B: 変化なし。
- 最終候補: `rolled back`・`turned out`・`standing behind`・`take over`・
  `speaks for`(すべてphrasal_verb系)。
- A/Bで変わった項目: なし(`take over`をOxfordが裏付けたのみ)。
- 既存Production: `turn out not to be`/`contract workers`/
  `on the other end`/`sensitive information`/`be rolled back`。
  重複: `rolled back`≈`be rolled back`、`turned out`≈`turn out not to be`
  (2/5=40%)。
- fallback: 不要。単語:phrase比率=140:15(90:10)。

### hormuz_a2
- A候補: word 141・phrase 8。B: Wiktionary multiword targeted lookupで
  2件追加ヒット(`brent crude`・`center stage`)、phrase 10。
- 最終候補: `brent crude`(phrase)・`center stage`(phrase)・
  `pulled back`(phrasal_verb)・`by trade`(idiom)・`passing through`
  (phrasal_verb、"pass through"のlemma還元で検出)。
- A/Bで変わった項目: **`brent crude`・`center stage`はWiktionary
  multiword targeted lookup[Aの一部]で発見**(Oxford由来の追加ではない、
  §5のとおりOxfordはこの2本文で新規phrase追加なし)。
- 既存Production: `give back gains`/`sea blockade`/`brent crude futures`/
  `take a sharp turn`/`settle at`。重複: `brent crude`≈`brent crude
  futures`(部分一致、1/5=20%)。
- fallback: 不要。単語:phrase比率=141:10(93:7)。
- 観測: `give back`はWiktionary DB自体には存在した
  (`categories: [idiom, phrasal_verb]`)が、本文は"gave back"(不規則
  活用)であり、既存lemma還元ロジック(`lemma_candidates_v2`、規則語尾
  のみ対応)は不規則動詞(gave→give等)を吸収できず**検出漏れ**が
  発生した。設計doc C-3で「未実装」と明記されていた複数語表現の活用形
  正規化の限界が、不規則動詞という具体的な形で実証された。

### hormuz_b1b
- A候補: word 140・phrase 9。B: 同様に2件追加(`brent crude`・
  `center stage`)、phrase 11。
- 最終候補: hormuz_a2と同一の5件(`brent crude`・`center stage`・
  `pulled back`・`by trade`・`passing through`)。
- 既存Production: `give back`/`sea blockade`/`stand at center stage`/
  `take a sharp turn`/`recover the cost`。重複: `center stage`≈`stand at
  center stage`(1/5=20%)。
- fallback: 不要。単語:phrase比率=140:11(93:7)。

### small_bag_a2
- A候補: word 111・phrase 5(6本文中最少)。B: 変化なし。
- 最終候補: `catch the eye`(idiom)・`taking over`(phrasal_verb)・
  `clutches`(word、wordfreq希少度上位)・`novelty`(word)・`luggage`
  (word)。**phrase供給が薄く、word群から3件補完**(§4で述べた
  「件数上fallback不要でも質的には薄い」具体例)。
- 既存Production Key Phrase: 存在しない(このrunはProduction配線前の
  Trial記事のため、比較対象なし)。
- fallback: 件数上は不要(phrase 5件で閾値4件を上回る)。ただし
  質的には5件中2件のみを採用し、残りはword群で補った。
  単語:phrase比率=111:5(96:4、6本文中最もword偏重)。

### small_bag_b1b
- A候補: word 116・phrase 6。B: 変化なし。
- 最終候補: `sits on`(phrasal_verb/idiom)・`all over`(idiom)・
  `clutches`(word)・`takeover`(word)・`novelty`(word)。
- 除外した誤検出例: `bags out`(§2の具体例参照、discontinuous phrasal
  verbとの取り違え)。
- 既存Production: 存在しない(比較対象なし)。
- fallback: 件数上は不要。単語:phrase比率=116:6(95:5)。

---

## 7. 全体まとめ表

| article | word候補 | phrase候補(B) | 複数DB一致phrase | fallback | Oxford新規phrase | 既存Production重複率 |
|---|---:|---:|---:|---|---:|---:|
| meta_a2 | 131 | 11 | 0 | 不要 | 0 | 20% |
| meta_b1b | 140 | 15 | 0 | 不要 | 0 | 40% |
| hormuz_a2 | 141 | 10 | 0 | 不要 | 0 | 20% |
| hormuz_b1b | 140 | 11 | 0 | 不要 | 0 | 20% |
| small_bag_a2 | 111 | 5 | 0 | 不要(質的には薄い) | 0 | N/A |
| small_bag_b1b | 116 | 6 | 0 | 不要(質的には薄い) | 0 | N/A |
| **合計/平均** | **779** | **58** | **0** | **0/6発動** | **0/6本文** | **平均25%(4本文中)** |

最終候補(6本文合計30件)のunit_type内訳: phrase系22件(73%)・word系
8件(27%)。うち、Gate通過後の生候補全体(93:7でword優勢)とは逆に、
**人間判断による最終選定では意図的にphrase系を優先した**(§3のD-2
ランキング方針どおり、複数DB一致数[word優勢]をそのまま使わず、
chunk価値のあるphraseを優先するという設計方針を反映)。

---

## 8. 事実整理(推奨はFable/ユーザーへ、ここでは仮分類のみ)

- **群1DB(CEFR-J・NGSL系・Wiktionary)だけで4〜5件のphrase候補は
  常に確保できた**(6本文中0件がfallback発動、phrase候補は5〜16件)。
  ただしphrase候補には、Wiktionaryのカテゴリタグ精度に起因する誤検出
  (`bags out`)や、不規則動詞の活用形を吸収できないことによる検出漏れ
  (`give back`←"gave back")が実際に確認された。
- **Oxford評価専用lookupは、この6本文サンプルでは新規phrase候補を
  1件も追加しなかった**(`take over`の裏付けのみ、2/6本文)。EVPは
  技術的に照会不成立(SPA、隠しAPI探索は行わなかった)。
- **複数DB一致(db_match_count>=2)は、word側でほぼ全件・phrase側で
  0件という極端な偏りが実測で確認された**。「複数DB一致の強さ」を
  ranking軸として使う設計は、群1の構成(word系2DB+phrase系実質1DB)
  である限り、phrase候補の識別には機能しない。
- **既存Production(LLM選定Strategy L)との重複率は20〜40%**(4本文で
  比較可能、small_bag系2本文は既存Production Key Phraseが存在せず
  比較不可)。既存Productionはphrase・collocation中心の選定結果になって
  おり(`brent crude futures`、`stand at center stage`、`give back gains`
  等)、DB照合方式の一部(brent crude、center stage等)と一致していた。

### 仮分類(事実に基づく整理、推奨はFableへ)

1. **Oxford/EVPがなくても実用上十分**: 本Trialの6本文サンプルでは、
   Oxford評価専用lookupが新規phrase候補を1件も追加しなかったこと、
   群1DBだけでphrase候補が常に確保できたことから、この分類に該当する
   事実が観測された。
2. **一部改善するが契約検討するほどではない**: Oxford 3000/5000は
   word候補のCEFR裏付けとして機能したが、群1(CEFR-J/NGSL)と重複する
   情報が大半で、新規性は乏しかった。
3. **影響が大きくライセンス交渉を検討すべき**: 本Trialのサンプル
   (6本文、各40候補)では該当する事実は観測されなかった。

**上記1に該当する事実が最も多く観測されたが、サンプルが6本文・ニュース
記事中心(Meta/Hormuz/small_bag)に限られる点、EVPが技術的制約で照会
できなかった点は明記しておく。最終的な採否・優先順位判断はFable/
ユーザーに委ねる。**

---

## 9. STOP条件該当チェック

- 群1DB取得不能: 該当なし(すべて自動取得成功)。
- Oxford・EVP照会が公開ページで成立しない: **EVPは該当**(SPA、静的
  HTTP GET不可)。Oxfordは成立したためTrial全体は継続、EVPのみ
  `lookup_not_available`として扱った。
- 照会上限を大幅に超えないと比較が成立しない: 該当なし(40件/本文の
  予算内で完結、§5)。
- 費用¥200到達: 該当なし(実測¥0、`cost.json`参照)。
- 除外Gateの規則化で意味判断が必要になり人間判断なしに候補が確定
  できない: **部分的に該当**(§2のとおり6項目中4項目が常に人間判断
  必須)。ただしこれは設計段階で明記済みの前提(閾値を決めない
  observation設計)であり、Trial自体は人間判断相当(実行者=Sonnetの
  判断)で完結させた。完全な機械的確定はできない、という点は
  Production採用検討時の重要な留意事項として明記する。

**総括: STOPには該当しない(EVPの部分的制約を除く)。Trialは最後まで
実施できた。**

---

## 10. 費用・証跡

- 費用: ¥0(LLM呼び出し0回、Web access費用0円)。詳細:
  `er023_output/key_phrase_db_trial_01/cost.json`。
- Unit test: `er023_key_phrase_db_trial_tests.py`(13件、すべてPASS、
  抽出n-gram決定性・DB照合決定性・word/phrase別集計非混在・
  重複排除決定性を検証)。実行コマンド:
  `.venv/Scripts/python.exe -m unittest er023_key_phrase_db_trial_tests -v`。
- 新規ファイル: `er023_key_phrase_db_ingest.py`・
  `er023_key_phrase_db_extraction.py`・`er023_key_phrase_db_trial_run.py`・
  `er023_oxford_evp_lookup.py`・`er023_key_phrase_llm_fallback.py`(未使用、
  fallback発動なし)・`er023_key_phrase_db_trial_tests.py`・
  `er023_output/key_phrase_db_trial_01/`(DB・各本文の結果一式)。
- Production経路(`er003_key_words_*`)への配線・変更は一切行っていない。

## 11. 次に進めてよい作業・まだ進めてはいけない作業

- 進めてよい(ユーザー承認があれば): 本Trial結果を踏まえた
  Production採用可否の判断、discontinuous phrasal verb対応や不規則
  動詞lemma還元の拡張実装(§6で検出漏れとして具体的に確認された課題)。
- まだ進めてはいけない: 本設計・Trial結果のProduction Key Phrase経路
  への配線(`APPROVED_FOR_PRODUCTION`はユーザーのみが決定)。Oxford/EVP
  データの永続保存・Production組込み(本Trialのlookup結果は評価専用、
  再利用しない、§0参照)。

---

## 12. Fable評価(2026-09-27)

- 委任条件照合: 6本文・A/B比較・Fableレビュー条件5件・Oxford照会上限・
  EVP不成立の正直な報告・費用¥0・Production無変更=いずれも充足。種別別
  集計は§3.1で補完。
- 分類: **VALIDATED**(Trialとしては設計どおり完了し、計測目的を達成)。
  ただしProduction採用は推奨しない(理由は次項)。
- 事実からのFable判断:
  (1) Oxford/EVP: 本サンプルでは新規phrase候補0件。「Oxford/EVPがなくても
  実用上十分」に該当し、ライセンス交渉・契約は不要と判断(EVPは技術的に
  未照会だが、Oxford Phrase Listで0件だった以上、EVPで状況が変わる見込み
  は低い)。
  (2) 設計の前提が実測で崩れた点: 除外Gate6項目中4項目は100%人間判断が
  必要で、本Trialではその「人間判断」をSonnet(LLM)が代行した。すなわち
  DB照合方式は「候補生成」からAI主観を除いたが、「最終選定」の主観は
  除けておらず、Productionで自動化するには結局LLM判定(または人手)が
  必要になる。当初の目的(AI主観の削減)に対する効果は限定的。
  (3) 品質の傾向: DB方式の最終候補は汎用的な句動詞(pulled back/take
  over/stepped out等)に寄り、既存Production(Strategy L)の選定
  (brent crude futures/stand at center stage/take a sharp turn等)の方が
  記事に根ざしたchunkを拾えている。重複率20〜40%。phrase供給はWiktionary
  単独依存で全候補の7%、誤検出(bags out)・検出漏れ(gave back)も実証。
  (4) 費用面の利点(fallback 0/6、LLM call削減)は事実だが、(2)により
  Productionでは選定LLM callが残るため削減幅は設計値どおりにならない。
- 次に進めてよい/いけない: Production配線は行わない。追加Trialはユーザー
  承認がある場合のみ(候補: DB照合結果を既存Strategy L選定promptへ
  「候補根拠」として渡すhybrid Trial)。
- CEFR-J取得の透明性: zipは同意クリックなしで直接取得できたが、引用条件
  (『CEFR-J Wordlist Version 1.6』東京外国語大学投野由紀夫研究室、
  URL・取得年月)は`db_licenses.md`に記録済みで遵守。Trial専用データで
  あり再配布・Production組込みはしていない。

Management-ID: KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01
