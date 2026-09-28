# PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01

管理ID: `PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01`
Status: 実装完了(初回: A-1・A-2とも。修正1回目: Opus L2所見反映、
§8参照)。**Opus L2レビューはBLOCKER0件で実施済み(§8)。Fable Gate 3
判定: `PRODUCTION_WIRED`(2026-09-28、ただしA-1のLedger surface条件は
`DEFERRED`/`NOT_ADOPTED`のまま、OPEN-208で継続監視)**。Human Review
Lockの解除・small_bag再実行は
本タスク(初回・修正1回目とも)では一切行っていない。

対象: `RESULT_PACKET_FXD1.md`(`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01`
Stage 3e後の診断)で分類Aとされた2件の実装穴。
- A-2: A2英語本文fallback経路でEN pronunciation resolverが一度も呼ばれない
  (OPEN-203)。
- A-1: ASR `entity_like`判定が「本文中で大文字始まり」ヒューリスティック
  のみに依存し、小文字外来語(minaudière等)やLedger登録済みsurfaceを
  拾えない。

## §1 既存資産照合(分類A: 既存承認仕様の実装穴、新仕様ではない)

ユーザー既承認仕様(`PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-
PRODUCTION-01`/Phase 2〜3)は「初回/retry/fallback/regenerationを含む
全Production経路でresolver適用」。実装状況をコードで確認した結果:

- 標準経路(`er003_v1_repro01_main_generate.generate_narration_snippet_
  verified_strict`、293行目)は`language=="en"`であれば**無条件**に
  `pron_resolver_core.resolve_and_augment_en_style_prefix()`を呼ぶ
  (Phase 2で確立した既存方針、opt-inフラグ自体が存在しない)。
- `generate_english_component_minimal_instruction()`(496行目)は
  `enable_pronunciation_resolver: bool = False`(511行目)という
  opt-in引数を持つ(Phase 3、OPEN-198是正でnews_tail_fix.
  generate_news_narration_wide_margin[B1B技術的fallback]専用に追加)。
- `er003_v1_crosslevel_audio_02_common._run_a2_minimal_fallback_
  attempt()`(A2 fallback経路本体)は、この関数を呼ぶ際に
  `enable_pronunciation_resolver`引数を**渡していなかった**(修正前の
  コード: `repro01.generate_english_component_minimal_instruction(text,
  out_path, tts_backend=tts_backend)`)。既定Falseのため、A2の
  fallback(minimal instruction)経路ではEN resolverが一度も実行されない
  状態だった(=分類A、実装穴。B1B技術的fallback[Phase 3で対応済み]とは
  別の呼び出し元)。

## §2 A-1/A-2 diff要約

### A-2: `er003_v1_crosslevel_audio_02_common.py`

- `_run_a2_minimal_fallback_attempt()`: `generate_english_component_
  minimal_instruction(...)`呼び出しへ`enable_pronunciation_resolver=True`
  を追加。標準経路の既存方針(無条件適用)に合わせ、新規opt-inフラグは
  作らずここで直接Trueを渡す方針を採用した(既存の`enable_
  pronunciation_resolver`引数自体・その既定Falseは変更しない。
  news_tail_fix経由のB1B技術的fallback呼び出しは既存のまま無変更)。
- `generate_english_segment_with_fallback()`: `fallback_attempts.append
  (...)`の2箇所(TTS失敗等の早期return分岐・OK分岐)へ`en_pronunciation_
  resolver_info`キーを追加。最終`stopped_result`(標準+fallback全滅時)
  のtop-levelへ新規キー`fallback_en_pronunciation_resolver_info`を追加
  (直近fallback attemptの値、無ければNone)。

`generate_english_component_minimal_instruction()`自体は既に全return
パス(STOPPED/OK問わず)で`en_pronunciation_resolver_info`を含めて返す
実装(Phase 3で対応済み)だったため、A-2の修正は「呼び出し時に有効化する
引数を渡す」+「呼び出し元での戻り値集約時にキーを保持する」の2点のみで
足りた(`generate_english_component_minimal_instruction()`自体は無変更)。

### A-1: `er006_preprod_hardening_01_validation.py`

新設関数2件(`capitalized_flags()`の直後に配置):

- `loanword_flags(text) -> set[str]`: 原文中で非ASCII文字を1文字でも
  含む語を、diacritics除去後の小文字形で返す。
