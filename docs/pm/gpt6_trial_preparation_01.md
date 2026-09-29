# GPT-6 Trial準備(read-only整理) — GPT6-TRIAL-PREPARATION-01

作成日: 2026-09-29。管理ID: `GPT6-TRIAL-PREPARATION-01`(委任_01)。

**本ファイルの性質**: 調査・整理のみ。Trial実行・Production変更・採用提案は含まない。
未確認・未計測の項目は明記する。GPT-6のmodel_id文字列は**「未確認」**(推測しない)。
ユーザー向け表記は Standard(旧称A2)/Advanced(旧称B1B)を用いる。

---

## 1. 現在の各RoleのActual Model ID(Production正式経路)

### 1-1. 結論(先出し)

Production正式経路のテキスト系LLM Roleは、Family X・Family A/B/Z(確認できた範囲)
すべてで**単一Approved Model `gpt-5.6-luna`**に統一されている
(`er006_model_routing_contract_01.py`、2026-08-22決定)。QUERY_PLANNER・
TOPIC_SELECTOR・RESEARCH・WRITER・WRITER_FACT_CHECK・SUPPORT・SUPPORT_FACT_CHECK
の7定数が全て同一値 `"gpt-5.6-luna"` であるため(`er006_model_routing_contract_01.py:30-36`)、
「Role間でmodelが分かれている」という前提は現状**成立しない**。Contractと実測
(`raw_usage_log.jsonl`の`model_id`)は今回確認した全サンプルで一致していた
(不一致0件)。GPT-6移行時は実質1つの定数群を差し替えれば理論上は済むが、
§2で述べる通りContract外にも同値のリテラルが散在する。

### 1-2. Role別表

