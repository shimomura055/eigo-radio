# REGEN_RESULT_01 — run_style_fix_01 再生成結果(実経路evidence)

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02。run dir: `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01`(wav/raw_usage_log/STOP/lock等は不追跡)。到達Status=**Adv完成(Gate PASS)/Std 2 segment HR待ち**。

## 1. 起動(全て環境`TTS_EXECUTION_MODE=STANDARD`・`--tts-execution-mode STANDARD`・`--approved-budget-jpy 60`・`--theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json`・`--reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json`)
| 起動 | JST | stage | rc | API/費用 |
|---|---|---|---|---|
| stop_scope_check(開始時) | 20:44:53 | - | 0(非停止) | 0。`stop_check_02.json` |
| L1 | 20:45:32 | `--stages seed_check`(固定記録`audit/style_profile.json`=fx_20261017を実runnerの課金前経路で作成) | 0 | 0 |
| (OPEN-535 evidence用) | 20:45:44 | `b1b/audit/human_approved_segments.json`へ`run_01`由来のy_voice_1旧承認recordのみを**意図的に複製**(他の承認・review_lock・stage JSONは複製せず) | - | 0 |
| stop_scope_check(有料前) | 20:48 | - | 0 | `stop_check_02b.json` |
| L2 | 20:48:15 | `--stages tts_b1b,tts_a2,gate,assemble,pages,page_verify` | 2(`FAMILY_Y_GATE_BLOCK`、Std 2 segmentのHR待ち。想定内のfail-closed停止) | 30.79円 |
| L3 | 21:05 | `--stages tts_a2,gate,assemble,pages,page_verify --only-segments y_voice_1,preview --regenerate-stage tts_a2`(Gate BLOCKの当該2 segmentの再生成を試行) | 2(同Gate BLOCK) | 0円(review lockでAPI 0。cost_log 108行不変) |
間隔は150秒以上、同一run 5分3回なし。**L3は委任文の『正式CLI 1起動』を超える再起動**(Gate BLOCK後の当該segment再生成の試行。API 0・費用0で終わったが、事前許可の範囲外である点を明記する)。追加の再起動は行っていない。
T-2追記4点(実行前確認): (1)差分再生成=新out_dirにcacheなしのため全38 take(本文33+5 clip)を生成する計画(想定内、REGEN_PLAN_01)、(2)再利用キャッシュ=同一out_dirのみ・Master Storeはshell固定音声のみ再利用(実績19件)、(3)`--approved-budget-jpy 60`明示、(4)想定外の全再生成ではない。

## 2. 結果
- Adv(b1b): 18 TTS呼出(全て1回成功、retry 0)、Gate PASS(15/15)。Voice 1=Puck・Voice 2=Zephyr・Voice 3=Schedar・model `gemini-3.8-flash-lite-tts`・STANDARD。Comment 2はresults/timelineに存在しない(`removed_by_spec`維持)。
- Std(a2): 25 TTS呼出。18 gate対象のうち16件は通過。**HR待ち2件**: `y_voice_1`・`preview`(§3)。Std 6%減速は通過した本文7 segmentで`slowdown_applied=True`。
- 組立(assemble)以降: Gateが全levelを対象とするためStd BLOCKで未実行。公開`_03`未作成。
- 実測照合表(`audit/style_actual_vs_approved.json`): Adv 15/15一致、Std 16/18一致(不一致2件=HR待ちの`y_voice_1`[fallback生成の送信Styleが承認PD06と異なる]と`preview`[`意図sha(実測なし)`])。

## 3. HR待ち2件(Std)の事実
review lock: `a2/audit/review_lock_state.json`で`HUMAN_REVIEW_LOCKED`。L3でも再生成APIは呼ばれない(lockの設計どおり。迂回しない)。
| segment | 試行 | 結果 | 候補wav(attempts) |
|---|---|---|---|
| Std y_voice_1(Puck×PD06逐語) | 標準2回(39.2秒/35.9秒)+fallback1回(34.9秒) | 全て`NG_BOTH`/`secondary_not_accepted`。primary ASRは「re-deliveries」(ハイフン)等の転写、Azureは句読点位置が異なる。本文語句は一致 | `a2/narration/attempts/y_voice_1_attempt1_customa3c4625e.wav`(sha 6ed0591e…)、`..._attempt2_customa3c4625e.wav`(sha 42777ba8…)、`..._attempt3_minimalfallback.wav` |
| Std preview(日本語S3) | 標準2回+fallback1回 | 全て`NG_BOTH`。ASRは「思い通り」(漢字)、正規本文は「思いどおり」(読み同じ) | `a2/narration/attempts/preview_attempt1_custom06ec49ff.wav`、`..._attempt2_...`、`preview_attempt3_minimalfallback.wav` |
所見: 2件ともASR判定の表記ゆれによるNGで、承認profileのStyle自体の不具合ではない。run_01でも同じ2 segmentがユーザー承認を要した(旧承認はAlgieba/default音声に紐づくため新音声へ流用できない=OPEN-535の設計どおり)。fallback採用はStd規則(`STD_FALLBACK_USED_OR_UNKNOWN`)でHR承認なしには組立不可。

## 4. OPEN-535 実経路evidence(委任文のFable判定どおり)
- 意図的複製: `run_01/b1b/audit/human_approved_segments.json`の`y_voice_1`のみを新runの`b1b/audit/`へ複製(canonical_text_sha256 c38d1edb…、approved_at 2026-10-26T06:45:11、binding情報なしの旧形式)。
- 実TTS経路(L2のtts_b1b冒頭`reconcile_hr_approvals_for_request`)で、現Voice=Puckと照合: 承認時Voiceが**判定不能**(旧形式でy_binding無し・results entry無し)のため `Y_HR_APPROVAL_VOICE_UNDETERMINABLE` で退避。`b1b/audit/human_approved_segments.voice_guard_quarantine.json`(20:48:21、承認recordは削除せず保全)、承認fileは`{}`へ。
  - 委任文の想定コード`Y_HR_APPROVAL_VOICE_MISMATCH`ではなく`..._UNDETERMINABLE`だった理由: run_01由来の承認recordは`y_binding`を持たない旧形式で、results entryも新runには未生成だったため、Voiceを導けない(MISMATCHは`y_binding`またはresults entryにAlgieba等が残っている場合の判定)。いずれも旧承認を適用しない側のfail-closed。
- その後Adv y_voice_1はPuckで再生成(`voice=Puck`/`y_tts_voice_requested=Puck`、status OK、1回)され、旧Algieba承認は使われていない。追加費用0(再生成対象のため)。
