# PHASE4_RESULT_04 (ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 委任_08、2026-10-23) 『開いた窓』完成段

Status: **OPEN_WINDOW_FINALIZED_USER_LISTENING_PENDING**(正式Gate PASS、Std/Adv全編組立、試聴ページ差替え済み、page_verify PASS)。API/TTS呼出0、run費用 76.4684円不変。

## 実行
| # | 内容 | 結果 |
|---|---|---|
| 1 | STOP範囲確認 `tools/stop_scope_check_01.py` | rc=3(RUN_STOP+RESTART_STORM_LOCK=Fable解除対象)。STOP_ALLなし |
| 2 | 保全 `run_sf_prod_01` -> `_preserve_20261023_b8/`(git未追跡) | 完了 |
| 3 | `--clear-stop --reason "RESTART_STORM: ... released by Fable 2026-10-23 per PM_GOVERNANCE 26 (委任_08)"` | rc=0、STOP/RESTART_STORM_LOCK.json削除、`audit_stop_sentinel.jsonl` に CLEARED 記録 |
| 4 | `--stages provision_shell,gate,assemble,pages,page_verify`(**1起動**、TTS_EXECUTION_MODE=STANDARD、JST 20:11-20:14) | rc=0。stage時間 provision_shell 1.2s / gate 0.6s / assemble 2.1s / pages 11.0s / page_verify 161.7s。spent_jpy 76.4684(不変) |
ログ: `run_sf_prod_01/console_b8_finalize.txt`、`e2e_stage_log.jsonl`、`page_verify_local.json`。

## Gate結果表(`{a2,b1b}/audit/gate_result_04C.json`)
| 項目 | Std(a2) | Adv(b1b) |
|---|---|---|
| m2_complete | true | true |
| shared_gate | PASS | PASS |
| z_speed_profile v2(33 clip) | 全clip ok(std_narrator_slow6 / std_dialogue_none) | 全clip ok(adv_narrator_none / adv_dialogue_fast6) |
| m1_slowdown | 16 clip全ok | 対象なし |
| audio_text_deviations | 0 | 0 |
| kp_vote_audit | 3/3 evidenceあり(non-blocking) | 3/3 |
| review_lock_state | 全segment RESOLVED | 全segment RESOLVED |
| PASS_WITH_WARNING(要試聴) | 3: part1_c13(SECONDARY_CORROBORATED, Veera)・part1_c14(同, Primary=`Birdie`をAzure=Bertieでcorroborate)・part3_c2(SECONDARY_CONFIRMED, Bertie) | 2: part1_c14(SECONDARY_CORROBORATED)・part3_c2(SECONDARY_CORROBORATED, Primary=`Birdie`) |

## 組立物
| level | path | 長さ |
|---|---|---|
| Std | er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/a2/assembly/Family_Z_the_open_window_a2.wav (+timeline.json) | 313.86秒 |
| Adv | er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/b1b/assembly/Family_Z_the_open_window_b1b.wav (+timeline.json) | 296.93秒 |

## 試聴ページ
`user_test/family_z_open_window_01/` を差替え(index/standard/advanced.html と audio_standard/audio_advanced の全mp3、更新 JST 20:11)。旧版バックアップ=`er026_output/family_z_production_e2e_01/the_open_window/_pages_backup_open_window_pre_b7_20261023`(および`er026_output/family_z_production_e2e_01/_pages_backup_open_window_pre_b5_20261023`)。
URL(push後公開): https://shimomura055.github.io/eigo-radio/user_test/family_z_open_window_01/index.html

## page_verify(`page_verify_local.json`、ローカルserver+実ブラウザ)
user_page_standard_check overall=**PASS**(failed 空)。index 38音声 plays_ok 38 / standard 55音声 plays_ok 55・script行51・seekボタン51・voiceラベル51 / advanced 53音声 plays_ok 53・script行50・seekボタン50・voiceラベル50。全ページ http>=400 0・console_errors 0・file://なし・A2/B1ラベルなし・同一行に音声とスクリプト(l)・全体再生(a)・プレビュー(b)・KP二列(n)・TTSモード明記(k) すべて true。全体再生/個別再生/スクリプト整合=上記のとおり。補足: seek_ok_all=false は既存E2E統合test(er026_family_z_e2e_integration_test_01.py:253)が期待する既存挙動と同じ(ユーザーページ基準判定はPASS)。

## 最終試聴の確認点(ユーザー)
1. Adv c12 `speciality` の英式/米式の読み
2. c2(full_story_part3_c2 "Bertie, why do you bound?")の Bertie(Std/Adv)
3. c14 の Bertie(Std/Adv)。ASR Primaryは `Birdie` でTier3(Azure)が `Bertie` とcorroborate = PASS_WITH_WARNING のため、実聴確認が必要。
