# EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01_REPORT

管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(Phase A+B)
日付: 2026-09-27
Status: 実装・テスト・runtime evidence取得完了。最終`PRODUCTION_WIRED`判定はFable Gate 3待ち。
性質: ユーザー正式採用済み(`APPROVED_FOR_PRODUCTION`、2026-09-27)のProduction配線。

---

## §0 前提

- Trial: `EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01_REPORT.md`(VALIDATED、POSITIVE 34/34・NEGATIVE false accept 0/34)。
- レビュー: `EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md` Part 2(Phase A/B承認範囲、配置方針)。
- 本Reportは上記2件で承認済みのロジックを実際のProduction経路へ配線した結果を記録する。Trial module(`er021_en_asr_semantic_equivalence_trial_01.py`)は無変更のまま併存(git diffゼロ、確認済み)。

## §1 実装(差分要点・配線箇所)

### 新規ファイル
- `er021_en_asr_semantic_equivalence_production_01.py`: Tier1数値パーサ(`tier1_numeric_equivalence()`、Trialから無変更移植)+Tier3純粋関数群(`determine_sub_reason()`/`locate_single_token_diff()`/`corroboration_supports()`/`is_benign_plural_pair()`)。**循環import回避のためval(`er006_preprod_hardening_01_validation`)を一切importしない設計**(tokenize済みtoken列・content_word_diffs等は呼び出し側が個別引数で渡す)。`FIVE_ROLES_APPLICABLE`定数、`append_telemetry_log()`。
- `er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`: unittest 23件。
- `er021_en_asr_semantic_equivalence_production_wiring_01_run.py`: runtime evidence取得用オーケストレーション。

### 配線箇所(関数・行)
1. **`er006_preprod_hardening_01_validation.py`**(ラッパー部のみ、`_classify_asr_match_core`は無変更):
   - `classify_asr_match()`(L1000〜)に`segment_id: str | None = None, role: str | None = None`をkeyword-only追加。`_resolve_semantic_equivalence_role()`(L982)がer020の`resolve_narrative_role()`を**遅延import**して同一SSOT判定を再利用(er020→val の既存import方向との循環を回避)。role適用時(5role: FULL_STORY/COMMENT/PREVIEW/TOPIC_INTRO/IN_ONE_LINE)のみ`_classify_asr_match_core()`呼び出し前にTier1 early-exit(`NUMERIC_EQUIVALENCE_MATCH`)。role適用でもTier1不一致の場合は既存(1)〜(4)手順を無変更で実行。role適用かつ最終的にshould_pass=Falseの場合のみ`sub_reason`をobservability telemetryへ記録(`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`)。
   - `VALID_CLASSIFICATIONS`へ`NUMERIC_EQUIVALENCE_MATCH`/`SECONDARY_ASR_CORROBORATED_MATCH`追加。`ClassificationResult`へ`semantic_equivalence_info: dict | None = None`(末尾default追加、既存位置引数呼び出しは無影響)。
   - `evaluate_attempt()`(L1142〜)へ`segment_id`引数追加、`classify_asr_match()`へ転送。
2. **`er006_secondary_asr_01.py`**:
   - `evaluate_attempt_with_cascade_detail()`(L451〜)/`evaluate_attempt_with_cascade()`へ`segment_id`引数追加。`val.evaluate_attempt()`呼び出し+5箇所の`val.classify_asr_match()`呼び出し(non_latin_secondary/secondary_forced/primary_2/secondary_1/secondary_2)全てへ`segment_id=segment_id`転送(Tier1が全cascade stepで一様に適用される)。
   - 既存Connected Speech Equivalence Layerブロックの直後・`cascade_eligible`判定より前に、Tier3 corroborationブロックを追加。`cls.classification == "ASR_VALIDATION_UNCERTAIN"`かつrole適用時のみ、`determine_sub_reason()`で`plural_only`/`entity_only`+1トークン差を検出した場合、Secondary ASR(既存`get_full_text_via_azure_stt_with_phrase_list()`)を1回追加実行してcorroborationを確認。支持されれば`SECONDARY_ASR_CORROBORATED_MATCH`(should_pass=True、`warning=True`)、支持されなければ既存判定を変えず`semantic_equivalence_info`のみ付与(false accept 0を安全側で維持)。
3. **呼び出し元(最小差分)**:
   - `er003_v1_sing01_voice01_generate.py::generate_charon_english()`: `review_lock.derive_segment_key(out_path)`でsegment_id導出(標準命名慣習外はNone=既存挙動)、`secondary_asr.evaluate_attempt_with_cascade()`へ転送。attempts_logへ`semantic_equivalence`項目追加。
   - `er003_v1_crosslevel_audio_02_common.py::_run_a2_minimal_fallback_attempt()`(A2 fallback経路): 同様にsegment_id導出・転送。
   - `er003_v1_n3_01_tts_generate.py::apply_a2_slowdown_postprocess()`: `name`(既にsegment_id)をそのまま`classify_asr_match(..., segment_id=name)`へ渡す1行変更。
   - `er011_human_review_lock_01.py::record_outcome()`: attempts_log中の`semantic_equivalence`を`attempt_history.jsonl`へパススルー(telemetry項目追加のみ)。

## §2 tests(23件、API課金なし)

