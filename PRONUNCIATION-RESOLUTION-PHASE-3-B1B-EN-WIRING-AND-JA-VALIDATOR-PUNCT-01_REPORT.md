# PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01 REPORT

作成: Sonnet実行層。委任文全文は
`docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_01.md`
に保存済み。**¥0**(コード・test・fixtureのみ、TTS/ASR/LLM実行なし、Human
Review Lock解除なし、共有ストア書込みなし)。Fable Gate 3判定は本REPORTでは
自称しない(**Fable Gate 3判定待ち**のまま記載する)。本commit後にOpus L2
レビュー(共有ASR/TTS層変更のため必須)を予定。

## §1 既存資産照合(分類A: 既存承認仕様の実装穴、新仕様ではない)

`CURRENT_SPEC.md`「固有名詞読み解決(JA/EN共通)」節(2026-09-27新設、
`Status: APPROVED_FOR_PRODUCTION`)は既に以下を明記済み:

> **Production配線範囲**: EN側resolver(`resolve_and_augment_en_style_
> prefix`)が実際に配線されているのは`generate_narration_snippet_verified_
> strict`(A2英語標準+fallback、Key Phrase Componentを含む全EN経路)経由の
> みである。`generate_english_component_minimal_instruction`(B1
> scaffold/crosslevel/news_tail_fix等が呼ぶ)・`generate_charon_english`
> (B1B、`voice01`経由)には未配線(`OPEN_ITEMS.md`参照)。

`OPEN_ITEMS.md` OPEN-197(`generate_charon_english`未配線)・OPEN-198
(`generate_english_component_minimal_instruction`未配線)・OPEN-199(JA ASR
Validator句読点正規化ギャップ、Muse実データ差分文字全件)はいずれも上記
承認済み仕様の**実装穴**として2026-09-27に起票されたもの。本タスクは
これら3件を実装する(新規仕様の追加ではない)。

## §2 実施内容

### 1. OPEN-197是正: `generate_charon_english`へのEN resolver配線

`er003_v1_sing01_voice01_generate.py`の`generate_charon_english()`に
opt-in引数`enable_pronunciation_resolver: bool = False`を追加。Trueの
場合のみ、A2英語標準経路(`generate_narration_snippet_verified_strict`)
と**同一関数**(`pron_resolver_core.resolve_and_augment_en_style_prefix`)
を同じタイミング(retryループ開始前、1回のみ)・同じconfidence gate
(`augment_style_prefix_with_pronunciation`のmin_confidence="medium"、
core内部固定)で呼び、style_prefixへ発音ヒントを注入する。hintが1件も
無い場合はstyle_prefix_overrideを一切変更しない(既存呼び出し元・既存
promptへの影響ゼロ)。telemetry`en_pronunciation_resolver_info`をOK/
ASR_VALIDATION_UNCERTAIN/STOPPED全ての戻り値へ追加(A2側と同じ形状)。

### 2. OPEN-198是正: `generate_english_component_minimal_instruction`への配線

`er003_v1_repro01_main_generate.py`の同関数へ同じopt-in引数・同じhook
ロジックを追加(MINIMAL_INSTRUCTION_PREFIXを対象にaugmentする)。この
関数はFamily X runnerから直接呼ばれることは無く、`news_tail_fix.
generate_news_narration_wide_margin()`の**技術的fallback**(発話区間検出
失敗時のみ発火する内部fallback、ASR内容不一致による標準retryとは別物)
経由でのみ到達可能なため、`generate_news_narration_wide_margin()`にも
同名opt-in引数を追加し、この内部呼び出しへそのまま転送するだけの配線を
行った(`generate_news_narration_wide_margin`自身のENGLISH_STYLE_PREFIX
標準分岐は無変更)。

