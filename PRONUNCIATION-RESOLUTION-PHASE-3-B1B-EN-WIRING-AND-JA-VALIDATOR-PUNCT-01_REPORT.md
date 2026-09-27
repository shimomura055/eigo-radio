# PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01 REPORT

作成: Sonnet実行層。委任文全文(初回)は
`docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_01.md`
に、Fable修正指示1回目の委任文全文は
`docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_02.md`
に、Fable修正指示2回目(Opus L2所見反映)の委任文全文は
`docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_03.md`
に保存済み。**¥0**(コード・test・fixtureのみ、TTS/ASR/LLM実行なし、Human
Review Lock解除なし、共有ストア書込みなし)。Fable Gate 3判定は本REPORTでは
自称しない(**Fable Gate 3判定待ち**のまま記載する)。§1〜§7は初回commit
(b3cb2308)時点の記述のまま残す。修正1回目の内容は§8「修正1回目」に、
Opus L2所見は§10、修正2回目の内容は§11に記録する(修正1回目commit
[8da4b190]後にOpus L2レビューを実施し、その所見をFableが本ラウンドの
委任文で中継した)。

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

## §8 修正1回目(2026-09-27、Fable指示: 標準ENGLISH_STYLE_PREFIX分岐への
配線+EN側Lock記録の同型ギャップ是正)

Fable判定: 初回の範囲指定(2関数)が狭すぎた。承認済み仕様は「Family X/Z
全経路で読み解決」であり、実際のsmall_bag B1B `full_story_part2/3`の
STOPは`generate_news_narration_wide_margin`の**標準ENGLISH_STYLE_PREFIX
分岐**(初回は対象外にした技術的fallbackとは別物)で起きている。これは
新仕様判断ではなく、初回で報告した実装穴(§2-2「重要な限界」・§5項目3)の
残りの是正。**¥0**(コード・test・fixtureのみ、TTS/ASR/LLM実行なし、Lock
解除なし、SSOT編集なし)、本ラウンドも変わらない。

### 1. 標準ENGLISH_STYLE_PREFIX分岐への配線(OPEN-198残課題の是正)

`er003_v1_sing01_news_tail_fix.py`の`generate_news_narration_wide_
margin()`の標準分岐(retryループ開始前でp9a.ENGLISH_STYLE_PREFIXから
prompt構築していた箇所)へ、`voice01.generate_charon_english`と**同一の
hook**(同じ関数`pron_resolver_core.resolve_and_augment_en_style_prefix`・
同じconfidence gate[`augment_style_prefix_with_pronunciation`の
min_confidence="medium"、core内部固定]・同じtelemetry形状
`en_pronunciation_resolver_info`)を追加した。hintが1件も無い場合は
`p9a.ENGLISH_STYLE_PREFIX`のまま変更しない(既存呼び出し元・既存
promptへの影響ゼロ)。`en_pronunciation_resolver_info`をOK/ASR_
VALIDATION_UNCERTAIN/最終STOPPED全ての戻り値へ追加した(A2/charon側と
同じ形状)。技術的fallback(`generate_english_component_minimal_
instruction`呼び出し)への転送は初回のまま無変更。この関数自身の他の
ロジック(trim・disfluency/repetition gate・cool-down・Local Rewrite
回復)は一切変更していない。

`enable_pronunciation_resolver=True`は初回commitで既にFamily X runner
(`er019_family_x_audio_production_runner_01.py`の`generate_family_x_b1_
segments()`)の`generate_news_narration_wide_margin`呼び出し4箇所
[full_story_part1/2/3・in_one_line]から渡されているため、Family X
runner側のコード変更は本ラウンドでは不要だった(初回配線がそのまま
標準分岐にも及ぶ)。Family A/B/C legacy呼び出し元は本ラウンドでも
一切編集していない(既定Falseのまま、挙動無変更、シグネチャ検査test
`FamilyLegacyCallersUnaffectedTests`で確認済み・無変更のまま維持)。

### 2. EN側Lock記録の同型ギャップ是正(§5項目5の解消)