`er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`:
- `RoleGatingTest`(7件): segment_id/role未指定時は無変更、5role全件でTier1発火、Heading/Key Phrase/未知segmentで非発火。
- `Tier1ProductionCorpusTest`(2件)+`TrialFullCorpusViaProductionWiringTest`(2件、Trial corpus全68件をProduction経由で再実行): NEGATIVE 34件false accept 0、POSITIVE(tier1_numeric 27+tier1_numeric_or_tier3 1+baseline_normalized_match 2=30件)無回帰。
- `ExistingFixtureRegressionViaProductionWiringTest`(2件): OPEN-123 fixture 57件(POSITIVE29+NEGATIVE28、role gate ON)無回帰・false accept 0。
- `Tier3CascadeIntegrationTest`(5件、Azure呼び出しmock): plural_only corroboration成功/不成立、role非適用時不発火、segment_id無し時不発火、数値TRUE_CONTENT_MISMATCHがTier3に飲み込まれないこと。
- `StringComparisonSafetyTest`(5件、recon_02 C-1個別確認): `is_entity_like_mismatch`/`is_homophone_candidate_mismatch`/`_step_alternate_pass`/`should_stop_retrying`が新規ラベルに対し安全(非該当)であること、Tier1発火時にcascade_eligible判定へ到達しないこと。

**既存regression**: `python -m unittest discover -s . -p "*_test_01.py"` = **Ran 1286 tests, failures=3, errors=1**(本タスク追加23件込み)。内訳確認済み、いずれも本タスクと無関係:
- `er019_family_x_pointless_01_test_01.FamilyAUnchangedTest`/`er020_tts_cooldown_local_rewrite_trial_01_test_01.ProductionModuleUnchangedTest`/`er020_tts_local_rewrite_natural_english_qa_trial_02_test_01.ProductionModuleUnchangedTest`(計3件): 他管理ID(Family A/Family X隔離)が「これらの共有Production module[`er003_v1_sing01_voice01_generate.py`/`er011_human_review_lock_01.py`/`er003_v1_n3_01_tts_generate.py`]に一切diffが無いこと」を保証するguard testであり、本タスクが正規に(ユーザー承認範囲で)これらへ最小差分を加えたこと自体を正しく検知している(design通りの反応、本タスクの欠陥ではない)。
- `er012_e_family_entertainment_two_level_runner_test_01.TtsModeCliTests.test_batch_mode_without_reason_errors_via_subprocess`(1件): `git status`で`er012_e_family_entertainment_two_level_runner_01.py`/`_test_01.py`が並行Agent(Family X JA Fact Check配線)により未commitで変更中であることを確認済み。本タスクはこれらのファイルを一切所有・変更していない。

## §3 runtime evidence(実TTS/ASR、実測¥2.72、TTS_EXECUTION_MODE=STANDARD)

### B1(`voice01.generate_charon_english()`、5 probe、専用out-dir`er021_output/.../probes/semantic_equivalence_probe/b1_dev/`)

| segment_id(role) | canonical | 実Primary ASR逐語 | 結果 |
|---|---|---|---|
| comment_1(COMMENT) | "Company profits reached four point seven billion dollars this quarter." | "Company profits reached $4.7 billion this quarter." | `NUMERIC_EQUIVALENCE_MATCH`(救済) |
| in_one_line(IN_ONE_LINE) | "The new policy officially took effect in twenty twenty-six." | "The new policy officially took effect in 2026." | `NUMERIC_EQUIVALENCE_MATCH`(救済) |
| topic_intro(TOPIC_INTRO) | "Growth came in at two point five percent this month." | "Growth came in at 2.5 percent this month." | `NUMERIC_EQUIVALENCE_MATCH`(救済) |
| preview(PREVIEW) | "The device now costs one hundred twenty five dollars." | "The device now costs $125." | `NUMERIC_EQUIVALENCE_MATCH`(救済) |
| point_one_heading(HEADING、非適用対照) | 同上comment_1と同一canonical | "Company profits reached $4.7 billion this quarter."(同一ASR) | `TRUE_CONTENT_MISMATCH`(role非適用のため正しく非救済、`status=STOPPED`) |

5probe中4/4(適用role)が実際にbaseline不一致を実測し本配線で救済、対照1件(非適用role、同一canonical/ASR)は正しく非救済——role gatingが実データで機能していることを直接確認した。

### A2(`crosslevel.generate_english_segment_with_fallback()`、1 probe)

canonical: "The company reported profits of three point one billion dollars last year."。標準経路の実Primary ASR: "The company reported profits of $3.1 billion last year."(`review_lock_state.json`に実記録済み)。標準経路自体(`er003_v1_repro01_main_generate.py`、所有ファイル外)は今回segment_id未配線のため`TRUE_CONTENT_MISMATCH`のまま`STOPPED`(**既知Gap、§5参照**)。実際に配線した1行(`apply_a2_slowdown_postprocess`の`classify_asr_match(..., segment_id=name)`)を、上記の実ASR逐語(追加API呼び出し無し、¥0)で再現: `segment_id="full_story_part1"`指定時`NUMERIC_EQUIVALENCE_MATCH`(救済)、未指定時`TRUE_CONTENT_MISMATCH`(既存挙動)。

**cost logger実測**: gemini(TTS)¥2.61 + openai_asr(Primary ASR)¥0.12 = **¥2.72**(予算目安¥15以内、Guardrail¥30以内)。詳細: `er021_output/en_asr_semantic_equivalence_production_wiring_01/runtime_evidence_results.json`、`audit/raw_usage_log.jsonl`。

## §4 Gate 3 checklist

