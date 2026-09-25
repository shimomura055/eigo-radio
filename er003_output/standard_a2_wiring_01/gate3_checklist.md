# gate3_checklist.md — NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01

Gate 3(Production Wiring Checklist)14項目の判定と根拠。

| # | 項目 | 判定 | 根拠 |
|---|---|---|---|
| 1 | Production正式初回経路へv5実装(runnerから呼ばれる位置に接続) | **×** | `recon.md` (a)(b)確認のとおり、日本語Entertainment R2・Advanced Natural Adaptationいずれも既存Production経路が存在しない。`er003_v1_n3_01_standard_a2_generate.py`はどのrunner(`er012_b_family_production_runner_01.py`等)からもimportされていない。 |
| 2 | retry・fallback・regenerationとの整合 | **△** | `generate_standard_a2()`は既存`vfl01.run_writer_no_search()`を再利用し、空出力→1回再試行・fallbackモデル未定義という既存Production方針(News A2/B1 Writerと同一)を関数レベルで満たす(単体テストで確認)。ただし、この関数を呼び出す上位のオーケストレーター(`MAX_WRITER_ATTEMPTS`等)自体が存在しないため、「既存オーケストレーターとの整合」を実地確認することはできない。 |
| 3 | DEV・Trial-onlyではないこと | **○** | `er003_v1_n3_01_standard_a2_generate.py`はer003 Family命名のProduction moduleとして実装済み。Trial script(`er015_*`)からのimportは無し(`Grep "er015_"`結果はコメント・テスト内パス文字列のみ、`import er015`文は0件)。 |
| 4 | Advanced Natural→Standard A2の正式経路との整合(Advanced経路の存在含む) | **×** | Advanced自体のProduction実装が存在しないため、「正式経路との整合」を確認する対象が無い。 |
| 5 | Key Words/Phrasesとの役割分担に矛盾なし | **△** | 設計上は独立工程(`recon.md` (e))であり矛盾は無いが、Standard A2が未接続のため実接続テスト・入力選択(Advanced本文かStandard本文か)の判断は未実施。 |
| 6 | Production runtimeでの実発火 | **×** | 実施したのはCLI直接実行(`--advanced-file`/`--out-dir`)であり、Production runner経由ではない(runner自体が存在しないため)。 |
| 7 | 必要testのPASS | **○** | 単体テスト14件PASS(`er003_v1_n3_01_standard_a2_generate_test_01.py`)。影響範囲regression(`er006_model_routing_contract_01_test.py`、`er003_discovery_focus_staged_production_01_test_01.py` 24件、`er011_discovery_focus_s2_full_trial_01_test_01.py` 22件、`er003_v1_en_direct_vfl_01_generate_deviation_v2_test.py` 6件)すべてPASS。 |
| 8 | runtime evidence | **○** | `er003_output/standard_a2_wiring_01/{sewer,meta}/runtime_evidence.json`にmodel_id実値・response_id・usage・cost・prompt sha256・checksを記録。 |
| 9 | 実際のmodel_id・routing確認 | **○** | Sewer/Meta両方でmodel_id_actual=`gpt-5.6-luna`確認、`routing.require_model("STANDARD_A2_ADAPTATION", ...)`使用(routing SSOTへ新規process追加)。 |
| 10 | コスト影響評価 | **○** | 合計cost_jpy=0.8024(Sewer 0.5045+Meta 0.2979)、予算¥20の4%程度。Production接続後の1記事あたり追加コストは1 call相当(既存Advanced生成コストに、Standard A2生成1 call分[概算¥0.3〜0.5]が追加される見込み)。 |
| 11 | `CURRENT_SPEC.md` | **○** | L829にStandard(A2)行を新設、v1〜v5履歴・配線Status・関連管理IDを記録(本コミットで反映)。 |
| 12 | `DECISION_LOG.md` | **○** | 本管理IDで新規エントリ追加(ユーザー正式採用逐語・偵察結果・実装・runtime evidence・Gate 3チェックリスト・未完了事項を記録、本コミットで反映)。 |
| 13 | `OPEN_ITEMS.md` | **○** | OPEN-177を更新(サブ項目(2)(5)(9)をCLOSED、(1)(3)(4)(6)(7)(8の一部)はOPEN継続として明記、本コミットで反映)。 |
| 14 | 必要なGit反映 | **○**(本レポート後にcommit実施) | 新規module・test・evidence・SSOT更新・REPORT・delegation_logを対象ファイル指定でcommit。 |
| (別項目) approved specとProduction挙動の一致 | **○** | Prompt本文はv5逐語(sha256 assert、`STANDARD_A2_PROMPT_SHA256`)、実行結果(Sewer/Meta)は「6,000語超を必ず置換ではない」という正式仕様どおり(septic/wastewater/artery等の必要語残存、不自然置換なし)。 |
| (delegation 14) Dangling Reference Check | **○** | `Grep "er015_" glob="er003_*.py,er012_*.py"`は本タスクの新規ファイル自体(コメント・テストのパス文字列のみ、`import er015`文なし)を除き0件。`Grep "STANDARD_A2_PROMPT_V5"`定義1箇所(`er003_v1_n3_01_standard_a2_generate.py`)+参照(同ファイル内`build_prompt`/`reconstruct_prompt_file_text`)のみ。 |

## 最終判定
×3件(1, 4, 6)、△2件(2, 5)が残るため、**`PRODUCTION_WIRED`にはしない**。
最終Status: `APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`。

STOP条件(delegation記載)に該当: 「Advanced Natural→Standard A2の正式初回経路が
存在せず、経路の設計[入口・Production contract付与・downstream接続]に仕様判断が
必要」。経路設計はFable/ユーザー判断待ちとし、本タスクでは実施しない。
