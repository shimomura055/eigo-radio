# WIRING_DESIGN_01(ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ①固有名詞 Run Entity Table [RET] / OPEN-472 / 委任_03、2026-10-23)

Status: 設計のみ(Production .py変更0・API 0円・`er111_*`変更0・②UKUS側ファイル編集0)。次=Opus条件Cレビュー(`OPUS_REVIEW_REQUEST_02.md`)→実装委任。
承認根拠: ユーザー原文 `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md`(①②=`APPROVED_FOR_PRODUCTION`、対象X/Z共通、到達目標=X/Z双方`PRODUCTION_WIRED`、必須受入条件9項目=その§2)、UDR #168。
入力: `DESIGN_02.md`(OF-PN2-01〜13)、`TRIAL_RESULT_01.md`、`er111_pn_entity_table_trial_01.py`/`er111_pn_trial_evaluate_01.py`(Trial、読取のみ)。

## 0. 結論(先に)
1. **新module `er103_run_entity_table_01.py`**(表の構築・位置紐づけ・保存/復元・NER)を作り、Trialの共通ロジックを**移植**(コピー+整理、`er111_*`をimportしない)。**`er103_proper_noun_alarm_policy_01.evaluate_alarm_eligibility`に`entity_table=None`引数を足す(RET-2=G5の証拠供給、RET-3=G3)**。`entity_table=None`/空のときの全分岐は現行とバイト一致。Trialの「判定関数の複製+drift guard」方式は撤去し、**実装前に取る現行er103のbaseline署名との一致test**に置換する(§D-5)。
2. **有効条件は単一読取関数 `er103_run_entity_table_01.is_active_for_run()` = `RUN_ENTITY_TABLE_ENABLED is True ∧ pnap.is_active_for_run()`**(PNAP flag有効 ∧ X/Z run scope内)。委任文の「`er109_xz_scope_01.run_scope`再利用」は採らず、PNAPの`run_scope`に乗る(理由=§B-2。`er109_xz_scope_01`は触らない=②と競合しない)。A/B/C・単体呼出・dry_run・scope外は常に不活性=従来と同一。
3. **構築点はX/Z各TTS段の入口hook 1か所**(`er103_pnap_runner_hooks_01.run_with_alarm_hook`にkw-only provider引数を足す。runner本体関数は無変更)。表はrun保存先 `audit/entity_table.json`(X=`<theme_out_dir>/audit/`、Z=`<run_dir>/audit/`)に、**text sha単位のcoverage付き和集合**として保存。resume/regenは「未カバーtextのみNER→和集合」、LRは表を減らさない(§A-5, A-12)。
4. 受理境界(類似度≥0.40・`R_GENERAL_WORD`・P-03・G3二重ASR・数値/否定/脱落・KP/JA除外・差分≤3・HR Lock)は**無変更**。RET-3は「従来不受理になる場合のみ」作用する(§D)。
5. 実装半日、追加費用 NER 平均0.06〜0.12円/記事セット(最大約0.17円)、runtime evidence合計 ≤15円(§F)。②UKUSとの重複は`er078_reuse_value_guard_01.py`・`er019_family_x_validation_inheritance_01.py`・allowlist系の**別hunk/行追加**のみ(§G)。

## A. 配線点表(X/Z別・file:line)
行番号は2026-10-23 HEAD(`17b1b5784`)。種別=新規(新設)/変更(既存コード編集)/無変更(確認のみ)。

