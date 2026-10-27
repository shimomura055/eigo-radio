# WIRED_CHECK_02 — OPEN-537 確認条件8項目の最終照合(委任_09、read-only、API 0・JPY0)
**判定は行わない(PRODUCTION_WIRED認定はFable専権)。** 原文=`docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_USER_04.md` §2(確認条件8項目)。ユーザー試聴PASSだけでWIRED認定しない(同§2末尾)。WIRED_CHECK_01(委任_07、commit 945b07a28)の条件1〜8に、委任_08(commit 53434b004、表示仕様のProduction実装)・委任_09(commit 29d1a79d7、`_03`公開ページ凡例是正)の成果を加えて再照合した。

## 条件別照合
| # | 条件(USER_04 §2) | 判定 | 根拠 |
|---|---|---|---|
| 1 | Y正式初回Production音声経路で`fx_20261017`が既定適用 | 充足(注記) | `er121_family_y_audio_01.py:804 Y_APPROVED_STYLE_PROFILE`、runnerにprofile上書きCLIなし、`resolve_style_profile`で課金前固定(`run_style_fix_01/audit/style_profile.json`)、commit 3af84a499。WIRED_CHECK_01#1のまま変化なし。注記=実走は再配達テーマの再生成run。新規テーマのゼロからの初回runは未実施(次のY新規記事で自然に満たされる)。委任_08/09はStyleに触れていない。 |
| 2 | Std/Adv全対象部位でStyle一致 | 充足 | `style_actual_vs_approved.json` Std 18/18・Adv 15/15 all_match=True(VERIFY_04)。委任_09で`_03`のaudio/*.mp3 sha不変(`VERIFY_07`: std_full 7c037f49…・adv_full f2c7d26f…)=音声は承認時のまま。 |
| 3 | Style不一致時fail-closed Gate | 充足 | `er121_family_y_audio_01.py:843-850`、`TestGateFailClosed`。style系test 37/37・hr_approval_guard 16/16・page_pause 9/9(WIRED_CHECK_01で実行)。委任_08でGate/Styleは無変更(IMPLEMENTATION_08 §4)。 |
| 4 | retry/fallback/regeneration/resume | 充足 | `TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/EVIDENCE_Y_01.md`、`REGEN_RESULT_02.md`§3/§5。委任_08/09は音声生成・retry系を無変更。 |
| 5 | 正式runnerのruntime evidence | 充足 | 正式runner `er121_family_y_runner_01.py --mode real`のrun `run_style_fix_01`(REGEN_RESULT_02)。DEV/Trial専用経路ではない。 |
| 6 | actual model_id・routing・Style profile・実測記録 | 充足 | `style_actual_vs_approved.json`(model=`gemini-3.8-flash-lite-tts`、tts_backend=`speech_metadata_flash_lite`、measured_sha=approved_sha)、`audit/style_profile.json`。 |
| 7 | 必須Regression/Validator/Integration test | 充足(Y Style範囲)+注記 | Y Style系62件PASS(WIRED_CHECK_01)。委任_08の回帰(IMPLEMENTATION_08/RESULT_PACKET_YSP8): er121=375中373 pass/1 error/1 skip、er019=552中551 pass/1 fail、er026=224中222 pass(2 skip)、er063=161全pass、er062=147全pass、er117=106全pass、新規`er_page_audience_marker_test_01` 14全pass。**既存失敗2件(今回起因でない、HEAD別worktreeでも同一失敗)**: (a) `er121_family_y_runner_01_test_01.StudyTextWiring.test_two_items_adopted_in_standard…`=文法採用が委任_05A新仕様(最大1件)になり旧仕様testと食い違い。GPG 05B(commit c76784bef「wiringの新仕様追従…」)で是正見込み(本委任では再実行せず未確認)。(b) `er019_x_std_chunk_opus_test_01.R4HunkClassifierTest`=bb578265cとのdiff分類が陳腐化(X part2等の他タスク変更で既にUNCLASSIFIED)=OPEN-543。プロジェクト全体regressionは並行Agent編集中のため未実行。 |
| 8 | SSOT/Git反映とFable独立受入 | **Fable受入待ち(未充足)** | Git反映済(3af84a499/d2d68194d/b9be75ef4/01e7d02ec/945b07a28/53434b004/29d1a79d7)。SSOT(OPEN-537 Status・CURRENT_SPEC:3166・DECISION_LOG)の更新とPRODUCTION_WIRED判定はFableが実施(是正文案=WIRED_CHECK_01 §3、追記案=RESULT_PACKET_YSP9 (6))。 |

## 注記
- 本委任で撤去した`_03`凡例⏸1行は表示のみ(音声・本文・KP不変、VERIFY_07)。USER_04 §1-C(公開ページに開発用マーカーを出さない)・§3-4(公開ページ整合)の`_03`側の最後の不整合を解消した。
- `pause_scan/pause_align/pause_stats`(委任_08で残置): Voice 1候補表の停止統計(解析表)用。ページ表示(台本のポーズ表示)には使わない(IMPLEMENTATION_08 §4、REMOVAL_RESULT_02)。
- 文法/KP表示、Voice説明文(`PAGE_NOTICE_JA`単一ソース)、Chunk境界マーカー(audience=dev|public、既定public)は委任_08でProduction builderにIMPLEMENTED+test済み(PRODUCTION到達判断はFable)。
