# PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 配線計画書 v2

Status=PROBED(設計更新+Phase 0互換probe完了。Production code未変更)。v1=2026-10-08(委任_01)、v2=2026-10-08(委任_02、Opus条件C M1〜M6/O1〜O3反映)。OPEN-241。
Opus条件Cレビュー全文: `docs/pm/opus_l2_review_production_model_routing_gpt6_wiring_01.md`(判定: 小規模な修正をしてから配線に進む)。
配線は委任_03以降、FACTLOCK-WRITER-REDESIGN-TRIAL-01の生成完了後。**未確認だった工程は「互換のみ確認、品質は未検証」**(§2)。

## §0 ユーザー決定と根拠数値(v1から変更なし)

ユーザー判断7(逐語、2026-10-08): 「全6-luna化をProduction方針として進めてOK(ネガ判定は微妙(同等)、コストメリットが大きく止める理由がない)」。背景発言: 「すべて6.0に変えるつもりだったし、そうなっていたと思ってました。上位互換で価格も安いのに、6.0に変えない理由がありません。」「Checker含めて、現状5.6を使っているものは6.0にTrial的に変更して…追って6.0の検証はしっかりやればいい。」

根拠数値(ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01 RESULT.md、MEASURED、完走19対19、baseline=5.6対all6=6-luna):
- 費用/本 ¥9.46→¥4.29、所要 491→341秒、Checker候補/記事 8.26→5.95。
- 生成側の事実NG: 評価者で方向が割れ差不明(JA R2 軽微 0.53→0.37/記事、R0軽微 11→12、重大 0→1。全体の重大は2件のみで床効果)。
- T-B(frozen既知NG再判定、n=2): 重大検出 1/14→4/14、軽微 3/32→4/32。
- 悪化側: EN must-fix 0/19→6/19、EN Advanced deviation STOP 0→2、保留/記事 0.05→0.26。Opus確認: Gate由来STOP 3/24→5/24(約13%→21%、nが小さく不確か)。
- 9/29 GPT6-MODEL-COMPARISON-TRIAL-01: Checker比較は6≥5.6。価格 gpt-6-luna $0.10/$0.01/$0.50 per 1M(gpt-5.6-lunaは $0.20/$0.02/$1.20)。
- 限界: N小、LLM単独評価、STOP10本は評価対象外、brief 12本(3テーマ)のみ。

## §1 変更対象の棚卸し(事実、v1を維持し委任_02で確定した所在を追記)

### 1-1 routing契約(er006_model_routing_contract_01.py L30-36)7定数
QUERY_PLANNER_MODEL / TOPIC_SELECTOR_MODEL / RESEARCH_MODEL / WRITER_MODEL / WRITER_FACT_CHECK_MODEL / SUPPORT_MODEL / SUPPORT_FACT_CHECK_MODEL(全て "gpt-5.6-luna")。PROCESS_MODEL_MAP(L65-110)は派生(PROPER_NOUN_EXTRACTION / SHARED_POINT_BLUEPRINT / STANDARD_A2_ADAPTATION / NATURAL_ENGLISH_ADAPTATION=WRITER_MODEL、KEY_PHRASE_ADVANCED_EXPLANATION=SUPPORT_MODEL)。FAMILY_X_FLASH_LITE_TTS・PROCESS_PROVIDER_MAPは対象外。`require_model`本体は無変更(未知model・未指定を拒否し続ける)。

### 1-2 require_model系呼び出し
Git管理*.py 約234行。大半はTrial script。定数変更で旧Trial再実行時は結果が変わる(切り戻し§4の「再実行は`require_model_or_override`で5.6明示」参照)。

