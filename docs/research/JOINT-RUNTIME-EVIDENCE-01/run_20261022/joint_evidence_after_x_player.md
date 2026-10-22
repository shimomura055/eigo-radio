# 合同runtime evidence 集計(er106)
- schema: `er106_joint_runtime_evidence_01/v1` / generated_at: 2026-10-22T17:45:54
- X run: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_jre_01` / Z run: `er026_output/family_z_production_e2e_01/melos/run_jre_01`
- 状態語: OK / NG / MISSING(期待キー・成果物が無い=実装側の名称差または未配線。推測補完しない) / NOT_FIRED(自然発火せず) / MANUAL(機械判定不可) / INFO

## Family X: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_jre_01` (levels=['a2', 'b1b'])
- entry_point: {"kp_backend_used_by_level": null, "m2_fallback_by_level": null, "kp_stage_status": null, "tts_backend": "speech_metadata_flash_lite", "stage": "player", "present": true}
### (a) KP選定・件数
| level | n_items | backend(used) | model_id | prompt sha | sel/canon/red/outer | shortfall | 変更(原形化)件 | stale |
|---|---|---|---|---|---|---|---|---|
| a2 | 3 | fulltext_p2 | gpt-6-luna | a12896f48560 | 1/1/1/1 | False | 2 | [] |
| b1b | 3 | fulltext_p2 | gpt-6-luna | a12896f48560 | 1/1/1/2 | False | 2 | [] |
- a2#1: span=`pumps its fist` used=`pump one's fist` (本文一致=True, 語数=3, gloss=True, reason=generalize_person_dependent_reference)
- a2#2: span=`on a regular basis` used=`on a regular basis` (本文一致=True, 語数=4, gloss=True, reason=none)
- a2#3: span=`pushed prices up` used=`push prices up` (本文一致=True, 語数=3, gloss=True, reason=lemma_normalization)
- b1b#1: span=`pumps its fist` used=`pump one's fist` (本文一致=True, 語数=3, gloss=True, reason=generalize_person_dependent_reference)
- b1b#2: span=`a time lag` used=`time lag` (本文一致=True, 語数=3, gloss=True, reason=remove_contextual_determiner)
- b1b#3: span=`behind price increases` used=`behind price increases` (本文一致=True, 語数=3, gloss=True, reason=none)
### (b) KP音声の3-ASR投票
| level | rank | 記録種別 | state | row | P | S | W発火 | W | W error | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| a2 | 1 | vote_check_v1 | None | None | False | False | False | None | None | False |
| a2 | 2 | vote_check_v1 | None | P+S | True | True | False | None | None | False |
| a2 | 3 | vote_check_v1 | None | P+S | True | True | False | None | None | False |
| b1b | 1 | vote_check_v1 | None | None | False | False | False | None | None | False |
| b1b | 2 | vote_check_v1 | None | P+S | True | True | False | None | None | False |
| b1b | 3 | vote_check_v1 | None | P+S | True | True | False | None | None | False |
### (c) 固有名詞アラーム
- a2: json=True md=True count=0 consistency={'alarm_state_records': 0, 'match': True, 'reported': 0} hr_residual={'available': True, 'hr_asr_uncertain_segments': 0, 'of_which_proper_noun_only_outside_alarm_boundary': 0} supply_applied=0
- b1b: json=True md=True count=0 consistency={'alarm_state_records': 0, 'match': True, 'reported': 0} hr_residual={'available': True, 'hr_asr_uncertain_segments': 0, 'of_which_proper_noun_only_outside_alarm_boundary': 0} supply_applied=0
### (d) 費用(JPY換算)
- 出典: `docs/pm/tools/daily_dev_cost_01.py`(USD_JPY=160.0、価格表 `er005_output/cost_baseline_01/pricing_snapshot.json`、cost_usd優先→tokens×単価、synthetic行は除外0件)。Whisperはローカル=0円(ログ対象外)。logs=['er019_output/family_x_audio_production_wiring_01/coffee_prices__run_jre_01/raw_usage_log.jsonl']
- 合計 **24.213円** / KP関連(chain+音声) 2.4483円 (+未分離scaffold 1.6747円を含めると 4.123円) / unpriced={}
| bucket | 円 | calls |
|---|---|---|
| kp_audio_english | 1.6147 | 36 |
| kp_audio_explanation | 0.3399 | 6 |
| kp_audio_ja_meaning | 0.2028 | 6 |
| kp_chain | 0.2909 | 3 |
| non_kp_audio | 20.0687 | 51 |
| other | 0.0214 | 1 |
| scaffold_llm_unsplit | 1.6747 | 19 |
| bucket:kind | 円 | calls |
|---|---|---|
| kp_audio_english:asr_azure | 0.9022 | 12 |
| kp_audio_english:asr_openai | 0.2034 | 12 |
| kp_audio_english:tts | 0.5091 | 12 |
| kp_audio_explanation:asr_openai | 0.0764 | 3 |
| kp_audio_explanation:tts | 0.2635 | 3 |
| kp_audio_ja_meaning:asr_openai | 0.0372 | 3 |
| kp_audio_ja_meaning:tts | 0.1656 | 3 |
| kp_chain:llm | 0.2909 | 3 |
| non_kp_audio:asr_azure | 6.9192 | 4 |
| non_kp_audio:asr_openai | 2.8306 | 25 |
| non_kp_audio:llm | 0.0224 | 1 |
| non_kp_audio:tts | 10.2965 | 21 |
| other:llm | 0.0214 | 1 |
| scaffold_llm_unsplit:llm | 1.6747 | 19 |
### (f) 試聴ページ・再生順
- page `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_jre_01/player.html`: 標準適合=None failed=None KP行=None アラーム語漏れ=[]
- a2 再生順(間接: key_phrase_N長 >= 2*英+第3):  (timeline=False)
- b1b 再生順(間接: key_phrase_N長 >= 2*英+第3):  (timeline=False)

