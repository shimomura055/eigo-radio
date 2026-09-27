# KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05_REPORT

管理ID: KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05
日付: 2026-09-27
実行層: Sonnet(sandwich方式)
**Status: 仮分類 USER_DECISION_REQUIRED(確定はFable/ユーザー)。Trial成功
でもAPPROVED_FOR_PRODUCTIONではない。Production配線は一切行っていない。**

---

## 0. 目的・スコープ

`KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01`(以下Family Z
Trial)で発見した「Family Z固有ではなくCore共通の候補生成品質課題」2件
(word bucket ranking、multiword/idiom lookup)+ユーザー指示の3点目
(proper noun/dialogue tag除外の明示化)を、Family Z向け特殊化ではなく
共通Core(候補生成段階)の一般的な品質改善として実装し、Family X
(既存12本文)を悪化させずにFamily Z(Melos)側の課題を改善できるかを
確認した。

新規ファイル: `er032_key_phrase_db_hybrid_core_v2_trial_05_stage1.py`
(V2-1/V2-2/V2-3の実装本体)、`er032_key_phrase_db_hybrid_core_v2_trial_05_run.py`
(12+1本文orchestration)、`er032_key_phrase_db_hybrid_core_v2_trial_05_test.py`
(unit test、22件・全PASS)。出力: `er032_output/key_phrase_db_hybrid_core_v2_trial_05/`。

`er029_*`(Trial-04 baseline、commit `57b61273`)・`er030_*`(Production
Core、別Agentが並行作業中)・`er028_*`/`er027_*`・`er003_key_words_*`は
**すべてimport/読み取りのみ、無変更**。

---

## 1. 既存資産照合(Existing Spec / Prior Trial Check Gate)

