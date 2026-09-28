# TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01_REPORT.md

管理ID: TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B: 実装+runtime証拠+Regression+SSOT、委任_02)
実行: 2026-09-28(Sonnet実行層)
到達Status: **`APPROVED_FOR_PRODUCTION`(配線完了、Opus L2レビュー+Fable Gate 3判定待ち)**。`PRODUCTION_WIRED`は未宣言。

## §0 ユーザーChecklist(要旨)

- 初回Production path: 対象4ファイル(下記§1)へ配線済み。Production Master
  Storeとの競合: なし(sha256前後不変、確認済み、§4)。
- retry/fallback/regeneration/Local Rewrite等の後続経路: fallback(minimal
  instruction)経路は意図的に不変(FAMILY-X-02 D-1踏襲)。Local Rewrite
  (`er020_tts_retry_local_rewrite_01`)はcanonical text書き換えのみでstyle
  引数に関与しないため無影響(設計書§2(e)表)。
- Trial専用scriptだけに残っていない: `er033`(Production共有定数)・
  `er019`(Production runner)へ配線済み(§1)。
- runtime evidence/actual model・voice・style metadata: §4参照(A2経路は
  `style_prefix`フィールドで実文字列を確認、B1B経路は間接証拠のみ、§7-1)。
- ASR/drift/Regression: §3/§4参照。
- CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS: §5参照。
- Git: §6参照。

## §1 実装(設計書§3どおり、行番号もPhase A記載から不変)

1. `er003_b1_p9a_audio.py`(`generate_narration_snippet`): ja分岐を
   `style_prefix_override or JAPANESE_STYLE_PREFIX`へ変更(en分岐と対称化、
   既定None=従来挙動)。戻り値dictへ`"style_prefix": style_prefix`を追加
   (runtime evidence)。
2. `er003_v1_n3_01_tts_generate.py`: `generate_a2_japanese_with_fallback`/
   `generate_a2_japanese_with_reading_safety`へ`style_prefix_override:
   str | None = None`引数を追加。標準経路(`c.generate_narration_snippet_
   verified_strict`)へのみ転送、fallback(`_generate_a2_japanese_minimal_
   instruction`)は無変更。
3. `er033_tts_flash_lite_family_x_styles_01.py`: `FAMILY_X_ROLE_STYLE_JA`
   (J3逐語)を新設。`FAMILY_X_ROLE_STYLE_EN`のTOPIC_INTRO/FULL_STORY/
   IN_ONE_LINEをE0→E2へ値更新(PREVIEW/COMMENT/HEADING_READOUTは不変)。
   `style_instruction_version`相当の識別子はこのモジュールに存在せず
   (可変segmentはMaster Store対象外)、bump対象なしと判断。
4. `er019_family_x_audio_production_runner_01.py`
   (`generate_family_x_a2_segments`): `_role_style_ja()`を新設(EN
   `_role_style()`と同一backendゲート)、preview/comment_1〜4のみへ配線。
   japanese_titleは対象外のまま(Trial-02のJA_SEGMENTS範囲外のため)。

各箇所に管理IDコメント付与済み(`git diff`で確認可能)。

## §2 Fable設計判断の適用結果

1. **backendゲート**: JA(J3)はEN 6-roleと同一条件
   (`--tts-backend speech_metadata_flash_lite`明示時のみ)。既定backend
   (`structured_separation`)では`_role_style_ja()`がNoneを返し、既定
   `style_prefix_override=None`と同じ挙動(§4のテストで確認)。
2. **方式**: J3は長文`JAPANESE_STYLE_PREFIX`を**置換**(Trial-02[er044]と
   同一、併記ではない)。p9a.generate_narration_snippetのja分岐テストで
   置換方式であることを確認(§4)。
3. **適用範囲**: JA=Family X Standard(A2)のpreview/comment_1〜4のみ。
   EN=`FAMILY_X_ROLE_STYLE_EN`のTOPIC_INTRO/FULL_STORY/IN_ONE_LINEを
   E2へ更新(Role定数はlevel非依存のためStandard/Advanced両方のENへ反映)。
   PREVIEW/COMMENT/HEADING_READOUTは不変。
4. **共有関数の既定値**: 全てNone=従来挙動(Family A/B/C無影響、§4の
   `FamilyAUnchangedTest`テストの性質は§3参照)。

## §3 テスト結果

- 新規`er019_family_x_variable_role_style_wiring_01_test_01.py`(13 test、
  全PASS): (a)`FAMILY_X_ROLE_STYLE_JA`/E2 3roleがer044と逐語一致、
  (b)既定backendはNone/Flash-Lite明示時のみJ3(runner経由のmock test)、
  (c)`generate_a2_japanese_with_reading_safety`の既定転送がNone、
  (d)shell固定phrase解決関数(`_resolve_shell_english_style_prefix_
  override`)が不変、(e)Key Phrase系は`style_prefix_override`を受け取らない、
  (f)fallback(minimal instruction)経路はoverrideの影響を受けない。
