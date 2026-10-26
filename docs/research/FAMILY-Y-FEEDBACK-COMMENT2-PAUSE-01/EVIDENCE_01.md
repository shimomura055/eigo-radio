# EVIDENCE_01 — 『宅配』E-1へのAdvanced Comment 2削除の反映(runtime evidence)と試聴ページ改修

管理ID: FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_03(2026-10-26 JST)。判定語(PRODUCTION_WIRED等)はFable。ここでは事実のみ記録する。

## 1. 再組立(API 0)
- 起動前: `stop_scope_check_01.py` rc=0(`run_01/stop_check_委任_03*.json`)。
- コマンド(1起動、09:12:26 JST、rc=0、`console_yfb3_reassemble.log`): `er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_01 --theme-package … --reuse-manifest … --approved-budget-jpy 170 --stages gate,assemble,pages,page_verify`(`TTS_EXECUTION_MODE=STANDARD`)。
  - 委任文の `--stages provision_shell,…` はY runnerに `provision_shell` stageが無く rc=2(`[STOP] --stages に不明なstage` 、起動前検証で何も実行せず)。`provision_shell`はZ runnerのstage名の混入。Y runnerのSTAGES=seed_check,text,translate,support,kp,tts_b1b,tts_a2,gate,assemble,pages,page_verify。
  - `--approved-budget-jpy 250` は `APPROVED_BUDGET_MAX_JPY=170`(案件個別Cap、runner:32)を超えるため rc=2(`FAMILY_Y_BUDGET_ABOVE_CASE_CAP`、何も実行せず)。過去の起動(`run_launch_log.jsonl`)と同じ170で実行。API 0なので消費0(`spent_jpy 52.134`は既存累計の表示)。上限定数は変更していない。
  - 上記rc=2が2回続いたが、いずれも引数検証での即時拒否(API呼出0・外部停止なし)であり、原因を特定して引数を是正した。
- 結果: gate b1b/a2とも PASS(`gate_summary.json`、`y_body_blocked=[]`)。page_verify `ok:true, violations:[]`(`page_verify_local.json`)。`final_manifest.json` に `removed_by_spec.b1b.comment_2 = "2026-10-26 FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01(ユーザー承認: Family Y Advanced Comment 2削除)"`。

## 2. timeline差分(再組立前後、`measure/pre_reassemble/`に前の写し)
| 対象 | 前 | 後 |
|---|---|---|
| Advanced `b1b/audit/timeline.json` | 45要素 sha256 `1e8144930739…`、全体330.10秒 | 43要素 sha256 `ea075990e230…`、全体320.69秒 |
| 差(multiset比較) | 削除: `Comment 2`(8.61秒)+`pause_comment_to_story`(0.8秒)の2要素のみ。追加0。他の全パートの種別・秒数は同一 | |
| Advanced assembled wav | sha `befe459fdc37…` | sha `0924c42122170d77…`(320.69秒) |
| Standard `a2/audit/timeline.json` | sha256 `527ff4d6cb38…` | **同一**(`527ff4d6cb387828c097d4db8bdbf45cb6e738c1ebb86ce05b7107c0b899b5ec`) |
| Standard assembled wav | sha `283a006b4536…` | **同一**(`283a006b453657890f13713d91734a6ab15516202058c26fa2603a6c32db7659`) |
- Standardは音声・timelineともバイト同一(Comment 2を維持、日本語側は現状維持)。公開dirのStd mp3(`std_*.mp3`、`std_full.mp3`)もgit差分0。
- 旧`b1b/narration/comment_2.wav`は削除していない(組立・ページ・manifestでは未使用)。`b1b/audit/tts_generation_results.json`の過去の生成記録(comment_2エントリ)は残置(記録であり、組立の入力ではない)。Preview(重複回避参照の旧role生成)は再生成せず再利用(Fable判断)。
- 公開ページ(`user_test/family_y_production_redelivery_fee_01/index.html`): Advanced節の`Comment 2`行0件、`Comment 1`・`Comment 3`行は存在。Standard節の`Comment 2`行は1件(維持)。

## 3. 試聴ページ改修(ユーザー原文§4)
- 実装(pages生成コードに追加、手書き差分なし): `er121_family_y_audio_01.py` の `pause_scan/pause_align/pause_stats/_script_with_pauses/_tts_unit_badge/page_legend_html/voice1_candidates_aux_html`、`build_page_rows`(バッジと停止重畳)、`render_y_page`(冒頭凡例)、`er121_family_y_runner_01.py` `stage_pages`(候補表をaux_htmlへ)。共通builder(`er_user_listening_page_common_01`)は無変更(X/Zページに影響なし)。
- R1: 全segment行(Std 8行/Adv 8行)に「TTS 1回 / 分割なし(段落=1) / 追加0.2秒ポーズ: なし」(Stdは「Standardの本文は分割対象外」)。分割の有無は`chunk_tts_decision.json`の実判定から読む。冒頭凡例に「TTSの実分割: なし/追加0.2秒ポーズ: なし」と、見た目の段落とTTS実分割は別である旨。
- R4: 完成音声を実測した700ms以上の停止を台本の語位置に重畳(`⏸1.88s@0:29.0`形式=長さ@その行の音声内の時刻、位置は推定±2〜3語の注記つき)。表示専用でblocking検査にしない。
- R2/R3/R5(分割境界マーカー/0.2秒実測offset/chunk個別再生)は分割があるsegmentのみ。今回は分割0のためバッジ文言の分岐のみ実装(境界マーカー・chunk個別再生は未実装=分割時に必要になった時の別実装。UIを増やさないR6に従う)。
- Voice 1個別再生: ページ末尾の補助表示(details)に「Voice 1の聴き比べ(候補・未採用)」として 現行採用+候補3(Std/Adv) をmp3再生付きで並べ、停止統計(1秒以上停止数・停止占有率・文中停止数・最長)を併記。候補・未採用を明記。
- E-3(`user_test/family_y_production_sns_age_limit_01/index.html`): Trialサンプル保管の注記1行を追加(音声・本文は不変)。
- check: `user_test_page_standard_check_01.py` rc=0(overall PASS)/`y_page_notice_check_01.py` rc=0(ok、violations []) を両ページで確認。
- 公開mp3のみ追跡(wav不追跡)。URL: https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_01/index.html

## 4. test
- 新規 `er121_family_y_page_pause_test_01.py` 9件PASS(合成信号の停止検出・blip統合・重畳・閾値未満非表示・バッジ・凡例・候補なし時の空・現行採用Adv Voice 1で委任_02 toolと数値一致[14停止/≥700ms 7/≥1000ms 3/最大1250ms/19.9%])。
- `PYTHONPATH=netblock_harness_01 .venv\Scripts\python.exe -m pytest er121_*test*.py -q` = **276 passed, 1 skipped**(HEAD比 +9)。

## 5. 副作用・注意
- 候補生成(正式経路)は共有の追記型ログ `er011_output/attempt_history.jsonl`(8行、パスに`voice1_candidates`を含む)と `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(1行、Std take1のSTOPPED=HR扱い、パスで識別可)へ追記した(他agent差分と同居するためcommit対象外)。run_01のreview_lock・tts_generation_results・narrationは未変更(git差分で確認)。
- PRODUCTION_WIRED判定の材料: (a)コード・test配線=委任_01、(b)実音声での反映=本書§2(Advanced timeline/assembled wavからComment 2が消え、Standardは同一、gate PASS、page_verify ok、公開ページから行が消えたこと)。
