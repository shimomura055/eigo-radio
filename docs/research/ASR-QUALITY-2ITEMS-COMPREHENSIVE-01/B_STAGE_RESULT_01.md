# B_STAGE_RESULT_01 -- ①RET(OPEN-472)・②UKUS(OPEN-471) Z runtime evidence (委任_05、2026-10-23)
使用モデル: NER=gpt-6-luna(最新世代推奨系、正式hook内)、Primary ASR=gpt-4o-mini-transcribe、Secondary=Azure STT、TTS=Gemini(Z正式backend、TTS_EXECUTION_MODE=STANDARD)。いずれも本番routing既定。Production code/Prompt/flag/閾値の変更0。

## ② UKUS(OPEN-471): Z evidence = **取得済み(正式Z `run_tts_stage`の実run、発火あり)**
- 入口: `er026_family_z_fiction_production_runner_01.py --stages tts_b1b --only-clips full_story_part3_c12`(CLI正式入口、run_sf_prod_01、Adv)。手順はUKUS/RUNTIME_EVIDENCE_01.md §3(保全→checkpoint不在確認→`reuse_blocked`印→1回実行)。
- 結果(`b1b/audit/tts_generation_results.json` c12): attempt 1でPASS(`primary_pass`/`ORTHOGRAPHIC_EQUIVALENT_MATCH`)。ASR `...Vera's specialty.`、`orthographic_equivalence.scope=Z, version=er109_orthographic_equivalence_v2_ukus01`、`er109.rules=['ukus_spelling_variant']`、`ukus_pairs=[{speciality/specialty, T1, varcon, both, pron_differs:true}]`、`ukus_active=true`、`ukus_table_sha256=c5598eb6…2dee`、Secondary呼出0、LR/cooldown/HR 0、audio_text_deviation なし。`text`(原稿)=`...Vera's speciality.`=字幕/スクリプトと一致。旧`reuse_value_guard_blocked_previous.reason=REUSE_BLOCKED_MARK`を自動記録。
- 旧(forte)の扱い: provenanceのforte記録は削除せず`superseded`注記。累積カウンタ 4→5(≤15)。
- 限界(明示): speciality/specialty は`pron_differs=true`のためTTSがどちらで読んだかは判定上区別不能。ユーザー最終試聴の確認点。
- X evidence(既存)と合わせ、②のX/Z双方の正式実run発火証跡が揃った。

## ① RET(OPEN-472): Z evidence = **部分取得(narrator経路は取得、dialogue経路はProduction不具合で非発火)**
### 取得できたもの
- 実run(run_sf_prod_01、CLI正式入口、tts_b1b/tts_a2/c12): RET構築hook発火。`audit/entity_table.json`(run直下、schema ret_prod_01)生成、NER=gpt-6-luna 2 call(A+B)、実体表5件[Bertie/Framton/Vera=person/confirmed、The Open Window=work_title/weak、India=place/weak]、covered 70 text(**両level脚本の和集合**)。以後のrun(tts_a2、c12)は **NER call=0**(保存表の復元=再開時NER 0)。operator報告に「実体表」節が別欄で表示(発音の根拠[Ledger/Perplexity]とは別)。`RUN_ENTITY_TABLE_ENABLED=True`・`UKUS_SPELLING_EQUIVALENCE_ENABLED=True`の両方ONの状態で、同一run内でUKUS発火(c12)・RET表復元が干渉なく動作(T-K Z実run: c12のjudgementに`ukus_active=true`、同runでNER 0)。
- ただし**実runでRETが受理に寄与した事例は0**: Bertie 4clipのうちc2×2はSecondary(Azure)一致のPASS_WITH_WARNING、c14×2はHR Lock。
- Ledger側の事実: 本runでPerplexity(復旧済み)が`Bertie`を自動調査し、正式経路どおり`cascade_unresolved_entity`(confidence=low、`evidence_tier=PRON_IN_CITED_PAGE`、updated_at 19:10:01、tier=Ledger auto)としてLedgerへ自動登録(個別手動登録ではない正規動作)。
- **隔離Z evidence(区分A、T-2.3方式)**: `er103_output/ret_prod_z_evidence_01/z_ret_evidence_01.py A`(正式Z `run_tts_stage`、Z実narrator生成器、TTS primitiveのみ保存の実誤読wav[b1b c14 attempt1]に差替、Primary/Azureは実API、Ledger語集合とASR Ledger hintを空にして初見の人名を模擬、HR queue/Stage1はstub)。結果(`z_ret_evidence_caseA_result.json`): **1 attemptでPASS_WITH_PRONUNCIATION_ALARM(`ENTITY_ONLY_ACCEPT`)**、`alarm_records[0].evidence=entity_table:confirmed:person`、`entity_table_basis`(entities=Bertie/person/confirmed, table_sha256…)付き、HR stub呼出0、`pronunciation_alarm.entity_table.per_diff`=bertie→Bertie、operator報告に実体表節。judgement `role=FULL_STORY, segment_key=full_story_part1_c14`。

### 取得できなかったもの(Production不具合)
- 同条件のdialogue生成器(Z会話clip、`case B`、`z_ret_evidence_caseB_result.json`)は **3 attempt全てNG_BOTH→HUMAN_REVIEW_REQUIRED**、`pronunciation_alarm_eval={accepted:false, reason:ROLE_NOT_APPLICABLE, detail:{role:null}}`。実runの会話clip(a2/b1b c14)の保全版・現行版も同じ`ROLE_NOT_APPLICABLE`。
- 原因: `er012_b_family_voices_production_01.py:553`の`evaluate_attempt_with_cascade`呼出に`segment_id`がなく、`er006_secondary_asr_01.py:1181`の`judge_role`が`None`、`er103_proper_noun_alarm_policy_01.py:336`の`role not in APPLICABLE_ROLES`で不適用。narrator生成器は`er003_v1_sing01_news_tail_fix.py:205-213`で`derive_segment_key(out_path)`を渡す。
- 影響: Z会話clipで発音アラーム受理(PNAP)・RETが無効=承認済みX/Z仕様(固有名詞の正式経路)と実動作が不一致。『開いた窓』のBertie(会話文中)が止まる直接原因。Production修正が必要(本委任は変更禁止のためFableへ。修正案は1箇所: `segment_id`をnews_tail_fix同様`review_lock.derive_segment_key(out_path)`から渡す。副作用=会話clipで`resolve_narrative_role`が`FULL_STORY`になり、Tier1(5role)・connected speech・semantic等の役割ゲート層も会話で有効になる可能性があるため、回帰とOpus条件の要否をFableが判断)。

## 費用
run_sf_prod_01: 61.95→71.41円(+9.46円、`make_real_spent_fn`=cost_log.jsonl。内訳増分: Gemini TTS 9 call・OpenAI ASR 10・Azure 9・NER 2・Perplexity 1[未計上])。隔離RET Z evidence: case A 0.50円+case B 0.66円(各raw_usage_logの`compute_cost_jpy_so_far`)。合計 約10.6円 / 上限20円。当日累計は`daily_dev_cost_01`でadopted 632.59→704.03円(他agent含む、1,400円上限内)。