- `ledger_registered_entity_flags(text) -> set[str]`: `er006_
  pronunciation_ledger_01.get_low_confidence_entries_for_text(text)`
  (exclude_entity_types未指定=`cascade_unresolved_entity`含め全件対象、
  既存の語境界一致`_surface_matches_text`をそのまま再利用)で本文中に
  含まれるLedger entryを取得し、各entryの`surface`を構成する語のうち、
  **そのentry自身の`canonical_spelling`を`capitalized_flags()`(既存
  関数の再利用、ロジック複製なし)へ通した結果と一致する語だけ**を
  entity_tokensへ加える(同形一般語ガード)。

`_classify_asr_match_core()`の`entity_tokens`算出箇所を
`capitalized_flags(canonical_text) | loanword_flags(canonical_text) |
ledger_registered_entity_flags(canonical_text)`の3集合の合流へ変更。
それ以外(`protected_check()`・`determine_sub_reason()`等の分類ロジック
本体)は無変更。

**同形一般語ガードの根拠**: 本番Ledgerには`surface="us"`/
`canonical_spelling="unknown"`(OPEN-207)、`surface="plus"`/
`canonical_spelling="cascade"`、`surface="main story"`/
`canonical_spelling="cascade"`、`surface="one voice"`/
`canonical_spelling="one voice unknown"`、`surface="mini"`/
`canonical_spelling="mini"`(いずれもBLOCKER-1系の既知の誤登録・
placeholder値)が実在する。これらは`canonical_spelling`が軒並み小文字の
一般語であるため`capitalized_flags(canonical_spelling)`が空集合を返し、
ガードにより自動的に除外される。一方khaite/KHAITE・altuzarra/
Altuzarra・familymart/FamilyMart・kallmeyer/Kallmeyer・lindberg/
Lindberg・zabelina/Zabelina・toteme/TOTEME・meink/Meink・ganis/Ganis・
kristie tse/Kristie Tse・stephen reicher/Stephen Reicherは
`canonical_spelling`が大文字始まりのため引き続き救済される(本番
Ledger全35件を実データで手動照合、2026-09-28時点)。

## §3 呼び出しチェーン表(initial/retry/fallback/regenerationの4経路)

| 経路 | 関数 | EN resolver hook | 状態 |
|---|---|---|---|
| initial(標準経路1回目) | `generate_narration_snippet_verified_strict` | `resolve_and_augment_en_style_prefix`(無条件、Phase 2) | 既存のまま(無変更) |
| retry(標準経路2回目、`PRODUCTION_STANDARD_TTS_ATTEMPTS=2`) | 同上(forループ内で再呼び出し) | 同上 | 既存のまま(無変更) |
| fallback(minimal instruction、`PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS=1`) | `_run_a2_minimal_fallback_attempt` → `generate_english_component_minimal_instruction` | `resolve_and_augment_en_style_prefix`(`enable_pronunciation_resolver=True`) | **本タスクA-2で新規配線** |
| regeneration(`approve_regenerate`後の再生成) | `generate_english_segment_with_fallback`を再度呼ぶだけ(専用の別関数は無い、`review_lock.approve_regenerate()`でLock状態を`REGENERATE_APPROVED`にした後、通常のinitial/retry/fallbackループを再実行する構造) | 上記3行と同一(呼び出し経路が同じため自動的に同じhookを通る) | 既存のまま(A-2の効果がそのまま適用される) |

Dangling Reference確認: `_run_a2_minimal_fallback_attempt`は
`_local_rewrite_recovery_for_english_segment_with_fallback`の`_retts_fn`
からも呼ばれる(Local Rewrite回復の再TTS)。この経路も同じ関数を経由する
ため、A-2の修正は自動的にLocal Rewrite回復時のfallback再試行にも適用
される(呼び出し元を個別に修正する必要はなかった)。

## §4 Test結果

### 新規: `er006_pronunciation_phase4_entity_like_test_01.py`(A-1、15件、全PASS)

- `LoanwordFlagsTests`(3件): 非ASCII語検出/ASCII一般語非検出/ASCII固有
  名詞は対象外(役割分担確認)。
- `LedgerRegisteredEntityFlagsTests`(7件): cascade_unresolved_entity+
  大文字canonical→救済、`tts_injection_disabled=True`でも分類目的では
  使う、このtext内では小文字のままでもLedger側の大文字canonicalで救済
  (A-1(a)固有の効果)、同形一般語ガード(us/unknown、plus/cascade、
  未登録語mark)、Ledgerファイル不在時はfail-safeで空集合。
