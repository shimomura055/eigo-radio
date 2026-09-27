# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01_REPORT

## Phase 0: SSOT反映+配線設計(2026-09-27)

性質: ¥0。API呼び出し0件。Production code変更0件。SDK更新0件。実装は
次Phase(本REPORT末尾のGate 3チェックリスト参照)。

### 背景

ユーザーは2026-09-27、Gemini 3.8 Flash-Lite TTS(`gemini-3.8-flash-lite-
tts`、`speech_metadata`構造化方式)のProduction採用を正式決定した
(Family Xから段階導入、Status `VALIDATED` → `APPROVED_FOR_PRODUCTION`。
`PRODUCTION_WIRED`ではない)。詳細な決定内容・比較材料は`TTS-GEMINI-3.8-
FLASH-LITE-NEXT-TRIAL-01_REPORT.md`(§14-§23)および`docs/pm/flash_lite_
production_adoption_packet_01.md`(A〜I)を参照。本Phaseはこの決定を
SSOTへ反映し、Production配線の詳細設計を行った。

### 実施内容

1. **SSOT反映**: `CURRENT_SPEC.md`(「Gemini 3.8 Flash-Lite TTS」行を
   `APPROVED_FOR_PRODUCTION`へ更新、`PRODUCTION_WIRED`未到達・Family X
   先行・A/B/C対象外・Z別判断・6-role初期仕様を明記)、`DECISION_LOG.md`
   (新規エントリ、ユーザー決定16項目の必須確認事項を記録)、
   `OPEN_ITEMS.md`(OPEN-201をGate 3配線追跡へ切替、Production採用可否の
   USER_DECISION_REQUIREDを解除)、`docs/pm/REPORT_LEDGER.md`(新規管理
   ID行)。
2. **配線設計書**: `docs/pm/design_flash_lite_family_x_wiring_01.md`
   新規作成(a〜kの11節、Family X実関数チェーンの特定、retry/fallback/
   regenerationの同一関数経由確認、pronunciation resolver統合設計、
   role別style定数の位置、SDK導入計画、model routing、regression
   fixture化、公平cost比較計画、rate limit確認計画、実装Phase分割案)。

### 主要な設計上の発見(次Phase実装の前提として重要)

- `generate_charon_english`/`generate_english_segment_with_fallback`/
  `generate_a2_japanese_with_fallback`/`generate_charon_japanese`は
  **Family A/B/C(legacy)からも呼ばれる共有関数**であるため、内部を
  無条件でspeech_metadata方式へ置き換えると「Family X先行、A/B/C対象外」
  というユーザー決定に反してlegacy Familyの挙動まで変わってしまう。
  対策として、既存の`enable_pronunciation_resolver=True`(Family X
  runnerのみが明示的に渡す既存パターン)と同型の、新規opt-in引数
  (`tts_backend`)を追加する設計とした(設計書§a-3)。
- `er006_model_routing_contract_01.require_provider("TTS", ...)`は
  現状どのProduction call siteからも呼ばれておらず未配線であることを
  Grepで確認した(設計書§g)。TTS routing契約の構造自体を変える必要は
  ない。
- Pronunciation resolverは英語側(style_prefixへのhint注入)・日本語側
  (text自体への表記置換)で仕組みが異なり、英語側はspeech_metadata.
  styleへの移行と矛盾しない(text不変の原則を保ったまま)。日本語側は
  speech_metadata方式と無関係な層のため変更不要(設計書§c)。
- `_generate_a2_japanese_minimal_instruction()`は上記4共有関数と異なる
  独立コードパスであり、fallback対応のためこのヘルパーにも個別に
  opt-in分岐が必要(見落としやすい箇所として設計書§bに明記)。

### USER_DECISION候補(新規、設計書末尾に詳細)

1. A2 6% slowdown post-processの適用方針(そのまま適用して実測するか、
   A2は別Phaseへ先送りするか)。
2. 公平な1回完成cost比較(新規記事での実測)の実施タイミングと承認範囲。
3. rate limit確認(Phase 3の逐次運用)の報告粒度。

### Gate 3チェックリスト(空欄、次Phase以降で1件ずつ埋める)

| # | 項目 | 状態 |
|---|---|---|
| 1 | Production正式初回pathへのspeech_metadata方式実装 | 未着手 |
| 2 | retry・fallback・regenerationでの同一実装経由 | 未着手 |
| 3 | Human Review Lockとの整合 | 未着手 |
| 4 | Pronunciation・Reading Resolverとの統合 | 未着手(設計は完了、実装は次Phase) |
| 5 | voice指定 | 未着手(設計は完了、変更不要と判断) |
| 6 | role別style正式仕様化(6-role) | 未着手(定数モジュール新設が必要) |
| 7 | A2 6% slowdown post-processとの関係 | 未着手(USER_DECISION候補あり) |
| 8 | ASR validation流用 | 未着手(設計は完了、変更不要と判断) |
| 9 | cost ledger・telemetry正式統合 | 未着手(設計は完了、既存cl.segment_contextで自動記録される見込み) |
| 10 | SDK 2.25.0 Production `.venv`導入 | 未着手 |
| 11 | フル回帰(3300+件規模) | 未着手 |
| 12 | 実際のmodel_id・routing runtime evidence | 未着手(設計は完了、result["model"]既存フィールド流用) |
| 13 | rate limit・concurrency確認 | 未着手 |
| 14 | Act One型digit読みのregression fixture化 | 未着手 |
| 15 | 現行モデルとの公平な1回完成cost比較 | 未着手(USER_DECISION候補あり) |
| 16 | rollback可能性確認 | 設計完了(2段階rollback案: SDK pin戻し+tts_backend切替) |

### STOP該当

無し(Phase 0の範囲はSSOT反映+設計のみ、コード変更・API呼び出しを
伴わない)。

### 参照