## Family Z: `er026_output/family_z_production_e2e_01/melos/run_jre_01` (levels=['a2', 'b1b'])
### (a) KP選定・件数
| level | n_items | backend(used) | model_id | prompt sha | sel/canon/red/outer | shortfall | 変更(原形化)件 | stale |
|---|---|---|---|---|---|---|---|---|
| a2 | 3 | fulltext_p2 | gpt-6-luna | a12896f48560 | 1/1/1/1 | False | 2 | [] |
| b1b | 3 | fulltext_p2 | gpt-6-luna | a12896f48560 | 1/1/1/1 | False | 1 | [] |
- a2#1: span=`in your place` used=`in someone's place` (本文一致=True, 語数=3, gloss=True, reason=generalize_person_dependent_reference)
- a2#2: span=`held out` used=`hold out` (本文一致=True, 語数=2, gloss=True, reason=lemma_normalization)
- a2#3: span=`For once` used=`For once` (本文一致=True, 語数=2, gloss=True, reason=none)
- b1b#1: span=`sentenced him to death` used=`sentence him to death` (本文一致=True, 語数=4, gloss=True, reason=lemma_normalization)
- b1b#2: span=`without asking for another promise` used=`without asking for another promise` (本文一致=True, 語数=5, gloss=True, reason=none)
- b1b#3: span=`earn such trust` used=`earn such trust` (本文一致=True, 語数=3, gloss=True, reason=none)
### (b) KP音声の3-ASR投票
| level | rank | 記録種別 | state | row | P | S | W発火 | W | W error | reused |
|---|---|---|---|---|---|---|---|---|---|---|
### (c) 固有名詞アラーム
- a2: json=False md=False count=None consistency=None hr_residual=None supply_applied=None
- b1b: json=False md=False count=None consistency=None hr_residual=None supply_applied=None
### (d) 費用(JPY換算)
- 出典: `docs/pm/tools/daily_dev_cost_01.py`(USD_JPY=160.0、価格表 `er005_output/cost_baseline_01/pricing_snapshot.json`、cost_usd優先→tokens×単価、synthetic行は除外0件)。Whisperはローカル=0円(ログ対象外)。logs=['er026_output/family_z_production_e2e_01/melos/run_jre_01/cost_log.jsonl']
- 合計 **4.9992円** / KP関連(chain+音声) 3.2535円 (+未分離scaffold 0円を含めると 3.2535円) / unpriced={}
| bucket | 円 | calls |
|---|---|---|
| kp_audio_english | 0.4866 | 9 |
| kp_audio_explanation | 0.3669 | 6 |
| kp_chain | 2.4 | 19 |
| non_kp_audio | 1.7457 | 15 |
| bucket:kind | 円 | calls |
|---|---|---|
| kp_audio_english:asr_azure | 0.2747 | 3 |
| kp_audio_english:asr_openai | 0.0562 | 3 |
| kp_audio_english:tts | 0.1558 | 3 |
| kp_audio_explanation:asr_openai | 0.081 | 3 |
| kp_audio_explanation:tts | 0.2859 | 3 |
| kp_chain:llm | 2.4 | 19 |
| non_kp_audio:asr_azure | 0.1191 | 1 |
| non_kp_audio:asr_openai | 0.215 | 7 |
| non_kp_audio:tts | 1.4116 | 7 |
### (f) 試聴ページ・再生順
- pageが見つからない(--x-page/--z-pageで指定)
- a2 再生順(間接: key_phrase_N長 >= 2*英+第3):  (timeline=False)
- b1b 再生順(間接: key_phrase_N長 >= 2*英+第3):  (timeline=False)

