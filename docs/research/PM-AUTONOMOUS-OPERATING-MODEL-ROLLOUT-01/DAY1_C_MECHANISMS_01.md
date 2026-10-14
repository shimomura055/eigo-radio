# DAY1_C_MECHANISMS_01: 既存の自動チェック機構の棚卸(C)
管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / 委任_01A / 2026-10-14 / read-only・JPY0
STOP確認: `*STOP_NOTICE*`=2026-10-12 Melos 1件(旧・非適用)、`STOP_ALL`/`STOP`なし。事実/推測/未確認を明示。

## 1. 既存機構の所在(事実)
| 区分 | 実体 | 強制力 |
|---|---|---|
| STOP共通実装(Family Z) | `er062_family_z_structure_01.py` の `check_stop_sentinel`(L129)・`install_api_stop_guard`(L176)。RUN_LOCK(rc=4)・RESTART_STORM(5分3回)・`--clear-stop --reason`。`tools/stop_all_family_z.py`。テスト `er026_family_z_stop_sentinel_test_01.py` | コード(Z runner `er026_family_z_fiction_production_runner_01.py`/`er062`/`er063`) |
| runner別STOP確認(Z以外) | 8通り: ①`er064_kp_int_03_run.py` 管理ID付きglob `*STOP_NOTICE*KP-INTEGRATED*` ②`er065_..._runner.py` NOTICEを読むが別管理IDは無視 ③`er067_..._trial_01.py` NOTICEを読むだけ・STOP/STOP_ALLのみ阻止 ④`er070_..._alignment_01.py` センチネルのみ ⑤`er073_..._run.py` 旧通知の管理IDを除外 ⑥`er077_m1_oov_..._evidence_runner.py` 全`*STOP_NOTICE*`で停止(T6の原因) ⑦`er057_coffee_comment4_trial_03.py` STOP存在をassert ⑧`er057_..._h_speed_05_gen04.py` STOP_ALLパス参照 | 各runnerが任意実装(統一なし) |
| Validator(名称のみ) | Audio Validation Gate=`er003_v1_n3_01_assemble.py` `verify_episode_audio_validation_gate`(L469)、KP source gate=`verify_key_phrase_source_gate`(L385)・`er003_key_phrase_source_gate_01.py`、ASR cascade=`er006_secondary_asr_01.py`。Rule7/M3の入口関数名は未確認 | コード(Gate迂回は実績なし) |
| secret scan | `tools/secret_scan_01.py`(`--staged`/`--rev`/`--untracked`)。§26-X・RESULT_PACKETに`hits=0`記録 | 人が実行(自動起動なし) |
| 委任文検査 | `docs/pm/tools/check_delegation_prompt.py`(`tools/`直下には無い)。`*_check.json` 587件中 PASS 284 / FAIL 277(約49%、要点保存で必須節欠落) | 非blocking |
| Git hooks | `.git/hooks`は`*.sample`のみ(有効0)、`core.hooksPath`未設定 | なし |
| Claude Code hooks | `.claude/settings.local.json`は`permissions`のみ、`~/.claude/settings.json`にもhooks 0。プロジェクト`settings.json`なし | なし |
| CI | `.github/workflows` 7件。`ci-test.yml`は`automation/AUTO-001-clean`へのpushとmain向けPRのみ(mainへ直接push運用ではCI不発動)。他6件はAUTO-001(`workflow_dispatch`)。`scripts/run_ci_tests.py`は独立manifest方式 | CIはPR時のみ |
| 回帰テスト | `run_project_regression.py`(pattern `er0*_test_*.py`、259ファイル)。手動実行 | 人が実行 |
| 費用記録 | `raw_usage_log.jsonl` 657ファイル、`cost_summary*.json` 104ファイル、`er005_output/cost_baseline_01/`(`cost_summary.json`/`pricing_snapshot.json`/`raw_usage_log.jsonl`)。予算ガード関数が各スクリプトにコピー: `compute_cost_jpy_so_far` 38ファイル・`assert_budget_ok` 26ファイル・`compute_actual_cost_jpy` 5ファイル、`--approved-budget-jpy`/`--budget`系13ファイル。詳細集計は委任_01B(D)の担当 | run単位のみ。タスク横断・日次の集計機構はなし |
| 手更新の台帳 | UDR_REGISTER(行59件 vs 集計「合計55」)、ACTIVE_TASK固定ヘッダ(UDR「35件」)、OPEN_ITEMS | 手更新(ズレ実測) |