### 1-3 直書き5.6参照(Opus F1〜F5で確定した所在)
- **F3(Fact Check)**: 実際にFact Check modelを決めているのは`vfl01.run_deviation_check(..., model: str = MODEL)`(er003_v1_en_direct_vfl_01_generate.py L773)の既定値`MODEL = routing.WRITER_MODEL`(L57、import時固定)。関数内に`require_model`が無くfail-closed対象外。
- **F4**: er019_family_x_kp_explanation_01.py L43 `MODEL = "gpt-5.6-luna"`(直書き)→L259 `require_model("KEY_PHRASE_ADVANCED_EXPLANATION", MODEL)`。SUPPORT_MODELだけ変えるとFamily Xが停止。
- **F5**: gather_topic.py L29、er002_topic_adapter.py L21(`MODEL_SEARCH`)、er006_research_coverage_gate_01.py L17(`GATE_MODEL`)は`require_model`を呼ばず、契約変更後も5.6のまま黙って動く。
- **F2**: er026_family_z_fiction_production_runner_01.py L696 / er018_fiction_story_dna_e_axis_redesign_01.py L425(`load_luna_pricing`が5.6専用)・L445の`!= "gpt-5.6-luna"`は費用集計フィルタ。切替で費用が無言で0円。
- **F1**: 予算ガード/コスト関数の`except StopIteration`(単価未登録を0円扱い=fail-open)。

### 1-4 テストのhardcode
17ファイル(v1の一覧)。**必ず落ちる2件(M6)**: er052_all6_writer_trial_01_test_01.py(L15,28,42-47,54,65-66で5.6前提)、er006_model_routing_contract_01_test.py:24(`approved == "gpt-5.6-luna"`)。他は`routing.<定数>`参照または6-lunaへ更新。

## §2 互換性(Phase 0 probe結果を反映)

Phase 0 probe(2026-10-08、`er052_gpt6_wiring_probe_01.py`、メモリ上で`require_model_or_override`+model定数を差し替え、Production code不変、実費¥10.70/¥30)。**互換のみ確認、品質は未検証**。詳細: `er052_output/gpt6_wiring_probe_01/PROBE_SUMMARY.md`。

| 工程 | 6-luna確認 | 根拠 |
|---|---|---|
| JA Writer R0-R2(previous_response_id) | 確認済み(品質は§0) | ALL-6-LUNA Trial 24/24 |
| JA/EN Fact Check(run_deviation_check) | 確認済み | 同上(本日Trialで実測済みのためprobe不要) |
| EN化(NATURAL_ENGLISH_ADAPTATION) | 確認済み | 同上 |
| Production Checker(OPEN-233経路) | 確認済み | 2026-09-29 Trial等 |
| SHARED_POINT_BLUEPRINT(json_schema strict+reasoning=medium) | 互換OK(PROBED) | probe: model_id=gpt-6-luna、schema適合、effort受付 |
| PROPER_NOUN_EXTRACTION(json_schema、effort未指定) | 互換OK | 同上(応答側effort=medium) |
| STANDARD_A2_ADAPTATION(長文、reasoning=high) | 互換OK | 2205字completed、切れなし、structure PASS(1 call) |
| EVIDENCE_PACK / VFL(json_schema strict+medium) | 互換OK(VERIFICATIONは同パターンのため未実施) | 2 call、3402/4329字completed |
| Research Coverage Gate(GATE_MODEL直書き) | 互換OK | schema適合 |
| B1_SUPPORT(Key Phrase選定、reasoning=high、strategy_l) | 互換OK(A2_SUPPORTは同パターンで未実施) | 4035字completed |
| KEY_PHRASE_ADVANCED_EXPLANATION | 互換OK | 5件schema適合 |
| Topic research(topic_adapter、web_search tool) | 互換OK | web_search_call 5件、10393字completed、費用¥9.07(検索結果token主因)。gather_topic.pyは同一呼び出しパターン |
| Fiction系費用集計(F2) | コード修正要(probe対象外) | Opus F2 |
| Production側Fact Checker/Ledger Deviation v2の5.6箇所 | Grepで直書き5.6は検出なし(`er012_e`/`er019`/`er003_discovery_focus_staged`にgpt-5.6-lunaリテラルなし)、routing/WRITER_MODEL経由 | 委任_02 Grep |

NG工程なし(8/8 OK)。O2はそのまま採用(web_search互換NGで5.6に残す工程なし)。未観測: web_search引用の読み取り品質、A2_SUPPORT/VERIFICATION/gather_topic構造化phase(同パターンの派生)。

## §3 配線計画(Opus推奨構成、Phase 0完了)

### Phase 0(完了): 互換probe
上記。費用¥10.70。

