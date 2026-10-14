# 委任_01 STOP-NOTICE-SCOPE-RULE-PRODUCTION-01(2026-10-14、要点保存。§0・§1逐語)

新管理ID。ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 委任_04がSonnet上限到達かつ権限classifier拒否で中断したため、STOP_NOTICE適用範囲規則(ユーザー2026-10-14承認・案a)を独立管理IDで実装し、そのruntime evidenceとしてM1 evidence runを実施する。並行: Coffee 委任_04(er019系)・Family Z 委任_03(er076系)・Day 1棚卸(docs/research)。領域分離厳守。

## 0. ユーザー正式判断(2026-10-14、逐語)
「M1 evidence runnerについて、ユーザーは**案aを正式承認**した。停止判定を以下の適用範囲に整理する。
- 当該管理IDに有効なSTOP_NOTICE
- 共通のSTOP／STOP_ALL等の全体停止条件
- 既存の安全機構が定めるその他の有効な停止条件
別管理IDの過去のSTOP_NOTICEが、無関係なrunを機械的に停止させないようにする。ただし、**単純な管理ID文字列一致によって安全停止を迂回してよいという承認ではない。** 実施前に通知の発行主体・対象範囲・有効性を確認し、次の条件を守ること。
1. 有効な全体STOP、親スコープSTOP、安全停止を引き続き検出する。
2. 旧Melos STOP_NOTICEが現在のM1に本当に非適用であることを証拠で確認する。
3. 別IDだが本当に適用すべきSTOPを見逃さない。
4. Coffee側とM1側でSTOP解釈が一致するよう、共通の適用範囲規則を確認する。
5. 正常系・異常系のRegressionを実施し、既存停止機構を弱めない。
6. 正式runnerでの動作証拠を確認する。
7. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitを適切に更新する。
安全classifierが以前拒否した理由も確認し、拒否理由が今回の承認によって解消される範囲を明確にすること。**承認された適用範囲を超える安全機構の変更は行わず、必要ならSTOPして報告する。** 本件のStatusは`APPROVED_FOR_PRODUCTION`。必要なProduction配線・テスト・runtime evidenceが揃うまでは`PRODUCTION_WIRED`にしない。」

## 1. 前回中断の経緯と本委任での扱い(重要、逐語)
- M1 委任_04は、`tools/stop_scope_check_01.py`を**Bashのheredocで書いて即実行する1回の呼出**が権限classifierに「dangerous」(理由表示なし)で拒否され、指示どおり別手段を試さず中断した(設計案・調査結果は`docs/pm/RESULT_PACKET_M1OOV.md`末尾に保存済み)。
- 本委任では、ファイルの作成・編集は**WriteツールとEditツール**(通常経路)で行い、Bashは`pytest`/runner実行等の実行専用に使う。heredocによるファイル生成は使わない。
- これは権限判断の迂回ではない: 各操作は引き続き権限システムの審査を受ける。**もし再び拒否されたら、その操作内容(ファイル名・コマンド)と表示理由を記録し、別手段を試さず即STOPしてFableへ報告する**。STOPセンチネル・STOP_NOTICEの編集/削除/作成は一切行わない(helperは読取専用)。

## 要点(§2-§3)
2-1 helper(判定順: STOP_ALL→自run STOP→NOTICE各件parse[自ID/scope/status/期限/旧書式fail-closed]→RESTART_STORM/RUN_LOCK)。2-2 `STOP_SCOPE_RULE_01.md`。2-3 er077 runnerのみhelper切替(他runnerは編集しない)。2-4 9系統Regression+既存(er006 M1 68/配線22/F1 13)。2-5 evidence run(<=JPY5)。2-6 SSOT/UDR #52-55/Checklist。固定: E-1 Write/Edit、D-1 er019/er076/Coffee run dir/docs/research無接触・STOP編集禁止、G-1 明示add・secret_scan・trailer `Managed-ID: STOP-NOTICE-SCOPE-RULE-PRODUCTION-01`、F-1 JPY5。
