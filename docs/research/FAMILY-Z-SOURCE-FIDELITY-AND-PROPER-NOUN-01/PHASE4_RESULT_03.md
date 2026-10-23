# PHASE4_RESULT_03 (ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 委任_07、2026-10-23) 『開いた窓』c14再生成

Status: **C14_REGENERATED_OK / GATE_ASSEMBLE_PAGES_BLOCKED_BY_RESTART_STORM_STOP**(公開ページ user_test/family_z_open_window_01 は従来のまま。差替えは未実施)。
根拠: OPEN-479をX/Z scope限定で修正(Fable承認)。c14 x2を approve_regenerate(根拠=ASRQ USER_02 §1-B/§3・Fable承認・委任_07)。保全=`run_sf_prod_01_preserve_20261023_b7/`・旧ページ=`_pages_backup_open_window_pre_b7_20261023/`(いずれもgit未追跡)。

## 実行
| # | 内容 | 結果 |
|---|---|---|
| 1 | `--stages tts_b1b,tts_a2 --only-clips full_story_part1_c14`(JST 19:58-20:01、TTS_EXECUTION_MODE=STANDARD) | rc=0。a2/b1b とも c14 = OK(attempt 1)。run費用 71.41->76.47円(+5.06円)。再起動0 |
| 2 | `--stages gate,assemble,pages,page_verify` | rc=2: `FamilyZTtsResultsIncompleteStop`(shell clip entry欠落=provision_shell未実行)。API 0 |
| 3 | `--stages provision_shell,gate,...` | rc=3: **RESTART_STORM sentinel**(5分内3起動: #1含む。#2が自行の誤り)。`<run>/STOP`作成。**削除せず停止**。解除=`--clear-stop --reason`はFable判断 |

## c14 x2 の受理(OPEN-479修正後、clip別)
| level | 結果 | judge | basis | HR |
|---|---|---|---|---|
| a2 | OK attempt 1, ASR `...sang, Birdie, why do you bound?...` | role=**FULL_STORY**、segment_id=full_story_part1_c14、adapter layers=[tier3]、PASS_WITH_WARNING `SECONDARY_CORROBORATED`(Azure real call 1) | Tier3 entity_only(Azureが`Bertie`でcorroborate)。PNAP/RET/Ledgerは評価に到達せず | 0 |
| b1b | OK attempt 1(tts_generations_used 2)、同上 | 同上 | 同上 | 0 |
修正前=両level 3 attempt x2 NG_BOTH->HR Lock(累計6 TTS、`ROLE_NOT_APPLICABLE`)。

## 隔離Z会話経路evidence(`er103_output/ret_prod_z_evidence_01/z_ret_evidence_01.py B`、保全コピーの誤読wav入力、Ledger空)
修正後: status OK、role=FULL_STORY、PASS_WITH_WARNING(Tier3)、HR 0、実体表 Bertie person/confirmed(NER 2 call、約0.01円)、`pronunciation_alarm_eval=null`(Tier3が先に受理)。修正前(`z_ret_evidence_caseB_result_before_open479_fix.json`)=3 attempt NG_BOTH->HR、ROLE_NOT_APPLICABLE。
所見: 会話経路でPNAP/RETが**実受理に寄与する場面は今回観測されず**(Tier3が先に受理)。経路が通ること(role解決・適用可能)はtestと実runで確認。

## ユーザー最終試聴の確認点(完成後)
(1) Adv c12 `speciality` の英式/米式の読み、(2) c2 の Bertie、(3) c14 の Bertie(a2/b1b)。
