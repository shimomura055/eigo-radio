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
`docs/pm/REPORT_LEDGER.md`(新規行)。

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
既存差分)は一切addしない。

Management-ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01
