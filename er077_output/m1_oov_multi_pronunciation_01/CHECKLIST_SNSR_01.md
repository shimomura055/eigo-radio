# CHECKLIST_SNSR_01(STOP-NOTICE-SCOPE-RULE-PRODUCTION-01、Checklist 12項目+Dangling、2026-10-14)

判定: **`APPROVED_FOR_PRODUCTION`(ユーザー2026-10-14案a)。`PRODUCTION_WIRED`は付与しない**(未充足: 1部分・5部分。他runner/Coffee側へのコード統一が未了)。

| # | 項目 | 判定 | 証跡 |
|---|---|---|---|
| 1 | 正式初回経路 | **部分**: M1 evidence runnerのSTOP判定は共通helperを通る(`MANAGED_IDS`+毎clip前再判定)。他runner(er019/er026・062・063/er064系/er065/er067/er073)は未配線=承認範囲内の後続(OPEN-354) | runner、`STOP_SCOPE_RULE_01.md` §4-5 |
| 2 | retry/fallback/既存停止機構との整合 | 充足: STOP_ALL・自run STOP・RUN_LOCK・RESTART_STORM・SDK入口guardは無変更。helperは読取専用、停止方向のfail-closed。retry上限・予算hard stopは無変更 | test 21件、diff |
| 3 | Trial専用実装に依存しない | 充足: helperは標準ライブラリのみ | `tools/stop_scope_check_01.py` |
| 4 | Regression PASS(正常系・異常系) | 充足: 9系統(自ID宛/STOP_ALL/自run STOP/RUN_LOCK/scope=ALL/CLOSED/他ID限定run/parse不能/旧書式)+補強、21件+9 subtest PASS。既存M1 68/配線22/F1 39/er077 14 PASS | `regression_01/snsr_helper_test.txt` |
| 5 | 正式経路でのruntime発火 | **部分**: 正式evidence runnerで、旧Melos NOTICEが存在する状態でhelperが非適用と判定し有料run(JPY3.3435)が完走。ただし**適用側(実NOTICEで停止)の実機発火はtestの擬似ファイルのみ**(実センチネル・実NOTICEは作成禁止のため) | `EVIDENCE_RUN_01.md` §4 |
| 6 | actual model_id/routing | N/A(STOP判定は非LLM)。evidence runのモデルは`EVIDENCE_RUN_01.md`冒頭 | - |
| 7 | CURRENT_SPEC更新 | 充足 | CURRENT_SPEC「STOP_NOTICE適用範囲規則」 |
| 8 | DECISION_LOG更新 | 充足 | DECISION_LOG |
| 9 | OPEN_ITEMS更新・整理 | 充足(OPEN-354/355) | OPEN_ITEMS |
| 10 | commit/push/merge | 充足見込み(明示add・secret scan・Managed-ID trailer) | git log |
| 11 | 承認内容とProduction挙動の一致 | 充足: 非適用は旧書式で「見出しID=ファイル名ID+対象run明示限定+全体宣言なし+自runが対象外」を全て満たす場合のみ。ID文字列の相違だけでは非適用にならない。全体STOP/親scope/自ID/parse不能は停止維持。classifier拒否理由(STOP判定縮小)に対し、解消範囲は適用範囲規則の明確化のみで安全機構は未変更 | `STOP_SCOPE_RULE_01.md` §1-3 |
| 12 | Coffee側とM1側のSTOP解釈の一致(条件4) | **部分**: 文書上は整合(Coffee=§26-2(d)の存在確認、案aと矛盾しない)。コード統一は未了 | `STOP_SCOPE_RULE_01.md` §4 |
| D | Dangling Reference | 充足: 参照先(`tools/stop_scope_check_01.py`・`_test_01.py`・`STOP_SCOPE_RULE_01.md`・`EVIDENCE_RUN_01.md`・`CHECKLIST_*`・`evidence_01/stop_check_01.json`)は実在 | ls確認 |

## 未充足
#1/#12(他runner・Coffee側コード統一=OPEN-354)、#5(適用側の実機発火はtest擬似ファイルのみ)、NOTICE新書式正本化・Governance文言統一(OPEN-355)。