| 論点 | 分類 | 根拠 |
|---|---|---|
| word bucket rankingが屈折形バイアスでloyaltyを押し出す | **B(Family Z Trialで発見済み、Core共通問題と判定済み、未修正)** | `KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01_REPORT.md` §4-2「Coreの`word_survivors_sorted`ランキング方式そのものの一般的な弱点」。本Trialが修正対象。 |
| Wiktionary multiword lookupが重要idiom(in someone's place相当)を拾えない | **B(同Trialで発見済み、未修正)** | 同REPORT §4-3「Core側のlookup候補選定ロジック・budget配分の見直しが必要」。本Trialが修正対象。 |
| proper noun/dialogue tag除外が偶然のzipf閾値頼み | **B(同Trialで発見済み、観測のみ)** | 同REPORT §4-4「意図的な固有名詞除外設計ではなく偶然の副産物」。本Trialが明示的機構を新設する対象。 |
| `apply_exclusion_gate`の`proper_noun`項目 | **A(既存仕様、`rule_determined: False`固定)** | `er023_key_phrase_db_extraction.apply_exclusion_gate`は固有名詞判定を「規則では判定不能」として観測のみ返す設計(無変更のまま)。本Trialはer023自体を変更せず、er032側の後段フィルタとして新設した。 |

---

## 2. V2実装(3点、いずれも一般化・Family Z固有hardcodeなし)

### V2-1. word bucket ranking改善

`_lemma_normalized_word_rarity_key`: 表層形+lemma候補群(既存
`ext.lemma_candidates_for_word`、既存er015 `lemma_candidates_v2`を無変更
のまま再利用)の中で最も高いzipf頻度を採用する。既存lemma化ロジックが
`hurried→hurry`のような「子音+y→ied」型過去形を生成できないギャップは、
ranking専用の一般規則(`_extra_lemma_candidates_for_ranking`、英語綴り
規則の一般知識)で補った。新DB追加なし(既存wordfreq+既存lemma化の範囲内)。

実データ確認(Melos): "hurried"(生zipf3.14)→lemma正規化後4.14(hurry)、
"executions"(3.44)→4.29(execution)等、�ែ屈折形の見かけ上の低頻度が解消
された。ただし実データで判明した点として、デバイアス後も"whispered"/
"ruler"/"punish"/"shouted"/"hurried"の5語が**genuineに**loyaltyより
稀であったため、固定word_min=5枠からloyaltyがちょうど1位差で漏れる境界
ケースが残った(§3-1参照)。

### V2-2. multiword/idiom lookup改善

1. **代名詞プレースホルダ照合**(`match_candidate_with_pronoun_
   placeholder_rescue`): Wiktionary辞書のidiom見出しが可変スロット
   (代名詞)を`one's`/`one`/`someone`/`someone's`で表す一般的な辞書慣習
   (実データ確認: ローカルWiktionary idiom dumpに`"one's place"`が存在)
   を利用し、本文中の実際の代名詞(his/her/my等)をプレースホルダへ機械
   置換したバリアントで追加照合する。表示・validator照合は本文中の実際
   の表現のまま変更しない(既存`irregular_verb_rescue`と同じ設計方針)。
2. **lookup優先順位付けの改善**(`select_unmatched_ngram_candidates_
   for_lookup_v2`): 代名詞スロットを含む候補だけを小さな予約枠
   (既定15、budgetの小部分)で優先し、残りは既存v1と同じ順序
   (len昇順→content語数降順→アルファベット順)で埋める。

   **実装中に発見・修正した重大な設計ミス**: 当初案は「前置詞・助詞
   (in/on/back/over等)で始まる/終わる候補」も優先シグナルに含めていたが、
   実データ検証(hormuz_a2)でこの形状が2-3gram候補全体528件中162件
   (31%)を占めるほど粗く、budget=60を優先候補だけで埋め尽くして既存の
   良い候補("Brent crude"、v1では528件中12位で楽にbudget内だった)を
   budget外へ完全に押し出す**regressionを引き起こすことが判明**した。
   このため前置詞シグナルは不採用とし、より狭く再現性の高い「代名詞
   スロット」シグナルのみを、小さく固定した予約枠で使う設計へ修正した。
   修正後は回帰テスト(`test_lookup_priority_does_not_crowd_out_
   existing_good_candidate`)でBrent crudeが再びbudget内に入ることを
   固定確認している。

### V2-3. proper noun / dialogue tag除外の明示化

`compute_proper_noun_signals`: 本文全体から各token(小文字key)ごとに
(a) 小文字出現の有無、(b) 文頭以外での大文字始まり出現回数、
(c) 会話attribution動詞(said/asked/replied等の一般リスト、個別作品の
hardcodeではない)への隣接、を集計する。

- **Fix B(1-gram、DB不一致専用経路)**: 既存v1のガード(小文字出現が
  一度もない語は対象外)を維持した。実データ検証の結果、より一般化した
  「文頭以外の大文字始まり2回以上」基準に差し替えると、記事中**1回しか
  出現しない固有名詞**(Dionysius等)を誤って許してしまうことが判明した
  ため(v1のガードの方が的確だった)、Fix Bはv1のまま維持し、新しい
  `is_proper_noun_like`は他の2経路にのみ適用した。
- **word_survivors(DB一致語)**: `is_proper_noun_like`(小文字出現なし+
  文頭以外の大文字始まり2回以上)を適用。実データで"Muse"(Meta記事の
  AI機能の固有名詞)・"echo"(twinsのキャラクター名、一般語"echo"と同形)
  が正しく除外されることを確認した。
- **会話タグ形状(dialogue-tag-shape)の複合名詞2-3gram**
  (`find_repeated_compound_noun_candidates_v2`): 候補が「固有名詞らしい
  語+会話attribution動詞」の隣接構成である場合のみ除外する(固有名詞を
  含むという理由だけでは除外しない)。これにより"Brent crude"のような
  既存の真の技術複合語(会話attribution動詞を含まない)を保護しつつ、
  "echo said"/"mara said"を正しく除外できることを実データ(twins_a2)で
  確認した。

**安全策(実装中に発見した副作用と対策)**: 「文頭以外の大文字始まり」を
単純に1回でも検出したら固有名詞とみなす初期案は、引用符内発話冒頭の語
(例: `Then Melos shouted, "Wait!"`の"Wait"、既存の文分割[Fix A、カンマ
は文境界にしない]の都合上「文頭以外」扱いになる)を誤って固有名詞と
判定するfalse positiveを実データで引き起こした。この安全策として、
「文頭以外の大文字始まりが2回以上」を要求する(登場人物名は記事中で
繰り返し出現するという一般的性質を根拠にする)ことでこの偶然を除外した。

新しいDB(有料辞書・大規模コーパス等)・新規pip依存は一切導入していない。

---

## 3. v1 vs v2 比較(実データ、実LLM実行)

### 3-1. Family Z(Melos)

| 項目 | v1(Family Z Trial Z0、既存artifact再利用) | v2(本Trial、新規実行) |
|---|---|---|
| `loyalty`が候補生成段階へ復帰したか | **No**(word bucket枠から漏れ、LLMに一度も提示されず) | **Yes**(shortlistの候補一覧に`loyalty`が実際に出現、`lightweight_selector_prompt.txt`で確認済み) |
| `in someone's place`相当が候補化されたか | **No** | **Yes**(`his place`がpronoun_placeholder_rescueで`one's place`[Wiktionary idiom]に一致し、idiom候補として出現) |
| structural status(公式1回目、attempt=1) | PASS | **INVALID**(§3-3参照、原因分析あり) |
| 最終5件(公式1回目) | fair trial / execution / my word / fall to / come back | fair trial / my word / let me go / come back / at last |
| 既存Production KP一致 | 2/5(execution, fair trial) | 2/5相当(fair trial一致、他は言い回し違い) |
| cost | ¥1.5112 | ¥0.8305 |

`loyalty`・`in someone's place`相当がいずれも**候補生成段階(shortlist)
へ復帰した**ことは実データで確定した(item 1/2の主目的達成)。ただし
公式1回目のLLM選定ではどちらも最終5件には選ばれず(候補はあるが選定は
LLMの裁量、既存設計どおり)、さらに公式1回目はsource_sentenceの引用符
二重ラップにより構造INVALIDとなった(§3-3)。診断目的の追加1サンプル
(下記)では`in one's place`・`give one's word`が実際に選ばれており、
候補復帰の実効性(選ばれ得ること)を補強する参考証跡として記録する。

### 3-2. 診断用追加サンプル(公式比較には使わない、structural INVALID
原因切り分けのため+2 call、`docs/pm`ではなくこのREPORTにのみ記録)