| 項目 | 状態 | 根拠 |
|---|---|---|
| Production初回path | 実施済み | §3(B1 5probe、A2 1probe、実TTS/ASR) |
| retry/fallback/regeneration整合 | 確認済み | `StringComparisonSafetyTest`5件、cascade_eligible/should_stop_retrying非干渉を実証 |
| runtime evidence | 取得済み | §3(実測¥2.72、4/4適用role救済+対照1件非救済) |
| actual model・routing(ASR provider・Cascade発火) | 確認済み | `Tier3CascadeIntegrationTest`でAzure Cascade実配線経路(mock)を経由、B1/A2はOpenAI Primary ASR実呼び出し |
| regression・validator・integration test | 実施済み | 新規23件PASS、既存1286件中failures=3+errors=1は全て無関係(§2) |
| SSOT記載案 | 本Report §5に記載(編集は未実施、Fable/ユーザー判断待ち) | — |
| Git | 完了 | commit `014bb9e5`、push済み |
| Dangling Reference Check | 実施済み | `VALID_CLASSIFICATIONS`新規2ラベルの参照先(is_entity_like_mismatch等)を個別確認、Trial module無変更確認(`git diff`ゼロ) |

未充足項目: なし。STOP該当: なし(false accept・安全性問題は未検出)。

**既知Gap(SSOT記載案で明記予定)**: A2標準経路(`er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()`、所有ファイル外)自体にはsegment_idが未配線。A2の`apply_a2_slowdown_postprocess`後段(post-slowdown再判定)には配線済みだが、標準経路の初回判定はTier1の恩恵を受けない。将来の別管理IDでの追配線候補として記録する。

## §5 SSOT記載案(編集は未実施、Fable/ユーザー判断待ち)

### CURRENT_SPEC.md(既存「TTS Retry条件」節近傍への新規行案)

> | English ASR Semantic Equivalence Layer(OPEN-186、数値/通貨/%/年/時刻/分数/ローマ数字/略語のTier1値等価+規則的複数形・固有名詞のTier3 corroboration救済) | ユーザー正式承認(`APPROVED_FOR_PRODUCTION`、2026-09-27)。`er006_preprod_hardening_01_validation.py::classify_asr_match()`ラッパー冒頭に、role gating(5role: Full Story/Comment/Preview/Topic intro/In One Line、Key Phrase/Heading非適用、判定はer020`resolve_narrative_role()`を再利用)付きTier1 early-exit(`NUMERIC_EQUIVALENCE_MATCH`)を追加。Tier3(規則的複数形・固有名詞のみの1トークン差、Secondary ASR corroboration必須)は`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail()`のConnected Speech Equivalence Layer後段に配線(`SECONDARY_ASR_CORROBORATED_MATCH`、warning付き)。**適用箇所**: `voice01.generate_charon_english()`/`crosslevel_audio_02_common._run_a2_minimal_fallback_attempt()`(A2 fallback経路)/`er003_v1_n3_01_tts_generate.py::apply_a2_slowdown_postprocess()`。**既知Gap**: A2標準経路(`er003_v1_repro01_main_generate.py`)は今回未配線。Runtime evidence: B1実probe4/4救済+対照1件非救済、A2は実ASR逐語の再判定で救済確認(実測¥2.72)。詳細`EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01_REPORT.md` | `APPROVED_FOR_PRODUCTION`(実装済み、Gate 3進行中、`PRODUCTION_WIRED`は未宣言) | EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01(Trial・VALIDATED)、EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(Production配線) | 2026-09-27 |

### OPEN_ITEMS.md(OPEN-186行への追記案)

> **追記4(2026-09-27、`EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01`)**: Phase A+BをProduction配線完了(実装・test 23件・runtime evidence¥2.72取得済み)。既知Gap: A2標準経路(`er003_v1_repro01_main_generate.py`)未配線、将来別管理IDで追配線検討。Fable Gate 3判定待ち(`PRODUCTION_WIRED`確定は次段階)。

### DECISION_LOG.mdへの追記案(1エントリ)

> 2026-09-27(`EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01`): ユーザー承認済みPhase A+B(数値等価Tier1+複数形/固有名詞corroboration Tier3)をProduction配線。commit`014bb9e5`。詳細`EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01_REPORT.md`。

## §6 Git

commit `014bb9e5`(main反映済み)。所有ファイルのみ`git add`(`git add -A`不使用)。

主要ファイルraw URL:
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er021_en_asr_semantic_equivalence_production_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_preprod_hardening_01_validation.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er006_secondary_asr_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er021_en_asr_semantic_equivalence_production_wiring_01_run.py

---

## §7 修正1回目(Fable差し戻し、Gap解消)

### §7.0 差し戻し理由(再掲)
初回報告の既知Gap:「A2の標準生成経路(`er003_v1_repro01_main_generate.py`)には未配線。A2のfallback経路と生成後の再検証(post-slowdown)には配線済み」。数値表記差segmentがattempt 1/2で`TRUE_CONTENT_MISMATCH`→600秒cool-down→fallbackでTier1がPASS、という無駄な経路になっていた。

### §7.1 Gap特定(Grep結果)
`generate_a2_segments`/`generate_a2_segment_with_slowdown`(`er003_v1_n3_01_tts_generate.py`)の呼び出し連鎖を辿った結果、実際のGapは`er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()`自体に`segment_id`引数が存在しないこと、および`er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback()`の**標準経路呼び出し**(L100付近)がこれを渡していなかったことだった(同関数のfallback経路`_run_a2_minimal_fallback_attempt()`は初回報告時点で既に配線済み、これは変更していない)。

### §7.2 配線一覧表(全経路、Grep網羅)

**A2側**