`docs/pm/flash_lite_production_adoption_packet_01.md`、`TTS-GEMINI-3.8-
FLASH-LITE-NEXT-TRIAL-01_REPORT.md`(§14-§23)、`docs/pm/design_flash_
lite_family_x_wiring_01.md`、`DECISION_LOG.md`本管理ID冒頭エントリ、
`OPEN_ITEMS.md` OPEN-201。

## Phase 1: opt-in実装(2026-09-27〜28)

性質: ¥0。API呼び出し0件。Production `.venv`(google-genai 2.11.0)は
完全無変更。追加したのはコード(opt-in引数・新規モジュール・テスト)のみ。

### 実施内容(diff要約)

**新規モジュール**
- `er033_tts_flash_lite_family_x_styles_01.py`: Trial Stage3
  (`er022_tts_gemini_3_8_flash_lite_next_trial_01_stage3.py`の
  `ROLE_ATTEMPT1_STYLE`/`FALLBACK_STYLES`)とbyte-identicalな6-role
  style定数(Family X専用)。定数・文字列・辞書のみでbehaviorを持たない
  (Dangling Reference Check、下記参照)。
- `er033_tts_flash_lite_backend_wiring_01.py`: TTS backend抽象の本体。
  `resolve_tts_call_and_prompt()`(既定`structured_separation`では
  byte-identical、`speech_metadata_flash_lite`では新方式)、
  `make_speech_metadata_call_fn()`(実API呼び出しはPhase 1では一度も
  実行されない)、WAV/PCM防御(`_decode_audio_defensive`/
  `_resample_to_common_rate`/`_float_to_pcm16_bytes`)、SDKバージョン
  fail-closedガード(`assert_sdk_supports_speech_metadata()`、
  `MIN_SUPPORTED_GENAI_VERSION=(2,25,0)`未満で`TTSBackendSDKUnsupportedError`
  即時送出)、`resolve_actual_model_name()`(結果dictの既存`"model"`
  フィールドへ実際のmodel_idを記録)。

**共有TTS関数8箇所へ`tts_backend`引数を追加**(全て既定
`"structured_separation"`、byte-identical): `er003_b1_p9a_audio.
generate_narration_snippet`、`er003_v1_sing01_voice01_generate.
generate_charon_english`/`_local_rewrite_recovery_for_charon_english`/
`generate_charon_japanese_minimal_instruction`/`generate_charon_japanese`、
`er003_v1_repro01_main_generate.
generate_narration_snippet_verified_strict`/
`generate_english_component_minimal_instruction`、`er003_v1_sing01_
news_tail_fix.generate_news_narration_wide_margin`(新規
`style_prefix_override`引数も追加)/`_local_rewrite_recovery_for_news_
narration`、`er003_v1_sing01_point_headings_aoede.generate`(新規
`style_prefix_override`引数も追加)、`er003_v1_crosslevel_audio_02_
common.generate_english_segment_with_fallback`/
`_run_a2_minimal_fallback_attempt`/`_local_rewrite_recovery_for_
english_segment_with_fallback`、`er003_v1_n3_01_tts_generate.
_generate_a2_japanese_minimal_instruction`(委任文で名指しされた
「見落としやすいfallbackヘルパー」)/`generate_a2_japanese_with_fallback`/
`generate_a2_japanese_with_reading_safety`/
`generate_charon_japanese_with_reading_safety`/
`generate_a2_segment_with_slowdown`。

**Family X runner**(`er019_family_x_audio_production_runner_01.py`):
`--tts-backend` CLI引数(既定`structured_separation`)、
`generate_family_x_b1_segments`/`generate_family_x_a2_segments`への
スレッド、role別style(`_role_style()`ヘルパー、`speech_metadata_
flash_lite`選択時のみ有効)、`entry_point.json`/`tts_generation_
results.json`/`run_summary_tts.json`への`tts_backend`記録、各segment
結果dictへの実際のmodel_id記録(`resolve_actual_model_name`経由)。

**Model Routing Contract**(`er006_model_routing_contract_01.py`):
`PROCESS_MODEL_MAP`へ`"FAMILY_X_FLASH_LITE_TTS": "gemini-3.8-flash-
lite-tts"`を追加。既存の単一値契約の構造は変更していない。

**Regression fixture**(`er003_test_v1_n3_01_tts_generate.py`):
`TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01_REPORT.md`§22.5のAct One/
Two/Three実測(digit読み vs word読み)に基づく`ActHeadingDigitReading
RegressionTests`(2件)を`classify_asr_match`のtext-onlyフィクスチャ
として追加(API呼び出し0件)。

**新規テスト3ファイル、計46件**: `er033_tts_flash_lite_family_x_
styles_01_test_01.py`(9件、Trial定数とのbyte一致・6-role網羅・
Dangling Reference Check)、`er033_tts_flash_lite_backend_wiring_01_
test_01.py`(22件、既定backend byte-identical・SDK fail-closed・
model routing統合・WAV/PCM防御・speech_metadata call_fn形状)、
`er033_tts_flash_lite_family_x_wiring_phase1_regression_01_test_01.py`
(15件、8共有関数それぞれの既定backendプロンプトがbyte-identicalで
あることを実際の`_call_tts_with_retry`呼び出しをmockして直接確認)。

**既存テスト7ファイルの互換修正**(新規`tts_backend`引数追加に伴う
mock stub側の`TypeError`修正、`**kwargs`または明示引数追加のみ):
`er003_test_b1_p4c_audio.py`、`er007_reading_validation_wiring_test_
01.py`、`er011_tts_attempt_audio_retention_wiring_01_test.py`、
`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_
01.py`、`er011_open121_repetition_qa_production_wiring_01_test_01.py`、
`er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`、
`er012_b_family_voices_a2_new_topic_production_01_test_01.py`。

### 実装中に発見・修正したバグ(本Phase内で完結)

