# STOP_SCOPE_RULE_01(STOP-NOTICE-SCOPE-RULE-PRODUCTION-01 委任_01、2026-10-14)

ユーザー正式承認(2026-10-14、案a): 停止判定の適用範囲を (1)当該管理IDに有効なSTOP_NOTICE (2)共通のSTOP/STOP_ALL等の全体停止条件 (3)既存安全機構が定めるその他の有効な停止条件 に整理する。**単純な管理ID文字列一致で安全停止を迂回してよいという承認ではない。** Status=`APPROVED_FOR_PRODUCTION`(PRODUCTION_WIREDは全Checklist充足時のみ)。

## 1. 実装(`tools/stop_scope_check_01.py`、読取専用、API 0)
判定順(1つでも「適用」なら stop=True、rc=3):
1. `er026_output/family_z_production_e2e_01/STOP_ALL`(全体) -> 常に適用
2. 自runディレクトリの`STOP` -> 常に適用
3. `docs/pm/delegation_log/*STOP_NOTICE*`を1件ずつ判定(sha256と判定理由を結果JSONへ記録)
   - a. status=CLOSED/RESOLVED/RELEASED/EXPIRED/解除/終了 or expiresが過去 -> 非適用。expiresがparse不能 -> 適用(fail-closed)
   - b. 本文に自管理ID(複数可)・親IDが現れる -> **適用**
   - c. 構造化`scope:` が ALL/全体/有料run全般/API/PARENT/親/FAMILY -> **適用**。run限定(`run:<名>`等)は自run名が列挙されれば適用、なければ非適用。未知の値 -> 適用(fail-closed)
   - d. 旧書式(scope欄なし): 「見出しIDとファイル名IDが一致」かつ「対象runを明示限定する文言(`run_xxx の(以降の)実行は無効`)」かつ「全体宣言の文言なし」かつ「限定対象が自runでない」のときだけ非適用。それ以外(読取失敗・parse不能・限定文言なし・全体宣言あり)は**適用(fail-closed)**
4. 自runの`RESTART_STORM_LOCK.json` -> 適用。`RUN_LOCK.json`は生存PID(自プロセス/親を除く)が保持なら適用、parse不能なら適用、staleは非適用(Windowsでは`os.kill(pid,0)`がTerminateProcessになるためOpenProcess/GetExitCodeProcessで生存確認)
helperはSTOP/NOTICE/LOCKを作成・編集・削除しない(testで確認)。管理ID文字列が違うだけでは非適用にならない(a/c/dの根拠が必須)。

## 2. 旧Melos NOTICEが現在のM1に非適用である証拠
対象: `docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md`(sha256 `ee1311ecf42ad21dffb26e22d7b5e99251e02045602036d3f770ea88bfa1b6b2`、作業ツリー版)
- 見出し: `# STOP NOTICE (FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01, 2026-10-12, ローカルのみ・commitしない)`、ファイル名のIDと一致。
- 本文冒頭: 「ユーザー仕様変更により **run_e2e_01 の以降の実行は無効**。再開は委任_11以降の指示に従う。」= 対象run明示限定。
- 停止したプロセスは全て`er026_family_z_fiction_production_runner_01.py ... --run run_e2e_01`系と、その別名wrapper(runner_dbg/dbg3/dbg4。26節の別名ラッパ事故の記録)。
- grepで確認: 全体宣言(`全体停止|全体STOP|全run|全ての有料|全API|全管理ID|all runs|STOP_ALL を発行`)なし。`scope/status/issuer`欄なし(旧書式)。M1のID(`ASR-M1-...`)・本管理IDの文字列なし。(`全体`は「provider別(全体, entries/...)」の集計見出し、`全て`は「全て ... run_e2e_01」の説明文であり宣言ではない。)
- helper判定: `evidence_01/stop_check_01.json` -> `applies=false, rule=d_legacy_id_match_run_limited`、STOP_ALL/自run STOP/LOCKなし -> stop=false。
- 反証(regression `test_13`): 同じNOTICEは (i)対象run=`run_e2e_01`に対しては適用、(ii)Melos自身の管理IDで判定すれば適用、と出る。= 別runのM1にだけ非適用で、Melos本体の停止は弱まらない。
- 非適用の根拠は「別ID」ではなく「旧書式で対象run明示限定+全体宣言なし+見出し/ファイル名ID一致」という証拠。仮にNOTICEが将来「全run」等を宣言する追記を受けると自動的に適用に戻る(fail-closed)。

## 3. 権限classifier拒否の記録と、今回の承認で解消する範囲
| 委任 | 拒否された操作 | 表示 |
|---|---|---|
| ASR-M1 委任_03 | runnerのSTOP globを狭める変更(`docs/pm/delegation_log/*STOP_NOTICE*`を他管理IDで除外) | 「Security Weaken」 |
| ASR-M1 委任_04 | `tools/stop_scope_check_01.py`をBash heredocで作成して即実行する1回の呼出 | 「dangerous」(理由表示なし) |
| 本委任_01 | 拒否なし(helperはWriteツール、テスト/runner実行のみBash) | - |
解消範囲(ユーザー承認案aで明確化): 停止判定の**適用範囲規則**(他管理IDの、run限定の旧NOTICEが無関係なrunを機械停止しないこと)。維持=全体STOP_ALL・親scope・自ID宛・parse不能(fail-closed)・既存のRUN_LOCK/RESTART_STORM/自run STOPの検出。**承認範囲外のため変更していない**: STOP_ALL/STOPセンチネル・RESTART_STORM・SDK入口guard(er062)・他runner(er019/er026/062/063/064/065/067/073)の挙動、STOPの解除手段。

## 4. 既存runnerのSTOP_NOTICE解釈(2026-10-14調査、ASR-M1 RESULT_PACKET転記)と整合
| runner | NOTICE解釈 |
|---|---|
| er077 evidence runner(旧) | `*STOP_NOTICE*`を全件停止 -> **本委任でhelperへ切替** |
| er064_kp_int_01-03 | `*KP-INTEGRATED*`のみ |
| er064_kp_noway | KP-NO-WAY + KP-INTEGRATED |
| er064_kp_opt_01_phase2 | `FAMILY-X-KP*` |
| er064_prefetch | 全NOTICE停止 |
| er065 | NOTICE無視 |
| er067 | 読むが無視 |
| er073 | ファイル名にMelos IDを含むものを除外 |
| er026系(er062/063) | センチネル(STOP/STOP_ALL)のみ、NOTICEは見ない |
| er019(Coffee) | コード内にSTOP_NOTICE確認なし。PM_GOVERNANCE 26-2(d)の文書規則のみ(実行層が起動前に確認) |
Coffee(er019)との整合: 26-2(d)は文書上「`docs/pm/delegation_log/*STOP_NOTICE*`の存在確認」であり、案aの適用範囲規則(他IDの限定run旧NOTICEは非適用、全体/親/自ID/parse不能は適用)と矛盾しない。同じhelperを使えば同一解釈になる。**コード統一は本委任では行わない(後続管理ID、OPEN起票)**。

## 5. 本委任で編集したファイル
新規: `tools/stop_scope_check_01.py`、`tools/stop_scope_check_01_test_01.py`。編集: `er077_m1_oov_multi_pronunciation_01_evidence_runner.py`(STOP判定のみhelperへ、`MANAGED_IDS`=M1 ID+本管理ID)。他のSTOP関連コード・センチネル・NOTICEは無編集。