| ファイル | 関数 | 行 | 状態 | 備考 |
|---|---|---|---|---|
| `er003_v1_repro01_main_generate.py` | `generate_narration_snippet_verified_strict()` | L194(定義)/L280-287(`evaluate_attempt_with_cascade`呼び出し) | **修正1回目で配線** | `segment_id: str \| None = None`をkeyword-only追加、既定Noneのため他の全呼び出し元(Family A等)は無変更 |
| `er003_v1_crosslevel_audio_02_common.py` | `generate_english_segment_with_fallback()`標準経路 | L109-115 | **修正1回目で配線** | `_run_a2_minimal_fallback_attempt()`と同一の導出方法(`review_lock.derive_segment_key`)でsegment_id導出・転送。A2の`full_story_part1/2・point_one/two・topic_intro・in_one_line`が標準経路attempt1/2からTier1の恩恵を受ける |
| `er003_v1_crosslevel_audio_02_common.py` | `_run_a2_minimal_fallback_attempt()`(fallback経路) | L246-258 | 初回報告時点で配線済み(無変更) | — |
| `er003_v1_n3_01_tts_generate.py` | `apply_a2_slowdown_postprocess()`(post-slowdown再検証) | L141 | 初回報告時点で配線済み(無変更) | — |
| `er008_n8_a2_resume_01.py` | `_verify_existing()` | L41 | 未配線(所有ファイル外) | legacy一回限りのincident resume script。retry/cooldownを伴わない単発reuse判定のみ(実際の(再)生成時は`c.generate_english_segment_with_fallback`/`tg.generate_a2_segment_with_slowdown`経由で本修正の恩恵を受ける)。対象外と判断、報告のみ |
| `verify_cascade_production_on.py`/`verify_sweeny_cascade.py` | `classify_asr_match()`直接呼び出し | — | 未配線 | 生成pipelineの一部ではない独立診断script、対象外 |

**B1側(Grep全件確認、要件2)**

| ファイル | 関数 | 行 | 状態 | 備考 |
|---|---|---|---|---|
| `er003_v1_sing01_voice01_generate.py` | `generate_charon_english()` | L157-167 | 配線済み(初回報告時点、無変更) | preview/comment_1-4/topic_intro/in_one_lineのB1英語roleが対象 |
| `er003_v1_sing01_news_tail_fix.py` | `generate_news_narration_wide_margin()` | L129-132 | **未配線(B1側の同型Gap、新規発見)** | full_story_part1/2・point_one/two・in_one_line(B1本文5role、`er003_v1_n3_01_tts_generate.py`のL772経由)の初回attempt経路。所有ファイル外のため本タスクでは修正せず、Fable/ユーザーへ報告のみ(§7.5参照) |
| `er008_n8_b1_resume_01.py` | `_verify_existing()` | L47 | 未配線 | A2 resumeと同型のlegacy単発reuse判定のみ、対象外 |
| `er007_ja_secondary_asr_01.py` | `evaluate_attempt_ja_with_cascade()` | — | 対象外 | 日本語専用path、Tier1は英語専用設計のため非該当 |

### §7.3 tests(3件追加、既存23件と合わせて26件、API課金なし)
`er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`へ`A2StandardPathProductionWiringFixTest`を追加:
- `test_full_story_part1_numeric_diff_rescued_at_attempt1_no_cooldown_no_fallback`: `crosslevel.generate_english_segment_with_fallback()`を実際に呼び出し(TTS/ASRのみmock、Tier1判定は実ロジック)、数値差segment(segment_id="full_story_part1")がattempt1(標準経路1回目)で`NUMERIC_EQUIVALENCE_MATCH`となり、TTS呼び出しが1回のみ・`cooldown_events`キー不在(fallback未到達)であることを固定。
- `test_point_one_heading_non_applicable_role_regression_unaffected`: 同じ数値差ペアでもrole非適用(HEADING)のsegment_idでは既存通り2回とも不合格・TTS 2回消費のまま(role gatingの回帰確認)。
- `test_no_segment_id_default_unchanged_family_a_regression`: segment_id未指定(Family A等)は生成関数レベルでも無変更。

**regression実行結果**:
1. `er021_..._test_01.py`単体: 26件PASS。
2. 全体(`python -m unittest discover -s . -p "*_test_01.py"`)1回目: **Ran 1295 tests, errors=6**。原因調査の結果、全6件が本修正(`generate_narration_snippet_verified_strict`内部の`evaluate_attempt_with_cascade`呼び出しへ`segment_id`引数を追加したこと)によって、当該関数を固定シグネチャのfakeで完全置換していた既存test(`er007_reading_validation_wiring_test_01.py`/`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`(2件)/`er011_open121_repetition_qa_production_wiring_01_test_01.py`(2件)/`er012_b_family_voices_a2_new_topic_production_01_test_01.py`)のfake関数が`segment_id`キーワードを受け付けず`TypeError`になったもの(動作の後方互換性は保たれているが、fakeの固定シグネチャが前方互換ではなかった)。追加でGrep探索した結果、discoverパターン(`*_test_01.py`)に該当しない`er011_tts_attempt_audio_retention_wiring_01_test.py`(3 test methods)でも同型の破壊を確認した。
   - **修正**: 上記のうち**所有ファイル外だが本修正が直接原因のfake破壊**である4ファイル(`er007_reading_validation_wiring_test_01.py`/`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`/`er011_open121_repetition_qa_production_wiring_01_test_01.py`/`er011_tts_attempt_audio_retention_wiring_01_test.py`)のfake関数へ`segment_id=None`パラメータを追加(挙動確認ロジックは無変更、シグネチャの後方互換性回復のみ)。5ファイル合計122件再実行→**PASS**。
   - **`er012_b_family_voices_a2_new_topic_production_01_test_01.py`は同一原因(fake_standard()がsegment_id未対応)だが、本タスクの所有範囲外(`er012`除外指示)のため意図的に未修正のまま**。§7.5でFable/ユーザーへ報告する。