`resolve_tts_call_and_prompt()`の初期実装は既定backend分岐で
`er003_b1_p4c_audio`/`er006_batch_tts_wiring_01`を自前でfresh import
していたため、既存テスト(`er025_pronunciation_resolution_phase3_
b1b_en_wiring_01_test_01.py`、OPEN-197/198 pronunciation resolver
wiring test)が使う`mock.patch.object(caller_module, "p4c", ...)`
パターン(呼び出し元モジュールの名前空間ごと差し替える既存方式)が
効かなくなり、5件(errors=3、failures=2)が新規regressionとして
発生した。原因はfresh importが呼び出し元モジュールのグローバル
名前空間ではなく`er033`モジュール自身のimportを参照していたため。
対策として`resolve_tts_call_and_prompt(..., build_tts_prompt=None,
make_batch_tts_call_fn=None)`を追加し、各呼び出し元が自分の既存
`p4c.build_tts_prompt`/`batch_wiring.make_batch_tts_call_fn`参照を
明示的に渡すよう6ファイル7箇所を修正した(省略時のみ`er033`自身が
fresh importするfallbackは残す)。修正後、該当29件全てPASSを確認。
同型のバグが`er011_open121_repetition_qa_production_wiring_01_test_
01.py`内の別ローカルfake(`fake_minimal`、kwargs非対応)でも1件発見され、
`**_kw`追加で解消した。

### Dangling Reference Check結果

- `er033_tts_flash_lite_family_x_styles_01.py`は定数以外の呼び出し
  可能オブジェクトを一切持たない(`annotations`以外の`dir()`結果に
  関数・クラスが存在しないことをテストで確認)。
- Trial本体`er022_tts_gemini_3_8_flash_lite_next_trial_01_stage3.py`
  からは本Phaseの新規モジュール群への参照は一切追加していない(Grep
  で確認、importは無し)。
- Family A/B/C(legacy)呼び出し元コード自体は本管理IDで一切編集して
  いない(共有関数側にoptional引数を追加しただけ、legacy側の呼び出し
  行は無変更)。`FamilyLegacyCallersUnaffectedTests`/
  `FamilyLegacyCallersUnaffectedTests`相当のシグネチャ検査
  (`enable_pronunciation_resolver`と同型の`tts_backend`既定値検査)は
  `er033_tts_flash_lite_family_x_wiring_phase1_regression_01_test_01.py`
  内の各`DefaultBackend*Tests`で担保。
- Family X runnerのみが`er033_tts_flash_lite_family_x_styles_01`を
  importする(Grepで確認、他のimport元は無し)。

### テスト結果・regression確認

- 新規3ファイル: 46件全PASS。
- 既存修正7ファイル + 関連する共有関数を持つ既存suite(計約40
  ファイル、`er003`〜`er030`台の関連regression): 全PASS(修正過程で
  発見した2種のバグ[上記]を解消後)。
- `run_project_regression.py`(全件、pattern`er0*_test_*.py`):
  collected=3398 passed=3387 failed=9 errors=2(作業ディレクトリに
  本Phaseの未commit差分がある状態での実測)。内訳を`git stash`で
  clean HEADと比較し切り分け:
  - 8件(failed=6/errors=2: `er003_test_p2j_investigate.py`の
    テスト件数照合4件[コミット履歴が進み過去の固定件数と現在の
    collected総数が乖離する既知のドリフト]、`er011_open112_trend_
    synthesis_mode_production_wiring_01_test_01.py`の`build_common_
    block`baseline一致3件[時刻表記コロン全角対応など、本Phaseと
    無関係な既存コミットに起因]、`er015_standard_a2_6000_generation_
    first_trial_01_test_01.py`のmodule-level import時RuntimeError
    1件)は**clean HEAD(stash後)でも同一に再現し、本Phaseと無関係な
    既存baseline**であることを確認済み(delegationで言及された
    「既知6件」からさらに増えている点はSSOT側の既知件数記載が
    stale化していることを示唆し、別途報告に値するがPhase 1の
    スコープ外)。
  - 3件(failed=3: `er019_family_x_pointless_01_test_01`の
    `test_family_a_files_have_no_working_tree_diff`、`er020_tts_
    cooldown_local_rewrite_trial_01_test_01`/`er020_tts_local_
    rewrite_natural_english_qa_trial_02_test_01`の`test_production_
    modules_have_no_uncommitted_diff_caused_by_this_trial`)は、
    working-tree差分ゼロを要求するgit-diffガードテストであり、
    本Phaseが委任文で明示的に指示された共有ファイル
    (`er003_v1_n3_01_tts_generate.py`/`er003_v1_sing01_voice01_
    generate.py`)を意図的に変更しているために**commit前は必ず
    赤くなる**(`git status --porcelain`/`git diff --stat`が非空)。
    commit後は working tree = HEAD となるため自然に解消する見込み
    (post-commit再実行で確認予定、下記Opus引き継ぎメモにも記載)。
  - 結論: **本Phaseに起因する新規regressionは0件**。

### Gate 3チェックリスト更新