| Role | process名(Contract) | Contract上のmodel_id | 実測model_id(log) | reasoning effort | 呼び出しファイル:行 | Family |
|---|---|---|---|---|---|---|
| Query Planning | `QUERY_PLANNING` | gpt-5.6-luna | 未確認(本タスクでは実測log未特定) | 未確認 | `er006_model_routing_contract_01.py:66` | 全Family共通(定義のみ確認、Family X実運用での呼出未追跡) |
| Topic Selection | `TOPIC_SELECTION` | gpt-5.6-luna | 未確認 | 未確認 | 同上:67。Family Xは現状ユーザーがテーマ選定するためこのRole自体が実運用で呼ばれているか未確認(`er002_topic_adapter.py`のMODEL_SEARCH="gpt-5.6-luna"はハードコードでContract非経由、使用箇所未追跡) | 未確認 |
| Evidence Pack/VFL/Verification(Researcher) | `EVIDENCE_PACK`/`VFL`/`VERIFICATION` | gpt-5.6-luna | gpt-5.6-luna(`er019_output/family_x_refresh_e2e_01/hormuz/run_03/raw_usage_log.jsonl`の`theme`列に対応する呼び出し、ただし`stage`ラベル欠落分に混在) | high(`er003_v1_en_direct_vfl_01_generate.py:58`) | `er003_v1_en_direct_vfl_01_generate.py:173,256` | Family X(共通研究基盤、他Familyも同モジュール利用と推定・未全数確認) |
| JA Writer O/R1/R2 | `B1_WRITER`(Family X内部では`WRITER_MODEL=vfl01.MODEL`を直接参照、require_model経由ではない) | gpt-5.6-luna | gpt-5.6-luna(`hormuz/run_03/raw_usage_log.jsonl` stage=`ja_original`/`ja_r1`/`ja_r2`等、22件全件luna) | high | `er019_family_x_ja_writer_o_r1_r2_01.py:48,211,225,381` | Family X |
| Ledger/Deviation Checker(JA Fact Check・EN Advanced・Standard共通関数) | Contract未定義process(`vfl01.run_deviation_check`が`MODEL=routing.WRITER_MODEL`をデフォルト値として使用、呼び出し元は明示的processキーを渡さない) | gpt-5.6-luna(WRITER_MODEL経由) | gpt-5.6-luna(stage=`ja_original_check`/`ja_r2_check`等、`advanced_attempt*.json`) | high | `er003_v1_en_direct_vfl_01_generate.py:773` 定義、呼び出しは`er019_family_x_ja_writer_o_r1_r2_01.py:278,298,391,426` (JA)・`er012_e_family_entertainment_two_level_runner_01.py:382,415,478,509` (EN Advanced/Standard) | Family X |
| Translation(忠実英訳、Advanced生成) | `NATURAL_ENGLISH_ADAPTATION` | gpt-5.6-luna | gpt-5.6-luna(stage=`advanced`、n=8、`an3_t0_wiring_regression_01`) | high(`er003_v1_n3_01_advanced_adaptation_generate.py`はvfl01.REASONING_EFFORT継承) | `er003_v1_n3_01_advanced_adaptation_generate.py:69,444,643,707` | Family X(`adv_gen.generate_family_x_faithful_translation`) |
| Standard simplification(A2) | `STANDARD_A2_ADAPTATION` | gpt-5.6-luna | gpt-5.6-luna(未ラベル分に混在、個別分離は本タスクでは未実施) | high | `er003_v1_n3_01_standard_a2_generate.py:89,419,566` | Family X(`std_gen.generate_family_x_standard_a2_no_heading`) |
| Comment1〜4・Preview | `B1_SUPPORT`/`A2_SUPPORT` | gpt-5.6-luna | 未ラベル分に混在(個別分離未実施) | high(vfl01.REASONING_EFFORT継承) | `er003_v1_n3_01_scaffold_generate.py:799,803,817,834,845`(B1)・`860-883`(A2)、Family X呼び出し元`er019_family_x_audio_production_runner_01.py:99-104,236-303` | Family X・Family A/B共通(`er012_b_family_production_runner_01.py:254,747,1073`も`B1_SUPPORT`使用を確認) |
| Key Phrase抽出・選定 | `B1_SUPPORT`/`A2_SUPPORT`(`sc.run_key_phrases(process=...)`) | gpt-5.6-luna | 未ラベル分に混在 | 未確認(Selector系は別定数`SELECTOR_REASONING_EFFORT`の可能性、本タスクでは未特定) | `er003_v1_n3_01_scaffold_generate.py:340-341,711,914-915`、Family X経路`er019_family_x_audio_production_runner_01.py:340-341` | Family X。Key Phrase DB Hybrid系(`er030_key_phrase_db_hybrid_selector_01.py`)は別のSELECTOR_MODEL系統(§1-3参照、未確認) |
| Key Phrase explanation(Advanced英語解説) | `KEY_PHRASE_ADVANCED_EXPLANATION` | gpt-5.6-luna(=SUPPORT_MODEL) | gpt-5.6-luna(コード上`MODEL="gpt-5.6-luna"`を候補値として`require_model()`へ渡しfail-closed検証、実測log未個別確認) | medium(`er019_family_x_kp_explanation_01.py:44`、Comment/KPより低いreasoning) | `er019_family_x_kp_explanation_01.py:42-44,259` | Family X(2026-09-29 W4追加) |
| In One Line | `NATURAL_ENGLISH_ADAPTATION`(Translationと同一processキーを流用、専用キーなし) | gpt-5.6-luna | 未確認(個別分離未実施) | high(継承) | `er003_v1_n3_01_advanced_adaptation_generate.py:703-707` | Family X |
| Natural English QA(TTS Local Rewrite候補生成) | Contract未定義process。`b1s.MODEL`(=`vfl01.MODEL`)をデフォルト引数として直接使用、`require_model()`呼び出しなし | gpt-5.6-luna(間接) | 未確認 | 未確認 | `er020_tts_retry_local_rewrite_01.py:325,474` | 全Family共通(TTS再生成カスケード) |
| Pronunciation resolver(固有名詞抽出) | `PROPER_NOUN_EXTRACTION` | gpt-5.6-luna(=WRITER_MODEL) | 未確認 | 未確認 | `er006_proper_noun_extraction_01.py`(未読、Contract定義のみ確認`er006_model_routing_contract_01.py:80`) | 全Family共通 |
| Shared Point Blueprint | `SHARED_POINT_BLUEPRINT` | gpt-5.6-luna | 未確認 | 未確認 | Contract定義のみ確認(`:85`) | Family A/B(A2/B1 Point構造整合) |
| Family X Flash-Lite TTS(音声、参考) | `FAMILY_X_FLASH_LITE_TTS` | gemini-3.8-flash-lite-tts(テキストLLMではなくTTS、GPT-6比較対象外) | — | — | `er006_model_routing_contract_01.py:104` | Family X(TTS Phase 1) |