## 2. 提案5機構の判定(RPD §6/§10/§13、#51〜#55)
| 提案 | 既存で満たす部分 | 不足 | 結論 | 新設時の負荷(定性) |
|---|---|---|---|---|
| stop_check(#52) | Z系は完備(センチネル・RUN_LOCK・STORM・API guard・テスト)。26-5 | Z以外は8通り。STOP_NOTICEに適用範囲欄なし。規則文言も不一致(agent定義=全`*STOP_NOTICE*`、§26-2(d)=該当管理ID)。Securityの分類器がrunner側globの変更を拒否した実績(T6) | **既存拡張**: ①STOP_NOTICEに`scope: <管理ID>`1行を足す運用 ②`check_stop_sentinel`をZ専用でなく汎用に使えるよう薄く拡張し、新runnerは1行呼ぶだけにする ③agent定義/§26-2(d)の文言を1箇所に揃える。新ライブラリ・新状態ファイルは不要 | 小。既存runnerの一括書換えは不要(新規・改修時のみ) |
| state_gate(#51) | Statusは文書(OPEN/CURRENT_SPEC/UDR/ACTIVE_TASK)に手書き。`docs/pm/state/`は存在しない | 機械可読な状態・遷移検証・委任回数の自動計数なし(手更新はズレ実測) | **新設は後回し(Day3-4対象外)**。当面は既存Statusの整合lint(下記docs_lint)と、Trial結果をProductionと混同させない運用規則(維持)で代替(推測) | 新設すると全タスクに状態更新が増え、負荷大 |
| budget_gate(#53) | run単位ガード(上記コピー群)、費用ログ、§7-6 Guardrail | タスク横断・日次(JST)集計、量産1記事セット70円の判定入口。OPEN-242(web_search未計上)・OPEN-315(旧run累計を見ない)の既知穴 | **既存拡張(小)**: 既存`raw_usage_log.jsonl`を日付で合算する読み取り専用script1本+委任文に残額1行。新しい実行時ガードは作らない。データ構造の可否は委任_01Bの結果と突合(未確認) | 小(集計scriptのみ)。実行時ガードを足すと各runner改修で大 |
| docs_lint(#54) | `check_delegation_prompt.py`(形式検査、FAIL常態で情報量低)、`secret_scan` | UDR集計・ACTIVE_TASKヘッダ・OPEN行長・常駐文書量の検査なし | **既存拡張**: `docs/pm/tools/`に1スクリプト(UDR行数と集計の一致/ヘッダ件数/常駐文書量)。`check_delegation_prompt`はblocking化せず、要点保存時は検査対象外にする1行修正が現実的 | 小。lint項目を増やすほど保守が増える |
| Git hook+強制Regression(#55) | `secret_scan_01.py --staged`が既に存在。regression入口`run_project_regression.py`あり | commit時の自動起動なし。10-12にAzure Keyが平文混入しpush protectionが拒否した実績 | **新設(極小)**: pre-commit 1本で`secret_scan_01.py --staged`のみ(`core.hooksPath`の設定変更を伴うためDay2でユーザー承認要)。**強制Regressionは新設しない**(259ファイルは遅く、commit毎実行は速度を落とす。変更範囲に応じた手動実行を維持) | pre-commit: 小。全regression強制: 大 |

結論(機構数を増やさない観点): 新規フレームワーク級の新設は**0**。実装は ①secret scan用pre-commit(極小新設) ②STOP_NOTICE範囲欄+汎用呼出+文言統一(拡張) ③日次集計script(拡張) ④lint 1本(拡張) ⑤報告マーカーhook(下記)。state_gateは後回し。

## 3. 報告マーカー違反の防止(既存の軽量手段で足りるか)
- 既存: agent定義(`sandwich-pm.md` L104-108)・§9-8-1・CLAUDE.md復帰手順(8)・auto-memoryの4箇所に文言あり。にもかかわらず2026-10-05と10-12に再発(事実)。**文章の追加では防げない**。
- 軽量な機械化案(推測・未検証): プロジェクトの`.claude/settings.json`にStop hookを1件追加し、最終応答に`★★★★報告ここから★★★★`/`★★★★報告ここまで★★★★`が両方あるかを数行のscriptで検査して欠落時は差戻す。1ファイル+1スクリプト。留意点(未確認): `claude --agent sandwich-pm`でhookが主スレッドに効くか、tool呼出を伴う途中報告は捕捉できない可能性、無限差戻し防止(stop_hook_active確認)。Day2に実機で最小検証が必要。
- RPD OF-220(hooks設定ファイルの扱い)の注意と整合させ、`settings.local.json`ではなく共有`settings.json`に置くか、ユーザー承認(設定変更)が要る点はDay2判断。
