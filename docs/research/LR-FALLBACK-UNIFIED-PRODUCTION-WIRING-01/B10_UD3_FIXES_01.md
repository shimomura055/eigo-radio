# 委任_15(B10) UD-3違反 D1/D2・D4/D5/D6 修正+再評価+再実走(実費 ¥1.97)

前提: B8_RUNTIME_EVIDENCE_01.md §5(D1〜D5)、D6は委任中の追加指示(月Phase2 Std kp1/kp2で実発生)。D3はB7/B9で修正済み。Style・Prompt・回数・ASR閾値は不変(許可Style集合への既存承認Style登録のみ)。Python=`.venv\Scripts\python.exe`。

## 修正
| ID | 原因 | 修正(file) |
|---|---|---|
| D1 | KP解説③(X/Y/Z共通の単一関数`er019_family_x_audio_production_runner_01.py:1316` `_kp_explanation_unified`)が送る`repro01.MINIMAL_INSTRUCTION_PREFIX`(`er003_v1_repro01_main_generate.py:566`、sha b66d3a74)がer130許可集合に無い(`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`のみ) | `er130_adopted_take_classifier_01.py build_allowlist`の`FALLBACK_MINIMAL_EN`へleaf定数importでsha追加。**新Styleの採用ではなく、既に量産経路で送信中の承認済みStyleの登録漏れ是正**。X/Y/Zは同一関数なので同一sha(KP解説③の呼出元は`er019:1282`の1か所のみ) |
| D2 | Z会話ctx→legacy_fallback(③)はfinal_adoptionが`sent_style_sha`を持たず(`how=final_adoption`)、(a)分類核が`STYLE_RECORD_MISSING`、(b)`style_actual`はctx shaによる推定のため`Z_DIALOGUE_STYLE_ACTUAL_MISMATCH` | (a)`er130 dialogue_legacy_fallback_direct`: `dialogue_tts`の直接記録(final_mode==legacy_fallback・policy!=legacy・final_attempt_n==採用take ordinal・該当attemptがmode=legacy_fallbackかつverified)が揃う場合のみkind確定(`ctx.dialogue_legacy_direct`)。(b)`override_violations(replaced_when_fallback=Z_REPLACED_WHEN_FALLBACK)`: 分類核が正常Fallback(非BLOCK)かつtake kindがFallback系のときだけ`Z_DIALOGUE_STYLE_ACTUAL_MISMATCH`を置換(`er063_family_z_audio_01.py:2197`)。記録欠落・未承認・通常takeは従来どおりBLOCK |
| D4 | `er129._lr_info`がresume形の`lr_selection_audit_restored`(`er127:812`)を読まず「理由: 記録なし」 | `er129_lr_display_reflection_01.py _lr_info`: selection/candidate_genに理由が無いときのみ`lr_selection_audit_restored.selected.rationale`を採用(書換え文が一致する場合のみ。不一致は従来どおり記録なし) |
| D5 | `er131.check_page_fhr_contamination`が試聴ページの赤+濃青(`fhr_color_pair`)・注記文言を混入と判定(USER_02 §4と矛盾) | `fhr_color_pair`規則を**撤去**。試聴ページ注記ブロック`div.rpt-notes`(er133 `CLASS_NOTES`)を除外して従来のトークン検査(`fhr-`接頭辞・FINAL_HUMAN_REPORTマーカー・内部コード・注記文言・Style名)を維持=注記ブロック外への混入はNG |
| D6 | `er130.adopted_asr_state`が`asr_judgement`のみ参照。Master Audio Store再利用時はrunner(`er019:1124 _mark_asr_judgement_inherited`)が`asr_judgement_inherited`へ改名するためstore_reuse takeが`ASR_RECORD_MISSING`でBLOCK(B-wire回帰) | `adopted_asr_state`: `asr_judgement`が無く`asr_judgement_inherited.state`がある場合のみそのstateを返す。stateなし・記録欠落は従来どおり(None,None)=MISSING |