**Contract-実測不一致**: 今回確認した全サンプル(Hormuz run_03、an3_t0 regression
hormuz/meta、計58 API callの`model_id`列)で**不一致は0件**。全て`gpt-5.6-luna`。
ただし「未確認」と記したRole(Query Planning/Topic Selection/Natural English QA/
Pronunciation resolver/Shared Point Blueprint/Key Phrase抽出個別分離)は、実測log
個別特定を本タスクでは実施していない(Contract定義値の存在確認のみ)。

### 1-3. Family別補足

- **Family A(News、`er011_*`系)**: `B1_SUPPORT`/`A2_SUPPORT`利用を`er011_*`ファイル群
  (130ファイル中の大半)で確認したが、大半がTrial番号付きDEVスクリプトであり、
  現行Production正式runnerの特定は本タスク範囲外(未確認)。
- **Family B(Editorial、`er012_b_family_production_runner_01.py`)**: `B1_SUPPORT`
  (`routing.SUPPORT_MODEL`)使用を確認(:254,747,1073)。Writer側の確認は未実施。
- **Family C(`er013_family_c_production_runner_01.py`)**: `require_model()`の
  直接呼び出しは0件。`er013_family_c_production_01.py`はmodelを引数として受け取る
  設計(:500 `run_support_text_fn(..., model=model)`)であり、実際にどのmodelが
  渡されるかは呼び出し元(`bvoices`=`er012_b_family_voices_production_01.py`等)
  まで追う必要がある。**本タスクでは未確認**(Lunaである可能性は高いが断定しない)。
- **Family Z(Fiction、`er026_family_z_fiction_production_runner_01.py`)**:
  `vfl01`(Writer=Luna)・`scaffold`(Support=Luna)をimport(:60,62)、Family Xと
  同じ基盤モジュールを再利用していると見られる(個別呼び出し箇所は未追跡)。

---

## 2. Routing SSOT

### 2-1. Contract構造(`er006_model_routing_contract_01.py`)

- `PROCESS_MODEL_MAP`(process名→Approved Model、13キー)・`PROCESS_PROVIDER_MAP`
  (`EXCEPTION_SEARCH`/`TTS`/`ASR`の3キー)の2辞書がSSOT本体。
- `require_model(process, model)`: API call**実行前**に呼び、Contract値と不一致
  またはmodel未指定ならfail-closedで`ModelContractViolation`を送出(:118-137)。
- `require_model_or_override(process, model, override_reason)`: DEV/Trial専用の
  薄いラッパー。`override_reason`を明示的に渡した場合のみApproved Model以外を
  許可(Production call siteはこちらを使わない設計、:148-167)。
- `require_provider(process, provider)`: Provider版(:170-182)。

### 2-2. CURRENT_SPEC/DECISION_LOG上のrouting関連決定(Grep結果要約)

- 2026-08-22: Writer(B1/A2)・Writer Fact Check・Support(B1/A2)・Support Fact Check
  の4工程を`gpt-5.6-sol`から`gpt-5.6-luna`へ正式固定(`er006_model_routing_contract_01.py:8-18`
  のコメントに経緯記載、ユーザー承認済み)。
- OPEN-233(`OPEN_ITEMS.md:416`、2026-09-29新規、`DEFERRED (non-blocking)`):
  「GPT-6系への移行可能性が高く、モデル変更により過剰BLOCK傾向・非決定性・
  changed_causality判定・notes_for_writerの扱い・重大fixture検出率自体が変わる
  可能性があるため一旦defer」「順序: Family X E2E完了→GPT-6 Trial/Routing判断→
  必要なProduction導入→新モデル前提でChecker問題を再評価」と明記。再開タイミング
  =GPT-6 Trial/Production Routing判断後。

### 2-3. GPT-6切替時に触る箇所(ハードコード全数調査)

