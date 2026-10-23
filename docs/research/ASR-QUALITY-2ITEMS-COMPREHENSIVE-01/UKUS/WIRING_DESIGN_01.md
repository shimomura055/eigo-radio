# WIRING_DESIGN_01 -- ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り(UKUS) Production配線設計
(UKUS 委任_03 / 2026-10-23 / 設計のみ・コード変更0・API 0円 / 次工程=Opus条件Cレビュー[OPUS_REVIEW_REQUEST_02.md]→実装委任)
承認: ユーザー正式採用 APPROVED_FOR_PRODUCTION(2026-10-23、UDR #168、原文=`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md`)。対象=Family X/Z。A/B/C凍結(PM_GOVERNANCE 27-3/27-7)。
入力=Trial成果(`er111_ukus_spelling_trial_01.py`、`er111_ukus_pairs_v1.json`、DESIGN_02、OPUS_REVIEW_01 OF-UKUS-01〜14、TRIAL_RESULT_01)。**本設計は承認済み仕様(Trial判定ロジック・固定対表・安全条件)を変えず、Production経路へ移すだけ。**

## 0. 結論(設計の骨子)
1. **統合点は1か所**: `er109_asr_orthographic_equivalence_01.evaluate` の opcode ループ内(:729-761)。既存判定が不合格になった「同数・語unit・1:1のreplace span」にだけ、位置別に固定対表を参照する救済(`SpanRecord(rule="ukus_spelling_variant")`)を追加する。**既存判定が合格するspanには一切触れない**ので、既存PASSの結果(reason/rules/warnings/spans)はバイト同一=PASS→NG 0は構造保証。
2. **既存hookは全て `er109_xz_scope_01.decision()` → `_evaluate_cached` → `e109.evaluate` を通る**(§1で全hookを列挙、Grep確認済み)。hook側のコード変更は不要(Store再利用guardの1条件追加のみ)。
3. **flagは単一定数 `UKUS_SPELLING_EQUIVALENCE_ENABLED=True`(既定ON)。親 `ORTHOGRAPHIC_EQUIVALENCE_ENABLED` がFalseなら本層も不活性。読取は X/Z run scope内の `er109_xz_scope_01.is_ukus_active_for_run()` 1関数のみ。** `evaluate(..., ukus=False)` の既定はFalse(scope無し・offline tool・A/B/Cは従来どおり)。
4. 固定対表は `er109_ukus_pairs_v1.json`(Production名)を同梱し、DEV(`er111_*`)へ依存しない。

## 1. 配線点表(file:line はいずれも現HEAD)
| # | 配線点 | file:line | 変更 | 新層が自動で効く根拠・確認方法 |
|---|---|---|---|---|
| W1 | 判定本体 `evaluate` のopcodeループ(同数語spanの救済) | `er109_asr_orthographic_equivalence_01.py:709`(def)、`:729-761`(loop)、`:743`(bad検査)、`:748`(`_judge_span`) | **変更**: `evaluate(..., ukus: bool=False)`。span不合格(`bad`または`rec.equivalent==False`)かつ `ukus` かつ 同数の語spanのときだけ `er109_ukus_spelling_01.rescue_span(...)` を呼び、成功時は位置ごとのSpanRecordに置換して継続。他の分岐・早期returnは不変 | 既存PASS spanは`:748`で合格し救済関数は呼ばれない(構造)。差分test=§6 T-A |
| W2 | 結果record | `er109...py:512-549`(SpanRecord/EquivalenceResult/audit) | **追加のみ**: `EquivalenceResult.ukus_pairs: list=[]`。`audit()`は **ukus_pairsが非空のときだけ** `ukus_pairs`/`pron_differs_n` キーを追加(空なら既存と同一dict) | 非UKUS行のaudit署名は不変(version文字列を除く) |
| W3 | LAYER_VERSION | `er109...py:32` | `"er109_orthographic_equivalence_v1_proto_aho02"` → `"er109_orthographic_equivalence_v2_ukus01"` | §4-3(golden影響) |
| W4 | 新module | (新規)`er109_ukus_spelling_01.py` | 固定対表ロード(1回/process、sha検証)・`PairTable`・`canon_entity_flags`・`rescue_span`。er109は**ukus=Trueのときだけ遅延import** | `evaluate`既定経路ではimportされない |
| W5 | scope module(flag読取・メモ) | `er109_xz_scope_01.py:97-101`(`_evaluate_cached`)、`:131`(`eq.version != LAYER_VERSION`)、`:125-139`(decision) | **変更**: `is_ukus_active_for_run()`(=`is_active_for_run() ∧ e109.ukus_is_enabled()`)を追加。`_evaluate_cached(canonical, text, ukus)` とし、flag値をcache keyに含める(flag値はメモ外で毎回計算=既存M4と同じ原則)。`decision()`が `ukus=is_ukus_active_for_run()` を渡す | LRU汚染防止: ON/OFF切替・test monkeypatchで古い結果を返さない(T-F)。`:131`はversion一致のまま通る |
| W6 | Primary adapter(tail/後段) | `er006_secondary_asr_01.py:1132-1141`(`decision`→`ORTHO_LABEL`)、`:1164-1168` | **変更なし** | `decision()`経由。T-E1 |
| W7 | Secondary `_secondary_accept` | `er006_secondary_asr_01.py:1206-1210`、`:1254-1256` | 変更なし | 同上 |
| W8 | er078 judge: Primary記録 / P-06 span解除 / Secondary precheck / KP票印 | `er078_asr_unified_judge_01.py:361-427`(`_ortho_record_primary/_ortho_unlock_primary/_ortho_secondary_precheck/_ortho_mark_votes`)、呼出`:484,:543,:664,:687-722` | 変更なし | **P-06の安全性**: `explain_protected`(`er109_xz_scope_01.py:195-283`)は値DIFF/否定差を「同値span内に存在する場合のみ」解除する。UKUS spanは(a)数字を含まない、(b)否定語を含まない(固定表の全active語を `uj.negation_counter` と数字検査で走査して該当0、2026-10-23確認)ので **UKUS spanは値DIFF/否定差を説明(解除)できない**=`value_diff_not_explained_by_span`/`negation_diff_outside_equivalent_spans`となり従来どおりNG_PROTECTED。構造test T-D |
| W9 | KP英語3-ASR投票 | `er104_kp_three_asr_vote_01.py:246-258`(`_classify`)、`:257-290`(`make_voter`) | 変更なし | `_classify`→`decision()` |
| W10 | er019 継承再判定(X) | `er019_family_x_validation_inheritance_01.py:325-340` | 変更なし | `ortho_scope.decision()` 2か所 |
| W11 | Store再利用guard `ortho_contributed` | `er078_reuse_value_guard_01.py:58-66`、`er109_xz_scope_01.py`(`ortho_contributed`) | **追加**: `ukus_contributed(aj)`(site audit の `er109.rules` に `ukus_spelling_variant` を含む/`ukus_pairs_n>0`)。`ukus_contributed ∧ not is_ukus_active_for_run()` なら再利用ブロック(reason=`UKUS_SPELLING_EQUIVALENT_AUDIO_OUT_OF_SCOPE`)。親flag OFF/scope外/A/B/Cは既存`ortho_contributed`で既にブロック(UKUS受理entryも `orthographic_equivalence.applied=True` を持つため) | **UKUS flagだけOFF(親ON)** のrollback時に、UKUS受理音声がX/Zで再利用されない整合のための追加。T-E5 |
| W12 | retry / fallback / regen / resume | Z: `er063_family_z_audio_01.py:748-796`(`generate_or_reuse_z`: 再利用は `reuse_key`一致∧status OK∧sha一致∧`guard_entry`通過)、X: `er019_family_x_audio_production_runner_01.py`(guard_entry経由) | 変更なし | UKUS受理は「ASR段のPASS」であり、retry回数・cooldown・Gate・LRの上限は不変(PASSした時点でretry/LRに入らない=不要retry削減)。受理済みentryは`asr_judgement`に`ukus_pairs`が記録される(監査) |
| W13 | HR Lock経路 | `er109_hr_lock_rejudge_01.py:66-72`(`_code_commit`のdirty検査対象一覧)、`:169`(version記録) | **追加のみ**: dirty検査対象に `er109_ukus_spelling_01.py` を追加 | HR Lockそのものは残置(解除は人間承認/明示CLIのみ)。HR Lock済みsegmentの再判定でUKUS分も`decision()`経由で候補列挙される |
| W14 | LR(Local Rewrite) | `er020_tts_retry_local_rewrite_01.py:181`(`identify_ng_span`)、`:708`(`run_local_rewrite_recovery`) | **変更なし**(DESIGN_02 §6 案Hは別案件、本配線に含めない) | UKUSでPASSするので3回NG→cooldown→LRに到達しない |
| W15 | A/B/C(凍結) | `val.BR_AM_SPELLING_PAIRS`(`er006_preprod_hardening_01_validation.py:56-62`)ほか | 変更なし | scope無し→`decision()`がNone=従来どおり。golden `pre_wiring_signatures_none_01` 完全一致test(既存`er109_wiring_golden_test_01`) |

**hook自動伝播の確認(Opus論点1)**: Production全体で `e109.evaluate` を直接呼ぶのは `er109_xz_scope_01._evaluate_cached`(`:101`)のみ(Grep: 他の呼出は全て `er109_*` のoffline/評価script)。他の全hook(W6〜W10)は `ortho_scope.decision()` を経由する(付録A)。**実装時にこのGrepを再実行し、test `test_only_xz_scope_calls_evaluate`(AST)で固定する。**

## 2. 判定ロジック(Trialからの移植、仕様不変)
- Trial `evaluate_trial` の「既存PASSならそのまま返す→NGなら同じunit列・整列で位置別判定」を、**ループ内の局所救済**へ形を変えて移す(同じ判定、呼出構造のみ変更)。位置別規則(OF-01/02/05/06、DESIGN_02 §2)・直接対のみ(推移しない)・AMB一方向・語幹+同一接尾・ハイフン複合・数/記号/略語spanは非関与・欠落/付加は従来NG、は全てそのまま。
- **構造変更の同等性検証(実装時必須の差分test)**: 保存6,137行+合成ケース(Trial test 27件の入力)に対し、`er111.evaluate_trial` と 新`evaluate(ukus=True)` が (equivalent, reason, rules, warnings, ukus_pairs) で全件一致すること。結果を保存してからTrialを退役し、以後は固定expectedとの一致testに置換する。
- `canon_entity_flags` は canonical文のtoken列に対し e109 `_TOKEN_RE` で独立に走査する(Trial同様)。unit列との長さ不一致はfail-closed(救済しない)。計算は救済候補が出たときだけ(遅延)。

## 3. 固定対表の同梱とロード
- 同梱: `er109_ukus_pairs_v1.json`(`er111_ukus_pairs_v1.json`を **内容そのまま** `git mv`で改名。1,539,181 B、active 6,361対[T1 6,356+規則由来5]、Tier-2 inactive 8,718対、denylist 146、AMB一方向168、pron_differs 52)。`meta`に許諾文(VarCon/SCOWL 2020.12.07 著作権+許諾、`meta.license`)・入力sha256(scowl `70f41f69…`、varcon `75af63da…`)・build_versionを保持(Trialで確認済み。test `test_license_and_input_hashes`を移植)。
- ロード: `er109_ukus_spelling_01.table()`(`lru_cache(1)`)で **1 process 1回**、初回のNG経路でのみ遅延ロード(Trial実測0.017〜0.020秒、追加判定p95 0.10〜0.14ms)。Tier-2は`active=false`のまま保持しロード時に無視(有効化は仕様変更=ユーザー承認+Opus)。**ロード時に`pairs`のsha256を`meta.pairs_sha256`と照合し、不一致なら例外=`decision()`のfail-closed経路[従来判定+sinkへエラー記録]。**
- 辞書更新手順(開発ツール): `er109_ukus_pairs_build_01.py`(`er111_ukus_pairs_build_01.py`をgit mvで改名、**Productionからimportされない**開発ツール。入力=`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/work/{varcon,scowl}`)。更新は (1) denylist/入力変更 → (2) `--write`で再生成(決定的) → (3) 差分対を人手確認(PAIRS_REVIEW形式) → (4) **LAYER_VERSIONのsuffix更新(`ukus02`…)+X/Z golden再作成** → (5) Opus/Fable確認(対表の追加・Tier昇格は仕様変更=ユーザー承認)。手順を`er109_ukus_spelling_01.py`冒頭コメントと`CURRENT_SPEC`に記載。

## 4. flag・隔離・LAYER_VERSION
### 4-1 flag
| 項目 | 設計 |
|---|---|
| 定数 | `er109_asr_orthographic_equivalence_01.UKUS_SPELLING_EQUIVALENCE_ENABLED = True`(ユーザー正式採用後のrollbackスイッチ。未承認機能の既定OFF隔離=11-7限定例外ではない) |
| 読取関数 | `ukus_is_enabled()` = `bool(UKUS_…) ∧ is_enabled()`(親`ORTHOGRAPHIC_EQUIVALENCE_ENABLED`がFalseなら常にFalse)。**run scope判定を含む唯一の読取は`er109_xz_scope_01.is_ukus_active_for_run()` = `is_active_for_run() ∧ ukus_is_enabled()`** |
| 変更経路 | env/引数/設定dict/起動scriptから変えられない(コード定数のみ)。`evaluate`の`ukus`引数は **production非testコードでは `er109_xz_scope_01._evaluate_cached` だけが渡す**(AST test)。直接呼出(offline tool・既存test)の既定はFalse=従来 |
| scope | X/Z run scope内のみ(scope外=A/B/C・単体は`decision()`がNone)。A/B/C・単体は従来どおり |
| rollback | Falseにすると X/Zでも従来判定へ戻る。UKUS受理済みStore entryはW11で再利用ブロック→再生成(再生成費用が出る旨をコメントに記載。既存`ORTHOGRAPHIC_EQUIVALENCE_ENABLED`と同型) |

### 4-2 DEV依存0(受入条件3)
- Productionから `er111_*` をimportしない。`er109_ukus_spelling_01.py`は`er111`に依存せず、コードはTrial moduleから**コピーして改名・整理**する。
- Trial資料の扱い: `er111_ukus_spelling_trial_01.py` / `_test_01.py` / `er111_ukus_trial_eval_01.py` / `er111_ukus_trial_cases_01.py` は、差分test(§2)の結果を`WIRING/DIFF_TEST_RESULT_01.json`に保存してから **撤去**(git履歴+TRIAL_01/に証跡残置。Production複製との二重管理を避ける)。撤去後Grep(`er111_ukus`)残存0を確認する。
- 許可リスト整理対象: `er109_xz_isolation_01_test_01.py:185-192`(dev_trial許可の`er111_ukus_*`)、`er109_asr_orthographic_equivalence_01_test.py:218-219`(`er111_ukus_`をskip)、`er064_kp_int_01_test_01.ProductionUnchanged`(git diff許可リスト)。撤去後は`er111_ukus_*`の許可を削除し、新moduleを「Production module」として検査対象に入れる。

### 4-3 LAYER_VERSION・golden(OF-07(c))
- 参照箇所のGrep(2026-10-23): `LAYER_VERSION`の機能的な比較は `er109_xz_scope_01.py:131`(結果versionとの一致)・`:214`(`explain_protected`)のみ=結果は常に現行定数で生成されるので不一致にならない。保存済みentryの`orthographic_equivalence.version`(`er109_xz_scope_01.py:146`)・`er104:206`(`ortho_layer_version`)・`er109_hr_lock_rejudge_01.py:169,235`は**監査記録のみ**で再利用判定に使われない(`ortho_contributed`は`applied`/label/warningsのみを見る)。→ **既存Store entryのversionが旧でも再利用可否は変わらない**。
- golden: `er109_wiring_golden_test_01.py`は scope無し=配線前署名と完全一致(`pre_wiring_signatures_none_01`)、X/Z=`post_wiring_changed_{X,Z}_01`との一致。versionは**X/Zのortho適用行の署名**にだけ現れる(scope無しには出ない=W5/W6の`is_active`ガード)ため、`pre_wiring_signatures_none`は不変、`post_wiring_changed_X/Z`のみ再作成。手順: 配線前HEAD overlay(`ER109_OVERLAY`)でbaselineを採り直し、`er109_wiring_golden_build_01.py` の `SYNTHETIC`にUKUS合成行(c12 speciality/specialty ×Primary/Secondary/KP、負例=固有名詞・綴り差+実誤読・数/否定同居)を追加→ fixture再作成。変化行の全件目視分類(version文字列のみ/新規PASS[UKUS]/PASS→NG=0)を`WIRING/GOLDEN_CHANGE_01.md`に保存。
- 副作用の抑制: auditの新キー(`ukus_pairs`/`pron_differs_n`)はUKUS適用時のみ出す(W2)ので、非UKUS行の変更はversion文字列のみ。

## 5. 安全条件(受入条件6・7)
| 条件 | 設計 | 検証 |
|---|---|---|
| PASS→NG 0 | W1の構造(既存合格spanは救済関数に入らず結果不変)+ `ukus`False時は完全に従来 | T-A(保存6,137行、PASS→NG 0、PASS行のreason/rules/warnings変化0)、T-B(合成) |
| 固有名詞らしさ(entity token)除外 | **canonical側**で判定(全大文字/語中大文字/非ASCII/文中の大文字始まり/文頭大文字+次が大文字語)。位置: `rescue_span`内で候補1語ごと(OF-02の実装位置をそのまま)。**①RET表は参照しない**(理由§7)。CMU-OOV(`jewellery`等)は固有名詞判定の根拠にしない | T-C(Aluminium City/Jewellery Quarter/Centre Street/Grey Gardens=NG維持、US形固有名詞→UK形NG) |
| 一般語・数字・否定の安全 | 数/記号/略語を含むspanは非関与。対表のactive語に数字・否定語0(確認済み、test化)。UKUS spanは値DIFF/否定差を説明できない(W8) | T-D |
| `pron_differs`監査 | 対ごと(52対)の`pron_differs`を`ukus_pairs[]`に記録。**warningsには入れない**(`PASS_WITH_WARNING`/`ORTHO_*`写像=事後試聴負担を作らない)。集計は`audit()`の`pron_differs_n`。運用: 実run後のRUNTIME_EVIDENCEに件数を報告(c12 speciality=該当) | T-G |
| 意図しない誤PASS | 直接対のみ・AMB一方向・Tier-2 inactive・denylist 146・語数違い/欠落/付加は従来NG | T-B/T-H+差分test |
| 失敗終了時の最終成果物 | UKUS層は判定のみ。ASR NG時のretry/LR/HR Lock/STOPで保存される成果物は既存どおり不変 | 既存STOP系test |

## 6. test計画
| ID | 内容 | 場所 |
|---|---|---|
| T-A | **差分test**: Trial `evaluate_trial` ⇔ 新`evaluate(ukus=True)` 全件一致(保存6,137行+合成)。PASS→NG 0、er109 PASS行のreason/rules/warnings変化0、NG→PASS全件の原因が`ukus_spelling_variant`のみ。Trial退役後は固定expected(`er109_output/ukus_wiring_01/stored_regression_expected.jsonl.gz`)との一致testとして**回帰化** | 新規 `er109_ukus_spelling_01_test_01.py`+fixture |
| T-B | Trial test 27件の移植(c12両方向、代表対、活用/所有/ハイフン、AMB一方向、意味が違う対、mum/mom、Tier-2 inactive、byte-identical、table性質[ライセンス・入力hash・OF-03/04・denylist・決定性・推移なし]) | 同上 |
| T-C | 固有名詞除外(canonical側)境界ケース | 同上 |
| T-D | 対表のactive語に数字・否定語が無い、UKUS spanがP-06で値DIFF/否定差を説明できない(`explain_protected`へ実spanを通す)、数・否定を含む文との同居ケースはNG維持 | 同上+`er109_xz_scope_01_test_01.py`追記 |
| T-E1〜E5 | hook別: Primary/Secondary/KP voter/er019継承再判定/Store guard(UKUS flagのみOFFでブロック)でc12が OFF=NG→ON=PASS、rules=ukus、warnings空、retry/LR/HR 0(mock) | `er109_xz_scope_01_test_01.py` |
| T-F | cache: ON/OFF切替・scope切替でLRUが古い結果を返さない。`evaluate(ukus=…)`をxz以外が渡さない(AST)。`UKUS_…`の代入がtest以外に無い。`test_only_xz_scope_calls_evaluate` | `er109_xz_isolation_01_test_01.py` |
| T-G | `pron_differs_n`・`ukus_pairs`がauditに入り、`warnings==[]`/`verdict=="PASS"` | 同 |
| T-H | 既存: `er109_asr_orthographic_equivalence_01_test.py`(29)・`er109_xz_scope_01_test_01.py`(56)・`er109_xz_isolation_01_test_01.py`(14)・`er109_wiring_golden_test_01.py`(6、fixture再作成後)・`er109_bfix_test_01.py`(15)全PASS | 既存 |
| T-I | **DefaultOnScope型**: scope無し→UKUS不活性(従来署名一致)、親flag OFF→不活性、UKUS flag OFF→従来(X/Z署名=pre-UKUS)、ON→UKUS | 新規 |
| T-K | ①RETとの両方ON相互作用(§7) | 新規 |
| T-J | 必須Regression: `run_project_regression.py`全回帰(Trial撤去後のコレクション数を記録、failed 0/errors 0)、Validator系・integration(er019/er063/er026 e2e mock)・`er064 ProductionUnchanged`許可リスト更新 | 既存+runner |

## 7. ①RET(OPEN-472)との順序・競合
- 共有/近接ファイル: `er109_xz_scope_01.py`・`er078_reuse_value_guard_01.py`・`er078_asr_unified_judge_01.py`・`er109_xz_scope_01_test_01.py`・`er064_kp_int_01_test_01.py`(許可リスト)・`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`。**UKUSが触るのは er109本体・er109_xz_scope(cache key+flag読取+`ukus_contributed`)・reuse guard(1条件)のみ。RETの本体はPNAP(`er103_*`)側で、PN側の配線設計は並行作成中=本書作成時点で未確認**。重なり得るのは reuse guard と test許可リストとSSOTの3点だけ。
- commit順の推奨: **②UKUSを先にcommit(変更が小さく独立)→①RETがrebase/再確認して重なりを解消**、または両者独立で `git add` を各自のファイルに限定し、共有ファイルの編集直前に`git status`確認→自分の行のみ→即commit(CLAUDE.md運用)。`LAYER_VERSION`の取り合いは無い(RETはer109を変更しない設計)。
- **相互作用(両方ON)**: 実体token(固有名詞)は②対象外=canonical側の固有名詞らしさで必ずNG維持→①RET/PNAP(別層・別PASS種別`PASS_WITH_PRONUNCIATION_ALARM`)の判定に委ねる。**②は①のRET表を参照しない**(理由: `evaluate`は純関数でrun文脈を持たず、runごとのRETを読むとLRU cache keyにRET shaを含める必要が出てW1の構造保証[純関数性]とcache設計が複雑化する。②の除外は保守側[fail-closed]なので、①の表が無くても安全側)。T-K: 「`Centre Street`(canonical)↔`Center Street`(ASR)」は②でNGのまま、②のspan記録が空(rulesに`ukus_spelling_variant`が現れない)こと、両flag ONで①の判定が②によって変わらない/逆も然りを確認。実体表の読み取り専用共有は将来拡張として記録のみ。

## 8. runtime evidence計画(受入条件4・9、費用見込み ≤ 10円)
| ID | 内容 | 費用(見込み) |
|---|---|---|
| E-Z | **Z**: 『開いた窓』Adv `full_story_part3_c12`(canonical `…Vera's speciality.`)を **原稿 speciality のまま正式経路で再生成**(ユーザー指示B)。事前に当該clipのresume状態を安全に解除(§9)。ASRが`specialty`でも`ukus_spelling_variant`でPASS、`asr_judgement.orthographic_equivalence.sites[].er109.rules`に`ukus_spelling_variant`、`ukus_pairs`に`speciality/specialty`(`pron_differs`記録)、attempt=1、LR 0、cooldown 0、HR 0、Z結果への登録(status OK、`audio_text_deviation`なし) | TTS 1+ASR 1+Azure 1 ≈ 0.4〜0.8円(失敗時上限=retry3回で約1.5円) |
| E-X | **X**: 保存データにX UK綴りNG事例なし(2026-10-23 Grep: er019/er021/er025 `*tts_generation_results*`のcanonicalでUK専用綴り語を含むsegment=0)。よって (a) **API 0**: 合成・保存X転写を `run_scope("X")` の正式経路(`er109_runtime_evidence_04_01.py`型harness、adapter/guard/rejudge/voter)で再判定しUKUS PASSと負例NGを確認。(b) **実TTS 1clip**: X正式のTTS generator単文(UK綴りを含む1文)を本番TTS+Primary/Azure ASRへ。ASRが米綴りに書いた場合の発火を実測。ASRが英綴りのままなら「発火せず通過」も記録(発火しない事実も記録)。いずれも正式経路の関数を使う(実装時に単文入口を確認) | (b) ≈ 0.5〜1円 |
| E-N | 非発火確認: scope無し(A/B/C相当)で同入力→従来どおりNG。UKUS flag False→従来 | 0円 |
| E-R | 全回帰(§6 T-J) | 0円 |
合計見込み ≈ 2〜4円(上限10円)。案件見積300円以下・承認済みScope内=都度承認不要(PM_GOVERNANCE 7-7)。有料run開始前に`stop_scope_check_01.py`をrun-dir指定で実行しrc確認。

## 9. c12 LR上書き解除手順(安全性。Opus論点4)
c12の現状: Adv(b1b)の結果entryは `status=OK`・`canonical_text="…Vera's speciality."`・`asr_text="…Vera's forte."`・`audio_text_deviation`あり(`er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/b1b/audit/tts_generation_results.json` の `segments.full_story_part3_c12`)。**再利用判定は`reuse_key`(canonical sha・voice・style・backend)と`guard_entry`のみ**(`er063_family_z_audio_01.py:748-796`)で、canonicalが同一(`speciality`のまま)なので **何もしないと現行entry(`forte`音声)が再利用される**。LR採択結果は`er011_output/local_rewrite_recovery/run_sf_prod_01/b1b/local_rewrite_recovery_full_story_part3_c12.json`。解除は**当該1clipの結果entryの無効化のみ**とし、他clip・他levelの結果・HR Lockの既存安全装置には触れない:
1. **保全**: `b1b/audit/tts_generation_results.json`・`b1b/audit/review_lock_state.json`・c12のwav(`narration/full_story_part3_c12.wav`と`_original`)・LR json・`attempt_history`該当行を `b1b/audit/preserved_c12_forte_01/` へコピー(sha256一覧つき)。元の追記型ログ(attempt_history等)は触らない。
2. `tts_generation_results.json` の `segments.full_story_part3_c12` **のみ**を、`superseded_by_ukus_regen`マーカー付きで別fileへ退避しsegments辞書から除く(1キー)。`review_lock_state.json`のc12 entryがHR Lock(未解決)ではない(RESOLVEDまたは無し)ことを確認する。**累積カウンタ(`cumulative_tts_attempts`、budget_guard)が再生成の上限判定に効くか、実装時に`er019`/`er063`のコードで確認**し、効く場合の扱いはOpus/Fableに諮る(推測で書き換えない)。Store(Master Audio Store)にc12のcanonical hash(`canonical_text_hash`)・voice Aoedeの登録があるかも確認し、あれば同様に無効化対象へ含める(Zの再利用はresults経由が主。要確認)。
3. 再生成: 既存の `er026_family_z_fiction_production_runner_01.py --only-clips full_story_part3_c12`(`:2075,:1617,:1625`。当該clipのみ、全体自動再生成なし)。**追加の独自スクリプト・監督ループ・ラッパを作らない。再起動は委任文で許可された回数のみ。**
4. 検証: 結果entryの`asr_text`が`specialty`(または英綴り)、`asr_judgement`に`ukus_spelling_variant`、`audio_text_deviation`なし、wav sha更新、他clip(Bertie HR Lock対象・Std a2)のentry shaが不変(全clip sha一覧の前後差分=c12のみ)。失敗(ASR NG→cooldown→LR)になっても**LRは既存どおり働く**(UKUS層が救済できなかっただけ)ので、その場合は保全copyから元のentry(`forte`版)を復元して停止・報告。
5. 範囲: ユーザー指示B「Advancedの`forte`を`speciality`に戻し、原稿と音声の一致を確認」の実施手順。Std(a2)のc12は`Vera needed only seconds…`で対象外。

## 10. 撤去・残置
| 対象 | 扱い |
|---|---|
| `er111_ukus_spelling_trial_01.py`+`_test_01.py`、`er111_ukus_trial_eval_01.py`、`er111_ukus_trial_cases_01.py` | 差分test実行・結果保存後に撤去(git履歴・TRIAL_01/に証跡残置) |
| `er111_ukus_pairs_v1.json`/`er111_ukus_pairs_build_01.py` | `er109_ukus_pairs_v1.json`/`er109_ukus_pairs_build_01.py`へ改名(内容不変) |
| 許可リスト(`er109_xz_isolation_01_test_01.py:185-192`、`er109_asr_orthographic_equivalence_01_test.py:218-219`、`er064 ProductionUnchanged`) | `er111_ukus_*`の許可を削除し、新moduleをProduction扱いで検査 |
| DESIGN_01の旧方式(key正規化/breame補助辞書/Tier-2 PASS_WITH_WARNING/wordfreq規則) | DESIGN_02で廃止済み。Production実装に混入しない(Grep: `wordfreq`・`breame`・key正規化関数がProduction moduleに無いことをtest化) |
| `val.BR_AM_SPELLING_PAIRS`(13ペア、A/B/C共有Validator) | **凍結残置**(触らない。X/Zでは新層が上位互換として働き、13ペアの`normalize_text`は従来どおり先に効く) |
| 旧`er109 v1`のX/Z配線(OPEN-459) | 維持(本層は同じ`decision()`の内側に追加) |
撤去後Grep: `er111_ukus`/`wordfreq`/`breame`の残存を実装後に実行し`RESULT_PACKET`(4)へ。

## 11. 実装手順(次委任)とクリティカルパス
1. Opus条件Cレビュー(OPUS_REVIEW_REQUEST_02.md)→Fable照合。
2. 実装: W1〜W5・W11・W13 → T-A差分test(Trial撤去前) → Trial撤去・改名 → golden再作成 → 全回帰。
3. runtime evidence(E-Z/E-X/E-N)→ RUNTIME_EVIDENCE_01.md。
4. SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/ACTIVE_TASK)→ commit/push(`git add`は対象ファイルのみ)。
5. **PRODUCTION_WIRED判定はFable受入(コード配線とTrial成功だけで判定しない)**。X/Z別に「実動作=承認仕様」を確認(受入条件9)。
並列化: ①RETの実装とは独立(§7)。テスト作成・golden baseline採取(overlay)は実装と並行可。c12再生成(E-Z)は配線完了後に直列(前工程出力依存)。所要見込み: 実装+test 2〜3時間、evidence 0.5時間。

## 付録A hook直接呼出のGrep(2026-10-23)
- `e109.evaluate`の非test・非offline-tool呼出: `er109_xz_scope_01.py:101`のみ。
- `ortho_scope.decision`/`xz.decision`呼出: `er006_secondary_asr_01.py:1135,1207`、`er019_family_x_validation_inheritance_01.py:328,339`、`er104_kp_three_asr_vote_01.py:257,286-289`、`er078_asr_unified_judge_01.py:416-427,716`。
- `ortho_contributed`: `er078_reuse_value_guard_01.py:63`。