## test(追加)
er130: D1(allowlist/KP_EXPL通過/未承認sha・slot・記録欠落はBLOCK)・D2(直接記録PASS、記録なし/ctx/ordinal不一致/未verified/mode不一致/policy=legacyはBLOCK、override置換は正常Fallbackのみ)・D6(inherited state読取・優先順位・stateなし/FAIL)・driftテスト更新。er129: D4(復元根拠読取・不一致は不採用)。er131: D5(試聴ページ表示PASS・注記ブロック外混入/専用語/マーカーはNG)、旧`fhr_color_pair`のassertを新仕様へ更新。
結果: er129/er130(+mock E2E)/er131/er132/er133/er127_final_adoption/er063_style_actual_gate=252 PASS。広域(er019_fx wiring・kp_structure・flash_lite/variable role style・er063 audio/common_style/fz_ctx/speed_v2/std_chunk/narrator_voice・er121 runner/style_profile/hr_guard/hr_adopt・er127 block policy)=下記2件を除き全PASS(259+232)。除外/既存失敗: `er063_fz_ctx_wiring_test_01::test_w11b_...`(HEADでも`_narrator_inner`差で失敗、本件無関係)・`er063_family_z_audio_01_test_01::WiringTest::test_preview_comment_kp_styles`(B9記載の既存失敗)。

## 保存run読取再評価(API 0、HEAD+本修正、`B8_evidence_01/B10_audit_diff_{X,Y,Z}.json`・`B10_read_reeval_01.json`)
- 旧PASS→新BLOCK(厳格化): **X0/Y0/Z0**。(D6修正前は他workerの月Phase2進行中run `moon_shrinking__run_reselect_01` a2のstore_reuse kp1_en/kp2_enが新BLOCK=ASR_RECORD_MISSING 2件だったが、D6修正後に0)
- 旧BLOCK→新PASS: X4(AI島a2/b1b k2 LR・B8 X-Adv-14b preview・**B8 X-Adv-7 kp1_explanation=D1**)・Y3・Z2(B8 Z-Adv-6 KP_EN・**B8 Z-Std-2会話=D2**)。D1該当1件・D2該当1件がBLOCK→PASS。
- store_reuse(`asr_judgement_inherited.state`を持ち`asr_judgement`が無いentry): X保存run 391 entry(23 run)。うちイベント(LR/Fallback)clipでGate評価対象に入るのは月run_reselect_01 kp1_en/kp2_enの2件(BLOCK→PASS)、その他はイベントclipでなくGate置換対象外=不変。

## 再実走(有料、`run_b10_01.py`=run_b8_01.pyのcase id接頭辞のみ`B10-`。driver=`tru_ev_run_01.run_case`・既定profile・STANDARD、見積¥2.0(B8実績0.66+1.34)・Cap¥6・全起動前`stop_check_{x_b10_x_adv_7,z_b10_z_std_2}.json` rc=0)
実費: B10-X-Adv-7 ¥0.681 / B10-Z-Std-2 ¥1.287 = **¥1.968**(`evidence_runs/B10-*.json`)。例外0・hrq_rows 0・停止なし・再起動なし。
| case | 発火 | ledger | Gate(保存run読取、`B10_rerun_reeval_01.json`) | 三者一致 | 最終Human報告 | 混入 |
|---|---|---|---|---|---|---|
| B10-X-Adv-7(X Adv KP解説) | Fallback(③) | FB USED | **kp1_explanation=FALLBACK_APPLIED(通過)**(旧B8=BLOCK) | OK | 濃青(fb=1・consistent) | 0 |
| B10-Z-Std-2(Z Std会話ctx→legacy) | Fallback(③) | FB USED | **full_story_part1_c13=FALLBACK_APPLIED(通過、block {})**(旧B8=BLOCK) | OK | 濃青(fb=1・consistent) | 0 |
注: driver内蔵の`gate_observation`は1segmentだけの部分results向けの暫定観測(`NO_SEGMENT_RECORD`・`Z_STYLE_COVERAGE_EMPTY`・ledgerなし)で、B8でも同様。判定は保存run読取(実Gate関数+台帳)で行った。実ASRの自然な逸脱なくX-Adv-7は計画どおり①②NG→③採用。

## 残存・新規OPEN
- D5後も`scan_public_html(user_test)`は`family_x_ai_island_form_01_candidate_b7_01/index.html`の1件が`LR_REWRITTEN`(ASR警告コードを列挙する既存の事後試聴リスト由来、未公開候補)でhit。分類=**実害なし**(er131検査は未配線・候補ページ非公開。本委任範囲外)。
- Z会話ctx再試行ログ`style_actual`(推定)とlegacy_fallback採用の食い違いは正常として置換済み。`style_actual`自体の推定精度改善は未着手(実害なし)。
- 判断候補(ユーザー)=なし。
