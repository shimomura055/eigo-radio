# 完了条件・STOP条件 照合表(RISK-FLAGGER-PRODUCTION-WIRING-01 委任_16、2026-10-11)

作成: Sonnet実行層(ドキュメント作業のみ、API 0件、コード変更なし)。**本表は事実の照合であり、`PRODUCTION_WIRED`判定ではない(判定はFable/ユーザー)。**
条件・STOP条件の逐語出典: `DECISION_LOG.md` 2026-10-10エントリ「ユーザー原文の逐語記録: Production Wiring完了条件・STOP条件」(commit `3b3368b8`)。
**件数の注意**: 委任文は「18点」だが、逐語原文の箇条書きは**19項目**(「retry / regeneration / fallback / reused article経路と整合」を1項目として数えた場合)。本表は逐語どおり19行で照合する。

凡例(充足状況): 充足 / 一部 / 未充足 / Fable判定待ち。
「発火区分」: **R**=正式Production経路(最終L3 `er019_output/coffee_prices/run_l3_01/`、main上、`--stage all`)でruntime発火した / **T**=unit/integration/stub testのみ(正式経路ではruntime未発火) / **D**=開発用確認run(`semiconductor_earnings`、W-1下流)。

## A. 完了条件(逐語)

| # | 条件(逐語) | 充足状況 | 発火区分 | 根拠(path / commit) | 備考 |
|---|---|---|---|---|---|
| 1 | Production正式初回経路へ実装済み | 充足 | R | `er019_family_x_entertainment_production_runner_01.py` main(storyline_b3直後 `run_annotation_producer`、W-1、Adv→RF→Std→RF)。L3は `er019_output/coffee_prices/run_l3_01/entry_point.json`(`args.stage=all`、runner_sha256 `6aa5b362…`)、`raw_usage_log.jsonl` 17行のstage順=research→ledger→storyline_b3→w1_r0→w1_astra_r1→w1_astra_r2→advanced→risk_flag(b1b×4)→standard→risk_flag(a2×4)。merge `3a80b77c` | audio runnerも正式経路でscaffold→rf_guard→tts→assemble→player発火(委任_14、`audio_stdout*.log`、`scaffold_run_summary.json`) |
| 2 | retry / regeneration / fallback / reused article経路と整合 | 一部(staticとtestは充足、runtimeは一部のみ) | T(retry/regeneration/resume/fallback)、R(reused・tts単独) | static: `c4_gate3_static_01.md` §B(retry/regeneration/resume/fallback/reused 各「充足」)、`FourPathOrderTests`(`er053_b3_deterministic_producer_01_test_01.py`/`er053_c4_wiring_test_01.py`)、U-1 test(`er019_family_x_entertainment_production_runner_01_test_01.py`、`LegacyWriterProvenanceStop` assert)。runtime発火: reused=`--stage standard`でR2をU-1再利用してStandard再生成(`l3_run_01/stdregen_stdout.log`、委任_14 §3(a))、audio `--stage tts`単独(`ttsonly_stdout.log`、`rf_tts_guard.json` match=true/action=verified) | `--regenerate-stage storyline_b3`、resume(`--stage writer`)、記号QA再実行、技術retry(段落3分割)の**正式経路runtime発火は未観測**(testのみ)。audio側ASR自動retryはR(委任_14 §2)。Open Item候補: OPEN-249(regenerate後の下流自動再生成要否)、OPEN-250(audio旧記事TTS再生成のU-1相当、現状は安全側)=いずれもFable/ユーザー判断 |
| 3 | DEV / Trial専用path依存なし | 充足 | R(正式経路がDEV/Trial非依存で完走)+T(静的検査) | `c4_gate3_static_01.md` S1・S9・§B「DEV・Trial専用path依存なし」(AST test: runner/契約/W-1/producerが `er053_dev_b3_fixture_adapter_01`・`er050/51/52*`・`b3_annotation_check_01`・Lane B moduleをimportしない)。L3は正式runnerのみで完走 | DEV adapterは `copy_inputs` のみ・Productionから参照されない |
| 4 | B3 producerが決定論方式になっているruntime evidence | 充足 | R | `er019_output/coffee_prices/run_l3_01/ja_writer/runtime_evidence.json`: `annotation_manifest_producer="deterministic_v2"`、`annotation_rules_sha256=525f2309…`、`annotation_rule_version="deterministic_v2.0"`、`annotation_input_shas`。`entry_point.json` `annotation_producer_module_sha256=8899d0fa…`。`cost.json` に producer用stageなし(LLM 0 call、by_stageはstoryline_b3→w1_r0へ直結)。Queue `queue.json` `producer="deterministic_v2"` | |
| 5 | W-1 R0/R1/R2 runtime evidence | 充足 | R | `ja_writer/runtime_evidence.json`: R0 `gpt-6-luna`(`model_mismatch=false`)、R1/R2 `gpt-6-astra`(effort high、`previous_response_id_used=false`、`developer_message=null`、`model_mismatch=false`)、`ja_writer/factlock/{r0,r0_with_tags,r1.raw,r2.raw}.md`+response.json。`cost.json` by_stage: w1_r0 ¥0.543 / w1_astra_r1 ¥18.162 / w1_astra_r2 ¥19.664 | 記号QA: `symbol_qa.r0.regenerated=false`、`symbol_qa.r2.rerun=false`(再実行経路はT止まり)。R2入力=R1 raw(コード `run_w1_writer`、test) |
| 6 | Advanced / Standard両RF runtime evidence | 充足 | R | `entry_point.json` `risk_flagger.b1b`/`a2`: 各 `status=OK`、4条件OK。`review_queue/post_en/coffee_prices__run_l3_01/{b1b__rf20261010T125626Z-f4c2,a2__rf20261010T125728Z-ea2b}/queue.json` の `conditions[]`: luna A3/A4=`gpt-6-luna`、gemini35fl A3/A4=`gemini-3.5-flash-lite`(`model_id_returned` 一致)、`system_prompt_sha256` A3=`9d995042…`/A4=`c87b95e5…`。b1b 4 issue、a2 5 issue。runner順序: Advanced直後にb1b RF、Standard直後にa2 RF(raw_usage_logのstage順) | RF_UNAVAILABLE/PARTIAL/BudgetCheckStopの正式経路発火は未観測(stub E2E S5/S6のみ=T) |
| 7 | Review Queue保存確認 | 充足 | R | `review_queue/post_en/index.jsonl`(L3分 b1b/a2 各1行、`queue_path`・`issue_count`・`run_label=L3_PRODUCTION_E2E_01`)、`review_queue/post_en/coffee_prices__run_l3_01/…/{queue.json,queue.md,inputs/,raw/}`。`git ls-files review_queue` に42ファイル(追跡対象)、origin/main `b2eeff82` に含まれる(GitHubから参照可) | `review_state`なし(設計どおり)。Queue commit/push責務はOPEN-245(未解決)。追加: `coffee_prices__run_l3_01_stdregen`(Std再生成の追加証跡) |
| 8 | TTS / Technical QA runtime確認 | 充足(確認中事項あり) | R | 委任ログ `docs/pm/delegation_log/2026-10-10_RISK-FLAGGER-PRODUCTION-WIRING-01_14.md` §2: a2 21 seg/b1b 25 seg全 `status=OK`、asr_verified全True、clipping 0、KP source gate PASS(両level)、disfluency flagged 0、repetition flagged 0、ASR初回不一致の自動retry(attempt2で解決)を観測。証跡: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_l3_01/{a2,b1b}/audit/{tts_generation_results,timeline}.json`、`run_summary_tts.json`、`scaffold_run_summary.json`、`audit/rf_tts_guard.json`。完成音声: a2 320.96s / b1b 303.0s(wavはgitignore、所在のみ) | **委任_15で確認中**: (a) coffee a2の `a2_derived_from_advanced_sha_mismatch` 警告(recorded `2c627b38…` vs current b1b `5e8979df…`、観測のみ・STOPに使わない設計)、(b) `tts_generation_results.json` の `retry_count=0` 表示とASR自動retry発生の関係。いずれも結論は本表では書かない |
| 9 | actual model_id / routing evidence | 充足(LLM段のみ。音声・TTS側のmodel_id個別列挙は未確認) | R | W-1: `runtime_evidence.json` の `requested_model`/`model`/`model_mismatch=false`(R0 gpt-6-luna、R1/R2 gpt-6-astra)。RF: `queue.json` `conditions[].model_id_requested/model_id_returned`(4条件×2 Level)。routing: `er006_model_routing_contract_01.py` `PROCESS_MODEL_MAP` の `FAMILY_X_FACTLOCK_R0/REVISE`、`FAMILY_X_RF_LUNA/GEMINI`(リテラル固定、`require_model`でAPI前確認)。audio: KP選定(er030 db_hybrid)・Gemini TTS・ASR のmodel_idは `scaffold_run_summary.json`/`run_summary_tts.json` に記録(本委任では値の逐一照合は未実施) | `raw_usage_log.jsonl` の `model` 欄はNone(stage tag・providerのみ)。model_id証跡の正本はruntime_evidence/queue.json |
| 10 | regression / integration test PASS | Fable判定待ち | T | merge後の全suite(`er053_output/risk_flagger_production_wiring_01/l3_run_01/merge_full_suite_log.txt`): `36 failed, 5833 passed, 14 skipped`。36件はC3/C4で分類済みの既存32+順序依存4と同一集合(新規failure 0、`c3_test_results_01.md`/`c4_test_results_01.md`)。OPEN-251の追加test 4件+関連24 passed(委任_14 §1)。C4時点の回帰set 686 passed / 0 failed | 「PASS」を文字どおり全suite 0 failedとするか、既存失敗の同一集合照合で足りるかはFable判断(STOP条件4「重大failure」の判定も同じ) |
| 11 | Dangling Reference Check = 0 | 充足 | R(main上でscan) | `er053_output/risk_flagger_production_wiring_01/l3_run_01/dangling_on_main.json`: `after_c4_fact_checker_symbols_total=0`、`unclassified_truly_orphaned=0`、残36語=技術QA語彙11+レビューラベル25(分類済み)。`dangling_after_c4.json` と同結果(DECISION_LOG 委任_13「Dangling Check on main=Fact Checker専用シンボル孤立0」) | `dangling_on_main.json` の項目名は `after_c4_*` のまま(スクリプト流用)。main merge `3a80b77c` 後の再走査という位置づけ |
| 12 | CURRENT_SPEC更新 | 充足 | — | 本委任_16で実施: 新節「Family X Production経路 — W-1 Fact Lock Writer + Risk Flagger + Review Queue」追加+旧記述4か所に「撤去済み(2026-10-10)」注記+冒頭更新行。commit hashは委任ログ_16/報告に記載 | Status欄は「配線済み(最終Gate判定待ち)」(`PRODUCTION_WIRED`とは書いていない) |
| 13 | DECISION_LOG更新 | 一部 | — | 2026-10-10エントリ群あり(ROOTFIX最終仕様+Lane A C4、完了条件・STOP条件の逐語記録、Opus条件Cレビュー・merge・ユーザー決定[委任_12/_13])。OPEN-251修正は commit `8ba79fdc`(SSOT記録を含む) | 委任_14(OPEN-251修正+L3 audio完了)・委任_15(META再生成)・委任_16(CURRENT_SPEC更新)分のDECISION_LOG追記は**委任_15 agentが担当中**(本委任はDECISION_LOGを編集しない)。完了後に再照合が必要 |
| 14 | OPEN_ITEMS close/update | 一部 | — | OPEN-244(親)は進捗更新済み(本委任_16で「L3 coffee完了、CURRENT_SPEC更新済み、META再生成中」を追記)、**closeしていない**(close判断はFable)。OPEN-247 CLOSED、OPEN-251 CLOSED。OPEN-245/246/248/249/250は[OPEN]等のまま | 未解決のOpen Item: OPEN-245(Queue push責務)、OPEN-246(Astra請求照合)、OPEN-249/250(安全側の判断待ち)。OPEN-244をcloseするか残すかはFable/ユーザー判断 |
| 15 | Lane BをREJECTED/supersededでclose | 充足 | — | `DECISION_LOG.md` 2026-10-10「ユーザー最終決定(ROOTFIX最終仕様)+Lane A C4完了」の(3): Lane B(B3-ANNOTATION-AUTOMATION-TRIAL-01)=REJECTED・superseded by D-det v2+deterministic assembler、クローズ。`OPEN_ITEMS.md` OPEN-244行(委任_11進捗)・OPEN-247 | Sonnet注記方式はProduction不採用(約¥15.7/記事を回避) |
| 16 | rollback tag作成 | 充足 | — | tag `rollback/pre-factlock-rf-wiring-01-20261010` = `35406ebcb82946aea37a07c5f9f65083ee21b4be`(main merge直前)。`git ls-remote --tags origin` で存在確認済み(origin push済み) | rollbackは `git revert -m 1 3a80b77c` |
| 17 | feature branch → main --no-ff merge | 充足 | — | `feature/factlock-rf-wiring-01` → main `3a80b77cd38cf639c28d5841e81afc6d13368643`(`--no-ff`、競合なし、委任_13、DECISION_LOG「merge」項) | 案Y(ブランチ分離+merge時にtag)で運用。ブランチはorigin/ローカルとも残存 |
| 18 | push確認 | 充足 | — | `git merge-base --is-ancestor 3a80b77c origin/main` = true、origin/main先頭 `b2eeff82`(2026-10-11確認時点) | 以降の委任_15/_16のcommit/pushは別途 |
| 19 | ユーザー承認内容とProduction挙動が一致 | Fable判定待ち(差異候補あり) | R/T混在 | 下記 B. 対応表 | 軽微な差異候補を明示(§B末尾)。新仕様候補は実装せず報告のみ |

集計(本表の判定、19項目中):

- 充足: #1, #3, #4, #5, #6, #7, #8, #9, #11, #12, #15, #16, #17, #18 = **14**
- 一部: #2, #13, #14 = **3**
- 未充足: **0**
- Fable判定待ち: #10, #19 = **2**
- 合計 19

(#8は委任_15で確認中の2事項あり、#9はLLM段のみ確認のため、Fableが条件を厳格に解する場合は「一部」へ寄せる余地がある。)

## B. 「ユーザー承認内容」と「Production実挙動」の対応表(条件19の根拠)

| 承認内容(出典) | 実挙動(根拠) | 一致 | 発火区分 / 備考 |
|---|---|---|---|
| W-1: 注記版B3 → R0 Luna(`gpt-6-luna`)→ R1 Astra → R2 Astra(OPEN-244行・委任_01/04) | `run_w1_writer`: R0=gpt-6-luna effort high+developer message、R1/R2=gpt-6-astra effort high・developer none・previous_response_idなし、R2入力=R1 raw。runtime_evidenceで実測 | 一致 | R。R0のeffortはコード `R0_EFFORT="high"`(承認文に明示値なし=未確認、W-1 Trial移植のため一致と推定。変更はUSER_DECISION_REQUIRED) |
| 記号QA案A(S3-1、案A既定) | R0: 1回再生成→残ればSTOP。R2: R2のみ同一R1 rawで1回再実行→残ればSTOP | 一致 | T(L3では `rerun=false`) |
| D-det v2+決定論assembler(`APPROVED_FOR_PRODUCTION`、追加LLM 0、¥0/記事) | `er053_b3_deterministic_producer_01.py`: 66記号をTrial逐語移植(byte-identical 66/66、`c4_port_sha_table.json`)、`llm_calls=0`、`rules_sha256=525f2309…`。L3で `annotation_manifest_producer=deterministic_v2`、cost.jsonにproducer費用なし | 一致 | R |
| RF 4条件(Luna A3/A4・`gemini-3.5-flash-lite` A3/A4)両Level、OR+dedupe、非Blocking、自動Rewrite/retry/削除なし、Gemini A4 0件でも停止しない | `er053_risk_flagger_production_01.py`: 4条件逐次・`merge_issues`・BudgetCheckStop/ArticleModifiedErrorのみ伝播・他は `RF_UNAVAILABLE`。L3でgemini A3/A4が b1b 0件でも続行 | 一致 | R(OK経路)/T(RF_UNAVAILABLE・PARTIAL)。LunaのReasoning effortは `medium`(承認文に明示値なし=未確認、Trialの値の移植) |
| RF位置: Advanced英訳→Advanced RF→Standard Level調整(入力=Advanced英文)→Standard RF(DESIGN_03) | runner: `advanced` → `run_post_en_risk_flag(b1b)` → `standard` → `run_post_en_risk_flag(a2)`。raw_usage_logのstage順で実測 | 一致 | R。Standardの入力がAdvanced英文であることはコード根拠(委任_04 §4、`er012_e` L615/L617)で、runtime個別確認は未実施 |
| M1(a) Advanced限定・無条件ON(ユーザー確定、意図的Level非対称) | `_advanced_in_one_line`: 環境変数条件なし、Standardは呼ばない。L3のadvanced stageで2 call記録(本文+In one line相当と推定) | 一致 | R(advanced stage発火)。M1(a)の個別call識別(どちらがIn one lineか)は**未確認**。b1b `article.md` に `## In one line` あり |
| Review Queue: GitHub参照可能なリポジトリ内保存、`review_queue/post_en/`、runnerにgit責務なし、`review_state`なし | `er053_review_queue_01.py`: `review_queue/post_en/<slug>__<run>/<level>__<rf_run_id>/…`+`index.jsonl`。追跡対象・origin/mainに存在。runnerはgit不使用 | 一致 | R。push運用責務=OPEN-245(未解決のまま、承認内容どおり) |
| 旧Fact Checker撤去(両Level、R2後JA含む、OPEN-233系は未配線のままSUPERSEDED)、技術QA維持 | C2: R-01〜R-28実施(委任_08)、Fact Checker専用シンボル0(`dangling_on_main.json`)、技術QA語彙は維持(11語分類)。共有 `vfl01.run_deviation_check` は旧Family A/B/C用に残置(Family X参照0) | 一致 | T(AST+spy test)+R(L3で旧Checker起動なし=stage順に該当stageなし) |
| U-1: 旧Writer記事の再利用はSTOP | `LegacyWriterProvenanceStop`(`chain_method=="W-1"`+annotated sha一致のみ再利用) | 一致 | T(正式経路でのSTOP発火は未観測。再利用成立側のみR) |
| U-2: 単体CLI `--ja-article` 等封鎖 | `guard_standalone_cli`(`er012_e`)。subprocess testでSTOP確認 | 一致 | T |
| 案Y(ブランチ分離運用、条件付き同意: 独立部分先行・凍結・`git merge main`取込・merge直前tag・`--no-ff`・rollback=`git revert -m 1`) | feature branch運用、C3/C4で `git merge main`(通常merge)、tag `rollback/pre-factlock-rf-wiring-01-20261010`(main 35406ebc)、`3a80b77c` `--no-ff` | 一致 | 条件(f)「開発用確認runの証跡はブランチsha付き」は委任_12で実施(ブランチshaの記載有無はこの表では個別未確認) |
| 費用: L3上限¥350、L3+META合計¥600 | L3累計¥110.43(Research〜Queue 89.05+audio 15.80+Std再生成1.49+tts単独4.09)。残(合計600に対し)¥489.57。META分は進行中 | 一致(L3) | META費用は委任_15で確認中 |

