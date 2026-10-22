# 合同runtime evidence 集計(er106)
- schema: `er106_joint_runtime_evidence_01/v1` / generated_at: 2026-10-22T16:29:35
- X run: `er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_02` / Z run: `er026_output/family_z_production_e2e_01/melos/run_e2e_06`
- 状態語: OK / NG / MISSING(期待キー・成果物が無い=実装側の名称差または未配線。推測補完しない) / NOT_FIRED(自然発火せず) / MANUAL(機械判定不可) / INFO

## Family X: `er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_02` (levels=['a2', 'b1b'])
- entry_point: {"kp_backend_used_by_level": {"a2": "db_hybrid", "b1b": "db_hybrid"}, "m2_fallback_by_level": {"a2": null, "b1b": null}, "kp_stage_status": null, "tts_backend": "speech_metadata_flash_lite", "stage": "all", "present": true}
### (a) KP選定・件数
| level | n_items | backend(used) | model_id | prompt sha | sel/canon/red/outer | shortfall | 変更(原形化)件 | stale |
|---|---|---|---|---|---|---|---|---|
| a2 | 5 | db_hybrid | None | None | None/1/1/None | None | 1 | [] |
| b1b | 5 | db_hybrid | None | None | None/1/1/None | None | 2 | [] |
- a2#1: span=`conscientiousness` used=`conscientiousness` (本文一致=True, 語数=1, gloss=True, reason=none)
- a2#2: span=`weak link` used=`weak link` (本文一致=True, 語数=2, gloss=True, reason=none)
- a2#3: span=`Coming first` used=`come first` (本文一致=True, 語数=2, gloss=True, reason=inherit_selection_normalization)
- a2#4: span=`none other than` used=`none other than` (本文一致=True, 語数=3, gloss=True, reason=none)
- a2#5: span=`pay raise` used=`pay raise` (本文一致=True, 語数=2, gloss=True, reason=none)
- a2 metadataの未存在キー: ['prompt_id', 'prompt_sha256', 'user_message_sha256', 'record_status', 'model_requested', 'model_id', 'response_id', 'final_status', 'shortfall', 'kp_count_max', 'attempts', 'attempts_detail']
- b1b#1: span=`conscientiousness` used=`conscientiousness` (本文一致=True, 語数=1, gloss=True, reason=none)
- b1b#2: span=`Came first` used=`come first` (本文一致=True, 語数=2, gloss=True, reason=inherit_selection_normalization)
- b1b#3: span=`weakly` used=`weakly linked to higher income` (本文一致=True, 語数=1, gloss=True, reason=restore_semantic_complement)
- b1b#4: span=`in the spotlight` used=`in the spotlight` (本文一致=True, 語数=3, gloss=True, reason=none)
- b1b#5: span=`hold on` used=`hold on` (本文一致=True, 語数=2, gloss=True, reason=none)
- b1b metadataの未存在キー: ['prompt_id', 'prompt_sha256', 'user_message_sha256', 'record_status', 'model_requested', 'model_id', 'response_id', 'final_status', 'shortfall', 'kp_count_max', 'attempts', 'attempts_detail']
### (b) KP音声の3-ASR投票
| level | rank | 記録種別 | state | row | P | S | W発火 | W | W error | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| a2 | 1 | LEGACY_DUAL | None | None | None | None | None | None | None | False |
| a2 | 2 | LEGACY_DUAL | None | None | None | None | None | None | None | False |
| a2 | 3 | LEGACY_DUAL | None | None | None | None | None | None | None | False |
| a2 | 4 | LEGACY_DUAL | None | None | None | None | None | None | None | False |
| a2 | 5 | LEGACY_DUAL | None | None | None | None | None | None | None | False |
| b1b | 1 | LEGACY_DUAL | None | None | None | None | None | None | None | True |
| b1b | 2 | LEGACY_DUAL | None | None | None | None | None | None | None | True |
| b1b | 3 | LEGACY_DUAL | None | None | None | None | None | None | None | False |
| b1b | 4 | LEGACY_DUAL | None | None | None | None | None | None | None | False |
| b1b | 5 | LEGACY_DUAL | None | None | None | None | None | None | None | False |
### (c) 固有名詞アラーム
- a2: json=False md=False count=None consistency=None hr_residual=None supply_applied=None
- b1b: json=False md=False count=None consistency=None hr_residual=None supply_applied=None
### (d) 費用(JPY換算)
- 出典: `docs/pm/tools/daily_dev_cost_01.py`(USD_JPY=160.0、価格表 `er005_output/cost_baseline_01/pricing_snapshot.json`、cost_usd優先→tokens×単価、synthetic行は除外0件)。Whisperはローカル=0円(ログ対象外)。logs=['er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_02/raw_usage_log.jsonl']
- 合計 **15.4488円** / KP関連(chain+音声) 1.4908円 (+未分離scaffold 2.1022円を含めると 3.593円) / unpriced={}
| bucket | 円 | calls |
|---|---|---|
| kp_audio_english | 0.8208 | 24 |
| kp_audio_explanation | 0.307 | 10 |
| kp_audio_ja_meaning | 0.2829 | 14 |
| kp_chain | 0.0801 | 1 |
| non_kp_audio | 11.8302 | 48 |
| other | 0.0255 | 1 |
| scaffold_llm_unsplit | 2.1022 | 16 |
| bucket:kind | 円 | calls |
|---|---|---|
| kp_audio_english:asr_azure | 0.5404 | 8 |
| kp_audio_english:asr_openai | 0.1292 | 8 |
| kp_audio_english:tts | 0.1512 | 8 |
| kp_audio_explanation:asr_openai | 0.1176 | 5 |
| kp_audio_explanation:tts | 0.1894 | 5 |
| kp_audio_ja_meaning:asr_azure | 0.0729 | 1 |
| kp_audio_ja_meaning:asr_openai | 0.0592 | 5 |
| kp_audio_ja_meaning:llm | 0.0156 | 3 |
| kp_audio_ja_meaning:tts | 0.1352 | 5 |
| kp_chain:llm | 0.0801 | 1 |
| non_kp_audio:asr_azure | 3.4203 | 2 |
| non_kp_audio:asr_openai | 2.9102 | 25 |
| non_kp_audio:tts | 5.4997 | 21 |
| other:llm | 0.0255 | 1 |
| scaffold_llm_unsplit:llm | 2.1022 | 16 |
### (f) 試聴ページ・再生順
- page `er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_02/player.html`: 標準適合=None failed=None KP行=None アラーム語漏れ=[]
- a2 再生順(間接: key_phrase_N長 >= 2*英+第3): kp1:OK, kp2:OK, kp3:OK, kp4:OK, kp5:OK (timeline=True)
- b1b 再生順(間接: key_phrase_N長 >= 2*英+第3): kp1:OK, kp2:OK, kp3:OK, kp4:OK, kp5:OK (timeline=True)