**重要な限界(正直に報告)**: 実際に観測された小規模記事(small_bag)B1B
`full_story_part2`/`full_story_part3`のASR_VALIDATION_UNCERTAIN(ブランド名
未解決)は、`generate_news_narration_wide_margin`の**標準ENGLISH_STYLE_
PREFIX分岐**(技術的fallbackではない)で起きている。本タスクは委任文が
明示した2関数(`generate_charon_english`/`generate_english_component_
minimal_instruction`)のみを対象範囲としたため、この標準分岐自体への
resolver配線は行っていない。したがって本修正だけでは、その具体的な
STOP事例(Stage 3d §3記載)は解消されない。標準分岐への配線要否は
範囲拡大が必要な別判断であり、Fable/ユーザー判断を仰ぐ(§5参照)。

### 3. Family X production runner配線

`er019_family_x_audio_production_runner_01.py`の`generate_family_x_b1_
segments()`内、`voice01.generate_charon_english`呼び出し(topic_intro/
preview/comment_1-4、計6箇所)と`news_tail_fix.generate_news_narration_
wide_margin`呼び出し(full_story_part1/2/3/in_one_line、計4箇所)の
**全て**へ`enable_pronunciation_resolver=True`を明示的に渡した。Family
A/B/C(legacy、`er003_v1_b1redesign_*`/`er012_*`/`er013_*`等)の既存
呼び出し元コードは本タスクで一切編集していない(既定Falseのまま、
挙動無変更)。A2側(`generate_family_x_a2_segments`)は管理ID名(B1B-EN-
WIRING)どおり対象外(A2は既にPhase 2でJA/EN標準経路が配線済み)。

### 4. OPEN-199是正: JA ASR Validator句読点正規化

`er007_ja_asr_validator_01.py`の`normalize_ja()`/`_PUNCT_RE`へ、以下を
既存の句読点除去と同じ層(NFKC正規化後の除去regex)へ追加した:
- 引用符: ASCIIストレート(`"`/`'`)・カーリー(`“”‘’`)。
  日本語の「」『』は既存どおり(変更なし)。
- 全角スペース(`　`): 既存のNFKC(→半角スペース変換)+`\s`除去で
  実質的には既に機能していたが(実測確認済み、下記参照)、既存の全角
  ！？と同じ防御的明示のスタイルで追加した。
- 「…」(ellipsis、U+2026)由来の非発話記号: NFKC正規化により「…」は
  視覚的に2文字以上のASCIIピリオド("...")へ分解されることを実測で
  発見した(**Phase 2 REPORTが「全角疑問符・全角スペース」と報告して
  いた原因の実態は、実は「…」→"..."のNFKC分解漏れだったことが今回の
  実装で判明**、下記§3参照)。単独の"."(小数点等)は除去対象に含めない
  よう、2文字以上連続するピリオドのみを対象にする専用regex
  (`_ELLIPSIS_RUN_RE = re.compile(r"\.{2,}")`)を追加した(数値比較
  ロジック`_DIGIT_RE`への影響を回避)。
- 中点(・): 既存どおり対象(コードを読んで既存動作を確認、変更なし)。

数値・否定語検出(`_extract_numbers_ja`相当の`_DIGIT_RE`/
`safety._has_negation_ja`)や、opcode単位の読み比較ロジック(`_reading_
equal`等)自体は一切変更していない。

### 5. Stage 3d副次発見の是正: Key Phrase Japanese meaning Lock記録漏れ

`er003_v1_n3_01_tts_generate.py`の`generate_a2_japanese_with_fallback()`
(A2 Key Phrase Japanese meaning等が使う標準+fallback合成関数)に
`@review_lock.guarded_generate("ja")`を追加した。

**原因**: この関数は内側で`@review_lock.guarded_generate_with_language_
arg`済みの`c.generate_narration_snippet_verified_strict`(標準経路)を
呼んだ後、自前の(未guardの)fallback(minimal instruction)ループを実行
する。従来はこの関数自身がguardされておらず、標準経路のみで
`record_outcome()`が(不合格として)確定してしまい、その後fallbackが
実際に成功しても`review_lock_state.json`へ反映されないギャップが
あった(small_bag A2 `meaning_5`で実測、Stage 3d §0既述)。

