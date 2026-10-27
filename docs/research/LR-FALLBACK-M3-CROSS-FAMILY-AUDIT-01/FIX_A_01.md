# FIX_A_01: 分類A是正3件(LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01 委任_05、2026-10-27、API 0)

根拠: W2_SIX_ROUTES_01.md §5 F1/F2・§6 P1/P2、W1_LR_DATAFLOW_01.md F-3、W3_M3_LR_HR_01.md J-3。Gate判定・HR Lock・音声・resume正当性・Prompt・閾値は不変。

## 変更点
| # | 修正 | file:line(変更後) | 内容 |
|---|---|---|---|
| F1a | `lr_recover`入口で未closeの③を閉じる | `er127_tts_block_policy_01.py:645-649` | `blk._open_ordinal`が残っていれば`blk.done(…, False)`。③NGでLRに入る以上、後続`finish`で③が`verified:true`に化けない |
| F1b | `BlockProgress._write`をdepth別merge書込に | 同`:259`(`_touched`)・`:277-284`・`:322`(`_block`でtouched記録) | 自instanceが触れたdepthは自分のin-memory、触れていないdepthはfileの最新を採用。depth0のfinish_attempt/_writeがdepth1(LR block)記録を上書きで消さない。根本原因=depth0 stateの`finish_attempt→_write`がmark_done(委任_04のmerge)より前にfileを古いin-memoryで上書きしていた |
| F2 | 減速後最終judgeへscript_version伝播 | `er003_v1_n3_01_tts_generate.py:125-126,149,152`(引数`script_version="v0"`追加)・`:223,229,255-258` | 明示LR block(`lock_text!=tts_input_text`分岐)のときだけ`script_version="v1"`→統一judgeが`LR_REWRITTEN`を付与(PASS→PASS_WITH_WARNING)。PASS/NG判定は不変。旧外側ループ経路(A/B/C scope外、golden byte同一)は`v0`のまま |
| OPEN-564 | `_merge`の`fallback_used`を採用attempt種別に従わせる | `er003_v1_crosslevel_audio_02_common.py:477-480` | `res["fallback_used"]=bool(res.get("fallback_used"))`(①'/②'採用=False、③'採用=True)。M3/Y gateは`local_rewrite_recovery`で別途BLOCKするので結果不変 |

旧外側ループの`resolved["fallback_used"]=True`(同ファイル:627)は③相当のminimal instruction再TTSなので正しく、変更なし。

## test(追加分)
- `er127_tts_block_policy_01_test_01.py`: `test_real_lr_path_third_open_then_lr_block_then_finish_keeps_records`(実LR経路: ③未close→lr_recover→LR block→finish→`blocks["0"]`③verified:false・`blocks["1"]`①'記録が残る。修正前コードでFAILすることを確認)、`test_write_keeps_other_depth_block_when_not_touched`(同じく修正前FAIL確認)、`test_lr_success_fallback_used_follows_adopted_attempt_open564`(L3: ①'採用=False/③'採用=True、local_rewrite_recovery常時付与)。既存`test_mark_done_keeps_depth1_lr_block_record`は維持(追加で実経路版を補完)。
- `er019_family_x_style_profile_01_test_01.py`: `test_lr_adoption_blocks_even_when_fallback_used_false_open564`(LR+fallback_used=Falseでもb1b/a2ともBLOCK、LOCAL_REWRITE_RECOVERYのみ、Gate不変)。
- `er008_n8_a2_slowdown_sha256_refresh_22_test_01.py`: `SlowdownJudgeLrRewrittenWarningTests`(LR block attemptの`asr_judgement.warnings`に`LR_REWRITTEN`・state=PASS_WITH_WARNING・status OK / LRなしは警告なし / script_version既定v0)。

## 実行結果(`.venv\Scripts\python.exe -m pytest`)
- 主要: er127(golden含む104件)+er019_family_x_style_profile(51件)+er008_n8 slowdown(7件)=162 passed、失敗0。golden(A/B/C byte同一)PASS。初回、F2を`_expected_source`基準にしたとき`test_golden_n3_l4`がFAILしたため、明示LR block分岐のみに限定して解消(A/B/C出力不変を維持)。
- 関連全体(変更3moduleを参照する89 test file、er020*/er121 style/er078 backcompat/er117/er003_lr_post_rewrite含む): 2282 passed / 9 failed / 2 skipped。9 failedは本変更起因でない:
  - er006_kp5_canonical_bug_01_test.py 4件(日本語tilde処理。未変更module)
  - er020_tts_retry_local_rewrite_fullseg_test_01 `test_recorded_candidates`(`er011_output/local_rewrite_recovery/...b1b/..`保存データの欠落=git status上のD。既存失敗)
  - er109_xz_isolation_01_test_01 2件(er118_fz_*/er122_fz_ctx_fakes_01/er121_e1_*のimport list差。本修正3fileとは無関係)
  - er078_asr_unified_wiring_05 `test_hr_lock_module_unchanged…`(`er011_human_review_lock_01.py`の作業ツリー差分。本委任で未変更)
  - er019_family_x_pointless_01 `test_family_a_files_have_no_working_tree_diff`: `er003_v1_n3_01_tts_generate.py`が「未コミット差分なし」を要求するFamily Aファイル一覧に含まれるため、commit前の差分で失敗(commit後は解消する性質。内容はA/B/C出力不変=golden PASS)。
  OPEN-543管理の既存失敗との完全な同一性はbaseline再実行していない(本変更前後の同一run比較は未実施)。上記は失敗内容が変更3fileに触れないことで判断。

## 影響範囲(X/Y/Z 6経路)
| 経路 | F1 | F2 | OPEN-564 |
|---|---|---|---|
| X Std(A2) L4/L3 | 効く(er127共通) | 効く(L4 hook、LR block内のみ) | 効く(`_merge`) |
| X Adv(B1) | 効く | 該当なし(減速なし) | 該当なし |
| Y Std/Adv | 効く | Std L4のみ | Std(unified)のみ |
| Z Std/Adv(chunk) | 効く | Std本文L4相当のみ | 該当なし(Zは別merge) |
| A/B/C(scope外) | 変更なし(golden PASS) | 変更なし(v0維持) | 変更なし |

## Dangling/旧記述Grep
- `script_version.*v0`は`_post_slowdown_unified_judge`既定値のみ(旧固定は撤去)。`res["fallback_used"] = True`の無条件代入は`_merge`から撤去、残存(:627旧外側ループ)は意図どおり。

## 未観測(実証済みと書かない)
- 実LR自然発生runでの`tts_block_progress`の`blocks["1"]`保全、Std LR採用の`pass_with_warning_listening_list.json`への`LR_REWRITTEN`掲載、`fallback_used`値の実測は、API 0のため未観測(fake/単体・結合testまで)。次回のLR自然発生runで採取する。
- AI島a2保存データ・過去run保存データは書き換えていない。
