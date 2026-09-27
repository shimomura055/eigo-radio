# KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01_REPORT

管理ID: KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01
日付: 2026-09-27
実行層: Sonnet(sandwich方式)
**Status: 仮分類 USER_DECISION_REQUIRED(確定はFable/ユーザー)。
Production配線は一切行っていない。Trial成功でもAPPROVED_FOR_PRODUCTION
ではない。**

---

## 0. 目的・スコープ

Family X向けCommon DB Hybrid Core(`er029_key_phrase_db_hybrid_trial_04_*`、
baseline = commit `57b61273`)が、Fiction/Story系のFamily Zでも有効かを
確認する。以下3点への回答が主目的:

1. Core自体は共通利用できるか。
2. Family Zに必要なのはCore変更ではなく、最終選定Prompt/weight/category
   priorityの差分だけで済むか。
3. X側のProduction仕様を壊さず「共通Core + Family別最終選定ルール」構成
   が成立するか。

er029(Core baseline)・er028/er027・er003_key_words_*は**無変更**
(read-only import)。新規コードは`er031_key_phrase_db_hybrid_family_z_
trial_01_{run,rules,test}.py`のみ。共有ストアへの書込みなし
(`er006_output/{audio_retry_cascade_prod_01/human_review_queue.jsonl,
master_audio_store_01/manifest.json}`のmtime実行前後で不変を確認)。

---

## 1. 既存資産照合・素材

- Family Z実データ: `er026_output/family_z_production_e2e_01/melos/
  run_01/article.md`(383語、A2レベル、Public Domain文学「走れメロス」
  英語リライト、既にAPPROVED_FOR_PRODUCTIONのrights方針下で生成済み)。
  レベル分岐(A2/B1B)は存在せず単一レベルのみ(article_config.json
  `source_level: "A2"`)。
- 既存Family Z Production公開Key Phrase(参考比較用、`key_phrases/
  keywords_canonicalized.json`由来、変更なし):
  `in someone's place / execution / give one's word / fair trial /
  loyalty`。生成方式は現行Family Z Production(=**article全文をそのまま
  1 callで送る方式**、strategy_id "L"、model gpt-5.6-sol、reasoning
  effort high)であり、Hybrid Core(shortlist方式)ではない。
- 参考(dialogue-heavy、Family C twins、新規実行なし・読み取り専用):
  `er029_output/key_phrase_db_hybrid_trial_04/{twins_a2,twins_b1}/
  hybrid4_trial_result.json`(Trial-04で既に生成済みのartifactを再利用)。

---

## 2. Z0/Z1設計

- **Z0(Core無変更)**: `er029_key_phrase_db_hybrid_trial_04_run.
  run_one_article`(Trial-04の本番run関数、無変更)をそのまま呼ぶ。
  Stage1(quote-aware sentence segmentation+rare single word候補)・
  Wiktionary multiword lookup・shortlist構築・selector prompt文言
  (`SELECTION_GUIDANCE`)は全てCoreのまま。
- **Z1(Family Z固有選定ルール)**: Stage1/shortlist生成は`run4.
  run_stage1_and_shortlist_v4`(Z0と同一関数、無変更)を再利用し、
  最終選定LLMへ渡すprompt文言の末尾(`SELECTION_GUIDANCE`相当)だけを
  `er031_..._rules.FAMILY_Z_SELECTION_GUIDANCE`へ差し替えた。差分は
  3点のみ:
  (a) 本文がFiction/Storyであることの明記、
  (b) phrase/idiom/phrasal verb区分からの最低選定数を1→2に引き上げ
     (category priority、候補不足時は1まで緩和可)、
  (c) 候補一覧に無い登場人物名を選ばない旨の明記。
  候補一覧(shortlist)自体の中身・並び順はZ0/Z1で完全に同一であることを
  unit testで確認済み(`test_z0_and_z1_share_identical_candidate_
  sections_only_guidance_differs`)。

実行: `.venv/Scripts/python.exe er031_key_phrase_db_hybrid_family_z_
trial_01_run.py`。実API call = Melos 1本文 × 2条件 = **2 call**
(各条件`max_attempts=1`、既存`run_selector_once`/`run_production_
selection_gate`を無変更のまま再利用)。

---

## 3. 実行結果

