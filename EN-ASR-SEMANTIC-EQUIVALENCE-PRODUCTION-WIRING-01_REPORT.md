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

Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01