### Phase 1(≈40分): 単価登録+予算ガードfail-closed化(M1)
定数変更より**先**(または同commit)。
1. `er005_output/cost_baseline_01/pricing_snapshot.json`へ gpt-6-luna追記(既存5.6エントリ書式L192-227): input_tokens 0.10 / cached_input_tokens 0.01 / output_tokens 0.50(各`per 1,000,000 tokens`、confidence=PROJECT_INTERNAL_RECORD、note=GPT6-MODEL-COMPARISON-TRIAL-01 DECISION_LOG由来)、cache writes 0.125を別meter(`cache_write_input_tokens`)で1件。
2. F1の4関数を「Production経路で単価が見つからなければ例外」へ(下記修正箇所一覧A)。
3. 静的test新設: PROCESS_MODEL_MAPに現れるOpenAI modelはすべてsnapshotに単価がある。
4. 受入: 新test+既存回帰PASS。この時点で定数は5.6のまま。

### Phase 2(≈60分): 定数7行+直書き修正を一括1 commit(M2/M4/O1/O2)
- routing定数7行を"gpt-6-luna"へ。
- 直書き修正(下記一覧B)、必ず落ちるtest更新(下記一覧C)。
- 受入: 回帰全件PASS、fail-closed維持、Phase 1のtest PASS。

### Phase 3(≈1〜2時間): Production E2E 1本(M3)
Family Xを最初から最後まで1本。受入3点: (1)raw_usage_logのprocess別model_idがすべてgpt-6-luna(定数からの推測は不可)、(2)cost.json>0、(3)予算ガード累計>0。未確認工程の品質は未検証のため、E2Eは互換と費用記録の確認に限る。

### 修正箇所一覧(委任_03で編集。本委任では未編集)

**A. 予算ガード/コスト関数のfail-closed化(F1、M1)**
| ファイル:行 | 現状 | 修正案 |
|---|---|---|
| er012_e_family_entertainment_two_level_runner_01.py L136-137 | `except StopIteration: usd = 0.0` | `except StopIteration: raise RuntimeError(f"[STOP] 単価未登録model: {provider}/{model}")`(Production経路。Trial用途で0円許容が必要なら引数`strict=True`既定) |
| er019_family_x_entertainment_production_runner_01.py L262-263, L268-269 | `except StopIteration: pass` | 同様にraise(web_search単価欠落も例外) |
| er003_v1_n3_01_advanced_adaptation_generate.py L386,392,398 | `except StopIteration: pass`×3 | 同様にraise(未登録modelで`_compute_cost_jpy`が例外) |
| er003_v1_n3_01_standard_a2_generate.py L294,300,306 | 同上×3 | 同上 |
(例diff: `-            except StopIteration:\n-                usd = 0.0\n+            except StopIteration as e:\n+                raise RuntimeError(f"[STOP] pricing missing: {provider}/{model}") from e`)

**B. 直書き・費用集計(M2/M4/O1/O2)**
| ファイル:行 | 修正案 |
|---|---|
| er019_family_x_kp_explanation_01.py L43 | `MODEL = routing.SUPPORT_MODEL`(M4、SUPPORT_MODEL切替と同commit。routing importは既存) |
| er003_v1_en_direct_vfl_01_generate.py L57 / L773 | O1: 既定値を`routing.WRITER_FACT_CHECK_MODEL`へ、`run_deviation_check`内に`model = routing.require_model("WRITER_FACT_CHECK", model)`。`MODEL`は他用途(Writer既定)にも使われるため、変更はdeviation関数の既定値のみに限定(別名定数`DEVIATION_MODEL = routing.WRITER_FACT_CHECK_MODEL`) |
| gather_topic.py L29、er002_topic_adapter.py L21 | O2: `MODEL_SEARCH = routing.QUERY_PLANNER_MODEL`、呼び出し前に`routing.require_model("QUERY_PLANNING", MODEL_SEARCH)`(gather_topic.pyはモジュール直下実行のためimport追加が必要) |
| er006_research_coverage_gate_01.py L17 | O2: `GATE_MODEL = routing.RESEARCH_MODEL`(専用process keyは新設しない。Gate用process新設が必要かはFable判断事項) |
| er026_family_z_fiction_production_runner_01.py L696 | `!= "gpt-5.6-luna"`を`not in routing.APPROVED_COST_MODELS`相当(`{routing.WRITER_MODEL, routing.SUPPORT_MODEL, ...}`)または単価が引けるmodelか、へ。単価読込をrouting由来modelで引く |
| er018_fiction_story_dna_e_axis_redesign_01.py L425, L445 | `load_luna_pricing`を引数`model`受け取りに変更(既定=routing由来)、L445は同フィルタ修正(旧Trial再現用は5.6を明示引数) |

