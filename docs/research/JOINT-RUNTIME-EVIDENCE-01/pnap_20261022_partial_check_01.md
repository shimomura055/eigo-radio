# 合同runtime evidence 集計(er106)
- schema: `er106_joint_runtime_evidence_01/v1` / generated_at: 2026-10-22T16:29:36
- X run: `er019_output/family_x_audio_production_wiring_01/pnap_evidence_01__small_bag__run_02` / Z run: `er026_output/family_z_production_e2e_01/melos/run_pnap_01`
- 状態語: OK / NG / MISSING(期待キー・成果物が無い=実装側の名称差または未配線。推測補完しない) / NOT_FIRED(自然発火せず) / MANUAL(機械判定不可) / INFO

## Family X: `er019_output/family_x_audio_production_wiring_01/pnap_evidence_01__small_bag__run_02` (levels=['b1b'])
- entry_point: {"present": false}
### (a) KP選定・件数
| level | n_items | backend(used) | model_id | prompt sha | sel/canon/red/outer | shortfall | 変更(原形化)件 | stale |
|---|---|---|---|---|---|---|---|---|
| b1b | 0 | None | gpt-5.6-luna | None | None/None/None/None | None | 0 | [] |
- b1b metadataの未存在キー: ['kp_backend', 'kp_backend_used', 'prompt_id', 'prompt_sha256', 'user_message_sha256', 'model_requested', 'shortfall', 'kp_count_max', 'attempts']
### (b) KP音声の3-ASR投票
| level | rank | 記録種別 | state | row | P | S | W発火 | W | W error | reused |
|---|---|---|---|---|---|---|---|---|---|---|
### (c) 固有名詞アラーム
- b1b: json=True md=True count=1 consistency={'alarm_state_records': 1, 'match': True, 'reported': 1} hr_residual={'available': True, 'hr_asr_uncertain_segments': 0, 'of_which_proper_noun_only_outside_alarm_boundary': 0} supply_applied=0
  - khaite @ full_story_part2: state=PASS_WITH_PRONUNCIATION_ALARM 供給={'evidence_tier': None, 'human_approved': False, 'ledger_id': None, 'original': 'khaite', 'policy_id': 'PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01', 'reason': 'EVIDENCE_NOT_VERIFIED_ESTIMATED', 'respelling': None, 'source_urls': [], 'supplied': False, 'tier': None} 根拠={'confidence': 'medium', 'evidence_tier': 'UNVERIFIED_AI_OUTPUT', 'has_basis': True, 'ipa': '\x02keɪt\x02', 'note': '', 'pronunciation_hint': 'KAYT', 'sources': ['https://www.farfetch.com/style-guide/brands/khaite-brand-everything-you-need-to-know', 'https://azzurrodue.com/khaite/', 'https://medium.com/@joycebirkins/khaite-cool-quirky-and-ethereal-style-4-year-runway-collection-and-10-classic-pieces-f2d95b0251df']}
### (d) 費用(JPY換算)
- 出典: `docs/pm/tools/daily_dev_cost_01.py`(USD_JPY=160.0、価格表 `er005_output/cost_baseline_01/pricing_snapshot.json`、cost_usd優先→tokens×単価、synthetic行は除外0件)。Whisperはローカル=0円(ログ対象外)。logs=['er019_output/family_x_audio_production_wiring_01/pnap_evidence_01__small_bag__run_02/raw_usage_log.jsonl']
- 合計 **7.9279円** / KP関連(chain+音声) 0.0円 (+未分離scaffold 0円を含めると 0.0円) / unpriced={}
| bucket | 円 | calls |
|---|---|---|
| non_kp_audio | 7.9279 | 9 |
| bucket:kind | 円 | calls |
|---|---|---|
| non_kp_audio:asr_azure | 4.7911 | 3 |
| non_kp_audio:asr_openai | 0.5178 | 3 |
| non_kp_audio:tts | 2.619 | 3 |
### (f) 試聴ページ・再生順
- pageが見つからない(--x-page/--z-pageで指定)
- b1b 再生順(間接: key_phrase_N長 >= 2*英+第3):  (timeline=False)

