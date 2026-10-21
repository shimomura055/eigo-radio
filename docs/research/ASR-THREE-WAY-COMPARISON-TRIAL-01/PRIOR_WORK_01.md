# PRIOR_WORK_01 (ASR-THREE-WAY-COMPARISON-TRIAL-01 S0 Phase 0: 過去Trial・既存結果の再利用表)

読了範囲(全文読込禁止のSSOTは節/行単位Grep): `docs/research/FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01/TRIAL_RESULT_01.md`(全文)、`docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/KP_TAKE_PART_INVESTIGATION_01.md`(全文)、`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/WEIGHT_2_0_FACTCHECK_01.md`(冒頭〜§3)、`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/TRIAL_CLOSEOUT_01.md`(§1〜§2)、`er084_output/azure_phraselist_weight_trial_01/wav/manifest_01.json,manifest_02.json`、`OPEN_ITEMS.md`(試聴PASS記録行のGrep: 行914,917,928,934)。**未精読**: `BYUS_EQUIVALENCE_INVESTIGATION_01.md`、`FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01/`、`FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01/`(ラベル付き音声の供給源になりうるが、本Trialでは時間対効果から再利用せず。必要ならFable判断で追加)。

| 既存資産 | 再利用 | 内容 / 制約 |
|---|---|---|
| FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01(`er088_output/kp_asr_dual_pass_trial_01/results.jsonl`、`er088_kp_asr_dual_pass_trial_01.py`) | 転写10回分を保存値として再利用(Phase 3構成を適用=結果§I)。scriptはPhase 1/2の雛形(`er091_asr_three_way_trial_01_run.py`の方式別呼出) | 同一wav(take part旧NG、sha 675cd6b1…)を10回独立実行: Primary『part』x3/『tart』x6/『heart』x1、Azure 10/10 Tart、Whisper small 10/10 Tarte。**1音声の反復であり独立音声の証拠ではない** |
| FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01(OPEN-424、Fable判定REJECTED、ユーザーが重み2.0を採用=OPEN-426、`USER_DECISION_REGISTER_01.md:293` #126) | 音声15本(Melos正例6+負例Mello/Melon/Mullos 9、Aoede非減速)を`er084_output/azure_phraselist_weight_trial_01/wav/`から再利用 | 構成ラベル(TTSにその綴りを読ませた)。人間試聴ではない。旧Trialの副作用所見(w2.0で『Mullos』→『Melos』誤PASS)を本Trialで独立に再現(C1/C2: NM_P3,NM_P4) |
| 人間試聴済み記事(OPEN_ITEMS.md:917 Boredom、:928 Yemen-Saudi、:934 Melos) | KP30+本文24セグメントを正常ラベル源 | 記事全体の試聴PASS。**KP/セグメント単位の個別聴取ではない**ため『正常』ラベルの強度は中(take part事例のとおり個別見逃しは起こりうる)。記事A(Paycheck)・記事B(manga_ai_chat_byus)は試聴未了のため正常ラベルに使わない |
| `human_approved_segments.json`(HR承認) | EN 6件をHR承認難例として再利用(Melos drank/Melos said/Troy Meink/Toteme・Kallmeyer/Oimo no Cane/pool_n9 KP default) | 承認時wavと現存wavの同一性は未照合(承認hashはcanonical_text hash) |
| HR queue(`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`) | 不使用 | 解決済みラベル(status/resolution)フィールドが存在しない(全件キー: timestamp/canonical_text/wav_path/steps/final_status…)ため正解ラベル源にならない |
| Store内EN 333件中29件のASR間不一致リスト(KP_TAKE_PART_INVESTIGATION_01.md §5) | 不使用(ラベル不能) | 聴取者がいない状態では正誤を確定できず混同行列に入れられない。8.7%という上限目安のみ参考 |
| ER-008吃音QA教材(`er008_output/n7_*`)、`er006_output/pool_pilot_01/`、`er020/er021`のequivalence検証セット | 不使用 | 時間対効果。ラベルの出所確認(telemetry等)は未実施 |

## 既存仕様との整合(照合箇所)
- Primary PASSならSecondary不要・force_secondaryはfallback音声限定(CURRENT_SPEC.md:2808,2055: KP_TAKE_PART_INVESTIGATION_01.md §1が引用。本Trialでは再Grepせず二次引用)。Production判定関数は`er006_secondary_asr_01.py:730-`(`evaluate_attempt_with_cascade_detail`)、Secondary許容集合は`:993-1010`(`classify_asr_match`+`_step_alternate_pass`+M1)、統一judgeは`er078_asr_unified_judge_01.py:352-`(`unified_judge`、純関数でSecondaryは注入)。
- Azure Phrase List重み2.0は`er006_secondary_asr_01.py:75,106-111`(PL空なら未送信)。KP全て(`get_hint_for_text(min_confidence="low")`)でPL空であることを本Trialのmanifestで確認(KP 0件にLedger hint)。
