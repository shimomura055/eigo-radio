# WIRING_DESIGN_01: A-1(参照語の不定化)Production配線の設計・準備

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_05 / 2026-10-23 / OPEN-474 / 本書は設計のみ(Production .py・template・test変更0、API 0)。
承認: A-1=APPROVED_FOR_PRODUCTION(ユーザー決定2026-10-23、UDR #169、原文=docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_02.md §2)。配線実施はA-3追加検証(委任_04)の採否判断後にまとめて行う。配線前にOpus条件Cレビュー(論点=OPUS_REVIEW_REQUEST_02.md)。
A-1仕様(Trial実証済み、DESIGN_02/TRIAL_RESULT_01/OPUS_REVIEW_01): this/that→a/an(単数可算名詞の限定詞のみ)、him/her/me/us→someone、固定表現・不可算・代名詞/副詞/接続詞のthat・it/them/these/thoseは置換しない、本文存在・5語以下・既存安全条件は維持。OPEN-476(`bound→bind`)は触らない(DEFERRED)。

## 1. 変更対象(file:line、現行HEADで再確認済み)
| # | ファイル:行 | 現状 | 変更(A-1) |
|---|---|---|---|
| T1 | `er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt` :7 | 自問文「既にそのままで自然ならdisplay_phraseと同一」 | 「規則5該当の参照語を含む場合は『そのままで自然』とみなさず規則5を先に検討」を追記 |
| T2 同:11 | 規則3末尾「him/her(目的格)/them/me/us/it等…そのまま残してください(列挙外の置換は決定論検証で却下)」 | 「規則3で一般化してよい代名詞は列挙語のみ。目的格him/her/me/usは規則5(b)。them/it等はそのまま残す」へ差替え(**撤去対象: him/her/me/usを残せという旧文**) |
| T3 同:12の直後 | (規則5は存在しない。「この規則のいずれにも該当しない場合」は:14) | **規則5『参照語の不定化』本文を新設**(er112 `A1_RULE5`: (a)this/that→a/an+reason `generalize_reference_word`、(b)him/her/me/us→someone+reason `generalize_person_dependent_reference`、置換しない条件、規則3/4を控えめにしない旨)。:14を「規則(1〜5)」へ |
| T4 同:20 | key_phrase許容形の列挙 | 「規則5(参照語の不定化)に従った…1対1の置換」を追加 |
| T5 同:32 | `qa_traceable_contiguous_span` PASS条件(a)〜(d) | (e)規則5生成を追加 |
| T6 同:39 | `qa_person_reference_generalized` | 「規則3(目的格him/her/me/usは規則5(b))」へ |
| T7 同:41 | normalization_reason列挙 | `generalize_person_dependent_reference`に目的格を含める旨+`generalize_reference_word`(this/that→a/an、規則5(a))を追加 |
| K1 `er003_key_words_canonicalization.py`:113-136 | `NORMALIZATION_REASONS`(A/B/C共有)と`NORMALIZATION_REASONS_FULLTEXT = NORMALIZATION_REASONS[:-1] + (lemma, "other")`(:120) | **fulltext enumのみ**に`generalize_reference_word`を追加(`NORMALIZATION_REASONS`は不変=A/B/C schemaバイト同一を維持)。Trialの`_dev_schema`相当は不要化 |
| K2 同:431-469 | `_PERSON_DEPENDENT_TO_GENERIC`(閉集合)/`_is_valid_person_generalization` | **表は拡張しない**(OF-01: 表はgloss `_CONCRETE_PERSON_EN`[er003_key_words_gloss_alignment.py:167-168、import時固定]・`person_generalization_pairs`[:236-243]・er105:676が参照し、`her`所有格の`lose her job→lose someone job`を機械で防げなくなるため)。代わりに同ファイルへ**新関数`reference_pair_ok(kt,dt,idx,key_tokens,window)`**(er112 `_ref_pair_ok`相当: this/that→a/an+直後語条件[_DEM_FOLLOW_BLOCK/_UNCOUNTABLE/複数形]+a/an母音一致、him/me/us→someone/somebody、her→someone/somebodyは直後語が`_OBJ_HER_FOLLOW`のときのみ)を追加。a/an母音判定は**Productionの既存CMU資産(er108のcmudict 1.1.3、`cmu_gate`と同一辞書)を再利用**し、er112の`_cmu_dict`は移植しない |
| K3 同:502 | `_is_valid_fulltext_normalization`のreasonゲート`(lemma, generalize_person_dependent_reference)` | `generalize_reference_word`を追加。ゲート3箇所のうち変更が必要なのはここだけ(:512 `_qa_field_effective_verdict`と:571 `validate_canonicalization_item`は`generalize_person_dependent_reference`+table判定で偽になった場合、いずれも`_is_valid_fulltext_normalization`[:502]へ流れる)。Trial `DEV_ALLOWED_REASONS`と同一集合 |
| K4 同:650 | reasonのenum所属検査 | K1で自動追随(変更不要、test追加のみ) |
| K5 `er105_kp_fulltext_selector_01.py`:670-709 | `_token_pair_ok`(key側1対1置換の許可)/`is_valid_inflection_normalization`(連続窓走査) | `is_valid_inflection_normalization`の窓判定`all(_token_pair_ok(...))`を`all(_token_pair_ok(...) or kc.reference_pair_ok(kt,dt,i,k,window))`へ(`_token_pair_ok`自体は不変。er105は既にkcを遅延import済み[:676] → **isolation test許可リスト`ALLOWED`[er105_kp_fulltext_selector_01_test_01.py:294]の変更不要**) |
| G1 `er003_key_words_gloss_alignment.py`:236-243 | `person_generalization_pairs`は表由来のみ | him/her/me/us→someone/somebodyのペアも返す(Trial `d_pairs`相当)。`_CONCRETE_PERSON_EN`(:167)はme/him/usを既に含む=変更不要。`_person_mismatch_reason`が`someone`含むKPに「彼/私」混入glossを不一致にする(望ましい方向、OF-08) |
| X1 `er019_family_x_kp_explanation_01.py` | 変更なし(A-1単独ではPROMPT_SHA256不変)。A-3採用時のみ`_header_for`変更=B仕様PROMPT_SHA256更新 |
| 非変更 | `er105`選定Prompt 2逐語、`er003_key_phrase_source_gate_01.py`、`er003_v1_n3_01_scaffold_generate.py`(:485でtemplate選択、:499で`run_canonicalization_gate`)、A/B/C用template(`6e19a90557…`でtest固定) |

実装規模見込み: .py 3ファイル(kc/er105/gloss_alignment)+template 1+test 3〜4ファイル、差分は数十行+template約20行。

## 2. X/Z共通であることの確認(呼出経路、コード照合済み)
- Z: `er062_family_z_writer_01.py:1290-1294 run_kp_stage` → `run_kp_with_outer_retry_fulltext`(:1340) → `sc.run_key_phrase_selection(kp_backend=FULLTEXT_BACKEND_ID)` → `er003_v1_n3_01_scaffold_generate.py:485`(`kc.load_prompt_template(kc.FULLTEXT_PROMPT_TEMPLATE_PATH)`)→:499 `kc.run_canonicalization_gate`。
- X: `er019_family_x_audio_production_runner_01.py:385-392 run_theme_scaffold(kp_backend="fulltext_p2")` → `sc.run_key_phrases(..., kp_backend=...)` → 同じ`n3 scaffold`の:485/:499。
- 共通点は`kc`(template・enum・reasonゲート)とer105 validatorの1経路のみ。X/Z別の分岐コードは追加不要。A/B/C(`is_fulltext=False`)は旧template・`NORMALIZATION_REASONS`・旧validatorのまま(K1はfulltext専用enumにのみ追加するため無影響)。

## 3. retry / fallback / regeneration / resume との整合
- 外側retry(X/Z共通`run_kp_with_outer_retry`、`Z_KP_OUTER_RETRY_MAX=3`、er062:1305)・`OUTER_RETRY_EXHAUSTED`のfail-closed(旧5件経路へfallbackしない、er019:389-391)は**変更しない**。
- 方向性: 現行はLLMが`draw a line`/`pull someone under`を出すとvalidatorが却下しINVALID→外側retry消費(ROOT_CAUSE_01: 一般化不足は構造的)。K1〜K5で**受理側が増えるためINVALID/REVIEW_REQUIREDは減る方向**。増える側のリスクは(i)規則5がLLMに新しい変換を促し、置換条件外(`that advice`等)の誤置換がvalidatorで却下され外側retryを消費する可能性、(ii)OPEN-476型(`bound→bind`)は今回触らないので不変。Trial実績: 合成否定20/20保持、正常KP一致96.3%(baseline揺れ96.7%)。ただしTrialはreplay(選定・外側retry・音声側を通していない)のため、配線後runtime evidenceで`outer_retry_log.json`の試行数をbaselineと比較。
- resume / regeneration: KP成果物の再利用は`_kp_already_generated`(er019 `--scaffold-only kp`は1レベル1回STOP)・`--regenerate-stage kp_<lv>`(Z)・gloss側`UNEVALUATED_REASON`の既存判定に従う。**既存成果物(記事B等)の`draw that line`は配線後も自動では変わらない**(再生成は明示操作。ユーザー決定③「記事BのKP修正は採用配線後」で別委任)。
- 既存artifact互換: 新reasonは出力側enumの追加のみ。過去artifact(reasonが既存値)の読込・Gate(`validate_canonicalization_response`)に影響なし。

## 4. 音声・説明・ページ側(used_form経由)
- `used_form = key_phrase`(`er003_key_phrase_source_gate_01.py`の`"used_form": canon["key_phrase"]`)。KP英語の音声はused_formをTTS入力にする(`er019_family_x_audio_production_runner_01.py:1099-1106,1159-1170`、`expected_text=used_form`)。`draw a line`になれば音声・ページ・説明は新used_formで生成される(`one's`置換と同じ既存挙動)。
- 説明textのcache署名は`explanation_phrase(it)=used_form`基準(er019_family_x_kp_explanation_01.py:145-151、runner:1077-1081)=**used_formが変われば説明は自動再生成**、変わらないものはreuse(部分変更時は5件一括再生成の既存仕様)。
- KP3V(`pump one's fist`型保護)・CMU gate(M1選定時/M2 canonicalization後のused_form再確認)・5語上限は不変。`a`/`an`/`someone`はCMU登録語のため`cmu_post_canon`は通る見込み(配線後evidenceで`cmu_post_canon.ok`を確認)。
- 要確認(配線実施委任で実測): Store reuse_keyがused_form文字列基準であること、ページ表示がused_form/japanese_glossの既存表示のままで追加変更不要であること(目視)、`draw a line`の`a`(弱形)がKP3V照合で不安定にならないこと。

## 5. Trial依存0・撤去対象
- `er112_kp_gm_trial_01.py`はProductionからimport禁止。既存test `er112_kp_gm_trial_01_test_01.py::test_no_production_module_imports_er112`(:44)が機械的に保証。移植は`A1_RULE5`/`_A1_EDITS`/`_ref_pair_ok`/`d_pairs`の**ロジックの再実装**(本番CMU資産・本番enum定義へ接続)。DEV注入(`install_dev_patches`の`d_load`/`d_valid_ft`/`d_make_canon`/`kc.NORMALIZATION_REASONS_FULLTEXT`差替え/`d_pairs`)は配線後は不要。`prod_hashes`/`test_git_diff_has_no_production_file_change`(:176)はProduction sha不変が前提で**配線後は陳腐化するため、配線委任でskip化または基準更新**。
- 撤去する旧ルール(識別子): (1) template:11「him/her(目的格)/them/me/us/it等…そのまま残してください」のうちhim/her/me/us部分、(2) `er003_test_kp_fulltext_wiring_01.py`:261-267 `test_object_pronoun_kept_accepted_but_generalized_rejected`(`sentence someone to death`をINVALIDと期待する旧assert=JRE 委任_02 Z melos事象への対応の逆転。不整合な出力を期待値としてassertするtestは残さない→受理+`sentence him to death`も引き続き受理の2ケースへ書換)、(3) :287-288のtemplate内容assert(`"目的格"`・`"そのまま残してください"`)は、T2差替え文にも両語が残るため維持できる(配線時に実測)。配線後Grepで旧文`列挙外の置換は決定論検証で却下`が0件であることを確認。
- ルール矛盾の予防: 承認済みの規則4『形容詞化した分詞は原形にしない』・Std/Adv説明/gloss側は変更しない(規則5が規則3/4を控えめ・拡張しない旨をtemplate本文に明記済み=A1_RULE5末尾)。

## 6. golden / test 更新計画
| 区分 | ファイル | 内容 |
|---|---|---|
| 書換 | `er003_test_kp_fulltext_wiring_01.py`:261(上記(2))、reason受理test | `generalize_reference_word`受理、`generalize_person_dependent_reference`でhim/her/me/us受理 |
| 追加 | 同ファイル or 新規test | 付録A(validator真理値表)、reasonゲート、enum(fulltext schemaにのみ有り・A/B/C schemaバイト同一)、a/an CMU、template内容assert(規則5本文・置換しない条件・reason列挙)、gloss `person_generalization_pairs` |
| 追加 | 同上 | 隔離: A/B/C経路(`is_fulltext=False`)の旧template sha1(`6e19a905…`)・旧enum・旧validator挙動不変 |
| 更新 | `er105_kp_fulltext_selector_01_test_01.py`(:338-360) | `is_valid_inflection_normalization`の受理/拒否表に参照語ケース追加(`bound→bind`=OPEN-476は**そのまま拒否**として維持) |
| 変更なし | `er105 TestIsolation.ALLOWED`(:294) | K5はkc経由のため許可リスト変更不要 |
| 確認 | `er019_family_x_b3_min2_test_01.py`:34 `RULES_SHA256_BEFORE`ピン | Writer rules側のhash(`prod.rules_sha256()`)でKP templateとは無関係の見込み→配線時に全回帰で実測確認 |
| PROMPT_SHA256 | `er019_family_x_kp_explanation_01.py:142` | A-1単独では不変。A-3採用時は新hashへ更新し`er019_family_x_kp_structure_wiring_01_test_01.py`:71/77/155/251の期待値を同時更新(B仕様変更として記録) |
| 全回帰 | `run_project_regression.py` | 配線後に実施。基準=OPEN-456 F6(failed 0/errors 0、6,872 passed) |

## 7. runtime evidence 計画(配線後)
いずれも「KP段のみ再実行」。既存記事の成果物は上書きせず別out-dir(新run_id)で出力し、本番成果物(記事B等)は③の別委任まで保全。
- **X(`draw that line`型、this/that→a)**: 記事B `uk_train_speaker_playback`(`er019_output/uk_train_speaker_playback/`、`user_test/uk_train_speaker_playback_e2e_02`)の`b1b`/`a2`いずれかの本文でFamily X runnerの`--scaffold-only kp`(正式入口、出力は別`--out-dir`、support成果物のsha照合済みcopyを前置、er019:2392・:410-420)。期待: 正式経路で`draw a line`(reason `generalize_reference_word`)、`cmu_post_canon.ok`、外側retry試行数、gloss、used_form変化を採取。費用≤5円(OPEN-458 evidence実績: X KP段0.8〜1.5円+KP音声0.3円)。
- **Z(`him`型、him→someone)**: メロス(`sentenced him to death`、OPEN-458 evidenceでZ kp1に出現)または開いた窓のkp段をZ runner `--mode real --regenerate-stage kp_<lv>`相当(別run dir、er026:2076)で再実行。期待: `sentence someone to death`相当、OUTER_RETRY回数、glossに「彼」混入なし。費用≤5円(Z kp 1.08円+KP3clip 0.37円の実績)。
- LLM出力は確率的なため、自然発火しない場合は同一入力のKP段を最大2回(配線委任文で許可された範囲)まで再実行。それでも不発なら、不発の事実とTrial実績(6/6, 5/5)をそのまま報告(mock再生をruntime evidenceと呼ばない)。
- A-3採用時: 同じX evidenceでAdv説明のPrompt変更(新`PROMPT_SHA256`、説明が中心義になること)を併せて確認(追加API費用は説明1回分のみ)。
- 両Familyの証拠が揃うまで`PRODUCTION_WIRED`と判定しない(ユーザー指示§2)。
- 事前: `tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run>`のrc=0、`TTS_EXECUTION_MODE=STANDARD`、Production差分commit済みを確認。

## 8. 費用・時間見込み
- 実装・test: Sonnet 1委任(単一ファイル群、半日程度)+回帰。API 0。
- runtime evidence: X≤5円+Z≤5円=**≤10円**(案件見積300円以下=PM_GOVERNANCE 7-7によりAI自律可、日次1,000円内)。A-3同時の場合は説明1回分(数円)を加算。
- Production運用費: +0.05円/記事セット(Trial実測。70円目標への影響は軽微)。
- クリティカルパス: Opus条件Cレビュー → Production実装(本設計で準備済み) → test/全回帰 → runtime evidence(X/Z並列実行可: 別run dir・別state、rate limitは軽微) → SSOT。待機はA-3採否判断のみ。

## 付録A: test草案(Production test群を汚さないため本書内のみ、配線実施委任で実体化)
validator(`is_valid_inflection_normalization(key, display)` / `reference_pair_ok`): `er112_kp_gm_trial_01_test_01.py:ValidatorDev.CASES`(Trialで実測PASS済み)を真理値表として採用する。
- 肯定: `draw a line←draw that line` / `float an idea←float that idea` / `take a step←take that step` / `make a call←make that call` / `pull someone under←pulled him under` / `sentence someone to death←sentenced him to death` / `tell someone the truth←told her the truth` / `give someone a hand←gave him a hand` / `close around someone←close around me` / `lose someone's job←lose her job`(規則3) / `push prices up←pushed prices up`(既存不変)
- 否定: `draw the line←draw that line`(theは許可しない=ユーザー明示例優先) / `float a idea←float that idea`(a/an不一致) / `take an advice←take that advice` / `cost a much←cost that much` / `so a nobody noticed←so that nobody noticed` / `a time←that time` / `lose someone job←lose her job` / **`bind to the protein←bound to the protein`(OPEN-476=DEFERRED。拒否のまま維持)**
- 固定表現(置換しない): `that said` / `at that point` / `in that case` / `this time` / `like that` / `between you and me` / `all that` / `not that bad` / `that much` / `so that…` — templateの置換しない条件の文字列assert+LLM出力が置換した場合のvalidator却下を合成で確認。
- 句末・直後語・不可算: 句末that、直後が`much/many/is/was/said…`、複数形、不可算(`advice/information/news…`)。
- reason: fulltext schemaのenumに`generalize_reference_word`が有り、A/B/C schema(`CANONICALIZATION_JSON_SCHEMA`)に無い。`kc._is_valid_fulltext_normalization("draw a line","draw that line", reason)`が3 reasonで真、`none`/`other`で偽。`validate_canonicalization_response`でPASS(合成item)。
- a/an: `idea/hour/umbrella`→母音音、`line/university/one`→子音音(CMU、辞書外語は簡易規則)。
- gloss: `person_generalization_pairs({"display_phrase":"pulled him under","key_phrase":"pull someone under"})`が`[{from:him,to:someone}]`、`person_reference_mismatch("pull someone under","彼を引きずり込む")`が不一致理由を返す。
- 隔離: A/B/C旧template blob sha1=`6e19a90557b8512a0f3727cfa4547663df873ea4`不変、`import er112`をProductionが行わない。

## 付録B: 未確定・配線実施委任で実測する事項
1. Store reuse_key・ページ表示の実測(§4)。 2. `reference_pair_ok`でtheを許容しない(OPEN-474 ITERATION_LOG #1の確定)ことの再確認。 3. `us`→someoneはTrial未テスト(OPEN-474開示)。仕様に含まれる(ユーザー決定§2)ためvalidatorは通すが、runtime evidenceでの自然発火は期待せず合成testで担保。 4. `brace yourself for`型の取りこぼしはn=3で判定不能(Trial開示)=A-1の範囲外。