## (e) STOP・HR・共有log
- STOPセンチネル(現在): ['C:/Users/tensh/eigo-radio/docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md']
- 前後差分: snapshot未指定
- Ledger対象語照合: {}

## KPFT(KP全文選定+3件化) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| KPFT-1 全文直接選定(候補DBでない) | OK | OK | a2:OK(kp_backend=fulltext_p2 used=fulltext_p2 db_hybrid_dir=False); b1b:OK(kp_backend=fulltext_p2 used=fulltext_p2 db_hybrid_dir=False) / a2:OK(kp_backend=fulltext_p2 used=fulltext_p2 db_hybrid_dir=False); b1b:OK(kp_backend=fulltext_p2 used=fulltext_p2 db_hybrid_dir=False) |
| KPFT-2 actual model ID=gpt-6-luna | OK | OK | a2:OK(model_id=gpt-6-luna requested=gpt-6-luna); b1b:OK(model_id=gpt-6-luna requested=gpt-6-luna) / a2:OK(model_id=gpt-6-luna requested=gpt-6-luna); b1b:OK(model_id=gpt-6-luna requested=gpt-6-luna) |
| KPFT-3 正式Prompt 2のsha | OK | OK | a2:OK(prompt_sha256=a12896f485604f32); b1b:OK(prompt_sha256=a12896f485604f32) / a2:OK(prompt_sha256=a12896f485604f32); b1b:OK(prompt_sha256=a12896f485604f32) |
| KPFT-4 KP最大3件 | OK | OK | a2:OK(n_items=3 shortfall=False (期待3, 1-2はshortfall記録つきで許容)); b1b:OK(n_items=3 shortfall=False (期待3, 1-2はshortfall記録つきで許容)) / a2:OK(n_items=3 shortfall=False (期待3, 1-2はshortfall記録つきで許容)); b1b:OK(n_items=3 shortfall=False (期待3, 1-2はshortfall記録つきで許容)) |
| KPFT-5 本文外/6語以上が不採用 | OK | OK | a2:OK(本文不一致/6語以上のrank=[] (全3件のsource_span本文一致+<=5語)); b1b:OK(本文不一致/6語以上のrank=[] (全3件のsource_span本文一致+<=5語)) / a2:OK(本文不一致/6語以上のrank=[] (全3件のsource_span本文一致+<=5語)); b1b:OK(本文不一致/6語以上のrank=[] (全3件のsource_span本文一致+<=5語)) |
| KPFT-6 原形化・一般化 | INFO | INFO | a2:INFO(変更2件(要:聴取/目視で一般化の妥当性確認): [(1, 'pumps its fist', "pump one's fist", 'generalize_person_dependent_reference'), (3, 'pushed prices up', 'push prices up', 'lemma_normalization' / a2:INFO(変更2件(要:聴取/目視で一般化の妥当性確認): [(1, 'in your place', "in someone's place", 'generalize_person_dependent_reference'), (2, 'held out', 'hold out', 'lemma_normalization')]); b1b:INF |
| KPFT-7 後段(意味/解説/音声/ASR/組立) | NG | MISSING | a2:NG(timeline無し(assemble未実施?) 未OK=['kp1.english']); b1b:NG(timeline無し(assemble未実施?) 未OK=['kp1.english']) / a2:MISSING(tts_generation_results.json無し); b1b:MISSING(tts_generation_results.json無し) |
| KPFT-8 retry/fallback/regen/resume | INFO | INFO | a2:INFO(選定1/2 canon1/2 red1(REDUNDANCY_PASS) outer1/3 stale=[] fallback_notice=False); b1b:INFO(選定1/2 canon1/2 red1(REDUNDANCY_PASS) outer2/3 stale=[] fallback_notice=False) / a2:INFO(選定1/2 canon1/2 red1(REDUNDANCY_PASS) outer1/3 stale=[] fallback_notice=False); b1b:INFO(選定1/2 canon1/2 red1(REDUNDANCY_PASS) outer1/3 stale=[] fallback_notice=False) |
| KPFT-9 旧DB/5件のDangling Reference | MANUAL | MANUAL | --dangling-grep で別途集計(下記)。run出力からは判定しない / --dangling-grep で別途集計(下記)。run出力からは判定しない |
| KPFT-10 必須Regression/Validator/test | MANUAL | MANUAL | 当日手順書の事前チェック(全回帰PASS)で確認 / 当日手順書の事前チェック(全回帰PASS)で確認 |
| KPFT-11 X/Z双方の正式runtime evidence | INFO | INFO | levels=['a2', 'b1b'] / levels=['a2', 'b1b'] |
| KPFT-12 SSOT/Git | MANUAL | MANUAL | Fable受入時 / Fable受入時 |

## KP3V(3-ASR多数決) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| KP3V-0 KP英語voteの存在 | OK | MISSING | new=6 legacy_dual=0 missing=0 (旧dual/証跡無しが残る=新判定が通っていない) / KP英語音声のresultsが無い |
| KP3V-0b 期待キー不一致 | MISSING | - | missing_keys=['canonical_text', 'checked_at', 'judge_state', 'ok', 'reason_code', 'source', 'vote_state', 'wav_sha256'](実装側の名称が設計書と違う可能性。推測補完しない) /  |
| KP3V-1 割れた場合のみWhisper発動 | OK | - | split(P!=S)=0 whisper_fired=0 割れ無しで発火(I1違反)=[] 割れたのに未発火=[] /  |
| KP3V-1b Whisperの自然発火(発火証拠) | NOT_FIRED | - | 割れが発生しなかった場合は NOT_FIRED(自然発火待ち。保存wavのreplayは正式runtime証拠に当たらない=PNAP設計§10と同じ扱い) /  |
| KP3V-1c Whisper事前確認(preflight)の記録(設計§16-1 P-08) | MISSING | - | 記録を含むファイル=[](名称は配線後に確認。無い場合は実装側の記録先を確認) /  |
| KP3V-2 2/3 PASSで正常終了 | NOT_FIRED | - | PASS_VOTE_2OF3=0件 rank=[] /  |
| KP3V-3 2/3 NGは従来どおりNG | INFO | - | NG系state=0件(最終採用wavがNG stateでないかはKP3V-4/invariantsで検査。NG attemptはattempts履歴側) /  |
| KP3V-4 Whisper error/未利用でPASSにしない(不変条件I1-I7) | OK | - | 6件の投票記録でI1-I7違反なし /  |
| KP3V-4b Whisper構成(small/int8) | NOT_FIRED | - | observed=[] /  |
| KP3V-5 retry/fallback/regen/resumeへの一貫適用 | INFO | - | 再利用(reused=True)のvote=[] / attempts={'a2#1': None, 'a2#2': None, 'a2#3': None, 'b1b#1': None, 'b1b#2': None, 'b1b#3': None} /  |
| KP3V-6 Store再利用時にも新判定 | NOT_FIRED | - | reused=0件 /  |
| KP3V-7 KP英語解説・その他音声に影響なし(voteの証跡が英語phrase以外に付かない) | NG | - | 英語phrase以外にvote証跡が付いた箇所=[('b1b', 'kp2.phrase_repeat'), ('b1b', 'kp3.phrase_repeat')] /  |
| KP3V-8 固有名詞アラームとの適用範囲整合 | INFO | - | KP segmentにPNAPアラーム状態が付いていないこと: PNAP側のKP混入検査を参照 /  |
| KP3V-9 X/Z双方の正式runtime evidence | INFO | - | levels=['a2', 'b1b'] /  |
| KP3V-J Whisper正式runtime発火(X/Zいずれか) | (合同) | (合同) | NOT_FIRED: X=False Z=False。双方未発火なら『Xで発火観測+Z同adapterをtestで固定』は不成立→別素材で追加run(設計P-06) |

## PNAP(固有名詞アラーム) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| PNAP-0 audit/pronunciation_alarms.json と operator_alarm_report.md の生成 | OK | MISSING | levels=['a2', 'b1b'] json=['a2', 'b1b'] / levels=['a2', 'b1b'] json=[] |
| PNAP-0b 期待キー不一致(payload/record) | OK | MISSING | payload_missing=[] record_missing=[] / payload_missing=[] record_missing=[] |
| PNAP-6 アラームが完成報告へ引継ぎ(集計一致P-08) | OK | MISSING | consistency=[('a2', {'alarm_state_records': 0, 'match': True, 'reported': 0}), ('b1b', {'alarm_state_records': 0, 'match': True, 'reported': 0})] / ALARM state segments(results)={' / consistency=[('a2', None), ('b1b', None)] / ALARM state segments(results)={'a2': None, 'b1b': None} |
| PNAP-2 不一致時にアラーム記録+制作継続(発火証拠) | NOT_FIRED | NOT_FIRED | alarms=0件 nouns=[](0件=自然発火せず。再実行は別素材へ。設計§10) / alarms=0件 nouns=[](0件=自然発火せず。再実行は別素材へ。設計§10) |
| PNAP-2b アラーム記録の必須項目(固有名詞/箇所/不一致/根拠/TTS供給結果/最終状態/models) | NOT_FIRED | NOT_FIRED | 欠落=[] / 欠落=[] |
| PNAP-3 固有名詞不一致のみでHRに回らない | NG | MANUAL | snapshot未指定のためHR queue/attempt_history前後比較不可。非RESOLVED lock={'a2': ['kp1_en'], 'b1b': ['kp1_en']} / snapshot未指定のためHR queue/attempt_history前後比較不可。非RESOLVED lock={} |
| PNAP-1 発音情報取得・TTS供給(respelling)の発火記録 | NOT_FIRED | NOT_FIRED | results内supply記録(非空)=0 / payload.supply_applied=0 / results内supply記録(非空)=0 / payload.supply_applied=0 |
| PNAP-1b Ledger evidence_tier/human_approved | INFO | INFO | 対象語=[] Ledger一致={} / 対象語=[] Ledger一致={} |
| PNAP-4 通常ASR/retry/fallback/regen/resume整合 | INFO | INFO | tts_generation_results.segments statusとattempts: {'a2': {'topic_intro': 'OK', 'japanese_title': 'OK', 'preview': 'OK', 'comment_1': 'OK', 'comment_2': 'OK', 'comment_3': 'OK', 'com / tts_generation_results.segments statusとattempts: {'a2': None, 'b1b': None} |
| PNAP-5 固有名詞以外の不一致は従来どおり | MANUAL | MANUAL | アラーム対象外のNG/HRが従来どおり残るかは、HR residual(payload.hr_residual)で確認: {'a2': {'available': True, 'hr_asr_uncertain_segments': 0, 'of_which_proper_noun_only_outside_alarm_boundary': 0}, 'b1b / アラーム対象外のNG/HRが従来どおり残るかは、HR residual(payload.hr_residual)で確認: {'a2': None, 'b1b': None} |
| PNAP-7 一般リスナー(公開ページ)に非露出 | OK | MISSING | leaks=[] pages=['er019_output/family_x_audio_production_wiring_01/coffee_prices__run_jre_01/player.html'] / leaks=[] pages=[] |
| PNAP-8 KP segmentにアラーム受理が適用されていない(範囲外) | OK | OK | KP alarm segments=[] / KP alarm segments=[] |
| PNAP-9 必須Regression/Validator/test | MANUAL | MANUAL | 当日手順書の事前チェック / 当日手順書の事前チェック |
| PNAP-J アラーム発火(X・Z双方、PNAP原文§5-9) | (合同) | (合同) | NOT_FIRED: alarms X=0 Z=0 |

## 総括
- KPFT: {'OK': 10, 'INFO': 6, 'NG': 1, 'MANUAL': 6, 'MISSING': 1}
- KP3V: {'OK': 3, 'MISSING': 3, 'NOT_FIRED': 5, 'INFO': 4, 'NG': 1}
- PNAP: {'OK': 6, 'NOT_FIRED': 7, 'NG': 1, 'INFO': 4, 'MANUAL': 5, 'MISSING': 4}