- `ClassifyAsrMatchEntityLikeGeneralizationTests`(5件): Ledger経由の
  Altuzarra、単独のloanword(minaudière)、既存negative fixture 3件が
  引き続きTRUE_CONTENT_MISMATCH(回帰確認)、同形一般語ガードのend-to-end
  確認、**small_bag A2 `full_story_part2`の実ASR書き起こし(Stage 3e
  artifact)を使った再分類**(修正前TRUE_CONTENT_MISMATCH→修正後ASR_
  VALIDATION_UNCERTAIN、entity_like_flags=`{True}`)。

全て一時Ledger(`er006_output/_test_pronunciation_phase4_entity_like_
tmp/`)へ隔離、本番Ledgerは読み書きしない。API呼び出し0件。

### 既存test個別実行(A-2関連、201件、全PASS)

`er021_en_asr_semantic_equivalence_production_wiring_01_test_01`・
`er012_b_family_voices_a2_new_topic_production_01_test_01`・
`er011_open121_repetition_qa_production_wiring_01_test_01`・
`er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01`・
`er007_ja_tts_retry_path_fix_test_01`・`er020_tts_retry_local_rewrite_
01_test_01`・`er008_crosslevel_audio_02_tts_cap_25_test_01`を実行し
201件全PASS(既存のfallback呼び出しmockが`generate_english_component_
minimal_instruction`への呼び出しに対し厳密なkwargs一致(`assert_called_
with`)を要求していないことを確認済みのため、`enable_pronunciation_
resolver=True`引数追加は既存test互換)。

### 既存本体fixture(`er006_preprod_hardening_01_validation_test.py`、57件、全PASS)

A-1変更後も本番Ledger(35 entry)を使った状態でPOSITIVE/AMBIGUOUS/
NEGATIVE全fixtureが期待通りに分類されることを確認(entity_tokens拡張に
よる既存回帰なし)。

### `run_project_regression.py`

`collected=3418 passed=3409 failed=6 errors=3`。内訳:

| カテゴリ | 件数 | 内容 |
|---|---|---|
| 既知baseline(pre-existing、本タスク無関係) | 5 FAIL + 2 ERROR | `er003_test_p2j_investigate`(3 FAIL)・`test_per_file_counts_sum_matches_pattern_discovery`(ERROR)・`er015_standard_a2_6000_generation_first_trial_01_test_01`(loader ERROR)・`er003_test_bad.FixtureTests.test_case_0`(1 FAIL) |
| 既知baseline(pre-existing、本タスク無関係) | 3 FAIL | `er011_open112_trend_synthesis_mode_production_wiring_01_test_01.TestBuildCommonBlockDefaultByteParity`3件 |
| 環境依存flake(本タスク無関係、新規発見) | 1 ERROR | `er012_e_family_entertainment_two_level_runner_test_01.TtsModeCliTests.test_batch_mode_without_reason_errors_via_subprocess`。個別実行して原因確認: Windows cp932コンソールencodingでsubprocess stderr読み取りthreadが`UnicodeDecodeError`を起こす環境依存の既存flake。当該test/対象ファイル(`er012_e_family_entertainment_two_level_runner_01.py`)は本タスクで変更したいずれのファイル(`er003_v1_crosslevel_audio_02_common.py`/`er006_preprod_hardening_01_validation.py`)もimportしていないことをGrepで確認済み。 |

合計6 FAIL + 3 ERROR = 9件、`collected=3418`のうち`passed=3409`と完全
一致。委任文が示した過去のbaseline(failed=6/errors=2)との差分は上記
環境依存flake1件のみであり、本タスク起因の新規regressionは0件。

## §5 runtime evidence(Guardrail¥15、evidenceモード、Lock解除なし)

スクリプト: `er025_pronunciation_resolution_phase4_a2_fallback_
evidence_01_run.py`。出力: `er025_output/phase4_evidence_01/`
(`evidence_result.json`・`cost_log.jsonl`・生成wav)。