## Family Z: `er026_output/family_z_production_e2e_01/melos/run_e2e_06` (levels=['a2', 'b1b'])
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
| a2 | 1 | MISSING | None | None | None | None | None | None | None | None |
| a2 | 2 | MISSING | None | None | None | None | None | None | None | None |
| a2 | 3 | MISSING | None | None | None | None | None | None | None | None |
| a2 | 4 | MISSING | None | None | None | None | None | None | None | None |
| a2 | 5 | MISSING | None | None | None | None | None | None | None | None |
| b1b | 1 | MISSING | None | None | None | None | None | None | None | None |
| b1b | 2 | MISSING | None | None | None | None | None | None | None | None |
| b1b | 3 | MISSING | None | None | None | None | None | None | None | None |
| b1b | 4 | MISSING | None | None | None | None | None | None | None | None |
| b1b | 5 | MISSING | None | None | None | None | None | None | None | None |
### (c) 固有名詞アラーム
- a2: json=False md=False count=None consistency=None hr_residual=None supply_applied=None
- b1b: json=False md=False count=None consistency=None hr_residual=None supply_applied=None
### (d) 費用(JPY換算)
- 出典: `docs/pm/tools/daily_dev_cost_01.py`(USD_JPY=160.0、価格表 `er005_output/cost_baseline_01/pricing_snapshot.json`、cost_usd優先→tokens×単価、synthetic行は除外0件)。Whisperはローカル=0円(ログ対象外)。logs=['er026_output/family_z_production_e2e_01/melos/run_e2e_06/cost_log.jsonl']
- 合計 **27.5762円** / KP関連(chain+音声) 1.5211円 (+未分離scaffold 0円を含めると 1.5211円) / unpriced={}
| bucket | 円 | calls |
|---|---|---|
| kp_audio_english | 0.5819 | 21 |
| kp_audio_explanation | 0.6422 | 10 |
| kp_audio_ja_meaning | 0.297 | 10 |
| non_kp_audio | 26.0551 | 170 |
| bucket:kind | 円 | calls |
|---|---|---|
| kp_audio_english:asr_azure | 0.0524 | 1 |
| kp_audio_english:asr_openai | 0.156 | 10 |
| kp_audio_english:tts | 0.3734 | 10 |
| kp_audio_explanation:asr_openai | 0.1376 | 5 |
| kp_audio_explanation:tts | 0.5046 | 5 |
| kp_audio_ja_meaning:asr_openai | 0.0568 | 5 |
| kp_audio_ja_meaning:tts | 0.2402 | 5 |
| non_kp_audio:asr_azure | 7.8701 | 21 |
| non_kp_audio:asr_openai | 2.7228 | 83 |
| non_kp_audio:llm | 0.0384 | 6 |
| non_kp_audio:tts | 15.4237 | 60 |
### (f) 試聴ページ・再生順
- pageが見つからない(--x-page/--z-pageで指定)
- a2 再生順(間接: key_phrase_N長 >= 2*英+第3): kp1:OK, kp2:OK, kp3:OK, kp4:OK, kp5:OK (timeline=True)
- b1b 再生順(間接: key_phrase_N長 >= 2*英+第3): kp1:OK, kp2:OK, kp3:OK, kp4:OK, kp5:OK (timeline=True)