`grep -rn "\"gpt-5\.6-(luna|sol)\""` (コメント行除く、テストファイル・
`er0*_output/`配下除く)で**229件・85ファイル**がヒットしたが、その大半
(約210件)はTrial/DEV番号付きスクリプト(`er011_*_trial_*`・`er015_*_trial_*`
等のcost_compute補助スクリプト含む)。**Production runner系ファイルに絞ると
15件**:

| ファイル:行 | 内容 | GPT-6移行時の要否 |
|---|---|---|
| `er006_model_routing_contract_01.py:30-36`(7件) | Contract本体、Approved Model定義 | **変更必須**(ここが単一の正式変更点) |
| `er002_ja_free_markdown_restore.py:42` | `WRITER_MODEL = "gpt-5.6-sol"`(2026-08-22以前の旧リテラル、Contractには追従していない) | 影響調査要。`er011_open146_ledger_canonical_en_spelling_production_01.py:186`の`make_proper_noun_extraction_fn`のデフォルト引数がこの`restore.WRITER_MODEL`(=`r3.WRITER_MODEL`)を継承しているが、Production本体(`er003_v1_n3_01_articles_generate.py`)は`canon_spelling`モジュールのテキスト整形関数のみ使用しており当該関数は呼んでいないことを確認(実害なしと推定、断定はしない) |
| `er002_topic_adapter.py:21` | `MODEL_SEARCH = "gpt-5.6-luna"`(Contract非経由の独立ハードコード) | Family X実運用での使用有無が未確認のため要調査 |
| `er006_research_coverage_gate_01.py:17` | `GATE_MODEL = "gpt-5.6-luna"`、コメントに「検証用固定。Production本配線せず」と明記 | 対応不要(DEV専用と自己申告) |
| `er006_model_routing_contract_01_static_audit.py`/`er006_audio_cost_spec_fix_01_static_audit.py` | "gpt-5.6-sol"という**文字列が存在しないこと**を検証するaudit test(モデル呼び出しではない) | 変更不要(監査ロジック自体は文字列非依存) |
| `er019_family_x_kp_explanation_01.py:43` | `MODEL = "gpt-5.6-luna"`(`require_model()`へ渡す候補値、Contractと不一致ならfail-closed) | Contract変更と同時にこの1行も更新必要(fail-closedで検知されるため見落としリスクは低い) |

**結論**: Contract 1ファイルの変更だけでは済まない。少なくとも
`er019_family_x_kp_explanation_01.py:43`のような「Contract値を手動で複製している
候補値」がRole単位で複数存在する可能性が高く(今回はKP explanationの1件のみ
確認)、切替時は上記15件全数のレビューに加え、§1で「未確認」とした残りRole
(Query Planning/Natural English QA/Pronunciation resolver等)の実際の呼び出し
チェーンをGPT-6切替直前に再調査する必要がある。

---

## 3. 現行モデルのBaseline Cost/Latency

### 3-1. 既存REPORTの公式値(引用、優先採用)

`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`§5(母集団:
Family X entertainment、n=12、model=gpt-5.6-luna、reasoning=high、web検索なし):

| 指標 | コスト(JPY) | latency(秒) |
|---|---|---|
| 最小 | ¥0.323 | 9.55 |
| 中央値 | ¥0.9024 | 33.16 |
| 平均 | ¥0.954 | 38.07 |
| 最大 | ¥1.6505 | 84.89 |

出典: 同REPORT§5「Checker単発コール」、原典`NEWS-FAMILY-X-JA-FACT-DOUBLE-CHECK-COST-01_REPORT.md`§0/§1。
OPEN-233(`OPEN_ITEMS.md:416`)にも同じ中央値(¥0.90/33秒)が再掲されている。

### 3-2. 本タスクで独自集計した値(参考、母集団明記)

母集団: `er019_output/family_x_refresh_e2e_01/hormuz/run_03/raw_usage_log.jsonl`(22件)
+`meta/run_03/raw_usage_log.jsonl`(13件)+`er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01/{hormuz,meta}/raw_usage_log.jsonl`(13+9件)、計**58件**、全件`model_id=gpt-5.6-luna`。
単価は`er005_output/cost_baseline_01/pricing_snapshot.json`(input $0.20/M・
cached $0.02/M・output $1.20/M)を使用、集計スクリプトはscratchpad
(`aggregate_usage.py`、repoに追加していない)。

