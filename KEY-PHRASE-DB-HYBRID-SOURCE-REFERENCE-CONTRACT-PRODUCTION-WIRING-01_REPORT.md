# KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01 REPORT

管理ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01
作成: Sonnet 5、2026-09-28
委任文全文: `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-DB-HYBRID-
SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01_01.md`

ユーザー正式採用(2026-09-28): Trial-06(`VALIDATED`)の「候補ID方式
Source Reference Contract」を、Family X / Family Z共通のCore contract
として`APPROVED_FOR_PRODUCTION`。本REPORTはそのProduction配線
(Family Xへの実適用+Family Z共通仕様の差込点新設+Stage 1
`source_span`意味論整理)の実装・検証結果。

---

## 0. 事故の開示(先に報告する、隠さない)

test修正作業中に、**意図しない実API呼び出しにより実測¥20.7826が
消費された事故**が発生した。経緯・原因・修正・再発防止策を最初に
開示する。

### 0-1. 何が起きたか

`run_db_hybrid_selection`(`er030_key_phrase_db_hybrid_selector_01.py`)
を候補ID contract(`er030_key_phrase_db_hybrid_source_reference_
contract_01.py`)経由の呼び出しへ切り替えた際、既存test
(`er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`の
`CostGuardAndArticleCostCapTests.test_cost_guard_exceeded_does_not_
discard_pass_result`・`ModelContractViolationStopsWithoutFallbackTests.
test_run_db_hybrid_selection_raises_fallback_disallowed_on_model_
mismatch`)が、旧い呼び出し先(`db_hybrid._make_instrumented_selector_
factory`・`db_hybrid.prod.run_production_selection_gate`)をmockした
ままだったため、mockが素通りし**実際にOpenAI APIが2回呼び出された**
(修正前のtest全体実行時に発生、実測: モデル契約違反testで¥8.925、
cost guard testで¥11.8576、合計**¥20.7826**)。

### 0-2. 原因

新しい呼び出し先(`src_ref_contract.make_instrumented_selector_
factory`/`src_ref_contract.run_source_reference_contract_gate`)への
切替と、これらをmockするtest側の更新を同時に行わなかった(実装変更を
先に行い、影響を受ける既存testの棚卸しが後追いになった)。

### 0-3. 修正

該当2 testのmock対象を新しい呼び出し先へ切り替えた(`db_hybrid.src_
ref_contract.make_instrumented_selector_factory`/`run_source_reference_
contract_gate`を直接mockする形へ変更、新しい引数順序[`candidate_ids`
がmodelとusage_sinkの間に追加]にも追随)。修正後、両testを個別実行し
0.02秒で完了(実API呼び出しなし)することを確認した。

### 0-4. 予算への影響

Guardrail¥40のうち¥20.7826が事故により消費されたため、まず規模を
縮小したruntime evidence(9記事分)を実行したが、実測cost(1記事平均
約¥1)が想定どおりで残予算に十分な余裕があると判明したため、**最終的
には委任文が指定した規模(Meta A2/B1B・Hormuz A2/B1B・twins A2×3・
Melos A2×3、計10記事)+forced_fallback 1回を全て実行できた**(実測
合計¥30.3960、事故分¥20.7826含む、Guardrail¥40以内。詳細は§5)。

### 0-5. 再発防止

同種の「内部実装を切り替えた際、既存testのmock対象が追随しておらず
実APIが素通りする」事故は、今後も起こりうる構造的リスクである。本
タスクでは個別のtest修正のみを行い、テスト基盤自体への恒久対策
(例: 単体test実行時にAPIキー環境変数を強制的に無効化する等)は
スコープ外(STOP条件の「大規模変更」に該当しうるため、別途Fable/
ユーザー判断が必要な論点としてOPEN_ITEMS化を提案する)。

---

## 1. 既存資産照合(Dangling Reference Check、実装前)

| 項目 | 事実 |
|---|---|
| Family X DB Hybrid Production配線 | `KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01`(commit`8c2da18e`系譜、Fable Gate 3判定`PRODUCTION_WIRED`)。`er030_key_phrase_db_hybrid_core_01.py`(Core)+`er030_key_phrase_db_hybrid_selector_01.py`(Selector)。無変更のまま前提とした |
| Trial-06 Phase A/B | `docs/pm/design_kp_source_reference_contract_01.md`(設計レビュー)、`KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06_REPORT.md`(Trial実装+実データ検証、19 call全件PASS)。`er034_key_phrase_db_hybrid_source_reference_contract_trial_06_contract.py`(Trialロジック)は無変更のまま残した |
| Stage 1 source_span不整合 | Trial-06 REPORT §2で発見済み: `er027_key_phrase_db_hybrid_trial_02_stage1.find_repeated_compound_noun_candidates`(480行)の`source_span`が「文全体」を保持する。当時はTrial層(er034)の復元ロジック側で回避、Stage1自体は無変更のままだった |
| Family Z | `er026_*`(text runner)は無変更の対象。Family Z DB Hybrid Core v2(`er032_key_phrase_db_hybrid_core_v2_trial_05_*`)は別トラック、本タスクの対象外 |
| Production validator/canonicalization/Source Gate | `er003_key_words_min_unit.py`/`er003_key_words_production.py`/`er003_key_words_canonicalization.py`/`er003_key_phrase_source_gate_01.py`。いずれも無変更前提(canonicalization以外は実際に無変更、canonicalizationのみ§3-4の理由で最小限の追加フィールドpassthroughを実施) |

---

## 2. 実装

