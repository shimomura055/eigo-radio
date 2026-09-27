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
