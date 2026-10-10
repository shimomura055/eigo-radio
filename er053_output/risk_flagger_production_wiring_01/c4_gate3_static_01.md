# C4 Gate 3 Static 再確認 充足表(RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C4、2026-10-10)

対象: DESIGN_03 12-4 Static(S1〜S10)+ユーザー完了条件のStatic項目。証跡はすべて `c4_test_results_01.md` 他の同ディレクトリ・test file。
判定は「Static(コード・test・stub)の充足」であり、Runtime(開発用確認run・最終L3)・`PRODUCTION_WIRED` 判定ではない。

## A. DESIGN_03 12-4 S1〜S10(C4で producer/契約/配線が加わった後の再確認)
| # | 項目 | 結果 | 根拠 |
|---|---|---|---|
| S1 | Production moduleが er050/er051/er052* をimportしない(DEV adapterはProductionから参照されない) | 充足 | producer module のimport集合はAST testで固定(`PortFidelityTests::test_producer_does_not_import_trial_or_lane_b_or_checker`)。runner/契約/W-1/producerに adapter・Trial参照なし(`NoFallbackAstTests::test_no_trial_fixture_or_plain_b3_literal_in_production_modules`、既存W-1 testのadapter非参照test) |
| S2 | 旧Checker呼出0(AST+grep) | 充足 | C2 test維持(`er053_c2_old_checker_removal_test_01`含む)、stub E2E `old_checker_called=false`、dangling_after_c4 のFact Checker専用シンボル0 |
| S3 | 各経路で旧Checker不到達(spy) | 充足 | `er053_c2_wiring_test_01`(15 PASS)・`er053_c4_wiring_test_01` の全経路で `run_deviation_check` が呼ばれればAssertionError(spy) |
| S4 | A3/A4 prompt shaとW-1 Prompt定数shaが契約表一致 | 充足 | W-1 R0 Prompt本体は不変(`verbatim_shas` pinned test PASS)。C4で変えたのは[ニュース]欄に渡す文字列(Facts+制約ブロック)のみ |
| S5 | model固定(routing 4キー・env上書きなし・fail-closed・pricing登録) | 充足(無変更) | C4はmodel/routing/pricingを変更していない。producerはLLM 0(`llm_calls=0`、`model_ids=[]`) |
| S6 | RF非Blocking | 充足(無変更) | C2/C3 test PASS(`rf_status RF_UNAVAILABLE/PARTIAL` でも次工程へ) |
| S7 | splitter golden+他経路diff 0 | 充足(無変更) | 回帰set 686 PASS(splitter test含む) |
| S8 | Dangling Reference 0 or SUPERSEDED | 充足 | `dangling_after_c4.json`: Fact Checker専用シンボル 0、残存36語=技術QA語彙11+レビューラベル25(分類済み)、孤立0 |
| S9 | 隠れswitch0(注記なしB3フォールバック含む) | 充足 | `NoFallbackAstTests`: argparseオプション集合固定(注記関連switchなし)、`os.environ`/`getenv`なし(runner・producer)、producer呼出は storyline_b3 確定直後の1箇所のみで `run_annotation_producer` に if/try/IfExpなし、producer失敗でW-1/契約/英訳/RFへ進まない(`test_producer_failure_stops_before_contract_w1_and_api`)、W-1入口は `validate_annotated_b3` のみ(既存T-13) |
| S10 | Standard/Advanced対称test(意図的差=M1(a)のみAdvanced) | 充足(無変更) | C2/C3 testの対称test PASS |

## B. ユーザー完了条件 Static項目
| 項目 | 結果 | 根拠 |
|---|---|---|
| Production正式初回経路へ実装済み | 充足 | `er019_family_x_entertainment_production_runner_01.py` main の storyline_b3 確定直後に `run_annotation_producer`(初回: `FourPathOrderTests::test_path1_initial_run_producer_then_contract_then_w1`、stub E2E S0 でmain実駆動) |
| retry整合 | 充足 | producerは決定論・冪等でAPIなし=retry対象外。W-1のR0記号QA再生成1回/R2記号QA再実行1回の上限は無変更(W-1 test PASS)。再生成時もR0 Prompt(news field)は同一(R0 symbol regen promptは `news_text` を共有、test_r0_symbol_qa_regenerates_once...) |
| regeneration整合 | 充足 | `--regenerate-stage storyline_b3`: B3再生成→producer→契約→(注記sha一致ならJA再利用/不一致ならU-1 STOP)(path2/path2b test)。producer失敗時は古い注記artifactを削除(`test_failure_removes_stale_annotation_artifacts`)。`--regenerate-stage writer/advanced/standard` も stage=all 経由で storyline_b3 分岐を通りproducerが先行 |
| resume整合 | 充足 | `--stage writer`(B3まで完了済み・注記なし)→producerが先行(path3) |
| fallback整合 | 充足(fallback不在) | 注記なしB3へのfallback・runtime switch・CLI・環境変数なし(S9)。producer失敗=課金前STOP(`AnnotationProducerError`、`[STOP] ANNOTATION_PRODUCER_FAILED`) |
| reused整合 | 充足 | 既存B3/既存JA記事の再利用分岐でも producer→契約(U-1来歴確認)の順(path4)。決定論なので同入力→同`annotated_md_sha256`(冪等test)→ U-1 provenance 一致 |
| DEV・Trial専用path依存なし | 充足 | Production経路(runner/producer/契約/W-1)は `er053_dev_b3_fixture_adapter_01`・`er052*`・`b3_annotation_check_01`・Lane B moduleをimport/参照しない(AST test)。adapterは copy_inputs のみ(注記artifact非生成)で Production から参照されない(既存W-1 test) |
| regression PASS | 充足 | 回帰set 686 passed / 0 failed。全suite 37 failed のうち36はC3分類済み既存(新規0)+1は未commit起因でcommit後PASS |
| Dangling 0 | 充足 | S8(Fact Checker専用シンボル 0、孤立0)。producer経路にTrial module参照 0 |
| Production化条件の実装範囲 | 充足 | D-det v2+決定論assemblerをTrialから逐語移植(66記号byte-identical)。B3 Prompt/schema不変、追加LLM call 0、¥0/記事 |

## C. 未充足・Static外(明示)
- **Runtime**: 開発用確認run(`c4_dev_confirm_run_plan_01.md`、未実行)・最終L3(G-C)は未実施。
- `PRODUCTION_WIRED` 判定・Status更新・Lane B(Sonnet注記)REJECTED/superseded のSSOT記録は merge 時にまとめて(本委任はコードのみ)。
- OPEN-247(V5/V6/V10解釈)・OPEN-246(Astra請求照合)は未解消のまま。
- 軽微仕様の処理結果は RESULT_PACKET_LANEA_C4.md の「判断メモ」を参照。