## Family Z: `er026_output/family_z_production_e2e_01/melos/run_pnap_01` (levels=['a2', 'b1b'])
### (a) KP選定・件数
| level | n_items | backend(used) | model_id | prompt sha | sel/canon/red/outer | shortfall | 変更(原形化)件 | stale |
|---|---|---|---|---|---|---|---|---|
| a2 | 5 | None | gpt-6-luna | None | None/1/1/3 | None | 4 | [] |
| b1b | 5 | None | gpt-6-luna | None | None/1/1/1 | None | 4 | [] |
- a2#1: span=`pulled him under` used=`pull someone under` (本文一致=True, 語数=3, gloss=True, reason=inherit_selection_normalization)
- a2#2: span=`in your place` used=`in someone's place` (本文一致=True, 語数=3, gloss=True, reason=generalize_person_dependent_reference)
- a2#3: span=`lost my trust in you` used=`lose trust in someone` (本文一致=True, 語数=5, gloss=True, reason=inherit_selection_normalization)
- a2#4: span=`held out` used=`hold out` (本文一致=True, 語数=2, gloss=True, reason=inherit_selection_normalization)
- a2#5: span=`far bank` used=`far bank` (本文一致=True, 語数=2, gloss=True, reason=none)
- a2 metadataの未存在キー: ['kp_backend', 'kp_backend_used', 'prompt_id', 'prompt_sha256', 'user_message_sha256', 'model_requested', 'shortfall', 'kp_count_max', 'attempts']
- b1b#1: span=`sentenced him to death` used=`sentence someone to death` (本文一致=True, 語数=4, gloss=True, reason=inherit_selection_normalization)
- b1b#2: span=`current` used=`current` (本文一致=True, 語数=1, gloss=True, reason=none)
- b1b#3: span=`held out his hands` used=`hold out` (本文一致=True, 語数=4, gloss=True, reason=inherit_selection_normalization)
- b1b#4: span=`seized` used=`seize` (本文一致=True, 語数=1, gloss=True, reason=inherit_selection_normalization)
- b1b#5: span=`abandoned` used=`abandon` (本文一致=True, 語数=1, gloss=True, reason=inherit_selection_normalization)
- b1b metadataの未存在キー: ['kp_backend', 'kp_backend_used', 'prompt_id', 'prompt_sha256', 'user_message_sha256', 'model_requested', 'shortfall', 'kp_count_max', 'attempts']
### (b) KP音声の3-ASR投票
| level | rank | 記録種別 | state | row | P | S | W発火 | W | W error | reused |
|---|---|---|---|---|---|---|---|---|---|---|
### (c) 固有名詞アラーム
- a2: json=True md=True count=0 consistency={'alarm_state_records': 0, 'match': True, 'reported': 0} hr_residual={'available': True, 'hr_asr_uncertain_segments': 0, 'of_which_proper_noun_only_outside_alarm_boundary': 0} supply_applied=0
- b1b: json=True md=True count=0 consistency={'alarm_state_records': 0, 'match': True, 'reported': 0} hr_residual={'available': True, 'hr_asr_uncertain_segments': 0, 'of_which_proper_noun_only_outside_alarm_boundary': 0} supply_applied=0
### (d) 費用(JPY換算)
- 出典: `docs/pm/tools/daily_dev_cost_01.py`(USD_JPY=160.0、価格表 `er005_output/cost_baseline_01/pricing_snapshot.json`、cost_usd優先→tokens×単価、synthetic行は除外0件)。Whisperはローカル=0円(ログ対象外)。logs=['er026_output/family_z_production_e2e_01/melos/run_pnap_01/cost_log.jsonl']
- 合計 **3.2191円** / KP関連(chain+音声) 0.0円 (+未分離scaffold 0円を含めると 0.0円) / unpriced={}
| bucket | 円 | calls |
|---|---|---|
| non_kp_audio | 3.2191 | 31 |
| bucket:kind | 円 | calls |
|---|---|---|
| non_kp_audio:asr_azure | 1.3751 | 10 |
| non_kp_audio:asr_openai | 0.3268 | 12 |
| non_kp_audio:tts | 1.5172 | 9 |
### (f) 試聴ページ・再生順
- pageが見つからない(--x-page/--z-pageで指定)
- a2 再生順(間接: key_phrase_N長 >= 2*英+第3):  (timeline=False)
- b1b 再生順(間接: key_phrase_N長 >= 2*英+第3):  (timeline=False)

## (e) STOP・HR・共有log
- STOPセンチネル(現在): ['C:/Users/tensh/eigo-radio/docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md']
- 前後差分: snapshot未指定
- Ledger対象語照合: {"khaite": [{"surface": "khaite", "evidence_tier": "MISSING", "human_approved": true, "tts_respelling": "Kate", "pronunciation_hint": "KAYT", "ledger_disabled": null}]}

