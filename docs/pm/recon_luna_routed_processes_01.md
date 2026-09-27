# Recon: Production上でLuna系モデルへルーティングされている処理の棚卸し

管理ID: GPT-6-LUNA-PRODUCTION-ROLE-AB-TRIAL-01(準備: 経路インベントリ)
種別: read-only調査(¥0、API呼び出しなし、コード/SSOT変更なし)
作成日: 2026-09-27

本ファイルは将来の「現行Luna(gpt-5.6-luna) vs GPT-6 Luna」A/B Trial準備の
ための棚卸しであり、それ自体はTrialの実行・計画確定ではない。Trial本体は
ユーザー指示があるまで開始しない。

---

## 1. Model Routing Contract上の役割別モデル割当(CURRENT_SPEC/報告書からの逐語引用+根拠)

正式SSOT: `CURRENT_SPEC.md` 1667〜1696行「Model Routing Contract」節。
コードSSOT: `er006_model_routing_contract_01.py`(`PROCESS_MODEL_MAP`/
`PROCESS_PROVIDER_MAP`、`require_model()`/`require_provider()`)。

| 役割(Process) | Approved Model | 根拠(コード行) | 根拠(SSOT行) |
|---|---|---|---|
| Query Planning | `gpt-5.6-luna` | `er006_model_routing_contract_01.py:30` | `CURRENT_SPEC.md:1674` |
| Topic Selection | `gpt-5.6-luna` | `er006_model_routing_contract_01.py:31` | `CURRENT_SPEC.md:1675` |
| Evidence Pack / VFL / Verification(Research) | `gpt-5.6-luna` | `er006_model_routing_contract_01.py:32` | `CURRENT_SPEC.md:1676` |
| B1 Writer / A2 Writer(Deviation Check含む) | `gpt-5.6-luna` | `er006_model_routing_contract_01.py:33` | `CURRENT_SPEC.md:1678` |
| Writer Fact Check | `gpt-5.6-luna` | `er006_model_routing_contract_01.py:34` | `CURRENT_SPEC.md:1679` |
| B1 Support / A2 Support(Key Phrase選定・正規化含む) | `gpt-5.6-luna` | `er006_model_routing_contract_01.py:35` | `CURRENT_SPEC.md:1680` |
| Support Fact Check | `gpt-5.6-luna` | `er006_model_routing_contract_01.py:36` | `CURRENT_SPEC.md:1681` |
| Proper Noun Extraction(発音Ledger用抽出) | `gpt-5.6-luna`(WRITER_MODELと同一、新規モデル追加なし) | `er006_model_routing_contract_01.py:77-80` | — |
| Shared Point Blueprint(A2/B1 Point構造整合) | `gpt-5.6-luna`(同上) | `er006_model_routing_contract_01.py:81-85` | — |
| Standard A2 Adaptation(6,000語版生成) | `gpt-5.6-luna`(同上) | `er006_model_routing_contract_01.py:86-90` | — |
| Natural English Adaptation(Advanced生成) | `gpt-5.6-luna`(同上) | `er006_model_routing_contract_01.py:91-95` | — |
| A2 Reading Resolver(読み解決、A2_SUPPORTとして) | `gpt-5.6-luna`(`require_model_or_override("A2_SUPPORT", ...)`) | `er011_a2_reading_resolver_01.py:61-62` | — |
| TTS | Gemini `gemini-2.5-pro-preview-tts`(EN)/`gemini-3.1-flash-tts-preview`(JA) | — | `CURRENT_SPEC.md:1682` |
| ASR / Audio QA | OpenAI `gpt-4o-mini-transcribe`(Primary、SSOTは`er006_asr_provider_routing_01.py`) | — | `CURRENT_SPEC.md:1683` |
| Exception Search | Perplexity Search API | `er006_model_routing_contract_01.py:41` | `CURRENT_SPEC.md:1677` |

**Fail-Closed契約**: 規定外Model/未指定Modelは`ModelContractViolation`を
API call実行前に送出する(`er006_model_routing_contract_01.py:104-123`)。
Regression: `er006_model_routing_contract_01_test.py`、Static audit:
`er006_model_routing_contract_01_static_audit.py`。