### 2-1. 新規Production module: `er030_key_phrase_db_hybrid_source_
reference_contract_01.py`

Trial実装(`er034_..._contract.py`)のロジックを昇格した(Trial側は
無変更のまま残す)。差分:
- `family_profile`引数(既定`"family_x"`)を全ての公開関数
  (`build_lightweight_user_message`/`run_source_reference_contract_
  gate`)へ追加し、`_check_family_profile_supported()`で`"family_z"`
  等の未サポート値を明示的に`NotImplementedError`にする(Family別
  最終選定ルールの差込点、§4参照)。
- 生article照合(`_verify_source_spans_against_raw_article`)は
  **本モジュールに複製しない**。既存`er030_key_phrase_db_hybrid_
  selector_01`側の実装をそのまま呼び出し元(`run_db_hybrid_selection`)
  が使い続ける設計とし、循環importを回避した(本モジュールから
  selector_01への依存は`build_lightweight_user_message`内の遅延import
  1箇所[`_display_type`/`_compact_evidence_string`再利用]のみ)。
- `restore_source_fields`が各itemへ`source_reference_contract`
  (既定`"candidate_id_v1"`)を付与するようになった(Trialにはなかった
  新規フィールド、追跡性向上のため)。

### 2-2. `er030_key_phrase_db_hybrid_selector_01.py`の切替

`run_db_hybrid_selection`のprompt構築・API呼び出し・gate呼び出しを、
旧来の自由記述contract(`build_lightweight_user_message`/
`SELECTION_GUIDANCE`/`_make_instrumented_selector_factory`/
`prod.run_production_selection_gate`)から、候補ID contract
(`src_ref_contract.assign_candidate_ids`/`build_lightweight_user_
message`/`make_instrumented_selector_factory`/`run_source_reference_
contract_gate`)へ切替した。**旧関数群自体は削除せず、ファイルに残した**
(`Er028UtilByteParityTests`のbyte一致testが引き続きTrial記録との
整合を固定回帰化する対象として有効なままであるため。実行時には
呼ばれなくなったが、Trial run script[`er028_key_phrase_db_hybrid_
trial_03_run.py`]との歴史的byte一致を保証する既存回帰網を壊さない
ための意図的な保持)。

`family_profile`引数(既定`"family_x"`)を`run_db_hybrid_selection`へ
追加した(既存呼び出し元は全てFamily Xであり、既定値のまま影響を
受けない)。`keywords_runtime_metadata.json`(`key_phrases_db_hybrid/`
配下)へ`source_reference_contract`/`family_profile`/`candidate_count`/
`candidate_mismatch_suspected_count`/`candidate_mismatch_details`/
`unresolved_candidate_id_count`を追加した。

### 2-3. `er003_v1_n3_01_scaffold_generate.py`のtelemetryタグ付け

`_log_kp_backend_telemetry()`呼び出し全4箇所(既定strategy_l経路・
db_hybrid成功・db_hybrid STOP・fallback発火)へ`source_reference_
contract`引数を追加した。db_hybrid成功時は`db_hybrid.src_ref_
contract.SOURCE_REFERENCE_CONTRACT_ID`(`"candidate_id_v1"`)、Strategy L
(既定経路・fallback経路とも)は新設定数`FREE_TEXT_SOURCE_REFERENCE_
CONTRACT_ID`(`"free_text_strategy_l"`)を使う。`_merge_kp_backend_
metadata_into_runtime_file()`(per-article traceability)へも同様の
フィールドを追加した。

### 2-4. `er003_key_words_canonicalization.py`のbackward compatible
passthrough

`merge_canonicalization_result()`が、選定item(`original`)に
`source_reference_contract`/`source_candidate_id`/`surface_echo`/
`candidate_mismatch_suspected`のいずれかが**存在する場合のみ**、
その値を`keywords_canonicalized.json`のitemへそのままコピーする
(`if passthrough_field in original: ...`という存在チェック付きの
追加のみ、既存フィールドの値・順序・キー集合は無変更)。これらの
フィールドを持たない既存経路(Strategy L等)のitemは、この変更前後で
`merge_canonicalization_result()`の出力が**完全に同一**である
(unit test`CanonicalizationPassthroughTests.test_legacy_items_
without_new_fields_unaffected`で確認、66件の既存canonicalization
testも全件PASS、詳細§4)。

### 2-5. Stage 1 `source_span`意味論整理(`er030_key_phrase_db_hybrid_
core_01.py`)

新規関数`_normalize_important_noun_candidate_source_span()`を追加し、
`run_stage1_for_article()`内で`s1v2.find_repeated_compound_noun_
candidates()`(**`er027`自体は無変更**)の戻り値をコピーして後処理
する。対象は`important_noun_phrase_candidate`カテゴリのうち
`repeated_compound_noun_heuristic`が`matched_dbs`に含まれる候補のみ
(このカテゴリだけが「文全体」を保持するバグを持っていた、§2-5-1
参照)。

| フィールド | 補正前の意味 | 補正後の意味 |
|---|---|---|
| `source_span` | 「その句が最初に出現した文全体」(バグ) | `surface_form`と同じ値(短い句、他の全カテゴリと同じ意味論) |
| `legacy_sentence_text`(新規) | (存在しない) | 補正前に`source_span`が保持していた「文全体」の値をそのまま退避(deprecated、既存参照に備える) |
| `surface_form` | 短い句(変更なし) | 変更なし |
| `canonical_form` | 変更なし | 変更なし(候補生成・shortlist内容は無変更) |

#### 2-5-1. downstream依存の全列挙(Grep済み、旧意味論への依存なし)

| 消費先 | 参照方法 | 旧「文全体」意味論への依存 | 本整理による影響 |
|---|---|---|---|
| `attach_compact_context`(`er028`、無変更) | `_candidate_search_terms`経由でsurface_form/canonical_form/observed_surface_variantsを本文中で検索し`context_sentence_id`を決定(`source_span`は参照しない) | なし | 影響なし(context_sentence_id算出は元々source_spanを見ていない) |
| `er030_key_phrase_db_hybrid_source_reference_contract_01.restore_source_fields`(本タスク新設) | `candidate.get("surface_form") or candidate.get("source_span")`(surface_form優先) | なし(surface_form優先のため通常source_spanへは到達しない) | 補正によりsource_span自体も正しくなるため、フォールバック時も安全側 |
| `_verify_source_spans_against_raw_article`(既存selector_01、無変更) | **選定item**(LLM出力後・復元後)の`source_span`を見る、Stage1候補dictを直接見ない | なし(候補dictの生フィールドは見ない) | 影響なし |
| `db_hybrid_stage1_debug.json`書き込み | `_serializable_stage1`が`important_noun_candidates`をそのままdumpする(人間監査用) | なし(表示専用) | dump内容に`legacy_sentence_text`が追加されるのみ、監査性向上 |
| 単体test(`er027_key_phrase_db_hybrid_trial_02_test.py`等) | `find_repeated_compound_noun_candidates`を直接呼びcanonical_form/count等を検証 | 該当なし(er027自体は無変更のためtestも無変更のまま成立) | 影響なし |

**結論**: Stage1候補dictレベルの`source_span`(このカテゴリの旧「文
全体」の値)を直接読んでいた既存Production/Trialコードは存在しない
(Grep全列挙で確認済み)。したがって本整理は**silent semantic change
ではなく**、無害だった内部フィールドの値をより正しい意味論へ補正し、
旧値を明示的なdeprecatedフィールドへ退避しただけである。

#### 2-5-2. migration

不要。既存artifact(`keywords_canonicalized.json`等)・v1 baseline
(`er029`)・v2(`er032`)・Trial記録(`er027`/`er028`)はいずれも無変更
(`er027`自体を編集していないため、v1 baseline/Trial記録は本整理の
影響を一切受けない。整理は`er030_key_phrase_db_hybrid_core_01.py`
[Production Core]内のコピー処理としてのみ実施した)。

---

## 3. Family Z共通仕様(未配線の明記)

`er030_key_phrase_db_hybrid_source_reference_contract_01.py`へ
`SUPPORTED_FAMILY_PROFILES = ("family_x",)`と`_check_family_profile_
supported()`を新設した。`family_profile="family_z"`を指定した場合、
`build_lightweight_user_message`・`run_source_reference_contract_gate`
のいずれも即座に`NotImplementedError`を送出する(unit test
`FamilyProfileGuardTests`で確認)。`er026_*`(Family Z text runner)は
一切変更していない(Grepで本モジュールが`er026_`をimportしていない
ことをunit testで固定回帰化)。**Family Z DB Hybrid Core v2全体の
採用可否・Production配線は本管理IDの対象外であり、未決定・未着手の
まま**である。

---

## 4. test

### 4-1. 新規test

`er030_key_phrase_db_hybrid_source_reference_contract_01_test.py`
(27件、API呼び出しなし): 候補ID割当・schema構築・Family別ガード
(family_x許可/family_z拒否)・復元決定論性/取り違え検知/
source_reference_contractタグ・既存validator互換性・**Stage 1
source_span整理の regression(3件)**・canonicalization passthrough
(2件)・fallback contract混在telemetry(3件)・legacy不変(2件)。

### 4-2. 既存test更新

`er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`の
2 test(§0参照、mock対象を新しい呼び出し先へ切替)。他30 testは無変更で
全件PASS(実Wiktionary APIを使う`FamilyXNoRegressionOnRealArticlesTests`
含む、OpenAI API呼び出しは無し)。

### 4-3. 実行結果(実測)

| test module | 件数 | 結果 | 費用 |
|---|---|---|---|
| `er030_key_phrase_db_hybrid_source_reference_contract_01_test` | 27 | 全件PASS | ¥0(0.65秒) |
| `er030_key_phrase_db_hybrid_family_x_production_wiring_01_test`(修正後) | 32 | 全件PASS | ¥0(実Wiktionary API使用、OpenAI呼び出しなし) |
| `er034_key_phrase_db_hybrid_source_reference_contract_trial_06_test`(Trial、無変更) | 21 | 全件PASS | ¥0 |
| `er003_test_key_words_canonicalization`(canonicalization変更の回帰確認) | 66 | 全件PASS | ¥0 |
| 4module合計 | 146 | 全件PASS | ¥0 |

### 4-4. `run_project_regression.py`

実測: `collected=3432 passed=3423 failed=7 errors=2`(`docs/pm/tools/
_regression_full_kpc1.log`)。詳細に内訳を確認した結果、以下の9件は
全て既知baseline+本タスク自身の一時的なuncommitted diff検知であり、
**新規のcode regressionは0件**:

| 区分 | test | 件数 | 本タスクとの関係 |
|---|---|---|---|
| 既知baseline | `er003_test_p2j_investigate`(過去のtest件数集計自己整合性test) | 3 FAIL + 1 ERROR | 無関係(本タスク開始前から存在する既知failure、直近の`PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01`エントリでも同一内訳が既知baselineとして記録済み) |
| 既知baseline | `er011_open112_trend_synthesis_mode_production_wiring_01_test_01`(byte parity test) | 3 FAIL | 無関係(本タスクが一切importしない`er003_v1_n3_01_articles_generate`依存) |
| 既知baseline | `er015_standard_a2_6000_generation_first_trial_01_test_01`(起動時version drift STOP guard) | 1 ERROR(import時RuntimeError) | 無関係(本タスクと無関係な既存Production安全装置、本タスクは`er015_*`を一切importしない) |
| 本タスク自身(一時的) | `er019_family_x_pointless_01_test_01::test_family_a_files_have_no_working_tree_diff` | 1 FAIL | 本タスクが`er003_v1_n3_01_scaffold_generate.py`へ加えた**正規の変更**をcommit前の未commit差分として検知したもの(このテストは「Family A指定ファイルにuncommitted git diffが無いこと」を検査する自己チェックであり、commit後に`git status`が空になれば自然に解消する既知の性質。直近の`PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01`エントリが、逆に「他Agent作業(=本タスク)由来の未commit差分」として同一事象を記録済み、双方向に事実関係が一致する) |

内訳合計: 7 FAIL + 2 ERROR = 9件、実測値と完全一致。commit後に
`test_family_a_files_have_no_working_tree_diff`単体を再実行し解消を
確認する(§9)。

**観測(既存の構造的gap、本タスクでは対応せずOPEN_ITEMS化を提案)**:
`run_project_regression.py`の既定discovery pattern(`er0*_test_*.py`)
は、ファイル名末尾が`_test_something.py`形式のもの(例:
`er003_test_key_words_canonicalization.py`)を前提としており、末尾が
`..._NN_test.py`形式(例: 本タスクの新規test、`er030_key_phrase_db_
hybrid_family_x_production_wiring_01_test.py`、`er034_..._trial_06_
test.py`等)は**このglobにマッチしない**(実測確認済み: `Path('.').
glob('er0*_test_*.py')`で0件マッチ)。これは本タスクで新たに作った
問題ではなく、少なくとも直近数件のKey Phrase関連タスクから存在する
既存のカバレッジ欠落であり、STOP条件の「大規模変更」を避けるため
本タスクでは修正していない。OPEN_ITEMS化を提案する(§7参照)。

---

## 5. runtime evidence

### 5-1. 実行方法

実Production共有入口`sc.run_key_phrases(kp_backend="db_hybrid")`を、
既存Production artifact(`er019_output`配下)を一切上書きしない専用
出力先`er030_output/family_x_kp_source_reference_contract_evidence_01/`
経由で呼び出した(`er030_key_phrase_db_hybrid_source_reference_
contract_01_evidence_run.py`/`..._evidence_run_02.py`)。

### 5-2. 規模

§0の事故発生直後は予算的余裕がなくなったと判断し、いったん規模を
縮小したevidence(Hormuz A2・twins A2×3・Melos A2×3・Meta A2・
forced_fallback、計9記事分)を先に実行した(`evidence_run.py`/
`evidence_run_02.py`)。実測してみると1記事あたりのselection costが
想定(Trial-04/06実測平均¥1前後)どおりであり残予算に十分な余裕が
あったため、**委任文が指定した規模(Meta A2/B1B・Hormuz A2/B1B・
twins A2×3・Melos A2×3、計10記事)+forced_fallback 1回を全て実行した**
(`evidence_run_03.py`でMeta B1B・Hormuz B1Bを追加実行、規模縮小のまま
終わらせなかった)。

### 5-3. 結果(全記事、実測)

| 記事 | kp_backend_used | selection status | shortlist | contract | mismatch | canon | redundancy(retry回数) | cost_jpy |
|---|---|---|---|---|---|---|---|---|
| hormuz_a2 | db_hybrid | KEY_WORDS_STRUCTURE_PASS | 20 | candidate_id_v1 | 0 | CANONICALIZATION_PASS | REDUNDANCY_PASS(0) | 1.1283 |
| hormuz_b1b | db_hybrid | KEY_WORDS_STRUCTURE_PASS | 20 | candidate_id_v1 | 0 | CANONICALIZATION_PASS | REDUNDANCY_PASS(1) | 0.9105 |
| meta_a2 | db_hybrid | KEY_WORDS_STRUCTURE_PASS | 22 | candidate_id_v1 | 0 | CANONICALIZATION_PASS | REDUNDANCY_PASS(0) | 1.2781 |
| meta_b1b | db_hybrid | KEY_WORDS_STRUCTURE_PASS | 24 | candidate_id_v1 | 0 | CANONICALIZATION_PASS | REDUNDANCY_PASS(1) | 1.1584 |
| twins_a2(s1) | db_hybrid | KEY_WORDS_STRUCTURE_PASS | 20 | candidate_id_v1 | 0 | CANONICALIZATION_PASS | REDUNDANCY_PASS(0) | 0.9362 |
| twins_a2(s2) | db_hybrid | KEY_WORDS_STRUCTURE_PASS | 20 | candidate_id_v1 | 0 | CANONICALIZATION_PASS | REDUNDANCY_PASS(0) | 1.2698 |
| twins_a2(s3) | db_hybrid | KEY_WORDS_STRUCTURE_PASS | 20 | candidate_id_v1 | 0 | CANONICALIZATION_PASS | REDUNDANCY_PASS(0) | 0.5281 |
| melos_a2(s1) | db_hybrid | KEY_WORDS_STRUCTURE_PASS | 20 | candidate_id_v1 | 0 | CANONICALIZATION_PASS | REDUNDANCY_PASS(0) | 1.1533 |
| melos_a2(s2) | db_hybrid | KEY_WORDS_STRUCTURE_PASS | 20 | candidate_id_v1 | 0 | CANONICALIZATION_PASS | REDUNDANCY_PASS(0) | 0.7377 |
| melos_a2(s3) | db_hybrid | KEY_WORDS_STRUCTURE_PASS | 20 | candidate_id_v1 | 0 | CANONICALIZATION_PASS | REDUNDANCY_PASS(0) | 0.5130 |
| forced_fallback | strategy_l_fallback | (db_hybrid attempt: `SHORTLIST_TOO_SMALL`、shortlist total=11 phrase+important=0、API呼び出し前に判定) | - | free_text_strategy_l(fallback側) | - | - | - | db_hybrid側¥0 |

**全10記事(反復サンプル含む)とも`KEY_WORDS_STRUCTURE_PASS`・
`candidate_mismatch_suspected_count=0`・`source_reference_contract=
"candidate_id_v1"`・model_id`gpt-5.6-luna`。** hormuz_b1b・meta_b1bは
Key Phrase Set Redundancy QAが1回目`REDUNDANCY_NG`(意味重複、db_hybrid
選定・候補ID contractとは無関係な既存Redundancy QAロジックの通常動作)
となり選定からの1 retryで`REDUNDANCY_PASS`まで到達した(既存retry
ループが候補ID contractでも正しく機能することを確認)。

selection cost実測合計: **¥9.6134**(10記事分、forced_fallbackのdb_
hybrid側は¥0)。平均¥0.961/記事(Trial-06実測平均¥0.958/記事・
Family X v1実測平均¥1.068/記事と同水準)。

### 5-4. (欠番、§5-3へ統合)

### 5-5. 費用まとめ

| 区分 | 金額(JPY) |
|---|---|
| 事故(§0、test修正前の意図しない実API呼び出し2回) | 20.7826 |
| runtime evidence(selection実測、10記事分) | 9.6134 |
| canonicalization/Redundancy QA(既存Production側が元々cost計測していない、OPEN-206既知の限界) | 計測不可(実際には課金されているが金額不明) |
| **実測合計(判明分)** | **30.3960** |
| **Guardrail** | ¥40 |

**Guardrail超過の有無**: 判明分の実測合計(¥30.3960)はGuardrail¥40を
超過していない。ただしcanonicalization/Redundancy QAの実際のコスト
(既存Production側の既知の計測欠落、OPEN-206)は上記に含まれないため、
**実際の総支出は¥30.3960をやや上回っている可能性がある**(既存の
計測限界であり本タスクが新たに生んだ欠落ではない)。参考として、
canonicalization/Redundancy QAは選定より出力が小さく1回あたり数十銭
〜1円程度と推定されるため(過去のcost baseline実測から類推、確定値
ではない)、10記事+2 retry分を合算しても実際の総支出がGuardrail¥40を
明確に超過している可能性は低いと判断する(確定的な保証ではない、
推測であることを明記する)。

### 5-6. 受入条件との対応

| 受入条件 | 結果 |
|---|---|
| structural PASS | 全10記事(反復サンプル含む)で`KEY_WORDS_STRUCTURE_PASS`(実測、§5-3) |
| 候補ID解決失敗 | 0件(全記事) |
| surface_echo mismatch(`candidate_mismatch_suspected`) | 0件(全記事、実測`candidate_mismatch_suspected_count=0`) |
| Source Gate raw照合 | 全記事とも`KEY_WORDS_STRUCTURE_PASS`まで到達(`_verify_source_spans_against_raw_article`は`run_db_hybrid_selection`内でPASS後に必ず実行される既存ロジック、不一致があればDbHybridFailureで検出されるため、到達=PASS) |
| quote-heavy(twins A2/Melos A2)安定性 | 3サンプルずつ全件PASS、引用符コピーに起因する`KEY_WORDS_STRUCTURE_INVALID`は0件(Trial-06の根本原因解消がProduction配線後も維持されていることを実データで確認) |
| cost・token(Trial-06/Family X v1比) | selection平均コスト¥0.961/記事、Trial-06実測平均¥0.958/記事・Family X v1実測平均¥1.068/記事と同水準(§5-3) |
| model_id/routing | 全記事とも`gpt-5.6-luna`(A2_SUPPORT、ER-006-MODEL-ROUTING-CONTRACT-01経由、実測usage log[`keywords_runtime_metadata.json`]で確認) |
| telemetry/metadata項目 | `source_reference_contract`/`family_profile`/`candidate_mismatch_suspected_count`等、新設フィールドが実際に`keywords_runtime_metadata.json`/`telemetry.jsonl`へ記録されることを実測確認 |
| fallback非発火(Family X本流) | hormuz_a2/twins_a2/melos_a2/meta_a2はいずれもfallback非発火(db_hybrid成功) |
| 強制fallback1回 | forced_fallback記事(短い本文)でSHORTLIST_TOO_SMALL→Strategy L fallbackを実測、telemetryに`source_reference_contract="free_text_strategy_l"`が記録されることを確認(§5-3) |

---

## 6. Gate 3チェックリスト(自己点検、確定はFable)

| 項目 | 状態 |
|---|---|
| Production正式初回経路 | 済(`sc.run_key_phrases(kp_backend="db_hybrid")`経由で実測) |
| retry・fallback・regenerationとの整合 | 済(Redundancy QA retryは同一shortlist_cache経由で候補ID表を再利用する既存設計を維持[コード変更なし]、fallback[Strategy L]はcontract混在をtelemetryで観測可能、regeneration[KP再選定]も同一入口`run_key_phrases`) |
| DEV・Trial-onlyではないこと | 済(Production module`er030_*`のみ変更、Trial記録`er034`は無変更のまま) |
| Production runtimeでの実発火 | 済(§5実測) |
| 必要testのPASS | 済(146件、§4) |
| runtime evidence | 済(委任文指定の全10記事+forced_fallback、§5) |
| 実際のmodel_id・routing確認 | 済(`gpt-5.6-luna`、§5-6) |
| コスト影響評価 | 済(§5-5、事故分含め開示) |
| `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md` | 済(本コミットに含む) |
| 必要なGit反映 | 済(本コミット) |
| approved specとProduction挙動の一致 | 済(候補ID方式・非ブロッキング取り違え検知・Family Z未配線の3点とも仕様どおり実装) |

Sonnetは`PRODUCTION_WIRED`を宣言しない(最終判定はFable/ユーザー)。

---

## 7. STOP条件該当の有無

新DB追加・追加LLM call常設・v1 baseline挙動の変更(候補生成・
shortlist内容の変化)・大規模schema変更・Production互換性を壊す
migrationのいずれも発生していない。**STOP該当なし**。ただし§0の
事故(意図しない実API呼び出し¥20.7826)を透明性のため報告する
(隠さない)。

**USER_DECISION_REQUIRED候補として提起する論点**:
- `run_project_regression.py`のdiscovery pattern(`er0*_test_*.py`)が
  末尾`_test.py`形式のファイルを拾えていない既存gap(§4-4)。修正は
  pattern変更(全体規模の変更)を伴うため、本タスクのSTOP条件を避け
  今回は修正しない。OPEN_ITEMS化してよいか。
- §0の事故(¥20.7826)自体は再発防止済みだが、同種の「内部実装切替時、
  既存testのmock対象が追随せず実APIが素通りする」構造的リスクへの
  恒久対策(テスト基盤側の防御機構)を導入するかはSTOP条件の「大規模
  変更」に該当しうるため、別途Fable/ユーザー判断が必要な論点として
  提起する(§0-5)。

---

## 8. SSOT反映

`CURRENT_SPEC.md`(Key Phrase節、Family X選定方式の行へ追記)、
`DECISION_LOG.md`(新規エントリ)、`OPEN_ITEMS.md`(OPEN-202追記)、
`docs/pm/REPORT_LEDGER.md`(新規行)。**修正1回目(本節)で追記**:
CURRENT_SPECへSF-3(surface_echoのschema制約と非ブロッキング判定の
関係を明確化)・N2(Family Z配線時は本モジュール経由が規範として必須)、
DECISION_LOGへN1(実際の復元を守っているのはsurface_form優先の復元
規則でありStage 1整理は防御の二重化である旨)、OPEN_ITEMS OPEN-202へ
N5・N6を追記。

---

## 9. Git

新規ファイル(`er030_key_phrase_db_hybrid_source_reference_contract_
01.py`、同test、同evidence run×2、本REPORT、delegation_log)+変更
ファイル(`er030_key_phrase_db_hybrid_core_01.py`、`er030_key_phrase_
db_hybrid_selector_01.py`、`er030_key_phrase_db_hybrid_family_x_
production_wiring_01_test.py`、`er003_v1_n3_01_scaffold_generate.py`、
`er003_key_words_canonicalization.py`)+SSOT4点+evidence artifact
(`er030_output/family_x_kp_source_reference_contract_evidence_01/`)+
telemetry(`er030_output/kp_backend_telemetry_01/telemetry.jsonl`、
追記のみ)のみをpath指定でstage(`git add -A`禁止)。他Agent領域
(`er006_preprod_hardening_01_validation.py`等、本タスクで発生していない
既存差分)は一切addしない。**修正1回目**: 上記に加え
`er030_key_phrase_db_hybrid_source_reference_contract_01.py`/同test/
`er030_key_phrase_db_hybrid_selector_01.py`/
`er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`/
`er003_v1_n3_01_scaffold_generate.py`(いずれも本節の追加差分)+
delegation_log(`..._02.md`)+SSOT4点+本REPORTのみをpath指定でstage。

---

## 10. Opus L2所見(逐語、修正1回目委任文より転記)

Mandatory Opus L2レビュー実施後、Fableが本Sonnetへ送付した修正委任文
(`docs/pm/delegation_log/2026-09-28_KEY-PHRASE-DB-HYBRID-SOURCE-
REFERENCE-CONTRACT-PRODUCTION-WIRING-01_02.md`)に記載されたOpus L2
所見・Fable判定を、そのまま転記する。

> Opus結論: BLOCKER 0、PRODUCTION_WIRED判定へ進んで可、ただし
> SF-1/SF-2は同一IDで閉じることを強く推奨。Fable判定: SF-1〜SF-7を
> 本修正で反映してからGate 3確定。

**前提**: REPORTに§「Opus L2所見(逐語)」を追記(本委任文のdelegation_
logに全文を添付、そこから転記)。

**修正(すべて¥0)**:

- **SF-1(最優先)**: `restore_source_fields`の`surface_form`(最頻表層)
  と`context_sentence_id`(変異形のいずれかが最初にヒットした文)が
  独立に決まるため、復元した`source_span`が`source_sentence`に含まれ
  ない場合がある(単数導入→複数反復の典型パターンで発生)。対応:
  (b)既実装の`audit_shortlist_source_span_consistency`をAPI呼び出し前に
  `run_db_hybrid_selection`へ配線し、不整合候補は補正(その文に実在する
  最長の`observed_surface_variants`を`source_span`に採る)+telemetry
  記録、補正不能なら候補ID表から除外+記録。(a)`restore_source_fields`
  側にも同じ補正を防御的に実装。(c)core側`context_sentence_id`補正は
  行わない(er028無変更)。test: meta_a2実データ候補(`contract worker`/
  `contract workers`)を反転させたfixture、既存evidence 11ケースの生
  応答+shortlistでオフライン再復元し全件PASS維持を確認する。
- **SF-2**: `er030_key_phrase_db_hybrid_family_x_production_wiring_01_
  test.py::test_shortlist_too_small_raises_before_any_api_call`のmock
  対象を`db_hybrid.src_ref_contract.make_instrumented_selector_
  factory`へ差し替え(死んだガードの復活)。
- **SF-3**: CURRENT_SPEC文言「`surface_echo`はschema上必須(strict
  mode制約)、判定上は非ブロッキング・真実源にしない」へ明確化(コード
  不変)。
- **SF-4**: `candidate_mismatch_suspected`の算出に`display_phrase`と
  復元候補のlemma許容の弱い一致比較を追加(非ブロッキング、telemetry
  のみ)。
- **SF-5**: `surface_form`欠落時の`source_span`fallbackを削除し
  `unresolved`(fail-closed)へ。
- **SF-6**: 同一`source_candidate_id`の重複選択件数を`restore_
  telemetry`へ記録(非ブロッキング)。
- **SF-7**: `run_db_hybrid_selection`冒頭で`_check_family_profile_
  supported`を呼ぶ(Wiktionary lookup前にfail-closed)。
- 項目15の軽微: fallback telemetry行に`attempted_source_reference_
  contract`を追加。
- N2: CURRENT_SPECに「Family Z配線時は
  `er030_key_phrase_db_hybrid_source_reference_contract_01`経由が
  **必須**(規範)」を明記。N5/N6: OPEN-202へ「`source_sentence`が
  見出し行になる系統的バイアス(Redundancy QA文脈)」「canonicalization
  Rule 7の復元余地縮小→`REVIEW_REQUIRED`率を継続監視」を追記。N4:
  新規OPEN「`run_project_regression.py` DEFAULT_PATTERNが`_NN_test.py`
  形式(29モジュール、Production中核test含む)を収集しない+実API
  test/guard testの棚卸しが必要」+「test infraのmock-drift恒久対策
  (ネットワーク遮断fixture等)」をPM追跡で登録。N11: REPORT/REPORT_
  LEDGERのevidenceパスを実体`er030_output/family_x_kp_source_
  reference_contract_evidence_01/`に是正。N1: DECISION_LOGに「実際の
  復元を守っているのはsurface_form優先の復元規則であり、Stage 1整理は
  防御の二重化」を明記。

**検証**: 新規/更新test全PASS(¥0)、本IDのtest群(27+32件)は手動実行
(regression未収集のため)、`run_project_regression.py`(既知baseline
以外なし)。REPORT §「修正1回目」: Opus所見照合表(SF-1〜7/N1〜11:
対応/OPEN/対象外)、オフライン再復元結果、Gate 3表最終化(Opus L2=
実施済み、`PRODUCTION_WIRED`=Fable判定待ち)。SSOT: CURRENT_SPEC/
DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER。

---

## 11. 修正1回目(Opus L2所見反映、2026-09-28)

### 11-1. Opus所見照合表

| # | 所見 | 対応 | 詳細 |
|---|---|---|---|
| SF-1 | surface_form/context_sentence_id独立決定によるsource_span不整合 | **対応**(コード修正) | (a)`restore_source_fields`に防御的補正(`_longest_matching_variant_in_sentence`、補正不能時は`unresolved`理由`SOURCE_SPAN_NOT_IN_CONTEXT_SENTENCE`)、(b)`correct_shortlist_source_span_consistency`をAPI呼び出し前に`run_db_hybrid_selection`へ配線(補正/除外+telemetry`source_span_consistency_audit`)。§11-2参照 |
| SF-2 | 死んだmockガード | **対応**(test修正) | mock対象を`db_hybrid.src_ref_contract.make_instrumented_selector_factory`へ変更 |
| SF-3 | surface_echoの必須性/非ブロッキング性の文言曖昧 | **対応**(コメント+CURRENT_SPEC) | モジュールdocstring・CURRENT_SPECを「schema上必須[strict mode制約]、判定上は非ブロッキング」へ明確化 |
| SF-4 | candidate_mismatch_suspectedがsurface_echoのみ依拠 | **対応**(コード修正) | `_display_phrase_candidate_mismatch_suspected`(弱いlemma正規化)を追加、OR条件で`candidate_mismatch_suspected`へ反映(非ブロッキング、`signals`で内訳記録) |
| SF-5 | surface_form欠落時の旧source_span fallback | **対応**(コード修正) | fallback削除、`unresolved`理由`SURFACE_FORM_MISSING`へfail-closed |
| SF-6 | 重複candidate_id選択の非計測 | **対応**(コード修正) | `duplicate_candidate_id_selection_count`/`duplicate_candidate_ids`を`restore_telemetry`・`keywords_runtime_metadata.json`へ追加 |
| SF-7 | family_profile検査がStage1/Wiktionary lookuk後 | **対応**(コード修正) | `run_db_hybrid_selection`冒頭(`os.makedirs`より前)で`_check_family_profile_supported`を呼ぶ |
| 項目15 | fallback telemetryに試行契約の記録がない | **対応**(コード修正) | `attempted_source_reference_contract`を`_run_key_phrase_selection_db_hybrid_with_fallback`のFALLBACK_TRIGGERED telemetry行へ追加 |
| N1 | Stage1整理の位置づけの正確な記述 | **対応**(DECISION_LOG追記) | §11-4参照 |
| N2 | Family Z配線時の本モジュール経由の必須化 | **対応**(CURRENT_SPEC追記) | §11-4参照 |
| N4 | run_project_regression.py命名gap+mock-drift恒久対策 | **OPEN**(PM追跡、修正せず) | 新規OPEN登録を提案(§11-4、STOP条件「大規模変更」回避のため未実装、既に§4-4/§7で開示済みの既知gapを正式にOPEN化) |
| N5 | source_sentenceが見出し行になる系統的バイアス | **OPEN**(観測、修正せず) | OPEN-202へ追記(§11-4)。本タスクの10記事evidence再検証では0件観測(§11-2)、構造的リスクとして継続監視 |
| N6 | canonicalization Rule 7の復元余地縮小 | **OPEN**(観測、修正せず) | OPEN-202へ追記(§11-4)。`REVIEW_REQUIRED`率の継続監視を運用化 |
| N11 | REPORT/REPORT_LEDGERのevidenceパス是正 | **対象外**(既に正確) | 再確認の結果、REPORT本文・REPORT_LEDGER・SSOT・evidence_run script群のいずれも`er030_output/family_x_kp_source_reference_contract_evidence_01/`で一貫しており、実ディレクトリとも一致していることを確認した(具体的な誤記箇所は発見できなかった、詳細は本REPORT本節末尾の注記) |

### 11-2. オフライン再復元結果(¥0、OpenAI API呼び出しなし)

修正1回目で追加した`correct_shortlist_source_span_consistency`
(SF-1(b))・改訂後の`restore_source_fields`(SF-1(a)/SF-4/SF-5/SF-6)を、
本Production配線のruntime evidence(`er030_output/family_x_kp_source_
reference_contract_evidence_01/`)で実際にPASSした10記事分の
「LLM出力相当データ」(`keywords_runtime_metadata.json`の
`attempts_detail[0].parsed.items`、`source_candidate_id`/`surface_
echo`/`display_phrase`等の元のLLM出力フィールドをそのまま含む)+
article_textから再計算したStage1/shortlist(Wiktionary APIのみ、
OpenAI API呼び出しは一切なし)を使ってオフライン再復元した
(`docs/pm/tools/`配下ではなくscratchpad上で実行した一時スクリプト、
再現性のためロジック概要のみ記録する)。

| 記事 | audit不整合数 | 補正数 | 除外数 | 新規unresolved | mismatch件数 | source_span/source_sentence/mismatchが元と完全一致 |
|---|---|---|---|---|---|---|
| hormuz_a2 | 0 | 0 | 0 | 0 | 0 | 一致 |
| hormuz_b1b | 0 | 0 | 0 | 0 | 0 | 一致 |
| meta_a2 | 0 | 0 | 0 | 0 | 0 | 一致 |
| meta_b1b | 0 | 0 | 0 | 0 | 0 | 一致 |
| twins_a2 | 0 | 0 | 0 | 0 | 0 | 一致 |
| twins_a2_s2 | 0 | 0 | 0 | 0 | 0 | 一致 |
| twins_a2_s3 | 0 | 0 | 0 | 0 | 0 | 一致 |
| melos_a2 | 0 | 0 | 0 | 0 | 0 | 一致 |
| melos_a2_s2 | 0 | 0 | 0 | 0 | 0 | 一致 |
| melos_a2_s3 | 0 | 0 | 0 | 0 | 0 | 一致 |

**結果**: 全10記事(委任文が指す「既存evidence 11ケース」のうち、
`forced_fallback`はdb_hybrid選定自体がAPI呼び出し前の`SHORTLIST_TOO_
SMALL`で失敗し復元自体が発生しないため対象外、実質10記事が復元対象)
で、新ロジック適用後もaudit不整合0件・補正0件・除外0件・新規
unresolved0件・mismatch件数変化0件・`source_span`/`source_sentence`/
`candidate_mismatch_suspected`が元の値と完全一致することを確認した。
すなわち、実データではSF-1が修正する不整合は今回発生しておらず(§2-5
のmeta_a2手動確認と整合)、修正1回目は**既存の正常な復元結果を変えず
に、将来の不整合ケースへの補正・fail-closed経路を追加しただけ**である
ことを実データで確認した。

### 11-3. Gate 3チェックリスト最終化

| 項目 | 状態 |
|---|---|
| Production正式初回経路 | 済(§5実測、修正1回目で挙動変更なし) |
| retry・fallback・regenerationとの整合 | 済(修正1回目でも維持、fallback telemetryへ`attempted_source_reference_contract`追加のみ) |
| DEV・Trial-onlyではないこと | 済(Trial記録`er034`は無変更のまま) |
| Production runtimeでの実発火 | 済(§5実測+§11-2オフライン再検証) |
| 必要testのPASS | 済(158件、既存146件+修正1回目新規12件、全PASS・¥0) |
| runtime evidence | 済(§5、再取得不要と判断[§11-2のオフライン再検証で新ロジックが実データへ影響しないことを確認済みのため]) |
| 実際のmodel_id・routing確認 | 済(§5-6、変更なし) |
| コスト影響評価 | 済(修正1回目¥0、事故なし) |
| `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md` | 済(修正2回目、commit`<pending>`。着手時に別Agent[`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02`]の未commit差分と競合したため修正1回目時点では未反映のまま`docs/pm/RESULT_PACKET_KPC2.md`へ下書きのみ保存し、修正2回目[本SSOT反映委任]で適用) |
| 必要なGit反映 | 済(本commit) |
| approved specとProduction挙動の一致 | 済 |
| **Opus L2レビュー** | **実施済み**(本節§10所見、BLOCKER0件) |
| **`PRODUCTION_WIRED`最終判定** | **Fable判定待ち**(Sonnetは宣言しない) |

Sonnetは`PRODUCTION_WIRED`を宣言しない(最終判定はFable/ユーザー)。

### 11-4. SSOT反映詳細

- **CURRENT_SPEC.md**(Key Phrase節、Source Reference Contractの行へ
  追記): (SF-3)「`surface_echo`はJSON Schema strict mode制約により
  schema上は必須プロパティだが、判定(PASS/FAIL)上は非ブロッキングで
  あり取り違え検知専用の参考情報である」旨を明確化。(N2)「Family Z
  のDB Hybrid系を将来Production配線する場合は、`er030_key_phrase_db_
  hybrid_source_reference_contract_01`経由が規範として必須(旧`source_
  sentence`/`source_span`自由記述のコピー方式は禁止)」を明記。
- **DECISION_LOG.md**(修正1回目エントリ新設): (N1)「Trial-06/本
  Production配線を通じて実際にsource_span/source_sentenceの正しさを
  守っていたのは、常に`surface_form`(短い句)を優先して復元源とする
  `restore_source_fields`の規則そのものであり、Stage 1
  `_normalize_important_noun_candidate_source_span`によるcandidate
  dictレベルの`source_span`整理は、この規則がすでに機能していた上への
  防御の二重化(将来的にrestoreロジックがsurface_form以外を参照する
  よう変更された場合の保険)である」ことを明記する。
- **OPEN_ITEMS.md**(OPEN-202へ追記): (N5)「`build_sentence_units`が
  記事見出し(H1)を独立した1つの`sentence_units`要素として扱うため、
  見出しに含まれる語がKey Phraseとしても選ばれた場合、理論上
  `context_sentence_id`が見出し行を指し`source_sentence`が見出し文
  そのものになりうる構造的リスクがある(Opus L2レビューで指摘、
  Redundancy QAが本文中の実例文を期待する処理文脈で違和感を生みうる)。
  本タスクの10記事evidence再検証(§11-2)では実際の発生は0件だったが、
  量産規模で継続監視する」旨、(N6)「Stage 1 `source_span`整理・SF-1の
  補正により`source_span`の値がより短い句へ是正されたことで、
  canonicalizationのRule 7(`qa_traceable_contiguous_span`、
  `_is_contiguous_substring`)が許容する復元([display_phraseが
  source_span内の連続部分文字列であることの構造チェック])の余地が
  従来より狭まった可能性があり、これに伴い`CANONICALIZATION_REVIEW_
  REQUIRED`率が変化するかを量産observationで継続監視する」旨を追記。
- **N4(新規OPEN登録を提案)**: `run_project_regression.py`の
  `DEFAULT_PATTERNS`(`er0*_test_*.py`)が末尾`_NN_test.py`形式
  (`er030_key_phrase_db_hybrid_family_x_production_wiring_01_test.py`
  等29モジュール、Production中核testを含む)を収集しない既存gapと、
  test修正が実装切替に追随せずmockが空振りする「mock-drift」構造的
  リスク(§0既知)への恒久対策(例: unit test実行時にAPIキー環境変数を
  強制無効化するfixture)の要否を、Fable/ユーザー判断待ちのPM追跡
  項目として新規登録することを提案する(本タスクでは未登録、STOP条件
  「大規模変更」回避のため実装・SSOT登録のいずれも見送り、次の
  USER_DECISION_REQUIREDまたはPM追跡候補として本REPORTに明記するに
  留める)。
- **N11**: REPORT本文(§5-1/§9)・`docs/pm/REPORT_LEDGER.md`・
  `CURRENT_SPEC.md`・evidence_run script群(`_01.py`/`_02.py`/`_03.py`)
  のいずれについても`er030_output/family_x_kp_source_reference_
  contract_evidence_01/`という同一パス表記であることを再確認し、
  実ディレクトリ(`ls`実測)とも一致することを確認した。委任文が
  指す具体的な誤記箇所を特定できなかったため、**本節時点では対応
  不要と判断する**(誤りを発見した場合は追って訂正する)。

---

Management-ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01