差異・留意(承認内容と実挙動の食い違いというより、判断を要する候補):
1. **条件数**: 委任文18点に対し逐語19項目(上記)。
2. **a2派生元Advanced sha不一致の警告**(`a2_derived_from_advanced_sha_mismatch`): 設計(S3-2)は「観測のみ・STOPに使わない」で一致しているが、coffee L3で実際に出た原因は**委任_15で確認中**。
3. **`retry_count=0`表示**: ASR自動retryが観測されている一方でrecordは0。意味づけは**委任_15で確認中**。
4. **META再生成結果**: 委任_15で確認中。
5. 新仕様候補(実装せず報告のみ): OPEN-249(regenerate後の下流自動再生成)、OPEN-250(audio側U-1相当)、`unlocated_flags` 部分採用(未実装)、audio側scaffold後記事変更時のRF重複費用(委任_09 解釈メモ3)。

## C. STOP条件(逐語)

| # | STOP条件(逐語) | 該当 | 根拠 |
|---|---|---|---|
| 1 | D-det v2 / assemblerを実装すると既承認W-1仕様と矛盾する | 該当なし | W-1 Prompt本体不変(`verbatim_shas`固定test)、変えたのは[ニュース]欄に渡す文字列(Facts+制約ブロック)のみ。Trial3ファイル66記号を byte-identical 移植(`c4_port_sha_table.json`)。ROOTFIX-02 E9 `news_field.txt` と完全一致6/6(委任_10 §3) |
| 2 | retry / regeneration / reused経路で仕様不整合が解消不能 | 該当なし(Fable確認推奨) | `FourPathOrderTests`で初回/regeneration/resume/再利用/producer失敗の5経路を整合確認(委任_10 §4)。残る論点OPEN-249/250は現状「安全側」(自動再生成しない・STOPする)で不整合ではなく判断待ち |
| 3 | Production正式pathでruntime発火できない | 該当なし(**履歴: 一時該当・解消済み**) | 委任_13でaudio stageが `UnknownModelPricingError: gpt-6-luna`(OPEN-251)でSTOP→Fable承認の最小修正 `8ba79fdc`→委任_14でaudio全stage(scaffold/rf_guard/tts/assemble/player)がmain上で発火・EXIT=0 |
| 4 | regression / integration testで重大failure | 該当なし(Fable確認推奨) | 全suite 36 failed / 5833 passed は既存集合(C3/C4分類済み32+順序依存4)と同一、新規failure 0(`merge_full_suite_log.txt`)。「既存36件を重大とみなすか」はFable判断(条件10と同じ論点) |
| 5 | Dangling Referenceが残る | 該当なし | `dangling_on_main.json`: Fact Checker専用シンボル0、孤立0(技術QA語彙11+ラベル25は分類済み) |
| 6 | 新しい仕様判断が必要 | 該当候補あり(Fable判断待ち) | OPEN-249/250、a2派生元sha警告の扱い(委任_14「要Fable確認」、委任_15確認中)、`retry_count=0`表示。いずれも現状の挙動は安全側/観測のみで、本委任では実装・決定していない |
| 7 | 累計費用が承認Capを超える見込み | 該当なし(META分は確認中) | L3累計¥110.43 / 上限¥350。L3+META合計上限¥600に対し残¥489.57(委任_14 §4)。META再生成の費用は委任_15で確定 |
