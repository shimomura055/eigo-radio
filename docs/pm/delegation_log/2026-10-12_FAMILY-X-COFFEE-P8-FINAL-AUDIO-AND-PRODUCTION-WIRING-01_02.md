# FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_02(2026-10-12、課金JPY0)

Status: 実装・test・Regression・dry-run完了。**runtime evidence(実TTS)未実行、`PRODUCTION_WIRED`未達**。

## 1. M1〜M6 / S1〜S6 反映結果
設計書v02 `docs/pm/design/2026-10-12_COFFEE-P8-PRODUCTION-WIRING-DESIGN-02.md` に全て反映。
| ID | 反映 | 実装/test |
|---|---|---|
| M1 | Local Rewrite回復・minimal_fallbackは非P8(共有module不変)、経路表訂正、既存の穴をOPEN-312起票 | M3 Gateで捕捉(test: `LOCAL_REWRITE_RECOVERY`/`ADV_MINIMAL_FALLBACK`/`STD_FALLBACK_USED_OR_UNKNOWN`) |
| M2 | coffee_p8は新out_dirのみ。3 file(top/a2/b1b audit)のいずれか存在でSTOP、記録を作らない。記録欠落の扱い(default=default/coffee_p8+既存=STOP) | `resolve_run_profile`+test(6パターン+main経由) |
| M3 | Assembly前Gate(runnerの`stage_assemble_family_x_b1/a2`内のみ、`_style_profile_gate_blocked_summary`)。人間承認(text sha一致)でbypass | test: PASS/各BLOCK/承認bypass/stale承認/統合 |
| M4 | segmentごとに`style_base_sha256`(hint追記前)を記録、hintなし=最終sha一致/hintあり=head200一致+cache_hits列挙 | `evaluate_segment_evidence`+test |
| M5 | profile!=defaultでflash-lite以外はSTOP(`--allow-legacy-backend`でも)。main(全stage)と`generate_*`の両方 | test(main経由でout_dir未作成も確認) |
| M6 | PRODUCTION_WIRED表記を「Coffee Full StoryのStyle解決のみ」に限定、`overridden_roles=["FULL_STORY"]`、runtime evidence episodeは01A成果物(v4)を置換しない | 記録/設計書/SSOT |
| S1 | Std逐語+6%減速はCoffee限定例外`COFFEE-P8-STD-VERBATIM-EXCEPTION-01`(コード注記、er003の説明文との差異記載) | test固定(coffee_p8 Std Full Story=減速指示非連結、default/IN_ONE_LINEは従来連結) |
| S2 | plan段階でLedger hit計算(web lookup無効) | dry-run結果参照(hit 0件) |
| S3 | defaultで新key/file無し。mock TTSでb1/a2全segmentの`style_prefix_override`をbaseline commit 776c6b92のrunnerと比較 | test(backend 2種) |
| S4 | rollback手順+coffee_p8 out_dir再利用禁止 | 設計書 |
| S5 | Phase 2申し送り(`_generate_or_reuse_kp`のprofile照合・Master Store `style_instruction_id`分離) | OPEN-313 |
| S6 | runtime evidence費用見積 | `er057_output/coffee_final_audio_assembly_01/RUNTIME_EVIDENCE_COST_ESTIMATE_01.md` |

## 2. 実装概要
- 新: `er019_family_x_style_profile_01.py`、`er019_family_x_style_profile_01_test_01.py`。
- 変更: `er019_family_x_audio_production_runner_01.py`(+108/-10行): import、CLI `--style-profile`(既定None)、b1/a2の`_role_style`/`_role_style_slower`を`resolve_role_style`経由、P8対象segmentへの`style_profile`記録、`run_plan_stage`のS2記録(非defaultのみ)、`_style_profile_gate_blocked_summary`とassemble呼出、mainのM5/M2判定とentry_point記録(非defaultのみ)。
- 不変: 共有module(er003/er006/er011/er020/er033定数)、Master Store、他Family、`FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`。
- 設計上の解釈(ユーザー判断候補): 固定記録の置き場は`<out_dir>/audit/style_profile.json`(out_dir直下。level別でなくrun単位)。M3 GateのStd側は`attempts_log`末尾の`style_prefix` recordも要求(欠落=BLOCK、fail-closed)。人間承認bypassは`asm.record_human_approval`が作る`human_approved_segments.json`のcanonical text sha一致で判定。

## 3. 検証
- 新規test: `er019_family_x_style_profile_01_test_01` 32件 PASS(API 0、全mock)。
- Regression(新規failure 0): er019 audio runner 49、variable_role_style 24、flash_lite_role_style 8、opus_l2_fixes 24、new_structure 31、er003 standard_a2 27、er011 human_review_lock 18、er033 styles 10 / backend_wiring 36 / family_x_wiring_phase1_regression 18。
- dry-run(¥0): `er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_l3_01 --out-dir er019_output/coffee_prices/run_p8_wiring_01 --style-profile coffee_p8 --tts-backend speech_metadata_flash_lite --dry-run` -> a2/b1b plan OK、`audit/style_profile.json`作成(profile_id=coffee_p8、overridden_roles=["FULL_STORY"]、sha=3eadf4f6…e5595)。実TTS/ASR/LLM呼出なし。
- S2 Ledger hit(現行Ledger 37 entries、web lookup無効): a2/b1bとも full_story_part1〜3 で **hit 0件**(P8にhint追記なし)。証跡 `er019_output/coffee_prices/run_p8_wiring_01/plan_run_result.json`。

## 4. runtime evidence費用見積
`er057_output/coffee_final_audio_assembly_01/RUNTIME_EVIDENCE_COST_ESTIMATE_01.md`。実績(Coffee両level tts stage JPY12.34)ベースで通常約JPY10〜15、再生成込み理論上限約JPY30。scaffoldは明示コピー(JPY0)。

## 5. Wiring Checklist
実装済み: 案2実装、初回経路(mock)、resume、fallback/LR扱い(M3)、Std逐語+6%、他記事非影響(default同一性)、SSOT。
未実行: 実TTSでのsha一致(初回/retry/regen)、Audio Validation Gate/ASR/duration(P8で既存閾値)、runtime evidence run、Production採用(人間のみ)。

## 6. ユーザー判断候補
1. runtime evidence run(新out_dir・両level全segment+KP)の実行可否と費用(見積約JPY10〜15/上限約JPY30、`--level`分割推奨)。
2. M3解釈: LR回復・fallbackしたP8対象segmentは人間承認なしにAssemblyをBLOCKする運用でよいか(厳格だが、既存の穴OPEN-312が表面化する可能性)。
3. OPEN-312(Family X Adv Local Rewriteでrole styleが落ちる既存の穴)の是正方針(共有module改変を伴うためFamily X全体の判断)。