安全設計:
- `OUT_PATH`を`er025_output/phase4_evidence_01/audio_not_narration_
  layout/full_story_part2.wav`とし、`er011_human_review_lock_01.
  _has_valid_narration_layout()`が**構造的に**Falseを返すようにした
  (パスの末尾2階層が`.../narration/<file>`という既存命名慣習に一致
  しない)。これによりHuman Review Lock機構(`review_lock_state.json`
  の読み書き・`save_tts_attempt_audio`によるattempts保存)は一切発火
  しない(スクリプト内でassertでも二重に確認、実行ログでも
  `narration_layout_detected=False`を確認)。
- `ALLOW_PRONUNCIATION_WEB_LOOKUP=0`(cache-only)・`TTS_EXECUTION_
  MODE=STANDARD`を明示的に環境変数で強制。
- 標準経路(`generate_narration_snippet_verified_strict`)を`unittest.
  mock.patch.object`で「標準2回相当消費済みのSTOPPED」に固定し、実TTS/
  ASRを一切呼ばずにfallback_budget=1へ収束させた(既存unittestと同じ
  技法)。これによりfallback(minimal instruction)経路の実TTS+実ASRが
  正確に1回だけ実行された。

実行結果(2026-09-28):
- `result.status = "ASR_VALIDATION_UNCERTAIN"`、`fallback_used = True`。
- 実ASR書き起こし: `"...Its examples included Kite's palm-sized
  evening clutch and Chanel's novelty minaudière..."`(khaiteのみ誤認識、
  minaudièreは今回のTTS発話ではASRが正しく綴った——毎回同じ誤りが
  再現するとは限らない実例)。
- `fallback_attempts_log[1].en_pronunciation_resolver_info =
  {"hints_applied": false, "cache_hits": [], "low_confidence_retry_
  attempted": false, "low_confidence_retry_improved": false,
  "research_meta": null}` — **修正前はこのキー自体がfallback attempt
  entryに存在しなかった(None扱いにすらならず欠落)。修正後はresolver
  が実際に呼ばれたことを示す値(空でも構造化された辞書)が入ることを
  確認した**。`hints_applied=false`になっている理由は、khaiteの
  Ledger entryが`entity_type="cascade_unresolved_entity"`のため
  `augment_style_prefix_with_pronunciation()`の`exclude_entity_types`
  フィルタで意図的にTTS注入対象から除外されている既存設計(§2-2、Opus
  L2 BLOCKER-1是正)によるものであり、A-2の配線自体は正しく機能して
  いる(resolverが「呼ばれたが除外設計により0件」という状態を正しく
  telemetryへ反映できている)。
- model_id: `gemini-2.5-pro-preview-tts`、voice: `Aoede`。
- cost: `cost_logger`(Azure Secondary ASR分のみ記録対象)に2件
  (各31.121秒、既存単価で軽微)。Gemini TTS・Primary ASRは既存cost_
  loggerの記録対象外だが、過去実績(`TTS-GEMINI-3.8-FLASH-LITE-
  PRODUCTION-WIRING-FAMILY-X-01_REPORT.md`Phase 3: 同モデル13segment
  ¥10.49≈¥0.8/segment)からGuardrail¥15内に収まると判断する(1
  segment・1 TTS attempt・1 Primary ASR callのみのため)。
- Production artifact(`er019_output/family_x_audio_production_
  wiring_01/family_x_b3_diversity_trial_01/small_bag__run_02/`)・
  Lock state(`review_lock_state.json`)への書き込みは0件(`git status`
  で確認)。

A-1側の再分類確認は§4のunit test(実ASR transcript、Stage 3e
artifactそのもの)で行った(§4参照)。同一runで両方を一度に検証しな
かった理由: 本evidence run自体のASR結果ではminaudièreの誤認識が
再現しなかった(ASRの非決定性)ため、A-1の効果を確実に示すには
Stage 3eで実際に観測された固定transcriptを使うunit testの方が
再現性・検証可能性の点で適切と判断した。

## §6 Gate 3チェックリスト(現況)

| # | 項目 | 状況 |
|---|---|---|
| 1 | コード実装(A-1・A-2) | 済 |
| 2 | Unit test(新規15件+既存201件+本体57件) | 済、全PASS |
| 3 | Fixture(proper noun/loanword/Ledger surface/negative control/same-form guard/実transcript) | 済(§4) |
| 4 | Runtime evidence(A-2実発火) | 済(§5) |
| 5 | Regression(新規regression0件を確認) | 済(§4) |
| 6 | SSOT反映(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER) | 済(本コミットに含む) |
| 7 | Git(delegation_log保存・path指定commit・push) | 本REPORT完成後に実施 |
| 8 | **Opus L2レビュー** | **未実施(Fable判断待ち)** |
| 9 | `PRODUCTION_WIRED`最終判定 | **未実施(Fable判断待ち)** |