`er003_v1_crosslevel_audio_02_common.py`の`generate_english_segment_
with_fallback()`(A2英語標準+fallback合成関数、`repro01.generate_
narration_snippet_verified_strict`[`@review_lock.guarded_generate_
with_language_arg`済み]を内側で呼んだ後、自前の未guarded fallback
[`_run_a2_minimal_fallback_attempt`]ループを実行する構造)へ、JA側
(`generate_a2_japanese_with_fallback`に`@review_lock.guarded_
generate("ja")`)と**完全に同じ最小差分**(関数自身に`@review_lock.
guarded_generate("en")`を追加するだけ)を適用した。既存のreentrancy
guard(同一out_pathが`_ACTIVE_GUARDED_OUT_PATHS`に入っている間は二重に
check_before_generation/record_outcomeしない、OPEN-105 fix)により、
内側の標準経路呼び出しは自動的にスキップされ、`record_outcome()`は
この関数全体の最終結果(fallback成功後の結果を含む)で一度だけ呼ばれる
ようになる。状態ファイル(review_lock_state.json)自体はこの修正では
書き換えない(次回実行時から正しく記録されるようになるだけ)。

唯一のProduction呼び出し元一覧(Grepで全列挙、`generate_english_
segment_with_fallback(`の実引数呼び出しのみ、defも除く): `er003_v1_a2_
point_heading_audio_01_generate.py`・`er003_v1_iran01_a2_audio_fix.py`・
`er003_v1_n3_01_tts_generate.py`(2箇所)・`er007_evidence_density_ab_
01_tts.py`・`er008_n7_content_audio_qa_02.py`・`er008_n7_pilot_run_
01.py`・`er008_n8_a2_resume_01.py`・`er011_no18_evidence_compression_a_
precision_21r_audio_stage.py`・`er019_family_x_audio_production_
runner_01.py`(A2ランナー、`generate_family_x_a2_segments`)・
`er021_en_asr_semantic_equivalence_production_wiring_01_run.py`/
`_fix1_run.py`。全て`(text, out_path, ...)`という共通シグネチャで直接
呼んでおり、guarded_generateのwrapper(`(text, out_path, *args,
**kwargs)`)とそのまま整合する(呼び出し元コード自体は本ラウンドで
一切編集していない)。

