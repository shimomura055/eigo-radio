# VALIDATION_WIRING_04: KGCPW 委任_04 Family Z 正式CLI runtime evidence(2026-10-15)
Status: **Z_EVIDENCE_PARTIAL_STOPPED_AT_ADV_AUDIO_HR**(PRODUCTION_WIRED未宣言)。run=`er026_output/family_z_production_e2e_01/melos/run_kgcpw_z_e2e_01`。evidence=`evidence/E11_z_e2e/`。

## §0 超サマリ
- E11a(Z 正式CLI `--stage kp` 実LLM、自然): a2/b1b とも NO_TARGETS(JPY1.978)。Z自然発火は今回も未観測。
- E11b(注入HR、正式`main()`をin-process駆動し`_kp_fn_for_ctx`のみ差替): `FamilyZE2EStop ...HUMAN_REVIEW_REQUIRED(a2): rank=[2]`、rc=2、API 0(cost_log行数不変7)、HR報告書json+md・`gloss_alignment_human_review_events.json`・stdout最終行あり。
- E11c(正式CLI `--stage tts_a2`): `FamilyZE2EStop ... (TTS/Gate/Assemblyへ進まない)` rc=2、cost_log行数不変(API 0)。
- E11d(`resolve_gloss`→正式CLI `--stage kp --regenerate-stage kp_a2`): rc=0、API 0、`gloss_alignment_pending_result.consumed.json`、a2 TTSでrank2 ja=『人を引きずり込む』(resolve値)が音声入力・ASRに反映。
- E11e(E2E完成): **未完**。a2 TTS 29 clip全OK(JPY18.5)。b1b TTSは既存の音声Human Review Lock(kp1_en/kp3_en=TRUE_CONTENT_MISMATCH/TTS_FAILURE 2回失敗、full_story_part1_c5=ASR_VALIDATION_UNCERTAIN『Melos said.』→『Nello said.』)でrc=2停止。`approve_regenerate`はユーザー明示承認が必要な既存安全装置のため回避せず停止。gate/assemble/pages/page_verifyは未実行。
- 費用実測 JPY38.74(openai 2.42/gemini 20.36/asr 4.21/azure 11.74)。Guardrail 80の48%。

## §1 Z evidence表
| ID | 内容 | provenance | 観測 |
|---|---|---|---|
| E11a | `--stage kp --approved-budget-jpy 10` 実LLM | fresh+production_formal_path | rc=0 220秒 JPY1.978 NO_TARGETS(a2/b1b)、flag source=default enabled |
| E11b | `evidence/E11_z_e2e/inject_z_a2_cli.py --story melos ... --stage kp --regenerate-stage kp_a2` | synthetic(selection=自然a2 mergedのrank2を対象化+align fail2)+production_formal_path(main/build_real_context/_launch_guard/stage_kp/_gloss_hr_gate) | rc=2、`[STOP] FamilyZE2EStop: FAMILY_Z_KP_GLOSS_ALIGNMENT_HUMAN_REVIEW_REQUIRED(a2): rank=[2] ...`、最終行`[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED] ... (ユーザーへ必ず報告してください)`、`evidence/E11_z_e2e/hr_a2/` |
| E11c | `--stage tts_a2 --approved-budget-jpy 45` | production_formal_path | rc=2、`FamilyZE2EStop ...(TTS/Gate/Assemblyへ進まない。resolve_gloss後に再実行)`、API 0 |
| E11d | resolve_gloss(rank2,'人を引きずり込む')→`--stage kp --regenerate-stage kp_a2` | human gloss+production_formal_path | rc=0、API 0、`.consumed.json`、spent不変1.9781 |
| E11e | tts_a2 rc=0 JPY18.48 / tts_b1b rc=2 | fresh+production_formal_path | 上記。a2 29/29 OK(narrator style N01記録`audit/narrator_style_record.json`=旧guard不発) |

## §2 10条件表(Z列の更新)
- 条件1(Z): 自然発火は未観測のまま。ただしZ正式`stage_kp`/`main()`の実ctxでalign失敗→HR経路が発火(注入)=**注入では確認済み**。
- 条件4: Z正式CLIのHR停止(stage_kp停止+後続`--stage tts_a2`停止、API 0)は**確認済み**。Z E2E完成(gate/assemble/pages)は**未確認**(Adv音声HRで停止)。Z自然発火は未確認。
- 条件6(Z): 再開(snapshot復元・選定API 0・.consumed.json・resolve値のTTS反映)は**確認済み**(a2)。Adv(b1b)のgloss HRは未実施。
- 他条件は委任_03の判定から変更なし。

## §3 費用
E11a 1.98(kp)、E11b〜d 0、tts_a2 18.48、tts_b1b(停止まで)約18.3、計38.74。見積(実行前): writer〜support再利用=0(provenance sha一致を確認)、残≈TTS 2レベル≈40。

## §4 provenance区別
実LLM自然=E11a、失敗注入=E11b(selection入力は自然a2の加工=synthetic)、実TTS(正式CLI)=tts_a2/tts_b1b。writer/std_adjust/plan/support成果物は`run_e2e_02`から再利用(copy、費用0)。narrator clipを含む全TTS clipは新規生成。

## §5 想定外・逸脱
1. tts_b1b rc=2: 既存音声HR Lock(上記3 clip)。回避せず停止。解除=`er011_human_review_lock_01.approve_regenerate`(ユーザー明示承認)後に`--only-clips`再実行が必要(約JPY1〜2/clip、cooldown10分)。
2. 起動時刻16:42:46と16:42:58の2回が12秒差(同一300秒窓で2回、閾値3未満)。以降は全て5分以上空けた。
3. `--stage all --stop-after support`の初回は`--approved-budget-jpy 3`でest guard(WARN_THRESHOLD)により課金前停止(書込0)→25で再実行し再利用0円。
4. kp_expl_b1bはkp stage内でb1b KP不変のため再利用(別stage起動不要)。