**適用範囲の注記(既存)**: 上記契約は、production到達可能な呼び出し箇所
(N3/Pool pipeline: `er003_v1_n3_01_articles_generate.py`・
`er003_v1_n3_01_scaffold_generate.py`・`er006_pool_pilot_01_*.py`)にのみ
適用(`CURRENT_SPEC.md:1691-1696`)。Family X(er019_*)・Family E
Entertainment(er012_e_*)は、これらモジュールを`import`して再利用または
`routing.WRITER_MODEL`/`routing.SUPPORT_MODEL`を直接参照する設計であり、
別モデルへの切替口は存在しない(下記2節)。

---

## 2. コード上の実際の割当(Production経路ごと)

### 2-1. Family X(`er019_family_x_*`)+ 共有Writer/Support基盤(`er003_v1_n3_01_*`)

| 関数/呼び出し箇所 | 行番号 | model_id | reasoning_effort | Structured Output | 呼び出し回数/記事(概算) |
|---|---|---|---|---|---|
| Research(Evidence Pack/VFL) `er003_v1_en_direct_vfl_01_generate.py::run_research`系 | L176周辺(`text.format.json_schema`) | `gpt-5.6-luna`(`routing.WRITER_MODEL`経由の`MODEL`変数、L57) | "high"(`WRITER_REASONING_EFFORT`連鎖、L58) | あり(`FACT_LEDGER_JSON_SCHEMA`) | 1回(web_search呼出し複数、実測7回/記事は3-4節参照) |
| Ledger Verification `run_verification`系 | L259周辺 | `gpt-5.6-luna` | "high" | あり(`VERIFICATION_JSON_SCHEMA`) | 1回 |
| Deviation Check(Fact Check、hook_aware) `run_deviation_check` | L773-812(`text.format.json_schema`はL812) | `gpt-5.6-luna`(既定`model=MODEL`) | "high" | あり(schema変数) | 2〜6回(Original直後・R2直後×[初回+MAJOR時must-fix retry+recheck]) |
| Family X Storyline B3 Fact Selection `er019_family_x_storyline_b3_fact_selection_01.py::_call_once/run_storyline_b3_selection` | L187-209、schema L195 | `gpt-5.6-luna`(呼び出し元`vfl01.MODEL`を渡す、`er019_family_x_entertainment_production_runner_01.py:145`) | 呼び出し元指定(`vfl01.REASONING_EFFORT`="high") | あり(`STORYLINE_B3_JSON_SCHEMA`) | 1回 |
| JA Writer Original/R1/R2 `er019_family_x_ja_writer_o_r1_r2_01.py::call_fresh/call_with_previous_response_id` | L192-215 | `gpt-5.6-luna`(`WRITER_MODEL = vfl01.MODEL`、L48) | 呼び出し元`WRITER_EFFORT = vfl01.REASONING_EFFORT`="high"(L49) | なし(plain text、記事本文) | 3回(Original/R1/R2、previous_response_id chain) |
| B1/A2 Scaffold Comment1-4+Preview `er003_v1_n3_01_scaffold_generate.py::run_b1_scaffold/run_a2_scaffold` | L410-505付近 | `gpt-5.6-luna`(`_b1_support_model()`/`_a2_support_model()` = `routing.require_model("B1_SUPPORT"/"A2_SUPPORT", routing.SUPPORT_MODEL)`、L51-56) | "high"(`SELECTOR_REASONING_EFFORT`連鎖、複数モジュール経由) | なし(plain text) | 5回×2level=10回/記事 |
| Key Phrase選定/正規化/重複QA `run_key_phrase_selection/run_key_phrase_canonicalization/run_key_phrase_redundancy_qa` | L190-352 | `gpt-5.6-luna`(同上SUPPORT_MODEL) | "high" | 未確認(script未読了分、既存契約はSUPPORT_MODEL固定のみ確認) | 3回×2level=6回/記事 |
| Standard A2 Adaptation `er003_v1_n3_01_standard_a2_generate.py` | L419 | `gpt-5.6-luna`(`routing.require_model(PROCESS_LABEL, routing.WRITER_MODEL)`) | "high"(Writerと同一信頼度) | なし | 1回+Fact Check |
| Advanced(Natural English Adaptation) `er003_v1_n3_01_advanced_adaptation_generate.py` | L444 | `gpt-5.6-luna`(同上) | "high" | なし | 1回+Fact Check |
| Family X B1/A2 Support model参照(Audio Production Runner側の再露出) `er019_family_x_audio_production_runner_01.py::_b1_support_model/_a2_support_model` | L98-103 | `gpt-5.6-luna`(同上SUPPORT_MODEL、scaffold_generate.pyと同一呼び出し) | "high" | — | (2-1のScaffold行と重複計上しない、同一契約の別露出点) |