| # | 項目 | 状態(Phase 1後) |
|---|---|---|
| 1 | Production正式初回pathへのspeech_metadata方式実装 | opt-in配線完了(既定は既存のまま、API呼び出しは未実施=Phase 2) |
| 2 | retry・fallback・regenerationでの同一実装経由 | 完了(`_call_tts_with_retry`のduck-typed呼び出し1箇所を経由、8関数全てで確認) |
| 3 | Human Review Lockとの整合 | 完了(既存Lock機構は無変更、`tts_backend`はLock判定に影響しない設計) |
| 4 | Pronunciation・Reading Resolverとの統合 | 完了(EN側は`speech_metadata.style`へstyle_prefixをそのまま渡す設計、JA側は無関係) |
| 5 | voice指定 | 完了(既存voice名をそのまま流用、変更なし) |
| 6 | role別style正式仕様化(6-role) | 完了(`er033_tts_flash_lite_family_x_styles_01.py`新設) |
| 7 | A2 6% slowdown post-processとの関係 | 完了(post-process自体は無変更、`generate_a2_segment_with_slowdown`へ`tts_backend`スレッドのみ) |
| 8 | ASR validation流用 | 完了(既存関数をそのまま流用、変更なし) |
| 9 | cost ledger・telemetry正式統合 | 設計通り(既存の`cl.segment_context`等の自動記録に乗る、Phase 1では新規API呼び出しが無いため実測未取得) |
| 10 | SDK 2.25.0 Production `.venv`導入 | 未着手(Phase 2、意図的に本Phaseでは実施していない) |
| 11 | フル回帰(3300+件規模) | 完了(collected=3398、本Phase起因の新規failureは0件、上記参照) |
| 12 | 実際のmodel_id・routing runtime evidence | コード完了(`resolve_actual_model_name`で結果dict記録)、実API呼び出しでのruntime evidenceはPhase 2 |
| 13 | rate limit・concurrency確認 | 未着手(Phase 2、API呼び出しが発生してから観測可能) |
| 14 | Act One型digit読みのregression fixture化 | 完了(`ActHeadingDigitReadingRegressionTests`) |
| 15 | 現行モデルとの公平な1回完成cost比較 | 未着手(USER_DECISION候補のまま、Phase 2) |
| 16 | rollback可能性確認 | 設計通り実装(`tts_backend`引数を既定へ戻すだけで即rollback、SDK更新自体を伴わない) |

### Opus L2引き継ぎメモ(次Phaseレビュー向け)

1. **news_tail_fix/point_headings scope拡張**: 委任文が名指ししたのは
   4関数+`_generate_a2_japanese_minimal_instruction`だったが、実際の
   Family X B1B呼び出しチェーンをGrepで辿った結果、
   `generate_news_narration_wide_margin`と`point_headings.generate`にも
   `tts_backend`(および将来のrole別style用`style_prefix_override`)を
   通す必要があると判明し、追加で配線した(design docの「実コードが
   優先」原則に基づく)。
2. **A2側はrole別style非対応のまま**: `generate_family_x_a2_segments`
   には`tts_backend`をスレッドしたが、`_role_style()`によるrole別
   style注入はB1側のみ(A2はDECISION_LOG既定の6-roleがB1想定の
   role名[TOPIC_INTRO/PREVIEW/COMMENT/FULL_STORY/HEADING_READOUT/
   IN_ONE_LINE]であり、A2固有roleへの対応は未設計のため意図的に
   対象外とした)。Phase 2でのA2対応要否はUSER_DECISION候補。
3. **JA style「Trial未検証」フラグ**: `FAMILY_X_JA_STYLE_NOTE`定数に
   明記した通り、JA側の`speech_metadata.style`短文は本Phaseでは新規
   考案していない(各共有関数の既存`JAPANESE_STYLE_PREFIX`/minimal
   instructionテキストをそのまま流用する設計に留めた)。Trialで検証
   済みなのはEN側6-roleのみ。
4. **Key Phrase(shared_narration経由)は対象外のまま**: 設計書a-1の
   通り、Key Phrase生成はMaster Audio Store経由の別コードパスであり、
   本Phaseの`tts_backend`配線対象に含めていない(常に
   `structured_separation`)。
5. **SDK 2.11.0 vs 2.25.0テスト方針**: Production `.venv`が
   `types.SpeechMetadata`を持たないため、`er033_tts_flash_lite_
   backend_wiring_01_test_01.py`の`MakeSpeechMetadataCallFnShapeTests`
   は`_FakePart`/`_FakeContent`/`_FakeSpeechMetadata`等の軽量fake
   クラスで`google.genai.types`を`mock.patch.multiple(...,
   create=True)`により模擬し、実SDKスキーマに依存せず配線ロジックの
   形状のみを検証している。Phase 2でSDK 2.25.0導入後、実SDK型を使う
   統合テストへの置き換えを検討すること。
6. **git-diff系ガードテスト3件**: 上記「テスト結果」節参照。commit後
   に自然解消する見込みだが、post-commitでの`run_project_regression.py`
   再実行による最終確認をGate 3判定前に行うことを推奨する。

### Phase 2計画(未着手、次の委任待ち)

1. Production `.venv`へのgoogle-genai 2.25.0導入(`requirements*.txt`
   整理、他Gemini利用箇所のcompatibility確認、rollback手順の実地確認)。
2. Hormuz B1B(または同等の実記事)での実end-to-end実行
   (`--tts-backend speech_metadata_flash_lite`、実API呼び出し、
   実際のmodel_id/rate-limit/429・backoff件数の実測)。
3. 公平な1回完成cost比較: 既存クリーン記事1本の実測値、または
   ¥100上限の新規1本実測のいずれかで算出(USER_DECISION範囲、事前に
   Fable/ユーザーへ実施方法を確認してから着手)。
4. rate limit観測(Phaseごとの429/backoff件数報告、逐次運用時の
   concurrency確認)。
5. A2 role別style対応要否、JA style本文の是非、Key Phrase対象化の
   要否についてのUSER_DECISION確認。
6. 上記が全て完了した時点でGate 3 Mandatory Opus L2レビューを実施し、
   `PRODUCTION_WIRED`可否をFableが判定する。

### STOP該当

無し(本Phaseの範囲はコード実装+テストのみ、API呼び出し0件、SDK・
Production `.venv`変更0件)。

### 参照(Phase 1追加分)

`docs/pm/delegation_log/2026-09-27_TTS-GEMINI-3.8-FLASH-LITE-
PRODUCTION-WIRING-FAMILY-X-01_02.md`、`er025_pronunciation_
resolution_phase3_b1b_en_wiring_01_test_01.py`(既存pronunciation
resolver wiring test、本Phaseのbugfix対象)。

### Phase 1 post-commit独立検証(2026-09-28、別Agentセッションによる
セカンドオピニオン、追加コード変更なし)

「Phase 1が未commitのまま停止した」という前提で再開委任を受けたが、
作業開始後、commit `f548541e4567ff70f53bec1966836310101eb81a`
(2026-09-28 00:28:32、Management-ID trailer付き、origin/main反映済み)
が既に前Agent(または並行dispatchされた別インスタンス)によって完了・
push済みであることが判明した。追加のコード変更は行わず、以下を
commit `f548541e`のHEAD状態に対して独立に再実行し、正当性を確認した。

