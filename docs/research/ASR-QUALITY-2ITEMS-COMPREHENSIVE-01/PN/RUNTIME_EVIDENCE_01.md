# RUNTIME_EVIDENCE_01(ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ①固有名詞 Run Entity Table [RET] / OPEN-472 / 委任_04 / X分、2026-10-23)

結論(先に): RETのX runtime evidence(構築・scope・証拠供給・受理・audit・HR 0・継承・Store guard・rollback)を、**保存済みの実誤読wav 2本**と**正式X runnerのTTS段関数**で取得した。**PRODUCTION_WIRED判定に使える証拠区分は「正式runner関数+生成器primitive差し替え+実ASR」(X-2)まで**。「自然発火のCLI正式入口」(`--only-segments`で新規生成して自然に誤読が出た)の証拠は**取れていない**(下記X-2対象の制約)。Z分(Bertie 4clip)は本委任の範囲外(後続B工程)。費用 **8.23円 / 上限15円**。

## 0. 証拠区分と取得条件(受入記録に明記する区分)
| 区分 | 内容 | PRODUCTION_WIRED判定への扱い |
|---|---|---|
| (A) 正式runner関数+生成器primitive差し替え+実ASR | X-2。正式`generate_family_x_b1_segments`(PNAP scope+RET構築hookのdecorator付き、`_ONLY_SEGMENTS`指定=`--only-segments`相当)を隔離run_dirで実行。TTS合成のprimitive(`er002_common._call_tts_with_retry`)**だけ**を保存した実誤読wavのPCMに差し替え、下流(trim/OpenAI ASR/統一judge/Azure/cascade/PNAP/RET/results書出/finally報告)は全て正式経路・実API | 実配線の証拠として使える(W-07予備策)。ただしCLI入口(`main()`)は通っていない(RFなど無関係な前段を避けるため関数を直接呼んだ) |
| (B) 保存wav replay(隔離) | X-1。保存した実誤読wav(HR queue由来)を正式hook[`run_with_alarm_hook`+`XProvider`]+正式adapter[`evaluate_attempt_with_cascade`]+実ASRへ通す | 配線の部分証拠(adapter・hook・継承・guard)。runnerの生成loopは通らない |
| (C) API 0の決定論 | 継承再判定・Store guard・rollback・署名・対照 | 補助 |

**Ledger全除外(初見の固有名詞の模擬)**: live Ledgerには既に`kristie tse`/`mimoun`相当が登録済みで、そのまま走らせると**従来のLedger/CMU未収録で受理される**(下記「Ledger live」行は表が寄与しない=W-01反実仮想どおり`entity_table`キーが付かない)。表の効果を見るため受理判定の`pol.ledger_surface_tokens`だけを空にして(Trial D1の『Ledger全除外』と同じ前提)再実行した。これは「新規記事の初見の人名」を模擬するもので、本番Ledgerには一切書いていない。

## 1. X-2(区分A): 正式runner関数、`--only-segments full_story_part2`、保存誤読wav replay、Ledger全除外
- スクリプト: `RUNTIME_EVIDENCE_01/x2_formal_runner_replay_01.py`、結果: `x2_formal_runner_replay_01_result.json`(初回)・`..._result_rerun.json`(同一out_dir再実行)。隔離run_dir=`RUNTIME_EVIDENCE_01/x2_run/theme_n8`。
- 対象: `pool_n8_airport_line` `point_two`(Kristie Tse、系統的誤読[Primary `Christy C.`/Secondary `Kristie Tsee`])。**制約**: 委任文のX-2は「`pool_n8_airport_line`を正式入口`--only-segments`で再生成」だが、同dirは旧構造(`parts.json`=point_one/point_two系)で現行runnerは`parts["part1"]`を読めず再生成不能(確認済み)。そのため現行構造の隔離themeに`part2`=当該wavの`canonical_text`(HR queue行)を置き、保存wavをTTS primitiveの戻りに使った。
- 結果(初回): 1 attemptでPASS_WITH_PRONUNCIATION_ALARM(`ENTITY_ONLY_ACCEPT`、`asr_judgement.state=PASS_WITH_PRONUNCIATION_ALARM`)、`pronunciation_alarm.entity_table`あり: per_diff=`kristie tse`(grant=kristie,tse)・entries_used=`Kristie Tse`(person/confirmed、sources=llm_a+llm_b_agree)・alarm_labels=`low(0.40-0.50)`、アラームrecordの`proper_noun_evidence`=`entity_table:confirmed:person`・`entity_table_basis`あり。**HR queue呼出0**(stub捕捉0件)。`audit/entity_table.json`生成(schema=ret_prod_01・builder_version・raw[llm_a/llm_b]・covered 1件・builds[calls=2])。NER=gpt-6-luna 2 call(A+B)。operator報告に「実体表」節(表の根拠と発音の根拠は別欄)。所要27秒。
- 結果(同一out_dir再実行): `reused_from_previous_run=True`・`asr_judgement_inherited.state=PASS_WITH_PRONUNCIATION_ALARM`・`entity_table`保持、TTS stub呼出0・ASR呼出0・NER 0(builds件数不変)、1.4秒 = 正式の再利用経路(`_reuse_guard_blocks`→`guard_entry`→保存entry復元)でRET由来音声が再生成なしに継承された。
- 対照(API 0、`controls_01_result.json`): 同じ転写・Ledger全除外・表なし=`NO_PROPER_NOUN_EVIDENCE`(`token=kristie`、従来はHR行き)、表あり=`ENTITY_ONLY_ACCEPT`(`entity_table:confirmed:person`)。