Family E Entertainment(`er012_e_family_entertainment_two_level_runner_01.py`)は
`er003_v1_n3_01_advanced_adaptation_generate`/`standard_a2_generate`/
`scaffold_generate`/`assemble`/`tts_generate`をそのまま`import`して再利用
しており(L56-60)、Family Xと同一のLuna経路をたどる(別モデル無し)。

### 2-2. Trial専用/legacy(Family A/B/C、旧番号体系)経路 — 別表(区別)

Family A/B/C(Legacy/Backup化済み、PM-FAMILY-SYSTEM-MIGRATION-ABC-TO-XYZ-
2026-09-27でActive FamilyはX/Y/Zへ移行済み)の`er009_*`/`er011_*`/`er012_*`/
`er013_*`配下の多数のtrialスクリプトは、いずれも`vfl01.MODEL`/
`routing.WRITER_MODEL`等を参照して同じLuna(`gpt-5.6-luna`)を使う設計が
大半だが、一部は**DEV/Trial専用の明示override経路**
(`require_model_or_override(process, model, override_reason=...)`、
`er006_model_routing_contract_01.py:134-153`)を使い、意図的に別modelで
実験している。今回の棚卸しで実際に非Lunaのmodel_idを確認できた箇所:

| ファイル | model_id(実測) | 位置づけ |
|---|---|---|
| `er025_output/pronunciation_resolution_phase2_evidence_01/raw_usage_log.jsonl` | `gpt-5.6-sol`(`en1`/`en2`/`ja2`のevidence実行ログ、2026-09-27 06:31 UTC) | PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(進行中、他Agent作業中)のPhase 2 evidence gathering。Production Model Routing Contract外の値であり、Production経路へ配線済みではない(詳細は3-4節「注意点」参照、本ファイルはread-onlyで参照したのみで編集していない) |

上記以外の`gpt-5.6-luna`/`luna`文字列を含む108ファイルは、大半が
`er005_*`/`er006_*`/`er008_*`〜`er018_*`のcost比較・trial・reproスクリプト
であり、production到達可能な経路(2-1節)には含まれない。全件の個別
model_id確認は本Reconのスコープ外(read-only準備作業のため、Trial設計
確定時に対象を絞って再確認する)。

---

## 3. 1記事あたり実測コスト・latency(Meta run_01・Hormuz run_02)

出典: `er019_output/family_x_b3_production_wiring_01/run_01/cost.json`
(topic: Meta/Museロールバック記事)、`er019_output/family_x_b3_diversity_
trial_01/hormuz/run_02/cost.json`(topic: Hormuz、B3 Diversity Trial内の
安定コピー、`hormuz__run_02`という別Agent編集中のディレクトリではなく
`hormuz/run_02`を参照)。

### 3-1. Meta run_01(フルパイプライン、Research/Ledgerから実行)