## KPFT(KP全文選定+3件化) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| KPFT-1 全文直接選定(候補DBでない) | MISSING | MISSING | b1b:MISSING(kp_backend=None used=None db_hybrid_dir=False) / a2:MISSING(kp_backend=None used=None db_hybrid_dir=False); b1b:MISSING(kp_backend=None used=None db_hybrid_dir=False) |
| KPFT-2 actual model ID=gpt-6-luna | NG | OK | b1b:NG(model_id=gpt-5.6-luna requested=None) / a2:OK(model_id=gpt-6-luna requested=None); b1b:OK(model_id=gpt-6-luna requested=None) |
| KPFT-3 正式Prompt 2のsha | MISSING | MISSING | b1b:MISSING(prompt_sha256=None) / a2:MISSING(prompt_sha256=None); b1b:MISSING(prompt_sha256=None) |
| KPFT-4 KP最大3件 | MISSING | NG | b1b:MISSING(n_items=0 shortfall=None (期待3, 1-2はshortfall記録つきで許容)) / a2:NG(n_items=5 shortfall=None (期待3, 1-2はshortfall記録つきで許容)); b1b:NG(n_items=5 shortfall=None (期待3, 1-2はshortfall記録つきで許容)) |
| KPFT-5 本文外/6語以上が不採用 | MISSING | OK | b1b:MISSING(items無し) / a2:OK(本文不一致/6語以上のrank=[] (全5件のsource_span本文一致+<=5語)); b1b:OK(本文不一致/6語以上のrank=[] (全5件のsource_span本文一致+<=5語)) |
| KPFT-6 原形化・一般化 | MISSING | INFO | b1b:MISSING(items無し) / a2:INFO(変更4件(要:聴取/目視で一般化の妥当性確認): [(1, 'pulled him under', 'pull someone under', 'inherit_selection_normalization'), (2, 'in your place', "in someone's place", 'generalize_person_de |
| KPFT-7 後段(意味/解説/音声/ASR/組立) | MISSING | NG | b1b:MISSING(timeline無し(assemble未実施?) 未OK=[]) / a2:NG(timeline無し(assemble未実施?) 未OK=['kp1.english', 'kp2.english', 'kp3.english', 'kp4.english', 'kp5.english']); b1b:NG(timeline無し(assemble未実施?) 未OK=['kp1.english', 'kp2.english',  |
| KPFT-8 retry/fallback/regen/resume | INFO | INFO | b1b:INFO(選定None/2 canonNone/2 redNone(None) outerNone/3 stale=[] fallback_notice=False) / a2:INFO(選定None/2 canon1/2 red1(REDUNDANCY_PASS) outer3/3 stale=[] fallback_notice=False); b1b:INFO(選定None/2 canon1/2 red1(REDUNDANCY_PASS) outer1/3 stale=[] fallback_notice=False) |
| KPFT-9 旧DB/5件のDangling Reference | MANUAL | MANUAL | --dangling-grep で別途集計(下記)。run出力からは判定しない / --dangling-grep で別途集計(下記)。run出力からは判定しない |
| KPFT-10 必須Regression/Validator/test | MANUAL | MANUAL | 当日手順書の事前チェック(全回帰PASS)で確認 / 当日手順書の事前チェック(全回帰PASS)で確認 |
| KPFT-11 X/Z双方の正式runtime evidence | INFO | INFO | levels=['b1b'] / levels=['a2', 'b1b'] |
| KPFT-12 SSOT/Git | MANUAL | MANUAL | Fable受入時 / Fable受入時 |

## KP3V(3-ASR多数決) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| KP3V-0 KP英語voteの存在 | MISSING | MISSING | KP英語音声のresultsが無い / KP英語音声のresultsが無い |
| KP3V-J Whisper正式runtime発火(X/Zいずれか) | (合同) | (合同) | NOT_FIRED: X=False Z=False。双方未発火なら『Xで発火観測+Z同adapterをtestで固定』は不成立→別素材で追加run(設計P-06) |

## PNAP(固有名詞アラーム) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| PNAP-0 audit/pronunciation_alarms.json と operator_alarm_report.md の生成 | OK | OK | levels=['b1b'] json=['b1b'] / levels=['a2', 'b1b'] json=['a2', 'b1b'] |
| PNAP-0b 期待キー不一致(payload/record) | OK | OK | payload_missing=[] record_missing=[] / payload_missing=[] record_missing=[] |
| PNAP-6 アラームが完成報告へ引継ぎ(集計一致P-08) | OK | OK | consistency=[('b1b', {'alarm_state_records': 1, 'match': True, 'reported': 1})] / ALARM state segments(results)={'b1b': ['full_story_part2']} / consistency=[('a2', {'alarm_state_records': 0, 'match': True, 'reported': 0}), ('b1b', {'alarm_state_records': 0, 'match': True, 'reported': 0})] / ALARM state segments(results)={' |
| PNAP-2 不一致時にアラーム記録+制作継続(発火証拠) | OK | NOT_FIRED | alarms=1件 nouns=['khaite'](0件=自然発火せず。再実行は別素材へ。設計§10) / alarms=0件 nouns=[](0件=自然発火せず。再実行は別素材へ。設計§10) |
| PNAP-2b アラーム記録の必須項目(固有名詞/箇所/不一致/根拠/TTS供給結果/最終状態/models) | OK | NOT_FIRED | 欠落=[] / 欠落=[] |
| PNAP-3 固有名詞不一致のみでHRに回らない | MANUAL | MANUAL | snapshot未指定のためHR queue/attempt_history前後比較不可。非RESOLVED lock={} / snapshot未指定のためHR queue/attempt_history前後比較不可。非RESOLVED lock={} |
| PNAP-1 発音情報取得・TTS供給(respelling)の発火記録 | OK | NOT_FIRED | results内supply記録(非空)=2 / payload.supply_applied=0 / results内supply記録(非空)=0 / payload.supply_applied=0 |
| PNAP-1b Ledger evidence_tier/human_approved | INFO | INFO | 対象語=['khaite'] Ledger一致={'khaite': [{'surface': 'khaite', 'evidence_tier': 'MISSING', 'human_approved': True, 'tts_respelling': 'Kate', 'pronunciation_hint': 'KAYT', 'ledger_disabl / 対象語=[] Ledger一致={} |
| PNAP-4 通常ASR/retry/fallback/regen/resume整合 | INFO | INFO | tts_generation_results.segments statusとattempts: {'b1b': {'topic_intro': 'SKIPPED_NOT_SELECTED', 'preview': 'SKIPPED_NOT_SELECTED', 'comment_1': 'SKIPPED_NOT_SELECTED', 'comment_2' / tts_generation_results.segments statusとattempts: {'a2': {'full_story_part1_c1': 'OK', 'full_story_part1_c5': 'OK', 'full_story_part3_c3': 'OK'}, 'b1b': {'full_story_part1_c1': 'OK' |
| PNAP-5 固有名詞以外の不一致は従来どおり | MANUAL | MANUAL | アラーム対象外のNG/HRが従来どおり残るかは、HR residual(payload.hr_residual)で確認: {'b1b': {'available': True, 'hr_asr_uncertain_segments': 0, 'of_which_proper_noun_only_outside_alarm_boundary': 0}} / アラーム対象外のNG/HRが従来どおり残るかは、HR residual(payload.hr_residual)で確認: {'a2': {'available': True, 'hr_asr_uncertain_segments': 0, 'of_which_proper_noun_only_outside_alarm_boundary': 0}, 'b1b |
| PNAP-7 一般リスナー(公開ページ)に非露出 | MISSING | MISSING | leaks=[] pages=[] / leaks=[] pages=[] |
| PNAP-8 KP segmentにアラーム受理が適用されていない(範囲外) | OK | OK | KP alarm segments=[] / KP alarm segments=[] |
| PNAP-9 必須Regression/Validator/test | MANUAL | MANUAL | 当日手順書の事前チェック / 当日手順書の事前チェック |
| PNAP-J アラーム発火(X・Z双方、PNAP原文§5-9) | (合同) | (合同) | NOT_FIRED: alarms X=1 Z=0 |

## 総括
- KPFT: {'MISSING': 8, 'NG': 3, 'INFO': 5, 'MANUAL': 6, 'OK': 2}
- KP3V: {'MISSING': 2, 'NOT_FIRED': 1}
- PNAP: {'OK': 11, 'MANUAL': 6, 'INFO': 4, 'MISSING': 2, 'NOT_FIRED': 4}