| 項目 | melos診断#2 | twins_a2診断#2 |
|---|---|---|
| status | INVALID(同一原因、後述) | **PASS** |
| 最終5件 | in one's place / give one's word / let me go / fair trial / step forward | take over / digital twin / repair office / open the door / **sit up** |
| 既存Production KP一致 | in one's place・give one's word・fair trial = 3/5相当 | take over・digital twin = 2/5 |

twins_a2は診断#2でPASSし、Trial-04と同じ核心語(sit up含む)を再現した
(§3-3で後述するとおり、公式1回目のINVALIDは単発サンプルの書式ゆらぎで
あったことを裏付ける)。melosは診断#2でも同一原因(quote二重ラップ)で
INVALIDだったが、`in one's place`(=`in someone's place`相当)・
`give one's word`という、Family Z Trialのer031では一度も候補にすら
現れなかった2語が**実際に最終選定された**ことは、item 1/2の改善効果を
裏付ける追加証跡である。

### 3-3. structural INVALIDの原因分析(公式1回目: twins_a2, melos)

いずれも「LLMがsource_sentence値に、SENTENCE REFERENCEの表示形式
(`Sx: "text"`)由来の引用符を二重に付け足して返した」ことによる
substring不一致が原因であり(例:
`"Her digital twin appeared in the mirror"`のように実際の本文には
存在しない外側の引用符が付与された)、**v2の候補生成ロジック(V2-1/
V2-2/V2-3)自体に起因する不具合ではない**ことを確認した。根拠:
- twins_a2は診断用の同一候補セットでの再サンプルでPASSした(§3-2)。
- melosの2サンプルとも、失敗した項目に含まれない候補(fair trial等)は
  正しく引用符なしで返っており、問題は特定候補の内容ではなく出力書式の
  ゆらぎである。
- この失敗パターンは、Fix A(引用符を閉じた発話単位認識、er029由来・
  無変更)がsentence unit内に残す「発話境界の片割れの引用符」
  (例: `wedding," he said`)という**v1と共有の既存アーキテクチャ特性**
  に起因しており、v1のFamily Z Trial(Z0/Z1)・Trial-04(twins_a2)は
  たまたま1回のサンプルでこの書式ゆらぎを踏まなかっただけである
  可能性が高い(単発サンプルの既知limitation、Family Z Trial REPORT
  §4-6で既出の「揺らぎを統計的に区別できない」という限界と同種)。

この単発サンプル脆弱性(quote-heavyな引用符主体の記事で顕在化しやすい)
は、v1/v2共通のプロンプト書式(`SELECTION_GUIDANCE`・Fix Aのsentence
unit構成)に起因するものであり、**本Trialのスコープ(Core候補生成層)
の外**にある表示・出力書式の課題として、未解決事項に記録する
(§7参照、修正は行っていない)。