| Stage | 費用(JPY) | model_id(実測) | latency | 備考 |
|---|---|---|---|---|
| research | 14.473 | `gpt-5.6-luna`(`storyline_b3/runtime_evidence.json`は別stageだが同様に記録あり) | 未計測(response_idのみ記録、latency_secondsフィールド無し) | web_search_call_count=7 |
| ledger(verification) | 14.266 | `gpt-5.6-luna` | 未計測 | VERIFIED 15/AMBIGUOUS 0/REJECTED 0 |
| storyline_b3 | 0.668 | `gpt-5.6-luna` | 24.28秒(`storyline_b3/runtime_evidence.json`実測) | attempts=1、retried=false |
| ja_original | 0.235 | `gpt-5.6-luna` | 未計測 | |
| ja_r1 | 0.243 | `gpt-5.6-luna` | 未計測 | previous_response_id chain |
| ja_r2 | 0.260 | `gpt-5.6-luna` | 未計測 | |
| advanced | 7.839 | `gpt-5.6-luna` | 未計測 | |
| standard | 6.673 | `gpt-5.6-luna` | 未計測 | |
| **合計** | **44.658 JPY** | | | |

### 3-2. Hormuz run_02(JA Writer段階でMAJOR Deviation発生、must-fix retry込み)

| Stage | 費用(JPY) | 備考 |
|---|---|---|
| ja_original | 0.225 | |
| ja_original_check | 1.785 | Fact Check(Deviation Check)、MAJOR検出 |
| ja_original_must_fix | 0.850 | must-fix rewrite 1回 |
| ja_original_check_retry | 0.277 | 再Check |
| ja_r1 | 0.549 | |
| ja_r2 | 0.522 | |
| ja_r2_check | 0.697 | |
| ja_r2_must_fix | 0.713 | 同様にMAJOR再発、must-fix rewrite |
| ja_r2_check_retry | 0.383 | |
| advanced | 1.828 | |
| standard | 0.915 | |
| **合計** | **8.745 JPY** | (research/ledgerはLedger再利用のため¥0、storyline_b3は別ファイル`family_x_b3_diversity_trial_01/cost.json`のhormuz_run_01_partial値1.047 JPYのみ確認できた。run_02側のstoryline_b3個別値は本ファイルには無し) |

**latencyについて**: 上記のうちruntime_evidence.jsonへ`latency_seconds`
実測値を持つのはstoryline_b3のみ(24.28秒/記事、Meta run_01)。Research/
Ledger/Writer/Support/Advanced/Standardの各stageはresponse_id記録のみで
経過時間を記録しておらず、「未計測」として扱う。

---

## 4. A/B比較の候補設計(案のみ、Trial未実施)

**固定するもの(候補)**:
- TTS(model・Batch/Standard実行モード・voice設定)は完全固定し、比較対象に含めない。
- 入力: 既存確定記事のFull Ledger(`storyline_b3/full_ledger.json`)/JA
  Original(`ja_writer/original.md`)等、既に承認済みのテキストを再利用し、
  Luna側とGPT-6 Luna側で同一inputを与える(新規Topic Selection/Research
  からのやり直しはしない=Query Planning/Research/Verificationの結果自体は
  固定)。
- Prompt文字列(developer_message/user prompt template)は同一SHA256で固定
  (既存runtime_evidence.jsonの`prompt_shas`/`verbatim_shas`と同じ仕組みを
  流用可能)。
- reasoning_effort="high"(Writer/Support共通)を両モデルで揃える(GPT-6 Luna
  側が異なるreasoning effort語彙を要求する場合は、公式ドキュメント確認後に
  対応表を作る、推測しない)。
- previous_response_id chain方式(JA Writer O→R1→R2)は同じ手順を両モデルで
  踏襲する。

**比較指標(候補)**:
- Fact Check(Deviation Check)MAJOR検出率・件数(既存`deviation_checks/*.json`
  のseverity集計)
- 逸脱検出の一致度(同一記事に対しLuna判定とGPT-6 Luna判定が同じ箇所を
  MAJORと判定するか)
- Key Phrase選定・正規化の重複率(既存`run_key_phrase_redundancy_qa`の
  出力を両モデルで比較)
- 費用(input/output/cached tokens×単価)
- latency(response単位の実測秒数、現状Writer/Support系はlatency未記録の
  ためTrial実施時に記録項目として追加する必要がある)