- Gatekeeper diff review: `er033_tts_flash_lite_backend_wiring_01.py`/
  `er033_tts_flash_lite_family_x_styles_01.py`/role別style値
  (Stage3 `ROLE_ATTEMPT1_STYLE`/`FALLBACK_STYLES`とbyte一致)/model_id
  (`gemini-3.8-flash-lite-tts`、routing contractと一致)/
  `resolve_tts_call_and_prompt`のmock.patch互換設計を確認。問題なし。
- 新規test 46件+OPEN-197/198 pronunciation resolver wiring test 29件+
  既存修正7ファイル関連suite 192件+`er003_test_v1_n3_01_tts_generate`
  23件(新規`ActHeadingDigitReadingRegressionTests`含む)を個別実行、
  全PASS。
- `run_project_regression.py`(collected=3398)再実行:
  passed=3390 failed=6 errors=2。内訳はPhase 1節記載のpre-existing
  baseline(p2j件数照合4件[1件はERROR]、er011_open112 baseline一致3件、
  er015 module-level import RuntimeError 1件)と完全一致。
  `test_combined_equals_sum_of_er002_and_er003`の根本原因を追加確認: 
  `er0NN_test_*.py`という旧命名規則専用globを使っており、er007以降の
  新命名規則(`er0NN_説明_test_NN.py`)ファイルを一切カウントできない
  (常に0件)という構造的欠陥であり、本Phase起因ではない
  (pre-existing、将来的な別タスクでのテスト側修正を提案するに留める)。
- git-diff系ガードテスト3件(`er019_family_x_pointless_01_test_01.
  FamilyAUnchangedTest`/`er020_tts_cooldown_local_rewrite_trial_01_
  test_01.ProductionModuleUnchangedTest`/`er020_tts_local_rewrite_
  natural_english_qa_trial_02_test_01.ProductionModuleUnchangedTest`)
  を個別実行し、post-commit状態でPASSであることを明示的に再確認した
  (前Agentの「commit後に自然解消する見込み」という予測の直接的な
  裏付け)。

結論: Phase 1のcommit・push内容に問題は見つからず、独立検証により
正当性を確認した。追加のコード変更・追加commitは行っていない
(paperwork commit[本追記+delegation_log `_03.md`]のみ)。詳細は
`docs/pm/delegation_log/2026-09-27_TTS-GEMINI-3.8-FLASH-LITE-
PRODUCTION-WIRING-FAMILY-X-01_03.md`。

## Phase 2: SDK 2.25.0 Production導入+end-to-end実測+公平cost比較
(2026-09-28)

性質: 実API呼び出しあり(実測費用合計**約¥55.90**、Guardrail¥200以内)。
Production `.venv`のgoogle-genaiを2.11.0→2.25.0へ実際に更新した
(rollback実演込み)。全TTS呼び出しで`TTS_EXECUTION_MODE=STANDARD`を
明示指定。委任文: `docs/pm/delegation_log/2026-09-28_TTS-GEMINI-3.8-
FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01_04.md`。

### 1. SDK導入・rollback実演

| 項目 | 結果 |
|---|---|
| Production `.venv`(導入前) | google-genai==2.11.0 |
| Production `.venv`(導入後) | google-genai==2.25.0 |
| 巻き込み変更(pip freeze差分) | `google-auth`のみ(2.55.2→2.58.1)。他パッケージ変化なし(`er033_output/sdk_upgrade_01/pip_freeze_before.txt`/`pip_freeze_after.txt`) |
| `.venv-ci`(requirements-ci.txt) | google-genai 2.14.0→2.25.0。他パッケージ変化なし(`pip list --format=freeze`差分で確認) |
| `.venv_trial_genai225` | 既に2.25.0のため変更不要(Trial専用のまま維持) |
| `pip check`(導入後) | `No broken requirements found` |
| **rollback実演** | `.venv`を2.11.0へ降格→`assert_sdk_supports_speech_metadata()`が`TTSBackendSDKUnsupportedError`を実際に送出することを確認(fail-closedガード実証)→2.25.0へ再導入→`pip check`再度クリーン、ガード正常復帰。1往復完了 |

`requirements-ci.txt`の正式再生成手順(ファイル冒頭コメント記載の
「クリーン`.venv-ci`再作成+`scripts/run_ci_tests.py`実行」)は、本更新とは
無関係な既存`ci_test_manifest.json`のドリフト(未登録testファイル多数、
SDK更新前から存在する既知の別問題)により実行できなかった。個別のTTS
関連import健全性は`.venv-ci`で直接確認済み(下記2節)。

### 2. フル回帰・import smoke test・fake→実SDK型置き換え

- **フル回帰(SDK 2.25.0導入後、Production `.venv`)**: `collected=3398
  passed=3390 failed=6 errors=2`。Phase 1 post-commit独立検証時と完全に
  同一の既知baseline(`er003_test_p2j_investigate.py`件数照合ドリフト
  4件、`er011_open112_trend_synthesis_mode_production_wiring_01_test_01.py`
  baseline一致3件、`er015_standard_a2_6000_generation_first_trial_01_test_01.py`
  module-level import RuntimeError 1件)と一致、**SDK更新起因の新規
  regressionは0件**。
- **Gemini利用箇所(パケットD-3一覧)のimport smoke test**: `er002_gemini_client`/
  `er003_b1_p7a_audio`/`er003_b1_p3v_capability`/`er003_v1_b1_p3v_generate`/
  `er003_v1_b1_p7a_generate`/`er003_v1_repro01_main_generate`/
  `er006_model_routing_contract_01`/`er006_batch_tts_wiring_01`/
  `er005_avr02_instruction_separation`/`er008_n7_baseline_reset_01`/
  `er008_n7_pilot_run_01`/`er011_open121_tts_repetition_general_qa_trial_01`/
  `er011_open107_opened_tts_diagnostic_trial_01`/
  `er011_kp_display_tts_separation_prod_wiring_01`の14ファイル全件、
  import時エラー0件。