**修正**: 関数自身をguardすることで、内側の呼び出しは既存の
reentrancy guard(同一out_pathが`_ACTIVE_GUARDED_OUT_PATHS`に入っている
間は二重にcheck_before_generation/record_outcomeしない、OPEN-105 fix、
`generate_key_phrase_component_verified`の既存reentrancy保護と同じ
機構)により自動的にスキップされ、`record_outcome()`はこの関数全体の
最終結果(fallback成功後の結果を含む)で一度だけ呼ばれるようになる。
状態ファイル(`review_lock_state.json`)自体はこの修正では書き換えて
いない(次回実行時から正しく記録されるようになるだけ)。

唯一のProduction呼び出し元(`generate_a2_japanese_with_reading_safety`)・
既存test(`er007_ja_tts_retry_path_fix_test_01.py`/`er009_ja_foreign_
token_gate_01_test_01.py`、いずれも`out_path="dummy.wav"`使用)は
narration layout非該当のためcheck_before_generation/record_outcome
両方でbypassされ、無変更のまま全PASSを確認した(§4)。

**関連する未修正の同種ギャップ(発見、報告のみ)**: EN側の対称パターン
`crosslevel_common.generate_english_segment_with_fallback()`(A2英語
標準+fallback)も、構造的には同じ「内側guarded標準+自前未guarded
fallback」パターンを持つ。本タスクでは委任範囲(small_bag A2
meaning_5のJA側)のみを修正しており、このEN側の同種修正は行っていない
(実害が実測されたわけではないが、理論上同じ既存コードの構造的ギャップ。
Fable/ユーザー判断案として`OPEN_ITEMS.md`記載案§5に記録)。

## §3 実測で判明した事実(正直な報告)

Phase 2 REPORT(§17 JA-1、§22-1)は差分文字を「(1)引用符脱落 (2)全角
疑問符「？」不再現 (3)全角スペース脱落」と記述していたが、本タスクで
実際のJA-1 2回目実行evidence(`er025_output/pronunciation_resolution_
phase2_evidence_01/ja1_second_run_evidence_01/ja1_second_run_evidence_
full_result.json`)のcanonical_text/asr_textを直接読み、`normalize_ja()`
の前後で差分をopcode単位で検証した結果、**実際に残っていた差分は
(1)カーリー引用符2文字と(2)「…」のNFKC分解由来"..."の2種類のみ**
だった。全角疑問符(`？`)は元々NFKCでASCII"?"へ変換され、既存の
`!?`除去規則で正しく除去できていた(fullwidth `！？（）`等の既存規則
自体もNFKC後は同様に実質dead-codeであることを確認したが、既存コードの
防御的記述スタイルを踏襲しそのまま残した)。全角スペースもNFKC+`\s`で
既に正しく除去できていた。この事実を`er007_ja_asr_validator_01_test.py`
のfixtureコメントへ記録した。

修正後、JA-1の実データ(canonical_text+3回分のASR実文字列)を
`classify_ja_asr_match()`へ直接投入し、3回とも`TRUE_CONTENT_MISMATCH`
から`PHONETIC_MATCH`(expected_readings指定時)/`ASR_VALIDATION_
UNCERTAIN`(指定なし時、entity_likeとして正しくCascade対象化)へ改善
することを実測確認した(§4「実データ再現」参照)。

## §4 Test結果

### 新規test

- `er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01.py`
  (新設、unittest、14件、全PASS): `generate_charon_english`/
  `generate_english_component_minimal_instruction`のresolver配線
  (hint注入あり/なし/既定disabled)、`generate_news_narration_wide_
  margin`への引数転送、Family Xランナーが実際に`enable_pronunciation_
  resolver=True`を渡すこと、Family A/B/C legacy呼び出し元の既定値が
  Falseのままであること(シグネチャ検査)、Key Phrase Japanese meaning
  Lock記録fix(fallback成功時RESOLVED/標準+fallback両方不合格時HUMAN_
  REVIEW_REQUIREDの両方を実際のLock store読み書きで確認)。cache-only
  (`pron_resolver_core.disable_web_lookup_for_test()`使用、API呼び出し
  0件)。