**必要な差し替え点(model_id定数の所在)**:
- `er006_model_routing_contract_01.py`の`WRITER_MODEL`/`SUPPORT_MODEL`/
  `WRITER_FACT_CHECK_MODEL`/`SUPPORT_FACT_CHECK_MODEL`/`RESEARCH_MODEL`
  (L30-36)がSingle Source of Truthであり、A/B Trial実施時はここを書き換えず
  DEV/Trial側で`require_model_or_override(process, model, override_reason=...)`
  (L134-153)を使い、Production契約(fail-closed)を回避せずに実験する設計が
  既存の安全装置と整合する。

**1処理あたりの費用上限案**: 既存`assert_budget_ok()`
(`er019_family_x_audio_production_runner_01.py:1059`)のBudget Cap方式を
踏襲し、Trial実施時に別途ユーザー承認を得た上で具体額を設定する(本Reconでは
金額を提案しない)。

**GPT-6 Lunaの正式model_id・単価**: リポジトリ内(`er005_output/
cost_baseline_01/pricing_snapshot.json`等)に記載無し。**未確認**
(Trial計画時にHTTP GETで公式ドキュメントを確認する。本Reconでは推測しない)。
現行`gpt-5.6-luna`の単価(参考、同ファイルより): input $0.20/1M tokens、
cached input $0.02/1M tokens、output $1.20/1M tokens(Standard tier)。

---

## 5. 注意点(Luna評価に影響し得る進行中の変更)

- **読み解決(Pronunciation Resolution)Phase 2**: 
  `PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01`は現在Phase 1
  (棚卸し+設計recon、read-only、2026-09-27コミット)まで完了。Phase 2で
  A2 Reading Resolver等へLLM呼び出しが追加される計画であり、他Agentが
  作業中(`er025_output/pronunciation_resolution_phase2_evidence_01/`に
  evidence実行済み、model_idは`gpt-5.6-sol`)。この工程が将来Production
  へ配線されると、Family X記事あたりのLuna呼び出し回数・費用構成が変わる
  ため、**baseline確定後にTrialすべき**(Phase 2配線前後で1記事あたりの
  呼び出し回数が変わり、A/B比較のinput固定が崩れる)。
- **記号正規化Validatorのmust-fix retry増分**: `CURRENT_SPEC.md`
  「Family Z Writer実装時の必須適用」節(1642-1657行)にある通り、Prompt
  予防+Normalizer+Gateの3層(実質4層)構成が既存Production(Family X)へ
  適用済みだが、Gate差し戻し時のmust-fix retry(Writer/Support呼び出し
  増分)が記事によって変動する。Hormuz run_02の`ja_original_must_fix`/
  `ja_r2_must_fix`(3-2節)がこの一例であり、A/B比較で「呼び出し回数/記事」
  を固定条件として扱う場合は、MAJOR Deviation発生の有無自体がLuna側と
  GPT-6 Luna側で異なりうる点に留意が必要(同一inputでも判定モデルが変われば
  retry有無自体が変わる)。
- **Family Z(Fiction)は新設中**: Production Writerが未実装のため、本Recon
  ではコード上の実割当を確認できていない(design doc記載のみ)。A/B Trialの
  初期スコープからは除外が妥当。
- **TTS Flash-Lite検証との混同回避**: `TTS-GEMINI-3.8-FLASH-LITE-NEXT-
  TRIAL-01`はTTS側の別Trialであり、今回のLuna A/B Trialとは独立させる
  (ユーザー指示どおり「TTS固定後に実施、Flash-Lite検証と混ぜない」)。

---

## 補足: 本ファイルの作成範囲

本Reconは以下のみを対象とし、他は一切変更していない:
- 読み取り専用のGrep/Read(`er0*.py`、`CURRENT_SPEC.md`、各種
  `raw_usage_log.jsonl`/`cost.json`/`runtime_evidence.json`)
- 本ファイル(`docs/pm/recon_luna_routed_processes_01.md`)の新規作成
- `docs/pm/RESULT_PACKET_LUN.md`(一時ファイル、Git管理対象外)

他Agentが編集中と指示されたファイル(`er003_*`/`er006_*`/`er019_*`の一部、
`docs/pm/PM_GOVERNANCE.md`/`PM_BRIEF.md`、SSOT 3ファイル、
`REPORT_LEDGER`等)は読み取りのみ行い、一切編集していない。
