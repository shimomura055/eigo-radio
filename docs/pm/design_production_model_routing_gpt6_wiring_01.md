# PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 配線計画書 v1

Status=PLANNED(設計のみ。Production code未変更、¥0)。作成 2026-10-08(委任_01)。OPEN-241。
本書は Opus条件C(重要変更のProduction採用前)の必須レビュー対象。配線は委任_02以降、Opusレビュー後かつ FACTLOCK-WRITER-REDESIGN-TRIAL-01 の生成完了後。

## §0 ユーザー決定と根拠数値

ユーザー判断7(逐語、2026-10-08): 「全6-luna化をProduction方針として進めてOK(ネガ判定は微妙(同等)、コストメリットが大きく止める理由がない)」。背景発言: 「すべて6.0に変えるつもりだったし、そうなっていたと思ってました。上位互換で価格も安いのに、6.0に変えない理由がありません。」「Checker含めて、現状5.6を使っているものは6.0にTrial的に変更して…追って6.0の検証はしっかりやればいい。」

根拠数値(ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01 RESULT.md、MEASURED、完走19対19、baseline=5.6対all6=6-luna):
- 費用/本 ¥9.46→¥4.29、所要 491→341秒、Checker候補/記事 8.26→5.95。
- 生成側の事実NG: 評価者で方向が割れ差不明(JA R2 軽微 0.53→0.37/記事、R0軽微 11→12、重大 0→1。全体の重大は2件のみで床効果)。
- T-B(frozen既知NG再判定、n=2): 重大検出 1/14→4/14、軽微 3/32→4/32。
- 悪化側: EN must-fix 0/19→6/19、EN Advanced deviation STOP 0→2、保留/記事 0.05→0.26。
- 9/29 GPT6-MODEL-COMPARISON-TRIAL-01: Checker比較は6≥5.6(重大検出優位、gold一致率90%対70%、不要BLOCK率同等75%、latency+34%)。価格 gpt-6-luna Input $0.10 / Cached $0.01 / Output $0.50 per 1M(gpt-5.6-lunaは $0.20/$0.02/$1.20、DECISION_LOG 12925-12933行付近)。
- 限界(RESULT.md §4): N小、LLM単独評価(評価者差が群間差より大)、STOP10本は評価対象外、brief 12本(3テーマ)のみ。

## §1 変更対象の棚卸し(事実)

### 1-1 routing契約(er006_model_routing_contract_01.py L30-36)7定数
QUERY_PLANNER_MODEL / TOPIC_SELECTOR_MODEL / RESEARCH_MODEL / WRITER_MODEL / WRITER_FACT_CHECK_MODEL / SUPPORT_MODEL / SUPPORT_FACT_CHECK_MODEL(全て "gpt-5.6-luna")。
PROCESS_MODEL_MAP(L65-110)は上記定数を参照する派生: QUERY_PLANNING, TOPIC_SELECTION, EVIDENCE_PACK/VFL/VERIFICATION(RESEARCH), B1_WRITER/A2_WRITER, WRITER_FACT_CHECK, B1_SUPPORT/A2_SUPPORT, SUPPORT_FACT_CHECK、派生キー PROPER_NOUN_EXTRACTION / SHARED_POINT_BLUEPRINT / STANDARD_A2_ADAPTATION / NATURAL_ENGLISH_ADAPTATION(=WRITER_MODEL)、KEY_PHRASE_ADVANCED_EXPLANATION(=SUPPORT_MODEL)。FAMILY_X_FLASH_LITE_TTS(Gemini)・PROCESS_PROVIDER_MAP(Perplexity/TTS/ASR)は対象外。
定数の値変更だけでPROCESS_MODEL_MAPの全キーが連動して切り替わる構造。

### 1-2 require_model系 呼び出し(Git管理*.py、output除外、テスト除く)
- 234行/多数ファイル(Trial runner含む)。processキー別: label/process変数経由 約120、"WRITER_FACT_CHECK" 40、"A2_WRITER" 18、"B1_SUPPORT" 17、"B1_WRITER" 10、"A2_SUPPORT" 5、"VFL"/"VERIFICATION"/"EVIDENCE_PACK"/"SUPPORT_FACT_CHECK"/"SHARED_POINT_BLUEPRINT"/"PROPER_NOUN_EXTRACTION" 各1。Production主線: er003_discovery_focus_staged_production_01.py(4)、er012_b_family_production_runner_01.py(3)、er003_v1_n3_01_*_generate.py、er019_family_x_*_runner等。大半はTrial scriptで、定数が変われば同時に6-lunaへ変わる(旧Trial再実行時は結果が変わる点に注意)。

