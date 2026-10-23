# PHASE4_RESULT_02 (ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 委任_05 B工程、2026-10-23) 『開いた窓』再開結果

Status: **B_STAGE_BLOCKED_AT_BERTIE_C14**(Bertie 4clipのうち2clip=OK、2clip=HR Lock。gate/assemble/pages/page_verifyは未実行。ユーザー試聴ページは未更新=従来のuser_test/family_z_open_window_01のまま)。
原文根拠: 解除は `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md` §1-B/§3(Fable approve_regenerate、委任文=同_委任_05.md)。run=`er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01`、`TTS_EXECUTION_MODE=STANDARD`。

## 保全
`run_sf_prod_01_preserve_20261023/`(a2/b1b audit全体、対象3clipのwav、writer/provenance.json、local_rewrite_recovery、cost_log、voice_assignment、全narration wav sha256一覧[before / after_c12])と、公開ページ旧版`_pages_backup_open_window_pre_b5_20261023/`。wavはgit未追跡(*.wav ignore)。`tts_checkpoint.json`は不在を確認。

## 実行(再起動は1回のみ使用)
| # | 内容 | 結果 |
|---|---|---|
| 1 | `--stages tts_b1b,tts_a2 --only-clips full_story_part1_c14,full_story_part3_c2`(4clipを`approve_regenerate`済み) | rc=2: b1b c14=STOPPED(3 attempt全て Primary `Birdie`)で停止。b1b c2=OK。a2は未到達 |
| 2 | `--stages tts_a2 --only-clips …`(上記停止後の再起動1回) | rc=2: a2 c14=STOPPED、a2 c2=OK |
| 3 | `--stages tts_b1b --only-clips full_story_part3_c12`(reuse_blocked印付与後、UKUS Z手順) | rc=0: c12 OK(attempt 1、下記) |

## 4clipの結果(Bertie)
| clip | 結果 | 受理basis |
|---|---|---|
| a2 full_story_part3_c2 | OK(PASS_WITH_WARNING `secondary_confirmed`、Primary `Birdie`・Azure `Bertie`) | Secondary(Azure)一致。RET/Ledger寄与なし |
| b1b full_story_part3_c2 | OK(PASS_WITH_WARNING、Primary `Birdie`、`SECONDARY_ASR_CORROBORATED_MATCH`/`SECONDARY_CORROBORATED`) | Secondary corroborated。RET/Ledger寄与なし |
| a2 full_story_part1_c14 | **STOPPED/HR Lock**(3 attempt全てNG_BOTH、累計TTS 6) | `pronunciation_alarm_eval=ROLE_NOT_APPLICABLE(role=None)` |
| b1b full_story_part1_c14 | **STOPPED/HR Lock**(同上) | 同上 |
→ 4clipは「勝手にRET受理」されていない。c2はSecondary一致のPASS_WITH_WARNING(listening_listに載る、最終試聴で`Bertie`と聞こえるか確認対象)。c14はRET以前にPNAPが適用されないため止まる(下記)。

## 根本原因(c14 HR Lockの真因、Production不具合候補)
- 旧PHASE4_RESULT_01の診断(`NO_PROPER_NOUN_EVIDENCE`)はオフライン再現であり、実runのjudgementは当初から`pronunciation_alarm_eval.reason=ROLE_NOT_APPLICABLE, detail.role=None`(preserve保全版のa2/b1b review_lock_state.jsonで確認)。
- 経路: `er063_family_z_audio_01.real_generators.dialogue` → `er012_b_family_voices_production_01.generate_voice_body_wide_margin` が `secondary_asr.evaluate_attempt_with_cascade(...)`(er012_b:553)を **`segment_id=`なしで呼ぶ** → `er006_secondary_asr_01.py:1181`の`judge_role=resolve_narrative_role(segment_id)`が`None` → `er103_proper_noun_alarm_policy_01.py:336` `role not in APPLICABLE_ROLES` で `ROLE_NOT_APPLICABLE`。Narrator生成器(`news_tail_fix.generate_news_narration_wide_margin`、er003_v1_sing01_news_tail_fix.py:205-213)は`derive_segment_key(out_path)`で`segment_id`を渡すため役割=FULL_STORYで正しく動く。
- したがって**Zの会話(dialogue)clip[`generate_voice_body_wide_margin`を使う経路]ではPNAP(固有名詞発音アラーム受理)・RETのどちらも一切発火しない**(Bertieは会話文中の人名)。同じ欠落で`judge_role`によるTier1/5role等の役割ゲートも会話では無効(要確認)。承認済み仕様(PNAP/RETをX/Zの正式経路で有効)との矛盾=不具合(PM_GOVERNANCE 11-8)。本委任はProduction code変更禁止のため**修正せずFableへ**。
- 隔離Z再現(同一wav・同一RET表・Ledger空、`er103_output/ret_prod_z_evidence_01/`): narrator生成器=ENTITY_ONLY_ACCEPT(`entity_table:confirmed:person`、HR 0)/dialogue生成器=3 attempt NG_BOTH→HR(`ROLE_NOT_APPLICABLE`)。

## c12(UKUS Z evidence、Adv)
`reuse_blocked`印→原稿どおり`speciality`で再生成: attempt 1でPASS。ASR=`...Vera's specialty.`、`orthographic_equivalence.version=er109_orthographic_equivalence_v2_ukus01`、`scope=Z`、`rules=['ukus_spelling_variant']`、`ukus_pairs=[speciality/specialty, T1, varcon, both, pron_differs=true]`、`ukus_table_sha256=c5598eb6…2dee`、audio_text_deviation なし、LR/cooldown/HR 0。wav sha 19812cbe(forte版)→b054321b。累積カウンタ4→5(上限15)。他clipのsha差分=Bertie c2/c14のみ(c12以外の無関係clip不変、`narration_sha256_{before,after_c12}.txt`)。`writer/provenance.json`の`audio_text_deviations`(forte記録)は削除せず`superseded`注記を追記。

## 未実施(blocker解消後)
gate(speed v2含む)→assemble(Std/Adv)→pages→page_verify。c14 2clipがOKになるまで`assert_tts_results_complete`で進めない(迂回しない)。ユーザー最終試聴の確認点(完成後): (1) c12 `speciality`の英式/米式の読み(`pron_differs=true`)、(2) c2(Bertie)の読み、(3) c14のBertie。
費用: run_sf_prod_01の追加分 9.46円(61.95→71.41、make_real_spent_fn)、隔離RET Z evidence 1.16円。詳細は`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/B_STAGE_RESULT_01.md`。
