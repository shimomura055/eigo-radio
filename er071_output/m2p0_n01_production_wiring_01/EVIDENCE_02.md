# EVIDENCE_02 (FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_03、2026-10-13)

機械可読版: `evidence_02.json` / `cost_03.json` / `coffee_evidence_02/pages_play_evidence_03.json`。run dir: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01`。

## 0. STOP確認・モデル
開始時: `*STOP_NOTICE*`は2026-10-12 Melos旧記録のみ(本件非適用)、Coffee run dir/`er026_output/family_z_production_e2e_01/`に`STOP`/`STOP_ALL`なし、`.git/index.lock`なし。使用モデル: KP=gpt-6-luna(本番既定・最新ライン)。本委任でTTS/ASR呼出なし。

## A. Fallback通知経路(ユーザー受入条件)
既存パターン(run dir内notice file+run summary+標準出力)のみで実装。新通知仕様は不要=未実装要素なし。
1. 検知: `_run_key_phrase_selection_db_hybrid_with_fallback`(`er003_v1_n3_01_scaffold_generate.py`)のDbHybridFailure fallback分岐で`build_m2_fallback_record`を生成(`m2_related`=M2_SUPPLY_EXCEPTION/SELECTOR_EXCEPTIONのとき真。SHORTLIST_TOO_SMALL等の他のDB Hybrid→Strategy L fallbackも区別しつつ報告対象)。`run_key_phrases`はwrapper化し、retry全attemptのeventを`m2_fallback_events`で返す。
2. summary: `scaffold_run_summary.json[level].m2_fallback`(最新1件またはnull)/`m2_fallback_events`(全件)、`entry_point.json.m2_fallback_by_level`。keys=family/article/level/stage/reason_code/reason/fallback_result/m2_related/kp_supply_actual/note。
3. notice file: run dir直下`M2_FALLBACK_NOTICE.md`(STOP_NOTICEと同パターン、「M2P0正常動作ではない・ユーザーへ必ず報告」明記)。
4. stdout: scaffold中に`[M2-FALLBACK][NOTICE]`ブロック、runner終了時に常時`[M2-FALLBACK]`1行(発生なし/発生あり+notice path)。
5. 報告義務: CURRENT_SPEC M2供給節+OPEN-347に記録(PM_GOVERNANCEは編集せず)。通知を受けて**ユーザーへ報告する主体はFable/PM**(Production運用では`M2_FALLBACK_NOTICE.md`/stdout/summaryでユーザーが把握可能)。
6. Family Z: `er063`/`er026`のKPは`sc.run_key_phrases(strategy_l既定)`を使うためM2経路なし。同じ`run_key_phrases`戻り値に`m2_fallback_events=[]`が追記される(summaryキー契約のみ・Z挙動は不変)。将来のZ移行Trial/Productionで同じ契約を共有できる(test `test_family_z_contract...`)。
7. test(synthetic/mock、API呼出なし): `er030_key_phrase_db_hybrid_m2_fallback_notice_01_test_01.py` 6件OK(M2_SUPPLY_EXCEPTION/SELECTOR_EXCEPTION/他理由/発生なし/Zキー契約/summary+notice+stdoutの3点)。
8. 委任_02/03のCoffee runでM2→Strategy L fallbackが発生したか: **発生なし**。`er030_output/kp_backend_telemetry_01/telemetry.jsonl`のa2/b1b/a2再生成の3行すべて`backend_used=db_hybrid, fallback_triggered=false, kp_supply=m2`。Std失敗はcanonicalization段(M2 fallbackではない)。※委任_02のrunは本実装前のため`M2_FALLBACK_NOTICE.md`/stdout行は存在しない(telemetryが根拠)。

## B. Coffee Standard完走(結果: Std KPがまたINVALID、STOP)
1. Std KP再生成1 job(約JPY1.07): `--stage scaffold --scaffold-only kp --level a2`。既存`a2/key_phrases`は`a2/key_phrases_d02_attempt_invalid`へ退避(上書きしない)。結果=**CANONICALIZATION_INVALID**(委任_02と同じrank5『based on』→『based on interviews』、Rule7、既存retry各2回=通算4回不合格)。M2供給は発火(kp_supply=m2、M2 15.8秒、fallbackなし)。KP selection段は同じ`based on`を再選択=確定的な再発。→委任文どおり**再実行せずSTOP**(OPEN-310/343/346、UDR)。
2. Std KP音声: 未実行(KP INVALID)。
3. Std Full Story: part1/3はN01合格のまま(再生成なし)。part2は再生成なし。試聴ページへfallback take(N01でない、198.2WPM=EVIDENCE_01)と「N01 attempt1(ASR不合格・減速前の生音声)」を参考掲載。
4. Adv正式assemble(`--stage assemble --level b1b`): **BLOCK**(`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`: topic_intro/preview/comment_1-4/in_one_line=UNVALIDATED)。原因=新out_dirにはFull Story+KPしか生成しておらず、v5承認済みの再利用segmentはsha一致でseed(`audit/seed_provenance_03_assemble.json`、16 role)してもtts_generation_results上は`SKIPPED_NOT_SELECTED`(OPEN-346②)でGateにUNVALIDATEDとされる。**Gateは迂回していない**(results entryの手編集・Gate緩和なし)。Std assemble: 不可(Std KP INVALID+M3 Gate part2 BLOCK)。→Checklist 5/11未充足。完走手段はユーザー判断(OPEN-343 (c))。
5. 試聴ページ更新: https://shimomura055.github.io/eigo-radio/user_test/coffee_m2p0_n01_01/index.html 。Adv完成版(Trial assembler版、開示を更新)、Std Full Story 3part、Std part2 N01 attempt1参考clip。Playwright(公開Pages上の実再生): 29/29再生OK、seek OK、console error 0、http>=400 0、file:///なし(`coffee_evidence_02/pages_play_evidence_03.json`)。
6. 速度・ポーズ: Std KP音声/Adv assemble後の新音声が無いため実測値は更新なし(`coffee_evidence_02/speed_pause_02.json`のまま。Std 168WPM/Adv 178WPM)。

## C. 費用・時間
本委任のAPI費用=JPY1.07(Std KP再生成 openai 3.13-2.06)。run dir累計JPY26.77(委任_02 25.70+1.07)。runnerのguardはrun dir累計基準のため`--budget-jpy 55.7`(=25.70+本委任cap30)を指定(委任文の`--budget-jpy 30`だとrun dir累計25.70で上限が即時近接するため。本委任の増分cap30はJPY1.07で未到達)。有料run再起動0回、外部停止0、原因不明rc!=0 0回(Adv assemble rc=1はGateによる想定内のBLOCK、API呼出なし)。

## D. 回帰
er030 108/108(102+新6)/er019 357/er063 59/er026 107(並行regression同時実行でstate_guard 1件失敗→単独再実行で全PASS)。

## E. 全体regression(`run_project_regression.py`全件)
collected=6071 passed=6040 failed=15 errors=12 skipped=4。失敗27件のうち、変更ファイル(`er003_v1_n3_01_scaffold_generate.py`/`er019_family_x_audio_production_runner_01.py`)と関連しうるer025(runner kwarg)・er068・er054・er011_open112・er006を、変更前commit 5da8ac79のworktreeで同じtestを実行して**変更前から同じ失敗**であることを確認(er025:error1/er068:failure1/er054:1/er011:3/er006:1)。残り(er003_test_bad/p2j、er008、er015、er020、er040/043、er053、er064_*、er069/070/074)は変更ファイルをimport/変更していない領域(個別のbaseline比較は未実施=未照合)。M2供給・Fallback通知・runnerに関わる回帰(er030 108/er019 357/er063 59/er026 107)は全PASS。