- 既存テスト更新(E0→E2期待値、理由コメント付き):
  `er033_tts_flash_lite_family_x_styles_01_test_01.py`(2 test分割、
  E0不変roleとE2更新roleを別々にassert)、
  `er038_tts_all_spoken_role_style_trial_01_test_01.py`(2 test更新)、
  `er044_tts_variable_spoken_role_style_trial_02_test_01.py`(1 test更新、
  E0比較→E2比較)。
- `run_project_regression.py --pattern "er033*_test_*.py"`: 64/64 PASS。
- `--pattern "er038*_test_*.py"`: 16/16 PASS。
- `--pattern "er044*_test_*.py"`: 11/11 PASS。
- `--pattern "er019*_test_*.py"`: 142/143 PASS。1件FAIL
  (`er019_family_x_pointless_01_test_01.FamilyAUnchangedTest.
  test_family_a_files_have_no_working_tree_diff`)。このテストは
  `er003_b1_p9a_audio.py`/`er003_v1_n3_01_tts_generate.py`に**未コミットの
  git working tree差分が存在しないこと**を検査する(別タスク
  `NEWS-FAMILY-X-POINTLESS-TRIAL-01`が設けた、Family A共有ファイルへの
  意図しない変更混入を防ぐガード)。本タスクはこの2ファイルへの変更が
  承認済みscope(delegation記載の「本タスクの所有」4ファイル)そのもの
  であるため、commit前の一時的な状態としてFAILするのは想定内(commit後は
  working tree差分が解消されるため、このテストの検査対象[git status]
  上は再びPASSに戻る見込み。機能的な後退・regressionではない)。
- `-m unittest er019_family_x_variable_role_style_wiring_01_test_01 -v`:
  13/13 PASS(詳細ログはコマンド実行結果として本タスク実行中に確認済み)。

## §4 確認用再生成(Hormuz、専用out-dir、¥20内)

runnerのCLI(`--stage tts`)はsegment単位の部分実行を提供しない(level全体
[a2 12segment/b1b 12segment+KP]を一括生成)ため、delegation記載の代替方針
に従い、runnerを直接呼ばず、runnerが使う低レベル生成関数を対象segmentのみ
直接呼ぶ小スクリプト
`er019_family_x_variable_role_style_wiring_01_confirmation_regen_01.py`を
新規作成して使用した(記事text自体は再生成せず、既存Hormuz Flash-Lite run
`er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_
trial_01/hormuz__run_06_flashlite_full_kp/`のparts.json/support textを
readonly再利用)。

- 対象13segment、`--tts-backend speech_metadata_flash_lite`固定。
- **Standard(A2) JA 5segment**(preview/comment_1〜4): 全件OK・
  asr_verified=True。戻り値dict`style_prefix`フィールドが
  `FAMILY_X_ROLE_STYLE_JA`(J3)と逐語一致することを実測確認(byte一致)。
  model=`gemini-3.8-flash-lite-tts`、voice=`Aoede`。
- **Advanced(B1B) EN 6segment**(topic_intro/full_story_part1/
  full_story_part2[+見出し2件]/in_one_line): 全件OK・asr_verified=True、
  `instruction_type="english_style_prefix"`(またはwide_margin版、
  fallback未発火の間接証拠)。**ただし** `voice01.generate_charon_english`/
  `news_tail_fix.generate_news_narration_wide_margin`/`point_headings.
  generate`は本タスクのファイル所有範囲外のため`style_prefix`フィールドを
  持たず、実際に使われた文字列のJSON直接記録は無い(§7-1のOpus L2申し送り
  参照。コード読解では`flw.resolve_tts_call_and_prompt`へ同じoverride値が
  渡る設計を確認済み)。model=`gemini-3.8-flash-lite-tts`、voice=`Charon`/
  `Aoede`(segmentにより異なる)。
- **Standard(A2) EN 2segment**(full_story_part1/in_one_line、slower重畳の
  実測用): `in_one_line`はOK、`style_prefix`フィールドが
  `FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"]`(E2)+`\n`+
  `A2_SLOWER_PACE_INSTRUCTION`(逐語)の連結値と一致することを実測確認
  (slower指示との重畳が失われていないことを確認)。`full_story_part1`は
  **STOPPED**("Act One/Two/Three"の数詞読み`TRUE_CONTENT_MISMATCH`、
  standard 2回+fallback 1回とも不合格)。これはOPEN-201のPhase 3実測
  (同一記事・同一箇所)で既に確認済みのcontent-classification事象であり、
  Production full pipelineでは`retry_primitive`経由のLocal Rewrite
  Recovery(Luna)が自己解決する既存の安全網が働く想定だが、本確認スクリプト
  はrunner本体が使うLocal Rewrite Recovery層・`enable_connected_speech_
  equivalence_layer`・`enable_repetition_qa`を意図的に含めていない
  簡略版のため、この安全網が発動しなかった。J3/E2配線自体が原因の可能性は
  低いと判断(style変更ではなく数詞表記読み上げの既知の問題であり、
  設計書§9-2/§7に記録)。