3. 全体2回目(上記4ファイル修正後): **Ran 1302 tests, errors=2**。
   - `er012_b_family_voices_a2_new_topic_production_01_test_01.NarratorHeadingRetryPolicyAlignmentTests.test_standard_stop_retrying_does_not_skip_fallback_budget`: 上記の通り、意図的に未修正(§7.5)。
   - `er015_standard_a2_6000_generation_first_trial_01_test_01`(loader ImportError): `git status`で確認した結果、`er003_v1_n3_01_standard_a2_generate.py`が並行Agent(JA Fact Check配線)により未commitで変更中であり、そのモジュールがimport時に`STANDARD_A2_PROMPT_V5`の内容不一致で`RuntimeError`を自己送出していることが原因。本タスクはこのファイルを一切所有・変更していない。
   - 初回報告(§2)で記録した既存3件のguard test失敗(`er019_family_x_pointless_01_test_01`/`er020_tts_cooldown_local_rewrite_trial_01_test_01`/`er020_tts_local_rewrite_natural_english_qa_trial_02_test_01`)は、本regression実行では**解消済み**(エラー一覧に出現しない)。

### §7.4 runtime evidence(実TTS/ASR、実測¥0.97、TTS_EXECUTION_MODE=STANDARD)
専用out-dir`er021_output/en_asr_semantic_equivalence_production_wiring_01/probes_fix1/`(既存記事artifact無変更)。`crosslevel.generate_english_segment_with_fallback(..., max_attempts=1, standard_attempts=1)`で**fallback予算を意図的に0にし**、標準経路attempt1のみで合否が決まる状態にした上で実際に呼び出した(判定層の個別呼び出しではなく正式generate関数そのもの)。

| segment_id(role) | canonical | 実Primary ASR逐語 | 結果 |
|---|---|---|---|
| full_story_part1(FULL_STORY) | "The company reported profits of four point seven billion dollars last year." | "The company reported profits of $4.7 billion last year." | `NUMERIC_EQUIVALENCE_MATCH`、attempts_log_len=1、fallback_used=False、cooldown_events不在 |
| topic_intro(TOPIC_INTRO) | "The forecast now covers the period through twenty twenty-six." | "The forecast now covers the period through 2026." | `NUMERIC_EQUIVALENCE_MATCH`、attempts_log_len=1、fallback_used=False、cooldown_events不在 |

fallback予算0(標準経路attempt1回のみ)という最も厳しい条件下でも両方ともPASSしたことは、Gapが実際に解消され、標準経路attempt1の時点でTier1 early-exitが発火していることの直接証拠である(修正前であれば、この設定は必ず`STOPPED`になっていたはずである)。

**cost logger実測**: gemini(TTS)¥0.93 + openai_asr(Primary ASR)¥0.04 = **¥0.97**(目安予算¥5以内、Guardrail¥15以内)。詳細: `er021_output/en_asr_semantic_equivalence_production_wiring_01/runtime_evidence_results_fix1.json`、`audit/raw_usage_log_fix1.jsonl`。オーケストレーション: `er021_en_asr_semantic_equivalence_production_wiring_01_fix1_run.py`。

### §7.5 Fable/ユーザーへの報告事項(未実装のまま、判断待ち)
1. **`er012_b_family_voices_a2_new_topic_production_01_test_01.py`のtest破壊**: 本修正(`generate_narration_snippet_verified_strict`→`evaluate_attempt_with_cascade`へのsegment_id転送)により、同ファイルの`NarratorHeadingRetryPolicyAlignmentTests.test_standard_stop_retrying_does_not_skip_fallback_budget`が`fake_standard()`の固定シグネチャ非対応で`TypeError`になる(本物の生成ロジックの回帰ではなく、mock関数のシグネチャ更新のみで解決する)。委任文の除外指示(`er012`には触れない)を厳守し、本タスクでは**意図的に未修正**とした。該当箇所(`crosslevel.generate_narration_snippet_verified_strict`をmockする`fake_standard(...)`)へ`segment_id=None`引数を1つ追加するだけの機械的修正で解消できる。修正の可否をFable/ユーザーの判断に委ねる。
2. **B1側の同型Gap(`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin()`)**: A2で解消したものと同じ構造のGapがB1側にも存在する(§7.2参照)。所有ファイル外のため本タスクでは修正していない。将来の別管理ID候補として報告する。

### §7.6 Gate 3再照合
| 項目 | 状態 | 根拠 |
|---|---|---|
| 既知Gap(A2標準経路未配線) | **解消** | §7.1・§7.4(fallback予算0でも実際にattempt1でPASS) |
| B1側同型Gapの有無確認(要件2) | 確認済み、1件検出・報告のみ(所有範囲外) | §7.2 |
| retry/fallback/regeneration整合 | 確認済み | §7.3(role非適用segmentの既存挙動維持を回帰test化) |
| runtime evidence | 取得済み | §7.4(実測¥0.97) |
| regression | 実施済み、残差2件はいずれも本タスク外要因(git statusで確認) | §7.3 |
| Git | 所有ファイルのみpath指定add予定(次節) | §7.7 |