### 1-3 gpt-5.6-lunaリテラル直参照(routing契約を経由しない)
- Git管理*.py全体: コメント除く非テスト 207行/89ファイル、test系を含め合計312行(うちtest系ファイルは19ファイル)。うちrouting契約の定数7行が1-1。
- 契約外の直参照でProduction寄りのもの:
  - gather_topic.py:29 / er002_topic_adapter.py:21 `MODEL_SEARCH = "gpt-5.6-luna"`(Topic調査、web_search使用)
  - er006_research_coverage_gate_01.py:17 `GATE_MODEL`(「検証用固定。Production本配線時は…」とコメントあり)
  - er019_family_x_kp_explanation_01.py:43 `MODEL`(Key Phrase explanation)
  - er018_fiction_story_dna_e_axis_redesign_01.py:425,445 / er026_family_z_fiction_production_runner_01.py:696 `model_id != "gpt-5.6-luna"` 検査(Fiction側で5.6を前提に判定。6-luna化で不一致判定になる恐れ)
  - er009_n1_routing_governance_10_actual_model_cost.py:25 / compute_topic_cost.py:11-13 / er015_*系: 単価表引き。
  - 残りはTrial/cost_compute/bench系(旧Trial再現用)で、5.6のまま凍結する選択肢がある。
- 注意(委任文との差異): 委任文は cost logger(er005_cost_logger.py)に単価表がある想定だったが、同ファイルに単価表は無い(Grep gpt-5.6-luna|pricing 該当なし)。単価は `er005_output/cost_baseline_01/pricing_snapshot.json`(gpt-6-luna 0件)と、各scriptに散在するhardcode表(例 er009_n1_routing_governance_10_actual_model_cost.py:25、er052_open233_stage1_phase1_recall_check_01.py:29 は両モデル併記)から読まれる。pricing_snapshot.jsonを参照するpyは101ファイル。6-luna未登録のままでは費用が0円計上になる(本日Trialで確認済み)。追加すべき値: Input 0.10 / Cached 0.01 / Output 0.50(+Cache writes 0.125)$/1M。

### 1-4 テストのhardcode
`gpt-5.6-luna`を含む*_test*.py等は17ファイル: er003_v1_en_direct_vfl_01_generate_test_01 / er003_v1_n3_01_advanced_adaptation_generate_test_01 / er003_v1_n3_01_standard_a2_generate_test_01 / er006_model_routing_contract_01_test(`approved == "gpt-5.6-luna"`を検証、行24付近) / er008_n8_cost_compute_pricing_fix_24_test_01 / er009_n1_routing_governance_10_legacy_scan_test / er012_e_family_entertainment_two_level_runner_test_01 / er019_family_x_b3_production_wiring_01_test_01 / er019_family_x_entertainment_production_runner_01_test_01 / er019_family_x_ja_recheck_retry_01_test_01 / er019_family_x_ja_writer_o_r1_r2_01_test_01 / er019_writer_run_summary_reconstruction_01_test_01 / er020_tts_retry_local_rewrite_01_test_01 / er050_gpt6_checker_comparison_trial_01_test_01 / er052_all6_writer_trial_01_test_01 / generate_test.py / tts_test.py。
(generate_test.py・tts_test.pyはファイル名がtest系だが実体の役割は未確認。gather_topic.py・er002_topic_adapter.pyもtest系grepに混入。)
配線時は期待値を `routing.<定数>` 参照へ寄せるか、gpt-6-lunaへ更新する必要がある。

## §2 互換性の既知/未知(6-lunaでの動作)

| 工程 | 6-luna確認 | 根拠 |
|---|---|---|
| JA Writer R0-R2(previous_response_id使用: er019_family_x_ja_writer_o_r1_r2_01) | 確認済み | 2026-10-08 ALL-6-LUNA Trial、24/24本をraw_usageで実測 |
| JA/EN Fact Check(WRITER_FACT_CHECK) | 確認済み | 同上 |
| EN化(NATURAL_ENGLISH_ADAPTATION、EN Advanced) | 確認済み(品質は§0のとおりEN STOP/must-fix増) | 同上 |
| Production Checker(OPEN-233経路) | 確認済み | 2026-09-29 GPT6-MODEL-COMPARISON-TRIAL-01、OPEN-233 Trial群 |
| Production側Fact Checker / Ledger Deviation v2の5.6箇所 | 未確認(routing経由か直参照かはPhase 2で要精査) | — |
| Standard A2 Adaptation(STANDARD_A2_ADAPTATION) | 未確認(Writer系だが専用prompt・6000語ライン) | — |
| Shared Point Blueprint / Proper Noun Extraction | 未確認 | — |
| Research(Evidence Pack/VFL/Verification、json_schema strict、reasoning=medium、er006_pool_pilot_01_research.py) | 未確認 | — |
| Research Coverage Gate(GATE_MODEL直参照、json_schema strict) | 未確認 | — |
| Support B1/A2(Key Phrase選定・正規化、reasoning effortあり) | 未確認 | — |
| KEY_PHRASE_ADVANCED_EXPLANATION / kp_explanation / key_phrase_llm_fallback(reasoning effort) | 未確認 | — |
| Query Planner / Topic Selector(gather_topic.py、web_search tool使用) | 未確認(web_search互換含む) | — |
| Fiction系の `model_id` 検査(5.6固定比較) | 未確認(コード修正要の可能性) | — |

未検証のAPIパターン: web_search tool(er002_*、gather_topic.py)、json_schema strict + reasoning(Research/Gate)。previous_response_idはJA Writerで6-luna確認済み。