- **費用実測**: ¥18.26(上限¥20以内)。
- **retry**: JA/EN大半のsegmentはcall_count=1(初回一発OK)。STOPPED
  segmentのみ標準2回+fallback1回=計3回(既存`PRODUCTION_MAX_TTS_ATTEMPTS`
  上限どおり、独自緩和なし)。
- **Production Master Audio Store**: `er006_output/master_audio_store_01/
  manifest.json`のsha256が作業前後で不変
  (`9070cb818999596e59bb8ec8a417999738dfba9ff0658857dfa5aa6629be888b`)。
  `reuse_telemetry.jsonl`/`manifest.json`自体は本タスク開始時点で既に
  他作業由来の未コミット差分(`M`)を持っていたが(セッション開始時の
  `git status`スナップショットで確認済み)、本タスクの確認用再生成前後で
  この2ファイルのsha256/内容に変化はなく、本タスクがこれらへ追記・変更を
  行っていないことを確認した。
- 詳細JSON: `er019_output/family_x_audio_production_wiring_01/
  variable_role_style_wiring_regression_01/hormuz/audit/
  confirmation_regen_results.json`/`confirmation_regen_summary.json`。

## §5 SSOT反映

- `CURRENT_SPEC.md`: 「可変segment Role Style(J3/E2)」節をStatus
  `APPROVED_FOR_PRODUCTION`(配線完了、`PRODUCTION_WIRED`判定待ち)へ更新、
  適用範囲・backendゲート・実装箇所・runtime evidence・Regression結果を
  追記。
- `DECISION_LOG.md`: 末尾に新エントリ`## TTS-VARIABLE-ROLE-STYLE-
  PRODUCTION-WIRING-01`を追加(実装内容・Fable設計判断の適用・テスト/
  Regression結果・確認用再生成の結果・費用・到達Status)。
- `OPEN_ITEMS.md`: OPEN-201本体行へ「2026-09-28追記2」を追加(JA側未配線の
  指摘はPhase Bで解消)。OPEN-229本体行へ「2026-09-28追記2(Phase B、最小
  導入済み)」を追加し、Status欄を`OPEN(最小導入済み、既定backendへの拡張は
  別判断待ちのためCLOSEしない)`へ更新(delegation記載どおりCLOSEはFable
  Gate 3後のため、Statusラベル自体は`OPEN`のまま維持)。
- `docs/pm/REPORT_LEDGER.md`: `TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02`行の
  直後に新規`TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`行を追加
  (Opus発火列: 「予定(Phase B後、Mandatory)」)。

### 差分所有者確認

1回目(タスク開始時、実装前): `git status --porcelain CURRENT_SPEC.md
DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/
PM_GOVERNANCE.md` → 出力なし(差分ゼロ、他Agent差分なし。`docs/pm/
ACTIVE_TASK.md`に記録済み)。
2回目(commit直前): 本REPORT作成後、commit実行前に再実行し結果を記録する
(§6参照)。

## §6 Git

commit前に2回目の差分所有者確認を実行し、対象ファイルのみをpath指定で
`git add`する。add対象: 実装4ファイル、更新した既存テスト3ファイル、新規
テスト1ファイル、新規確認用再生成スクリプト1ファイル、専用out-dirのjson
(wav/attempts wav非commit)、本REPORT、設計書、SSOT4点、delegation_log
(`_02.md`/`_02.md_check.json`)、`docs/pm/ACTIVE_TASK.md`。他Agent差分
(er045/046/047系、他delegation_log、er006 store等)はaddしない。

## §7 Opus L2論点(設計書§7再掲+Phase B新規発見)

設計書§7の1〜7に加え、Phase Bで新たに以下2点を発見・追記した(設計書§9-2/
§7にも同内容を記載):

**7-1. B1B(Advanced)EN経路のruntime evidence欠落**: `voice01.generate_
charon_english`/`news_tail_fix.generate_news_narration_wide_margin`/
`point_headings.generate`は`p9a.generate_narration_snippet`を経由しない
独自の戻り値dict実装であり、本タスクで追加した`style_prefix`フィールドが
伝播しない。実際の適用は`instruction_type`(fallback未発火の間接証拠)と
コード読解で確認したが、JSON直接証拠は無い。この3ファイルは本タスクの
ファイル所有範囲外のため変更していない。B1B側にも同様のフィールドを
追加するかはFable/Opus L2判断が必要な追加スコープ候補。

**7-2. 確認用再生成で1segment STOPPED(a2_en_full_story_part1)**:
OPEN-201既知のAct One/Two/Three数詞読みcontent-classification事象と一致
(本配線が原因ではないと判断)。本確認スクリプトはLocal Rewrite Recovery層
を含まない簡略版のため自己解決しなかった。Fable/Opus L2が必要と判断すれば
runner本体を通した完全経路でのRegression追加実施の余地がある(追加費用
発生のため¥20上限内では未実施)。

## §8 STOP有無

STOPなし。全ての確認は¥20予算内・承認済みscope内で完了した。

## §9 commit/push

本REPORT作成後、実装commitとSSOT commitを分けて実行する(詳細は
delegation記載のGitセクションどおり)。commit hash・raw URLは
RESULT_PACKET/handbackへ記載する。