**副作用として発見・修正した既存test汚染**: `er007_ja_tts_retry_path_
fix_test_01.py`の`A2CooldownLocalRewriteWiringTests`内2件(Local Rewrite
回復のテストのため、意図的に標準命名慣習[".../<theme>/<level>/
narration/<segment>.wav"]に従う`out_path`を使っていた)が、リポジトリ
直下の固定パス`"unittest_scratch_theme/a2/narration/test_segment.wav"`
を共有していた。本ラウンドの guard追加により、この2 testが実際に
review_lock_state.jsonを読み書きするようになった結果、(1)同一
canonical_text+同一segment_idの2 test methodが同じLock entryを共有し、
一方が書いたHUMAN_REVIEW_REQUIRED状態がもう一方をブロックする(既存の
`_has_valid_narration_layout`docstringが警告する既知の罠と同型)、
(2)実行のたびにリポジトリへ実ファイルが残る、という2つの問題が
顕在化した(初回実装時は`generate_english_segment_with_fallback`自体が
guardされていなかったためこの問題は表面化していなかった)。この2 test
だけを、setUp/tearDownで`tempfile.mkdtemp()`ベースの一意なpathへ隔離する
よう最小修正した(test対象のロジック・assertion自体は無変更)。

### 3. test結果

- `er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01.py`
  (既存ファイルへ追加、unittest、**20件**[初回14件+本ラウンド6件]、
  全PASS): 標準分岐hint注入あり(`GenerateNewsNarrationWideMargin
  StandardBranchResolverWiringTests`、hit時にstyle_prefixへ実際に
  hintが注入されることをbuild_tts_prompt捕捉で確認)・なし(既定
  False・hintなし2パターン)・cache-only switch(`ALLOW_PRONUNCIATION_
  WEB_LOOKUP=0`下でconfidence=lowのentryがあってもresearch_
  pronunciations[有料API]を一切呼ばないことを`_fail_if_web_lookup_
  called`で保証)・EN側Lock記録fix(`EnglishSegmentWithFallbackLock
  RecordingFixTests`、fallback成功時RESOLVED/標準+fallback両方不合格時
  HUMAN_REVIEW_REQUIREDの両方を実際のLock store読み書きで確認、JA側の
  既存test`KeyPhraseJapaneseMeaningLockRecordingFixTests`と対になる
  構成)を追加。cache-only(`disable_web_lookup_for_test()`使用、API
  呼び出し0件)。
- `er007_ja_tts_retry_path_fix_test_01.py`(既存、28件、全PASS):
  上記2の副作用是正(tempdir隔離)を適用した上で全件PASSを維持。
- 既存test個別実行(全PASS、変更3関数[`generate_charon_english`は
  本ラウンド無変更だが関連group、`generate_english_segment_with_
  fallback`・`generate_news_narration_wide_margin`]を参照する既存
  unittest): `er009_ja_foreign_token_gate_01_test_01.py`(26件)・
  `er011_open121_repetition_qa_production_wiring_01_test_01.py`
  (76件、151.8秒)・`er012_editorial_b_family_production_phase1_
  test_01.py`(33件)・`er012_editorial_b_family_voices_3v_production_
  wiring_phase1_test_01.py`(56件)・`er013_family_c_production_
  test_01.py`(39件)・`er020_tts_cooldown_local_rewrite_trial_01_
  test_01.py`(17件)・`er021_en_asr_semantic_equivalence_production_
  wiring_01_test_01.py`(29件)。
- `er007_ja_asr_validator_01_test.py`(OPEN-199向け、本ラウンドでは
  無変更): 再実行し全51件PASSを再確認(既存fixture、regressionなし)。
- 既知の自己診断FAIL(commit前のuncommitted diffによる一時的なもの、
  Phase 2 closeoutと同型、commit後にPASSへ戻る想定): `er019_family_x_
  pointless_01_test_01.FamilyAUnchangedTest.test_family_a_files_have_
  no_working_tree_diff`(保護listに`er003_v1_sing01_news_tail_fix.py`が
  含まれるため、本ラウンドのuncommitted diffで一時的にFAIL、commit後に
  再確認予定)。
- `run_project_regression.py`: 本ラウンドでも実行し、代表実行結果
  `collected=3335 passed=3326 failed=7 errors=2`(初回commit時の
  `collected=3329`から新規test6件分[本ラウンドの追加test]増加した以外は
  同一)を確認した。内訳は初回commit時と同じ既知baseline: Phase 2既知
  (`test_case_0`[意図的]・`er003_test_p2j_investigate`3件・
  `test_per_file_counts_sum_matches_pattern_discovery`[ERROR]・
  `er015_standard_a2_6000_generation_first_trial_01_test_01`[loader
  ERROR]、計4 FAIL+2 ERROR)、pre-existing 3 FAIL(`er011_open112_trend_
  synthesis_mode_production_wiring_01_test_01.TestBuildCommonBlock
  DefaultByteParity`)、本ラウンドのuncommitted diffによる自己診断FAIL
  1件(`er019_family_x_pointless_01_test_01.FamilyAUnchangedTest.test_
  family_a_files_have_no_working_tree_diff`、保護listの`er003_v1_sing01_
  news_tail_fix.py`が対象、commit後にPASSへ戻る想定)。合計7 FAIL+2
  ERROR=9件、いずれも既知カテゴリのみで新規regressionは無い。初回で
  報告した間欠的flake(`test_n3_01_a2/b1_body_loop_scopes_flag_to_4_
  segments_only`)は本ラウンドの実行では再現しなかった(0件)。

### 4. §5(OPEN_ITEMS.md記載案)の更新

初回§5の項目3(標準ENGLISH_STYLE_PREFIX分岐未配線)は本ラウンドで解消
したため取り下げる。項目2(OPEN-198部分クローズ)は本ラウンドの配線に
より技術的fallback+標準分岐の両方が揃ったため、フルクローズ提案へ
更新する。項目5(EN側Lock記録の同型ギャップ)は本ラウンドで実装した
ため取り下げる。更新後のOPEN_ITEMS.md記載案(SSOTは本タスクでは編集
しない、Fable/ユーザー判断待ち):

1. **OPEN-197クローズ提案**(初回のまま維持): `generate_charon_
   english`へopt-in配線完了(Family Xのみ有効化)。
2. **OPEN-198クローズ提案**(本ラウンドで更新): `generate_english_
   component_minimal_instruction`への配線(技術的fallback経路)に加え、
   `generate_news_narration_wide_margin`の標準ENGLISH_STYLE_PREFIX
   分岐にも同一hookを配線完了。small_bag B1B `full_story_part2/3`の
   実STOP解消可否は§6のruntime evidence(Lock解除後)で確認予定。
3. **OPEN-199クローズ提案**(初回のまま維持): JA ASR Validatorの
   引用符・ellipsis正規化を実装、JA-1実データで実測確認済み。
4. **Lock記録fix完了報告**(本ラウンドで追加): Key Phrase Japanese
   meaning(JA側、初回)+`generate_english_segment_with_fallback`
   (EN側、本ラウンド)の同型Lock記録漏れギャップを両方是正完了。

### 5. §6(runtime evidence計画)の更新

- **Family X B1B EN resolver配線の実効性確認**(更新): small_bag B1B
  `preview`/`comment_1-4`(Altuzarra/minaudière等)に加え、本ラウンドで
  標準分岐に配線した`full_story_part2`/`full_story_part3`(実際に
  ASR_VALIDATION_UNCERTAINが観測されたsegment)も対象に追加する。
  ユーザーが該当segmentのHuman Review Lockを`approve_regenerate()`で
  解除後、`--stage tts --level b1b`を再実行し、`en_pronunciation_
  resolver_info`が実際にhitする(またはLedgerに該当entryが無く
  hints_applied=Falseのまま)ことを実測する。対象6 segment
  (preview/comment_1-4/fsp2/fsp3のうちLock対象、重複除く)。
- **OPEN-199修正の実効性確認**(初回のまま): Meta A2 `japanese_title`
  のHuman Review Lockをユーザーが解除後、`--stage tts --level a2`を
  再実行し、ASR判定PASSを実測する。
- **small_bag B1B KP再選定**(初回計画のまま、本ラウンドで追加言及):
  1 call分。
- **Guardrail案**: 各segment再実行あたり¥60(Phase 2 closeoutと同
  水準)、合計見積り上限**¥150**(6 segment+japanese_title+KP再選定
  1 callの合算、実費用はcache hit想定のため¥0〜数円/件と推定)。
- 上記いずれもHuman Review Lock解除はユーザーの明示的操作が必要な安全
  装置であり、本タスク(初回・本ラウンドとも)では一切実行していない。

### 6. Opus L2申し送り(初回3点+本修正2点を1表に統合)

| # | ラウンド | 項目 | 状態・懸念 |
|---|---|---|---|
| 1 | 初回 | `generate_news_narration_wide_margin`の標準ENGLISH_STYLE_PREFIX分岐がresolver未配線だった(§2-2既述の限界) | 本ラウンドで是正完了(§8-1)。A2標準経路・charon経路と同一hook/gateであることをtestで確認済みだが、Opusには「3箇所目の同型hookが本当に完全に同一ロジックか(confidence gate・telemetry形状のコピペずれが無いか)」の再確認を依頼したい |
| 2 | 初回 | `crosslevel_common.generate_english_segment_with_fallback()`がJA側と同型の「内側guarded標準+自前未guarded fallback」構造を持つ(§2-5、実害未確認のまま報告のみだった) | 本ラウンドで是正完了(§8-2、JA側と同一の`@review_lock.guarded_generate("en")`追加)。ただしこの関数は`generate_charon_english`(B1B専用)より遥かに多い11箇所のProduction呼び出し元(A2全体)から呼ばれており、Opusには「reentrancy guardが実際にA2の全既存呼び出し経路で二重記録を防げているか」の設計確認を依頼したい(実行環境でのruntime evidenceは§6計画、本ラウンドでは静的test確認のみ) |
| 3 | 初回 | JA ASR Validatorの既存fullwidth`！？（）`除去規則が、NFKC正規化後は実質dead codeだったと判明(§3)。既存コードの防御的記述スタイルを踏襲しそのまま残した | 未着手(観察のみ、実装変更なし)。Opusには「dead codeをそのまま残す判断でよいか、それとも将来の保守性のため削除すべきか」の方針確認を依頼したい |
| 4 | 本ラウンド | `generate_english_segment_with_fallback`にLock decoratorを追加した結果、既存test(`er007_ja_tts_retry_path_fix_test_01.py`)2件が標準命名慣習の`out_path`を使っていたため、実際にreview_lock_state.jsonをリポジトリ直下へ書き込み、かつ2 test間でLock状態を共有してしまう副作用が判明した(§8-2末尾) | tempdir隔離で修正済み(test対象のロジック自体は無変更)。Opusには「他にも同様の`_has_valid_narration_layout`を満たす`out_path`を使う既存testが、本タスクで確認した範囲外に残っていないか」の横断確認を依頼したい(本ラウンドはGrepで実引数呼び出し元のみ確認、既存test全件の網羅的監査はスコープ外) |
| 5 | 本ラウンド | §6のruntime evidence計画をLock対象6 segment+japanese_title+KP再選定1 callへ拡張し、Guardrail見積りを¥150へ更新した(§8-5) | 未実施(Lock解除はユーザー操作待ち)。Opusには「見積り¥150が実際のcache hit想定([EN低確信度entryのweb lookup発火可能性]を含む)と整合しているか」の確認を依頼したい |

## §10 Opus L2所見(逐語、修正2回目)

**正直な限界**: Sonnet実行層はOpus L2の生レビュー出力そのものには直接
アクセスしていない。以下は、Fableが委任文
(`docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01_03.md`
に保存済み)で中継したOpus L2所見の記述を、Sonnetが改変・要約せずそのまま
転記したものである(「逐語」の対象は委任文の当該箇所であり、Opus自身の
生ログ全文ではない)。

> S1: `er003_v1_sing01_news_tail_fix.py` `_local_rewrite_recovery_for_
> news_narration`(L281-286付近)へ `enable_pronunciation_resolver` を
> 引数追加し `__wrapped__` へ転送、戻りdictに `en_pronunciation_
> resolver_info` を `setdefault` で注入。
>
> S2: `er003_v1_sing01_voice01_generate.py` `_local_rewrite_recovery_
> for_charon_english` の戻りdictに `en_pronunciation_resolver_info` を
> 注入(hint自体は既に保持)。
>
> S3: 同ファイル `generate_charon_english` の技術的fallback(L159
> `MINIMAL_INSTRUCTION_PREFIX`)を、算出済みhitsで同一hookにより
> augment(非対称解消)。
>
> S4(a): `er025_entity_pronunciation_resolver_core_01.py` EN低confidence
> web lookupに `MAX_EN_WEB_LOOKUP_CALLS_PER_RUN`(JA同型、既定5)+
> telemetryを追加。
>
> N6/N7: blocked時戻り値形状の変化と累積会計(2→最大3/call)をREPORTに
> 記録(コード変更なし)。
>
> N4: fullwidth dead codeは現状維持。
>
> S5: (§8-6既存表項目5、Guardrail見積り¥150の整合性確認、Part 2
> runtime着手時に扱う)。

BLOCKERは無し、SHOULD_FIXがS1〜S5(うちS1〜S4がPart 1のコード対応対象、
S5はPart 2のGuardrail運用確認対象)、N4/N6/N7/N8/N9/N12はNOTE(N4/N6/N7は
本ラウンドで記録のみ、N8/N9/N12はPart 2 runtime着手時の事前措置対象)。

## §11 修正2回目(2026-09-27、Opus L2所見S1〜S4反映)

Fable判定: 修正1回目でOpus L2レビューへ提出した3件の申し送り事項(§8-6の
表)に対し、Opusが上記S1〜S5・N4・N6〜N9・N12を返した。BLOCKERは無かった
ため、SHOULD_FIX(S1〜S4)をコードへ反映する。**¥0**(コード・test
のみ、TTS/ASR/LLM実行なし、Human Review Lock解除なし、SSOT編集なし)。

### 1. S1: `_local_rewrite_recovery_for_news_narration`のresolver転送+telemetry注入

`er003_v1_sing01_news_tail_fix.py`の`_local_rewrite_recovery_for_news_
narration()`へ`enable_pronunciation_resolver: bool = False`と
`en_pronunciation_resolver_info: dict | None = None`の2引数を追加した
(前者が委任文で明示された追加引数、後者はsetdefault注入のフォール
バック値を保持するための付随引数)。

- `_retts_fn`内の`generate_news_narration_wide_margin.__wrapped__(...)`
  呼び出しへ`enable_pronunciation_resolver=enable_pronunciation_resolver`
  をそのまま転送した。これにより、Local Rewrite回復時の再TTS
  (`rewritten_text`に対する1回のみのattempt)でも、標準分岐の
  resolver hookが(呼び出し元がTrueを渡していれば)実際に発火する
  ようになった(修正前は常にFalseで固定され、書き換え後テキストに対する
  発音ヒント再解決が一切行われていなかった)。
- 呼び出し元(`generate_news_narration_wide_margin`本体、2箇所)を
  `enable_pronunciation_resolver=enable_pronunciation_resolver,
  en_pronunciation_resolver_info=en_pronunciation_resolver_info`を渡す
  よう更新した。
- 戻り値`resolved`へ`resolved.setdefault("en_pronunciation_resolver_
  info", en_pronunciation_resolver_info)`を追加した。`__wrapped__`の
  ほとんどの戻り値パス(OK/ASR_VALIDATION_UNCERTAIN/STOPPED)は転送した
  引数により自身のen_pronunciation_resolver_infoを持つが、禁止記号gate
  (symbol_findings)等、resolver hookより前で早期returnするパスは
  このキー自体を持たないため、呼び出し元が関数冒頭で算出済みの値を
  安全網として補う。

### 2. S2: `_local_rewrite_recovery_for_charon_english`のtelemetry注入

`er003_v1_sing01_voice01_generate.py`の`_local_rewrite_recovery_for_
charon_english()`へ`en_pronunciation_resolver_info: dict | None = None`
引数を追加した(委任文の記述どおり、hint自体[style_prefix_override]は
既にこの関数の既存引数として保持・転送されているため、`enable_
pronunciation_resolver`自体を`__wrapped__`へ新たに転送する変更は行って
いない)。呼び出し元2箇所を`en_pronunciation_resolver_info=en_
pronunciation_resolver_info`を渡すよう更新し、戻り値`resolved`へ
`resolved.get("en_pronunciation_resolver_info") is None`の場合のみ
呼び出し元の値を注入するガードを追加した(`__wrapped__`呼び出しは
`enable_pronunciation_resolver`既定Falseのため、resolved自身の当該
キーは常にNoneで返る。単純な`dict.setdefault()`はキーが既に存在すると
[値がNoneでも]上書きしないため、ここでは明示的な条件分岐を使った)。

### 3. S3: `generate_charon_english`技術的fallbackへのcache_hits適用(非対称解消)

`generate_charon_english`は関数冒頭で`en_pronunciation_resolver_info`
(cache_hitsを含む)を1回だけ算出するが、修正前はこの結果を標準style_
prefix(`style_prefix_override`)にのみ適用し、発話区間検出失敗時の技術的
fallback(`repro01.MINIMAL_INSTRUCTION_PREFIX`ベース)には一切適用して
いなかった(非対称)。

是正のため、`er006_pronunciation_tts_injection_01.py`の
`augment_style_prefix_with_pronunciation()`から、hitsを既存base
prefixへ適用する部分を`apply_precomputed_hints_to_style_prefix(style_
prefix, hits)`として抽出した(純粋な文字列整形のみ、Ledgerアクセス
なし)。`er025_entity_pronunciation_resolver_core_01.py`にこれを
呼び出す薄いwrapper`augment_style_prefix_with_cached_hits(style_prefix,
hits)`を追加した。`generate_charon_english`の技術的fallback直前で、
`enable_pronunciation_resolver`かつ`en_pronunciation_resolver_info`に
`cache_hits`がある場合のみ、算出済みのcache_hitsをこのwrapper経由で
`repro01.MINIMAL_INSTRUCTION_PREFIX`へ適用する。**新規Ledger読み取り・
新規web lookupは一切発生しない**(既に確定済みのhitsをそのまま文字列
整形するだけ)。

### 4. S4(a): EN web lookup run単位上限+telemetry

`er025_entity_pronunciation_resolver_core_01.py`の`resolve_and_augment_
en_style_prefix()`のlow-confidence再research経路(`en_research.
research_pronunciations`呼び出し)に、JA側`MAX_JA_WEB_LOOKUP_CALLS_PER_
RUN`と同型の`MAX_EN_WEB_LOOKUP_CALLS_PER_RUN`(既定5)+`_EN_WEB_LOOKUP_
CALL_COUNT`(run単位カウンタ、`reset_run_caches()`でリセット)を追加
した。上限到達時はfail-safeで`low_confidence_retry_attempted=False`の
まま(=再research不能)扱いにし、既存Gate(HUMAN_REVIEW/通常TTS)は一切
緩めない。`_log_telemetry()`(既存の`er025_output/pronunciation_
resolution_core_telemetry_01/telemetry.jsonl`へのbest-effort追記、JA側
と同一機構)で`en_run_lookup_cap_reached`/`en_web_lookup_call`の2
イベントを記録するようにした。上限超過時は`_EN_LOW_CONFIDENCE_RETRY_
DONE`へは追加しない(このrun内で恒久的にブロックするのではなく、単に
今回分のweb lookup予算切れであることを示すため)。

### 5. N4/N6/N7の記録(コード変更なし、委任文の指示どおり)

- **N4**: JA ASR Validatorのfullwidth`！？（）`除去規則は、初回§3で
  報告したとおりNFKC正規化後は実質dead codeだが、既存コードの防御的
  記述スタイルを踏襲し現状維持のまま(本ラウンドでも変更していない)。
- **N6/N7**: 「blocked時戻り値形状の変化」「累積会計(2→最大3/call)」
  について、Fableからの委任文はこの2点を「REPORTに記録(コード変更
  なし)」とのみ指示しており、Opusの生ログ自体にSonnetは直接アクセス
  していないため、具体的な該当箇所・数値の内訳をSonnet自身の解釈で
  断定することは避ける(誤った憶測を記録しない)。委任文の文言をその
  まま§10に転記したことをもって記録完了とし、詳細な原因分析・要否判断
  はFable/Opusへ差し戻す。

### 6. Test結果

- `er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01.py`
  (既存ファイルへ追加、**29件**[修正1回目20件+本ラウンド9件]、全PASS):
  S3(技術的fallbackへのcache_hits適用あり/なしの2件)・S2呼び出し元
  配線(stop_retrying時に`_local_rewrite_recovery_for_charon_english`
  へ算出済み`en_pronunciation_resolver_info`が渡ることを1件)・S2
  telemetry注入ロジック単体(2件)・S1転送+setdefault注入(4件、
  デフォルトFalse転送・True転送・setdefault注入・既存値の非上書き)を
  追加。cache-only(`disable_web_lookup_for_test()`使用、API呼び出し
  0件)。
- `er025_entity_pronunciation_resolver_core_01_test.py`(既存ファイルへ
  追加、print方式、**20件**[既存18件+本ラウンド2件]、全PASS): S4(a)
  のrun単位上限test(`test_resolve_and_augment_en_style_prefix_run_
  lookup_cap`、`en_research.research_pronunciations`をmockし、上限
  到達後は呼ばれないことを実カウントで確認)・S3の`augment_style_
  prefix_with_cached_hits`単体test(`test_augment_style_prefix_with_
  cached_hits_no_new_ledger_access`、`ledger.get_hint_for_text`を
  意図的に例外化しLedger非アクセスを保証)を追加。
- 既存test個別実行(全PASS、変更/参照ファイルを含む): `er007_ja_tts_
  retry_path_fix_test_01.py`(28件)・`er009_ja_foreign_token_gate_01_
  test_01.py`(26件)・`er012_editorial_b_family_production_phase1_
  test_01.py`・`er012_editorial_b_family_voices_3v_production_wiring_
  phase1_test_01.py`・`er013_family_c_production_test_01.py`(39件)・
  `er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`
  (29件)。
- `er020_tts_cooldown_local_rewrite_trial_01_test_01.py`(17件中16件
  PASS、1件は既知の自己診断FAIL): `ProductionModuleUnchangedTest.test_
  production_modules_have_no_uncommitted_diff_caused_by_this_trial`が、
  本ラウンドのuncommitted diff(`er003_v1_sing01_voice01_generate.py`が
  保護listに含まれる)により一時的にFAILした。修正1回目・Phase 2
  closeoutと同型の既知パターンであり、本commit後にPASSへ戻る想定。
- `run_project_regression.py`: 実行結果`collected=3344 passed=3333
  failed=9 errors=2`(153ファイル超規模、他Agentの並行作業由来の
  test増減を含むため、修正1回目時点の`collected=3335`からの純増分は
  本タスク起因の9件[新規unittest]と一致しない。詳細はGrep/個別実行で
  内訳を確認する)。詳細は次項参照。

### 7. `run_project_regression.py`の詳細内訳(既知カテゴリのみ、新規regressionなし)

代表実行(`-v 1`)のFAIL/ERROR一覧をGrepで抽出し、以下のみであることを
確認した。ログを精査した結果、`test_case_0
(er003_test_bad.FixtureTests.test_case_0)`は独立した4件目の失敗では
なく、`er003_test_p2j_investigate.py`の実test methodが自分自身の
内部で(カウント整合性を検証するため)動的に生成・実行する**入れ子の
合成fixture**(`unittest.TextTestRunner`をtest method内部から呼ぶ
自己完結runで、"Ran 3 tests ... FAILED (failures=1)"という別summaryを
標準出力へ印字する)の一部であり、その入れ子run自体の意図的な失敗
[assertTrue(False)]を出力しているだけで、outer(=`run_project_
regression.py`が実際に集計する)3344件のsuiteの`result.failures`には
含まれない。したがってPhase 2既知baselineの実際の件数は3 FAIL(=
`er003_test_p2j_investigate`のtest method 3件、いずれも上記の入れ子
runの結果とouter記録済みcountの整合性を検証するアサーションで実際に
FAILしている)+2 ERRORである(修正1回目REPORT §4の表記「4 FAIL+2
ERROR=6」は、この入れ子printを誤って独立の1件として数えていたための
誤記と判明した。SonnetはREPORT §1〜§8の既存記述自体は書き換えない
方針のためそのまま残すが、本ラウンドの集計はここで訂正した正しい
内訳を使う):

| カテゴリ | 件数 | 内容 |
|---|---|---|
| Phase 2既知baseline(不変、内訳は上記の訂正済み) | 3 FAIL + 2 ERROR = 5 | `er003_test_p2j_investigate`3件・`test_per_file_counts_sum_matches_pattern_discovery`(ERROR)・`er015_standard_a2_6000_generation_first_trial_01_test_01`(loader ERROR) |
| 本タスクのuncommitted diffによる一時的自己診断FAIL(commit後にPASSへ戻る、既知パターン) | 3 | `er019_family_x_pointless_01_test_01.test_family_a_files_have_no_working_tree_diff`・`er020_tts_cooldown_local_rewrite_trial_01_test_01`/`er020_tts_local_rewrite_natural_english_qa_trial_02_test_01`の同型git diff self-check(いずれも本ラウンドで変更した`er003_v1_sing01_voice01_generate.py`等が保護listに含まれるため) |
| 本タスク無関係の既存pre-existing failure | 3 | `er011_open112_trend_synthesis_mode_production_wiring_01_test_01.TestBuildCommonBlockDefaultByteParity`3件 |

合計9 FAIL+2 ERROR=11件、実行結果`collected=3344 passed=3333 failed=9
errors=2`と完全一致する。修正1回目時点(実行結果`collected=3335 failed=7
errors=2`、内訳は上記の訂正済みbaselineで数え直すと3 FAIL+2 ERROR+
自己診断FAIL1件+pre-existing3件=7 FAIL+2 ERROR)と比べ、自己診断FAILが
1件→3件に増えているのは、本ラウンドで新たに`er003_v1_sing01_voice01_
generate.py`(`_local_rewrite_recovery_for_charon_english`・技術的
fallback augmentation)を変更した影響で、このファイルを保護listに含む
複数の既存git-diff self-checkが同時にFAILするようになったため(commit
後は全て解消しPASSへ戻る想定、Phase 2 closeoutと同型の既知パターン)。
新規の実装regressionは無い。

## §12 変更ファイル一覧(初回+修正1回目+修正2回目、累積)

- `er003_v1_sing01_voice01_generate.py`(初回、OPEN-197: `generate_
  charon_english`へresolver配線。**修正2回目**: S2[`_local_rewrite_
  recovery_for_charon_english`の戻りdictへのtelemetry注入]・S3
  [技術的fallbackへの`augment_style_prefix_with_cached_hits`適用]を追加)
- `er003_v1_repro01_main_generate.py`(初回、OPEN-198: `generate_
  english_component_minimal_instruction`へresolver配線)
- `er003_v1_sing01_news_tail_fix.py`(初回: `generate_news_narration_
  wide_margin`の技術的fallbackへの引数転送。**修正1回目**: 同関数の
  標準ENGLISH_STYLE_PREFIX分岐自体にもresolver hookを追加。**修正2回目**:
  S1[`_local_rewrite_recovery_for_news_narration`への`enable_
  pronunciation_resolver`引数追加+`__wrapped__`転送+setdefault注入])
- `er003_v1_crosslevel_audio_02_common.py`(**修正1回目、新規**:
  `generate_english_segment_with_fallback`へEN側Lock記録fixの
  `@review_lock.guarded_generate("en")`を追加)
- `er006_pronunciation_tts_injection_01.py`(**修正2回目、新規**: S3向け
  `apply_precomputed_hints_to_style_prefix()`を抽出、`augment_style_
  prefix_with_pronunciation()`はこれを呼ぶよう内部委譲)
- `er025_entity_pronunciation_resolver_core_01.py`(**修正2回目、新規**:
  S4(a)[`MAX_EN_WEB_LOOKUP_CALLS_PER_RUN`+telemetry]・S3向け
  `augment_style_prefix_with_cached_hits()`wrapperを追加)
- `er019_family_x_audio_production_runner_01.py`(初回: Family X B1B
  runnerが`generate_charon_english`/`generate_news_narration_wide_
  margin`へ`enable_pronunciation_resolver=True`を渡すよう配線。修正
  1回目・修正2回目でのコード変更は無し[標準分岐配線・recovery配線は
  既存の呼び出し引数がそのまま効く])
- `er003_v1_n3_01_tts_generate.py`(初回、Stage 3d副次発見: `generate_
  a2_japanese_with_fallback`のLock記録漏れ是正)
- `er007_ja_asr_validator_01.py`(初回、OPEN-199: 引用符・ellipsis
  正規化)
- `er007_ja_asr_validator_01_test.py`(初回、OPEN-199向けfixture追加)
- `er007_ja_tts_retry_path_fix_test_01.py`(**修正1回目、新規**:
  `A2CooldownLocalRewriteWiringTests`の2 testを実Lock書込みに対応
  させるためtempdir隔離へ修正[試験ロジック自体は無変更])
- `er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01.py`
  (初回、OPEN-197/198配線+Lock記録fixのunittest新設。**修正1回目**:
  標準分岐resolver配線test4件+EN側Lock記録fix test2件を追加、計20件。
  **修正2回目**: S1〜S3向けunittest9件を追加、計29件)
- `er025_entity_pronunciation_resolver_core_01_test.py`(**修正2回目**:
  S4(a)のrun単位上限test・S3の`augment_style_prefix_with_cached_hits`
  単体testを追加、計20件)