| stage(=role相当) | n | median elapsed(秒) | median cost(USD) |
|---|---|---|---|
| advanced(Translation) | 8 | 36.37 | 0.00549 |
| ja_original(JA Writer) | 5 | 20.41 | 0.00230 |
| ja_original_check(Ledger Checker) | 5 | 16.75 | 0.00332 |
| ja_r1 | 5 | 15.86 | 0.00227 |
| ja_r2 | 5 | 14.63 | 0.00188 |
| ja_r2_check | 5 | 8.40 | 0.00224 |
| ja_original_must_fix | 3 | 28.85 | 0.00398 |
| ja_original_check_retry | 3 | 17.47 | 0.00300 |
| ja_r2_must_fix | 2 | 29.83 | 0.00425 |
| ja_r2_check_retry | 2 | 7.25 | 0.00181 |
| (stage未ラベル、KP選定/Comment/Standard等混在) | 15 | 18.65 | 0.00232 |

**未計測**: Standard/Comment1-4/KP抽出/KP explanation/In One Line個別のcost・
latencyはstageラベルが付与されておらず、本タスクでは個別分離していない
(上記「(stage未ラベル)」行に混在)。GPT-6 Trial設計時はraw_usage_logへの
stageラベル付与状況を確認し、個別分離が必要なら別途集計スクリプトが必要。

---

## 4. 代表Fixture

### 4-1. Checker比較用: ER-009-N1 危険fixture 9種

`er009_ledger_deviation_recalibration_02_test.py:24-63`(`FIXTURES`辞書)。
基準Ledger: `er006_output/pool_pilot_01/pool_n9_tip_screens/research/verified_fact_ledger.txt`
(存在確認OK)。結果ファイル: `er006_output/pool_pilot_01/pool_n9_tip_screens/false_negative_fixture_results.json`(存在確認OK、9/9 PASS実績)。
9種: `changed_number`/`changed_actor`/`changed_scope`/`changed_causality`/
`changed_certainty`/`changed_negation`/`changed_comparison`/`changed_time`/
`unsupported_new_claim`(各fixtureのJA/EN逐語は上記test fileに直接記載済み、
本ファイルへの転記は省略しソースへのリンクのみとする)。

### 4-2. Checker比較用: A群5件・B群4件(`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`第3章)

母集団: origin付きMAJOR/MINOR 15件(全てFamily X Entertainment、er019/037/039/045)。

**A群(明らかに止めるべき、5件)**:
| # | Evidence | 存在確認 |
|---|---|---|
| A-1 | `er019_output/family_x_b3_production_wiring_01/run_01/audit/fact_fidelity_fix_01_recheck_summary.json` | OK |
| A-2/A-3 | `er037_output/family_xy_concreteness_control_trial_01/hormuz/task_a_advanced/A3_deviation.json` | OK(ファイル個別確認済み) |
| A-4 | `er039_output/family_xy_concreteness_control_trial_02/meta/cells/AN2-T1_deviation.json` | OK(ファイル個別確認済み) |
| A-5 | `er045_output/family_x_no_heading_segmentation_trial_01/meta/v2/must_fix_retry_result.json` | OK(ファイル個別確認済み) |

**B群(過剰品質の可能性、4件)**:
| # | Evidence | 存在確認 |
|---|---|---|
| B-1 | `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/ja_writer/audit/deviation_checks/ja_original_attempt1.json` | OK |
| B-2(Hormuz B-2、委任背景記載の本件) | `er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/audit/deviation_checks/advanced_attempt1.json` | OK |
| B-3 | `er037_output/family_xy_concreteness_control_trial_01/hormuz/task_b_cleanup/B1_deviation.json` | OK(ファイル個別確認済み) |
| B-4 | `er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/deviation_checks/advanced_attempt1.json` | OK |

JA/EN逐語・gold判定(MAJOR/MINOR・origin)は上記REPORT第3章の表に完全収録済み
(本ファイルへの再転記は省略、ソースを正とする)。

