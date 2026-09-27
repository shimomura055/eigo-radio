# KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06 REPORT
# Phase B: Trial実装+検証(候補ID方式)

管理ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06
作成: Sonnet 5、2026-09-28
Phase A(設計レビュー)は`docs/pm/design_kp_source_reference_contract_01.md`
(2026-09-28作成、Fableが§14の推奨案(iii)候補ID方式を採用、以下
「B改良版」)。本REPORTはPhase B(Trial実装+実データ検証)の結果。

---

## 1. Fable設計レビュー結果・採用contract

設計書§13-14の比較表・推奨に基づき、Fableは以下を決定した(委任文より):

**B改良版(候補ID方式+非ブロッキングの取り違え検知)**:
1. selector schemaから`source_sentence`/`source_span`を除去し、
   `source_candidate_id`(enum=当該呼び出しのshortlist候補ID`C1..Cn`の
   み)を必須化。LLMに本文文字列を一切書かせない。
2. 決定論的復元: 候補ID → Stage 1候補データ(`surface_form`/
   `context_sentence_id`)から、`source_span`=候補の`surface_form`、
   `source_sentence`=`sentence_reference[context_sentence_id]`(最初の
   出現文)を復元。
3. 取り違え検知(非ブロッキング): `surface_echo`(短いsurface文字列)を
   schemaに追加し、復元結果と正規化比較して不一致なら
   `candidate_mismatch_suspected=true`をtelemetryに記録するのみ
   (validatorには使わない、STOPさせない)。
4. 復元後は既存Production validator(`p2g.validate_min_unit_selection`)・
   canonicalization・Source Consistency Gate(`er003_key_phrase_source_
   gate_01`相当ロジック)を無変更で通す。
5. (iv)validator寛容化は今回実装しない(Production変更のため)。

---

## 2. 実装

新規ファイル(すべてTrial layer、Production/v1 baseline/v2は無変更・
read-only import):

- `er034_key_phrase_db_hybrid_source_reference_contract_trial_06_contract.py`
  — 候補ID付与(`assign_candidate_ids`)、派生schema構築
  (`build_item_schema_properties`/`build_json_schema`、既存
  `p2g._ITEM_SCHEMA_PROPERTIES`から`source_span`/`source_sentence`を
  除去し`source_candidate_id`(enum)/`surface_echo`を同位置に追加)、
  候補ID方式prompt構築(`build_lightweight_user_message`、候補行へ
  `id: Cx`を追加、旧`SELECTION_GUIDANCE`の「source_sentenceをそのまま
  使用」指示を候補ID選定指示へ差し替え)、API呼び出し
  (`make_instrumented_selector_factory`、既存er030と同じ計測
  パターン)、候補ID解決+復元(`restore_source_fields`)、薄いgate
  オーケストレーション(`run_source_reference_contract_gate`
  = 既存`p2g.parse_selector_json`→復元(新規)→既存
  `p2g.validate_min_unit_selection`→既存Source Gate相当チェック
  `er030..._verify_source_spans_against_raw_article`を再利用)。
- `er034_key_phrase_db_hybrid_source_reference_contract_trial_06_run.py`
  — v1(`er029`stage1)/v2(`er032`stage1)いずれもラップする実行
  エントリポイント(`run_stage1_and_shortlist_v1_wrap`/`_v2_wrap`)、
  Family X 12本文+Melos A2のprepare/呼び出し/cost tracking。
- `er034_key_phrase_db_hybrid_source_reference_contract_trial_06_test.py`
  — 21件のunit test(API呼び出しなし、schema構造・候補ID解決の
  決定論性・複数候補の復元規則・取り違え検知・v1/v2ラップ構造・
  article全文非送信assertionを検証)。全件PASS。

### 実装修正1回目(実データで発見、API再呼び出しなしで修正・再検証)