## §7 Opus L2レビューへの申し送り事項(未実施、Fable起動時の参考)

1. A-1の同形一般語ガード設計(§2参照)は、本番Ledger35件全件との
   手動照合で意図通り動作することを確認したが、将来Ledgerへ新規
   登録される「大文字始まりのcanonical_spellingを持つ一般語」
   (例: 文頭のみ大文字になった一般名詞が誤ってcanonical_spellingへ
   そのまま保存されるケース)までは防げない設計であることに留意
   (現状データでは発生していないが、閉じた保証ではない)。
2. `ledger_registered_entity_flags()`は`classify_asr_match()`の
   ほぼ全呼び出し経路(EN ASR比較全般、Key Phraseを含む)へ影響する
   ため、本番Ledgerへの将来の書き込み(reactive research等)が
   意図せず一般語の安全弁を広げすぎないか、運用開始後の
   `ledger_health_check()`定期実行(OPEN-207参照)との組み合わせで
   継続監視する価値がある。
3. A-2のruntime evidence(§5)はkhaite自体の救済(TTS注入)を実証した
   ものではなく、あくまで「resolver hookが呼ばれ情報が伝播する」
   ことの実証である点をOpus L2へ明確に伝える必要がある(cascade_
   unresolved_entity除外設計により、既存3 segmentの再Lock解除には
   §8の追加判断が必要)。

## §8 再実行提案(対象segment・期待救済・見積・Guardrail、実施しない)

`RESULT_PACKET_FXD1.md`§4の修正案(1)(A-2配線)は本タスクで実装完了
したが、同§4が指摘した通り、khaite/altuzarra(いずれも`cascade_
unresolved_entity`型)は§2-2の既存除外設計により今回のA-2配線だけでは
TTS事前注入されない。A-1(entity_like一般化)は、たとえ注入されなくても
「entity不一致のみならretry消費せず安全側[ASR_VALIDATION_UNCERTAIN]
へ回る」効果を持つため、**再実行時にretryが早期に安全側で打ち切られ、
無駄なretry消費を減らせる可能性が高い**(§4の実データ再現で確認済み)。

- 対象: small_bag A2 `full_story_part2`・`full_story_part3`、small_bag
  B1B `full_story_part2`(いずれも既存Human Review Lockのまま、本タスク
  では解除していない)。
- 期待効果: A-1により、khaite/minaudière/altuzarra等の固有名詞ASR誤りが
  entity_onlyとして扱われ、TRUE_CONTENT_MISMATCHへ格上げされにくくなる
  (退行防止であり、TTS発話自体の正しさを保証するものではない。ASRが
  綴れないだけの場合はASR_VALIDATION_UNCERTAIN→Human Reviewが正しい
  最終非常口のまま)。
- 見積: segment数3×attempt上限3(標準2+fallback1)=最大9 attempt相当。
  実測単価(本タスクevidence: 1 attempt≒Guardrail¥15以内)から、3segment
  再実行の見積は**上限¥45程度**(Local Rewrite Recovery発火時は追加
  attemptが生じうるため、既存の事前承認済み上限管理[review_lock.
  PRODUCTION_MAX_TTS_ATTEMPTS]の範囲内で収まる)。
- Guardrail案: ¥50(3 segment、Local Rewrite Recovery余裕込み)。
- **Human Review Lockの解除はユーザー再承認後の別委任で実施すること
  (本タスクの範囲外、実施しない)**。

## §8 修正1回目(2026-09-28、Opus L2所見反映。¥0・API呼び出しなし・
Human Review Lock解除なし・small_bag再実行なし)

### §8-1 Opus L2所見照合表

Opus L2レビュー(BLOCKER 0件)を踏まえたユーザー正式決定に基づく対応表。
S2・N4〜N7は本委任(Sonnet修正1回目)の実装対象としては指示されなかった
項目であり、内容を本Reportで創作していない(Fable/Opus側の粒度・
判断のまま、Sonnet側では「対応不要/別途Fable判断」として扱う)。