### 4-3. changed_causality代表事例(Hormuz B-2追加補足)

`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§E2E run_03に、B-2と別の
changed_causality事例が記載済み: JA「その価格が一段落したのはそのためです」
(要約)→EN `"That is why the price pulled back only once after the fee proposal
was withdrawn, and then returned to a high level."`、`changed_causality=true`・
`changed_certainty=true`・`related_fact_id=HF-009`。案B(JA 1回差し戻し)発動後、
Standard段で**別のja_source MAJOR**(`changed_scope=true`、HF-009)が再発しSTOP
(2026-09-29、run_03)。

### 4-4. notes_for_writer 12件(Hormuz Ledger)

`er019_output/family_x_refresh_e2e_01/hormuz/run_02/research_ledger/verified_fact_ledger.txt`
に`notes_for_writer`が**12件**出現することを確認(`grep -c`実測)。run_03の同ファイル
(`.../run_03/research_ledger/verified_fact_ledger.txt`)も同じく12件、かつ両ファイルは
MD5一致(run_03がrun_02のLedgerをそのまま複製・reuseしているため=同一入力での
非決定性測定に使える組)。

### 4-5. 非決定性測定用セット

Hormuz run_02とrun_03は**同一Ledger**(`verified_fact_ledger.txt`のMD5一致確認済み)
から出発しているが、JA Writer/Checkerの実行自体はrun_02→STOP後にrun_03で再実行
されたものであり、両runのJA本文・Checker判定を比較すれば「同一入力での判定一致率」
の実測データとして使える(既存の`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md:688`
に「Checker非決定性の定量実測(同一入力n回判定の一致率)は**未実施**」と明記されて
おり、GPT-6 Trialが最初の定量測定機会になる)。

### 4-6. 生成Role比較用: Family X代表記事(Hormuz・Meta)入出力ペア

| 記事 | run | JA Ledger | JA本文 | Advanced | Standard |
|---|---|---|---|---|---|
| Hormuz | run_03 | `.../hormuz/run_03/research_ledger/verified_fact_ledger.txt` | `.../hormuz/run_03/ja_writer/revision2.md`(推定パス、個別sha256未取得) | `.../hormuz/run_03/b1b/article.md`(REPORT記載、`title="The Fee Plan Leaves, High Oil Prices Stay"`) | STOP(未完成、run_03はStandard段MAJORでSTOP) |
| Meta | run_03 | `.../meta/run_03/`配下(存在確認OK、詳細は並行タスクMeta E2E完了後に確認要) | 未確認(並行タスクが編集中のため本タスクでは深追いしていない) | 未確認 | 未確認 |

**sha256個別収集は本タスクでは未実施**(存在確認のみ、コピー・追加取得はしていない、
上記表の空欄は「未確認」であり「存在しない」ではない)。

---

## 5. Evidenceの所在

| 対象 | パス/REPORT |
|---|---|
| Hormuz run_01〜03(STOP evidence、案B発動記録) | `er019_output/family_x_refresh_e2e_01/hormuz/run_01,02,03/`、`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`§E2E run_03(L1155以降) |
| Meta run_02/run_03 | `er019_output/family_x_refresh_e2e_01/meta/run_03/`(run_02は並行Sonnetタスクが編集中、Meta E2E完了後に追記欄を空けておく。**Meta E2E完了後の追記が必要**) |
| 調査・レビューREPORT | `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`(commit `247e0a1f`)、`LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_REPORT.md`(commit `2c4f5ed3`) |
| OPEN-233本文 | `OPEN_ITEMS.md:416` |
| Family X各Trialのdeviation json | §4-2/4-3参照(A群5件・B群4件・Hormuz B-2追加分) |
| コスト調査REPORT | `NEWS-FAMILY-X-JA-FACT-DOUBLE-CHECK-COST-01_REPORT.md`、`LEDGER-DEVIATION-CHECKER-SEARCH-COST-RECONCILIATION-01_REPORT.md` |

**Meta E2E完了後の追記欄(空欄、後続タスクが埋める)**:
- Meta run_02/run_03のraw_usage_log集計:
- Meta記事のAdvanced/Standard完成状況:

