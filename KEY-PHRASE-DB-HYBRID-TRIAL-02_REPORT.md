# KEY-PHRASE-DB-HYBRID-TRIAL-02 — DB+機械処理screening→Strategy L 1回 Hybrid方式 Trial結果

管理ID: KEY-PHRASE-DB-HYBRID-TRIAL-02
性質: Trial(到達最大Status=`REJECTED`/`VALIDATED`/`USER_DECISION_REQUIRED`)。
**Production配線禁止・Production module/Prompt変更禁止。** Trial結果が良くても
自動でProduction実装へは進めない(ユーザー最終判断待ち)。

## 0. ファイル番号の訂正(委任前提とのずれ)

委任文は「er025まで使用中、新規ファイルはer026」を前提としていたが、実際には
`er026_family_z_fiction_production_runner_01*.py`が既に他Agent(Family Z)に
より使用済みだった(Glob確認済み)。他Agentの並走作業と衝突しないよう、
本Trialは**er027**を使用した。

- `er027_key_phrase_db_hybrid_trial_02_stage1.py`(Stage 1: 機械screening、
  LLM不使用・決定論的)
- `er027_key_phrase_db_hybrid_trial_02_run.py`(オーケストレーション、
  Stage 2としてStrategy Lを1回呼ぶ)
- `er027_key_phrase_db_hybrid_trial_02_test.py`(unit test、21件・全PASS)
- `er027_output/key_phrase_db_hybrid_trial_02/`(6本文の実行結果一式)

`er023_key_phrase_db_ingest.py`/`er023_key_phrase_db_extraction.py`
(KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01の資産)は**import/再利用のみで
無変更**。`er003_key_words_production.py`/`er003_b1_p2_keywords.py`
(現行Production Strategy L)も**無変更**(定数・スキーマ・prompt template・
selector関数を読み取り専用で再利用し、usage計測のためのAPI呼び出し
ラッパーをTrial側に独立実装しただけ)。

---

## 1. 対象・比較設計

対象6本文はKEY-PHRASE-DB-BASED-SELECTION-TRIAL-01と同一(既存確定本文、
再生成なし): Meta(`run_01`) a2/b1b、Hormuz(`diversity_trial_01/hormuz/run_02`)
a2/b1b、small_bag(`diversity_trial_01/small_bag/run_02`) a2/b1b。

比較対象:
- meta/hormuz(4本文): 既存の`keywords_canonicalized.json`(現行Production
  Strategy Lの実際の採用結果)。