| # | 所見概要 | 対応 | 決定/Status |
|---|---|---|---|
| BLOCKER | 0件(全経路同一hook確認済み、A-2はそのまま維持) | 対応不要 | 該当なし |
| A-1 Ledger surface条件 | Ledger登録surfaceをentity_like判定に使う設計(A-1(a))の妥当性 | Production既定`OFF`へ変更(`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION = False`)。関数自体は残置、read-only診断ヘルパーとして独立 | `DEFERRED / NOT_ADOPTED`(将来S1/量産telemetryでの追加証拠待ち、OPEN_ITEMS新規項目案は§8-4参照) |
| S1 | 既存NG記録のオフライン再判定(Ledger条件OFF前提での実データ影響測定) | `er025_phase4_s1_offline_reclassification_01.py`新設・実行。母数4115/反転20/`_case_a_entity_pass`0/loanword-only0 | 実施済み(§8-2) |
| S2 | (本委任の実装対象外。Fable/Opus側の粒度のまま、Sonnet側では追加実装を行っていない) | 対応なし(本委任範囲外) | `別途Fable判断`(Sonnet未着手) |
| S3 | `content_word_diffs`にentity_like根拠(capitalized/loanword)を持たせるprovenance付与 | `entity_like_source`をprotected_check/telemetry/cascade各step/human_review_queueへadditive伝播 | 実施済み(§8-3) |
| N1 | entity_like拡張がcascade起動条件・既存自動PASS機構(`_case_a_entity_pass`、ARPAbet完全一致条件)の入力域も広げる事実の明記 | CURRENT_SPEC/DECISION_LOG/本REPORTへ明記 | 実施済み(記録のみ、機構自体は無変更) |
| N2 | evidence記述の是正(Lock回避でattempt音声保存・segment_id role gateも無効化されていた点) | CURRENT_SPEC/DECISION_LOGへ明記 | 実施済み(記録のみ) |
| N3 | `ALLOW_PRONUNCIATION_WEB_LOOKUP`既定`"1"`でfallbackが初回lookup発火点になりうる点 | CURRENT_SPEC/DECISION_LOGへ明記 | 実施済み(記録のみ) |
| N4〜N7 | (本委任の実装対象外) | 対応なし(本委任範囲外) | `別途Fable判断`(Sonnet未着手) |

### §8-2 S1実測結果(¥0・read-only)

`er025_phase4_s1_offline_reclassification_01.py`(unit test:
`er025_phase4_s1_offline_reclassification_01_test_01.py`、6件全PASS)で、
以下2ファイルの全NG記録(canonical/ASR保持分)を現行コード(Ledger条件
OFF)で再判定した(実TTS/ASR/LLM呼び出し0件、入力ファイルは一切書き
込んでいない)。