### §7.7 Git(修正1回目)
所有ファイルのみ`git add`(`git add -A`不使用)。対象: `er003_v1_repro01_main_generate.py`/`er003_v1_crosslevel_audio_02_common.py`/`er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`/`er021_en_asr_semantic_equivalence_production_wiring_01_fix1_run.py`/`EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01_REPORT.md`/evidence out-dir新規ファイル、および本修正で直接破壊された既存test 4ファイル(`er007_reading_validation_wiring_test_01.py`/`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py`/`er011_open121_repetition_qa_production_wiring_01_test_01.py`/`er011_tts_attempt_audio_retention_wiring_01_test.py`)。

---

## §8 修正2回目(Fable差し戻し、B1側Gap最終解消)

### §8.0 差し戻し理由(再掲)
Fable判断: (1)`er012_b_family_voices_a2_new_topic_production_01_test_01.py`のfake関数へ
`segment_id=None`を追加して修正する。(2)B1の`er003_v1_sing01_news_tail_fix.py::
generate_news_narration_wide_margin`(Full Story part1/2/3・In One Line=Family X本文の主要経路)の
同型Gap(§7.2・§7.5で報告済み、所有範囲外のため未実装のまま報告のみだった)を、本管理ID内で
今すぐ解消する(B1 Full Storyは「Production初回path」の中核であり、未配線のまま`PRODUCTION_WIRED`
にできない)。

### §8.1 実装

1. **`er012_b_family_voices_a2_new_topic_production_01_test_01.py`**: `fake_standard()`の
   固定シグネチャへ`segment_id=None`をキーワード引数として追加(挙動確認ロジックは無変更)。
   `test_standard_stop_retrying_does_not_skip_fallback_budget`が単体で再びPASSすることを確認済み
   (15件中1件のpiece test、`.venv/Scripts/python.exe -m unittest
   er012_b_family_voices_a2_new_topic_production_01_test_01 -v` = Ran 15 tests, OK)。

2. **`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin`**: `routing.transcribe()`
   呼び出し直後・`secondary_asr.evaluate_attempt_with_cascade()`呼び出し直前に、A2修正1回目
   (`er003_v1_crosslevel_audio_02_common.py`)と同一の導出方法(`review_lock._has_valid_narration_
   layout(out_path)`が真の場合のみ`review_lock.derive_segment_key(out_path)`でsegment_idを導出、
   従わない場合はNoneのまま=既存挙動)を追加し、`evaluate_attempt_with_cascade(..., segment_id=
   segment_id)`として転送する1箇所の変更。

   この関数は標準attempt・TTS技術的fallback(minimal_instruction、trimmed is Noneの場合の
   `repro01.generate_english_component_minimal_instruction`)・Local Rewrite回復再帰呼び出し
   (`_local_rewrite_recovery_for_news_narration`が`generate_news_narration_wide_margin.__wrapped__`を
   再帰呼び出し)の全経路が、単一のforループ内にある単一の`evaluate_attempt_with_cascade`呼び出しを
   共有する設計(A2の`_run_a2_minimal_fallback_attempt`のような別関数化されたfallback経路は
   存在しない)。そのため、この1箇所の修正だけでB1本文の全attempt経路(初回・fallback・
   Local Rewrite再帰)がTier1 early-exit/Phase B corroborationの恩恵を受ける。

### §8.2 配線一覧表(最終、全経路)

**B1側**

| ファイル | 関数 | 状態 | 備考 |
|---|---|---|---|
| `er003_v1_sing01_voice01_generate.py` | `generate_charon_english()` | 配線済み(初回報告時点、無変更) | preview/comment_1-4/topic_intro/in_one_lineのB1英語roleが対象 |
| `er003_v1_sing01_news_tail_fix.py` | `generate_news_narration_wide_margin()`(standard attempt・TTS技術的fallback・Local Rewrite回復再帰の全経路共通) | **修正2回目で配線** | full_story_part1/2/3・point_one/two・in_one_line(B1本文5role)の初回attemptからTier1が有効 |
| `er008_n8_b1_resume_01.py` | `_verify_existing()` | 未配線(所有ファイル外) | legacy一回限りのincident resume script。retry/cooldownを伴わない単発reuse判定のみ、対象外(A2の`er008_n8_a2_resume_01.py`と同型・同じ判断) |
| `er007_ja_secondary_asr_01.py` | `evaluate_attempt_ja_with_cascade()` | 対象外 | 日本語専用path、Tier1は英語専用設計のため非該当 |

**A2側(修正1回目で既に全解消、再掲)**

| ファイル | 関数 | 状態 |
|---|---|---|
| `er003_v1_repro01_main_generate.py` | `generate_narration_snippet_verified_strict()` | 配線済み(修正1回目) |
| `er003_v1_crosslevel_audio_02_common.py` | `generate_english_segment_with_fallback()`標準経路 | 配線済み(修正1回目) |
| `er003_v1_crosslevel_audio_02_common.py` | `_run_a2_minimal_fallback_attempt()`(fallback経路) | 配線済み(初回報告時点) |
| `er003_v1_n3_01_tts_generate.py` | `apply_a2_slowdown_postprocess()`(post-slowdown再検証) | 配線済み(初回報告時点) |
| `er008_n8_a2_resume_01.py` | `_verify_existing()` | 未配線(所有ファイル外、legacy単発reuse判定のみ、対象外) |