- `er007_ja_asr_validator_01_test.py`(既存fixtureスクリプトへ追加、
  print方式、全51件PASS、うちOPEN-199向け新規12件): 引用符/ellipsis
  正規化fixture5件、単独小数点非除去のregression確認1件、JA-1実データ
  再現3件×2パターン(expected_readingsあり/なし)。

### 既存test・回帰

- 変更した3関数(`generate_charon_english`/`generate_english_component_
  minimal_instruction`/`generate_news_narration_wide_margin`)を直接・
  間接に参照する既存unittest(`er007_ja_tts_retry_path_fix_test_01.py`/
  `er009_ja_foreign_token_gate_01_test_01.py`/`er011_open121_repetition_
  qa_production_wiring_01_test_01.py`[76件、149.7秒]/`er012_editorial_
  b_family_production_phase1_test_01.py`/`er012_editorial_b_family_
  voices_3v_production_wiring_phase1_test_01.py`/`er013_family_c_
  production_test_01.py`/`er020_tts_cooldown_local_rewrite_trial_01_
  test_01.py`/`er021_en_asr_semantic_equivalence_production_wiring_01_
  test_01.py`)を個別実行し全PASSを確認した。
- 既存JA fixture回帰(`er011_open145_ja_asr_variant_production_wiring_
  01_regression_run.py`、既存fixtureを再利用する専用回帰script):
  `all_ok: True`(POSITIVE/NEGATIVE/ENTITY_LIKE/PHONETIC_UNCERTAIN/
  WHOLE_TEXT_SCRIPT_MISMATCH等の全グループ)。
- 本番既存artifact(`er019_output/**/tts_generation_results.json`・
  `er012_output/**/tts_generation_results.json`・`er011_output/**/
  tts_generation_results.json`)のJA segment(非ASCII canonical_text)
  でaudio_classification∈{EXACT_MATCH, NORMALIZED_MATCH, PHONETIC_
  MATCH, READING_RESOLVED_MATCH}(=既存OK判定)だった369組のcanonical/
  ASRペアを、修正後の`classify_ja_asr_match()`(素の引数のみ)で再判定
  し、367組がPASSのまま維持されることを確認した。残り2組は、修正前
  コードでも同一の素の呼び出しでは既にPASSではなかった(実際の
  Production呼び出しは`expected_readings`/`known_key_phrase_terms`等の
  追加引数を渡しており、本簡易チェックはそれらを再現していないための
  既知の限界。個別に確認し、いずれも修正前後で判定が変化していない
  ことを`git stash`で明示的に検証済み、詳細は本タスクの作業ログ参照)。

### 回帰(`run_project_regression.py`)

複数回実行し(153ファイル・3300件超)、既知の非決定性(後述)を含め
以下を確認した:

