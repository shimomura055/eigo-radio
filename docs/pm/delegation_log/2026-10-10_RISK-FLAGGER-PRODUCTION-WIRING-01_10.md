# RISK-FLAGGER-PRODUCTION-WIRING-01 委任_10 = Phase 2 C4: 正式 annotated B3 producer(D-det v2+決定論assembler)の実装とW-1 interface整合(feature branch)

- 日付: 2026-10-10 / 実行: Sonnet(実行層) / **課金API 0件**(stubのみ) / ユーザー確定 2026-10-10(APPROVED_FOR_PRODUCTION: D-det v2+決定論assembler、追加LLM call 0、¥0/記事)
- 使用モデル(PM_GOVERNANCE 25節): 本作業のLLM呼出0件(producerは決定論)。W-1/RFの予定モデルはC1〜C3固定のまま変更なし。
- 範囲: コードのみ。SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT)・ACTIVE_TASK.md・RESULT_PACKET.mdは未編集(Lane B REJECTED/superseded の記録はmerge時にまとめて)。

## 0. git手順の実績
main(HEAD 84a9ef8f)確認 -> `git checkout feature/factlock-rf-wiring-01` -> `git merge main`(通常merge、競合なし、merge commit 3e67df52)-> 論理単位でcommit(明示add、`-A`/`-f`未使用) -> `git push origin feature/factlock-rf-wiring-01` -> 本ログ commit -> `git checkout main`。mainへはcommitしていない。
他agent由来のuntracked/modified(`er006/er011/er012/er021/er030/er052_output`の既存modified、docs/pm配下のuntracked等)は不触・不add。テスト実行で変化した追跡2件(er005 cost_summary.json / er025 telemetry.jsonl)は`git checkout --`で原状復帰。

## 1. 実装(C4-1〜C4-5。変更ファイル一覧)
| ID | 内容 | ファイル |
|---|---|---|
| C4-1 | 新規 Production module `er053_b3_deterministic_producer_01.py`: Trial3ファイルの66記号(assembler 14 / D-det v2 47 / eval 5)を**ソース逐語**で移植(Trial非import。`B1.`/`RK.`参照は本module内の同名namespaceで解決)。`produce_annotated_b3(out_dir)` が `selected_brief_annotated.md` / `annotation.json`(annotator=DETERMINISTIC、unmapped_claims=[]、annotation_notes=cap超過の周辺化を規則生成) / `annotation_manifest.json`(producer="deterministic_v2"、rules_sha256、input_shas、internal_checks、llm_calls=0) / `writer_constraints.txt` を出力。`fact_selection_evidence.json["selected_fact_brief_text"]` は維持して中身を決定論出力に(元のB3 LLM文は `b3_llm_selected_fact_brief_text` へ退避、冪等) | `er053_b3_deterministic_producer_01.py`(+908行、うち移植部は逐語) |
| C4-2 | 契約module: `ANNOTATORS`に`DETERMINISTIC`追加、`writer_constraints.txt`(manifest.`writer_constraints_sha256`で束縛。DETERMINISTICは必須)、`AnnotatedB3.constraints_text`/`news_field_text`、V10のDETERMINISTIC分岐(判断メモ1)。既存注記検査(Trial `b3_annotation_check_01`)の同等規則は producer内 `run_internal_checks`(5区分)で代替しTrial scriptをimportしない | `er053_b3_annotation_contract_01.py`(+57/-) |
| C4-2' | W-1: R0 Prompt本体は不変、`[ニュース]`欄に渡す文字列を `annotated.news_field_text`(注記済みFacts+制約ブロック、制約が空ならFactsのみ=従来と文字列同一)へ。runtime evidenceに producer規則sha・入力sha・制約sha・ニュース欄sha | `er053_family_x_factlock_ja_writer_01.py`(+11/-) |
| C4-3 | runner: `run_annotation_producer(out_dir)`(storyline_b3 stage 確定直後=if/else の後・`--stop-after`判定の前の**1箇所**。初回/regeneration/resume/再利用の全分岐を通る)。`entry_point.json`にproducer module sha。evidenceは `storyline_b3/audit/annotation_producer_evidence.json` | `er019_family_x_entertainment_production_runner_01.py`(+21) |
| C4-4 | dev adapter: `copy_inputs`(台帳・selected_brief.md・evidenceの複製のみ)。`build_fixture`=copy_inputs+本番producer呼出(testの便宜)。`producer="trial_fixture"` 廃止 | `er053_dev_b3_fixture_adapter_01.py` |
| C4-5 | test | `er053_b3_deterministic_producer_01_test_01.py`(22) / `er053_c4_wiring_test_01.py`(12) / 既存3 test更新 |