| 項目 | Z0 | Z1 |
|---|---|---|
| structural status | KEY_WORDS_STRUCTURE_PASS | KEY_WORDS_STRUCTURE_PASS |
| attempts | 1 | 1 |
| stop_conditions | なし | なし |
| shortlist_total | 20 | 20(Z0と同一candidate set) |
| 最終5件 | fair trial / execution / my word / fall to / come back | give one's word / execution / fair trial / come back / fall into |
| 既存Production KPとのoverlap | 2/5(execution, fair trial) | 3/5(execution, fair trial, give one's word) |
| cost | ¥1.5112 | ¥1.0471 |

合計費用: **¥2.5583**(Guardrail¥30、STOP閾値¥25に対し未到達)。

既存Production KP(`in someone's place / execution / give one's word /
fair trial / loyalty`)のうち、Z0/Z1いずれも**`in someone's place`と
`loyalty`を一度も選べなかった**(候補にすら無かった、§4-2/4-3)。

参考(twins、既存artifact、新規実行なし): twins_a2の既存Production KP
5件中Trial-04最終選定との一致は2/5(digital twin, take over)。Melosと
同様に「既存KPの上位重要語のうち一部がHybrid Coreでは再現できない」
傾向が別記事でも観測されており、単発記事固有の偶然ではない可能性を
示唆する(確定的な統計的結論ではない、参考情報)。

---

## 4. 評価項目別の結果と切り分け

### 4-1. structural PASS

PASS(Z0/Z1とも)。5件ちょうど、rank1-5整合、1-5語、完全文/節排除、
source_sentence照合、いずれもhard requirement違反なし。

### 4-2. important term保持(loyalty)

**Core共通部の問題**。`loyalty`はStage1のexclusion gateを正しく通過し
`word_survivors`に含まれていた(zipf 4.17)が、shortlist構築時の
word bucket順位付け(`_word_rarity_key`、生wordfreq zipf昇順)により、
`hurried`(zipf 3.14)/`executions`(3.44)/`whispered`(3.44)/`shouted`
(3.78)/`lowered`(3.86)/`smiled`(3.86)/`punish`(3.95)/`shaking`(4.08)/
`demanded`(4.12)より「一般的」と判定され、shortlistのword bucket枠
(実測5枠)から溢れて**LLMに一度も提示されなかった**(stage1_debug.json
で実測確認)。

原因は屈折形(過去形/複数形)のwordfreq分割による見かけ上の低頻度化
(例: `hurried`は`hurry`の活用形として独立カウントされるため、コーパス
頻度が本来の語の使用頻度より低く出る)であり、Fiction特有の設計ではなく
**Coreの`word_survivors_sorted`ランキング方式そのものの一般的な弱点**
である。ただしFiction(過去形の行動描写語が密集する文体)では発生頻度が
高まりやすい、というジャンル依存の「顕在化しやすさ」の違いはある。

→ Family Z側の最終選定prompt/weight/category priority層は、LLMに
提示された候補の中からしか選べないため、この種の**候補生成前の
取りこぼしを原理的に救えない**。Core側のword bucketランキング方式
(例: CEFR-Jレベルまたはlemma正規化後のzipfを使う等)の変更が必要
であり、**本Trialのスコープ外としてSTOP**(実施せず)。

### 4-3. narrative relevance(in someone's place)

**Core共通部の問題**。`in his place`(→`in someone's place`)は
phrase_survivors・important_noun_candidatesのいずれにも一度も出現
しなかった。Wiktionary multiword lookup(2-3gram、budget=60)は
60候補中1件のみhit(`other side`)であり、この慣用句はlookup対象の
優先順位付け(`select_unmatched_ngram_candidates_for_lookup`、既存
Trial-02仕様、無変更)の中で選ばれなかったか、選ばれても該当ページが
無かった可能性がある(本Trialでは切り分けのためのWiktionary個別
再クエリは追加実施していない、新規API callの節約を優先)。

→ これも候補生成段階(Core Stage1)の欠落であり、Family Z側prompt層
では救えない。Core側のlookup候補選定ロジック・budget配分の見直しが
必要な項目であり、**本Trialのスコープ外としてSTOP**(実施せず)。

### 4-4. dialogue handling / false positive(会話タグ)

Trial-04既知limitation②(`echo said`/`mara said`がimportant_noun_
candidatesに混入)は、**Melosでは再現しなかった**(`melos said`は
本文中に2回出現し閾値`min_repetition=2`を満たすにもかかわらず候補化
されなかった)。原因を追跡した結果、`find_repeated_compound_noun_
candidates`の`_is_real_content_word`(wordfreq zipf >= 2.0の実在語
フィルタ)が、`melos`(zipf 1.92)・`dionysius`(2.56、ただしlowercase
非出現でFix Bガードにも別途該当)・`selinuntius`(zipf 0.0)を偶然
足切りしていたためと判明した。

これは**意図的な固有名詞除外設計ではなく偶然の副産物**であり、
`echo`(twinsのキャラクター名、一般英単語としても十分popularなためzipf
が閾値を超える)のように「一般語と綴りが一致する固有名詞」では
引き続き会話タグFPが混入しうる。ただしTrial-04・本Trialのいずれでも
**最終5件には一度も選ばれていない**(実害は今回もゼロ)。

→ Core共通部の潜在リスク(既知limitation②の一般化)。現状は最終選定
LLMの常識判断が実害を防ぐ非公式なセーフティネットとして機能している
だけであり、構造的な保証ではない。Family Z側prompt層で「候補一覧に
無い登場人物名は選ばない」旨を明記した(Z1 (c))が、これは候補に紛れ
込んだ場合の追加防御であり、根本原因(Stage1側の偶然の足切り)を
解消するものではない。**観測のみ、修正は行っていない(スコープ外)**。

### 4-5. proper noun handling

PASS。Melos/Dionysius/Selinuntiusはいずれも候補化されず(shortlistに
一件も出現せず)、unit test
`test_melos_proper_nouns_not_selected_as_stage1_candidates`で回帰
確認済み。

### 4-6. phrase・idiom quality / category priority weight

Z0・Z1とも最終5件中3件がphrase/idiom/phrasal verb区分から選ばれており
(Z0: my word, fall to, come back / Z1: give one's word, come back,
fall into)、Z1の「最低2個」ルールはどちらの条件でも**自然に満たされて
おり拘束力を発揮していない**(Z0側が既にguidance変更前から3個選んで
いたため)。観測された唯一の差はidiomの正規化品質(Z0の生の`my word`
に対し、Z1は正規化された`give one's word`を選択)だが、**各条件1回
ずつの実行(温度付きLLMの単発サンプル)であり、この差がFamily Z
guidance変更に起因するのか単なる出力の揺らぎなのかを統計的に区別
できない**。追加試行(同条件複数回)なしにZ1のprompt差分が有効だったと
断定することはできない。

### 4-7. general-word偏重

Z0/Z1ともword bucketから選ばれたのは`execution`(既存Production KPにも
含まれるdomain語)のみで、Trial-04既知limitation④(small_bagの
`roomy`/`pouch`/`tote`のような一般語過多)に相当する偏重は本Melos
runでは観測されなかった(単発記事のため一般化はできない)。

### 4-8. 公開・既存KPとの比較(参考)

§3表のとおり、Z0=2/5、Z1=3/5。既存Production方式(article全文を
1 callで送る、high reasoning、gpt-5.6-sol)は`in someone's place`・
`loyalty`という本記事で最も物語理解上重要な2項目を含めて5/5相当の
質を達成しており、本Hybrid Core条件(Z0/Z1)はいずれもこれに届いて
いない。ただし既存Production方式はarticle全文をLLMへ送るためprompt
軽量化(article全文非送信)の利点を持たず、コスト・latencyの比較は
本Trialのスコープでは実施していない(参考情報として明記のみ)。

---

## 5. cost・API call実測

| label | model | cost_jpy |
|---|---|---|
| melos_hybrid4(Z0) | gpt-5.6-luna | 1.5112 |
| melos_z1(Z1) | gpt-5.6-luna | 1.0471 |
| **合計** | | **2.5583** |

Guardrail¥30・STOP閾値¥25に対し未到達。API callは合計2回
(本文1件×2条件、各条件1 call、`max_attempts=1`)。使用モデルは
`er006_model_routing_contract_01.require_model("A2_SUPPORT", ...)`
経由で`SUPPORT_MODEL`(gpt-5.6-luna)を強制取得しており、Approved Model
外の使用はない。

---

## 6. (1)(2)(3)への回答

**(1) Core自体は共通利用できるか?**
構造的にはYES。Fiction本文(引用符混じりの会話・過去形narrative)でも
Stage1(quote-aware sentence segmentation含む)・exclusion gate・
shortlist構築・selector gate・validatorはエラーなく動作し、
`KEY_WORDS_STRUCTURE_PASS`・cost(¥1.0〜1.5/call、Family Xと同水準)・
article全文非送信assertionのいずれも満たした。ただし**出力の質**では、
既存Family Z Production(全文送信方式)と比べ、本記事で最も重要な項目
2件(`in someone's place`/`loyalty`)を再現できておらず、単純な
「共通利用OK」と言い切るには品質面の裏付けが不足している。

**(2) Family Zに必要なのはCore変更ではなく最終選定Prompt/weight/
category priorityの差分だけで済むか?**
本Melos 1記事の実測では**NO(不十分)**。今回発見した2つの主要ギャップ
(§4-2 shortlist word bucket ranking、§4-3 Wiktionary multiword
lookup coverage)は、いずれも**候補がLLMに提示される前に消えている**
ため、Family Z側の最終選定prompt/weight/category priority層では
原理的に救済不可能である。「共通Core + Family別最終選定ルール」という
構成の**最終選定層だけ**で解決できる問題と、**Core側の候補生成層**
まで踏み込まないと解決できない問題が両方存在することが分かった。

**(3) X側のProduction仕様を壊さず「共通Core + Family別最終選定ルール」
構成が成立するか?**
配線・分離の観点ではYES。er031はer029/er028/er027/er003_key_words_*
を一切変更せず(read-only import)、既存69件のregression testは全て
無変更のままPASSし、共有ストアへの書込みも発生していない。「Core
無変更+Family別ルールを独立ファイルへ閉じ込める」という構成パターン
自体はX側Production仕様に影響を与えない。ただし(2)の結果により、
この構成だけでFamily Zの実用品質を満たせるかは**未確定**であり、
Core側改修が必要になった場合にその改修がX側の既存動作にどう影響するか
は別途評価が必要(本Trialでは未検証、スコープ外)。

---

## 7. STOP候補(未実施、Fable/ユーザー判断待ち)

1. **shortlist word bucket rankingの改善**(§4-2)。生wordfreq zipf
   昇順ではなく、CEFR-Jレベルまたはlemma正規化後の頻度を使う等の
   Core Stage1/shortlist構築ロジック変更が必要。新DB追加ではないが
   Core仕様変更に該当するため実施せず。
2. **Wiktionary multiword lookup候補選定・budgetの見直し**(§4-3)。
   `in someone's place`のような重要idiomがlookup対象60件に入らない/
   入っても不一致となるケースへの対応。Core Stage1のlookup候補選定
   ロジック変更に該当するため実施せず。

いずれも「新DB追加や大きなCore仕様変更が必要なら勝手に実施せずSTOP」
というユーザー指示に基づき、設計のみ記録し実装は行っていない。

---

## 8. Status仮分類・next user decision案

**仮分類: USER_DECISION_REQUIRED**(REJECTED/VALIDATEDいずれの確定も
Sonnetの権限外、Fable/ユーザー判断が必要)。

判断が必要な論点:
- 本Trialの結果(2/5〜3/5の既存KP一致、2件のCore共通ギャップ検出)を
  もって「Family Z適用は時期尚早」と判断するか、「まず§7 STOP候補を
  Core側で解消してから再評価する」方針にするか。
- Family Z既存Production方式(全文送信、gpt-5.6-sol、high reasoning)
  を当面維持し、Hybrid Core移行はFamily X限定のまま据え置くか。
- 追加検証(Melos以外のFamily Z記事、複数回試行による揺らぎ排除)を
  行うか。

**Production配線は一切行っていない**(er030_*・Family Z Production
Key Phrase生成経路のいずれにも本Trialのコードは配線されていない)。

---

## 9. 証跡・再現方法

### 9-1. Unit test(実行済み、全PASS)

```
.venv/Scripts/python.exe -m unittest er031_key_phrase_db_hybrid_family_z_trial_01_test -v
→ 11件、全PASS

.venv/Scripts/python.exe -m unittest er029_key_phrase_db_hybrid_trial_04_test er028_key_phrase_db_hybrid_trial_03_test er027_key_phrase_db_hybrid_trial_02_test -v
→ 69件、全PASS(Core無変更の回帰確認)
```

### 9-2. 実行コマンド(実API call、2回)

```
.venv/Scripts/python.exe er031_key_phrase_db_hybrid_family_z_trial_01_run.py
```

出力: `er031_output/key_phrase_db_hybrid_family_z_trial_01/
{z0_melos,z1_melos}/{lightweight_selector_prompt.txt,
hybrid4_trial_result.json|hybridz1_trial_result.json,stage1_debug.json}`、
`er031_output/key_phrase_db_hybrid_family_z_trial_01/
{cost.json,raw_usage_log.jsonl,twins_reference_readonly.json}`。

### 9-3. 実行ログ

```
Loading group1 DBs...
=== melos ===
  stage1: 381->166->165, shortlist=20, hybrid4_status=KEY_WORDS_STRUCTURE_PASS, stops=[], rare_word_final=[], prompt_chars=4474 (article_chars=2138)
=== melos (Z1) ===
  shortlist=20, z1_status=KEY_WORDS_STRUCTURE_PASS, stops=[], prompt_chars=4726 (article_chars=2138)
Done. Total cost JPY: 2.5583
```

### 9-4. 共有ストア非書込み確認

`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`・
`er006_output/master_audio_store_01/manifest.json`のmtimeが実行前後で
不変であることを確認済み(git statusの既存差分は本Trialとは無関係な
並行Agent作業由来であり、本Trialでは触れていない)。

---

## Status

**Sonnet報告完了、Fable/ユーザー判断待ち(§7 STOP候補・§8 next user
decision案)。Production配線なし。**