### 3-4. Family X(既存12本文、v1=Trial-04既存artifact再利用、v2=新規実行)

| article | v1 shortlist | v2 shortlist | v1 status | v2 status | v1 cost(¥) | v2 cost(¥) | 既存KP一致(v1→v2) |
|---|---:|---:|---|---|---:|---:|---|
| meta_a2 | 22 | 23 | PASS | PASS | 1.1222 | 1.1100 | N/A |
| meta_b1b | 24 | 25 | PASS | PASS | 1.3080 | 0.9231 | N/A |
| hormuz_a2 | 20 | 20 | PASS | PASS | 1.1096 | 1.2203 | N/A |
| hormuz_b1b | 20 | 20 | PASS | PASS | 0.9399 | 0.9302 | N/A |
| small_bag_a2 | 20 | 20 | PASS | PASS | 1.1059 | 1.2760 | N/A |
| small_bag_b1b | 20 | 20 | PASS | PASS | 2.0284 | 1.5383 | N/A |
| wake_a2 | 20 | 21 | PASS | PASS | 0.8684 | 0.9408 | 2/5 → 2/5 |
| wake_b1b | 20 | 20 | PASS | PASS | 0.8861 | 1.3201 | 3/5 → 3/5 |
| aihiring_a2 | 21 | 22 | PASS | PASS | 0.7246 | 0.9227 | 1/5 → 1/5 |
| aihiring_b1 | 20 | 20 | PASS | PASS | 0.7710 | 1.0058 | 2/5 → 2/5 |
| twins_a2 | 20 | 20 | PASS | **INVALID**(§3-3、診断再サンプルでPASS確認) | 0.8780 | 1.6220 | 2/5 → 3/5相当(公式サンプル) |
| twins_b1 | 20 | 20 | PASS | PASS | 1.0738 | 1.6099 | 3/5 → 3/5 |
| **合計** | **247** | **252** | **12/12 PASS** | **11/12 PASS(1件は書式ゆらぎ、§3-3)** | **¥12.8159** | **¥15.2497** | — |

**X側候補プール regression チェック**(公式1回目のstage1候補プール、
LLM選定前の機械生成候補一覧)では、Trial-04の全12本文・最終5件相当語
(合計60項目)のうち、v2候補プールから消えていたのは0件だった(初回
実装のlookup優先順位付けバグでは"Brent crude"が一時的に消えたが、
§2で修正・§3-4の数値は修正後のもの)。既知bug A(discontinuous phrasal
verb false positive)・bug C(possessive noise)の再発は12本文全件で
確認されなかった。

---

## 4. cost・API call実測(合計、Guardrail¥70)

| 区分 | 内容 | cost(¥) |
|---|---|---|
| 初回実装(lookup優先順位付けバグ混入版)の無駄になった7 call | meta_a2/meta_b1b/hormuz_a2/hormuz_b1b/small_bag_a2/small_bag_b1b/wake_a2(§2のバグ発見・修正前に実行、修正後に同じ7本文を再実行したため二重計上) | 7.0484 |
| 修正後の正式run(13本文、X12+Melos、公式1回目) | 本REPORT §3の比較表の元データ | 15.2497 |
| 診断用追加サンプル(twins_a2・melos各1回、§3-2、structural INVALID原因切り分け目的) | 公式比較には使わない | 2.5126 |
| **合計** | | **24.8107** |

Guardrail¥70・事前STOP閾値¥60のいずれにも抵触していない。API call数
=7(無駄)+13(正式)+2(診断)=22回、うち正式比較に使うのは13回
(1本文1 call、`max_attempts=1`)。全call、article全文非送信assertion
(`base.assert_no_full_article_body`)を通過済み。使用モデルは
`er006_model_routing_contract_01.require_model`経由で強制取得
(Approved Model外の使用なし)。

**無駄になった7 callの理由**: lookup優先順位付けの初期実装(前置詞
シグナルを優先枠に無制限に含める案)が実データ検証前にrun.pyへ組み込ま
れており、最初の通し実行の途中(hormuz以降)で回帰チェックにより
"Brent crude"消失を発見し、優先順位付けロジックを修正した上で全体を
再実行した(§2参照)。修正前の7本文分の呼び出しは結果的に不要になった
が、Trialの通常の実装→検証→修正サイクルの一部であり、ユーザー指示の
「候補選定の質改善を優先(単純なbudget増で解決しない)」を遵守した
結果として発生したコストである。