- **fake `SpeechMetadata`→実SDK型**: `er033_tts_flash_lite_backend_wiring_01_test_01.py`へ
  `RealSDKSpeechMetadataIntegrationTests`(3件)を新規追加。既存の
  `_patch_genai_types`ベースのFake実装(`MakeSpeechMetadataCallFnShapeTests`)は
  `.venv-ci`等の旧SDK環境向けフォールバックとして残置し、実SDK型
  (`google.genai.types.Part`/`Content`/`SpeechMetadata`)を一切patchせず
  そのまま使う統合テストを別クラスとして追加した(該当ファイル計25件、
  全件PASS)。
- **最終フル回帰(本Phase全変更完了後、再実行)**: `collected=3401
  passed=3393 failed=6 errors=2`(collected/passed増分3件は上記新規
  テストのみ、failed/errorsは既知baselineと不変)。**本Phase起因の
  新規regression 0件を最終確認**。

### 3. end-to-end実測(Flash-Liteバックエンド、Hormuz B1B全12segment)

evidence run dir: `er019_output/family_x_audio_production_wiring_01/
family_x_b3_diversity_trial_01/hormuz__run_03_flashlite`(既存Production
artifact`hormuz__run_02`は無変更。scaffoldテキスト成果物[parts.json/
b1_support_texts.json/key_phrases]とKey Phrase音声[kp1-5 en/ja]は
`hormuz__run_02`からコピーして再利用し、Key Phrase分の新規TTS呼び出しは
発生させていない[Key PhraseはPhase 1範囲外のため常にstructured_
separation、詳細は同dir内`PHASE2_EVIDENCE_RUN_NOTE.md`]。主記事12segment
[topic_intro/preview/comment_1-4/full_story_part1-3+見出し2件/
in_one_line]のみ`tts_backend=speech_metadata_flash_lite`で新規生成)。

| 項目 | 実測結果 |
|---|---|
| 実行コマンド | `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level b1b --stage tts --out-dir <上記dir> --tts-backend speech_metadata_flash_lite --budget-jpy 30` |
| segment結果 | 12/12 `status=OK`(全segment最終PASS) |
| 実際のmodel_id(raw_usage_log実測) | 全14 gemini呼び出しで`"model_id": "gemini-3.8-flash-lite-tts"`を確認(routing contract`FAMILY_X_FLASH_LITE_TTS`経由) |
| tts_execution_mode | 全呼び出しで`"tts_execution_mode": "STANDARD"`を確認 |
| 費用 | **¥10.78**(gemini ¥9.16+openai_asr ¥1.63、runner自己集計とtoken数からの手計算[input 1,058/output 9,449 tokens×公式単価]が完全一致) |
| API呼び出し内訳 | gemini 14回(12segment+`full_story_part1`のみ2回追加retry)、openai_asr 15回。**429・失敗0件** |
| instruction leakage | 0件(全segmentのasr_textをrole別style文字列["conversational"/"engaging"等]でスキャンし、文脈上の自然な語のみでverbatim leakage無しを確認) |
| 異常長・clipping | 該当なし(全segment`clipping_detected=False`、duration実測値は12.7〜47.0秒の範囲で異常なし) |
| Human Review Lock | `review_lock_state.json`で12/12 segmentが`RESOLVED`、Lock到達0件・regeneration発火0件 |
| pronunciation resolver | 呼び出し経路は正しく実行された(`en_pronunciation_resolver_info.hints_applied=false`、本記事に発音辞書登録済み固有名詞が無かったため不発火。実際にhintが適用される正のケースの実測は本Phase範囲外) |
| A2 6% slowdown | 対象外(本evidence runはB1Bのみ、A2 flash-lite本文segmentの実行は未実施。post-process自体がbackend非依存であることはコードで確認済み[§(e)]) |
| **Act One/Two/Three digit読みの再現**(Gate項目14の追加実測) | `full_story_part1`のattempt1・attempt2の両方で"Act 1"/"Act 2"/"Act 3"というdigit読みが再発し、既存ASR検証が`TRUE_CONTENT_MISMATCH`で正しく検出(Trial N=1から実測でN=2以上へ拡大)。既存の**事前承認済み10分cool-down機構**(`er020_tts_retry_local_rewrite_01.maybe_cooldown_before_attempt`、`COOLDOWN_SECONDS=600`、attempt3直前に無条件発火する既存Production仕様。Flash-Lite固有ではなく全backend共通)が実際に600.004秒待機した後、attempt3(同一style・同一text、rewriteなし)で`NORMALIZED_MATCH`となりそのまま自己解決した(Luna Local Rewrite Recoveryへは到達せず) |

### 4. JA speech_metadataの初実測(Meta A2 `japanese_title`、1segment)

既存Production関数`n3_tts.generate_a2_japanese_with_reading_safety()`を
`tts_backend="speech_metadata_flash_lite"`で直接呼ぶ評価専用スクリプト
(`er033_output/phase2_ja_evidence_01/run_ja_flashlite_evidence_01.py`)を
新規作成し実行(既存Meta A2 Production artifact`japanese_title.wav`は
無変更、別path`er033_output/phase2_ja_evidence_01/japanese_title_flashlite.wav`
[.gitignore対象]へ出力)。

| 項目 | 実測結果 |
|---|---|
| 実行コマンド | `TTS_EXECUTION_MODE=STANDARD PYTHONPATH=. .venv/Scripts/python.exe er033_output/phase2_ja_evidence_01/run_ja_flashlite_evidence_01.py` |
| canonical text | Meta A2既存`entry_point.json`記載の日本語タイトル(逐語) |
| 結果 | `status=OK`、1 attempt目で`audio_classification=PHONETIC_MATCH`、`asr_verified=True` |
| 実際のmodel_id/voice | `gemini-3.8-flash-lite-tts`/`Aoede`(raw_usage_log実測) |
| style | 既存`JAPANESE_STYLE_PREFIX`(Trial新規JA style不使用、設計書§(c-2)/`FAMILY_X_JA_STYLE_NOTE`の方針どおり)をそのまま`speech_metadata.style`へ転送 |
| 費用 | ¥0.27(gemini ¥0.23+openai_asr ¥0.04) |

