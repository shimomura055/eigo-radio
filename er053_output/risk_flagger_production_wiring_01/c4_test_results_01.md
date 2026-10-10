# C4 test results (RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C4, 2026-10-10, API 0 / cost JPY 0)

Branch `feature/factlock-rf-wiring-01`(commit 1758f54f / f3379630 の後)。コマンド: `PYTHONUTF8=1 .venv/Scripts/python.exe -X utf8 -m pytest <files> -q -p no:cacheprovider`
(`PYTHONUTF8=1` が必要なのは既存の subprocess系2test[er012_e U-2 CLI block / TtsModeCli]が子プロセスのstderrを日本語で読むため。C4と無関係。)

## 1. C4新規・更新test
| ファイル | 件数 | 内容 |
|---|---|---|
| er053_b3_deterministic_producer_01_test_01.py | 22 | 9テーマgolden(ROOTFIX-02 eval_v2のannotated md/sidecarと完全一致、ROOTFIX-01 D-full assemblerのFact行・制約ブロックと完全一致、E9 news_fieldと完全一致6テーマ)/契約PASS/既存Trial注記検査の指摘がannotator値のみ/冪等/移植66記号のbyte-identical/Trial・Lane B・checker非import(AST)/失敗系(入力欠落・未知ID・重複ID・Storyline不一致→課金前STOP、失敗時に古い注記artifactを残さない)/内部検査5区分の欠陥検出 |
| er053_c4_wiring_test_01.py | 12 | 4経路(初回/regeneration/resume/再利用)の `producer -> contract -> W-1` 順序spy・regenerationでB3選定が変わった場合のU-1 STOP・producer失敗で契約/W-1/API/英訳/RFへ進まない・注記なしfallback不在のAST(producer呼出が1箇所・writerより前、CLI/env switch無し、`run_annotation_producer`に分岐/try無し、`trial_fixture`/adapter参照無し) |
| er053_b3_annotation_contract_01_test_01.py | 33(更新) | `DETERMINISTIC` annotator許容・writer_constraints束縛(V2/V3)・V10再導出(B3 LLM文ではなく決定論再導出が原本)・既存V1〜V10負例は全て従来どおり・adapterをcopy_inputs方式へ |
| er053_family_x_factlock_ja_writer_01_test_01.py | 35(更新) | R0 [ニュース]欄=注記済みFacts+制約ブロック、R0 Prompt本体は不変(pinned sha維持)、evidenceにproducer規則sha・入力sha |
| er053_c2_wiring_test_01.py | 15(更新) | mainのevent順に `annotation` を追加(storyline_b3直後・writerの前)、注記なし→AnnotationProducerError |

## 2. 回帰set(C3と同一の35ファイル)
`er053_*_test_01.py / er019_family_x_*test* / er019_writer_run_summary_reconstruction_01_test_01 / er012_e_family_entertainment_two_level_runner_test_01 /
er052_factlock_{sweep,writer_trial}_01_test_01 / er052_open243_m123_trial_test_01 / er052_factlock_astra_e2e_runner_01_test / er006_model_routing*test*`
結果: **686 passed, 14 skipped, 0 failed**(C3 baseline 644 passed / 14 skipped。+42 = C4 test追加)。skipped 14 = C2/C3と同一のlegacy Trial test。
(`er052_factlock_writer_trial_01_test_01::test_production_files_unchanged_vs_head` は「ProductionファイルがHEADから無変更」を見るため、runner変更が未commitの間は失敗する。commit後に PASS。)

## 3. 全suite(er*test*.py 253ファイル、er015_standard_a2_6000... を除く。runner変更が未commitの時点で実行)
結果: 37 failed, 5822 passed, 14 skipped, 362 subtests passed(11m21s)。詳細一覧 = `c4_full_suite_log.txt`。
37 failed の内訳 = C3で分類済みの36件(既存32+順序依存4)と**同一** + 上記 `test_production_files_unchanged_vs_head` 1件(commit後にPASS、§2の再実行に含まれ PASS)。**C4起因の新規failure 0**。
C3 baseline: 36 failed / 5781 passed → C4: 36(commit後) / 5822 passed(+41)。
テスト実行で変化した追跡ファイル2件(er005 cost_summary.json / er025 telemetry.jsonl)は `git checkout --` で原状復帰(C3と同じ扱い)。

## 4. stub E2E(`run_stub_e2e_c4_01.py`、実コード: main/producer/契約/W-1/RF module/Review Queue/audio runner main。stub: client/EN/RF call/TTS生成)
`stub_e2e_c4_01/summary_meta.json`, `summary_central_bank_mortgage.json`(2テーマ):
- producer evidence: event順 `research_ledger -> annotation_producer(real) -> contract.validate_annotated_b3 -> W-1 R0 -> R1 -> R2`、manifest.producer=`deterministic_v2`、annotator=`DETERMINISTIC`、llm_calls=0、内部検査5区分PASS、W-1 evidenceのproducer/規則sha/制約sha/ニュース欄shaが実ファイルと一致
- S0 Writer main -> Advanced RF -> Standard RF -> Queue保存(2 Level) / S1 scaffold -> tts: 三者sha一致でRF再実行なし / S2 Queueなし: audio側でRF実行(Level別) / S3 再実行は一致 / S4 a2のみ変更: a2のみRF / S5 RF全滅でもTTSへ / S6 予算超過でRF STOP(BudgetCheckStop伝播)
- 旧Checker呼出 0(`old_checker_called=false`)、課金API 0。

## 5. 移植sha表: `c4_port_sha_table.json`(66記号: assembler 14 / D-det v2 47 / eval 5、**66/66 byte-identical**、rules_sha256=525f2309b521...)
## 6. Dangling after C4: `dangling_after_c4.json`(Fact Checker専用シンボル 0、残存語36=技術QA語彙11+Opus所見ラベル25=C3と同一、孤立0、producer module をscopeに追加して走査)