---

## 6. GPT-6 Trial計画の下書き(決定しない、材料のみ)

### 6-1. 比較軸

- **Quality**: 重大fixture検出率(§4-1の9種、目標9/9維持)、A群5件の再現検出率、
  不要BLOCK率(B群4件・B-1の4回独立発生パターンが再現するか)、同一入力での
  判定一致率(§4-5のHormuz run_02/03 Ledgerを再利用、新規測定)。
- **Cost**: Role別1 call中央値(§3)×fixture数×2モデル。
- **Delivery**: latency中央値(§3、Checker33秒・Writer/Translation15〜36秒)。

### 6-2. Role比較順(案、優先度順)

1. Checker(JA Fact Check・EN Advanced・Standard共通の`run_deviation_check`)
   — OPEN-233の主目的、Evidence(§4)が最も揃っている。
2. Writer(JA Original/R1/R2)
3. Translation(Advanced忠実英訳)
4. Standard simplification
5. Comment/Key Phrase(低優先、reasoning effort差異[high/medium]がある点に注意)

### 6-3. 反復回数案

n=5(委任文の提示値)。§4-5のHormuz run_02/03は既にn=2の実データがあるため、
n=5達成には追加3回のCheckerコール(同一Ledger・同一JA本文に対する再判定)が
必要になる見込み(未確定、Trial設計時に確定)。

### 6-4. 費用概算(粗い概算、Trial設計確定前の参考値)

Checker中央値¥0.90(§3-1)を基準に、9 fixture×n=5×2モデル(新旧)=90回
→ 概算¥81(Checkerのみ、GPT-6側の単価が未確認のため**旧モデル価格を仮置き**、
実際はGPT-6単価判明後に再計算必須)。A群/B群9件を同様にn=5×2で流す場合は
90回追加で概算¥81。Writer/Translation/Standardまで含めた全Role比較は
§3-2の中央値(¥0.0019〜0.0055/call、Checkerより1桁安い)から、記事1本
(Hormuz相当、約22コール/run)×n=5×2モデル=220回で概算¥数十円程度と
見積もられるが、**GPT-6の単価が未確認のため全て「旧モデル単価を仮置きした
参考値」であり、確定額ではない**。

### 6-5. STOP条件・Guardrail案(材料、決定しない)

- 既存のfail-closed require_model()契約を維持したまま、DEV/Trial側では
  `require_model_or_override(process, model, override_reason)`(§2-1)を使い
  Production側のContractを一切変更せずにGPT-6を試せる(既存の仕組みで対応可能、
  新規メカニズム不要)。
- 予算上限・Opus起動制限は既存PM_GOVERNANCE.mdの管理IDループ上限(Sonnet最大4回・
  Opus最大1回)に従う。

### 6-6. GPT-6のmodel_id登録手順(変更しない、手順のみ記載)

GPT-6のmodel_id文字列自体は**未確認**(本タスクでは調査不可、OpenAI側の正式
名称発表を待つ必要がある)。登録する場合は`er006_model_routing_contract_01.py`
の`PROCESS_MODEL_MAP`の対象キーの値を差し替えるか、DEV/Trial用に新しい
`TRIAL_MODEL`定数を追加し`require_model_or_override()`経由でoverride_reason
付きで試す(Contract本体は変更せず、Trialスクリプト側だけで完結させる)方式が
考えられる(§2-3のハードコード15件レビューが前提)。

---

## 未確認事項一覧(まとめ)

- Query Planning/Topic Selection/Natural English QA/Pronunciation resolver/
  Shared Point Blueprint/Key Phrase抽出個別分離の実測model_id・reasoning effort。
- Family A(News)・Family C個別のmodel解決チェーン(Family Cは`model`引数の
  委譲設計のため呼び出し元まで未追跡)。
- Standard/Comment1-4/KP抽出/KP explanation/In One LineのCost/Latency個別分離
  (raw_usage_logのstageラベル欠落のため)。
- Meta run_02/run_03のraw_usage_log集計(並行Meta E2Eタスク完了待ち)。
- GPT-6のmodel_id文字列・料金体系(未発表/未確認)。
