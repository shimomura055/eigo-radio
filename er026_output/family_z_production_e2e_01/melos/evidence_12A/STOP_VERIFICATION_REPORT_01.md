# STOP_VERIFICATION_REPORT_01 (FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_12A, 2026-10-12)

課金JPY0・実API 0(mock/dry-runのみ)。test=`er026_family_z_stop_sentinel_test_01.py` 16件 全PASS(約110秒)。
実行: `.venv/Scripts/python.exe -m unittest er026_family_z_stop_sentinel_test_01 -v`

| 項目 | 内容 | 結果 | 証跡(本dir) |
|---|---|---|---|
| 1 | 初回mock run(TTS途中)にSTOP設置 -> 次のAPI境界で停止 | PASS: rc=3、STOP時点21呼出=最終21呼出、STOP後の呼出0、audit記録(`where=tts:comment_2`)、RUN_LOCK残存なし、cost_log未作成 | item1_initial_run_stop.json / item1_run_stoptest_01/ |
| 2a | 共有`er002_common._call_tts_with_retry`(`except Exception`+sleep)内のretryでSTOP | PASS: 2回目のAPI呼出を阻止(BaseException系で握り潰されない) | item2a_shared_retry_loop.json |
| 2b | primary NG -> fallback前にSTOP(Z側生成wrapper経由) | PASS: fallback呼出0 | item2b_fallback_blocked.json |
| 2c | 共有`er020.maybe_cooldown_before_attempt`の待機中にSTOP -> 待機後の再生成前に停止 | PASS: 待機後のAPI呼出0 | item2c_cooldown.json |
| 2d | 実SDK入口(OpenAI Responses/Transcriptions、Gemini generate_content)のguard | PASS: STOP中はnetwork前に停止。install順=cost_logger後・client生成前(最外殻) | item2d_sdk_entry_guard.json |
| 3 | `--regenerate-stage` と resume(tts_b1b/tts_a2/all)でSTOP検出 | PASS: 全てrc=3、呼出18のまま不変。`--clear-stop`後は再開しrc=0(対照) | item3_regenerate_resume.json / item3_run_stoptest_03/ |
| 4a | runpy wrapper / 別名コピー / subprocess wrapper / 直接real / Writer単体CLI をSTOP_ALLで | PASS: 全てrc=3(Writer単体CLIもrc=3)、run dir未作成。別cwdは共有moduleのimport時相対path依存で失敗(API到達前)、STOP_ALL自体は別cwdでも検出(絶対path) | item4a_wrappers_blocked.json |
| 4b | RUN_LOCK.json二重起動拒否 | PASS: 生存PIDのlock -> rc=4・呼出0、holder死亡後(stale)は起動可、実2プロセス同時起動でP2 rc=4・API呼出はP1のみ、親PID記録 | item4b_run_lock.json / item4b_run_stoptest_4b2/ |
| 4c | STOP_ALL中は`--mode real`をclient生成前に拒否 | PASS: build_real_context / er062 _setup_real / er063 real_generators・attribution / main(real)の全てで、get_client・cost_logger.installをAssertionErrorに差し替えても未到達、run dir未作成 | item4c_real_refused_before_client.json |
| 4d | RESTART_STORM(5分間に3回起動) | PASS: 3回目でrc=3、`<run>/STOP`+`RESTART_STORM_LOCK.json`自動作成、起動履歴3件、auditにRESTART_STORM | item4d_item6_restart_storm_clear.json / item4d_run_stoptest_4d/ |
| 5 | STOP後のAPI呼出0・追加費用0 | PASS: 項目1/3のカウンタ不変、STOP_ALL下のreal起動試行後も`run_e2e_01/cost_log.jsonl`(226,946B)・stage_logのsize/mtime不変 | item5_no_spend.json |
| 6 | 解除は明示的正規操作 | PASS: RESTART_STORMはSTOP手動削除でも解除されず(markerが残る)、`--clear-stop`は`--reason`なし=rc2、あり=解除+`audit_stop_sentinel.jsonl`にCLEARED記録。通常STOPは手動削除でも可。RUN_CLOSEDは`--clear-stop`でもrc=5で解除不可。STOP_ALLは`--clear-stop`で消えない | item4d_item6_*.json / item6_clear_stop_rules.json |
| 7 | 新しい実行手段を作らない | PASS: 文書規則(PM_GOVERNANCE 26節+26-5)+機械的阻止(4a/4b/4c/4d)。`tools/stop_all_family_z.py`: dry-run=列挙のみ・STOP_ALL未作成・process生存、`--execute --reason`=STOP_ALL作成+対象process停止(dummyで確認)、`--release --reason`=解除+監査記録 | item7_stop_all_tool.json |
| 8 | 統合test `test_shared_state_files_unchanged_by_mock_run` の再確認 | PASS: Coffee run(`er019_coffee_p8_wiring_evidence_01.py`)終了確認(関連process不在、監視対象stateの更新停止)後、`er026_family_z_e2e_integration_test_01` 42件OK(同testを含む) | (統合test出力。下記) |

## Regression(新規failure 0)
er026統合 42件OK / er062 63件OK / er063 46件OK / er060 9件OK / er026_..._runner_01_test 21件OK / 本検証 16件OK。

## 残存リスク・制約
- 別cwdからの起動は共有module(er002_ja_article_generation)がimport時に相対pathを読むため失敗する(既存仕様。API到達前なので安全側)。
- Writer単体CLI(er062_family_z_writer_01.py)はSTOP確認のみ(RUN_LOCK/RESTART_STORM未実装)。
- Azure STTのwrapは`from module import fn`で既に束縛された参照には効かない(cost_loggerと同一制約)。OpenAI/Gemini入口はclassレベルwrapのため全参照に効く。
- STOP_ALL/STOPを置く/外すのは運用(Fable/ユーザー)。実行層が`tools/stop_all_family_z.py --release`や`--clear-stop`を使うこと自体は技術的には可能だが、文書規則(26節)で禁止。
- 環境変数`FAMILY_Z_MOCK_API_DELAY_SEC`はmock専用(real経路では参照しない)。