| カテゴリ | 件数 | 内容 |
|---|---|---|
| Phase 2既知baseline(不変) | 4 FAIL + 2 ERROR = 6 | `test_case_0`(意図的)、`er003_test_p2j_investigate`3件、`test_per_file_counts_sum_matches_pattern_discovery`(ERROR)、`er015_standard_a2_6000_generation_first_trial_01_test_01`(loader ERROR) |
| 本タスクのuncommitted diffによる一時的自己診断FAIL(commit後にPASSへ戻る、Phase 2closeoutと同型の既知パターン) | 3 | `er019_family_x_pointless_01_test_01.test_family_a_files_have_no_working_tree_diff`(`er003_v1_sing01_voice01_generate.py`/`er003_v1_sing01_news_tail_fix.py`を含む保護list)、`er020_tts_cooldown_local_rewrite_trial_01_test_01`/`er020_tts_local_rewrite_natural_english_qa_trial_02_test_01`の同型git diff self-check(いずれも`er003_v1_sing01_voice01_generate.py`) |
| 本タスク無関係の既存pre-existing failure(`git stash`でA/B確認、本タスクの変更を全て除いても再現) | 3 | `er011_open112_trend_synthesis_mode_production_wiring_01_test_01.TestBuildCommonBlockDefaultByteParity`3件 |
| 全153ファイル同時実行時のみ間欠的に再現する既存test isolation課題(1回のみ観測、単独実行/2回の再実行では常にPASS) | 0〜2 | `er011_open121_...test_n3_01_a2/b1_body_loop_scopes_flag_to_4_segments_only`(`inspect.getsource()`ベースのsource文字列検査、単独実行・本ファイルとの2ファイル併走[90件、157秒]では常にPASS、`git stash`で本タスクの変更を除いた場合の同時実行では未再現・本タスクの変更を戻した後の再実行[2回]でも1回のみ再現・1回は未再現という非決定的挙動を実測。実行順序依存のcross-test汚染(153ファイル・3300件超の大規模suite既知の脆弱性領域、詳細後述)であり、単独実行で常にPASSする以上、実際の関数の挙動(`generate_a2_segments`/`generate_b1_segments`は本タスクで一切編集していない)自体に問題は無いと判断する) |
| 本タスク新規追加test | 14(unittest) | 全PASS(複数回の全体回帰でも常にPASS) |

代表実行結果: `collected=3329 passed=3318 failed=9 errors=2`(新規
regressionは無し、上表の説明済みカテゴリのみ)。

**正直な限界**: `test_n3_01_a2/b1_body_loop_scopes_flag_to_4_segments_
only`は、153ファイル一括実行時にのみ・かつ非決定的に(複数回試行して
1回だけ)再現した。原因はおそらく`inspect.getsource()`が大規模test
suite内の別ファイルの実行順序・状態に依存して不安定になる既存の
test infrastructure課題(このsuite自体の既知の脆弱性領域、詳細因果は
特定できていない)であり、単独実行・ペア実行では常にPASSすることを
複数回確認した。本タスクの対象関数(`generate_a2_segments`/
`generate_b1_segments`)は一切編集していない。追加調査・修正はスコープ
外(test infrastructure自体の課題)と判断し、実装せず本REPORTで報告
するに留める。

## §5 OPEN_ITEMS.md記載案(SSOTは本タスクでは編集しない、Fable/ユーザー判断待ち)

1. **OPEN-197クローズ提案**: `generate_charon_english`へopt-in配線完了
   (Family Xのみ有効化)。
2. **OPEN-198部分クローズ提案**: `generate_english_component_minimal_
   instruction`へopt-in配線完了、ただし到達経路は`generate_news_
   narration_wide_margin`の技術的fallbackのみ(§2-2の限界を参照)。
3. **新規起票案**: `generate_news_narration_wide_margin`の標準
   ENGLISH_STYLE_PREFIX分岐自体にはresolver未配線のまま(§2-2既述)。
   small_bag B1B `full_story_part2`/`full_story_part3`の実STOP解消には
   この分岐への配線が必要。委任文の明示的スコープ外のため実装していない。
4. **OPEN-199クローズ提案**: JA ASR Validatorの引用符・ellipsis正規化を
   実装、JA-1実データで実測確認済み。
5. **新規起票案**: `crosslevel_common.generate_english_segment_with_
   fallback()`が、Key Phrase Japanese meaning経路と同型の「内側guarded
   標準+自前未guarded fallback」構造を持つ(§2-5既述)。実害は未確認だが
   理論上同じLock記録漏れリスクを持つ。修正要否をFable/ユーザーが判断。

## §6 runtime evidence計画(Lock解除承認後に実施、本タスクでは未実施)

- **Family X B1B EN resolver配線の実効性確認**: small_bag B1B
  `preview`/`comment_1-4`(Altuzarra/minaudière等のブランド名を含む
  segment)のHuman Review Lockをユーザーが`approve_regenerate()`で
  解除後、`--stage tts --level b1b`を再実行し、`en_pronunciation_
  resolver_info`が実際にhitする(または既存Ledgerに該当entryが無く
  hints_applied=Falseのまま)ことを実測する。見積り: 既存retry予算
  (標準or fallback、実費用は前回Stage 3d実測[¥0〜数円]と同程度)。