| # | 配線点 | X | Z | file:line(現行) | 内容 | 種別 |
|---|---|---|---|---|---|---|
| A-1 | flag・有効判定・run単位holder | 同一 | 同一 | 新`er103_run_entity_table_01.py` | `RUN_ENTITY_TABLE_ENABLED=True`(単一定数)・`is_enabled()`・`is_active_for_run()`(=enabled ∧ `pnap.is_active_for_run()`)・`current_table()`・`run_table(table)`(context manager、finallyで必ず復元)。env/引数/設定dictから変えられない | 新規 |
| A-2 | 表本体・構築・NER | 同一 | 同一 | 新`er103_run_entity_table_01.py` | Trial `EntityTable/Entry/build_entity_table/table_from_saved_entries/merge`を移植。NERは`openai.responses.create`、model=`er006_model_routing_contract_01.RUN_ENTITY_TABLE_MODEL`(`gpt-6-luna`)。単価は登録済み(`er006_model_routing_pricing_coverage_test_01.py:50-52`)。cost loggerの`cl.install`経由で記録(Trial独自usage logは撤去)。**cost logger未init/単価未登録などの設定不備は握りつぶさず伝播**(`er006_secondary_asr_01.py` `_AzureShared._call`の`is_config_stop_error`と同方針)。それ以外の例外はstatus=`LLM_UNAVAILABLE`で縮退(例外を投げない) | 新規 |
| A-3 | 構築hook(TTS前・scope内) | `@pnap_hooks.family_scope("X","b1b"/"a2")`のwrapperが`run_with_alarm_hook`を呼ぶ | `run_tts_stage`が`run_with_alarm_hook("Z",…)`を呼ぶ(`dry_run`時はhookを通らない=API 0維持) | `er103_pnap_runner_hooks_01.py:28-39`(run_with_alarm_hook)、`:78-91`(family_scope)、`er063_family_z_audio_01.py:1291-1303`、X decorator `er019_family_x_audio_production_runner_01.py:886,1232` | `run_with_alarm_hook(family, level_dir, fn, *args, _ret_provider=None, **kwargs)`: scope内・`pnap_supply.clear_registry()`直後・`fn`直前で `if ret.is_active_for_run() and _ret_provider: table = ret.ensure_table(_ret_provider())`、`with ret.run_table(table): fn(...)`。**runner本体関数(`generate_family_x_*_segments`/`_run_tts_stage_impl`)は無変更**。`family_scope`はX用provider(`ret.x_segments_provider(subdir)`)、Zの`run_tts_stage`はZ用provider(`ret.z_segments_provider(plan)`)を渡す | 変更(hooks 2関数+Z 1呼出)+新規provider |
| A-4 | 構築入力 | `<theme_out_dir>/b1b/parts.json`(title/part1-3/in_one_line)+`b1b/b1_support_texts.json`(preview/comment_1-4)+topic_intro(`Today's topic is {title}.`)。a2段=`a2/parts.json`+`a2/a2_support_texts.json`(preview/comment/japanese_titleは日本語=`has_ja_chars`で除外)。**両levelの入力が存在すれば1回のNERにまとめる**(Std/Adv統合1call=OF-PN2-10) | `plan`(ClipSpec列)の`text`。kind∈narrator/dialogue/preview/comment/topic_intro。KP(`kp_*`)/japanese_title除外。**当該levelのplanのみ**(他levelは`run_tts_stage`の引数に無い→Std/Advで最大2 call、§F) | X入力: `er019_family_x_audio_production_runner_01.py:950-1035`(b1b)、`:1356-1420`(a2)。Z: `er063_family_z_audio_01.py:480-491`(ClipSpec) | role判定は単一関数`er020_tts_retry_local_rewrite_01.resolve_narrative_role(segment_id)`(`:125-150`)で`APPLICABLE_ROLES`(`er103:89`)のみ。**KP/JA/HEADING_READOUT除外はprovider側で選別**(OF-PN2-05)。入力textは**供給前script text**(runnerの`results[..]["canonical_text"]`と同じ)。判定時の`canonical_text`(供給後tts_input)への出現は`occurrences()`が位置で確認し、置換された語は既存`supply_map`経路が先に扱う(§D-4) | 新規 |
| A-5 | 保存・resume/regen | `<theme_out_dir>/audit/entity_table.json` | `<run_dir>/audit/entity_table.json` | 新module(`os.replace`のatomic書込。`audit/`作成は`er103_pnap_runner_hooks_01.py:70`と同パターン) | 形式: `{schema, builder_version, status, sha256, meta, entries[], covered_text_sha256[]}`。**再入時**: (i)`builder_version`(prompt A/B・カテゴリ規則・`_token_class`・`MAX_ENTITY_WORDS`のhash)不一致→保存tableは使わない(古い規則で作ったeligible判定を黙って通さない。再構築)。(ii)一致→providerのtext shaのうち`covered_text_sha256`に無いものだけNER→和集合(**entryは減らない**、NER失敗でも既存entry維持)。(iii)全text既カバー=NER 0 call(`--only-segments`・resume・STOP再開・全再実行のどれでも同一入力ならAPI 0)。書込前に再読込して和集合(X b1b/a2の別プロセス並行でも片方のentryを消さない) | 新規 |
| A-6 | 証拠供給(RET-2=G5) | 同一 | 同一 | `er103_proper_noun_alarm_policy_01.py:381-398`(`for d in dp:`の`_noun_checks`呼出)、`:293-300`(シグネチャ) | `evaluate_alarm_eligibility(..., entity_table=None)`を追加。非空のとき**Primary diff 1句ごと**に `grant, ginfo = entity_table.grant_for_phrase(canonical_text, d["canonical"].split())` を計算し、`ls = ledger_surfaces | grant` を**その句の`_noun_checks`(Primary/Secondary両側)にだけ**渡す。`ledger_surfaces`(語集合)自体は変更しない=他句へ漏れない(OF-PN2-01)。None/空なら分岐に入らない | 変更(er103) |
| A-7 | RET-3(G3のSecondary span) | 同一 | 同一 | `er103:358-366`(`elif c_set & noun_tokens:`内の`adjacent_word_changed`不受理) | 現行は「rest tokenがASR側に保存されていなければ即`R_SECONDARY_NOT_ENTITY_ONLY`」。**この不受理になる分岐に限り** `entity_table`が非空なら `entity_table.ret3_check(...)`(Trial `_ret3_check`を表メソッドへ移植)を呼び、(i)spanが当該位置の連続1実体出現(または区切り語なし隣接複数実体)とtoken一致 (ii)重なるPrimary diffがspanに全て含まれ1つ以上含まれる (iii)合成spanにも`_noun_checks`(類似度≥0.40・ASR長≤2×・数値/否定・一般語)+P-03、の**全て**を満たす場合のみnoise扱いで継続。1つでも外れれば現行と同じ不受理(`detail.ret3_rejected`に理由)。**既存の受理経路は無変更** | 変更(er103、**承認済み正式採用に基づくProduction実装**。11-7限定例外ではない) |
| A-8 | 判定結果の保存(audit) | 同一 | 同一 | `er103:399`(`AlarmDecision(True,…)`)、`:460-465`(`alarm_audit_block`)、`:728-734`(`build_audit_block`)、`er006_secondary_asr_01.py:864` | 受理時のみ`decision.detail["entity_table"]={sha256,status,builder_version,per_diff,ret3,entries_used}`と`alarm_labels`(OF-PN2-08、試聴優先度用。受理境界は不変)を付加。`build_audit_block`が`pronunciation_alarm.entity_table`として保存(**受理に使ったentry全体=surface/words/category/grade/eligible/initials**)。表が証拠に使われなかった受理にはキー自体を付けない(既存audit署名不変) | 変更(er103、additive) |
| A-9 | adapter呼出(新規生成) | 同一 | 同一 | `er006_secondary_asr_01.py:1278`(`pnap.is_active_for_run()`ゲート)→`:827`(`pnap.evaluate_for_adapter`)、`er103:714-725` | adapter側コードは**無変更**。`evaluate_for_adapter`内で、引数`entity_table`が未指定のとき`ret.is_active_for_run()`なら`ret.current_table()`を取得して`evaluate_alarm_eligibility`へ渡す(`er103`→新moduleのimportはfunction内lazy=循環回避。新module→`er103`が通常方向) | 変更(er103 `evaluate_for_adapter`のみ) |
| A-10 | 継承再判定 | 継承が走る | (Zは`generate_or_reuse_z`、継承再判定なし) | `er019_family_x_validation_inheritance_01.py:347-366`(`pnap.evaluate_for_adapter`呼出)、`er078_reuse_value_guard_01.py:46-` | 元entryが`PASS_WITH_PRONUNCIATION_ALARM`かつ`ab["entity_table"]["entries_used"]`があるとき、`ret.table_from_saved_entries(entries_used, builder_version=…)`で表を復元して`evaluate_for_adapter(…, entity_table=復元表)`へ渡す(**LLM 0 call・表sha一致不要・当該segment textへの逐語出現のみ確認**=OF-PN2-06(i))。`builder_version`不一致 or `ret.is_active_for_run()`False → 復元しない(=RET由来受理は再判定NG→再生成。境界を厳しくした後に古い受理を黙って通さない)。**現行Ledgerによる受理(`entity_table`キー無し)の継承は無変更** | 変更(5行程度) |
| A-11 | Store再利用guard | 共有Master Audio Store | 同 | `er078_reuse_value_guard_01.py:51-57`(PNAP範囲外ブロック)の直後 | RET由来受理音声(`pronunciation_alarm.entity_table`あり)は`not ret.is_active_for_run()`のとき`blocked=True, reason="ENTITY_TABLE_ALARM_AUDIO_RET_INACTIVE"`(再生成へ)。`asr_judgement`と`asr_judgement_inherited`の**両方**を見る(`ortho_contributed`と同形の`entity_contributed(aj)`をA-1に置く)。**要否の根拠**: scope外は既存のPNAPブロック(`PRONUNCIATION_ALARM_AUDIO_OUT_OF_SCOPE`)が全アラーム音声を止めるため、新guardが追加で効くのは「X/Z scope内でRET flag=Falseにrollbackした場合」のみ。これが無いとrollback後もRET受理音声が再利用され、rollbackの意味が消える。新entryにのみ作用し既存Store entryは不変 | 変更(guard 1か所)+新規関数 |
| A-12 | Local Rewrite | `er020_tts_retry_local_rewrite_01`のLR | `_handle_local_rewrite` | `er063_family_z_audio_01.py:1440-1460`、`er020_tts_retry_local_rewrite_01.py` | **LR時点でNERは呼ばない**(LR呼出内にLLM呼出を足すと遅延・STOP確認・コスト記録の経路が増える)。表はrun中不変(holderは読取のみ)でLR後textにも`occurrences()`で位置判定され、**表は減らない**。LRが新規固有名詞を導入した場合は表に無い=証拠なし=現行と同じ挙動(fail-closed)。LR後textは次の段入口/resumeで`covered_text_sha256`に無いため**その時点でNER→和集合**(OF-PN2-06(ii)を「LR直後」ではなく「次の構築点」で満たす=設計変更、Opus論点) | 新規コードなし(確認のみ)+test |
| A-13 | retry/fallback/regeneration | 同一 | 同一 | `er006_secondary_asr_01.py:1275-1290`(`evaluate_attempt_with_cascade_detail`内) | 受理は引き続き「NG_BOTH ∧ `secondary_not_accepted`」の**最終救済**でのみ評価(`R_JUDGE_STATE`/`R_P3_ENTRY`/`R_BELOW_MIN_SLOT`は現行どおり先に落ちる)。attempt間でtable不変。表由来でも受理しなければ従来のretry→LR→HR。retry上限・fallback順序・HR投入条件は不変。NER自体はretryしない(1回失敗→縮退→現行挙動) | 無変更(test固定) |
| A-14 | kp_vote_check | — | — | `er103`G0(`vote_required→R_DUAL`、roleがKEY_PHRASEなら`R_ROLE`)、KP voter=`er104_kp_three_asr_vote_01.py` | KPはG0除外のまま。A-4のprovider側でもKPをNERへ渡さない。KP3票経路は一切変更しない | 無変更 |
| A-15 | HR Lock経路 | — | — | `er011_human_review_lock_01.py`(`derive_segment_key`/`approve_regenerate`) | 無変更。HR Lock済みBertie 4clipは採用後に人間(またはFableが明示許可した)`approve_regenerate`で解除→再生成(B工程)。RETは自動解除しない・NG_BOTH起点の再評価拡張はしない(OF-PN2-12) | 無変更 |
| A-16 | operator報告 | 同一 | 同一 | `er103_pnap_runner_hooks_01.py:15-25`(`emit_alarm_report`)、`er103:626-`(`render_operator_report`) | 実体表サマリ(`operator_report_lines`移植)を`operator_alarm_report.md`と標準出力へ。`status!=OK`/未構築は「実体表: 未構築または縮退」と明記(SC-6)。非blocking | 変更(report 1関数)+新規 |
| A-17 | Model Routing | 同一 | 同一 | `er006_model_routing_contract_01.py:45-51`(定数群) | `RUN_ENTITY_TABLE_MODEL="gpt-6-luna"`を追加(既存定数と同形、pricing coverage testの対象に追加)。Trialの`COST_GUARD_JPY`/独自usage logは撤去し、`MAX_NER_CALLS_PER_BUILD=2`と入力文字数上限で担保 | 変更(routing定数1)+新規 |
| A-18 | STOP sentinel | 同一 | 同一 | `er063_family_z_audio_01.py:1120`(`_check_stop_sentinel`)、X runnerはSTOP確認箇所を実装委任で特定(`er062_family_z_structure_01.check_stop_sentinel`相当) | NER(新規API呼出)の**前**に`<run>/STOP`・`STOP_ALL`・`*STOP_NOTICE*`を確認し、存在すればNERせず縮退(表なし=現行)。STOPを削除・回避しない | 新規 |

