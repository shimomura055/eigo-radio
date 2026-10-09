# 委任_05 結果 FACTLOCK-ASTRA-E2E-TRIAL-01(2026-10-09) Status=IMPL_READY / G0_PASS(stub、API支出¥0)

## 1. 成果物・commit・テスト
- commit1(単価登録): 46be02ad / commit2(本体): 下記追記(hash追記commitで確定)
- 新規: er052_factlock_astra_e2e_runner_01.py(1258行、指針450-600行を超過)、_stub_01.py、_aggregate_01.py、_ws_check_01.py、_runner_01_test.py(31件)
- 変更: er005_output/cost_baseline_01/pricing_snapshot.json、er006_model_routing_pricing_coverage_test_01.py(commit1)
- テスト: runner test 31件 OK(282秒)、er006 pricing 9件 OK、m123 16件 OK。既存全体回帰 325件中1 error(TtsModeCliTests.test_batch_mode_without_reason_errors_via_subprocess。PYTHONUTF8未設定時のcp932起因の既存環境問題、PYTHONUTF8=1でPASS、本変更と無関係)。
- 証跡: er052_output/factlock_astra_e2e_trial_01/g0_dryrun/(unittest_log.txt含む)、g0_dryrun_g0check_10themes/

## 2. 前提作業の状況
- (a) 完了(別commit)。設計3メーターに加え cache_write 12.50も登録(commit message準拠)。PricingNotFoundError解消をテスト。
- (b) 完了(R0・最終JA、両腕、記録のみ) / (c) 完了(strip単一経路) / (c2) 完了(1記事1回・Trial全体3回、E2E_B1_TOTAL_MAX、counterはroot/b1_counter.jsonl+.b1_lock)
- (d) 完了(M1 Standardは未実装、majors_only_in_summaryで分類ログのみ) / (e) 完了(strip_markdown→ellipsis→dash、Astra R2直後・FC前)
- (f) 完了(規模超過)。差分: 承認スイッチ/FLOOR_MODEは環境変数でなくChecker subprocess内でapply_open233_approved_flow_switches()+assertで適用。M3の保護主張再判定は未実装、G3 telemetry(telemetry/g3_telemetry.jsonl)件数記録のみ。
- (g) 完了: run_02でguard 19.1047 / er019 19.105 / cost.json 19.105 一致(web_search 2行9call ¥14.4)
- (k) 完了(cap1000/alert800/astra x1.5、超過でGlobalStop・STOP.json・exit3) / (m) 完了(shimパッチ+raw usage事後検査、stubでresearch/web_search発生時に全停止をテスト) / (i) 完了(固定分母2x themes/腕)

## 3. G0 dry-run
- 旧4テーマ(meta/hormuz/space_weapons/small_bag)x2腕x2レベル、全stage done(新腕: new_r0/r1/r2/ii/en_adv/en_std/shadow/check_adv/check_std、旧腕: er019 shim)。シナリオ: hormuz=旧case B+新B1+summary-major影、space_weapons=両腕R2後FC MAJOR、他default。B1回復2件(counter)。環境分離確認(旧腕M1/M3なし、新腕M1=1+PROTECT=changed_actor、M2両腕OFF)。
- 10テーマG0照合のみ(g0_dryrun_g0check_10themes/): 全PASS(台帳sha・B3 sha・check_a・JSON整合・宇宙兵器台帳一致)。
- 代用した入力: B3は委任_06のstage_r再生成版を使用(凍結B3ではない)。注記は機械的dry-run注記(仕様v2の成果物ではない)。注記版JSONは自動導出し整合検査をスキップ(substitutionsに記録)。stub費用(約¥217 raw/guard 296)は実測ではない。

## 4. 実行コマンド(cwd=repo root、.venv/Scripts/python.exe -X utf8 er052_factlock_astra_e2e_runner_01.py ...)
- 共通: 既定 cap1000/alert800/E2E_B1_TOTAL_MAX=3/--checker-cap 10/--arm-cap 100。実API時は OPENAI_API_KEY 等を通常環境から引継ぎ(stage subprocessはホワイトリスト環境)。--stub は付けない。入力は inputs/<theme>/ → stage_r/<theme>/ の順。
- G1: `run --root er052_output/factlock_astra_e2e_trial_01/runs --themes meta --arms new --until new_check_adv --worker-id 1` 続けて `--arms old --until old_adv`
- G2 round1: 4プロセス(旧4テーマ各1、--worker-id 1..4、--themes <theme>、両腕、同--root)
- G2 round2: 3プロセス(新6テーマを2つずつ、--worker-id 5..7)
- 再開: 同コマンド再実行(stage markerで継続)。runner/stub改変後は --allow-script-change が必要。

## 5. 未確認・Fable判断要(優先順)
1. 実API経路は未実行(Astra応答形、動的fixtureのChecker(baseline_parsed=None)、M1/M3実挙動)。G1が初の実証。
2. 注記仕様v2は注記版JSON(fact_selection_evidence)の作り方を定義せず、runnerは自動導出+整合検査スキップ。要判断。
3. 注記パイプライン最終成果物(inputs/<theme>/selected_brief_annotated.md、annotation.json)未着。着荷までstage_rへfallback。
4. 仕様ファイルshaの記録値は生CRLFバイト一致、LF正規化値と不一致(ANNOTATOR.md・SPEC_v2.md・check/merge py・test py)。LF値はg0.jsonに出力。「LF正規化後sha」運用との整合を要判断。
5. astra請求照合未了のためx1.5維持。cache_write登録は設計(3メーター)と差分。
6. runner 1258行(指針超過、分割要否)。タグ測定は最小限(LLM pair_check・数値クロスチェック未実施、r0_with_tags.md保存のみ)。(ii)検出器は両腕のR0と最終JA。
7. TTS入口は未特定。round2のworker-idとテーマ組合せはFable決定。
8. 作業中に誤って `git stash`(-uなし)を実行、直後に pop で復元済み(HEADとM一覧は復元確認済み)。

## 6. 所要時間・API支出
- API支出¥0(全stub)。所要時間は未計測(長時間セッション、テスト全件約282秒)。