---

## 5. 既知bug A〜E再発チェック

| # | チェック項目 | 結果(v2、12本文) |
|---|---|---|
| A | discontinuous phrasal verb false positive(bags out/move in/play in) | 再発なし |
| C | possessive noise(user's等) | 再発なし(word_survivors確認) |
| D | important noun phrase bucket精度 | contract worker/sea blockade/Brent crude/digital twinはいずれもv2候補プールで保持(§3-4) |
| E | small_bag「have a big moment」 | Production module無変更のため既存どおり(本Trialでは変更していない) |
| B | Wiktionary multiword粗さ(even though等) | 個別確認は省略(既存の観測事項、本Trialのスコープ外の既知limitation) |
| 会話タグFP(twins) | `echo said`/`mara said`が候補プールから正しく除外されたことを実データ・unit testで確認(V2-3の主目的達成) | 解消(§2参照) |

---

## 6. STOP条件チェック

| STOP条件 | 該当有無 | 根拠 |
|---|---|---|
| 新DB追加が必要 | 非該当 | 既存wordfreq/CEFR-J/Wiktionary/NGSLの範囲内(§2) |
| 追加LLM callが必要 | 非該当 | 1本文1 call厳守(診断用+2 callは公式比較に使わない別枠として明示、§3-2/§4) |
| Production module変更が必要 | 非該当 | er029/er030/er028/er027/er003_key_words_*すべて無変更 |
| Family X v1 baselineを変更しないとTrialできない | 非該当 | er032は新規ファイルに閉じ、v1は既存artifact再利用のみ |
| 大幅なcost増 | 非該当 | 合計¥24.8107、Guardrail¥70・STOP閾値¥60未達 |
| 重要な既存KP regression | 非該当 | §3-4で候補プールregressionチェック済み、0件消失(初回バグは修正済み) |
| 新しい大規模仕様変更が必要 | 非該当 | word_min=5→6の小幅パラメータ調整(既存の公開引数の値変更のみ、§3-1)を除き、新規メカニズムの追加はしていない |
| 素材不足 | **該当(部分)** | Family Z本文はMelos(A2)1本のみ(既存Family Z B1B・追加Fiction本文はer026/er013に存在しない、grep確認済み)。ユーザー指示どおり新規記事生成は行わず「既存素材不足」として報告する |

いずれもSonnetの判断ではSTOP対象の事象は発生していない。素材不足のみ
該当し、指示どおり新規記事生成はせず報告に留めた。

---

## 7. 未解決事項・限界

1. **word_min=5→6のパラメータ調整**(§3-1): lemma正規化後もgenuineに
   稀な語が5個ちょうど存在する記事では、loyalty相当の語が固定5枠から
   わずかに漏れる境界ケースが残る。本Trialではer027.build_shortlistの
   既存公開引数`word_min`を6へ小幅に拡張して救済したが(shortlist総数
   +1語程度、STOP閾値30件には遠く及ばない)、この値の一般化・最適値は
   Fable/ユーザー判断が必要。
2. **単発サンプルのstructural INVALID脆弱性**(§3-3): quote-heavyな
   記事(Melos、twins)で、LLMがsource_sentenceへ引用符を二重に付け足す
   書式ゆらぎが観測された。v1/v2共有のプロンプト書式・Fix A設計に起因し
   Core候補生成ロジック(本Trialのスコープ)とは独立した課題であり、
   修正は行っていない。Production採用検討時は、この単発サンプル脆弱性
   への対応(既存Production既定のmax_attempts=2相当のリトライ許容、
   または表示書式の見直し)を別途検討する必要がある。
3. **Wiktionary/MediaWiki API接続の間欠的timeout**: 本Trial実行中に
   複数回、live API呼び出しがネットワークtimeoutで失敗した(既存
   `er023_key_phrase_db_ingest`の再試行ロジックはHTTPError 429のみ
   対象で、汎用timeoutは対象外)。本Trialでは都度再実行で対応したが、
   Production運用時の耐障害性は本Trialのスコープ外。
4. **lookup優先順位付けの予約枠サイズ(15)**: 実データ1記事(hormuz_a2)
   の回帰確認のみで決めた値であり、他記事・他ジャンルでの汎化性は未検証。
5. 素材不足(§6)により、Family Z側の検証はMelos A2の1本文のみに基づく
   (統計的一般化はできない)。

---

## 8. Production採用時の影響範囲(共有Core[er030]差し替えが必要か)

もしFable/ユーザーがCore v2の採用(APPROVED_FOR_PRODUCTION化)を決定
する場合、Production Core(`er030_key_phrase_db_hybrid_core_01.py`、
Family X本番配線済み)は現在er029(v1)のロジックを無変更のまま複製した
ものであるため、Core v2採用にはer030の該当関数(word bucket ranking・
multiword lookup候補選定・複合名詞候補生成)の差し替えが必要になる。
影響範囲: `er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`
(既存equivalence testの前提=「er029と一字一句同一」が崩れるため、
テスト自体の再設計が必要)、Family X本番運用中の全記事のKey Phrase
選定結果が変化しうる(regression計画: 本Trialと同様にX既存本文群での
再比較、既存Production公開KPとの一致率変化の追跡が必要)。**本Trialでは
er030への変更は一切行っていない**(Production配線禁止の指示どおり)。

---

## 9. Status仮分類(Sonnet仮判定、確定はFable/ユーザー判断)

Item 1(word bucket ranking)・Item 2(multiword/idiom lookup)・Item 3
(proper noun/dialogue tag除外)はいずれも実データで改善効果を確認した
(loyalty・in someone's place相当の候補復帰、Brent crude等の既存候補
保持、echo said等の会話タグFP解消)。一方、(a) 実装過程で発見した
lookup優先順位付けの重大バグ(修正済みだがコスト超過を招いた)、
(b) X側1本文(twins_a2)・Z側(Melos)でstructural INVALIDが発生した
(原因はCore候補生成ロジックとは別の単発サンプル書式ゆらぎと分析済み
だが確定的な保証ではない)、(c) word_min調整という小幅だが新規の
パラメータ変更を伴った、という3点があり、Sonnetは`VALIDATED`とは
断定せず、`USER_DECISION_REQUIRED`を提案する。

判断が必要な論点:
- structural INVALID(twins_a2・melos)を「Core候補生成ロジックとは
  独立した単発サンプルの書式ゆらぎ」という分析で納得できるか、追加
  検証(複数回サンプル)を求めるか。
- word_min=5→6のパラメータ調整を許容範囲内の設計判断とみなすか。
- Family Z側の検証がMelos 1本文のみである点(素材不足)を踏まえ、
  Production採用判断を追加のFamily Z記事が揃うまで保留するか。

**Production配線は一切行っていない**(er030・Family X/Z Production
Key Phrase生成経路のいずれにも本Trialのコードは配線されていない)。

---

## 10. 証跡・再現方法

### 10-1. Unit test(実行済み、全PASS)

```
.venv/Scripts/python.exe -m unittest er032_key_phrase_db_hybrid_core_v2_trial_05_test -v
→ 22件、全PASS

.venv/Scripts/python.exe -m unittest er027_key_phrase_db_hybrid_trial_02_test er028_key_phrase_db_hybrid_trial_03_test er029_key_phrase_db_hybrid_trial_04_test -v
→ 70件、全PASS(v1 baseline無変更の回帰確認)
```

### 10-2. 実行コマンド(正式run、13本文、実API呼び出し)

```
.venv/Scripts/python.exe er032_key_phrase_db_hybrid_core_v2_trial_05_run.py
```

出力: `er032_output/key_phrase_db_hybrid_core_v2_trial_05/{x_<article>,
z_melos}/{lightweight_selector_prompt.txt, hybrid_core_v2_trial_result.json,
stage1_debug.json}`、`{cost.json, raw_usage_log.jsonl,
all_articles_stop_conditions.json, v1_reference_x_readonly.json,
v1_reference_melos_readonly.json}`。

### 10-3. 共有ストア非書込み確認

Strategy L呼び出しは`run_production_selection_gate`(既存関数、無変更)
をvalidatorとしてのみ使用し、pronunciation ledger/master audio store/
human_review_queue/telemetry等への書き込みAPIは別途呼び出していない
(コードレビューによる確認。他Agentの並行作業により当該ファイルの
mtimeが本Trial実行前後で変化しているため、mtime比較では本Trial由来か
判別できず、設計上の非呼び出しであることをコードで確認する方法を
採用した)。

---

## Status

**Sonnet報告完了、Fable/ユーザー判断待ち(§9仮分類・判断が必要な論点
参照)。Production配線なし。**

Management-ID: KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05