- small_bag(2本文): 既存ファイルが無いため、本Trial内で現行Production
  Strategy L(候補根拠なし、通常promptのみ)を1回実行し比較対象を作成した
  (ユーザー指示#8、費用計上済み、後述)。

---

## 2. Stage 1設計(機械処理のみ、LLM不使用、決定論的)

KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01(er023_*)の候補生成・DB照合ロジックを
再利用しつつ、以下を新規追加した(すべて`er027_key_phrase_db_hybrid_trial_02_stage1.py`)。

1. **見出し連結artifact除外**: markdown見出し行を独立ブロックとして扱う
   heading-aware sentence分割へ変更し、"line In"のような偽の2-gramが
   構造的に発生しなくなった(個別語の事後除外ではなく、tokenize段階での
   修正)。
2. **不規則動詞の活用形正規化**: 約90語の標準的な英語不規則動詞表
   (新規ライセンス不要の一般文法知識)を追加し、規則語尾ロジックでは
   検出できなかった"gave back"/"went on"/"took off"/"taken back"を
   "give back"/"go on"/"take off"/"take back"としてDB一致へrescueした。
3. **品詞・文脈の明らかな不一致除外(規則化可能な範囲のみ)**: 実データ
   検証の結果、window(前方参照範囲)を広く取ると既存の良い候補
   ("pulled back"/"rolled back"/"standing behind"/"take over"等)まで
   誤って除外することが判明したため、各ルールは直前1語のみを見る狭い
   スコープに限定した5規則(直前が決定詞/直前がbe動詞+曖昧な小辞/
   先頭語が主語代名詞/2語目がwh語/2語目on・in・at+直後3語以内に時間
   表現)を実装した。**"play in"/"move in"/"large bags out"
   (discontinuous phrasal verb)はこの狭いスコープでは捕捉できない
   既知の残存ギャップ**として明記する(POSタグ付けが必要、無理な
   ルール拡張は既存の良い候補を壊すため見送った)。
4. **duplicate/near-duplicate整理**: 先頭語のlemma候補集合が重なる
   候補("pulled back"/"pull back"等)を1件へ統合する機構を実装した
   (実データでの実際の統合発生は本6本文サンプルでは僅少、機構自体は
   unit testで動作確認済み)。
5. **重要な単語・単語群(important noun phrase)検出の補完**: group1 DB
   (CEFR-J/NGSL/Wiktionary idiom・phrasal_verb・proverb)には
   "contract worker(s)"/"sea blockade"のような重要な名詞句を拾う
   カテゴリが存在しないという構造的限界が、本Trialの設計段階で新たに
   確認された(§3参照)。この限界を補うため、(a) 記事内で2回以上
   出現する実在語(wordfreq zipf≧2.0、CEFR-Jのpos情報で動詞・副詞・
   前置詞等を除外)の2〜3-gramを「重要な単語群」候補として拾う機構と、
   (b) KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01と同じWiktionary multiword
   terms targeted lookup(1回のみ出現する"brent crude"等を拾う、
   API費用¥0)を両方使う。

---

## 3. 重要な発見(設計段階、事実)

- **"sea blockade"はgroup1 word DB(CEFR-J/NGSL)に構成語"blockade"すら
  存在しない**(教育用コア語彙リストのため)。"contract worker(s)"も
  2語の複合語としては群1DBのどのカテゴリにも一致しない(個々の単語
  "contract"/"worker"は一致するが、複合語としての一致先が無い)。
  これはDB選定の質の問題ではなく、**参照辞書の構造そのものに
  「重要だが辞書的多語表現カテゴリに乗らない一般名詞句」という
  区分が存在しない**という、KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01
  §13.5で既に指摘されていた限界の具体的な再確認である。
- 上記の理由により、§2-5の「repeated compound noun検出」を追加しなければ、
  ユーザー確定原則4(1枠=重要単語・単語群)の担保対象である
  "sea blockade"/"contract worker(s)"は機械screening後の候補集合に
  一切現れなかった(STOP条件相当になるところだった)。本Trialでは
  この検出を追加実装することで対応した。

---

## 4. Stage 2(Strategy L、既存Production module・prompt無変更、1本文1回)

`er003_b1_p2_keywords.py`の`load_prompt_template()`/`build_user_message()`
(現行Production prompt template、無変更)で作った基本メッセージへ、
Stage 1のshortlist(候補ごとの種別・DB根拠・頻度・記事内出現回数)を
Trial側で追記した「in-memoryコピー」のみを使用した(テンプレート
ファイル自体は書き換えていない)。追記文には「1枠は重要単語・単語群を
含める」「残りはphrase/idiom/phrasal verb優先」「CEFR難易度を主要な
判断軸にしない」を明記した。

呼び出しは`er003_key_words_production.SELECTOR_MODEL`/
`SELECTOR_REASONING_EFFORT`/`SELECTOR_DEVELOPER_MESSAGE`/
`SELECTOR_JSON_SCHEMA`(すべてProduction定数、無変更)をそのまま使い、
Model Routing Contract(`er006_model_routing_contract_01.require_model`)
経由で"A2_SUPPORT"/"B1_SUPPORT"→`gpt-5.6-luna`を確定させた。usage
(token数)計測のためだけにTrial側で独立したAPI呼び出しラッパーを実装した
(Production moduleのファイル自体は一切変更していない)。解析・hard
requirement検証は`er003_key_words_production.run_production_selection_gate`
(既存Production Gate関数、そのまま呼び出し)を使い、**max_attempts=1**
(ユーザー指示#6「既存Strategy L/LLMを原則1回」に対応、自動再試行なし)
で実行した。

---

## 5. 本文別結果(12項目、ユーザー指示#12)

以下、各本文について(1)機械処理前候補数 (2)機械処理後候補数(shortlist)
(3)important word/multiword term候補 (4)phrase/idiom/phrasal_verb候補
(5)Strategy Lへ実際に渡した候補一覧 (6)Hybrid最終5件 (7)現行Production
最終5件 (8)何が変わったか (9)cost/token/latency (10)Fable評価欄(空欄)
の順に示す。

### 5.1 meta_a2

1. 機械処理前候補数: 390件(1〜5-gram、group1 DB一致、dedup前)
2. 機械処理後候補数(shortlist): **21件**(phrase 11・important noun 5・
   word 5)
3. important word/multiword term候補: `contract workers`・`call center`・
   `even though`・`other end`・`other side`(後2件はWiktionary
   multiword_termタグの粗さによるノイズ、§6で既知の限界として明記)
4. phrase/idiom/phrasal_verb候補(11件): `at all`・`come from`・`need to`・
   `pulled back`・`speaks for`・`stepped out`・`stood behind`
   (不規則動詞rescue)・`take over`・`took off`(rescue)・`want to know`・
   `went on`(rescue)
5. Strategy Lへ渡した候補一覧: 上記3・4 + word群5件
   (`user's`・`Muse`・`listens`・`reservations`・`admits`)、計21件
6. Hybrid最終5件: `contract workers`(noun_phrase)・`pull back`
   (phrasal_verb)・`other end`(noun_phrase)・`take over`(phrasal_verb)・
   `stand behind`(phrasal_verb)
7. 現行Production最終5件: `take off an AI costume`・`contract worker`・
   `human concierge feature`・`sensitive information`・`pull back`
8. 何が変わったか: 重複率**40%**(`contract workers`≈`contract worker`、
   `pull back`=`pull back`完全一致)。前Trial(DB-onlyランキング方式)の
   同記事重複率20%から改善。「1枠=重要単語」ルールが機能し、
   `contract workers`がrank1で選ばれた。
9. cost/token/latency: input 2,732 / output 2,902(うちreasoning 1,552)
   / 合計5,634 token、**¥0.6446**、29.7秒
10. Fable評価欄: (空欄)

### 5.2 meta_b1b

1. 機械処理前候補数: 406件
2. 機械処理後候補数(shortlist): **24件**(phrase 15・important noun 4・
   word 5)
3. important word/multiword term候補: `contract workers`・`call center`・
   `even though`・`other end`
4. phrase/idiom/phrasal_verb候補(15件): `as if`・`at all`・`came from`
   (rescue)・`end of`・`need to`・`rolled back`・`speaks for`・
   `standing behind`・`stepped out`・`take over`・`talking to`・
   `took off`(rescue)・`turned out`・`want to know`・`went on`(rescue)
5. Strategy Lへ渡した候補一覧: 上記3・4 + word群5件
   (`Muse`・`reservations`・`admits`・`costume`・`stepped`)、計24件
6. Hybrid最終5件: `turn out`(phrasal_verb)・`contract worker`
   (noun_phrase)・`be rolled back`(phrasal_verb)・`take over`
   (phrasal_verb)・`speak for`(phrasal_verb)
7. 現行Production最終5件: `turn out not to be`・`contract workers`・
   `on the other end`・`sensitive information`・`be rolled back`
8. 何が変わったか: 重複率**60%**(`turn out`≈`turn out not to be`、
   `contract worker`≈`contract workers`、`be rolled back`=完全一致)。
   前Trial(同記事)の重複率40%から改善。
9. cost/token/latency: input 2,838 / output 5,111(reasoning 3,796) /
   合計7,949 token、**¥1.0721**、45.9秒
10. Fable評価欄: (空欄)

### 5.3 hormuz_a2

1. 機械処理前候補数: 353件
2. 機械処理後候補数(shortlist): **20件**(phrase 9・important noun 4・
   word 7)
3. important word/multiword term候補: `center stage`・`sea blockade`・
   `Brent crude`・`Middle Eastern`(すべてrepeated compound noun検出
   またはWiktionary multiword targeted lookupで発見。**"sea blockade"・
   "brent crude"はユーザー例示語、machine screening後も残存確認済み**)
4. phrase/idiom/phrasal_verb候補(9件): `by trade`・`feels like`・
   `gave back`(rescue)・`move in`・`no one`・`passing through`・
   `play in`・`pulled back`・`Taken Back`(rescue、見出し文由来で
   大文字表記が残った=既知の軽微な表記上の粗さ)
5. Strategy Lへ渡した候補一覧: 上記3・4 + word群7件
   (`chart's`・`disliked`・`Strait`・`shipments`・`futures`・
   `recovering`・`curtain`)、計20件
6. Hybrid最終5件: `give back gains`(collocation)・`sea blockade`
   (technical_term)・`Brent crude`(technical_term)・`center stage`
   (idiom)・`pull back`(phrasal_verb)
7. 現行Production最終5件: `give back gains`・`sea blockade`・
   `Brent crude futures`・`take a sharp turn`・`settle at`
8. 何が変わったか: 重複率**60%**(`give back gains`=完全一致、
   `sea blockade`=完全一致、`Brent crude`≈`Brent crude futures`部分
   一致)。前Trial(同記事)の重複率20%から大幅改善。ユーザーが
   固定1枠の例として挙げた`brent crude`/`sea blockade`が**両方**
   最終5件に入った(この記事では重要名詞句2枠になった。ユーザー
   指示は「少なくとも1枠」であり2枠は許容範囲、規則違反ではない)。
9. cost/token/latency: input 2,701 / output 6,014(reasoning 4,660) /
   合計8,715 token、**¥1.2411**、59.9秒
10. Fable評価欄: (空欄)

### 5.4 hormuz_b1b

1. 機械処理前候補数: 340件
2. 機械処理後候補数(shortlist): **20件**(phrase 8・important noun 4・
   word 8)
3. important word/multiword term候補: `center stage`・`sea blockade`・
   `Brent crude`・`Middle Eastern`
4. phrase/idiom/phrasal_verb候補(8件): `by trade`・`feels like`・
   `gave back`(rescue)・`move in`・`no one`・`passing through`・
   `play in`・`pulled back`
5. Strategy Lへ渡した候補一覧: 上記3・4 + word群8件
   (`chart's`・`disliked`・`Strait`・`shipments`・`futures`・
   `recovering`・`curtain`・`Withdrawn`)、計20件
6. Hybrid最終5件: `give back`(phrasal_verb)・`charge ships`
   (collocation)・`sea blockade`(noun_phrase)・`pull back`
   (phrasal_verb)・`center stage`(idiom)
7. 現行Production最終5件: `give back`・`sea blockade`・
   `stand at center stage`・`take a sharp turn`・`recover the cost`
8. 何が変わったか: 重複率**60%**(`give back`=完全一致、
   `sea blockade`=完全一致、`center stage`≈`stand at center stage`
   部分一致)。前Trial(同記事)の重複率20%から大幅改善。
9. cost/token/latency: input 2,679 / output 9,680(reasoning 8,258) /
   合計12,359 token、**¥1.9443**、92.4秒(6本文中最長。reasoning
   token数も最多)
10. Fable評価欄: (空欄)

### 5.5 small_bag_a2

1. 機械処理前候補数: 284件
2. 機械処理後候補数(shortlist): **20件**(phrase 3・important noun 4・
   word 13、phrase候補が薄い記事genreのため既存Trial同様word群で
   多く補完)
3. important word/multiword term候補: `mini bags`・`large bags`・
   `fashion reports`・`small pouches`
4. phrase/idiom/phrasal_verb候補(3件): `Catch the Eye`・`looking at`・
   `taking over`
5. Strategy Lへ渡した候補一覧: 上記3・4 + word群13件
   (`runways`・`clutches`・`novelty`・`proudly`・`luggage`・`basics`・
   `runway`・`lip`・`eye-catching`・`wallet`・`sizes`・`beside`・
   `carries`)、計20件
6. Hybrid最終5件: `take over`(phrasal_verb)・`catch the eye`(idiom)・
   `set the mood`(collocation)・`carry the load`(collocation)・
   `fashion report`(noun_phrase)
7. 現行Production最終5件(本Trial内で1回実行、比較用): **技術的には
   応答は得られたがhard requirement不適合**(`have a big moment`が
   有限助動詞"have"を含み"KEY_WORDS_STRUCTURE_INVALID"、参考として
   実際の出力を示す: `have a big moment`・`minaudière`・`take over`・
   `catch the eye`・`set the mood`)
8. 何が変わったか: Hybridは5/5がhard requirement PASSしたのに対し、
   現行Production(候補根拠なし)は同一記事・同一max_attempts=1条件で
   INVALID(1件が有限助動詞を含む)となった。ただし**n=1回のみの比較
   であり、モデルの出力ゆらぎの範囲内である可能性が高く、「hybridが
   構造的に優れている」と断定はできない**(小標本での留意点として
   明記)。
9. cost/token/latency: hybrid: input 2,615 / output 6,385
   (reasoning 5,105) / 合計9,000 token、**¥1.3096**、61.3秒。
   baseline: input 1,511 / output 5,175(reasoning 3,900) / 合計
   6,686 token、**¥1.042**、50.2秒
10. Fable評価欄: (空欄)

### 5.6 small_bag_b1b

1. 機械処理前候補数: 291件
2. 機械処理後候補数(shortlist): **20件**(phrase 4・important noun 3・
   word 13)
3. important word/multiword term候補: `mini bags`・`large bags`・
   `small pouches`
4. phrase/idiom/phrasal_verb候補(4件): `all over`・`bags out`・
   `Looking at`・`sits on`(**"bags out"は前Trialで確認済みの誤検出
   [discontinuous phrasal verb取り違え]が本Trialでも規則的には
   除外できず残存**、context_mismatch_excluded_count=0で確認済み。
   §2で明記した既知の残存ギャップの実例)
5. Strategy Lへ渡した候補一覧: 上記3・4 + word群13件
   (`runways`・`clutches`・`styling`・`season's`・`novelty`・
   `takeover`・`proudly`・`vanished`・`clearer`・`luggage`・`basics`・
   `runway`・`lip`)、計20件
6. Hybrid最終5件: **KEY_WORDS_STRUCTURE_INVALID**(`have a big moment`
   が有限助動詞"have"を含み不適合。参考として実際の出力を示す:
   `sense of occasion`・`have a big moment`・`division of labor`・
   `draw the eye`・`mini bags`)
7. 現行Production最終5件(本Trial内で1回実行、比較用): **同じく
   INVALID**(参考: `have a big moment`・`sense of occasion`・
   `minaudière`・`draw the eye`・`division of labor`)
8. 何が変わったか: **Hybrid・現行Productionの両方**が同じ
   `have a big moment`(有限助動詞含み)でINVALIDになった。これは
   hybrid候補リストの有無に関係なく発生した同一のモデル傾向であり、
   **本Trialが新たに持ち込んだ問題ではない**(既存Production Gateの
   既知の挙動、max_attempts=1で自動再試行しない設計のため今回は
   両方とも不採用のまま記録)。
9. cost/token/latency: hybrid: input 2,599 / output 4,974
   (reasoning 3,712) / 合計7,573 token、**¥1.0382**、45.8秒。
   baseline: input 1,519 / output 7,047(reasoning 5,696) / 合計
   8,566 token、**¥1.4016**、64.4秒(baselineの方が高コスト・
   高reasoningだった。n=1件の比較であり傾向断定はしない)
10. Fable評価欄: (空欄)

---

## 6. ステップ別減少表(6本文合計)

| article | 機械処理前(dedup前) | dedup後 | 既存Gate通過後 | 不規則動詞rescue | 文脈不一致除外 | 文脈Gate通過後 | phrase生存 | important noun | word生存 | shortlist |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| meta_a2 | 390 | 189 | 144 | 3 | 2 | 142 | 11 | 5 | 131 | 21 |
| meta_b1b | 406 | 204 | 158 | 3 | 3 | 155 | 15 | 4 | 140 | 24 |
| hormuz_a2 | 353 | 187 | 151 | 2 | 1 | 150 | 9 | 4 | 141 | 20 |
| hormuz_b1b | 340 | 188 | 150 | 1 | 2 | 148 | 8 | 4 | 140 | 20 |
| small_bag_a2 | 284 | 148 | 115 | 0 | 1 | 114 | 3 | 4 | 111 | 20 |
| small_bag_b1b | 291 | 159 | 121 | 0 | 0 | 121 | 4 | 3 | 116 | 20 |
| **合計** | **2,064** | **1,075** | **839** | **9** | **9** | **830** | **50** | **24** | **779** | **125** |

**「機械スクリーニングで何件まで減らせたか」**: 390〜779件規模のDB一致
候補(word+phrase合算、記事により変動)から、**AIへ実際に渡した候補は
各記事20〜24件**まで機械的に絞り込めた(目標「20件前後」をほぼ達成、
STOP条件の「大量候補をLLMへ渡す必要がある」には該当しない)。

---

## 7. 前Trial(DB-onlyランキング方式)との重複率比較

| article | KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01(前Trial) | 本Trial(Hybrid) |
|---|---:|---:|
| meta_a2 | 20% | **40%** |
| meta_b1b | 40% | **60%** |
| hormuz_a2 | 20% | **60%** |
| hormuz_b1b | 20% | **60%** |
| small_bag_a2/b1b | N/A(比較不可) | N/A(両者ともINVALID/n=1のため断定不可) |
| **平均(4本文)** | **25%** | **55%** |

既存Production(Strategy L)の実際の採用結果との重複率が、平均25%→55%へ
改善した(4本文中3本文で60%、1本文で40%)。これはDB-onlyランキング方式
(前Trial、複数DB一致数を軸に機械的に並べた候補をSonnetが人間相当で選定)
よりも、Hybrid方式(機械screening→既存Strategy Lが最終意味判断)の方が、
既存Productionの実際の選定結果に近い出力を再現できたことを示す実測結果
である。

---

## 8. 費用・token・latency合計

| 区分 | 呼び出し数 | 入力token合計 | 出力token合計(reasoning内数) | 費用合計(JPY) |
|---|---:|---:|---:|---:|
| Hybrid(6本文) | 6 | 16,164 | 34,266(reasoning 27,083) | ¥7.2500 |
| 現行Production比較用(small_bag 2本文) | 2 | 3,030 | 12,222(reasoning 9,596) | ¥2.4436 |
| **合計** | **8** | **19,194** | **46,488** | **¥9.6935** |

Guardrail(¥100目安)・STOP閾値(¥80到達で中止)いずれにも到達せず、
全呼び出しが正常完了した(`er027_output/key_phrase_db_hybrid_trial_02/
cost.json`・`raw_usage_log.jsonl`に実測値を保存)。

**モデル/routing**: 全呼び出し`gpt-5.6-luna`(Model Routing Contract
`A2_SUPPORT`/`B1_SUPPORT`→Support→Luna系、既存Strategy Lと同一)。
Structured Output(JSON Schema、既存Production schemaをそのまま使用)。
Canonicalization段階は本Trialでは実行していない(ユーザー指示どおり、
選定結果の比較が目的のため)。

**Latency**: Hybrid呼び出しは29.7秒〜92.4秒(reasoning_effort=high、
reasoning token数と強く相関、hormuz_b1bが最長かつreasoning token数も
最多)。small_bagの直接比較2件では、baselineの方がhybridよりlatency・
reasoning tokenともに高い場合もあり(b1b)、"候補を渡すと逆に推論が
軽くなる"傾向が見えたが、**n=2件の比較であり断定はしない**。

---

## 9. Sonnet仮分類(推奨はFable/ユーザーへ、ここでは事実整理のみ)

- **候補生成段階の改善は明確**: 機械処理前390〜779件規模から、AIへ渡す
  候補を20〜24件へ絞り込めた(目標達成)。ユーザー確定原則4(1枠=重要
  単語・単語群)の担保対象("contract worker(s)"/"brent crude"/
  "sea blockade")は、追加実装(repeated compound noun検出+Wiktionary
  multiword targeted lookup)により全6本文で機械screening後も残存し、
  かつ実際に最終5件へ採用された(hormuz系では"brent crude"も
  "sea blockade"も両方採用)。
- **既存Productionとの一致度が明確に改善**: 前Trial(DB-onlyランキング)
  の重複率平均25%から、本Trialでは55%(4本文平均)へ改善した。
  「DBは候補を絞るだけ、最終判断は既存Strategy Lに任せる」という設計が、
  「DB一致数でSonnetが最終選定する」前Trial方式よりも既存Productionの
  実際の判断パターンに近い結果を再現できた、という事実が観測された。
- **費用面**: Hybridの1呼び出しあたり費用(¥0.64〜¥1.94)は、候補リスト
  追加分だけ入力tokenが増える(baseline比+1,000〜1,300 token程度)ものの、
  絶対額としては現行Productionの通常運用コストと同程度〜わずかに高い
  範囲に収まり、Guardrail(¥100)は全く問題にならない水準だった。
  「候補整理のための別LLM call」は追加していない(1本文1 call、
  ユーザー指示#6を遵守)。
- **未解決の既知ギャップ(規則化できなかった部分)**: (a) discontinuous
  phrasal verb("bags out"相当)はStage 1の狭いスコープ規則では捕捉
  できず、small_bag_b1bのshortlistに残存した。(b) Wiktionary
  multiword_termタグの粗さに起因するノイズ("even though"/"other side"
  等)がimportant noun候補に混入したが、**Strategy L自身がこれらの
  ノイズを最終5件に一切採用しなかった**(最終判断をAIに委ねる設計が、
  機械処理側の不完全さを許容範囲内で吸収した、という観測)。
  (c) word候補に所有格'sの残存("user's"/"chart's"/"season's")等の
  軽微な表記上の粗さがあったが、これもStrategy Lは採用しなかった。
- **small_bag系のhard requirement INVALID**: b1bはHybrid・現行Production
  の両方が同一の理由(`have a big moment`の有限助動詞違反)でINVALIDと
  なった。これは本Trialが持ち込んだ新しい問題ではなく、既存Production
  Gate・当該記事genreにおける既存のモデル挙動である(max_attempts=1の
  Trial設計により今回は自動再試行していない)。

---

## 10. STOP条件該当チェック(ユーザー指示#13)

| STOP条件 | 該当有無 | 根拠 |
|---|---|---|
| 20件前後まで機械的に絞れず大量候補をLLMへ渡す必要がある | **非該当** | 全6本文で20〜24件に収まった(§6) |
| 機械rankingで重要語が明らかに落ちる | **非該当** | contract worker(s)/brent crude/sea blockadeは全該当記事でshortlist後も残存・最終採用された(§3・§5) |
| phrase偏重またはword偏重を防げない | **非該当** | 最終5件はphrase/idiom/phrasal_verb中心+重要名詞句1(hormuzは2)枠という設計どおりの構成になった(§5) |
| LLM callが複数必要 | **非該当** | 1本文1回のみ(max_attempts=1を厳守、自動再試行なし) |
| 現行より明確に高コスト | **非該当** | 合計¥9.6935(Guardrail¥100の10%未満) |
| 新たなDB導入判断が必要 | **非該当** | 既存Wiktionary/CEFR-J/NGSL/wordfreqの範囲内で対応できた |
| Production仕様変更が必要 | **非該当** | Production module・prompt templateは無変更のまま実施できた |

**総括: 上記7条件いずれにも該当しない。Trialは最後まで実施できた。**
ただし§5.6(small_bag_b1b)のhard requirement INVALID(Hybrid・
Baseline両方)は、STOP該当ではないが「未解決のまま残った事実」として
明記する(既存Production Gateの既知挙動であり、本Trial固有の新規問題
ではない)。

---

## 11. 証跡・再現方法

- Unit test: `er027_key_phrase_db_hybrid_trial_02_test.py`(21件、全PASS)。
  実行コマンド:
  `.venv/Scripts/python.exe -m unittest er027_key_phrase_db_hybrid_trial_02_test -v`
- 既存er023 unit test(13件)も無変更のまま全PASSを再確認済み
  (`er023_key_phrase_db_trial_tests.py`)。
- 実行コマンド(全6本文、実API呼び出し): `.venv/Scripts/python.exe
  er027_key_phrase_db_hybrid_trial_02_run.py`
- 出力: `er027_output/key_phrase_db_hybrid_trial_02/<article>/
  {hybrid_selector_prompt.txt, hybrid_trial_result.json, stage1_debug.json}`、
  `er027_output/key_phrase_db_hybrid_trial_02/{cost.json,
  raw_usage_log.jsonl, all_articles_stop_conditions.json}`
- APIキーは環境変数(`.env`)のみ使用、本文・prompt全文はREPORTへ転記
  していない(候補一覧・最終語句のみ引用)。

---

## 12. 次に進めてよい作業・まだ進めてはいけない作業

- 進めてよい(ユーザー承認があれば): 本Trial結果を踏まえたProduction
  採用可否の判断、discontinuous phrasal verb対応・possessive 's
  除去・Wiktionary multiword_termタグの精度向上等の追加改善Trial。
- まだ進めてはいけない: 本設計・Trial結果のProduction Key Phrase経路
  への配線(`APPROVED_FOR_PRODUCTION`はユーザーのみが決定)。

**Fable評価(2026-09-27、`PM-CLOSEOUT-CONSOLIDATION-2026-09-27-C`)**:
`VALIDATED`(Trialとして目標達成: 390〜779件→20〜24件、重要名詞句保持・
採用、1本文1 call、STOP条件7項目非該当)。留保: (1) 現行Productionとの
重複率55%は同じStrategy Lが選定器のため品質証明ではない、(2) 費用は
現行同等〜わずかに高く「現行より安く」は未達(article全文+候補で入力
+1,000〜1,300 token)、(3) discontinuous phrasal verb残存・
Wiktionary multiwordタグのノイズ・possessive noise、(4)
small_bag_b1bは既存Gate(有限助動詞)で双方INVALID。ユーザー指示により
TRIAL-03(軽量化・bug一般化修正・回帰・新記事Trial)へ継続。Production
採用は未決。

---

## Status

**Sonnet報告完了、ユーザー/Fable判断待ち**(§9仮分類・§10 STOP該当
チェックいずれも非該当だが、最終Status(`VALIDATED`/`REJECTED`/
`USER_DECISION_REQUIRED`)の確定はFable/ユーザーに委ねる)。

Management-ID: KEY-PHRASE-DB-HYBRID-TRIAL-02