初回実行時、Family X 12本文中4本文(meta_a2/meta_b1b/hormuz_b1b/
aihiring_b1)とMelos A2(v1/v2すべてのサンプル)がvalidatorの
「source_spanがsource_sentence内に存在しない」で`KEY_WORDS_STRUCTURE_
INVALID`になった。原因調査の結果、既存共有Stage1
(`er027_key_phrase_db_hybrid_trial_02_stage1.find_repeated_compound_
noun_candidates`、480行)の`important_noun_phrase_candidate`カテゴリ
(`repeated_compound_noun_heuristic`)で、候補dictの`source_span`
フィールドが実際には「短い句」ではなく「その句が最初に出現した文
全体(コンマ除去済み)」を保持していることが判明した(例:
`source_span`="In some calls through Muse trained contract workers
made the calls not AI"、実際のcandidateは"contract workers")。この
フィールドは旧来の自由記述契約では一切参照されない内部フィールドで
無害だったが(LLMが`source_sentence`/`source_span`を自由生成していた
ため)、候補ID契約でこのフィールドをそのまま復元源にするとvalidatorが
落ちることが実データで判明した。

設計書§3(b)・§14は元々「`surface_form`を復元源にする」ことを推奨して
おり、この推奨どおりに`restore_source_fields`の実装を修正した
(`source_span = candidate["surface_form"]`、既存Stage1コード自体は
無変更)。修正後、Family X 13本文(v2)の全shortlist(274候補、選定
対象の5件だけでなく全候補)を対象にオフライン(API呼び出しなし)で
`surface_form`が`context_sentence_id`が指す文に実在するかを機械監査し、
**274/274件で不整合0件**を確認した。さらに、修正前にINVALIDだった
8件(meta_a2/meta_b1b/hormuz_b1b/aihiring_b1の各1件+melos_a2 v2の
3サンプル+melos_a2 v1の1件)について、**既存の生モデル応答
(`source_candidate_id`/`surface_echo`)をそのまま再利用し、追加API
呼び出しゼロで**復元ロジックのみ再実行したところ、8/8件が
`KEY_WORDS_STRUCTURE_PASS`に変わった(Source Gate raw照合も全件PASS)。
この再検証は本Trialの予算(¥18.2707、Guardrail¥40・STOP閾値¥35)を
一切消費していない。

---

## 3. 検証結果(実データ、実際にAPIを呼び出した19 call分)

対象: Family X 12本文(既存Trial-04/05と完全同一パス)+ Melos A2
(Family Z、quote-heavy、既知失敗事例、er032_run.pyと同一パス)。

| 区分 | 本文数×サンプル | call数 | 
|---|---|---|
| v2ラップ(Family X 12 + Melos A2) | 13本文×1サンプル | 13 |
| v1ラップ(比較用、twins_a2・melos_a2) | 2本文×1サンプル | 2 |
| 反復安定性(twins_a2・melos_a2をv2ラップで追加) | 2本文×2追加サンプル | 4 |
| **合計** | | **19** |

### 3-1. structural PASS率

**修正後: 19/19 = 100% `KEY_WORDS_STRUCTURE_PASS`**(修正前の初回実行では
13/19、6件がINVALID。§2参照)。

### 3-2. 候補ID解決・取り違え検知・Source Gate(19 call、選定item合計95件)

| 指標 | 実測 |
|---|---|
| 候補ID解決失敗(enum外/unresolved) | 0/95 |
| `candidate_mismatch_suspected`(surface_echo不一致、非ブロッキング) | 0/95 |
| Source Gate raw article照合missing | 0/19 call(全件) |

`surface_echo`による取り違え検知は今回の実データでは1件も発火しな
かった(実害率0%、ただしサンプル数19 callに限られる)。

### 3-3. quote-heavy安定性(twins A2・Melos A2、既知失敗事例)

| 記事 | wrap | サンプル数 | status |
|---|---|---|---|
| twins_a2 | v1 | 1 | PASS |
| twins_a2 | v2 | 3(s1/s2/s3) | 全件PASS |
| melos_a2 | v1 | 1 | PASS(修正後) |
| melos_a2 | v2 | 3(s1/s2/s3) | 全件PASS(修正後) |

Trial-05で確認されていたtwins_a2の引用符二重ラップによる
`KEY_WORDS_STRUCTURE_INVALID`(設計書§0)は、候補ID方式では
**構造的に発生しない**(LLMがsource_sentence/source_spanを一切
書かないため)ことを実データで確認した。3サンプルとも選定結果は
ほぼ同一(digital twin/take over/audition/open the door/repair
office の組み合わせがサンプル間で安定、rankの入れ替わりのみ)。

### 3-4. cost・token比較(Trial-04/05比)

| 項目 | Trial-04(v1、12本文) | Trial-05(v2、13本文=X12+Melos) | Trial-06(v2、13本文=X12+Melos、候補ID契約) |
|---|---|---|---|
| 合計cost | ¥12.8159 | ¥15.2497 | ¥12.4537(s1のみ、13本文) |
| 1本文平均 | ¥1.068 | ¥1.173 | ¥0.958 |

候補ID契約はcostを増加させていない(むしろ13本文合計で約18%減、
ただしreasoning token数のrun毎ばらつきの範囲内であり、契約変更
そのものによる系統的な削減と断定はできない)。promptはSENTENCE
REFERENCE表を維持しつつ各候補行へ`id: Cx`を1個追加しただけであり、
article全文は元々含まないためtoken数は同等〜微減という設計書の
事前評価(§14)と整合する。

### 3-5. phrase比率・重要語保持(Trial-04/05基準との比較)

19 call・95 itemの`phrase_type`内訳: phrasal_verb 28・idiom 21・
word 19・noun_phrase 18・technical_term 7・collocation 2。

既存Production採用済みKey Phrase(Trial-04/05 REPORT記載の
`EXISTING_PRODUCTION_KP`)との文字列完全一致overlapは、Family X本文で
1〜4/5件、Melos A2で1〜3/5件(サンプルにより変動)。この変動幅は
Trial-04/05でも既に観測されていたLLM選定の自然なばらつきと同水準
であり、候補ID契約への切り替えが選定の多様性・質を損なっている
兆候は見られない。

### 3-6. 受入条件との対応表

| 受入条件 | 結果 |
|---|---|
| 引用符・空白・句読点コピー揺らぎでINVALIDにならない | 達成(LLMが本文文字列を一切書かないため構造的に発生しない) |
| canonical対応が決定論的 | 達成(候補ID→surface_form/context_sentence_idは同一入力に対し常に同一出力、unit test`test_deterministic_restoration_same_input_same_output`で確認) |
| quote-heavy(twins A2・Melos A2)安定 | 達成(4記事×計8サンプル全件PASS、§3-3) |
| v1 regressionなし | 達成(v1ラップ2本文とも既存挙動と同じくPASS) |
| v2改善を壊さない | 達成(v2ラップ13本文とも修正後PASS、選定内容もTrial-05相当の傾向を維持) |
| bug A〜E(Trial-05既知課題)再発なし | 引用符二重ラップ(bug由来のINVALID)は再発なし。今回のTrialで**新たに発見**したのは「候補ID契約特有」の課題(§2の`source_span`フィールド誤用、Stage1側の既存潜在不整合)であり、bug A〜Eそのものの再検証は本Trialのスコープ外(選定候補自体はStage1無変更のため据え置き) |
| 1本文1 call | 達成(全19 callとも1本文(1サンプル)につき1 selector call、max_attempts相当のリトライなし) |
| 全文非送信 | 達成(`assert_no_full_article_body`を全promptで実行、unit test含む) |
| costが増えない | 達成(§3-4) |
| Human Review/STOPを通常系にしない | 達成(19/19 PASS、STOP発火なし) |

---

## 4. v1/v2への影響

- v1(`er029`)/v2(`er032`)いずれのStage1・Production `er030`・
  Production validator(`p2g`/`prod`)・v1 baseline・Source Gateは
  **一切変更していない**(read-only importのみ)。
- 候補ID契約は既存のどちらの選定層にも同一の薄いwrapperとして適用
  できることを実データで確認した(v1ラップ2本文・v2ラップ13本文
  ×最大3サンプル、計19 call)。

---

## 5. Production(`er030`)適用時に必要な変更範囲・migration(参考、未実装)

本Trialの結果を踏まえた場合に、将来Production適用を検討するなら
必要になる変更(**今回は一切実装していない、Fable/ユーザーの別途
判断が必要**):

1. `er030_key_phrase_db_hybrid_selector_01.py`のprompt構築
   (`build_lightweight_user_message`)・schema
   (`prod.SELECTOR_JSON_SCHEMA`由来)を、本Trialの
   `er034_..._contract.build_lightweight_user_message`/
   `build_json_schema`相当のものへ差し替える。
2. `run_db_hybrid_selection`のgate呼び出し部分を、`prod.run_
   production_selection_gate`(parse直後にvalidateする一体型)から、
   本Trialの`run_source_reference_contract_gate`相当(parse→候補ID
   解決・復元→validate)へ差し替える。
3. **migration**: 既存artifact(`keywords_canonicalized.json`等)は
   無変更のまま(復元後の`source_sentence`/`source_span`は既存
   フィールドと同じ意味論の文字列になるため、下流
   canonicalization/Redundancy QA/Source Gate/reading copyは無変更で
   動作する、設計書§10で確認済み)。追加で`source_candidate_id`
   (今回のitem dictに含まれる`resolved_candidate_id`相当)を新規
   フィールドとしてartifactへ保持しておけば、監査時の追跡性が
   上がる。
4. §2で発見した「`repeated_compound_noun_heuristic`カテゴリの
   `source_span`フィールドの意味論不整合」は、Production適用前に
   Stage1側(`er027`/`er030`共有コード)を見直すか、Trial層と同様に
   `surface_form`を復元源として使う実装を徹底する必要がある(**今回は
   Trial層の実装選択で回避しており、Stage1自体は変更していない**)。

---

## 6. unresolved・要ユーザー判断の論点(USER_DECISION_REQUIRED候補)

- **取り違え率**: 本Trialの実測(95 item中0件)では`candidate_mismatch_
  suspected`は発火しなかったが、サンプル数(19 call)は量産規模
  (数百〜数千記事)に対して小さく、実際の取り違え発生率は未確定の
  ままである(設計書§12(c)の指摘どおり)。
- **複数出現の意味差**: 同一candidate(同一canonical_form)が記事内に
  複数回出現し、出現ごとに意味・ニュアンスが異なる稀なケースは、
  「最初の出現文」固定の復元規則では検出できない(設計書§5・本
  Trialでも新規の実データ確認はしていない、既存の制約を維持する
  だけ)。
- **`repeated_compound_noun_heuristic`カテゴリのsource_spanフィールド
  意味論不整合**(§2): 今回はTrial層で`surface_form`を使うことで
  回避したが、Stage1側のフィールド命名自体(`source_span`が実際には
  「文全体」を指す)は既存の潜在的な混乱要因であり、Production適用
  時やStage1保守時に再度同種の実装ミスを誘発するリスクがある。
  Stage1側のフィールド名・意味論の整理(例:
  `context_sentence_full_text`のような別名への変更)は、Production
  `er030`・v1 baseline `er029`・v2 `er032`すべてに影響する変更に
  なるため、本Trialのスコープ外(Trial層の変更のみで許可された範囲)
  として、ユーザー/Fableの判断を仰ぐ論点として明記する。
- v1 Production(`er030`)への適用可否・タイミングは、設計書§11の
  とおり本Trial-06の結果を踏まえてFable/ユーザーが別途判断する
  (本REPORTでは提案(§5)のみ、実装・Production配線はしていない)。

---

## 7. STOP条件該当の有無

大規模schema変更・migrationのProduction互換性破壊・追加LLM call常設・
新DB・新しい大きな仕様判断・v1 baseline書き換えのいずれも発生して
いない。Guardrail¥40・STOP閾値¥35に対し実測合計¥18.2707(46%)で
完了しており、費用超過によるSTOPも発生していない。§2の実装修正
(source_span→surface_form切り替え)は、設計書§14が既に推奨していた
内容への実装修正であり、新しい仕様判断ではない(Fable既承認の設計
方針の範囲内)。

**STOP該当なし。**

---

## 8. Status仮分類(確定はFable)

**VALIDATED**(Trial実装として)。候補ID方式(B改良版)は:
- quote-heavy記事(twins A2・Melos A2)を含む全19 callでstructural
  PASS率100%を達成し、Trial-05までの引用符コピー由来の
  `KEY_WORDS_STRUCTURE_INVALID`を構造的に解消した。
- 既存Production validator・canonicalization・Source Gateを一切
  変更せずに実現できることを実データで確認した。
- costを増加させず、選定内容の多様性・質もTrial-04/05相当を維持
  している。
- v1(`er029`)/v2(`er032`)いずれの選定層にも同一のwrapperとして
  適用できることを確認した。

一方で、Production(`er030`)への適用は別途独立した意思決定であり
(§5参照)、§6の未解決論点(取り違え率の量産規模での実測、Stage1
フィールド意味論の整理)が残るため、**Production配線の可否・
タイミングはUSER_DECISION_REQUIRED**として引き続きユーザー/Fableの
判断を仰ぐ。

---

## 9. 実行環境・証跡

- 実行: `.venv/Scripts/python.exe er034_key_phrase_db_hybrid_source_
  reference_contract_trial_06_run.py`
- 出力: `er034_output/key_phrase_db_hybrid_source_reference_contract_
  trial_06/`(記事別`source_reference_contract_trial_result_s{1,2,3}.
  json`、`cost.json`、`raw_usage_log.jsonl`、`all_articles_summary.
  json`、`trial06_aggregate_analysis.json`)
- unit test: `.venv/Scripts/python.exe -m unittest er034_key_phrase_
  db_hybrid_source_reference_contract_trial_06_test -v`
  (21件、API呼び出しなし、全件PASS)
- 費用: 実測合計¥18.2707(19 call、Guardrail¥40・STOP閾値¥35未達)。
  APIキーは環境変数(`.env`経由の`OpenAI()`既定読み込み)のみ使用。