## 2. 移植sha表(要約。全66行は `er053_output/risk_flagger_production_wiring_01/c4_port_sha_table.json`)
66/66 byte-identical(関数はソース原文、constant/regexは代入文原文の一致)。`rules_sha256 = 525f2309b5212e68a5891794e7fa6194fb25cbf92f1954727c286796597910d8`(正式値は上記JSONと各manifest)。RULE_VERSION=`deterministic_v2.0`。移植しなかった物: `assemble_Aprime`(A'腕)・`validate_number_ranks`(LLM出力検証)・b3r2_eval_01のM指標群。
個別shaはJSON参照。担保は「Trial側ソースとの完全一致」(`PortFidelityTests::test_every_ported_symbol_is_byte_identical_to_trial_source`)。

## 3. 契約・検査整合の結果
- 9テーマ(Trial実データ)で `validate_annotated_b3` PASS(V1〜V10+V5/V6/V10解釈=OPEN-247)。ROOTFIX-02 eval_v2 の annotated md/sidecar と**完全一致**9/9、ROOTFIX-02 E9 `news_field.txt` と**完全一致**6/6(=Writerが実際に読んだ文字列)、ROOTFIX-01 D-full assembler の Fact行・制約ブロックと**完全一致**9/9。
- 既存Trial注記検査(`b3_annotation_check_01`、**testでのみ実行**)の指摘は9/9で `annotator が A/B/MERGED でない: 'DETERMINISTIC'` のみ(=契約側で許容値追加した点そのもの。他の指摘0)。
- 内部検査5区分(a_alignment/b_numbers/c_core_peripheral/d_tags/e_sidecar): 9テーマとも PASS。欠陥注入(タグ番号飛ばし・印の欠落・本文改変・台帳ID不正・適格外のcore)で各区分が検出。

## 4. 配線経路表(`FourPathOrderTests` で spy 検証。いずれも producer -> contract(T-19/U-1) -> W-1)
| 経路 | コマンド例 | 観測order | 備考 |
|---|---|---|---|
| 初回 | `--stage all` | research -> storyline -> **producer -> contract -> w1(R0,R1,R2)** -> advanced -> rf:b1b -> standard -> rf:a2 | R0 promptの[ニュース]欄に制約ブロックが入る |
| regeneration | `--regenerate-stage storyline_b3` | research -> storyline -> producer -> contract(U-1) -> (JA再利用) -> advanced... | B3選定が変われば注記shaが変わり U-1 PROVENANCE_MISMATCH で STOP(古いJA記事を黙って再利用しない) |
| resume | `--stage writer`(B3まで完了済み) | research -> producer -> contract -> w1 | B3は再実行しない |
| 再利用 | `--stage standard`(JA記事あり) | research -> producer -> contract(U-1) -> standard -> rf:a2 | 決定論なので同入力→同sha→再利用成立 |
| producer失敗 | evidenceのIDが台帳に無い等 | research -> producer(STOP) | 契約・W-1・API・英訳・RFに進まない。古い注記artifactも削除 |

## 5. 判断メモ(Fableへ。新しい意味仕様ではなく、確定仕様の実装上の帰結として処理したもの。異論があれば指示を)
1. **V10のDETERMINISTIC分岐**(契約moduleの解釈追加4): 従来のV10は「注記済みFact本文 == 原 `selected_brief.md` のFact本文」。決定論producerのFactはB3 LLM文ではなく台帳からの再導出なので、DETERMINISTIC時の原本は「台帳+sidecar `facts[].ledger_ids` の順+原Storylineからの決定論再導出(D-full)」。Fact本文・制約ブロックとも再導出と一致を要求(1文字違いでFAIL)。Storylineの完全一致検査は従来どおり原 `selected_brief.md`。
2. **制約ブロックの受け渡し**: 確定仕様の「別欄『制約ブロック』」を `storyline_b3/writer_constraints.txt`+manifest `writer_constraints_sha256` として実装(V2/V3で存在・sha束縛)。W-1はR0 Prompt本体を変えず、`[ニュース]`欄の文字列を Facts+制約ブロック にするだけ(ROOTFIX-02 E9で実際にWriterが読んだ文字列と完全一致)。`parse_brief_md`互換(annotated mdのFacts節は`- 【事実N】本文`行のみ)。
3. **入力検証をTrialより厳格化**: 選択IDの台帳不在・重複・空、evidenceのStorylineとselected_brief.mdのStoryline不一致はSTOP(Trialの`ids = [i for i in ... if i in ledger]`は黙って落としていた)。9テーマでは全て一致(STOPは発火しない)。
4. `spec_sha256` = `rules_sha256`(規則のconstant・関数ソースのsha表からの合成)。sidecar `brief_sha256` は契約V9のため `selected_brief.md` のsha(Trial評価時の「plain D-full briefのsha」とは意味が異なる)。
5. `annotation_notes` = 「cap(N)超過で周辺化: <表記>」(適格だが上限で周辺になった表記のみ)。`unmapped_claims` は常に `[]`。`DUPLICATE`緩和・役割宣言は入れていない。
6. `build_fixture`(adapter)は `copy_inputs`+本番producer呼出の便宜関数。producerのコードはadapterに無い。Production経路はadapterを参照しない(AST test)。
7. `fact_selection_evidence.json` の `selected_fact_brief_text` を決定論出力で上書き(元のB3文は退避)。これを読む既存のTrial script(er037/er039)はProduction外で、実行は本作業の範囲外(必要なら退避キーを参照)。
8. 既存のTrial test `er052_factlock_writer_trial_01_test_01::test_production_files_unchanged_vs_head` はrunner等が未commitの間だけ失敗する(commit後PASS)。
9. **新しい仕様候補**: なし(実装中に新しい意味仕様が必要になった箇所はない=STOP非該当)。

## 6. 検証
`er053_output/risk_flagger_production_wiring_01/`: `c4_test_results_01.md`(回帰set 686 passed / 14 skipped / 0 failed、全suite 37 failed=C3分類済み36+未commit起因1[commit後PASS]・新規0)/ `stub_e2e_c4_01/summary_{meta,central_bank_mortgage}.json`(`run_stub_e2e_c4_01.py`)/ `c4_port_sha_table.json` / `dangling_after_c4.json` / `c4_gate3_static_01.md` / `c4_dev_confirm_run_plan_01.md`(C4-7、未実行)/ `c4_candidate_features.json` / `c4_full_suite_log.txt`。

## 7. 禁止事項の遵守
Agent起動なし。課金API 0件。mainへのcommitなし・rollback tag未付与。SSOT・Prompt・schema未変更(Writer R0 Prompt本体・B3 Prompt/schema不変)。