## (e) STOP・HR・共有log
- STOPセンチネル(現在): ['C:/Users/tensh/eigo-radio/docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md']
- 前後差分: snapshot未指定
- Ledger対象語照合: {}

## Dangling Reference grep(Production .py、testは別掲)
- KPFT: db_hybrid経路: production=3 test=0 ['er003_v1_n3_01_scaffold_generate.py:333', 'er003_v1_n3_01_scaffold_generate.py:606', 'er003_v1_n3_01_scaffold_generate.py:622']
- KPFT: m2_fallback: production=26 test=2 ['er003_v1_n3_01_scaffold_generate.py:544', 'er003_v1_n3_01_scaffold_generate.py:564', 'er003_v1_n3_01_scaffold_generate.py:570', 'er003_v1_n3_01_scaffold_generate.py:571', 'er003_v1_n3_01_scaffold_generate.py:576', 'er003_v1_n3_01_scaffold_generate.py:595', 'er003_v1_n3_01_scaffold_generate.py:642', 'er003_v1_n3_01_scaffold_generate.py:657']
- KPFT: KP_ARTICLE_COST_CAP: production=6 test=2 ['er003_v1_n3_01_scaffold_generate.py:1058', 'er003_v1_n3_01_scaffold_generate.py:1060', 'er003_v1_n3_01_scaffold_generate.py:1078', 'er003_v1_n3_01_scaffold_generate.py:1081', 'er003_v1_n3_01_scaffold_generate.py:1085', 'er019_family_x_audio_production_runner_01.py:349']
- KP3V: 旧dual識別子(撤去対象): production=22 test=3 ['er078_asr_unified_judge_01.py:27', 'er096_kp_dual_pass_01.py:5', 'er096_kp_dual_pass_01.py:12', 'er096_kp_dual_pass_01.py:14', 'er096_kp_dual_pass_01.py:16', 'er096_kp_dual_pass_01.py:18', 'er096_kp_dual_pass_01.py:22', 'er096_kp_dual_pass_01.py:38']
- KP3V: 維持する容器名/telemetry名(情報。0件でなくてよい): production=39 test=4 ['er019_family_x_audio_production_runner_01.py:781', 'er019_family_x_audio_production_runner_01.py:785', 'er019_family_x_audio_production_runner_01.py:786', 'er063_family_z_audio_01.py:747', 'er063_family_z_audio_01.py:751', 'er063_family_z_audio_01.py:752', 'er063_family_z_audio_01.py:1022', 'er063_family_z_audio_01.py:1023']