## B. flag設計と隔離
1. **単一定数** `RUN_ENTITY_TABLE_ENABLED = True`(`er103_run_entity_table_01.py`)。読取は`is_enabled()`、有効判定は`is_active_for_run()`の各1関数。env/引数/設定dict/起動script/`.env`から変えられない(AST testで`os.environ`/`getenv`/argparse参照0を固定)。**既定ON**はユーザー正式採用(`APPROVED_FOR_PRODUCTION`、UDR #168・USER_02)に基づく。未承認機能ではないので`DefaultOffIsolation`型は不要(前例=`PROPER_NOUN_ALARM_POLICY_ENABLED=True`、er109の`ORTHOGRAPHIC_EQUIVALENCE_ENABLED`)。rollback=定数をFalseに戻す1行(A-10/A-11でRET由来音声は再生成へ回る)。
2. **scopeの選択(委任文との差分、Opus論点)**: 委任文は`er109_xz_scope_01.run_scope`再利用を想定したが、**PNAPの`er103.run_scope`に乗る**。理由: (i)RETの唯一の消費者は`evaluate_alarm_eligibility`(PNAP)で、PNAP flag/scope外では呼ばれない→PNAP scopeがRETの必要十分条件。(ii)`er109`のscopeはPNAP flagと独立(`er063:1290`コメント)で、PNAP OFF時にもONになる=RETだけONの不整合状態が生じ得る。(iii)`run_with_alarm_hook`はPNAP有効時のみscope+finallyで報告を出す構造で、RETの構築・解除をその`try/finally`に載せると解除漏れが構造的に起きない。(iv)X/Zの入口は既に`er109`とPNAPの2 decoratorが同一関数に重なっており(`er019:886-887,1232-1233`、`er063:1290-1303`)有効範囲は一致する。`er109_xz_scope_01`は触らない。
3. **有効範囲**: A/B/C(`pnap.is_active_for_run()`=False)・単体呼出(scope未設定)・`dry_run=True`(Zはhookを通らない)・X/Z以外=不活性=API 0・出力不変・副作用ファイル0。
4. **LLM失敗=現行同一挙動**(SC-6): timeout/空/不正JSON/refusal/幻覚/cost guard/STOP→status!=OK・宣言entryのみ。例外を投げず、表由来の受理は0、operator報告に縮退を明記。設定不備のみ伝播(A-2)。
5. **旧11-7例外の扱い**: 本件は`APPROVED_FOR_PRODUCTION`済みのため11-7限定例外(新コード経路+flag既定OFF)は使わない。ただしRET-3は`er103`本体のG3を直接編集する(11-7が対象外とする経路)ので、**承認済み正式採用に基づくProduction実装**としてDECISION_LOG/OPEN-472に明記する。`PRODUCTION_WIRED`はFable受入後。

## C. Trial → Production の差分と撤去
| Trial(`er111_pn_*`) | Production | 差分・撤去 |
|---|---|---|
| `er111_pn_trial_evaluate_01.evaluate_alarm_eligibility_pn`(er103判定関数の**複製**+RET差分)、`ORIG_SOURCE_SHA256`/`source_hashes`(drift guard、OF-PN2-11) | `er103.evaluate_alarm_eligibility(..., entity_table=None)`の**本体に統合**(A-6/A-7) | **複製を作らない**。drift guardは意味を失う(複製元=本体になる)→撤去し、「現行er103のbaseline署名との一致test」を新設(D-5)。`er111_pn_*`のtestのうち複製/drift guard依存分は、`er103`本体変更で落ちる。ユーザーの「`er111_*`変更禁止」は本設計委任の範囲。実装委任で変更要否をFableが決める(推奨=`er111_*`は“Trial資料”として残し、複製依存testのみ「Production統合済み」注記付きで撤去/skip) |
| `er111_pn_entity_table_trial_01.py`(表・構築・NER・保存/復元・`run_table`) | `er103_run_entity_table_01.py`へ**移植**。**Production→`er111_*`のimportは0**(AST testで固定) | Trial版`llm_ner_real`(独自usage log・`COST_GUARD_JPY=29`・`COST_CAP_JPY=30`)は撤去し`cl.install`経由+定数上限。`TRIAL_ID`/`SCHEMA_VERSION="ret_trial_02"`は`schema`・`builder_version`へ置換。`current_table()`/`run_table()`の「er103は見ない」前提を、`evaluate_for_adapter`が読む形へ(A-9) |
| ablation用`general_in_phrase`変種(採否差なし=不採用、DESIGN_02 OF-01) | 実装しない(既定False固定の相当) | コードに残さない(撤去) |
| Trialの`alarm_labels`(OF-08) | 移植(A-8)。受理境界は変えない | 残置 |
| Trial評価script(`TRIAL_01/*.py`)・データ | 変更しない(Trial資料) | 残置(Productionからimportしない) |
| 旧状態名`TRIAL_IMPLEMENTED`/「Production未配線・承認前・既定OFF相当」 | OPEN-472/CURRENT_SPECで`APPROVED_FOR_PRODUCTION`→(実装後)`WIRED_PENDING_FABLE`→(Fable受入後)`PRODUCTION_WIRED` | 実装委任でGrep確認(E-Grep) |

**暗黙依存0の担保**: (a)`er111_`のimportがProduction module(`er103_*`/`er006_*`/`er019_*`/`er063_*`/`er078_*`)に存在しない(AST test)、(b)新moduleがDEV専用path(`docs/research/…/TRIAL_01`・`er111_output`等)を参照しない、(c)Trial cache(`llm_cache.jsonl`)を読まない。

## D. 安全条件の不変(受入条件6)と等価性の担保
1. **コードで触れない条件**: `MIN_SPAN_SIMILARITY=0.40`(`er103:102`)、`R_GENERAL_WORD`(`_noun_checks`のall-general判定)、P-03(`:393-397`+`_noun_checks`末尾)、G3二重ASR(`R_SECONDARY_MISSING`)、数値/否定(`_span_has_number_or_negation`)、脱落(`R_DELETION`)、`MAX_DIFFS_PER_SEGMENT=3`(`:92`)、`MAX_ASR_TOKENS_PER_CANON_TOKEN=2`、KP/JA除外(`vote_required→R_DUAL`、`lang`、`role`)、P-01入口(`p3_entry`)、`slot`下限(`R_BELOW_MIN_SLOT`)、HR Lock。`proper_noun_evidence`本体(P-02位置規則込み)・`is_general_word`・`asr_all_general`・`val.capitalized_flags`は無変更。
2. **表が緩めるのは2点だけ**: ①eligible token(非一般語・カテゴリ規則適合・小文字形なし)と実体内部イニシャルへの位置紐づけ証拠(A-6)、②RET-3(A-7)。いずれも現行で不受理になる場合のみ作用。
3. **fail-closed**: 表が無い/空/status!=OK/builder_version不一致/例外 → `entity_table=None`相当=現行。
4. **供給後textと表の整合**: 判定は`canonical_text`(供給後tts_input)で`occurrences()`を取る。供給で綴り置換された語(例 Khaite→Kate)は既存`supply_map`分岐(`_noun_checks`冒頭)が先に扱うため表は関与しない。供給されなかった実体は供給前後で同一文字列。Trial(Seg.pre_text、OF-05)は供給前後の両textで逐語検証したが、Productionの構築入力は供給前script text(A-4)なので「構築時の逐語検証=供給前text」「判定時=供給後textの`occurrences`」の二段になる。この二段で取りこぼす/誤付与するケースを実装委任のtestで固定(Opus論点)。
5. **等価性の担保(drift guardの代替)**: 実装**前**に現行er103で`er103_ret_baseline_signature_01.py`を実行し、署名(D1 HR queue 88件[現行Ledger・Ledger全除外]+D2 保存EN pair+既存test fixture全件の`AlarmDecision`[accept/reason/detail/evidence]のsha256)を`er103_ret_baseline_signature_v1.json`に凍結して**先にcommit**。実装後、`entity_table=None`・空表・無関係表で署名が**バイト一致**することをtestで固定。

## E. test計画
**既存の維持(全PASS必須)**: `er103_proper_noun_alarm_policy_test_01.py`・`er103_pnap_wiring_test_01.py`(AST/hook/scope)・`er019`継承系・`er063`系(Z TTS段/LR/resume)・`er078_reuse_value_guard`系・`er006_secondary_asr`系・`er104_kp_vote_wiring_test_01`/`er104_kp_vote_guard_lifted_test_01`・`er109_*`(wiring_golden・xz_scope・xz_isolation)・`er006_model_routing_pricing_coverage_test_01`・`er078_asr_unified_wiring_static_audit_01`。新module追加が`er094 StaticChecks`/`er078 ja_wiring allowlist`/`er104 allowlist`に影響した前例(`ASR-HOMOPHONE…/WIRING_DESIGN_03.md` §G)があるためallowlistを同時更新。最後に全回帰`run_project_regression.py`(baseline failed 0/errors 0、6,872 passed[`2771b49a9`時点])を実行して比較。
**新規(`er103_run_entity_table_01_test_01.py`ほか)**
1. 位置紐づけ(OF-01): Primary diff句が実体出現範囲に**全出現**含まれるときだけ付与・一部範囲外は付与なし・実体が無ければ付与なし・他句へ漏れない・一般語tokenは付与しない(Will/University/Said)。
2. RET-3厳密(OF-02): 連続1実体spanのみ受理。`Reicher will`→`riker well`・`melos drank`・機能語/数値/否定巻き込み・別実体の偶然隣接・P-03(両ASR一般語)は不受理。comma連結可/and連結不可。現行で受理される経路は無変更。
3. 負例回帰: 偽候補(inventing/canceling/fats/…)・題名中の低頻度一般語(petal/crimson)・見出し語・Title Case一般語・work_title/other_namedのCMU収録token証拠化=0(OF-04)。Iran/Mark型ブロック維持。
4. 構築(OF-03/05/10): 独立裏付けなしentryは独立call B一致時のみconfirmed、call Bは必要時のみ、Std/Adv統合1call、KP/JA/HEADING除外、`MAX_NER_CALLS_PER_BUILD`。
5. 保存/復元/resume(OF-06): 既カバーtextのみならNER 0 call、未カバーtextのみNER→和集合、`builder_version`不一致で破棄、NER失敗でも既存entry維持、並行書込で片方が消えない、atomic書込。
6. 継承再判定: 保存entry復元→LLM 0 call・表sha不一致でも元の受理と一致(Trial SC-10の92/92を再現)、`builder_version`不一致/`is_active_for_run()`Falseで再判定NG、Ledger受理の継承は不変。
7. Store guard: RET由来音声は`RET inactive`でblocked・`asr_judgement`/`asr_judgement_inherited`両方・既存entry不変・scope外は既存PNAP guardが先に止める。
8. **DefaultOn scope isolation**: `RUN_ENTITY_TABLE_ENABLED=True`でも scope未設定/A・B・C/dry_run で `is_active_for_run()`=False・API 0・出力不変・副作用ファイル0。scope内でflag=Falseにすると不活性(rollback)。入れ子・例外時のholder復元(finally)。flag参照がenv/引数に無い(AST)。Production→`er111_*` import 0(AST)。
9. LLM失敗注入(SC-6): 例外/timeout/空/不正JSON/refusal/幻覚/STOP/config STOP(伝播)で、表由来受理0・現行同一・operator報告に縮退明記。
10. 等価性: D-5の署名とバイト一致(表None/空/無関係表)。`evaluate_alarm_eligibility`の既存引数・戻り値・`detail`キーが不変(additiveのみ)。
11. drift guard撤去後の等価test: Productionに判定関数の複製が無いこと(`er111_pn_trial_evaluate`をimportするProduction pathが0)と、D-5署名が代替。
12. retry/fallback整合: 表由来受理でもG1(`secondary_not_accepted`)/P-01入口が先に評価される・受理しなければ従来のretry→LR→HR。
13. 回帰セット(Trial再現): SC-4相当(Bertie 3/3・Kristie Tse・Reicher受理、Melos drank×3不受理、A類41維持、D/E維持)とSC-5b adjudication済み新規受理全件の再現(Production module経由。LLMはcache/mockの固定応答で決定的に)。

**E-Grep(実装委任で実行、撤去・残置の確認)**: `ORIG_SOURCE_SHA256|source_hashes|general_in_phrase|er111_pn_|ret_trial_02|TRIAL_IMPLEMENTED` がProduction `.py`(`er103_*`/`er006_*`/`er019_*`/`er063_*`/`er078_*`)に0件、`未承認・既定OFF`がOPEN-472/CURRENT_SPECのRET記述に残らないこと。

## F. runtime evidence計画(受入条件4・9)と費用・時間
前提: 自然発火に依存しない(`RUNTIME_EVIDENCE_04.md`の教訓)。**正式入口を通る実行**で「構築・scope・証拠供給・受理・audit・HR 0・Store反映」を取る。各run前に`tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run> --out <json>`(rc=3で即停止)。**直列化の明記**: 実音声生成は他agentの有料run(『開いた窓』B工程・FAMILY-Y)と`er006_output/master_audio_store_01/manifest.json`・`raw_usage_log.jsonl`が競合するため、`ACTIVE_TASK.md`の該当Status解除後に直列実行。実装・test・署名・API 0検証は先行して並列。

| # | Family | 内容 | 確認項目 | 見積(出典) |
|---|---|---|---|---|
| Z-1 | Z | **B工程そのもの**: 『開いた窓』停止Bertie関連4clipを、HR Lock解除(`approve_regenerate`)後に正式入口`er063.run_tts_stage(..., only_clips=…)`で再生成(専用の追加runは作らない) | `<run_dir>/audit/entity_table.json`生成(Bertie=confirmed[独立call B]/Framton・Vera=declared)、`pronunciation_alarm.entity_table.entries_used`・`ENTITY_ONLY_ACCEPT`(自然発火した場合)、または正しく読まれて通常PASS(その場合は「表が不要だった」事実を記録)、Bertie分HR 0、Store manifest反映、operator報告に実体表サマリ | TTS約0.6〜1.2円/clip×4+ASR+NER0.06〜0.17円 → **約2〜5円**(出典: `RUNTIME_EVIDENCE_04.md` §2のZ KP 1.05円/3clip実績と`FAMILY-Z-VOICE-PRODUCTION-WIRING-01`の再生成実績) |
| Z-2 | Z | **API 0の決定的検証**: Bertie停止4clipの保存wav+保存転写(`openwindow_4clip_01_result.json`の3行+attempt1・2)を、配線後の正式`run_scope("Z")`内の本物の`evaluate_for_adapter`へ(表は正式hookが構築) | 現行`NO_PROPER_NOUN_EVIDENCE`→RETで`ENTITY_ONLY_ACCEPT`の再現(Trial机上再判定と一致) | 0円(NERのみ0.06〜0.17円) |
| X-1 | X | **保存済み実誤読wavを正式adapterで実ASR判定**: 人名を含むX系既存misread音声(候補: `er006_output/pool_pilot_01/pool_n8_airport_line/b1b/narration/point_two.wav`=`Kristie Tse`[`human_review_queue.jsonl`に5行・Trial SC-4で表受理4/4]、`stephen reicher`を含む保存wav[実装委任でgrep特定])を、`run_scope("X")`内の正式adapter(`evaluate_attempt_with_cascade_detail`)に通す。表は**正式hookが構築**したものを使う | scope(X)有効・`entity_table.json`生成・実Azure+OpenAI ASRでの`ENTITY_ONLY_ACCEPT`と`entity_table`audit・alarm record・`state=PASS_WITH_PRONUNCIATION_ALARM`・HR 0・Store登録 | 実Azure STT(数十秒≒1.7円試算[`RUNTIME_EVIDENCE_04.md` §2単価])+OpenAI transcribe数円未満+NER0.06円 → **約1.5〜3円** |
| X-2 | X | **正式入口の新規生成(入口path証拠)**: 直近のX記事(人名を含む)の`generate_family_x_b1_segments --only-segments`相当で2 segmentを再生成(`--only-segments`=`er019_family_x_audio_production_runner_01.py:2623`) | hookがscope(X)内でtableを構築(`covered_text_sha256`に当該text)、同一run再実行でNER 0 call、`only_segments`でも他segmentのentry保持、`tts_generation_results.json`と`audit/entity_table.json`の整合。発火は自然発火時のみ記録(必須にしない) | 約3〜8円(出典: 同形X 2 segment 7.93円=`PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/RUNTIME_EVIDENCE_02.md`) |
| X/Z-3 | X/Z | **継承再判定(API 0)**: X-1/Z-1で得たアラーム受理entryを保存entryから復元して再判定 | LLM 0 call・表sha不一致でも一致・`builder_version`不一致で再判定NG | 0円 |
| X/Z-4 | X/Z | **A/B/C不変とrollback**: scope未設定・`dry_run`・flag Falseでの署名比較(D-5)とStore guardのrollback挙動 | A/B/C出力不変・flag Falseで現行バイト一致 | 0円 |

**合計見積 約7〜16円(上限15円)**。X-2は2 segmentに絞り、見込みが15円を超える場合は先に`ACTIVE_TASK`費用欄を確認(案件見積300円以下は7-7で自律、超過はFable報告)。必須最小=Z-1・X-1・X/Z-2〜4、X-2は入口path証拠。モデル=最新原則(`PM_GOVERNANCE.md` 25節): NER=`gpt-6-luna`(現行世代の推奨系、本番routing定数に登録)、TTS=`gemini-3.8-flash-lite-tts`(X/Z runner既定)、Primary ASR=`gpt-4o-mini-transcribe`、Secondary=Azure STT。新規モデル選定なし。
**時間**: 実装半日(新module移植+er103差分+hook+guard+test)、署名baseline取得30分(実装前)、全回帰30〜60分、runtime evidence約1時間(直列待ち除く)。**クリティカルパス**: baseline署名commit → er103/新module実装 → test → Z-1(B工程と同時)/X-1。**並列可能**: 新module移植・test作成・署名baseline・Opus条件Cレビュー・②UKUS実装は互いに独立。
**NER費用**: Std/Adv統合は、Xは両level入力が揃えば1 call、Zは`run_tts_stage`がlevel単位のため最大2 call。平均0.06〜0.12円/記事セット(Trial実測平均0.059〜0.067円・最大0.168円)=70円/記事セットの約0.1〜0.2%。Zで1 callに統合する最適化(providerが他levelのscriptも読む)は削減0.05円/セット程度で未カバー判定が複雑になるため**初版は採らず実測後に判断**(量産単価原則3の継続検討項目)。

## G. ②UKUSとの順序・競合整理
| 観点 | ①RET(本設計) | ②UKUS(`UKUS/DESIGN_02.md` §4) | 競合 |
|---|---|---|---|
| 主に触るmodule | `er103_proper_noun_alarm_policy_01.py`(G3/G5/audit)、`er103_pnap_runner_hooks_01.py`、新`er103_run_entity_table_01.py`、`er006_model_routing_contract_01.py` | `er109_asr_orthographic_equivalence_01.py`(`unit_postprocess`拡張点+固定表同梱)、`er109_xz_scope_01.py`(単一flag読取) | **重複なし** |
| 判定の位置 | `evaluate_for_adapter`→`evaluate_alarm_eligibility`(PNAP、NG_BOTH後の**最終救済**) | `er109_xz_scope.decision()`(Primary/Secondary/KP票/再判定の**同値判定**、NG_BOTH前) | 処理順で分離: ②が先に同値と判定すればPNAPへ到達しない。同一segmentに「固有名詞diff」と「綴り差diff」が同居するとPNAP G2(全diffがentity_like)で不受理(現行と同じ。①②とも改善しない=別案件候補)。①②は互いに緩める側にしか働かず、片方が他方の安全条件を外さない |
| 共有Store guard | `er078_reuse_value_guard_01.py:51-57`直後に追加 | ortho範囲外ブロック(`:58-67`)は既存。②が追加guardを足すなら同区間 | **同一ファイル・近接hunk**。commitを分け、後続側が`git pull --rebase` |
| 継承 | `er019_family_x_validation_inheritance_01.py:347-366` | `:305-324`(`decision()`の2点) | 同一ファイル・**別hunk** |
| allowlist系 | `er094 StaticChecks`/`er078 ja_wiring`/`er104`のallowlistへ行追加 | 同様の可能性 | **行追加どうし**=競合しやすい。後続側がrebase時に両方残す |
| golden/署名 | 新`er103_ret_baseline_signature_v1.json`(別ファイル) | `er109_wiring_golden`(LAYER_VERSION更新・X/Z golden再作成=OF-07) | 別ファイル。入力コーパス(D1/D2)が重なるため、②のON/OFFで①の署名(PNAP判定)が変わらないことも実装後に確認 |
| flag | RET flag(PNAP scope依存) | ②flag(er109 scope依存) | 独立。rollback単位も独立 |
| 実音声run | Z-1はB工程と同一 | Bの`forte→speciality`再生成と同一run | 同一runで両方の発火確認が可能(runを分けない=費用重複なし) |

**推奨順序**: ①②は独立にOpus条件C→実装→commit。先に完了した側が先にmain、後続は上記近接hunk/allowlistを解消。B工程(Bertie 4clip+forte→speciality再生成)は**A配線完了後**。②が遅れる場合は①のZ-1(Bertie 4clip)を先に実施し、forteの再生成は②完了後に別clipとして追加。

## H. リスク・未決(Opus論点は`OPUS_REVIEW_REQUEST_02.md`)
- R1 Zの構築がlevel単位で最大2 call(平均0.12円/セット)。
- R2 構築入力=供給前script text(OF-05は供給後textを要求)。D-4の二段で等価と主張、test必須。
- R3 LR直後のNER省略(A-12)はOF-PN2-06(ii)「LR時に変更segmentのみNER」からの設計変更。
- R4 `builder_version`不一致で古い受理は再生成になる(境界を動かす変更時に再生成費用が出る=意図)。
- R5 RET受理の増加で`_resolve_unresolved_entity_for_review`(Perplexity、OPEN-473=クレジット切れ)呼出も増える。失敗時は既存の`stub_note`経路(`er006_secondary_asr_01.py:846`)で非blocking。実装委任でtest確認。
- R6 Z Seed `key_roles`宣言は現行`er103`では未使用(Trialが追加した宣言型R2)。`run_tts_stage`は`story_key`のみ受け取るため、Seedの在処を実装委任で特定(無ければ宣言0=LLM NERのみ。現行同等以上)。
