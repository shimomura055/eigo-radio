# FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_04 要点 (2026-10-28)
J3 = 承認済み仕様内の不具合是正(11-8): R4(_secondary_accept に値等価層なし、CURRENT_SPEC.md:2931乖離)・R3(桁区切り8,900 vs 8900)を値等価層の範囲で是正。新受理クラス/閾値/flag/Family拡大禁止。
安全条件: 負例(凍結負例・N-3・合成負例・値10倍・不規則読み値)で誤PASS増分0を事前登録、API 0評価2回一致。rollback定数(既定True)+監視field。構造変更要なら実装前停止(Opus条件A)。
B: OPEN-515/517/333・DECISION_LOG・新規OPEN(静的監査allowlist EN KP3票drift)・UDR(J1/J2/J4、分類D)・PM_GOVERNANCE 11-8へ1項(過去対策確認1行)。
C: HRページ curl 200/mp3 9本確認。D: docs/pm/RESULT_PACKET_FXMS5.md。
stop_check: docs/pm/delegation_log/2026-10-28_FXMS_stop_check_04.json rc=0。
