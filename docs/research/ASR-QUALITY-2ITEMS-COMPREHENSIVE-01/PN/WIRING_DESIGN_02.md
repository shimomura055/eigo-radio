# WIRING_DESIGN_02(ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ①固有名詞 Run Entity Table [RET] / OPEN-472 / 委任_04、2026-10-23)

WIRING_DESIGN_01.md(委任_03)に Opus条件Cレビュー(`OPUS_REVIEW_02_COND_C.md`、必須 OF-PN-W-01〜07・推奨 08〜15)を反映した**差分表**。全体設計(新module+er103本体統合・PNAP scope・既定ON+1行rollback・構築hook 1か所)は01のまま。
承認根拠: ユーザー原文 `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md`(APPROVED_FOR_PRODUCTION、UDR #168)。PRODUCTION_WIREDはFable受入後。

## 1. OF反映表(W-01〜W-15)

| OF | 区分 | 01の設計 | 02(実装) | 実装 file:line / test |
|---|---|---|---|---|
| W-01 | 必須 | `ls=ledger|grant`を全Primary句へ渡し、`table_used`に寄与前の句も記録 | **反実仮想**: 句ごとにまず元の`ledger_surfaces`で`_noun_checks`。`R_NOT_PROPER_EVIDENCE`で落ちた句だけ`ls|grant`で再判定。再判定が通った句(+その句のSecondary)にだけ`per_diff/entries_used/alarm_labels/entity_table`を付ける。寄与が無い受理にはキー自体を付けない | `er103_proper_noun_alarm_policy_01.py` G5(`ls, ginfo`)・`detail["entity_table"]`; `TestCounterfactualContribution` |
| W-02 | 必須 | baseline署名のみ | (a)単調性test=Trial実表の全entry和集合を与えても**表なし受理はバイト一致**、不受理->受理への変化(flips>0)は`entity_table`付き (b)差分test=Trialの`evaluate_alarm_eligibility_pn`をtestからのみimportし、凍結コーパス1516件で accept/reason/diffs(canonical,asr,evidence)一致 (c)表が関与しないspanは`ret3_rejected`を付けない(touched判定)=無関係表でもバイト一致。署名は`evaluate_alarm_eligibility`**入力**(cls diffs直列化)で凍結(`er103_ret_baseline_signature_v1.json`、実装前commit `78a2c7c6e`) | `er103_ret_baseline_signature_01.py`; `TestEquivalenceW02`; `TestRet3.test_w02c_*`; Trial test(`er111_pn_entity_table_trial_01_test_01.py`)は旧drift guardを差分testへ再構成(skipせず) |
| W-03 | 必須 | 保存=entry全体、resumeは`builder_version`一致時に再利用 | 保存は**LLM生候補(raw: declared/llm_a/llm_b)+coverage(text sha)のみ**。判定用entryは構築のたびに**今のprovider textの和集合**に対し決定論(API 0)で再導出(`derive_entries`)。今のtextに逐語出現しない旧候補は外す。eligible/`lowercase_seen`/見出し/`_det_support`は全textに依存するため毎回再計算。Zは他levelの脚本(`segment_plan_<level>.json`・`support/<level>_support.json`の英語分)が揃えば和集合に加える。call Bは「独立裏付け待ちが残り、現textが`covered_b`に未収録」のときだけ**現textの和集合1回**(Zで4 callになる経路を撤去) | `er103_run_entity_table_01.py` `derive_entries`/`ensure_table`/`ZProvider`; `TestPersistence` |
| W-04 | 必須 | `evaluate_for_adapter`が未指定なら`current_table()`を自動取得 | `evaluate_for_adapter`は`entity_table`を**明示渡しのみ**(既定None)。自動取得は`ret.adapter_table()`をadapter(`er006_secondary_asr_01.py` `_pnap_try_accept`)が明示で呼ぶ1か所のみ。継承(`er019 rejudge_with_current_judge`)は`ret.restore_from_audit_block(ab)`(復元表 or None)を明示、**現runの表は混入しない**(poison表test)。継承で受理したら`pronunciation_alarm.entity_table`を`dec.detail`で更新(寄与が無くなればキーを外す) | `er103_proper_noun_alarm_policy_01.py` `evaluate_for_adapter`; `er006_secondary_asr_01.py:828`; `er019_family_x_validation_inheritance_01.py:365-`; `TestInheritance` |
| W-05 | 必須 | RET-3: 供給tokenの扱い未記載 | span内tokenが`supply_map`に含まれる場合は不適用(`ret3_rejected="supplied_token_in_span"`) | `EntityTable.ret3_check`; `TestRet3.test_w05_*` |
| W-06 | 必須 | Store guard: `not ret.is_active_for_run()`のみ | 保存entryが`rules_version`不一致(復元不能)でもblock(`ENTITY_TABLE_ALARM_AUDIO_RET_INACTIVE_OR_UNRESTORABLE`)。さらに再判定NGは保護理由でなくても`REJUDGE_NG_ENTITY_TABLE`でblock(`REJUDGE_NG_NOT_PROTECTED`を素通りしない)。`asr_judgement`と`asr_judgement_inherited`の**両方**を見る。RET由来entryだけが対象 | `er078_reuse_value_guard_01.py`(PNAP guardの直後・再判定後); `TestStoreGuard` |
| W-07 | 必須 | X-2は自然発火に依存 | X-2=正式入口(`er019_family_x_audio_production_runner_01.py --stage tts --only-segments`)。ただし**`pool_n8_airport_line`は旧構造(`point_one/point_two`)で現行runnerが`parts["part1"]`を読めず再生成不能**(確認: `parts.json` keys=point_one_heading..)。→ X-1(保存misread wav[pool_n8 point_two=Kristie Tse、pool_n5_cafes full_story_part1=L. Mimoun/Gruen]+正式hook[XProvider]+正式adapter+実ASR、隔離run_dir)とX-2(現行構造の記事を隔離コピー上で`--only-segments`再生成)を分け、**証拠区分を明記**。harnessのみの証拠ではPRODUCTION_WIREDにしない | `PN/RUNTIME_EVIDENCE_01.md` |
| W-08 | 推奨 | LR時NERなし | 許容(fail-closed)。「LRで新たに出た固有名詞は表外=現行挙動(受理範囲は縮小方向)」をDECISION_LOGへ記録。LRで名前を残したtextは既存entryの`occurrences`で証拠付与される | `TestRet3`/`TestPersistence`; DECISION_LOG |
| W-09 | 推奨 | NER失敗の扱い | NER失敗textは`covered_text_sha256`に入れず再試行、statusは構築ごと`builds[]`に記録。失敗のみの構築はファイルを書かない | `ensure_table`; `TestPersistence.test_w09_*` |
| W-10 | 推奨 | `builder_version`=prompt等のhash | `build_version`(prompt/model/検証・導出関数source/rules)と`rules_version`(eligible規則: `_token_class`/`is_general_word`/`proper_noun_evidence`のsource・`GENERAL_WORD_MIN_ZIPF`・`CMU_OK_CATEGORIES`・`USABLE_GRADES`・`MAX_ENTITY_WORDS`・wordfreq/pronouncing version)に分離。明示定数`BUILDER_RULES_CONSTANT`/`BUILDER_BUILD_CONSTANT`+source hashのgolden test。継承の復元可否は`rules_version`、resume再利用は`build_version` | `er103_run_entity_table_01.py`; `TestPersistence.test_w10_*`(GOLDEN) |
| W-11 | 推奨 | atomic書込のみ | lockfile(`O_EXCL`、stale 30秒回収、待機5秒、取得不可なら書込skip=runは止めない)+再読込和集合+atomic replace | `_file_lock`/`_save`; `TestPersistence.test_w11_*` |
| W-12 | 推奨 | 逐語検証=供給前script text | provider側で`tts_safe_*`変換後textを`alt_texts`に付け、逐語検証(`_check_texts`)は両方で行う(NER入力は供給前script text) | `Seg.alt_texts`; `TestBuilder.test_providers_*` |
| W-13 | 推奨 | Perplexity memo未確認 | `_resolve_unresolved_entity_for_review`(Stage 1)は`pronun_ledger`(upsert)+neg_storeがrun横断memo(Ledger hit/negative TTLで再呼出しない)。受理判定(`evaluate_for_adapter`)は呼出より前で、**Perplexity結果は受理を左右しない**(None/{}/dictで同一accept)をtest固定。operator報告は「発音の根拠(Ledger/Perplexity調査)」と「固有名詞と認識した根拠(実体表)」を別欄 | `TestAdapterIntegration.test_perplexity_result_*`; `pol.render_operator_report` |
| W-14 | 推奨 | B工程のHR Lock解除根拠 | USER_02 §1-B・§3(HR Lock解除=承認済みB工程)を受入記録へ明記(本委任ではZ実行・Bertie HR Lock解除なし) | RESULT_PACKET_ASRQ_PN4 |
| W-15 | 推奨 | commit手順 | `git commit --only -- <path>`、直前に`git diff --cached --name-status`確認、baseline署名commitは単独path限定(`78a2c7c6e`)、worktree分離で「HEADでも落ちる既存失敗」を切り分け | commit |

## 2. 配線点(file:line、実装後)
| # | 配線点 | file |
|---|---|---|
| 1 | flag/有効判定/holder/表/NER/provider/保存 | 新`er103_run_entity_table_01.py`(`RUN_ENTITY_TABLE_ENABLED`・`is_active_for_run()`・`ensure_table`・`XProvider`/`ZProvider`) |
| 2 | 構築hook(1か所) | `er103_pnap_runner_hooks_01.py` `run_with_alarm_hook(..., _ret_provider=)`・`family_scope`(X)・`emit_alarm_report(level_dir, table)`; Z=`er063_family_z_audio_01.py` `run_tts_stage` |
| 3 | 判定(RET-2/RET-3/audit) | `er103_proper_noun_alarm_policy_01.py` `evaluate_alarm_eligibility(..., entity_table=None)`・`build_alarm_records`・`build_audit_block`・`render_operator_report` |
| 4 | adapter | `er006_secondary_asr_01.py` `_pnap_try_accept`(`entity_table=pnap_ret.adapter_table()`) |
| 5 | 継承 | `er019_family_x_validation_inheritance_01.py` `rejudge_with_current_judge` |
| 6 | Store guard | `er078_reuse_value_guard_01.py` `guard_entry` |
| 7 | model定数 | `er006_model_routing_contract_01.py` `RUN_ENTITY_TABLE_MODEL="gpt-6-luna"`(pricing coverage testに追加) |
| 8 | STOP確認 | NER(新規API呼出)の前に`er062_family_z_structure_01.stop_sentinel_hit(run_dir)`(`<run>/STOP`・`STOP_ALL`・restart-storm marker)。Z=`er063_family_z_audio_01.py:1120 _check_stop_sentinel`と同じ判定、**X runnerにはSTOP確認が無い**(`er019_family_x_audio_production_runner_01.py`にsentinel参照0件を確認)ためXのSTOP確認はRETのNER前確認が唯一(`er103_run_entity_table_01.py` `_stop_hit`)。SDK入口guard(`install_api_stop_guard`)はBaseException系で、NER中のSTOPはそのまま伝播(握りつぶさない) |

## 3. 撤去・残置
- Trialの判定関数複製+drift guard(`ORIG_SOURCE_SHA256`/`source_hashes`)は**Production側に作らない**(`er111_*`はTrial資料として残置、Productionからのimport 0をAST testで固定)。Trial testの旧drift guardは「Trial関数 vs Production本体」の差分testへ再構成。
- `general_in_phrase`・Trial独自usage log・`COST_GUARD_JPY`・`TRIAL_ID`/`ret_trial_02`は移植せず(コードに残さない)。コスト管理=`MAX_NER_CALLS_PER_BUILD=2`+入力上限+cost logger(`cl.install`)。
- `er006_secondary_asr_01` adapter側は`entity_table=`引数1行のみの変更(WIRING_DESIGN_01の「無変更」から、W-04の明示渡しのため変更)。