**結論**: B1/A2ともに、Production初回生成path(標準attempt・retry・fallback・再検証・Local Rewrite回復)は
**全経路が配線済み**。未配線として残るのは、いずれも「実際の(再)生成コールパスの一部ではない
legacy単発resume script」(`er008_n8_a2_resume_01.py`/`er008_n8_b1_resume_01.py`、実際の(再)生成時は
配線済みの正式generate関数を経由する)のみであり、これらはretry/cooldownを伴わない性質から
対象外と判断する(修正1回目と同一の判断基準)。

### §8.3 tests

`er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`へ`NewsTailFixB1WiringFixTest`
(3件)を追加(既存29件と合わせて32件、API課金なし)。TTSパイプライン
(`common._call_tts_with_retry`/`p3u.trim_english_keyword_silence`/`safety.detect_duration_anomaly`)と
Primary ASR(`routing.transcribe`)のみモックし、Tier1判定(`secondary_asr.evaluate_attempt_with_cascade`/
`val.classify_asr_match`)は実ロジックをそのまま通す設計(既存の
`er011_open121_repetition_qa_production_wiring_01_test_01.GenerateNewsNarrationWideMarginScopeTests`と
同一のモック方式)。

- `test_full_story_part1_numeric_diff_rescued_at_attempt1_no_cooldown`: 数値差segment
  (segment_id="full_story_part1"、標準命名慣習パス)がattempt1で`NUMERIC_EQUIVALENCE_MATCH`、
  `attempts_log`長1、`cooldown_events == []`(cool-down不発火)、TTS呼び出し1回のみであることを固定。
- `test_point_one_heading_non_applicable_role_regression_unaffected`: 同じ数値差ペアでも
  非適用role(point_one_heading)では既存通り不合格のまま(role gatingの回帰確認)。
- `test_no_valid_narration_layout_segment_id_none_unchanged`: 標準命名慣習に従わないout_path
  (単体テストのダミーパス等)ではsegment_id=Noneのまま、既存挙動と完全に同じであることを確認。

`er012_b_family_voices_a2_new_topic_production_01_test_01.py`修正(fake_standard()へ
`segment_id=None`追加)により、同ファイル15件がPASS(修正前は
`test_standard_stop_retrying_does_not_skip_fallback_budget`が`TypeError`)。

**regression実行結果**:
1. `er021_..._test_01.py`単体: 32件PASS(追加3件込み)。
2. `er012_b_family_voices_a2_new_topic_production_01_test_01.py`単体: 15件PASS。
3. 全体(`python -m unittest discover -s . -p "*_test_01.py"`): **Ran 1314 tests, failures=1,
   errors=1**。内訳確認済み、いずれも本タスクと無関係:
   - `er015_standard_a2_6000_generation_first_trial_01_test_01`(loader ImportError): `git status`で
     確認した結果、`er003_v1_n3_01_standard_a2_generate.py`/`er003_v1_n3_01_advanced_adaptation_
     generate.py`が並行Agent(JA Fact Check配線)により未commitで変更中であることが原因。本タスクは
     これらのファイルを一切所有・変更していない。
   - `er019_family_x_pointless_01_test_01.FamilyAUnchangedTest.test_family_a_files_have_no_working_
     tree_diff`(1件): このguard testは「共有Production module(`er003_v1_sing01_news_tail_fix.py`含む)
     に一切diffが無いこと」を保証する設計であり、本タスクがFableの明示的指示(§8.0)に基づき
     `er003_v1_sing01_news_tail_fix.py`へ正規の最小差分を加えたこと自体を正しく検知している(design
     通りの反応、本タスクの欠陥ではない。初回報告§2で同種の反応が記録され、commit後に解消したのと
     同じパターン。本修正2回目のcommit後も同様に解消する見込み)。

### §8.4 runtime evidence(実TTS/ASR、実測¥0.52、TTS_EXECUTION_MODE=STANDARD)

専用out-dir`er021_output/en_asr_semantic_equivalence_production_wiring_01/probes_fix2/`
(既存記事artifact無変更)。`news_tail_fix.generate_news_narration_wide_margin(canonical, out_path,
max_attempts=1)`を、正式generate関数そのもの経由で実際に呼び出した(判定層の個別呼び出しではない)。
オーケストレーション: `er021_en_asr_semantic_equivalence_production_wiring_01_fix2_run.py`。

| segment_id(role) | canonical | 実Primary ASR逐語 | 結果 |
|---|---|---|---|
| full_story_part1(FULL_STORY) | "The company reported profits of four point seven billion dollars last year." | "The company reported profits of $4.7 billion last year." | `NUMERIC_EQUIVALENCE_MATCH`、status=OK、attempts_log_len=1、cooldown_events=[]（不発火） |

max_attempts=1(唯一の試行)という最も厳しい条件下でPASSしたことは、修正前であれば必ず
`STOPPED`になっていたはずの経路が、attempt1の時点でTier1 early-exitにより救済されていることの
直接証拠である。

telemetry.jsonl(observability、role適用かつTier1不一致の場合のみ追記される既存設計)の行数は、
本probe実行前後で512→512と不変だった。これは設計どおりの挙動である(Tier1でPASSした場合は
observability対象外、既存Phase A実装時からの仕様)。telemetry機構自体が生きていることは、本タスクの
regression実行(§8.3、role適用NEGATIVE corpusを実ロジック経由で通す既存test群)で434→512行へ
実際に増加したことにより別途確認済み(実行前後の差分は本タスクの新規テスト実行によるものであり、
既存の観測性機構が正しく動作し続けていることを示す)。

