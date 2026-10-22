# 合同runtime evidence 集計(er106)
- schema: `er106_joint_runtime_evidence_01/v1` / generated_at: 2026-10-22T17:41:49
- X run: `None` / Z run: `er026_output/family_z_production_e2e_01/melos/run_jre_01`
- 状態語: OK / NG / MISSING(期待キー・成果物が無い=実装側の名称差または未配線。推測補完しない) / NOT_FIRED(自然発火せず) / MANUAL(機械判定不可) / INFO

## Family X: `None` (levels=None)
- run dirが存在しない

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
- 合計 **2.4円** / KP関連(chain+音声) 2.4円 (+未分離scaffold 0円を含めると 2.4円) / unpriced={}
| bucket | 円 | calls |
|---|---|---|
| kp_chain | 2.4 | 19 |
| bucket:kind | 円 | calls |
|---|---|---|
| kp_chain:llm | 2.4 | 19 |
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
| KPFT-ALL | MISSING | - | X run dirが存在しない /  |
| KPFT-1 全文直接選定(候補DBでない) | - | OK |  / a2:OK(kp_backend=fulltext_p2 used=fulltext_p2 db_hybrid_dir=False); b1b:OK(kp_backend=fulltext_p2 used=fulltext_p2 db_hybrid_dir=False) |
| KPFT-2 actual model ID=gpt-6-luna | - | OK |  / a2:OK(model_id=gpt-6-luna requested=gpt-6-luna); b1b:OK(model_id=gpt-6-luna requested=gpt-6-luna) |
| KPFT-3 正式Prompt 2のsha | - | OK |  / a2:OK(prompt_sha256=a12896f485604f32); b1b:OK(prompt_sha256=a12896f485604f32) |
| KPFT-4 KP最大3件 | - | OK |  / a2:OK(n_items=3 shortfall=False (期待3, 1-2はshortfall記録つきで許容)); b1b:OK(n_items=3 shortfall=False (期待3, 1-2はshortfall記録つきで許容)) |
| KPFT-5 本文外/6語以上が不採用 | - | OK |  / a2:OK(本文不一致/6語以上のrank=[] (全3件のsource_span本文一致+<=5語)); b1b:OK(本文不一致/6語以上のrank=[] (全3件のsource_span本文一致+<=5語)) |
| KPFT-6 原形化・一般化 | - | INFO |  / a2:INFO(変更2件(要:聴取/目視で一般化の妥当性確認): [(1, 'in your place', "in someone's place", 'generalize_person_dependent_reference'), (2, 'held out', 'hold out', 'lemma_normalization')]); b1b:INF |
| KPFT-7 後段(意味/解説/音声/ASR/組立) | - | MISSING |  / a2:MISSING(tts_generation_results.json無し); b1b:MISSING(tts_generation_results.json無し) |
| KPFT-8 retry/fallback/regen/resume | - | INFO |  / a2:INFO(選定1/2 canon1/2 red1(REDUNDANCY_PASS) outer1/3 stale=[] fallback_notice=False); b1b:INFO(選定1/2 canon1/2 red1(REDUNDANCY_PASS) outer1/3 stale=[] fallback_notice=False) |
| KPFT-9 旧DB/5件のDangling Reference | - | MANUAL |  / --dangling-grep で別途集計(下記)。run出力からは判定しない |
| KPFT-10 必須Regression/Validator/test | - | MANUAL |  / 当日手順書の事前チェック(全回帰PASS)で確認 |
| KPFT-11 X/Z双方の正式runtime evidence | - | INFO |  / levels=['a2', 'b1b'] |
| KPFT-12 SSOT/Git | - | MANUAL |  / Fable受入時 |

## KP3V(3-ASR多数決) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| KP3V-ALL | MISSING | - | X run dirが存在しない /  |
| KP3V-0 KP英語voteの存在 | - | MISSING |  / KP英語音声のresultsが無い |
| KP3V-J Whisper正式runtime発火(X/Zいずれか) | (合同) | (合同) | NOT_FIRED: X=False Z=False。双方未発火なら『Xで発火観測+Z同adapterをtestで固定』は不成立→別素材で追加run(設計P-06) |

## PNAP(固有名詞アラーム) 確認項目
| 項目 | X | Z | 根拠(X) / (Z) |
|---|---|---|---|
| PNAP-ALL | MISSING | - | X run dirが存在しない /  |
| PNAP-0 audit/pronunciation_alarms.json と operator_alarm_report.md の生成 | - | MISSING |  / levels=['a2', 'b1b'] json=[] |
| PNAP-0b 期待キー不一致(payload/record) | - | MISSING |  / payload_missing=[] record_missing=[] |
| PNAP-6 アラームが完成報告へ引継ぎ(集計一致P-08) | - | MISSING |  / consistency=[('a2', None), ('b1b', None)] / ALARM state segments(results)={'a2': None, 'b1b': None} |
| PNAP-2 不一致時にアラーム記録+制作継続(発火証拠) | - | NOT_FIRED |  / alarms=0件 nouns=[](0件=自然発火せず。再実行は別素材へ。設計§10) |
| PNAP-2b アラーム記録の必須項目(固有名詞/箇所/不一致/根拠/TTS供給結果/最終状態/models) | - | NOT_FIRED |  / 欠落=[] |
| PNAP-3 固有名詞不一致のみでHRに回らない | - | MANUAL |  / snapshot未指定のためHR queue/attempt_history前後比較不可。非RESOLVED lock={} |
| PNAP-1 発音情報取得・TTS供給(respelling)の発火記録 | - | NOT_FIRED |  / results内supply記録(非空)=0 / payload.supply_applied=0 |
| PNAP-1b Ledger evidence_tier/human_approved | - | INFO |  / 対象語=[] Ledger一致={} |
| PNAP-4 通常ASR/retry/fallback/regen/resume整合 | - | INFO |  / tts_generation_results.segments statusとattempts: {'a2': None, 'b1b': None} |
| PNAP-5 固有名詞以外の不一致は従来どおり | - | MANUAL |  / アラーム対象外のNG/HRが従来どおり残るかは、HR residual(payload.hr_residual)で確認: {'a2': None, 'b1b': None} |
| PNAP-7 一般リスナー(公開ページ)に非露出 | - | MISSING |  / leaks=[] pages=[] |
| PNAP-8 KP segmentにアラーム受理が適用されていない(範囲外) | - | OK |  / KP alarm segments=[] |
| PNAP-9 必須Regression/Validator/test | - | MANUAL |  / 当日手順書の事前チェック |
| PNAP-J アラーム発火(X・Z双方、PNAP原文§5-9) | (合同) | (合同) | NOT_FIRED: alarms X=None Z=0 |

## 総括
- KPFT: {'MISSING': 2, 'OK': 5, 'INFO': 3, 'MANUAL': 3}
- KP3V: {'MISSING': 2, 'NOT_FIRED': 1}
- PNAP: {'MISSING': 5, 'NOT_FIRED': 4, 'MANUAL': 3, 'INFO': 2, 'OK': 1}