## §3 段階配線案

### Phase 1(≈1時間): 確認済み工程
- routing契約の WRITER_MODEL / WRITER_FACT_CHECK_MODEL を "gpt-6-luna" へ(定数2行)。ただしWRITER_MODEL連動で PROPER_NOUN_EXTRACTION / SHARED_POINT_BLUEPRINT / STANDARD_A2_ADAPTATION / NATURAL_ENGLISH_ADAPTATION / A2_WRITER / B1_WRITER も同時に切り替わる。§2で未確認の3派生キーは現構造では分離不可のため、(a)派生キーに個別定数を設ける構造変更、(b)Phase 1に含めて1 call smokeを先に行う、のいずれかが必要(Opus論点)。
- pricing_snapshot.json(および配線対象scriptの単価参照)へ gpt-6-luna 追加、0円計上防止。
- 受入: 回帰テスト全件PASS(§1-4のhardcode更新後)、fail-closed契約維持(require_modelの例外経路テスト)、各processの実使用model_idをraw_usage_logで実測、cost.jsonが0円計上でないこと。

### Phase 2(≈1時間): Checker
- Production CheckerのFact Checker/Ledger Deviation v2の5.6箇所の特定とroutingまたは6-lunaへの統一。OPEN-233経路は既に6-luna。
- 受入: Phase 1同様+Checker既存回帰、model_id実測。

### Phase 3(≈1〜2時間): 未確認工程
- Research(Evidence Pack/VFL/Verification)、Research Coverage Gate、Support B1/A2、Key Phrase explanation/fallback、Query Planner、Topic Selector(MODEL_SEARCH 2箇所)、Fiction側model_id検査。
- 各工程1 callのsmoke probe(≈¥1〜5)で互換確認後に切替。3a(json_schema+reasoning工程)と3b(web_search使用工程)に分けてもよい。
- 受入: smoke probeでAPI成功・schema適合・model_id実測、回帰PASS、費用記録確認。

### 一括切替案との比較
- 一括: 定数7行+単価表+テスト更新を1回で。利点: 作業が1回、契約が一貫。欠点: §2の未確認工程(web_search、strict schema+reasoning)が問題を起こすと全量が同時に停止、原因切り分け困難、切り戻しも全量。
- 段階: 利点: 未確認工程を1 call probeで先に検証、問題Phaseのみ戻せる。欠点: 5.6と6-lunaが一時併存、作業が3回、WRITER_MODEL連動の派生キー分離には構造変更が必要。
- 段階案の根拠(事実): §2に未確認工程が複数ある、切り戻しの影響範囲が小さい。

## §4 リスクと緩和

- 6-luna Fact Check厳格化によるSTOP増(EN must-fix 0/19→6/19、EN Advanced STOP 0→2): STOPの許容/閾値調整は別論点(本計画の範囲外、ユーザー判断)。
- 評価者差: 生成NGは評価者で方向が割れ、品質同等は「差不明」であり「改善」ではない。保留/記事が0.05→0.26へ増加(人間確認負荷)。
- 5.6固有挙動に依存するprompt: 網羅調査は未実施(未確認)。Fiction側 `model_id != "gpt-5.6-luna"` 検査は直接依存の例。
- 切り戻し手順: routing契約の定数を "gpt-5.6-luna" へ戻し(Phase 1は2行、全Phase後は7行)、pricing_snapshot追記は残す(無害)。回帰テスト全件実行。Phase単位で別commitにしてgit revertで戻せるようにする。
- 並行作業: FACTLOCK Trial生成中のコード変更は条件同一性を損なう。

## §5 Opus条件Cレビュー論点(候補)

1. WRITER_MODEL連動の派生キー(Blueprint/Proper Noun/Standard A2/EN化)をPhase 1で一括切替するか、個別定数で分離する構造変更を入れるか。
2. 「品質は同等(差不明)、コストは約半額」を根拠にした、EN must-fix/STOP増加と保留増加の運用上の扱い(許容か、Phase 1受入条件にするか)。
3. 未確認工程(web_search、strict schema+reasoning)のsmoke probe受入条件の十分性(1 callで足りるか)。
4. pricing_snapshot.jsonへの単価追記方式(散在hardcode表の一元化は別タスクか)と0円計上防止の検査方法。
5. Trial旧scriptの再現性(定数変更で過去Trial再実行の結果が変わる)の扱い。

## §6 実施タイミング

FACTLOCK-WRITER-REDESIGN-TRIAL-01(進行中)の生成完了後。理由: メモリ負荷、Trial条件同一性(生成中にroutingを変えない)、Git/SSOT編集の直列化。Opus条件Cレビュー後。

## §7 費用・時間見積

- 費用: smoke probe合計≈¥20以内(Phase 3 各1 call≈¥1〜5×数工程。Phase 1/2は既存Trial結果で確認済みのため原則追加課金なし、model_id実測は次回量産時のログで確認)。
- 時間: Phase 1 ≈1時間、Phase 2〜3 ≈1〜2時間。
