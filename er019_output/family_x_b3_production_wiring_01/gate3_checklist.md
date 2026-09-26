# Gate 3 Checklist — NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01

Sonnetによる証跡整理のみ(PRODUCTION_WIRED判定はFable/ユーザー)。
runtime evidence run: `er019_output/family_x_b3_production_wiring_01/run_01/`
(theme: Meta「Muse human concierge」、entry point: `entry_point.json`)。

| # | 項目 | 証跡 | Sonnet観察 |
|---|---|---|---|
| 1 | Production正式初回path | `er019_family_x_entertainment_production_runner_01.py`(新規entry point、`--theme/--slug/--out-dir/--stage/--regenerate-stage/--stop-after`) | 実装・実runで発火確認 |
| 2 | Research→Ledger接続 | `run_01/research_ledger/`(`fact_ledger_draft.json`/`fact_ledger_verification.json`/`verified_fact_ledger.txt`/`verdict_counts.json`/`runtime_evidence.json`)。`er012_e_family_entertainment_two_level_runner_01.run_researcher_for_topic`/`run_verification_for_topic`をそのまま呼び出し | VERIFIED 15/AMBIGUOUS 0/REJECTED 0、web_search_call_count=7 |
| 3 | AI Storyline生成 | `run_01/storyline_b3/fact_selection_evidence.json`(`selected_storyline`) | LLM 1 callで1行決定、Full Ledger 15 Factを踏まえた内容 |
| 4 | B3 4テスト | 同上`fact_tests`(15件全Factにtest1-4回答+reason) | 全Fact個別回答、ハードコードFACT_TESTS不使用(新規LLM判定) |
| 5 | Selected Brief生成 | `run_01/storyline_b3/selected_brief.md` | 3 Fact採用(目安3〜5件の範囲内、recheck_note=null) |
| 6 | Writer入力への接続 | `run_01/ja_writer/runtime_evidence.json`のoriginal.prompt(「テーマ：」行=Storyline、[ニュース]=Selected Fact Brief) | 接続を実データで確認 |
| 7 | Original→R1→R2正式path | `run_01/ja_writer/{original,revision1,revision2}.md`+`runtime_evidence.json`(chain_method="previous_response_id"、r3なし) | 3段とも生成、previous_response_id連鎖成功(fallback未使用) |
| 8 | Advanced・Standard整合 | `run_01/b1b/article.md`(411語、LEDGER_COMPLIANT)+`run_01/a2/article.md`(414語、LEDGER_COMPLIANT) | `er012_e_family_entertainment_two_level_runner_01.run_writer_stage`をそのまま呼び出し |
| 9 | retry | Storyline+B3: `storyline_b3/runtime_evidence.json.attempts=1`(retry不要)。Advanced: 1回目MAJOR→1回retryでPASS(既存`vfl01.run_deviation_check`→`run_writer_stage`の1回retry cap)。B3 moduleは技術的Fact ID不整合等で1回retry→STOPの構造をunit testで確認(`RunStorylineB3SelectionTests`) | Advanced retryが実際に発火し正しく機能したことを確認 |
| 10 | fallback | JA Writer: `chain_method="previous_response_id"`(fallback_full_text未使用、ただしunit testで両経路を検証)。Advanced/Standard: 既存`vfl01.run_writer_with_technical_retry`のfallback方針(未定義)をそのまま流用、変更なし | 既存Production方針を維持 |
| 11 | regeneration | `--regenerate-stage storyline_b3|writer|advanced|standard`実装(今回未使用、advanced/standardは`efam.run_writer_stage`のdeviation MAJOR時1回再生成→STOP構造をそのまま流用) | 今回は両段ともdeviation=LEDGER_COMPLIANT(1回で通過、再生成不要) |
| 12 | Full LedgerとSelected Briefの分離 | `storyline_b3/full_ledger.json`(ledger_text全文) vs `storyline_b3/selected_brief.md`(Storyline+3 Fact要約)。別ファイル(unit test`LedgerAndBriefSeparationTests`で検証) | 分離済み、deviation checkはFull Ledgerを使用(`run_writer_stage`へledger_text=Full Ledgerを渡す実装) |
| 13 | runtime evidence | 各stageディレクトリの`runtime_evidence.json`(research_ledger/storyline_b3/ja_writer)+`writer_run_summary.json`(advanced/standard) | 全stage揃い |
| 14 | actual model_id | 全stageで`model_id_actual`(または`response.model`)="gpt-5.6-luna"を記録・確認 | fallback_detected=false(advanced/standard) |
| 15 | Fact selection evidence | `storyline_b3/fact_selection_evidence.json`(selected_storyline/full_ledger_fact_ids/fact_tests/selected_fact_ids/recheck_note/soft_warnings) | 追跡可能な形で保存 |
| 16 | cost evidence | `run_01/cost.json`(stage別内訳、完了) | Research/Ledger/Storyline+B3/Original/R1/R2/Advanced/Standardを分離集計。合計¥40.00 |
| 17 | integration test | `er019_family_x_b3_production_wiring_01_test_01.py`(24件、mock LLM、stage順序・Ledger/Brief分離・後工程不在を検証) | 24/24 PASS |
| 18 | regression test | `python -m unittest discover -s . -p "*_test_01.py"` | 全PASS(exit code 0、実行ログ確認済み) |
| 19 | CURRENT_SPEC | `CURRENT_SPEC.md` L828行(Entertainment Writer方式)への追記 | 反映済み(WIRING INCOMPLETE維持、PRODUCTION_WIREDへは変更していない) |
| 20 | DECISION_LOG | `DECISION_LOG.md`新規エントリ(NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01) | 反映済み |
| 21 | OPEN_ITEMS | `OPEN_ITEMS.md` OPEN-177(1)更新+OPEN-183新設(記事ユーザー確認待ち) | 反映済み |
| 22 | Git commit・push | commit `365b572d6fc67da39c39999fd4d8b04cac9faded`、`git push origin main`実行済み(`8975bd8b..365b572d`) | 完了 |
| 23 | Dangling Reference Check | `NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01_REPORT.md`§Dangling Reference | Grep結果を別途記録 |
| 24 | ユーザー承認仕様との一致 | 本委任文ユーザー確定事項1〜13との対応表(REPORT参照) | Sonnet仮判定のみ、正式判定はFable/ユーザー |

**Status(Sonnet仮)**: 上記1〜18は技術的証跡として充足(N=1記事のrun)。19〜21はSSOT反映済み。22は本Report作成後に実施。24はREPORT参照。**`PRODUCTION_WIRED`の正式判定はFable/ユーザーが行う**(Sonnetは自称しない)。記事内容自体はOPEN-183によりユーザー確認待ち。