**cost logger実測**: gemini(TTS)¥0.49 + openai_asr(Primary ASR)¥0.03 = **¥0.52**
(目安予算¥3以内、Guardrail¥10以内)。詳細: `er021_output/en_asr_semantic_equivalence_production_
wiring_01/runtime_evidence_results_fix2.json`、`audit/raw_usage_log_fix2.jsonl`。

### §8.5 Gate 3最終照合表

| 項目 | 状態 | 根拠 |
|---|---|---|
| B1側同型Gap(`generate_news_narration_wide_margin`) | **解消** | §8.1・§8.4(max_attempts=1でも実際にattempt1でPASS) |
| A2標準経路Gap(修正1回目で解消済み) | 解消済み | §7 |
| `er012`fake関数破壊 | **解消** | §8.1・§8.3(15件PASS) |
| B1/A2全経路配線一覧(要件2) | 完成、未配線はlegacy単発resume scriptのみ(対象外理由明記) | §8.2 |
| retry/fallback/regeneration整合 | 確認済み | §8.3(role非適用・segment_id未指定の既存挙動維持を回帰test化) |
| runtime evidence | 取得済み | §8.4(実測¥0.52) |
| regression | 実施済み、残差2件はいずれも本タスク外要因(git statusで確認・確定) | §8.3 |
| Git | 所有ファイルのみpath指定add(次節) | §8.6 |

未充足項目: なし。STOP該当: なし(false accept・安全性問題は未検出)。

### §8.6 SSOT記載案(編集は未実施、Fable/ユーザー判断待ち、最終版)

#### CURRENT_SPEC.md(§5の既存案を以下へ差し替え)

> | English ASR Semantic Equivalence Layer(OPEN-186、数値/通貨/%/年/時刻/分数/ローマ数字/略語の
> Tier1値等価+規則的複数形・固有名詞のTier3 corroboration救済) | ユーザー正式承認
> (`APPROVED_FOR_PRODUCTION`、2026-09-27)。`er006_preprod_hardening_01_validation.py::
> classify_asr_match()`ラッパー冒頭に、role gating(5role: Full Story/Comment/Preview/Topic
> intro/In One Line、Key Phrase/Heading非適用、判定はer020`resolve_narrative_role()`を再利用)付き
> Tier1 early-exit(`NUMERIC_EQUIVALENCE_MATCH`)を追加。Tier3(規則的複数形・固有名詞のみの1トークン差、
> Secondary ASR corroboration必須)は`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_
> detail()`のConnected Speech Equivalence Layer後段に配線(`SECONDARY_ASR_CORROBORATED_MATCH`、
> warning付き)。**適用箇所(B1/A2の英語本文segment生成、初回attempt・fallback・post-slowdown再検証・
> Local Rewrite回復の全経路)**: `voice01.generate_charon_english()`/`news_tail_fix.generate_news_
> narration_wide_margin()`(B1 Full Story part1/2/3・Point・In One Line)/`crosslevel_audio_02_common.
> generate_english_segment_with_fallback()`(A2標準経路+`_run_a2_minimal_fallback_attempt()`fallback
> 経路)/`repro01.generate_narration_snippet_verified_strict()`/`er003_v1_n3_01_tts_generate.py::
> apply_a2_slowdown_postprocess()`。既知Gapなし(legacy単発resume script[`er008_n8_a2_resume_01.py`/
> `er008_n8_b1_resume_01.py`]のみ対象外、実際の(再)生成は上記配線済み経路を経由)。Runtime evidence:
> B1実probe5/5救済(初回4件+Full Story 1件)+対照1件非救済、A2実probe2件救済(fallback予算0でも
> attempt1でPASS)、実測合計¥4.21(初回¥2.72+修正1回目¥0.97+修正2回目¥0.52、詳細は各節)。
> 詳細`EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01_REPORT.md` | `APPROVED_FOR_PRODUCTION`
> (実装・全経路配線完了、`PRODUCTION_WIRED`はFable Gate 3最終判定待ち) |
> EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01(Trial・VALIDATED)、EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-
> WIRING-01(Production配線) | 2026-09-27 |

#### OPEN_ITEMS.md(OPEN-186行への追記案、最終)

> **追記5(2026-09-27、`EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01`修正2回目)**: B1側同型Gap
> (`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin`)を解消し、B1/A2の
> Production初回生成path(標準attempt・fallback・post-slowdown再検証・Local Rewrite回復)が全経路
> 配線済みになった。残る未配線はlegacy単発resume script(実際の(再)生成コールパス外)のみ。
> Fable Gate 3最終判定待ち(`PRODUCTION_WIRED`確定は次段階)。

#### DECISION_LOG.mdへの追記案(最終、1エントリ)

> 2026-09-27(`EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01`修正2回目): Fable差し戻しに基づき
> B1側同型Gap(`news_tail_fix.generate_news_narration_wide_margin`)を解消。B1/A2ともにProduction
> 初回生成path全経路が配線済みとなった。commit(本コミットhash、§8.7参照)。詳細
> `EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01_REPORT.md` §8。

### §8.7 Git(修正2回目)
所有ファイルのみ`git add`(`git add -A`不使用)。対象: `er003_v1_sing01_news_tail_fix.py`/
`er012_b_family_voices_a2_new_topic_production_01_test_01.py`/`er021_en_asr_semantic_equivalence_
production_wiring_01_test_01.py`/`er021_en_asr_semantic_equivalence_production_wiring_01_fix2_run.py`/
`EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01_REPORT.md`/evidence out-dir新規・更新ファイル
(`er021_output/en_asr_semantic_equivalence_production_wiring_01/`配下)。

---

Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01