## 2. X-1(区分B): 保存wav replay、正式hook+正式adapter+実ASR
スクリプト: `x1_replay_01.py`(`--excl-ledger`で初見名模擬)。Primary=OpenAI gpt-4o-mini-transcribe(`routing.transcribe`)、Secondary=Azure STT(adapter内)、NER=gpt-6-luna(正式hook内)。
| case | Ledger | 受理 | 表の寄与 | 継承再判定(API 0) | Store guard(RET flag False) | 同一入力再構築 |
|---|---|---|---|---|---|---|
| n8 point_two(Kristie Tse) | live | `ENTITY_ONLY_ACCEPT`(`ledger`) | **なし**(W-01: 元のLedgerで受理=`entity_table`キー無し) | ok、`entity_table_updated=False` | blocked=False(RET非寄与) | NER 0 |
| n8 point_two | 全除外 | `ENTITY_ONLY_ACCEPT` | **RET-2**: per_diff=`kristie tse`、evidence=`entity_table:confirmed:person` | ok、`entity_table`更新=True、`rules_version`不一致なら再判定NG | **blocked=True**(`ENTITY_TABLE_ALARM_AUDIO_RET_INACTIVE_OR_UNRESTORABLE`) | NER 0 |
| cafes full_story_part1(L. Mimoun/A. Gruen、82秒) | 全除外 | `ENTITY_ONLY_ACCEPT` | **RET-3**: span=`l mimoun`(`mimoun`はCMU未収録でevidence=`cmu_oov`、Secondaryがイニシャル`L.`まで巻き込んで従来は`SECONDARY_NOT_ENTITY_ONLY`になる型) | ok、更新=True | blocked=True | NER 0 |
共通: HR queue stub呼出0、Stage1(Perplexity+Ledger upsert)はstub(呼出は記録、本番Ledgerへ書込0)、`audit/entity_table.json`生成、operator報告に実体表節。

## 3. X/Z-3・X/Z-4(区分C、API 0)
- 継承再判定: 上記のとおり保存entry(`entries_used`)からLLM 0 callで復元して再判定=ok。`rules_version`不一致(`BUILDER_RULES_CONSTANT`差替え)=ok False、RET flag False=ok False(test `TestInheritance`)。**現runの表を継承へ混入させない**(poison表test)。
- A/B/C不変・rollback(`controls_01_result.json`): scope外でholderがあっても`adapter_table()`=None/`is_active_for_run()`=False、scope内でもflag False=False。PNAP OFF・RET rollbackのhookでNER call=0。凍結baseline署名1516件(D1 HR queue 88×Ledger現行/全除外、D2保存EN pair 1309、fixture 31)が、表なし・空表・無関係表・RET flag Falseの全てで**バイト一致**。

## 4. 費用・時間
実費(raw_usage_logの集計): X-1 n8 live 1.06 + X-1 n8全除外 1.1 + cafes 全除外 約4.0 + X-2 1.06(+再実行0) = **8.23円**(Azure 7.43円・OpenAI ASR 0.71円・NER 0.10円、TTS 0円[stub])。上限15円内。NER実費 約0.02〜0.03円/回(5〜8 segment相当)。当日費用の確認: ACTIVE_TASKの記録=adopted 536.81円(2026-10-23の別タスク分)+本件8.23円 << 1,000円。モデル=最新原則: NER `gpt-6-luna`(現行世代推奨系)、Primary ASR `gpt-4o-mini-transcribe`、Secondary Azure STT(いずれも本番routing既定)。

## 5. 未取得・限界(PRODUCTION_WIRED前にFableが判断)
1. **CLI正式入口での自然発火**は未取得(現存のX記事に難読人名がほぼ無く、旧構造の誤読記事は現行runnerで再生成不能)。区分Aの「primitive差し替え」で代替した。
2. **Z分は本委任範囲外**(B工程でBertie 4clipの正式runner実行、HR Lock解除[USER_02 §1-B・§3の承認済み工程]が必要)。Zのhook・provider・providerの他level和集合・resumeは`er063 run_tts_stage`をfake generatorで通すtest(`TestZRunTtsStageIntegration`)でAPI 0確認済み。
3. 実運用の「新規生成で表が受理に寄与した」件数は、運用ログ(`pronunciation_alarms.json`の`entity_table_basis`)で今後集計できる(operator専用)。