- **OPEN-199修正の実効性確認**: Meta A2 `japanese_title`のHuman Review
  Lockをユーザーが解除後、`--stage tts --level a2`を再実行し、実際に
  ASR判定がPASSすることを実測する(cache hit想定のため追加API費用は
  ¥0〜数円)。
- **Guardrail案**: 各segment再実行あたり¥60(Phase 2 closeoutと同水準)。
- 上記いずれもHuman Review Lock解除はユーザーの明示的操作が必要な安全
  装置であり、本タスクでは一切実行していない(委任文の¥0方針どおり)。

## §7 Gate 3チェックリスト evidence表(`PM_GOVERNANCE.md`2節)

| Gate 3項目 | evidence | Status |
|---|---|---|
| Production正式初回経路 | `generate_charon_english`/`generate_english_component_minimal_instruction`/`generate_news_narration_wide_margin`いずれも既存Production関数、呼び出し元は無変更のままopt-in引数で拡張 | 充足 |
| retry・fallback・regenerationとの整合 | 標準/fallback retry予算(3回上限)は無変更。Human Review Lockは独自判断で解除していない(Key Phrase Lock記録fixも既存Lock機構[reentrancy guard]をそのまま再利用) | 充足 |
| DEV・Trial-onlyではないこと | 変更ファイルはいずれも共有Production module。opt-in引数は既定Falseで全既存呼び出し元は無変更 | 充足 |
| Production runtimeでの実発火 | ¥0方針のため本タスクでは実行していない(§6のruntime evidence計画はLock解除承認後) | **未充足(次回実施予定)** |
| 必要testのPASS | 新規test 14件(unittest)+新規fixture 12件(既存fixture scriptへ追加)全PASS、既存test(8ファイル)個別実行全PASS、既存JA fixture回帰all_ok:True | 充足 |
| runtime evidence | JA-1実データ(§3)・369組の実artifact再判定(§4)で確認、実TTS/ASR新規呼び出しは無し(¥0) | 部分充足(静的再判定のみ、実発火は§6待ち) |
| コスト影響評価 | ¥0(実測、API呼び出しなし) | 充足 |
| `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md` | 記載案のみ本REPORT §5に記録、SSOT本体は編集していない(委任文の指示どおり) | 記載案のみ(SSOT反映はFable判断後) |
| 必要なGit反映 | 本コミットでpush予定 | 充足(本コミット完了後) |
| Dangling Reference Check | 変更した3関数のシグネチャ拡張(既定引数追加のみ)、既存呼び出し元は全て無変更のまま。新規参照(Family Xランナー4箇所+2箇所)は全て実在する既存opt-in引数への参照 | 充足 |

## §8 変更ファイル一覧

- `er003_v1_sing01_voice01_generate.py`(OPEN-197: `generate_charon_
  english`へresolver配線)
- `er003_v1_repro01_main_generate.py`(OPEN-198: `generate_english_
  component_minimal_instruction`へresolver配線)
- `er003_v1_sing01_news_tail_fix.py`(OPEN-198: `generate_news_
  narration_wide_margin`への引数転送)
- `er019_family_x_audio_production_runner_01.py`(Family X B1B runnerが
  上記2関数へ`enable_pronunciation_resolver=True`を渡すよう配線)
- `er003_v1_n3_01_tts_generate.py`(Stage 3d副次発見: `generate_a2_
  japanese_with_fallback`のLock記録漏れ是正)
- `er007_ja_asr_validator_01.py`(OPEN-199: 引用符・ellipsis正規化)
- `er007_ja_asr_validator_01_test.py`(OPEN-199向けfixture追加)
- `er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01.py`
  (新設、OPEN-197/198配線+Lock記録fixのunittest)