JA側の`speech_metadata`実測はStage1-3(Trial)・Phase1(opt-in配線)を
通じて本Phaseが初(Gate 3項目4のJA側実証として記録)。

### 5. 公平な1回完成cost比較(現行モデル、同一記事・同一12segment)

evidence run dir: `hormuz__run_03_baseline`(flash-lite runと同じ再利用
方針[scaffold/KP流用、主記事12segmentのみ新規生成]、`--tts-backend
structured_separation`[既定]で実行。既存`hormuz__run_02`実測[Adoption
Packet§B-5]が複数run分のretry混入で「1回完成コスト」として使えない
ことが既に判明していたため、新規1回完成実測を実施)。

| 項目 | Flash-Lite(本Phase実測) | 現行モデル(本Phase実測、baseline) |
|---|---|---|
| 実行コマンド | 上記3節参照 | `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level b1b --stage tts --out-dir <baseline dir> --tts-backend structured_separation --budget-jpy 100` |
| segment結果 | 12/12 OK | 12/12 OK |
| 総attempt数(gemini) | 14(12segment+2 retry) | 20(12segment+8 retry) |
| 総費用 | **¥10.78**(gemini¥9.16+ASR¥1.63) | **¥44.85**(gemini¥38.33+openai_asr¥2.26+openai/Luna¥4.26+azure/perplexity¥0) |
| retry内訳 | `full_story_part1`のみ2回追加(cool-down後に自己解決) | `comment_3`(1回追加)・`comment_4`(3回追加、Luna Local Rewrite Recovery経由で解決)・`full_story_part1`(1回追加)・`full_story_part2`(2回追加、Secondary ASR Cascade[azure+perplexity corroboration]経由で解決) |
| 429・失敗 | 0件 | 0件 |

**結論(誇張しない記載)**: 本実測では現行モデルの方がFlash-Liteより
総額・総attempt数とも多かった(¥44.85 vs ¥10.78、20 vs 14attempt)。ただし
これは主に本記事1回の実測でたまたま現行モデル側のretry率が高かった
ことに起因しており(`comment_4`のLocal Rewrite Recovery・
`full_story_part2`のSecondary ASR Cascade発火は現行モデルでも起こり得る
既存の想定内挙動)、**単価差(Adoption Packet§B-5: 同一token量なら
Flash-Liteは現行の約30.1%)とは別の要因**である。N=1回の比較であり、
retry率の再現性は統計的に未確認(既存Trialと同じ限界)。

### 6. rate limit・concurrency観測

| 項目 | 結果 |
|---|---|
| 429エラー件数 | 0件(flash-lite run 29回・baseline run 50回・JA evidence 2回、計81 API呼び出し中、`success=false`は0件) |
| 意図的cool-down発火 | flash-lite run 1回(`full_story_part1`)、baseline run 1回(`comment_4`)。いずれも既存の事前承認済み10分機構(§3参照)であり、Flash-Lite固有の新規挙動ではない |
| 並列実行 | 未検証(本Phaseは逐次実行のみ、設計書§(j)の計画どおりPhase 3以降の課題として残す) |

### 7. Dangling Reference Check(再実施)

`grep`で"stage3"/"Stage3"/`TRIAL_UNVALIDATED`等を全`er003_*.py`から検索した
結果、Trial本体(`er022_...`)への新規参照追加は無し(該当4ファイルの
うち3件は無関係な既存コード["Discovery Focus"独自のstage命名]、1件は
Phase1で追加済みの正当なtext-only regression fixtureのコメント記載)。
Production初回/retry/fallback/regeneration経路がTrial専用style・未承認
原則を参照していないことを再確認した(問題なし)。

### 8. Gate 3チェックリスト更新(Phase 2後)

| # | 項目 | 状態(Phase 2後) |
|---|---|---|
| 1 | Production正式初回pathへのspeech_metadata方式実装 | **完了**(実e2eでHormuz B1B全12segment実行、実際にAPI呼び出しが発生し全segment PASSしたことを実測) |
| 2 | retry・fallback・regenerationでの同一実装経由 | **完了**(実e2eで`full_story_part1`が実際にretry+cool-down経路を通過したことを実測。`approve_regenerate()`自体は本Phaseで発火するSTOPが0件だったため未発火[Lock全件RESOLVED]、コード経路はPhase1で確認済み) |
| 3 | Human Review Lockとの整合 | **完了**(`review_lock_state.json`で12/12 segment RESOLVED、Lock到達0件を実測) |
| 4 | Pronunciation・Reading Resolver統合 | **完了(EN側hook動作確認・JA側初実測)**。実際にhintsが適用される正のケースの実測は範囲外のまま(次回記事での確認を推奨) |
| 5 | voice指定 | **完了**(Charon/Aoede実際に使用確認)。**新規軽微所見**: flash-lite backendの`SpeechConfig`に既存英語経路が持つ`language_code="en-us"`相当の指定が無い(§9参照、Gate 3判定前の検討事項として記録) |
| 6 | role別style正式仕様化(6-role) | **完了**(実際にrole別style文字列がAPIへ送信されたことを実測) |
| 7 | A2 6% slowdown post-processとの関係 | 未実測のまま(本Phase e2eはB1Bのみ。USER_DECISION候補、次Phase) |
| 8 | ASR validation流用 | **完了**(NORMALIZED_MATCH/PHONETIC_MATCH/TRUE_CONTENT_MISMATCHが実際に正しく機能したことを実測) |
| 9 | cost ledger・telemetry正式統合 | **完了**(raw_usage_log.jsonl・attempt_history.jsonl・review_lock_state.jsonへの自動記録を実測) |
| 10 | SDK 2.25.0 Production `.venv`導入 | **完了**(rollback実演込み) |
| 11 | フル回帰(3300+件規模) | **完了**(最終`collected=3401 passed=3393 failed=6 errors=2`、新規regression0件) |
| 12 | 実際のmodel_id・routing runtime evidence | **完了**(raw_usage_log.jsonlで`gemini-3.8-flash-lite-tts`を実測) |
| 13 | rate limit・concurrency確認 | **部分完了**(429エラー0件を実測。並列実行は未検証のままPhase 3へ) |
| 14 | Act One型digit読みのregression fixture化 | **完了+実測補強**(text-only fixtureに加え、実e2eで同一現象を実際に2回連続再現し既存cool-downで自己解決したことを実測) |
| 15 | 現行モデルとの公平な1回完成cost比較 | **完了**(同一記事・同一12segment・新規1回完成実測、¥10.78 vs ¥44.85) |
| 16 | rollback可能性確認 | **完了**(SDK downgrade実演+tts_backend切替の2段階、両方実証) |

