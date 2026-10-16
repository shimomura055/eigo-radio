# CLOSEOUT_PLAN_07: AUW Gate 3/4/7チェックリスト・Dangling Reference表・merge計画・15条件最終表

管理ID: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_07(2026-10-16)。性質: Closeout準備。**mainへのmergeは行わない(ユーザーGo待ち=USER_DECISION_REGISTER #87)**。`PRODUCTION_WIRED`は宣言しない。有料API: narrator A2外側ループ実音声の途中終了分 約JPY 0.57のみ。関連=`REVERT_REHEARSAL_07.md`、`RUNTIME_EVIDENCE_06.md`§15、`CURRENT_SPEC.md`「統一ASR判定仕様」節。

## 0. 当初目的(ユーザー原文の逐語。`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md` L201〜L215・L217)
1. ユーザー承認済みのASR判定仕様と実際のProduction動作が一致。 2. 日本語・英語、すべてのProduction音声Sectionに適用。 3. Primary NG→Secondary PASSがWARNING付きで採用される。 4. Primary／Secondary両NGなら最大3回のTTS生成フローが成立。 5. 数値の同値・異値を適切に判定し、否定保護を維持。 6. Connected Speech／M1／F1の既存Regressionに悪化なし。 7. 試聴リストへのWARNING連動が動作。 8. Secondary二重呼び出し・予算超過・無限retryがない。 9. Production正式pathのruntime evidenceがある。 10. 必要なUnit／Regression／Integration testがPASS。 11. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSに実態を反映。 12. 必要なcommit／push／mergeを確認。 13. Dangling Reference Checkで問題なし。 14. 未解決USER_DECISION_REQUIRED・未配線APPROVED項目を明示。 15. Fableがユーザー承認内容・実装・証跡を独立照合。
**「1項目でも未確認であればPRODUCTION_WIREDと報告しない。」**(L217)

## 1. merge計画(ユーザーGo後に実施。本委任では未実施)
前提: ユーザーGo(#87)・Fable独立照合(条件15)完了・STOP通知なし(`tools/stop_scope_check_01.py`のrc=0)。
1. 事前予行(API 0・結果破棄): `git fetch origin` → 最新`origin/main`と本branchの差を確認。mainにAUW以外のcommitが載っていれば別worktreeで`git merge --no-commit --no-ff feat/auw-unified-asr-01`を試し、競合0を確認してから`git merge --abort`。
2. **merge(squash禁止、revert単位=merge commit 1個)**: main worktree(`C:\Users\tensh\eigo-radio-crbn`等、main checkout済みの場所)で
   `git checkout main && git pull --ff-only origin main && git merge --no-ff feat/auw-unified-asr-01 -m "ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01: 統一ASR判定・全Section Production Wiring(main merge、ユーザーGo #87)" && git push origin main`
   競合・エラー時はCLAUDE.mdのGit運用ルールどおりユーザーへ確認(解決せず中止)。
3. merge後に走らせるもの(すべてAPI 0、通信遮断plugin付き):
   - AUW中核12 file(`er058_asr_tts_prodfix_01_test_01.py`、`er063_family_z_audio_01_n01_test_01.py`、`er063_family_z_audio_01_test_01.py`、`er078_*_test_01.py`[en/ja/judge/wiring_05/06c/06d/06e/value_guard/registry]): 期待 **411 passed**。後方互換`er078_asr_unified_backcompat_07_test_01.py`: 期待 **53 passed**。
   - 静的監査`er078_asr_unified_wiring_static_audit_01.py`: 15 passed、かつ`.venv/Scripts/python.exe er078_asr_unified_wiring_static_audit_01.py`の出力が`unlisted_new_calls`/`vanished`/`count_changed`すべて空。
   - flag OFFロールバック経路: `er078_asr_unified_wiring_06c_test_01.py -k test_g` 3 passed。
   - 影響suite per-file(06eの`patch_06e/summary_06e.json`と同形式)を回し、06c baselineの失敗idに無い新規失敗が0であること。
   - smoke(API 0): `er078_auw_runtime_evidence_06e.py tstop|kp4|dlg_cap2`および`er078_auw_runtime_evidence_07.py narr_cap3`を`--execute`**なし**で実行し(dry-run)、`stop_files_present: []`・`shared_state_unchanged: true`を確認。`tools/stop_scope_check_01.py --managed-id ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01`がrc=0。
4. merge後のSSOT: `CURRENT_SPEC.md`の統一ASR判定仕様節のStatusを「merge済み・`PRODUCTION_WIRED`判定はFable」へ更新(別commit、既存行は書換えず追記)。`PRODUCTION_WIRED`宣言は条件1・2・4・9・15の充足後にFable/ユーザーが判断。

## 2. ロールバック手順(Gate 4予行の結果に基づく。`REVERT_REHEARSAL_07.md`)
1. mainで`git revert -m 1 <AUW merge commit hash>`(1コマンド・衝突0を予行確認済み[15 commit単位のrevertでmain相当へ完全復元、`git diff origin/main --name-only`=0 file])。続けて`git push origin main`。
2. revert後に旧test(AUWが変更した18 moduleをimportする83 file)を回し、main時点baselineと同一(予行では1,768 case中差0)であることを確認。
3. 部分ロールバック(判定だけ旧挙動へ): Secondary呼出の無効化は既存のflag OFF経路(`cascade_enabled=False`、`FEATURE_FLAG_SECONDARY_ASR_ENABLED`)で可能(旧leaf挙動を保持、06c `test_g_*`)。ただし旧Cascade(Primary#2/Secondary#2)の再導入ではない。
4. 状態の残渣: revert後も実行時に追記された`er011_output/attempt_history.jsonl`・`er006_output/master_audio_store_01/*`・HR queue等のstateは戻らない(追記専用の履歴。必要なら個別判断)。

## 3. Dangling Reference Check(条件13、Gate 4。撤去対象=`_post_slowdown_cascade_rescue`/Primary#2/Secondary#2/4段尽き`stop_retrying`+HR直行)
コード側の確認: `git grep _post_slowdown_cascade_rescue -- '*.py'`の本番参照は**0**(`er003_v1_n3_01_tts_generate.py:131`のコメント[撤去記録]と、撤去を固定するtest[`er078_asr_unified_wiring_06c_test_01.py:532 assert not hasattr`・同06c他のコメント]、および下記の証跡script 2本のみ)。`PM_GOVERNANCE.md`のGrep(4段階等)は無関係な語のみ(旧機構への言及0)。

| ファイル:行(委任_07開始時) | 内容 | 処置 |
|---|---|---|
| `CURRENT_SPEC.md:676` | `secondary_asr`の`stop_retrying=True`でfallback未到達→HR | 注記追記(統一ASR判定仕様節末尾「旧記述の注記」)。既存行は不変 |
| `CURRENT_SPEC.md:1975` | 中間ASR結果`Primary#2/Secondary#1/#2`が成果物JSONに残らない | 同上 |
| `CURRENT_SPEC.md:2020` | ASR-first Retry Policy: Cascade`stop_retrying`(尽き) | 同上 |
| `CURRENT_SPEC.md:2022` | 減速後`_post_slowdown_cascade_rescue()`・4-step cascade全体 | 同上(撤去済み・現行は`_post_slowdown_unified_judge`) |
| `CURRENT_SPEC.md:2029` | 減速後cascade救済はCS Layerのflagを渡さない | 同上 |
| `CURRENT_SPEC.md:2032` | JA Variant Layerの`Primary#1/#2・Secondary#1/#2`の4箇所 | 同上 |
| `DECISION_LOG.md:8045,8047,8117,9547,9762,20548,20604,20649,20662,20663,20711`(索引1行の追記で現在+2行) | stop_retrying/Primary#2/Secondary#1/#2/減速後cascade救済の当時の判断・観測 | 末尾「ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01」節に「旧記述(2026-10-16 AUWで撤去済み、現行は統一judge)」注記。履歴として有効、不変 |
| `OPEN_ITEMS.md:238,240,246,297,299,362,759,773,823,831`(OPEN-61/62/66/122/125/181/257/270/320/328) | 旧Cascade・stop_retrying・Primary#2/Secondary#2・`_post_slowdown_cascade_rescue`・減速後cascade救済 | 新規OPEN-380に同旨の注記(各OPENの既存行は不変)。OPEN-270(`_post_slowdown_cascade_rescue`配線、CLOSED)は履歴として有効 |
| `er026_output/family_z_production_e2e_01/melos/asr_root_cause_01/reeval_post_slowdown_01.py:53` | `tg._post_slowdown_cascade_rescue(...)`呼出(撤去済み関数) | 冒頭に「撤去済み関数参照・履歴保存(実行不能)」コメントを追加(構文確認済み)。コード本体は不変 |
| `er026_output/.../reeval_counterexample_phraselist_01.py:50` | 同上 | 同上 |
| `er026_post_slowdown_cascade_rescue_01_test_01.py` | 旧「減速後cascade救済」test(コメントに`Primary#2`) | 05で統一経路へ追随済みの現行test(`apply_a2_slowdown_postprocess`を検証)。処置なし |
| `er006_secondary_asr_01_m1_wiring_test_01.py:269`・`er065_short_clip_asr_context_trial_01_regression_test_01.py:225`・`er078_asr_unified_en_wiring_test_01.py:414`・`er078_asr_unified_wiring_06c_test_01.py:532` | 撤去記録のコメント/撤去固定assert | 現行・処置なし |
| `er006_secondary_asr_01.py`/`er007_ja_secondary_asr_01.py`(Primary#2・Secondary#2・`stop_retrying`の語) | 旧Cascade関数は**flag OFFロールバック経路として保持**(`cascade_enabled=False`)。Production既定では統一judge経由 | 処置なし(意図した残置。OPEN-380に記載) |
| docs/履歴文書: `docs/pm/delegation_log/*`(2026-10-12〜15の委任文)・`docs/pm/recon_reading_validation_wiring_01.md`・`docs/pm/design_principles/connected_speech_proper_noun_phonetic_equivalence_2026-10-13.md`・`docs/pm/reports/2026-10-13_CONNECTED_SPEECH_REPORT_REPLAY_01.md`・`docs/research/ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01/REDETERMINATION_CHECK_01.md`・`er053_output/*`・`er056_output/*`・`ER-006/007-*_report.md`ほか | 当時の設計・調査・報告 | 履歴として保存(不変)。旧機構の記述は**時点記録**でありProduction仕様の参照ではない |
| 旧評価script群: `er006_retry_cascade_prod_01_eval.py`・`er007_ja_cost_latency_projection_01.py`・`er007_ja_tts_retry_path_fix_cost_01.py`・`er056_ja_scg_offline_replay_01.py`・`er011_output/open123_*/gate_a_trial08_p3_runtime_evidence.py` | 旧Cascade(Primary#2/Secondary#2)前提の評価 | 旧関数は残置のため実行可能だが、現行Productionの経路とは別。OPEN-380に「旧評価script群のPrimary#2参照[再現不能になり得る]」として記録(コードは不変) |

判定: SSOT側3ファイルに注記を追記済み(既存行の書換え・削除0)、撤去関数を呼ぶscript 2本に冒頭コメント追記済み。Production code/Promptが**未承認・未実装・撤去済みの機構を参照する箇所は0**(上記コード側の確認)。

## 4. 15条件の最終充足表(2026-10-16 委任_07時点)
| # | 条件 | 判定 | 根拠・残 |
|---|---|---|---|
| 1 | ASR判定仕様と実際のProduction動作が一致 | **一部** | 全状態機械・値ガード・Secondary 1回・試聴・LR/HR末端の実音声を取得(`RUNTIME_EVIDENCE_06.md`§1〜§14)。残=Family C JAの新規生成到達不能(F4=OPEN-372)、Family B A2 narrator見出し/Hook/Tension/Closing・(narrator外側ループ最終NGは07b §15-5で実音声取得済み) |
| 2 | 日本語・英語、全Production音声Sectionに適用 | **一部** | 43行マトリクス中37行を実音声、5行は再利用・複製で判定なしが仕様どおり、Y-00 N/A(§13-10)。未充足=C JA新規生成(F4)とB A2 narrator一部 |
| 3 | Primary NG→Secondary PASSがWARNING付きで採用 | **充足** | 06b/06d/06e(`xkp`/`nlkp`/`nlneg`ほか)。取込後も中核test 411 passed |
| 4 | 両NGなら最大3回のTTS生成フロー成立 | **充足(一部残: C JA新規生成F4)** | Dialogue通算3回(`dlg_cap2`)・KP英語4回(`kp4`)・Z `kp_en`・A2減速後NGのHR末端に加え、07b(`RUNTIME_EVIDENCE_06.md` §15-5)でnarrator `generate_a2_segment_with_slowdown`の通算3回(cool-down 600.004秒込み)→`NG_BOTH`→Lock HR(cumulative 3)・HR queue 1行・Secondary重複0・shared_state不変を実音声で確認。残=C JA新規生成(F4)のみ |
| 5 | 数値の同値・異値判定と否定保護 | **充足** | 9例test(`er078_asr_value_guard_01_test_01.py` 58)・`nlneg`・集計oracle 0 |
| 6 | Connected Speech／M1／F1の既存Regressionに悪化なし | **充足** | 取込後の中核test 411 passed。Melos regression(06・06b)。旧test 83 fileの本予行はmainと同一outcome。ただしCS MIXED時のSecondary単独採用は**意図した挙動変化**(CURRENT_SPEC記載) |
| 7 | 試聴リストへのWARNING連動 | **充足** | 06b/06d(最終ページ節・導出失敗表示)。後方互換test 53 passed |
| 8 | Secondary二重呼出・予算超過・無限retryなし | **充足** | 06〜06eの全run重複0(06d 18呼出、06e circuit異常終了F2解消)。07のnarrator途中終了分・07bの完走分とも重複0(Azure 各1)。費用累計 約91円(各上限内) |
| 9 | Production正式pathのruntime evidence | **一部** | X/B/legacy A/Z/Cの各入口で実音声。残=C JA(F4)・B A2 narrator一部(条件1・2と同じ) |
| 10 | 必要なUnit／Regression／Integration testがPASS | **充足** | 取込後 中核12 file 411 passed・静的監査15 passed(差分空)・後方互換53 passed・flag OFF経路3 passed。全suiteのper-fileは06eで新規失敗0。既存の失敗(main時点148件等)は同一でAUW起因ではない |
| 11 | CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSに実態を反映 | **一部(branch上に草案を追記済み。main反映はmerge時)** | `CURRENT_SPEC.md`統一ASR判定仕様節・`DECISION_LOG.md`末尾節+索引・`OPEN_ITEMS.md` OPEN-370〜380・`USER_DECISION_REGISTER_01.md` #83〜#87・`REPORT_LEDGER.md`。**注**: 委任文の「OPEN-356更新」はKGCPW(別項目)の番号のため、OPEN-370を置き場とした |
| 12 | commit／push／mergeを確認 | **一部** | branchはcommit/push済み。**merge未(ユーザーGo待ち #87)** |
| 13 | Dangling Reference Checkで問題なし | **充足** | §3の表。Production code/Promptの旧機構参照0、SSOT注記・script冒頭コメント済み |
| 14 | 未解決UDR・未配線APPROVED項目を明示 | **充足** | U1〜U4+Go(#83〜#87)・OPEN-371〜380。AUW自体は「実装済み・merge待ち・PRODUCTION_WIRED未宣言」 |
| 15 | Fableの独立照合 | **未充足** | Fableの工程(本委任の対象外) |

→ **1項目でも未確認があるため`PRODUCTION_WIRED`とは報告しない**(条件1・2・4・9の一部、12、15)。

## 5. Gate 3／4／7チェックリスト
### Gate 3 — Production Wiring Checklist(`PM_GOVERNANCE.md` 2-0)
- [x] Production正式初回経路: 各Family runnerの入口(X/Z/legacy A/B/C)で統一judge。DEV/Trial-onlyではない(静的監査のpost_wiring allowlist)。
- [x] retry・fallback・regenerationとの整合: 通算TTS3回(KP英語4回の既存例外)・A2外側ループ・LR後v1・再利用guard。HR Lock/予算guardは無変更(`er011_human_review_lock_01.py`のdiffは`asr_judgement`のadditive 1項目のみ)。
- [x] 必要testのPASS・runtime evidence: 上記条件3〜10。
- [ ] Production runtimeでの実発火: C JA新規生成(F4)・narrator外側ループ最終NGの実音声が未完。
- [x] 実際のmodel_id・routing: TTS=`gemini-3.8-flash-lite-tts`、Primary=`gpt-4o-mini-transcribe`、Secondary=Azure STT(`usage_log.jsonl`で実測)。モデル・Voice・速度・Promptは不変。
- [x] コスト影響評価: 追加増分 中央値0.55〜0.82円/セット(目標70円の約1〜4%)。実費累計 約90円。
- [ ] `CURRENT_SPEC`/`DECISION_LOG`/`OPEN_ITEMS`/Git反映: branch上の草案は済み、main merge未。
- [ ] approved specとProduction挙動の一致: 一致(条件1)は前進したが未充足部あり。**Opusレビュー(必須案件)反映状況**: 条件A=OF-AUW-01〜18採否済み、条件C=C-01〜14のFable採用分を06cで実装、C-04/05/07/09/11の個別内容は未転記。
### Gate 4 — Dangling Reference Check(+ADDENDUM §2 L99)
- [x] Dangling Reference Check(§3)。[x] revert予行(`REVERT_REHEARSAL_07.md`:衝突0・main相当へ完全復元)。[x] 旧test再実行(main時点とoutcome差0)。[x] 新キー後方互換test(53 passed)。
### Gate 7 — 実務報告の受入判定(Fableが実施)
- 照合推奨の重要証拠(2件以上+失敗経路1件): (1)`er078_asr_unified_judge_01.py:65-66`のU1/U2定数が既定値のまま(`git diff`で変更なし)、(2)`CURRENT_SPEC.md`統一ASR判定仕様節と`DESIGN_01.md`§4-3の文言照合、(3)失敗経路=`dlg_cap2`(通算3回NG→Lock HR・queue 1行、`evidence_06e/dlg_cap2/runner_execute.json`)と`tstop`(Secondary障害→技術STOP・残clip TTS 0)、(4)07の失敗終了=narrator途中終了(`evidence_07/narr_cap3/`: 最終成果物=減速後NGの2 attempt分のwav・attempt_history 4行・`runner_execute.json`なし・Lock RESOLVED[3回目に到達せず])は目的要件(L204「両NGなら最大3回のTTS生成フロー」)に対し**未完**であり、それ自体は目的を満たす成果物ではない。
- 高リスク案件(retry/fallback/Human Review/複数Family)として全件+影響範囲まで確認。受入記録は`受入記録:`固定見出し5項目(当初目的の逐語は§0)。
- Production採用(`APPROVED_FOR_PRODUCTION`)はユーザー済み。`PRODUCTION_WIRED`は人間/Fableが条件1・2・4・9・12・15の充足後に判断。

## 6. 後始末の確認
- 予行worktree 3つ(`eigo-radio-auw-revert`/`-revert-b`/`-main`)は`git worktree remove --force`で撤去済み(`git worktree list`にAUW用なし)。
- `docs/pm/delegation_log/2026-10-15_DAY3-4-OBJECTIVE-ALIGNMENT-REBLIND-02_P.md`・`_P_check.json`は、`origin/main`取込時にuntracked同名file(main側と同一内容を確認)との衝突を避けるため、branchへ1 commit(`143d1b78a`、内容はmainと同一)として取り込んだ。



## 4-b. 15条件の充足表(2026-10-16 委任_11時点。§4の再掲更新。既存表は不変)
| # | 条件 | 委任_11時点 | 根拠・残 |
|---|---|---|---|
| 1 | ASR判定仕様と実際のProduction動作が一致 | **一部** | U1発効済み(`RUNTIME_EVIDENCE_06.md`§17-1)。残=A3(length)未是正(s4保留、OPEN-388)、narrator Hook/Tension/Closing未取得(OPEN-396)、fresh JA正例未取得 |
| 2 | JA・EN、全Production音声Sectionに適用 | **一部** | 43行: 実音声37・部分1(B-A2-01)・再利用4・N/A 1。Family C JAはFCJ 委任_03で実音声済み、X-B1-06は本委任で実音声 |
| 4 | 両NGなら最大3回のTTS生成フロー成立 | **充足(委任_07時点から変更なし)** | 本委任でpoint_twoがNG_BOTH→再生成→PASSを実音声でも確認(正当な標準retry) |
| 9 | Production正式pathのruntime evidence | **一部** | Family B入口(`run_tts_a2_2v_new_topic`)の実音声を取得(5 clip)したが、Hook/Tension/Closingと`tts_generation_results.json`・試聴リスト導出が未到達(OPEN-396) |
| 11 | SSOTに実態を反映 | **充足(本commitで反映)** | CURRENT_SPEC・DECISION_LOG・OPEN-394〜396・REGISTER #83・REPORT_LEDGER・Opus台帳 |
| 12 | commit/push/merge | **充足見込み(本commit後に確認)** | mainへ反映(`crbn`でff)。merge自体は#87 Go・委任_08で完了済み |
| 15 | Fableの独立照合 | **未充足** | Fableの工程 |
→ 未取得evidence(条件1・2・9の一部)があるため`PRODUCTION_WIRED`とは報告しない。

## 4-c. 15条件の充足表(2026-10-16 委任_12時点。§4・§4-bの再掲更新。既存表は不変)
| # | 条件 | 委任_12時点 | 根拠・残 |
|---|---|---|---|
| 1 | ASR判定仕様と実際のProduction動作が一致 | **一部(残=A3のみ)** | narrator全Section(Hook/Tension/Closing含む)とfresh JA Secondary呼出の実音声を取得(`RUNTIME_EVIDENCE_06.md`§18)。残=A3(length)未是正(s4保留、OPEN-388、Opus D1レビュー・是正は別委任) |
| 2 | JA・EN、全Production音声Sectionに適用 | **一部(残=A3のみ)** | 43行最終: 実音声38(B-A2-01を区分1へ)・再利用4・N/A 1。実音声で未確認のSectionは残っていない(A3は判定仕様の長さ条件であり音声Sectionではない) |
| 4 | 両NGなら最大3回のTTS生成フロー成立 | **充足** | 委任_11(point_two)に加え、委任_12でもpoint_one attempt1 NG_BOTH→attempt2 PASS、fresh JA jf2は3回NG_BOTH→HR(誤受理なし)を実音声で確認 |
| 9 | Production正式pathのruntime evidence | **一部(残=A3のみ)** | Family B入口`run_tts_a2_2v_new_topic`の9 segment全て(Hook=full_story_part1/2、Tension=tension_reflection、Closing=in_one_line含む)+`tts_generation_results.json`+試聴リスト導出まで取得。fresh JAもSecondary実呼出1正例(jf3)取得 |
| 11 | SSOTに実態を反映 | **充足(本commitで反映)** | CURRENT_SPEC・DECISION_LOG・OPEN-395/396・REPORT_LEDGER・Opus台帳(OF-AUW-U1R-08→EVIDENCED) |
| 12 | commit/push/merge | **充足見込み(本commit後に確認)** | mainへ反映(`crbn`でff) |
| 13 | Dangling Reference Check | **充足(変更なし)** | §3。本委任はProduction無編集 |
| 15 | Fableの独立照合 | **未充足** | Fableの工程 |
→ 条件1・2・9の残はA3(OPEN-388、別委任)のみ。`PRODUCTION_WIRED`は宣言しない(到達上限=`AUW_EVIDENCE_COMPLETE_PENDING_FABLE_15`)。

## 4-d. 15条件の充足表(2026-10-16 委任_13時点。§4・§4-b・§4-cの再掲更新。既存表は不変)
| # | 条件 | 委任_13時点 | 根拠・残 |
|---|---|---|---|
| 1 | ASR判定仕様と実際のProduction動作が一致 | **充足(残なし、A3是正済み)** | A3(length)をSecondary採用転写で再評価する実装を反映(`IMPLEMENTATION_13.md`)。実音声(Azure)でEN/JA正例・EN負例(`RUNTIME_EVIDENCE_06.md`§19)。Fable判定待ち(`A3_FIXED_PENDING_FABLE`) |
| 2 | JA・EN、全Production音声Sectionに適用 | **充足(残なし)** | 43行最終=実音声38・再利用4・N/A 1(委任_12から不変)。A3は呼出元10箇所(EN6/JA4)が`max_len`を渡して適用 |
| 11 | SSOTに実態を反映 | **充足(本commitで反映)** | CURRENT_SPEC・DECISION_LOG・OPEN-388追記/OPEN-397/398・REPORT_LEDGER・Opus台帳(OF-AUW-A3R-01〜09) |
| 12 | commit/push/merge | **充足見込み(本commit後に確認)** | mainへ`--no-ff` merge |
| 15 | Fableの独立照合 | **未充足** | Fableの工程 |
→ 条件1・2の残なし(A3是正済み)。`PRODUCTION_WIRED`は宣言しない(到達上限=`A3_FIXED_PENDING_FABLE`)。

## 4-e. Fable独立照合(条件15、2026-10-16、委任_14記録)
A-7完了条件13項目の照合(Fableが現物確認した事実のみ。Sonnetは記録のみ)。
| # | 条件 | 判定 | 根拠file |
|---|---|---|---|
| 1 | 正式初回経路に統一判定 | 充足 | X/Z/legacy A/B/C入口、静的監査allowlist |
| 2 | retry/fallback/regeneration/LR後の整合 | 充足 | 06c〜07b、A2外側ループ、LR後v1、再利用guard |
| 3 | U1是正 | 充足(発効済み) | 範囲限定A7=登録読み辞書不一致のみ事前除外維持。`er078_asr_unified_judge_01.py:73`(`U1_KEEP_C1_SIMILARITY_EXCLUSIONS = False`)、同`:125/:148`(A7) |
| 4 | U2確認・整理 | 充足 | (i)維持、死定数撤去、呼出点1箇所を静的test固定 |
| 5 | 全Section実音声 | 充足 | 43行: 実音声38・再利用4・N/A 1。narrator 9 segment、Family C JA 5 clip(`er079_output/.../EVIDENCE_02.md`§6)、X-B1-06 |
| 6 | 数値/否定/CS/M1/F1 Regression | 充足 | 中核test、Melos 06/06b、値ガード9例。既存失敗2件(koro)はAUW前から |
| 7 | WARNING試聴リスト機能 | 充足 | 06b/06d、委任_12導出、test_13 |
| 8 | 二重Secondary/無限retryなし | 充足 | 全run重複0、circuit breaker、cap |
| 9 | model_id/routing | 充足 | usage_log実測 |
| 10 | SSOT更新 | 充足 | 本委任(委任_14)で最終記録 |
| 11 | merge/push/merge後test | 充足 | `b010cb469`〜`9f3738334` |
| 12 | Dangling Reference | 充足 | §3+各委任 |
| 13 | Fable独立照合 | 充足(本記録) | Fableが現物確認: `er078_asr_unified_judge_01.py:73/:125/:148`、a3 worktree同file`:56/:95/:146/:437/:542/:558`(A3是正)、`CLOSEOUT_PLAN_07.md`§4-c/§4-d、`USER_DECISION_REGISTER_01.md:170-172`、`RUNTIME_EVIDENCE_06.md`§15〜§19要旨 |
**Fable判定: `PRODUCTION_WIRED`(2026-10-16)**。付帯事項(宣言の条件ではなく開示): (a)A7範囲限定[ユーザー報告で明示。ユーザーが解放を望む場合は定数/規則1行で変更可] (b)独立OPEN: 371(U4現行許容)/373/374/375/377/378/379/380/381〜386(FCJ)/389/390/391/394(Primary層の弱点=ユーザー判断事項)/395(JA Latin語web lookup費用=ユーザー判断事項)/397/398 (c)`PRIMARY_LENGTH_EXCESS`は閾値なしで全件付与(試聴対象増は運用観察) (d)A4(C2)・P1は不変。