**C. テスト更新(M6)**
- er052_all6_writer_trial_01_test_01.py: L15,28,42-47,54,65-66の`"gpt-5.6-luna"`期待値を`routing.WRITER_MODEL`参照へ(mock引数のdefault値は6-lunaへ)。
- er006_model_routing_contract_01_test.py:24: `approved == "gpt-5.6-luna"`を`approved == routing.<対応定数>`参照へ。
- 他15ファイル(§1-4)は、5.6固定期待値を持つものだけ`routing`参照へ。

## §4 リスクと緩和・切り戻し

- STOP増: EN must-fix 0/19→6/19、EN Advanced STOP 0→2、保留/記事 0.05→0.26。**再評価トリガー(O3)**: Production量産の最初の10本で、EN Advanced deviation STOPが3本以上、または保留が0.3/記事以上になったら、条件D(QCD悪化)として見直す。SSOT記録は委任_03。
- 評価者差: 品質同等は「差不明」であり「改善」ではない。
- 5.6固有prompt依存の網羅調査は未実施。
- **切り戻し手順(M6)**:
  1. 定数+直書き修正のcommit(Phase 2)をrevertする。
  2. 単価の追記とfail-closed化(Phase 1)は**戻さない**(無害であり、戻すと費用0円計上に逆戻りする)。
  3. 常駐processは**再起動**が必要(`run_deviation_check`既定値等がimport時固定、F3)。
  4. 旧Trial script(89ファイル)は書き換えない。本日以降の旧Trial再実行は`require_model_or_override(process, "gpt-5.6-luna", override_reason=...)`で5.6を明示(DECISION_LOGに記録、委任_03)。
  5. 回帰テスト全件実行。
- 並行作業: FACTLOCK Trial生成中のコード変更は条件同一性を損なう。配線順は「6-luna配線commit→E2E→Fact Lock配線(別commit、混ぜない)」。Fact Lock Trialが5.6で動いていた場合、採用前に6-lunaで小規模再確認(Opus論点7)。

## §5 Opus条件Cレビュー論点への回答(完了)

Opus判定「小規模な修正をしてから配線に進む」。採否はOPUS_FINDINGS_LEDGER OF-063〜OF-071(M1〜M6/O1〜O3、すべて採用)。派生キー個別定数化(案a)は不採用(F3により見かけだけの分離)。

## §6 実施タイミング

FACTLOCK-WRITER-REDESIGN-TRIAL-01の生成完了後(メモリ・条件同一性・Git直列化)。Opus条件C実施済み。Production採用判断はユーザー判断7で済み。

## §7 費用・時間見積

- Phase 0 実費¥10.70(予算¥30)。Phase 1 ≈40分¥0、Phase 2 ≈60分¥0(回帰のみ)、Phase 3 ≈1〜2時間(Production E2E 1本の費用は6-luna単価で約¥4〜10/本、Trial実績)。

## 改訂履歴

- v1(2026-10-08 委任_01): 初版(棚卸し、3段階案、Opus論点候補)。
- v2(2026-10-08 委任_02): Opus条件C M1〜M6/O1〜O3反映。Phase構成をOpus推奨(Phase 0 probe→Phase 1 単価+fail-closed→Phase 2 定数+直書き一括→Phase 3 Production E2E 1本)に変更。§2へPhase 0 probe結果(8/8 OK)反映、F1〜F5修正箇所一覧(A=4箇所/B=7箇所/C=test 2件+他)、切り戻し手順(revert範囲・単価は戻さない・process再起動・旧Trial 5.6明示)、受入条件M3、再評価トリガーO3を追記。