**Gate 3残項目**: #7(A2 6% slowdownとの関係、backend実測)、#13後半
(並列実行時のrate limit)。いずれもUSER_DECISION範囲またはPhase 3以降の
課題として次Phaseへ持ち越す。

### 9. Opus L2引き継ぎメモ(Phase 1引き継ぎ5点の状況+Phase 2新規所見)

Phase 1引き継ぎ5点の現状:
1. news_tail_fix/point_headings scope拡張 → 本Phase e2eで実際に
   正しく機能したことを実測確認(full_story_part2/3・見出しsegment
   全てOK)。
2. A2側role別style非対応のまま → 変更なし(A2 flash-lite本文の実行
   自体を本Phaseで行っていないため、Gate項目7とあわせて未解決)。
3. JA style「Trial未検証」フラグ → 本Phase§4で初実測(1件のみ、PASS)。
   6-role相当のJA短styleは依然未考案のまま(既存`JAPANESE_STYLE_PREFIX`
   を流用する現行方針は実測で問題なし)。
4. Key Phrase対象外のまま → 変更なし(本Phase evidence runもKey Phrase
   は既存音声を再利用、新規TTS呼び出しなし)。
5. SDK 2.11.0→2.25.0 → 本Phaseで完了(§1参照)。

Phase 2新規所見(次Phaseレビュー向け):
1. **flash-lite call_fnにexplicit timeoutが無い**: `er033_tts_flash_lite_
   backend_wiring_01.make_speech_metadata_call_fn()`の
   `GenerateContentConfig`には、既存英語経路(`er002_gemini_client.
   make_tts_call_fn`)が持つ`http_options=types.HttpOptions(timeout=
   TTS_TIMEOUT_MS)`[150,000ms]に相当する指定が無い。本Phaseの実行では
   全呼び出しが数秒〜15秒程度で完了しハングは一切発生しなかった
   (§3で観測した約10分の遅延は、既存の意図的な600秒cool-downによる
   ものであり、この所見とは無関係)。ただし将来的なAPI側の異常応答
   (無応答)に対する防御が無い状態であるため、Gate 3判定前に
   タイムアウト追加を検討することを推奨する。
2. **`language_code`未指定**: 上記Gate表#5参照。英語音声で実際に
   問題は観測されなかったが(全segment ASR PASS)、モデル側の暗黙
   デフォルト言語判定に依存している点は将来のモデル更新で挙動が
   変わるリスクがあるため、明示指定を追加候補として記録する。
3. **現行モデルの方がretry率が高かった実測(§5)**: 「Flash-Liteは
   品質面で同等以上」という従来の評価と矛盾しない(Flash-Liteは
   むしろ本実測でretryが少なかった)が、単価差の主張(30.1%)と
   実額差(24%)を混同しないよう、次回報告時も両者を明確に分けて
   記載すること。
4. **A2側flash-lite実測が依然0件**: Gate項目7(A2 6% slowdown)は
   Phase 3以降でA2記事1本の実測が必要(USER_DECISION候補、継続)。
5. **並列実行のrate limit確認は未着手**: 意図的な逐次運用を継続しつつ、
   Production通常運用でのFamily X複数記事同時生成時に429の有無を
   観測することを次Phaseの課題とする。
6. **既存Pronunciation Ledgerの誤登録を偶発的に発見(本Phase起因ではない
   既存バグ、修正せず報告のみ)**: baseline run実行中、Secondary ASR
   Cascadeが`full_story_part2`の"US"という語を未解決entityとして
   research対象にした際、`er006_output/pronunciation_ledger_01/
   ledger.json`へ`surface="us"`のエントリが追加されたが、その中身
   (`canonical_spelling`/IPA/pronunciation_hint等)は誤って"unknown"
   という**別の単語**の発音情報になっていた(cascade_unresolved_entity
   のresearch対象特定ロジックに既存の取り違えバグがある可能性を示唆)。
   本Phaseのtts_backend変更とは無関係な既存共有機構([ER-010-ENTITY-
   PHONETIC-CORROBORATION-01]系)の挙動であり、本Phaseでは修正せず
   事実のみ記録する(該当1件のみ、Gate判定・Cost・音声品質には
   影響しない)。

### STOP該当

無し(guardrail¥200に対し実測合計¥55.90で完了、STOP条件[累計超過見込み・
segment単位早期STOP・SDK regression・共有ストア破壊]のいずれにも該当
しなかった)。

### 参照(Phase 2追加分)

`docs/pm/delegation_log/2026-09-28_TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-
WIRING-FAMILY-X-01_04.md`、`er033_output/sdk_upgrade_01/`(pip freeze
前後)、`er033_output/phase2_ja_evidence_01/`(JA evidence一式)、
`er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_
trial_01/hormuz__run_03_flashlite/`・`hormuz__run_03_baseline/`(e2e
evidence一式)。