| 入力ファイル | 母数 |
|---|---|
| `er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl` | 3875 |
| `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(steps単位) | 240 |
| **合計** | **4115** |

| 指標 | 件数 |
|---|---|
| entity_like反転(記録当時TRUE_CONTENT_MISMATCH→現行コードでASR_VALIDATION_UNCERTAIN) | 20 |
| そのうち`_case_a_entity_pass`(CMU辞書ARPAbet完全一致)でPASS化しうる件数 | 0 |
| そのうちloanword根拠のみによる反転(一般語誤りが隠れるリスクの保守的な注意フラグ、確定判定ではない) | 0 |

出力: `er025_output/phase4_s1_offline_01/summary.json`・
`flips_detail.jsonl`(反転20件の詳細、監査用)。

### §8-3 S3実装範囲

`protected_check()`の`content_word_diffs[*]`へ`entity_like_source`
(sorted list、Ledger条件OFFの間は`"ledger"`が出現することはない)を
追加し、`aggregate_entity_like_sources()`ヘルパー経由で以下へadditive
伝播した(既存キー・分類結果自体は無変更):

- er021 telemetry record(`er006_preprod_hardening_01_validation.py`の
  role gate経路、`er006_secondary_asr_01.py`のtier3_corroboration経路の
  2箇所)。
- `er006_secondary_asr_01.py`のcascade各step
  (`primary_1`/`primary_2`/`secondary_1`/`secondary_2`/
  `tier3_corroboration_secondary`/`non_latin_secondary`/
  `secondary_forced`)。
- human_review_queueレコード(`_log_human_review()`のtop-level要約
  キー、および`steps`経由で各stepの値も伝播)。

### §8-4 test/回帰

新規test 14件追加(`er006_pronunciation_phase4_entity_like_test_01.py`
に`LedgerConditionOffTests`4件+`EntityLikeSourceProvenanceTests`4件で
計23件、新規`er025_phase4_s1_offline_reclassification_01_test_01.py`
6件)、いずれも全PASS。既存関連test 201件+本体fixture57件+
`er006_secondary_asr_01_test.py`29件を再実行し全PASS(cascade各stepへの
`entity_like_source`追加後もdict厳密比較を要求するtestは無かったため
互換)。

`run_project_regression.py`: `collected=3432 passed=3422 failed=7
errors=3`。内訳は既知baseline(`er003_test_p2j_investigate`3 FAIL+
1 ERROR・`er003_test_bad`1 FAIL・`er011_open112_trend_synthesis_mode_
production_wiring_01_test_01`3 FAIL・`er015_standard_a2_6000_
generation_first_trial_01_test_01`loader 1 ERROR)+環境依存flake1件
(`er012_e_family_entertainment_two_level_runner_test_01`、cp932
subprocess、本タスク無関係)に加え、新規に1件
(`er019_family_x_pointless_01_test_01.FamilyAUnchangedTest.
test_family_a_files_have_no_working_tree_diff`)。この新規1件は
`er003_v1_n3_01_scaffold_generate.py`に本タスク**以外**の別Agent作業
(`KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-*`系)による未commit
差分が存在することが原因であり(`git status`で本タスク開始前から
未commitだったことを確認済み、本タスクでは当該ファイルを一切編集して
いない)、本タスクのcode regressionではない。本タスクが変更した
ファイル(`er006_preprod_hardening_01_validation.py`/`er006_secondary_
asr_01.py`)起因の新規code regressionは0件。

### §8-5 SSOT・OPEN_ITEMS反映状況

CURRENT_SPEC.md・DECISION_LOG.mdへ本修正1回目の内容を反映した。
`OPEN_ITEMS.md`は、本タスク着手前から`OPEN-202`行に別Agent
(`KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-*`系)の未commit差分が
存在することを`git status`で確認し(委任文の指示どおり)、待機後も
解消しなかったため、本タスクでは`OPEN_ITEMS.md`を編集していない
(他Agentの未commit差分を巻き込んで一緒にcommitすることを避けるため)。
反映すべき内容の記載案はRESULT_PACKET側に記録し、Fableへ引き継ぐ。

### §8-6 Gate 3チェックリスト最終表

| # | 項目 | 状況 |
|---|---|---|
| 1 | コード実装(A-1・A-2、修正1回目でLedger条件OFF化) | 済 |
| 2 | Unit test(新規23+6件、既存201件+本体57件+cascade29件) | 済、全PASS |
| 3 | Fixture(proper noun/loanword/同形一般語ガード/negative control/実transcript/Ledger条件OFF固定) | 済 |
| 4 | Runtime evidence(A-2実発火、初回のみ。修正1回目は¥0コード変更のためAPI呼び出しなし) | 済(初回§5) |
| 5 | Regression(新規code regression0件を確認、他Agent起因1件を除外し記録) | 済(§8-4) |
| 6 | SSOT反映(CURRENT_SPEC/DECISION_LOG/REPORT_LEDGER) | 済。`OPEN_ITEMS.md`は他Agent未commit差分のため今回は未反映(§8-5、記載案はRESULT_PACKET) |
| 7 | Git(delegation_log保存・path指定commit・push) | 本REPORT完成後に実施 |
| 8 | **Opus L2レビュー** | **実施済み(BLOCKER0件、§8-1)** |
| 9 | `PRODUCTION_WIRED`最終判定 | **Fable判定 `PRODUCTION_WIRED`(2026-09-28)**(Ledger surface条件は`DEFERRED`/`NOT_ADOPTED`のまま) |

### §8-7 再実行候補(実施しない、見積のみ)

初回§8の見積(3segment・上限¥45程度・Guardrail案¥50)から変更なし。
Ledger条件をOFFへ変更したことによる追加の期待救済・リスクの差分は
無い(該当3segmentのkhaite/altuzarraはいずれも`capitalized_flags`
(本文中で大文字始まり)で既にentity_like扱いされており、A-1(a)
[Ledger条件]の有効/無効に影響を受けない。§4のtest fixtureで確認済み)。
Human Review Lockの解除はユーザー再承認後の別委任で実施すること
(本タスクの範囲外、実施しない)。