## KPFT(KP全文選定+3件化) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| KPFT-1 全文直接選定(候補DBでない) | NG | MISSING | a2:NG(kp_backend=db_hybrid used=db_hybrid db_hybrid_dir=True); b1b:NG(kp_backend=db_hybrid used=db_hybrid db_hybrid_dir=True) / a2:MISSING(kp_backend=None used=None db_hybrid_dir=False); b1b:MISSING(kp_backend=None used=None db_hybrid_dir=False) |
| KPFT-2 actual model ID=gpt-6-luna | MISSING | OK | a2:MISSING(model_id=None requested=None); b1b:MISSING(model_id=None requested=None) / a2:OK(model_id=gpt-6-luna requested=None); b1b:OK(model_id=gpt-6-luna requested=None) |
| KPFT-3 正式Prompt 2のsha | MISSING | MISSING | a2:MISSING(prompt_sha256=None); b1b:MISSING(prompt_sha256=None) / a2:MISSING(prompt_sha256=None); b1b:MISSING(prompt_sha256=None) |
| KPFT-4 KP最大3件 | NG | NG | a2:NG(n_items=5 shortfall=None (期待3, 1-2はshortfall記録つきで許容)); b1b:NG(n_items=5 shortfall=None (期待3, 1-2はshortfall記録つきで許容)) / a2:NG(n_items=5 shortfall=None (期待3, 1-2はshortfall記録つきで許容)); b1b:NG(n_items=5 shortfall=None (期待3, 1-2はshortfall記録つきで許容)) |
| KPFT-5 本文外/6語以上が不採用 | OK | OK | a2:OK(本文不一致/6語以上のrank=[] (全5件のsource_span本文一致+<=5語)); b1b:OK(本文不一致/6語以上のrank=[] (全5件のsource_span本文一致+<=5語)) / a2:OK(本文不一致/6語以上のrank=[] (全5件のsource_span本文一致+<=5語)); b1b:OK(本文不一致/6語以上のrank=[] (全5件のsource_span本文一致+<=5語)) |
| KPFT-6 原形化・一般化 | INFO | INFO | a2:INFO(変更1件(要:聴取/目視で一般化の妥当性確認): [(3, 'Coming first', 'come first', 'inherit_selection_normalization')]); b1b:INFO(変更2件(要:聴取/目視で一般化の妥当性確認): [(2, 'Came first', 'come first', 'inheri / a2:INFO(変更4件(要:聴取/目視で一般化の妥当性確認): [(1, 'pulled him under', 'pull someone under', 'inherit_selection_normalization'), (2, 'in your place', "in someone's place", 'generalize_person_de |
| KPFT-7 後段(意味/解説/音声/ASR/組立) | OK | OK | a2:OK(KP音声/解説/ja意味 OK、timeline KP=5、再生順間接検査 miss=[]); b1b:OK(KP音声/解説/ja意味 OK、timeline KP=5、再生順間接検査 miss=[]) / a2:OK(KP音声/解説/ja意味 OK、timeline KP=5、再生順間接検査 miss=[]); b1b:OK(KP音声/解説/ja意味 OK、timeline KP=5、再生順間接検査 miss=[]) |
| KPFT-8 retry/fallback/regen/resume | INFO | INFO | a2:INFO(選定None/2 canon1/2 red1(REDUNDANCY_PASS) outerNone/3 stale=[] fallback_notice=False); b1b:INFO(選定None/2 canon1/2 red1(REDUNDANCY_PASS) outerNone/3 stale=[] fallback_notice=F / a2:INFO(選定None/2 canon1/2 red1(REDUNDANCY_PASS) outer3/3 stale=[] fallback_notice=False); b1b:INFO(選定None/2 canon1/2 red1(REDUNDANCY_PASS) outer1/3 stale=[] fallback_notice=False) |
| KPFT-9 旧DB/5件のDangling Reference | MANUAL | MANUAL | --dangling-grep で別途集計(下記)。run出力からは判定しない / --dangling-grep で別途集計(下記)。run出力からは判定しない |
| KPFT-10 必須Regression/Validator/test | MANUAL | MANUAL | 当日手順書の事前チェック(全回帰PASS)で確認 / 当日手順書の事前チェック(全回帰PASS)で確認 |
| KPFT-11 X/Z双方の正式runtime evidence | INFO | INFO | levels=['a2', 'b1b'] / levels=['a2', 'b1b'] |
| KPFT-12 SSOT/Git | MANUAL | MANUAL | Fable受入時 / Fable受入時 |

## KP3V(3-ASR多数決) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| KP3V-0 KP英語voteの存在 | MISSING | MISSING | new=0 legacy_dual=10 missing=0 (旧dual/証跡無しが残る=新判定が通っていない) / new=0 legacy_dual=0 missing=10 (旧dual/証跡無しが残る=新判定が通っていない) |
| KP3V-0b 期待キー不一致 | MISSING | MISSING | missing_keys=[](実装側の名称が設計書と違う可能性。推測補完しない) / missing_keys=[](実装側の名称が設計書と違う可能性。推測補完しない) |
| KP3V-1 割れた場合のみWhisper発動 | MISSING | MISSING | split(P!=S)=0 whisper_fired=0 割れ無しで発火(I1違反)=[] 割れたのに未発火=[] / split(P!=S)=0 whisper_fired=0 割れ無しで発火(I1違反)=[] 割れたのに未発火=[] |
| KP3V-1b Whisperの自然発火(発火証拠) | NOT_FIRED | NOT_FIRED | 割れが発生しなかった場合は NOT_FIRED(自然発火待ち。保存wavのreplayは正式runtime証拠に当たらない=PNAP設計§10と同じ扱い) / 割れが発生しなかった場合は NOT_FIRED(自然発火待ち。保存wavのreplayは正式runtime証拠に当たらない=PNAP設計§10と同じ扱い) |
| KP3V-1c Whisper事前確認(preflight)の記録(設計§16-1 P-08) | MISSING | MISSING | 記録を含むファイル=[](名称は配線後に確認。無い場合は実装側の記録先を確認) / 記録を含むファイル=[](名称は配線後に確認。無い場合は実装側の記録先を確認) |
| KP3V-2 2/3 PASSで正常終了 | NOT_FIRED | NOT_FIRED | PASS_VOTE_2OF3=0件 rank=[] / PASS_VOTE_2OF3=0件 rank=[] |
| KP3V-3 2/3 NGは従来どおりNG | INFO | INFO | NG系state=0件(最終採用wavがNG stateでないかはKP3V-4/invariantsで検査。NG attemptはattempts履歴側) / NG系state=0件(最終採用wavがNG stateでないかはKP3V-4/invariantsで検査。NG attemptはattempts履歴側) |
| KP3V-4 Whisper error/未利用でPASSにしない(不変条件I1-I7) | MISSING | MISSING | 0件の投票記録でI1-I7違反なし / 0件の投票記録でI1-I7違反なし |
| KP3V-4b Whisper構成(small/int8) | NOT_FIRED | NOT_FIRED | observed=[] / observed=[] |
| KP3V-5 retry/fallback/regen/resumeへの一貫適用 | INFO | INFO | 再利用(reused=True)のvote=[] / attempts={'a2#1': None, 'a2#2': None, 'a2#3': None, 'a2#4': None, 'a2#5': None, 'b1b#1': None, 'b1b#2': None, 'b1b#3': None, 'b1b#4': None, 'b1b#5': None / 再利用(reused=True)のvote=[] / attempts={'a2#1': 1, 'a2#2': 1, 'a2#3': 1, 'a2#4': 1, 'a2#5': 1, 'b1b#1': 1, 'b1b#2': 1, 'b1b#3': 1, 'b1b#4': 1, 'b1b#5': 1} |
| KP3V-6 Store再利用時にも新判定 | NG | NOT_FIRED | reused=2件 / reused=0件 |
| KP3V-7 KP英語解説・その他音声に影響なし(voteの証跡が英語phrase以外に付かない) | OK | OK | 英語phrase以外にvote証跡が付いた箇所=[] / 英語phrase以外にvote証跡が付いた箇所=[] |
| KP3V-8 固有名詞アラームとの適用範囲整合 | INFO | INFO | KP segmentにPNAPアラーム状態が付いていないこと: PNAP側のKP混入検査を参照 / KP segmentにPNAPアラーム状態が付いていないこと: PNAP側のKP混入検査を参照 |
| KP3V-9 X/Z双方の正式runtime evidence | INFO | INFO | levels=['a2', 'b1b'] / levels=['a2', 'b1b'] |
| KP3V-J Whisper正式runtime発火(X/Zいずれか) | (合同) | (合同) | NOT_FIRED: X=False Z=False。双方未発火なら『Xで発火観測+Z同adapterをtestで固定』は不成立→別素材で追加run(設計P-06) |

## PNAP(固有名詞アラーム) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| PNAP-0 audit/pronunciation_alarms.json と operator_alarm_report.md の生成 | MISSING | MISSING | levels=['a2', 'b1b'] json=[] / levels=['a2', 'b1b'] json=[] |
| PNAP-0b 期待キー不一致(payload/record) | MISSING | MISSING | payload_missing=[] record_missing=[] / payload_missing=[] record_missing=[] |
| PNAP-6 アラームが完成報告へ引継ぎ(集計一致P-08) | MISSING | MISSING | consistency=[('a2', None), ('b1b', None)] / ALARM state segments(results)={'a2': [], 'b1b': []} / consistency=[('a2', None), ('b1b', None)] / ALARM state segments(results)={'a2': [], 'b1b': []} |
| PNAP-2 不一致時にアラーム記録+制作継続(発火証拠) | NOT_FIRED | NOT_FIRED | alarms=0件 nouns=[](0件=自然発火せず。再実行は別素材へ。設計§10) / alarms=0件 nouns=[](0件=自然発火せず。再実行は別素材へ。設計§10) |
| PNAP-2b アラーム記録の必須項目(固有名詞/箇所/不一致/根拠/TTS供給結果/最終状態/models) | NOT_FIRED | NOT_FIRED | 欠落=[] / 欠落=[] |
| PNAP-3 固有名詞不一致のみでHRに回らない | MANUAL | MANUAL | snapshot未指定のためHR queue/attempt_history前後比較不可。非RESOLVED lock={} / snapshot未指定のためHR queue/attempt_history前後比較不可。非RESOLVED lock={} |
| PNAP-1 発音情報取得・TTS供給(respelling)の発火記録 | NOT_FIRED | NOT_FIRED | results内supply記録(非空)=0 / payload.supply_applied=0 / results内supply記録(非空)=0 / payload.supply_applied=0 |
| PNAP-1b Ledger evidence_tier/human_approved | INFO | INFO | 対象語=[] Ledger一致={} / 対象語=[] Ledger一致={} |
| PNAP-4 通常ASR/retry/fallback/regen/resume整合 | INFO | INFO | tts_generation_results.segments statusとattempts: {'a2': {'topic_intro': 'OK', 'japanese_title': 'OK', 'preview': 'OK', 'comment_1': 'OK', 'comment_2': 'OK', 'comment_3': 'OK', 'com / tts_generation_results.segments statusとattempts: {'a2': {'topic_intro_en': 'OK', 'japanese_title': 'OK', 'preview': 'OK', 'comment_1': 'OK', 'comment_2': 'OK', 'comment_3': 'OK', ' |
| PNAP-5 固有名詞以外の不一致は従来どおり | MANUAL | MANUAL | アラーム対象外のNG/HRが従来どおり残るかは、HR residual(payload.hr_residual)で確認: {'a2': None, 'b1b': None} / アラーム対象外のNG/HRが従来どおり残るかは、HR residual(payload.hr_residual)で確認: {'a2': None, 'b1b': None} |
| PNAP-7 一般リスナー(公開ページ)に非露出 | OK | MISSING | leaks=[] pages=['er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_02/player.html'] / leaks=[] pages=[] |
| PNAP-8 KP segmentにアラーム受理が適用されていない(範囲外) | OK | OK | KP alarm segments=[] / KP alarm segments=[] |
| PNAP-9 必須Regression/Validator/test | MANUAL | MANUAL | 当日手順書の事前チェック / 当日手順書の事前チェック |
| PNAP-J アラーム発火(X・Z双方、PNAP原文§5-9) | (合同) | (合同) | NOT_FIRED: alarms X=0 Z=0 |

## 総括
- KPFT: {'NG': 3, 'MISSING': 4, 'OK': 5, 'INFO': 6, 'MANUAL': 6}
- KP3V: {'MISSING': 10, 'NOT_FIRED': 8, 'INFO': 8, 'NG': 1, 'OK': 2}
- PNAP: {'MISSING': 7, 'NOT_FIRED': 7, 'MANUAL': 6, 'INFO': 4, 'OK': 3}
